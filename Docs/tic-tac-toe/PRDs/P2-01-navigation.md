# PRD: Navigation and the Back Stack

> **Status:** Draft · Source docs read: `Menus and UI.md`, `Tech Design.md`,
> `Game Overview.md`, `Game Board Design.md`, `Theming.md`, `Animations.md`, `Rules.md`,
> `roadmap.md`, plus the read-only reference asset `design_handoff_game_ui/README.md`.
> `Alternative Game Styles.md` is a declared parking-lot doc and was not sourced from.

**Wave:** P2 · **File:** `P2-01-navigation.md`

**Depends on:** `P1-01-app-scaffold.md` — `app.dart`, the layer-first `lib/` tree
(including `lib/navigation/`, see Requirement 2 and Open Question 16) and the Riverpod
root this layer is installed into.

**Depended on by:** every screen PRD. Each owns a destination this layer moves between and
specifies its own contents: `P3-01-board-rendering.md`, `P3-04-game-over-rematch.md`,
`P4-01-main-menu.md`, `P4-02-open-games-list.md`, `P4-03-theme-selection.md`,
`P4-04-settings.md`. `P4-05-purchase-flow.md` may become a seventh — see Out of Scope.

---

## Problem

Nothing owns the movement between screens. Every screen PRD specifies its own contents and
then hands off by filename — main menu → open-games list → game screen → settings → game
over — but no PRD, and no Decision in any design doc, says how a player gets from one to
the next or back again. `Tech Design.md` → Decisions → *Navigation* states this outright:
*"No Decision above names a routing approach, and the dependency list has no router in it
yet."* `Menus and UI.md` → Decisions → *Navigation and the back stack* states the same for
the flows: *"No screen flow in this doc currently says what 'back' does anywhere."*

The cost is already visible in the other PRDs. `P4-02-open-games-list.md` → Open Question 7
records that the approved drawing `1b` has a back button no design doc mentions and nothing
says where it leads. `P4-04-settings.md` settles that reaching settings mid-game must not
abandon the game, but its Open Questions record that no doc names the control that returns
you to it. `P3-04-game-over-rematch.md` → OQ3 records that nothing says whether the
top-right settings button — the settled way out of a game — is still live once the result
is on screen. Three PRDs each assume someone else owns the back stack, and today nobody
does. A fourth consequence is quieter: `P4-02-open-games-list.md` specifies the name
prompt's own comings and goings (its Requirements 8, 10 and 12), which are screen changes
with no routing owner. Requirement 8 below claims them.

## Goal

The app has one explicit navigation layer, in one known place, exposing one named operation
per transition, and every screen change goes through it. The flows the design docs already
settle work end to end: the app launches on the main menu, Play Game reaches either a new
game or the list of open ones, the theme overlay opens on top of a main menu that stays
mounted, settings is reachable from both the main menu and mid-game without abandoning the
game, and exiting a game from the in-game quick actions lands the player back on the main
menu with the game intact and resumable. **How** that layer is built — plain `Navigator`,
`go_router`, or something else — and what every back affordance does are deliberately not
decided here; they are recorded in Open Questions as the docs word them. Requirement 3 is
written so that answer can land later without changing a single call site.

## Requirements

Each requirement names the screens it moves between by filename. None specifies what a
screen contains.

### The layer itself

1. **The app has one explicit navigation layer, and every screen change goes through it**
   rather than being performed ad hoc inside a screen widget.
   *Source: `Tech Design.md` → Decisions → Navigation ("The app has an explicit navigation
   layer, and it is now in scope"); `Menus and UI.md` → Decisions → Navigation and the back
   stack ("The app has a defined navigation model — this is now in scope to build out").*
   *Testable:* a source scan finds no `Navigator.` call, no route construction and no route
   name outside `lib/navigation/` — in particular none under `lib/ui/`. That assertion holds
   whichever approach Open Question 1 resolves to.

2. **The layer lives in `lib/navigation/`.**
   *Source: `Tech Design.md` → Decisions → Project structure — layer-first, whose tree now
   carries `navigation/   ← the app's routing layer`, and whose accompanying paragraph:
   "`navigation/` is a new layer, for the same reason `storage/` was added above …  It is
   Flutter-side, same as `ui/` and `state/` — nothing here changes the `engine/` purity
   rule. What goes inside it is not decided; the routing approach is still open."*
   The directory is created by `P1-01-app-scaffold.md`, which does not yet list it — see
   Open Question 16.

3. **The layer exposes one named operation per transition this PRD settles, and screens
   invoke operations rather than routes.** A screen calls `exitGameToMainMenu()`; it does
   not push, pop, name a route, or know what the layer does underneath. This is the contract
   the six screen PRDs code against, and it is deliberately separable from the routing
   approach: every operation below is expressible under plain `Navigator`, under `go_router`,
   or under anything else Open Question 1 might land on.

   | Operation | The transition it performs | Settled by |
   |---|---|---|
   | `openMainMenu()` | presents the main menu as the app's first screen | R4 |
   | `playGame()` | the Play Game branch — the layer picks the destination, the caller does not | R5 |
   | `openThemeSelection()` | the theme overlay, over a still-mounted main menu | R6 |
   | `openSettings()` | the main menu's settings entry point | R7 |
   | `openQuickActions()` | the in-game settings entry point | R7, R10 |
   | `openNewGamePrompt()` | the open-games list → the opponent-name prompt | R8 |
   | `openGame(gameId)` | the game screen for one open game, newly created or resumed | R8, R9 |
   | `exitGameToMainMenu()` | the quick-actions exit | R11 |
   | `dismissCurrent()` | closes the surface on top and returns to what is beneath it | R6, R8, R10 |

   *Testable:* every screen change in the app is a call to one of these, and the scan in
   Requirement 1 finds no other means of changing screens under `lib/ui/`.

   **Three things this table does not settle.** Whether `openSettings()` and
   `openQuickActions()` resolve to the same surface follows Open Question 7 — two operations
   are named because there are two settled entry points, not because there are certainly two
   surfaces. What *invokes* `dismissCurrent()` on the in-game surface is unnamed in every doc
   (Open Question 9), but the operation must exist regardless, because Requirement 10 requires
   the return trip to work. And whether `dismissCurrent()` pops a route or hides an overlay is
   Open Question 10.

   **The operation names are this PRD's, not the design docs'.** No doc names an API. The
   *set* is derived from the settled transitions and each row cites the requirement that
   settles it; the identifiers are a proposal, and renaming any of them is free so long as the
   set stays one operation per settled transition.

### Launch

4. **The main menu is the app's launch screen** — the first screen the app presents, with
   nothing beneath it in the stack.
   *Source: `Menus and UI.md` → Decisions → Navigation and the back stack ("The main menu
   being the app's launch screen is assumed throughout this doc … Recording it here since
   nothing contradicts it"); → Screens (so far) → 1. Main Menu.*
   *Testable:* after a cold launch the main menu (`P4-01-main-menu.md`) is the screen on
   display and the back stack holds nothing under it.
   *Not settled:* whether anything renders *before* it — an iOS launch image, or a gate while
   the persisted theme is materialized. See Open Question 13; this requirement is about the
   first screen of the app, not the first pixels on the display.

### Out of the main menu

5. **Play Game branches on whether stored open games exist: with none, the player goes
   straight into a new game and the open-games list is not shown; with one or more, the
   open-games list opens.** The branch is evaluated inside the layer, so callers of
   `playGame()` do not test the count themselves.
   *Source: `Menus and UI.md` → Play Game → Where It Takes You ("No open games — straight
   into a new game, no intermediate screen"; "Open games exist — a new screen listing all open
   games"); → Decisions → Is the main menu button "New Game" or "Play Game"?*
   *Testable:* with zero stored open games, `playGame()` never renders the list destination;
   with one or more, it does.
   The count comes from `P1-04-persistence.md`; the list screen is
   `P4-02-open-games-list.md`'s. Whether the **name prompt** appears on the empty path is
   unresolved — Open Question 4 — so this must not be read as settling it either way.

6. **The Theme button opens theme selection as an overlay on the main menu, with the main
   menu still mounted beneath it.** It is not a screen the menu is replaced by.
   *Source: `Menus and UI.md` → Decisions → Is theme selection its own screen or an overlay?
   ("**An overlay** on the main menu"); → Screens (so far) → 5; `Theming.md` → Decisions →
   Where theme selection lives.*
   *Testable:* while the overlay is open the main menu is still mounted and visible behind it;
   `dismissCurrent()` reveals that same menu rather than constructing a new one.
   The overlay's contents are `P4-03-theme-selection.md`'s.

7. **Settings is reachable from exactly two entry points — the main menu's Settings button
   and the game screen's top-right button — and from nowhere else.**
   *Source: `Menus and UI.md` → Settings Menu ("Reachable from two places: 1. The **main
   menu** (Settings button). 2. The **gameplay screen**"); → Screens (so far) → 6;
   `Game Board Design.md` → Scoreboard.*
   What either entry point opens is `P4-04-settings.md`'s; whether the two are the same
   surface is unresolved there and here — Open Question 7.

### Into and out of a game

8. **The New Game name prompt's three transitions belong to this layer:** the open-games list
   opens the prompt; confirming it opens the game screen on the newly created game;
   cancelling it returns to the open-games list, which is still there.
   *Source: `Menus and UI.md` → Play Game → Where It Takes You ("Selecting New Game prompts
   for the opponent's name"); → Decisions → What does each row in the open-games list show?;
   → Screens (so far) → 3. New Game Name Prompt.*
   *Testable:* selecting New Game renders the prompt and opens no game; confirming opens the
   game screen exactly once; cancelling leaves the list on screen.
   `P4-02-open-games-list.md` Requirements 8, 10 and 12 specify the prompt's *contents and
   effects* — the `ItSaMeMaRiO` default, the 16-character limit, that confirming creates a
   game and cancelling creates nothing. This requirement claims only the screen changes those
   sentences imply, which previously belonged to nobody's routing graph. Creating the game is
   `P1-04-persistence.md`'s; whether the prompt is its own screen or an overlay is Open
   Question 5, and this requirement reads the same either way.

9. **Selecting an open game from the list opens the game screen on that game, and it resumes
   the series rather than starting a new one.**
   *Source: `Menus and UI.md` → Decisions → What does an open game hold? ("resuming a game
   from the open-games list resumes the *series*, not just the last individual board");
   → Play Game → Where It Takes You.*
   Restoring board and score is `P1-04-persistence.md`'s and `P4-02-open-games-list.md`'s;
   this covers only that the list's destination is the game screen
   (`P3-01-board-rendering.md`), reached with the selected game's identity.

10. **Opening the in-game settings / quick-actions surface does not leave the game.** The game
    is still there when the surface is dismissed, and `dismissCurrent()` returns to that same
    game.
    *Source: `Menus and UI.md` → Settings Menu ("you can get to settings without abandoning a
    game. That second one is the important requirement: settings must be available mid-game");
    → How you reach settings from gameplay.*
    *Testable:* open the surface mid-game, dismiss it, and the same game is on screen with its
    board, its current player and its scoreboard unchanged.
    **Two things this does not settle:** what control invokes the dismissal (Open Question 9)
    and what happens to a pending move selection while the surface is up (Open Question 11).

11. **Exiting the game from quick actions returns the player to the main menu, and it is
    available without finishing the game.**
    *Source: `Menus and UI.md` → Decisions → How do you get back to the main menu from a game?
    ("Via the settings button at the top right of the game screen. It opens quick actions,
    which include exiting the game. You don't have to finish a game to leave it"); → How you
    reach settings from gameplay ("the settings button does double duty in-game: it's both the
    settings entry point and the way out of a game").*
    *Testable:* from a game in progress, `exitGameToMainMenu()` leaves the main menu as the
    screen on display.
    *Not settled:* whether it **pops** to an existing main-menu route or **pushes** a fresh one
    (Open Question 2), and whether it prompts for confirmation first (Open Question 6).

12. **Leaving a game discards nothing.** No part of this layer ends, resets, deletes or
    finalizes a game on the way out; the game stays in the open-games list with its own
    scoreboard and is resumable.
    *Source: `Menus and UI.md` → Leaving a game mid-play ("going back to the main menu doesn't
    discard anything — the game stays in the open-games list with its own scoreboard, and you
    can pick it up again"); → Persistence (table: "Game in progress — Saved to device storage,
    resumable from the open-games list"); → Decisions → Does a game in progress have to be
    saved to device storage?; `Game Overview.md` → Decisions → Scoreboard lifetime.*
    *Testable:* exit a game mid-board with a non-zero score, reopen it from the list, and the
    board and its running series score are unchanged.

13. **Taking the rematch performs no navigation.** The series continues in the same open game
    rather than routing back to the open-games list or the main menu.
    *Source: `Menus and UI.md` → Game Over → Rematch ("The rematch continues in the **same
    open game** — same series, scoreboard intact. It does not start a second open game");
    `Game Overview.md` → Session Structure ("Continuing **resets the board**").*
    *Testable:* taking the rematch leaves the game screen on display and adds no entry to the
    back stack.
    *Note:* the docs settle this at the level of *which open game the series belongs to*;
    reading it as "no route change" is the narrow routing consequence, not a separate decision.
    Whether the game-over surface itself can be dismissed, and whether an exit control sits
    beside Rematch, are `P3-04-game-over-rematch.md`'s open questions — Open Question 12.

### Constraints on the graph

14. **No route reachable from a game leads to theme selection.** The theme cannot be changed
    mid-game.
    *Source: `Theming.md` → Decisions → Can you change the theme mid-game ("**No** — leave it
    out for now. Theme changes happen from the main menu only"); `Menus and UI.md` → Theme
    Selection.*
    *Testable:* no operation reachable from the game screen or its quick-actions surface
    reaches the theme overlay. `P4-03-theme-selection.md` Requirement 19 asserts the same
    constraint from the screen's side; this one holds it in the routing graph.

15. **The navigation layer holds no hardcoded theme values** — including no hardcoded
    `Duration(…)` for any transition — and passes the hardcoded-theme-value test with the
    baseline at zero.
    *Source: `Theming.md` → Architectural Rule ("All of our code operates off of the theme. No
    code should be operating independently from the selected theme"); `Tech Design.md` →
    Decisions → Do we add a test that fails on hardcoded theme values? ("Durations are in
    scope because … a hardcoded `Duration` is a theme value that escaped"; "the baseline starts
    at zero").*
    *Testable:* the scan in `P1-05-theme-guard-test.md` passes over `lib/navigation/` with no
    baseline entries.
    Whether there is any transition motion to time at all is Open Question 14.

## Out of Scope

Referenced by filename rather than specified here. This PRD moves between these surfaces and
specifies none of them:

- **The main menu** — its buttons, title, logo and styling → `P4-01-main-menu.md`.
- **The open-games list and the name prompt's contents** — rows, the delete action, the cap,
  the `ItSaMeMaRiO` default, the character limit, and the back button drawn on `1b` →
  `P4-02-open-games-list.md`. Requirement 8 claims the prompt's *transitions* only.
- **The theme selection overlay** — its rows, highlight, labels and failure modal →
  `P4-03-theme-selection.md`.
- **Settings and the in-game quick-actions surface** — the three toggles, what quick actions
  contains, and the exit control's own presentation → `P4-04-settings.md`.
- **The game screen** → `P3-01-board-rendering.md`. **Move input and the pending selection** →
  `P3-02-move-input.md`. **The game-over surface and rematch** →
  `P3-04-game-over-rematch.md`.
- **Storing, capping, creating, deleting and restoring open games** → `P1-04-persistence.md`.
- **The purchase flow and its host surface** → `P4-05-purchase-flow.md`. `Menus and UI.md` →
  Decisions → *Where the open-game slot unlock is sold* settles that a buying surface exists
  and that *"which screen it lives on is not decided"*; its Open Questions name the open-games
  list at the cap, the settings screen, or **a dedicated store surface** as candidates. Under
  the third that is a destination this graph has no route to, and a global *Restore purchases*
  affordance may be another. No route to either is specified here — same shape as the About Us
  item below.
- **The About Us screen (`1c`).** Drawn in the approved handoff, not listed in
  `Menus and UI.md` → Screens (so far), and whether it exists at all is open in
  `P4-01-main-menu.md`. No route to it is specified here.
- **A fuller Rules / How-to-Play screen.** `P3-05-how-to-play.md` owns the on-board legend and
  hint, which need no route. `Menus and UI.md` → Open Questions holds open *"Is there also a
  fuller Rules/How-to-Play screen"* and lists Rules/How to Play among future menu items; if one
  appears it is another destination, and no route to it is specified here.
- **Screen transition animations.** `Animations.md` → Scope For Now: *"We are **not**
  animating the board, the layout, or transitions between screens yet."* Requirement 15
  constrains what happens if a motion value is nonetheless introduced; it does not authorize
  one. See Open Question 14.
- **A confirmation prompt on exiting a game.** Unsettled — Open Question 6. Nothing here
  designs one and nothing here rules one out.
- **`Alternative Game Styles.md`** — declared parking lot; not what is being built.

## Open Questions

### From the design docs — unresolved, worded as the docs word them

1. **The routing approach.** `Tech Design.md` → Open Questions → *4. Navigation approach*:

   > The app has an explicit navigation layer (see Decisions → Navigation), but no Decision
   > names how it's built — plain `Navigator` push/pop, `go_router`, or something else — and
   > the dependency list has no router in it yet.

   Requirements 1–3 are written to stand either way.

2. **Pop or push on exit.** `Menus and UI.md` → Open Questions:

   > **What is the routing/navigation approach**, and does exiting a game pop back to an
   > existing main menu instance or push a fresh one?

   This is where Requirement 11 stops. It also decides whether the iOS back-swipe can carry a
   player back into the game they just exited — and iOS is the primary target
   (`Tech Design.md` → Decisions → Primary target — Apple), so the gesture is present by
   default.

3. **Where each back affordance leads.** `Menus and UI.md` → Open Questions:

   > **Where does each back affordance lead** — the in-game back/exit action, and the iOS
   > back-swipe gesture — and can the swipe gesture carry a player back into a game they just
   > exited?

4. **Does the empty-state path show the name prompt?** `Menus and UI.md` → Play Game → Where
   It Takes You:

   > Undecided: whether the empty-state path (no open games → straight into a new game) also
   > shows the opponent-name prompt, or skips it. "No intermediate screen" and the prompt
   > can't both be true on that path.

   Requirement 5 stands either way; Requirement 8 covers the from-the-list path only. Also
   carried by `P4-02-open-games-list.md` → Open Question 1.

5. **Is the name prompt its own screen or an overlay?** `Menus and UI.md` → Screens (so far)
   → 3. New Game Name Prompt: *"Undecided whether it's its own screen or an overlay."*
   One instance of Open Question 10, and it lands directly on Requirement 8.

6. **Does leaving a game still need a confirmation prompt?** `Menus and UI.md` → Leaving a
   game mid-play:

   > Whether leaving still needs a confirmation prompt is undecided; the original reason for
   > one ("Leave game? Your score will be lost") no longer applies.

7. **Is quick actions the same settings screen as the main menu's?** `Menus and UI.md` → How
   you reach settings from gameplay:

   > Undecided: whether quick actions is the *same* settings screen as the main menu's, or a
   > trimmed-down in-game version with the exit option added.

   Requirement 7 settles that there are two entry points, not that there are two surfaces;
   Requirement 3 names an operation per entry point for the same reason. Also carried by
   `P4-04-settings.md` → Open Question 1.

### Raised by PRD review across the existing PRDs — carried here, not answered

8. **The open-games list draws a back button no design doc mentions.**
   `P4-02-open-games-list.md` → Open Question 7: *"How does the player leave the list without
   picking anything? `1b` draws a back button; no design doc mentions one, or says where back
   goes."* Under Requirement 5 the list is reached from the main menu, but nothing settles
   that back returns there rather than, say, into a game.

9. **No control is named for returning from the in-game settings surface to the game.**
   `P4-04-settings.md` records that its Requirement 2 settles that reaching settings does not
   abandon the game, *"but no doc names the control that returns you to it. The handoff gives
   `1f` a close button and a 'Back to the game' action; the docs give it neither."*
   Requirements 3 and 10 have the same hole: the operation is specified, its trigger is not.

10. **Is a modal or sheet a route, or an overlay?** The approved handoff draws `2b — Settings
    page` as *"Full screen, not a sheet — this is the main-menu route; 1f stays the trimmed
    in-game version"*, and draws `1f` as a bottom sheet. `P4-04-settings.md` → Open Question 1
    holds this unresolved, and it is a navigation-layer question as much as a presentation one:
    a route participates in the back stack and the back-swipe gesture, an overlay does not. It
    decides what `dismissCurrent()` does. Requirement 6 settles it for theme selection only,
    because a Decision covers that one case.

11. **What happens to a pending move selection when a surface opens over the board?** The two
    PRDs disagree about the status of this question, not just the answer:
    `P4-04-settings.md` → Requirement 2 asserts as testable that the pending selection is
    *"exactly as it was"* after dismissing the surface, while `P3-02-move-input.md` → OQ-1
    lists it as open — *"whether opening the in-game settings / quick-actions modal (`1f`)
    clears a pending selection or leaves it standing when the modal is dismissed."*
    Requirement 10 deliberately does not take a side.

12. **Is the exit route live while the game-over surface is on screen?**
    `P3-04-game-over-rematch.md` → OQ3: *"`Menus and UI.md` settles that settings must be
    reachable *mid-game* and that it is also the way out; a finished game is not mid-game, and
    the docs do not say whether that button keeps working, is hidden, or is the intended exit
    route."* If it is not live, then at game over the only settled route out of a game
    (Requirement 11) does not exist.

### Raised by round-2 review of this PRD — recorded, not answered

13. **Does anything render before the main menu?** Requirement 4 makes the main menu the app's
    first screen, and as written its testable would forbid two things nobody has ruled out: the
    iOS launch screen the platform shows before the first frame, and any gate held while the
    persisted theme is materialized — `Theming.md` → Why this matters for the build says
    materialization happens *"at startup"*, and `Tech Design.md` → Open Questions → *2. Theme
    loading* leaves open how many themes that covers. Whether a splash, a loading state, or
    nothing at all precedes the menu is unstated.

14. **Do screen transitions animate at all, and does the Animations toggle apply to them?**
    `Animations.md` → Scope For Now says transitions between screens are not animated *yet*,
    while → Decisions → *Turn animations off — a global setting* and → *Animations off =
    instant state change* describe a toggle that governs everything the game animates. If a
    transition ever animates, whether its timing is a theme value (Requirement 15) and whether
    the toggle switches it off are both unaddressed.

15. **What does wave P2 build against?** Every testable in this PRD asserts a transition
    between screens that waves P3 and P4 have not built yet, and the wave rule is that a lower
    wave ships first. Whether this PRD ships the layer plus placeholder destinations, ships the
    layer with its tests deferred, or is re-sequenced is not stated.

### Found while writing this PRD — gaps, flagged rather than answered

16. **`P1-01-app-scaffold.md` does not create the directory this PRD depends on.** Its
    Requirement 2 enumerates `main.dart`, `app.dart`, `engine/`, `storage/`, `theme/`,
    `state/`, `ui/board/`, `ui/menus/` and calls that *"exactly the tree given in the doc"* —
    which predates the amendment to `Tech Design.md` → Decisions → Project structure —
    layer-first that added `navigation/`. As the two read today, wave 1 would not create the
    directory Requirement 2 above places this layer in. The fix belongs to `P1-01`.

17. **The declared dependency set has no router in it.** `P1-01-app-scaffold.md` Requirement 12
    enumerates the `pubspec.yaml` dependencies exhaustively. If Open Question 1 resolves to a
    package, that requirement needs amending — and it is in an earlier wave.
