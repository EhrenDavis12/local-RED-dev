# PRD: Animation System

> **Status:** Draft · Source docs read: `Animations.md` (primary), `Theming.md`,
> `Game Board Design.md`, `Tech Design.md`, `Menus and UI.md`, `Game Overview.md`,
> `Rules.md`, `roadmap.md`, plus the read-only reference asset `design_handoff_game_ui/`
> (`README.md` → *2b — Settings page*, *Interactions & behavior*, *State*;
> `neon.theme.json` → `animation`). `Alternative Game Styles.md` is a declared parking-lot
> doc and was read only to confirm it is out of scope — no requirement here comes from it.

**Wave:** P2 · **File:** `P2-04-animations.md` — parallel-safe with the other P2 PRDs.

**Dependencies:**

- `P1-01-app-scaffold.md` — the Riverpod root this layer's provider hangs off, and the
  `lib/` structure it lives in.
- `P1-03-theme-system.md` — owns the theme object, the animation **slots** on it (req 18),
  the merge-over-Neon materialization, and the Riverpod exposure of the active theme
  (req 24). This PRD owns what those slots *do* at runtime; it defines no new slot shape.
- `P1-04-persistence.md` — stores the animations toggle's value across sessions. This PRD
  reads it.
- `P1-05-theme-guard-test.md` — bans a hardcoded `Duration` in scanned source (its req 5),
  exempting only `lib/theme/` (its req 3). See OQ under *Raised by this PRD*: whether a
  **theme-derived** `Duration` constructed in this layer is permitted is unsettled, and
  that seam sits between the two PRDs.

> **The toggle is a persisted preference, not a settings-screen behavior.** This PRD reads
> the stored value through `P1-04-persistence.md`. `P4-04-settings.md` draws the switch and
> owns no part of what "off" means — so it is a wave-4 consumer of this feature, not a
> dependency of it.

**Depended on by:**

- `P3-01-board-rendering.md` — owns the marks, the three highlights and the quadrant/cell
  states this system animates on top of. Its req 31 is the board-side half of Requirement
  21 here. **Note:** its Out of Scope defers *"the looping glow-pulse on the active quadrant
  and the last move"* to this PRD as committed work — see **Open Questions**; whether those
  two are animated at all is not settled, so that deferral asserts an answer this PRD does
  not have.
- `P3-02-move-input.md` — fires the `placeMark` moment on the confirming tap; its req 18 is
  the caller-side half of Requirements 15–16 here.
- `P3-04-game-over-rematch.md` — its req 14 is the caller-side half of Requirements 19–21.
- `P4-04-settings.md` — draws the Animations toggle whose behavior is Requirements 17–20.

**Note on source status:** `Animations.md` carries the house banner *"Nothing here is
settled except what's under **Decisions**"* and carries a `## Decisions` section with eight
settled entries. This PRD sources its requirements from those Decisions and from the
narrative sections they point at, and leaves anything the doc explicitly hedges in **Open
Questions**. In particular, the values in `design_handoff_game_ui/neon.theme.json →
animation` are described by `Animations.md` → Where Animations Fire as *"starting values, in
the handoff's own words — not decisions"*, and are treated here as a starting point for
authoring, never as a requirement.

> **On the acceptance floor.** An earlier draft of this PRD made every animated moment
> conditional, which left acceptance criteria an empty implementation could satisfy. That is
> fixed: **Requirement 23 commits `placeMark` unconditionally.** The judgment behind that —
> and it is a judgment, so it is stated rather than buried — is that `Animations.md` →
> Where Animations Fire hedges *which moments make the full list*, not *whether anything
> animates*: it calls placing a marker *"the primary one"*, and placing a marker is the only
> listed moment that falls squarely inside the settled marker-only scope of → Scope For Now.
> The other moments are quadrant- or board-level and are entangled with the unresolved
> marker-only-vs-quadrant scope question below, so they stay open.

---

## Problem

The board can be fully correct and completely lifeless. `Animations.md` → The Direction
states the game is aimed partly at kids and needs to feel alive — *"snappy and playful, not
slow and cinematic"* — and today nothing moves: a mark placed on an 81-cell grid simply
appears, with no moment of feedback that something happened.

The other half of the problem is structural, and the wave move makes it urgent. This PRD now
ships **before** its consumers. `P1-03-theme-system.md` puts animation slots on the theme
object and gives each one its own duration, but nothing reads them, and no doc names an
animation layer, says how a caller asks for a moment, or says how motion reaches the active
theme and the toggle. `P3-02-move-input.md` req 18 and `P3-04-game-over-rematch.md` req 14
are already written against that interface. If it is not specified here, each wave-3
consumer invents its own — and motion typed directly into a widget as a literal `Duration`
is exactly the escape from the Architectural Rule that `Tech Design.md` → Decisions → Do we
add a test that fails on hardcoded theme values? calls out. There is also no runtime path for
the Animations toggle: a player who turns animations off currently has nothing to turn off.

## Goal

The player's marker moves. Placing a mark pops — that much ships — and any further moment
the theme defines plays from the theme's own definitions, type and duration both, so that
swapping themes swaps the animation personality with no change to game, board or menu code.
One animation layer owns all of it, so callers name a moment and nothing else. Exactly one
animation plays at a time, none of them ever blocks or delays input, and the whole layer can
be switched off, at which point the game does the thing instantly with no substitute effect.
Because the layer is purely additive, the game remains fully playable and fully readable
with every animation stripped out.

## Requirements

### Direction and scope

1. **Animations are poppy** — snappy and playful rather than slow and cinematic. The
   implementation targets that feel; timing values that read as cinematic are wrong for
   this game.
   *Source:* [Animations](../Animations.md) → The Direction.
   *Testable:* not mechanically testable — this is a review criterion on the authored Neon
   values, not on code. The values themselves are `P1-03-theme-system.md`'s slot data.
2. **Only the player's marker is animated in this version** — whatever the active theme
   says that marker is (an X, an O, a checkbox, an icon, an image). "The marker is the
   thing that moves."
   *Source:* [Animations](../Animations.md) → Scope For Now; corroborated by
   [Theming](../Theming.md) → What a Theme Controls → Animation and
   [Game Board Design](../Game%20Board%20Design.md) → Animation & Juice.
   *Testable:* the only widget this layer animates is the mark widget. **Subject to the
   marker-only-vs-quadrant open question below** — if quadrant-level moments are confirmed,
   this requirement changes.
3. **The board, the layout, and transitions between screens are not animated.** A change to
   any of those three renders without motion.
   *Source:* [Animations](../Animations.md) → Scope For Now.
   *Testable:* navigating between screens, and any layout change, produces no tween — the
   new frame is the new state. Screen routing is `P2-01-navigation.md`'s; this requirement
   constrains it to no transition animation.
4. The animation vocabulary this system must be able to express is: **grow & shrink** (the
   signature move — enlargement and shrinking of the marker, growing then shrinking or
   shrinking then growing), **glow / backlight**, **shadowbox** (a drop-shadow / raised-box
   effect that lifts the marker off the board), **jiggle** (in place), and **dance** (moving
   the marker around the screen a little).
   *Source:* [Animations](../Animations.md) → The Animation Vocabulary; all five are also
   listed in → The Direction and in → Decisions → Themes author their own animations — no
   shared library, and in [Theming](../Theming.md) → What a Theme Controls → Animation.
   *Testable:* each of the five is expressible by an authored theme animation. Note this
   is a floor on expressiveness, not a closed list — see Requirement 9.

### The animation layer

> **Derived, not stated.** No design doc names an animation layer or an interface. The three
> requirements in this section are the shape the cited rules force, and they are here because
> this PRD now ships before its consumers and they would otherwise each invent one. If a
> different structure satisfies Requirements 8, 14 and 15, these are negotiable.

5. **All animation playback goes through one animation layer.** The board, the menus and the
   game-over surface request a **named animation moment**; they never construct an
   `AnimationController`, a `Duration`, a curve or a tween themselves, and never read an
   animation slot off the theme directly.
   *Derived from:* [Theming](../Theming.md) → Architectural Rule (*"if something moves, that
   motion came from the theme"*) plus [Tech Design](../Tech%20Design.md) → Decisions → Do we
   add a test that fails on hardcoded theme values?, which bans hardcoded `Duration(…)`
   outside the theme layer — so a caller cannot hold its own timing. Requirement 14
   (one at a time) is also unenforceable if every caller animates independently.
   *Testable:* no `AnimationController`, `Duration` literal or animation-slot read appears
   in `lib/ui/` outside this layer; a caller's entire animation surface is naming a moment.
6. **Requesting a moment is fire-and-forget.** The call returns immediately, returns nothing
   the caller must await, and the caller never learns whether an animation played, was
   dropped, or was skipped because the toggle is off. This is what makes Requirements 15, 19
   and 20 implementable at every call site rather than at some of them.
   *Derived from:* [Animations](../Animations.md) → Decisions → Animations don't block input
   (*"the game doesn't wait on it"*) and → Animations off = instant state change (*"Don't
   worry about animations at all in this mode"*).
   *Testable:* the request call is synchronous and non-awaitable; with the toggle off it is
   a no-op that returns identically; no caller branches on animation state.
7. **The animation layer reads the active theme and the animations setting through
   Riverpod** (plain `Notifier`/`NotifierProvider`, no `@riverpod` codegen), so both are
   readable from anywhere that fires a moment, including deep in the board widget tree.
   *Source:* [Tech Design](../Tech%20Design.md) → Decisions → State management — Riverpod
   (which explicitly covers *"the requirement that settings and the theme be readable from
   everywhere, including deep in the board widget tree"*); `P1-03-theme-system.md` req 24.
   *Testable:* overriding the theme provider changes which animation plays for the same
   named moment, with no change at the call site.

### Animations belong to the theme

8. **Every animation played comes from the active theme.** No motion originates in game,
   board or menu code: *"If something moves, that motion came from the theme. No
   exceptions."*
   *Source:* [Theming](../Theming.md) → Architectural Rule;
   [Animations](../Animations.md) → Animation Sets Are Part of the Theme.
   *Testable:* with a theme whose animation set is replaced wholesale, every animation the
   app plays changes, and no code outside `lib/theme/` and this layer is touched.
9. **There is no shared animation library and no menu of animations for a theme to pick
   from.** A theme authors its own animations; the vocabulary in Requirement 4 is
   *direction*, not a fixed option set the runtime enumerates. Nothing in the
   implementation may present animations as a closed list a theme selects an index into.
   *Source:* [Animations](../Animations.md) → Decisions → Themes author their own
   animations — no shared library.
   *Testable:* no enum, constant list or switch over a fixed set of animation kinds gates
   what a theme may author. **The value shape that makes this satisfiable is
   `P1-03-theme-system.md` req 18's, and that PRD ships first** — see Open Questions.
10. **A theme's animations merge over Neon's**, overriding only what the theme names —
    the same inheritance rule as every other theme value, resolved once at
    materialization rather than per lookup. This layer therefore performs **no fallback at
    play time**; it plays whatever the materialized active theme holds.
    *Source:* [Animations](../Animations.md) → Decisions → Do themes inherit Neon's
    animations?; [Tech Design](../Tech%20Design.md) → Decisions → Fallback to Neon — merge,
    not resolve.
    *Testable:* a theme that overrides one animation and nothing else plays its own for that
    moment and Neon's for every other; no lookup in this layer has a fallback branch.
11. **Neon's animation set is complete** — every moment the game animates has a Neon
    definition, because Neon is the fallback for every other theme. A moment that can play
    an animation but has no Neon entry is a defect.
    *Source:* [Animations](../Animations.md) → Animations Inherit From Neon;
    [Theming](../Theming.md) → Neon Is the Base Theme → Why this matters for the build.
    *Testable:* for every named moment this layer can be asked to play, Neon resolves a
    definition — assertable as a test over the moment inventory against the materialized
    Neon theme.
12. A different theme brings a **different animation personality** — the animation set
    travels with the theme, so selecting a different theme changes how things move without
    any code change.
    *Source:* [Animations](../Animations.md) → Animation Sets Are Part of the Theme;
    [Theming](../Theming.md) → What Is a Theme?
    *Testable:* covered by Requirements 8 and 10's tests; adding a theme adds a theme file
    and changes no code.

### Playback rules

13. **Duration lives in the animation, not globally.** Each animation definition carries
    its own timing, so a theme controls its own pacing. There is no global animation-speed
    or duration-multiplier value anywhere, and changing one animation's duration in a theme
    file changes that animation only.
    *Source:* [Animations](../Animations.md) → Decisions → Duration lives in the animation.
    *Testable:* editing one slot's duration in a theme file changes that animation's runtime
    duration and no other's; no global speed constant or multiplier exists.
    *Seam:* `P1-05-theme-guard-test.md` req 5 makes a hardcoded `Duration` a violation and
    its req 3 exempts only `lib/theme/`. This layer must construct a `Duration` **from a
    theme value** at playback, outside that exempt path. Whether that is permitted is
    unsettled — see Open Questions. This PRD states the rule; it does not claim `P1-05` is
    its mechanical guard.
14. **One animation at a time — animations never overlap.** At no point are two animations
    running simultaneously.
    *Source:* [Animations](../Animations.md) → Decisions → One animation at a time.
    *Testable:* with a clock the test controls, requesting a second moment while one is in
    flight never results in two concurrently running animations. **What happens to that
    second request — queue, drop, or replace — is unsettled** (Open Questions); this
    requirement asserts only that they do not overlap.
15. **Animations never block input.** While an animation is playing, taps are accepted and
    processed exactly as they would be with no animation running, and the game does not
    wait on the animation before changing state.
    *Source:* [Animations](../Animations.md) → Decisions → Animations don't block input.
    *Testable:* a tap dispatched mid-animation produces the same state change, in the same
    number of frames, as the same tap dispatched at rest. (Mirrors
    `P3-02-move-input.md` req 18's caller-side assertion.)
16. **A tapped-through animation is neither interrupted nor skipped** — it keeps playing as
    normal to its full duration.
    *Source:* [Animations](../Animations.md) → Decisions → Animations don't block input.
    *Testable:* an animation whose duration is *d* still completes at *d* when a tap lands
    partway through, and is not cut short, restarted or fast-forwarded.

### The off switch

17. **There is a global animations on/off toggle**, and it is **not theme-defined**: it is
    a player setting that sits alongside the sound-effects and vibrate toggles in the
    Settings menu. No theme file key can set, override or read it, and switching themes
    does not change its value.
    *Source:* [Animations](../Animations.md) → Decisions → Turn animations off — a global
    setting; [Menus and UI](../Menus%20and%20UI.md) → Settings Menu;
    [Theming](../Theming.md) → What a Theme Does NOT Control.
    *Ownership:* the stored value is `P1-04-persistence.md`'s and the switch that sets it is
    `P4-04-settings.md`'s. **What "off" means — Requirements 19 and 20 — is this PRD's.**
    *Testable:* no theme file contains an animations-enabled key; switching the active theme
    leaves the toggle's value unchanged; this layer has no default of its own and no writer.
18. **iOS Reduce Motion does not drive the toggle.** With Reduce Motion enabled and the
    game's Animations toggle on, animations still play. There is exactly one control and
    the player owns it: *"no lets leave this as a game setting for user to command."*
    *Source:* [Animations](../Animations.md) → Decisions → Does iOS Reduce Motion drive the
    animations toggle?
    *Testable:* with the platform accessibility flag forced on and the game toggle on, a
    `placeMark` request still plays an animation; nothing in the codebase reads
    `MediaQuery.disableAnimations` or the equivalent platform flag.
19. **Animations off = instant state change.** With the toggle off, the mark simply
    appears and the quadrant is simply claimed. No animation runs, and **no substitute
    effect, fade or transition stands in for one**.
    *Source:* [Animations](../Animations.md) → Decisions → Animations off = instant state
    change.
    *Testable:* with the toggle off, the new state is fully rendered in the frame the state
    changed; no tween, opacity ramp, scale or cross-fade is scheduled by any code path.
20. With the toggle off, the game state changes and the screen shows the new state — and
    nothing else in the game behaves differently. The off path is not a second, shorter
    animation path; it is the absence of one.
    *Source:* [Animations](../Animations.md) → Decisions → Animations off = instant state
    change (*"Don't worry about animations at all in this mode"*).
    *Testable:* the full move / claim / cat-game / win sequence produces identical state,
    identical timing and identical caller behavior with the toggle off as it would with the
    animation layer absent entirely.

### Animations are a pure layer on top

21. **The game is fully playable and fully readable with every animation stripped out.**
    Nothing an animation communicates may be communicated *only* by that animation — every
    board state the player needs (last move, active quadrant, locked quadrants, pending
    preview, claimed, cat game, whose turn) remains legible with animations off.
    *Source:* [Animations](../Animations.md) → Decisions → Animations off = instant state
    change → *"Practical consequence: animations are a pure layer on top."* Restated as a
    test in [Design Handoff](../design_handoff_game_ui/README.md) → Interactions & behavior:
    *"Every screen above is fully readable with animation off — that is the correctness
    test."*
    *Verified elsewhere:* this enumerates board and screen states that **do not exist until
    wave 3**, so it is not assertable here. It is verified by `P3-01-board-rendering.md`
    req 31 (board states legible with animations off), `P3-04-game-over-rematch.md` req 14
    (the game-over surface), and `P3-05-how-to-play.md` (its legend swatches). This PRD's
    obligation is to add nothing that would break it — which Requirements 19 and 20 make
    testable here.
22. Removing the animation layer entirely must not change any game outcome, any legality
    decision, or any persisted state. Animation is presentation only; it is not part of
    the rules engine, which is pure Dart with zero Flutter imports.
    *Source:* Requirement 21 above, plus [Tech Design](../Tech%20Design.md) → Decisions →
    Is the game logic separate from Flutter?
    *Testable:* the engine's test suite passes with no animation layer present and imports
    nothing from it; no persisted field describes animation state.

### Where animations fire

23. **Placing a marker is animated.** On a confirmed move, the newly placed marker plays the
    active theme's `placeMark` animation — *"the mark appears with a pop."* This is not
    conditional: an implementation in which nothing animates does not satisfy this PRD.
    *Source:* [Animations](../Animations.md) → Where Animations Fire (*"**Placing a
    marker** — the primary one. The mark appears with a pop"*), read together with → Scope
    For Now, which settles that animations apply to the player's marker and that *"the
    marker is the thing that moves"*. See the acceptance-floor note above for why this one
    moment is committed while the rest of the list stays open.
    *Testable:* with animations on, confirming a legal move records exactly one `placeMark`
    animation against the newly placed mark, running for the duration the active theme
    specifies. With the toggle off, it records none and the mark is on screen in the frame
    the move committed (Requirement 19). It fires on the **confirming** tap only — the
    pending selection animates nothing, matching `P2-02-audio.md` req 7's rule for sound.
24. **Every moment the game animates plays its animation from the active theme's slot for
    that moment, and has a Neon definition** (per Requirement 11). Adding or removing an
    animated moment is a theme-data and slot change, not a change to board or menu code.
    *Source:* [Animations](../Animations.md) → Where Animations Fire; Animations Inherit
    From Neon; [Theming](../Theming.md) → Architectural Rule.
    *Testable:* the moment inventory this layer exposes is data-driven — adding a moment to
    the inventory and to Neon's set makes it playable with no change in `lib/ui/`.

> The remainder of the list is where `Animations.md` → Where Animations Fire applies its
> hedge — **"Not yet decided in detail, but the obvious moments"**. Requirements 25 and 26
> record the candidates without committing them; they are not acceptance criteria.

25. The further moments the doc lists as obvious candidates are: **winning a small board /
    claiming a quadrant**, **cat game**, and **winning the whole game**. The doc also notes
    the **last-move highlight and active-quadrant highlight** *"could be animated rather
    than static, e.g. a pulsing glow on the legal quadrant"* — recorded here as the doc's
    hedge, not as a commitment that they are animated. See **Open Questions**.
    *Source:* [Animations](../Animations.md) → Where Animations Fire;
    [Game Board Design](../Game%20Board%20Design.md) → Last Move Highlight, Active Quadrant
    Highlight.
26. `design_handoff_game_ui/neon.theme.json → animation` supplies **starting values** for
    `placeMark`, `claimQuadrant`, `catGame`, `winGame`, `activeQuadrant` and `lastMove`,
    each with a type and a duration (the last two drawn as looping glow-pulses). These are
    the starting point for authoring Neon's set. They are **starting values in the
    handoff's own words — not decisions** — and no requirement in this PRD fixes any of
    those types or numbers, including `placeMark`'s in Requirement 23.
    *Source:* [Animations](../Animations.md) → Where Animations Fire, which says exactly
    this; [Design Handoff](../design_handoff_game_ui/README.md) → Interactions & behavior.

## Out of Scope

Referenced by filename only; this PRD specifies none of them.

- **The theme mechanism and where the animation keys live** — the theme object's shape, the
  animation slots on it and their value shape, YAML loading, UUID identity, and
  merge-over-Neon materialization: `P1-03-theme-system.md` (req 18). This PRD consumes those
  slots and defines none of them.
- **The last-move and active-quadrant highlights themselves** — their static treatments,
  their two modes, their distinguishability, and the locked/pending states they sit
  alongside: `P3-01-board-rendering.md`. Whether either is animated is an open question
  below, not a requirement here.
- **The Settings toggle's UI** — where the Animations row sits, its label, and its switch
  behavior: `P4-04-settings.md`. This PRD specifies only what the toggle *does*.
- **Persisting the toggle** across sessions via `shared_preferences`:
  `P1-04-persistence.md`.
- **The Classic Red vs Blue theme's animation choices.** Classic inherits Neon's animations
  unless it overrides them, and what it overrides is `P5-01-classic-theme.md`.
  *(`Theming.md` → Theme Catalog → Theme 2 — Classic Red vs Blue → What it inherits from
  Neon; and → Watch out for, which notes a partial theme inherits Neon's *personality*.)*
- **The hardcoded-`Duration` scan** — the guard test itself, its banned-pattern list and its
  baseline: `P1-05-theme-guard-test.md`. Requirement 13 states the rule and flags the seam;
  that PRD owns the check.
- **Firing the events.** Detecting that a move was confirmed, a quadrant claimed, a small
  board a cat game, or the game won belongs to the engine and the board PRDs
  (`P1-02-engine-rules.md`, `P3-02-move-input.md`, `P3-04-game-over-rematch.md`). This PRD
  specifies what an animation moment *is* and what plays; not who detects it.
- **Sound and haptics.** They fire at overlapping moments and are switched by sibling
  toggles, but they are separate channels: audio is theme-driven (`P2-02-audio.md`) and
  haptics are explicitly *not* theme-driven (`P2-03-haptics.md`). Nothing here couples an
  animation to a sound or a buzz, and nothing in `Animations.md` is carried across to them.
- **Board, layout and screen-transition animation.** Excluded by Requirement 3, not
  deferred to another PRD — the docs say it is not being built yet.
- **Producing any animation asset.** Art and audio assets are generated with Replicate when
  actually needed, not now (`Tech Design.md` → Decisions → Where do sound and art assets
  come from?; `P5-02-asset-generation-replicate.md`).

## Open Questions

### From the design docs, worded as the docs word them

`Animations.md` → Open Questions is empty (*"Nothing outstanding on this doc right now"*).
The hedges below are carried from the body of the doc rather than from that section.

- **Where animations fire is "not yet decided in detail."** `Animations.md` → Where
  Animations Fire lists placing a marker, winning a small board / claiming a quadrant, cat
  game, and winning the whole game as *"the obvious moments"* — the list is explicitly not
  settled, and this PRD settles only the first of them (Requirement 23), because that is
  the one the doc calls "the primary one" and the one that sits inside the settled
  marker-only scope.
- **Should the last-move and active-quadrant highlights be animated at all?** As worded:
  *"The last-move highlight and active-quadrant highlight … these could be animated rather
  than static, e.g. a pulsing glow on the legal quadrant."* Left open.
- Which values, concretely, does Classic Red vs Blue override? (`Theming.md` → Open
  Questions. Listed here only because animations are among the values in question;
  `P5-01-classic-theme.md` owns it.)

### Contradictions between docs — flagged, not resolved

- **Marker-only scope vs. animating the highlights.** `Animations.md` → Scope For Now says
  animations apply to **the player's marker** and that *"the marker is the thing that
  moves"*; `Theming.md` → What a Theme Controls → Animation repeats this. But the same doc's
  Where Animations Fire raises animating the **active-quadrant highlight** (a whole
  quadrant, not a marker), and `neon.theme.json → animation` carries `activeQuadrant` and
  `claimQuadrant` entries. Requirements 2 and 25 record both sides without picking one.
  Someone has to say whether "marker only" is a hard boundary this version holds, or a
  starting scope the quadrant-level entries already exceed.
- **"One animation at a time, never overlapping" vs. looping glow-pulses.**
  `Animations.md` → Decisions → One animation at a time is unambiguous. The handoff's
  starting values give `activeQuadrant` and `lastMove` `"loop": true` — animations that by
  construction run continuously, and so would be running whenever a `placeMark` pop fires.
  These cannot both be true as literally stated. The handoff values are declared "not
  decisions," so the Decision wins by default; but if the looping highlight pulses are
  wanted, the one-at-a-time rule needs restating (e.g. as "one *transient* animation at a
  time"). This blocks implementation of Requirement 14 the moment a looping highlight is
  authored.
- **A sibling PRD has already assumed an answer.** `P3-01-board-rendering.md` → Out of Scope
  defers *"the looping glow-pulse on the active quadrant and the last move"* to this PRD as
  **committed work**. That asserts an answer to both questions above — that the highlights
  are animated, and that they loop — which neither this PRD nor the design docs have. Flagged
  here rather than fixed: either that deferral should be reworded as conditional, or the
  scope question should be settled and both PRDs updated. `P3-01` is not mine to edit.

### Raised by this PRD, not by the design docs (proposals, clearly mine)

The docs are silent on all of these. Each is a decision an implementer would otherwise make
by accident.

- **Is a theme-derived `Duration` a theme-guard violation?** Requirement 13 puts timing in
  the theme, and this layer must therefore build
  `Duration(milliseconds: <theme value>)` at playback — in `lib/ui/` or a dedicated
  animation package, **not** in `lib/theme/`. `P1-05-theme-guard-test.md` req 5 makes a
  hardcoded `Duration` a violation and its req 3 exempts only `lib/theme/` by path. Neither
  PRD says whether a `Duration` constructed *from* a theme value outside that path passes,
  and `P1-05` ships in wave 1 with an empty baseline and no knowledge of this consumer. If
  the scan is literal-argument-based this is a non-issue; if it is constructor-based, this
  layer fails the guard on day one. Needs deciding before `P1-05` is built.
- **What is an animation slot's value shape, and what happens to an unknown type?**
  Requirement 9 forbids "a closed list a theme selects an index into," but the slot's value
  shape is `P1-03-theme-system.md` req 18's, and that requirement fixes only the duration —
  and `P1-03` ships first. So the answer to Requirement 9 must exist before `P1-03` is
  built, not before this PRD is. Related and equally unstated: what happens when a theme
  names a type the runtime does not implement (`"type": "backflip"`) — fall back to Neon's
  entry, play nothing, or fail to load the theme? `P1-03`'s own open question about
  misspelled keys is adjacent but not the same: a misspelled *key* is filled silently by
  the merge, while an unknown *type* survives the merge intact.
- **What happens when a second animation is triggered while one is playing?** Requirements
  14, 15 and 16 pin three things — one at a time, input is never blocked, and a running
  animation is never interrupted or skipped — and together they leave a gap: a player can
  tap through a playing animation, producing a second trigger, and the docs do not say
  whether that second animation queues behind the first, is dropped, or replaces it.
  "Never overlap" rules out playing both; "never interrupted" rules out cutting the first
  short. Queue and drop are both consistent with the letter of the docs and feel very
  different in the hand.
- **Co-occurring moments are a different question from the tap-through case.** A single
  confirmed move can be `placeMark` **and** `claimQuadrant` **and** `winGame` at the same
  instant — no second tap is involved, and nothing the player did caused the pile-up. The
  answer may reasonably differ from the tap-through answer: sequencing three animations into
  a little cascade is a plausible design here and a bad one there. `P2-02-audio.md` raises
  the identical case for sound and likewise leaves it open; the two channels may or may not
  want the same answer.
- **What happens if animations are switched off while one is playing?** Requirement 16 says
  a running animation is never interrupted or skipped; Requirements 19 and 20 say that with
  the toggle off, nothing runs. Both readings — let the in-flight animation finish, or cut
  it immediately — satisfy the wording. Reachable in practice, since settings are available
  mid-game via the in-game sheet (`Menus and UI.md` → How you reach settings from gameplay).
- **Does an animation have to finish before the state it depicts is committed?**
  Requirement 15 says the game does not wait on the animation, which implies state commits
  immediately and the animation plays over the already-changed state. Worth confirming,
  because the opposite reading (animate, then commit) would break Requirement 15 and is a
  natural thing to build by accident.
- **Is there a "currently animating" state anywhere in persisted game state?** The handoff's
  *State* section does not include one, and Requirement 22 says animation is presentation
  only — so backgrounding the app mid-animation should simply lose it. Not stated anywhere;
  stating it would close off a class of save-file bug.
