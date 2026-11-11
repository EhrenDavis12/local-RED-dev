"""Turn an animation video into a Unity-ready transparent sprite sheet.

  python video_to_spritesheet.py walk.mp4 --fps 12 --cell 256
  python video_to_spritesheet.py attack.mp4 --start 0.5 --end 2.0 --method chroma --key 00ff00

Steps: ffmpeg extracts frames -> background removed per frame -> every frame is
cropped with the SAME box (the union of all visible pixels), so the character's
feet stay put and the animation doesn't jitter -> scaled into fixed-size cells,
anchored bottom-centre -> packed into a grid.

Outputs (in --out, default output/sprites/<video name>/):
  <name>_sheet.png   the sprite sheet (transparent)
  <name>.json        frame rects, fps, pivot - for import scripts
  frames/            individual transparent frames
Unity: Sprite Mode = Multiple, Sprite Editor > Slice > Grid By Cell Size = cell,
pivot = Bottom Center. Or let Claude Code write an editor script that reads the json.
"""
from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from PIL import Image

from remove_bg import DEFAULT_MODEL, remove_background

MAX_TEXTURE = 4096  # Unity's safe default max texture size; 8192 works on most desktop targets


def extract_frames(video: Path, fps: float, start: float | None, end: float | None, tmp: Path) -> list[Path]:
    cmd = ["ffmpeg", "-loglevel", "error", "-y"]
    if start is not None:
        cmd += ["-ss", str(start)]
    if end is not None:
        cmd += ["-to", str(end)]
    cmd += ["-i", str(video), "-vf", f"fps={fps}", str(tmp / "f_%05d.png")]
    subprocess.run(cmd, check=True)
    return sorted(tmp.glob("f_*.png"))


def union_bbox(frames: list[Image.Image], pad: int) -> tuple[int, int, int, int]:
    boxes = [f.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox() for f in frames]
    boxes = [b for b in boxes if b]
    if not boxes:
        raise SystemExit("No visible pixels after background removal - check --method / --key.")
    w, h = frames[0].size
    l = max(min(b[0] for b in boxes) - pad, 0)
    t = max(min(b[1] for b in boxes) - pad, 0)
    r = min(max(b[2] for b in boxes) + pad, w)
    b_ = min(max(b[3] for b in boxes) + pad, h)
    return l, t, r, b_


def fit_cell(img: Image.Image, cell_w: int, cell_h: int) -> Image.Image:
    scale = min(cell_w / img.width, cell_h / img.height)
    resized = img.resize((max(1, round(img.width * scale)), max(1, round(img.height * scale))), Image.LANCZOS)
    canvas = Image.new("RGBA", (cell_w, cell_h), (0, 0, 0, 0))
    canvas.paste(resized, ((cell_w - resized.width) // 2, cell_h - resized.height), resized)  # bottom-centre
    return canvas


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video", type=Path)
    ap.add_argument("--fps", type=float, default=12, help="sprite frame rate (8-12 typical)")
    ap.add_argument("--cell", default="256", help="cell size, e.g. 256 or 256x320")
    ap.add_argument("--start", type=float, help="seconds; trim to the loop you want")
    ap.add_argument("--end", type=float)
    ap.add_argument("--cols", type=int, help="columns (default: as square as possible)")
    ap.add_argument("--method", choices=["birefnet", "chroma", "none"], default="birefnet",
                    help="'none' if the video already has alpha")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--key", default="00ff00")
    ap.add_argument("--pad", type=int, default=6)
    ap.add_argument("--lock-x", action="store_true",
                    help="keep the character horizontally centred (for walk/run clips where it drifts across the frame)")
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()

    cw, ch = (int(x) for x in (a.cell.lower().split("x") * 2)[:2])
    name = a.video.stem
    out = a.out or Path("output/sprites") / name
    (out / "frames").mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    with tempfile.TemporaryDirectory() as td:
        paths = extract_frames(a.video, a.fps, a.start, a.end, Path(td))
        if not paths:
            raise SystemExit("ffmpeg produced no frames.")
        print(f"{len(paths)} frames extracted")
        frames = []
        for i, p in enumerate(paths, 1):
            img = Image.open(p).convert("RGBA")
            if a.method != "none":
                img = remove_background(img, a.method, model=a.model, key=a.key)
            frames.append(img)
            print(f"  background removed {i}/{len(paths)}", end="\r", flush=True)
        print()

    if a.lock_x:  # re-centre each frame horizontally, so a drifting character walks "in place"
        centred = []
        for f in frames:
            b = f.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
            shift = 0 if not b else f.width // 2 - (b[0] + b[2]) // 2
            g = Image.new("RGBA", f.size, (0, 0, 0, 0))
            g.paste(f, (shift, 0))
            centred.append(g)
        frames = centred
    box = union_bbox(frames, a.pad)
    cells = [fit_cell(f.crop(box), cw, ch) for f in frames]

    n = len(cells)
    cols = a.cols or math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)
    sheet = Image.new("RGBA", (cols * cw, rows * ch), (0, 0, 0, 0))
    rects = []
    for i, c in enumerate(cells):
        x, y = (i % cols) * cw, (i // cols) * ch
        sheet.paste(c, (x, y))
        c.save(out / "frames" / f"{name}_{i:03d}.png")
        rects.append({"name": f"{name}_{i:03d}", "x": x, "y": y, "w": cw, "h": ch})

    sheet_path = out / f"{name}_sheet.png"
    sheet.save(sheet_path, optimize=True)
    meta = {"name": name, "fps": a.fps, "frame_count": n, "cell": [cw, ch], "columns": cols, "rows": rows,
            "sheet_size": list(sheet.size), "pivot": [0.5, 0.0], "frames": rects,
            "origin_note": "x/y measured from top-left; Unity rects use bottom-left (y_unity = sheet_h - y - h)"}
    (out / f"{name}.json").write_text(json.dumps(meta, indent=2))

    print(f"Sheet: {sheet_path}  ({sheet.width}x{sheet.height}, {n} frames, {cols}x{rows})")
    if max(sheet.size) > MAX_TEXTURE:
        print(f"WARNING: sheet is larger than {MAX_TEXTURE}px. Use a smaller --cell, lower --fps, "
              f"or trim with --start/--end to just the loop.")
    print(f"Done in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    if not shutil.which("ffmpeg"):
        raise SystemExit("ffmpeg not found (brew install ffmpeg)")
    main()
