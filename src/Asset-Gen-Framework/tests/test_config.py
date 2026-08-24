"""
Config validation — cli-v1 R6-R13. Every rule here exits 2.

Wrong implementation this file defends against, per test: a config check that
is silently skipped, that reports the wrong exit code, that resolves a path
against the working directory instead of the config file's own directory, or
that lets the framework quietly create a directory it should instead refuse
to run without.
"""
from __future__ import annotations

from conftest import (
    parse_single_json_document,
    write_config,
    write_manifest,
    write_raw_config,
)


def test_r6_default_config_path_is_assetgen_yaml_in_cwd(project, run_cli, monkeypatch):
    """R6: with no --config, the CLI reads ./assetgen.yaml relative to cwd."""
    write_manifest(project, [])
    monkeypatch.chdir(project.root)
    code, out, _ = run_cli(["list"])
    doc = parse_single_json_document(out)
    assert code == 0
    assert doc["ok"] is True


def test_r7_config_flag_overrides_default_and_works_from_elsewhere(project, run_cli, monkeypatch, tmp_path):
    """R7: --config is the only way to run from outside the project root."""
    write_manifest(project, [])
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    code, out, _ = run_cli(["list", "--config", str(project.config_path)])
    doc = parse_single_json_document(out)
    assert code == 0
    assert doc["ok"] is True


def test_r8_missing_config_exits_2_and_names_the_path(run_cli, monkeypatch, tmp_path):
    """R8: a missing config exits 2 naming the path it looked for."""
    empty_dir = tmp_path / "no_config_here"
    empty_dir.mkdir()
    monkeypatch.chdir(empty_dir)
    code, out, _ = run_cli(["list"])
    doc = parse_single_json_document(out)
    assert code == 2
    assert doc["ok"] is False
    assert "assetgen.yaml" in doc["error"]["message"]


def test_r8_never_searches_parent_directories_for_config(run_cli, monkeypatch, tmp_path):
    """R8: an upward search is explicitly forbidden — a parent's config is invisible."""
    outer = tmp_path / "outer"
    outer.mkdir()
    (outer / "assetgen.yaml").write_text(
        "manifest: manifest.yaml\ndrafts: drafts\nrecord: record.json\n"
    )
    inner = outer / "inner"
    inner.mkdir()
    monkeypatch.chdir(inner)
    code, out, _ = run_cli(["list"])
    doc = parse_single_json_document(out)
    assert code == 2
    assert doc["ok"] is False


def test_r9_missing_required_key_manifest_exits_2(project, run_cli):
    write_config(project, manifest=None)
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 2
    assert "manifest" in doc["error"]["message"]


def test_r9_missing_required_key_drafts_exits_2(project, run_cli):
    write_config(project, drafts=None)
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 2
    assert "drafts" in doc["error"]["message"]


def test_r9_missing_required_key_record_exits_2(project, run_cli):
    write_config(project, record=None)
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 2
    assert "record" in doc["error"]["message"]


def test_r9_samples_and_base_are_optional(project, run_cli):
    """R9: samples and base are not required; omitting both is legal."""
    write_config(project, samples=None, base=None)
    write_manifest(project, [])
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0
    assert doc["ok"] is True


def test_r11_unknown_key_exits_2_naming_it(project, run_cli):
    write_config(project, bogus_key="whatever")
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 2
    assert "bogus_key" in doc["error"]["message"]


def test_r11_declared_manifest_path_missing_exits_2(project, run_cli):
    write_config(project, manifest="does_not_exist.yaml")
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 2
    assert "manifest" in doc["error"]["message"]


def test_r11_declared_drafts_path_missing_exits_2(project, run_cli):
    write_config(project, drafts="no_such_drafts_dir")
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 2
    assert "drafts" in doc["error"]["message"]


def test_r11_declared_samples_path_missing_exits_2(project, run_cli):
    write_config(project, samples="no_such_samples_dir")
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 2
    assert "samples" in doc["error"]["message"]


def test_r11_declared_base_path_missing_exits_2(project, run_cli):
    write_config(project, base="no_such_base_dir")
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 2
    assert "base" in doc["error"]["message"]


def test_r11_record_parent_directory_missing_exits_2(project, run_cli):
    """R11: the record FILE need not exist, but its parent directory must."""
    write_config(project, record="nested/does_not_exist/record.json")
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 2
    assert "record" in doc["error"]["message"]


def test_r11_record_file_itself_need_not_exist(project, run_cli):
    """R11: a record path whose parent exists, but whose file does not, is fine."""
    assert not project.record_path.exists()
    write_manifest(project, [])
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0
    assert doc["ok"] is True


def test_r11_record_path_inside_drafts_exits_2(project, run_cli):
    """
    R11: a record path resolving inside drafts, at any depth, exits 2 —
    otherwise the record's temp copy and the lock would sit in the sweep's
    own scan path.
    """
    write_config(project, record="drafts/record.json")
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 2
    assert "record" in doc["error"]["message"]
    assert "drafts" in doc["error"]["message"]


def test_r11_record_path_nested_inside_drafts_exits_2(project, run_cli):
    """R11: 'at any depth' — a record two levels under drafts is still rejected."""
    (project.drafts / "nested" / "deeper").mkdir(parents=True)
    write_config(project, record="drafts/nested/deeper/record.json")
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 2


def test_r10_paths_resolve_relative_to_config_directory_not_cwd(project, run_cli, monkeypatch, tmp_path):
    """
    R10: every config value is resolved relative to the config file's own
    directory, never to the working directory — this is what lets --config
    work from anywhere (R7).
    """
    write_manifest(project, [])
    somewhere_else = tmp_path / "somewhere_else_entirely"
    somewhere_else.mkdir()
    monkeypatch.chdir(somewhere_else)
    code, out, _ = run_cli(["list", "--config", str(project.config_path)])
    doc = parse_single_json_document(out)
    assert code == 0, doc


def test_r10_absolute_path_in_config_accepted_as_is(project, run_cli, tmp_path):
    """R10: an absolute path in the config is accepted as-is."""
    abs_manifest = tmp_path / "elsewhere_manifest.yaml"
    abs_manifest.write_text("[]\n")
    write_config(project, manifest=str(abs_manifest))
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0
    assert doc["ok"] is True


def test_config_unparseable_yaml_exits_2(project, run_cli):
    write_raw_config(project, "manifest: [this is not: valid: yaml:::\n")
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 2
    assert doc["ok"] is False


def test_r12_framework_never_creates_a_declared_config_directory(project, run_cli):
    """
    R12: the framework creates no directory declared in the config — proven
    by the negative space of R11: a missing declared directory is a hard
    error (exit 2), never silently created and continued from.
    """
    write_config(project, drafts="drafts_never_created")
    assert not (project.root / "drafts_never_created").exists()
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 2
    assert not (project.root / "drafts_never_created").exists()
