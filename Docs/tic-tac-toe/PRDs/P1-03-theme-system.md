# PRD: Theme System

> **Status:** Draft · Source docs read: `Theming.md`, `Tech Design.md`, `Animations.md`,
> `Menus and UI.md`, `Game Board Design.md`, `Game Overview.md`, `Rules.md`, `roadmap.md`,
> and the read-only reference asset `design_handoff_game_ui/` (`README.md`,
> `neon.theme.json`, `themes.catalog.json`). `Alternative Game Styles.md` is a declared
> parking-lot doc and was not used as a source.

**Wave:** P1 · **File:** `P1-03-theme-system.md`

**Depends on:** nothing. This is greenfield — `src/Tic-Tac-Toe-Extreme` has no application
code yet, so this PRD stands up the `lib/theme/` layer from zero.

**Depended on by:** `P1-04-persistence.md` (stores the selected theme UUID),
`P1-05-theme-guard-test.md` (enforces the Architectural Rule),
`P3-03-theme-selection.md` (the selection overlay), `P4-01-audio.md` (plays the sound
slots), `P4-03-animations.md` (plays the animation slots), `P4-04-classic-theme.md`
(authors the second theme), `P4-05-in-app-purchases.md` (entitlements, purchase and
restore). This PRD defines the **slots**; those define the behavior.

---

## Problem

There is no application code yet, and the one constraint the design docs say is expensive
to retrofit is the theme system: *"All of our code operates off of the theme. No code
should be operating independently from the selected theme"* (`Theming.md` → Architectural
Rule; repeated in `Tech Design.md` → The theme system is the main architectural risk).
Any screen built before the theme layer exists will hardcode a color, a font, a mark, a
sound or a duration, and every one of those is a file that has to be touched again later.

There is also no runtime home for the Neon definition. Neon exists as an approved,
machine-readable file in the handoff bundle, but nothing in the app can load it, merge a
partial theme over it, or hand its values to a widget.

## Goal

The app ships a theme layer in which a theme is a **data file, not code**: YAML, bundled
with the app, identified by a UUID, materialized once at startup by merging over a
complete Neon base, and readable from anywhere in the widget tree. Neon is authored in
full — every themeable value defined, no gaps — because it is the floor with no fallback.
Every visual, audio and motion value the rest of the app will need has a named slot on
that object, so that adding a theme later requires adding a theme file and changing no
game, board or menu code.

## Requirements

### Themes as data

1. A theme is **data loaded at runtime, not a Dart class compiled into the app** — "a
   universal, theme-like object that can be loaded in."
   *(`Tech Design.md` → Decisions → Theme representation — data, not code)*
2. The on-disk format for theme files is **YAML**.
   *(`Tech Design.md` → Decisions → What format are theme files — JSON or YAML?)*
3. Theme files are **bundled/shipped with the app**, living in `assets/themes/*.yaml`.
   They are not user-uploaded, not user-authored and not downloaded from a server.
   *(`Theming.md` → Where Themes Live; `Tech Design.md` → Decisions → Project structure —
   layer-first)*
4. **Each theme carries a UUID in its YAML file, and that UUID is the theme's identity.**
   Nothing downstream identifies a theme by name — renaming a theme must not change which
   theme it is.
   *(`Tech Design.md` → Decisions → Theme identity — UUID)*
5. The theme layer lives at `lib/theme/`, with `theme.dart` holding the merged theme
   object and `loader.dart` holding YAML → theme.
   *(`Tech Design.md` → Decisions → Project structure — layer-first)*

### Inheritance and materialization

6. **Neon is the base theme.** Anything a theme does not define comes from Neon — colors,
   art style, sound effects, animations, "the whole nine yards."
   *(`Theming.md` → Neon Is the Base Theme)*
7. **Inheritance depth is exactly one level.** A theme inherits from Neon, full stop. No
   chains, no theme inheriting from another theme.
   *(`Theming.md` → Inheritance Depth; corroborated by
   `design_handoff_game_ui/themes.catalog.json` → `inheritanceDepth: 1`)*
8. Fallback is implemented as a **merge, not a per-lookup resolve**: each theme is
   materialized into a complete theme **at startup** by merging its overrides over Neon,
   so at runtime every lookup hits a complete theme and there is no fallback step.
   *(`Tech Design.md` → Decisions → Fallback to Neon — merge, not resolve; `Theming.md` →
   Why this matters for the build)*
9. A theme file may define **only** what it wants to be different; a theme that overrides
   two colors and nothing else must still materialize into a complete, working theme.
   *(`Theming.md` → Neon Is the Base Theme → How it works, Why this matters for the
   build)*
10. Animations and sounds merge by the same rule as every other value — a theme starts
    from Neon's complete set and its own definitions merge over the top, overriding only
    what it names.
    *(`Animations.md` → Decisions → Do themes inherit Neon's animations?; `Theming.md` →
    Sound Decisions → Sound falls back to Neon)*

### The Neon base theme

11. Neon ships **complete — every themeable value defined, no gaps** — because it is the
    one theme with nothing to fall back to. A gap in Neon is the one failure the system
    cannot absorb.
    *(`Theming.md` → Neon Is the Base Theme → How it works; Why this matters for the
    build; What happens if a theme fails to load)*
12. Neon's authored values are those of the approved definition
    `design_handoff_game_ui/neon.theme.json` — its `color`, `marks`, `type`, `radius` and
    `board` sections are final and exact, and the handoff's *Design tokens* tables are the
    human-readable form of the same values.
    *(`design_handoff_game_ui/README.md` → Fidelity, Design tokens; `Theming.md` → Theme
    Catalog → Neon as drawn)*
13. Neon's UUID is `b7c1f0a6-2f5e-4d3a-9c88-0f5a1e2d3c40`, and Neon is both the base theme
    and the default active theme — what a player sees before they have ever opened theme
    selection.
    *(`design_handoff_game_ui/themes.catalog.json` → `baseThemeId`, `defaultThemeId`;
    `Menus and UI.md` → Decisions → Which theme is active by default?)*
14. Neon's `sound` and `animation` keys exist as **stubs with no produced assets** — the
    sound files are not made yet, and the animation entries are starting values, not
    decisions. The keys must be present and merge-able; the assets behind them are
    `P4-01` and `P4-03` work.
    *(`neon.theme.json` → `notes`, `sound`, `animation`; `design_handoff_game_ui/README.md`
    → Assets → Sounds; `Animations.md` → Where Animations Fire; `Tech Design.md` →
    Decisions → Where do sound and art assets come from?)*

### What the theme object must carry (the slots)

15. The theme object carries **visual** slots covering at minimum: page/board background,
    big-board and small-board grid lines, the player marks, last-move highlight,
    active-quadrant highlight, locked/inactive quadrant styling, pending-move preview
    styling, claimed-quadrant styling, cat-game quadrant styling, turn indicator,
    scoreboard, and main menu styling (background, button look, title).
    *(`Theming.md` → What a Theme Controls → Visual; `Menus and UI.md` → Main Menu;
    `Game Board Design.md` → Everything Here Is Theme-Driven)*
16. **Marks are asset slots on the theme, not shapes drawn in board code** — a theme
    supplies its mark art as an **image or an icon**. Marks are not locked to X and O; a
    theme may swap them for icons, emoji, animals or shapes. Neon's X and O are Neon's
    choice of art, not a constraint on the system.
    *(`Tech Design.md` → Decisions → Marks — image or icon, supplied by the theme;
    `Theming.md` → Decisions → Marks beyond X and O)*
17. The theme object carries **audio** slots for: placing a mark, winning a small board /
    claiming a quadrant, cat game, winning the whole game, and button taps / menu
    navigation. A **background-music** slot is part of the shape but is not used in this
    version — one-shot sound effects only, and the audio structure must not make adding a
    music layer painful later.
    *(`Theming.md` → What a Theme Controls → Audio; Sound Decisions → One-shot sound
    effects only, for now; `neon.theme.json` → `sound.music: null`)*
18. The theme object carries **animation** slots, and each animation carries **its own
    duration** — speed is specified in the animation, not globally, so a theme controls
    its own pacing. The animated moments named are placing a marker, claiming a quadrant,
    cat game, winning the game, and the active-quadrant and last-move highlights.
    *(`Animations.md` → Decisions → Duration lives in the animation; Where Animations
    Fire; `neon.theme.json` → `animation`)*
19. **A theme supplies its own font**, and the theme object needs somewhere to put one.
    Inter 400/500/600 is bundled as **Neon's font choice, not an app-wide font constant** —
    a font is a themeable value like any other. This is what keeps Requirement 25 whole:
    the Architectural Rule names fonts among its six categories, so an app-wide font
    constant would be an exception carved into the rule rather than a value the theme
    owns.
    *(`Theming.md` → Decisions → Does a theme supply its own font; `Tech Design.md` →
    Decisions → Do themes pick their own font?; `design_handoff_game_ui/README.md` →
    Assets → Fonts)*
20. The last-move highlight, the active-quadrant highlight and the pending-move preview
    are **separately addressable slots**, because all three can be on screen at once and
    must be visually distinguishable.
    *(`Game Board Design.md` → Three highlights on screen at once; The Two Highlights
    Together; `design_handoff_game_ui/README.md` → Cell states)*
21. The schema must let a theme distinguish things by **more than colour** — shape, icon,
    outline, pattern — because whether anything is distinguished by colour alone is
    "handled per theme," not a system-wide rule.
    *(`Theming.md` → Decisions → Is anything distinguished by colour alone?)*

### Runtime integration

22. Use Flutter's **`ThemeData` / `ThemeExtension` as far as possible**, filled out from
    the theme file. The parts Flutter's theming does not support are implemented
    ourselves.
    *(`Tech Design.md` → Decisions → Flutter's ThemeData vs our own theme object)*
23. **Sounds and animations live in the same theme object**, not a parallel structure —
    Flutter gets what it can take, we handle the rest, all fed from the same file.
    *(`Tech Design.md` → Decisions → Flutter's ThemeData vs our own theme object)*
24. The active theme is exposed through **Riverpod** (plain `Notifier`/`NotifierProvider`,
    no `@riverpod` codegen), and must be readable from **everywhere**, including deep in
    the board widget tree.
    *(`Tech Design.md` → Decisions → State management — Riverpod)*
25. **Architectural Rule.** No hardcoded colors, backgrounds, fonts, piece styles, sounds
    or animations anywhere in the code. Every visual, audio and motion value is read from
    the currently selected theme: if something on screen has a color, that color came from
    the theme; if something makes a noise, that sound came from the theme; if something
    moves, that motion came from the theme. No exceptions.
    *(`Theming.md` → Architectural Rule)*
26. **Adding a new theme requires zero changes to game, board or menu code** — only adding
    a new theme definition.
    *(`Theming.md` → Architectural Rule)*

### Failure behavior

27. If a theme fails to load, show a **modal on the Theme screen** saying the theme is
    unavailable and asking the player to pick another, **then fall back to Neon**.
    *(`Theming.md` → Decisions → What happens if a theme fails to load; restated in
    `themes.catalog.json` → `failureBehavior`)*
28. Neon is the one theme with nothing to fall back to.
    *(`Theming.md` → Decisions → What happens if a theme fails to load; Why this matters
    for the build)*

### Boundaries of the theme object

29. **Haptics are not theme-driven.** Vibration lives at the application setting level; a
    theme cannot define or change the buzz. The theme object has no haptics slot.
    *(`Theming.md` → What a Theme Does NOT Control)*
30. The sound-effects, animations and vibrate **toggles are global player settings, not
    theme properties** — a theme cannot override them, and they mute/disable a channel for
    every theme.
    *(`Theming.md` → Sound Decisions → Global mute; `Animations.md` → Decisions → Turn
    animations off — a global setting; `Menus and UI.md` → Settings Menu)*
31. **Ownership / entitlement is not part of a theme definition.** A theme is an
    audio-visual package; purchase state is account/device state and lives outside the
    theme object. This holds now that some themes are paid — a theme file still describes
    a theme; what a player owns lives elsewhere.
    *(`design_handoff_game_ui/themes.catalog.json` → `note`;
    `design_handoff_game_ui/README.md` → 2a → The four themes shown)*

## Out of Scope

- **The hardcoded-theme-value enforcement test.** Requirement 25 states the rule; the test
  that checks it, its banned-pattern list and its zero baseline are `P1-05-theme-guard-test.md`.
  *(`Tech Design.md` → Decisions → Do we add a test that fails on hardcoded theme values?)*
- **Persisting the selected theme UUID** to device storage via `shared_preferences` —
  `P1-04-persistence.md`. This PRD only fixes that the identity persisted is the UUID
  (Requirement 4).
- **The theme selection overlay UI** — the sheet, the rows, the preview tiles, the ACTIVE
  highlight, the free/paid labelling, and the fact that selection lives on the main menu
  as an overlay: `P3-03-theme-selection.md`. Note also that the theme **cannot be changed
  mid-game** (`Theming.md` → Decisions → Can you change the theme mid-game).
- **Entitlements, purchase and restore** — `P4-05-in-app-purchases.md`. Themes beyond the
  two free ones are paid: Neon and Classic Red vs Blue are free, every theme beyond those
  two is paid, and the selection list labels which is which. None of that reaches the
  theme object — ownership is not part of a theme definition (Requirement 31), so a theme
  file is unchanged by it.
  *(`Theming.md` → Decisions → Are themes unlockable/rewards, Which themes are free;
  `Tech Design.md` → Decisions → In-app purchases)*
- **The Classic Red vs Blue theme content** — its UUID's YAML file and the concrete list of
  values it overrides: `P4-04-classic-theme.md`. Two themes ship at launch
  (`Theming.md` → Decisions → How many themes ship at launch), but only Neon is authored
  here.
- **Audio playback** — loading and firing the sound assets, and the `audioplayers`
  integration: `P4-01-audio.md`. This PRD defines only the slots.
- **Animation playback** — running the animations, one-at-a-time sequencing, non-blocking
  input, and the animations-off instant-state-change path: `P4-03-animations.md`. This PRD
  defines only the slots and that each carries its own duration.
- **Producing sound and art assets.** Assets are generated with Replicate when actually
  needed, not now.
  *(`Tech Design.md` → Decisions → Where do sound and art assets come from?)*
- **Board rendering, screens and widgets.** This PRD stands up the theme layer they read
  from, not the widgets themselves.

## Open Questions

### From the design docs, worded as the docs word them

*(`Tech Design.md` → Open Questions → 2. Theme loading — all three sit directly on this
feature and are **not** resolved here.)*

- Are all themes loaded and materialized at startup, or only the selected one, on demand?
  `Theming.md` → Why this matters for the build says materialization happens "at startup"
  but does not say for how many themes.
- Are the theme YAML files declared as assets in `pubspec.yaml`?
- What happens to an unknown or misspelled *key* inside an otherwise-valid theme file?
  Merge-over-Neon will quietly fill the gap with Neon's value, so a typo in a theme file
  fails silently. The hardcoded-theme-value test guards code that bypasses the theme; it
  does not guard a theme file that misspells a key.

Also open, from `Theming.md` → Open Questions (owned by `P4-04-classic-theme.md`, listed
here because it is the first real test of Requirement 9):

- Which values, concretely, does Classic Red vs Blue override?

### Contradiction between docs — flagged, not resolved

- **How many themes the selection list shows.** `design_handoff_game_ui/README.md` →
  *2a — Theme Select* and `themes.catalog.json` show **four** themes — Neon, Classic Red
  vs Blue, Splat and Dinosaurs — while `Theming.md` → Decisions → How many themes ship at
  launch says **two**, and `Menus and UI.md` → Theme Selection lists exactly those two.
  The handoff itself marks Splat and Dinosaurs as placeholders that "do not exist" and
  must not ship as designed, so this may be a mock artifact rather than a real
  disagreement — but the two documents still describe different screens. That is
  `P3-03-theme-selection.md`'s call, not this PRD's.

  The free-vs-paid half of this disagreement is **no longer contested**: `Theming.md` →
  Decisions → Are themes unlockable/rewards now says some themes are paid, which agrees
  with the handoff's `free` / `owned` / `locked` states, its price button and its
  *Restore purchases* footer. Requirement 31 — entitlement is not part of a theme
  definition — is stated by both sides and stands unchanged.

### Raised by this PRD, not by the design docs (proposals, clearly mine)

- **What counts as "fails to load"?** Requirement 27 gives the behavior but not the
  trigger. Missing file, malformed YAML, missing/duplicate UUID, and a referenced asset
  that is absent are four different failures, and only some of them are detectable at
  startup. An implementer will otherwise guess.
- **What happens if *Neon* fails to load?** The docs say Neon is the theme with nothing to
  fall back to, which states the constraint but not the behavior. Hard failure at startup?
  A built-in minimal fallback? Not settled anywhere.
- **JSON reference vs YAML runtime format.** The approved Neon definition is
  `neon.theme.json` and the handoff says "load it as the base theme," while `Tech
  Design.md` settles the shipped theme-file format as **YAML**. This PRD reads that as:
  ship Neon as YAML transcribed faithfully from `neon.theme.json`, which stays the
  read-only source of truth for the values. If the intent was instead to load the JSON
  directly, that is a decision that needs stating.
- **CSS-shaped values in `neon.theme.json`.** Several `board` values are CSS shadow
  strings (`"0 0 0 1.5px rgba(...), 0 0 14px rgba(...)"`) and colors appear as `rgba()`
  strings. Flutter has no direct equivalent, so the YAML schema has to decide how these
  are represented — structured fields, or parsed strings. Requirement 12 fixes the values,
  not their encoding.
