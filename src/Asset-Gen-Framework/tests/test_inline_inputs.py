"""
`inline_inputs`: an optional boolean manifest field. When an entry sets it
`true`, every file named under that entry's `input_files` is sent to the
provider as a `data:<mime>;base64,<payload>` URI instead of being uploaded to
Replicate's file endpoint first (`agf.provider.upload` must never be called
for that entry). Absent or `false`, behaviour is unchanged: the file is
uploaded and the URL it hands back is sent instead.

The reason: a Replicate model (`lucataco/real-esrgan-video`) rejects a
file-endpoint URL for its video input and only accepts an inline data URI.
"""
from __future__ import annotations

import base64

import pytest

from conftest import (
    extract_frames_entry,
    image_model_entry,
    parse_single_json_document,
    png_bytes,
    sheet_assemble_entry,
    write_manifest,
)


def test_inline_inputs_true_sends_a_data_uri_and_never_uploads(project, run_cli, fake_provider):
    video_bytes = b"fake-mp4-bytes-not-a-real-video-\x00\x01\x02\xffend"
    (project.samples / "clip.mp4").write_bytes(video_bytes)
    entry = image_model_entry(
        name="img", input_files={"video": "samples:clip.mp4"}, inline_inputs=True
    )
    write_manifest(project, [entry])
    calls = fake_provider(run_result={"version": "v1", "seed": None, "outputs": [png_bytes()]})

    code, out, _ = run_cli(["generate", "img"] + project.config_args())

    assert code == 0, out
    # upload must never be reached for an inline_inputs entry.
    assert calls["upload"] == []
    expected_uri = "data:video/mp4;base64," + base64.b64encode(video_bytes).decode("ascii")
    assert calls["run"][0]["inputs"]["video"] == expected_uri


def test_inline_inputs_true_on_a_list_reference_inlines_each_file_with_its_own_mime(
    project, run_cli, fake_provider
):
    png_data = b"fake-png-bytes-AAA-\x00\x01"
    jpg_data = b"fake-jpg-bytes-BBB-\x02\x03"
    (project.samples / "ref.png").write_bytes(png_data)
    (project.samples / "ref.jpg").write_bytes(jpg_data)
    entry = image_model_entry(
        name="img",
        input_files={"init_images": ["samples:ref.png", "samples:ref.jpg"]},
        inline_inputs=True,
    )
    write_manifest(project, [entry])
    calls = fake_provider(run_result={"version": "v1", "seed": None, "outputs": [png_bytes()]})

    code, out, _ = run_cli(["generate", "img"] + project.config_args())

    assert code == 0, out
    # A list-valued input_files reference must inline every element too —
    # not just the single-reference branch — and never touch upload.
    assert calls["upload"] == []
    sent = calls["run"][0]["inputs"]["init_images"]
    assert sent == [
        "data:image/png;base64," + base64.b64encode(png_data).decode("ascii"),
        "data:image/jpeg;base64," + base64.b64encode(jpg_data).decode("ascii"),
    ]


@pytest.mark.parametrize(
    "entry_extra", [{}, {"inline_inputs": False}], ids=["field_absent", "field_explicit_false"]
)
def test_inline_inputs_absent_or_false_still_uploads(project, run_cli, fake_provider, entry_extra):
    video_bytes = b"fake-mp4-bytes-still-goes-through-upload"
    (project.samples / "clip.mp4").write_bytes(video_bytes)
    entry = image_model_entry(name="img", input_files={"video": "samples:clip.mp4"}, **entry_extra)
    write_manifest(project, [entry])
    calls = fake_provider(
        run_result={"version": "v1", "seed": None, "outputs": [png_bytes()]},
        upload_result="https://files.replicate.delivery/uploaded-clip",
    )

    code, out, _ = run_cli(["generate", "img"] + project.config_args())

    assert code == 0, out
    assert len(calls["upload"]) == 1
    assert calls["upload"][0]["path"].name == "clip.mp4"
    assert calls["run"][0]["inputs"]["video"] == "https://files.replicate.delivery/uploaded-clip"


@pytest.mark.parametrize("bad_value", ["yes", 1, ["true"]])
def test_non_boolean_inline_inputs_is_a_manifest_error(project, run_cli, bad_value):
    (project.samples / "clip.mp4").write_bytes(b"x")
    entry = image_model_entry(
        name="img", input_files={"video": "samples:clip.mp4"}, inline_inputs=bad_value
    )
    write_manifest(project, [entry])

    code, out, _ = run_cli(["list"] + project.config_args())

    assert code == 3, out
    assert "inline_inputs" in parse_single_json_document(out)["error"]["message"]


def test_inline_inputs_true_with_an_unsupported_extension_is_a_manifest_error(project, run_cli):
    """The inline encoder only knows png/mp4/jpeg/jpg/webp — a referenced file
    with any other extension must be refused when the manifest is loaded
    (`agf list`), not only discovered later when `generate` tries to encode
    it, and the error must name the offending file."""
    (project.samples / "clip.mov").write_bytes(b"x")
    entry = image_model_entry(
        name="img", input_files={"video": "samples:clip.mov"}, inline_inputs=True
    )
    write_manifest(project, [entry])

    code, out, _ = run_cli(["list"] + project.config_args())

    assert code == 3, out
    assert "clip.mov" in parse_single_json_document(out)["error"]["message"]


@pytest.mark.parametrize(
    "entry_builder", [sheet_assemble_entry, extract_frames_entry], ids=["assemble_sheet", "extract_frames"]
)
def test_inline_inputs_is_illegal_outside_a_model_operation(project, run_cli, entry_builder):
    """inline_inputs is a call-only field, exactly like model/prompt/inputs/
    input_files (CALL_FIELDS in agf/manifest.py) — illegal on any operation
    those are illegal on."""
    entry = entry_builder(name="e1")
    entry["inline_inputs"] = True
    write_manifest(project, [entry])

    code, out, _ = run_cli(["list"] + project.config_args())

    assert code == 3, out
    message = parse_single_json_document(out)["error"]["message"]
    assert "e1" in message
    assert "inline_inputs" in message
