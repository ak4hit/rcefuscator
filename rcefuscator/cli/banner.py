"""
cli/banner.py — Animated startup banner for rcefuscator.

Renders a large figlet ASCII-art title with a fire-coloured gradient,
revealed line-by-line with a short delay for a typewriter feel.
Falls back to a hardcoded banner if pyfiglet is unavailable.
"""

import time

from rich.console import Console
from rich.text import Text
from rich.align import Align

# ---------------------------------------------------------------------------
# ASCII art via pyfiglet (optional dep — graceful fallback if missing)
# ---------------------------------------------------------------------------

try:
    import pyfiglet
    _PYFIGLET_OK = True
except ImportError:
    _PYFIGLET_OK = False

_FONT = "doom"

# Hardcoded fallback (doom font, pre-rendered)
_FALLBACK = r"""
                      __                     _
 _ __ ___ ___ / _|_   _ ___  ___ __ _| |_ ___  _ __
| '__/ __/ _ \ |_| | | / __|/ __/ _` | __/ _ \| '__|
| | | (_|  __/  _| |_| \__ \ (_| (_| | || (_) | |
|_|  \___\___|_|  \__,_|___/\___\__,_|\__\___/|_|
"""

# ---------------------------------------------------------------------------
# Fire-colour palette  (dark red → orange → gold → bright yellow)
# ---------------------------------------------------------------------------

_FIRE: list[str] = [
    "#CC0000",
    "#DD1100",
    "#EE2200",
    "#FF3300",
    "#FF5500",
    "#FF7700",
    "#FF9900",
    "#FFBB00",
    "#FFDD00",
    "#FFEE11",
    "#FFFF33",
]


def _get_lines() -> list[str]:
    """Return the banner as a list of raw text lines."""
    if _PYFIGLET_OK:
        art = pyfiglet.figlet_format("rcefuscator", font=_FONT)
    else:
        art = _FALLBACK
    # Keep all lines (including blank ones) so spacing is preserved
    return art.split("\n")


def print_banner(console: Console, delay: float = 0.035) -> None:
    """
    Print the animated rcefuscator banner to *console*.

    Each line of the ASCII art is revealed after *delay* seconds,
    coloured with a top-to-bottom fire gradient.
    A small attribution line follows the art.
    """
    lines = _get_lines()

    # Strip leading/trailing blank lines for centering, but keep internal ones
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()

    # How many non-blank lines are there? We spread the palette over those.
    non_blank = [l for l in lines if l.strip()]
    n_colours = len(_FIRE)
    colour_step = max(1, len(non_blank) // n_colours)

    colour_idx = 0
    blank_run  = 0

    console.print()

    for line in lines:
        if line.strip():
            blank_run = 0
            col = _FIRE[min(colour_idx // colour_step, n_colours - 1)]
            colour_idx += 1
            console.print(Align(Text(line, style=f"bold {col}"), align="center"))
            time.sleep(delay)
        else:
            # Never print more than one consecutive blank line
            if blank_run == 0:
                console.print()
            blank_run += 1

    # -----------------------------------------------------------------------
    # Attribution tagline  — small, dim, centered
    # -----------------------------------------------------------------------
    console.print()
    console.print(
        Align(
            Text(
                "RCE Payload Generator & WAF Evasion Toolkit",
                style="dim white",
            ),
            align="center",
        )
    )
    console.print(
        Align(
            Text("— ak4hit", style="dim italic #888888"),
            align="center",
        )
    )
    console.print()
