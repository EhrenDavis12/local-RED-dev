"""
`matting.apply`'s grow band: a band pixel the colour key itself measures as
fully foreground (its distance from the background already reaches or
exceeds "full", the outermost body ring's own measured distance) must keep
its own true colour, not the nearest-body-pixel fill colour the band uses
for a genuinely blended edge pixel. The fill exists to guess an un-blended
colour for a pixel that IS a background/foreground mix; a pixel the key
already trusts as solid foreground was never a guess to begin with, and
overwriting it with the nearest core pixel's colour repaints a real edge
(an outline the mask model shaved off whole) in the body's colour instead
of its own.
"""
from __future__ import annotations

import io

import numpy as np
from PIL import Image

from agf import matting

BACKGROUND = (230, 226, 230)   # #e6e2e6
RED = (200, 40, 40)
OUTLINE = (20, 20, 20)

GREEN_BACKGROUND = (0, 255, 0)   # #00ff00
SILVER = (220, 220, 220)


def _png(arr: np.ndarray, mode: str) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(arr, mode).save(buf, format="PNG")
    return buf.getvalue()


def _outlined_scene():
    """A 64x64 flat background, a 20x20 red square with a 2px black outline
    around it, and a mask that covers only the red square -- the model
    shaved the whole outline off, exactly like a matte model does to a dark
    line against a flat background."""
    size, outline_w, sq = 64, 2, 20
    off_outline = (size - (sq + 2 * outline_w)) // 2   # 20
    off_sq = off_outline + outline_w                    # 22

    rgb = np.full((size, size, 3), BACKGROUND, dtype=np.uint8)
    rgb[off_outline : off_outline + sq + 2 * outline_w, off_outline : off_outline + sq + 2 * outline_w] = OUTLINE
    rgb[off_sq : off_sq + sq, off_sq : off_sq + sq] = RED

    mask = np.zeros((size, size), dtype=np.uint8)
    mask[off_sq : off_sq + sq, off_sq : off_sq + sq] = 255   # only the red square

    outline_mask = np.zeros((size, size), dtype=bool)
    outline_mask[off_outline : off_outline + sq + 2 * outline_w, off_outline : off_outline + sq + 2 * outline_w] = True
    outline_mask[off_sq : off_sq + sq, off_sq : off_sq + sq] = False

    return rgb, mask, outline_mask


def test_a_fully_foreground_band_pixel_keeps_its_own_colour_not_the_fill():
    rgb, mask, outline_mask = _outlined_scene()
    options = {"grow": 3, "threshold": 60, "background": "#e6e2e6"}
    out = np.array(Image.open(io.BytesIO(matting.apply(_png(rgb, "RGB"), _png(mask, "L"), options))))

    alpha = out[..., 3]
    colour = out[..., :3].astype(int)

    assert np.all(alpha[outline_mask] == 255), "the shaved outline must be restored at full alpha"
    diff = np.abs(colour[outline_mask] - np.array(OUTLINE))
    assert np.all(diff <= 8), f"outline pixels must keep their own dark colour, not the red fill: max diff {diff.max()}"


def _capped_full_scene():
    """A 64x64 green-screen frame with a 24x24 dark square -- a 2px dark
    outline ring around a 20x20 silver interior -- masked only by the
    interior's innermost 14x14. A 3px margin of silver interior, plus the
    whole dark outline, are left outside the mask for the grow band to
    recover, and both fall inside `grow`'s reach."""
    size, outer, outline_w, margin = 64, 24, 2, 3
    outer_off = (size - outer) // 2                       # 20
    interior_off = outer_off + outline_w                  # 22
    interior = outer - 2 * outline_w                      # 20
    core_off = interior_off + margin                      # 25
    core = interior - 2 * margin                           # 14

    rgb = np.full((size, size, 3), GREEN_BACKGROUND, dtype=np.uint8)
    rgb[outer_off : outer_off + outer, outer_off : outer_off + outer] = OUTLINE
    rgb[interior_off : interior_off + interior, interior_off : interior_off + interior] = SILVER

    mask = np.zeros((size, size), dtype=np.uint8)
    mask[core_off : core_off + core, core_off : core_off + core] = 255

    outer_bool = np.zeros((size, size), dtype=bool)
    outer_bool[outer_off : outer_off + outer, outer_off : outer_off + outer] = True
    interior_bool = np.zeros((size, size), dtype=bool)
    interior_bool[interior_off : interior_off + interior, interior_off : interior_off + interior] = True
    core_bool = np.zeros((size, size), dtype=bool)
    core_bool[core_off : core_off + core, core_off : core_off + core] = True

    outline_mask = outer_bool & ~interior_bool
    silver_band_mask = interior_bool & ~core_bool

    return rgb, mask, outline_mask, silver_band_mask


def test_full_is_capped_at_twice_threshold_so_a_far_band_pixel_reaches_full_alpha():
    """`full` -- the band's fully-foreground reference distance -- must be
    capped at `2 * threshold`. Uncapped, `full` is whatever the mask's own
    outer ring happens to measure -- here the silver interior, itself
    ~313 from the green background -- and a same-band pixel of a different
    colour but still clearly foreground (the dark outline, ~237 from the
    background, well past the threshold of 60) normalises to under 1
    against that inflated `full` and comes out partially transparent
    instead of solid."""
    rgb, mask, outline_mask, silver_band_mask = _capped_full_scene()
    options = {"grow": 6, "threshold": 60, "background": "#00ff00"}
    out = np.array(Image.open(io.BytesIO(matting.apply(_png(rgb, "RGB"), _png(mask, "L"), options))))

    alpha = out[..., 3]

    assert np.all(alpha[silver_band_mask] == 255), "silver band pixels must be fully opaque"
    assert np.all(alpha[outline_mask] == 255), "the outline, clearly foreground, must be fully opaque too"


def _capped_blend_scene():
    """A 64x64 green-screen frame with a 24x24 dark outline square around a
    20x20 silver interior. The mask covers the whole square except its own
    outermost 1px ring -- its boundary sits on the outline, the darkest
    ring pixel, the way a real matte model's mask edge does, not deep
    inside the silver. That is what makes the grow band's reference
    distance the outline's (~237 from the green background), not the
    silver's (~313) -- the fixture matters here, because measuring from
    the silver would starve the ring pixel below the 50% confidence this
    test means to exercise. The outline's own outermost 1px -- the ring
    pixel touching the green background directly, left outside the mask --
    is painted as a 50/50 blend of the outline and the background colour,
    exactly what a matte model produces at a dark/chroma-key edge."""
    size, outer, outline_w = 64, 24, 2
    outer_off = (size - outer) // 2               # 20
    interior_off = outer_off + outline_w           # 22
    interior = outer - 2 * outline_w               # 20

    rgb = np.full((size, size, 3), GREEN_BACKGROUND, dtype=np.uint8)
    rgb[outer_off : outer_off + outer, outer_off : outer_off + outer] = OUTLINE
    rgb[interior_off : interior_off + interior, interior_off : interior_off + interior] = SILVER

    outer_bool = np.zeros((size, size), dtype=bool)
    outer_bool[outer_off : outer_off + outer, outer_off : outer_off + outer] = True
    shaved_bool = np.zeros((size, size), dtype=bool)
    shaved_bool[outer_off + 1 : outer_off + outer - 1, outer_off + 1 : outer_off + outer - 1] = True
    blend_mask = outer_bool & ~shaved_bool          # the outline's outermost 1px ring
    rgb[blend_mask] = (10, 138, 10)                  # 50/50 blend of OUTLINE and GREEN_BACKGROUND

    interior_bool = np.zeros((size, size), dtype=bool)
    interior_bool[interior_off : interior_off + interior, interior_off : interior_off + interior] = True

    mask = np.zeros((size, size), dtype=np.uint8)
    mask[shaved_bool] = 255   # everything except the outermost 1px ring -- mask boundary sits on the outline

    return rgb, mask, blend_mask, interior_bool


def test_a_5050_blend_band_pixel_is_unblended_to_the_outline_colour_not_left_green():
    """A band pixel's confidence is `clip(distance / min(full, 2 * threshold), 0, 1)`
    (uncapped before the clip), where `full` is the mask's own boundary
    ring's distance from the background. With the mask boundary sitting on
    the outline, `full` is the outline's own distance (~237, capped at
    `2*threshold=120`), and a pixel that is a 50/50 blend of the outline and
    the chroma-green background sits at ~118 -- right at the ring's 50%
    confidence threshold -- so it must be un-blended against the background
    (background's share removed), not left showing the greenish blend it was
    painted with, and not treated as too uncertain to trust. The silver
    interior, entirely inside the mask here, must come out silver, not
    green-tinted, confirming the background removal is confined to the band
    and does not bleed into pixels the mask already covers."""
    rgb, mask, blend_mask, silver_mask = _capped_blend_scene()
    options = {"grow": 6, "threshold": 60, "background": "#00ff00"}
    out = np.array(Image.open(io.BytesIO(matting.apply(_png(rgb, "RGB"), _png(mask, "L"), options))))

    alpha = out[..., 3]
    colour = out[..., :3].astype(int)

    assert np.all(alpha[blend_mask] >= 240), "a 50/50 foreground/background band pixel must be opaque to the eye"
    blend_colour = colour[blend_mask]
    assert np.all(blend_colour[:, 1] <= 60), (
        f"unblending must remove the background's green share, not leave it: max green {blend_colour[:, 1].max()}"
    )
    assert np.all(blend_colour[:, 0] <= 60) and np.all(blend_colour[:, 2] <= 60), (
        "unblended colour must read as the dark outline, not the lightened 50/50 blend"
    )

    assert np.all(alpha[silver_mask] == 255), "silver already inside the mask must stay fully opaque"
    silver_colour = colour[silver_mask]
    assert np.all(silver_colour >= 190), f"a silver pixel inside the mask must come out silver, not dimmed: min channel {silver_colour.min()}"
    assert np.all(np.abs(silver_colour[:, 1] - silver_colour[:, 0]) <= 20), (
        "silver must not read green-tinted -- its green channel must track its red channel"
    )
