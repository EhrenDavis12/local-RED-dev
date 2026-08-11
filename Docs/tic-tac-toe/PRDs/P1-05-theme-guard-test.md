**Build-readiness: 95**

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
> **Revised again** for `P1-03-theme-system.md` schemaVersion 3, which added an `icons`
> section and made chrome glyphs theme data. `icon-constant` widened from board widgets to
> the whole scan root. *(Historical note: that schema is now at **version 8**, and this PRD
> is written against v8 — see the revision below.)*
>
> **Revised again — 88 → 89.** The user **confirmed** chrome icons are theme-controlled and
> that a theme may name a glyph from a bundled set or ship its own image, closing Open
> Question 3. The `icon-constant` widening is now built on a Decision rather than on a
> sibling PRD's reading. Two named provisionals remain — the Phosphor symbol name and the
> resolver's location — which is why this is +1 and not more.
>
> **Revised again — 89 → 95.** Three kinds of change, all of them landing at once:
>
> - **Open Question 1 is closed by the user: narrow P1 formally, and the `analyzer`/AST
>   option is rejected.** Requirement 4 now states what P1 claims and what it defers, and
>   the deferral is tracked against a **trigger** — `P3-01-board-rendering.md` — rather than
>   a wave number. See Open Question 1 for the reasoning, which is load-bearing.
> - **`glyph` is ratified as a third mark `kind`.** `P1-03`'s closed set is
>   `glyph | icon | image`; its Blocking item 6 is closed. `mark-glyph` needs no pattern
>   change and Requirement 6 says why.
> - **Six blocking defects fixed** — a scope contradiction in Requirement 4, a determinate
>   merge deadlock in `opacity-call`, a missing precondition on `font-weight-literal`, an
>   ambiguous `scanSource` contract, an unspecified scanning model, and an unspecified
>   comment/string mechanism. Requirements **15–19** are new and append-only; **1–14 keep
>   their numbers and meanings**, because five sibling PRDs cite them by number.
>
> The remaining 5 is: Open Questions 2 and 4 stay open by design (neither blocks),
> Requirement 6's Phosphor alternative is still unverified against any published API, and
> Requirements 15–19 are `[PRD decision]`s rather than findings from the docs.

**Wave:** P1 · **Slug:** `theme-guard-test`

**Depends on:** `P1-01-app-scaffold.md`, which creates the Flutter project, the `lib/` tree
and the test suite this guard runs in. `P1-01` records that it ships before the rest of its
own wave. Parallel-safe with every other P1 PRD.

**Related:** `P1-03-theme-system.md` Requirement 25 states the rule; this PRD is the check
that enforces it, and `P1-03` Requirement 15 holds the authoritative slot inventory — at
**schemaVersion 8**, whose `icons` section carries **six** slots (`settings`, `close`,
`chevronLeft`, `chevronRight`, `plus`, `trash`) and is what this PRD's `icon-constant` rule
defends. This PRD tracks that inventory rather than restating it.

**Seam with `P2-04-animations.md`.** That PRD's animation layer must construct a `Duration`
**from a theme value** at playback — `Duration(milliseconds: theme.animation.placeMark.durationMs)`
— and its req 13 records the seam from its side, its req 5 forbidding callers from holding
their own timing. Requirement 6's `duration-literal` rule is narrowed to a numeric-literal
argument precisely so that construction is legal. Its req 5's *testable* ("no `Duration`
literal appears in `lib/ui/` outside this layer") implies the layer lives inside this scan
root; that PRD contradicts itself on its own location and is being corrected separately, but
**wherever it lands, this narrowing is what keeps the suite green.** If anyone re-widens the
rule, that PRD goes red on merge with no legal fix.

**Seam with `P1-03-theme-system.md` — two resolutions that must live in `lib/theme/`.**

1. **The icon resolver.** Chrome icons are theme-controlled, so something has to turn an
   `icons.<slot>` with `kind: iconSet` and a `set`/`name` pair into a concrete `IconData`.
   **That resolution must live inside `lib/theme/`.**
2. **The font-weight mapper.** `P1-03` req 15 stores weights as **integers**
   (`type.weights.{regular,medium,semibold}`, `type.scale.<style>.weight`), and Flutter's
   `TextStyle` takes a `FontWeight`. Something must map int → `FontWeight`. **That mapping
   must live inside `lib/theme/` too**, for exactly the same reason — see Requirement 6's
   `font-weight-literal` row.

These are constraints this PRD places on the seam, not requirements it can write for another
PRD. `P1-03` req 5 names **five** files in the theme layer — `theme.dart`, `loader.dart`,
`catalog.dart`, `theme_providers.dart` and `required_keys.dart` — and **none of them is
obviously either resolver's home**, so the constraint is on the *directory*, not on a file:
whichever file ends up holding them, it is under `lib/theme/`.

The consequence if either lands elsewhere is determinate, not hypothetical. `Icons.` or
`PhosphorIcons.` inside the icon resolver, and `FontWeight.` inside the weight mapper, are
exactly what Requirement 6's `icon-constant` and `font-weight-literal` rules catch;
Requirement 3 exempts only `lib/theme/`; Requirement 14 forbids any suppression convention;
Requirement 8 forbids baselining a day-one violation. A resolver in `lib/ui/` is red on merge
with no legal fix — the same shape as the `P2-04` deadlock above, which is why it is worth
stating **before** the code exists rather than discovering it at integration. **The fix in
that event is to move the resolution into the theme layer, never to weaken the rule.**

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
   - `test/support/theme_guard/dart_source_view.dart` — the comment/string lexer
     (Requirement 15).
   - `test/theme_guard_baseline.json` — the baseline (Requirement 11).
   - `test/support/theme_guard/regenerate_baseline.dart` — the regeneration script.

   **The scanner must not live under `lib/`.** Its rule table contains the banned patterns as
   string literals, so a scanner inside the scan root would flag itself on the first run. Under
   `test/` it is outside the root by Requirement 2 and the problem does not arise.

2. **It scans `lib/`, the entry points are parameterized, and scanning is whole-file.** The
   production test scans the glob `lib/**/*.dart` from the src root.
   *Source:* same Decision (*"scans the source under `lib/`"*).

   **[PRD decision]** The scanner exposes two entry points, and **neither hardcodes
   `Directory('lib')`**:
   - `List<Violation> scanSource({required String source, required String path})` — pure, no
     I/O.
   - `List<Violation> scanTree({required Directory root})` — walks the glob and calls
     `scanSource` per file.

   The production test calls `scanTree` with `lib/`. Requirement 13's per-rule tests call
   `scanSource` with inline fixture strings; its one `scanTree` case uses a temporary fixture
   directory. Without this split those tests cannot be written at all, which is the likeliest
   way Requirement 4 quietly goes unmet.

   **`path` is *applied*, not merely reported. [PRD decision, stated because the earlier
   wording said "report" and Requirement 13 requires "apply".]** `scanSource` performs **all**
   path logic against the `path` argument, with no filesystem access:
   - Requirement 3's exemptions — a `path` under `lib/theme/`, or ending `.g.dart` /
     `.freezed.dart`, yields no violations at all.
   - `mark-glyph`'s scoping — that rule only fires when `path` is under `lib/ui/board/`.
   - `icon-constant`'s whole-root applicability, which is the absence of a scope predicate
     rather than the presence of one.

   `scanTree` therefore contains no rule logic of its own: it enumerates files, reads each,
   and delegates. Requirement 13's two `icon-constant` cases and its `mark-glyph` case are
   only expressible because of this, and they are the reason the parameter exists.

   **Matching is whole-file, and line numbers come from an offset→line map. [PRD decision.]**
   The scanner runs each rule's `RegExp` over the whole (masked, per Requirement 15) source
   with `allMatches`, then converts each match's start offset to a 1-based line number by
   binary search over the source's newline offsets. **It does not iterate lines and match each
   one independently.** The reason is not hypothetical: `duration-literal`, `color-hex`,
   `radius-literal` and `opacity-call` all use `\s*` between tokens, and `dart format` routinely
   wraps a long constructor call across lines — so
   ```dart
   Duration(
     milliseconds: 220,
   )
   ```
   is a real violation that a per-line scan silently misses. That is what the formatter
   produces from ordinary code, not an exotic case. Requirement 10's reported line number is
   the line the **match starts on**.

3. **Two exclusions, both by path.**
   - **`lib/theme/` is exempt.** It holds the merged theme object and the YAML loader, so it is
     the one place a literal theme value legitimately appears. It is also **the one place a
     theme's `icons.<slot>` may resolve to a concrete `IconData`, and the one place a
     `type.*.weight` integer may become a `FontWeight`** — see the seam note above and
     Requirement 6's `icon-constant` and `font-weight-literal` rules, which both depend on
     that resolution living here.
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
   `storage/`, `state/`, `navigation/`, `diagnostics/` and `ui/`.

### What the guard is for, and what this deliverable actually reaches

4. **(Scope and reporting statement — *not* an assertable requirement.)** Requirement 4 has no
   testable form and nothing verifies it directly; it bounds what the numbered, checkable
   requirements are allowed to claim, and it is what Requirements 6 and 13 are read against.
   It is left at number 4 rather than renumbered because `P1-03-theme-system.md` req 25 and
   `P3-01-board-rendering.md` both cite "req 4(c)" by number.

   **(a) The rule.** The Architectural Rule enumerates what the theme owns by deriving it from
   what the screens actually consume: colors, backgrounds, fonts, piece styles, sounds and
   animations, **plus** the drawn geometry of a thing itself (grid-line width, grid-line inset,
   mark sizes), corner radii, the type scale, opacities (the locked, claimed and cat-game
   veils), and every named surface — modals, sheets, the settings card, open-game rows and
   their chips, badges, the main-menu logo, and a gradient-capable page background.

   **Spacing and layout numbers are *not* in this list and never were the guard's business.**
   Outer gap, quadrant padding and inner gap are **code constants, not theme values**:
   *"No. Spacing and layout numbers are fixed in the code, not theme-controlled"*
   ([Theming](../Theming.md) → Decisions → Does a theme control spacing and padding?), which
   `P1-03-theme-system.md` req 15's boundary table restates as *fixed in code* against *still
   themed*, and which `P3-01-board-rendering.md` implements as `BoardMetrics`' four
   `static const double`s. An earlier revision of this requirement listed those three among the
   things the rule covers **and** among this deliverable's gaps; both were wrong, and the
   correction matters because reading (a) as licence to add a `padding:` or `width:` rule would
   fail legitimate, already-decided code that Requirement 14 forbids suppressing and
   Requirement 8 forbids baselining.

   *Source:* [Tech Design](../Tech%20Design.md) → Decisions → Do we add a test that fails on
   hardcoded theme values? (*"covering the slot inventory the Architectural Rule names"*);
   [Theming](../Theming.md) → Architectural Rule; [Theming](../Theming.md) → Decisions → What
   the theme's slots are derived from; → Decisions → Does a theme control spacing and padding?
   The authoritative enumeration is `P1-03-theme-system.md` Requirement 15, whose group names —
   **Board and geometry**, **Marks**, **Surfaces and chrome**, **Type**, **Audio**,
   **Animation** — Requirement 6 uses verbatim. At that PRD's **schemaVersion 8** the inventory
   carries an **`icons`** section (`icons.<slot>.{kind,set,name,path,tint,size}`, slots
   `settings`, `close`, `chevronLeft`, `chevronRight`, `plus`, `trash`), and its req 25 states
   that *"an `Icons.*` reference outside the theme layer"* is a theme value that escaped.

   **(b) What ships in P1 — this is now the formal scope, not a snapshot.** The rule set in
   Requirement 6 reaches, and P1 claims, exactly: **colours** (literals and the Flutter
   palette), **durations**, **fonts** (the typeface), **font sizes**, **font weights**,
   **radii** expressed through `BorderRadius`/`Radius`, **opacity** expressed through
   `withOpacity`/`withValues`, **asset paths** including the `audioplayers` form and a theme
   folder referenced from a widget, **marks** in board code, and **chrome icons** anywhere
   outside the theme layer. Requirement 13 requires a committed test per rule.

   **(c) What P1 defers, and the trigger that reopens it.** Deferred: the remaining bare-numeric
   slots — a theme value that reaches code as an unlabelled or non-distinctively-labelled
   number. After (a)'s correction the residue is **three keys, not six values**:
   `board.gridLineWidth`, `board.gridLineInsetPercent`, and the `size` fields on marks and
   icons (`icons.<slot>.size`, and mark size via `type.scale.mark*.size`, which
   `P3-01-board-rendering.md` req 17 treats as the side of the box a mark is laid out in — so
   `font-size-literal` catches it when it reaches code as `fontSize:` and nothing catches it
   when it reaches code as a box side).

   A regex cannot tell `SizedBox(width: 8)` holding a themed value from `SizedBox(width: 8)`
   holding a sanctioned code constant; there is no distinctive constructor to match on the way
   `Color(0x…)` has. **The deferral is tracked against a trigger, not a wave:
   `P3-01-board-rendering.md`** — the first PRD that writes a bare numeric into a painter, the
   first consumer of all three deferred keys, and therefore the first point at which a noisier
   rule could be calibrated against real UI code rather than guessed at. Today
   `src/Tic-Tac-Toe-Extreme/` holds a `README.md` and nothing else, so there is nothing to
   calibrate against at all. `P1-03` req 25 and `P3-01`'s own Open Questions already name
   `board.gridLineWidth` as *"the one deliberate false negative"*; this clause is the other
   half of that agreement.

   **Other known false negatives, listed so they are not mistaken for oversights.**
   - `Opacity(opacity: 0.45, child: …)` — the idiomatic Flutter veil widget. `opacity-call`
     matches `.withOpacity(` / `.withValues(alpha:` and matches this **not at all**. A veil
     drawn this way is invisible to the guard.
   - `Color.fromARGB(…)`, `Color.fromRGBO(…)` and `.withAlpha(115)`. `color-hex` matches only
     the `Color(0x…)` form, so (b)'s claim to cover "colour literals and the Flutter palette"
     is narrower than it sounds.
   - An intermediate variable or arithmetic defeats every labelled-literal rule
     (`final ms = 220; … Duration(milliseconds: ms)`), as Requirement 6's `duration-literal`
     row already records for itself.
   - A path assembled rather than written (`'assets/themes/$name/gear.png'`).
   - A construct split across lines *inside a token* — Requirement 2's whole-file scanning
     removes the wrapped-argument miss, but a rule's own `\s*` gaps are still the only
     flexibility any pattern has.

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
   read as the inventory being covered.** The inventory is covered **as far as P1 claims** —
   (b) is that claim, (c) is what is outstanding, and Open Question 1 records that this
   narrowing is the user's settlement rather than a drafting convenience. This clause exists
   because an earlier draft demanded coverage here that Requirement 6 deferred, and the
   predicted result was a green, well-named guard that met neither.

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
   `P1-03` Requirement 15 slot group it defends. Every pattern runs against the **masked views**
   of Requirement 15 and is matched **whole-file** per Requirement 2.

   - **`color-hex`** — `r'\bColor\(\s*0x[0-9A-Fa-f]{6,8}\s*\)'` — `Color(0xFF00E5FF)`.
     Colour slots, all groups.
   - **`color-palette`** — `r'\bColors\.[A-Za-z]\w*'` — `Colors.red`, `Colors.black87`.
     Colour slots, all groups.
   - **`opacity-call`** —
     `r'\.with(?:Opacity\(\s*[\d._]+\s*\)|Values\(\s*alpha\s*:\s*[\d._]+\s*[,)])'` —
     `.withOpacity(0.45)` and its non-deprecated successor `.withValues(alpha: 0.45)`.
     **Board and geometry** (the locked, claimed and cat-game veil opacities).

     **The argument must be a numeric literal, and this must not be "tightened" back to
     matching the call alone.** The rule id is kept for baseline stability (Requirement 7), but
     it now matches a **literal**, not a call. Matching the call was a determinate deadlock of
     exactly the shape `duration-literal` carries: `P1-03-theme-system.md` req 15 publishes
     `board.gridLineOpacity` and `board.pendingGhostOpacity` as numeric keys, so the **compliant**
     consumer writes
     `theme.color.boardLine.withOpacity(theme.board.gridLineOpacity)` — fully theme-derived,
     necessarily **outside** `lib/theme/`, and under the old pattern matched, unexemptable
     (Requirement 3), unsuppressable (Requirement 14) and unbaselinable (Requirement 8). Red on
     merge with no legal fix, arriving in wave 3 with `P3-01-board-rendering.md`. Requiring a
     literal argument preserves the rule's entire purpose — a typed-in opacity is caught, a
     theme-derived one passes — and is consistent with this requirement's own closing note that
     these rules match a labelled numeric literal and let an expression through.
     **Known false negative:** `Opacity(opacity: 0.45, child: …)` is a different widget and is
     matched by nothing — Requirement 4(c).
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

     **This rule bans *every* `FontWeight.` reference outside the theme layer, and that has a
     precondition — stated here because without it the rule is unsatisfiable.**
     `P1-03-theme-system.md` req 15 stores weights as **integers** (`type.weights.*`,
     `type.scale.<style>.weight`), while Flutter's `TextStyle` takes a `FontWeight`. Something
     must therefore map int → `FontWeight`, and **that mapping must live inside `lib/theme/`**
     — the same precondition, for the same reason, that `icon-constant` places on the icon
     resolver. Note that the pattern also matches the index form `FontWeight.values[…]`
     (`values` is `\w+`), so *"look it up dynamically"* is not an escape either; the escape is
     the directory.

     If the mapping lands in `lib/ui/` it is red on merge with no legal fix — Requirement 3
     exempts only `lib/theme/`, Requirement 14 forbids suppression, Requirement 8 forbids a
     baseline entry. **The fix in that event is to move the mapping, never to weaken the rule**,
     because a `FontWeight.w600` typed into a widget is precisely the escaped type value this
     rule exists to catch. See the seam note at the head of this PRD.
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

     *Source:* [Theming](../Theming.md) → Decisions → **Do themes control the app's chrome
     icons?** — *"**Yes.** The settings gear, close X, chevrons and plus are theme-controlled,
     and a theme may either name a glyph from a bundled icon set or ship its own image."* That
     Decision has **landed**, so this citation is now the doc rather than the two PRDs that were
     carrying it. [Tech Design](../Tech%20Design.md)'s guard table has likewise been corrected
     and now reads *"Hardcoded `'X'`/`'O'` strings and `Icons.*` anywhere outside the theme
     layer"* — the *"inside board widgets"* scoping is gone. Implemented in
     `P1-03-theme-system.md` Requirement 15's `icons` section and stated as a rule by its
     req 25.

     **What this rule's default means, stated because it is the intended behaviour rather than
     an inference:** a hardcoded menu icon **fails the build**. It was invisible to the guard
     before this widening.

     **One provisional, and it is the symbol name, not the rule.** `PhosphorIcons\w*` is written
     as a family match and is **unverified against any published API** — no PRD declares a
     Phosphor package yet, nobody has checked what symbol root the package actually exposes, and
     `phosphor_flutter` has changed its API across versions. It is a placeholder standing in for
     a real symbol, not a considered pattern, and it should not be described as merely
     "provisional": there is no evidence it matches anything.
     `P1-01-app-scaffold.md` Requirement 14's amendment path says *"an icon package, if Phosphor
     ships as one, by whichever PRD lands it,"* and its Open Questions still carries *"Does
     Phosphor ship as a package dependency or as bundled icon art?"*, owned by the first screen
     PRD that draws a chrome icon. So:
     - **If Phosphor ships as a package**, replace the family match with that package's actual
       symbol root once `P1-01` req 14 names it, **verified against that package's own API**.
     - **If Phosphor ships as bundled art**, `PhosphorIcons.*` never appears in source at all,
       the `Icons`/`CupertinoIcons` alternatives carry this rule alone, and `asset-path` carries
       the art. Nothing else changes.

     Either way the rule's substance — Flutter icon constants outside the theme layer are
     violations — is settled. Only the third alternative in the pattern is pending, and until it
     is verified the rule's Phosphor coverage should be assumed to be zero.
   - **`mark-glyph`** — `r'''['"](?:X|O|✕|○|Ø)['"]'''` — a mark drawn as a literal. **Marks**.
     *Scoped to `lib/ui/board/`* — unchanged. Marks are board values, and a bare `'X'` in a menu
     is far more likely to be ordinary text than an escaped theme value.

     **Ratifying `glyph` as a third mark `kind` changes nothing in this rule, and the reason is
     worth stating.** `P1-03-theme-system.md`'s closed set is now confirmed as
     `glyph | icon | image` (its Blocking item 6, closed by the user), so Neon's `✕ ○ Ø` are
     drawn from `marks.<slot>.value` — an **expression**, not a literal — exactly like every
     other compliant read in this PRD. The compliant form
     `Text(theme.marks.playerOne.value, style: …)` produces no violation and the violating form
     `Text('✕')` still does. No pattern change, no scope change.
     **Residual gap the ratification makes visible:** the alternation matches Neon's five
     characters only. A future theme whose glyph is, say, `#` or `▲` would have that character
     typed into board code unmatched. Widening the alternation to "any single-character string
     literal in `lib/ui/board/`" was considered and **not taken** — it would fire on ordinary
     punctuation — so this stays a named false negative under Requirement 4(c) rather than a
     rule change.

   **The `kind: image` half of the `icons` section is in scope this wave, and it is
   `asset-path` that covers it.** A slot may ship an asset path instead of a glyph name — part
   of the landed Decision — so `AssetImage('assets/themes/neon/gear.png')` or
   `Image.asset('assets/…')` written in a widget is the same defect wearing different clothes,
   and because `asset-path` already applies across the whole scan root, it is already caught
   with no new rule required. Stated explicitly rather than left silent, because a silent
   omission reads as coverage. **The residual gap:** a path assembled rather than written
   (`'assets/themes/$name/gear.png'`, or a constant joined at runtime) defeats it, the same
   regex limitation as everywhere else. The compliant form —
   `Image.asset(theme.icons.settings.path)` — correctly produces no violation.

   Note the shape `duration-literal` shares with `opacity-call`, `font-size-literal` and
   `radius-literal`: each matches a **labelled numeric literal** and lets an expression through.
   That is the general form of the escape a caller is meant to use — read the value from the
   theme and pass it — and any rule added later should follow it. The two rules that do *not*
   follow it, `font-weight-literal` and `icon-constant`, are the two that carry a
   **`lib/theme/` precondition** instead; a rule can have one or the other, and a rule with
   neither is the deadlock shape this PRD has now hit three times.

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
   the last three. **The mechanism that produces those two views is Requirement 15**, which is
   where this clause becomes buildable rather than aspirational. **[PRD decision]**

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
   did — leaves entries already keyed on that id matching exactly as before. **Adding a rule is
   not a licence to baseline what it finds:** Requirement 8 governs, so newly surfaced
   violations get fixed. Today the question is moot — the baseline is `{}` and no application
   code exists — which is precisely why the `icons` widening was free to land and would not have
   been later. The same applies to swapping `PhosphorIcons\w*` for a real symbol root once
   `P1-01` names one, and to `opacity-call`'s narrowing in this revision: a **narrowing** can
   only orphan entries, which Requirements 12 and 18 report rather than fail on.

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
    rather than debugs. The line number is the line the match **starts** on (Requirement 2).
    **This format is produced by one named function over one named type, and Requirement 16
    says which** — an earlier revision left this requirement and Requirement 13 naming
    different assertion targets, so read them together.

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
    - **Loading it is Requirement 17**, which says what happens when the file is missing or
      malformed.

12. **[PRD decision] Fewer violations than the baseline passes.** A file whose violations have
    been fixed does not fail; the test prints a note naming the stale entries so they can be
    pruned. Failing on improvement would make the safe direction — deleting a hardcoded value —
    the one that breaks the build. The docs settle only the other direction (Requirement 7), so
    this is a default chosen for safety, and it is reversible. Requirement 18 extends the same
    rule to an entry whose **file** is gone.

13. **[PRD decision] The verification cases ship as committed tests, one per rule in
    Requirement 6.** Each calls `scanSource` (Requirement 2) with an inline fixture string
    holding one representative violation, asserting the **`Violation` fields** (Requirement 16)
    — rule id, reported line number and matched text; and a companion case asserts that the
    compliant form of the same construct produces no violation. Inline strings rather than
    fixture files, so no fixture ever sits inside the scan root and trips the real scan.

    **Three rules carry a mandatory extra case, because for each of them the *negative* is the
    requirement:**
    - **`duration-literal`** —
      `Duration(milliseconds: theme.animation.placeMark.durationMs)` produces **no** violation.
      That case is the regression test for the deadlock described in Requirement 6, and it is
      what makes a later re-widening of the rule fail loudly here instead of silently in
      `P2-04-animations.md`.
    - **`opacity-call`** —
      `theme.color.boardLine.withOpacity(theme.board.gridLineOpacity)` produces **no**
      violation, and `.withValues(alpha: theme.board.pendingGhostOpacity)` likewise. Same
      shape, same reason; without these two, the deadlock B2 describes can be reintroduced by a
      one-character edit and nothing notices until `P3-01` lands.
    - **`font-weight-literal`** — `FontWeight.w600` at a `lib/ui/…` path **is** a violation and
      the same text at a `lib/theme/…` path is **not**, which is the executable form of the
      mapping's `lib/theme/` precondition.

    **`icon-constant` carries two path-dependent cases**, because its whole substance is scope:
    `Icons.settings` at a `lib/ui/menus/…` path **is** a violation, and the same source text at
    a `lib/theme/…` path is **not**. Both are expressible through `scanSource`'s `path`
    parameter without touching the filesystem — which is the reason that parameter exists
    (Requirement 2). The second case is also the regression test for the seam constraint above:
    if the icon resolver is later moved out of `lib/theme/`, that test still passes while the
    real scan goes red, which is the correct signal — the resolver moved, the rule did not.

    **`mark-glyph` carries a path-dependent pair too:** `Text('✕')` at `lib/ui/board/…` is a
    violation; the identical text at `lib/ui/menus/…` is not.

    **One `scanTree` test is mandatory, and it is the only test that touches the filesystem.**
    Every other case above runs on inline strings, so **nothing in them asserts that the tree
    walk finds any file at all** — and a relative glob resolved against the wrong working
    directory yields zero files and a green pass over an untouched `lib/`, which is the failure
    mode this whole feature exists to prevent, reproduced inside the feature itself. The test
    builds a **temporary fixture directory** (created and deleted by the test, never under
    `lib/`) containing exactly three files:

    | Fixture file | Contains | Expected |
    |---|---|---|
    | `ui/menus/settings_row.dart` | `Icons.settings` | **one** violation, `icon-constant` |
    | `engine/state.g.dart` | `Icons.settings` | none — Requirement 3, generated |
    | `theme/icon_resolver.dart` | `Icons.settings` | none — Requirement 3, exempt path |

    The test asserts `scanTree` returns **exactly one** violation and that its path is the
    first file's. Asserting the count rather than "contains" is what makes a zero-file walk
    fail. Requirement 19 governs what happens if one of those files cannot be read.

    Without this requirement, Requirement 4(b) is unverifiable, and the likely outcome is that
    these tests are never written at all.

14. **[PRD decision] The baseline file is the only exception mechanism.** There is no
    `// ignore:` comment convention, no allow-list annotation and no per-line suppression, and
    none may be invented while building this — a suppression convention invented here has to be
    honored forever. If a legitimate literal exists outside `lib/theme/`, it lives in the
    baseline and is visible in review. Whether a real escape hatch *should* exist is Open
    Question 2.

### Mechanism, types and failure modes

> Requirements 15–19 are **appended** and were added in the 89 → 95 revision. Requirements
> 1–14 keep their numbers and meanings; five sibling PRDs cite them by number.

15. **[PRD decision] Comments and strings are separated by a hand-rolled Dart lexer that
    produces two masked views, not by regex.** Requirement 6 requires comment stripping *and*
    per-rule string awareness, and a regex cannot do either reliably — the naive *"drop
    everything after `//`"* turns any line containing `'https://…'` into a dropped line,
    silently, and the naive *"strip anything between quotes"* cannot survive the first
    apostrophe in a comment.

    **The artifact:** `test/support/theme_guard/dart_source_view.dart` exposes

    ```dart
    class DartSourceView {
      DartSourceView(String source);
      final String code;    // same length as source; comments and string interiors blanked
      final String strings; // same length as source; code and comments blanked
    }
    ```

    **Masking, not deletion, is the load-bearing choice.** Each view is the same length as the
    original source, with excluded regions replaced character-for-character by spaces and
    **newlines preserved**. That means a match offset in either view is an offset in the
    original file, so Requirement 2's offset→line mapping works unchanged and no second
    coordinate system exists. Deleting the excluded regions would require a position map and
    would let a rule match across a seam that is not really adjacent.

    **What the lexer must handle**, because each of these is a real Dart form that a naive
    implementation gets wrong:
    - `//` line comments and `///` doc comments, to end of line.
    - `/* … */` block comments, **which nest in Dart** — depth must be counted, not matched.
    - Single- and double-quoted strings, and their triple-quoted `'''` / `"""` forms.
    - Raw strings (`r'…'`, `r"""…"""`), in which `\` is an ordinary character.
    - Backslash escapes in non-raw strings, so `'it\'s'` does not terminate early.
    - Interpolation: `$identifier` stays string; `${ … }` returns to **code** for the
      expression's extent, with brace depth counted, and returns to string after. A
      `theme.color.x.withOpacity(0.5)` inside `${…}` is code and must be caught.
    - Adjacent string literals (`'a' 'b'`), which are two strings with code-classified space
      between them.

    **Rule dispatch:** each rule in Requirement 6 declares which view it runs against — the
    nine code rules against `code`, and `asset-source`, `asset-path` and `mark-glyph` against a
    view that is `strings` **plus** the delimiters, since `asset-source` matches the opening
    quote after `AssetSource(` and needs the code before it. **[PRD decision]** the simplest
    satisfying arrangement is that those three run against the **original, comment-stripped
    source** (`code` ∪ `strings`), which is exactly "everything but comments" — the property
    they actually need.

    **Testable:** the lexer has its own cases, independent of any rule — a `//` comment holding
    `https://` classified entirely as comment; a nested block comment; `'it\'s'`; `r'\n'`;
    `'''…'''` spanning lines; `'${theme.color.a.withOpacity(0.5)}'` with the `withOpacity` call
    classified as **code**; and `'a' 'b'`. Plus one end-to-end case per class: a `Colors.red`
    inside a comment and inside a string is not a violation, an `assets/…` path inside a comment
    is not, and the same path in a real string is.

    **`P1-06-crash-reporting.md` Requirement 16 carries an identical exempt-contexts clause**
    for its transport scan and has the same problem. This artifact would serve both. Flagged as
    an observation only — that PRD's scanner is its own, and nothing here requires it to adopt
    this.

16. **[PRD decision] `Violation` is the data type; the rendered line is a formatter over it, and
    tests assert against the type.** This closes a mismatch between Requirement 10, which
    specifies a rendered line, and Requirement 13, which specifies assertions — an implementer
    reading them in either order had to guess which was the assertion target.

    ```dart
    class Violation {
      final String path;      // relative to the src root
      final int line;         // 1-based, per Requirement 2
      final String ruleId;
      final String match;     // the matched text, per Requirement 7's key
      final String slotGroup; // a P1-03 req 15 group name, per Requirement 6
    }

    String formatViolation(Violation v);   // exactly Requirement 10's line
    String formatReport(List<Violation> v); // the lines plus the footer
    ```

    - **Requirement 13's per-rule tests assert `Violation` fields.** They do not string-match
      the report.
    - **Exactly one test asserts the rendered format**, comparing `formatViolation` against
      Requirement 10's literal example. That keeps the format load-bearing without making every
      rule test brittle to a spacing change.
    - `formatReport`'s footer gives the total and names the regeneration script (Requirement 11).

17. **[PRD decision] A missing or malformed baseline file fails the test loudly; it is never
    treated as `{}`.** Reading `test/theme_guard_baseline.json` has three outcomes:

    | State | Result |
    |---|---|
    | Valid JSON in Requirement 11's shape | scan proceeds |
    | File absent | **fail**, naming the path and saying to commit `{}` or run the regeneration script |
    | Present but unparseable, or not in Requirement 11's shape | **fail**, naming the path and the parse error |

    Silently substituting `{}` would be *stricter* — every violation becomes new — and that is
    exactly why it is the wrong default: a deleted or half-written baseline would present as a
    wall of unrelated failures rather than as the one thing that is actually broken. Failing on
    the file itself puts the real cause in the first line of output. Shape validation is
    structural only — object of arrays of `{rule, match, count}` with the right types — not a
    check that the rule ids still exist, which Requirement 18 covers.

18. **[PRD decision] A baseline entry whose file no longer exists is reported, not failed.**
    Same class as Requirement 12 and the same reasoning: deleting a file that held hardcoded
    values is the safe direction, and a guard that breaks the build for it teaches people to
    stop deleting things. The test prints such entries under the same "stale baseline entries"
    note Requirement 12 produces, grouped by path, so one pass of the regeneration script clears
    both kinds. An entry whose **rule id** no longer exists in Requirement 6's table is reported
    the same way — that is what a rule narrowing or a rename produces.

19. **[PRD decision] A file under `lib/` that cannot be read fails the test.** If `scanTree`
    encounters a `.dart` file it cannot read or decode as UTF-8, it fails naming the path and
    the error, rather than skipping it. **A skipped file is an unscanned file**, and a guard that
    silently declines to look at part of the scan root gives exactly the false assurance
    Requirement 4 spends a page warning about. This is deliberately harsher than Requirements 12
    and 18: those concern the baseline, where the safe direction is to under-report; this
    concerns coverage, where the safe direction is to stop.

## Out of Scope

- **The theme system itself** — the theme object, the slot inventory's implementation, the YAML
  loader, merge-over-Neon, materialization, the `icons` schema, and **where the icon resolver
  and the font-weight mapper live**. See `P1-03-theme-system.md`, whose Requirement 25 is the
  rule this PRD checks. This PRD delivers the guard and states its preconditions on those two
  resolutions' location; it does not specify either.
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
- **A custom analyzer plugin or a lint rule** — and, as of Open Question 1's closure, **an
  `analyzer`/AST-based scanner of any kind**. Explicitly ruled out by the source Decision and,
  for the AST variant, by the user.
- **Spacing and layout numbers.** Outer gap, quadrant padding and inner gap are code constants
  ([Theming](../Theming.md) → Decisions → Does a theme control spacing and padding?), so no rule
  may target `padding:`, `width:`, `height:` or `SizedBox` — a rule that did would fail
  sanctioned code with no legal fix. This is a boundary, not a gap.
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
- **`P1-06-crash-reporting.md`'s transport scan.** Requirement 15 notes the shared
  comment/string problem; sharing the artifact is that PRD's call, not this one's requirement.
- **Anything outside `lib/`** — `test/`, `assets/`, `ios/`, and the read-only
  `design_handoff_game_ui/` bundle are not scanned. The Decision scopes the scan to `lib/`.
- **Haptics and vibration.** Haptics are not theme-driven; they are an app-level setting, so a
  literal haptic value is not a theme value that escaped.
  *Source:* [Theming](../Theming.md) → What a Theme Does NOT Control.

## Open Questions

1. **~~The bare-numeric slots — how far does the P1 guard go?~~ CLOSED — narrow P1 formally.**
   Answered by the user. Retained as a numbered entry rather than renumbered away, because
   Requirement 4 and two sibling PRDs refer to "Open Question 1."

   **The answer: P1 covers colours, durations, fonts, font sizes, font weights, radii, opacity,
   asset paths, marks and chrome icons — Requirement 4(b). The remaining bare-numeric slots are
   deferred until real UI code exists to calibrate against — Requirement 4(c). The
   `analyzer`/AST option is rejected.**

   **Why the AST option was rejected, recorded because the reasoning is load-bearing and not
   obvious from the option as it was written.** That option proposed matching argument
   positions including `padding:` and `width:` under `lib/ui/` — and those are **exactly** the
   positions [Theming](../Theming.md) → Decisions → *Does a theme control spacing and padding?*
   sanctions as code constants rather than theme values: *"No. Spacing and layout numbers are
   fixed in the code, not theme-controlled."* Adopting it would have built a rule whose whole
   claimed advantage — telling a themed gap from an incidental one — is a distinction the docs
   had already made in the other direction, and it would have failed
   `P3-01-board-rendering.md`'s `BoardMetrics` constants on the day they landed, with
   Requirement 14 forbidding suppression and Requirement 8 forbidding a baseline entry. The
   larger build was the smaller objection.

   **Why deferring the rest costs less than it looks.** The gap had already shrunk before the
   question was answered: with spacing and padding out of scope, what remains is
   `board.gridLineWidth`, `board.gridLineInsetPercent` and the `size` fields on marks and icons
   — **three keys, not six values**. `P1-03` req 25 already names `board.gridLineWidth` as *"the
   one deliberate false negative"* it accepts.

   **The trigger, recorded instead of a wave number.** `P3-01-board-rendering.md` is where the
   first bare numeric gets written into a painter and the first place a noisier rule could be
   calibrated against real code. Today `src/Tic-Tac-Toe-Extreme/` contains a `README.md` and a
   `.git` directory — there is no UI code in existence to calibrate against, which is the
   substantive reason the deferral is not merely a scheduling preference.

2. *(Raised by this PRD.)* **Should a real escape hatch exist?** Requirement 14 makes the
   baseline the only exception mechanism, which is the safe default but not obviously the right
   long-term answer.

   **Neither example this question was originally written around is live, and saying so is not
   the same as closing the question.** Both were named before the PRDs that own them existed:
   - *A pre-theme bootstrap colour in `main.dart`.* Not required. `P1-01-app-scaffold.md`
     Requirement 11 keeps `main.dart` to binding init, the orientation lock and one `runApp`
     call — *"No UI and no business logic"* — and `app.dart` **omits `theme:` entirely**, naming
     it as the extension point `P1-03` supplies. There is no pre-theme paint to colour.
   - *A crash-report fallback.* Not required. `P1-06-crash-reporting.md` Requirement 8 leaves
     `ErrorWidget.builder` **at the framework default and does not override it**, with *"No
     dialog, banner, snackbar, toast, sound, haptic, navigation or theme change"* resulting from
     a caught error; its Requirement 15 states that `lib/diagnostics/` *"has no colors, fonts,
     durations, icons or asset paths"* and must stay that way for the day-one-zero baseline.

   **The real trigger, named so the question has something to watch rather than two dead
   examples:** `P1-06-crash-reporting.md` **Open Question 7** — *"Should a caught error ever be
   visible to the player?"* — which that PRD fences to "no" as a default the user can overturn.
   If it is overturned, an error surface has to render **before or without** a working theme,
   and that is the first genuine instance of the case this question is about. **Left open.**

3. **~~Are chrome icons theme values?~~ CLOSED — confirmed, both halves.** Retained as a
   numbered entry rather than renumbered away, because earlier revisions of this PRD and its
   siblings refer to "Open Question 3."

   **The answer: chrome icons are theme-controlled, and a theme may either name a glyph from a
   bundled icon set or ship its own image.** Both halves of `P1-03-theme-system.md`'s Blocking
   item 9 are confirmed. Consequences, all landed in this PRD:
   - `icon-constant` applies across the whole scan root with `lib/theme/` permitted
     (Requirement 6). A hardcoded menu icon fails the build — intended, not inferred.
   - The `kind: image` escape is covered by `asset-path` (Requirement 6).
   - The resolver must live in `lib/theme/` (seam note above).

   **Both follow-ups are now done.** [Theming](../Theming.md) → Decisions → *Do themes control
   the app's chrome icons?* has landed, and Requirement 6's `icon-constant` citation is
   re-pointed at it. [Tech Design](../Tech%20Design.md)'s guard table has had its *"inside board
   widgets"* scoping corrected and now reads *"`Icons.*` anywhere outside the theme layer"*.
   Nothing is outstanding against this item.

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

   **`opacity-call`'s narrowing in Requirement 6 gives this question a second instance**: an
   opacity that is not a theme value — a debug overlay, a disabled-control convention — is a
   violation for the same reason and escapes the same way.

5. **Theme files that misspell a key are not guarded.** Stated as
   [Tech Design](../Tech%20Design.md) → Open Questions → 2. Theme loading:

   > What happens to an unknown or misspelled *key* inside an otherwise-valid theme file?
   > Merge-over-Neon will quietly fill the gap with Neon's value, so a typo in a theme file
   > fails silently. The hardcoded-theme-value test guards code that bypasses the theme; it
   > does not guard a theme file that misspells a key.

   Left open. This PRD does not extend the guard to cover it.
