"""
output/formatter.py -- Rich terminal output formatter for rcefuscator.
"""

import sys
import io
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box

# Force UTF-8 output on Windows so box-drawing chars don't crash cp1252
_stdout_utf8 = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
console = Console(file=_stdout_utf8, highlight=False)


def format_payloads(results: list, blacklist: list, show_skipped: bool = False) -> None:
    """
    Print all generated payloads to the terminal using Rich panels.

    Green panel  = payload passes blacklist check (clean)
    Red panel    = payload uses blacklisted chars (unsafe for this WAF profile)
    Dim line     = technique was skipped
    """
    clean_count = sum(1 for r in results if not r["skipped"] and r["clean"])
    total_run   = sum(1 for r in results if not r["skipped"])

    console.print()
    console.rule("[bold cyan]rcefuscator[/bold cyan] -- WAF Evasion Payloads", style="cyan")
    console.print()

    idx = 0
    for r in results:
        if r["skipped"]:
            if show_skipped:
                console.print(
                    f"  [dim][SKIP] [{r['id']}] {r['name']} -- {r['skip_reason']}[/dim]"
                )
            continue

        idx += 1
        is_clean = r["clean"]

        # Build panel content
        payload_text = Text(r["payload"], style="bold white")

        meta_parts = []
        if r["uses_chars"]:
            chars_str = " ".join(r["uses_chars"])
            meta_parts.append(f"Uses chars: [yellow]{chars_str}[/yellow]")
        else:
            meta_parts.append("Uses chars: [green]none[/green]")
        meta_parts.append(f"Shell: [cyan]{r['shell']}[/cyan]")

        body = Text.assemble(
            payload_text,
            "\n\n",
            Text.from_markup("  ".join(meta_parts)),
        )

        status_label = "[CLEAN]" if is_clean else "[FLAGGED - contains blacklisted chars]"
        status_style = "green" if is_clean else "red"
        border_style = "green" if is_clean else "red"

        title = (
            f"[bold]{idx}. {r['name']}[/bold]   "
            f"[{status_style}]{status_label}[/{status_style}]"
        )

        console.print(
            Panel(
                body,
                title=title,
                border_style=border_style,
                box=box.ROUNDED,
                padding=(1, 2),
            )
        )

    console.print()
    console.rule(style="dim")
    console.print(
        f"\n  [bold]Generated [cyan]{total_run}[/cyan] payloads.[/bold]  "
        f"[green]{clean_count} clean[/green] for your WAF profile.  "
        f"[red]{total_run - clean_count} flagged[/red].\n"
    )


def format_techniques_table(techniques: list) -> None:
    """Print a rich table listing all registered techniques."""
    table = Table(
        title="[bold cyan]rcefuscator -- Available Techniques[/bold cyan]",
        box=box.ROUNDED,
        border_style="cyan",
        show_lines=True,
    )
    table.add_column("#",          style="dim", width=3)
    table.add_column("ID",         style="bold yellow")
    table.add_column("Name",       style="bold white")
    table.add_column("Uses Chars", style="red")
    table.add_column("Shell",      style="cyan")
    table.add_column("Description")

    for i, t in enumerate(techniques, start=1):
        chars = " ".join(t["uses_chars"]) if t["uses_chars"] else "[green]none[/green]"
        table.add_row(
            str(i),
            t["id"],
            t["name"],
            chars,
            t["shell"],
            t["description"],
        )

    console.print()
    console.print(table)
    console.print()
