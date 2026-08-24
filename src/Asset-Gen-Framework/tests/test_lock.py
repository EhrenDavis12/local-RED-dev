"""
The run lock — cli-v1 R72.

Wrong implementation this file defends against, per test: busy decided by
checking whether the lock file exists rather than by trying to acquire the
kernel lock (which would wedge every future run behind one killed process
forever), a lock scoped to the drafts path instead of the record, or `list`/
`record` blocked by a lock they were never supposed to take.
"""
from __future__ import annotations

import fcntl

from conftest import image_model_entry, parse_single_json_document, write_manifest


def _hold_lock(project):
    lock_path = project.record_path.with_name(project.record_path.name + ".lock")
    fd = open(lock_path, "w")
    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    return lock_path, fd


def test_r72_second_concurrent_generate_exits_9_busy(project, run_cli, monkeypatch):
    monkeypatch.setenv("REPLICATE_API_TOKEN", "token")
    write_manifest(project, [image_model_entry(name="e1", model="acme/x")])
    lock_path, fd = _hold_lock(project)
    try:
        code, out, _ = run_cli(["generate", "e1"] + project.config_args())
        doc = parse_single_json_document(out)
        assert code == 9
        assert doc["ok"] is False
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        fd.close()


def test_r72_regenerate_is_also_blocked_by_the_lock(project, run_cli, monkeypatch):
    monkeypatch.setenv("REPLICATE_API_TOKEN", "token")
    write_manifest(project, [image_model_entry(name="e1", model="acme/x")])
    lock_path, fd = _hold_lock(project)
    try:
        code, out, _ = run_cli(["regenerate", "e1"] + project.config_args())
        doc = parse_single_json_document(out)
        assert code == 9
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        fd.close()


def test_r72_busy_error_names_the_lock_files_own_path(project, run_cli, monkeypatch):
    monkeypatch.setenv("REPLICATE_API_TOKEN", "token")
    write_manifest(project, [image_model_entry(name="e1", model="acme/x")])
    lock_path, fd = _hold_lock(project)
    try:
        code, out, _ = run_cli(["generate", "e1"] + project.config_args())
        doc = parse_single_json_document(out)
        assert lock_path.name in doc["error"]["message"]
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        fd.close()


def test_r72_list_takes_no_lock_and_is_never_blocked(project, run_cli):
    write_manifest(project, [image_model_entry(name="e1", model="acme/x")])
    lock_path, fd = _hold_lock(project)
    try:
        code, out, _ = run_cli(["list"] + project.config_args())
        doc = parse_single_json_document(out)
        assert code == 0
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        fd.close()


def test_r72_record_command_takes_no_lock_and_is_never_blocked(project, run_cli):
    write_manifest(project, [image_model_entry(name="e1", model="acme/x")])
    lock_path, fd = _hold_lock(project)
    try:
        code, out, _ = run_cli(["record", "e1"] + project.config_args())
        doc = parse_single_json_document(out)
        assert code == 0
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        fd.close()


def test_r72_busy_is_decided_by_acquiring_not_by_the_file_existing(project, run_cli, monkeypatch):
    """
    R72: 'Busy is decided by trying to acquire the lock, never by the file
    existing' — a lock file present but held by nobody (fd already released)
    must not block a run.
    """
    monkeypatch.setenv("REPLICATE_API_TOKEN", "token")
    lock_path = project.record_path.with_name(project.record_path.name + ".lock")
    lock_path.write_text("")  # the file exists, but nobody holds the OS lock
    from conftest import sheet_assemble_entry, make_png

    for i in range(4):
        make_png(project.samples / "frames" / f"f{i}.png")
    write_manifest(project, [sheet_assemble_entry(name="s1")])
    code, out, _ = run_cli(["generate", "s1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0


def test_r72_lock_file_persists_after_a_successful_run_and_is_not_deleted(project, run_cli, monkeypatch):
    from conftest import sheet_assemble_entry, make_png

    for i in range(4):
        make_png(project.samples / "frames" / f"f{i}.png")
    write_manifest(project, [sheet_assemble_entry(name="s1")])
    code, out, _ = run_cli(["generate", "s1"] + project.config_args())
    assert code == 0
    lock_path = project.record_path.with_name(project.record_path.name + ".lock")
    assert lock_path.exists(), "R72: the lock file is created once and never deleted"


def test_r72_a_second_run_after_the_first_releases_succeeds(project, run_cli, monkeypatch):
    from conftest import sheet_assemble_entry, make_png

    for i in range(4):
        make_png(project.samples / "frames" / f"f{i}.png")
    write_manifest(
        project,
        [sheet_assemble_entry(name="s1", output="s1.png"), sheet_assemble_entry(name="s2", output="s2.png")],
    )
    first = run_cli(["generate", "s1"] + project.config_args())
    assert first[0] == 0
    second = run_cli(["generate", "s2"] + project.config_args())
    assert second[0] == 0
