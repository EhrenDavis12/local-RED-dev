"""
`matte` on `operation: extract_frames`: alpha comes from a mask video made
from the same source, and the outline a learned matte shaved off is restored
by colour distance from the flat background. Legal nowhere else.
"""
from __future__ import annotations

import io

import numpy as np
import pytest
from PIL import Image

from conftest import extract_frames_entry, image_model_entry, parse_single_json_document, write_manifest

from agf import matting


def _png(arr: np.ndarray, mode: str) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(arr, mode).save(buf, format="PNG")
    return buf.getvalue()


def _scene():
    """A 40x40 flat light-grey background with a dark-outlined blue square,
    and a mask that stops two pixels short of the outline on every side."""
    rgb = np.full((40, 40, 3), (230, 225, 229), dtype=np.uint8)
    rgb[10:30, 10:30] = (20, 20, 25)      # outline
    rgb[13:27, 13:27] = (40, 80, 200)     # body
    mask = np.zeros((40, 40), dtype=np.uint8)
    mask[12:28, 12:28] = 255              # eats the outline
    return rgb, mask


def test_apply_restores_the_outline_and_keeps_the_background_out():
    rgb, mask = _scene()
    out = np.array(Image.open(io.BytesIO(matting.apply(_png(rgb, "RGB"), _png(mask, "L"), {"grow": 3, "feather": 0}))))
    assert out.shape == (40, 40, 4)
    assert out[10, 20, 3] == 255 and out[29, 20, 3] == 255   # outline rows restored
    assert out[20, 10, 3] == 255 and out[20, 29, 3] == 255   # outline columns restored
    assert out[9, 20, 3] == 0 and out[20, 9, 3] == 0         # background inside the grow band stays out
    assert out[20, 20, 3] == 255                             # body untouched
    assert tuple(out[20, 20, :3]) == (40, 80, 200)


def test_apply_unblends_a_half_covered_edge_pixel():
    """An edge pixel that is half outline, half background gets half alpha and
    the outline's colour -- not the blend, which would read as a light rim."""
    rgb, mask = _scene()
    rgb[10, :, :] = ((np.array((20, 20, 25)) + np.array((230, 225, 229))) / 2).astype(np.uint8)
    out = np.array(Image.open(io.BytesIO(matting.apply(_png(rgb, "RGB"), _png(mask, "L"), {"grow": 3, "feather": 0}))))
    alpha = out[10, 20, 3]
    assert 90 < alpha < 170, alpha
    assert out[10, 20, :3].max() < 70, out[10, 20, :3]   # dark, like the outline
    assert tuple(out[5, 5, :3]) == (0, 0, 0) and out[5, 5, 3] == 0   # transparent pixels are black


def test_fit_frame_does_not_bleed_transparent_colour_into_the_edge():
    from agf.execute import _fit_frame

    arr = np.zeros((64, 64, 4), dtype=np.uint8)
    arr[..., :3] = 255                       # white everywhere ...
    arr[16:48, 16:48] = (20, 20, 25, 255)    # ... but only a dark square is visible
    arr[..., 3][arr[..., 3] == 0] = 0
    out = np.array(Image.open(io.BytesIO(_fit_frame(_png(arr, "RGBA"), [32, 32], "png"))))
    edge = out[out[..., 3] > 0]
    assert edge[:, :3].max() < 60, edge[:, :3].max()     # no white crept in


def test_apply_with_no_grow_is_just_the_mask():
    rgb, mask = _scene()
    out = np.array(Image.open(io.BytesIO(matting.apply(_png(rgb, "RGB"), _png(mask, "L"), {"grow": 0, "feather": 0}))))
    assert out[10, 20, 3] == 0 and out[20, 20, 3] == 255


def test_explicit_background_colour_is_used():
    rgb, mask = _scene()
    # Declare the background as the body colour: the band then keeps grey and drops nothing blue.
    out = np.array(Image.open(io.BytesIO(matting.apply(_png(rgb, "RGB"), _png(mask, "L"), {"grow": 3, "feather": 0, "background": "#2850c8"}))))
    assert out[9, 20, 3] == 255


def test_generate_applies_the_matte_from_a_mask_video(project, run_cli, fake_extraction):
    (project.samples / "mask.mp4").write_bytes(b"not a real video, just needs to exist")
    entry = extract_frames_entry(
        name="f1", output="f1/frame_{n:02d}.png", matte={"mask": "samples:mask.mp4", "grow": 3, "feather": 0}
    )
    write_manifest(project, [entry])
    rgb, mask = _scene()

    def side_effect(source_path, format):
        return [_png(mask, "L")] if source_path.name == "mask.mp4" else [_png(rgb, "RGB")]

    fake_extraction(side_effect=side_effect)
    code, out, _ = run_cli(["generate", "f1"] + project.config_args())
    assert code == 0, out
    with Image.open(project.drafts / "f1" / "frame_01.png") as img:
        px = np.array(img.convert("RGBA"))
    assert px[10, 20, 3] == 255 and px[9, 20, 3] == 0


def test_mask_frame_count_must_match(project, run_cli, fake_extraction):
    (project.samples / "mask.mp4").write_bytes(b"x")
    write_manifest(project, [extract_frames_entry(name="f1", matte={"mask": "samples:mask.mp4"})])
    rgb, mask = _scene()
    fake_extraction(side_effect=lambda p, f: [_png(mask, "L")] * 2 if p.name == "mask.mp4" else [_png(rgb, "RGB")])
    code, out, _ = run_cli(["generate", "f1"] + project.config_args())
    assert code != 0
    assert "frame(s)" in out


@pytest.mark.parametrize(
    "matte",
    ["samples:mask.mp4", {}, {"mask": "samples:mask.mp4", "bogus": 1}, {"mask": "samples:mask.mp4", "background": "grey"},
     {"mask": "samples:mask.mp4", "grow": -1}, {"mask": "samples:nope.mp4"}],
)
def test_bad_matte_declarations_are_manifest_errors(project, run_cli, matte):
    (project.samples / "mask.mp4").write_bytes(b"x")
    write_manifest(project, [extract_frames_entry(name="f1", matte=matte)])
    code, out, _ = run_cli(["list"] + project.config_args())
    assert code == 3, out
    assert "matte" in parse_single_json_document(out)["error"]["message"] or "nope" in out


def test_matte_is_illegal_outside_extract_frames(project, run_cli):
    (project.samples / "mask.mp4").write_bytes(b"x")
    write_manifest(project, [image_model_entry(name="img", matte={"mask": "samples:mask.mp4"})])
    code, out, _ = run_cli(["list"] + project.config_args())
    assert code == 3
    assert "extract_frames" in parse_single_json_document(out)["error"]["message"]
