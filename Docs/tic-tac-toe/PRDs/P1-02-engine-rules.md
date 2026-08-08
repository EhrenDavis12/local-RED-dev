**Build-readiness: 88**

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
> **Decisions** section now settles all three questions earlier drafts of this PRD had to
> flag — the opening-move send (OQ-1), the claim-then-send ordering (OQ-6), and the illegal
> move (OQ-5) — and its **Open Questions** section is empty. Nothing behavioral is left open
> here; OQ-3 and OQ-4 concern the persisted JSON only and are fenced.

> **Requirement numbers are stable.** Other PRDs cite them by number (`P1-04` reqs 14 and
> 23, `P3-02` reqs 3, 18–20 and 22, `P3-04` reqs 14, 22, 26 and 27). Nothing below has been
> renumbered; the named surface was appended as requirements 29–42.

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

> **Read requirements 29–42 first.** They name the types, accessors, operations and error
> contract the behavioral requirements below are written against, and they are what the
> consuming PRDs bind to. They sit last only so the existing numbering stays stable.

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
   state is immutable.)* What `Board` and `Move` are is requirements 29 and 30; what the
   returned `Board` carries is requirement 33; what happens instead of a return when the
   move is illegal is requirement 42.
   **Testable:** after `applyMove`, the input `Board` is unchanged and compares equal to a
   freshly constructed copy of its pre-move value; applying the same move to the same board
   twice yields two equal results.
4. The board is exactly **two levels**: one big board of 9 quadrants, each holding its own
   3x3 small board — 81 playable cells. No deeper nesting. *(Rules → Setup; Game Board
   Design → Board Structure; Game Overview → Decisions → Recursion depth.)*
5. A cell is empty, Player One's, or Player Two's. A quadrant is **open**, **claimed by
   Player One**, **claimed by Player Two**, or **cat game**. A new game starts with all
   quadrants open and all small boards empty. *(Rules → Setup; Game Overview →
   Terminology.)* The types are requirement 41; the fresh-game state is requirement 32.
6. Players are identified in the engine as **Player One** and **Player Two**. The engine
   holds no mark glyph — X and O are theme-supplied asset slots, not engine values, and the
   player labels must not be hardcoded in a way that fights adding real names later.
   *(Game Overview → Decisions → Player names; Tech Design → Decisions → Marks — image or
   icon, supplied by the theme; Game Board Design → Pieces & Marks.)*
   **Testable:** a source scan of `lib/engine/` finds no `'X'` or `'O'` literal, no
   `Icons.`, no `assets/` path, and no user-facing display string.
7. **The public API uses the project's vocabulary** — *big board*, *quadrant*, *small
   board*, *claim*, *cat game*, *Player One*, *Player Two*. *(Game Overview →
   Terminology.)*
   **Testable, as a concrete identifier list:** the symbols required by requirements 29–42
   exist and are spelled `Board`, `Move`, `Move.quadrant`, `Move.cell`, `Player.one`,
   `Player.two`, `QuadrantState.open`, `QuadrantState.claimedByPlayerOne`,
   `QuadrantState.claimedByPlayerTwo`, `QuadrantState.catGame`, `PlacementState.forced`,
   `PlacementState.freeChoice`, `PlacementState.gameOver`, `GameOutcome.inProgress`,
   `GameOutcome.playerOneWins`, `GameOutcome.playerTwoWins`, `GameOutcome.tie`,
   `Score.playerOne`, `Score.ties`, `Score.playerTwo`, `IllegalMoveError`,
   `IllegalMoveReason.notLegal`, `IllegalMoveReason.gameAlreadyFinished` — no abbreviation
   of *quadrant* to *quad*, and no `p1`/`p2` anywhere in the public API.

### Turn structure and placement

8. Players **alternate turns**. A move places one mark in one empty cell of one small board,
   after which it is the other player's turn. *(Rules → Turn Structure 1–2; Menus and UI →
   A New Game → What It Starts; Pass-and-Play Turn Handoff — "the game switches the active
   player automatically after each move".)* Whose turn it is, is requirement 38.
   **Testable:** `currentPlayer` differs from its pre-move value after every `applyMove`,
   and the mark written is always the pre-move `currentPlayer`'s.
9. **First move of a game:** the player who goes first selects the starting quadrant and
   places their mark somewhere in that quadrant's small board. This is **not a third
   placement state** — the opening move *is* the free-choice state of requirement 18, over
   all nine quadrants because all nine are open. *(Rules → Placement Rules → First move;
   Rules → Edge Cases → Sent to a dead quadrant — "This is the same kind of freedom the
   first player has on the opening move"; Game Board Design → Active Quadrant Highlight →
   The free-choice state — "This also covers the opening move".)*
   **Testable:** on `Board.newSeries()` the placement state is `freeChoice`,
   `activeQuadrant` is null, and `legalMoves` has 81 entries.
10. **The opening move sends the opponent, exactly like every other move.** The cell the
    first player plays sends the second player to the matching quadrant. There is **no
    exception for move 1**, and the second player is *not* bound to the quadrant the first
    player selected. *(Rules → Decisions → Does the opening move send the opponent? —
    "**Yes — the cell the first player plays sends the second player, exactly as on every
    later move. There is no exception for move 1.**"; Rules → Placement Rules → The sending
    rule — "This is true of the opening move exactly the same as every move after it";
    Game Overview → Core Concept.)*
    **Testable:** `applyMove(Board.newSeries(), Move(quadrant: 0, cell: 4))` yields
    `activeQuadrant == 4` and a `legalMoves` set confined to quadrant 4 — not quadrant 0.
11. **The sending rule, on every move:** the cell played inside a small board maps to the
    corresponding quadrant on the big board, and that is where the opponent must play next.
    It applies uniformly from move 1 onward — there is no move to which it does not apply.
    *(Rules → Placement Rules → The sending rule.)*
    **Testable:** for any in-progress board and any legal move *m*, the resulting board has
    `activeQuadrant == m.cell`, unless requirement 17 redirects it to free choice.
12. The **cell → quadrant mapping is positional identity**: the 3x3 position of the cell
    within its small board is identical to the 3x3 position of the quadrant within the big
    board — top-left cell → top-left quadrant, centre cell → centre quadrant, and so on for
    all 9 positions. *(Rules → Cell → Quadrant Mapping.)* Under requirement 31's indexing
    this is exactly `activeQuadrant == move.cell`, which is the form to implement and test
    against. The 1–9 labels in the `Rules.md` diagram are for human reading; **requirement
    31 is the authoritative index base**, so no one needs that diagram to write a test.
    **Testable:** for each of the 9 cell indices *c*, playing index *c* in any quadrant
    yields `activeQuadrant == c`.

### Claiming a quadrant

13. Three in a row on a small board — row, column, or diagonal — **claims** that quadrant
    for the player who completed it, effective on the move that completes it. *(Rules →
    Turn Structure 4; Winning a Sub-Board.)*
    **Testable:** for each of the 8 lines in a small board — cells `{0,1,2}`, `{3,4,5}`,
    `{6,7,8}`, `{0,3,6}`, `{1,4,7}`, `{2,5,8}`, `{0,4,8}`, `{2,4,6}` — the move completing
    that line leaves `quadrantAt(q)` at the mover's claimed state, while the board *before*
    that move has it `open`.
14. A **claimed quadrant is closed to further play**, including any cells in it that are
    still empty. *(Rules → Edge Cases → Sent to a dead quadrant — "Claimed quadrants and
    cat-game quadrants are both off limits".)*
    **Testable:** a quadrant claimed while it still has empty cells contributes no entry to
    `legalMoves` thereafter, in either the forced or the free-choice state.
15. Quadrants are claimed **only** by winning the small board inside them. There is no other
    route to claiming a quadrant. *(Rules → Winning the Game.)*
    **Testable:** over a fully played-out game, every transition of `quadrantAt(q)` out of
    `open` into a claimed state coincides with a move completing a line in quadrant *q*;
    filling a small board with no line yields `catGame` (requirement 16), never a claim, and
    no other operation — including `startNextGame()` — ever produces a claimed quadrant.

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
    **The send resolves against the board *after* the move.** A move that claims or
    cat-games the very quadrant it sends to leaves that quadrant dead, so the opponent gets
    a free choice — the ordinary dead-quadrant rule applying, not an exception to it. *(Rules
    → Decisions → Does a move that claims its own send target still send there? — "**The
    send is evaluated against the board *after* the claim.**... The send always resolves
    against the board as it stands after the move that triggers it, and a quadrant that move
    just claimed (or cat-gamed) is dead exactly the same as one that was already dead
    beforehand.")*
    **One still-open quadrant is still free choice, not forced.** When the send lands on a
    dead quadrant and exactly one quadrant remains open, the state is `freeChoice` with
    `activeQuadrant == null` — not `forced` on that last quadrant. The two readings produce
    the same legal moves but render differently, and free choice is what the docs describe:
    *"**Free choice** — *Every* still-open quadrant — could be up to 9"*, a set that is
    simply of size one here. *(Game Board Design → Active Quadrant Highlight → The
    free-choice state, mode table; Rules → Edge Cases — "Any still-open quadrant is fair
    game".)*
    **Testable, three assertions:** (a) a move sending the opponent to a claimed quadrant,
    and the same against a cat-game quadrant, both yield `placementState == freeChoice` and
    `activeQuadrant == null`; (b) from a board with exactly one open quadrant, such a move
    still yields `freeChoice` with `activeQuadrant == null`, and `legalMoves` holds exactly
    that quadrant's empty cells; (c) **the self-sending claim** — playing the cell whose
    index equals its own quadrant's index (say `Move(quadrant: 5, cell: 5)`) where that move
    completes quadrant 5's small board — yields `placementState == freeChoice`,
    `activeQuadrant == null`, and a `legalMoves` set spanning every still-open quadrant,
    **not** `forced` on the quadrant just claimed and **not** an empty legal-move set. The
    same assertion holds when that move cat-games quadrant 5 instead of claiming it. This is
    the case reviewers name as the most common defect in an ultimate-tic-tac-toe engine, and
    it must have its own test.
18. The engine exposes which placement state is active — **forced** (exactly one legal
    quadrant, named by `activeQuadrant`), **free choice** (every still-open quadrant, one to
    nine of them), or **game over** (the game is won or drawn, and nothing is legal) — as
    engine state the UI reads rather than as something the UI infers. The opening move is
    the free-choice state (requirement 9), not a state of its own. *(Tech Design → Decisions
    → Is the game logic separate from Flutter?, which names "legal moves, sending rule,
    win/cat-game detection, free-choice state" as engine responsibilities; Game Board Design
    → Active Quadrant Highlight → The free-choice state, whose two in-play modes are Forced
    and Free choice and which says "This also covers the opening move"; for the third state,
    Rules → Winning the Game, → Edge Cases → Big board full, and this PRD's requirement 20 —
    "no further moves are legal" — which `P3-02-move-input.md` requirement 13 consumes as
    "the engine reports no legal moves".)* The accessors are requirement 36.
    **Three states are enough** because a send onto a just-claimed quadrant resolves to free
    choice (requirement 17), so `forced` never names a quadrant with nothing legal in it.
    *(Rules → Decisions → Does a move that claims its own send target still send there?)*
    **Testable:** the three states are mutually exclusive and exhaustive over every reachable
    board, and `gameOver` holds exactly when `outcome != inProgress` (requirement 37).
19. **Legal-move computation.** In the forced state the legal moves are exactly the empty
    cells of the forced quadrant. In the free-choice state they are the empty cells of every
    still-open quadrant. In the game-over state there are none. Cells that are occupied, and
    every cell in a claimed or cat-game quadrant, are never legal. *(Rules → Placement
    Rules; Edge Cases → Sent to a dead quadrant; → Decisions → Does a move that claims its
    own send target still send there?; Game Board Design → Active Quadrant Highlight.)*
    **Testable, three assertions:** (a) in a forced state, `legalMoves` equals exactly the
    empty cells of `activeQuadrant`, and every entry has `quadrant == activeQuadrant`; (b)
    in a free-choice state, `legalMoves` equals the union of the empty cells of every
    `QuadrantState.open` quadrant, and contains no cell of a claimed or cat quadrant; (c)
    `legalMoves` is empty **if and only if** `placementState == gameOver`, so an in-progress
    board always offers at least one move — including immediately after the self-sending
    claim of requirement 17(c).

### Ending a game

20. Three **claimed quadrants in a row** on the big board — row, column, or diagonal — wins
    the game, effective on the claim that completes the line. The game is over; no further
    moves are legal. *(Rules → Turn Structure 5; Winning the Game.)*
    **Testable:** for each of the 8 big-board lines (the quadrant-index triples of
    requirement 13's list), the move whose claim completes it yields the mover's win
    outcome, `placementState == gameOver`, and an empty `legalMoves` — with open quadrants
    and empty cells still remaining on the board.
21. If **no quadrant remains open** (every quadrant is claimed or cat game) and no player has
    three claimed quadrants in a row, the game is a **straight draw** — a tie.
    **Most-quadrants-claimed does not win; the count is irrelevant.** *(Rules → Edge Cases →
    Big board full with no three-in-a-row → straight draw.)*
    **Testable:** a filled big board where one player holds 5 quadrants and the other 3 with
    no line reports a tie, not a win.
22. The engine reports the game's outcome as one of: in progress, won by Player One, won by
    Player Two, or tie. *(Rules → Winning the Game and Edge Cases; Game Board Design →
    Scoreboard, whose three counters are Player One / Ties / Player Two.)* The accessor is
    requirement 37.
    **Testable:** driving a board to each of the three terminal results reports the matching
    `GameOutcome`, and it stays that value on every later read of that board; a board with
    any quadrant still open and no completed big-board line reports `inProgress`. This is
    the accessor `P3-04-game-over-rematch.md` requirement 1 activates its game-over surface
    from, including after rehydration from storage.
23. The engine's state includes the **most recent completed move** (which quadrant, which
    cell), which is what the last-move highlight renders from and what has to survive
    leaving and resuming a game. *(Game Board Design → Last Move Highlight and → Lifetime;
    Menus and UI → Persistence → Leaving a game mid-play.)* The accessor and its empty-board
    form are requirement 40.
    **Testable:** after any `applyMove(b, m)` the result's `lastMove == m`; on
    `Board.newSeries()` and on the board returned by `startNextGame()` it is null, so no
    consumer can draw a last-move highlight on a board nobody has played.

### The series

24. Engine state for an open game covers the **whole series** — the board plus the running
    score of Player One / Ties / Player Two — because each open game carries its own
    scoreboard and resuming a game resumes the series, not just the last board. *(Game
    Overview → Decisions → Scoreboard lifetime; Session Structure — Games and Continuing;
    Menus and UI → Decisions → What does an open game hold?)* The accessor is requirement
    39. Writing that state to storage belongs to `P1-04-persistence.md`.
    **Testable:** the score is reachable from the same `Board` value `applyMove` returns,
    with no second object to thread — `P1-04-persistence.md` requirement 7 persists the
    board, the last move, the current player and the score together, and can take all four
    from one value.
25. **Turn order across games.** Game 1: Player One goes first. After a win: the winner of
    the last game goes first. After a tie: the player who went first in the tied game goes
    first again. The engine therefore retains who went first in the current game
    (requirement 39). *(Rules → Turn Order Across Games; Rules → Decisions → Who goes first
    after a tie?; Game Overview → Session Structure.)*
    **Testable:** three consecutive games — a Player Two win, then a tie, then a Player One
    win — produce first players Player One, Player Two, Player Two, Player One.
26. Starting the next game in a series **resets the board** and applies requirement 25 to
    choose its first player. It **leaves the score untouched** — by requirement 27 the
    finished game was already counted when it ended, so starting the next game must not
    move any counter. *(Menus and UI → Decisions → What happens when a game ends? — "It
    resets the board for the next game"; → Decisions → When does the scoreboard increment —
    "Taking the rematch only resets the board"; Game Overview → Session Structure —
    "Continuing **resets the board**".)* The operation is requirement 34.
    **Testable:** the three counters immediately after `startNextGame()` are identical to
    their values immediately before it, and the returned board's cells, quadrants, placement
    state and `lastMove` equal a fresh game's.
27. **The series score increments as part of resolving the game, at game end** — the
    winner's column, or the **Ties** column on a straight draw, goes up by one on the move
    that ends the game, not when a rematch is taken. *(Menus and UI → Decisions → When does
    the scoreboard increment — "**At game end.** The winner's column, or Ties, increments as
    soon as the game is won or tied — not when a rematch is taken"; Game Board Design →
    Scoreboard — "Increments when a game ends"; Rules → Edge Cases → "The Ties counter on
    the scoreboard goes up one"; Game Overview → Session Structure.)*
    **Testable:** the `Board` returned by the winning or drawing `applyMove` already has
    that column one higher and the other two unchanged, with no further call — which is why
    requirement 29 puts the score on that same type; and across a series of *n* finished
    games the three counters sum to *n* whether or not each was followed by another game.
    The presentation side of this same answer is `P3-03-scoreboard-turn-indicator.md`
    requirement 4 and `P3-04-game-over-rematch.md` requirement 4 — this requirement is the
    engine-side statement that the score is series state changed by the game resolving.
    Requirement 42 is what keeps the increment bound to exactly one move: a second
    `applyMove` on a finished board throws rather than resolving that game again.

### Tests

28. The engine has **unit tests** — this is where the real complexity is. They are written
    from these requirements, against the surface named in requirements 29–42, not from the
    implementation. *(Tech Design → Decisions → Unit tests for the rules engine.)*

### The public API

The named surface. Consuming PRDs bind to these symbols rather than to prose. All of it
lives under `lib/engine/` and obeys requirements 1–3.

29. **`Board` is the engine's whole-game-plus-series state**, and it is the type in
    requirement 3's `Board applyMove(Board, Move)`. One value carries: the 81 cells, the 9
    quadrant states, the placement state and active quadrant, the current player, the last
    completed move, the outcome, the series score, and who went first in the current game.
    **This resolves an ambiguity in requirement 3.** Requirement 27 requires the value
    returned by the game-ending `applyMove` to already carry the incremented score, and
    requirements 24–25 put the score and the first-player-this-game in engine state, so what
    comes back cannot be a bare grid. Two resolutions were available: treat `Board` as the
    whole-game type, or introduce an outer type and change requirement 3's signature. **This
    PRD takes the first**, because the signature is fixed verbatim by `Tech Design.md` →
    Decisions → Game state is immutable, and no design doc names an outer type. Consequences,
    stated so nobody re-derives them:
    - `P3-02-move-input.md` requirement 22, which already copied `Board applyMove(Board,
      Move)`, stays correct **verbatim** — nothing to change there.
    - `P1-04-persistence.md` requirement 7 serializes one `Board` per open game, plus that
      PRD's own opponent name and record id — not a board plus score side-cars.
    - The name `Board` is narrower than what it holds. That is the design doc's word, kept
      deliberately rather than silently improved; renaming it is a `Tech Design.md` edit for
      `forge-doc-writer`, not a change made here.
30. **`Move` has exactly two fields:** `int quadrant` (0–8) and `int cell` (0–8), both under
    requirement 31's indexing. It carries **no player field** — the mover is the pre-move
    `board.currentPlayer` (requirement 38), which is what makes alternation (requirement 8)
    the engine's to enforce rather than the caller's to get right. `Move` is a `freezed`
    value type with value equality, so two equal moves are interchangeable and membership
    tests against `legalMoves` work. *(Shape corroborated by Design Handoff → State, whose
    `lastMove` and `pendingSelection` are both `{ quadrant, cell }`, and by
    `P3-02-move-input.md` requirement 21, which names the same pair. Its persisted JSON
    field names remain OQ-3.)*
    **Testable:** `Move(quadrant: 3, cell: 7) == Move(quadrant: 3, cell: 7)`, and a `Set`
    de-duplicates them.
31. **Indices are 0-based, 0–8, row-major from the top-left**, for both quadrants and cells:
    0 1 2 across the top row, 3 4 5 the middle, 6 7 8 the bottom — so 0 is top-left, 4 is
    centre, 8 is bottom-right, with `row == index ~/ 3` and `column == index % 3`. The same
    numbering applies to a cell within its small board and to a quadrant within the big
    board, which is what makes requirement 12 the identity `activeQuadrant == move.cell`.
    *(Base and range from Design Handoff → State — `cells[9][9]`, `quadrants[9]`,
    `activeQuadrant // 0..8, or null = free choice`; row-major order from `Rules.md` → Cell
    → Quadrant Mapping, whose 1–9 labels are that same order, one-based. The approved
    handoff is the reference asset for the numbering, and no doc contradicts it.)*
    **Testable:** every test literal in this PRD resolves — playing cell 4 sends to quadrant
    4, `quadrantAt(0)` is the top-left quadrant, and cells `{0,4,8}` are the
    top-left-to-bottom-right diagonal.
32. **`Board.newSeries()`** constructs a brand-new series: all 81 cells empty, all 9
    quadrants `open`, `score` 0/0/0, `firstPlayerThisGame == Player.one`,
    `currentPlayer == Player.one`, `lastMove == null`, `placementState == freeChoice`,
    `activeQuadrant == null`, `outcome == inProgress`. *(Rules → Setup; → Turn Order Across
    Games — "Game 1: Player One goes first".)*
33. **`Board applyMove(Board board, Move move)`** returns the new state. On the returned
    board: the cell holds the pre-move `currentPlayer`'s mark; `lastMove` is `move`;
    `currentPlayer` has alternated (requirement 38); the quadrant is re-evaluated for claim
    or cat game (requirements 13, 16) **before** the send is resolved (requirement 17);
    `placementState` and `activeQuadrant` follow requirements 11, 17 and 18; `outcome`
    follows requirements 20–21; and if the move ended the game, `score` is already
    incremented (requirement 27). The input board is unchanged (requirement 3). If the move
    is not legal, or the board is already finished, it **throws instead of returning** —
    requirement 42.
34. **`Board startNextGame()`** is requirement 26's next-game operation — the engine side of
    what `P3-04-game-over-rematch.md` requirement 6 calls taking the rematch. It returns a
    board whose cells, quadrants, `lastMove`, `placementState`, `activeQuadrant` and
    `outcome` are as `newSeries()` leaves them, whose `score` is **unchanged**, and whose
    `firstPlayerThisGame` and `currentPlayer` are both requirement 25's answer for the game
    just finished. It is a method on `Board` because it needs that finished game's result
    and first player to compute the next one.
    **Testable:** called on a Player-Two win it yields `currentPlayer == Player.two` and an
    unchanged score; called on a tie it yields the tied game's `firstPlayerThisGame`.
35. **`Set<Move> get legalMoves`** is requirement 19's legal-move query — a `Set` of
    value-equality members, so `legalMoves.contains(Move(quadrant: q, cell: c))` is the
    per-cell legality check `P3-02-move-input.md` requirements 11–12 run across all 81
    cells. It is also the predicate requirement 42 throws on.
36. **`PlacementState get placementState`** and **`int? get activeQuadrant`** are requirement
    18's accessors. `PlacementState` is `{ forced, freeChoice, gameOver }`. `activeQuadrant`
    is non-null **exactly when** the state is `forced`, and null in the other two — so a
    consumer branches on `placementState`, never on `activeQuadrant == null` alone, which
    would read a finished game as free choice. A `forced` state always has at least one
    legal move in the quadrant it names, because requirement 17 sends a player onto a
    just-claimed quadrant into free choice instead.
37. **`GameOutcome get outcome`** is requirement 22's accessor, with values `{ inProgress,
    playerOneWins, playerTwoWins, tie }`. `placementState == gameOver` holds exactly when
    `outcome != inProgress`.
38. **`Player get currentPlayer` is engine state**, not something a consumer derives.
    `Player` is `{ one, two }`. `P1-04-persistence.md` requirement 7 persists it,
    `P3-03-scoreboard-turn-indicator.md` requirement 9 reads it for the turn indicator, and
    `P3-02-move-input.md` requirement 1 asserts it. **It must not be derived from move
    parity**: requirement 25 makes Player Two the first player of some games, and a parity
    implementation passes a single-game test suite while silently inverting the turn
    indicator for every later game in a series. It alternates on every `applyMove`,
    **including the one that ends the game**, so after a terminal move it names the mover's
    opponent; consumers that must not present a turn on a finished game gate on
    `placementState == gameOver` (requirement 36), never on this value.
    *Interface choice, recorded so it stays visible:* alternating on the terminal move keeps
    requirement 8 exceptionless and `currentPlayer` single-meaning. The alternative — freeze
    it at the player who made the winning move — is a one-line change that would alter only
    what a turn indicator drawn behind the game-over overlay shows. No doc chooses between
    them.
    **Testable:** on `newSeries()` it is `Player.one`; it differs from its pre-move value
    after every `applyMove`, including the terminal one; after `startNextGame()` it equals
    `firstPlayerThisGame`.
39. **`Score get score`** and **`Player get firstPlayerThisGame`** are requirements 24 and
    25's accessors. `Score` is a `freezed` value type with three non-negative `int` fields —
    `playerOne`, `ties`, `playerTwo` — one per scoreboard column.
40. **`Move? get lastMove`** is requirement 23's accessor. It is **null**, not a sentinel, on
    `Board.newSeries()` and on the board returned by `startNextGame()`. A sentinel such as
    `Move(quadrant: 0, cell: 0)` or an index of `-1` would make
    `P3-01-board-rendering.md`'s last-move ring draw on a cell nobody played, on the first
    board of every rematch.
41. **Reading the board:** `Player? cellAt(int quadrant, int cell)` returns null for an empty
    cell, and `QuadrantState quadrantAt(int quadrant)` returns one of `{ open,
    claimedByPlayerOne, claimedByPlayerTwo, catGame }` — requirement 5's two value sets, and
    what `P3-01-board-rendering.md` renders its 81 cells and 9 quadrant states from.
42. **The engine throws on an illegal move.** `applyMove` raises `IllegalMoveError` — never
    returns the board unchanged, and never returns a result object the caller might ignore —
    in exactly two conditions, distinguished by an `IllegalMoveReason` on the error:
    - **`gameAlreadyFinished`** — `board.placementState == gameOver` (equivalently
      `outcome != inProgress`). Checked **first**, so a move on a finished board always
      reports this reason rather than `notLegal`, even though such a board also has an empty
      `legalMoves`.
    - **`notLegal`** — the board is in progress and `!board.legalMoves.contains(move)`. This
      covers every way a move can be wrong: an occupied cell, a cell outside the forced
      quadrant, any cell of a claimed or cat-game quadrant, and an out-of-range index under
      requirement 31.

    `IllegalMoveError` extends Dart's `Error`, not `Exception`, because this is a contract
    violation rather than a recoverable condition, and it carries the offending `Move` and
    the `Board` state it was applied to so a crash report can say what happened.
    *(Rules → Decisions → What happens if an illegal move reaches the engine? — "**The engine
    throws.** An illegal move, or any move applied to an already-finished game, raises rather
    than returning silently... *I think failing loud and throwing an error is correct when in
    theory the UI should never allow it to begin with.*" The two-reason split, the error type
    and its payload are this PRD's interface work; the throw itself and both conditions are
    the Decision's.)*
    **Why this is a defensive contract and not a hostile one:** it is unreachable through
    the UI by construction. `P3-02-move-input.md` requirement 10 makes illegal cells absorb
    taps and do nothing, its requirement 11 reads legality from this engine rather than
    re-deriving it, and its requirement 13 makes a finished game accept no input at all — so
    the only caller in the app never produces either condition, and requirement 22 of that
    PRD applies moves through this same signature. A throw therefore surfaces a real defect
    loudly instead of silently returning stale state, which is the framing the Decision
    gives it.
    **Testable, both conditions:** (a) on an in-progress board, `applyMove` with a move not
    in `legalMoves` — one per category: an occupied cell, a cell outside the forced
    quadrant, a cell in a claimed quadrant, a cell in a cat-game quadrant, and an index
    outside 0–8 — throws `IllegalMoveError` with reason `notLegal`, and the input board is
    unchanged; (b) on a board whose game is won, and again on one that is drawn, `applyMove`
    with **any** move — including one that would have been legal a move earlier — throws
    with reason `gameAlreadyFinished`, and the three score counters are identical before and
    after the throw, so the finished game cannot be counted twice against requirement 27.

## Out of Scope

Named here so the boundary is explicit. Each is specified elsewhere; do not specify it
here.

- **Rendering, the three highlights, and quadrant/cell visual states** —
  `P3-01-board-rendering.md`. The engine supplies the state; it draws nothing and holds no
  theme value.
- **The two-tap select-then-confirm gesture, the pending selection, illegal taps, and
  haptics** — `P3-02-move-input.md`. A pending selection is input state, never engine state.
  That PRD is also what makes requirement 42's throw unreachable in the app.
- **Catching, reporting or recovering from `IllegalMoveError`.** The engine raises it;
  what the app does with an unhandled error — the catch sites and the crash-report object —
  is `P1-06-crash-reporting.md`.
- **The scoreboard UI and the turn indicator** — `P3-03-scoreboard-turn-indicator.md`. The
  engine owns the score *data* as part of series state; the display is not its problem.
- **The game-over surface and the rematch control** — `P3-04-game-over-rematch.md`. The
  engine reports the outcome and counts it; offering the rematch and drawing the result are
  that PRD's.
- **Storage — the Hive box, the repository interface, the open-games list, the game cap,
  `shared_preferences`** — `P1-04-persistence.md`. The engine generates `toJson`/`fromJson`
  and stops there.
- **The opponent name and the open game's record id.** They title and identify a saved game;
  neither is a rule, and no requirement here puts them on `Board`.
  `P1-04-persistence.md` requirement 7 owns them.
- **Anything from `Alternative Game Styles.md`**, including Lock-In Style. That is a
  parking-lot doc and explicitly not the game being built.
- **Themes, animations, sounds, menus, and screen flow** — none of it reaches `engine/`.
- **AI opponent and online multiplayer.** *(Game Overview → Decisions → Single-player / AI
  opponent — "No.")* Note the standing constraint that tech choices must not foreclose
  syncing board state over a network *(Tech Design → Decisions → Online multiplayer is an
  intended future direction)*; nothing is built for it now.

## Open Questions

Numbering is stable — answered questions stay as stubs, because other PRDs cite these
numbers. **No behavioral question is open.** OQ-1, OQ-2, OQ-5 and OQ-6 are answered; OQ-3
and OQ-4 concern the persisted JSON only, are fenced below, and block nothing here.

**OQ-1 — Answered and closed.** *Does the first player's opening cell send the second
player, or is the second player bound to the opening quadrant?* Settled in `Rules.md` →
Decisions → **Does the opening move send the opponent?**: *"**Yes — the cell the first
player plays sends the second player, exactly as on every later move. There is no exception
for move 1.**"* Requirements 10 and 11 carry the answer.

**OQ-2 — Answered and closed.** *When does the score increment — at game end, or when the
rematch is taken?* Settled in `Menus and UI.md` → Decisions → **When does the scoreboard
increment**: *"**At game end.**"* Requirements 26 and 27 carry the answer.

**OQ-3 — The persisted JSON shape, only.** The in-memory surface is settled by requirements
29–42; what is still open is the **serialized** form — the JSON field names and nesting
`toJson`/`fromJson` produce, including how the cells, the quadrants and `lastMove` are
written. `Tech Design.md`, alongside Decisions → Serialization and the storage layer, records
the handoff's sketch — *"cells, quadrants, activeQuadrant, currentPlayer, lastMove, score,
firstPlayerThisGame"* — as *"a design sketch, not a decision taken here."* In practice this
is the storage layer's call and it is carried by `P1-04-persistence.md` → Open Questions →
1. Persisted data — versioning. No requirement above depends on the answer.

**OQ-4 — Persisted data, versioning.** From `Tech Design.md` → Open Questions 1: *"When the
shape of stored data changes — a fifth preference is added, a key is renamed, an open game
gains a field — what happens to data already on the device? A game written by v1.0 has to
still load in v1.1."* It reaches the engine because `toJson`/`fromJson` are generated into
`engine/`. **Fenced, matching `P1-04-persistence.md`:** no migration hooks, schema-version
fields, or upgrade paths are designed here. Requirement 2 requires round-tripping today's
shape and nothing more.

**OQ-5 — Answered and closed.** *What does the engine do when handed an illegal move, or a
move on an already-finished game?* Settled in `Rules.md` → Decisions → **What happens if an
illegal move reaches the engine?**: *"**The engine throws.** An illegal move, or any move
applied to an already-finished game, raises rather than returning silently,"* with the
reasoning *"failing loud and throwing an error is correct when in theory the UI should never
allow it to begin with"* and the note that the already-finished case *"is the one where a
silent return risks counting a game twice."* Requirement 42 is the contract and its tests;
requirement 33 points at it.

**OQ-6 — Answered and closed.** *A move that claims (or cat-games) the very quadrant it
sends the opponent to — which state does the send see, before or after the move?* Settled in
`Rules.md` → Decisions → **Does a move that claims its own send target still send there?**:
*"**The send is evaluated against the board *after* the claim.**... The quadrant is dead by
the time the send resolves, so the opponent gets a **free choice** of any still-open
quadrant,"* framed there as the ordinary dead-quadrant rule applying rather than an
exception to it. This is the answer requirements 17, 18, 19 and 36 were already written
against, so nothing was restructured; requirement 17 states it with the citation, and
requirement 17(c) is its test.
