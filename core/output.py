from rich.console import Console
from rich import box
from rich.table import Table

console = Console()

BANNER = r"""
 ██╗ ██████╗██████╗  █████╗  ██████╗██╗  ██╗██╗   ██╗
 ██║██╔════╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██║   ██║
 ██║██║     ██████╔╝███████║██║     █████╔╝ ██║   ██║
 ██║██║     ██╔══██╗██╔══██║██║     ██╔═██╗ ██║   ██║
 ██║╚██████╗██║  ██║██║  ██║╚██████╗██║  ██╗╚██████╔╝
 ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝"""


def print_header():
    console.print(f"[bright_green]{BANNER}[/bright_green]")
    console.print(
        "  [dim green][ OSINT FRAMEWORK ][/dim green]"
        "  [dim]·[/dim]"
        "  [dim green]KALI LINUX[/dim green]"
        "  [dim]·[/dim]"
        "  [dim green]ROOT@LOCALHOST[/dim green]"
    )
    console.print()
    console.rule(style="bright_green")
    console.print()


def print_tool_header(tool_name: str):
    console.rule(f"[bright_green]{tool_name}[/bright_green]", style="green")


def print_line(line: str):
    console.print(f"  {line}")


def print_tool_skipped(tool_name: str):
    console.print(f"  [dim]{tool_name}  not installed[/dim]")


def _make_table(*columns: str, **kwargs) -> Table:
    table = Table(
        box=box.SIMPLE_HEAVY,
        show_header=True,
        header_style="bold",
        show_edge=False,
        pad_edge=True,
        **kwargs,
    )
    for col in columns:
        table.add_column(col)
    return table


def print_summary(tool_results: list[dict], txt_path: str, json_path: str):
    console.print()
    console.rule("[dim]summary[/dim]", style="dim")
    console.print()

    table = _make_table("Tool", "Status", "Lines")
    for r in tool_results:
        if r["returncode"] == -1:
            status = "[dim]–[/dim]"
        elif r["returncode"] == -2:
            status = "[yellow]⏱[/yellow]"
        elif r["returncode"] == 0:
            status = "[green]✓[/green]"
        else:
            status = f"[dim]exit {r['returncode']}[/dim]"
        lines = str(len(r["output"].splitlines()))
        table.add_row(r["tool"], status, lines)

    console.print(table)
    console.print()
    _label = "saved"
    console.print(f"  [dim]{_label}[/dim]  {txt_path}")
    console.print(f"  [dim]      [/dim]  {json_path}")
    console.print()


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
