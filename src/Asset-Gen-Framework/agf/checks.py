"""
Checks — cli-v1 R54, R57, R61, R71. Each check yields exactly one of
`pass`/`fail`/`skipped` (R71) plus a detail string naming the declared and
actual values, used to build `error.message` — the `checks` dict itself
stays the fixed three-value vocabulary.
"""
from __future__ import annotations

import io

from PIL import Image

CHECKS_KEYS = ("format", "layout", "frame_size", "frame_count", "output_count")


def detect_format(data: bytes) -> str | None:
    """Inspect the bytes themselves — never the filename or a stated content
    type (R54)."""
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if data[:2] == b"\xff\xd8":
        return "jpeg"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    if data[:4] == b"RIFF" and data[8:12] == b"WAVE":
        return "wav"
    if data[:3] == b"ID3":
        return "mp3"
    if len(data) >= 2 and data[0] == 0xFF and (data[1] & 0xE0) == 0xE0:
        return "mp3"
    if len(data) >= 12 and data[4:8] == b"ftyp":
        # QuickTime and MP4 share the ftyp box; the major brand tells them
        # apart. `qt  ` is what a ProRes 4444 (alpha-carrying) .mov declares.
        return "mov" if data[8:12] == b"qt  " else "mp4"
    return None


def check_format(data: bytes, declared_format: str) -> tuple[str, str | None]:
    actual = detect_format(data)
    if actual == declared_format:
        return "pass", None
    if actual is None:
        detail = (
            f"declared format is {declared_format!r}, but the bytes are not "
            "recognisable as any supported format"
        )
    else:
        detail = f"declared format is {declared_format!r}, but the bytes are {actual!r}"
    return "fail", detail


def check_layout(sheet_data: bytes, layout: dict, frame_size: list) -> tuple[str, str | None]:
    """R57: a sheet's pixel dimensions must equal exactly
    columns * frame_size[0] by rows * frame_size[1]."""
    expected = (frame_size[0] * layout["columns"], frame_size[1] * layout["rows"])
    try:
        with Image.open(io.BytesIO(sheet_data)) as img:
            actual = img.size
    except Exception:
        return "fail", (
            f"declared layout requires {expected[0]}x{expected[1]} pixels; "
            "the sheet image could not be read"
        )
    if actual != tuple(expected):
        return "fail", (
            f"declared layout requires {expected[0]}x{expected[1]} pixels, "
            f"sheet is {actual[0]}x{actual[1]} pixels"
        )
    return "pass", None


def check_frame_sizes(frame_paths, frame_size: list) -> tuple[str, str | None]:
    """R61: every assemble_sheet input frame's own pixel size must equal the
    declared `frame_size` — the framework never scales, crops or pads. A
    frame that cannot even be decoded is a `frame_size` failure too (R61),
    never an uncaught exception (defect 9).

    `Image.open` alone only reads the header, so a *truncated* file still
    reports a correct `.size` and would pass here while failing only later,
    when something actually decodes the pixel data — silently, if that
    later failure is swallowed (the defect-9 fix's own regression). `.load()`
    forces the real decode here, so an unreadable frame is caught at the
    one place already responsible for judging it, and nothing downstream
    needs to guard against the same failure a second time."""
    declared = tuple(frame_size)
    for path in frame_paths:
        try:
            with Image.open(path) as img:
                img.load()
                actual = img.size
        except Exception:
            return "fail", (
                f"frame {path.name} could not be read as an image; "
                f"declared frame_size is {declared[0]}x{declared[1]}"
            )
        if actual != declared:
            return "fail", (
                f"frame {path.name} is {actual[0]}x{actual[1]} pixels, "
                f"declared frame_size is {declared[0]}x{declared[1]}"
            )
    return "pass", None
