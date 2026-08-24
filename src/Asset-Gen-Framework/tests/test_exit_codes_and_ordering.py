"""
Exit codes and validation order — cli-v1 R27, R28.

R27 fixes a strict validation order specifically so the exit code for a
broken invocation never depends on which check happens to run first in a
given implementation. Each ordering test below sets up two simultaneous
violations and asserts the earlier-stage one wins — the wrong implementation
this defends against is exit codes that depend on incidental check order
rather than the fixed one R27 specifies.
"""
from __future__ import annotations

import fcntl

from conftest import (
    assert_checks_list_shape,
    extract_frames_entry,
    image_model_entry,
    parse_single_json_document,
    sheet_assemble_entry,
    write_manifest,
    write_raw_manifest,
)


# ---------------------------------------------------------------------------
# R28 — one test per exit code
# ---------------------------------------------------------------------------

def test_exit_0_success(project, run_cli):
    write_manifest(project, [])
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0
    assert doc["ok"] is True


def test_exit_1_usage_wrong_argument_count(project, run_cli):
    write_manifest(project, [])
    code, out, _ = run_cli(["generate", "a", "b"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 1
    assert doc["ok"] is False


def test_exit_2_config(run_cli, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    code, out, _ = run_cli(["list"])
    doc = parse_single_json_document(out)
    assert code == 2


def test_exit_3_manifest(project, run_cli):
    write_raw_manifest(project, "not_a_list: 1\n")
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 3


def test_exit_4_no_entry_by_that_name(project, run_cli):
    write_manifest(project, [image_model_entry(name="real", model="acme/x")])
    code, out, _ = run_cli(["record", "does-not-exist"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 4


def test_exit_5_credential_absent(project, run_cli, monkeypatch):
    monkeypatch.delenv("REPLICATE_API_TOKEN", raising=False)
    write_manifest(project, [image_model_entry(name="e1", model="acme/x")])
    code, out, _ = run_cli(["generate", "e1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 5
    assert "REPLICATE_API_TOKEN" in doc["error"]["message"]


def test_exit_6_provider_prediction_failed(project, run_cli, fake_provider, monkeypatch):
    monkeypatch.setenv("REPLICATE_API_TOKEN", "test-token")
    write_manifest(project, [image_model_entry(name="e1", model="acme/x")])

    def _raise_provider_error(*a):
        from agf.provider import ProviderError

        raise ProviderError("the model rejected the request: bad input")

    fake_provider(run_side_effect=_raise_provider_error)
    code, out, _ = run_cli(["generate", "e1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 6
    assert "bad input" in doc["error"]["message"]


def test_exit_7_check_failed_wrong_format_bytes(project, run_cli, fake_provider, monkeypatch):
    monkeypatch.setenv("REPLICATE_API_TOKEN", "test-token")
    write_manifest(project, [image_model_entry(name="e1", model="acme/x", output="e1.png", format="png")])
    fake_provider(run_result={"version": "acme/x:abc123", "seed": None, "outputs": [b"not a png at all"]})
    code, out, _ = run_cli(["generate", "e1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 7
    checks_list = assert_checks_list_shape(doc["error"]["checks"])
    assert len(checks_list) == 1  # one declared output, R59
    assert checks_list[0]["checks"]["format"] == "fail"
    assert "path" in checks_list[0]


def test_exit_8_refused_output_already_exists(project, run_cli, monkeypatch):
    (project.drafts / "e1.png").write_bytes(b"already here")
    monkeypatch.setenv("REPLICATE_API_TOKEN", "test-token")
    write_manifest(project, [image_model_entry(name="e1", model="acme/x", output="e1.png")])
    code, out, _ = run_cli(["generate", "e1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 8


def test_exit_9_busy_when_lock_already_held(project, run_cli, monkeypatch):
    monkeypatch.setenv("REPLICATE_API_TOKEN", "test-token")
    write_manifest(project, [image_model_entry(name="e1", model="acme/x")])
    lock_path = project.record_path.with_name(project.record_path.name + ".lock")
    lock_fd = open(lock_path, "w")
    fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    try:
        code, out, _ = run_cli(["generate", "e1"] + project.config_args())
        doc = parse_single_json_document(out)
        assert code == 9
        assert str(lock_path) in doc["error"]["message"] or lock_path.name in doc["error"]["message"]
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        lock_fd.close()


def test_exit_10_commit_fails_when_destination_is_a_directory(project, run_cli):
    """
    R18/R67/R28: a *directory* sitting at a single-file entry's declared
    output is not R18's refusal (nothing generated it); it is what makes the
    commit rename fail with exit 10. Exercised via assemble_sheet so no
    provider stub is needed.
    """
    from conftest import make_png

    for i in range(4):
        make_png(project.samples / "frames" / f"f{i}.png")
    (project.drafts / "sheet1.png").mkdir()  # a directory, not a file
    entry = sheet_assemble_entry(name="sheet1", output="sheet1.png")
    write_manifest(project, [entry])
    code, out, _ = run_cli(["generate", "sheet1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 10
    assert doc["ok"] is False


def test_exit_11_internal_unexpected_failure(project, run_cli, fake_provider, monkeypatch):
    monkeypatch.setenv("REPLICATE_API_TOKEN", "test-token")
    write_manifest(project, [image_model_entry(name="e1", model="acme/x")])
    fake_provider(run_side_effect=lambda *a: (_ for _ in ()).throw(RuntimeError("boom")))
    code, out, _ = run_cli(["generate", "e1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 11


def test_exit_12_extraction_failed(project, run_cli, fake_extraction):
    """
    R74/R28: a source video that cannot be read or decoded is exit 12, never
    6 — an agent has to be able to tell a local decode failure from a
    Replicate failure without parsing the message.
    """
    entry = extract_frames_entry(name="f1", output="frames/walk_{n:03d}.png")
    write_manifest(project, [entry])

    def _raise_extraction_error(*a):
        import agf.frames as frames

        raise frames.ExtractionError("could not decode samples/video.mp4: unsupported codec")

    fake_extraction(side_effect=_raise_extraction_error)
    code, out, _ = run_cli(["generate", "f1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 12
    assert doc["ok"] is False
    assert "unsupported codec" in doc["error"]["message"]
    assert doc["error"]["remedy"]  # names the source file
    assert not (project.drafts / "frames").exists()  # nothing committed


def test_exit_12_is_never_reused_for_a_provider_failure(project, run_cli, fake_provider, monkeypatch):
    """The converse of the above: a provider failure stays exit 6, never 12
    — the two local/remote failure modes must not collapse into one code."""
    monkeypatch.setenv("REPLICATE_API_TOKEN", "token")
    write_manifest(project, [image_model_entry(name="e1", model="acme/x")])

    def _raise_provider_error(*a):
        from agf.provider import ProviderError

        raise ProviderError("the model rejected the request")

    fake_provider(run_side_effect=_raise_provider_error)
    code, out, _ = run_cli(["generate", "e1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 6


# ---------------------------------------------------------------------------
# R27 — fixed validation order
# ---------------------------------------------------------------------------

def test_r27_argument_shape_checked_before_config(run_cli, tmp_path, monkeypatch):
    """Step 1 (usage) precedes step 2 (config) — wrong arg count wins even
    with no config file anywhere in sight."""
    monkeypatch.chdir(tmp_path)
    code, out, _ = run_cli(["generate", "a", "b", "c"])
    doc = parse_single_json_document(out)
    assert code == 1


def test_r27_config_checked_before_manifest(project, run_cli):
    """Step 2 (config) precedes step 5 (manifest) — a broken config wins
    even when the manifest is also broken."""
    from conftest import write_config

    write_config(project, drafts="does_not_exist_dir")
    write_raw_manifest(project, "not_a_list: 1\n")
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 2


def test_r27_lock_checked_before_manifest_parse(project, run_cli, monkeypatch):
    """Step 3 (lock) precedes step 5 (manifest parse) — busy wins even when
    the manifest cannot parse at all."""
    monkeypatch.setenv("REPLICATE_API_TOKEN", "test-token")
    write_raw_manifest(project, "not: [valid: yaml:::\n")
    lock_path = project.record_path.with_name(project.record_path.name + ".lock")
    lock_fd = open(lock_path, "w")
    fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    try:
        code, out, _ = run_cli(["generate", "anything"] + project.config_args())
        doc = parse_single_json_document(out)
        assert code == 9
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        lock_fd.close()


def test_r27_manifest_validated_before_entry_lookup(project, run_cli):
    """Step 5 (manifest) precedes step 6 (entry lookup) — a manifest-wide
    error wins even when asking for an entry that would also 404."""
    entries = [
        sheet_assemble_entry(name="a", frame_count=5, layout={"columns": 2, "rows": 2}),  # 2*2 < 5, exit 3
    ]
    write_manifest(project, entries)
    code, out, _ = run_cli(["generate", "no-such-entry"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 3


def test_r27_output_collision_checked_before_credential(project, run_cli, monkeypatch):
    """Step 7 (collision, generate only) precedes step 8 (credential) — a
    pre-existing draft wins over a missing token."""
    monkeypatch.delenv("REPLICATE_API_TOKEN", raising=False)
    (project.drafts / "e1.png").write_bytes(b"already here")
    write_manifest(project, [image_model_entry(name="e1", model="acme/x", output="e1.png")])
    code, out, _ = run_cli(["generate", "e1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 8


def test_r27_regenerate_has_no_collision_step_credential_checked_directly(project, run_cli, monkeypatch):
    """regenerate has no step-7 collision check (R20) — a pre-existing draft
    does not shadow the missing-credential failure the way it does for
    generate."""
    monkeypatch.delenv("REPLICATE_API_TOKEN", raising=False)
    (project.drafts / "e1.png").write_bytes(b"already here")
    write_manifest(project, [image_model_entry(name="e1", model="acme/x", output="e1.png")])
    code, out, _ = run_cli(["regenerate", "e1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 5
