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
  ceiling and size, then ranks what's left by how many of the description's
  keywords each one contains.
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
  - *How results are ranked:* each listing scores one point per description
    keyword found in its title, description, category, style tags, colors,
    or brand. Keywords in the title count twice. Common words like "a" and
    "for" are dropped, and a trailing "s" is ignored, so `tees` matches
    `tee`. Ties go to the cheaper listing.
- **When it has nothing:** an empty list `[]`, never `None` and never an
  exception. Listings that score 0 are dropped, so an empty or all-filler
  `description` also returns `[]`.

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
all, that raises `ModelUnavailable`, which the loop doesn't catch yet. That's
unit 4.

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
  `session["selected_item"]` and checks its price with `compare_price`.
- **Second branch (stretch):** if that pick is above typical and the search
  results hold a cheaper close match (same category, same item word in the
  title, not above typical itself), the loop switches to it, keeps the
  original in `session["passed_over"]`, and checks the new pick's price.
  Otherwise it goes on to `suggest_outfit`, then `create_fit_card`.

**Where it lives:** `agent.py::run_agent`. It's a `while` loop over named
steps (search → price → suggest → card → done), and every pass calls
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
4. `selected_item` (`search_results[0]`, unless the second branch switches
   to a cheaper close match)
5. `price_check` (what `compare_price` said; stretch tool, see below)
6. `passed_over` (only set when the second branch switched)
7. `outfit_suggestion`
8. `fit_card`

`steps` lists the tool each loop step called, in order:
`["search_listings", "compare_price", "suggest_outfit", "create_fit_card"]` on
a full run, with `compare_price` twice when the second branch switched (the old
pick, then the new one), and
`["search_listings"]` when the branch stops it. `error` is set only when the
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
  - **Known limit:** matching is loose (see Unit 4 notes), so a switch can
    contradict a word you typed. For example, `'blue jeans'` switches to the
    black jeans. If matching gets stricter in Unit 4, `'velvet blazer'`
    stops switching (`'graphic tee'` still would), so this run log will need
    re-capturing.
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

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

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

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



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
