"""
Running one entry's step and committing it — cli-v1 R19/R20, R27 steps
9-12, R54, R57-R61, R67-R68, R71, R74-R75.
"""
from __future__ import annotations

import io
import json
import os
import shutil
import uuid
from pathlib import Path, PurePosixPath

from PIL import Image

import agf.frames as frames
import agf.matting as matting
import agf.provider as provider
from agf.checks import check_format, check_frame_sizes, check_layout
from agf.config import Config
from agf.errors import (
    AgfError,
    ChecksFailedError,
    CredentialError,
    DestinationError,
    ExtractionFailedError,
    ProviderCallError,
)
from agf.manifest import Entry
from agf.refs import resolve_reference


def get_credential() -> str:
    """R29/R30: read from the environment and nowhere else."""
    token = os.environ.get("REPLICATE_API_TOKEN")
    if not token:
        raise CredentialError("REPLICATE_API_TOKEN is not set (or is empty) in the environment")
    return token


def execute_entry(config: Config, entry: Entry, credential: str | None) -> tuple[list[dict], str | None, object]:
    """Run `entry`'s step (R27 step 10), check its result (step 11), commit
    it (step 12), and return (file_results, model_version, seed) for the
    success document (R19/R20)."""
    drafts = config.drafts
    run_id = uuid.uuid4().hex
    multi_file = entry.operation == "extract_frames"

    if multi_file:
        destination_rel = str(PurePosixPath(entry.output).parent)
    else:
        destination_rel = entry.output

    parent_rel = PurePosixPath(destination_rel).parent
    parent_abs = drafts if str(parent_rel) == "." else drafts / parent_rel
    try:
        parent_abs.mkdir(parents=True, exist_ok=True)  # R12
    except OSError as exc:
        # R12: creating an intermediate directory can fail on a manifest
        # that is entirely valid — a plain file already occupies the path
        # a directory is needed at. Nothing has been called, spent or
        # placed yet, so this is the same "Destination" failure R67's
        # commit-rename failure is (R28 code 10), not an internal one.
        raise DestinationError(
            f"could not create the directory {parent_abs} for entry {entry.name!r}'s "
            f"output: something that is not a directory already occupies that path ({exc})",
            remedy=f"remove or rename whatever occupies {parent_abs}, then retry",
        ) from exc

    destination_abs = drafts / destination_rel

    # Capture what already exists, before anything is touched, for R20's
    # per-file `replaced` reporting.
    if multi_file:
        prior_names = (
            {p.name for p in destination_abs.iterdir()} if destination_abs.exists() else set()
        )
    else:
        prior_exists = destination_abs.exists()

    staging_dir = parent_abs / f".agf-tmp-{run_id}"
    staging_dir.mkdir()
    marker_path = parent_abs / f".agf-tmp-{run_id}.json"
    displaced_rel = (
        str(parent_rel / f".agf-old-{run_id}")
        if str(parent_rel) != "."
        else f".agf-old-{run_id}"
    )
    _write_marker(marker_path, destination_rel, displaced_rel)

    try:
        model_version = None
        seed = None
        frame_size_detail = None
        if entry.operation == "model":
            model_version, seed, files, output_count_status = _run_model_op(
                config, entry, credential, destination_rel
            )
            frame_size_status = "skipped"
        elif entry.operation == "assemble_sheet":
            files, frame_size_status, frame_size_detail = _run_assemble_sheet(config, entry)
            output_count_status = "skipped"
        else:
            files = _run_extract_frames(config, entry)
            frame_size_status = "skipped"
            output_count_status = "skipped"

        for basename, data in files:
            (staging_dir / basename).write_bytes(data)

        checks_list, all_passed, failure_message = _run_checks(
            entry,
            files,
            output_count_status,
            frame_size_status,
            frame_size_detail,
            destination_rel,
            multi_file,
        )
        if not all_passed:
            raise ChecksFailedError(
                failure_message
                or f"one or more checks failed for entry {entry.name!r}; nothing was committed",
                remedy="inspect the failing check(s) in error.checks and fix the entry or its inputs",
                checks=checks_list,
            )
    except provider.ProviderError as exc:
        _cleanup_failed_run(staging_dir, marker_path)
        raise ProviderCallError(str(exc)) from exc
    except frames.ExtractionError as exc:
        _cleanup_failed_run(staging_dir, marker_path)
        raise ExtractionFailedError(
            str(exc), remedy=f"check that the source video ({entry.source}) is readable and decodable"
        ) from exc
    except AgfError:
        _cleanup_failed_run(staging_dir, marker_path)
        raise
    except (Exception, KeyboardInterrupt):
        # R68 names an interrupt directly among the cases that must remove
        # staging and then its marker — KeyboardInterrupt is a
        # BaseException, not an Exception, so it needs naming explicitly.
        _cleanup_failed_run(staging_dir, marker_path)
        raise

    _commit(drafts, staging_dir, marker_path, destination_abs, displaced_rel, multi_file, files)

    file_results = []
    for (basename, data), check_entry in zip(files, checks_list):
        if multi_file:
            replaced = basename in prior_names
        else:
            replaced = prior_exists
        abs_path = drafts / check_entry["path"]
        file_results.append(
            {
                "path": str(abs_path),
                "format": entry.format,
                "bytes": abs_path.stat().st_size,
                "replaced": replaced,
                "checks": check_entry["checks"],
            }
        )

    return file_results, model_version, seed


def _write_marker(marker_path: Path, destination_rel: str, displaced_rel: str) -> None:
    with open(marker_path, "w") as fh:
        json.dump({"destination": destination_rel, "displaced": displaced_rel}, fh)
        fh.flush()
        os.fsync(fh.fileno())

    # The marker's own bytes are durable once fsynced above, but the
    # directory entry that names it is a separate write the filesystem may
    # not have made durable yet — a power loss can leave the file gone from
    # the directory even though its contents were flushed. fsync the parent
    # directory's fd too, so the marker's existence itself survives a crash.
    dir_fd = os.open(str(marker_path.parent), os.O_RDONLY)
    try:
        os.fsync(dir_fd)
    except OSError:
        pass  # best-effort: not every filesystem supports fsync on a directory
    finally:
        os.close(dir_fd)


def _cleanup_failed_run(staging_dir: Path, marker_path: Path) -> None:
    """R68: a run that exits before committing removes its staging directory
    and everything in it, then its marker."""
    if staging_dir.exists():
        shutil.rmtree(staging_dir, ignore_errors=True)
    marker_path.unlink(missing_ok=True)


def _run_model_op(config: Config, entry: Entry, credential: str, destination_rel: str):
    inputs = dict(entry.inputs or {})
    if entry.prompt is not None:
        key = entry.prompt_key if entry.prompt_key is not None else "prompt"
        inputs[key] = entry.prompt
    for key, ref in (entry.input_files or {}).items():
        context = f"entry {entry.name!r} input_files[{key!r}]"
        if isinstance(ref, list):
            # A model input that takes several files (reference images,
            # say) is declared as a list of references and arrives as a
            # list of URLs, in the order written.
            inputs[key] = [
                provider.upload(resolve_reference(config, one, context=context), credential)
                for one in ref
            ]
        else:
            inputs[key] = provider.upload(resolve_reference(config, ref, context=context), credential)

    result = provider.run(entry.resolved_model, inputs, credential)
    version = result["version"]
    provider_seed = result.get("seed")
    declared_seed = (entry.inputs or {}).get("seed")
    seed = declared_seed if declared_seed is not None else provider_seed

    outputs = result["outputs"]
    if len(outputs) != 1:
        checks_list = [
            {
                "path": destination_rel,
                "checks": {
                    "format": "skipped",
                    "layout": "skipped",
                    "frame_size": "skipped",
                    "frame_count": "skipped",
                    "output_count": "fail",
                },
            }
        ]
        raise ChecksFailedError(
            f"provider returned {len(outputs)} file(s) for entry {entry.name!r}, "
            "which declares one output",
            remedy="the model is not behaving as the entry expects; check the model or its inputs",
            checks=checks_list,
        )

    basename = PurePosixPath(entry.output).name
    return version, seed, [(basename, outputs[0])], "pass"


def _run_assemble_sheet(config: Config, entry: Entry):
    frame_paths = [
        resolve_reference(config, ref, context=f"entry {entry.name!r} frames") for ref in entry.frames
    ]
    frame_size_status, frame_size_detail = check_frame_sizes(frame_paths, entry.frame_size)
    basename = PurePosixPath(entry.output).name

    # The canvas is always built at the full declared layout/frame_size,
    # even when a frame already failed its size check: the entry still has
    # exactly one output, and the checks step below is what actually
    # rejects it (R71) — the format check must still see real PNG bytes,
    # not a placeholder, so a check that already passed is reported
    # accurately rather than trimmed away (R71).
    columns, rows = entry.layout["columns"], entry.layout["rows"]
    frame_w, frame_h = entry.frame_size
    canvas = Image.new("RGBA", (columns * frame_w, rows * frame_h), (0, 0, 0, 0))
    for index, path in enumerate(frame_paths):
        col, row = index % columns, index // columns
        try:
            with Image.open(path) as frame_img:
                frame_rgba = frame_img.convert("RGBA")
                # No mask: pasting an RGBA image with itself as the mask
                # composites (premultiplies colour, squares alpha) instead
                # of copying. The declared pixels must land in the sheet
                # exactly.
                canvas.paste(frame_rgba, (col * frame_w, row * frame_h))
        except Exception:
            # Not decodable as an image at all (R61/defect 9) — already a
            # frame_size failure (check_frame_sizes above), so the run will
            # be rejected regardless; leave this cell as it was rather than
            # crash building a canvas that will be discarded.
            continue

    buffer = io.BytesIO()
    canvas.save(buffer, format="PNG")
    return [(basename, buffer.getvalue())], frame_size_status, frame_size_detail


def _run_extract_frames(config: Config, entry: Entry):
    source_path = resolve_reference(config, entry.source, context=f"entry {entry.name!r} source")
    extracted = frames.extract(source_path, entry.format)
    if entry.matte is not None:
        mask_path = resolve_reference(config, entry.matte["mask"], context=f"entry {entry.name!r} matte.mask")
        masks = frames.extract(mask_path, entry.format)
        if len(masks) != len(extracted):
            raise ChecksFailedError(
                f"matte mask has {len(masks)} frame(s) but the source has {len(extracted)}",
                remedy="the mask video must be made from this exact source video",
                checks=[],
            )
        extracted = [
            matting.apply(frame, mask, entry.matte) for frame, mask in zip(extracted, masks)
        ]
    if entry.resize is not None:
        extracted = [_fit_frame(data, entry.resize, entry.format) for data in extracted]
    basename_template = PurePosixPath(entry.output).name
    return [(basename_template.format(n=i), data) for i, data in enumerate(extracted, start=1)]


def _fit_frame(data: bytes, size: list, format: str) -> bytes:
    """Scale one extracted frame to fit inside `size`, keeping its aspect
    ratio, centred on a canvas of exactly `size`. PNG canvases are
    transparent; other formats are black. This is the one place the
    framework scales, and only because a video model cannot be asked for
    game-sized frames while a sheet has to be."""
    width, height = size
    with Image.open(io.BytesIO(data)) as source:
        source.load()
        if format == "png":
            image = source.convert("RGBA")
            canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        else:
            image = source.convert("RGB")
            canvas = Image.new("RGB", (width, height), (0, 0, 0))
    scale = min(width / image.width, height / image.height)
    fitted_size = (max(1, round(image.width * scale)), max(1, round(image.height * scale)))
    if format == "png":
        fitted = _resize_premultiplied(image, fitted_size)
    else:
        fitted = image.resize(fitted_size, Image.LANCZOS)
    offset = ((width - fitted_size[0]) // 2, (height - fitted_size[1]) // 2)
    canvas.paste(fitted, offset)
    buffer = io.BytesIO()
    canvas.save(buffer, format={"png": "PNG", "jpeg": "JPEG", "webp": "WEBP"}[format])
    return buffer.getvalue()


def _resize_premultiplied(image: Image.Image, size: tuple) -> Image.Image:
    """Resize RGBA with the colour premultiplied by alpha, so transparent
    pixels' colour cannot bleed into the edge: a straight RGBA resize mixes
    whatever colour sits under alpha 0 into its neighbours and paints a
    fringe around every outline."""
    import numpy as np

    arr = np.asarray(image, dtype=np.float32)
    alpha = arr[..., 3:4] / 255.0
    channels = [arr[..., i] * alpha[..., 0] for i in range(3)] + [arr[..., 3]]
    resized = [np.asarray(Image.fromarray(c).resize(size, Image.LANCZOS)) for c in channels]
    out_alpha = np.clip(resized[3], 0, 255)
    denominator = np.maximum(out_alpha / 255.0, 1e-3)[..., None]
    rgb = np.clip(np.dstack(resized[:3]) / denominator, 0, 255)
    rgb[out_alpha < 1] = 0
    return Image.fromarray(np.dstack([rgb, out_alpha]).round().astype(np.uint8), "RGBA")


def _run_checks(
    entry, files, output_count_status, frame_size_status, frame_size_detail, destination_rel, multi_file
):
    format_results = []
    format_details = []
    for _basename, data in files:
        status, detail = check_format(data, entry.format)
        format_results.append(status)
        if status == "fail" and detail:
            format_details.append(detail)

    if entry.type == "sprite_sheet":
        layout_result, layout_detail = check_layout(files[0][1], entry.layout, entry.frame_size)
    else:
        layout_result, layout_detail = "skipped", None

    if entry.operation == "extract_frames" and entry.frame_count is not None:
        if len(files) == entry.frame_count:
            frame_count_result, frame_count_detail = "pass", None
        else:
            frame_count_result = "fail"
            frame_count_detail = (
                f"declared frame_count is {entry.frame_count}, "
                f"the video yielded {len(files)} frame(s)"
            )
    else:
        frame_count_result, frame_count_detail = "skipped", None

    checks_list = []
    for (basename, _data), fmt_result in zip(files, format_results):
        if multi_file:
            path = str(PurePosixPath(destination_rel) / basename)
        else:
            path = destination_rel
        checks_list.append(
            {
                "path": path,
                "checks": {
                    "format": fmt_result,
                    "layout": layout_result,
                    "frame_size": frame_size_status,
                    "frame_count": frame_count_result,
                    "output_count": output_count_status,
                },
            }
        )

    all_passed = (
        all(r == "pass" for r in format_results)
        and layout_result != "fail"
        and frame_size_status != "fail"
        and frame_count_result != "fail"
        and output_count_status != "fail"
    )

    failure_message = None
    if not all_passed:
        details = list(format_details)
        if layout_result == "fail" and layout_detail:
            details.append(layout_detail)
        if frame_size_status == "fail" and frame_size_detail:
            details.append(frame_size_detail)
        if frame_count_result == "fail" and frame_count_detail:
            details.append(frame_count_detail)
        if details:
            failure_message = f"check(s) failed for entry {entry.name!r}: " + "; ".join(details)

    return checks_list, all_passed, failure_message


def _commit(
    drafts: Path,
    staging_dir: Path,
    marker_path: Path,
    destination_abs: Path,
    displaced_rel: str,
    multi_file: bool,
    files: list,
) -> None:
    """R67: displace, then rename, then delete."""
    displaced_abs = drafts / displaced_rel
    displaced_made = False

    try:
        if multi_file:
            # Step 2 (multi-file only): displace an existing destination.
            if destination_abs.exists():
                os.rename(destination_abs, displaced_abs)
                displaced_made = True
            # Step 3: a single rename onto the now-vacant destination.
            os.rename(staging_dir, destination_abs)
        else:
            # Single-file entry: one atomic rename onto the declared path,
            # whether or not a file was already there (R67) — no displace
            # step for this case.
            basename = files[0][0]
            staged_file = staging_dir / basename
            os.replace(staged_file, destination_abs)
    except OSError as exc:
        if displaced_made and displaced_abs.exists() and not destination_abs.exists():
            os.rename(displaced_abs, destination_abs)
        shutil.rmtree(staging_dir, ignore_errors=True)
        marker_path.unlink(missing_ok=True)
        raise DestinationError(
            f"could not commit entry's output to {destination_abs}: {exc}",
            remedy=f"resolve the obstruction at {destination_abs} and retry",
        ) from exc

    # Steps 4-6: best-effort cleanup. A failure here is not a commit
    # failure (R67) — stop at the first failure and leave the rest for the
    # next sweep.
    try:
        if displaced_made:
            _remove_tree(displaced_abs)
        if not multi_file:
            staging_dir.rmdir()
        marker_path.unlink()
    except OSError:
        pass


def _remove_tree(path: Path) -> None:
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink()
