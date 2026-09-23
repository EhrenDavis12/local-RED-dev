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
foreground pixel measures, and the colour is un-blended -- the background's
share, `(1 - alpha) * background`, is subtracted out. The body keeps the
model's mask at full alpha. Transparent pixels get black colour so nothing
downstream can bleed the background back in.

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


def _background(rgb: np.ndarray, spec: str) -> np.ndarray:
    if spec != "auto":
        return np.array([int(spec[i : i + 2], 16) for i in (1, 3, 5)], dtype=float)
    h, w = rgb.shape[:2]
    m = max(4, min(h, w) // 25)
    corners = np.concatenate(
        [rgb[:m, :m].reshape(-1, 3), rgb[:m, -m:].reshape(-1, 3),
         rgb[-m:, :m].reshape(-1, 3), rgb[-m:, -m:].reshape(-1, 3)]
    )
    return np.median(corners, axis=0)


def _binary_filter(mask: np.ndarray, size: int, op) -> np.ndarray:
    return np.array(Image.fromarray(mask.astype(np.uint8) * 255).filter(op(size))) > 0


def apply(frame_data: bytes, mask_data: bytes, options: dict) -> bytes:
    grow = int(options.get("grow", 3))
    threshold = float(options.get("threshold", 60))
    feather = float(options.get("feather", 0))

    rgb = np.array(_decode(frame_data).convert("RGB")).astype(float)
    mask = np.array(_decode(mask_data).convert("L"))
    if mask.shape != rgb.shape[:2]:
        mask = np.array(Image.fromarray(mask).resize((rgb.shape[1], rgb.shape[0]), Image.BILINEAR))

    core = mask >= 128
    alpha = core.astype(float)
    colour = rgb.copy()
    if grow > 0 and core.any():
        band = _binary_filter(core, 2 * grow + 1, ImageFilter.MaxFilter) & ~core
        background = _background(rgb, options.get("background", "auto"))
        distance = np.sqrt(((rgb - background) ** 2).sum(axis=-1))
        # What a fully-foreground pixel measures: the outermost ring of the
        # body, which for outlined art is the outline itself.
        ring = core & ~_binary_filter(core, 5, ImageFilter.MinFilter)
        full = float(np.median(distance[ring])) if ring.any() else float(np.median(distance[core]))
        full = max(full, threshold, 1.0)
        band_alpha = np.clip(distance / full, 0.0, 1.0)
        band_alpha[distance <= threshold * 0.5] = 0.0
        alpha = np.where(band, band_alpha, alpha)
        # Un-blend: the pixel was alpha * fg + (1 - alpha) * background.
        sel = band & (alpha > 0)
        a = alpha[sel][:, None]
        colour[sel] = np.clip((rgb[sel] - (1.0 - a) * background) / np.maximum(a, 1e-3), 0, 255)

    alpha_img = Image.fromarray((alpha * 255).round().astype(np.uint8))
    if feather > 0:
        alpha_img = alpha_img.filter(ImageFilter.GaussianBlur(feather))
    alpha8 = np.array(alpha_img)
    colour[alpha8 == 0] = 0
    out = Image.fromarray(np.dstack([colour, alpha8]).astype(np.uint8), "RGBA")
    buffer = io.BytesIO()
    out.save(buffer, format="PNG")
    return buffer.getvalue()
