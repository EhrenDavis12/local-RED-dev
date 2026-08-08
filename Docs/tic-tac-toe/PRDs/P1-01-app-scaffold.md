**Build-readiness: 88**

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

## Pending confirmation — two literals, not two designs

Both are needed before `flutter create` can run. Each carries a proposal so the PRD is
executable the moment it is confirmed; neither changes anything else in this document.

1. **The Dart package name.** `Tic-Tac-Toe-Extreme` is the *repository* name and is not a
   legal Dart package identifier (hyphens and capitals are not permitted), so Requirement 1
   cannot run as the directory is named. **Proposed: `tic_tac_toe_extreme`** — the
   lower_snake_case form of the app name *[Tech Design → Decisions → App name]*, matching the
   bundle identifier's final segment. This cannot be deferred: every `package:` URI in the
   codebase and every import in twenty-three downstream PRDs embeds it, and changing it later
   is a whole-codebase rewrite.
2. **`hive` or `hive_ce`.** *[Tech Design → Decisions → Game state storage — Hive]* names
   "Hive" and `hive_flutter` and stops there, but the two options are different packages with
   different names, different Flutter pairings (`hive_flutter` vs `hive_ce_flutter`) and
   different imports. **Proposed: `hive_ce` + `hive_ce_flutter`**, on the reasoning that
   `hive_ce` is the actively maintained community fork while `hive` has been dormant, and
   that the decision to store JSON with **no `TypeAdapter`s** *[Tech Design → Decisions →
   Serialization and the storage layer]* means the app uses only the box API the two share —
   so the fork costs nothing and the maintenance risk sits with the other option. The
   fallback is `hive` + `hive_flutter` exactly as the doc words it. `P1-04-persistence.md`
   builds directly on whichever lands, so confirm before that PRD starts.

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
sibling PRD in wave P1 has anywhere to put a file, no `flutter analyze` or `flutter test` can
run, and none of the build-level decisions already taken — portrait lock, minimum iOS
version, bundle identifier, app name, dependency set, layer-first structure — exist anywhere
except as prose. [Tech Design → Decisions → Fresh build, not a refactor] is explicit that
nothing from the earlier Flutter work carries over, so this is a greenfield create.

## Goal

A Flutter application exists at the src root with the layer-first `lib/` structure and asset
folders the design docs specify, its build-level configuration set as decided (portrait only,
iOS 13 minimum, bundle identifier `com.ehrendavis.tictactoeextreme`, display name "Tic Tac
Toe Extreme"), the decided dependency set declared with reproducible version constraints,
`ProviderScope` wired in above the root widget, `go_router` installed with a placeholder
route that `P2-01-navigation.md` replaces, the generated counter demo deleted, and `flutter
analyze` and `flutter test` both running clean locally. It is a skeleton: no rules, no theme,
no persistence, no screens — just the shape those land in, with the layering constraints that
keep `engine/` pure enforced by a test rather than by discipline.

## Requirements

Each requirement carries a *Source* and a *Verification*. A requirement whose verification
cannot be run as written is a defect — report it rather than guessing.

1. **The app is a Flutter project written in Dart, created fresh at the src root**
   (`src/Tic-Tac-Toe-Extreme`), with package name `tic_tac_toe_extreme` (**pending
   confirmation** — see above). Nothing is carried over or refactored from earlier Flutter
   work, and the existing `README.md` at that path is preserved.
   *Source: Tech Design → Decisions → Framework — Flutter; Language — Dart; Fresh build, not
   a refactor. The README is observed repo state.*
   *Verification:* `pubspec.yaml` exists with `name: tic_tac_toe_extreme`; `flutter pub get`
   succeeds; `README.md` is unmodified in the diff.

2. **`lib/` follows the layer-first structure, grouped by kind, not by feature** — the
   **fourteen** paths the doc's tree now names:

   | Path | Filled by |
   |---|---|
   | `main.dart` | this PRD (Requirement 11) |
   | `app.dart` | this PRD (Requirement 11) |
   | `engine/` | `P1-02-engine-rules.md` |
   | `storage/` | `P1-04-persistence.md` |
   | `theme/` | `P1-03-theme-system.md` |
   | `state/` | Riverpod providers, per the PRD that owns each |
   | `navigation/` | this PRD's placeholder router, then `P2-01-navigation.md` |
   | `audio/` | `P2-02-audio.md` |
   | `haptics/` | `P2-03-haptics.md` |
   | `entitlements/` | `P1-07-entitlements.md` |
   | `diagnostics/` | `P1-06-crash-reporting.md` |
   | `purchase/` | `P4-05-purchase-flow.md` |
   | `ui/board/` | `P3-01-board-rendering.md` and the other P3 PRDs |
   | `ui/menus/` | the P4 screen PRDs |

   This PRD **creates all fourteen and fills only `main.dart`, `app.dart` and
   `navigation/`**. Directories that would otherwise be empty carry a `.gitkeep`, because git
   does not track empty directories and an untracked directory does not survive a clone. File
   names inside each layer belong to the owning PRD, not to this one.
   *Source: Tech Design → Decisions → Project structure — layer-first, whose tree now carries
   `audio/`, `haptics/`, `entitlements/`, `diagnostics/` and `purchase/` alongside the
   original layers: "five more new layers, each proposed by the PRD that needs it and
   following the same one-folder-per-layer convention as `storage/` and `navigation/` above.
   This closes the same gap in five PRDs at once … File names inside each are that PRD's to
   decide, not this doc's." The `.gitkeep` mechanism is this PRD's call — the docs do not
   address it.*
   *Verification:* after a fresh clone of the committed branch, all **fourteen** paths exist.
   No other directory is created under `lib/`.

   **The tree is the design doc's, and this PRD tracks it rather than owning it.** Every
   layer here arrived by amending Tech Design → Decisions → Project structure — layer-first,
   including the five added after this PRD was first written. A PRD that needs a layer this
   tree lacks should amend that Decision — which is how `diagnostics/` reached
   `P1-06-crash-reporting.md`, closing both its Open Question 6 and the matching open
   question this PRD used to carry.

3. **`assets/themes/`, `assets/images/` and `assets/audio/` exist, and this PRD declares no
   asset paths in `pubspec.yaml`.** Each folder carries a `.gitkeep`. The asset declaration
   for a folder is added by the PRD that lands the first real file in it — themes by
   `P1-03-theme-system.md`, images and audio by `P5-02-asset-generation-replicate.md`.
   *Source: Tech Design → Decisions → Project structure — layer-first, which names these as
   the "designated folders for assets" required by Where do sound and art assets come from?*
   *Rationale (this PRD's, not the docs'):* Flutter fails the build when `pubspec.yaml`
   declares an asset directory containing no files, so declaring them now would make
   Requirement 15 unachievable. `P5-02-asset-generation-replicate.md` structured its
   two-stage deliverable around that finding, so this assignment is load-bearing rather than
   bookkeeping — see its req 9, and `P2-02-audio.md` req 18, which both place the
   `assets/audio/` declaration with `P5-02` rather than with the audio layer.
   *Boundary:* this does **not** answer Tech Design → Open Questions → 2, "are the theme YAML
   files declared as assets in `pubspec.yaml`?" — that stays open and is `P1-03`'s to
   resolve. This requirement fixes only the mechanical rule that no declaration may name a
   directory with no files in it.
   *Verification:* the three directories exist after a fresh clone; `pubspec.yaml` has no
   `assets:` entries; `flutter build ios --no-codesign` succeeds.

4. **`engine/` has zero Flutter imports.** The layer is pure Dart.
   *Source: Tech Design → Decisions → Is the game logic separate from Flutter?*
   *Verification:* a test scans every `.dart` file under `lib/engine/` and fails on any
   import beginning `package:flutter/`, `dart:ui`, `package:flutter_riverpod/` or
   `package:go_router/`. This scan is written by this PRD — the constraint is decided, the
   check was previously nobody's, and "discipline" is not a deliverable.

5. **`hive_flutter` (or `hive_ce_flutter`) is never imported from `engine/`; `storage/` owns
   it.** It is not pure Dart, so it cannot cross into the engine layer.
   *Source: Tech Design → Decisions → Serialization and the storage layer — "`hive_flutter`
   is not pure Dart, so it must never be imported from `engine/`."*
   *Verification:* the same scan as Requirement 4, extended to fail on any `hive_flutter` /
   `hive_ce_flutter` import under `lib/engine/`. One test file covers both requirements.

6. **`storage/` is local persistence only, and no backend of ours — and no account system we
   operate — is introduced.** Nothing in the app talks to a server of ours: no HTTP client,
   no login, no user record. The app is **fully offline, except for in-app purchases**:
   StoreKit is the one permitted exception, needing network access and a restore-purchases
   path tied to the Apple ID, and it arrives in `P4-05-purchase-flow.md`, not here.
   *Source: Tech Design → Decisions → Project structure — layer-first: "`storage/` is local
   persistence only … There is still **no backend data layer**: nothing in the app talks to a
   server"; → Decisions → In-app purchases; → What the Design Docs Already Imply → "**Fully
   offline, except for in-app purchases.** No backend, no network, no accounts — StoreKit is
   the one exception … The exception is a StoreKit query against Apple, not a service we
   run."*
   *Verification:* an outbound-call scan over `lib/` finds no HTTP client and no network
   target other than the store SDK. That is deliberately the same form as
   `P4-05-purchase-flow.md` Requirement 7, so a check written in this wave still passes when
   the store layer lands in P4. The stricter form — "no networking API is reachable from
   `lib/`" — must **not** be built: it would fail the day `P4-05` ships, and that PRD has no
   way to know this check exists.
   *Scope note:* the scan covers `lib/` only, so build-time tooling is outside it by
   construction — `P5-02-asset-generation-replicate.md`'s Replicate script lives in `tool/`,
   uses `dart:io`'s `HttpClient`, and resolves every path against its `--root` flag
   (defaulting to the package root) rather than the CWD, so neither its network use nor its
   writes reach the shipped app.

7. **The app runs portrait only.** No landscape, at both the Flutter level and the iOS
   project level.
   *Source: Tech Design → Decisions → Orientation — portrait only.*
   *Verification:* `main.dart` calls `SystemChrome.setPreferredOrientations` with the two
   portrait values only; `ios/Runner/Info.plist` → `UISupportedInterfaceOrientations` lists
   `UIInterfaceOrientationPortrait` and no landscape value; rotating the simulator does not
   re-lay-out the app.

8. **Minimum iOS deployment target is iOS 13.**
   *Source: Tech Design → Decisions → Minimum iOS version.*
   *Verification:* `ios/Podfile` declares `platform :ios, '13.0'` and the Xcode project's
   `IPHONEOS_DEPLOYMENT_TARGET` is `13.0` for every configuration; `flutter build ios
   --no-codesign` succeeds.

9. **The bundle identifier is `com.ehrendavis.tictactoeextreme`**, set for every build
   configuration.
   *Source: Tech Design → Decisions → Bundle identifier.*
   *Verification:* `PRODUCT_BUNDLE_IDENTIFIER` equals that string in Debug, Release and
   Profile. Note the doc's warning: effectively permanent once submitted to App Store
   Connect.

10. **The app's display name is "Tic Tac Toe Extreme."**
    *Source: Tech Design → Decisions → App name — "**Tic Tac Toe Extreme.**" 20 characters,
    inside Apple's 30-character App Store limit.*
    *Verification:* `ios/Runner/Info.plist` → `CFBundleDisplayName` is exactly
    `Tic Tac Toe Extreme`; the caption under the icon on a simulator home screen reads the
    same.

11. **`main.dart` and `app.dart` have a defined shape, `ProviderScope` is the outermost
    app-level widget, and the app is routed by `go_router` from the first build.** The split
    is:
    - **`main.dart`** — entry point only: ensure the Flutter binding is initialized, apply
      the orientation lock (Requirement 7), and call `runApp` exactly once, from one place.
      No UI and no business logic.
    - **`app.dart`** — the root widget `TicTacToeExtremeApp`, returning
      **`MaterialApp.router`** with a `routerConfig:`. Not `MaterialApp` with `home:` — the
      routed form is the shape `go_router` requires, and building it now means
      `P2-01-navigation.md` replaces a value rather than restructuring the widget.
    - **`lib/navigation/`** — holds the placeholder `GoRouter`: a single route at `/`
      rendering the placeholder surface of Requirement 13. It lives here rather than in
      `app.dart` because `P2-01-navigation.md` Requirement 1's own test asserts that no route
      construction appears outside `lib/navigation/` — a router defined in `app.dart` would
      fail that scan the day it lands.
    - **`ProviderScope` wraps the root widget**, above `MaterialApp.router`:
      `runApp(const ProviderScope(child: TicTacToeExtremeApp()))`. Every provider therefore
      resolves from anywhere in the tree, including deep in the board.

    **Named extension points, so siblings have something to build against:**
    `P1-03-theme-system.md` supplies the `theme:` argument, absent here.
    `P2-01-navigation.md` replaces the placeholder `GoRouter` with the real route table and
    owns everything about it — route naming, nesting, shells, redirects, transitions.
    `P1-06-crash-reporting.md` may wrap the single `runApp` call site; its handlers and any
    guarded zone therefore sit **outside** `ProviderScope`, so failures during scope
    construction are still caught. Which mechanism it uses, and which file under
    `lib/diagnostics/` holds it, is that PRD's call; this requirement guarantees only that
    there is one wrappable call site.
    *Source: Tech Design → Decisions → Navigation approach — go_router; → State management —
    Riverpod ("settings and the theme be readable from **everywhere**, including deep in the
    board widget tree"); → Project structure — layer-first, whose tree names `main.dart` and
    `app.dart` as distinct files; → Flutter's ThemeData vs our own theme object, which puts
    the app on `ThemeData` and so on the `MaterialApp` family.*
    *Verification:* a widget test pumps `TicTacToeExtremeApp` and asserts a `ProviderScope`
    ancestor exists above the `MaterialApp`; `lib/main.dart` contains exactly one `runApp`
    call; `app.dart` uses `MaterialApp.router`; no `GoRouter` is constructed outside
    `lib/navigation/`.

    **`ProviderScope`'s placement is unchanged by the routing decision, and the decision
    reinforces it.** If `P2-01` exposes the router as a Riverpod provider — the usual shape,
    so redirects can read app state — then `app.dart` must read that provider, which requires
    `ProviderScope` to sit *above* `app.dart`, exactly where it already is. `P1-06`'s zone
    stays outside both. One constraint for `P2-01` to carry: a `GoRouter` must be a single
    long-lived instance rather than rebuilt on every widget build, so whatever holds it has
    to outlive rebuilds.

12. **Riverpod is used without its own codegen: plain `NotifierProvider` declarations, no
    `@riverpod` annotations, and no legacy `StateNotifier`.**
    *Source: Tech Design → Decisions → State management — Riverpod, including its "Watch out
    for" on fey-tactics using the legacy API.*
    *Verification:* `pubspec.yaml` contains no `riverpod_generator` or `riverpod_annotation`
    entry; a source scan over `lib/` finds no `@riverpod` annotation and no `StateNotifier`
    reference.

13. **The generated counter demo is deleted, and what replaces it renders nothing themeable.**
    `flutter create` scaffolds a counter app and a `test/widget_test.dart` that drives it.
    Both are removed. What ships instead is `main.dart`, `app.dart` and the placeholder route
    per Requirement 11, whose placeholder surface contains **no** color, icon, font-size,
    duration or asset-path literal, plus one smoke test that pumps the app and asserts it
    builds. After this PRD the app launches to an empty placeholder surface — deliberately
    not a screen. The first real screen is `P4-01-main-menu.md`, reached through
    `P2-01-navigation.md`.
    *Source: derived, and the derivation matters — `P1-05-theme-guard-test.md` Requirement 8
    requires the committed baseline to ship with **zero** recorded violations, and its
    Requirement 3 exempts only `lib/theme/`. The generated demo contains `Colors.deepPurple`,
    `Icons.add`, a literal `fontSize` and hardcoded strings — a full slate of what that guard
    scans for. Leaving it in place would either fail `P1-05` or force a non-empty baseline,
    contradicting Tech Design → Decisions → Do we add a test that fails on hardcoded theme
    values? ("the baseline starts at zero").*
    *Verification:* a scan of `lib/` finds no `Colors.`, no `Icons.`, no `fontSize:`, no
    `Color(0x` and no `Duration(`; the generated `test/widget_test.dart` is gone; `flutter
    test` passes; `P1-05`'s guard passes with an empty baseline when it lands.

14. **The dependency set declared in `pubspec.yaml` is exhaustive as of this wave**, and any
    later addition amends this requirement rather than being added silently:

    | Package | Kind | Source |
    |---|---|---|
    | `flutter_riverpod` | runtime | Tech Design → State management — Riverpod |
    | `go_router` | runtime | Tech Design → Navigation approach — go_router |
    | `shared_preferences` | runtime | Tech Design → Persistence package |
    | `hive_ce` + `hive_ce_flutter` *(pending — see top)* | runtime | Tech Design → Game state storage — Hive |
    | `freezed_annotation` | runtime | Tech Design → Serialization and the storage layer |
    | `json_annotation` | runtime | Tech Design → Serialization and the storage layer |
    | `audioplayers` | runtime | Tech Design → Audio package |
    | `build_runner` | dev | Tech Design → Serialization and the storage layer |
    | `freezed` | dev | Tech Design → Serialization and the storage layer |
    | `json_serializable` | dev | Tech Design → Serialization and the storage layer |
    | `flutter_lints` | dev | Tech Design → CI — local builds only (Requirement 15) |

    **Amendments accepted after this wave** — recorded here so this table stays the single
    index, while each remains the amending PRD's to declare and own:

    | Package | Kind | Declared by | For |
    |---|---|---|---|
    | `yaml` | runtime | `P1-03-theme-system.md` req 36 | parsing theme YAML |
    | `image` | dev | `P5-02-asset-generation-replicate.md` req 8 | downscaling the logo to its `2.0x`/`3.0x` variants |

    `P5-02` reports its amendment as **a set of exactly one**: `yaml` was already declared by
    `P1-03`, and it uses `dart:io`'s `HttpClient` for the Replicate calls specifically to
    avoid adding `package:http`. Both additions are consistent with Requirement 6 — `image`
    is a pure-Dart dev dependency that never ships in the app, and the script lives in
    `tool/`, outside the `lib/` scope of that requirement's scan.
    **`go_router` is declared here and consumed by `P2-01-navigation.md`** — the same pattern
    as `audioplayers` (declared here, used by `P2-02-audio.md`) and `shared_preferences`
    (used by `P1-04-persistence.md`).
    **Which Riverpod package:** `flutter_riverpod`, because Requirement 11 needs the
    `ProviderScope` widget and Requirement 12 rules out both codegen (`riverpod_annotation`)
    and hooks (`hooks_riverpod`). The Decision names the family rather than the package, so
    this is stated rather than cited — flag it if it is wrong, but it does not block.
    **Naming, stated because it is easy to get wrong:** the generators are `freezed` and
    `json_serializable` themselves — there is no `freezed_generator` and no
    `json_serializable_generator` package. `freezed_annotation` and `json_annotation` are
    **runtime** dependencies, not dev: the generated `toJson`/`fromJson` and union code
    imports them, so omitting them means the generated code does not compile. Both are pure
    Dart, so neither breaches Requirement 4.
    **Still unnamed:** the store SDK, added by `P4-05-purchase-flow.md`; and an icon package,
    if the bundled icon set ships as one — see Open Questions, which is now the last unnamed
    package and has a sibling waiting on it.
    **Version constraints:** every entry uses a caret range (`^x.y.z`) pinned to the version
    resolved at scaffold time, and `pubspec.lock` **is committed**, per Dart's guidance for
    application packages — without it, twenty-three downstream PRDs build against whatever
    resolved that day.
    *Verification:* `flutter pub get` resolves with no version conflict; `pubspec.lock` is
    tracked in git; `dart run build_runner build` exits zero against an empty model set.

15. **`flutter analyze` and `flutter test` both run clean locally from the src root, and there
    is no CI.** The analyzer runs against the default `flutter_lints` rule set as the floor;
    anything stricter is deferred rather than chosen here. Nothing runs on a push.
    *Source: Tech Design → Decisions → CI — local builds only ("`flutter test` and `flutter
    analyze` run locally", "Nothing runs them on a push").*
    *Verification:* `flutter analyze` reports zero issues and `flutter test` exits zero, both
    from `src/Tic-Tac-Toe-Extreme`; `analysis_options.yaml` includes
    `package:flutter_lints/flutter.yaml`; no workflow file is added anywhere.

16. **The project is created for iOS and Android only** — `flutter create --platforms
    ios,android`. No web, macOS, Windows or Linux folders.
    *Source: Tech Design → Decisions → Primary target — Apple ("iOS is the primary target …
    Android is supported by virtue of Flutter, but Apple is what we're building and testing
    against first"); → Device support ("iPhone first, iPad second, Android far future"),
    where "all media devices" is recorded as stated and explicitly "not yet scoped to
    particular platforms."*
    *Verification:* `ios/` and `android/` exist; `web/`, `macos/`, `windows/` and `linux/` do
    not. Cheap to revisit — `flutter create --platforms <p> .` is re-runnable in place and
    adds a platform folder without disturbing `lib/`.

### Design notes — constraints on how the above is built, not separately assertable

- **Nothing in the scaffold forecloses syncing board state over a network.** *[Tech Design →
  Decisions → Online multiplayer is an intended future direction]* This was previously a
  numbered requirement; it has no assertable form — no test distinguishes a structure that
  permits a future sync layer from one that does not — so it is recorded as a constraint on
  judgment rather than a deliverable. Practically it means Requirement 6 describes what the
  app *does today*, not a structural ban on ever adding a data layer.

## Out of Scope

Referenced by filename rather than specified here. Each named PRD fills the directory
Requirement 2 creates for it:

- **The rules engine** (`lib/engine/`) — board state, legal moves, the sending rule,
  win/cat-game detection, free choice, immutability, and `Board applyMove(Board, Move)` →
  `P1-02-engine-rules.md`.
- **The theme object and YAML loading** (`lib/theme/`) — the merged theme, merge-over-Neon,
  `ThemeData` / `ThemeExtension` population, theme UUIDs, and the `theme:` argument this PRD
  leaves absent → `P1-03-theme-system.md`.
- **Bundling Inter 400/500/600.** `Theming.md` → Decisions → *Does a theme supply its own
  font* settles that Inter is bundled as **Neon's** font choice, not an app-wide constant —
  so the font files and their `pubspec.yaml` `fonts:` declaration land with Neon's theme
  definition in `P1-03-theme-system.md`, under the same rule as Requirement 3. This PRD
  declares no fonts.
- **The repository interface and its Hive implementation** (`lib/storage/`), preference
  storage, and the persisted model shapes → `P1-04-persistence.md`.
- **The hardcoded-theme-value scan test** and its per-file baseline →
  `P1-05-theme-guard-test.md`. Requirement 13 exists to make that PRD's empty baseline
  achievable; the guard itself is not built here.
- **Error catching and the crash-report object** (`lib/diagnostics/`) →
  `P1-06-crash-reporting.md`. Requirement 11 guarantees a single wrappable `runApp` call site
  and nothing more.
- **The entitlement model** (`lib/entitlements/`) — what the player owns, its local cache, the
  free-tier defaults, and the query interface siblings read → `P1-07-entitlements.md`. Same
  wave, parallel-safe with this PRD.
- **The route table and everything `go_router` is configured with** (`lib/navigation/`) — what
  routes exist, how they are named and nested, shells, redirects, transitions, and deep-link
  handling → `P2-01-navigation.md`. This PRD declares the `go_router` dependency *[Tech Design
  → Decisions → Navigation approach — go_router]*, wires `MaterialApp.router`, and ships one
  placeholder route for that PRD to replace. It chooses nothing about routing beyond
  installing the package the Decision names.
- **Sound playback** (`lib/audio/`) → `P2-02-audio.md`. This PRD declares `audioplayers` and
  creates both `lib/audio/` and `assets/audio/`; the **`assets/audio/` declaration in
  `pubspec.yaml` belongs to `P5-02-asset-generation-replicate.md`**, which lands the first
  audio file — per Requirement 3, `P5-02` req 9 and `P2-02` req 18.
- **Haptic feedback** (`lib/haptics/`) → `P2-03-haptics.md`.
- **Every screen** (`lib/ui/board/`, `lib/ui/menus/`) — main menu, open games list, name
  prompt, board, theme overlay, settings, game-over modals → waves P3/P4.
- **In-app purchases** (`lib/purchase/`) — StoreKit, the purchase flow, restore-purchases,
  purchase outcomes and the store-side product concerns → `P4-05-purchase-flow.md`.
- **The app icon.** *[Tech Design → Decisions → The app icon]* settles that the app ships one,
  that it is not the main-menu logo, and that it lives in the iOS asset catalog rather than
  the Flutter `assets/` tree — but who produces it is open there. The scaffold leaves the
  generated placeholder icon in place; replacing it belongs with the asset work
  (`P5-02-asset-generation-replicate.md`) and the submission (`P5-03-release-fastlane.md`).
- **Release tooling.** fastlane, `deliver`/`match`/`produce`, and the App Store Connect
  listing are decided but explicitly deferred: *"Set up when actually approaching shipping —
  not now."* *[Tech Design → Decisions → Release tooling — fastlane]*
- **Asset generation.** The single Replicate API script, the logo, and sound assets are *"not
  now"* by decision. *[Tech Design → Decisions → Where do sound and art assets come from?]*
  This PRD creates the folders, not their contents.
- **Alternative Game Styles.md** — parking lot, not what is being built.

## Open Questions

Everything fenceable has been fenced into a requirement above. What remains genuinely needs a
decision from outside this PRD.

### Blocking — answered above as proposals, needing confirmation

- **The Dart package name** and **`hive` vs `hive_ce`** — see *Pending confirmation* at the
  top. Both carry a proposal so the PRD executes on confirmation; neither is guessable by an
  implementer without committing the whole codebase to the guess.

### Non-blocking — owned elsewhere, recorded so they are not answered by accident

- **Which bundled icon set the app ships, and whether it is a pub package.** `Theming.md` →
  Decisions → *Do themes control the app's chrome icons?* settles that chrome icons are
  theme-controlled and that "a theme may either name a glyph from a bundled icon set or ship
  its own image" — so a bundled set is sanctioned, but **no Decision names one**, and
  `design_handoff_game_ui/README.md` → *Assets* names Phosphor without that being a decision.
  If it is a package it amends Requirement 14's table; if it is per-theme image assets it
  lands under Requirement 3's rule. It has an owner in practice: `P4-02-open-games-list.md`
  draws the first chrome glyph (the trash affordance), and `P1-03-theme-system.md` has
  authored `icons.trash` as a **required** slot in schema v8 — its triage rule holds that an
  unauthored *value* is debt but a missing *glyph* is a deadlock, "with no slot to read and
  no permitted literal, there is no legal way to draw the thing at all." The slot closes the
  deadlock; naming the set is what remains. `P1-05-theme-guard-test.md` meanwhile wrote its
  `icon-constant` rule as a family match against `PhosphorIcons\w*` and flags the symbol name
  as **provisional** precisely because Requirement 14's table names no package.
- **Are the theme YAML files declared as assets in `pubspec.yaml`?** *[Tech Design → Open
  Questions → 2. Theme loading]*, worded as the doc words it. Requirement 3 fixes only that no
  declaration may name an empty directory; the question itself is `P1-03-theme-system.md`'s.
- **Whether the iOS target device family includes iPad.** *[Tech Design → Decisions → Device
  support]* orders iPhone first and iPad second but sets no build setting, and the portrait
  lock in Requirement 7 applies to both. Left at the `flutter create` default rather than
  narrowed, because narrowing it is a product call.

### Closed since the last revision

- **Where error-handling code lives.** Closed by the doc amendment that added `diagnostics/`
  to Tech Design → Decisions → Project structure — layer-first, owned by
  `P1-06-crash-reporting.md`. Requirement 2 now creates it. This also closes that PRD's Open
  Question 6.

### Notes for `P2-01-navigation.md`

Both gaps that PRD flagged against this one are now closed, and neither needs rewriting here:

- **Open Question 16** says this PRD "does not create the directory this PRD depends on" and
  quotes a superseded tree. Requirement 2 creates `lib/navigation/` and Requirement 11 puts
  the placeholder router in it. Stale — can be closed.
- **Requirement 17** says the declared dependency set has no router in it. Requirement 14 now
  declares `go_router`. Stale — can be closed. Its Open Question 1, asking which routing
  approach to use, is likewise settled by *[Tech Design → Decisions → Navigation approach —
  go_router]* rather than by this PRD.
