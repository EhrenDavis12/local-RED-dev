# Game Board Design

> **Status:** Brain dump. Contradictions are expected and OK. Nothing here is settled.
>
> **Approved UI design:** `Docs/tic-tac-toe/design_handoff_game_ui/README.md` —
> [Design Handoff](./design_handoff_game_ui/README.md). Most of this doc now has a drawn
> counterpart there: board geometry, quadrant and cell state tables, and all three
> highlights. This doc says *what must be communicated*; the handoff says *what it looks
> like* in Neon. Reference asset — read-only.

## Board Structure
- Outer: 3x3 grid of quadrants.
- Inner: each quadrant holds a full 3x3 tic-tac-toe board.
- Total playable cells: 81.
- Depth is **fixed at 2 levels** (big board → small board). No deeper nesting.
  See [Game Overview](./Game%20Overview.md) → Core Concept.

```
╔═══════════╦═══════════╦═══════════╗
║ . │ . │ . ║ . │ . │ . ║ . │ . │ . ║
║───┼───┼───║───┼───┼───║───┼───┼───║
║ . │ . │ . ║ . │ . │ . ║ . │ . │ . ║
║───┼───┼───║───┼───┼───║───┼───┼───║
║ . │ . │ . ║ . │ . │ . ║ . │ . │ . ║
╠═══════════╬═══════════╬═══════════╣
║ . │ . │ . ║ . │ . │ . ║ . │ . │ . ║
║───┼───┼───║───┼───┼───║───┼───┼───║
║ . │ . │ . ║ . │ . │ . ║ . │ . │ . ║
║───┼───┼───║───┼───┼───║───┼───┼───║
║ . │ . │ . ║ . │ . │ . ║ . │ . │ . ║
╠═══════════╬═══════════╬═══════════╣
║ . │ . │ . ║ . │ . │ . ║ . │ . │ . ║
║───┼───┼───║───┼───┼───║───┼───┼───║
║ . │ . │ . ║ . │ . │ . ║ . │ . │ . ║
║───┼───┼───║───┼───┼───║───┼───┼───║
║ . │ . │ . ║ . │ . │ . ║ . │ . │ . ║
╚═══════════╩═══════════╩═══════════╝
```
Thick lines = big board. Thin lines = small boards.

Exact geometry — gaps, padding, radii, grid-line insets, line weights — is in
[Design Handoff](./design_handoff_game_ui/README.md) → *The board (the important part)*.
The small-board crosses are drawn lines inset inside the quadrant border, not gaps, and
the big/small hierarchy this section asks for is carried by weight and glow, not by two
colors.

## Scoreboard
A **scoreboard sits at the top of the game screen**, above the board. Three counters:

| Player One | Ties | Player Two |
|:----------:|:----:|:----------:|

```
┌─────────────────────────────────┐
│▓PLAYER 1▓     TIES     PLAYER 2 │
│     2          1          0     │
├─────────────────────────────────┤
│                                 │
│         [ THE BIG BOARD ]       │
│                                 │
└─────────────────────────────────┘
```
PLAYER 1 highlighted above — their turn to play.

**The scoreboard chips read `PLAYER 1` and `PLAYER 2`** (with `TIES` between them), not
`PLAYER ONE` / `PLAYER TWO`.

This does **not** change the settled term for the player — the players are still called
"Player One" and "Player Two." The chip uses the numeral because that is what every drawn
screen shows and because the spelled-out form is materially wider in a fixed-width column.

- Tracks results across multiple games played back to back.
- A **settings button sits at the top right**, alongside the scoreboard — the mid-game
  entry point to quick actions and exiting the game. See
  [Menus and UI](./Menus%20and%20UI.md).
- Increments when a game ends: the winner's column, or the Ties column on a tie.
- Styling is theme-driven like everything else.
- Takes vertical space away from the board — worth noting given the board already has
  81 cells to fit on a phone.

**How much vertical space it takes isn't a fixed number — the height is derived from its
content.** A theme picks the type scale, so a theme with larger chip text makes the
scoreboard taller: it grows rather than clipping the labels or the numbers. Whatever
height it lands on, the whole 9x9 board still has to fit below it with no zoom and no
scrolling — see [Responsive / Screen Size](#responsive--screen-size).

### Turn Indicator
The active player's name in the scoreboard is **highlighted** to show whose turn it is.

This is one of two mechanisms for the "whose turn it is" affordance in
[Player Feedback / Affordances](#player-feedback--affordances) below — the other is the
turn banner, which names the active player whenever no move is pending (see
[Menus and UI](./Menus%20and%20UI.md) → How to Play — the On-Board Legend and Hint). Both
are built. It matters because both players share one phone, so the screen is the only
thing telling them who's up.

Like everything else, what the highlight looks like is theme-driven — see
[Everything Here Is Theme-Driven](#everything-here-is-theme-driven).

## Visual Layout
- Nesting needs to stay readable at a glance: heavy borders for the big board,
  light borders for the small boards.
- Vertical stack: **scoreboard on top, board below.**

## Last Move Highlight
**Player-stated requirement:** *"As a player, what I want to be able to see is where my
opponent last made their move."*

- The opponent's most recent mark must be **exaggerated** — highlighted, glowing,
  outlined, whatever makes it pop.
- It has to be readable **at a quick glance**. The player shouldn't have to hunt across
  81 cells to find what changed.
- The whole point is that it feeds the next decision: *see where they played → understand
  where that sent me → move accordingly.*

### Why this matters more here than in normal tic-tac-toe
Two reasons stack up:
1. **81 cells.** A single small mark somewhere in a 9x9 field is genuinely easy to miss.
2. **Pass-and-play.** The phone changes hands between turns. You aren't watching your
   opponent play — you're handed a board that changed while you weren't looking. The
   highlight is the only record of what happened.

### Lifetime
**The highlight persists until your move is completed.** It stays visible the entire time
you're deciding — through selecting a cell and previewing where it sends your opponent —
and only clears once you confirm.

That's the right lifetime for what it's for: the highlight is reference material while you
think, not a notification that flashes and disappears. You can look back at what your
opponent did while weighing your own move, and compare it against your pending selection
side by side.

## Active Quadrant Highlight
**Player-stated requirement:** *"When I'm forced to play in a specific zone or quadrant, I
want that quadrant to be highlighted for me so I know that's where I need to play and that
I can only play in that box."*

Two distinct jobs, and the design has to do **both**:

1. **Show where you must play.** The forced quadrant is highlighted — obvious, immediate,
   no reading required.
2. **Show where you _can't_ play.** It must be clear the rest of the board is off limits.
   Not just "this one is special" but "this one is the *only* one."

That second job is the easy one to under-build. Highlighting the legal quadrant alone
leaves the other eight looking normal and tappable. The non-legal quadrants should read as
**locked** — dimmed, desaturated, greyed, receded, something. The contrast between "here"
and "not here" is what carries the rule.

**Dimmed, not blacked out.** Whatever's already been played in a locked quadrant has to
stay readable through the dimming. You can't plan a move without reading the whole board,
and in the forced state eight of the nine quadrants are locked.

**Once the game is over, nothing reads as playable.** Every quadrant goes locked — a
finished board doesn't sit there glowing with places to tap behind the result card.

### The free-choice state
There's a second legal state the board has to handle: when a player is sent to a dead
(claimed or cat-game) quadrant, they get a **free choice of any still-open quadrant**
(see [Rules](./Rules.md) → Edge Cases). This also covers the opening move.

So the active-quadrant highlight needs **two modes**:

| Mode | What's highlighted |
|---|---|
| **Forced** | Exactly one quadrant |
| **Free choice** | *Every* still-open quadrant — could be up to 9 |

The free-choice state should still make the *locked* quadrants (claimed, cat-game) read as
locked. It's "pick any of these open ones," not "the board is unlocked." Nine glowing
quadrants at once would look like noise, so free choice takes a calmer treatment than the
single-quadrant forced highlight — the still-open quadrants read as available rather than
each getting a copy of the forced highlight — and a text cue ("Free choice — pick any open
board") as well.

**The free-choice cue lives in the how-to-play strip below the board — not in a turn banner
above it.** That strip already exists, already swaps its content by board state, and
already has an owner and a theme slot.

### Taps outside the legal quadrant
Illegal cells shouldn't accept input. They also shouldn't *look* like they would — the
visual state and the actual behavior need to agree.

**An illegal tap does nothing.** No shake, no flash, no error message — and, per the
haptic rule, **no buzz**, since the haptic only fires on valid clicks.

The lack of a buzz *is* the feedback. A player who taps a locked quadrant feels nothing
and immediately understands the tap didn't count, without the game telling them off. This
is why the locked/dimmed styling matters so much: it has to prevent the tap, because
nothing will explain it after the fact.

## The Two Highlights Together
The last-move highlight and the active-quadrant highlight are the two halves of one
sentence, and they're the core of the board's readability:

> *"They played **there** → so you must play **here**."*

```
┌───────────╥───────────╥───────────┐
│ . │ . │ . ║ ▓▓▓▓▓▓▓▓▓ ║ . │ . │ . │   ← this quadrant is
│───┼───┼───║ ▓ . │ . │.║───┼───┼───│     highlighted: you must
│ . │ . │[O]║ ▓ . │ . │.║ . │ . │ . │     play HERE
│───┼───┼───║ ▓───┼───┼─║───┼───┼───│
│ . │ . │ . ║ ▓ . │ . │.║ . │ . │ . │
╞═══════════╬═══════════╬═══════════╡
        ▲
   opponent's last move, exaggerated.
   They played the TOP-RIGHT cell,
   which sends you to the TOP-RIGHT quadrant.
```

**These two treatments must be visually distinguishable.** Same-looking highlights would
create exactly the confusion they exist to prevent. They differ in scope, which helps:
one marks a **single cell** (what just happened), the other marks a **whole quadrant**
(what you can do now).

**The last-move highlight reads through the dimming.** The opponent's last move is usually
sitting in a quadrant that's now locked — that's the normal case, not the odd one — so the
locked treatment dims that quadrant without hiding what's highlighted inside it. The claim
mark is different: on a won quadrant it covers the whole quadrant, and the cell that won
it isn't picked out separately underneath. What changed there is that the quadrant was
won, and that's what the player sees.

Between them they answer the only two questions a player has when handed the phone:
*what changed, and what can I do?*

Both are drawn together in [Design Handoff](./design_handoff_game_ui/README.md) →
*1e — Game Board, forced quadrant + last move*; the exact ring, glow and veil values are
in *Quadrant states* and *Cell states*.

## Player Feedback / Affordances
Things the board needs to communicate (driven by the rules so far):
- **The opponent's last move** — see the dedicated section above. Highest priority.
- **Which quadrant is legal right now** — see dedicated section. Equally high priority.
- **Which quadrants are _not_ legal** — the locked/dimmed state. Half of the rule.
- **The pending move preview** — the provisional select-before-confirm state.
- **Claimed quadrants** — a won quadrant needs to read as claimed, probably a big
  X or O overlaid on the whole quadrant.
- **Cat-game quadrants** — must look visually distinct from claimed *and* from
  in-play. It's permanently dead and neither player can ever have it.
- **Whose turn it is** — extra important here: both players share one phone, so the
  screen is the only thing telling them who's up. Needs to be unmissable. Carried by the
  scoreboard highlight and the turn banner both — see dedicated section above (Turn
  Indicator).

> These treatments all need to coexist on one screen without turning into visual noise —
> and every one of them is theme-driven, so **each theme has to solve this, not just the
> default one.**

## Move Input — Tap to Select, Tap Again to Confirm
Placing a mark takes **two taps**, not one.

1. **First tap — select.** The player taps a cell in the small board. This *doesn't* place
   the mark. Instead, the big board **highlights the quadrant that choice points to** —
   showing where this move would send the opponent. (Unless that move would claim or
   cat-game the very quadrant it points at — see *When the selected move claims its own
   send target* below.)
2. **Second tap — confirm.** Tapping the same cell again commits the move. The mark is
   placed and the turn passes.

That's the whole gesture, everywhere. There's no separate step where you pick a quadrant
first — on the opening move and in free choice you still just tap the cell you want,
there are simply more of them to choose from.

### When the selected move claims its own send target
**Every still-open quadrant is highlighted.** Normally, selecting a cell previews the
quadrant the opponent will be sent to. But if that move would claim or cat-game the very
quadrant it points at, the quadrant is dead by the time the send resolves and the opponent
gets a free choice — so there is no single quadrant to ring. The preview shows the truth —
the opponent may play anywhere still open — rather than showing nothing.

This reuses the free-choice highlight that already exists for the state after such a move
lands (see **The free-choice state** above), so the preview and the resulting board state
look consistent. It also teaches the rule at the moment it fires, which matters because
sending an opponent to a dead quadrant is a real strategic cost that players have to learn.

**The quadrant this move kills is not one of the highlighted ones.** It's open now and
dead the moment the move lands, so the preview shows the board as it will be, not as it
is — otherwise it would be pointing the opponent at the one quadrant they can't use.

**A move that ends the game previews no destination at all.** If confirming would win or
draw the whole game, nobody is being sent anywhere, so the big board gets no preview
treatment and only the pending cell reads as provisional.

### Why this is more than a safety net
The preview between the two taps is a teaching tool. It makes the sending rule visible
*before* you commit:

> *"If I play here… my opponent gets sent **there**."*

That's the entire strategic core of the game, and normally a player has to hold it in
their head. This surfaces it. Especially valuable for kids and first-time players, who
otherwise have to learn the cell→quadrant mapping the hard way.

It also solves the tap-accuracy problem that keeps coming up: 81 small targets on a phone
means mis-taps are likely, and an accidental move is unrecoverable. Two-tap confirm makes
a mis-tap harmless — you just tap the cell you actually meant.

### Changing your mind
- **Tap a different cell** → that cell becomes the new selection. No need to cancel first.
- **Tap outside the nine quadrants** → deselects entirely, clearing the pending move.

So there are two ways out of a pending selection, and neither needs a dedicated cancel
button: pick something else, or tap away.

**Any tap outside the nine quadrants clears a pending, unconfirmed selection.** That
includes the legend/how-to-play strip, the scoreboard, the settings button, and opening any
menu or sheet. One rule, uniformly applied.

The gutters between cells (3pt) and the quadrant padding (5pt) are outside the cells, so a
near-miss between two cells clears the selection rather than doing nothing. That is the
accepted cost of the single uniform rule.

### Confirming
The confirm tap is **on the same cell** — effectively a **double tap** to place a mark.
No separate Confirm button.

Note this makes a fast double-tap the natural "I know what I'm doing" gesture, while a
slower tap-look-tap gives you the preview. Same interaction serves both the player who
wants speed and the one who wants to check.

**There's no time limit between the two taps.** A pending selection sits there until
it's confirmed, replaced or tapped away — look at the board for a minute, come back, tap
the same cell again, and it still commits.

### Sound
The pending selection **does not** get its own sound. Sound belongs to the confirmed
move, not the preview — so the board doesn't chirp every time someone browses their
options.

### Three highlights on screen at once
This adds a **third** highlight to the board, and all three must be distinguishable:

| Highlight | Scope | Meaning |
|---|---|---|
| **Opponent's last move** | one cell | what just happened |
| **Active quadrant** | one quadrant | where you're allowed to play |
| **Pending-move preview** | one cell + one quadrant | where you'd send them if you confirm |

The preview is the trickiest: it marks a *cell* (your pending choice) and a *quadrant*
(the destination) simultaneously, and both need to read as **provisional** — clearly not
yet committed. Distinct from the last-move highlight, which is committed and final.

All three appear at once in [Design Handoff](./design_handoff_game_ui/README.md) →
*2d — Board, pending move*, which resolves them by weight rather than color: dashed white
for provisional, solid lavender for the last move, solid purple for the active quadrant.

## Pieces & Marks
- Baseline is X and O, but marks are **theme-driven** — a theme may swap them for icons,
  emoji, animals, shapes. See [Theming](./Theming.md).

## Everything Here Is Theme-Driven
Nothing in this document should be read as a hardcoded visual decision. Grid line colors,
backgrounds, mark styling, claimed/cat-game treatments, turn indicator — all of it comes
from the selected theme. This doc describes *what needs to be communicated*; the theme
decides *what it looks like*.

## Animation & Juice
Animations are **theme-controlled** and currently scoped to the player's marker —
poppy grow/shrink, glow, shadowbox, jiggle, dance. Full detail in
[Animations](./Animations.md).

## Responsive / Screen Size
- **Phone is the primary target** — two players passing one device.
- **No zoom.** The whole 9x9 grid stays visible at all times. A 9x9 grid can be shown on a
  phone screen without needing zoom — that's the call for now.
- 81 tappable cells means each cell is roughly 1/9th of the board's width, so tap targets
  are small. Keeping the full board visible is worth that tradeoff: seeing the whole board
  at once is what lets a player reason about where their move sends the opponent.
- The two-tap confirm carries the accuracy problem instead of zoom — a mis-tap is
  recoverable, so small targets don't cost you a move.

The handoff commits numbers to this: at a 402pt frame with 16pt side padding the board is
370pt, a quadrant ≈118pt and a cell ≈35pt — under Apple's 44pt target, accepted because
the two-tap confirm makes a mis-tap free. See
[Design Handoff](./design_handoff_game_ui/README.md) → *The board (the important part)*.

## Sketches & Notes
<!-- ASCII diagrams, rough layouts -->

## Haptic Rule
**The haptic fires on every valid click, anywhere in the app.** Any valid selection or
valid action buzzes — including the first tap of a two-tap move, since selecting a legal
cell is a valid action, and including controls that aren't board cells: menu buttons,
theme rows, settings toggles, the game-over card's controls, the settings gear. It matches
the setting's own name, *Vibrate on Touch*.

**It's the same buzz every time.** One buzz per action, and no vocabulary of different
haptics — the settings gear, a theme row and a board cell all feel identical. What that
buzz feels like is [Menus and UI](./Menus%20and%20UI.md) → Vibrate on Touch.

Paired with the illegal-tap rule above, this produces a clean, consistent system:

> **A buzz means "that registered." No buzz means "that did nothing."**

The haptic becomes the validity signal itself. The player doesn't need an error state —
the *absence* of feedback is the feedback. Nothing scolds them; invalid taps just quietly
don't happen.

**Cancelling a pending move buzzes too.** Tapping outside the nine quadrants drops the
pending mark, and that's something happening — so it registers like any other valid
action.

All of this is subject to the vibrate-on-touch setting being on — see
[Menus and UI](./Menus%20and%20UI.md). **With it off, it's off**: no buzz, and nothing
takes its place. The player has the visuals, and that's the whole of the feedback.

## Open Questions
- **Do things the player didn't tap buzz?** A quadrant getting claimed, a game being won,
  the turn handing over — the rule is written around taps, and nothing says whether events
  like these get a buzz of their own or stay silent.
