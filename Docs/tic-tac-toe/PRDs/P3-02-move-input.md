# PRD: Move Input — Tap to Select, Tap Again to Confirm

> **Status:** Draft · Source docs read: `Game Board Design.md`, `Game Overview.md`, `Rules.md`,
> `Menus and UI.md`, `Animations.md`, `Tech Design.md`, `Theming.md`, `roadmap.md`, plus the
> read-only reference asset `design_handoff_game_ui/README.md` (screen *2d — Board, pending
> move* and *Interactions & behavior*). `Alternative Game Styles.md` is a declared parking-lot
> doc and was read only to confirm it is out of scope — no requirement here comes from it.

> **Wave:** P3 · **Depends on:** `P1-01-app-scaffold.md`; `P1-02-engine-rules.md` (supplies the
> legal-move set, the forced/free-choice state, and `applyMove`); `P3-01-board-rendering.md`
> (supplies the 81 tappable cells and every visual state this PRD's behavior must agree with);
> and the three wave-2 channels this PRD's move lifecycle fires into —
> `P2-02-audio.md` (the confirmed-move sound), `P2-03-haptics.md` (the buzz on every valid
> tap) and `P2-04-animations.md` (which must never block input). Each owns its own mechanism;
> this PRD owns only *which taps count*.
> **Depended on by:** `P3-05-how-to-play.md`, whose hint text describes this gesture in words.

> **Note on source status:** `Game Board Design.md` carries the house banner *"Nothing here is
> settled"* and has **no Decisions section**, yet its **Move Input — Tap to Select, Tap Again to
> Confirm** section is the only specification of this interaction, its Open Questions section is
> empty, `Game Overview.md` → *How a Move Is Made* states the same interaction independently,
> and the approved UI handoff was drawn from it. This PRD therefore treats that section as
> settled and flags disagreements rather than picking a side.

> **Note on requirement numbering:** stable. The round-2 revision changed the text of
> requirements 9, 10, 12, 13, 14, 15, 18, 19 and 23 and added no new numbers, because the review
> and the sibling PRDs cite these numbers. **Every cross-PRD requirement number cited below was
> re-verified against the current text of that PRD in round 2**, since `P2-02-audio.md`,
> `P2-03-haptics.md` and `P2-04-animations.md` were all revised and the first renumbered — a
> stale number in this family resolves silently to a real but wrong requirement. Where this
> document refers to one of its own requirements it now says *"this PRD's requirement N"*.

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
   state; drawing them is `P3-01-board-rendering.md`. *(Game Board Design → Move Input, step 1
   and → Three highlights on screen at once, whose Pending-move row is scoped "one cell + one
   quadrant"; Game Overview → How a Move Is Made; Rules → Cell → Quadrant Mapping.)*
   **Testable:** for each of the 9 cell positions, a first tap exposes a destination quadrant of
   the same position. This holds for the opening move too: `Rules.md` → Decisions → *Does the
   opening move send the opponent?* answers **yes**, *"exactly as on every later move. There is
   no exception for move 1"*, so no cell position is a special case.
   **This requirement publishes exactly one destination quadrant, which already takes a side in
   OQ-2 and depends on OQ-6.** Read both before implementing.
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
9. There is **no dedicated cancel control and no confirm control**, and a pending selection ends
   in **exactly three ways**: it is **confirmed** (this PRD's requirement 4), **replaced** (this
   PRD's requirement 7), or **cleared** by a tap outside the grid (this PRD's requirement 8).
   Confirming is one of the three — committing the move clears the pending selection as part of
   placing the mark, because the cell it named now holds a committed mark and the preview
   describes something that has already happened. *(Game Board Design → Changing your mind —
   "neither needs a dedicated cancel button" — and → Confirming — "No separate Confirm button" —
   for the absence of controls; → Three highlights on screen at once, whose pending row means
   "where you'd send them **if you confirm**", and which requires the provisional treatment to
   read as "clearly not yet committed", for the clear-on-commit half.)*
   **Testable:** immediately after a confirming tap the pending selection is null. Downstream
   that means `P3-01-board-rendering.md` requirement 23 draws neither the dashed cell ring with
   its 40% ghost mark over the newly committed mark, nor the dashed destination ring, and by
   this PRD's requirement 13 a game-ending move leaves nothing provisional drawn under the
   game-over overlay.

### Illegal taps

10. **An illegal tap does nothing, and the illegal cell absorbs it.** A tap on any cell that is
    not currently legal — a cell in a locked, claimed, or cat-game quadrant, an already-occupied
    cell, any cell outside the forced quadrant — places nothing, selects nothing, clears
    nothing, and produces **no shake, no flash, no error message, no sound, and no haptic
    buzz**. The absence of feedback *is* the feedback. **The tap is consumed where it lands: it
    must not fall through to the tap-outside-the-grid handler of this PRD's requirement 8**,
    because a fall-through would clear the pending selection and so would not be "nothing".
    *(Game Board Design → Active Quadrant Highlight → Taps outside the legal quadrant; → Haptic
    Rule; → Changing your mind, whose clear is scoped to taps *outside the full grid*; Design
    Handoff → Interactions & behavior — "Illegal tap does nothing — no shake, no flash, no
    error, and no haptic".)*
    **Testable:** with a pending selection held on a legal cell, tapping an illegal cell leaves
    the engine state *and* the pending selection byte-for-byte unchanged, and fires no audio or
    haptic call. ("Does not clear the pending selection" is the literal reading of *does
    nothing*; no doc addresses it separately.) The absorption mechanism is this PRD's
    requirement 19.
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
    **Testable, but not yet anchorable — see OQ-7.** The intended assertion is set-equality, for
    several engine states (forced, free choice, claimed and cat quadrants present), between the
    cells that respond to a tap and the cells the renderer marks playable. The first set is this
    PRD's and is directly observable; **the second set has nothing to read it from today** —
    `P3-01-board-rendering.md` requirement 40 enumerates addressable cell states as *empty, P1,
    P2, last move, pending*, with no per-cell playable state, and its locked state is
    quadrant-level only. This is the requirement that would catch a drift between that PRD and
    this one, so leaving it unanchored is not acceptable; what to anchor it on is OQ-7.
13. **A finished game accepts no input.** When the game is won or drawn the engine reports no
    legal moves, so by this PRD's requirements 10–11 every tap on the board is inert, including
    taps on the board that stays visible behind the game-over overlay. By this PRD's requirement
    9 the game-ending move left no pending selection behind, so nothing provisional is drawn
    under that overlay. *(`P1-02-engine-rules.md` requirement 20 — "The game is over; no further
    moves are legal"; Design Handoff → Interactions & behavior → Game over — "1g / 1h overlays
    the finished board; the board stays visible behind".)*

### What the taps trigger

14. **Haptics.** Both the first tap of a two-tap move and the confirming tap are **valid
    actions and fire the haptic**; illegal taps fire none. Everything about the haptic mechanism
    — the API, the subtlety, and the wiring to the *Vibrate on touch* setting it is subject to —
    belongs to `P2-03-haptics.md`, whose **requirement 2** (the first tap of a two-tap move
    fires it, and so does the confirming tap) and **requirement 4** (an illegal tap does
    nothing) state the same rule from its side, and whose **requirement 3** covers the
    reselection of this PRD's requirement 7. *(Game Board Design → Haptic Rule — "including the
    first tap of a two-tap move, since selecting a legal cell is a valid action"; Menus and UI →
    Settings Menu → Vibrate on Touch; Design Handoff → 2d and → Interactions & behavior.)*
    **Testable:** a legal first tap and a confirming tap each classify as one valid action and
    each invoke the haptic layer exactly once; an illegal tap classifies as no action and does
    not invoke it. `P2-03-haptics.md` **requirement 13** — added in its own round-2 revision —
    now gives that assertion something concrete to name: *"every haptic in the app goes through
    a single app-level entry point"* with the vibrate gate **inside** it, so this PRD's call
    sites invoke it unconditionally and never read the setting. **What remains unstated is
    whether that entry point can be substituted in a widget test — see OQ-8**, which is narrowed
    to exactly that.
15. **No sound on selection.** The pending selection gets **no sound of its own** — sound
    belongs to the confirmed move, not the preview, so the board does not chirp while someone
    browses their options. Which sound the confirmed move plays and how it is played belong to
    `P2-02-audio.md`, whose **requirement 8** is the silent-preview rule (`placeMark` fires on
    the second, confirming tap only, and reselecting or tapping outside is also silent) and
    whose **requirement 9** keeps illegal taps silent. *(Game Board Design → Move Input → Sound;
    Design Handoff → 2d — "No sound fires on selection (docs)".)*
    **Testable:** the move lifecycle emits a *move committed* event on the second tap only, and
    emits nothing on selection, reselection, tap-outside, or an illegal tap. Asserting that no
    sound was *played* rests on the same substitutability question as this PRD's requirement 14:
    `P2-02-audio.md` requirement 2 puts all playback behind one audio layer that call sites
    address by naming a moment, but its requirement 5 routes only the active theme and the sound
    setting through Riverpod, and nothing says the layer itself can be overridden — see OQ-8.
16. **The confirm tap, not the select tap, ends the previous move's last-move highlight.** The
    opponent's last-move highlight persists through selecting a cell and previewing the
    destination, and clears only on confirmation. The input layer therefore signals "move
    completed" on the second tap only. Rendering the highlight is
    `P3-01-board-rendering.md`. *(Game Board Design → Last Move Highlight → Lifetime — "The
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
    Animations don't block input; `P2-04-animations.md` **requirement 15** — animations never
    block input, taps are accepted while one plays — and **requirement 16** — a tapped-through
    animation is neither interrupted nor skipped.)*
    **Testable:** a tap dispatched mid-animation produces the same state change as the same tap
    dispatched at rest.

### Where this lives

19. The tap surface is the **per-cell `GestureDetector`** built by
    `P3-01-board-rendering.md` — 81 of them in nested grids — not a hit-test computed over a
    painted board. **Every cell hit-tests as opaque over its full square, whatever it draws.**
    Two consequences, and both are load-bearing:
    - a legal **empty** cell must still take taps even though it renders nothing —
      `P3-01-board-rendering.md` requirement 15 makes it *"transparent, with no fill and no
      border"*, and a transparent child under `HitTestBehavior.deferToChild` does not hit-test
      at all, so deferring to the child would make the whole board inert;
    - an **illegal** cell must consume the tap rather than let it pass through to the
      tap-outside handler, which is what this PRD's requirement 10 "clears nothing" depends on.

    *(Tech Design → Decisions → How is the board rendered? — "81 `GestureDetector`s in nested
    `GridView`/`Column`s, not a `CustomPainter`"; `P3-01-board-rendering.md` requirements 3 and
    15 for the transparent, unfilled cell; Game Board Design → Taps outside the legal quadrant
    and → Changing your mind for the two behaviors this has to keep apart.)*
    **Testable:** with a pending selection active, a tap at the centre of an empty legal cell
    selects it, and a tap at the centre of an empty illegal cell leaves the pending selection
    intact — neither tap reaches a board-level or screen-level handler. The gaps *between* cells
    and quadrants are a separate question — see OQ-1.
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
    than from a Decisions entry — see also `P1-02-engine-rules.md` OQ-3. The `{quadrant, cell}`
    shape it names is also what OQ-2 turns on.
22. Committing applies the move **through the engine** — `Board applyMove(Board, Move)`
    returning new state — and the UI renders what comes back. The input layer never mutates
    board state itself. *(Tech Design → Decisions → Game state is immutable;
    `P1-02-engine-rules.md` requirement 3.)*

### Tests

23. Every behavior above is covered by **widget tests** that assert taps do the right thing.
    **No golden image tests.** They run locally (`flutter test`); nothing runs them on a push.
    *(Tech Design → Decisions → Widget tests for the board — no golden tests — "Test that taps do
    the right thing and that the highlight states appear"; → CI — local builds only.)*
    Two assertions above cannot be written as stated yet: requirement 12's second set has
    nothing to read it from (OQ-7), and requirements 14–15 need their channel entry points to be
    substitutable (OQ-8). Neither blocks the behavior — only its assertion.

## Out of Scope

Named so the boundary is explicit. Each is specified elsewhere; do not specify it here.

- **What any of it looks like** — the pending-cell ring, the ghost mark, the destination-quadrant
  ring, the locked veil, the claimed/cat overlays, the three highlights' mutual
  distinguishability, board geometry and cell size, and the provisional turn banner ("Play
  here?" / "Tap again to lock it in") — `P3-01-board-rendering.md`. This PRD specifies only
  *which cells accept input, when, and what state the tap produces*.
- **Explaining the gesture to the player** — the hint text "Tap a square to see where it sends
  them. / Tap it again to play it." and the on-board legend: `P3-05-how-to-play.md`. This PRD
  implements the gesture; that one describes it in words. Note its requirement 15 also asserts
  what a tap on that text does — see OQ-1.
- **The haptic mechanism** — the API, the "small, subtle buzz" character, the single app-level
  entry point, and the *Vibrate on touch* setting — `P2-03-haptics.md`. This PRD's requirement
  14 says only *which taps count as valid*.
- **Sound playback** — the audio package, the audio layer, the per-theme sound, the global mute
  — `P2-02-audio.md`, whose requirement 8 owns the silent-preview rule. This PRD's requirement
  15 says only *that the preview is silent from the input side*.
- **Legal-move rules** — the sending rule, dead quadrants and free choice, claiming, cat game,
  win and draw detection, and `applyMove` — `P1-02-engine-rules.md`.
- **Animations** — the vocabulary, timing, the global toggle, instant state changes —
  `P2-04-animations.md`, whose requirements 15–16 own the non-blocking rule. This PRD's
  requirement 18 says only that input outranks them.
- **The scoreboard and turn indicator** — `P3-03-scoreboard-turn-indicator.md`.
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
Unspecified, and each of these is a place a real tap can land:

- the scoreboard row, the settings button, and the padding between the board and the screen
  edge;
- the 8pt gaps **between quadrants** *(`P3-01-board-rendering.md` requirement 3)*;
- the **3pt gutters between cells and the 5pt quadrant padding** *(same requirement)* — these
  are *inside* the grid, so this PRD's requirement 8 "outside the full grid" does not reach them
  at all, and requirement 19's per-cell absorption does not cover them either. A tap in a gutter
  currently has no specified behavior;
- whether opening the in-game settings / quick-actions modal (`1f`) clears a pending selection
  or leaves it standing when the modal is dismissed.

*(Raised by this PRD; not addressed in any doc.)*

> **Carried by three sibling PRDs. Two record it open; the third has already answered one
> instance of it.**
> `P4-04-settings.md` → Open Question 5 records the modal half as unresolved and points back
> here — an earlier draft of its requirement 2 asserted the pending selection survives the
> surface, and that assertion has since been removed. `P2-01-navigation.md` → Open Question 11
> records the same conflict from the routing side, though its wording still describes the
> `P4-04` assertion that no longer exists.
> **`P3-05-how-to-play.md` requirement 15 does not record it as open.** It asserts that its
> layer is non-interactive and that *"a tap landing on the hint or the legend is a tap outside
> the grid, and therefore clears any pending selection, exactly as a tap on any other non-board
> area does"*, with a testable to match — deciding one instance of this question in one PRD
> while three others hold it open. No design doc settles it either way, and this PRD does not
> settle it here. Whatever the answer is, all four must carry the same one.

**OQ-2 — What does the preview show when the destination quadrant is dead?** `Game Board
Design.md` → Move Input says the first tap makes the big board highlight *"the quadrant that
choice points to — showing where this move would send the opponent."* But `Rules.md` → Edge
Cases → *Sent to a dead quadrant → free choice* says that if that quadrant is claimed or a cat
game, the opponent does **not** go there — they get a free choice of any still-open quadrant.
Highlighting the dead quadrant would therefore preview something that will not happen, which
cuts directly against the stated purpose of the preview as a teaching tool that makes the
sending rule visible. Whether the preview should instead show the free-choice state (and how)
is unspecified. *(Raised by this PRD; not discussed in any doc.)*

> **This PRD has already taken a side, and should be read as such rather than as neutral.**
> Requirement 3 publishes **exactly one** destination quadrant, and requirement 21's
> `{quadrant, cell}` shape has no way to express "the opponent will get a free choice" — so as
> written, this PRD previews the dead quadrant. That is the literal reading of `Game Board
> Design.md`, not a decision made here, and it is the answer that will ship by default. If the
> other answer is wanted, requirement 3 and the published pending shape both change, and
> `P3-01-board-rendering.md` requirement 23 gains a state it does not have.

**OQ-3 — Are the preview visuals designed or not?** The read-only handoff contradicts itself:
*Interactions & behavior* says of the two-tap move *"Preview visuals still to be designed,"*
while *Cell states* in the same document specifies the pending selection precisely (2pt dashed
`#e9e9ed` at 85%, ghost mark at 40%, plus a dashed destination-quadrant ring) and screen *2d —
Board, pending move* draws all three highlights together. Resolving it belongs to
`P3-01-board-rendering.md` (whose requirement 23 builds from the specified version and whose
Open Questions flag the same contradiction), but requirement 12 of this PRD depends on the
provisional and locked states being visually settled.

**OQ-4 — Does a tap on a locked quadrant really give no feedback?** `Game Board Design.md` →
Taps outside the legal quadrant and → Haptic Rule are explicit that it does not: *"The lack of a
buzz *is* the feedback."* `Menus and UI.md` → Vibrate on Touch justifies the buzz differently:
*"A tap that lands slightly off, or on a locked quadrant, is easy to misread as 'did that
register?' A buzz answers that question without the player having to look for a change."* Read
one way those agree (a buzz means it registered); read another, the second sentence wants a
locked-quadrant tap to be acknowledged. Requirement 10 follows `Game Board Design.md`, which is
explicit and which the handoff repeats; the wording is flagged rather than resolved. Related but
separate, and both `P2-03-haptics.md`'s rather than this PRD's: its OQ-4 asks whether *tapping
outside the grid to deselect* buzzes — a valid action by this PRD's requirement 8 and a tap on
nothing at the same time — and its OQ-5 asks whether the app is meant to have any validity
signal at all when vibrate is off.

**OQ-5 — What does the engine do if it is ever handed an illegal move?** Carried over from
`P1-02-engine-rules.md` OQ-5. Requirements 10–12 mean the input layer should never send one, so
this does not block building this feature; it decides only what happens if the guard is ever
wrong, and requirement 22's `Board applyMove(Board, Move)` signature does not settle whether it
throws, returns the board unchanged, or returns a result carrying a reason.

**OQ-6 — A move that claims (or cat-games) the very quadrant it sends the opponent to — which
state does the send see, before or after the move?** Carried from `Rules.md` → Open Questions
via `P1-02-engine-rules.md` OQ-6, worded there as:

> Example: play the centre cell of quadrant 5, and that same move completes three in a row *in*
> quadrant 5, claiming it. The cell played sends the opponent to the center quadrant — but is
> the send evaluated against quadrant 5's state *before* this move... or *against its state
> after* this move (the quadrant is already dead by the time the send happens, so the opponent
> gets free choice instead)?

It lands here, not only on the engine, because **requirement 3 computes and shows the preview at
select time — before the move exists**. Whichever answer is taken, the preview drawn on the
first tap has to match what the second tap actually does, and for exactly the moves this
question is about, the pre-move and post-move answers differ. `P1-02-engine-rules.md` notes its
own requirement 18 already presupposes one of the two answers. Not resolved here.

**OQ-7 — What does requirement 12's set-equality compare against?** *(Raised by this PRD.)*
The assertion needs a second set — "the cells the renderer marks playable" — and
`P3-01-board-rendering.md` does not expose one: its requirement 40 makes each *cell* state
addressable as *empty, P1, P2, last move, pending*, none of which is "playable", and its locked,
claimed and cat states are **quadrant**-level (its requirements 10–12). Deriving the second set
from quadrant state plus occupancy inside this PRD's test would re-implement legality in the
test and so assert nothing, which is the trap requirement 11 exists to avoid. Either
`P3-01-board-rendering.md` gains a per-cell playable/unplayable addressable state, or requirement
12 is anchored on something else. That is a change to a sibling PRD in the same wave and is not
this PRD's to make.

**OQ-8 — Are the haptic and audio entry points substitutable in a widget test?** *(Raised by
this PRD; **narrowed** in round 2 after both sibling PRDs were revised.)* Requirements 14 and 15
have to assert *"buzzed once, played nothing"* and *"played once"*. Half of what that needs now
exists, and the earlier draft of this question — which said no seam existed at all — was
overtaken:

- `P2-03-haptics.md` **requirement 13** puts every haptic behind **one app-level entry point**,
  with the vibrate gate inside it, and forbids any platform haptic outside the layer;
- `P2-02-audio.md` **requirement 2** puts all playback behind **one audio layer** that call
  sites address by naming a moment, never by constructing a player.

So each channel now has a single named thing to intercept. What neither PRD states is that the
entry point is **injectable**: `P2-02-audio.md` requirement 5 routes the active theme and the
sound setting through Riverpod but says nothing about the layer itself, `P2-03-haptics.md` names
no provider at all, and that PRD's own requirement 13 testable is satisfied by a source scan
plus a setting-on/setting-off count — neither of which needs an override to exist. If both ship
as static entry points, this PRD's tests can observe them only through platform-channel traffic,
which is a sibling's internals and brittle. The shape `Tech Design.md` → Decisions → State
management — Riverpod already points at — a plain `NotifierProvider` a widget test can override
— would settle it, but nothing says so. Both features ship a wave earlier, so the seam is theirs
to define, not this PRD's.
