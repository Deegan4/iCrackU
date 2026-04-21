from typing import Callable, Optional
from core.runner import run_tool

TOOLS = {
    "phoneinfoga": lambda q: ["scan", "-n", q],
}

def lookup(query: str, on_line: Optional[Callable[[str], None]]) -> list[dict]:
    results = []
    for tool, args_fn in TOOLS.items():
        results.append(run_tool(tool, args_fn(query), query, on_line))
    return results
