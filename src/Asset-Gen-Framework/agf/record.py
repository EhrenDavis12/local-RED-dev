"""
The record file — cli-v1 R47-R53, R76. A single JSON file, owned by the
framework, replaced by writing a complete new copy to a temp file and
renaming it into place — never edited or truncated in place.
"""
from __future__ import annotations

import json
import os
import uuid
from pathlib import Path

from agf.errors import RecordCorruptError
from agf.manifest import Entry

RECORD_ENTRY_KEYS = (
    "operation", "type", "model", "model_version", "prompt", "prompt_key",
    "seed", "inputs", "input_files", "output", "format", "frame_count",
    "frame_size", "layout", "frames", "source",
)


def _remedy(record_path: Path) -> str:
    return (
        f"delete {record_path} — the record is contained and trashable; "
        "deleting it costs only the ability to tweak from the last request, and nothing else"
    )


def load_record(record_path: Path) -> dict | None:
    """
    R76: a record file that exists and cannot be read as a valid record
    exits 13 — never an unexpected internal failure. The forms this takes
    (unparseable JSON, an empty file, a non-object top level, a missing or
    non-object `entries`, a non-object entry within it) are illustrative,
    not exhaustive: anything that stops the file being read as a record
    takes this path, so the whole body below is guarded, not just the
    JSON parse.
    """
    if not record_path.exists():
        return None

    try:
        text = record_path.read_text()
        data = json.loads(text)
        if not isinstance(data, dict):
            raise ValueError("its top level is not an object")
        entries = data.get("entries")
        if not isinstance(entries, dict):
            raise ValueError("its 'entries' is missing or is not an object")
        for entry_name, entry_value in entries.items():
            if not isinstance(entry_value, dict):
                raise ValueError(f"its entry {entry_name!r} is not an object")
    except RecordCorruptError:
        raise
    except Exception as exc:
        raise RecordCorruptError(
            f"record file {record_path} cannot be read as a valid record: {exc}",
            remedy=_remedy(record_path),
        ) from exc

    return data


def get_stored_entry(record_path: Path, name: str) -> dict | None:
    data = load_record(record_path)
    if data is None:
        return None
    return data.get("entries", {}).get(name)


def build_record_entry(entry: Entry, model_version: str | None, seed) -> dict:
    return {
        "operation": entry.operation,
        "type": entry.type,
        "model": entry.model,
        "model_version": model_version,
        "prompt": entry.prompt,
        "prompt_key": entry.prompt_key,
        "seed": seed,
        "inputs": entry.inputs,
        "input_files": entry.input_files,
        "output": entry.output,
        "format": entry.format,
        "frame_count": entry.frame_count,
        "frame_size": entry.frame_size,
        "layout": entry.layout,
        "frames": entry.frames,
        "source": entry.source,
    }


def write_record(record_path: Path, entry: Entry, model_version: str | None, seed) -> None:
    """R53: write a complete new copy to `.agf-tmp-<run id>` beside the
    record, then rename it onto the record path."""
    data = load_record(record_path) or {"version": 1, "entries": {}}
    data.setdefault("entries", {})
    data["entries"][entry.name] = build_record_entry(entry, model_version, seed)

    tmp_path = record_path.with_name(f".agf-tmp-{uuid.uuid4().hex}")
    with open(tmp_path, "w") as fh:
        json.dump(data, fh, indent=2, sort_keys=False)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp_path, record_path)
