from rich.console import Console
from rich.table import Table
from rich import box

console = Console()

BANNER = r"""
 _  _____                _    _   _
(_)/  __ \              | |  | | | |
 _ | /  \/_ __ __ _  ___| | _| | | |
| || |   | '__/ _` |/ __| |/ / | | |
| || \__/\ | | (_| | (__|   <| |_| |
|_| \____/_|  \__,_|\___|_|\_\\___/
"""

def print_banner():
    console.print(f"[bold cyan]{BANNER}[/bold cyan]")
    console.print("[dim]  OSINT Lookup Tool — Kali Linux[/dim]\n")

def print_tool_header(tool_name: str, query: str):
    console.rule(f"[bold yellow]{tool_name}[/bold yellow]  [dim]{query}[/dim]")

def print_line(line: str):
    lower = line.lower()
    if any(w in lower for w in ["found", "yes", "true", "registered", "+"]):
        console.print(f"[green]{line}[/green]")
    elif any(w in lower for w in ["not found", "no ", "false", "[-]", "error"]):
        console.print(f"[yellow]{line}[/yellow]")
    else:
        console.print(line)

def print_tool_skipped(tool_name: str):
    console.print(f"[red]  ✗ {tool_name} not installed — skipping[/red]")

def print_summary(tool_results: list[dict], txt_path: str, json_path: str):
    console.print()
    table = Table(title="Summary", box=box.ROUNDED)
    table.add_column("Tool", style="cyan")
    table.add_column("Status")
    table.add_column("Lines")

    for r in tool_results:
        if r["returncode"] == -1:
            status = "[red]skipped[/red]"
        elif r["returncode"] == 0:
            status = "[green]ok[/green]"
        else:
            status = f"[yellow]exit {r['returncode']}[/yellow]"
        lines = str(len(r["output"].splitlines()))
        table.add_row(r["tool"], status, lines)

    console.print(table)
    console.print(f"\n[dim]Saved:[/dim] [cyan]{txt_path}[/cyan]")
    console.print(f"[dim]       [/dim] [cyan]{json_path}[/cyan]")
