"""C0rps3 — The Intelligence Tool

Interactive OSINT REPL. Type a command and hit Enter. 'help' lists commands.

Run with:
    python main.py
"""
from __future__ import annotations

import os
import shlex
import sys

# Force UTF-8 on Windows consoles so the Unicode skull banner renders.
# On non-Windows this is a no-op.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
except Exception:
    pass

from utils.output import (
    RED, RESET, BOLD, GREEN,
    print_section, print_kv, print_error, print_warning,
)


# ---------------------------------------------------------------------------
# Banner
# ---------------------------------------------------------------------------

ASCII_BANNER = """\
  | | | | |       | | | | |     | | | | |     | | | | |     / | | | | | |    | | | | }
| |         |   | |       | |   | |     | |   | |     | |   | |              | |
| |             | |       | |   | | | |       | | | | |     | | | | | | |    | | | | /
| |         |   | |       | |   | |   | |     | |                     | |    | |
  | | | | |       | | | | |     | |     | |   | |           | | | | | | /    | | | | }
"""

ascii_art = """\
⠀⢀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⡀⢄⢮⡳⣶⢭⣖⣢⡤⢀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢀⢤⣢⣵⣾⣾⣿⣿⣿⣹⣿⣿⣿⣿⣶⣯⣵⣒⡠⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢸⣎⣿⣿⣿⣿⣿⡿⠛⠛⠻⣿⣿⣿⣿⣿⣿⡇⣿⣟⣵⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢸⡇⠼⣿⣿⣿⡟⠀⢠⣤⢸⡊⢻⣿⡿⣿⣿⡇⣿⣿⣷⣝⣕⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢸⡇⢑⢻⣿⣿⣧⡀⣅⡡⣠⠆⠹⣿⣿⣿⣿⣷⣿⣿⣿⣿⣷⢟⢯⠢⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢸⡇⣸⢉⢿⣯⣿⣿⣶⣧⣤⣰⣾⣿⡟⠽⣋⣈⢿⣿⣿⣿⣿⢸⣷⣝⠮⡢⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢸⣷⣿⠠⣞⢿⣿⣿⣿⣿⢟⡫⡗⡢⡑⢭⣗⡺⢷⣙⠿⣿⣿⣼⣿⢿⣷⣍⣎⡢⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢸⣿⣿⣼⡏⠗⢝⢿⣿⡈⢥⣿⠞⡜⡼⣾⣛⢿⣛⣻⣷⣰⠹⣻⣿⣿⣿⣿⣿⣮⡪⡢⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⣸⣿⣿⣾⡇⠄⠁⠋⣊⢟⠬⡻⣯⡵⣣⡻⣟⡦⢾⣿⣋⣇⢉⣿⣿⣿⣿⣿⣿⣿⣿⣿⡪⡢⡀⠀⠀⠀⠀⠀⠀⠀
⠠⠰⣹⢔⠹⣿⣿⣫⠁⠀⢰⡌⢿⡎⢜⠝⡿⣟⡫⢗⡫⠏⠙⢫⣵⠘⣄⡘⠿⣿⣿⣿⣿⣿⣿⣿⣾⣮⡢⡀⠀⠀⠀⠀⠀
⠀⠀⠀⠄⡚⠘⢿⣯⡅⠀⢸⠇⠄⠀⠀⠉⠲⠔⡱⡻⢿⣽⣁⠢⢼⣶⣿⣿⣷⣬⡉⡹⠿⣿⣿⣿⣿⣿⣯⡪⡢⡀⠀⠀⠀
⠀⠀⠠⠀⢀⠄⠎⢿⣷⠀⢸⠇⡄⡆⡌⠁⡂⠀⡘⢠⠱⠨⢛⢿⣶⣬⡉⡹⠻⣿⣷⣢⣄⠙⢿⣿⣿⣿⣿⡿⠞⢞⡆⠀⠀
⠀⠀⠀⠀⠈⠈⠒⠊⡻⡇⡄⡒⠤⡀⠁⠃⠁⢠⢀⠁⠀⠀⠂⢉⢊⠝⠿⣶⡤⡘⢿⣿⣷⣝⢦⣙⠿⡛⣉⣼⣾⣿⡇⠀⠀
⠀⠀⠀⠀⠀⠘⠠⢬⠐⠱⠺⢵⡣⢆⡅⢆⡎⠘⠈⠘⢰⠰⠀⠃⠎⡔⠸⢐⠹⢻⢵⡩⣛⢟⢋⣡⣵⣿⡟⢹⢿⣿⡇⠀⠀
⠀⠀⠀⠀⠀⠀⠂⠄⡈⢀⠀⠑⢉⢓⠾⡥⢨⠐⡠⣀⠂⠆⡄⡄⡀⠐⢀⠀⡌⡖⢌⠪⣤⢾⣿⣿⣿⣏⣍⢰⣿⢿⡇⢤⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠋⠐⠁⠀⠈⠐⠱⠁⢊⢅⡃⠉⢒⠤⡁⠃⠦⢌⠘⠀⠁⠀⠂⣿⣿⣿⣿⣿⣿⣧⣸⣾⣿⡇⢠⠰
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂⠄⠄⡀⠂⠅⠌⠕⣰⢈⠒⠵⢢⢎⣐⠀⡃⠄⠀⣿⢷⣿⣿⣿⣟⣯⣷⠿⢻⢱⠂⠈
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠀⠀⠀⠀⠈⠀⢉⢒⠄⡂⡖⡩⢒⠄⠀⣿⡿⣟⣽⣾⡟⡏⠆⠀⠑⠈⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠄⠂⠈⠈⢑⠣⢇⡎⠄⣿⣿⡿⡉⠃⠃⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠀⠀⠁⠁⠀⠎⠛⠉⡀⠉⠃⠀⠀⠀⠀⠀⠀⠀
"""

def print_banner() -> None:
    print(f"{RED}{ASCII_BANNER}")
    print(f"{RED}{ascii_art}{RESET}")
    print(f"{BOLD}{RED}C0rps3 — The Intelligence Tool{RESET}")
    print(f"{BOLD}Type 'help' for commands, 'exit' to quit.{RESET}")
    print()


# ---------------------------------------------------------------------------
# Command registry
# ---------------------------------------------------------------------------

def _build_commands():
    """Build the command dispatch table. Built lazily so local handlers
    (`_help`, `_exit`, etc.) are defined when the dict is constructed."""
    from osint import shodan_recon, network, people, media, web, social, deep
    return {
        "help":      _help,
        "exit":      _exit,
        "quit":      _exit,
        "clear":     _clear,
        "about":     _about,
        "shodan":    shodan_recon.run,
        "dns":       lambda a: network.run(["dns"] + a),
        "whois":     lambda a: network.run(["whois"] + a),
        "geo":       lambda a: network.run(["geo"] + a),
        "user":      lambda a: people.run(["user"] + a),
        "email":     lambda a: people.run(["email"] + a),
        "phone":     lambda a: people.run(["phone"] + a),
        "exif":      lambda a: media.run(a),
        "headers":   lambda a: web.run(["headers"] + a),
        "scrape":    lambda a: web.run(["scrape"] + a),
        "paste":     lambda a: web.run(["paste"] + a),
        "deep":     lambda a: deep.run(a),
        "twitter":   lambda a: social.run(["twitter"] + a),
        "reverse":   lambda a: social.run(["reverse"] + a),
    }

HELP_LINES = [
    ("help",                    "Show this help"),
    ("clear",                   "Clear the screen"),
    ("exit / quit",             "Leave the REPL"),
    ("about",                   "About C0rps3"),
    ("",                        ""),
    ("shodan host <ip>",        "Shodan host report (banners, vulns)"),
    ("shodan search <query>",   "Shodan search query"),
    ("dns <domain>",            "A/AAAA/MX/NS/TXT records"),
    ("whois <target>",          "Domain or IP WHOIS (RDAP)"),
    ("geo <ip>",                "IP geolocation (city/country/ISP)"),
    ("",                        ""),
    ("user <username>",         "Username enumeration across platforms"),
    ("email <addr>",            "HaveIBeenPwned breach check"),
    ("phone <number>",          "Phone number parse/carrier/region"),
    ("",                        ""),
    ("exif <image_path>",       "Extract EXIF metadata from an image"),
    ("",                        ""),
    ("headers <url>",           "Show HTTP response headers"),
    ("scrape <url>",            "Title + meta + first links"),
    ("paste <query>",           "Public paste search"),
    ("twitter <handle>",        "Twitter/X user lookup (needs TWITTER_BEARER)"),
    ("reverse <lat,lon>",       "Reverse geocode coordinates to address"),
    ("deep <type> <target>",    "Aggregated OSINT lookup across modules (ip, domain, user, email, phone)")
]


def _help(_args):
    print_section("Commands")
    for cmd, desc in HELP_LINES:
        if cmd and desc:
            print_kv(cmd, desc)
        else:
            print()


def _exit(_args):
    print(f"{GREEN}Goodbye.{RESET}")
    sys.exit(0)


def _clear(_args):
    os.system("cls" if os.name == "nt" else "clear")


def _about(_args):
    print_section("About")
    print_kv("Name",    "C0rps3 — The Intelligence Tool")
    print_kv("Version", "1.0.0")
    print_kv("Mode",    "Interactive OSINT REPL")
    print_kv("Keys",    "Loaded from .env (see .env.example)")


# ---------------------------------------------------------------------------
# REPL
# ---------------------------------------------------------------------------

def repl() -> None:
    print_banner()
    commands = _build_commands()
    while True:
        try:
            line = input(f"{RED}C0rps3{RESET}{BOLD}> {RESET}")
        except (EOFError, KeyboardInterrupt):
            print()
            _exit([])
        line = line.strip()
        if not line:
            continue
        try:
            parts = shlex.split(line)
        except ValueError as exc:
            print_error(f"Parse error: {exc}")
            continue
        cmd, args = parts[0], parts[1:]
        handler = commands.get(cmd.lower())
        if not handler:
            print_warning(f"Unknown command: {cmd}  (try 'help')")
            continue
        try:
            handler(args)
        except KeyboardInterrupt:
            print_warning("Interrupted.")
        except Exception as exc:  # keep the REPL alive on any error
            print_error(f"{exc.__class__.__name__}: {exc}")


if __name__ == "__main__":
    repl()
