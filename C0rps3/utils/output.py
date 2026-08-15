"""Cross-platform ANSI color + REPL output helpers.

Uses colorama so colors work on Windows (which doesn't natively support ANSI
in the legacy console). Provides:
  - print_section(title)   — bold header line
  - print_kv(label, value) — key/value pair
  - print_table(rows, headers) — fixed-width table
  - print_error(msg) / print_warning(msg) / print_success(msg)
  - need(value, name) — returns value or prints a "missing key" message and returns None
"""
from __future__ import annotations

from typing import Iterable, Sequence

try:
    from colorama import init as _colorama_init
    _colorama_init(autoreset=False)
except Exception:  # pragma: no cover - colorama always available per requirements
    pass

try:
    from colorama import Fore, Style
except Exception:  # pragma: no cover
    class Fore:  # type: ignore[no-redef]
        RED = ""
        GREEN = ""
        YELLOW = ""
        CYAN = ""
        MAGENTA = ""
        WHITE = ""
        RESET = ""
    class Style:  # type: ignore[no-redef]
        BRIGHT = ""
        RESET_ALL = ""

RED = Fore.RED
GREEN = Fore.GREEN
YELLOW = Fore.YELLOW
CYAN = Fore.CYAN
MAGENTA = Fore.MAGENTA
RESET = Style.RESET_ALL
BOLD = Style.BRIGHT


def print_section(title: str) -> None:
    """Print a bold cyan header."""
    print(f"\n{BOLD}{CYAN}== {title} =={RESET}")


def print_kv(label: str, value: object) -> None:
    """Print a single key: value pair, left-aligned label."""
    print(f"  {BOLD}{label:<16}{RESET} {value}")


def print_table(rows: Iterable[Sequence[object]], headers: Sequence[str]) -> None:
    """Print a simple space-aligned table. Truncates long cells."""
    rows = list(rows)
    if not rows:
        print("  (no results)")
        return
    cols = len(headers)
    widths = [len(str(h)) for h in headers]
    for row in rows:
        for i in range(cols):
            cell = str(row[i]) if i < len(row) else ""
            if len(cell) > 40:
                cell = cell[:37] + "..."
            widths[i] = max(widths[i], len(cell))
    header_line = "  ".join(str(h).ljust(widths[i]) for i, h in enumerate(headers))
    sep_line = "  ".join("-" * widths[i] for i in range(cols))
    print(BOLD + header_line + RESET)
    print(sep_line)
    for row in rows:
        line_cells = []
        for i in range(cols):
            cell = str(row[i]) if i < len(row) else ""
            if len(cell) > 40:
                cell = cell[:37] + "..."
            line_cells.append(cell.ljust(widths[i]))
        print("  ".join(line_cells))


def print_error(msg: str) -> None:
    print(f"{RED}[!]{RESET} {msg}")


def print_warning(msg: str) -> None:
    print(f"{YELLOW}[~]{RESET} {msg}")


def print_success(msg: str) -> None:
    print(f"{GREEN}[+]{RESET} {msg}")


def need(value, name: str):
    """Return value if truthy; otherwise print a 'missing key/setup' hint and return None."""
    if value:
        return value
    print_error(f"Missing {name}. Set it in your .env file (see .env.example).")
    return None
