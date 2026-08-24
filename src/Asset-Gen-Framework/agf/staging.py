"""
The run lock and the sweep — cli-v1 R66-R70, R72.
"""
from __future__ import annotations

import errno
import fcntl
import json
import shutil
from pathlib import Path

from agf.errors import BusyError, ConfigError

TMP_PREFIX = ".agf-tmp-"
OLD_PREFIX = ".agf-old-"

# The two errnos POSIX flock(2) documents for "already locked by another
# process" with LOCK_NB — what "busy" (R28 code 9) actually means. Anything
# else raised trying to acquire the lock is a different failure: the lock
# file or its directory could not be opened at all, which is not busy.
_LOCK_HELD_ERRNOS = {errno.EACCES, errno.EAGAIN}


def acquire_lock(lock_path: Path):
    """R72: a kernel-level advisory lock on `<record filename>.lock`,
    created once and never deleted. Busy is decided by trying to acquire it,
    never by the file existing — and only a lock actually held by another
    run is busy; a lock file that could not even be opened (permissions, a
    filesystem with no lock support) is a different, stated failure."""
    try:
        lock_path.touch(exist_ok=True)
        fh = open(lock_path, "r+")
    except OSError as exc:
        raise ConfigError(
            f"could not open the lock file {lock_path}: {exc}",
            remedy=f"check permissions on {lock_path} and its directory",
        ) from exc

    try:
        fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as exc:
        fh.close()
        if exc.errno in _LOCK_HELD_ERRNOS:
            raise BusyError(
                f"another run holds the lock on {lock_path}, which serialises {lock_path.stem}"
            ) from exc
        raise ConfigError(
            f"could not acquire a lock on {lock_path}: {exc}",
            remedy=f"check that {lock_path} is on a filesystem that supports file locking",
        ) from exc
    return fh


def release_lock(fh) -> None:
    """R72: the lock is released when the run ends. The file itself stays —
    unlinking it would race a run still waiting on the same inode."""
    try:
        fcntl.flock(fh, fcntl.LOCK_UN)
    finally:
        fh.close()


def _remove_path(path: Path) -> None:
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink()


def sweep(drafts: Path, record_path: Path) -> None:
    """
    R69: repair interrupted staging before anything else touches drafts.
    Reads only the config (already resolved into `drafts`/`record_path`) and
    the markers themselves — never the manifest.
    """
    markers = sorted(drafts.rglob(f"{TMP_PREFIX}*.json"))
    accounted_displaced: set[Path] = set()

    for marker_path in markers:
        try:
            data = json.loads(marker_path.read_text())
            destination_rel = data["destination"]
            displaced_rel = data["displaced"]
        except (OSError, ValueError, KeyError):
            # Unreadable or incomplete: the marker is written whole and
            # flushed before any rename, so this means no rename happened.
            run_id = marker_path.name[len(TMP_PREFIX) : -len(".json")]
            staging_dir = marker_path.parent / f"{TMP_PREFIX}{run_id}"
            if staging_dir.exists():
                _remove_path(staging_dir)
            marker_path.unlink(missing_ok=True)
            continue

        destination = drafts / destination_rel
        displaced = drafts / displaced_rel
        accounted_displaced.add(displaced.resolve())

        run_id = marker_path.name[len(TMP_PREFIX) : -len(".json")]
        staging_dir = marker_path.parent / f"{TMP_PREFIX}{run_id}"

        dest_exists = destination.exists()
        displaced_exists = displaced.exists()

        if not dest_exists and displaced_exists:
            destination.parent.mkdir(parents=True, exist_ok=True)
            displaced.rename(destination)
        elif dest_exists and displaced_exists:
            _remove_path(displaced)
        # else: nothing to restore, nothing to delete.

        if staging_dir.exists():
            _remove_path(staging_dir)
        marker_path.unlink(missing_ok=True)

    # A staging directory with no marker at all — killed between creating
    # the directory and writing the marker — holds nothing committed.
    for candidate in drafts.rglob(f"{TMP_PREFIX}*"):
        if candidate.is_dir() and not candidate.name.endswith(".json"):
            marker_path = candidate.with_name(candidate.name + ".json")
            if not marker_path.exists():
                _remove_path(candidate)

    # A `.agf-old-*` directory no marker points at is unaccounted debris.
    for old_dir in drafts.rglob(f"{OLD_PREFIX}*"):
        if old_dir.resolve() not in accounted_displaced:
            _remove_path(old_dir)

    # R53/R69: a leftover temporary record copy, beside the record file
    # (never inside drafts, per R11), is swept too.
    for stray in record_path.parent.glob(f"{TMP_PREFIX}*"):
        _remove_path(stray)
