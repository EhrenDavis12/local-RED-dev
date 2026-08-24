"""
`agf generate` / `agf regenerate` on `operation: assemble_sheet` — cli-v1
R17-R22, R57, R60, R61, R71, R19/R20 result shape. Chosen as the live,
executable path for these requirements because it needs no provider stub:
assembling a sheet from real on-disk PNG frames is pure local image work.

Wrong implementation this file defends against, per test: generate silently
overwriting an existing draft instead of refusing (that is regenerate's job
alone), a regenerate that reports every file as replaced regardless of
whether it actually overwrote something, a sheet assembled at the wrong
pixel size, or a checks object whose key set changes shape between entries.
"""
from __future__ import annotations

from PIL import Image

from conftest import (
    assert_checks_list_shape,
    make_png,
    parse_single_json_document,
    sheet_assemble_entry,
    write_manifest,
)


def _make_frames(project, count=4, size=(10, 10)):
    for i in range(count):
        make_png(project.samples / "frames" / f"f{i}.png", size=size)
    return [f"samples:frames/f{i}.png" for i in range(count)]


def test_r19_generate_success_document_shape(project, run_cli):
    frames = _make_frames(project)
    entry = sheet_assemble_entry(name="sheet1", output="sheet1.png", frames=frames)
    write_manifest(project, [entry])
    code, out, _ = run_cli(["generate", "sheet1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0
    assert doc["ok"] is True
    assert doc["command"] == "generate"
    assert doc["name"] == "sheet1"
    assert isinstance(doc["output"], list)
    assert len(doc["output"]) == 1
    file_doc = doc["output"][0]
    assert file_doc["format"] == "png"
    assert file_doc["replaced"] is False
    assert file_doc["bytes"] == (project.drafts / "sheet1.png").stat().st_size
    assert file_doc["bytes"] > 0
    assert set(file_doc["checks"].keys()) == {
        "format",
        "layout",
        "frame_size",
        "frame_count",
        "output_count",
    }
    # local operation: no model call at all
    assert doc["model_version"] is None
    assert doc["seed"] is None


def test_r71_checks_table_for_assemble_sheet_success(project, run_cli):
    """
    R71's table: for assemble_sheet, format/layout/frame_size run and pass;
    frame_count and output_count are properties this operation never
    produces (frame_count is a manifest-time check here per R61, and
    output_count only ever runs for a provider call) — both 'skipped'.
    """
    frames = _make_frames(project)
    entry = sheet_assemble_entry(name="sheet1", output="sheet1.png", frames=frames)
    write_manifest(project, [entry])
    code, out, _ = run_cli(["generate", "sheet1"] + project.config_args())
    doc = parse_single_json_document(out)
    checks = doc["output"][0]["checks"]
    assert checks["format"] == "pass"
    assert checks["layout"] == "pass"
    assert checks["frame_size"] == "pass"
    assert checks["frame_count"] == "skipped"
    assert checks["output_count"] == "skipped"


def test_r57_sheet_pixel_dimensions_match_columns_rows_times_frame_size(project, run_cli):
    frames = _make_frames(project, count=4, size=(10, 10))
    entry = sheet_assemble_entry(
        name="sheet1",
        output="sheet1.png",
        frames=frames,
        frame_count=4,
        frame_size=(10, 10),
        layout={"columns": 2, "rows": 2},
    )
    write_manifest(project, [entry])
    code, out, _ = run_cli(["generate", "sheet1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0
    with Image.open(project.drafts / "sheet1.png") as img:
        assert img.size == (20, 20)


def test_r61_frame_pixel_size_mismatch_exits_7_and_commits_nothing(project, run_cli):
    make_png(project.samples / "frames" / "f0.png", size=(10, 10))
    make_png(project.samples / "frames" / "f1.png", size=(5, 5))  # wrong size
    make_png(project.samples / "frames" / "f2.png", size=(10, 10))
    make_png(project.samples / "frames" / "f3.png", size=(10, 10))
    entry = sheet_assemble_entry(
        name="sheet1",
        output="sheet1.png",
        frames=[f"samples:frames/f{i}.png" for i in range(4)],
    )
    write_manifest(project, [entry])
    code, out, _ = run_cli(["generate", "sheet1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 7
    checks_list = assert_checks_list_shape(doc["error"]["checks"])
    assert len(checks_list) == 1  # assemble_sheet has exactly one declared output
    result_checks = checks_list[0]["checks"]
    assert result_checks["frame_size"] == "fail"
    # the checks that passed are still present, not trimmed to the failing
    # one (R71): the canvas is built at the declared layout/frame_size
    # regardless of what is pasted into it, and it is still valid PNG bytes.
    assert result_checks["format"] == "pass"
    assert result_checks["layout"] == "pass"
    assert result_checks["frame_count"] == "skipped"
    assert result_checks["output_count"] == "skipped"
    assert not (project.drafts / "sheet1.png").exists()


def test_r18_generate_refuses_when_output_already_exists(project, run_cli):
    frames = _make_frames(project)
    entry = sheet_assemble_entry(name="sheet1", output="sheet1.png", frames=frames)
    write_manifest(project, [entry])
    (project.drafts / "sheet1.png").write_bytes(b"pretend previous draft")
    code, out, _ = run_cli(["generate", "sheet1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 8
    assert "regenerate" in doc["error"]["remedy"]
    # untouched
    assert (project.drafts / "sheet1.png").read_bytes() == b"pretend previous draft"


def test_r17_generate_has_no_overwrite_flag(project, run_cli):
    """R17: there is no option that makes generate overwrite."""
    frames = _make_frames(project)
    entry = sheet_assemble_entry(name="sheet1", output="sheet1.png", frames=frames)
    write_manifest(project, [entry])
    (project.drafts / "sheet1.png").write_bytes(b"existing")
    code, out, _ = run_cli(["generate", "sheet1", "--force"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 1  # unknown option, not a successful overwrite


def test_r20_regenerate_replaces_existing_draft_and_reports_replaced_true(project, run_cli):
    frames = _make_frames(project)
    entry = sheet_assemble_entry(name="sheet1", output="sheet1.png", frames=frames)
    write_manifest(project, [entry])
    (project.drafts / "sheet1.png").write_bytes(b"stale previous draft")
    code, out, _ = run_cli(["regenerate", "sheet1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0
    assert doc["output"][0]["replaced"] is True
    with Image.open(project.drafts / "sheet1.png") as img:
        assert img.size == (20, 20)


def test_r20_regenerate_succeeds_with_no_prior_draft_and_reports_replaced_false(project, run_cli):
    frames = _make_frames(project)
    entry = sheet_assemble_entry(name="sheet1", output="sheet1.png", frames=frames)
    write_manifest(project, [entry])
    assert not (project.drafts / "sheet1.png").exists()
    code, out, _ = run_cli(["regenerate", "sheet1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0
    assert doc["output"][0]["replaced"] is False


def test_r21_regenerate_does_not_accept_a_prompt_override(project, run_cli):
    frames = _make_frames(project)
    entry = sheet_assemble_entry(name="sheet1", output="sheet1.png", frames=frames)
    write_manifest(project, [entry])
    code, out, _ = run_cli(
        ["regenerate", "sheet1", "--prompt", "something else"] + project.config_args()
    )
    doc = parse_single_json_document(out)
    assert code == 1  # unrecognised option


def test_r22_no_bulk_generate_via_multiple_names(project, run_cli):
    frames = _make_frames(project)
    entries = [
        sheet_assemble_entry(name="sheet1", output="sheet1.png", frames=frames),
        sheet_assemble_entry(name="sheet2", output="sheet2.png", frames=frames),
    ]
    write_manifest(project, entries)
    code, out, _ = run_cli(["generate", "sheet1,sheet2"] + project.config_args())
    doc = parse_single_json_document(out)
    # "sheet1,sheet2" is not a name in the manifest — no comma-list expansion
    assert code == 4


def test_r22_no_bulk_generate_via_all_sentinel(project, run_cli):
    frames = _make_frames(project)
    entry = sheet_assemble_entry(name="sheet1", output="sheet1.png", frames=frames)
    write_manifest(project, [entry])
    code, out, _ = run_cli(["generate", "all"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 4


def test_r46_no_sidecar_file_is_written_alongside_the_sheet(project, run_cli):
    frames = _make_frames(project)
    entry = sheet_assemble_entry(name="sheet1", output="sheet1.png", frames=frames)
    write_manifest(project, [entry])
    code, out, _ = run_cli(["generate", "sheet1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0
    assert sorted(p.name for p in project.drafts.iterdir()) == ["sheet1.png"]


def test_r19_replaced_frame_layout_leftover_cells_are_transparent(project, run_cli):
    """
    R44: columns x rows > frame_count leaves leftover cells fully
    transparent — the sheet is the full grid, not cropped.
    """
    frames = _make_frames(project, count=3)
    entry = sheet_assemble_entry(
        name="sheet1",
        output="sheet1.png",
        frames=frames,
        frame_count=3,
        frame_size=(10, 10),
        layout={"columns": 2, "rows": 2},
    )
    write_manifest(project, [entry])
    code, out, _ = run_cli(["generate", "sheet1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0
    with Image.open(project.drafts / "sheet1.png") as img:
        assert img.size == (20, 20)
        rgba = img.convert("RGBA")
        # last cell (bottom-right, row-major with only 3 frames) is empty
        leftover_pixel = rgba.getpixel((15, 15))
        assert leftover_pixel[3] == 0  # fully transparent alpha
