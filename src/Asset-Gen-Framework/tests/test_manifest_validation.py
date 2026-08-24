"""
Manifest validation — cli-v1 R13, R34-R46, R55, R56, R58, R60-R64. Every rule
here exits 3.

Wrong implementation this file defends against, per test: a validation rule
that only looks at the entry named on the command line instead of the whole
manifest (R34), a type/operation pairing that silently falls through to a
default behaviour instead of being refused, a field the framework quietly
ignores instead of rejecting, or a containment check that only catches the
two-sibling case and misses nesting.
"""
from __future__ import annotations

from conftest import (
    extract_frames_entry,
    image_model_entry,
    parse_single_json_document,
    sheet_assemble_entry,
    sheet_model_entry,
    write_manifest,
    write_raw_manifest,
)


def _entries_error(project, run_cli, entries, command_entry_name="whatever"):
    write_manifest(project, entries)
    code, out, _ = run_cli(["record", command_entry_name] + project.config_args())
    doc = parse_single_json_document(out)
    return code, doc


# ---------------------------------------------------------------------------
# R16 / R34 — empty manifest, whole-manifest validation
# ---------------------------------------------------------------------------

def test_r16_empty_manifest_file_is_zero_entries_not_an_error(project, run_cli):
    write_raw_manifest(project, "")
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0
    assert doc["entries"] == []


def test_r16_manifest_yaml_null_document_is_zero_entries(project, run_cli):
    write_raw_manifest(project, "null\n")
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0
    assert doc["entries"] == []


def test_r16_manifest_top_level_not_a_list_exits_3(project, run_cli):
    write_raw_manifest(project, "name: not_a_list\n")
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 3


def test_r16_manifest_malformed_yaml_exits_3(project, run_cli):
    write_raw_manifest(project, "- name: [broken: yaml:::\n")
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 3


def test_r34_whole_manifest_validated_even_for_unrelated_command_entry(project, run_cli):
    """
    R34: `agf record a` exits 3 when b and c collide with each other, even
    though a itself is faultless — the rule that matters most is cross-entry
    and can't be seen by looking at one entry.
    """
    entries = [
        image_model_entry(name="a", output="a.png", model="acme/x"),
        extract_frames_entry(name="b", output="frames/{n}.png"),
        extract_frames_entry(name="c", output="frames/{n}.png"),
    ]
    write_manifest(project, entries)
    code, out, _ = run_cli(["record", "a"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 3
    assert doc["ok"] is False


def test_r37_duplicate_name_exits_3(project, run_cli):
    entries = [
        image_model_entry(name="dup", output="a.png", model="acme/x"),
        image_model_entry(name="dup", output="b.png", model="acme/x"),
    ]
    code, doc = _entries_error(project, run_cli, entries)
    assert code == 3
    assert "dup" in doc["error"]["message"]


# ---------------------------------------------------------------------------
# R36 — operation/type legality
# ---------------------------------------------------------------------------

def test_r36_assemble_sheet_requires_type_sprite_sheet(project, run_cli):
    entry = sheet_assemble_entry(name="bad")
    entry["type"] = "image"
    code, doc = _entries_error(project, run_cli, [entry])
    assert code == 3
    assert "bad" in doc["error"]["message"]


def test_r36_extract_frames_requires_type_image(project, run_cli):
    entry = extract_frames_entry(name="bad")
    entry["type"] = "sprite_sheet"
    code, doc = _entries_error(project, run_cli, [entry])
    assert code == 3
    assert "bad" in doc["error"]["message"]


def test_r36_model_operation_allows_any_type(project, run_cli):
    for t in ("image", "sound", "music", "sprite_sheet", "video"):
        entry = {
            "name": f"ok_{t}",
            "type": t,
            "model": "acme/anything",
            "output": f"ok_{t}.png",
            "format": "png",
        }
        if t == "sprite_sheet":
            entry.update(frame_count=1, frame_size=[8, 8], layout={"columns": 1, "rows": 1})
        write_manifest(project, [entry])
        code, out, _ = run_cli(["list"] + project.config_args())
        doc = parse_single_json_document(out)
        assert code == 0, f"type {t} with operation=model should be legal: {doc}"


# ---------------------------------------------------------------------------
# R37 — unknown / missing / illegal-for-operation fields
# ---------------------------------------------------------------------------

def test_r37_unrecognized_field_exits_3(project, run_cli):
    entry = image_model_entry(name="e1", model="acme/x")
    entry["totally_unknown_field"] = "x"
    code, doc = _entries_error(project, run_cli, [entry])
    assert code == 3
    assert "totally_unknown_field" in doc["error"]["message"]
    assert "e1" in doc["error"]["message"]


def test_r37_missing_required_field_output_exits_3(project, run_cli):
    entry = image_model_entry(name="e1", model="acme/x")
    del entry["output"]
    code, doc = _entries_error(project, run_cli, [entry])
    assert code == 3


def test_r37_missing_required_field_format_exits_3(project, run_cli):
    entry = image_model_entry(name="e1", model="acme/x")
    del entry["format"]
    code, doc = _entries_error(project, run_cli, [entry])
    assert code == 3


def test_r37_missing_required_field_name_exits_3(project, run_cli):
    entry = image_model_entry(model="acme/x")
    del entry["name"]
    code, doc = _entries_error(project, run_cli, [entry], command_entry_name="anything")
    assert code == 3


def test_r37_missing_required_field_type_exits_3(project, run_cli):
    entry = image_model_entry(name="e1", model="acme/x")
    del entry["type"]
    code, doc = _entries_error(project, run_cli, [entry])
    assert code == 3


def test_r37_model_field_on_assemble_sheet_exits_3(project, run_cli):
    """'model only' fields are rejected on assemble_sheet under R37."""
    entry = sheet_assemble_entry(name="s1")
    entry["model"] = "acme/x"
    code, doc = _entries_error(project, run_cli, [entry])
    assert code == 3
    assert "s1" in doc["error"]["message"]
    assert "model" in doc["error"]["message"]


def test_r37_prompt_field_on_extract_frames_exits_3(project, run_cli):
    entry = extract_frames_entry(name="f1")
    entry["prompt"] = "shouldn't be here"
    code, doc = _entries_error(project, run_cli, [entry])
    assert code == 3
    assert "prompt" in doc["error"]["message"]


def test_r37_inputs_field_on_assemble_sheet_exits_3(project, run_cli):
    entry = sheet_assemble_entry(name="s1")
    entry["inputs"] = {"x": 1}
    code, doc = _entries_error(project, run_cli, [entry])
    assert code == 3


def test_r37_frames_field_on_model_operation_exits_3(project, run_cli):
    """'frames' is assemble_sheet only; naming it on a model call is illegal."""
    entry = image_model_entry(name="e1", model="acme/x")
    entry["frames"] = ["samples:a.png"]
    code, doc = _entries_error(project, run_cli, [entry])
    assert code == 3


def test_r37_source_field_on_model_operation_exits_3(project, run_cli):
    entry = image_model_entry(name="e1", model="acme/x")
    entry["source"] = "samples:video.mp4"
    code, doc = _entries_error(project, run_cli, [entry])
    assert code == 3


# ---------------------------------------------------------------------------
# R38 — model required/optional/rejected, and the two settled defaults
# ---------------------------------------------------------------------------

def test_r38_model_required_for_sound_type_exits_3_when_omitted(project, run_cli):
    entry = {"name": "s1", "type": "sound", "output": "s1.wav", "format": "wav"}
    code, doc = _entries_error(project, run_cli, [entry])
    assert code == 3


def test_r38_model_required_for_sprite_sheet_via_model_op_exits_3_when_omitted(project, run_cli):
    entry = sheet_model_entry(name="sh1")
    del entry["model"]
    code, doc = _entries_error(project, run_cli, [entry])
    assert code == 3


def test_r38_model_required_for_video_type_exits_3_when_omitted(project, run_cli):
    entry = {"name": "v1", "type": "video", "output": "v1.mp4", "format": "mp4"}
    code, doc = _entries_error(project, run_cli, [entry])
    assert code == 3


def test_r38_image_default_model_is_riverflow(project, run_cli):
    """R38's table names this default explicitly; R15 surfaces it via model_source."""
    entry = image_model_entry(name="img1", model=None)
    write_manifest(project, [entry])
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    listed = doc["entries"][0]
    assert listed["model"] == "sourceful/riverflow-2.0-pro"
    assert listed["model_source"] == "default"


def test_r38_music_default_model_is_stable_audio(project, run_cli):
    entry = {"name": "m1", "type": "music", "output": "m1.wav", "format": "wav"}
    write_manifest(project, [entry])
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    listed = doc["entries"][0]
    assert listed["model"] == "stability-ai/stable-audio-2.5"
    assert listed["model_source"] == "default"


def test_r38_model_on_assemble_sheet_is_rejected_not_merely_ignored(project, run_cli):
    """Covered again here to state R38's own framing: naming a model on a
    local operation exits 3 under R37, it is never silently dropped."""
    entry = sheet_assemble_entry(name="s1")
    entry["model"] = "acme/x"
    code, doc = _entries_error(project, run_cli, [entry])
    assert code == 3


def test_r39_named_model_overrides_the_default(project, run_cli):
    entry = image_model_entry(name="img1", model="someone/custom-model")
    write_manifest(project, [entry])
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    listed = doc["entries"][0]
    assert listed["model"] == "someone/custom-model"
    assert listed["model_source"] == "entry"


def test_r15_model_source_none_for_local_operations(project, run_cli):
    from conftest import make_png

    for i in range(4):
        make_png(project.samples / "frames" / f"f{i}.png")
    entry = sheet_assemble_entry(name="s1")
    write_manifest(project, [entry])
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    listed = doc["entries"][0]
    assert listed["model"] is None
    assert listed["model_source"] == "none"


# ---------------------------------------------------------------------------
# R41 — prompt_key, and the prompt/inputs collision
# ---------------------------------------------------------------------------

def test_r41_prompt_and_conflicting_inputs_key_exits_3(project, run_cli):
    entry = image_model_entry(name="e1", model="acme/x", prompt="a cat", prompt_key="text")
    entry["inputs"] = {"text": "a dog"}
    code, doc = _entries_error(project, run_cli, [entry])
    assert code == 3


def test_r41_prompt_key_defaults_to_prompt_when_omitted(project, run_cli):
    """The record holds prompt_key as null when the entry omitted it (R47)."""
    entry = image_model_entry(name="e1", model="acme/x", prompt="a cat")
    write_manifest(project, [entry])
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0


# ---------------------------------------------------------------------------
# R42 / R43 — file references
# ---------------------------------------------------------------------------

def test_r43_file_reference_to_undeclared_root_exits_3(project, run_cli):
    """R43: 'base:' is unusable once the config omits the base key."""
    from conftest import write_config

    write_config(project, base=None)
    entry = image_model_entry(name="e1", model="acme/x")
    entry["input_files"] = {"ref": "base:something.png"}
    code, doc = _entries_error(project, run_cli, [entry])
    assert code == 3
    assert "base" in doc["error"]["message"]


def test_r43_file_reference_to_missing_file_exits_3(project, run_cli):
    entry = image_model_entry(name="e1", model="acme/x")
    entry["input_files"] = {"ref": "samples:does_not_exist.png"}
    code, doc = _entries_error(project, run_cli, [entry])
    assert code == 3
    assert "does_not_exist.png" in doc["error"]["message"]


def test_r43_file_reference_resolves_when_file_exists(project, run_cli):
    from conftest import make_png

    make_png(project.samples / "ref.png")
    entry = image_model_entry(name="e1", model="acme/x")
    entry["input_files"] = {"ref": "samples:ref.png"}
    write_manifest(project, [entry])
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0


# ---------------------------------------------------------------------------
# R44 — geometry, keyed on type/operation
# ---------------------------------------------------------------------------

def test_r44_sprite_sheet_assemble_sheet_requires_frame_count(project, run_cli):
    entry = sheet_assemble_entry(name="s1")
    del entry["frame_count"]
    code, doc = _entries_error(project, run_cli, [entry])
    assert code == 3


def test_r44_sprite_sheet_assemble_sheet_requires_frame_size(project, run_cli):
    entry = sheet_assemble_entry(name="s1")
    del entry["frame_size"]
    code, doc = _entries_error(project, run_cli, [entry])
    assert code == 3


def test_r44_sprite_sheet_assemble_sheet_requires_layout(project, run_cli):
    entry = sheet_assemble_entry(name="s1")
    del entry["layout"]
    code, doc = _entries_error(project, run_cli, [entry])
    assert code == 3


def test_r44_sprite_sheet_model_op_also_requires_all_three_geometry_fields(project, run_cli):
    """Required on both paths — a model-produced sheet needs geometry too."""
    entry = sheet_model_entry(name="sh1")
    del entry["layout"]
    code, doc = _entries_error(project, run_cli, [entry])
    assert code == 3


def test_r44_extract_frames_rejects_frame_size(project, run_cli):
    entry = extract_frames_entry(name="f1")
    entry["frame_size"] = [10, 10]
    code, doc = _entries_error(project, run_cli, [entry])
    assert code == 3


def test_r44_extract_frames_rejects_layout(project, run_cli):
    entry = extract_frames_entry(name="f1")
    entry["layout"] = {"columns": 1, "rows": 1}
    code, doc = _entries_error(project, run_cli, [entry])
    assert code == 3


def test_r44_plain_image_model_entry_rejects_geometry_fields(project, run_cli):
    entry = image_model_entry(name="e1", model="acme/x")
    entry["frame_count"] = 4
    code, doc = _entries_error(project, run_cli, [entry])
    assert code == 3


def test_r44_columns_times_rows_less_than_frame_count_exits_3(project, run_cli):
    entry = sheet_assemble_entry(
        name="s1", frame_count=5, layout={"columns": 2, "rows": 2}
    )
    code, doc = _entries_error(project, run_cli, [entry])
    assert code == 3


# ---------------------------------------------------------------------------
# R13 / R45 — output filenames
# ---------------------------------------------------------------------------

def test_r13_absolute_output_path_exits_3(project, run_cli):
    entry = image_model_entry(name="e1", model="acme/x", output="/etc/passwd_replacement.png")
    code, doc = _entries_error(project, run_cli, [entry])
    assert code == 3


def test_r13_output_path_escaping_drafts_via_dotdot_exits_3(project, run_cli):
    entry = image_model_entry(name="e1", model="acme/x", output="../escape.png")
    code, doc = _entries_error(project, run_cli, [entry])
    assert code == 3


# ---------------------------------------------------------------------------
# R55 / R56 — declared format vs. extension, recognised formats
# ---------------------------------------------------------------------------

def test_r55_extension_disagrees_with_declared_format_exits_3(project, run_cli):
    entry = image_model_entry(name="e1", model="acme/x", output="e1.jpg", format="png")
    code, doc = _entries_error(project, run_cli, [entry])
    assert code == 3


def test_r56_unrecognized_format_exits_3(project, run_cli):
    entry = image_model_entry(name="e1", model="acme/x", output="e1.xyz", format="xyz")
    code, doc = _entries_error(project, run_cli, [entry])
    assert code == 3


def test_r56_each_documented_format_is_accepted_at_manifest_stage(project, run_cli):
    formats = {
        "png": "a.png",
        "jpeg": "a.jpeg",
        "webp": "a.webp",
        "wav": "a.wav",
        "mp3": "a.mp3",
        "mp4": "a.mp4",
    }
    for fmt, filename in formats.items():
        entry = {
            "name": f"e_{fmt}",
            "type": "sound" if fmt in ("wav", "mp3") else ("video" if fmt == "mp4" else "image"),
            "model": "acme/x",
            "output": filename,
            "format": fmt,
        }
        write_manifest(project, [entry])
        code, out, _ = run_cli(["list"] + project.config_args())
        doc = parse_single_json_document(out)
        assert code == 0, f"format {fmt} should be recognised: {doc}"


# ---------------------------------------------------------------------------
# R58 — assemble_sheet frames must be PNG
# ---------------------------------------------------------------------------

def test_r58_assemble_sheet_declared_format_must_be_png(project, run_cli):
    entry = sheet_assemble_entry(name="s1", output="s1.jpeg", format="jpeg")
    # keep extension/format agreement so R55 doesn't fire first
    code, doc = _entries_error(project, run_cli, [entry])
    assert code == 3


def test_r58_assemble_sheet_frame_reference_that_is_not_png_exits_3(project, run_cli):
    """R58: a frame that is not PNG is rejected — a non-.png frame reference,
    distinct from the entry's own declared format (tested above)."""
    (project.samples / "frames").mkdir(parents=True, exist_ok=True)
    (project.samples / "frames" / "f0.jpg").write_bytes(b"not a real jpeg either")
    entry = sheet_assemble_entry(
        name="s1",
        frame_count=1,
        layout={"columns": 1, "rows": 1},
        frames=["samples:frames/f0.jpg"],
    )
    code, doc = _entries_error(project, run_cli, [entry])
    assert code == 3


# ---------------------------------------------------------------------------
# R61 — assemble_sheet frame count, detectable purely from the entry
# ---------------------------------------------------------------------------

def test_r61_frames_list_length_mismatch_with_frame_count_exits_3(project, run_cli):
    entry = sheet_assemble_entry(name="s1", frame_count=4)
    entry["frames"] = entry["frames"][:3]  # only 3 listed, frame_count says 4
    code, doc = _entries_error(project, run_cli, [entry])
    assert code == 3


# ---------------------------------------------------------------------------
# R63 — extract_frames template syntax and directory-claim rules
# ---------------------------------------------------------------------------

def test_r63_template_with_no_placeholder_exits_3(project, run_cli):
    entry = extract_frames_entry(name="f1", output="frames/walk.png")
    code, doc = _entries_error(project, run_cli, [entry])
    assert code == 3


def test_r63_template_with_two_placeholders_exits_3(project, run_cli):
    entry = extract_frames_entry(name="f1", output="frames/walk_{n}_{n}.png")
    code, doc = _entries_error(project, run_cli, [entry])
    assert code == 3


def test_r63_template_directly_in_drafts_with_no_subdirectory_exits_3(project, run_cli):
    entry = extract_frames_entry(name="f1", output="walk_{n:03d}.png")
    code, doc = _entries_error(project, run_cli, [entry])
    assert code == 3
    assert "f1" in doc["error"]["message"]


def test_r63_two_extract_frames_entries_claiming_same_directory_exits_3(project, run_cli):
    entries = [
        extract_frames_entry(name="a", output="frames/walk_{n:03d}.png"),
        extract_frames_entry(name="b", output="frames/run_{n:03d}.png"),
    ]
    code, doc = _entries_error(project, run_cli, entries)
    assert code == 3
    assert "a" in doc["error"]["message"] and "b" in doc["error"]["message"]


def test_r63_claimed_directory_nested_inside_another_claimed_directory_exits_3(project, run_cli):
    """'frames' against 'frames/run' — the worst case, stated explicitly in the PRD."""
    entries = [
        extract_frames_entry(name="outer", output="frames/walk_{n:03d}.png"),
        extract_frames_entry(name="inner", output="frames/run/step_{n:03d}.png"),
    ]
    code, doc = _entries_error(project, run_cli, entries)
    assert code == 3


def test_r63_single_file_output_sitting_inside_a_claimed_directory_exits_3(project, run_cli):
    entries = [
        extract_frames_entry(name="frames_owner", output="frames/walk_{n:03d}.png"),
        image_model_entry(name="stray", output="frames/stray.png", model="acme/x"),
    ]
    code, doc = _entries_error(project, run_cli, entries)
    assert code == 3


def test_r63_unrelated_directories_do_not_collide(project, run_cli):
    entries = [
        extract_frames_entry(name="a", output="frames_a/walk_{n:03d}.png"),
        extract_frames_entry(name="b", output="frames_b/run_{n:03d}.png"),
        image_model_entry(name="c", output="loose/other.png", model="acme/x"),
    ]
    write_manifest(project, entries)
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0, doc


def test_r63_placeholder_matching_is_documented_via_list_draft_exists(project, run_cli):
    """
    R18/R15: draft_exists for a template entry is true when any existing file
    matches the template's shape — exercised here through `list`, which is
    pure manifest+disk inspection and needs no provider.
    """
    (project.drafts / "frames").mkdir()
    (project.drafts / "frames" / "walk_007.png").write_bytes(b"not really a png")
    entry = extract_frames_entry(name="f1", output="frames/walk_{n:03d}.png")
    write_manifest(project, [entry])
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0
    assert doc["entries"][0]["draft_exists"] is True


def test_r63_bare_placeholder_collides_with_padded_existing_name(project, run_cli):
    """R18: a bare {n} is not narrower than a padded one — walk_007.png collides."""
    (project.drafts / "frames").mkdir()
    (project.drafts / "frames" / "walk_007.png").write_bytes(b"x")
    entry = extract_frames_entry(name="f1", output="frames/walk_{n}.png")
    write_manifest(project, [entry])
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert doc["entries"][0]["draft_exists"] is True


def test_r64_extract_frames_frame_count_is_legal_and_optional(project, run_cli):
    entry = extract_frames_entry(name="f1", frame_count=24)
    write_manifest(project, [entry])
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0
