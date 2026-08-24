# PRD: CLI Version One

> **Status:** Draft · Source docs read: `Framework Design.md`

## Problem

There is no code. An agent asked to generate an asset for a calling project has nothing to
run: no command to invoke, no agreed file to write the request in, no way to find out what
was asked for last time. Every calling project would otherwise invent its own arrangement,
which is the thing the framework exists to prevent — it is "a shared utility: other projects
in the mono repo call it to generate the assets they need" (`Framework Design.md` § What this
is).

This is the contract every calling project and the agent driving it will depend on, so it is
specified before it is built rather than discovered by writing it.

## Goal

An agent, working under some other active project, can run four commands against that
project's hand-written manifest: find out what entries exist, generate one by name,
read back what an entry was last asked for, and regenerate one by name replacing what is
there. Every command reads its paths from one config file in the calling project, prints one
JSON document, never asks a question, and either finishes cleanly or leaves the tree exactly
as it found it.

## Notes on sourcing

Every requirement below carries one of:

- **[§ Name]** — settled in `Framework Design.md` under that section.
- **[PRD choice]** — decided here because the contract cannot be written without it. Each one
  states its reason and how expensive it is to reverse.

Two of the design doc's Open Questions are answered by this PRD, on instruction: **how the CLI
is told where things live** (R6–R13, an explicitly overturnable assumption) and **what the
CLI's command surface is** (R14–R33). The design doc still lists both as open; it needs
updating to match whatever survives review.

---

## Requirements

### The program

**R1.** The framework ships one executable named `agf`, invoked as `agf <command> [args]`.
No other entry point exists — it is a CLI, not a library, and no application code links
against it. [§ A CLI, driven by an agent] · name is [PRD choice], taken from the project
manifest's alias; renaming it before anything calls it is free.

**R2.** Exactly four commands exist: `list`, `generate`, `record`, `regenerate`. An unknown
command exits 1 without reading any file. [PRD choice — working backwards from what a driving
agent needs; adding a fifth later is additive.]

**R3.** No command prompts, waits for input, or reads stdin. Given a fully-specified
invocation, every command runs to a terminal state unattended. [§ A CLI, driven by an agent]

**R4.** Every command writes **exactly one JSON document to stdout** and nothing else to
stdout, on success and on failure alike. Diagnostics and progress go to stderr and are never
required to interpret a result. [§ A CLI, driven by an agent — "predictable, parseable
output"] · JSON-on-stdout is [PRD choice].

**R5.** Every failure prints `{"ok": false, "command": ..., "error": {"code", "message",
"remedy"}}`, where `message` states what failed and `remedy` states what to change. Both
fields are non-empty on every error path. [§ A CLI, driven by an agent — "errors that say what
failed and what to change"]

### How the CLI is told where things are

> **This section is an assumption, flagged for overturning.** The design doc leaves path
> discovery open (§ Open Questions). Version one assumes a config file in the calling project
> rather than flags on every command or a hardcoded convention: the caller is an agent, and a
> config file is the shape with the fewest things to get wrong per invocation, while keeping
> the paths per-project data the calling project writes — like everything else it writes.
> Nothing consumes this yet, so it is cheap to change.

**R6.** The CLI reads its paths from a YAML file named `assetgen.yaml` in the calling
project's root directory, resolved as `./assetgen.yaml` relative to the working directory.
[PRD choice]

**R7.** `--config <path>` overrides R6 for one invocation. It is the only way to run from
outside the calling project's root. [PRD choice]

**R8.** The CLI never searches parent directories for a config file. A missing config exits 2
naming the path it looked for. Reason: an upward search makes the same command mean different
things depending on where it is run from, and an agent cannot see that it happened. [PRD
choice]

**R9.** `assetgen.yaml` holds exactly these keys:

| Key | Required | Meaning |
|---|---|---|
| `manifest` | yes | The prompt manifest file |
| `drafts` | yes | The drafts area — the only directory generated assets are written into |
| `record` | yes | The record file the framework owns |
| `samples` | no | Root for sample and reference assets |
| `base` | no | Root for base assets built from |

[§ Drafts, then approval; § The per-asset record; § Sample images; § Providing base assets to
build from] · file name, key names and file format are [PRD choice].

**R10.** Every value in `assetgen.yaml` is a path resolved **relative to the config file's own
directory**, not to the working directory, so `--config` works from anywhere. An absolute path
is accepted as-is. [PRD choice]

**R11.** An unknown key in `assetgen.yaml`, a missing required key, or a declared `manifest`,
`drafts`, `samples` or `base` path that does not exist, exits 2 naming the offending key.
[PRD choice — a silently-ignored typo is exactly the failure an agent cannot see.]

**R12.** The framework creates no directory declared in the config. It does create
intermediate directories **under `drafts`** implied by an entry's output filename. [PRD
choice]

**R13.** The framework writes to exactly two locations: inside `drafts`, and the `record`
file. Any resolved write path outside both is refused before anything is written. In
particular an entry's output path that is absolute, or that escapes `drafts` via `..`, is a
manifest error. [§ Drafts, then approval — "that is the only place it writes… handed one path
and can reach nowhere else"]

> The design doc says drafts is the *only* place the framework writes, while also requiring it
> to write one record. R13 reads that as two declared write targets and no others. The doc's
> wording needs reconciling.

### The commands

**R14.** `agf list` takes no positional arguments and accepts only `--config`. It requires no
credential. [PRD choice]

**R15.** `agf list` prints, for every entry in the manifest, in manifest order:

```json
{"ok": true, "command": "list", "entries": [
  {"name": "...", "type": "image", "operation": "model",
   "model": "sourceful/riverflow-2.0-pro", "model_source": "entry|default|none",
   "output": "...", "format": "png", "draft_exists": false, "has_record": false}
]}
```

`model_source` says whether the model id came from the entry or from a framework default, so
the agent can see that a default applied without being told separately. `draft_exists` says
whether a file already sits at the entry's declared output path; `has_record` whether the
record holds an entry under that name. [PRD choice; defaults per § Choosing a model]

**R16.** `agf list` against a manifest with zero entries exits 0 with an empty `entries` list.
An empty manifest is a result, not a failure. [PRD choice]

**R17.** `agf generate <name>` takes exactly one positional argument and accepts only
`--config`. Two or zero positional arguments exit 1. There is no option that makes `generate`
overwrite; replacing an existing draft is `regenerate`'s job and nothing else's. [§
Regenerating, and leaving nothing behind — "an existing draft is replaced only when the rerun
says so explicitly"]

**R18.** `agf generate <name>` exits 8 without calling anything if a file already exists at
any of the entry's declared output paths, naming the path and naming `regenerate` as the
remedy. [§ Regenerating, and leaving nothing behind]

**R19.** `agf generate <name>` performs the entry's single step, checks the result, writes the
output into `drafts`, replaces that entry's record, and prints:

```json
{"ok": true, "command": "generate", "name": "...", "operation": "model",
 "outputs": ["assets/drafts/x.png"], "format": "png", "bytes": 12345,
 "model_version": "owner/model:0e9f...", "seed": 42, "replaced": false,
 "checks": {"format": "pass", "layout": "skipped"}}
```

`outputs` is **always a list**, including for the single-file case, so an agent parses one
shape. `seed` is `null` when no seed is available (R50). `model_version` and `seed` are `null`
for local operations. [PRD choice; one-step-per-entry per § One entry is one call]

**R20.** `agf regenerate <name>` is `generate` with R18 removed: it succeeds whether or not a
draft already exists, replacing whatever is there. It reports `"replaced": true` when it
overwrote an existing file and `false` when it did not. [§ Regenerating, and leaving nothing
behind]

**R21.** Invoking `regenerate` **is** the explicit override. It does not accept overrides of
the entry's prompt, model, inputs or filename from the command line, and no command does.
Reason, stated so an implementer does not add one as a convenience: "The agent runs the
generation; it does not author the request… never to invent what the entry should have said"
(§ A CLI, driven by an agent). Changing what is asked for means editing the manifest.

**R22.** There is no command, option or argument form that generates more than one named entry
per invocation, including a glob, a comma-separated list, a repeated argument or an "all"
sentinel. [§ Regenerating, and leaving nothing behind — "There is no bulk regenerate"]

**R23.** `agf record <name>` takes exactly one positional argument and accepts only
`--config`. It requires no credential and makes no call. [PRD choice]

**R24.** `agf record <name>` validates the name against the **manifest** first and exits 4 if
no entry bears that name — so a typo is caught rather than answered with "never generated".
[PRD choice]

**R25.** For a manifest entry that has never been generated, `agf record <name>` exits **0**
with `"record": null`. Never generated is an answer, not an error. [PRD choice]

**R26.** For a generated entry, `agf record <name>` prints the stored record entry verbatim
(R47). [§ The per-asset record — "knowing what was last asked for, so the next request is a
change from it"]

### Validation order and exit codes

**R27.** Every command validates in this fixed order, stopping at the first failure, so that
the exit code for a given broken invocation is deterministic:

1. Argument shape → 1
2. Config file → 2
3. Manifest parse and entry validity → 3
4. Entry name lookup → 4
5. Existing draft collision (`generate` only) → 8
6. Credential → 5
7. The call or local operation → 6
8. Format and layout checks → 7
9. Commit output, then write the record → 0

[PRD choice — an agent branches on the exit code, so the codes must not depend on ordering
luck.]

**R28.** Exit codes:

| Code | Means |
|---|---|
| 0 | Success |
| 1 | Usage — unknown command, wrong argument count, unknown option |
| 2 | Config — missing, unparseable, missing or unknown key, declared path absent |
| 3 | Manifest — missing, unparseable, invalid or contradictory entry |
| 4 | No entry by that name |
| 5 | Credential absent from the environment |
| 6 | Provider — request rejected, prediction failed or canceled, transport failure |
| 7 | Check failed — bytes do not match the declared format, or sheet does not match the declared layout |
| 8 | Refused — a draft already exists at the declared output path |

[PRD choice — nothing consumes these yet; renumbering is free until something does.]

**R29.** The credential is read from the environment variable `REPLICATE_API_TOKEN` and from
nowhere else. The CLI has no option, config key or manifest field that supplies it, and does
not read any credentials file. [§ An authoring tool, not a build step]

**R30.** A missing or empty `REPLICATE_API_TOKEN` exits 5 naming the variable — but only for
entries that make a provider call. Local operations (R60–R65) run without a credential. [§ An
authoring tool, not a build step; § Sprite sheets]

**R31.** The credential value never appears in stdout, in stderr, or in the record. [§ An
authoring tool, not a build step — "never lands in anything the tool writes"]

**R32.** The CLI polls a prediction until it reaches a terminal state and imposes no timeout
of its own. Reason: generation times differ by orders of magnitude between models, so any
default would cancel real work; a caller that wants a limit imposes it. [PRD choice]

**R33.** A failed or canceled prediction exits 6 with the provider's own error text in
`message`. The full provider response is not written to any file and is not printed to stdout.
[§ Regenerating, and leaving nothing behind — "no response dumps"]

### The manifest

**R34.** The manifest is a YAML file holding a list of entries, one per asset. The framework
reads it and **never writes it** — no command creates, edits, reorders, formats or appends to
the manifest. [§ One script, per-asset inputs are data]

**R35.** An entry is exactly one step: one provider call, or one of the two local operations.
The framework holds no notion of a multi-step asset, does not sequence entries, does not
resolve dependencies between them, and does not know that one entry's input file was another
entry's output. Rerunning an entry never cascades to any other. [§ One entry is one call]

> The design doc says an entry is exactly one *API call*, while also requiring two local
> operations that make no call (§ Sprite sheets). R35 takes the narrow reconciliation — one
> entry is one step — and changes nothing else. The doc's wording needs reconciling.

**R36.** Entry fields:

| Field | Required | Meaning |
|---|---|---|
| `name` | yes | Unique across the manifest; the argument every command takes |
| `type` | yes | One of `image`, `sound`, `music`, `sprite_sheet`, `video` |
| `operation` | no | `model` (default), `assemble_sheet`, or `extract_frames` |
| `model` | see R38 | Replicate model id, e.g. `owner/name` |
| `prompt` | no | The text prompt, if the model takes one |
| `output` | yes | Exact output filename, relative to `drafts` |
| `format` | yes | Declared file format, checked against the bytes |
| `inputs` | no | Map of arbitrary model inputs, passed through untouched |
| `input_files` | no | Map of input names to file references (R41) |
| `frame_count`, `frame_size`, `layout` | see R42 | Sprite sheet geometry |
| `frames` | `assemble_sheet` only | Ordered list of file references |
| `source` | `extract_frames` only | File reference to the video |

[§ One script, per-asset inputs are data; § Choosing a model; § Filenames; § Format checking;
§ Sample images; § Sprite sheets] · field names are [PRD choice].

**R37.** A duplicate `name`, a missing required field, or an **unrecognized field** anywhere in
an entry exits 3 naming the entry and the field. A misspelled key is never silently ignored.
[PRD choice — an ignored typo is a wrong asset generated with no signal.]

**R38.** `model` is optional where the framework has a default for the entry's `type`, and
required otherwise. Version one has defaults for two types only:

| `type` | Default model |
|---|---|
| `image` | `sourceful/riverflow-2.0-pro` |
| `music` | `stability-ai/stable-audio-2.5` |
| `sound`, `sprite_sheet`, `video` | none — `model` required, omitting it exits 3 |

[§ Choosing a model] · Requiring an explicit model for the other three is how version one
proceeds without answering the open question of what their defaults should be. Filling one in
later is additive and breaks no existing manifest.

**R39.** A `model` named in an entry always overrides the default for its type. A default is
what an entry gets for saying nothing. [§ Choosing a model]

**R40.** Everything under `inputs` is passed to the provider **untouched** — not renamed,
reordered, validated against any schema, coerced, or filtered. The framework holds no
knowledge of what any model input means. [§ Choosing a model — "This is what keeps a new model
from being a code change"]

**R41.** `prompt` is a first-class field, not an ordinary input, because the record is required
to hold the prompt and so the framework must know which field it is. The framework merges it
into the inputs sent to the provider under the key `prompt`. An entry that sets both `prompt`
and `inputs.prompt` exits 3. [§ The per-asset record; § Choosing a model]

**R42.** Values under `input_files`, and every element of `frames` and `source`, are **file
references** of the form `<root>:<relative path>`, where `<root>` is `samples`, `base` or
`drafts`. The framework resolves the reference against the corresponding config path, reads
the file, and substitutes it into the inputs under that key. A path string sitting in `inputs`
is passed through as a literal string and is never treated as a file. Reason for the explicit
root token: with three roots, a bare relative path is ambiguous and the resolution order would
be a rule everyone has to remember. [§ Sample images; § Providing base assets to build from; §
One entry is one call — a later entry names an earlier entry's output file] · syntax is [PRD
choice].

**R43.** A file reference naming a root that is not declared in `assetgen.yaml`, or a file that
does not exist, exits 3 naming the reference and the missing config key or path. [PRD choice]

**R44.** `frame_count` (integer), `frame_size` (`[width, height]` in pixels) and `layout`
(`{columns, rows}`) are required when `type` is `sprite_sheet` and rejected on any other type.
`columns × rows < frame_count` exits 3. Frames are ordered row-major: left to right, then top
to bottom. [§ Sprite sheets — "How many frames, what size, and how they are laid out are
per-entry data the calling project writes"] · row-major and the field shapes are [PRD choice];
both readings of ordering are reasonable, so it is stated rather than left to an implementer.

**R45.** `output` is a filename, may contain subdirectories under `drafts`, and is written
exactly as declared. The framework never generates, adjusts, suffixes, deduplicates or
sanitises a filename. [§ Filenames — "the framework writes that name and never invents one"]

**R46.** The framework writes no sidecar or metadata file alongside any asset, sprite sheets
included. [§ Sprite sheets — "No sidecar metadata travels with the sheet"]

### The record

**R47.** The record is a single JSON file at the config's `record` path, owned by the
framework, written nowhere else and never merged into any other document:

```json
{"version": 1, "entries": {
  "<entry name>": {
    "operation": "model", "type": "image",
    "model_version": "owner/name:0e9f…", "prompt": "…", "seed": 42,
    "inputs": {…}, "input_files": {…},
    "outputs": ["…"], "format": "png",
    "generated_at": "2026-08-23T10:11:12Z"}}}
```

[§ The per-asset record] · JSON, the single-file shape, the `version` key and the field names
are [PRD choice]. JSON rather than YAML because this file is machine-written and read back
through `agf record`; hand-editing it is not a use it needs to invite.

**R48.** The record holds **one entry per asset, the last generation only**. Regenerating
replaces that entry in place. Nothing appends, and no history, previous value or timestamp
series is retained anywhere. [§ The per-asset record]

**R49.** `model_version` is always the **pinned** version — the full `owner/name:version`
identifier the provider actually ran — never a bare model name. An entry whose `model` names
no version is resolved to a pinned version at call time and the pinned value is what is
recorded. [§ The per-asset record — "The model version is always pinned… which is the whole
reason the record is worth keeping"]

**R50.** `seed` records the seed when the entry declared one in its inputs or the provider
returned one, and is `null` otherwise. The framework never invents a seed, because injecting
one would be the framework authoring an input that belongs to the manifest. An entry that
wants a reproducible seed declares it. [§ One script, per-asset inputs are data — "it invents
nothing that belongs in it"] · the `null` case is [PRD choice].

**R51.** A local operation gets a record entry like any other, with `model_version`, `prompt`
and `seed` set to `null`. [PRD choice — the record's purpose is knowing what produced the
asset, which applies equally.]

**R52.** The framework never prunes the record. An entry for a name no longer in the manifest
stays. Deleting the whole file is the supported reset and costs only the ability to tweak from
the last request. [§ The per-asset record — "It is contained and trashable"]

**R53.** The record is written only after the asset is in its final place, and is not touched
at all when a run fails for any reason. [§ Regenerating, and leaving nothing behind]

### Checks

**R54.** After a download or a local operation, the file's **bytes** are checked against the
entry's declared `format` by inspecting the content itself, never the filename or the
provider's stated content type. A mismatch exits 7 stating the declared format and what the
bytes actually are. [§ Format checking]

**R55.** An entry whose `output` extension disagrees with its declared `format` exits 3. [§
Format checking — "so a file never contradicts its own extension"]

**R56.** The framework recognises at least these declared formats: `png`, `jpeg`, `webp`,
`wav`, `mp3`, `mp4`. An unrecognised `format` exits 3. Recognising a format for checking is not
the same as choosing a default: which format and codec generated video uses stays open, and
the framework checks whatever the entry declares. [§ Format checking] · the set is [PRD
choice], extended by adding a detector.

**R57.** A returned or assembled sprite sheet is checked against its declared geometry: the
image's pixel dimensions must equal exactly `columns × frame_width` by `rows × frame_height`.
A mismatch exits 7 stating both the declared and the actual dimensions, and the sheet is not
written. This matters most on the pixel-art path, where the model does its own framing. [§
Sprite sheets — "A model that returns a different frame count or framing than was asked for is
a mismatch, not a result to accept"]

**R58.** Sprite-sheet frames are PNG with alpha. An `assemble_sheet` entry whose frames are not
PNG, or whose declared `format` is not `png`, exits 3. [§ Sprite sheets — "every frame is PNG
with alpha"]

**R59.** A provider that returns more than one output file for an entry declaring one `output`
exits 7. The framework never selects among returned files and never invents names for the
extras. [§ Filenames]

### Local operations

**R60.** `operation: assemble_sheet` performs no provider call. It reads the files named in
`frames`, in the order given, and writes one sheet at `output` laid out per the entry's
`frame_count`, `frame_size` and `layout`. [§ Sprite sheets — "Assembling those frames into one
sheet is likewise the framework's own work, not a Replicate call"]

**R61.** `assemble_sheet` exits 3 if `len(frames) != frame_count`, or if any frame's pixel
dimensions differ from the declared `frame_size`. It does not scale, crop or pad a frame to
fit. [PRD choice — silently resizing a frame produces a plausible-looking wrong sheet.]

**R62.** `operation: extract_frames` performs no provider call and shells out to no external
binary. It reads the video named by `source` and writes its frames into `drafts`. [§ Sprite
sheets — "Extracting frames is local image handling the framework does itself, not a Replicate
call"; ffmpeg is named there as a dependency this project does not have]

**R63.** For `extract_frames`, `output` is a filename template containing exactly one `{n}`
placeholder in Python format-spec syntax, e.g. `walk_{n:03d}.png`. Frames are numbered from 1
in video order. A template with zero or more than one placeholder exits 3. [PRD choice — it
keeps R45's "never invents a name" true for a step that writes many files.]

**R64.** `extract_frames` accepts an optional `frame_count`; when present, a video yielding a
different number of frames exits 7. When absent, every frame is written. [PRD choice]

**R65.** The framework never delivers a sprite sheet as loose numbered frames. Frames written
by `extract_frames` are the output of that entry; the sheet is the output of the
`assemble_sheet` entry that consumes them. [§ Sprite sheets]

### Cleanliness

**R66.** A run leaves behind exactly the files an entry declared and the record, and nothing
else: no temp files, no scratch scripts, no response dumps, no logs, no half-written asset. [§
Regenerating, and leaving nothing behind]

**R67.** Every output is staged and only then committed: the framework writes to a staging file
**inside the `drafts` directory** named with the reserved prefix `.agf-tmp-`, runs all checks
against it, and renames it onto the declared path as the last step. Staging inside `drafts`
rather than the system temp directory is deliberate — a same-filesystem rename is atomic, so a
process killed mid-write can never leave a truncated file at a declared path. [PRD choice, with
the reason recorded because a cross-device copy would silently break it.]

**R68.** A run that exits for any reason before committing — a failed check, a provider error,
an interrupt — removes its staging files. The declared output path is untouched: absent if it
was absent, unchanged if it existed. [§ Regenerating, and leaving nothing behind — "A run that
dies partway leaves the tree as it was"]

**R69.** `generate` and `regenerate` delete any pre-existing `.agf-tmp-*` file in `drafts` at
startup, before doing anything else. A process killed with a signal it cannot handle leaves
one behind, and sweeping at the next run is what makes R66 true in that case too. [PRD choice]

**R70.** No path beginning `.agf-tmp-` is ever reported by `list` as a draft, accepted as an
entry's `output`, or resolvable as a file reference. [PRD choice]

---

## Out of Scope

Version one does **not** include, and no requirement above should be read as implying:

- **Fine-tuning or training a model**, and any fuller mechanism for artistic consistency.
  That is version two. Version one holds consistency by passing reference images as inputs,
  which is `input_files` (R42) and needs no new machinery. What that mechanism should be is
  open in `Framework Design.md` § Open Questions. [§ Artistic consistency]
- **Any bulk or batch command** generating more than one named entry per invocation (R22).
  [§ Regenerating, and leaving nothing behind]
- **Approving an asset, or moving one out of the drafts area.** Approval is a person saying
  yes, and the move is not the framework's. The framework cannot reach where approved assets
  live. [§ Drafts, then approval]
- **Anything that plays, sequences or times an animation** — playback, frame timing, when an
  animation fires. That is the calling application's. [§ Sprite sheets]
- **Code-driven animation** — a transform over art that already exists produces no file, so
  there is nothing to generate. [§ What the framework does not generate]
- **A library API.** There is one executable and no importable interface for application code.
  [§ A CLI, driven by an agent]
- **Sequencing, dependency resolution or cascading reruns** between entries (R35).
  [§ One entry is one call]
- **Writing the manifest** (R34), and **sidecar metadata** beside any asset (R46).

## Open Questions

Open in `Framework Design.md` and deliberately left open here. Where version one needs
something from one, it is noted with what makes the choice reversible.

- **Which default model for sound clips, sprite sheet frames, and video?** Images and music
  have one; the other three do not. *Version one requires an explicit `model` on entries of
  those three types (R38). Adding a default later is additive and breaks no manifest.*
- **Which of the two paths — the pixel-art model or the image-to-video-and-matte chain — is
  the sprite-sheet framework default?** *Version one needs no answer: both paths are written
  as ordinary entries by the calling project, and R38 makes the model explicit either way.*
- **What format and codec does generated video use, given that transparency is not
  available?** *Version one checks whatever `format` the entry declares (R54, R56); no codec
  is chosen.*
- **Is a seamless music loop closed by inpainting across the wrap-around seam — joining the
  track's end to its start and filling the join — and does that make a looping music entry a
  chain rather than a single call?** *Version one needs no answer: a chain, if that is the
  answer, is already several entries under R35, which needs no new command.*
- **Are generated asset files committed to git by the calling project?** *Nothing in version
  one depends on this; the framework writes into `drafts` and takes no git action.*
- **What does managing artistic consistency look like beyond passing reference images on every
  call?** Out of scope for version one; see Out of Scope above.

Raised here, not by the design doc:

- **Is a config file in the calling project the right way to learn its paths?** R6–R13 assume
  yes and specify `assetgen.yaml`. This answers a question the design doc lists as open, and
  is flagged for overturning: nothing consumes it yet, so switching to flags or a convention
  costs only this section.
- **May an `assemble_sheet` entry name its frames by pattern instead of listing them?** R60
  requires an explicit ordered list, which never guesses order but means a 24-frame sheet
  lists 24 filenames by hand. A `{pattern, count}` shorthand would remove that. *This is a
  proposal of mine, not something the design doc raises.*
