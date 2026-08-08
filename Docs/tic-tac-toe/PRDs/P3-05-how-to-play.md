**Build-readiness: 90** — actionability 19/20 · verifiability 18/20 · decision completeness
16/20 · interface precision 19/20 · self-containment 18/20. *(Author's estimate. An independent
re-grade follows and governs.)*
**Why 90:** every requirement is buildable except two sentences. Req 8's sending-rule copy and
req 10's cue phrasing are **copy-blocked, not under-specified** — host, condition, precedence,
placement, theme key and vocabulary are settled for both, and both are explicitly marked *leave
unbuilt*. They are one ask, **OQ-1**, and the only thing standing between this PRD and a build.
What holds the remaining points: six reversible defaults a ruling would confirm cheaply
(**OQ-3, 4, 6, 9, 10, 14**), and **OQ-7**'s sub-402pt budget, now quantified exactly but still
with the user.
*Changed since the 89: the strip publishes `HowToPlayStrip` and `HowToPlayKeys` (requirements
25–26), closing the hole `P3-01` req 47 flagged; requirement 13 hands the board-to-strip gap to
`GameScreen` rather than applying it here, which would have double-counted it; and OQ-7's
arithmetic is corrected for `max`-not-sum safe-area insets.*

# PRD: How To Play — The On-Board Legend and Hint

> **Status:** Draft · Source docs read: `Menus and UI.md`, `Game Board Design.md`,
> `Game Overview.md`, `Theming.md`, `Rules.md`, `Tech Design.md`, `Animations.md`,
> `roadmap.md`, plus the read-only reference asset `design_handoff_game_ui/`
> (`README.md`, `design-files/Tic Tac Toe Extreme - Screens.dc.html`, `neon.theme.json`).
> Sibling PRDs read for boundary, key paths and symbols: `P1-02-engine-rules.md`,
> `P1-03-theme-system.md` (schemaVersion **3**), `P1-05-theme-guard-test.md`,
> `P3-01-board-rendering.md` (*Board Rendering and the Game Screen*), `P3-02-move-input.md`,
> `P3-03-scoreboard-turn-indicator.md`, `P3-04-game-over-rematch.md`.
> `Alternative Game Styles.md` is a declared parking-lot doc and was read only to confirm
> it is out of scope — no requirement here comes from it.

> **Wave:** P3 — the game-screen wave, alongside `P3-01-board-rendering.md`,
> `P3-02-move-input.md`, `P3-03-scoreboard-turn-indicator.md` and
> `P3-04-game-over-rematch.md`.
> **Depends on:** `P1-02-engine-rules.md` (its `placementState`, `lastMove` accessors),
> `P3-02-move-input.md` (owns the pending selection this strip reads a boolean from, and the
> outside-the-quadrants rule requirement 16 defers to), `P1-03-theme-system.md` (its
> requirement 15 publishes `surfaces.legend.*`), `P3-01-board-rendering.md` (**composes this
> strip** in its `GameScreen` requirement 47, supplies its constructor arguments in
> requirement 48, owns the board-to-strip gap in requirement 50, and owns the quadrant and
> cell treatments these swatches stand for).
> **Depended on by:** nothing. This is a leaf — it is composed, and composes nothing.
> Within a wave, work is parallel-safe; a lower wave ships first.

> **Note on source status:** `Menus and UI.md` → Decisions → *How to play — the on-board
> legend and hint* is the decision that scopes this feature. `Game Board Design.md` carries
> the house banner *"Nothing here is settled"* and, until recently, had **no `## Decisions`
> section at all** — `roadmap.md` records the gap, and the siblings written before it treat
> that doc's body as settled anyway. **That section now exists**, and requirements 10 and 16
> are sourced to it. The rest of that doc's body is still treated as settled on the same
> grounds its siblings use: the approved handoff was drawn from it, and `Tech Design.md` →
> What the Design Docs Already Imply treats its layout statements as locked. Where it hedges,
> this PRD flags rather than resolves.

---

## Two rules this PRD is written under

Both were settled elsewhere and both touch nearly every requirement, so they are stated once
here rather than re-argued at each.

### Vocabulary

> **Player-facing text says "board". The internal term stays "quadrant."** "Board" is what the
> player reads; "quadrant" is what the docs, the PRDs and the code use.

*(`Game Overview.md` → Terminology (working vocabulary), which now marks which terms are
internal-only. The reasoning recorded with it: "board" is the more natural word for a child,
and children are a stated target audience — `Game Overview.md` → Target Audience & Platform.)*

**The cost, accepted with the decision and landing squarely in this strip:** "board" now means
both the big 3x3 grid *and* each of the nine small ones, so player-facing copy has to
disambiguate by context. This strip is where that shows up — requirement 10's cue must read
unmistakably as *one of the nine*, not as the whole grid. The approved copy already juggles
three player-facing nouns: **square** for a cell (requirement 5), **board** for a quadrant
(requirements 7 and 10), and the big board implied but never named. That is a **copy
constraint, not a terminology question**, and requirements 8 and 10's unwritten sentences are
where it has to be solved — see **OQ-1**.

### What the theme owns, and what the code owns

> **Themes do not control spacing and padding. Gaps and layout numbers are fixed in the code.**

*(`Theming.md` → Decisions → Does a theme control spacing and padding? The reasoning is the one
`P1-05-theme-guard-test.md` requirement 4(c) had already surfaced: a regex cannot tell a themed
gap from an incidental one, so a `padding` section would have been a rule nothing verifies.)*

The line, in the form `P1-03-theme-system.md` now phrases it:

> **A theme controls the drawn geometry of a thing itself — stroke width, glyph size, corner
> radius, glow spread. Code controls where things sit relative to one another.**

For this strip that splits cleanly, and requirement 19 marks every value on one side or the
other:

| Theme reads | Code constants |
|---|---|
| swatch dimensions, corner radii, border widths, glow spreads, every color, every type size and weight | the gaps `6` / `8` / `9` / `16`, and `padding-top: 18` / `22` |

Requirement 18 states the exception this creates rather than forbidding all hardcoded values,
because without it that requirement would forbid the only legal implementation of requirement
19's own layout numbers.

## Problem

The game never explains itself. Its central mechanic — *the cell you play sends your
opponent to the matching quadrant* (`Game Overview.md` → Core Concept) — is the whole of
the strategy and, per `Menus and UI.md` → Decisions → *How to play*, **"the hardest thing
in the game to explain"**. Nothing in the shipped product says it. There is no tutorial, no
rules screen in this version's menu (`Menus and UI.md` → Open Questions lists Rules/How to
Play only as a *future* menu item), and the board itself is silent: a player handed the
phone sees dimmed quadrants, a glowing one, and a ring around somebody else's mark, with
nothing telling them what any of that means or why their first tap did not place a mark.

Two facts make that fatal rather than merely unfriendly. **Kids are a stated target
audience** (`Game Overview.md` → Target Audience & Platform), and `Game Board Design.md` →
Move Input → *Why this is more than a safety net* says the cell→quadrant mapping is
otherwise learned "the hard way." And the game's only feedback for a wrong tap is
*nothing at all* — `Game Board Design.md` → Taps outside the legal quadrant: no shake, no
flash, no error message, and no haptic, because "the lack of a buzz *is* the feedback."
A player who does not already understand which quadrants are locked gets silence, and
silence teaches nothing.

The two-tap move compounds it. A first tap that visibly does not place a mark reads as a
failure, not a feature, to anyone who has not been told the first tap is a preview.

There is a fourth thing the board cannot say. When a player is sent to a dead quadrant they
get a **free choice of any open one** (`Rules.md` → Edge Cases), and the board signals that by
lighting up to nine quadrants at once — which `Game Board Design.md` warns "risks looking like
noise." Without words, a suddenly-open board is indistinguishable from a bug.

## Goal

`lib/ui/board/` ships a `HowToPlayStrip` that sits below the board and changes what it says
with what the board is doing, so a first-time player — including a child — can learn what the
board is telling them and how to move **without leaving the board**: no tutorial, no rules
screen, nobody sitting beside them. Across its states it names the quadrant states, says in
words what each ring means, states in words when the player has a free choice, says explicitly
that the first tap previews and the second tap plays, and states the sending rule itself. It
is the only explanatory surface on the game screen — nothing is added above the board. It
reads no game-state provider, registers no gesture, resolves every drawn value from a `P1-03`
key and every gap from a named constant, stays readable with animations off, and costs the
board none of its 81-cells-visible-no-zoom budget.

## Interface this PRD publishes and consumes

### What it publishes

> **Author judgment — fenced, because no design doc names a widget.** Reversible, and stated
> so `GameScreen` composes a symbol rather than describing this strip in prose.
> `P3-01-board-rendering.md` requirement 47 flagged its absence; this closes it.
>
> ```dart
> // lib/ui/board/how_to_play_strip.dart
> class HowToPlayStrip extends ConsumerWidget {
>   const HowToPlayStrip({
>     super.key,
>     required this.placementState,       // PlacementState — P1-02 req 36
>     required this.hasPendingSelection,  // pending != null — requirement 1, row S3
>     required this.hasLastMove,          // board.lastMove != null — P1-02 req 40, requirement 12
>   });
>   // build(context, ref) reads activeThemeProvider and nothing else.
> }
> ```
>
> **Three booleans-and-an-enum, not the objects behind them.** The strip renders no value
> *from* a `Move` — requirements 1 and 12 branch only on whether a pending selection and a
> last move **exist**. Taking `Move?` parameters it never dereferences would widen the surface
> past what the widget uses and would make every test construct a `Move` to reach a branch.
> Deriving the booleans at the call site follows the pattern `P3-01` requirement 48 already
> uses for `isGameOver`.
>
> **`ConsumerWidget`, not `StatelessWidget`,** for the same reason `P3-03` requirement 19
> gives: requirement 18 requires every drawn value to come from the active theme, and the
> published accessor is a Riverpod provider (`P1-03` req 24), so a `StatelessWidget` would need
> an unlisted `theme` parameter and break the call-site contract this fence exists to fix.
>
> **It reads exactly one provider.** `activeThemeProvider`. Notably **not** `boardProvider`,
> **not** `pendingSelectionProvider`, **not** `appNavigatorProvider`, and no haptic or audio
> layer — requirement 16 makes this widget non-interactive, so it has no tap handler in which
> to read one.

### What it consumes

`GameScreen` (`P3-01-board-rendering.md` requirements 46–48) reads game state once and passes
values down. This strip's three arguments come from that single read:

```dart
HowToPlayStrip(
  placementState: board.placementState,      // P1-02 req 36
  hasPendingSelection: pending != null,      // P3-02 req 24
  hasLastMove: board.lastMove != null,       // P1-02 req 40
)
```

**Gate on `placementState`, never on `activeQuadrant == null`.** `P1-02-engine-rules.md`
requirement 36 states `activeQuadrant` is null in **both** `freeChoice` and `gameOver`, and
warns that a consumer branching on nullity alone conflates them. `P3-01-board-rendering.md`
requirement 14 takes the same gate. This strip would otherwise render its free-choice content
over a finished game — and requirement 10's cue is a direct consequence of gating this way:
free choice is a first-class board state here, so a block keyed to it drops straight in.

**Theme keys read:** `surfaces.legend.*` — requirements 18 and 19.

## Requirements

### The strip and its content blocks

1. **The strip's content is state-dependent** — what it says changes with what the board is
   doing. It is not a fixed block of text.

   | # | Condition | Content | Drawn as |
   |---|---|---|---|
   | **C** | `placementState == freeChoice` and `!hasPendingSelection` | requirement 10's free-choice cue | `1d`, relocated from its banner |
   | **S3** | `hasPendingSelection` | requirement 9's pair | `2d` |
   | **S1** | `!hasPendingSelection` and `placementState == freeChoice` | requirement 2's legend **and** requirement 5's hint | `1d` |
   | **S2** | `!hasPendingSelection` and `placementState == forced` | requirement 7's pair | `1e` |
   | — | `placementState == gameOver` | nothing — requirement 20 | — |

   **S1, S2 and S3 are mutually exclusive; exactly one renders and the other two are absent
   from the widget tree.** **C is not one of them** — it is an independent block that
   **coexists with S1**, so a free-choice turn shows the cue, the hint and the legend
   together.

   **Precedence, stated the way `2d`-over-`1e` is:**
   - **S3 beats S2.** `2d` is drawn on the same shell as `1e` (*"Same board shell as 1e"*), so
     a pending selection inside a forced quadrant satisfies S2's condition too — and the
     drawing resolves it by showing only the pending pair.
   - **S3 suppresses C.** Taking a first tap during a free-choice turn hides the cue rather
     than stacking it above the pending pair. On `2d` the banner drops its mode cue and
     switches wholly to the provisional voice; that is the only evidence in the drawings of
     what the cue does while a selection is held, and this follows it.
   - **C never renders in `forced`.** The forced-mode equivalent is already carried in words by
     requirement 7's second line, *"The only board you can play in right now."* — so nothing is
     lost, and a second forced-mode cue would say the same thing twice.

   *Source: `Menus and UI.md` → Decisions → How to play — the on-board legend and hint
   ("**The game explains its own central mechanic — this is now in scope to build out.** The
   approved handoff makes this strip **state-dependent** — what it says changes with what the
   board is doing"), which then enumerates `1d`, `1e` and `2d`;
   `design_handoff_game_ui/README.md` → 2d ("Same board shell as 1e") and → 1d, 1e, 2d for the
   banner's per-state voice; `design-files/… Screens.dc.html` → `#2d`, whose bottom strip
   carries requirement 9's pair and none of requirement 7's, and whose banner carries no mode
   cue.*
   **Testable:** a table-driven widget test constructs `HowToPlayStrip` for each of the five
   rows and asserts, for each, that its own strings are present and every other row's are
   absent — except that the S1 case asserts C's cue is **present** alongside. A sixth case,
   `placementState: forced` with `hasPendingSelection: true`, asserts requirement 9's pair and
   neither requirement 7's nor C's. All six are plain constructor calls; no provider override
   is needed to reach any branch.
   **Reversible, two ways:** S3-over-S2 is read off the drawing, not stated in any doc
   (*reverses to:* both pairs stacked). S3-suppresses-C is inferred from the banner's behavior
   in an element that is no longer built (*reverses to:* the cue persisting through S3, which
   is arguable — free choice is still true while the selection is held, and the player may
   still reselect any open quadrant). See **OQ-3**.

2. **In S1 the strip renders a legend of quadrant states carrying exactly three entries —
   `Open`, `Locked`, `Cat game` — each a swatch followed by its label**, in that order.
   *Source: `Menus and UI.md` → Decisions → How to play (`1d` — "the legend (Open · Locked ·
   Cat game)"); `design_handoff_game_ui/README.md` → 1d ("Legend pinned to the bottom: Open
   (blue outline) · Locked (dim swatch) · Cat game (Ø)"); `design-files/… Screens.dc.html` →
   `#1d`.*
   **Testable:** in S1 the strip renders three entries with those three labels in that order,
   each preceded by a swatch widget, addressable by requirement 26's keys.

3. **The swatches are legend-specific tokens drawn to requirement 19's specs — not the
   board's own treatments reused at small size.** This is the normative reading, and it
   contradicts the reading a previous revision took.
   Every drawn swatch is a deliberate simplification of the state it stands for: `Open` is an
   11×11 inset border with **no glow**, where `P3-01-board-rendering.md` requirement 8's
   available quadrant carries a 20px glow at radius 9; `Locked` is a **solid `#1b1e2c`
   fill**, where requirement 10 applies a 50% veil *over live content*; `Cat game` is a bare
   10pt `Ø` with **no box at all**, where requirement 12 applies a 0.76 veil plus a `CAT`
   caption. The ring swatches are flattened the same way — a 2pt border with a reduced glow
   and no inset shadow.
   That the swatches are their own tokens is also why `surfaces.legend.swatchStyle` is a
   separate per-state map rather than an alias onto the board's keys — see requirement 18.
   *Source: `design-files/… Screens.dc.html` → `#1d`, `#1e`, `#2d` (the swatch declarations);
   `design_handoff_game_ui/README.md` → Fidelity ("Colors, type, spacing, radii and glow
   values are final and exact. Recreate pixel-for-pixel"); the board treatments they simplify
   are `P3-01-board-rendering.md` reqs 8, 10, 12.*
   **Reversible:** the alternative — that a swatch must reproduce its board treatment — is
   defensible from `Game Board Design.md` → Everything Here Is Theme-Driven, but it makes the
   `Locked` swatch a 50% veil over nothing, a near-invisible grey patch, and no drawn screen
   shows it. *Reverses to:* swatches rendered by the board's own state widgets at 11pt. See
   **OQ-6**.

4. **A legend swatch and the board state it stands for must not drift — and the test asserts
   the *mapping*, not string equality.** The internal key vocabulary and the player-facing
   label vocabulary are allowed to differ; that is the general rule, not an exception granted
   to one entry.

   | Player-facing label (req 2) | Internal key (`P3-01` req 40) | Swatch key (req 18) |
   |---|---|---|
   | `Open` | `available` | `swatchStyle.open` |
   | `Locked` | `locked` | `swatchStyle.locked` |
   | `Cat game` | `catGame` | `swatchStyle.catGame` |

   The `Open` → `available` row is the same internal/player-facing split ratified for *board*
   vs *quadrant*, one layer down: `P3-01-board-rendering.md` requirement 8 renamed the
   handoff's **Open** state to **available** internally while the drawn label stayed **Open**.
   A test asserting equality would have to special-case that row, and would break again the
   next time either vocabulary moved.
   *Source: `P3-01-board-rendering.md` → Out of Scope ("Its swatches read the same requirement
   28 keys, so the two must not drift") and its requirement 40's `BoardKeys` vocabulary;
   `Game Overview.md` → Terminology, for the general rule; `Theming.md` → Architectural Rule.*
   **Testable:** a test walks the mapping table above and asserts, for each row, that the
   internal key resolves in `BoardKeys`, that the swatch key resolves in the theme, and that
   the rendered label equals the player-facing string. Adding a board state without a mapping
   entry fails it; renaming any of the three columns without updating the table fails it.

5. **In S1 the strip renders the hint text verbatim, on two lines:**

   > Tap a square to see where it sends them.
   > Tap it again to play it.

   This is the only statement anywhere in the product that the two-tap mechanic exists.
   *Source: `Menus and UI.md` → Decisions → How to play (quotes exactly this text under
   `1d`); `design_handoff_game_ui/README.md` → 1d; `design-files/… Screens.dc.html` → `#1d`,
   which draws it centered with an explicit `<br>` between the sentences.*
   **Testable:** in S1 the rendered hint equals those two sentences, in that order, broken
   across two lines, character for character.

6. **The hint carries both halves of the mechanic** — that the first tap previews the
   destination, and that a second tap on the same square commits. Neither half may be dropped
   if the copy is ever revised: the preview half is what teaches the sending rule, and the
   "tap it again" half is what stops a first tap reading as a failure.
   *Source: `Game Overview.md` → How a Move Is Made ("Moves are **two taps — select, then
   confirm**"); `Game Board Design.md` → Move Input, → Why this is more than a safety net.*
   **Testable:** the rendered S1 hint matches both `/see where it sends/` and
   `/[Tt]ap it again/`. This is the test that fails if the copy is later edited to drop a half.

7. **In S2 the strip renders two ring-explanation lines verbatim, each preceded by a swatch
   standing for the ring it describes:**

   | Swatch | Line |
   |---|---|
   | `swatchStyle.lastMove` | They played here last — that's what sent you. |
   | `swatchStyle.activeQuadrant` | The only board you can play in right now. |

   The second line is **confirmed as drawn** under the ratified vocabulary — "board" here means
   one of the nine, and that is what a player reads. It is also what makes a separate
   forced-mode cue unnecessary; see requirement 1's precedence note.
   *Source: `Menus and UI.md` → Decisions → How to play (`1e` — "two lines explaining the two
   rings", quoted); `design_handoff_game_ui/README.md` → 1e;
   `design-files/… Screens.dc.html` → `#1e`; `Game Overview.md` → Terminology, for the word.*
   **Testable:** in S2 both sentences render in that order, each preceded by a swatch, and the
   two swatches resolve from different keys.

8. **The strip must state the sending rule — that the cell you play inside a small board
   determines which quadrant your opponent must play in next.**
   None of requirements 2–7 closes this. Requirement 5's hint says a tap shows you "where it
   sends them" without saying that *where* is determined by *which cell*. Requirement 7's
   first line states the causality after the fact (*"that's what sent you"*) without the
   mapping, and only to a player already in S2 who can already read the rings.
   *Source: `Menus and UI.md` → Decisions → How to play ("**The game explains its own central
   mechanic** … The sending rule is the hardest thing in the game to explain, kids are a
   stated target audience … and today nothing in these docs explains it anywhere");
   `Game Overview.md` → Core Concept ("**The cell you play sends your opponent to the matching
   quadrant** — play the center cell, your opponent must play in the center quadrant");
   `Rules.md` → Placement Rules → Cell → Quadrant Mapping.*
   **Testable:** the strip renders a string naming the cell→quadrant correspondence in at
   least one reachable state.
   > **BLOCKED on copy — a writing task, not a research gap.** The mandate, the host and the
   > vocabulary are all settled; the **sentence is not written and no approved screen draws
   > it.** Every other string in this PRD is transcribed from a drawing. This sentence is the
   > hardest one in the product to write, because it has to say *cell → quadrant* using the
   > player's words — "square" and "board" — where "board" is overloaded. **Raised jointly with
   > requirement 10's wording as OQ-1. An implementer leaves this unbuilt rather than writing
   > the sentence.**

9. **In S3 the strip renders two lines verbatim, each preceded by a swatch:**

   | Swatch | Line |
   |---|---|
   | `swatchStyle.pending` (dashed) | Your pick, not played yet — and where it sends them. |
   | `swatchStyle.lastMove` (solid) | Still showing what they did last — it stays until you commit. |

   The second line restates the lifetime rule the board obeys — the last-move highlight
   *"persists until your move is completed."*
   *Source: `design-files/… Screens.dc.html` → `#2d`, which draws exactly these two lines;
   `design_handoff_game_ui/README.md` → Fidelity; `Game Board Design.md` → Last Move Highlight
   → Lifetime; corroborated by `P3-01-board-rendering.md` requirement 20.*
   **Testable:** after a first tap both sentences render in that order; the first swatch is
   dashed and the second solid.
   > **Divergence, recorded not resolved.** The Decision describes `2d`'s explanation as
   > sitting *"on the turn banner rather than a bottom strip"* and quotes **different copy** —
   > *"Play here?"* / *"Tap again to lock it in."* Both exist in the drawing: those two strings
   > are on `2d`'s **banner**, which requirement 11 confirms is **not built**; the two above
   > are on `2d`'s **bottom strip**, which is this PRD's territory. This requirement builds the
   > strip pair. If the banner's provisional voice is wanted, it has no host and would have to
   > be re-homed here as a fourth block. See **OQ-4**.

10. **When the player has a free choice of quadrant, the strip says so in words — and the
    strip is where that cue lives.** Free choice covers the opening move and being sent to a
    claimed or cat-game quadrant. Rendered under requirement 1's condition **C**.
    **The cue uses the handoff's vocabulary — "board", not "quadrant".** Of the two candidates
    on the record, `Game Board Design.md`'s *"Free choice — pick any open quadrant"* is ruled
    out by the ratified rule; the handoff's *"Free choice — pick any board"* is the form that
    survives it.
    *Source: `Game Board Design.md` → Decisions → **Where does the free-choice cue live?** —
    **"The free-choice cue lives in the how-to-play strip below the board — not in a banner
    above it."** The reasoning recorded with it: the strip already exists, already swaps
    content by board state, and already has an owner and a theme slot.
    `Game Overview.md` → Terminology, for the word. Supporting: `Game Board Design.md` →
    Active Quadrant Highlight → The free-choice state (which offered the cue as an option —
    "**or a text cue**" — and is now answered); `Rules.md` → Edge Cases → Sent to a dead
    quadrant → free choice; `P3-01-board-rendering.md` → Out of Scope, which declines the cue,
    does **not** push it to `P3-03`, and names this requirement as its owner.*
    **Testable:** constructing the strip with `placementState: freeChoice` and
    `hasPendingSelection: false` renders a cue naming it; `forced` renders none; `freeChoice`
    with `hasPendingSelection: true` renders none (requirement 1).
    > **BLOCKED on the exact sentence only.** Vocabulary, host, condition, precedence,
    > placement and theme key are all settled. What remains is a **phrasing** call, and it is
    > not cosmetic: *"pick any board"* has to read unmistakably as *one of the nine* rather
    > than as the whole grid, which is the disambiguation cost the vocabulary decision
    > accepted. Raised with requirement 8's sentence as **OQ-1**.

11. **The turn banner is not built.** Nothing is added above the board. The free-choice cue was
    the only content the banner carried that no other element covered, requirement 10 rehomes
    it, and requirement 7's second line covers the forced-mode case — so the banner has no
    remaining reason to exist.
    *Source: `Game Board Design.md` → Decisions → Where does the free-choice cue live?
    ("**not in a banner above it**"); `P1-03-theme-system.md`, which holds
    `surfaces.scoreboard.turnBanner` as **deferred** with "**No confirmed reader**" — a status
    that is now permanent rather than provisional.*
    **Consequences, stated so they are not rediscovered:**
    - `P3-03-scoreboard-turn-indicator.md` → Open Question 1, which held the banner question
      open, closes. Its assertion that `P1-03` carries `turnBanner` as `required` was wrong
      when written — it is `deferred` — and is now moot.
    - The banner's *"Player One, you're up!"* line is not built either. The whose-turn
      affordance remains the scoreboard's name highlight, which `Game Board Design.md` →
      Turn Indicator names as **the** mechanism for it.
    - `P3-01` requirement 47 composes exactly three children, with nothing between the
      scoreboard and the board except its `stripToBoardGap` — which is the same fact stated
      from the screen's side.
    **Testable:** no widget above the board renders any of the banner's four drawn strings.

12. **A line whose referent does not exist is omitted, and its swatch with it.** In S2 the
    first line of requirement 7, and in S3 the second line of requirement 9, are suppressed
    when `hasLastMove` is false; the remaining line still renders.
    S2 with no last move is unreachable in practice — `placementState == forced` is produced
    only by a move, and `P1-02` requirement 40 guarantees `lastMove == null` only on
    `newSeries()` and `startNextGame()`, both of which leave `placementState == freeChoice`.
    S3 with no last move is routine: the opening move of any game, first tap held.
    *Source: `P1-02-engine-rules.md` requirements 32 and 40; `Rules.md` → Placement Rules;
    the drawn `1d`, which is the opening move and carries no ring-explanation line at all.*
    **Testable:** constructing the strip with `hasPendingSelection: true, hasLastMove: false`
    produces one line, not two, and no dangling swatch.

### Placement and layout

13. **Each block sits where the drawings put it.** Every number in this requirement is a **code
    constant**, per the theme/code line above.

    | Block | Placement within the strip |
    |---|---|
    | C — free-choice cue | first child, at the strip's top |
    | S1 — hint | below the cue when present, `gap: 8`; otherwise the first child |
    | S1 — legend | pinned to the strip's bottom, `padding-top: 18` |
    | S2 — ring pair | pinned to the strip's bottom, `padding-top: 22` |
    | S3 — pending pair | pinned to the strip's bottom, `padding-top: 22` |

    Nothing in this layer overlays the board or any of the 81 cells.

    **The 14pt gap between the board and this strip is `GameScreen`'s, not this widget's.**
    The drawings express it as `margin-top: 14` on the strip's first child, but
    `P3-01-board-rendering.md` requirement 50 owns it as `stripToBoardGap`, fenced at **14pt**
    and chosen for symmetry with it so the board sits in equal vertical gutters. Applying it in
    both places would double it to 28pt. This follows the precedent `P3-03` requirement 21 set
    for the scoreboard-to-board gap: **the gap between two widgets belongs to their host.**
    *Source: `design-files/… Screens.dc.html` → `#1d`, `#1e`, `#2d` (the declarations);
    `P3-01-board-rendering.md` requirements 47, 50; `Theming.md` → Decisions → Does a theme
    control spacing and padding?, for why these are constants.*
    **C's position is a reversible placement default.** The cue was drawn in a banner *above*
    the board and no drawing shows it below one, so its position within the strip is chosen,
    not transcribed. The reasoning: it is a status line about the turn, so it reads before the
    instructional hint and well before the reference legend; and sitting at the strip's top
    keeps it adjacent to the nine lit quadrants it describes. *Reverses to:* the bottom block,
    above the legend. See **OQ-14**.
    **Testable:** in each state the strip's children resolve in the order above; the strip's
    own top padding is zero, so `GameScreen`'s gap is the only separation from the board.

14. **The whole 9x9 board stays visible with no zoom and no scrolling, with this strip on
    screen, in every state.** The board's full visibility is the constraint that wins.
    *Source: `Game Board Design.md` → Responsive / Screen Size ("**No zoom.** The whole 9x9
    grid stays visible at all times"); → Scoreboard ("Takes vertical space away from the
    board"); `P3-01-board-rendering.md` requirement 37, whose verification `GameScreen`
    extends past the board subtree to the screen.*
    **Testable:** at the 402 × 874 reference frame, for **S1+C** (the tallest case — cue, hint
    and legend together), S2 and S3, the scoreboard, the settings button, all 81 cells and the
    strip lay out with no `RenderBox` reporting overflow and no `Scrollable` in `GameScreen`'s
    tree.
    **The budget improved, and the arithmetic is now stable.** Requirement 11 returns the
    banner's block — margins 16 + 12, padding 11 + 11, and a ~20pt content line, so **≈70pt** —
    while requirement 10's cue costs a 19pt line plus the `gap: 8` above the hint, **27pt**.
    **Net 43pt returned** to every board screen, a fixed number now that spacing is code rather
    than theme. Frames other than 402pt remain **OQ-7**, which is `GameScreen`'s to answer.

15. **Portrait only.** No landscape layout is built.
    *Source: `Tech Design.md` → Decisions → Orientation — portrait only, enforced at the app
    level by `P1-01-app-scaffold.md` requirement 7.*
    **Testable:** the strip is asserted only at portrait frames; this layer adds no
    orientation-dependent branch.

### Behavior

16. **This layer registers no gesture handler of its own** and must not absorb, intercept or
    special-case a tap. A tap that lands on it therefore reaches `GameScreen`'s clear surface
    and **clears a pending, unconfirmed selection**, which is the uniform rule for everything
    outside the nine quadrants.
    *Source: `Game Board Design.md` → Decisions → Does a tap outside the board clear a pending
    move? — **"Yes — any tap outside the nine quadrants clears a pending, unconfirmed
    selection."** That decision names this strip explicitly, alongside the scoreboard, the
    settings button, and opening any menu or sheet: **"One rule, uniformly applied."** The
    surface itself is `P3-01-board-rendering.md` requirement 51, whose boundary is "**a widget,
    not a rectangle**" — a `GestureDetector` ancestor sees every tap no descendant recognizer
    claimed, and it names "the non-interactive how-to-play strip" among them. That is exactly
    what this requirement guarantees: that no descendant here claims one.*
    *The gutter and padding figures that decision mentions — 3pt cell gutters, 5pt quadrant
    padding — are **code constants owned by `P3-01` requirement 3**, not theme values; `P1-03`
    removed `board.outerGap`, `board.quadrantPadding` and `board.innerGap` when spacing left
    the theme. This requirement neither reads nor defines them.*
    **Testable:** (i) no widget in this layer's subtree carries a `GestureDetector`, an
    `InkWell` or an `onTap`; (ii) in a `GameScreen` test with a pending selection held, a tap
    at the strip's centre leaves `pendingSelection == null`.
    *History, so the reversal is legible:* an earlier revision asserted (ii) with no source and
    was correctly flagged for deciding, alone, a question three siblings were holding open. The
    assertion was withdrawn, and is restored here **because the user settled it** — not because
    the earlier reasoning was accepted. See **OQ-8**.

17. **The strip is fully readable with animations switched off.** No part of it may depend on
    motion to be understood.
    *Source: `Animations.md` → Decisions → Animations off = instant state change;
    `design_handoff_game_ui/README.md` → Interactions & behavior ("Every screen above is fully
    readable with animation off — that is the correctness test").*
    **Testable:** with the animations setting off, every state renders the same strings and the
    same swatch widgets as with it on.

### Theming

18. **Every *drawn* value in this layer resolves from a `P1-03-theme-system.md` requirement 15
    key path. Spacing is the stated exception and is written as code constants.**

    | Key path | Carries |
    |---|---|
    | `surfaces.legend.hintStyle` | requirement 5's hint typography — 12/400 |
    | `surfaces.legend.labelStyle` | requirement 2's legend labels — 10.5/400 |
    | `surfaces.legend.ringExplanationStyle` | requirements 7 and 9's line typography — 12/400 |
    | `surfaces.legend.freeChoiceCueStyle` | requirement 10's cue — 12/400 `#4fc3ff` |
    | `surfaces.legend.swatchStyle.<state>` | the swatches, as a **per-state map** |

    `swatchStyle` carries six entries — `open`, `locked`, `catGame`, `lastMove`,
    `activeQuadrant`, `pending` — each `{fill, border, radius, glow}`. One flat style cannot
    serve six treatments without a hardcoded switch, which this requirement forbids;
    `labelStyle` is separate from `hintStyle` for the same reason, the two being distinct drawn
    values at 10.5 and 12.

    **The exception, stated precisely.** *No color, font, size, weight, opacity, corner radius,
    border width or glow is written into this layer's code.* **Gaps and padding are** — they
    are code constants, listed in requirements 13 and 19, and are not theme reads. The line is:
    **a theme controls the drawn geometry of a thing itself; code controls where things sit
    relative to one another.** Without this exception, requirement 19's own layout numbers would
    have no legal implementation.
    *Source: `Theming.md` → Decisions → Does a theme control spacing and padding? ("**Themes do
    not control spacing and padding. Gaps and layout numbers are fixed in the code.**");
    `P1-03-theme-system.md` req 15 → `surfaces`, which removed every `*.padding` key on that
    ruling; `P3-01-board-rendering.md` requirement 28's constants column, which draws the same
    line for the board.*

    **The cue must be read from `freeChoiceCueStyle`, never from `color.boardLine`, even though
    the two hold the identical hex.** The cue is board-blue *on purpose* — it names the state
    the open quadrants are in — so the match is semantic, not incidental. Reading it from the
    palette token would silently break any theme that recolours the cue without recolouring the
    grid, and `P1-05`'s guard cannot see the difference because neither is a literal.
    *Source: `P1-03-theme-system.md` → Appendix A.1, which records this cue as a near-miss for
    exactly that reason, and its rule that a component reads its own `surfaces.*` key and never
    a `color.*` key that happens to look right.*

    **Testable — three checks.**
    (i) `P1-05-theme-guard-test.md` reports zero violations for this layer's files.
    (ii) This layer references no `color.*` path; recolouring
    `surfaces.legend.freeChoiceCueStyle` alone changes the cue and leaves the board's grid
    lines unchanged.
    (iii) **A narrowed manual review gate.** `P1-05` requirement 4(c) says the guard cannot see
    "any theme value passed as a positional or unlabelled number." That blind spot used to
    cover this layer's spacing; spacing is now legitimately hardcoded, so the gate's remaining
    job is small and specific — **the swatch dimensions** (11×11, 15×15), which are theme reads
    that the guard still cannot distinguish from constants.

19. **Neon's values, transcribed here so this PRD is self-contained** and no implementer has
    to open the HTML. Each is marked **[T]** for a theme read under requirement 18's keys, or
    **[C]** for a code constant.

    **Shared by all bottom blocks**
    - **[C]** bottom block pinned with `margin-top: auto`, column, `gap: 8`
    - **[C]** `padding-top`: `18` in S1, `22` in S2 and S3

    **C — free-choice cue** *(from `#1d`'s banner, relocated)*
    - **[T]** `12 / 400`, color `#4fc3ff` — board-blue, the same hue the open quadrants take,
      and the same hex as `color.boardLine`; requirement 18 forbids reading it from there
    - **[C]** centered, `gap: 8` above the hint. The 14pt above *it* is `GameScreen`'s
      `stripToBoardGap` — requirement 13.
    - The forced-state variant the banner also drew — `#c9b3ff` with *"Play the middle
      board"* — is **transcribed but unused**: requirement 1 never renders C in `forced`, and
      requirement 7's second line carries that meaning instead. Recorded so a later reader does
      not think it was missed, and so no key is requested for it.

    **S1 — legend and hint** *(`#1d`)*
    - **[T]** hint: `12 / 400`, line-height `1.6`, `#75798c`; **[C]** centered,
      `text-wrap: pretty`, explicit break between the sentences
    - **[T]** legend labels: `10.5 / 400`, `#595d6c`; **[C]** row centered, `gap: 16` between
      entries, `gap: 6` between a swatch and its label
    - **[T]** swatches, all `11 × 11`, radius `3`:
      · `open` — `inset 0 0 0 1px rgba(79,195,255,.85)`, no fill, no glow
      · `locked` — solid fill `#1b1e2c`
      · `catGame` — no box; a centered `Ø` at `10pt` in `#9aa2c2`

    **S2 — ring explanations** *(`#1e`)*
    - **[T]** each line `12 / 400`, `#b2b6ca`; **[C]** `gap: 9` between swatch and line
    - **[T]** `lastMove` swatch: `15 × 15`, radius `4`, `2px solid #d2cefd`,
      glow `0 0 10px 2px rgba(181,171,252,.7)`
    - **[T]** `activeQuadrant` swatch: `15 × 15`, radius `5`, `2px solid #b57cff`,
      glow `0 0 12px 3px rgba(181,124,255,.6)`

    **S3 — pending explanations** *(`#2d`)*
    - **[T]** each line `12 / 400`, `#b2b6ca`; **[C]** `gap: 9`
    - **[T]** `pending` swatch: `15 × 15`, radius `4`, `2px dashed #e9e9ed`, no glow
    - **[T]** `lastMove` swatch: as S2's, and the same key — not a second copy

    *Source: `design-files/… Screens.dc.html` → `#1d`, `#1e`, `#2d`;
    `design_handoff_game_ui/README.md` → Design tokens → Type, Color; `neon.theme.json`;
    `Theming.md` → Decisions → Does a theme control spacing and padding?, for the [T]/[C] split.*
    **No value is invented, altered or rounded** — mechanical transcription, the same
    discipline `P1-03-theme-system.md` requirement 13 imposes on Neon.

20. **The strip renders nothing once the game is over** — `placementState == gameOver` produces
    an empty subtree, cue included.
    **Default (reversible); no doc states it.** The reasoning: every string in requirements
    2–12 describes a move that can still be made, and none can be true after the last one.
    *Reverses to:* the strip persisting under the result card, or freezing on its last content.
    `P3-04-game-over-rematch.md` → Out of Scope points this question back here, and
    `P3-01-board-rendering.md` carries the parallel question for the board. Note that
    `P3-01` requirement 52 hosts the result card **over** the screen's content, so this
    requirement decides only whether there is anything of ours underneath it. See **OQ-9**.
    *Source for the gate itself: `P1-02-engine-rules.md` requirement 36, which makes `gameOver`
    a distinct `placementState` rather than a null `activeQuadrant`.*
    **Testable:** constructed with `placementState: gameOver`, the strip renders no child
    carrying any requirement 26 key.

21. **This layer's text does not scale with the iOS Dynamic Type setting.**
    *Source: `Menus and UI.md` → Decisions → Do we support Dynamic Type? ("**Not for now.**
    *'Lets not do this as of yet.'*").*
    **Testable:** rendering the strip under a `textScaler` of 2.0 produces the same laid-out
    text height as under 1.0.

22. **The strip never fades, hides or self-dismisses.** It renders on its three constructor
    arguments and on nothing else — no move counter, no games-played threshold, no dismiss
    control, no setting.
    **Default (reversible); no doc addresses it.** The reasoning: a fade needs a trigger, a
    dismiss needs a way back, and both are unstated; requirement 1's state-dependence already
    means no state shows more text than that state needs. *Reverses to:* any of those triggers,
    each of which adds a constructor argument and probably state this widget does not have.
    See **OQ-10**.
    **Testable:** two constructions with identical arguments produce identical output,
    regardless of how many times the widget has been built before.

### Tests

23. **Widget tests, no golden image tests.** Every element above is addressable via requirement
    26's keys, so a test asserts presence and text without comparing pixels.
    *Source: `Tech Design.md` → Decisions → Widget tests for the board — no golden tests.*
    **Known reach limit, inherited from `P3-01-board-rendering.md` requirement 39:** these
    keys assert a state is *present*, never that its treatment is *correct*. A build drawing
    the `locked` swatch at the wrong fill passes every test here. Treatment correctness is
    verified by eye against `1d`/`1e`/`2d`, and that review is the only check on it.

24. **Tests run locally** via `flutter test`. There is no CI; nothing runs them on a push.
    *Source: `Tech Design.md` → Decisions → CI — local builds only.*

### The widget surface

25. **`HowToPlayStrip` is a `ConsumerWidget` in `lib/ui/board/how_to_play_strip.dart`**, with
    the three constructor parameters and the one provider read fenced in *Interface this PRD
    publishes* above. It is composed by `P3-01-board-rendering.md` requirement 47 as
    `GameScreen`'s third child and constructed by its requirement 48's single state read.
    *(`P3-01-board-rendering.md` requirements 47, 48, whose requirement 47 flagged the absence
    of this symbol; `P3-03-scoreboard-turn-indicator.md` requirement 19 for the shape and for
    the no-game-state-provider rule this mirrors.)*
    **Verification:** the widget's constructor takes exactly `placementState`,
    `hasPendingSelection` and `hasLastMove`; a grep of `how_to_play_strip.dart` finds
    `activeThemeProvider` and no other provider — in particular no `boardProvider`, no
    `pendingSelectionProvider`, no `appNavigatorProvider`; and every requirement 1 branch is
    reachable in a test by construction alone, with no `ProviderScope` override beyond the
    theme.

26. **`HowToPlayKeys` publishes every key literal**, in
    `lib/ui/board/how_to_play_keys.dart`, in the shape of `P3-01` requirement 45's `BoardKeys`
    and `P3-03` requirement 20's `ScoreboardKeys`:

    ```dart
    // lib/ui/board/how_to_play_keys.dart
    enum LegendEntry { open, locked, catGame }
    ```

    | Accessor | Key string | Present when |
    |---|---|---|
    | `strip` | `howToPlay.strip` | `placementState != gameOver` |
    | `freeChoiceCue` | `howToPlay.cue` | condition **C** |
    | `hint` | `howToPlay.hint` | **S1** |
    | `legend` | `howToPlay.legend` | **S1** |
    | `legendEntry(LegendEntry e)` | `howToPlay.legend.{open\|locked\|catGame}` | **S1** |
    | `ringLine(BoardKeys-style state)` | `howToPlay.ring.{lastMove\|activeQuadrant\|pending}` | **S2** or **S3**, per requirements 7, 9, 12 |
    | `sendingRule` | `howToPlay.sendingRule` | requirement 8 — **not yet built**, key reserved |

    The `sendingRule` key is reserved rather than omitted so that requirement 8 landing is a
    copy change and a test, not a rename across files.
    **Verification:** requirement 1's table-driven test asserts presence and absence entirely
    through these accessors; no test in this layer matches on a raw string.

## Rationale — not requirements

Recorded because they explain the shape of the requirements, and demoted because they are not
independently testable. Nothing here is a deliverable.

- **Why the ring lines exist.** The rings are gameplay-critical, not decoration.
  `Game Board Design.md` → The Two Highlights Together calls the last-move and
  active-quadrant highlights "the two halves of one sentence" — *"They played **there** → so
  you must play **here**."* Requirement 7's lines are the redundant channel for a player who
  cannot yet read the rings.
- **Why the free-choice cue is words and not just a highlight.** `Game Board Design.md` → The
  free-choice state observes that nine glowing quadrants at once "risks looking like noise,"
  and offers the calmer highlight and the text cue as alternatives. The board took the calmer
  highlight (`P3-01-board-rendering.md` req 21); this strip takes the words. Both, not either
  — which is what the approved handoff drew.
- **The cue supplements the highlight, it does not replace it.** The board still renders every
  still-open quadrant as available and claimed/cat quadrants as locked
  (`P3-01-board-rendering.md` reqs 21–22). This layer sets no board state, so there is nothing
  here to assert that `P3-01`'s own tests do not already cover.
- **Legibility as a contract on every theme.** `Theming.md` → What a Theme Controls requires
  every theme to keep gameplay-critical treatments legible, and this strip carries the only
  words explaining the game. Not stated as a requirement because `P1-03-theme-system.md` →
  Open Questions already records that contract as *"Unfalsifiable as written"* and owns
  finding it a form. A second unfalsifiable assertion here would add no test.

## Out of Scope

Named so the boundary is explicit. Each is specified elsewhere; do not specify it here.

- **`GameScreen` itself** — its route, its single state read, its safe-area inset, its
  `stripToBoardGap`, its clear surface and its game-over overlay: `P3-01-board-rendering.md`
  requirements 46–52. This PRD publishes a child and consumes three arguments; it composes
  nothing and holds no screen-level number.
- **The board and every quadrant / cell treatment these swatches stand for** —
  `P3-01-board-rendering.md`. Requirement 3 draws simplified swatches; it defines no board
  state and publishes no board key. The free-choice **highlight** is that PRD's requirement 21;
  requirement 10 here owns only the words. Board geometry constants — outer gap, quadrant
  padding, inner gap — are that PRD's too, now that they have left the theme.
- **The two-tap gesture the hint describes, and the implementation of the
  outside-the-quadrants clear** — `P3-02-move-input.md`, whose requirements 7–9 own the
  pending selection's lifecycle, hosted by `P3-01` requirement 51. Requirement 16 only
  guarantees this widget stays transparent to it.
- **The scoreboard, the turn indicator and the settings button** —
  `P3-03-scoreboard-turn-indicator.md`. The whose-turn affordance stays entirely there;
  requirement 11 removes the banner that would have duplicated it.
- **The turn banner** — *not built at all*, per requirement 11.
- **The rules being explained** — the sending rule's mechanics, claims, cat game, free
  choice, win and draw detection: `P1-02-engine-rules.md`. Requirement 8 states the rule in
  words; it computes nothing.
- **Ratifying the player-facing vocabulary** (`Game Overview.md` → Terminology) and **the
  theme/spacing boundary** (`Theming.md` → Decisions). Both are settled elsewhere; this PRD
  applies them and records where they cost something.
- **The theme mechanism** — the schema, YAML loading, merge-over-Neon and authoring
  `neon.yaml`: `P1-03-theme-system.md`. This PRD names keys and transcribes Neon's values into
  requirement 19; it does not build the loader or fill the file.
- **The theme guard's rule set** — `P1-05-theme-guard-test.md`. Requirement 18 consumes it and
  records its documented reach limit; it does not extend it.
- **Game-over presentation** — the winner and draw cards and their copy:
  `P3-04-game-over-rematch.md`, hosted by `P3-01` requirement 52. Requirement 20 only decides
  what is underneath.
- **A fuller Rules / How-to-Play screen or menu item** — explicitly unsettled; **OQ-12**.
- **Localisation.** No design doc raises it; strings are specified in English as the docs word
  them.
- **Anything from `Alternative Game Styles.md`** — a declared parking-lot doc, explicitly not
  the game being built.

## Open Questions

Numbers are stable across revisions so siblings can cite them; an answered question is marked
rather than removed. **OQ-1 is the only thing blocking a requirement from being built.**

### Answered — kept so the citation trail survives

**OQ-11 — Does this layer have the theme keys it needs? — ANSWERED, all three items.**
- `surfaces.legend.swatchStyle` became a **per-state map** — `open`, `locked`, `catGame`,
  `lastMove`, `activeQuadrant`, `pending`, each `{fill, border, radius, glow}` — agreeing that
  "non-blocking" and "flat" could not both hold.
- `surfaces.legend.labelStyle` was added, the legend label at 10.5/400 and the hint at 12/400
  being distinct drawn values that one key cannot serve.
- **Spacing left the theme entirely.** `Theming.md` → Decisions → *Does a theme control spacing
  and padding?* answers **no**, on the reasoning `P1-05` requirement 4(c) had already surfaced.
  `P1-03` removed nine keys accordingly. Requirement 18 now states the exception this creates
  instead of depending on a key that will never exist.

Earlier: `surfaces.legend.freeChoiceCueStyle` landed as `required`, and the cue is recorded in
`P1-03` → Appendix A.1 as a `color.boardLine` near-miss — requirement 18 carries that rule and
a test for it.

**OQ-5 — Which vocabulary does player-facing copy use, "board" or "quadrant"? — ANSWERED.**
> **Player-facing text says "board". The internal term stays "quadrant."**

*(`Game Overview.md` → Terminology.)* Applied at requirement 7 (confirmed as drawn),
requirement 10 (the handoff's *"pick any board"* survives), and requirement 4 (the
internal/player-facing split is the general rule its test is written against). The **cost** —
"board" meaning both the big grid and each of the nine small ones — is stated at the top of this
file and is now a copy constraint on OQ-1.

**OQ-2 — Where does the free-choice text cue live? — ANSWERED.**
> **The free-choice cue lives in the how-to-play strip below the board — not in a banner above
> it.**

*(`Game Board Design.md` → Decisions.)* Requirement 10 builds it, requirement 1 gives it a
condition and precedence, requirement 13 places it, requirement 18 gives it a key, requirement
26 gives it a test key, and requirement 11 records the consequence: **the turn banner is not
built**. `P3-03-scoreboard-turn-indicator.md` → Open Question 1 closes as a side effect.

**OQ-8 — What does a tap landing on this strip do? — ANSWERED.**
> **Any tap outside the nine quadrants clears a pending, unconfirmed selection** — including
> the legend/how-to-play strip, the scoreboard, the settings button, and opening any menu or
> sheet. One rule, uniformly applied.

*(`Game Board Design.md` → Decisions.)* Requirement 16 guarantees this widget claims no tap;
`P3-01` requirement 51 hosts the surface that receives it and names this strip explicitly.
`P3-02-move-input.md` (OQ-1), `P4-04-settings.md` (OQ-5) and `P2-01-navigation.md` (OQ-11)
carry the same answer.

### Blocking — needs the user; no amount of reading settles it

**OQ-1 — What do the two unwritten sentences actually say?**
Kept as one ask because the user will be settling the strip's **voice** once.

| # | Requirement | What is missing |
|---|---|---|
| a | req 8 | the sending-rule sentence — *the cell you play decides which board they play in*. No copy written, none drawn |
| b | req 10 | the free-choice cue's exact phrasing. The handoff's *"Free choice — pick any board"* is the surviving candidate; whether it ships as drawn is the call |

**The constraint on both is disambiguation, not style.** Under the ratified vocabulary "board"
means both the big 3x3 grid and each of the nine small ones, and this strip is where that
collides: the approved copy already carries **square** for a cell (req 5) and **board** for a
quadrant (req 7), with the big board implied and never named. So (b) has to read unmistakably
as *one of the nine*, and (a) — the hardest sentence in the product — has to express
*cell → quadrant* as *square → board* without either noun sliding scale. Whoever writes these
is solving that, not choosing a tone.

*Everything else about both requirements is buildable: host, condition, precedence, placement,
theme key, test key and vocabulary are settled. Requirement 26 reserves `howToPlay.sendingRule`
so that (a) landing is a copy change, not a rename. An implementer leaves (a) and (b) unbuilt
rather than authoring them.*

### Recorded defaults — decided in this PRD, reversible, worth confirming

**OQ-3 — Two precedence calls, both inferred from the drawings.**
(i) *Does S3 replace S2's pair or stack with it?* `2d` is drawn on the same shell as `1e`, so
a pending selection in a forced quadrant satisfies both. Requirement 1 gives S3 precedence,
because that is what the drawing shows.
(ii) *Does the free-choice cue survive a first tap?* Requirement 1 suppresses it in S3,
following `2d`'s banner, which drops its mode cue and switches wholly to the provisional voice.
The counter-argument is real: free choice is still true while a selection is held, and the
player may still reselect any open quadrant — so the cue arguably should persist. The evidence
for suppression comes from an element that is no longer built (requirement 11), which weakens
it. Cost of reversing: one extra line in S3, 27pt, which requirement 14's recovered 43pt now
comfortably affords.

**OQ-4 — `2d`'s explanation is specified twice, with two different texts.** The Decision says
it sits *"on the turn banner rather than a bottom strip"* and quotes *"Play here?"* / *"Tap
again to lock it in."* The drawn `2d` has **both**: those strings on the banner, and
requirement 9's two different strings on the bottom strip. Requirement 9 builds the strip pair.
**Requirement 11 sharpens this:** the banner is not built, so if the Decision's reading is the
intended one, that copy is now homeless and would have to be re-homed into this strip as a
fourth block — not merely relabelled.

**OQ-6 — Do swatches reproduce their board treatments or simplify them?** Requirement 3 takes
the drawings as normative. The alternative is defensible from `Game Board Design.md` →
Everything Here Is Theme-Driven, but produces a `locked` swatch that is a 50% veil over
nothing — a near-invisible grey patch — and is drawn nowhere. `P1-03`'s decision to give
`swatchStyle` its own per-state map rather than aliasing the board's keys is consistent with
the reading taken here.

**OQ-9 — Does the strip survive game over?** Requirement 20 removes it. `P3-01` requirement 52
hosts the result card over the screen's content with the finished board still visible behind
it, so something is drawn down there; nothing says whether it is this.
`P3-04-game-over-rematch.md` → Out of Scope points the question back here.

**OQ-10 — Do the hint and legend ever fade once a player knows the game?** Requirement 22 says
no. They are training wheels on the screen with the tightest vertical budget in the app, and a
player on their fortieth game pays for them every turn. If they can fade, the trigger is
unstated — a move count, a games-played count, a setting, a dismiss control — and a dismiss
control needs a way to bring them back, plus a fourth constructor argument. Requirement 14's
recovered 43pt lowers the pressure behind this question without answering it.

**OQ-14 — Where within the strip does the free-choice cue sit?** Requirement 13 puts it at the
strip's top, above the hint: it is a status line about this turn, so it reads before the
instruction and well before the reference legend, and sitting directly under the board keeps it
adjacent to the lit quadrants it describes. Nothing draws it below a board, so the position is
chosen rather than transcribed. *Reverses to:* the bottom block, above the legend.

### Relieved, and now owned elsewhere

**OQ-7 — What is the vertical budget below 402pt?** **Requirement 11 changed the arithmetic in
this PRD's favour, and both sides are now constants:** not building the banner returns its
margins (16 + 12), padding (11 + 11) and ~20pt content line — **≈70pt** — while requirement
10's cue costs a 19pt line plus the `gap: 8` above the hint, **27pt**. **Net 43pt returned to
every board screen.**

Two further inputs have since closed. `stripToBoardGap` is fenced at **14pt**
(`P3-01` requirement 50), so the board's lower gutter is a known number rather than an unknown.
And the safe-area inset is **`max(mediaQuery.padding.top, 62)`, never the sum** — the handoff's
62pt is measured from the frame top, so a naive `SafeArea` *plus* 62 double-counts the notch on
any modern iPhone. Earlier revisions of this PRD described the frame as having "62pt top and
44pt bottom padding" without saying which; on a device whose inset exceeds 62 the top cost is
the inset, not 62 plus it. That correction makes the budget *less* tight than an additive
reading suggested.

**The remaining question is `GameScreen`'s, not jointly held.** `P3-01-board-rendering.md`
requirements 46–52 now hold the vertical sum, so a sub-402pt scaling rule — proportional
scaling, fixed points with re-centering, or a cap — lands there and this strip consumes
whatever it decides. Its Open Questions 3 states the answer is **"unresolved and with the
user."** iPhone SE is 375 × 667, **207pt shorter** than the reference frame, so the recovered
43pt covers about a fifth of the deficit; iPad remains a declared second target; and
requirement 21 rules out Dynamic Type as the mechanism. Recorded here because S1+C is the
tallest strip state and therefore the case any rule has to clear.

### Carried from the design docs — not this PRD's to resolve

**OQ-12 — Is there also a fuller Rules/How-to-Play screen**, separate from the on-board legend
and hint, or does the legend/hint fully cover "how to play" for this version? (Already listed
as a future menu item to consider.)
*(`Menus and UI.md` → Open Questions, worded as it words it. The Decision scoping this feature
carries the same hedge: "Whether there is also a fuller Rules/How-to-Play screen is left open."
This PRD covers the on-board layer only. It bears directly on OQ-1(a): a rules screen would be
the natural home for the sending-rule explanation, and would change what S1 must carry.)*

**OQ-13 — Which values, concretely, does Classic Red vs Blue override?**
*(`Theming.md` → Open Questions; owned by `P5-01-classic-theme.md`.)* Listed because the second
theme is the first real test of this strip's legibility under a theme that is not Neon, and
because requirement 19 transcribes Neon's values only.
