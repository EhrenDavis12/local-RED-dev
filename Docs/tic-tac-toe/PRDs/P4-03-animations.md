# PRD: Animation System

> **Status:** Draft · Source docs read: `Animations.md` (primary), `Theming.md`,
> `Game Board Design.md`, `Tech Design.md`, `Menus and UI.md`, `Game Overview.md`,
> `Rules.md`, `roadmap.md`, plus the read-only reference asset `design_handoff_game_ui/`
> (`README.md` → *2b — Settings page*, *Interactions & behavior*, *State*;
> `neon.theme.json` → `animation`). `Alternative Game Styles.md` is a declared parking-lot
> doc and was read only to confirm it is out of scope — no requirement here comes from it.

**Wave:** P4 · **File:** `P4-03-animations.md`

**Dependencies:**

- `P1-03-theme-system.md` — owns the theme object, the animation **slots** on it, the
  merge-over-Neon materialization, and the fact that each animation carries its own
  duration. This PRD owns what those slots *do* at runtime; it defines no new slot shape.
- `P2-01-board-rendering.md` — owns the marks, the three highlights and the quadrant/cell
  states this system animates on top of.
- `P3-04-settings.md` — owns the Settings screen and the Animations toggle's UI.
- `P1-04-persistence.md` — owns storing the toggle's value across sessions.
- `P1-05-theme-guard-test.md` — enforces that no `Duration` is hardcoded in source, which
  is the mechanical guard on Requirement 10.

**Note on source status:** `Animations.md` carries the house banner *"Nothing here is
settled"* while also carrying a `## Decisions` section with eight settled entries. This
PRD sources its requirements from those Decisions and from the narrative sections they
point at, and leaves anything the doc explicitly hedges in **Open Questions**. In
particular, the values in `design_handoff_game_ui/neon.theme.json → animation` are
described by `Animations.md` → Where Animations Fire as *"starting values, in the handoff's
own words — not decisions"*, and are treated here as a starting point for authoring, never
as a requirement.

---

## Problem

The board can be fully correct and completely lifeless. `Animations.md` → The Direction
states the game is aimed partly at kids and needs to feel alive — *"snappy and playful, not
slow and cinematic"* — and today nothing moves: a mark placed on an 81-cell grid simply
appears, and a claimed quadrant simply changes state, with no moment of feedback that
something happened.

The other half of the problem is structural. `P1-03-theme-system.md` puts animation slots
on the theme object and gives each one its own duration, but nothing reads them. Until
something does, motion is either absent or — worse — typed directly into a widget as a
literal `Duration`, which is exactly the escape from the Architectural Rule that
`Tech Design.md` → Decisions → Do we add a test that fails on hardcoded theme values? calls
out. And there is no runtime path for the Animations toggle: a player who turns animations
off currently has nothing to turn off.

## Goal

The player's marker moves. Placing a mark pops, and the other animated moments the theme
defines play from the theme's own definitions — type and duration both — so that swapping
themes swaps the animation personality with no change to game, board or menu code.
Exactly one animation plays at a time, none of them ever blocks or delays input, and the
whole layer can be switched off from Settings, at which point the game does the thing
instantly with no substitute effect. Because the layer is purely additive, the game remains
fully playable and fully readable with every animation stripped out.

## Requirements

### Direction and scope

1. **Animations are poppy** — snappy and playful rather than slow and cinematic. The
   implementation targets that feel; timing values that read as cinematic are wrong for
   this game.
   *Source:* [Animations](../Animations.md) → The Direction.
2. **Only the player's marker is animated in this version** — whatever the active theme
   says that marker is (an X, an O, a checkbox, an icon, an image). "The marker is the
   thing that moves."
   *Source:* [Animations](../Animations.md) → Scope For Now; corroborated by
   [Theming](../Theming.md) → What a Theme Controls → Animation and
   [Game Board Design](../Game%20Board%20Design.md) → Animation & Juice.
3. **The board, the layout, and transitions between screens are not animated.** A change to
   any of those three renders without motion.
   *Source:* [Animations](../Animations.md) → Scope For Now.
4. The animation vocabulary this system must be able to express is: **grow & shrink** (the
   signature move — enlargement and shrinking of the marker, growing then shrinking or
   shrinking then growing), **glow / backlight**, **shadowbox** (a drop-shadow / raised-box
   effect that lifts the marker off the board), **jiggle** (in place), and **dance** (moving
   the marker around the screen a little).
   *Source:* [Animations](../Animations.md) → The Animation Vocabulary.

### Animations belong to the theme

5. **Every animation played comes from the active theme.** No motion originates in game,
   board or menu code: *"If something moves, that motion came from the theme. No
   exceptions."*
   *Source:* [Theming](../Theming.md) → Architectural Rule;
   [Animations](../Animations.md) → Animation Sets Are Part of the Theme.
6. **There is no shared animation library and no menu of animations for a theme to pick
   from.** A theme authors its own animations; the vocabulary in Requirement 4 is
   *direction*, not a fixed option set the runtime enumerates. Nothing in the
   implementation may present animations as a closed list a theme selects an index into.
   *Source:* [Animations](../Animations.md) → Decisions → Themes author their own
   animations — no shared library.
7. **A theme's animations merge over Neon's**, overriding only what the theme names —
   the same inheritance rule as every other theme value, resolved once at
   materialization rather than per lookup.
   *Source:* [Animations](../Animations.md) → Decisions → Do themes inherit Neon's
   animations?; [Tech Design](../Tech%20Design.md) → Decisions → Fallback to Neon — merge,
   not resolve.
8. **Neon's animation set is complete** — every moment the game animates has a Neon
   definition, because Neon is the fallback for every other theme. A moment that can play
   an animation but has no Neon entry is a defect.
   *Source:* [Animations](../Animations.md) → Animations Inherit From Neon;
   [Theming](../Theming.md) → Neon Is the Base Theme → Why this matters for the build.
9. A different theme brings a **different animation personality** — the animation set
   travels with the theme, so selecting a different theme changes how things move without
   any code change.
   *Source:* [Animations](../Animations.md) → Animation Sets Are Part of the Theme;
   [Theming](../Theming.md) → What Is a Theme?

### Playback rules

10. **Duration lives in the animation, not globally.** Each animation definition carries
    its own timing, so a theme controls its own pacing. There is no global animation-speed
    or duration-multiplier value anywhere, and changing one animation's duration in a theme
    file changes that animation only.
    *Source:* [Animations](../Animations.md) → Decisions → Duration lives in the animation.
    Mechanically guarded by `P1-05-theme-guard-test.md`: a hardcoded `Duration` in scanned
    source is a theme value that escaped.
11. **One animation at a time — animations never overlap.** At no point are two animations
    running simultaneously.
    *Source:* [Animations](../Animations.md) → Decisions → One animation at a time.
12. **Animations never block input.** While an animation is playing, taps are accepted and
    processed exactly as they would be with no animation running, and the game does not
    wait on the animation before changing state.
    *Source:* [Animations](../Animations.md) → Decisions → Animations don't block input.
13. **A tapped-through animation is neither interrupted nor skipped** — it keeps playing as
    normal to its full duration.
    *Source:* [Animations](../Animations.md) → Decisions → Animations don't block input.

### The off switch

14. **There is a global animations on/off toggle**, and it is **not theme-defined**: it is
    a player setting that sits alongside the sound-effects and vibrate toggles in the
    Settings menu. No theme file key can set, override or read it, and switching themes
    does not change its value.
    *Source:* [Animations](../Animations.md) → Decisions → Turn animations off — a global
    setting; [Menus and UI](../Menus%20and%20UI.md) → Settings Menu;
    [Theming](../Theming.md) → What a Theme Does NOT Control.
15. **iOS Reduce Motion does not drive the toggle.** With Reduce Motion enabled and the
    game's Animations toggle on, animations still play. There is exactly one control and
    the player owns it: *"no lets leave this as a game setting for user to command."*
    *Source:* [Animations](../Animations.md) → Decisions → Does iOS Reduce Motion drive the
    animations toggle?
16. **Animations off = instant state change.** With the toggle off, the mark simply
    appears and the quadrant is simply claimed. No animation runs, and **no substitute
    effect, fade or transition stands in for one**.
    *Source:* [Animations](../Animations.md) → Decisions → Animations off = instant state
    change.
17. With the toggle off, the game state changes and the screen shows the new state — and
    nothing else in the game behaves differently. The off path is not a second, shorter
    animation path; it is the absence of one.
    *Source:* [Animations](../Animations.md) → Decisions → Animations off = instant state
    change (*"Don't worry about animations at all in this mode"*).

### Animations are a pure layer on top

18. **The game is fully playable and fully readable with every animation stripped out.**
    Nothing an animation communicates may be communicated *only* by that animation — every
    board state the player needs (last move, active quadrant, locked quadrants, pending
    preview, claimed, cat game, whose turn) remains legible with animations off.
    *Source:* [Animations](../Animations.md) → Decisions → Animations off = instant state
    change → *"Practical consequence: animations are a pure layer on top."* Restated as a
    test in [Design Handoff](../design_handoff_game_ui/README.md) → Interactions & behavior:
    *"Every screen above is fully readable with animation off — that is the correctness
    test."*
19. Removing the animation layer entirely must not change any game outcome, any legality
    decision, or any persisted state. Animation is presentation only; it is not part of
    the rules engine, which is pure Dart with zero Flutter imports.
    *Source:* Requirement 18 above, plus [Tech Design](../Tech%20Design.md) → Decisions →
    Is the game logic separate from Flutter?

### Where animations fire

> `Animations.md` → Where Animations Fire opens with **"Not yet decided in detail, but the
> obvious moments"**. That hedge is carried forward deliberately: the moments below are
> what the doc lists, not a settled set. Requirement 20 is written so it holds whatever the
> final list turns out to be.

20. **Every moment the game animates plays its animation from the active theme's slot for
    that moment, and has a Neon definition** (per Requirement 8). Adding or removing an
    animated moment is a theme-data and slot change, not a change to board or menu code.
    *Source:* [Animations](../Animations.md) → Where Animations Fire; Animations Inherit
    From Neon; [Theming](../Theming.md) → Architectural Rule.
21. **Placing a marker is the primary animated moment** — "the mark appears with a pop."
    If only one moment is animated in a first cut, this is it.
    *Source:* [Animations](../Animations.md) → Where Animations Fire.
22. The further moments the doc lists as obvious candidates are: **winning a small board /
    claiming a quadrant**, **cat game**, and **winning the whole game**. The doc also notes
    the **last-move highlight and active-quadrant highlight** *"could be animated rather
    than static, e.g. a pulsing glow on the legal quadrant"* — recorded here as the doc's
    hedge, not as a commitment that they are animated. See **Open Questions**.
    *Source:* [Animations](../Animations.md) → Where Animations Fire;
    [Game Board Design](../Game%20Board%20Design.md) → Last Move Highlight, Active Quadrant
    Highlight.
23. `design_handoff_game_ui/neon.theme.json → animation` supplies **starting values** for
    `placeMark`, `claimQuadrant`, `catGame`, `winGame`, `activeQuadrant` and `lastMove`,
    each with a type and a duration (the last two drawn as looping glow-pulses). These are
    the starting point for authoring Neon's set. They are **starting values in the
    handoff's own words — not decisions** — and no requirement in this PRD fixes any of
    those types or numbers.
    *Source:* [Animations](../Animations.md) → Where Animations Fire, which says exactly
    this; [Design Handoff](../design_handoff_game_ui/README.md) → Interactions & behavior.

## Out of Scope

- **The theme mechanism and where the animation keys live** — the theme object's shape, the
  animation slots on it, YAML loading, UUID identity, and merge-over-Neon materialization:
  `P1-03-theme-system.md`. This PRD consumes those slots and defines none of them.
- **The last-move and active-quadrant highlights themselves** — their static treatments,
  their two modes, their distinguishability, and the locked/pending states they sit
  alongside: `P2-01-board-rendering.md`. Whether either is animated is an open question
  below, not a requirement here.
- **The Settings toggle's UI** — where the Animations row sits, its label, and its switch
  behavior: `P3-04-settings.md`. This PRD specifies only what the toggle *does*.
- **Persisting the toggle** across sessions via `shared_preferences`:
  `P1-04-persistence.md`.
- **The Classic Red vs Blue theme's animation choices.** Classic inherits Neon's animations
  unless it overrides them, and what it overrides is `P4-04-classic-theme.md`.
  *(`Theming.md` → Theme Catalog → Theme 2 — Classic Red vs Blue → What it inherits from
  Neon; and → Watch out for, which notes a partial theme inherits Neon's *personality*.)*
- **The hardcoded-`Duration` scan** — the guard test that fails when a literal `Duration`
  appears in scanned source: `P1-05-theme-guard-test.md`. Requirement 10 states the rule;
  that PRD owns the check.
- **Sound and haptics.** They fire at the same moments and are switched by sibling toggles,
  but they are separate channels: audio is theme-driven (`Theming.md` → Sound Decisions)
  and haptics are explicitly *not* theme-driven (`Theming.md` → What a Theme Does NOT
  Control). Nothing here couples an animation to a sound or a buzz.
- **Board, layout and screen-transition animation.** Excluded by Requirement 3, not
  deferred to another PRD — the docs say it is not being built yet.
- **Producing any animation asset.** Art and audio assets are generated with Replicate when
  actually needed, not now (`Tech Design.md` → Decisions → Where do sound and art assets
  come from?).

## Open Questions

### From the design docs, worded as the docs word them

`Animations.md` → Open Questions is empty (*"Nothing outstanding on this doc right now"*).
The hedges below are carried from the body of the doc rather than from that section.

- **Where animations fire is "not yet decided in detail."** `Animations.md` → Where
  Animations Fire lists placing a marker, winning a small board / claiming a quadrant, cat
  game, and winning the whole game as *"the obvious moments"* — the list is explicitly not
  settled, and this PRD does not settle it.
- **Should the last-move and active-quadrant highlights be animated at all?** As worded:
  *"The last-move highlight and active-quadrant highlight … these could be animated rather
  than static, e.g. a pulsing glow on the legal quadrant."* Left open.
- Which values, concretely, does Classic Red vs Blue override? (`Theming.md` → Open
  Questions. Listed here only because animations are among the values in question;
  `P4-04-classic-theme.md` owns it.)

### Contradictions between docs — flagged, not resolved

- **Marker-only scope vs. animating the highlights.** `Animations.md` → Scope For Now says
  animations apply to **the player's marker** and that *"the marker is the thing that
  moves"*; `Theming.md` → What a Theme Controls → Animation repeats this. But the same doc's
  Where Animations Fire raises animating the **active-quadrant highlight** (a whole
  quadrant, not a marker), and `neon.theme.json → animation` carries `activeQuadrant` and
  `claimQuadrant` entries. Requirements 2 and 22 record both sides without picking one.
  Someone has to say whether "marker only" is a hard boundary this version holds, or a
  starting scope the quadrant-level entries already exceed.
- **"One animation at a time, never overlapping" vs. looping glow-pulses.**
  `Animations.md` → Decisions → One animation at a time is unambiguous. The handoff's
  starting values give `activeQuadrant` and `lastMove` `"loop": true` — animations that by
  construction run continuously, and so would be running whenever a `placeMark` pop fires.
  These cannot both be true as literally stated. The handoff values are declared "not
  decisions," so the Decision wins by default; but if the looping highlight pulses are
  wanted, the one-at-a-time rule needs restating (e.g. as "one *transient* animation at a
  time"). This one blocks implementation of Requirement 11 the moment a looping highlight
  is authored.
- **Shadowbox is missing from the Decisions restatement.** `Animations.md` → The Animation
  Vocabulary lists five items including **Shadowbox**; the Decisions entry *Themes author
  their own animations — no shared library* restates the vocabulary as *"(grow/shrink,
  glow, jiggle, dance)"*, dropping it. `Theming.md` → What a Theme Controls → Animation
  keeps shadowbox. Requirement 4 keeps all five, on the grounds that the vocabulary section
  is the definition and the Decisions line is an abbreviation — but it is an inconsistency
  in the doc, and `forge-doc-writer`'s to fix, not mine.

### Raised by this PRD, not by the design docs (proposals, clearly mine)

- **What happens when a second animation is triggered while one is playing?** Requirements
  11, 12 and 13 pin three things — one at a time, input is never blocked, and a running
  animation is never interrupted or skipped — and together they leave exactly one gap: a
  player can tap through a playing animation, which produces a second trigger, and the docs
  do not say whether that second animation queues behind the first, is dropped, or replaces
  it. "Never overlap" rules out playing both; "never interrupted" rules out cutting the
  first short. Queue and drop are both consistent with the letter of the docs and feel very
  different in the hand. An implementer will otherwise guess, and this is the single most
  likely thing to be guessed wrong.
- **Does an animation have to finish before the state it depicts is committed?**
  Requirement 12 says the game does not wait on the animation, which implies state commits
  immediately and the animation plays over the already-changed state. Worth confirming,
  because the opposite reading (animate, then commit) would break requirement 12 and is a
  natural thing to build by accident.
- **Is there a "currently animating" state anywhere in persisted game state?** The handoff's
  *State* section does not include one, and Requirement 19 says animation is presentation
  only — so backgrounding the app mid-animation should simply lose it. Not stated anywhere;
  stating it would close off a class of save-file bug.
