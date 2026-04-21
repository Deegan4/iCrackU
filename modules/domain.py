from typing import Callable, Optional

import dns.resolver
import whois

from core.runner import run_tool


def lookup(
    query: str,
    on_line: Optional[Callable[[str], None]] = None,
    on_tool_start: Optional[Callable[[str], None]] = None,
) -> list[dict]:
    results = []

    # python-whois — registration data
    if on_tool_start:
        on_tool_start("whois-py")
    try:
        w = whois.whois(query)
        lines = [
            f"Registrar:    {w.registrar or 'n/a'}",
            f"Created:      {w.creation_date or 'n/a'}",
            f"Expires:      {w.expiration_date or 'n/a'}",
            f"Name servers: {', '.join(w.name_servers or [])}",
        ]
        output = "\n".join(lines)
        rc = 0
        if on_line:
            for line in output.splitlines():
                on_line(line)
    except Exception as e:
        output = f"whois error: {e}"
        rc = 1
    results.append({"tool": "whois-py", "query": query, "returncode": rc, "output": output})

    # dnspython — DNS records
    if on_tool_start:
        on_tool_start("dns-records")
    dns_lines = []
    for record_type in ("A", "MX", "NS", "TXT"):
        try:
            answers = dns.resolver.resolve(query, record_type)
            for rdata in answers:
                dns_lines.append(f"{record_type}: {rdata}")
        except Exception:
            pass
    output = "\n".join(dns_lines) if dns_lines else "No DNS records found."
    rc = 0 if dns_lines else 1
    if on_line and rc == 0:
        for line in dns_lines:
            on_line(line)
    results.append({"tool": "dns-records", "query": query, "returncode": rc, "output": output})

    # subfinder CLI — optional, no key needed
    if on_tool_start:
        on_tool_start("subfinder")
    results.append(run_tool("subfinder", ["-d", query, "-silent"], query, on_line))

    return results
