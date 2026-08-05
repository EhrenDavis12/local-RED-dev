# PRD: App Scaffold

> **Status:** Draft · Source docs read: Tech Design.md, Game Overview.md, Menus and UI.md,
> Theming.md, Animations.md, Game Board Design.md, Rules.md, roadmap.md, and the read-only
> reference asset `design_handoff_game_ui/`. `Alternative Game Styles.md` is a declared
> parking-lot doc and was not sourced from.

> **Wave:** P1 · **Depends on:** nothing — this is the first thing built.
> Everything else in P1 (`P1-02-engine-rules.md`, `P1-03-theme-system.md`,
> `P1-04-persistence.md`, `P1-05-theme-guard-test.md`, `P1-06-crash-reporting.md`) lands
> inside the structure this PRD creates. Within a wave, work is parallel-safe; a lower wave
> ships first.

## Problem

There is no application. `src/Tic-Tac-Toe-Extreme/` holds a README and nothing else, so no
sibling PRD in wave P1 has anywhere to put a file, no `flutter analyze` or `flutter test`
can run, and none of the build-level decisions already taken — portrait lock, minimum iOS
version, bundle identifier, dependency set, layer-first structure — exist anywhere except
as prose. [Tech Design → Decisions → Fresh build, not a refactor] is explicit that nothing
from the earlier Flutter work carries over, so this is a greenfield create.

## Goal

A Flutter application exists at the src root with the layer-first `lib/` structure and
asset folders the design docs specify, its build-level configuration set as decided
(portrait only, iOS 13 minimum, bundle identifier `com.ehrendavis.tictactoeextreme`), the
decided dependency set declared, Riverpod wired in at the root of the widget tree, and
`flutter analyze` and `flutter test` both running clean locally. It is a skeleton: no
rules, no theme, no persistence, no screens — just the shape those land in, with the
layering constraints that keep `engine/` pure enforceable from day one.

## Requirements

1. **The app is a Flutter project written in Dart, created fresh at the src root**
   (`src/Tic-Tac-Toe-Extreme`). Nothing is carried over or refactored from earlier Flutter
   work. *[Tech Design → Decisions → Framework — Flutter; Language — Dart; Fresh build, not
   a refactor]* The existing `README.md` at that path is preserved (observed repo state).

2. **`lib/` follows the layer-first structure, grouped by kind, not by feature** — exactly
   the tree given in the doc: `main.dart`, `app.dart`, `engine/`, `storage/`, `theme/`,
   `state/`, `ui/board/`, `ui/menus/`. *[Tech Design → Decisions → Project structure —
   layer-first]* Each directory exists and is reachable at the end of this PRD; what goes
   *in* them belongs to the sibling PRDs listed under Out of Scope.

3. **`assets/themes/`, `assets/images/` and `assets/audio/` exist** and are the designated
   asset folders. *[Tech Design → Decisions → Project structure — layer-first, which names
   these as the "designated folders for assets" required by Where do sound and art assets
   come from?]*

4. **`engine/` has zero Flutter imports.** The layer is pure Dart. *[Tech Design →
   Decisions → Is the game logic separate from Flutter?]*

5. **`hive_flutter` is never imported from `engine/`; `storage/` owns it.** It is not pure
   Dart, so it cannot cross into the engine layer. *[Tech Design → Decisions →
   Serialization and the storage layer]*

6. **`storage/` is local persistence only. There is no backend data layer** — nothing in
   the app talks to a server, and the app is fully offline with no network and no accounts.
   *[Tech Design → Decisions → Project structure — layer-first; What the Design Docs
   Already Imply → "Fully offline. No backend, no network, no accounts."]*

7. **The app runs portrait only.** No landscape, at the Flutter level and in the iOS
   project configuration. *[Tech Design → Decisions → Orientation — portrait only]*

8. **Minimum iOS deployment target is iOS 13.** *[Tech Design → Decisions → Minimum iOS
   version]*

9. **The bundle identifier is `com.ehrendavis.tictactoeextreme`.** *[Tech Design →
   Decisions → Bundle identifier]* Note the doc's own warning: this is effectively
   permanent once the app has been submitted to App Store Connect.

10. **Riverpod is wired up as the state-management root** — a `ProviderScope` above the
    application widget, so providers resolve from anywhere in the tree. *[Tech Design →
    Decisions → State management — Riverpod, which requires that settings and the theme be
    readable from **everywhere**, including deep in the board widget tree]*

11. **Riverpod is used without its own codegen: plain `NotifierProvider` declarations, no
    `@riverpod` annotations, and no legacy `StateNotifier`.** Use `Notifier` /
    `NotifierProvider`. *[Tech Design → Decisions → State management — Riverpod, including
    its "Watch out for" on fey-tactics using the legacy API]*

12. **The dependency set declared in `pubspec.yaml` is:** Riverpod *[State management —
    Riverpod]*, `shared_preferences` *[Persistence package]*, Hive — including
    `hive_flutter` in the Flutter-facing layer *[Game state storage — Hive; Serialization
    and the storage layer]*, `freezed` and `json_serializable` *[Serialization and the
    storage layer]*, and `audioplayers` *[Audio package]*. All citations are Tech Design →
    Decisions. `freezed` and `json_serializable` are code generators, so their generator
    toolchain (`build_runner` and the matching `*_generator` packages) is declared as dev
    dependencies — that is what "generated into `engine/` by json_serializable" requires.

13. **`flutter analyze` and `flutter test` both run clean locally from the src root, and
    there is no CI.** Nothing runs on a push. *[Tech Design → Decisions → CI — local builds
    only]* Note for the implementer: `flutter test` fails when the suite is empty, so the
    scaffold ships the minimum needed for the command to succeed; the substance of the
    tests belongs to the sibling PRDs.

14. **Nothing in the scaffold forecloses syncing board state over a network later.**
    Not built now, but the structure must not rule it out. *[Tech Design → Decisions →
    Online multiplayer is an intended future direction]*

## Out of Scope

Referenced by filename rather than specified here:

- **The rules engine** — board state, legal moves, the sending rule, win/cat-game
  detection, free choice, immutability, and `Board applyMove(Board, Move)` →
  `P1-02-engine-rules.md`.
- **The theme object and YAML loading** — the merged theme, merge-over-Neon, `ThemeData` /
  `ThemeExtension` population, theme UUIDs → `P1-03-theme-system.md`.
- **The repository interface and its Hive implementation**, preference storage, and the
  persisted model shapes → `P1-04-persistence.md`.
- **The hardcoded-theme-value scan test** and its per-file baseline →
  `P1-05-theme-guard-test.md`.
- **Error catching and the crash-report object** → `P1-06-crash-reporting.md`. `main.dart`
  exists after this PRD but does not yet install error handlers.
- **Every screen** — main menu, open games list, name prompt, board, theme overlay,
  settings, game-over modals → waves P2/P3.
- **Release tooling.** fastlane, `deliver`/`match`/`produce`, and the App Store Connect
  listing are decided but explicitly deferred: *"Set up when actually approaching shipping
  — not now."* *[Tech Design → Decisions → Release tooling — fastlane]*
- **Asset generation.** The single Replicate API script, the logo, and sound assets are
  *"not now"* by decision. *[Tech Design → Decisions → Where do sound and art assets come
  from?]* This PRD creates the folders, not their contents.
- **Alternative Game Styles.md** — parking lot, not what is being built.

## Open Questions

### From the design docs — unresolved, worded as the docs word them

- **App name?** *[Tech Design → Open Questions → 3. Build and distribution]* Everything
  else in that group is resolved; the display name under the icon is not. The scaffold
  needs one to set, so this blocks a value in the iOS configuration.
- **Are the theme YAML files declared as assets in `pubspec.yaml`?** *[Tech Design → Open
  Questions → 2. Theme loading]* `pubspec.yaml` is this PRD's territory, so whichever way
  this lands, the declaration lives here even though the loading does not.

### Found while writing this PRD — not settled anywhere, and flagged rather than answered

These are gaps I noticed, not proposals with any authority behind them. Each is a place an
implementer would otherwise have to guess.

- **No YAML parsing package appears in any Decision**, though theme files are YAML *[Tech
  Design → Decisions → What format are theme files — JSON or YAML?]*. Which package, and
  whether it is declared in this PRD's `pubspec.yaml` or added by `P1-03-theme-system.md`,
  is undecided.
- **Which platform folders the project is created with.** iOS is primary and Android is
  *"supported by virtue of Flutter"*, iPad is second and *"all media devices"* is recorded
  but not scoped *[Tech Design → Decisions → Primary target — Apple; Device support]*.
  Whether the scaffold generates ios + android only, or every platform Flutter offers, is
  not stated.
- **Whether the iOS target device family includes iPad at scaffold time.** The ordering is
  decided (iPhone first, iPad second); the build setting is not.
- **Which lint ruleset `flutter analyze` runs against.** The docs require it to run clean
  locally but never say whether that is the default `flutter_lints` set or something
  stricter.
- **Whether the engine-purity constraints (Requirements 4 and 5) get an automated check.**
  The only scan-style test decided anywhere is the hardcoded-theme-value one
  (`P1-05-theme-guard-test.md`), which covers theme values, not imports. As written today
  these two constraints are discipline, not a check — the same failure mode *[Theming →
  Architectural Rule]* was hardened against for theme values.
- **Whether the scaffold bundles Inter 400/500/600 and the Phosphor icon set.** The
  approved handoff names both as concrete dependencies *[design_handoff_game_ui/README.md →
  Assets]*, and Tech Design's own comment notes no Decision covers them. It also interacts
  with *[Tech Design → Decisions → Do themes pick their own font?]*, where a font is a
  themeable value — which would put font bundling in tension with putting a font in the
  scaffold.
