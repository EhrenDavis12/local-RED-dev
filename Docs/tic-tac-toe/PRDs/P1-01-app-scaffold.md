# PRD: App Scaffold

> **Status:** Draft · Source docs read: Tech Design.md, Game Overview.md, Menus and UI.md,
> Theming.md, Animations.md, Game Board Design.md, Rules.md, roadmap.md, and the read-only
> reference asset `design_handoff_game_ui/`. `Alternative Game Styles.md` is a declared
> parking-lot doc and was not sourced from.

> **Wave:** P1 · **Depends on:** nothing — this is the first thing built.
> Everything else in P1 (`P1-02-engine-rules.md`, `P1-03-theme-system.md`,
> `P1-04-persistence.md`, `P1-05-theme-guard-test.md`, `P1-06-crash-reporting.md`,
> `P1-07-entitlements.md`) lands inside the structure this PRD creates, so **this PRD ships
> before the rest of its own wave** — see the exceptions below the table.

## Build order — the wave scheme

Recorded here because this is the first PRD anyone reads, so the ordering is discoverable
without opening all 24 files. **A lower wave ships first. Within a wave, work is
parallel-safe. No PRD may declare a dependency on a higher wave.**

| Wave | Theme | PRDs |
|---|---|---|
| **P1** | Foundations — nothing above exists yet | `P1-01-app-scaffold`, `P1-02-engine-rules`, `P1-03-theme-system`, `P1-04-persistence`, `P1-05-theme-guard-test`, `P1-06-crash-reporting`, `P1-07-entitlements` |
| **P2** | Cross-cutting channels the screens fire into | `P2-01-navigation`, `P2-02-audio`, `P2-03-haptics`, `P2-04-animations` |
| **P3** | The game screen | `P3-01-board-rendering`, `P3-02-move-input`, `P3-03-scoreboard-turn-indicator`, `P3-04-game-over-rematch`, `P3-05-how-to-play` |
| **P4** | Menus and store surfaces | `P4-01-main-menu`, `P4-02-open-games-list`, `P4-03-theme-selection`, `P4-04-settings`, `P4-05-purchase-flow` |
| **P5** | Content and ship | `P5-01-classic-theme`, `P5-02-asset-generation-replicate`, `P5-03-release-fastlane` |

The channels in P2 ship before the screens in P3 because the screens *call* them: the board
fires a haptic and a sound, and the animation layer runs over state the board already
renders. The entitlement model sits in P1 rather than beside the purchase flow because
`P1-04-persistence.md`, `P4-02-open-games-list.md` and `P4-03-theme-selection.md` all read
what the player owns, while only `P4-05-purchase-flow.md` needs StoreKit.

### Known exceptions to "within a wave, work is parallel-safe"

The rule above is the default, not a guarantee. Three exceptions exist today, recorded here
because a reader scheduling a wave off the table alone would hit all three:

1. **P1-01 is not parallel with its own wave.** This PRD creates the Flutter project,
   `pubspec.yaml` and the `lib/` tree that every other P1 PRD writes into. Dispatch it
   **first**, then the rest of P1 in parallel. Note the declarations in those PRDs are
   inconsistent on this point and should not be scheduled from directly:
   `P1-05-theme-guard-test.md` and `P1-06-crash-reporting.md` name this PRD explicitly,
   while `P1-02-engine-rules.md` and `P1-03-theme-system.md` declare "**Depends on:**
   nothing" and `P1-04-persistence.md` omits it from its dependency list. Being pure Dart
   does not remove the need for a project to exist to hold the file.
2. **`P1-04-persistence.md` and `P1-07-entitlements.md` depend on each other.** `P1-04`
   lists `P1-07` as a dependency ("owns the entitlement model … build against that
   interface"), and `P1-07` lists `P1-04` as a dependency ("where entitlement state is
   written down") *and* as a dependent. Both nonetheless describe themselves as
   parallel-safe with the rest of P1. This is the same circularity the entitlements/purchase
   split was performed to break — see `P4-05-purchase-flow.md`'s split note — surviving
   inside wave 1 rather than across the P1/P4 boundary it was cut at. Flagged, not resolved:
   which of the two moves, or whether the cut is drawn again, is not this PRD's call.
3. **`P4-05-purchase-flow.md` flags its own wave-4 parallelism as conditional** — "**subject
   to the host-surface question below**", because where the open-game unlock is sold is
   unresolved and could put it behind another P4 screen.

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

2. **`lib/` follows the layer-first structure, grouped by kind, not by feature** — the tree
   given in the doc: `main.dart`, `app.dart`, `engine/`, `storage/`, `theme/`, `state/`,
   `navigation/`, `ui/board/`, `ui/menus/`. *[Tech Design → Decisions → Project structure —
   layer-first, as amended to add `navigation/`: "a new layer, for the same reason
   `storage/` was added … It is Flutter-side, same as `ui/` and `state/` — nothing here
   changes the `engine/` purity rule"]* Each directory exists and is reachable at the end of
   this PRD; what goes *in* them belongs to the sibling PRDs listed under Out of Scope.
   `navigation/` is created empty here — its contents are `P2-01-navigation.md`'s, and the
   routing approach is still open *[Tech Design → Open Questions → 4. Navigation approach]*.

   **This tree is the design doc's, and it is not a closed set on this PRD's authority.**
   `navigation/` got a home by amending the doc; error handling has not, and
   `P1-06-crash-reporting.md` Open Question 6 asks where that code lives, noting the doc
   "names no home for error handling." Read as a closed list, this requirement would leave a
   same-wave sibling homeless. This PRD does **not** invent a directory to fix that — see
   Open Questions.

3. **`assets/themes/`, `assets/images/` and `assets/audio/` exist** and are the designated
   asset folders. *[Tech Design → Decisions → Project structure — layer-first, which names
   these as the "designated folders for assets" required by Where do sound and art assets
   come from?]*

4. **`engine/` has zero Flutter imports.** The layer is pure Dart. *[Tech Design →
   Decisions → Is the game logic separate from Flutter?]*

5. **`hive_flutter` is never imported from `engine/`; `storage/` owns it.** It is not pure
   Dart, so it cannot cross into the engine layer. *[Tech Design → Decisions →
   Serialization and the storage layer]*

6. **`storage/` is local persistence only, and no backend of ours — and no account system
   we operate — is introduced.** Nothing in the app talks to a server of ours: no HTTP
   client, no login, no user record. The app is **fully offline, except for in-app
   purchases**: StoreKit is the one permitted exception, needing network access and a
   restore-purchases path tied to the Apple ID, and it arrives in
   `P4-05-purchase-flow.md`, not here. *[Tech Design → Decisions → Project structure —
   layer-first: "`storage/` is local persistence only … There is still **no backend data
   layer**: nothing in the app talks to a server"; → Decisions → In-app purchases; → What
   the Design Docs Already Imply → "**Fully offline, except for in-app purchases.** No
   backend, no network, no accounts — StoreKit is the one exception, needing network access
   and a restore-purchases path tied to the Apple ID."]*
   *Testable:* an outbound-call scan over `lib/` finds no HTTP client and no network target
   other than the store SDK. That is deliberately the same form as
   `P4-05-purchase-flow.md` Requirement 7, so a check written in this wave still passes
   when the store layer lands in P4. The stricter form — "no networking API is reachable
   from `lib/`" — must **not** be built: it would fail the day `P4-05` ships, and that PRD
   has no way to know this check exists.

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
    and the storage layer]*, `freezed` and `json_serializable` together with their runtime
    annotation packages **`freezed_annotation` and `json_annotation`** *[Serialization and
    the storage layer]*, and `audioplayers` *[Audio package]*. All citations are Tech Design
    → Decisions.

    **Code generation, named correctly:** `build_runner` is the dev dependency that runs the
    generators, and the generators are `freezed` and `json_serializable` *themselves* —
    there is no `freezed_generator` package and no `json_serializable_generator` package on
    pub. `freezed_annotation` and `json_annotation` are ordinary runtime dependencies, not
    dev dependencies: the generated `toJson`/`fromJson` and union code imports them, so
    omitting them means the generated code does not compile. That is what "generated into
    `engine/` by json_serializable" requires in practice, and both annotation packages are
    pure Dart, so they do not breach Requirement 4.

13. **`flutter analyze` and `flutter test` both run clean locally from the src root, and
    there is no CI.** Nothing runs on a push. *[Tech Design → Decisions → CI — local builds
    only]* Note for the implementer: `flutter test` fails when the suite is empty, so the
    scaffold ships the minimum needed for the command to succeed; the substance of the
    tests belongs to the sibling PRDs.

14. **Nothing in the scaffold forecloses syncing board state over a network.**
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
- **The entitlement model** — what the player owns, its local cache, the free-tier
  defaults, and the query interface siblings read → `P1-07-entitlements.md`. Same wave as
  this PRD, and parallel-safe with it.
- **The routing layer's contents** — what routes exist, how they are declared, and the
  router package → `P2-01-navigation.md`. This PRD creates the empty `navigation/`
  directory and nothing inside it.
- **Every screen** — main menu, open games list, name prompt, board, theme overlay,
  settings, game-over modals → waves P3/P4.
- **In-app purchases** — StoreKit, the purchase flow, restore-purchases, purchase outcomes
  and the store-side product concerns → `P4-05-purchase-flow.md`. This PRD only keeps
  Requirement 6 from blocking it.
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

- **Where does error-handling code live in the layer-first tree?** Requirement 2 builds the
  doc's tree, and that tree has no home for it — the same gap `P1-06-crash-reporting.md`
  Open Question 6 raises from the other side, quoting the doc as naming "no home for error
  handling." `navigation/` was given a home by amending Tech Design → Decisions → Project
  structure — layer-first; error handling has not been, and a same-wave PRD needs one. This
  PRD does not invent a directory, and `P1-06` should not have to either.
- **Which Riverpod package is declared** — `flutter_riverpod`, `riverpod`, or
  `hooks_riverpod`. Requirements 10 and 11 imply `flutter_riverpod` (a `ProviderScope`
  widget and `Notifier`/`NotifierProvider` with no hooks), but *[Tech Design → Decisions →
  State management — Riverpod]* names the family, not the package, and the three are not
  interchangeable in `pubspec.yaml`.
- **Whether "Hive" means `hive` or the maintained `hive_ce` fork.** *[Tech Design →
  Decisions → Game state storage — Hive; Serialization and the storage layer]* names Hive
  and `hive_flutter` and stops there. This is a live choice at the keyboard rather than a
  detail, and `P1-04-persistence.md` builds on whichever is declared here.
- **No YAML parsing package appears in any Decision**, though theme files are YAML *[Tech
  Design → Decisions → What format are theme files — JSON or YAML?]*. Which package, and
  whether it is declared in this PRD's `pubspec.yaml` or added by `P1-03-theme-system.md`,
  is undecided.
- **No router package appears in any Decision**, though `navigation/` is now a required
  layer *[Tech Design → Decisions → Navigation; → Open Questions → 4. Navigation approach:
  "the dependency list has no router in it yet"]*. Whether the router is declared here or by
  `P2-01-navigation.md` is unsettled, same shape as the YAML question above.
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
