# PRD: How To Play — The On-Board Legend and Hint

> **Status:** Draft · Source docs read: `Menus and UI.md`, `Game Board Design.md`,
> `Game Overview.md`, `Theming.md`, `Rules.md`, `Tech Design.md`, `Animations.md`,
> `roadmap.md`, plus the read-only reference asset `design_handoff_game_ui/`
> (`README.md`, `design-files/Tic Tac Toe Extreme - Screens.dc.html`, `neon.theme.json`).
> `Alternative Game Styles.md` is a declared parking-lot doc and was read only to confirm
> it is out of scope — no requirement here comes from it.

> **Wave:** P3 — the game-screen wave, alongside `P3-01-board-rendering.md`,
> `P3-02-move-input.md`, `P3-03-scoreboard-turn-indicator.md` and the game-over PRD.
> **Depends on:** `P1-02-engine-rules.md` (supplies the free-choice / forced state and the
> pending-selection state this layer describes in words), `P1-03-theme-system.md` (every
> value drawn here is read from a theme slot), `P3-01-board-rendering.md` (the quadrant and
> cell treatments this layer's swatches must match).
> **Depended on by:** nothing. This is a leaf.
> Within a wave, work is parallel-safe; a lower wave ships first.

> **Note on source status:** `Menus and UI.md` → Decisions → *How to play — the on-board
> legend and hint* is the decision that puts this feature in scope, and it is the only
> `## Decisions` entry anywhere that covers it. `Game Board Design.md` carries the house
> banner *"Nothing here is settled"* and has **no `## Decisions` section at all** (recorded
> in `roadmap.md`), but its **Open Questions** section is empty, the approved handoff was
> drawn from it, and the two PRDs already written from it treat its body as settled. This
> PRD does the same, and flags rather than resolves every place the body hedges or the
> handoff goes beyond it.

---

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
failure, not as a feature, to anyone who has not been told that the first tap is a preview.

## Goal

The game screen carries an explanatory layer — a legend of the quadrant states and a hint
naming the two-tap mechanic — so that a first-time player, including a child, can learn
what the board is telling them and how to move **without leaving the board**: no tutorial,
no rules screen, no one sitting beside them. The layer names the states the board draws
(open, locked, cat game), says in words what the last-move ring and the active-quadrant
ring mean, states in words when the player has a free choice, and says explicitly that the
first tap previews and the second tap plays. It is entirely theme-driven, readable with
animations off, and it costs the board none of its 81-cells-visible-no-zoom budget.

## Requirements

### What a player must be able to learn from the board

1. **The game screen explains its own central mechanic; a player does not have to leave the
   board to learn how to play.** Specifically, the on-board layer must convey (a) what the
   quadrant states mean, (b) that the first tap previews where the move sends the opponent
   and the second tap plays it, and (c) what the two gameplay-critical rings mean.
   *Source: `Menus and UI.md` → Decisions → How to play — the on-board legend and hint
   ("**The game explains its own central mechanic — this is now in scope to build out.**
   … the sending rule is the hardest thing in the game to explain, kids are a stated target
   audience … and today nothing in these docs explains it anywhere"); `Game Overview.md` →
   Target Audience & Platform ("Kids are a target audience").*
   *Testable:* every one of (a), (b) and (c) has a corresponding on-screen element in the
   game screen's widget tree, present without any user action.

### The legend — quadrant states

2. **A legend of quadrant states is rendered on the game screen, carrying exactly three
   entries — Open, Locked, Cat game — each a swatch beside its label.**
   *Source: `Menus and UI.md` → Decisions → How to play ("The approved handoff draws a
   legend (Open · Locked · Cat game)"); `design_handoff_game_ui/README.md` → 1d ("Legend
   pinned to the bottom: Open (blue outline) · Locked (dim swatch) · Cat game (Ø)");
   `design-files/Tic Tac Toe Extreme - Screens.dc.html` → `#1d`, which draws the three
   entries as an 11pt swatch + label row at 10.5pt.*
   *Testable:* the game screen renders three legend entries, labelled Open, Locked and Cat
   game, each with a swatch.

3. **Each legend swatch is drawn from the same theme values the board uses for that state**,
   not from a second set of values authored for the legend — an Open swatch carries the
   open quadrant's border treatment, a Locked swatch the locked veil, a Cat game swatch the
   cat glyph. A legend that disagrees with the board it explains is worse than none.
   *Source: `Game Board Design.md` → Everything Here Is Theme-Driven ("Nothing in this
   document should be read as a hardcoded visual decision … all of it comes from the
   selected theme"); `design_handoff_game_ui/README.md` → Quadrant states (the treatments
   being referenced); `Theming.md` → Architectural Rule.*
   *Testable:* changing the active theme's open / locked / cat-game quadrant slots changes
   the corresponding legend swatch, with no edit to legend code.

4. **The legend names the three states in the same words the board's states are named** —
   Open, Locked, Cat game — matching the state vocabulary `Game Board Design.md` uses for
   what the board must communicate.
   *Source: `Game Board Design.md` → Player Feedback / Affordances (the board must
   communicate "which quadrant is legal right now", "which quadrants are _not_ legal", and
   "Cat-game quadrants"); `Game Overview.md` → Terminology ("**Cat game** — a small board
   filled with no winner").*
   See Open Questions on "board" vs "quadrant" in player-facing copy.

### The hint — the two-tap mechanic

5. **The hint text is rendered on the game screen, verbatim, as two lines:**

   > Tap a square to see where it sends them.
   > Tap it again to play it.

   This is the only statement anywhere in the product that the two-tap mechanic exists.
   *Source: `Menus and UI.md` → Decisions → How to play (quotes exactly this text);
   `design_handoff_game_ui/README.md` → 1d ("Hint text: 'Tap a square to see where it sends
   them. / Tap it again to play it.'"); `design-files/… Screens.dc.html` → `#1d`, which
   draws it centered, 12pt, line-height 1.6, with an explicit line break between the two
   sentences.*
   *Testable:* both sentences are present on the game screen as drawn, on two lines, with
   the wording unchanged.

6. **The hint states both halves of the mechanic — that the first tap previews the
   destination, and that a second tap on the same square commits.** Neither half may be
   dropped: the preview is what teaches the sending rule, and the "tap it again" is what
   stops a first tap reading as a failure.
   *Source: `Game Overview.md` → How a Move Is Made ("Moves are **two taps — select, then
   confirm**… This makes the game's central mechanic visible before you commit to it —
   *play here, send them there*"); `Game Board Design.md` → Move Input — Tap to Select, Tap
   Again to Confirm, and → Why this is more than a safety net.*

### The rings explained in words

7. **In the forced-quadrant state the layer explains both rings in words**, verbatim:

   > They played here last — that's what sent you.
   > The only board you can play in right now.

   Each line carries a swatch drawn in the ring treatment it describes — the last-move ring
   and the active-quadrant ring respectively.
   *Source: `design_handoff_game_ui/README.md` → 1e ("Bottom legend explains both rings in
   words: 'They played here last — that's what sent you.' / 'The only board you can play in
   right now.'"); `design-files/… Screens.dc.html` → `#1e`, which draws a solid `#d2cefd`
   swatch on the first line and a solid `#b57cff` swatch on the second.*
   *Testable:* with a forced quadrant and a last move on screen, both sentences render, each
   beside a swatch matching its ring.

8. **These two lines exist because the rings they describe are gameplay-critical, not
   decoration.** The last-move highlight answers "what changed" and the active-quadrant
   highlight answers "what can I do" — `Game Board Design.md` calls them "the two halves of
   one sentence": *"They played **there** → so you must play **here**."* The words are the
   redundant channel for a player who cannot yet read the rings.
   *Source: `Game Board Design.md` → The Two Highlights Together; → Player Feedback /
   Affordances; `Theming.md` → What a Theme Controls ("The last-move highlight and
   active-quadrant highlight are *gameplay-critical*, not decoration").*

9. **In the pending-move state the layer explains the provisional highlight and the
   persisting last-move highlight in words**, verbatim:

   > Your pick, not played yet — and where it sends them.
   > Still showing what they did last — it stays until you commit.

   Each carries a swatch — dashed for the provisional pick, solid for the last move.
   *Source: `design-files/… Screens.dc.html` → `#2d`, which draws exactly these two lines
   with a dashed `#e9e9ed` swatch and a solid `#d2cefd` swatch;
   `design_handoff_game_ui/README.md` → Fidelity ("Colors, type, spacing, radii and glow
   values are final and exact"). The second line restates the lifetime rule in
   `Game Board Design.md` → Last Move Highlight → Lifetime ("The highlight persists until
   your move is completed").*
   *Testable:* after a first tap, both sentences render; the dashed swatch differs from the
   solid one.

### The free-choice text cue

10. **When the player has a free choice of quadrant, the screen says so in words**, not by
    highlight alone. Free choice covers the opening move and being sent to a claimed or
    cat-game quadrant.
    *Source: `Game Board Design.md` → Active Quadrant Highlight → The free-choice state
    ("Nine glowing quadrants at once also risks looking like noise, so free choice may want
    a calmer treatment than the single-quadrant forced highlight — **or a text cue ('Free
    choice — pick any open quadrant')**"); `Rules.md` → Edge Cases → Sent to a dead quadrant
    → free choice; `design_handoff_game_ui/README.md` → 1d, which draws the cue as "Free
    choice — pick any board" in board-blue.*
    *Testable:* entering the free-choice state renders a text cue naming it; leaving it
    removes the cue.
    The cue's **exact wording** and **which element hosts it** are unresolved — see Open
    Questions. `P3-01-board-rendering.md` requirement 21 builds only the highlight half of
    this and explicitly leaves the text half unowned.

11. **The text cue is a supplement to the free-choice highlight, not a replacement for it.**
    The board still renders every still-open quadrant in the open treatment, and still
    renders claimed and cat-game quadrants as locked — "pick any of these open ones," not
    "the board is unlocked."
    *Source: `Game Board Design.md` → Active Quadrant Highlight → The free-choice state;
    `P3-01-board-rendering.md` requirements 21–22, which own the highlight.*

### Placement and layout

12. **The explanatory layer sits below the board in the game screen's vertical stack** — the
    hint directly beneath the board, the legend pinned to the bottom of the screen. It never
    overlays the board or any of the 81 cells.
    *Source: `design_handoff_game_ui/README.md` → 1d ("Legend pinned to the bottom");
    `design-files/… Screens.dc.html` → `#1d`, where the hint has `margin-top:14` after the
    board and the legend block has `margin-top:auto; padding-top:18`; `Game Board Design.md`
    → Visual Layout (the screen is a vertical stack).*

13. **The whole 9x9 board stays visible with no zoom and no scrolling, with this layer on
    screen.** The layer competes for the same vertical budget as the scoreboard, and the
    board's full visibility is the constraint that wins.
    *Source: `Game Board Design.md` → Responsive / Screen Size ("**No zoom.** The whole 9x9
    grid stays visible at all times"); → Scoreboard ("Takes vertical space away from the
    board — worth noting given the board already has 81 cells to fit on a phone");
    `Tech Design.md` → Decisions → Orientation — portrait only.*
    *Testable:* on the target portrait frame, the scoreboard, the settings button, all 81
    cells, the hint and the legend lay out without overflow and without a scroll view.
    See Open Questions on frames other than 402pt.

14. **The layer is portrait-only, like the rest of the game.**
    *Source: `Tech Design.md` → Decisions → Orientation — portrait only.*

### Behavior

15. **The layer is non-interactive text: nothing in it accepts a tap as its own action.** A
    tap landing on the hint or the legend is a tap outside the grid, and therefore clears any
    pending selection, exactly as a tap on any other non-board area does.
    *Source: `Game Board Design.md` → Move Input → Changing your mind ("**Tap outside the
    full grid** → deselects entirely, clearing the pending move"). The gesture itself is
    `P3-02-move-input.md`'s; this requirement only forbids this layer from intercepting it.*
    *Testable:* with a pending selection active, tapping the hint text clears it; no legend
    or hint element registers a tap handler of its own.

16. **The layer is fully readable with animations switched off.** No part of it may depend
    on motion to be understood, and with animations off the game simply shows the new state
    with no substitute effect.
    *Source: `Animations.md` → Decisions → Animations off = instant state change;
    `design_handoff_game_ui/README.md` → Interactions & behavior ("Every screen above is
    fully readable with animation off — that is the correctness test").*

### Theming

17. **Every value in this layer is read from the active theme** — text color, type size and
    weight, swatch treatments, spacing and gaps. **No color, font, size, opacity, radius or
    duration is written into this layer's code.**
    *Source: `Theming.md` → Architectural Rule; → Decisions → What the theme's slot list is
    derived from ("The theme's slot list is derived from what the screens actually consume");
    `Game Board Design.md` → Everything Here Is Theme-Driven;
    `design_handoff_game_ui/README.md` → the critical architectural constraint callout.*
    *Testable:* the hardcoded-theme-value scan (`P1-05-theme-guard-test.md`) reports zero
    violations for this layer's files.

18. **The concrete values quoted in this PRD are Neon's**, and they belong in the theme file
    rather than in this layer's code — Neon draws the hint at 12pt `#75798c`, the legend at
    10.5pt `#595d6c`, and the ring-explanation lines at 12pt `#b2b6ca`.
    *Source: `design-files/… Screens.dc.html` → `#1d`, `#1e`, `#2d`;
    `design_handoff_game_ui/README.md` → Design tokens → Type; `neon.theme.json`.*
    Whether a slot for this typography exists is unresolved — see Open Questions.

19. **Legibility of this layer is a contract on every theme, not just Neon.** It carries the
    only words that explain the game; a theme that renders them unreadable breaks the same
    thing a theme that hides the last-move highlight breaks.
    *Source: `Theming.md` → What a Theme Controls, closing note ("**Every theme must keep
    these legible** … A pretty theme that hides the last move is a broken theme");
    `Game Board Design.md` → Player Feedback / Affordances, closing note ("every one of them
    is theme-driven, so **each theme has to solve this, not just the default one**").*

20. **This layer's text does not scale with the iOS Dynamic Type setting.**
    *Source: `Menus and UI.md` → Decisions → Do we support Dynamic Type? ("**Not for now.**
    *'Lets not do this as of yet.'*").*

### Tests

21. **The layer is covered by widget tests, with no golden image tests** — each element is
    addressable in the widget tree so a test can assert its presence and its text without
    comparing pixels.
    *Source: `Tech Design.md` → Decisions → Widget tests for the board — no golden tests.*

22. **Tests run locally** via `flutter test`. There is no CI; nothing runs them on a push.
    *Source: `Tech Design.md` → Decisions → CI — local builds only.*

## Out of Scope

Named here so the boundary is explicit. Each is specified elsewhere; do not specify it here.

- **The board and every quadrant / cell treatment the legend refers to** — the open, locked,
  claimed and cat-game quadrant states, the three highlights, board geometry and the z-order:
  `P3-01-board-rendering.md`. This PRD renders swatches *matching* those treatments and
  defines none of them.
- **The two-tap gesture the hint describes** — select, confirm, reselect, tap-outside to
  clear, illegal taps doing nothing, and the haptic on valid taps: `P3-02-move-input.md`.
  This PRD describes the gesture in words and implements none of it.
- **The scoreboard, the turn-indicator highlight and the settings button** —
  `P3-03-scoreboard-turn-indicator.md`.
- **The turn banner itself** — whether it is built at all, and its "Player One, you're up!"
  copy and provisional "Play here? / Tap again to lock it in" voice. Unowned and unsettled;
  see Open Questions. Requirement 10 requires *that* the free-choice state is stated in
  words, not that the banner is the thing stating it.
- **The rules being explained** — the sending rule, claims, cat game, free choice, win and
  draw detection: `P1-02-engine-rules.md`.
- **The theme mechanism** — the theme object, its slots, loading and merge-over-Neon:
  `P1-03-theme-system.md`. This PRD says which slots this layer needs, not how they load.
- **Game-over presentation** — the winner and draw modals and their explanatory copy
  ("The big board filled up with no three in a row. Cat game."): the game-over PRD.
- **A fuller Rules / How-to-Play screen or menu item.** Explicitly not settled; see Open
  Questions. This PRD covers the on-board layer only.
- **Localisation.** No design doc raises it; the strings above are specified in English as
  the docs word them.
- **Anything from `Alternative Game Styles.md`** — a declared parking-lot doc, explicitly not
  the game being built.

## Open Questions

### From the design docs — unresolved, worded as the docs word them

- **Is there also a fuller Rules/How-to-Play screen**, separate from the on-board legend and
  hint, or does the legend/hint fully cover "how to play" for this version? (Already listed
  above as a future menu item to consider.)
  *(`Menus and UI.md` → Open Questions. The same doc's Open Questions also lists
  "Future menu items to consider later: Rules/How to Play, Settings, vs. AI, Online.")*
  This PRD builds the on-board layer only, per that Decision's own hedge: *"Whether there is
  also a fuller Rules/How-to-Play screen is left open."*

- **Is the turn banner drawn above the board in the approved handoff actually built, and does
  it carry the free-choice text cue (`Free choice — pick any board`)?** Right now the
  scoreboard's name-highlight is the *only* whose-turn mechanism in these docs, but
  `Game Board Design.md` says that cue must be "unmissable" because both players share one
  phone — the turn banner is the redundancy the approved design provides for exactly that
  case, stating whose turn it is in words. Three PRDs each deferred the banner to another and
  none of them accepted it, so as things stand it does not get built.
  *(`Menus and UI.md` → Open Questions.)*
  **This blocks requirement 10's placement**, not its existence: the handoff hosts the
  free-choice cue *inside* the banner, so if the banner is not built the cue needs a home.
  `P3-01-board-rendering.md` → Out of Scope pushes the mode cue to
  `P3-03-scoreboard-turn-indicator.md`; `P3-03` → Open Questions pushes it back.

- **Which values, concretely, does Classic Red vs Blue override?** *(`Theming.md` → Open
  Questions.)* Listed because the second theme is the first real test of requirement 19 —
  this layer's text and swatches have to stay legible under a theme that is not Neon.

### Contradictions and gaps between documents — flagged, not resolved

- **The Decision does not match what the handoff actually draws.** `Menus and UI.md` →
  Decisions → How to play says the handoff draws the legend *and* the hint "on screens
  `1d`/`1e`". In the drawn screens, `1d` carries the hint plus the Open/Locked/Cat-game
  legend; `1e` carries **neither** — its bottom strip is the two ring-explanation lines
  instead; and `2d` carries a **third**, different pair of lines. So the bottom strip is
  state-dependent in the approved design and the Decision describes it as fixed. Requirements
  2, 5, 7 and 9 build what is drawn; which strip appears in which state is the next question.

- **Does the Open/Locked/Cat-game legend appear in every board state, or only in free
  choice?** It is drawn only on `1d`, the free-choice/opening screen. Nothing says whether it
  persists once a quadrant is forced, or is replaced by the ring explanations. Likewise
  **does the hint appear outside `1d`?** It is drawn only there, and a first-time player is
  most confused on their *first forced* move, not their opening one.

- **The free-choice cue has two different wordings.** `Game Board Design.md` → The free-choice
  state proposes *"Free choice — pick any open quadrant"*; the handoff draws *"Free choice —
  pick any board"*. Related: the handoff's player-facing copy calls a quadrant a **board**
  throughout ("pick any board", "Play the middle board", "The only board you can play in
  right now"), while `Game Overview.md` → Terminology fixes the working vocabulary as
  **quadrant / section** for the outer cells and **small board** for the inner 3x3. Since this
  entire PRD is about the words shown to a player, which vocabulary the player sees needs a
  decision.

- **`Game Board Design.md` has no `## Decisions` section**, and its free-choice text cue is
  hedged — free choice *"**may** want a calmer treatment … **or** a text cue"* — i.e. offered
  as an alternative or supplement, never concluded. Requirement 10 exists because the
  approved handoff drew it and `Menus and UI.md` put the explanatory layer in scope, not
  because that sentence settled it. Already flagged by `P3-01-board-rendering.md`.

### Raised by this PRD — not discussed in any design doc, and flagged rather than answered

Each is a place an implementer would otherwise have to guess.

- **Do the hint and legend persist forever, or fade once a player clearly knows the game?**
  No doc addresses it. They are training wheels on the screen with the tightest vertical
  budget in the app, and a player on their fortieth game is paying for them. If they can
  fade, on what trigger — a move count, a games-played count, a setting, a dismiss control?
  A dismiss control would also need somewhere to bring them back.

- **Vertical budget: what happens at frames other than 402pt?** The handoff commits its
  spacing at a 402 × 874 frame with 62pt top and 44pt bottom padding, and this layer sits in
  the same strip that `P3-01-board-rendering.md` is already fighting for height in — that
  PRD's own open question asks the same thing of the board. iPhone SE is 375pt. Whether the
  hint and legend shrink, drop lines, or are dropped entirely before the board gives up any
  of its 81-cells-visible requirement (requirement 13) is unstated, and requirement 20 rules
  out Dynamic Type as the mechanism.

- **Is there a theme slot for this layer's typography?** `Theming.md` → What a Theme Controls
  and `P1-03-theme-system.md` requirement 15 were rewritten to derive the slot list from what
  the screens consume, and the resulting inventory names board, highlights, turn indicator,
  scoreboard, modals, sheets, the settings card, open-game rows, chips, badges and the logo —
  **but no legend and no hint**. `neon.theme.json`'s type scale has a generic `caption` entry
  and nothing more specific. Requirement 17 cannot be satisfied without a slot, so either
  `P1-03`'s inventory gains one or this layer has to borrow an existing slot — and which is
  not a call this PRD should make.

- **Does the explanatory layer stay on screen once the game is over?** The winner and draw
  modals overlay the finished board, which stays visible behind at 60%
  (`design_handoff_game_ui/README.md` → 1g / 1h). Nothing says whether the hint and legend
  are still drawn under the scrim, and the hint would then be describing a move that can no
  longer be made.

- **Do the ring-explanation lines appear before there is anything to explain?** On the very
  first move of a game there is no last move, so *"They played here last — that's what sent
  you."* has no referent, and no quadrant is forced. `1d` shows the swatch legend instead,
  which suggests they do not — but nothing states the rule.
