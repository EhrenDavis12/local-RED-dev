**Build-readiness: 90**

# PRD: Board Rendering and the Game Screen

> **Status:** Draft · Source docs read: `Game Board Design.md`, `Tech Design.md`,
> `Theming.md`, `Rules.md`, `Game Overview.md`, `Animations.md`, `Menus and UI.md`,
> `roadmap.md`, plus the read-only reference asset `design_handoff_game_ui/`
> (`README.md`, `neon.theme.json`). `Alternative Game Styles.md` is a declared
> parking-lot doc and was read only to confirm it is out of scope — no requirement here
> comes from it.
>
> **Revised for build-readiness.** Requirement 28 is a **key-path table**, one row per
> requirement. Requirements 42–45 publish the widget surface. Requirement 14's derivation
> is gated on `placementState`. Requirements 14, 17, 34 and 43 carry reversible author
> judgments in place of guesses.
>
> **Revised again** against `P3-02`'s landed interface (requirement 43's one-way invariant,
> requirement 44's non-nullable `onCellTap`), then for the free-choice-cue Decision (the
> turn banner is not built), then for two more Decisions — the self-claiming preview
> (requirement 23's third row) and spacing-is-code (requirement 28's constants column).
>
> **Revised again to take ownership of `GameScreen`** — requirements 46–53. Four PRDs
> asserted against a widget none of them built. It is accepted here rather than deflected;
> see *On accepting `GameScreen`* below for why this file and not another.
>
> **Revised again** to fix two defects in that new work: requirement 51's clear surface
> now names `HitTestBehavior.opaque` — the default `deferToChild` would have silently
> narrowed *"every other tap clears"* to *"every tap that lands on painted pixels"* — and
> requirement 53 takes ownership of the three scoreboard label strings, which `P3-03`
> requirement 11 forbids in its own file and no PRD had claimed.
>
> **Revised again for the defect that made `GameScreen`'s only parameter dead code.**
> **Requirement 54** is new: the screen loads the stored game its `GameId` names and seeds
> `boardProvider` from it. Without it, `boardProvider`'s `build()` returns
> `Board.newSeries()` and **resuming a saved game silently renders a new one** — a full,
> legal, empty board that looks exactly like a correct new game. Requirement 46's stateless
> fence is reversed by it, as that requirement said it might be, and requirement 48 gains a
> precondition. The settlement also routed the missing artifact both sides needed — a
> provider holding the on-screen game's identity — to `P3-02` requirement 35, which is where
> its only *reader* lives.
>
> **Why 90:** every value this PRD draws is a published theme key or a named code constant,
> the widget surface is named, the screen four PRDs assert against exists and now actually
> shows the game it was asked for, and both hit-test behaviours on the screen are explicit
> rather than defaulted. It is two points below the previous estimate rather than above it
> because requirement 54 is new territory that opens two questions of its own — **what the
> screen does when `readById` returns null, and what it does when the read throws** — where
> before it opened none by doing nothing at all. That is an honest trade: a stated gap in a
> requirement that exists beats no gap in a requirement that was missing. The same three
> user decisions remain, two of them visual defects that fire on ordinary play.
> Author's estimate, pending re-grade.

> **Wave:** P3 · **Depends on:** `P1-01-app-scaffold.md` (creates `lib/ui/board/` and the
> `ProviderScope`), `P1-02-engine-rules.md` (the state this renders — bound by symbol in
> requirements 43 and 48), `P1-03-theme-system.md` (every themed value here is a Requirement
> 15 key — bound by key path in requirement 28), `P1-04-persistence.md` (its req 21's
> `OpenGamesRepository.readById`, `StoredGame` and its req 22's `GameId` — read by
> requirement 54), `P2-01-navigation.md` (its req 2 route table constructs `GameScreen`; its
> req 4 `appNavigatorProvider` is read by requirement 49), `P2-04-animations.md` (owns all
> motion; requirement 31 here is the board-side half of its requirement 21).
> **Depended on by:** `P3-02-move-input.md` (its req 19 taps the cell surface of requirement
> 44; its req 26 clear surface is hosted by requirement 51; its OQ-7 is answered by
> requirement 45; its req 36 save depends on requirement 54 having seeded `currentGameProvider`),
> `P3-03-scoreboard-turn-indicator.md` (its `ScoreboardStrip` is composed by
> requirement 47 and fed by requirements 48, 49 and 53), `P3-04-game-over-rematch.md` (its
> result card is hosted by requirement 52), `P3-05-how-to-play.md` (its strip is composed by
> requirement 47 and its legend swatches read the same theme keys).
> Within a wave, work is parallel-safe; a lower wave ships first.
>
> **⚠ One amendment is needed in a file this PRD cannot edit.**
> 1. `P3-05-how-to-play.md` **names no widget class and no file** for the strip it specifies.
>    Requirement 47 has to compose it and cannot name it. Routing it is the coordinator's.
>
> **Closed since the last revision:** `P3-02-move-input.md` **has published** the previewed
> still-open quadrant set — `PendingSelection.freeChoiceQuadrants` (its req 23), derived in
> its req 3 and passed at its req 27 call site — so requirement 23's third row has its data
> source and requirement 43's `pendingFreeChoiceQuadrants` parameter is fed. That PRD has
> also **widened `BoardNotifier`** with `replace(Board)` (its req 29), which is what makes
> requirement 54 implementable.

> **On accepting `GameScreen`.** It could have gone to a new screen PRD or to `P3-02`, and
> neither is better. A separate PRD would hold a widget whose entire content is three
> children specified elsewhere — a file of cross-references with no subject of its own.
> `P3-02` owns *what a tap means*, not what is on screen, and its own Out of Scope says so.
> This file already owns the screen's dominant child, its 402×874 layout reasoning, and — in
> requirement 38 — an assertion about the screen itself, so the arithmetic that the vertical
> budget turns on is already here. The cost is that the title no longer describes the file:
> it is now the board **and** its host. That is recorded rather than hidden.

> **Note on source status.** `Game Board Design.md` carries the house banner *"Nothing here
> is settled"*, and until recently had no `## Decisions` section at all. **It now has
> five** — the free-choice cue's home, the tap-outside rule, the self-claiming preview, the
> chip labels, and the non-board haptic — of which only the chip labels reach a value this
> PRD holds (requirement 53). None covers the visual *treatments* it draws. So the position
> is unchanged for everything below: that doc is the only specification of the board's visual
> design, its Open Questions section is empty, the approved handoff was built from it, and
> `Tech Design.md` → What the Design Docs Already Imply treats its body as already locked.
> Where that doc hedges — *"probably* a big X or O", *"dimmed, desaturated, greyed, receded,
> **something**"*, free choice *"**may** want a calmer treatment"* — the approved handoff is
> what turns the hedge into a concrete answer, and the requirement cites both. See Open
> Questions: those hedges still have no Decision behind them.

> **Requirement numbers 1–45 are stable and must not be renumbered.** Inbound citations from
> `P1-03`, `P3-02`, `P3-03` and `P3-05` bind to them by number; the screen was appended as
> 46–53 for that reason, and requirement 54 was appended for the same reason. Five
> requirements are relabelled as constraints in *Design notes* below and **keep their
> numbers**.

---

## Problem

There is no board, and no screen to put one on. The game's entire readability rests on one
screen that has to answer two questions the moment the phone changes hands — *what changed,
and what can I do?* — across 81 cells, and `Game Board Design.md` → Last Move Highlight
names why that is harder here than in normal tic-tac-toe: a single small mark in a 9x9 field
is genuinely easy to miss, and in pass-and-play you were not watching when it was made.

Three highlights have to coexist on that screen at once — the opponent's committed last
move, the quadrant you are allowed to play in, and your own not-yet-committed selection —
and if any two of them look alike they create exactly the confusion they exist to
prevent. Alongside them the board has to say which quadrants are dead, which are claimed
and by whom, and which are simply off limits this turn. That last one is what
`Game Board Design.md` calls *"the easy one to under-build"*: highlighting the legal
quadrant alone leaves the other eight looking normal and tappable, and since an illegal
tap produces no shake, no flash, no message and no haptic, the dimming has to prevent the
tap because nothing will explain it afterwards.

Around the board, four PRDs specify pieces of one screen and none of them assembles it.

**And the screen that assembles it shows the wrong game.** `Menus and UI.md` → Leaving a
game mid-play promises that *"going back to the main menu doesn't discard anything"*, and
`P1-04-persistence.md` writes every confirmed move to disk so it can be resumed. But the
route hands `GameScreen` a `GameId` and, until requirement 54, nothing read it: the screen
rendered whatever `boardProvider` happened to hold, whose initial value is
`Board.newSeries()`. **Tapping a saved game in the open-games list would have opened an
empty board** — and because that board is complete and legal and correct-looking, nothing
about it says a game was lost.

## Goal

`lib/ui/board/` ships a `BoardView` that renders the 3x3-of-3x3 grid, its 81 cells, and
every quadrant and cell state the game can be in, from a `P1-02` `Board` and a pending
selection supplied by `P3-02`, with every treatment read from a `P1-03` Requirement 15 key
and its spacing from named code constants. Every one of the three simultaneous highlights
is drawn so that it cannot be mistaken for either of the other two; locked, claimed and
cat-game quadrants each read as unplayable and as distinct from one another; the whole 9x9
stays visible in portrait with no zoom; and every state is legible with animations switched
off. It also ships `GameScreen`, the host that **loads the game its id names**, composes the
scoreboard strip, the board and the how-to-play strip into one vertical stack, reads the game
once and passes it down, and holds the surfaces and strings its collaborators need it to
hold. Opening a saved game shows that game. The board draws state — it computes no rules,
handles no gesture, and holds no hardcoded *theme* value.

## Requirements

### Structure and geometry

1. The board is a 3x3 grid of quadrants, each holding its own full 3x3 small board — **81
   playable cells**, with depth **fixed at exactly two levels** (big board → small board)
   and no deeper nesting.
   *(`Game Board Design.md` → Board Structure; `Game Overview.md` → Decisions → Recursion
   depth; `Rules.md` → Setup)*
   **Verification:** the rendered tree contains 9 `QuadrantView`s, each containing exactly
   9 `CellView`s, and no `BoardView` or `QuadrantView` occurs beneath a `CellView`.

2. The board is **one component, driven entirely by per-quadrant state** — `BoardView`
   renders every screen state, rather than there being a "free choice board" and a "forced
   board."
   *(`design_handoff_game_ui/README.md` → The board (the important part))*

3. **Board geometry**, as approved: big board a 3x3 grid with gap 8; quadrant padding 5;
   cells a 3x3 grid with gap 3, square, and **transparent — no cell fill**; quadrant radius
   9, cell radius 3; grid lines drawn as an overlay inset 5, i.e. inside the quadrant's
   padding box. **The three gaps are code constants and the two radii are theme keys** —
   see requirement 28's split.
   *(`design_handoff_game_ui/README.md` → Geometry; `Theming.md` → Decisions → Does a theme
   control spacing and padding?)*

4. At the approved **402pt frame with 16pt side padding the board is 370pt, a quadrant
   ≈118pt and a cell ≈35pt**. That is below Apple's 44pt target and is accepted, because
   the two-tap select-then-confirm interaction makes a mis-tap free. These numbers are the
   approved visual source of truth and are not re-decided here. What happens at any other
   frame width is **unresolved and with the user** — see Open Questions.
   *(`design_handoff_game_ui/README.md` → Geometry; `Game Board Design.md` → Responsive /
   Screen Size, whose closing paragraph adopts exactly these numbers)*

5. **Small-board grid lines are drawn lines, not gaps, and must not touch the quadrant
   border**: 2 vertical lines at 33.33% and 66.67% of the quadrant's inner box, each
   1.5pt wide, running from 9% to 91% of the height; 2 horizontal lines the same but
   transposed; colored `boardLine` at 0.75 opacity with its glow. **Line width and inset
   stay theme values** — they are line weight, not spacing (requirement 28).
   *(`design_handoff_game_ui/README.md` → Grid lines — read this carefully;
   `Game Board Design.md` → Board Structure, which restates this)*
   **Verification:** no `CellView` subtree contains a `Border`, a `BoxDecoration.border` or
   an `OutlinedBorder`; `QuadrantGridLines` emits exactly 4 line children per quadrant, and
   each line's start and end offsets lie strictly inside the quadrant's inner box.

6. The **quadrant border** is the same blue at full presence: `0 0 0 1.5px
   rgba(79,195,255,0.5)`, outer glow `0 0 14px rgba(79,195,255,0.16)`, inner glow `inset 0
   0 12px rgba(79,195,255,0.06)`. Every quadrant carries it; requirement 8 replaces it and
   requirement 9 draws on top of it, per the composition fence in requirement 14.
   *(`design_handoff_game_ui/README.md` → Grid lines — read this carefully)*

7. *(Constraint — see Design notes.)* The **big board must read heavier than the small
   boards**. That hierarchy is carried by **weight, glow and the inset**, not by two
   different colors: both grids are the same blue, and the 9%–91% inset is what keeps them
   visually separate.
   *(`Game Board Design.md` → Visual Layout, Board Structure;
   `design_handoff_game_ui/README.md` → Grid lines — read this carefully)*

### Quadrant states

Requirement 14 defines the two orthogonal axes these treatments hang off, and fences how
they compose. Requirements 8–10 are **playability** treatments (one per quadrant, always);
requirements 11–12 are **status** treatments.

8. **Available** — still in play, and playable this turn because the player has a free
   choice. The quadrant's border is replaced by the brightened variant
   (`board.quadrantShadowOpen`, `color.quadrantBorderOpen`). This is the state the
   handoff's *Quadrant states* table calls **Open**; see requirement 14 on the rename. The
   same treatment is reused, by Decision, for the previewed free choice of requirement 23.
   *(`design_handoff_game_ui/README.md` → Quadrant states; screen 1d, where all nine
   quadrants are in this state)*

9. **Forced** (the one legal quadrant): a 2pt `highlightForced` ring, offset −3, radius
   12, with its outer and inset glow, drawn **over** requirement 6's base border.
   *(`design_handoff_game_ui/README.md` → Quadrant states; screen 1e)*

10. **Locked** (not playable this turn): a veil of `color.veilLocked` — **dimmed but not
    blacked out**. This is half the rule and the half that is easy to under-build: the
    other quadrants must not look normal and tappable, and because an illegal tap produces
    no shake, no flash, no error message and **no haptic**, the dimming is what has to
    prevent the tap. The absence of the buzz is the only feedback there is. Per requirement
    14 this state covers **every** quadrant that is neither forced nor available —
    including every claimed and every cat-game quadrant, and every quadrant once the game
    is over.
    *(`Game Board Design.md` → Active Quadrant Highlight (job 2) and → Taps outside the
    legal quadrant; `design_handoff_game_ui/README.md` → Quadrant states, Interactions &
    behavior)*
    **Verification:** for a locked still-in-play quadrant the veil child is present, its
    color resolves to `color.veilLocked`, its alpha is `< 1.0`, and every `CellView`
    content key inside that quadrant is still present in the tree — the veil covers the
    marks, it does not remove them. *(That the result is **readable** is a constraint, not
    an assertion: see requirement 39.)*

11. **Claimed** (status, either player): a centered claim mark over the whole quadrant —
    the player's mark art at `type.scale.markClaimX` / `markClaimO` in their mark color
    with `board.claimedMarkGlow` — over a `color.veilClaimed` veil.
    *(`Game Board Design.md` → Player Feedback / Affordances, which asks for "a big X or O
    overlaid on the whole quadrant"; `design_handoff_game_ui/README.md` → Quadrant states)*

12. **Cat game** (status, dead): a centered cat mark at `type.scale.markCat` in
    `color.catGame` with `board.catMarkGlow`, over a `color.veilCat` veil, with the
    `board.catCaption` label beneath it. It must be **visually distinct from claimed and
    from in-play** — it is permanently dead and neither player can ever have it.
    *(`Game Board Design.md` → Player Feedback / Affordances;
    `design_handoff_game_ui/README.md` → Quadrant states)*

13. Claimed and cat quadrants deliberately share the **same overlay language** — all three
    finished states read as "finished," and it is the glyph and its color that say whose
    it is, or that it belongs to nobody. Distinctness between claimed and cat is carried
    by glyph and color, not by a different veil.
    *(`design_handoff_game_ui/README.md` → Quadrant states, closing note)*

14. A quadrant's rendered state is **two orthogonal facts, not one**, and both are derived
    rather than authored. Both derive from `P1-02-engine-rules.md`'s published accessors —
    `board.placementState`, `board.activeQuadrant`, `board.quadrantAt(q)`.

    | Axis | Value | Derivation |
    |---|---|---|
    | **Status** | still in play | `quadrantAt(q) == QuadrantState.open` |
    | | claimed by Player One | `quadrantAt(q) == QuadrantState.claimedByPlayerOne` |
    | | claimed by Player Two | `quadrantAt(q) == QuadrantState.claimedByPlayerTwo` |
    | | cat game | `quadrantAt(q) == QuadrantState.catGame` |
    | **Playability** | **forced** | `placementState == PlacementState.forced && activeQuadrant == q` |
    | | **available** | `placementState == PlacementState.freeChoice && quadrantAt(q) == QuadrantState.open` |
    | | **locked** | otherwise |

    **Gate on `placementState`, never on `activeQuadrant == null`.**
    `P1-02-engine-rules.md` requirement 36 states that `activeQuadrant` is null in **both**
    `freeChoice` and `gameOver`, and warns that a consumer branching on nullity alone
    "would read a finished game as free choice." Under the derivation above, `gameOver`
    makes **every** quadrant locked — which is what stops a won board lighting up nine
    brightened borders behind the result card.

    **Every quadrant carries exactly one value on each axis, simultaneously.** A claimed or
    cat quadrant is **never** forced — the engine sends a player onto a dead quadrant into
    free choice instead (`P1-02` requirements 17–19) — and is never available, so **every
    claimed and every cat quadrant is locked, in both modes, always**.

    Both axes describe the board **as it is now**. Requirement 23's preview is a third,
    provisional layer over them, and a quadrant that is currently `locked` can carry a
    previewed free-choice highlight at the same time.

    **How the two axes compose visually — fenced, reversible.** The handoff's *Quadrant
    states* table lists Locked, Claimed-P1, Claimed-P2 and Cat as **sibling rows, each
    carrying exactly one veil**, and `P1-03` requirement 15 notes that the locked veil is
    "deliberately weaker than the other two." Reading those as siblings:
    - a **finished** quadrant draws its own `veilClaimed` / `veilCat` and **not**
      `veilLocked` on top — finished subsumes locked *visually*, while still keying as
      `locked` on the playability axis (requirement 45);
    - the base border of requirement 6 is drawn on every quadrant; `quadrantShadowOpen`
      **replaces** it when playability is available; the forced ring is drawn **over** it
      and does not replace it.

    **PRD-author judgment, reversible.** No doc states the composition. Stacking the two
    veils would put a finished quadrant at ~0.88 and contradict the table's sibling
    structure. This reading changes only which veil widget `QuadrantView` emits, and is a
    one-line change if the user rules the other way.

    *(`design_handoff_game_ui/README.md` → State → "Derived for rendering", Quadrant
    states; `P1-02-engine-rules.md` requirements 5, 17–19, 36, 41; `Rules.md` → Edge Cases
    → Sent to a dead quadrant → free choice)*
    **Verification:** across a table of engine states — opening board, forced, free choice
    with claimed and cat quadrants present, and a won board — every quadrant resolves to
    exactly one status key and exactly one playability key; no claimed or cat quadrant ever
    resolves forced or available; and on a `gameOver` board all nine resolve locked.

### Cell states

15. An **empty cell renders nothing** — it is transparent, with no fill and no border. It
    still takes taps: see requirement 44.
    *(`design_handoff_game_ui/README.md` → Cell states, Geometry)*

16. A **played cell renders its player's mark** at `type.scale.mark` in that player's mark
    color with its glow pair, from `board.cellAt(quadrant, cell)`.
    *(`design_handoff_game_ui/README.md` → Cell states; `P1-02` requirement 41)*

17. Marks are **theme-supplied asset slots — an image or an icon — not shapes drawn in
    board code**, and are not locked to X and O. Neon's ✕, ○ and Ø are Neon's choice of
    art, not a constraint on the board. The board reads
    `marks.<slot>.{kind,value,font,weight}` and never a literal glyph. **Mark sizes remain
    theme values** — they are the type scale, which `Theming.md` → Decisions → Does a theme
    control spacing and padding? explicitly keeps in the theme.
    *(`Tech Design.md` → Decisions → Marks — image or icon, supplied by the theme;
    `Game Board Design.md` → Pieces & Marks; `Theming.md` → Decisions → Marks beyond X and
    O; `P1-03` requirement 16)*

    **What a `type.scale.mark*` size means, per `kind` — fenced, reversible.** The four
    mark sizes are a *type* scale, which is meaningful for a glyph and not for a bitmap.
    The board treats the size as **the side of the square box the mark is laid out in**:

    | `marks.<slot>.kind` | `size` means | `weight` |
    |---|---|---|
    | `glyph` | the font size, laid out in a box of that side | applied |
    | `icon` | the icon's box side | ignored |
    | `image` | the box side; art fitted `BoxFit.contain`, aspect preserved | ignored |

    **PRD-author judgment, reversible.** Without this, a claim mark supplied as an image has
    nothing constraining it to fit inside its quadrant, and requirement 30's legibility
    contract binds every theme. Neon authors all three marks as `glyph` and is the only
    theme through wave 3, so the fence is observationally free this wave and is a change in
    `MarkView` alone if ruled otherwise.

### The three highlights

18. *(Constraint — see Design notes.)* **All three highlights can be on screen at once, and
    all three must be visually distinguishable.** They differ in scope, which is part of
    how they are told apart:

    | Highlight | Scope | Meaning |
    |---|---|---|
    | Opponent's last move | one cell | what just happened |
    | Active quadrant | one quadrant | where you're allowed to play |
    | Pending-move preview | one cell + one destination quadrant, **or every still-open quadrant** | where you'd send them |

    *(`Game Board Design.md` → Three highlights on screen at once; The Two Highlights
    Together; → Decisions → What does the board preview when the selected move would claim
    its own send target?; `design_handoff_game_ui/README.md` → Cell states, screen 2d)*

19. **Opponent's last move** — one cell, committed, and **exaggerated so it is readable at
    a quick glance**: the player must not have to hunt across 81 cells to find what
    changed. Drawn as `board.lastMoveRing` (2pt **solid** `color.highlightLastMove`, offset
    −1, radius 5, with its outer and inset glow) on the cell named by `board.lastMove`. When
    `lastMove` is null — a new series, or the board returned by `startNextGame()` — no ring
    is drawn.
    **It is a static ring and does not pulse.** `Animations.md` → Where Animations Fire
    floats a pulsing treatment as a possibility; the user has since settled that animation
    scope is the player's marker only, so this treatment is the whole of what the highlight
    does. *(`P2-04-animations.md` requirement 2 and its requirement 25.)*
    *(`Game Board Design.md` → Last Move Highlight; `design_handoff_game_ui/README.md` →
    Cell states; `P1-02` requirement 40, which guarantees null rather than a sentinel)*

20. **Last-move lifetime: the highlight persists until your move is confirmed.** It stays
    visible the entire time you are deciding — through selecting a cell and previewing
    where it sends your opponent — and only clears once you confirm. It is reference
    material while you think, not a notification that flashes and disappears, so it can be
    compared side by side against your pending selection. The board draws `board.lastMove`
    and nothing else; the lifetime follows from the engine's `lastMove` changing only on
    `applyMove`.
    *(`Game Board Design.md` → Last Move Highlight → Lifetime; `P3-02` requirement 16,
    which puts the commit on the second tap)*
    **Verification:** with a pending selection set, then changed to a different cell, the
    last-move ring key stays on the same cell throughout; after a commit it is present on
    the newly played cell and absent from the previous one.

21. The **active-quadrant highlight has two modes**, and the board must render both:

    | Mode | What's highlighted |
    |---|---|
    | **Forced** | Exactly one quadrant (requirement 9) |
    | **Free choice** | *Every* still-in-play quadrant — one to nine (requirement 8) |

    Free choice also covers the opening move. Nine forced rings at once would look like
    noise, so free choice takes the calmer **available** treatment rather than nine copies
    of the forced ring. A free-choice state with exactly one still-open quadrant still
    renders as available, not forced (`P1-02` requirement 17).
    *(`Game Board Design.md` → Active Quadrant Highlight → The free-choice state, which
    floats the calmer treatment as a "may want"; resolved concretely by
    `design_handoff_game_ui/README.md` → Quadrant states and screen 1d)*
    **Both modes are static.** The *"pulsing glow on the legal quadrant"* the docs float is
    not built — animation scope is marker-only, settled by the user (`P2-04-animations.md`
    requirement 2). The forced ring's glow is a drawn treatment, not motion.
    The **text** half of the free-choice cue is not this PRD's, and its home is settled: it
    lives in the how-to-play strip **below** the board, owned by `P3-05-how-to-play.md`
    requirements 10 and 13 — not in a banner above it.
    *(`Game Board Design.md` → Decisions → Where does the free-choice cue live?)*

22. In free choice, **claimed and cat-game quadrants still read as locked**. It is "pick
    any of these open ones," not "the board is unlocked." This is requirement 14's
    derivation, not an exception to it.
    *(`Game Board Design.md` → Active Quadrant Highlight → The free-choice state)*

23. **Pending-move preview** — it marks a cell *and* what the move would do to the big
    board, and **both must read as provisional**, clearly not yet committed and clearly
    distinct from the committed last-move highlight. **The halves are drawn independently**,
    and the big-board half branches on `pendingDestinationState` (requirement 43), never on
    the destination's nullity:

    | Half | Drawn when | Treatment |
    |---|---|---|
    | selected cell | `pendingSelection != null` | `board.pendingCellRing` (2pt **dashed** `color.highlightPending`, offset −1, radius 5), plus a **ghost mark** — the current player's own mark art (requirement 17) at `board.pendingGhostOpacity` |
    | destination quadrant | `pendingDestinationState == forced` — destination non-null | `board.pendingQuadrantRing` (2pt **dashed**, offset −3, radius 12) over a `board.pendingQuadrantWash` wash, on that one quadrant |
    | **previewed free choice** | `pendingDestinationState == freeChoice` — destination null | requirement 8's **available** treatment on **every quadrant in `pendingFreeChoiceQuadrants`** |
    | *(game over)* | `pendingDestinationState == gameOver` — destination null | **no big-board treatment** — fenced, see below |

    **Why the third row exists.** *"If that move would claim or cat-game the very quadrant
    it points at, the quadrant is dead by the time the send resolves and the opponent gets
    a free choice — so there is no single quadrant to ring. The preview shows the truth —
    the opponent may play anywhere still open — rather than showing nothing."* It reuses
    the free-choice highlight that exists for the state *after* such a move lands, so the
    preview and the resulting board look consistent, and it teaches the rule at the moment
    it fires.
    *(`Game Board Design.md` → Decisions → What does the board preview when the selected
    move would claim its own send target?)*

    **The previewed set is supplied, not computed.** `pendingFreeChoiceQuadrants` comes
    from `P3-02`'s previewed post-move board. The board must **not** substitute its own
    still-open quadrants: the quadrant the pending move is about to claim is open *now* and
    dead *then*, and highlighting it would preview a quadrant the opponent cannot use —
    the exact failure `P3-02` requirement 3 was rewritten to prevent.

    **Both values come from `P3-02-move-input.md`** (its requirements 3, 23, 25 and 27, all
    landed). **The board does not derive the destination from the cell** — that mapping is
    the sending rule, which the engine overrides whenever the move kills its own send
    target, and it belongs to the engine (requirement 35).
    **The ghost is the player's mark at an opacity, not separate art.** `P1-03`
    requirement 15 publishes `board.pendingGhostOpacity` and no ghost-art slot.

    **The `gameOver` row is fenced, reversible.** A move that ends the game also publishes
    a null destination, and the Decision above does not reach it — there is no next move, so
    "the opponent may play anywhere still open" is not true. Drawing no big-board treatment
    is the only claim that is not false. It is a fence, not an answer; see Open Questions.

24. *(Constraint — see Design notes.)* The three are separated **by weight, not by color**:
    **dashed = provisional, solid = committed**. Last move is a solid lavender ring, the
    active quadrant a solid purple glowing ring, the pending move dashed white with a ghost
    mark. Purple is reserved for the two gameplay-critical highlights and nothing else.
    **Requirement 23's third row is the one exception**, and it is a Decision rather than an
    oversight: the previewed free choice is provisional but is drawn in the *solid*
    available treatment, because the Decision's stated reason is that the preview and the
    resulting board should look consistent. Flagged under Open Questions.
    *(`design_handoff_game_ui/README.md` → Cell states, Design tokens → Color logic;
    `Game Board Design.md` → The Two Highlights Together; → Decisions → What does the board
    preview when the selected move would claim its own send target?)*

25. **Z-order inside a quadrant is fixed**, and is the child order of `QuadrantView`'s
    `Stack`: cells 0 → grid lines 1 → veils / claim / cat overlays 2 → forced ring,
    destination ring and previewed-free-choice border 3 → **last-move ring and pending ring
    4**. The last-move ring sits **above the locked veil** on purpose, so a mark in a
    now-locked quadrant still reads at a glance — which is the whole point of the highlight.
    *(`design_handoff_game_ui/README.md` → Cell states → Z-order; screen 1e, where the
    last-move ring sits in the locked quadrant q8)*
    **Verification:** in `QuadrantView`'s `Stack.children`, the index of the last-move ring
    child is strictly greater than the index of the veil child, which is strictly greater
    than the index of the cell grid. *(Whether the mark **underneath** a `veilClaimed`
    remains readable is not assertable and is a known defect — see Open Questions.)*

26. `BoardView` establishes its **own stacking context** — a single `Stack` root that the
    claim and veil overlays never escape — so the game-over card of requirement 52 and any
    sheet drawn over the board reliably sit above them.
    *(`design_handoff_game_ui/README.md` → 1f, which notes this explicitly)*

### Everything here is theme-driven — except spacing

27. **Every *treatment* in this PRD is theme-driven.** This document specifies *what must
    be communicated*; the theme decides *what it looks like*. **Board and screen code
    contain no hardcoded color, background, font, mark, radius, opacity or duration** —
    every such value resolves through a `P1-03` Requirement 15 key path.
    *(`Game Board Design.md` → Everything Here Is Theme-Driven; `Theming.md` →
    Architectural Rule; `P1-03` requirement 25; enforced by `P1-05-theme-guard-test.md`)*

    **Spacing is the one carve-out, by Decision.** *"No. Spacing and layout numbers are
    fixed in the code, not theme-controlled — for now."* The reason is enforcement: the
    guard cannot tell a themed gap from an incidental one, so a padding section in the
    schema would have been *"a rule that nothing verifies."* Requirement 3's three gaps,
    requirement 38's screen padding and requirement 50's two screen constants are therefore
    **named code constants**, and that is conformant, not a violation. **Requirement 53's
    three label strings are the second carve-out** — they are content, not style.
    *(`Theming.md` → Decisions → Does a theme control spacing and padding?)*
    **Verification:** the hardcoded-theme-value scan reports zero violations under
    `lib/ui/board/`; every literal number in that directory outside `BoardMetrics` and
    `GameScreen`'s own constants (requirements 42, 50) traces to a theme key.

28. **The key-path binding, and the line between theme and code.** Every value this PRD
    names is either a `P1-03-theme-system.md` Requirement 15 key or a named code constant.
    One row per requirement; a value in neither column is a value this PRD does not draw.

    | Req | Draws | Theme key paths | Code constants |
    |---|---|---|---|
    | 3 | board and quadrant geometry, quadrant fill | `radius.quadrant`, `radius.cell`, `color.quadrantFill` | `outerGap` 8, `quadrantPadding` 5, `innerGap` 3 |
    | 5 | small-board grid lines | `board.gridLineWidth`, `board.gridLineInsetPercent`, `board.gridLineOpacity`, `board.gridLineGlow`, `color.boardLine` | — |
    | 6 | quadrant base border | `board.quadrantShadow`, `color.quadrantBorder` | — |
    | 8 | available quadrant, and requirement 23's previewed free choice | `board.quadrantShadowOpen`, `color.quadrantBorderOpen` | — |
    | 9 | forced ring | `board.forcedRing`, `color.highlightForced`, `color.highlightForcedGlow` | — |
    | 10 | locked veil | `color.veilLocked` | — |
    | 11 | claimed veil, claim mark, its glow | `color.veilClaimed`, `marks.playerOne.*`, `marks.playerTwo.*`, `type.scale.markClaimX`, `type.scale.markClaimO`, `color.playerOneMark`, `color.playerTwoMark`, `board.claimedMarkGlow` | — |
    | 12 | cat veil, cat mark, its glow, caption | `color.veilCat`, `marks.catGame.*`, `type.scale.markCat`, `color.catGame`, `board.catMarkGlow`, `board.catCaption.{size,weight,tracking,color}` | — |
    | 16 | in-cell mark | `type.scale.mark`, `marks.playerOne.{kind,value,font,weight}`, `marks.playerTwo.{kind,value,font,weight}`, `color.playerOneMark`, `color.playerTwoMark`, `color.playerOneGlow`, `color.playerTwoGlow` | — |
    | 19 | last-move ring | `board.lastMoveRing`, `color.highlightLastMove`, `color.highlightLastMoveGlow` | — |
    | 23 | pending cell ring, ghost, destination ring and wash | `board.pendingCellRing`, `board.pendingGhostOpacity`, `board.pendingQuadrantRing`, `board.pendingQuadrantWash`, `color.highlightPending` | — |
    | 38, 50 | screen padding and gaps | `color.ground` (the screen's background) | `screenHorizontalPadding` 16, `safeAreaTop` 62, `stripToBoardGap` 14 |
    | 53 | the three chip label strings | — | `playerOneLabel`, `tiesLabel`, `playerTwoLabel` |
    | 54 | the pre-seed surface, while the stored game loads | `color.ground` | — |

    **The boundary is narrower than "no numbers in code", and reading it wrong in either
    direction produces a defect.** What moved into code is the **gaps between things**:
    outer gap, quadrant padding, inner gap, screen padding, and the screen's two vertical
    gaps. What stayed in the theme is everything the guard *can* see or that a theme must be
    able to restyle: **grid-line width and inset, the two radii, all colors and veils, and
    every mark size**. A theme that changes its board's line weight or its mark art must
    still be able to; a theme cannot reflow the grid.
    *(`Theming.md` → Decisions → Does a theme control spacing and padding?, which keeps
    *"colour, marks, sounds, icons, animation, radii and the type scale"* in the theme)*

    Every theme key above is status **`required`** in `P1-03` requirement 15 and is
    transcribed into `assets/themes/neon.yaml` by its requirement 13, so every one resolves
    in Neon. Composite values arrive as `P1-03` requirement 35's structured **ring object**
    and **shadow list**, not as CSS strings — the board reads fields, it does not parse.
    **Verification:** every dotted path in this table appears in
    `lib/theme/required_keys.dart` and resolves against the materialized Neon theme.

    **Routing note, not this PRD's to fix:** `P1-03` requirement 15 still publishes
    `board.outerGap`, `board.quadrantPadding` and `board.innerGap` as `required` keys. This
    PRD was their only consumer and no longer reads them. Whether they are dropped from the
    schema or left as unread keys is `P1-03`'s call.

29. The board's highlights are **separately addressable keys** — `color.highlightLastMove`,
    `color.highlightForced` and `color.highlightPending` with their `board.*Ring`
    companions — because up to three are on screen at once and must not collapse into one
    another. Locked, claimed and cat carry three separate veil keys for the same reason.
    *(`Theming.md` → What a Theme Controls → Visual; `P1-03` requirement 20)*

30. *(Constraint — see Design notes.)* **Legibility is a contract on every theme, not just
    Neon.** The last-move and active-quadrant highlights are *gameplay-critical, not
    decoration* — "a pretty theme that hides the last move is a broken theme."
    *(`Theming.md` → What a Theme Controls; `Game Board Design.md` → Player Feedback /
    Affordances, closing note)*

31. *(Constraint — see Design notes.)* **The board is fully readable with animations
    switched off.** No state in this PRD may depend on motion to be understood; with
    animations off the game simply shows the new state, with no substitute effect. This is
    the board-side half of `P2-04-animations.md` requirement 21.
    **Cheap to hold, now that animation scope is settled.** Not one treatment in this PRD
    animates — the marker's pop is the only motion in the game (`P2-04` requirement 2), and
    it is drawn *over* a mark this PRD renders statically. So there is no board state whose
    only expression is motion, and this constraint is structural rather than a discipline to
    maintain.
    *(`Animations.md` → Decisions → Animations off = instant state change;
    `design_handoff_game_ui/README.md` → Interactions & behavior)*

### How it is rendered

32. **The board is rendered with widgets, not a `CustomPainter`.** 81 `GestureDetector`s in
    nested grids. *"ok widgets is the winner lets make that happen."*
    *(`Tech Design.md` → Decisions → How is the board rendered?)*

33. **Watch out for the documented hazards:** nested `Border.all` **doubles interior grid
    lines** — two adjacent 1px borders read as 2px — and hairlines can look uneven at
    fractional device pixel ratios. Requirement 5 already forbids per-cell borders; this
    records why.
    *(`Tech Design.md` → Decisions → How is the board rendered? → "Watch out for")*

34. **Grid lines are widgets: a `Stack` of four positioned line boxes per quadrant**, laid
    out by `QuadrantGridLines` at z-index 1 (requirement 25), each sized and inset per
    requirement 5. **The `CustomPaint` escape hatch is not taken.**
    *(`Tech Design.md` → Decisions → How is the board rendered?, which records the hybrid
    thin `CustomPaint` grid-line overlay as *"an escape hatch, not a decision taken"*)*
    **PRD-author judgment, reversible.** Four positioned boxes satisfy requirement 5's inset
    geometry without any per-cell border, so the hatch is not needed. Fenced rather than
    left open because a build agent cannot raise a question mid-run. Reversible: swapping to
    one `CustomPaint` per quadrant changes `QuadrantGridLines`'s internals only.

35. The board **renders engine state and computes no rules**. Legal-move computation, the
    sending rule, claim and cat-game detection and the free-choice state all come from
    `P1-02-engine-rules.md`; the board reads them. Requirement 14's derivation is a
    projection of state the engine already exposes; the pending destination, its state and
    the previewed open set are all supplied by `P3-02` rather than derived here.
    *(`Tech Design.md` → Decisions → Is the game logic separate from Flutter?)*
    **Verification:** a source scan of `lib/ui/board/` finds no three-in-a-row check, no
    cell→quadrant mapping, no call to `applyMove`, and no construction of a legal-move set.

### Layout

36. **Portrait only.** No landscape.
    *(`Tech Design.md` → Decisions → Orientation — portrait only; enforced at the app level
    by `P1-01` requirement 7)*

37. **The whole 9x9 grid stays visible at all times. No zoom**, and no scrolling to reach
    part of the board.
    *(`Game Board Design.md` → Responsive / Screen Size; `Tech Design.md` → What the
    Design Docs Already Imply)*
    **Verification:** the board subtree contains no `Scrollable`, `InteractiveViewer` or
    `SingleChildScrollView`, and at the 402pt reference frame no `RenderBox` in the board
    subtree reports overflow. `P3-05` requirement 14 extends this assertion past the board
    subtree to the whole game screen.

38. The board sits in a **vertical stack below the scoreboard**, with **16pt horizontal
    padding, as a code constant** (`BoardMetrics.screenHorizontalPadding`). **Nothing sits
    between the scoreboard and the board** except requirement 50's gap — the turn banner the
    handoff drew there is not built, and the how-to-play strip sits *below* the board. The
    stack itself is requirement 47.
    *(`Game Board Design.md` → Visual Layout; → Decisions → Where does the free-choice cue
    live?; `Theming.md` → Decisions → Does a theme control spacing and padding?;
    `design_handoff_game_ui/README.md` → Spacing, screens 1d/1e; `P3-03` requirement 2;
    `P3-05` requirement 13)*

### Tests

39. The board is covered by **widget tests, with no golden image tests**.
    *(`Tech Design.md` → Decisions → Widget tests for the board — no golden tests;
    `P3-02` requirement 23 applies the same rule on the input side)*

    **What that rules out, stated so coverage is not overstated.** Roughly 70% of this
    document is pixel values — hex colors, glow radii, ring widths, dash patterns, offsets,
    opacities, point sizes. **None of it is machine-verifiable in this repo.** Requirement
    40's keys assert that a state is **present**, never that its treatment is correct: a
    build that draws the locked veil at 0.95 instead of 0.50, or the pending ring solid
    instead of dashed, passes every test in this PRD. What *is* assertable is structure
    (requirements 1, 47), derivation (requirement 14), key presence, absence and coexistence
    (requirements 40, 45), the no-per-cell-border rule (requirement 5), stack order
    (requirement 25), theme-key resolution and the guard scan (requirements 27–28), the
    engine-purity scan (requirement 35), the last-move lifetime (requirement 20), the four
    preview branches (requirements 23, 43), the tap surfaces (requirements 44, 51), the
    screen's composition, wiring and strings (requirements 47–49, 53), **and the load path
    (requirement 54)**. Treatment correctness is verified by eye against the handoff screens,
    and that review is the only check on it.

40. **Each rendered fact is independently addressable** via requirement 45's `BoardKeys`.
    The keys mirror requirement 14's two axes rather than flattening them into one
    enumeration, and the cell keys are **facets that may coexist**, not an exclusive list:

    | Group | Keys | Cardinality |
    |---|---|---|
    | Quadrant **status** | stillInPlay · claimedByPlayerOne · claimedByPlayerTwo · catGame | exactly one per quadrant |
    | Quadrant **playability** | forced · available · locked | exactly one per quadrant |
    | Quadrant **preview** | pendingDestination · pendingFreeChoice | at most one kind per board; `pendingDestination` on zero or one quadrant, `pendingFreeChoice` on zero or many |
    | Cell **content** | empty · playerOne · playerTwo | exactly one per cell |
    | Cell **highlight** | lastMove · pending · ghostMark | zero or more, independent of content |
    | Cell **legality** | playable | present iff legal; independent of everything above |

    **Verification:** a claimed quadrant is findable as **both** `claimedByPlayerOne`
    **and** `locked`; a played cell that is the last move is findable as **both**
    `content.playerOne` **and** `lastMove`; a pending cell is findable as `content.empty`
    **and** `pending` **and** `ghostMark`; a quadrant carrying `pendingFreeChoice` while the
    board is in a `forced` state is findable as **both** `locked` **and**
    `pendingFreeChoice`; `pendingDestination` and `pendingFreeChoice` never both appear on
    one board; and no cell in a claimed quadrant carries `playable`.

41. Tests **run locally** via `flutter test`. There is no CI; nothing runs them on a push.
    *(`Tech Design.md` → Decisions → CI — local builds only)*

### The widget surface

Named so `P3-02`, `P3-03` and `P3-05` bind to symbols rather than to prose, in the manner of
`P1-02-engine-rules.md` → The public API.

42. **Files and classes under `lib/ui/board/`:**

    | File | Public symbol | Role |
    |---|---|---|
    | `game_screen.dart` | `GameScreen` | the host; requirements 46–54 |
    | `board_view.dart` | `BoardView` | the 3x3 of quadrants; requirements 1–4, 26, 38 |
    | `quadrant_view.dart` | `QuadrantView` | one quadrant: the `Stack` of requirement 25; requirements 6–14, 23 |
    | `quadrant_grid_lines.dart` | `QuadrantGridLines` | requirement 34's four line boxes |
    | `cell_view.dart` | `CellView` | one cell and its tap surface; requirements 15–17, 19, 23, 44 |
    | `mark_view.dart` | `MarkView` | renders a `marks.<slot>` per requirement 17's kind table, at a given box side |
    | `board_metrics.dart` | `BoardMetrics` | the board's spacing constants: `outerGap` 8, `quadrantPadding` 5, `innerGap` 3, `screenHorizontalPadding` 16 — `static const double`, one place, not scattered literals |
    | `board_keys.dart` | `BoardKeys` | requirement 45's key literals |

    Requirement 50's two screen-level constants, requirement 53's three strings and
    requirement 54's load state all live in `game_screen.dart` beside their only user,
    following `P3-03` requirement 21's precedent of keeping a component's layout constants in
    its own file.
    *(`Tech Design.md` → Decisions → Project structure — layer-first; `P1-01` requirement 2
    creates the directory)*

43. **`BoardView`'s constructor is its whole input surface.** It is a `ConsumerWidget`
    reading the active theme from `P1-03` requirement 24's `activeThemeProvider`, and takes:

    | Parameter | Type | Supplied by |
    |---|---|---|
    | `board` | `Board` (required) | `P1-02` requirement 29 |
    | `pendingSelection` | `Move?` | `P3-02` requirement 27 passes `pending?.move` |
    | `pendingDestinationQuadrant` | `int?` | `P3-02`'s `pending?.destinationQuadrant` — **passed, never derived** |
    | `pendingDestinationState` | `PlacementState?` | `P3-02`'s `pending?.destinationState` |
    | `pendingFreeChoiceQuadrants` | `Set<int>?` | `P3-02` requirement 23's `pending?.freeChoiceQuadrants` — the still-open quadrants of its previewed post-move board |
    | `onCellTap` | `void Function(int quadrant, int cell)` — **required, non-nullable** | requirement 48 |

    **The pending parameters are not paired. The invariant is one-way:**

    > `pendingDestinationQuadrant != null` **implies** `pendingSelection != null`.
    > The converse does **not** hold.

    A non-null selection with a **null destination is legal and reachable**, not an error.
    `P3-02` requirement 3 reads the destination from the board *after* the previewed move
    rather than from positional identity — per `Rules.md` → Decisions → *Does a move that
    claims its own send target still send there?* — so a selection whose confirmation would
    claim or cat-game the quadrant its cell points at, or would end the game, publishes
    `destinationQuadrant == null`. `pendingFreeChoiceQuadrants` is non-empty exactly when
    `pendingDestinationState == freeChoice`.

    **Branch on `pendingDestinationState`, never on the destination's nullity.** This was
    incidental when both null cases drew nothing. **It is now load-bearing:** `freeChoice`
    draws the available treatment across the previewed open set, `gameOver` draws no
    big-board treatment at all, and the two are indistinguishable from a null destination
    alone. Requirement 23's table is the branch.

    **The `gameOver` case is reachable and must be handled.** A player can select the cell
    that completes a third quadrant in a line, or the last cell of the last open quadrant,
    and stand there with the pending selection on screen before confirming.

    **What is drawn when the destination is null:** always the cell half of requirement 23.
    **Suppressing the whole preview because the destination is null is a defect** — it would
    blank the cell the player just tapped, making a legal first tap look like it did
    nothing. `P3-02` requirement 27 verifies this case from its side.

    **PRD-author judgment, reversible.** Scalars rather than `P3-02`'s `PendingSelection`
    keep `lib/ui/board/` from importing a type in `lib/state/`, and keep `BoardView`
    testable with no provider override beyond the theme.
    **Verification, four cases** — one per row of requirement 23's table: (a) no pending
    selection: none of `cellPending`, `cellGhostMark`, `quadrantPendingDestination` or
    `quadrantPendingFreeChoice` appears; (b) `forced`: cell keys plus
    `quadrantPendingDestination` on exactly the named quadrant; (c) `freeChoice`: cell keys
    plus `quadrantPendingFreeChoice` on exactly the quadrants in
    `pendingFreeChoiceQuadrants`, and no `quadrantPendingDestination` anywhere;
    (d) `gameOver`: cell keys only, and no big-board preview key anywhere.

44. **`CellView` is the tap surface, and it hit-tests opaque.** Each of the 81 cells wraps
    its content in a `GestureDetector` with **`behavior: HitTestBehavior.opaque`** and an
    `onTap` forwarding to `BoardView.onCellTap(quadrant, cell)`. **Every cell installs that
    callback, on every build, regardless of legality** — the board does not gate input, it
    draws state; whether a tap does anything is `P3-02`'s.
    *(`Tech Design.md` → Decisions → How is the board rendered?; `P3-02` requirement 19)*

    **`onCellTap` is required and non-nullable, and `CellView` never omits `onTap`. Do not
    "simplify" either.** Both look like obvious cleanups, and both reintroduce the same
    shipped defect:
    - **`opaque` alone does not absorb the tap.** It makes the cell a hit-test target; it
      does not stop an ancestor recognizer winning the gesture arena. What wins the arena is
      the cell having a recognizer of its own — and a `GestureDetector` with a null `onTap`
      registers no tap recognizer at all. An "illegal cells don't need a handler" cleanup
      therefore lets illegal taps fall through to requirement 51's clear surface, so tapping
      a locked quadrant would silently **clear the player's pending selection**. `P3-02`
      requirement 26 states the boundary in exactly these terms — *"a tap absorbed by a
      `CellView` never clears; every other tap on the board screen does."*
    - **An empty legal cell renders nothing** (requirement 15), so under
      `HitTestBehavior.deferToChild` it would not hit-test at all and the whole board would
      be inert.

    **Verification:** a tap at the centre of an empty cell **in a locked quadrant** invokes
    `onCellTap` with that cell's indices **and does not reach requirement 51's surface**.
    The second half of that assertion is the only thing standing between this requirement
    and the defect above — a test that checked only that `onCellTap` fired would stay green
    through the nullable-`onTap` regression.

45. **`BoardKeys` publishes every key literal.** Requirement 40's addressability is
    delivered as **keys, not widget types** — a facet that coexists with others cannot be
    asserted by type without inventing a widget per facet, and `P3-02` and `P3-05` write
    tests against these literals. Each accessor returns a `ValueKey<String>`:

    | Accessor | Key string | Present when |
    |---|---|---|
    | `quadrant(q)` | `board.quadrant.$q` | always |
    | `quadrantStatus(q, status)` | `board.quadrant.$q.status.{stillInPlay\|claimedByPlayerOne\|claimedByPlayerTwo\|catGame}` | requirement 14 status axis |
    | `quadrantPlayability(q, p)` | `board.quadrant.$q.playability.{forced\|available\|locked}` | requirement 14 playability axis |
    | `quadrantPendingDestination(q)` | `board.quadrant.$q.pendingDestination` | `pendingDestinationState == forced` and `pendingDestinationQuadrant == q` |
    | `quadrantPendingFreeChoice(q)` | `board.quadrant.$q.pendingFreeChoice` | `pendingDestinationState == freeChoice` and `pendingFreeChoiceQuadrants` contains `q` |
    | `cell(q, c)` | `board.cell.$q.$c` | always |
    | `cellContent(q, c, content)` | `board.cell.$q.$c.content.{empty\|playerOne\|playerTwo}` | requirement 16 |
    | `cellLastMove(q, c)` | `board.cell.$q.$c.lastMove` | requirement 19 |
    | `cellPending(q, c)` | `board.cell.$q.$c.pending` | `pendingSelection` names this cell |
    | `cellGhostMark(q, c)` | `board.cell.$q.$c.ghostMark` | as `cellPending` |
    | **`cellPlayable(q, c)`** | `board.cell.$q.$c.playable` | **`board.legalMoves.contains(Move(quadrant: q, cell: c))`** |
    | `screen` · `clearSurface` | `board.screen`, `board.screen.clearSurface` | requirements 46, 51 |
    | **`screenLoading`** | `board.screen.loading` | **requirement 54 — while the stored game is being read** |

    Spelling follows `P1-02` requirement 8's convention — no `p1`/`p2`, no `quad`.
    `quadrantPendingFreeChoice` is deliberately distinct from the `available` playability
    key even though both render requirement 8's treatment: one is the board's current state,
    the other a preview of a state that has not happened.

    **`cellPlayable` answers `P3-02` OQ-7** — the set to compare its tap-responding set
    against, rendered straight from `P1-02` requirement 35's `legalMoves` membership. A
    read, not a re-derivation. Being per-cell, it also covers the occupied-cell and
    cell-in-a-dead-quadrant cases the quadrant-level locked key cannot express.
    **Verification:** for a board in each of the forced, free-choice and game-over states,
    the set of cells carrying `cellPlayable` equals `board.legalMoves` exactly — and is
    empty on a finished board.

### `GameScreen` — the host

Accepted by this PRD rather than left unowned; see the status block. Every obligation below
is already specified from the other side, so these requirements assemble rather than invent —
**with one exception, requirement 54, which no PRD specified from any side.**

46. **`GameScreen` is a `ConsumerStatefulWidget` in `lib/ui/board/game_screen.dart`**,
    constructed by `P2-01` requirement 2's route table as `GameScreen(id: GameId(...))` and
    taking that `GameId` as its only constructor parameter.
    *(`P2-01-navigation.md` requirement 2, whose route table already attributes it here;
    `P1-04-persistence.md` requirement 22 for `GameId`)*

    **Stateful, because requirement 54 made it so — and that requirement said it might.**
    An earlier revision fenced this class as stateless, with the reasoning that both pieces
    of mutable state it renders live in providers — `boardProvider` (`P3-02` requirement 29)
    and `pendingSelectionProvider` (`P3-02` requirement 24) — and that *"if a later
    requirement needs a controller, promoting the class changes no call site."* Requirement
    54 is that later requirement: it performs **one async read, once, keyed to this screen's
    `id`**, and it must not be re-issued on every rebuild. That is per-instance lifecycle,
    which is what `initState` exists for. **The prediction held** — the route still builds
    it with an id and no other argument, and no call site changed.

    **The alternative considered and not taken:** a `FutureProvider.family` keyed by
    `GameId`. It would keep the class stateless and give caching for free, but no PRD
    declares such a provider, it puts a `lib/ui/board/` concern into `lib/state/` — `P3-02`'s
    territory — and a `.family` provider that is never disposed accumulates one entry per
    game ever opened. **Reversible**, and it changes only this class and requirement 54's
    mechanism.
    **Verification:** the route builds it with an id and no other argument; a widget test
    pumps it inside a `ProviderScope` with the repository, `boardProvider` and
    `currentGameProvider` overridden and nothing else.

47. **The screen is one vertical stack of three children, in this order:** the scoreboard
    strip (`P3-03`'s `ScoreboardStrip`), `BoardView`, and the how-to-play strip
    (`P3-05-how-to-play.md`). Nothing else sits between the scoreboard and the board except
    requirement 50's gap.
    *(`Game Board Design.md` → Visual Layout — "Vertical stack: **scoreboard on top, board
    below**"; → Decisions → Where does the free-choice cue live? for the third child's
    position; `P3-03` requirement 2; `P3-05` requirement 13; requirement 38 here)*
    **This stack is what requirement 54 withholds until the game has loaded**, so "the
    screen is these three children" describes the loaded state, which is every state the
    player spends time in.
    **The column is height-bounded, and no child is asked to size itself intrinsically.**
    The stack sits directly inside the screen's `Scaffold` body under requirement 50's
    padding, so every child receives a bounded vertical constraint. `GameScreen` wraps no
    child in anything that removes that bound — no `IntrinsicHeight`, no unbounded scroll
    view — and assumes nothing about the strip's height beyond `P3-03` requirement 21's
    fixed 60pt. *(Recorded because `P3-03` found that `crossAxisAlignment: stretch` inside
    an unbounded `Column` fails in Flutter; the fix is that PRD's, and this requirement is
    the host-side guarantee that the constraint it needs is actually there.)*
    **Verification:** `P3-03` requirement 2's assertion, from this side — the bottom edge of
    `ScoreboardStrip` is above the top edge of `BoardView`, which is above the top edge of
    the how-to-play strip, and no two overlap.
    **⚠ `P3-05` publishes no widget class or file for its strip**, so this requirement can
    state the child's position but cannot name its symbol. Flagged in the status block.

48. **The screen reads game state once and passes it down.** It does
    `ref.watch(boardProvider)` (`P3-02` requirement 29) and
    `ref.watch(pendingSelectionProvider)` (`P3-02` requirement 24), then:

    ```dart
    final board = ref.watch(boardProvider);
    final pending = ref.watch(pendingSelectionProvider);

    ScoreboardStrip(
      score: board.score,                                          // P1-02 req 39
      currentPlayer: board.currentPlayer,                          // P1-02 req 38
      isGameOver: board.placementState == PlacementState.gameOver, // P1-02 req 36
      playerOneLabel: GameScreen.playerOneLabel,                   // requirement 53
      tiesLabel: GameScreen.tiesLabel,
      playerTwoLabel: GameScreen.playerTwoLabel,
      onSettingsPressed: …,                                        // requirement 49
    );

    BoardView(
      board: board,
      pendingSelection: pending?.move,
      pendingDestinationQuadrant: pending?.destinationQuadrant,
      pendingDestinationState: pending?.destinationState,
      pendingFreeChoiceQuadrants: pending?.freeChoiceQuadrants,
      onCellTap: (q, c) => ref.read(pendingSelectionProvider.notifier)
                              .tapCell(Move(quadrant: q, cell: c)),
    );
    ```

    **This code runs only after requirement 54 has seeded `boardProvider`.** That is the
    precondition, and it is not decorative: read one frame earlier, `board` is
    `BoardNotifier.build()`'s `Board.newSeries()` and this snippet renders a correct-looking
    empty game in place of the player's. Requirement 54 delivers the precondition by not
    building this subtree at all until the seed lands.
    **Neither child reads a game-state provider.** `P3-03` requirement 19 is explicit that
    `ScoreboardStrip` reads neither `boardProvider` nor `pendingSelectionProvider`, and
    requirement 43 here says the same of `BoardView`. One watcher for the screen is what
    makes both testable from a plain `Board` without a container.
    *(`P3-02` requirements 24, 27, 29; `P3-03` requirement 19; `P1-02` requirements 36,
    38, 39)*
    **Verification:** pumping `GameScreen` with an overridden `boardProvider` renders the
    strip with that board's score and current player and the board with its cells; a source
    scan finds `boardProvider` and `pendingSelectionProvider` read in `game_screen.dart` and
    in no other file under `lib/ui/`.

49. **The screen owns the settings callback.** It passes
    `onSettingsPressed: () => ref.read(appNavigatorProvider).openQuickActions()` to the
    scoreboard strip. The navigator is read, never constructed.
    **This lands here because it cannot land there:** `P3-03` requirement 12 requires
    exactly one `openQuickActions()` call, while its requirement 19 closes that strip's
    provider reads to theme, haptic and audio — so the strip takes the callback and the
    screen supplies it. The haptic and the tap sound stay the strip's (its requirements 12
    and 22); this requirement supplies only the navigation.
    *(`P3-03` requirements 12, 19; `P2-01` requirements 3, 4, 14)*
    **Verification:** tapping the settings control records exactly one `openQuickActions()`
    on `P2-01` requirement 3's recording fake, and no other navigation operation.

50. **The screen's two vertical constants** — `static const double` in `game_screen.dart`,
    code not theme (requirement 27):

    | Constant | Value | Basis |
    |---|---|---|
    | `safeAreaTop` | **62pt** | the handoff's committed top padding on board screens |
    | `stripToBoardGap` | **14pt** | fenced — see below |

    **`stripToBoardGap` is fenced at 14pt, reversible.** `P3-03` requirement 21 assigns the
    gap to this screen so it is not applied twice by two widgets, and gives no number;
    nothing else states one. 14pt is chosen for symmetry with `P3-05` requirement 13's
    `margin-top: 14` below the board, so the board sits in equal vertical gutters. It is an
    input to `P3-03` requirement 17's vertical arithmetic and to `P3-05`'s OQ-7.

    **`safeAreaTop` is a total, not an addition — and this is the trap.** The handoff's 62pt
    is measured from the frame top, so a naive `SafeArea` *plus* 62pt double-counts the
    notch inset on every modern iPhone. The screen pads to `max(mediaQuery.padding.top,
    safeAreaTop)` — 62pt where the inset is smaller, the inset where it is larger, never the
    sum. **The same padding applies to requirement 54's pre-seed surface**, so nothing
    shifts vertically when the game lands.
    *(`design_handoff_game_ui/README.md` → Spacing — "Safe-area top padding 62 on board
    screens"; `Theming.md` → Decisions → Does a theme control spacing and padding?)*
    **The route does not supply this.** `P2-01` requirement 1 states that none of its
    requirements specifies what a screen contains, so the inset is the screen's.
    **Verification:** at the 402 × 874 reference frame with a zero inset, the scoreboard's
    top edge is 62pt from the frame top; with a 59pt inset it is 62pt; with a 74pt inset it
    is 74pt.

51. **The screen hosts the tap-outside-to-clear surface.** One `GestureDetector` ancestor of
    the three children, carrying `BoardKeys.clearSurface`, with **`behavior:
    HitTestBehavior.opaque`**, whose `onTap` calls
    `ref.read(pendingSelectionProvider.notifier).clear()`.

    **`opaque` is normative here for the same reason it is on `CellView`, and the default
    would be wrong.** `HitTestBehavior.deferToChild` registers a hit only where a descendant
    actually paints, which would silently narrow *"every other tap clears"* to *"every other
    tap that happens to land on painted pixels."* The cases it would drop are exactly the
    ones the collaborators assert: `P3-03` requirement 13 requires that **a tap on the
    strip's background** leaves `pendingSelectionProvider` null, and the Decision's own list
    includes the board's own margins and the gaps between quadrants — none of which paints
    anything. `opaque` makes the whole screen rectangle a hit-test target, which is what
    "one rule, uniformly applied" requires.

    **The boundary is a widget, not a rectangle:** a tap absorbed by a `CellView`
    (requirement 44) never reaches this surface; every other tap on the screen does —
    including the 3pt cell gutters, the 5pt quadrant padding, the 8pt quadrant gaps, the
    16pt board margins, the scoreboard strip's background and its counters, and the
    non-interactive how-to-play strip.
    *(`P3-02` requirement 26, which owns this rule and assigns the surface to the board
    screen; `P3-03` requirement 13, which requires the strip to carry no recognizer of its
    own so its taps reach here; `Game Board Design.md` → Decisions → Does a tap outside the
    board clear a pending move? — "any tap outside the nine quadrants clears a pending,
    unconfirmed selection… One rule, uniformly applied")*

    **A tap-catching surface alone is not sufficient, and that is not this requirement's
    gap to close.** A `GestureDetector` ancestor sees only taps no descendant recognizer
    claimed, so it misses the Decision's last case — *"opening any menu or sheet"*, which
    includes the settings button of requirement 49. `P2-01` requirement 20 closes that from
    the router side by clearing before every navigation operation. Both halves are needed;
    neither substitutes for the other.
    **Not installed over the pre-seed surface.** Requirement 54's loading state hosts no
    clear surface: there is no board, so there is nothing pending to clear, and
    `pendingSelectionProvider` is null throughout by construction.
    **Verification:** with a pending selection active, a tap clears it when it lands in a
    cell gutter, on the board's 16pt margin, **on the scoreboard strip's background**, and
    on one of the three counters; a tap on an illegal cell does not clear it; exactly one
    non-test call site of `clear()` exists in `lib/ui/`.

52. **The screen hosts the game-over overlay.** When the game is finished, `P3-04`'s result
    card is presented over the screen's content, with the finished board still visible
    behind it. `P2-01` requirement 2 routes to no such screen, so the overlay is a child of
    this one, not a route.
    *(`P3-04-game-over-rematch.md` requirement 13; `design_handoff_game_ui/README.md` → 1g,
    1h — the finished board stays visible at 60% behind the scrim; `P2-01` requirement 2)*
    **This requirement owns the hosting, not the card.** The card's contents, its two
    buttons, its own score chips and the dimming treatment are `P3-04`'s. What the *board*
    draws underneath is partly settled (requirement 14: every quadrant locked) and partly
    open — see Open Questions. Requirement 26's stacking context is what lets the card sit
    above the claim overlays.
    **A resumed game can open straight into this state.** `P1-04` stores finished games —
    the game-ending move is a confirmed move and is written like any other — so requirement
    54 can seed a board whose `placementState` is already `gameOver`. Nothing special is
    needed: the overlay's condition is read from the board, not from a transition.
    **Verification:** with a finished board, `P3-04`'s card is in the tree above
    `BoardView`, and `BoardView` is still mounted beneath it; and a game loaded by
    requirement 54 whose stored board is finished shows the card on first paint of the
    loaded state, with no intervening frame of a live-looking board.

53. **The screen owns the three scoreboard label strings** — `static const String` in
    `game_screen.dart`, passed to `ScoreboardStrip` by requirement 48:

    | Constant | Value |
    |---|---|
    | `playerOneLabel` | `'Player 1'` |
    | `tiesLabel` | `'Ties'` |
    | `playerTwoLabel` | `'Player 2'` |

    **They live here because they cannot live where they are rendered.** `P3-03`
    requirement 11 requires the three labels be *"supplied as data, never literals in the
    layout code"*, and its own verification includes a source scan of `scoreboard_strip.dart`
    finding **no user-facing display string**. `GameScreen` is the thing that passes them, so
    it is the thing that holds them. Without this requirement the strings are forbidden in
    one file and unwritten in the other.

    **The numeral is settled; the casing is not baked in.** *"The scoreboard chips read
    `PLAYER 1` and `PLAYER 2` (with `TIES` between them), not `PLAYER ONE` / `PLAYER TWO`"* —
    the numeral because every drawn screen shows it and the spelled-out form is materially
    wider in a fixed-width column. The strings passed are **title case**; the uppercase form
    is a render-time transform the strip applies when the resolved `chipLabel` style has
    `uppercase == true`, per `P3-03` requirement 11. Passing `'PLAYER 1'` here would defeat
    that and is wrong.
    *(`Game Board Design.md` → Decisions → What do the scoreboard chips read?; `P3-03`
    requirement 11)*

    **This is a label, not a name.** The players are still "Player One" and "Player Two"
    (`Game Overview.md` → Decisions → Player names). Keeping the three strings at one call
    site is what makes `P3-03` requirement 10's future swap to real opponent names a change
    here rather than a change inside the strip. **Requirement 54 makes that swap cheaper
    than it was**: `currentGameProvider` now holds the record's `opponentName`, so the data
    the future swap needs is already on this screen.
    **Verification:** a source scan of `scoreboard_strip.dart` finds no user-facing display
    string; under Neon the three chips render `PLAYER 1`, `TIES`, `PLAYER 2`; no rendered
    chip ever reads `PLAYER ONE` or `PLAYER TWO`.

54. **`GameScreen` loads the stored game its `GameId` names, and seeds the two state
    providers from it before rendering the board.**

    **The defect this closes.** `P2-01` requirement 2's route builds `GameScreen(id: …)`,
    requirement 46 takes that id as the only constructor parameter — and **until this
    requirement, nothing read it.** The screen rendered whatever `boardProvider` held, whose
    `build()` is `Board.newSeries()` (`P3-02` requirement 29). So **tapping a saved game in
    the open-games list opened a brand-new empty board**, silently, with a correct scoreboard
    header above it and no error anywhere. Every layer worked: `P1-04` wrote the game after
    every confirmed move, the list showed it, the route carried its id, and the id went
    nowhere. This is the only requirement in this PRD whose absence is a data-loss bug rather
    than a visual one.

    **The mechanism.**
    1. In `initState`, once and only once, the screen calls
       `ref.read(openGamesRepositoryProvider).readById(widget.id)` (`P1-04` requirements 21
       and 28). It is keyed to `widget.id` and is never re-issued on rebuild.
    2. **On success**, and **outside `build`**, it seeds both providers:
       ```dart
       ref.read(boardProvider.notifier).replace(game.board);       // P3-02 req 29
       ref.read(currentGameProvider.notifier).set(game);           // P3-02 req 35
       ```
       then marks itself loaded so the next build produces requirement 47's stack.
    3. **Until step 2 completes**, the screen builds a minimal surface carrying
       `BoardKeys.screenLoading` — the theme's `color.ground` under requirement 50's padding
       — and **no `ScoreboardStrip`, no `BoardView` and no clear surface**.

    **Seeding must not happen during `build`.** Riverpod forbids mutating a provider while a
    widget is building, and the natural-looking shortcut — reading the future in `build` and
    calling `replace` when it resolves inline — is exactly that mutation. Doing the write in
    the `initState` future's completion callback keeps it out of the build phase. Recorded
    because it is the mistake an implementer makes once.

    **Why the board is withheld rather than seeded-over.** This is the invalidation answer,
    and it needs stating because the obvious reading of "seed on entry" is unsafe:
    `boardProvider` is a plain `NotifierProvider`, **not `autoDispose`** (`P3-02`
    requirement 29), and `P2-01` requirement 2's child-route structure never unmounts the
    game screen. So the provider **survives leaving game A and opening game B**, still
    holding A's board. If `GameScreen` rendered `BoardView` immediately and seeded when the
    read returned, the player would see **game A's position** on game B's screen for as many
    frames as the disk took — a wrong board that looks exactly like a right one, which is
    the same failure class as the defect above and harder to notice. **Withholding the
    subtree until the seed lands makes the stale value unobservable**, which is what makes
    a non-auto-dispose provider safe here without changing its lifecycle.
    - **`replace` is a full overwrite**, so no residue of the previous game survives the
      seed. No `ref.invalidate` is needed and none is issued: invalidating would return the
      provider to `Board.newSeries()`, which is the wrong value to be holding, one frame
      earlier than necessary.
    - **The pending selection clears itself.** `replace` changes the board, which fires
      `P3-02` requirement 30's `ref.listen(boardProvider)`, which nulls
      `pendingSelectionProvider`. That is requirement 9's row 4 in that PRD. Nothing here
      clears it explicitly, and adding a second clear would create a second owner of a
      rule that has one.
    - **`currentGameProvider` is overwritten on the same path**, so the identity and the
      board can never describe two different games. Seeding one without the other is the
      failure mode this ordering exists to prevent; `P3-02` requirement 36's save reads that
      provider and would otherwise write game A's `GameId` with game B's board.

    **Why this screen owns the load, rather than the router or the storage layer.** `P2-01`
    requirement 1 states that none of its requirements specifies what a screen contains, so
    the router hands over an id and stops. `P1-04` is a repository and has no idea which game
    is on screen. `P3-02` owns the state but not the lifecycle, and says so — its
    requirement 29 declares `boardProvider` and explicitly disclaims *"seeding it from
    storage."* **The screen holding the id is the only thing that knows which game to load,
    and it is the only thing that can withhold the board while it loads.** Settled with the
    user.

    **Fenced, reversible — two failure cases this PRD decides rather than guesses.** Both
    are recorded as Open Questions because neither has a design-doc answer:
    - **`readById` returns null** — the record is gone. Reachable: `P4-02` deletes games, and
      a route can outlive one. **Default: navigate back to the main menu** via
      `ref.read(appNavigatorProvider).exitGameToMainMenu()` (`P2-01` requirement 3), showing
      nothing else. Reasoning: the alternative — an error screen — needs copy, a surface key
      and a control that nobody has specified, and there is nothing for the player to do on
      it. Returning to the list they came from is the only action available. **Reversible**;
      changes one branch.
    - **`readById` throws** — the store failed. **Default: the same path**, and the error is
      **not caught**, so it reaches `P1-06-crash-reporting.md` requirement 2's handler as an
      unhandled asynchronous error and becomes one `CrashReport`, exactly as `P3-02`
      requirement 36 treats a failed save. Nothing reads that sink in wave 1 — the same
      honest limit that requirement records.

    *(`Menus and UI.md` → Leaving a game mid-play — *"going back to the main menu doesn't
    discard anything"* — and → Decisions → When is a game written to storage?, which is what
    makes a resumable record exist to load; `P1-04-persistence.md` requirements 6, 11, 21,
    22, 28; `P3-02-move-input.md` requirements 29, 30, 35, 36; `P2-01-navigation.md`
    requirements 1, 2, 3.)*
    **Verification**, with an overridden `openGamesRepositoryProvider`:
    - (a) **the defect test.** `readById` returns a `StoredGame` whose board has moves
      played; after the future resolves, `boardProvider` is `identical()` to that board and
      the rendered cells match it. **Run with `boardProvider` left at its default**, so a
      build that never seeds fails here rather than passing on a lucky override — this is the
      assertion the whole requirement exists for;
    - (b) `currentGameProvider` holds the same record — same `GameId`, `opponentName`,
      `createdAt` — so `P3-02` requirement 36's save has its five fields;
    - (c) **the stale-board test.** Seed `boardProvider` with game A's board, then pump
      `GameScreen(id: B)` against a repository whose `readById` completes on a controlled
      future: **before** it completes, `BoardKeys.screenLoading` is present and no
      `BoardKeys.quadrant(0)` and no `BoardKeys.clearSurface` are in the tree; after it
      completes, the rendered board is B's and A's position was never painted;
    - (d) `readById` is called exactly once across an arbitrary number of rebuilds, and with
      `widget.id`;
    - (e) a pending selection set before the seed is null after it, with no explicit clear
      call in `game_screen.dart` (source scan) — `P3-02` requirement 30 does it;
    - (f) `readById` returning null records exactly one `exitGameToMainMenu()` on `P2-01`
      requirement 3's recording fake, and no board is rendered;
    - (g) `readById` throwing records the same navigation, and a source scan of
      `game_screen.dart` finds no `catch`, no `.catchError` and no `onError` around it;
    - (h) a stored board whose `placementState` is `gameOver` renders requirement 52's
      overlay on the first painted frame of the loaded state.

### Design notes — constraints on how the above is built, not separately assertable

These five keep their requirement numbers because inbound citations bind to them. Each
states a property of the result that no test distinguishes; each is a constraint on
judgment and a brief for the by-eye review requirement 39 names, not a deliverable with a
check.

- **Requirement 7 — the big board reads heavier than the small boards.** Both grids are the
  same blue at the same 1.5pt; "heavier" is the sum of glow, opacity and inset. No
  assertion separates a correct hierarchy from an inverted one.
- **Requirement 18 — the three highlights are mutually distinguishable.** Requirement 45's
  keys prove three *different widgets* are present; nothing proves a player can tell them
  apart.
- **Requirement 24 — dashed means provisional, solid means committed.** A dash pattern is a
  paint property, unassertable without goldens — and requirement 23's third row is now a
  stated exception to the rule.
- **Requirement 30 — every theme keeps the highlights legible.** Unfalsifiable as written;
  `P1-03` → Open Questions carries the question of what form this contract could take.
- **Requirement 31 — the board is readable with animations off.** `P2-04-animations.md`
  owns the toggle; that the *static* board carries every state is a property of this PRD's
  design — no requirement here specifies motion, and under that PRD's marker-only scope none
  could — and reviewing it is a by-eye check.

## Out of Scope

Named here so the boundary is explicit. Each is specified elsewhere; do not specify it
here.

- **What a tap means** — select, confirm, reselect, illegal taps doing nothing, the preview
  `applyMove`, the `clear()` implementation, and the haptic on every valid click:
  `P3-02-move-input.md`. This PRD publishes the tap surface (requirement 44), hosts the
  clear surface (requirement 51) and draws the pending selection; it decides none of the
  semantics and never computes a destination or a previewed open set. Focus/hover styling
  (`surfaces.focusRing`) is input-state styling and belongs there too.
- **The state providers themselves** — `boardProvider`, `pendingSelectionProvider` and
  `currentGameProvider`, their types and their mutators: `P3-02-move-input.md` requirements
  24, 29 and 35. Requirement 54 **calls** `replace` and `set`; it declares neither, and
  nothing under `lib/ui/board/` may add a provider or a notifier member.
- **The storage layer** — the repository, `StoredGame`'s shape, `GameId` minting, the Hive
  box, ordering, the 3-game cap, and **writing after a confirmed move**:
  `P1-04-persistence.md`, whose confirmed-move write is claimed by `P3-02` requirement 36.
  **This PRD reads once, on entry, and never writes.** A source scan of `lib/ui/board/`
  finds `readById` and no other repository call.
- **Resetting the game** — the rematch's `startNextGame()` and its own storage write:
  `P3-04-game-over-rematch.md` requirements 6 and 9. It calls the same `replace` requirement
  54 does, from the other end of the game's life.
- **The scoreboard strip's contents and rendering** — the three counters, the turn
  highlight, the casing transform, the settings button's own haptic and tap sound, and its
  internal layout constants: `P3-03-scoreboard-turn-indicator.md`. This PRD composes the
  strip (requirement 47), feeds it (requirements 48, 49) and holds the three label strings
  it may not hold itself (requirement 53). The scoreboard's name highlight is the
  **permanent** whose-turn affordance, since the banner that would have duplicated it is not
  built.
- **The how-to-play strip's contents** — the free-choice text cue, the two-tap hint, the
  legend and the ring explanations: `P3-05-how-to-play.md`. This PRD composes it and holds
  the gap above it.
- **The game-over card** — its contents, buttons, chips and the dimming treatment:
  `P3-04-game-over-rematch.md`. Requirement 52 hosts it and nothing more.
- **Routes, the router, and clearing on navigation** — `P2-01-navigation.md`. This PRD reads
  `appNavigatorProvider`; it never imports `go_router`, and `P2-01` requirement 1's scan
  enforces that.
- **Crash reporting** — the sink, the handlers and whether a recovered error ever reports:
  `P1-06-crash-reporting.md`. Requirement 54's throwing case relies on its requirement 2
  handler existing and reports nothing itself.
- **The theme mechanism** — the schema, YAML loading, merge-over-Neon and authoring
  `neon.yaml`: `P1-03-theme-system.md`.
- **Legal-move computation and all rules** — `P1-02-engine-rules.md`.
- **All motion** — `P2-04-animations.md`. **Nothing in this PRD animates, and that is now
  settled rather than deferred.** Animation scope is the player's marker only (its
  requirement 2, settled by the user), so the last-move ring, the active-quadrant highlight,
  the claim and cat overlays and the pending preview are all **static treatments in their
  final form** — requirements 19, 21 and 23 are the whole of what those highlights do. The
  earlier note that whether they animate *"is unanswered and sits with the user"* is
  withdrawn; it is answered.
- **Sound** — the pending selection deliberately has no sound of its own
  (`Game Board Design.md` → Move Input → Sound); playback is `P2-02-audio.md`.
- **The app-root Dynamic Type clamp** — unowned across `P3-03`, `P3-05` and `P4-01`; this
  PRD does not claim it either. It wants one app-level owner, not four component clamps.
- **Anything from `Alternative Game Styles.md`** — a declared parking-lot doc.

## Open Questions

### Blocking — needs the user

1. **The forced ring and the destination ring are geometrically identical and collide.**
   Requirement 9's forced ring and requirement 23's destination ring are both 2pt, offset
   −3, radius 12, and both sit at z-index 3 (requirement 25), differing only in solid vs.
   dashed. They land on the **same quadrant** whenever the selected cell's index equals its
   own quadrant's index *and* that send still resolves to a forced state — roughly one
   selection in nine, including the centre-cell-in-centre-quadrant case the handoff itself
   draws on screen 2d. Which one wins, whether they compose, or whether the destination
   ring insets further is unspecified. **Narrowed, not solved,** by the self-claiming-preview
   Decision: the subset where the move *claims* its own target now takes requirement 23's
   third row and never draws a destination ring. The rest still collide.

2. **The last-move ring survives the claim veil but the mark it circles does not.**
   Requirement 25 lifts the last-move ring to z4, above the z2 overlays, but the **cell**
   and its mark stay at z0 — beneath the `veilClaimed` or `veilCat` of requirements 11–12.
   Since the move that completes a small board *is* by definition the last move, this fires
   **after every claim**: the ring floats over a quadrant-sized claim glyph while the mark
   it points at is underneath it. That defeats the stated purpose of the highlight
   (`Game Board Design.md` → Last Move Highlight, *"readable at a quick glance"*), and no
   test catches it — requirement 10's verification covers only the `veilLocked` case, and
   requirement 25's asserts stack order, which is already correct.

3. **What does the preview show when the selected move would end the game?** The
   self-claiming case is decided — every still-open quadrant is highlighted — but a
   game-ending move publishes the same null destination and that Decision does not reach
   it: there is no next move, so "the opponent may play anywhere still open" is false.
   Requirement 23's fourth row draws no big-board treatment, which is the only claim that
   is not wrong, but showing the player nothing at the exact moment they are about to win
   may not be what is wanted — a distinct "this ends it" treatment is a live alternative.
   Reachable on any board where a selected cell would complete a third quadrant in a line or
   fill the last open quadrant.

### New with requirement 54 — needs the user, not blocking

4. **What should the player see while a stored game loads?** Requirement 54 renders a bare
   `color.ground` surface with the screen's padding and nothing else, on the reasoning that
   a local Hive read of one small record is fast enough that a spinner would flash and read
   as a stutter — and that no doc, screen or token specifies a loading treatment anywhere in
   this app. `design_handoff_game_ui/` draws no loading state on any of its screens. If a
   spinner, a skeleton board or the scoreboard-without-a-board is wanted, it needs a
   treatment and probably a theme key. **Not blocking:** something legal renders today.

5. **What should happen when the game a route names is gone, or cannot be read?**
   Requirement 54 defaults both cases to `exitGameToMainMenu()` with no message. Reachable
   for real: `P4-02` deletes games, and a route can name one that no longer exists. The
   alternatives are an error surface with copy and a control, or a silent fallback to a new
   game in that slot — the second being *exactly the defect requirement 54 exists to close*,
   so it is not proposed. **Silently returning to the menu is honest but tells the player
   nothing about why**, which for a deleted game is arguably fine and for a storage failure
   is arguably not. `Menus and UI.md` describes no failure surface anywhere.

### Relieved, not closed — still with the user

6. **What happens at frame widths other than 402pt?** Every number in requirement 4 is
   committed at a 402 × 874 reference frame. Whether the board scales proportionally, holds
   fixed point values and re-centers, or caps at a maximum width is unstated — and if it
   scales, whether the four mark sizes scale with it. Dynamic Type is off *(`Menus and
   UI.md` → Decisions)*, so nothing else moves these numbers.

   **The arithmetic improved and is now known.** The turn banner is not built, and `P3-05`
   requirements 11 and 14 compute the effect: the banner's block returns **≈70pt** while the
   cue costs **27pt exactly**, for **net 43pt returned** to every board screen — both sides
   code constants now, so a fixed number rather than an estimate. With requirement 50's two
   constants supplied, the whole column closes at the reference frame: 874 − 62 − ~48 − 370
   − 56 − 14 ≈ **324pt** of remainder.

   **That relieves the contention; it does not close the question.** iPhone SE is 375 × 667
   — **207pt shorter** than the reference frame — so 43pt covers roughly a fifth of the
   deficit. iPad remains a declared second target. What gives up height first is still the
   user's call, and this is **one shared question** with `P3-05` → OQ-7, not two.
   **`GameScreen` now holds the sum** (requirements 47, 50), so this PRD is where a scaling
   rule would land when one exists.

   *(This item was numbered 4 before requirement 54 added two questions above it; it is
   renumbered because nothing cites it by number. Items 1–3 keep their numbers.)*

### Fenced by this PRD — reversible, flagged so a ruling is cheap

- **Veil and border composition** (requirement 14) — finished subsumes locked. Changes
  `QuadrantView` only.
- **The game-over preview draws no big-board treatment** (requirement 23) — the fence behind
  Blocking 3. Changes one branch.
- **What a mark size means for a non-glyph mark** (requirement 17) — the box side, art
  fitted, weight ignored. Changes `MarkView` only; observationally free while Neon is the
  only theme.
- **Grid lines as four positioned boxes, not `CustomPaint`** (requirement 34) — changes
  `QuadrantGridLines`'s internals only.
- **`BoardView` takes pending scalars rather than `PendingSelection` or a provider**
  (requirement 43) — changes one constructor and `P3-02` requirement 27's call site.
- **`GameScreen` loads in `initState` rather than through a `FutureProvider.family`**
  (requirements 46, 54) — changes this class only; the family alternative and why it was not
  taken are recorded in requirement 46.
- **The board subtree is withheld until the seed lands** (requirement 54) — the alternative
  is rendering immediately and accepting stale frames from a non-auto-dispose provider,
  which is a wrong-board defect rather than a slower one. Not really reversible; recorded
  because it looks like a free optimisation to remove.
- **Both load-failure cases exit to the main menu** (requirement 54) — Blocking 5. Changes
  one branch.
- **`stripToBoardGap` = 14pt** (requirement 50) — a number nothing states, chosen for
  symmetry with the 14pt below the board. Changes one constant, and `P3-03` requirement
  17's and `P3-05`'s OQ-7 arithmetic with it.
- **`safeAreaTop` is a max, not a sum** (requirement 50) — the reading that avoids
  double-counting the notch. Changes one expression.
- **Addressability is keys, not widget types** (requirements 40, 45) — expensive now that
  `P3-02` has bound its OQ-7 to `cellPlayable`.

### Contradictions and gaps between documents — flagged, not resolved

- **`P3-05-how-to-play.md` names no widget class and no file.** Requirement 47 composes its
  strip as `GameScreen`'s third child and cannot name the symbol it is composing. Every
  other collaborator publishes one — `ScoreboardStrip`, `BoardView`, `AppNavigator`. Needs
  routing, not a user decision.
- **The previewed free choice is provisional but drawn solid**, the one place requirement
  24's *dashed = provisional* rule breaks. It follows from the Decision, whose stated reason
  is that preview and result should look consistent. Recorded because a reader who knows
  requirement 24 will read the third row as a bug. A dashed variant would need a theme key
  `P1-03` does not have.
- **Grid-line width is the one bare number the guard cannot see.** It stays a theme key by
  explicit choice while the gaps beside it became code constants — but `Theming.md` →
  Decisions is explicit that the guard *"cannot catch a hardcoded gap"*, and
  `board.gridLineWidth` is a gap-shaped number living in the theme. A theme author who sets
  it and a widget that hardcodes 1.5 will both look correct forever. Same for
  `board.gridLineInsetPercent`.
- **The handoff contradicts itself on the pending-move preview** — *"Preview visuals still
  to be designed"* against a fully specified *Cell states* and screen 2d. This PRD builds
  from the specified version, and `P1-03` requirement 15 has since promoted those values to
  `required` keys. Also carried by `P3-02` → OQ-3. The handoff draws **no** version of
  requirement 23's third row — that preview is a Decision with no mock behind it.
- **`Game Board Design.md`'s visual hedges still have no Decision behind them.** Its five
  Decisions cover the cue's home, the tap-outside rule, the self-claiming preview, the chip
  labels and the non-board haptic — not the treatments this PRD draws. The claimed-quadrant
  mark, the locked treatment and the free-choice highlight are still hedges, settled here
  only because the approved handoff drew a concrete answer.
- **No design doc describes opening a saved game as a *screen* behaviour.** `Menus and
  UI.md` covers leaving one (*"doesn't discard anything"*) and `P1-04` covers storing one,
  but nothing on either side says what the screen does when it arrives. Requirement 54 is
  derived from the two halves plus the user's settlement of its ownership, and it is the
  only requirement in this PRD with no direct design-doc sentence behind its mechanism.

### Closed since the last revision — recorded so they are not reopened

- **`GameScreen` renders a new game when asked for a saved one.** Closed: requirement 54.
  It was not previously listed as a question because no PRD had noticed the parameter was
  unread.
- **The provider holding the on-screen game's identity had no owner.** Closed: `P3-02`
  requirement 35's `currentGameProvider`, declared there because `lib/state/` is that PRD's
  layer and its requirement 36's save is the only thing that *reads* it. Requirement 54
  writes it. Neither this PRD's load nor that PRD's save closes without it.
- **`P3-02` had not published the previewed still-open quadrant set.** Closed: its
  requirement 23's `freeChoiceQuadrants`, derived in its requirement 3 and passed at its
  requirement 27. Requirement 23's third row has its data source.
- **`P3-02`'s `BoardNotifier` published no way to seed a board.** Closed: its requirement
  29's `replace(Board)`, which requirement 54 and `P3-04` requirement 6 both call.
- **Whether the last-move and active-quadrant highlights animate.** Closed: they do not.
  Animation scope is marker-only, settled by the user (`P2-04` requirement 2). Requirements
  19 and 21 draw the final static treatments and this PRD's Out of Scope no longer defers
  anything conditional to that PRD.
- **`GameScreen` has no owner.** Closed: it is this PRD's, requirements 46–54. `P3-03`'s
  *Needs an assignment* section resolves with it.
- **The three scoreboard label strings are unowned.** Closed: requirement 53. They were
  forbidden in `scoreboard_strip.dart` by `P3-03` requirement 11 and written nowhere.
- **What the preview shows when the move claims its own send target.** Settled: every
  still-open quadrant is highlighted. Requirement 23's third row builds it; `P3-02` OQ-2
  closes with it. The `gameOver` sub-case is Blocking 3.
- **Where requirement 38's 16pt padding comes from.** Settled: code, not theme.
- **Where the free-choice text cue lives, and whether a turn banner is built.** Settled: the
  strip below the board, and the banner is not built.

### Carried from elsewhere — recorded so they are not answered by accident

- **What does the board draw once the game is over?** The **playability half is settled**:
  `gameOver` makes every quadrant locked (requirement 14). What remains open is whether the
  last-move ring persists behind the result card and whether the veils change under it.
  `P3-04` owns the card; requirement 52 only hosts it. `P3-05` → OQ-9 asks the same of the
  strip.
- **Who stamps `updatedAt` on a save?** `P3-02` → OQ-10, routed to `P1-04`. Not this PRD's —
  requirement 54 reads a record and writes none — but it shares the record this screen holds.
- **Which values, concretely, does Classic Red vs Blue override?** *(`Theming.md` → Open
  Questions; owned by `P5-01-classic-theme.md`.)* The first real test of requirement 30 —
  and `P1-03` notes Classic has a near-white ground while inheriting veils and glows tuned
  for a near-black one, which lands directly on this board.
- **How do the counters read past 99?** *(`P3-03` → Open Questions.)* Not this PRD's, but
  requirement 53's strings and requirement 50's arithmetic both sit next to it: whatever
  gives at three digits changes the strip's fixed 60pt height, which is a term in the
  vertical budget requirement 47 composes.
