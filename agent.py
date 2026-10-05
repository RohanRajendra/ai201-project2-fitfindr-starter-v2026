"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""

import re

import config
import trace
from tools import search_listings, suggest_outfit, create_fit_card, _price, _size_tokens
from utils.data_loader import load_listings
from generate import ModelUnavailable


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
        "steps": [],                 # tools called, in order
    }


# ── query parsing ─────────────────────────────────────────────────────────────

_PRICE_PATTERNS = [
    # "under $30", "below 30", "less than $30", "up to $30", "max $30 dollars"
    re.compile(
        r"\b(?:under|below|less than|up to|max(?:imum)?|no more than|at most)"
        r"\s*\$?\s*(\d+(?:\.\d{1,2})?)(?:\s*(?:dollars|bucks|usd)\b)?",
        re.I,
    ),
    re.compile(r"\$\s*(\d+(?:\.\d{1,2})?)"),                                 # "$30"
    re.compile(r"\b(\d+(?:\.\d{1,2})?)\s*(?:dollars|bucks|usd)\b", re.I),   # "30 dollars"
]

# A size is only read after "size" or "sz", so "medium wash jeans" stays a
# description instead of turning into size M.
_SIZE_PATTERN = re.compile(
    r"\b(?:in\s+)?(?:size|sz)\b\.?\s*[:=]?\s*"
    r"(us\s*\d+(?:\.\d)?|\d+(?:\.\d)?|w\d+(?:\s*l\d+)?|one[\s-]?size|"
    r"(?:extra|x)[\s-]?(?:small|large)|small|medium|med|large|"
    r"[sml]/(?:[sml]|xl)|x{0,2}[sl]|m)\b",
    re.I,
)

_LEADING_FILLER = re.compile(
    r"^(?:i'?m\s+|i\s+am\s+|i\s+)?"
    r"(?:looking\s+for|searching\s+for|want|need|find(?:\s+me)?|show(?:\s+me)?)\s+",
    re.I,
)


def parse_query(query: str) -> dict:
    """
    Pull a description, a size and a max_price out of what the user typed.

    Regex rather than the model: the same query always parses the same way
    and costs no model call. Price and size phrases are cut out so they don't
    end up as search keywords ("30", "size").
    """
    text = query or ""

    max_price = None
    for pattern in _PRICE_PATTERNS:
        match = pattern.search(text)
        if match:
            max_price = float(match.group(1))
            text = text[: match.start()] + " " + text[match.end():]
            break

    size = None
    match = _SIZE_PATTERN.search(text)
    if match:
        size = re.sub(r"\s+", " ", match.group(1)).upper()
        text = text[: match.start()] + " " + text[match.end():]

    text = _LEADING_FILLER.sub("", text.strip())
    words = [w for w in re.sub(r"[,;:!?()]+", " ", text).split()
             if w.lower() not in {"something", "anything", "please"}]
    while words and words[0].lower() in {"a", "an", "some", "the"}:
        words.pop(0)

    return {
        "description": " ".join(words).strip(" .-"),
        "size": size,
        "max_price": max_price,
    }


def _and_list(items: list[str]) -> str:
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def _no_results_message(parsed: dict) -> str:
    """
    Say what to change when the search comes back empty, worked out from the
    data: which part of the query emptied it. Plain code, so the same query
    always gets the same message.

    Price advice names the closest match (best keyword score), not the
    cheapest loose one: for "track jacket" the cheapest keyword match was a
    shacket.
    """
    description, size, max_price = parsed["description"], parsed["size"], parsed["max_price"]

    if not description:
        return ("I couldn't tell what kind of item you want. Add one, like "
                "'graphic tee', 'denim jacket' or 'platform sneakers'.")

    by_words = search_listings(description)
    if not by_words:
        message = (f"Nothing in the listings matches '{description}' at any size or "
                   "price. Try a broader word for the item, like 'dress', 'jacket' "
                   "or 'tee'.")
        # Say now if the size or the price would be the next wall too.
        listings = load_listings()
        cheapest = min(x["price"] for x in listings)
        also = []
        if max_price is not None and max_price < cheapest:
            also.append(f"nothing is listed under {_price(max_price)} "
                        f"(the cheapest listing is {_price(cheapest)})")
        if size and not any(_size_tokens(size) & _size_tokens(x["size"]) for x in listings):
            also.append(f"no listing comes in size {size}")
        if also:
            message += " Also, " + ", and ".join(also) + "."
        return message

    asked = f"'{description}'"
    if size:
        asked += f" in size {size}"
    if max_price is not None:
        asked += f" under {_price(max_price)}"

    in_size = search_listings(description, size) if size else by_words
    advice = []
    if not in_size:
        sizes = sorted({x["size"] for x in by_words})[:6]
        verb = "is" if len(sizes) == 1 else "are"
        advice.append(f"Only {_and_list(sizes)} {verb} listed for it: try one of "
                      "those, or remove the size from your search to see them all.")
    if max_price is not None and not search_listings(description, None, max_price):
        closest = (in_size or by_words)[0]
        advice.append(f"The closest match, {closest['title']}, is {_price(closest['price'])}: "
                      f"raise your max price to at least {_price(closest['price'])}, or "
                      "remove the price limit to see everything that matches.")
    if not advice:  # size alone and price alone each find something, just not together
        closest = in_size[0]
        advice.append(f"The closest match in size {size}, {closest['title']}, is "
                      f"{_price(closest['price'])}: raise your max price to at least "
                      f"{_price(closest['price'])}, or remove the size from your search.")

    return f"No listings matched {asked}. " + " ".join(advice)

# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.

    Args:
        query:    what the user asked for, in plain language
                  (e.g. "vintage graphic tee under $30, size M").
        wardrobe: a wardrobe dict — get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py.

    Returns:
        The session dict. **Check session["error"] first** — if it isn't None,
        the run ended early and the later fields will still be None.

    ─────────────────────────────────────────────────────────────────────────
    The branch rule (README, Planning Loop):

      If search_listings returns an empty list, put a message in
      session["error"] naming what to change and stop: suggest_outfit is
      never called. Otherwise take the first result as
      session["selected_item"] and go to suggest_outfit, then create_fit_card.

    Each pass of the loop runs one step, reads its inputs back out of the
    session, writes its result into the session, and picks the next step.
    trace.check_iterations() guards every pass.

    ─────────────────────────────────────────────────────────────────────────
    IN UNIT 4 you come back and add two things:

      • Trace calls. One per step. `trace.step("search_listings", inputs=...,
        returned=...)` — see trace.py. Your README needs the output.

      • A handler for ModelUnavailable, so a bad key produces a message rather
        than a stack trace. The import is already at the top of this file.
    """
    session = new_session(query, wardrobe)
    session["parsed"] = parse_query(query)

    step, count = "search", 0
    while step != "done":
        count += 1
        trace.check_iterations(count)

        if step == "search":
            parsed = session["parsed"]
            session["steps"].append("search_listings")
            session["search_results"] = search_listings(
                parsed["description"], parsed["size"], parsed["max_price"]
            )
            if not session["search_results"]:  # the branch: stop, say what to change
                session["error"] = _no_results_message(parsed)
                step = "done"
            else:
                session["selected_item"] = session["search_results"][0]
                step = "suggest"

        elif step == "suggest":
            session["steps"].append("suggest_outfit")
            session["outfit_suggestion"] = suggest_outfit(
                session["selected_item"], session["wardrobe"]
            )
            step = "card"

        elif step == "card":
            session["steps"].append("create_fit_card")
            session["fit_card"] = create_fit_card(
                session["outfit_suggestion"], session["selected_item"]
            )
            step = "done"

    return session


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )
