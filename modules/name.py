from typing import Callable, Optional
from core.runner import run_tool

TOOLS = {
    "theHarvester": lambda q: ["-d", q.replace(" ", "+"), "-b", "all", "-l", "100"],
}

def lookup(query: str, on_line: Optional[Callable[[str], None]]) -> list[dict]:
    results = []
    for tool, args_fn in TOOLS.items():
        results.append(run_tool(tool, args_fn(query), query, on_line))
    return results
