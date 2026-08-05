# PRD: Asset Generation — Replicate

> **Status:** Draft · **Deferred — explicitly not now.** Source docs read: `Tech Design.md`,
> `Theming.md`, `Menus and UI.md`, `Game Overview.md`, `Game Board Design.md`, `Animations.md`,
> `Rules.md`, `roadmap.md`, and the read-only reference asset `design_handoff_game_ui/`
> (`README.md` → *Assets*, `neon.theme.json`, `themes.catalog.json`). `Alternative Game
> Styles.md` is a declared parking-lot doc and was not sourced from.

**Wave:** P5 · **File:** `P5-02-asset-generation-replicate.md`

**This work does not start until an asset is actually needed.** The decision behind this PRD
sets timing as part of the answer: *"We don't have to start now and it's best to do what we can
without images or music but once needed Replicate can help us out here."* (`Tech Design.md` →
Decisions → *Where do sound and art assets come from?*). Every wave above ships with
placeholders, and every wave above must be completable without any generated asset —
discovering that upstream work is blocked on one is a defect in that upstream PRD, not a reason
to pull this one forward. This is a scheduling constraint, not a requirement: it is not
assertable, and any run that implements this PRD has already set it aside deliberately. This
document exists so that the tooling, when it is finally built, is built to the constraints
already stated — not so that it gets built next.

**Depends on:** `P1-01-app-scaffold.md` requirement 3 — which creates the `assets/themes/`,
`assets/images/` and `assets/audio/` folders. **It creates the folders only.** No requirement in
`P1-01` declares them under `pubspec.yaml`'s `flutter: assets:` key, and `P1-01`'s own Open
Questions show that even declaring the theme YAML is unsettled. A file this script writes into
`assets/audio/` is therefore **not guaranteed to be bundled into the app** — see Open Questions.

**Depended on by (each ships with placeholders until then):** `P4-01-main-menu.md` (the logo
slot), `P2-02-audio.md` (playback, which must work before any generated asset exists),
`P5-01-classic-theme.md` (the splat), `P1-03-theme-system.md` (the slots the assets fill).
All of those ship in earlier waves, without assets, by design.

---

## Problem

The game has asset slots and no assets. The logo on the main menu is a placeholder
(`design_handoff_game_ui/README.md` → *Assets*: *"Logo — placeholder only. Needs real art."*),
and no sound has been produced at all (same section: *"Sounds — none produced. Neon's signature
is an electric buzz; Classic Red vs Blue is a splat."*). Neon's five playable sound slots hold
the strings `"TODO: neon buzz one-shot"` and four `"TODO"` (`neon.theme.json` → `sound`), while
`P1-03-theme-system.md` requirement 11 requires Neon to define every slot with no gaps — so the
gap is real, just not urgent.

**The sound gap is real; the mark-art gap is not.** All three of Neon's marks are glyphs, not
images — `neon.theme.json` → `marks` gives `playerOne ✕`, `playerTwo ○` and `catGame Ø`, each
`"kind": "glyph"` in Inter. `Theming.md` → Decisions → *Marks beyond X and O* settles only that
a theme *may* supply mark art; Neon does not, and whether Classic overrides the marks at all is
an open question in `P5-01-classic-theme.md`. **No mark images are needed today, and generating
✕/○ art would be work nobody asked for.**

The risk this PRD guards against is not the missing art — it is how the art gets made. The user
has done this before and named the failure mode: a generation system that accumulates a script
per asset and leaves debris behind.

## Goal

When an asset is finally needed, one script makes a Replicate API call for it and writes the
result into the project's designated asset folder — and nothing else is left behind. There is
no generator per asset type, no script per asset, and no junk in the tree after a run. The same
one script serves both audio (Neon's sound set, Classic's override) and art (the logo).

## Requirements

1. **Exactly one script performs the Replicate API call.** Testable as: after this PRD is
   built, there is one asset-generation script, and generating an additional asset adds no new
   script. *Which* tree that script lives in is unresolved — see Open Questions.
   *(`Tech Design.md` → Decisions → Where do sound and art assets come from? — *"Just one
   script that makes the API call with what we need. Not a script of every asset generation."*
   and the doc's own gloss: **"one script that makes the API call"**, not a generator per asset
   type)*

2. **That one script covers both audio and images**, rather than an audio script and an image
   script.
   *(same Decision — *"This answers both the sound assets (the Neon buzz, the Classic splat)
   and the art (the logo)"*)*

3. **"The buzz" and "the splat" are sonic *characters*, not filenames — the asset set is
   larger than three files.** Reading the decision's phrasing as a three-item manifest
   under-generates, and three settled facts say so:

   - **`signature` is descriptive metadata that is never played.** `neon.theme.json` →
     `sound.signature` holds the word `"buzz"`, and `themes.catalog.json` →
     `signatureSound: "splat"` is the same kind of value. *(`P2-02-audio.md` requirement 7 —
     *"`signature` is descriptive metadata, not an asset"*, and the audio layer never plays
     it.)* Generating one file called "the buzz" satisfies nothing.
   - **Neon needs five playable sounds, not one.** `placeMark`, `claimQuadrant`, `catGame`,
     `winGame` and `buttonTap` are the moments that fire, all five currently `"TODO"`.
     *(`P2-02-audio.md` requirement 6; `Theming.md` → What a Theme Controls → Audio;
     `P1-03-theme-system.md` requirement 11 — Neon must define every slot, being the one theme
     with nothing to fall back to)*
   - **Classic overrides at least one of those five, and the count is open.** *"Whether the
     splat replaces only the place-a-mark sound, or several of the five audio slots, is not
     written down"* — `P5-01-classic-theme.md` → Open Questions.

   So the floor is **five Neon sounds + at least one Classic sound + the logo**, and the true
   figure is higher than three and not yet fixed. The full manifest is an open question below;
   this requirement fixes only that the three-item reading is wrong.

4. **Generated assets are written into the designated asset folders** — art into
   `assets/images/`, audio into `assets/audio/`. The script does not write generated output
   anywhere else in the tree. `assets/themes/` holds theme YAML and is not a destination for
   generated output.
   *(`Tech Design.md` → Decisions → Project structure — layer-first, which names
   `assets/themes/`, `assets/images/` and `assets/audio/` as **"the designated folders for
   assets required by Where do sound and art assets come from?"**)*

5. **A run leaves no junk behind.** After the script produces an asset, the only new or changed
   files are the generated asset(s) in the folders of Requirement 4 — no temp files, no per-run
   scratch scripts, no response dumps, no leftover intermediate output.
   *(same Decision — *"we just need the APIs and will need to build our own system that
   operates clean and generates no junk"*, *"I would prefer to not have junk scripts lying
   around"*, and the doc's gloss **"no leftover scripts"**)*

   **How to check it, and how not to.** `src/Tic-Tac-Toe-Extreme` is a **git submodule**, so
   `git status` from the repo root shows only a changed submodule pointer and never a single
   file inside it. A root-level `git status` therefore passes no matter how much junk a run
   leaves — a vacuous check, and one this repo has already shipped once (`CLAUDE.md` →
   *`srcRoots` are git submodules*). It must be scoped to the tree the run actually wrote
   into:

   ```
   git -C src/Tic-Tac-Toe-Extreme status
   ```

   and, if the script lives outside the submodule, a root-level `git status` **as well**, not
   instead. Whichever trees a run can touch, each is checked in its own right.

   Second caveat: a `.gitignore` entry makes junk invisible to `git status` too, so a clean
   `git status` is evidence, not proof. Junk that is ignored is still junk lying around. The
   assertion is about what is on disk after a run, so a listing of the working tree — not only
   its git-visible portion — is what settles it.

6. **fey-tactics is consulted for the API call only, and its system is not adopted.** As
   stated: *"do not take on the system from fey-tactics as it's not a good system we just need
   the APIs and will need to build our own."*

   This is a **code-review criterion, not a test.** It asserts a negative about provenance —
   that nothing beyond the shape of the API call was carried over — and no test can establish
   where code came from. A reviewer reads the resulting tooling and judges whether it is our
   own system or theirs.

   Two facts about its force: fey-tactics is **not reachable from this project** — it is not a
   `srcRoot` in `Docs/tic-tac-toe/project.json` and sits outside this repo — and Replicate's
   HTTP API is publicly documented, so consulting fey-tactics is not required in order to make
   the call. The requirement's real weight is therefore **prohibitive** ("do not adopt their
   system"), with the consultation an option rather than a step.
   *(same Decision. The same "reference, not template" posture is already recorded against
   fey-tactics elsewhere — `Tech Design.md` → Decisions → State management — Riverpod warns it
   uses the legacy `StateNotifier` API.)*

7. **Conditional, and only if that model is the one used: confirm the transparent-background
   claim against the model card before anything relies on it.** Recorded exactly as hedged:
   the user notes that the Replicate model `sourceful/riverflow-2.0-pro` *"does allow for png
   transparent background images"* — **that is the user's note, not verified against the
   current model card, and not a model choice.** No requirement here selects a model, and
   which image model is used is itself open below — so this requirement asks for verification
   of a property of a model that may never be chosen. It binds at first use of that model and
   not before.
   *(`Tech Design.md` → Decisions → Where do sound and art assets come from? — *"Worth
   confirming at first use"*)*

## Out of Scope

Referenced by filename or by decision rather than specified here:

- **The audio playback system** — `audioplayers`, the one-shot sound effects, the global mute.
  It must work before any generated asset exists → `P2-02-audio.md`.
- **The theme system's asset slots** — which sounds and mark images a theme declares, and how
  they are named and resolved → `P1-03-theme-system.md`. This PRD produces files; it does not
  define the slots they fill.
- **The logo's placement on the menu** → `P4-01-main-menu.md`.
- **The Classic Red vs Blue theme**, including which values it overrides →
  `P5-01-classic-theme.md`.
- **Mark art.** Neon's marks are glyphs and need no image; whether Classic overrides marks is
  `P5-01-classic-theme.md`'s open question, not this PRD's to pre-empt by generating art.
  *(`neon.theme.json` → `marks`; `Theming.md` → Decisions → Marks beyond X and O)*
- **Inter 400/500/600 and the Phosphor icon set** — third-party dependencies to bundle, not
  generated assets. `Tech Design.md` notes explicitly that **neither is Replicate-generated**.
  *(`design_handoff_game_ui/README.md` → Assets; `Tech Design.md` → Decisions → Where do sound
  and art assets come from?, trailing note)*
- **A Replicate agent.** *"We might need to build out a Replicate Agent that has the skills to
  utilize Replicate for both audio and images when needed"* — recorded as **hedged and
  explicitly not now**, and `Tech Design.md` places it in the agent system rather than in the
  game. Not this PRD's territory in either timing or location.
  *(`Tech Design.md` → Decisions → Where do sound and art assets come from?)*
- **`Alternative Game Styles.md`** — declared parking lot; not what is being built.

## Open Questions

### From the design docs — unresolved, worded as the docs word them

- **Whether `sourceful/riverflow-2.0-pro` in fact *"does allow for png transparent background
  images"*** — recorded as the user's note, *"worth confirming at first use"*, not verified and
  not a model choice. Which model is used for images, and which for audio, is not decided
  anywhere. Requirement 7 is conditional on this.
  *(`Tech Design.md` → Decisions → Where do sound and art assets come from?)*
- **Who produces the app icon, and is it generated or hand-made?**
  *(`Tech Design.md` → Open Questions → 3. Build and distribution)* See the folder conflict
  below.

### Raised by this PRD, not by the design docs (mine, and clearly marked)

The decision settles *how many* scripts and *where the output goes*. It is silent on the
following, and each is a decision an implementer would otherwise make by accident:

- **Which tree does the script live in — `local-RED-dev` or `src/Tic-Tac-Toe-Extreme`?**
  Requirement 1 says "one script" and Requirement 5 checks the tree it wrote into, but "the
  repository" is ambiguous between the mono repo and the submodule. The script is a build-time
  tool, not app code; it need not be Dart and may not belong inside the Flutter app at all.
  Both requirements depend on the answer, so it is not a detail to settle at the keyboard.
- **The app icon cannot live where Requirement 4 allows, and no PRD produces it.**
  `Tech Design.md` → Decisions → *The app icon* settles that the app ships a **1024×1024 icon,
  that it is not the main-menu logo, and that it lives in the iOS asset catalog rather than the
  Flutter `assets/` tree** — only who produces it, and whether it is generated, is open. That
  creates a direct conflict: Requirement 4 forbids this script writing outside `assets/`, so if
  the icon is ever generated here, Requirement 4 as written blocks it and would need widening
  to `ios/Runner/Assets.xcassets/`. Meanwhile **no PRD in the roster produces the icon** — this
  one does not claim it, and `P5-03-release-fastlane.md` raises the same missing asset from the
  store side.
- **Nothing declares the generated assets in `pubspec.yaml`.** `P1-01-app-scaffold.md`
  requirement 3 creates `assets/audio/` and `assets/images/` but declares neither under
  `flutter: assets:`, and `P1-01` → Open Questions shows even the theme YAML declaration is
  unsettled. A generated file can therefore satisfy every requirement here and still not be
  bundled into the app. Which PRD adds the declaration — `P1-01`, `P1-03-theme-system.md`, or
  this one — is unassigned.
- **Where does the Replicate API key live?** No doc mentions credentials. `Tech Design.md` →
  Decisions → CI — local builds only means there is no CI secret store to put it in, so it is
  a local-machine question — but "which local mechanism" is unanswered.
- **Are generated assets committed to the repo?** `Theming.md` → Where Themes Live says themes
  are *"contained within the codebase. Bundled/shipped with the app"*, which implies the assets
  they reference ship too — but nothing states whether the binary output of a generation run is
  committed, and Requirement 5's git checks read differently depending on the answer.
- **What is the script's interface?** *"One script that makes the API call with what we need"*
  does not say what "what we need" is passed as — CLI arguments, a manifest file, prompts held
  in the script. A prompt manifest would be the natural way to keep one script serving many
  assets, but that is my inference and is not written down.
- **Is generation reproducible?** Whether the prompt, model version and seed for each asset are
  recorded so an asset can be regenerated, and if so where — the "no junk lying around"
  constraint pushes against scattering per-asset metadata files, and no doc resolves that
  tension.
- **What is the real asset manifest, and in what formats?** Requirement 3 fixes the floor —
  five Neon sounds, at least one Classic sound, the logo — but not the total. Unfixed: how many
  of the five Classic overrides (`P5-01-classic-theme.md` → Open Questions), whether the
  whole-game draw needs its own sound (`P2-02-audio.md` → OQ-5), whether `buttonTap` is one
  sound or several (→ OQ-4), the app icon above, file formats, image dimensions, and audio
  length or sample rate. No doc anywhere lists the asset set as a manifest.
- **A third unowned placeholder: the About Us team photos.**
  `design_handoff_game_ui/README.md` → Assets names *"Team photos (1c) — placeholder only"*
  alongside the logo and the sounds. Screen `1c — About Us` is drawn in the handoff, is absent
  from `Menus and UI.md` → Screens (so far), and **no PRD owns it** — so neither the screen nor
  its photos have a home. Whether those photos are even a generated asset is unasked; real
  team photos are not something Replicate produces.
