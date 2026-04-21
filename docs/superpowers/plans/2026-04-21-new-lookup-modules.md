# New Lookup Modules Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add four new lookup modules (ip, domain, breach, hash), a config system for API key management, and wire everything into the CLI and interactive menu.

**Architecture:** Each module follows the existing pattern (`lookup(query, on_line, on_tool_start) -> list[dict]`). A new `core/config.py` handles API key storage at `~/.icrackU/keys.json` with prompt-once-then-cache behaviour. Free tools run without keys; optional API tools degrade gracefully when keys are absent.

**Tech Stack:** Python 3.12+, Rich, requests, dnspython, python-whois, shodan pip package, hashid CLI, whois CLI, subfinder CLI

---

## File Map

| File | Action |
|---|---|
| `core/config.py` | Create — API key management |
| `modules/ip.py` | Create — IP geolocation, reverse DNS, whois, Shodan |
| `modules/domain.py` | Create — WHOIS, DNS records, subfinder |
| `modules/breach.py` | Create — HaveIBeenPwned v3 |
| `modules/hash.py` | Create — hashid, VirusTotal |
| `tests/test_config.py` | Create |
| `tests/test_modules.py` | Modify — add 4 new tests |
| `icrack.py` | Modify — new flags, menu entries, imports, tool lists |
| `requirements.txt` | Modify — add dnspython, python-whois, requests, shodan |

---

## Task 1: `core/config.py`

**Files:**
- Create: `core/config.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_config.py
import json
import pytest
from unittest.mock import patch
import core.config


def test_get_key_returns_none_when_missing(tmp_path):
    with patch.object(core.config, "KEYS_FILE", str(tmp_path / "keys.json")):
        assert core.config.get_key("shodan") is None


def test_get_key_returns_value_when_present(tmp_path):
    keys_file = tmp_path / "keys.json"
    keys_file.write_text(json.dumps({"shodan": "abc123"}))
    with patch.object(core.config, "KEYS_FILE", str(keys_file)):
        assert core.config.get_key("shodan") == "abc123"


def test_prompt_and_save_key_writes_file(tmp_path):
    keys_file = tmp_path / "keys.json"
    with patch.object(core.config, "KEYS_FILE", str(keys_file)), \
         patch.object(core.config, "CONFIG_DIR", str(tmp_path)), \
         patch.object(core.config, "console") as mock_console:
        mock_console.input.return_value = "mykey"
        result = core.config.prompt_and_save_key("shodan", "Enter key: ")
    assert result == "mykey"
    assert json.loads(keys_file.read_text())["shodan"] == "mykey"


def test_prompt_and_save_key_returns_none_on_empty(tmp_path):
    keys_file = tmp_path / "keys.json"
    with patch.object(core.config, "KEYS_FILE", str(keys_file)), \
         patch.object(core.config, "CONFIG_DIR", str(tmp_path)), \
         patch.object(core.config, "console") as mock_console:
        mock_console.input.return_value = ""
        result = core.config.prompt_and_save_key("shodan", "Enter key: ")
    assert result is None
    assert json.loads(keys_file.read_text()).get("shodan") == "__skip__"


def test_require_key_returns_cached_key(tmp_path):
    keys_file = tmp_path / "keys.json"
    keys_file.write_text(json.dumps({"hibp": "xyz"}))
    with patch.object(core.config, "KEYS_FILE", str(keys_file)), \
         patch.object(core.config, "console") as mock_console:
        result = core.config.require_key("hibp", "Enter key: ")
    assert result == "xyz"
    mock_console.input.assert_not_called()


def test_require_key_prompts_when_missing(tmp_path):
    keys_file = tmp_path / "keys.json"
    with patch.object(core.config, "KEYS_FILE", str(keys_file)), \
         patch.object(core.config, "CONFIG_DIR", str(tmp_path)), \
         patch.object(core.config, "console") as mock_console:
        mock_console.input.return_value = "newkey"
        result = core.config.require_key("hibp", "Enter key: ")
    assert result == "newkey"


def test_require_key_skip_sentinel_prevents_reprompt(tmp_path):
    keys_file = tmp_path / "keys.json"
    keys_file.write_text(json.dumps({"shodan": "__skip__"}))
    with patch.object(core.config, "KEYS_FILE", str(keys_file)), \
         patch.object(core.config, "console") as mock_console:
        result = core.config.require_key("shodan", "Enter key: ")
    assert result is None
    mock_console.input.assert_not_called()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /home/deegan/iCrackU && source venv/bin/activate && python -m pytest tests/test_config.py -v
```

Expected: `ModuleNotFoundError: No module named 'core.config'`

- [ ] **Step 3: Implement `core/config.py`**

```python
import json
import os
import stat

from rich.console import Console

CONFIG_DIR = os.path.expanduser("~/.icrackU")
KEYS_FILE = os.path.join(CONFIG_DIR, "keys.json")
SKIP_SENTINEL = "__skip__"

console = Console()


def _load() -> dict:
    if not os.path.exists(KEYS_FILE):
        return {}
    with open(KEYS_FILE) as f:
        return json.load(f)


def _save(data: dict) -> None:
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(KEYS_FILE, "w") as f:
        json.dump(data, f, indent=2)
    os.chmod(KEYS_FILE, stat.S_IRUSR | stat.S_IWUSR)


def get_key(name: str) -> str | None:
    val = _load().get(name)
    if val is None or val == SKIP_SENTINEL:
        return None
    return val


def prompt_and_save_key(name: str, prompt_text: str) -> str | None:
    value = console.input(f"  [dim]{prompt_text}[/dim] ").strip()
    data = _load()
    if not value:
        data[name] = SKIP_SENTINEL
        _save(data)
        return None
    data[name] = value
    _save(data)
    return value


def require_key(name: str, prompt_text: str) -> str | None:
    raw = _load().get(name)
    if raw == SKIP_SENTINEL:
        return None
    if raw:
        return raw
    return prompt_and_save_key(name, prompt_text)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd /home/deegan/iCrackU && source venv/bin/activate && python -m pytest tests/test_config.py -v
```

Expected: 7 passed

- [ ] **Step 5: Commit**

```bash
git -C /home/deegan/iCrackU add core/config.py tests/test_config.py
git -C /home/deegan/iCrackU commit -m "feat: add core/config.py for API key management"
```

---

## Task 2: `modules/ip.py`

**Files:**
- Create: `modules/ip.py`
- Modify: `tests/test_modules.py`

- [ ] **Step 1: Add failing test to `tests/test_modules.py`**

Append to the existing file:

```python
def test_ip_lookup_returns_list():
    import socket
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"ip": "8.8.8.8", "city": "Mountain View", "org": "AS15169 Google"}
    with patch("modules.ip.requests.get", return_value=mock_resp), \
         patch("modules.ip.socket.gethostbyaddr", return_value=("dns.google", [], ["8.8.8.8"])), \
         patch("core.runner.run_tool", side_effect=fake_run_tool), \
         patch("modules.ip.require_key", return_value=None):
        from modules.ip import lookup
        results = lookup("8.8.8.8", on_line=None)
    assert isinstance(results, list)
    assert all("tool" in r for r in results)
    assert any(r["tool"] == "ipinfo" for r in results)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /home/deegan/iCrackU && source venv/bin/activate && python -m pytest tests/test_modules.py::test_ip_lookup_returns_list -v
```

Expected: `ModuleNotFoundError: No module named 'modules.ip'`

- [ ] **Step 3: Implement `modules/ip.py`**

```python
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
    results.append({"tool": "ipinfo", "query": query, "returncode": rc, "output": output})

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
    results.append({"tool": "reverse-dns", "query": query, "returncode": rc, "output": output})

    # whois CLI — free
    results.append(run_tool("whois", [query], query, on_line))

    # Shodan — optional API key
    key = require_key("shodan", "Shodan API key (Enter to skip): ")
    if not key:
        results.append({
            "tool": "shodan",
            "query": query,
            "returncode": -1,
            "output": "shodan — API key not configured (Enter to skip next time)",
        })
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
    results.append({"tool": "shodan", "query": query, "returncode": rc, "output": output})

    return results
```

- [ ] **Step 4: Install requests if needed, run test**

```bash
cd /home/deegan/iCrackU && source venv/bin/activate && pip install requests -q && python -m pytest tests/test_modules.py::test_ip_lookup_returns_list -v
```

Expected: PASS

- [ ] **Step 5: Run full test suite**

```bash
python -m pytest tests/ -v
```

Expected: all previous 13 + 1 new = 14 passed

- [ ] **Step 6: Commit**

```bash
git -C /home/deegan/iCrackU add modules/ip.py tests/test_modules.py
git -C /home/deegan/iCrackU commit -m "feat: add modules/ip.py for IP lookup"
```

---

## Task 3: `modules/domain.py`

**Files:**
- Create: `modules/domain.py`
- Modify: `tests/test_modules.py`

- [ ] **Step 1: Add failing test to `tests/test_modules.py`**

Append:

```python
def test_domain_lookup_returns_list():
    mock_whois = MagicMock()
    mock_whois.registrar = "GoDaddy"
    mock_whois.creation_date = "2000-01-01"
    mock_whois.expiration_date = "2030-01-01"
    mock_whois.name_servers = ["ns1.example.com", "ns2.example.com"]

    mock_answer = MagicMock()
    mock_answer.__iter__ = MagicMock(return_value=iter([MagicMock(address="93.184.216.34")]))

    with patch("modules.domain.whois.whois", return_value=mock_whois), \
         patch("modules.domain.dns.resolver.resolve", return_value=mock_answer), \
         patch("core.runner.run_tool", side_effect=fake_run_tool):
        from modules.domain import lookup
        results = lookup("example.com", on_line=None)
    assert isinstance(results, list)
    assert all("tool" in r for r in results)
    assert any(r["tool"] == "whois-py" for r in results)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /home/deegan/iCrackU && source venv/bin/activate && python -m pytest tests/test_modules.py::test_domain_lookup_returns_list -v
```

Expected: `ModuleNotFoundError: No module named 'modules.domain'`

- [ ] **Step 3: Install dependencies**

```bash
cd /home/deegan/iCrackU && source venv/bin/activate && pip install python-whois dnspython -q
```

- [ ] **Step 4: Implement `modules/domain.py`**

```python
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
            f"Registrar:   {w.registrar or 'n/a'}",
            f"Created:     {w.creation_date or 'n/a'}",
            f"Expires:     {w.expiration_date or 'n/a'}",
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
    results.append(run_tool("subfinder", ["-d", query, "-silent"], query, on_line))

    return results
```

- [ ] **Step 5: Run test**

```bash
cd /home/deegan/iCrackU && source venv/bin/activate && python -m pytest tests/test_modules.py::test_domain_lookup_returns_list -v
```

Expected: PASS

- [ ] **Step 6: Run full suite**

```bash
python -m pytest tests/ -v
```

Expected: 15 passed

- [ ] **Step 7: Commit**

```bash
git -C /home/deegan/iCrackU add modules/domain.py tests/test_modules.py
git -C /home/deegan/iCrackU commit -m "feat: add modules/domain.py for domain/WHOIS lookup"
```

---

## Task 4: `modules/breach.py`

**Files:**
- Create: `modules/breach.py`
- Modify: `tests/test_modules.py`

- [ ] **Step 1: Add failing test to `tests/test_modules.py`**

Append:

```python
def test_breach_lookup_returns_list():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = [
        {"Name": "Adobe", "PwnCount": 153000000, "IsVerified": True},
        {"Name": "LinkedIn", "PwnCount": 164611595, "IsVerified": True},
    ]
    with patch("modules.breach.requests.get", return_value=mock_resp), \
         patch("modules.breach.require_key", return_value="testkey"):
        from modules.breach import lookup
        results = lookup("foo@bar.com", on_line=None)
    assert isinstance(results, list)
    assert any(r["tool"] == "hibp" for r in results)
    assert results[0]["returncode"] == 0
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /home/deegan/iCrackU && source venv/bin/activate && python -m pytest tests/test_modules.py::test_breach_lookup_returns_list -v
```

Expected: `ModuleNotFoundError: No module named 'modules.breach'`

- [ ] **Step 3: Implement `modules/breach.py`**

```python
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
        return [{
            "tool": "hibp",
            "query": query,
            "returncode": -1,
            "output": "hibp — API key not configured",
        }]

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
```

- [ ] **Step 4: Run test**

```bash
cd /home/deegan/iCrackU && source venv/bin/activate && python -m pytest tests/test_modules.py::test_breach_lookup_returns_list -v
```

Expected: PASS

- [ ] **Step 5: Run full suite**

```bash
python -m pytest tests/ -v
```

Expected: 16 passed

- [ ] **Step 6: Commit**

```bash
git -C /home/deegan/iCrackU add modules/breach.py tests/test_modules.py
git -C /home/deegan/iCrackU commit -m "feat: add modules/breach.py for HaveIBeenPwned breach check"
```

---

## Task 5: `modules/hash.py`

**Files:**
- Create: `modules/hash.py`
- Modify: `tests/test_modules.py`

- [ ] **Step 1: Add failing test to `tests/test_modules.py`**

Append:

```python
def test_hash_lookup_returns_list():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "data": {"attributes": {"meaningful_name": "eicar.txt", "last_analysis_stats": {"malicious": 0}}}
    }
    with patch("core.runner.run_tool", side_effect=fake_run_tool), \
         patch("modules.hash.requests.get", return_value=mock_resp), \
         patch("modules.hash.require_key", return_value="vtkey"):
        from modules.hash import lookup
        results = lookup("d41d8cd98f00b204e9800998ecf8427e", on_line=None)
    assert isinstance(results, list)
    assert any(r["tool"] == "hashid" for r in results)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /home/deegan/iCrackU && source venv/bin/activate && python -m pytest tests/test_modules.py::test_hash_lookup_returns_list -v
```

Expected: `ModuleNotFoundError: No module named 'modules.hash'`

- [ ] **Step 3: Implement `modules/hash.py`**

```python
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
    results.append(run_tool("hashid", [query], query, on_line))

    # VirusTotal — optional API key
    key = require_key(
        "virustotal",
        "VirusTotal API key (free at virustotal.com — Enter to skip): ",
    )
    if not key:
        results.append({
            "tool": "virustotal",
            "query": query,
            "returncode": -1,
            "output": "virustotal — API key not configured",
        })
        return results

    if on_tool_start:
        on_tool_start("virustotal")
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

    results.append({"tool": "virustotal", "query": query, "returncode": rc, "output": output})
    return results
```

- [ ] **Step 4: Run test**

```bash
cd /home/deegan/iCrackU && source venv/bin/activate && python -m pytest tests/test_modules.py::test_hash_lookup_returns_list -v
```

Expected: PASS

- [ ] **Step 5: Run full suite**

```bash
python -m pytest tests/ -v
```

Expected: 17 passed

- [ ] **Step 6: Commit**

```bash
git -C /home/deegan/iCrackU add modules/hash.py tests/test_modules.py
git -C /home/deegan/iCrackU commit -m "feat: add modules/hash.py for hash identification and VirusTotal lookup"
```

---

## Task 6: Wire into `icrack.py` and `requirements.txt`

**Files:**
- Modify: `icrack.py`
- Modify: `requirements.txt`

- [ ] **Step 1: Update `requirements.txt`**

Replace the file with:

```
rich>=13.0.0
geopy>=2.4.0
pytest>=8.0.0
requests>=2.31.0
dnspython>=2.4.0
python-whois>=0.9.0
shodan>=1.28.0
```

- [ ] **Step 2: Install new dependencies**

```bash
cd /home/deegan/iCrackU && source venv/bin/activate && pip install requests dnspython python-whois shodan -q
```

- [ ] **Step 3: Update imports in `icrack.py`**

Add after the existing module imports (after `import modules.address as mod_address`):

```python
import modules.ip as mod_ip
import modules.domain as mod_domain
import modules.breach as mod_breach
import modules.hash as mod_hash
```

- [ ] **Step 4: Update `CLI_TOOLS` and `PYTHON_LIBS` in `icrack.py`**

Replace the existing `CLI_TOOLS` and `PYTHON_LIBS` dicts with:

```python
CLI_TOOLS = {
    "holehe":       "pip install holehe",
    "theHarvester": "pip install theHarvester",
    "ghunt":        "pip install ghunt",
    "sherlock":     "pip install sherlock-project",
    "maigret":      "pip install maigret",
    "phoneinfoga":  "https://github.com/sundowndev/phoneinfoga",
    "whois":        "apt install whois",
    "subfinder":    "go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest",
    "hashid":       "pip install hashid",
}

PYTHON_LIBS = {
    "geopy":     "pip install geopy",
    "requests":  "pip install requests",
    "dns":       "pip install dnspython",
    "whois":     "pip install python-whois",
    "shodan":    "pip install shodan",
}
```

- [ ] **Step 5: Add new CLI flags to `main()` in `icrack.py`**

After `parser.add_argument("--address", ...)` add:

```python
    parser.add_argument("--ip",      metavar="IP",      help="IP address lookup")
    parser.add_argument("--domain",  metavar="DOMAIN",  help="Domain/WHOIS lookup")
    parser.add_argument("--breach",  metavar="EMAIL",   help="Breach check (HaveIBeenPwned)")
    parser.add_argument("--hash",    metavar="HASH",    help="Hash identification and lookup")
```

After `elif args.address:` add:

```python
    elif args.ip:
        run_lookup("ip", args.ip, mod_ip)
    elif args.domain:
        run_lookup("domain", args.domain, mod_domain)
    elif args.breach:
        run_lookup("breach", args.breach, mod_breach)
    elif args.hash:
        run_lookup("hash", args.hash, mod_hash)
```

- [ ] **Step 6: Update `interactive_menu()` in `icrack.py`**

Replace the `options` list with:

```python
    options = [
        ("1", "Email lookup",         "email"),
        ("2", "Username lookup",      "username"),
        ("3", "Phone lookup",         "phone"),
        ("4", "Name lookup",          "name"),
        ("5", "Address lookup",       "address"),
        ("6", "IP lookup",            "ip"),
        ("7", "Domain lookup",        "domain"),
        ("8", "Breach check",         "breach"),
        ("9", "Hash lookup",          "hash"),
        ("10", "Check installed tools", None),
        ("11", "List saved results",    None),
        ("0", "Exit",                   None),
    ]
```

Update the `elif choice == "6":` and `elif choice == "7":` blocks to use the new numbers:

```python
        if choice == "0":
            console.print("[dim]  bye[/dim]")
            sys.exit(0)
        elif choice == "10":
            check_tools()
        elif choice == "11":
            list_results()
```

Add the new module to the module dispatch dict inside the loop:

```python
            module = {
                "email":    mod_email,
                "username": mod_username,
                "phone":    mod_phone,
                "name":     mod_name,
                "address":  mod_address,
                "ip":       mod_ip,
                "domain":   mod_domain,
                "breach":   mod_breach,
                "hash":     mod_hash,
            }[lookup_type]
```

- [ ] **Step 7: Run full test suite**

```bash
cd /home/deegan/iCrackU && source venv/bin/activate && python -m pytest tests/ -v
```

Expected: 17 passed (all existing tests pass; icrack.py changes have no new tests since they're wiring only)

- [ ] **Step 8: Smoke test**

```bash
python icrack.py --check
```

Expected: new tools (whois, subfinder, hashid) and libs (requests, dns, whois, shodan) appear in the table.

- [ ] **Step 9: Commit**

```bash
git -C /home/deegan/iCrackU add icrack.py requirements.txt
git -C /home/deegan/iCrackU commit -m "feat: wire ip/domain/breach/hash modules into CLI and menu"
```
