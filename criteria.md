# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:** Search is plain code and deterministic, so the same query
finds the same listing every time. But every full run also makes two model
calls (`suggest_outfit`, `create_fit_card`), and with the cache off either one
can fail in ways my loop doesn't handle yet: `generate.py`'s retries can run
out under the 15-requests-per-minute limit, or a `ModelUnavailable` error can
occur that nothing catches. My size rule is also strict: it compares whole size
tokens, so a size written differently from the data ("size 30" for jeans listed
as "W30") filters out the matching listings, and the run stops before
`suggest_outfit`. One miss in five allows for that; a second miss would mean
something in my loop is actually broken.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:** This path never reaches the model. The stop depends only on
`search_listings`, which is plain code over a fixed data file, so an impossible
query like "designer ballgown size XXS under $5" comes back `[]` on every try,
and the `if` in `run_agent` stops before `suggest_outfit` is ever called. The
message is built by code from the data as well (which part of the query found
nothing, the closest match and its price, or the sizes that exist), so the same
query gets the same message every time. Nothing random sits on this path, so
5 of 5 is the honest target: a single miss would be a bug in my code.

---

## 3. The found item reaches `suggest_outfit`

Given 5 different queries that each return at least one search result, in
every run the listing shown as the input to `suggest_outfit` in the run's trace
has the same title, price, and platform as `session["selected_item"]`, 5 of 5
runs. A run where `suggest_outfit` is never called counts as a miss.

**Why this target:** Handing the item along is the same plain code for every
query, not the model: `run_agent` stores the first search result in
`session["selected_item"]`, and `suggest_outfit` reads it back out of the
session instead of getting it from a local variable. Nothing random happens
between `search_listings` and `suggest_outfit`, so a miss could only mean my
loop handed over the wrong item (a stale variable or the wrong index) or
skipped the call, which is why the target is 5 of 5. That kind of bug is easy
to miss by eye because it looks like a tool problem: an outfit built around a
different item than the one that was found.

---

## 4. Fit cards name price and platform, and vary

Given 5 different queries that each return at least one search result, each
fit card (1) states the price of `session["selected_item"]` with a dollar sign
(`$19` and `$19.00` both count for a $19.0 listing), (2) names its platform
(any capitalization), and (3) doesn't start with the same five words as any of
the other four cards, 5 of 5 cards. A run that ends without a fit card counts
as a miss.

**Why this target:** The fit card is the one output my code can't pin down:
`create_fit_card` asks the model at `TEMPERATURE` 0.9, and the prompt only
*asks* for the price and the platform; nothing in my code forces them in.
They're the facts a buyer needs and the only checkable link back to the
listing, so every card is held to them. Five different items should never open
the same way; if they do, the caption has turned into a template. I set it at
5 of 5 even though the model may slip, because a card that drops the price or
reads like every other card isn't one I'd post.

---

## 5. A down model gets a readable message

With the model unreachable (one character of `GEMINI_API_KEY` in `.env`
changed, and the cache off with `AI201_CACHE=0`), run 5 different queries that
each return at least one search result. Every run must end without a stack
trace, show a message saying the styling service is unavailable and to try
again later, with no exception name or status code in it (such as
`ModelUnavailable` or `400`), and show no outfit or fit card, 5 of 5 runs.

**Why this target:** A broken key fails the same way every time: `generate()`
turns the rejected call into a `ModelUnavailable` on the first attempt, with no
retries and nothing random, so once that error is caught every run takes the
same path, and anything less than 5 of 5 means a code path I didn't cover.
Nothing catches it yet: `app.py` prints the exception's name and text, which is
exactly the error-code output this criterion rules out. The cache matters for
the test, because `generate()` answers from the cache before it ever uses the
key, so with the cache on a broken key can look like it works.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Capstone criteria (unit 9)

Written before any capstone test was run. All five are tested against the
hosted service, https://fitfindr-am5n.onrender.com.

**One trial**
1. `GET /health` must answer in under 2 s. If it doesn't, wait 30 s and try
   again, up to 5 times; if it still doesn't, start the trial later.
2. Read `GET /log?n=500` and note the last record's `request_id`.
3. If the log has no `fit_card` record yet, send one unscored warm-up:
   `vintage graphic tee under $30`.
4. Send criterion 1's requests, then criterion 2's, then criterion 3's.
5. Read `GET /log?n=500` again.

Send every request with
`curl -s --max-time 150 -D headers.txt -o body.json -w '%{http_code} %{time_total}'`.
That gives the status, the client time, and the `X-Request-Id` header. A
`000` (no response) or a 502 from Render counts as a failed request. Wait
60 s between trials. Each target must hold in **3 of 3 trials**.

## 1. Warm runs return a fit card in under 8 seconds

Send these five queries one at a time:
- `90s track jacket in size M`
- `silk slip dress in midi length under $40`
- `platform sneakers size 8`
- `denim jacket under $50`
- `chunky knit cardigan`

A run passes if it returns 200, a non-blank `fit_card`, and a client time
under 8.0 s. **Target: 4 of 5 runs.**

**Why this target:**
- On the host, the two MCP calls alone took 7.7–8.5 s in every warm run.
  Each one starts a new Python process, which spends about 4 s importing the
  MCP library.
- The model calls take about 2 s. So 8 s can be met with one process start
  per run, but not with two.
- 10 s would sit right on today's median (10.3 s), so it would pass or fail
  on noise.
- It's 4 of 5, not 5 of 5, because one slow model call is the model's fault,
  not the deploy's. One call took 35.6 s locally.

## 2. A malformed request gets a 400, not a crash

Send these five bodies, as JSON:
- `[1, 2]`
- `{"query": 42}`
- `"vintage tee"`
- `{"query": ""}`
- `not json`

Each must get a 400, a JSON body with a non-empty `error` message, and an
`X-Request-Id` header. An HTML page fails. **Target: 5 of 5.**

**Why this target:**
- The check happens in plain code before the model is called, so the same
  body always gets the same answer. Any miss is a bug, so the target is
  5 of 5.
- Today `serve.py` assumes the body is a dict holding a string, so the first
  three crash into Flask's HTML 500 page.
- That page blames the server for the caller's mistake, and it has no
  request id to find in the log.
- The last two already pass. They're included so that a fix for the first
  three can't break them.

## 3. The log's time matches the user's wait when two requests overlap

Send `designer ballgown size XXS under $5` and `wetsuit size XXS` at the
same moment (`curl … & curl … & wait`). Neither one calls the model.
- **When to resend:** if the slower client's time is less than 1.5 times the
  faster one's, the two didn't queue, so send the pair again (at most twice).
  Only the last pair counts.
- **How it's scored:** find both records by `X-Request-Id`. Both must return
  200 with outcome `stopped`. For both, the client time minus `duration_ms`
  must be at most 1,000 ms. (`duration_ms` includes `waited_ms`.)
- **Target:** both requests pass in every trial.

**Why this target:**
- `waited_ms` exists so the log can tell "slow" apart from "waiting its
  turn". Today it can't.
- In Milestone 3, the second client waited 22.6 s, but its record said
  9.2 s, with `waited_ms` 0. Gunicorn's single sync worker holds the request
  before `serve.py` sees it.
- Locally, the record matched the client.
- 1,000 ms is about 2.5 times the normal network gap (0.13–0.38 s), so a
  hidden wait stands out.
- It's every trial, because whether the wait shows depends on the server
  setup, not on chance.

## 4. Every request leaves exactly one matching log record

Take the records after the noted one. There must be exactly one per `/ask`
sent: 12, plus 1 for a warm-up and 2 for each resent pair. More or fewer
fails the trial.
- **How to pair them:** in sending order (warm-up, criterion 1, criterion
  2). Criterion 3's pair is matched by `X-Request-Id`.
- **What matches:** a record's `status` must equal the status its client got.
  A `000` or a 502 never matches.
- **Target:** every request, in every trial.

**Why this target:**
- The record is written in a `finally`, so successes, rejections and
  crashes are all logged by design.
- A gap means something real went wrong: the 512 MB instance ran out of
  memory, gunicorn's 120 s timeout killed the worker, or the instance
  restarted and wiped the file.
- The log is this unit's only evidence. The cost, the latency breakdown and
  the README extracts all come from it, so not one request may go missing.

## 5. Each run makes exactly 2 model calls and costs at most $0.0008 on average

For criterion 1's five runs, find each record by `X-Request-Id`.
- **The cost of a run:** `tokens_in` × $0.30 + `tokens_out` × $2.50, per
  million tokens.
- **What passes:** each record must show outcome `fit_card`, `model_calls`
  exactly 2, and a cost of at most $0.0010. The five costs must average at
  most $0.0008.
- **What fails:** a run with no request id, no `fit_card`, or no token count.
- **Target:** all five, in every trial.

**Why this target:**
- **The real limit is 500 model requests a day,** on a free key shared with
  another project. A retry makes `model_calls` 3, which uses 50% more quota
  than the README's arithmetic assumes. Retries are counted exactly, so the
  call count must be exactly 2.
- **Why cap the average:** the cost does vary, because output tokens change
  at temperature 0.9. These five queries measured $0.00066–$0.00078 (mean
  $0.00070).
  - A $0.0008 average fails if output grows by about 21%, which is what a
    longer caption would look like.
  - A $0.0008 cap on each run would fail on noise: the silk slip dress
    already costs $0.00078.
