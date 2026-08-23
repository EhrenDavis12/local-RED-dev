# Asset-Gen-Framework

> **Status:** In design. No code exists yet.

## What this is

A project-agnostic asset generation framework that calls Replicate. It lives directly
inside the `local-RED-dev` mono repo at `src/Asset-Gen-Framework` — not a separate
repository and not a submodule. It is a shared utility: other projects in the mono repo
call it to generate the assets they need.

It holds only the plumbing — the Replicate API calls, credential handling, reading the
prompt manifest, the drafts fence, the per-asset record, and checking that a downloaded
file's bytes match the format its entry declared. It holds nothing about any particular
asset: no prompt, no model choice, no filename, no knowledge of any calling project's
structure. That is what lets one framework serve projects with nothing in common.

### A CLI, driven by an agent

The framework is a CLI, and its only caller is an agent. It is not a library, and no
application code interacts with it at any point — not the calling project's app, not its
build, not its tests. What it exists to be is the layer that makes Replicate usable from a
terminal by an agent: the connection, the credentials, the call, the file that comes back.

Its command surface is designed for an agent to drive, which is a different audience from
a person at a prompt. That means predictable, parseable output, errors that say what
failed and what to change, and no interactive prompting — an agent cannot answer a
question mid-command.

The agent runs the generation; it does not author the request. What to generate stays the
calling project's, written by hand in the manifest — the prompt, the model, the inputs,
the filename. The agent's job is to execute a named entry and report what came back, never
to invent what the entry should have said.

### Called from another project's session

It is called from another project's session, and is not editable from there. Work happens
under one active project at a time. A project such as Tic-Tac-Toe-Extreme calls this
framework as a utility while that project is the active one; nothing in that session edits
the framework. Changing the framework means making the framework the active project.
Project scoping already enforces this — an agent working under another project resolves
that project's paths and never this one's source — so the separation is structural rather
than a rule anyone has to remember.

### Language

The framework is Python. It is shared across projects rather than being any one project's
script, so matching a caller's toolchain is not what matters — Python is on every machine
already, and it handles HTTP, the manifest, and the file checks cleanly.

### fey-tactics

fey-tactics is consulted for the API call and for nothing else. It is not part of this
project and is not reachable from it, and Replicate's HTTP API is publicly documented, so
the reference is a convenience rather than a dependency. Its system is not adopted; the
requirement is a clean framework that generates no junk.

## The prompt manifest

### One script, per-asset inputs are data

Adding an asset adds an entry to a list, never a second script. The script reads a
hand-written prompt manifest — one entry per asset — and generates whichever entry it is
asked for. Asking is by name: name the asset you want and the framework generates that
one. What varies per asset is data the calling project writes, not code in the framework.

The manifest is YAML, because it is hand-authored project data. The script reads it and
never writes it, and it invents nothing that belongs in it: prompts, formats, model ids
and inputs are the calling project's to write. A prompt an agent made up would be recorded
as provenance and read back later as a decision.

### Choosing a model

The framework supplies a default for every choice it can, and a calling project overrides
any of them, per entry, whenever it wants. A default is what an entry gets for saying
nothing, never something it is stuck with. Every asset type has a default model on
Replicate this way, and any manifest entry may name a different one. Model choice is per
asset and therefore lives in the manifest, never in the framework.

For images the model is `sourceful/riverflow-2.0-pro`. It emits PNG, which is the image
format of choice, and it supports transparent backgrounds for both text-to-image and
image-to-image editing. It accepts input images, and supports reference-based
super-resolution — detail fixing driven by a reference image. It offers more than ten
aspect ratios, including `auto`, and resolutions at 1K, 2K and 4K. The model's page does
not enumerate its output file formats beyond the transparency capability implying PNG.

Music is generated with `stability-ai/stable-audio-2.5`. It produces instrumentals and
sound effects up to roughly three minutes from a text prompt. It is chosen for a specific
capability rather than for fidelity or length: it supports audio inpainting and
continuation — given a clip, it fills a gap or extends the clip. That primitive is what a
seamless loop needs, and no other music model on Replicate offers it. Models with higher
fidelity or longer output exist and none of them can close a loop.

Every model has its own inputs, and the manifest carries them. Models do not share an
input shape: what one takes, another does not. The manifest entry carries whatever inputs
its model needs, and the framework passes them through rather than knowing what any of
them mean. This is what keeps a new model from being a code change.

### Sample images

Most models take sample images, and more is better. Sample and reference images are inputs
like any other and are named by the manifest entry. They are the calling project's files,
not the framework's — the framework reads the paths it is given and holds no opinion about
what a good sample is.

### Providing base assets to build from

A request may supply existing assets as the starting point for the one being generated,
rather than asking for something from nothing. Building a final asset out of base assets
that already exist is the preferred way to ask.

### Filenames

The calling project asks for a filename; the framework writes what it is told. Every
manifest entry carries the exact output filename, and the framework writes that name and
never invents one. How that name is arrived at is the calling project's business.

### Format checking

A format is declared per entry and checked against the bytes that arrive, so a file never
contradicts its own extension.

## What it generates

Five kinds of asset: images, sound clips, music, sprite sheets, and video.

### What the framework does not generate

Code-driven animation is out of scope, because it produces no asset. A transform applied
to art that already exists — growing a mark to double size and shrinking it back, a pulse,
a spin, a fade, a slide — is written in the calling project's code and generates no file,
so there is nothing for the framework to make. The framework's business is assets; motion
that is arithmetic over an existing asset belongs to whoever draws the frame.

A sprite sheet is what an animation becomes when the art itself has to change rather than
merely move — a jaw that opens, a mark that transforms into something else. No transform
produces new art, which is what makes a sprite sheet a generated asset and a
scale-and-settle not one.

### Sprite sheets

A sprite sheet is a sequence of frames, and every frame is PNG with alpha, like every
other image the framework produces. How many frames, what size, and how they are laid out
are per-entry data the calling project writes, like every other model input.

The two paths — the pixel-art model and the image-to-video-and-matte chain — are a choice
with a framework default, and an entry names the other path when it wants it. Which one is
the default is unsettled — see Open Questions.

Pixel art comes back as a finished sheet from a single call.
`retro-diffusion/rd-animation` returns a sprite sheet directly, with consistent framing
and frame counts sized for game engines, and it accepts input images, palette images,
background removal and seamless tiling. It is a pixel-art model, so it fits a theme drawn
in pixel art and nothing else.

Every other art style is a chain. An image-to-video model animates a reference image, the
subject is matted out of the video, and the frames become the sheet. Models that hold a
character consistent across frames from reference images include Veo 3.1, Seedance 2.0 —
which takes up to nine reference images — and Wan 2.7 R2V. Matting is its own step:
`arielreplicate/robust_video_matting` is built for video rather than stills and tracks the
subject across frames, which is what stops the edge flicker that matting each frame
independently produces.

Pulling a whole frame sequence out of a video is not a solved step.
`lucataco/frame-extractor` returns only the first or last frame of a video, so a full
sequence needs something else — and ffmpeg is an external binary this project does not
otherwise depend on.

How assembly is expressed for the chained path is unsettled — see Open Questions.

Frame-to-frame consistency is the hard part of a sprite sheet and is a sharper version of
the consistency requirement already stated under `### Artistic consistency`: frames that
do not match each other read as a flicker rather than a motion.

The framework assembles the frames and hands over one sheet. It does not deliver loose
numbered frames, and it does not animate anything. This project generates assets; playing
a sheet back — timing, sequencing, when an animation fires — belongs to the calling
application, which is not asset generation and not this framework's business.

No sidecar metadata travels with the sheet. How many frames, what size, and how they are
laid out are already declared by the calling project in its manifest entry, so it holds
the geometry before the sheet exists. A metadata file the framework wrote would be a
second copy of what the caller already wrote down.

A returned sheet is checked against the layout its entry declared, the same way a file's
bytes are checked against its declared format. A model that returns a different frame
count or framing than was asked for is a mismatch, not a result to accept — this matters
most on the pixel-art path, where the model does its own framing.

### Video

Video is generated, and no calling project consumes it yet. It is built because it is
wanted later — tutorials and similar material.

Video carries no usable transparency, which is why it is not how an in-game animation is
produced. Video codecs do not reliably carry an alpha channel, so a video cannot sit over
a game board the way a PNG can. That is the reason a sprite sheet, not a video, is the
animation asset.

### Artistic consistency

Artistic consistency is a requirement. Assets generated across a project have to look like
they belong together, and the framework needs a mechanism that makes that hold rather than
leaving it to how each prompt happens to be worded. Which mechanism is not settled — see
Open Questions.

### Looping

Some assets have to loop, and a loop has to be seamless: background music should loop with
no point a player can identify as the start or the end. Looping animations are likely
wanted too. Looping is a property an asset is asked for, not something the caller repairs
afterward.

## Drafts and approval

### An authoring tool, not a build step

No application interacts with it at all, in any direction. Its only invocation is an agent
running the CLI on a developer's machine — a calling project builds and ships on a machine
that has never held a Replicate credential. The credential is read from the environment,
never from a committed file, a flag or a prompt, and never lands in anything the tool
writes.

### Drafts, then approval

Nothing generated is applied directly. Generation is two stages. The framework writes into
a drafts area belonging to the calling project, and that is the only place it writes. It
is handed one path and can reach nowhere else. Approval is a person saying yes: there is
no score, no threshold and nothing automatic. Only then does the asset move into the place
it ships from.

The fence is structural rather than a rule the tool has to remember. Approved assets do
not live anywhere the framework can write, so a rerun cannot clobber one — the guarantee
holds even if the tool is wrong about everything else.

## The record

### The per-asset record

One record per asset, holding the last generation only. Not a history and not an
append-only log — regenerating an asset replaces that asset's entry rather than adding to
it. An entry holds the pinned model version, the prompt, the seed and the inputs that
produced the asset. The model version is always pinned, never a bare model name, which is
the whole reason the record is worth keeping. What the record is for is knowing what was
last asked for, so the next request is a change from it rather than a fresh invention.

It is contained and trashable: one file the framework owns, written nowhere else and never
into any other document. Deleting it costs the ability to tweak from the last request, and
nothing else.

### Regenerating, and leaving nothing behind

A run leaves the drafted assets and one record, and nothing else — no temp files, no
scratch scripts, no response dumps, no half-written asset. A run that dies partway leaves
the tree as it was rather than leaving a truncated file behind.

Regenerating is deliberate and one named asset at a time. There is no bulk regenerate,
because a single command that redoes everything is how generation gets out of control; and
an existing draft is replaced only when the rerun says so explicitly.

## Open Questions

- Which default model for sound clips, sprite sheet frames, and video? Images and music
  have one; the other three do not.
- What mechanism guarantees artistic consistency across a project's assets — reference
  images passed on every call, a model fine-tuned on already-approved assets, a fixed
  seed, or something else? Fine-tuning would mean the framework grows a second verb beyond
  generating.
- Which of the two paths — the pixel-art model or the image-to-video-and-matte chain — is
  the sprite-sheet framework default?
- What format and codec does generated video use, given that transparency is not
  available?
- Is a seamless music loop closed by inpainting across the wrap-around seam — joining the
  track's end to its start and filling the join — and does that make a looping music entry
  a chain rather than a single call?
- How does a manifest entry express a chain of steps, given that some entries are a single
  call and others are not?
- How is the CLI told where a calling project's manifest, sample images, base assets,
  drafts area and record live — flags on the command, a config file in the calling
  project, or a convention?
- Are generated asset files committed to git by the calling project?
- What is the CLI's command surface — which commands exist, what they take, and what they
  print for an agent to read?

