**Build-readiness: 82** — carried from the last grade, because an author does not grade their
own work. The three fixes from that review are in: `--manifest`'s resolution rule
(Requirement 1), who writes `pubspec.yaml` (Requirement 9), and the seed discriminator
(*Needs the user*).

# PRD: Asset Generation — Replicate

> **Status:** Draft · **Deferred until dispatched — see Requirement 5.** Source docs read:
> `Tech Design.md`, `Theming.md`, `Menus and UI.md`, `Game Overview.md`, `Game Board Design.md`,
> `Animations.md`, `Rules.md`, `roadmap.md`, and the read-only reference asset
> `design_handoff_game_ui/` (`README.md` → *Assets*, `neon.theme.json`, `themes.catalog.json`).
> `Alternative Game Styles.md` is a declared parking-lot doc and was not sourced from.

**Wave:** P5 · **File:** `P5-02-asset-generation-replicate.md`

**The timing this PRD was written under.** `Tech Design.md` → Decisions → *Where do sound and
art assets come from?* sets timing as part of the answer: *"We don't have to start now and it's
best to do what we can without images or music but once needed Replicate can help us out
here."* Every wave above ships with placeholders and must be completable without any generated
asset. That is a **scheduling** statement about when this PRD is dispatched, not a licence to
decline the work once it is — Requirement 5 states what to do on dispatch.

**Depends on:** `P1-01-app-scaffold.md` requirement 3 — which creates `assets/themes/`,
`assets/images/` and `assets/audio/`, each with a `.gitkeep`, and declares **no** asset paths in
`pubspec.yaml`. That requirement assigns the declaration onward by name: *"The asset declaration
for a folder is added by the PRD that lands the first real file in it — themes by
`P1-03-theme-system.md`, **images and audio by `P5-02-asset-generation-replicate.md`**"* — i.e.
to this PRD. See Requirement 9. `P2-02-audio.md` requirement 18 repeats the same assignment.
`P1-01`'s Out of Scope, which pointed the audio declaration at `P2-02`, is being corrected
there.

**Dependency amendment — a set of one.** Requirement 8 adds **`image`** as a `dev_dependency`,
which amends `P1-01` requirement 14's table (declared *"exhaustive as of this wave"*, with any
later addition required to amend it rather than arrive silently). Nothing else is added:
`yaml` is already declared by `P1-03` requirement 36, and `dart:io`'s `HttpClient` covers the
Replicate calls, so no HTTP package is needed.

**Consumed by:** `P4-01-main-menu.md` requirement 8 (the logo, rendered through
`surfaces.menu.logo`), `P2-02-audio.md` requirements 17–19 (playback, complete and testable
before any asset exists), `P1-03-theme-system.md` requirement 15 (the slots whose values are
the paths this PRD produces). Those three ship in **earlier** waves, without assets, by design.
`P5-01-classic-theme.md` is in **this same wave**, so the two are sequenced by need rather than
by wave — that has been true here since an earlier revision, so `P5-01`'s flag against this
header is the stale one.

---

## Problem

The game has asset slots and no assets. The logo on the main menu is a placeholder
(`design_handoff_game_ui/README.md` → *Assets*: *"Logo — placeholder only. Needs real art."*),
and no sound has been produced at all (same section: *"Sounds — none produced."*). Neon's five
playable sound slots hold `"TODO: neon buzz one-shot"` and four `"TODO"` (`neon.theme.json` →
`sound`), while `P1-03-theme-system.md` requirement 11 requires Neon to define every `required`
slot — so the gap is real, just not urgent.

**The sound gap is real; the mark-art gap is not.** All three of Neon's marks are glyphs, not
images — `neon.theme.json` → `marks` gives `playerOne ✕`, `playerTwo ○`, `catGame Ø`, each
`"kind": "glyph"` in Inter. `Theming.md` → Decisions → *Marks beyond X and O* settles only that
a theme *may* supply mark art; Neon does not, and whether Classic overrides marks at all is
`P5-01-classic-theme.md`'s open question 3. **No mark images are needed today, and generating
✕/○ art would be work nobody asked for.**

The risk this PRD guards against is not the missing art — it is how the art gets made. The user
has done this before and named the failure mode: a generation system that accumulates a script
per asset and leaves debris behind.

## Goal

When an asset is needed, one script makes a pinned Replicate API call for it, writes the result
into the designated asset folder under a filename the theme layer can rely on, records enough
to regenerate it, declares it so it actually ships — and leaves nothing else behind.

## Deliverable — two stages, and why the split is load-bearing

**Stage 1 — the tool, complete.** The script, the prompt manifest's schema and the metadata
file. **Every code path in Requirements 1–16 is written at stage 1**, Requirement 7's path
computation and Requirement 8's downscale chain included. Nothing is stubbed and no `TODO`
stands where an output path is computed. What stage 1 lacks is not code but **inputs** — a
model id and a prompt, both of which live in the prompt manifest (Requirement 13) and neither
of which this PRD chooses. Nothing is generated, no `pubspec.yaml` asset declaration is added,
and **no real model id appears anywhere in the tree.**

**What makes the stage-1 tests runnable: the path seam plus a fake id.** Every stage-1 test is
written as process behaviour, so it needs a manifest the script will actually read and a place
to write. Requirement 1 therefore takes **`--manifest <path>`** and **`--root <dir>`**, and a
test supplies a fixture manifest at an absolute path with a temporary root. The fixture may
carry an obviously fake pinned id —
`example/not-a-real-model:0000000000000000000000000000000000000000000000000000000000000000` —
which never appears in `tool/asset_prompts.yaml`, cannot resolve at Replicate, and commits
nothing. **Both halves are required.** A fake id with no `--manifest` seam still leaves the
tests needing a parseable file at the one hardcoded path the fixture is forbidden to occupy,
which was an earlier draft's defect: of six stage-1 cells needing a resolvable entry, only
`--all --force` worked, because it exits at check 1 before any manifest is read.

**Stage 2 — the first real generation run.** Prompts, `ext` values and model ids are filled in,
assets land, and the `pubspec.yaml` declarations of Requirement 9 land **in the same change**.

**Which evidence is available when.** Implementation does not split; verification does.

| Runnable at stage 1 | Needs a live call — stage 2 | Neither — review criteria |
|---|---|---|
| 1 (entry point, `--dry-run`, every flag error), 3, 4, 5, 9's stage-1 testable, 10's schema and pin rule, 11's missing-token path, 12 against a `--dry-run`, 13's five pre-flight exits, 16's refuse-without-`--force`, `--all --force` rejection and partial-output exit | 2, 6, 7, 8, 9's stage-2 testable, 10's reproduce-from-record test, 11's rejected-token path, 16's `--force`, list-selection, `status: failed` and killed-mid-download halves | 14 and 15 — both assert something no test can establish; a reviewer judges them |

Every stage-2 cell needs a model id to form a request, which is why it cannot move left.

**Why the split exists.** Two reasons, and the second carries it alone if the first turns out
not to hold:

1. `P1-01-app-scaffold.md` requirement 3 records that Flutter fails the build when a declared
   asset directory contains no files, so declaring `assets/audio/` before generating anything
   breaks the build. **Premise worth checking rather than repeating:** that same requirement
   puts a `.gitkeep` in each folder, so the directories are never *literally* empty — whether
   Flutter's directory-asset bundling counts a dotfile decides whether this reason holds. It is
   asserted as fact in three PRDs and verified in none.
2. Generating anything requires the two model choices this PRD reserves for the user. This one
   is not contingent on anything.

## Requirements

### The script

1. **Exactly one script performs the Replicate API call**, and it has this shape:

   | | |
   |---|---|
   | Language | **Dart** — `Tech Design.md` → Decisions → Language — Dart; the SDK ships with Flutter, so no new toolchain |
   | Tree | **inside `src/Tic-Tac-Toe-Extreme`** — `dart run` needs a `pubspec.yaml`, Requirement 8 adds a `dev_dependency` to it, and Requirement 4's grep is scoped to `lib/`. *Reversible*; the user question below is confirmation, not a blocker |
   | Path | `tool/generate_asset.dart` — Dart's conventional `tool/` directory, outside `lib/` so Requirement 4's grep stays clean |
   | Invocation | `dart run tool/generate_asset.dart <flags>` |
   | Flags | `--asset <id>` · `--all` · `--force` · `--dry-run` · `--timeout <seconds>` (default **600**) · **`--manifest <path>`** (default `tool/asset_prompts.yaml`) · **`--root <dir>`** (default the package root) |
   | Path resolution | **Every path the script *writes* resolves against `--root`** — `assets/audio/`, `assets/images/` and `tool/generation.manifest.json` — so a test can point the whole tool at a temp dir without relocating anything relative to anything else. **`--manifest` is the one exception and is deliberately not root-relative:** it is an *input*, and the fixture that drives a stage-1 test lives in the Dart test directory rather than in the temp root being written to. An absolute path is used as given; a relative one resolves against the current working directory, and tests pass absolute paths so they do not depend on where `dart run` was invoked. The default, `tool/asset_prompts.yaml`, resolves against `--root` because that is where the real one lives |
   | HTTP | `dart:io` `HttpClient`, **polling** the prediction endpoint every 2s — *not* `Prefer: wait`, which caps near 60s and would silently contradict the 600s timeout |
   | Exit | `0` on success; non-zero on every failure path in Requirements 11, 13 and 16 |

   **The two path flags are the seam that makes stage 1 verifiable.** Without them every
   process-level test needs a real file at a hardcoded path, and an agent closes the gap by
   inventing an undocumented flag, changing the working directory (which relocates outputs and
   metadata, breaking Requirement 12's whole-root diff), or testing internal functions instead
   — none of which this PRD asks for. Splitting the two resolution rules is what stops the seam
   breaking one level down: root-relative manifests would put the fixture back inside the tree
   under test.

   **Flag combinations, all defined:**
   - `--asset` and `--all` together, or neither: exit non-zero with usage. Exactly one selects
     the work.
   - `--all` alone: every manifest entry **whose outputs do not yet exist**. Entries whose
     outputs all exist are skipped silently — not regenerated, not an error.
   - **`--all --force`: rejected — exit non-zero.** `--force` overwrites approved art, so it
     applies to exactly one named asset at a time. Bulk-overwriting every generated asset in
     one command is the failure Requirement 16 exists to prevent, and it must not be reachable
     by combining two individually reasonable flags.
   - **`--dry-run` runs pre-flight checks 1–3, *reports* check 4, and never reaches check 5.**
     It prints the exact paths that would be written and whether each would be created,
     overwritten or skipped, then exits `0`. It **never reads `REPLICATE_API_TOKEN` and never
     makes a network call** — which is what keeps it usable on a machine that has no
     credential, as Requirement 4 guarantees and the stage-1 column assumes.
   - **`--all` stops at the first failure**, leaving the assets and metadata entries already
     completed in place and exiting non-zero naming the failed id. It does not press on: a
     half-finished batch that reports success is how a missing asset reaches a build.

   Generating an additional asset adds a prompt-manifest **entry**, never a second script.
   *(`Tech Design.md` → Decisions → Where do sound and art assets come from? — *"Just one
   script that makes the API call with what we need. Not a script of every asset generation."*)*
   **The language, tree, path, flags and exit contract are mine and reversible.**
   **There is deliberately no `--model` flag**: the model id lives in the prompt-manifest entry
   (Requirement 13), which is what keeps stage 1 model-free.
   **Testable:** the tree contains exactly one asset-generation entry point; `--dry-run` against
   an absolute fixture manifest and a temp root exits 0 with no token set, having written
   nothing and printed one complete path per output; each rejected flag combination exits
   non-zero; generating a second asset produces a diff with no new script.

2. **That one script covers both audio and images**, rather than an audio script and an image
   script.
   *(same Decision — *"This answers both the sound assets (the Neon buzz, the Classic splat)
   and the art (the logo)"*)*
   **Testable (stage 2):** the same entry point produces an audio file under `assets/audio/`
   and a PNG under `assets/images/`.

3. **Generated assets are written into the designated asset folders** — art into
   `assets/images/`, audio into `assets/audio/` (both under `--root`) — and the script writes
   **no generated asset** anywhere else. `assets/themes/` holds theme YAML and is not a
   destination for generated output.
   *(`Tech Design.md` → Decisions → Project structure — layer-first, which names those three as
   **"the designated folders for assets required by Where do sound and art assets come
   from?"**; `P1-01-app-scaffold.md` req 3 creates them.)*

   **The folders are cited; the *prohibition* on writing elsewhere is mine.** The design doc
   requires designated folders; it does not say the script may write nowhere else. That clause
   is this PRD's addition and is load-bearing twice — it is what collides with the iOS app icon
   (Open Questions) and why Requirement 10 needs an explicit carve-out. Rebuttable by the user,
   not by an implementer.

   **Inbound citations.** `P2-02-audio.md` requirement 18 and `P5-03-release-fastlane.md`
   requirement 23 both cite this rule as *"`P5-02` requirement 3"*; `P5-03`'s pointer was
   corrected back to 3 after an intermediate draft of this PRD renumbered. Both are live, and
   this requirement keeps its number for that reason.
   **Testable:** every path the script opens for writing is under `<root>/assets/audio/`,
   `<root>/assets/images/` or `<root>/tool/generation.manifest.json` — asserted by a filesystem
   diff of the whole root across a run, not by reading the source.

4. **The script is an offline authoring tool, not a build step.** It is never invoked by
   `flutter build`, `flutter run`, `flutter test`, a `pubspec.yaml` hook or any CI job; no code
   under `lib/` imports or shells out to it; and the app builds, tests and archives on a
   machine that has never held a Replicate credential.
   *(**Mine, derived** — no doc states it. It follows from `Tech Design.md` → Decisions → CI —
   local builds only (nowhere to hold a build-time secret) and from *"Fully offline, except for
   in-app purchases"*, whose one network exception is StoreKit against Apple.)*
   **Testable:** `flutter build ios` and `flutter test` succeed with `REPLICATE_API_TOKEN`
   unset; a grep of `lib/` finds no reference to the script or to `replicate`.

5. **Being dispatched is the signal that the asset is needed — build it.** An agent handed this
   PRD does not return "deferred, not starting"; the deferral above governs *when the
   coordinator dispatches*, and dispatch ends it. An agent dispatched without model ids and
   prompts builds **stage 1 in full** and says so, rather than stalling or inventing either.
   *(**Mine.** `Tech Design.md`'s *"once needed Replicate can help us out here"* fixes the
   trigger but names no actor, and a PRD that stops itself from being executed is a dead
   letter.)*
   **Testable:** a dispatch that produces no `tool/generate_asset.dart` fails this requirement;
   a dispatch that produces one with no real model id anywhere satisfies it.

### What gets generated — stage 2

6. **"The buzz" and "the splat" are sonic *characters*, not filenames — the asset set is
   larger than three files.** Reading the decision as a three-item manifest under-generates:

   - **`signature` is descriptive metadata that is never played.** `neon.theme.json` →
     `sound.signature` holds the word `"buzz"`; `themes.catalog.json` →
     `signatureSound: "splat"` is the same kind of value. *(`P2-02-audio.md` req 7 —
     *"descriptive metadata, not an asset"*; `P1-03-theme-system.md` req 15 → `sound` —
     *"string, **metadata, never played**"*.)* One file called "the buzz" satisfies nothing.
   - **Neon needs five playable sounds:** `placeMark`, `claimQuadrant`, `catGame`, `winGame`,
     `buttonTap` — all five `"TODO"` today, all five `required`. `buttonTap` is **one** sound:
     `P2-02` OQ-3 is closed on the user's Decision, *one tap sound everywhere*.
     *(`P2-02-audio.md` req 6; `P1-03-theme-system.md` reqs 11 and 15)*
   - **Classic overrides at least one of the five**, count open
     (`P5-01-classic-theme.md` open question **2**).
   - **The logo is per-theme, not one file** — and each logo is **three** files (Requirement 8).
     `surfaces.menu.logo` is a **required** slot on every theme, and the design doc puts the
     logo inside what a theme controls: `Theming.md` → Architectural Rule lists *"the
     main-menu logo"* among the surfaces every theme owns, and → What a Theme Controls repeats
     it. *(`P5-01-classic-theme.md` req 5's override set is colour-shaped leaves and does not
     mention the logo, so it is not the citation for this.)*

   **Floor: five Neon sounds + at least one Classic sound + at least one logo (three files).**
   The total is higher and is not yet fixed — see Open Questions.

7. **The output filename is a published interface, and these are the names.** The path is
   **derived** by the script from a prompt-manifest entry's `theme`, `slot`, `kind` and `ext` —
   never authored by hand, so there is one source of truth for it.

   | Consumer slot | File this PRD produces |
   |---|---|
   | `sound.{placeMark,claimQuadrant,catGame,winGame,buttonTap}` on Neon | `assets/audio/neon-<slot>.<ext>` |
   | the same five slots where Classic overrides them | `assets/audio/classic-<slot>.<ext>` |
   | `surfaces.menu.logo` on theme `<t>` | `assets/images/<t>-logo.png`, plus `assets/images/2.0x/<t>-logo.png` and `assets/images/3.0x/<t>-logo.png` |

   `<slot>` is the slot key verbatim in lowerCamelCase; `<t>` is the theme's folder-scan name
   (`neon`, `classic`). Theme-prefixing everything — the logo included — is what lets one theme
   override a slot without colliding with another's file in a flat folder.

   **`<ext>` comes from the entry's `ext` field and is verified against the bytes.** It is a
   **required field on every `kind: audio` entry** (Requirement 13) — not a global constant and
   not derived from the response, because deriving it would leave the path unknown until after
   the call, breaking both `--dry-run` and pre-flight check 4. Image entries need no `ext`:
   always `.png`.

   | `ext` | Accepted `Content-Type` | Magic bytes |
   |---|---|---|
   | `mp3` | `audio/mpeg`, `audio/mp3` | `ID3` at offset 0 **or** a frame sync `FF Ex`/`FF Fx` |
   | `wav` | `audio/wav`, `audio/x-wav` | `RIFF` at 0 and `WAVE` at 8 |
   | `flac` | `audio/flac`, `audio/x-flac` | `fLaC` at 0 |
   | `png` | `image/png` | `89 50 4E 47` at 0 |

   Legal values are exactly those four. **`application/octet-stream` is accepted** — Replicate's
   CDN commonly serves it, and rejecting it would make the tool unusable — and in that case the
   magic bytes decide alone. **Magic bytes win any disagreement with `Content-Type`.** If the
   bytes match none of the accepted signatures for the declared `ext`, the script **exits
   non-zero without writing, naming both the declared `ext` and the encoding actually
   detected** (or "unrecognised"), mirroring Requirement 8's "naming the size received". That
   message is the only thing the user gets: Requirement 11 forbids the response body on disk,
   so a bare "mismatch" would leave a paid-for prediction with nothing to inspect.

   **The audio half rests on a fixed value shape; the logo half does not.** `P1-03` req 15
   types the five sound slots as `assetPath` = *"a path under `assets/`, or null"*, and
   `P2-02-audio.md` req 3 fixes that the slot holds the **full path**, *"not a bare file name
   and not a key into a manifest"* — settled. **`surfaces.menu.logo` is typed nowhere:**
   `P1-03` req 15's `surfaces` table gives that row a status (*"**required** slot; **asset is a
   placeholder**"*) but no value shape, unlike every neighbouring row. Whether it is an
   `assetPath`, an `icons`-style `{kind, value}` pair, or a structured description of the drawn
   81-dot placeholder is unstated, so the logo row above assumes the `assetPath` reading and is
   **provisional on `P1-03` typing it**.
   **The convention itself is mine** — no doc names a filename. Cheap to change before any YAML
   references it, expensive after.
   **Testable (stage 2):** every path the script writes matches a pattern above, density paths
   included; a response whose bytes contradict the declared `ext` exits non-zero naming the
   detected encoding and writes nothing; every generated-asset `assetPath` in
   `assets/themes/*.yaml` resolves to a file this script produced.

8. **Formats, dimensions, and the two conversions they imply.**

   - **Audio format is per-entry, not global.** The entry's `ext` declares it and Requirement 7
     verifies it. `.mp3` is the expected value — `P2-02-audio.md` req 3 is written against it —
     but **most Replicate audio models emit wav or flac**, and three paths remain open: choose
     a model that emits mp3; declare `ext: wav` and ship wav, which `P2-02` req 3's own grep
     names and `AssetSource` handles; or transcode with **ffmpeg**, an external binary **no doc
     authorizes installing**. That choice is the user's (Open Questions); the mechanism holds
     under all three. One-shots only; `music` is never played (`P2-02` reqs 7 and 14).
   - **Logo: PNG with alpha, square, 104×104 logical points** at 1x, with 2x and 3x variants.
     *(104×104 is `P4-01` req 13 item 3 and `design_handoff_game_ui/README.md` → screen 1a. The
     1x/2x/3x layout is Flutter's documented resolution-variant mechanism, not a preference.)*
   - **The render gate: square, and at least 312 on a side.** Nothing carries a model's
     supported sizes, and many models take an `aspect_ratio` string rather than width/height,
     so the script does **not** introspect the model. It passes whatever the entry's `params`
     specifies; with no `params`, it requests the model's default. It then **rejects any render
     that is not square, and any render whose side is under 312**, exiting non-zero and naming
     the dimensions received. *Rejecting rather than cropping is mine and deliberate:*
     crop-center, crop-top, letterbox and squash all satisfy "make it square" and three of them
     mangle a logo, so the script refuses and the user sets `params` for a square render.
   - **One render, then a *chain* of downscales — not three model calls and not three
     independent resamples.** Flutter treats `2.0x`/`3.0x` variants as the *same artwork* at
     different densities, so three independent generations would make the logo change
     appearance from device to device. The pipeline is:

     ```
     render → resample to 312 (3.0x) → resample the 312 to 208 (2.0x) → resample the 208 to 104 (1x)
     ```

     **Chained, not parallel**, because resampling is not associative: downscaling the render
     separately to 208 and 104 produces files a test cannot derive from the 3x one.
   - **The image library and its pinned constants.** `package:image` (pure Dart) as a
     `dev_dependency`. The resample filter is one named constant — **`Interpolation.cubic`**,
     stated because `copyResize`'s own default is `nearest` — and the PNG encoder is
     `encodePng` with **`level: 6`** and **`filter: PngFilter.paeth`**. *What these buy is not
     the test below*, which re-invokes the script's own chain so the filter cancels out; they
     buy **cross-machine reproducibility**, so two people regenerating from the same record get
     the same bytes. That claim holds under the committed `pubspec.lock`, since `package:image`
     sits behind a caret range and a minor bump may change encoder output. *Mine and
     reversible; what is not optional is that they are pinned somewhere a regeneration can
     reuse.*

   **Testable (stage 2):** each audio file decodes as the encoding its `ext` claims and plays as
   a single one-shot; a non-square or under-312 render exits non-zero naming the dimensions;
   the three logo files are square PNGs with alpha at 312/208/104; and **re-running the
   script's own chain and encoder over the 3x file reproduces the 2x file byte-for-byte, and
   over that the 1x file byte-for-byte.**

9. **The `assets/images/` and `assets/audio/` declarations in `pubspec.yaml` are this PRD's,
   and they are a hand edit in the stage-2 change — the script never writes them.**
   `P1-01-app-scaffold.md` req 3 assigns the declaration here by name; declaration and first
   asset ship together, and neither ships alone.

   **Why the script does not do it.** `pubspec.yaml` is a pinned, hand-maintained file —
   `P1-01` req 14's caret ranges and a committed `pubspec.lock` — and `P1-03` req 36 already
   writes an `assets:` block for `assets/themes/`. A load-and-dump would reorder and reformat
   the file and could clobber that block; specifying a non-destructive YAML merge, its
   idempotency, its `--force` behaviour and its `--dry-run` output would be a second feature
   inside a tool whose whole point is that it does one thing. So the edit is two lines a human
   adds in the same commit as the first generated asset, and Requirement 12's inventory counts
   only what the *script* writes.

   **This is the item whose absence silently ships a working-looking, non-functioning
   feature:** land the files without the declaration and the bundle contains neither, the audio
   layer's `AssetSource` misses, the logo slot renders nothing, and every other test in this
   PRD still passes.
   *(`P1-01-app-scaffold.md` req 3; `P2-02-audio.md` req 18; `P1-03-theme-system.md` req 36.)*
   **Testable (stage 2):** `pubspec.yaml` declares both directories; a release build's asset
   bundle contains every file from Requirement 7; the app plays a generated sound on a device;
   and a generation run against a fixture root leaves `pubspec.yaml` byte-identical.
   **Testable (stage 1):** `pubspec.yaml` gains only Requirement 8's `dev_dependency` and no
   asset declaration, and `flutter build` still succeeds.

### Inputs, reproducibility and provenance

10. **Generation is reproducible where the model allows it, and exactly one metadata file
    records how.** `tool/generation.manifest.json` is **written only by the script, never
    hand-edited**, never under `assets/`, and has this shape:

    ```json
    {
      "schemaVersion": 1,
      "entries": {
        "<id>": {
          "outputs": ["assets/images/neon-logo.png", "assets/images/2.0x/neon-logo.png",
                      "assets/images/3.0x/neon-logo.png"],
          "kind": "image",
          "model": "owner/model:<version>",
          "prompt": "…",
          "seed": 1234,
          "seedSource": "generated",
          "reproducible": true,
          "params": {},
          "outputIndex": 0,
          "ext": "png",
          "generatedAt": "2026-08-08T14:03:11Z"
        }
      }
    }
    ```

    Keyed by the prompt-manifest `id`, so **one entry per id** — a logo's three files are one
    entry with three `outputs`, not three entries. `generatedAt` is ISO-8601 UTC with a `Z`
    suffix. `outputIndex` records the element chosen by Requirement 16 when a prediction
    returned a list.

    **Seeds, including when the entry omits one.** `seed` is optional in the prompt manifest,
    and a model left to itself will seed randomly — which would make this requirement's own
    testable unrunnable. So:
    - entry supplies a seed → use it, record it, `seedSource: "manifest"`;
    - entry omits one and **the model accepts a seed** → the script generates a random 32-bit
      seed, passes it, records it, `seedSource: "generated"`;
    - **the model accepts no seed** → record `seed: null`, `seedSource: "unsupported"` and
      **`reproducible: false`**, which is the honest record and scopes the test below.

    **How the script decides which of those three applies is not settled** — Requirement 8
    forbids model introspection and Requirement 13's field list carries no discriminator, so
    the cheapest legal implementation marks everything `reproducible: false` and the test below
    quantifies over the empty set. That is the difference between this requirement meaning
    something and passing vacuously; it is in *Needs the user* below.

    **The call pins its model version**, independent of which model is chosen:
    `owner/model:<version>`, never a bare `owner/model`.

    *(**Mine, and stated because the alternative is worse.** No doc asks for reproducibility.
    But Requirement 12 *is* a hard requirement, so an implementer resolves the tension by
    writing no metadata at all, and then nothing can be regenerated after a tweak — the
    debris-and-one-off-scripts failure this PRD exists to prevent, arrived at from the other
    side. The user may instead declare generation explicitly non-reproducible; see Open
    Questions.)*
    **Testable:** every entry names a pinned version and one `id` key; for every entry with
    `reproducible: true`, re-running with its recorded prompt, version, seed and params
    reproduces the asset; no per-asset metadata file exists anywhere.

11. **The credential is `REPLICATE_API_TOKEN`, and every network failure has a defined exit.**
    The script reads the token from the `REPLICATE_API_TOKEN` environment variable —
    Replicate's own documented convention, so research rather than preference — and never from
    a committed file, a CLI flag or an interactive prompt.
    - **Missing:** exit non-zero **before any network call**, with a message naming the
      variable, having written nothing. (`--dry-run` never reaches this check at all.)
    - **Rejected (401/403):** exit non-zero, leaving no partial or zero-byte file and no
      metadata entry.
    - **Terminal `status: failed` or `status: canceled`:** exit non-zero, naming the prediction
      id and quoting the response's `error` string. This is the most common real failure and it
      is neither an auth error nor a timeout. The `error` string is a message, not a response
      body, so quoting it does not breach the rule below.
    - The token is never written to `tool/generation.manifest.json`, never echoed, never
      committed.
    - **No response body is written to disk** other than the decoded asset bytes at their final
      path — no raw JSON dump, no prediction log. Requirement 12 depends on this.

    *(**Mine**, on Replicate's documented convention. `Tech Design.md` → Decisions → CI — local
    builds only rules out a CI secret store; where the token lives on the machine is the
    user's call — see Open Questions.)*
    **Testable:** with the variable unset the script exits non-zero, makes no network call and
    leaves the tree unchanged; with a bad token it exits non-zero and leaves no new file; a
    stubbed `failed` prediction exits non-zero naming the id and the error.

12. **A run leaves no junk behind.** After a successful run the only new or changed files under
    `--root` are the generated asset(s) of Requirement 7 and `tool/generation.manifest.json`.
    **Nothing else** — no temp files, no per-run scratch scripts, no response dumps, no
    leftover intermediates, and **not `pubspec.yaml`**, which Requirement 9 keeps as a human
    edit in the same commit rather than a script write.
    *(`Tech Design.md` → Decisions → Where do sound and art assets come from? — *"we just need
    the APIs and will need to build our own system that operates clean and generates no junk"*,
    *"I would prefer to not have junk scripts lying around"*.)*

    **The metadata carve-out is explicit because the earlier wording forbade it.** The metadata
    file is a changed file that is not a generated asset; read strictly, this requirement once
    banned the provenance record Requirement 10 requires.

    **How to check it, and how not to.** `src/Tic-Tac-Toe-Extreme` is a **git submodule**, so
    `git status` from the repo root shows only a changed submodule pointer and never a single
    file inside it. A root-level `git status` therefore passes no matter how much junk a run
    leaves — a vacuous check, and one this repo has already shipped once (`CLAUDE.md` →
    *`srcRoots` are git submodules*). Scope it to the tree the run actually wrote into —
    Requirement 1 puts the script inside the submodule, so that is:

    ```
    git -C src/Tic-Tac-Toe-Extreme status
    ```

    and, should the script be moved outside it, a root-level `git status` **as well**, not
    instead. Whichever trees a run can touch, each is checked in its own right.

    Second caveat: a `.gitignore` entry makes junk invisible to `git status` too, so a clean
    status is evidence, not proof. Junk that is ignored is still junk lying around.
    **Testable:** a full listing of `--root` before and after a run — not only its git-visible
    portion — differs by exactly the files named above.

13. **The prompt manifest is the tool's input, is user-authored, and is a different file from
    the metadata of Requirement 10.**

    | | |
    |---|---|
    | Path | `tool/asset_prompts.yaml` by default, **overridable with `--manifest <path>`** so tests can supply a fixture without occupying the real path. Resolution is Requirement 1's: the default is root-relative, an override is used as given |
    | Format | YAML — `Tech Design.md` → Decisions → *What format are theme files* chose YAML for hand-authored project data, and this is hand-authored. The `yaml` package is already declared by `P1-03` req 36 |
    | Written by | **the user only.** The script reads it and never writes it |
    | Read by | the script, keyed on `--asset <id>` |

    Fields: **`id`** (the `--asset` key), **`kind`** (`audio` \| `image`), **`theme`**,
    **`slot`**, **`ext`** (required for `kind: audio`; images are always `png`), **`prompt`**,
    **`model`** (pinned `owner/model:<version>`), optional **`seed`**, optional **`params`**.

    ```yaml
    - id: neon-place-mark
      kind: audio
      theme: neon
      slot: placeMark
      ext: mp3
      model: owner/model:0000000000000000000000000000000000000000000000000000000000000000
      prompt: "…the user writes this…"
    ```

    **The two files must not be merged.** `tool/generation.manifest.json` is script-written
    provenance; this one is human-written input. One file would mean the script rewriting
    user-authored prompts, and would break Requirement 10's one-entry-per-id invariant for
    every id that has never been generated.

    **The model id lives here — not in a flag, and not as a constant in the script.** A
    constant would choose a model at stage 1, which is exactly what the two-stage split exists
    to prevent.

    **The script invents nothing.** Nothing anywhere specifies what to prompt for; five Neon
    sound prompts written by an agent would be pure invention, and Requirement 10 would then
    record the invented text as provenance — laundering a guess into the record. Prompts,
    `ext` values and model ids are the user's to write.

    **Pre-flight exits, in this order.** The order is part of the contract: it decides which
    failure a caller is told about, and at stage 1 it decides which tests can run at all.

    | # | Check | Exit |
    |---|---|---|
    | 1 | Flag combination valid (Requirement 1) | non-zero, usage |
    | 2 | The manifest — `--manifest` or the default — exists and parses | non-zero, naming the resolved path and the parse error |
    | 3 | The id resolves, and its entry has `kind`, `theme`, `slot`, `prompt`, `model`, and `ext` if audio | non-zero, naming the id and the missing field |
    | 4 | Outputs absent, or `--force` given (Requirement 16) | non-zero, naming the existing path — **reported rather than enforced under `--dry-run`** |
    | 5 | `REPLICATE_API_TOKEN` present (Requirement 11) | non-zero, naming the variable — **skipped entirely under `--dry-run`** |

    Only after all five does any network call happen. Checks 4 and 5 are unreachable until 2
    and 3 pass, which is why the stage-1 tests of Requirements 11 and 16 need **both** the
    `--manifest` seam and the fixture's fake id.

    A manifest is data, not a script, so it does not violate Requirement 1 — that requirement
    counts executable entry points, and the decision's wording is *"not a script of every asset
    generation."*
    *(**Mine.** No doc mentions prompts at all.)*
    **Testable:** each of the five checks fails on its own fixture, in order, naming the gap and
    writing nothing; the script never opens the manifest for writing.

### Provenance of the tooling

14. **fey-tactics is consulted for the API call only, and its system is not adopted.** As
    stated: *"do not take on the system from fey-tactics as it's not a good system we just need
    the APIs and will need to build our own."*

    This is a **code-review criterion, not a test.** It asserts a negative about provenance and
    no test can establish where code came from; a reviewer reads the tooling and judges whether
    it is our own system or theirs.

    Two facts about its force: fey-tactics is **not reachable from this project** — not a
    `srcRoot` in `Docs/tic-tac-toe/project.json`, and outside this repo — and Replicate's HTTP
    API is publicly documented, so consulting it is not required in order to make the call. The
    requirement's real weight is **prohibitive** ("do not adopt their system").
    *(same Decision; the same posture is recorded against fey-tactics in `Tech Design.md` →
    Decisions → State management — Riverpod, over its legacy `StateNotifier` API.)*

15. **Conditional, and a review criterion rather than a test — only if that model is the one
    used: confirm the transparent-background claim against the model card before Requirement
    8's logo depends on it.** The user notes that `sourceful/riverflow-2.0-pro` *"does allow
    for png transparent background images"* — **the user's note, not verified against the
    current model card, and not a model choice.** No requirement here selects a model, so this
    asks for verification of a property of a model that may never be chosen; it binds at first
    use of that model and not before. Requirement 8 needs *some* model that emits alpha. No
    test can assert it: the fact lives on a model card outside the repo, and a reviewer checks
    it.
    *(`Tech Design.md` → Decisions → Where do sound and art assets come from? — *"Worth
    confirming at first use"*)*

16. **Re-running, selection and interruption are defined.**
    - **Outputs exist, no `--force`:** exit non-zero without calling the API, naming the
      existing path. Silent overwriting of approved art is the expensive failure. (Under
      `--all`, such entries are skipped rather than an error — Requirement 1.)
    - **An entry's outputs are all-or-nothing.** A logo id owns three files; if some exist and
      some do not, the run **exits non-zero naming the missing ones** rather than guessing —
      a partial set means an interrupted run, and `--all` must not treat it as "already done".
      `--force` regenerates the whole set.
    - **Outputs exist, with `--force`:** regenerate, replace the files, and **rewrite that id's
      metadata entry in place** — never append a second entry for the same id. Requirement 10's
      one-entry-per-id is an invariant, not a starting state. `--force` never combines with
      `--all`.
    - **A prediction that returns a list** — many Replicate models return an array of outputs.
      **Take the first element, write exactly one asset, and record the index as
      `outputIndex`.** Writing all of them would violate both Requirement 7's naming and
      Requirement 12's no-junk rule. An empty array exits non-zero, writing nothing.
    - **Interrupted, timed out or partial:** the download is staged in the system temp
      directory and moved into place only after a complete, verified transfer, so **nothing
      partial ever appears under `assets/`**; a run that dies mid-download leaves no file and
      no metadata entry. A prediction still not terminal after `--timeout` (default **600
      seconds**, polled every 2s per Requirement 1) exits non-zero on the same terms.
    *(**Mine.** Requirement 11 covered auth failure only; Requirement 12 tolerated replace,
    append and refuse equally, so all three were reachable by accident.)*
    **Testable:** a second run without `--force` exits non-zero and makes no request; a
    partially-present output set exits non-zero naming the missing files; `--all --force` exits
    non-zero; a `--force` run leaves exactly one entry for that id; a list-returning prediction
    writes one asset and records its index; killing a run mid-download leaves the tree as it
    was.

## Out of Scope

- **The audio playback system** — `audioplayers`, the five moments, the mute gate →
  `P2-02-audio.md`. This PRD produces files; that one plays them.
- **The theme schema and every slot's shape** → `P1-03-theme-system.md` req 15. This PRD writes
  files whose paths become slot values; it defines no slot and authors no theme content.
- **Authoring theme YAML** — putting Requirement 7's paths into `neon.yaml` and Classic's file
  is `P1-03`'s and `P5-01`'s. This PRD does not edit `assets/themes/`.
- **Editing `pubspec.yaml` programmatically.** Requirement 9 keeps the asset declaration a hand
  edit; no YAML-merge, idempotency or dry-run story is specified because the script has none.
- **The logo's placement and the menu's pixel fidelity** → `P4-01-main-menu.md`.
- **Mark art.** Neon's marks are glyphs and need no image; whether Classic overrides marks is
  `P5-01-classic-theme.md`'s open question 3, not this PRD's to pre-empt by generating art.
- **Icon images.** `P1-03` req 15 → `icons` permits `kind: image` with a `path` of shape
  `assetPath`, so a theme *could* supply a chrome icon as a file. Neither shipping theme does —
  every `icons.<slot>` is `kind: iconSet` from the bundled **Phosphor** set. If a future theme
  sets `kind: image`, that file is this script's to produce; none exists today.
- **Inter 400/500/600 and the Phosphor set** — third-party dependencies to bundle, not
  generated assets; `Tech Design.md` notes explicitly that **neither is Replicate-generated**.
- **A Replicate agent** — *"hedged and explicitly not now"*, and it would live in the agent
  system rather than in the game.
- **`Alternative Game Styles.md`** — declared parking lot.

## Open Questions

### From the design docs — unresolved, worded as the docs word them

- **Whether `sourceful/riverflow-2.0-pro` *"does allow for png transparent background
  images"*** — the user's note, *"worth confirming at first use"*, not verified and not a model
  choice. Requirements 8 and 15 are both conditional on it. *(`Tech Design.md` → Decisions →
  Where do sound and art assets come from?)*
- **Who produces the app icon, and is it generated or hand-made?** *(`Tech Design.md` → Open
  Questions → 3)* See below.

### Cross-PRD

- **`surfaces.menu.logo` has a status but no value shape.** `P1-03-theme-system.md` req 15's
  `surfaces` table marks it *"**required** slot; **asset is a placeholder**"* and types nothing,
  unlike its neighbours — `assetPath`, an `icons`-style `{kind, value}` pair, and a structured
  description of the 81-dot placeholder are all still reachable readings. Until `P1-03` types
  it, Requirement 7's logo row is provisional.
- **The `.mp3` circularity is closed on the interface, not on the format — and `P2-02` no
  longer asserts otherwise.** That PRD withdrew the claim: its req 3 now reads `<ext>`
  throughout, states *"`<ext>` is not settled, and this PRD must not pretend otherwise,"* and
  lists the old `.mp3`-as-fact claim under *Stale claims withdrawn*. **There is nothing to fix
  in `P2-02`**, and its OQ renumbering is reflected here (OQ-2 is the tie sound; OQ-3 is
  closed). What remains is that the *path* is computable per entry (Requirement 7's `ext`
  field) while the *format* is the user's call — the transcode fork below, not a documentation
  defect.

### Needs the user — each changes a requirement's shape

- **How does the script decide a model accepts a seed?** Requirement 10's three-way seed rule
  needs a discriminator and there is none: Requirement 8 forbids model introspection, and
  Requirement 13's field list has no flag for it. Three candidates, three different costs — a
  **schema fetch** from the version endpoint (introspection, which Requirement 8's gate rule
  currently rules out), **try-and-retry** on a 422 rejection (one wasted round trip per new
  model, and 422 has other causes), or a **manifest field** such as `seedSupported` (free, but
  another thing the user must know and get right). Left unanswered, the cheapest legal
  implementation marks every entry `reproducible: false` and Requirement 10's only testable
  quantifies over the empty set — reproducibility passes vacuously and buys nothing.
- **Which image model and which audio model?** Requirement 10 pins whatever is chosen and
  Requirement 13 holds it per entry; Requirement 8 needs an image model that emits alpha and
  can be asked for a square render. **Stage 2 cannot start without this.**
- **If no audio model emits mp3: declare `ext: wav` and ship wav, or install ffmpeg?** The
  second adds an external binary no doc authorizes. Requirement 8 permits either and forbids
  pretending; Requirement 7 verifies whichever is declared against the bytes.
- **The logo's subject and brief.** Nothing states what the logo *is*. The handoff's placeholder
  is *"an 11pt-padded 3×3 grid (gap 5) of 3×3 dot clusters (gap 2) … — 81 dots, the game
  itself"*, followed by *"Replace with real art"* — which reads either as the brief for the real
  logo or as a description of the thing being replaced. Requirement 13 forbids the script
  inventing the prompt, so this is the user's to write.
- **Confirm the script's tree.** Requirement 1 fences it inside `src/Tic-Tac-Toe-Extreme` and
  Requirement 12's `git` invocation follows; moving it out changes both.
- **Are generated binaries committed?** `Theming.md` → Where Themes Live says themes are
  *"contained within the codebase. Bundled/shipped with the app"*, implying the assets they
  reference ship too — but nothing states it, and Requirement 12's git check is undecidable
  until it lands.
- **The real asset total.** Requirement 6 fixes the floor, not the total: how many of the five
  slots Classic overrides (`P5-01` open question 2), whether Classic authors its own logo, and
  whether a whole-game tie needs its own sound (`P2-02` → **OQ-2**, which that PRD mirrors to
  `P3-04` → OQ-7 — *answer it once, there*). `buttonTap` is settled at one sound (`P2-02` →
  OQ-3, closed).
- **Is the app icon generated here?** `Tech Design.md` → Decisions → *The app icon* settles that
  the app ships a **1024×1024 icon, that it is not the main-menu logo, and that it lives in the
  iOS asset catalog rather than the Flutter `assets/` tree** — only production is open. **If
  yes**, Requirement 3 must widen to permit `ios/Runner/Assets.xcassets/`. **If no**, it stays
  unowned roster-wide: `P5-03-release-fastlane.md` req 23 records that **no PRD puts an icon in
  the catalog** and has no supplier.
- **Reproducibility, confirming Requirement 10.** Either the single script-written metadata
  file as written, or an explicit "generation is not reproducible." Requirement 10 takes the
  first because the second cannot be inferred; reversing it is the user's call.
- **Where does the token live on the machine?** Requirement 11 fixes the variable name; shell
  profile, a local `.env`, or a secrets tool is a preference nothing records.
- **The About Us team photos.** `design_handoff_game_ui/README.md` → Fidelity names *"the About
  Us copy and team photos on 1c"* as placeholders alongside the logo. Screen `1c` is absent
  from `Menus and UI.md` → Screens (so far) and **no PRD owns it**. Whether this is an
  asset-generation question at all is doubtful — real team photos are not something Replicate
  produces.
- **Replicate output licensing.** `P5-03-release-fastlane.md` req 24 and its Open Question D
  need the terms attached to model output before submission can answer the content-rights
  question, and record that *"`P5-02` generates assets without stating their terms."* It may
  also constrain the model choice. This PRD cannot establish the facts.
