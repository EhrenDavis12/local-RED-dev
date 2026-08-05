# PRD: Game Over → Rematch

> **Status:** Draft · Source docs read: `Menus and UI.md`, `Game Overview.md`, `Rules.md`,
> `Game Board Design.md`, `Animations.md`, `Tech Design.md`, `Theming.md`, `roadmap.md`,
> plus the read-only reference asset `design_handoff_game_ui/README.md` (screens
> *1g — Modal: winner*, *1h — Modal: draw*, and → *Interactions & behavior*).
> `Alternative Game Styles.md` is a declared parking-lot doc and was read only to confirm
> it is out of scope — no requirement here comes from it.

**Wave:** P2.

**Dependencies:**

- `P1-02-engine-rules.md` — owns outcome detection (win / straight draw), series state,
  the score, and the turn-order-across-games rule. This PRD consumes that; it re-derives
  nothing.
- `P1-04-persistence.md` — owns writing the series to storage. Requirement 9 below
  restates that boundary rather than specifying storage.
- `P1-03-theme-system.md` — every value on this surface resolves through the active theme.
- `P2-01-board-rendering.md` — draws the finished board that this surface sits with or
  over.
- `P2-03-scoreboard-turn-indicator.md` — owns the scoreboard's own display; this PRD only
  specifies what the game-over surface must communicate about the result.

**Note on source status:** `Menus and UI.md` carries the house banner *"Nothing here is
settled"* while also carrying a `## Decisions` section. Following the practice set by
`P1-02-engine-rules.md`, this PRD sources requirements from that doc's **Decisions** and
from the *Game Over → Rematch* section that those decisions point at, and leaves everything
that section explicitly marks *"Undecided"* in **Open Questions**.

## Problem

A game of Tic-Tac-Toe-Extreme currently has no ending. The engine can report that a player
has three claimed quadrants in a row, or that the big board filled with nobody's line
(`Rules.md` → Winning the Game; → Edge Cases → Big board full with no three-in-a-row), but
nothing in the app tells the two players sharing the phone that it is over, nothing counts
the result, and there is no way to play the next one.

That gap breaks the unit of play the game is designed around. `Game Overview.md` → Session
Structure says the app *"isn't built around a single one-off game"* but around *"playing
several in a row on the same phone"*, with the scoreboard carrying across games so a
session becomes a running series. Without a game-over flow the scoreboard never moves, the
series never advances, and the finished board just sits there rejecting taps with no
explanation.

## Goal

When a game is won or drawn, the result is counted on that game's own scoreboard, the two
players are told what happened, and they are offered a rematch. Taking it resets the board
and hands the first move to the winner — or, after a tie, back to whoever went first in the
tied game — and carries on inside the *same* open game, so a session of many games
accumulates into one series with one running score rather than a pile of separate saved
games.

## Requirements

### Reaching the game-over state

1. **A game-over state is entered whenever the engine reports the game is no longer in
   progress** — won by Player One, won by Player Two, or a tie. Both outcomes lead to the
   game-over flow; there is no third ending.
   *Source: `Rules.md` → Turn Structure 5, → Winning the Game, → Edge Cases → Big board
   full with no three-in-a-row; `P1-02-engine-rules.md` req 22 (outcome is one of: in
   progress, won by Player One, won by Player Two, tie).*
   *Testable:* driving the engine to each of the three terminal outcomes enters the
   game-over state exactly once, and an in-progress game never enters it.

2. **A finished board accepts no further moves.** No cell and no quadrant is playable once
   the game is over, and the two-tap select-then-confirm interaction is inert.
   *Source: `P1-02-engine-rules.md` req 20 ("The game is over; no further moves are
   legal"), which sources `Rules.md` → Winning the Game.*
   *Testable:* after the game ends, taps on every one of the 81 cells produce no state
   change and no pending selection.

3. **A straight draw is presented as a tie with no winner.** When the big board fills with
   no three claimed quadrants in a row, the result is a tie regardless of how many
   quadrants each player holds — most-quadrants-claimed does not win, and the count is
   irrelevant. The game-over surface names no winner in this case.
   *Source: `Rules.md` → Edge Cases → Big board full with no three-in-a-row → straight
   draw.*
   *Testable:* a filled big board on which one player holds five quadrants and the other
   three, with no line, reaches the tie presentation and never the winner presentation.

4. **The scoreboard increments at game end — not when the rematch is taken.** As soon as
   the game is won or tied, exactly one column goes up by exactly one: the winner's column
   on a win, the **Ties** column on a tie. Taking the rematch increments nothing, and
   leaving without taking it does not un-count the game.
   *Source: `Menus and UI.md` → Decisions → When does the scoreboard increment ("**At game
   end.** The winner's column, or Ties, increments as soon as the game is won or tied — not
   when a rematch is taken. Taking the rematch only resets the board."); → Decisions → What
   happens when a game ends?; → Game Over → Rematch; `Game Overview.md` → Session Structure
   ("The score increments at game end, not when continuing is taken"); `Game Board
   Design.md` → Scoreboard ("Increments when a game ends"); `Rules.md` → Edge Cases → Big
   board full ("The Ties counter on the scoreboard goes up one").*
   *Testable:* the counter moves on the move that ends the game, before any further input;
   taking the rematch afterwards leaves all three counters unchanged; across a series of
   *n* finished games the three counters sum to *n* whether or not each was rematched.

5. **Rematch is offered as an option the player takes deliberately.** A rematch control is
   available in the game-over state; nothing restarts the board automatically, and the
   result stays on screen until the player acts.
   *Source: `Menus and UI.md` → Decisions → What happens when a game ends? ("A rematch
   button is available as an option"); → Game Over → Rematch; `Game Overview.md` → Session
   Structure ("the player is offered an option to continue playing").*
   *Testable:* with the game over and no input given, the board is not reset after an
   arbitrary wait.

### Taking the rematch

6. **Taking the rematch resets the board, and does nothing to the score.** All 81 cells are
   empty, all nine quadrants are unclaimed and open, and the new game begins in the
   free-choice state for its first player.
   *Source: `Menus and UI.md` → Game Over → Rematch ("Taking it resets the board for the
   next game"); → Decisions → What happens when a game ends? ("It resets the board for the
   next game"); → Decisions → When does the scoreboard increment ("Taking the rematch only
   resets the board"); `Game Overview.md` → Session Structure ("Continuing **resets the
   board**"); `Rules.md` → Setup, → Placement Rules → First move.*
   *Testable:* after a rematch, engine state equals a fresh game's board state, the legal
   moves are the empty cells of every quadrant, and the three counters are identical to
   their values immediately before the rematch was taken.

7. **The rematch continues in the same open game.** It does not create a second open game;
   the game's identity, its opponent name, and its running scoreboard are the same record
   before and after, and a rematch never consumes an open-game slot.
   *Source: `Menus and UI.md` → Game Over → Rematch ("The rematch continues in the **same
   open game** — same series, scoreboard intact. It does not start a second open game"); →
   Decisions → What does an open game hold? ("A rematch continues in the same open game
   with the scoreboard intact"); → Decisions → How many open games do we keep?;
   `Game Overview.md` → Decisions → Scoreboard lifetime.*
   *Testable:* with the open-games list at its cap and one of those games finished, taking
   the rematch leaves the open-game count unchanged and the other records untouched; the
   rematched game's identity and opponent name are unchanged.

8. **The rematch's first player follows the turn-order rule across games:** after a win,
   the winner of that game goes first; after a tie, the player who went first in the tied
   game goes first again — a tie does not pass the first-move advantage. The flow reads
   this from the engine rather than computing it.
   *Source: `Rules.md` → Turn Order Across Games; → Decisions → Who goes first after a
   tie?; `Menus and UI.md` → Game Over → Rematch ("The winner of that game goes first in
   the rematch — or on a tie, whoever went first last time"); `Game Overview.md` → Session
   Structure ("The winner of the last game goes first"); `P1-02-engine-rules.md` reqs
   25–26.*
   *Testable:* Player Two wins game 1 → Player Two opens game 2; game 2 ties → Player Two
   opens game 3; Player One wins game 3 → Player One opens game 4.

9. **The end-of-game increment and the rematch reset both go through the same persisted
   series record**, so quitting the app immediately after either one and reopening the game
   shows the score and board as they were on screen, with the correct first player. How
   that is written is `P1-04-persistence.md`'s (its reqs 8 and 9); this PRD requires only
   that neither step bypass it.
   *Source: `Menus and UI.md` → Persistence (table: scoreboard and game in progress both
   persist); `P1-04-persistence.md` req 8 ("A rematch continues in the same stored open
   game ... does not create a second stored record").*
   *Testable:* end a game, rebuild the store from disk, resume — the increment survived;
   repeat after taking the rematch — board, score and first player match what was on
   screen.

### What the game-over surface communicates

These are content requirements, deliberately independent of the presentation form, which is
unsettled — see **OQ-1**.

10. **The outcome is stated in words, and the two outcomes are visually distinct.** A win
    names the winning player; a tie states that nobody won.
    *Source: `Menus and UI.md` → Decisions → What happens when a game ends?;
    `design_handoff_game_ui/README.md` → 1g — Modal: winner ("Player One takes it!", card
    bordered in the winner's color) and → 1h — Modal: draw ("Nobody wins this one!",
    neutral border, both players' glyphs at 55%).*
    *Testable:* a Player One win, a Player Two win and a tie each produce different
    on-screen result copy, and the tie copy names no winner.

11. **The scoreboard is shown as part of the result, already including the finished game,
    with the column that moved identifiable.** Per requirement 4 the increment has already
    happened by the time this surface appears.
    *Source: `design_handoff_game_ui/README.md` → 1g ("the three score chips at 27/600
    with a `+1` under the incremented column") and → 1h ("TIES chip highlighted with
    `+1`"); `Menus and UI.md` → Decisions → When does the scoreboard increment.*
    *Testable:* on a Player Two win the Player Two column is the one marked as incremented
    and its value already counts the game just finished; on a tie the Ties column is.

12. **The surface states who goes first in the rematch.**
    *Source: `design_handoff_game_ui/README.md` → 1g ("Player One goes first next time.")
    and → 1h ("Player One goes first again — a tie doesn't pass it on."), which the handoff
    attributes to `Rules.md`.*
    *Testable:* the named player matches the player the engine reports as first for the
    next game under requirement 8, for all three outcomes.

13. **Every value on this surface comes from the active theme** — colors, backgrounds,
    fonts, mark/glyph art, sounds and animation timings. Nothing about game over is a
    hardcoded visual decision, and the hardcoded-theme-value test must still pass with this
    feature in place.
    *Source: `Game Board Design.md` → Everything Here Is Theme-Driven; `Theming.md` →
    Architectural Rule; `Tech Design.md` → Decisions → Do we add a test that fails on
    hardcoded theme values? (baseline starts at zero).*
    *Testable:* the theme-value scan reports no new violation from the files added by this
    feature.

14. **The whole flow works with animations off.** With the animations toggle off, the
    game-over state and the rematch reset are instant state changes — no animation, no fade
    or transition standing in for one — and the surface stays fully readable and its
    controls fully usable.
    *Source: `Animations.md` → Decisions → Animations off = instant state change ("no
    animation, no substitute effect, no fade or transition standing in for one"); →
    Decisions → Animations don't block input; `design_handoff_game_ui/README.md` →
    Interactions & behavior ("Every screen above is fully readable with animation off —
    that is the correctness test").*
    *Testable:* with animations off, the result is on screen in the same frame the game
    ends, and the rematch takes effect in the same frame it is tapped.

15. **Taking the rematch fires the haptic**, subject to the vibrate-on-touch setting, since
    it is a valid action. A tap that does nothing fires nothing.
    *Source: `Game Board Design.md` → Haptic Rule ("The haptic fires on every valid
    click"); `Menus and UI.md` → Settings Menu → Vibrate on Touch;
    `design_handoff_game_ui/README.md` → Interactions & behavior ("Haptic on every valid
    tap ... Haptics are an app setting, never theme-driven").*
    *Testable:* with vibrate on, the rematch control fires one haptic; with it off, none;
    an inert tap on the finished board fires none either way.

## Out of Scope

Named so the boundary is explicit. Each is specified elsewhere; do not specify it here.

- **Win, claim, cat-game and straight-draw detection, legal-move computation, the score as
  data, and the turn-order-across-games computation** — `P1-02-engine-rules.md`. This
  feature reads the engine's outcome and asks it to start the next game; it implements none
  of that logic.
- **The scoreboard's own layout, chips and turn indicator** —
  `P2-03-scoreboard-turn-indicator.md`. Requirements 11 and 12 cover only what the *result*
  surface says about the score, not how the persistent scoreboard row is drawn.
- **Writing the series to storage — the Hive box and the repository** —
  `P1-04-persistence.md`.
- **The open-games list, its cap (3 by default, 100 with the in-app purchase), and the
  delete action that frees a slot** — `P3-02-open-games-list.md`, with the storage half in
  `P1-04-persistence.md`. Requirement 7 requires only that a rematch consume no slot.
- **The in-game settings modal, quick actions, and the exit-to-main-menu path** —
  `P3-04-settings.md`. That the settings button at the top right is the way out of a game
  is already settled (`Menus and UI.md` → Decisions → How do you get back to the main menu
  from a game?); whether an exit control also sits *beside* Rematch is not — see OQ-2.
- **Win, claim and cat-game animations, and the `winGame` animation slot** —
  `P4-03-animations.md`. Requirement 14 constrains only the animations-off behavior.
- **Result sounds** — `P4-01-audio.md`.
- **Board and cell rendering, the three highlights, and the two-tap input gesture** —
  `P2-01-board-rendering.md` and `P2-02-move-input.md`. Requirement 2 only makes input
  inert; it does not respecify it.
- **Anything from `Alternative Game Styles.md`.** That is a declared parking-lot doc and
  explicitly not the game being built.

## Open Questions

> **Closed since the first draft:** *when does the score increment — at game end, or when
> the rematch is taken?* Settled as **at game end**, and promoted to requirement 4
> (`Menus and UI.md` → Decisions → When does the scoreboard increment). Note that the same
> conflict is still listed as OQ-2 in `P1-02-engine-rules.md`, which has not been revised.

### OQ-1 — Is game over a full result screen, a banner, or an overlay?

As worded in `Menus and UI.md` → Game Over → Rematch:

> Undecided: whether this is a full result screen, a banner, or an overlay on the finished
> board.

**The approved handoff has drawn one answer that the doc has not settled.**
`design_handoff_game_ui/README.md` draws game over as two modal cards over the finished
board — *1g — Modal: winner* and *1h — Modal: draw*, with the board still visible at 60%
behind a scrim — and its *Interactions & behavior* section states "**Game over** → 1g / 1h
overlays the finished board; the board stays visible behind." That is the overlay option of
the three the doc lists. This PRD does not treat the drawing as the decision: requirements
10–12 specify content, not form. Nothing else in this PRD depends on the answer.

### OQ-2 — What sits beside Rematch?

As worded in `Menus and UI.md` → Game Over → Rematch:

> ("Rematch is an option" implies at least one other choice sits next to it — presumably
> exiting to the main menu, which is also reachable via the top-right settings button.)

Recorded as stated, not as a decision. The handoff draws the presumption as real — 1g lists
a ghost **Exit to Main Menu** under REMATCH — but the doc has not settled that a second
control exists on this surface, and the settled exit route is the settings button
(`Menus and UI.md` → Decisions → How do you get back to the main menu from a game?).

### OQ-3 — Gaps found while writing this PRD

Flagged by the PRD author, not asked by the docs. Each is something an implementer would
otherwise decide by accident. None is resolved here.

- **What a finished game the players never rematched shows when it is resumed.** The score
  is no longer at stake: the increment now happens at game end (requirement 4), so such a
  game is already counted and walking away loses nothing. What is still unsettled is
  narrower — reopening that game from the open-games list, does the player get the finished
  board with the result surface again, or a board already reset and waiting for the first
  move of the next game? Requirement 6 makes the reset an effect of taking the rematch, so
  as the docs stand a resumed un-rematched game is still a finished game, and the question
  is what it looks like rather than what it counts.
- **Whether the game-over surface can be dismissed to look at the finished board.** The
  handoff keeps the board visible behind 1g/1h but, unlike the in-game settings sheet (1f),
  draws no close control on either. Whether a player can put the result aside to study how
  the game ended — and get it back — is unspecified.
- **Whether the top-right settings button is still live while the result is on screen.**
  `Menus and UI.md` settles that settings must be reachable *mid-game* and that it is also
  the way out; a finished game is not mid-game, and the docs do not say whether that button
  keeps working, is hidden, or is the intended exit route referenced in OQ-2.
