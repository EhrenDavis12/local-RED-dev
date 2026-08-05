# PRD: Move Input — Tap to Select, Tap Again to Confirm

> **Status:** Draft · Source docs read: `Game Board Design.md`, `Game Overview.md`, `Rules.md`,
> `Menus and UI.md`, `Animations.md`, `Tech Design.md`, `Theming.md`, `roadmap.md`, plus the
> read-only reference asset `design_handoff_game_ui/README.md` (screen *2d — Board, pending
> move* and *Interactions & behavior*). `Alternative Game Styles.md` is a declared parking-lot
> doc and was read only to confirm it is out of scope — no requirement here comes from it.

> **Wave:** P2 · **Depends on:** `P1-01-app-scaffold.md`; `P1-02-engine-rules.md` (supplies the
> legal-move set, the forced/free-choice state, and `applyMove`); `P2-01-board-rendering.md`
> (supplies the 81 tappable cells and every visual state this PRD's behavior must agree with).
> **Depended on by:** `P4-01-audio.md`, `P4-02-haptics.md`, `P4-03-animations.md` — all three
> hook onto the move lifecycle events defined here.

> **Note on source status:** `Game Board Design.md` carries the house banner *"Nothing here is
> settled"* and has **no Decisions section**, yet its **Move Input — Tap to Select, Tap Again to
> Confirm** section is the only specification of this interaction, its Open Questions section is
> empty, `Game Overview.md` → *How a Move Is Made* states the same interaction independently,
> and the approved UI handoff was drawn from it. This PRD therefore treats that section as
> settled and flags disagreements rather than picking a side.

## Problem

There is no application code yet. The board carries 81 tap targets on a phone — the handoff
puts a cell at roughly 35pt, under Apple's 44pt guidance — and in a game where an accidental
move is unrecoverable, a single-tap board would make mis-taps cost turns. Worse, the game's
central mechanic (*the cell you play sends your opponent to the matching quadrant*) is
invisible: a new player has to hold the cell→quadrant mapping in their head and only finds out
where they sent their opponent after the move is already committed.

There is also no defined answer to what a tap on an illegal cell does, and until there is, an
implementer will invent one — a shake, a toast, an error buzz — each of which contradicts the
feedback system the docs actually describe.

## Goal

Placing a mark takes two taps on the same cell. The first tap selects without placing and the
big board previews the quadrant that choice would send the opponent to; the second tap on that
same cell commits the move and passes the turn. Changing your mind needs no cancel button —
tap another legal cell to reselect, or tap outside the grid to clear. Taps on illegal cells do
nothing at all, with no sound, no haptic and no error state, so the only thing that explains an
illegal tap is the locked styling that should have prevented it — which makes it a hard
requirement that the set of cells that accept a tap and the set of cells that *look* tappable
are the same set.

## Requirements

### The two-tap gesture

1. Placing a mark takes **exactly two taps**, not one. *(Game Board Design → Move Input — Tap
   to Select, Tap Again to Confirm; Game Overview → How a Move Is Made.)*
   **Testable:** a widget test that taps a legal empty cell once and asserts the engine state is
   unchanged — no mark placed, same current player.
2. **First tap — select.** A tap on a legal empty cell creates a **pending selection** on that
   cell. It does **not** place a mark and does not pass the turn. *(Game Board Design → Move
   Input, step 1.)*
   **Testable:** after one tap, the exposed pending selection is `{quadrant, cell}` for the
   tapped cell and the engine state is untouched.
3. The first tap makes the big board **highlight the quadrant that choice points to** — the
   quadrant the opponent would be sent to. The destination is the positional identity mapping
   from `P1-02-engine-rules.md` (cell position within its small board = quadrant position within
   the big board). This PRD publishes the pending cell *and* its destination quadrant as input
   state; drawing them is `P2-01-board-rendering.md`. *(Game Board Design → Move Input, step 1
   and → Three highlights on screen at once, whose Pending-move row is scoped "one cell + one
   quadrant"; Game Overview → How a Move Is Made; Rules → Cell → Quadrant Mapping.)*
   **Testable:** for each of the 9 cell positions, a first tap exposes a destination quadrant of
   the same position.
4. **Second tap — confirm.** A tap on the **same cell** commits: the mark is placed and the turn
   passes. It is effectively a **double tap** to place a mark, and there is **no separate
   Confirm button**. *(Game Board Design → Move Input, step 2 and → Confirming.)*
   **Testable:** two taps on the same cell advance the engine by exactly one move; the board
   subtree contains no confirm control.
5. There is **no time window** between the two taps. A fast double-tap and a slow
   tap-look-tap are the same interaction, so the pending selection persists indefinitely until
   it is confirmed, replaced, or cleared. *(Game Board Design → Confirming — "a fast double-tap
   the natural 'I know what I'm doing' gesture, while a slower tap-look-tap gives you the
   preview. Same interaction serves both".)*
   **Testable:** tap, pump the test clock well past any double-tap threshold, tap the same cell
   again — the move commits.
   *Implementation note, not a requirement:* Flutter's `GestureDetector.onDoubleTap` carries its
   own ~300ms window and would violate this; two `onTap` events on the same cell will not.
6. A move is always selected by tapping a **cell**. There is no separate quadrant-picking
   gesture, including on the opening move and in the free-choice state — the legal set simply
   spans more quadrants. *(Game Board Design → Move Input, step 1 — "The player taps a cell in
   the small board"; → Active Quadrant Highlight → The free-choice state, whose Free-choice mode
   highlights every still-open quadrant and which "also covers the opening move"; Rules →
   Placement Rules → First move.)*
   **Testable:** in a free-choice state, a first tap on a cell in any still-open quadrant
   produces a pending selection directly, with no intermediate state.

### Changing your mind

7. **Tapping a different legal cell** replaces the pending selection with that cell. No cancel
   step is required first. *(Game Board Design → Changing your mind.)*
   **Testable:** tap cell A, then cell B — the pending selection is B, nothing is placed, and a
   subsequent tap on B commits B.
8. **Tapping outside the full grid** clears the pending selection entirely and places nothing.
   *(Game Board Design → Changing your mind.)* What counts as "outside the full grid" is
   **OQ-1**.
9. There is **no dedicated cancel control and no confirm control**. Requirements 7 and 8 are the
   only two ways out of a pending selection. *(Game Board Design → Changing your mind — "neither
   needs a dedicated cancel button"; → Confirming — "No separate Confirm button".)*

### Illegal taps

10. **An illegal tap does nothing.** A tap on any cell that is not currently legal — a cell in a
    locked, claimed, or cat-game quadrant, an already-occupied cell, any cell outside the forced
    quadrant — places nothing, selects nothing, clears nothing, and produces **no shake, no
    flash, no error message, no sound, and no haptic buzz**. The absence of feedback *is* the
    feedback. *(Game Board Design → Active Quadrant Highlight → Taps outside the legal quadrant;
    → Haptic Rule; Design Handoff → Interactions & behavior — "Illegal tap does nothing — no
    shake, no flash, no error, and no haptic".)*
    **Testable:** with a pending selection held on a legal cell, tapping an illegal cell leaves
    the engine state *and* the pending selection byte-for-byte unchanged, and fires no audio or
    haptic call. ("Does not clear the pending selection" is the literal reading of *does
    nothing*; no doc addresses it separately.)
11. **Legality is read from the engine, never re-derived in the UI.** The input layer asks
    `P1-02-engine-rules.md` for the legal-move set and the forced/free-choice state; it does not
    reimplement the sending rule, dead-quadrant handling, or occupancy checks. *(Tech Design →
    Decisions → Is the game logic separate from Flutter? — "legal moves, sending rule,
    win/cat-game detection, free-choice state" are engine responsibilities and "the UI layer
    reads from it"; `P1-02-engine-rules.md` requirements 18–19.)*
    **Testable:** driven by an engine state whose forced quadrant is *q*, taps in every other
    quadrant are inert without the test configuring the UI separately.
12. **The visual state and the actual behavior must agree.** For any engine state, the set of
    cells that accept a first tap is **identical** to the set of cells rendered in the playable
    (non-locked, non-claimed, non-cat, unoccupied) state. Nothing explains an illegal tap after
    the fact, so the locked/dimmed styling has to prevent it. *(Game Board Design → Taps outside
    the legal quadrant — "Illegal cells shouldn't accept input. They also shouldn't *look* like
    they would — the visual state and the actual behavior need to agree"; "this is why the
    locked/dimmed styling matters so much: it has to prevent the tap, because nothing will
    explain it after the fact".)*
    **Testable:** a widget test that, for several engine states (forced, free choice, claimed
    and cat quadrants present), asserts set-equality between the cells that respond to a tap and
    the cells the renderer marks playable. This is the requirement that catches a drift between
    `P2-01-board-rendering.md` and this PRD.
13. **A finished game accepts no input.** When the game is won or drawn the engine reports no
    legal moves, so by requirements 10–11 every tap on the board is inert, including taps on the
    board that stays visible behind the game-over overlay. *(`P1-02-engine-rules.md` requirement
    20 — "The game is over; no further moves are legal"; Design Handoff → Interactions &
    behavior → Game over — "1g / 1h overlays the finished board; the board stays visible
    behind".)*

### What the taps trigger

14. **Haptics.** Both the first tap of a two-tap move and the confirming tap are **valid
    actions and fire the haptic**; illegal taps fire none. Everything about the haptic mechanism
    — the API, the subtlety, and the wiring to the *Vibrate on touch* setting it is subject to —
    belongs to `P4-02-haptics.md`. *(Game Board Design → Haptic Rule — "including the first tap
    of a two-tap move, since selecting a legal cell is a valid action"; Menus and UI → Settings
    Menu → Vibrate on Touch; Design Handoff → 2d and → Interactions & behavior.)*
    **Testable:** with a fake haptic sink, a legal first tap and a confirm tap each record one
    invocation; an illegal tap records none.
15. **No sound on selection.** The pending selection gets **no sound of its own** — sound
    belongs to the confirmed move, not the preview, so the board does not chirp while someone
    browses their options. Which sound the confirmed move plays and how it is played belong to
    `P4-01-audio.md`. *(Game Board Design → Move Input → Sound; Design Handoff → 2d — "No sound
    fires on selection (docs)".)*
    **Testable:** with a fake audio sink, a first tap records no playback; a confirm tap records
    exactly one.
16. **The confirm tap, not the select tap, ends the previous move's last-move highlight.** The
    opponent's last-move highlight persists through selecting a cell and previewing the
    destination, and clears only on confirmation. The input layer therefore signals "move
    completed" on the second tap only. Rendering the highlight is
    `P2-01-board-rendering.md`. *(Game Board Design → Last Move Highlight → Lifetime — "The
    highlight persists until your move is completed... only clears once you confirm".)*
    **Testable:** after a first tap the last-move reference is unchanged; after the confirm tap
    it refers to the move just made.
17. **The turn passes immediately on commit.** No interstitial or "pass the phone" screen sits
    between the confirming tap and the opponent's turn. *(Menus and UI → Pass-and-Play Turn
    Handoff — "The game switches the active player automatically after each move" and "The
    handoff can be instant"; Design Handoff → Interactions & behavior — "Turn handoff is
    instant".)*
18. **Animations never block input.** Taps register normally while an animation is playing, and
    the animation is neither interrupted nor skipped by the tap. *(Animations → Decisions →
    Animations don't block input.)*
    **Testable:** a tap dispatched mid-animation produces the same state change as the same tap
    dispatched at rest.

### Where this lives

19. The tap surface is the **per-cell `GestureDetector`** built by
    `P2-01-board-rendering.md` — 81 of them in nested grids — not a hit-test computed over a
    painted board. *(Tech Design → Decisions → How is the board rendered? — "81
    `GestureDetector`s in nested `GridView`/`Column`s, not a `CustomPainter`".)*
20. The **pending selection is UI state, not engine state**. It is held in the Riverpod state
    layer (`lib/state/`) and consumed by `lib/ui/board/`; the pure-Dart engine never learns
    about it. *(Tech Design → Decisions → Is the game logic separate from Flutter?; → State
    management — Riverpod; → Project structure — layer-first; Design Handoff → State, which
    lists `pendingSelection` beside the game fields.)*
    **Testable:** a source scan finds no reference to the pending selection under `lib/engine/`.
21. The pending selection is **never persisted**. Leaving a game and resuming it from the
    open-games list restores the board, the turn and the scoreboard, but no pending selection.
    *(Design Handoff → State — `pendingSelection // { quadrant, cell } | null (never
    persisted)`.)* **Caveat:** `Tech Design.md` annotates that whole state block as *"a design
    sketch, not a decision taken here"*, so this is sourced from the approved handoff rather
    than from a Decisions entry — see also `P1-02-engine-rules.md` OQ-3.
22. Committing applies the move **through the engine** — `Board applyMove(Board, Move)`
    returning new state — and the UI renders what comes back. The input layer never mutates
    board state itself. *(Tech Design → Decisions → Game state is immutable;
    `P1-02-engine-rules.md` requirement 3.)*

### Tests

23. Every behavior above is covered by **widget tests** that assert taps do the right thing.
    **No golden image tests.** They run locally (`flutter test`); nothing runs them on a push.
    *(Tech Design → Decisions → Widget tests for the board — no golden tests — "Test that taps do
    the right thing and that the highlight states appear"; → CI — local builds only.)*

## Out of Scope

Named so the boundary is explicit. Each is specified elsewhere; do not specify it here.

- **What any of it looks like** — the pending-cell ring, the ghost mark, the destination-quadrant
  ring, the locked veil, the claimed/cat overlays, the three highlights' mutual
  distinguishability, board geometry and cell size, and the provisional turn banner ("Play
  here?" / "Tap again to lock it in") — `P2-01-board-rendering.md`. This PRD specifies only
  *which cells accept input, when, and what state the tap produces*.
- **The haptic mechanism** — the API, the "small, subtle buzz" character, and the *Vibrate on
  touch* setting — `P4-02-haptics.md`. Requirement 14 says only *which taps count as valid*.
- **Sound playback** — the audio package, the per-theme sound, the global mute —
  `P4-01-audio.md`. Requirement 15 says only *that the preview is silent*.
- **Legal-move rules** — the sending rule, dead quadrants and free choice, claiming, cat game,
  win and draw detection, and `applyMove` — `P1-02-engine-rules.md`.
- **Animations** — the vocabulary, timing, the global toggle, instant state changes —
  `P4-03-animations.md`. Requirement 18 says only that input outranks them.
- **The scoreboard and turn indicator** — `P2-03-scoreboard-turn-indicator.md`.
- **Persistence of game state** — `P1-04-persistence.md`.
- **Non-touch input.** Design Handoff → Interactions & behavior specifies a focus/hover outline
  "on any pointer or keyboard platform", but no doc specifies keyboard or pointer activation
  semantics, and the target is a portrait phone *(Tech Design → Decisions → Orientation —
  portrait only; Game Board Design → Responsive / Screen Size)*. Nothing here covers it.
- **Anything from `Alternative Game Styles.md`.** Parking-lot doc; explicitly not the game being
  built.

## Open Questions

**OQ-1 — What counts as "outside the full grid"?** `Game Board Design.md` → Changing your mind
says only: *"**Tap outside the full grid** → deselects entirely, clearing the pending move."*
Unspecified: whether the scoreboard row, the settings button, the padding between the board and
the screen edge, and the gaps between quadrants all count; and whether opening the in-game
settings / quick-actions modal (`1f`) clears a pending selection or leaves it standing when the
modal is dismissed. *(Raised by this PRD; not addressed in any doc.)*

**OQ-2 — What does the preview show when the destination quadrant is dead?** `Game Board
Design.md` → Move Input says the first tap makes the big board highlight *"the quadrant that
choice points to — showing where this move would send the opponent."* But `Rules.md` → Edge
Cases → *Sent to a dead quadrant → free choice* says that if that quadrant is claimed or a cat
game, the opponent does **not** go there — they get a free choice of any still-open quadrant.
Highlighting the dead quadrant would therefore preview something that will not happen, which
cuts directly against the stated purpose of the preview as a teaching tool that makes the
sending rule visible. Whether the preview should instead show the free-choice state (and how)
is unspecified. *(Raised by this PRD; not discussed in any doc.)*

**OQ-3 — Are the preview visuals designed or not?** The read-only handoff contradicts itself:
*Interactions & behavior* says of the two-tap move *"Preview visuals still to be designed,"*
while *Cell states* in the same document specifies the pending selection precisely (2pt dashed
`#e9e9ed` at 85%, ghost mark at 40%, plus a dashed destination-quadrant ring) and screen *2d —
Board, pending move* draws all three highlights together. Resolving it belongs to
`P2-01-board-rendering.md`, but requirement 12 of this PRD depends on the provisional and
locked states being visually settled.

**OQ-4 — Does a tap on a locked quadrant really give no feedback?** `Game Board Design.md` →
Taps outside the legal quadrant and → Haptic Rule are explicit that it does not: *"The lack of a
buzz *is* the feedback."* `Menus and UI.md` → Vibrate on Touch justifies the buzz differently:
*"A tap that lands slightly off, or on a locked quadrant, is easy to misread as 'did that
register?' A buzz answers that question without the player having to look for a change."* Read
one way those agree (a buzz means it registered); read another, the second sentence wants a
locked-quadrant tap to be acknowledged. Requirement 10 follows `Game Board Design.md`, which is
explicit and which the handoff repeats; the wording is flagged rather than resolved.

**OQ-5 — What does the engine do if it is ever handed an illegal move?** Carried over from
`P1-02-engine-rules.md` OQ-5. Requirements 10–12 mean the input layer should never send one, so
this does not block building this feature; it decides only what happens if the guard is ever
wrong, and requirement 22's `Board applyMove(Board, Move)` signature does not settle whether it
throws, returns the board unchanged, or returns a result carrying a reason.
