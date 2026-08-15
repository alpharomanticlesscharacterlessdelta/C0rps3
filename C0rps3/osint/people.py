"""Identity lookups: username enumeration, email breach check, phone parsing."""
from __future__ import annotations

import phonenumbers
import requests

from . import config
from utils.output import (
    print_section, print_kv, print_table, print_error, print_warning,
    print_success, need,
)

# (display_name, url_template) — {u} is replaced with the username.
# Hit pattern: HEAD where possible (cheap), GET fallback.
USERNAME_SITES: list[tuple[str, str, str]] = [
    # (platform, url, method)
    ("GitHub",       "https://github.com/{u}",                 "GET"),
    ("Twitter/X",    "https://x.com/{u}",                       "GET"),
    ("Reddit",       "https://www.reddit.com/user/{u}/",        "GET"),
    ("Instagram",    "https://www.instagram.com/{u}/",          "GET"),
    ("TikTok",       "https://www.tiktok.com/@{u}",             "GET"),
    ("Pinterest",    "https://www.pinterest.com/{u}/",          "GET"),
    ("Medium",       "https://medium.com/@{u}",                 "GET"),
    ("Dev.to",       "https://dev.to/{u}",                      "GET"),
    ("HackerNews",   "https://news.ycombinator.com/user?id={u}","GET"),
    ("Keybase",      "https://keybase.io/{u}",                  "GET"),
]

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
HEADERS = {"User-Agent": UA}


def _check_username(site: str, url: str, method: str, username: str) -> str:
    """Return 'FOUND', 'NOT FOUND', or 'UNKNOWN'."""
    full = url.format(u=username)
    try:
        if method == "HEAD":
            r = requests.head(full, headers=HEADERS, timeout=10, allow_redirects=True)
        else:
            r = requests.get(full, headers=HEADERS, timeout=10, allow_redirects=True)
        if r.status_code == 200:
            return "FOUND"
        if r.status_code == 404:
            return "NOT FOUND"
        return f"HTTP {r.status_code}"
    except requests.RequestException as exc:
        return f"ERROR ({exc.__class__.__name__})"


def user(args: list[str]) -> None:
    if not args:
        print_warning("Usage: user <username>")
        return
    username = args[0]
    print_section(f"Username enumeration: {username}")
    rows = []
    for site, url, method in USERNAME_SITES:
        status = _check_username(site, url, method, username)
        rows.append((site, url.format(u=username), status))
    print_table(rows, headers=("Platform", "URL", "Status"))


def email(args: list[str]) -> None:
    """HaveIBeenPwned breach check for an email address."""
    if not args:
        print_warning("Usage: email <address>")
        return
    address = args[0]
    key = need(config.get_hibp_key(), "HIBP_API_KEY")
    if not key:
        return
    print_section(f"Breach check: {address}")
    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{address}"
    headers = {"hibp-api-key": key, "User-Agent": "C0rps3-OSINT"}
    try:
        r = requests.get(url, headers=headers, params={"truncateResponse": "false"}, timeout=15)
    except requests.RequestException as exc:
        print_error(f"HIBP request failed: {exc}")
        return
    if r.status_code == 404:
        print_success("No breaches found.")
        return
    if r.status_code == 401:
        print_error("HIBP rejected the API key (401). Check HIBP_API_KEY.")
        return
    if r.status_code == 429:
        print_error("Rate-limited by HIBP. Slow down.")
        return
    if not r.ok:
        print_error(f"HIBP returned {r.status_code}: {r.text[:200]}")
        return
    breaches = r.json()
    rows = []
    for b in breaches:
        rows.append((
            b.get("Name", "?"),
            b.get("BreachDate", "?"),
            b.get("PwnCount", "?"),
            ", ".join(b.get("DataClasses", [])),
        ))
    print_kv("Breaches", len(rows))
    print_table(rows, headers=("Name", "Date", "PwnCount", "Data classes"))


def phone(args: list[str]) -> None:
    if not args:
        print_warning('Usage: phone <number>   e.g. phone +14155551234')
        return
    raw = args[0]
    print_section(f"Phone lookup: {raw}")
    try:
        parsed = phonenumbers.parse(raw, None)
    except phonenumbers.NumberParseException as exc:
        print_error(f"Parse failed: {exc}")
        return
    print_kv("E.164", phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164))
    print_kv("International", phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL))
    print_kv("Country", f"{phone_region_country_name(parsed)} ({parsed.country_code})")
    print_kv("Carrier", carrier_name(parsed))
    print_kv("Line type", line_type(parsed))
    print_kv("Valid", phonenumbers.is_valid_number(parsed))
    print_kv("Possible", phonenumbers.is_possible_number(parsed))


def phone_region_country_name(num) -> str:
    """Best-effort country name for the parsed number's region."""
    try:
        from phonenumbers import geocoder, region_code_for_number
        code = region_code_for_number(num)
        name = geocoder.description_for_number(num, "en")
        return f"{name} [{code}]" if name else code or "?"
    except Exception:
        return "?"


def carrier_name(num) -> str:
    try:
        from phonenumbers import carrier
        return carrier.name_for_number(num, "en") or "?"
    except Exception:
        return "?"


def line_type(num) -> str:
    try:
        t = phonenumbers.number_type(num)
        return {
            phonenumbers.PhoneNumberType.MOBILE: "mobile",
            phonenumbers.PhoneNumberType.FIXED_LINE: "fixed line",
            phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "fixed/mobile",
            phonenumbers.PhoneNumberType.TOLL_FREE: "toll-free",
            phonenumbers.PhoneNumberType.PREMIUM_RATE: "premium-rate",
            phonenumbers.PhoneNumberType.VOIP: "voip",
            phonenumbers.PhoneNumberType.PERSONAL_NUMBER: "personal",
            phonenumbers.PhoneNumberType.PAGER: "pager",
            phonenumbers.PhoneNumberType.UAN: "UAN",
            phonenumbers.PhoneNumberType.VOICEMAIL: "voicemail",
            phonenumbers.PhoneNumberType.UNKNOWN: "unknown",
        }.get(t, "?")
    except Exception:
        return "?"


def run(args: list[str]) -> None:
    """Dispatch: user <u> | email <addr> | phone <num>"""
    if not args:
        print_warning("Usage: user <u>  |  email <addr>  |  phone <num>")
        return
    cmd, rest = args[0], args[1:]
    if cmd == "user":
        user(rest)
    elif cmd == "email":
        email(rest)
    elif cmd == "phone":
        phone(rest)
    else:
        print_warning(f"Unknown people command: {cmd}")
