# PRD: AI Opponent

> **Status:** Draft · Source docs read: `AI.md`, `Menus and UI.md`, `Rules.md`,
> `Game Board Design.md`, `Game Overview.md`, `Tech Design.md`, `Theming.md`,
> `Animations.md`. (`Alternative Game Styles.md` is a parking lot and was not sourced
> from.) Source code read: `lib/engine/`, `lib/state/`, `lib/storage/`,
> `lib/navigation/`, `lib/ui/board/`, `lib/ui/menus/`.
>
> A requirement marked **(Decision…)** was settled for this feature rather than read out of a
> design doc — it is as binding as the rest, and it is what a harvest has to carry back.

## Problem
The app only plays pass-and-play. A player on their own has nobody to play, and there is no
way to say so: the new-game flow asks for an opponent's name and nothing else. The design
docs describe a three-level AI opponent, how a player reaches it and what the board shows
while it moves; none of it exists in code.

## Goal
A player starting a new game is asked who they are playing, and can pick the AI at
Beginner, Medium or Advanced. The AI plays as Player Two, taking a legal move on every turn
after a visible pause, opening a game itself when it won the last one. The level is saved
with that game and changeable from the result card between games, with everything else
about a game — board, rules, scoreboard, series, persistence — unchanged.

## Requirements

### How the AI picks a move

1. Every level plays a legal move on every turn, and the pick is made **from** the moves
   the engine reports legal rather than made and then checked — the engine throws on an
   illegal move. (`AI.md` → What the AI Is; The Random Fallback; `Rules.md` → Engine
   Contract.)
2. **Beginner:** inside the board it is playing in, a cell that completes three in a row
   for the AI if there is one; otherwise a random cell out of the ones it is allowed to
   play. Beginner never blocks — an opponent one square from claiming a quadrant gets it
   unless Beginner lands on the blocking square by chance. (`AI.md` → Beginner.)
3. **Medium:** win, then block, then random, in that order, all inside the board it is
   playing in — a cell completing three in a row for the AI; otherwise a cell that stops
   the opponent completing three in a row on their next move; otherwise random. Offence
   beats defence when both are available. (`AI.md` → Medium.)
4. **Advanced** makes the same two small-board checks Medium makes, in the same order, and
   never fewer — the ladder takes nothing away going up. (`AI.md` → What the AI Is;
   Advanced.)
5. Advanced is the **only** level that weighs where its move sends the opponent. Beginner's
   and Medium's picks are unaffected by which quadrant the cell they choose sends the
   opponent to. (`AI.md` → The Sending Rule.)
6. **The losing-send check.** Advanced does not make a move that sends the opponent to a
   board they can win **on their immediate next move** — one legal cell there claims that
   quadrant for them and completes three in a row for them on the big board. It is
   single-move reachability, never "could eventually win": read the looser way the check
   refuses nearly every send and Advanced plays as Medium with a ranking. The check applies
   to a move that would claim a quadrant for Advanced too. It is the one thing that outranks
   its own win, and the bar is the game itself: Advanced still takes a win that merely hands
   the opponent a quadrant, or that sends them somewhere useful. (`AI.md` → When the send
   outranks a win; the single-move reading is a decision.)
7. **A send that gives the opponent a free pick is judged like any other send.** When the
   move would send the opponent to a quadrant that is dead by the time the send resolves,
   the opponent may play in any open quadrant, so R6 is applied against *every* open
   quadrant: the move is refused if the opponent could, in one move in any one of them,
   claim that quadrant and complete their big-board line. A free-pick send is not exempt.
   (Decision — the reading R6's own wording demands; `Rules.md` → Edge Cases → Sent to a dead
   quadrant, and → The send resolves against the board as it stands after the move.)
8. **A move that wins the game outright is always taken.** The losing-send check never
   declines it: the move ends the game, so there is no opponent to send anywhere.
   (Decision.)
9. **When every legal move fails the check, Advanced still moves** — there is no passing,
   and a lost position is played out rather than refused. It plays **the same board-first
   order it always plays**: the quadrant by R10's ranking, then its own win, then the block,
   then random inside that quadrant. The only difference in a lost position is that the
   losing-send filter is dropped, because every move fails it. It must not invert to a
   move-first search — that would make Advanced hunt wins better when it is losing than when
   it is healthy. (`AI.md` → When the send outranks a win; `Rules.md` → Turn Structure; the
   order is a decision.)
10. **Advanced ranks quadrants by closeness to finishing.**
    - **Only live lines count.** A big-board line Advanced can no longer complete — the
      opponent holds one of the three, or one of the three is a cat game — is not a line it
      ranks by. A dead line takes it nowhere.
    - **A quadrant is ranked by its best live line:** one where Advanced already holds two of
      three beats one where it holds one of three, which beats one on no live line at all.
    - **Ties on that go to the quadrant sitting on more live lines**, then to random. This is
      what makes the centre quadrant, on four lines, worth more than a corner tied with it.
    - **A quadrant is excluded only when *every* legal cell in it makes a losing send**
      (R6/R7). The checks judge moves, not quadrants: excluding a quadrant because one of its
      cells fails would throw away nearly every quadrant and drop Advanced into R9's fallback
      most turns.

    (Decision, settling `AI.md` → Advanced's "the one that takes it toward three in a row on
    the big board".)
11. **Free choice, Beginner and Medium:** pick one of the still-open quadrants at random,
    then play it the way they play any board. A win available in a quadrant they did not
    pick is missed. (`AI.md` → Free Choice.)
12. **Free choice, Advanced:** chooses which quadrant to play in by R10's ranking, then
    plays that board by R4. This — and the opening move of R14 — are the only points at
    which any level chooses its board; in a forced state there is nothing to choose.
    (`AI.md` → Free Choice; Advanced.)
13. Advanced never blocks on the big board. It has no notion of stopping a quadrant that
    would complete the opponent's line; its only big-board defence is R6. (`AI.md` →
    Advanced.)
14. **The opening move is random at every level, Advanced included** — one of the nine
    quadrants at random and one cell inside it at random. "Opening move" means the first
    move of **each game in the series**, not only of the first game: any game the AI leads
    under R19 opens this way. (`AI.md` → The Random Fallback.)
15. **Wherever more than one move satisfies the check being made, the pick among them is
    random** — two cells that both complete a line, two that both block one, two quadrants
    tied on R10's ranking. (Decision, matching `AI.md`'s random fallback at every level.)
16. **The AI's randomness is injected as a "pick one of these candidates" source**, not as a
    seeded `Random` handed to the algorithm. Every random choice above — the fallback cell,
    the free-choice quadrant, R15's ties — goes through it, and nothing in the AI reaches a
    global random directly. The seam is shaped this way so a test can say *which candidate
    gets picked* without replaying the implementation's own draw order: a test written against
    a seeded `Random` asserts what the code does rather than what was specified, and would
    have to be rewritten every time the implementation reorders a loop. (Decision;
    `project.json` → `testing`.)

### The AI as a player

17. The AI is Player Two and the person is Player One. The mode changes none of the three
    scoreboard strings, and the opponent name still titles the game in the open-games list
    and nothing else. (`AI.md` → The AI as a Player; `Menus and UI.md` → Play Game → Where
    It Takes You.)
18. The AI takes its turn whenever it is Player Two's turn on an in-progress AI game. That
    includes the opening move of a game it leads and a game reopened from the open-games
    list with its turn pending — the pending turn is re-derived from the loaded game, never
    restored from anything saved about it. (`AI.md` → What the AI Is: "Every level plays a
    legal move every turn"; The AI as a Player. *Derived:* the docs describe no other actor,
    and without this a resumed game whose turn had passed to the AI would never move again.)
19. Turn order across games is untouched by the mode — if the AI won the last game, the AI
    goes first in the next one, and opens it under R14. (`AI.md` → The AI as a Player;
    `Rules.md` → Turn Order Across Games.)
20. **A tap on the board does nothing while it is the AI's turn** — it neither places a mark
    nor starts a two-tap selection. (Decision, not a doc citation. The engine marks for
    whoever is the current player, so an unguarded tap during the AI's turn would place the
    AI's mark for it.)
21. The AI's move is a confirmed move like any other and the game is written to storage as
    it lands. (`Menus and UI.md` → Persistence → When a game is written to storage.)
22. The AI's move fires the same board moments a human's confirmed move does — placing a
    mark as Player Two, plus claiming or cat-game and winning where they apply. (`Theming.md`
    → Sound Decisions → Placing a mark may sound different for each player; `Tech Design.md`
    → One way to play a sound.)
23. **The AI's move fires no haptic.** The setting is *Vibrate on Touch* and an AI move is
    not a touch, so the AI's move must not route through anything that inherits the buzz a
    confirming tap fires. (Decision; `Game Board Design.md` → Haptic Rule, "the haptic fires
    on every valid click".)
24. **A pending AI turn belongs to the game it was started for, and is cancelled when the
    player leaves the board.** It never runs to completion against whatever game the state
    layer holds later. Cancelling loses nothing, because R18 re-derives the AI's turn when a
    game is opened again. (Decision. The state layer survives navigation deliberately, so
    without this an AI move can land in a different game — possibly a two-player one.)
25. **"Leaves the board" means leaving the game route itself.** A surface drawn *over* the
    board — in-game quick actions, the settings screen reached from it, the result card —
    does not cancel the pending turn: the board stays mounted underneath all three, and the
    AI's move lands under them. In particular the cancel must **not** hang off the navigation
    layer's existing clear-pending-selection choke point, which fires on every navigation
    including opening quick actions — since the AI's turn is only re-derived when a game is
    *opened* (R18), cancelling there would leave a player who closed the sheet on a board
    that never moves again. **The wait is not paused either:** the timer keeps running while
    such a surface is open. (Decision; `Tech Design.md` → Navigation → Surfaces that stay on
    top of something are nested, and → Every operation clears the pending, unconfirmed
    selection.)

### The AI's turn on the board

26. The AI waits **two to three seconds** before it moves, on every move it makes, opening
    moves included. **The wait is a fresh random draw within that range per move**, not a
    fixed constant, and it **draws from its own seam, separate from R16's** — so a test can
    control timing without disturbing which move gets chosen. (`AI.md` → Thinking Time; the
    per-move draw and the second seam are decisions.)
27. **The wait starts the moment the AI's turn begins** — the player's confirming tap, in
    the ordinary case — and therefore **runs during the win celebration** rather than after
    it, with the AI's move landing when the wait expires. The celebration's input lock stops
    *player* taps; it must neither stop nor delay the AI's own move. (Decision, settling
    `Menus and UI.md` → The AI's Turn on the Board, "it comes up when the player's move is
    confirmed", against `Animations.md` → How Animations Play.)
28. **Celebrations still never overlap.** When the AI's move lands under a running
    celebration and itself claims a quadrant or wins the game, the AI's celebration begins
    when the player's finishes, and the input lock stays engaged until the last one
    completes. R27 deliberately puts an AI move inside a running celebration, so this is the
    case it creates. (`Animations.md` → How Animations Play: "Animations never overlap",
    "Win sequences do block input".)
29. A banner reading **"Thinking"** is up from the moment the AI's turn begins until its
    move lands, and not otherwise. The word is fixed in code and the theme styles it. How it
    sits against the turn banner and the how-to-play strip is not specified here — that is
    looked at by running the app. (`Menus and UI.md` → The AI's Turn on the Board;
    `Theming.md` → What a Theme Does NOT Control.)
30. **The how-to-play strip is unchanged by the AI's turn** — it keeps showing whatever the
    board state already gives it, and gains no AI-specific content. (Decision about what
    gets built now; it does not answer the design doc's own open question about that strip,
    which stays open there.)

### Reaching the AI

31. Creating a new game asks **who you are playing, first** — before the name prompt — and
    the prompt offers three choices: **Two Player**, **AI**, **Versus**. **Tapping a mode row
    picks it and moves the flow on**, to the level select or to the name prompt. (`Menus and
    UI.md` → Playing the AI.)
32. **Versus is drawn in the list and cannot be picked.** It is visible so a player can see
    it is coming; nothing else about it is specified. (`Menus and UI.md` → Playing the AI;
    `Game Overview.md` → Modes.)
33. Picking AI opens a second overlay asking which level — Beginner, Medium or Advanced. The
    order of the whole flow is **mode, then level, then name**. (`Menus and UI.md` → Playing
    the AI.)
34. All three are **overlays**, not screens: whatever the player was looking at stays
    mounted and painted behind them with a scrim over it — the open-games list on the
    ordinary path, the main menu on the empty-state path. **Backing out of any of the three
    leaves the player on that surface and creates nothing** — it drops the whole flow rather
    than stepping back to the previous overlay. (`Menus and UI.md` → Playing the AI: "backing
    out of any of the three leaves the player where they started, rather than partway down a
    stack of screens"; Play Game → Where It Takes You: "Cancelling the prompt creates
    nothing".)
35. The empty-state path — Play Game with no open games — asks the same questions: mode,
    then level on AI, then the name. There is one new-game flow, not two; what the empty
    state saves the player is the open-games list and nothing else. (`Menus and UI.md` →
    Play Game → Where It Takes You.)
36. **The stored record is created from the answers to that flow, on both paths**, and the
    game is then opened by its id. The empty-state path stops creating a record inside the
    game screen under the default name. The game route's payload does not grow a mode or a
    level: the record exists, carrying both, before the route is taken. (Decision; without it
    a player with no open games cannot reach an AI game at all. `Menus and UI.md` →
    Persistence: "a brand-new game is written the moment it starts".)
37. The level select opens with **Beginner already highlighted**, and carries its own
    control to go on to the name prompt, so a player who does not care moves on without
    touching a level row. **Tapping a level row moves the highlight and does not advance** —
    deliberately unlike a mode row (R31), because the design doc's reason for the Beginner
    default only holds if there is a way forward that touches no row. The inconsistency is
    known and is on the list to look at on the simulator, not to settle on paper.
    (`Menus and UI.md` → The level select: "there is always a level on it and a player who
    does not care can move on without choosing"; the advance control is a call made here.)
38. The level in use is highlighted with theme selection's active-row treatment — a **ring
    around the row and a badge**, both drawn from the theme. A ring alone or a badge alone
    is not the highlight. (`Menus and UI.md` → The level select; Theme Selection.)
39. An AI game is named exactly as a two-player game is — same prompt, same **ItSaMeMaRiO**
    default, same 16 characters, same empty-field fallback. The mode changes nothing about
    it. (`Menus and UI.md` → Playing the AI.)

### The level belongs to the game

40. The difficulty is saved **with the game, not app wide**. Two open games can sit in the
    list at two different levels, and picking one back up resumes it at its own.
    (`AI.md` → The Level Belongs to the Game; `Menus and UI.md` → Persistence.)
41. Whether a game is against the AI is saved with the game too, so a game reopened from the
    list is resumed in the mode it was started in. (*Derived from* `Menus and UI.md` → A New
    Game → What It Starts, and → Persistence, which persists the difficulty per game: a
    resumed game that did not know its own mode could not honour R18.)
42. **The mode and the level live in the stored record's envelope, beside the opponent name
    and the timestamps — never inside the engine's game state.** The engine's state is the
    rules' own, kept pure and guarded by a test; a difficulty setting is not a rule of the
    game. Creating a record therefore takes the mode, and for an AI game the level, alongside
    the opponent name and the board. **The mode parameter is required and has no default** —
    a default makes a forgotten argument silently produce a two-player game, which is
    invisible until the AI never moves. (Decision; `Tech Design.md` → What a stored open game
    holds; The Rules Engine; What the engine is not.)
43. **On save: the mode is preserved from the stored copy, and the level is honoured from the
    caller only when the caller supplies one.**
    - The mode is immutable after create, exactly as the opponent name is.
    - **A supplied level replaces the stored level. A supplied nothing leaves the stored level
      untouched.** Absence means "no change", never "clear it" — the app's one save path
      passes placeholder values for every field a save does not honour, so under the clearing
      reading an Advanced game would silently demote itself to Beginner on the AI's own first
      move, with no error anywhere.
    - **A two-player record carries no level at all** — absent, not a default value — and a
      level supplied alongside a two-player mode is ignored, on create and on save alike.

    (Decision; `Tech Design.md` → What a stored open game holds, which gives the name and the
    timestamps the same preserve-on-save treatment.)
44. **The open game's mode and level are part of the session the app holds while a game is on
    screen**, so the save path supplies the level from what it is already holding rather than
    depending on R43's absence rule. R43 is the safety net; this is the mechanism. (Decision;
    `Tech Design.md` → State Management.)
45. The level is **not** one of the app-wide preferences and does not go in
    `shared_preferences` alongside the four settings toggles. A level chosen on one game
    changes that game and nothing else. (`AI.md` → The Level Belongs to the Game;
    `Tech Design.md` → Persistence and Serialization.)
46. **Records already on the device still read back, and a missing or unrecognised mode or
    level never makes one fail to decode.**
    - A record whose mode is **absent or unrecognised** is a **two-player** game. No shipped
      build has ever had an AI, so no stored record can be an AI game.
    - A record carrying an AI mode whose level is **absent or unrecognised** reads back at
      **Beginner**, the documented default.
    - Neither case may make the record decode as nothing. Today an unreadable record is
      skipped by the list read entirely and a save against it answers "no such record", so a
      strict read of a new field would make every pre-existing game vanish from the
      open-games list.

    (Decision, settling `Tech Design.md` → Open Questions → 1. Persisted data — migration for
    this one field pair; `Menus and UI.md` → The level select for Beginner as the default.)
47. **In an AI game the result card also carries the difficulty menu**, offering the same
    three levels with the one in use highlighted the same way (R38), so the level can be
    changed between games in a series without leaving the game. The three levels are drawn on
    the card itself rather than behind a control that opens a further surface — a surface
    opened from the card could not report the chosen level back to it. A two-player game's
    result card does not carry the menu. (`Menus and UI.md` → The result card; Playing the AI
    → Changing the level later; `Tech Design.md` → Navigation → No operation reports an
    outcome back.)
48. **Picking a level on the result card is written to disk immediately**, not deferred until
    the next game is taken. A player who changes the level and leaves for the main menu finds
    the new level when they reopen that game. (Decision; `Menus and UI.md` → Persistence →
    When a game is written to storage, "nothing is ever lost to a crash or a force-quit".)
49. **Changing the level does nothing to the scoreboard.** The running score keeps counting
    across the change: nothing resets, splits or annotates it, and the score does not record
    what it was won against. (`AI.md` → The Level Belongs to the Game.)

### How this gets checked

The move-selection rules (R1–R16) are where the risk is, and they are pure logic over the
engine. R16's candidate-picking seam is what makes them assertable: a test names which
candidate comes back, so each level's choice on a given board is a single expected move rather
than a distribution, and no test has to replay the implementation's draw order. Cover them
with fast isolated tests over hand-built positions, plus property tests that play many games
at each level and assert what must never happen — no illegal move ever reaches the engine;
Medium takes an available win before an available block, and Beginner takes that same win but,
on a board offering a block and no win, plays exactly the move the candidate source names,
which is the assertable form of "Beginner never defends" (an unsteered Beginner can land on
the blocking square by chance); Advanced never makes a send that loses it the game while a
non-losing legal move exists, takes a game-winning move whenever one is legal, and — the case
R6's single-move wording exists for — does **not** refuse a send merely because the opponent
could win that board in two moves.

R17–R25 and R40–R49 are state and storage rules, testable the same way: a save/load round trip
carrying the mode and the level; a save proving the mode is preserved and a supplied level
replaces the stored one; **a save supplying no level, proving the stored level survives it**
(R43) — the present-level case passes under either reading of that rule, so the null case is
the one that actually pins it; decoding of records written without either field, asserting
they come back as playable two-player games and still appear in the open-games list (R46) —
this one must be tested, since the failure it prevents is every existing game disappearing; a
pending turn cancelled on leaving the game route but **not** on opening quick actions (R24,
R25); and a level picked on the result card being on disk before the next game is taken (R48).
The two-to-three-second wait (R26) is asserted against a controllable clock, never by waiting.

**Checked by running the app, not asserted:** the look and placement of the mode prompt, the
level select and the "Thinking" banner, including how it stacks against the turn banner and
the how-to-play strip; how the ring-and-badge highlight reads under each theme; and whether
the pause feels like thinking rather than a stall. No golden tests, and no test asserting
spacing, position or feel. (`project.json` → `testing`; `Tech Design.md` → Testing.)

## Out of Scope
- **Versus / online play.** Drawn and disabled (R32); nothing else about it.
- Any change to the rules engine's semantics, or to what its state holds. The AI is a
  consumer of `legalMoves` and `applyMove`, and the level lives outside the engine (R42).
- **Changing the level mid-game.** The result card is the only place it changes (R47); the
  in-game quick-actions sheet gains no difficulty menu.
- **New copy for the how-to-play strip during the AI's turn.** R30 leaves the strip alone.
  The design doc's open question about what that strip should eventually say is untouched
  and stays open there.
- Recording the level a score was won at, or showing it anywhere. Explicitly rejected
  (`AI.md` → The Level Belongs to the Game).
- An AI Player One, or two AIs. The AI is Player Two (R17); it merely moves first sometimes.
- New art, new drawings, or a second highlight treatment for the level select (R38 reuses
  the existing one).

## Open Questions
- **Neither new surface is drawn.** `Menus and UI.md` → Screens (so far): *"The mode prompt
  and the AI level select are the two surfaces with no approved drawing."* The result card's
  difficulty menu is undrawn as well — the approved `1g`/`1h` modals predate the AI. Nothing
  in this PRD waits on a drawing: the three surfaces are built from the requirements above
  and then looked at on the simulator.
