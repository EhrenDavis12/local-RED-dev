# Asset-Gen-Framework

> **Status:** Version one is built.

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

The CLI learns a calling project's paths — its manifest, sample and base assets, drafts
area and record — from a config file in the calling project. The caller is an agent, and a
config file gives it fewer things to get wrong per invocation than flags repeated on every
command, while keeping paths as per-project data like everything else the calling project
writes. It looks for that file in one place and never searches parent directories: an
upward search makes the same command mean different things depending on where it was run
from, and an agent cannot see that it happened.

The CLI exposes four things, derived from what an agent needs to do its job: discover
what entries a manifest holds; generate one named entry; read what an entry was last
asked for, from the record; and regenerate one named entry, replacing what is there.

Every command writes exactly one machine-readable document, on success and failure alike,
written once at the end of the run rather than a piece at a time — so no partial result is
ever already out when something goes wrong, and an unexpected failure is reported in the
same shape as an expected one. Diagnostics are separate and are never needed to read a
result. A failure says what failed and what to change. The exact flags and output shapes
are the code's and its tests', not this doc's.

### Called from another project's session

It is called from another project's session, and is not editable from there. Work happens
under one active project at a time. A project such as Tic-Tac-Toe-Extreme calls this
framework as a utility while that project is the active one; nothing in that session edits
the framework. Changing the framework means making the framework the active project.
Project scoping already enforces this — an agent working under another project resolves
that project's paths and never this one's source — so the separation is structural
rather than a rule anyone has to remember.

### Language

The framework is Python. It is shared across projects rather than being any one project's
script, so matching a caller's toolchain is not what matters — Python is on every
machine already, and it handles HTTP, the manifest, and the file checks cleanly.

### One path to Replicate, one path into a video

Every call to Replicate goes through a single point and nothing else speaks to it.
Decoding a video is the same, one point, no other code path opens a video. Both are
substitutable — a stand-in works with no network, no credential and no video file,
everything else about the run staying real.

This is a requirement rather than taste, for two reasons. A test suite can guarantee no
test reaches the network or spends money only if there is one place to replace, and the
first anyone hears of a third call site is an invoice. And a whole generation can be
exercised for real — manifest checks, lock, sweep, staging, every check, commit, record
write — with only the remote call standing in, without which the path that commits a whole
set of files has no coverage and an implementation copying frames into place one at a time
would satisfy everything else while breaking the all-or-nothing guarantee.

Only the conversation itself sits behind each point: choosing the model, resolving
references, assembling inputs, checking returned bytes, committing and recording stay in
front. Which library decodes a video is not settled by this.

The framework imposes no time limit on a generation and no cap on how long it waits,
because generation times differ between models by orders of magnitude so any default would
cancel real work, and a caller wanting a limit imposes it — but it does not wait on a
response it cannot read, since a reply whose status it does not recognise fails
immediately rather than being polled again, and a cap on attempts is a timeout on
legitimate work wearing different clothes.

### fey-tactics

fey-tactics is consulted for the API call and for nothing else. It is not part of this
project and is not reachable from it, and Replicate's HTTP API is publicly documented, so
the reference is a convenience rather than a dependency. Its system is not adopted; the
requirement is a clean framework that generates no junk.

## The prompt manifest

### One script, per-asset inputs are data

Adding an asset adds an entry to a list, never a second script. The script reads a
hand-written prompt manifest — one entry per asset — and generates whichever entry it
is asked for. Asking is by name: name the asset you want and the framework generates that
one. What varies per asset is data the calling project writes, not code in the framework.

The manifest is YAML, because it is hand-authored project data. The script reads it and
never writes it, and it invents nothing that belongs in it: prompts, formats, model ids
and inputs are the calling project's to write. A prompt an agent made up would be recorded
as provenance and read back later as a decision.

### One entry is one step

An entry is exactly one step, and the framework holds no notion of a multi-step asset.
Almost every step is a single call to a model on Replicate; two of them — assembling
frames into a sprite sheet and extracting frames from a video — are local work the
framework does itself, with no call to Replicate at all. Either way, an entry never
chains several steps together: a list of assets to generate is a list of steps, one per
entry, and that is the whole model.

An asset that takes several steps is several entries, each naming the previous entry's
output file as one of its inputs. That works because an entry may already start from
assets that exist — see `### Providing base assets to build from` — and because every
entry declares the exact filename it writes, so the file an earlier entry produced is a
file a later entry can name.

The order is the order the calling project runs them in. Nothing in the framework
sequences entries, resolves dependencies between them, or knows that one entry's input
came from another. This is what keeps a sprite sheet's several steps from turning into
machinery: the caller writes the entries and runs them, and each one is the same single
step as a plain image.

Rerunning an early step does not cascade. A later entry is rerun deliberately, by name,
like any other — which is the same rule as everywhere else in the framework.

### Choosing a model

The framework supplies a default for every choice it can, and a calling project overrides
any of them, per entry, whenever it wants. A default is what an entry gets for saying
nothing, never something it is stuck with. Images and music have a default model on
Replicate this way; sound clips, sprite sheet frames and video do not, and their manifest
entries name the model themselves. Any manifest entry may name a model different from its
default, where one exists. Model choice is per asset and therefore lives in the manifest,
never in the framework.

For images the model is `sourceful/riverflow-2.0-pro`. It emits PNG, which is the image
format of choice, and it supports transparent backgrounds for both text-to-image and
image-to-image editing. It accepts input images, and supports reference-based
super-resolution — detail fixing driven by a reference image. It offers more than ten
aspect ratios, including `auto`, and resolutions at 1K, 2K and 4K. The model's page does
not enumerate its output file formats beyond the transparency capability implying PNG.

Music is generated with `stability-ai/stable-audio-2.5`. It produces instrumentals and
sound effects up to roughly three minutes from a text prompt. It is chosen for a specific
capability rather than for fidelity or length: it supports audio inpainting and
continuation — given a clip, it fills a gap or extends the clip. That primitive is what
a seamless loop needs, and no other music model on Replicate offers it. Models with higher
fidelity or longer output exist and none of them can close a loop.

Every model has its own inputs, and the manifest carries them. Models do not share an
input shape: what one takes, another does not. The manifest entry carries whatever inputs
its model needs, and the framework passes them through rather than knowing what any of
them mean. This is what keeps a new model from being a code change.

### Sample images

Most models take sample images, and more is better. Sample and reference images are inputs
like any other and are named by the manifest entry. They are the calling project's files,
not the framework's — the framework reads the paths it is given and holds no opinion
about what a good sample is.

### How a referenced file reaches the model

The framework uploads a referenced file to Replicate and passes the returned URL as the
model's input. It does not inline the file as a data URI and does not pass a local path. A
data URI carries a size limit, and passing reference images is version one's entire
mechanism for artistic consistency, so the encoding has to work at the sizes real
reference art comes in, not just small ones.

### Providing base assets to build from

A request may supply existing assets as the starting point for the one being generated,
rather than asking for something from nothing. Building a final asset out of base assets
that already exist is the preferred way to ask.

### Filenames

The calling project asks for a filename; the framework writes what it is told. Every
manifest entry carries the exact output filename, and the framework writes that name and
never invents one. How that name is arrived at is the calling project's business.

A step returning more than one file for an entry that declared one filename is a failure,
not a choice: the framework never selects among returned files and never names the extras.
More than one file coming back means the entry asked for something other than what it
declared.

### An entry that writes many files owns its directory

An entry producing a whole set of files names a filename template rather than a filename,
and that template must name a directory of its own beneath the drafts area, belonging to
that entry alone — no other entry may claim it, sit inside it, or contain it, and no
single-file entry's output may land inside it.

The reason is how a set is committed: the destination directory is replaced whole in one
rename rather than written into file by file, which is what makes twenty-four frames as
all-or-nothing as one image. So a shared directory is one where committing the first entry
destroys what the second committed, with nothing to restore from; two entries on the same
directory is the obvious case, one sitting inside another is the one that looks harmless
and is worse, and a template writing straight into the drafts area is the same mistake at
its limit, replacing every other entry's drafted assets in a single rename.

The frame number must come out as ordinary digits, because whether a run's output already
exists is decided by matching the template against names on disk — a template formatting
its number as anything else defeats that match, so the framework fails to notice frames
already there, replaces the directory whole, and reports as absent a set of frames sitting
in it. Two frame sets mixed in one directory is what this prevents, and nothing downstream
would catch it.

### Format checking

A format is declared per entry and checked against the bytes that arrive, so a file never
contradicts its own extension.

### The whole manifest is checked before anything is spent

Every command reading the manifest checks every entry, not only the one named, and stops
at the first that is wrong. The rules that matter most concern pairs of entries — two
sharing a name, two whose outputs collide — and none can be checked by looking at one
entry, so generating one faultless entry still fails when two others contradict each
other.

Checking happens before the credential is read and before any model is called, so a
manifest mistake costs nothing.

What the framework refuses is anything it would otherwise have to guess about: a
misspelled key, a field with no effect on the entry it sits on, a combination of asset
kind and operation describing something it cannot do, a declared file or directory that is
not there, an output path escaping the drafts area. An ignored mistake is a wrong asset
generated with no signal, and the caller is an agent that cannot see it happened.

## What it generates

Five kinds of asset: images, sound clips, music, sprite sheets, and video.

### What the framework does not generate

Code-driven animation is out of scope, because it produces no asset. A transform applied
to art that already exists — growing a mark to double size and shrinking it back, a
pulse, a spin, a fade, a slide — is written in the calling project's code and generates
no file, so there is nothing for the framework to make. The framework's business is
assets; motion that is arithmetic over an existing asset belongs to whoever draws the
frame.

A sprite sheet is what an animation becomes when the art itself has to change rather than
merely move — a jaw that opens, a mark that transforms into something else. No transform
produces new art, which is what makes a sprite sheet a generated asset and a
scale-and-settle not one.

### Sprite sheets

A sprite sheet is a sequence of frames, and every frame is PNG with alpha, like every
other image the framework produces. How many frames, what size, and how they are laid out
are per-entry data the calling project writes, like every other model input.

Frames are laid out row-major — left to right, then top to bottom — and where the declared
grid holds more cells than frames, the leftover cells are fully transparent. The sheet is
the full grid rather than cropped to the last frame, because the calling project declared
the layout and a consumer indexes cells by it.

The two paths — the pixel-art model and the image-to-video-and-matte chain — are a
choice with a framework default, and an entry names the other path when it wants it. Which
one is the default is unsettled — see Open Questions.

Pixel art comes back as a finished sheet from a single call.
`retro-diffusion/rd-animation` returns a sprite sheet directly, with consistent framing
and frame counts sized for game engines, and it accepts input images, palette images,
background removal and seamless tiling. It is a pixel-art model, so it fits a theme drawn
in pixel art and nothing else.

Every other art style is a chain of several entries rather than one entry doing several
things — see `### One entry is one step`. An image-to-video model animates a reference
image, the subject is matted out of the video, and the frames become the sheet. Models
that hold a character consistent across frames from reference images include Veo 3.1,
Seedance 2.0 — which takes up to nine reference images — and Wan 2.7 R2V. Matting is
its own step: `arielreplicate/robust_video_matting` is built for video rather than stills
and tracks the subject across frames, which is what stops the edge flicker that matting
each frame independently produces.

Pulling a whole frame sequence out of a video is not a solved step.
`lucataco/frame-extractor` returns only the first or last frame of a video, so a full
sequence needs something else — and ffmpeg is an external binary this project does not
otherwise depend on. Extracting frames is local image handling the framework does itself,
not a Replicate call.

The steps that produce the frames are separate manifest entries the calling project writes
and runs in order, per `### One entry is one step`. Assembling those frames into one sheet
is likewise the framework's own work, not a Replicate call.

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

A returned sheet is checked against the dimensions its entry declared: frame size and
layout imply a pixel width and height, and a sheet that is not that size is a mismatch,
not a result to accept — this matters most on the pixel-art path, where the model does
its own framing. What is not checked is how many cells hold art. A correctly-sized sheet
with too few frames drawn into it passes; a blank cell is indistinguishable from a frame
that is deliberately empty.

### Video

Video is generated, and no calling project consumes it yet. It is built because it is
wanted later — tutorials and similar material.

Video carries no usable transparency, which is why it is not how an in-game animation is
produced. Video codecs do not reliably carry an alpha channel, so a video cannot sit over
a game board the way a PNG can. That is the reason a sprite sheet, not a video, is the
animation asset.

### Artistic consistency

Artistic consistency is a requirement. Assets generated across a project have to look like
they belong together, and the first version holds that with reference images — the same
reference assets passed as inputs to each generation, which is what the image model
already accepts.

Fine-tuning a model on already-approved assets is a second-version concern, and it is
wanted: consistency deserves a real mechanism rather than being left to how each prompt is
worded. Building it would give the framework a second verb beyond generating. What that
plan is has not been worked out.

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
writes. Only a step that calls Replicate needs it: listing a manifest, reading the record,
and the two local operations run without one.

### Drafts, then approval

Nothing generated is applied directly. Generation is two stages. Two places hold anything
the framework writes that persists once a run ends: a drafts area belonging to the calling
project, and its own record file. The lock file (see One run at a time) is the one
exception: it holds no content, and what is transient is the lock being held on it, not
the file itself. The framework is handed the drafts path and can reach nowhere else
within the calling project. Approval is a person saying yes: there is no score, no
threshold and nothing automatic. Only then does the asset move into the place it ships
from.

The fence is structural rather than a rule the tool has to remember. Approved assets do
not live anywhere the framework can write, so a rerun cannot clobber one — the guarantee
holds even if the tool is wrong about everything else.

### One run at a time

- **Two runs never write at once.** The framework takes a single-writer lock for the
  duration of a run, and a second invocation that finds the lock held refuses rather than
  proceeding. Concurrent runs would interleave their staging and could each delete the
  other's partial work, which would break the guarantee that a killed run leaves the tree
  as it found it.
- **The lock sits beside the record file, never in the drafts area.** Drafts holds
  drafted assets and nothing else — that is what makes drafting cheap, since generating,
  looking and discarding costs nothing. Framework bookkeeping belongs where the record
  already lives.
- **The lock file is created once and never deleted.** What is acquired and released is
  the lock on it, not the file. Deleting a lock file while a run still holds it is a
  race — a second run can end up holding a lock on a file that has been unlinked while a
  third creates a fresh file and locks that, leaving two runs each believing they hold
  it — exactly the collision the lock exists to prevent. A lock file lying there unheld
  blocks nobody, so leaving it in place costs nothing, and a lock held by no live process
  does not block the next run forever.

## The record

### The per-asset record

One record per asset, holding the last generation only. Not a history and not an
append-only log — regenerating an asset replaces that asset's entry rather than adding
to it. An entry holds the pinned model version, the prompt and the inputs that produced
the asset, plus the seed when there was one — the entry declared it or the model
returned it. The framework never invents a seed to fill the gap; where none exists, the
entry records that there was none. An asset generated without a seed cannot be
reproduced exactly, only asked for again. The model version is always pinned, never a
bare model name, which is the whole reason the record is worth keeping. What the record
is for is knowing what was last asked for, so the next request is a change from it
rather than a fresh invention.

It is contained and trashable: one file the framework owns, written nowhere else and never
into any other document. Deleting it costs the ability to tweak from the last request, and
nothing else.

The framework never prunes the record; an entry for an asset the manifest no longer names
stays, and deleting the whole file is the supported reset — pruning would make reading the
record destructive as a side effect of an unrelated manifest edit, and would silently
discard what an asset was last asked for the moment someone renamed its entry; the file
grows until someone deletes it, which costs nothing that matters.

An asset never generated is a question with an answer rather than a failure — asking what
it was last asked for succeeds and says there is nothing, which is a different case from a
record that exists and cannot be read.

- **A record the framework cannot read is a stated failure, never a crash.** Whatever the
  reason — it does not parse, it is empty, its shape is wrong — the framework stops and
  says so, and it says the same thing every time rather than surfacing whichever internal
  error happened first.
- **It is noticed before anything is generated.** The check comes early enough that no
  model is called and no asset is written, because an asset that lands while its record
  cannot be updated is the exact divergence the record exists to prevent — the asset
  would exist with the record insisting it never did.
- **The remedy is to delete it, and the framework says so rather than doing it.** This
  is the one failure with a safe and obvious fix, and it is safe precisely because the
  record is trashable: deleting it costs the ability to tweak from the last request and
  nothing else, which this section already says. The framework never deletes or repairs
  the record itself — that is the user's to do, like every other destructive act here.

### Regenerating, and leaving nothing behind

A run leaves the drafted assets and one record, and nothing else — no temp files, no
scratch scripts, no response dumps, no half-written asset. A run that dies partway leaves
the tree as it was rather than leaving a truncated file behind.

Regenerating is deliberate and one named asset at a time. There is no bulk regenerate,
because a single command that redoes everything is how generation gets out of control; and
an existing draft is replaced only when the rerun says so explicitly.

### How a run leaves nothing behind

A run that dies partway leaves the tree as it found it because it never writes an asset
where the asset is going to live — it builds its output in a staging area inside the
drafts area, and the result reaches its declared path by a single rename.

- **Staging is inside the drafts area, not a system temp directory**, because a rename
  within one filesystem is atomic and a copy across two is not, and a process killed
  mid-copy leaves a truncated file at exactly the declared path.
- **A destination is never written into incrementally** — for one file the commit is one
  rename onto the declared path, for a set the existing directory is moved aside, the
  staged directory renamed onto the vacated path, and only then the moved-aside copy
  deleted, so there is no moment where the destination holds some new and some old files.
- **Each run leaves a marker beside its staging area** saying what it is building and
  where it moved anything aside to, written before anything is staged and never updated
  after, which is what lets a later run repair an interrupted one from the marker alone
  without reading the manifest — a run can be interrupted mid-commit and the manifest then
  edited, stop parsing, or no longer hold the entry that was building.
- **The next run repairs what an interrupted one left**, sweeping the drafts area before
  doing anything else — a set moved aside but never replaced is put back, a moved-aside
  copy whose replacement did land is deleted, leftover staging areas removed, so a killed
  run is not something anyone cleans up by hand.
- **The sweep never removes what it cannot account for**, acting only on what a marker
  explains and only on names in the namespace the framework reserves under the drafts
  area, which no entry may declare as its output — a sweep deleting everything that merely
  looked temporary would destroy a set that had only been moved aside.
- **One drafts area belongs to one config**, because the sweep repairs runs other than its
  own and what stops it repairing a live one is the lock, but the lock is held per record
  while the sweep ranges over the drafts area, and those are the same scope only while
  each drafts area has exactly one record — two configs sharing a drafts area would take
  different locks, run at once, and sweep each other's work in flight; the framework
  cannot detect this and does not try, so it is a constraint on the calling project.

What none of this covers is the asset and its record changing together — they are two
files in two directories and no single rename makes both true at once, so a run killed
between committing the asset and writing the record leaves a whole asset described by the
previous run's record entry; that is a stale description, never a torn file, and the next
run of that entry closes it.

## Open Questions

- Which default model for sound clips, sprite sheet frames, and video? Images and music
  have one; the other three do not.
- What does managing artistic consistency look like beyond passing reference images on
  every call — fine-tuning a model on already-approved assets, or something else?
- Which of the two paths — the pixel-art model or the image-to-video-and-matte chain —
  is the sprite-sheet framework default?
- What format and codec does generated video use, given that transparency is not
  available?
- Is a seamless music loop closed by inpainting across the wrap-around seam — joining
  the track's end to its start and filling the join — and does that make a looping
  music entry a chain rather than a single call?
- Are generated asset files committed to git by the calling project?
- When an entry assembles a sheet, must it list every frame filename, or should it be
  able to name them once with a count? Listing is explicit about the order they play in;
  a pattern is far less to write and leaves the order implicit.

