# Demo Design

> **Status:** Built and being tuned. This is a demo project: the doc holds what is settled
> about the pipeline and the app, and nothing more.

## What This Is

A two-screen Flutter app — a showcase and a battle screen — that proves we can generate
character animations for our games in a consistent style, repeatably, with transparent
backgrounds, at a size a game can ship, and play them smoothly. The proof also includes
effects: a projectile, its impact, and the target's flinch, generated in each character's own
style and played between two squads on the battle screen. The app is the proof; the pipeline
that fills it is the deliverable.

Five requirements, and how each is met:

| Requirement | How |
|---|---|
| Plays in our Flutter game | Sprite sheets drawn with `drawImageRect` from a ticker, plain Flutter, no packages |
| Smooth | 16 frames per second, every second video frame kept, the flashing tail dropped, drawn once per frame change |
| Same style repeatedly | One style bible prompt, and every character after the first is generated with the first as a reference image |
| Reasonable size and playability | 256px cells, a 7x6 sheet of 38 frames per action, roughly 1–2 MB per action as PNG |
| Transparent backgrounds | The video is matted by a model built for stylized art, the outline is restored against the known flat background, and the alpha survives into the sheet |

## The Screens

On the Showcase, top half: the selected character, playing its idle loop. Bottom half: a
carousel of characters, five tiles visible at a time and scrollable sideways, then a row of
action buttons — one per action the character has, Attack, Defend and Hurt today. Tapping an
action plays it once, then the idle loop resumes. Tapping another action mid-play restarts
with the new one. Picking a character shows its idle at once. A tile shows the first frame
of that character's idle.

A segmented control in the app bar switches between Showcase and Battle, and both keep their
state. The battle arena is the top half: five circles per side in a staggered formation, the
right side mirrored so its characters face left. Characters are placed by long-pressing a
carousel tile and dragging it onto a circle; dropping on a filled circle replaces, tapping a
filled circle empties it. Under the carousel there is one button per placed character,
"Knight · Sword Wave", enabled once the other side has someone; with one enemy it fires at
once, with several the enemy circles light up and a tap picks the target. A cast plays the
attacker's attack, spawns the projectile at its front halfway through, flies it in a straight
line to the target's centre (rotated to the flight angle, mirrored when flying left, and spun
by code for the thrown weapons), then plays the burst on the target while the target plays
hurt; several casts can be in the air at once. A Fight button makes every placed character
with a skill attack a random enemy in turn.

The app reads `assets/characters/characters.json`: a list of characters, each with named
animations, each animation a sheet path plus its geometry (cell width and height, columns,
rows, frame count, fps, loop). `idle` is required; every other key becomes a button, in
the order written. Each character may also carry `skill`: a name, a `spin` flag, and two more
animations with the same geometry — `animation`, the looping projectile, and `impact`, the
one-shot burst, which the catalog plays at 32 fps so it reads as a hit. Frames are laid out
row-major and cells past the frame count are empty. Each character's folder is listed in
`pubspec.yaml` by hand, because Flutter does not bundle asset directories recursively.

## The Pipeline

The pipeline is the `animate-characters` skill (`.claude/skills/animate-characters/`); this
project is its first user and the place it was worked out. Everything this project decides —
the style bibles, the characters, their skills, the actions, the sheet geometry — is data
in `animate.yaml` beside `assetgen.yaml`. Every generated step is an Asset-Gen-Framework
manifest entry, run by name and recorded, so a character can be regenerated exactly and a
new one is a few lines of YAML. The skill's script writes the manifest one stage at a time
as inputs come into existence, because the framework refuses a manifest that names a file
that is not there.

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
   colour: the mask is grown three pixels and, in that band, each pixel is keyed by its
   colour distance from the flat background — that distance becomes its alpha and the
   background's share is subtracted from its colour, so the edge carries no background and
   no pale rim. The body is the model's; the edge is decided by colour, the same on every
   frame. The fit to 256px is premultiplied so transparent pixels cannot bleed into the
   edge. Every frame comes out as a 256px transparent PNG, centered.
6. **Sheet** — the framework's own `assemble_sheet`: the 38 kept frames into a 7x6 grid of
   256px cells, one PNG.

Per skill:

1. **Effect reference image** — the effect style bible plus the skill's own look, with the
   character's own reference as the init image and a prompt that says draw only this effect,
   no character.
2. **Animation video** — a looping video of the effect animating in place. The app supplies
   the travel, so the review fails a clip that drifts.
3. **Impact video** — a burst video from the same reference whose last-frame image is a flat
   background frame the skill writes locally, so the model is pulled to an empty frame, and
   whose review checks that it ends empty.
4. **Mask, frames and sheet** — as for an action, but the frames step runs the framework's
   effect matte: outside the mask body every pixel is keyed by colour with a narrow ramp
   around the threshold, because the mask model loses small shards, and inside it only exact
   background is dropped, because the model fills holes between dense shards. Characters
   never use it; their silver is too close to the grey.

A thrown weapon is not asked to spin — the model turns it slowly and off-centre — so it gets
a subtle in-place motion and the app spins it. `hurt` is an ordinary fourth action.

The skill's `approve.py` copies a character's finished sheets from the drafts area into
`assets/characters/<id>/`, adds the folder to `pubspec.yaml`, and rewrites
`characters.json`. Nothing reaches the app without that step, and the framework can never
write there itself.

### What the framework gained for this

Six small additions, each a gap this pipeline hit:

- `extract_frames` keeps the alpha of a source that has one. Before, every frame was
  flattened to RGB on the way out.
- `extract_frames` accepts `resize: [w, h]`, the one place the framework scales. A video
  model cannot be asked for game-sized frames, and `assemble_sheet` refuses a frame that
  is not exactly the declared cell size, so something had to fit one to the other.
- `extract_frames` accepts `matte:` — a mask video, a background colour (or `auto`, read
  from the corners of the clip's first frame and held, because a burst's later frames have
  shards in the corners), a grow radius, a colour threshold and an optional feather — and
  does the difference key and outline restoration described above locally, with no model
  call. Its resize is premultiplied.
- `mov` is a declared video format, told apart from `mp4` by the ftyp brand, for the case
  where a matte comes back as ProRes 4444 with alpha.
- An `input_files` value may be a list of references, uploaded in order and passed as a
  list. The image model takes its style references as a list, and one reference is how
  every character after the first stays in the first one's style.
- `matte:` also takes `effect: true`, which runs the effect matte described above.

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

The second batch — adding a skill, a burst and a hurt to all six — was 6 images, 18 videos
and 18 masks; three videos were regenerated (a hurt that read as a lunge, and two spinning
weapons that wandered before the spin moved into code); the app's sheets roughly doubled to
about 62 MB.

## Open Questions

- Is 256px per cell enough on a 3x phone, or should the sheets be 384px and larger?
- Should sheets be quantized (pngquant) to bring 1.8 MB per action down, and does the
  banding show?
- Should the idle loop be generated shorter than the actions, since it repeats?
