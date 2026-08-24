"""
Program-level contract — cli-v1 R2-R5. What every command must do regardless
of which one it is.

Wrong implementation this file defends against, per test: an unknown command
that reads a config file before rejecting itself, a bare invocation that
crashes instead of reporting a usage error, a command that blocks reading
stdin, or an uncaught exception whose traceback lands on stdout and breaks
the one property every caller (an agent) depends on.
"""
from __future__ import annotations

from conftest import parse_single_json_document, write_manifest


def test_r2_unknown_command_exits_1_and_reports_it_as_invoked(run_cli, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # no assetgen.yaml here at all
    code, out, _ = run_cli(["frobnicate"])
    doc = parse_single_json_document(out)
    assert code == 1
    assert doc["ok"] is False
    assert doc["command"] == "frobnicate"


def test_r2_unknown_command_never_reads_any_file(run_cli, tmp_path, monkeypatch):
    """An unknown command exits 1 'without reading any file' — proven by
    running it somewhere with no config and no manifest at all."""
    empty = tmp_path / "nothing_here"
    empty.mkdir()
    monkeypatch.chdir(empty)
    code, out, _ = run_cli(["not-a-real-command"])
    doc = parse_single_json_document(out)
    assert code == 1


def test_r2_bare_invocation_exits_1_with_null_command(run_cli, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    code, out, _ = run_cli([])
    doc = parse_single_json_document(out)
    assert code == 1
    assert doc["ok"] is False
    assert doc["command"] is None


def test_r2_bare_invocation_message_names_the_four_commands(run_cli, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    code, out, _ = run_cli([])
    doc = parse_single_json_document(out)
    message = doc["error"]["message"]
    for name in ("list", "generate", "record", "regenerate"):
        assert name in message, f"expected {name!r} to be named in: {message!r}"


def test_r3_no_command_ever_reads_stdin(project, run_cli, monkeypatch):
    """
    R3: given a fully-specified invocation, every command runs unattended.
    A stdin that raises the instant it is touched proves nothing tried to
    read it.
    """
    write_manifest(project, [])

    class ExplodingStdin:
        def read(self, *a, **kw):
            raise AssertionError("stdin.read() was called — R3 forbids this")

        def readline(self, *a, **kw):
            raise AssertionError("stdin.readline() was called — R3 forbids this")

        def __iter__(self):
            raise AssertionError("stdin was iterated — R3 forbids this")

    monkeypatch.setattr("sys.stdin", ExplodingStdin())
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0


def test_r4_stdout_is_a_single_json_document_on_every_failure_kind(
    project, run_cli, tmp_path, monkeypatch
):
    """
    R4: the one-document property holds for every failure category, not just
    success — spot-checked across usage, config, and manifest failures.
    """
    # usage failure
    monkeypatch.chdir(tmp_path)
    code, out, _ = run_cli(["generate"])  # zero positional args
    parse_single_json_document(out)
    assert code == 1

    # config failure
    code, out, _ = run_cli(["list", "--config", str(tmp_path / "no_such.yaml")])
    parse_single_json_document(out)
    assert code == 2

    # manifest failure
    from conftest import write_raw_manifest

    write_raw_manifest(project, "not_a_list: true\n")
    code, out, _ = run_cli(["list"] + project.config_args())
    parse_single_json_document(out)
    assert code == 3


def test_r4_unexpected_internal_exception_exits_11_with_valid_json_and_no_traceback_on_stdout(
    project, run_cli, fake_provider, monkeypatch
):
    """
    R4/R28: an exception nobody coded a specific exit for — raised deep
    inside a provider call, standing in for anything unanticipated — must
    still exit 11 with exactly one JSON document on stdout, never a raw
    traceback.
    """
    from conftest import image_model_entry

    entry = image_model_entry(name="e1", model="acme/x")
    write_manifest(project, [entry])
    monkeypatch.setenv("REPLICATE_API_TOKEN", "test-token")
    fake_provider(run_side_effect=lambda *a: (_ for _ in ()).throw(RuntimeError("boom-unexpected")))
    code, out, err = run_cli(["generate", "e1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 11
    assert doc["ok"] is False
    assert "Traceback" not in out
    assert doc["error"]["message"]
    assert doc["error"]["remedy"]


def test_r5_error_object_has_non_empty_message_and_remedy(run_cli, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    code, out, _ = run_cli(["nope"])
    doc = parse_single_json_document(out)
    assert doc["error"]["message"].strip() != ""
    assert doc["error"]["remedy"].strip() != ""
    assert "code" in doc["error"]


def test_r5_command_field_is_the_command_as_invoked_including_unrecognised(run_cli, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    code, out, _ = run_cli(["totally-bogus-command"])
    doc = parse_single_json_document(out)
    assert doc["command"] == "totally-bogus-command"
