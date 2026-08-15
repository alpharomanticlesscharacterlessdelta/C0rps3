"""Web reconnaissance: HTTP headers, scraping, paste search."""
from __future__ import annotations

import requests
from bs4 import BeautifulSoup

from utils.output import print_section, print_kv, print_table, print_error, print_warning

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")


def headers(args: list[str]) -> None:
    if not args:
        print_warning("Usage: headers <url>")
        return
    url = args[0]
    print_section(f"HTTP Headers: {url}")
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=15, allow_redirects=True)
    except requests.RequestException as exc:
        print_error(f"Request failed: {exc}")
        return
    print_kv("Final URL", r.url)
    print_kv("Status", f"{r.status_code} {r.reason}")
    print_kv("Encoding", r.encoding)
    print_kv("Content-Type", r.headers.get("Content-Type", "?"))
    print_kv("Content-Length", r.headers.get("Content-Length", "?"))
    print_kv("Server", r.headers.get("Server", "?"))
    print_kv("Cookies", len(r.cookies))
    print_section("All headers")
    for k, v in r.headers.items():
        print_kv(k, v)


def scrape(args: list[str]) -> None:
    if not args:
        print_warning("Usage: scrape <url>")
        return
    url = args[0]
    print_section(f"Scrape: {url}")
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
        r.raise_for_status()
    except requests.RequestException as exc:
        print_error(f"Request failed: {exc}")
        return
    soup = BeautifulSoup(r.text, "html.parser")
    title = (soup.title.string.strip() if soup.title and soup.title.string else None)
    meta_desc = None
    og_desc = None
    for tag in soup.find_all("meta"):
        name = (tag.get("name") or "").lower()
        prop = (tag.get("property") or "").lower()
        if name == "description" and tag.get("content"):
            meta_desc = tag["content"]
        if prop == "og:description" and tag.get("content"):
            og_desc = tag["content"]
    print_kv("Title", title or "(none)")
    print_kv("Meta description", meta_desc or "(none)")
    print_kv("OG description", og_desc or "(none)")
    # First N <a href> links
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        text = a.get_text(" ", strip=True)[:60]
        if href and not href.startswith("#"):
            links.append((href[:80], text))
        if len(links) >= 25:
            break
    if links:
        print_section(f"First {len(links)} links")
        print_table(links, headers=("Href", "Text"))


def paste(args: list[str]) -> None:
    """Search recent public pastes via psbdmp.ws (no key required)."""
    if not args:
        print_warning("Usage: paste <query>")
        return
    query = " ".join(args)
    print_section(f"Paste search: {query}")
    try:
        r = requests.post(
            "https://psbdmp.ws/api/v3/search",
            json={"q": query},
            headers={"User-Agent": UA, "Content-Type": "application/json"},
            timeout=20,
        )
        r.raise_for_status()
    except requests.RequestException as exc:
        print_error(f"Paste search failed: {exc}")
        return
    try:
        data = r.json()
    except ValueError:
        print_error("Paste API returned non-JSON response (rate-limited?).")
        return
    items = data.get("data") or []
    if not items:
        print_warning("No pastes matched.")
        return
    rows = []
    for it in items[:30]:
        rows.append((
            it.get("id", "?"),
            it.get("title", "")[:40] or "(untitled)",
            it.get("author", "?")[:30],
            it.get("date", "?"),
        ))
    print_table(rows, headers=("ID", "Title", "Author", "Date"))


def run(args: list[str]) -> None:
    """Dispatch: headers <url> | scrape <url> | paste <query>"""
    if not args:
        print_warning("Usage: headers <url>  |  scrape <url>  |  paste <query>")
        return
    cmd, rest = args[0], args[1:]
    if cmd == "headers":
        headers(rest)
    elif cmd == "scrape":
        scrape(rest)
    elif cmd == "paste":
        paste(rest)
    else:
        print_warning(f"Unknown web command: {cmd}")
