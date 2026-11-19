# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools and the planning loop are built, so that last command runs
> the whole agent.
>
> Unit 4 additions:
> - The search and the price check run through MCP (`mcp_server.py`).
> - `python app.py ask '...' --trace` prints the loop step by step.
> - `python run_eval.py --label <name>` runs the five-tries test. That costs
>   about 45 model calls, so mind a free-tier key.
>
> Unit 9 (capstone) additions:
> - It's hosted at **https://fitfindr-am5n.onrender.com**.
> - `python serve.py` runs the same thing locally (RUNNING.md has both).
> - Every request is logged. The Capstone section at the end has the rest.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

FitFindr is a command-line thrift-shopping agent. You type what you want in
plain words, like `'vintage graphic tee under $30, size M'`, and it pulls out
the item, the size, and the price ceiling, then searches 40 secondhand
listings from Depop, thredUp, and Poshmark for the best match. When something
matches, you get the listing it picked (title, price, platform), one or two
outfits that pair it with pieces from your wardrobe, and a short caption you
could post about the find. When nothing matches, it stops before calling the
model and tells you what to change: the item words, the size, or the max
price.

---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Filters the 40 listings in `data/listings.json` by price
  ceiling and size, keeps only the ones that contain every keyword in the
  description, and ranks them. Since unit 4 it's offered over MCP by
  `mcp_server.py`, and the agent calls it through `mcp_client.call_tool`.
- **Inputs:**
  - `description` (str): the item words, e.g. `"vintage graphic tee"`.
  - `size` (str or None): e.g. `"M"`, `"8"`, `"W30"`. `None` skips size
    filtering.
  - `max_price` (float or None): inclusive ceiling in dollars, so a $30.00
    listing passes `max_price=30.0`. `None` skips price filtering.
- **Returns:** a `list[dict]` of at most 10 listings
  (`config.SEARCH_RESULT_LIMIT`), best match first. Each dict is one whole
  listing with these fields:
  - `id` (str), `title` (str), `description` (str), `category` (str)
  - `style_tags` (list of str), `colors` (list of str)
  - `size` (str), `condition` (str), `price` (float)
  - `brand` (str or None), `platform` (str)
  - *How sizes match:* a listing's size is split on `/` into whole tokens and
    compared token by token, ignoring case. Notes in parentheses are ignored.
    - `M` matches `S/M` and `M/L`, but `L` does **not** match `XL`.
    - `8` matches `US 8` but not `US 8.5`.
    - `W30` matches `W30 L30`.
    - `small`, `medium`, `large`, and `extra large` count as `S`, `M`, `L`,
      and `XL`.
    - A `One Size` listing matches any size.
  - *Which listings match (changed in unit 4):* a listing has to contain
    every description keyword somewhere in its title, description,
    category, style tags, colors, or brand.
    - Common words like "a" and "for" are dropped, and a trailing "s" is
      ignored, so `tees` matches `tee`.
    - Until unit 4's improvement, one shared keyword was enough. See The
      Improvement for what that got wrong.
  - *How results are ranked:* one point per keyword, and keywords in the
    title count twice, so listings with more of the words in their title
    come first. Ties go to the cheaper listing.
- **When it has nothing:** an empty list `[]`, never `None` and never an
  exception. A listing missing any keyword is dropped, so an empty or
  all-filler `description` also returns `[]`.

### `suggest_outfit`

- **What it does:** Asks the model for one or two outfits built around the new
  item, using pieces from the user's wardrobe.
- **Inputs:**
  - `new_item` (dict): one listing dict from `search_listings`.
  - `wardrobe` (dict): `{"items": [...]}`. Each item is a dict with `id`,
    `name`, `category`, `colors` (list), `style_tags` (list), and `notes`
    (str or None).
- **Returns:** a non-empty `str` with 1–2 outfit suggestions in plain text.
  When the wardrobe has items, the prompt asks for outfits that name the pieces
  exactly as they're written in their `name` field. The model sometimes
  changes the capitalization. A wardrobe piece with the same name as
  `new_item` is skipped, so a find saved by `--remember` isn't treated as
  something you already own when it comes up again.
- **When it has nothing:**
  - Empty wardrobe (`items` is `[]` or missing): returns general styling
    advice for the item. Still a non-empty string, and it never claims the
    user owns anything.
  - Empty `new_item`: returns `"No item to style — search for something first."`
    without calling the model.
  - Model sends back empty text: returns a one-line message saying so instead
    of `""`.

### `create_fit_card`

- **What it does:** Asks the model for a short caption about the find, written
  like a real social post.
- **Inputs:**
  - `outfit` (str): the outfit text `suggest_outfit` returned.
  - `new_item` (dict): the same listing dict that went into `suggest_outfit`.
- **Returns:** a `str` caption with 2–4 casual sentences, then 1–3 hashtags on
  the last line.
  - The prompt asks it to mention the item, its price (written like `$24`),
    and its platform once each. Nothing in the code enforces that: the
    Sample Run below has a card that spells the price out as "eighteen
    dollars".
  - The prompt also asks for the buyer's voice, opening with the vibe or the
    outfit rather than the price or the platform.
  - The code leaves the brand out of the prompt when the listing has none.
  - Wording changes from run to run (`TEMPERATURE` is 0.9) when the cache is
    off (`AI201_CACHE=0`). With the cache on, the same prompt returns the
    saved caption.
- **When it has nothing:**
  - Empty or whitespace-only `outfit`: returns
    `"Can't write a fit card without an outfit suggestion."`
  - Empty `new_item`: returns `"Can't write a fit card without an item."`
  - Neither case calls the model.
  - Model sends back empty text: returns a one-line message saying so instead
    of `""`.

Both model tools go through `generate()`. If the model can't be reached at
all, that raises `ModelUnavailable`. The tools let it through, and since unit
4 `run_agent` catches it and stops with a readable message (see Planning
Loop).

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:**
- If `search_listings` returns an empty list, the loop puts a message in
  `session["error"]` naming what to change (the item words, the size, or the
  max price) and stops. `suggest_outfit` is never called, and `fit_card`
  stays `None`.
- Otherwise it takes the first (best-scoring) result as
  `session["selected_item"]` and checks its price with `compare_price`, over
  MCP since the unit 4 stretch.
- **Second branch (stretch):** if that pick is above typical and the search
  results hold a cheaper close match (same category, same item word in the
  title, not above typical itself), the loop switches to it, keeps the
  original in `session["passed_over"]`, and checks the new pick's price.
  Otherwise it goes on to `suggest_outfit`, then `create_fit_card`.
- **Retry without the size** (unit 4 stretch): before that empty-search
  stop, if the query had a size, the loop searches once more without it. If
  that finds something, it carries on with it and records the dropped size
  in `session["dropped"]`. If not, it stops with the same message.
- **If the model can't be reached** (unit 4): when `suggest_outfit` or
  `create_fit_card` raises `ModelUnavailable` (a bad key, no network, or a
  service that stays busy through every retry), the
  loop puts a message in `session["error"]` and stops. The message says the
  styling service is unavailable and to try again. No outfit or fit card is
  shown.

**Where it lives:** `agent.py::run_agent`. It's a `while` loop over named
steps (search → retry, only when an empty search had a size → price →
suggest → card → done), and every pass calls
`trace.check_iterations(count)`, so a runaway loop raises an error once it
passes `MAX_ITERATIONS` (10) instead of running forever.

**How the query is parsed:** Regex, in `agent.py::parse_query`.
- A price phrase becomes `max_price`: `under $30`, `below 30`,
  `less than $30`, `up to $30`, `max $30`, a bare `$30`, or `30 dollars`.
- A size phrase becomes `size`: `size M`, `in size M`, `sz 8`.
- Leading filler like "looking for a" is dropped.
- Whatever is left becomes `description`.
- A size is only read after the word "size" or "sz". So "medium wash jeans"
  stays a description and doesn't become size M.

**What moves through the session:** Each tool reads its inputs back out of the
session, not from a local variable. The fields fill in this order:
1. `query`
2. `parsed` (`description`, `size`, `max_price`)
3. `search_results`
4. `dropped` (only set when the size retry found something, e.g. `"size 11"`)
5. `selected_item` (`search_results[0]`, unless the second branch switches
   to a cheaper close match)
6. `price_check` (what `compare_price` said; stretch tool, see below)
7. `passed_over` (only set when the second branch switched)
8. `outfit_suggestion`
9. `fit_card`

`steps` lists the tool each loop step called, in order:
`["search_listings", "compare_price", "suggest_outfit", "create_fit_card"]` on
a full run, with `compare_price` twice when the second branch switched (the old
pick, then the new one). It's
`["search_listings"]` when the branch stops it. It's
`["search_listings", "search_listings"]` when a query with a size stops
after the size retry. When the model can't be
reached, it ends at the model tool that failed. `error` is set only when the
run stops early.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

Recorded before the stretch features. The same query now also prints a
`Price:` line, shown under Stretch Features below.

```
$ python app.py ask 'vintage graphic tee under $30, size M'

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Outfit 1: Streetwear Contrast
Pair the Y2K Baby Tee — Butterfly Print with baggy straight-leg jeans, dark wash to balance the fitted top. Throw the black cropped zip hoodie on top and finish the look with chunky white sneakers.

Outfit 2: Casual Grunge
Wear the Y2K Baby Tee — Butterfly Print tucked into wide-leg khaki trousers, accented by the brown leather belt. Layer the vintage black denim jacket over it and anchor the outfit with black combat boots.

  Fit card: Total soft grunge fairy vibes with this little butterfly tee. Got it on depop for eighteen dollars and I am so obsessed with the pastel print. Going to wear it with baggy denim and beat up sneakers all week.

#y2k #thrifthaul #babytee

2 model calls this session, 710 prompt + 156 output tokens
```

**The three tools, tested one at a time**

`search_listings`: a match, then the empty case

(Recorded in unit 3. Since unit 4's strict matching, the first command
returns only the 4 listings that contain both "graphic" and "tee": lst_006,
lst_002, lst_033 and lst_017. The hoodie, the crewneck and the cargo pants
are gone.)

```
$ python -c "from tools import search_listings; print([(x['id'], x['title'], x['price'], x['size']) for x in search_listings('graphic tee', max_price=30)])"
[('lst_006', 'Graphic Tee — 2003 Tour Bootleg Style', 24.0, 'L'), ('lst_002', 'Y2K Baby Tee — Butterfly Print', 18.0, 'S/M'), ('lst_033', 'Vintage Band Tee — Faded Grey', 19.0, 'L'), ('lst_017', 'Mesh Long-Sleeve Top — Black', 15.0, 'S/M'), ('lst_015', 'Vintage Graphic Hoodie — Faded Black', 26.0, 'L'), ('lst_012', 'Oversized Crewneck Sweatshirt — Vintage Navy', 20.0, 'XL (fits oversized)'), ('lst_011', 'Low-Rise Cargo Pants — Khaki', 27.0, 'W29')]

$ python -c "from tools import search_listings; print(search_listings('designer ballgown', size='XXS', max_price=5))"
[]
```

`suggest_outfit`: the example wardrobe, then an empty one

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
Outfit 1: Casual Streetwear
Pair the Vintage Levi's 501 Jeans with the White ribbed tank top tucked in, layered under the Oversized grey crewneck sweatshirt. Finish the look with the Chunky white sneakers and the Black crossbody bag. This effortless combination plays with proportions while keeping the classic denim front and center.

Outfit 2: Edge & Denim
Style the Vintage Levi's 501 Jeans with the Black cropped zip hoodie and the Vintage black denim jacket on top for a double-denim contrast. Ground the outfit with the Black combat boots and accessorize with the Black crossbody bag. It is a sharp, textured streetwear look that leans into the vintage nature of the jeans.

$ python -c "from tools import suggest_outfit; from utils.data_loader import get_empty_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_empty_wardrobe()))"
Outfit 1: Pair these with a cropped white ribbed tank top, an oversized black leather biker jacket, and retro low-top sneakers like Adidas Sambas for an effortless streetwear look. 

Outfit 2: Style them tucked into knee-high brown leather boots, topped with a chunky cream cable-knit crewneck sweater and a tortoiseshell belt for a classic, cozy aesthetic. 

Thrifting tip: Wash vintage denim inside out in cold water and hang to dry to preserve the indigo dye and prevent further shrinking.
```

`create_fit_card`: a real card, then a blank outfit

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
nothing beats broken-in denim and fresh white sneakers for that effortless skater-off-duty look. scored these vintage levi's 501s on depop for $38 and they fit like an absolute dream. finally found the perfect medium wash pair.

#levis #streetwear #thrifted

$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('   ', load_listings()[0]))"
Can't write a fit card without an outfit suggestion.
```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* Fixing bugs in my helpers for the listing search. Before
  building `search_listings`, I had Claude check the size and keyword helpers
  I'd written after the lecture (`_size_tokens`, `_size_matches`, `_keywords`).
- *What came back:* Instead of just reading them, it ran them against the real
  sizes in `data/listings.json`. `_size_matches('8', 'US 8')` returned `False`:
  every shoe is listed as `US 8`, `US 8.5`, and so on, so the starter's own
  example `'platform sneakers size 8'` would have found nothing. `'W30'` didn't
  match `'W30 L30'` either, and `_keywords()` kept `30` and `size` from "under
  $30, size M".
- *What I changed:* I had it patch `_size_tokens` to strip a leading `US ` and
  split `W30 L30` into `W30` and `L30`, keeping the rule that `L` never matches
  `XL`. I also chose a regex parser that cuts the price and size phrases out of
  the query before keyword scoring. The search check now confirms
  `'platform sneakers'` in size 8 finds lst_019.

**Moment 2**

- *What I asked for:* An idea about the data that we are working with. Analysing the data to write more informed criteria. 
- *What came back:* My draft claimed that a phrasing my search doesn't read
  ("t-shirt" for "tee", or a size without the word "size") "finds nothing".
  When Claude reviewed my version, it checked that claim against the data, and
  it was wrong: "t-shirt" still matches three shirts through the word "shirt",
  and a size without "size" is simply ignored. The real way a matching query
  comes back empty is a size written differently from the data:
  `'jeans size 30'` keeps only the One Size listings and drops both W30 jeans.
- *What I changed:* I replaced that sentence with the "size 30" vs "W30"
  example. Since then I check every
  claim in a reason against the real data before committing it.

**Unit 4**

**Moment 3: the model "went down" with a working key**

- *What I asked:* Run the before test and explain every miss.
- *What came back:*
  - 7 of the 22 runs that reached the model failed with the "styling service
    is unavailable" message. My key was fine.
  - Claude used the run log to rule out the key and my pacing. The same key
    worked in the other 15 runs, and the run averaged about 8 calls a
    minute, so the pacer never waited.
  - A 10-call probe and a 20-call replay had no errors, so the failures were
    passing ones. The raw error hadn't been recorded anywhere.
  - In the after run it got worse (11 of 20). A probe during that stretch
    caught the raw error: `503 UNAVAILABLE … high demand … Please try again
    later.`
- *What I changed:*
  - I kept both runs exactly as they happened instead of re-running for
    better numbers.
  - I wrote the diagnosis as "`generate()` never retries a 503", with the
    evidence.
  - I fixed search first, because a fix for passing errors can't be shown
    working in one run. The retry is my stretch improvement.

**Moment 4: arguing against my own verdicts**

- *What I asked:* My existing criteria and verdicts: push the criteria on its edge cases and contradict the verdicts. 
- *What came back:* four arguments were returned based on the tests:
  1. The outages belong to criterion 5.
  2. "red cowboy boots" returned 3 results, so it "matched".
  3. The second branch's swap meant the "found item" never reached
     `suggest_outfit`.
  4. Criterion 5 wasn't proven, because the key was changed in memory and
     there was no evidence of "no stack trace".
- *What I changed:*
  - No verdicts changed. I checked each argument against the code and the
    logs, and wrote the answers into Verdicts and Diagnoses:
    - Criterion 1's own reason counts outages.
    - The other reading of "matches" makes criterion 2 circular.
    - During a run only `generate._get_client()` reads the key.
    - The run had 0 tracebacks.
  - Its passing remark about a card saying "forty four dollars" became a
    count: 3 of 15 cards spelled the price out. That turned a one-off into
    a pattern.

**Moment 5: which tool to move onto MCP second**

- *What I asked:* Planning the mcp tool call for additional features. 
- *What came back:*
  - Every `call_tool` starts `mcp_server.py` as a separate process.
  - That process gets only a short list of environment variables, and it
    reads `.env` itself.
  - So a model tool behind MCP would never see `run_eval.py`'s cache-off
    switch or criterion 5's broken key. Those test runs would quietly stop
    measuring what they claim, and the calls would bypass `generate.py`'s
    rate limiter.
- *What I changed:*
  - `compare_price` to make no model call, for the "second tool on MCP" additional feature. 
  - Criterion 5 breaks the key inside the process that makes the model calls.

---

## Stretch Features

Declared here **before any of them is built**. Each one gets its own commit
after this one, and this section will then say what it changed and show a run
where it happened.

### 1. Fourth tool: `compare_price`

- **What it does:** Compares the picked item's price with the median price of
  the other listings in the same category.
- **Input:** `item` (dict): one listing dict.
- **Returns:** a `dict` with these keys:
  - `price` (float, or None when the item had no usable price)
  - `typical_price` (float): the category median
  - `verdict` (str): `"below typical"` when the price is at least 15% under
    the median, `"above typical"` when it's at least 15% over, and
    `"about typical"` otherwise
  - `compared_with` (int): how many listings the median came from
- **When it has nothing:** an empty item, an item without a numeric price, or
  a category with no other listings returns `verdict: "no comparison"` and
  `typical_price: None`.
- **In the loop:** it's called right after an item is picked. The result goes
  in `session["price_check"]`, and the output prints it as a `Price:` line.
- **Status:** built.
- **What it changed:**
  - The loop has a new step between search and `suggest_outfit`.
  - `steps` on a full run now lists four tools.
  - The session has a `price_check` field.
  - `app.py` and `agent.py` print a `Price:` line under `Found:`.
  - The fit card doesn't use the result, so criterion 4 is untouched.
- **The tool on its own:**

  ```
  $ python -c "from tools import compare_price; from utils.data_loader import load_listings; print(compare_price(load_listings()[1]))"
  {'price': 18.0, 'typical_price': 21.5, 'verdict': 'below typical', 'compared_with': 14}
  ```

- **A run where the agent called it:**

  ```
  $ python app.py ask 'vintage graphic tee under $30, size M'
    Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop
    Price:    $18, below the typical $21.50 for tops
  ...

  $ python -c "from agent import run_agent; from utils.data_loader import get_example_wardrobe; s = run_agent('vintage graphic tee under \$30, size M', get_example_wardrobe()); print(s['steps']); print(s['price_check'])"
  ['search_listings', 'compare_price', 'suggest_outfit', 'create_fit_card']
  {'price': 18.0, 'typical_price': 21.5, 'verdict': 'below typical', 'compared_with': 14}
  ```

### 2. Second branch: switch away from an overpriced pick

- **Condition:** `compare_price` says the picked item is `"above typical"`, and
  the search results hold a cheaper close match that isn't above typical. A
  close match has the same category and the same item word at the end of its
  title, for example two blazers or two pairs of jeans.
- **Path:**
  - If there's a close match, the loop switches `session["selected_item"]` to
    it, keeps the item it passed over in `session["passed_over"]`, and the
    output says why.
  - If there isn't, it keeps the original pick, and the price check shows it as
    above typical.
- **Where it lives:** `agent.py::run_agent`, in the `price` step.
  `_better_deal` finds the close match.
- **Status:** built.
- **What it changed:**
  - After a switch the loop goes round one more time, and `compare_price`
    runs again for the new pick.
  - The session has a `passed_over` field.
  - The output adds a line saying what was passed over and why.
  - It switches at most once per run.
  - `_better_deal` also prices each candidate with `compare_price`, and those
    checks aren't added to `steps`. A switched run makes three
    `compare_price` calls but records two.
  - **Known limit (unit 3):** matching was loose, so a switch could
    contradict a word you typed. For example, `'blue jeans'` switched to the
    black jeans.
  - **Update after unit 4's strict matching** (see The Improvement):
    - That limit is fixed: `'blue jeans'` now keeps the dark-wash carpenter
      jeans.
    - As predicted, `'velvet blazer'` stopped switching, because the linen
      blazer doesn't say "velvet". The run log below was recorded before that
      change.
    - `'graphic tee'` and `"vintage levi's jeans"` still switch. The Loop
      Trace has a current switched run.
  - None of the example queries switch, because their picks are below or
    about typical. Overpriced picks with no close match, such as
    `'graphic hoodie'` or `'leather bomber'`, are kept.
- **A run where the branch was taken:**

  ```
  $ python app.py ask 'velvet blazer'

    Found:    Vintage Linen Blazer — Cream — $38.0 on thredUp
    Price:    $38, about the typical $42 for outerwear
    Switched from Velvet Blazer — Emerald Green ($52, above the typical $40 for outerwear) to this cheaper close match.

    Outfit:   Outfit 1: High-Low Contrast
  Pair the vintage linen blazer with the white ribbed tank top tucked into the baggy straight-leg jeans, dark wash. Add the chunky white sneakers and the black crossbody bag for an effortless high-low mix of structured vintage and relaxed streetwear.

  Outfit 2: Monochromatic Earth Tones
  Layer the vintage linen blazer over the white ribbed tank top and wide-leg khaki trousers. Cinch the waist with the brown leather belt and finish with the chunky white sneakers for a polished, minimalist daytime look.

    Fit card: Channelling the ultimate coastal grandma energy with this cream linen blazer. Scored it on thredUp for just $38 and the fabric is so crisp and breathable. It instantly pulls together any casual denim look or wide-leg pant moment. 

  #vintagefinds #thrifthaul #minimaliststyle

  0 model calls this session, 2 served from cache

  $ python -c "from agent import run_agent; from utils.data_loader import get_example_wardrobe; s = run_agent('velvet blazer', get_example_wardrobe()); print(s['steps']); print('passed_over:', s['passed_over']['title'], s['passed_over']['price']); print('selected_item:', s['selected_item']['title'], s['selected_item']['price']); print('price_check:', s['price_check'])"
  ['search_listings', 'compare_price', 'compare_price', 'suggest_outfit', 'create_fit_card']
  passed_over: Velvet Blazer — Emerald Green 52.0
  selected_item: Vintage Linen Blazer — Cream 38.0
  price_check: {'price': 38.0, 'typical_price': 42.0, 'verdict': 'about typical', 'compared_with': 7}
  ```

### 3. Style memory: `--remember`

- **What it does:** `python app.py ask '...' --remember` runs with a saved
  wardrobe instead of the example one.
  - The saved wardrobe starts empty.
  - After each completed run, the found item is added to it, so the next run's
    outfit can use pieces earlier runs found.
  - `python app.py forget` clears it.
- **Where it's stored:** a gitignored file, `.fitfindr/wardrobe.json`. Runs
  without `--remember`, and `run_eval.py`, never read or change it.
- **Status:** built.
- **What it changed:**
  - A new `memory.py` has `load_wardrobe`, `remember`, and `forget`.
  - `app.py ask` takes `--remember`, which can't be combined with
    `--empty-wardrobe`, and there's a new `app.py forget` command.
  - After a completed `--remember` run, the selected item is saved as a
    wardrobe piece. It has the same fields as the wardrobe schema, plus a
    note saying where it was found and for how much.
  - `run_agent`, `run_eval.py`, and `serve.py` are unchanged and never read
    the file.
  - `.gitignore` now lists `.fitfindr/`.
  - A saved file that can't be read, or isn't shaped like a wardrobe, counts
    as empty, and `forget` always deletes it. Saves go to a temp file first,
    so a run that dies mid-write can't wipe earlier pieces.
- **Two runs where the second is shaped by the first:**
  - Run 1 starts from an empty memory, so its outfit is general advice. It
    saves the Y2K Baby Tee.
  - Run 2's outfits are built around the new denim jacket, and both of them
    use that tee.
  - This is a re-run of the same sequence after a wording fix, so both runs
    are served from the cache. The first time, they made 2 real model calls
    each and returned the same text.

  ```
  $ python app.py forget
  Forgot 2 saved pieces.

  $ python app.py ask 'vintage graphic tee under $30, size M' --remember
  (running with your saved wardrobe: 0 pieces)

    Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop
    Price:    $18, below the typical $21.50 for tops

    Outfit:   Outfit 1: Low-rise light-wash flare jeans and white platform sneakers for a classic Y2K pop star look.

  Outfit 2: A pastel pink pleated tennis skirt and chunky strappy sandals to lean into the playful butterfly aesthetic.

  Styling tip: Keep accessories minimal. Add a small pink shoulder bag and thin silver hoop earrings to let the graphic print stand out.

    Fit card: Channeling total 2000s pop star energy in this little butterfly baby tee. Found it on depop for just 18 dollars and the print is so nostalgic. Pairing it with low rise flares and platforms for the ultimate bratz doll vibe. 🦋✨

  #y2k #babytee #vintage

    Remembered Y2K Baby Tee — Butterfly Print. Your saved wardrobe has 1 piece now.

  0 model calls this session, 2 served from cache

  $ python app.py ask 'denim jacket under $50' --remember
  (running with your saved wardrobe: 1 piece)

    Found:    Denim Jacket — Light Wash, Cropped — $42.0 on poshmark
    Price:    $42, about the typical $40 for outerwear

    Outfit:   Outfit One: Layer the Wrangler Denim Jacket over the Y2K Baby Tee — Butterfly Print for a nostalgic, double-vintage look. Add light wash low-rise jeans and chunky platform sneakers to complete the Y2K street style aesthetic.

  Outfit Two: Wear the Y2K Baby Tee — Butterfly Print tucked into a pleated white tennis skirt, then throw the Wrangler Denim Jacket loosely over your shoulders. Finish with pastel sneakers and a beaded shoulder bag for a sweet, throwback daytime vibe.

    Fit card: That early 2000s street style vibe is too good in this little cropped Wrangler jacket. Scored it on Poshmark for $42 and honestly haven't taken it off since it arrived. Tossed it over a baby tee with some chunky sneakers today and the fit is just immaculate. 

  #y2kstyle #denimjacket #poshmarkfinds

    Remembered Denim Jacket — Light Wash, Cropped. Your saved wardrobe has 2 pieces now.

  0 model calls this session, 2 served from cache
  ```

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

`python run_eval.py --label before` wrote
[`results/run_2026-10-13_2045_before.md`](results/run_2026-10-13_2045_before.md).
It ran every scenario in `scenarios.py` five times, with the cache off and
`TEMPERATURE` at 0.9, and made 46 model calls.

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. A matching query completes all three tools | 4 of 5 | FAIL | PASS | FAIL | FAIL | PASS | MISSED (2/5) |
| 2. An impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | FAIL | FAIL | MISSED (3/5) |
| 3. The found item reaches `suggest_outfit` | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit cards name price and platform, and vary | 5 of 5 | FAIL | PASS | FAIL | PASS | PASS | MISSED (3/5) |
| 5. A down model gets a readable message | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

**What each try ran.** Every row is five *different* queries, one per try:
try 1 ran the first query in that criterion's list in `scenarios.py`, try 2
the second, and so on.
- Criteria 3, 4, and 5 each call for 5 different queries.
- Criteria 1 and 2 are tested the same way, so no row is one lucky query
  repeated.
- Each list was picked by a rule, written in its comment in `scenarios.py`,
  before anything ran.

| # | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 |
|---|---|---|---|---|---|
| 1 | vintage graphic tee under $30 | 90s track jacket in size M | silk slip dress in midi length under $40 | platform sneakers size 8 | denim jacket under $50 |
| 2 | designer ballgown size XXS under $5 | platform sneakers size 11 | track jacket under $20 | leather jacket under $40 | red cowboy boots |
| 3 | velvet blazer | chunky knit cardigan | chelsea boots size 8.5 | cargo pants under $30 | crochet halter top size S under $25 |
| 4 | y2k baby tee | corduroy pants | vintage windbreaker | mini shoulder bag | denim shorts |
| 5 (model unreachable) | denim vest | henley | polo shirt | linen trousers | tie-dye long sleeve |

- **Criterion 5's tries ran with the model unreachable.**
  `run_eval.py::model_unreachable` changes one character of `GEMINI_API_KEY`
  for each try, in memory only, and then puts it back. That's the change
  criterion 5 describes, made without editing `.env`.
- **The two harness additions** (both in `run_eval.py`) are one query per
  try (`query_for`) and the model-unreachable mode. The agent itself is
  untouched by them.
- **Not one of the five:** the empty-wardrobe diagnostic
  (`denim jacket under $50`, with an empty wardrobe) completed 5 of 5 with
  general styling advice.

**Real output, one try per criterion.** Each block below is copied from the
results file, which `run_eval.py::write_report` wrote. The run itself is
`agent.py::run_agent`:
- the search is `tools.py::search_listings`, reached through `mcp_server.py`
- the outfit is `tools.py::suggest_outfit`
- the card is `tools.py::create_fit_card`
- the stop messages come from `agent.py::_no_results_message` and
  `agent.py::_model_down_message`

Long outfit texts are cut where marked; they're in full in the results file.

*Criterion 1, try 1 (FAIL)*, `vintage graphic tee under $30`. The model call
in `create_fit_card` failed, although the key was fine:

```
- stopped early: yes — Found Vintage Band Tee — Faded Grey for $19 on depop, but the styling service is unavailable right now, so there's no outfit or fit card this time. Try again in a few minutes. If it keeps failing, check that you're online and that GEMINI_API_KEY in the project's .env file is correct, or create a new key at aistudio.google.com.
- selected_item: Vintage Band Tee — Faded Grey ($19.0, depop)
- search_results: 10
- steps: search_listings → compare_price → suggest_outfit → create_fit_card

[1] search_listings (via MCP)
      in:  description='vintage graphic tee', size=None, max_price=30.0
      out: 10 items: Vintage Band Tee — Faded Grey, Graphic Tee — 2003 Tour Bootleg Style, Y2K Baby Tee — Butterfly Print … +7 more
      →    not empty: selected_item = the first result
[2] compare_price
      in:  Vintage Band Tee — Faded Grey ($19.0, depop)
      out: {'price': 19.0, 'typical_price': 21.5, 'verdict': 'about typical', 'compared_with': 14}
[3] suggest_outfit
      in:  Vintage Band Tee — Faded Grey ($19.0, depop)
      out: Outfit 1: Grunge Streetwear  Wear the Vintage Band Tee tucked into the Baggy straight-leg jeans, dark wash. La…
      →    wardrobe: 10 pieces
[4] create_fit_card
      in:  Vintage Band Tee — Faded Grey ($19.0, depop)
      →    the model couldn't be reached: stop with a message
```

*Criterion 2, try 5 (FAIL)*, `red cowboy boots`. Nothing in the data is red
cowboy boots, but the loop went all the way to a fit card for a crewneck:

```
- stopped early: no
- selected_item: Oversized College Crewneck — Faded Red ($21.0, thredUp)
- search_results: 3
- steps: search_listings → compare_price → suggest_outfit → create_fit_card

Fit card:
Living in this faded red oversized college crewneck because the vintage athletic vibe is just too good. Score it on thredUp for only $21 and it's already my favorite piece for lazy campus days.

#thriftedfashion #oversizedsweater #vintageathletic

[1] search_listings (via MCP)
      in:  description='red cowboy boots', size=None, max_price=None
      out: 3 items: Oversized College Crewneck — Faded Red, Oversized Flannel Shirt — Plaid Red/Black, Suede Chelsea Boots — Tan
      →    not empty: selected_item = the first result
[2] compare_price
      in:  Oversized College Crewneck — Faded Red ($21.0, thredUp)
      out: {'price': 21.0, 'typical_price': 21.0, 'verdict': 'about typical', 'compared_with': 14}
[3] suggest_outfit
      in:  Oversized College Crewneck — Faded Red ($21.0, thredUp)
      out: Outfit 1: Sporty Streetwear Layer your faded red oversized college crewneck over the white ribbed tank top, pa…
      →    wardrobe: 10 pieces
[4] create_fit_card
      in:  Oversized College Crewneck — Faded Red ($21.0, thredUp)
      out: Living in this faded red oversized college crewneck because the vintage athletic vibe is just too good. Score …
      →    with the outfit from suggest_outfit
```

*Criterion 3, try 1 (PASS)*, `velvet blazer`. The second branch swapped the
pick, and the item shown going into `suggest_outfit` is
`session["selected_item"]`. This try then hit the same model failure as
criterion 1, at `create_fit_card`, which criterion 3 doesn't measure:

```
- stopped early: yes — Found Vintage Linen Blazer — Cream for $38 on thredUp, but the styling service is unavailable right now, so there's no outfit or fit card this time. Try again in a few minutes. If it keeps failing, check that you're online and that GEMINI_API_KEY in the project's .env file is correct, or create a new key at aistudio.google.com.
- selected_item: Vintage Linen Blazer — Cream ($38.0, thredUp)
- search_results: 2
- steps: search_listings → compare_price → compare_price → suggest_outfit → create_fit_card

[1] search_listings (via MCP)
      in:  description='velvet blazer', size=None, max_price=None
      out: 2 items: Velvet Blazer — Emerald Green, Vintage Linen Blazer — Cream
      →    not empty: selected_item = the first result
[2] compare_price
      in:  Velvet Blazer — Emerald Green ($52.0, depop)
      out: {'price': 52.0, 'typical_price': 40.0, 'verdict': 'above typical', 'compared_with': 7}
      →    above typical: switch to Vintage Linen Blazer — Cream, then check its price
[3] compare_price
      in:  Vintage Linen Blazer — Cream ($38.0, thredUp)
      out: {'price': 38.0, 'typical_price': 42.0, 'verdict': 'about typical', 'compared_with': 7}
[4] suggest_outfit
      in:  Vintage Linen Blazer — Cream ($38.0, thredUp)
      out: Outfit 1: High-Low Contrast Pair the vintage linen blazer with the white ribbed tank top and baggy straight-le…
      →    wardrobe: 10 pieces
[5] create_fit_card
      in:  Vintage Linen Blazer — Cream ($38.0, thredUp)
      →    the model couldn't be reached: stop with a message
```

*Criterion 4, try 1 (FAIL)*, `y2k baby tee`. The card names depop but writes
the $18 price in words:

```
- selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)
- steps: search_listings → compare_price → suggest_outfit → create_fit_card

Fit card:
Accidentally unlocked peak 2000s mall goth energy with this little butterfly baby tee. Scored it on depop for eighteen bucks and I am never taking it off. Looks so good under an oversized jacket with some beat-up combat boots.

#y2k #babytee
```

*Criterion 5, try 2 (PASS)*, `henley`, with the model unreachable:

```
- stopped early: yes — Found Henley Long Sleeve — Washed Burgundy for $16 on thredUp, but the styling service is unavailable right now, so there's no outfit or fit card this time. Try again in a few minutes. If it keeps failing, check that you're online and that GEMINI_API_KEY in the project's .env file is correct, or create a new key at aistudio.google.com.
- selected_item: Henley Long Sleeve — Washed Burgundy ($16.0, thredUp)
- search_results: 1
- steps: search_listings → compare_price → suggest_outfit

[1] search_listings (via MCP)
      in:  description='henley', size=None, max_price=None
      out: 1 items: Henley Long Sleeve — Washed Burgundy
      →    not empty: selected_item = the first result
[2] compare_price
      in:  Henley Long Sleeve — Washed Burgundy ($16.0, thredUp)
      out: {'price': 16.0, 'typical_price': 21.5, 'verdict': 'below typical', 'compared_with': 14}
[3] suggest_outfit
      in:  Henley Long Sleeve — Washed Burgundy ($16.0, thredUp)
      →    the model couldn't be reached: stop with a message
```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

Each verdict counts the passes in the before run and compares them with the
target written in unit 3. 4 of 5 needs at least 4 passes, and 5 of 5 needs
all five.

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | A matching query completes all three tools | 4 of 5 | **MISSED (2/5)** | A try passes when all three tools run and a fit card comes back. Tries 1, 3 and 4 ended with no card, because the model call failed. 2 passes is under 4. |
| 2 | An impossible query stops before the second tool | 5 of 5 | **MISSED (3/5)** | A try passes when the steps are only `search_listings` and the message names something to change. Tries 4 and 5 picked a listing and called `suggest_outfit`. 3 passes is under 5. |
| 3 | The found item reaches `suggest_outfit` | 5 of 5 | **MET (5/5)** | A try passes when `suggest_outfit` was called and its `in:` line in the trace has the same title, price and platform as `selected_item`. All 5 matched. In try 4 the model failed inside `suggest_outfit`, but the call was made with the right item, which is what this criterion checks. |
| 4 | Fit cards name price and platform, and vary | 5 of 5 | **MISSED (3/5)** | A card passes when it has the price with a `$`, names the platform, and opens with five words (ignoring case and punctuation) that no other card opens with. A run with no card is a miss. Try 1 wrote "eighteen bucks", and try 3 had no card. All openings were different. |
| 5 | A down model gets a readable message | 5 of 5 | **MET (5/5)** | A try passes when it stops with no crash and no outfit or card, and the message says the styling service is unavailable and to try again, with no exception name or status code. All 5 did. The console shows 0 tracebacks. |

**Arguing against my own verdicts.** As the milestone suggests, I gave a
fresh Claude the criteria, the five tries for each, and my verdicts, and asked
it to "argue the opposite verdict as strongly as you can". It found no mark
wrong on a plain reading. Its strongest arguments, and why each verdict
stands:

- **Criterion 1** (the case for MET): the three misses were outages, and
  criterion 5 is where outages are tested, so they shouldn't count here.
  - *Stands as MISSED.* The criterion's own reason counts these. It sets 4 of
    5 because a model call can fail "in ways my loop doesn't handle yet". The
    agent didn't return a fit card, and that's what criterion 1 measures.
- **Criterion 2** (the case for MET): tries 4 and 5 found 3 results, so they
  weren't queries that "match no listings".
  - *Stands as MISSED.* No listing is a leather jacket under $40, and no
    listing is red cowboy boots.
  - If "matches" meant "search returns something", criterion 2 would be
    circular: it would only ever be tested on queries the branch already
    stops.
  - Criteria 3–5 say "return at least one search result" when they mean the
    search; criteria 1 and 2 say "matches".
- **Criterion 3** (the case for MISSED): in try 1 search found the Velvet
  Blazer first, but the Linen Blazer reached `suggest_outfit`. So the "found
  item" didn't reach it.
  - *Stands as MET.* The criterion compares the trace with
    `session["selected_item"]`, not with the first result.
  - The swap is the second branch working on purpose. The trace says so
    ("above typical: switch to Vintage Linen Blazer — Cream"), and the
    velvet blazer is kept in `session["passed_over"]`.
  - One thing this does show: criterion 3's reason ("`run_agent` stores the
    first search result in `session["selected_item"]`") was written before
    the second branch existed, and isn't always true now.
- **Criterion 5** (the case for "not proven"):
  - **The key was changed in memory, not in `.env`.** During a run, only
    `generate._get_client()` reads `GEMINI_API_KEY`, and it reads it from the
    environment at the first model call. That's exactly what the in-memory
    change sets, so the code path is the one a `.env` edit takes.
  - **The run log doesn't show "no stack trace".** `run_eval.py` records any
    exception as a crash. There were 0 crashes, and the run's console output
    has 0 tracebacks.
  - **The message names `GEMINI_API_KEY`.** That's a setting the user put in
    `.env` themselves, not an exception name or a status code.

**Diagnoses**

Seven misses, from **three separate problems**. None of them is in the loop's
branch or the session.

**1. The model call fails and nothing retries it.** This caused 4 misses:
criterion 1 tries 1, 3 and 4, and criterion 4 try 3.
- **Place:** a tool. It's the model call that `suggest_outfit` and
  `create_fit_card` both make through `generate.generate()`. The loop's
  handler did its job: it caught `ModelUnavailable` and stopped with the
  message.
- **Mechanism:** `generate()` retries only errors that look like rate limits:
  "429", "resource … exhaust", or "rate … limit" (`generate.py:326–332`).
  Any other error from the service becomes `ModelUnavailable` on the first
  attempt.
  - In the before run, 7 of the 22 runs that reached the model hit such an
    error with a working key: 4 in `create_fit_card` and 3 in
    `suggest_outfit`, with no pattern by tool or item.
  - Four of those cost a criterion its fit card.
  - The other three landed in tries whose criterion doesn't need the card
    (criterion 2 try 4, criterion 3 tries 1 and 4).
- **Why I think it was the service, not my key, my pacing, or my code:**
  - The same key worked in the other 15 runs in the same process.
  - In criterion 1 try 1, `suggest_outfit` succeeded seconds before
    `create_fit_card` failed.
  - The run averaged about 8 calls a minute against a limit of 15, so the
    pacer never waited, and no 429 retry was printed.
  - Right afterwards, 10 direct calls and a replay of criteria 1 and 4 (20
    more calls) had no errors.
- **What I can't say: which error it was.** My handler shows the user one
  message, by design, and the trace doesn't keep the underlying error. So
  the run log can't tell a passing service error from a dead key, and that's
  a gap of its own.
  - Criterion 1's reason predicted this miss: "a `ModelUnavailable` error can
    occur that nothing catches". It's caught now, but caught means stopped.
- **Update, Milestone 5: now I know which error it was.** During the after
  run the service failed again, more often: 11 of 20 runs. A probe during
  that stretch caught the raw exception twice in six calls. The probe was a
  scratch script that wrapped `generate._explain`; no repo code changed.

  ```
  google.genai.errors.ServerError: 503 UNAVAILABLE. {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}
  ```

  - It's a 503, which `generate()`'s rate-limit check doesn't recognize, so
    it never retries it, even though the service itself says to "try again
    later".
  - The calls that worked in that window took 28–42 seconds, which is why
    the after run took 24 minutes.

**2. Search counts a one-word overlap as a match, so the empty branch never
fires.** This caused 2 misses: criterion 2 tries 4 and 5.
- **Place:** a tool: the `score > 0` filter in `tools.py::search_listings`,
  as it stood for the before run. The loop's branch is
  fine: it stopped all three queries that really came back `[]` (tries 1–3).
- **Mechanism:** a listing is kept if it shares any one word with the
  description (`score > 0`), and ties go to the cheaper listing.
  - "leather jacket under $40": the only listing with both words, the 90s
    Leather Bomber, is $75, so the price filter removes it. What's left are
    one-word matches: the Leather Belt, the Mini Shoulder Bag ("leather"),
    and the Shacket ("jacket" in its description). The belt and the bag both
    score 2, and the $12 belt is cheaper, so the loop styled a belt. It
    should have stopped and said the closest match is $75.
  - "red cowboy boots": no listing has "cowboy". Three listings tie at 2,
    each matching a single word: the Faded Red crewneck, the Plaid Red/Black
    flannel, and the Suede Chelsea Boots. The cheapest, the $21 crewneck,
    won.

**3. The fit card prompt never says how to write the price.** This caused 1
miss, criterion 4 try 1, but it showed up 3 times.
- **Place:** the model's output, from `create_fit_card`'s prompt
  (`tools.py::create_fit_card`: the lines "I just bought this on {platform}
  for {price}." and "Mention the item, the price ({price})…").
- **Mechanism:** the prompt gives the price as "for $18" and asks to "Mention
  … the price ($18)", but it never says to write it that way. At
  `TEMPERATURE` 0.9, in the casual voice the prompt asks for, the model
  sometimes spells it out.
  - Across all 15 cards in the before run, 3 did: "eighteen bucks",
    "forty four dollars" and "forty-two bucks".
  - Only the first was in a criterion 4 try. The other two were in criterion
    3 and the diagnostic, which don't score the card.
  - It's also the same $18 tee whose unit 3 cards said "eighteen dollars" and
    "18 dollars".

**The pattern.** Four of the seven misses are one cause in one place: the
model call, with no retry. Two are one cause in `search_listings`, and one is
the prompt. Criterion 3, the session handoff, held 5 of 5 even in the runs
where the model failed afterwards. So the plain-code parts of the agent did
what the criteria asked, and every miss is at an edge: the service, the data
matching, or the model's wording.

**The two criteria I met.** Neither target can go higher than 5 of 5, but
each one tests less than it could.
- **Criterion 3** checks only the half of the handoff that is plain code. A
  tighter version: the same listing is also the input to `create_fit_card`,
  and its fit card names that listing's price. Tries 1 and 4 show why that
  matters: the run can fail after the handoff, and criterion 3 can't see it.
- **Criterion 5** only tests a dead key, which fails the same way every time.
  The failure that actually hurt this run was a passing one. A tighter
  version: "when the service fails once on a model call, the run still
  completes, 5 of 5". Today that would fail, because nothing retries.

---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

`agent.py::run_agent` writes one `trace.step()` for each tool call, after the
tool returns. Each step has the tool, what went in (`in:`), what came back
(`out:`), and a note on the branch it took (`→`).
- The search step is named `search_listings (via MCP)`, because that call
  goes through `mcp_client.call_tool` to `mcp_server.py`.
- Steps are only recorded once `trace.start_trace()` has run. `ask --trace`
  starts it, and so does `run_eval.py` on every try. A plain `ask` prints no
  trace.
- Since unit 4 stretch item 2, `compare_price` goes over MCP too, so a run
  today shows `compare_price (via MCP)` where the traces below say
  `compare_price`. See Unit 4 Stretch Features for a current trace.
- The happy-path and second-branch traces below were re-recorded after
  Milestone 5's strict matching.
  - The happy path's search now returns 1 item instead of 10, and it's the
    same item.
  - `velvet blazer` no longer switches, so `vintage levi's jeans` shows the
    second branch instead.

**Happy path** (four steps, with the MCP call first)

```
$ python app.py ask 'vintage graphic tee under $30, size M' --trace
[1] search_listings (via MCP)
      in:  description='vintage graphic tee', size='M', max_price=30.0
      out: 1 items: Y2K Baby Tee — Butterfly Print
      →    not empty: selected_item = the first result
[2] compare_price
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: {'price': 18.0, 'typical_price': 21.5, 'verdict': 'below typical', 'compared_with': 14}
[3] suggest_outfit
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: Outfit 1: Streetwear Contrast Pair the Y2K Baby Tee — Butterfly Print with baggy straight-leg jeans, dark wash…
      →    wardrobe: 10 pieces
[4] create_fit_card
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: Total soft grunge fairy vibes with this little butterfly tee. Got it on depop for eighteen dollars and I am so…
      →    with the outfit from suggest_outfit

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop
  Price:    $18, below the typical $21.50 for tops

  Outfit:   Outfit 1: Streetwear Contrast
Pair the Y2K Baby Tee — Butterfly Print with baggy straight-leg jeans, dark wash to balance the fitted top. Throw the black cropped zip hoodie on top and finish the look with chunky white sneakers.

Outfit 2: Casual Grunge
Wear the Y2K Baby Tee — Butterfly Print tucked into wide-leg khaki trousers, accented by the brown leather belt. Layer the vintage black denim jacket over it and anchor the outfit with black combat boots.

  Fit card: Total soft grunge fairy vibes with this little butterfly tee. Got it on depop for eighteen dollars and I am so obsessed with the pastel print. Going to wear it with baggy denim and beat up sneakers all week.

#y2k #thrifthaul #babytee

0 model calls this session, 2 served from cache
```

This is the same query as the Sample Run, so its outfit and card came from the
cache.

**Empty search** (one step: the branch stops before `suggest_outfit`)

Recorded before unit 4's stretch retry. Today this query has a size, so it
searches once more without `XXS` before stopping with the same message: two
steps. Unit 4 Stretch Features, item 3, has that trace.

```
$ python app.py ask 'designer ballgown size XXS under $5' --trace
[1] search_listings (via MCP)
      in:  description='designer ballgown', size='XXS', max_price=5.0
      out: [] (empty)
      →    empty: stop here, suggest_outfit is never called

  Nothing in the listings matches 'designer ballgown' at any size or price. Try a broader word for the item, like 'dress', 'jacket' or 'tee'. Also, nothing is listed under $5 (the cheapest listing is $12), and no listing comes in size XXS.

0 model calls this session
```

**Second branch** (an overpriced pick switched to a cheaper close match, so
`compare_price` runs twice)

```
$ python app.py ask "vintage levi's jeans" --trace
[1] search_listings (via MCP)
      in:  description="vintage levi's jeans", size=None, max_price=None
      out: 2 items: Vintage Levi's 501 Jeans — Medium Wash, Straight Leg Black Jeans — Faded
      →    not empty: selected_item = the first result
[2] compare_price
      in:  Vintage Levi's 501 Jeans — Medium Wash ($38.0, depop)
      out: {'price': 38.0, 'typical_price': 30.0, 'verdict': 'above typical', 'compared_with': 9}
      →    above typical: switch to Straight Leg Black Jeans — Faded, then check its price
[3] compare_price
      in:  Straight Leg Black Jeans — Faded ($30.0, thredUp)
      out: {'price': 30.0, 'typical_price': 30.0, 'verdict': 'about typical', 'compared_with': 9}
[4] suggest_outfit
      in:  Straight Leg Black Jeans — Faded ($30.0, thredUp)
      out: Outfit 1: Grunge Monochrome  Pair the straight leg black jeans — faded with the white ribbed tank top tucked i…
      →    wardrobe: 10 pieces
[5] create_fit_card
      in:  Straight Leg Black Jeans — Faded ($30.0, thredUp)
      out: Total 90s indie sleaze vibes with these faded black Levi's straight legs. Scored them on thredUp for just $30 …
      →    with the outfit from suggest_outfit
```

### Failure modes, triggered on purpose

All three were triggered on purpose, one at a time. The model-down one was the
only one that crashed, so it's the only one that got a new handler.

**1. Empty search.** A query the data can't match. It stops before
`suggest_outfit` (trace above) and names what to change. This was handled in
unit 3, so nothing changed.

```
$ python app.py ask 'designer ballgown size XXS under $5'

  Nothing in the listings matches 'designer ballgown' at any size or price. Try a broader word for the item, like 'dress', 'jacket' or 'tee'. Also, nothing is listed under $5 (the cheapest listing is $12), and no listing comes in size XXS.

0 model calls this session
```

**2. Empty wardrobe.** `suggest_outfit` gets `{"items": []}`. It returns
general advice that doesn't claim you own anything: no crash, and not an empty
string. This was also handled in unit 3, so nothing changed.

```
$ python app.py ask 'denim jacket under $50' --empty-wardrobe
(running with an empty wardrobe)

  Found:    Denim Jacket — Light Wash, Cropped — $42.0 on poshmark
  Price:    $42, about the typical $40 for outerwear

  Outfit:   Outfit 1: Layer the cropped Wrangler jacket over a black ribbed cotton midi dress and white canvas low-top sneakers for an easy, casual weekend look.

Outfit 2: Pair it with high-waisted pleated wide-leg trousers in beige, a fitted white baby tee, and chunky retro running shoes to lean into a streetwear vibe.

Styling tip: Because the jacket is cropped and light wash, balance your proportions by pairing it with high-waisted bottoms to elongate your silhouette and define your waist.

  Fit card: Weekend indie sleaze energy is officially back. Snagged this cropped Wrangler denim jacket on Poshmark for $42 and it's already my new go-to layer. Honestly obsessed with how the light wash goes with literally everything in my closet.

#thriftedfashion #wrangler #streetwear

2 model calls this session, 458 prompt + 169 output tokens
```

**3. Model unavailable.**
- **How I triggered it:** one character of `GEMINI_API_KEY` was changed in
  memory after `config.py` loaded `.env`, so the file itself was never
  edited. The cache was off (`AI201_CACHE=0`), and the query was one I hadn't
  run before. The trigger was a small script:

  ```python
  import os, sys
  import config                                    # loads .env into os.environ
  key = os.environ["GEMINI_API_KEY"]
  os.environ["GEMINI_API_KEY"] = key[:-1] + ("x" if key[-1] != "x" else "y")
  import app
  sys.argv = ["app.py", "ask", "corduroy wide-leg pants under $40", "--trace"]
  app.main()
  ```

- **Before the handler, it crashed:**
  - `ModelUnavailable` came up out of `run_agent`.
  - `app.py`'s catch-all printed the exception's name and exited with status 1.
  - The search had worked, but nothing on screen said what it found.

  ```
  ModelUnavailable: The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com.

  1 model calls this session
  ```

- **The handler:**
  - `run_agent` catches `ModelUnavailable` around `suggest_outfit` and
    `create_fit_card`.
  - It puts a message in `session["error"]` and stops.
  - The message says what broke, what still worked, and what to try. It has
    no exception name and no status code.
- **After:**

  ```
  [1] search_listings (via MCP)
        in:  description='corduroy wide-leg pants', size=None, max_price=40.0
        out: 5 items: Corduroy Wide-Leg Pants — Rust, Wide-Leg Linen Trousers — Natural, Low-Rise Cargo Pants — Khaki … +2 more
        →    not empty: selected_item = the first result
  [2] compare_price
        in:  Corduroy Wide-Leg Pants — Rust ($32.0, depop)
        out: {'price': 32.0, 'typical_price': 30.0, 'verdict': 'about typical', 'compared_with': 9}
  [3] suggest_outfit
        in:  Corduroy Wide-Leg Pants — Rust ($32.0, depop)
        →    the model couldn't be reached: stop with a message

    Found Corduroy Wide-Leg Pants — Rust for $32 on depop, but the styling service is unavailable right now, so there's no outfit or fit card this time. Try again in a few minutes. If it keeps failing, check that you're online and that GEMINI_API_KEY in the project's .env file is correct, or create a new key at aistudio.google.com.

  1 model calls this session
  ```

- **Checked by a reader with no context.** As the milestone suggests, I gave
  all three messages to a fresh Claude with the course prompt ("tell me what I
  would try next as a user who can't see the code… Don't rewrite them for
  me").
  - None of the three left it with nothing to try.
  - Message 1: it would search "dress under $20" with no size.
  - Message 2: it would save wardrobe pieces.
  - Message 3: it would retry in a few minutes, then check the connection and
    the key.
  - The one gap was in message 3. The first version said to check
    `GEMINI_API_KEY` in your .env file but not where that file is, or how to
    get a new key. So it now says "the project's .env file" and points to
    aistudio.google.com, which `generate.py`'s own explanation already
    mentioned. The output above is the re-run after that change.

**On the MCP move:**

- **What changed in the code:**
  - `mcp_server.py` registers `search_listings`. Its description is written
    for an agent that can't see the code, so it names the units (US dollars,
    inclusive) and the types, and says that no match returns an empty list.
    The input names and types are the ones in the Tool Inventory.
  - In `agent.py::run_agent`, the search step calls
    `call_tool("search_listings", {...})` instead of the function.
  - Each call starts the server, asks, and stops it again, which adds about
    0.8 seconds to a run (a direct call takes about 1 ms).
  - `_no_results_message` still calls `search_listings` directly. It only
    words the advice in the "nothing found" message and isn't a loop step.
- **Did anything behave differently afterwards?** No.
  - A check compared the MCP result with a direct call on 10 inputs: with and
    without a size and a price, an empty description, and an impossible
    query. All 10 matched exactly, and the value types matched too, so prices
    stayed floats.
  - `python app.py ask 'vintage graphic tee under $30'` found the same Vintage
    Band Tee as before.
- **One difference from what the starter documents:** before the tool was
  registered, the client's message "The server doesn't offer a tool called…"
  never reached the screen. It came out as "unhandled errors in a TaskGroup
  (1 sub-exception)" instead, because the error is raised inside an async
  task group and gets wrapped on the way out. A misspelled tool name, such
  as `call_tool('search_listing', ...)`, gets the same unhelpful message.
- **What the move meant later:** when Milestone 5 made matching strict, the
  tool's description in `mcp_server.py` had to change in the same commit as
  the code. That description is a published contract now. An agent built
  against the old wording would still expect one shared word to count as a
  match.



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:** strict matching in `tools.py::search_listings`.
- A listing is now kept only if it contains **every** description keyword,
  where before it took just one. The plural and stopword rules didn't
  change.
- In code it's one condition, `if not wanted <= _listing_words(listing)[1]:
  continue`, plus a small helper so the filter and the score read the same
  words.
- Nothing else in the agent changed. The MCP tool's description in
  `mcp_server.py` and the Tool Inventory now say "every word", because the
  published contract has to match what the tool does.

**Which failure it was meant to fix:** diagnosis 2, criterion 2's tries 4
and 5.
- "leather jacket under $40" styled a leather belt, and "red cowboy boots"
  styled a red crewneck. One shared word was enough to count as a match, so
  the loop's empty-search branch never fired.
- **Why this one first.** Diagnosis 1, the model errors, caused more misses.
  But those errors came and went, and no single run can show a fix for them
  working on demand. Search is plain code, so one run can show for certain
  whether this change worked. The retry for diagnosis 1 is a stretch item
  (see Unit 4 Stretch Features).
- **Checked before running anything:** I applied the rule to all 25 scenario
  queries. Only the two misses changed (both now stop), and the other 23
  kept the same pick.

### Run Log — After

`python run_eval.py --label after` wrote
[`results/run_2026-10-13_2156_after.md`](results/run_2026-10-13_2156_after.md).
It used the same scenarios, the same five queries per row, and the same
settings (cache off, `TEMPERATURE` 0.9), and made 40 model calls.

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. A matching query completes all three tools | 4 of 5 | FAIL | FAIL | FAIL | FAIL | PASS | MISSED (1/5) |
| 2. An impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. The found item reaches `suggest_outfit` | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit cards name price and platform, and vary | 5 of 5 | FAIL | FAIL | FAIL | FAIL | PASS | MISSED (1/5) |
| 5. A down model gets a readable message | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

Why each try failed:
- **Criterion 1:** tries 1–4 failed because the model call failed, three
  times in `create_fit_card` and once in `suggest_outfit`.
- **Criterion 4:**
  - Tries 2 and 4 failed because the model call failed, so there was no card.
  - Tries 1 and 3 spelled out the price: "eighteen bucks" and "forty bucks".
- **The empty-wardrobe diagnostic** completed 3 of 5. The other two were cut
  off by the same model failure.

**Before and after, side by side**

| Criterion | Target | Before | After | What moved it |
|---|---|---|---|---|
| 1. A matching query completes all three tools | 4 of 5 | MISSED (2/5) | MISSED (1/5) | Model failures went from 3 to 4. Not this change |
| 2. An impossible query stops before the second tool | 5 of 5 | MISSED (3/5) | **MET (5/5)** | **This change**: both weak-spot queries now stop |
| 3. The found item reaches `suggest_outfit` | 5 of 5 | MET (5/5) | MET (5/5) | No change |
| 4. Fit cards name price and platform, and vary | 5 of 5 | MISSED (3/5) | MISSED (1/5) | Model failures went from 1 to 2, and spelled-out prices from 1 to 2. Not this change |
| 5. A down model gets a readable message | 5 of 5 | MET (5/5) | MET (5/5) | No change |

**Did it help, and how I know:**

- **Yes, for the failure it was meant to fix.**
  - Criterion 2 went from 3/5 to 5/5. Both former misses now stop at
    `search_listings` and name what to change. The first now says "No
    listings matched 'leather jacket' under $40. The closest match, 90s
    Leather Bomber — Black, is $75: raise your max price to at least $75…".
    The second says "Nothing in the listings matches 'red cowboy boots' at
    any size or price…".
  - This isn't luck. Search is plain code with no model in it, so these
    queries stop the same way every time, and the check script runs them
    directly too.
  - A bonus from the same fix: the "platform sneakers size 11" message now
    offers only US 8. Before, it also offered US 7 and US 9, which were the
    Mary Janes and the canvas sneakers that loose matching had let in.
- **Criteria 1 and 4 got worse, and not because of this change.**
  - The change only touches `search_listings`, and every criterion 1, 3, 4
    and 5 query picked the same listing as in the before run. I checked that
    before running, and both run logs show it. The one exception is
    `velvet blazer`, covered below.
  - What changed was the model service. This time 11 of the 20 runs that
    reached the model failed, against 7 of 22 before. The run took 24
    minutes instead of 6, because even the calls that worked were slow.
  - A probe during the slowdown finally caught the raw error (see the
    update under diagnosis 1): `503 UNAVAILABLE … This model is currently
    experiencing high demand.`
  - Criterion 4 also had two cards spell out the price, which is diagnosis 3.
    This change doesn't touch that.
- **What it cost.** Strict matching can now stop on a query a person would
  call a match.
  - "comfy denim jacket" finds nothing, because no listing says "comfy",
    even though a denim jacket exists. The stop message then says "Try a
    broader word for the item, like … 'jacket'", which the user already
    typed.
  - `velvet blazer` now finds only the velvet blazer, since the linen blazer
    doesn't say "velvet". So the second branch no longer switches for it,
    and criterion 3's try 1 now tests a plain handoff instead of a switched
    one. `vintage levi's jeans` still switches (see the Loop Trace).
  - Both points are in What's Still Broken.


---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->

After the improvement, two criteria are still missed. Here's what I'd do
about each, and why I stopped where I did.

**Criterion 1, MISSED (1/5 after, 2/5 before): model outages end the run.**
- **What's broken:** the model service sometimes answers `503 UNAVAILABLE`
  ("high demand… usually temporary… try again later"). `generate()` retries
  only rate-limit errors, so a 503 becomes `ModelUnavailable` on the first
  attempt, and the handler stops the run.
- **What I'd do:**
  1. Retry a 503 inside `generate.py`, once or twice with a short wait,
     before giving up, the same way it already retries a 429.
  2. Record the underlying error in the trace, but not in the user's
     message, so a run log can tell a passing 503 from a dead key.
  3. With that recorded, the message could also stop telling someone with a
     503 to check their key.
- **Why I stopped:**
  - Milestone 5 allows one change, and strict matching was the one I could
    measure cleanly.
  - The retry is the declared stretch improvement, measured in its own run.
  - The catch: a run where the service happens to behave can't show the
    retry working, so its measurement depends on the service.
- **Update after the stretch:** step 1 is now built, as the second measured
  improvement. Criterion 1 was MET (5/5) in the third run. The retry
  caught the one 503 that run hit, though most of the jump came from a
  healthier service (see Unit 4 Stretch Features, item 1). Steps 2 and 3
  are still open.

**Criterion 4, MISSED (1/5 after, 3/5 before): two causes.**
- **The same 503s:** 2 of the 5 tries ended with no card. The fix above
  covers these.
- **Spelled-out prices:** "eighteen bucks" and "forty bucks" in the after
  run. Across both runs, 6 of 24 cards wrote the price without digits. The
  prompt shows the price as "$18" but never says to write it that way.
- **What I'd do:**
  - Change the prompt to "write the price exactly as $18, with the dollar
    sign and digits, never in words".
  - More robust: check the card in code. If the exact `$18` isn't in it,
    regenerate once.
- **Why I stopped:**
  - It was the third diagnosis.
  - It's noisy to measure: one bad card in five before the change.
  - Fixing it alongside search would have mixed two changes in one after
    run.
- **Update after the stretch:** with the outages retried, criterion 4's third
  run missed 2/5 for this reason alone. 9 of 20 cards wrote the price in
  words ("18 dollars", "32 dollars", "forty bucks"). This prompt fix is now
  the only thing between criterion 4 and its target.

**Also still broken, outside the five criteria.** The first two were found by
a fresh code review after the after run. I'm writing them down rather than
changing the agent again: this unit allows one improvement, and a further
change after the measured runs wouldn't be measured.
- **Strict matching sometimes stops when it shouldn't, and the advice then
  dead-ends.**
  - Six everyday phrasings now all stop with "Try a broader word for the
    item, like 'dress', 'jacket' or 'tee'": "cheap denim jacket", "comfy
    denim jacket", "a nice jacket for fall", "denim jacket in good
    condition", "cute summer dress", and "jeans for $30 or less" (the parser
    leaves "or less" in).
  - That advice is a dead end, because the user often already typed
    "jacket" or "dress". It never names the word that actually blocked the
    match ("cheap").
  - Next step: when the full description finds nothing, name the word or
    words whose removal brings results back. Or require only the item word
    ("jacket") and use the other words for ranking.
  - I stopped because loosening the rule needs its own measured run, and the
    strict rule is what made criterion 2 pass.
- **When only the fit card fails, the message hides an outfit that was
  made.**
  - If `suggest_outfit` succeeds and then `create_fit_card` hits a 503,
    `session["outfit_suggestion"]` holds a finished outfit, but the message
    says "there's no outfit or fit card this time" and `app.py` shows only
    the message.
  - This happened in 10 of the logged tries: 4 before, 6 after. Criterion 1
    try 1, pasted under Run Log — Before, is one of them.
  - No verdict depends on it. Criteria 1 and 4 still had no card, and
    criterion 5's model fails at `suggest_outfit`.
  - Next step: give a card failure its own message ("here's your outfit,
    but the fit card couldn't be written"), and have `app.py` print the
    outfit when there is one. I corrected `run_agent`'s docstring, which
    claimed the later fields stay `None`.
- **Criterion 3 lost its switched try.** `velvet blazer` no longer triggers
  the second branch, so criterion 3's try 1 now tests a plain handoff.
  - The scenario list should use a query that still switches, such as
    `vintage levi's jeans`.
  - I kept the scenarios fixed so that before and after stay comparable.
- **The starter's MCP client hides a useful error.** "The server doesn't
  offer a tool called…" comes out as "unhandled errors in a TaskGroup". That
  file is given plumbing, so I left it alone.
- **Small wording and parsing gaps from unit 3:**
  - "Only US 8 is listed for it: try one of those" reads oddly when only one
    size is listed.
  - `tee under $1,000` reads the ceiling as $1.
  - `30 or less` isn't read as a price.
  - `anything for me under $20` says nothing matches "for me", instead of
    asking what item you want.


---

## Unit 4 Stretch Features

Declared here **before any of them is built**. Each one gets its own commit
after this one. Once it's built, this section will say what it changed and
show the run where it happened. They're built in the order listed: the
second improvement comes first, so its run log measures that one change and
nothing else.

### 1. A second measured improvement: retry a passing model error

- **What it fixes:** diagnosis 1.
  - `generate()` retries only rate-limit errors. So a `503 UNAVAILABLE`
    ("This model is currently experiencing high demand… Please try again
    later") ends the run on the first attempt.
  - That caused 4 of the 7 misses in the before run, and hit 11 of the 20
    runs that reached the model in the after run.
- **The change:** in `generate.py::generate`:
  - Treat temporary server errors (503 UNAVAILABLE, and its relatives 500
    INTERNAL and 504 DEADLINE_EXCEEDED) like a rate limit. Wait, try again,
    and say so on screen, using the same attempts and backoff the 429 retry
    already uses.
  - If every attempt fails, raise `ModelUnavailable` as before, so the
    handler's message still shows.
  - A rejected key (400) or an unknown model name (404) still fails at once,
    so criterion 5 is unaffected.
- **How it will be measured:** `python run_eval.py --label second`.
  - A third run log in the same table format, compared row by row with Run
    Log — After.
  - The console's retry lines show whether the retry fired at all. If the
    service behaves during that run, the run can't show the retry working,
    and I'll say so.
- **Status:** built.
  - In `generate.py`, a new `_server_busy()` recognizes 500, 503 and 504
    errors. `generate()` now retries those on the same backoff as a 429,
    printing a `[model busy]` line each time.
  - If every attempt is busy, it raises `ModelUnavailable`, so the agent's
    handler still shows its message.
  - The check script (fake client, no real calls) confirmed the rest:
    - A 400 rejected key and a 404 unknown model still fail on the first
      attempt.
    - 429s behave exactly as before.
    - A 503 on `create_fit_card` no longer ends the run.

**Run Log — Third**

`python run_eval.py --label second` wrote
[`results/run_2026-10-13_2231_second.md`](results/run_2026-10-13_2231_second.md).
It ran the same scenarios and the same five queries per row with the cache
off, and made 46 model calls.

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. A matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. An impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. The found item reaches `suggest_outfit` | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit cards name price and platform, and vary | 5 of 5 | FAIL | FAIL | FAIL | PASS | PASS | MISSED (2/5) |
| 5. A down model gets a readable message | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

- Criterion 4's three FAILs all wrote the price in words: "18 dollars", "32
  dollars" and "forty bucks". Every try produced a card.
- The empty-wardrobe diagnostic completed 5 of 5.

**All three runs side by side**

| Criterion | Target | Before | After (strict matching) | Third (plus the retry) |
|---|---|---|---|---|
| 1. A matching query completes all three tools | 4 of 5 | MISSED (2/5) | MISSED (1/5) | **MET (5/5)** |
| 2. An impossible query stops before the second tool | 5 of 5 | MISSED (3/5) | MET (5/5) | MET (5/5) |
| 3. The found item reaches `suggest_outfit` | 5 of 5 | MET (5/5) | MET (5/5) | MET (5/5) |
| 4. Fit cards name price and platform, and vary | 5 of 5 | MISSED (3/5) | MISSED (1/5) | MISSED (2/5) |
| 5. A down model gets a readable message | 5 of 5 | MET (5/5) | MET (5/5) | MET (5/5) |
| *Runs stopped by a model error, outside criterion 5* | — | 7 of 22 | 11 of 20 | **0 of 20** |
| *Cards with the price written in words* | — | 3 of 15 | 3 of 9 | 9 of 20 |

**Did it help, and how I know:** yes, but this run can only show it once.

- **The retry fired once, and that once mattered.** The console of the third
  run shows it in criterion 1, try 2:

  ```
  A matching query completes all three tools  (example wardrobe)
    try 1 [vintage graphic tee under $30]: completed — fit card 222 chars
    …  (try 2's live trace lines, cut here)
    [model busy] the service answered 503 UNAVAILABLE. Waiting 1s, then trying again (attempt 1 of 5).
    try 2 [90s track jacket in size M]: completed — fit card 279 chars
  ```

  - In the after run, this same try ended with the "styling service is
    unavailable" message (in the before run it passed).
  - Here the second attempt worked, and the try passed. Without the retry,
    criterion 1 would have been 4/5. That still meets its target of 4 of 5,
    but only just.
- **Most of the jump from 1/5 to 5/5 was the service, not my change.**
  - This run hit one busy answer in 46 calls. The after run had 11 runs
    stopped by 503s, with calls taking 30–40 seconds.
  - So this run shows the retry working, but not how much it would save on a
    bad day like the after run.
  - A fair way to measure that would be to run the same scenarios while the
    service is struggling, with and without the retry. I can't schedule
    that.
- **What it didn't fix: criterion 4.** With the outages gone, every one of
  criterion 4's misses is diagnosis 3. Across the run, 9 of 20 cards wrote the
  price in words.
  - That's the problem I left for What's Still Broken.
  - It now limits criterion 4 on its own. If the service stays healthy, the
    price wording is the one thing between criterion 4 and its target.
- **Cost:** a retried call is one more request. This run spent 46 calls (45
  plus 1 retry), and the free tier allows 500 a day. On a bad day each failing
  call could take up to 5 attempts.

### 2. A second tool on MCP: `compare_price`

- **What:** `mcp_server.py` registers `compare_price(item: dict) -> dict`
  next to `search_listings`.
  - Its description will be written for someone who can't see the code:
    prices in US dollars, the ±15% band, and the "no comparison" empty case.
  - `run_agent`'s price step calls it through `mcp_client.call_tool`, and so
    does `_better_deal`, which uses it to choose whether to switch.
  - `switch_line` only formats a line for the screen, so it keeps calling it
    directly.
- **Why this tool:** it makes no model call. A model tool behind MCP would
  run in a separate process that never sees `run_eval.py`'s cache-off switch
  or criterion 5's broken key. That's Moment 5 under How I Used AI.
- **How it will be shown:**
  - A check that the MCP result equals the direct result for all 40
    listings.
  - A `--trace` run with both MCP calls visible: `search_listings (via MCP)`
    and `compare_price (via MCP)`.
- **Status:** built.
  - `mcp_server.py` registers `compare_price(item: dict) -> dict`, with a
    description that names dollars, the ±15% band, and the "no comparison"
    case.
  - `agent.py` has a small `_check_price(item)` that calls
    `call_tool("compare_price", {"item": item})`. The price step and
    `_better_deal` use it.
- **What it changed:**
  - **The trace:** the price step now shows as `compare_price (via MCP)`.
    `session["steps"]` still says `compare_price`.
  - **Speed:** each check starts the server once, about 0.8 seconds, like
    the search. A switched run makes three of them: the pick, the cheaper
    candidate inside `_better_deal`, and the new pick. The candidate check
    isn't a loop step, so the trace shows two.
  - **Results:** nothing. A check compared the MCP result with a direct call
    for all 40 listings, an empty item, an item with no price, and a
    category with nothing to compare. All matched, value types included.
- **The server now offers both:**

  ```
  $ python mcp_client.py
  Asking mcp_server.py what it offers…

    search_listings
      …
      - description: string
      - size: string  (optional)
      - max_price: number  (optional)

    compare_price
      …
      - item: object
  ```

  (`…` stands for each tool's description, cut here for length.)

- **A run through both MCP tools** (outfit and card from the cache, 0 model
  calls):

  ```
  $ python app.py ask "vintage levi's jeans" --trace
  [1] search_listings (via MCP)
        in:  description="vintage levi's jeans", size=None, max_price=None
        out: 2 items: Vintage Levi's 501 Jeans — Medium Wash, Straight Leg Black Jeans — Faded
        →    not empty: selected_item = the first result
  [2] compare_price (via MCP)
        in:  Vintage Levi's 501 Jeans — Medium Wash ($38.0, depop)
        out: {'price': 38.0, 'typical_price': 30.0, 'verdict': 'above typical', 'compared_with': 9}
        →    above typical: switch to Straight Leg Black Jeans — Faded, then check its price
  [3] compare_price (via MCP)
        in:  Straight Leg Black Jeans — Faded ($30.0, thredUp)
        out: {'price': 30.0, 'typical_price': 30.0, 'verdict': 'about typical', 'compared_with': 9}
  [4] suggest_outfit
        in:  Straight Leg Black Jeans — Faded ($30.0, thredUp)
        out: Outfit 1: Grunge Monochrome  Pair the straight leg black jeans — faded with the white ribbed tank top tucked i…
        →    wardrobe: 10 pieces
  [5] create_fit_card
        in:  Straight Leg Black Jeans — Faded ($30.0, thredUp)
        out: Total 90s indie sleaze vibes with these faded black Levi's straight legs. Scored them on thredUp for just $30 …
        →    with the outfit from suggest_outfit

    Found:    Straight Leg Black Jeans — Faded — $30.0 on thredUp
    Price:    $30, about the typical $30 for bottoms
    Switched from Vintage Levi's 501 Jeans — Medium Wash ($38, above the typical $30 for bottoms) to this cheaper close match.
  ```

### 3. Retry an empty search without the size

- **What:** when a search with a size comes back empty, the loop searches
  once more without the size.
  - If that finds something, the run goes on with it and says what it
    dropped, for example "Nothing came in size 11, so I searched again
    without the size."
  - If it still finds nothing, the run stops with the same message as
    before.
  - It retries once at most, and only when a size was given.
- **Where:** `agent.py::run_agent`. The search step hands off to a new
  `retry` step, the session gets a `dropped` field, and `app.py` prints the
  line.
- **How it will be shown:** `python app.py ask 'platform sneakers size 11'
  --trace`. The trace will show the second `search_listings (via MCP)` call
  and a note naming the dropped size.
- **What it will change:** criterion 2's `platform sneakers size 11` try
  would no longer stop. Instead it would style the US 8 pair, and say so.
  That trade is the point of the feature. All three run logs above are
  recorded before it exists.
- **Status:** built.
  - `run_agent`'s search step hands an empty result that had a size to a new
    `retry` step. That step calls `search_listings` over MCP again with the
    same description and price but `size=None`.
  - If that finds something, `session["dropped"]` becomes `"size 11"` and
    the run carries on. If not, the run stops with the original message.
  - `retry_line(session)` words it, and `app.py` prints it. The line names
    the price ceiling too, if there was one, and the size of what was found.
    For example: "Nothing came in size S under $40, so I searched again
    without the size: this one is size M/L." The final review caught that a
    first version said "Nothing came in size S", which is false when a size
    S exists over the ceiling.
  - The retry happens at most once, because the `retry` step never leads
    back to `search`.
  - Queries without a size don't change.
- **Run log: the retry, and the constraint it dropped** (outfit and card from
  the cache, 0 model calls):

  ```
  $ python app.py ask 'platform sneakers size 11' --trace
  [1] search_listings (via MCP)
        in:  description='platform sneakers', size='11', max_price=None
        out: [] (empty)
        →    empty: try once more without the size
  [2] search_listings (via MCP)
        in:  description='platform sneakers', size=None, max_price=None
        out: 1 items: Platform Sneakers — White Chunky Sole
        →    dropped size 11: selected_item = the first result
  [3] compare_price (via MCP)
        in:  Platform Sneakers — White Chunky Sole ($48.0, poshmark)
        out: {'price': 48.0, 'typical_price': 44.0, 'verdict': 'about typical', 'compared_with': 3}
  [4] suggest_outfit
        in:  Platform Sneakers — White Chunky Sole ($48.0, poshmark)
        out: Outfit 1: Streetwear Layers Pair the chunky white sneakers with the baggy straight-leg jeans, dark wash and th…
        →    wardrobe: 10 pieces
  [5] create_fit_card
        in:  Platform Sneakers — White Chunky Sole ($48.0, poshmark)
        out: Living in these chunky platform sneakers for that ultimate 90s skater vibe. Scored this pair on poshmark for $…
        →    with the outfit from suggest_outfit

    Nothing came in size 11, so I searched again without the size: this one is size US 8.
    Found:    Platform Sneakers — White Chunky Sole — $48.0 on poshmark
    Price:    $48, about the typical $44 for shoes
  ```

- **When the retry finds nothing too, the run stops as before**, with the
  same message:

  ```
  $ python app.py ask 'designer ballgown size XXS under $5' --trace
  [1] search_listings (via MCP)
        in:  description='designer ballgown', size='XXS', max_price=5.0
        out: [] (empty)
        →    empty: try once more without the size
  [2] search_listings (via MCP)
        in:  description='designer ballgown', size=None, max_price=5.0
        out: [] (empty)
        →    still empty without size XXS: stop, suggest_outfit is never called

    Nothing in the listings matches 'designer ballgown' at any size or price. Try a broader word for the item, like 'dress', 'jacket' or 'tee'. Also, nothing is listed under $5 (the cheapest listing is $12), and no listing comes in size XXS.
  ```

- **What it changed:**
  - **Criterion 2.** In the before, after and third run logs,
    `platform sneakers size 11` stopped. Today it styles the US 8 pair
    instead, and says the size was dropped.
    - So a fourth run would score that try FAIL against criterion 2 as
      written ("stops before calling `suggest_outfit`").
    - That's the trade this feature makes on purpose. Someone who wears an 11
      gets a near miss they can judge, not a dead end.
    - The criterion's other four tries still stop. The two with a size
      (ballgown, size 11) now make two searches each.
  - **The session** has a new field, `dropped`.
  - **`--remember`** no longer saves a find the retry got in another size,
    and it says why. Saving it would build later outfits around shoes the
    user can't wear.
  - **The trace** for a query with a size that finds nothing now shows two
    search steps instead of one.
  - **The checks:** four older checks assumed one search for the ballgown
    query, and were updated to two. A new check covers the rest: the retry,
    the dropped size, the unchanged message, no retry without a size, and
    no retry when the size finds something.

<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**

---

## Capstone

Unit 9. Everything above this heading is from units 3 and 4 and stays as it
was. Everything this unit asks for is below it.

**What This Extends**

FitFindr, the agent from units 3 and 4. It searches 40 secondhand listings
(`search_listings`, over MCP), checks the price (`compare_price`, over MCP),
and asks the model for an outfit (`suggest_outfit`) and a caption
(`create_fit_card`). Until now it only ran on my laptop, one command at a
time (`python app.py ask`, `run_eval.py`).

What's new:
- **It runs on a host with a URL:** `serve.py` under gunicorn, on Render's
  free tier.
- **Every `/ask` request writes one structured log record** (one JSON
  line), including requests that are rejected or crash. Each record holds
  when the request came in, the query, the status, what came out, the
  error, how long it took, how long it waited its turn, and the model calls
  and tokens it used.
- **The records can be read back three ways:** `results/serve_log.jsonl` on
  the machine running it, the host's log viewer (stdout), and `GET /log`.

**The Shape**

**A: deploy and instrument.** The agent already works. What it lacked was
the operational layer around it: a run path that isn't my editor, a record
of every request, and numbers that come out of that record. The cost per
run is measured from the logged token counts, not from the pricing page.

Out of scope. I considered these and decided against them:
- **Changing what the agent does.** `agent.py`, `tools.py` and the MCP
  server stay as they are, so anything the log shows comes from running the
  agent, not from new behavior.
- **A log that outlives the free host.** No database and no log drain. The
  free instance wipes its files when it sleeps, so I copy the records into
  the repo the same day I make them.
- **More than one request at a time.** It stays one at a time, as
  `serve.py` ships: one sync worker and the lock. A real queue, or more
  workers on a 512 MB instance, would be a different project.

**Stretch Features**

Declared here before any of them is built. The first two are built
alongside the milestones they belong to. The last two come after
Milestone 7.

1. **A latency breakdown.** Every log record also carries how many
   milliseconds each stage took: `search_listings` and `compare_price` over
   MCP, `suggest_outfit`, and `create_fit_card`. They're timed in `serve.py`
   around the agent's calls, without changing `agent.py`. The README will
   give the numbers and say which stage dominates. Built in Milestone 2,
   with the logging.
2. **Both run paths.** Hosted on Render, and documented as a local run
   (`python serve.py`), with a note on what differed between them: setup,
   latency, cost or behavior. Built in Milestone 3.
3. **A second measured improvement.** A second change drawn from the
   diagnosis, with a third run log in the same format and a statement of
   whether it helped.
4. **A load observation.** The hosted service run at about ten times its
   normal request rate, with what changed: latency, errors, cost, or
   nothing.

**Running It**

Path A, hosted: **https://fitfindr-am5n.onrender.com**. It's a free web
service on Render, deployed from `render.yaml` as a Blueprint on the `main`
branch, so a merge to `main` redeploys it. It also runs locally from one
command (stretch 2, below). [RUNNING.md](RUNNING.md), under "Capstone: where
it runs", has both: the URL and how it got there, the build and start
commands, the environment and Python version, and the local steps.

Checking the local steps turned up one problem: `serve.py` listens on port
5000 by default, and on a Mac the AirPlay Receiver already listens there and
answers a `curl` with a 403. RUNNING.md now uses port 5001 and says why. With
that change, a fresh clone of the GitHub repo ran as written: venv,
`pip install`, `.env` (I linked the existing one instead of pasting the key
again), the server, `curl`, and the measured run below.

**Both Run Paths (stretch 2)**

The same code and the same twelve requests (`measure.py`), one at a time,
with the cache off, on 2026-11-18. The reports are
`results/measure_hosted_2026-11-18_1826.md` and
`results/measure_local_2026-11-18_1828.md`.

| | Hosted (Render free tier) | Local (my Mac) |
|---|---|---|
| Setup | Render signup, a Blueprint from `render.yaml`, the key pasted into the dashboard. First build: 1 min 4 s | A fresh clone, venv, `pip install`, `.env`, and port 5001 instead of 5000 |
| Server | gunicorn, one sync worker | Flask's development server |
| Time per completed run, server-side `duration_ms`: median (mean) | 10.1 s (11.7 s) | 3.6 s (7.5 s) |
| Slowest run, and why | 25.6 s: the first request after the deploy (first MCP process 9.1 s, first model call 8.6 s) | 37.4 s: one `create_fit_card` call took 35.6 s at the model, with no retry |
| One MCP call (search or price) | about 4 s | about 0.5 s |
| Tokens per run | 728 in, 185 out | 723 in, 180 out |
| Waking up after 15 idle minutes | 17.3 s for `GET /health` (a warm one: 0.27 s). The log was empty afterwards: the twelve records below survive only because `measure.py` saved them | Never needed: it doesn't sleep |
| A second request sent while one runs (two impossible queries at once, 0 model calls) | The second client waited 22.6 s, but its record says `duration_ms` 9,192 and `waited_ms` 0, and its `ts` is 13 s late: gunicorn's one sync worker holds it before `serve.py` sees it | The second record shows `waited_ms` 1,388 of its 2,345 ms, matching its client's 2.35 s: Flask's server hands it to `serve.py`, which waits on the lock |
| The log file | Wiped when the instance sleeps; stdout stays in Render's Logs tab | Stays on disk |
| Outcomes | 10 fit cards, the 400, the crash 500 | The same |

What differed is how long a run takes, not what comes out. A typical run on
the host takes about three times as long, and almost all of the difference
is the two MCP calls (see the latency breakdown). The tokens, and so the
cost, are the same, because the prompts are the same.

**Instrumentation**

Each `/ask` request writes one record, whatever happens to it: a run that
finishes, a run that stops early, a 400, or a crash. The record goes to three
places: stdout (Render's Logs tab keeps it), `results/serve_log.jsonl` on the
machine running it, and `GET /log?n=` (the file's last n lines).
`serve.py::ask` writes it, in a `finally` around the route.

| Field | What it holds |
|---|---|
| `ts`, `request_id`, `route` | When it came in (UTC), a short id (also sent back as `X-Request-Id`), and `/ask` |
| `query` | **What came in:** the `query` field, or the raw body when there isn't one |
| `status`, `outcome`, `item`, `error` | **What came out:** the HTTP status; `fit_card`, `stopped`, `rejected` or `crashed`; the listing it picked; the error text |
| `duration_ms`, `waited_ms` | **How long:** arrival to response, and the part of that spent waiting for the one-at-a-time lock |
| `model_calls`, `tokens_in`, `tokens_out` | This run's share of `generate.py`'s running totals: the count after the run minus the count before |
| `stages_ms` | Milliseconds per stage: `search_listings` and `compare_price` (both over MCP), `suggest_outfit` and `create_fit_card` (the model) |

Here are twelve records from the hosted service, exactly as `GET /log`
returned them, from `results/measure_hosted_2026-11-18_1826.md`
(`measure.py::main`). The first ten are matching queries. The last two are
failures:
- **An empty query:** rejected, 400.
- **A JSON list body:** crashed, 500. `serve.py` assumes the body is a
  dict, and the log records that bug rather than fixing it.

```jsonl
{"ts": "2026-11-18T23:24:14.292+00:00", "request_id": "ae98d068", "route": "/ask", "status": 200, "query": "vintage graphic tee under $30", "outcome": "fit_card", "item": "Vintage Band Tee — Faded Grey ($19.0, depop)", "error": null, "duration_ms": 25623, "waited_ms": 0, "model_calls": 2, "tokens_in": 726, "tokens_out": 188, "stages_ms": {"search_listings": 9110, "compare_price": 3907, "suggest_outfit": 8579, "create_fit_card": 4025}}
{"ts": "2026-11-18T23:24:40.042+00:00", "request_id": "b54c2876", "route": "/ask", "status": 200, "query": "90s track jacket in size M", "outcome": "fit_card", "item": "90s Track Jacket — Navy/White Stripe ($45.0, poshmark)", "error": null, "duration_ms": 12404, "waited_ms": 0, "model_calls": 2, "tokens_in": 724, "tokens_out": 184, "stages_ms": {"search_listings": 3961, "compare_price": 4211, "suggest_outfit": 3533, "create_fit_card": 699}}
{"ts": "2026-11-18T23:24:53.028+00:00", "request_id": "58d7503c", "route": "/ask", "status": 200, "query": "silk slip dress in midi length under $40", "outcome": "fit_card", "item": "90s Silk Slip Dress — Floral, Midi Length ($30.0, depop)", "error": null, "duration_ms": 9835, "waited_ms": 0, "model_calls": 2, "tokens_in": 771, "tokens_out": 218, "stages_ms": {"search_listings": 3883, "compare_price": 4098, "suggest_outfit": 950, "create_fit_card": 904}}
{"ts": "2026-11-18T23:25:03.019+00:00", "request_id": "dbd97c03", "route": "/ask", "status": 200, "query": "platform sneakers size 8", "outcome": "fit_card", "item": "Platform Sneakers — White Chunky Sole ($48.0, poshmark)", "error": null, "duration_ms": 10126, "waited_ms": 0, "model_calls": 2, "tokens_in": 712, "tokens_out": 180, "stages_ms": {"search_listings": 4080, "compare_price": 4206, "suggest_outfit": 995, "create_fit_card": 844}}
{"ts": "2026-11-18T23:25:13.266+00:00", "request_id": "2b53e9cf", "route": "/ask", "status": 200, "query": "denim jacket under $50", "outcome": "fit_card", "item": "Denim Jacket — Light Wash, Cropped ($42.0, poshmark)", "error": null, "duration_ms": 9410, "waited_ms": 0, "model_calls": 2, "tokens_in": 726, "tokens_out": 180, "stages_ms": {"search_listings": 3839, "compare_price": 3909, "suggest_outfit": 816, "create_fit_card": 845}}
{"ts": "2026-11-18T23:25:23.025+00:00", "request_id": "836562a2", "route": "/ask", "status": 200, "query": "chunky knit cardigan", "outcome": "fit_card", "item": "Knit Cardigan — Chunky Brown ($35.0, depop)", "error": null, "duration_ms": 10018, "waited_ms": 0, "model_calls": 2, "tokens_in": 748, "tokens_out": 199, "stages_ms": {"search_listings": 4069, "compare_price": 4106, "suggest_outfit": 1137, "create_fit_card": 705}}
{"ts": "2026-11-18T23:25:33.184+00:00", "request_id": "38e2d0f1", "route": "/ask", "status": 200, "query": "cargo pants under $30", "outcome": "fit_card", "item": "Low-Rise Cargo Pants — Khaki ($27.0, poshmark)", "error": null, "duration_ms": 9229, "waited_ms": 0, "model_calls": 2, "tokens_in": 715, "tokens_out": 162, "stages_ms": {"search_listings": 3810, "compare_price": 3906, "suggest_outfit": 962, "create_fit_card": 549}}
{"ts": "2026-11-18T23:25:42.562+00:00", "request_id": "02cc7241", "route": "/ask", "status": 200, "query": "y2k baby tee", "outcome": "fit_card", "item": "Y2K Baby Tee — Butterfly Print ($18.0, depop)", "error": null, "duration_ms": 9899, "waited_ms": 0, "model_calls": 2, "tokens_in": 724, "tokens_out": 181, "stages_ms": {"search_listings": 4246, "compare_price": 4001, "suggest_outfit": 943, "create_fit_card": 707}}
{"ts": "2026-11-18T23:25:52.853+00:00", "request_id": "ab283328", "route": "/ask", "status": 200, "query": "corduroy pants", "outcome": "fit_card", "item": "Corduroy Wide-Leg Pants — Rust ($32.0, depop)", "error": null, "duration_ms": 10328, "waited_ms": 0, "model_calls": 2, "tokens_in": 708, "tokens_out": 160, "stages_ms": {"search_listings": 4560, "compare_price": 3813, "suggest_outfit": 1173, "create_fit_card": 699}}
{"ts": "2026-11-18T23:26:03.324+00:00", "request_id": "39a04dfb", "route": "/ask", "status": 200, "query": "mini shoulder bag", "outcome": "fit_card", "item": "Mini Shoulder Bag — Tan Leather ($38.0, poshmark)", "error": null, "duration_ms": 10596, "waited_ms": 0, "model_calls": 2, "tokens_in": 721, "tokens_out": 197, "stages_ms": {"search_listings": 4071, "compare_price": 4407, "suggest_outfit": 921, "create_fit_card": 1196}}
{"ts": "2026-11-18T23:26:14.062+00:00", "request_id": "7c2534fd", "route": "/ask", "status": 400, "query": "", "outcome": "rejected", "item": null, "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-18T23:26:14.182+00:00", "request_id": "7f468d3b", "route": "/ask", "status": 500, "query": "[1, 2]", "outcome": "crashed", "item": null, "error": "AttributeError: 'list' object has no attribute 'get'", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
```

**Latency Breakdown (stretch 1)**

These numbers come from the `stages_ms` of the hosted records above. The
first request after the deploy is shown on its own; the other nine are warm.

| Stage | Warm runs (9): mean | Share of the run | First run after the deploy |
|---|---|---|---|
| `search_listings` (MCP) | 4.06 s | 40% | 9.11 s |
| `compare_price` (MCP) | 4.07 s | 40% | 3.91 s |
| `suggest_outfit` (model) | 1.27 s | 12% | 8.58 s |
| `create_fit_card` (model) | 0.79 s | 8% | 4.03 s |
| Everything else | 0.01 s | 0% | 0.00 s |
| Total (`duration_ms`) | 10.21 s | | 25.62 s |

**On the host, the MCP stages dominate: 80% of a warm run.**
- **Why:** each `call_tool` starts `mcp_server.py` as a new Python process,
  and that process imports the MCP library and the tools before it does any
  work.
- **Measured on my Mac:** that import takes 0.5 s, while a bare Python start
  takes 0.02 s. The search itself is plain code over 40 listings.
- **On Render's free-tier CPU:** the same start takes about 4 s.
- **The model:** the two model calls together take about 2 s.
- **Locally, the picture flips:** MCP is 14% of a run and the model 86%.

**What It Costs**

**Measured per run** (the mean of the ten hosted runs above, cache off):
**727.5 input tokens and 184.9 output tokens, from 2 model calls.** The ten
local runs came to 722.9 and 179.6.

How I measured it:
- `generate.py` adds up the token counts the API reports on every response
  (`usage_metadata`).
- `serve.py` reads that total before and after each run, and logs the
  difference as `tokens_in` and `tokens_out`.
- `measure.py` sent ten matching queries to the hosted service with the
  cache off (`AI201_CACHE=0`), and I averaged the ten records.
- To check that these counts are what Google bills, I looked at one call's
  full usage. It had no thinking tokens (`thoughts_token_count` was empty),
  and the total was exactly input plus output.

**In dollars**, at Gemini 3.5 Flash-Lite's paid-tier price on Google's pricing
page (checked 2026-11-18): $0.30 per million input tokens, and $2.50 per
million output tokens, thinking included.

```
input:   727.5 × $0.30 / 1,000,000 = $0.000218
output:  184.9 × $2.50 / 1,000,000 = $0.000462
one run                            = $0.000680
```

**A hundred people a day, one query each:**

```
model:    100 runs × $0.000680 = $0.068 a day   (× 30 = $2.04 a month)
quota:    100 runs × 2 calls   = 200 model requests a day
compute:  100 runs × 10.2 s    = 1,020 s, about 17 minutes of the instance a day
```

**What I actually pay is $0.** My key is on the free tier, and Render's free
instance costs nothing. The free tier's real limit is 500 model requests a
day, which is 250 runs:
- A hundred people asking once each fits: 200 requests.
- A hundred people asking three times each doesn't: 300 runs is 600
  requests. That would need the paid tier, at 300 × $0.000680 = $0.20 a
  day.

**Checked again in the trials.** Criterion 5 recomputed the cost from the
logged tokens on 30 more runs, across the before and after sets. The trial
means were $0.000630–$0.000688, and every run made exactly 2 model calls. So
the $0.00068 per run above holds, and so does the hundred-a-day arithmetic.

**Run Log and Verdicts**

The before run is three trials against the hosted service, following the
"One trial" steps in `criteria.md`. It ran on 2026-11-18 from `trials.py::main`
and cost 32 model calls. The full output, with every request and every log
record, is in `results/capstone_before_2026-11-18_1940.md`.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Warm runs return a fit card in under 8 s | 4 of 5, 3 of 3 trials | 0/5 | 0/5 | 0/5 | MISSED |
| 2. A malformed request gets a 400 | 5 of 5, 3 of 3 trials | 2/5 | 2/5 | 2/5 | MISSED |
| 3. The log's time matches the wait when requests overlap | 2 of 2, 3 of 3 trials | 1/2 | 1/2 | 1/2 | MISSED |
| 4. Every request leaves one matching record | all, 3 of 3 trials | 13/13 | 12/12 | 12/12 | MET |
| 5. 2 model calls, mean cost ≤ $0.0008 | 5 of 5 and mean ≤ $0.0008, 3 of 3 trials | 5/5, $0.000630 | 5/5, $0.000671 | 5/5, $0.000665 | MET |

Real output follows, from trial 3 unless a line says otherwise. The client
times come from `trials.py::curl`. The records come from `serve.py::ask`,
read back through `GET /log`.

**Criterion 1.** Client times for the five runs were 8.9–10.4 s across all three
trials, so no run came in under 8 s. A typical record:
```jsonl
{"ts": "2026-11-19T00:39:12.200+00:00", "request_id": "39947acb", "route": "/ask", "status": 200, "query": "90s track jacket in size M", "outcome": "fit_card", "item": "90s Track Jacket — Navy/White Stripe ($45.0, poshmark)", "error": null, "duration_ms": 8972, "waited_ms": 0, "model_calls": 2, "tokens_in": 721, "tokens_out": 162, "stages_ms": {"search_listings": 3656, "compare_price": 3703, "suggest_outfit": 936, "create_fit_card": 676}}
```

**Criterion 2.** The same three bodies failed in all three trials:

| Body | Status | X-Request-Id |
|---|---|---|
| `[1, 2]` | 500, HTML page | none |
| `{"query": 42}` | 500, HTML page | none |
| `"vintage tee"` | 500, HTML page | none |
| `{"query": ""}` | 400, JSON `error` | yes |
| `not json` | 400, JSON `error` | yes |

Two of the crash records:
```jsonl
{"ts": "2026-11-19T00:39:57.968+00:00", "request_id": "3231ba60", "route": "/ask", "status": 500, "query": "[1, 2]", "outcome": "crashed", "item": null, "error": "AttributeError: 'list' object has no attribute 'get'", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T00:39:58.129+00:00", "request_id": "d4ffa0db", "route": "/ask", "status": 500, "query": 42, "outcome": "crashed", "item": null, "error": "AttributeError: 'int' object has no attribute 'strip'", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
```

**Criterion 3.** Both requests were sent at the same moment. The ballgown
client took 7,843 ms and the wetsuit client 15,538 ms. Their records:
```jsonl
{"ts": "2026-11-19T00:39:58.955+00:00", "request_id": "9c1be737", "route": "/ask", "status": 200, "query": "designer ballgown size XXS under $5", "outcome": "stopped", "item": null, "error": "Nothing in the listings matches 'designer ballgown' at any size or price. Try a broader word for the item, like 'dress', 'jacket' or 'tee'. Also, nothing is listed under $5 (the cheapest listing is $12), and no listing comes in size XXS.", "duration_ms": 7691, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {"search_listings": 7608}}
{"ts": "2026-11-19T00:40:06.646+00:00", "request_id": "9a9c7601", "route": "/ask", "status": 200, "query": "wetsuit size XXS", "outcome": "stopped", "item": null, "error": "Nothing in the listings matches 'wetsuit' at any size or price. Try a broader word for the item, like 'dress', 'jacket' or 'tee'. Also, no listing comes in size XXS.", "duration_ms": 7699, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {"search_listings": 7613}}
```
The wetsuit record says 7,699 ms, but its client waited 15,538 ms, so 7,839 ms is
missing from the log. Its `ts` is 7.7 s after the moment it was sent. All three
trials looked the same: 7,375–8,091 ms was missing each time.

**Criterion 4.** Each trial's records lined up one for one with the requests
sent: 13 in trial 1, which had a warm-up, and 12 in trials 2 and 3. Every
`status` matched what the client saw, including the three HTML 500s. The
trial 3 records, in order:

| Part | Statuses |
|---|---|
| Criterion 1 | 200 ×5 |
| Criterion 2 | 500, 500, 500, 400, 400 |
| Criterion 3 | 200, 200 |

**Criterion 5.** Every criterion 1 record showed `model_calls` 2. The mean cost
per trial was $0.000630, $0.000671 and $0.000665. The most expensive single
run cost $0.000746 (chunky knit cardigan: 745 tokens in, 209 out), under the
$0.0010 per-run cap.

**Verdicts and diagnoses (before run)**

- **1. MISSED (0/5 in every trial): `mcp_client.call_tool`, run twice per
  request on Render's free CPU.**
  - The runs took 8.9–10.4 s. The two MCP stages alone took 7.1–8.5 s of
    that, and the model only 1.3–2.2 s.
  - Each `call_tool` starts `mcp_server.py` as a new Python process, and
    that process imports the MCP SDK before it does anything. That takes
    0.53 s on my Mac and about 3.7 s on the host.
  - The mechanism: latency scales with process starts (two per run), not
    with the work. The search itself is plain code over 40 listings.
- **2. MISSED (2/5 in every trial): `serve.py::_answer`, the body
  parsing.**
  - The code assumes the JSON body is a dict holding a string. A list or a
    bare string fails on `.get`, and a number fails on `.strip`.
  - The `AttributeError` escapes the route, so Flask answers with its own
    HTML 500. That page has no `X-Request-Id`, so nobody can find its record
    in the log.
- **3. MISSED (1/2 in every trial): gunicorn's single sync worker, from the
  start command in `render.yaml`.**
  - A sync worker accepts one connection at a time. The second request
    waits in the socket queue, before Flask, so `serve.py`'s clock (and its
    `ts`) starts only when the first request finishes.
  - So the record is short by exactly the first request's run time:
    7,375–8,091 ms, against first runs of 7.2–8.0 s. `waited_ms` stays 0,
    because the lock is never contended.
- **4. MET** and **5. MET.**
  - The `finally` logged every request, including the three crashes per
    trial.
  - Every run made exactly 2 model calls, with a highest mean of $0.000671.
  - Both have room: no retry and no worker kill happened in these 3 trials.
    5's mean sits 16% under its cap.

**The pattern:** 1 and 3 both come from the deploy layer, not the agent.
Render's free CPU makes the per-call process start expensive (1), and
gunicorn's default worker hides the queue from the app (3). Both were
invisible on my Mac, where an MCP start costs 0.5 s and Flask's server is
threaded. 2 is a plain input-handling bug in `serve.py`.

**The Improvement**

- **What I changed:** criterion 3's miss, by switching the start command in
  `render.yaml` from `--workers 1` to `--workers 1 --threads 2`. I also
  updated the comment in `serve.py` and the start-command row in RUNNING.md.
- **Why:** with two threads, gunicorn accepts the second request at once.
  It reaches `serve.py::ask`, which starts its clock, and then waits on the
  one-at-a-time lock. `waited_ms` and `duration_ms` now include the wait
  instead of missing it.
- **What stays the same:**
  - The lock still runs one agent at a time, so the 512 MB budget is the
    same.
  - A worker thread has no running event loop, so `mcp_client`'s
    `asyncio.run()` still works (gevent would break it).
- **Checked locally first** (gunicorn on my Mac, 0 model calls). Two
  impossible queries sent at once:
  - With one sync worker, the second client waited 3.31 s and its record
    said 1,293 ms, with `waited_ms` 0.
  - With `--threads 2`, the client waited 2.58 s and its record said
    2,579 ms, with `waited_ms` 1,485.
- **Why this miss and not the others:** it's the log's own truthfulness,
  which is what this unit added. The change is one line, and it follows
  directly from the diagnosis. Criterion 1's fix (keeping one MCP process
  open) is a much bigger change to given plumbing, so it's in What's Still
  Broken. Criterion 2's fix is the declared second improvement.

**Run Log — After** (2026-11-18, `trials.py::main`, 32 model calls. Full output
in `results/capstone_after_2026-11-18_2101.md`.)

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Warm runs return a fit card in under 8 s | 4 of 5, 3 of 3 trials | 0/5 | 0/5 | 0/5 | MISSED |
| 2. A malformed request gets a 400 | 5 of 5, 3 of 3 trials | 2/5 | 2/5 | 2/5 | MISSED |
| 3. The log's time matches the wait when requests overlap | 2 of 2, 3 of 3 trials | **2/2** | **2/2** | **2/2** | **MET** (was MISSED) |
| 4. Every request leaves one matching record | all, 3 of 3 trials | 13/13 | 12/12 | 12/12 | MET |
| 5. 2 model calls, mean cost ≤ $0.0008 | 5 of 5 and mean ≤ $0.0008, 3 of 3 trials | 5/5, $0.000683 | 5/5, $0.000680 | 5/5, $0.000688 | MET |

Criterion 3, after, trial 3. The two requests now arrive together (their `ts`
values are 4 ms apart). The one that queued records its wait: the client took
17,771 ms, and the record shows `duration_ms` 17,623 with `waited_ms` 9,115.
```jsonl
{"ts": "2026-11-19T02:00:46.901+00:00", "request_id": "d7268185", "route": "/ask", "status": 200, "query": "wetsuit size XXS", "outcome": "stopped", "item": null, "error": "Nothing in the listings matches 'wetsuit' at any size or price. Try a broader word for the item, like 'dress', 'jacket' or 'tee'. Also, no listing comes in size XXS.", "duration_ms": 9120, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {"search_listings": 9037}}
{"ts": "2026-11-19T02:00:46.905+00:00", "request_id": "820dd2c0", "route": "/ask", "status": 200, "query": "designer ballgown size XXS under $5", "outcome": "stopped", "item": null, "error": "Nothing in the listings matches 'designer ballgown' at any size or price. Try a broader word for the item, like 'dress', 'jacket' or 'tee'. Also, nothing is listed under $5 (the cheapest listing is $12), and no listing comes in size XXS.", "duration_ms": 17623, "waited_ms": 9115, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {"search_listings": 8506}}
```

**Did it help?**
- **Yes, for what it targeted.** Criterion 3 went from 1/2 to 2/2 in every
  trial.
  - Before the fix, 7,375–8,091 ms went missing from each queued record.
  - After it, the gaps between client and log were 112–269 ms across all
    six requests.
  - The queued request's `waited_ms` was 7,909–9,115 ms, where before it was
    always 0.
- **Nothing else changed verdict.** 1 and 2 still miss for the reasons
  diagnosed, and 4 and 5 still hold.
- **What it cost elsewhere:**
  - **Criterion 1's run times doubled,** from a median of 9.5 s to 18.7 s
    (up to 28.3 s). All of the extra time was in the two model stages, often
    7–16 s each against about 1 s before. The MCP stages didn't move: a
    median of 8.2 s, against 7.6 s.
  - **The likely cause is the model service, not the threads.** I checked
    with 4 extra model calls right after the run:
    - Two direct `generate()` calls from my Mac, with no server and no
      threads, took 9.0 s and 2.6 s (about 1 s each earlier in the day).
    - A hosted run took 35.7 s in `suggest_outfit` alone.
    - A worker setting on Render can't slow a call made from my laptop, so
      the slowdown came from the shared free-tier key or the service.
  - **What I didn't rule out:** that the threads add a little on top.
    Settling it would mean running the before and after configurations in
    the same hour.
  - **Either way,** criterion 1 misses with MCP alone (7–8.5 s of the 8 s
    budget).
- **The real cost of the fix:** two threads accept two connections at once,
  so a queued request now holds a thread while it waits on the lock. That's
  free at two requests. Under heavy load, gunicorn would queue the third, the
  same blind spot one step later. The load observation will show whether
  that happens.

**What's Still Broken**

Two criteria are still missed after the improvement.

**Criterion 1, MISSED (0/5 in every trial): warm runs take 9–10 s, not
under 8.**
- **What I'd do:** keep one MCP server process open and reuse its session,
  instead of starting `mcp_server.py` for each call. That removes about
  3.7 s per call on the host, or about 7.5 s per run, which would put a warm
  run near 2–3 s.
- **Why I stopped:** it means rewriting `mcp_client.call_tool`, given
  plumbing that wraps `asyncio.run()` around one connection per call. A
  long-lived session needs its own event loop in a thread, and has to
  restart if the server dies. That's more than a one-change improvement
  should carry, and it touches unit 4's MCP evidence.

**Criterion 2, MISSED (2/5 in every trial): three malformed bodies get
Flask's HTML 500.**
- **What I'd do:** in `serve.py::_answer`, reject anything that isn't a JSON
  object with a string `query`, with the same JSON 400 the empty query
  already gets. That's about five lines.
- **Why I stopped:** the one improvement went to criterion 3, the log's own
  accuracy. This fix is the declared second improvement (stretch), so it
  will get its own measured run.

**Also broken, outside the five criteria:**
- **The queue blind spot moved, but it isn't gone.** Two threads accept two
  requests, so a third arriving while two are in flight waits in gunicorn's
  queue, unseen, as before.
- **The log is gone when the free instance sleeps** (the log was empty after
  the 17.3 s wake-up in M3). The copies in `results/` exist only because
  `measure.py` and `trials.py` saved them.
- **`generate.py`'s 300-calls-per-process budget** was built for a CLI
  session. A server that makes 300 model calls without restarting (150 runs)
  would start answering every request with a 500. The free instance's sleep
  resets it, so I never reached it.
- **`GET /log` is public.** It holds shopping queries only (no keys, no
  wardrobe), but anyone with the URL can read them.

**The one thing I'd do first:** the persistent MCP session (criterion 1).
- It's the biggest cost on every single request: 80% of a warm run, for
  every user.
- Criterion 2's fix only matters to callers who send broken JSON.
- If this were real, a user waits 10 s for every answer today; with the fix,
  they'd wait 2–3 s.

**How I Used AI**

**1. The after run looked worse, and I asked for proof before blaming the
fix.**
- **What I asked:** after the threaded-worker fix, I asked Claude to run
  the after set and compare it with the before.
- **What I got:**
  - Criterion 3 was fixed, but criterion 1's run times had doubled (a median
    of 9.5 s became 18.7 s).
  - Instead of calling it the fix's cost or calling it noise, Claude showed
    that all of the extra time was inside the two model stages, while the MCP
    stages hadn't moved.
  - It asked whether my other project was using the shared key at the time.
- **What I changed:**
  - I wasn't sure, so I approved a 4-call probe. A direct model call from my
    Mac, with no server and no threads, also took 9.0 s, so the slowdown
    followed the model service, not my change.
  - "Did it help" now reports both the win and the slowdown, with the probe
    and what it didn't rule out.

**2. A fresh model's scope check was wrong about my own code.**
- **What I asked:** at Milestone 1 I used the brief's prompt: break the
  extension into its separate pieces and count them.
- **What I got:** six pieces. One claim was that logging token counts would
  need a change to the agent, because "the agent doesn't expose these
  today."
- **What I changed:**
  - Nothing in the plan. `generate.py` already keeps running totals
    (`call_count()`, `token_counts()`), so `serve.py` subtracts the count
    before a run from the count after it, and `agent.py` stayed untouched.
  - I kept `/log` as the only optional piece, and recorded the other five as
    what Shape A requires.

**Stretch: Second Improvement (criterion 2)**

- **What I changed:** `serve.py::_answer` now treats anything that isn't a
  JSON object holding a string `query` the same way as an empty query: a JSON
  400 with an `error` and an `X-Request-Id`. It is three lines, following the
  diagnosis that the code assumed a dict holding a string.
- **The third run** (2026-11-18, `trials.py::main`, 32 model calls). Full
  output in `results/capstone_third_2026-11-18_2215.md`.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Warm runs return a fit card in under 8 s | 4 of 5, 3 of 3 trials | 0/5 | 0/5 | 0/5 | MISSED |
| 2. A malformed request gets a 400 | 5 of 5, 3 of 3 trials | **5/5** | **5/5** | **5/5** | **MET** (was MISSED) |
| 3. The log's time matches the wait when requests overlap | 2 of 2, 3 of 3 trials | 2/2 | 2/2 | 2/2 | MET |
| 4. Every request leaves one matching record | all, 3 of 3 trials | 13/13 | 12/12 | 12/12 | MET |
| 5. 2 model calls, mean cost ≤ $0.0008 | 5 of 5 and mean ≤ $0.0008, 3 of 3 trials | 5/5, $0.000673 | 5/5, $0.000662 | 5/5, $0.000695 | MET |

The three bodies that used to crash, from trial 3:
```jsonl
{"ts": "2026-11-19T03:15:22.300+00:00", "request_id": "eb6d2def", "route": "/ask", "status": 400, "query": "[1, 2]", "outcome": "rejected", "item": null, "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T03:15:22.466+00:00", "request_id": "8f5333fd", "route": "/ask", "status": 400, "query": 42, "outcome": "rejected", "item": null, "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
{"ts": "2026-11-19T03:15:22.615+00:00", "request_id": "78bf6f5f", "route": "/ask", "status": 400, "query": "\"vintage tee\"", "outcome": "rejected", "item": null, "error": "Send JSON with a 'query' field, e.g. {\"query\": \"vintage graphic tee under $30\"}", "duration_ms": 0, "waited_ms": 0, "model_calls": 0, "tokens_in": 0, "tokens_out": 0, "stages_ms": {}}
```

**Did it help?**
- **Yes.** Criterion 2 went from 2/5 to 5/5 in every trial, and all five
  bodies now carry a request id that leads to their record.
- **What it cost:** nothing seen. The other four criteria kept their
  verdicts.
- **One trade to be aware of:** the error message is the same for every bad
  body, so a caller who sent `{"query": 42}` is told to send a `query`
  field, not that the field must be text.
- **A side result on the after run's slowdown:** this run still has the
  threaded worker, yet criterion 1's median came back to 10.3 s (from
  18.7 s), with model stages at a median of 1.8 s. That supports the probe:
  the after run's slow model calls came from the service, not from
  `--threads 2`.

**What's still broken, updated:** only criterion 1 is still missed. What I'd
do about it, and why I stopped, is unchanged (see What's Still Broken).
