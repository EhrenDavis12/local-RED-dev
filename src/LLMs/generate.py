"""Run the local models. Standard library only - any python3 works, no venv.

  python3 generate.py image "a red apple on a table" -o apple.png
  python3 generate.py video "the apple rolls off the table" --image apple.png -o roll.mp4
  python3 generate.py video "an apple rolling off a table" -o roll.mp4        # no --image: text-to-video
  python3 generate.py matte knight.png -o knight_cutout.png                   # image -> transparent PNG
  python3 generate.py matte roll.mp4 -o roll_mask.mp4                         # video -> white-on-black mask video
  python3 generate.py interpolate roll.mp4 -o roll_smooth.mp4                 # 2x the frames, 2x the fps
  python3 generate.py upscale knight.png -o knight_4x.png                     # image or short video, 4x
  python3 generate.py edit knight.png "same knight, head turned to the left" -o knight_turn.png
  python3 generate.py keyframes "the knight turns his head" --start a.png --end b.png -o a_to_b.mp4
  python3 generate.py i2v "the knight falls" --image a.png -o fall.mp4 --width 832 --height 640 --frames 33

The server must be up first: ./llms start

This runs the models and nothing else. Style, prompts, keying and sprite sheets belong to the
project that calls it. From Python: `from generate import image, video, matte, interpolate, upscale, edit, keyframes, i2v`.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

URL = os.environ.get("LLMS_URL", "http://127.0.0.1:8188")

IMAGE_CHECKPOINT = "animagine-xl-4.0-opt.safetensors"
VIDEO_MODEL = "wan2.2_ti2v_5B_fp16.safetensors"
VIDEO_TEXT_ENCODER = "umt5_xxl_fp8_e4m3fn_scaled.safetensors"
VIDEO_VAE = "wan2.2_vae.safetensors"
# The distilled 4-step LoRA and the small decoder are what make video usable on a Mac: without
# them a one-second clip takes 20 minutes, almost all of it in the full decoder.
VIDEO_FAST_LORA = "Wan2_2_5B_FastWanFullAttn_lora_rank_128_bf16.safetensors"
VIDEO_FAST_DECODER = "lighttaew2_2.safetensors"
MATTE_MODEL = "birefnet.safetensors"
INTERPOLATION_MODEL = "film_net_fp16.safetensors"
UPSCALE_MODEL = "RealESRGAN_x4plus_anime_6B.pth"   # line art and cel shading; RealESRGAN_x4plus.safetensors for photos

# Edit: Qwen-Image-Edit 2511 as a Q5_K_M GGUF (the ComfyUI-GGUF node loads it) - the native files are
# fp8 (Apple's GPU has none) or bf16 (41 GB). The 4-step Lightning LoRA cuts 40 steps to 4.
EDIT_MODEL = "qwen-image-edit-2511-Q5_K_M.gguf"
EDIT_TEXT_ENCODER = "qwen_2.5_vl_7b_fp8_scaled.safetensors"
EDIT_VAE = "qwen_image_vae.safetensors"
EDIT_FAST_LORA = "Qwen-Image-Edit-2511-Lightning-4steps-V1.0-bf16.safetensors"
# Keyframes: Wan 2.2 I2V A14B, two experts run one after the other (high noise, then low noise),
# each a Q5_K_M GGUF with its 4-step LoRA. It shares the video text encoder.
KEYFRAME_HIGH_MODEL = "Wan2.2-I2V-A14B-HighNoise-Q5_K_M.gguf"
KEYFRAME_LOW_MODEL = "Wan2.2-I2V-A14B-LowNoise-Q5_K_M.gguf"
KEYFRAME_HIGH_LORA = "wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors"
KEYFRAME_LOW_LORA = "wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors"
KEYFRAME_VAE = "wan_2.1_vae.safetensors"
NEUTRAL = 0x808080   # what a transparent input is laid on before an edit or keyframe model sees it

VIDEO_SUFFIXES = {".mp4", ".mov", ".webm", ".mkv"}


# ---------- ComfyUI API ----------
def _request(path: str, data: bytes | None = None, headers: dict | None = None, timeout: float = 60) -> bytes:
    req = urllib.request.Request(URL + path, data=data, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"ComfyUI rejected {path}: {e.read().decode(errors='replace')[:2000]}") from None
    except urllib.error.URLError as e:
        raise RuntimeError(f"ComfyUI is not reachable at {URL} ({e.reason}) - run ./llms start") from None


def _upload(file: Path) -> str:
    """Send a local image or video to the server's input folder; returns the name loaders refer to it by."""
    boundary = uuid.uuid4().hex
    body = b"".join([
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n".encode(),
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{file.name}\"\r\n"
        f"Content-Type: application/octet-stream\r\n\r\n".encode(),
        file.read_bytes(),
        f"\r\n--{boundary}--\r\n".encode(),
    ])
    reply = json.loads(_request("/upload/image", body, {"Content-Type": f"multipart/form-data; boundary={boundary}"},
                                timeout=300))
    return f"{reply['subfolder']}/{reply['name']}" if reply.get("subfolder") else reply["name"]


def _free() -> None:
    """Unload every model once the server is idle. The server applies it after the job it is
    running, so a queued caller is never cut off. LLMS_KEEP_LOADED=1 skips it for a batch."""
    if os.environ.get("LLMS_KEEP_LOADED") == "1":
        return
    try:
        _request("/free", json.dumps({"unload_models": True, "free_memory": True}).encode(),
                 {"Content-Type": "application/json"}, timeout=30)
    except RuntimeError:
        pass   # the job's own result or error matters more than the cleanup


def _run(workflow: dict, out: Path, timeout: float) -> Path:
    """Queue a workflow, wait for it, write what its "save" node produced to `out`, then unload."""
    try:
        return _wait(workflow, out, timeout)
    finally:
        _free()


def _wait(workflow: dict, out: Path, timeout: float) -> Path:
    payload = json.dumps({"prompt": workflow, "client_id": uuid.uuid4().hex}).encode()
    pid = json.loads(_request("/prompt", payload, {"Content-Type": "application/json"}))["prompt_id"]
    deadline = time.time() + timeout
    while time.time() < deadline:
        entry = json.loads(_request(f"/history/{pid}")).get(pid)
        if entry is None:
            time.sleep(2)
            continue
        status = entry.get("status", {})
        if status.get("status_str") == "error":
            raise RuntimeError(f"ComfyUI error: {json.dumps(status.get('messages', []))[:2000]}")
        for files in entry.get("outputs", {}).get("save", {}).values():
            for f in files if isinstance(files, list) else []:
                if isinstance(f, dict) and f.get("type") == "output" and f.get("filename"):
                    query = urllib.parse.urlencode(
                        {"filename": f["filename"], "subfolder": f.get("subfolder", ""), "type": "output"})
                    out.parent.mkdir(parents=True, exist_ok=True)
                    out.write_bytes(_request(f"/view?{query}", timeout=300))
                    return out
        raise RuntimeError("The workflow finished but produced no output file.")
    raise TimeoutError(f"Job {pid} did not finish within {timeout:.0f}s")


def _is_video(path: Path) -> bool:
    return Path(path).suffix.lower() in VIDEO_SUFFIXES


def _source(wf: dict, path: Path) -> tuple[list, list | None]:
    """Add the nodes that load `path`; returns (frames, fps) links - fps is None for a still image."""
    if _is_video(path):
        wf["source"] = {"class_type": "LoadVideo", "inputs": {"file": _upload(Path(path))}}
        wf["parts"] = {"class_type": "GetVideoComponents", "inputs": {"video": ["source", 0]}}
        return ["parts", 0], ["parts", 2]
    wf["source"] = {"class_type": "LoadImage", "inputs": {"image": _upload(Path(path))}}
    return ["source", 0], None


def _save(wf: dict, frames: list, fps, prefix: str) -> None:
    """Add the "save" node: a video when there is an fps, otherwise an image."""
    if fps is None:
        wf["save"] = {"class_type": "SaveImage", "inputs": {"images": frames, "filename_prefix": f"llms/{prefix}"}}
    else:
        wf["clip_out"] = {"class_type": "CreateVideo", "inputs": {"images": frames, "fps": fps}}
        wf["save"] = {"class_type": "SaveVideo", "inputs": {
            "video": ["clip_out", 0], "filename_prefix": f"llms/{prefix}", "format": "auto", "format.codec": "auto"}}


def _flat(wf: dict, name: str, path: Path, background: int = NEUTRAL) -> list:
    """Add the nodes that load the image at `path` laid on a flat `background`; returns its link.
    A transparent PNG's see-through pixels hold arbitrary colour, which these models would draw."""
    wf[name] = {"class_type": "LoadImage", "inputs": {"image": _upload(Path(path))}}
    wf[f"{name}_alpha"] = {"class_type": "InvertMask", "inputs": {"mask": [name, 1]}}  # an opaque image gives all-ones
    wf[f"{name}_size"] = {"class_type": "GetImageSize", "inputs": {"image": [name, 0]}}
    wf[f"{name}_bg"] = {"class_type": "EmptyImage", "inputs": {
        "width": [f"{name}_size", 0], "height": [f"{name}_size", 1], "batch_size": 1, "color": background}}
    wf[f"{name}_flat"] = {"class_type": "ImageCompositeMasked", "inputs": {
        "destination": [f"{name}_bg", 0], "source": [name, 0], "x": 0, "y": 0, "resize_source": False,
        "mask": [f"{name}_alpha", 0]}}
    return [f"{name}_flat", 0]


# ---------- the models ----------
def image(prompt: str, out: Path, *, negative: str = "", width: int = 1024, height: int = 1024, steps: int = 28,
          cfg: float = 5.0, seed: int | None = None, checkpoint: str = IMAGE_CHECKPOINT,
          timeout: float = 1800) -> Path:
    """Text-to-image (SDXL). Returns the path written."""
    seed = random.randint(0, 2**31) if seed is None else seed
    return _run({
        "ckpt": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": checkpoint}},
        "pos": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["ckpt", 1], "text": prompt}},
        "neg": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["ckpt", 1], "text": negative}},
        "latent": {"class_type": "EmptyLatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}},
        "sample": {"class_type": "KSampler", "inputs": {
            "model": ["ckpt", 0], "positive": ["pos", 0], "negative": ["neg", 0], "latent_image": ["latent", 0],
            "seed": seed, "steps": steps, "cfg": cfg, "sampler_name": "euler_ancestral", "scheduler": "normal",
            "denoise": 1.0}},
        "decode": {"class_type": "VAEDecode", "inputs": {"samples": ["sample", 0], "vae": ["ckpt", 2]}},
        "save": {"class_type": "SaveImage", "inputs": {"images": ["decode", 0], "filename_prefix": "llms/image"}},
    }, out, timeout)


def video(prompt: str, out: Path, *, start_image: Path | None = None, width: int = 704, height: int = 704,
          frames: int = 121, fps: int = 24, steps: int = 4, seed: int | None = None,
          timeout: float = 4 * 3600) -> Path:
    """Image-to-video from `start_image`, or text-to-video without one (Wan 2.2 TI2V 5B, 4-step).

    Width and height must be multiples of 32; frames must be 4n+1 (121 frames at 24 fps = 5 s).
    The model is distilled to run without a negative prompt, so there is none to pass.
    """
    if width % 32 or height % 32:
        raise ValueError("width and height must be multiples of 32")
    if frames % 4 != 1:
        raise ValueError("frames must be 4n+1 (e.g. 25, 49, 73, 97, 121)")
    seed = random.randint(0, 2**31) if seed is None else seed
    # The full VAE only encodes the start image; the small decoder turns the result into frames.
    latent = {"vae": ["vae", 0], "width": width, "height": height, "length": frames, "batch_size": 1}
    wf = {
        "unet": {"class_type": "UNETLoader", "inputs": {"unet_name": VIDEO_MODEL, "weight_dtype": "default"}},
        "lora": {"class_type": "LoraLoaderModelOnly", "inputs": {
            "model": ["unet", 0], "lora_name": VIDEO_FAST_LORA, "strength_model": 1.0}},
        # On the CPU: the encoder's fp8 weights are a type Apple's GPU cannot load.
        "clip": {"class_type": "CLIPLoader", "inputs": {
            "clip_name": VIDEO_TEXT_ENCODER, "type": "wan", "device": "cpu"}},
        "vae": {"class_type": "VAELoader", "inputs": {"vae_name": VIDEO_VAE}},
        "decoder": {"class_type": "VAELoader", "inputs": {"vae_name": VIDEO_FAST_DECODER}},
        "shift": {"class_type": "ModelSamplingSD3", "inputs": {"model": ["lora", 0], "shift": 8.0}},
        "pos": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["clip", 0], "text": prompt}},
        "neg": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["clip", 0], "text": ""}},
        "latent": {"class_type": "Wan22ImageToVideoLatent", "inputs": latent},
        "sample": {"class_type": "KSampler", "inputs": {
            "model": ["shift", 0], "positive": ["pos", 0], "negative": ["neg", 0], "latent_image": ["latent", 0],
            "seed": seed, "steps": steps, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple",
            "denoise": 1.0}},
        "decode": {"class_type": "VAEDecode", "inputs": {"samples": ["sample", 0], "vae": ["decoder", 0]}},
    }
    if start_image is not None:
        wf["start"] = {"class_type": "LoadImage", "inputs": {"image": _upload(Path(start_image))}}
        latent["start_image"] = ["start", 0]
    _save(wf, ["decode", 0], float(fps), "video")
    return _run(wf, out, timeout)


def matte(source: Path, out: Path, *, mask_only: bool = False, timeout: float = 3600) -> Path:
    """Find the subject (BiRefNet). An image becomes a transparent PNG, or its mask with `mask_only`.
    A video always becomes a mask video - white subject on black - since mp4 carries no alpha."""
    wf = {"model": {"class_type": "LoadBackgroundRemovalModel", "inputs": {"bg_removal_name": MATTE_MODEL}}}
    frames, fps = _source(wf, source)
    wf["mask"] = {"class_type": "RemoveBackground", "inputs": {"bg_removal_model": ["model", 0], "image": frames}}
    if fps is not None or mask_only:
        wf["result"] = {"class_type": "MaskToImage", "inputs": {"mask": ["mask", 0]}}
    else:
        wf["alpha"] = {"class_type": "InvertMask", "inputs": {"mask": ["mask", 0]}}
        wf["result"] = {"class_type": "JoinImageWithAlpha", "inputs": {"image": frames, "alpha": ["alpha", 0]}}
    _save(wf, ["result", 0], fps, "matte")
    return _run(wf, out, timeout)


def interpolate(source: Path, out: Path, *, multiplier: int = 2, timeout: float = 3600) -> Path:
    """Insert generated in-between frames (FILM). The clip keeps its length; its fps is multiplied."""
    if not _is_video(source):
        raise ValueError("interpolate needs a video")
    wf = {"model": {"class_type": "FrameInterpolationModelLoader", "inputs": {"model_name": INTERPOLATION_MODEL}}}
    frames, fps = _source(wf, source)
    wf["result"] = {"class_type": "FrameInterpolate", "inputs": {
        "interp_model": ["model", 0], "images": frames, "multiplier": multiplier}}
    wf["fps"] = {"class_type": "ComfyMathExpression", "inputs": {
        "expression": "a * b", "values.a": fps, "values.b": multiplier}}
    _save(wf, ["result", 0], ["fps", 0], "interpolate")
    return _run(wf, out, timeout)


def upscale(source: Path, out: Path, *, scale: float = 4.0, model: str = UPSCALE_MODEL, timeout: float = 3600) -> Path:
    """Upscale an image or a short video (Real-ESRGAN). The model works at 4x; any other `scale` is
    reached by resizing its result down. Every frame is held in memory at 4x, so keep videos short."""
    wf = {"model": {"class_type": "UpscaleModelLoader", "inputs": {"model_name": model}}}
    frames, fps = _source(wf, source)
    wf["result"] = {"class_type": "ImageUpscaleWithModel", "inputs": {"upscale_model": ["model", 0], "image": frames}}
    result = ["result", 0]
    if scale != 4.0:
        wf["resize"] = {"class_type": "ImageScaleBy", "inputs": {
            "image": result, "upscale_method": "lanczos", "scale_by": scale / 4.0}}
        result = ["resize", 0]
    _save(wf, result, fps, "upscale")
    return _run(wf, out, timeout)


def _image_size(path: Path) -> tuple[int, int]:
    """Width and height of a PNG or JPEG, read from its header."""
    data = Path(path).read_bytes()
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")
    if data[:2] == b"\xff\xd8":
        i = 2
        while i + 9 < len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            marker, length = data[i + 1], int.from_bytes(data[i + 2:i + 4], "big")
            if marker in (0xC0, 0xC1, 0xC2):
                return int.from_bytes(data[i + 7:i + 9], "big"), int.from_bytes(data[i + 5:i + 7], "big")
            i += 2 + length
    raise ValueError(f"{path}: edit reads PNG or JPEG images")


def _qwen_size(w: int, h: int, side: int, step: int) -> tuple[int, int]:
    """The size Qwen's edit encoder resizes a w x h image to (about side x side pixels), chosen so that
    asking the encoder to resize it again is a no-op. Its resize is an "area" resize, which Apple's GPU
    can only do by whole-number factors - handed any other size it fails."""
    def fit(a: int, b: int) -> tuple[int, int]:
        k = (side * side / (a * b)) ** 0.5
        return round(a * k / step) * step, round(b * k / step) * step
    size = fit(w, h)
    for _ in range(8):
        if fit(*size) == size:
            return size
        size = fit(*size)
    raise ValueError(f"no stable Qwen edit size for {w}x{h}")


def edit(images: Path | list[Path], instruction: str, out: Path, *, steps: int = 4, seed: int | None = None,
         background: int = NEUTRAL, timeout: float = 3600) -> Path:
    """Edit an image by instruction, keeping who is in it and how it is drawn (Qwen-Image-Edit 2511).

    `images` is one image or up to three: the first is the one edited, the rest are references the
    instruction can name ("picture 2"). The result has the first image's size.

    A transparent PNG is laid on a flat `background` (mid grey) first, and the result is opaque:
    the caller re-mattes it. At 4 steps the Lightning LoRA runs; above 8 the full model runs at its
    own settings (cfg 4, about ten times slower).
    """
    images = [Path(images)] if isinstance(images, (str, Path)) else [Path(i) for i in images]
    if not 1 <= len(images) <= 3:
        raise ValueError("edit takes one to three images")
    seed = random.randint(0, 2**31) if seed is None else seed
    fast = steps <= 8
    wf = {
        "unet": {"class_type": "UnetLoaderGGUF", "inputs": {"unet_name": EDIT_MODEL}},
        # On the CPU: the encoder's fp8 weights are a type Apple's GPU cannot load.
        "clip": {"class_type": "CLIPLoader", "inputs": {
            "clip_name": EDIT_TEXT_ENCODER, "type": "qwen_image", "device": "cpu"}},
        "vae": {"class_type": "VAELoader", "inputs": {"vae_name": EDIT_VAE}},
        "shift": {"class_type": "ModelSamplingAuraFlow", "inputs": {"model": ["unet", 0], "shift": 3.1}},
        "norm": {"class_type": "CFGNorm", "inputs": {"model": ["shift", 0], "strength": 1.0}},
    }
    model = ["norm", 0]
    if fast:
        wf["lora"] = {"class_type": "LoraLoaderModelOnly", "inputs": {
            "model": model, "lora_name": EDIT_FAST_LORA, "strength_model": 1.0}}
        model = ["lora", 0]
    # TextEncodeQwenImageEditPlus resizes each image twice - about 384x384 for the vision encoder,
    # about 1024x1024 for the reference latent. Both resizes are done here at sizes it leaves alone,
    # and the reference latents are attached with ReferenceLatent, as the node does with a vae.
    looks, latents = {}, []
    for n, path in enumerate(images, 1):
        flat = _flat(wf, f"in{n}", path, background)
        w, h = _image_size(path)
        for kind, (side, step) in (("look", (384, 1)), ("ref", (1024, 8))):
            sw, sh = _qwen_size(w, h, side, step)
            wf[f"in{n}_{kind}"] = {"class_type": "ImageScale", "inputs": {
                "image": flat, "upscale_method": "lanczos", "width": sw, "height": sh, "crop": "disabled"}}
        wf[f"in{n}_latent"] = {"class_type": "VAEEncode", "inputs": {"pixels": [f"in{n}_ref", 0], "vae": ["vae", 0]}}
        looks[f"image{n}"] = [f"in{n}_look", 0]
        latents.append([f"in{n}_latent", 0])
    for name, text in (("pos", instruction), ("neg", "")):
        wf[f"{name}_0"] = {"class_type": "TextEncodeQwenImageEditPlus", "inputs": {
            "clip": ["clip", 0], "prompt": text, **looks}}
        for n, latent in enumerate(latents, 1):
            wf[f"{name}_{n}"] = {"class_type": "ReferenceLatent", "inputs": {
                "conditioning": [f"{name}_{n - 1}", 0], "latent": latent}}
        # 2511 reads its reference images this way; a GGUF does not carry the marker that says so.
        wf[name] = {"class_type": "FluxKontextMultiReferenceLatentMethod", "inputs": {
            "conditioning": [f"{name}_{len(latents)}", 0], "reference_latents_method": "index_timestep_zero"}}
    wf.update({
        "sample": {"class_type": "KSampler", "inputs": {
            "model": model, "positive": ["pos", 0], "negative": ["neg", 0], "latent_image": latents[0],
            "seed": seed, "steps": steps, "cfg": 1.0 if fast else 4.0, "sampler_name": "euler",
            "scheduler": "simple", "denoise": 1.0}},
        "decode": {"class_type": "VAEDecode", "inputs": {"samples": ["sample", 0], "vae": ["vae", 0]}},
        "resize": {"class_type": "ImageScale", "inputs": {
            "image": ["decode", 0], "upscale_method": "lanczos", "width": _image_size(images[0])[0],
            "height": _image_size(images[0])[1], "crop": "disabled"}},
    })
    _save(wf, ["resize", 0], None, "edit")
    return _run(wf, out, timeout)


def keyframes(prompt: str, start: Path, end: Path | None, out: Path, *, width: int = 640, height: int = 640,
              frames: int = 81, fps: int = 16, steps: int = 4, seed: int | None = None,
              background: int = NEUTRAL, negative: str = "", cfg_high: float = 1.0,
              timeout: float = 12 * 3600) -> Path:
    """The in-between video from a first frame to a last frame (Wan 2.2 I2V A14B, 4-step).

    Width and height must be multiples of 16; frames must be 4n+1 (81 frames at 16 fps = 5 s). The
    clip opens on `start` and lands on `end`. Transparent PNGs are laid on a flat `background` first,
    so the video is opaque. The high-noise expert runs the first half of the steps, the low-noise
    expert the rest; only one of them needs to be in memory at a time. With `end` None the clip is
    conditioned on `start` alone and lands wherever the prompt takes it (see `i2v`).
    `negative` and `cfg_high` give the high-noise expert a real negative prompt at that cfg; the
    low-noise expert always runs at cfg 1.0.
    """
    if width % 16 or height % 16:
        raise ValueError("width and height must be multiples of 16")
    if frames % 4 != 1:
        raise ValueError("frames must be 4n+1 (e.g. 17, 33, 49, 81)")
    if steps < 2:
        raise ValueError("steps must be at least 2 - half go to each expert")
    seed = random.randint(0, 2**31) if seed is None else seed
    wf = {
        "clip": {"class_type": "CLIPLoader", "inputs": {
            "clip_name": VIDEO_TEXT_ENCODER, "type": "wan", "device": "cpu"}},
        "vae": {"class_type": "VAELoader", "inputs": {"vae_name": KEYFRAME_VAE}},
        "pos_text": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["clip", 0], "text": prompt}},
        "neg_text": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["clip", 0], "text": negative}},
    }
    wf["cond"] = {"class_type": "WanImageToVideo" if end is None else "WanFirstLastFrameToVideo", "inputs": {
        "positive": ["pos_text", 0], "negative": ["neg_text", 0], "vae": ["vae", 0], "width": width,
        "height": height, "length": frames, "batch_size": 1, "start_image": _flat(wf, "start", start, background)}}
    if end is not None:
        wf["cond"]["inputs"]["end_image"] = _flat(wf, "end", end, background)
    for name, unet, lora in (("high", KEYFRAME_HIGH_MODEL, KEYFRAME_HIGH_LORA),
                             ("low", KEYFRAME_LOW_MODEL, KEYFRAME_LOW_LORA)):
        wf[f"{name}_unet"] = {"class_type": "UnetLoaderGGUF", "inputs": {"unet_name": unet}}
        wf[f"{name}_lora"] = {"class_type": "LoraLoaderModelOnly", "inputs": {
            "model": [f"{name}_unet", 0], "lora_name": lora, "strength_model": 1.0}}
        wf[f"{name}_model"] = {"class_type": "ModelSamplingSD3", "inputs": {"model": [f"{name}_lora", 0], "shift": 5.0}}
    common = {"positive": ["cond", 0], "negative": ["cond", 1], "steps": steps,
              "sampler_name": "euler", "scheduler": "simple", "noise_seed": seed}
    wf["sample_high"] = {"class_type": "KSamplerAdvanced", "inputs": {
        **common, "cfg": cfg_high, "model": ["high_model", 0], "latent_image": ["cond", 2], "add_noise": "enable",
        "start_at_step": 0, "end_at_step": steps // 2, "return_with_leftover_noise": "enable"}}
    wf["sample_low"] = {"class_type": "KSamplerAdvanced", "inputs": {
        **common, "cfg": 1.0, "model": ["low_model", 0], "latent_image": ["sample_high", 0], "add_noise": "disable",
        "start_at_step": steps // 2, "end_at_step": 10000, "return_with_leftover_noise": "disable"}}
    wf["decode"] = {"class_type": "VAEDecode", "inputs": {"samples": ["sample_low", 0], "vae": ["vae", 0]}}
    _save(wf, ["decode", 0], float(fps), "keyframes")
    return _run(wf, out, timeout)


def i2v(prompt: str, start: Path, out: Path, **kwargs) -> Path:
    """The video that follows a first frame alone (Wan 2.2 I2V A14B, 4-step): `keyframes` with no end frame."""
    return keyframes(prompt, start, None, out, **kwargs)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="kind", required=True)

    i = sub.add_parser("image", help="text-to-image")
    i.add_argument("prompt")
    i.add_argument("-o", "--out", type=Path, default=Path("image.png"))
    i.add_argument("--negative", default="")
    i.add_argument("--width", type=int, default=1024)
    i.add_argument("--height", type=int, default=1024)
    i.add_argument("--steps", type=int, default=28)
    i.add_argument("--cfg", type=float, default=5.0)
    i.add_argument("--seed", type=int)
    i.add_argument("--checkpoint", default=IMAGE_CHECKPOINT)

    v = sub.add_parser("video", help="image-to-video with --image, otherwise text-to-video")
    v.add_argument("prompt")
    v.add_argument("-o", "--out", type=Path, default=Path("video.mp4"))
    v.add_argument("--image", type=Path, help="start frame; turns this into image-to-video")
    v.add_argument("--width", type=int, default=704)
    v.add_argument("--height", type=int, default=704)
    v.add_argument("--frames", type=int, default=121, help="4n+1; 121 at 24 fps is 5 s")
    v.add_argument("--fps", type=int, default=24)
    v.add_argument("--steps", type=int, default=4)
    v.add_argument("--seed", type=int)

    m = sub.add_parser("matte", help="image -> transparent PNG; video -> mask video")
    m.add_argument("source", type=Path)
    m.add_argument("-o", "--out", type=Path, required=True)
    m.add_argument("--mask-only", action="store_true", help="for an image, write the mask instead of the cutout")

    n = sub.add_parser("interpolate", help="multiply a video's frame rate with generated in-between frames")
    n.add_argument("source", type=Path)
    n.add_argument("-o", "--out", type=Path, required=True)
    n.add_argument("--multiplier", type=int, default=2)

    u = sub.add_parser("upscale", help="upscale an image or a short video")
    u.add_argument("source", type=Path)
    u.add_argument("-o", "--out", type=Path, required=True)
    u.add_argument("--scale", type=float, default=4.0)
    u.add_argument("--model", default=UPSCALE_MODEL)

    e = sub.add_parser("edit", help="edit an image by instruction, keeping identity and style (output is opaque)")
    e.add_argument("images", type=Path, nargs="+", help="the image to edit, then up to two reference images")
    e.add_argument("instruction")
    e.add_argument("-o", "--out", type=Path, required=True)
    e.add_argument("--steps", type=int, default=4, help="4 uses the Lightning LoRA; above 8 runs the full model")
    e.add_argument("--seed", type=int)

    k = sub.add_parser("keyframes", help="first frame + last frame -> the video in between")
    k.add_argument("prompt")
    k.add_argument("--start", type=Path, required=True, help="first frame")
    k.add_argument("--end", type=Path, required=True, help="last frame")
    k.add_argument("-o", "--out", type=Path, default=Path("keyframes.mp4"))
    k.add_argument("--width", type=int, default=640)
    k.add_argument("--height", type=int, default=640)
    k.add_argument("--frames", type=int, default=81, help="4n+1; 81 at 16 fps is 5 s")
    k.add_argument("--fps", type=int, default=16)
    k.add_argument("--steps", type=int, default=4)
    k.add_argument("--seed", type=int)
    k.add_argument("--negative", default="", help="negative prompt for the high-noise expert; needs --cfg-high above 1")
    k.add_argument("--cfg-high", type=float, default=1.0, help="cfg of the high-noise expert; the low-noise one stays 1.0")

    j = sub.add_parser("i2v", help="first frame alone -> the video that follows (A14B, no end frame)")
    j.add_argument("prompt")
    j.add_argument("--image", type=Path, required=True, help="first frame")
    j.add_argument("-o", "--out", type=Path, default=Path("i2v.mp4"))
    j.add_argument("--width", type=int, default=640)
    j.add_argument("--height", type=int, default=640)
    j.add_argument("--frames", type=int, default=81, help="4n+1; 81 at 16 fps is 5 s")
    j.add_argument("--fps", type=int, default=16)
    j.add_argument("--steps", type=int, default=4)
    j.add_argument("--seed", type=int)
    j.add_argument("--negative", default="", help="negative prompt for the high-noise expert; needs --cfg-high above 1")
    j.add_argument("--cfg-high", type=float, default=1.0, help="cfg of the high-noise expert; the low-noise one stays 1.0")

    a = ap.parse_args()
    t0 = time.time()
    try:
        if a.kind == "image":
            path = image(a.prompt, a.out, negative=a.negative, width=a.width, height=a.height, steps=a.steps,
                         cfg=a.cfg, seed=a.seed, checkpoint=a.checkpoint)
        elif a.kind == "video":
            path = video(a.prompt, a.out, start_image=a.image, width=a.width, height=a.height, frames=a.frames,
                         fps=a.fps, steps=a.steps, seed=a.seed)
        elif a.kind == "matte":
            path = matte(a.source, a.out, mask_only=a.mask_only)
        elif a.kind == "interpolate":
            path = interpolate(a.source, a.out, multiplier=a.multiplier)
        elif a.kind == "edit":
            path = edit(a.images, a.instruction, a.out, steps=a.steps, seed=a.seed)
        elif a.kind == "keyframes":
            path = keyframes(a.prompt, a.start, a.end, a.out, width=a.width, height=a.height, frames=a.frames,
                             fps=a.fps, steps=a.steps, seed=a.seed, negative=a.negative, cfg_high=a.cfg_high)
        elif a.kind == "i2v":
            path = i2v(a.prompt, a.image, a.out, width=a.width, height=a.height, frames=a.frames,
                       fps=a.fps, steps=a.steps, seed=a.seed, negative=a.negative, cfg_high=a.cfg_high)
        else:
            path = upscale(a.source, a.out, scale=a.scale, model=a.model)
    except (RuntimeError, TimeoutError, ValueError) as e:
        sys.exit(str(e))
    print(f"{path}  ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
