"""
The extraction boundary — cli-v1 R62, R74.

Every video read happens through `extract` and nowhere else. It decodes with
PyAV (linked against ffmpeg's decoding libraries in-process), never by
shelling out to an external ffmpeg binary — R62 forbids depending on one.

Callers must always go through the module attribute (`frames.extract(...)`),
never `from agf.frames import extract`, so that a test's `monkeypatch.setattr`
on this module is actually honoured.
"""
from __future__ import annotations

import io
from pathlib import Path

import av
from PIL import Image

_PIL_FORMAT_BY_DECLARED = {"png": "PNG", "jpeg": "JPEG", "webp": "WEBP"}


class ExtractionError(Exception):
    """Raised by `extract` when the source cannot be read or decoded (R74)."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


def extract(source_path: Path, format: str) -> list[bytes]:
    """R74: read and decode the video at `source_path`, returning one
    already-encoded frame per element, in video order, encoded as the
    entry's declared `format`."""
    source_path = Path(source_path)
    pil_format = _PIL_FORMAT_BY_DECLARED.get(format)
    if pil_format is None:
        raise ExtractionError(
            f"cannot extract frames as {format!r}: extracted frames must be an image format"
        )
    if not source_path.exists():
        raise ExtractionError(f"source video not found: {source_path}")

    encoded_frames: list[bytes] = []
    try:
        with av.open(str(source_path)) as container:
            if not container.streams.video:
                raise ExtractionError(f"{source_path} has no video stream to extract frames from")
            stream = container.streams.video[0]
            for frame in container.decode(stream):
                if pil_format == "PNG" and "a" in frame.format.name:
                    # An alpha-carrying source (ProRes 4444, VP9 with
                    # alpha) keeps its matte: to_image() would flatten it.
                    image = Image.fromarray(frame.to_ndarray(format="rgba"), "RGBA")
                else:
                    image = frame.to_image()
                    if pil_format == "PNG":
                        image = image.convert("RGBA")
                buffer = io.BytesIO()
                image.save(buffer, format=pil_format)
                encoded_frames.append(buffer.getvalue())
    except ExtractionError:
        raise
    except Exception as exc:
        raise ExtractionError(f"could not decode {source_path}: {exc}") from exc

    if not encoded_frames:
        raise ExtractionError(f"no frames could be decoded from {source_path}")
    return encoded_frames
