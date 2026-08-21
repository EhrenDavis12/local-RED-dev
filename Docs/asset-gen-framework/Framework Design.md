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

Every asset type has a default model on Replicate, and any manifest entry may name a
different one. The default is what an entry gets when it does not say; naming a model in
the entry overrides it. Model choice is per asset and therefore lives in the manifest,
never in the framework.

For images the model is `sourceful/riverflow-2.0-pro`. It emits PNG, which is the image
format of choice, and it supports transparent backgrounds for both text-to-image and
image-to-image editing. It accepts input images, and supports reference-based
super-resolution — detail fixing driven by a reference image. It offers more than ten
aspect ratios, including `auto`, and resolutions at 1K, 2K and 4K. The model's page does
not enumerate its output file formats beyond the transparency capability implying PNG.

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

Five kinds of asset: images, sound clips, music, animations, and videos.

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

Nothing in a calling project's app or its build ever runs it. No build, test or CI job
invokes it, and no shipped code imports it or shells out to it — a calling project builds
and ships on a machine that has never held a Replicate credential. The credential is read
from the environment, never from a committed file, a flag or a prompt, and never lands in
anything the tool writes.

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

- Which default model for sound clips, music, animations, and video? Images have one; the
  other four do not.
- What mechanism guarantees artistic consistency across a project's assets — reference
  images passed on every call, a model fine-tuned on already-approved assets, a fixed
  seed, or something else? Fine-tuning would mean the framework grows a second verb beyond
  generating.
- What does an animation actually produce as a file, and how is that different from a
  video? A Replicate model emits a video clip, but what a project can use may be a frame
  sequence, a sprite sheet, or something else.
- How is a seamless music loop achieved if the chosen model does not guarantee one? A
  crossfade or similar repair after generation would be post-processing the framework does
  not currently do.
- Is generating an asset ever more than one call — background removal, upscaling, or
  resizing to several densities are themselves Replicate models — and if so, does a
  manifest entry describe a chain of steps rather than a single call?
- Where do a calling project's sample images, base assets, and drafts area physically
  live, and how does the framework learn those paths?
- Are generated asset files committed to git by the calling project?
