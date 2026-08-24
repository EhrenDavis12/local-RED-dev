"""
The record file — cli-v1 R47-R53. Written as a complete new copy renamed
over the old, holding the entry's declarations plus exactly two resolved
values, with file references stored as the reference string and never
resolved paths, URLs, or bytes.

Wrong implementation this file defends against, per test: a record write
that edits the file in place (so a kill mid-write can leave a truncated
file), a regenerate that only appends or touches the one entry and drops
every other asset's provenance, an entry pruned the moment its name leaves
the manifest, or a record touched even though the run that would have
produced it failed.
"""
from __future__ import annotations

import json

from conftest import make_png, parse_single_json_document, sheet_assemble_entry, write_manifest


def _make_frames(project, prefix, count=4, size=(10, 10)):
    for i in range(count):
        make_png(project.samples / prefix / f"f{i}.png", size=size)
    return [f"samples:{prefix}/f{i}.png" for i in range(count)]


def test_r53_record_untouched_when_run_fails(project, run_cli):
    frames = _make_frames(project, "a")
    entry_a = sheet_assemble_entry(name="a", output="a.png", frames=frames)
    write_manifest(project, [entry_a])
    code, out, _ = run_cli(["generate", "a"] + project.config_args())
    assert code == 0
    before = project.record_path.read_text()

    # Now force a failing regenerate of the same entry.
    bad_frames = _make_frames(project, "a_bad", size=(1, 1))
    entry_a_bad_size = sheet_assemble_entry(name="a", output="a.png", frames=bad_frames)
    write_manifest(project, [entry_a_bad_size])
    code, out, _ = run_cli(["regenerate", "a"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 7
    after = project.record_path.read_text()
    assert before == after


def test_r48_regenerate_replaces_the_one_entry_in_place_no_history_kept(project, run_cli):
    frames = _make_frames(project, "a")
    entry_a = sheet_assemble_entry(name="a", output="a.png", frames=frames)
    write_manifest(project, [entry_a])
    run_cli(["generate", "a"] + project.config_args())
    first_record = json.loads(project.record_path.read_text())["entries"]["a"]

    new_frames = _make_frames(project, "a2", size=(20, 20))
    entry_a2 = sheet_assemble_entry(
        name="a", output="a.png", frames=new_frames, frame_size=(20, 20)
    )
    write_manifest(project, [entry_a2])
    run_cli(["regenerate", "a"] + project.config_args())
    record = json.loads(project.record_path.read_text())
    assert list(record["entries"].keys()) == ["a"]  # one entry, not two, no history array
    assert record["entries"]["a"] != first_record


def test_r53_write_is_a_full_copy_every_other_entrys_provenance_survives(project, run_cli):
    """
    R53: the record is written as a complete new copy of the WHOLE record —
    generating B must not lose what A was last asked for.
    """
    frames_a = _make_frames(project, "a")
    frames_b = _make_frames(project, "b")
    entry_a = sheet_assemble_entry(name="a", output="a.png", frames=frames_a)
    entry_b = sheet_assemble_entry(name="b", output="b.png", frames=frames_b)
    write_manifest(project, [entry_a, entry_b])
    run_cli(["generate", "a"] + project.config_args())
    run_cli(["generate", "b"] + project.config_args())
    record = json.loads(project.record_path.read_text())
    assert set(record["entries"].keys()) == {"a", "b"}


def test_r52_record_never_prunes_an_entry_whose_manifest_entry_is_gone(project, run_cli):
    frames_a = _make_frames(project, "a")
    frames_b = _make_frames(project, "b")
    entry_a = sheet_assemble_entry(name="a", output="a.png", frames=frames_a)
    entry_b = sheet_assemble_entry(name="b", output="b.png", frames=frames_b)
    write_manifest(project, [entry_a, entry_b])
    run_cli(["generate", "a"] + project.config_args())
    run_cli(["generate", "b"] + project.config_args())

    # b is dropped from the manifest entirely, then a fresh write happens for a.
    write_manifest(project, [entry_a])
    code, out, _ = run_cli(["regenerate", "a"] + project.config_args())
    assert code == 0
    record = json.loads(project.record_path.read_text())
    assert "b" in record["entries"], "R52: an entry must survive its manifest entry disappearing"


def test_r53_temporary_record_copy_never_survives_a_completed_run(project, run_cli):
    frames = _make_frames(project, "a")
    entry_a = sheet_assemble_entry(name="a", output="a.png", frames=frames)
    write_manifest(project, [entry_a])
    code, out, _ = run_cli(["generate", "a"] + project.config_args())
    assert code == 0
    siblings = list(project.record_path.parent.iterdir())
    tmp_leftovers = [p for p in siblings if p.name.startswith(".agf-tmp-")]
    assert tmp_leftovers == []


def test_r51_local_operation_record_entry_has_call_fields_null(project, run_cli):
    frames = _make_frames(project, "a")
    entry_a = sheet_assemble_entry(name="a", output="a.png", frames=frames)
    write_manifest(project, [entry_a])
    code, out, _ = run_cli(["generate", "a"] + project.config_args())
    assert code == 0
    record = json.loads(project.record_path.read_text())["entries"]["a"]
    assert record["model"] is None
    assert record["model_version"] is None
    assert record["prompt"] is None
    assert record["prompt_key"] is None
    assert record["seed"] is None
    assert record["inputs"] is None


def test_r51_local_operation_record_stores_frames_as_reference_strings(project, run_cli):
    frames = _make_frames(project, "a")
    entry_a = sheet_assemble_entry(name="a", output="a.png", frames=frames)
    write_manifest(project, [entry_a])
    code, out, _ = run_cli(["generate", "a"] + project.config_args())
    assert code == 0
    record = json.loads(project.record_path.read_text())["entries"]["a"]
    assert record["frames"] == frames


def test_r47_record_output_field_is_the_declared_filename_never_an_expansion(project, run_cli):
    frames = _make_frames(project, "a")
    entry_a = sheet_assemble_entry(name="a", output="a.png", frames=frames)
    write_manifest(project, [entry_a])
    run_cli(["generate", "a"] + project.config_args())
    record = json.loads(project.record_path.read_text())["entries"]["a"]
    assert record["output"] == "a.png"


def test_r47_no_timestamp_field_anywhere_in_a_record_entry(project, run_cli):
    frames = _make_frames(project, "a")
    entry_a = sheet_assemble_entry(name="a", output="a.png", frames=frames)
    write_manifest(project, [entry_a])
    run_cli(["generate", "a"] + project.config_args())
    record = json.loads(project.record_path.read_text())["entries"]["a"]
    time_like = {k for k in record if "time" in k.lower() or "date" in k.lower() or k in ("created", "updated")}
    assert time_like == set()


def test_r47_record_has_version_key_at_top_level(project, run_cli):
    frames = _make_frames(project, "a")
    entry_a = sheet_assemble_entry(name="a", output="a.png", frames=frames)
    write_manifest(project, [entry_a])
    run_cli(["generate", "a"] + project.config_args())
    record = json.loads(project.record_path.read_text())
    assert record["version"] == 1
    assert "entries" in record
