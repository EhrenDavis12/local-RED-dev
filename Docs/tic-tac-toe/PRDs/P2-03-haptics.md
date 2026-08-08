**Build-readiness: 84**

# PRD: Haptics

> **Status:** Draft · Source docs read: `Game Board Design.md`, `Menus and UI.md`,
> `Theming.md`, `Tech Design.md`, `Animations.md`, `Game Overview.md`, `Rules.md`,
> `roadmap.md`, plus the read-only reference asset `design_handoff_game_ui/README.md`
> (→ *Interactions & behavior*, *1f — Modal: in-game settings*, *2b — Settings page*,
> *2d — Board, pending move*). `Alternative Game Styles.md` is a declared parking-lot doc
> and was read only to confirm it is out of scope — no requirement here comes from it.
>
> **What remains open, and with whom:** one value — the concrete haptic call — is
> **proposed for ratification** at the top of this document, so the PRD executes the moment
> it is confirmed. Genuinely with the user: what happens on a device with no haptic engine
> (OQ-3 — **answering it changes the published interface, not one line**), whether non-tap
> game events buzz (OQ-4b), and the vibrate-off no-signal case (OQ-5). Carrying a **fenced
> default** rather than a question: tap-outside-to-clear does not buzz (OQ-4a).
> **Closed:** the scope of the rule — it is **app-wide** (OQ-2), the vibrate value and its
> publisher (OQ-7), who asserts requirement 3 (OQ-8), and the `lib/` layer this lives in
> (OQ-6).
>
> **There are four settings toggles, not three** — Music, Sound Effects, Vibrate on Touch,
> Animations (`Theming.md` → Decisions → *Do all four toggles ship, and is music a theme
> concern?*; `Menus and UI.md` → Settings Menu). **Nothing in this layer changes:**
> `vibrateOnTouchEnabledProvider` is unaffected, music is a theme concern and not a haptics
> one, and the only edits here are counts — requirement 11's citation, requirement 14's test
> comment, requirement 15's stub, and OQ-7.

**Wave:** P2 · **File:** `P2-03-haptics.md` — parallel-safe with the other P2 PRDs.

**Dependencies:**

- `P1-01-app-scaffold.md` — creates the `lib/` tree (its req 2), the `ProviderScope` (its
  req 11) and the Riverpod idiom this layer's provider uses (its req 12), and owns the
  **exhaustive** dependency table (its req 14) that requirement 16 below declares unchanged.
  Requirement 19 below pins the one thing that table leaves free and this PRD's tests need.
- `P1-04-persistence.md` — owns the vibrate-on-touch preference end to end:
  - **req 26** declares `vibrateOnTouchEnabledProvider`, a plain `Provider<bool>` over
    `settingsProvider`, resolving "nothing stored" to `true`. This is the symbol requirement
    14 codes against, and the only thing the buzz is gated on.
  - **req 27** guarantees it is current — seeded once off the tap path, and updated by
    `SettingsNotifier`'s setters *before* the write completes. That PRD states the
    consequence directly: *"This is what makes `P2-03` req 12 hold."*
  - **req 28** declares `preferencesRepositoryProvider` in
    `lib/storage/storage_providers.dart`. **Every test in this PRD that resolves
    `hapticServiceProvider` must override it** — see requirements 8 and 14.
  - **req 21** publishes the `PreferencesRepository` interface — **five reads and five
    writes**, one pair per preference (theme, music, sound effects, vibrate on touch,
    animations). This layer calls none of them; requirement 15's stub implements all ten.
- `P1-03-theme-system.md` — req 29 states the theme object has no haptics slot; requirement 7
  below is the behavioral half of that boundary. Its **req 24** publishes `activeThemeProvider`,
  `themeCatalogProvider` and `activeThemeIdProvider` in `lib/theme/theme_providers.dart`,
  which requirement 8 asserts against. It ships **Neon only** — Classic Red vs Blue is
  `P5-01-classic-theme.md`, wave 5.
- `P1-06-crash-reporting.md` — its req 2 installs `PlatformDispatcher.instance.onError`, which
  is what makes requirement 14's handling of the platform-channel future a decision rather
  than a detail.

> **The toggle is a persisted preference, not a settings-screen behavior.** This PRD reads
> the value through `P1-04-persistence.md`. `P4-04-settings.md` draws the switch and owns no
> part of what "off" means — so it is a wave-4 consumer of this feature, not a dependency of
> it.

**Depended on by:**

- `P3-02-move-input.md` — owns the two-tap select-then-confirm gesture and what counts as a
  legal cell, and calls `HapticService.validAction()` on each valid tap. Requirement 15
  closed that PRD's OQ-8 on the haptics side; its req 14 carries the call-site counts,
  including the reselection assertion this PRD's requirement 3 needed, and imports the fake
  named in requirement 15.
- `P3-01-board-rendering.md` — owns the locked/dimmed quadrant styling constrained by the
  *Design notes* section below. This PRD specifies no visuals.
- **The non-board callers, settled rather than provisional** (see OQ-2):
  `P3-04-game-over-rematch.md` req 15 (Rematch), `P4-03-theme-selection.md` req 18 (selecting
  a theme), `P3-03-scoreboard-turn-indicator.md` req 12 (the in-game settings gear) and
  `P4-01-main-menu.md` req 24 (all four menu buttons) all fire this layer, ratified by
  `Game Board Design.md` → Decisions → *Does the haptic fire on non-board controls?*
- `P4-04-settings.md` req 8 owns the *switch* for vibrate on touch and none of the behavior
  behind it. Its own controls buzz like any others, per the same Decision.

**A wording trap two callers have already hit, recorded so the next one does not.** A
call-site requirement phrased *"invokes `playGame()` exactly once and nothing else"* reads as
forbidding the buzz. `P4-01-main-menu.md` (reqs 14–16) and `P3-03-scoreboard-turn-indicator.md`
(req 12) both narrowed to *"no other **navigation** operation"*. The haptic is not an
alternative to the action; it accompanies it.

**Callers land in later waves, deliberately not blocking:** the deliverable of this wave is
the haptic layer, its gate and its provider — requirements 13–19 — not any screen that calls
it. Requirements 1–6 state rules whose natural assertion is a call-site interaction and run
when those screens land; each carries a *wave note* naming what is assertable here and which
PRD owns the rest. Everything under *The published interface* is fully assertable in this
wave, with no screen present.

**Note on source status:** `Game Board Design.md` carries the house banner *"Nothing here is
settled"*, and its `## Decisions` section now covers the scope question (OQ-2) though not the
Haptic Rule itself. That rule is treated as settled because it is stated as a rule in that
doc, restated in `Menus and UI.md` → Settings Menu (*"Fires on every valid click"*), listed in
`Tech Design.md` → What the Design Docs Already Imply as *"already locked by decisions made
elsewhere"*, and drawn into the approved handoff. Nothing here comes from a single
unsupported mention.

## Pending confirmation — one value, not a design

It is needed before a line of this can run, and it is not guessable without committing the
app to the guess. It carries a proposal, following `P1-01-app-scaffold.md` → *Pending
confirmation* and `P1-04-persistence.md` req 25, so this PRD is executable the moment it is
confirmed. It changes nothing else in this document.

**Which concrete haptic the "small, subtle buzz" is.** An implementer must emit exactly one
call, and no fence substitutes for it. **Proposed: `HapticFeedback.selectionClick()`** from
`package:flutter/services.dart`. Reasoning, all from requirement 6's sources: it is the
lightest thing the Flutter surface offers and the only one whose name and platform meaning
are *"a selection changed"* — which is what `Menus and UI.md` → Vibrate on Touch asks for,
*"enough to confirm 'you selected that,' nothing more."* The impact family (`lightImpact` /
`mediumImpact` / `heavyImpact`) carries a collision metaphor, and `vibrate()` is the rumble
that same section rules out. Stated in executable form as requirement 18; recorded as
unsettled at OQ-1.

## Problem

The board has 81 tap targets on a phone, each roughly 35pt — under Apple's 44pt guidance
(`Game Board Design.md` → Responsive / Screen Size). A tap that lands slightly off, or on one
of the eight quadrants the player is not allowed to play in, leaves them asking *"did that
register?"* and hunting the screen for a change (`Menus and UI.md` → Vibrate on Touch).

The docs answer that with feedback the player feels rather than reads, and they answer it
without an error state: nothing shakes, flashes, or tells the player off. That only works if
the rule holds everywhere and without exception — a buzz that fires on an illegal tap, or
fails to fire on a legal one, inverts the signal and makes the board less trustworthy than
having no haptic at all. Today no such rule is implemented anywhere, and six PRDs across
three waves call into a layer that has no name, no signature, and no seam a test can hold.

## Goal

**While vibrate on touch is on**, every valid click anywhere in the app produces one small,
subtle buzz, and nothing else ever does. That single rule is the app's validity signal — *a
buzz means "that registered," no buzz means "that did nothing"* — so an illegal tap needs no
error message, no shake and no flash to explain itself. The buzz is gated only by that
setting, lives at the application-setting level, is identical under every theme, and reaches
its callers through one named, injectable entry point that owns the gate.

Two conditions on that sentence, stated rather than smoothed over:

- **With the setting off there is no validity signal at all.** Requirement 5 and the
  *Design notes* forbid any substitute, so a legal tap and an illegal tap become
  indistinguishable to a player who is not watching the screen. That follows from the docs;
  whether it is the intended outcome is with the user — see OQ-5.
- **One value is proposed, not decided** — the concrete haptic call. See *Pending
  confirmation*.

The scope question that stood here through three revisions is closed: the rule is **app-wide**
(OQ-2). OQ-4a records a smaller, still-fenced instance of the same shape.

## Requirements

### When the haptic fires

1. **The haptic fires on every valid click, anywhere in the app.** Any valid selection or
   valid action produces exactly one haptic event — board cells, menu buttons, theme rows,
   settings toggles, the game-over card's controls and the settings gear alike.
   *Source: `Game Board Design.md` → Haptic Rule ("The haptic fires on every valid click.
   Any valid selection or valid action buzzes"); → **Decisions → Does the haptic fire on
   non-board controls?** ("**Yes — every valid tap buzzes, anywhere in the app.**");
   `Menus and UI.md` → Settings Menu ("Fires on every *valid* click");
   `design_handoff_game_ui/README.md` → Interactions & behavior ("Haptic on every valid
   tap").*
   *Testable:* **with vibrate on touch on**, each valid action fires the haptic exactly once
   — never zero times, never twice for one action. Requirement 10 is the gate on this and on
   every requirement in this section; "never zero times" is false with the setting off, by
   design.
   *Wave note:* assertable here as *one call to `validAction()` produces at most one platform
   message, never two* (requirement 15 names the message). That a valid **tap** reaches
   `validAction()` exactly once is a call-site fact, owned by each calling PRD —
   `P3-02-move-input.md` req 14 for the board, and reqs 15 / 18 / 12 / 24 of `P3-04`,
   `P4-03`, `P3-03` and `P4-01` for the non-board controls.

2. **The first tap of a two-tap move fires it**, because selecting a legal cell is itself a
   valid action. The confirming second tap, being a valid action too, fires it as well.
   *Source: `Game Board Design.md` → Haptic Rule ("including the first tap of a two-tap
   move, since selecting a legal cell is a valid action"); `design_handoff_game_ui/README.md`
   → *2d — Board, pending move* ("No sound fires on selection (docs). The haptic **does**
   fire — selecting a legal cell is a valid action").*
   *Testable:* a select-then-confirm sequence on a legal cell fires two haptic events, one
   per tap. Note this differs from sound, which fires only on the confirmed move
   (`Game Board Design.md` → Move Input → Sound) — the two channels are not interchangeable.
   *Wave note:* a board interaction, asserted by `P3-02-move-input.md` req 14's counts
   (legal first tap → 1, confirming tap → 3) in wave 3.

3. **Re-selecting a different legal cell fires it**, since that is a valid selection.
   *Source: `Game Board Design.md` → Haptic Rule (any valid selection); → Move Input →
   Changing your mind ("Tap a different cell → that cell becomes the new selection").*
   *Testable:* tapping legal cell A then legal cell B fires two haptic events and leaves one
   pending selection.
   *Wave note:* **now asserted**, by `P3-02-move-input.md` req 14: "tap on a different legal
   cell → 2", against the fake named in requirement 15 — see OQ-8. **This requirement and
   requirement 2 are board instances of requirement 1, not the whole of it:** since
   `Game Board Design.md` → Decisions → *Does the haptic fire on non-board controls?* settles
   the rule as app-wide, the board is where the two-tap shape makes it most visible, not where
   it stops. Non-board controls are asserted by their own PRDs.

### When it does not

4. **An illegal tap does nothing.** No shake, no flash, no error message — and no buzz. This
   covers any tap the app does not accept, including taps on cells inside a locked, claimed
   or cat-game quadrant.
   *Source: `Game Board Design.md` → Active Quadrant Highlight → Taps outside the legal
   quadrant ("**An illegal tap does nothing.** No shake, no flash, no error message — and,
   per the haptic rule, **no buzz**"); → Decisions → Does the haptic fire on non-board
   controls? (which widens *where* the rule applies and explicitly leaves this half
   unchanged: "an illegal board tap remains silent, which is the existing rule and is
   unchanged"); `design_handoff_game_ui/README.md` → Interactions & behavior.*
   *Testable:* tapping every cell of every non-legal quadrant produces zero haptic events,
   zero state changes, and no visible error affordance of any kind.
   *Wave note:* a board interaction; owned by `P3-02-move-input.md` reqs 10 and 14 ("tap on
   any illegal cell → still 3"), wave 3. The half this layer holds is structural and is
   assertable here: `HapticService` exposes **no** member an illegal tap could call —
   requirement 14's interface has exactly one, and it means *a valid action happened*.

5. **No error state exists for invalid input anywhere in this feature.** The absence of the
   buzz is the feedback; nothing is added to explain, warn about, or scold an invalid tap —
   not a toast, not a message, not a substitute effect. This holds regardless of the vibrate
   setting: nothing appears to compensate when the buzz is off.
   *Source: `Game Board Design.md` → Haptic Rule ("The player doesn't need an error state —
   the *absence* of feedback is the feedback. Nothing scolds them; invalid taps just quietly
   don't happen"); → Taps outside the legal quadrant ("The lack of a buzz *is* the
   feedback").*
   *Testable — the bounded half, stated mechanically so it is decidable by a scan over
   `lib/haptics/` as a whole, however many files it holds:* `HapticService` has exactly one
   member and it returns `void`, declaring no error type and no result type; and the
   directory contains **no `Text(`, `SnackBar`, `showDialog(`, `showModalBottomSheet(`,
   `Semantics(`, `debugPrint(` or `log(`**, **no `throw` and no `Exception`/`Error` subclass
   declaration**, and **no string literal in any code position** — with two exclusions, both
   mechanical: doc comments (`///`), which are not code, and **URIs in `import` / `export`
   directives**, which are not user-facing by construction. Those exclusions are what make
   "no user-facing string" decidable without a judgement call.
   *Stated as a property, not a count:* the only string literals anywhere under
   `lib/haptics/` are import URIs, and requirement 16 bounds which packages those may name.
   Requirement 14 ships the layer as a single file today, so that is four URIs — but the scan
   asserts the property, not the number, and splitting the file changes nothing.
   *Note, since it constrains a later decision:* "exactly one member returning `void`" is
   also what makes OQ-3 an interface change rather than a line change — see requirement 14's
   closing note and OQ-3.
   *Wave note:* that no *screen* adds an error affordance is `P3-02-move-input.md` req 10's
   and `P3-01-board-rendering.md`'s, in wave 3.
   *Prose, deliberately not a test:* with vibrate **on**, the pair reads as a biconditional —
   for any tap, either it was valid and buzzed, or it did nothing and produced no output on
   any channel. That form is not written as an assertion: it is a universally quantified
   negative over every channel in the app, no single PRD can hold it, and with vibrate
   **off** it is simply false, because requirement 10 removes the buzz from valid taps too.
   A test asserting it unconditionally would fail on that path and should not be written.
   *Consequence, recorded not hidden:* with vibrate off, a valid tap and an invalid tap
   produce the same nothing on this channel, and this requirement plus the *Design notes*
   forbid any substitute — so the app has no validity signal at all in that mode. Whether
   that is intended is the user's call — see OQ-5.

### What it feels like

6. **The buzz is small and subtle** — one discrete confirmation that "you selected that,"
   nothing more. Deliberately not a rumble: no sustained, repeating or escalating vibration,
   and no distinct haptic per action type. The Decision that widened the rule to non-board
   controls changed *where* it fires, not *what* it feels like: the settings gear and a board
   cell produce the same single buzz.
   *Source: `Menus and UI.md` → Settings Menu → Vibrate on Touch ("A **small, subtle buzz**
   … enough to confirm 'you selected that,' nothing more … Deliberately subtle. Not a
   rumble"); `design_handoff_game_ui/README.md` → *1f* ("A little buzz on every valid tap").*
   *Testable:* a source scan of `lib/` finds exactly one `HapticFeedback.` call site, and no
   `vibrate(`, no loop and no timer around it; in this layer's own test, one `validAction()`
   with the gate open records exactly one platform message on the channel requirement 15
   names.
   *Wave note:* fully assertable in this wave — it is a property of requirement 14's
   implementation, not of any screen. "No distinct haptic per action type" is enforced
   structurally: `validAction()` takes no argument, so no caller can ask for a different one.
   Which concrete call it is, is requirement 18 and OQ-1.

### Where it lives

7. **Haptics are not theme-driven.** Vibration lives at the application-setting level; a
   theme cannot define or change the buzz, and the theme object carries no haptics slot.
   *Source: `Theming.md` → What a Theme Does NOT Control ("Haptics are **not** theme-driven.
   Vibration lives at the **application setting level** … a theme cannot define or change the
   buzz"); `P1-03-theme-system.md` req 29; `design_handoff_game_ui/README.md` →
   Interactions & behavior ("Haptics are an app setting, never theme-driven").*
   *Unaffected by music becoming a theme concern:* `Theming.md` → Decisions → *Do all four
   toggles ship, and is music a theme concern?* adds a channel to the theme; it does not move
   haptics into it. The boundary table still reads ❌ for vibration.
   *Testable:* no theme file contains a haptic key, and `lib/haptics/` imports nothing from
   `lib/theme/`. Consistent with `P1-05-theme-guard-test.md`, a literal haptic value in
   source is **not** a theme-guard violation.

8. **It is a single app-level behavior, identical under every theme.** The same valid action
   produces the same buzz under any theme, now or later.
   *Source: `Theming.md` → What a Theme Does NOT Control ("It's a single app-level behavior,
   the same under every theme"); → the theme-boundary table (Haptics / vibration: ❌ No — app
   setting).*
   *Testable, wave 2 — the structural form, which is the normative one.* Both overrides and
   both assertions below are required:

    ```dart
    final container = ProviderContainer(overrides: [
      // Required: resolving hapticServiceProvider builds settingsProvider, whose
      // build() fires unawaited(_seed()) → ref.read(preferencesRepositoryProvider).
      // Without this override that read hits an unimplemented provider (or real
      // shared_preferences with no binding) and, being unawaited, surfaces as an
      // unhandled async error that fails the test. No theme override is needed —
      // the point is that none is reached.
      preferencesRepositoryProvider.overrideWithValue(_NullPreferencesRepository()),
    ]);
    container.read(hapticServiceProvider).validAction();

    final origins = container
        .getAllProviderElements()
        .map((e) => e.origin)        // .origin, not .provider — see below
        .toSet();

    // Positive control — proves the graph was actually built.
    expect(origins, contains(vibrateOnTouchEnabledProvider));
    // The property under test.
    expect(origins, isNot(contains(activeThemeProvider)));
    expect(origins, isNot(contains(themeCatalogProvider)));
    expect(origins, isNot(contains(activeThemeIdProvider)));
    ```

    **`.origin`, not `.provider`.** `activeThemeIdProvider` is a `NotifierProvider`, so a
    dependency taken as `activeThemeIdProvider.notifier` produces an element whose `provider`
    is the sub-provider and whose `origin` is the parent — comparing `provider` would let
    exactly that case slip the check. `settingsProvider` has the same shape, which is why the
    positive control reads `vibrateOnTouchEnabledProvider` (a plain `Provider`) rather than
    the notifier.
    **Why an element walk and not "reading it does not throw":** the latter passes even if the
    layer *does* depend on a theme, so it tests nothing. The walk tests the stated property —
    this layer never reaches the theme at all, so no theme can change what it does. The
    positive control is what stops the three negatives passing vacuously on a graph that was
    never built.
    **This assertion depends on the Riverpod major pinned by requirement 19**, because
    container introspection is not stable across majors. If that pin ever moves and
    `getAllProviderElements()` is unavailable, the sanctioned fallback is requirement 7's
    import scan — `lib/haptics/` imports nothing from `lib/theme/` — which is weaker but
    always available. Do not substitute a "does not throw" check.
    *Not asserted, and why:* the behavioral form — override `activeThemeProvider` with two
    different themes and compare the emitted message — is **not constructible in wave 2**.
    `P1-03` ships Neon only (Classic is `P5-01`, wave 5), its req 24 routes every read through
    the published providers rather than a constructor, and it publishes **no test fixture** for
    building a second `Theme`. The structural assertion stands in and is strictly stronger:
    it rules out theme dependence for *all* themes rather than sampling two. If `P1-03` ever
    publishes a fixture helper, the two-theme version is a free addition — worth raising with
    that PRD, not resolving here.

9. **Moved to *Design notes*.** This number held the locked/dimmed-styling constraint. Its
   own testable conceded it is not tested here, so it is now recorded below as a constraint
   on judgment rather than a deliverable, following `P1-01-app-scaffold.md` → *Design notes*.
   The number is retained and not reused so that requirement references in sibling PRDs do
   not shift.

### The setting that gates it

10. **All haptics are gated on the vibrate-on-touch setting.** With it off, no valid action
    anywhere in the app fires a haptic; with it on, requirement 1 holds.
    *Source: `Game Board Design.md` → Haptic Rule ("Subject to the vibrate-on-touch setting
    being on"); `Menus and UI.md` → Settings Menu ("**Vibrate on touch** — Haptic feedback on
    tap. Fires on every *valid* click. On/off").*
    *Testable:* with a `VibrateOnTouchSource` returning `false`, `validAction()` emits zero
    platform messages on the channel requirement 15 names; returning `true`, exactly one.
    "Anywhere in the app" is now a settled scope rather than a bounded one (OQ-2), and
    requirement 13 is what makes it enforceable rather than a promise about future callers.
    *Wave note:* fully assertable in this wave. The call-site half — that a real control fires
    nothing with the setting off — belongs to each calling PRD.

11. **The setting is a global player setting, not a theme property**, and its stored value is
    what governs — this feature reads it and never owns, defaults or writes it.
    *Source: `Menus and UI.md` → Settings Menu ("All four are **global**,
    **player-controlled**, and **not theme-defined** — a theme can't override them");
    → Persistence (the vibrate toggle is remembered between sessions);
    `P1-04-persistence.md` reqs 26–27 (owner of the resolved value and its only writer).*
    *Testable:* `lib/haptics/` contains no default literal for the setting, no `bool`
    constant, and no call to any `PreferencesRepository` method or `SettingsNotifier` setter;
    the only way the layer learns the value is the `VibrateOnTouchSource` handed to it.
    *Where the first-launch value is decided, since it is not decided here:*
    `readVibrateOnTouchEnabled()` returns `Future<bool?>`, and `P1-04` req 21 states that
    every read returns `null` rather than a default because **defaults belong to the
    consuming layer**. This layer is barred from being that consuming layer, and it does not
    have to be: `P1-04` req 26 resolves the `null` to **`true`** inside `Settings.defaults`,
    per `Menus and UI.md` → Decisions → *What are the settings on a fresh install?* (**all
    four toggles default to on** — music, sound effects, vibrate on touch, animations), in
    one place for all four.

12. **A mid-game change to the setting governs the next tap.** The vibrate toggle is offered
    inside in-game quick actions, so its current value — not a value captured at app or game
    start — decides whether the next valid action buzzes. The mechanism, and this
    requirement's wave-2 assertable form, are requirement 17.
    *Source: `Menus and UI.md` → How you reach settings from gameplay → Quick actions
    contents ("The sound effects and vibrate toggles"); → Settings Menu ("settings must be
    available mid-game"); `design_handoff_game_ui/README.md` → *1f* (the vibrate row is in
    the in-game sheet).*
    *Satisfied by:* `P1-04-persistence.md` req 27, whose setters update `state` before the
    write completes and which states the consequence itself — *"This is what makes `P2-03`
    req 12 hold."*
    *Wave note:* the sheet itself is `P4-04-settings.md`'s and lands in wave 4; this
    requirement constrains how this layer reads the value, not when the sheet exists.

### The published interface

> Six PRDs across three waves call into this layer. Everything in this section is normative:
> these are the names and signatures they may code against. The **names** are an engineering
> call, not a doc citation — no design doc names an API; the docs settle meaning, not
> signatures. The **mechanism** is fixed by `Tech Design.md` → Decisions → State management —
> Riverpod and by `P1-01-app-scaffold.md` reqs 11–12 (plain providers, no `@riverpod`
> codegen, no legacy `StateNotifier`). The symbols this section uses but does not define —
> `vibrateOnTouchEnabledProvider`, `settingsProvider`, `SettingsNotifier`,
> `preferencesRepositoryProvider`, `PreferencesRepository`, `activeThemeProvider`,
> `themeCatalogProvider`, `activeThemeIdProvider` — are declared by `P1-04-persistence.md`
> reqs 21, 26 and 28 and `P1-03-theme-system.md` req 24. Nothing below is a forward reference
> to something unwritten, and everything this PRD invents is in requirement 15's table.

13. **One haptic layer, and the gate lives inside it.** Every haptic in the app goes through
    a single app-level entry point. That entry point reads the vibrate-on-touch preference
    itself and fires or stays silent accordingly, so a call site invokes it unconditionally
    on a valid action and never consults the setting. No call site holds its own gate, and no
    code path fires a platform haptic without going through the layer.
    *(**Derived, not stated** — no design doc names a haptic layer. It is the shape the cited
    requirements force: `Theming.md` → What a Theme Does NOT Control calls haptics "a single
    app-level behavior, the same under every theme" (requirement 8); requirement 10 has to
    hold for "no valid action **anywhere in the app**" — which `Game Board Design.md` →
    Decisions → *Does the haptic fire on non-board controls?* has now made literal; and
    requirement 12 requires the value to be read at fire time rather than captured. The
    alternative shape — an ungated fire that each call site gates for itself — makes
    requirement 10 depend on every future caller remembering, and a caller that forgets breaks
    it invisibly. That risk grew with the Decision, which multiplied the call sites. This
    mirrors `P2-02-audio.md` req 2, which takes the same shape for sound.)*
    *Testable:* a call site that invokes the layer unconditionally produces one platform
    message with the setting on and zero with it off, without the call site reading the
    preference; a source scan finds no `HapticFeedback.` call and no platform-channel haptic
    invocation anywhere in `lib/` outside `lib/haptics/`.

14. **The public surface is named, and these are the names.**

    ```dart
    // lib/haptics/haptic_service.dart
    // (lib/haptics/ is in Tech Design → Decisions → Project structure — layer-first.)

    import 'dart:async';                           // unawaited — requirement 16
    import 'package:flutter/services.dart';        // HapticFeedback, PlatformException
    import 'package:flutter_riverpod/flutter_riverpod.dart';

    // vibrateOnTouchEnabledProvider — Provider<bool>, declared by
    // P1-04-persistence.md requirement 26. It resolves the stored null to true.
    import '../state/settings_providers.dart';

    /// A synchronously readable snapshot of the vibrate-on-touch preference.
    /// Read on every fire and never captured — requirement 17.
    /// This layer reads it and never owns, defaults or writes it — requirement 11.
    typedef VibrateOnTouchSource = bool Function();

    /// The single entry point for every haptic in the app — requirement 13.
    abstract interface class HapticService {
      /// One buzz for one valid selection or valid action.
      /// Silent when vibrate-on-touch is off; callers never check the setting.
      /// Returns immediately: the platform call is never awaited, and a
      /// PlatformException or MissingPluginException from it is swallowed.
      /// Any other rejection propagates, and reading the preference source is
      /// not guarded at all — see "What 'never throws' covers" below.
      void validAction();
    }

    final class PlatformHapticService implements HapticService {
      const PlatformHapticService(this.vibrateOnTouch);

      final VibrateOnTouchSource vibrateOnTouch;

      @override
      void validAction() {
        if (!vibrateOnTouch()) return;
        unawaited(
          HapticFeedback.selectionClick().catchError(
            (Object _) {},
            test: (Object e) => e is PlatformException || e is MissingPluginException,
          ),
        );
      }
    }

    /// The single read point. Every caller resolves the service through this and
    /// constructs none of its own. Overridable in tests — requirement 15.
    ///
    /// `ref.read` inside the closure, never `ref.watch` — see below.
    final hapticServiceProvider = Provider<HapticService>(
      (ref) => PlatformHapticService(() => ref.read(vibrateOnTouchEnabledProvider)),
    );
    ```

    **Why the platform future is caught at all, stated accurately.**
    `HapticFeedback.selectionClick()` returns `Future<void>` over `SystemChannels.platform`,
    which is implemented by the **Flutter engine itself, not by a plugin** — so
    `MissingPluginException` there is effectively unreachable on a real device, and on the
    iPad that OQ-3 is about **the call succeeds and does nothing**. The catch is therefore
    *not* a device-capability fence and must not be read as one; an earlier revision of this
    PRD claimed it was, and that claim was wrong. It is here because a bare call makes a
    rejection — from a future platform port, an engine change, or a test harness — an
    **unhandled async error**, which `P1-06-crash-reporting.md` req 2 routes to
    `PlatformDispatcher.instance.onError` and turns into a `CrashReport`. Catching costs one
    line and keeps this layer inside `P1-06` req 1's scope, which reports **unhandled** errors
    only.
    **The `test:` predicate is deliberate.** A bare `.catchError` swallows *everything*,
    permanently — including a `TypeError` introduced by a later change, which is exactly the
    bug worth reporting. Narrowing to `PlatformException` and `MissingPluginException` keeps
    channel-level failures silent and lets a programming error reach `P1-06`'s handler. Both
    types come from `package:flutter/services.dart`, so no import is added. This is an
    explicit trade, not an oversight: a non-matching rejection is reported, by design.
    **What "never throws" covers.** It covers a `PlatformException` or
    `MissingPluginException` from the platform call, and nothing else — which is what the doc
    comment now says. It does **not** cover the first line: `vibrateOnTouch()` runs *outside*
    the guard, and a closure reading a disposed `ProviderContainer` throws synchronously,
    inside a tap handler. That is ordinary Riverpod lifetime — a service resolved from a scope
    that still exists cannot hit it — and it is deliberately **not** caught, because
    swallowing it would hide a real wiring bug behind a silent no-op.
    **`unawaited` is documentation, not lint compliance.** `P1-01-app-scaffold.md` req 15
    sets the analyzer floor at `package:flutter_lints/flutter.yaml`, which does **not** enable
    `unawaited_futures`; nothing currently requires it. It marks the discard as intentional
    for the next reader and keeps the line correct if the floor is ever raised.
    **`void`, not `Future<void>`** — a tap handler fires and returns. Nothing awaits a buzz,
    and an async signature would push `await` into every call site for no observable gain.
    **No argument, ever** — requirement 6 bans a distinct haptic per action type, and a
    no-argument method makes that structural rather than a rule to remember. It also means the
    app-wide scope settled at OQ-2 costs nothing here: a menu button and a board cell call the
    same member, which is the reason `P4-01-main-menu.md` req 24 and
    `P3-03-scoreboard-turn-indicator.md` req 12 both cite this requirement.
    **One member, and the cost of a second.** Requirement 5 pins this interface at exactly one
    `void` member, which is what makes an illegal tap structurally unable to call anything —
    and it is also why **OQ-3 cannot be answered by editing one line**: capability detection
    has no expression here. See OQ-3.
    **A plain `Provider`, not a `NotifierProvider`** — the service holds no state. `P1-01`
    req 12 bans codegen, annotations and `StateNotifier`; it does not require every provider
    to be a notifier. The *setting* is the state: it lives in `settingsProvider`
    (`NotifierProvider<SettingsNotifier, Settings>`), and `vibrateOnTouchEnabledProvider` is
    `P1-04` req 26's read point over it. This PRD codes against those names and declares
    neither (requirement 11).
    **`ref.read` inside the closure, never `ref.watch`** — stated because the "improvement"
    is tempting and silent. `watch` would make `hapticServiceProvider` a *dependent* of the
    setting, so toggling vibrate would dispose and rebuild the service; that contradicts
    requirement 17, which requires the same instance to reflect the new value with nothing
    captured at construction. The closure captures `ref`, not the `bool`, so each fire
    re-reads the current value — which is what requirement 12 asks for, with no rebuild.
    *Testable — the seam:* a unit test constructs `PlatformHapticService` with a fake source
    and asserts both branches; a source scan finds exactly one class in `lib/` implementing
    `HapticService`, and no construction of it outside the provider.
    *Testable — the `read`/`watch` constraint.* **The scan is what holds this line: a source
    scan of `lib/haptics/` finds no `ref.watch`.** A behavioral test is possible but must be
    written exactly one way, with every variable below pinned:

    ```dart
    // _NullPreferencesRepository is this PRD's own stub — requirement 15's table.
    final container = ProviderContainer(overrides: [
      preferencesRepositoryProvider.overrideWithValue(_NullPreferencesRepository()),
    ]);
    final first = container.read(hapticServiceProvider);
    container.read(settingsProvider.notifier).setVibrateOnTouch(false);
    final second = container.read(hapticServiceProvider);
    expect(identical(first, second), isTrue);   // a `watch` implementation rebuilds → fails
    // and first.validAction() now emits nothing.
    //
    // No await, no pump, no pumpEventQueue anywhere between the three lines above:
    // SettingsNotifier.build() fires unawaited(_seed()), and if that seed resolves it
    // overwrites all four Settings fields — with a null-returning stub it would restore
    // vibrateOnTouch to the default `true` and silently invalidate both assertions.
    // The setter assigns state before its first await, so the un-awaited call has
    // already taken effect on the line after it.
    ```

    The setting **must** be changed through `settingsProvider.notifier`
    (`SettingsNotifier.setVibrateOnTouch`, `P1-04` req 27), because that is what invalidates
    the provider graph. **Overriding `vibrateOnTouchEnabledProvider` with a captured variable
    does not work and must not be used**: `overrideWithValue(true)` is immutable, so the
    change cannot be made at all; and `overrideWith((ref) => enabled)` over a captured `var`
    never notifies Riverpod, so the override element stays cached — a `watch` implementation
    is never invalidated, `identical(first, second)` is **true, and the test passes the exact
    bug it exists to catch**, while the "still reflects the new value" half fails a *correct*
    implementation. An earlier revision of this PRD specified that recipe; it was wrong.

15. **The entry point is injectable, and that is what makes it observable — and these are the
    test names.** A widget or unit test replaces the whole service through
    `ProviderScope(overrides: [hapticServiceProvider.overrideWithValue(FakeHapticService())])`.
    **No test outside this layer** needs to watch platform-channel traffic to know whether
    the app buzzed.

    **Test fixtures this PRD owns.** Everything in this table is declared here, by this PRD,
    because no other PRD declares it. Nothing below is asserted about a sibling.

    | Name | Shape | Where | Why pinned |
    |---|---|---|---|
    | `FakeHapticService` | `implements HapticService`; records each `validAction()` and exposes **`int get count`** — and nothing else | `test/haptics/fake_haptic_service.dart` — **public, not private to a test file** | `P3-02-move-input.md` req 14 imports it by this exact name and asserts `→ 1`, `→ 2`, `→ 3` in wave 3, and the non-board callers ratified at OQ-2 do the same. Naming it differently, scoping it privately, **or exposing the tally under a different member** each break a test that is already written. `int get count` is the member those assertions read. |
    | `_NullPreferencesRepository` | `implements PreferencesRepository` (`P1-04` req 21) — **all ten members**: the five reads (`readSelectedThemeUuid` → `Future<String?>`; `readMusicEnabled` / `readSoundEffectsEnabled` / `readVibrateOnTouchEnabled` / `readAnimationsEnabled` → `Future<bool?>`) each return `null`; the five writes accept and discard | private to `test/haptics/haptic_service_test.dart` | Requirements 8 and 14 both depend on the null-returning reads, and `setVibrateOnTouch` calls a write, so a read-only stub fails at runtime. **Ten, because there are five preferences** — theme, music, sound effects, vibrate, animations (`Menus and UI.md` → Settings Menu, four toggles; plus the theme UUID). Earlier revisions said three reads and then eight members; both predate `Theming.md` → Decisions → *Do all four toggles ship…* and neither compiles. *No PRD declares a shared in-memory `PreferencesRepository` fake — `P1-04` req 13 mentions its providers "can be overridden with an in-memory fake" but names no type, path or behavior. If `P1-04` ever publishes one, delete this stub and use it.* |
    | `haptic_service_test.dart` | this layer's own tests — requirements 6, 8, 10, 13, 14, 17, 18 | `test/haptics/haptic_service_test.dart` | — |

    **Where channel interception *is* legitimate, and what to intercept.** This layer's own
    tests are the one place `HapticFeedback` is the unit under test rather than a sibling's
    internals. The target, named once here so requirements 1, 6, 10 and 13 all inherit it:
    **`SystemChannels.platform`** (the `flutter/platform` channel), method call
    **`HapticFeedback.vibrate`** with argument **`'HapticFeedbackType.selectionClick'`** —
    that is what `HapticFeedback.selectionClick()` sends. Intercept it with
    `TestDefaultBinaryMessenger.setMockMethodCallHandler` and count matching calls. If OQ-1
    ratifies a different call, the *method* stays `HapticFeedback.vibrate` and only the
    argument string changes, so every count above survives the change — see requirement 18.
    *Testable:* a widget test that overrides `hapticServiceProvider` observes every call the
    widget under test makes, with no mock method-call handler and no `SystemChannels`
    interception anywhere in that test.

16. **This layer adds no dependency.** It uses `HapticFeedback`, `PlatformException` and
    `MissingPluginException` from `package:flutter/services.dart`, and `unawaited` from
    `dart:async` — all of which ship with Flutter and Dart. No `vibration`,
    `haptic_feedback`, `gaimon` or similar package is added.
    *(`P1-01-app-scaffold.md` req 14 declares its dependency table **exhaustive as of this
    wave** and requires any later addition to amend that requirement rather than appear
    silently. This requirement is the amendment that does not happen: the table gains no row
    for haptics. `dart:async` is a core library, not a pub package, so it is not a table
    entry either.)*
    *Testable:* `pubspec.yaml` is unchanged by this feature; a scan of `lib/haptics/` finds
    no import outside `dart:async`, `package:flutter/`, `package:flutter_riverpod/`, and this
    project's own `lib/state/settings_providers.dart` — the allow-list requirement 5's
    string-literal scan defers to.

17. **The gate reads a cached value synchronously, at fire time.** The persisted read
    published by `P1-04-persistence.md` req 21 is a `Future<bool?>` and cannot be awaited
    inside a tap handler. `P1-04` req 27 does the asynchronous read **once, off the tap
    path**, seeding `settingsProvider`; `vibrateOnTouchEnabledProvider` exposes the resolved
    `bool`, and `VibrateOnTouchSource` reads it on every call. Nothing in this layer captures
    the value into a field at construction, and nothing re-reads storage per tap.
    *(This is the shape `P2-02-audio.md` req 5 takes for the sound setting, against
    `soundEffectsEnabledProvider`. Requirement 12 is the behavior; this is the mechanism.)*
    *The currency guarantee is a satisfied dependency, not an open ask:* `P1-04` req 27
    states that a setter updates `state` before the write completes, so the next `ref.read`
    sees the new value — and names this requirement's consequence explicitly. One residual
    cost that PRD flags rather than hides: for a returning player who turned vibrate **off**,
    there is a window between first frame and seed completion where the provider still reads
    `true`, so one tap in that window could buzz. The mitigation — awaiting the seed during
    bootstrap — is `P1-01-app-scaffold.md`'s `main.dart` territory. Nothing in this layer
    changes either way, though the window now covers menu taps too (OQ-2), which is a reason
    for `P1-01` to take the mitigation rather than a change here.
    *Testable, and this is requirement 12's wave-2 assertable form:* build the service with a
    mutable fake — `var enabled = true; final s = PlatformHapticService(() => enabled);` —
    call `validAction()` (one platform message), set `enabled = false`, call again (zero),
    set it back to `true`, call again (one), with no rebuild and no reconstruction of the
    service in between. (A captured variable is correct **here**, where the fake *is* the
    source and Riverpod is not involved — unlike requirement 14's provider-level test, where
    it silently defeats the assertion.)

### The concrete haptic, and the version it is written against

18. **`validAction()` emits exactly one `HapticFeedback.selectionClick()`.**
    ***Proposed for ratification — see Pending confirmation.*** No design doc names a platform
    call; requirement 6 constrains only the character ("small, subtle", "not a rumble", one
    per action), and OQ-1 records that the mapping is unsettled. This requirement states the
    proposal in executable form so that an implementer emits the agreed line rather than
    picking one silently, and so that changing it later is a one-line edit at a single call
    site — which is what requirement 13 buys.
    *Testable:* `lib/haptics/haptic_service.dart` contains exactly one `HapticFeedback.`
    call; no other file in `lib/` contains any.
    *Cost of ratifying differently:* one line here and one argument string in requirement
    15's interception target. No count, no test structure and no other requirement changes.
    **This cheapness is specific to OQ-1** and does not extend to OQ-3, which changes the
    interface — the two are priced separately for that reason.

19. **The Riverpod major is pinned at 2.x for this layer's tests.** Requirement 8's element
    walk uses `ProviderContainer.getAllProviderElements()` and `ProviderElement.origin`;
    requirement 14's recipe uses `overrideWithValue` on a `Provider` and
    `settingsProvider.notifier`. Container introspection in particular is **not stable across
    Riverpod majors**, and `P1-01-app-scaffold.md` req 14 pins only a caret range resolved at
    scaffold time — which fixes the major in `pubspec.lock` but does not say which one this
    PRD's tests were written against. This requirement says it: **`flutter_riverpod` 2.x**.
    *(Stated rather than cited — no doc names a version. It is recorded because two testables
    here are version-sensitive and would otherwise fail with no indication of why. If the
    project moves to a later major, requirements 8 and 14 are the two places to re-verify,
    and requirement 8 names its fallback.)*
    *Testable:* `pubspec.lock` resolves `flutter_riverpod` to a 2.x version; `flutter test`
    compiles both recipes without modification.

### Design notes — constraints on how the above is built, not separately assertable

- **The locked/dimmed styling has to prevent the illegal tap in the first place**, because
  nothing explains it afterwards. This feature adds no compensating affordance and depends on
  that styling doing the work; the visuals are `P3-01-board-rendering.md`'s.
  *(`Game Board Design.md` → Taps outside the legal quadrant — "This is why the locked/dimmed
  styling matters so much: it has to prevent the tap, because nothing will explain it after
  the fact"; `design_handoff_game_ui/README.md` → Interactions & behavior — "which is why the
  locked veil sits at 0.50: it must be obviously non-tappable while still readable".)* This
  was requirement 9. It has no assertable form in this PRD — the thing it constrains is drawn
  a wave later by another PRD — so it is recorded as a constraint handed forward. It carries
  more weight when vibrate is off, where per requirement 5 the styling is the *only* thing
  standing between the player and an unexplained tap.

## Out of Scope

Named so the boundary is explicit. Each is specified elsewhere; do not specify it here.

- **The two-tap select-then-confirm gesture, what counts as a legal cell, and the
  tap-outside-to-clear behavior** — `P3-02-move-input.md`. This PRD attaches a buzz to valid
  actions; it does not define them, and that PRD's reqs 10 and 14 own the board-level
  assertions that requirements 2–4 here state as rules.
- **Which non-board controls exist, and their own call sites** — `P3-03`, `P3-04`, `P4-01`,
  `P4-03`, `P4-04`. The Decision at OQ-2 settles that they buzz; each PRD owns the call and
  its assertion.
- **Locked, dimmed, claimed and cat-game quadrant visuals, and the three highlights** —
  `P3-01-board-rendering.md`. The *Design notes* record a constraint on that work, nothing
  more.
- **The settings screen and sheet, the four toggle controls, and their layout** —
  `P4-04-settings.md`, whose req 8 owns the vibrate switch.
- **The music toggle, and music itself** — `Theming.md` → Decisions → *Do all four toggles
  ship, and is music a theme concern?* makes music a theme channel;
  `P1-04-persistence.md` stores it and publishes `musicEnabledProvider`, which has no
  consumer yet. None of it is a haptics concern, and this layer reads only the vibrate
  provider.
- **Storing the preferences, declaring `settingsProvider` / `vibrateOnTouchEnabledProvider` /
  `SettingsNotifier` / `preferencesRepositoryProvider` / `PreferencesRepository`, resolving
  the stored `null`, and seeding them** — `P1-04-persistence.md` reqs 21, 24, 26, 27 and 28.
  Requirement 14 codes against those symbols and implements none of them. A **shared**
  in-memory fake repository is nobody's today; requirement 15 stubs one privately rather than
  claim it.
- **The theme object, the theme providers, and any fixture for building a second `Theme`** —
  `P1-03-theme-system.md` req 24. Requirement 8 names its symbols and builds nothing.
- **Reporting errors, installing the handlers, and the `CrashReport` type** —
  `P1-06-crash-reporting.md`. Requirement 14 only decides what this layer hands to that path.
- **Sound effects and the audio package** — `P2-02-audio.md`. Sound is theme-driven and fires
  on different events; the two channels are specified separately and must not be wired
  together.
- **Animations and the animations toggle** — `P2-04-animations.md`.
- **Anything from `Alternative Game Styles.md`.** That is a declared parking-lot doc and
  explicitly not the game being built.

## Open Questions

Everything fenceable has been fenced into a requirement or a default above, and the one value
that could not be fenced carries a proposal at the top. Numbers are stable; answered ones are
kept as closed stubs, following `P1-02-engine-rules.md` and `P3-02-move-input.md`.

### OQ-1 — Which concrete haptic does "small, subtle buzz" map to?

*(Answered above as a proposal, needing confirmation — *Pending confirmation* and
requirement 18.)*

`Menus and UI.md` → Vibrate on Touch specifies the *feel* — "a **small, subtle buzz**",
"deliberately subtle", "not a rumble" — and no doc names a platform API or intensity. iOS is
the primary target (`Tech Design.md` → Decisions → Primary target — Apple). A fence does not
substitute here: an implementer must emit one line, so the choice is made either by the user
or by whoever types it. Requirement 18 records the reversal cost: one line, one argument
string, nothing else.

### OQ-2 — Closed: the rule is app-wide

**Answered.** `Game Board Design.md` → Decisions → *Does the haptic fire on non-board
controls?*:

> **Yes — every valid tap buzzes, anywhere in the app.** Menu buttons, theme rows, settings
> toggles, the game-over card's controls, the settings gear — not only board cells.

The Decision records the reasoning — it matches the setting's own name, *Vibrate on Touch*,
and it is what three PRDs had already assumed — and preserves the other half explicitly:
*"an illegal board tap remains silent, which is the existing rule and is unchanged."*

**What this changes here:** requirement 1 is literal rather than bounded, requirement 3
records that the board is one instance of the rule and not its extent, and requirement 13's
"anywhere in the app" is enforceable in the plain sense. **What it changed elsewhere:** nothing
was deleted. `P3-04` req 15, `P4-03` req 18 and `P3-03` req 12 are ratified; `P4-03` has
dropped its conditional; and `P4-01-main-menu.md` added req 24, firing the buzz on all four
menu buttons. Two of those PRDs also had to narrow "and nothing else" to "no other
**navigation** operation" — see the wording-trap note near the top of this file.

Kept as a stub because four requirements and four sibling PRDs reference this number. The
escalation table it carried is deleted — it did its job.

### OQ-3 — What happens on a device with no haptic engine?

No doc addresses it. `Tech Design.md` → Decisions → Device support names iPhone first, iPad
second, Android far future — and iPad has no Taptic Engine, so this is reachable inside the
stated support ordering, not a hypothetical.

**What actually happens today, stated precisely.** `HapticFeedback.selectionClick()` goes over
`SystemChannels.platform`, which the Flutter engine implements directly. On hardware with no
haptic engine the call **succeeds and does nothing** — it does not reject, and requirement 14's
`catchError` is *not* what handles it. So the current behavior is a silent no-op, and it is a
no-op by default rather than by design.

**The consequence, which this PRD is the right place to record: there is no observable signal
anywhere in this design by which this question could be answered.** Nothing in the app can
currently distinguish "buzzed" from "did nothing" on a device that cannot buzz. That makes the
reversal more expensive than an earlier revision of this PRD claimed:

- *"Fall back to a system vibration"* — a change to requirement 14's single line. Cheap.
- *"Hide the toggle on hardware that cannot buzz"* (`P4-04-settings.md`) — **not cheap, and
  not a line.** It needs capability *detection*, and `HapticService` has exactly one member
  returning `void`, pinned there by requirement 5 precisely so an illegal tap can call
  nothing. Answering this way means **a second member on the published interface** — something
  like `bool get isSupported` — plus requirement 5's testable, requirement 15's
  `FakeHapticService`, and `P4-04`'s switch. It is an interface change, and the sooner it is
  known the cheaper it is: six PRDs code against this interface today.

Needed before `P4-04-settings.md` decides whether the toggle is drawn on iPad.

### OQ-4a — Tap-outside-to-clear: **fenced default, no buzz**

`P3-02-move-input.md` req 14 asserts *"tap in a gutter or on the scoreboard → still 3"*, with
the parenthetical that the counts "encode today's answer, 'no'" — so the call site has already
implemented one reading. It is recorded as the default it has become:

> **A tap that clears a pending selection does not buzz.**

**OQ-2's Decision does not settle this.** That Decision widens *where* valid taps buzz — it
names controls, all of which do something — while this is about whether a tap on nothing that
happens to clear a selection is a valid action at all. The tension is why this is a *default*
rather than a requirement: `Game Board Design.md` → Move Input → Changing your mind makes
"tap outside the full grid → deselects entirely" one of exactly two ways out of a pending
selection, so it changes state — but it is also a tap on nothing, the paradigm case of "that
did nothing".

**Reversing it costs one clause** in `P3-02` req 14's counts and nothing in this PRD:
requirement 13 means the call site decides whether to invoke `validAction()`, and this layer
behaves identically either way.

### OQ-4b — Do actions the player did not initiate by tapping buzz?

Open, and genuinely with the user. OQ-2's Decision is worded around *taps* — "every valid
**tap** buzzes" — so it widens the set of controls without saying anything about events the
player did not touch. Whether a haptic accompanies a quadrant being claimed, a game being won,
or the turn handing over is still unstated. Nothing in this PRD attaches a haptic to a game
event, and requirement 14's interface neither supports nor forbids one being added later.

### OQ-5 — With vibrate off, is the app meant to have no validity signal at all?

Stated as a condition of the design rather than resolved, per requirement 5.

The docs combine to this: the haptic is the validity signal (`Game Board Design.md` → Haptic
Rule, *"the absence of feedback is the feedback"*), the setting can switch it off
(`Menus and UI.md` → Settings Menu), and nothing may stand in for it — no shake, no flash, no
error message (`Game Board Design.md` → Taps outside the legal quadrant). So with vibrate
off, a legal tap and an illegal tap are indistinguishable on this channel, and the *Design
notes* leave the locked/dimmed styling as the only thing preventing the confusion.

OQ-2's Decision sharpens this rather than answering it: the buzz is now the confirmation
signal for every control in the app, so switching it off removes more than it used to. No doc
acknowledges that state, so it is unclear whether it is an accepted trade-off or an oversight.
The PRD does not choose: requirements 1, 5 and 10 are all explicitly scoped to the setting's
state, so an implementer cannot invent a substitute signal by accident. This one needs the
user's intent.

### OQ-6 — Closed: which `lib/` layer does this live in

**`lib/haptics/`.** `Tech Design.md` → Decisions → *Project structure — layer-first* lists it
in the tree — *"`haptics/` ← haptic feedback, owned by P2-03-haptics"* — one of five layers
added in a single amendment alongside `audio/`, `entitlements/`, `diagnostics/` and
`purchase/`, which that Decision records as closing "the same gap in five PRDs at once."
`P1-01-app-scaffold.md` req 2 builds that tree. Kept as a stub because six testables name the
path.

### OQ-7 — Closed: who publishes the vibrate value, and who resolves its `null`

- **The value.** `Menus and UI.md` → Decisions → *What are the settings on a fresh install?* —
  **all four toggles default to on** (music, sound effects, vibrate on touch, animations).
  The count changed with `Theming.md` → Decisions → *Do all four toggles ship, and is music a
  theme concern?*; the vibrate default did not.
- **The publisher.** `P1-04-persistence.md` req 26 declares `settingsProvider`,
  `SettingsNotifier` and **four** `Provider<bool>` read points — `musicEnabledProvider`,
  `soundEffectsEnabledProvider`, `vibrateOnTouchEnabledProvider`, `animationsEnabledProvider`
  — in `lib/state/settings_providers.dart`, resolving "nothing stored" to `true` in one
  place; its req 27 seeds and updates them. This layer reads exactly one of the four.
- **The repository provider.** `P1-04` req 28 declares `preferencesRepositoryProvider` in
  `lib/storage/storage_providers.dart`. The interface behind it now carries five preferences,
  which is why requirement 15's stub implements ten members.
- **Still nobody's, and stubbed rather than claimed:** a shared in-memory
  `PreferencesRepository` fake. See requirement 15's table.
- **The parallel case:** `P2-02-audio.md` req 5 names `soundEffectsEnabledProvider`.

### OQ-8 — Closed: nothing asserts requirement 3

**Closed by `P3-02-move-input.md` req 14**, whose verification counts a reselecting tap —
*"tap on a different legal cell → 2"* — against `FakeHapticService`, and which states that it
is supplying the assertion this PRD recorded as owned by nobody. That PRD's own OQ-8 (the
substitutability question) is closed against requirement 15 here. **Nothing further is asked
of `P3-02`;** an earlier revision of this PRD carried a paste-ready clause, and acting on it
now would add a duplicate assertion.
