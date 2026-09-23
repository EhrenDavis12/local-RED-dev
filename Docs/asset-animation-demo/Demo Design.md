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
| Smooth | 16 frames per second, every second video frame kept, the flashing tail dropped, drawn once per frame change |
| Same style repeatedly | One style bible prompt, and every character after the first is generated with the first as a reference image |
| Reasonable size and playability | 256px cells, a 7x6 sheet of 38 frames per action, roughly 1–2 MB per action as PNG |
| Transparent backgrounds | The video is matted by a model built for stylized art, the outline is restored against the known flat background, and the alpha survives into the sheet |

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

The pipeline is the `animate-characters` skill (`.claude/skills/animate-characters/`); this
project is its first user and the place it was worked out. Everything this project decides —
the style bible, the characters, the actions, the sheet geometry — is data in `animate.yaml`
beside `assetgen.yaml`. Every generated step is an Asset-Gen-Framework manifest entry, run by
name and recorded, so a character can be regenerated exactly and a new one is a few lines of
YAML. The skill's script writes the manifest one stage at a time as inputs come into
existence, because the framework refuses a manifest that names a file that is not there.

Per character:

1. **Reference image** — `sourceful/riverflow-2.0-pro`, 1K, square, PNG. The prompt is the
   style bible plus that character's description. The first character is generated from
   text alone; every later one also gets the first character's image as an init image and
   is told to match its style and draw a different character. The background is a flat
   light gray, deliberately not transparent: it is only an input to the video model, and a
   flat known background is what the matte and the outline restoration depend on.
2. **Action video** — `wan-video/wan-2.2-i2v-fast`, per action. Image-to-video from the
   reference, 81 frames at 16 fps, 480p. Wan will not make fewer than 81 frames, which is
   five seconds — about twice what a one-shot action wants — so the sheet keeps every
   second frame and the app plays those at 16 fps: the motion runs at twice the model's
   pace, which reads as snappy rather than as dropped frames. The same reference is
   passed as the last frame too, which is what makes an action return to its starting
   pose and an idle loop close. The prompt asks for a brisk action, a static camera, a
   centered character of unchanging size, and an unchanged flat background.
3. **Review** — the skill measures the raw video before anything else is spent on it: a
   brightness step at the end of the kept range or a background that stops being flat
   fails the video and blocks its chain; mid-clip spikes, loop gap and drift are warnings
   with a contact sheet to look at. The last six frames of every video are dropped before
   anything uses them, because the model blends toward its last-frame image there and the
   character brightens — that was the flash seen at the end of every action.
4. **Mask** — `sprited/birefnet-video` with the `toonout` variant (the stylized-art model),
   as a grayscale alpha video. A video matte rather than per-frame image matting, so the
   edge does not flicker between frames.
5. **Frames** — the framework's own `extract_frames` with `matte:` and `resize: [256, 256]`.
   The alpha comes from the mask, and the outline the matte shaved off is restored by
   colour: the mask is grown three pixels and, in that band, only pixels clearly unlike the
   flat background are kept. The body is the model's; the edge is decided by colour, the
   same on every frame. Every frame comes out as a 256px transparent PNG, centered.
6. **Sheet** — the framework's own `assemble_sheet`: the 38 kept frames into a 7x6 grid of
   256px cells, one PNG.

The skill's `approve.py` copies a character's finished sheets from the drafts area into
`assets/characters/<id>/`, adds the folder to `pubspec.yaml`, and rewrites
`characters.json`. Nothing reaches the app without that step, and the framework can never
write there itself.

### What the framework gained for this

Five small additions, each a gap this pipeline hit:

- `extract_frames` keeps the alpha of a source that has one. Before, every frame was
  flattened to RGB on the way out.
- `extract_frames` accepts `resize: [w, h]`, the one place the framework scales. A video
  model cannot be asked for game-sized frames, and `assemble_sheet` refuses a frame that
  is not exactly the declared cell size, so something had to fit one to the other.
- `extract_frames` accepts `matte:` — a mask video, a background colour (or `auto`, read
  from the corners), a grow radius, a colour threshold and a feather — and does the
  outline restoration described above locally, with no model call.
- `mov` is a declared video format, told apart from `mp4` by the ftyp brand, for the case
  where a matte comes back as ProRes 4444 with alpha.
- An `input_files` value may be a list of references, uploaded in order and passed as a
  list. The image model takes its style references as a list, and one reference is how
  every character after the first stays in the first one's style.

Community models on Replicate are named with a pinned version (`owner/name:hash`), which
the framework already routes to the generic predictions endpoint; the matte model is one.

## What Six Characters Cost

Six characters, three actions each, came to 78 framework entries and about 33 MB of PNG
in the app — roughly 1.8 MB per sheet. Every video came back usable on the first try;
none was regenerated. Two defects were found on the finished sheets and fixed in the
pipeline rather than by regenerating: the end-of-clip flash (now trimmed and gated by the
review) and a flickering outline (now restored by colour). The one artifact that stays is
the mage's defend, where a translucent magic barrier matted as an opaque white disc for a
few frames: a matte cannot carry a half-transparent effect, so effects that should be
see-through belong in code or in a separate layer, not in the character's video.

## Open Questions

- Is 256px per cell enough on a 3x phone, or should the sheets be 384px and larger?
- Should sheets be quantized (pngquant) to bring 1.8 MB per action down, and does the
  banding show?
- Should the idle loop be generated shorter than the actions, since it repeats?
