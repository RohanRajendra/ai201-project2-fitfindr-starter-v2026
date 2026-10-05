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
