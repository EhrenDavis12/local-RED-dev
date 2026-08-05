# PRD: Hardcoded-Theme-Value Guard Test

> **Status:** Draft · Source docs read: Tech Design.md, Theming.md, Animations.md, Game Board
> Design.md, Menus and UI.md, Game Overview.md, Rules.md, roadmap.md, and the read-only
> reference asset `design_handoff_game_ui/README.md`. `Alternative Game Styles.md` is a
> parking-lot doc and was not used as a source. Tech Design.md and Theming.md were re-read
> after both were revised; this PRD is written against the revised text.

**Wave:** P1 · **Slug:** `theme-guard-test`

**Dependencies.** Parallel-safe with the rest of wave 1 in authorship. To *run*, it needs the
Flutter project and test suite from `P1-01-app-scaffold.md` to exist. It does not depend on
`P1-03-theme-system.md` being built — the baseline starts empty, so the guard is meaningful
against an empty `lib/` and stays meaningful as code lands — but `P1-03` carries the full slot
inventory this guard is scoped against, and this PRD tracks that list rather than restating it.

## Problem

[Theming](../Theming.md) → Architectural Rule states the constraint that touches every file in
the app: *"All of our code operates off of the theme. No code should be operating independently
from the selected theme."* [Tech Design](../Tech%20Design.md) → What the Design Docs Already
Imply → The theme system is the main architectural risk names why that is dangerous — it is the
one constraint that is expensive to retrofit, and today nothing enforces it. A single
`Color(0xFF00E5FF)`, a `Duration(milliseconds: 200)`, a corner radius, a veil opacity or a type
size typed inline is invisible at review time, works fine under Neon, and only surfaces as a bug
when Classic Red vs Blue is selected and one thing on screen refuses to change. Since there is
no application code yet ([Tech Design](../Tech%20Design.md) → Decisions → Fresh build, not a
refactor), the cost of holding the line is zero today and grows with every file added.

## Goal

An ordinary test in the suite scans `lib/` for values that should have come from the theme and
fails when a new one appears. The Architectural Rule stops being a matter of discipline and
becomes a check that a developer trips over the moment they break it — and because the codebase
starts empty, it starts from a clean baseline rather than a backlog of exceptions.

## Requirements

Each requirement cites the doc and section it comes from. Nothing here is sourced from
`Alternative Game Styles.md`.

1. **The guard is an ordinary test, not tooling.** It is a test in the project's test suite,
   executed by `flutter test`, and explicitly **not** a custom analyzer plugin.
   *Source:* [Tech Design](../Tech%20Design.md) → Decisions → Do we add a test that fails on
   hardcoded theme values?

2. **It scans source under `lib/`.** The scan reads the app's Dart source under `lib/` and
   inspects it for banned patterns.
   *Source:* same Decision.

3. **The theme layer is exempt, and it is exempt by path.** Files under `lib/theme/` are
   excluded from the scan; everything else under `lib/` is scanned. `lib/theme/` is where the
   merged theme object and the YAML loader live, so it is the one place a literal theme value
   legitimately appears.
   *Source:* same Decision (*"outside the theme layer itself"*) plus its inline note pinning the
   theme layer to `lib/theme/`, which resolves against
   [Tech Design](../Tech%20Design.md) → Decisions → Project structure — layer-first.

4. **The guard's scope is the slot inventory, not a closed category list.** The Architectural
   Rule enumerates what the theme owns by deriving it from what the screens actually consume:
   colors, backgrounds, fonts, piece styles, sounds and animations, **plus** board geometry and
   sizing (outer gap, quadrant padding, inner gap, grid-line width, grid-line inset, mark
   sizes), corner radii, the type scale (sizes and weights, distinct from the typeface),
   opacities (the locked, claimed and cat-game veils), and every named surface — modals, sheets,
   the settings card, open-game rows and their chips, badges, the main-menu logo, and a
   gradient-capable page background. The guard covers that inventory. A guard that catches a
   stray `Color(…)` but cannot catch a hardcoded corner radius, veil opacity, type size or
   grid-line width does **not** satisfy this requirement.
   *Source:* [Tech Design](../Tech%20Design.md) → Decisions → Do we add a test that fails on
   hardcoded theme values? (*"covering the slot inventory the Architectural Rule names"*);
   [Theming](../Theming.md) → Architectural Rule (the inventory itself);
   [Theming](../Theming.md) → Decisions → What the theme's slots are derived from (why it is
   derived from the screens rather than written in the abstract).
   *Tracking, not duplication:* the inventory is quoted above only so this requirement is
   testable today. `P1-03-theme-system.md` carries the authoritative slot list; where the two
   diverge, that PRD and the Architectural Rule win.
   *Verification:* for each group in the inventory, a representative violation introduced into a
   scanned file fails the suite, and removing it passes.

5. **Animation timing counts as a theme value.** A hardcoded `Duration` in scanned source is a
   violation, because timing lives inside the theme's animation definitions — so a literal
   duration is a theme value that escaped.
   *Source:* [Animations](../Animations.md) → Decisions → Duration lives in the animation, cited
   for exactly this purpose by [Tech Design](../Tech%20Design.md) → Decisions → Do we add a test
   that fails on hardcoded theme values?

6. **The concrete pattern set is sharpened during implementation, not frozen here.** Tech Design
   gives an indicative table — raw `Color(0x…)` literals and `Colors.*`; hardcoded `Duration(…)`;
   `GoogleFonts.*` and literal `fontFamily:`; hardcoded `'X'`/`'O'` strings and `Icons.*` inside
   board widgets; literal `assets/…` paths outside the theme layer — and states plainly both that
   these are *"to be sharpened at the keyboard rather than settled here"* and that they are
   *"not a complete enumeration of that slot inventory."* This PRD carries that framing intact:
   the table is the starting point, and the obligation is Requirement 4.
   *Source:* same Decision — the indicative-patterns table and the two sentences framing it.

   **Known misses to sharpen.** The same Decision records three indicative patterns that review
   found miss the idiomatic form this project actually decided on. They are findings to sharpen,
   not a redesign of the guard:
   - **Sounds** — the rule looks for literal `assets/…` paths, but `audioplayers` uses
     `AssetSource('audio/…')` and supplies the `assets/` prefix itself, so a literal `assets/`
     path never appears. (`audioplayers` per [Tech Design](../Tech%20Design.md) → Decisions →
     Audio package.)
   - **Fonts** — the rule looks for `GoogleFonts.*`, which will never appear, because Inter is
     bundled rather than fetched. (See [Theming](../Theming.md) → Decisions → Does a theme
     supply its own font, which makes Inter *Neon's* font choice rather than an app-wide
     constant.)
   - **Piece styles** — the rule looks for `'X'`/`'O'`, while Neon's approved marks are
     `✕ ○ Ø`.

   *(Observation, not from the docs.)* The slots named in Requirement 4 beyond the original six
   — geometry, radii, the type scale, opacities — appear in source as bare numeric literals,
   with no distinctive constructor to match on the way `Color(0x…)` has. That is where the
   sharpening work actually lands, and it is the difference between a guard that satisfies
   Requirement 4 and one that only looks like it does.

7. **The guard holds a per-file baseline and fails when a new violation appears.** Violations are
   recorded per file; a file that gains a violation beyond its recorded baseline fails the test.
   *Source:* same Decision (*"holds a per-file baseline that fails when a new violation
   appears"*).
   *Verification:* adding a violation to a file with no recorded violations fails the suite.

8. **The baseline ships empty.** At the time this feature lands, the committed baseline contains
   zero recorded violations, because there is no application code yet.
   *Source:* same Decision (*"There is no application code yet, so the baseline starts at
   zero"*); [Tech Design](../Tech%20Design.md) → Decisions → Fresh build, not a refactor.

9. **It runs in the default local test run.** The guard is part of what `flutter test` executes
   with no extra flag, tag, or separate command, since a local run is the only thing that will
   ever execute it.
   *Source:* [Tech Design](../Tech%20Design.md) → Decisions → CI — local builds only, which names
   the hardcoded-theme-value test directly.
   *Consequence, stated in that Decision and worth repeating to whoever builds this:* **nothing
   runs this on a push.** No CI exists. The guard catches a violation when someone runs the
   suite locally and not before, so a violation can be committed and pushed unnoticed. That is
   the accepted cost of the no-CI decision, not a gap in this feature.

## Out of Scope

- **The theme system itself** — the theme object, the slot inventory's implementation, the YAML
  loader, merge-over-Neon, materialization. See `P1-03-theme-system.md`. This PRD delivers the
  guard, not the thing being guarded.
- **The rules-engine unit tests** (`P1-02-engine-rules.md`) and the **board widget tests**
  (`P3-01-board-rendering.md`). Three separate test decisions sit side by side in
  [Tech Design](../Tech%20Design.md) → Decisions; this is only the third.
- **Project setup** — creating the Flutter project, `lib/` layout, dependencies. See
  `P1-01-app-scaffold.md`.
- **A custom analyzer plugin or a lint rule.** Explicitly ruled out by the source Decision.
- **CI enforcement.** [Tech Design](../Tech%20Design.md) → Decisions → CI — local builds only.
- **Validating the contents of a theme file.** The guard checks code that bypasses the theme; it
  does not check that a theme file is correct or complete. See Open Questions.
- **Anything outside `lib/`** — `test/`, `assets/`, `ios/`, and the read-only
  `design_handoff_game_ui/` bundle are not scanned. The Decision scopes the scan to `lib/`.
- **Haptics and vibration.** Haptics are not theme-driven; they are an app-level setting, so a
  literal haptic value is not a theme value that escaped.
  *Source:* [Theming](../Theming.md) → What a Theme Does NOT Control.

## Open Questions

1. **Theme files that misspell a key are not guarded.** Stated as
   [Tech Design](../Tech%20Design.md) → Open Questions → 2. Theme loading:

   > What happens to an unknown or misspelled *key* inside an otherwise-valid theme file?
   > Merge-over-Neon will quietly fill the gap with Neon's value, so a typo in a theme file
   > fails silently. The hardcoded-theme-value test guards code that bypasses the theme; it
   > does not guard a theme file that misspells a key.

   Left open. This PRD does not extend the guard to cover it.

2. **The exact patterns per slot.** Deliberately deferred by
   [Tech Design](../Tech%20Design.md) → Decisions → Do we add a test that fails on hardcoded
   theme values?: the indicative table is *"to be sharpened at the keyboard rather than settled
   here"* and is *"not a complete enumeration of that slot inventory."* Recorded as deferred,
   not resolved. The three known misses in Requirement 6 are inputs to that sharpening, not an
   answer to it.

3. *(Raised by this PRD — not from the docs.)* **Where does the baseline live, and in what
   format?** A checked-in file beside the test, a constant in the test, or a generated snapshot?
   The docs say a per-file baseline exists but not what it is. Answering it costs nothing today
   because it starts empty; it becomes expensive to change once entries exist.

4. *(Raised by this PRD.)* **Does the baseline ratchet downward?** Settled: it fails when a new
   violation appears. Unstated: what happens when a file has *fewer* violations than its
   baseline — silently pass, or fail until the baseline is tightened?

5. *(Raised by this PRD.)* **Is there a sanctioned escape hatch?** Requirement 3 exempts
   `lib/theme/` and nothing else, so a legitimate literal elsewhere — e.g. a pre-theme bootstrap
   color in `main.dart` before the theme has loaded, or a crash-report fallback per
   [Tech Design](../Tech%20Design.md) → Decisions → Crash reporting — has no way to be recorded
   as intentional other than living in the baseline. Whether an inline ignore or allow-list
   exists is not decided.

6. *(Raised by this PRD — a scope tension in the source material.)* **Are chrome icons theme
   values?** The indicative table scopes `Icons.*` and `'X'`/`'O'` to *"inside board widgets"*,
   narrower than Requirement 2's scan scope of all `lib/` outside `lib/theme/`. Meanwhile
   [Design Handoff](../design_handoff_game_ui/README.md) → Assets requires the real Phosphor set
   for chevron-left, chevron-right, plus, x and sliders-horizontal — navigation chrome, not
   "piece styles," which is the slot [Theming](../Theming.md) → Architectural Rule actually
   names. Whether a Phosphor chevron in a menu widget is a theme value or an app-level asset is
   not settled anywhere.
