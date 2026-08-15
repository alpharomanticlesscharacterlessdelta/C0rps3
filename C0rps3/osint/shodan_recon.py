"""Shodan host & search lookups."""
from __future__ import annotations

import shodan

from . import config
from utils.output import print_section, print_kv, print_table, print_error, print_warning, need


def _client():
    key = need(config.get_shodan_key(), "SHODAN_API_KEY")
    if not key:
        return None
    try:
        return shodan.Shodan(key)
    except shodan.APIError as exc:
        print_error(f"Shodan init failed: {exc}")
        return None


def _print_host(host: dict) -> None:
    print_section("Shodan Host Report")
    print_kv("IP", host.get("ip_str", "?"))
    print_kv("Org", host.get("org", "?"))
    print_kv("ISP", host.get("isp", "?"))
    print_kv("OS", host.get("os", "?"))
    print_kv("Country", host.get("country_name", "?"))
    print_kv("City", host.get("city", "?"))
    print_kv("ASN", host.get("asn", "?"))
    print_kv("Last update", host.get("last_update", "?"))
    ports = host.get("ports", [])
    vulns = host.get("vulns") or {}
    if ports:
        print_kv("Open ports", ", ".join(str(p) for p in ports))
    if vulns:
        print_kv("Vulns (CVEs)", ", ".join(sorted(vulns.keys())))
    services = []
    for item in host.get("data", []):
        services.append((
            item.get("port", "?"),
            item.get("transport", "?"),
            (item.get("product") or "")[:30],
            (item.get("version") or "")[:20],
        ))
    if services:
        print_section(f"Banners ({len(services)})")
        print_table(services, headers=("Port", "Transport", "Product", "Version"))


def host(args: list[str]) -> None:
    if len(args) < 1:
        print_warning("Usage: shodan host <ip>")
        return
    client = _client()
    if not client:
        return
    ip = args[0]
    try:
        result = client.host(ip)
    except shodan.APIError as exc:
        print_error(f"Shodan error: {exc}")
        return
    _print_host(result)


def search(args: list[str]) -> None:
    if not args:
        print_warning("Usage: shodan search <query>")
        print_warning('Example: shodan search "apache country:US"')
        return
    client = _client()
    if not client:
        return
    query = " ".join(args)
    try:
        results = client.search(query)
    except shodan.APIError as exc:
        print_error(f"Shodan error: {exc}")
        return
    matches = results.get("matches", [])
    print_section(f"Shodan Search: {query}")
    print_kv("Total", results.get("total", "?"))
    if not matches:
        print_warning("No matches.")
        return
    rows = []
    for m in matches[:25]:
        rows.append((
            m.get("ip_str", "?"),
            m.get("port", "?"),
            m.get("org", "?")[:30],
            (m.get("product") or "")[:20],
            m.get("location", {}).get("country_name", "?"),
        ))
    print_table(rows, headers=("IP", "Port", "Org", "Product", "Country"))


def run(args: list[str]) -> None:
    """Dispatch shodan subcommands: shodan host <ip> | shodan search <query>"""
    if not args or args[0] in ("help", "?"):
        print_section("shodan")
        print("  shodan host <ip>")
        print("  shodan search <query>")
        return
    sub = args[0]
    rest = args[1:]
    if sub == "host":
        host(rest)
    elif sub == "search":
        search(rest)
    else:
        print_warning(f"Unknown shodan subcommand: {sub}")
        print_warning("Try: shodan host <ip>  |  shodan search <query>")
