# Tech Design

> **Status:** Brain dump / early tech decisions. Contradictions are expected and OK.
> Nothing here is settled except what's under **Decisions**.
>
> This doc covers *how we build it*. What we're building lives in
> [Game Overview](./Game%20Overview.md), [Rules](./Rules.md),
> [Game Board Design](./Game%20Board%20Design.md), [Menus and UI](./Menus%20and%20UI.md),
> [Theming](./Theming.md), and [Animations](./Animations.md).
>
> **Approved UI design:** `Docs/tic-tac-toe/design_handoff_game_ui/README.md` —
> [Design Handoff](./design_handoff_game_ui/README.md). Its *State* section sketches a
> per-game data shape and its *Assets* section names concrete font and icon dependencies.
> Reference asset — read-only.

## Decisions

### Framework — Flutter
**Flutter.** Already in use for the game.

### Primary target — Apple
**iOS is the primary target as of right now.** Android is supported by virtue of Flutter,
but Apple is what we're building and testing against first.

Practical meaning: when a platform question comes up, iOS wins. Android is a
build-target, not a design constraint.

### Language — Dart
**Dart.** Comes with Flutter.

### Theme representation — data, not code
**Themes are data — a JSON or YAML object loaded at runtime**, not a Dart class compiled
into the app. A universal, theme-like object that can be loaded in.

### What format are theme files — JSON or YAML?
**YAML.**

### Theme identity — UUID
**Each theme carries a UUID in its YAML file, and that UUID is the theme's identity.**
*"the themes should be saved by UUID in the YAML files."*

The persisted "selected theme" preference stores the UUID, not the theme's name. See
[Theming](./Theming.md) → Decisions → Does the theme persist between sessions.

### Fallback to Neon — merge, not resolve
**Merge over Neon.** Each theme is materialized into a complete theme by merging it over
Neon.

### Flutter's ThemeData vs our own theme object
**Use Flutter's `ThemeData`/`ThemeExtension` as far as possible**, filled out from our
theme JSON/YAML file. The remaining parts, not supported by the Flutter theme, we
implement ourselves.

Sounds and animations live in the **same theme object** — not a parallel structure. We
give Flutter's `ThemeData` what we can and handle the rest ourselves, all from the same
file.

### Orientation — portrait only
**Portrait only.** No landscape.

### Minimum iOS version
**iOS 13.**

### Is the game logic separate from Flutter?
**Yes.** The rules engine — board state, legal moves, sending rule, win/cat-game detection,
free-choice state — is **pure Dart with zero Flutter imports**, and the UI layer reads from
it.

### Persistence package
**`shared_preferences` — for the four player preferences.**

Game state does not go here. It is saved too, in Hive — see **Game state storage — Hive**
below.

### Game state storage — Hive
**Hive.** Open games — the board, whose turn it is, and the scoreboard — are stored in
Hive, not in `shared_preferences`.

This is what makes [Menus and UI](./Menus%20and%20UI.md) → Decisions → Does a game in
progress have to be saved to device storage? and [Game Overview](./Game%20Overview.md) →
Decisions → Scoreboard lifetime implementable.

### Serialization and the storage layer
**`freezed` + `json_serializable` for the domain models in `engine/`, and a `storage/`
layer holding a repository interface with a Hive implementation that stores JSON. No Hive
`TypeAdapter`s.**

Three consequences worth naming, because they cut across other Decisions:

- **`storage/` is a new layer** in **Project structure — layer-first** below.
- **`hive_flutter` is not pure Dart, so it must never be imported from `engine/`.**
  `storage/` owns it.
- **Serialization lives with the model.** `toJson`/`fromJson` are generated into `engine/`
  by json_serializable — pure Dart, Flutter-free — while the Hive box, adapters-free,
  lives in `storage/`.

This does not change **Game state storage — Hive** above; Hive is still the store. It
decides what gets written into it, and who is allowed to know it is Hive.

<!-- A candidate shape for the persisted Game object — cells, quadrants, activeQuadrant,
     currentPlayer, lastMove, score, firstPlayerThisGame — is sketched in Design Handoff →
     State (Docs/tic-tac-toe/design_handoff_game_ui/README.md). It is a design sketch, not
     a decision taken here. -->

### Unit tests for the rules engine
**Yes — this is where the real complexity is.**

### Do themes pick their own font?
**Yes.** A font is a themeable value like any other, and the theme object needs somewhere
to put one. See [Theming](./Theming.md) → Architectural Rule.

### How is the board rendered?
**Widgets.** *"ok widgets is the winner lets make that happen."*

81 `GestureDetector`s in nested `GridView`/`Column`s, not a `CustomPainter`.

**Watch out for:** nested `Border.all` doubles interior grid lines — two adjacent 1px
borders read as 2px — and hairlines can look uneven at fractional device pixel ratios.
The known fix is a hybrid: widgets for cells and marks, plus one thin `CustomPaint`
overlay drawing only the grid lines. That is an escape hatch, not a decision taken.

### Audio package
**`audioplayers`.**

### Marks — image or icon, supplied by the theme
**"Due to themes im thinking the marks can be an image or an icon. For example neon just
needs icons of X and O while the dinosaur theme might use a T-Rex as an Icon."**

So marks are asset slots on the theme, not shapes drawn in board code.

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

Worth confirming at first use: the user notes that the Replicate model
`sourceful/riverflow-2.0-pro` *"does allow for png transparent background images."* That
is recorded as the user's note, not verified against the current model card, and not a
model choice.

A **Replicate agent** may follow — *"we might need to build out a Replicate Agent that
has the skills to utilize Replicate for both audio and images when needed"* — but that
is hedged and explicitly not now, and it would live in the agent system rather than in
this doc.

<!-- Design Handoff → Assets names two third-party dependencies this decision does not
     cover: Inter 400/500/600 (bundled, not from a CDN) and the Phosphor icon set.
     Neither is Replicate-generated. See
     Docs/tic-tac-toe/design_handoff_game_ui/README.md. -->

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

Durations are in scope because [Animations](./Animations.md) → Decisions → Duration lives
in the animation puts timing inside the theme's animation definitions, so a hardcoded
`Duration` is a theme value that escaped.

This is the structural enforcement that **The theme system is the main architectural
risk** below asks for, and it is what makes [Theming](./Theming.md) → Architectural Rule a
checkable rule rather than a matter of discipline.

### State management — Riverpod
**Riverpod, without Riverpod's own codegen to start.** Plain `NotifierProvider`
declarations, no `@riverpod` annotations. Riverpod codegen can be adopted later without
rewriting the logic.

It also covers the requirement that settings and the theme be readable from
**everywhere**, including deep in the board widget tree.

**Watch out for:** fey-tactics uses `StateNotifier`, which is the legacy API. Use
`Notifier`/`NotifierProvider` — fey-tactics is a reference for the sync shape, not for
the API surface.

### Online multiplayer is an intended future direction
**Tech choices must not foreclose syncing board state over a network.** Not built now —
see **Fully offline. No backend, no network, no accounts.** under What the Design Docs
Already Imply below, which holds today.

### Game state is immutable
**Immutable.** The engine never mutates a board in place — every move produces a new state
object, and that new object is what the UI renders.

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

`storage/` is local persistence only — the repository interface and its Hive
implementation (see **Serialization and the storage layer** above). There is still **no
backend data layer**: nothing in the app talks to a server. One gets added if multiplayer
arrives.

`assets/themes/`, `assets/images/` and `assets/audio/` are the **designated folders for
assets** required by **Where do sound and art assets come from?** above.

### Widget tests for the board — no golden tests
**Widget tests, no goldens.** Test that taps do the right thing and that the highlight
states appear. Skip golden image tests.

This sits alongside **Unit tests for the rules engine** above, which covers the engine
layer, and **Do we add a test that fails on hardcoded theme values?** below.

### Fresh build, not a refactor
**A fresh build.** Nothing from the earlier Flutter work carries into this design — every
Decision in this doc describes something being built new, not refactored toward.

### Distribution — public App Store release
**The App Store.** A public release, not a personal or TestFlight-only build.

That makes the App Store Connect listing a real deliverable — description, keywords,
screenshots, categories — which is what **Release tooling — fastlane** below manages.

### Bundle identifier
**`com.ehrendavis.tictactoeextreme`.** Lowercase reverse-DNS, the conventional Apple form.

**Watch out for:** a bundle identifier is effectively permanent once the app has been
submitted to App Store Connect, so this is not a name to revisit casually.

### CI — local builds only
**No CI. Local builds only.** `flutter test` and `flutter analyze` run locally.

Consequence worth noting: the test decisions above — the rules-engine unit tests, the
board widget tests, and the hardcoded-theme-value test — run when they are run locally.
Nothing runs them on a push.

### Release tooling — fastlane
**fastlane.** The App Store listing is kept as local text files, edited and committed
like code, and pushed to App Store Connect from the CLI.

The three pieces:

- **`deliver`** (aka `upload_to_app_store`) keeps the listing as local files:
  `fastlane/metadata/` for description, keywords, release notes and categories — one
  file per field per locale — and `fastlane/screenshots/` for the images. Edit
  locally, commit, run, and it pushes to App Store Connect.
- **`match`** stores signing certificates and provisioning profiles in a git repo and
  syncs them.
- **`produce`** creates the app record and registers the bundle identifier from the CLI.

It runs on Apple's official App Store Connect API underneath.

**Set up when actually approaching shipping — not now.**

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
| **Game-state persistence.** Every open game is saved and resumable, each with its own scoreboard. | [Menus and UI](./Menus%20and%20UI.md) → Persistence, Decisions |
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
  an open game gains a field — what happens to data already on the device? A game
  written by v1.0 has to still load in v1.1.

### 2. Theme loading
- Are all themes loaded and materialized at startup, or only the selected one, on demand?
  [Theming](./Theming.md) → Why this matters for the build says materialization happens
  "at startup" but does not say for how many themes.
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
