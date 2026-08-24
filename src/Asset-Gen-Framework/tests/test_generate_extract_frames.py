"""
`agf generate` / `agf regenerate` on `operation: extract_frames` — cli-v1
R18, R20, R47, R62-R64, R66-R67, R71, R74. The one operation that produces
many files, driven live end to end through the R74 extraction boundary
(`agf.frames.extract` / `agf.frames.ExtractionError`) — the boundary exists
specifically so the multi-file commit (displace, rename, delete — R67) gets
real coverage instead of only the sweep's repair-fixture coverage.

Wrong implementation this file defends against, per test: a commit that
copies frames into the destination one at a time instead of a single
directory-level replace (invisible to every other test in this suite, since
every other live `generate` writes one file), a regenerate that leaves
orphaned frames from a larger previous set, a marker or staging remnant
that ends up nested inside the committed directory, a cleanup failure after
a successful rename being reported as a commit failure when R67 says it
must not be, or one entry's commit disturbing another's already-committed
directory.
"""
from __future__ import annotations

import json
import os
import stat
from pathlib import PurePosixPath

import pytest

from conftest import (
    CHECKS_KEYS,
    RECORD_ENTRY_KEYS,
    assert_checks_list_shape,
    extract_frames_entry,
    parse_single_json_document,
    png_bytes,
    write_manifest,
)


def _expected_basenames(template: str, count: int) -> list[str]:
    name = PurePosixPath(template).name
    return [name.format(n=i) for i in range(1, count + 1)]


def _reserved_paths(drafts_root):
    return [
        p
        for p in drafts_root.rglob(".agf-tmp-*")
    ] + [p for p in drafts_root.rglob(".agf-old-*")]


def test_r67_multi_file_generate_writes_a_real_directory(project, run_cli, fake_extraction):
    entry = extract_frames_entry(name="f1", output="frames/walk_{n:03d}.png")
    write_manifest(project, [entry])
    frame_bytes = [png_bytes(color=(i, 0, 0, 255)) for i in range(1, 5)]
    calls = fake_extraction(frames_result=frame_bytes)

    code, out, _ = run_cli(["generate", "f1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0
    assert doc["operation"] == "extract_frames"

    basenames = _expected_basenames(entry["output"], 4)
    assert isinstance(doc["output"], list)
    assert len(doc["output"]) == 4
    for item, expected_name, data in zip(doc["output"], basenames, frame_bytes):
        assert item["path"].endswith(expected_name)
        assert item["format"] == "png"
        assert item["bytes"] == len(data)
        assert item["replaced"] is False
        checks = item["checks"]
        assert set(checks.keys()) == CHECKS_KEYS
        assert checks["format"] == "pass"
        assert checks["layout"] == "skipped"  # type: image, not sprite_sheet
        assert checks["frame_size"] == "skipped"  # not assemble_sheet
        assert checks["frame_count"] == "skipped"  # entry declared no frame_count
        assert checks["output_count"] == "skipped"  # not a provider call

    committed = project.drafts / "frames"
    assert sorted(p.name for p in committed.iterdir()) == basenames
    assert _reserved_paths(project.drafts) == []

    assert len(calls["extract"]) == 1
    assert calls["extract"][0]["source_path"].samefile(project.samples / "video.mp4")
    assert calls["extract"][0]["format"] == "png"


def test_r47_multi_file_record_written_correctly(project, run_cli, fake_extraction):
    entry = extract_frames_entry(name="f1", output="frames/walk_{n:03d}.png")
    write_manifest(project, [entry])
    fake_extraction(frames_result=[png_bytes() for _ in range(3)])
    code, out, _ = run_cli(["generate", "f1"] + project.config_args())
    assert code == 0

    written = json.loads(project.record_path.read_text())["entries"]["f1"]
    assert set(written.keys()) == RECORD_ENTRY_KEYS
    assert written["operation"] == "extract_frames"
    assert written["type"] == "image"
    # output is the declared TEMPLATE, never expanded to a real filename (R47/R26)
    assert written["output"] == "frames/walk_{n:03d}.png"
    assert written["source"] == "samples:video.mp4"
    # every field illegal for extract_frames is present and null (R47, R51)
    assert written["model"] is None
    assert written["model_version"] is None
    assert written["prompt"] is None
    assert written["prompt_key"] is None
    assert written["seed"] is None
    assert written["inputs"] is None
    assert written["input_files"] is None
    assert written["frames"] is None
    # entry declared no frame_count/frame_size/layout
    assert written["frame_count"] is None
    assert written["frame_size"] is None
    assert written["layout"] is None


def test_r64_declared_frame_count_matching_passes_the_check(project, run_cli, fake_extraction):
    entry = extract_frames_entry(name="f1", output="frames/walk_{n:03d}.png", frame_count=4)
    write_manifest(project, [entry])
    fake_extraction(frames_result=[png_bytes() for _ in range(4)])
    code, out, _ = run_cli(["generate", "f1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0
    for item in doc["output"]:
        assert item["checks"]["frame_count"] == "pass"
    record = json.loads(project.record_path.read_text())["entries"]["f1"]
    assert record["frame_count"] == 4  # the declaration, copied as written (R47)


def test_r64_declared_frame_count_mismatch_exits_7_and_commits_nothing(project, run_cli, fake_extraction):
    entry = extract_frames_entry(name="f1", output="frames/walk_{n:03d}.png", frame_count=5)
    write_manifest(project, [entry])
    fake_extraction(frames_result=[png_bytes() for _ in range(4)])  # video yields 4, not 5
    code, out, _ = run_cli(["generate", "f1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 7
    checks_list = assert_checks_list_shape(doc["error"]["checks"])
    # "the same files ... that the success document's output list would have
    # named had every check passed" (R71) — the 4 actually-extracted frames.
    assert len(checks_list) == 4
    for element in checks_list:
        assert element["checks"]["frame_count"] == "fail"
    assert not (project.drafts / "frames").exists()
    assert not project.record_path.exists()


def test_r18_collision_refusal_for_a_template_entry_via_generate(project, run_cli):
    """
    R18: for a template entry, ANY existing file matching the template's
    shape refuses generate, before the operation runs at all — the default
    network/extraction guard (conftest.py) enforces the "before the
    operation" half: if generate reached extraction first, that guard would
    raise and this test would see exit 11, not 8.
    """
    (project.drafts / "frames").mkdir()
    (project.drafts / "frames" / "walk_007.png").write_bytes(b"pre-existing frame, untouched")
    entry = extract_frames_entry(name="f1", output="frames/walk_{n:03d}.png")
    write_manifest(project, [entry])

    code, out, _ = run_cli(["generate", "f1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 8
    assert "regenerate" in doc["error"]["remedy"]
    assert (project.drafts / "frames" / "walk_007.png").read_bytes() == b"pre-existing frame, untouched"
    assert _reserved_paths(project.drafts) == []


def test_r20_regenerate_more_frames_over_fewer_reports_replaced_correctly(project, run_cli, fake_extraction):
    """
    R20's own worked example: regenerating twelve frames over an existing
    nine reports nine `true` and three `false`.
    """
    entry = extract_frames_entry(name="f1", output="frames/walk_{n:03d}.png")
    write_manifest(project, [entry])
    fake_extraction(frames_result=[png_bytes() for _ in range(9)])
    first = run_cli(["generate", "f1"] + project.config_args())
    assert first[0] == 0

    fake_extraction(frames_result=[png_bytes() for _ in range(12)])
    code, out, _ = run_cli(["regenerate", "f1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0
    assert len(doc["output"]) == 12
    replaced_flags = [item["replaced"] for item in doc["output"]]
    assert replaced_flags[:9] == [True] * 9
    assert replaced_flags[9:] == [False] * 3


def test_r20_regenerate_fewer_frames_over_more_leaves_no_stale_files(project, run_cli, fake_extraction):
    """
    R20/R67: the reverse case — nine frames over an existing twelve leaves
    nine, not nine-plus-three-stale, because the destination directory is
    replaced whole rather than written into file by file.
    """
    entry = extract_frames_entry(name="f1", output="frames/walk_{n:03d}.png")
    write_manifest(project, [entry])
    fake_extraction(frames_result=[png_bytes() for _ in range(12)])
    first = run_cli(["generate", "f1"] + project.config_args())
    assert first[0] == 0
    assert sorted(p.name for p in (project.drafts / "frames").iterdir()) == _expected_basenames(
        entry["output"], 12
    )

    fake_extraction(frames_result=[png_bytes() for _ in range(9)])
    code, out, _ = run_cli(["regenerate", "f1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0

    final_files = sorted(p.name for p in (project.drafts / "frames").iterdir())
    assert final_files == _expected_basenames(entry["output"], 9)
    assert "walk_010.png" not in final_files
    assert "walk_011.png" not in final_files
    assert "walk_012.png" not in final_files
    assert _reserved_paths(project.drafts) == []


def test_r67_nothing_of_the_framework_remains_inside_the_committed_directory(project, run_cli, fake_extraction):
    entry = extract_frames_entry(name="f1", output="frames/walk_{n:03d}.png")
    write_manifest(project, [entry])
    fake_extraction(frames_result=[png_bytes() for _ in range(5)])
    code, out, _ = run_cli(["generate", "f1"] + project.config_args())
    assert code == 0

    committed = project.drafts / "frames"
    reserved_inside = [
        p for p in committed.iterdir() if p.name.startswith(".agf-tmp-") or p.name.startswith(".agf-old-")
    ]
    assert reserved_inside == []
    assert _reserved_paths(project.drafts) == []


@pytest.mark.skipif(os.name != "posix" or os.geteuid() == 0, reason="relies on POSIX permission enforcement, not meaningful as root")
def test_r67_cleanup_failure_after_successful_rename_is_not_a_commit_failure(project, run_cli, fake_extraction):
    """
    R67: 'A failure in steps 4, 5 or 6 is not a commit failure... The run
    stops the cleanup where it failed, leaves the remainder for the sweep,
    writes the record, and exits 0.' Simulated black-box, with no hook into
    the implementation: the pre-existing destination directory holds an
    unreadable nested subdirectory, so *it* can still be renamed whole as
    the displace step (2) requires only write permission on its *parent*,
    but deleting it afterward (step 4) cannot finish, because deleting a
    directory's contents requires read/execute on every directory in it,
    including the locked one.
    """
    entry = extract_frames_entry(name="f1", output="frames/walk_{n:03d}.png")
    write_manifest(project, [entry])

    destination = project.drafts / "frames"
    destination.mkdir()
    (destination / "walk_001.png").write_bytes(b"old frame content")
    locked_subdir = destination / "locked"
    locked_subdir.mkdir()
    (locked_subdir / "inner.bin").write_bytes(b"unreachable once locked")
    os.chmod(locked_subdir, 0)  # no read/execute: blocks traversal into it

    try:
        fake_extraction(frames_result=[png_bytes(color=(9, 9, 9, 255)) for _ in range(2)])
        code, out, _ = run_cli(["regenerate", "f1"] + project.config_args())
        doc = parse_single_json_document(out)

        assert code == 0, doc  # NOT exit 10 — the rename itself succeeded
        assert doc["ok"] is True

        # the new content really did land at the destination
        new_files = sorted(p.name for p in destination.iterdir())
        assert new_files == ["walk_001.png", "walk_002.png"]

        # the record was written despite the leftover cleanup debris
        record = json.loads(project.record_path.read_text())
        assert "f1" in record["entries"]

        # the displaced copy the failed step-4 deletion could not finish
        # removing is real debris left for the next sweep — not silently
        # invented, not silently dropped, and the run still exits 0 rather
        # than reporting this as a commit failure.
        leftover_old_dirs = list(project.drafts.glob(".agf-old-*"))
        assert len(leftover_old_dirs) == 1
    finally:
        # restore permissions so pytest can clean up tmp_path afterward
        for p in project.drafts.rglob("locked"):
            os.chmod(p, 0o755)


def test_cross_entry_isolation_during_a_live_commit(project, run_cli, fake_extraction):
    """
    Runtime counterpart to the manifest-time containment rules (R63):
    committing one entry's directory must never disturb another entry's
    already-committed directory, even when the two are generated back to
    back in the same run of the suite.
    """
    entry_a = extract_frames_entry(name="a", output="frames_a/walk_{n:03d}.png")
    entry_b = extract_frames_entry(name="b", output="frames_b/run_{n:03d}.png")
    write_manifest(project, [entry_a, entry_b])

    fake_extraction(frames_result=[png_bytes(color=(1, 0, 0, 255)) for _ in range(3)])
    code_a, out_a, _ = run_cli(["generate", "a"] + project.config_args())
    assert code_a == 0

    a_files_before = {
        p.name: p.read_bytes() for p in (project.drafts / "frames_a").iterdir()
    }

    fake_extraction(frames_result=[png_bytes(color=(0, 1, 0, 255)) for _ in range(5)])
    code_b, out_b, _ = run_cli(["generate", "b"] + project.config_args())
    assert code_b == 0

    a_files_after = {
        p.name: p.read_bytes() for p in (project.drafts / "frames_a").iterdir()
    }
    assert a_files_after == a_files_before

    b_files = sorted(p.name for p in (project.drafts / "frames_b").iterdir())
    assert b_files == _expected_basenames(entry_b["output"], 5)
    assert _reserved_paths(project.drafts) == []
