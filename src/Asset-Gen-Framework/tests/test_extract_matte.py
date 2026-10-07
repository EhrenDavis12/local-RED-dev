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


def _hole_fill_scene():
    """A 40x40 flat background with a solid ring far from it in colour, and
    an interior the same colour as the background -- the situation a matte
    model that fills the hole between densely packed foreground shards
    produces: the mask covers the interior too, and there is nothing there
    to distinguish from the background except colour. A second patch, a
    near-background silver, sits elsewhere in the body -- a light colour
    that is genuinely foreground (a white band, steel blades) but close
    enough to the background to have been wrongly caught by a proportional
    key; effect must leave it alone. A third patch, a shard, sits solidly
    OUTSIDE the mask entirely and more than `grow` pixels from it -- what a
    matte model that loses small shards outright produces: `grow`'s few
    pixels of band can never reach it, so only a whole-frame key can bring
    it back."""
    background = (217, 217, 217)   # #D9D9D9
    ring = (40, 80, 200)
    silver = (200, 205, 210)       # colour-distance from background ~= 22
    shard = (250, 200, 30)         # colour-distance from background ~= 190
    rgb = np.full((40, 40, 3), background, dtype=np.uint8)
    rgb[8:32, 8:32] = ring
    rgb[14:26, 14:26] = background   # the "hole": flat background, but mask-covered
    rgb[16:20, 10:14] = silver       # near-background foreground, away from the hole and the mask edge
    rgb[1:5, 35:39] = shard          # a lost shard, well outside the mask and its grow band
    mask = np.zeros((40, 40), dtype=np.uint8)
    mask[8:32, 8:32] = 255           # the model filled the hole: one solid disc, no gap
    return rgb, mask


def test_effect_keys_the_body_and_the_whole_frame_outside_it():
    """matte.effect: in the body (mask >= 128), only a pixel within
    threshold * 0.25 of the background is a hard cutoff to alpha 0;
    everything else in the body keeps full alpha and its own colour
    untouched -- no proportional alpha, no un-blending, so a near-background
    foreground colour (silver, steel, a white band) is never dimmed. Outside
    the body, effect colour-keys the WHOLE frame, not a `grow`-pixel band
    around the mask: a shard the mask model lost outright, arbitrarily far
    from the mask, comes back at full alpha and its true colour, while exact
    background anywhere stays fully transparent. `grow` plays no part in
    this mode. `effect: false` (the default) must be unchanged from today's
    band-only behaviour -- asserted alongside so this test proves the flag
    does something, not just that the pipeline runs."""
    rgb, mask = _hole_fill_scene()
    frame, mask_png = _png(rgb, "RGB"), _png(mask, "L")

    without = np.array(Image.open(io.BytesIO(matting.apply(frame, mask_png, {"grow": 3, "feather": 0}))))
    assert without[20, 20, 3] == 255   # default: the leftover background inside the body stays opaque
    assert without[3, 37, 3] == 0      # default: the shard sits outside the mask and its grow band, so it's dropped

    with_effect = np.array(Image.open(io.BytesIO(matting.apply(frame, mask_png, {"grow": 3, "feather": 0, "effect": True}))))
    assert with_effect[20, 20, 3] == 0                        # body: the leftover background is keyed out
    assert tuple(with_effect[20, 20, :3]) == (0, 0, 0)        # transparent pixels stay black
    assert with_effect[10, 10, 3] == 255                      # body: the real foreground (the ring) is untouched
    assert with_effect[18, 12, 3] == 255                      # body: near-background silver (~22 away) is NOT keyed
    assert tuple(with_effect[18, 12, :3]) == (200, 205, 210)  # ... and its colour is left unblended
    assert with_effect[3, 37, 3] == 255                       # outside the body: a lost shard is fully restored
    assert tuple(with_effect[3, 37, :3]) == (250, 200, 30)    # ... at its true, unblended colour
    assert with_effect[2, 2, 3] == 0                          # outside the body: exact background, far from the mask, stays out


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


def test_generate_accepts_matte_effect_and_it_reaches_apply(project, run_cli, fake_extraction):
    """matte.effect: true must be a legal manifest declaration (not just
    rejected as an unknown key), and the option it turns on must actually
    reach matting.apply through the real extract_frames path -- not just the
    unit-level call in test_effect_keys_the_body_and_the_whole_frame_outside_it."""
    (project.samples / "mask.mp4").write_bytes(b"not a real video, just needs to exist")
    entry = extract_frames_entry(
        name="f1", output="f1/frame_{n:02d}.png",
        matte={"mask": "samples:mask.mp4", "grow": 3, "feather": 0, "effect": True},
    )
    write_manifest(project, [entry])
    rgb, mask = _hole_fill_scene()

    def side_effect(source_path, format):
        return [_png(mask, "L")] if source_path.name == "mask.mp4" else [_png(rgb, "RGB")]

    fake_extraction(side_effect=side_effect)
    code, out, _ = run_cli(["generate", "f1"] + project.config_args())
    assert code == 0, out   # a legal matte key, accepted by the manifest
    with Image.open(project.drafts / "f1" / "frame_01.png") as img:
        px = np.array(img.convert("RGBA"))
    assert px[20, 20, 3] == 0     # the option reached apply: the hole is keyed out, not left opaque
    assert px[10, 10, 3] == 255   # the real foreground (the ring) is untouched
    assert px[18, 12, 3] == 255   # near-background silver (~22 away) is NOT keyed, even through the CLI path
    assert px[3, 37, 3] == 255    # outside the body: a lost shard is restored across the whole frame, even through the CLI path


def test_extract_frames_resolves_auto_background_once_from_the_first_frame(project, run_cli, fake_extraction):
    """matte.background: auto (the default) must be resolved ONCE, from the
    first decoded source frame's corners, and reused for every frame -- not
    re-measured per frame. A burst's later frames can have their corners
    covered by shards; re-measuring per frame would pick up the shard
    colour as "background" and, under effect: true, key the real, untouched
    background as opaque instead of transparent."""
    (project.samples / "mask.mp4").write_bytes(b"not a real video, just needs to exist")
    background = (217, 217, 217)
    fg = (40, 80, 200)
    shard = (250, 200, 30)

    frame0 = np.full((40, 40, 3), background, dtype=np.uint8)
    frame0[18:22, 18:22] = fg   # a small central blob under the mask, in both frames -- corners stay clean

    frame1 = np.full((40, 40, 3), background, dtype=np.uint8)
    frame1[18:22, 18:22] = fg
    for rows in (slice(0, 4), slice(36, 40)):
        for cols in (slice(0, 4), slice(36, 40)):
            frame1[rows, cols] = shard   # frame 1's corners are covered by shards, like a late burst frame

    mask = np.zeros((40, 40), dtype=np.uint8)
    mask[18:22, 18:22] = 255   # covers only the small central blob, in both frames

    entry = extract_frames_entry(
        name="f1", output="f1/frame_{n:02d}.png",
        matte={"mask": "samples:mask.mp4", "effect": True, "feather": 0},
    )
    write_manifest(project, [entry])

    def side_effect(source_path, format):
        if source_path.name == "mask.mp4":
            return [_png(mask, "L"), _png(mask, "L")]
        return [_png(frame0, "RGB"), _png(frame1, "RGB")]

    fake_extraction(side_effect=side_effect)
    code, out, _ = run_cli(["generate", "f1"] + project.config_args())
    assert code == 0, out
    with Image.open(project.drafts / "f1" / "frame_02.png") as img:
        px = np.array(img.convert("RGBA"))
    # A per-frame estimate would have taken frame 1's own (shard) corners as
    # "background" and, being far from the true grey, left the real
    # background opaque instead of keying it out.
    assert px[5, 20, 3] == 0
    # The genuine foreground the shards represent still stays opaque, at its
    # true, unblended colour.
    assert px[1, 1, 3] == 255
    assert tuple(px[1, 1, :3]) == shard


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
     {"mask": "samples:mask.mp4", "grow": -1}, {"mask": "samples:nope.mp4"},
     {"mask": "samples:mask.mp4", "effect": "yes"}],
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
