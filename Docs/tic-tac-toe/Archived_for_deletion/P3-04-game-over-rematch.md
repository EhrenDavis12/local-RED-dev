**Build-readiness: 93** · *self-assessed after B-2 was answered: actionability 19/20,
verifiability 19/20, decision completeness 18/20, interface precision 19/20,
self-containment 18/20 (was 88, 79, and 49 three rounds ago). **Nothing blocks this PRD.**
What holds it under a clean pass, none of it fixable from inside this file: the two button
**labels** are deliberately unwritten (copy is a separate ask — OQ-2), the `winGame`
animation moment is fenced out of wave 2 by `P2-04` req 27 (OQ-9), five theme values plus
one shape change are requested but not yet **authored** into `P1-03`'s schema (req 13). *The
fourth item is resolved: the confirmed-move save call req 9 depended on is **claimed by
`P3-02-move-input.md` req 36**, on the commit path its req 4 defines.*

# PRD: Game Over → Rematch

> **Status:** Draft · Source docs read: `Menus and UI.md`, `Game Overview.md`, `Rules.md`,
> `Game Board Design.md`, `Animations.md`, `Tech Design.md`, `Theming.md`, `roadmap.md`,
> plus the read-only reference asset `design_handoff_game_ui/README.md` (screens
> *1g — Modal: winner*, *1h — Modal: draw*, and → *Interactions & behavior*).
> `Alternative Game Styles.md` is a declared parking-lot doc and was read only to confirm
> it is out of scope — no requirement here comes from it.

**Wave:** P3.

> **Naming, stated once so nobody looks for a third behaviour.** The design docs call the
> mechanic a **rematch** (`Menus and UI.md` → *Game Over → Rematch*) and call the control
> that triggers it the **next game** button (→ Decisions → *What controls does the
> game-over result card carry?*). **They are the same thing under two names.** There is one
> behaviour — requirement 6 — reached by one button. This PRD uses "rematch" for the
> mechanic and "next-game control" for the button, and defines no third path.

**Dependencies:**

- `P1-02-engine-rules.md` — owns outcome detection, series state, the score and its
  increment, and turn order across games. This PRD codes against its `Board`,
  `GameOutcome` (its reqs 22, 37), `PlacementState.gameOver` (req 36), `Score`,
  `Board.startNextGame()` (req 34) and **`winningLine` (its req 43, added by user
  settlement — see the OQ-5 closure)**. It re-derives none of it.
- `P1-04-persistence.md` — owns `OpenGamesRepository`, `StoredGame` and `GameId` (its reqs
  21–25) and the save timing (its req 6). Requirement 9 codes against those and claims one
  call site its Out-of-Scope table left unclaimed. **Its req 21 also owns both timestamps:
  `save` stamps `updatedAt` itself and preserves the stored `createdAt`**, which is what
  closed OQ-10.
- `P1-03-theme-system.md` — owns the theme schema (`meta.schemaVersion` **8**). Requirement
  13 binds to its `surfaces.modal.*`, `surfaces.scrim.modal` and `surfaces.button.*` keys —
  all three unchanged across the v3→v8 bumps — and requests five values plus one shape
  change that would join its req 13(b) **authored** table.
- `P2-01-navigation.md` — owns routing. Requirement 5's exit control leaves through it;
  requirement 7 records that the next-game control does not.
- `P2-02-audio.md` — owns `AudioLayer`, `SoundMoment`, `audioLayerProvider`, the sound
  files and the mute gate (its reqs 2, 6), and publishes the two test doubles requirements
  16–17 assert against. **This PRD owns the two call sites** — requirement 16.
- `P2-04-animations.md` — owns `ThemedAnimation`, `AnimationMoment`,
  `AnimationCoordinator` and the interpreter (its reqs 6–7, 31) and the animations-off path
  (its reqs 19–20). Requirement 14 constrains the off path; **the game-over animation
  moment is fenced out of wave 2 — see OQ-9.**
- `P2-03-haptics.md` — the buzz requirement 15 fires on both card controls.
- `P3-01-board-rendering.md` — draws the finished board this surface sits over, dimmed.
- `P3-03-scoreboard-turn-indicator.md` — owns the persistent scoreboard strip.

**Note on source status:** `Menus and UI.md` carries the house banner *"Nothing here is
settled"* while also carrying a `## Decisions` section. Following the practice set by
`P1-02-engine-rules.md`, this PRD sources requirements from that doc's **Decisions** and
from the *Game Over → Rematch* section that those decisions point at.

## Problem

A game of Tic-Tac-Toe-Extreme currently has no ending. The engine can report that a player
has three claimed quadrants in a row, or that no quadrant remains open with nobody's line
on the big board (`Rules.md` → Winning the Game; → Edge Cases → Big board full with no
three-in-a-row), but nothing in the app tells the two players sharing the phone that it is
over, nothing counts the result, and there is no way to play the next one or to leave.

That gap breaks the unit of play the game is designed around. `Game Overview.md` → Session
Structure says the app *"isn't built around a single one-off game"* but around *"playing
several in a row on the same phone"*, with the scoreboard carrying across games so a
session becomes a running series. Without a game-over flow the scoreboard never moves, the
series never advances, and the finished board just sits there rejecting taps with no
explanation.

## Goal

When a game is won or drawn, the result is counted on that game's own scoreboard and a
result card is drawn over the dimmed finished board, telling the two players what happened
and offering them two ways forward: play the next game, or go back to the main menu.
Playing the next game resets the board and hands the first move to the winner — or, after a
tie, back to whoever went first in the tied game — and carries on inside the *same* open
game, so a session of many games accumulates into one series with one running score rather
than a pile of separate saved games.

## Requirements

### Ending a game, and entering the game-over state

These are two different things, and the difference is load-bearing. **Requirements 4 and
16(a) are bound to the single move that ends a game** and happen once, ever. Requirements
1–3 and 5 describe the *state* a finished game is in — a standing condition that is entered
again every time that game is reopened from storage, and that must therefore count nothing
and replay nothing.

1. **The game-over state is a function of the engine's reported outcome**, not of an event.
   The surface activates whenever `board.outcome != GameOutcome.inProgress` — equivalently
   `board.placementState == PlacementState.gameOver` — which is true both on the move that
   ends the game and on every later occasion the same finished game is rehydrated from
   storage. `GameOutcome.playerOneWins` and `GameOutcome.playerTwoWins` route to the winner
   presentation, `GameOutcome.tie` to the draw presentation; there is no third ending.
   *Source: `Rules.md` → Turn Structure 5, → Winning the Game, → Edge Cases → Big board
   full with no three-in-a-row; `P1-02-engine-rules.md` req 22 and its accessor req 37
   ("This is the accessor `P3-04-game-over-rematch.md` requirement 1 activates its
   game-over surface from, including after rehydration from storage"), and req 36 for
   `placementState == gameOver` holding exactly when `outcome != inProgress`.*
   *Testable:* driving a `Board` to each of the three terminal outcomes activates the
   matching presentation, and `inProgress` never activates one. **Rehydration:** a
   `StoredGame` read back through `OpenGamesRepository.readById` whose board is finished
   activates the state again while leaving `Score` untouched and firing no `SoundMoment`
   and no `AnimationMoment` — on every relaunch, any number of times.

2. **A finished board accepts no further moves.** No cell and no quadrant is playable once
   the game is over, and the two-tap select-then-confirm interaction is inert.
   *Source: `P1-02-engine-rules.md` req 20 ("The game is over; no further moves are
   legal"), and its req 42, under which `applyMove` throws
   `IllegalMoveReason.gameAlreadyFinished` rather than returning.*
   *Testable:* with `placementState == gameOver`, `legalMoves` is empty and taps on all 81
   cells produce no state change and no pending selection; no code path calls `applyMove`
   on a finished board.

3. **A straight draw is presented as a tie with no winner.** When **no quadrant remains
   open** — every quadrant is either claimed or a cat game — and no player has three
   claimed quadrants in a row, the result is a tie regardless of how many quadrants each
   player holds. Most-quadrants-claimed does not win; the count is irrelevant, and the
   game-over surface names no winner.
   *Source: `Rules.md` → Edge Cases → Big board full with no three-in-a-row → straight
   draw; `P1-02-engine-rules.md` req 21, whose wording this follows ("If **no quadrant
   remains open** (every quadrant is claimed or cat game)").*
   *Note for test authors:* this is deliberately **not** "all 81 cells are filled." A
   claimed quadrant closes with empty cells still inside it (`P1-02-engine-rules.md` req
   14), so a full-board cell check would never fire. Detection belongs to the engine
   (requirement 1); this requirement governs only how `GameOutcome.tie` is presented.
   *Testable:* a board reporting `GameOutcome.tie` with five quadrants claimed by one
   player, three by the other, and empty cells remaining inside claimed quadrants, reaches
   the draw presentation and never the winner presentation. On that same board
   `winningLine` is null (`P1-02` req 43), so the draw presentation has nothing to draw a
   line from and must not look for one.

4. **The score increments on the move that ends the game — once, ever.** The winner's
   column, or the **Ties** column on a straight draw, goes up by exactly one as part of
   resolving that move. The increment is bound to that move and to nothing else: not to
   entering the game-over state, not to re-entering it when a finished game is reopened,
   and not to taking the rematch. Leaving without taking it does not un-count the game. The
   engine performs it; this surface only reads `Score`.
   *Source: `Menus and UI.md` → Decisions → When does the scoreboard increment ("**At game
   end.** The winner's column, or Ties, increments as soon as the game is won or tied — not
   when a rematch is taken. Taking the rematch only resets the board."); → Decisions → What
   happens when a game ends?; → Game Over → Rematch; `Game Overview.md` → Session Structure
   ("The score increments at game end, not when continuing is taken"); `Game Board
   Design.md` → Scoreboard ("Increments when a game ends"); `Rules.md` → Edge Cases → "The
   Ties counter on the scoreboard goes up one"; `P1-02-engine-rules.md` req 27, which owns
   the increment and binds it to "the move that ends the game."*
   **Contradicted by the approved handoff — see the flag under Open Questions.** The docs
   win; the handoff is read-only.
   *Testable:* `Score` changes on the `applyMove` that ends the game, before any further
   input; reading that finished board back from storage ten times leaves all three counters
   unchanged; `Board.startNextGame()` leaves them unchanged; across a series of *n*
   finished games the three counters sum to *n* whether or not each was rematched and
   however often the app was relaunched.

5. **The result card carries exactly two controls, and the player chooses between them
   deliberately.**

   - **The next-game control** starts the next game in this series — the rematch mechanic,
     requirements 6–9. This is the **affirmative** action.
   - **The back-to-main-menu control** leaves the finished game and routes to the main
     menu, through `P2-01-navigation.md`. Leaving is safe and discards nothing: the game
     and its scoreboard are already on disk (requirement 9; `P1-04-persistence.md` req 11,
     *"leaving a game does not remove a stored game"*), and the series is resumable from
     the open-games list exactly as it stands.

   **The card is self-sufficient.** A player is never dependent on the in-game settings
   button to leave a finished game, whatever that button's liveness turns out to be. Nothing
   restarts the board automatically, and the result stays on screen until one of the two is
   pressed.
   *Source: `Menus and UI.md` → Decisions → **What controls does the game-over result card
   carry?** — "**The result card carries two buttons — one to start the next game, and one
   to go back to the main menu.**" *"On game over result card we should have a button for
   next game as well as back to main menu."* That Decision states the consequence directly:
   "the card is self-sufficient, so the player is never dependent on the settings button to
   leave a finished game." Also → Decisions → What happens when a game ends?; →
   Game Over → Rematch; `Game Overview.md` → Session Structure.*
   **Labels are not specified here** — the user named the two controls and no more; copy is
   a separate ask. See OQ-2.
   **Both controls' feedback is specified elsewhere in this PRD:** the haptic in
   requirement 15, the tap sound in requirement 16(b). This requirement is the inventory;
   those two are the call sites.
   *Testable:* the result card exposes exactly two enabled controls for every
   `GameOutcome`; with neither pressed, no `startNextGame()` call and no navigation occurs
   after an arbitrary wait; pressing the next-game control satisfies requirements 6–9;
   pressing the exit control routes to the main menu and leaves the stored record equal to
   what it was before the press.

   **Other PRDs may cite this requirement rather than re-deriving it.**
   `P3-03-scoreboard-turn-indicator.md` and `P2-01-navigation.md` each held a question
   about whether the top-right settings button stays live at game over. This requirement
   does not answer that — it removes what made it urgent. The exit path at game over is the
   card's own control, so the settings button's liveness is now a plain UI choice with no
   dead end behind it. `P2-01` has closed its OQ-12 against this requirement.
   **The exit control is now also the *only* way out of the game route at game over**, in a
   stronger sense than when this was written: `P2-01-navigation.md` req 23 disables the iOS
   back-swipe on `/game/:gameId`, and that block is a property of the route rather than of
   the game's liveness, so it holds over a finished board too. Nothing here changes — the
   card was already self-sufficient — but the claim that a player depends on no other
   affordance is now structural rather than a courtesy.

### Taking the rematch — the next-game control

6. **The next-game control calls `Board.startNextGame()` and does nothing else to the
   series.** All 81 cells are empty, all nine quadrants are unclaimed and open, and the new
   game begins in the free-choice state for its first player, with `Score` carried forward
   unchanged.
   *Source: `Menus and UI.md` → Game Over → Rematch ("Taking it resets the board for the
   next game"); → Decisions → What happens when a game ends?; → Decisions → When does the
   scoreboard increment ("Taking the rematch only resets the board"); `Game Overview.md` →
   Session Structure; `Rules.md` → Setup, → Placement Rules → First move;
   `P1-02-engine-rules.md` req 34 ("the engine side of what `P3-04-game-over-rematch.md`
   requirement 6 calls taking the rematch") and req 26.*
   *Testable:* after the next-game control is pressed, the board equals what
   `startNextGame()` returns — cells, quadrants, `lastMove` null, `placementState`
   `freeChoice`, `winningLine` null — and the three counters are identical to their values
   immediately before.

7. **The rematch continues in the same open game.** It does not create a second open game;
   the `GameId`, the opponent name and the running `Score` are the same record before and
   after, and it never consumes an open-game slot.
   *Source: `Menus and UI.md` → Game Over → Rematch ("The rematch continues in the **same
   open game** — same series, scoreboard intact. It does not start a second open game"); →
   Decisions → What does an open game hold?; → Decisions → How many open games do we keep?;
   `Game Overview.md` → Decisions → Scoreboard lifetime; `P1-04-persistence.md` req 8.*
   *Testable:* with the open-games list at its cap and one game finished, pressing
   next-game leaves `readAll().length` unchanged, the record's `GameId` unchanged, and the
   other records untouched.
   `P2-01-navigation.md` **requirement 17** holds the routing half: the next-game control
   performs no navigation and records zero navigator invocations. **The exit control is the
   opposite case** — it is the only navigating control on this surface (requirement 5).

8. **The rematch's first player follows the turn-order rule across games:** after a win,
   the winner of that game goes first; after a tie, the player who went first in the tied
   game goes first again — a tie does not pass the first-move advantage. This surface reads
   the result of `startNextGame()` rather than computing it; that method derives the first
   player from the finished game's `GameOutcome` and `firstPlayerThisGame`.
   *Source: `Rules.md` → Turn Order Across Games; → Decisions → Who goes first after a
   tie?; `Menus and UI.md` → Game Over → Rematch; `Game Overview.md` → Session Structure;
   `P1-02-engine-rules.md` reqs 25–26 and 34.*
   *Testable:* Player Two wins game 1 → the next board's `currentPlayer` is `Player.two`;
   game 2 ties → `Player.two` again; Player One wins game 3 → `Player.one`.

9. **Both state changes reach storage, and this requirement claims the rematch write.**
   Two writes, with two owners:

   - **The game-ending move** is a confirmed move, so it is covered by the settled rule
     that a game is written **after every confirmed move** (`P1-04-persistence.md` req 6,
     sourced to `Menus and UI.md` → Decisions → When is a game written to storage?). The
     call site is the move-commit path, and **`P3-02-move-input.md` req 36 claims it** —
     `P1-04` → Out of Scope → *Who calls save* now names that requirement in rows 1 and 2.
     This PRD named the gap and did not fill it; that PRD closed it in this wave, which is
     what makes testable (a) below assertable from both sides.
   - **Pressing next-game is not a move**, so no existing rule covers it. `P1-04`'s
     call-site table marks that row *"**Unclaimed** — `P3-04-game-over-rematch.md` req 9's
     territory."* **[PRD decision] This requirement claims it: the rematch path calls
     `OpenGamesRepository.save(StoredGame)` with the same `GameId` and the board returned
     by `startNextGame()`, as the new board is shown.** The alternative `P1-04` names —
     letting the next confirmed move cover it — leaves the state on disk lagging by one
     game, so a player who takes the next game and quits before moving reopens the
     *finished* board with the result still up, having already asked for a new one.
     Claiming the write costs one call and matches the reasoning behind the settled save
     rule ("nothing is ever lost to a crash or a force-quit"). Reversible: dropping this
     write reintroduces exactly that lag and nothing else.

   This is also what makes requirement 5's exit control safe: by the time either button is
   available, the finished game — increment included — is already on disk, so leaving
   performs no write and has nothing to lose.
   *Source: `Menus and UI.md` → Persistence; → Decisions → When is a game written to
   storage?; `P1-04-persistence.md` reqs 6, 8, 11 and its Out of Scope call-site table.*
   *Testable:* (a) end a game, rebuild the store from disk, `readById` — the record's
   `Score` shows the increment exactly once and its board reports the terminal
   `GameOutcome`; (b) press next-game, rebuild the store from disk without playing a move,
   `readById` — the record has the same `GameId`, a board equal to `startNextGame()`'s
   result, unchanged counters, an **unchanged `createdAt`**, and an **`updatedAt` later
   than the one the game-ending move's save wrote**; (c) press the exit control instead and
   the stored record is byte-identical to what (a) produced; (d) `readAll().length` is
   unchanged throughout.

   **What this write does to `updatedAt` is settled — OQ-10 is closed.** The user has
   settled that `StoredGame` carries **both `createdAt` and `updatedAt`**, that the
   open-games list is ordered **most-recent-first on `updatedAt`** (`P1-04-persistence.md`
   → Open Question 8, and its reqs 21 and 29), and — closing what this requirement raised —
   that **`OpenGamesRepository.save` stamps `updatedAt` itself, ignoring whatever the
   caller passes, and preserves the stored `createdAt`** (`P1-04` req 21). **This call site
   therefore makes no choice at all**: it passes the record carrying `startNextGame()`'s
   board, and the repository stamps. Neither timestamp is an argument this surface
   supplies, and the `createdAt` half follows from requirement 7 writing back the same
   record.
   **The player-visible effect, stated because it is a real behaviour of this control:**
   taking the rematch moves that game to the **top** of the open-games list, before a move
   is played in the new game. That falls out of the storage settlement rather than being
   decided here, and `P4-02-open-games-list.md` renders it unchanged — it sorts nothing
   (its req 2).

### What the game-over surface is, and what it communicates

**The form is settled: a result card drawn over the board, with the board dimmed behind
it.** Not a separate screen, not a banner — the finished position stays visible behind the
card. Requirements 10–12 are content and hold under any form; requirement 13 draws the
settled one.

10. **The outcome is stated in words, and the two outcomes are visually distinct.** A win
    names the winning player; a tie states that nobody won.
    *Source: `Menus and UI.md` → Decisions → What does the player see when a game ends?; →
    Decisions → What happens when a game ends?; `design_handoff_game_ui/README.md` →
    1g — Modal: winner ("Player One takes it!", card bordered in the winner's color) and →
    1h — Modal: draw ("Nobody wins this one!", neutral border, both players' glyphs at
    55%).*
    *Testable:* the three `GameOutcome` values produce three distinct on-screen strings,
    and the tie string names no player.
    Copy wording is fenced by requirement 20; see also OQ-4 and OQ-5.

11. **The scoreboard is shown as part of the result, already including the finished game,
    with the column that moved identifiable.** Per requirement 4 the increment happened on
    the ending move, so it is already reflected the first time this surface appears and
    every subsequent time it appears for the same game. The `+1` delta itself is fenced by
    requirement 19.
    *Source: `design_handoff_game_ui/README.md` → 1g ("the three score chips at 27/600
    with a `+1` under the incremented column") and → 1h ("TIES chip highlighted with
    `+1`"); `Menus and UI.md` → Decisions → When does the scoreboard increment.*
    *Testable:* on `playerTwoWins` the Player Two column is the one marked as incremented
    and its value already counts the game just finished; on `tie` the Ties column is.

12. **The surface states who goes first in the rematch.**
    *Source: `design_handoff_game_ui/README.md` → 1g ("Player One goes first next time.")
    and → 1h ("Player One goes first again — a tie doesn't pass it on."), which the handoff
    attributes to `Rules.md`.*
    *Testable:* the named player equals the `currentPlayer` of the board `startNextGame()`
    would return, for all three outcomes.

13. **The result is a themed card over a dimmed board, and every value it draws resolves
    through the active theme.** The board behind stays rendered and legible — the players
    can still read the finished position — under a scrim, with the card above it. Nothing
    here is a hardcoded visual decision, and `P1-05-theme-guard-test.md`'s scan must still
    pass with this feature in place.

    **Keys that already exist** in `P1-03-theme-system.md` req 15's schema, all `required`,
    all unchanged across the v3→v8 bumps, and attributed there to this PRD's reqs 10
    and 13:
    - `surfaces.modal.{fill,border,radius,shadow,winnerBorder}` — the result card. Now
      **shared**: `P1-03` records it as "reused by the delete confirmation," which is
      `P4-02` binding to this surface's keys, not a change to them.
    - `surfaces.scrim.modal` — distinct from `surfaces.scrim.settings`; the handoff draws
      the result at `0.62` and the settings sheet at `0.72`, so one shared scrim cannot
      serve both.
    - `surfaces.button.{primary,secondary}` — **the tiers are assigned, not left to the
      implementer:** the **next-game control takes `primary`** and the
      **back-to-main-menu control takes `secondary`**. Next game is the affirmative action
      that continues the session `Game Overview.md` → Session Structure is built around;
      leaving is the alternative. The handoff draws the same weighting on 1g (REMATCH
      primary, a ghost exit beneath it). This is a visible, permanent-looking choice to a
      player, so it is stated rather than inferred.

    **Values this surface draws that the schema does not yet carry — all of them
    *authored*, not transcribed.** `P1-03` req 13(b) splits `required` keys into values
    **transcribed** from the handoff and values **authored** because nothing exists to
    copy; its authored table currently holds two members, the destructive treatment and the
    animation keyframe magnitudes. **Every value below would join that table**, and that is
    the accurate framing: no drawing contains them, so nobody forgot to transcribe them —
    someone has to design them. Together they are one `meta.schemaVersion` bump under
    `P1-03` req 37 (currently **8**):
    - **board-behind opacity** — the finished board stays visible at 60%;
      `surfaces.menu.dimBehindOverlay` is the main menu's 35% and is a different value.
    - **winner-tint radial gradient** behind the card, resolved per player. `P1-03` v5
      defined the gradient *shape*, so this needs the values, not a new shape.
    - **result title type** (28/600) and **result score-chip type** (27/600) — both
      distinct from the scoreboard strip's chip type (22/600); three sizes, not one.
    - **draw glyph-pair opacity** — the ✕ / ○ pair at 55% in each player's color.
    - **`surfaces.modal.winnerBorder` needs per-player grain.** Requirement 10 needs the
      border resolved to the winning player's color and 1h needs a neutral counterpart; one
      key cannot serve three cases. `P1-03` has already set this precedent — its scoreboard
      chips split into `surfaces.scoreboard.chip.playerOne.*`, `.playerTwo.*` and `.ties.*`
      for exactly this reason ("per player, because the states are not shared").
      `winnerBorder` wants the same shape. Note this key is now shared with the delete
      confirmation, so the reshape has a second consumer to keep working.

    **Not requested, and deliberately so: spacing and padding.** The card's internal
    padding, its gaps and its inset from the screen edge are **code constants, not theme
    values**, per `Theming.md` → Decisions → *Does a theme control spacing and padding?* —
    "**No. Spacing and layout numbers are fixed in the code, not theme-controlled — for
    now**," because the theme-guard test cannot distinguish a themed gap from an incidental
    one. `P1-03` v7 removed every spacing and padding key from the schema, so this is not
    merely unrequested — there is no such key to bind to, and this PRD's key list names
    none. Radii, type and color stay themed; only the spacing numbers are code.

    *Source: `Menus and UI.md` → Decisions → What does the player see when a game ends? —
    "**A result card drawn over the board, with the board dimmed behind it** — not a
    separate screen and not a banner," which also names the scrim, the board-behind opacity
    and the card's own fill/border/radius as "real values that need a home";
    `Game Board Design.md` → Everything Here Is Theme-Driven; `Theming.md` → Architectural
    Rule and → Decisions → Does a theme control spacing and padding?; `Tech Design.md` →
    Decisions → Do we add a test that fails on hardcoded theme values?;
    `P1-03-theme-system.md` req 13(b) (transcribed vs authored), req 15 (`surfaces`) and
    req 37 (schema versioning); `design_handoff_game_ui/README.md` → 1g, 1h, Design tokens.
    The handoff's numbers are Neon's authored values, quoted to identify **which** keys are
    needed; they constrain no other theme.*
    *Testable:* the theme-guard scan reports no new violation from this feature's files;
    every color, radius and type value this surface draws resolves to a named key; with the
    result on screen the board widget is still built and rendered, not replaced or
    unmounted — including when the board beneath is showing free-choice highlights, which
    the card must remain legible over.

14. **The whole flow works with animations off.** With the toggle off, the game-over state
    and the rematch reset are instant — no animation and no substitute effect, fade or
    transition standing in for one — and the surface stays fully readable and both controls
    fully usable.
    *Source: `Animations.md` → Decisions → Animations off = instant state change;
    `P2-04-animations.md` **reqs 19–20** (with the toggle off, `begin` returns null, the
    new state is fully rendered in the frame it changed, and the off path "is the absence
    of one").*
    *Testable:* with the toggle off, the result is rendered in the frame the game ends and
    the next game takes effect in the frame the control is pressed; no tween or opacity
    ramp is scheduled by this feature's code.

15. **Both card controls fire the haptic**, subject to the vibrate-on-touch setting, since
    both are valid actions. A tap that does nothing fires nothing.
    *Source: `Game Board Design.md` → Decisions → **Does the haptic fire on non-board
    controls?** — "**Yes — every valid tap buzzes, anywhere in the app.** Menu buttons,
    theme rows, settings toggles, **the game-over card's controls**, the settings gear —
    not only board cells"; → Haptic Rule ("The haptic fires on every valid click");
    `Menus and UI.md` → Settings Menu → Vibrate on Touch.*
    *Testable:* with vibrate on, each control fires exactly one haptic per press; with it
    off, none; an inert tap on the finished board fires none either way.

### Firing this surface's sounds

Two call sites, both this PRD's. `P2-02-audio.md` owns the moment enum, the sound file and
the mute gate; **it does not own the calls** — its req 6 makes a control's tap reaching
`play` exactly once a call-site fact belonging to each calling PRD, and its table names
this PRD for both moments below. Neither call reads a `sound` key or checks the setting:
the gate lives inside the layer, so both fire unconditionally.

16. **This surface fires exactly two sound moments.**

    **(a) `winGame`, on the move that wins the game — exactly once.**
    `ref.read(audioLayerProvider).play(SoundMoment.winGame)`. Like the increment in
    requirement 4, the call is bound to the ending **move**, not to the game-over state —
    re-entering that state by reopening a finished game (requirement 1) plays nothing, on
    any relaunch. A drawn game fires it never (requirement 17).
    *Source: `Animations.md` → Where Animations Fire, which lists *"Winning the whole
    game"* among the **moments** — a moment, not a standing state; `Theming.md` → What a
    Theme Controls → Audio; `P2-02-audio.md` req 6, whose table names `winGame` → this
    requirement.*

    **(b) `buttonTap`, once per press of either card control.**
    `ref.read(audioLayerProvider).play(SoundMoment.buttonTap)` from the next-game control
    and from the back-to-main-menu control alike — the same moment, the same one sound,
    no per-control variation.
    *Source: `Theming.md` → Decisions → **Do non-board controls make a sound?** — "**Yes —
    one tap sound, everywhere.** Every button, row and toggle plays the same short tap
    sound: menu buttons, theme rows, settings toggles, **the game-over card's two
    controls**, the trash button and the modal's Yes and No"; `P2-02-audio.md` req 6, whose
    table names this PRD among `buttonTap`'s call-site owners and states that `buttonTap`
    is "one moment and one sound file, not a family."*
    This mirrors requirement 15 deliberately: the same two controls, the same two channels,
    settled by the same symmetry argument the haptic decision uses.

    *Testable (both parts):* in a widget test installing the layer double through
    `ProviderScope(overrides: [audioLayerProvider.overrideWithValue(FakeAudioLayer())])` —
    a winning move records exactly one `SoundMoment.winGame`; pressing either control
    records exactly one `SoundMoment.buttonTap` per press; reopening a finished game
    records nothing at all; a drawn game records no `winGame`. Neither call branches on the
    sound setting, so the recorded sequence is identical with sound on and off.

    **⚠ Which double — every assertion in this PRD means `FakeAudioLayer`**
    (`test/support/fake_audio_layer.dart`), the double that **replaces the layer** and so
    records which *moments were requested*. None may be asserted against
    `RecordingOneShotSink` (`test/support/recording_one_shot_sink.dart`), which sits
    *below* the layer and records only what reached the player **after the mute gate**.
    Every claim here is about what the layer was asked for — the mute path is `P2-02`'s,
    not this surface's — so the sink would answer a different question: with sound muted it
    records nothing for *any* outcome, and could not distinguish a correctly silent draw
    from a muted win. `P2-02` req 16 carries the same warning from its side: choosing
    wrongly between the two produces a test that **fails a correct implementation**.

    **Co-occurrence is expected, not a defect.** One press of next-game produces
    `buttonTap`, and the move that follows produces `placeMark`; a winning move produces
    `placeMark`, `claimQuadrant` and `winGame` together. `P2-02`'s OQ-1 is fenced on "play
    all," so multiple sounds from one gesture is the specified behaviour. The first two of
    those are `P3-02`'s call sites, not this PRD's.

    **The matching animation moment is fenced out of wave 2 — OQ-9.**

### Stated defaults — reversible [PRD decision]

Each fences a question that would otherwise block the build, in the pattern
`P2-04-animations.md` req 27 sets. None is a ruling: each names what ships now and what
reverses it.

17. **The draw is silent and still this wave.** `GameOutcome.tie` fires no outcome
    `SoundMoment` and no `AnimationMoment`. No slot exists for it — `P2-02-audio.md` req 6
    and `P2-04-animations.md` req 23 name `placeMark`, `claimQuadrant`, `catGame`,
    `winGame`, (audio) `buttonTap` and (animation) `activeQuadrant`, `lastMove`, and
    `catGame` is the *small*-board case (`Game Overview.md` → Terminology), not the
    big-board straight draw. **This governs the result, not the controls:** the card's two
    buttons still fire `buttonTap` on a drawn game exactly as on a won one
    (requirement 16(b)). Reversed by adding a draw moment to those inventories. See OQ-7.
    *Testable:* a drawn game records **zero `winGame` requests against `FakeAudioLayer`**
    — not against `RecordingOneShotSink`; see the ⚠ note under requirement 16 — and one
    `buttonTap` per control press.

18. **A resumed un-rematched game shows the finished board with the result card.** This is
    what requirements 1 and 6 already produce — the state is finished, and only the
    next-game control resets it — stated so an implementer does not invent an auto-reset on
    resume. The player is not stuck either way: requirement 5's two controls are both
    present on a resumed result. Reversed by a decision that resuming a finished game
    starts the next one. See OQ-3.
    *Testable:* reopening a finished game renders the result card with both controls over
    the finished board, and calls `startNextGame()` zero times.

19. **The `+1` delta is drawn only when the result appears as a consequence of the ending
    move in this session.** A rehydrated result shows the three counters without a delta,
    because `+1` reads as "just now" and a game finished last week did not just happen.
    Requirement 11's identifiability holds either way — the incremented column is still
    identifiable, by highlight rather than by delta. Reversed by drawing the delta
    unconditionally. See OQ-8.
    *Testable:* the delta is present on the ending move's presentation and absent on the
    same game's result after a store rebuild.

20. **Player-facing copy uses the design docs' vocabulary, and omits what nothing supplies.**
    The draw is described as a tie / straight draw, never as a "cat game" (OQ-4), and no
    string in the shipped copy names *which* line won.
    **The second half is now a copy fence rather than a capability limit, and the change is
    worth stating.** It previously read *"because `GameOutcome` does not expose it"* — that
    reason is gone. **The user has settled that the engine publishes the winning line**:
    `P1-02-engine-rules.md` req 43's `List<int>? get winningLine` returns the three
    big-board quadrant indices on a won game and null otherwise, so the handoff's *"Three
    boards in a row, straight down the middle"* is implementable as drawn. What remains
    unwritten is the **copy**, which is a separate ask under requirement 5 and OQ-2 — this
    default ships the docs' vocabulary until that copy lands, rather than inventing a
    sentence to spend the new value on.
    **Reading `winningLine` correctly, for whoever writes that copy:** branch on `outcome`
    (`P1-02` req 37) and read the line only inside the two winning branches. Null means
    *in progress* on one board and *tie* on another, and this accessor cannot tell them
    apart — `P1-02` req 43 states that explicitly. And when one claim completes two lines at
    once the engine returns exactly one of them (`P1-02` OQ-8), which a sentence naming
    "the" line would quietly assume away.
    Reversed by a copy decision in the docs. **No engine requirement is needed any more.**
    *Testable, as this default stands:* no string in this feature contains "cat game"; no
    string describes a row, column or diagonal. The second assertion lapses the moment the
    copy decision lands and is not evidence that the line is unavailable.

21. **Only the two card controls give feedback; nothing else on this surface does.** No
    other element fires a haptic or a sound.
    **No longer a fence — the underlying question is settled.** Earlier drafts held this
    open against `P2-03-haptics.md` → OQ-2. `Game Board Design.md` → Decisions → *Does the
    haptic fire on non-board controls?* and `Theming.md` → Decisions → *Do non-board
    controls make a sound?* both answer **yes, everywhere**, and both name the game-over
    card's controls explicitly. This requirement now just scopes that to the two controls
    requirement 5 puts on the card.
    *Testable:* per press, the surface fires exactly one haptic and one `buttonTap`, and
    only from the next-game and back-to-main-menu controls.

## Out of Scope

- **Outcome detection, legal moves, the score as data, the increment, turn order, and the
  winning line** — `P1-02-engine-rules.md` (reqs 20–22, 25–27, 34, 36–37, 43). Requirement 4
  states *when* the increment lands because this surface depends on it, not because this
  layer performs it; requirement 20 reads `winningLine` and does not compute it.
- **The persistent scoreboard strip and turn indicator** —
  `P3-03-scoreboard-turn-indicator.md`.
- **The repository, the Hive box, and the confirmed-move write's call site** —
  `P1-04-persistence.md` and `P3-02-move-input.md` **req 36**, on the commit path its req 4
  defines. Requirement 9 claims only the rematch write.
- **`StoredGame`'s two timestamp fields, their semantics, which side stamps them on a save,
  and the list's sort order** — `P1-04-persistence.md` reqs 21 and 29, settled at its Open
  Question 8 and the stamping settlement recorded there. This PRD defines none of it;
  requirement 9 states the consequence for this call site and OQ-10 is closed against it.
- **Routing itself** — `P2-01-navigation.md`. Requirement 5 states that the exit control
  goes to the main menu; how the route is performed, what the main menu shows on arrival,
  and whether the back-swipe is available on the game route (its req 23) are that PRD's.
- **The open-games list, its cap, the delete action and its confirmation** —
  `P4-02-open-games-list.md`, with the storage half in `P1-04-persistence.md` and the cap
  in `P1-07-entitlements.md`. That flow reuses `surfaces.modal` and `surfaces.scrim.modal`;
  its own `surfaces.destructive.*` and `icons.trash` keys are not drawn by this surface and
  reach nothing here.
- **The in-game settings modal and the settings button's own behavior** —
  `P4-04-settings.md` and `P3-03-scoreboard-turn-indicator.md`. Requirement 5 makes the
  card self-sufficient; it does not decide whether that button is live at game over.
- **What the sounds *are*, how they load and play, the asset path and extension, the mute
  gate, and whether two sounds may overlap** — `P2-02-audio.md`. Requirement 16 fires two
  moments; that PRD owns everything downstream of the request, which is exactly why its two
  doubles are not interchangeable.
- **`placeMark` and `claimQuadrant`** — `P3-02-move-input.md`'s call sites, even on the
  move that ends the game.
- **The animation machinery and what a `winGame` animation would be** —
  `P2-04-animations.md`. This PRD fires no animation moment — OQ-9. **The engine now
  publishes the winning quadrants (`P1-02` req 43), which makes a winning-line highlight
  expressible; it does not schedule or design one, and neither does this PRD.**
- **Board and cell rendering and the two-tap gesture** — `P3-01-board-rendering.md`,
  `P3-02-move-input.md`. Requirement 13 requires only that the board stay rendered behind
  the card; how it is drawn — including the free-choice highlight it may be showing, and
  anything it might one day draw from `winningLine` — is that PRD's.
- **The on-board legend and hint** — `P3-05-how-to-play.md`.
- **Anything from `Alternative Game Styles.md`.**

## Blocking — needs the user

**None.** Both blocking items are answered: B-1 (the form) and B-2 (the compound dead end).
The only thing still awaiting a person is the two button **labels**, and that is copy, not
a decision this PRD is blocked on — the requirement is complete without them and OQ-2 holds
the ask.

## Open Questions

> **Closed since the first draft:**
> - *When does the score increment* — settled as **at game end**, requirement 4;
>   `P1-02-engine-rules.md` OQ-2 is closed there too (its reqs 26–27).
> - *Where the save is written* — settled by `P1-04-persistence.md` req 6 (**after every
>   confirmed move**) and claimed for the rematch by requirement 9.
> - *Is game over a screen, a banner, or an overlay* (was OQ-1, was Blocking B-1) —
>   settled as a **result card over the dimmed board**, now cited in requirement 13 from
>   `Menus and UI.md` → Decisions → *What does the player see when a game ends?*. Worth
>   recording *how* it closed: requirement 13 had already been written against that
>   reading, naming a scrim, a board-behind opacity and a card border — values that exist
>   under no other option. That is why this PRD's earlier claim that "nothing else depends
>   on the answer" was false, and why the Decision **confirmed what requirement 13 was
>   built on rather than changing it**.
> - *Can a finished game become a dead end* (was OQ-6, was Blocking B-2) — **no.** The card
>   carries its own exit (requirement 5), so the dead end is impossible regardless of the
>   settings button. This also closes what was OQ-3's third bullet, and the same question
>   as held in `P3-03-scoreboard-turn-indicator.md` → Open Question 2 and
>   `P2-01-navigation.md` → Open Question 12 — the latter has already closed against
>   requirement 5, and the former may do the same.
> - *Do the card's controls buzz and make a sound* — **yes, both.** Settled by
>   `Game Board Design.md` → Decisions → *Does the haptic fire on non-board controls?* and
>   `Theming.md` → Decisions → *Do non-board controls make a sound?*, each naming this
>   card's controls. Requirements 15 and 16(b) are the call sites; requirement 21 is no
>   longer a fence. This also removes a circular gap: an earlier draft of requirement 16
>   said `buttonTap` was `P2-02`'s to say while `P2-02` req 6's table named this PRD, so
>   neither fired it.
> - *Can the winner copy name which line won* — **yes, the value now exists.** Settled by
>   the user as `P1-02-engine-rules.md` req 43. See OQ-5, kept as a closed stub because
>   requirement 20 and `P1-02` both cite it.
> - *Does the rematch write stamp `updatedAt`* — **the caller does not choose; `save`
>   stamps.** Settled by the user one layer down, in `P1-04-persistence.md` req 21. See
>   OQ-10, kept as a numbered stub.

> **Flagged contradiction — the approved handoff still carries the losing reading.**
> `design_handoff_game_ui/README.md` → *Interactions & behavior* states: **"REMATCH resets
> the board, increments the right column, and stays in the same save slot."** The middle
> clause is the rematch-increments reading that `Menus and UI.md` → Decisions → *When does
> the scoreboard increment* settled against. **The docs win; requirements 4 and 6 are
> correct as written, and that sentence is stale.** Recorded rather than fixed because the
> handoff is read-only — and a code writer building this surface reads that same section
> for the scrim, board opacity and haptic rules that requirements 13–15 cite.

### OQ-2 — What the two controls are called

`Menus and UI.md` → Decisions → *What controls does the game-over result card carry?*
settles that there are two and what each does; it does not name them. **This PRD writes no
labels**, deliberately — copy is a separate ask, and a plausible-sounding invention here
would be indistinguishable from a decision. The handoff draws **REMATCH** and a ghost
**Exit to Main Menu** (1g), which is evidence of weighting, not of wording — and the doc
calls the first control "next game" while calling the mechanic "rematch," so even the
handoff's label is not automatically the answer. Requirement 13 fixes the button *tiers*;
requirement 5 fixes the *behaviours*; requirements 15 and 16(b) fix their *feedback*; only
the strings are open.

### OQ-3 — Gaps found while writing this PRD

Flagged by the PRD author, not asked by the docs.

- **What a finished game the players never rematched shows when it is resumed.** Fenced by
  requirement 18 (it shows the finished board and the result card, both controls live). The
  score is not at stake — requirement 4 already counted it and reopening counts nothing
  further — and neither is the player's ability to leave, since requirement 5 puts an exit
  on the card. What remains is only whether resuming should instead start the next game
  outright, which is now a preference rather than a defect.
- **Whether the result card can be dismissed to look at the finished board.** The board is
  visible behind it by construction, which softens this — but, unlike the settings sheet
  (1f), neither 1g nor 1h draws a close control, so whether the card can be put aside
  entirely is still unspecified. Nothing here assumes one, and nothing depends on it now
  that the card carries both ways forward.
- ~~Whether the top-right settings button is still live while the result is on screen.~~
  **Closed** — see the closure note above. The card is self-sufficient, so this is a plain
  UI choice with no dead end behind it.

### OQ-4 — The draw modal's copy calls the big-board draw a "cat game"

`design_handoff_game_ui/README.md` → *1h* words the result as *"The big board filled up
with no three in a row. **Cat game.**"* That cuts against settled terminology:
`Game Overview.md` → Terminology defines a **cat game** as *"a small board filled with no
winner"*, and `Rules.md` → Edge Cases names the big-board case a **straight draw**.
Requirement 20 fences this — the shipped copy uses the docs' vocabulary — and the handoff
is read-only, so the wording question stays with the docs.
`P3-05-how-to-play.md` raises the same vocabulary split for player-facing copy generally.

### OQ-5 — CLOSED by the user: the engine exposes the winning line

*Was: the winner modal's copy names* which *line won, and the engine cannot supply it.*

`design_handoff_game_ui/README.md` → *1g* draws *"Three boards in a row, straight down the
middle."* This PRD recorded that as unimplementable, because `P1-02-engine-rules.md` reqs 22
and 37 exposed only `GameOutcome` and never the winning triple, and noted that naming the
line would need a new engine requirement.

**The user has settled it: `P1-02-engine-rules.md` req 43 adds `List<int>? get winningLine`
to the engine's published surface** — the three big-board quadrant indices of the completed
line on a won game, and **null** otherwise, including on a straight draw and on any
in-progress board. It lands in wave 1 alongside the rest of the engine, so it is available
before this surface is built rather than after.

**What this changes here:** requirement 20's omission of the line is now a **copy** fence
(the copy is unwritten — OQ-2) rather than a capability limit, and it says so; requirement 3
records that a drawn board's `winningLine` is null, so the draw presentation must not go
looking for one; the dependency list and Out of Scope name the accessor. **What it does not
change:** no string in this feature names a line today, and nothing here decides that one
should. Whoever writes the copy inherits two cautions `P1-02` req 43 states — null is
ambiguous between *in progress* and *tie* so the branch is on `outcome`, and a claim that
completes two lines at once yields exactly one of them (`P1-02` OQ-8).

**Kept as a numbered heading** because requirement 20 and `P1-02` req 43 both cite it.

### OQ-7 — What does a *tie* sound and look like?

Fenced by requirement 17: no outcome sound and no animation, though the card's two controls
still buzz and click like any other button. Whether the draw gets its own moment, reuses
`catGame` (which OQ-4 shows is the wrong word for it), or stays deliberately quiet is
unsettled — as is whether `Animations.md` → Scope For Now (*"animations apply to the
player's marker"*) even permits a result-card animation at all.

### OQ-8 — Should the `+1` delta show on a re-shown result?

Fenced by requirement 19 to the ending move's presentation only. The docs describe no delta
at all; the `+1` exists solely in the handoff. If a resumed finished game should instead
show a reset board (OQ-3, requirement 18), the question disappears.

### OQ-9 — The `winGame` animation moment is fenced out of wave 2

Recorded as a boundary, not a requirement, because nothing this PRD wrote could be honoured
in this wave. Two of the three blocks named earlier are gone:

- **The theme schema can express it.** `P1-03-theme-system.md` req 15 describes motion
  rather than naming a behaviour: `animation.<moment>.duration`,
  `animation.<moment>.repeat.{count,mode}`, and `tracks[]` carrying `property`, `easing`,
  optional `delay` and `keyframes[].{at,value}` over a closed property set.
- **The runtime can execute it.** `P2-04-animations.md` req 31 specifies
  `lib/animation/interpreter.dart` concretely against that schema — one
  `AnimationController` per animation, driven by `duration` and `repeat`, with **no table
  of known animation names and no branch on a behaviour string**. The earlier blocker, that
  `glow-pulse` was an unimplemented named type, no longer exists as a concept.

What still blocks it:

- **`P2-04` req 27 fences wave 2 to `placeMark` alone.** `AnimationCoordinator.begin`
  returns null for the other five moments including `winGame`, and *"no `ThemedAnimation`
  wrapping a quadrant, a highlight or a game-over surface is built in this wave"* — this
  surface by name. That PRD is explicit that the fence is about which *moments* play, not
  about what the interpreter can execute, so this is a scheduling boundary, not a
  capability gap.
- **`ThemedAnimation` takes no target parameter** (`P2-04` req 6 — `moment`, `trigger`,
  `child`): the animated thing is the wrapper's own child. Even unfenced, nothing in this
  PRD or the handoff says *what* on the result card would move — the card, the winner's
  mark, the score chip — so a requirement to "fire the `winGame` animation" would still not
  tell an implementer what to wrap. **This is the one part that is this PRD's to answer**,
  and it should be answered when the moment is unfenced rather than guessed now.
  **One candidate target is no longer this PRD's at all**, and that is new: with
  `P1-02` req 43 publishing the winning quadrants, an animation that highlights **the
  winning line on the board** is expressible, and the board is `P3-01-board-rendering.md`'s
  surface rather than this card's. The user records that highlight as the likely consequence
  of the settlement. **Nothing is designed here or there** — it is recorded so that whoever
  unfences the moment knows the target may not live on this card.
- **The magnitudes are not authored.** `P1-03` req 13(b) lists
  `animation.<moment>.tracks[].keyframes[].value` in its **authored** table — *"the handoff
  gives durations, easings and loop flags but never says how far."*

Requirement 14's animations-off path is unaffected and stays testable: with the toggle off
the behavior is identical to `lib/animation/` being absent, which is today's state. The
sound half (requirement 16) is blocked by none of this and ships now.

### OQ-10 — CLOSED by the user: `save` stamps `updatedAt`, so a rematch moves to the top

*Was: does the rematch write stamp `updatedAt`, or carry the stale value?*

Raised because `P1-04-persistence.md` → Open Question 8 settled the two fields and the sort
order while leaving the first **non-move** write to decide what happened to `updatedAt`, and
requirement 9 is that first caller.

**The user settled it one layer down, which removes the choice rather than making it.**
`OpenGamesRepository.save` **stamps `updatedAt` itself, ignoring whatever the caller
passes**, and **preserves the stored `createdAt`**, discarding an incoming one
(`P1-04-persistence.md` req 21). Neither timestamp is an argument this or any other call
site supplies, so there is no per-caller answer to give.

**What that means here:** the rematch write stamps, so **taking the rematch moves that game
to the top of the open-games list** (`P1-04` req 29's most-recent-first order) before a move
is played in the new game. That is the "stamp now" reading of the two this question set out
— reached by the repository owning the field rather than by this surface choosing.
Requirement 9 states the consequence, and its testable (b) now asserts the advanced
`updatedAt` and the unchanged `createdAt` rather than being written to be indifferent.
`P4-02-open-games-list.md` is unaffected: it sorts nothing (its req 2) and renders whatever
order `readAll()` returns.

**Kept as a numbered stub** because requirement 9 and `P1-04-persistence.md` → Open
Question 8 both cite this number.
