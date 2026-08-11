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
> here; OQ-3 and OQ-4 concern the persisted JSON only and are fenced, OQ-7 collects three
> unspecified edges found in review, and OQ-8 records one edge on requirement 43's winning
> line.

> **Three user settlements live in this PRD and in no design doc.** Requirement 43's
> `winningLine` accessor is one, requirement 17's *free choice on the last open quadrant* is
> the second — that one confirms what this PRD had inferred, which changes its standing even
> though it changed no text of the rule — and requirement 42's **`toString()` contract on
> `IllegalMoveError`** is the third, which resolves the payload contradiction earlier
> revisions flagged against `P1-06-crash-reporting.md` req 17. Landing all three in
> `Rules.md` and `Tech Design.md` is `forge-doc-writer`'s, not this PRD's.

> **Requirement numbers are stable, and nothing below has been renumbered** — the named
> surface was appended as requirements 29–42, and requirement 43 was appended after it for
> the same reason. Other PRDs cite these numbers heavily; treat any list of *which* PRDs cite
> *which* requirements as **indicative rather than exhaustive** and verify with a search
> before relying on it. Earlier revisions of this note carried a concrete list that had
> already gone stale and substantially understated the inbound citations — a list of that
> kind cannot be kept true from inside this file, so it is not maintained here. The stability
> guarantee is the part that matters and it still holds.

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
won — and with which three quadrants — and when the game is a straight draw. Every rule in
`Rules.md` is enforced by the engine and covered by unit tests; no UI layer implements any
of it.

## Requirements

> **Read requirements 29–43 first.** They name the types, accessors, operations and error
> contract the behavioral requirements below are written against, and they are what the
> consuming PRDs bind to. They sit last only so the existing numbering stays stable.

### Architecture and representation

1. The engine lives under `lib/engine/` and is **pure Dart with zero Flutter imports**. It
   must not import any Hive package or any Flutter package. *(Tech Design →
   Decisions → Is the game logic separate from Flutter?; Serialization and the storage
   layer — "`hive_flutter` is not pure Dart, so it must never be imported from `engine/`";
   Project structure — layer-first, whose tree names `engine/board.dart` and
   `engine/rules.dart`.)*
   **The Hive packages are `hive_ce` + `hive_ce_flutter`**, settled by the user and recorded
   in `P1-01-app-scaffold.md` → *Confirmed by the user* and its req 14 — the design doc names
   the older `hive` / `hive_flutter` spelling and the rule is unchanged either way.
   **Testable:** a source scan of `lib/engine/` finds no `package:flutter` import and **no
   import whose package segment begins `hive`** — the same form `P1-01-app-scaffold.md`
   req 5 states, which catches `hive`, `hive_flutter`, `hive_ce` and `hive_ce_flutter`
   alike, so the scan survives the choice ever being revisited. A scan naming only the two
   literals `package:hive` and `package:hive_flutter` would pass against the packages the
   project actually uses, which is the defect this wording removes.
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

   **Testable, as a concrete identifier list.** These are **all** the symbols requirements
   29–43 require — the types and enum values *and every operation and accessor*. An earlier
   revision listed only the former while claiming to enumerate the whole surface, which left
   thirteen members of the published API unnamed by the one requirement that exists to fix
   their spelling.

   *Types and values:* `Board`, `Move`, `Move.quadrant`, `Move.cell`, `Player.one`,
   `Player.two`, `QuadrantState.open`, `QuadrantState.claimedByPlayerOne`,
   `QuadrantState.claimedByPlayerTwo`, `QuadrantState.catGame`, `PlacementState.forced`,
   `PlacementState.freeChoice`, `PlacementState.gameOver`, `GameOutcome.inProgress`,
   `GameOutcome.playerOneWins`, `GameOutcome.playerTwoWins`, `GameOutcome.tie`,
   `Score.playerOne`, `Score.ties`, `Score.playerTwo`, `IllegalMoveError`,
   `IllegalMoveReason.notLegal`, `IllegalMoveReason.gameAlreadyFinished`.

   *Operations and accessors:* `applyMove` (requirement 33), `Board.newSeries`
   (requirement 32), `startNextGame` (requirement 34), `legalMoves` (requirement 35),
   `placementState` and `activeQuadrant` (requirement 36), `outcome` (requirement 37),
   `currentPlayer` (requirement 38), `score` and `firstPlayerThisGame` (requirement 39),
   `lastMove` (requirement 40), `cellAt` and `quadrantAt` (requirement 41), and
   `winningLine` (requirement 43).

   No abbreviation of *quadrant* to *quad*, and no `p1`/`p2` anywhere in the public API.

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

    **Testable, with both carve-outs stated, because the bare invariant is false on two
    reachable moves.** For any in-progress board and any legal move *m*, the resulting board
    has `activeQuadrant == m.cell` — **except**:
    - **the dead-target case (requirement 17):** if quadrant `m.cell` is claimed or a cat
      game on the board *after* the move — including when *m* itself claimed or cat-gamed
      it — the result is `placementState == freeChoice` with `activeQuadrant == null`; and
    - **the game-over case (requirements 20–21):** if *m* ended the game, the result is
      `placementState == gameOver` with `activeQuadrant == null` per requirement 36, whatever
      `m.cell` was.

    A test asserting `activeQuadrant == m.cell` unconditionally over legal moves **fails a
    correct engine** on the winning or drawing move, because requirement 36 requires
    `activeQuadrant` to be null in both non-`forced` states. Assert the identity only on
    fixtures where the move neither ends the game nor sends onto a dead quadrant, and assert
    the two exceptions as their own cases.
12. The **cell → quadrant mapping is positional identity**: the 3x3 position of the cell
    within its small board is identical to the 3x3 position of the quadrant within the big
    board — top-left cell → top-left quadrant, centre cell → centre quadrant, and so on for
    all 9 positions. *(Rules → Cell → Quadrant Mapping.)* Under requirement 31's indexing
    this is exactly `activeQuadrant == move.cell`, which is the form to implement and test
    against. The 1–9 labels in the `Rules.md` diagram are for human reading; **requirement
    31 is the authoritative index base**, so no one needs that diagram to write a test.

    **Testable, carrying the same two carve-outs as requirement 11.** For each of the 9 cell
    indices *c*, playing index *c* in any quadrant yields `activeQuadrant == c` — **provided
    quadrant *c* is still open on the resulting board (requirement 17) and the move did not
    end the game (requirements 20–21)**. Both conditions are satisfiable for all nine
    indices, so the nine-case sweep is still writable; it just has to choose its fixtures.
    Where either condition fails, `activeQuadrant` is null by requirement 36 and this
    identity is not the property under test. The reason this matters here as well as in
    requirement 11: the self-sending case — playing cell *c* inside quadrant *c* — is
    exactly the fixture an implementer reaches for when sweeping all nine indices, and it is
    also the case requirement 17(c) singles out as the most common defect.

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
    **One still-open quadrant is still free choice, not forced — confirmed by the user.**
    When the send lands on a dead quadrant and exactly one quadrant remains open, the state
    is `freeChoice` with `activeQuadrant == null` — **not** `forced` on that last quadrant.
    This PRD had **inferred** that from the mode table — *"**Free choice** — *Every*
    still-open quadrant — could be up to 9"*, a set that is simply of size one here — and
    **the user has now confirmed the inference, so it is a settlement rather than a
    reading.** It needed confirming rather than deriving precisely because nothing testable
    at the rules level distinguishes the two: **the legal moves are identical either way**,
    and the whole difference is visual. The board draws the open-state (available) treatment
    on that one quadrant rather than the forced ring — `P3-01-board-rendering.md` req 8
    states the same consequence from the rendering side (*"A free-choice state with exactly
    one still-open quadrant still renders as available, not forced"*), so the two PRDs agree
    as written. *(Game Board Design → Active Quadrant Highlight → The free-choice state,
    mode table; Rules → Edge Cases — "Any still-open quadrant is fair game". The
    confirmation itself is the user's and is recorded in no design doc.)*
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
    *All three assume the move did not also end the game* — a move that completes a
    big-board line yields `gameOver`, not `freeChoice`, and requirements 20–21 own that case.
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
    moves are legal. *(Rules → Turn Structure 5; Winning the Game.)* **Which three quadrants
    they were is published** — requirement 43.
    **Testable:** for each of the 8 big-board lines (the quadrant-index triples of
    requirement 13's list), the move whose claim completes it yields the mover's win
    outcome, `placementState == gameOver`, an empty `legalMoves`, and `activeQuadrant ==
    null` — with open quadrants and empty cells still remaining on the board.
21. If **no quadrant remains open** (every quadrant is claimed or cat game) and no player has
    three claimed quadrants in a row, the game is a **straight draw** — a tie.
    **Most-quadrants-claimed does not win; the count is irrelevant.** *(Rules → Edge Cases →
    Big board full with no three-in-a-row → straight draw.)*
    **Testable:** a filled big board where one player holds 5 quadrants and the other 3 with
    no line reports a tie, not a win; `placementState == gameOver` and `activeQuadrant ==
    null` on that board — and `winningLine` is **null**, per requirement 43.
22. The engine reports the game's outcome as one of: in progress, won by Player One, won by
    Player Two, or tie. *(Rules → Winning the Game and Edge Cases; Game Board Design →
    Scoreboard, whose three counters are Player One / Ties / Player Two.)* The accessor is
    requirement 37, and on the two winning values the line itself is requirement 43.
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
    from these requirements, against the surface named in requirements 29–43, not from the
    implementation. *(Tech Design → Decisions → Unit tests for the rules engine.)*
    *How a test builds a board is not specified here — see OQ-7*, which matters more than it
    looks: the obvious shortcut binds the whole suite to a JSON shape OQ-3 leaves open.

### The public API

The named surface. Consuming PRDs bind to these symbols rather than to prose. All of it
lives under `lib/engine/` and obeys requirements 1–3.

29. **`Board` is the engine's whole-game-plus-series state**, and it is the type in
    requirement 3's `Board applyMove(Board, Move)`. One value carries: the 81 cells, the 9
    quadrant states, the placement state and active quadrant, the current player, the last
    completed move, the outcome and its winning line, the series score, and who went first
    in the current game.
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
      PRD's own opponent name, record id and timestamps — not a board plus score side-cars.
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
    `activeQuadrant == null`, `outcome == inProgress`, `winningLine == null`. *(Rules →
    Setup; → Turn Order Across Games — "Game 1: Player One goes first".)*
33. **`Board applyMove(Board board, Move move)`** returns the new state. On the returned
    board: the cell holds the pre-move `currentPlayer`'s mark; `lastMove` is `move`;
    `currentPlayer` has alternated (requirement 38); the quadrant is re-evaluated for claim
    or cat game (requirements 13, 16) **before** the send is resolved (requirement 17);
    `placementState` and `activeQuadrant` follow requirements 11, 17 and 18; `outcome`
    follows requirements 20–21 and `winningLine` follows requirement 43; and if the move
    ended the game, `score` is already incremented (requirement 27). The input board is
    unchanged (requirement 3). If the move is not legal, or the board is already finished,
    it **throws instead of returning** — requirement 42.
34. **`Board startNextGame()`** is requirement 26's next-game operation — the engine side of
    what `P3-04-game-over-rematch.md` requirement 6 calls taking the rematch. It returns a
    board whose cells, quadrants, `lastMove`, `placementState`, `activeQuadrant`, `outcome`
    and `winningLine` are as `newSeries()` leaves them, whose `score` is **unchanged**, and
    whose `firstPlayerThisGame` and `currentPlayer` are both requirement 25's answer for the
    game just finished. It is a method on `Board` because it needs that finished game's
    result and first player to compute the next one.
    **Testable:** called on a Player-Two win it yields `currentPlayer == Player.two` and an
    unchanged score; called on a tie it yields the tied game's `firstPlayerThisGame`.
    *What it does when called on a board that is **not** finished is unspecified — OQ-7.*
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
    **This is the clause requirements 11 and 12 carve out against:** on the move that ends
    the game, `activeQuadrant` is null no matter which cell was played.
37. **`GameOutcome get outcome`** is requirement 22's accessor, with values `{ inProgress,
    playerOneWins, playerTwoWins, tie }`. `placementState == gameOver` holds exactly when
    `outcome != inProgress`. It is also the value requirement 43's `winningLine` is read
    against: non-null on the two winning values, null on the other two.
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
    *What either returns for an index outside 0–8 is unspecified — OQ-7.*
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

    **`IllegalMoveError.toString()` renders the reason and the `Move`, and never the
    board — settled by the user.** The error object **keeps** the `Board` field named above;
    **nothing renders it into text.** `toString()` returns the `IllegalMoveReason` and the
    move's two indices, and nothing drawn from the board. This is the resolution of the
    contradiction earlier revisions of this PRD flagged against `P1-06-crash-reporting.md`
    req 17, and **both PRDs now state it** — `P1-06` req 19 carries the same contract from the
    consuming side. The debugging value this payload was written for survives where it is
    actually used, a debugger attached in process; what does not survive is the board reaching
    a rendered report or a log line.

    **Why the contract belongs on this requirement rather than being left to an implementer:**
    `P1-06` req 3 stores **`final Object error`** — the error object itself — so every way a
    crash report is ever rendered as text calls this `toString()`. An unconstrained one is
    what would actually put an 81-cell board position inside a report whose field set
    (`P1-06` req 17, sourced to `Tech Design.md` → Decisions → *What does a crash report
    capture?* — "the error, the stack trace, and a timestamp. Nothing else. No game state, no
    screen") exists to exclude it, through a field `P1-06`'s three-field check cannot see,
    because the leak is *inside* `error` rather than beside it.

    **Testable, as part of this requirement:** `toString()` on a thrown `IllegalMoveError`
    contains the `IllegalMoveReason` and both of the offending move's indices, and contains
    **no board content**. Asserted against a board with a distinctive position: the output
    contains neither `board.toString()` nor any of the field names a `freezed`
    `Board.toString()` prints (`cells`, `quadrants`, `score`). A source-level companion,
    because a string assertion can pass by accident on a sparse fixture — the `toString()`
    implementation references the reason and the move and **does not reference `board`**.

    **The residual is real, and it belongs to whoever adds serialization.** This constrains a
    *string*, not the object: the `Board` is still on the error, so anything that renders or
    copies the error by another route re-leaks the position — a `toJson` added to the error,
    a **persisted** crash report (`P1-06` → Open Question 5), or any reflective or generated
    serializer that walks it. `P1-06` req 19 records the same residual from its side and its
    Open Question 5 now carries it as a constraint on the answer. **Nothing here designs that
    persistence**, and no requirement in this PRD gives `IllegalMoveError` a `toJson`.

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

43. **`List<int>? get winningLine` — the three quadrants that won it.** On a won game it
    returns the **big-board quadrant indices** (requirement 31's 0–8 indexing) of the three
    claimed quadrants forming the completed line — one of the 8 triples requirement 20 names,
    which are the same triples requirement 13 lists, read against quadrants rather than
    cells. All three are claimed by the winner, so `quadrantAt(q)` on each equals
    `QuadrantState.claimedByPlayerOne` when `outcome == playerOneWins` and
    `QuadrantState.claimedByPlayerTwo` when `outcome == playerTwoWins`.
    ***Settled by the user***, and recorded in no design doc — `Rules.md` states the winning
    condition without saying the engine publishes which line met it. Landing it in the doc is
    `forge-doc-writer`'s. **Why it is here in wave 1 rather than added later:** the accessor
    is one line beside the win detection requirement 20 already performs, and adding it after
    the engine has shipped and been tested re-opens an approved PRD — `P3-04`'s, whose
    already-approved handoff copy needed it.

    **Non-null exactly when the game is won; null in every other case.** Stated as a closed
    table rather than left to inference, because `null` here carries two different meanings
    and must not be read as either one alone:

    | Board | `outcome` | `winningLine` |
    |---|---|---|
    | in progress, any position | `inProgress` | **null** |
    | won by either player | `playerOneWins` / `playerTwoWins` | **three indices** |
    | straight draw (requirement 21) | `tie` | **null** |
    | `newSeries()` / `startNextGame()` | `inProgress` | **null** |

    So `winningLine != null` holds **exactly when** `outcome` is `playerOneWins` or
    `playerTwoWins`, which is the invariant a consumer's branch depends on.

    **`null` is not "unknown", and it is not "the game was a draw".** The same discipline
    requirement 36 imposes on `activeQuadrant` applies here, and for the same reason: two
    unrelated states share the null value. A consumer branches on `outcome` (requirement 37)
    and reads this accessor only inside the two winning branches; reading `null` as "draw" is
    wrong on an in-progress board, and reading it as "still playing" is wrong on a tie. The
    accessor cannot distinguish them and is not meant to. There is also **no sentinel** — it
    never returns an empty list, a list containing `-1`, or a three-element list of anything
    but real claimed quadrant indices, so a consumer never has to test for one.

    **Ordering — [PRD decision], reversible.** The three indices come back in **ascending
    order**: the top-left-to-bottom-right diagonal is `[0, 4, 8]` and never `[8, 4, 0]`. A
    `List` has to have *some* order, no doc gives one, and fixing it here is what lets a test
    assert equality instead of sorting first. Reversible at no cost to anything else: a
    consumer wanting a directional order — the order a line is drawn in, say — sorts or
    reverses it itself.

    **When one claim completes two lines at once, exactly one triple is returned.** This is
    reachable: claiming the centre quadrant with `{0, 8}` and `{3, 5}` already claimed
    finishes both a diagonal and the middle row on the same move. **[PRD decision, fenced so
    the value is deterministic and testable]** the triple returned is the **first match in
    requirement 13's canonical order** — `{0,1,2}`, `{3,4,5}`, `{6,7,8}`, `{0,3,6}`,
    `{1,4,7}`, `{2,5,8}`, `{0,4,8}`, `{2,4,6}`. This fences *which value comes back*; it does
    not answer what a player should be *shown* in that case, which is **OQ-8**.

    **Consumers, named so nobody re-derives them:**
    - `P3-04-game-over-rematch.md` — its req 20 omitted the handoff's *"Three boards in a
      row, straight down the middle"* copy solely because reqs 22 and 37 exposed only
      `GameOutcome`. That blocker is gone; whether the shipped copy uses the value is that
      PRD's copy question, not this requirement's, and its OQ-5 closes against this.
    - **A `winGame` animation highlighting the winning quadrants is the expected
      consequence**, for `P2-04-animations.md` (which already carries
      `AnimationMoment.winGame`, fenced out of wave 2 by its req 27) and for
      `P3-01-board-rendering.md` (which would draw the highlight). **This PRD designs no
      animation and adds no rendering requirement.** It supplies a value; what is drawn with
      it, whether it moves, and what it looks like belong to those two PRDs, and neither has
      been amended here.

    **Testable, five assertions:** (a) for each of the 8 big-board lines, the move whose
    claim completes it returns exactly that triple in ascending order, and each of the three
    named quadrants reports the winner's claimed state; (b) an in-progress board returns
    null — including one with two quadrants of a line already claimed, which is the fixture
    that would catch an implementation returning a partial line; (c) requirement 21's
    straight draw returns null; (d) `Board.newSeries()` and the board returned by
    `startNextGame()` both return null; (e) across every board a test reaches,
    `winningLine != null` holds if and only if `outcome` is `playerOneWins` or
    `playerTwoWins`.

## Out of Scope

Named here so the boundary is explicit. Each is specified elsewhere; do not specify it
here.

- **Rendering, the three highlights, and quadrant/cell visual states** —
  `P3-01-board-rendering.md`. The engine supplies the state; it draws nothing and holds no
  theme value. **Including anything drawn from requirement 43's winning line** — the engine
  publishes the triple and specifies no highlight for it.
- **The two-tap select-then-confirm gesture, the pending selection, illegal taps, and
  haptics** — `P3-02-move-input.md`. A pending selection is input state, never engine state.
  That PRD is also what makes requirement 42's throw unreachable in the app.
- **Catching, reporting or recovering from `IllegalMoveError`.** The engine raises it;
  what the app does with an unhandled error — the catch sites and the crash-report object —
  is `P1-06-crash-reporting.md`. **What that report is allowed to contain is that PRD's
  req 17, and the payload conflict earlier revisions flagged is settled:** requirement 42's
  `toString()` renders the reason and the `Move` and never the board, so the error may carry
  the `Board` without the report ever rendering it. `P1-06` req 19 states the same contract
  from the consuming side, and the residual — anything that serializes the error by another
  route — is recorded in both places and designed in neither.
- **The scoreboard UI and the turn indicator** — `P3-03-scoreboard-turn-indicator.md`. The
  engine owns the score *data* as part of series state; the display is not its problem.
- **The game-over surface and the rematch control** — `P3-04-game-over-rematch.md`. The
  engine reports the outcome, the winning line and counts the result; offering the rematch,
  drawing the result and writing the copy are that PRD's.
- **Any `winGame` animation** — `P2-04-animations.md`, whose req 27 fences the moment out of
  wave 2. Requirement 43 makes a winning-quadrant highlight *expressible*; it does not
  schedule, design or authorize one.
- **Storage — the Hive box, the repository interface, the open-games list, the game cap,
  `shared_preferences`** — `P1-04-persistence.md`. The engine generates `toJson`/`fromJson`
  and stops there.
- **The opponent name, the open game's record id, and its two timestamps.** They title,
  identify and order a saved game; none is a rule, and no requirement here puts any of them
  on `Board`. `P1-04-persistence.md` requirements 7 and 21 own them.
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
and OQ-4 concern the persisted JSON only, are fenced below, and block nothing here; OQ-7
collects three edges that are unspecified rather than undecided, and OQ-8 collects one more
that arrived with requirement 43.

**OQ-1 — Answered and closed.** *Does the first player's opening cell send the second
player, or is the second player bound to the opening quadrant?* Settled in `Rules.md` →
Decisions → **Does the opening move send the opponent?**: *"**Yes — the cell the first
player plays sends the second player, exactly as on every later move. There is no exception
for move 1.**"* Requirements 10 and 11 carry the answer.

**OQ-2 — Answered and closed.** *When does the score increment — at game end, or when the
rematch is taken?* Settled in `Menus and UI.md` → Decisions → **When does the scoreboard
increment**: *"**At game end.**"* Requirements 26 and 27 carry the answer.

**OQ-3 — The persisted JSON shape, only.** The in-memory surface is settled by requirements
29–43; what is still open is the **serialized** form — the JSON field names and nesting
`toJson`/`fromJson` produce, including how the cells, the quadrants and `lastMove` are
written. `Tech Design.md`, alongside Decisions → Serialization and the storage layer, records
the handoff's sketch — *"cells, quadrants, activeQuadrant, currentPlayer, lastMove, score,
firstPlayerThisGame"* — as *"a design sketch, not a decision taken here."* In practice this
is the storage layer's call and it is carried by `P1-04-persistence.md` → Open Questions →
1. Persisted data — versioning. No requirement above depends on the answer.
**One thing does depend on it, and it is OQ-7's third bullet:** if the test suite builds
board fixtures through `fromJson`, every one of those tests binds to this still-open shape.
*(Note the sketch predates requirement 43 and names no winning line. Whether `winningLine` is
persisted or recomputed on load is part of this same open shape — it is derivable from the
quadrant states, so nothing is lost either way, and no requirement above depends on which.)*

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
requirement 33 points at it. **What the error may *carry* is now settled too, by the user:**
it carries the offending `Move` and the `Board`, and its `toString()` renders the reason and
the `Move` and never the board — which is what resolves the contradiction earlier revisions
flagged against `P1-06-crash-reporting.md` req 17. Requirement 42 states the contract and its
test; `P1-06` req 19 states the same thing from the consuming side.

**OQ-6 — Answered and closed.** *A move that claims (or cat-games) the very quadrant it
sends the opponent to — which state does the send see, before or after the move?* Settled in
`Rules.md` → Decisions → **Does a move that claims its own send target still send there?**:
*"**The send is evaluated against the board *after* the claim.**... The quadrant is dead by
the time the send resolves, so the opponent gets a **free choice** of any still-open
quadrant,"* framed there as the ordinary dead-quadrant rule applying rather than an
exception to it. This is the answer requirements 17, 18, 19 and 36 were already written
against, so nothing was restructured; requirement 17 states it with the citation, and
requirement 17(c) is its test.
**The one-open-quadrant corollary is separately confirmed by the user** and is stated in
requirement 17: that case is `freeChoice`, not `forced`. It was an inference in earlier
revisions of this PRD and is now a settlement.

**OQ-7 — Three edges the requirements do not specify (author-raised, found in review).**
None is a rule of play, and none blocks the build; each is a place an implementer or a test
author would otherwise decide silently, and two of them are on the published API.

- **`startNextGame()` has no precondition.** Requirements 26 and 34 describe what it does to
  a *finished* game — reset the board, carry the score, apply requirement 25's first-player
  rule — and its only caller is `P3-04-game-over-rematch.md` req 6, which fires from a
  surface that exists only when `outcome != inProgress` (its req 1). But nothing says what
  happens if it is called on an **in-progress** board. The candidates are: throw, as
  requirement 42 does for the analogous contract violation; return a reset board and
  silently discard a game in progress; or be documented as undefined. Requirement 25 has no
  answer to apply on a board with no result, so "carry on regardless" is not actually
  available. Note the asymmetry worth deciding against: `applyMove` is fully specified for
  its wrong-state case and this operation is not.
- **`cellAt` / `quadrantAt` out-of-range reads.** Requirement 41 gives both a
  well-defined result for indices 0–8 and says nothing about anything else, while
  requirement 42 explicitly *does* handle an out-of-range index on the write path (it is
  `notLegal`). So the read path's behaviour on `cellAt(9, 0)` or `quadrantAt(-1)` is
  whatever the underlying collection does — a `RangeError` under a list, `null` under a map,
  or a silent wrong answer under modular arithmetic. `P3-01-board-rendering.md` iterates
  fixed ranges so nothing in the app reaches it today; that is what makes this cheap to
  settle now and awkward later.
- **How a test may construct a board.** Requirement 28 requires unit tests written from
  these requirements, and every fixture in this PRD is described as a *position* rather than
  as a move sequence. The engine's only public constructor is `Board.newSeries()`
  (requirement 32), so reaching a mid-game position through the public API means replaying
  legal moves — which is faithful but verbose, and for some fixtures (a board with five
  quadrants claimed and empty cells inside them, requirement 21) a long sequence. The
  tempting shortcut is `fromJson` fixtures, and **that would bind the suite to the JSON
  shape OQ-3 leaves open**: every such test breaks when the serialized form is settled, and
  the breakage looks like a rules failure rather than a fixture failure. Whether a test-only
  constructor should exist, whether `fromJson` fixtures are sanctioned, or whether the suite
  is restricted to legal move sequences, is not specified anywhere and is a real choice
  about how the tests are written.

**OQ-8 — When one claim completes two big-board lines, which one is the winning line?**
*(Author-raised, arriving with requirement 43. Fenced for the build, unanswered as a product
question.)* Requirement 43 returns exactly one triple and fences *which* one deterministically
so the value is testable — but that fence decides what the accessor returns, not what a
player should see. The case is reachable rather than theoretical: claiming the centre
quadrant with `{0, 8}` and `{3, 5}` already claimed completes a diagonal and the middle row
on the same move.

> If a win completes two lines at once, does the game name one of them, or both?

It matters only downstream of this PRD, which is why it is recorded rather than decided here.
If `winningLine` only ever feeds a copy string (`P3-04` req 20), one triple is plenty. If it
drives the winning-quadrant highlight requirement 43 records as the expected consequence,
lighting one of two completed lines and leaving the other dark is a visible choice — and
`List<int>?` **cannot express "both" at all**; a `List<List<int>>` would. That is the part
worth deciding while the accessor is still unbuilt: widening the return type later is a
signature change across every consumer, while widening the fence is not.
