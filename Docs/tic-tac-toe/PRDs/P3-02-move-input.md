**Build-readiness: 96**

# PRD: Move Input — Tap to Select, Tap Again to Confirm

> **Why 96:** every requirement binds to a named symbol — `P1-02`'s `Board` API, `P3-01`'s
> `BoardView`/`CellView`/`BoardKeys`, `P2-01`'s `AppNavigator`, `P2-02`'s `audioLayerProvider`,
> `P2-03`'s `hapticServiceProvider` — this PRD publishes its own interface rather than describing
> it, every verification can be written, and **OQ-2 closed this round**, which was the last
> question of this PRD's own that an implementer could have guessed at. Nothing here is blocked
> or unbuildable. The residue is two flags that change no requirement in this file: **OQ-3** is a
> contradiction inside the read-only handoff and is `P3-01`'s to resolve, and **OQ-4** is a
> wording ambiguity between two design docs where requirement 10 follows the explicit one.
> Author's estimate, pending re-grade.

> **Status:** Draft · Source docs read: `Game Board Design.md`, `Game Overview.md`, `Rules.md`,
> `Menus and UI.md`, `Animations.md`, `Tech Design.md`, `Theming.md`, `roadmap.md`, plus the
> read-only reference asset `design_handoff_game_ui/README.md` (screen *2d — Board, pending
> move* and *Interactions & behavior*). `Alternative Game Styles.md` is a declared parking-lot
> doc and was read only to confirm it is out of scope — no requirement here comes from it.

> **Wave:** P3 · **Depends on:** `P1-01-app-scaffold.md` (the `ProviderScope` above the root
> widget, and `lib/state/`); `P1-02-engine-rules.md` (`Board`, `Move`, `legalMoves`,
> `placementState`, `activeQuadrant`, `quadrantAt`, `applyMove`, `IllegalMoveError`);
> `P3-01-board-rendering.md` (`BoardView`, `CellView`, `BoardKeys` — this PRD supplies its
> `onCellTap` and all four pending parameters); and the three wave-2 channels this move
> lifecycle fires into — `P2-02-audio.md` (`AudioLayer.play` for three of its five moments),
> `P2-03-haptics.md` (`HapticService.validAction()`) and `P2-04-animations.md` (which must never
> block input).
> **Depended on by:** `P3-01-board-rendering.md` requirement 23 (draws the pending selection
> this publishes, in all three of its states), `P2-01-navigation.md` requirement 20 (calls
> requirement 24's `clear()` before every router call), `P3-05-how-to-play.md` (describes this
> gesture in words; its requirement 15 depends on requirement 26 below).
> **One inbound edit is owed:** `P2-02-audio.md` requirement 6's *Call-site owner* column still
> reads **"none — see Out of Scope"** for `claimQuadrant` and `catGame`, and its header note
> still says two of five moments have no caller. Requirements 32–33 below take both. That is
> that PRD's line to change, not this one's; it is queued.

> **Note on source status:** `Game Board Design.md` carries the house banner *"Nothing here is
> settled"* and, until recently, had **no Decisions section at all** — its **Move Input — Tap
> to Select, Tap Again to Confirm** section is nonetheless the only specification of this
> interaction, `Game Overview.md` → *How a Move Is Made* states the same interaction
> independently, and the approved UI handoff was drawn from it. This PRD therefore treats that
> section as settled and flags disagreements rather than picking a side. That doc now has a
> `## Decisions` section holding two entries this PRD depends on: the tap-outside rule
> (requirement 26) and the self-claiming preview (requirement 3).

> **Note on numbering.** Requirements **1–22 keep their numbers** — `P1-02` cites 21 and 22,
> `P2-01` cites 24 and 30, `P2-03` cites 10, 14 and 15, `P2-02` cites 15, and `P3-01` cites 3,
> 10, 19, 25, 26 and 27. Requirements **23–31** hold the published interface and commit safety,
> **32–33** the commit's sounds, and **34** is the test requirement once numbered 23.
> Open-question numbers are stable: **OQ-1, OQ-2, OQ-5, OQ-6, OQ-7 and OQ-8 are answered and
> kept as closed stubs**, following `P1-02-engine-rules.md`, because siblings cite them by
> number. Every cross-PRD number and quotation below was re-verified against that PRD's current
> text this round.

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
big board previews where confirming would send the opponent — one quadrant when the send lands
somewhere, every still-open quadrant when the move kills its own destination. The second tap on
that same cell commits the move, passes the turn, and makes whatever sound that move earned.
Changing your mind needs no cancel button — tap another legal cell to reselect, or tap anywhere
that is not a cell to clear. Taps on illegal cells do nothing at all, with no sound, no haptic
and no error state, so the only thing that explains an illegal tap is the locked styling that
should have prevented it — which makes it a hard requirement that the set of cells that accept a
tap and the set of cells that *look* tappable are the same set. The pending selection ships as
one named provider that `P3-01-board-rendering.md` draws from and nothing else writes.

## Requirements

### The two-tap gesture

1. Placing a mark takes **exactly two taps**, not one. *(Game Board Design → Move Input — Tap
   to Select, Tap Again to Confirm; Game Overview → How a Move Is Made.)*
   **Verification:** tapping a legal empty cell once leaves `boardProvider` `identical()` to its
   pre-tap value — no mark, same `currentPlayer`.
2. **First tap — select.** A tap on a legal empty cell creates a **pending selection** on that
   cell. It does **not** place a mark and does not pass the turn. *(Game Board Design → Move
   Input, step 1.)*
   **Verification:** after one tap, `pendingSelectionProvider` holds a `PendingSelection` whose
   `move` is the tapped cell, and `boardProvider` is identical to its pre-tap value.
3. **The first tap previews what confirming would do to the big board, read from the board as it
   would be *after* the move.** Never from the cell's position. Requirement 25's select path
   computes `applyMove(board, move)` as a throwaway preview (requirement 31) and publishes
   **three** facts from it — `placementState`, `activeQuadrant`, and the quadrants the opponent
   could then play in — which is everything `P3-01` requirement 23's three-way branch needs:

   | Previewed `placementState` | Published | What `P3-01` draws |
   |---|---|---|
   | `forced` | `destinationQuadrant` = the previewed `activeQuadrant` | its dashed ring on that one quadrant |
   | `freeChoice` | `destinationQuadrant` = null, `freeChoiceQuadrants` = the previewed open set | its **available** treatment across every quadrant in that set |
   | `gameOver` | `destinationQuadrant` = null, `freeChoiceQuadrants` = empty | no big-board treatment |

   **The free-choice row is a Decision, not a fallback.** *"**Every still-open quadrant is
   highlighted.** ... if that move would claim or cat-game the very quadrant it points at, the
   quadrant is dead by the time the send resolves and the opponent gets a free choice — so there
   is no single quadrant to ring. The preview shows the truth — the opponent may play anywhere
   still open — rather than showing nothing."* *(`Game Board Design.md` → Decisions → **What does
   the board preview when the selected move would claim its own send target?**, which also gives
   the reasoning: it reuses the free-choice highlight that exists for the state *after* such a
   move lands, so preview and result look consistent, and it teaches the rule at the moment it
   fires.)*

   **The previewed open set is the post-move one, and that distinction is the whole point.** The
   quadrant the pending move is about to claim is open **now** and dead **then**; substituting
   the current board's open set would preview a quadrant the opponent cannot use. `P3-01`
   requirement 23 states the same constraint from its side and takes the set as data rather than
   computing it, so this is the only place it is derived:

   ```dart
   // requirement 25's select path — from the SAME throwaway preview, not a second call
   final preview = applyMove(board, move);
   final freeChoice = preview.placementState == PlacementState.freeChoice
       ? {for (final m in preview.legalMoves) m.quadrant}   // P1-02 req 35
       : const <int>{};

   // WRONG — previews the quadrant this move is about to kill:
   //   {for (var q = 0; q < 9; q++) if (board.quadrantAt(q) == QuadrantState.open) q}
   ```

   Deriving it from the previewed `legalMoves` rather than from `quadrantAt` makes it exactly
   *"where the opponent may play"* — the engine's own answer, with no equivalence argument
   needed, and requirement 11 untouched. Gating on `placementState` keeps `P3-01` requirement
   43's invariant — the set is non-empty **exactly** when the state is `freeChoice` — structural
   rather than incidental; in `gameOver` the previewed `legalMoves` is empty anyway (`P1-02`
   requirement 19), and the explicit branch means nobody has to know that to read the code.

   **Why not positional identity.** `Rules.md` → Cell → Quadrant Mapping is the *rule*, and
   `P1-02` requirement 12 implements it as `activeQuadrant == move.cell` — but requirement 17
   overrides it whenever the destination is dead, **including when this very move is what killed
   it**. An earlier draft specified the positional mapping directly; for every move that claims
   or cat-games its own send target, that preview pointed at a quadrant the opponent will not be
   sent to. Asking the engine costs one pure call and cannot drift from it.

   *(Game Board Design → Move Input, step 1, and → Three highlights on screen at once; Game
   Overview → How a Move Is Made; `Rules.md` → Decisions → **Does a move that claims its own send
   target still send there?**; `P1-02` requirements 17, 33, 35 and 36.)*
   **Verification, four cases:** (a) on a board where the destination is in play, a first tap on
   cell *c* publishes `destinationQuadrant == c`, `destinationState == PlacementState.forced` and
   an **empty** `freeChoiceQuadrants`, for each of the 9 positions; (b) the same on the opening
   move — `Rules.md` → Decisions → *Does the opening move send the opponent?* answers **yes**,
   *"exactly as on every later move. There is no exception for move 1"*; (c) on a board where the
   tapped cell completes three in a row in its own quadrant, the tap publishes `freeChoice`, a
   null destination, and a `freeChoiceQuadrants` that **excludes the quadrant being claimed** and
   equals the previewed board's open set — matching `P1-02` requirement 17(c); (d) on a board
   where the tapped cell wins or draws the game, the tap publishes `gameOver`, a null
   destination and an empty set.
4. **Second tap — confirm.** A tap on the **same cell** commits: the mark is placed and the turn
   passes. It is effectively a **double tap**, and there is **no separate Confirm button**.
   *(Game Board Design → Move Input, step 2 and → Confirming.)*
   **Verification:** two taps on one cell advance `boardProvider` by exactly one move
   (`lastMove` equals it, `currentPlayer` flipped); the board subtree contains no confirm
   control.
5. There is **no time window** between the two taps. A fast double-tap and a slow tap-look-tap
   are the same interaction, so a pending selection persists indefinitely until it is confirmed,
   replaced, or cleared. *(Game Board Design → Confirming — "a fast double-tap the natural 'I
   know what I'm doing' gesture, while a slower tap-look-tap gives you the preview. Same
   interaction serves both".)*
   **Verification:** tap, pump the test clock well past any double-tap threshold, tap the same
   cell — the move commits.
   *Implementation note, not a requirement:* Flutter's `GestureDetector.onDoubleTap` carries its
   own ~300ms window and would violate this; two `onTap` events will not.
   **Consequence, handled by requirement 30:** "indefinitely" outlives the board the selection
   was computed against unless something invalidates it — and under requirement 3 a stale
   selection now carries a stale *previewed set* too, which is the sharper reason it must not
   survive.
6. A move is always selected by tapping a **cell**. There is no separate quadrant-picking
   gesture, including on the opening move and in free choice — the legal set simply spans more
   quadrants. *(Game Board Design → Move Input, step 1 — "The player taps a cell in the small
   board"; → Active Quadrant Highlight → The free-choice state, which "also covers the opening
   move"; Rules → Placement Rules → First move; `P1-02` requirement 18 — exactly two placement
   states, the opening move being the free-choice one, not a third.)*
   **Verification:** on `Board.newSeries()` (81 legal moves), a first tap on a cell in any
   quadrant produces a pending selection directly, with no intermediate state.

### Changing your mind

7. **Tapping a different legal cell** replaces the pending selection. No cancel step first.
   *(Game Board Design → Changing your mind.)*
   **Verification:** tap cell A then cell B — the pending selection is B with B's own previewed
   values, `boardProvider` is unchanged, and a further tap on B commits B.
8. **Tapping anything that is not a cell clears the pending selection entirely** and places
   nothing. *(Game Board Design → Changing your mind — *"Tap outside the full grid → deselects
   entirely, clearing the pending move"* — and → Decisions → **Does a tap outside the board
   clear a pending move?**, which settles the scope of "outside".)* Requirement 26 defines the
   boundary and names the two mechanisms.
   **Verification:** with a selection active, a tap in a cell gutter, in the quadrant padding,
   in a gap between quadrants, on the scoreboard, or on the legend strip each leave
   `pendingSelectionProvider` null and `boardProvider` unchanged.
9. There is **no dedicated cancel control and no confirm control**, and a pending selection ends
   in **exactly three ways**: **confirmed** (requirement 4), **replaced** (requirement 7), or
   **cleared** by a tap that is not on a cell (requirement 8, bounded by requirement 26).
   Confirming is one of the three — committing clears the selection as part of placing the mark,
   because the cell it named now holds a committed mark and the preview describes something that
   has already happened. *(Game Board Design → Changing your mind — "neither needs a dedicated
   cancel button" — and → Confirming — "No separate Confirm button" — for the absent controls; →
   Three highlights on screen at once, whose pending row means "where you'd send them **if you
   confirm**" and which requires the provisional treatment to read as "clearly not yet
   committed", for the clear-on-commit half.)*
   **Verification:** immediately after a confirming tap, `pendingSelectionProvider` is null, so
   `P3-01` requirement 23 draws no `BoardKeys.cellPending`, no `cellGhostMark`, no
   `quadrantPendingDestination` and no `quadrantPendingFreeChoice`; and by requirement 13 a
   game-ending move leaves nothing provisional under the game-over overlay. Requirement 30 is
   the mechanism delivering the confirmed case.

### Illegal taps

10. **An illegal tap does nothing, and the illegal cell absorbs it.** A tap on any cell that is
    not currently legal — one in a locked, claimed or cat-game quadrant, an occupied cell, any
    cell outside the forced quadrant — places nothing, selects nothing, clears nothing, and
    produces **no shake, no flash, no error message, no sound, and no haptic buzz**. The absence
    of feedback *is* the feedback. **The tap is consumed where it lands: it must not reach
    requirement 26's clear surface**, because a fall-through would clear the pending selection
    and so would not be "nothing". *(Game Board Design → Active Quadrant Highlight → Taps
    outside the legal quadrant; → Haptic Rule; → Decisions → Does a tap outside the board clear
    a pending move?, whose clear is scoped to taps that are not on a cell; Design Handoff →
    Interactions & behavior — "Illegal tap does nothing — no shake, no flash, no error, and no
    haptic".)*
    **A cell is a cell whether or not it is legal**, so it absorbs; the distinction from
    requirement 26 is carried entirely by which widget takes the tap — see requirements 19
    and 26.
    **Verification:** with a selection held on a legal cell, tapping an illegal cell leaves
    `boardProvider` `identical()` and `pendingSelectionProvider` equal to its pre-tap value, and
    records zero calls on both the overridden `HapticService` and `AudioLayer`. ("Clears
    nothing" is the literal reading of *does nothing*; no doc addresses it separately.) The
    absorption mechanism is requirement 19; the decision is requirement 25's first branch.
11. **Legality is read from the engine, never re-derived in the UI.** The input layer reads
    `board.legalMoves` and `board.placementState`; it does not reimplement the sending rule,
    dead-quadrant handling, or occupancy checks. *(Tech Design → Decisions → Is the game logic
    separate from Flutter?; `P1-02` requirements 18–19, 35–36.)*
    **Verification:** driven by an engine state whose forced quadrant is *q*, taps in every
    other quadrant are inert with no UI-side configuration; a source scan of `lib/state/` and
    `lib/ui/board/` finds no comparison of a cell index against a quadrant index and no
    reimplementation of `legalMoves`.
12. **The visual state and the actual behavior must agree.** For any engine state, the set of
    cells that accept a first tap is **identical** to the set of cells the renderer marks
    playable. Nothing explains an illegal tap after the fact, so the locked/dimmed styling has
    to prevent it. *(Game Board Design → Taps outside the legal quadrant — "Illegal cells
    shouldn't accept input. They also shouldn't *look* like they would — the visual state and
    the actual behavior need to agree"; "the locked/dimmed styling... has to prevent the tap,
    because nothing will explain it after the fact".)*
    **Verification — anchored, closing OQ-7.** `P3-01` requirement 45 publishes
    **`BoardKeys.cellPlayable(q, c)`**, present exactly when
    `board.legalMoves.contains(Move(quadrant: q, cell: c))`. For boards in the forced,
    free-choice, claimed-and-cat and game-over states: the set of cells carrying `cellPlayable`
    equals the set of cells whose tap produces a pending selection, with both differences empty.
    Per-cell, so it covers the occupied cell and the cell inside a dead quadrant, which the
    quadrant-level `locked` key cannot express.
13. **A finished game accepts no input.** When the game is won or drawn, `placementState ==
    gameOver` and `legalMoves` is empty *(`P1-02` requirements 19, 36–37)*, so by requirements
    10–11 and 25 every tap is inert, including taps on the board that stays visible behind the
    game-over overlay. By requirement 9 the game-ending move left no pending selection, so
    nothing provisional is drawn under it. *(Design Handoff → Interactions & behavior → Game
    over — "1g / 1h overlays the finished board; the board stays visible behind"; `P1-02`
    requirement 20.)*
    **Verification:** from a board whose `outcome != inProgress`, dispatch a tap to each of the
    81 cells; afterwards `boardProvider` is `identical()` to its pre-tap value,
    `pendingSelectionProvider` is null, both overridden channels record zero calls, and no
    `IllegalMoveError` is thrown — requirement 29's guard means `applyMove` is never reached, so
    the engine's `gameAlreadyFinished` path (`P1-02` requirement 42) is never exercised from the
    UI.

### What the taps trigger

14. **Haptics.** The first tap of a two-tap move, a reselecting tap, and the confirming tap are
    all **valid actions and fire the haptic**; illegal taps fire none. The mechanism — the API,
    the subtlety, the vibrate gate — is `P2-03-haptics.md`, whose requirement 2 (first and
    confirming tap), requirement 3 (reselection) and requirement 4 (illegal tap) state the same
    rule from its side, and whose requirement 13 puts every buzz behind one entry point with the
    gate **inside** it, so the call sites here invoke it unconditionally and never read the
    setting. *(Game Board Design → Haptic Rule — "including the first tap of a two-tap move,
    since selecting a legal cell is a valid action"; Menus and UI → Settings Menu → Vibrate on
    Touch; Design Handoff → 2d and → Interactions & behavior.)*
    **Verification — closes OQ-8 on the haptics side.** In a widget test wrapped in
    `ProviderScope(overrides: [hapticServiceProvider.overrideWithValue(FakeHapticService())])`,
    the fake counting `validAction()`: legal first tap → 1; tap on a different legal cell → 2;
    confirming tap → 3; tap on any illegal cell → still 3; tap in a gutter or on the scoreboard
    → still 3. No `TestDefaultBinaryMessenger` handler and no `SystemChannels` interception
    anywhere in the test, per `P2-03` requirement 15. **The reselection count is the load-bearing
    one:** `P2-03` requirement 3's wave note records reselection as *"now asserted"* **by this
    requirement's `→ 2`**, having previously recorded it as asserted by no PRD — whether a
    reselect tap reaches `validAction()` is a call-site fact, and this is the call site. Whether
    requirement 26's clear should itself buzz is that PRD's OQ-4; the counts above encode
    today's answer, "no". **One buzz per valid tap regardless of how many sounds that tap
    causes** — requirement 32 can add a second sound to a commit; it never adds a second buzz,
    because `P2-03` requirement 6 bans a distinct haptic per action type.
15. **No sound on selection.** The pending selection gets **no sound of its own** — sound belongs
    to the confirmed move, not the preview, so the board does not chirp while someone browses
    options. `P2-02-audio.md` requirement 8 is the same rule from its side, and its requirement
    9 keeps illegal taps silent. *(Game Board Design → Move Input → Sound; Design Handoff → 2d —
    "No sound fires on selection (docs)".)*
    **Verification — closes OQ-8 on the audio side.** In a widget test wrapped in
    `ProviderScope(overrides: [audioLayerProvider.overrideWithValue(FakeAudioLayer())])`, the
    fake recording the `SoundMoment` sequence: a first tap, a reselecting tap, a clearing tap
    and a tap on an illegal cell each append **nothing**; the confirming tap appends
    `SoundMoment.placeMark` exactly once. What else that same commit may append is requirements
    32–33.
16. **The confirm tap, not the select tap, ends the previous move's last-move highlight.** The
    opponent's last-move highlight persists through selecting and previewing, and clears only on
    confirmation, so `lastMove` changes on the second tap only. Rendering it is `P3-01`.
    *(Game Board Design → Last Move Highlight → Lifetime — "The highlight persists until your
    move is completed... only clears once you confirm".)*
    **Verification:** after a first tap and after a reselecting tap, `boardProvider.lastMove` is
    unchanged; after the confirming tap it equals the committed move (`P1-02` requirement 40).
17. **The turn passes immediately on commit.** No interstitial or "pass the phone" screen sits
    between the confirming tap and the opponent's turn. *(Menus and UI → Pass-and-Play Turn
    Handoff — "The game switches the active player automatically after each move", "The handoff
    can be instant"; Design Handoff → Interactions & behavior — "Turn handoff is instant";
    `P1-02` requirement 38, which flips `currentPlayer` inside `applyMove`.)*
    **Verification:** in the frame after the confirming tap settles, `boardProvider.currentPlayer`
    differs from its pre-tap value, `BoardView` is still the visible surface, and no route was
    pushed and no dialog, overlay or modal barrier entered the tree — the handoff adds nothing.
18. **Animations never block input.** Taps register normally while an animation plays, and the
    animation is neither interrupted nor skipped. *(Animations → Decisions → Animations don't
    block input; `P2-04-animations.md` requirement 15 — never block input — and requirement 16 —
    a tapped-through animation is neither interrupted nor skipped.)*
    **Verification:** a tap dispatched mid-animation produces the same state change as the same
    tap at rest.

### Where this lives

19. **The tap surface is `CellView`'s `GestureDetector`, and every cell always carries a live
    `onTap`.** `P3-01` requirement 44 builds it with `behavior: HitTestBehavior.opaque` and
    forwards to `BoardView.onCellTap(quadrant, cell)` **for every cell regardless of legality**.
    Both halves are load-bearing, and the second is the one that is easy to get wrong:
    - **`opaque`, not `deferToChild`** — a legal *empty* cell renders nothing (`P3-01`
      requirement 15), and under `deferToChild` a transparent child does not hit-test at all, so
      the board would be inert.
    - **`onTap` is never null.** `opaque` alone does **not** absorb the tap: it makes the box
      report a hit against widgets *behind* it, while **ancestors stay in the hit-test path
      regardless**. Absorption comes from winning the gesture arena, which requires a live
      `TapGestureRecognizer` — that is, a non-null `onTap`. So the natural idiom is a bug:

      ```dart
      // WRONG — satisfies "opaque" and still ships the defect requirement 10 forbids.
      // With onTap null there is no recognizer, requirement 26's clear surface wins the
      // arena, and a tap on a locked cell wipes the pending selection.
      GestureDetector(behavior: HitTestBehavior.opaque, onTap: isLegal ? _select : null)

      // RIGHT — the callback does not depend on legality at all. Requirement 25 decides
      // legality inside the notifier, so no branch here can produce null.
      GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: () => onCellTap(quadrant, cell),
      )
      ```

    **This is also what implements requirement 26's boundary.** A tap on a cell is absorbed by
    that cell's own recognizer and never reaches the clear surface; a tap that lands anywhere
    else — a gutter, the quadrant padding, the gap between quadrants — is claimed by no cell and
    falls through to it. The two requirements are one mechanism seen from either side, and
    neither may be "simplified" independently of the other.
    **Division of ownership:** `P3-01` requirement 44 owns those two arguments on `CellView` and
    now states both, including the nullable-`onTap` regression and its verification. This PRD
    owns the **callback it is given** — requirement 27's `onCellTap` wiring — and the standing
    constraint that `onCellTap` stays required and non-nullable and is never gated on state of
    its own.
    *(Tech Design → Decisions → How is the board rendered? — "81 `GestureDetector`s in nested
    `GridView`/`Column`s, not a `CustomPainter`"; `P3-01` requirements 15, 42 and 44; Game Board
    Design → Taps outside the legal quadrant and → Decisions → Does a tap outside the board
    clear a pending move?, the two behaviors this keeps apart.)*
    **Verification:** with a selection active and a spy installed on requirement 26's clear
    surface, a tap at the centre of an empty **legal** cell selects it and the spy records
    nothing; a tap at the centre of an empty **illegal** cell leaves the selection intact and
    the spy still records nothing; a tap just outside a cell's edge reaches the spy.
20. The **pending selection is UI state, not engine state**. It lives in `lib/state/` and is
    consumed by `lib/ui/board/`; the pure-Dart engine never learns about it. *(Tech Design →
    Decisions → Is the game logic separate from Flutter?; → State management — Riverpod; →
    Project structure — layer-first, whose `lib/` layer list this PRD adds nothing to; Design
    Handoff → State, which lists `pendingSelection` beside the game fields and marks it never
    persisted.)*
    **Verification:** a source scan finds no `PendingSelection` under `lib/engine/`, and
    `lib/engine/` imports nothing from `lib/state/`.
21. The pending selection is **never persisted**. Leaving a game and resuming it from the
    open-games list restores the board, the turn and the scoreboard, but no pending selection.
    *(Design Handoff → State — `pendingSelection // { quadrant, cell } | null (never
    persisted)`.)* **Caveat:** `Tech Design.md` annotates that state block as *"a design sketch,
    not a decision taken here"*, so this is sourced from the approved handoff rather than a
    Decisions entry — see `P1-02` OQ-3. It is forced independently twice over: by requirement 30
    (a selection is only valid against the board it was computed from, and a reload produces a
    different `Board`) and by `P2-01` requirement 20 (leaving the board is a navigation, and
    every navigation clears first), so nothing is ever alive to write.
    **Verification:** `PendingSelection` has no `toJson`/`fromJson` and is unreferenced under
    `lib/storage/`; after a save/restore round-trip through `P1-04-persistence.md` with a
    selection active before the save, the restored session has `pendingSelectionProvider == null`
    while board, `currentPlayer` and score match.
22. Committing applies the move **through the engine** — `Board applyMove(Board, Move)` returning
    new state — and the UI renders what comes back. The input layer never mutates board state.
    *(Tech Design → Decisions → Game state is immutable; `P1-02` requirements 3 and 33, which
    confirm this signature stays correct verbatim now that `Board` is the whole-game type.)*
    **Verification:** the pre-commit `Board` is unchanged afterwards and still equal to a fresh
    copy of its pre-move value; `boardProvider`'s new state is `identical()` to `applyMove`'s
    return value; a source scan of `lib/state/` and `lib/ui/board/` finds no `copyWith` on
    `Board` and no assignment to a `Board` field.

### The published interface

The artifact this PRD exists to produce is the pending selection `P3-01` requirement 23 draws.
Naming it here means no consumer invents it. Paths follow `Tech Design.md` → Decisions → Project
structure — layer-first; provider style follows → State management — Riverpod (plain
`Notifier`/`NotifierProvider`, no `@riverpod` codegen, no `StateNotifier`), enforced by `P1-01`
requirement 12.

23. **`PendingSelection` is the published type, and it reuses the engine's `Move`.** Its four
    fields are exactly what `P3-01` requirement 43's four pending parameters need — nothing on
    the board side is derived from the cell.

    ```dart
    // lib/state/pending_selection.dart
    import '../engine/board.dart';   // Move, PlacementState

    /// A move selected but not yet confirmed, with everything the board needs to draw the
    /// preview. Every field is read from the previewed post-move board (requirement 3).
    /// Never persisted (requirement 21).
    @freezed
    class PendingSelection with _$PendingSelection {
      const factory PendingSelection({
        /// The engine's own `Move` — `P1-02` requirement 30's `{quadrant, cell}` value
        /// type, with the equality `legalMoves.contains(...)` needs. No parallel type,
        /// so nothing converts between two shapes of one fact.
        required Move move,

        /// `applyMove(board, move).placementState`. **Consumers branch on this**, never on
        /// `destinationQuadrant == null` — the two null cases below are drawn differently.
        /// The discipline `P1-02` requirement 36 asks of every consumer.
        required PlacementState destinationState,

        /// `applyMove(board, move).activeQuadrant` — the post-move destination. Non-null
        /// only when `destinationState == forced`.
        required int? destinationQuadrant,

        /// The quadrants the opponent could play in if this move were confirmed — the
        /// **post-move** open set, which excludes a quadrant this move is about to claim.
        /// Non-empty **exactly** when `destinationState == freeChoice`, which is the
        /// invariant `P3-01` requirement 43 states from its side.
        required Set<int> freeChoiceQuadrants,
      }) = _PendingSelection;
    }
    ```

    `freezed` compares collection fields with `DeepCollectionEquality`, so two selections with
    equal sets are `==` — which is what keeps requirement 7's replace-and-compare assertions
    meaningful.
    *(`freezed` value types follow `Tech Design.md` → Decisions → Serialization and the storage
    layer and `P1-02` requirement 2 — minus `json_serializable`, which requirement 21 forbids
    here.)*
    **Verification:** two `PendingSelection`s with equal fields, including sets built
    separately, are `==`; the type has no `toJson`; and across the four cases of requirement 3's
    verification, `freeChoiceQuadrants.isNotEmpty` holds if and only if `destinationState ==
    PlacementState.freeChoice`.
24. **`pendingSelectionProvider` holds it and is the only writer.**

    ```dart
    // lib/state/pending_selection_provider.dart
    final class PendingSelectionNotifier extends Notifier<PendingSelection?> {
      @override
      PendingSelection? build() {
        ref.listen(boardProvider, (_, __) => state = null);   // requirement 30
        return null;
      }

      /// The only entry point the 81 cells call (requirement 27).
      /// Select / confirm / nothing — requirement 25.
      void tapCell(Move move) { /* requirement 25 */ }

      /// Requirement 26's clear, and the entry point `P2-01` requirement 20 calls before
      /// every router operation. Idempotent: clearing when nothing is pending is a no-op,
      /// which is what lets that caller be unconditional.
      void clear() => state = null;
    }

    final pendingSelectionProvider =
        NotifierProvider<PendingSelectionNotifier, PendingSelection?>(
      PendingSelectionNotifier.new,
    );
    ```

    `tapCell` and `clear` are the **entire** mutating surface, and `clear()` has exactly two
    callers: this PRD's clear surface and `P2-01`'s navigator. That PRD adds a caller, not a
    second owner.
    **Verification:** a source scan finds no `pendingSelectionProvider.notifier` outside
    `lib/state/`, `lib/ui/board/` and `lib/navigation/`, and no notifier member beyond `tapCell`
    and `clear`.
25. **`tapCell(Move move)` is a three-way branch, in this order**, against
    `ref.read(boardProvider)`:

    | Condition | Behavior |
    |---|---|
    | `!board.legalMoves.contains(move)` | **Nothing** — no state change, no haptic, no sound (requirement 10). |
    | `state?.move == move` | **Confirm** — requirement 29's commit path, then requirement 32's sounds and one `HapticService.validAction()`. |
    | otherwise | **Select or replace** — compute requirement 3's preview once, publish all four `PendingSelection` fields from it, then `HapticService.validAction()` (requirements 2, 3, 7, 14). |

    The illegal branch is checked **first**, so an illegal tap can never be read as a confirm
    even if a stale selection named it. `legalMoves` is empty exactly when the game is over
    (`P1-02` requirement 19), so requirement 13 needs no separate branch. **One `applyMove` per
    select** — the destination, the state and the free-choice set all come from that single
    previewed board, never from three separate calls or from the live board.
    **Verification:** one test per branch asserting state, haptic count and sound sequence; plus
    a fourth where `state?.move` names a cell that is no longer legal — that tap takes the first
    branch, not the second.
26. **Any tap that is not on a cell clears the pending selection.** This is the settled scope of
    requirement 8's "outside", and it is **one uniform rule**:

    > *"**Yes — any tap outside the nine quadrants clears a pending, unconfirmed selection.**
    > That includes the legend/how-to-play strip, the scoreboard, the settings button, and
    > opening any menu or sheet. One rule, uniformly applied."*
    > — `Game Board Design.md` → Decisions → **Does a tap outside the board clear a pending
    > move?**

    **The boundary is a widget, not a rectangle.** Stated in the terms `P3-01` requirement 44
    owns: **a tap absorbed by a `CellView` never clears; every other tap on the board screen
    does.** That is requirement 19's mechanism seen from the other side, and expressing it
    positionally instead would put two PRDs' pixel arithmetic in a race with each other.

    Two categories, with **different owners**:

    | Category | How the clear is reached | Owner |
    |---|---|---|
    | Taps no other recognizer claims — the 3pt cell gutters, the 5pt quadrant padding, the 8pt quadrant gaps, the 16pt board margins, the scoreboard strip, the non-interactive legend/hint strip (`P3-05` requirement 15) | they fall through to the board screen's clear surface, which calls `clear()` | **this PRD** |
    | Taps a control claims — the settings button, and anything else that opens a menu or sheet over the board, plus leaving the board by any route | the control wins the gesture arena, so no surface below it sees the tap; the **navigation** it triggers is what clears | **`P2-01` requirement 20** |

    The second row is why a tap-catching surface alone is not enough: a `GestureDetector`
    ancestor only sees taps no descendant recognizer claimed, so it would silently miss exactly
    the case the Decision names last — *"opening any menu or sheet"*. `P2-01` requirement 20
    closes it from the side that can: `GoRouterAppNavigator` calls
    `pendingSelectionProvider.notifier.clear()` **before every router operation,
    unconditionally**, so no operation added later can forget. That call cannot live here — the
    board layer would have to observe the router, and that PRD's requirement 1 forbids importing
    `go_router` outside `lib/navigation/`.

    **The gutters and padding are included on purpose — this is not an oversight to be "fixed"
    later.** An earlier round of this PRD flagged that a near-miss between two 35pt cells lands
    in a 3pt gutter and wipes the pending move, and that no requirement in any PRD reached those
    regions. That consequence was put to the user with the question, and the uniform rule was
    chosen with it in view: `Game Board Design.md` → Decisions records that *"a near-miss between
    two cells clears the selection rather than doing nothing. That is the accepted cost of the
    single uniform rule."* Anyone reading requirement 10 (an illegal *cell* tap does nothing)
    beside this one will notice the two differ by a few points of travel. That difference is
    deliberate, and it is tolerable because clearing costs one tap while a mis-commit costs a
    turn.

    **Verification:** with a selection active — a tap in a cell gutter, in the quadrant padding,
    in a quadrant gap, in the board's side margin, on the scoreboard, and on the legend strip
    each leave `pendingSelectionProvider` null, and `clear()` is invoked at most once per tap
    and never by a tap on any of the 81 cells, legal or not. The navigation half is asserted by
    `P2-01` requirement 20's own wave-3 test — a selection pending on `/game/abc` is null after
    each of `openQuickActions()`, `openSettings()`, `openThemeSelection()`,
    `exitGameToMainMenu()` and `playGame()`, and still null after `dismissCurrent()` returns.
27. **The board screen wires the two together**, and is the only place they meet. All four
    pending parameters come from one `PendingSelection`, so they cannot disagree:

    ```dart
    final pending = ref.watch(pendingSelectionProvider);

    BoardView(
      board: ref.watch(boardProvider),
      pendingSelection: pending?.move,                             // P3-01 req 43
      pendingDestinationState: pending?.destinationState,
      pendingDestinationQuadrant: pending?.destinationQuadrant,
      pendingFreeChoiceQuadrants: pending?.freeChoiceQuadrants,
      onCellTap: (q, c) => ref
          .read(pendingSelectionProvider.notifier)
          .tapCell(Move(quadrant: q, cell: c)),
    );
    ```

    `P3-01` requirement 23 branches on `pendingDestinationState` and draws the cell half from
    `pendingSelection`, the dashed ring from `pendingDestinationQuadrant`, and its **available**
    treatment across `pendingFreeChoiceQuadrants` — keyed `BoardKeys.quadrantPendingFreeChoice`,
    deliberately distinct from the `available` playability key so a mis-fired preview is
    distinguishable from genuine free choice.
    **Both earlier conflicts on this surface are resolved.** The pairing invariant is one-way
    (`pendingDestinationQuadrant != null` **implies** `pendingSelection != null`, not the
    converse), and the free-choice set that requirement 23's third row had no data source for is
    supplied here rather than recomputed there — the board must never substitute its own
    still-open quadrants, for the reason requirement 3 gives.
    **Verification:** a widget test drives a full select→confirm through `BoardView` with only
    the theme, haptic and audio providers overridden; a selection whose confirmation would claim
    its own send target renders with `cellPending` present, `quadrantPendingDestination` absent,
    and `quadrantPendingFreeChoice` present on exactly the previewed open quadrants and **not**
    on the quadrant being claimed; and a selection that would end the game renders the cell half
    with no big-board treatment of either kind.
28. **Nothing outside `lib/state/` calls `applyMove`.** Widgets request an intent; notifiers
    change state.
    **Verification:** a source scan finds `applyMove(` only under `lib/state/` and
    `lib/engine/`, never under `lib/ui/`.

### Commit safety and the pending selection's lifetime

29. **The confirming tap re-checks legality against the current board immediately before
    `applyMove`, and never catches `IllegalMoveError`.**

    ```dart
    // lib/state/board_provider.dart
    final class BoardNotifier extends Notifier<Board> {
      @override
      Board build() => Board.newSeries();          // P1-02 requirement 32

      /// The UI layer's only writer of board state.
      void commit(Move move) {
        final board = state;
        if (!board.legalMoves.contains(move)) return;   // the guard
        state = applyMove(board, move);                 // may throw; never caught
      }
    }

    final boardProvider = NotifierProvider<BoardNotifier, Board>(BoardNotifier.new);
    ```

    `Rules.md` → Decisions → **What happens if an illegal move reaches the engine?** settles that
    the engine **throws** — *"failing loud and throwing an error is correct when in theory the UI
    should never allow it to begin with"* — and `P1-02` requirement 42 raises `IllegalMoveError`
    with reason `notLegal` or `gameAlreadyFinished`. The guard is how the UI upholds the *"in
    theory"*; the absent `catch` is deliberate, because swallowing the error would turn a loud
    contract violation into a tap that silently did nothing — indistinguishable, from the
    player's side, from requirement 10, and invisible to the report `P1-06-crash-reporting.md`
    builds.
    **`boardProvider` is declared here for want of an owner, and flagged.** No PRD in the family
    names a game-state provider, yet `P3-01`, `P3-03-scoreboard-turn-indicator.md`,
    `P3-04-game-over-rematch.md` and `P1-04-persistence.md` all read or seed it. This PRD
    declares it because it is the only feature that *writes* the board; **seeding it from
    storage, `startNextGame()` on rematch, and open-game identity are not specified here** and
    belong to `P1-04` and `P3-04`. If either claims ownership, only the declaration moves — every
    requirement here is written against the name.
    **Verification:** a board whose `legalMoves` excludes the pending move takes the guard and
    calls `applyMove` zero times; a source scan of `lib/state/` and `lib/ui/board/` finds no
    `catch` of `IllegalMoveError` and no bare `catch` around an `applyMove` call.
30. **Any change to `boardProvider` clears the pending selection — and that covers board changes
    only.** The `ref.listen` in requirement 24 fires when the *board* changes, which delivers
    three things: requirement 9's clear-on-commit; invalidation when the board underneath a
    selection is **replaced** — a rematch's `startNextGame()`, a game loaded from the open-games
    list, any future undo; and the guarantee that a published `PendingSelection` was computed
    against exactly the board now in the provider. That last one is what makes requirement 3's
    preview trustworthy, and it now covers three published facts rather than one: a selection
    that outlived its board would show a stale destination **and** a stale free-choice set.

    **It is not the general clearing mechanism, and must not be read as one.** Opening a menu or
    a sheet changes no board state, and `P2-01` requirement 2's child-route structure never
    unmounts the game screen, so `pendingSelectionProvider` is never disposed either — this
    listener does not fire on any navigation, and a selection would survive one. That path is
    `P2-01` requirement 20's, which calls `clear()` before every router operation. The two
    mechanisms are disjoint by design: **board changes here, navigations there**, and requirement
    26's table is the map of which is which. This is recorded explicitly because the wrong
    assumption is easy to re-derive from this requirement's shape and was nearly missed once.

    *(**Derived, not stated** — no design doc discusses a pending selection outliving its board.
    It is forced by requirement 5, which lets a selection persist indefinitely with no time
    window, plus requirement 29's fail-loud contract: without it, a selection surviving a rematch
    meets a board where that move is illegal, and the only thing between that and an uncaught
    `IllegalMoveError` is the guard silently eating the player's tap. Marked derived in the house
    manner of `P2-02` requirement 2 and `P2-03` requirement 13; if another mechanism gives the
    same guarantee, this is negotiable.)*
    **Verification:** select a cell, replace the board via `startNextGame()` —
    `pendingSelectionProvider` is null with no tap; and a selection made before a rematch cannot
    be confirmed by a second tap on the same cell afterwards, it selects afresh. The negative is
    worth asserting too: with a selection pending, a rebuild that changes no board state leaves
    it intact.
31. **The preview is pure and is discarded.** Requirement 3's `applyMove` call produces a board
    that must never be written to `boardProvider`, persisted, or handed to another layer; only
    its `placementState`, `activeQuadrant` and `legalMoves` are read, and only the three derived
    values are published. The engine is immutable and side-effect-free (`Tech Design.md` →
    Decisions → Game state is immutable), so computing it changes nothing.
    **Verification:** after any number of first taps and reselections, `boardProvider` is
    `identical()` to its value before the first of them; and no previewed `Board` instance is
    reachable from any provider.

### Sounds the committed move causes

Assigned to this PRD as a coordination call. `P2-02-audio.md` carried `claimQuadrant` and
`catGame` as *"none — see Out of Scope"* in its requirement 6 table and correctly declined to
assign a caller itself, since *"a requirement here would specify another PRD's surface."* Its own
Out of Scope names the reasoning these two requirements act on: *"A claim and a cat game are
consequences of a committed move, detected by the engine and rendered by `P3-01`, with `P3-02`
owning the commit path."* Both are consequences of a commit; `P3-01` draws the claim veil and the
cat caption but never learns when a move lands. This PRD does, so it takes them.

32. **Sound fires on a commit for every moment that commit caused**, never on a preview. The
    select tap and the reselect tap stay silent (requirement 15); only confirmation makes sound.

    | Moment | Fires when the committed move… | `SoundMoment` |
    |---|---|---|
    | Placing a mark | …is applied at all (requirement 15) | `placeMark` |
    | Claiming a quadrant | …completes three in a row in its small board, so that quadrant becomes claimed | `claimQuadrant` |
    | Cat game | …fills the last empty cell of its small board with no winner, so that quadrant becomes a cat game | `catGame` |

    **Detection is a comparison of two published accessor values, not a rule.** `P1-02`
    requirement 41's `QuadrantState quadrantAt(int quadrant)` returns one of `{ open,
    claimedByPlayerOne, claimedByPlayerTwo, catGame }`; the commit path holds the board on both
    sides of `applyMove` and compares that one quadrant. **Only `move.quadrant` can have
    changed** — a move places one mark in one small board, so no other quadrant's status can
    move on that commit — which is what keeps this a single comparison rather than a scan.
    Requirement 11 is not breached: nothing here re-derives when a claim happens, it reads what
    the engine already decided.

    ```dart
    // lib/state/pending_selection_provider.dart — requirement 25's confirm branch
    final before = ref.read(boardProvider);
    ref.read(boardProvider.notifier).commit(move);          // requirement 29
    final after = ref.read(boardProvider);
    if (identical(before, after)) return;                   // the guard rejected it: silent

    final audio = ref.read(audioLayerProvider);             // P2-02 requirement 2
    audio.play(SoundMoment.placeMark);

    final was = before.quadrantAt(move.quadrant);           // P1-02 requirement 41
    final now = after.quadrantAt(move.quadrant);
    if (now != was) {
      audio.play(now == QuadrantState.catGame
          ? SoundMoment.catGame
          : SoundMoment.claimQuadrant);
    }
    ref.read(hapticServiceProvider).validAction();          // requirement 14 — once
    ```

    The `identical(before, after)` early return matters: requirement 29's guard can reject a
    stale move, and a commit that did not happen must make no sound, exactly as requirement 10
    requires of an illegal tap.
    *(`Theming.md` → What a Theme Controls → Audio, which lists *"Winning a small board /
    claiming a quadrant"* and *"Cat game"* among the five; `Animations.md` → Where Animations
    Fire, which names the same two as **moments**; `P2-02` requirements 2 and 6; `P1-02`
    requirements 22 and 41.)*
    **Verification** — in a widget test wrapped in
    `ProviderScope(overrides: [audioLayerProvider.overrideWithValue(FakeAudioLayer())])`:
    a commit that claims a quadrant records exactly `[placeMark, claimQuadrant]`; a commit that
    cat-games one records exactly `[placeMark, catGame]`; an ordinary commit records exactly
    `[placeMark]`; and a first tap, a reselect, a clear and an illegal tap record nothing.
    > ⚠ **`FakeAudioLayer`, not `RecordingOneShotSink`.** `P2-02` requirement 22 publishes both.
    > The fake **replaces the layer** and records which moments were *requested*, which is the
    > call-site fact this requirement owns. `RecordingOneShotSink` sits *below* the layer, after
    > the mute gate, and answers a different question — that PRD's requirement 16 carries a ⚠
    > note that asserting through the wrong one fails a correct implementation, and the likely
    > "repair" is moving the gate out to call sites, which breaks its requirement 2.
33. **One tap can legitimately produce three sounds, and that is not a defect.** The
    co-occurrence cases, stated because they are reachable in ordinary play and the answer is
    not obvious from any single PRD:

    - **Claim + game win.** A move that claims a quadrant can complete three claimed quadrants
      in a row. `P3-04-game-over-rematch.md` requirement 16 fires `winGame` on that same commit,
      bound to the ending **move**. So one confirming tap produces `placeMark`, `claimQuadrant`
      **and** `winGame` — three independent `play` calls from two PRDs' call sites.
    - **Cat game + game end.** A cat game can fill the last open quadrant and end the game as a
      draw. `P3-04` requirement 17 keeps a drawn game silent of `winGame`, so that tap produces
      `placeMark` and `catGame` only.
    - **Claim and cat are mutually exclusive on one move.** A small board either has a winner or
      is full with none; it cannot become both on the same commit. The `now != was` branch in
      requirement 32 is single-valued for that reason, not by choice.

    **What happens audibly is `P2-02`'s, not this PRD's.** Its requirement 24 records that
    `ThemedAudioLayer` *"has no concept of"* co-occurrence — *"the call site makes three
    independent `play` calls and the layer cannot tell them from three unrelated ones"* — and its
    overlap strategy is one player per moment, which its OQ-1 still fences. This requirement
    fixes only that the calls are made; whether three near-simultaneous sounds are pleasant is
    that PRD's open question and the user's.
    **Verification:** a commit that both claims a quadrant and wins the game records
    `placeMark`, `claimQuadrant` and `winGame` on the same `FakeAudioLayer`, in one tap, with no
    error and exactly one `validAction()` on the haptic fake.
    **Not carried across to motion.** `P2-04-animations.md` ships **only** `placeMark` as an
    animation moment in its wave, deliberately, *"so the questions the docs leave open about the
    other five are not answered by accident"* — its requirement 2 is still fenced on the
    marker-only-vs-quadrant question. Taking the audio moments here implies nothing about the
    animation ones, and no claim or cat animation is requested by this PRD. **This is the
    symmetric-looking next step to avoid**: the audio and motion channels have different open
    questions behind them, and firing an animation moment because the sound moment exists would
    answer one of them by accident.

### Tests

34. Every behavior above is covered by **widget tests** asserting taps do the right thing. **No
    golden image tests.** They run locally (`flutter test`); nothing runs them on a push. *(Tech
    Design → Decisions → Widget tests for the board — no golden tests — "Test that taps do the
    right thing and that the highlight states appear"; → CI — local builds only.)*
    Every requirement carries a verification that can be written against named symbols. The five
    that could not be written in earlier rounds are all closed: requirement 12's second set by
    `P3-01` requirement 45's `cellPlayable`, requirements 14–15's channel seams by `P2-03`
    requirement 15 and `P2-02` requirement 2, requirement 26's boundary by the tap-outside
    Decision plus `P2-01` requirement 20, and requirement 3's free-choice row by the
    self-claiming-preview Decision plus `P3-01`'s `quadrantPendingFreeChoice` key. **No
    verification in this PRD is blocked.**

## Out of Scope

Named so the boundary is explicit. Each is specified elsewhere; do not specify it here.

- **What any of it looks like** — the pending-cell ring, ghost mark, destination ring, the
  free-choice preview treatment, locked veil, claimed/cat overlays, the three highlights' mutual
  distinguishability, geometry, and the provisional turn banner ("Play here?" / "Tap again to
  lock it in") — `P3-01`. This PRD supplies the four pending values and the tap callback, and
  draws nothing. **Note the split on claims and cat games:** that PRD draws them, this one
  sounds them (requirement 32); neither owns both halves.
- **Explaining the gesture** — the hint text and on-board legend: `P3-05-how-to-play.md`. Its
  requirement 15 keeps that layer non-interactive, which is what puts a tap on it in requirement
  26's first category.
- **The haptic mechanism** — `HapticService`, the vibrate gate, the concrete platform call:
  `P2-03-haptics.md`. Requirement 14 says only *which taps count as valid*.
- **The audio mechanism** — `AudioLayer`, the theme sound slots, the mute gate, overlap policy
  and what a co-occurring trio sounds like: `P2-02-audio.md`. This PRD owns three call sites —
  `placeMark`, `claimQuadrant`, `catGame` — and nothing about playback. **`winGame` is
  `P3-04-game-over-rematch.md` requirement 16's** even though it can fire on a commit this PRD
  triggers; `buttonTap` belongs to the six control-owning PRDs its requirement 6 names.
- **Legal-move rules** — sending rule, dead quadrants, free choice, claiming, cat game, win and
  draw detection, `applyMove` semantics, `IllegalMoveError`: `P1-02-engine-rules.md`.
  Requirements 3 and 32 read `legalMoves`, `placementState`, `activeQuadrant` and `quadrantAt`,
  and decide nothing.
- **Seeding and resetting the game** — loading an open game into `boardProvider`, the rematch's
  `startNextGame()`, the 3-game cap, open-game identity, and deleting a game:
  `P1-04-persistence.md`, `P3-04-game-over-rematch.md` and `P4-02-open-games-list.md`.
  Requirement 29 declares the provider; it does not own the lifecycle.
- **Navigation, and the clear that rides on it** — routes, sheets, the router, and
  `GoRouterAppNavigator`'s unconditional `clear()` before every operation:
  `P2-01-navigation.md` requirement 20. Requirement 24 publishes the entry point it calls; this
  PRD observes no router and imports no `go_router`.
- **The settings button and the surfaces behind it** —
  `P3-03-scoreboard-turn-indicator.md`, `P4-04-settings.md`. Neither has to call anything here.
- **Animations** — `P2-04-animations.md`. Requirement 18 says only that input outranks them, and
  requirement 33 declines to request any moment beyond the `placeMark` that PRD ships.
- **Non-touch input.** The handoff specifies a focus/hover outline "on any pointer or keyboard
  platform", but no doc specifies keyboard or pointer activation semantics and the target is a
  portrait phone *(Tech Design → Decisions → Orientation — portrait only)*.
- **Anything from `Alternative Game Styles.md`.** Parking-lot doc; explicitly not the game being
  built.

## Open Questions

**OQ-1 — Answered and closed.** *What counts as "outside the full grid"?* Settled by the user
and recorded in `Game Board Design.md` → Decisions → **Does a tap outside the board clear a
pending move?** — *"any tap outside the nine quadrants clears a pending, unconfirmed
selection... including the legend/how-to-play strip, the scoreboard, the settings button, and
opening any menu or sheet. One rule, uniformly applied."* Requirement 26 carries it, in widget
terms rather than pixels, split across the two owners the mechanism actually has, together with
the cost the doc records as accepted: the 3pt cell gutters and 5pt quadrant padding are outside
the cells, so a near-miss between two cells clears rather than doing nothing. The same ruling
lands in `P3-05-how-to-play.md` requirement 15, `P2-01-navigation.md` requirement 20 and
`P4-04-settings.md`, so no PRD is deciding it for the others.

**OQ-2 — Answered and closed.** *What does the preview show when confirming would not send the
opponent to a single quadrant?* Settled by the user and recorded in `Game Board Design.md` →
Decisions → **What does the board preview when the selected move would claim its own send
target?**: *"**Every still-open quadrant is highlighted.** ... The preview shows the truth — the
opponent may play anywhere still open — rather than showing nothing."* The reasoning recorded
there is that it reuses the free-choice highlight that already exists for the state *after* such
a move lands, so preview and result look consistent, and it teaches the rule at the moment it
fires.

> **What each PRD carries.** Requirement 3 publishes `destinationState` and the **post-move**
> `freeChoiceQuadrants`; requirement 23 holds them; requirement 27 passes them. `P3-01`
> requirement 23 branches on the state across four rows and draws its **available** treatment
> across the previewed set, keyed `quadrantPendingFreeChoice` so a mis-fired preview is
> distinguishable from genuine free choice. The `gameOver` case draws no big-board treatment,
> which is a fenced answer rather than an accident of nullity.
>
> **The consistency this bought.** An earlier round noted that requirement 32 fires a sound on
> exactly the commits whose preview said nothing. Under this Decision the preview no longer says
> nothing — it lights every still-open quadrant — so both channels now mark the self-claiming
> move, which is the consistency the user was reaching for.

**OQ-3 — Are the preview visuals designed or not?** *Open; `P3-01`'s to resolve, and it changes
no requirement here.* The read-only handoff contradicts itself: *Interactions & behavior* says
*"Preview visuals still to be designed,"* while the same document's *Cell states* specifies the
pending selection precisely and screen *2d* draws all three highlights together. Neither
statement reaches this PRD's surface — requirement 27 passes values, and what they look like is
that PRD's, whose Open Questions flag the same contradiction.

**OQ-4 — Does a tap on a locked quadrant really give no feedback?** *Open as a wording question;
requirement 10 follows the explicit source.* `Game Board Design.md` → Taps outside the legal
quadrant and → Haptic Rule are explicit that it does not: *"The lack of a buzz *is* the
feedback."* `Menus and UI.md` → Vibrate on Touch justifies the buzz differently: *"A tap that
lands slightly off, or on a locked quadrant, is easy to misread as 'did that register?' A buzz
answers that question without the player having to look for a change."* Read one way they agree
(a buzz means it registered); read another, the second wants a locked tap acknowledged.
Requirement 10 follows `Game Board Design.md`, which is explicit and which the handoff repeats,
so nothing here is unbuildable — but the second doc's sentence is worth a look. Related and both
`P2-03`'s: its OQ-4 asks whether requirement 26's clear buzzes (requirement 14's counts encode
today's answer, "no") and its OQ-5 asks whether the app has any validity signal at all with
vibrate off.

**OQ-5 — Answered and closed.** *What does the engine do if handed an illegal move?* Settled in
`Rules.md` → Decisions → **What happens if an illegal move reaches the engine?**: *"**The engine
throws.**"* `P1-02` requirement 42 publishes `IllegalMoveError` with reasons `notLegal` and
`gameAlreadyFinished`. **Requirement 29 is this PRD's half** — the commit-time re-check and the
deliberate absence of a `catch`.

**OQ-6 — Answered and closed.** *A move that claims (or cat-games) the very quadrant it sends the
opponent to — which state does the send see?* Settled in `Rules.md` → Decisions → **Does a move
that claims its own send target still send there?**: *"**The send is evaluated against the board
after the claim.**"* **Requirement 3 was rewritten to match** — every previewed value is read
from the post-move board, the only formulation that cannot drift from `P1-02` requirement 17.
What the board then shows is OQ-2, now also closed.

**OQ-7 — Answered and closed.** *What does requirement 12's set-equality compare against?*
`P3-01` requirement 45 publishes **`BoardKeys.cellPlayable(q, c)`**, present exactly when
`board.legalMoves.contains(Move(quadrant: q, cell: c))` — rendered from the engine's own
membership, not re-derived, and per-cell, so it covers the occupied cell and the cell in a dead
quadrant that a quadrant-level key cannot express. Requirement 12 is anchored on it.

**OQ-8 — Answered and closed.** *Are the haptic and audio entry points substitutable in a widget
test?* Both siblings publish injectable seams and both name this question: `P2-03` requirement 15
(`HapticService.validAction()` behind `hapticServiceProvider`) and `P2-02` requirement 2
(`AudioLayer.play(SoundMoment)` behind `audioLayerProvider`), each overridable via
`ProviderScope(overrides: [...])`. Requirements 14, 15 and 32 are written against those symbols,
and requirement 14's reselection count is what `P2-03` requirement 3 now records as its
assertion.
