# Game asset pipeline — instructions for Claude Code

This folder generates game assets locally on an Apple Silicon Mac. No Docker.
ComfyUI runs natively at http://127.0.0.1:8188 and does the image generation;
the Python scripts here drive it and post-process the results.

## Art style
Chibi characters. The style is locked in `style.json` (checkpoint, LoRA, style tags,
sizes per asset type). Do not change `style.json` unless the user asks — consistency
across all assets depends on it. Put per-asset details in the asset list instead.

## Licensing (assets ship in a commercial game)
Only use models whose license allows commercial use of outputs:
- Animagine XL 4.0 / SDXL — CreativeML Open RAIL++-M (OK)
- BiRefNet (background removal) — MIT (OK)
- Wan 2.2 (video) — Apache 2.0 (OK)
Do NOT add: RMBG-2.0 (non-commercial), FLUX.1 [dev] (non-commercial), any Civitai
LoRA/checkpoint unless its page allows selling generated images. If unsure, stop and ask.
Never delete `output/manifest.jsonl`; it is the provenance record.

## Before anything
1. `curl -s http://127.0.0.1:8188/system_stats` — if it fails, ask the user to run
   `./start_comfyui.sh` in a separate terminal (it must stay running).
2. `./.venv/bin/python generate_assets.py --check` — confirms models are installed.

## Commands (always use ./.venv/bin/python)
- Batch images: write a JSON list like `assets.example.json`, then
  `./.venv/bin/python generate_assets.py my_assets.json`
  Types: character, building, prop (transparent PNG) and background (opaque).
  Fields: name, type, prompt (subject only — style tags are added automatically),
  count, optional seed, negative, width, height, transparent.
- Single image: `./.venv/bin/python generate_assets.py --one "1girl, archer" --type character --name archer`
- Background removal on existing files: `./.venv/bin/python remove_bg.py in/*.png -o output/transparent`
- Video → sprite sheet: `./.venv/bin/python video_to_spritesheet.py walk.mp4 --fps 12 --cell 256`
  Use `--start/--end` to keep just one loop; `--lock-x` if the character drifts sideways; `--method chroma --key 00ff00` for green-screen video (much faster).
- Custom ComfyUI workflow (IP-Adapter, LayerDiffuse, Wan video, …): user exports it with
  "Export (API)", replaces the prompt text with `{{PROMPT}}` and seed with `"{{SEED}}"`, then
  `./.venv/bin/python generate_assets.py --workflow wf.json --one "..." --name x`

## Working rules
- Generations take ~1–2 min per SDXL image on this Mac. For long batches run the
  command in the background and report progress from its output.
- Re-running a batch skips files that already exist, so resuming after a failure is safe.
- After generating, open a few results and check them (transparency, style, cropping)
  before reporting success. Report failures listed at the end of the run.
- Outputs go to `output/<type>/`; originals to `output/raw/`; sprite sheets to `output/sprites/`.
- When the user wants assets in Unity, copy them into the Unity project's `Assets/Art/...`
  folder (ask for the path once) rather than moving them.
