"""
An `input_files` value may be a list of references: a model input that takes
several files (init or reference images) is declared as a list and reaches
the model as a list of uploaded URLs, in the order written.
"""
from __future__ import annotations

from conftest import image_model_entry, parse_single_json_document, png_bytes, write_manifest


def test_a_list_of_references_uploads_each_and_passes_a_list(project, run_cli, fake_provider):
    (project.samples / "a.png").write_bytes(png_bytes(color=(1, 0, 0, 255)))
    (project.samples / "b.png").write_bytes(png_bytes(color=(2, 0, 0, 255)))
    entry = image_model_entry(
        name="img", input_files={"init_images": ["samples:a.png", "samples:b.png"], "mask": "samples:a.png"}
    )
    write_manifest(project, [entry])
    calls = fake_provider(run_result={"version": "v1", "seed": None, "outputs": [png_bytes()]})

    code, out, _ = run_cli(["generate", "img"] + project.config_args())
    assert code == 0, out
    uploaded = [c["path"].name for c in calls["upload"]]
    assert uploaded == ["a.png", "b.png", "a.png"]
    sent = calls["run"][0]["inputs"]
    assert isinstance(sent["init_images"], list) and len(sent["init_images"]) == 2
    assert isinstance(sent["mask"], str)


def test_an_empty_list_is_a_manifest_error(project, run_cli):
    write_manifest(project, [image_model_entry(name="img", input_files={"init_images": []})])
    code, out, _ = run_cli(["list"] + project.config_args())
    assert code == 3
    assert "must not be empty" in parse_single_json_document(out)["error"]["message"]


def test_a_missing_file_inside_the_list_is_a_manifest_error(project, run_cli):
    (project.samples / "a.png").write_bytes(png_bytes())
    write_manifest(
        project, [image_model_entry(name="img", input_files={"init_images": ["samples:a.png", "samples:nope.png"]})]
    )
    code, out, _ = run_cli(["list"] + project.config_args())
    assert code == 3
    assert "nope.png" in parse_single_json_document(out)["error"]["message"]
