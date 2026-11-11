"""
`matting.apply`'s two opt-in backdrop-colour cleanups, both scoped to the
non-effect path (the normal character-matte grow/band branch, not
`matte.effect`):

`despill` removes backdrop tint that survives on an otherwise-opaque pixel.
For every output pixel with alpha > 0 whose excess (defined below) strictly
exceeds `despill_slack` (default 4), each of the backdrop's *chroma*
channels is reduced by (excess - despill_slack), pulling them down in
lockstep until the pixel's own excess again equals the slack, clamped at 0.
For a single-channel backdrop (chroma green) this has exactly one chroma
channel, so it reduces to the old reading: that channel clamped to at most
the max of the other two plus `despill_slack`. Critically, both the excess
that decides whether to clamp and the values clamped from are read from the
pixel's *final* colour -- after the grow band's own nearest-body colour
fill has already replaced a partial-coverage edge pixel's raw blend with
its true, un-blended colour -- never from the raw decoded frame. A band
pixel the fill has already cleaned up must be left alone; reclamping it
against the raw blend's own (much smaller) channel values is what produces
a magenta or orange cast on an edge that was already correct. A pixel not
tinted toward the backdrop already sits at or below the ceiling, so the
clamp is a no-op for it -- the formula itself is what makes the option
selective, not a separate "is this pixel tinted" check. This exists because
a mask model's body alpha can be full and correct while the pixel's own
colour still carries a sliver of the green screen (a fast-moving blade
catching backdrop-coloured motion blur), or, against a magenta or cyan
backdrop, a sliver split across two channels -- a purple or teal fringe
rather than a single-channel tint.

`drop_backdrop_inside` removes backdrop colour the mask model has no
business claiming as foreground at all: inside `eroded_core` only (the
mask body after `erode` has shrunk it -- never the band, and never the
ring between `core` and `eroded_core` either, even though that ring is
still `mask >= 128`), a pixel is forced to alpha 0 when it actually looks
like the backdrop: its excess (defined below) exceeds `drop_excess`
(default 90) *and* its colour distance to the measured background is at
most `threshold` (the same option the colour key itself uses, default 60).
A pixel far from the backdrop in Euclidean terms is never dropped no matter
how large its excess -- a saturated but distant colour is not backdrop,
whatever channel happens to dominate it. This exists for enclosed gaps a
matte model fills in by treating them as body -- between an arm and the
torso, in a sword-arm gap -- where the pixel is, in truth, still backdrop.

Both options additionally require the measured background itself to be a
strongly saturated colour, and both read the same two channel sets off it.
The background's "chroma channels" are whichever of its three channels sit
within 60 of its own largest channel -- one, for a single-colour backdrop
like chroma green; two, for a magenta, cyan, or yellow backdrop, where the
colour is split across a pair of channels -- and the rest are its "off
channels". Unless the smallest chroma channel exceeds the largest off
channel by at least 100, both options do nothing at all and the output is
byte-identical to leaving them off. A neutral or lightly tinted backdrop --
grey, white, black -- has no off channel at all once every channel sits
within 60 of the largest, and stays inert exactly as before, never misfiring
on ordinary colour because no channel can be read as dominant. A pixel's own
"excess", read above wherever a single dominant channel used to be read
alone, is the smallest of its chroma channels minus the largest of its off
channels; for a single-channel backdrop this is byte-identical to the old
dominant-minus-max-of-the-others reading.

Both default to off, so a manifest that never opts in gets byte-for-byte
today's output, and both are independent of each other: enabling one must
not gate or replace the other. Both apply regardless of `grow` (including
`grow: 0`, which skips the band branch entirely) and are silently ignored
on the `effect` path, which has its own, separate backdrop handling. Both
run before `feather`: `drop_backdrop_inside` punches alpha to 0 first, and
only then does feather blur that edge like any other. A pixel either
option drops to alpha 0 is still forced to black colour by `apply`'s
existing transparent-pixel handling. `despill_slack` and `drop_excess`
both use "exceeds" strictly: a pixel whose excess exactly equals either is
left alone.
"""
from __future__ import annotations

import io

import numpy as np
from PIL import Image

from agf import matting

# The real backdrop this option pair was built for: chroma green, measured
# off actual footage at ~(24, 221, 11) rather than pure (0, 255, 0).
GREEN_BACKDROP = (24, 221, 11)
GREEN_BACKDROP_HEX = "#18dd0b"

BLUE_BACKDROP_HEX = "#0000ff"

# A backdrop whose channels sit within 2 of each other -- nowhere near the
# 100-excess dominance the options require -- so it must leave both inert.
GREY_BACKDROP_HEX = "#c8c8c6"   # (200, 200, 198)

SPILL_GREEN = (120, 200, 120)     # green-tinted opaque pixel: excess 80
BLUE_ARMOUR = (40, 80, 200)
SKIN = (240, 190, 150)
RED_PLUME = (210, 50, 25)

STEEL_GREY = (140, 140, 140)      # R == G == B: zero excess against any backdrop
CHARCOAL = (20, 20, 20)

SILVER_EDGE = (190, 190, 200)

# A two-channel chroma backdrop -- magenta -- measured off real footage
# closer to (249, 0, 251) than to pure (255, 0, 255), the same way
# GREEN_BACKDROP above is measured rather than pure.
MAGENTA_BACKDROP = (249, 0, 251)
MAGENTA_BACKDROP_HEX = "#f900fb"

PURPLE_FRINGE = (180, 60, 190)   # magenta-spill-tinted opaque pixel: excess 120
BROWN = (120, 70, 40)
GREEN_LEAF = (60, 160, 60)

NEAR_MAGENTA_GAP = (240, 10, 245)   # excess 230, distance ~15 from MAGENTA_BACKDROP
FAR_PURPLE = (150, 60, 160)         # excess exactly 90, distance ~147 -- far from the backdrop


def _png(arr: np.ndarray, mode: str) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(arr, mode).save(buf, format="PNG")
    return buf.getvalue()


def _apply(rgb: np.ndarray, mask: np.ndarray, options: dict) -> np.ndarray:
    out = matting.apply(_png(rgb, "RGB"), _png(mask, "L"), options)
    return np.array(Image.open(io.BytesIO(out)))


def _despill_scene():
    """An 8x8 canvas, entirely covered by the mask (a uniform opaque body),
    split into four 4x4 quadrants: a green-spill-tinted pixel, a blue
    armour pixel, a skin pixel, and a red plume pixel -- one real defect
    and three colours that must never move."""
    size = 8
    rgb = np.zeros((size, size, 3), dtype=np.uint8)
    rgb[0:4, 0:4] = SPILL_GREEN
    rgb[0:4, 4:8] = BLUE_ARMOUR
    rgb[4:8, 0:4] = SKIN
    rgb[4:8, 4:8] = RED_PLUME

    mask = np.full((size, size), 255, dtype=np.uint8)

    def region(r0, r1, c0, c1):
        m = np.zeros((size, size), dtype=bool)
        m[r0:r1, c0:c1] = True
        return m

    regions = {
        "spill": region(0, 4, 0, 4),
        "blue": region(0, 4, 4, 8),
        "skin": region(4, 8, 0, 4),
        "red": region(4, 8, 4, 8),
    }
    return rgb, mask, regions


def test_despill_clamps_green_tinted_pixel_and_leaves_untinted_colours_exact():
    """despill: a green-tinted opaque pixel ((120, 200, 120), excess 80 over
    the default despill_slack of 4) must have its green channel clamped to
    at most max(R, B) + 4 == 124, while blue armour, skin, and a red plume
    -- none of them tinted toward the green backdrop -- must come out
    byte-exact, because the clamp is only ever a ceiling on the dominant
    channel and a no-op below it."""
    rgb, mask, regions = _despill_scene()
    options = {"grow": 3, "background": GREEN_BACKDROP_HEX, "despill": True}
    out = _apply(rgb, mask, options)

    alpha = out[..., 3]
    colour = out[..., :3].astype(int)

    assert np.all(alpha[regions["spill"]] == 255), "despill must not touch alpha"
    spill = colour[regions["spill"]]
    assert np.all(spill[:, 1] == 124), f"green channel must clamp to exactly max(R,B)+4=124: got {np.unique(spill[:, 1])}"
    assert np.all(spill[:, 0] == 120) and np.all(spill[:, 2] == 120), "despill must only touch the dominant (green) channel"

    for name, expected in (("blue", BLUE_ARMOUR), ("skin", SKIN), ("red", RED_PLUME)):
        got = colour[regions[name]]
        assert np.all(got == np.array(expected)), f"{name} pixel must be unchanged by despill: got {got[0]}"


def test_despill_is_off_by_default():
    """despill: with the option absent, a green-tinted pixel must survive
    untouched -- the option is opt-in, and today's callers must see
    byte-identical output."""
    rgb, mask, regions = _despill_scene()
    options = {"grow": 3, "background": GREEN_BACKDROP_HEX}
    out = _apply(rgb, mask, options)

    colour = out[..., :3].astype(int)
    spill = colour[regions["spill"]]
    assert np.all(spill == np.array(SPILL_GREEN)), "despill must not run unless explicitly enabled"


def test_despill_slack_is_honoured():
    """despill: `despill_slack` sets how much green excess over max(R, B)
    survives. A pixel with excess 40 -- (100, 140, 100) -- sits above the
    default slack of 4 (clamped) but below a widened slack of 50 (left
    alone), so the same pixel must come out differently under each."""
    size = 6
    rgb = np.full((size, size, 3), (100, 140, 100), dtype=np.uint8)
    mask = np.full((size, size), 255, dtype=np.uint8)
    base = {"grow": 3, "background": GREEN_BACKDROP_HEX, "despill": True}

    default_out = _apply(rgb, mask, base)
    widened_out = _apply(rgb, mask, {**base, "despill_slack": 50})

    assert np.all(default_out[..., 1] == 104), "default despill_slack=4 must clamp a 40-excess pixel to exactly max(R,B)+4=104, not merely reduce it"
    assert np.all(widened_out[..., 1] == 140), "a despill_slack of 50 must leave a 40-excess pixel's green channel untouched"


def test_despill_generalises_to_the_backdrops_own_dominant_channel():
    """despill: against a blue backdrop, the channel clamped must be blue
    -- the one the backdrop actually dominates -- not a hardcoded green.
    A blue-tinted pixel must be clamped; a green-tinted pixel, irrelevant
    against a blue backdrop, must be left exactly as it is."""
    size = 8
    rgb = np.zeros((size, size, 3), dtype=np.uint8)
    blue_tinted = (100, 100, 200)   # excess 100 over max(R,G)=100
    rgb[0:4, 0:4] = blue_tinted
    rgb[4:8, 4:8] = SPILL_GREEN

    mask = np.full((size, size), 255, dtype=np.uint8)
    blue_region = np.zeros((size, size), dtype=bool)
    blue_region[0:4, 0:4] = True
    green_region = np.zeros((size, size), dtype=bool)
    green_region[4:8, 4:8] = True

    options = {"grow": 3, "background": BLUE_BACKDROP_HEX, "despill": True}
    out = _apply(rgb, mask, options)
    colour = out[..., :3].astype(int)

    blue = colour[blue_region]
    assert np.all(blue[:, 2] == 104), f"blue backdrop must clamp the blue channel to exactly max(R,G)+4=104: got {np.unique(blue[:, 2])}"
    assert np.all(blue[:, 0] == 100) and np.all(blue[:, 1] == 100)

    green = colour[green_region]
    assert np.all(green == np.array(SPILL_GREEN)), "a green-tinted pixel must be untouched when the backdrop's dominant channel is blue"


def _blend_edge_scene(body_colour):
    """A 64x64 green-screen frame with a 24x24 square of `body_colour` --
    no dark outline, an outline-less edge -- masked everywhere except its
    own outermost 1px ring, where the mask boundary sits directly on the
    true edge the way an outline-less matte model's boundary does. That
    ring is painted the raw 50/50 blend of `body_colour` and the green
    backdrop -- a spill-tinted edge -- which the grow band's own
    nearest-body colour fill must recover to `body_colour` before despill
    ever looks at it."""
    size, sq = 64, 24
    off = (size - sq) // 2

    rgb = np.full((size, size, 3), GREEN_BACKDROP, dtype=np.uint8)
    rgb[off : off + sq, off : off + sq] = body_colour

    outer_bool = np.zeros((size, size), dtype=bool)
    outer_bool[off : off + sq, off : off + sq] = True
    shaved_bool = np.zeros((size, size), dtype=bool)
    shaved_bool[off + 1 : off + sq - 1, off + 1 : off + sq - 1] = True
    blend_ring = outer_bool & ~shaved_bool

    blend_colour = tuple(int(round((b + g) / 2)) for b, g in zip(body_colour, GREEN_BACKDROP))
    rgb[blend_ring] = blend_colour

    mask = np.zeros((size, size), dtype=np.uint8)
    mask[shaved_bool] = 255

    return rgb, mask, blend_ring


def test_despill_keys_off_the_filled_colour_not_the_raw_blend_for_a_silver_edge():
    """despill must compute both the excess and the clamp ceiling from the
    pixel's final colour -- after the grow band's nearest-body fill -- not
    the raw decoded frame. A silver outline-less edge, contaminated by a
    raw green-backdrop blend at its true boundary, is recovered to pure
    silver by the fill; despill, reading that final colour (green channel
    190, already below max(R,B)+4 = 204), must leave it exactly
    (190, 190, 200) -- not reclamp it into a magenta cast using the raw
    blend's much smaller red and blue."""
    rgb, mask, blend_ring = _blend_edge_scene(SILVER_EDGE)
    options = {"grow": 12, "erode": 3, "threshold": 60, "background": GREEN_BACKDROP_HEX, "despill": True}
    out = _apply(rgb, mask, options)

    colour = out[..., :3].astype(int)
    assert np.all(colour[blend_ring] == np.array(SILVER_EDGE)), (
        f"a fill-recovered silver edge must stay exactly (190,190,200), got {colour[blend_ring][0]}"
    )


def test_despill_keys_off_the_filled_colour_not_the_raw_blend_for_a_red_edge():
    """The same guarantee for a red edge: the fill-recovered colour must
    come out exactly (210, 50, 25) -- green already far below max(R,B)+4 --
    not shifted toward orange by a clamp ceiling (or a clamp target)
    computed from the raw blend instead of the final colour."""
    rgb, mask, blend_ring = _blend_edge_scene(RED_PLUME)
    options = {"grow": 12, "erode": 3, "threshold": 60, "background": GREEN_BACKDROP_HEX, "despill": True}
    out = _apply(rgb, mask, options)

    colour = out[..., :3].astype(int)
    assert np.all(colour[blend_ring] == np.array(RED_PLUME)), (
        f"a fill-recovered red edge must stay exactly (210,50,25), got {colour[blend_ring][0]}"
    )


def test_despill_and_drop_backdrop_inside_are_gated_by_backdrop_dominance():
    """Both options require the measured background's dominant channel to
    exceed the max of the other two by at least 100 -- a strongly
    saturated backdrop, not an incidental colour cast. A neutral grey
    backdrop, whose channels are all within 2 of each other, must leave
    both options inert: the output must be byte-identical with both
    enabled and both off, a skin pixel must stay exactly (240, 190, 150),
    and a red plume must stay fully opaque."""
    rgb, mask, regions = _despill_scene()
    without = _apply(rgb, mask, {"grow": 3, "background": GREY_BACKDROP_HEX})
    with_both = _apply(rgb, mask, {
        "grow": 3,
        "background": GREY_BACKDROP_HEX,
        "despill": True,
        "drop_backdrop_inside": True,
    })

    assert np.array_equal(without, with_both), "both options must be gated off entirely when the backdrop is not dominant enough"
    colour = with_both[..., :3].astype(int)
    assert np.all(colour[regions["skin"]] == np.array(SKIN)), "a skin pixel must be untouched when the backdrop guard blocks despill"
    assert np.all(with_both[..., 3][regions["red"]] == 255), "a red plume must stay opaque when the backdrop guard blocks drop_backdrop_inside"


def _enclosed_gap_scene(gap_colour):
    """A 10x10 canvas: the mask body covers the centre 6x6, filled with a
    mid-grey steel colour, except for a 2x2 patch fully enclosed inside it
    -- the sword-arm gap a matte model fills in as body -- painted
    `gap_colour`. Outside the body the canvas is plain backdrop and
    unmasked, matching a real matte frame."""
    size = 10
    rgb = np.full((size, size, 3), GREEN_BACKDROP, dtype=np.uint8)
    rgb[2:8, 2:8] = STEEL_GREY
    rgb[4:6, 4:6] = gap_colour

    mask = np.zeros((size, size), dtype=np.uint8)
    mask[2:8, 2:8] = 255

    gap = np.zeros((size, size), dtype=bool)
    gap[4:6, 4:6] = True
    steel = np.zeros((size, size), dtype=bool)
    steel[2:8, 2:8] = True
    steel[4:6, 4:6] = False

    return rgb, mask, gap, steel


def test_drop_backdrop_inside_drops_an_enclosed_backdrop_patch_to_transparent():
    """drop_backdrop_inside: a pure-backdrop-coloured patch fully enclosed
    inside the mask body (excess 197 over the default drop_excess of 90,
    distance 0 well under the default threshold of 60) must be forced to
    alpha 0 and, by the existing transparent-pixel handling, black --
    while the surrounding steel body (zero excess) stays fully opaque at
    its own true colour."""
    rgb, mask, gap, steel = _enclosed_gap_scene(GREEN_BACKDROP)
    options = {"grow": 3, "background": GREEN_BACKDROP_HEX, "drop_backdrop_inside": True}
    out = _apply(rgb, mask, options)

    alpha = out[..., 3]
    colour = out[..., :3].astype(int)

    assert np.all(alpha[gap] == 0), "an enclosed pure-backdrop patch inside the mask body must be dropped to transparent"
    assert np.all(colour[gap] == 0), "a dropped pixel must be forced to black by the existing transparent-pixel handling"
    assert np.all(alpha[steel] == 255), "the surrounding steel body must stay opaque"
    assert np.all(colour[steel] == np.array(STEEL_GREY)), "the steel body's own colour must be untouched"


def test_drop_backdrop_inside_is_off_by_default():
    """drop_backdrop_inside: with the option absent, the enclosed backdrop
    patch must stay fully opaque -- exactly today's behaviour, where the
    mask alone decides the body regardless of colour."""
    rgb, mask, gap, _steel = _enclosed_gap_scene(GREEN_BACKDROP)
    options = {"grow": 3, "background": GREEN_BACKDROP_HEX}
    out = _apply(rgb, mask, options)

    assert np.all(out[..., 3][gap] == 255), "drop_backdrop_inside must not run unless explicitly enabled"


def test_drop_excess_threshold_is_honoured():
    """drop_backdrop_inside: `drop_excess` sets how much backdrop-channel
    excess, on a pixel already close enough to the backdrop to satisfy the
    distance half of the test, survives inside the eroded body. A patch of
    (30, 180, 20) -- excess 150, distance ~42 from the backdrop, well under
    the default threshold of 60 -- is dropped under the default drop_excess
    of 90, but kept opaque once drop_excess is raised past 150."""
    rgb, mask, gap, _steel = _enclosed_gap_scene((30, 180, 20))
    base = {"grow": 3, "background": GREEN_BACKDROP_HEX, "drop_backdrop_inside": True}

    default_out = _apply(rgb, mask, base)
    lenient_out = _apply(rgb, mask, {**base, "drop_excess": 160})

    assert np.all(default_out[..., 3][gap] == 0), "default drop_excess=90 must drop a 150-excess, near-backdrop patch"
    assert np.all(lenient_out[..., 3][gap] == 255), "a drop_excess of 160 must leave a 150-excess patch opaque"


def test_despill_and_drop_backdrop_inside_apply_independently_when_both_enabled():
    """Enabling both options together must not gate one on the other: a
    green-tinted body pixel must still be despilled, and an enclosed
    backdrop patch must still be dropped, in the same call."""
    size = 10
    rgb = np.full((size, size, 3), GREEN_BACKDROP, dtype=np.uint8)
    rgb[2:8, 2:8] = STEEL_GREY
    rgb[2:4, 2:4] = SPILL_GREEN
    rgb[4:6, 4:6] = GREEN_BACKDROP

    mask = np.zeros((size, size), dtype=np.uint8)
    mask[2:8, 2:8] = 255

    spill = np.zeros((size, size), dtype=bool)
    spill[2:4, 2:4] = True
    gap = np.zeros((size, size), dtype=bool)
    gap[4:6, 4:6] = True
    steel = np.zeros((size, size), dtype=bool)
    steel[2:8, 2:8] = True
    steel[2:4, 2:4] = False
    steel[4:6, 4:6] = False

    options = {
        "grow": 3,
        "background": GREEN_BACKDROP_HEX,
        "despill": True,
        "drop_backdrop_inside": True,
    }
    out = _apply(rgb, mask, options)
    alpha = out[..., 3]
    colour = out[..., :3].astype(int)

    assert np.all(alpha[gap] == 0), "drop_backdrop_inside must still fire when despill is also enabled"
    spill_pixels = colour[spill]
    assert np.all(spill_pixels[:, 1] == 124), "despill must still fire when drop_backdrop_inside is also enabled, clamping to exactly max(R,B)+4=124"
    assert np.all(alpha[steel] == 255)
    assert np.all(colour[steel] == np.array(STEEL_GREY))


def _exterior_band_scene():
    """A 30x30 canvas: a 10x10 steel body (mask-covered) and, 2px outside
    its edge -- inside `grow`'s reach but never in the mask -- a small
    patch coloured to be strongly green (high backdrop-channel excess) yet
    close enough to the backdrop, in Euclidean distance, that the colour
    key's own band alpha comes out genuinely graded rather than 0 or 255."""
    size = 30
    rgb = np.full((size, size, 3), GREEN_BACKDROP, dtype=np.uint8)
    rgb[10:20, 10:20] = STEEL_GREY
    band_pixel_colour = (5, 180, 5)   # excess 175; distance from GREEN_BACKDROP ~45.6
    rgb[8:10, 14:16] = band_pixel_colour

    mask = np.zeros((size, size), dtype=np.uint8)
    mask[10:20, 10:20] = 255

    band_patch = np.zeros((size, size), dtype=bool)
    band_patch[8:10, 14:16] = True

    return rgb, mask, band_patch


def test_drop_backdrop_inside_leaves_a_graded_band_pixel_untouched():
    """drop_backdrop_inside's scope is `eroded_core` only, never the
    antialiasing band: a band pixel with a genuinely graded alpha (strictly
    between 0 and 255) and a backdrop-channel excess well past `drop_excess`
    must come out with that same alpha, unchanged, because the band already
    trusts the colour key and this option never touches it."""
    rgb, mask, band_patch = _exterior_band_scene()
    base = {"grow": 3, "threshold": 60, "background": GREEN_BACKDROP_HEX}
    baseline = _apply(rgb, mask, base)
    with_drop = _apply(rgb, mask, {**base, "drop_backdrop_inside": True})

    baseline_alpha = baseline[..., 3][band_patch]
    assert np.all((baseline_alpha > 0) & (baseline_alpha < 255)), (
        f"fixture must produce a genuinely graded band pixel to exercise this: got {np.unique(baseline_alpha)}"
    )
    assert np.array_equal(with_drop[..., 3][band_patch], baseline_alpha), (
        "drop_backdrop_inside must never touch a band pixel's alpha -- its scope is eroded_core, not the band"
    )


def _charcoal_ring_scene():
    """A 64x64 canvas: a 24x24 charcoal square masked as the body, with a
    small charcoal-to-green blend patch sitting in the outer 3px ring of
    that square -- the mask edge landing 2px into the true edge's blend,
    the way a matte model's slight over-claim does. The patch is still
    part of `core` (`mask >= 128`) but is excluded from `eroded_core` once
    `erode: 3` shrinks the body, and its colour is deliberately chosen to
    satisfy drop_backdrop_inside's excess-and-distance test -- so the only
    thing that can save it from being dropped is being outside the
    option's scope."""
    size, off, sq = 64, 20, 24
    rgb = np.full((size, size, 3), GREEN_BACKDROP, dtype=np.uint8)
    rgb[off : off + sq, off : off + sq] = CHARCOAL
    ring_colour = (60, 180, 10)   # excess 120; distance from GREEN_BACKDROP ~54.6
    rgb[off : off + 3, off + 8 : off + 10] = ring_colour

    mask = np.zeros((size, size), dtype=np.uint8)
    mask[off : off + sq, off : off + sq] = 255

    ring_patch = np.zeros((size, size), dtype=bool)
    ring_patch[off : off + 3, off + 8 : off + 10] = True

    return rgb, mask, ring_patch


def test_drop_backdrop_inside_never_touches_the_erosion_ring_even_when_the_pixel_looks_like_backdrop():
    """drop_backdrop_inside's scope is `eroded_core` only: a charcoal-to-
    green blend patch in the ring between `core` and `eroded_core` --
    still `mask >= 128`, but excluded by `erode: 3` -- must keep its
    normal graded, colour-keyed alpha even though its excess (120) and
    distance (~55) would satisfy the drop test if it were in scope. Being
    outside `eroded_core` is what saves it, not its colour."""
    rgb, mask, ring_patch = _charcoal_ring_scene()
    base = {"grow": 6, "erode": 3, "threshold": 60, "background": GREEN_BACKDROP_HEX}
    baseline = _apply(rgb, mask, base)
    with_drop = _apply(rgb, mask, {**base, "drop_backdrop_inside": True})

    baseline_alpha = baseline[..., 3][ring_patch]
    assert np.all((baseline_alpha > 0) & (baseline_alpha < 255)), (
        f"fixture must produce a genuinely graded ring pixel to exercise this: got {np.unique(baseline_alpha)}"
    )
    assert np.array_equal(with_drop[..., 3][ring_patch], baseline_alpha), (
        "a pixel in the ring between core and eroded_core must never be touched by drop_backdrop_inside, "
        "even when it would otherwise satisfy the excess-and-distance test"
    )


DARK_GREEN = (0, 100, 0)      # excess 100, distance ~124 -- far from the backdrop
EMERALD = (30, 160, 60)       # excess 100, distance ~78 -- far from the backdrop
NEAR_BACKDROP = (30, 215, 20)  # excess 185, distance ~12 -- genuinely backdrop-like


def _body_interior_excess_scene():
    """A 12x12 canvas, entirely covered by the mask (`core == eroded_core`,
    no erode, no band), split into three 4x4 quadrants: two saturated
    greens that are nonetheless far from the measured backdrop in colour
    distance, and one pixel that is both high-excess and genuinely close
    to the backdrop."""
    size = 12
    rgb = np.full((size, size, 3), STEEL_GREY, dtype=np.uint8)
    rgb[0:4, 0:4] = DARK_GREEN
    rgb[0:4, 4:8] = EMERALD
    rgb[0:4, 8:12] = NEAR_BACKDROP

    mask = np.full((size, size), 255, dtype=np.uint8)

    def region(c0, c1):
        m = np.zeros((size, size), dtype=bool)
        m[0:4, c0:c1] = True
        return m

    regions = {"dark_green": region(0, 4), "emerald": region(4, 8), "near_backdrop": region(8, 12)}
    return rgb, mask, regions


def test_drop_backdrop_inside_requires_both_high_excess_and_closeness_to_backdrop():
    """drop_backdrop_inside only drops a pixel that is both high-excess
    (backdrop-channel excess > drop_excess) AND close to the backdrop in
    colour distance (<= threshold). Dark green and emerald both clear the
    excess bar but sit far from the measured backdrop and must stay
    opaque; a near-backdrop green clears both and must be dropped."""
    rgb, mask, regions = _body_interior_excess_scene()
    options = {"grow": 3, "background": GREEN_BACKDROP_HEX, "drop_backdrop_inside": True, "threshold": 60}
    out = _apply(rgb, mask, options)
    alpha = out[..., 3]

    assert np.all(alpha[regions["dark_green"]] == 255), "a high-excess pixel far from the backdrop (dark green) must stay opaque"
    assert np.all(alpha[regions["emerald"]] == 255), "a high-excess pixel far from the backdrop (emerald) must stay opaque"
    assert np.all(alpha[regions["near_backdrop"]] == 0), "a pixel with high excess AND close to the backdrop must be dropped"


def test_despill_applies_when_grow_is_zero():
    """despill must still run when `grow: 0` skips the band branch
    entirely -- it is not conditioned on that branch having executed."""
    rgb, mask, regions = _despill_scene()
    options = {"despill": True, "background": GREEN_BACKDROP_HEX, "grow": 0}
    out = _apply(rgb, mask, options)
    colour = out[..., :3].astype(int)

    spill = colour[regions["spill"]]
    assert np.all(spill[:, 1] == 124), "despill must clamp the green channel even with grow=0"
    assert np.all(spill[:, 0] == 120) and np.all(spill[:, 2] == 120)
    for name, expected in (("blue", BLUE_ARMOUR), ("skin", SKIN), ("red", RED_PLUME)):
        assert np.all(colour[regions[name]] == np.array(expected))


def test_drop_backdrop_inside_applies_when_grow_is_zero():
    """drop_backdrop_inside must still run when `grow: 0` skips the band
    branch entirely -- it is not conditioned on that branch having
    executed."""
    rgb, mask, gap, steel = _enclosed_gap_scene(GREEN_BACKDROP)
    options = {"drop_backdrop_inside": True, "background": GREEN_BACKDROP_HEX, "grow": 0}
    out = _apply(rgb, mask, options)

    assert np.all(out[..., 3][gap] == 0), "drop_backdrop_inside must drop the enclosed patch even with grow=0"
    assert np.all(out[..., 3][steel] == 255)


def test_despill_runs_before_feather_and_still_clamps_colour():
    """despill must still clamp colour when `feather` is also requested --
    feather only blurs the alpha channel, and despill's own effect must not
    be skipped or altered by its presence."""
    rgb, mask, regions = _despill_scene()
    options = {"grow": 3, "background": GREEN_BACKDROP_HEX, "despill": True, "feather": 2.0}
    out = _apply(rgb, mask, options)
    colour = out[..., :3].astype(int)

    spill = colour[regions["spill"]]
    assert np.all(spill[:, 1] == 124), "despill must still clamp the green channel to 124 when feather is requested"


def _feather_drop_scene():
    """A 24x24 canvas: a 20x20 steel body and a 14x14 pure-backdrop patch
    well inside it, so its innermost 2x2 centre sits a full 6px from the
    patch's own edge -- comfortably beyond a feather radius of 1.0, so any
    post-drop blur cannot reach it."""
    size = 24
    rgb = np.full((size, size, 3), GREEN_BACKDROP, dtype=np.uint8)
    rgb[2:22, 2:22] = STEEL_GREY
    rgb[4:18, 4:18] = GREEN_BACKDROP

    mask = np.zeros((size, size), dtype=np.uint8)
    mask[2:22, 2:22] = 255

    gap_centre = np.zeros((size, size), dtype=bool)
    gap_centre[10:12, 10:12] = True

    return rgb, mask, gap_centre


def test_drop_backdrop_inside_centre_stays_zero_after_feather():
    """drop_backdrop_inside must punch alpha to 0 before `feather` blurs
    it, not after: the centre of a dropped patch, 6px from its own edge --
    far beyond a feather radius of 1.0 -- must stay exactly transparent."""
    rgb, mask, gap_centre = _feather_drop_scene()
    options = {"grow": 3, "background": GREEN_BACKDROP_HEX, "drop_backdrop_inside": True, "feather": 1.0}
    out = _apply(rgb, mask, options)

    assert np.all(out[..., 3][gap_centre] == 0), (
        "drop_backdrop_inside must zero alpha before feathering runs -- the patch centre must stay exactly transparent"
    )


def test_despill_and_drop_backdrop_inside_are_ignored_when_effect_is_true():
    """Both options are ignored entirely on the `effect` path, which has
    its own separate backdrop handling: enabling them must produce
    byte-identical output to leaving them off."""
    rgb, mask, _regions = _despill_scene()
    base_options = {"effect": True, "background": GREEN_BACKDROP_HEX, "threshold": 60}
    without = _apply(rgb, mask, base_options)
    with_both = _apply(rgb, mask, {
        **base_options,
        "despill": True,
        "despill_slack": 4,
        "drop_backdrop_inside": True,
        "drop_excess": 90,
    })

    assert np.array_equal(without, with_both), "despill and drop_backdrop_inside must be ignored entirely on the effect path"


def test_despill_boundary_excess_equal_to_slack_stays_unchanged():
    """despill's "exceeds" is strict: a pixel whose excess exactly equals
    `despill_slack` (4) -- (100, 104, 100) -- must be left unchanged, not
    clamped any further."""
    size = 4
    rgb = np.full((size, size, 3), (100, 104, 100), dtype=np.uint8)
    mask = np.full((size, size), 255, dtype=np.uint8)
    options = {"despill": True, "background": GREEN_BACKDROP_HEX, "grow": 3}
    out = _apply(rgb, mask, options)

    assert np.all(out[..., 1] == 104), "excess exactly equal to despill_slack must not be clamped further"


def test_drop_backdrop_inside_boundary_excess_equal_to_drop_excess_stays_opaque():
    """drop_backdrop_inside's "exceeds" is strict: a patch of (24, 114, 11)
    -- excess exactly 90, distance ~107 from the backdrop, kept within a
    generously raised threshold of 150 so the distance half of the test is
    not what is under test -- must stay fully opaque, not dropped."""
    rgb, mask, gap, _steel = _enclosed_gap_scene((24, 114, 11))
    options = {"grow": 3, "background": GREEN_BACKDROP_HEX, "drop_backdrop_inside": True, "threshold": 150}
    out = _apply(rgb, mask, options)

    assert np.all(out[..., 3][gap] == 255), "excess exactly equal to drop_excess must not be dropped"


def _magenta_despill_scene():
    """An 8x8 canvas, entirely covered by the mask, split into four 4x4
    quadrants against a two-channel magenta backdrop: a purple-fringe
    pixel tinted toward magenta across *both* its chroma channels (R and
    B), a brown pixel, a green leaf, and skin -- one real defect and three
    colours that must never move. Brown and the leaf each have their own
    argmax channel near one of magenta's chroma channels (R for brown, G
    for the leaf), which is exactly the case a per-pixel (rather than
    per-backdrop) reading of 'chroma channels' would misclassify and
    wrongly despill."""
    size = 8
    rgb = np.zeros((size, size, 3), dtype=np.uint8)
    rgb[0:4, 0:4] = PURPLE_FRINGE
    rgb[0:4, 4:8] = BROWN
    rgb[4:8, 0:4] = GREEN_LEAF
    rgb[4:8, 4:8] = SKIN

    mask = np.full((size, size), 255, dtype=np.uint8)

    def region(r0, r1, c0, c1):
        m = np.zeros((size, size), dtype=bool)
        m[r0:r1, c0:c1] = True
        return m

    regions = {
        "fringe": region(0, 4, 0, 4),
        "brown": region(0, 4, 4, 8),
        "leaf": region(4, 8, 0, 4),
        "skin": region(4, 8, 4, 8),
    }
    return rgb, mask, regions


def test_despill_generalises_to_a_two_channel_magenta_backdrop():
    """despill must generalise beyond a single dominant channel: against a
    magenta backdrop (~(249, 0, 251)), R and B are both chroma channels (R
    sits within 60 of magenta's own largest channel, B) and G is the sole
    off channel, so a purple fringe pixel (180, 60, 190) -- excess
    min(R,B) - G == 120 -- must have *both* R and B reduced by
    (120 - despill_slack=4) == 116, landing at exactly (64, 60, 74). A
    single-channel formula would only ever touch one of R or B and leave a
    visible residual tint on the other. Brown, a green leaf, and skin --
    none of them tinted toward magenta once the excess is read against
    magenta's own chroma/off split -- must come out byte-exact."""
    rgb, mask, regions = _magenta_despill_scene()
    options = {"grow": 3, "background": MAGENTA_BACKDROP_HEX, "despill": True}
    out = _apply(rgb, mask, options)

    alpha = out[..., 3]
    colour = out[..., :3].astype(int)

    assert np.all(alpha[regions["fringe"]] == 255), "despill must not touch alpha"
    fringe = colour[regions["fringe"]]
    assert np.all(fringe[:, 0] == 64) and np.all(fringe[:, 2] == 74), (
        f"both chroma channels (R, B) must be reduced to exactly (64, 74): got R={np.unique(fringe[:, 0])}, B={np.unique(fringe[:, 2])}"
    )
    assert np.all(fringe[:, 1] == 60), "the off channel (G) must be untouched"

    for name, expected in (("brown", BROWN), ("leaf", GREEN_LEAF), ("skin", SKIN)):
        got = colour[regions[name]]
        assert np.all(got == np.array(expected)), f"{name} pixel must be unchanged by despill against a magenta backdrop: got {got[0]}"


def _magenta_two_gap_scene():
    """A 10x14 canvas: a steel body enclosing two 2x2 gaps against a
    two-channel magenta backdrop -- a near-magenta gap (high excess, close
    to the backdrop) and a far purple gap whose excess sits exactly at the
    default drop_excess boundary of 90 *and* whose colour distance from
    the backdrop (~147) is far past the default threshold of 60, so it
    must stay opaque regardless of which half of the test a buggy
    implementation gets wrong."""
    rows, cols = 10, 14
    rgb = np.full((rows, cols, 3), MAGENTA_BACKDROP, dtype=np.uint8)
    rgb[2:8, 2:12] = STEEL_GREY
    rgb[4:6, 4:6] = NEAR_MAGENTA_GAP
    rgb[4:6, 8:10] = FAR_PURPLE

    mask = np.zeros((rows, cols), dtype=np.uint8)
    mask[2:8, 2:12] = 255

    near_gap = np.zeros((rows, cols), dtype=bool)
    near_gap[4:6, 4:6] = True
    far_gap = np.zeros((rows, cols), dtype=bool)
    far_gap[4:6, 8:10] = True
    steel = np.zeros((rows, cols), dtype=bool)
    steel[2:8, 2:12] = True
    steel[4:6, 4:6] = False
    steel[4:6, 8:10] = False

    return rgb, mask, near_gap, far_gap, steel


def test_drop_backdrop_inside_generalises_to_a_two_channel_magenta_backdrop():
    """drop_backdrop_inside must use the same generalised excess as
    despill: against a magenta backdrop, a near-magenta gap (240, 10, 245)
    -- excess min(R,B) - G == 230, past the default drop_excess of 90, and
    colour distance ~15 from the measured backdrop, well under the default
    threshold of 60 -- enclosed in the eroded body must be dropped to
    transparent and black. A far purple gap (150, 60, 160) -- excess
    exactly 90, not strictly exceeding drop_excess, and ~147 from the
    backdrop -- must stay fully opaque at its own true colour."""
    rgb, mask, near_gap, far_gap, steel = _magenta_two_gap_scene()
    options = {"grow": 3, "background": MAGENTA_BACKDROP_HEX, "drop_backdrop_inside": True}
    out = _apply(rgb, mask, options)

    alpha = out[..., 3]
    colour = out[..., :3].astype(int)

    assert np.all(alpha[near_gap] == 0), "a near-magenta enclosed gap must be dropped under a magenta backdrop"
    assert np.all(colour[near_gap] == 0), "a dropped pixel must be forced to black"
    assert np.all(alpha[far_gap] == 255), "a far purple gap must stay opaque"
    assert np.all(colour[far_gap] == np.array(FAR_PURPLE)), "a kept pixel's own colour must be untouched"
    assert np.all(alpha[steel] == 255), "the surrounding steel body must stay opaque"
    assert np.all(colour[steel] == np.array(STEEL_GREY)), "the steel body's own colour must be untouched"


def test_despill_and_drop_backdrop_inside_stay_inert_when_backdrop_channels_are_all_near_equal():
    """The dominance gate must not misfire when a backdrop's three channels
    are *all* within 60 of each other -- grey (200, 200, 198) -- leaving no
    off channel to read a 'max' from at all. A wrong implementation that
    defaults an empty off-channel set's max to 0 would compute a spurious
    dominance of ~198 (>= 100) and wrongly engage both options; the gate
    must instead stay closed, leaving a strongly magenta-tinted pixel and
    an enclosed near-magenta-coloured gap exactly as they came in, even
    though both would be acted on under a magenta backdrop."""
    rgb, mask, regions = _magenta_despill_scene()
    gap_rgb, gap_mask, near_gap, _far_gap, steel = _magenta_two_gap_scene()

    despill_out = _apply(rgb, mask, {"grow": 3, "background": GREY_BACKDROP_HEX, "despill": True})
    fringe = despill_out[..., :3].astype(int)[regions["fringe"]]
    assert np.all(fringe == np.array(PURPLE_FRINGE)), (
        f"despill must stay inert against an all-near-equal grey backdrop: got {fringe[0]}"
    )

    # threshold raised well past the near-magenta gap's colour distance from
    # grey (~200) so the distance half of drop_backdrop_inside's test can
    # never be what keeps this pixel opaque -- only the dominance gate can.
    drop_out = _apply(gap_rgb, gap_mask, {
        "grow": 3, "background": GREY_BACKDROP_HEX, "drop_backdrop_inside": True, "threshold": 250,
    })
    assert np.all(drop_out[..., 3][near_gap] == 255), (
        "drop_backdrop_inside must stay inert against an all-near-equal grey backdrop, "
        "even for a pixel that would be dropped under a magenta backdrop and even with "
        "threshold raised so distance alone cannot explain it staying opaque"
    )
    assert np.all(drop_out[..., 3][steel] == 255), "the steel body must stay opaque regardless"


def _uniform_scene(colour, size=4):
    """A small canvas filled with a single colour, entirely covered by the
    mask -- the minimal fixture for a pointwise despill check."""
    rgb = np.full((size, size, 3), colour, dtype=np.uint8)
    mask = np.full((size, size), 255, dtype=np.uint8)
    return rgb, mask


def test_despill_pulls_a_two_channel_pixel_down_in_lockstep_without_going_negative():
    """despill reduces *both* chroma channels by the same amount
    (excess - despill_slack), never per-channel: against a magenta
    backdrop, (255, 0, 60) has chroma min 60, off (G) 0, so excess 60; at
    the default despill_slack of 4 both R and B drop by 56, landing at
    exactly (199, 0, 4) -- not independently clamped to some per-channel
    floor, which would have left R untouched at 255. A more extreme pixel,
    (250, 0, 100) -- excess 100, reduction 96 -- must land at exactly
    (154, 0, 4) by the same rule.

    Neither example drives a channel below 0, and none ever can with a
    positive despill_slack: because excess == min(chroma) - max(off) and
    max(off) >= 0, excess is always at most min(chroma), so the reduced
    value of the smallest chroma channel is always max(off) + despill_slack
    -- never negative. The floor is only reachable at all, at exactly 0, in
    the degenerate case where both the off channel and despill_slack are
    0, confirmed below with despill_slack explicitly set to 0."""
    rgb, mask = _uniform_scene((255, 0, 60))
    out = _apply(rgb, mask, {"background": MAGENTA_BACKDROP_HEX, "despill": True, "grow": 3})
    colour = out[..., :3].astype(int)
    assert np.all(colour[..., 0] == 199) and np.all(colour[..., 1] == 0) and np.all(colour[..., 2] == 4), (
        f"(255,0,60) at the default slack must land at exactly (199,0,4): got {colour[0,0]}"
    )

    rgb2, mask2 = _uniform_scene((250, 0, 100))
    out2 = _apply(rgb2, mask2, {"background": MAGENTA_BACKDROP_HEX, "despill": True, "grow": 3})
    colour2 = out2[..., :3].astype(int)
    assert np.all(colour2[..., 0] == 154) and np.all(colour2[..., 1] == 0) and np.all(colour2[..., 2] == 4), (
        f"(250,0,100) at the default slack must land at exactly (154,0,4): got {colour2[0,0]}"
    )

    # The genuine zero floor: despill_slack=0 and an off channel of 0 make
    # excess - slack equal min(chroma) exactly, so the smallest chroma
    # channel must land at precisely 0 -- never negative -- and the other
    # chroma channel must land at precisely its own excess over the min.
    rgb3, mask3 = _uniform_scene((255, 0, 60))
    out3 = _apply(rgb3, mask3, {"background": MAGENTA_BACKDROP_HEX, "despill": True, "despill_slack": 0, "grow": 3})
    colour3 = out3[..., :3].astype(int)
    assert np.all(colour3[..., 0] == 195) and np.all(colour3[..., 1] == 0) and np.all(colour3[..., 2] == 0), (
        f"with despill_slack=0, (255,0,60) must land at exactly (195,0,0), hitting the floor without underflowing: got {colour3[0,0]}"
    )


CYAN_BACKDROP_HEX = "#00ffff"
CYAN_FRINGE = (40, 180, 200)   # excess 140 against cyan's chroma pair (G, B)


def test_despill_generalises_to_a_two_channel_cyan_backdrop():
    """despill's chroma/off split must come from the measured background,
    not a hardcoded R/B pair: against a cyan backdrop (0, 255, 255), G and
    B are the chroma channels and R is the sole off channel, so
    (40, 180, 200) -- excess min(G,B) - R == 140 -- must have *both* G and
    B reduced by (140 - despill_slack=4) == 136, landing at exactly
    (40, 44, 64). A red pixel, far from cyan's chroma pair, must be left
    byte-exact."""
    size = 8
    rgb = np.zeros((size, size, 3), dtype=np.uint8)
    rgb[0:4, 0:4] = CYAN_FRINGE
    rgb[0:4, 4:8] = RED_PLUME
    mask = np.full((size, size), 255, dtype=np.uint8)

    fringe_region = np.zeros((size, size), dtype=bool)
    fringe_region[0:4, 0:4] = True
    red_region = np.zeros((size, size), dtype=bool)
    red_region[0:4, 4:8] = True

    options = {"grow": 3, "background": CYAN_BACKDROP_HEX, "despill": True}
    out = _apply(rgb, mask, options)
    colour = out[..., :3].astype(int)

    fringe = colour[fringe_region]
    assert np.all(fringe[:, 0] == 40) and np.all(fringe[:, 1] == 44) and np.all(fringe[:, 2] == 64), (
        f"a cyan fringe pixel must land at exactly (40,44,64): got {fringe[0]}"
    )
    red = colour[red_region]
    assert np.all(red == np.array(RED_PLUME)), f"a red pixel must be unchanged against a cyan backdrop: got {red[0]}"


BOUNDARY_CHROMA_HEX = "#ffc300"   # (255, 195, 0): G sits exactly 60 below the max -- chroma
BOUNDARY_OFF_HEX = "#ffc200"      # (255, 194, 0): G sits 61 below the max -- off


def test_despill_chroma_grouping_boundary_at_exactly_60_is_inclusive():
    """A backdrop channel exactly 60 below the max is grouped as chroma,
    not off: against (255, 195, 0), R and G are both chroma (G is exactly
    60 from R) and B is the sole off channel, giving background dominance
    min(255,195) - 0 == 195 (>= 100, engaged). A pixel of (200, 160, 20) --
    chroma excess min(R,G) - B == 140 -- must have *both* R and G reduced
    by (140 - despill_slack=4) == 136, to exactly (64, 24, 20). Grouping G
    as off instead would both misread the excess (giving (164, 160, 20))
    and, on the background itself, drop dominance to 255 - 195 == 60,
    wrongly gating the option off entirely."""
    rgb, mask = _uniform_scene((200, 160, 20))
    out = _apply(rgb, mask, {"background": BOUNDARY_CHROMA_HEX, "despill": True, "grow": 3})
    colour = out[..., :3].astype(int)
    assert np.all(colour[..., 0] == 64) and np.all(colour[..., 1] == 24) and np.all(colour[..., 2] == 20), (
        f"with G grouped as chroma, (200,160,20) must land at exactly (64,24,20): got {colour[0,0]}"
    )


def test_despill_chroma_grouping_boundary_at_61_is_excluded_and_gates_inert():
    """A backdrop channel 61 below the max is grouped as off, not chroma:
    against (255, 194, 0), only R is chroma and G and B are off, giving
    background dominance 255 - max(194, 0) == 61 (< 100), so despill must
    be gated off entirely -- the same (200, 160, 20) pixel that gets
    despilled one hex step away, at exactly 60, must come out byte-exact
    here."""
    rgb, mask = _uniform_scene((200, 160, 20))
    out = _apply(rgb, mask, {"background": BOUNDARY_OFF_HEX, "despill": True, "grow": 3})
    colour = out[..., :3].astype(int)
    assert np.all(colour[..., 0] == 200) and np.all(colour[..., 1] == 160) and np.all(colour[..., 2] == 20), (
        f"with dominance at 61 (< 100), (200,160,20) must be left unchanged: got {colour[0,0]}"
    )
