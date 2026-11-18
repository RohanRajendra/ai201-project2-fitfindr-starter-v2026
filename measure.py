#!/usr/bin/env python3
"""
Send a fixed set of requests to a running FitFindr server, and save what
came back. ← UNIT 9

    python measure.py http://localhost:5001 --label local
    python measure.py https://<your-service>.onrender.com --label hosted

It first times GET /health (on a sleeping free host, that's the wake-up).
Then it sends each request in REQUESTS, one at a time, and times it from this
side. Finally it reads the server's own record of each one back from
GET /log and writes both to results/measure_<label>_<time>.md, with averages
over the completed runs. Those averages are where the README's What It Costs
comes from.

Every completed run costs two model calls, so the default set costs 20.
"""

import argparse
import datetime as dt
import json
import time
import urllib.error
import urllib.request

import config

# Ten queries the data can match (app.py's five examples, then five from unit
# 4's scenarios), then two the server should turn away: an empty query (a
# 400), and a JSON list body that serve.py doesn't handle (a 500).
REQUESTS = [
    '{"query": "vintage graphic tee under $30"}',
    '{"query": "90s track jacket in size M"}',
    '{"query": "silk slip dress in midi length under $40"}',
    '{"query": "platform sneakers size 8"}',
    '{"query": "denim jacket under $50"}',
    '{"query": "chunky knit cardigan"}',
    '{"query": "cargo pants under $30"}',
    '{"query": "y2k baby tee"}',
    '{"query": "corduroy pants"}',
    '{"query": "mini shoulder bag"}',
    '{"query": ""}',
    "[1, 2]",
]


def call(method, url, body=None, timeout=180):
    """One request: (status, ms from this side, X-Request-Id, body text)."""
    request = urllib.request.Request(
        url, data=body.encode() if body else None, method=method,
        headers={"Content-Type": "application/json"} if body else {},
    )
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status, headers, text = response.status, response.headers, response.read().decode()
    except urllib.error.HTTPError as exc:
        status, headers, text = exc.code, exc.headers, exc.read().decode(errors="replace")
    except (urllib.error.URLError, TimeoutError) as exc:
        status, headers, text = None, {}, f"{type(exc).__name__}: {exc}"
    return status, round((time.perf_counter() - start) * 1000), headers.get("X-Request-Id"), text


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("url", help="the server, e.g. http://localhost:5001")
    parser.add_argument("--label", default="run")
    args = parser.parse_args()
    base = args.url.rstrip("/")

    health = call("GET", f"{base}/health")
    print(f"/health: {health[0]} in {health[1]} ms")

    sent = []
    for body in REQUESTS:
        status, ms, request_id, _ = call("POST", f"{base}/ask", body)
        sent.append({"body": body, "status": status, "client_ms": ms, "request_id": request_id})
        print(f"  {status} in {ms:>6} ms  {body}")

    # The server's records, in the order sent. A 500 from Flask's own error
    # page carries no X-Request-Id, so pairing is by position, checked by id.
    lines = call("GET", f"{base}/log?n={len(REQUESTS)}")[3].splitlines()
    for row, record in zip(sent, map(json.loads, lines)):
        if row["request_id"] not in (None, record["request_id"]):
            raise SystemExit("The log doesn't line up with the requests sent "
                             "(did the server restart, or did someone else call it?).")
        row["record"] = record

    write_report(args, base, health, sent, lines)


def write_report(args, base, health, sent, lines):
    done = [r["record"] for r in sent if r.get("record", {}).get("outcome") == "fit_card"]
    client = [r["client_ms"] for r in sent if r.get("record", {}).get("outcome") == "fit_card"]

    def avg(values):
        return round(sum(values) / len(values)) if values else None

    out = [
        f"# measure.py — {args.label}",
        "",
        f"- Server: {base}",
        f"- When: {dt.datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"- GET /health first: {health[0]} in {health[1]} ms",
        "- Produced by: `measure.py::main`; the records come from `serve.py::ask`, via GET /log",
        "",
        "| # | Request | Status | Client ms | Server duration_ms | Outcome | Model calls | Tokens in | Tokens out |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for i, row in enumerate(sent, 1):
        r = row.get("record", {})
        out.append(f"| {i} | `{row['body']}` | {row['status']} | {row['client_ms']} | "
                   f"{r.get('duration_ms')} | {r.get('outcome')} | {r.get('model_calls')} | "
                   f"{r.get('tokens_in')} | {r.get('tokens_out')} |")
    averages = (
        f"**Averages over the {len(done)} completed runs (outcome fit_card):** "
        f"client {avg(client)} ms · server {avg([r['duration_ms'] for r in done])} ms · "
        f"model calls {avg([r['model_calls'] for r in done])} · "
        f"tokens in {avg([r['tokens_in'] for r in done])} · "
        f"tokens out {avg([r['tokens_out'] for r in done])}"
    )
    out += [
        "",
        averages,
        "",
        "## The log records, as GET /log returned them",
        "",
        "```jsonl",
        *lines,
        "```",
        "",
    ]
    config.RESULTS_DIR.mkdir(exist_ok=True)
    path = config.RESULTS_DIR / f"measure_{args.label}_{dt.datetime.now().strftime('%Y-%m-%d_%H%M')}.md"
    path.write_text("\n".join(out), encoding="utf-8")
    print(f"\n{averages}\nWrote {path.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
