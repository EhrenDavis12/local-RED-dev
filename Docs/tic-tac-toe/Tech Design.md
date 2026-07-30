# Tech Design

> **Status:** Brain dump / early tech decisions. Contradictions are expected and OK.
> Nothing here is settled except what's under **Decisions**.
>
> This doc covers *how we build it*. What we're building lives in
> [Game Overview](./Game%20Overview.md), [Rules](./Rules.md),
> [Game Board Design](./Game%20Board%20Design.md), [Menus and UI](./Menus%20and%20UI.md),
> [Theming](./Theming.md), and [Animations](./Animations.md).

## Decisions

### Framework — Flutter
**Flutter.** Already in use for the game.

The reason it fits: it compiles to **both Android and Apple** from one codebase, so we're
not writing the game twice.

### Primary target — Apple
**iOS is the primary target as of right now.** Android is supported by virtue of Flutter,
but Apple is what we're building and testing against first.

Practical meaning: when a platform question comes up, iOS wins. Android is a
build-target, not a design constraint.

### Language — Dart
**Dart.** Comes with Flutter.

### How is a theme represented?
**JSON or YAML would be a good universal theme like object that can be loaded in.**

Themes are "contained within the codebase" for now either way.

### How does fallback-to-Neon work?
**Merge over Neon.** Each theme gets *materialized* into a complete theme at startup by
merging over Neon.

### Do we use Flutter's ThemeData/ThemeExtension, or roll our own?
**Use the ThemeData/ThemeExtensions from Flutter as possible filled out from our theme
JSON/YAML file. The remaining parts not supported in the Flutter theme. Will need to be
implemented on our own.**

### Do sounds and animations live in the same theme object?
**All live in the same theme object And we give what we can to the flutter themeData and
handle the rest ourselves all from the same doc.**

### Orientation
**Portrait only.**

### Minimum iOS version
**iOS 13.**

### Is the game logic separate from Flutter?
**Yes.** The rules engine — board state, legal moves, sending rule, win/cat-game detection,
free-choice state — is **pure Dart with zero Flutter imports**, and the UI layer reads from
it.

The upside stands as written: the rules become unit-testable without a widget test, and the
rules are the part where bugs actually hurt (sending rule, dead-quadrant free choice,
big-board draw).

### Persistence package
**`shared_preferences`.** Four small key-value preferences, nothing sensitive, and no game
state to save — the obvious default stands.

### Unit tests for the rules engine
**Yes — this is where the real complexity is.**

### Do themes pick their own font?
**Yes.** [Theming](./Theming.md) → Architectural Rule already lists fonts among the things
that must never be hardcoded: *"No hardcoded colors, backgrounds, fonts, piece styles,
sounds, or animations anywhere in the code."* So a font is a themeable value like any
other, and the theme object needs somewhere to put one.

### How is the board rendered?
**Widgets.** *"ok widgets is the winner lets make that happen."*

81 `GestureDetector`s in nested `GridView`/`Column`s, not a `CustomPainter`.

The deciding argument is the theme rule. A widget-based theme slot can be typed as a
`Widget` rather than a value, so a theme supplies its mark art directly — an icon, an
image, an animation — instead of the board code having to know how to paint it.
[Theming](./Theming.md) → Architectural Rule forbids hardcoded piece styles: with a
painter, each new theme idea risks a code change; with widgets it does not.

Nested containers also let quadrant-level and cell-level highlight treatments **layer**
rather than compete, which is what [Game Board Design](./Game%20Board%20Design.md) →
Three highlights on screen at once requires.

**Watch out for:** nested `Border.all` doubles interior grid lines — two adjacent 1px
borders read as 2px — and hairlines can look uneven at fractional device pixel ratios.
The known fix is a hybrid: widgets for cells and marks, plus one thin `CustomPaint`
overlay drawing only the grid lines. That is an escape hatch, not a decision taken.

Widgets are the weaker choice **only** if recursion ever goes deeper than two levels,
since you cannot build an unbounded widget tree and would need level-of-detail
management. [Game Overview](./Game%20Overview.md) → Recursion depth fixes depth at two
levels, so this does not currently bite — and the pure-Dart rules engine already decided
means the renderer stays replaceable if that ever changes.

### Audio package
**`audioplayers`.** The choice was delegated: *"i have no preference. what would be best
for our case use that."*

One-shot sound effects is its core use case; it plays bundled assets by path, which fits
sounds being resolved from the theme object; and it handles several overlapping short
sounds without ceremony. Its platform coverage also matches the porting ambition under
**Device support** below.

`just_audio`'s advantages are streaming, playlists, gapless playback and background audio
— none of which this game needs, since [Theming](./Theming.md) → Sound Decisions
scopes this version to one-shot effects only. If background music later becomes
central, `just_audio` can be added alongside for the music channel specifically.

### Marks — image or icon, supplied by the theme
**"Due to themes im thinking the marks can be an image or an icon. For example neon just
needs icons of X and O while the dinosaur theme might use a T-Rex as an Icon."**

So marks are asset slots on the theme, not shapes drawn in board code. This is the same
property the widget renderer decision above buys: a theme slot typed as a `Widget` can
hold an `Icon`, an `Image`, or anything else, so the board never has to know what a mark
looks like.

This also settles the marks question in [Theming](./Theming.md) — see Theming →
Decisions → Marks beyond X and O.

### Device support
**"We will want to port our game over to every devices. iPhone will be the primary target
iPads next then will want to branch out to all media devices. such as Android in the far
future."**

Ordering, concretely: **iPhone first, iPad second, Android far future.** This refines
**Primary target — Apple** above rather than replacing it — iOS still wins any
platform question today.

"All media devices" is recorded as stated and is not yet scoped to particular platforms.

### Where do sound and art assets come from?
**Generated with Replicate when we actually need them — not now.** This answers both the
sound assets (the Neon buzz, the Classic splat) and the art (the logo): *"I have used
Replicate in the past so will need to build out a clean Replicate API calling mechanism
for this."*

Timing is part of the answer: *"We don't have to start now and it's best to do what we can
without images or music but once needed Replicate can help us out here."*

The requirement on how it gets built, as stated:

> *"You can check out the fey-tactics for the API call however do not take on the system
> from fey-tactics as it's not a good system we just need the APIs and will need to build
> our own system that operates clean and generates no junk. We will have to have
> designated folders for assets. And I would prefer to not have junk scripts lying around.
> Just one script that makes the API call with what we need. Not a script of every asset
> generation."*

Concretely: **one script that makes the API call**, not a generator per asset type;
**designated folders for assets**; no leftover scripts.

**Watch out for:** fey-tactics is a reference for the API call only, and it has no audio
precedent to copy — its own asset plan states *"Audio assets are not generated by
Replicate or image AI tools."* Everything generated there is imagery, so the audio half
is greenfield.

For calibration on what's being rejected: fey-tactics' `scripts/` runs to 2,343 lines
across 10 top-level scripts plus a `lib/` and a `prompts/` tree, with the Replicate call
implemented twice and not shared. It also already had an agent whose description promised
it "does NOT mass-generate trash, keeps scripts/ clean" — and the sprawl happened
anyway. That is the argument for the one-script rule being enforced structurally rather
than left to discipline.

Worth confirming at first use: the user notes that the Replicate model
`sourceful/riverflow-2.0-pro` *"does allow for png transparent background images."* That
is recorded as the user's note, not verified against the current model card, and not a
model choice — but it bears directly on the no-junk rule. Three of the fey-tactics
scripts (`clean-unit-sprites.py`, `remove-bg.sh`, `chroma-key.py` — 295 lines together)
exist only because their model cannot emit transparency and generates onto a green chroma
plate that then has to be cut out. Native transparent output would remove the need for
that whole category of post-processing.

A **Replicate agent** may follow — *"we might need to build out a Replicate Agent that
has the skills to utilize Replicate for both audio and images when needed"* — but that
is hedged and explicitly not now, and it would live in the agent system rather than in
this doc.

---

## What the Design Docs Already Imply
Some technical requirements are already locked by decisions made elsewhere. Listing them
here so they don't get re-litigated:

| Requirement | Comes from |
|---|---|
| **Fully offline.** No backend, no network, no accounts. | Two players, one phone |
| **Local persistence** for 4 values: theme, sound, vibrate, animations | [Menus and UI](./Menus%20and%20UI.md) → Persistence |
| **No game-state persistence.** Games aren't saved. | Same |
| **Audio playback** for one-shot sound effects (no music yet) | [Theming](./Theming.md) |
| **Haptics** on every valid click | [Game Board Design](./Game%20Board%20Design.md) → Haptic Rule |
| **A theme system with fallback** — every visual/audio/motion value resolves through the active theme, falling back to Neon | [Theming](./Theming.md) |
| **Animations toggleable off entirely**, with instant state changes instead | [Animations](./Animations.md) |
| **Portrait phone layout**, whole 9x9 board visible, no zoom | [Game Board Design](./Game%20Board%20Design.md) |

### The theme system is the main architectural risk
> *"All of our code operates off of the theme. No code should be operating independently
> from the selected theme."*

This is the one constraint that touches every file, and it's the one that's expensive to
retrofit. Whatever we choose for state management and widget structure has to make
"every value comes from the theme" the *easy* path, not a discipline we have to maintain
by hand.

---

## Open Questions

These are the things I think we need to hammer out. Grouped roughly by how much they
block other work.

### 1. State management
What holds game state and settings? Options in rough order of ceremony:
`setState`/`InheritedWidget` → `provider` → `riverpod` → `bloc`.

Relevant considerations for this specific app:
- Game state is small and entirely local. There's no async, no network, no server sync.
- Settings and theme need to be readable from **everywhere**, including deep in the board
  widget tree.
- Do you have a preference already, or a pattern you've used in your existing Flutter
  work on this?

### 2. Project structure
Rough folder layout — where do rules, theme definitions, widgets, and assets live? Worth
agreeing before there's much code, since the theme rule means theme access shows up
everywhere.
<!-- Constraint from Decisions → Where do sound and art assets come from: assets live in
     designated folders. That constrains this question, it does not answer it — no
     layout is specified yet. -->

### 3. Testing
- Widget/golden tests for the board and its highlight states?
- Or keep it light and test by playing?

### 4. Build and distribution
- Is this going to the **App Store**, or is it a personal/TestFlight build?
- Bundle identifier / app name?
- Any CI, or local builds only?

### 5. Existing code
You said you've **already been using Flutter to write the game** — how far along is it,
and does any of it survive into this design? That changes whether this doc describes a
fresh build or a refactor toward these decisions.

<!-- The repo currently contains no application code — docs only. Worth confirming
     whether the existing Flutter work lives somewhere else. -->
