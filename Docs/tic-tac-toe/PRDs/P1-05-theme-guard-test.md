**Build-readiness: 89**

# PRD: Hardcoded-Theme-Value Guard Test

> **Status:** Draft · Source docs read: Tech Design.md, Theming.md, Animations.md, Game Board
> Design.md, Menus and UI.md, Game Overview.md, Rules.md, roadmap.md, and the read-only
> reference asset `design_handoff_game_ui/README.md`. `Alternative Game Styles.md` is a
> parking-lot doc and was not used as a source. Tech Design.md and Theming.md were re-read
> after both were revised; this PRD is written against the revised text.
>
> **Revised** to emit the concrete starting pattern set, the baseline artifact and the
> failure format rather than deferring them to "the keyboard" — a coding agent has no
> keyboard, and the previous draft mandated in Requirement 4 what it deferred in
> Requirement 6. Requirement 4 is now honest about what this deliverable does and does not
> reach. Requirement numbering is stable: `P2-02-audio.md` cites requirement 6 and
> `P2-04-animations.md` cites requirement 5.
>
> **Revised again** to narrow `duration-literal` to a numeric-literal argument, which
> removes a determinate deadlock with `P2-04-animations.md` — see the rule's own row for
> why it must not be tightened back.
>
> **Revised again** for `P1-03-theme-system.md` schemaVersion 3, which adds an `icons`
> section and makes chrome glyphs theme data. `icon-constant` widens from board widgets to
> the whole scan root.
>
> **Revised again — 88 → 89.** The user **confirmed** chrome icons are theme-controlled and
> that a theme may name a glyph from a bundled set or ship its own image, closing Open
> Question 3. The `icon-constant` widening is now built on a Decision rather than on a
> sibling PRD's reading. Two named provisionals remain — the Phosphor symbol name and the
> resolver's location — which is why this is +1 and not more.

**Wave:** P1 · **Slug:** `theme-guard-test`

**Depends on:** `P1-01-app-scaffold.md`, which creates the Flutter project, the `lib/` tree
and the test suite this guard runs in. `P1-01` records that it ships before the rest of its
own wave. Parallel-safe with every other P1 PRD.

**Related:** `P1-03-theme-system.md` Requirement 25 states the rule; this PRD is the check
that enforces it, and `P1-03` Requirement 15 holds the authoritative slot inventory — now
including the `icons` section this PRD's `icon-constant` rule defends. This PRD tracks that
inventory rather than restating it.

**Seam with `P2-04-animations.md`.** That PRD's animation layer must construct a `Duration`
**from a theme value** at playback — `Duration(milliseconds: theme.animation.placeMark.durationMs)`
— and its req 13 records the seam from its side, its req 5 forbidding callers from holding
their own timing. Requirement 6's `duration-literal` rule is narrowed to a numeric-literal
argument precisely so that construction is legal. Its req 5's *testable* ("no `Duration`
literal appears in `lib/ui/` outside this layer") implies the layer lives inside this scan
root; that PRD contradicts itself on its own location and is being corrected separately, but
**wherever it lands, this narrowing is what keeps the suite green.** If anyone re-widens the
rule, that PRD goes red on merge with no legal fix.

**Seam with `P1-03-theme-system.md` — where the icon resolver must live.** Now that chrome
icons are theme-controlled, something has to turn an `icons.<slot>` with `kind: iconSet` and
a `set`/`name` pair into a concrete `IconData`. **That resolution must live inside
`lib/theme/`.** This is a constraint this PRD places on the seam, not a requirement it can
write for another PRD: `P1-03` req 5 currently names only `theme.dart` (the merged object)
and `loader.dart` (YAML → theme), so the resolver has no home yet, and `P1-03` is specifying
`icons` resolution now.

The consequence if it lands elsewhere is determinate, not hypothetical. `Icons.` or
`PhosphorIcons.` inside the resolver is exactly what Requirement 6's `icon-constant` rule
catches; Requirement 3 exempts only `lib/theme/`; Requirement 14 forbids any suppression
convention; Requirement 8 forbids baselining a day-one violation. A resolver in `lib/ui/` is
red on merge with no legal fix — the same shape as the `P2-04` deadlock above, which is why
it is worth stating **before** the code exists rather than discovering it at integration.
**The fix in that event is to move the resolver into the theme layer, never to weaken the
rule.**

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
fails when a new one appears, naming the file, line, matched text and slot group so the
developer can fix it. The Architectural Rule stops being a matter of discipline and becomes a
check that a developer trips over the moment they break it — and because the codebase starts
empty, it starts from a clean baseline rather than a backlog of exceptions.

## Requirements

Each requirement cites the doc and section it comes from. Where this PRD decides something the
design docs leave unstated, it says so inline as **[PRD decision]** — those are engineering
choices made to keep the feature buildable, not findings from the docs, and each is cheap to
reverse *today* and expensive once baseline entries exist. Nothing here is sourced from
`Alternative Game Styles.md`.

### The test and what it reads

1. **The guard is an ordinary test, not tooling.** It is a test in the project's test suite,
   executed by `flutter test`, and explicitly **not** a custom analyzer plugin.
   *Source:* [Tech Design](../Tech%20Design.md) → Decisions → Do we add a test that fails on
   hardcoded theme values?

   **[PRD decision] File layout:**
   - `test/theme_guard_test.dart` — the test.
   - `test/support/theme_guard/scanner.dart` — the scanner and the rule table.
   - `test/theme_guard_baseline.json` — the baseline (Requirement 11).
   - `test/support/theme_guard/regenerate_baseline.dart` — the regeneration script.

   **The scanner must not live under `lib/`.** Its rule table contains the banned patterns as
   string literals, so a scanner inside the scan root would flag itself on the first run. Under
   `test/` it is outside the root by Requirement 2 and the problem does not arise.

2. **It scans `lib/`, and the entry points are parameterized.** The production test scans the
   glob `lib/**/*.dart` from the src root.
   *Source:* same Decision (*"scans the source under `lib/`"*).

   **[PRD decision]** The scanner exposes two entry points, and **neither hardcodes
   `Directory('lib')`**:
   - `List<Violation> scanSource({required String source, required String path})` — pure, no
     I/O, takes the source text and the path it should report.
   - `List<Violation> scanTree({required Directory root})` — walks the glob and calls
     `scanSource` per file.

   The production test calls `scanTree` with `lib/`. Requirement 13's verification tests call
   `scanSource` with inline fixture strings. Without this split those tests cannot be written
   at all, which is the likeliest way Requirement 4 quietly goes unmet.

3. **Two exclusions, both by path.**
   - **`lib/theme/` is exempt.** It holds the merged theme object and the YAML loader, so it is
     the one place a literal theme value legitimately appears. It is also **the one place a
     theme's `icons.<slot>` may resolve to a concrete `IconData`** — see the seam note above
     and Requirement 6's `icon-constant` rule, which both depend on that resolution living
     here.
     *Source:* same Decision (*"outside the theme layer itself"*) plus its inline note pinning
     the theme layer to `lib/theme/`, resolved against [Tech Design](../Tech%20Design.md) →
     Decisions → Project structure — layer-first, and `P1-03-theme-system.md` req 5.
   - **Generated files are exempt:** `*.g.dart` and `*.freezed.dart`, anywhere under `lib/`.
     They are machine-written by `freezed` and `json_serializable`, which
     `P1-01-app-scaffold.md` Requirement 14 declares and which
     [Tech Design](../Tech%20Design.md) → Decisions → Serialization and the storage layer puts
     *"generated into `engine/`"* — inside the scan root. A developer cannot fix a violation in
     a file that `build_runner` rewrites. **[PRD decision]** on the exclusion; the citations are
     why such files exist inside `lib/` at all.

   Everything else under `lib/` is scanned, including `main.dart`, `app.dart`, `engine/`,
   `storage/`, `state/`, `navigation/` and `ui/`.

### What the guard is for, and what this deliverable actually reaches

4. **The rule's scope is the slot inventory; this deliverable reaches part of it, and says
   which part.**

   **(a) The rule.** The Architectural Rule enumerates what the theme owns by deriving it from
   what the screens actually consume: colors, backgrounds, fonts, piece styles, sounds and
   animations, **plus** board geometry and sizing (outer gap, quadrant padding, inner gap,
   grid-line width, grid-line inset, mark sizes), corner radii, the type scale, opacities (the
   locked, claimed and cat-game veils), and every named surface — modals, sheets, the settings
   card, open-game rows and their chips, badges, the main-menu logo, and a gradient-capable page
   background. That is the rule the guard exists to enforce, and it is not narrowed here.
   *Source:* [Tech Design](../Tech%20Design.md) → Decisions → Do we add a test that fails on
   hardcoded theme values? (*"covering the slot inventory the Architectural Rule names"*);
   [Theming](../Theming.md) → Architectural Rule; [Theming](../Theming.md) → Decisions → What
   the theme's slots are derived from. The authoritative enumeration is
   `P1-03-theme-system.md` Requirement 15, whose group names — **Board and geometry**,
   **Marks**, **Surfaces and chrome**, **Type**, **Audio**, **Animation** — Requirement 6 uses
   verbatim. As of that PRD's schemaVersion 3 the inventory also carries an **`icons`** section
   (`icons.<slot>.{kind,set,name,path,tint,size}`, slots `settings`, `close`, `chevronLeft`,
   `chevronRight`, `plus`), and its req 25 states that *"an `Icons.*` reference outside the
   theme layer"* is a theme value that escaped.

   **(b) What ships in P1.** The rule set in Requirement 6 reaches: colour literals and the
   Flutter palette, animation durations, the typeface, type sizes and weights, corner radii
   expressed through `BorderRadius`/`Radius`, veil opacities expressed through
   `withOpacity`/`withValues`, mark glyphs in board code, **chrome icon constants anywhere
   outside the theme layer**, and asset paths including the `audioplayers` form and a theme
   folder referenced from a widget. Requirement 13 requires a committed test per rule.

   **(c) What it does not reach, stated as a limitation of this deliverable and not of the
   rule.** Board geometry written as bare numerics — outer gap, quadrant padding, inner gap,
   grid-line width, grid-line inset, mark sizes — and any theme value passed as a positional or
   unlabelled number. A regex cannot tell `SizedBox(width: 8)` holding a themed gap from
   `SizedBox(width: 8)` holding an incidental one; there is no distinctive constructor to match
   on the way `Color(0x…)` has, and no real UI code exists yet to calibrate a noisier rule
   against.

   **The same false-negative character applies to chrome icons, and is worth stating in full
   because three sibling PRDs cite this paragraph to explain why their own testables are weaker
   than they look.** `icon-constant` catches the *constant* form — `Icons.settings`, the thing
   an agent writes when no slot exists. It does not catch a theme-supplied glyph **name**
   hardcoded as a string: `iconFromName('gear')`, or a `switch` over slot names with the
   Phosphor names typed inline, resolves to the same defect and reads to a regex as an ordinary
   string. Nor does it catch a widget that reads `theme.icons.settings` and then ignores
   `tint` or `size` in favour of its own values — that is the "read from the wrong key" class
   `P1-03-theme-system.md` Appendix A.1 catalogues, which no pattern scan can see. **The guard
   claims to catch chrome icons written as Flutter constants. It does not claim the `icons`
   section is fully enforced.**

   **Therefore: completing this PRD must not be reported as satisfying
   [Theming](../Theming.md) → Architectural Rule in full, and the guard being green must not be
   read as the inventory being covered.** Closing (c) is blocked on Open Question 1, which needs
   the user. This clause exists because an earlier draft demanded coverage here that
   Requirement 6 deferred, and the predicted result was a green, well-named guard that met
   neither.

5. **Animation timing counts as a theme value.** A hardcoded `Duration` in scanned source is a
   violation, because timing lives inside the theme's animation definitions — so a literal
   duration is a theme value that escaped.
   *Source:* [Animations](../Animations.md) → Decisions → Duration lives in the animation, cited
   for exactly this purpose by [Tech Design](../Tech%20Design.md) → Decisions → Do we add a test
   that fails on hardcoded theme values?

   **"Hardcoded" means a numeric literal argument.** `Duration(milliseconds: 220)` is a theme
   value that escaped and is a violation; `Duration(milliseconds: someThemeValue)` is the
   correct behaviour this requirement exists to encourage and is **not** a violation. The
   mechanism is Requirement 6's `duration-literal` rule — read that row before acting on this
   requirement alone, because reading req 5 in isolation is what produced a merge deadlock with
   `P2-04-animations.md`.
   *(Cited as "req 5" by `P2-04-animations.md`.)*

### The pattern set

6. **The starting rule set is concrete and ships as written below; sharpening happens against
   it, not instead of it.** Tech Design's indicative table remains *"to be sharpened at the
   keyboard rather than settled here"* and *"not a complete enumeration of that slot
   inventory"* — so this set is a floor to be widened, never a ceiling, and never a substitute
   for Requirement 4(a). What follows is that table transcribed into executable form with the
   three corrections the same Decision records, so that an implementer widens a working rule set
   instead of inventing one.
   *Source:* same Decision — the indicative-patterns table and the two sentences framing it.
   Regex form is **[PRD decision]**; every rule's substance is cited.

   Each rule is `id`, pattern (Dart raw-string `RegExp`), what it matches, and the
   `P1-03` Requirement 15 slot group it defends.

   - **`color-hex`** — `r'\bColor\(\s*0x[0-9A-Fa-f]{6,8}\s*\)'` — `Color(0xFF00E5FF)`.
     Colour slots, all groups.
   - **`color-palette`** — `r'\bColors\.[A-Za-z]\w*'` — `Colors.red`, `Colors.black87`.
     Colour slots, all groups.
   - **`opacity-call`** — `r'\.with(?:Opacity\(|Values\(\s*alpha\s*:)'` — `.withOpacity(0.45)`
     and its non-deprecated successor `.withValues(alpha: 0.45)`. **Board and geometry** (the
     locked, claimed and cat-game veil opacities).
   - **`duration-literal`** —
     `r'\bDuration\(\s*(?:days|hours|minutes|seconds|milliseconds|microseconds)\s*:\s*[\d._]+\s*[,)]'`
     — `Duration(milliseconds: 220)`. **Animation**, per Requirement 5.

     **The argument must be a numeric literal, and this must not be "tightened" back to
     matching any `Duration(unit:` at all.** A constructor-only pattern creates a determinate
     deadlock: `P2-04-animations.md` req 13 requires its animation layer to build
     `Duration(milliseconds: theme.animation.placeMark.durationMs)` at playback, necessarily
     **outside** `lib/theme/`; Requirement 3 exempts only that path, Requirement 14 forbids any
     suppression convention, and Requirement 8 forbids baselining a day-one violation. The
     suite would be red on merge with no legal fix. Requiring a literal argument preserves the
     rule's entire purpose — a typed-in duration is caught, a theme-derived one passes — and
     that distinction *is* the behaviour the guard exists to encourage.

     **Known limitations, stated so they are not mistaken for oversights.**
     `const kPop = Duration(milliseconds: 220);` at file scope still matches, which is correct:
     the literal is still hardcoded, merely named. An intermediate variable
     (`final ms = 220; … Duration(milliseconds: ms)`) defeats the rule, as does arithmetic
     (`milliseconds: 110 * 2`) — the same regex limitation acknowledged for the other rules in
     Requirement 4(c), not a special weakness here.
   - **`font-family-literal`** — `r'''fontFamily\s*:\s*['"]'''` — `fontFamily: 'Inter'`.
     **Type**.
   - **`font-size-literal`** — `r'fontSize\s*:\s*[\d.]+'` — `fontSize: 22`. **Type**.
   - **`font-weight-literal`** — `r'\bFontWeight\.\w+'` — `FontWeight.w600`. **Type**.
   - **`radius-literal`** —
     `r'\b(?:BorderRadius\.(?:circular|all)|Radius\.circular)\(\s*[\d.]+'` —
     `BorderRadius.circular(11)`. **Surfaces and chrome** / **Board and geometry** (corner
     radii).
   - **`asset-source`** — `r'''AssetSource\(\s*['"]'''` — `AssetSource('audio/place.mp3')`.
     **Audio**.
   - **`asset-path`** — `r'''['"]assets/[^'"]+['"]'''` — a literal `assets/…` path. **Audio**
     and **Surfaces and chrome** (images, backgrounds, the logo). This rule is what covers the
     `kind: image` half of the `icons` section — see the note below it.
   - **`icon-constant`** — `r'\b(?:Icons|CupertinoIcons|PhosphorIcons\w*)\.\w+'` —
     `Icons.settings`, `Icons.close`. **Surfaces and chrome** (`icons.<slot>`).
     **Applies across the whole scan root**, i.e. everywhere under `lib/` except the paths
     Requirement 3 exempts.

     **Scope, not existence.** `Icons.` is legitimate **inside `lib/theme/`**, which is where a
     `kind: iconSet` slot resolves a `set`/`name` pair to a concrete `IconData`. Requirement 3
     already exempts that path, so no new exemption is introduced: the rule is simply unscoped
     and the theme layer is the permitted directory, consistent with every other resolution
     point in this PRD. The resolver landing there is a precondition, not an assumption — see
     the seam note above.

     *Source:* **the user's Decision that chrome icons are theme-controlled, and that a theme
     may either name a glyph from a bundled icon set or ship its own image** (confirmed in
     review; `Theming.md` gains the Decision and [Tech Design](../Tech%20Design.md)'s guard
     table has its *"inside board widgets"* scoping corrected — both dispatched to
     `forge-doc-writer`, neither this PRD's to write). Implemented in
     `P1-03-theme-system.md` Requirement 15's `icons` section and stated as a rule by its req
     25: *"an `Icons.*` reference outside the theme layer is one too, which the guard's
     board-widgets-only scoping currently misses."* **Re-point this citation at `Theming.md`
     once that Decision lands** — the Decision is the source, and the two PRDs are its current
     carriers.

     **What this rule's default means, stated because it is the intended behaviour rather than
     an inference:** a hardcoded menu icon **fails the build**. It was invisible to the guard
     before this widening.

     **One provisional, and it is the symbol name, not the rule.** `PhosphorIcons\w*` is written
     as a family match because **no PRD declares a Phosphor package yet**:
     `P1-01-app-scaffold.md` Requirement 14's amendment path says *"an icon package, if Phosphor
     ships as one, by whichever PRD lands it,"* and its Open Questions still carries *"Does
     Phosphor ship as a package dependency or as bundled icon art?"*, owned by the first screen
     PRD that draws a chrome icon. So:
     - **If Phosphor ships as a package**, replace the family match with that package's actual
       symbol root once `P1-01` req 14 names it. `phosphor_flutter` has changed its API across
       versions, so the family match is a placeholder for a real symbol, not a considered
       pattern.
     - **If Phosphor ships as bundled art**, `PhosphorIcons.*` never appears in source at all,
       the `Icons`/`CupertinoIcons` alternatives carry this rule alone, and `asset-path` carries
       the art. Nothing else changes.

     Either way the rule's substance — Flutter icon constants outside the theme layer are
     violations — is settled. Only the third alternative in the pattern is pending.
   - **`mark-glyph`** — `r'''['"](?:X|O|✕|○|Ø)['"]'''` — a mark drawn as a literal. **Marks**.
     *Scoped to `lib/ui/board/`* — unchanged. Marks are board values, and a bare `'X'` in a menu
     is far more likely to be ordinary text than an escaped theme value. Only `icon-constant`
     widened.

   **The `kind: image` half of the `icons` section is in scope this wave, and it is
   `asset-path` that covers it.** A slot may ship an asset path instead of a glyph name — now
   confirmed as part of the Decision — so `AssetImage('assets/themes/neon/gear.png')` or
   `Image.asset('assets/…')` written in a widget is the same defect wearing different clothes,
   and because `asset-path` already applies across the whole scan root, it is already caught
   with no new rule required. Stated explicitly rather than left silent, because a silent
   omission reads as coverage. **The residual gap:** a path assembled rather than written
   (`'assets/themes/$name/gear.png'`, or a constant joined at runtime) defeats it, the same
   regex limitation as everywhere else. The compliant form —
   `Image.asset(theme.icons.settings.path)` — correctly produces no violation.

   Note the shape `duration-literal` shares with `font-size-literal` and `radius-literal`: each
   matches a **labelled numeric literal** and lets an expression through. That is the general
   form of the escape a caller is meant to use — read the value from the theme and pass it —
   and any rule added later should follow it.

   **The three corrections, as recorded in the source Decision.** These are why the set above
   differs from the doc's table, and each is a finding to sharpen, not a redesign:
   - **Sounds** — the doc's rule looks for literal `assets/…` paths, but `audioplayers` uses
     `AssetSource('audio/…')` and supplies the `assets/` prefix itself, so a literal `assets/`
     path never appears for a sound. `asset-source` is added to cover it. `asset-path` is
     **retained** rather than replaced, because image and background paths have no
     prefix-supplying API hiding them. (`audioplayers` per [Tech Design](../Tech%20Design.md) →
     Decisions → Audio package. `P2-02-audio.md` cites this observation as "requirement 6".)
   - **Fonts** — `GoogleFonts.*` is **dropped**: it will never appear, because Inter is bundled
     rather than fetched. Literal `fontFamily:` is kept. (See [Theming](../Theming.md) →
     Decisions → Does a theme supply its own font, which makes Inter *Neon's* font choice rather
     than an app-wide constant, and `P1-03-theme-system.md` req 19.)
   - **Piece styles** — `'X'`/`'O'` alone is insufficient: Neon's approved marks are `✕ ○ Ø`,
     authored as glyph slots (`P1-03-theme-system.md` req 16; `neon.theme.json` → `marks`). All
     five are matched.

   **Exempt contexts.** A match inside a `//` line comment, a `///` doc comment or a `/* … */`
   block comment is never a violation. **String literals are exempt per rule, not globally** —
   `color-hex`, `color-palette`, `opacity-call`, `duration-literal`, `font-family-literal`,
   `font-size-literal`, `font-weight-literal`, `radius-literal` and `icon-constant` match code
   and ignore text inside string literals, while `asset-source`, `asset-path` and `mark-glyph`
   look **inside** string literals by design. A blanket string exemption would silently disable
   the last three. **[PRD decision]**

   **A note on legitimate reads.** The guard bans literals; it does not allow-list the way a
   value is read. `P1-03-theme-system.md` Open Questions notes three legitimate read paths —
   `ThemeData` via `Theme.of(context)`, a `ThemeExtension` via the same, and the
   Riverpod-exposed theme object. None of them appear in the rule set, so however that split
   lands, the pattern set does not change.

### The baseline

7. **The guard holds a per-file baseline and fails when a new violation appears.** Violations
   are recorded per file; a file that gains a violation beyond its recorded baseline fails the
   test.
   *Source:* same Decision (*"holds a per-file baseline that fails when a new violation
   appears"*).

   **[PRD decision] A baseline entry is keyed on `(file path, rule id, matched text)` and
   carries an occurrence count.** The scan fails when a `(path, rule, match)` triple is absent
   from the baseline, or when its occurrence count exceeds the recorded count. This is the
   highest-value unstated decision in the feature, because all three plausible readings satisfy
   the sentence above while behaving differently:
   - *Count per file* would let a developer delete one violation and add a different one in the
     same file with the total unchanged — a silent pass on a real regression.
   - *Line numbers in the key* would fail spuriously on any edit that shifts lines, and a guard
     that cries wolf gets deleted.
   - *Matched text* is stable under line moves and catches the swap. It collapses duplicates of
     the identical literal in one file, which the occurrence count restores.

   **Line numbers are reported (Requirement 10) but never stored in the baseline.** That
   separation is the point: precise output, stable key.

   **Adding or widening a rule interacts with the baseline, and the rule id in the key is what
   makes it safe.** A new rule id can only *add* findings; it cannot orphan, rewrite or silently
   absorb an existing entry, and widening an existing rule's path scope — as `icon-constant`
   just did — leaves entries already keyed on that id matching exactly as before. **Adding a
   rule is not a licence to baseline what it finds:** Requirement 8 governs, so newly surfaced
   violations get fixed. Today the question is moot — the baseline is `{}` and no application
   code exists — which is precisely why the `icons` widening is free to land now and would not
   have been later. The same applies to swapping `PhosphorIcons\w*` for a real symbol root once
   `P1-01` names one.

8. **The baseline ships empty, and a scaffold that trips the guard gets fixed rather than
   recorded.** At the time this feature lands the committed baseline contains zero entries,
   because there is no application code yet.
   *Source:* same Decision (*"There is no application code yet, so the baseline starts at
   zero"*); [Tech Design](../Tech%20Design.md) → Decisions → Fresh build, not a refactor.

   **Consequence, stated because the day-one case is otherwise ambiguous:** if code already in
   `lib/` trips the guard when this lands, the resolution is to **change that code**, not to
   seed the baseline with it. Requirement 8 admits no exception, and a baseline seeded on day
   one would ship exactly the backlog this feature exists to prevent. This is now aligned from
   the other side: `P1-01-app-scaffold.md` Requirement 13 deletes the generated counter demo and
   requires its replacement placeholder to contain *"no color, icon, font-size, duration or
   asset-path literal"* — one clause per rule family in Requirement 6. The expected state at
   merge is a `lib/` that scans clean. **If it does not, this PRD is blocked on that fix, not on
   a baseline entry.**

9. **It runs in the default local test run.** The guard is part of what `flutter test` executes
   with no extra flag, tag, or separate command, since a local run is the only thing that will
   ever execute it.
   *Source:* [Tech Design](../Tech%20Design.md) → Decisions → CI — local builds only, which names
   the hardcoded-theme-value test directly.
   *Consequence, stated in that Decision:* **nothing runs this on a push.** No CI exists. The
   guard catches a violation when someone runs the suite locally and not before, so a violation
   can be committed and pushed unnoticed. That is the accepted cost of the no-CI decision, not a
   gap in this feature.

10. **[PRD decision] The failure message names, per new violation: relative file path, 1-based
    line number, rule id, the matched text, and the slot group.** One line each, plus a footer
    giving the total and pointing at the regeneration script. Format:

    ```
    lib/ui/board/cell.dart:42  [color-palette]  Colors.red  → slot group: Board and geometry
    ```

    A guard that fails with *"1 new violation"* and no location is a guard someone deletes
    rather than debugs. This is also what Requirement 13's tests assert against, so the format
    is load-bearing rather than cosmetic.

11. **[PRD decision] The baseline artifact.**
    - **Path:** `test/theme_guard_baseline.json`.
    - **Format:** a JSON object mapping relative file path → array of
      `{"rule": <id>, "match": <matched text>, "count": <int>}`, sorted by path, then rule, then
      match, so the file diffs cleanly and a reviewer sees exactly what was added.
    - **Ships as:** `{}` (Requirement 8).
    - **Regeneration:** `dart run test/support/theme_guard/regenerate_baseline.dart`, run
      deliberately and **never** as part of `flutter test`. A guard that rewrites its own
      baseline during the run always passes and checks nothing.
    - **Review rule:** a diff that adds baseline entries is a diff that adds hardcoded theme
      values, and should be read that way. A diff that adds entries *while* adding a rule is the
      case Requirement 7 forbids.

12. **[PRD decision] Fewer violations than the baseline passes.** A file whose violations have
    been fixed does not fail; the test prints a note naming the stale entries so they can be
    pruned. Failing on improvement would make the safe direction — deleting a hardcoded value —
    the one that breaks the build. The docs settle only the other direction (Requirement 7), so
    this is a default chosen for safety, and it is reversible.

13. **[PRD decision] The verification cases ship as committed tests, one per rule in
    Requirement 6.** Each calls `scanSource` (Requirement 2) with an inline fixture string
    holding one representative violation, asserting the rule id, the reported line number and
    the matched text; and a companion case asserts that the compliant form of the same construct
    produces no violation. Inline strings rather than fixture files, so no fixture ever sits
    inside the scan root and trips the real scan.

    **`duration-literal` carries a third, mandatory case:**
    `Duration(milliseconds: theme.animation.placeMark.durationMs)` produces **no** violation.
    That case is the regression test for the deadlock described in Requirement 6, and it is what
    makes a later re-widening of the rule fail loudly here instead of silently in
    `P2-04-animations.md`.

    **`icon-constant` carries two path-dependent cases**, because its whole substance is scope:
    `Icons.settings` at a `lib/ui/menus/…` path **is** a violation, and the same source text at
    a `lib/theme/…` path is **not**. Both are expressible through `scanSource`'s `path`
    parameter without touching the filesystem — which is the reason that parameter exists. The
    second case is also the regression test for the seam constraint above: if the icon resolver
    is later moved out of `lib/theme/`, that test still passes while the real scan goes red,
    which is the correct signal — the resolver moved, the rule did not.

    Without this requirement, Requirement 4(b) is unverifiable, and the likely outcome is that
    these tests are never written at all.

14. **[PRD decision] The baseline file is the only exception mechanism.** There is no
    `// ignore:` comment convention, no allow-list annotation and no per-line suppression, and
    none may be invented while building this — a suppression convention invented here has to be
    honored forever. If a legitimate literal exists outside `lib/theme/`, it lives in the
    baseline and is visible in review. Whether a real escape hatch *should* exist is Open
    Question 2.

## Out of Scope

- **The theme system itself** — the theme object, the slot inventory's implementation, the YAML
  loader, merge-over-Neon, materialization, the `icons` schema, and **where the icon resolver
  lives**. See `P1-03-theme-system.md`, whose Requirement 25 is the rule this PRD checks. This
  PRD delivers the guard and states its precondition on the resolver's location; it does not
  specify the resolver.
- **The animation layer itself** — how a moment is named, how playback reaches the theme, and
  where that layer lives → `P2-04-animations.md`. This PRD only guarantees its theme-derived
  `Duration` construction is legal.
- **The rules-engine unit tests** (`P1-02-engine-rules.md`) and the **board widget tests**
  (`P3-01-board-rendering.md`). Three separate test decisions sit side by side in
  [Tech Design](../Tech%20Design.md) → Decisions; this is only the third.
- **Project setup** — creating the Flutter project, `lib/` layout, and the dependency set,
  including **whether Phosphor ships as a package or as bundled art**. See
  `P1-01-app-scaffold.md` Requirement 14 and its Open Questions, which own that call; this PRD
  only records what its `icon-constant` pattern does under either outcome.
- **A custom analyzer plugin or a lint rule.** Explicitly ruled out by the source Decision.
- **CI enforcement.** [Tech Design](../Tech%20Design.md) → Decisions → CI — local builds only.
- **Validating the contents of a theme file.** The guard checks code that bypasses the theme; it
  does not check that a theme file is correct or complete. See Open Question 5.
- **Catching a value read from the wrong slot.** `P1-03-theme-system.md` Appendix A.1 catalogues
  this limit — including its own entry for the settings glyph — and its Requirement 13 states
  it: an implementer reaching for a near-miss key is not hardcoding anything, so no pattern scan
  can see it.
- **Checking `engine/` purity or import layering.** `P1-01-app-scaffold.md` Open Questions asks
  whether its Requirements 4 and 5 get an automated check. Same shape, different rule set, and
  not decided anywhere — this PRD does not absorb it.
- **Anything outside `lib/`** — `test/`, `assets/`, `ios/`, and the read-only
  `design_handoff_game_ui/` bundle are not scanned. The Decision scopes the scan to `lib/`.
- **Haptics and vibration.** Haptics are not theme-driven; they are an app-level setting, so a
  literal haptic value is not a theme value that escaped.
  *Source:* [Theming](../Theming.md) → What a Theme Does NOT Control.

## Open Questions

1. **The bare-numeric slots — how far does the P1 guard go?** Requirement 4(c) names what the
   rule set cannot reach: board geometry as bare numerics, and theme values passed positionally.
   Two ways forward, and this one needs a call rather than more reading:
   - **Narrow P1 formally** — colours, durations, fonts, type sizes and weights, radii, opacity
     calls, assets, marks and chrome icons now; the remaining numeric slots deferred until real
     UI code exists to calibrate a noisier rule against. Requirement 4 is then amended to say
     the inventory is covered *as far as P1 claims*, and the deferral is tracked against a later
     wave.
   - **Adopt an AST mechanism** — the `analyzer` package, matching argument positions such as
     `borderRadius:`, `opacity:`, `fontSize:`, `padding:` and `width:` under `lib/ui/`, which
     can distinguish a themed gap from an incidental one where a regex cannot. This is a larger
     build than the source Decision anticipated, and it sits close to the *"not a custom
     analyzer plugin"* line — an `analyzer`-based test is still an ordinary test, but it is
     worth confirming that reading is intended.

   Requirement 4 is written to stay honest under either answer. It is *not* written to let the
   question be skipped: leaving it open leaves a named gap in the guard.

   **This is now the only thing capping this PRD's build-readiness.**

2. *(Raised by this PRD.)* **Should a real escape hatch exist?** Requirement 14 makes the
   baseline the only exception mechanism, which is the safe default but not obviously the right
   long-term answer — a pre-theme bootstrap color in `main.dart` before the theme has loaded, or
   a crash-report fallback per [Tech Design](../Tech%20Design.md) → Decisions → Crash reporting,
   would each sit in the baseline looking like a defect rather than a decision.

3. **~~Are chrome icons theme values?~~ CLOSED — confirmed, both halves.** Retained as a
   numbered entry rather than renumbered away, because earlier revisions of this PRD and its
   siblings refer to "Open Question 3."

   **The answer: chrome icons are theme-controlled, and a theme may either name a glyph from a
   bundled icon set or ship its own image.** Both halves of `P1-03-theme-system.md`'s Blocking
   item 9 are confirmed. Consequences, all now landed in this PRD:
   - `icon-constant` applies across the whole scan root with `lib/theme/` permitted
     (Requirement 6). A hardcoded menu icon fails the build — intended, not inferred.
   - The `kind: image` escape is covered by `asset-path` (Requirement 6).
   - The resolver must live in `lib/theme/` (seam note above).

   Two follow-ups are **not** this PRD's to make and are already dispatched to
   `forge-doc-writer`: `Theming.md` gains the Decision, and
   [Tech Design](../Tech%20Design.md)'s guard table has its *"inside board widgets"* scoping
   corrected — the contradiction with `P1-03` req 25 that surfaced this. When the `Theming.md`
   Decision lands, Requirement 6's `icon-constant` citation should be re-pointed at it.

4. *(Raised by this PRD — narrowed, no longer blocking.)* **Should a `Duration` that is not
   theme timing be exempt?** The animation layer is **no longer** the open case: Requirement 6
   lets `Duration(milliseconds: <expression>)` through, so theme-derived playback timing is
   legal and `P2-04-animations.md` is unblocked.

   What remains open is narrower and does not block this PRD. **Recorded as intended for now:**
   a `Duration` built from a numeric literal is a violation *wherever it appears in the scan
   root*, including timing that is not a theme value at all — a debounce interval, a storage
   timeout, an animation-off delay. A literal at file scope (`const kTimeout = Duration(seconds:
   5);`) trips it too. The guard cannot distinguish themed timing from incidental timing, and
   the escape is the same either way: name the value and pass it as an expression. Whether that
   is an acceptable tax on non-theme code, or whether such timing deserves an exemption, is the
   user's call — but nothing is blocked while it stays open.

5. **Theme files that misspell a key are not guarded.** Stated as
   [Tech Design](../Tech%20Design.md) → Open Questions → 2. Theme loading:

   > What happens to an unknown or misspelled *key* inside an otherwise-valid theme file?
   > Merge-over-Neon will quietly fill the gap with Neon's value, so a typo in a theme file
   > fails silently. The hardcoded-theme-value test guards code that bypasses the theme; it
   > does not guard a theme file that misspells a key.

   Left open. This PRD does not extend the guard to cover it.
