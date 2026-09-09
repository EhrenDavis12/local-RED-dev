# AI

> **Status:** Brain dump. Contradictions are expected and OK. What's settled is stated in
> present tense; anything unsettled is in **Open Questions**.

## What the AI Is
An **AI opponent with three difficulty levels — Beginner, Medium and Advanced.** This is
the basic AI. Every level plays a legal move every turn; what separates them is how far
they look before picking one.

The levels are a ladder, and each rung adds to the rung below it: Beginner looks for a win,
Medium adds a block, Advanced adds the big board and is the only one that thinks about
where its move sends the opponent. Nothing is ever taken away going up — Advanced still
wins and still blocks on the small board the same way Medium does.

| Level | What it looks at | Order of checks |
|---|---|---|
| **Beginner** | The small board it is playing in | Win → random |
| **Medium** | The small board it is playing in | Win → block → random |
| **Advanced** | The big board, then the small board | Big board → win → block → random |

## The Three Levels

### Beginner
**Looks for a win on the small board. If there isn't one, it plays a random square.**

- It checks the small board it is playing in for a square that completes three in a row.
- If there is one, it plays it and claims that quadrant.
- If there isn't, it picks a random square out of the ones it is allowed to play.

**Beginner never defends.** An opponent sitting one square away from claiming a quadrant
gets to take it, unless Beginner happens to land on the blocking square by chance. That is
the level, not a gap in it — it is the rung a player who has just learned the rules can
beat.

### Medium
**Win, then block, then random** — three checks, in that order, all on the small board it
is playing in:

1. A square that completes three in a row for the AI. Take it.
2. Otherwise, a square that stops the opponent completing three in a row on their next
   move. Take it.
3. Otherwise, a random square out of the ones it is allowed to play.

Offence beats defence when both are on the table — a claimed quadrant is worth more than a
quadrant denied, because only claiming wins the game.

Medium looks at exactly what Beginner looks at. The second check is the whole difference.

### Advanced
**Starts on the big board, then plays the small board.** It works out where it wants to go
first, and only then how to play the square:

1. **The big board.** It looks at the claimed quadrants and works out which quadrant it
   wants — the one that takes it toward three in a row on the big board.
2. **The small board.** Inside the board it is playing in, it goes for the win first, then
   for the block, the same two checks Medium makes.
3. **Random**, if it finds no big-board line to go for and no win or block on the small
   board.

Advanced is the only level that knows the game is being played on two boards at once.
Beginner and Medium play the small board in front of them and are indifferent to what
claiming it is worth; Advanced has a reason to want one quadrant more than another.

**Its only defence on the big board is knowing which boards to keep the opponent out of, so
the opponent does not win them.** That is the whole of it — Advanced does not block on the
big board the way it blocks on a small one. It has no notion of stopping a quadrant that
would complete the opponent's line; what it has is a reason not to hand them a board they
are about to claim.

## The Sending Rule
**Advanced is the only level that thinks about where its move sends the opponent. Beginner
and Medium do not.** Both play the square in front of them and are indifferent to which
board the opponent lands in next — a winning square that drops the opponent into a board
they are one move from claiming is taken the same as any other.

That is the sharpest difference between the levels, because the sending rule is where the
strategy of the game lives (see [Rules](./Rules.md) → Placement Rules). A level that
ignores it is playing nine separate games of tic-tac-toe; Advanced is playing this one.

### When the send outranks a win
**Advanced goes for its own win first — unless taking that small win hands the opponent the
whole game. Then it does not make that move.**

This is the one thing that outranks a win, and the bar is the game itself, not a quadrant.
Advanced will take a small board that sends the opponent somewhere useful, and will take
one that lets the opponent claim a quadrant; what it will not do is claim a quadrant when
the board it sends the opponent to is one they can win to complete three in a row on the
big board. It gives up a claim to avoid losing, and nothing less than losing buys that.

The move it makes instead is whatever its remaining logic gives it — a different win if
there is one, then the block, then the rest. **If every legal square hands the game over,
it still moves**, because a player must play (see [Rules](./Rules.md) → Turn Structure).
There is no passing, so a lost position is played out rather than refused.

## Free Choice
When a move sends a player to a quadrant that is already claimed or cat-gamed, they may
play in any open quadrant instead (see
[Rules](./Rules.md) → Edge Cases → Sent to a dead quadrant). The levels split on what to do
with that:

- **Beginner and Medium pick a board at random, then play it the way they play any board**
  — Beginner looks for its win, Medium looks for its win and then its block, inside
  whichever board the random pick landed on.
- **Advanced chooses the board.** It looks for what the big board offers it — a quadrant
  that takes it toward three in a row — and for the boards it does not want the opponent
  sent to.

So a free choice is worth something to Advanced and worth nothing to the other two. It also
means **Medium can miss a win it could have taken**: a board it never looked at may have
had one, and it only ever looks at the board it landed in.

## The Random Fallback
**Every level ends in a random square, and every level reaches it often.** Most turns
offer no win and no block, so random is the ordinary case rather than a last resort — it
is what the AI mostly does.

The pick is made from the squares the AI is allowed to play, not made and then checked. The
engine throws on an illegal move ([Rules](./Rules.md) → Engine Contract), so an AI that
picked first and validated afterwards would be one bug away from crashing the game.

**The opening move is random at every level — the quadrant and the square both.** When the
AI goes first it picks one of the nine quadrants at random and one square inside it at
random, and Advanced does this too. There is nothing on the board yet for any of the three
to reason about: no claimed quadrants for a big-board line, no marks for a win or a block.

## Thinking Time
**The AI waits two to three seconds before it moves.** The pause is deliberate — it is the
AI appearing to think, not the app being slow.

It also separates the player's move from the AI's. Pass-and-play has no handoff screen
because there is no hidden information (see
[Menus and UI](./Menus%20and%20UI.md) → Pass-and-Play Turn Handoff), so without the pause
the confirming tap and the AI's reply would land together and read as one event — the
player's own tap appearing to place two marks.

What the board shows while it waits is
[Menus and UI](./Menus%20and%20UI.md) → The AI's Turn on the Board.

## The AI as a Player
Where a player chooses to play the AI, picks its level and changes that level later is
[Menus and UI](./Menus%20and%20UI.md) → Playing the AI. This section is what the AI *is*
once a game has started.

**The AI is Player Two.** The person is Player One, and the scoreboard reads Player One /
Cat / Player Two exactly as it does in a two-player game — those three strings are fixed in
code and no mode changes them (see [Theming](./Theming.md) → What a Theme Does NOT
Control).

**Being Player Two does not mean always moving second. If the AI wins, the AI goes first in
the next game.** Turn order across games is untouched by the mode — the winner of the last
game opens the next one, whoever that is (see [Rules](./Rules.md) → Turn Order Across
Games). Going first means picking the starting quadrant, and every level picks it at
random — see **The Random Fallback** below.

## The Level Belongs to the Game
**The difficulty is saved per game, not app wide.** An open game already holds a whole
series — its board and its running score — and the level it is being played at is part of
that (see [Menus and UI](./Menus%20and%20UI.md) → What an open game holds). So two open
games can sit in the list at two different levels, and picking one back up resumes it at
its own.

It is saved with the game rather than alongside the four settings toggles, which are app
wide and live in `shared_preferences` — see
[Menus and UI](./Menus%20and%20UI.md) → Persistence. A level chosen on one game's result
card changes that game and nothing else.

**Changing the level does nothing to the scoreboard.** Not mid-game, not between games in a
series. The running score keeps counting across the change — a series that starts against
Beginner and moves up to Advanced is still one series with one score, and nothing resets,
splits or annotates it.

That means the score does not record what it was won against, and a 6–0 built on Beginner
reads the same as one built on Advanced. That is the accepted cost: the scoreboard is
bragging rights between people sharing a phone (see
[Game Overview](./Game%20Overview.md) → Session Structure), and a player who moves the
level up mid-series already knows they did.

## Conflicting Ideas (unresolved)
<!-- Two rules that can't both be true yet. Keep both here until we pick. -->

## Open Questions
<!-- Nothing outstanding on this doc right now. -->
