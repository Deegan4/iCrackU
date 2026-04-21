from typing import Callable, Optional

import requests

from core.config import require_key


def lookup(
    query: str,
    on_line: Optional[Callable[[str], None]] = None,
    on_tool_start: Optional[Callable[[str], None]] = None,
) -> list[dict]:
    if on_tool_start:
        on_tool_start("hibp")

    key = require_key(
        "hibp",
        "HaveIBeenPwned API key (free at haveibeenpwned.com/API/Key — Enter to skip): ",
    )
    if not key:
        return [
            {
                "tool": "hibp",
                "query": query,
                "returncode": -1,
                "output": "hibp — API key not configured",
            }
        ]

    try:
        resp = requests.get(
            f"https://haveibeenpwned.com/api/v3/breachedaccount/{query}",
            headers={"hibp-api-key": key, "user-agent": "iCrackU-osint"},
            timeout=10,
        )
        if resp.status_code == 404:
            output = f"{query} — not found in any known breach"
            rc = 0
        elif resp.status_code == 401:
            output = "hibp — invalid API key"
            rc = 1
        else:
            breaches = resp.json()
            lines = [f"Found in {len(breaches)} breach(es):"]
            for b in breaches:
                lines.append(
                    f"  {b['Name']}  ({b['PwnCount']:,} accounts)"
                    + ("  [verified]" if b.get("IsVerified") else "")
                )
            output = "\n".join(lines)
            rc = 0
        if on_line and rc == 0:
            for line in output.splitlines():
                on_line(line)
    except Exception as e:
        output = f"hibp error: {e}"
        rc = 1

    return [{"tool": "hibp", "query": query, "returncode": rc, "output": output}]
