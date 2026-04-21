import json
import os
import re
from datetime import datetime

def save_results(
    lookup_type: str,
    query: str,
    tool_results: list[dict],
    results_dir: str = "results",
) -> tuple[str, str]:
    os.makedirs(results_dir, exist_ok=True)

    safe_query = re.sub(r"[^a-zA-Z0-9@._+-]", "_", query)[:50]
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    base = f"{timestamp}_{lookup_type}_{safe_query}"

    txt_path = os.path.join(results_dir, f"{base}.txt")
    json_path = os.path.join(results_dir, f"{base}.json")

    with open(txt_path, "w") as f:
        f.write(f"iCrackU — {lookup_type.upper()} lookup: {query}\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write("=" * 60 + "\n\n")
        for r in tool_results:
            f.write(f"[{r['tool']}]\n{r['output']}\n\n")

    data = {
        "timestamp": timestamp,
        "type": lookup_type,
        "query": query,
        "tools": [
            {"name": r["tool"], "returncode": r["returncode"], "output": r["output"]}
            for r in tool_results
        ],
    }
    with open(json_path, "w") as f:
        json.dump(data, f, indent=2)

    return txt_path, json_path
