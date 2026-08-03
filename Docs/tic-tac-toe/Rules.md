# Rules

> **Status:** Brain dump. Contradictions are expected and OK. Nothing here is settled.
>
> **Approved UI design:** `Docs/tic-tac-toe/design_handoff_game_ui/README.md` —
> [Design Handoff](./design_handoff_game_ui/README.md). Game logic stays in this doc;
> the handoff only draws the result. Reference asset — read-only.

Here is a list of our game rules.

## Setup
- Two players.
- One big board: a 3x3 grid of quadrants.
- Each quadrant contains its own small 3x3 tic-tac-toe board (81 playable cells total).
- All quadrants start unclaimed, all small boards start empty.

## Turn Structure
1. Players alternate turns.
2. On your turn you place one mark in one cell of one small board.
3. Which small board you're allowed to play in is constrained — see Placement Rules.
4. If your mark completes three in a row on that small board, you **claim** that quadrant.
5. If that claim completes three in a row on the big board, you win the game.

## Placement Rules
- **First move:** the player who goes first gets to **select the starting big quadrant**.
  They then place their mark somewhere in that quadrant's small board.
- **Second player:** must play in the big quadrant that the first player selected.
- **Every move after that — the sending rule:** the *cell* you play inside a small board
  maps to the corresponding *quadrant* on the big board, and that's where your opponent
  must play next.
  - Play the **top-left cell** of any small board → opponent must play in the
    **top-left quadrant** of the big board.
  - Play the **center cell** → opponent must play in the **center quadrant**.
  - And so on for all 9 positions.

Your move therefore does two things at once: it contests the small board you're in, and
it chooses where your opponent is allowed to play. That dual purpose is the heart of the
strategy.

### Cell → Quadrant Mapping
The 3x3 position of the cell within its small board is identical to the 3x3 position of
the quadrant within the big board.

```
  Cell you play          Quadrant opponent
  in a small board       is sent to
  ┌───┬───┬───┐          ┌───┬───┬───┐
  │ 1 │ 2 │ 3 │          │ 1 │ 2 │ 3 │
  ├───┼───┼───┤   ──►    ├───┼───┼───┤
  │ 4 │ 5 │ 6 │          │ 4 │ 5 │ 6 │
  ├───┼───┼───┤          ├───┼───┼───┤
  │ 7 │ 8 │ 9 │          │ 7 │ 8 │ 9 │
  └───┴───┴───┘          └───┴───┴───┘
```

Made visible in [Design Handoff](./design_handoff_game_ui/README.md) → *1e — Game Board,
forced quadrant + last move* and *2d — Board, pending move*: the cell they played and the
quadrant it sent you to are drawn in the same 3x3 position.

## Winning a Sub-Board
- Standard tic-tac-toe: three in a row (row, column, or diagonal) on the small board.
- The winner **claims** that quadrant on the big board.

## Winning the Game
- Get three claimed quadrants in a row on the big board (row, column, or diagonal).
- You claim quadrants only by winning the smaller tic-tac-toe boards inside them.

## Edge Cases

### Cat game (small board draw)
- If a small board is completely filled with no winner, it's a **cat game**.
- That larger quadrant is **unclaimed for the rest of the game** — nobody ever gets it.
- Implication: a cat-game quadrant is dead weight; it can block a big-board line
  permanently for both players.

### Sent to a dead quadrant → free choice
If a move sends you to a quadrant that is **already claimed** or is a **cat game**, that
small board can't be played. Instead:

> **The player gets a free choice — they may play in any other quadrant that is still
> unclaimed and open.**

- Claimed quadrants and cat-game quadrants are both off limits.
- Any still-open quadrant is fair game.
- This is the same kind of freedom the first player has on the opening move.

Design consequence: sending your opponent to a dead quadrant **hands them a free choice**,
which is a real strategic cost. Players will learn to avoid it — and sometimes to use it
deliberately.

### Big board full with no three-in-a-row → straight draw
If the whole big board fills and nobody has three claimed quadrants in a row, it is a
**straight draw**. Most-quadrants-claimed does *not* win — the count is irrelevant.

- The result is a tie.
- **The Ties counter on the scoreboard goes up one.**

## Turn Order Across Games
- Game 1: Player One goes first.
- **Game 2 and beyond: the winner of the last game goes first.**
- **After a tie: the player that went first in the tied game goes first again.**

Note that going first is an advantage — you pick the opening quadrant — so this hands the
advantage to whoever is already ahead.

## Variants / Optional Rules
<!-- House rules, difficulty toggles, alt win conditions -->

## Conflicting Ideas (unresolved)
<!-- Two rules that can't both be true yet. Keep both here until we pick. -->

## Decisions

### Who goes first after a tie?
**The player that went first last time for the tie game goes first again.** A tie doesn't
pass the first-move advantage — it stays where it was.

That completes the turn order rule across games: first game → Player One; after a win →
the winner; after a tie → whoever went first in the tied game.

## Open Questions
<!-- Nothing outstanding on this doc right now. -->
