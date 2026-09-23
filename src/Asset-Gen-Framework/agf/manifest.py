"""
The manifest — cli-v1 R34-R46, R55-R56, R58, R60-R64, plus R13/R45 output
rules and the R70 reserved prefix. The framework reads it and never writes
it (R34). Every entry in the whole file is validated, in manifest order,
before any command acts on the one it was asked for (R34).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

import yaml

from agf.config import Config
from agf.errors import ManifestError
from agf.refs import RESERVED_PREFIXES, resolve_reference

RECOGNIZED_TYPES = {"image", "sound", "music", "sprite_sheet", "video"}
RECOGNIZED_OPERATIONS = {"model", "assemble_sheet", "extract_frames"}

# R56 — the set of formats the framework can check bytes against.
RECOGNIZED_FORMATS = {
    "png": (".png",),
    "jpeg": (".jpeg", ".jpg"),
    "webp": (".webp",),
    "wav": (".wav",),
    "mp3": (".mp3",),
    "mp4": (".mp4",),
    "mov": (".mov",),
}

# R38 — version one's two settled defaults.
DEFAULT_MODELS = {
    "image": "sourceful/riverflow-2.0-pro",
    "music": "stability-ai/stable-audio-2.5",
}

ALL_FIELDS = {
    "name", "type", "operation", "model", "prompt", "prompt_key", "output",
    "format", "inputs", "input_files", "frame_count", "frame_size", "layout",
    "frames", "source", "resize", "matte",
}
REQUIRED_FIELDS = {"name", "type", "output", "format"}
CALL_FIELDS = {"model", "prompt", "prompt_key", "inputs", "input_files"}

_PLACEHOLDER_RE = re.compile(r"\{n(?::([^}]*))?\}")

# R63: a placeholder's format spec must produce decimal digits, since R18's
# collision check matches a placeholder against one or more decimal digits
# and the literal text around it — anything else silently defeats that
# match. Legal: empty, 'd', or a *zero-padded* width followed by 'd'
# ('03d', '05d'). A width with no leading zero space-pads instead —
# verified, "{:5d}".format(7) == '    7' — which produces filenames with
# spaces where the collision matcher expects digits: the same false
# negative as '.2f', just quieter. The leading '0' is required, and the
# width digits after it are capped at three so an absurd width (e.g.
# '0999999999d') can't blow up formatting a basename into a
# multi-gigabyte string.
_ALLOWED_PLACEHOLDER_SPEC_RE = re.compile(r"^(?:|d|0\d{1,3}d)$")


@dataclass
class Entry:
    name: str
    type: str
    operation: str
    model: str | None  # declared, verbatim (R47)
    resolved_model: str | None  # declared or the type's default; None if none applies
    model_source: str  # "entry" | "default" | "none" (R15)
    prompt: str | None
    prompt_key: str | None
    inputs: dict | None  # declared, verbatim; None if the entry omitted it
    input_files: dict | None  # declared, verbatim; None if the entry omitted it
    output: str  # declared filename or template, never expanded (R45)
    format: str
    frame_count: int | None
    frame_size: list | None
    layout: dict | None
    frames: list | None
    source: str | None
    resize: list | None  # extract_frames only: every frame is fitted into [w, h]
    matte: dict | None  # extract_frames only: alpha from a mask video, outline restored


def load_manifest_raw(manifest_path: Path):
    try:
        text = manifest_path.read_text()
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ManifestError(f"manifest {manifest_path} is not valid YAML: {exc}") from exc
    except OSError as exc:
        raise ManifestError(f"manifest {manifest_path} could not be read: {exc}") from exc

    # R16: an empty file, or a `null` YAML document, is a manifest of zero
    # entries — a legitimate starting state, not an error.
    if data is None:
        return []
    if not isinstance(data, list):
        raise ManifestError(
            f"manifest {manifest_path} must be a list of entries at its top level"
        )
    return data


def validate_manifest(raw_entries: list, config: Config) -> list[Entry]:
    entries: list[Entry] = []
    names_seen: set[str] = set()
    for index, raw in enumerate(raw_entries):
        entry = _validate_entry(raw, index, config)
        if entry.name in names_seen:
            raise ManifestError(f"duplicate entry name: {entry.name!r}")
        names_seen.add(entry.name)
        entries.append(entry)

    _validate_cross_entry_claims(entries)
    return entries


def _validate_entry(raw, index: int, config: Config) -> Entry:
    if not isinstance(raw, dict):
        raise ManifestError(f"manifest entry #{index} must be a mapping")

    label = raw.get("name", f"<entry #{index}>")

    unknown = set(raw.keys()) - ALL_FIELDS
    if unknown:
        raise ManifestError(
            f"entry {label!r} has unrecognized field(s): {', '.join(sorted(unknown))}"
        )

    missing = REQUIRED_FIELDS - set(raw.keys())
    if missing:
        raise ManifestError(
            f"entry {label!r} is missing required field(s): {', '.join(sorted(missing))}"
        )

    name = raw["name"]
    if not isinstance(name, str) or not name:
        raise ManifestError(f"entry {label!r}: 'name' must be a non-empty string")
    type_ = raw["type"]
    operation = raw.get("operation", "model")

    if operation not in RECOGNIZED_OPERATIONS:
        raise ManifestError(f"entry {name!r} has an unrecognized operation: {operation!r}")
    if type_ not in RECOGNIZED_TYPES:
        raise ManifestError(f"entry {name!r} has an unrecognized type: {type_!r}")

    # R36 — the operation/type pairing.
    if operation == "assemble_sheet" and type_ != "sprite_sheet":
        raise ManifestError(
            f"entry {name!r}: operation 'assemble_sheet' requires type 'sprite_sheet', "
            f"got {type_!r}"
        )
    if operation == "extract_frames" and type_ != "image":
        raise ManifestError(
            f"entry {name!r}: operation 'extract_frames' requires type 'image', got {type_!r}"
        )

    # R37 — fields legal only for a particular operation.
    if operation != "model":
        illegal = CALL_FIELDS & set(raw.keys())
        if illegal:
            raise ManifestError(
                f"entry {name!r}: field(s) {', '.join(sorted(illegal))} not legal for "
                f"operation {operation!r}"
            )
    if operation != "assemble_sheet" and "frames" in raw:
        raise ManifestError(f"entry {name!r}: field 'frames' not legal for operation {operation!r}")
    if operation != "extract_frames" and "source" in raw:
        raise ManifestError(f"entry {name!r}: field 'source' not legal for operation {operation!r}")

    # R38 — model required/optional/rejected.
    model = raw.get("model")
    resolved_model = None
    model_source = "none"
    if operation == "model":
        if model is not None:
            resolved_model = model
            model_source = "entry"
        elif type_ in DEFAULT_MODELS:
            resolved_model = DEFAULT_MODELS[type_]
            model_source = "default"
        else:
            raise ManifestError(
                f"entry {name!r}: 'model' is required for type {type_!r} (no default)"
            )

    # R41 — prompt / prompt_key, and the collision with an inputs key.
    prompt = raw.get("prompt")
    prompt_key = raw.get("prompt_key")
    inputs = raw.get("inputs")
    if operation == "model" and prompt is not None:
        effective_key = prompt_key if prompt_key is not None else "prompt"
        if inputs and effective_key in inputs:
            raise ManifestError(
                f"entry {name!r}: 'prompt' conflicts with inputs key {effective_key!r} — "
                "only one may set it"
            )

    output = raw["output"]
    _validate_output_path(name, output, operation)

    format_ = raw["format"]
    if format_ not in RECOGNIZED_FORMATS:
        raise ManifestError(f"entry {name!r}: unrecognized format {format_!r}")
    _validate_extension_matches_format(name, output, format_)

    if operation == "assemble_sheet" and format_ != "png":
        raise ManifestError(
            f"entry {name!r}: assemble_sheet requires declared format 'png', got {format_!r}"
        )

    frame_count = raw.get("frame_count")
    frame_size = raw.get("frame_size")
    layout = raw.get("layout")
    _validate_geometry(name, type_, operation, raw, frame_count, frame_size, layout)

    frames_list = raw.get("frames")
    if operation == "assemble_sheet":
        if frames_list is None:
            raise ManifestError(f"entry {name!r}: 'frames' is required for assemble_sheet")
        if not isinstance(frames_list, list) or len(frames_list) == 0:
            raise ManifestError(f"entry {name!r}: 'frames' must be a non-empty list")
        if len(frames_list) != frame_count:
            raise ManifestError(
                f"entry {name!r}: 'frames' lists {len(frames_list)} file(s) but "
                f"frame_count is {frame_count}"
            )
        # R58 — every assemble_sheet frame is PNG.
        for ref in frames_list:
            if not str(ref).lower().endswith(".png"):
                raise ManifestError(
                    f"entry {name!r}: assemble_sheet frame {ref!r} is not a PNG file"
                )

    source = raw.get("source")
    if operation == "extract_frames" and source is None:
        raise ManifestError(f"entry {name!r}: 'source' is required for extract_frames")

    # R42/R43 — every file reference must resolve to a real file, now.
    for key, ref in (raw.get("input_files") or {}).items():
        context = f"entry {name!r} input_files[{key!r}]"
        if isinstance(ref, list):
            if not ref:
                raise ManifestError(f"{context}: a list of file references must not be empty")
            for one in ref:
                resolve_reference(config, one, context=context)
        else:
            resolve_reference(config, ref, context=context)
    if operation == "assemble_sheet":
        for ref in frames_list:
            resolve_reference(config, ref, context=f"entry {name!r} frames")
    if operation == "extract_frames":
        resolve_reference(config, source, context=f"entry {name!r} source")
    _validate_matte(name, operation, raw, config)

    return Entry(
        name=name,
        type=type_,
        operation=operation,
        model=model,
        resolved_model=resolved_model,
        model_source=model_source,
        prompt=prompt,
        prompt_key=prompt_key,
        inputs=inputs,
        input_files=raw.get("input_files"),
        output=output,
        format=format_,
        frame_count=frame_count,
        frame_size=frame_size,
        layout=layout,
        frames=frames_list,
        source=source,
        resize=raw.get("resize"),
        matte=raw.get("matte"),
    )


def _validate_output_path(name: str, output, operation: str) -> None:
    if not isinstance(output, str) or not output:
        raise ManifestError(f"entry {name!r}: 'output' must be a non-empty string")

    posix = PurePosixPath(output)
    if posix.is_absolute():
        raise ManifestError(f"entry {name!r}: output path {output!r} must not be absolute")
    if ".." in posix.parts:
        raise ManifestError(
            f"entry {name!r}: output path {output!r} must not escape drafts via '..'"
        )
    for part in posix.parts:
        if part.startswith(RESERVED_PREFIXES):
            raise ManifestError(
                f"entry {name!r}: output path {output!r} uses a prefix reserved by the framework"
            )

    if operation == "extract_frames":
        _validate_template_syntax(name, output)


def _validate_template_syntax(name: str, output: str) -> None:
    matches = list(_PLACEHOLDER_RE.finditer(output))
    if len(matches) != 1:
        raise ManifestError(
            f"entry {name!r}: extract_frames output {output!r} must contain exactly one "
            "'{n}' placeholder"
        )
    match = matches[0]

    # R63: the spec is validated, not just counted — a float, string,
    # char, space-padded, fill/align/sign/thousands-separator spec, or an
    # absurdly wide one, produces something other than a clean run of
    # decimal digits and silently defeats R18's collision match.
    spec = match.group(1) or ""
    if not _ALLOWED_PLACEHOLDER_SPEC_RE.match(spec):
        raise ManifestError(
            f"entry {name!r}: extract_frames output {output!r} has an unsupported format "
            f"spec {spec!r} for '{{n}}' — only an empty spec, 'd', or a width (optionally "
            "zero-padded) followed by 'd' produces decimal digits"
        )

    # It is not enough to count the one legitimate `{n}` (or `{n:spec}`)
    # placeholder — the rest of the string must be a safe literal for
    # `str.format(n=i)` too, or a second field (`{x}`, `{0}`), an unbalanced
    # brace, or any other stray `{`/`}` passes validation and only fails
    # (or, for extract_frames, decodes the whole video first) when the
    # basename is actually formatted at generate time.
    remainder = output[: match.start()] + output[match.end() :]
    if "{" in remainder or "}" in remainder:
        raise ManifestError(
            f"entry {name!r}: extract_frames output {output!r} must contain exactly one "
            "'{n}' placeholder and no other braces"
        )
    if len(PurePosixPath(output).parts) < 2:
        raise ManifestError(
            f"entry {name!r}: extract_frames output {output!r} must write into a "
            "subdirectory of drafts, not directly into it"
        )


def _validate_extension_matches_format(name: str, output: str, format_: str) -> None:
    extensions = RECOGNIZED_FORMATS.get(format_, ())
    suffix = PurePosixPath(output).suffix.lower()
    if suffix not in extensions:
        raise ManifestError(
            f"entry {name!r}: output extension {suffix!r} disagrees with declared format "
            f"{format_!r}"
        )


def _is_int(value) -> bool:
    # bool is a subclass of int; a manifest author writing `true` for a
    # count or a dimension is not writing a number.
    return isinstance(value, int) and not isinstance(value, bool)


MATTE_KEYS = {"mask", "background", "grow", "threshold", "feather"}


def _validate_matte(name: str, operation: str, raw: dict, config) -> None:
    if "matte" not in raw:
        return
    if operation != "extract_frames":
        raise ManifestError(f"entry {name!r}: 'matte' is legal only for extract_frames")
    matte = raw["matte"]
    if not isinstance(matte, dict) or "mask" not in matte:
        raise ManifestError(f"entry {name!r}: 'matte' must be a mapping with at least 'mask'")
    unknown = set(matte) - MATTE_KEYS
    if unknown:
        raise ManifestError(
            f"entry {name!r}: matte has unknown key(s) {', '.join(sorted(unknown))}; "
            f"legal keys are {', '.join(sorted(MATTE_KEYS))}"
        )
    resolve_reference(config, matte["mask"], context=f"entry {name!r} matte.mask")
    background = matte.get("background", "auto")
    if background != "auto" and not (
        isinstance(background, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", background)
    ):
        raise ManifestError(
            f"entry {name!r}: matte.background must be 'auto' or a '#rrggbb' colour, "
            f"got {background!r}"
        )
    for key, low, high in (("grow", 0, 16), ("threshold", 0, 441), ("feather", 0, 8)):
        if key in matte:
            value = matte[key]
            if not (isinstance(value, (int, float)) and not isinstance(value, bool)) or not (
                low <= value <= high
            ):
                raise ManifestError(
                    f"entry {name!r}: matte.{key} must be a number from {low} to {high}, got {value!r}"
                )


def _validate_geometry(name, type_, operation, raw, frame_count, frame_size, layout) -> None:
    is_sheet = type_ == "sprite_sheet"
    if "resize" in raw:
        if operation != "extract_frames":
            raise ManifestError(
                f"entry {name!r}: 'resize' is legal only for extract_frames"
            )
        resize = raw["resize"]
        if not (
            isinstance(resize, list)
            and len(resize) == 2
            and all(_is_int(v) and v > 0 for v in resize)
        ):
            raise ManifestError(
                f"entry {name!r}: 'resize' must be a [width, height] list of two "
                f"positive integers, got {resize!r}"
            )
    if is_sheet:
        missing = [k for k in ("frame_count", "frame_size", "layout") if k not in raw]
        if missing:
            raise ManifestError(
                f"entry {name!r}: sprite_sheet requires {', '.join(missing)}"
            )

        # R44: every geometry value is positive — an integer greater than
        # zero. Zero or negative reaches image construction and surfaces
        # there as an unexpected internal failure instead of the manifest
        # mistake it already was.
        if not _is_int(frame_count) or frame_count <= 0:
            raise ManifestError(f"entry {name!r}: 'frame_count' must be a positive integer")

        if not (
            isinstance(frame_size, list)
            and len(frame_size) == 2
            and all(_is_int(v) and v > 0 for v in frame_size)
        ):
            raise ManifestError(
                f"entry {name!r}: 'frame_size' must be a [width, height] list of two "
                f"positive integers, got {frame_size!r}"
            )

        if not isinstance(layout, dict) or "columns" not in layout or "rows" not in layout:
            raise ManifestError(f"entry {name!r}: 'layout' must have 'columns' and 'rows'")
        columns, rows = layout["columns"], layout["rows"]
        if not _is_int(columns) or columns <= 0 or not _is_int(rows) or rows <= 0:
            raise ManifestError(
                f"entry {name!r}: layout 'columns' and 'rows' must be positive integers, "
                f"got {layout!r}"
            )

        if columns * rows < frame_count:
            raise ManifestError(
                f"entry {name!r}: layout {columns}x{rows} cannot hold frame_count {frame_count}"
            )
    elif operation == "extract_frames":
        if "frame_size" in raw:
            raise ManifestError(f"entry {name!r}: 'frame_size' not legal for extract_frames")
        if "layout" in raw:
            raise ManifestError(f"entry {name!r}: 'layout' not legal for extract_frames")
        # R44: positivity holds wherever frame_count is legal, including
        # here — it is not sheet geometry, but a negative or zero count is
        # exactly as nonsensical for a video's frame yield.
        if frame_count is not None and (not _is_int(frame_count) or frame_count <= 0):
            raise ManifestError(f"entry {name!r}: 'frame_count' must be a positive integer")
    else:
        present = [k for k in ("frame_count", "frame_size", "layout") if k in raw]
        if present:
            raise ManifestError(
                f"entry {name!r}: geometry field(s) {', '.join(present)} not legal here"
            )


def _claimed_dir(entry: Entry) -> PurePosixPath:
    return PurePosixPath(entry.output).parent


def _dirs_overlap(a: PurePosixPath, b: PurePosixPath) -> bool:
    a_parts, b_parts = a.parts, b.parts
    shorter, longer = (a_parts, b_parts) if len(a_parts) <= len(b_parts) else (b_parts, a_parts)
    return longer[: len(shorter)] == shorter


def _path_inside(file_path: PurePosixPath, dir_path: PurePosixPath) -> bool:
    return (
        len(file_path.parts) > len(dir_path.parts)
        and file_path.parts[: len(dir_path.parts)] == dir_path.parts
    )


def _validate_cross_entry_claims(entries: list[Entry]) -> None:
    claimed = [(e.name, _claimed_dir(e)) for e in entries if e.operation == "extract_frames"]
    singles = [
        (e.name, PurePosixPath(e.output)) for e in entries if e.operation != "extract_frames"
    ]

    for i in range(len(claimed)):
        for j in range(i + 1, len(claimed)):
            name_a, dir_a = claimed[i]
            name_b, dir_b = claimed[j]
            if _dirs_overlap(dir_a, dir_b):
                raise ManifestError(
                    f"entries {name_a!r} and {name_b!r} claim overlapping directories under "
                    f"drafts: {dir_a} vs {dir_b}"
                )

    for name_s, file_s in singles:
        for name_c, dir_c in claimed:
            if _path_inside(file_s, dir_c):
                raise ManifestError(
                    f"entry {name_s!r}'s output {file_s} sits inside entry {name_c!r}'s "
                    f"claimed directory {dir_c}"
                )

    for i in range(len(singles)):
        for j in range(i + 1, len(singles)):
            name_a, file_a = singles[i]
            name_b, file_b = singles[j]
            # R63: be, contain, or sit inside one another — not just
            # equality. `a.png` against `a.png/b.png` is the containment
            # case, where the second entry needs a directory at the exact
            # path the first declares as a file; `_dirs_overlap` already
            # covers both be/contain/sit-inside and plain equality.
            if _dirs_overlap(file_a, file_b):
                raise ManifestError(
                    f"entries {name_a!r} and {name_b!r} declare outputs that collide, "
                    f"contain, or sit inside one another: {file_a} vs {file_b}"
                )
