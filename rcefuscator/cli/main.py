"""
cli/main.py -- Click-based CLI entrypoint for rcefuscator.

Usage examples:
  rcefuscator --cmd "id"
  rcefuscator --cmd "id" --profile strict
  rcefuscator --cmd "whoami" --blacklist "; | & `"
  rcefuscator --cmd "id" --json
  rcefuscator --cmd "id" --output payloads.txt
  rcefuscator --cmd "id" --technique base64
  rcefuscator --list-techniques
  rcefuscator --cmd "id" --copy
"""

import sys
import io
from pathlib import Path

import click
from rich.console import Console
from rich.prompt import Confirm

# On Windows, the legacy console renderer can't handle box-drawing/unicode
# characters. Wrapping stdout in UTF-8 fixes this for real terminals.
# We skip the wrap under Click's CliRunner (no .buffer attribute).
def _make_console() -> "Console":
    if hasattr(sys.stdout, "buffer"):
        out = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        return Console(file=out, highlight=False)
    return Console(highlight=False)

console = _make_console()



# Path where one-time disclaimer acknowledgment is stored
ACK_FILE = Path.home() / ".rcefuscator_ack"

DISCLAIMER_TEXT = """
[bold yellow]*** DISCLAIMER ***[/bold yellow]

[bold]rcefuscator[/bold] is for [bold green]authorized penetration testing, CTF challenges, and educational research ONLY.[/bold green]

Using this tool against systems you do not own or have explicit written
permission to test is [bold red]ILLEGAL[/bold red] and may result in criminal prosecution.

The author bears no responsibility for any misuse.
"""


def _check_disclaimer() -> None:
    """Display disclaimer and require one-time acknowledgment. Stored in ~/.rcefuscator_ack."""
    if ACK_FILE.exists():
        return  # Already acknowledged

    console.print(DISCLAIMER_TEXT)
    try:
        confirmed = Confirm.ask(
            "[bold]I confirm this tool will only be used on systems I own "
            "or have written permission to test[/bold]",
            default=False,
        )
    except (KeyboardInterrupt, EOFError):
        console.print("\n[red]Aborted.[/red]")
        sys.exit(1)

    if not confirmed:
        console.print("[red]You must accept the disclaimer to use rcefuscator. Exiting.[/red]")
        sys.exit(1)

    ACK_FILE.write_text("acknowledged", encoding="utf-8")
    console.print("[green][OK] Disclaimer acknowledged. Stored in ~/.rcefuscator_ack.[/green]\n")


def _resolve_blacklist(profile: str, blacklist_str) -> tuple:
    """Return (blacklist, active_profile_name) given CLI flags."""
    from rcefuscator.core.techniques import WAF_PROFILES

    if blacklist_str:
        # Split on whitespace or commas
        chars = [c.strip() for c in blacklist_str.replace(",", " ").split() if c.strip()]
        return chars, "custom"

    if profile not in WAF_PROFILES:
        raise click.BadParameter(
            f"Unknown profile '{profile}'. Choose from: {', '.join(WAF_PROFILES.keys())}",
            param_hint="--profile",
        )

    return WAF_PROFILES[profile], profile


# ---------------------------------------------------------------------------
# Main CLI command
# ---------------------------------------------------------------------------

@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--cmd",         "-c", default=None,   help="OS command to obfuscate (e.g. 'id')")
@click.option("--profile",     "-p", default="moderate",
              help="WAF profile preset: moderate | strict | paranoid  [default: moderate]")
@click.option("--blacklist",   "-b", default=None,
              help="Custom blacklist chars (overrides --profile). Space or comma separated.")
@click.option("--technique",   "-t", default=None,
              help="Run a single technique by ID (see --list-techniques)")
@click.option("--list-techniques", "-l", is_flag=True, default=False,
              help="List all available techniques and exit")
@click.option("--json",        "-j", "output_json", is_flag=True, default=False,
              help="Print output as JSON instead of rich terminal format")
@click.option("--output",      "-o", default=None,
              help="Save payloads to a plain-text file")
@click.option("--copy",        is_flag=True, default=False,
              help="Copy the first clean payload to clipboard")
@click.option("--show-skipped", is_flag=True, default=False,
              help="Show skipped techniques in the output")
@click.version_option("1.0.0", prog_name="rcefuscator")
def cli(cmd, profile, blacklist, technique, list_techniques, output_json, output, copy, show_skipped):
    """
    \b
    rcefuscator -- RCE Payload Generator & WAF Evasion Toolkit
    Educational use only. See DISCLAIMER.md.
    """
    from rcefuscator.cli.banner import print_banner
    from rcefuscator.core.techniques import (
        TECHNIQUES, run_all_techniques, get_technique_by_id,
    )
    from rcefuscator.output.formatter import format_payloads, format_techniques_table
    from rcefuscator.output.exporter import export_json, export_to_file

    # Animated banner — always shown at startup
    print_banner(console)

    # Always check disclaimer first
    _check_disclaimer()

    # --list-techniques: print table and exit
    if list_techniques:
        format_techniques_table(TECHNIQUES, console=console)
        return

    # --cmd is required for everything else
    if not cmd:
        click.echo(click.get_current_context().get_help())
        return

    # Resolve blacklist
    try:
        active_blacklist, active_profile = _resolve_blacklist(profile, blacklist)
    except click.BadParameter as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)

    # Announce what we're running
    blocked_str = " ".join(active_blacklist) if active_blacklist else "none"
    console.print(
        f"\n  [dim]Command:[/dim] [bold cyan]{cmd}[/bold cyan]   "
        f"[dim]Profile:[/dim] [bold]{active_profile}[/bold]   "
        f"[dim]Blocked:[/dim] [yellow]{blocked_str}[/yellow]"
    )

    # Run techniques
    if technique:
        t = get_technique_by_id(technique)
        if not t:
            ids = ", ".join(x["id"] for x in TECHNIQUES)
            console.print(f"[red]Unknown technique '{technique}'. Available: {ids}[/red]")
            sys.exit(1)
        from rcefuscator.core.techniques import run_technique
        results = [run_technique(t, cmd, active_blacklist)]
    else:
        results = run_all_techniques(cmd, active_blacklist)

    # JSON output mode
    if output_json:
        print(export_json(results, cmd, active_profile))
        return

    # Rich terminal output
    format_payloads(results, active_blacklist, show_skipped=show_skipped, console=console)

    # --output: save to file
    if output:
        n = export_to_file(results, cmd, active_profile, output)
        console.print(f"  [green][OK] Saved {n} payloads to[/green] [bold]{output}[/bold]\n")

    # --copy: copy first clean payload to clipboard
    if copy:
        clean_results = [r for r in results if not r["skipped"] and r["clean"]]
        if clean_results:
            _copy_to_clipboard(clean_results[0]["payload"])
        else:
            console.print("  [yellow][!] No clean payloads to copy.[/yellow]\n")


def _copy_to_clipboard(text: str) -> None:
    """Copy text to clipboard, gracefully degrade if pyperclip/backend unavailable."""
    try:
        import pyperclip
        pyperclip.copy(text)
        console.print(f"  [green][OK] Copied to clipboard:[/green] [bold]{text}[/bold]\n")
    except Exception:
        console.print(
            "  [yellow][!] Clipboard unavailable.[/yellow] "
            "Install xclip: [bold]sudo apt install xclip[/bold]\n"
        )


if __name__ == "__main__":
    cli()
