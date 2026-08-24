"""
What already sits at an entry's declared output — cli-v1 R15 (`draft_exists`)
and R18 (generate's refusal). Both ask the same question of disk, so they
share one answer here.
"""
from __future__ import annotations

import re
from pathlib import Path, PurePosixPath

from agf.manifest import Entry

# Split-only, non-capturing: manifest.py's own `_PLACEHOLDER_RE` gained a
# capturing group for R63's spec validation, and `re.split` interleaves a
# capturing group's own matched text into its result — exactly the wrong
# shape here, where only the literal text around the one placeholder is
# wanted.
_PLACEHOLDER_SPLIT_RE = re.compile(r"\{n(?::[^}]*)?\}")


def _template_regex(basename: str) -> re.Pattern:
    """R18: `{n}` — bare, or carrying a format spec — matches one or more
    decimal digits; the literal text around it must match exactly."""
    parts = _PLACEHOLDER_SPLIT_RE.split(basename)
    pattern = r"\d+".join(re.escape(part) for part in parts)
    return re.compile(pattern + "$")


def find_occupying_path(entry: Entry, drafts: Path) -> Path | None:
    """The first path that already occupies `entry`'s declared output, or
    None if it is vacant."""
    if entry.operation == "extract_frames":
        dirpath = drafts / PurePosixPath(entry.output).parent
        if not dirpath.exists():
            return None
        pattern = _template_regex(PurePosixPath(entry.output).name)
        for candidate in sorted(dirpath.iterdir()):
            if candidate.is_file() and pattern.fullmatch(candidate.name):
                return candidate
        return None

    path = drafts / entry.output
    if path.exists() and path.is_file():
        return path
    return None
