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

The design doc settles that the CLI learns the calling project's paths from a config file in
the calling project, and that the CLI exposes four things (§ A CLI, driven by an agent). What
it leaves to this PRD is the config file's name, format and keys, and "the exact flags, exit
codes and output shapes."

---

## Requirements

### The program

**R1.** The framework ships one executable named `agf`, invoked as `agf <command> [args]`.
No other entry point exists — it is a CLI, not a library, and no application code links
against it. [§ A CLI, driven by an agent] · name is [PRD choice], taken from the project
manifest's alias; renaming it before anything calls it is free.

**R2.** Exactly four commands exist: `list`, `generate`, `record`, `regenerate` — the four
things the design doc says the CLI exposes. An unknown command exits 1 without reading any
file, reporting the string as invoked in `command`. A bare `agf` with no command at all exits 1
with `"command": null` and a `message` naming the four. [§ A CLI, driven by an agent — "The CLI
exposes four things"] · adding a fifth later is additive.

**R3.** No command prompts, waits for input, or reads stdin. Given a fully-specified
invocation, every command runs to a terminal state unattended. [§ A CLI, driven by an agent]

**R4.** Every command writes **exactly one JSON document to stdout** and nothing else to
stdout, on success and on failure alike. Diagnostics and progress go to stderr and are never
required to interpret a result. [§ A CLI, driven by an agent — "predictable, parseable
output"] · JSON-on-stdout is [PRD choice].

**One document, even when something unexpected goes wrong.** stdout is written **once, at the end
of the run**, never incrementally, so no partial document is ever already out when a failure
happens. Every exception that escapes is caught at the top level and reported as R5's failure
document with code 11 (R28); the traceback goes to stderr, where diagnostics belong. An unhandled
traceback arriving on stdout instead of a JSON document would break the one property every caller
depends on, and the caller is an agent that cannot look at the terminal and decide what happened.
R5's `message` and `remedy` are non-empty here too — `message` carries the exception's own text and
`remedy` points at the stderr traceback. [PRD choice]

**R5.** Every failure prints `{"ok": false, "command": ..., "error": {"code", "message",
"remedy"}}`, where `message` states what failed and `remedy` states what to change. Both
fields are non-empty on every error path. `command` is the command as invoked — including an
unrecognised one — and `null` when none was given (R2). A failed check adds `checks` to the
error object — a **list**, one element per file, in the shape R71 fixes. [§ A CLI, driven by an
agent — "errors that say what failed and what to change"]

### How the CLI is told where things are

That there **is** a config file, in the calling project, carrying its manifest, sample and base
assets, drafts area and record, is settled: § A CLI, driven by an agent. Its name, format and
keys are not, and are [PRD choice] throughout this section.

**R6.** The CLI reads its paths from a YAML file named `assetgen.yaml` in the calling
project's root directory, resolved as `./assetgen.yaml` relative to the working directory.
[§ A CLI, driven by an agent — "a config file in the calling project"] · the name and location
are [PRD choice].

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

**R11.** An unknown key in `assetgen.yaml`, a missing required key, a declared `manifest`,
`drafts`, `samples` or `base` path that does not exist, or a `record` path whose **parent
directory** does not exist, exits 2 naming the offending key. The record *file* need not exist
— never generated is an answer (R25) — but the directory that will hold it must, and is
checked here rather than discovered at commit time. Reason: an asset that commits and then cannot
have its record written *for want of a directory* is an avoidable failure, and ruling it out costs
one check. The framework still creates no directory (R12).

**What that check does not buy, stated so nothing downstream over-claims it.** The asset and the
record are two files in two different directories, so no single rename makes both true at once. A
run killed in the window between the commit (R67) and the record's rename (R53) leaves a committed
asset described by the **previous** run's record entry, or by no entry at all where the asset had
never been generated. That window is unavoidable and is not a torn file — both files are
individually whole, and the next run of the same entry closes it. What R11 rules out is the
different failure of a record that could never have been written at all.

**A `record` path that resolves inside the `drafts` area, at any depth, also exits 2**, naming the
key and both paths. Reason: the record's temporary copy (R53) and the run lock (R72) would then sit
in the sweep's own scan path, where a `.agf-tmp-` record copy is indistinguishable from a run's
marker (R67); and the claim in R70 that no lock file ever appears under `drafts` would simply be
false. Drafts holds drafted assets and nothing else (§ One run at a time).

[PRD choice — a silently-ignored typo is exactly the failure an agent cannot see.]

**R12.** The framework creates no directory declared in the config. It does create
intermediate directories **under `drafts`** implied by an entry's output filename. They are
created at R27 step 10, immediately before the staging directory, because the staging directory
is a sibling of the destination (R67) and so its parent has to exist by then. A run that fails
after this point leaves them: a directory the entry's own `output` named is not debris, and
removing one risks removing a directory that was already there. R66 permits exactly this and
nothing else.

**Creating one can fail while the manifest is entirely valid**, so it has a stated outcome
rather than a crash: a plain file may already occupy a path a directory is needed at — put
there by something outside the framework, or left by an earlier manifest that declared a file
where a directory now belongs. That **exits 10**, naming the path and what occupies it, with
`remedy` saying to remove or rename the obstruction. Nothing has been called, spent or placed.
Reusing 10 rather than adding a code is deliberate: this is the same class of failure as a
commit blocked by what already sits at the destination (R67), and it has the identical remedy,
which is what an agent branches on. Two entries in *one* manifest colliding this way is not
this case — R63 catches that at validation, exit 3. [PRD choice]

**R13.** The framework writes assets into `drafts` and nothing else, and writes its own
bookkeeping — the `record` file, and the run lock beside it (R72) — in the record's directory
and nowhere else. Any resolved write path outside those is refused before anything is written.
In particular an entry's output path that is absolute, or that escapes `drafts` via `..`, is a
manifest error. [§ Drafts, then approval — "The framework writes to exactly two places, and
nowhere else, ever: a drafts area belonging to the calling project, and its own record file"] ·
the lock file is a third path the design doc's wording does not anticipate; it holds no asset
and no data, sits in the location the framework already owns, and persists between runs by
design (R66, R72).

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

`model` and `output` are the entry's declared values — `output` is the declared filename or,
for `extract_frames`, the declared template (R63), never an expansion of it. `model_source`
says where the model id came from, so the agent can see that a default applied without being
told separately:

| `model_source` | Means |
|---|---|
| `entry` | The entry named a `model` |
| `default` | The entry named none and the framework's default for its `type` applied (R38) |
| `none` | No model is involved — the operation is local (`assemble_sheet`, `extract_frames`), so `model` is `null` and naming one would be an error (R38) |

`draft_exists` says whether anything already occupies the entry's output: for a single-file
entry, whether a file sits at the declared path; for a template entry, whether any existing
file matches the template's shape (R18). `has_record` says whether the record holds an entry
under that name. [PRD choice; defaults per § Choosing a model]

**R16.** `agf list` against a manifest with zero entries exits 0 with an empty `entries` list.
An empty manifest is a result, not a failure. A file that is empty, or whose YAML document is
`null`, **is** a manifest of zero entries and is treated identically. Malformed YAML, or a
document whose top level is anything other than a list, exits 3 — those are mistakes, whereas
a file not yet filled in is a legitimate starting state. [PRD choice]

**R17.** `agf generate <name>` takes exactly one positional argument and accepts only
`--config`. Two or zero positional arguments exit 1. There is no option that makes `generate`
overwrite; replacing an existing draft is `regenerate`'s job and nothing else's. [§
Regenerating, and leaving nothing behind — "an existing draft is replaced only when the rerun
says so explicitly"]

**R18.** `agf generate <name>` exits 8 without calling anything, and before staging anything, if
the entry's output is already occupied — naming the first occupied path found and naming
`regenerate` as the remedy. Occupied means:

- **Single-file entry:** a file exists at the declared output path. A *directory* at that path is
  not this refusal — nothing generated it and `regenerate` would not fix it — and it is what makes
  the commit rename fail with exit 10 (R67).
- **Template entry (`extract_frames`, R63):** *any* existing file matches the template's shape
  — that is, any name the template could produce. This holds whether or not the entry declares
  a `frame_count`: with no declared count the framework cannot know which names this run would
  write, so any match is a collision. A partial set left by a previous arrangement is exactly
  what must not be silently half-overwritten.

  **What the placeholder matches:** for collision purposes the `{n}` placeholder — bare, or
  carrying any of the format specs R63 permits, such as `{n:03d}` — matches **one or more decimal
  digits**, and the literal text around it must match exactly. R63 admits only specs that produce
  digits, precisely so that this match and the names a run writes cannot diverge. A bare `{n}` is therefore not narrower than a
  padded one: `walk_{n}.png` and `walk_{n:03d}.png` both collide with `walk_7.png` and with
  `walk_007.png`. The match is deliberately wider than the set of names this run would write,
  because a false positive is a refusal an agent can read and act on, while a false negative
  mixes two frame sets in one directory and nothing downstream catches it (R63). [PRD choice]

[§ Regenerating, and leaving nothing behind]

**R19.** `agf generate <name>` performs the entry's single step, checks the result, commits its
output into `drafts` (R67), replaces that entry's record, and prints:

```json
{"ok": true, "command": "generate", "name": "...", "operation": "model",
 "model_version": "owner/model:0e9f...", "seed": 42,
 "output": [
   {"path": "assets/drafts/x.png", "format": "png", "bytes": 12345,
    "replaced": false,
    "checks": {"format": "pass", "layout": "skipped", "frame_size": "skipped",
               "frame_count": "skipped", "output_count": "pass"}}
 ]}
```

`output` is **always a list**, for every command and every operation, including the single-file
case. An agent that parses one shape for all of them is worth more than a shorter document for
the common case, so `format`, `bytes`, `replaced` and `checks` are per-file inside it and never
appear at the top level. **It lists the entry's declared outputs and nothing else** — the run's
marker (R67) is a framework file that sits outside the staging directory and never appears here,
with a byte count or otherwise. Every file's `checks` object carries **all five** of R71's keys, every
time, with `skipped` where the check did not apply — the key set is fixed, not a function of the
entry (R71). `model_version` and `seed` stay at the top level because one step has
exactly one of each; both are `null` for local operations, and `seed` is `null` whenever no
seed is available (R50). [PRD choice; one-step-per-entry per § One entry is one step]

**R20.** `agf regenerate <name>` is `generate` with R18 removed: it succeeds whether or not
output already exists, replacing whatever is there. Its success document has the same shape as
R19's, and each file's `replaced` reports that file alone — `true` where that path already held
a file this run overwrote, `false` where it did not. A regenerate that writes twelve frames over
an existing nine therefore reports nine `true` and three `false`. Because a multi-file entry's
directory is replaced whole (R67), the reverse case leaves no orphans: nine frames over an
existing twelve leaves nine, not nine plus three stale ones. [§ Regenerating, and leaving
nothing behind]

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

**R25.** `agf record <name>` prints `{"ok": true, "command": "record", "name": "...",
"record": ...}`, where `record` is the stored entry or `null`. A manifest entry that has never
been generated, and a `record` file that does not exist at all, both exit **0** with
`"record": null`: never generated is an answer, not an error. A record file that **exists and
cannot be read** is the different case and is not this one — it exits 13 at R27 step 5, before
this document is produced (R76). [PRD choice]

**R26.** For a generated entry, the `record` field holds the stored record entry verbatim
(R47) — including its `output`, which is what the entry declared, not a list of files on disk.
[§ The per-asset record — "knowing what was last asked for, so the next request is a change
from it"]

### Validation order and exit codes

**R27.** Every command validates in this fixed order, stopping at the first failure, so that
the exit code for a given broken invocation is deterministic:

1. Argument shape → 1
2. Config file — keys, and every path R11 requires to exist, including the record's parent
   directory → 2
3. Acquire the run lock (`generate` and `regenerate` only), beside the record → 9
4. Sweep and repair interrupted staging (`generate` and `regenerate` only) — not a failure stage
5. Record readable — the record file, **if it exists**, parses as a record (R76) → 13
6. Manifest parse and entry validity — **every entry, not only the one named** (R34) → 3
7. Entry name lookup → 4
8. Output collision (`generate` only) → 8
9. Credential → 5
10. Create any missing intermediate directories under `drafts` (R12), then the staging directory
    and, beside it, its marker (R67); then the call or local operation → **10** when an
    intermediate directory cannot be created because a file occupies its path (R12), **6** when a
    provider call fails (R75), **12** when extraction fails (R74). One stage, three codes, because
    a blocked destination, a remote failure and an unreadable local file have different remedies
    (R28).
11. Checks — format, sheet layout, frame size, frame count (R71) → 7
12. Commit the staged files (R67) → 10, then write the record → 0

**Nothing precedes the sweep but config validation and the lock.** It is after config
validation because the drafts area it sweeps is named by the config, and after the lock because
a live concurrent run's staging directory is not debris and must not be swept (R72). It is
before everything else, and in particular **before the manifest is read**, because a run
interrupted mid-commit has to be repairable whether or not the manifest still parses, still
holds the entry that was building, or still declares the same `output`. R69 accordingly
repairs from each run's own marker and the state on disk, and reads nothing but the config.

**The record is read at step 5 — after the sweep, before the manifest, and long before anything
is committed.** After the sweep for the same reason the manifest is: a run interrupted mid-commit
has to be repairable whether or not anything else in the calling project still parses, and the
sweep reads only the config and the markers (R69). Before the manifest, the credential and the
call, because step 12 is the first point at which the record is *written* and the asset is
already in place by then. A record discovered to be unreadable at that point would leave a
committed asset that can never be recorded — the one failure the record exists to prevent, and
the only one no later ordering can undo. Reading it at step 5 means the run refuses having called
no provider, spent nothing, and placed nothing.

**Step 12's two halves fail differently.** The commit itself can fail — a single-file destination
occupied by a directory, an unwritable parent, a filesystem error — and exits **10** having placed
nothing, restoring what it displaced (R67). The record write that follows cannot fail for want of
its directory, because step 2 established that the directory exists, so an asset does not commit
and then find nowhere to be recorded. What is left is the window between the two, which no ordering
removes: a kill in it leaves a committed asset described by the previous run's record entry
(R11, R53).

[PRD choice — an agent branches on the exit code, so the codes must not depend on ordering
luck.]

**R28.** Exit codes:

| Code | Means |
|---|---|
| 0 | Success |
| 1 | Usage — unknown command, wrong argument count, unknown option |
| 2 | Config — missing, unparseable, missing or unknown key, declared path absent, record's parent directory absent |
| 3 | Manifest — missing, unparseable, invalid or contradictory entry anywhere in the file (R34), including an illegal `type`/`operation` pairing (R36) and an output path that collides with, contains or sits inside another entry's (R63) |
| 4 | No entry by that name |
| 5 | Credential absent from the environment |
| 6 | Provider — request rejected, prediction failed or canceled, malformed response, or transport failure (R32, R33, R75) |
| 7 | Check failed — anything in R71's list, including a frame whose pixel size is not the declared `frame_size` |
| 8 | Refused — output already exists (R18) |
| 9 | Busy — another run holds the run lock (R72) |
| 10 | Destination — the output could not be placed where the entry declared it: the result passed its checks and the commit rename failed (R67), or a directory on the way to it could not be created because a file occupies that path (R12) |
| 11 | Internal — an unexpected failure; the JSON document is printed anyway (R4) |
| 12 | Extraction — the source video could not be read or decoded (R74) |
| 13 | Record — the record file exists and cannot be read as a record (R76); deleting it is the remedy |

**A local operation's failure and a provider's failure are never the same code.** Extraction
failing and a Replicate call failing both happen at R27's step 10, and reusing one code for both
would leave an agent parsing `message` to tell them apart — which the design doc's requirement
that an error says "what failed and what to change" (§ A CLI, driven by an agent) does not
survive. The remedies differ: a failed prediction is worth retrying unchanged, an unreadable
source video needs the file fixed and will fail identically forever.

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

**Waiting is for a prediction that says it is still running, never for a response the framework
cannot read.** The two are different things and are handled differently:

| The response's status | What the framework does |
|---|---|
| A known in-progress status — `starting`, `processing` | Poll again, indefinitely, per the paragraph above |
| A known terminal status — `succeeded`, `failed`, `canceled` | Stop; succeed, or exit 6 with the provider's error text (R33) |
| **Absent, or a value not in either set** | **Malformed response — fail immediately, exit 6** |

A malformed response fails on its **first occurrence**, not after any number of attempts, and its
`message` names the status value seen, or says the response carried no status at all. There is
nothing to wait for: a response the framework cannot read is not evidence that work is underway,
and polling it again asks the same unanswerable question.

**No attempt cap is introduced, and none may be**, in this requirement or in any implementation
of it. A cap on attempts is a timeout on legitimate work wearing different clothes — the run it
would end is a real prediction reporting real progress, which the paragraph above rules out.
Treating an unreadable status as "not finished yet" is what makes a cap look necessary, and
failing on it directly is what removes the need. Left alone, the loop waits forever holding the
run lock (R72), and every later run exits 9 until someone kills the process.

The status sets are named here rather than left open because "known" has to be decidable for the
malformed case to exist at all. A status the provider adds later therefore fails loudly instead
of hanging, and adding it to the in-progress set is a one-line change behind the provider
boundary (R75). That trade is deliberate: an unrecognised status is either a hang no agent can
diagnose or an error one can read, and the error is worth more. [PRD choice — the design doc
settles nothing about polling; the sets are Replicate's own.]

**R33.** A failed or canceled prediction exits 6 with the provider's own error text in
`message`. The full provider response is not written to any file and is not printed to stdout.
[§ Regenerating, and leaving nothing behind — "no response dumps"]

### The manifest

**R34.** The manifest is a YAML file holding a list of entries, one per asset. The framework
reads it and **never writes it** — no command creates, edits, reorders, formats or appends to
the manifest. [§ One script, per-asset inputs are data]

**The whole manifest is validated, never just the entry named on the command line.** Every command
that reads the manifest validates **every** entry in it, in manifest order, and exits 3 at the
first invalid or contradictory one — whether or not that is the entry being asked for. This is not
thoroughness for its own sake: the rules that matter most are cross-entry, and none of them can be
checked by looking at one entry. A duplicate `name` (R37) is a property of a pair, and so is every
containment rule on claimed directories (R63). `agf generate a` therefore exits 3 when entries `b`
and `c` collide with each other and `a` itself is faultless. [PRD choice]

**R35.** An entry is exactly one step: one provider call, or one of the two local operations.
The framework holds no notion of a multi-step asset, does not sequence entries, does not
resolve dependencies between them, and does not know that one entry's input file was another
entry's output. Rerunning an entry never cascades to any other. [§ One entry is one step]

**R36.** Two fields describe an entry. `type` says what the asset **is**; `operation` says how
it is **produced**. They describe different things, but they are **not independent**: the
operation constrains which types are legal, because each local operation produces exactly one
kind of thing.

| `operation` | Legal `type` |
|---|---|
| `assemble_sheet` | `sprite_sheet` only — assembling frames produces a sheet and nothing else (R60) |
| `extract_frames` | `image` only — pulling frames out of a video produces images and nothing else (R62) |
| `model` (the default) | any of the five — a model call can return any kind of asset |

**Any other pairing exits 3**, naming the entry, its `type` and its `operation`. Reason for
failing rather than ignoring the mismatch: `type: video` with `operation: assemble_sheet` is an
entry whose author meant something the framework cannot do, and every downstream rule — which
fields are legal (R37), which geometry is required (R44), which checks run (R71) — would
otherwise be applied to a combination nobody specified.

Given a legal pairing, each per-field rule below keys on one of the two fields, and which one is
never arbitrary:

- **Fields about the call key on `operation`** — `model`, `prompt`, `prompt_key`, `inputs`,
  `input_files`, `frames`, `source`. A step that makes no model call must not name a model, and
  a step that makes one has no local `frames` to assemble (R37, R38).
- **Geometry keys on `type`** — `frame_count`, `frame_size` and `layout` are required on every
  entry whose output **is** a sprite sheet, whichever path produced it (R44).

A sprite sheet arrives either from a model or from `assemble_sheet`; which one it was decides
which call fields are legal, and does not change the fact that the thing produced is a sheet
with a declared shape.

| Field | Required | Meaning |
|---|---|---|
| `name` | yes | Unique across the manifest; the argument every command takes |
| `type` | yes | One of `image`, `sound`, `music`, `sprite_sheet`, `video` — what the entry produces |
| `operation` | no | `model` (default), `assemble_sheet`, or `extract_frames` |
| `model` | `model` only | Replicate model id, e.g. `owner/name` — see R38 |
| `prompt` | `model` only | The text prompt, if the model takes one — see R41 |
| `prompt_key` | `model` only | Provider input key the prompt is sent under; default `prompt` (R41) |
| `output` | yes | Exact output filename relative to `drafts`, or a template for `extract_frames` (R63) |
| `format` | yes | Declared file format, checked against the bytes |
| `inputs` | `model` only | Map of arbitrary model inputs, passed through untouched |
| `input_files` | `model` only | Map of input names to file references (R42) |
| `frame_count`, `frame_size`, `layout` | see R44 | Sheet geometry, keyed on `type` |
| `frames` | `assemble_sheet` only | Ordered list of file references |
| `source` | `extract_frames` only | File reference to the video |

"`model` only" means the field is rejected on `assemble_sheet` and `extract_frames` under R37 —
a local operation has no provider to send an input to, so a `model`, `prompt` or `inputs` on one
is a mistake being made silently, not a harmless extra.

[§ One script, per-asset inputs are data; § Choosing a model; § Filenames; § Format checking;
§ Sample images; § Sprite sheets; § One entry is one step] · field names are [PRD choice].

**R37.** A duplicate `name`, a missing required field, an **unrecognized field**, or a field
**not legal for the entry's `operation`** anywhere in an entry exits 3 naming the entry and the
field. A misspelled key is never silently ignored, and neither is a field that would have no
effect. [PRD choice — an ignored typo is a wrong asset generated with no signal.]

**R38.** `model` is required when and only when the entry's `operation` is `model` — a
provider call — and is then optional where the framework has a default for the entry's `type`.
On `assemble_sheet` and `extract_frames` it is neither required nor accepted: those operations
make no call, so naming a model exits 3 under R37. This keys on `operation`, not on `type`: an
entry with `type: sprite_sheet` and `operation: model` needs a model, and one with
`type: sprite_sheet` and `operation: assemble_sheet` must not name one.

For a `model` operation, version one has defaults for two types only:

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
to hold the prompt (§ The per-asset record) and so the framework must know which field it is.
The framework merges it into the inputs sent to the provider under the key given by
`prompt_key`, which defaults to `prompt`. A model that calls its prompt something else —
`text`, `description` — is served by the entry declaring `prompt_key: text`; the framework
still holds no knowledge of what the input means, only of which key carries it. An entry that
sets both `prompt` and an `inputs` key equal to its `prompt_key` exits 3, because which one
wins would otherwise be a silent guess.

The record holds `prompt` and `prompt_key` exactly as the entry declared them, with
`prompt_key` `null` when the entry omitted it (R47) — the framework records the declaration,
not the key it resolved to.

[PRD choice — the design doc requires the record to hold the prompt but says nothing about how
the prompt reaches a provider that names the field differently, and the alternative, making the
prompt an ordinary `inputs` key, would leave the framework unable to find it for the record.
Reversible: adding or renaming `prompt_key` breaks no manifest that omits it.]

**R42.** Values under `input_files`, and every element of `frames` and `source`, are **file
references** of the form `<root>:<relative path>`, where `<root>` is `samples`, `base` or
`drafts`. The framework resolves the reference against the corresponding config path. A path
string sitting in `inputs` is passed through as a literal string and is never treated as a
file. Reason for the explicit root token: with three roots, a bare relative path is ambiguous
and the resolution order would be a rule everyone has to remember. [§ Sample images; §
Providing base assets to build from; § One entry is one step — a later entry names an earlier
entry's output file] · syntax is [PRD choice].

**How a referenced file reaches the provider:** for an `input_files` entry, the framework
**uploads the file to Replicate's file endpoint and sends the URL that endpoint returns**,
under the key the entry named. It sends neither a base64 data URI nor a local path — a local
path is meaningless to the provider, and a data URI carries a size limit. [PRD choice — the
design doc requires reference images to be passed as inputs but does not say in what encoding.
The reason to pick the upload: passing reference images is version one's entire mechanism for
artistic consistency (§ Artistic consistency), so the encoding has to keep working at the sizes
real reference art arrives in, which is exactly where a data URI stops. Reversible — no calling
project exists yet, and the choice is invisible to the manifest either way.]

`frames` and `source` are consumed by local operations and are never uploaded anywhere; they
are read from disk.

**R43.** A file reference naming a root that is not declared in `assetgen.yaml`, or a file that
does not exist, exits 3 naming the reference and the missing config key or path. [PRD choice]

**R44.** The geometry fields are `frame_count` (integer), `frame_size` (`[width, height]` in
pixels) and `layout` (`{columns, rows}`). `frame_size` is the only name for a frame's
dimensions anywhere in this PRD — there is no `frame_width` or `frame_height` field. They are
keyed on `type`, never on `operation`:

The table covers **every legal `type`/`operation` pairing and only those** — an illegal pairing
has already exited 3 at R36 and never reaches a geometry rule:

| `type` | `operation` | `frame_count` | `frame_size`, `layout` |
|---|---|---|---|
| `sprite_sheet` | `assemble_sheet` | required | required |
| `sprite_sheet` | `model` | required | required |
| `image` | `extract_frames` | optional (R64) | rejected |
| `image`, `sound`, `music`, `video` | `model` | rejected | rejected |

All three are required on every entry whose output **is** a sheet, whether that sheet is
assembled locally or returned by a model, and R57 checks the sheet against them on both paths.
Requiring the declaration on the model path is what makes as much of the design doc's check as
version one delivers possible at all: "A returned sheet is checked against the layout its entry
declared… this matters most on the pixel-art path, where the model does its own framing"
(§ Sprite sheets). The pixel-art model frames the sheet itself, so an entry that declared
nothing would leave nothing to check the result against, and the check could not exist at all.
What the check does and does not catch is stated in R57.

`extract_frames` lays nothing out, so `frame_size` and `layout` on one exit 3 under R37, while
its `frame_count` is legal, is not sheet geometry, and means what R64 says. Geometry on any
other legal entry exits 3 under R37 — a field that would have no effect is a mistake being made
silently.

**Every geometry value is positive.** `frame_count`, both elements of `frame_size`, and
`layout`'s `columns` and `rows`, must be integers **greater than zero**; zero or negative exits
3 at manifest validation, like any other invalid entry, naming the entry and the field. This
holds wherever the field is legal, so it covers an `extract_frames` entry's `frame_count` (R64)
as well as a sheet's, even though that one is not sheet geometry. Reason: no image of zero or
negative extent can be constructed and no video yields a negative number of frames, so an
unchecked `frame_size: [0, 0]`, `frame_size: [-32, 32]` or negative column count reaches image
construction and surfaces there as an unexpected internal failure (exit 11) — which tells an
agent only that something went wrong, about an entry whose mistake was visible in the manifest
all along. A negative `frame_count` is worse for being quieter: `columns × rows < frame_count`
is false for every negative, so it passes the rule below, and it is then caught only by luck
where the frame list happens to disagree with it (R61), or on the extraction path not until the
entire video has been decoded and the count check fails at exit 7 (R64). [PRD choice]

`columns × rows < frame_count` exits 3. Frames are ordered row-major: left to right, then top
to bottom. Where `columns × rows > frame_count` the leftover cells are **fully transparent** —
the sheet is still the full `columns × rows` grid, not cropped to the last frame, because the
caller declared the layout and a consumer indexes cells by it. [§ Sprite sheets — "How many
frames, what size, and how they are laid out are per-entry data the calling project writes";
"every frame is PNG with alpha"; "A returned sheet is checked against the layout its entry
declared"] · row-major, the field shapes and the transparent fill are [PRD choice]; both
readings of ordering and of leftover cells are reasonable, so they are stated rather than left to an implementer.

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
    "model": null, "model_version": "sourceful/riverflow-2.0-pro:0e9f…",
    "prompt": "…", "prompt_key": null, "seed": 42,
    "inputs": {…}, "input_files": {"image": "samples:hero.png"},
    "output": "…", "format": "png",
    "frame_count": null, "frame_size": null, "layout": null,
    "frames": null, "source": null}}}
```

**The record holds what the manifest declared, plus exactly two resolved values, and nothing
else** — never what was sent to the provider. `model`, `inputs`, `input_files`, `prompt`,
`prompt_key`, `output`, `format`, `type`, the geometry fields (R44), and `frames` and `source`
on a local operation (R51) are the entry's literal declarations, copied as written. In
particular a file reference is stored as **the reference string the entry wrote** —
`samples:hero.png` — never the resolved path, never the uploaded URL (R42), and never the
file's contents or an encoding of its bytes. `output` is the declared filename or template, not
an expansion of it.

**The key set is closed, and stated here so a test can compare against it.** A record entry's
keys are **exactly** these sixteen, on every entry the framework writes, whatever its `type` and
`operation`:

`operation`, `type`, `model`, `model_version`, `prompt`, `prompt_key`, `seed`, `inputs`,
`input_files`, `output`, `format`, `frame_count`, `frame_size`, `layout`, `frames`, `source`

Every one is present every time, carrying `null` where the entry declared nothing, where no
resolved value exists (R50), or where the field is not legal for the entry's `operation` at all
(R51) — so a `model` entry records `frames: null` and `source: null`, and an `assemble_sheet`
entry records `model: null` beside its declared `frames`. A test states it directly:
`set(entry.keys()) == {…}` for every entry in the file.

**Any other key appearing in a record entry is a defect**, not a harmless extra: no third
resolved value, no timestamp, no part of a provider response, no field the framework invented.
Stating the set closed rather than "the declarations plus two values" is what makes that
assertable — the open phrasing can only be checked one key at a time, which is satisfied by an
entry that carries the right fields *and* the whole provider payload beside them, exactly what
R31 and R33 forbid everywhere else. It is the same fixed-key-set trade R71 makes for `checks`.

`model` is the declared model id and is **`null` where the entry named none** — as in the
example above, where a default applied. Recording the declaration next to the resolved
`model_version` is what lets a reader see that a default was in play at all: a `null` `model`
beside a pinned `model_version` says the framework's default for the type supplied it, which is
the same fact `agf list` surfaces as `model_source: default` (R15). Without the declared field
the record could not distinguish that from an entry that named the model itself.

**No timestamp is recorded.** The design doc enumerates what an entry holds — pinned model
version, prompt, inputs, and the seed where there was one (§ The per-asset record) — and a time
is not among them, nor is it something the next request is a change *from*. Recording one would
also be the third resolved value this requirement forbids.

The two resolved values are `model_version` (R49) — the pinned version the provider actually
ran — and `seed` (R50) when the model returned one the entry did not declare. Both are there
for the same reason: **they are what you would need to ask for this again, and neither can be
read off the manifest.** An entry may name a bare `owner/name`, so the pinned version exists
only at call time; a returned seed exists nowhere in the manifest at all. The design doc names
both cases directly — "the pinned model version, the prompt and the inputs that produced the
asset, plus the seed when there was one — the entry declared it or the model returned it"
(§ The per-asset record). Where the entry declared the seed itself, the recorded `seed` is that
declaration like any other field. No third resolved value is ever recorded.

Reason: the record exists so the next request can be a change from the last one, and it is
"contained and trashable" — one small file. What a change is made *from* is the declaration a
person wrote and will edit; a provider payload with megabytes of encoded reference art inlined
is neither what they would edit nor something a trashable file should carry. [§ The per-asset
record] · JSON, the single-file shape, the `version` key and the field names are [PRD choice].
JSON rather than YAML because this file is machine-written and read back through `agf record`;
hand-editing it is not a use it needs to invite.

**R48.** The record holds **one entry per asset, the last generation only**. Regenerating
replaces that entry in place. Nothing appends, and no history, previous value or timestamp
series is retained anywhere. [§ The per-asset record]

**R49.** `model_version` is always the **pinned** version — the full `owner/name:version`
identifier the provider actually ran — never a bare model name. An entry whose `model` names
no version is resolved to a pinned version at call time and the pinned value is what is
recorded. [§ The per-asset record — "The model version is always pinned… which is the whole
reason the record is worth keeping"]

**R50.** `seed` records the seed the entry declared in its inputs, or the seed the provider
returned where the entry declared none — the second of R47's two resolved values — and is
`null` where neither exists. The framework never invents a seed, because injecting one would be
the framework authoring an input that belongs to the manifest. An entry that wants a
reproducible seed declares it. [§ The per-asset record — "the entry declared it or the model
returned it"; § One script, per-asset inputs are data — "it invents nothing that belongs in
it"] · the `null` case is [PRD choice].

**R51.** A local operation gets a record entry like any other, with `model`, `model_version`,
`prompt`, `prompt_key`, `seed` and `inputs` all `null` — R38 and R36 make those fields illegal on one, so
there is nothing to record. `frames` and `source`, which a local operation does declare, are
recorded as the reference strings the entry wrote (R47). [PRD choice — the record's purpose is
knowing what produced the asset, which applies equally.]

**R52.** The framework never prunes the record. An entry for a name no longer in the manifest
stays. Deleting the whole file is the supported reset. [PRD choice — the design doc says the
record is "contained and trashable" and holds the last generation per asset, but says nothing
about entries whose manifest entry has gone. Keeping them is chosen because pruning would make
`agf record` destructive as a side effect of an unrelated manifest edit, and because a rename
in the manifest would silently discard what the old name was last asked for. The cost is a
record file that grows monotonically until someone deletes it, which the doc already blesses.
Reversible: adding a prune later is additive.]

**R53.** The record is written only after the asset is in its final place, and is not touched
at all when a run fails for any reason.

**The record is replaced, never edited in place.** The framework writes a **complete new copy**
of the whole record — every entry, with this run's entry replaced — to a temporary file named
`.agf-tmp-<run id>` in the record's own directory, so the rename is within one directory and on
one filesystem, and then **renames that file onto the record path**. It never truncates
the record and never appends to it. A run killed at any moment during the write therefore leaves
the previous record whole: either the rename has happened and the record is the new one, or it
has not and the record is the old one. Nothing in between is reachable.

**What is not guaranteed is that the asset and its record change together.** They are two files in
two directories, and one rename cannot cover both. A run killed between the commit (R67) and this
rename leaves a whole new asset beside the previous run's whole record entry — a stale description,
never a torn file — and the next run of that entry closes it (R11).

This matters more here than anywhere else the same technique is used. The record holds every
asset's provenance, not one asset's, so a truncated write loses what every other entry was last
asked for; and `record` and `list` take no lock and are never blocked (R72), so a half-written
record is a file another invocation can read while it is being written. The temporary file is a
file the run creates and does not leave behind, which is what R66 constrains.

[§ Regenerating, and leaving nothing behind — "A run that dies partway leaves the tree as it was
rather than leaving a truncated file behind"] · the write-new-and-rename mechanism is [PRD
choice], recorded because a plain in-place write silently breaks that guarantee.

**R76.** **A record file that exists and cannot be read as a valid record exits 13, and the error
says the file may be deleted.** That is the whole test, stated structurally rather than as a list
of shapes: **whatever prevents the file being read as a record puts it on this path**, and none
of them is ever an unexpected internal failure. Existing and unreadable is a different case from
not existing at all, which is a legitimate "never generated" and exits 0 (R25).

The forms this takes are **illustrative, not exhaustive** — the file does not parse as JSON, it
is empty, its top level is not an object, its entries collection is missing or is not an object,
or an individual entry under it is not an object. Enumerating shapes is how the next shape gets
missed, and a shape missed here is a crash rather than a stated failure, which is exactly what
this requirement exists to remove. Every one of them exits 13, is detected at the same step
before anything is committed or spent, and carries the same remedy below.

**Every command that reads the record is subject to it** — `list`, which reports `has_record`
(R15); `record`, which prints the stored entry (R25); and `generate` and `regenerate`, which
replace an entry in it (R53). One unreadable file, one code, whichever command met it.

**It is detected before anything is committed**, at R27 step 5: before the manifest is read,
before the credential is checked, before any provider call, and before any staging directory
exists. Nothing is asked of Replicate and nothing lands in `drafts`. The failure this ordering
exists to prevent is an asset committed to the drafts area with no record entry describing it —
the run would place the file and then discover, at the write, that the record could not be read
in order to be replaced. R11 already rules out the neighbouring failure of a record that could
never be written *for want of its directory*; this rules out the one where the directory is
there and the file in it is rubble.

**The error names the remedy, and the remedy is deletion.** `message` names the record's path
and what is wrong with it; `remedy` says the file can be deleted, and that doing so costs the
ability to tweak from the last request and nothing else. That sentence is what makes this an
error an agent can act on rather than one it can only report: the design doc settles that the
record is "contained and trashable: one file the framework owns… Deleting it costs the ability
to tweak from the last request, and nothing else" (§ The per-asset record), so the safe remedy
already exists and only needs saying. **The framework never deletes or repairs the record
itself**, and never writes over one it could not read — that is a person's call about their own
provenance, and a tool that silently discarded it would be indistinguishable from the bug.

[§ The per-asset record — "contained and trashable"; § A CLI, driven by an agent — "errors that
say what failed and what to change"] · the exit code and the placement in R27's order are [PRD
choice]. Without it every unreadable record is an unexpected internal failure (exit 11, R4),
which tells an agent only that something went wrong; and on `generate` the asset commits first
and the failure lands after it, leaving the asset and its provenance permanently divergent with
nothing to restore from.

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
image's pixel dimensions must equal exactly `columns × frame_size[0]` by `rows ×
frame_size[1]`. A mismatch exits 7 stating both the declared and the actual dimensions, and the
sheet is not committed. This matters most on the pixel-art path, where the model does its own
framing. Every `sprite_sheet` entry declares its geometry (R44), so this check runs on both
paths and is never skipped for a sheet; it records `skipped` only on an entry that is not one.

**What this check cannot see.** It compares pixel dimensions and nothing else. A returned sheet
of exactly the declared size, laid out on the declared grid, but with fewer frames actually
drawn in it — say eight frames of art and four blank cells where twelve were asked for — passes
this check. The design doc treats a returned frame-count mismatch as unacceptable ("A model that
returns a different frame count or framing than was asked for is a mismatch, not a result to
accept", § Sprite sheets), and a dimensions comparison cannot deliver that half of the promise:
telling a drawn frame from an empty or duplicated cell is image analysis the framework does not
do. Version one detects the framing mismatch and not the count mismatch, and this is stated
rather than implied — a check that quietly covers less than the doc promises is worse than one
that says what it is blind to. On the `assemble_sheet` path the count is not at risk, because
the frames are counted from the entry itself (R61). [§ Sprite sheets]

**R58.** Sprite-sheet frames are PNG with alpha. An `assemble_sheet` entry whose frames are not
PNG, or whose declared `format` is not `png`, exits 3. [§ Sprite sheets — "every frame is PNG
with alpha"]

**R59.** A provider that returns more than one output file for an entry declaring one `output`
exits 7, committing nothing. The framework never selects among returned files and never invents
names for the extras. [PRD choice — the design doc says the framework writes the name it is
told and never invents one (§ Filenames), which rules out naming the extras but does not say
what to do about them. Failing is chosen over taking the first: a model returning two images
means the entry asked for something other than what it declared, and silently keeping one
produces an asset nobody chose. Reversible — an entry-level way to say "take the first" is
additive and breaks no manifest.]

### Local operations

**R60.** `operation: assemble_sheet` performs no provider call. It **requires `type:
sprite_sheet`**, and an `assemble_sheet` entry declaring any other `type` exits 3 under R36 — a
sheet is the only thing assembling frames produces. It reads the files named in `frames`, in the
order given, and writes one sheet at `output` laid out per the entry's `frame_count`,
`frame_size` and `layout` (all three required here, per R44). [§ Sprite sheets — "Assembling
those frames into one sheet is likewise the framework's own work, not a Replicate call"]

**R61.** `assemble_sheet` rejects frames it would have to alter, and never scales, crops or
pads one to fit. The two failures land at different stages because they are detectable at
different times, and R27 fixes which code each gets:

| Failure | Detected | Exit |
|---|---|---|
| `len(frames) != frame_count` | From the entry alone, at manifest validation | 3 |
| A frame's pixel size differs from `frame_size` | Only by opening the file, during the operation | 7 |

The second is a check like any other in R71, reported as `frame_size: "fail"` naming the frame,
its actual size and the declared one — on the sheet's own `checks` object, the sheet being the
entry's only output (R71). [PRD choice — silently resizing a frame produces a
plausible-looking wrong sheet; the split follows R27's stage-to-code table rather than
inventing a code.]

**R62.** `operation: extract_frames` performs no provider call and shells out to no external
binary. It reads the video named by `source` and writes its frames into `drafts`. It **requires
`type: image`**, and an `extract_frames` entry declaring any other `type` — `sprite_sheet` above
all — exits 3 under R36: images are what it produces, and the sheet, if there is to be one, is a
later `assemble_sheet` entry's output (R65). The decoding of the video itself happens behind the
boundary R74 names and nowhere else; everything the framework does with the frames that come back
is its own work. [§ Sprite sheets — "Extracting frames is local
image handling the framework does itself, not a Replicate call"; ffmpeg is named there as a
dependency this project does not have]

**R63.** For `extract_frames`, `output` is a filename template containing exactly one `{n}`
placeholder in Python format-spec syntax, e.g. `frames/walk_{n:03d}.png`. Frames are numbered
from 1 in video order. A template with zero or more than one placeholder exits 3.

**The placeholder must produce decimal digits, and its format spec is validated.** The spec is
empty (`{n}`), `d` (`{n:d}`), or a zero-padded width followed by `d` (`{n:03d}`), and nothing
else. Any other spec — a float such as `{n:.2f}`, a string or character such as `{n:s}` or
`{n:c}`, a space-padded width such as `{n:3d}`, or one carrying a fill, alignment, sign or
thousands separator — **exits 3**, naming the entry and the spec.

The reason is the collision check: R18 matches a placeholder against **one or more decimal
digits** and the literal text around it, so a spec that produces anything else does not merely
look unusual, it silently defeats that check. `{n:.2f}` writes `walk_1.00.png`, which no digit
match can find, so a second `generate` is not refused, the destination directory is replaced
whole (R67), and `list` reports the drafts as absent while they sit on disk — the mixed frame
sets R18 exists to prevent, with nothing downstream to signal it. The specs that cannot format an
integer at all fail differently and no better: they raise while the frames are being named, after
the entire video has already been decoded, and surface as an unexpected internal failure (exit
11). Validating the spec at manifest validation refuses both classes before anything is read,
called or written, and is what keeps R18's match and the names a run actually writes the same
set. [PRD choice — the design doc settles nothing about the template's syntax; the restriction
follows from R18 rather than from taste.]

**The template must name a subdirectory under `drafts`, and this is validated.** A template
whose files would land directly in the drafts area — `walk_{n:03d}.png`, with no directory
component — **exits 3**, naming the entry and saying that a multi-file entry must write into a
directory of its own. The reason belongs in the requirement, because the rule looks like fussy
tidiness and is not: the commit replaces the destination **directory whole** (R67), so that
directory has to belong to one entry and nothing else, and the drafts area itself never does.
Without this rule, committing one `extract_frames` entry would replace the drafts area — every
other entry's drafted assets — in a single rename.

**No two entries' outputs may nest, in either direction.** The directory a template names is
*claimed* by that entry. Across the whole manifest (R34), and at the same validation stage:

- No claimed directory may **be**, **contain**, or **sit inside** another claimed directory, at any
  depth.
- No single-file entry's `output` may sit inside any claimed directory, at any depth.
- No single-file entry's `output` may **be**, **contain**, or **sit inside** another single-file
  entry's `output`. Two entries declaring `a.png` is the equality case; `a.png` against
  `a.png/b.png` is the containment one, where the second entry needs a directory at the very path
  the first declares as a file. Comparing these two only for equality is what leaves the second
  validating and then failing at commit, exit 10, after a provider call has already been paid for
  — a manifest mistake reported as a filesystem obstruction.

Any of these exits **3**, naming both entries and both paths. One containment rule rather than a
list of collisions, because the list kept missing cases and every one of them is the same
mistake — the file-versus-file case above is exactly what an equality comparison keeps missing.
Two entries claiming `frames` is the obvious one. `frames` against `frames/run` is the one that looks
harmless and is the worst of them: committing the outer entry replaces `frames` whole, taking the
inner entry's already-committed frames with it, and then deletes the displaced copy — so the sweep
has nothing left to restore from and the work is simply gone. A single file sitting inside a
claimed directory disappears the same way, with nothing downstream to signal it.

A claimed directory therefore belongs to **this entry alone**. That is what makes replacing it
whole safe, and the consequence is the intended behaviour rather than a side effect: a run that
writes nine frames where twelve were written before leaves nine, not nine plus three stale ones.
A frame from a previous run sitting alongside a fresh set is the worse failure of the two,
because nothing downstream catches it — the `assemble_sheet` entry that consumes the directory
would simply produce a wrong sheet, and it would look like a real one.

[PRD choice — it keeps R45's "never invents a name" true for a step that writes many files, and
sole ownership of the directory is what makes replacing it whole safe.]

**R64.** `extract_frames` accepts an optional `frame_count`, which is legal here and means the
number of frames the video is expected to yield: when present, a video yielding a different
number exits 7 and nothing is committed; when absent, every frame is written. Nothing about
this is sheet geometry — an `extract_frames` entry produces images, not a sheet (R62), and this
field counts what came out of a video rather than describing a layout. It accepts neither
`frame_size` nor `layout` (R44). [PRD choice]

**R65.** The framework never delivers a sprite sheet as loose numbered frames. Frames written
by `extract_frames` are the output of that entry; the sheet is the output of the
`assemble_sheet` entry that consumes them. [§ Sprite sheets]

### Cleanliness

**R66.** **Cleanliness is a property of what a run leaves behind, not of what it may create while
it runs.** Once
a run has ended — cleanly, in failure, or killed — the only things it has added to the calling
project are the files its entry declared, the record, and the intermediate directories under
`drafts` its own `output` named (R12). Nothing else remains: no scratch script, no response dump,
no log, no half-written asset, no partially-committed file set, and no staging directory, marker or
displaced copy left over from a commit.

Temporary files during a run are not merely allowed but **required**, and they are how the two
guarantees below are delivered: the staging directory, its marker and the displaced copy that make
a commit atomic (R67), and the temporary copy the record is written to before being renamed into
place (R53). Forbidding those would forbid the only safe way to write anything here. What R66 says
is that none of them is still there afterwards, and a run that could not remove its own — because
it was interrupted, or because the removal itself failed (R67) — is repaired by the next run's
sweep (R69).

The **lock file is the one thing that persists between runs and is not cleaned up**, by design:
it is created once and never deleted, because deleting a lock file is itself a race (R72). It
holds no content, and one lying there unheld blocks nothing.

[§ Regenerating, and leaving nothing behind — "A run leaves the drafted assets and one record,
and nothing else… A run that dies partway leaves the tree as it was rather than leaving a
truncated file behind"] · the restatement in terms of what remains, and the lock-file exception,
are [PRD choice]; R72 gives the race that makes the exception necessary.

**R67.** **An entry commits every file it produces or none of them.** A run that dies partway
leaves the tree as it found it, and that holds for twenty-four extracted frames exactly as for
one image.

**Staging is flat, and does not mirror the destination.** A run stages into one directory,
`.agf-tmp-<run id>`, created inside the drafts area — specifically in the **parent directory of
what it will commit**, so the staging directory is a sibling of the destination and the commit is
a single rename within one parent. Files are written into it under their **final basenames
only**: a template `frames/walk_{n:03d}.png` stages `walk_001.png` directly inside the staging
directory, never `frames/walk_001.png`. Staging the relative path instead of the basename is the
error to avoid — renaming such a directory onto the destination nests the committed files one
level deeper than the entry declared.

**Each run writes a marker beside its staging directory, never inside it.** The marker is a file
named `.agf-tmp-<run id>.json`, a **sibling** of the staging directory — same parent, inside the
drafts area. Its name begins with `.agf-tmp-`, so R70's existing reservation already covers it and
no second prefix is reserved.

Beside rather than inside, because the commit renames the staging directory onto the destination
whole. A marker inside it would arrive in the committed destination as a framework file among the
entry's declared outputs, and getting it back out would mean deleting a file *inside* a committed
destination — an unlisted step in a window the sweep does not cover.

**The marker is JSON with exactly two keys**, both paths relative to the drafts area:

| Key | Holds |
|---|---|
| `destination` | The path this run is building — the directory a template claims (R63), or the single file an ordinary entry declares |
| `displaced` | The path of the displaced copy, `.agf-old-<run id>`, this run will move an existing destination directory to |

Both values are written when the staging directory is created, **before anything is staged and
before any rename**, and **neither is ever updated afterwards**. The run id is known up front, so
`displaced` is recorded whether or not anything is ever displaced, and nothing has to be appended
mid-commit. That is what lets a later sweep repair an interrupted run **from the marker alone,
without reading the manifest** (R69, R27). The marker is written whole and flushed before the run
proceeds, which is what makes an unreadable marker mean "no rename had happened yet" (R69).

**The marker records no kind field.** It does not say whether `destination` is a directory or a
file, and nothing needs it to: R69 classifies from what is on disk. Two paths are the whole
contents.

**The marker is never a staged file.** It sits outside the staging directory, so it is not one of
the entry's declared outputs: no check in R71 ever runs against it, it never counts toward
`output_count` (R59), and it never appears in a result document's `output` list (R19). Nothing
enumerates the staging directory and reports it with a byte count or a failed format check.

**Its fate.** The commit removes it as its last step, below. The sweep removes it in every case
where the sweep touches the run it belongs to, whether that run is restored or discarded (R69). No
committed destination ever contains one, which follows structurally from its sitting outside the
directory that gets renamed.

**The commit is: displace, then rename, then delete.** Exactly these steps, in this order:

1. All checks (R71) run against the staged files. Nothing below happens if one fails (R68).
2. **Multi-file entry only** — if the destination directory exists, it is renamed to
   `.agf-old-<run id>`, a sibling of the staging directory.
3. The staging directory is renamed onto the destination — **a single rename onto a path that
   does not exist**, because step 2 has just vacated it. For a single-file entry, this step is
   instead the one staged file being renamed onto its declared path, which is atomic whether or
   not a file was there.
4. The displaced copy, if there is one, is deleted.
5. Anything left of the staging directory — for a single-file entry, the now-empty directory — is
   removed.
6. **The marker is removed last**, once everything it accounts for is gone.

**The marker goes last, and steps 4–6 stop at the first failure rather than skipping ahead.** The
marker is what lets the sweep account for a staging directory or a displaced copy, so nothing it
names may outlive it. That ordering is what makes R69's rule about an unaccounted `.agf-old-*`
directory safe.

**Steps 2 and 3 can fail.** A single-file destination occupied by a directory, an unwritable
parent, a filesystem error — the rename is not guaranteed to succeed just because the checks
passed. A failure at either exits **10**, having committed nothing: the run renames the displaced
copy back if it made one, then removes the staging directory and the marker, leaving the
destination exactly as it found it, as R68 does for every other pre-commit failure. The error's
`message` names the destination and what the filesystem said; `remedy` names the obstruction.

**A failure in steps 4, 5 or 6 is not a commit failure.** The destination is already in place by
then, and reversing it would be the destructive act, not the safe one. The run stops the cleanup
where it failed, leaves the remainder for the sweep (R69), writes the record, and exits 0. What is
left behind is by definition still accounted for by a marker, because the marker is removed last.

**The destination is never written into incrementally.** No file the entry produces is ever
written, renamed or deleted inside the destination directory: the only thing that ever touches
it is a whole-directory rename. An N-step rename that can be killed after frame nine of
twenty-four never happens, and neither does a partial overwrite of a previous frame set.

Staging inside `drafts` rather than the system temp directory is deliberate: a same-filesystem
rename is atomic, and a cross-device copy is not, so a process killed mid-write can never leave a
truncated file at a declared path. [§ Regenerating, and leaving nothing behind — "A run that dies
partway leaves the tree as it was rather than leaving a truncated file behind"] · the staging
layout, the marker and the reserved prefixes are [PRD choice], with the reasons recorded because
a cross-device copy, a per-file rename, or a nested staging layout each silently breaks the
guarantee.

**R68.** A run that exits for any reason before committing — a failed check, a provider error, a
failed commit rename (R67), an interrupt — removes its staging directory and everything in it, and
then its marker, in that order and for the same reason the commit removes the marker last. The
declared output is untouched: absent if it was absent, unchanged if it existed, and for a
multi-file entry that means every one of the previous files is unchanged, not some of them. A run
killed so abruptly that it cannot do this leaves the staging directory and the marker for R69.
[§ Regenerating, and leaving nothing behind — "A run that dies partway leaves the tree as it was"]

**R69.** `generate` and `regenerate` sweep before doing anything else, at R27 step 4 — after
config validation, because the drafts area is named by the config, and after the lock, because a
live concurrent run's staging directory is not debris (R72). **The sweep reads the config and the
markers and nothing else** — never the manifest, which may no longer parse, no longer hold the
entry that was interrupted, or no longer declare the same `output`.

It scans `drafts` recursively for the two reserved prefixes and reads every marker it finds
(`.agf-tmp-<run id>.json`, R67) before acting on any of them. **A marker, not a staging directory,
is what anchors a run's repair**: the commit renames the staging directory away, so a run killed
just after that rename is represented on disk by its marker alone.

**The sweep classifies from on-disk state, never from a field in the marker.** The marker supplies
two paths and nothing else — it does not say whether the destination is a directory or a file, and
it does not record how far the commit got. Both are read from what is actually there. For each
marker, with `destination` and `displaced` resolved against the drafts area:

| Destination | Displaced copy | What the sweep does |
|---|---|---|
| Missing | Present | Rename the displaced copy back onto the destination |
| Present | Present | Delete the displaced copy |
| Present or missing | Absent | Nothing to restore and nothing to delete |

Then, in every row: remove the staging directory if it is still there, and **remove the marker
last**.

The first row is the only repair, and it is the one that matters — a multi-file run killed between
displacing the previous frame set and renaming the new one into place. The rest describe state
rather than diagnosing a history, deliberately: "destination present, displaced absent" is reached
by a single-file commit that finished, by a multi-file run killed before it displaced anything, and
by a run killed mid-staging with the previous asset sitting untouched at the destination. The
action is right for all three and the diagnosis would be wrong for two, so the table does not
attempt one. No marker field could tell them apart, which is why none is recorded.

**A staging directory with no marker** — a run killed between creating the directory and writing
the marker — holds nothing committed and is removed. So is one whose marker cannot be parsed: the
marker is written whole and flushed before any rename (R67), so an unreadable one means no rename
had happened.

**After** every marker has been processed, a `.agf-old-*` directory that **no marker points at** is
removed. A marker is always removed last (R67), so nothing it named outlives it, and a displaced
copy with no marker is therefore one whose run got past deleting everything the marker accounted
for. The order matters: a displaced copy is only unaccounted for once every marker that could
account for it has been read.

**The sweep never deletes a directory it cannot account for from a marker.** Specifically, it never
deletes a `.agf-old-*` directory whose marker shows the destination missing — that directory *is*
the previous frame set and gets restored, not removed. A sweep that deletes everything matching a
reserved prefix is how a cleanup destroys a frame set that was only displaced, and the marker is
what distinguishes the two cases.

**The sweep deletes nothing outside the two reserved prefixes.** It writes exactly one path that is
not reserved — the destination it restores in the first row, and only when that destination is
missing — and that write is a rename of a reserved path back into place. Nothing else outside
`.agf-tmp-*` and `.agf-old-*` is created, overwritten or removed.

The sweep also removes any leftover temporary record copy (R53) beside the record file, which
carries the same `.agf-tmp-` prefix. That directory is never inside `drafts` (R11), so the two
scans never overlap and a record copy is never mistaken for a marker. A process killed with a
signal it cannot handle is what leaves any of this behind, and sweeping at the next run is what
makes R66 true in that case too. [PRD choice]

**R70.** No path beginning `.agf-tmp-` or `.agf-old-` is ever reported by `list` as a draft,
accepted as an entry's `output` or template, or resolvable as a file reference; both prefixes are
reserved to the framework. **Two prefixes cover everything the framework writes under `drafts`** —
the staging directory, its marker and the displaced copy alike, because the marker's name derives
from the staging directory's (R67) and so falls inside the same reservation. No lock file appears
under `drafts` at all (R72), and R11 keeps the record and its temporary copy out of `drafts`
entirely, so there is nothing else to exclude. [PRD choice]

**R71.** A check has exactly three results — `pass`, `fail`, `skipped` — and the framework runs
exactly these checks:

| Check | Runs when | Fails when |
|---|---|---|
| `format` | Always (R54) | The bytes are not the declared format |
| `layout` | `type: sprite_sheet`, either path (R44, R57) | Sheet dimensions are not `columns × frame_size[0]` by `rows × frame_size[1]` |
| `frame_size` | `assemble_sheet` (R61) | A named frame's pixel size is not `frame_size` |
| `frame_count` | `extract_frames` with a declared `frame_count` (R64) | The video yields a different number of frames |
| `output_count` | A provider call (R59) | More than one file came back for one declared `output` |

`skipped` means the check did not apply to this entry — not that it was waived.

**Checks run against the entry's declared outputs and nothing else.** The run's marker (R67) is not
one of them: it sits outside the staging directory, so no enumeration of staged files reaches it,
and it is never format-checked, never counted, and never carries a `checks` object of its own.

**The key set is fixed: all five keys, always.** Every `checks` object carries `format`,
`layout`, `frame_size`, `frame_count` and `output_count`, on every file, in every success
document and every failure — a check that did not run is present with the value `skipped`, never
absent. The key set is therefore a constant an agent can assert against, rather than something it
has to derive from the entry's `type` and `operation`. A test can state it directly:
`set(checks.keys()) == {"format", "layout", "frame_size", "frame_count", "output_count"}` for
every file of every result.

**Checks whose scope is the entry appear on every file, with the same value.** `frame_count` and
`output_count` are properties of the run as a whole rather than of one file, and `layout` is a
property of the one sheet an entry produces; each is repeated identically on each file's object
rather than being hoisted to the top level. This is the same trade R19 makes for `output` always
being a list: one shape the agent parses everywhere beats a shorter document that branches.
`format` and `frame_size` are genuinely per-file and differ between files.

Every success document carries this object per file (R19), and a failure carries the same objects
in `error.checks` (R5) together with `error.code` 7, so an agent reads which check failed from a
field rather than from prose. The failing check's entry carries the declared and actual values.

**The failure path reports checks per file, in the same shape as the success path.**
`error.checks` is **always a list**, never a bare object, holding one element per file the entry
produced — the same files, in the same order, that the success document's `output` list would
have named had every check passed. Where the failure is that the file set itself is wrong
(`output_count`, R59), the list holds one element, for the entry's single declared `output`. Each
element has exactly two keys:

| Key | Holds |
|---|---|
| `path` | The path that file would have been committed to — the same path R19's `output` would have reported for it |
| `checks` | The object described above: all five keys, always |

`format`, `bytes` and `replaced` do not appear, because nothing was committed — there is no byte
count for a file that was thrown away and no file it replaced.

**The complete five-key set appears on the failure path too.** The checks that passed and the
checks that were skipped are present beside the one that failed; an object trimmed to only the
failing key is what must not happen, because then an agent parsing a result has two structures to
handle instead of one — the trade R19 already refused for `output`. Twelve frames failing on the
third are twelve elements, eleven of whose `format` keys read `pass`.

**A check on an entry's inputs reports on the entry's output.** `frame_size` on an
`assemble_sheet` entry inspects the frames the entry names as *inputs*, while the entry declares
exactly one `output` (R60). The aggregate result attaches to **that one output file's `checks`
object**: `pass` when every frame matched the declared `frame_size`, `fail` when any did not,
with the offending frame, its actual size and the declared one named per R61. Input frames are
files the run read, not files it produced, so no input frame ever appears as an element of
`output` (R19) or of `error.checks`.

[PRD choice — the design doc requires checks (§ Format checking, §
Sprite sheets) but says nothing about how a result is reported; an agent is the only caller, so
a parseable result is worth more than a sentence.]

**R72.** `generate` and `regenerate` hold one exclusive lock for the whole run, taken at R27
step 3 as a **kernel-level advisory lock** on a file named `<record filename>.lock`, in the
same directory as the `record` file. A second concurrent `generate` or `regenerate` exits **9**
immediately, naming **the lock file's own path** and the record it serialises — not the drafts
path, which is not what the lock is scoped to — and touches nothing. `list` and `record` take no
lock, write nothing, and are never blocked.

The lock exists because the sweep (R69) repairs and removes staging directories it does not own,
and two runs sweeping each other would destroy work mid-flight — which the sweep cannot
distinguish from cleaning up after a crash.

**The lock file is created once and never deleted.** What is acquired and released is the
advisory lock *on* the file, never the file itself: a run creates it if it is not there, locks
it, works, releases, and leaves it. No code path unlinks it.

The reason is the classic unlink race, and it belongs in the requirement because deleting the
file looks like tidiness. Unlinking a lock file that the holder still holds means a second run
can be waiting on — or holding — a lock against an inode that no longer has a name, while a
third run creates a fresh file at that name and locks that instead. Two runs then both believe
they hold the lock, and the single-writer guarantee this requirement exists to provide is gone.
A lock file lying there unheld blocks nobody (see below), so leaving it costs nothing and buys
the absence of that race. R66 accordingly does not require a run to clean it up.

**The lock file lives beside the record, not in `drafts`.** What makes drafting cheap —
generate, look, discard — is that "a run leaves the drafted assets and one record, and nothing
else" (§ Regenerating, and leaving nothing behind), and framework bookkeeping sitting in the
drafts area erodes exactly that. The record's directory is already framework-owned bookkeeping,
which is where a lock belongs, and R11 has already established that it exists. Naming the lock
after the record gives one lock per record, which is one per calling project — the scope being
serialised.

**The lock is released when the run ends**, on success and on failure alike. The file stays.

**A lock file left behind blocks nothing**, which is what makes leaving it free. The lock is held
by the kernel on an open file descriptor, not by the file's existence, so a process killed by a
signal it cannot handle releases it, and so does one that exited normally. The next run opens the
same file, finds no holder, and acquires it. **Busy is decided by trying to acquire the lock,
never by the file existing** — an existence check would let one killed process wedge the tool
until someone deleted the file by hand, and a run must not be blocked forever by a process that
no longer exists.

[PRD choice — the design doc neither requires nor forbids concurrent runs; refusing is chosen
over serialising because an agent that has to wait an unknown time for a generation it did not
start cannot tell that from a hang, whereas exit 9 is something it can act on. Reversible.]

**R73.** **One drafts area belongs to one config.** A config's `drafts` and `record` paths are a
matched pair: the drafts area a config names is swept by that config's runs and no others, and no
second config names the same drafts area alongside a different `record`.

This is stated as a requirement rather than left as an assumption because the sweep's entire safety
argument rests on it. The lock is scoped to the **record** (R72) while the sweep is scoped to
**drafts** (R69), and those are the same scope only while the mapping is one-to-one. Two configs
sharing a drafts area would take two different locks, so both could run at once, and each would
sweep the other's live staging directories and displaced copies as debris — precisely the
destruction the lock exists to prevent, with no lock standing in the way.

**The framework cannot detect a violation and does not try.** An invocation sees one config and has
no way to learn that another one, somewhere else, names the same directory. It is a constraint on
the calling project, written down so that nothing downstream is designed as though the sweep were
safe without it. [PRD choice — the design doc gives a calling project one drafts area and one
record (§ Drafts, then approval; § The per-asset record) and does not contemplate two configs; this
states the consequence of that shape rather than adding to it.]

### The extraction boundary

**R74.** Frame extraction is reached through **one named boundary and nowhere else**, and that
boundary is **substitutable**: a stand-in can be put in its place with no video file and no
decoder present, and everything else about the run stays real.

| | |
|---|---|
| Name | `agf.frames.extract` |
| Takes | the resolved path of the video the entry's `source` names (R42), and the entry's declared `format` |
| Returns | an ordered list of `bytes`, one element per frame, in video order, each already encoded in that declared format |
| Raises | `agf.frames.ExtractionError(message)` when the source cannot be read or decoded |

**Only the decoding sits behind it.** No other code path opens or reads a video. What
`extract_frames` does with what comes back is its own work and stays in front of the boundary:
writing each element into the staging directory under the basename the template gives it (R63,
R67), checking the bytes against the declared format (R54), counting them against a declared
`frame_count` (R64), committing the staging directory whole (R67), and writing the record (R53).

An `ExtractionError` exits **12** with its text in `message`, and `remedy` names the source file.
It is deliberately **not** exit 6: a provider call that failed and a local video that could not be
read reach R27's step 10 by different routes and need different things done about them (R28), and
an agent should read which one happened from the exit code rather than from the message. Any other
exception escaping the boundary is not this and surfaces as R28's internal failure, exit 11.

**Why this is a requirement and not a structural detail left to an implementer.** Extraction is
the only operation that produces many files, so it is the only one that exercises the multi-file
commit — displace the existing directory, rename the staging directory onto it, delete the
displaced copy (R67). With no substitutable boundary there is nothing a test can stand in for, so
that commit path has **no coverage at all**, and an implementation that copied frames into the
destination one at a time would satisfy every other requirement here while breaking the guarantee
R67 exists to provide. Named, a test drives a genuine multi-file `generate` — real staging, real
commit, real record write — against a stand-in returning a handful of canned PNGs.

**This settles nothing about which library decodes.** The boundary fixes what extraction is called,
what it is handed and what it hands back, never what performs it. R62's rule that nothing shells
out to an external binary still stands, and the design doc's note that ffmpeg is an external
binary this project does not otherwise depend on (§ Sprite sheets) is unchanged and unresolved.
Whichever library ends up behind the boundary is a change behind it and nowhere else.

[PRD choice — the design doc settles that extracting frames is local work the framework does
itself (§ Sprite sheets) and says nothing about how that work is structured. The name is free to
change until something calls it; that there is exactly one substitutable boundary is what the
commit path's testability depends on.]

### The provider boundary

**R75.** Every call to Replicate is made through **one named boundary and nowhere else**, and
that boundary is **substitutable**: a stand-in can be put in its place with no network reachable
and no real credential, and everything else about the run stays real.

| | |
|---|---|
| Name | `agf.provider` — two functions and one exception, and nothing else speaks to Replicate |
| Predicting | `run(model_id, inputs, api_token)` |
| Uploading | `upload(local_path, api_token)` |
| Raises | `agf.provider.ProviderError(message)` from either |

**`run`** takes the resolved model id (R38, R39), the input map exactly as it is to be sent —
prompt already merged under `prompt_key` (R41), each `input_files` value already replaced by the
URL `upload` returned (R42), everything else passed through untouched (R40) — and the credential
read from the environment (R29). It polls until the prediction reaches a terminal state and
imposes no timeout of its own (R32), fetches the files the prediction produced, and returns a
mapping with exactly three keys:

The polling loop is inside this boundary, so R32's distinction is this function's to make: it
waits on a known in-progress status indefinitely, and raises `ProviderError` on the first
response whose status is absent or unrecognised. No attempt cap exists here or anywhere else
(R32).

```
{"version": "owner/name:0e9f…", "seed": 42 | None, "outputs": [b"…", b"…"]}
```

| Key | Holds |
|---|---|
| `version` | The **pinned** `owner/name:version` the provider actually ran — what R49 records, and never a bare model name |
| `seed` | The seed the provider returned, or `None` where it returned none (R50). Never the seed the entry declared: the framework already has that one |
| `outputs` | An ordered list of `bytes`, one element per file the prediction returned, **already fetched**. R59 counts this list; a length other than one, for an entry declaring one `output`, is `output_count: "fail"` |

Fetching the result files sits behind the boundary rather than in front of it because it is more
HTTP with the provider, and a boundary that returned URLs for someone else to download would
leave a second path to the network — which is exactly what the first reason below exists to rule
out.

**`upload`** takes the resolved path of a file an `input_files` reference names (R42, R43) and
the credential, and returns the URL Replicate's file endpoint handed back. [§ How a referenced
file reaches the model] `frames` and `source` are read from disk by local operations and never
reach this function (R42).

**`ProviderError(message)`** is raised by either function when the request is rejected, the
prediction fails or is canceled, the response is malformed (R32), or the transport fails. It
carries **the provider's own error text** where the provider gave one; for a malformed response
there is none, and `message` names the unrecognised status or its absence instead (R32). It
exits **6** with that text in `message` (R33), with no part of the full response
written to a file or printed to stdout. Any other exception escaping the boundary is not this and
surfaces as R28's internal failure, exit 11. A local operation's failure is never exit 6 (R28,
R74).

**Only the HTTP conversation with Replicate sits behind it.** Choosing the model (R38, R39),
resolving file references (R42, R43), assembling the inputs (R40, R41), checking the returned
bytes against the declared format (R54), counting the returned files (R59), staging and
committing (R67) and writing the record (R53) all stay in front of it — the same division R74
draws for extraction. Nothing outside `agf.provider` opens a connection to the provider, and no
code outside it uses the credential for anything but handing it to these two functions (R31).

**Why this is a requirement and not a structural detail left to an implementer.** Two things
depend on it, and neither is recoverable once the calls are spread out:

- **No test can reach the network or spend money.** One named boundary is what a test suite can
  guard wholesale: replace both functions with something that raises, and any path that would
  have called Replicate fails loudly instead of billing the user. A provider call assembled in
  three places cannot be guarded that way, and the first anyone hears of the third one is an
  invoice.
- **The whole of `generate` can be driven in a test with only the remote call replaced.** Config
  resolution, whole-manifest validation, the credential check, argument assembly, the lock, the
  sweep, staging, every check, the commit and the record write all stay real, while a stand-in
  supplies canned bytes and a pinned version. Without the boundary each of those is either
  tested against something other than the real command or not tested at all.

[PRD choice — the design doc settles that the framework calls Replicate, and settles that a
referenced file is uploaded and its returned URL passed as the input (§ How a referenced file
reaches the model), but says nothing about how the calling code is structured. The names, the
argument lists and the returned shape are free to change until something calls them; that there
is exactly **one** substitutable boundary is not, because both properties above rest on it.]

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
  [§ One entry is one step]
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

- **Is `assetgen.yaml`, with these five keys, the right shape for the config file?** That there
  *is* a config file in the calling project is settled by the design doc; its name, format and
  keys are this PRD's (R6–R13). Nothing consumes it yet, so changing any of that costs only
  that section.
- **May an `assemble_sheet` entry name its frames by pattern instead of listing them?** R60
  requires an explicit ordered list, which never guesses order but means a 24-frame sheet
  lists 24 filenames by hand. A `{pattern, count}` shorthand would remove that. *This is a
  proposal of mine, not something the design doc raises.*
