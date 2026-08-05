# PRD: Board Rendering

> **Status:** Draft · Source docs read: `Game Board Design.md`, `Tech Design.md`,
> `Theming.md`, `Rules.md`, `Game Overview.md`, `Animations.md`, `Menus and UI.md`,
> `roadmap.md`, plus the read-only reference asset `design_handoff_game_ui/`
> (`README.md`, `neon.theme.json`). `Alternative Game Styles.md` is a declared
> parking-lot doc and was read only to confirm it is out of scope — no requirement here
> comes from it.

> **Wave:** P2 · **Depends on:** `P1-01-app-scaffold.md` (the `lib/ui/board/` directory
> and the Riverpod root), `P1-02-engine-rules.md` (the state this renders — quadrant
> status, active quadrant, forced vs. free choice, last move), `P1-03-theme-system.md`
> (every value drawn here comes from a theme slot).
> **Depended on by:** `P2-02-move-input.md` (drives the pending selection this draws),
> `P2-03-scoreboard-turn-indicator.md` and `P2-04-game-over-rematch.md` (sit above and
> over this board), `P4-03-animations.md` (animates these highlights).
> Within a wave, work is parallel-safe; a lower wave ships first.

> **Note on source status:** `Game Board Design.md` carries the house banner *"Nothing
> here is settled"* and has **no `## Decisions` section at all** — the roadmap records
> this. It is nonetheless the only specification of the board's visual design, its **Open
> Questions** section is empty (*"Nothing outstanding on this doc right now"*), the
> approved handoff was built from it, and `Tech Design.md` → What the Design Docs Already
> Imply treats its body as already locked (*"Portrait phone layout, whole 9x9 board
> visible, no zoom"*). This PRD therefore treats the body of `Game Board Design.md` as
> settled. Where that doc hedges — *"probably* a big X or O", *"dimmed, desaturated,
> greyed, receded, **something**"*, free choice *"**may** want a calmer treatment"* — the
> approved handoff is what turns the hedge into a concrete answer, and the requirement
> cites both. See Open Questions for what that leaves unresolved.

---

## Problem

There is no board. The game's entire readability rests on one screen that has to answer
two questions the moment the phone changes hands — *what changed, and what can I do?* —
across 81 cells, and `Game Board Design.md` → Last Move Highlight names why that is
harder here than in normal tic-tac-toe: a single small mark in a 9x9 field is genuinely
easy to miss, and in pass-and-play you were not watching when it was made.

Three highlights have to coexist on that screen at once — the opponent's committed last
move, the quadrant you are allowed to play in, and your own not-yet-committed selection —
and if any two of them look alike they create exactly the confusion they exist to
prevent. Alongside them the board has to say which quadrants are dead, which are claimed
and by whom, and which are simply off limits this turn. That last one is what
`Game Board Design.md` calls *"the easy one to under-build"*: highlighting the legal
quadrant alone leaves the other eight looking normal and tappable, and since an illegal
tap produces no shake, no flash, no message and no haptic, the dimming has to prevent the
tap because nothing will explain it afterwards.

## Goal

A single board widget under `lib/ui/board/` renders the 3x3-of-3x3 grid, its 81 cells,
and every quadrant and cell state the game can be in, driven entirely by state read from
the rules engine and styled entirely from the active theme. Every one of the three
simultaneous highlights is drawn so that it cannot be mistaken for either of the other
two; locked, claimed and cat-game quadrants each read as unplayable and as distinct from
one another; the whole 9x9 stays visible in portrait with no zoom; and every state is
legible with animations switched off. The board draws state — it computes no rules,
handles no gesture, and holds no hardcoded value.

## Requirements

### Structure and geometry

1. The board is a 3x3 grid of quadrants, each holding its own full 3x3 small board — **81
   playable cells**, with depth **fixed at exactly two levels** (big board → small board)
   and no deeper nesting.
   *(`Game Board Design.md` → Board Structure; `Game Overview.md` → Decisions → Recursion
   depth; `Rules.md` → Setup)*
   **Testable:** the rendered tree contains 9 quadrant widgets, each containing exactly 9
   cell widgets, and nothing nests a board inside a cell.

2. The board is **one component, driven entirely by per-quadrant state** — the same
   component renders every screen state, rather than there being a "free choice board"
   and a "forced board."
   *(`design_handoff_game_ui/README.md` → The board (the important part))*

3. **Board geometry**, as approved: big board a 3x3 grid with gap 8; quadrant padding 5,
   radius 9, fill `rgba(18,20,32,0.60)`; cells a 3x3 grid with gap 3, square, and
   **transparent — no cell fill**; grid lines drawn as an overlay inset 5, i.e. inside the
   quadrant's padding box.
   *(`design_handoff_game_ui/README.md` → Geometry; `neon.theme.json` → `board`,
   `radius`)*

4. At the approved **402pt frame with 16pt side padding the board is 370pt, a quadrant
   ≈118pt and a cell ≈35pt**. That is below Apple's 44pt target and is accepted, because
   the two-tap select-then-confirm interaction makes a mis-tap free. These numbers are the
   approved visual source of truth and are not re-decided here.
   *(`design_handoff_game_ui/README.md` → Geometry; `Game Board Design.md` → Responsive /
   Screen Size, whose closing paragraph adopts exactly these numbers)*

5. **Small-board grid lines are drawn lines, not gaps, and must not touch the quadrant
   border**: 2 vertical lines at 33.33% and 66.67% of the quadrant's inner box, each
   1.5pt wide, running from 9% to 91% of the height; 2 horizontal lines the same but
   transposed; colored `boardLine` at 0.75 opacity with glow `0 0 7px
   rgba(79,195,255,0.90)`.
   *(`design_handoff_game_ui/README.md` → Grid lines — read this carefully;
   `Game Board Design.md` → Board Structure, which restates this)*
   **Testable:** no cell widget carries a border of its own, and the drawn lines stop
   short of the quadrant's edge on all four sides.

6. The **quadrant border** is the same blue at full presence: `0 0 0 1.5px
   rgba(79,195,255,0.5)`, outer glow `0 0 14px rgba(79,195,255,0.16)`, inner glow `inset 0
   0 12px rgba(79,195,255,0.06)`.
   *(`design_handoff_game_ui/README.md` → Grid lines — read this carefully;
   `neon.theme.json` → `board.quadrantShadow`)*

7. The **big board must read heavier than the small boards** — the nesting has to stay
   readable at a glance. That hierarchy is carried by **weight, glow and the inset**, not
   by two different colors: both grids are the same blue, and the 9%–91% inset is what
   keeps them visually separate.
   *(`Game Board Design.md` → Visual Layout, Board Structure;
   `design_handoff_game_ui/README.md` → Grid lines — read this carefully)*

### Quadrant states

8. **Open** (playable, free-choice mode): the border brightens to `rgba(79,195,255,0.85)`
   with glow `0 0 20px rgba(79,195,255,0.35)`.
   *(`design_handoff_game_ui/README.md` → Quadrant states; screen 1d, where all nine
   quadrants are in this state)*

9. **Forced** (the one legal quadrant): a 2pt `highlightForced` ring, offset −3, radius
   12, glow `0 0 20px 5px rgba(181,124,255,0.6)` plus `inset 0 0 16px
   rgba(181,124,255,0.3)`.
   *(`design_handoff_game_ui/README.md` → Quadrant states; screen 1e)*

10. **Locked** (illegal this turn): a veil of `rgba(15,16,26,0.50)` — **dimmed but still
    readable, deliberately not blacked out**. This is half the rule and the half that is
    easy to under-build: the other eight quadrants must not look normal and tappable, and
    because an illegal tap produces no shake, no flash, no error message and **no haptic**,
    the dimming is what has to prevent the tap. The absence of the buzz is the only
    feedback there is.
    *(`Game Board Design.md` → Active Quadrant Highlight (job 2) and → Taps outside the
    legal quadrant; `design_handoff_game_ui/README.md` → Quadrant states, Interactions &
    behavior)*
    **Testable:** marks inside a locked quadrant remain legible under the veil.

11. **Claimed**: veil `0.76` plus a centered claim mark over the whole quadrant — P1 ✕ at
    56pt `playerOneMark` with glow `0 0 26px rgba(255,61,113,0.95)`, P2 ○ at 52pt
    `playerTwoMark` with glow `0 0 26px rgba(45,255,158,0.90)`.
    *(`Game Board Design.md` → Player Feedback / Affordances, which asks for "a big X or O
    overlaid on the whole quadrant"; `design_handoff_game_ui/README.md` → Quadrant states;
    `neon.theme.json` → `type.scale.markClaimX` / `markClaimO`)*

12. **Cat game** (dead): veil `0.76` plus a centered Ø at 44pt `catGame` with glow `0 0
    22px rgba(154,162,194,0.75)` and an 8pt `CAT` label beneath it. It must be **visually
    distinct from claimed and from in-play** — it is permanently dead and neither player
    can ever have it.
    *(`Game Board Design.md` → Player Feedback / Affordances;
    `design_handoff_game_ui/README.md` → Quadrant states; `neon.theme.json` →
    `marks.catGame`, `type.scale.markCat`)*

13. Claimed and cat quadrants deliberately share the **same overlay language** — all three
    finished states read as "finished," and it is the glyph and its color that say whose
    it is, or that it belongs to nobody. Distinctness between claimed and cat is carried
    by glyph and color, not by a different veil.
    *(`design_handoff_game_ui/README.md` → Quadrant states, closing note)*

14. Which state a quadrant is in is **derived, not authored**: a quadrant is **forced**
    when it is the active quadrant; **open** when there is no active quadrant and the
    quadrant is still unclaimed and not a cat game; **locked** otherwise.
    *(`design_handoff_game_ui/README.md` → State → "Derived for rendering"; the underlying
    game state comes from `P1-02-engine-rules.md`, whose requirement 18 exposes forced vs.
    free choice as engine state the UI reads rather than infers)*

### Cell states

15. An **empty cell renders nothing** — it is transparent, with no fill and no border.
    *(`design_handoff_game_ui/README.md` → Cell states, Geometry)*

16. A **played cell renders its player's mark** at 19/600 in that player's mark color with
    its glow pair — P1 `#ff5c85`, P2 `#4dffb0`.
    *(`design_handoff_game_ui/README.md` → Cell states; `neon.theme.json` →
    `type.scale.mark`)*

17. Marks are **theme-supplied asset slots — an image or an icon — not shapes drawn in
    board code**, and are not locked to X and O. Neon's ✕ and ○ are Neon's choice of art,
    not a constraint on the board.
    *(`Tech Design.md` → Decisions → Marks — image or icon, supplied by the theme;
    `Game Board Design.md` → Pieces & Marks; `Theming.md` → Decisions → Marks beyond X and
    O; the slots themselves are `P1-03-theme-system.md`)*

### The three highlights

18. **All three highlights can be on screen at once, and all three must be visually
    distinguishable.** They differ in scope, which is part of how they are told apart:

    | Highlight | Scope | Meaning |
    |---|---|---|
    | Opponent's last move | one cell | what just happened |
    | Active quadrant | one quadrant | where you're allowed to play |
    | Pending-move preview | one cell + one destination quadrant | where you'd send them |

    *(`Game Board Design.md` → Three highlights on screen at once; The Two Highlights
    Together; `design_handoff_game_ui/README.md` → Cell states, screen 2d)*

19. **Opponent's last move** — one cell, committed, and **exaggerated so it is readable at
    a quick glance**: the player must not have to hunt across 81 cells to find what
    changed. Drawn as a 2pt **solid** `highlightLastMove` ring, offset −1, radius 5, glow
    `0 0 14px 3px rgba(181,171,252,0.90)` plus `inset 0 0 8px rgba(181,171,252,0.4)`.
    *(`Game Board Design.md` → Last Move Highlight; `design_handoff_game_ui/README.md` →
    Cell states)*

20. **Last-move lifetime: the highlight persists until your move is confirmed.** It stays
    visible the entire time you are deciding — through selecting a cell and previewing
    where it sends your opponent — and only clears once you confirm. It is reference
    material while you think, not a notification that flashes and disappears, so it can be
    compared side by side against your pending selection.
    *(`Game Board Design.md` → Last Move Highlight → Lifetime)*
    **Testable:** the ring is still drawn on the opponent's cell after a pending selection
    is made and after it is changed to a different cell; it moves only when a move is
    committed.

21. The **active-quadrant highlight has two modes**, and the board must render both:

    | Mode | What's highlighted |
    |---|---|
    | **Forced** | Exactly one quadrant (requirement 9) |
    | **Free choice** | *Every* still-open quadrant — up to 9 (requirement 8) |

    Free choice also covers the opening move. Nine forced rings at once would look like
    noise, so free choice takes the calmer **open** treatment rather than nine copies of
    the forced ring.
    *(`Game Board Design.md` → Active Quadrant Highlight → The free-choice state, which
    floats the calmer treatment as a "may want"; resolved concretely by
    `design_handoff_game_ui/README.md` → Quadrant states and screen 1d)*

22. In free choice, **claimed and cat-game quadrants still read as locked**. It is "pick
    any of these open ones," not "the board is unlocked."
    *(`Game Board Design.md` → Active Quadrant Highlight → The free-choice state)*

23. **Pending-move preview** — it marks a cell *and* a quadrant simultaneously, and
    **both must read as provisional**, clearly not yet committed and clearly distinct from
    the committed last-move highlight:
    - the selected cell: 2pt **dashed** `highlightPending` at 85%, offset −1, radius 5,
      plus a **ghost mark in the current player's color at 40% opacity**;
    - the destination quadrant: 2pt **dashed** `highlightPending` at 80%, offset −3,
      radius 12, over a `rgba(233,233,237,0.05)` wash.

    *(`Game Board Design.md` → Three highlights on screen at once;
    `design_handoff_game_ui/README.md` → Cell states and its following paragraph, screen
    2d)*

24. The three are separated **by weight, not by color**: **dashed = provisional, solid =
    committed**. Last move is a solid lavender ring, the active quadrant a solid purple
    glowing ring, the pending move dashed white with a ghost mark. Purple is reserved for
    the two gameplay-critical highlights and nothing else, so "where they played" and
    "where you must play" never compete with the board lines or the marks.
    *(`design_handoff_game_ui/README.md` → Cell states (the three-highlight table), Design
    tokens → Color logic; `Game Board Design.md` → The Two Highlights Together)*

25. **Z-order inside a quadrant is fixed**: cells 0 → grid lines 1 → veils / claim / cat
    overlays 2 → forced ring and destination ring 3 → **last-move ring and pending ring
    4**. The last-move ring sits **above the locked veil** on purpose, so a mark in a
    now-locked quadrant still reads at a glance — which is the whole point of the
    highlight.
    *(`design_handoff_game_ui/README.md` → Cell states → Z-order; screen 1e, where the
    last-move ring sits in the locked quadrant q8)*
    **Testable:** a last move played in a quadrant that is locked on the following turn is
    still drawn at full strength, not dimmed by the veil.

26. The board wrapper establishes its **own stacking context**, because the claim and veil
    overlays are stacked — otherwise a sheet drawn over the board cannot reliably sit above
    them.
    *(`design_handoff_game_ui/README.md` → 1f, which notes this explicitly; the sheet
    itself is `P2-04`/`P3-04` territory, not this PRD's)*

### Everything here is theme-driven

27. **Every treatment in this PRD is theme-driven.** This document specifies *what must be
    communicated*; the theme decides *what it looks like*. Grid line colors, backgrounds,
    mark styling, the three highlights, locked / claimed / cat-game treatments — all of it
    is read from the active theme, and **board code contains no hardcoded color,
    background, font, piece style, size or duration**.
    *(`Game Board Design.md` → Everything Here Is Theme-Driven; `Theming.md` →
    Architectural Rule; enforced by `P1-05-theme-guard-test.md`)*
    **Testable:** the hardcoded-theme-value scan finds no violation in `lib/ui/board/`.

28. The concrete values quoted throughout this PRD are **Neon's**, and they live in the
    theme file, not in board code — including the board's geometry, which
    `neon.theme.json` carries under `board` (`outerGap`, `quadrantPadding`, `innerGap`,
    `gridLineWidth`, `gridLineInsetPercent`, the quadrant shadows, the forced ring and the
    last-move ring) and `radius` (`cell`, `quadrant`).
    *(`neon.theme.json`; `design_handoff_game_ui/README.md` → Design tokens; the slots are
    `P1-03-theme-system.md`)*

29. The board must have separately addressable theme slots for the **last-move highlight,
    the active-quadrant highlight, the locked/inactive styling, the pending-move preview,
    claimed-quadrant styling and cat-game quadrant styling** — because up to three of them
    are on screen simultaneously and must not collapse into one another.
    *(`Theming.md` → What a Theme Controls → Visual; `Game Board Design.md` → Player
    Feedback / Affordances)*

30. **Legibility is a contract on every theme, not just Neon.** The last-move and
    active-quadrant highlights are *gameplay-critical, not decoration* — "a pretty theme
    that hides the last move is a broken theme" — and these treatments must coexist on one
    screen without turning into visual noise, in every theme.
    *(`Theming.md` → What a Theme Controls; `Game Board Design.md` → Player Feedback /
    Affordances, closing note)*

31. **The board is fully readable with animations switched off.** No state in this PRD may
    depend on motion to be understood; with animations off the game simply shows the new
    state, with no substitute effect.
    *(`Animations.md` → Decisions → Animations off = instant state change;
    `design_handoff_game_ui/README.md` → Interactions & behavior → "Every screen above is
    fully readable with animation off — that is the correctness test")*

### How it is rendered

32. **The board is rendered with widgets, not a `CustomPainter`.** 81 `GestureDetector`s
    in nested `GridView`/`Column`s. *"ok widgets is the winner lets make that happen."*
    *(`Tech Design.md` → Decisions → How is the board rendered?)*

33. **Watch out for the documented hazards:** nested `Border.all` **doubles interior grid
    lines** — two adjacent 1px borders read as 2px — and hairlines can look uneven at
    fractional device pixel ratios. Requirement 5 already forbids per-cell borders; this
    records why.
    *(`Tech Design.md` → Decisions → How is the board rendered? → "Watch out for")*

34. The hybrid — widgets for cells and marks plus **one thin `CustomPaint` overlay drawing
    only the grid lines** — is recorded as the known fix and is **an escape hatch, not a
    decision taken**. It is not adopted by this PRD. If the implementation reaches for it,
    that is a decision to raise deliberately, not to drift into.
    *(`Tech Design.md` → Decisions → How is the board rendered?)* See Open Questions,
    which flags why requirement 5's geometry puts pressure on this.

35. The board **renders engine state and computes no rules**. Legal-move computation, the
    sending rule, claim and cat-game detection and the free-choice state all come from
    `P1-02-engine-rules.md`; the board reads them.
    *(`Tech Design.md` → Decisions → Is the game logic separate from Flutter?;
    `P1-02-engine-rules.md` → Out of Scope)*

### Layout

36. **Portrait only.** No landscape.
    *(`Tech Design.md` → Decisions → Orientation — portrait only)*

37. **The whole 9x9 grid stays visible at all times. No zoom**, and no scrolling to reach
    part of the board — seeing the whole board at once is what lets a player reason about
    where their move sends the opponent. Small tap targets are the accepted cost, carried
    by the two-tap confirm rather than by zoom.
    *(`Game Board Design.md` → Responsive / Screen Size; `Tech Design.md` → What the
    Design Docs Already Imply)*

38. The board sits in a **vertical stack below the scoreboard**, with 16pt horizontal
    padding on board screens.
    *(`Game Board Design.md` → Visual Layout; `design_handoff_game_ui/README.md` →
    Spacing, screens 1d/1e)*

### Tests

39. The board is covered by **widget tests, with no golden image tests** — tests that
    assert the highlight states appear.
    *(`Tech Design.md` → Decisions → Widget tests for the board — no golden tests)*

40. Because there are no goldens, **each visual state must be addressable in the widget
    tree** — a keyed or typed widget per quadrant state (open, forced, locked, claimed-P1,
    claimed-P2, cat) and per cell state (empty, P1, P2, last move, pending) — so a test can
    assert its presence without comparing pixels. This is what requirement 39's decision
    requires in practice.
    *(`Tech Design.md` → Decisions → Widget tests for the board — no golden tests)*

41. Tests **run locally** via `flutter test`. There is no CI; nothing runs them on a push.
    *(`Tech Design.md` → Decisions → CI — local builds only)*

## Out of Scope

Named here so the boundary is explicit. Each is specified elsewhere; do not specify it
here.

- **The two-tap gesture and all input handling** — select, confirm, reselect, tap-outside
  to clear, illegal taps doing nothing, and the haptic on every valid click:
  `P2-02-move-input.md`. This PRD draws the pending selection; it does not produce or
  manage it. Focus/hover styling on pointer and keyboard platforms
  (`design_handoff_game_ui/README.md` → Interactions & behavior) is input-state styling and
  belongs there too.
- **The scoreboard, the turn indicator and the turn banner above the board** —
  including the banner's mode cue ("Free choice — pick any board", "Play the middle
  board", "Play here? / Tap again to lock it in"): `P2-03-scoreboard-turn-indicator.md`.
  Note that `Game Board Design.md` → The free-choice state offers a text cue as an
  *alternative* to a calmer highlight; the handoff provides both, and only the highlight
  half is this PRD's (requirement 21).
- **Game-over presentation** — the winner and draw modals, the finished board dimmed
  behind them, and rematch: `P2-04-game-over-rematch.md`.
- **The theme mechanism** — the theme object, its slots, YAML loading, merge-over-Neon and
  the Neon definition itself: `P1-03-theme-system.md`. This PRD says which slots the board
  reads, not how they are loaded.
- **Legal-move computation and all rules** — the sending rule, claims, cat game, free
  choice, win and draw detection: `P1-02-engine-rules.md`.
- **Animation of the highlights** — the looping glow-pulse on the active quadrant and the
  last move, one-at-a-time sequencing, non-blocking input, and the animations-off path:
  `P4-03-animations.md`. Requirement 31 only fixes that the board must be readable without
  any of it.
- **Sound** — the pending selection deliberately has no sound of its own
  (`Game Board Design.md` → Move Input → Sound); audio playback is `P4-01-audio.md`.
- **Anything from `Alternative Game Styles.md`** — a declared parking-lot doc, explicitly
  not the game being built.

## Open Questions

### From the design docs — unresolved, worded as the docs word them

`Game Board Design.md` → Open Questions is empty (*"Nothing outstanding on this doc right
now"*), and no Open Question in `Tech Design.md` lands on rendering. The one adjacent open
item:

- **Which values, concretely, does Classic Red vs Blue override?** *(`Theming.md` → Open
  Questions.)* Owned by `P4-04-classic-theme.md`, listed here because the second theme is
  the first real test of requirement 30 — the board's highlights have to stay legible
  under a theme that is not Neon.

### Contradictions and gaps between documents — flagged, not resolved

- **The approved grid-line geometry sits awkwardly with the "widgets, not
  `CustomPainter`" decision.** Requirement 5's lines are drawn *inside* the quadrant, run
  from 9% to 91%, and must not touch the border — they are not cell borders and cannot be
  produced by nested `Border.all`, which is the very construct `Tech Design.md` warns
  about. Some overlay is therefore required, and `Tech Design.md` → Decisions → How is the
  board rendered? records the thin `CustomPaint` grid-line overlay as *"an escape hatch,
  not a decision taken."* Whether that overlay is built from widgets (a `Stack` of thin
  positioned boxes) or the escape hatch is taken after all is not settled anywhere, and
  requirement 34 deliberately does not settle it.
- **The handoff contradicts itself on the pending-move preview.**
  `design_handoff_game_ui/README.md` → Interactions & behavior says *"Preview visuals still
  to be designed"*, while the same document's *Cell states* section and screen *2d* specify
  them exactly — dashed ring, ghost mark, dashed destination quadrant, all with concrete
  values. This PRD builds from the specified version (requirement 23) on the grounds that
  2d exists and the Fidelity section calls the drawn values final, but the sentence should
  probably go.
- **`Game Board Design.md` has no `## Decisions` section**, despite being the sole source
  for an entire feature and despite the house style requiring one. Several of its
  statements are hedged (*"probably* a big X or O", *"dimmed, desaturated, greyed,
  receded, **something**"*, free choice *"**may** want a calmer treatment"*) and are
  settled here only because the approved handoff drew a concrete answer. If the intent is
  that the handoff's answers *are* the decisions, that doc should say so under Decisions.

### Raised by this PRD — not discussed in any design doc, and flagged rather than answered

Each is a place an implementer would otherwise have to guess.

- **How do quadrant states compose when more than one applies?** The handoff's derived
  rule (requirement 14) makes a claimed or cat quadrant **locked** in free-choice mode,
  while the *Quadrant states* table gives claimed and cat their own `0.76` veil and locked
  a `0.50` veil. Whether the veils stack, whether the stronger one wins, or whether
  claimed/cat simply subsume locked is unstated. The same question applies to whether a
  **forced** quadrant also takes the brightened "open" border or keeps the base one.
- **What happens at frame widths other than 402pt?** Every number in requirement 4 is
  committed at a 402pt frame. iPhone SE is 375pt, Pro Max is 430pt, and iPad is the
  declared second target *(`Tech Design.md` → Decisions → Device support)*. Whether the
  board scales proportionally, holds fixed point values and re-centers, or caps at a
  maximum width is not stated — and if it scales, whether the mark sizes (19 / 56 / 52 /
  44pt) scale with it. Dynamic Type is off *(`Menus and UI.md` → Decisions → Do we support
  Dynamic Type?)*, so nothing else moves these numbers.
- **What does the board render once the game is over?** The engine reports the game as
  won or tied and no further moves are legal *(`P1-02-engine-rules.md` → requirements
  20–22)*, but nothing says whether the active-quadrant highlight, the last-move ring and
  the locked veils persist, all clear, or the whole board goes to a single finished state
  underneath the result modal. The handoff only says the finished board stays visible at
  60% behind the scrim.
- **Who owns the on-screen legend and hint text?** Screen 1d pins a legend to the bottom
  (Open · Locked · Cat game) plus hint text *"Tap a square to see where it sends them. /
  Tap it again to play it."*, and 1e's legend explains both rings in words. These explain
  board state, so they may belong here; they are screen chrome below the board, so they
  may belong with the board screen or `P2-03`. No PRD currently claims them, so as things
  stand they would simply not get built.
- **Is the ghost mark a distinct theme slot or the player's mark at 40% opacity?**
  Requirement 23 says "a ghost mark in the current player's color at 40% opacity", and
  marks are images or icons supplied by the theme (requirement 17). Dropping an icon to
  40% is trivial; a theme wanting distinct ghost art would need its own slot in
  `P1-03-theme-system.md`. Not settled either way.
