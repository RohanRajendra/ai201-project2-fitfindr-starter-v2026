"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are built, and each was tested on its own from a terminal before
the loop existed.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import config
from generate import generate
from utils.data_loader import load_listings
import re


# ── Tool 1: search_listings ───────────────────────────────────────────────────

_STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can", "could", "did", "do", "does", "doing", "down", "during", "each", "few", "for", "from", "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself", "him", "himself", "his", "how",
    "i", "if", "in", "into", "is", "it", "its", "itself", "just", "me", "more", "most", "my", "myself", "no", "nor", "not", "now", "of", "off", "on", "once", "only", "or", "other", "our", "ours", "ourselves", "out", "over", "own", "same", "she", "should", "so", "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves", "then", "there", "these", "they",
    "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "we", "were", "what", "when", "where", "which", "while", "who", "whom", "why", "will", "with", "would", "you", "your", "yours", "yourself", "yourselves",
}

_SIZE_ALIASES = {
    "EXTRA SMALL": "XS", "X-SMALL": "XS",
    "SMALL": "S", "MEDIUM": "M", "MED": "M", "LARGE": "L",
    "EXTRA LARGE": "XL", "X-LARGE": "XL",
    "OS": "ONE SIZE", "OSFA": "ONE SIZE", "ONESIZE": "ONE SIZE", "ONE-SIZE": "ONE SIZE",
}

def _keywords(text: str) -> set[str]:
    """Lowercase words worth matching on, stopwords removed."""
    words = re.findall(r"[a-z0-9']+", (text or "").lower())
    return {w for w in words if w not in _STOPWORDS and len(w) > 1}

def _size_tokens(size: str) -> set[str]:
    cleaned = re.sub(r"\([^)]*\)", " ", size or "").upper()  # drop parentheticals
    cleaned = re.sub(r"\bO/S\b", "OS", cleaned)  # stop O/S splitting into O and S
    tokens = set()
    for p in re.split(r"[/,|]", cleaned):
        p = re.sub(r"\s+", " ", p).strip()
        p = re.sub(r"^SIZE\s+", "", p)
        p = re.sub(r"^US\s*(?=\d)", "", p)  # "US 8" -> "8", so "size 8" finds shoes
        p = re.sub(r"^(?:EXTRA|X)[\s-]?(SMALL|LARGE)$", lambda m: "X" + m.group(1)[0], p)  # "xlarge" -> XL
        waist_length = re.fullmatch(r"(W\d+)\s*(L\d+)", p)  # "W30 L30" -> W30, L30
        if waist_length:
            tokens.update(waist_length.groups())
        elif p:
            tokens.add(_SIZE_ALIASES.get(p, p))
    return tokens

def _size_matches(wanted: str, listing_size: str) -> bool:
    if not wanted:
        return True
    listing_tokens = _size_tokens(listing_size)
    if any(token.startswith("ONE SIZE") for token in listing_tokens):
        return True
    return bool(_size_tokens(wanted) & listing_tokens)

def _stem(word: str) -> str:
    """Fold plurals and apostrophes, so "tees" meets "tee" and "levi's" meets "levis"."""
    word = word.replace("'", "")
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        word = word[:-1]
    return word

def _stems(text: str) -> set[str]:
    return {_stem(w) for w in _keywords(text)}

def _score(wanted: set[str], listing: dict) -> int:
    """One point per wanted word found anywhere in the listing; title hits count twice."""
    title = _stems(listing["title"])
    everything = title | _stems(" ".join([
        listing["description"],
        listing["category"],
        " ".join(listing["style_tags"]),
        " ".join(listing["colors"]),
        listing["brand"] or "",  # brand is None for most listings
    ]))
    return len(wanted & everything) + len(wanted & title)

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Sizes match as whole tokens, ignoring case: "M" matches
                     "S/M", "8" matches "US 8", "W30" matches "W30 L30", and
                     "L" never matches "XL". A "One Size" listing matches any
                     size.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    Scoring: one point per description keyword found in the title,
    description, category, style tags, colors or brand, with title hits
    counted twice. Stopwords are dropped and plurals folded ("tees" -> "tee").
    Ties go to the cheaper listing.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    wanted = _stems(description)
    if not wanted:
        return []

    scored = []
    for listing in load_listings():
        if max_price is not None and listing["price"] > max_price:
            continue
        if not _size_matches(size, listing["size"]):
            continue
        score = _score(wanted, listing)
        if score > 0:
            scored.append((score, listing))

    scored.sort(key=lambda pair: (-pair[0], pair[1]["price"]))
    return [listing for _, listing in scored[: config.SEARCH_RESULT_LIMIT]]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

_STYLIST = (
    "You are a practical thrift stylist. You build outfits around one "
    "secondhand piece. Be specific and brief. Plain text, no markdown."
)

def _describe(item: dict) -> str:
    """One line about a listing for a prompt. Brand is left out when there isn't one."""
    parts = [
        item.get("title", "an item"),
        f"brand: {item['brand']}" if item.get("brand") else "",
        f"category: {item.get('category', '')}",
        f"colors: {', '.join(item.get('colors', []))}",
        f"style: {', '.join(item.get('style_tags', []))}",
        f"size: {item.get('size', '')}",
        f"condition: {item.get('condition', '')}",
    ]
    return "; ".join(p for p in parts if p)

def _wardrobe_lines(items: list[dict]) -> str:
    lines = []
    for piece in items:
        line = (
            f"- {piece['name']} ({piece.get('category', '')}; "
            f"colors: {', '.join(piece.get('colors', []))}; "
            f"style: {', '.join(piece.get('style_tags', []))})"
        )
        if piece.get("notes"):  # notes is None for half the example wardrobe
            line += f" — {piece['notes']}"
        lines.append(line)
    return "\n".join(lines)

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.

    With wardrobe items, the prompt lists each piece and asks for outfits that
    name pieces exactly as written. With none, it asks for general advice that
    doesn't claim the user owns anything. None of the empty cases raise:
        empty new_item -> "No item to style — search for something first."
                          (no model call)
        empty wardrobe -> general styling advice
        empty reply    -> a one-line message saying so

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    if not new_item:
        return "No item to style — search for something first."

    items = (wardrobe or {}).get("items") or []
    if items:
        prompt = (
            f"New thrift find: {_describe(new_item)}\n\n"
            f"Pieces I already own:\n{_wardrobe_lines(items)}\n\n"
            "Suggest 1-2 outfits built around the new find, using only pieces "
            "from my list. Name each piece exactly as it's written in the list. "
            "Two or three sentences per outfit."
        )
    else:
        prompt = (
            f"New thrift find: {_describe(new_item)}\n\n"
            "I haven't saved any wardrobe pieces yet. Give general styling "
            "advice: 1-2 outfit ideas naming the kinds of pieces this goes with "
            "(e.g. 'straight-leg dark jeans'), plus one tip. Don't say I own "
            "anything. Under 120 words."
        )

    outfit = generate(prompt, system=_STYLIST)
    if not outfit:
        return f"The model returned no outfit suggestion for {new_item.get('title', 'this item')}. Try again."
    return outfit


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

_CAPTION_WRITER = (
    "You write short, casual captions for thrift finds, the way someone posts "
    "their own outfit. Specific about the vibe, never salesy. Plain text, no "
    "markdown."
)

def _price(amount: float) -> str:
    """How a person writes a price: $24 for 24.0, $18.50 for 18.5."""
    return f"${amount:.0f}" if float(amount).is_integer() else f"${amount:.2f}"

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A caption: two to four casual sentences, then 1-3 hashtags on the
        last line. None of the empty cases raise or call the model:
            blank outfit   -> "Can't write a fit card without an outfit suggestion."
            empty new_item -> "Can't write a fit card without an item."
        An empty reply from the model comes back as a one-line message.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    if not outfit or not outfit.strip():
        return "Can't write a fit card without an outfit suggestion."
    if not new_item:
        return "Can't write a fit card without an item."

    price = _price(new_item["price"])
    platform = new_item["platform"]
    # Say who bought it: with a bare "Platform: depop" line the model sometimes
    # wrote the caption as the seller ("grab these on my depop"). And keep the
    # facts out of the first sentence, or every card opens "scored these on
    # depop for $38".
    prompt = (
        f"My thrift find: {_describe(new_item)}\n"
        f"I just bought this on {platform} for {price}.\n\n"
        f"How I'm styling it:\n{outfit.strip()}\n\n"
        "Write a caption for my post about this find. I'm the buyer showing it "
        "off, not the seller. 2-4 casual sentences in first person, then 1-3 "
        "hashtags on their own final line. Open with the vibe or the outfit, "
        f"not the price or where I got it. Mention the item, the price ({price}) "
        f"and the platform ({platform}) exactly once each, and don't use the "
        "platform as a hashtag. Name a specific vibe instead of generic words "
        "like 'stylish'. Emoji are fine. Don't wrap the caption in quotes."
    )

    card = generate(prompt, system=_CAPTION_WRITER)
    if not card:
        return f"The model returned no caption for {new_item.get('title', 'this item')}. Try again."
    return card
