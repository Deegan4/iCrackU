from rich.console import Console
from rich import box
from rich.table import Table

console = Console()

HEADER_WIDTH = 32


def print_header():
    console.print(
        f"[steel_blue]  iCrackU[/steel_blue][dim]  ·  OSINT Lookup Tool[/dim]"
    )
    console.print(f"[dim]  {'─' * HEADER_WIDTH}[/dim]")


def print_tool_header(tool_name: str):
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
    _label = "  saved  "
    console.print(f"[dim]{_label}[/dim]{txt_path}")
    console.print(f"[dim]{' ' * len(_label)}[/dim]{json_path}")
