# PRD: Theme Selection

> **Status:** Draft · Source docs read: `Menus and UI.md`, `Theming.md`, `Tech Design.md`,
> `Game Overview.md`, `Game Board Design.md`, `Animations.md`, `roadmap.md`, and the
> read-only reference asset `design_handoff_game_ui/` (`README.md` → *2a — Theme Select*,
> `themes.catalog.json`). `Alternative Game Styles.md` is a declared parking-lot doc and
> was not used as a source.
>
> **Revised** after `Theming.md` → Decisions → *Are themes unlockable/rewards* was
> rewritten and → *Which themes are free* was added. The free-vs-paid question this PRD
> previously carried as an open contradiction is now decided and appears in Requirements
> 10–14.

**Wave:** P3 · **File:** `P3-03-theme-selection.md`

**Depends on:**

- `P1-03-theme-system.md` — the theme object, its UUID identity, merge-over-Neon
  materialization, and the slots this screen reads. This PRD consumes that layer and
  defines none of it.
- `P1-04-persistence.md` — storing and restoring the selected theme's UUID. This PRD
  requires that a selection be handed to that layer; it does not specify the storage.
- `P3-01-main-menu.md` — the main menu this overlay opens on top of, including the Theme
  button that opens it.
- `P4-05-in-app-purchases.md` — entitlements, purchasing and restore. This screen **reads**
  entitlement state and renders labels from it; it never implements buying.

**Depended on by:** `P4-04-classic-theme.md` authors the second theme this screen lists;
until it exists, the Classic row has a name and a UUID but no authored overrides.

---

## Problem

Themes are the feature the design docs put front and center — *"the point is to make it
fun for kids to change out the theme"* (`Theming.md` → The Idea), and theme selection is
deliberately *"up front, not buried in settings"* (`Menus and UI.md` → Main Menu). But
there is no application code yet, so a player has no way to see which themes exist, no way
to tell which one they are looking at, and no way to change it. Two themes ship at launch
and neither is reachable.

Themes are also now partly a paid product: *"we will have 2 free themes the neon and the
red Vs Blue themes any other themes will be a paid for theme"* (`Theming.md` → Decisions →
Are themes unlockable/rewards). The list is the only place that tells a player which is
which, and nothing shows it today.

There is also no place for the one failure the theme system is specified to survive.
`Theming.md` → Decisions → What happens if a theme fails to load puts the "this theme is
unavailable" modal *on the Theme screen* — a screen that does not exist yet, so the
fallback-to-Neon behavior has nowhere to be shown.

## Goal

A player on the main menu taps **Theme** and gets an overlay, drawn over the menu rather
than replacing it, listing the themes that ship with the app — each labeled free or paid,
with the currently active one visibly highlighted before they touch anything. Picking one
applies it immediately, closes the overlay onto a main menu now drawn in the new theme,
and that choice survives closing the app. Neon is what they see before they have ever
opened it. Both themes that ship are free, so nothing here is buyable yet — but the list
carries its ownership labeling from day one, so a paid theme drops in without reshaping
the screen. If a theme cannot be loaded, they are told so and put back on Neon rather than
left on a broken screen.

## Requirements

### Where it lives and how it opens

1. **Theme selection is an overlay on the main menu, not its own screen.** The main menu
   remains present behind it.
   *(`Menus and UI.md` → Decisions → Is theme selection its own screen or an overlay?;
   → Screens (so far) → 5; `Theming.md` → Decisions → Where theme selection lives;
   corroborated by `design_handoff_game_ui/README.md` → 2a, "never its own screen".)*
   *Testable:* opening theme selection does not replace the main menu route; the menu is
   still mounted and visible behind the overlay's scrim.

2. **The overlay is opened by the Theme button on the main menu**, and by nothing else.
   *(`Menus and UI.md` → Main Menu; → Theme Selection.)* The button's placement, size and
   equal-to-Play-Game weight belong to `P3-01-main-menu.md`.

3. **The overlay can be dismissed without changing the active theme**, via the close
   control in its header.
   *(`design_handoff_game_ui/README.md` → 2a, header: "close icon button right".)*
   *Testable:* open the overlay, close it, and the active theme UUID is unchanged.

### What it lists

4. **The list is built from the app's theme catalog, not from a hardcoded pair of rows.**
   Adding a theme definition must add a row with no change to menu code.
   *(`Theming.md` → Architectural Rule: "Adding a new theme should require zero changes to
   game/board/menu code — only adding a new theme definition".)*
   *Testable:* adding a third theme definition makes a third row appear with no edit under
   the menu UI source.

5. **Two themes are listed at launch: Neon and Classic Red vs Blue.**
   *(`Theming.md` → Decisions → How many themes ship at launch; `Menus and UI.md` → Theme
   Selection, → Screens (so far) → 5.)* See also Open Question 1 — the approved handoff
   still draws four.

6. **Each row shows a preview tile rendered in that theme's own colors and marks, the
   theme's name, and a one-line description.**
   *(`design_handoff_game_ui/README.md` → 2a: "a 66×66 preview tile (a miniature quadrant
   rendered in that theme's own colors and marks), the name, and a one-line description in
   the theme's voice"; per-theme `blurb` values in `themes.catalog.json`.)*

7. **The preview tile is the one place in the app that reads a non-active theme's values.**
   Rendering a row must not require making that theme active.
   *(`design_handoff_game_ui/README.md` → 2a.)* What that costs at load time is Open
   Question 3.

8. **The currently active theme is highlighted in the list**, so it is obvious which one is
   in use before the player changes anything.
   *(`Menus and UI.md` → Decisions → How does theme selection show which theme is in use?;
   → Theme Selection; visual treatment in `design_handoff_game_ui/README.md` → 2a →
   Ownership states → Active, and `themes.catalog.json` → `activeBadge`.)*
   *Testable:* with Neon active, the Neon row carries the active treatment and the Classic
   row does not; after switching, the treatment moves with the selection.

9. **Before a player has ever opened theme selection, Neon is the active theme**, and the
   first time the overlay is opened Neon is the highlighted row.
   *(`Menus and UI.md` → Decisions → Which theme is active by default?; `Theming.md` →
   Neon Is the Base Theme; `themes.catalog.json` → `defaultThemeId`.)*
   *Testable:* on a device with nothing stored, open the overlay — Neon reads as active.

### Free and paid

10. **The list labels which themes are free and which are paid.** Every row carries an
    ownership label.
    *(`Theming.md` → Decisions → Which themes are free: "The theme selection list
    **labels** which themes are free and which are paid"; → Are themes unlockable/rewards:
    "Yes — some themes are paid ... We will label what themes are free".)*
    *Testable:* every rendered row carries exactly one ownership label.

11. **Neon and Classic Red vs Blue are free. Every theme beyond those two is paid.**
    *(`Theming.md` → Decisions → Which themes are free.)*
    *Testable:* both rows that ship render the free label; a fixture theme outside those
    two UUIDs does not.

12. **The label is driven by entitlement state read per theme, not by a field inside the
    theme definition.** A theme file carries no ownership or price value.
    *(`design_handoff_game_ui/themes.catalog.json` → `note`: "Ownership is NOT part of a
    theme definition — a theme is an audio-visual package; entitlement is account/device
    state"; `design_handoff_game_ui/README.md` → 2a: "keep purchase state **out of the
    theme definition**"; consistent with `P1-03-theme-system.md` → Requirement 31.)*
    *Testable:* no shipped theme YAML contains an ownership or price key; changing the
    entitlement a row is given changes its label with no edit to any theme file.

13. **The row supports the ownership states `free`, `owned` and `locked` without reshaping
    the screen**, with the treatments the handoff specifies — `FREE` and `OWNED` tags, and
    for a locked row a dimmed preview tile and a price action in place of a tag. Attaching
    a price to a theme must not require changing the row's layout.
    *(`design_handoff_game_ui/README.md` → 2a → Ownership states — the part to build
    carefully: "Build the theme list so an `ownership` field (`free | owned | locked`) and
    a price can be attached per theme without reshaping the screen";
    `themes.catalog.json` → `ownershipStates`.)*
    *Testable:* a fixture theme in each of the three states renders its specified treatment
    through the same row widget.

14. **A theme the player is not entitled to cannot be applied from this screen**, and **no
    purchase flow is reachable here at launch.** Both themes that ship are free, so no row
    can be locked and there is nothing to sell: the price button, the purchase sheet and
    the *Restore purchases* footer drawn on handoff `2a` have no product behind them. This
    screen reads entitlement and renders labels; buying, restoring and whatever a locked
    row's price action opens are `P4-05-in-app-purchases.md`'s.
    *(`Theming.md` → Decisions → Which themes are free + → How many themes ship at launch;
    `themes.catalog.json` → `ownershipStates.locked.playable: false`;
    `design_handoff_game_ui/README.md` → 2a, which calls its paywall "a *direction*, not
    current scope".)*
    *Testable:* with only the two shipped themes installed, no row renders a price action
    and no purchase or restore control is present; a fixture locked theme cannot be applied
    by tapping its row.

### Selecting a theme

15. **Selecting a theme applies it.** The change takes effect immediately, not on restart.
    *(`Menus and UI.md` → Theme Selection: "Selecting a theme applies it".)*
    *Testable:* select Classic Red vs Blue and the main menu behind the overlay renders in
    Classic's values without an app restart.

16. **Selecting a theme closes the overlay**, returning the player to the main menu.
    *(`design_handoff_game_ui/README.md` → 2a: "tapping a free or owned row applies the
    theme and closes the overlay".)*

17. **The selection persists between sessions.** Close the app, open it again, and that is
    still the player's theme, active before they touch anything.
    *(`Theming.md` → Decisions → Does the theme persist between sessions; `Menus and UI.md`
    → Persistence.)* This PRD requires only that the applied selection be handed to the
    persistence layer at the moment it is applied; the store, the key and the fact that the
    persisted value is a UUID are `P1-04-persistence.md`'s.
    *Testable:* select Classic, restart the app, and the main menu renders in Classic and
    the Classic row reads as active.

18. **Selecting a theme fires the vibrate haptic**, subject to the vibrate-on-touch
    setting, because it is a valid selection.
    *(`Menus and UI.md` → Settings Menu → Vibrate on Touch: "Fires on making a selection /
    clicking"; `Game Board Design.md` → Haptic Rule: "Any valid selection or valid action
    buzzes".)*

### Where it is *not* available

19. **The theme can be changed from the main menu only — there is no mid-game theme
    change.** No control reachable from a game in progress changes the active theme.
    *(`Theming.md` → Decisions → Can you change the theme mid-game: "No — leave it out for
    now. Theme changes happen from the main menu only"; corroborated by
    `design_handoff_game_ui/README.md` → 1f, "Themes live on the main menu — you can't
    switch mid-game".)*
    *Testable:* there is no route from the game screen or its quick-actions modal that
    reaches this overlay, and no theme control in either.

### Failure path

20. **If a theme fails to load, a modal is shown on the theme selection overlay** saying
    the theme is unavailable and asking the player to try another theme.
    *(`Theming.md` → Decisions → What happens if a theme fails to load: "From the Theme
    screen if a theme fails to load put up a modal with sorry this theme is unavailable
    please try another theme"; restated in `themes.catalog.json` → `failureBehavior`.)*

21. **After that modal, the app falls back to Neon**, which becomes the active theme, and
    the overlay reflects Neon as the highlighted row.
    *(`Theming.md` → Decisions → What happens if a theme fails to load: "Then fallback to
    neon".)*
    *Testable:* force a load failure for the selected theme, and after the modal is
    dismissed the active theme is Neon and the Neon row carries the active treatment.

### Presentation

22. **Every value used to draw the overlay comes from the active theme** — colors,
    background, fonts, button styling, sounds and motion. Nothing on this screen is
    hardcoded.
    *(`Theming.md` → Architectural Rule; → What a Theme Controls → Visual, "Main menu
    styling (background, button look, title)"; `Menus and UI.md` → Main Menu: "The entire
    main menu is itself theme-driven ... No hardcoded styling here either".)*
    *Testable:* the hardcoded-theme-value test (`P1-05-theme-guard-test.md`) passes over
    this screen's source with the baseline at zero.

## Out of Scope

- **The theme system itself** — the theme object, YAML loading, UUID identity, and
  merge-over-Neon materialization, and what a theme contains: `P1-03-theme-system.md`.
- **Persisting the selected theme UUID** — the `shared_preferences` store, the key, and
  the default-on-empty-store read: `P1-04-persistence.md`.
- **The main menu** — its layout, title, logo, and the Theme button itself:
  `P3-01-main-menu.md`.
- **The Classic Red vs Blue theme's content** — its YAML file and the concrete values it
  overrides: `P4-04-classic-theme.md`. This PRD requires only that it be listed and
  selectable.
- **Purchasing, entitlements and restore** — the store SDK, what a price action opens, how
  an entitlement is granted, checked or restored, and localized pricing:
  `P4-05-in-app-purchases.md`. Requirements 10–14 cover only what this screen *displays*
  and what it refuses to apply. Note `themes.catalog.json` → `storeRequirements`: prices
  must be read from the store SDK at runtime and never hardcoded — the `$1.99` in the
  handoff is mock data.
- **Any paid theme's content.** No paid theme exists. `design_handoff_game_ui/README.md` →
  2a marks Splat and Dinosaurs as placeholders that "do not exist" and says "Do not ship
  them as designed"; Requirement 13 is satisfied with fixtures, not with those two.
- **The settings page's read-only "Theme — Picked from the main menu" display**
  (`design_handoff_game_ui/README.md` → 2b): that belongs to the settings PRD. It is not a
  second entry point and does not change Requirement 19.
- **Audio playback**, including whatever sound a menu tap makes: `P4-01-audio.md`. This
  PRD fixes only that such values come from the theme (Requirement 22).
- **What counts as "fails to load", and what happens if *Neon* fails to load.** Both are
  already flagged as unresolved in `P1-03-theme-system.md` → Open Questions and are that
  PRD's to settle; this PRD specifies only what the player is shown once a failure is
  reported to it.

## Open Questions

### 1. What the handoff draws vs. what ships — the remaining half of the contradiction

The free-vs-paid half of this contradiction is **settled** and is now Requirements 10–14:
themes are labeled free or paid, Neon and Classic are the two free ones, everything beyond
them is paid (`Theming.md` → Decisions → Are themes unlockable/rewards, → Which themes are
free). What is still unresolved is **how many rows the list shows**, and this PRD picks
neither side:

- `design_handoff_game_ui/README.md` → *2a* draws **four** theme rows — Neon, Classic,
  Splat and Dinosaurs — and headers the sheet **"Two free, two extra. Switch any time."**
- `Theming.md` → Decisions → How many themes ship at launch says **"Two — Neon and Classic
  Red vs Blue"**, and `Menus and UI.md` → Theme Selection and → Screens (so far) → 5 say
  the same. Requirement 5 follows those two docs.

The handoff itself calls Splat and Dinosaurs placeholders that "do not exist" and says "Do
not ship them as designed", so the four-row drawing is not obviously an instruction. But
the paid direction is now decided, which makes *some* future paid theme expected, and
nothing states which paid themes ship or when. Left open:

- Does the launch list show two rows, or four with two of them unbuilt placeholders?
- Is the header sub-copy "Two free, two extra. Switch any time." — which describes the
  four-row layout — the copy for a two-row list, or does it change?

### 2. From `Theming.md` → Open Questions

- Which values, concretely, does Classic Red vs Blue override? (Settled in principle —
  graphics and its splat sound, inheriting the rest. An exact list will fall out when it's
  actually built.)

This lands on Requirement 6: the Classic preview tile renders in "that theme's own colors
and marks", and until the overrides are authored the only concrete values are the
`previewColors` in `themes.catalog.json`.

### 3. From `Tech Design.md` → Open Questions → 2. Theme loading

- Are all themes loaded and materialized at startup, or only the selected one, on demand?
  `Theming.md` → Why this matters for the build says materialization happens "at startup"
  but does not say for how many themes.

This sits directly on Requirement 7 — the preview tiles need every listed theme's values,
not just the active one's.

### 4. Gaps found while writing this PRD (raised by the PRD author, not asked by the docs)

Each is something an implementer would otherwise have to guess. None is resolved here.

- **The failure modal is not designed.** `design_handoff_game_ui/README.md` → *Still to
  design* → 3 lists "The 'theme failed to load' modal (`Theming.md`: apologise, then fall
  back to Neon)" as undrawn. Requirements 20 and 21 fix the behavior and the message's
  content; its layout, its dismiss control and whether it offers any action beyond
  acknowledging have no approved design.
- **Where the failure modal goes when the failure happens at launch.** The decision is
  worded "*From the Theme screen* if a theme fails to load" — but the persisted theme is
  loaded at startup, before the player has opened this overlay. Whether the app opens the
  overlay to show the modal, shows it on the main menu, or falls back to Neon silently
  until the player next opens theme selection is not stated anywhere.
- **What tapping the already-active row does.** Re-apply and close, or nothing. The docs
  describe selecting a theme, not re-selecting the current one.
- **Whether tapping the scrim outside the sheet dismisses the overlay.** The handoff gives
  a close icon button (Requirement 3) and does not say whether the scrim is also a dismiss
  target.
- **The order of the rows.** The handoff lists Neon first; nothing states whether order is
  catalog order, alphabetical, active-first, or free-before-paid, which starts to matter as
  themes are added (Requirement 4).
