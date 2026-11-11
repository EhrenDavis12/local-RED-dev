# Local Game Asset Pipeline — Setup Guide

Oct 1, 2026 · @Ehren Davis

## Summary

Everything except generating the animation videos runs well on your MacBook Pro, natively, with no Docker. Video generation on an M1 takes far longer than 10 minutes per clip, so that one step needs a different plan (see Animations).

- **Images (character sprites, buildings, props, backgrounds):** local. ComfyUI + Animagine XL 4.0 (an anime/chibi-capable SDXL model), with a style file that locks the chibi look for every asset.
- **Transparent PNGs:** local. BiRefNet cuts the background out automatically after each image is made.
- **Video → sprite sheets:** local and fast. One command turns a clip into a transparent, Unity-ready sheet.
- **Generating the videos themselves:** not practical locally on an M1. Use a cloud model per clip, or skip video and animate the sprites in Unity.
- **Claude Code:** runs all of it from Terminal through the scripts in `asset-pipeline.zip`, guided by its `CLAUDE.md`.

## Run time expectations

Every image and sprite-sheet task fits well under your 10-minute limit; only local video generation blows past it. These are estimates from published M1 reports; your first run of the pipeline prints real timings for your machine. A 32GB M1 MacBook Pro is an M1 Pro or M1 Max, and a Max runs roughly 1.5–2× faster.

| Task | Expected time on M1 Pro / Max 32GB | Under 10 min? |
| --- | --- | --- |
| One 1024×1024 chibi sprite, building or prop (28 steps) | about 1–2 min | Yes |
| One 1344×768 background | about 1.5–2.5 min | Yes |
| Background removal per image (BiRefNet) | a few seconds | Yes |
| Batch of 20 images | about 25–45 min, unattended | Run overnight or while away |
| Video → sprite sheet, 2 s loop at 12 fps (24 frames) | about 1–3 min | Yes |
| Video → sprite sheet, 10 s clip at 12 fps (120 frames) | about 5–12 min with BiRefNet; under 1 min with a green-screen video | Mostly |
| Generate a 5–10 s animation video locally (Wan 2.2) | 30 min to well over an hour per clip | No |
| Generate a 5–10 s animation video in the cloud (Wan 2.2) | a few minutes per clip | Yes |
| First-time setup (downloads \~9 GB) | 30–60 min | One time |

Two things make the 10-second clips easier. Game sprite loops are usually 0.5–2 seconds, so the script's `--start`/`--end` flags keep just the loop. And generating videos on a solid green background lets the fast chroma-key mode replace BiRefNet.

## Licensing

Every model in this pipeline allows commercial use of what it produces. The pipeline also logs each image's prompt, seed and model to `output/manifest.jsonl`, so you can show where any shipped asset came from. I'm not a lawyer; read each license once before you ship.

| Model or tool | Role | License | Shipped assets OK? |
| --- | --- | --- | --- |
| [Animagine XL 4.0](https://huggingface.co/cagliostrolab/animagine-xl-4.0) | Image generation (chibi/anime) | CreativeML Open RAIL++-M | Yes, with use-based restrictions (no harmful content) |
| SDXL 1.0 base | The model Animagine is built on | CreativeML Open RAIL++-M | Yes |
| BiRefNet | Background removal | MIT | Yes |
| [Wan 2.2](https://docs.comfy.org/tutorials/video/wan/wan2_2) | Video generation | Apache 2.0 | Yes |
| ComfyUI | The app that runs the models | GPL-3.0 (covers the software, not your images) | Yes |
| RMBG-2.0 | Background removal | Non-commercial without a paid license | **Avoid** |
| FLUX.1 \[dev\] | Image generation | Non-commercial without a paid license | **Avoid** |
| Wan fine-tunes such as LongLive | Video | Some are non-commercial (CC BY-NC) | **Check each one** |
| Civitai LoRAs and checkpoints | Style add-ons | Varies per upload | **Only if the page allows selling images** |

The safest chibi LoRA is one you train yourself on art you already own. Your style is already decided, so 20–40 of your approved images is enough to train one.

## Step-by-step setup

Setup is about 10 minutes of your time plus 30–60 minutes of downloads, done once.

1. **Install Homebrew** if you don't have it: follow the one-line install at brew.sh.
2. **Unzip the kit.** Put the `asset-pipeline` folder somewhere permanent, for example `~/GameDev/asset-pipeline`.
3. **Run the setup script** in Terminal:
   1. `cd ~/GameDev/asset-pipeline`
   2. `chmod +x setup_mac.sh && ./setup_mac.sh`
   3. It installs Python 3.11 and ffmpeg, installs ComfyUI in `~/AI/ComfyUI` with Metal GPU support, downloads Animagine XL 4.0 (\~7 GB), and sets up the pipeline's own Python environment.
4. **Start ComfyUI:** `./start_comfyui.sh`. Leave that Terminal window open; it is the image engine. You can also open http://127.0.0.1:8188 in a browser to experiment by hand.
5. **Check it:** in a second Terminal, `./.venv/bin/python generate_assets.py --check`. It should list the Animagine checkpoint.
6. **Make a test image:** `./.venv/bin/python generate_assets.py --one "1girl, archer" --name archer`. The first run downloads BiRefNet (\~1 GB). The result lands in `output/character/archer_01.png` with a transparent background.
7. **Lock in your chibi style:**
   1. Open `style.json` and adjust the style tags to match your art direction.
   2. If you have (or train) a chibi style LoRA, put the `.safetensors` file in `~/AI/ComfyUI/models/loras`, set its file name in `style.json`, and set `enabled` to true.
   3. Generate a few test characters and tweak until they match your approved art. After that, leave `style.json` alone.
8. **Point Claude Code at the folder:** open Claude Code in the `asset-pipeline` folder. It reads `CLAUDE.md` automatically and knows every command, the licensing rules and the style rules.

## Daily workflow

You describe what you need; Claude Code writes the asset list, runs the batch, and checks the results.

**Images.** List assets in a JSON file (see `assets.example.json`). Each entry has a name, a type and a short subject prompt; the chibi style tags are added automatically.

| Type | Size | Background | Output folder |
| --- | --- | --- | --- |
| character | 1024×1024 | Transparent PNG, trimmed | `output/character/` |
| building | 1024×1024 | Transparent PNG, trimmed | `output/building/` |
| prop | 1024×1024 | Transparent PNG, trimmed | `output/prop/` |
| background | 1344×768 | Opaque PNG | `output/background/` |

Run it with `./.venv/bin/python generate_assets.py my_assets.json`. If a batch stops partway, run the same command again and it skips what is already done.

**Sprite sheets.** For each animation video:

`./.venv/bin/python video_to_spritesheet.py walk.mp4 --fps 12 --cell 256 --start 0 --end 1.5`

- `--lock-x` keeps a character centred if it drifts across the frame.
- `--method chroma --key 00ff00` is the fast mode for green-screen videos.
- Output: `walk_sheet.png`, a `frames/` folder, and `walk.json` with frame positions and fps.
- Every frame uses the same crop, anchored bottom-centre, so the feet don't jitter.

**Into Unity.** Set the sheet's Sprite Mode to Multiple, open the Sprite Editor, and slice by cell size with the pivot at Bottom Center. Claude Code can also write a small Unity editor script that reads the `.json` and builds the animation clips for you.

## Animations

Generating the videos locally isn't realistic on an M1: one tester reported 82 minutes for a 2-second Wan 2.2 clip on an M1 Max, and Wan's own figure for a 5-second clip is about 9 minutes on a high-end NVIDIA card. Three ways to get the many animations you need:

| Option | How it works | Time per animation | Cost | Best for |
| --- | --- | --- | --- | --- |
| A. Cloud video, local processing | Send a sprite image + motion prompt to Wan 2.2 image-to-video on Replicate; download the clip; run the sprite-sheet script locally | a few minutes | Pay per clip | Organic motion: attacks, spells, idles with hair or cloth |
| B. Skeletal animation in Unity | Generate the character as separate parts (head, body, arms, legs) locally; rig once in Unity's 2D Animation package; reuse the rig for every move | minutes per move after rigging | Free | Large numbers of walks, runs, idles; chibi bodies rig especially well |
| C. Local Wan 2.2 | Run Wan 2.2 5B in ComfyUI overnight | 30 min to over an hour per clip | Free | Occasional clips you can queue overnight |

My suggestion is B for the bulk and A for the few moves that need hand-drawn-looking motion. Either way, generate the videos on a flat green background so the sprite sheets can use the fast chroma-key mode, and keep each clip to the single loop you need.

The pipeline already supports C and any cloud-downloaded clip: export a Wan workflow from ComfyUI as API JSON and run it with `generate_assets.py --workflow`.

## What Claude Code automates

After the one-time setup, your job is mostly approving art; Claude Code handles the running.

| Claude Code does | You do |
| --- | --- |
| Writes asset lists from plain descriptions ("10 villagers, 4 shops") | Run `setup_mac.sh` once and keep `start_comfyui.sh` open while generating |
| Runs batches, resumes them after failures, reports timings | Approve the chibi style in `style.json` and supply or train the style LoRA |
| Removes backgrounds and trims every transparent asset | Pick the best of each set of variations |
| Turns every animation video into a sprite sheet | Supply the animation videos (or rig characters in Unity) |
| Copies finished assets into your Unity project and writes import scripts | Check licenses before adding any new model |
| Keeps the provenance log in `output/manifest.jsonl` |  |

### Sources

- [Docker Model Runner docs](https://docs.docker.com/ai/model-runner/): image generation needs NVIDIA GPUs on Linux
- [Animagine XL 4.0 model page](https://huggingface.co/cagliostrolab/animagine-xl-4.0)
- [Wan 2.2 repository](https://github.com/Wan-Video/Wan2.2) and [ComfyUI Wan 2.2 guide](https://docs.comfy.org/tutorials/video/wan/wan2_2)
- [LTX-2 vs Wan 2.2 on M1 Max](https://lilting.ch/en/articles/ltx2-wan22-mac-local-video-gen): local video timings on Apple Silicon
- [ComfyUI issue #2992](https://github.com/comfyanonymous/ComfyUI/issues/2992): SDXL timings on M1 MacBook Pro
