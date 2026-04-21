# Sub-project 2: Target Profile / Multi-Lookup

**Date:** 2026-04-21
**Status:** Approved
**Depends on:** Sub-project 1 (new lookup modules)

---

## Goal

Add a target profile mode that runs all relevant lookups for a single subject and aggregates results into a combined profile. Available as `--target` CLI flag and as an interactive profile builder in the menu.

---

## Section 1: Auto-detect — `--target` flag

A new `core/profiler.py` classifies input and dispatches the right modules:

| Pattern | Modules run |
|---|---|
| Contains `@` | email + breach |
| Valid IP (`\d{1,3}(\.\d{1,3}){3}`) | ip |
| Has `.`, no `@`, no spaces | domain |
| Starts with `+` or all digits, 7–15 chars | phone |
| Anything else | username + name |

Multiple patterns can match the same input (e.g. `foo@bar.com` → email + breach).

Results from all dispatched modules are collected. A combined `profile_<timestamp>_<slug>.json` is saved to `results/` alongside the individual per-lookup files. The terminal shows each tool's live output as it runs, then a combined summary table at the end.

---

## Section 2: Interactive Profile Builder

New menu option **`P  Target profile`** added above option `10  Check installed tools`.

Flow — prompts for each identifier, Enter to skip:
```
  name      > John Doe
  email     > johndoe@gmail.com
  username  > johndoe
  phone     > (skip)
  ip        > (skip)
  domain    > (skip)
```

Runs all non-skipped lookups in sequence. Shows live output per tool. After all lookups complete, prints combined summary then saves profile JSON.

---

## Section 3: Combined Profile Output

**Terminal summary** printed after all lookups complete:

```
── profile summary ─────────────────────────────────
  name      John Doe
  email     johndoe@gmail.com
  username  johndoe

  Tool            Type       Status   Lines
 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  holehe          email      ✓        18
  theHarvester    email      ✓        42
  sherlock        username   ✓        31
  hibp            breach     ✓        4
```

**Profile JSON structure** (`results/profile_<timestamp>_<slug>.json`):
```json
{
  "timestamp": "2026-04-21_063340",
  "type": "profile",
  "targets": [
    {
      "identifier": "johndoe@gmail.com",
      "lookup_type": "email",
      "tools": [{ "name": "holehe", "returncode": 0, "output": "..." }]
    },
    {
      "identifier": "johndoe@gmail.com",
      "lookup_type": "breach",
      "tools": [{ "name": "hibp", "returncode": 0, "output": "..." }]
    }
  ]
}
```

This structure is consumed by Sub-project 3 (report export).

---

## Section 4: Testing

**`tests/test_profiler.py`** — new file:
- `test_classify_email` — assert `foo@bar.com` → `["email", "breach"]`
- `test_classify_ip` — assert `8.8.8.8` → `["ip"]`
- `test_classify_domain` — assert `example.com` → `["domain"]`
- `test_classify_phone` — assert `+15551234567` → `["phone"]`
- `test_classify_username` — assert `johndoe` → `["username", "name"]`
- `test_run_profile_returns_combined_results` — mock all module lookups, assert combined profile structure

---

## Files Created/Modified

| File | Action |
|---|---|
| `core/profiler.py` | Create |
| `icrack.py` | Modify — add `--target` flag, `P` menu option, import profiler |
| `tests/test_profiler.py` | Create |
