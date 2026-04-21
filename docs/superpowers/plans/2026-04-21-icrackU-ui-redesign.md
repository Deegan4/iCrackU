# iCrackU UI Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the colorful ASCII-banner UI with a restrained Claude Code-style terminal aesthetic — one `steel_blue` accent, plain white body text, dim secondary text, simple horizontal rules, no line-by-line colorization.

**Architecture:** Two files change — `core/output.py` (all print functions rewritten) and `icrack.py` (menu, table styles, prompts updated). No logic, no signatures, no saved-results format changes. Existing tests all pass unchanged because they mock at the `run_tool` level and never call output functions.

**Tech Stack:** Python 3.12+, Rich (`Console`, `Table`, `box`, `rule`)

---

## File Map

| File | Change |
|---|---|
| `core/output.py` | Full rewrite of all print/render functions |
| `icrack.py` | Update `run_lookup`, `check_tools`, `list_results`, `interactive_menu` |

---

## Task 1: Rewrite `core/output.py`

**Files:**
- Modify: `core/output.py`

- [ ] **Step 1: Replace the file with the new implementation**

```python
from rich.console import Console
from rich import box
from rich.table import Table

console = Console()

HEADER_WIDTH = 32


def print_header():
    console.print(f"[steel_blue]  iCrackU[/steel_blue][dim]  ·  OSINT Lookup Tool[/dim]")
    console.print(f"[dim]  {'─' * HEADER_WIDTH}[/dim]")


def print_tool_header(tool_name: str, query: str):
    console.rule(f"[dim]{tool_name}[/dim]", style="dim")


def print_line(line: str):
    console.print(line)


def print_tool_skipped(tool_name: str):
    console.print(f"[dim]  {tool_name}  not installed[/dim]")


def print_summary(tool_results: list[dict], txt_path: str, json_path: str):
    console.print()
    table = Table(box=box.SIMPLE_HEAD, show_header=True, header_style="dim")
    table.add_column("Tool")
    table.add_column("Status")
    table.add_column("Lines")

    for r in tool_results:
        if r["returncode"] == -1:
            status = "–"
        elif r["returncode"] == -2:
            status = "⏱"
        elif r["returncode"] == 0:
            status = "✓"
        else:
            status = f"exit {r['returncode']}"
        lines = str(len(r["output"].splitlines()))
        table.add_row(r["tool"], status, lines)

    console.print(table)
    console.print(f"[dim]  saved  [/dim]{txt_path}")
    console.print(f"[dim]         [/dim]{json_path}")
```

- [ ] **Step 2: Run existing tests to confirm no regressions**

```bash
cd /home/deegan/iCrackU && source venv/bin/activate && python -m pytest tests/ -v
```

Expected: all 13 tests pass (output.py functions are never called by tests — they mock at run_tool level).

- [ ] **Step 3: Commit**

```bash
git -C /home/deegan/iCrackU add core/output.py
git -C /home/deegan/iCrackU commit -m "feat: rewrite output.py to Claude Code style"
```

---

## Task 2: Update `icrack.py`

**Files:**
- Modify: `icrack.py`

- [ ] **Step 1: Update imports — swap `print_banner` for `print_header`**

Change the import block from:
```python
from core.output import (
    print_banner,
    print_tool_header,
    print_line,
    print_tool_skipped,
    print_summary,
)
```
To:
```python
from core.output import (
    print_header,
    print_tool_header,
    print_line,
    print_tool_skipped,
    print_summary,
)
```

- [ ] **Step 2: Update `run_lookup` — use `print_header`, remove colored lookup line**

Replace:
```python
def run_lookup(lookup_type: str, query: str, module):
    print_banner()
    console.print(
        f"[bold]Lookup:[/bold] [cyan]{lookup_type.upper()}[/cyan]  [white]{query}[/white]\n"
    )
```
With:
```python
def run_lookup(lookup_type: str, query: str, module):
    print_header()
    console.print(f"  {lookup_type}  {query}\n")
```

- [ ] **Step 3: Update `check_tools` — use `print_header` and `box.SIMPLE_HEAD`, remove color from status cells**

Replace the entire `check_tools` function:
```python
def check_tools():
    print_header()
    table = Table(box=box.SIMPLE_HEAD, show_header=True, header_style="dim")
    table.add_column("Tool")
    table.add_column("Type")
    table.add_column("Status")
    table.add_column("Install hint")

    for tool, hint in CLI_TOOLS.items():
        found = shutil.which(tool) is not None
        status = "✓" if found else "✗"
        table.add_row(tool, "cli", status, hint if not found else "")

    for lib, hint in PYTHON_LIBS.items():
        try:
            __import__(lib)
            table.add_row(lib, "python", "✓", "")
        except ImportError:
            table.add_row(lib, "python", "✗", hint)

    console.print(table)
```

- [ ] **Step 4: Update `list_results` — use `print_header` and `box.SIMPLE_HEAD`**

Replace the entire `list_results` function:
```python
def list_results():
    print_header()
    files = (
        sorted(
            [f for f in os.listdir(RESULTS_DIR) if f.endswith(".json")],
            reverse=True,
        )
        if os.path.isdir(RESULTS_DIR)
        else []
    )

    if not files:
        console.print("[dim]  No saved results found.[/dim]")
        return

    table = Table(box=box.SIMPLE_HEAD, show_header=True, header_style="dim")
    table.add_column("#", justify="right")
    table.add_column("File")

    for i, name in enumerate(files, 1):
        table.add_row(str(i), name)

    console.print(table)
```

- [ ] **Step 5: Update `interactive_menu` — dim numbers, `>` prompt, plain heading**

Replace the entire `interactive_menu` function:
```python
def interactive_menu():
    print_header()
    options = [
        ("1", "Email lookup", "email"),
        ("2", "Username lookup", "username"),
        ("3", "Phone lookup", "phone"),
        ("4", "Name lookup", "name"),
        ("5", "Address lookup", "address"),
        ("6", "Check installed tools", None),
        ("7", "List saved results", None),
        ("0", "Exit", None),
    ]

    while True:
        console.print()
        for key, label, _ in options:
            console.print(f"  [dim]{key}[/dim]  {label}")

        choice = console.input("\n  [dim]>[/dim] ").strip()

        if choice == "0":
            console.print("[dim]  bye[/dim]")
            sys.exit(0)
        elif choice == "6":
            check_tools()
        elif choice == "7":
            list_results()
        else:
            mapping = {o[0]: (o[2], o[1]) for o in options if o[2]}
            if choice not in mapping:
                console.print("[dim]  invalid choice[/dim]")
                continue
            lookup_type, label = mapping[choice]
            query = console.input(f"  [dim]{label.lower()}[/dim]  > ").strip()
            if not query:
                console.print("[dim]  empty query[/dim]")
                continue
            module = {
                "email": mod_email,
                "username": mod_username,
                "phone": mod_phone,
                "name": mod_name,
                "address": mod_address,
            }[lookup_type]
            run_lookup(lookup_type, query, module)
```

- [ ] **Step 6: Run existing tests to confirm no regressions**

```bash
cd /home/deegan/iCrackU && source venv/bin/activate && python -m pytest tests/ -v
```

Expected: all 13 tests pass.

- [ ] **Step 7: Smoke test the CLI visually**

```bash
cd /home/deegan/iCrackU && source venv/bin/activate && python icrack.py --check
```

Expected output matches this shape (no colors except steel_blue on `iCrackU`):
```
  iCrackU  ·  OSINT Lookup Tool
  ────────────────────────────────

 Tool           Type      Status    Install hint
─────────────────────────────────────────────────
 holehe         cli       ✗         pip install holehe
 theHarvester   cli       ✓
 ...
 geopy          python    ✓
```

- [ ] **Step 8: Commit**

```bash
git -C /home/deegan/iCrackU add icrack.py
git -C /home/deegan/iCrackU commit -m "feat: update icrack.py to Claude Code style"
```
