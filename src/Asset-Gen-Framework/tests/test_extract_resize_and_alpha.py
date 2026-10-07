"""
`resize` on `operation: extract_frames`, and alpha surviving extraction.

A video model cannot be asked for game-sized frames, while `assemble_sheet`
refuses a frame that is not exactly `frame_size` — so `extract_frames` may
declare `resize: [w, h]` and every frame is fitted into that canvas,
aspect preserved, centred, transparent where nothing landed. `resize` is
legal nowhere else. And a source that carries alpha (ProRes 4444, VP9 with
alpha) keeps it: a matted video is the whole point of extracting frames.
"""
from __future__ import annotations

import io

import numpy as np
import pytest
from PIL import Image

from conftest import (
    extract_frames_entry,
    image_model_entry,
    parse_single_json_document,
    png_bytes,
    write_manifest,
)

# Bound at import time, before the autouse fixture replaces the module
# attribute with its network-and-video guard: this one test reads a real,
# locally encoded video on purpose.
from agf.frames import extract as real_extract


def _decode(path):
    with Image.open(path) as img:
        img.load()
        return img.convert("RGBA")


def test_resize_fits_each_frame_into_the_declared_canvas(project, run_cli, fake_extraction):
    entry = extract_frames_entry(name="f1", output="f1/frame_{n:02d}.png", resize=[32, 32])
    write_manifest(project, [entry])
    wide = png_bytes(size=(64, 16), color=(255, 0, 0, 255))
    tall = png_bytes(size=(8, 64), color=(0, 0, 255, 255))
    fake_extraction(frames_result=[wide, tall])

    code, out, _ = run_cli(["generate", "f1"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 0, doc

    frame_1 = _decode(project.drafts / "f1" / "frame_01.png")
    frame_2 = _decode(project.drafts / "f1" / "frame_02.png")
    assert frame_1.size == (32, 32)
    assert frame_2.size == (32, 32)
    px = np.array(frame_1)
    # The wide frame scales to 32x8, centred: rows 12..19 are red and opaque,
    # everything above and below is fully transparent.
    assert px[15, 15].tolist() == [255, 0, 0, 255]
    assert px[2, 15, 3] == 0 and px[29, 15, 3] == 0
    px = np.array(frame_2)
    # The tall frame scales to 4x32, centred: columns 14..17 are blue.
    assert px[15, 15].tolist() == [0, 0, 255, 255]
    assert px[15, 2, 3] == 0 and px[15, 29, 3] == 0


def test_resize_is_recorded(project, run_cli, fake_extraction):
    import json

    entry = extract_frames_entry(name="f1", output="f1/frame_{n:02d}.png", resize=[16, 16])
    write_manifest(project, [entry])
    fake_extraction(frames_result=[png_bytes()])
    code, out, _ = run_cli(["generate", "f1"] + project.config_args())
    assert code == 0, out
    written = json.loads(project.record_path.read_text())["entries"]["f1"]
    assert written["resize"] == [16, 16]


@pytest.mark.parametrize(
    "bad",
    [[0, 16], [16], "16x16", [16, 16, 16], [16.0, 16], [True, 16]],
)
def test_resize_must_be_two_positive_integers(project, run_cli, bad):
    write_manifest(project, [extract_frames_entry(name="f1", resize=bad)])
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 3
    assert "resize" in doc["error"]["message"]


def test_resize_is_illegal_outside_extract_frames(project, run_cli):
    write_manifest(project, [image_model_entry(name="img", resize=[16, 16])])
    code, out, _ = run_cli(["list"] + project.config_args())
    doc = parse_single_json_document(out)
    assert code == 3
    assert "resize" in doc["error"]["message"]
    assert "extract_frames" in doc["error"]["message"]


def test_extraction_keeps_alpha_from_a_prores_4444_source(tmp_path):
    import av

    source = tmp_path / "matted.mov"
    try:
        with av.open(str(source), "w") as container:
            stream = container.add_stream("prores_ks", rate=8)
            stream.width, stream.height = 16, 16
            stream.pix_fmt = "yuva444p10le"
            stream.options = {"profile": "4444"}
            for alpha in (255, 128, 0):
                rgba = np.zeros((16, 16, 4), dtype=np.uint8)
                rgba[..., 1] = 255
                rgba[..., 3] = alpha
                frame = av.VideoFrame.from_ndarray(rgba, format="rgba")
                for packet in stream.encode(frame):
                    container.mux(packet)
            for packet in stream.encode():
                container.mux(packet)
    except Exception as exc:  # pragma: no cover - depends on the ffmpeg build
        pytest.skip(f"this ffmpeg build cannot encode ProRes 4444 with alpha: {exc}")

    extracted = real_extract(source, "png")
    assert len(extracted) == 3
    alphas = [np.array(Image.open(io.BytesIO(data)).convert("RGBA"))[8, 8, 3] for data in extracted]
    assert alphas[0] > 240
    assert 100 < alphas[1] < 160
    assert alphas[2] < 15
