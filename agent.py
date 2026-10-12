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
from mcp_client import MCPError, call_tool
from tools import suggest_outfit, create_fit_card
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
    }


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
    The loop parses the query, searches, and branches on the search result.
    A match moves through the outfit and fit-card stages using session state;
    an empty result records a useful error and returns immediately.

    ─────────────────────────────────────────────────────────────────────────
    IN UNIT 4 you come back and add two things:

      • Trace calls. One per step. `trace.step("search_listings", inputs=...,
        returned=...)` — see trace.py. Your README needs the output.

      • A handler for ModelUnavailable, so a bad key produces a message rather
        than a stack trace. The import is already at the top of this file.
    """
    session = new_session(query, wardrobe)

    price_match = re.search(
        r"(?:under|below|up to|less than|max(?:imum)?(?: price)?(?: of)?)\s*\$?(\d+(?:\.\d+)?)",
        query,
        re.IGNORECASE,
    )
    size_match = re.search(r"(?:in\s+)?size\s+([A-Za-z0-9./-]+)", query, re.IGNORECASE)

    description = re.sub(
        r"(?:under|below|up to|less than|max(?:imum)?(?: price)?(?: of)?)\s*\$?\d+(?:\.\d+)?",
        "",
        query,
        flags=re.IGNORECASE,
    )
    description = re.sub(
        r"(?:in\s+)?size\s+[A-Za-z0-9./-]+", "", description, flags=re.IGNORECASE
    )
    description = re.sub(
        r"^(?:i(?:'m| am)?\s+)?(?:looking for|searching for|find me|want)\s+",
        "",
        description.strip(),
        flags=re.IGNORECASE,
    ).strip(" ,.-")

    session["parsed"] = {
        "description": description,
        "size": size_match.group(1) if size_match else None,
        "max_price": float(price_match.group(1)) if price_match else None,
    }

    stage = "search"
    iterations = 0
    while stage:
        iterations += 1
        trace.check_iterations(iterations)

        if stage == "search":
            parsed = session["parsed"]
            try:
                session["search_results"] = call_tool(
                    "search_listings",
                    {
                        "description": parsed["description"],
                        "size": parsed["size"],
                        "max_price": parsed["max_price"],
                    },
                )
            except MCPError as exc:
                session["error"] = (
                    f"The listing search service could not be reached: {exc} "
                    "Check the MCP server and try again."
                )
                trace.step(
                    "search_listings (via MCP)",
                    inputs=parsed,
                    returned="error",
                    note="MCP failure, stopping",
                )
                return session
            if not session["search_results"]:
                session["error"] = (
                    "No matching listings were found. Try a larger size range, "
                    "a higher price limit, or fewer description words."
                )
                trace.step(
                    "search_listings (via MCP)",
                    inputs=parsed,
                    returned=session["search_results"],
                    note="branch: empty, stopping",
                )
                return session
            trace.step(
                "search_listings (via MCP)",
                inputs=parsed,
                returned=session["search_results"],
                note="branch: match, continuing",
            )
            session["selected_item"] = session["search_results"][0]
            stage = "outfit"

        elif stage == "outfit":
            try:
                session["outfit_suggestion"] = suggest_outfit(
                    session["selected_item"], session["wardrobe"]
                )
            except ModelUnavailable as exc:
                session["error"] = (
                    f"The outfit model could not be reached: {exc} "
                    "Check the API key or internet connection and try again."
                )
                trace.step(
                    "suggest_outfit",
                    inputs={"item": session["selected_item"], "wardrobe": session["wardrobe"]},
                    returned="error",
                    note="model unavailable, stopping",
                )
                return session
            trace.step(
                "suggest_outfit",
                inputs={"item": session["selected_item"], "wardrobe": session["wardrobe"]},
                returned=session["outfit_suggestion"],
            )
            stage = "fit_card"

        elif stage == "fit_card":
            try:
                session["fit_card"] = create_fit_card(
                    session["outfit_suggestion"], session["selected_item"]
                )
            except ModelUnavailable as exc:
                session["error"] = (
                    f"The fit-card model could not be reached: {exc} "
                    "Check the API key or internet connection and try again."
                )
                trace.step(
                    "create_fit_card",
                    inputs={"outfit": session["outfit_suggestion"], "item": session["selected_item"]},
                    returned="error",
                    note="model unavailable, stopping",
                )
                return session
            trace.step(
                "create_fit_card",
                inputs={"outfit": session["outfit_suggestion"], "item": session["selected_item"]},
                returned=session["fit_card"],
            )
            stage = None

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
