"""
The staging/commit/sweep mechanism — cli-v1 R66-R70. These fixtures
hand-craft the on-disk state an interrupted `generate`/`regenerate` would
have left (a staging directory, its marker, a displaced copy — see R67 for
the exact marker format assumed here), then trigger a sweep and assert what
it does. No provider and no real staging run is needed: `generate`/
`regenerate` sweep unconditionally at R27 step 4, before the manifest is
even parsed, so an intentionally-empty manifest plus a nonexistent entry
name is enough to reach exit 4 *after* the sweep has already run and
repaired whatever was sitting in drafts.

Wrong implementation this file defends against, per test: a sweep that
restores a displaced copy it should have deleted (or vice versa), one that
deletes debris it cannot account for from a marker, one that reaches into
the manifest to decide what to do, or one that touches a legitimate draft
sitting outside the two reserved prefixes.
"""
from __future__ import annotations

import json

from conftest import parse_single_json_document, write_manifest, write_raw_manifest


def _trigger_sweep(project, run_cli):
    """generate sweeps at step 4, before manifest parse (5) and entry lookup
    (6) — an empty manifest plus an unknown name reaches exit 4 only after
    the sweep has already run to completion."""
    code, out, _ = run_cli(["generate", "__no_such_entry__"] + project.config_args())
    doc = parse_single_json_document(out)
    return code, doc


def _marker(project, run_id, destination, displaced):
    path = project.drafts / f".agf-tmp-{run_id}.json"
    path.write_text(json.dumps({"destination": destination, "displaced": displaced}))
    return path


def _staging_dir(project, run_id):
    d = project.drafts / f".agf-tmp-{run_id}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _old_dir(project, run_id):
    d = project.drafts / f".agf-old-{run_id}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def test_sweep_runs_before_manifest_is_even_parsed(project, run_cli):
    """
    R69: 'nothing precedes the sweep but config validation and the lock...
    in particular before the manifest is read'. A repair must complete even
    when the manifest cannot parse at all.
    """
    write_raw_manifest(project, "not: [valid: yaml:::\n")
    old = _old_dir(project, "run1")
    (old / "walk_001.png").write_bytes(b"restored frame")
    _marker(project, "run1", destination="frames", displaced=".agf-old-run1")

    code, out, _ = run_cli(["generate", "whatever"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 3  # the run itself still fails, at the manifest stage...
    # ...but the sweep already repaired the drafts area before it got there.
    assert (project.drafts / "frames" / "walk_001.png").read_bytes() == b"restored frame"
    assert not old.exists()
    assert not (project.drafts / ".agf-tmp-run1.json").exists()


def test_row1_destination_missing_displaced_present_is_restored(project, run_cli):
    """
    R69 table row 1 — the repair that matters: a multi-file run killed
    between displacing the previous frame set and renaming the new one in.
    The staging directory (abandoned, unfinished) is discarded; the
    displaced copy (the previous, complete frame set) is restored.
    """
    write_manifest(project, [])
    old = _old_dir(project, "run1")
    (old / "walk_001.png").write_bytes(b"previous complete frame set")
    (old / "walk_002.png").write_bytes(b"previous complete frame set 2")
    staging = _staging_dir(project, "run1")
    (staging / "walk_001.png").write_bytes(b"unfinished new frame")
    _marker(project, "run1", destination="frames", displaced=".agf-old-run1")
    assert not (project.drafts / "frames").exists()

    code, doc = _trigger_sweep(project, run_cli)
    assert code == 4  # sweep succeeded; the probe entry just doesn't exist

    restored = project.drafts / "frames"
    assert restored.is_dir()
    assert (restored / "walk_001.png").read_bytes() == b"previous complete frame set"
    assert (restored / "walk_002.png").read_bytes() == b"previous complete frame set 2"
    assert not old.exists()
    assert not staging.exists()
    assert not (project.drafts / ".agf-tmp-run1.json").exists()


def test_row2_destination_present_displaced_present_deletes_displaced(project, run_cli):
    """
    R69 table row 2: the rename onto the destination already succeeded; only
    the old copy's deletion (step 4) didn't finish. The new destination must
    be left exactly as it is — never restored over with the old one.
    """
    write_manifest(project, [])
    dest = project.drafts / "frames"
    dest.mkdir()
    (dest / "walk_001.png").write_bytes(b"brand new committed frame")
    old = _old_dir(project, "run1")
    (old / "walk_001.png").write_bytes(b"stale previous frame")
    _marker(project, "run1", destination="frames", displaced=".agf-old-run1")

    code, doc = _trigger_sweep(project, run_cli)
    assert code == 4

    assert (dest / "walk_001.png").read_bytes() == b"brand new committed frame"
    assert not old.exists()
    assert not (project.drafts / ".agf-tmp-run1.json").exists()


def test_row3_single_file_destination_present_displaced_absent_is_left_alone(project, run_cli):
    """
    R69 table row 3, single-file variant: a completed single-file commit,
    interrupted only before its own marker got removed. Nothing to restore,
    nothing to delete — just clean up the marker.
    """
    write_manifest(project, [])
    dest = project.drafts / "sheet1.png"
    dest.write_bytes(b"finished sheet contents")
    # displaced is declared in every marker regardless of whether it was
    # ever used (R67); for a single-file entry it never gets created.
    _marker(project, "run1", destination="sheet1.png", displaced=".agf-old-run1")
    assert not (project.drafts / ".agf-old-run1").exists()

    code, doc = _trigger_sweep(project, run_cli)
    assert code == 4

    assert dest.read_bytes() == b"finished sheet contents"
    assert not (project.drafts / ".agf-tmp-run1.json").exists()


def test_row3_multi_file_destination_present_displaced_absent_killed_before_displacing(project, run_cli):
    """
    R69 table row 3, the other reading: a run killed mid-staging, before it
    ever touched the previous frame set at the destination. The previous,
    untouched asset must survive exactly as it was.
    """
    write_manifest(project, [])
    dest = project.drafts / "frames"
    dest.mkdir()
    (dest / "walk_001.png").write_bytes(b"previous untouched frame")
    staging = _staging_dir(project, "run1")
    (staging / "walk_001.png").write_bytes(b"half-written new frame")
    _marker(project, "run1", destination="frames", displaced=".agf-old-run1")

    code, doc = _trigger_sweep(project, run_cli)
    assert code == 4

    assert (dest / "walk_001.png").read_bytes() == b"previous untouched frame"
    assert not staging.exists()
    assert not (project.drafts / ".agf-old-run1").exists()
    assert not (project.drafts / ".agf-tmp-run1.json").exists()


def test_staging_directory_with_no_marker_is_removed(project, run_cli):
    """A run killed between creating the staging directory and writing its
    marker: holds nothing committed and is discarded."""
    write_manifest(project, [])
    orphan_staging = _staging_dir(project, "orphan")
    (orphan_staging / "half_written.png").write_bytes(b"junk")
    assert not (project.drafts / ".agf-tmp-orphan.json").exists()

    code, doc = _trigger_sweep(project, run_cli)
    assert code == 4
    assert not orphan_staging.exists()


def test_unparseable_marker_means_no_rename_had_happened_yet(project, run_cli):
    """
    R69: the marker is written whole and flushed before any rename, so one
    that cannot be parsed at all means the run never got as far as
    displacing or renaming anything — clean up and move on, restore nothing.
    """
    write_manifest(project, [])
    staging = _staging_dir(project, "corrupt")
    (staging / "half_written.png").write_bytes(b"junk")
    marker = project.drafts / ".agf-tmp-corrupt.json"
    marker.write_text("{not valid json::: at all")

    code, doc = _trigger_sweep(project, run_cli)
    assert code == 4
    assert not staging.exists()
    assert not marker.exists()


def test_unaccounted_displaced_copy_with_no_marker_at_all_is_removed(project, run_cli):
    """
    R69: 'after every marker has been processed, a .agf-old-* directory that
    no marker points at is removed.' Not restored anywhere — there is no
    marker naming a destination to restore it to.
    """
    write_manifest(project, [])
    unaccounted = _old_dir(project, "ghost")
    (unaccounted / "walk_001.png").write_bytes(b"orphaned")
    assert not (project.drafts / ".agf-tmp-ghost.json").exists()

    code, doc = _trigger_sweep(project, run_cli)
    assert code == 4
    assert not unaccounted.exists()


def test_sweep_never_restores_a_displaced_copy_whose_marker_names_a_present_destination(project, run_cli):
    """
    The negative of row 1: the sweep must not restore .agf-old-* over a
    destination that is already correctly in place, purely because a
    displaced copy happens to exist.
    """
    write_manifest(project, [])
    dest = project.drafts / "frames"
    dest.mkdir()
    (dest / "walk_001.png").write_bytes(b"correct current frame")
    old = _old_dir(project, "run1")
    (old / "walk_001.png").write_bytes(b"should never come back")
    _marker(project, "run1", destination="frames", displaced=".agf-old-run1")

    code, doc = _trigger_sweep(project, run_cli)
    assert code == 4
    assert (dest / "walk_001.png").read_bytes() == b"correct current frame"


def test_sweep_touches_nothing_outside_the_two_reserved_prefixes(project, run_cli):
    """R69: 'the sweep deletes nothing outside the two reserved prefixes.'"""
    write_manifest(project, [])
    legit_file = project.drafts / "hero.png"
    legit_file.write_bytes(b"a real, finished draft asset")
    legit_dir = project.drafts / "loose_frames"
    legit_dir.mkdir()
    (legit_dir / "frame1.png").write_bytes(b"also real")

    # plus some genuine debris to repair, so the sweep does real work too
    old = _old_dir(project, "run1")
    (old / "walk_001.png").write_bytes(b"restored")
    _marker(project, "run1", destination="frames", displaced=".agf-old-run1")

    code, doc = _trigger_sweep(project, run_cli)
    assert code == 4
    assert legit_file.read_bytes() == b"a real, finished draft asset"
    assert (legit_dir / "frame1.png").read_bytes() == b"also real"


def test_sweep_also_removes_a_leftover_temporary_record_copy(project, run_cli):
    """
    R69's closing paragraph: a leftover .agf-tmp- record copy, beside the
    record file (never inside drafts, per R11), is swept too.
    """
    write_manifest(project, [])
    project.record_path.write_text(json.dumps({"version": 1, "entries": {}}))
    stray_record_copy = project.record_path.with_name(".agf-tmp-oldrun999")
    stray_record_copy.write_text(json.dumps({"version": 1, "entries": {"ghost": {}}}))

    code, doc = _trigger_sweep(project, run_cli)
    assert code == 4
    assert not stray_record_copy.exists()
    # the real record file itself is untouched by the sweep
    assert json.loads(project.record_path.read_text()) == {"version": 1, "entries": {}}


def test_r70_reserved_prefix_rejected_as_a_declared_output(project, run_cli):
    from conftest import image_model_entry

    entry = image_model_entry(name="e1", model="acme/x", output=".agf-tmp-sneaky.png")
    write_manifest(project, [entry])
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 3


def test_r70_reserved_prefix_rejected_as_a_file_reference(project, run_cli):
    """Even if a file happened to exist there, a reserved-prefix path is
    never resolvable as a file reference."""
    from conftest import image_model_entry

    reserved_dir = project.drafts / ".agf-tmp-not-really-a-run"
    reserved_dir.mkdir()
    (reserved_dir / "sneaky.png").write_bytes(b"x")
    entry = image_model_entry(name="e1", model="acme/x")
    entry["input_files"] = {"ref": "drafts:.agf-tmp-not-really-a-run/sneaky.png"}
    write_manifest(project, [entry])
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 3
