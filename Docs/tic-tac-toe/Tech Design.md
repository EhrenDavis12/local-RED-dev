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

<!-- Resolved: the format is YAML. The bold answer above is the user's wording from when
     the choice was still open. See Decisions → What format are theme files — JSON or
     YAML? -->

### What format are theme files — JSON or YAML?
**YAML.**

YAML supports comments, which matters for a file that gets hand-edited per theme. The
cost is a dependency on the `yaml` package, where JSON would have needed none.

This settles the choice left open in **How is a theme represented?** above and in **Do we
use Flutter's ThemeData/ThemeExtension, or roll our own?** below. Both were written while
the choice was still open and both are left in the user's original wording.

### Theme identity — UUID
**Each theme carries a UUID in its YAML file, and that UUID is the theme's identity.**
*"the themes should be saved by UUID in the YAML files."*

Consequence worth naming: the persisted "selected theme" preference stores the UUID, not
the theme's name — so renaming a theme does not lose a player's selection. See
[Theming](./Theming.md) → Decisions → Does the theme persist between sessions.

### How does fallback-to-Neon work?
**Merge over Neon.** Each theme gets *materialized* into a complete theme at startup by
merging over Neon.

### Do we use Flutter's ThemeData/ThemeExtension, or roll our own?
**Use the ThemeData/ThemeExtensions from Flutter as possible filled out from our theme
JSON/YAML file. The remaining parts not supported in the Flutter theme. Will need to be
implemented on our own.**

<!-- Resolved: "theme JSON/YAML file" above means YAML. See Decisions → What format are
     theme files — JSON or YAML? -->

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
**`shared_preferences` — for the four player preferences.** Four small key-value
preferences, nothing sensitive — the obvious default stands.

Game state does not go here. It is saved too, in Hive — see **Game state storage — Hive**
below.

<!-- Superseded: this decision originally read "Four small key-value preferences, nothing
     sensitive, and no game state to save — the obvious default stands." The clause "no
     game state to save" no longer holds: game state persists. The choice of
     shared_preferences for the preferences themselves is unchanged; only its
     justification narrowed. See Decisions → Game state storage — Hive and Menus and UI →
     Persistence. -->

### Game state storage — Hive
**Hive.** Saved games — the board, whose turn it is, and the scoreboard — are stored in
Hive, not in `shared_preferences`.

Chosen over a plain JSON file and over `sqflite`. `shared_preferences` stays for the four
player preferences (see above); it is a key-value store for small scalars, the wrong shape
for a structured game state that gets read and rewritten as a unit.

This is what makes [Menus and UI](./Menus%20and%20UI.md) → Decisions → Does a game in
progress persist? and [Game Overview](./Game%20Overview.md) → Decisions → Scoreboard
lifetime implementable.

### Serialization and the storage layer
**`freezed` + `json_serializable` for the domain models in `engine/`, and a `storage/`
layer holding a repository interface with a Hive implementation that stores JSON. No Hive
`TypeAdapter`s.** The choice was delegated, with the criterion stated:

> *"I want to use the more comprehensive solution as this project will be used for more
> game templates later. These other games will have more depth to them. So pick the
> solution here carefully to enable the most future growth with the games"*

So the criterion is maximum future growth across several deeper games, not the smallest
thing that works for this one. What decided it, in order:

1. **Online multiplayer is already an intended direction** — **State management —
   Riverpod** below cites board sync as its reason. Network sync needs JSON. Hive
   `TypeAdapter`s produce a Hive-specific binary format that is useless over a wire, so
   adapters would mean writing JSON serialization as well, not instead. One format
   serving both local save and future sync beats two.
2. **Adapters couple the domain to the storage library.** `TypeAdapter` annotations sit
   on the model classes themselves. **Is the game logic separate from Flutter?** above
   keeps `engine/` clean; a repository interface means the engine never learns that Hive
   exists, and swapping storage later touches one layer instead of every model.
3. **Hive `typeId`s are a migration hazard** — manually assigned integers, where a
   collision or a reused id corrupts data. With JSON, versioning is a `schemaVersion`
   field read and migrated on load. That does not answer **Persisted data — versioning**
   under Open Questions, but it decides what shape that answer will take.
4. **`freezed` is the codegen that pays for itself.** **Game state is immutable** below is
   already settled, and hand-writing immutable classes with `copyWith` for deep game state
   is more boilerplate than hand-writing `toJson` — and it is the part that grows worst as
   the models deepen, which is the stated concern.

Precedent: fey-tactics runs freezed + json_serializable across 126 domain files and keeps
124 of them free of Flutter imports.

Three consequences worth naming, because they cut across other Decisions:

- **`storage/` is a new layer** in **Project structure — layer-first** below.
- **`hive_flutter` is not pure Dart, so it must never be imported from `engine/`.**
  `storage/` owns it.
- **Serialization lives with the model.** `toJson`/`fromJson` are generated into `engine/`
  by json_serializable — pure Dart, Flutter-free — while the Hive box, adapters-free,
  lives in `storage/`.

This does not change **Game state storage — Hive** above; Hive is still the store. It
decides what gets written into it, and who is allowed to know it is Hive.

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

### Do we add a test that fails on hardcoded theme values?
**Yes — add it, covering all six categories the Architectural Rule names.** An ordinary
test in the suite, not a custom analyzer plugin. It scans the source under `lib/` for
banned patterns outside the theme layer itself, and it holds a per-file baseline that
fails when a new violation appears. There is no application code yet, so **the baseline
starts at zero**.

<!-- "The theme layer" is concretely `lib/theme/`. See Decisions → Project structure —
     layer-first. -->

The six categories come straight from [Theming](./Theming.md) → Architectural Rule —
colors, backgrounds, fonts, piece styles, sounds, and animations. Indicative patterns to
catch, to be sharpened at the keyboard rather than settled here:

| Category | Roughly what the scan looks for |
|---|---|
| **Colors** | Raw `Color(0x…)` literals and references to Flutter's `Colors.*` palette |
| **Animations** | Hardcoded `Duration(…)` timing values |
| **Fonts** | `GoogleFonts.*` and literal `fontFamily:` values |
| **Piece styles** | Hardcoded `'X'`/`'O'` strings and `Icons.*` inside board widgets |
| **Sounds and backgrounds** | Literal `assets/…` paths outside the theme layer |

Why a test and not a lint: `dart analyze` cannot tell a legitimate reference inside the
theme layer from a hardcoded value in a widget — that is a semantic distinction, not a
syntactic one.

Durations are in scope because [Animations](./Animations.md) → Decisions → Duration lives
in the animation puts timing inside the theme's animation definitions, so a hardcoded
`Duration` is a theme value that escaped.

This is the structural enforcement that **The theme system is the main architectural
risk** below asks for, and it is what makes [Theming](./Theming.md) → Architectural Rule a
checkable rule rather than a matter of discipline.

Precedent: fey-tactics' `test/lint/faction_type_mechanical_use_test.dart` does exactly
this for a different rule and held. That same project had no such guard for theming and
ended up with roughly 900 hardcoded color sites against zero `Theme.of(context)` calls.

### State management — Riverpod
**Riverpod, without Riverpod's own codegen to start.** Plain `NotifierProvider`
declarations, no `@riverpod` annotations. Riverpod codegen can be adopted later without
rewriting the logic.

The reasoning, as stated:

> *"Sounds like Riverpod is more complex setup but provides more powerful features in
> the future. This can service as our same game state for future games as well that
> would be more complicated. Maybe going with riverpod would support a more complex
> game structure."*

> *"A question I have is why do we say their is no sync state. In the future of the
> Tic-tac-toe game we will have multiplayer so i want the tech to be chosen that can
> handle this state sync of a board. Can Provider handle that?"*

To answer that last question directly: `provider` *can* do async, but Riverpod is
materially better for a board whose state syncs over a network. `AsyncValue` models
loading, data and error as one sealed type, so no consumer can forget a state; `family`
gives per-game providers, which is exactly what fey-tactics uses `StreamProvider.family`
for in its realtime turn sync; and providers are readable outside the widget tree, which
a sync service reacting to network events needs.

It also covers the requirement that settings and the theme be readable from
**everywhere**, including deep in the board widget tree.

What decided it is the cost asymmetry: adopting Riverpod now is a modest concept cost,
while migrating to it later is a refactor across every widget that reads state.

**Watch out for:** fey-tactics uses `StateNotifier`, which is the legacy API. Use
`Notifier`/`NotifierProvider` — fey-tactics is a reference for the sync shape, not for
the API surface.

Narrowed since this was written: `build_runner` *does* run in this project — freezed and
json_serializable use it (see **Serialization and the storage layer** above). What is
being skipped is Riverpod's own codegen specifically, because it adds annotation concepts
this project does not need; that argument does not carry over to freezed, where the
codegen replaces boilerplate the project would otherwise hand-write. The Riverpod choice
itself is unchanged.

<!-- Superseded: the original state-management Open Question framed this as "Game state
     is small and entirely local. There's no async, no network, no server sync." The
     answer above supersedes that framing — it is what the second quote is responding
     to. -->

<!-- Superseded: this decision originally read "Riverpod, without codegen to start. Plain
     `NotifierProvider` declarations, no `build_runner`. Codegen can be adopted later
     without rewriting the logic." The clause "no `build_runner`" no longer holds:
     freezed and json_serializable run build_runner. Only the scope of the no-codegen
     claim narrowed — the Riverpod choice, and skipping Riverpod's own codegen, are
     unchanged. See Decisions → Serialization and the storage layer. -->

### Game state is immutable
**Immutable.** The engine never mutates a board in place — every move produces a new state
object, and that new object is what the UI renders.

The reasoning, as stated:

> *"Sounds like you already have the decision as immutable and we generate new state to
> make sure we trigger a rerender. sounds like we should continue with this."*

This is forced by **State management — Riverpod** above: a Riverpod `Notifier` only
rebuilds when its state is a *new* object, so a board mutated in place would render
nothing.

It also pins down the shape of the API that **Is the game logic separate from Flutter?**
leaves open. The engine exposes `Board applyMove(Board, Move)` returning new state, not
`board.play(move)` mutating in place — so the pure-Dart engine and the Riverpod layer
agree on how state changes.

### Project structure — layer-first
**Layer-first.** Group by kind, not by feature:

```
lib/
  main.dart
  app.dart
  engine/          ← pure Dart, zero Flutter imports
    board.dart
    rules.dart
  storage/         ← repository interface + Hive implementation
  theme/
    theme.dart     ← merged theme object
    loader.dart    ← YAML → theme
  state/           ← Riverpod providers
  ui/
    board/
    menus/
assets/
  themes/*.yaml
  images/
  audio/
```

Layer-first is simpler for one game with one main feature; feature-first buys a separation
this project does not need yet.

`storage/` is local persistence only — the repository interface and its Hive
implementation (see **Serialization and the storage layer** above). There is still **no
backend data layer**: nothing in the app talks to a server. One gets added if multiplayer
arrives.

<!-- Superseded: this previously read "There is **no `data/` layer**, because there is no
     backend yet. One gets added if multiplayer arrives." A local storage layer now
     exists, so the flat "no data layer" claim no longer holds; what is still absent is a
     backend. See Decisions → Serialization and the storage layer. -->

`assets/themes/`, `assets/images/` and `assets/audio/` are the **designated folders for
assets** required by **Where do sound and art assets come from?** above.

### Widget tests for the board — no golden tests
**Widget tests, no goldens.** Test that taps do the right thing and that the highlight
states appear. Skip golden image tests.

Testing by playing was the alternative offered and was not chosen.

The argument against goldens is that both reference projects specified them and neither
maintained one. fey-tactics has exactly one golden test, it is `skip`ed, and its reference
image was never committed — against 239 unit tests and 118 widget tests. The Sudoku
project has only the default `test/widget_test.dart` scaffold. Golden tests were specified
in both and effectively never happened in either.

This sits alongside **Unit tests for the rules engine** above, which covers the engine
layer, and **Do we add a test that fails on hardcoded theme values?** below.

### Fresh build, not a refactor
**A fresh build.** Nothing from the earlier Flutter work carries into this design — every
Decision in this doc describes something being built new, not refactored toward.

Confirmed against the repo: there is no application code yet, only a README in the source
tree.

### Distribution — public App Store release
**The App Store.** A public release, not a personal or TestFlight-only build.

That makes the App Store Connect listing a real deliverable — description, keywords,
screenshots, categories — which is what **Release tooling — fastlane** below manages.

### Bundle identifier
**`com.ehrendavis.tictactoeextreme`.** Lowercase reverse-DNS, the conventional Apple form.

Deliberately not modelled on the existing Sudoku app's `com.EhrenDaivs.sudoku`, which
misspells the surname and uses mixed case. The new identifier inherits neither.

**Watch out for:** a bundle identifier is effectively permanent once the app has been
submitted to App Store Connect, so this is not a name to revisit casually.

### CI — local builds only
**No CI. Local builds only.** `flutter test` and `flutter analyze` run locally.

This matches the user's other two Flutter projects, neither of which has any CI
configured.

Consequence worth noting: the test decisions above — the rules-engine unit tests, the
board widget tests, and the hardcoded-theme-value test — run when they are run locally.
Nothing runs them on a push.

### Release tooling — fastlane
**fastlane.** The App Store listing is kept as local text files, edited and committed
like code, and pushed to App Store Connect from the CLI.

The question behind this was whether there is "a Terraform for the Apple App Store" — a
way to fill out App Store configuration locally and apply it to the live store. fastlane
is the thing that actually does this:

- **`deliver`** (aka `upload_to_app_store`) keeps the listing as local files:
  `fastlane/metadata/` for description, keywords, release notes and categories — one
  file per field per locale — and `fastlane/screenshots/` for the images. Edit
  locally, commit, run, and it pushes to App Store Connect.
- **`match`** stores signing certificates and provisioning profiles in a git repo and
  syncs them.
- **`produce`** creates the app record and registers the bundle identifier from the CLI.

It runs on Apple's official App Store Connect API underneath.

**Set up when actually approaching shipping — not now.** It is recorded here as the
intended approach so the choice does not have to be made again under release pressure.

Community Terraform providers for App Store Connect do exist —
[`fintreal/terraform-provider-appstore`](https://github.com/fintreal/terraform-provider-appstore),
[`alexprogrammr/terraform-provider-appstore`](https://github.com/alexprogrammr/terraform-provider-appstore)
and
[`TrueTickets/terraform-provider-appleappstoreconnect`](https://github.com/TrueTickets/terraform-provider-appleappstoreconnect)
— but each covers only a fragment of App Store Connect and all are unofficial
single-maintainer projects. That is why the answer is fastlane and not an actual
Terraform provider.

**Watch out for:** fastlane does not automate App Review, which stays manual — and an
Apple Developer Program membership is required before any of it works.

### Crash reporting — catch and build the report, don't send it
**Catch errors and construct the crash-report object from the start. Do not transmit it.**
As stated:

> *"I have nowhere to send the data. I think it would be good to set the game up to handle
> this putting in the catches now from the start to build out the crash report. We just
> won't send it out just yet. We will come up with where it will be sent to later. But for
> now just catch and build out the object. Just don't send it. yet"*

So the error handling and the report object are day-one work; the transport is not. The
destination is deliberately left for later rather than being an open question — today's
answer is "nowhere."

This keeps **Fully offline. No backend, no network, no accounts.** under **What the Design
Docs Already Imply** below true for now. It stops being true the day a destination is
chosen.

---

## What the Design Docs Already Imply
Some technical requirements are already locked by decisions made elsewhere. Listing them
here so they don't get re-litigated:

| Requirement | Comes from |
|---|---|
| **Fully offline.** No backend, no network, no accounts. | Two players, one phone |
| **Local persistence** for 4 values: theme, sound, vibrate, animations | [Menus and UI](./Menus%20and%20UI.md) → Persistence |
| **Game-state persistence.** A game in progress and its scoreboard are saved and can be resumed. | Same |
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

<!-- Both halves are now chosen: state management is Riverpod (Decisions → State
     management — Riverpod) and the renderer is widgets (Decisions → How is the board
     rendered?). The requirement stands; the choice is no longer open. -->

The countermeasure is now decided: a test that fails on hardcoded theme values — see
**Do we add a test that fails on hardcoded theme values?** under Decisions. That is what
turns this from a discipline into a check.

---

## Open Questions

These are the things I think we need to hammer out. Grouped roughly by how much they
block other work.

### 1. Persisted data — versioning
- When the shape of stored data changes — a fifth preference is added, a key is renamed,
  a saved game gains a field — what happens to data already on the device? A game written
  by v1.0 has to still load in v1.1.
- Not an answer, but it fixes the shape the answer takes: saved data is JSON, not Hive
  `TypeAdapter`s, so versioning means a `schemaVersion` field read and migrated on load
  rather than `typeId` bookkeeping. See Decisions → Serialization and the storage layer.

### 2. Theme loading
- Are all themes loaded and materialized at startup, or only the selected one, on demand?
  **How does fallback-to-Neon work?** above says materialization happens "at startup" but
  does not say for how many themes.
- Are the theme YAML files declared as assets in `pubspec.yaml`?
- What happens to an unknown or misspelled *key* inside an otherwise-valid theme file?
  Merge-over-Neon will quietly fill the gap with Neon's value, so a typo in a theme file
  fails silently. The hardcoded-theme-value test guards code that bypasses the theme; it
  does not guard a theme file that misspells a key.

### 3. Build and distribution
- App name?

<!-- Resolved: public App Store release; bundle identifier
     com.ehrendavis.tictactoeextreme; local builds only, no CI; fastlane as the release
     tooling. Only the app name — the display name under the icon — is still open.
     See Decisions → Distribution — public App Store release, Bundle identifier,
     CI — local builds only, and Release tooling — fastlane. -->
