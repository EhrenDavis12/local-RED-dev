"""
Local matting: combine a source frame with a mask frame into one RGBA frame,
restoring the outline a learned matte tends to eat.

A video matte model is good at the body of a character and bad at its dark
outline: a thick charcoal line against a flat background reads as shadow and
gets shaved by a pixel or two, differently on every frame, which plays back
as a flickering edge. When the background is a flat known colour the fix is
mechanical: grow the mask a few pixels, and in that band keep only the pixels
that are clearly not the background. The body keeps the model's mask; the
edge is decided by colour, which is the same on every frame.

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


def apply(frame_data: bytes, mask_data: bytes, options: dict) -> bytes:
    grow = int(options.get("grow", 3))
    threshold = float(options.get("threshold", 60))
    feather = float(options.get("feather", 0.7))

    rgb = np.array(_decode(frame_data).convert("RGB"))
    mask = np.array(_decode(mask_data).convert("L"))
    if mask.shape != rgb.shape[:2]:
        mask = np.array(Image.fromarray(mask).resize((rgb.shape[1], rgb.shape[0]), Image.BILINEAR))

    core = mask >= 128
    keep = core
    if grow > 0:
        grown = np.array(Image.fromarray(core.astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(2 * grow + 1))) > 0
        band = grown & ~core
        background = _background(rgb, options.get("background", "auto"))
        distance = np.sqrt(((rgb.astype(float) - background) ** 2).sum(axis=-1))
        keep = core | (band & (distance > threshold))

    alpha = Image.fromarray((keep * 255).astype(np.uint8))
    if feather > 0:
        alpha = alpha.filter(ImageFilter.GaussianBlur(feather))
    out = Image.fromarray(np.dstack([rgb, np.array(alpha)]).astype(np.uint8), "RGBA")
    buffer = io.BytesIO()
    out.save(buffer, format="PNG")
    return buffer.getvalue()
