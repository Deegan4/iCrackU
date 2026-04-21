# Sub-project 1: New Lookup Modules

**Date:** 2026-04-21
**Status:** Approved

---

## Goal

Add four new lookup modules (`ip`, `domain`, `breach`, `hash`) and a config system for API key management. Free tools work by default; API-key services are prompted once at runtime and cached.

---

## Section 1: Config System — `core/config.py`

Keys stored at `~/.icrackU/keys.json`, `chmod 600` on creation.

**Functions:**
- `get_key(name: str) -> str | None` — return cached key or None
- `prompt_and_save_key(name: str, prompt_text: str) -> str` — prompt user, write to file, return value
- `require_key(name: str, prompt_text: str) -> str` — get_key → if missing, prompt_and_save_key

Supported key names: `"shodan"`, `"hibp"`, `"virustotal"`.

Every module degrades gracefully if a key is absent — skips the keyed tool and notes it in output. No key is ever required to run a lookup.

---

## Section 2: New Modules

All modules follow the existing interface: `lookup(query, on_line, on_tool_start) -> list[dict]`.

### `modules/ip.py`

Free tools:
- `ipinfo.io` REST API (no key, 50k req/day) via `requests` — returns geolocation, ASN, org
- `socket.gethostbyaddr()` for reverse DNS
- `whois` CLI

Optional (key prompted on first use):
- Shodan host lookup via `shodan` pip package (`require_key("shodan", ...)`)

### `modules/domain.py`

Free tools:
- `python-whois` pip package for registration data
- `dnspython` pip package for A, MX, NS, TXT records
- `whois` CLI

Optional (no key required):
- `subfinder` CLI for subdomain enumeration if installed

### `modules/breach.py`

Requires HaveIBeenPwned v3 API key (free tier available at haveibeenpwned.com/API/Key):
- `require_key("hibp", "Enter HaveIBeenPwned API key: ")`
- Returns: breach names, paste count, whether passwords were exposed
- Degrades to a "key required — run iCrackU --check to configure" message if user skips prompt

### `modules/hash.py`

Free tools:
- `hashid` CLI for hash type identification

Optional (key prompted on first use):
- VirusTotal file/hash lookup via REST API (`require_key("virustotal", ...)`)

---

## Section 3: CLI and Menu Wiring

**New CLI flags:** `--ip`, `--domain`, `--breach`, `--hash`

**New menu entries** (inserted between address and check-tools):
```
  6  IP lookup
  7  Domain lookup
  8  Breach check
  9  Hash lookup
 10  Check installed tools
 11  List saved results
```

**`CLI_TOOLS` additions:** `subfinder`, `hashid`, `whois`

**`PYTHON_LIBS` additions:** `shodan`, `dnspython`, `python-whois`, `requests`

**`requirements.txt` additions:** `dnspython`, `python-whois`, `requests`, `shodan`

---

## Section 4: Testing

**`tests/test_modules.py`** — four new tests following existing mock pattern:
- `test_ip_lookup_returns_list`
- `test_domain_lookup_returns_list`
- `test_breach_lookup_returns_list`
- `test_hash_lookup_returns_list`

All network calls (`requests.get`, `shodan.Shodan`, `whois.whois`, `dns.resolver.resolve`) patched. No live API calls.

**`tests/test_config.py`** — new file:
- `test_get_key_returns_none_when_missing` — tmp_path, no keys file
- `test_get_key_returns_value_when_present` — write keys file, assert value returned
- `test_prompt_and_save_key_writes_file` — mock `console.input`, assert file written
- `test_require_key_prompts_when_missing` — mock input, assert key returned and saved
- `test_require_key_returns_cached_key` — pre-write key, assert no prompt

---

## Files Created/Modified

| File | Action |
|---|---|
| `core/config.py` | Create |
| `modules/ip.py` | Create |
| `modules/domain.py` | Create |
| `modules/breach.py` | Create |
| `modules/hash.py` | Create |
| `icrack.py` | Modify — add flags, menu entries, module imports, CLI_TOOLS/PYTHON_LIBS |
| `requirements.txt` | Modify — add dnspython, python-whois, requests, shodan |
| `tests/test_config.py` | Create |
| `tests/test_modules.py` | Modify — add 4 new tests |
