from typing import Callable, Optional
from core.runner import run_tool

TOOLS = {
    "sherlock": lambda q: [q],
    "maigret": lambda q: [q, "--no-color"],
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
