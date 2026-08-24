"""
`agf record <name>` — cli-v1 R23-R26.

Wrong implementation this file defends against, per test: a typo'd entry
name answered with "never generated" instead of being caught as an error, a
missing record file treated as an error instead of a legitimate "never
generated" answer, or the record command needing a credential it has no
business needing.
"""
from __future__ import annotations

import json

from conftest import (
    full_record_entry,
    image_model_entry,
    parse_single_json_document,
    write_manifest,
)


def test_r23_record_requires_exactly_one_positional_argument(project, run_cli):
    write_manifest(project, [image_model_entry(name="e1", model="acme/x")])
    code, out, _ = run_cli(["record"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 1


def test_r23_record_rejects_two_positional_arguments(project, run_cli):
    write_manifest(project, [image_model_entry(name="e1", model="acme/x")])
    code, out, _ = run_cli(["record", "e1", "e2"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 1


def test_r23_record_requires_no_credential(project, run_cli, monkeypatch):
    monkeypatch.delenv("REPLICATE_API_TOKEN", raising=False)
    write_manifest(project, [image_model_entry(name="e1", model="acme/x")])
    code, out, _ = run_cli(["record", "e1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0


def test_r24_typo_in_name_exits_4_not_answered_as_never_generated(project, run_cli):
    """R24: the name is validated against the manifest FIRST, so a typo is
    caught rather than silently answered with record: null."""
    write_manifest(project, [image_model_entry(name="correct_name", model="acme/x")])
    code, out, _ = run_cli(["record", "korrect_name"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 4
    assert doc["ok"] is False


def test_r25_valid_entry_never_generated_exits_0_with_null_record(project, run_cli):
    assert not project.record_path.exists()
    write_manifest(project, [image_model_entry(name="e1", model="acme/x")])
    code, out, _ = run_cli(["record", "e1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0
    assert doc["ok"] is True
    assert doc["record"] is None
    assert doc["command"] == "record"
    assert doc["name"] == "e1"


def test_r25_record_file_does_not_exist_at_all_still_exits_0(project, run_cli):
    """A record FILE that does not exist at all — distinct from an existing
    record that simply lacks this entry — is also exit 0, record: null."""
    assert not project.record_path.exists()
    write_manifest(project, [image_model_entry(name="e1", model="acme/x")])
    code, out, _ = run_cli(["record", "e1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0
    assert doc["record"] is None


def test_r25_valid_entry_present_in_existing_record_but_not_this_one(project, run_cli):
    """The record exists and has entries, but none named 'e2' — still
    exit 0, record: null, never an error."""
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
    write_manifest(
        project,
        [
            image_model_entry(name="e1", model=None, output="e1.png"),
            image_model_entry(name="e2", model="acme/x", output="e2.png"),
        ],
    )
    code, out, _ = run_cli(["record", "e2"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0
    assert doc["record"] is None


def test_r26_record_field_holds_the_stored_entry_verbatim(project, run_cli):
    stored_entry = full_record_entry(
        operation="model",
        type="image",
        model=None,
        model_version="sourceful/riverflow-2.0-pro:abcdef",
        prompt="a red fox in the snow",
        seed=42,
        inputs={"guidance": 7.5},
        input_files={"ref": "samples:hero.png"},
        output="e1.png",
        format="png",
    )
    project.record_path.write_text(json.dumps({"version": 1, "entries": {"e1": stored_entry}}))
    write_manifest(project, [image_model_entry(name="e1", model=None, output="e1.png")])
    code, out, _ = run_cli(["record", "e1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0
    assert doc["record"] == stored_entry
