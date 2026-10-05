"""
Style memory (stretch): a wardrobe that remembers what earlier runs found.

    python app.py ask '...' --remember    run with the saved wardrobe, then add
                                          the found item to it
    python app.py forget                  clear it

The saved wardrobe starts empty and lives in .fitfindr/wardrobe.json, which
is gitignored. Only app.py's --remember and forget touch it, so plain runs,
run_eval.py and serve.py never see it: a test run can't be shaped by
something an earlier run happened to save.
"""

import json
import os
import tempfile
from pathlib import Path

import config
from tools import _price

WARDROBE_FILE = config.ROOT / ".fitfindr" / "wardrobe.json"


def _well_formed(piece) -> bool:
    return isinstance(piece, dict) and isinstance(piece.get("name"), str) and bool(piece["name"].strip())


def load_wardrobe() -> dict:
    """
    The saved wardrobe, or an empty one ({"items": []}) before anything is saved.

    A file that can't be read, or isn't shaped like a wardrobe, counts as empty,
    and pieces without a name are skipped, so neither `ask --remember` nor
    `forget` can crash on it.
    """
    try:
        saved = json.loads(WARDROBE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):  # missing, unreadable, not UTF-8, not JSON
        return {"items": []}
    items = saved.get("items") if isinstance(saved, dict) else None
    if not isinstance(items, list):
        return {"items": []}
    return {"items": [piece for piece in items if _well_formed(piece)]}


def remember(item: dict) -> bool:
    """Add a found listing to the saved wardrobe. False if it was already there."""
    wardrobe = load_wardrobe()
    piece_id = f"found_{item['id']}"
    if any(piece.get("id") == piece_id for piece in wardrobe["items"]):
        return False

    # Same shape as a wardrobe item in data/wardrobe_schema.json, so
    # suggest_outfit formats it like any other piece.
    wardrobe["items"].append({
        "id": piece_id,
        "name": item["title"],
        "category": item["category"],
        "colors": item["colors"],
        "style_tags": item["style_tags"],
        "notes": f"Found with FitFindr on {item['platform']} for {_price(item['price'])}",
    })
    # Write a temp file and swap it in, so a run that dies mid-write can't
    # leave a half-written file that the next load would read as empty.
    WARDROBE_FILE.parent.mkdir(exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=WARDROBE_FILE.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(wardrobe, f, indent=2, ensure_ascii=False)
        os.replace(tmp, WARDROBE_FILE)
    finally:
        Path(tmp).unlink(missing_ok=True)
    return True


def forget() -> int:
    """Delete the saved wardrobe, whatever state it's in. Returns how many pieces it held."""
    count = len(load_wardrobe()["items"])
    WARDROBE_FILE.unlink(missing_ok=True)
    return count
