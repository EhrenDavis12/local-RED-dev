# PRD: Asset Generation — Replicate

> **Status:** Draft · **Deferred — explicitly not now.** Source docs read: `Tech Design.md`,
> `Theming.md`, `Menus and UI.md`, `Game Overview.md`, `Game Board Design.md`, `Animations.md`,
> `Rules.md`, `roadmap.md`, and the read-only reference asset `design_handoff_game_ui/`
> (`README.md` → *Assets*). `Alternative Game Styles.md` is a declared parking-lot doc and was
> not sourced from.

**Wave:** P5 · **File:** `P5-01-asset-generation-replicate.md`

**This work does not start until an asset is actually needed.** The decision behind this PRD
sets timing as part of the answer: *"We don't have to start now and it's best to do what we can
without images or music but once needed Replicate can help us out here."* (`Tech Design.md` →
Decisions → *Where do sound and art assets come from?*). Every wave above ships with
placeholders. This document exists so that the tooling, when it is finally built, is built to
the constraints already stated — not so that it gets built next.

**Depends on:** `P1-01-app-scaffold.md` — the `assets/themes/`, `assets/images/` and
`assets/audio/` folders and the `pubspec.yaml` asset declarations exist there first.

**Depended on by (each ships with placeholders until then):** `P3-01-main-menu.md` (the logo
slot), `P4-01-audio.md` (playback, which must work before any generated asset exists),
`P4-04-classic-theme.md` (the splat), `P1-03-theme-system.md` (the slots the assets fill).

---

## Problem

The game has asset slots and no assets. The logo on the main menu is a placeholder
(`design_handoff_game_ui/README.md` → *Assets*: *"Logo — placeholder only. Needs real art."*),
and no sound has been produced at all (same section: *"Sounds — none produced. Neon's signature
is an electric buzz; Classic Red vs Blue is a splat."*). The theme system requires every theme
to supply mark art and sounds (`Theming.md` → *What a Theme Controls*), so the placeholders are
a real gap, just not an urgent one.

The risk this PRD guards against is not the missing art — it is how the art gets made. The user
has done this before and named the failure mode: a generation system that accumulates a script
per asset and leaves debris behind.

## Goal

When an asset is finally needed, one script makes a Replicate API call for it and writes the
result into the project's designated asset folder — and nothing else is left behind. There is
no generator per asset type, no script per asset, and no junk in the tree after a run. The same
one script serves both audio (the Neon buzz, the Classic splat) and art (the logo).

## Requirements

1. **Nothing in this PRD is built until an asset is actually needed.** Waves P1–P4 must be
   completable with placeholder art and no audio files; discovering that some upstream work is
   blocked on a generated asset is a defect in that upstream PRD, not a reason to pull this one
   forward.
   *(`Tech Design.md` → Decisions → Where do sound and art assets come from? — **"Generated
   with Replicate when we actually need them — not now"**, and the timing paragraph)*

2. **Exactly one script performs the Replicate API call.** Testable as: after this PRD is
   built, the repository contains one asset-generation script, and generating an additional
   asset adds no new script.
   *(same Decision: *"Just one script that makes the API call with what we need. Not a script
   of every asset generation."* and the doc's own gloss: **"one script that makes the API call",
   not a generator per asset type**)*

3. **That one script covers both audio and images.** The assets named by the decision are the
   **Neon buzz**, the **Classic splat**, and the **logo**; all three are produced by the same
   script, not by an audio script and an image script.
   *(same Decision — *"This answers both the sound assets (the Neon buzz, the Classic splat)
   and the art (the logo)"*; the buzz and splat are `Theming.md` → Theme Catalog, the logo is
   `Menus and UI.md` → Decisions → Does the main menu need a title/logo?)*

4. **Generated assets are written into the designated asset folders** — art into
   `assets/images/`, audio into `assets/audio/`. The script does not write generated output
   anywhere else in the tree. `assets/themes/` holds theme YAML and is not a destination for
   generated output.
   *(`Tech Design.md` → Decisions → Project structure — layer-first, which names
   `assets/themes/`, `assets/images/` and `assets/audio/` as **"the designated folders for
   assets required by Where do sound and art assets come from?"**)*

5. **A run leaves no junk behind.** After the script produces an asset, the only new or changed
   files in the working tree are the generated asset(s) in the folders of Requirement 4 — no
   temp files, no per-run scratch scripts, no response dumps, no leftover intermediate output.
   Testable as: `git status` after a run shows the generated asset and nothing else.
   *(same Decision — *"we just need the APIs and will need to build our own system that
   operates clean and generates no junk"*, *"I would prefer to not have junk scripts lying
   around"*, and the doc's gloss **"no leftover scripts"**)*

6. **fey-tactics is consulted for the API call only.** Its system is explicitly not adopted:
   *"do not take on the system from fey-tactics as it's not a good system we just need the APIs
   and will need to build our own."* Testable as: nothing beyond the shape of the Replicate API
   call is carried over, and the resulting tooling is our own.
   *(same Decision. Note the separate, already-recorded warning that fey-tactics also uses the
   legacy `StateNotifier` API — `Tech Design.md` → Decisions → State management — Riverpod —
   which is the same "reference, not template" posture applied elsewhere.)*

7. **The transparent-background claim is confirmed against the model card at first use, before
   anything relies on it.** Recorded exactly as hedged: the user notes that the Replicate model
   `sourceful/riverflow-2.0-pro` *"does allow for png transparent background images"* — **that
   is the user's note, not verified against the current model card, and not a model choice.**
   No requirement here selects a model.
   *(`Tech Design.md` → Decisions → Where do sound and art assets come from? — *"Worth
   confirming at first use"*)*

## Out of Scope

Referenced by filename or by decision rather than specified here:

- **The audio playback system** — `audioplayers`, the one-shot sound effects, the global mute.
  It must work before any generated asset exists → `P4-01-audio.md`.
- **The theme system's asset slots** — which sounds and mark images a theme declares, and how
  they are named and resolved → `P1-03-theme-system.md`. This PRD produces files; it does not
  define the slots they fill.
- **The logo's placement on the menu** → `P3-01-main-menu.md`.
- **The Classic Red vs Blue theme**, including which values it overrides → `P4-04-classic-theme.md`.
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
  anywhere. *(`Tech Design.md` → Decisions → Where do sound and art assets come from?)*

### Raised by this PRD, not by the design docs (mine, and clearly marked)

The decision settles *how many* scripts and *where the output goes*. It is silent on the
following, and each is a decision an implementer would otherwise make by accident:

- **Where does the Replicate API key live?** No doc mentions credentials. `Tech Design.md` →
  Decisions → CI — local builds only means there is no CI secret store to put it in, so it is
  a local-machine question — but "which local mechanism" is unanswered.
- **Are generated assets committed to the repo?** `Theming.md` → Where Themes Live says themes
  are *"contained within the codebase. Bundled/shipped with the app"*, which implies the assets
  they reference ship too — but nothing states whether the binary output of a generation run is
  committed, and Requirement 5's `git status` test reads differently depending on the answer.
- **What is the script's interface?** *"One script that makes the API call with what we need"*
  does not say what "what we need" is passed as — CLI arguments, a manifest file, prompts held
  in the script — nor what language it is written in, nor where it lives (inside
  `src/Tic-Tac-Toe-Extreme/` or beside it). A prompt manifest would be the natural way to keep
  one script serving many assets, but that is my inference and is not written down.
- **Is generation reproducible?** Whether the prompt, model version and seed for each asset are
  recorded so an asset can be regenerated, and if so where — the "no junk lying around"
  constraint pushes against scattering per-asset metadata files, and no doc resolves that
  tension.
- **Where is fey-tactics?** It is named as the reference for the API call, but no `srcRoot` in
  `project.json` points at it and it is not present in this repo. Consulting it needs a path.
- **What exactly gets generated, in what format?** Beyond the three named assets — the Neon
  buzz, the Classic splat, the logo — no doc lists the full asset set, file formats, image
  dimensions or audio length/sample rate. `Theming.md` → What a Theme Controls → Audio lists
  six sound events per theme, which suggests the eventual list is longer than two sounds, but
  it is not written as an asset manifest.
