#!/usr/bin/env python3
import argparse
import os
import sys
import shutil

from rich.console import Console
from rich.table import Table
from rich import box

from core.output import print_banner, print_tool_header, print_line, print_tool_skipped, print_summary
from core.saver import save_results
import modules.email as mod_email
import modules.username as mod_username
import modules.phone as mod_phone
import modules.name as mod_name
import modules.address as mod_address

console = Console()

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")

ALL_TOOLS = {
    "holehe":          "pip install holehe",
    "theHarvester":    "pip install theHarvester",
    "ghunt":           "pip install ghunt",
    "sherlock":        "pip install sherlock-project",
    "maigret":         "pip install maigret",
    "social-analyzer": "pip install social-analyzer",
    "phoneinfoga":     "https://github.com/sundowndev/phoneinfoga",
}

def run_lookup(lookup_type: str, query: str, module):
    print_banner()
    console.print(f"[bold]Lookup:[/bold] [cyan]{lookup_type.upper()}[/cyan]  [white]{query}[/white]\n")

    def on_line(line):
        print_line(line)

    def on_tool_start(tool_name):
        print_tool_header(tool_name, query)

    tool_results = module.lookup(query, on_line=on_line, on_tool_start=on_tool_start)

    txt_path, json_path = save_results(
        lookup_type=lookup_type,
        query=query,
        tool_results=tool_results,
        results_dir=RESULTS_DIR,
    )
    print_summary(tool_results, txt_path, json_path)

def check_tools():
    print_banner()
    table = Table(title="Tool Availability", box=box.ROUNDED)
    table.add_column("Tool", style="cyan")
    table.add_column("Status")
    table.add_column("Install hint", style="dim")

    for tool, hint in ALL_TOOLS.items():
        found = shutil.which(tool) is not None
        status = "[green]✓ installed[/green]" if found else "[red]✗ missing[/red]"
        table.add_row(tool, status, hint if not found else "")

    console.print(table)

def interactive_menu():
    print_banner()
    options = [
        ("1", "Email lookup",    "email"),
        ("2", "Username lookup", "username"),
        ("3", "Phone lookup",    "phone"),
        ("4", "Name lookup",     "name"),
        ("5", "Address lookup",  "address"),
        ("6", "Check installed tools", None),
        ("0", "Exit", None),
    ]

    while True:
        console.print("\n[bold cyan]  iCrackU — OSINT Lookup Tool[/bold cyan]")
        console.print("  " + "─" * 29)
        for key, label, _ in options:
            console.print(f"  [[bold]{key}[/bold]] {label}")

        choice = console.input("\n[bold]Select:[/bold] ").strip()

        if choice == "0":
            console.print("[dim]Bye.[/dim]")
            sys.exit(0)
        elif choice == "6":
            check_tools()
        else:
            mapping = {o[0]: (o[2], o[1]) for o in options if o[2]}
            if choice not in mapping:
                console.print("[red]Invalid choice.[/red]")
                continue
            lookup_type, label = mapping[choice]
            query = console.input(f"[bold]{label} query:[/bold] ").strip()
            if not query:
                console.print("[red]Empty query.[/red]")
                continue
            module = {
                "email":    mod_email,
                "username": mod_username,
                "phone":    mod_phone,
                "name":     mod_name,
                "address":  mod_address,
            }[lookup_type]
            run_lookup(lookup_type, query, module)

def main():
    parser = argparse.ArgumentParser(
        prog="iCrackU",
        description="Terminal OSINT lookup tool",
    )
    parser.add_argument("--email",    metavar="EMAIL",    help="Email lookup")
    parser.add_argument("--username", metavar="USERNAME", help="Username lookup")
    parser.add_argument("--phone",    metavar="PHONE",    help="Phone number lookup")
    parser.add_argument("--name",     metavar="NAME",     help="Person name lookup")
    parser.add_argument("--address",  metavar="ADDRESS",  help="Address lookup")
    parser.add_argument("--check",    action="store_true", help="Show installed tools")

    args = parser.parse_args()

    if args.check:
        check_tools()
    elif args.email:
        run_lookup("email", args.email, mod_email)
    elif args.username:
        run_lookup("username", args.username, mod_username)
    elif args.phone:
        run_lookup("phone", args.phone, mod_phone)
    elif args.name:
        run_lookup("name", args.name, mod_name)
    elif args.address:
        run_lookup("address", args.address, mod_address)
    else:
        interactive_menu()

if __name__ == "__main__":
    main()
