"""
The runs my test needs: one scenario per criterion in criteria.md, five tries
each, plus the empty-wardrobe failure mode as a diagnostic.

`run_eval.py` runs everything here five times and writes the run log — five
because the criteria are written out of five.

A scenario gives either one "query", run on every try, or "queries", one per
try: try 1 runs the first, try 2 the second, and so on. Criteria 3, 4 and 5
each call for five different queries, and the others are tested the same
way, so each row of the run log covers five different requests rather than
one request five times. "model": "unreachable" makes run_eval.py change one
character of the key for each try (criterion 5).

Each list was picked by the rule in its comment, and checked against
data/listings.json, before any run.
"""

SCENARIOS = [
    {
        # Criterion 1. The five matching queries app.py ships as examples,
        # one per try: a tee, a jacket, a dress, shoes, a jacket again, each
        # with a price ceiling or a size.
        "name": "A matching query completes all three tools",
        "queries": [
            "vintage graphic tee under $30",
            "90s track jacket in size M",
            "silk slip dress in midi length under $40",
            "platform sneakers size 8",
            "denim jacket under $50",
        ],
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        # Criterion 2. Five things a shopper might ask for that the data
        # doesn't have, one of each kind: an item no listing names, a size
        # nothing comes in, a price under every match, and two real item words
        # in combinations the data lacks. The only leather jacket is the $75
        # bomber, and the only boots are tan Chelsea boots.
        "name": "An impossible query stops before the second tool",
        "queries": [
            "designer ballgown size XXS under $5",
            "platform sneakers size 11",
            "track jacket under $20",
            "leather jacket under $40",
            "red cowboy boots",
        ],
        "wardrobe": "example",
        "criterion": 2,
    },
    {
        # Criterion 3. Five queries that each return results, covering the
        # ways an item reaches suggest_outfit: the second branch swapping the
        # pick ('velvet blazer'), an overpriced pick that's kept, a size, a
        # price, and both. Since unit 4's strict matching, 'velvet blazer'
        # finds only the velvet blazer and no longer swaps; it stays in the
        # list so the before and after runs are the same test.
        "name": "The found item reaches `suggest_outfit`",
        "queries": [
            "velvet blazer",
            "chunky knit cardigan",
            "chelsea boots size 8.5",
            "cargo pants under $30",
            "crochet halter top size S under $25",
        ],
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        # Criterion 4. Five queries for five different items, across all
        # three platforms and $18 to $40, so the five cards have five
        # different prices and platforms to get right.
        "name": "Fit cards name price and platform, and vary",
        "queries": [
            "y2k baby tee",
            "corduroy pants",
            "vintage windbreaker",
            "mini shoulder bag",
            "denim shorts",
        ],
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        # Criterion 5. Five queries that each return results, none used by
        # another scenario, run with the model unreachable.
        "name": "A down model gets a readable message",
        "queries": [
            "denim vest",
            "henley",
            "polo shirt",
            "linen trousers",
            "tie-dye long sleeve",
        ],
        "wardrobe": "example",
        "model": "unreachable",
        "criterion": 5,
    },
    {
        # A user with nothing saved: one of unit 4's three failure modes. Not
        # one of the five criteria, so run_eval.py marks it as diagnostic.
        "name": "empty wardrobe",
        "query": "denim jacket under $50",
        "wardrobe": "empty",
        "criterion": None,
    },
]

WARDROBES = ("example", "empty")
MODEL_STATES = ("reachable", "unreachable")


def validate() -> list[str]:
    """Complain about anything malformed, before a long run rather than during."""
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        queries = scenario.get("queries")
        if queries is not None:
            if not isinstance(queries, list) or not queries:
                problems.append(f"scenario {i}'s queries should be a non-empty list")
            elif not all(isinstance(q, str) and q.strip() for q in queries):
                problems.append(f"scenario {i} has an empty query in its list")
        elif not (isinstance(scenario.get("query"), str) and scenario["query"].strip()):
            problems.append(f"scenario {i} has no query (or it isn't a string)")
        if scenario.get("wardrobe") not in WARDROBES:
            problems.append(
                f"scenario {i} has wardrobe {scenario.get('wardrobe')!r} — "
                f"it should be one of {WARDROBES}"
            )
        if scenario.get("model", "reachable") not in MODEL_STATES:
            problems.append(
                f"scenario {i} has model {scenario.get('model')!r} — "
                f"it should be one of {MODEL_STATES}"
            )
    return problems
