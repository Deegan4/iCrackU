from typing import Callable, Optional

import requests

from core.config import require_key
from core.runner import run_tool


def lookup(
    query: str,
    on_line: Optional[Callable[[str], None]] = None,
    on_tool_start: Optional[Callable[[str], None]] = None,
) -> list[dict]:
    results = []

    # hashid CLI — identify hash type
    if on_tool_start:
        on_tool_start("hashid")
    results.append(run_tool("hashid", [query], query, on_line))

    # VirusTotal — optional API key
    if on_tool_start:
        on_tool_start("virustotal")
    key = require_key(
        "virustotal",
        "VirusTotal API key (free at virustotal.com — Enter to skip): ",
    )
    if not key:
        results.append(
            {
                "tool": "virustotal",
                "query": query,
                "returncode": -1,
                "output": "virustotal — API key not configured",
            }
        )
        return results
    try:
        resp = requests.get(
            f"https://www.virustotal.com/api/v3/files/{query}",
            headers={"x-apikey": key},
            timeout=10,
        )
        if resp.status_code == 404:
            output = f"{query} — not found in VirusTotal"
            rc = 0
        elif resp.status_code == 401:
            output = "virustotal — invalid API key"
            rc = 1
        else:
            attrs = resp.json()["data"]["attributes"]
            stats = attrs.get("last_analysis_stats", {})
            lines = [
                f"Name:      {attrs.get('meaningful_name', 'n/a')}",
                f"Malicious: {stats.get('malicious', 0)}",
                f"Harmless:  {stats.get('harmless', 0)}",
                f"Type:      {attrs.get('type_description', 'n/a')}",
            ]
            output = "\n".join(lines)
            rc = 0
        if on_line and rc == 0:
            for line in output.splitlines():
                on_line(line)
    except Exception as e:
        output = f"virustotal error: {e}"
        rc = 1

    results.append(
        {"tool": "virustotal", "query": query, "returncode": rc, "output": output}
    )
    return results
