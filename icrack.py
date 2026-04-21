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
import modules.ip as mod_ip
import modules.domain as mod_domain
import modules.breach as mod_breach
import modules.hash as mod_hash

console = Console()

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")

CLI_TOOLS = {
    "holehe": "pip install holehe",
    "theHarvester": "pip install theHarvester",
    "ghunt": "pip install ghunt",
    "sherlock": "pip install sherlock-project",
    "maigret": "pip install maigret",
    "phoneinfoga": "https://github.com/sundowndev/phoneinfoga",
    "whois": "apt install whois",
    "subfinder": "go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest",
    "hashid": "pip install hashid",
}

PYTHON_LIBS = {
    "geopy": "pip install geopy",
    "requests": "pip install requests",
    "dns": "pip install dnspython",
    "whois": "pip install python-whois",
    "shodan": "pip install shodan",
}


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


def run_target_profile(inputs: dict[str, str]):
    from core.profiler import build_targets_from_input, run_profile, save_profile
    from core.output import print_profile_summary

    print_header()
    label = "  ·  ".join(v for v in inputs.values() if v)
    console.print(f"  [dim]target profile[/dim]  [bold]{label}[/bold]\n")

    targets = build_targets_from_input(inputs)
    profile_results = run_profile(
        targets,
        on_line=print_line,
        on_tool_start=print_tool_header,
    )

    os.makedirs(RESULTS_DIR, exist_ok=True)
    json_path = save_profile(profile_results, results_dir=RESULTS_DIR)
    print_profile_summary(inputs, profile_results, json_path)


def check_tools():
    print_header()
    table = Table(
        box=box.SIMPLE_HEAVY,
        show_header=True,
        header_style="bold",
        show_edge=False,
        pad_edge=True,
    )
    table.add_column("Tool")
    table.add_column("Type")
    table.add_column("Status")
    table.add_column("Install hint", style="dim")

    for tool, hint in CLI_TOOLS.items():
        found = shutil.which(tool) is not None
        status = "[green]✓[/green]" if found else "[red]✗[/red]"
        table.add_row(tool, "cli", status, hint if not found else "")

    for lib, hint in PYTHON_LIBS.items():
        try:
            __import__(lib)
            table.add_row(lib, "python", "[green]✓[/green]", "")
        except ImportError:
            table.add_row(lib, "python", "[red]✗[/red]", hint)

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
        console.print("  [dim]No saved results found.[/dim]")
        return

    table = Table(
        box=box.SIMPLE_HEAVY,
        show_header=True,
        header_style="bold",
        show_edge=False,
        pad_edge=True,
    )
    table.add_column("#", justify="right", style="dim")
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
        ("6", "IP lookup", "ip"),
        ("7", "Domain lookup", "domain"),
        ("8", "Breach check", "breach"),
        ("9", "Hash lookup", "hash"),
        ("P", "Target profile", None),
        ("R", "Generate report", None),
        ("10", "Check installed tools", None),
        ("11", "List saved results", None),
        ("0", "Exit", None),
    ]

    mapping = {o[0]: (o[2], o[1]) for o in options if o[2]}

    while True:
        console.print()
        for key, label, _ in options:
            console.print(f"  [bright_green]{key}[/bright_green]  {label}")

        console.print()
        console.rule(style="dim")
        choice = console.input("  [bright_green]>[/bright_green] ").strip()

        if choice == "0":
            console.print("[dim]  bye[/dim]")
            sys.exit(0)
        elif choice == "10":
            check_tools()
        elif choice == "11":
            list_results()
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
            fmt = (
                console.input("  [dim]format (html/md/both)[/dim]  > ").strip()
                or "html"
            )
            generate_report(os.path.join(RESULTS_DIR, chosen), fmt=fmt)
        elif choice in ("p", "P"):
            inputs = {}
            fields = ["name", "email", "username", "phone", "ip", "domain"]
            for field in fields:
                val = console.input(f"  [dim]{field:<10}[/dim]  > ").strip()
                if val:
                    inputs[field] = val
            if not inputs:
                console.print("[dim]  no input provided[/dim]")
            else:
                run_target_profile(inputs)
        else:
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
                "ip": mod_ip,
                "domain": mod_domain,
                "breach": mod_breach,
                "hash": mod_hash,
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
    parser.add_argument("--ip", metavar="IP", help="IP address lookup")
    parser.add_argument("--domain", metavar="DOMAIN", help="Domain/WHOIS lookup")
    parser.add_argument(
        "--breach", metavar="EMAIL", help="Breach check (HaveIBeenPwned)"
    )
    parser.add_argument("--hash", metavar="HASH", help="Hash identification and lookup")
    parser.add_argument("--check", action="store_true", help="Show installed tools")
    parser.add_argument("--list", action="store_true", help="List saved results")
    parser.add_argument(
        "--target", metavar="TARGET", help="Auto-detect and run all relevant lookups"
    )
    parser.add_argument(
        "--report", metavar="JSON_FILE", help="Generate report from saved result JSON"
    )
    parser.add_argument(
        "--save-report",
        action="store_true",
        help="Generate report after lookup completes",
    )
    parser.add_argument(
        "--format",
        metavar="FORMAT",
        default="html",
        help="Report format: html (default), md, or both",
    )

    args = parser.parse_args()

    report_fmt = args.format if args.save_report else None

    if args.check:
        check_tools()
    elif args.list:
        list_results()
    elif args.report:
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


if __name__ == "__main__":
    main()
