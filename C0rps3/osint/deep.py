'''Deep OSINT aggregation.

Provides a single `deep` command that runs a suite of OSINT lookups depending on the target type.
Supported target types:
- ip:   Runs Shodan host lookup, IP WHOIS, and geolocation.
- domain:   Runs WHOIS, DNS records, and geo (if the domain resolves to an IP).
- user:   Runs username enumeration across many platforms.
- email:   Runs HaveIBeenPwned breach check.
- phone:   Runs phone number parsing.

The command is intended to give a quick, comprehensive profile without the user needing
to invoke several individual commands.
'''

from __future__ import annotations

from typing import List

# Import sub-modules lazily when needed to avoid unnecessary dependency load.

def _run_ip(target: str) -> None:
    """Run a set of IP‑based lookups: Shodan host, WHOIS, and geolocation."""
    from . import shodan_recon, network
    # Shodan host report
    shodan_recon.run(["host", target])
    # IP WHOIS (RDAP)
    network.run(["whois", target])
    # Geolocation (ip-api.com)
    network.run(["geo", target])


def _run_domain(target: str) -> None:
    """Run domain‑based lookups: WHOIS, DNS records, and optional Geo lookup.
    If the domain resolves to an IP, a geo lookup is performed on the first A record.
    """
    from . import network
    # Domain WHOIS (RDAP)
    network.run(["whois", target])
    # DNS query for common record types
    network.run(["dns", target])
    # Attempt to resolve an A record for geo lookup
    try:
        import dns.resolver as resolver
        answers = resolver.resolve(target, "A", raise_on_no_answer=False)
        if answers:
            ip = answers[0].to_text()
            network.run(["geo", ip])
    except Exception:
        # Silently ignore resolution failures – they will already be reported by the DNS command.
        pass


def _run_user(username: str) -> None:
    """Run username enumeration across many platforms."""
    from . import people
    people.run(["user", username])


def _run_email(address: str) -> None:
    """Run HaveIBeenPwned breach check for an email address."""
    from . import people
    people.run(["email", address])


def _run_phone(number: str) -> None:
    """Parse and display information about a phone number."""
    from . import people
    people.run(["phone", number])


def run(args: List[str]) -> None:
    """Dispatch deep OSINT based on target type.
    Usage examples:
        deep ip 8.8.8.8
        deep domain example.com
        deep user alice
        deep email alice@example.com
        deep phone +14155551234
    """
    if not args:
        from utils.output import print_warning
        print_warning("Usage: deep <type> <target>")
        return
    typ, *rest = args
    target = " ".join(rest).strip()
    if not target:
        from utils.output import print_warning
        print_warning("Missing target for deep command.")
        return
    typ = typ.lower()
    if typ == "ip":
        _run_ip(target)
    elif typ == "domain":
        _run_domain(target)
    elif typ == "user":
        _run_user(target)
    elif typ == "email":
        _run_email(target)
    elif typ == "phone":
        _run_phone(target)
    else:
        from utils.output import print_warning
        print_warning(f"Unknown deep target type: {typ}. Supported: ip, domain, user, email, phone.")
