# PRD: Rules Engine

> **Status:** Draft · Source docs read: `Rules.md`, `Game Overview.md`, `Tech Design.md`,
> `Game Board Design.md`, `Menus and UI.md`, `roadmap.md`, plus the read-only reference asset
> `design_handoff_game_ui/README.md`. `Alternative Game Styles.md` is a declared parking-lot
> doc and was read only to confirm it is out of scope — no requirement here comes from it.

> **Wave:** P1 · **Depends on:** nothing. The engine is pure Dart and can be built and
> unit-tested with no other PRD in place. **Depended on by:** `P1-04-persistence.md`
> (serializes these models), `P3-01-board-rendering.md`, `P3-02-move-input.md`,
> `P3-03-scoreboard-turn-indicator.md`, `P3-04-game-over-rematch.md` (all read this state).

> **Note on source status:** `Rules.md` carries the house banner *"Nothing here is settled"*
> while being the only specification of the rules of play, and the approved UI handoff was
> built from it. This PRD therefore treats the body of `Rules.md` as settled. Its
> **Decisions** section now settles the opening-move question an earlier draft of this PRD
> had to flag — see OQ-1, closed — and its **Open Questions** section carries one live
> question, reproduced here as OQ-6, which this PRD does not resolve.

## Problem

There is no application code for Tic-Tac-Toe-Extreme yet. Every other piece of the app —
the board rendering, the two-tap input, the scoreboard, the Hive save file — needs one
authoritative answer to "what is the state of this game, and what may happen next?" Without
a rules engine, each of those layers would have to re-derive the sending rule, the
free-choice state, and the win/cat-game conditions for itself, and they would disagree.

The rules are also not the trivial part. Recursive tic-tac-toe stacks a sending rule, dead
quadrants, a free-choice escape hatch, a per-quadrant claim, a big-board win, and a
big-board draw on top of each other, and `Tech Design.md` → Decisions → *Unit tests for the
rules engine* names this as **"where the real complexity is."**

## Goal

A pure-Dart, Flutter-free rules engine under `lib/engine/` that holds the complete state of
a game of Tic-Tac-Toe-Extreme and of the series it belongs to, computes the legal moves for
both the forced and free-choice states, applies a move by returning a new immutable state,
and reports when a quadrant is claimed, when a quadrant is a cat game, when a player has
won, and when the game is a straight draw. Every rule in `Rules.md` is enforced by the
engine and covered by unit tests; no UI layer implements any of it.

## Requirements

### Architecture and representation

1. The engine lives under `lib/engine/` and is **pure Dart with zero Flutter imports**. It
   must not import `hive`, `hive_flutter`, or any Flutter package. *(Tech Design →
   Decisions → Is the game logic separate from Flutter?; Serialization and the storage
   layer — "`hive_flutter` is not pure Dart, so it must never be imported from `engine/`";
   Project structure — layer-first, whose tree names `engine/board.dart` and
   `engine/rules.dart`.)*
   **Testable:** a source scan of `lib/engine/` finds no `package:flutter`, `package:hive`
   or `package:hive_flutter` import.
2. The domain models are built with **`freezed` + `json_serializable`**, with
   `toJson`/`fromJson` generated **into `engine/`**. No Hive `TypeAdapter`s. *(Tech Design →
   Decisions → Serialization and the storage layer.)*
   **Testable:** every model round-trips — `fromJson(toJson(x)) == x` — using only engine
   code.
3. State is **immutable**. The engine never mutates a board in place; applying a move
   produces a new state object. The API shape is `Board applyMove(Board, Move)` returning
   new state, not `board.play(move)` mutating in place. *(Tech Design → Decisions → Game
   state is immutable.)*
   **Testable:** after `applyMove`, the input `Board` is unchanged and compares equal to a
   freshly constructed copy of its pre-move value; applying the same move to the same board
   twice yields two equal results.
4. The board is exactly **two levels**: one big board of 9 quadrants, each holding its own
   3x3 small board — 81 playable cells. No deeper nesting. *(Rules → Setup; Game Board
   Design → Board Structure; Game Overview → Decisions → Recursion depth.)*
5. A cell is empty, Player One's, or Player Two's. A quadrant is **open**, **claimed by
   Player One**, **claimed by Player Two**, or **cat game**. A new game starts with all
   quadrants open and all small boards empty. *(Rules → Setup; Game Overview →
   Terminology.)*
6. Players are identified in the engine as **Player One** and **Player Two**. The engine
   holds no mark glyph — X and O are theme-supplied asset slots, not engine values, and the
   player labels must not be hardcoded in a way that fights adding real names later.
   *(Game Overview → Decisions → Player names; Tech Design → Decisions → Marks — image or
   icon, supplied by the theme; Game Board Design → Pieces & Marks.)*
7. The engine's domain vocabulary is the project's: *big board*, *quadrant*, *small board*,
   *claim*, *cat game*. *(Game Overview → Terminology.)*

### Turn structure and placement

8. Players **alternate turns**. A move places one mark in one empty cell of one small board,
   after which it is the other player's turn. *(Rules → Turn Structure 1–2; Menus and UI →
   A New Game → What It Starts; Pass-and-Play Turn Handoff — "the game switches the active
   player automatically after each move".)*
9. **First move of a game:** the player who goes first selects the starting quadrant and
   places their mark somewhere in that quadrant's small board. This is **not a third
   placement state** — the opening move *is* the free-choice state of requirement 18, over
   all nine quadrants because all nine are open. *(Rules → Placement Rules → First move;
   Rules → Edge Cases → Sent to a dead quadrant — "This is the same kind of freedom the
   first player has on the opening move"; Game Board Design → Active Quadrant Highlight →
   The free-choice state — "This also covers the opening move".)*
   **Testable:** on a new game the engine reports the free-choice state, and the legal moves
   are all 81 cells.
10. **The opening move sends the opponent, exactly like every other move.** The cell the
    first player plays sends the second player to the matching quadrant. There is **no
    exception for move 1**, and the second player is *not* bound to the quadrant the first
    player selected. *(Rules → Decisions → Does the opening move send the opponent? —
    "**Yes — the cell the first player plays sends the second player, exactly as on every
    later move. There is no exception for move 1.**"; Rules → Placement Rules → The sending
    rule — "This is true of the opening move exactly the same as every move after it";
    Game Overview → Core Concept.)*
    **Testable:** the first player selects the top-left quadrant and plays its centre cell —
    the second player's only legal quadrant is the centre quadrant, not the top-left one.
11. **The sending rule, on every move:** the cell played inside a small board maps to the
    corresponding quadrant on the big board, and that is where the opponent must play next.
    It applies uniformly from move 1 onward — there is no move to which it does not apply.
    *(Rules → Placement Rules → The sending rule.)*
12. The **cell → quadrant mapping is positional identity**: the 3x3 position of the cell
    within its small board is identical to the 3x3 position of the quadrant within the big
    board — top-left cell → top-left quadrant, centre cell → centre quadrant, and so on for
    all 9 positions, in the row-major order of the diagram in `Rules.md`. *(Rules → Cell →
    Quadrant Mapping.)*
    **Testable:** for each of the 9 positions, playing that position in any small board
    forces the opponent into the same-numbered quadrant.

### Claiming a quadrant

13. Three in a row on a small board — row, column, or diagonal — **claims** that quadrant
    for the player who completed it, effective on the move that completes it. *(Rules →
    Turn Structure 4; Winning a Sub-Board.)*
14. A **claimed quadrant is closed to further play**, including any cells in it that are
    still empty. *(Rules → Edge Cases → Sent to a dead quadrant — "Claimed quadrants and
    cat-game quadrants are both off limits".)*
    **Testable:** a quadrant claimed while it still has empty cells yields no legal moves
    thereafter, in either the forced or the free-choice state.
15. Quadrants are claimed **only** by winning the small board inside them. There is no other
    route to claiming a quadrant. *(Rules → Winning the Game.)*

### Cat game

16. A small board **completely filled with no winner** is a **cat game**. That quadrant is
    unclaimed for the rest of the game — nobody ever gets it — it is closed to further play,
    and it can never count toward either player's big-board line. *(Rules → Edge Cases → Cat
    game; Game Overview → Terminology.)*
    **Testable:** a cat quadrant blocks every big-board line through it for both players for
    the remainder of the game.

### Free choice

17. If the sending rule points a player at a quadrant that is **already claimed** or is a
    **cat game**, that player instead gets a **free choice: they may play in any other
    quadrant that is still unclaimed and open**. *(Rules → Edge Cases → Sent to a dead
    quadrant → free choice.)*
    **"Already claimed" carries an unstated timing** in the one case where the sending move
    is itself what claimed or cat-gamed the destination — see **OQ-6**.
18. The engine exposes which of the two placement states is active — **forced** (exactly one
    legal quadrant) or **free choice** (every still-open quadrant, up to 9) — as engine
    state the UI reads rather than as something the UI infers. There are only these two
    states: the opening move is the free-choice state (requirement 9), not a third one.
    *(Tech Design → Decisions → Is the game logic separate from Flutter?, which names "legal
    moves, sending rule, win/cat-game detection, free-choice state" as engine
    responsibilities; Game Board Design → Active Quadrant Highlight → The free-choice state,
    whose two modes are Forced and Free choice and which says "This also covers the opening
    move".)*
    **This two-state definition presupposes one of the two answers to OQ-6** — read that
    question before implementing.
19. **Legal-move computation.** In the forced state the legal moves are exactly the empty
    cells of the forced quadrant. In the free-choice state they are the empty cells of every
    still-open quadrant. Cells that are occupied, and every cell in a claimed or cat-game
    quadrant, are never legal. *(Rules → Placement Rules; Edge Cases → Sent to a dead
    quadrant; Game Board Design → Active Quadrant Highlight.)*

### Ending a game

20. Three **claimed quadrants in a row** on the big board — row, column, or diagonal — wins
    the game, effective on the claim that completes the line. The game is over; no further
    moves are legal. *(Rules → Turn Structure 5; Winning the Game.)*
21. If **no quadrant remains open** (every quadrant is claimed or cat game) and no player has
    three claimed quadrants in a row, the game is a **straight draw** — a tie.
    **Most-quadrants-claimed does not win; the count is irrelevant.** *(Rules → Edge Cases →
    Big board full with no three-in-a-row → straight draw.)*
    **Testable:** a filled big board where one player holds 5 quadrants and the other 3 with
    no line reports a tie, not a win.
22. The engine reports the game's outcome as one of: in progress, won by Player One, won by
    Player Two, or tie. *(Rules → Winning the Game and Edge Cases; Game Board Design →
    Scoreboard, whose three counters are Player One / Ties / Player Two.)*
23. The engine's state includes the **most recent completed move** (which quadrant, which
    cell), which is what the last-move highlight renders from and what has to survive
    leaving and resuming a game. *(Game Board Design → Last Move Highlight and → Lifetime;
    Menus and UI → Persistence → Leaving a game mid-play.)* The concrete field name and
    shape fall under OQ-3.

### The series

24. Engine state for an open game covers the **whole series** — the board plus the running
    score of Player One / Ties / Player Two — because each open game carries its own
    scoreboard and resuming a game resumes the series, not just the last board. *(Game
    Overview → Decisions → Scoreboard lifetime; Session Structure — Games and Continuing;
    Menus and UI → Decisions → What does an open game hold?)* Writing that state to storage
    belongs to `P1-04-persistence.md`.
25. **Turn order across games.** Game 1: Player One goes first. After a win: the winner of
    the last game goes first. After a tie: the player who went first in the tied game goes
    first again. The engine therefore retains who went first in the current game. *(Rules →
    Turn Order Across Games; Rules → Decisions → Who goes first after a tie?; Game Overview
    → Session Structure.)*
    **Testable:** three consecutive games — a Player Two win, then a tie, then a Player One
    win — produce first players Player One, Player Two, Player Two, Player One.
26. Starting the next game in a series **resets the board** and applies requirement 25 to
    choose its first player. It **leaves the score untouched** — by requirement 27 the
    finished game was already counted when it ended, so starting the next game must not
    move any counter. *(Menus and UI → Decisions → What happens when a game ends? — "It
    resets the board for the next game"; → Decisions → When does the scoreboard increment —
    "Taking the rematch only resets the board"; Game Overview → Session Structure —
    "Continuing **resets the board**".)*
    **Testable:** the three counters immediately after starting the next game are identical
    to their values immediately before it was started.
27. **The series score increments as part of resolving the game, at game end** — the
    winner's column, or the **Ties** column on a straight draw, goes up by one on the move
    that ends the game, not when a rematch is taken. *(Menus and UI → Decisions → When does
    the scoreboard increment — "**At game end.** The winner's column, or Ties, increments as
    soon as the game is won or tied — not when a rematch is taken"; Game Board Design →
    Scoreboard — "Increments when a game ends"; Rules → Edge Cases → "The Ties counter on
    the scoreboard goes up one"; Game Overview → Session Structure.)*
    **Testable:** applying the move that wins or draws a game leaves the resulting state
    with that column one higher and the other two unchanged, with no further call needed;
    across a series of *n* finished games the three counters sum to *n* whether or not each
    was followed by another game. The presentation side of this same answer is
    `P3-03-scoreboard-turn-indicator.md` requirement 4 and `P3-04-game-over-rematch.md`
    requirement 4 — this requirement is the engine-side statement that the score is series
    state changed by the game resolving.

### Tests

28. The engine has **unit tests** — this is where the real complexity is. They are written
    from these requirements, and they run locally (`flutter test`); nothing runs them on a
    push. *(Tech Design → Decisions → Unit tests for the rules engine; CI — local builds
    only.)*

## Out of Scope

Named here so the boundary is explicit. Each is specified elsewhere; do not specify it
here.

- **Rendering, the three highlights, and quadrant/cell visual states** —
  `P3-01-board-rendering.md`. The engine supplies the state; it draws nothing and holds no
  theme value.
- **The two-tap select-then-confirm gesture, the pending selection, illegal taps, and
  haptics** — `P3-02-move-input.md`. A pending selection is input state, never engine state.
- **The scoreboard UI and the turn indicator** — `P3-03-scoreboard-turn-indicator.md`. The
  engine owns the score *data* as part of series state; the display is not its problem.
- **The game-over surface and the rematch control** — `P3-04-game-over-rematch.md`. The
  engine reports the outcome and counts it; offering the rematch and drawing the result are
  that PRD's.
- **Storage — the Hive box, the repository interface, the open-games list, the 3-game cap,
  `shared_preferences`** — `P1-04-persistence.md`. The engine generates `toJson`/`fromJson`
  and stops there.
- **Anything from `Alternative Game Styles.md`**, including Lock-In Style. That is a
  parking-lot doc and explicitly not the game being built.
- **Themes, animations, sounds, opponent names, menus, and screen flow** — none of it
  reaches `engine/`.
- **AI opponent and online multiplayer.** *(Game Overview → Decisions → Single-player / AI
  opponent — "No.")* Note the standing constraint that tech choices must not foreclose
  syncing board state over a network *(Tech Design → Decisions → Online multiplayer is an
  intended future direction)*; nothing is built for it now.

## Open Questions

Numbering is stable — answered questions stay as stubs, because other PRDs cite these
numbers.

**OQ-1 — Answered and closed.** *Does the first player's opening cell send the second
player, or is the second player bound to the opening quadrant?* Settled in `Rules.md` →
Decisions → **Does the opening move send the opponent?**: *"**Yes — the cell the first
player plays sends the second player, exactly as on every later move. There is no exception
for move 1.**"* The *Second player* bullet that said otherwise is gone from `Rules.md` →
Placement Rules. Requirements 10 and 11 carry the answer.

**OQ-2 — Answered and closed.** *When does the score increment — at game end, or when the
rematch is taken?* Settled in `Menus and UI.md` → Decisions → **When does the scoreboard
increment**: *"**At game end.**"* Requirements 26 and 27 carry the answer.

**OQ-3 — What is the concrete shape of the persisted game object?** From `Tech Design.md`,
alongside Decisions → Serialization and the storage layer: *"A candidate shape for the
persisted Game object — cells, quadrants, activeQuadrant, currentPlayer, lastMove, score,
firstPlayerThisGame — is sketched in Design Handoff → State... It is a design sketch, not a
decision taken here."* The requirements above are written against behavior, not against
that shape.

**OQ-4 — Persisted data, versioning.** From `Tech Design.md` → Open Questions 1: *"When the
shape of stored data changes — a fifth preference is added, a key is renamed, an open game
gains a field — what happens to data already on the device? A game written by v1.0 has to
still load in v1.1."* This lands on the engine because `toJson`/`fromJson` are generated
into `engine/`.

**OQ-5 — What does the engine do when handed an illegal move?** *(Raised by this PRD; not
discussed in any design doc.)* The docs answer this only at the UI layer — `Game Board
Design.md` → Taps outside the legal quadrant: *"An illegal tap does nothing."* Whether
`applyMove` throws, returns the board unchanged, or returns a result type carrying a reason
is unspecified, and requirement 3's signature `Board applyMove(Board, Move)` does not settle
it. An implementer will otherwise decide this by accident.

**OQ-6 — A move that claims (or cat-games) the very quadrant it sends the opponent to —
which state does the send see, before or after the move?** From `Rules.md` → Open Questions,
as worded there:

> Example: play the centre cell of quadrant 5, and that same move completes three in a row
> *in* quadrant 5, claiming it. The cell played sends the opponent to the center quadrant —
> but is the send evaluated against quadrant 5's state *before* this move (in which case the
> opponent is sent to a quadrant that, by the time they'd play, is already claimed — an
> illegal position unless the free-choice rule kicks in), or *against its state after* this
> move (the quadrant is already dead by the time the send happens, so the opponent gets free
> choice instead)? This is reachable in normal play, not an edge case someone has to go
> looking for, and reviewers flagged it as the most common defect in an
> ultimate-tic-tac-toe engine.

**This PRD does not resolve it — but requirement 18 as written already presupposes the
*after* reading, and whoever answers needs to know that.** Requirement 18 admits exactly two
placement states: *forced*, defined as **exactly one legal quadrant**, and *free choice*.
Under the *before* reading the engine would have to report "forced → quadrant 5" while
quadrant 5 holds **zero** legal moves — a state that definition cannot express, and one
requirement 19 forbids by implication, since no cell of a claimed or cat-game quadrant is
ever legal. So **answering "before" requires requirement 18 to change**: it would need a
third placement state, or a forced state that can carry an empty legal-move set, plus a
rule for what the opponent actually does from there. Requirement 17 inherits the same
unstated timing — its *"already claimed"* does not say whether "already" is evaluated
before or after the move that sends.
