"""Background removal -> transparent PNG.

Two methods:
  * birefnet  (default) - BiRefNet via rembg. MIT licensed, commercial use OK.
                          Best quality; works on any background.
  * chroma              - fast colour key. Use when the source has a flat
                          solid background (e.g. a green-screen video).

CLI:  python remove_bg.py in.png [more.png ...] -o out_dir [--method chroma --key 00ff00]
"""
from __future__ import annotations

import argparse
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image

DEFAULT_MODEL = "birefnet-general"  # "birefnet-general-lite" is faster, slightly rougher


@lru_cache(maxsize=2)
def _session(model: str):
    from rembg import new_session  # imported lazily so chroma mode needs no model
    return new_session(model)


def birefnet(img: Image.Image, model: str = DEFAULT_MODEL) -> Image.Image:
    from rembg import remove
    return remove(img.convert("RGB"), session=_session(model)).convert("RGBA")


def chroma(img: Image.Image, key: str = "00ff00", tolerance: int = 60, soft: int = 40) -> Image.Image:
    """Key out a solid colour. tolerance = hard cut distance, soft = feather band."""
    rgb = np.asarray(img.convert("RGB")).astype(np.int32)
    k = np.array([int(key[i:i + 2], 16) for i in (0, 2, 4)])
    dist = np.sqrt(((rgb - k) ** 2).sum(axis=-1))
    alpha = np.clip((dist - tolerance) / max(soft, 1), 0, 1)
    # despill: on soft edges, clamp the key's dominant channel to the other two
    out = rgb.copy()
    if k.max() - k.min() < 100:  # white/grey/black key: nothing to despill
        return Image.fromarray(np.dstack([out, alpha * 255]).clip(0, 255).astype(np.uint8), "RGBA")
    c = int(np.argmax(k))
    others = [i for i in range(3) if i != c]
    edge = alpha < 1
    cap = out[..., others].max(axis=-1)
    out[..., c] = np.where(edge, np.minimum(out[..., c], cap), out[..., c])
    rgba = np.dstack([out, alpha * 255]).clip(0, 255).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA")


def remove_background(img: Image.Image, method: str = "birefnet", **kw) -> Image.Image:
    if method == "chroma":
        return chroma(img, **{k: v for k, v in kw.items() if k in ("key", "tolerance", "soft")})
    return birefnet(img, model=kw.get("model", DEFAULT_MODEL))


def trim(img: Image.Image, pad: int = 4) -> Image.Image:
    """Crop to the visible pixels, plus padding."""
    box = img.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox()
    if not box:
        return img
    l, t, r, b = box
    return img.crop((max(l - pad, 0), max(t - pad, 0), min(r + pad, img.width), min(b + pad, img.height)))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("images", nargs="+", type=Path)
    ap.add_argument("-o", "--out", type=Path, default=Path("output/transparent"))
    ap.add_argument("--method", choices=["birefnet", "chroma"], default="birefnet")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--key", default="00ff00", help="hex colour for --method chroma")
    ap.add_argument("--no-trim", action="store_true")
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    for p in a.images:
        img = remove_background(Image.open(p), a.method, model=a.model, key=a.key)
        if not a.no_trim:
            img = trim(img)
        dest = a.out / (p.stem + ".png")
        img.save(dest)
        print(dest)


if __name__ == "__main__":
    main()
