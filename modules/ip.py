import socket
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

    # ipinfo.io — free, no key
    if on_tool_start:
        on_tool_start("ipinfo")
    try:
        resp = requests.get(f"https://ipinfo.io/{query}/json", timeout=10)
        data = resp.json()
        lines = [f"{k}: {v}" for k, v in data.items() if k not in ("readme", "ip")]
        output = "\n".join(lines)
        rc = 0
        if on_line:
            for line in output.splitlines():
                on_line(line)
    except Exception as e:
        output = f"ipinfo error: {e}"
        rc = 1
    results.append(
        {"tool": "ipinfo", "query": query, "returncode": rc, "output": output}
    )

    # reverse DNS — free
    if on_tool_start:
        on_tool_start("reverse-dns")
    try:
        hostname = socket.gethostbyaddr(query)[0]
        output = f"Hostname: {hostname}"
        rc = 0
        if on_line:
            on_line(output)
    except socket.herror:
        output = "No reverse DNS record."
        rc = 1
    results.append(
        {"tool": "reverse-dns", "query": query, "returncode": rc, "output": output}
    )

    # whois CLI — free
    if on_tool_start:
        on_tool_start("whois")
    results.append(run_tool("whois", [query], query, on_line))

    # Shodan — optional API key
    key = require_key("shodan", "Shodan API key (Enter to skip): ")
    if not key:
        results.append(
            {
                "tool": "shodan",
                "query": query,
                "returncode": -1,
                "output": "shodan — API key not configured",
            }
        )
        return results

    if on_tool_start:
        on_tool_start("shodan")
    try:
        import shodan as shodan_lib

        api = shodan_lib.Shodan(key)
        host = api.host(query)
        lines = [
            f"Organization: {host.get('org', 'n/a')}",
            f"OS:           {host.get('os', 'n/a')}",
            f"Ports:        {', '.join(str(p) for p in host.get('ports', []))}",
            f"Hostnames:    {', '.join(host.get('hostnames', []) or [])}",
        ]
        output = "\n".join(lines)
        rc = 0
        if on_line:
            for line in output.splitlines():
                on_line(line)
    except Exception as e:
        output = f"shodan error: {e}"
        rc = 1
    results.append(
        {"tool": "shodan", "query": query, "returncode": rc, "output": output}
    )

    return results
