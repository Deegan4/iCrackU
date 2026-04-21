#!/usr/bin/env python3
import argparse
import os
import sys
import shutil

from rich.console import Console
from rich.table import Table
from rich import box

from core.output import (
    print_header,
    print_tool_header,
    print_line,
    print_tool_skipped,
    print_summary,
)
from core.saver import save_results
import modules.email as mod_email
import modules.username as mod_username
import modules.phone as mod_phone
import modules.name as mod_name
import modules.address as mod_address

console = Console()

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")

CLI_TOOLS = {
    "holehe": "pip install holehe",
    "theHarvester": "pip install theHarvester",
    "ghunt": "pip install ghunt",
    "sherlock": "pip install sherlock-project",
    "maigret": "pip install maigret",
    "phoneinfoga": "https://github.com/sundowndev/phoneinfoga",
}

PYTHON_LIBS = {
    "geopy": "pip install geopy",
}


def run_lookup(lookup_type: str, query: str, module):
    print_header()
    console.print(f"  {lookup_type}  {query}\n")

    def on_line(line):
        print_line(line)

    def on_tool_start(tool_name):
        print_tool_header(tool_name)

    tool_results = module.lookup(query, on_line=on_line, on_tool_start=on_tool_start)

    txt_path, json_path = save_results(
        lookup_type=lookup_type,
        query=query,
        tool_results=tool_results,
        results_dir=RESULTS_DIR,
    )
    print_summary(tool_results, txt_path, json_path)


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


def main():
    parser = argparse.ArgumentParser(
        prog="iCrackU",
        description="Terminal OSINT lookup tool",
    )
    parser.add_argument("--email", metavar="EMAIL", help="Email lookup")
    parser.add_argument("--username", metavar="USERNAME", help="Username lookup")
    parser.add_argument("--phone", metavar="PHONE", help="Phone number lookup")
    parser.add_argument("--name", metavar="NAME", help="Person name lookup")
    parser.add_argument("--address", metavar="ADDRESS", help="Address lookup")
    parser.add_argument("--check", action="store_true", help="Show installed tools")
    parser.add_argument("--list", action="store_true", help="List saved results")

    args = parser.parse_args()

    if args.check:
        check_tools()
    elif args.list:
        list_results()
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
