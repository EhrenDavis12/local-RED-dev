# PRD: Game Over → Rematch

> **Status:** Draft · Source docs read: `Menus and UI.md`, `Game Overview.md`, `Rules.md`,
> `Game Board Design.md`, `Animations.md`, `Tech Design.md`, `Theming.md`, `roadmap.md`,
> plus the read-only reference asset `design_handoff_game_ui/README.md` (screens
> *1g — Modal: winner*, *1h — Modal: draw*, and → *Interactions & behavior*).
> `Alternative Game Styles.md` is a declared parking-lot doc and was read only to confirm
> it is out of scope — no requirement here comes from it.

**Wave:** P3.

**Dependencies:**

- `P1-02-engine-rules.md` — owns outcome detection (win / straight draw), series state,
  the score and when it increments, and the turn-order-across-games rule. This PRD consumes
  that; it re-derives nothing.
- `P1-04-persistence.md` — owns writing the series to storage. Requirement 9 below
  restates that boundary rather than specifying storage.
- `P1-03-theme-system.md` — every value on this surface resolves through the active theme.
  Requirement 13 below enumerates the slots this surface needs, for that PRD's inventory.
- `P2-02-audio.md` — defines the `winGame` sound; requirement 16 below is what fires it.
- `P2-04-animations.md` — defines the `winGame` animation and the animations-off path;
  requirement 16 fires it and requirement 14 constrains the off path.
- `P2-03-haptics.md` — the buzz requirement 15 fires on the rematch control.
- `P3-01-board-rendering.md` — draws the finished board that this surface sits with or
  over.
- `P3-03-scoreboard-turn-indicator.md` — owns the scoreboard's own display; this PRD only
  specifies what the game-over surface must communicate about the result.

**Note on source status:** `Menus and UI.md` carries the house banner *"Nothing here is
settled"* while also carrying a `## Decisions` section. Following the practice set by
`P1-02-engine-rules.md`, this PRD sources requirements from that doc's **Decisions** and
from the *Game Over → Rematch* section that those decisions point at, and leaves everything
that section explicitly marks *"Undecided"* in **Open Questions**.

## Problem

A game of Tic-Tac-Toe-Extreme currently has no ending. The engine can report that a player
has three claimed quadrants in a row, or that no quadrant remains open with nobody's line
on the big board (`Rules.md` → Winning the Game; → Edge Cases → Big board full with no
three-in-a-row), but nothing in the app tells the two players sharing the phone that it is
over, nothing counts the result, and there is no way to play the next one.

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

### Ending a game, and entering the game-over state

These are two different things, and the difference is load-bearing. **Requirements 4 and 16
are bound to the single move that ends a game** and happen once, ever. Requirements 1–3 and
5 describe the *state* a finished game is in — a standing condition that is entered again
every time that game is reopened from storage, and that must therefore count nothing and
replay nothing.

1. **The game-over state is a function of the engine's reported outcome**, not of an event.
   It is active whenever the engine reports the game as won by Player One, won by Player
   Two, or a tie — which is true both on the move that ends the game and on every later
   occasion the same finished game is rehydrated from storage and shown again. Both
   outcomes lead to the game-over flow; there is no third ending.
   *Source: `Rules.md` → Turn Structure 5, → Winning the Game, → Edge Cases → Big board
   full with no three-in-a-row; `P1-02-engine-rules.md` req 22 (the engine reports the
   outcome as one of: in progress, won by Player One, won by Player Two, tie).*
   *Testable:* driving the engine to each of the three terminal outcomes activates the
   game-over state, and an in-progress game never activates it. **Rehydration:** closing a
   finished game and reopening it from the open-games list activates the state again while
   leaving all three counters exactly as they were and firing no sound and no animation —
   and does so on every relaunch, any number of times.

2. **A finished board accepts no further moves.** No cell and no quadrant is playable once
   the game is over, and the two-tap select-then-confirm interaction is inert.
   *Source: `P1-02-engine-rules.md` req 20 ("The game is over; no further moves are
   legal"), which sources `Rules.md` → Winning the Game.*
   *Testable:* after the game ends, taps on every one of the 81 cells produce no state
   change and no pending selection.

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
   (requirement 1); this requirement governs only how that outcome is presented.
   *Testable:* a big board with no open quadrants on which one player holds five quadrants
   and the other three, with no line and with empty cells remaining inside claimed
   quadrants, reaches the tie presentation and never the winner presentation.

4. **The score increments on the move that ends the game — once, ever.** The winner's
   column, or the **Ties** column on a straight draw, goes up by exactly one as part of
   resolving that move. The increment is bound to that move and to nothing else: not to
   entering the game-over state, not to re-entering it when a finished game is reopened,
   and not to taking the rematch. Leaving without taking the rematch does not un-count the
   game.
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
   *Testable:* the counter moves on the ending move, before any further input; reopening
   that finished game from storage ten times leaves all three counters unchanged; taking
   the rematch afterwards leaves them unchanged; across a series of *n* finished games the
   three counters sum to *n* whether or not each was rematched and however often the app
   was relaunched.

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
   board**"); `Rules.md` → Setup, → Placement Rules → First move; `P1-02-engine-rules.md`
   req 26 ("It **leaves the score untouched**").*
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
   `P2-01-navigation.md` requirement 10 holds the routing half of this: taking the rematch
   performs no navigation.

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
   series record** — neither is applied to screen state only, and neither writes a second
   record. How and *when* the write happens is `P1-04-persistence.md`'s (its reqs 8 and 9);
   this PRD requires only that neither step bypass it. Persisting a finished game is what
   makes requirement 1's rehydration case real, and requirement 4 is what keeps it from
   costing a second increment.
   *Source: `Menus and UI.md` → Persistence (table: scoreboard and game in progress both
   persist); `P1-04-persistence.md` req 8 ("A rematch continues in the same stored open
   game ... does not create a second stored record").*
   *Testable:* end a game and take a rematch, then rebuild the store from disk through
   whatever save point `P1-04-persistence.md` defines — the restored record shows the
   increment applied exactly once and the reset board, with the correct first player, and
   the stored open-game count is unchanged. **This test cannot be written until the save
   call site is named — see OQ-3.** It deliberately does not assume a write happens
   immediately at game end or at the rematch tap; that is unsettled in `P1-04`, and this
   PRD does not settle it by testable.

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
    Two details of the handoff's own copy sit unsettled against the docs — see **OQ-4** and
    **OQ-5**. Neither is required here.

11. **The scoreboard is shown as part of the result, already including the finished game,
    with the column that moved identifiable.** Per requirement 4 the increment happened on
    the ending move, so it is already reflected the first time this surface appears and
    every subsequent time it appears for the same game.
    *Source: `design_handoff_game_ui/README.md` → 1g ("the three score chips at 27/600
    with a `+1` under the incremented column") and → 1h ("TIES chip highlighted with
    `+1`"); `Menus and UI.md` → Decisions → When does the scoreboard increment.*
    *Testable:* on a Player Two win the Player Two column is the one marked as incremented
    and its value already counts the game just finished; on a tie the Ties column is.
    Whether the `+1` delta itself should persist on a re-shown result is **OQ-8**.

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

    **Slots this surface consumes**, named here for `P1-03-theme-system.md` req 15, whose
    inventory currently carries no modal or overlay slots at all. Under that requirement's
    own rule — the slot list is derived from what the screens actually consume — this
    surface adds:

    - **Result card surface fill and corner radius** — the card the result sits on.
    - **Result scrim** — distinct from the settings modal's scrim; the handoff draws the
      result at `0.62` and the settings sheet at `0.72`, so one shared scrim value cannot
      serve both.
    - **Board-behind opacity** — the finished board remains visible at 60% in the handoff.
    - **Winner-colored card border**, resolved per player, **and its neutral counterpart**
      for the draw.
    - **Winner-tint radial gradient** behind the card, resolved per player.
    - **Result title type** (handoff: 28/600) and **result score-chip type** (27/600),
      both distinct from the scoreboard strip's chip type (22/600) — three sizes, not one.
    - **Draw glyph pair opacity** — the ✕ / ○ pair drawn at 55% in each player's color.
    - **Primary button vs ghost/secondary button styling**, for the rematch control and
      whatever OQ-2 settles beside it.
    - The **`winGame` sound and animation slots**, already inventoried by
      `P1-03-theme-system.md` req 17 and `P2-04-animations.md` req 23 and fired by
      requirement 16 below.

    *Source: `design_handoff_game_ui/README.md` → 1g, 1h, and → Design tokens. The
    handoff's numbers are Neon's authored values, quoted to identify **which** slots exist;
    they are not a requirement on any other theme.*

14. **The whole flow works with animations off.** With the animations toggle off, the
    game-over state and the rematch reset are instant state changes — no animation, no fade
    or transition standing in for one — and the surface stays fully readable and its
    controls fully usable.
    *Source: `Animations.md` → Decisions → Animations off = instant state change ("no
    animation, no substitute effect, no fade or transition standing in for one"); →
    Decisions → Animations don't block input; `design_handoff_game_ui/README.md` →
    Interactions & behavior ("Every screen above is fully readable with animation off —
    that is the correctness test"); `P2-04-animations.md` reqs 16–18.*
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
    *Note:* `P2-03-haptics.md` → OQ-2 records that whether non-board controls buzz at all is
    unsettled, and names this requirement as a sibling PRD's broad reading rather than a
    decision in the docs.

### Firing the result's sound and motion

16. **This feature is the firing site for the game-over sound and animation. On the move
    that wins the game it fires the `winGame` sound and the `winGame` animation exactly
    once, through the audio and animation layers, with both slots read from the active
    theme.** Like the increment in requirement 4, the fanfare is bound to the ending
    **move**, not to the game-over state: re-entering that state by reopening a finished
    game (requirement 1) replays neither, on any relaunch.
    *Source: `Animations.md` → Where Animations Fire, which lists *"Winning the whole
    game"* among the **moments** animations fire at — a moment, not a standing state;
    `Theming.md` → What a Theme Controls → Audio; `P2-02-audio.md` req 6 (the `winGame`
    sound slot) and its Out of Scope, which assigns firing to "the engine and the
    board/game-over PRDs"; `P2-04-animations.md` req 23 (the `winGame` animation slot) and
    its Depended-on-by note that this PRD fires the animated moments.*
    *Testable:* winning a game fires exactly one `winGame` sound and one `winGame`
    animation; closing and reopening that finished game fires neither, on every relaunch;
    with sound muted no sound plays and with animations off no animation plays, and in
    both cases the result is still fully shown (requirement 14).
    **The tie has no equivalent slot and is deliberately not covered here — see OQ-7.**
    This requirement resolves *who fires*, which was contradictory across three PRDs. It
    does not decide what a draw sounds or looks like.

## Out of Scope

Named so the boundary is explicit. Each is specified elsewhere; do not specify it here.

- **Win, claim, cat-game and straight-draw detection, legal-move computation, the score as
  data, the increment itself, and the turn-order-across-games computation** —
  `P1-02-engine-rules.md` (reqs 20–22, 25–27). This feature reads the engine's outcome and
  asks it to start the next game; it implements none of that logic. Requirement 4 states
  *when* the increment lands because the game-over surface depends on it, not because this
  layer performs it.
- **The scoreboard's own layout, chips and turn indicator** —
  `P3-03-scoreboard-turn-indicator.md`. Requirements 11 and 12 cover only what the *result*
  surface says about the score, not how the persistent scoreboard row is drawn.
- **Writing the series to storage — the Hive box, the repository, and when a save is
  written** — `P1-04-persistence.md`.
- **The open-games list, its cap (3 by default, 100 with the in-app purchase), and the
  delete action that frees a slot** — `P4-02-open-games-list.md`, with the storage half in
  `P1-04-persistence.md` and the cap value in `P1-07-entitlements.md`. Requirement 7
  requires only that a rematch consume no slot.
- **The in-game settings modal, quick actions, and the exit-to-main-menu path** —
  `P4-04-settings.md`. That the settings button at the top right is the way out of a game
  is already settled (`Menus and UI.md` → Decisions → How do you get back to the main menu
  from a game?); whether an exit control also sits *beside* Rematch is not — see OQ-2.
- **What the result sound *is*, how it is loaded and played, and the mute path** —
  `P2-02-audio.md`. Requirement 16 fires it; that PRD defines it. The two are not the same
  job, and neither PRD may assume the other does both.
- **What the `winGame` animation *is*, its type and duration, the one-at-a-time rule, and
  the animations-off machinery** — `P2-04-animations.md`. Requirement 16 fires it;
  requirement 14 constrains its off path.
- **Board and cell rendering, the three highlights, and the two-tap input gesture** —
  `P3-01-board-rendering.md` and `P3-02-move-input.md`. Requirement 2 only makes input
  inert; it does not respecify it.
- **The on-board legend and hint** — `P3-05-how-to-play.md`, which raises separately whether
  its layer stays on screen under the result scrim.
- **Anything from `Alternative Game Styles.md`.** That is a declared parking-lot doc and
  explicitly not the game being built.

## Open Questions

> **Closed since the first draft:** *when does the score increment — at game end, or when
> the rematch is taken?* Settled as **at game end**, and promoted to requirement 4
> (`Menus and UI.md` → Decisions → When does the scoreboard increment). The matching
> question in `P1-02-engine-rules.md` — its OQ-2 — is closed there too, with the answer
> carried by its requirements 26 and 27.

> **Flagged contradiction — the approved handoff still carries the losing reading.**
> `design_handoff_game_ui/README.md` → *Interactions & behavior* states: **"REMATCH resets
> the board, increments the right column, and stays in the same save slot."** The middle
> clause is the rematch-increments reading that `Menus and UI.md` → Decisions → *When does
> the scoreboard increment* settled against. **The docs win; requirement 4 and requirement
> 6 are correct as written, and that sentence is stale.** It is recorded here rather than
> fixed because the handoff is a read-only reference asset. A code writer building the
> result modal will read that same section for the scrim, board opacity and haptic rules
> (requirements 13–15 cite it), so the correction has to be visible from this PRD.

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

Note that `P2-01-navigation.md` → Open Question 10 carries the routing consequence of the
same question: a route participates in the back stack and the back-swipe gesture, an
overlay does not.

### OQ-2 — What sits beside Rematch?

As worded in `Menus and UI.md` → Game Over → Rematch:

> ("Rematch is an option" implies at least one other choice sits next to it — presumably
> exiting to the main menu, which is also reachable via the top-right settings button.)

Recorded as stated, not as a decision. The handoff draws the presumption as real — 1g lists
a ghost **Exit to Main Menu** under REMATCH — but the doc has not settled that a second
control exists on this surface, and the settled exit route is the settings button
(`Menus and UI.md` → Decisions → How do you get back to the main menu from a game?).
See **OQ-6**, which is this question and the settings-button question taken together.

### OQ-3 — Gaps found while writing this PRD

Flagged by the PRD author, not asked by the docs. Each is something an implementer would
otherwise decide by accident. None is resolved here.

- **What a finished game the players never rematched shows when it is resumed.** The score
  is no longer at stake: the increment happens on the ending move (requirement 4), so such
  a game is already counted, walking away loses nothing, and reopening it counts nothing
  further. What is still unsettled is narrower — reopening that game from the open-games
  list, does the player get the finished board with the result surface again, or a board
  already reset and waiting for the first move of the next game? Requirement 6 makes the
  reset an effect of taking the rematch, so as the docs stand a resumed un-rematched game
  is still a finished game, and the question is what it looks like rather than what it
  counts.
- **Where the save is written.** Requirement 9 needs the increment and the reset to reach
  storage, but **no PRD in any wave names the save call site** — not this one, not
  `P1-04-persistence.md`, not `P1-02-engine-rules.md`. `P1-04` → Open Questions 4 records
  save granularity as unsettled: *"Whether the store is written after every confirmed move,
  or only when the player leaves the game."* Under its second candidate a crash between the
  ending move and leaving the game loses the increment, and requirement 9's original
  testable would have failed. That testable is now written to whatever save point `P1-04`
  defines rather than presuming one. The answer belongs in `P1-04`, where it can also
  settle move-by-move saving; answering it here would cover only game over.
- **Whether the game-over surface can be dismissed to look at the finished board.** The
  handoff keeps the board visible behind 1g/1h but, unlike the in-game settings sheet (1f),
  draws no close control on either. Whether a player can put the result aside to study how
  the game ended — and get it back — is unspecified.
- **Whether the top-right settings button is still live while the result is on screen.**
  `Menus and UI.md` settles that settings must be reachable *mid-game* and that it is also
  the way out; a finished game is not mid-game, and the docs do not say whether that button
  keeps working, is hidden, or is the intended exit route referenced in OQ-2. Also carried
  by `P3-03-scoreboard-turn-indicator.md` → Open Question 2 and `P2-01-navigation.md` →
  Open Question 12, which notes that if it is not live then at game over the only settled
  route out of a game does not exist. See **OQ-6**.

### OQ-4 — The draw modal's copy calls the big-board draw a "cat game"

`design_handoff_game_ui/README.md` → *1h — Modal: draw* words the result as:

> "The big board filled up with no three in a row. **Cat game.**"

That cuts against settled terminology. `Game Overview.md` → Terminology defines a **cat
game** as *"a small board filled with no winner"* — a quadrant-level event that leaves that
quadrant unclaimed forever — and `Rules.md` → Edge Cases names the big-board case a
**straight draw**, a separate entry from *Cat game (small board draw)*. Requirement 3 uses
"tie" and "straight draw", the docs' vocabulary. Whether the drawn copy should change, or
the word is being used loosely on purpose in player-facing text, is not resolved here: the
handoff is read-only and the terminology belongs to the design docs.
`P3-05-how-to-play.md` raises the same board/quadrant vocabulary split for player-facing
copy generally.

### OQ-5 — The winner modal's copy names *which* line won

`design_handoff_game_ui/README.md` → *1g — Modal: winner* draws the flavor line:

> "Three boards in a row, straight down the middle."

That sentence describes the winning triple. `P1-02-engine-rules.md` req 22 has the engine
report only the outcome — in progress, won by Player One, won by Player Two, or tie — and
nothing in that PRD exposes which row, column or diagonal completed the win, so this copy
is not implementable as drawn. This PRD does not assume the missing capability: requirement
10 asks only that the outcome be stated and the winner named. If the line-specific copy is
wanted, `P1-02-engine-rules.md` needs a requirement to expose the winning line — a decision
for the docs, not an inference to make here.

### OQ-6 — Taken together, can a finished game become a dead end?

OQ-2 and OQ-3's fourth bullet are two questions with one joint consequence, which neither
states on its own. **Asked as one question: at game over, what are *all* of the player's
available actions?**

If OQ-2 resolves to "nothing sits beside Rematch" — defensible, since only the rematch
button is settled in `Menus and UI.md` → Decisions → What happens when a game ends? — and
the settings-button question resolves to "not live during game over" — also defensible,
since `Menus and UI.md` settles that button as the *mid-game* route and a finished game is
not mid-game — then a finished game offers **exactly one possible action, forever**:
rematch. There is no way back to the main menu from the result, and an un-rematched
finished game can only be escaped by deleting it from the open-games list
(`P4-02-open-games-list.md`). Each answer is reasonable alone; the pair is not. Whoever
answers either should answer both together.

### OQ-7 — What does a *tie* sound and look like?

Requirement 16 fires the `winGame` sound and animation on a win. A straight draw has no
equivalent slot: the inventories in `P2-02-audio.md` req 6 and `P2-04-animations.md` req 23
name `placeMark`, `claimQuadrant`, `catGame`, `winGame` and (audio only) `buttonTap`, and
`catGame` belongs to a *small* board filling with no winner (`Game Overview.md` →
Terminology) — not to the big-board straight draw, which is exactly the confusion OQ-4
records in the handoff's copy. So as the docs and sibling PRDs stand, a drawn game ends in
silence and stillness while a won game does not. Whether the draw gets its own slot, reuses
`catGame`, or is deliberately quiet is unsettled, and so is whether `Animations.md` →
Scope For Now — *"animations apply to the player's marker"* — even permits a result-card
animation. Not resolved here.

A second, narrower part of the same question: requirement 16 binds the fanfare to the
ending **move**, reading `Animations.md` → Where Animations Fire as a list of *moments*. If
the intent is instead that reopening a finished game replays its win sound and animation,
requirement 16 needs restating — it is written to the narrow reading on purpose.

### OQ-8 — Should the `+1` delta still show on a re-shown result?

Requirement 11 requires the incremented column to be identifiable, sourced from the
handoff's `+1` chip. Because requirement 1 makes the game-over state a standing condition,
that surface can appear again for the same game weeks later — and as written, the `+1`
would still be drawn then. That may be intended (it always describes the same finished
game, and the delta is a fact about it) or an artefact of the condition-not-event framing
(a `+1` reads as "just now"). The docs say nothing about a delta at all; the `+1` exists
only in the handoff. Not resolved here, and it moves with OQ-3's first bullet — if a
resumed un-rematched game shows a reset board instead, the question disappears.
