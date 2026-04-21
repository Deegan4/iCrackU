from typing import Callable, Optional
from core.runner import run_tool


# sherlock/maigret accept a username-style token; we use the sanitised name
# (spaces → underscores) as the closest approximation for person-name searches.
# theHarvester is included only when the name looks like a domain/org keyword
# (no spaces), using its -d flag correctly as a domain seed.
def _name_token(q: str) -> str:
    return q.strip().lower().replace(" ", "_")


TOOLS = {
    "sherlock": lambda q: [_name_token(q)],
    "maigret": lambda q: [_name_token(q), "--no-color"],
}


def lookup(
    query: str,
    on_line: Optional[Callable[[str], None]],
    on_tool_start: Optional[Callable[[str], None]] = None,
) -> list[dict]:
    results = []
    for tool, args_fn in TOOLS.items():
        if on_tool_start:
            on_tool_start(tool)
        results.append(run_tool(tool, args_fn(query), query, on_line))
    return results
