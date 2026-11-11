"""
Local matting: combine a source frame with a mask frame into one RGBA frame
whose edge carries none of the background.

A video matte model is good at the body of a character and bad at its dark
outline: a thick charcoal line against a flat background reads as shadow and
gets shaved by a pixel or two, differently on every frame, which plays back
as a flickering edge. And every edge pixel of the source is a blend of the
character and the background, so keeping it as-is paints a light fringe
around the outline once the background is gone.

When the background is a flat known colour both are mechanical. The mask is
grown a few pixels; in that band each pixel is keyed by its colour distance
from the background: alpha is that distance relative to what a fully
foreground pixel measures, capped (below) so a band pixel of a different
material than the mask's own edge still reaches solid. Colour, though,
needs a measure of how much of the pixel really is foreground that the cap
can't distort, so it is judged by a separate, uncapped confidence -- the
same distance against the reference before the cap. Below confidence 1.0
the pixel takes the nearest body pixel's colour, spread outward by
iterative nearest-neighbour dilation, and only where that fill actually
reaches it: a partial-coverage pixel's own colour still carries a share of
the background and, recovered by un-blending, amplifies that share into
noise as coverage drops, where the body's colour right next to it is
already the right colour for what is, at any partial coverage, an
antialiasing pixel -- and a dark outline painted that colour is invisible
against any background, chroma key or otherwise. Only at confidence 1.0 --
as far from the background as the outline ring itself, no longer a blend
at all -- does the pixel keep its own colour. The body keeps the model's
mask at full alpha. Transparent pixels get black colour so nothing
downstream can bleed the background back in.

The model's own body edge routinely lands a pixel or two outside the painted
outline, in the background blend, and at full alpha those pixels average
into a pale rim once the frame is downscaled. `matte.erode` shrinks the body
by that many pixels before the band is built, so the colour key and the
nearest-body fill decide that ring instead of the model's mask. The band
itself still grows from the un-eroded body, not the shrunk one, so a
feature narrower than the erosion -- a thin limb, a whisker -- stays
reachable instead of falling outside `grow` pixels of the shrunk body and
vanishing.

`erode` assumes every feature narrower than `2*erode+1` pixels carries the
outline colour, which is true of outlined art at the matte's working size.
A light, outline-less detail thinner than that is keyed by colour after
erosion like any other band pixel, and where the fill reaches it, it takes
the nearest body colour instead of its own.

`matte.effect` is for material the mask model tracks badly: effects are
colourful and sparse, and the model routinely loses whole small shards, so
a grown band a few pixels wide never reaches back far enough to recover
them. Outside the body the key is by colour alone, over the whole frame,
with a narrow ramp around the threshold rather than the band's measured
"fully foreground" distance -- there is no reliable body left to measure
that from. Inside the body only the exact background colour is dropped;
everything else, including a shard the model missed, keeps full alpha and
its original colour untouched.

`apply` is pure image work -- no model, no network.
"""
from __future__ import annotations

import io

import numpy as np
from PIL import Image, ImageFilter


def _decode(data: bytes) -> Image.Image:
    with Image.open(io.BytesIO(data)) as img:
        img.load()
        return img.copy()


def background_of(rgb: np.ndarray, spec: str) -> np.ndarray:
    """The background colour `apply` keys against: `spec` verbatim if it is
    a `#rrggbb` colour, otherwise `auto`, read from this frame's corners.
    For a clip, `auto` is read from the corners of the clip's first frame
    and held for the whole clip, because later frames may have foreground
    in the corners -- that holding is the caller's job (`execute.py`), not
    this function's; `background_of` only ever measures one frame."""
    if spec != "auto":
        return np.array([int(spec[i : i + 2], 16) for i in (1, 3, 5)], dtype=float)
    h, w = rgb.shape[:2]
    m = max(4, min(h, w) // 25)
    corners = np.concatenate(
        [rgb[:m, :m].reshape(-1, 3), rgb[:m, -m:].reshape(-1, 3),
         rgb[-m:, :m].reshape(-1, 3), rgb[-m:, -m:].reshape(-1, 3)]
    )
    return np.median(corners, axis=0)


def _step_binary(mask: np.ndarray, combine) -> np.ndarray:
    """One 3x3-neighbourhood step of `mask`, edge pixels replicated outward
    -- matching how PIL's `MaxFilter`/`MinFilter` treat the border -- and
    `combine` reducing each pixel with its 8 neighbours (`logical_or` for a
    dilation step, `logical_and` for an erosion step)."""
    padded = np.pad(mask, 1, mode="edge")
    result = mask.copy()
    for dy in (0, 1, 2):
        for dx in (0, 1, 2):
            combine(result, padded[dy : dy + mask.shape[0], dx : dx + mask.shape[1]], out=result)
    return result


def _dilate(mask: np.ndarray, steps: int) -> np.ndarray:
    """`mask` grown by `steps` pixels (Chebyshev distance). `steps`
    iterations of a 3x3 step give the same result as one pass of a
    `(2*steps+1)`-wide filter -- a single wide pass is quadratic in
    `steps` -- and plain numpy shifts (`_step_binary`) do each 3x3 step
    far cheaper than a PIL rank filter call over a full frame."""
    result = mask
    for _ in range(steps):
        result = _step_binary(result, np.logical_or)
    return result


def _erode(mask: np.ndarray, steps: int) -> np.ndarray:
    """`mask` shrunk by `steps` pixels (Chebyshev distance); see `_dilate`."""
    result = mask
    for _ in range(steps):
        result = _step_binary(result, np.logical_and)
    return result


def _neighbour_sum(arr: np.ndarray) -> np.ndarray:
    """Sum of `arr` over each pixel's 3x3 neighbourhood (itself included),
    zero-padded at the edges. `arr` is 2D or 2D-plus-channels, and the
    result keeps `arr`'s own dtype -- callers on the hot path pass float32
    to halve the cost of `apply`'s per-frame fill loop."""
    padded = np.pad(arr, [(1, 1), (1, 1)] + [(0, 0)] * (arr.ndim - 2))
    total = np.zeros_like(arr)
    for dy in (0, 1, 2):
        for dx in (0, 1, 2):
            total += padded[dy : dy + arr.shape[0], dx : dx + arr.shape[1]]
    return total


def apply(frame_data: bytes, mask_data: bytes, options: dict) -> bytes:
    grow = int(options.get("grow", 3))
    erode = int(options.get("erode", 0))
    threshold = float(options.get("threshold", 60))
    feather = float(options.get("feather", 0))
    effect = bool(options.get("effect", False))
    despill = bool(options.get("despill", False))
    despill_slack = float(options.get("despill_slack", 4))
    drop_backdrop_inside = bool(options.get("drop_backdrop_inside", False))
    drop_excess = float(options.get("drop_excess", 90))

    rgb = np.array(_decode(frame_data).convert("RGB")).astype(float)
    mask = np.array(_decode(mask_data).convert("L"))
    if mask.shape != rgb.shape[:2]:
        mask = np.array(Image.fromarray(mask).resize((rgb.shape[1], rgb.shape[0]), Image.BILINEAR))

    core = mask >= 128
    alpha = core.astype(float)
    colour = rgb.copy()
    if effect:
        # No band, no grow: the model loses whole shards, so the key runs
        # over the whole frame by colour alone.
        background = background_of(rgb, options.get("background", "auto"))
        distance = np.sqrt(((rgb - background) ** 2).sum(axis=-1))
        outside = ~core

        half = max(threshold * 0.5, 1e-6)
        ramp = np.clip((distance - half) / half, 0.0, 1.0)
        alpha = np.where(outside, ramp, alpha)
        # Inside the body, only the exact background colour drops out.
        alpha = np.where(core & (distance <= threshold * 0.25), 0.0, alpha)

        # Un-blend: the pixel was alpha * fg + (1 - alpha) * background.
        # Only partially-keyed pixels outside the body need it -- alpha 1
        # is untouched colour, and the body never un-blends.
        sel = outside & (alpha > 0) & (alpha < 1)
        a = alpha[sel][:, None]
        colour[sel] = np.clip((rgb[sel] - (1.0 - a) * background) / np.maximum(a, 1e-3), 0, 255)
    elif grow > 0 and core.any():
        eroded_core = _erode(core, erode) if erode > 0 else core
        if not eroded_core.any():
            # Erosion swallowed the whole body -- key against the
            # un-eroded core instead of measuring `full` or filling colour
            # from nothing.
            eroded_core = core
        alpha = eroded_core.astype(float)
        # Grown from the *original* core, not the eroded one: a feature
        # narrower than the erosion (a thin limb, a whisker) can sit more
        # than `grow` pixels from the eroded body, and growing from the
        # eroded body would leave it outside the band -- and so at alpha 0
        # -- entirely.
        band = _dilate(core, grow) & ~eroded_core
        background = background_of(rgb, options.get("background", "auto"))
        distance = np.sqrt(((rgb - background) ** 2).sum(axis=-1))
        # What a fully-foreground pixel measures: the outermost ring of the
        # (possibly eroded) body, which for outlined art is the outline
        # itself.
        ring = eroded_core & ~_erode(eroded_core, 2)
        full_ring = float(np.median(distance[ring])) if ring.any() else float(np.median(distance[eroded_core]))
        full_ring = max(full_ring, threshold, 1.0)
        # Capped at twice the threshold: on a chroma-green background the
        # outline itself can sit ~430 from the background while a silver
        # body sits ~300, so scaling by the outline's `full_ring` left a
        # silver pixel the mask missed at alpha ~0.7 and a thin blade read
        # as translucent. A pixel at least twice the threshold from the
        # background is unmistakably foreground and must be solid;
        # antialiasing still comes from the downscale, not this ramp.
        full = min(full_ring, 2 * threshold)
        band_alpha = np.clip(distance / full, 0.0, 1.0)
        band_alpha[distance <= threshold * 0.5] = 0.0
        alpha = np.where(band, band_alpha, alpha)
        # How much of this pixel is really foreground, independent of the
        # cap above -- against `full_ring`, not `full`, so a pixel the cap
        # pushed to solid can still read as a partial blend here.
        confidence = np.clip(distance / full_ring, 0.0, 1.0)

        if band.any():
            # Below confidence 1.0, colour comes from the nearest body
            # pixel, spread outward by `grow + erode` steps of
            # nearest-neighbour dilation -- the extra `erode` steps because
            # the fill starts from the eroded body, but (per the band
            # above) now has to reach `grow` pixels past the un-eroded
            # core -- rather than this pixel's own colour; see the module
            # docstring. Restricted to the band's bounding box, padded by
            # one pixel, and to float32: the frame-size cost of this loop
            # is otherwise paid over pixels the band never touches.
            rows = np.where(band.any(axis=1))[0]
            cols = np.where(band.any(axis=0))[0]
            crop = np.s_[
                max(int(rows[0]) - 1, 0) : min(int(rows[-1]) + 2, band.shape[0]),
                max(int(cols[0]) - 1, 0) : min(int(cols[-1]) + 2, band.shape[1]),
            ]

            sub_core = eroded_core[crop]
            colour_fill = colour[crop].astype(np.float32) * sub_core[..., None]
            filled = sub_core.copy()
            for _ in range(grow + erode):
                neighbour_count = _neighbour_sum(filled.astype(np.float32))
                neighbour_colour = _neighbour_sum(colour_fill)
                newly_filled = (~filled) & (neighbour_count > 0)
                colour_fill[newly_filled] = (
                    neighbour_colour[newly_filled] / neighbour_count[newly_filled, None]
                )
                filled |= newly_filled

            # Only a band pixel the fill actually reached takes the fill
            # colour -- a band pixel `filled` never reached has no nearest
            # body colour to take -- `colour_fill` there is still zero --
            # and must keep its own colour too, or it comes out black. A
            # pixel at confidence 1.0 -- as far from the background as the
            # outline ring itself -- was never a blend to begin with and
            # keeps its own colour regardless of what the fill reached.
            sub_alpha = alpha[crop]
            sub_confidence = confidence[crop]
            sel = band[crop] & (sub_alpha > 0) & (sub_confidence < 1.0) & filled
            colour[crop][sel] = colour_fill[sel]

    if not effect and (despill or drop_backdrop_inside):
        if grow <= 0 or not core.any():
            # Only recompute if the band branch above didn't already run --
            # it measures the same background when it does.
            background = background_of(rgb, options.get("background", "auto"))
        # The backdrop's "chroma channels" are whichever sit within 60 of its
        # own largest channel -- one, for a single-colour backdrop like
        # chroma green; two, for magenta, cyan, or yellow, where the colour
        # splits across a pair of channels -- and the rest are its "off
        # channels". A neutral or lightly tinted backdrop (grey, white,
        # black) has every channel within 60 of the largest, so it has no
        # off channel at all, and must stay inert rather than have an empty
        # max default to 0 and read as a spurious, huge dominance.
        chroma_mask = background >= background.max() - 60
        off_mask = ~chroma_mask
        dominance = (
            background[chroma_mask].min() - background[off_mask].max()
            if off_mask.any() else -np.inf
        )
        # Both cleanups require the measured backdrop itself to be a
        # strongly saturated colour: unless its chroma channels clear its
        # off channels by at least 100, clamping or dropping against it
        # would misfire on ordinary colour rather than spill.
        if dominance >= 100:
            # Both key off the pixel's *final* colour (`colour`, not the
            # raw decoded `rgb`): a band pixel the nearest-body fill above
            # has already recovered to its true colour must be judged on
            # that recovered colour, not reclamped against the raw
            # background blend it replaced. A pixel's excess is the
            # smallest of its chroma channels minus the largest of its off
            # channels -- for a single-channel backdrop this is
            # byte-identical to the old dominant-minus-max-of-the-others
            # reading.
            excess = colour[..., chroma_mask].min(axis=-1) - colour[..., off_mask].max(axis=-1)

            if drop_backdrop_inside:
                # Scoped to `eroded_core` only -- never the band, and never
                # the ring between `core` and `eroded_core` even though
                # that ring is still `mask >= 128` -- both already trust
                # the colour key's own graded alpha.
                eroded_core = _erode(core, erode) if erode > 0 else core
                if erode > 0 and not eroded_core.any():
                    eroded_core = core
                distance = np.sqrt(((colour - background) ** 2).sum(axis=-1))
                drop = eroded_core & (excess > drop_excess) & (distance <= threshold)
                alpha = np.where(drop, 0.0, alpha)

            if despill:
                # Every chroma channel is pulled down by the same amount --
                # (excess - despill_slack) -- in lockstep, not independently
                # clamped to a per-channel ceiling: that is what keeps a
                # two-channel spill (a purple or teal fringe) from having
                # only one of its two tinted channels corrected.
                spill = (alpha > 0) & (excess > despill_slack)
                reduction = np.where(spill, excess - despill_slack, 0.0)
                colour[..., chroma_mask] = np.maximum(
                    colour[..., chroma_mask] - reduction[..., None], 0.0
                )

    alpha_img = Image.fromarray((alpha * 255).round().astype(np.uint8))
    if feather > 0:
        alpha_img = alpha_img.filter(ImageFilter.GaussianBlur(feather))
    alpha8 = np.array(alpha_img)
    colour[alpha8 == 0] = 0
    out = Image.fromarray(np.dstack([colour, alpha8]).astype(np.uint8), "RGBA")
    buffer = io.BytesIO()
    out.save(buffer, format="PNG")
    return buffer.getvalue()
