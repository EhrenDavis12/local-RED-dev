"""
`agf` — cli-v1 R1-R5, R14-R28. The one entry point: `agf <command> [args]`.
"""
from __future__ import annotations

import json
import sys
import traceback

from agf.config import load_config
from agf.draftstate import find_occupying_path
from agf.errors import AgfError, InternalError, NotFoundError, RefusedError, UsageError
from agf.execute import execute_entry, get_credential
from agf.manifest import load_manifest_raw, validate_manifest
from agf.record import get_stored_entry, load_record, write_record
from agf.staging import acquire_lock, release_lock, sweep

COMMANDS = ("list", "generate", "record", "regenerate")


def run() -> None:
    """Console-script entry point."""
    sys.exit(main(sys.argv[1:]))


def main(argv: list[str]) -> int:
    """R4: never raises. Every failure is caught and reported as one JSON
    document on stdout, with the matching exit code."""
    command = argv[0] if argv else None
    try:
        if command is None:
            raise UsageError(
                "no command given; expected one of: list, generate, record, regenerate",
                remedy="run one of: list, generate, record, regenerate",
            )
        if command not in COMMANDS:
            raise UsageError(
                f"unknown command: {command!r}; expected one of: "
                "list, generate, record, regenerate",
                remedy="run one of: list, generate, record, regenerate",
            )

        handler = {
            "list": _cmd_list,
            "generate": _cmd_generate,
            "record": _cmd_record,
            "regenerate": _cmd_regenerate,
        }[command]
        result = handler(argv[1:])
        doc = {"ok": True, **result}
        print(json.dumps(doc))
        return 0
    except AgfError as exc:
        doc = _error_document(command, exc)
        print(json.dumps(doc))
        return exc.code
    except (Exception, KeyboardInterrupt) as exc:  # noqa: BLE001 — R4/R28: never let a
        # traceback reach stdout. KeyboardInterrupt is a BaseException, not an
        # Exception, so it needs naming explicitly here to be caught at all.
        traceback.print_exc(file=sys.stderr)
        internal = InternalError(str(exc) or repr(exc))
        doc = _error_document(command, internal)
        print(json.dumps(doc))
        return internal.code


def _error_document(command, error: AgfError) -> dict:
    error_obj = {"code": error.code, "message": error.message, "remedy": error.remedy}
    if error.checks is not None:
        error_obj["checks"] = error.checks
    return {"ok": False, "command": command, "error": error_obj}


def _parse_args(args: list[str]) -> tuple[list[str], str | None]:
    """The only recognised option is `--config <path>`; anything else
    starting with `--` is an unrecognised option (R28 code 1)."""
    positional: list[str] = []
    config_arg = None
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--config":
            if i + 1 >= len(args):
                raise UsageError("--config requires a path")
            config_arg = args[i + 1]
            i += 2
        elif arg.startswith("--"):
            raise UsageError(f"unrecognized option: {arg}")
        else:
            positional.append(arg)
            i += 1
    return positional, config_arg


def _cmd_list(args: list[str]) -> dict:
    positional, config_arg = _parse_args(args)
    if positional:
        raise UsageError("'list' takes no positional arguments")

    config = load_config(config_arg)
    record_data = load_record(config.record)  # R27 step 5 (R76)
    raw_manifest = load_manifest_raw(config.manifest)
    entries = validate_manifest(raw_manifest, config)

    record_entries = record_data["entries"] if record_data else {}

    listed = []
    for entry in entries:
        listed.append(
            {
                "name": entry.name,
                "type": entry.type,
                "operation": entry.operation,
                "model": entry.resolved_model,
                "model_source": entry.model_source,
                "output": entry.output,
                "format": entry.format,
                "draft_exists": find_occupying_path(entry, config.drafts) is not None,
                "has_record": entry.name in record_entries,
            }
        )
    return {"command": "list", "entries": listed}


def _cmd_record(args: list[str]) -> dict:
    positional, config_arg = _parse_args(args)
    if len(positional) != 1:
        raise UsageError("'record' takes exactly one entry name")
    name = positional[0]

    config = load_config(config_arg)
    load_record(config.record)  # R27 step 5 (R76) — validated before the manifest is read
    raw_manifest = load_manifest_raw(config.manifest)
    entries = validate_manifest(raw_manifest, config)

    if not any(entry.name == name for entry in entries):
        raise NotFoundError(f"no entry named {name!r} in the manifest")

    stored = get_stored_entry(config.record, name)
    return {"command": "record", "name": name, "record": stored}


def _generate_or_regenerate(args: list[str], *, is_regenerate: bool) -> dict:
    command_name = "regenerate" if is_regenerate else "generate"
    positional, config_arg = _parse_args(args)
    if len(positional) != 1:
        raise UsageError(f"'{command_name}' takes exactly one entry name")
    name = positional[0]

    config = load_config(config_arg)  # R27 step 2

    lock_fh = acquire_lock(config.lock_path)  # R27 step 3
    try:
        sweep(config.drafts, config.record)  # R27 step 4

        load_record(config.record)  # R27 step 5 (R76) — before manifest, credential, and any spend

        raw_manifest = load_manifest_raw(config.manifest)
        entries = validate_manifest(raw_manifest, config)  # R27 step 6

        entry = next((e for e in entries if e.name == name), None)  # R27 step 7
        if entry is None:
            raise NotFoundError(f"no entry named {name!r} in the manifest")

        if not is_regenerate:
            occupied = find_occupying_path(entry, config.drafts)  # R27 step 8
            if occupied is not None:
                raise RefusedError(f"output already exists: {occupied}")

        credential = get_credential() if entry.operation == "model" else None  # R27 step 9

        file_results, model_version, seed = execute_entry(config, entry, credential)  # steps 10-12

        write_record(config.record, entry, model_version, seed)

        return {
            "command": command_name,
            "name": entry.name,
            "operation": entry.operation,
            "model_version": model_version,
            "seed": seed,
            "output": file_results,
        }
    finally:
        release_lock(lock_fh)


def _cmd_generate(args: list[str]) -> dict:
    return _generate_or_regenerate(args, is_regenerate=False)


def _cmd_regenerate(args: list[str]) -> dict:
    return _generate_or_regenerate(args, is_regenerate=True)
