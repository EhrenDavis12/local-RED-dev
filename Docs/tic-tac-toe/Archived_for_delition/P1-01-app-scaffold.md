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

## Confirmed by the user — two literals, not two designs

Both were needed before `flutter create` could run, and **both are now settled by the user**,
each proposal accepted as written. Neither changes anything else in this document.

1. **The Dart package name is `tic_tac_toe_extreme`** — *settled by the user; the proposal
   below was accepted as written.* It is the lower_snake_case form of the app name *[Tech
   Design → Decisions → App name]*, matching the bundle identifier's final segment.
   `Tic-Tac-Toe-Extreme` is the *repository* name and is not a legal Dart package identifier
   (hyphens and capitals are not permitted), so Requirement 1 could not have run as the
   directory is named. This could not be deferred: every `package:` URI in the codebase and
   every import in twenty-three downstream PRDs embeds it, and changing it later is a
   whole-codebase rewrite.
2. **The Hive packages are `hive_ce` + `hive_ce_flutter`** — *settled by the user; the
   `hive` + `hive_flutter` fallback is **not** taken.* *[Tech Design → Decisions → Game state
   storage — Hive]* names "Hive" and `hive_flutter` and stops there, but the two options are
   different packages with different names, different Flutter pairings (`hive_flutter` vs
   `hive_ce_flutter`) and different imports. The reasoning the accepted proposal carried:
   `hive_ce` is the actively maintained community fork while `hive` has been dormant, and
   that the decision to store JSON with **no `TypeAdapter`s** *[Tech Design → Decisions →
   Serialization and the storage layer]* means the app uses only the box API the two share —
   so the fork costs nothing and the maintenance risk sits with the other option.
   `P1-04-persistence.md` builds directly on this and is unblocked.

**Neither literal is recorded in a design doc.** No Decision names the Dart package name at
all, and Tech Design → Decisions → *Game state storage — Hive* still says `hive_flutter`.
Both settlements live in the PRDs until a doc edit lands them, and that edit is
`forge-doc-writer`'s rather than this PRD's.

**A third user settlement now lives in a requirement rather than here**, because it changes a
requirement's content rather than supplying a literal: **the app is upright portrait only and
does not rotate upside-down** — Requirement 7. It is likewise recorded in no design doc.

**A fourth, and unlike the others it changed a live Decision rather than filling a gap: the
minimum iOS version is raised from 13 to 15** — Requirement 8. **This one is recorded in a
design doc**: `Tech Design.md` → Decisions → *Minimum iOS version* now reads **iOS 15** and
carries the reasoning. The reason for the raise is `P4-05-purchase-flow.md`'s StoreKit 2
dependency — at an iOS 13 floor that layer was unbuildable, and this requirement is what the
floor is actually set by.

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
iOS 15 minimum, bundle identifier `com.ehrendavis.tictactoeextreme`, display name "Tic Tac
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
   (`src/Tic-Tac-Toe-Extreme`), with package name `tic_tac_toe_extreme` (**settled by the
   user** — see above). Nothing is carried over or refactored from earlier Flutter
   work, and the existing `README.md` at that path is preserved.
   *Source: Tech Design → Decisions → Framework — Flutter; Language — Dart; Fresh build, not
   a refactor. The package name itself is the user's settlement recorded above, not a doc
   citation. The README is observed repo state.*
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

5. **`hive_ce_flutter` is never imported from `engine/`; `storage/` owns it.** It is not pure
   Dart, so it cannot cross into the engine layer.
   *Source: Tech Design → Decisions → Serialization and the storage layer — "`hive_flutter`
   is not pure Dart, so it must never be imported from `engine/`." The doc names the `hive`
   spelling; the package is `hive_ce_flutter` per the settlement recorded above, and the rule
   is the same one.*
   *Verification:* the same scan as Requirement 4, extended to fail on any import whose
   package segment begins `hive` — which covers both `hive_flutter` and `hive_ce_flutter` —
   under `lib/engine/`. One test file covers both requirements.

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

   **The pattern set is the implementer's, and this PRD deliberately does not fix one.**
   Stated because `P4-05-purchase-flow.md` reqs 230–234 build against this scan and would
   otherwise be coding against a list that does not exist. There is no enumerated set of
   banned symbols here — no design doc names one, and inventing a closed list in wave 1 would
   either be incomplete (a package added in wave 4 that this list never heard of) or
   over-broad (catching the store SDK's own transport and failing the day `P4-05` lands).
   Instead:
   - **The property is what is fixed**, not the regex: no HTTP client and no network target
     other than the store SDK, over `lib/` only. An implementer chooses patterns that
     establish it — `dart:io`'s `HttpClient` / `Socket` / `WebSocket`, `package:http`,
     `package:dio` and the like are the obvious starting set, and that is a starting set
     rather than the specification.
   - **The acceptance condition is `P4-05` req 7 passing.** Whatever pattern set is written
     here must still be green when the store layer lands, and that is the check that decides
     whether it was drawn correctly. A set that fails then was wrong when it was written.
   - **Widening it later is expected and is not a breach of this requirement.** Adding a
     pattern when a new transport appears is ordinary maintenance; narrowing it to let a real
     network call through is not.

   *Scope note:* the scan covers `lib/` only, so build-time tooling is outside it by
   construction — `P5-02-asset-generation-replicate.md`'s Replicate script lives in `tool/`,
   uses `dart:io`'s `HttpClient`, and resolves every path against its `--root` flag
   (defaulting to the package root) rather than the CWD, so neither its network use nor its
   writes reach the shipped app.

7. **The app runs portrait only, and upright only — it does not rotate upside-down.** No
   landscape and no 180° rotation, at both the Flutter level and the iOS project level.
   *Source: Tech Design → Decisions → Orientation — portrait only, for the landscape half.
   **The upright-only half is settled by the user** and is recorded in no design doc: that
   Decision says "portrait only" and does not say whether portrait includes `portraitDown`.
   Landing it in the doc is `forge-doc-writer`'s, not this PRD's.*
   *Verification, four parts:*
   - `main.dart` calls `SystemChrome.setPreferredOrientations` with
     **`[DeviceOrientation.portraitUp]` alone** — `portraitDown` does not appear in the list,
     and does not appear anywhere in `lib/`;
   - `ios/Runner/Info.plist` → `UISupportedInterfaceOrientations` (the iPhone key) contains
     `UIInterfaceOrientationPortrait` and **nothing else** — no landscape value, and
     **`UIInterfaceOrientationPortraitUpsideDown` is absent**;
   - **`UISupportedInterfaceOrientations~ipad`**, which `flutter create` writes as a separate
     key containing `UIInterfaceOrientationLandscapeLeft` and
     `UIInterfaceOrientationLandscapeRight` among its four values, is reduced to that **same
     single value** — the upright-only rule applies to both key sets, not just the iPhone one;
   - rotating the simulator through all four orientations does not re-lay-out the app,
     **checked on an iPad simulator as well as an iPhone one**.

   **The two levels have to agree, and in the previous revision they did not.** That revision
   asked for "the two portrait values" at the Flutter level while asking the plist for
   portrait values with no landscape value — which a build could satisfy with `portraitUp` +
   `portraitDown` in Dart and no `UIInterfaceOrientationPortraitUpsideDown` in the plist. That
   combination is not a compromise between the two levels; it is dead code. **iOS never
   delivers a rotation the plist does not list**, so the Flutter-level preference for
   `portraitDown` could never take effect, while reading like a decision that the app rotates.
   Both levels now name the upright orientation alone, so the requirement is verifiable at
   either level and they cannot drift apart.

   **Why the second key is named explicitly.** A build satisfying an iPhone-only reading of
   this verification still permits landscape on iPad, because iOS reads the `~ipad` variant
   there and the generated one allows both landscape orientations. The Flutter-level
   `setPreferredOrientations` call masks this in most manual testing, which is what makes it
   worth asserting in the plist rather than by rotating a device.
   *Boundary:* this fixes the orientation lock on both key sets. It does **not** decide
   whether iPad is a declared target device family at all — that stays open, see Open
   Questions, and this requirement is written to hold whichever way it lands.

8. **Minimum iOS deployment target is iOS 15** — *raised from iOS 13, settled by the user.*
   *Source: Tech Design → Decisions → Minimum iOS version, **now "iOS 15"** — settled by the
   user and since landed in the doc. Forced by `P4-05-purchase-flow.md` Requirements 4, 14 and 16,
   which are built on `Transaction.currentEntitlements`, `Transaction.updates` and
   `AppStore.sync()` — StoreKit 2 APIs that require iOS 15. At iOS 13 the purchase layer was
   unbuildable on the project's own floor; `P4-05` records the conflict and the failure it
   avoided.*
   *Verification:* `ios/Podfile` declares `platform :ios, '15.0'` and the Xcode project's
   `IPHONEOS_DEPLOYMENT_TARGET` is `15.0` for every configuration; `flutter build ios
   --no-codesign` succeeds.

   > **This requirement is where the floor is actually set.** `P5-03-release-fastlane.md`
   > Requirement 13 asserts the submitted build's target and cites this one;
   > `P4-01-main-menu.md` Requirement 19 reasons from the floor to a layout width. Both were
   > updated with this settlement.

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
    per Requirement 11, whose placeholder surface trips **none** of the rules
    `P1-05-theme-guard-test.md` Requirement 6 defines. After this PRD the app launches to an
    empty placeholder surface — deliberately not a screen. The first real screen is
    `P4-01-main-menu.md`, reached through `P2-01-navigation.md`.
    *Source: derived, and the derivation matters — `P1-05-theme-guard-test.md` Requirement 8
    requires the committed baseline to ship with **zero** recorded violations, and its
    Requirement 3 exempts only `lib/theme/`. The generated demo contains `Colors.deepPurple`,
    `Icons.add`, a literal `fontSize` and hardcoded strings — a full slate of what that guard
    scans for. Leaving it in place would either fail `P1-05` or force a non-empty baseline,
    contradicting Tech Design → Decisions → Do we add a test that fails on hardcoded theme
    values? ("the baseline starts at zero").*

    **The permitted placeholder surface, stated precisely.** An earlier revision of this
    requirement named five patterns — `Colors.`, `Icons.`, `fontSize:`, `Color(0x` and
    `Duration(` — which is **narrower than the guard it exists to satisfy**. `P1-05` req 6's
    rule set is twelve rules, so a placeholder containing `FontWeight.w600`,
    `BorderRadius.circular(12)`, `fontFamily: 'Inter'`, `CupertinoIcons.circle`,
    `AssetSource('…')`, a literal `assets/…` path or a `.withOpacity(…)` call would satisfy
    the old five-pattern check and **still break `P1-05`'s zero baseline** — the exact
    failure this requirement exists to prevent, arriving through the gap between two lists.
    The scan is therefore stated against that PRD's rule set rather than restated as a
    shorter one of its own.

    **All twelve rules apply**, by name, as `P1-05` req 6 defines them and with `lib/theme/`
    the only exempt path (its req 3) — which the placeholder is not in: `color-hex`,
    `color-palette`, `opacity-call`, `duration-literal`, `font-family-literal`,
    `font-size-literal`, `font-weight-literal`, `radius-literal`, `asset-source`,
    `asset-path`, `icon-constant` and `mark-glyph`. **`P1-05` owns the patterns; this
    requirement owns only that the placeholder trips none of them.** If a rule's pattern
    changes there, nothing here needs rewriting.

    **Positively: what the placeholder may contain.** Layout and structural widgets with no
    visual value of their own — a `Scaffold`, a `Center`, a `SizedBox`, a `Column` — plus
    spacing and padding numbers, which are **code constants and not guard violations** per
    `Theming.md` → Decisions → *Does a theme control spacing and padding?* and `P1-03`'s v7
    removal of every spacing key. If it is genuinely empty it trips nothing by construction,
    and that is the cheapest way to satisfy this.
    *Verification:* the generated `test/widget_test.dart` is gone; `flutter test` passes; a
    scan of `lib/` finds no construct matching any of the twelve rules above — including, at
    minimum, no `Colors.`, no `Color(0x`, no `.withOpacity(`/`.withValues(alpha:`, no
    `Duration(<unit>: <number>)`, no `fontFamily:`, no `fontSize:`, no `FontWeight.`, no
    `BorderRadius.circular(`/`BorderRadius.all(`/`Radius.circular(`, no `AssetSource(`, no
    literal `'assets/…'` path, and no `Icons.` / `CupertinoIcons.` / `PhosphorIcons*.`
    reference; and `P1-05`'s guard passes with an empty baseline when it lands.
    **The last clause is the real acceptance condition** — this list is a convenience for
    building before `P1-05` exists, and `P1-05`'s own scan is what decides.

14. **The dependency set declared in `pubspec.yaml` is exhaustive as of this wave**, and any
    later addition amends this requirement rather than being added silently:

    | Package | Kind | Source |
    |---|---|---|
    | `flutter_riverpod` | runtime | Tech Design → State management — Riverpod |
    | `go_router` | runtime | Tech Design → Navigation approach — go_router |
    | `shared_preferences` | runtime | Tech Design → Persistence package |
    | `hive_ce` + `hive_ce_flutter` | runtime | Tech Design → Game state storage — Hive, as settled by the user at the top of this PRD |
    | `freezed_annotation` | runtime | Tech Design → Serialization and the storage layer |
    | `json_annotation` | runtime | Tech Design → Serialization and the storage layer |
    | `audioplayers` | runtime | Tech Design → Audio package |
    | `build_runner` | dev | Tech Design → Serialization and the storage layer |
    | `freezed` | dev | Tech Design → Serialization and the storage layer |
    | `json_serializable` | dev | Tech Design → Serialization and the storage layer |
    | `flutter_lints` | dev | Tech Design → CI — local builds only (Requirement 15) |
    | `flutter_test` (`sdk: flutter`) | dev | **Required by this PRD's own requirements** — see below |

    **`flutter_test` is in the table because this PRD cannot be satisfied without it**, and
    an "exhaustive" table that omitted it was wrong on its own terms. `flutter create`
    generates the entry; the point of listing it is that it must not be *removed* as
    unused-looking, and that a sibling PRD reading this table as the complete set finds it
    there. It is provably required rather than assumed: Requirements 4, 5, 11 and 13 all
    specify test files, and Requirement 15 requires `flutter test` to exit zero — none of
    which compiles without it. It is declared as `sdk: flutter` rather than a version
    constraint, which is why it carries no caret range under *Version constraints* below.

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
    **`cupertino_icons` is also generated by `flutter create` and is deliberately *not* in
    this table — flagged, not decided.** See Open Questions: keeping it or dropping it is a
    product call that rides on which icon set the app ships, and it interacts with `P1-05`
    req 6's `icon-constant` rule, which bans `CupertinoIcons.` outside `lib/theme/`. This
    requirement records the gap rather than closing it, so an implementer does not silently
    delete a generated dependency or silently bless one.
    **Still unnamed:** the store SDK, added by `P4-05-purchase-flow.md`; and an icon package,
    if the bundled icon set ships as one — see Open Questions, which is now the last unnamed
    package and has a sibling waiting on it.
    **Version constraints:** every entry uses a caret range (`^x.y.z`) pinned to the version
    resolved at scaffold time, and `pubspec.lock` **is committed**, per Dart's guidance for
    application packages — without it, twenty-three downstream PRDs build against whatever
    resolved that day. The one exception is `flutter_test`, which is an SDK dependency and
    takes `sdk: flutter`.
    *Verification:* `flutter pub get` resolves with no version conflict; `pubspec.lock` is
    tracked in git; `dart run build_runner build` exits zero against an empty model set;
    `flutter test` runs, which is what demonstrates `flutter_test` is declared.

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
- **The hardcoded-theme-value scan test**, its twelve rules and their patterns, and its
  per-file baseline → `P1-05-theme-guard-test.md`. Requirement 13 exists to make that PRD's
  empty baseline achievable and cites its rule set by name; the guard itself, and every
  regex in it, is not built here.
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
  installing the package the Decision names. **Including whether the iOS back-swipe is
  available on a given route** — that PRD's req 23 blocks it on the game route; nothing here
  configures a gesture.
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

### Blocking — none

Both items that stood here are answered. See *Closed since the last revision*.

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

- **Does `cupertino_icons` stay in `pubspec.yaml`?** *(Raised by this PRD; needs a call that
  is not this PRD's to make.)* `flutter create` generates the dependency, and Requirement 14
  declares its table **exhaustive as of this wave** — so the table and the generated file
  currently disagree, and an implementer resolves that disagreement silently in one of two
  directions. Both are defensible and neither is free:
  - **Drop it.** Nothing in any PRD reads `CupertinoIcons`, and `P1-05-theme-guard-test.md`
    req 6's `icon-constant` rule
    (`r'\b(?:Icons|CupertinoIcons|PhosphorIcons\w*)\.\w+'`) bans the symbol outside
    `lib/theme/` anyway, so keeping a package whose only export is banned reads as dead
    weight. Requirement 13 is written so the placeholder cannot use it either.
  - **Keep it.** It is one small, first-party package, it is what `flutter create` ships, and
    if the icon-set question above ever lands on Cupertino glyphs it is already there —
    resolved inside `lib/theme/`, which is the one path `P1-05` req 3 exempts, so the ban is
    not an argument against it.

  **This is downstream of the icon-set question**, which is why it is recorded beside it
  rather than fenced: answering that one probably answers this one. Requirement 14 leaves the
  row out and says so explicitly, so nothing is decided by omission in either direction.

- **Are the theme YAML files declared as assets in `pubspec.yaml`?** *[Tech Design → Open
  Questions → 2. Theme loading]*, worded as the doc words it. Requirement 3 fixes only that no
  declaration may name an empty directory; the question itself is `P1-03-theme-system.md`'s.

- **Whether the iOS target device family includes iPad.** *[Tech Design → Decisions → Device
  support]* orders iPhone first and iPad second but sets no build setting. Left at the
  `flutter create` default rather than narrowed, because narrowing it is a product call.
  **Requirement 7 no longer depends on the answer:** its verification now names the
  `UISupportedInterfaceOrientations~ipad` key explicitly, so the portrait lock is asserted on
  both key sets and holds whether or not iPad is ever a declared target. Only the device
  family itself is open.

### Closed since the last revision

- **The Dart package name — ANSWERED by the user: `tic_tac_toe_extreme`.** The proposal in
  *Confirmed by the user* was accepted as written. **Requirement 1** now states it rather
  than proposes it, as does the *Confirmed by the user* section above, and the twenty-three
  downstream PRDs whose `package:` URIs embed it — `P1-06-crash-reporting.md` req 18 and
  `P2-01-navigation.md` req 3 spell it out explicitly — are consistent with it as written.
  *(An earlier revision of this entry also cited Requirement 14. That was wrong: Requirement
  14 is the dependency table and states no package name. Corrected rather than silently
  dropped, because a reader chasing the citation would have found nothing and had no way to
  tell whether the requirement or the reference was at fault.)*
- **`hive` vs `hive_ce` — ANSWERED by the user: `hive_ce` + `hive_ce_flutter`.** The proposal
  was accepted as written and the `hive` + `hive_flutter` fallback is not taken. Requirements
  5 and 14 state it — and Requirement 14's table does carry these two rows, so that citation
  holds; `P1-04-persistence.md` is unblocked and its reqs 13–14 name the same packages.
- **Does "portrait only" include upside-down? — ANSWERED by the user: no.** The app is
  **upright portrait only**: `setPreferredOrientations` takes `DeviceOrientation.portraitUp`
  alone, and `UIInterfaceOrientationPortraitUpsideDown` is absent from both
  `UISupportedInterfaceOrientations` and `UISupportedInterfaceOrientations~ipad`.
  **This also resolves a contradiction inside Requirement 7**, found in review: its previous
  verification asked the Flutter level for two portrait values and the plist for one, which
  no build could satisfy consistently and which left the `portraitDown` preference dead
  whichever way an implementer went. Both levels now name the upright value alone.
  **Owed to the docs:** Tech Design → Decisions → *Orientation — portrait only* says only
  "portrait only" and does not address the 180° case; landing this there is
  `forge-doc-writer`'s.
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
