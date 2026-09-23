"""
`agf generate` on `operation: model` — cli-v1 R29-R33, R38, R41, R42, R47,
R49, R50, R54, R59, R75, via the stubbed provider boundary (see
conftest.py for the R74/R75-specified agf.provider contract).

Wrong implementation this file defends against, per test: the credential
read from anywhere but the one environment variable, the credential leaking
into the record or stdout, a bare model name recorded unpinned, a seed the
framework invented on its own, a prompt sent under the literal key "prompt"
when the entry asked for a different one, or a provider returning two files
for one declared output being silently narrowed to "just take the first".
"""
from __future__ import annotations

import json

from conftest import (
    RECORD_ENTRY_KEYS,
    assert_checks_list_shape,
    full_record_entry,
    image_model_entry,
    make_png,
    parse_single_json_document,
    png_bytes,
    sheet_model_entry,
    write_manifest,
)


def test_r29_credential_is_read_from_replicate_api_token_and_passed_through(project, run_cli, fake_provider, monkeypatch):
    monkeypatch.setenv("REPLICATE_API_TOKEN", "sekrit-token-value")
    write_manifest(project, [image_model_entry(name="e1", model="acme/gen")])
    calls = fake_provider(run_result={"version": "acme/gen:pinned1", "seed": None, "outputs": [png_bytes()]})
    code, out, _ = run_cli(["generate", "e1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0
    assert calls["run"][0]["api_token"] == "sekrit-token-value"


def test_r30_local_operation_runs_without_any_credential(project, run_cli, monkeypatch):
    from conftest import sheet_assemble_entry

    monkeypatch.delenv("REPLICATE_API_TOKEN", raising=False)
    for i in range(4):
        make_png(project.samples / "frames" / f"f{i}.png")
    entry = sheet_assemble_entry(name="s1")
    write_manifest(project, [entry])
    code, out, _ = run_cli(["generate", "s1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0


def test_r31_credential_never_appears_in_stdout_stderr_or_record(project, run_cli, fake_provider, monkeypatch):
    secret = "sekrit-value-must-not-leak-8675309"
    monkeypatch.setenv("REPLICATE_API_TOKEN", secret)
    write_manifest(project, [image_model_entry(name="e1", model="acme/gen")])
    fake_provider(run_result={"version": "acme/gen:pinned1", "seed": None, "outputs": [png_bytes()]})
    code, out, err = run_cli(["generate", "e1"] + project.config_args())
    assert secret not in out
    assert secret not in err
    assert secret not in project.record_path.read_text()


def test_r49_bare_model_name_recorded_as_the_pinned_version_returned(project, run_cli, fake_provider, monkeypatch):
    monkeypatch.setenv("REPLICATE_API_TOKEN", "token")
    write_manifest(project, [image_model_entry(name="e1", model="acme/gen")])
    fake_provider(run_result={"version": "acme/gen:9f8e7d6c", "seed": None, "outputs": [png_bytes()]})
    code, out, _ = run_cli(["generate", "e1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0
    assert doc["model_version"] == "acme/gen:9f8e7d6c"
    record = json.loads(project.record_path.read_text())
    assert record["entries"]["e1"]["model_version"] == "acme/gen:9f8e7d6c"
    # declared model is preserved as written, never overwritten with the pin
    assert record["entries"]["e1"]["model"] == "acme/gen"


def test_r38_record_model_is_null_when_the_default_applied(project, run_cli, fake_provider, monkeypatch):
    """R47: a null declared `model` beside a pinned model_version says the
    framework's default supplied it — the same fact list reports as
    model_source: default."""
    monkeypatch.setenv("REPLICATE_API_TOKEN", "token")
    entry = image_model_entry(name="e1", model=None)
    write_manifest(project, [entry])
    fake_provider(
        run_result={"version": "sourceful/riverflow-2.0-pro:abc123", "seed": None, "outputs": [png_bytes()]}
    )
    code, out, _ = run_cli(["generate", "e1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0
    record = json.loads(project.record_path.read_text())
    assert record["entries"]["e1"]["model"] is None
    assert record["entries"]["e1"]["model_version"] == "sourceful/riverflow-2.0-pro:abc123"


def test_r41_prompt_merged_under_default_prompt_key(project, run_cli, fake_provider, monkeypatch):
    monkeypatch.setenv("REPLICATE_API_TOKEN", "token")
    entry = image_model_entry(name="e1", model="acme/gen", prompt="a red fox")
    write_manifest(project, [entry])
    calls = fake_provider(run_result={"version": "acme/gen:v1", "seed": None, "outputs": [png_bytes()]})
    code, out, _ = run_cli(["generate", "e1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0
    assert calls["run"][0]["inputs"]["prompt"] == "a red fox"


def test_r41_prompt_merged_under_declared_prompt_key(project, run_cli, fake_provider, monkeypatch):
    monkeypatch.setenv("REPLICATE_API_TOKEN", "token")
    entry = image_model_entry(name="e1", model="acme/gen", prompt="a red fox", prompt_key="text")
    write_manifest(project, [entry])
    calls = fake_provider(run_result={"version": "acme/gen:v1", "seed": None, "outputs": [png_bytes()]})
    code, out, _ = run_cli(["generate", "e1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0
    assert calls["run"][0]["inputs"]["text"] == "a red fox"
    assert "prompt" not in calls["run"][0]["inputs"]


def test_r41_record_holds_declared_prompt_key_null_when_entry_omitted_it(project, run_cli, fake_provider, monkeypatch):
    monkeypatch.setenv("REPLICATE_API_TOKEN", "token")
    entry = image_model_entry(name="e1", model="acme/gen", prompt="a red fox")
    assert "prompt_key" not in entry
    write_manifest(project, [entry])
    fake_provider(run_result={"version": "acme/gen:v1", "seed": None, "outputs": [png_bytes()]})
    run_ok = run_cli(["generate", "e1"] + project.config_args())
    assert run_ok[0] == 0
    record = json.loads(project.record_path.read_text())
    assert record["entries"]["e1"]["prompt_key"] is None


def test_r42_input_files_uploaded_and_url_sent_never_a_local_path(project, run_cli, fake_provider, monkeypatch):
    monkeypatch.setenv("REPLICATE_API_TOKEN", "token")
    make_png(project.samples / "ref.png")
    entry = image_model_entry(name="e1", model="acme/gen")
    entry["input_files"] = {"image": "samples:ref.png"}
    write_manifest(project, [entry])
    calls = fake_provider(
        run_result={"version": "acme/gen:v1", "seed": None, "outputs": [png_bytes()]},
        upload_result="https://files.replicate.delivery/abc123",
    )
    code, out, _ = run_cli(["generate", "e1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0
    assert len(calls["upload"]) == 1
    assert calls["upload"][0]["path"].samefile(project.samples / "ref.png")
    sent_inputs = calls["run"][0]["inputs"]
    assert sent_inputs["image"] == "https://files.replicate.delivery/abc123"


def test_r42_record_stores_the_reference_string_never_the_url(project, run_cli, fake_provider, monkeypatch):
    monkeypatch.setenv("REPLICATE_API_TOKEN", "token")
    make_png(project.samples / "ref.png")
    entry = image_model_entry(name="e1", model="acme/gen")
    entry["input_files"] = {"image": "samples:ref.png"}
    write_manifest(project, [entry])
    fake_provider(
        run_result={"version": "acme/gen:v1", "seed": None, "outputs": [png_bytes()]},
        upload_result="https://files.replicate.delivery/abc123",
    )
    code, out, _ = run_cli(["generate", "e1"] + project.config_args())
    assert code == 0
    record = json.loads(project.record_path.read_text())
    assert record["entries"]["e1"]["input_files"] == {"image": "samples:ref.png"}
    assert "https://files.replicate.delivery" not in project.record_path.read_text()


def test_r50_seed_recorded_when_provider_returns_one_and_entry_declared_none(project, run_cli, fake_provider, monkeypatch):
    monkeypatch.setenv("REPLICATE_API_TOKEN", "token")
    entry = image_model_entry(name="e1", model="acme/gen")
    write_manifest(project, [entry])
    fake_provider(run_result={"version": "acme/gen:v1", "seed": 4242, "outputs": [png_bytes()]})
    code, out, _ = run_cli(["generate", "e1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0
    assert doc["seed"] == 4242
    record = json.loads(project.record_path.read_text())
    assert record["entries"]["e1"]["seed"] == 4242


def test_r50_seed_is_null_when_entry_declares_none_and_provider_returns_none(project, run_cli, fake_provider, monkeypatch):
    monkeypatch.setenv("REPLICATE_API_TOKEN", "token")
    entry = image_model_entry(name="e1", model="acme/gen")
    write_manifest(project, [entry])
    fake_provider(run_result={"version": "acme/gen:v1", "seed": None, "outputs": [png_bytes()]})
    code, out, _ = run_cli(["generate", "e1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert doc["seed"] is None
    record = json.loads(project.record_path.read_text())
    assert record["entries"]["e1"]["seed"] is None


def test_r50_entry_declared_seed_is_recorded_like_any_other_field(project, run_cli, fake_provider, monkeypatch):
    monkeypatch.setenv("REPLICATE_API_TOKEN", "token")
    entry = image_model_entry(name="e1", model="acme/gen")
    entry["inputs"] = {"seed": 7}
    write_manifest(project, [entry])
    fake_provider(run_result={"version": "acme/gen:v1", "seed": None, "outputs": [png_bytes()]})
    code, out, _ = run_cli(["generate", "e1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0
    record = json.loads(project.record_path.read_text())
    assert record["entries"]["e1"]["seed"] == 7


def test_r54_correct_bytes_pass_format_check(project, run_cli, fake_provider, monkeypatch):
    monkeypatch.setenv("REPLICATE_API_TOKEN", "token")
    entry = image_model_entry(name="e1", model="acme/gen", output="e1.png", format="png")
    write_manifest(project, [entry])
    fake_provider(run_result={"version": "acme/gen:v1", "seed": None, "outputs": [png_bytes()]})
    code, out, _ = run_cli(["generate", "e1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0
    assert doc["output"][0]["checks"]["format"] == "pass"
    assert doc["output"][0]["checks"]["output_count"] == "pass"


def test_r47_generate_writes_the_closed_sixteen_key_record_shape(project, run_cli, fake_provider, monkeypatch):
    """
    R47: a record entry's keys are exactly the seventeen it names, every
    time — asserted here on what `generate` itself writes, not on a
    hand-crafted fixture, so an implementation that stashes extra fields
    (say, the raw provider response) alongside the correct ones is caught.
    """
    monkeypatch.setenv("REPLICATE_API_TOKEN", "token")
    entry = image_model_entry(name="e1", model="acme/gen", prompt="a fox")
    write_manifest(project, [entry])
    fake_provider(run_result={"version": "acme/gen:v1", "seed": None, "outputs": [png_bytes()]})
    code, out, _ = run_cli(["generate", "e1"] + project.config_args())
    assert code == 0
    written = json.loads(project.record_path.read_text())["entries"]["e1"]
    assert set(written.keys()) == RECORD_ENTRY_KEYS
    # geometry and local-operation fields are illegal for a plain model op
    # and must still be present, carrying null (R47).
    assert written["frame_count"] is None
    assert written["frame_size"] is None
    assert written["layout"] is None
    assert written["frames"] is None
    assert written["source"] is None


def test_r40_arbitrary_inputs_pass_through_untouched(project, run_cli, fake_provider, monkeypatch):
    """R40: inputs are passed through untouched — not renamed, reordered,
    coerced, or filtered, however arbitrary or nested."""
    monkeypatch.setenv("REPLICATE_API_TOKEN", "token")
    entry = image_model_entry(name="e1", model="acme/gen", prompt="a fox")
    entry["inputs"] = {"guidance_scale": 7.5, "steps": 30, "nested": {"a": [1, 2, 3]}}
    write_manifest(project, [entry])
    calls = fake_provider(run_result={"version": "acme/gen:v1", "seed": None, "outputs": [png_bytes()]})
    code, out, _ = run_cli(["generate", "e1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0
    sent = calls["run"][0]["inputs"]
    assert sent["guidance_scale"] == 7.5
    assert sent["steps"] == 30
    assert sent["nested"] == {"a": [1, 2, 3]}


def test_r71_checks_table_for_plain_image_model_entry(project, run_cli, fake_provider, monkeypatch):
    monkeypatch.setenv("REPLICATE_API_TOKEN", "token")
    entry = image_model_entry(name="e1", model="acme/gen", output="e1.png", format="png")
    write_manifest(project, [entry])
    fake_provider(run_result={"version": "acme/gen:v1", "seed": None, "outputs": [png_bytes()]})
    code, out, _ = run_cli(["generate", "e1"] + project.config_args())
    doc = parse_single_json_document(out)
    checks = doc["output"][0]["checks"]
    assert checks == {
        "format": "pass",
        "layout": "skipped",
        "frame_size": "skipped",
        "frame_count": "skipped",
        "output_count": "pass",
    }


def test_r57_model_returned_sheet_with_correct_dimensions_passes_layout_check(project, run_cli, fake_provider, monkeypatch):
    monkeypatch.setenv("REPLICATE_API_TOKEN", "token")
    entry = sheet_model_entry(name="sh1", output="sh1.png", frame_count=4, frame_size=(10, 10), layout={"columns": 2, "rows": 2})
    write_manifest(project, [entry])
    correct_sheet = png_bytes(size=(20, 20))
    fake_provider(run_result={"version": "acme/sheetmaker:v1", "seed": None, "outputs": [correct_sheet]})
    code, out, _ = run_cli(["generate", "sh1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0
    checks = doc["output"][0]["checks"]
    assert checks["layout"] == "pass"
    assert checks["frame_size"] == "skipped"  # R71: frame_size only runs for assemble_sheet
    assert checks["frame_count"] == "skipped"
    assert checks["output_count"] == "pass"


def test_r57_model_returned_sheet_with_wrong_dimensions_exits_7_and_commits_nothing(project, run_cli, fake_provider, monkeypatch):
    """
    R57: this matters most on the pixel-art path, where the model does its
    own framing — a wrongly-sized returned sheet is a mismatch, not a
    result to accept.
    """
    monkeypatch.setenv("REPLICATE_API_TOKEN", "token")
    entry = sheet_model_entry(name="sh1", output="sh1.png", frame_count=4, frame_size=(10, 10), layout={"columns": 2, "rows": 2})
    write_manifest(project, [entry])
    wrong_sheet = png_bytes(size=(19, 20))  # one pixel short
    fake_provider(run_result={"version": "acme/sheetmaker:v1", "seed": None, "outputs": [wrong_sheet]})
    code, out, _ = run_cli(["generate", "sh1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 7
    checks_list = assert_checks_list_shape(doc["error"]["checks"])
    assert len(checks_list) == 1
    result_checks = checks_list[0]["checks"]
    assert result_checks["layout"] == "fail"
    # not trimmed to the failing key: the bytes really were a valid PNG,
    # just the wrong size, and that is a distinct fact from the layout fail.
    assert result_checks["format"] == "pass"
    assert result_checks["frame_size"] == "skipped"
    assert result_checks["frame_count"] == "skipped"
    assert result_checks["output_count"] == "pass"
    assert not (project.drafts / "sh1.png").exists()


def test_r59_provider_returning_two_files_for_one_output_exits_7_and_commits_nothing(project, run_cli, fake_provider, monkeypatch):
    monkeypatch.setenv("REPLICATE_API_TOKEN", "token")
    entry = image_model_entry(name="e1", model="acme/gen", output="e1.png", format="png")
    write_manifest(project, [entry])
    fake_provider(run_result={"version": "acme/gen:v1", "seed": None, "outputs": [png_bytes(), png_bytes()]})
    code, out, _ = run_cli(["generate", "e1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 7
    checks_list = assert_checks_list_shape(doc["error"]["checks"])
    # R71: "the list holds one element, for the entry's single declared
    # output" — even though the provider returned two files.
    assert len(checks_list) == 1
    assert checks_list[0]["checks"]["output_count"] == "fail"
    assert not (project.drafts / "e1.png").exists()
    assert not project.record_path.exists()  # R53: untouched on any failure
