# iCrackU UI Redesign — Claude Code Style

**Date:** 2026-04-21  
**Status:** Approved  
**Scope:** Visual reskin of `core/output.py` and `icrack.py` — no logic changes

---

## Goal

Replace the current colorful Rich UI (ASCII banner, cyan/yellow/green palette, rounded boxes) with a restrained, minimal aesthetic matching Claude Code's terminal style: one muted blue-gray accent, plain white body text, dim secondary text, simple horizontal rules, no line-by-line colorization.

---

## Section 1: Header / Banner

**Remove** the ASCII art banner (`BANNER` constant and `print_banner()`).

**Replace** with a two-line header function:

```
  iCrackU  ·  OSINT Lookup Tool
  ──────────────────────────────
```

- `iCrackU` rendered in `steel_blue` (Rich color name)
- `·  OSINT Lookup Tool` rendered in `dim`
- Second line: a plain `─` rule in `dim`, same width as the text above
- No other decorative characters

---

## Section 2: Tool Headers & Streaming Output

**Tool section headers** — replace `console.rule()` with yellow bold tool name:

```
── sherlock ────────────────────────────────────────
```

- Use `console.rule()` with `dim` style and the tool name inline (no color)

**Streaming output lines** — remove all colorization from `print_line()`:

- Every line prints as plain white text
- Remove the keyword-matching logic (found/not found/error coloring)
- `print_line(line)` becomes `console.print(line)`

**Skipped tools** — replace red `✗ {tool} not installed` with a single dim inline note:

```
  maigret  not installed
```

- Rendered entirely in `dim`, indented two spaces

---

## Section 3: Tables

**Replace** `box.ROUNDED` with `box.SIMPLE_HEAD` throughout.

- Column headers: `dim` style, no color
- No colored cells anywhere

**Check tools table** columns: Tool | Type | Status | Install hint

- Status values: `✓` (installed) or `✗` (missing) — plain white, no color markup

**Summary table** columns: Tool | Status | Lines

- Status values:
  - `✓` — returncode 0
  - `–` — returncode -1 (skipped / not installed)
  - `⏱` — returncode -2 (timeout)
  - `exit N` — any other non-zero returncode
- All status values rendered plain white, no color markup

---

## Section 4: Interactive Menu

**Replace** bold cyan heading and `[N]` bracket format:

```
  iCrackU  ·  OSINT Lookup Tool
  ──────────────────────────────

  1  Email lookup
  2  Username lookup
  3  Phone lookup
  4  Name lookup
  5  Address lookup
  6  Check installed tools
  7  List saved results
  0  Exit

  > 
```

- Option numbers rendered in `dim`
- Option labels plain white
- Prompt: `  > ` (two spaces, `>`, space) — no Rich markup
- Query prompts follow same pattern: `  email query  > `
- Separator between header and options: blank line only (the header rule serves as the visual anchor)

---

## Files Changed

| File | Change |
|---|---|
| `core/output.py` | Rewrite all print functions to new style |
| `icrack.py` | Update `interactive_menu()` prompts and menu rendering; update `list_results()` table style |

No changes to `core/runner.py`, `core/saver.py`, or any module file.

---

## Out of Scope

- Logic changes of any kind
- New features
- Changes to how results are saved
