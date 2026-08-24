"""
`agf list` — cli-v1 R14-R16.

Wrong implementation this file defends against, per test: list requiring a
credential it has no business needing, list reordering entries instead of
preserving manifest order, or draft_exists/has_record reporting a static
"false" instead of actually inspecting disk and the record file.
"""
from __future__ import annotations

import json

from conftest import (
    full_record_entry,
    image_model_entry,
    parse_single_json_document,
    sheet_assemble_entry,
    write_manifest,
)


def test_r14_list_rejects_a_positional_argument(project, run_cli):
    write_manifest(project, [])
    code, out, _ = run_cli(["list", "unexpected"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 1


def test_r14_list_requires_no_credential(project, run_cli, monkeypatch):
    monkeypatch.delenv("REPLICATE_API_TOKEN", raising=False)
    write_manifest(project, [image_model_entry(name="e1", model="acme/x")])
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0


def test_r15_list_preserves_manifest_order(project, run_cli):
    entries = [
        image_model_entry(name="zeta", model="acme/x", output="zeta.png"),
        image_model_entry(name="alpha", model="acme/x", output="alpha.png"),
        image_model_entry(name="mid", model="acme/x", output="mid.png"),
    ]
    write_manifest(project, entries)
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    names = [e["name"] for e in doc["entries"]]
    assert names == ["zeta", "alpha", "mid"]


def test_r15_entry_shape_has_all_documented_keys(project, run_cli):
    write_manifest(project, [image_model_entry(name="e1", model="acme/x", output="e1.png")])
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    entry = doc["entries"][0]
    expected_keys = {
        "name",
        "type",
        "operation",
        "model",
        "model_source",
        "output",
        "format",
        "draft_exists",
        "has_record",
    }
    assert expected_keys.issubset(entry.keys())


def test_r15_output_is_the_declared_filename_never_expanded(project, run_cli):
    entry = {
        "name": "f1",
        "type": "image",
        "operation": "extract_frames",
        "output": "frames/walk_{n:03d}.png",
        "format": "png",
        "source": "samples:video.mp4",
    }
    write_manifest(project, [entry])
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert doc["entries"][0]["output"] == "frames/walk_{n:03d}.png"


def test_r15_draft_exists_true_for_single_file_entry_when_file_present(project, run_cli):
    (project.drafts / "e1.png").write_bytes(b"x")
    write_manifest(project, [image_model_entry(name="e1", model="acme/x", output="e1.png")])
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert doc["entries"][0]["draft_exists"] is True


def test_r15_draft_exists_false_for_single_file_entry_when_absent(project, run_cli):
    write_manifest(project, [image_model_entry(name="e1", model="acme/x", output="e1.png")])
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert doc["entries"][0]["draft_exists"] is False


def test_r15_has_record_true_when_record_holds_the_entry(project, run_cli):
    project.record_path.write_text(
        json.dumps(
            {
                "version": 1,
                "entries": {
                    "e1": full_record_entry(
                        operation="model",
                        type="image",
                        model=None,
                        model_version="sourceful/riverflow-2.0-pro:abc",
                        prompt="a cat",
                        inputs={},
                        input_files={},
                        output="e1.png",
                        format="png",
                    )
                },
            }
        )
    )
    write_manifest(project, [image_model_entry(name="e1", model=None, output="e1.png")])
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert doc["entries"][0]["has_record"] is True


def test_r15_has_record_false_when_record_file_absent(project, run_cli):
    assert not project.record_path.exists()
    write_manifest(project, [image_model_entry(name="e1", model="acme/x", output="e1.png")])
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert doc["entries"][0]["has_record"] is False


def test_r15_operation_defaults_to_model_when_entry_omits_it(project, run_cli):
    entry = image_model_entry(name="e1", model="acme/x")
    assert "operation" not in entry
    write_manifest(project, [entry])
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert doc["entries"][0]["operation"] == "model"
