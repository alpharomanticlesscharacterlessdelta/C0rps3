"""DNS lookups, WHOIS, and IP geolocation."""
from __future__ import annotations

import socket

import dns.resolver as _dns_resolver
_dns = _dns_resolver
import requests
from ipwhois import IPWhois

from utils.output import print_section, print_kv, print_error, print_warning


DNS_TYPES = ("A", "AAAA", "MX", "NS", "TXT")


def dns(args: list[str]) -> None:
    if not args:
        print_warning("Usage: dns <domain>")
        return
    domain = args[0]
    print_section(f"DNS Records: {domain}")
    found_any = False
    for rtype in DNS_TYPES:
        try:
            answers = dns.resolver.resolve(domain, rtype, raise_on_no_answer=False)
            for rdata in answers:
                print_kv(rtype, rdata.to_text().strip('"'))
                found_any = True
        except dns.resolver.NoAnswer:
            continue
        except dns.resolver.NXDOMAIN:
            print_error(f"{domain} does not exist (NXDOMAIN).")
            return
        except dns.exception.Timeout:
            print_warning(f"{rtype} lookup timed out.")
        except Exception as exc:  # pragma: no cover
            print_warning(f"{rtype} lookup failed: {exc}")
    if not found_any:
        print_warning("No records found.")


def whois(args: list[str]) -> None:
    if not args:
        print_warning("Usage: whois <domain-or-ip>")
        return
    target = args[0]
    # Decide: domain or IP
    try:
        socket.inet_aton(target)
        kind = "ip"
    except OSError:
        kind = "domain"
    print_section(f"WHOIS: {target}")
    try:
        if kind == "ip":
            obj = IPWhois(target)
            res = obj.lookup_rdap(depth=1)
        else:
            # Domain RDAP via RDAP.org public bootstrap.
            url = f"https://rdap.org/domain/{target}"
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            data = r.json()
            res = _flatten_rdap(data)
            for k in (
                "handle", "name", "status", "registrationDate",
                "expirationDate", "lastChangedDate",
            ):
                print_kv(k, res.get(k, "-"))
            entities = res.get("entities") or []
            if entities:
                print_kv("Entities", ", ".join(str(e) for e in entities))
            nameservers = res.get("nameservers") or []
            if nameservers:
                print_kv("Nameservers", ", ".join(nameservers))
            return
    except requests.HTTPError as exc:
        print_error(f"RDAP lookup failed: {exc}")
        return
    except Exception as exc:
        print_error(f"WHOIS failed: {exc}")
        return
    # IP path
    for k in ("asn", "asn_country_code", "asn_description", "network"):
        v = res.get(k)
        if v:
            print_kv(k, v)


def _flatten_rdap(data: dict) -> dict:
    """Extract top-level RDAP fields + events + entities."""
    out = {
        "handle": data.get("handle"),
        "name": data.get("ldhName") or data.get("unicodeName"),
        "status": ", ".join(data.get("status", [])) if isinstance(data.get("status"), list) else data.get("status"),
        "entities": [],
        "nameservers": [],
    }
    for ev in data.get("events", []):
        action = (ev.get("eventAction") or "").lower()
        if action in ("registration", "expiration", "last changed", "last update"):
            out[action.replace(" ", "").capitalize() + "Date" if action == "registration" else
                "registrationDate" if action == "registration" else
                "expirationDate" if action == "expiration" else
                "lastChangedDate"] = ev.get("eventDate")
    for ent in data.get("entities", []):
        vcard = ent.get("vcardArray") or []
        if vcard and isinstance(vcard, list) and len(vcard) > 1:
            for field in vcard[1]:
                if isinstance(field, list) and field and field[0] == "fn":
                    out["entities"].append(str(field[3]))
                    break
    for ns in data.get("nameservers", []):
        out["nameservers"].append(ns.get("ldhName") or ns.get("unicodeName") or "?")
    return out


def geo(args: list[str]) -> None:
    """IP geolocation via ip-api.com (free, no key, 45 req/min)."""
    if not args:
        print_warning("Usage: geo <ip>")
        return
    ip = args[0]
    print_section(f"Geolocation: {ip}")
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=15)
        r.raise_for_status()
        data = r.json()
    except Exception as exc:
        print_error(f"Geo lookup failed: {exc}")
        return
    if data.get("status") == "fail":
        print_error(data.get("message", "lookup failed"))
        return
    for k in ("country", "regionName", "city", "zip", "lat", "lon",
              "timezone", "isp", "org", "as", "query"):
        if k in data and data[k]:
            print_kv(k, data[k])


def run(args: list[str]) -> None:
    """Dispatch: dns <dom> | whois <tgt> | geo <ip>"""
    if not args:
        print_warning("Usage: dns <domain>  |  whois <target>  |  geo <ip>")
        return
    cmd, rest = args[0], args[1:]
    if cmd == "dns":
        dns(rest)
    elif cmd == "whois":
        whois(rest)
    elif cmd == "geo":
        geo(rest)
    else:
        print_warning(f"Unknown network command: {cmd}")
