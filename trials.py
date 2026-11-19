#!/usr/bin/env python3
"""
Run the capstone criteria (criteria.md, "Capstone criteria") as three trials
against the hosted service, and score them. ← UNIT 9

    python trials.py https://fitfindr-am5n.onrender.com --label before

Each trial follows criteria.md's "One trial" steps, sending every request
with curl, exactly as the criteria say. The script writes
results/capstone_<label>_<time>.md with the run-log table, every request,
and the log records it was scored from. About 10 model calls a trial (12 if
a warm-up is needed).
"""

import argparse
import datetime as dt
import json
import subprocess
import tempfile
import threading
import time
from pathlib import Path

import config

C1_QUERIES = ["90s track jacket in size M", "silk slip dress in midi length under $40",
              "platform sneakers size 8", "denim jacket under $50", "chunky knit cardigan"]
C2_BODIES = ['[1, 2]', '{"query": 42}', '"vintage tee"', '{"query": ""}', "not json"]
C3_PAIR = ['{"query": "designer ballgown size XXS under $5"}', '{"query": "wetsuit size XXS"}']
WARM_UP = '{"query": "vintage graphic tee under $30"}'
TMP = Path(tempfile.mkdtemp())


def curl(url, body=None):
    """One request, sent the way criteria.md says. Returns what the client saw."""
    stem = TMP / f"{time.monotonic_ns()}_{threading.get_ident()}"
    cmd = ["curl", "-s", "--max-time", "150", "-D", f"{stem}.h", "-o", f"{stem}.b",
           "-w", "%{http_code} %{time_total}", url]
    if body is not None:
        cmd += ["-X", "POST", "-H", "Content-Type: application/json", "--data-binary", body]
    status, seconds = subprocess.run(cmd, capture_output=True, text=True).stdout.split()
    headers = Path(f"{stem}.h").read_text(errors="replace") if Path(f"{stem}.h").exists() else ""
    text = Path(f"{stem}.b").read_text(errors="replace") if Path(f"{stem}.b").exists() else ""
    rid = next((line.split(":", 1)[1].strip() for line in headers.splitlines()
                if line.lower().startswith("x-request-id:")), None)
    try:
        data = json.loads(text)
    except ValueError:
        data = None
    return {"body": body, "status": int(status), "ms": round(float(seconds) * 1000),
            "request_id": rid, "json": data}


def read_log(base):
    lines = subprocess.run(["curl", "-s", f"{base}/log?n=500"], capture_output=True, text=True).stdout
    return [json.loads(line) for line in lines.splitlines() if line.strip()]


def run_trial(base):
    for _ in range(6):  # step 1: the warm check, at most 5 repeats
        if curl(f"{base}/health")["ms"] < 2000:
            break
        time.sleep(30)
    else:
        raise SystemExit("/health never answered in under 2 s: start the trial later.")

    before = read_log(base)  # step 2: the mark
    mark = before[-1]["request_id"] if before else None
    seq = []
    if not any(r["outcome"] == "fit_card" for r in before):  # step 3
        seq.append({**curl(f"{base}/ask", WARM_UP), "part": "warm-up"})
    seq += [{**curl(f"{base}/ask", json.dumps({"query": q})), "part": "c1"} for q in C1_QUERIES]
    seq += [{**curl(f"{base}/ask", b), "part": "c2"} for b in C2_BODIES]

    pairs = []
    for _ in range(3):  # criterion 3: resend only if the pair didn't queue
        pair = [None, None]
        threads = [threading.Thread(target=lambda i=i: pair.__setitem__(i, curl(f"{base}/ask", C3_PAIR[i])))
                   for i in range(2)]
        [t.start() for t in threads]
        [t.join() for t in threads]
        pairs.append(pair)
        fast, slow = sorted(p["ms"] for p in pair)
        if slow >= 1.5 * fast:
            break

    after = read_log(base)  # step 5
    ids = [r["request_id"] for r in after]
    new = after[ids.index(mark) + 1:] if mark in ids else (after if mark is None else None)
    return {"seq": seq, "pairs": pairs, "new": new}


def score(t):
    """Each criterion's pass count for one trial, and whether the trial passed it."""
    by_id = {r["request_id"]: r for r in (t["new"] or [])}
    c1 = [r for r in t["seq"] if r["part"] == "c1"]
    c2 = [r for r in t["seq"] if r["part"] == "c2"]

    ok1 = [r["status"] == 200 and isinstance((r["json"] or {}).get("fit_card"), str)
           and r["json"]["fit_card"].strip() != "" and r["ms"] < 8000 for r in c1]
    ok2 = [r["status"] == 400 and isinstance(r["json"], dict) and isinstance(r["json"].get("error"), str)
           and r["json"]["error"].strip() != "" and bool(r["request_id"]) for r in c2]

    last = t["pairs"][-1]
    fast, slow = sorted(p["ms"] for p in last)
    queued = slow >= 1.5 * fast
    ok3 = [queued and p["status"] == 200 and p["request_id"] in by_id
           and by_id[p["request_id"]]["outcome"] == "stopped"
           and p["ms"] - by_id[p["request_id"]]["duration_ms"] <= 1000 for p in last]

    pair_reqs = [p for pair in t["pairs"] for p in pair]
    new = t["new"]
    if new is None or len(new) != len(t["seq"]) + len(pair_reqs):
        ok4 = [False]
    else:
        seq_recs = new[:len(t["seq"])]
        ok4 = [r["status"] not in (0, 502) and rec["status"] == r["status"]
               for r, rec in zip(t["seq"], seq_recs)]
        ok4 += [p["status"] not in (0, 502) and p["request_id"] in by_id
                and by_id[p["request_id"]]["status"] == p["status"] for p in pair_reqs]

    costs, ok5 = [], []
    for r in c1:
        rec = by_id.get(r["request_id"])
        good = bool(rec) and rec["outcome"] == "fit_card" and rec["model_calls"] == 2 \
            and rec["tokens_in"] is not None and rec["tokens_out"] is not None
        cost = (rec["tokens_in"] * 0.30 + rec["tokens_out"] * 2.50) / 1e6 if good else None
        costs.append(cost)
        ok5.append(good and cost <= 0.0010)
    mean = sum(costs) / 5 if all(c is not None for c in costs) else None
    pass5 = all(ok5) and mean is not None and mean <= 0.0008

    return {
        1: (f"{sum(ok1)}/5", sum(ok1) >= 4),
        2: (f"{sum(ok2)}/5", all(ok2)),
        3: (f"{sum(ok3)}/2", all(ok3)),
        4: (f"{sum(ok4)}/{len(ok4)}" if new is not None and len(ok4) > 1 else "count off", all(ok4)),
        5: (f"{sum(ok5)}/5, mean ${mean:.6f}" if mean else f"{sum(ok5)}/5", pass5),
    }


TITLES = {1: "1. Warm runs return a fit card in under 8 s", 2: "2. A malformed request gets a 400",
          3: "3. The log's time matches the wait when requests overlap",
          4: "4. Every request leaves one matching record", 5: "5. 2 model calls, mean cost ≤ $0.0008"}
TARGETS = {1: "4 of 5, 3 of 3 trials", 2: "5 of 5, 3 of 3 trials", 3: "2 of 2, 3 of 3 trials",
           4: "all, 3 of 3 trials", 5: "5 of 5 and mean ≤ $0.0008, 3 of 3 trials"}


def main():
    parser = argparse.ArgumentParser(description="Run the capstone criteria three times.")
    parser.add_argument("url")
    parser.add_argument("--label", default="run")
    args = parser.parse_args()
    base = args.url.rstrip("/")

    trials, scores = [], []
    for n in range(1, 4):
        if n > 1:
            time.sleep(60)
        print(f"trial {n}…", flush=True)
        trials.append(run_trial(base))
        scores.append(score(trials[-1]))
        print("  " + "  ".join(f"C{c}: {s[0]}" for c, s in scores[-1].items()), flush=True)

    out = [f"# Capstone trials — {args.label}", "",
           f"- Server: {base}", f"- When: {dt.datetime.now().strftime('%Y-%m-%d %H:%M')}",
           "- Produced by: `trials.py::main`; records from `serve.py::ask` via GET /log", "",
           "| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |", "|---|---|---|---|---|---|"]
    for c in range(1, 6):
        cells = " | ".join(("PASS " if s[c][1] else "FAIL ") + s[c][0] for s in scores)
        verdict = "MET" if all(s[c][1] for s in scores) else "MISSED"
        out.append(f"| {TITLES[c]} | {TARGETS[c]} | {cells} | {verdict} |")
    for n, t in enumerate(trials, 1):
        out += ["", f"## Trial {n}", "", "| Part | Request | Status | Client ms | X-Request-Id |", "|---|---|---|---|---|"]
        for r in t["seq"] + [p for pair in t["pairs"] for p in pair]:
            out.append(f"| {r.get('part', 'c3')} | `{r['body']}` | {r['status']} | {r['ms']} | {r['request_id']} |")
        out += ["", "Log records after the mark:", "", "```jsonl",
                *[json.dumps(r, ensure_ascii=False) for r in (t["new"] or [])], "```"]
    path = config.RESULTS_DIR / f"capstone_{args.label}_{dt.datetime.now().strftime('%Y-%m-%d_%H%M')}.md"
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out[6:13]))
    print(f"Wrote {path.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
