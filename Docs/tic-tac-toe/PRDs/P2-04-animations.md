**Build-readiness: 86**

# PRD: Animation System

> **Status:** Draft · Source docs read: `Animations.md` (primary — including Decisions →
> *Themes describe their animations; the runtime interprets them*), `Theming.md`,
> `Game Board Design.md`, `Tech Design.md`, `Menus and UI.md`, `Game Overview.md`, `Rules.md`,
> `roadmap.md`, plus the read-only reference asset `design_handoff_game_ui/` (`README.md` →
> *2b — Settings page*, *Interactions & behavior*, *State*; `neon.theme.json` → `animation`).
> `Alternative Game Styles.md` is a declared parking-lot doc and was read only to confirm it is
> out of scope — no requirement here comes from it.
>
> **Revised three times.** First for build-readiness: the interface (Requirements 5–7), the
> wave fence (27–29), the dispatch path (30–33), the test seam (34–36), the stated defaults
> (37–41). Then for `Animations.md`'s new Decision, which replaced "implement one type string"
> with "build an interpreter." **Now revised again after `P1-03-theme-system.md` published the
> motion schema** — Requirement 31's blocker is gone, and Requirements 30–32 are written
> against the shipped shape rather than against a statement of need.
>
> **Requirement numbering 1–40 is stable across all three revisions**; Requirement 31 was
> replaced in place and 41 appended. **Two inbound citations are stale and need fixing in files
> this PRD cannot edit:** `P3-02-move-input.md` req 18 cites "`P2-04` requirements 12–13" for
> *never blocks input* / *never interrupted* — those are **Requirements 15–16** here;
> `P3-04-game-over-rematch.md` req 14 cites "`P2-04` reqs 16–18" for the animations-off path —
> those are **Requirements 19–21** here. The behaviors are unchanged; only the numbers are
> wrong.
>
> **Why 86, up from 70.** The reason for 70 was that Requirement 31 asked for an interpreter
> against a format that did not exist. `P1-03-theme-system.md` req 15 and req 18 now publish
> it — duration, repeat, tracks, keyframes, per-track easing, a closed property set — matching
> this PRD's stated need point for point and going further on two axes. The interpreter is
> buildable and every test in Requirement 36 is writable today against fixture themes.
>
> **Why not higher.** Two things, neither fixable by editing this PRD. **(a) Neon's motion
> magnitudes are unauthored.** `P1-03` req 13 puts `animation.<moment>.tracks[].keyframes[].value`
> in its residue table as `deferred` — the durations and easings transcribe from the handoff,
> the numbers they interpolate between are drawn nowhere. So Requirement 23's *visible*
> outcome, a mark that actually pops under Neon, cannot be demonstrated end to end until
> someone authors them. An agent is **not** left guessing — `P1-03` names the gap, marks it
> deferred and instructs agents not to fill deferred keys — but the acceptance floor of this
> PRD depends on it. **(b) Two questions remain with the user** (marker-only vs quadrant-level
> scope; whether the highlights animate and loop). Requirement 27 fences both out of wave 2, so
> they do not block the build, but they are unanswered.

**Wave:** P2 · **File:** `P2-04-animations.md` — parallel-safe with the other P2 PRDs.

**Start here:** Requirements 5–7 (the published interface), 30–32 (the schema this executes and
how), then 27–29 (what this wave plays).

**Dependencies:**

- `P1-03-theme-system.md` — **satisfied.** It owns the `animation` schema (its reqs 15 and 18),
  the deep-merge rule including *a list is a leaf* (its req 8), Neon's authored content (its
  req 13), schema versioning — now **version 3** (its req 37), and the Riverpod exposure of the
  active theme (its req 24). Its req 18 hands the interpreter to this PRD by name: *"what
  executes a track, how tracks compose, one-at-a-time sequencing, non-blocking input, the
  animations-off path."* **Residual:** the keyframe magnitudes are `deferred` there — see the
  authoring gap under *Contradictions and gaps*.
- `P1-01-app-scaffold.md` — the Riverpod root this layer's provider hangs off, and the `lib/`
  tree it lands in. **It does not yet create `lib/animation/`** — the same gap
  `P2-01-navigation.md` records for `lib/navigation/` in its Open Question 16.
- `P1-04-persistence.md` — stores the animations toggle's value across sessions. This PRD reads
  it.
- `P1-05-theme-guard-test.md` — its req 5 makes a hardcoded `Duration` a violation and its
  req 3 exempts only `lib/theme/`. **Resolved** — see Requirement 33. Note `P1-03` req 25 now
  extends the rule explicitly to motion: *"an interpolation magnitude living in Dart is a theme
  value that escaped."*

> **The toggle is a persisted preference, not a settings-screen behavior.** This PRD reads the
> stored value through `P1-04-persistence.md`. `P4-04-settings.md` draws the switch and owns no
> part of what "off" means — so it is a wave-4 consumer of this feature, not a dependency of it.

**Depended on by:**

- `P3-01-board-rendering.md` — owns the marks and cell widgets this layer wraps. Its req 31 is
  the board-side half of Requirement 21. **Flagged for routing:** its Out of Scope defers *"the
  looping glow-pulse on the active quadrant and the last move"* to this PRD as **committed
  work**, which asserts answers to two questions still with the user.
- `P3-02-move-input.md` — its req 18 is the caller-side half of Requirements 15–16, and it owns
  the confirm tap that changes the `placeMark` trigger (Requirement 6).
- `P3-04-game-over-rematch.md` — its req 14 is the caller-side half of Requirements 19–21.
- `P4-04-settings.md` — draws the Animations toggle whose behavior is Requirements 17–20.

**Note on source status:** `Animations.md` carries the house banner *"Nothing here is settled
except what's under **Decisions**"* and carries nine settled entries. This PRD sources its
requirements from those Decisions and from the narrative sections they point at, and leaves
anything the doc explicitly hedges in **Open Questions**. Where this PRD decides something the
docs leave unstated it says so inline as **[PRD decision]**, following
`P1-05-theme-guard-test.md`'s convention.

> **On the acceptance floor.** **Requirement 23 commits `placeMark` unconditionally.**
> `Animations.md` → Where Animations Fire hedges *which moments make the full list*, not
> *whether anything animates*: it calls placing a marker *"the primary one"*, and placing a
> marker is the only listed moment that falls squarely inside the settled marker-only scope of
> → Scope For Now. The other moments are quadrant- or board-level and are entangled with the
> unresolved scope question, so Requirement 27 fences them out of this wave rather than leaving
> them ambiguous.

---

## Problem

The board can be fully correct and completely lifeless. `Animations.md` → The Direction states
the game is aimed partly at kids and needs to feel alive — *"snappy and playful, not slow and
cinematic"* — and today nothing moves: a mark placed on an 81-cell grid simply appears, with no
moment of feedback that something happened.

The second part is structural, and the wave move makes it urgent. This PRD ships **before** its
consumers. `P1-03-theme-system.md` now defines what a theme says about motion, but nothing
executes it, and no design doc names an animation layer or says how a caller asks for a moment.
`P3-02-move-input.md` req 18 and `P3-04-game-over-rematch.md` req 14 are already written against
that interface. If it is not published here, each wave-3 consumer invents its own — and motion
timing typed directly into a widget is exactly the escape from the Architectural Rule that
`P1-03` req 25 now names for motion specifically.

The third part is what the Decision named and the schema answered. The obvious way to make a
mark pop is to recognise the string `"grow-shrink"` and build the matching tween — and that is
the way that quietly kills the feature. Every new theme with a new idea for motion then needs a
new string and a new branch in game code, which is the opposite of *"I want to drop a file in
the new theme folder that can tell the application what animations are."* Whatever this layer
does first sets that direction, because unpicking it means touching every animation the app has
by then.

## Goal

The player's marker pops when it lands, and it pops because the active theme *described* the
pop — not because the runtime knows what "pop" means. One animation layer at a published address
owns all of it: a caller wraps the widget that should move and names a moment, and never touches
a controller, a duration or a curve. The layer reads a motion description from the theme —
tracks over properties, keyframes, per-track easing, repeat — and executes it, so a theme
composing motion nobody anticipated still animates with no code change. Exactly one animation
runs at a time, none blocks input, and the whole layer switches off into instant state changes
with no substitute effect. This wave plays one moment, `placeMark`, so the questions the docs
leave open about the other five are not answered by accident.

## Requirements

### Direction and scope

1. **Animations are poppy** — snappy and playful rather than slow and cinematic. The
   implementation targets that feel; timing values that read as cinematic are wrong for this
   game.
   *Source:* [Animations](../Animations.md) → The Direction.
   *Testable:* not mechanically testable as a feel, but not vacuous — the overshoot in Neon's
   transcribed `cubic-bezier(.34,1.56,.64,1)` (a second control point above 1.0, so the mark
   overshoots and settles back) **is** the poppiness, and Requirement 32 requires it be
   reproduced rather than flattened to an ease-out.
2. **Only the player's marker is animated in this version** — whatever the active theme says
   that marker is (an X, an O, a checkbox, an icon, an image). "The marker is the thing that
   moves."
   *Source:* [Animations](../Animations.md) → Scope For Now; corroborated by
   [Theming](../Theming.md) → What a Theme Controls → Animation and
   [Game Board Design](../Game%20Board%20Design.md) → Animation & Juice.
   *Testable:* the only widget wrapped by `ThemedAnimation` (Requirement 6) in wave 2 is the
   mark widget inside a cell. **Subject to the marker-only-vs-quadrant question** under
   *Blocking* — if quadrant-level moments are confirmed, this requirement changes.
3. **The board, the layout, and transitions between screens are not animated.**
   *Source:* [Animations](../Animations.md) → Scope For Now.
   *Testable, scoped to this layer:* `AnimationMoment` (Requirement 7) exposes no board, layout
   or screen-transition moment, so no caller can request one through this layer. **This PRD does
   not constrain `P2-01-navigation.md`'s territory** — that PRD holds the screen-transition half
   from its own side (its Out of Scope → *Screen transition animations*, its req 15, and its
   Open Question 14).
4. **The animation vocabulary is the direction, and the schema now reaches all of it.**
   `Animations.md` → The Animation Vocabulary names five building blocks; each maps onto
   properties in `P1-03` req 18's closed set:

   | Vocabulary item | Property it needs | In the closed set? |
   |---|---|---|
   | Grow & shrink | `scale` | yes |
   | Glow / backlight | `glowRadius`, `glowColor` | yes |
   | Shadowbox | `glowRadius` / `glowColor` as a cast shadow | yes, if a drop shadow is expressible as a glow; see *Gaps* |
   | Jiggle | `rotation`, `translateX`/`translateY`, repeating | yes |
   | Dance | `translateX`, `translateY` | yes |

   *Source:* [Animations](../Animations.md) → The Animation Vocabulary; all five are also listed
   in → The Direction, in → Decisions → Themes author their own animations, and in
   [Theming](../Theming.md) → What a Theme Controls → Animation. Property names from
   `P1-03-theme-system.md` req 18.
   *Testable:* four of the five are expressible as track compositions over the published
   property set and need no code beyond Requirement 31. **No theme authors jiggle, dance or
   shadowbox today** — Neon's six moments use only `scale`, `opacity` and `glowRadius` — so this
   is a check on the interpreter's generality, testable with a fixture theme (Requirement 36),
   not on shipped content.

### The animation layer — the published interface

> **[PRD decision] — derived, not stated.** No design doc names an animation layer or an API.
> This section is the shape the cited rules force, and it is published because this PRD ships
> before its consumers. The **identifiers** are a proposal and renaming any of them is free; the
> **structure** is what Requirements 8, 14, 15 and 19 need in order to hold. Same remit
> `P1-03-theme-system.md` used for its req 35 encoding decision and `P1-05-theme-guard-test.md`
> for its req 1 file layout — and `P1-03` req 18 assigns the interpreter here by name.

5. **The layer lives in `lib/animation/`, and all playback goes through it.** Board, menu and
   game-over code names a moment; it never constructs an `AnimationController`, a `Duration`, a
   `Curve` or a tween, and never reads an `animation.*` key off the theme.

   **Files:**
   - `lib/animation/animation_moment.dart` — the `AnimationMoment` enum (Requirement 7).
   - `lib/animation/themed_animation.dart` — the `ThemedAnimation` widget (Requirement 6).
   - `lib/animation/animation_coordinator.dart` — the coordinator and its provider
     (Requirement 7).
   - `lib/animation/resolved_animation.dart` — the resolved value objects (Requirement 30).
   - `lib/animation/interpreter.dart` — the motion interpreter (Requirement 31).

   **[PRD decision] on the location.** A top-level `lib/animation/` follows `Tech Design.md` →
   Decisions → Project structure — layer-first (*"group by kind, not by feature"*) and matches
   the precedent `P2-01-navigation.md` set with `lib/navigation/` for a cross-cutting wave-2
   layer consumed by board, menus and game-over alike. It is deliberately **not** `lib/theme/`:
   that path is exempt from the guard scan (`P1-05` req 3) and this layer must not be.
   *Testable:* no `AnimationController`, `Duration`, `Curve`, tween or `animation.*` theme read
   appears anywhere under `lib/ui/`; a call site's entire animation surface is wrapping a widget
   and naming a moment.

6. **The caller-facing surface is a widget wrapper, and there is no target parameter.**

   ```dart
   // lib/animation/themed_animation.dart
   class ThemedAnimation extends ConsumerStatefulWidget {
     const ThemedAnimation({
       super.key,
       required this.moment,
       required this.trigger,
       required this.child,
     });

     final AnimationMoment moment;
     final Object? trigger;
     final Widget child;
   }
   ```

   **This resolves a tension an earlier draft left open** — that a call was "fire-and-forget,
   naming a moment and nothing else" while Requirement 23 required the animation to play against
   one specific mark among 81. A parameterless moment name cannot address one cell; an
   imperative `play(moment, target: cellIndex)` can, but only by holding a registry of cells or
   an overlay stack, both of which must track widget geometry the board already knows. **The
   wrapper resolves it by position: the animated thing is the wrapper's own `child`, so no
   target is ever passed.**

   - **Trigger semantics.** The animation plays when `trigger` changes value between builds
     (`didUpdateWidget`, `trigger != oldWidget.trigger`). It does **not** play on first build —
     otherwise every mark on a restored board would animate on mount. For `placeMark` the
     natural trigger is the cell's occupant, which is null until the move commits; the caller
     chooses it, and it must change exactly when the moment occurs.
   - **Fire-and-forget holds.** The widget returns nothing, exposes no callback and no future. A
     caller cannot learn whether an animation played, was dropped, or was skipped because the
     toggle is off — which is what makes Requirements 15, 19 and 20 hold at every call site
     rather than at the disciplined ones.
   - **Callers.** `P3-01-board-rendering.md` wraps the mark widget; `P3-02-move-input.md` owns
     the confirm tap that changes the trigger. Neither is specified here.

   *Derived from:* [Animations](../Animations.md) → Decisions → Animations don't block input
   (*"the game doesn't wait on it"*), → Animations off = instant state change (*"Don't worry
   about animations at all in this mode"*), and [Theming](../Theming.md) → Architectural Rule.
   *Testable:* a widget test rebuilding `ThemedAnimation` with an unchanged `trigger` records no
   animation; changing it records exactly one; the first build records none.

7. **The moment identifier is an enum, and the coordinator is a Riverpod `Notifier`.**

   ```dart
   // lib/animation/animation_moment.dart
   enum AnimationMoment { placeMark, claimQuadrant, catGame, winGame, activeQuadrant, lastMove }

   // lib/animation/animation_coordinator.dart
   final animationCoordinatorProvider =
       NotifierProvider<AnimationCoordinator, AnimationMoment?>(AnimationCoordinator.new);

   class AnimationCoordinator extends Notifier<AnimationMoment?> {
     /// Null means "do not play" — toggle off, moment not played this wave,
     /// or another animation holds the slot.
     ResolvedAnimation? begin(AnimationMoment moment);
     void end(AnimationMoment moment);
   }
   ```

   - **An enum, not a `String`.** A string moment name is a typo the compiler cannot catch and
     `P1-05-theme-guard-test.md` does not scan for — it would resolve to a missing theme key and
     silently play nothing. The six values map 1:1 onto `P1-03` req 15's `animation.<moment>`
     keys and are named identically.
   - **The enum being closed is not a violation of Requirement 9.** The *moment* list is fixed by
     the schema — `P1-03` req 15 names exactly six and marks all six required, and growing it is
     a `meta.schemaVersion` bump under its req 37. Requirement 9 is about **what a theme
     describes at each moment**, a different axis.
   - **The provider's state is the moment currently playing, or null when idle**, which makes
     Requirement 14 directly observable rather than an internal invariant.
   - **`begin` returning null is invisible to callers** — only `ThemedAnimation` calls it.

   *Source for the Riverpod half:* [Tech Design](../Tech%20Design.md) → Decisions → State
   management — Riverpod, which explicitly covers *"the requirement that settings and the theme
   be readable from everywhere, including deep in the board widget tree"*; `P1-03` req 24. Plain
   `Notifier`/`NotifierProvider`, no `@riverpod` codegen.
   *Testable:* overriding the theme provider changes which animation plays for the same moment
   with no change at the call site; reading `animationCoordinatorProvider` reports the playing
   moment and null when idle.

### Animations belong to the theme

8. **Every animation played comes from the active theme.** No motion originates in game, board
   or menu code: *"If something moves, that motion came from the theme. No exceptions."*
   *Source:* [Theming](../Theming.md) → Architectural Rule; [Animations](../Animations.md) →
   Animation Sets Are Part of the Theme; `P1-03` req 25, which extends the rule to interpolation
   magnitudes specifically.
   *Testable:* with a theme whose `animation` section is replaced wholesale, every animation the
   app plays changes, and no file outside `lib/theme/` and `lib/animation/` is touched.
9. **There is no shared animation library and no menu of animations for a theme to pick from.**
   A theme authors its own animations; the vocabulary in Requirement 4 is *direction*, not a
   fixed option set the runtime enumerates.
   *Source:* [Animations](../Animations.md) → Decisions → Themes author their own animations —
   no shared library, strengthened by → Decisions → **Themes describe their animations; the
   runtime interprets them**: *"A theme describes its animations as data, and the runtime
   interprets that data,"* and *"adding an animation must not require changing game code."*

   **Settled, and the line is drawn at behaviours rather than properties.** `P1-03` req 18 ships
   a **closed property set** (`scale`, `opacity`, `glowRadius`, `glowColor`, `translateX`,
   `translateY`, `rotation`) and an **open space of motion composed from it**, stating the bar
   directly: *"new motion composed from these properties needs no code — that is the bar, and it
   is met. A property not on this list needs a runtime change and a version bump."* That is the
   shipped design, not a reading this PRD is defending: a runtime that can interpolate seven
   properties in any combination is bounded; a runtime that can play `"grow-shrink"` and nothing
   else is closed in the way the Decision rules out. Requirement 31 discharges it.
   *Testable:* a theme file composing motion no existing theme uses — different properties,
   different magnitudes, different keyframe counts, different repeat — plays correctly with
   **zero changes to any file under `lib/`**. That single assertion is the Decision in executable
   form.
10. **A theme's animations merge over Neon's, and a list is a leaf.** Animations merge by the
    same rule as every other theme value, resolved once at materialization rather than per
    lookup, so this layer performs **no fallback at play time**. But `P1-03` req 8 settles the
    list case, and it matters here more than anywhere else in the schema: **a theme naming a list
    replaces it whole.** Both `tracks` and `keyframes` are lists.

    **The authoring consequence, stated because it will surprise someone:** a theme that wants to
    change only the glow of Neon's two-track `claimQuadrant` (a `scale` track and a `glowRadius`
    track) **must restate both tracks**. There is no element-wise merge and no way to override
    one track in place — `P1-03` req 8's reasoning is that there is no stable identity for "the
    second keyframe," so element-wise merging would make a two-frame override collide with a
    three-frame original. Same for keyframes within a track.
    *Source:* [Animations](../Animations.md) → Decisions → Do themes inherit Neon's animations?;
    [Tech Design](../Tech%20Design.md) → Decisions → Fallback to Neon — merge, not resolve;
    `P1-03` req 8.
    *Testable:* this layer contains no fallback, default or null-coalescing branch on an
    `animation.*` key, and never merges tracks or keyframes itself — it receives whatever the
    materialized theme holds. A theme defining a one-track `animation.placeMark.tracks` yields
    exactly that one track (`P1-03` req 8's own testable, asserted from the consumer side).
11. **Neon's animation set is complete** — every moment the game animates has a Neon definition,
    because Neon is the fallback for every other theme.
    *Source:* [Animations](../Animations.md) → Animations Inherit From Neon;
    [Theming](../Theming.md) → Neon Is the Base Theme.
    *Owner of the behavior:* `P1-03` reqs 11, 13 and 18 — all six moments are required and
    re-expressed in the track shape. **This PRD authors no theme content and must not edit
    `assets/themes/`.** Restated only because Requirement 10 is true only if it holds — the same
    fencing `P2-02-audio.md` req 12 uses. See *Gaps* on the unauthored magnitudes.
12. A different theme brings a **different animation personality** — the animation set travels
    with the theme, so selecting a different theme changes how things move without any code
    change.
    *Source:* [Animations](../Animations.md) → Animation Sets Are Part of the Theme;
    [Theming](../Theming.md) → What Is a Theme?
    *Testable:* covered by Requirements 8, 9 and 10; adding a theme adds a theme file and changes
    no code.

### Playback rules

13. **Duration lives in the animation, not globally.** Each moment's description carries its own
    `animation.<moment>.duration`, so a theme controls its own pacing. There is no global
    animation-speed or duration-multiplier value anywhere.
    *Source:* [Animations](../Animations.md) → Decisions → Duration lives in the animation;
    `P1-03` req 15.
    *Testable:* editing `animation.placeMark.duration` in a theme file changes that animation's
    runtime duration and no other's; no global speed constant or multiplier exists. The guard
    interaction is settled — see Requirement 33.
14. **One animation at a time — animations never overlap.** At no point are two animations
    running simultaneously. Enforced centrally by `AnimationCoordinator` (Requirement 7), not by
    caller discipline.
    *Source:* [Animations](../Animations.md) → Decisions → One animation at a time.

    **"One animation" means one moment's description, not one track.** A moment's description may
    carry several tracks — Neon's `claimQuadrant` is `scale` + `glowRadius`, its `catGame` is
    `scale` + `opacity` (`P1-03` req 18) — and **all tracks of one animation run together**. That
    is one animation with concurrent property tracks, not two overlapping animations. Stated
    explicitly because the alternative reading would make every multi-track theme animation
    illegal under a Decision that was written about moments.
    *Testable:* with the widget clock the test controls (Requirement 35), requesting a second
    *moment* while one is in flight never produces two concurrent animations, and
    `animationCoordinatorProvider` never reports more than one playing moment; a two-track
    animation drives both properties within a single `begin`/`end` pair. What happens to the
    second request is Requirement 38's stated default.
15. **Animations never block input.** While an animation is playing, taps are accepted and
    processed exactly as they would be with no animation running, and the game does not wait on
    the animation before changing state.
    *Source:* [Animations](../Animations.md) → Decisions → Animations don't block input.
    *(One of the two behaviors `P3-02-move-input.md` req 18 cites as "requirements 12–13"; that
    citation is stale and the behavior is unchanged.)*
    *Testable:* a tap dispatched mid-animation produces the same state change, in the same number
    of frames, as the same tap dispatched at rest. `ThemedAnimation` adds no `IgnorePointer`, no
    `AbsorbPointer` and no gesture-blocking overlay above its child.
16. **A tapped-through animation is neither interrupted nor skipped** — it keeps playing as
    normal to its full duration.
    *Source:* [Animations](../Animations.md) → Decisions → Animations don't block input.
    *Testable:* an animation whose duration is *d* still completes at *d* when a tap lands
    partway through, and is not cut short, restarted or fast-forwarded.

### The off switch

17. **There is a global animations on/off toggle**, and it is **not theme-defined**: it is a
    player setting alongside the sound-effects and vibrate toggles in the Settings menu. No theme
    file key can set, override or read it, and switching themes does not change its value.
    *Source:* [Animations](../Animations.md) → Decisions → Turn animations off — a global
    setting; [Menus and UI](../Menus%20and%20UI.md) → Settings Menu; [Theming](../Theming.md) →
    What a Theme Does NOT Control; `P1-03` req 30.
    *Ownership:* the stored value is `P1-04-persistence.md`'s and the switch that sets it is
    `P4-04-settings.md`'s. **What "off" means — Requirements 19 and 20 — is this PRD's.**
    *Testable:* no theme file contains an animations-enabled key; switching the active theme
    leaves the toggle's value unchanged; `AnimationCoordinator` has no default of its own and no
    writer.
18. **iOS Reduce Motion does not drive the toggle.** With Reduce Motion enabled and the game's
    Animations toggle on, animations still play. There is exactly one control and the player owns
    it: *"no lets leave this as a game setting for user to command."*
    *Source:* [Animations](../Animations.md) → Decisions → Does iOS Reduce Motion drive the
    animations toggle?
    *Testable:* with the platform accessibility flag forced on and the game toggle on, a
    `placeMark` trigger change still plays; no file reads `MediaQuery.disableAnimations` or the
    equivalent platform flag.
19. **Animations off = instant state change.** With the toggle off, the mark simply appears and
    the quadrant is simply claimed. No animation runs, and **no substitute effect, fade or
    transition stands in for one**.
    *Source:* [Animations](../Animations.md) → Decisions → Animations off = instant state change.
    *Testable:* with the toggle off, `begin` returns null, the new state is fully rendered in the
    frame the state changed, and no tween, opacity ramp, scale or cross-fade is scheduled by any
    code path.
20. With the toggle off, the game state changes and the screen shows the new state — and nothing
    else in the game behaves differently. The off path is not a second, shorter animation path;
    it is the absence of one.
    *Source:* [Animations](../Animations.md) → Decisions → Animations off = instant state change
    (*"Don't worry about animations at all in this mode"*).
    *Testable:* the full move sequence produces identical state, identical timing and identical
    caller behavior with the toggle off as it would with `lib/animation/` absent entirely.

### Animations are a pure layer on top

21. **The game is fully playable and fully readable with every animation stripped out.** Nothing
    an animation communicates may be communicated *only* by that animation — every board state
    the player needs (last move, active quadrant, locked quadrants, pending preview, claimed, cat
    game, whose turn) remains legible with animations off.
    *Source:* [Animations](../Animations.md) → Decisions → Animations off = instant state change
    → *"Practical consequence: animations are a pure layer on top."* Restated as a test in
    [Design Handoff](../design_handoff_game_ui/README.md) → Interactions & behavior: *"Every
    screen above is fully readable with animation off — that is the correctness test."*
    *Verified elsewhere:* this enumerates board and screen states that **do not exist until wave
    3**, so it is not assertable here. It is verified by `P3-01-board-rendering.md` req 31,
    `P3-04-game-over-rematch.md` req 14, and `P3-05-how-to-play.md`. This PRD's obligation is to
    add nothing that would break it — which Requirements 19 and 20 make testable here.
22. Removing the animation layer entirely must not change any game outcome, any legality
    decision, or any persisted state. Animation is presentation only; it is not part of the rules
    engine, which is pure Dart with zero Flutter imports.
    *Source:* Requirement 21, plus [Tech Design](../Tech%20Design.md) → Decisions → Is the game
    logic separate from Flutter?
    *Testable:* `lib/engine/` imports nothing from `lib/animation/` and its suite passes with the
    layer absent; no persisted field describes animation state (Requirement 39).

### Where animations fire

23. **Placing a marker is animated.** On a confirmed move, the newly placed marker plays the
    active theme's `animation.placeMark` — *"the mark appears with a pop."* This is not
    conditional: an implementation in which nothing animates does not satisfy this PRD.
    *Source:* [Animations](../Animations.md) → Where Animations Fire (*"**Placing a marker** —
    the primary one. The mark appears with a pop"*), read together with → Scope For Now.
    *Testable:* with animations on, confirming a legal move records exactly one `placeMark`
    animation against the newly placed mark, running for `animation.placeMark.duration` and
    driving the properties its tracks name. With the toggle off, it records none and the mark is
    on screen in the frame the move committed. It fires on the **confirming** tap only — the
    pending selection animates nothing, matching `P2-02-audio.md` req 8's rule for sound.
    **Assertable today against a fixture theme; the visible Neon result waits on the magnitudes**
    — see *Gaps*.
24. **Every moment the game animates plays from the active theme's description for that moment,
    and has a Neon definition** (Requirement 11).
    *Source:* [Animations](../Animations.md) → Where Animations Fire; Animations Inherit From
    Neon; [Theming](../Theming.md) → Architectural Rule.
    **Corrected claim.** An earlier draft said adding or removing an animated moment is "a
    theme-data change, not a code change." False as stated: under `P1-03` req 37 a new
    `animation.<moment>` key is a schema version bump, and it also needs an `AnimationMoment`
    value and a `ThemedAnimation` wrapper. What is true: **changing how an existing moment
    animates is theme data alone** — including changing it to motion the runtime has never
    executed before, provided it composes from the published property set (Requirement 9).
    *Testable:* editing `animation.placeMark` in a theme file changes the animation with no source
    file modified.

> The remainder of the list is where `Animations.md` → Where Animations Fire applies its hedge —
> **"Not yet decided in detail, but the obvious moments"**. Requirements 25 and 26 record the
> candidates without committing them; they are not acceptance criteria.

25. The further moments the doc lists as obvious candidates are: **winning a small board /
    claiming a quadrant**, **cat game**, and **winning the whole game**. The doc also notes the
    **last-move highlight and active-quadrant highlight** *"could be animated rather than static,
    e.g. a pulsing glow on the legal quadrant"* — recorded as the doc's hedge, not as a
    commitment that they are animated.
    *Source:* [Animations](../Animations.md) → Where Animations Fire;
    [Game Board Design](../Game%20Board%20Design.md) → Last Move Highlight, Active Quadrant
    Highlight.
26. **The handoff's `type`/`durationMs` entries are superseded, not carried.** `Animations.md` →
    Where Animations Fire calls `neon.theme.json → animation` *"starting values … not
    decisions"*, and → Decisions → Themes describe their animations adds that the `type` shape
    *"does not yet reach this bar."* `P1-03` req 18 has re-expressed all six moments as
    tracks — *"a change of representation, not of motion"* — and its req 12 records `animation`
    as **the first deliberate drift** between `neon.yaml` and the reference JSON, with the YAML
    authoritative. **This layer reads `neon.yaml`, never the JSON**, and no requirement here
    fixes any magnitude or duration.

---

### What this wave plays — the fence

27. **[PRD decision] Wave 2 plays exactly one moment: `placeMark`.** The other five
    `AnimationMoment` values exist in the enum and in Neon's theme data, and
    `AnimationCoordinator.begin` returns null for them. No `ThemedAnimation` wrapping a quadrant,
    a highlight or a game-over surface is built in this wave.

    **This fence is about which *moments* play, not about what motion the interpreter can
    execute.** Independent axes, and conflating them would re-introduce exactly the closed list
    Requirement 9 forbids. The interpreter must handle any description the schema can express —
    every property, any track count, any repeat — whether or not this wave asks it to. It is
    simply only *invoked* for one moment.

    **What the fence buys.** Three open questions are only reachable through the unplayed five:
    the loop-vs-one-at-a-time contradiction (`activeQuadrant`, `lastMove`), co-occurrence
    (`placeMark` + `claimQuadrant` + `winGame` in one move), and the marker-only-vs-quadrant
    scope question. Fencing them out makes wave 2 buildable **without answering any of them**. It
    is a build boundary, not a ruling.
    *Testable:* `begin` returns null for all five non-`placeMark` moments; no widget test anywhere
    records an animation for them.
28. **The unplayed five are unblocked by decision, not by work.** When the scope questions are
    answered, playing a further moment is: wrap the right widget in `ThemedAnimation`, and — for
    `activeQuadrant` and `lastMove` only — resolve the looping contradiction (Requirement 29). No
    interface change and no interpreter change is required, which is why this fence is cheap to
    lift.
29. **Looping is determinate, not hypothetical.** `P1-03` req 18's re-expression table ships
    `activeQuadrant` and `lastMove` as a `glowRadius` track with
    `repeat: {count: infinite, mode: reverse}`. An infinitely repeating animation runs
    continuously and so overlaps everything, which `Animations.md` → Decisions → One animation at
    a time forbids in as many words. The schema change did not dissolve this — it made it
    explicit, since `repeat.count: infinite` is now a first-class value rather than a `loop`
    flag.

    This wave does not hit it, because Requirement 27 plays neither moment. **It must be answered
    before either is played**, and the answer is a ruling, not an implementation detail: either
    the highlights do not repeat infinitely, or "one animation at a time" is restated to mean one
    *transient* animation at a time with ambient repeating effects excluded. See *Blocking*,
    item 2.

### What the interpreter executes

30. **The published schema this layer compiles against.** Owned by `P1-03-theme-system.md`
    reqs 15 and 18, which are authoritative if this restatement ever differs. Restated inline so
    a coding agent can build without opening another PRD:

    ```yaml
    animation.<moment>:
      duration: <ms>
      repeat:
        count: <integer | infinite>     # 1 = once
        mode:  <restart | reverse>
      tracks:                            # list, >= 1
        - property: <scale | opacity | glowRadius | glowColor | translateX | translateY | rotation>
          easing:   <cubic-bezier(...) | named curve>
          delay:    <ms>                 # optional, default 0
          keyframes:                     # list, >= 2
            - at:     <0.0 .. 1.0>       # fraction of duration
              value:  <number | color>
              easing: <easing string>    # optional; overrides the track's for the segment ending here
    ```

    `<moment>` ∈ the six `AnimationMoment` values. **The property set is closed** (`P1-03`
    req 18); a property outside it needs a runtime change *and* a schema version bump, and is not
    something a theme can introduce. Schema version is **3**.

    The layer's resolved value objects, whose shape follows the schema:

    ```dart
    // lib/animation/resolved_animation.dart
    class ResolvedAnimation {
      const ResolvedAnimation({required this.duration, required this.repeat, required this.tracks});
      final Duration duration;
      final ResolvedRepeat repeat;
      final List<ResolvedTrack> tracks;
    }

    class ResolvedTrack {
      const ResolvedTrack({required this.property, required this.easing,
                           required this.delay, required this.keyframes});
      final AnimatedProperty property;   // the closed set, as an enum
      final Curve easing;
      final Duration delay;
      final List<ResolvedKeyframe> keyframes;
    }

    class ResolvedKeyframe {
      const ResolvedKeyframe({required this.at, required this.value, this.easing});
      final double at;                   // 0.0 .. 1.0
      final Object value;                // double, or Color for glowColor
      final Curve? easing;
    }
    ```

    **This PRD does not define, extend or version the schema.** It states how the description is
    executed.
31. **The runtime interprets a described animation; it does not recognise named ones.**
    `lib/animation/interpreter.dart` takes the active theme's description for a moment and
    produces a running animation on the wrapped child. **There is no table of known animation
    names and no branch on a behaviour string.**

    *Source:* [Animations](../Animations.md) → Decisions → **Themes describe their animations;
    the runtime interprets them**; `P1-03` req 18, which assigns the interpreter here by name —
    *"what executes a track, how tracks compose, one-at-a-time sequencing, non-blocking input,
    the animations-off path."*

    **How it executes:**
    - **One `AnimationController` per animation**, its duration the description's `duration`,
      repeating per `repeat.count` and `repeat.mode` (`restart` replays from the start, `reverse`
      plays back and forth). `count: 1` plays once.
    - **Every track runs concurrently within that one controller** (Requirement 14). A track maps
      its `property` through its `keyframes`, interpolating between successive `{at, value}`
      pairs as a fraction of `duration`.
    - **Easing applies per segment.** A track's `easing` governs each segment; a keyframe's
      optional `easing` overrides it for the segment **ending** at that keyframe. Values map to
      Flutter curves per Requirement 32.
    - **`delay` shifts the track within the animation** — Requirement 41's stated default.
    - **Tracks and keyframes arrive complete.** Because a list is a leaf (Requirement 10), the
      interpreter never merges or fills a partial track list; whatever the materialized theme
      holds is the whole description.
    - **`glowColor` interpolates as a colour**; the other six interpolate as doubles.

    **This requirement replaces an earlier one** that fenced wave 2 to implementing the single
    type string `grow-shrink` — a closed list of one, which Requirement 9 forbids. It was
    withdrawn rather than narrowed.
    *Testable, and this is the Decision's own bar:* a fixture theme describing motion no shipped
    theme uses — a property combination, magnitudes, keyframe count and repeat rule the runtime
    has never been asked for — plays correctly with **no change to any file under `lib/`**. A test
    that adds a fixture theme and asserts the resulting property values at sampled frames, with
    the source tree untouched, is the whole requirement.
32. **[PRD decision] Easing strings map to Flutter curves in two forms, and no others.** The
    schema permits *"cubic-bezier or named curve"* (`P1-03` req 15) without enumerating the
    names, so this layer fixes the mapping:
    - **`cubic-bezier(x1, y1, x2, y2)` → `Cubic(x1, y1, x2, y2)`**, by direct parameter
      correspondence. Flutter's `Cubic` takes the same four control points with the same meaning,
      so this is a four-number read, not a CSS grammar.
    - **A named curve maps to the identically-named member of Flutter's `Curves`** — `easeOut`,
      `easeInOutCubic`, `elasticOut` and so on. **[PRD decision — default]**, chosen because
      `Curves` is already a fixed, documented, closed set, so it needs no table of this PRD's own
      invention. **Reversible**, and flagged under *Gaps* since the schema does not enumerate
      valid names.
    - **Anything else is unexecutable** and reaches Requirement 37's path.

    **Neon's `placeMark` easing is `cubic-bezier(.34,1.56,.64,1)`**, transcribed from the handoff
    per `P1-03` req 13. `y2 = 1.56` exceeds 1.0 deliberately: the mark overshoots its final scale
    and settles back. **That overshoot is the poppiness of Requirement 1 and must be
    preserved** — substituting `Curves.easeOut` produces a technically-animated, characterless
    result that passes every other test in this PRD.
    *Testable:* `cubic-bezier(.34,1.56,.64,1)` resolves to a `Cubic` with those four control
    points and the animated value exceeds its final keyframe value partway through; a named curve
    resolves to the matching `Curves` member; an unrecognised string reaches Requirement 37.
33. **Durations become `Duration`s in this layer, and that is settled with respect to the
    guard.** `ResolvedAnimation.duration` and `ResolvedTrack.delay` are built from theme values
    inside `lib/animation/` — outside `lib/theme/`, the only path `P1-05` req 3 exempts.

    `P1-05` req 6's `duration-literal` pattern is being narrowed to require a **numeric literal**
    argument, so a `Duration` built from a theme value passes while `Duration(milliseconds: 220)`
    still fails. This PRD depends on that narrowing. Note `P1-03` req 25 now makes the converse
    explicit too: *"an interpolation magnitude living in Dart is a theme value that escaped"* — so
    a hardcoded scale factor in this layer is a violation even though no `Duration` is involved.
    *Testable:* the guard scan passes over `lib/animation/` with no baseline entry (`P1-05` req 8
    ships the baseline empty); a literal `Duration(milliseconds: 220)` or a literal interpolation
    magnitude introduced anywhere in this layer fails it.

### The test seam

34. **[PRD decision] `AnimationCoordinator` is the fake sink, and it is injectable.** Tests
    override `animationCoordinatorProvider` with a recording implementation that captures every
    `begin(moment)` call and its return, and never starts real motion. Every *Testable* line that
    says "records" asserts against that recorder.

    Without this the assertions above are unbuildable — the same reason `P2-02-audio.md` requires
    a fake audio sink explicitly, and the same failure mode `P1-05` req 2 fixes by splitting
    `scanSource` from `scanTree`.
    *Testable:* the recording coordinator is a committed test double; no test asserts on animation
    behavior by measuring wall-clock time.
35. **[PRD decision] The clock is the widget test's, never the layer's.** `ThemedAnimation` drives
    motion through a `TickerProvider` (`SingleTickerProviderStateMixin`) and **never** through
    `Timer`, `Future.delayed`, `DateTime.now()` or a `Stopwatch`, so `tester.pump(duration)`
    advances it deterministically.
    *Testable:* no `Timer`, `Future.delayed`, `DateTime.now()` or `Stopwatch` appears under
    `lib/animation/`; a widget test asserts an animation of duration *d* is still running at
    *d* − 1ms and complete at *d*.
36. **[PRD decision] The committed tests for this layer are, at minimum:** trigger-change plays
    and first-build does not (Requirement 6); one-at-a-time across moments, and both tracks of a
    two-track animation driven within one `begin`/`end` pair (Requirement 14); a tap
    mid-animation changes state identically and does not shorten the animation (Requirements 15,
    16); toggle off produces zero `begin` results and an instant render (Requirements 19, 20);
    the five fenced moments return null (Requirement 27); **a fixture theme composing unfamiliar
    motion — including a property no shipped theme uses, such as `rotation` — plays with no
    source change (Requirements 9, 31)**; keyframe interpolation sampled at intermediate frames,
    and a per-keyframe easing override applying only to its own segment (Requirement 31);
    `repeat` in both `restart` and `reverse` modes (Requirement 31); the cubic-bezier mapping
    including its overshoot (Requirement 32); and the guard scan over `lib/animation/`
    (Requirement 33).

    Every one of these is writable **today**: fixture themes supply their own magnitudes, so none
    depends on Neon's unauthored values.

### Stated defaults

> Five behaviors are implied by requirements above or reachable in this wave, and none is settled
> by a design doc. Each is stated as a **default with its reasoning and a reversibility note**, in
> the pattern `P1-05-theme-guard-test.md` req 12 uses — so an agent builds something specific and
> a reviewer can see exactly what to overturn. **None is a ruling**; the user's answers under
> *Blocking* govern where they overlap.

37. **[PRD decision — default] A description the interpreter cannot execute plays nothing, and
    the state change is instant.** A track naming a property outside the closed set, a malformed
    easing string, fewer than two keyframes, or an unreadable value results in no motion —
    identical to the toggle-off path (Requirement 19). The theme still loads and the game still
    runs. It is **not** a theme load failure and does not fall back to different motion.
    Reasoning: Requirement 22 makes animation purely additive, so an unexecutable description must
    degrade to no motion rather than take a screen down, and substituting different motion would
    silently misrepresent what the theme asked for. **Reversible** — see *Blocking*, item 3.
38. **[PRD decision — default] A moment triggered while another is playing is dropped, not
    queued.** `begin` returns null and the second animation does not run; the first is untouched,
    per Requirement 16.
    Reasoning: with `placeMark` around 220ms and a two-tap confirm, a queue accumulates lag and
    ends up animating a mark against a board that has already moved on — which reads as a bug and
    sits badly with Requirement 15's "the game does not wait." Dropping keeps motion aligned with
    current state. **Reversible** — see *Blocking*, item 4. This is the *tap-through* case only;
    **co-occurrence is a different question**, fenced out of this wave by Requirement 27.
39. **[PRD decision — default] State commits before the animation plays, and no animation state
    is persisted.** Both follow from settled requirements and are stated so they are not
    re-derived: Requirement 15 says the game does not wait, so the engine's new state is committed
    and rendered first and the animation plays over it; Requirement 22 makes animation
    presentation-only, so nothing about a running animation is written to Hive or
    `shared_preferences`. Backgrounding mid-animation loses it; resuming shows the settled state.
    *Testable:* the board reflects the new state in the frame the move commits regardless of
    animation; the persisted game object contains no animation field.
40. **[PRD decision — default] Switching animations off mid-flight lets the running animation
    finish; the next moment does not play.** Reasoning: Requirement 16 is a direct Decision about
    a running animation (*"it isn't interrupted or skipped"*), while Requirements 19 and 20
    describe what happens **at a state change** — so the reading that honors both is that the
    toggle governs what starts, not what is already running. Under Requirement 27's fence the
    exposure is a single short window. **Reversible** — see *Blocking*, item 5.
41. **[PRD decision — default] A track's `delay` maps its keyframes into the sub-window
    `[delay / duration, 1.0]` of the animation — Flutter's `Interval`.** The animation's total
    length is always `duration`; a delayed track holds its first keyframe value until its window
    opens. Keyframe `at` fractions are therefore of the track's window, not of the whole
    animation.
    Reasoning: the schema gives `delay` in milliseconds and `at` as a fraction of `duration`
    without saying how they compose, and the alternatives are worse — extending total length to
    `delay + duration` would make a delayed track outlast the animation that contains it, which
    breaks Requirement 14's accounting and Requirement 16's completion assertions. `Interval` is
    Flutter's idiom for exactly this and clamps at both ends. **Reversible**, and recorded under
    *Gaps* as something the schema left open.
    *Testable:* a two-track animation where one track has `delay` equal to half `duration` shows
    that track's first keyframe value until the midpoint, then its interpolation compressed into
    the second half, with both tracks completing at `duration`.

## Out of Scope

Referenced by filename only; this PRD specifies none of them.

- **The motion schema itself** — key paths, value shapes, the property set, versioning:
  `P1-03-theme-system.md` reqs 15 and 18. `Animations.md` → Decisions → Themes describe their
  animations assigns it there explicitly: *"the schema itself belongs to the theme system's PRD
  and is not settled here."* Requirement 30 restates it to compile against and claims no
  ownership.
- **Authoring Neon's animation values**, including the magnitudes — `P1-03` req 13 and its
  Appendix A.2.3. **This PRD authors no theme content and must not edit `assets/themes/`.**
- **The rest of the theme mechanism** — YAML loading, UUID identity, merge-over-Neon,
  materialization: `P1-03-theme-system.md`.
- **The last-move and active-quadrant highlights themselves** — their static treatments, two
  modes, distinguishability, and the locked/pending states: `P3-01-board-rendering.md`. Whether
  either animates is open, and Requirement 27 plays neither.
- **The Settings toggle's UI** — `P4-04-settings.md`. This PRD specifies only what the toggle's
  stored value does to motion.
- **Persisting the toggle** — `P1-04-persistence.md`.
- **The Classic Red vs Blue theme's animation choices** — `P5-01-classic-theme.md`. Classic
  inherits Neon's animations unless it overrides them, and it is the first real test of both
  Requirement 9's bar and Requirement 10's whole-list replacement.
- **The guard test itself**, its pattern set and baseline — `P1-05-theme-guard-test.md`.
- **Screen transition animations** — held by `P2-01-navigation.md`.
- **Who calls the animation.** This PRD owns *what plays and under what rules* and publishes the
  wrapper. Wrapping the mark widget is `P3-01-board-rendering.md`'s; the confirm tap that changes
  the trigger is `P3-02-move-input.md`'s.
- **Sound and haptics** — `P2-02-audio.md`, `P2-03-haptics.md`. Separate channels with separate
  toggles; nothing here couples an animation to a sound or a buzz.
- **Producing any animation asset** — `P5-02-asset-generation-replicate.md`. This layer needs
  none: every property in the closed set is a transform on a widget the theme already supplies.

## Open Questions

### Answered since earlier drafts — recorded so they are not reopened

- **"Does a closed list of animation types violate Requirement 9?"** — **Answered by the user.**
  `Animations.md` → Decisions → *Themes describe their animations; the runtime interprets them*.
  A theme describes motion as data; adding an animation must not require changing game code.
  This was this PRD's one blocking question and it is closed.
- **"Is a closed set of animatable *properties* what Requirement 9 forbids?"** — **No, and this
  is now shipped design rather than a reading.** `P1-03` req 18 closes the property set and
  leaves the composition open, stating the bar directly: *"new motion composed from these
  properties needs no code — that is the bar, and it is met."*
- **"How far does `grow-shrink` grow?"** — **The gap has a home.** Under the descriptive schema
  the magnitude is `animation.<moment>.tracks[].keyframes[].value`, a theme value rather than a
  hidden runtime constant. `P1-03` req 18 credits this PRD with finding it. It still needs
  authoring — see *Gaps*.
- **"What format does the interpreter execute?"** — **Published.** `P1-03` reqs 15 and 18.
  Requirement 30 compiles against it.

### Blocking — needs the user

1. **Marker-only scope vs. animating quadrant-level moments.** `Animations.md` → Scope For Now
   says animations apply to **the player's marker** and *"the marker is the thing that moves"*;
   `Theming.md` → What a Theme Controls → Animation repeats it. But the same doc's Where
   Animations Fire raises animating the **active-quadrant highlight** — a whole quadrant — and
   `P1-03` req 15 marks all six moments required, with req 18 authoring `claimQuadrant`,
   `catGame`, `winGame`, `activeQuadrant` and `lastMove` alongside `placeMark`. Requirements 2,
   25 and 27 record both sides without picking one. Is "marker only" a boundary this version
   holds, or a starting scope the shipped theme data already exceeds?
2. **Do the highlights repeat, and does "one animation at a time" survive it?** Determinate — see
   Requirement 29: `P1-03` req 18 ships `activeQuadrant` and `lastMove` with
   `repeat: {count: infinite, mode: reverse}`, and an infinitely repeating animation overlaps
   everything. Either they do not repeat infinitely, or the Decision is restated as one
   *transient* animation at a time. Must be answered before either moment is played.
3. **What should happen when a theme describes motion the runtime cannot execute?**
   Requirement 37 states a default (play nothing, instant change) so wave 2 is buildable, but the
   alternatives are real: treat it as a theme load failure per `Theming.md` → Decisions → What
   happens if a theme fails to load, or fall back to Neon's description for that moment. Note
   `P1-03` req 18 argues an open property set *"would only move the failure from load time to
   render time"* — which is an argument for validating descriptions at load, and that is a
   position this PRD's default does not take. Live the moment a second theme authors motion.
4. **Queue, drop or replace, when a moment fires while one is playing?** Requirement 38 defaults
   to drop with its reasoning; queue is equally consistent with the docs and feels materially
   different. "Never overlap" rules out both playing; "never interrupted" rules out replacing.
   **Co-occurrence is a separate question** — one confirmed move can be `placeMark` **and**
   `claimQuadrant` **and** `winGame` at the same instant, with no second tap and nothing the
   player did to cause the pile-up, and it may want a different answer (a cascade is plausible
   there and bad in the tap-through case). Requirement 27 fences co-occurrence out of this wave.
   `P2-02-audio.md` OQ-6 raises the identical case for sound and likewise leaves it open.
5. **What happens if animations are switched off while one is playing?** Requirement 40 defaults
   to letting it finish. Requirement 16 says a running animation is never interrupted or skipped;
   Requirements 19 and 20 say that with the toggle off nothing runs. Both readings satisfy the
   wording.

### From the design docs, worded as the docs word them

`Animations.md` → Open Questions is empty (*"Nothing outstanding on this doc right now"*). The
hedges below are carried from the body of the doc.

- **Where animations fire is "not yet decided in detail."** The doc lists placing a marker,
  winning a small board / claiming a quadrant, cat game, and winning the whole game as *"the
  obvious moments"* — explicitly not settled. This PRD commits only the first (Requirement 23).
- **Should the last-move and active-quadrant highlights be animated at all?** As worded: *"The
  last-move highlight and active-quadrant highlight … these could be animated rather than static,
  e.g. a pulsing glow on the legal quadrant."* Left open.
- Which values, concretely, does Classic Red vs Blue override? (`Theming.md` → Open Questions;
  owned by `P5-01-classic-theme.md`.)

### Gaps and routing — not resolved here

- **Neon's motion magnitudes are unauthored, and they gate this PRD's acceptance floor.**
  `P1-03` req 13's residue table puts `animation.<moment>.tracks[].keyframes[].value` in the
  *"needs authoring rather than transcription"* column: *"The magnitudes are drawn nowhere.
  Durations and easings transcribe; the numbers they interpolate between do not exist."* They are
  `deferred`, and `P1-03` instructs agents not to fill deferred keys. So the interpreter,
  Requirement 36's whole test list, and every behavior in this PRD are buildable and verifiable
  **today** against fixture themes — but Requirement 23's visible outcome, a mark that actually
  pops under Neon, is not demonstrable until someone authors them. **Not a guess an implementer
  can make** — `P1-03` req 25 makes a magnitude living in Dart a theme value that escaped, so the
  wrong fix is explicitly closed off. This needs an owner: authoring six moments' worth of
  numbers is a design act, not a transcription.
- **The schema does not enumerate valid named easing curves.** `P1-03` req 15 permits *"cubic-
  bezier or named curve"* without saying which names. Requirement 32 defaults to Flutter's
  `Curves` members, which is checkable and needs no invented table, but the schema should say so
  or say otherwise.
- **`delay` and keyframe `at` have no stated composition.** Requirement 41 states a default
  (Flutter `Interval` semantics). Worth confirming in the schema rather than living only here.
- **Shadowbox has no obviously right property.** Requirement 4 maps it onto `glowRadius` /
  `glowColor`, but a drop shadow that *lifts the marker off the board* is directional and offset,
  which a symmetric glow is not. No theme authors it today, so nothing is blocked; but if
  shadowbox is wanted as drawn, the property set may need an eighth member — a runtime change and
  a version bump per `P1-03` req 18.
- **`P3-01-board-rendering.md` asserts an answer nobody gave.** Its Out of Scope defers *"the
  looping glow-pulse on the active quadrant and the last move, one-at-a-time sequencing,
  non-blocking input, and the animations-off path"* to this PRD as **committed work**. Three of
  those four are committed here. The first is not: it asserts both that those highlights animate
  (Blocking item 1) and that they repeat (Blocking item 2). Under Requirement 27 this wave plays
  neither. **Needs routing** — either `P3-01`'s Out of Scope is reworded as conditional, or the
  scope questions are ruled on and both PRDs updated. `P3-01` is not this PRD's to edit, and
  leaving it unrouted means a wave-3 agent reads a commitment that does not exist.
