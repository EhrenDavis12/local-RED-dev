# Demo Design

> **Status:** Built and being tuned. This is a demo project: the doc holds what is settled
> about the pipeline and the app, and nothing more.

## What This Is

A one-screen Flutter app that proves one thing: we can generate character animations for
our games in a consistent style, repeatably, with transparent backgrounds, at a size a game
can ship, and play them smoothly. The app is the proof; the pipeline that fills it is the
deliverable.

Five requirements, and how each is met:

| Requirement | How |
|---|---|
| Plays in our Flutter game | Sprite sheets drawn with `drawImageRect` from a ticker, plain Flutter, no packages |
| Smooth | 16 frames per second, every second video frame kept, drawn once per frame change |
| Same style repeatedly | One style bible prompt, and every character after the first is generated with the first as a reference image |
| Reasonable size and playability | 256px cells, a 7x6 sheet of 41 frames per action, roughly 1–2 MB per action as PNG |
| Transparent backgrounds | The video is matted by a model built for stylized art, and the alpha survives all the way into the sheet |

## The Screen

Top half: the selected character, playing its idle loop. Bottom half: a carousel of
characters, five tiles visible at a time and scrollable sideways, then a row of action
buttons — one per action the character has, Attack and Defend today. Tapping an action
plays it once, then the idle loop resumes. Tapping another action mid-play restarts with
the new one. Picking a character shows its idle at once. A tile shows the first frame of
that character's idle.

The app reads `assets/characters/characters.json`: a list of characters, each with named
animations, each animation a sheet path plus its geometry (cell width and height, columns,
rows, frame count, fps, loop). `idle` is required; every other key becomes a button, in
the order written. Frames are laid out row-major and cells past the frame count are
empty. Each character's folder is listed in `pubspec.yaml` by hand, because Flutter does
not bundle asset directories recursively.

## The Pipeline

Every step is an Asset-Gen-Framework manifest entry, run by name, recorded in the
per-asset record — so a character can be regenerated exactly, and a new character is data,
not a new script. `tool/pipeline.py` holds that data (the style bible, the characters, the
actions) and drives the framework; it exists because the framework checks every entry's
input files before doing anything, so a chain has to be written to the manifest one stage
at a time as its inputs come into existence. The script writes only entries whose inputs
exist, generates what has no draft, and repeats until the chain is complete.

Per character:

1. **Reference image** — `sourceful/riverflow-2.0-pro`, 1K, square, PNG. The prompt is the
   style bible plus that character's description. The first character is generated from
   text alone; every later one also gets the first character's image as an init image and
   is told to match its style and draw a different character. The background is a flat
   light gray, deliberately not transparent: it is only an input to the video model, and a
   flat background is what the matte removes cleanly.
2. **Action video** — `wan-video/wan-2.2-i2v-fast`, per action. Image-to-video from the
   reference, 81 frames at 16 fps, 480p. Wan will not make fewer than 81 frames, which
   is five seconds — about twice what a one-shot action wants — so the sheet keeps every
   second frame and the app plays those at 16 fps: the motion runs at twice the model's
   pace, which reads as snappy rather than as dropped frames. The same reference is
   passed as the last frame too, which is what makes an action return to its starting
   pose and an idle loop close. The prompt asks for a brisk action, a static camera, a
   centered character of unchanging size, and an unchanged flat background.
3. **Matte** — `sprited/birefnet-video` with the `toonout` variant (the stylized-art
   model), cutout output as a ProRes 4444 `.mov`, which carries alpha. This is a video
   matte rather than per-frame image matting so the edge does not flicker between frames.
4. **Frames** — the framework's own `extract_frames`, with `resize: [256, 256]`. Every
   frame comes out as a 256px transparent PNG, aspect preserved, centered.
5. **Sheet** — the framework's own `assemble_sheet`: the 41 kept frames into a 7x6 grid
   of 256px cells, one PNG.

`tool/approve.py <character>` copies a character's finished sheets from the drafts area
into `assets/characters/<id>/`, adds the folder to `pubspec.yaml`, and rewrites
`characters.json`. Nothing reaches the app without that step, and the framework can never
write there itself.

### What the framework gained for this

Three small additions, each a gap the video path hit:

- `extract_frames` keeps the alpha of a source that has one. Before, every frame was
  flattened to RGB on the way out, which made a matted video pointless.
- `extract_frames` accepts `resize: [w, h]`, the one place the framework scales. A video
  model cannot be asked for game-sized frames, and `assemble_sheet` refuses a frame that
  is not exactly the declared cell size, so something had to fit one to the other.
- `mov` is a declared video format, told apart from `mp4` by the ftyp brand, because
  ProRes 4444 in a QuickTime container is how alpha comes back from the matte.

## Open Questions

- Is 256px per cell enough on a 3x phone, or should the sheets be 384px and larger?
- Should the idle loop be generated shorter than the actions, since it repeats?
