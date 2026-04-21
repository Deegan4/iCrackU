from typing import Callable, Optional
from core.runner import run_tool

TOOLS = {
    "sherlock": lambda q: [q],
    "maigret": lambda q: [q, "--no-color"],
    "social-analyzer": lambda q: ["--username", q, "--metadata"],
}

def lookup(query: str, on_line: Optional[Callable[[str], None]]) -> list[dict]:
    results = []
    for tool, args_fn in TOOLS.items():
        results.append(run_tool(tool, args_fn(query), query, on_line))
    return results
