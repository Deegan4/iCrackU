# Target Profile / Multi-Lookup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a target profile mode that auto-classifies an input, runs all relevant lookup modules, and saves a combined profile JSON. Available as `--target` CLI flag and as an interactive profile builder in the menu.

**Architecture:** A new `core/profiler.py` handles input classification and multi-module dispatch. `icrack.py` gets a `--target` flag and a `P` menu option. Profile results are saved as a single `profile_<timestamp>_<slug>.json` alongside the standard per-lookup files.

**Tech Stack:** Python 3.12+, Rich, all existing modules from Sub-project 1

**Prerequisite:** Sub-project 1 (new-lookup-modules plan) must be fully implemented first. This plan assumes `modules/ip.py`, `modules/domain.py`, `modules/breach.py`, and `modules/hash.py` exist.

---

## File Map

| File | Action |
|---|---|
| `core/profiler.py` | Create — classification + multi-dispatch |
| `tests/test_profiler.py` | Create |
| `icrack.py` | Modify — `--target` flag, `P` menu option, profile summary output |

---

## Task 1: `core/profiler.py` — classification

**Files:**
- Create: `core/profiler.py`
- Create: `tests/test_profiler.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_profiler.py
import pytest
from core.profiler import classify


def test_classify_email():
    assert classify("foo@bar.com") == ["email", "breach"]


def test_classify_ip():
    assert classify("8.8.8.8") == ["ip"]


def test_classify_domain():
    assert classify("example.com") == ["domain"]


def test_classify_phone():
    assert classify("+15551234567") == ["phone"]


def test_classify_username():
    assert classify("johndoe") == ["username", "name"]


def test_classify_ip_edge_cases():
    assert classify("192.168.1.1") == ["ip"]
    assert classify("256.256.256.256") == ["username", "name"]  # invalid IP → username


def test_classify_domain_with_subdomain():
    assert classify("sub.example.com") == ["domain"]


def test_classify_email_also_runs_breach():
    result = classify("admin@example.com")
    assert "email" in result
    assert "breach" in result
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /home/deegan/iCrackU && source venv/bin/activate && python -m pytest tests/test_profiler.py -v
```

Expected: `ModuleNotFoundError: No module named 'core.profiler'`

- [ ] **Step 3: Implement classification in `core/profiler.py`**

```python
import re
import socket


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
```

- [ ] **Step 4: Run tests**

```bash
cd /home/deegan/iCrackU && source venv/bin/activate && python -m pytest tests/test_profiler.py -v
```

Expected: 8 passed

- [ ] **Step 5: Commit**

```bash
git -C /home/deegan/iCrackU add core/profiler.py tests/test_profiler.py
git -C /home/deegan/iCrackU commit -m "feat: add core/profiler.py with input classification"
```

---

## Task 2: `core/profiler.py` — multi-dispatch and profile saving

**Files:**
- Modify: `core/profiler.py`
- Modify: `tests/test_profiler.py`

- [ ] **Step 1: Add failing tests**

Append to `tests/test_profiler.py`:

```python
from unittest.mock import patch, MagicMock
import json
import os


FAKE_RESULT = {"tool": "faketool", "query": "test", "returncode": 0, "output": "found"}


def fake_lookup(query, on_line=None, on_tool_start=None):
    return [{"tool": "faketool", "query": query, "returncode": 0, "output": "found"}]


def test_run_profile_returns_combined_results():
    with patch("core.profiler.MODULE_MAP", {
        "email":   MagicMock(lookup=fake_lookup),
        "breach":  MagicMock(lookup=fake_lookup),
    }):
        from core.profiler import run_profile
        results = run_profile(
            {"email": "foo@bar.com", "breach": "foo@bar.com"},
            on_line=None,
            on_tool_start=None,
        )
    assert isinstance(results, list)
    assert len(results) == 2
    assert all("lookup_type" in r for r in results)
    assert all("identifier" in r for r in results)
    assert all("tools" in r for r in results)


def test_save_profile_writes_json(tmp_path):
    from core.profiler import save_profile
    targets = [
        {"identifier": "foo@bar.com", "lookup_type": "email",
         "tools": [{"name": "holehe", "returncode": 0, "output": "found"}]},
    ]
    json_path = save_profile(targets, results_dir=str(tmp_path))
    assert os.path.exists(json_path)
    data = json.loads(open(json_path).read())
    assert data["type"] == "profile"
    assert len(data["targets"]) == 1
    assert data["targets"][0]["lookup_type"] == "email"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /home/deegan/iCrackU && source venv/bin/activate && python -m pytest tests/test_profiler.py::test_run_profile_returns_combined_results tests/test_profiler.py::test_save_profile_writes_json -v
```

Expected: FAIL — `run_profile` and `save_profile` not defined

- [ ] **Step 3: Extend `core/profiler.py` with dispatch and save**

Replace the full file:

```python
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
    "email":    mod_email,
    "username": mod_username,
    "phone":    mod_phone,
    "name":     mod_name,
    "address":  mod_address,
    "ip":       mod_ip,
    "domain":   mod_domain,
    "breach":   mod_breach,
    "hash":     mod_hash,
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
    """
    targets: dict mapping lookup_type -> identifier
    e.g. {"email": "foo@bar.com", "breach": "foo@bar.com", "username": "johndoe"}
    Returns list of {identifier, lookup_type, tools} dicts.
    """
    results = []
    for lookup_type, identifier in targets.items():
        module = MODULE_MAP[lookup_type]
        tool_results = module.lookup(identifier, on_line=on_line, on_tool_start=on_tool_start)
        results.append({
            "identifier": identifier,
            "lookup_type": lookup_type,
            "tools": [
                {"name": r["tool"], "returncode": r["returncode"], "output": r["output"]}
                for r in tool_results
            ],
        })
    return results


def save_profile(targets: list[dict], results_dir: str = "results") -> str:
    os.makedirs(results_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    slug = re.sub(r"[^a-zA-Z0-9]", "_", targets[0]["identifier"])[:30] if targets else "profile"
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
    inputs: dict of field -> value (e.g. {"email": "foo@bar.com", "username": "johndoe"})
    Returns flat lookup_type -> identifier dict for run_profile().
    Email inputs automatically add a breach lookup.
    """
    targets = {}
    for field, value in inputs.items():
        if not value:
            continue
        targets[field] = value
        if field == "email" and "breach" not in targets:
            targets["breach"] = value
    return targets
```

- [ ] **Step 4: Run all profiler tests**

```bash
cd /home/deegan/iCrackU && source venv/bin/activate && python -m pytest tests/test_profiler.py -v
```

Expected: 10 passed

- [ ] **Step 5: Run full suite**

```bash
python -m pytest tests/ -v
```

Expected: all previous + 2 new = 19 passed

- [ ] **Step 6: Commit**

```bash
git -C /home/deegan/iCrackU add core/profiler.py tests/test_profiler.py
git -C /home/deegan/iCrackU commit -m "feat: add run_profile and save_profile to core/profiler.py"
```

---

## Task 3: Wire `--target` and `P` menu into `icrack.py`

**Files:**
- Modify: `icrack.py`

- [ ] **Step 1: Add `print_profile_summary` to `core/output.py`**

Append to `core/output.py`:

```python
def print_profile_summary(inputs: dict, profile_results: list[dict], json_path: str):
    console.print()
    console.rule("[bright_green]profile summary[/bright_green]", style="green")
    console.print()

    for field, value in inputs.items():
        if value:
            console.print(f"  [dim]{field:<10}[/dim]  {value}")

    console.print()

    table = _make_table("Tool", "Type", "Status", "Lines")
    for target in profile_results:
        for tool in target["tools"]:
            if tool["returncode"] == -1:
                status = "[dim]–[/dim]"
            elif tool["returncode"] == -2:
                status = "[yellow]⏱[/yellow]"
            elif tool["returncode"] == 0:
                status = "[green]✓[/green]"
            else:
                status = f"[dim]exit {tool['returncode']}[/dim]"
            lines = str(len(tool["output"].splitlines()))
            table.add_row(tool["name"], target["lookup_type"], status, lines)

    console.print(table)
    console.print()
    console.print(f"  [dim]saved[/dim]  {json_path}")
    console.print()
```

- [ ] **Step 2: Add `run_target_profile` function to `icrack.py`**

Add this function after `run_lookup`:

```python
def run_target_profile(inputs: dict[str, str]):
    from core.profiler import build_targets_from_input, run_profile, save_profile
    from core.output import print_profile_summary

    print_header()
    console.print(f"  [dim]target profile[/dim]  [bold]{' · '.join(v for v in inputs.values() if v)}[/bold]\n")

    targets = build_targets_from_input(inputs)
    profile_results = run_profile(
        targets,
        on_line=print_line,
        on_tool_start=print_tool_header,
    )

    os.makedirs(RESULTS_DIR, exist_ok=True)
    json_path = save_profile(profile_results, results_dir=RESULTS_DIR)
    print_profile_summary(inputs, profile_results, json_path)
```

- [ ] **Step 3: Add `--target` flag to `main()` in `icrack.py`**

After `parser.add_argument("--hash", ...)` add:

```python
    parser.add_argument("--target", metavar="TARGET", help="Auto-detect and run all relevant lookups")
```

After `elif args.hash:` add:

```python
    elif args.target:
        from core.profiler import classify
        lookup_types = classify(args.target)
        inputs = {lt: args.target for lt in lookup_types}
        run_target_profile(inputs)
```

- [ ] **Step 4: Add `P` menu option to `interactive_menu()` in `icrack.py`**

Replace the `options` list inside `interactive_menu()`:

```python
    options = [
        ("1",  "Email lookup",          "email"),
        ("2",  "Username lookup",       "username"),
        ("3",  "Phone lookup",          "phone"),
        ("4",  "Name lookup",           "name"),
        ("5",  "Address lookup",        "address"),
        ("6",  "IP lookup",             "ip"),
        ("7",  "Domain lookup",         "domain"),
        ("8",  "Breach check",          "breach"),
        ("9",  "Hash lookup",           "hash"),
        ("P",  "Target profile",        None),
        ("10", "Check installed tools", None),
        ("11", "List saved results",    None),
        ("0",  "Exit",                  None),
    ]
```

Add handling for `P` in the `while True` loop (after `elif choice == "11":`):

```python
        elif choice in ("p", "P"):
            inputs = {}
            fields = ["name", "email", "username", "phone", "ip", "domain"]
            for field in fields:
                val = console.input(f"  [dim]{field:<10}[/dim]  > ").strip()
                if val:
                    inputs[field] = val
            if not inputs:
                console.print("[dim]  no input provided[/dim]")
            else:
                run_target_profile(inputs)
```

- [ ] **Step 5: Run full test suite**

```bash
cd /home/deegan/iCrackU && source venv/bin/activate && python -m pytest tests/ -v
```

Expected: 19 passed

- [ ] **Step 6: Smoke test `--target`**

```bash
python icrack.py --target "example.com" 2>&1 | head -20
```

Expected: header prints, domain module begins running (or skips if whois not installed), no crash.

- [ ] **Step 7: Commit**

```bash
git -C /home/deegan/iCrackU add icrack.py core/output.py
git -C /home/deegan/iCrackU commit -m "feat: add --target flag and P profile menu to icrack.py"
```
