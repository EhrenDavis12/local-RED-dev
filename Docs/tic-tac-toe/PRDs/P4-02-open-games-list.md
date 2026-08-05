# PRD: Open Games List and the New Game Name Prompt

> **Status:** Draft · Source docs read: `Menus and UI.md`, `Game Overview.md`, `Rules.md`,
> `Theming.md`, `Game Board Design.md`, `Tech Design.md`, `Animations.md`, `roadmap.md`, and
> the read-only reference asset `design_handoff_game_ui/` (screens `1b — Select Game` and
> `2c — New Game, opponent name prompt`). `Alternative Game Styles.md` is a declared
> parking-lot doc and was not sourced from.

> **Wave:** P4 · **Depends on:** `P1-01-app-scaffold.md` (the `ui/menus/` structure and
> Riverpod root), `P1-02-engine-rules.md` (the game/series model a new game is created
> from), `P1-03-theme-system.md` (every value on this screen is read from the active theme —
> its requirement 15 inventory, plus the three slots requirement 20 below names for it),
> `P1-04-persistence.md` (reading, creating, deleting and resuming stored open games — its
> requirements 10 and 17, and the identity scheme its Open Question 6 holds),
> `P1-07-entitlements.md` (the open-game cap value this screen reads — its requirement 3),
> `P2-01-navigation.md` (every screen change this feature performs — its requirements 3, 5,
> 8 and 9), and `P4-01-main-menu.md` (the Play Game button this path hangs off — same wave,
> parallel-safe). Hands off to `P3-01-board-rendering.md`, which owns the screen a game
> opens into and ships in an earlier wave.

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
   settling the prompt either way. `P2-01-navigation.md` requirement 5 holds the same branch
   in the routing graph — the branch is evaluated inside that layer, not by this screen —
   and is written to stand either way too.

2. **With one or more open games, Play Game opens a screen listing all open games**, and the
   screen renders every open game it is given: none is hidden, truncated or paginated away.
   *Source: `Menus and UI.md` → Play Game → Where It Takes You ("Open games exist — a new
   screen listing all open games"); → Screens (so far) → 2. Open Games List; → Decisions →
   Is the main menu button "New Game" or "Play Game"?*
   *Testable:* with 1, 2 and 3 stored open games, the screen renders exactly that many game
   rows.
   *Derived, not cited:* the list **scrolls** rather than assuming its contents fit one
   screen. No design doc says so; it follows from the cap of 100 in requirement 6 and the
   402×874 frame the handoff draws — 100 rows at `1b`'s card height cannot be on screen at
   once. What is derived is the scroll behavior alone.
   *Scoped to the normal state:* this requirement and requirement 6 both assume the stored
   count is at or below the effective cap. The over-cap state — an entitlement lapsing while
   games are stored — is Open Question 8. Nothing in this requirement licenses hiding a
   stored game, and nothing in requirement 6 licenses rendering fewer than there are.

3. **New Game is an option at the top of that list**, above every open game row.
   *Source: `Menus and UI.md` → Play Game → Where It Takes You ("with **New Game** as an
   option at the **top of the list**"); → Decisions → What does each row in the open-games
   list show? ("The list shows New Game plus any open games"); `design_handoff_game_ui/`
   → *1b — Select Game* ("`+ NEW GAME` sits at the **top of the list**").*
   *Testable:* New Game precedes all game rows in the rendered order at every list length.
   *Not settled:* whether it scrolls away with the list or stays pinned above it. "At the
   top of the list" is satisfied by both, and the difference is invisible at 3 games and
   unavoidable at 100 — see Open Question 11.

4. **Each open game row is titled with that game's opponent name.**
   *Source: `Menus and UI.md` → Decisions → What does each row in the open-games list show?
   ("each open game is titled with the opponent's name"); → Play Game → Where It Takes
   You.*
   *Testable:* a game stored with opponent name "Dad" renders a row titled "Dad".
   The name is a **title, not a key** — see requirement 19.

5. **Selecting an open game resumes that series, not just its last board** — the board
   picks up where it was left and the game's own running score (Player One / Ties / Player
   Two) comes back with it, rather than restarting at zero.
   *Source: `Menus and UI.md` → Decisions → What does an open game hold? ("An open game
   holds a whole series — the board plus the running score ... resuming a game from the
   open-games list resumes the *series*, not just the last individual board"); →
   Persistence (table); `Game Overview.md` → Decisions → Scoreboard lifetime.*
   *Testable:* store a game mid-board with a score of 3-1-2, resume it from the list, and
   the board state and 3-1-2 score are both present on the game screen.
   The screen change is `P2-01-navigation.md` requirement 9's `openGame(gameId)`; which game
   is identified by requirement 19 below; restoring the state is `P1-04-persistence.md`'s.

6. **The number of open games is capped, and the cap is entitlement-dependent: 3 by
   default, 100 once the unlock is owned.** The screen reads the effective cap rather than
   treating 3 as a constant.
   *Source: `Menus and UI.md` → Decisions → How many open games do we keep? ("**3 by
   default, no more.** A **$4.99 in-app purchase raises the cap to 100 open game slots**");
   → What does an open game hold?; `Tech Design.md` → Decisions → In-app purchases ("a
   **$4.99 unlock that raises the open-game cap from 3 to 100**").*
   *Testable:* with the unlock un-owned the effective cap this screen reads is 3; with it
   owned, 100; neither number is written into this screen's code.
   **The cap governs whether another game can be created, not how many stored games are
   drawn.** Enforcement is a create-time check in `P1-04-persistence.md` requirement 10,
   which explicitly declines to trim, evict or refuse to load games that already exist. This
   screen does not enforce the cap by displaying fewer rows than it holds.
   The **cap value** is `P1-07-entitlements.md`'s (its requirement 3) — wave 1, so it exists
   before this screen does. **StoreKit, the price, purchase and restore** are
   `P4-05-purchase-flow.md`'s. This screen consumes all three and defines none of them.

7. **The open-games list carries a delete action, and deleting an open game frees a slot.**
   The deleted game's series and scoreboard go with it, and the freed slot is immediately
   usable by a new game.
   *Source: `Menus and UI.md` → Decisions → Deleting an open game ("**The open-games list
   gains a delete action, so a slot can be freed.** This closes a hole — with a cap of 3
   and a rematch staying in the same open game, nothing previously ever freed a slot").*
   *Testable:* at the effective cap, deleting one game leaves the list one row shorter and
   makes New Game succeed where it previously could not.
   Delete acts on the identifier in requirement 19, never on the title. The repository call
   is `P1-04-persistence.md` requirement 17's.
   *Considered and rejected:* automatically **replacing the oldest** open game, as drawn in
   `design_handoff_game_ui/` → `1b`'s footer ("Three saved games. Starting a fourth replaces
   the oldest."). The decision is an explicit, player-initiated delete instead. That footer
   is stale — it annotates itself as reflecting an unconfirmed open question — and is not
   authoritative. Nothing in this feature deletes a game the player did not choose to
   delete.

### The New Game name prompt

> The prompt's three screen changes — opening it, opening the game on confirm, dismissing it
> on cancel — belong to `P2-01-navigation.md` requirement 8, which names them
> `openNewGamePrompt()`, `openGame(gameId)` and `dismissCurrent()` in its requirement 3.
> Requirements 8, 10 and 12 specify the prompt's **contents and effects** and invoke those
> operations; they do not perform or re-specify the transitions.

8. **The New Game control opens the opponent-name prompt, whose contents are a title, a
   labelled single-line text field, helper text, and a cancel / confirm pair.** Activating
   New Game invokes `openNewGamePrompt()`.
   *Source: `Menus and UI.md` → Play Game → Where It Takes You ("Selecting New Game prompts
   for the opponent's name"); → Decisions → What does each row in the open-games list show?
   ("When the user selects New Game, they get a prompt to input the name of their
   opponent"); → Screens (so far) → 3. New Game Name Prompt; `design_handoff_game_ui/` →
   *2c* for the contents — title, the `Opponent` field label, the helper line, and the two
   actions.*
   *Testable:* activating New Game invokes `openNewGamePrompt()` exactly once and creates no
   game; the prompt that results carries the field, the default value from requirement 9,
   and both actions.

9. **The prompt is pre-filled with the default name ItSaMeMaRiO**, so a player who types
   nothing gets that name.
   *Source: `Menus and UI.md` → Play Game → Where It Takes You ("with a default of
   **ItSaMeMaRiO**"); → Decisions → What does each row in the open-games list show?;
   `design_handoff_game_ui/` → *2c* ("Default value **ItSaMeMaRiO**, pre-selected so typing
   replaces it").*
   *Testable:* opening the prompt shows `ItSaMeMaRiO` in the field; confirming without
   editing creates a game titled `ItSaMeMaRiO`.

10. **Confirming the prompt creates exactly one new open game, titled with the entered name,
    and hands that game's identifier to `openGame(gameId)`.** The name is the game's title
    in the open-games list and is used nowhere else — in game the players stay Player One
    and Player Two (`P3-03-scoreboard-turn-indicator.md` owns the in-game scoreboard).
    *Source: `Menus and UI.md` → Decisions → Does the opponent name replace "Player Two" in
    game? ("No — not at this moment. The opponent name titles the game in the open-games
    list and nothing else"); `Game Overview.md` → Decisions → Player names.*
    *Testable:* after confirming with "Jules", exactly one new game is stored, its title is
    "Jules", `openGame` is invoked once carrying that game's identifier, and no in-game
    surface displays the name.
    Creating the record is `P1-04-persistence.md`'s; the transition is
    `P2-01-navigation.md` requirement 8's; the identifier is requirement 19's. What happens
    when the create is refused at the cap is Open Question 3.

11. **An empty name falls back to the default rather than blocking**, and the field accepts
    at most 16 characters.
    *Source: `design_handoff_game_ui/` → *2c — New Game, opponent name prompt* ("**Max 16
    characters** — the list row truncates past that. An empty name falls back to the
    default rather than blocking"). The `.md` design docs do not restate either rule; the
    handoff is the approved design and is the only source for them.*
    *Testable:* clearing the field and confirming creates a game titled `ItSaMeMaRiO`; a
    17th character cannot be entered.
    *Not settled — four separate coin-flips this requirement does not decide:* whether a
    whitespace-only entry counts as empty, whether input is trimmed, what "16 characters"
    counts, and what an over-limit paste does. See Open Question 10.

12. **Cancelling the prompt creates nothing** — no game record and no change to the stored
    open-game count — and dismisses the prompt with `dismissCurrent()`.
    *Source: `design_handoff_game_ui/` → *2c* ("Actions: `Cancel` (secondary, flex 1) and
    `Start playing` (primary, flex 2)", "the list stays visible and Cancel costs
    nothing").*
    *Testable:* after cancelling, no create call has reached `P1-04-persistence.md` and the
    stored open-game count is unchanged.
    Where the dismissal lands, and whether it pops a route or hides an overlay, are
    `P2-01-navigation.md` requirement 8 and its Open Question 10.

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
    no hardcoded colors, backgrounds, fonts, sizes, radii, sounds or motion.
    *Source: `Theming.md` → Architectural Rule ("All of our code operates off of the theme.
    No code should be operating independently from the selected theme"); `Menus and UI.md`
    → Main Menu ("The entire main menu is itself theme-driven ... No hardcoded styling here
    either"); `design_handoff_game_ui/` → the critical architectural constraint callout.*
    *Testable:* the hardcoded-theme-value scan (`P1-05-theme-guard-test.md`) passes over
    these files with the baseline at zero.
    The slots this screen consumes are `P1-03-theme-system.md` requirement 15's inventory —
    open-game rows and their chips, the sheet surface, the scrim, the text input field, the
    button pair and destructive-action styling — plus the three requirement 20 names.

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

### Added by round-2 review

> Numbered after 18 so that the cross-references other PRDs already hold into this one —
> `P1-03-theme-system.md` requirement 15 cites requirements 4, 7, 8, 9, 12, 17 and 18 here —
> keep pointing at the text they were written against.

19. **Every row carries the store's identifier for its open game, and resume and delete act
    on that identifier. The opponent name is a title and is never a key.** The identifier is
    what requirement 5 passes to `openGame(gameId)` and what requirement 7 passes to the
    delete call.
    *Source: `Menus and UI.md` → Decisions → What does each row in the open-games list show?
    (the name **titles** the game); `P1-04-persistence.md` → Open Question 6, which
    establishes that the name cannot serve as the key — requirement 9 above pre-fills
    `ItSaMeMaRiO` and confirming unedited accepts it, so **several identically titled games
    is the default case, not an edge case**; `P2-01-navigation.md` requirement 3, which
    already codes `openGame(gameId)` against an identity.*
    *Testable:* with three stored games all titled `ItSaMeMaRiO`, deleting the second
    removes exactly that record and leaves the other two byte-identical, and selecting the
    third invokes `openGame` with the third's identifier.
    The **id scheme itself** — what the identifier is and where it comes from — is
    `P1-04-persistence.md`'s and is unresolved in its Open Question 6. This requirement
    needs an identity to exist and to be stable; it does not choose one. The two halves that
    Open Question assigns to *this* PRD — whether the identity is ever player-visible, and
    whether duplicate titles are disambiguated in the list — are carried unanswered as Open
    Question 9.

20. **Three values this screen reads from the theme have no slot in
    `P1-03-theme-system.md` requirement 15's inventory yet, and are named here so it can
    carry them.** That inventory is explicitly open — its governing rule is that "the
    theme's slot list is derived from what the screens actually consume" — and requirement
    17 above is unbuildable for these three until they exist.
    - **The `+ NEW GAME` row's own treatment** — accent-outlined, 17pt, padding 18, radius
      13 in `1b`. This is a **fifth button tier**: it matches neither of the two main-menu
      tiers nor the prompt's primary/secondary pair, both of which requirement 15 already
      carries.
    - **The list's header chrome** — the 36×36 back icon button at radius 11, and the
      heading and sub-heading type (`1b`: "Pick up where you left off" 22/600 over a 12pt
      sub). Requirement 15 has a type scale but no slot for an icon button.
    - **The sheet underlay dimming** — `2c` dims the list **to 30%** behind an
      `rgba(15,16,24,0.74)` scrim. Requirement 15 carries the scrim set; the dimming of the
      surface beneath is a second, separate value, and `2a` dims the main menu to 35%, so it
      is not a constant either.
    *Source: `design_handoff_game_ui/` → *1b* and *2c* for the values;
    `Theming.md` → Decisions → What the theme's slots are derived from, for why naming them
    here is the mechanism rather than a request.*

## Out of Scope

Referenced by filename rather than specified here:

- **The main menu itself** — the Play Game button, its layout, title and logo →
  `P4-01-main-menu.md`. This PRD starts at the branch Play Game takes.
- **The routing layer** — the Play Game branch, the prompt's three transitions, where back
  leads, and whether exiting pops or pushes → `P2-01-navigation.md`. Requirements 8, 10 and
  12 invoke its operations and specify only what the prompt contains and does.
- **How open games are stored, read, deleted and capped** — the repository, Hive, the
  create-time cap check, the delete call, and the identity scheme → `P1-04-persistence.md`.
- **The entitlement that raises the cap** — the entitlement model, the free-tier defaults
  and the cap value → `P1-07-entitlements.md`. **The purchase itself** — StoreKit, the
  price point, and the purchase and restore-purchases flows → `P4-05-purchase-flow.md`.
  This screen reads the resulting cap and defines none of it.
- **The game screen** — the board, its highlights, move input and the game-over modals →
  `P3-01-board-rendering.md`, `P3-02-move-input.md`, `P3-04-game-over-rematch.md`. This PRD
  ends at handing off to them.
- **The in-game scoreboard and turn indicator**, including the settled fact that the
  opponent name does *not* replace "Player Two" in game →
  `P3-03-scoreboard-turn-indicator.md`.
- **The rules of play** — alternation mechanics, the sending rule, win and cat-game
  detection, and turn order across games → `P1-02-engine-rules.md`, `Rules.md`.
- **The theme slot schema.** Requirement 20 names three slots; defining them, and every
  other slot this screen reads, is `P1-03-theme-system.md`'s.
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
   New-Game-from-the-list path only. Also carried by `P2-01-navigation.md` → Open
   Question 4.

2. **Is the name prompt its own screen or an overlay?**
   `Menus and UI.md` → Screens (so far) → 3. New Game Name Prompt: *"Undecided whether it's
   its own screen or an overlay."*
   The approved handoff picks one — `2c` is drawn as *"A sheet over the games list (list
   dimmed to 30% ...)"* and says outright *"The docs leave 'own screen or overlay' open —
   this picks overlay, so the list stays visible and Cancel costs nothing."* That is the
   handoff answering a question the docs still hold open, and it is recorded here rather
   than resolved. Requirement 12 reads the same either way.
   `P2-01-navigation.md` → Open Questions 5 and 10 record the routing half: whether a sheet
   is a route at all changes what the back-swipe does.

### Found while writing this PRD — not settled anywhere, flagged rather than answered

3. **What does New Game do when the player is already at the effective cap?** The cap and
   the delete action are now settled (requirements 6 and 7), so a slot can always be freed —
   but nothing says what the player sees at the moment they tap New Game with no slot left.
   Refuse with a message pointing at delete, open the delete flow, and offer the $4.99
   unlock as an upsell are all consistent with the Decisions as written, and they are
   different screens. Replace-the-oldest is ruled out (requirement 7).
   Also carried by `P1-04-persistence.md` → Open Questions 3, whose requirement 10 fixes the
   storage half either way (the create fails rather than evicting). The upsell candidate
   overlaps `Menus and UI.md` → Open Questions on **where the $4.99 unlock gets sold**,
   carried by `P4-05-purchase-flow.md` → Open Question 2 — if the answer is "this screen,
   at the cap", that PRD and this one stop being parallel-safe within wave 4.

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
   button; no design doc mentions one, or says where back goes. Now also carried by
   `P2-01-navigation.md` → Open Question 8, which notes that under its requirement 5 the
   list is reached from the main menu but nothing settles that back returns there.

### Raised by round-2 review of this PRD — recorded, not answered

8. **What does the list do when the stored count exceeds the effective cap?** A player buys
   the unlock, creates 60 games, and then no longer holds the entitlement: the cap drops to
   3 and 60 games are stored. Requirements 2 and 6 are both scoped away from this state
   rather than taking a side — render all 60, render 3, or something else are all still on
   the table, and so is whether the list is even where that gets resolved.
   Already open in `P1-07-entitlements.md` → Open Question 1 (*"kept and read-only, kept and
   hidden, deleted oldest-first, or the cap simply stops being enforced downward is not
   stated anywhere"*) and `P1-04-persistence.md` → Open Question 5, whose requirement 10 is
   deliberately a create-time check *"so that nothing is destroyed by default, but that is a
   holding position, not the answer."* Both are with the user; this PRD carries the display
   half so an implementer meets the state in writing rather than in the field.

9. **Is a game's identity ever visible to the player, and do duplicate titles get
   disambiguated in the list?** `P1-04-persistence.md` → Open Question 6 raises the identity
   question and assigns exactly these two halves here: *"whether the identity is visible to
   the player at all, since it is otherwise a purely internal handle, and whether duplicate
   titles need disambiguating in the list — the latter is `P4-02-open-games-list.md`'s
   call."* Requirement 19 settles the mechanism (rows key off the identifier, never the
   title) and deliberately stops before both. Because `ItSaMeMaRiO` is pre-filled, three
   rows reading `ItSaMeMaRiO` is what a player gets by default, and nothing tells them apart
   unless Open Question 4 lands on per-row content that does.

10. **How is the entered name normalized?** Requirement 11 settles empty→default and a
    16-character limit. Four things ride on top of it and none is stated anywhere:
    - Is a **whitespace-only** entry "empty" for the fallback, or a valid title?
    - Is input **trimmed** before it is stored and titled?
    - Does "16 characters" count **UTF-16 code units or grapheme clusters**? An emoji or a
      combining accent lands differently under each, and `2c` draws a **live `11/16`
      counter** that has to agree with whatever the limit counts.
    - Does an **over-limit paste truncate or reject**?

11. **Does New Game scroll away with the list, or stay pinned above it?** The docs say only
    that it sits at the top of the list, which both satisfy. At 3 games the distinction
    never shows; at 100 it always does — a player scrolling a long list either keeps the
    control in reach or has to scroll back for it.
