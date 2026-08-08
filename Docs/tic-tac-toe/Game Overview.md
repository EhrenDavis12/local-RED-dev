# Game Overview

> **Status:** Brain dump. Contradictions are expected and OK. Nothing here is settled except
> what's under **Decisions**.
>
> **Approved UI design:** `Docs/tic-tac-toe/design_handoff_game_ui/README.md` —
> [Design Handoff](./design_handoff_game_ui/README.md). Approved high-fidelity mockups
> for all 12 screens, built from these docs. It is the source of truth for what the game
> *looks like*; these docs stay the source of truth for what it *is*. Reference asset —
> read-only, nothing in this repo edits it.

## The Pitch
Tic Tac Toe Extreme is a recursive board-in-a-board.

You play a basic tic-tac-toe game, but inside each section of the board is a smaller
tic-tac-toe game. The winners of the smaller games claim the larger section. The goal
is to win on the bigger board.

## Core Concept
- Big board = a normal 3x3 tic-tac-toe grid.
- Each of the 9 big sections contains its own full 3x3 tic-tac-toe game.
- Win a small board → you **claim** that big quadrant.
- Win three claimed quadrants in a row on the big board → win the game.
- Players don't freely pick where to play. **The cell you play sends your opponent to the
  matching quadrant** — play the center cell, your opponent must play in the center
  quadrant. Every move both contests a small board and dictates where the opponent goes
  next. That's where the strategy lives. See [Rules](./Rules.md) → Placement Rules.

Variants we've considered but aren't building live in
[Alternative Game Styles](./Alternative%20Game%20Styles.md).

## Session Structure — Games and Continuing
The app isn't built around a single one-off game. It's built around **playing several in
a row on the same phone**:

- A **scoreboard** at the top of the game screen tracks **Player One / Ties / Player Two**.
- When a game is won or tied, the player is offered an option to **continue playing**.
- Continuing **resets the board**. The score increments at game end, not when continuing
  is taken — see [Menus and UI](./Menus%20and%20UI.md) → Decisions → When does the
  scoreboard increment.
- The scoreboard carries across games so a session becomes a running series.
- **The winner of the last game goes first in the next one.**

This makes the natural unit of play a *session of many games*, not one game.

## How a Move Is Made
Moves are **two taps — select, then confirm:**

1. Tap a cell in the small board. The big board highlights **the quadrant that choice
   points to**, previewing where the opponent would be sent.
2. Tap again to confirm and commit the move.

This makes the game's central mechanic visible before you commit to it — *play here, send
them there* — instead of something you have to work out in your head. It also makes
mis-taps harmless on a board with 81 small targets. Detail in
[Game Board Design](./Game%20Board%20Design.md).

Drawn in [Design Handoff](./design_handoff_game_ui/README.md) → *2d — Board, pending
move* — the provisional cell, the ghost mark, and the destination quadrant it previews.

## Player Experience
- Fast, repeatable rounds. Win or tie, reset, go again — the scoreboard is what turns
  it into "best of" bragging rights between two people sharing a phone.

## Target Audience & Platform
- **Phone.** Two players sharing one device.
- **Kids are a target audience** — swappable themes exist specifically to make it fun
  for kids. See [Theming](./Theming.md).

## Inspirations / References
<!-- Ultimate Tic Tac Toe, other games, mechanics you liked elsewhere -->

## Modes
**Current scope — one mode only:**
- **Two player, same phone (pass-and-play).** Turns alternate Player One → Player Two →
  Player One → Player Two. Started from the **Play Game** button on the main menu.

See [Menus and UI](./Menus%20and%20UI.md) for the menu and screen flow.

## Terminology (working vocabulary)
- **Big board / bigger board** — the outer 3x3.
- **Quadrant / section** — one of the 9 cells of the big board (holds a small board).
- **Small board / smaller game** — the inner 3x3 inside a quadrant.
- **Claim** — winning a small board and taking its quadrant on the big board.
- **Cat game** — a small board filled with no winner. Quadrant stays unclaimed forever.

**Internal vs. player-facing:** the terms above are the docs' own working vocabulary — for
the docs, the PRDs and the code. What the player reads on screen is different — see
Decisions → Player-facing vocabulary below.

## Decisions

### Recursion depth
**Two levels is the whole game** — big board → small board, and that's it. No deeper
nesting. ("For now," but this is the game we're building.)

### Scoreboard lifetime
**Each open game carries its own scoreboard.** The score belongs to that game, not to a
session at the board — leave to the main menu, pick the same game back up from the
open-games list, and its running series is still there.

The scoreboard is saved along with the game. See
[Menus and UI](./Menus%20and%20UI.md) → Persistence and Decisions.

### Player names
**Always "Player One" and "Player Two"** — no custom names for the players themselves.

The opponent name entered at New Game does **not** replace "Player Two" on the in-game
scoreboard. It titles the game in the open-games list, and nothing else. See
[Menus and UI](./Menus%20and%20UI.md) → Decisions.

With the option to change that later. Don't hardcode the strings in a way that fights
adding real names down the road.

### Single-player / AI opponent
**No.** Two players on one phone is the only mode.

### Player-facing vocabulary: "board" vs. "quadrant"
**Player-facing text says "board". The internal term stays "quadrant".** "Board" is what
the player reads on screen; "quadrant" is what the docs, the PRDs and the code use. See
Terminology (working vocabulary) above.

This settles a disagreement the docs have carried for a while: every drawn screen says
"board", while the docs' working vocabulary says "quadrant". "Board" is the more natural
word for a child, and children are a stated target audience — see Target Audience &
Platform above.

The ambiguity that made this a real question does not disappear: "board" now refers both
to the big 3x3 grid and to each of the nine small ones, and player-facing copy has to
disambiguate by context. That's a known cost, not a solved problem.

## Open Questions
<!-- Nothing outstanding on this doc right now. -->
