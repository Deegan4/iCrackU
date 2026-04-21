from typing import Callable, Optional
from core.runner import run_tool

TOOLS = {
    "holehe": lambda q: ["--only-used", q],
    "theHarvester": lambda q: ["-d", q, "-b", "all", "-l", "100"],
    "ghunt": lambda q: ["email", q],
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
