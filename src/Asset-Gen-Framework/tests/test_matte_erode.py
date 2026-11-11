"""
`matte.erode`: shrinks the mask body (`mask >= 128`) by `erode` pixels --
a `MinFilter` of size `2*erode+1`, the mirror of how `grow` dilates the body
with a `MaxFilter` -- before the grow band is built. The pixels the mask
model over-claimed at its very edge are then decided by the colour key
instead of kept at full alpha, which is what fixes the pale rim a matte
model's over-claimed edge leaves once the frame is downscaled.
"""
from __future__ import annotations

import io

import numpy as np
import pytest
from PIL import Image

from conftest import extract_frames_entry, parse_single_json_document, write_manifest

from agf import matting

BACKGROUND = (230, 226, 230)   # #e6e2e6
FOREGROUND = (20, 20, 20)


def _png(arr: np.ndarray, mode: str) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(arr, mode).save(buf, format="PNG")
    return buf.getvalue()


def _overclaimed_scene():
    """A 64x64 flat background with a centred 24x24 dark square, and a mask
    that claims the square PLUS a 2-pixel ring beyond it -- the ring is
    still background colour in the frame, exactly what a mask model that
    over-claims a pixel or two at its edge produces."""
    size, sq, ring = 64, 24, 2
    off = (size - sq) // 2   # 20
    rgb = np.full((size, size, 3), BACKGROUND, dtype=np.uint8)
    rgb[off : off + sq, off : off + sq] = FOREGROUND

    mask = np.zeros((size, size), dtype=np.uint8)
    mask[off - ring : off + sq + ring, off - ring : off + sq + ring] = 255

    overclaimed = np.zeros((size, size), dtype=bool)
    overclaimed[off - ring : off + sq + ring, off - ring : off + sq + ring] = True
    overclaimed[off : off + sq, off : off + sq] = False   # the real square is not over-claimed

    # A patch comfortably inside the eroded body (erode=3 shrinks the 28x28
    # claimed square to a 22x22 body spanning [21, 43)) so it stays well
    # clear of both the ring and the erosion boundary itself.
    interior = np.zeros((size, size), dtype=bool)
    interior[off + 6 : off + sq - 6, off + 6 : off + sq - 6] = True

    return rgb, mask, overclaimed, interior


def test_erode_keys_out_the_overclaimed_ring_by_colour():
    """matte.erode: with erode > 0, pixels the mask over-claimed at its edge
    -- background colour, but marked as body by the mask -- are shrunk out
    of the body before the grow band is built, so the colour key (not the
    mask) decides them, and background-coloured over-claim ends transparent."""
    rgb, mask, overclaimed, interior = _overclaimed_scene()
    options = {"grow": 4, "erode": 3, "threshold": 60, "background": "#e6e2e6"}
    out = np.array(Image.open(io.BytesIO(matting.apply(_png(rgb, "RGB"), _png(mask, "L"), options))))

    assert np.all(out[..., 3][overclaimed] == 0), "over-claimed background ring must end fully transparent"
    assert np.all(out[..., 3][interior] == 255), "the real square's interior must stay fully opaque"
    assert np.all(out[..., :3][interior] == np.array(FOREGROUND)), "the real square's interior colour must be untouched"


def test_without_erode_the_overclaimed_ring_stays_opaque():
    """Control: with `erode` absent (today's behaviour), the mask alone
    decides the body, so the over-claimed background ring is never keyed
    out -- it stays at full alpha. This is the bug `erode` exists to fix,
    and proves the assertion above actually depends on the option."""
    rgb, mask, overclaimed, _interior = _overclaimed_scene()
    options = {"grow": 4, "threshold": 60, "background": "#e6e2e6"}
    out = np.array(Image.open(io.BytesIO(matting.apply(_png(rgb, "RGB"), _png(mask, "L"), options))))

    assert np.all(out[..., 3][overclaimed] == 255)


def _arm_scene():
    """A 24x24 dark square with a 4px-wide, 20px-long dark arm of the same
    colour sticking out to its right, and a mask that covers the square and
    the arm exactly -- a thin connected feature narrower than the erosion
    kernel (2*erode+1 = 7 for erode=3), which a naive whole-shape erosion
    would erase outright rather than treat as part of a body that should
    survive at full alpha. The canvas is generously wider than the arm's
    reach so neither `erode`'s MinFilter nor `grow`'s MaxFilter is affected
    by the canvas edge."""
    height, width, sq = 64, 100, 24
    off = 20
    rgb = np.full((height, width, 3), BACKGROUND, dtype=np.uint8)
    rgb[off : off + sq, off : off + sq] = FOREGROUND          # the square
    rgb[30:34, off + sq : off + sq + 20] = FOREGROUND         # the arm: 4px tall, 20px long

    mask = np.zeros((height, width), dtype=np.uint8)
    mask[off : off + sq, off : off + sq] = 255
    mask[30:34, off + sq : off + sq + 20] = 255

    arm = np.zeros((height, width), dtype=bool)
    arm[30:34, off + sq : off + sq + 20] = True

    return rgb, mask, arm


def test_erode_does_not_erase_a_thin_connected_feature():
    """A feature thinner than the erosion kernel, but attached to a wider
    body, must not be erased by `erode` -- it must still end at full alpha
    and its own true colour, not vanish because a naive whole-shape erosion
    would eat a 4px-wide arm under a 7px (2*erode+1) kernel."""
    rgb, mask, arm = _arm_scene()
    options = {"grow": 6, "erode": 3, "threshold": 60, "background": "#e6e2e6"}
    out = np.array(Image.open(io.BytesIO(matting.apply(_png(rgb, "RGB"), _png(mask, "L"), options))))

    assert np.all(out[..., 3][arm] == 255), "the thin arm must not be erased by erosion"
    assert np.all(out[..., :3][arm] == np.array(FOREGROUND)), "the arm must keep its own true colour"


BLOB = (240, 170, 90)


def _detached_blob_scene():
    """A 24x24 dark body and, 34px away from its right edge, a detached 5x5
    blob of its own distinct colour -- an isolated feature far too small for
    the erosion kernel (7px for erode=3) to leave anything of after erosion,
    and far outside `grow`'s reach from the body, so nothing in the
    colour-fill's nearest-body-pixel walk ever reaches it. The canvas is
    generously wider than the blob's position so neither filter is affected
    by the canvas edge."""
    height, width, sq = 64, 100, 24
    off = 20
    rgb = np.full((height, width, 3), BACKGROUND, dtype=np.uint8)
    rgb[off : off + sq, off : off + sq] = FOREGROUND                       # the body
    blob_col = off + sq + 34
    rgb[30:35, blob_col : blob_col + 5] = BLOB                             # the detached blob

    mask = np.zeros((height, width), dtype=np.uint8)
    mask[off : off + sq, off : off + sq] = 255
    mask[30:35, blob_col : blob_col + 5] = 255

    blob = np.zeros((height, width), dtype=bool)
    blob[30:35, blob_col : blob_col + 5] = True

    return rgb, mask, blob


def test_a_blob_the_colour_fill_never_reaches_keeps_its_own_colour():
    """A body pixel the nearest-body-pixel colour fill never reaches (it is
    eroded away and stays outside every other feature's grow band) must
    keep its own true colour -- not fall back to black (today's behaviour,
    because it ends at alpha 0 with no colour_fill contribution) and not
    the unrelated main body's colour either."""
    rgb, mask, blob = _detached_blob_scene()
    options = {"grow": 4, "erode": 3, "threshold": 60, "background": "#e6e2e6"}
    out = np.array(Image.open(io.BytesIO(matting.apply(_png(rgb, "RGB"), _png(mask, "L"), options))))

    assert np.all(out[..., 3][blob] > 0), "the blob must not be dropped to alpha 0"
    diff = np.abs(out[..., :3][blob].astype(int) - np.array(BLOB))
    assert np.all(diff <= 8), f"the blob must keep its own colour, not black or the body's: max diff {diff.max()}"


def test_manifest_accepts_matte_erode(project, run_cli):
    """The manifest's `matte:` block accepts `erode` as an optional key, the
    same way it accepts `grow` -- a legal declaration must not be rejected
    as an unrecognized matte key."""
    entry = extract_frames_entry(
        name="f1", output="f1/frame_{n:02d}.png",
        matte={"mask": "samples:video.mp4", "grow": 4, "erode": 3},
    )
    write_manifest(project, [entry])
    code, out, _ = run_cli(["list"] + project.config_args())
    assert code == 0, out


@pytest.mark.parametrize(
    "extra",
    [
        {"erode": -1},
        {"erode": "3"},
    ],
)
def test_manifest_rejects_bad_matte_erode(project, run_cli, extra):
    """`erode` must be a non-negative int -- a negative value or a
    non-integer (a string) is a manifest error naming `erode`, the same way
    a bad `grow` is."""
    entry = extract_frames_entry(
        name="f1", output="f1/frame_{n:02d}.png",
        matte={"mask": "samples:video.mp4", **extra},
    )
    write_manifest(project, [entry])
    code, out, _ = run_cli(["list"] + project.config_args())
    assert code == 3, out
    assert "erode" in parse_single_json_document(out)["error"]["message"]


def test_manifest_accepts_grow_zero_and_erode_not_smaller_than_grow(project, run_cli):
    """`grow: 0` (no erode at all) must stay legal -- it is long-established
    behaviour and must not be collaterally rejected by any rule relating
    `erode` to `grow`. And `erode` is not required to be smaller than
    `grow`: `grow: 3, erode: 3` is equally legal."""
    entries = [
        extract_frames_entry(
            name="f_grow0", output="f_grow0/frame_{n:02d}.png",
            matte={"mask": "samples:video.mp4", "grow": 0},
        ),
        extract_frames_entry(
            name="f_erode3", output="f_erode3/frame_{n:02d}.png",
            matte={"mask": "samples:video.mp4", "grow": 3, "erode": 3},
        ),
    ]
    write_manifest(project, entries)
    code, out, _ = run_cli(["list"] + project.config_args())
    assert code == 0, out
