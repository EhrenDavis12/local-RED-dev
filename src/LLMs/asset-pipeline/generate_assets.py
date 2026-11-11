"""Generate game assets in batches through the local ComfyUI API.

  python generate_assets.py --check                         # is ComfyUI up? which models are installed?
  python generate_assets.py assets.json                     # generate every asset in the list
  python generate_assets.py --one "1girl, archer" --type character --name archer --count 2
  python generate_assets.py --workflow my_api.json --one "..." --name x   # any workflow exported from ComfyUI

Style (checkpoint, LoRA, prompt tags, sizes) comes from style.json so every asset matches.
Transparent types (character/building/prop) are background-removed with BiRefNet and trimmed.

Output: output/<type>/<name>_<n>.png  (+ output/raw/ originals)
Every image is logged to output/manifest.jsonl (prompt, seed, model, LoRA) so you can
reproduce it and show where each shipped asset came from.
Re-running skips images that already exist, so an interrupted batch just resumes.

Custom workflows: in ComfyUI use "Export (API)". In the JSON, put the text {{PROMPT}},
{{NEGATIVE}} or {{SEED}} where those values should go ({{SEED}} as a string; it becomes a number).
"""
from __future__ import annotations

import argparse
import io
import json
import random
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import requests
from PIL import Image

HERE = Path(__file__).parent
OUT = Path("output")


# ---------- ComfyUI API ----------
class Comfy:
    def __init__(self, url: str):
        self.url = url.rstrip("/")
        self.client_id = str(uuid.uuid4())

    def up(self) -> dict:
        return requests.get(f"{self.url}/system_stats", timeout=5).json()

    def options(self, node: str, field: str) -> list[str]:
        info = requests.get(f"{self.url}/object_info/{node}", timeout=10).json()
        return info[node]["input"]["required"][field][0]

    def run(self, workflow: dict, timeout: float = 3600) -> list[tuple[str, bytes]]:
        r = requests.post(f"{self.url}/prompt", json={"prompt": workflow, "client_id": self.client_id}, timeout=30)
        if r.status_code != 200:
            raise RuntimeError(f"ComfyUI rejected the workflow: {r.text[:2000]}")
        pid = r.json()["prompt_id"]
        start = time.time()
        while time.time() - start < timeout:
            h = requests.get(f"{self.url}/history/{pid}", timeout=30).json()
            if pid in h:
                entry = h[pid]
                status = entry.get("status", {})
                if status.get("status_str") == "error":
                    raise RuntimeError(f"ComfyUI error: {json.dumps(status.get('messages', []))[:2000]}")
                files = []
                for node_out in entry.get("outputs", {}).values():
                    for key in ("images", "gifs", "videos"):
                        for f in node_out.get(key, []):
                            if f.get("type") != "output":
                                continue
                            data = requests.get(f"{self.url}/view", params={
                                "filename": f["filename"], "subfolder": f.get("subfolder", ""), "type": "output"},
                                timeout=120).content
                            files.append((f["filename"], data))
                return files
            time.sleep(1.5)
        raise TimeoutError(f"Job {pid} did not finish within {timeout}s")


# ---------- workflows ----------
def sdxl_workflow(style: dict, prompt: str, negative: str, seed: int, w: int, h: int, prefix: str) -> dict:
    s = style["sampler"]
    wf = {
        "ckpt": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": style["checkpoint"]}},
    }
    model, clip = ["ckpt", 0], ["ckpt", 1]
    for i, lora in enumerate(l for l in style.get("loras", []) if l.get("enabled")):
        nid = f"lora{i}"
        wf[nid] = {"class_type": "LoraLoader", "inputs": {
            "model": model, "clip": clip, "lora_name": lora["file"],
            "strength_model": lora.get("strength", 1.0), "strength_clip": lora.get("strength", 1.0)}}
        model, clip = [nid, 0], [nid, 1]
    wf.update({
        "pos": {"class_type": "CLIPTextEncode", "inputs": {"clip": clip, "text": prompt}},
        "neg": {"class_type": "CLIPTextEncode", "inputs": {"clip": clip, "text": negative}},
        "latent": {"class_type": "EmptyLatentImage", "inputs": {"width": w, "height": h, "batch_size": 1}},
        "sample": {"class_type": "KSampler", "inputs": {
            "model": model, "positive": ["pos", 0], "negative": ["neg", 0], "latent_image": ["latent", 0],
            "seed": seed, "steps": s["steps"], "cfg": s["cfg"], "sampler_name": s["sampler_name"],
            "scheduler": s["scheduler"], "denoise": 1.0}},
        "decode": {"class_type": "VAEDecode", "inputs": {"samples": ["sample", 0], "vae": ["ckpt", 2]}},
        "save": {"class_type": "SaveImage", "inputs": {"images": ["decode", 0], "filename_prefix": prefix}},
    })
    return wf


def fill_template(template: dict, prompt: str, negative: str, seed: int) -> dict:
    def sub(v):
        if isinstance(v, dict):
            return {k: sub(x) for k, x in v.items()}
        if isinstance(v, list):
            return [sub(x) for x in v]
        if v == "{{SEED}}":
            return seed
        if isinstance(v, str):
            return v.replace("{{PROMPT}}", prompt).replace("{{NEGATIVE}}", negative)
        return v
    return sub(template)


# ---------- main ----------
def build_prompt(style: dict, atype: str, prompt: str) -> str:
    t = style["types"].get(atype, {})
    parts = [style["style_prompt"], prompt, t.get("prompt_suffix", ""), style["quality_prompt"]]
    return ", ".join(p for p in parts if p)


def log(entry: dict):
    OUT.mkdir(exist_ok=True)
    with open(OUT / "manifest.jsonl", "a") as f:
        f.write(json.dumps(entry) + "\n")


def generate(comfy: Comfy, style: dict, item: dict, template: dict | None, bg_method: str):
    name, atype = item["name"], item.get("type", "character")
    tcfg = style["types"].get(atype, {"width": 1024, "height": 1024, "transparent": False})
    transparent = item.get("transparent", tcfg.get("transparent", False))
    prompt = build_prompt(style, atype, item["prompt"])
    negative = style["negative_prompt"] + (", " + item["negative"] if item.get("negative") else "")
    base_seed = item.get("seed", random.randint(0, 2**31))
    (OUT / atype).mkdir(parents=True, exist_ok=True)
    (OUT / "raw").mkdir(parents=True, exist_ok=True)

    for n in range(item.get("count", 1)):
        dest = OUT / atype / f"{name}_{n + 1:02d}.png"
        if dest.exists():
            print(f"skip  {dest} (exists)")
            continue
        seed = base_seed + n
        t0 = time.time()
        if template:
            wf = fill_template(template, prompt, negative, seed)
        else:
            wf = sdxl_workflow(style, prompt, negative, seed, item.get("width", tcfg["width"]),
                               item.get("height", tcfg["height"]), f"pipeline/{name}")
        files = comfy.run(wf)
        if not files:
            raise RuntimeError("Workflow finished but produced no output files.")
        gen_s = time.time() - t0
        fname, data = files[0]
        if not fname.lower().endswith(".png"):  # video / gif outputs from custom workflows
            vdest = dest.with_suffix(Path(fname).suffix)
            vdest.write_bytes(data)
            print(f"saved {vdest}  ({gen_s:.0f}s)")
            dest = vdest
        else:
            raw = OUT / "raw" / dest.name
            raw.write_bytes(data)
            img = Image.open(io.BytesIO(data))
            if transparent:
                from remove_bg import remove_background, trim
                img = trim(remove_background(img, bg_method, key="ffffff"))  # chroma keys the white bg
            img.save(dest)
            print(f"saved {dest}  ({gen_s:.0f}s gen, {time.time() - t0 - gen_s:.0f}s post)")
        log({"file": str(dest), "name": name, "type": atype, "prompt": prompt, "negative": negative, "seed": seed,
             "checkpoint": style["checkpoint"], "loras": [l["file"] for l in style.get("loras", []) if l.get("enabled")],
             "workflow": "custom" if template else "sdxl_txt2img", "transparent": transparent,
             "seconds": round(time.time() - t0, 1), "created": datetime.now(timezone.utc).isoformat()})


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("assets", nargs="?", type=Path, help="JSON list of assets (see assets.example.json)")
    ap.add_argument("--style", type=Path, default=HERE / "style.json")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--one", help="prompt for a single asset")
    ap.add_argument("--type", default="character")
    ap.add_argument("--name", default="test")
    ap.add_argument("--count", type=int, default=1)
    ap.add_argument("--seed", type=int)
    ap.add_argument("--workflow", type=Path, help="API-format workflow JSON with {{PROMPT}}/{{SEED}} placeholders")
    ap.add_argument("--bg", choices=["birefnet", "chroma"], default="birefnet")
    a = ap.parse_args()

    style = json.loads(a.style.read_text())
    comfy = Comfy(style.get("comfy_url", "http://127.0.0.1:8188"))
    try:
        stats = comfy.up()
    except requests.RequestException:
        sys.exit("ComfyUI is not reachable at " + comfy.url + " - run ./start_comfyui.sh first.")

    if a.check:
        dev = stats.get("devices", [{}])[0]
        print("ComfyUI OK  -", dev.get("name", "?"), dev.get("type", ""))
        ckpts, loras = comfy.options("CheckpointLoaderSimple", "ckpt_name"), comfy.options("LoraLoader", "lora_name")
        print("checkpoints:", ckpts)
        print("loras:", loras)
        if style["checkpoint"] not in ckpts:
            print("WARNING: style.json checkpoint not installed:", style["checkpoint"])
        for l in style.get("loras", []):
            if l.get("enabled") and l["file"] not in loras:
                print("WARNING: enabled LoRA not installed:", l["file"])
        return

    template = json.loads(a.workflow.read_text()) if a.workflow else None
    if a.one:
        items = [{"name": a.name, "type": a.type, "prompt": a.one, "count": a.count,
                  **({"seed": a.seed} if a.seed is not None else {})}]
    elif a.assets:
        items = json.loads(a.assets.read_text())
    else:
        ap.error("give an assets file, --one, or --check")

    t0 = time.time()
    failures = []
    for item in items:
        try:
            generate(comfy, style, item, template, a.bg)
        except Exception as e:  # keep the batch going; report at the end
            print(f"FAILED {item.get('name')}: {e}")
            failures.append(item.get("name"))
    print(f"\nFinished in {(time.time() - t0) / 60:.1f} min. Failures: {failures or 'none'}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
