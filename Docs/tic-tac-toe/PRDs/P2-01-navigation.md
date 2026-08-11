**Build-readiness: 91**

# PRD: Navigation and the Back Stack

> **Status:** Draft · Source docs read: `Menus and UI.md`, `Tech Design.md`,
> `Game Overview.md`, `Game Board Design.md`, `Theming.md`, `Animations.md`, `Rules.md`,
> `roadmap.md`, plus the read-only reference asset `design_handoff_game_ui/README.md`.
> `Alternative Game Styles.md` is a declared parking-lot doc and was not sourced from.

**Wave:** P2 · **File:** `P2-01-navigation.md` — parallel-safe with the other P2 PRDs.

> **Why the stamp is not higher.** The mechanism is settled (`go_router`), so the route
> table, the operation mapping and the layer's body are all specified below and buildable.
> What remains are three **one-line variants** across one operation and two page builders:
> Open Question 8 decides whether `leaveOpenGamesList()` is a `pop` or a `go`, and Open
> Question 10 decides whether the name prompt and the in-game quick actions are opaque or
> non-opaque pages. Both variants of each are written out below, so nothing is left to
> invent — but they are the user's calls, not an implementer's. **Open Question 2 —
> `exitGameToMainMenu()` — is now closed by the user: it is `router.go('/')`.** One route
> (requirement 21) also points at a screen no PRD owns yet.

> **Requirement numbering is load-bearing.** Four consumer PRDs cite requirements here by
> number (`P4-01`, `P4-02`, `P4-03`, `P4-04`), and citation drift into this file has had to
> be corrected once already. Requirements 1–19 have not moved; requirements 20, 21 and 22
> were appended for exactly this reason, **as was requirement 23**, and anything further
> should be too.

**Dependencies:**

- `P1-01-app-scaffold.md` — creates `lib/navigation/` (its req 2, with a `.gitkeep`), the
  single `runApp` call site and the `ProviderScope` above `MaterialApp` (its req 11), and
  leaves `MaterialApp`'s `home:` / routing configuration as the placeholder this PRD
  replaces (its reqs 11 and 13). Riverpod without codegen is its req 12. Its package name,
  settled by the user, is `tic_tac_toe_extreme` — the `package:` URI requirement 3's snippet
  imports.
- `P1-03-theme-system.md` — `activeThemeProvider` in `lib/theme/theme_providers.dart`, the
  accessor requirement 19 reads any transition value from. Its req 24 makes `read` normative
  for services and `watch` for widgets.
- `P1-04-persistence.md` — `OpenGamesRepository.count()` for requirement 7's branch, and
  `GameId` (its req 22) as the parameter type of `openGame` and `openDeleteConfirmation`.
  Its Open Question 6a records that this PRD's contract can be written against `GameId`
  today.
- `P3-02-move-input.md` — its req 24 publishes `pendingSelectionProvider` and its `clear()`
  entry point, which requirement 20 below calls. This is a **wave-3 PRD**, so requirement 20
  is specified here and lands when that provider exists; nothing else in this PRD waits on
  it. See requirement 20 for why the call has to originate in this layer, and requirement 23
  for the one path that would have bypassed it.

**Cross-PRD consequence of the routing decision.** `go_router` is a new package, and
`P1-01-app-scaffold.md` req 14 declares the dependency set exhaustively, so that list must
gain `go_router`. `Tech Design.md` → Decisions → *Navigation approach — go_router* names
this consequence itself. It is being routed separately; this PRD does not edit `P1-01`.

**Depended on by:** every screen PRD. Each owns a destination this layer moves between and
specifies its own contents: `P3-01-board-rendering.md`, `P3-04-game-over-rematch.md` (its
req 5, whose back-to-main-menu control is the second caller of requirement 15's operation),
`P4-01-main-menu.md` (its reqs 14–16, and its req 23, which requirement 21 below answers),
`P4-02-open-games-list.md` (its reqs 8, 10, 12; its OQ-7, which names requirement 13's
`leaveOpenGamesList()` as the owner of its back control; and its req 28, which requirement 22
below answers), `P4-03-theme-selection.md`, `P4-04-settings.md`. `P4-05-purchase-flow.md` may
become a seventh — see Out of Scope.

**Callers land in later waves, deliberately not blocking.** The deliverable of this wave is
the layer — its interface (requirement 3), its router configuration (requirement 2), its
acquisition seam (requirement 4) and the scans in requirements 1, 16 and 19 — not any screen
that calls it. Several testables below describe transitions between screens that waves P3
and P4 have not built. At this wave they are verified against a **recording fake
`AppNavigator`** injected through requirement 4's provider override, and the route table is
verified directly against the `GoRouter` instance; the screen-level assertions are **owned
by** the requirement named in each *Wave note*. This is the posture `P2-03-haptics.md` and
`P2-02-audio.md` already publish, applied here.

---

## Problem

Nothing owns the movement between screens. Every screen PRD specifies its own contents and
then hands off by filename — main menu → open-games list → game screen → settings → game
over — but no PRD says how a player gets from one to the next or back again.
`Menus and UI.md` → Decisions → *Navigation and the back stack* states it for the flows:
*"No screen flow in this doc currently says what 'back' does anywhere."*

The cost is already visible in the other PRDs. `P4-02-open-games-list.md` → Open Question 7
records that the approved drawing `1b` has a back button no design doc mentions and nothing
says where it leads. `P4-04-settings.md` settles that reaching settings mid-game must not
abandon the game, but its Open Questions record that no doc names the control that returns
you to it. Three PRDs each assume someone else owns the back stack, and today nobody does. A
fourth consequence is quieter: `P4-02-open-games-list.md` specifies the name prompt's own
comings and goings (its reqs 8, 10 and 12), which are screen changes with no routing owner.
Requirement 11 below claims them. A fifth arrived with the About Us button: `P4-01` req 23
had a control with nowhere to send the player, and requirement 21 gives it a route. A sixth
arrived with the delete confirmation, which had no legal host at all until requirement 22.

There is also a movement nobody specified because nobody *performs* it: the platform's own
back gesture. It changes the screen without any PRD asking it to, and requirement 23 is where
that is dealt with on the one route where it does damage.

## Goal

The app has one explicit navigation layer, in one known place, built on `go_router`,
published as one Dart interface acquired one way, and every screen change goes through it.
The flows the design docs already settle work end to end: the app launches on the main menu,
Play Game reaches either a new game or the list of open ones, the theme overlay opens on top
of a main menu that stays mounted, settings is reachable from both the main menu and mid-game
without abandoning the game, and a player leaves a game — mid-play from quick actions, or
finished from the result card — back to the main menu with the game intact and resumable.
Screens call operations, never routes, so the three remaining back-stack choices land as
edits inside this layer.

## Requirements

Each requirement names the screens it moves between by filename. None specifies what a
screen contains.

### The layer itself

1. **The app has one explicit navigation layer, and every screen change goes through it**
   rather than being performed ad hoc inside a screen widget. Stated positively, because that
   is the form the guard below has to take: **the only way any widget outside
   `lib/navigation/` causes a surface to appear or disappear is by calling an `AppNavigator`
   operation.**
   *Source: `Tech Design.md` → Decisions → Navigation ("The app has an explicit navigation
   layer, and it is now in scope"); `Menus and UI.md` → Decisions → Navigation and the back
   stack ("The app has a defined navigation model — this is now in scope to build out").*

   *Testable, wave 2 — two scans, both of which run with zero screens built:*

   - **The import scan (allow-list).** `import 'package:go_router/go_router.dart'` appears
     **only** under `lib/navigation/`. This one assertion catches every routing call —
     `context.go`, `context.push`, `context.pushReplacement`, `context.pop`, `GoRoute`,
     `GoRouter` — because none of them compiles without that import.
   - **The presentation scan (closed by shape, not by enumeration).** Outside
     `lib/navigation/`, and in particular anywhere under `lib/ui/`, the source contains:
     no call matching **`show[A-Z]\w*(`** — every Flutter API that puts a surface on screen is
     a top-level `show…` function; no reference to `Navigator`, `Overlay`, `OverlayEntry`,
     `ModalRoute`, `PageRoute`, `DialogRoute` or `PopupRoute`; and no
     `GlobalKey<NavigatorState>`.

   **Why the second scan is a pattern and not a list.** An earlier draft banned `showDialog`
   and `showModalBottomSheet` by name. `showGeneralDialog` and `showAdaptiveDialog` contain
   neither substring, so both passed a guard written to stop exactly what they do — and
   `showCupertinoDialog`, `showCupertinoModalPopup`, `showMenu` and `showBottomSheet` are the
   same family. This was found by `P4-02-open-games-list.md`, which needed a host for its
   delete confirmation, found every legal mechanism closed, and identified `showGeneralDialog`
   as the escape an agent under a name-shaped constraint reaches for first, *precisely because
   it looks compliant*. A deny-list is always one API name behind; `show[A-Z]` is not,
   because the naming convention is the thing being relied on rather than any particular name.
   **Deliberately over-broad**, and the escape hatch is the point: a legitimate `show…` call
   lives in `lib/navigation/` like every other presentation mechanism. Note `showAboutDialog`
   is in the banned family — About Us is a route (requirement 21), not a platform dialog.

   **Neither scan sees a gesture.** Both are about *calls*, and the platform back-swipe makes
   none — it pops the route itself. That is why requirement 23 exists as a requirement rather
   than as a line in this one: the hole it closes is the absence of a call, which no scan for
   forbidden calls can find.

2. **The layer lives in `lib/navigation/`, and the router is configured there and installed
   at `MaterialApp.router`.**
   *Source: `Tech Design.md` → Decisions → Project structure — layer-first ("`navigation/`
   … is Flutter-side, same as `ui/` and `state/` — nothing here changes the `engine/` purity
   rule"); → Decisions → Navigation approach — go_router, which states outright that "the
   route table and route paths are not designed here — that is a PRD's job".*
   `P1-01-app-scaffold.md` req 11 names `MaterialApp`'s routing configuration as this PRD's
   extension point and req 13 ships a placeholder home; both are replaced here.
   `MaterialApp` becomes `MaterialApp.router(routerConfig: …)`.

   ```dart
   // lib/navigation/routes.dart — path constants, so no route string is spelled twice
   abstract final class Routes {
     static const mainMenu = '/';
     static const themeSelection = 'theme';       // child of '/'
     static const settings = 'settings';          // child of '/'
     static const openGames = 'games';            // child of '/'
     static const newGamePrompt = 'new';          // child of '/games'
     static const confirmDelete = 'confirm-delete/:gameId'; // child of '/games' — req 22
     static const aboutUs = 'about';              // child of '/'  — requirement 21
     static const game = '/game/:gameId';
     static const quickActions = 'quick-actions'; // child of '/game/:gameId'
   }

   // lib/navigation/app_router.dart
   GoRouter buildRouter() => GoRouter(
         initialLocation: Routes.mainMenu, // requirement 6
         routes: [
           GoRoute(
             path: Routes.mainMenu,
             builder: (context, state) => const MainMenuScreen(), // P4-01
             routes: [
               GoRoute(
                 path: Routes.themeSelection,
                 // Non-opaque: the main menu stays mounted beneath. Requirement 9.
                 pageBuilder: (context, state) =>
                     const TransparentPage(child: ThemeSelectionOverlay()), // P4-03
               ),
               GoRoute(
                 path: Routes.settings,
                 builder: (context, state) => const SettingsScreen(), // P4-04
               ),
               GoRoute(
                 path: Routes.openGames,
                 builder: (context, state) => const OpenGamesListScreen(), // P4-02
                 routes: [
                   GoRoute(
                     path: Routes.newGamePrompt,
                     // Opaque or non-opaque: Open Question 10. See requirement 11.
                     pageBuilder: (context, state) =>
                         const TransparentPage(child: NewGamePrompt()), // P4-02
                   ),
                   GoRoute(
                     path: Routes.confirmDelete,
                     // Always non-opaque — requirement 22.
                     pageBuilder: (context, state) => TransparentPage(
                       child: DeleteGameConfirmation(     // P4-02 req 28
                         id: GameId(state.pathParameters['gameId']!),
                       ),
                     ),
                   ),
                 ],
               ),
               GoRoute(
                 path: Routes.aboutUs,
                 // Ordinary opaque page. Requirement 21 — screen currently unowned.
                 builder: (context, state) => const AboutUsScreen(),
               ),
             ],
           ),
           GoRoute(
             path: Routes.game,
             // pageBuilder, not builder: the back-swipe is blocked here — requirement 23.
             pageBuilder: (context, state) => NoBackGesturePage(
               child: GameScreen(                          // P3-01
                 id: GameId(state.pathParameters['gameId']!),
               ),
             ),
             routes: [
               GoRoute(
                 path: Routes.quickActions,
                 // Opaque or non-opaque: Open Question 10. See requirement 14.
                 pageBuilder: (context, state) =>
                     const TransparentPage(child: QuickActionsSurface()), // P4-04
               ),
             ],
           ),
         ],
       );
   ```

   **The hierarchy is the load-bearing part, not the strings.** Every surface that must leave
   something mounted beneath it is declared as a *child* of what it sits on: theme selection
   under the main menu (requirement 9, settled), quick actions under the game (requirement 14,
   settled), the name prompt and the delete confirmation under the open-games list
   (requirements 11 and 22). That is what makes "the menu is still there behind the overlay" a
   property of the route table rather than of each screen's discipline. **It also means
   nothing unmounts when a surface opens over the board — which is why requirement 20
   exists.**
   **The game-over result card is not in this table.** It is drawn over the board by
   `P3-04-game-over-rematch.md` rather than routed to; its two controls act on the game
   (next game) and on this layer (back to main menu, requirement 15). Nothing here presents
   it. Note this means the card sits inside the game route, so requirement 23's gesture block
   covers it too.
   **Open Questions 5 and 10 reduce to a `pageBuilder` choice, not a route-table change.** A
   surface drawn as a sheet is the same `GoRoute` with a non-opaque page; drawn as a full
   screen it is the same `GoRoute` with an ordinary one. Neither answer moves a route or
   changes a call site.
   *The paths are this PRD's, per the Decision that leaves them to a PRD.*
   *Testable, wave 2:* the built `GoRouter` reports `initialLocation == '/'`; every path above
   resolves; `/game/:gameId` and `/games/confirm-delete/:gameId` each yield their id as a path
   parameter; no route string appears outside `lib/navigation/routes.dart`.

3. **The layer publishes this interface, and the `go_router` decision does not change it.**
   Screens invoke operations, never routes: a screen calls `exitGameToMainMenu()` and does
   not `go`, `push`, `pop`, or name a path. This is the contract the six screen PRDs code
   against, and publishing it before the mechanism was chosen is why that choice arrived as
   an additive change.

   ```dart
   // lib/navigation/app_navigator.dart
   import 'package:tic_tac_toe_extreme/storage/game_id.dart'; // P1-04 req 22

   abstract interface class AppNavigator {
     /// Presents the main menu as the app's first screen. Requirement 6.
     Future<void> openMainMenu();

     /// The Play Game branch. Reads the stored open-game count and presents the
     /// destination itself; the caller does not read the count. Requirements 7, 8.
     Future<void> playGame();

     /// The theme overlay, over a still-mounted main menu. Requirement 9.
     Future<void> openThemeSelection();

     /// The main menu's settings entry point. Requirement 10.
     Future<void> openSettings();

     /// The in-game settings entry point. Requirements 10, 14.
     Future<void> openQuickActions();

     /// Open-games list -> the opponent-name prompt. Requirement 11.
     Future<void> openNewGamePrompt();

     /// The game screen for one open game, newly created or resumed.
     /// Requirements 11, 12.
     Future<void> openGame(GameId id);

     /// Leaving a game for the main menu — from quick actions mid-play, or from
     /// the game-over result card. The only way out of a game: requirement 23
     /// blocks the back-swipe on that route. Requirement 15.
     Future<void> exitGameToMainMenu();

     /// Leaving the open-games list without picking anything. Requirement 13.
     Future<void> leaveOpenGamesList();

     /// Closes the surface on top and returns to what is beneath it. Requirement 5.
     Future<void> dismissCurrent();

     // Extended by requirement 21: Future<void> openAboutUs();
     // Extended by requirement 22: Future<void> openDeleteConfirmation(GameId id);
   }
   ```

   **This block is not the closed set.** Requirements 21 and 22 add `openAboutUs()` and
   `openDeleteConfirmation(GameId)`, appended there rather than inserted here so the
   requirement numbers four consumer PRDs cite do not move. Read requirements 3, 21 and 22
   together for the full interface. **Requirement 23 adds no operation** — it removes a way
   of leaving one, which is why it is a route configuration rather than a method.

   **Each operation maps onto exactly one `go_router` call:**

   | Operation | `go_router` implementation | Settled? |
   |---|---|---|
   | `openMainMenu()` | `initialLocation` at startup; `router.go('/')` thereafter | yes |
   | `playGame()` | `await count()`, then `push('/games')`, or the empty-state destination | branch yes; empty-state target is OQ4 |
   | `openThemeSelection()` | `router.push('/theme')`, non-opaque page | yes |
   | `openSettings()` | `router.push('/settings')` | yes |
   | `openQuickActions()` | `router.push('/game/<id>/quick-actions')` | route yes; page opacity is OQ10 |
   | `openNewGamePrompt()` | `router.push('/games/new')` | route yes; page opacity is OQ5 / OQ10 |
   | `openGame(id)` | `router.push('/game/${id.value}')` | yes — and the pushed route blocks the back-swipe, requirement 23 |
   | `exitGameToMainMenu()` | **`router.go('/')`** | **yes — settled by the user, OQ2** |
   | `leaveOpenGamesList()` | `router.pop()` **or** `router.go('/')` | **OQ8** |
   | `dismissCurrent()` | `if (router.canPop()) router.pop();` | yes — requirement 5 |
   | `openAboutUs()` | `router.push('/about')`, ordinary opaque page | route yes — requirement 21 |
   | `openDeleteConfirmation(id)` | `router.push('/games/confirm-delete/${id.value}')`, non-opaque | yes — requirement 22 |

   Every one of them is preceded by requirement 20's clear.

   **Every operation returns `Future<void>`.** `playGame()` is genuinely asynchronous
   (requirement 8), and a mixed sync/async surface would make call sites differ for a reason
   no caller can see. **No operation throws.** Requirement 8 is the only one that can fail,
   and it recovers. **`GameId` is `P1-04-persistence.md`'s type**, referenced and never
   defined here; its `.value` string is passed as a path parameter and parsed by nobody.

   **No operation returns a result to its caller — and callers must be designed around
   that.** The `Future<void>` completes when the navigation is done, not when the surface it
   opened is finished with. A modal's *outcome* — which button the player pressed, whether
   they confirmed or cancelled — never comes back through this interface, and it cannot be
   recovered another way either, because requirement 1 forbids observing the router outside
   this layer. **So any flow that seems to need a modal's answer must be restructured so that
   nothing has to hear it**: the surface acts on the state itself, or the caller does its work
   before opening the surface rather than after it closes.

   This has already bitten once, which is why it is written here rather than left implicit.
   `P4-02-open-games-list.md` req 29 carried a bullet — the row's delete reveal closes when
   the confirmation is dismissed with No — that became unimplementable the moment the
   confirmation became a child route, and was fixed by reordering so the reveal closes
   *before* the modal opens. The general shape is worth naming: **a host choice that touches
   no model, no storage and no engine can still make a sibling requirement unassertable.**
   Check what a flow needs to *hear* before assuming a route can host it.

   *Testable, wave 2:* the interface compiles against `P1-04`'s `GameId`; a recording fake
   records one invocation per call with its arguments; the real implementation, driven against
   a test `GoRouter`, leaves the expected location after each operation.

   **One thing this interface still does not settle.** Whether `openSettings()` and
   `openQuickActions()` resolve to the same *surface* follows Open Question 7 — two operations
   and two routes exist because there are two settled entry points, not because there are
   certainly two screens.

   **The identifiers are this PRD's, not the design docs'.** No doc names an API. The *set* is
   derived from the settled transitions and each doc comment cites the requirement that
   settles it; the names are a proposal, and renaming any of them is free so long as the set
   stays one operation per settled transition.

4. **Screens acquire the layer through a Riverpod provider — plain Riverpod, no codegen —
   and by no other means.** No static singleton, no global instance, no `BuildContext`
   extension reaching a `GlobalKey<NavigatorState>`.

   ```dart
   // lib/navigation/navigation_providers.dart
   final goRouterProvider = Provider<GoRouter>((ref) => buildRouter());

   final appNavigatorProvider = Provider<AppNavigator>(
     (ref) => GoRouterAppNavigator(
       router: ref.watch(goRouterProvider),
       openGames: ref.watch(openGamesRepositoryProvider), // P1-04, for requirement 8
       ref: ref,                                          // for requirement 20
     ),
   );
   ```

   `GoRouterAppNavigator` is the only implementation and the only holder of the `GoRouter`.
   `app.dart` reads `goRouterProvider` for `MaterialApp.router`'s `routerConfig`; every screen
   reads `appNavigatorProvider` and never the router.
   *Source: `Tech Design.md` → Decisions → State management — Riverpod ("settings and the
   theme be readable from **everywhere**, including deep in the board widget tree");
   `P1-01-app-scaffold.md` req 12 (no `@riverpod` codegen, no legacy `StateNotifier`) and
   req 11 (the `ProviderScope` above `MaterialApp`). Precedent: `P2-02-audio.md` req 5 reaches
   its layer the same way.*
   **`Provider`, not `NotifierProvider`:** the navigator exposes operations, not observable
   state, so there is nothing for a `Notifier` to hold. `P1-01` req 12's constraint is *no
   codegen and no `StateNotifier`*, and this satisfies both.

   **This is why the seam matters, and it is not a stylistic preference.** Under a singleton
   or an internal `GlobalKey`, `P4-01-main-menu.md` reqs 14–16 and `P4-02-open-games-list.md`
   reqs 8, 10 and 12 would have no injection point, and their "invokes X exactly once"
   testables could not be written at all. Six PRDs depend on this choice.
   *Testable, wave 2:* a scan finds no top-level or static `AppNavigator` or `GoRouter`
   instance anywhere in `lib/`; a widget test overrides `appNavigatorProvider` with a
   recording fake and observes calls made by any widget beneath the scope.

5. **`dismissCurrent()` takes no argument, returns nothing, and is a no-op when nothing is
   dismissible.** It closes the surface on top and reveals what is beneath. Concretely:
   `if (router.canPop()) router.pop();` — nothing else. With no dismissible surface on screen
   it does nothing at all: it does not pop the main menu, does not exit the app, and does not
   throw.
   *Source: `Tech Design.md` → Decisions → Navigation approach — go_router ("Dismissing a
   route becomes `context.pop()` rather than `Navigator.pop`"). The `canPop()` guard, and
   therefore the no-op case, is this PRD's call: the alternatives are worse — throwing makes
   every call site defensive, and popping the root blanks the app on a double invocation.*
   **It is the single dismissal for every surface this layer presents:** the theme overlay
   (requirement 9), the name prompt (requirement 11), the in-game quick actions
   (requirement 14), About Us (requirement 21) and the delete confirmation (requirement 22).
   Two of those have unresolved page kinds — Open Questions 5 and 10 — and because all are
   child routes, one `pop()` covers them regardless, so a later answer changes a `pageBuilder`
   and not this operation. It does **not** dismiss the game-over result card, which is not a
   route — see requirement 2. **It is also not the way out of a game:** the game route is left
   by `exitGameToMainMenu()` (requirement 15), and requirement 23 removes the gesture that
   would otherwise have popped it.
   *Testable, wave 2:* on a router at `/` alone, calling it leaves the location `/` and
   nothing is popped; from `/theme` it returns to `/`; from `/games/new` to `/games`; from
   `/games/confirm-delete/abc` to `/games`.

### Launch

6. **The main menu is the app's launch screen** — the first screen the app presents, with
   nothing beneath it in the stack. This is the router's `initialLocation: '/'`.
   *Source: `Menus and UI.md` → Decisions → Navigation and the back stack ("The main menu
   being the app's launch screen is assumed throughout this doc … Recording it here since
   nothing contradicts it"); → Screens (so far) → 1. Main Menu.*
   *Testable, wave 2:* the built router's initial location is `/` and `canPop()` is false
   there.
   *Wave note:* the screen is `P4-01-main-menu.md`, wave 4.
   *Not settled:* whether anything renders *before* it — see Open Question 13. This
   requirement is about the first screen of the app, not the first pixels on the display.

### Out of the main menu

7. **Play Game branches on whether stored open games exist: with none, the player goes
   straight into a new game and the open-games list is not shown; with one or more, the
   open-games list opens.** The branch is evaluated inside the layer, so callers of
   `playGame()` never read the count themselves.
   *Source: `Menus and UI.md` → Play Game → Where It Takes You ("No open games — straight
   into a new game, no intermediate screen"; "Open games exist — a new screen listing all open
   games"); → Decisions → Is the main menu button "New Game" or "Play Game"?*
   *Testable, wave 2:* with a stub `OpenGamesRepository` reporting `count() == 0`,
   `playGame()` never navigates to `/games`; at 1, 2 and 100 the resulting location is
   `/games`.
   *Wave note:* the button is `P4-01-main-menu.md` req 14; the list is
   `P4-02-open-games-list.md` reqs 1–2, which own the screen-level assertions in wave 4.
   Whether the empty path lands on the **name prompt** (`/games/new`) or directly on a new
   game (`/game/<id>`) is Open Question 4, so this must not be read as settling it either way.

8. **`playGame()` is asynchronous, navigates nowhere until the count resolves, navigates at
   most once per invocation, and recovers from a failed read without reporting it.** The count
   comes from `P1-04-persistence.md` req 21's `Future<int> count()`, which that PRD states is
   asynchronous like every operation on the store. Concretely:
   - **While the read is in flight the main menu stays on screen.** No spinner, no
     intermediate surface and no blank frame is specified here — nothing is pushed until there
     is a destination.
   - **Re-entrancy:** a second `playGame()` while one is in flight results in at most one push
     in total. Tapping Play Game twice does not stack two screens.
   - **If the read fails, the failure is caught and recovered here:** nothing is pushed, the
     player is left on the main menu, the in-flight guard is released so a later tap can
     succeed, and **the operation does not rethrow**.
   - **The failure is not reported this wave.** `P1-06-crash-reporting.md` req 1 fences its
     scope to *unhandled* errors reaching `FlutterError.onError` and
     `PlatformDispatcher.instance.onError`, and its req 13 publishes an install seam that
     forbids globals, statics, service locators and a Riverpod-held sink **by name** — so
     there is deliberately no public API for application code to report a caught, recovered
     error, and this layer must not invent one. Whether recovered errors should be reported at
     all is that PRD's **Open Question 4**, and this requirement is its concrete forcing case:
     if it lands on "yes", this is the first caller and the reporting line is added here.

   *(Proposed for ratification — the shape is this PRD's. No design doc addresses an
   asynchronous read behind a menu button, and none specifies what the player sees when one
   fails. Recovering rather than rethrowing is the deliberate half: letting it go unhandled
   would reach the global handlers and satisfy a report, but a failed count is not a reason to
   take the app down. What the player sees instead is Open Question 15.)*

   *Testable, wave 2 — an assertion about the recovery path, not about a crash handler:* with
   a repository stub that never completes, the location stays `/`; with one that completes
   after two invocations, exactly one push occurs; with one that **throws**, `playGame()`
   completes normally, no exception escapes it, the location stays `/`, and a subsequent
   `playGame()` against a working stub navigates — proving the in-flight guard was released.

9. **The Theme button opens theme selection as an overlay on the main menu, with the main
   menu still mounted beneath it.** It is not a screen the menu is replaced by. In the route
   table this is `/theme` as a **child of `/`** with a **non-opaque page**, which is what
   keeps the menu mounted and painted behind it.
   *Source: `Menus and UI.md` → Decisions → Is theme selection its own screen or an overlay?
   ("**An overlay** on the main menu"); → Screens (so far) → 5; `Theming.md` → Decisions →
   Where theme selection lives.*
   *Testable, wave 2:* at `/theme` the main menu widget is still in the tree; `pop()` returns
   to `/` without rebuilding the menu from scratch.
   *Wave note:* owned by `P4-03-theme-selection.md` req 1, wave 4.

10. **Settings is reachable from exactly two entry points — the main menu's Settings button
    and the game screen's top-right button — and from nowhere else.** They are two routes:
    `/settings` under the menu, `/game/:gameId/quick-actions` under the game.
    *Source: `Menus and UI.md` → Settings Menu ("Reachable from two places: 1. The **main
    menu** (Settings button). 2. The **gameplay screen**"); → Screens (so far) → 6;
    `Game Board Design.md` → Scoreboard.*
    *Wave note:* the two buttons are `P4-01-main-menu.md` req 16 and
    `P3-03-scoreboard-turn-indicator.md`; what either opens is `P4-04-settings.md` reqs 1–2.
    Whether the two routes render the same surface is Open Question 7 — if they do, the two
    `GoRoute`s build the same widget and nothing else changes.

### Into and out of a game

11. **The New Game name prompt's three transitions belong to this layer, and the prompt
    reports its outcome by calling forward, not by returning a value:** the open-games list
    calls `openNewGamePrompt()` (`push('/games/new')`); confirming calls `openGame(id)` with
    the id of the newly created game; cancelling calls `dismissCurrent()` and the list is
    still there beneath it.
    *Source: `Menus and UI.md` → Play Game → Where It Takes You ("Selecting New Game prompts
    for the opponent's name"); → Decisions → What does each row in the open-games list show?;
    → Screens (so far) → 3. New Game Name Prompt.*
    **Not `Future<String?>`, and not a dialog function.** The idiomatic dialog-shaped
    alternative — the prompt returning the entered name to whoever opened it — would wire
    `P4-02-open-games-list.md` reqs 10 and 12 backwards: those requirements read as the prompt
    *creating* the game and cancelling *costing nothing*, not as the list receiving a string
    and acting on it. Call-forward keeps the ownership those requirements already state, and
    the whole `show…` family outside `lib/navigation/` is banned by requirement 1's scan.
    *Testable, wave 2:* against the recording fake, a confirm records exactly one
    `openGame(id)` and no other call; a cancel records exactly one `dismissCurrent()` and no
    `openGame`. Against the real router, cancelling from `/games/new` leaves `/games`.
    *Wave note:* the prompt's contents and effects — the `ItSaMeMaRiO` default, the
    16-character limit, that confirming creates a game and cancelling creates nothing — are
    `P4-02-open-games-list.md` reqs 8–12, wave 4. Creating the record is
    `P1-04-persistence.md` req 21's `create`. Whether the prompt is drawn as a sheet over the
    list or as a full screen is Open Question 5 — a `pageBuilder` choice that leaves this
    requirement unchanged.

12. **Selecting an open game from the list opens the game screen on that game, identified by
    `GameId`, and it resumes the series rather than starting a new one.** The id travels as
    the `:gameId` path parameter of `/game/:gameId`.
    *Source: `Menus and UI.md` → Decisions → What does an open game hold? ("resuming a game
    from the open-games list resumes the *series*, not just the last individual board");
    → Play Game → Where It Takes You.*
    The id is opaque, store-minted and stable for life — `P1-04-persistence.md` req 22 — so
    this layer passes `id.value` into the path and never parses it, orders by it, or displays
    it.
    *Testable, wave 2:* `openGame(GameId('abc'))` leaves the location `/game/abc`, and the
    route's builder receives that id.
    *Wave note:* the row and its id are `P4-02-open-games-list.md` reqs 5 and 19; restoring
    board and score is `P1-04-persistence.md`.

13. **Leaving the open-games list without picking anything is an operation this layer owns**
    — `leaveOpenGamesList()`. That the affordance needs a routing operation is settled by the
    screen having one drawn; **where it leads is not** (Open Question 8).
    *Source: `P4-02-open-games-list.md` → Open Question 7 ("`1b` draws a back button; no
    design doc mentions one, or says where back goes"), which now names this requirement as
    the owner of that control while leaving its destination open.*
    It is named separately from `dismissCurrent()` because the two are the same call only if
    back from the list always unwinds one step, which is exactly what Open Question 8 asks. A
    call site must not have to know.
    *Testable, wave 2:* the operation exists and records one invocation against the fake. Its
    resulting location is deliberately unasserted until Open Question 8 lands.
    *Note the asymmetry with requirement 15, now that OQ 2 has landed:* the game exit is
    settled as `go` and this one is not. They are separate questions — `go` was chosen for the
    game exit on the strength of the back-swipe consequence, and the list has no equivalent
    consequence to weigh, because nothing is lost by swiping back into it.
    *And note the second asymmetry, with requirement 23:* the swipe is blocked on the game
    route and is **not** blocked here. Whether it should be is Open Question 17, which this
    requirement's answer does not decide either.

14. **Opening the in-game settings / quick-actions surface does not leave the game.** It is a
    **child route of `/game/:gameId`**, so the game screen stays mounted beneath it, and
    `dismissCurrent()` returns to that same game.
    *Source: `Menus and UI.md` → Settings Menu ("you can get to settings without abandoning a
    game. That second one is the important requirement: settings must be available mid-game");
    → How you reach settings from gameplay.*
    *Testable, wave 2:* from `/game/abc`, `openQuickActions()` leaves
    `/game/abc/quick-actions` with the game screen still in the tree; `dismissCurrent()`
    returns to `/game/abc` and the game screen is not rebuilt.
    *Wave note:* the board-level assertion — board, current player and scoreboard unchanged —
    is `P4-04-settings.md` req 2, wave 4.
    **One thing this does not settle:** what control invokes the dismissal (Open Question 9).
    What happens to a **pending move selection** is now settled and is requirement 20 — it is
    cleared, and precisely because nothing unmounts here, this layer has to do the clearing.
    Whether the surface is drawn as a sheet or a full screen is Open Question 10 — again a
    `pageBuilder` choice.
    **Requirement 23 does not reach this child route.** It blocks the gesture on
    `/game/:gameId`; a swipe on `/game/:gameId/quick-actions` would pop back to the board,
    which is what `dismissCurrent()` does anyway. Whether that should be blocked too is Open
    Question 17.

15. **`exitGameToMainMenu()` returns the player to the main menu with `router.go('/')`, and
    it has two callers.** Mid-play it is the quick-actions exit, available without finishing
    the game. At game over it is the result card's **back to main menu** control. One
    operation serves both; neither caller knows what it does underneath.
    *Source, mid-play: `Menus and UI.md` → Decisions → How do you get back to the main menu
    from a game? ("Via the settings button at the top right of the game screen. It opens quick
    actions, which include exiting the game. You don't have to finish a game to leave it");
    → How you reach settings from gameplay ("the settings button does double duty in-game").
    Source, game over: `Menus and UI.md` → Decisions → What controls does the game-over result
    card carry? — **next game, and back to main menu** — specified in
    `P3-04-game-over-rematch.md` req 5, which is cited rather than restated here.
    Source, the `go`-not-`pop` half: **settled by the user** — see Open Question 2. No design
    doc states it; `Menus and UI.md` → Open Questions asks it and leaves it open.*
    *Testable:* after `exitGameToMainMenu()` the location is `/`, from either caller, **and
    `canPop()` is false there** — the game route is gone from the stack rather than sitting
    beneath the menu.
    *Wave note:* the mid-play control is `P4-04-settings.md` reqs 4–5, wave 4; the game-over
    control is `P3-04-game-over-rematch.md` req 5, wave 3. The operation is identical for
    both — which is why **Open Question 2 resolved once and applies to both**, rather than
    being answerable differently for a finished game than for a live one. That is the
    interface earning its keep.
    **The one line is settled: `router.go('/')`.** It **replaces the stack**, so the game route
    is gone and **the iOS back-swipe cannot carry the player back into the game they just
    exited** — the consequence the user accepted when settling this, and it holds identically
    whether the game was abandoned mid-play or finished. `router.pop()` was the alternative and
    is not taken.
    **This is now one half of a settled pair, and the halves are independent.** Requirement 23
    blocks the swipe in the other direction — *out of* a live game — on an argument that has
    nothing to do with this one. Read requirement 23's asymmetry note before assuming either
    answer implied the other; it is also what makes this operation the **only** way off the
    game route rather than merely the intended one.
    *Still open:* whether the mid-play exit prompts for confirmation first is Open Question 6;
    the game-over exit has nothing to confirm, since the game is over and already saved.

16. **Leaving a game discards nothing.** No part of this layer ends, resets, deletes or
    finalizes a game on the way out.
    *Source: `Menus and UI.md` → Leaving a game mid-play ("going back to the main menu doesn't
    discard anything — the game stays in the open-games list with its own scoreboard, and you
    can pick it up again"); → Persistence (table: "Game in progress — Saved to device storage,
    resumable from the open-games list"); → Decisions → Does a game in progress have to be
    saved to device storage?; `Game Overview.md` → Decisions → Scoreboard lifetime. Corroborated
    at game over by `P3-04-game-over-rematch.md` req 5, whose back-to-main-menu control
    discards nothing because the finished game is already on disk by then.*
    *Testable, wave 2:* a source scan finds no call to a mutating `OpenGamesRepository`
    method — `create`, `save` or `delete` — anywhere in `lib/navigation/`. `count()` is the
    only store call this layer makes (requirement 8). The scan runs with no game screen built.
    **Requirement 22 is not an exception.** This layer *presents* the delete confirmation; the
    deletion itself is performed by `P4-02-open-games-list.md` through
    `P1-04-persistence.md`'s `delete`, and no `delete` call appears in `lib/navigation/`.
    **Requirement 20's clear is not an exception either.** A pending selection is UI state that
    is never persisted (`P3-02-move-input.md` req 21), so clearing it discards nothing stored.
    **Requirement 15's `go` is not an exception.** Replacing the stack drops a *route*, not a
    record: the game is on disk after every confirmed move (`P1-04-persistence.md` req 6) and
    is still in the open-games list afterwards.
    *Wave note:* the round-trip assertion — leave mid-board, reopen, board and score
    unchanged — is `P1-04-persistence.md` req 11's, and `P4-02-open-games-list.md` req 5
    asserts it from the list side.

17. **Taking the next game performs no navigation.** The series continues in the same open
    game rather than routing back to the open-games list or the main menu — the location stays
    `/game/:gameId`.
    *Source: `Menus and UI.md` → Game Over → Rematch ("The rematch continues in the **same
    open game** — same series, scoreboard intact. It does not start a second open game");
    `Game Overview.md` → Session Structure ("Continuing **resets the board**").*
    *Testable, wave 2:* against the recording fake, the next-game path records zero navigator
    invocations; against the real router the location is unchanged.
    *Wave note:* the control is `P3-04-game-over-rematch.md` req 5 — the *other* of the result
    card's two controls, and the one that does not touch this layer. Because it performs no
    navigation, requirement 20 does not fire on it; the clear there is
    `P3-02-move-input.md` req 30's `boardProvider` listener, which *does* fire, since
    `startNextGame()` replaces the board.
    *Note:* the docs settle this at the level of *which open game the series belongs to*;
    reading it as "no route change" is the narrow routing consequence, not a separate
    decision.

### Constraints on the graph

18. **No route reachable from a game leads to theme selection.** The theme cannot be changed
    mid-game, and the route table enforces it structurally: `/theme` is a child of `/`, not of
    `/game/:gameId`, so it is not reachable from inside a game without leaving it.
    *Source: `Theming.md` → Decisions → Can you change the theme mid-game ("**No** — leave it
    out for now. Theme changes happen from the main menu only"); `Menus and UI.md` → Theme
    Selection.*
    *Testable, wave 2:* `/theme` appears only as a child of `/` in the route table, and no
    call site under the game screen or its quick-actions surface invokes
    `openThemeSelection()`.
    *Wave note:* `P4-03-theme-selection.md` req 19 asserts the same constraint from the
    screen's side.

19. **The navigation layer holds no hardcoded theme values** — including no hardcoded
    `Duration(…)` for any transition, and no color on a non-opaque page's barrier — and passes
    the hardcoded-theme-value test with the baseline at zero.
    *Source: `Theming.md` → Architectural Rule ("All of our code operates off of the theme. No
    code should be operating independently from the selected theme"); `Tech Design.md` →
    Decisions → Do we add a test that fails on hardcoded theme values? ("Durations are in
    scope because … a hardcoded `Duration` is a theme value that escaped"; "the baseline
    starts at zero").*
    Note this bites here in a way it does not elsewhere: a transition page takes a
    `transitionDuration` and a barrier color, and both are theme values, not constants.
    `Theming.md` → What a Theme Controls lists modal and sheet surfaces among the theme's
    slots. *(Spacing and padding are **not** theme values — `Theming.md` → Decisions fixes
    them in code — but that changes nothing here, because this layer specifies no geometry at
    all. Durations and the barrier colour are unaffected by that decision.)*
    **Any such value is read from `activeThemeProvider`** (`lib/theme/theme_providers.dart`,
    `P1-03-theme-system.md`) — `ref.read` inside `GoRouterAppNavigator`, which is a service,
    and `ref.watch` inside a page builder's widget, per `P1-03` req 24. This layer defines no
    theme slot of its own; whether the slots it needs exist is `P1-03`'s.
    *Testable, wave 2:* the scan in `P1-05-theme-guard-test.md` passes over `lib/navigation/`
    with no baseline entries.
    Whether there is any transition motion to time at all is Open Question 14.
    **Requirement 23's page introduces no value to theme** — suppressing a gesture is
    behaviour, not appearance, and the page it needs carries no colour, radius or duration of
    its own beyond whatever the other pages already carry.

### State this layer must clear

20. **Every navigation clears the pending move selection, and this layer is what clears it.**
    Opening any menu or sheet — `/settings`, `/theme`, `/games`, `/about`,
    `/game/:id/quick-actions` — discards an unconfirmed selection, as does leaving the board
    by any route.
    *Source: `Game Board Design.md` → Decisions: **"Any tap outside the nine quadrants clears
    a pending, unconfirmed selection — including the legend/how-to-play strip, the scoreboard,
    the settings button, and opening any menu or sheet. One rule, uniformly applied."** It
    extends → Move Input → Changing your mind ("**Tap outside the full grid** → deselects
    entirely, clearing the pending move") to the surfaces that open over the board.*

    **`P3-02-move-input.md` req 30's `boardProvider` listener does not cover this case, and
    this is the point.** That listener fires when the *board* changes. Opening a surface over
    the board changes no board state, and requirement 2's child-route structure means the game
    screen is never unmounted and `pendingSelectionProvider` is never disposed. So the listener
    does not fire, nothing else disposes the state, and **the selection would survive** — the
    exact opposite of what the Decision says. Something has to clear it actively, and that
    something is here: a navigation is the one event this layer sees and `P3-02` does not.
    That PRD has since removed its own competing clear-on-navigation mechanism, leaving one
    owner for this path.

    ```dart
    // lib/navigation/go_router_app_navigator.dart — before every router call
    void _clearPendingSelection() =>
        _ref.read(pendingSelectionProvider.notifier).clear(); // P3-02 req 24
    ```

    **Clear on every operation, not on a subset.** A pending selection can only exist while a
    board is on screen, so clearing when there is none is a no-op — `clear()` sets an already
    null state to null. Making it unconditional means no operation can be added later that
    forgets to, which is what "one rule, uniformly applied" asks for — and requirements 21 and
    22 inherited it for free, which is the property working.
    **It calls `P3-02`'s published entry point and adds no writer.** `clear()` is already that
    provider's mutating surface for its tap-outside-the-grid case; this adds a caller, not a
    second owner.
    **Why the call cannot live in `P3-02` instead:** the board layer would have to observe the
    router to know a navigation happened, and requirement 1's scan forbids importing
    `go_router` outside `lib/navigation/`. Moving the observation there would breach the one
    boundary this PRD exists to hold.

    **"Every navigation" is now true on the game route, where it was previously aspirational.**
    This requirement guarantees the clear over *operations* — it runs before each
    `AppNavigator` call — while its heading claims *navigations*. Those two words coincide only
    where no surface can appear or disappear without an operation, and on the board they did
    not: the iOS back-swipe popped `/game/:gameId` through no operation at all, so
    `_clearPendingSelection()` never ran and the stale selection survived the player leaving
    the board — the exact outcome this requirement exists to prevent, reached by the one path
    it could not see. **Requirement 23 closes it**, by blocking the gesture on that route, so
    on the game route operations and navigations now coincide and the guarantee is literal.
    Elsewhere the gesture is still live and the gap between the two words is still real; it is
    harmless there only because a pending selection cannot exist off the board. Whether the
    other routes should be treated the same way is Open Question 17.

    *Testable, wave 3* (when `pendingSelectionProvider` exists): with a selection pending on
    `/game/abc`, each of `openQuickActions()`, `openSettings()`, `openThemeSelection()`,
    `exitGameToMainMenu()` and `playGame()` leaves `pendingSelectionProvider` null; and
    `dismissCurrent()` back to `/game/abc` finds it still null rather than restored.
    *Testable, wave 2:* against a fake pending-selection notifier, every `AppNavigator`
    operation records exactly one `clear()` before its router call.

### The About Us route

21. **`openAboutUs()` is an operation on `AppNavigator`, and it pushes `/about` as an ordinary
    opaque page, a child of `/`.** Same `Future<void>` shape as every other operation, and
    preceded by requirement 20's clear like every other operation.

    ```dart
    // lib/navigation/app_navigator.dart — appended to the interface in requirement 3
    /// The main menu's About Us button. Requirement 21.
    Future<void> openAboutUs();
    ```

    *Source: `Menus and UI.md` → Decisions, which settles that the main menu carries four
    buttons — Play Game, Theme, Settings, About Us — with About Us last and its position
    explicitly provisional (*"for now we might move it in the future"*);
    `P4-01-main-menu.md` req 23, which owns the button, states what it needs of this layer,
    and marks the name a proposal to this PRD rather than a fact.*
    **This PRD accepts that proposal as written** — the name, the `Future<void>` shape, and
    the opaque-child-of-`/` treatment.

    **Why opaque, and why under `/`.** Handoff screen `1c` is a full screen with its own back
    control, not a sheet and not an overlay, so it does not take the non-opaque treatment
    `/theme` gets under requirement 9 — nothing needs to stay painted behind it. And it is
    reached only from the main menu, so it belongs under `/` and not under `/game/:gameId`;
    requirement 18's structural argument applies here too, in that nothing in a game can reach
    it. Returning from it is `dismissCurrent()`, which requirement 5 already covers.
    *(The opaque/child-of-`/` reasoning is `P4-01` req 23's and this PRD's jointly; the handoff
    is a read-only reference asset, not a Decision.)*

    **The screen this route points at has no owner.** `P4-01-main-menu.md` owns the button and
    this requirement owns the route, but no PRD owns `AboutUsScreen` — its content, its back
    control, or whether the handoff's team photos are what ships. Recorded as Open Question 16
    rather than absorbed here.

    *Testable, wave 2:* `openAboutUs()` leaves the location `/about`; `/about` resolves as a
    child of `/`; `dismissCurrent()` from `/about` returns to `/` with the main menu still
    beneath. The route resolving does not require the screen widget to be more than a
    placeholder — which is exactly the wave-2 posture, and here it is load-bearing rather than
    incidental.

### The delete-confirmation route

22. **`openDeleteConfirmation(GameId id)` is an operation on `AppNavigator`, and it pushes
    `/games/confirm-delete/:gameId` as a **non-opaque** page, a child of `/games`.** Same
    `Future<void>` shape, same requirement 20 clear, dismissed by `dismissCurrent()` like every
    other surface.

    ```dart
    // lib/navigation/app_navigator.dart — appended to the interface in requirement 3
    /// The open-games list's delete confirmation, for one game. Requirement 22.
    Future<void> openDeleteConfirmation(GameId id);
    ```

    *Source: `Menus and UI.md` → Decisions → Deleting an open game settles that the list
    carries a delete action; `P4-02-open-games-list.md` req 28 owns the confirmation's
    contents and proposed this operation, this path and the widget name
    `DeleteGameConfirmation` as a fence while no host existed.*
    **This PRD accepts that proposal**, with one change and one addition.

    **The change: the id travels in the path.** `P4-02` proposed `/games/confirm-delete`; this
    publishes `/games/confirm-delete/:gameId`. A `go_router` location is meant to be sufficient
    to rebuild the screen — a route that needs an id but does not carry one cannot survive
    restoration, cannot be rebuilt from its location, and forces the id to be smuggled through
    state that requirement 1 keeps out of `lib/ui/` anyway. `/game/:gameId` already sets this
    precedent (requirement 12). The widget takes it as a constructor argument, exactly as
    `GameScreen` does.

    **The addition: non-opaque is settled here, not left to Open Question 10.** A confirmation
    must show what it is confirming against — the player is deciding about a specific row, and
    the row is behind the modal. This is not the settings-surface question OQ-10 holds open,
    where the handoff drew two things two ways; nothing draws this modal at all, and the
    argument for keeping the list visible is intrinsic. *(This PRD's call, with reason, and
    revisable if `P4-02` finds a reason to cover the list.)*

    **This layer presents and dismisses; it never deletes.** The confirmation's Yes path calls
    `P4-02-open-games-list.md`'s delete, which calls `P1-04-persistence.md` req 21's `delete`.
    No `delete` call appears in `lib/navigation/` — requirement 16's scan asserts exactly that.

    **Why a route was the right host, and what it cost.** This is the same
    transient-dismissible-surface-over-a-list pattern the name prompt already uses at
    `/games/new` (requirement 11), inside the same feature — so accepting it adds a row to the
    route table and no new concept. The cost is the one requirement 3 now names: the modal
    cannot report its outcome back to the list, which made a bullet in `P4-02` req 29
    unimplementable until that PRD reordered the flow. That reordering is the correct fix and
    it stands as the worked example.

    *Testable, wave 2:* `openDeleteConfirmation(GameId('abc'))` leaves the location
    `/games/confirm-delete/abc`; the route resolves as a child of `/games` and receives `abc`
    as a path parameter; the list widget is still mounted beneath it; `dismissCurrent()`
    returns to `/games`.

### The back-swipe on the game route

23. **The iOS back-swipe gesture is disabled on `/game/:gameId`. A player cannot swipe out of
    a game.** The only way off that route is the explicit exit control — requirement 15's
    `exitGameToMainMenu()`, from quick actions mid-play or from the result card at game over —
    which is also the only path that runs requirement 20's clear.
    *Source: **settled by the user.** No design doc states it: `Menus and UI.md` → Open
    Questions asks where each back affordance leads and whether the swipe can carry a player
    back *into* a game they exited, and never asks about swiping *out of* one. The standing
    principle the user reasoned from is `Game Board Design.md` → Decisions — **"One rule,
    uniformly applied"** — the same sentence requirement 20 cites for the clear.*

    **What made this necessary, because it is invisible in the route table.** `openGame` is
    `router.push('/game/${id.value}')` (requirement 3's mapping), so under Flutter's
    `CupertinoPageTransitionsBuilder` the edge-swipe pop is **live by default** on that route —
    nobody enabled it and nothing in this PRD mentioned it. A gesture pop goes through **no
    `AppNavigator` operation**: the router pops itself, `_clearPendingSelection()` never fires,
    and a pending, unconfirmed selection survives the player leaving the board. That is exactly
    the outcome requirement 20 exists to prevent, reached by the one route change requirement
    20 cannot observe. **Requirement 1's scans do not catch it either** — nothing imports
    `go_router` outside this layer and no widget calls anything, because the defect is the
    *absence* of a call.

    **The mechanism is a proposal; the property is the requirement.** The game route takes a
    `pageBuilder` returning a page that declines to be popped by the platform — a `PopScope`
    with `canPop: false` around `GameScreen` is the straightforward form, and requirement 2's
    snippet names it `NoBackGesturePage`. Any mechanism satisfying the testables below is
    acceptable. **What is not acceptable is the block living in `lib/ui/`:** the route's
    presentation is this layer's (requirement 1), and a `PopScope` placed inside the game
    screen widget would put a navigation decision back in a screen, where the next person to
    read that screen has no reason to expect one.

    **It is a property of the route, not of the game's state.** The block holds over a finished
    game as well as a live one, because `/game/:gameId` is the same route either way. That
    costs nothing: `P3-04-game-over-rematch.md` req 5's result card carries its own
    back-to-main-menu control, so a finished game already has an exit that does not depend on
    the gesture — and that PRD records the same point from its side.

    **The asymmetry with requirement 15 is deliberate, and the two halves were settled
    separately.** Stated together so neither is read as implying the other:
    - **Out of a live game — blocked, here.** The swipe cannot take a player off the board,
      because it would bypass the pending-selection clear.
    - **Back into an exited game — impossible, under requirement 15.** `router.go('/')`
      replaces the stack, so the game route is gone and a swipe on the main menu has nothing to
      return to. That was settled earlier (Open Question 2), on a completely different
      argument, and needed no gesture handling at all.

    Both directions are now closed, for different reasons. Neither answer produced the other,
    and neither would have been safe to infer from the other.

    **The block is not selective about its input.** Whatever suppresses the iOS edge-swipe on
    this route also suppresses the **Android system back** there, since both arrive as a route
    pop. That is consistent with the rule — one explicit way out — but it is a consequence
    rather than something the user was asked, and no design doc mentions the Android back
    button anywhere. Recorded, not decided; it is part of Open Question 17.

    *Testable, wave 2:* against the real router at `/game/abc`, a platform pop request
    (the back-gesture / system-back path) leaves the location `/game/abc` and pops nothing;
    `exitGameToMainMenu()` from that same location leaves `/` with `canPop()` false; the same
    pop request at `/games`, `/settings` and `/about` is **not** suppressed, so the block is
    demonstrably scoped to one route rather than installed app-wide; and a scan finds no
    `PopScope`, `WillPopScope` or `NavigatorPopHandler` outside `lib/navigation/`.
    *Testable, wave 3* (when `pendingSelectionProvider` exists): with a selection pending on
    `/game/abc`, a pop request leaves both the location and the pending selection unchanged.
    That is the assertion that ties this requirement to requirement 20's guarantee rather than
    testing a gesture for its own sake.
    *Wave note:* the game screen is `P3-01-board-rendering.md` and the pending selection is
    `P3-02-move-input.md` req 24; neither has to change for this, and neither may implement it.

## Out of Scope

Referenced by filename rather than specified here. This PRD moves between these surfaces and
specifies none of them:

- **The main menu** — its buttons, title, logo and styling → `P4-01-main-menu.md`, including
  the About Us button that calls requirement 21.
- **The open-games list, the name prompt's contents, and the delete flow's contents** — rows,
  the delete affordance and its reveal, the cap, the `ItSaMeMaRiO` default, the character
  limit, the confirmation's copy and buttons, and the deletion itself →
  `P4-02-open-games-list.md`, with the storage half in `P1-04-persistence.md`. Requirements
  11, 13 and 22 claim the *transitions* only.
- **The theme selection overlay** — its rows, highlight, labels and failure modal →
  `P4-03-theme-selection.md`.
- **Settings and the in-game quick-actions surface** — the three toggles, what quick actions
  contains, and the exit control's own presentation → `P4-04-settings.md`.
- **The game screen** → `P3-01-board-rendering.md`. **The pending selection itself** — what it
  is, how a tap creates one, and every non-navigation way it clears → `P3-02-move-input.md`.
  Requirement 20 calls that PRD's `clear()`; it defines no selection state of its own, and
  requirement 23's gesture block lives in this layer's `pageBuilder` rather than in either
  screen.
- **The game-over result card** — that it carries two controls, what they read, how it is
  presented over the board, and whether it can be dismissed → `P3-04-game-over-rematch.md`
  req 5. Requirement 15 owns only what its back-to-main-menu control calls; requirement 17
  records that its other control calls nothing here; requirement 23 covers the card only in
  the sense that it sits inside the game route.
- **Storing, capping, creating, deleting and restoring open games, and minting `GameId`** →
  `P1-04-persistence.md`. This layer calls `count()` and carries ids; it writes nothing.
- **Crash reporting, and any decision about whether recovered errors are reported** →
  `P1-06-crash-reporting.md`, whose req 1 scopes its wave to unhandled errors and whose OQ-4
  holds the recovered-error question open. Requirement 8 recovers and reports nothing; it
  installs no handler, holds no sink, and invents no report path.
- **The theme object and its slots** → `P1-03-theme-system.md`. Requirement 19 reads
  `activeThemeProvider`; it defines nothing in it.
- **Deep links and the URL bar.** `go_router` was chosen partly because it *"handles deep
  links and the browser URL bar without rework"* (`Tech Design.md` → Decisions → Navigation
  approach — go_router), and the route table above is therefore link-shaped. But no design doc
  asks for an external entry point, the app is otherwise fully offline, and **no URL scheme,
  universal link or iOS associated-domain configuration is specified here.** The capability is
  retained; nothing is wired to it.
- **The purchase flow and its host surface** → `P4-05-purchase-flow.md`. `Menus and UI.md` →
  Decisions → *Where the open-game slot unlock is sold* settles that a buying surface exists
  and that *"which screen it lives on is not decided"*; its Open Questions name the open-games
  list at the cap, the settings screen, or **a dedicated store surface** as candidates. Under
  the third that is a route this table does not carry, and a global *Restore purchases*
  affordance may be another. No operation and no `GoRoute` for either is published here.
- **A fuller Rules / How-to-Play screen.** `P3-05-how-to-play.md` owns the on-board legend and
  hint, which need no route — and its req 15 takes the same clearing rule from the strip's
  side. `Menus and UI.md` → Open Questions holds open *"Is there also a fuller Rules/How-to-Play
  screen"*; if one appears it is another route, and none is published here.
- **Screen transition animations.** `Animations.md` → Scope For Now: *"We are **not**
  animating the board, the layout, or transitions between screens yet."* Requirement 19
  constrains any motion value that is nonetheless introduced; it does not authorize one. See
  Open Question 14.
- **A confirmation prompt on exiting a game.** Unsettled — Open Question 6. Nothing here
  designs one and nothing here rules one out. Note this is untouched by Open Question 2's
  answer: *where* the exit lands is settled; whether it asks first is not. It is untouched by
  requirement 23 too: blocking the gesture decides that the exit control is the only way out,
  not what that control asks first.
- **`Alternative Game Styles.md`** — declared parking lot; not what is being built.

## Open Questions

### From the design docs — unresolved, worded as the docs word them

1. **The routing approach — CLOSED.** `Tech Design.md` → Decisions → *Navigation approach —
   go_router* settles it: **`go_router`**, chosen as a long-term fit rather than a stopgap.
   Requirements 1–5 are written against it, and the interface in requirement 3 did not change
   when the answer landed. The former proposal to narrow this PRD's wave-2 deliverable to the
   interface and the scans is **withdrawn** — the body is buildable, so the full layer ships in
   wave 2. Kept as a numbered stub so the citations in sibling PRDs stay stable.

2. **Pop or `go` on exit — CLOSED by the user: `router.go('/')`.**
   `Menus and UI.md` → Open Questions:

   > … does exiting a game pop back to an existing main menu instance or push a fresh one?

   In `go_router` terms, `exitGameToMainMenu()` was either:
   - **`router.go('/')`** — replaces the stack, so the game route is gone and the **iOS
     back-swipe cannot carry the player back into the game they just exited**; or
   - **`router.pop()`** — unwinds one step to the menu route already beneath, leaving the game
     route in the stack until it is popped, so the swipe **can** return them.

   **The user chose `router.go('/')`, and accepted the consequence explicitly: the game route
   is gone, so the iOS back-swipe cannot carry a player back into a game they just exited.**
   `router.pop()` is not taken.

   It governs **both** the mid-play exit and the game-over card's back-to-main-menu control,
   since both call the same operation — so the swipe behaves identically whether the game was
   abandoned or finished, which was worth stating rather than discovering, and is what the one
   operation bought.

   **What this changes here:** requirement 3's mapping table reads `router.go('/')` and
   "settled" rather than "OQ2"; requirement 15 states the call, its testable now also asserts
   `canPop()` is false at `/`, and requirement 16 records that replacing the stack drops a
   route rather than a record. **What it changes elsewhere:** `P3-04-game-over-rematch.md`
   req 5 and `P4-04-settings.md` req 19 are the two call sites and neither has to change — that
   is the point of them calling an operation. Open Question 3's swipe half follows from this
   and is now answered with it. Kept as a numbered stub because requirements 3, 13, 15 and 23
   and Open Question 3 all reference this number.

   **Owed to the docs:** `Menus and UI.md` → Open Questions still asks this, and its
   back-affordance question still asks whether the swipe can carry a player back into a game
   they exited. Both are now answered. That doc edit is `forge-doc-writer`'s.

3. **Where each back affordance leads — the in-game half and both swipe halves are CLOSED; the
   list's back control is not.** `Menus and UI.md` → Open Questions:

   > **Where does each back affordance lead** — the in-game back/exit action, and the iOS
   > back-swipe gesture — and can the swipe gesture carry a player back into a game they just
   > exited?

   Open Question 2 was the in-game half and it is answered: the exit is `router.go('/')`. The
   swipe half followed from it for the direction the doc asks about — under `go_router` the
   gesture pops whatever is on the stack, so **the answer to the doc's last clause is no: the
   swipe cannot carry a player back into a game they just exited.**

   **The direction the doc does not ask about is now also settled, and separately.**
   Requirement 23 disables the swipe *out of* a live game, on the user's settlement: a gesture
   pop runs through no operation, so it would skip requirement 20's clear. That did **not**
   follow from Open Question 2 — it is a different argument about a different direction, and it
   is worth recording that this question's framing ("the answer is decided by what each
   operation leaves on the stack") turned out to be true of one direction only. A gesture is
   not always an operation's shadow.

   **What remains under this heading** is the *other* back affordance — the open-games list's
   back control — which is Open Question 8 and is still open. Answering it the other way would
   not disturb anything settled here. Whether the swipe is blocked anywhere else is Open
   Question 17.

4. **Does the empty-state path show the name prompt?** `Menus and UI.md` → Play Game → Where
   It Takes You:

   > Undecided: whether the empty-state path (no open games → straight into a new game) also
   > shows the opponent-name prompt, or skips it. "No intermediate screen" and the prompt
   > can't both be true on that path.

   Concretely: with `count() == 0`, does `playGame()` push `/games/new` or `/game/<id>`?
   Requirement 7 stands either way. This is the same question as `P4-02-open-games-list.md` →
   Open Question 1, and it decides whether `openNewGamePrompt()` has one caller or two.

5. **Is the name prompt its own screen or an overlay?** `Menus and UI.md` → Screens (so far)
   → 3. New Game Name Prompt: *"Undecided whether it's its own screen or an overlay."*
   Now a `pageBuilder` choice on the `/games/new` route — non-opaque leaves the list visible
   beneath, opaque covers it. The route, the operation and every call site read the same
   either way. (Requirement 22 settles the *delete* modal as non-opaque on its own argument;
   that does not decide this one.)

6. **Does leaving a game still need a confirmation prompt?** `Menus and UI.md` → Leaving a
   game mid-play:

   > Whether leaving still needs a confirmation prompt is undecided; the original reason for
   > one ("Leave game? Your score will be lost") no longer applies.

   This is the mid-play exit only. The game-over card's exit has nothing to confirm.
   **Unaffected by Open Question 2's answer** — that settled where the exit lands, not whether
   anything is asked before it — and unaffected by requirement 23, which settles that the exit
   control is the only way out, not what it asks on the way.

7. **Is quick actions the same settings screen as the main menu's?** `Menus and UI.md` → How
   you reach settings from gameplay:

   > Undecided: whether quick actions is the *same* settings screen as the main menu's, or a
   > trimmed-down in-game version with the exit option added.

   Requirement 10 settles that there are two entry points and two routes; whether the two
   `GoRoute`s build the same widget is what remains. Also carried by `P4-04-settings.md` →
   Open Question 1.

### Raised by PRD review across the existing PRDs — carried here, not answered

8. **Where does back from the open-games list lead?** `P4-02-open-games-list.md` → Open
   Question 7: *"How does the player leave the list without picking anything? `1b` draws a
   back button; no design doc mentions one, or says where back goes."* Requirement 13 settles
   that the operation exists — and that PRD now names it — but what remains is `router.pop()`,
   unwinding one step, which is the main menu whenever the list was reached from it, versus
   `router.go('/')`, which returns to the menu from anywhere the list might later be reached
   from. The two differ only once a second path into the list exists.
   **Open Question 2's answer does not decide this one.** The game exit took `go` on the
   strength of a consequence this control does not have — there is nothing behind the list a
   back-swipe could strand a player in — so the argument does not transfer, and this is still
   the user's call.

9. **No control is named for returning from the in-game settings surface to the game.**
   `P4-04-settings.md` records that its req 2 settles that reaching settings does not abandon
   the game, *"but no doc names the control that returns you to it. The handoff gives `1f` a
   close button and a 'Back to the game' action; the docs give it neither."* Requirements 5
   and 14 have the same hole: the operation is published and implemented, its trigger is not.

10. **Is a modal or sheet drawn opaque or non-opaque?** The approved handoff draws `2b —
    Settings page` as *"Full screen, not a sheet — this is the main-menu route; 1f stays the
    trimmed in-game version"*, and draws `1f` as a bottom sheet. `P4-04-settings.md` → Open
    Question 1 holds this unresolved. Under `go_router` it no longer changes the route table —
    `/settings`, `/games/new` and `/game/:gameId/quick-actions` are routes either way — it
    changes each one's `pageBuilder`, and therefore whether what is beneath stays painted.
    Requirements 9, 21 and 22 settle it for theme selection, About Us and the delete
    confirmation, because each of those has an argument of its own; the other three do not.

11. **The pending selection when a surface opens over the board — CLOSED, and it does not go
    the way this PRD expected.** `Game Board Design.md` → Decisions settles it: *"Any tap
    outside the nine quadrants clears a pending, unconfirmed selection — including the
    legend/how-to-play strip, the scoreboard, the settings button, and opening any menu or
    sheet. One rule, uniformly applied."* It is **cleared**, not preserved. This PRD had
    observed that the child-route structure made *preserved* the path of least resistance;
    that was right about the mechanics and wrong about the outcome, which is why requirement 20
    exists — nothing unmounts, so nothing clears it by accident. `P3-02-move-input.md` OQ-1,
    `P3-05-how-to-play.md` req 15 and `P4-04-settings.md` OQ-5 land on the same answer. Kept as
    a numbered stub so sibling citations stay stable.
    **One path escaped that rule and has since been closed:** the back-swipe off the board went
    through no operation, so nothing cleared the selection. Requirement 23 blocks it.

12. **The game-over exit — CLOSED as it bore on this layer; a smaller half remains
    elsewhere.** This PRD asked whether the settings button stays live over a finished game,
    because if it did not, requirement 15 was the *only* settled way out and a player could be
    stranded on a finished board. That is answered: `Menus and UI.md` → Decisions → *What
    controls does the game-over result card carry?* settles **next game, and back to main
    menu**, and `P3-04-game-over-rematch.md` req 5 specifies the card — cited here, not
    restated. The card is self-sufficient, so no player depends on the settings button to leave
    a finished game, and requirement 15 now has that control as a second caller.
    **Still open, and not this layer's:** whether the top-right settings button renders and
    responds while the card is on screen. It is a presentation question for
    `P3-04-game-over-rematch.md` and `P3-03-scoreboard-turn-indicator.md`, and it no longer
    strands anyone whichever way it goes.

13. **Does anything render before the main menu?** Requirement 6 makes `/` the initial
    location, and nobody has ruled out two things that would precede it: the iOS launch screen
    the platform shows before the first frame, and any gate held while the persisted theme is
    materialized — `Theming.md` → Why this matters for the build says materialization happens
    *"at startup"*, and `Tech Design.md` → Open Questions → *2. Theme loading* leaves open how
    many themes that covers. Whether a splash, a loading state, or nothing at all precedes the
    menu is unstated. (`go_router` would express a gate as a `redirect`; none is specified
    here.)

14. **Do screen transitions animate at all, and does the Animations toggle apply to them?**
    `Animations.md` → Scope For Now says transitions between screens are not animated *yet*,
    while → Decisions → *Turn animations off — a global setting* and → *Animations off =
    instant state change* describe a toggle that governs everything the game animates. This
    now has a concrete surface: every transition page in requirement 2 takes a
    `transitionDuration`, and requirement 19 says any such value is a theme value. Whether
    those durations are zero, theme-supplied, or gated on the toggle is unaddressed. (Unchanged
    by `Theming.md` → Decisions fixing spacing and padding in code — those are geometry, these
    are motion.)

15. **What does the player see when the open-game count cannot be read?** *(Author-raised —
    no design doc addresses it.)* Requirement 8 recovers: nothing is pushed and the player
    stays on the main menu, which from their side means **tapping Play Game appears to do
    nothing** — the one outcome `Game Board Design.md` → Taps outside the legal quadrant
    reserves for taps that are *deliberately* inert. A message, a retry affordance, or
    accepting the silence are all consistent with what is written today. This is the sibling of
    `P1-06-crash-reporting.md` → OQ-4, which asks whether such a recovered error is reported at
    all; this one asks what, if anything, is shown.

16. **The About Us screen has no owner, and its content is unspecified.** *(Appended with
    requirement 21 — recorded, not resolved.)* `Menus and UI.md` → Decisions settles that the
    button ships; `P4-01-main-menu.md` owns the button; requirement 21 owns the route. Nobody
    owns `AboutUsScreen` — not its copy, not its back control, not whether the team photos the
    handoff draws are what ships, and `P5-02-asset-generation-replicate.md` records that real
    team photos are probably not an asset-generation question at all. **The precedent is the
    turn banner**, which four PRDs each deferred to another until none accepted it and it went
    unbuilt until the user ruled. This layer will route to a screen that does not exist unless
    a PRD claims it.

17. **Does any other route block the back-swipe, or is this game-route-only?** *(Appended with
    requirement 23 — recorded, not resolved. The user settled the game route and said nothing
    about the rest, and no design doc mentions the gesture except in the direction Open
    Question 3 quotes.)* Requirement 23's argument is specific to the board: a gesture pop
    skips requirement 20's clear, and a pending selection only exists on the board. **That
    argument transfers to no other route**, which is why nothing else is blocked — but "no
    argument to block it" is not the same as "settled that it stays live," and three groups are
    currently unstated:
    - **The child route over the game** — `/game/:gameId/quick-actions`. A swipe there pops
      back to the board, which is what `dismissCurrent()` does anyway, so the outcome is
      benign; it just happens without an operation.
    - **The transient surfaces over something else** — `/games/new`,
      `/games/confirm-delete/:gameId`, `/theme`. Same shape: a swipe dismisses them, matching
      `dismissCurrent()`.
    - **The ordinary screens** — `/games`, `/settings`, `/about`. A swipe unwinds one step,
      which is `router.pop()`, and for the list that is one of the two answers Open Question 8
      is still choosing between — so a live gesture there quietly implements one side of an
      open question.

    The question the docs do not answer: is *"you leave a surface by its own control"* a rule
    of this app, or is it specifically that you may not leave **a game** by accident?
    **A second half arrives with the same mechanism: Android's system back.** Whatever
    suppresses the swipe suppresses it too (requirement 23), and no design doc mentions the
    Android back button on any screen — not on the game route, where it is now blocked as a
    side effect, and not anywhere else. Neither half is decided here.

### Recorded as closed — kept so they are not re-raised

- **The routing approach.** Settled — `go_router`. See Open Question 1's stub.
- **Where the game exit lands, and whether the back-swipe can return to a game.** Settled by
  the user — `router.go('/')`, replacing the stack, so the swipe **cannot**. See Open
  Question 2's stub, Open Question 3, and requirement 15. It applies to both callers because
  both call one operation.
- **Whether the back-swipe can carry a player *out of* a live game.** Settled by the user —
  **no**, requirement 23 disables the gesture on `/game/:gameId`. Separate settlement, separate
  argument: it exists to stop a gesture pop bypassing requirement 20's clear, not because of
  anything about the stack. The two directions are now both closed and neither implied the
  other. **Whether any other route gets the same treatment is Open Question 17 and is open.**
- **The pending selection across a navigation.** Settled — cleared, uniformly. See Open
  Question 11's stub and requirement 20. `P3-02` has removed its competing mechanism, so this
  path has one owner, and requirement 23 closes the one path that bypassed it.
- **How a player leaves a finished game.** Settled — the result card's own back-to-main-menu
  control, calling requirement 15's operation. See Open Question 12, and
  `P3-04-game-over-rematch.md` req 5 for the card. Requirement 23 makes that the only way out
  of the route rather than merely the intended one.
- **Where the delete confirmation lives.** Settled — requirement 22's
  `openDeleteConfirmation(GameId)` and `/games/confirm-delete/:gameId`, non-opaque, dismissed
  by `dismissCurrent()`. `P4-02-open-games-list.md` req 28's fence becomes a citation.
- **Whether the presentation guard is a deny-list.** Settled — it is not. Requirement 1's
  second scan bans the `show[A-Z]…` family by shape, after the name-based version was shown to
  miss `showGeneralDialog` and `showAdaptiveDialog`.
- **Where a failed count read gets reported.** Settled for this wave by scope, not by
  preference: it is **not** reported, because `P1-06-crash-reporting.md` covers unhandled
  errors only and publishes no reporting API for application code. Requirement 8 states this
  and points at that PRD's OQ-4 as the question that would change it.
- **How About Us is reached.** Settled — requirement 21's `openAboutUs()` and `/about`,
  accepting `P4-01-main-menu.md` req 23's proposal as written. What that route *renders* is
  Open Question 16 and is a different question.
- **The router dependency.** `go_router` must join `P1-01-app-scaffold.md` req 14's exhaustive
  dependency list. `Tech Design.md` names this consequence itself; it is routed separately and
  is not an open question.
- **What wave P2 builds against.** Settled by the posture in this PRD's header and the
  per-requirement *Wave note* lines: the deliverable is the layer, its interface, its router
  configuration, its seam and the scans; screen-level assertions are owned by the named P3/P4
  requirements and run in their waves. Requirement 20 is the one requirement whose full
  assertion waits on wave 3, and it says so — as does requirement 23's second testable, for the
  same reason and on the same provider.
- **Where the layer lives.** Settled — requirement 2. `P1-01-app-scaffold.md` req 2 creates
  `lib/navigation/` with a `.gitkeep` and states that its contents are this PRD's.
- **The game id.** Settled by `P1-04-persistence.md` req 22 and recorded in its Open
  Question 6a; requirement 3 is written against `GameId` today.
- **The theme accessor.** Settled by `P1-03-theme-system.md` — `activeThemeProvider` in
  `lib/theme/theme_providers.dart`, `read` in services and `watch` in widgets per its req 24.
  Requirement 19 names it.
