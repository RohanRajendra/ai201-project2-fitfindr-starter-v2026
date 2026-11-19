#!/usr/bin/env python3
"""
FitFindr over HTTP. ← UNIT 9

    python serve.py                       run it on your machine
    gunicorn serve:app                    run it the way a host runs it

Everything else in this repo exits after one command. A host has nothing to
keep running, so a command line cannot be deployed. This file is the smallest
thing that can: it starts a web server, waits, and hands each request to the
same `run_agent()` your CLI calls. **No new agent logic lives here.** If your
loop works from `python app.py ask`, it works from here; if it doesn't, fix it
there, not in this file.

Three routes:

    POST /ask       {"query": "vintage graphic tee under $30",
                     "wardrobe": {...}}     ← wardrobe is optional
    GET  /health    is it awake?
    GET  /log?n=20  the last n log records, one JSON line each

`/ask` returns the session dict from `run_agent()` as JSON, unchanged — the
same keys you print from the command line, including `error`. Read
`session["error"]` first, exactly as you do everywhere else.

It runs **one request at a time**, and one route is deliberately slower than a
web server has to be. The reason is worth reading before you deploy: see the
note above `_one_at_a_time` below — it also decides which gunicorn worker you
can use.

Every /ask request writes one structured log record, one JSON line, to stdout
(which a host's log viewer keeps) and to results/serve_log.jsonl (which you
can read back). That includes requests that are rejected or crash, because a
failure that leaves no record is one nobody finds. The fields are listed
above `_log` below.
"""

import datetime as dt
import json
import os
import sys
import threading
import time
import uuid

# config first, and before anything that talks to the model: it loads your .env
# and fixes the Windows console encoding for every module that imports it.
import config

from flask import Flask, jsonify, request

import agent
import generate
from utils.data_loader import get_example_wardrobe

app = Flask(__name__)


# ── the structured log ────────────────────────────────────────────────────────
# One record per /ask request, whatever happens to it. The fields:
#
#   ts            when the request came in, UTC
#   request_id    a short random id for this request
#   route         "/ask"
#   status        the HTTP status sent back (null: the worker was stopped mid-run)
#   query         what came in: the "query" field, or the raw body without one
#   outcome       fit_card, stopped (the run ended early, see error),
#                 rejected (400) or crashed (500)
#   item          the listing it picked, if it got that far
#   error         session["error"], the 400 message, or the exception
#   duration_ms   from arrival to response, waited_ms included
#   waited_ms     how long it waited for the one-at-a-time lock
#   model_calls   this run's share of generate.py's running totals: the count
#   tokens_in     after the run minus the count before. Retries count as
#   tokens_out    calls; cached answers cost nothing, so they add nothing.
#   stages_ms     ms per stage, summed over repeat calls: search_listings and
#                 compare_price (MCP: each call starts mcp_server.py as a new
#                 process), suggest_outfit and create_fit_card (the model).
#                 duration_ms - waited_ms - these = everything else.

LOG_FILE = config.RESULTS_DIR / "serve_log.jsonl"


def _ms(start: float) -> int:
    return round((time.perf_counter() - start) * 1000)


def _log(record: dict) -> None:
    line = json.dumps(record, ensure_ascii=False, default=str)
    print(line, flush=True)  # stdout: what the host's log viewer keeps
    try:
        LOG_FILE.parent.mkdir(exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as f:  # the copy you can read back
            f.write(line + "\n")
    except OSError as exc:  # a full disk shouldn't cost the user their answer
        print(f"  [serve] couldn't write {LOG_FILE}: {exc}", file=sys.stderr, flush=True)


# ── per-stage timing (stretch: the latency breakdown) ─────────────────────────
# agent.py looks these names up each time it calls them, so wrapping its module
# attributes times every call without changing a line of agent.py. Only this
# server process is affected. One run at a time (the lock), so one dict.

_stage_ms: dict[str, int] = {}


def _timed(fn, stage=None):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            name = stage or kwargs.get("name") or args[0]  # call_tool(name, arguments)
            _stage_ms[name] = _stage_ms.get(name, 0) + _ms(start)
    return wrapper


agent.call_tool = _timed(agent.call_tool)
agent.suggest_outfit = _timed(agent.suggest_outfit, "suggest_outfit")
agent.create_fit_card = _timed(agent.create_fit_card, "create_fit_card")


# ── one request at a time ─────────────────────────────────────────────────────
# Here's why this exists.
#
# A web server will happily run two requests at once. Two things in this repo
# assume otherwise:
#
#   • If you moved a tool onto MCP in unit 4, `mcp_client.call_tool` starts
#     `mcp_server.py` as a separate process over stdio, one per call. Two
#     overlapping requests means two extra Python interpreters, and the free
#     tier you're deploying to has 512 MB for all of it. That is the reason
#     that would still be here even if everything else were perfect.
#   • `generate.py`'s pacing window and its call counter are plain module
#     globals — deliberately, because that file is teaching pacing and quota,
#     not locking. Two threads sharing them means the per-minute limiter is
#     counting something that isn't true.
#
# What the lock covers is exactly the agent run: the part that spawns
# processes and calls the model. Reading the request, rejecting a bad one, and
# turning the answer into JSON all happen outside it — so a request with a
# malformed body comes straight back with a 400 instead of queueing behind
# somebody else's agent.
#
# Serialising the runs costs you nothing here — this is one user asking one
# question — and it keeps the deployed behaviour identical to the CLI's. When
# that stops being an acceptable trade, the fix is a real queue, not a bigger
# lock.
#
# The same constraint decides your start command, and this is the part that
# bites in deployment rather than on your machine. `mcp_client.call_tool`
# wraps `asyncio.run()`, and `asyncio.run()` refuses to start when an event
# loop is already running. An async worker always has one running. So under
# `gunicorn -k gevent` (or `-k eventlet`, or `serve:app` wrapped for an ASGI
# server like uvicorn) EVERY MCP call fails with "asyncio.run() cannot be
# called from a running event loop" — not some of them under load, all of
# them, every time, in a place your laptop never showed you.
#
#     gunicorn serve:app              ← right: the DEFAULT sync worker
#     gunicorn -k gevent serve:app    ← breaks every MCP call you make
#
# Since the capstone the host runs `--threads 2` (render.yaml). That is still
# not async: a worker thread has no event loop running, so asyncio.run() is
# fine. It lets a second request reach the lock, so waited_ms can see it.

_one_at_a_time = threading.Lock()


@app.get("/health")
def health():
    """Is the server awake? A host pings something like this to find out."""
    return jsonify({"status": "ok"})


@app.get("/log")
def log():
    """
    The last n lines of the log file, exactly as stored (one JSON record per
    line, oldest first): ?n=20 by default, at most 500. A free host wipes the
    file when it sleeps, so copy what you need the same day. Reading the log
    isn't a run, so it isn't logged.
    """
    n = max(1, min(request.args.get("n", default=20, type=int), 500))
    lines = LOG_FILE.read_text(encoding="utf-8").splitlines()[-n:] if LOG_FILE.exists() else []
    return app.response_class("".join(line + "\n" for line in lines), mimetype="text/plain")


@app.post("/ask")
def ask():
    """
    Run the agent on one query, and log it.

    In:   {"query": "...", "wardrobe": {...}}   wardrobe optional — leave it
                                                out and you get the same
                                                example wardrobe the CLI uses.
    Out:  the session dict from run_agent(), as JSON.

    The route's work is in _answer(). This wrapper times it and writes the
    record in `finally`, so a request that crashes is logged too.
    """
    start = time.perf_counter()
    record = {
        "ts": dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds"),
        "request_id": uuid.uuid4().hex[:8], "route": "/ask", "status": None,
        "query": None, "outcome": None, "item": None, "error": None,
        "duration_ms": None, "waited_ms": 0,
        "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {},
    }
    try:
        body, record["status"] = _answer(record)
        return jsonify(body), record["status"], {"X-Request-Id": record["request_id"]}
    except BaseException as exc:  # a crash, or the worker stopped mid-run
        record["status"] = 500 if isinstance(exc, Exception) else None
        record["outcome"], record["error"] = "crashed", f"{type(exc).__name__}: {exc}"
        raise  # Flask answers it as it always did: the log records it, it doesn't fix it
    finally:
        record["duration_ms"] = _ms(start)
        _log(record)


def _answer(record: dict) -> tuple[dict, int]:
    """The route as the starter wrote it, filling in the record as it goes."""
    payload = request.get_json(silent=True)
    # What came in, read without assuming a shape. The lines after this one
    # assume a dict holding a string; a body that isn't one still goes on record.
    record["query"] = (payload.get("query") if isinstance(payload, dict)
                       else request.get_data(as_text=True)[:200])
    payload = payload or {}
    query = (payload.get("query") or "").strip()
    if not query:
        # 400 rather than a stack trace: the caller can act on this one.
        message = ("Send JSON with a 'query' field, e.g. "
                   '{"query": "vintage graphic tee under $30"}')
        record["outcome"], record["error"] = "rejected", message
        return {"error": message}, 400

    wardrobe = payload.get("wardrobe")
    if not isinstance(wardrobe, dict):
        wardrobe = get_example_wardrobe()

    # A queued request should look like a queued request. Without this the
    # second caller just sits there, and "slow" and "waiting its turn" are
    # indistinguishable from the outside — which is how people conclude the
    # deployment is broken when it is behaving exactly as designed.
    #
    # The record's waited_ms is what measures the wait. This note only says,
    # as it happens, that there is one. `locked()` can be a moment out of
    # date, so the note is occasionally missed — which costs nothing, because
    # nothing depends on it.
    if _one_at_a_time.locked():
        print(
            "  [serve] another request is still running. This one is waiting "
            "its turn — serve.py handles one at a time, on purpose.",
            file=sys.stderr,
            flush=True,
        )

    failure = None
    session = None
    queued = time.perf_counter()
    with _one_at_a_time:
        record["waited_ms"] = _ms(queued)
        calls, tokens = generate.call_count(), generate.token_counts()
        _stage_ms.clear()
        try:
            session = agent.run_agent(query, wardrobe)
        except Exception as exc:  # noqa: BLE001 — a 500 with a sentence beats a hang
            failure = f"{type(exc).__name__}: {exc}"
        finally:  # this run's share of the running totals, and its stages
            spent = generate.token_counts()
            record["model_calls"] = generate.call_count() - calls
            record["tokens_in"] = spent["prompt"] - tokens["prompt"]
            record["tokens_out"] = spent["output"] - tokens["output"]
            record["stages_ms"] = dict(_stage_ms)

    # Outside the lock: building a response is not work the next caller should
    # be waiting on.
    if failure is not None:
        record["outcome"], record["error"] = "crashed", failure
        return {"error": failure}, 500

    item = session.get("selected_item")
    if item:
        record["item"] = f"{item.get('title')} (${item.get('price')}, {item.get('platform')})"
    record["outcome"] = "stopped" if session.get("error") else "fit_card"
    record["error"] = session.get("error")
    return session, 200


if __name__ == "__main__":
    # PORT and 0.0.0.0 are not decoration. A host tells you which port to
    # listen on through PORT, and it reaches your process from outside the
    # container — bind 127.0.0.1 and nothing but the container itself can
    # connect, which looks exactly like a broken app from the browser.
    port = int(os.getenv("PORT", "5000"))

    # Never on by default. Flask's debugger executes code typed into a browser,
    # and a deployed app with it on is a stranger's shell. Set AI201_DEBUG=1 in
    # your own terminal when you want the reloader.
    debug = os.getenv("AI201_DEBUG", "0") == "1"

    print(f"\nFitFindr is listening on http://localhost:{port}")
    print("It runs one request at a time — a second one waits for the first.")
    print("Ask it something (single quotes, as always):\n")
    print(
        f"  curl -X POST http://localhost:{port}/ask \\\n"
        f"    -H 'Content-Type: application/json' \\\n"
        f"    -d '{{\"query\": \"vintage graphic tee under $30\"}}'\n"
    )
    print("Ctrl-C to stop.\n")

    app.run(host="0.0.0.0", port=port, debug=debug)
