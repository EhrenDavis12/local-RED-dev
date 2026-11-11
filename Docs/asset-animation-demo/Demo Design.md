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
| Smooth | 16 frames per second, every video frame kept so motion plays at the speed it was made, the flashing tail dropped, drawn once per frame change |
| Same style repeatedly | One style bible prompt, and every character after the first is generated with the first as a reference image |
| Reasonable size and playability | 512px cells, a per-action grid — 75 frames for a loop, fewer for a one-shot that is cut a beat after it settles — roughly 6–10 MB per action as PNG (characters built before the upscale stage are still 256px, 1–2 MB, until regenerated) |
| Transparent backgrounds | The video is matted by a model built for stylized art, the outline is restored against the known flat background, and the alpha survives into the sheet |

## The Screens

On the Showcase, top half: the selected character, playing its idle loop. Bottom half: a
carousel of characters, five tiles visible at a time and scrollable sideways, then a row of
action buttons — one per action the character has, Attack, Defend and Hurt today. Tapping an
action plays it once, then the idle loop resumes. Tapping another action mid-play restarts
with the new one. Picking a character shows its idle at once. A tile shows the first frame
of that character's idle.

A segmented control in the app bar switches between Showcase and Battle, and both keep their
state. The battle arena is the top half: a side-on battlefield on a perspective floor — a
horizon about a third of the way down, a grid converging toward it — and both squads stand
near the middle facing each other, five a side: a back row of three standing higher and drawn
smaller, a front row of two lower and larger, the right squad mirrored so it faces left. Each
position is an elliptical pad on the floor; a placed fighter stands on its pad with its name
above it, and the pad lights up for the attacker choosing a target and for the enemies it may
pick. The pad and the fighter's feet are the drop and tap area, so a front-row fighter never
takes a tap meant for the one behind. The button band under the carousel has a fixed height,
so the arena never moves when buttons appear; in landscape the carousel tiles shrink so the
arena keeps at least half the screen. Characters are placed by long-pressing a carousel tile
and dragging it onto a pad; dropping on a filled pad replaces, tapping a filled pad empties
it. Under the carousel there is one button per placed character, "Knight · Sword Wave",
enabled once the other side has someone; with one enemy it fires at once, with several the
enemy pads light up and a tap picks the target. A cast plays the attacker's attack, spawns the
projectile at its front halfway through, flies it in a straight line to the target's centre
(rotated to the flight angle, mirrored when flying left, and spun by code for the thrown
weapons), then plays the burst on the target while the target plays hurt — the burst is drawn
larger than the fighter and fades out radially at its edge, so a sheet cell's square edge can
never show; several casts can be in the air at once. A Fight button makes every placed
character with a skill attack a random enemy in turn.

The app reads `assets/characters/characters.json`: a list of characters, each with named
animations, each animation a sheet path plus its geometry (cell width and height, columns,
rows, frame count, fps, loop). `idle` is required; every other key except a `fidget_` key
becomes a button, in the order written. Each character may also carry `skill`: a name, a
`spin` flag, and two more animations with the same geometry — `animation`, the looping
projectile, and `impact`, the one-shot burst, which the catalog plays at 32 fps so it reads
as a hit. Frames are laid out row-major and cells past the frame count are empty. Each
character's folder is listed in `pubspec.yaml` by hand, because Flutter does not bundle
asset directories recursively.

## The Idle

The idle is mostly stillness. A character at rest breathes and does little else, and an idle
that moves more than that reads as a puppet on a string rather than someone standing there.
It is two pieces:

- **A base loop**, played forever: breathing and nothing else. The chest and shoulders rise
  and fall by a few percent of the character's height, the feet stay planted and the hips
  nearly still, and the parts follow one another instead of moving as one block — the chest
  leads, the shoulders follow a beat later, the head after that, and loose things like a
  plume, a cape or hair trail last. Rigid armour barely moves. The breath is uneven: in is
  quicker than out, with a short pause at the top and bottom. Nothing in the loop is big
  enough to notice it repeating.
- **Fidgets** — short one-shots that start and end on the rest pose: a glance back over the
  shoulder, a re-grip of the weapon, a blink. The player picks one at random every 5 to 15
  seconds, never the same one twice running, plays it, and returns to the base loop. Playing
  an action resets that timer. The blink is a fidget rather than part of the base loop,
  because a blink on a fixed five-second cycle is exactly what gives a loop away.

In a crowd nobody idles in step: every fighter starts its base loop at its own random frame,
and head turns and weight shifts are peppered in at random times per fighter — two or three
each over a 36-second stretch, many at once is fine, never in sync — so the army never looks
uniform.

The base loop's prompt asks for a character standing nearly motionless with only the breath
visible, and never asks the knees to bend with the breath: nobody breathes with their knees,
and it turns the whole body into a bob. Fidgets keep the end frame pinned like every
one-shot, which is what brings them back to the rest pose. The player also carries an idle
playback speed, so how slow the loop should run is tuned by looking at it rather than by
re-rolling it.

An action whose key starts with `fidget_` is an idle variation, in `animate.yaml` and in the
catalog alike: it never becomes a button, and only the idle player plays it.

## The Pipeline

The pipeline is the `animate-characters` skill (`.claude/skills/AnimationSkills/animate-characters/`);
this project is its first user and the place it was worked out. Everything this project
decides — the style bibles, the characters, their skills, the actions, the sheet geometry
— is data in `animate.yaml` beside `assetgen.yaml`. Every generated step is an
Asset-Gen-Framework manifest entry, run by name and recorded, so a character can be
regenerated exactly and a new one is a few lines of YAML. The skill's script writes the
manifest one stage at a time as inputs come into existence, because the framework refuses
a manifest that names a file that is not there.

Per character:

1. **Reference image** — `sourceful/riverflow-2.0-pro`, 1K, square, PNG. The prompt is the
   style bible plus that character's description. The first character is generated from
   text alone; every later one also gets the first character's image as an init image and
   is told to match its style and draw a different character. The background is a flat
   light gray, deliberately not transparent: it is only an input to the video model, and a
   flat known background is what the matte and the outline restoration depend on. The image
   model still draws a soft ground shadow under the feet often enough to matter, so before
   anything is built from a reference its background is flattened locally: every pixel
   reachable from the corners within a colour tolerance becomes the exact corner colour. A
   shadow is contiguous with the background and goes; the character is sealed off by its own
   outline and stays. The same is done to the effect reference.
2. **Action video** — `wan-video/wan-2.2-i2v-fast`, per action. Image-to-video from the
   reference, 81 frames at 16 fps, 720p (a square clip comes back 960px). Wan will not
   make fewer than 81 frames, which is five seconds. Every frame is kept and played at
   16 fps, so an idle loop runs the full five seconds at real speed, and a one-shot
   action is cut four frames after the last frame that still moves (the review measures
   where the character has settled), so its return-to-pose hold does not pad the sheet.
   The same reference is passed as the last frame too, which is what makes an action
   return to its starting pose and an idle loop close. The prompt asks for a brisk
   action, a static camera, a centered character of unchanging size, an unchanged
   flat background, and a calm, steady face with the mouth closed, because the video
   model otherwise animates the mouth on its own and at speed that reads as talking.
3. **Review** — the skill measures the raw video before anything else is spent on it: a
   brightness step at the end of the kept range or a background that stops being flat
   fails the video and blocks its chain; mid-clip spikes, loop gap and drift are warnings
   with a contact sheet to look at. The last six frames of every video are dropped before
   anything uses them, because the model blends toward its last-frame image there and the
   character brightens — that was the flash seen at the end of every action.
4. **Upscale** — `lucataco/real-esrgan-video` with the `RealESRGAN_x4plus_anime_6B` model
   at its `2k` setting, which returns a square clip at 2560px with the same 81 frames and
   16 fps. The video model's 720p output through a lossy codec has a soft outline, and a
   256px cell cut from it is soft again once a game scales the sprite up; the anime-tuned
   super-resolution redraws the clip as hard line art, so the fit to the cell below is a
   downscale and the edge comes out as antialiased line art. It runs after the review so a
   failed roll is never upscaled, and its input is sent inline as a data URI because this
   model fails on Replicate's file-endpoint URLs. Everything after this step reads the
   upscaled clip.
5. **Mask** — `sprited/birefnet-video` with the `toonout` variant (the stylized-art model),
   as a grayscale alpha video. A video matte rather than per-frame image matting, so the
   edge does not flicker between frames.
6. **Frames** — the framework's own `extract_frames` with `matte:` and `resize: [512, 512]`.
   The alpha comes from the mask, and the outline the matte shaved off is restored by
   colour: the mask is shrunk three pixels (the model's body edge lands in the background
   blend just outside the outline) and then grown twelve (three, at the 624px the number
   was first tuned at), and in that band each pixel is keyed by its colour distance from
   the flat background — that distance becomes its alpha, and a partially covered pixel
   takes the colour of the nearest body pixel rather than an un-blend of its own, because
   un-blending a low-alpha pixel amplifies codec noise into a pale rim. The body is the
   model's; the edge is decided by colour, the same on every frame. The fit to 512px, a
   downscale from 2560px, is premultiplied so transparent pixels cannot bleed into the
   edge. Every frame comes out as a 512px transparent PNG, centered.
7. **Sheet** — the framework's own `assemble_sheet`: the kept frames into a grid as square
   as the count allows — 9x9 for a 75-frame loop (4608px, so a game engine must allow an
   8192 source texture or it downsamples the sheet on import), one PNG.

Per skill:

1. **Effect reference image** — the effect style bible plus the skill's own look, with the
   character's own reference as the init image and a prompt that says draw only this effect,
   no character.
2. **Animation video** — a looping video of the effect animating in place. The app supplies
   the travel, so the review fails a clip that drifts.
3. **Impact video** — a burst video from `skill_small.png`, the effect reference shrunk to
   42% on its own background (written locally like the blank frame), because a burst that
   starts from an effect filling two thirds of the frame has nowhere to expand and gets cut
   off by the cell; the prompt keeps the burst within the middle two thirds. Its last-frame
   image is a flat background frame the skill writes locally, so the model is pulled to an
   empty frame, and the review's `--contained` gate fails any frame whose border is more than
   2% solid foreground after a two-pixel erosion — a cut shard, not the spray of dots every
   burst throws.
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
- A manifest entry may set `inline_inputs: true` to send its input files as data URIs
  instead of uploading them to Replicate's file endpoint, for models that fail on those
  URLs.
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
and 18 masks; three videos regenerated for motion (a hurt that read as a lunge, and two
spinning weapons that wandered before the spin moved into code), and all six bursts
regenerated once more so they stay inside their cells; the app's sheets roughly doubled to
about 62 MB.

## The Game in Unity

What the demo proved now goes into the Unity side-scroller (`src/unity-side-scroler`).
Battle scenes, their intro, scenery motion and hit effects are built and recorded there, in
annie's sandbox, and the Flutter app stays the demo.

### Actions

- An action snaps from the idle straight into the already-wound-up pose, with no
  anticipation in between, then plays the action and its follow-through. The anticipation is
  what makes an action feel slow, so it is cut.
- An action ends on the spot it started. A push-back is fine, but the character is back home
  by the last frame, and the knock-back stays small so the return is short and stepped, never
  slid.
- A character's own animation holds only that character and their weapon: no other
  character in any frame and no blood. Enemies come from the game, and blood is a separate
  effect.
- A death or a hurt is played by the video model in one go from the character's look — same
  character, same side-on angle — rather than built from drawn keys, and a take is judged on
  how epic it looks over how controlled it is.
- A new enemy starts from five designs to choose from, each shown relaxed and at the ready,
  and its animations wait until the user picks one. They use the Archer and Assassin method. An enemy needs no attack wind-up, jumping
  right to the strike, and no run, run start, run stop or death animation.
- Every character and enemy keeps to one roster style: the same height, heads per figure
  and outline width, and colours kept within shared colour families picked from the Archer,
  so a new character never drifts to a look of its own.
- The party's main characters are the Archer, the Assassin, the Tank, the Brute, the Fighter
  and the Mage. The Tank gets a new weapon. The Porter, the Scout, the Blacksmith and the
  Alchemist are back-line utility members who barely fight but still get every animation the
  others have. The Cleric is an extra. Enemies are chibi but drawn as monsters, not humanized
  monsters: goblin, spider, skeleton and the dragon boss among them.
- A character with no death animation made for them holds their hurt pose and disintegrates
  into particles that fade, a reusable Unity sequence, so enemies need no death sheets.
- The Assassin is a melee character. Before his attack he closes the distance to the Archer
  with a single dash or jump moved by code, with no separate animation for it, and the attack
  animation plays once he arrives: "a single jump is fine by me where we just move it through
  code and not having to do another animation."

### Battle Scene 1

The backdrop is parallax layers of separate cut-outs, never one continuous strip: a bold sky
with separate bold clouds on three drift layers; separate mountains, a front range and a paler
back range, flat two-tone; hills; trees in the T-B style, some planted on the terrain at the
ground's speed so they blend into it; the ground as a texture only (sandy soil with fine
stones, no grass edge); and S-B bushes, with rocks, grass and ground patches moving with the
terrain. Each side fields three columns by five rows, the enemy side mirrored, back rows
smaller; the spacing grows as the figures shrink, so every column stays a straight line from
front to back.

The close trees, grass and bushes sway in the wind, moved by a grey pattern layer that pushes
pixels sideways only — tree tops lean about 16 px, bases stay planted. The strong sway is the
one used; a gentler one is barely noticeable. The ground varies by a mask blend: grass and soil
as two layers mixed by a third, invisible grey pattern, and different patterns chained one
after another, each starting and ending all white, so no join or repeat shows. A grey pattern
never moves a character — it was tried as a still character's breath and did not work.

The battle opens fast, on an empty battlefield, and nobody just appears on screen. Over about
4 s the camera scrolls with parallax, the player's side runs in at run pace, each runner coming
on at a random moment so they do not arrive in lines, and the enemies
scroll in from off screen right as if approached; they stop raggedly and the background eases
to a stop. A gamer wants to get to the action, so the intro stays short.

Health and mana show as a thin vertical bar at each character's side, red over blue, about
15 px out from the character and drawn on top of every character whatever the stack. A unit
at full health shows no bar. The bar stays still and does not follow the body; it moves only
on a hit or an attack, when it nudges out of the way and then comes back. The body gets no
glow or rim, and where a bar sits on the quiver of the archer in front, it is left that way.
The user picked this set: "1,5,11 thesee are what we want to go with for the Health bar
system."

The second scene is a cave: a small enclosed tunnel, its near wall moving almost at floor
speed with no far distance, a solid rock ceiling with stalactites here and there, and veins of
ore in the rock.

### Effects

A hit effect is many stacked layers, each one toggleable: a one-frame flash, a drawn core,
particles out the front of the hit and out the back of the target, a trail, lingering bits and
light, using drawn particle sprites. An arrow's trail is a thin faint streak, so it reads as
an arrow and not a missile. The full stack suits a dramatic hit; a plain arrow hit may be
toned down later.

Floating combat text pops up over the fighters: a red damage number on each hit, a green
number on a heal, and the words Miss and Blocked. It uses a chubby chibi-style font that matches the characters, at half the size first tried
so a full field stays readable. Each one pops in with a scale-in, drifts in a random upward
direction, tilts slightly and fades out.

### Sound

The battle music is medieval, Celtic background music, not happy or cheerful: "we're looking
for Celtic background music." It sits low, with no high, ear-piercing sounds, and leans
toward a low sea shanty. The music stays Celtic and sea shanty and never sounds Arabian or
Middle-Eastern: traditional Celtic instruments, a traditional Celtic scale with no awkward
flat notes from an Arabian scale, and the sea-shanty crew chanting voices. The strings stay a
violin and never turn into a fiddle. Battle music is intense; menu music is light-hearted on the same
themes. A victory song and a defeat song are real songs in the same Celtic / sea-shanty
style, kept low too. The songs are long and need no perfect loop: at the end the volume
fades out and comes back up as the song starts again. Arrow sounds come in four sets — release when the bow fires,
hit when the arrow strikes a body, miss when it flies past or lands in the ground, and blocked
when it knocks on a shield or weapon — and each shot picks one at random from its set, pitch
and level varied a little, so a crowd of archers firing together never repeats one sound.
The variety is what the user liked: "I love the variety in the arrow shots."

Menu sounds come in two pools, and each button or menu names the pool it pulls from: clicks,
and paper, which is the paper rustle and the scroll unrolling and rolling back up. Gold has
one bucket of coin sounds, used for gaining gold and for a purchase. Characters have voices — hurt grunts and
battle cries, male and female. Hurt grunts are the five shortest of each voice: "the longer one don't sound
right." Every sound set is sorted into labelled buckets the game picks from at random; which bucket plays
for which action is chosen later by the user.

### Menus

The main menu is one fixed screen: an inked map on old parchment, seen from above at an angle,
where each building is a button to a part of the game — the player's home, the Arena, the
cave entrance, the Guild Hall and an Armory — with no labels on the map. Every menu, pop-up
and button, in Unity too, uses the "R04 One Rod" scroll: paper rolled on one rod, not circles
at the ends. Item icons are painted (code shapes with a local painted pass), not drawn by code
alone, in the "Scorched Edge" style: soft oil paint with a warm glowing centre ("IO3 the
scorched Edge is the way to go here"). A pop-up's close button is a red ink X of hard
slashes in the same painted scroll style, set on a tan button, or given a darker edge where it
sits on a red one so it does not vanish.

A menu or pop-up opens by the scroll unrolling and closes by it rolling back up, done by code:
the rod rolls across while the writing stays still, 0.8 s each way, and closing is the opening
played backward.

All text in the game uses one font, "Steady Manuscript": Eagle Lake, an open-licence font,
with an ink treatment that looks written by a quill. Damage text over the fighters is the one
exception and stays chibi.

The victory and loss screens are pop-ups on the One Rod scroll, which unrolls open, with VICTORY
and DEFEAT in the game's quill-and-ink font. Victory is a tall scroll with the loot written
as a list of icon, name and amount above the buttons, with Exit as the red one. Defeat is
plain brown ink on the same paper with Retry as the red one, and a loss gives no loot. Button
labels are lettered in the same font. Gold and crystal are the two currencies, each with its own icon: a gold coin with a star and
a violet cut gem, for now.

## Open Questions

- Is 256px per cell enough on a 3x phone, or should the sheets be 384px and larger?
- Should sheets be quantized (pngquant) to bring 1.8 MB per action down, and does the
  banding show?
- Should the idle loop be generated shorter than the actions, since it repeats?
