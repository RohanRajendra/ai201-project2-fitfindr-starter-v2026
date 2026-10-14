"""
FitFindr's MCP server.

MCP is an agreed shape for describing a tool, so anything that speaks the
protocol can call it: this agent today, a different agent tomorrow. This
server offers one tool, search_listings. agent.py::run_agent calls it through
mcp_client.call_tool; suggest_outfit and create_fit_card are still called
directly.

    python mcp_server.py        starts the server (it will just sit there — that's right)
    python mcp_client.py        asks the server what it offers

The description below is written for an agent that will never see this code:
units and types are named, and so is what comes back when nothing matches.
"""

from mcp.server.fastmcp import FastMCP

# The real tool comes in under an alias: the function registered below takes
# the name "search_listings", and without the alias it would call itself.
from tools import search_listings as _search_listings_impl

# log_level="WARNING" keeps the server from printing an INFO line for every
# request. Without it your terminal fills with "Processing request of type
# CallToolRequest" and the output you actually care about scrolls away.
mcp = FastMCP("fitfindr", log_level="WARNING")


@mcp.tool()
def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search 40 secondhand clothing listings (from Depop, thredUp and Poshmark)
    for the ones that best match a description, optionally filtered by size
    and price. Returns an empty list, never an error, when nothing matches.

    Inputs:
      description (string, required): the item words, e.g. "vintage graphic
        tee". Only listings that contain every one of these words come back
        (plurals fold, so "tees" finds "tee"; words like "a" and "for" are
        ignored). Listings with more of the words in their title rank first;
        ties go to the cheaper one.
      size (string or null): e.g. "M", "8", "W30". Null skips the size filter.
        Sizes match as whole tokens, ignoring case: "M" matches "S/M", "8"
        matches "US 8", "W30" matches "W30 L30", "L" never matches "XL". A
        "One Size" listing matches any size.
      max_price (number or null): the most the user will pay, in US dollars,
        inclusive, so 30 keeps a $30.00 listing. Null skips the price filter.

    Returns: a list of up to 10 listings, best match first. Each is an object
    with id, title, description, category, style_tags (list of strings), size,
    condition, price (US dollars), colors (list of strings), brand (string or
    null) and platform ("depop", "thredUp" or "poshmark"). An empty list means
    nothing matched.
    """
    return _search_listings_impl(description, size, max_price)


# FastMCP builds the input schema from the type hints, which is why they're
# not optional here: `description: str` becomes a required string, and
# `max_price: float | None = None` an optional number. They match the Tool
# Inventory in README.md.


if __name__ == "__main__":
    mcp.run()
