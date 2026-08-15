"""Social/paste lookups: geo reverse from coordinates, Twitter/X lookup.

Twitter/X is intentionally a thin stub: it calls the v2 API directly with a
bearer token so we avoid tweepy's OAuth flow. If TWITTER_BEARER is unset, it
prints setup instructions.
"""
from __future__ import annotations

import requests
from geopy.geocoders import Nominatim

from . import config
from utils.output import print_section, print_kv, print_error, print_warning, need

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")


def reverse_geo(args: list[str]) -> None:
    """Reverse geocode lat,lon to an address. Usage: geo reverse <lat>,<lon>"""
    if not args:
        print_warning("Usage: geo reverse <lat>,<lon>   e.g. geo reverse 37.7749,-122.4194")
        return
    raw = args[0]
    if "," not in raw:
        print_warning("Expected lat,lon")
        return
    try:
        lat_s, lon_s = raw.split(",", 1)
        lat, lon = float(lat_s), float(lon_s)
    except ValueError:
        print_error("Invalid lat/lon")
        return
    print_section(f"Reverse geocode: {lat}, {lon}")
    try:
        geocoder = Nominatim(user_agent="C0rps3-OSINT/1.0")
        location = geocoder.reverse((lat, lon), language="en", timeout=15)
    except Exception as exc:
        print_error(f"Geocoder error: {exc}")
        return
    if not location:
        print_warning("No address found.")
        return
    print_kv("Address", location.address)
    print_kv("Lat/Lon", f"{location.latitude}, {location.longitude}")
    if location.raw.get("class"):
        print_kv("Class", location.raw.get("class"))
    if location.raw.get("type"):
        print_kv("Type", location.raw.get("type"))


def twitter(args: list[str]) -> None:
    """Look up a Twitter/X user by handle. Requires TWITTER_BEARER in .env."""
    if not args:
        print_warning("Usage: twitter <handle>")
        return
    handle = args[0].lstrip("@")
    bearer = need(config.get_twitter_bearer(), "TWITTER_BEARER")
    if not bearer:
        print_warning("Set TWITTER_BEARER in .env (get one at developer.twitter.com).")
        return
    print_section(f"Twitter/X lookup: @{handle}")
    url = f"https://api.twitter.com/2/users/by/username/{handle}"
    params = {"user.fields": "id,name,username,description,location,public_metrics,verified,created_at"}
    headers = {"Authorization": f"Bearer {bearer}", "User-Agent": UA}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=15)
    except requests.RequestException as exc:
        print_error(f"Twitter API error: {exc}")
        return
    if r.status_code == 401:
        print_error("Twitter rejected the bearer token (401). Check TWITTER_BEARER.")
        return
    if r.status_code == 429:
        print_error("Rate-limited by Twitter API. Slow down.")
        return
    if not r.ok:
        print_error(f"Twitter returned {r.status_code}: {r.text[:200]}")
        return
    data = (r.json() or {}).get("data") or {}
    if not data:
        print_warning("No user found.")
        return
    print_kv("ID", data.get("id"))
    print_kv("Name", data.get("name"))
    print_kv("Handle", "@" + data.get("username", ""))
    print_kv("Verified", data.get("verified"))
    print_kv("Created", data.get("created_at"))
    print_kv("Description", (data.get("description") or "(none)")[:200])
    print_kv("Location", data.get("location") or "(none)")
    metrics = data.get("public_metrics") or {}
    for k in ("followers_count", "following_count", "tweet_count", "listed_count"):
        if k in metrics:
            print_kv(k, metrics[k])


def run(args: list[str]) -> None:
    """Dispatch: geo reverse <lat,lon> | twitter <handle>"""
    if not args:
        print_warning("Usage: geo reverse <lat,lon>  |  twitter <handle>")
        return
    cmd, rest = args[0], args[1:]
    if cmd == "geo":
        # alias for reverse_geo so users can type `social geo ...` or `geo reverse ...`
        reverse_geo(rest)
    elif cmd == "twitter":
        twitter(rest)
    elif cmd == "reverse":
        reverse_geo(rest)
    else:
        print_warning(f"Unknown social command: {cmd}")
