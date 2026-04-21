import json
import os
import re
from datetime import datetime
from typing import Callable, Optional

import modules.email as mod_email
import modules.username as mod_username
import modules.phone as mod_phone
import modules.name as mod_name
import modules.address as mod_address
import modules.ip as mod_ip
import modules.domain as mod_domain
import modules.breach as mod_breach
import modules.hash as mod_hash

MODULE_MAP = {
    "email": mod_email,
    "username": mod_username,
    "phone": mod_phone,
    "name": mod_name,
    "address": mod_address,
    "ip": mod_ip,
    "domain": mod_domain,
    "breach": mod_breach,
    "hash": mod_hash,
}


def _is_valid_ip(value: str) -> bool:
    parts = value.split(".")
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(p) <= 255 for p in parts)
    except ValueError:
        return False


def classify(query: str) -> list[str]:
    if "@" in query:
        return ["email", "breach"]
    if _is_valid_ip(query):
        return ["ip"]
    if re.match(r"^\+?\d{7,15}$", query.replace(" ", "").replace("-", "")):
        return ["phone"]
    if re.match(r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", query) and "." in query:
        return ["domain"]
    return ["username", "name"]


def run_profile(
    targets: dict[str, str],
    on_line: Optional[Callable[[str], None]] = None,
    on_tool_start: Optional[Callable[[str], None]] = None,
) -> list[dict]:
    """Run all specified lookups and return combined results list."""
    results = []
    for lookup_type, identifier in targets.items():
        module = MODULE_MAP[lookup_type]
        tool_results = module.lookup(
            identifier, on_line=on_line, on_tool_start=on_tool_start
        )
        results.append(
            {
                "identifier": identifier,
                "lookup_type": lookup_type,
                "tools": [
                    {
                        "name": r["tool"],
                        "returncode": r["returncode"],
                        "output": r["output"],
                    }
                    for r in tool_results
                ],
            }
        )
    return results


def save_profile(targets: list[dict], results_dir: str = "results") -> str:
    """Save combined profile results to a JSON file. Returns the file path."""
    os.makedirs(results_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    slug = (
        re.sub(r"[^a-zA-Z0-9]", "_", targets[0]["identifier"])[:30]
        if targets
        else "profile"
    )
    filename = f"profile_{timestamp}_{slug}.json"
    path = os.path.join(results_dir, filename)
    data = {
        "timestamp": timestamp,
        "type": "profile",
        "targets": targets,
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return path


def build_targets_from_input(inputs: dict[str, str]) -> dict[str, str]:
    """
    Build flat lookup_type -> identifier dict from field inputs.
    Email inputs automatically add a breach lookup.
    """
    targets: dict[str, str] = {}
    for field, value in inputs.items():
        if not value:
            continue
        targets[field] = value
        if field == "email" and "breach" not in targets:
            targets["breach"] = value
    return targets
