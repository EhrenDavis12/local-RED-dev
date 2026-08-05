# PRD: Open Games List and the New Game Name Prompt

> **Status:** Draft · Source docs read: `Menus and UI.md`, `Game Overview.md`, `Rules.md`,
> `Theming.md`, `Game Board Design.md`, `Tech Design.md`, `Animations.md`, `roadmap.md`, and
> the read-only reference asset `design_handoff_game_ui/` (screens `1b — Select Game` and
> `2c — New Game, opponent name prompt`). `Alternative Game Styles.md` is a declared
> parking-lot doc and was not sourced from.

> **Wave:** P3 · **Depends on:** `P1-01-app-scaffold.md` (the `ui/menus/` structure and
> Riverpod root), `P1-02-engine-rules.md` (the game/series model a new game is created
> from), `P1-03-theme-system.md` (every value on this screen is read from the active
> theme), `P1-04-persistence.md` (reading, creating, deleting and resuming stored open
> games), `P4-05-in-app-purchases.md` (the open-game-slots entitlement this screen reads —
> it is defined there and only consumed here), and `P3-01-main-menu.md` (the Play Game
> button this path hangs off). Hands off to `P2-01-board-rendering.md`, which owns the
> screen a game opens into.

## Problem

Play Game is the only way into a game, and today it has nowhere to go. A player with games
already on the go has no way to see them, choose between them, or delete one to free a
slot, and no way to say who they are playing before starting a new one — so the saved
series the app keeps (`Menus and UI.md` → Decisions → How many open games do we keep?) are
unreachable, and an open game has no title to be listed under. The docs settle that Play
Game branches on whether open games exist, that the list is titled by opponent name, that
the list carries a delete action, and that New Game asks for that name; none of it exists.

## Goal

Tapping **Play Game** with no open games drops the player straight into a new two-player
pass-and-play game with no list screen in between; tapping it with open games shows a
screen listing every open game, each titled with its opponent's name, with **New Game** at
the top of that list and a delete action that frees a slot. Picking an open game resumes
that whole series — its board and its running score — and picking New Game prompts for the
opponent's name, defaulted to **ItSaMeMaRiO**, before starting a fresh series on the same
phone.

## Requirements

### Entry — where Play Game takes you

1. **With zero open games, Play Game goes straight into a new game and the open-games list
   screen is not shown.**
   *Source: `Menus and UI.md` → Play Game → Where It Takes You ("No open games — straight
   into a new game, no intermediate screen"); → Decisions → Is the main menu button "New
   Game" or "Play Game"?*
   *Testable:* with no stored open games, tapping Play Game never renders the list screen.
   *Note:* whether the **name prompt** appears on this path is unresolved — see Open
   Question 1. This requirement constrains the list screen only, and must not be read as
   settling the prompt either way.

2. **With one or more open games, Play Game opens a screen listing all open games.** Every
   stored open game is listed; none is hidden or paginated away.
   *Source: `Menus and UI.md` → Play Game → Where It Takes You ("Open games exist — a new
   screen listing all open games"); → Screens (so far) → 2. Open Games List; → Decisions →
   Is the main menu button "New Game" or "Play Game"?*
   *Testable:* with 1, 2 and 3 stored open games, the screen renders exactly that many game
   rows. Because the cap can be raised to 100 (requirement 6), the list scrolls rather than
   assuming its contents fit one screen.

3. **New Game is an option at the top of that list**, above every open game row.
   *Source: `Menus and UI.md` → Play Game → Where It Takes You ("with **New Game** as an
   option at the **top of the list**"); → Decisions → What does each row in the open-games
   list show? ("The list shows New Game plus any open games"); `design_handoff_game_ui/`
   → *1b — Select Game* ("`+ NEW GAME` sits at the **top of the list**").*
   *Testable:* New Game precedes all game rows in the rendered order at every list length.

4. **Each open game row is titled with that game's opponent name.**
   *Source: `Menus and UI.md` → Decisions → What does each row in the open-games list show?
   ("each open game is titled with the opponent's name"); → Play Game → Where It Takes
   You.*
   *Testable:* a game stored with opponent name "Dad" renders a row titled "Dad".

5. **Selecting an open game resumes that series, not just its last board** — the board
   picks up where it was left and the game's own running score (Player One / Ties / Player
   Two) comes back with it, rather than restarting at zero.
   *Source: `Menus and UI.md` → Decisions → What does an open game hold? ("An open game
   holds a whole series — the board plus the running score ... resuming a game from the
   open-games list resumes the *series*, not just the last individual board"); →
   Persistence (table); `Game Overview.md` → Decisions → Scoreboard lifetime.*
   *Testable:* store a game mid-board with a score of 3-1-2, resume it from the list, and
   the board state and 3-1-2 score are both present on the game screen.

6. **The number of open games is capped, and the cap is entitlement-dependent: 3 by
   default, 100 once the $4.99 in-app purchase is owned.** The screen reads the effective
   cap rather than treating 3 as a constant, and lists every open game up to it.
   *Source: `Menus and UI.md` → Decisions → How many open games do we keep? ("**3 by
   default, no more.** A **$4.99 in-app purchase raises the cap to 100 open game slots**");
   → What does an open game hold?; `Tech Design.md` → Decisions → In-app purchases ("a
   **$4.99 unlock that raises the open-game cap from 3 to 100**").*
   *Testable:* with the unlock un-owned the screen's effective cap is 3; with it owned, 100;
   no literal `3` governs list behavior.
   The entitlement itself — StoreKit, the price, purchase and restore — is
   `P4-05-in-app-purchases.md`'s; enforcing the cap in the store is
   `P1-04-persistence.md`'s. This screen consumes both.

7. **The open-games list carries a delete action, and deleting an open game frees a slot.**
   The deleted game's series and scoreboard go with it, and the freed slot is immediately
   usable by a new game.
   *Source: `Menus and UI.md` → Decisions → Deleting an open game ("**The open-games list
   gains a delete action, so a slot can be freed.** This closes a hole — with a cap of 3
   and a rematch staying in the same open game, nothing previously ever freed a slot").*
   *Testable:* at the effective cap, deleting one game leaves the list one row shorter and
   makes New Game succeed where it previously could not.
   *Considered and rejected:* automatically **replacing the oldest** open game, as drawn in
   `design_handoff_game_ui/` → `1b`'s footer ("Three saved games. Starting a fourth replaces
   the oldest."). The decision is an explicit, player-initiated delete instead. That footer
   is stale — it annotates itself as reflecting an unconfirmed open question — and is not
   authoritative. Nothing in this feature deletes a game the player did not choose to
   delete.

### The New Game name prompt

8. **Selecting New Game prompts for the opponent's name before the game starts.**
   *Source: `Menus and UI.md` → Play Game → Where It Takes You ("Selecting New Game prompts
   for the opponent's name"); → Decisions → What does each row in the open-games list show?
   ("When the user selects New Game, they get a prompt to input the name of their
   opponent"); → Screens (so far) → 3. New Game Name Prompt.*
   *Testable:* selecting New Game from the list renders the prompt and starts no game until
   it is confirmed.

9. **The prompt is pre-filled with the default name ItSaMeMaRiO**, so a player who types
   nothing gets that name.
   *Source: `Menus and UI.md` → Play Game → Where It Takes You ("with a default of
   **ItSaMeMaRiO**"); → Decisions → What does each row in the open-games list show?;
   `design_handoff_game_ui/` → *2c* ("Default value **ItSaMeMaRiO**, pre-selected so typing
   replaces it").*
   *Testable:* opening the prompt shows `ItSaMeMaRiO` in the field; confirming without
   editing creates a game titled `ItSaMeMaRiO`.

10. **Confirming the prompt creates a new open game titled with the entered name and opens
    it.** The name is the game's title in the open-games list and is used nowhere else —
    in game the players stay Player One and Player Two
    (`P2-03-scoreboard-turn-indicator.md` owns the in-game scoreboard).
    *Source: `Menus and UI.md` → Decisions → Does the opponent name replace "Player Two" in
    game? ("No — not at this moment. The opponent name titles the game in the open-games
    list and nothing else"); `Game Overview.md` → Decisions → Player names.*
    *Testable:* after confirming with "Jules", the new game's row is titled "Jules" and no
    in-game surface displays it.

11. **An empty name falls back to the default rather than blocking**, and the field accepts
    at most 16 characters.
    *Source: `design_handoff_game_ui/` → *2c — New Game, opponent name prompt* ("**Max 16
    characters** — the list row truncates past that. An empty name falls back to the
    default rather than blocking"). The `.md` design docs do not restate either rule; the
    handoff is the approved design and is the only source for them.*
    *Testable:* clearing the field and confirming creates a game titled `ItSaMeMaRiO`; the
    17th character cannot be entered.

12. **Cancelling the prompt returns to the open-games list and creates nothing.**
    *Source: `design_handoff_game_ui/` → *2c* ("Actions: `Cancel` (secondary, flex 1) and
    `Start playing` (primary, flex 2)", "the list stays visible and Cancel costs
    nothing").*
    *Testable:* cancelling leaves the stored open-game count unchanged and the list on
    screen.

### What a new game starts

13. **A new game is a two-player game on the same phone — one device, passed back and
    forth.**
    *Source: `Menus and UI.md` → A New Game → What It Starts; `Game Overview.md` → Modes
    ("Two player, same phone (pass-and-play) ... Started from the **Play Game** button on
    the main menu"); → Target Audience & Platform.*

14. **Turn order alternates Player One → Player Two → Player One → Player Two, and the
    active player switches automatically after each move** — the player does not confirm or
    trigger the handoff.
    *Source: `Menus and UI.md` → A New Game → What It Starts; → Pass-and-Play Turn Handoff
    ("The game switches the active player automatically after each move"); `Game
    Overview.md` → Modes.*
    *Testable:* committing a move leaves the other player active with no further input.
    Turn alternation inside the engine is `P1-02-engine-rules.md`'s; who goes first in a
    *rematch* is `Rules.md` → Turn Order Across Games, not this PRD.

15. **There is no "pass the phone, don't peek" screen between turns — the handoff is
    instant.** Nothing is interposed between one player's committed move and the other
    player's turn.
    *Source: `Menus and UI.md` → Pass-and-Play Turn Handoff ("tic-tac-toe has no hidden
    information, so there's no need for a 'pass the phone, don't peek' screen between
    turns. The handoff can be instant"); `design_handoff_game_ui/` → Interactions &
    behavior ("Turn handoff is instant — no 'pass the phone' screen; there is no hidden
    info").*

16. **No AI opponent and no online play in this version.** New Game offers no opponent type
    to choose between — same-phone two-player is the only thing it can start.
    *Source: `Menus and UI.md` → A New Game → What It Starts ("No AI opponent, no online
    play in this version"); `Game Overview.md` → Decisions → Single-player / AI opponent
    ("**No.** Two players on one phone is the only mode"); → Modes ("Current scope — one
    mode only").*
    *Testable:* the New Game path exposes no mode, difficulty or opponent-type control.

### Presentation

17. **Every visual value on this screen and on the prompt is read from the active theme** —
    no hardcoded colors, backgrounds, fonts, sounds or motion.
    *Source: `Theming.md` → Architectural Rule ("All of our code operates off of the theme.
    No code should be operating independently from the selected theme"); `Menus and UI.md`
    → Main Menu ("The entire main menu is itself theme-driven ... No hardcoded styling here
    either"); `design_handoff_game_ui/` → the critical architectural constraint callout.*
    *Testable:* the hardcoded-theme-value scan (`P1-05-theme-guard-test.md`) passes over
    these files.

18. **The screen matches the approved drawing for `1b — Select Game`, and the prompt
    matches `2c`,** recreated in Flutter rather than ported from the HTML prototypes.
    *Source: `design_handoff_game_ui/` → README ("Recreate pixel-for-pixel using the
    codebase's own widgets", "not production code to copy"); `Menus and UI.md` → Screens
    (so far) → the screen-to-handoff table.*
    *Note:* `1b` predates two decisions this PRD implements — it draws no delete affordance
    (requirement 7) and its footer states the rejected replace-the-oldest behavior
    (requirement 7). Where the drawing and a Decision disagree, the Decision wins. `1b` also
    draws per-row content the `.md` docs never decide on — a relative timestamp, three mini
    score chips, and a chevron. Only the opponent-name title is settled in the docs
    (requirement 4). See Open Question 4.

## Out of Scope

Referenced by filename rather than specified here:

- **The main menu itself** — the Play Game button, its layout, title and logo →
  `P3-01-main-menu.md`. This PRD starts at the branch Play Game takes.
- **How open games are stored, read, deleted and capped** — the repository, Hive, and the
  storage-side enforcement of the effective cap → `P1-04-persistence.md`.
- **The in-app purchase that raises the cap** — StoreKit, the price point, the purchase and
  restore-purchases flows, and where the entitlement is stored and read from →
  `P4-05-in-app-purchases.md`. This screen reads the resulting cap and defines none of it.
- **The game screen** — the board, its highlights, move input and the game-over modals →
  `P2-01-board-rendering.md`. This PRD ends at handing off to it.
- **The in-game scoreboard and turn indicator**, including the settled fact that the
  opponent name does *not* replace "Player Two" in game →
  `P2-03-scoreboard-turn-indicator.md`.
- **The rules of play** — alternation mechanics, the sending rule, win and cat-game
  detection, and turn order across games → `P1-02-engine-rules.md`, `Rules.md`.
- **Theme selection and settings**, both reachable from the main menu, not from here.
- **Game over and rematch.** A rematch continues in the same open game and never returns to
  this list (`Menus and UI.md` → Game Over → Rematch).
- **The About Us screen (`1c`)**, which the handoff draws and `Menus and UI.md` does not
  list.
- **`Alternative Game Styles.md`** — parking lot, not what is being built.

## Open Questions

### From the design docs — unresolved, worded as the docs word them

1. **Does the empty-state path show the name prompt?**
   `Menus and UI.md` → Play Game → Where It Takes You: *"Undecided: whether the empty-state
   path (no open games → straight into a new game) also shows the opponent-name prompt, or
   skips it. 'No intermediate screen' and the prompt can't both be true on that path."*
   Requirement 1 is written to stand either way; requirement 8 covers the
   New-Game-from-the-list path only.

2. **Is the name prompt its own screen or an overlay?**
   `Menus and UI.md` → Screens (so far) → 3. New Game Name Prompt: *"Undecided whether it's
   its own screen or an overlay."*
   The approved handoff picks one — `2c` is drawn as *"A sheet over the games list (list
   dimmed to 30% ...)"* and says outright *"The docs leave 'own screen or overlay' open —
   this picks overlay, so the list stays visible and Cancel costs nothing."* That is the
   handoff answering a question the docs still hold open, and it is recorded here rather
   than resolved. Requirement 12 (Cancel returns to the list) reads the same either way.

### Found while writing this PRD — not settled anywhere, flagged rather than answered

3. **What does New Game do when the player is already at the effective cap?** The cap and
   the delete action are now settled (requirements 6 and 7), so a slot can always be freed —
   but nothing says what the player sees at the moment they tap New Game with no slot left.
   Refuse with a message pointing at delete, open the delete flow, and offer the $4.99
   unlock as an upsell are all consistent with the Decisions as written, and they are
   different screens. Replace-the-oldest is ruled out (requirement 7).

4. **What does a row show besides the opponent's name?** The docs settle the title only.
   `1b` additionally draws a relative timestamp (`2 hours ago`, `Yesterday`, `Sat, 14 Jun`)
   and three `YOU / TIES / THEM` score chips per row. The timestamp needs a per-game
   `updatedAt` that no Decision requires and that `P1-04-persistence.md` does not persist,
   and `YOU / THEM` is vocabulary the docs never use — they say Player One / Player Two
   everywhere.

5. **How is the delete action reached, and does it confirm?** The Decision settles that the
   list has one, not what it looks like or whether deleting a series with a running score
   asks first. `1b` was drawn before that decision and shows no affordance for it — no
   swipe, no edit mode, no per-row control. Deletion is the one irreversible action in this
   feature, and `Menus and UI.md` → Leaving a game mid-play leaves the related "does leaving
   need a confirmation prompt" question open too.

6. **In what order are the open games listed?** Most recent first, creation order, or
   unspecified — no doc says, and `1b`'s sample rows are drawn newest-first without stating
   it as a rule. This matters more now that the list can hold 100 games.

7. **How does the player leave the list without picking anything?** `1b` draws a back
   button; no design doc mentions one, or says where back goes.
