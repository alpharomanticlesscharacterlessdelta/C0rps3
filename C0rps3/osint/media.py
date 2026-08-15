"""EXIF metadata extraction from images."""
from __future__ import annotations

import os

import exifread

from utils.output import print_section, print_kv, print_warning, print_error


# Human-friendly tags shown first; everything else is appended.
PRIORITY_TAGS = (
    "Image Make", "Image Model", "Image DateTime", "EXIF DateTimeOriginal",
    "EXIF DateTimeDigitized", "GPS GPSLatitude", "GPS GPSLongitude",
    "GPS GPSAltitude", "GPS GPSLatitudeRef", "GPS GPSLongitudeRef",
    "Image Software", "Image Artist", "Image Copyright",
)


def exif(args: list[str]) -> None:
    if not args:
        print_warning("Usage: exif <image_path>")
        return
    path = args[0]
    if not os.path.isfile(path):
        print_error(f"File not found: {path}")
        return
    print_section(f"EXIF: {path}")
    try:
        with open(path, "rb") as f:
            tags = exifread.process_file(f, details=True)
    except Exception as exc:
        print_error(f"Failed to read EXIF: {exc}")
        return
    if not tags:
        print_warning("No EXIF tags found.")
        return
    shown = set()
    for tag in PRIORITY_TAGS:
        if tag in tags:
            print_kv(tag, _fmt(tags[tag]))
            shown.add(tag)
    print_kv("...", f"{len(tags) - len(shown)} more tags")
    if len(tags) > len(shown):
        print_section("All tags")
        for k, v in tags.items():
            if k in shown:
                continue
            print_kv(k, _fmt(v))


def _fmt(tag) -> str:
    """Compact human-readable formatting for EXIF tag values."""
    try:
        s = str(tag)
        if len(s) > 80:
            s = s[:77] + "..."
        return s
    except Exception:
        return repr(tag)


def run(args: list[str]) -> None:
    """Dispatch: exif <path>"""
    if not args:
        print_warning("Usage: exif <image_path>")
        return
    exif(args)
