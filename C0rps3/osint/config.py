"""Centralized config / secret loader.

Reads .env once at import time and exposes typed accessors. Each accessor
returns None when the key is missing so command handlers can decide whether
to skip with a friendly message or fail.
"""
from __future__ import annotations

import os

try:
    from dotenv import load_dotenv
    load_dotenv()  # no-op if .env doesn't exist
except Exception:
    # python-dotenv missing — fall back to raw env vars.
    pass


def get_shodan_key() -> str | None:
    return os.getenv("SHODAN_API_KEY") or None


def get_hibp_key() -> str | None:
    return os.getenv("HIBP_API_KEY") or None


def get_twitter_bearer() -> str | None:
    return os.getenv("TWITTER_BEARER") or None
