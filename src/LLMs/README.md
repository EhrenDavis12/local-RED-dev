# LLMs

Runs the local generation models on this Mac and nothing else, behind one ComfyUI server.
No Docker. Style, prompts, colour keying and sprite sheets belong to whichever project calls
this one.

## Use

```
./llms install     # once: ComfyUI + every model in models.txt (safe to re-run)
./llms start       # server up on http://127.0.0.1:8188
./llms status      # is it up, which models are installed
./llms free        # drop models from memory, leave the server up
./llms stop

python3 generate.py image "a red apple on a table" -o apple.png
python3 generate.py video "the apple rolls off the table" --image apple.png -o roll.mp4
python3 generate.py matte apple.png -o apple_cutout.png        # image -> transparent PNG
python3 generate.py matte roll.mp4 -o roll_mask.mp4            # video -> white-on-black mask video
python3 generate.py interpolate roll.mp4 -o roll_smooth.mp4    # 2x the frames, 2x the fps
python3 generate.py upscale apple.png -o apple_4x.png          # image or short video
python3 generate.py edit knight.png "same knight, only the head turns left" -o knight_turn.png
python3 generate.py edit knight.png shield.png "give him the shield from picture 2" -o armed.png
python3 generate.py keyframes "the knight turns his head" --start a.png --end b.png \
    --frames 33 --width 512 --height 512 -o a_to_b.mp4           # first + last frame -> the video between
```

`generate.py` is standard library only, so any `python3` runs it, and another project can
shell out to it or `from generate import image, video, matte, interpolate, upscale, edit, keyframes`. Each
command prints the file it wrote and how long it took, and exits non-zero with the reason on
failure. `python3 generate.py <command> -h` lists every setting.

Jobs queue: the server runs one at a time, so two callers never fight over memory, they wait.

## Models

| Command | Model | License |
|---|---|---|
| `image` | Animagine XL 4.0 (SDXL) | CreativeML Open RAIL++-M |
| `video` | Wan 2.2 TI2V 5B, with the FastWan 4-step LoRA and the LightTAE decoder | Apache 2.0 |
| `matte` | BiRefNet | MIT |
| `interpolate` | FILM | Apache 2.0 |
| `upscale` | Real-ESRGAN (anime model by default, `--model RealESRGAN_x4plus.safetensors` for photos) | BSD 3-Clause |
| `edit` | Qwen-Image-Edit 2511 (Q5_K_M GGUF), Qwen2.5-VL 7B text encoder, Lightning 4-step LoRA | Apache 2.0 |
| `keyframes` | Wan 2.2 I2V A14B, high- and low-noise experts (Q5_K_M GGUF), lightx2v 4-step LoRAs, Wan 2.1 VAE | Apache 2.0 |

Every license allows commercial use of what the model produces. `models.txt` is the list
`./llms install` downloads, about 26 GB; add a model by adding a line there, and check its
license first. The files live in `~/AI/ComfyUI/models`, outside this repo. `edit` and `keyframes`
add about 49 GB more.

`edit` and `keyframes` need the one custom node, [ComfyUI-GGUF](https://github.com/city96/ComfyUI-GGUF)
(Apache 2.0), which `./llms install` clones at a pinned commit. Their native files will not run
here: the fp8 ones are a type Apple's GPU cannot hold, and the bf16 ones are 41 GB (edit) and
2 x 29 GB (keyframes). The GGUFs are 15 GB and 2 x 11 GB.

## One model in memory at a time

There is one server for every model. It loads a model when a job asks for it and evicts
others to make room, so nothing has to be started or stopped to switch between image and
video. `./llms free` empties memory without stopping the server, for when Unity needs the
room.

Memory is also handed back on its own: `generate.py` unloads every model when its job ends
(`LLMS_KEEP_LOADED=1` skips that for a batch of the same model), and the server keeps no old
results (`--cache-none`). The models may take at most 28 GB (`LLMS_MEMORY_CAP_GB`, 0 for no
cap); a job that needs more fails with "MPS backend out of memory" instead of stalling the
Mac. The cap takes effect at `./llms start`.

## What it costs on this machine (M1 Max, 32 GB)

| Job | Time |
|---|---|
| Server start | about 10 s |
| `image`, 1024×1024 | about 90 s |
| `video`, 704×704, 2 s (49 frames) | about 4 min |
| `video`, 704×704, 5 s (121 frames) | about 6.5 min |
| `matte`, one image | about 12 s |
| `matte`, video | about 1 s per frame |
| `interpolate`, 49 frames to 97 | about 30 s |
| `upscale`, one image | about 5 s |
| `edit`, 1024×1024, 4 steps | about 6 min (70 s a step) |
| `keyframes`, 384×384, 17 frames, 4 steps | about 4.5 min (25 s a step) |
| `keyframes`, 512×512, 33 frames, 4 steps | about 14.5 min (95 s a step) |
| `keyframes`, 640×640, 81 frames (5 s), 4 steps | not run; estimated 35–45 min (about 11 s a step per 1,000 of its 34,000 latent tokens) |

The first job after a model change pays for loading it: a few seconds for the image model,
about a minute for video, one to three minutes for `edit` and `keyframes`.

Peak memory, as macOS counts ComfyUI's footprint: about 20 GB for `edit` and for `keyframes`
at 512×512×33. `keyframes` holds one 14B expert at a time; ComfyUI swaps the high-noise one out
for the low-noise one halfway. Close Unity before a long `keyframes` run.

## What to know before calling it

- **Video sizes.** Width and height are multiples of 32; frames are 4n+1 (49 is 2 s, 121 is
  5 s at 24 fps). Time grows faster than length, so ask for the loop, not the full 5 s.
- **Calm motion holds up; big motion does not.** A breathing idle stays on model. A sword
  swing morphs — the shield vanishes, a second sword appears. This is the small model's
  limit, not a setting.
- **Image-to-video drifts off the start image** over the first few frames — colours settle
  into the model's own reading of the character. Cut from where it settles.
- **`upscale` drops transparency.** Upscale first, matte second.
- **`upscale` on video holds every frame in memory at 4x.** Keep clips short or small.
- **`matte` on video returns a mask, not a cutout**, because mp4 carries no alpha.
- **`edit` and `keyframes` return opaque images.** A transparent PNG is laid on flat mid grey
  (`#808080`) before the model sees it, since its see-through pixels hold colour the model would
  draw. Re-matte the result.
- **`edit` keeps identity and drawing style well, and moves only what it is told to.** Say what
  must not change ("same eyes, same size and position"). The first image is the one edited and
  sets the output size; up to two more are references the instruction calls "picture 2", "picture 3".
  Pose edits land in the general direction asked; "left" is not always the left you meant.
- **`keyframes` sizes and lengths.** Width and height are multiples of 16; frames are 4n+1
  (81 is 5 s at the model's 16 fps). It opens on `--start` and lands on `--end`; the prompt
  describes the motion between. Cost grows a little faster than pixels × frames.

## Settings that are here for a reason

- `--fp32-vae`: at the default precision the video VAE fails on Apple's GPU and every frame
  comes out flat grey.
- `--gpu-only`: without it the text encoder and the matte model run on the CPU, about ten
  times slower.
- The 4-step LoRA and the small decoder are not optional extras. Plain Wan 2.2 on this
  machine takes 20 minutes for one second of video, 15 of them in the full decoder.
- `edit` resizes its images itself, at sizes Qwen's encoder then leaves alone. The encoder's own
  "area" resize only works on Apple's GPU by whole-number factors and fails on anything else.
- The Lightning LoRAs (4 steps instead of 40) are what make `edit` minutes rather than an hour.
  `edit --steps` above 8 drops the LoRA and runs the full model at cfg 4, about ten times slower.
- `LLMS_ARGS` replaces the server flags. `COMFY_DIR` (default `~/AI/ComfyUI`) and
  `LLMS_PORT` (default `8188`) move the install and the port; `LLMS_URL` points
  `generate.py` at a different server.
