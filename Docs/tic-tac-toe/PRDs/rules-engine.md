# PRD: Rules Engine

> **Status:** Draft · Source docs read: [Rules](../Rules.md),
> [Tech Design](../Tech%20Design.md), [Game Overview](../Game%20Overview.md),
> [Game Board Design](../Game%20Board%20Design.md), [Menus and UI](../Menus%20and%20UI.md).
> `Alternative Game Styles.md` is a parking lot and is not a source.

## Problem

The game has no application code. Every rule of Tic-Tac-Toe-Extreme — the sending rule,
claiming, cat games, the two draw conditions, turn order across a series — exists only as
prose spread over three documents. Nothing can be played, and nothing above the engine (the
board, the scoreboard, storage) has a state object to read or a move to apply.

## Goal

`lib/engine/` holds a pure-Dart rules engine that plays a complete series of
Tic-Tac-Toe-Extreme: one immutable value carries the game and the series it belongs to, one
function applies a move and returns the next value, and the engine — not its callers —
decides what is legal, who claims what, whose turn it is, when a game is over, and what the
score is. It draws nothing, names nothing a player reads, and can be tested without a widget
harness.

## Requirements

### The layer and the shape of its state

**R1.** `lib/engine/` is pure Dart with **zero Flutter imports**, and imports no package
whose name begins `hive`, whatever the spelling. This is held by a test that scans the
layer's imports rather than by discipline. *(Tech Design → Project Structure; → The Rules
Engine)*

**R2.** Game state is **immutable**. Applying a move never mutates a board in place; it
produces a new state object. The API is `Board applyMove(Board, Move)`, not
`board.play(move)`. *(Tech Design → The Rules Engine)*

**R3.** **`Board` is the whole game plus the series it belongs to** — the 81 cells, the 9
quadrant states, the placement state and the forced quadrant, whose turn it is, the last
completed move, the outcome and the line that won it, the running score, and who went first
in this game. There is no outer type wrapping it. The name is narrower than what it holds
and is kept deliberately. *(Tech Design → One value holds the game and the series)*

**R4.** Quadrants and cells are both indexed **0 to 8, row-major from the top left** — 0
top-left, 4 centre, 8 bottom-right — for a cell inside its small board and for a quadrant
inside the big board alike. The 1–9 labels in Rules are that same order written for humans.
*(Tech Design → Quadrants and cells are indexed the same way; Rules → Cell → Quadrant
Mapping)*

**R5.** The public surface uses the working vocabulary — big board, quadrant, small board,
claim, cat game, Player One, Player Two. No abbreviation of *quadrant*, and nothing
shortened to `p1`/`p2`. *(Tech Design → The engine speaks the project's vocabulary; Game
Overview → Terminology)*

**R6.** The engine holds **no mark glyph, no display string, no icon, no asset path, and no
text a player reads**. The players are Player One and Player Two. *(Tech Design → The engine
speaks the project's vocabulary; → What the engine is not)*

**R7.** A `Move` names a quadrant and a cell and **never a player** — the mark is the current
player's, which makes alternation the engine's to enforce rather than the caller's to get
right. *(Tech Design → The series lives in the same state)*

### Applying a move

**R8.** **The sending rule is an identity on the shared index:** the index of the cell played
is the index of the quadrant the opponent is sent to. This is true of the opening move
exactly as of every move after it — no exception for move 1. *(Rules → Placement Rules; Tech
Design → Quadrants and cells are indexed the same way)*

**R9.** A mark completing three in a row on a small board **claims** that quadrant for its
player. **A claimed quadrant is closed to further play**, including the cells in it that are
still empty. *(Rules → Winning a Sub-Board)*

**R10.** A small board **completely filled with no winner** is a **cat game**. That quadrant
is **unclaimed for the rest of the game** — nobody ever gets it, and it can permanently block
a big-board line for both players. *(Rules → Cat game)*

**R11.** Within a single move, **the claim or cat game resolves before the send does**. The
send is evaluated against the board as it stands *after* the move that triggers it, so a
quadrant the move just claimed or cat-gamed is dead exactly as one that was already dead.
*(Rules → Sent to a dead quadrant → free choice; Tech Design → Three placement states)*

**R12.** When the send lands on a quadrant that is claimed or a cat game, the next player gets
a **free choice of any quadrant that is still unclaimed and open**. Claimed and cat-game
quadrants are both off limits. *(Rules → Sent to a dead quadrant → free choice)*

**R13.** **One still-open quadrant left is free choice, not forced.** When the send lands on a
dead quadrant and exactly one quadrant remains open, the placement state is free choice. The
legal moves are identical either way; the state differs. *(Tech Design → Three placement
states)*

### The three placement states

**R14.** **Forced, free choice and game over are engine state, not something a consumer
infers.** The engine names which one is active, and in the forced state which quadrant. A
consumer branches on the placement state and never on "there is no forced quadrant" — free
choice and game over both have none. *(Tech Design → Three placement states)*

**R15.** **A forced state always names a quadrant with at least one legal move in it**,
because a send onto a quadrant that just died resolves to free choice instead. *(Tech Design
→ Three placement states)*

**R16.** The opening move is **the free-choice state over all nine quadrants**, not a state of
its own. *(Tech Design → Three placement states; Rules → Placement Rules)*

**R17.** **The legal-move set is empty exactly when the game is over**, so an in-progress
board always offers at least one move. *(Tech Design → Three placement states)*

### Ending a game

**R18.** A player wins the game by holding **three claimed quadrants in a row** on the big
board — row, column, or diagonal. Quadrants are claimed only by winning the small boards
inside them. *(Rules → Winning the Game)*

**R19.** **A straight draw is "no quadrant is left open"** — every quadrant is either claimed
or a cat game — with nobody holding three in a row. This is *not* "all 81 cells are filled":
a claimed quadrant closes with empty cells still inside it. **Most-quadrants-claimed does not
win; the count is irrelevant.** The result is a tie. *(Rules → Big board full with no
three-in-a-row → straight draw)*

**R20.** On a won game the engine names **the three quadrants of the completed big-board
line**, in **ascending order**. It is **absent on an in-progress board and on a draw, with no
stand-in value** — a consumer reads the outcome first and asks for the line only in the two
winning cases. *(Tech Design → The engine publishes which three quadrants won)*

**R21.** When one claim completes **two big-board lines at once, exactly one is returned**:
the first in the fixed order — rows top to bottom, then columns left to right, then the two
diagonals — so the value is deterministic. *(Tech Design → The engine publishes which three
quadrants won)*

### Turn order, within a game and across games

**R22.** **Whose turn it is is engine state, never derived from move parity**, and the engine
also retains **who went first in the current game**. Player Two starts some games, so parity
silently inverts the turn for every later game in a series. *(Tech Design → The series lives
in the same state)*

**R23.** **The move that ends the game does not alternate.** Every other move flips whose turn
it is; the winning move leaves the **winner** as the current player, so a finished game reads
as the winner's. On a straight draw the value stays with **whoever made the final move**.
This is the one exception to alternation, and anything asserting that invariant has to carve
it out. Nobody is to move on a finished game. *(Tech Design → The series lives in the same
state)*

**R24.** **The last completed move is absent rather than a stand-in value on a board nobody
has played** — a fresh series and the board that starts the next game both have none. *(Tech
Design → The series lives in the same state)*

**R25.** **The score is series state and the engine moves it.** The winner's column, or Ties,
is already incremented on the state the **game-ending move** returns. A finished game is
counted once, ever. *(Tech Design → The series lives in the same state; Menus and UI → Game
Over → Rematch)*

**R26.** **Starting the next game resets the board and moves no counter** — the finished game
was counted when it ended. The series score carries across unchanged. *(Tech Design → The
series lives in the same state; Game Overview → Session Structure)*

**R27.** **Turn order across games:** Player One goes first in game 1 of a series; from game 2
on, **the winner of the last game goes first**; **after a tie, the player that went first in
the tied game goes first again.** *(Rules → Turn Order Across Games)*

### What the engine refuses

**R28.** The engine **throws** on an illegal move and on any move applied to an
already-finished game, rather than returning silently. There are two reasons, and **the
already-finished game is checked first**, so a move applied to a finished game reports that
rather than "not a legal move". *(Rules → Engine Contract; Tech Design → What the engine
refuses)*

**R29.** It raises an **`Error`, not an `Exception`** — a contract violation rather than a
recoverable condition, and no caller is meant to catch it. *(Tech Design → What the engine
refuses)*

**R30.** The error **carries the offending move and the board it was applied to**, and keeps
them — that is the debugging value, read from a debugger attached in process. *(Tech Design →
What the engine refuses; → The one error that carries game state renders none of it)*

**R31.** **`IllegalMoveError.toString()` renders the reason and the offending move, and never
the board.** The engine's own tests assert that rendering this error as text prints no board
content. *(Tech Design → The one error that carries game state renders none of it)*

## Out of Scope

- Anything drawn: UI, widgets, screens, rendering, layout, animation, theming. The engine
  draws nothing, holds no theme value, and knows nothing about screens. *(Tech Design → What
  the engine is not)*
- Riverpod, providers, and state management of any kind.
- Persistence and serialization — storage, Hive, `toJson`/`fromJson`, version stamps, saved
  open-game records. The record id, the opponent name and the timestamps a saved game carries
  belong to storage, not to game state. *(Tech Design → What the engine is not; → What a
  stored open game holds)*
- Navigation and routing; audio, haptics, assets; in-app purchases, entitlements, crash
  reporting as a system (R31 is the engine's own share of that contract, and nothing more).
- **The pending, unconfirmed selection of the two-tap move.** It is input state and never
  engine state. *(Tech Design → What the engine is not)*
- Which winning line a *player* is shown, and how a win, a claim or a cat game is announced or
  highlighted. R20 and R21 make a highlight expressible; they design none. *(Tech Design → The
  engine publishes which three quadrants won)*
- Publishing the three winning *cells* within a claimed small board. No doc asks for it.

## Open Questions

These are Tech Design → Open Questions → *9. The rules engine*, unchanged. None of them
blocks the requirements above; each bounds one of them.

- If a win completes two lines at once, does the game name one of them, or both? The engine
  returns one so the value is deterministic, but that fixes what the engine publishes, not
  what a player should be shown — and "both" is not expressible in what it returns today.
  Widening that later is a change at every consumer; widening which one it picks is not.
- What happens if the next game is started while a game is still in progress? Starting the
  next game is settled for a *finished* game — reset the board, carry the score, apply the
  turn-order rule — and there is no first player to derive from a board with no result. The
  candidates are throw, reset and discard the game in progress, or leave it undefined.
- What comes back from reading a cell or a quadrant with an index outside 0–8? An
  out-of-range index on the write path is an illegal move; the read path has no stated
  answer, so today it is whatever the underlying collection happens to do.
- How may a test build a mid-game board? The only way in through the public surface is a
  fresh series plus a replay of legal moves, which is faithful but long. The tempting
  shortcut is building fixtures from stored JSON, and that binds the whole suite to a
  serialized shape *1. Persisted data — migration* leaves open — where the breakage then
  looks like a rules failure rather than a fixture one.
