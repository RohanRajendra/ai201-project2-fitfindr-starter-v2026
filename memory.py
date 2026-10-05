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

import config
from tools import _price

WARDROBE_FILE = config.ROOT / ".fitfindr" / "wardrobe.json"


def load_wardrobe() -> dict:
    """The saved wardrobe, or an empty one ({"items": []}) before anything is saved."""
    try:
        saved = json.loads(WARDROBE_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {"items": []}
    return {"items": saved.get("items", [])}


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
    WARDROBE_FILE.parent.mkdir(exist_ok=True)
    WARDROBE_FILE.write_text(json.dumps(wardrobe, indent=2, ensure_ascii=False), encoding="utf-8")
    return True


def forget() -> int:
    """Delete the saved wardrobe. Returns how many pieces it held."""
    count = len(load_wardrobe()["items"])
    WARDROBE_FILE.unlink(missing_ok=True)
    return count
