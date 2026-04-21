# Report Export Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate HTML and/or Markdown reports from any saved result JSON (single lookup or profile). Triggered via `--report <file>` CLI flag, post-lookup `--report` flag, or interactive menu option `R`.

**Architecture:** A new `core/reporter.py` exposes `generate_html(data)` and `generate_markdown(data)` — pure functions that accept the standard result dict and return a string. `icrack.py` handles the `--report`/`--format` flags and `R` menu option. Reports are saved alongside the source JSON.

**Tech Stack:** Python 3.12+, Rich (terminal output only), standard library html/string for report generation

**Prerequisite:** Sub-projects 1 and 2 must be implemented. This plan uses the profile JSON structure from Sub-project 2.

---

## File Map

| File | Action |
|---|---|
| `core/reporter.py` | Create — HTML and Markdown generation |
| `tests/test_reporter.py` | Create |
| `icrack.py` | Modify — `--report`, `--format` flags, `R` menu option |

---

## Task 1: `core/reporter.py` — Markdown generation

**Files:**
- Create: `core/reporter.py`
- Create: `tests/test_reporter.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_reporter.py
import pytest
from core.reporter import generate_markdown, generate_html

SAMPLE_DATA = {
    "timestamp": "2026-04-21_063340",
    "type": "email",
    "query": "foo@bar.com",
    "tools": [
        {"name": "holehe", "returncode": 0, "output": "twitter: found\nfacebook: not found"},
        {"name": "ghunt",  "returncode": -1, "output": "ghunt not found — skipping"},
    ],
}

SAMPLE_PROFILE = {
    "timestamp": "2026-04-21_070000",
    "type": "profile",
    "targets": [
        {
            "identifier": "foo@bar.com",
            "lookup_type": "email",
            "tools": [{"name": "holehe", "returncode": 0, "output": "twitter: found"}],
        },
        {
            "identifier": "foo@bar.com",
            "lookup_type": "breach",
            "tools": [{"name": "hibp", "returncode": 0, "output": "Found in 2 breach(es)"}],
        },
    ],
}


def test_generate_markdown_contains_query():
    md = generate_markdown(SAMPLE_DATA)
    assert "foo@bar.com" in md


def test_generate_markdown_contains_summary_table():
    md = generate_markdown(SAMPLE_DATA)
    assert "| Tool |" in md or "| tool |" in md.lower()


def test_generate_markdown_contains_tool_section():
    md = generate_markdown(SAMPLE_DATA)
    assert "## holehe" in md


def test_generate_markdown_contains_output():
    md = generate_markdown(SAMPLE_DATA)
    assert "twitter: found" in md


def test_generate_markdown_handles_profile():
    md = generate_markdown(SAMPLE_PROFILE)
    assert "foo@bar.com" in md
    assert "holehe" in md
    assert "hibp" in md


def test_generate_html_contains_query():
    html = generate_html(SAMPLE_DATA)
    assert "foo@bar.com" in html


def test_generate_html_contains_tool_name():
    html = generate_html(SAMPLE_DATA)
    assert "holehe" in html


def test_generate_html_is_valid_structure():
    html = generate_html(SAMPLE_DATA)
    assert "<html" in html
    assert "<body" in html
    assert "<details" in html


def test_generate_html_handles_profile():
    html = generate_html(SAMPLE_PROFILE)
    assert "hibp" in html
    assert "holehe" in html


def test_generate_html_dark_theme():
    html = generate_html(SAMPLE_DATA)
    assert "#0d0d0d" in html or "0d0d0d" in html
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /home/deegan/iCrackU && source venv/bin/activate && python -m pytest tests/test_reporter.py -v
```

Expected: `ModuleNotFoundError: No module named 'core.reporter'`

- [ ] **Step 3: Implement `core/reporter.py`**

```python
from datetime import datetime


_STATUS = {0: "✓", -1: "–", -2: "⏱"}


def _status_str(rc: int) -> str:
    return _STATUS.get(rc, f"exit {rc}")


def _tools_from_data(data: dict) -> list[tuple[str, str, int, str]]:
    """Return list of (tool_name, lookup_type, returncode, output) tuples."""
    if data.get("type") == "profile":
        rows = []
        for target in data.get("targets", []):
            lt = target["lookup_type"]
            for t in target["tools"]:
                rows.append((t["name"], lt, t["returncode"], t["output"]))
        return rows
    return [
        (t["name"], data.get("type", ""), t["returncode"], t["output"])
        for t in data.get("tools", [])
    ]


def generate_markdown(data: dict) -> str:
    query = data.get("query") or (
        data["targets"][0]["identifier"] if data.get("targets") else "profile"
    )
    lookup_type = data.get("type", "lookup")
    timestamp = data.get("timestamp", "")
    tools = _tools_from_data(data)

    lines = [
        f"# iCrackU Report — {lookup_type} — {query}",
        f"**Generated:** {timestamp.replace('_', ' ')}",
        "",
        "## Summary",
        "",
        "| Tool | Type | Status | Lines |",
        "|---|---|---|---|",
    ]
    for name, lt, rc, output in tools:
        lines.append(f"| {name} | {lt} | {_status_str(rc)} | {len(output.splitlines())} |")

    lines.append("")

    for name, lt, rc, output in tools:
        lines.append(f"## {name}")
        lines.append("")
        lines.append("```")
        lines.append(output)
        lines.append("```")
        lines.append("")

    return "\n".join(lines)


def generate_html(data: dict) -> str:
    query = data.get("query") or (
        data["targets"][0]["identifier"] if data.get("targets") else "profile"
    )
    lookup_type = data.get("type", "lookup")
    timestamp = data.get("timestamp", "").replace("_", " ")
    tools = _tools_from_data(data)

    summary_rows = "".join(
        f"<tr><td>{name}</td><td>{lt}</td>"
        f"<td>{_status_str(rc)}</td><td>{len(output.splitlines())}</td></tr>"
        for name, lt, rc, output in tools
    )

    tool_sections = "".join(
        f"<details><summary>{name} <span class='type'>{lt}</span>"
        f" <span class='status'>{_status_str(rc)}</span></summary>"
        f"<pre>{_escape(output)}</pre></details>"
        for name, lt, rc, output in tools
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>iCrackU — {lookup_type} — {_escape(query)}</title>
<style>
  body {{background:#0d0d0d;color:#cccccc;font-family:monospace;padding:2rem;}}
  h1 {{color:#00ff41;border-bottom:1px solid #333;padding-bottom:.5rem;}}
  h2 {{color:#00ff41;margin-top:2rem;}}
  .meta {{color:#555;font-size:.85rem;margin-bottom:2rem;}}
  table {{border-collapse:collapse;width:100%;margin:1rem 0;}}
  th {{text-align:left;border-bottom:2px solid #00ff41;padding:.4rem .8rem;color:#00ff41;}}
  td {{padding:.3rem .8rem;border-bottom:1px solid #1a1a1a;}}
  details {{margin:.5rem 0;background:#1a1a1a;border-left:2px solid #00ff41;}}
  summary {{padding:.5rem 1rem;cursor:pointer;color:#00ff41;}}
  summary:hover {{background:#222;}}
  pre {{padding:1rem;overflow-x:auto;white-space:pre-wrap;word-break:break-all;margin:0;}}
  .type {{color:#555;font-size:.8rem;}}
  .status {{color:#00ff41;}}
  footer {{margin-top:3rem;color:#333;font-size:.8rem;border-top:1px solid #1a1a1a;padding-top:1rem;}}
</style>
</head>
<body>
<h1>iCrackU</h1>
<div class="meta">{lookup_type} &nbsp;·&nbsp; {_escape(query)} &nbsp;·&nbsp; {timestamp}</div>
<h2>Summary</h2>
<table>
  <tr><th>Tool</th><th>Type</th><th>Status</th><th>Lines</th></tr>
  {summary_rows}
</table>
<h2>Results</h2>
{tool_sections}
<footer>Generated by iCrackU &nbsp;·&nbsp; {timestamp}</footer>
</body>
</html>"""


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
    )
```

- [ ] **Step 4: Run all reporter tests**

```bash
cd /home/deegan/iCrackU && source venv/bin/activate && python -m pytest tests/test_reporter.py -v
```

Expected: 10 passed

- [ ] **Step 5: Run full test suite**

```bash
python -m pytest tests/ -v
```

Expected: all previous + 10 new passed

- [ ] **Step 6: Commit**

```bash
git -C /home/deegan/iCrackU add core/reporter.py tests/test_reporter.py
git -C /home/deegan/iCrackU commit -m "feat: add core/reporter.py for HTML and Markdown report generation"
```

---

## Task 2: Wire `--report`, `--format`, and `R` menu into `icrack.py`

**Files:**
- Modify: `icrack.py`

- [ ] **Step 1: Add `generate_report` helper to `icrack.py`**

Add this function after `run_target_profile` (or after `list_results` if Sub-project 2 isn't done yet):

```python
def generate_report(json_path: str, fmt: str = "html"):
    import json as json_lib
    from core.reporter import generate_html, generate_markdown

    if not os.path.exists(json_path):
        console.print(f"  [red]File not found:[/red] {json_path}")
        return

    with open(json_path) as f:
        data = json_lib.load(f)

    base = os.path.splitext(json_path)[0]
    generated = []

    if fmt in ("html", "both"):
        html_path = f"{base}.html"
        with open(html_path, "w") as f:
            f.write(generate_html(data))
        generated.append(html_path)

    if fmt in ("md", "both"):
        md_path = f"{base}.md"
        with open(md_path, "w") as f:
            f.write(generate_markdown(data))
        generated.append(md_path)

    print_header()
    console.print("  [dim]report generated[/dim]\n")
    for path in generated:
        console.print(f"  [bright_green]→[/bright_green]  {path}")
    console.print()
```

- [ ] **Step 2: Add `--report` and `--format` flags to `main()` in `icrack.py`**

After `parser.add_argument("--target", ...)` add:

```python
    parser.add_argument("--report", metavar="JSON_FILE", help="Generate report from saved result JSON")
    parser.add_argument("--format", metavar="FORMAT",   help="Report format: html (default), md, or both", default="html")
```

After `elif args.target:` add:

```python
    elif args.report:
        generate_report(args.report, fmt=args.format)
```

- [ ] **Step 3: Add post-lookup `--report` generation**

In `run_lookup`, after `print_summary(...)`, add:

```python
    if getattr(run_lookup, "_report_fmt", None):
        generate_report(json_path, fmt=run_lookup._report_fmt)
```

Then in `main()`, before each `run_lookup(...)` call, inject the flag:

```python
    run_lookup._report_fmt = args.format if args.report and not args.report.endswith(".json") else None
```

Wait — this approach is awkward. Instead, pass `report_fmt` as a parameter. Replace `run_lookup` signature and body:

```python
def run_lookup(lookup_type: str, query: str, module, report_fmt: str | None = None):
    print_header()
    console.print(f"  [dim]{lookup_type}[/dim]  [bold]{query}[/bold]\n")

    tool_results = module.lookup(
        query, on_line=print_line, on_tool_start=print_tool_header
    )

    os.makedirs(RESULTS_DIR, exist_ok=True)
    txt_path, json_path = save_results(
        lookup_type=lookup_type,
        query=query,
        tool_results=tool_results,
        results_dir=RESULTS_DIR,
    )
    print_summary(tool_results, txt_path, json_path)

    if report_fmt:
        generate_report(json_path, fmt=report_fmt)
```

In `main()`, pass `report_fmt` to each `run_lookup` call. Example for `--email`:

```python
    elif args.email:
        run_lookup("email", args.email, mod_email,
                   report_fmt=args.format if hasattr(args, "report") and args.report is None and True else None)
```

Actually, simplify: add a boolean `--report` flag as a post-lookup trigger (separate from `--report <file>`). Use `--save-report` for the post-lookup version to avoid ambiguity:

Replace the two `--report` / `--format` argparse lines with:

```python
    parser.add_argument("--report",      metavar="JSON_FILE", help="Generate report from saved result JSON")
    parser.add_argument("--save-report", action="store_true", help="Generate report after lookup completes")
    parser.add_argument("--format",      metavar="FORMAT",    default="html",
                        help="Report format: html (default), md, or both")
```

And pass to run_lookup:

```python
    report_fmt = args.format if args.save_report else None
    if args.report:
        generate_report(args.report, fmt=args.format)
    elif args.email:
        run_lookup("email", args.email, mod_email, report_fmt=report_fmt)
    elif args.username:
        run_lookup("username", args.username, mod_username, report_fmt=report_fmt)
    elif args.phone:
        run_lookup("phone", args.phone, mod_phone, report_fmt=report_fmt)
    elif args.name:
        run_lookup("name", args.name, mod_name, report_fmt=report_fmt)
    elif args.address:
        run_lookup("address", args.address, mod_address, report_fmt=report_fmt)
    elif args.ip:
        run_lookup("ip", args.ip, mod_ip, report_fmt=report_fmt)
    elif args.domain:
        run_lookup("domain", args.domain, mod_domain, report_fmt=report_fmt)
    elif args.breach:
        run_lookup("breach", args.breach, mod_breach, report_fmt=report_fmt)
    elif args.hash:
        run_lookup("hash", args.hash, mod_hash, report_fmt=report_fmt)
    elif args.target:
        from core.profiler import classify
        lookup_types = classify(args.target)
        inputs = {lt: args.target for lt in lookup_types}
        run_target_profile(inputs)
    else:
        interactive_menu()
```

- [ ] **Step 4: Add `R` menu option to `interactive_menu()` in `icrack.py`**

Add `("R", "Generate report", None)` to the options list just before `("10", ...)`:

```python
        ("R",  "Generate report",       None),
        ("10", "Check installed tools", None),
```

Add handling in the `while True` loop (after `elif choice == "11":`):

```python
        elif choice in ("r", "R"):
            files = (
                sorted(
                    [f for f in os.listdir(RESULTS_DIR) if f.endswith(".json")],
                    reverse=True,
                )
                if os.path.isdir(RESULTS_DIR)
                else []
            )
            if not files:
                console.print("  [dim]No saved results found.[/dim]")
                continue
            list_results()
            pick = console.input("  [dim]select #[/dim]  > ").strip()
            try:
                chosen = files[int(pick) - 1]
            except (ValueError, IndexError):
                console.print("[dim]  invalid selection[/dim]")
                continue
            fmt = console.input("  [dim]format (html/md/both)[/dim]  > ").strip() or "html"
            generate_report(os.path.join(RESULTS_DIR, chosen), fmt=fmt)
```

- [ ] **Step 5: Run full test suite**

```bash
cd /home/deegan/iCrackU && source venv/bin/activate && python -m pytest tests/ -v
```

Expected: all tests pass

- [ ] **Step 6: Smoke test**

```bash
# Generate report from an existing result file
ls results/*.json | head -1 | xargs -I{} python icrack.py --report {} --format both
```

Expected: two files created (`.html` and `.md`) alongside the source JSON, paths printed to terminal.

- [ ] **Step 7: Commit**

```bash
git -C /home/deegan/iCrackU add icrack.py
git -C /home/deegan/iCrackU commit -m "feat: add --report, --save-report, --format flags and R menu option"
```
