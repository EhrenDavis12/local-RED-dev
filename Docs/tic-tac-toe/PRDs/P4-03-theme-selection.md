# PRD: Theme Selection

> **Status:** Draft · Source docs read: `Menus and UI.md`, `Theming.md`, `Tech Design.md`,
> `Game Overview.md`, `Game Board Design.md`, `Animations.md`, `roadmap.md`, and the
> read-only reference asset `design_handoff_game_ui/` (`README.md` → *2a — Theme Select*,
> `themes.catalog.json`, `neon.theme.json`). `Alternative Game Styles.md` is a declared
> parking-lot doc and was not used as a source.
>
> **Revised** after `Theming.md` → Decisions → *Are themes unlockable/rewards* was
> rewritten and → *Which themes are free* was added. The free-vs-paid question this PRD
> previously carried as an open contradiction is now decided and appears in Requirements
> 10–14.
>
> **Revised again** by round-2 review: Requirements 16 and 20 no longer collide on an
> in-session load failure, Requirements 6 and 8 were tightened against implementations that
> passed the wording and missed the drawing, Requirement 14's testable is scoped, and
> Requirement 23 names the slots this screen needs that `P1-03-theme-system.md` Requirement
> 15 does not yet carry. **Requirements 1–22 were not renumbered** — `P1-03`, `P1-07` and
> `P4-05` cite several of them by number.
>
> **Revised a third time** after `Menus and UI.md` → Decisions → *Where the open-game slot
> unlock is sold* and `Tech Design.md` → Decisions → *Entitlements — Apple stores them, no
> backend needed* were added. Requirement 14's absent purchase and restore controls are now
> backed by a Decision rather than by a reading, and Open Question 5 is closed. No
> requirement changed its meaning.

**Wave:** P4 · **File:** `P4-03-theme-selection.md`

**Depends on:**

- `P1-03-theme-system.md` — the theme object, its UUID identity, merge-over-Neon
  materialization, the catalog (its req 32), the non-active read path (its req 33), the
  reportable load failure (its req 34), and the slots this screen reads. This PRD consumes
  that layer and defines none of it. Requirement 23 below names what its Requirement 15
  inventory still has to grow to cover.
- `P1-04-persistence.md` — storing and restoring the selected theme's UUID. This PRD
  requires that a selection be handed to that layer; it does not specify the storage.
- `P1-07-entitlements.md` — the per-theme `free` / `owned` / `locked` state this screen
  renders labels from (its req 4). Wave 1, so it exists before this screen does. This
  screen **reads** entitlement state; it never implements buying.
- `P2-01-navigation.md` — the rule that this overlay opens over a main menu that stays
  mounted, and the two operations this screen invokes: `openThemeSelection()` and
  `dismissCurrent()` (its **requirement 6**, and the operation table in its requirement 3).
- `P4-01-main-menu.md` — the main menu this overlay opens on top of, including the Theme
  button that opens it. Same wave, parallel-safe.

**Same-wave siblings:** `P4-05-purchase-flow.md` owns buying and restoring, both as
screen-agnostic invocable operations, and `P4-04-settings.md` hosts the controls that
invoke them — `Menus and UI.md` → Decisions → *Where the open-game slot unlock is sold*
settles that the Settings screen carries the purchases section holding the $4.99 unlock and
the global **Restore purchases** control. This screen hosts neither (Requirement 14), so
all three are parallel-safe within wave 4, and that is now a Decision rather than a
provisional reading. See Open Question 5, which this closed.

**Later wave:** `P5-01-classic-theme.md` authors the second theme this screen lists. This
screen ships first; until that PRD lands, the Classic row has a name and a UUID but no
authored overrides.

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
the screen. If a theme cannot be loaded, they are told so on the overlay they are standing
on and put back on Neon rather than left on a broken screen.

## Requirements

### Where it lives and how it opens

1. **Theme selection is an overlay on the main menu, not its own screen.** The main menu
   remains present behind it. It is presented by `P2-01-navigation.md`'s
   **`openThemeSelection()`**, not by a route this screen constructs.
   *(`Menus and UI.md` → Decisions → Is theme selection its own screen or an overlay?;
   → Screens (so far) → 5; `Theming.md` → Decisions → Where theme selection lives;
   corroborated by `design_handoff_game_ui/README.md` → 2a, "never its own screen";
   `P2-01-navigation.md` reqs 3 and 6.)*
   *Testable:* opening theme selection does not replace the main menu route; the menu is
   still mounted and visible behind the overlay's scrim.

2. **The overlay is opened by the Theme button on the main menu**, and by nothing else —
   that button is the only caller of `openThemeSelection()`.
   *(`Menus and UI.md` → Main Menu; → Theme Selection; `P2-01-navigation.md` req 6.)* The
   button's placement, size and equal-to-Play-Game weight belong to `P4-01-main-menu.md`.

3. **The overlay can be dismissed without changing the active theme**, via the close
   control in its header, which invokes **`dismissCurrent()`**.
   *(`design_handoff_game_ui/README.md` → 2a, header: "close icon button right";
   `P2-01-navigation.md` reqs 3 and 6, whose test is that `dismissCurrent()` reveals the
   same still-mounted menu rather than constructing a new one.)*
   *Testable:* open the overlay via `openThemeSelection()`, close it via `dismissCurrent()`,
   and the active theme UUID is unchanged. Naming both operations is what keeps this screen
   inside `P2-01-navigation.md` requirement 1's scan — a close performed with a bare
   `Navigator` call would pass this test and fail that one.

### What it lists

4. **The list is built from the app's theme catalog, not from a hardcoded pair of rows.**
   Adding a theme definition must add a row with no change to menu code.
   *(`Theming.md` → Architectural Rule: "Adding a new theme should require zero changes to
   game/board/menu code — only adding a new theme definition"; the catalog itself is
   `P1-03-theme-system.md` req 32.)*
   *Testable:* adding a third theme definition makes a third row appear with no edit under
   the menu UI source.

5. **Two themes are listed at launch: Neon and Classic Red vs Blue.**
   *(`Theming.md` → Decisions → How many themes ship at launch; `Menus and UI.md` → Theme
   Selection, → Screens (so far) → 5.)* See also Open Question 1 — the approved handoff
   still draws four.

6. **Each row shows a preview tile, the theme's name, and a one-line description.** The
   preview tile is a **miniature quadrant rendered in that theme's own colors and marks**:
   it draws that theme's grid lines and at least one mark of each player, in that theme's
   mark art, so that two themes side by side are told apart by the tile alone. An empty
   grid, or a grid drawn in the *active* theme's colors, does not satisfy this.
   *(`design_handoff_game_ui/README.md` → 2a: "a 66×66 preview tile (a miniature quadrant
   rendered in that theme's own colors and marks), the name, and a one-line description in
   the theme's voice"; per-theme `blurb` values in `themes.catalog.json`; mark art is
   `P1-03-theme-system.md` req 16.)*
   *Testable:* with Neon active, the Classic row's tile renders Classic's ground and both
   its player marks, and no pixel of it resolves to a Neon color.
   *Not settled — see Open Question 4:* **which** cells hold marks and whose. The handoff
   describes the tile in one clause and its drawn arrangement is not written down anywhere,
   so this requirement fixes what the tile must distinguish, not its exact composition.

7. **The preview tile is the one place in the app that reads a non-active theme's values.**
   Rendering a row must not require making that theme active.
   *(`design_handoff_game_ui/README.md` → 2a; the read path is `P1-03-theme-system.md`
   req 33.)* What that costs at load time is Open Question 3.

8. **The currently active theme is highlighted in the list**, so it is obvious which one is
   in use before the player changes anything. The active row carries **both** treatments the
   handoff draws — the ring (`0 0 0 2px` in the active-ring color plus its glow) **and** an
   `ACTIVE` tag — and it **keeps its ownership tag as well**, so an active free theme shows
   `ACTIVE` and `FREE` together. A ring alone, or a tag alone, is not this requirement.
   *(`Menus and UI.md` → Decisions → How does theme selection show which theme is in use?;
   → Theme Selection; `design_handoff_game_ui/README.md` → 2a → Ownership states, whose
   Active row reads "`ACTIVE` tag (blue) **and** its ownership tag"; `themes.catalog.json`
   → `activeBadge`.)*
   *Testable:* with Neon active, the Neon row carries the ring, the `ACTIVE` tag and the
   `FREE` tag, and the Classic row carries neither ring nor `ACTIVE` tag; after switching,
   both active treatments move together to the Classic row.

9. **Before a player has ever opened theme selection, Neon is the active theme**, and the
   first time the overlay is opened Neon is the highlighted row.
   *(`Menus and UI.md` → Decisions → Which theme is active by default?; `Theming.md` →
   Neon Is the Base Theme; `themes.catalog.json` → `defaultThemeId`;
   `P1-03-theme-system.md` req 14.)*
   *Testable:* on a device with nothing stored, open the overlay — Neon reads as active.

### Free and paid

10. **The list labels which themes are free and which are paid.** Every row carries exactly
    one **ownership** label — `FREE`, `OWNED`, or a locked row's price action in place of a
    tag. The `ACTIVE` tag of Requirement 8 is not an ownership label and does not replace
    one.
    *(`Theming.md` → Decisions → Which themes are free: "The theme selection list
    **labels** which themes are free and which are paid"; → Are themes unlockable/rewards:
    "Yes — some themes are paid ... We will label what themes are free".)*
    *Testable:* every rendered row carries exactly one ownership label; the active row
    carries that label plus the `ACTIVE` tag, for two tags total.

11. **Neon and Classic Red vs Blue are free. Every theme beyond those two is paid.**
    *(`Theming.md` → Decisions → Which themes are free; `P1-07-entitlements.md` reqs 1
    and 2.)*
    *Testable:* both rows that ship render the free label; a fixture theme outside those
    two UUIDs does not.

12. **The label is driven by entitlement state read per theme, not by a field inside the
    theme definition.** A theme file carries no ownership or price value. What this screen
    reads is the entitlement layer's answer; **Apple is the record of truth behind it** —
    `Transaction.currentEntitlements` is the authoritative answer to "does this player own
    this", and any locally held copy is an offline convenience, not the record. That is a
    doc-backed boundary rather than a premise this PRD assumes, and it does not change what
    this screen does: it renders whatever `P1-07-entitlements.md` reports, per theme.
    *(`design_handoff_game_ui/themes.catalog.json` → `note`: "Ownership is NOT part of a
    theme definition — a theme is an audio-visual package; entitlement is account/device
    state"; `design_handoff_game_ui/README.md` → 2a: "keep purchase state **out of the
    theme definition**"; `Tech Design.md` → Decisions → Entitlements — Apple stores them, no
    backend needed; consistent with `P1-03-theme-system.md` → Requirement 31 and
    `P1-07-entitlements.md` → Requirement 5.)*
    *Testable:* no shipped theme YAML contains an ownership or price key; changing the
    entitlement a row is given changes its label with no edit to any theme file.

13. **The row supports the ownership states `free`, `owned` and `locked` without reshaping
    the screen**, with the treatments the handoff specifies — `FREE` and `OWNED` tags, and
    for a locked row a dimmed preview tile and a price action in place of a tag. A locked
    row must still render its preview and must read as buyable, not broken. Attaching a
    price to a theme must not require changing the row's layout.
    *(`design_handoff_game_ui/README.md` → 2a → Ownership states — the part to build
    carefully: "Build the theme list so an `ownership` field (`free | owned | locked`) and
    a price can be attached per theme without reshaping the screen";
    `themes.catalog.json` → `ownershipStates` and `storeRequirements`. The three states
    themselves are `P1-07-entitlements.md` → Requirement 4; that a locked theme still
    renders its preview is its Requirement 6.)*
    *Testable:* a fixture theme in each of the three states renders its specified treatment
    through the same row widget.

14. **A theme the player is not entitled to cannot be applied from this screen**, and **no
    purchase or restore control is surfaced on this screen.** Both themes that ship are
    free, so no row can be locked and there is nothing here to sell: the price button, the
    purchase sheet and the *Restore purchases* footer drawn on handoff `2a` have no product
    behind them on this screen. This screen reads entitlement and renders labels; buying and
    restoring are operations owned by `P4-05-purchase-flow.md`, and this screen invokes
    neither.
    *(`Theming.md` → Decisions → Which themes are free + → How many themes ship at launch;
    **`Menus and UI.md` → Decisions → Where the open-game slot unlock is sold: "The Settings
    screen. The Settings screen gains a purchases section holding the $4.99 open-game-slot
    unlock and a global Restore purchases control … it keeps the purchase flow off the other
    menu screens";** `themes.catalog.json` → `ownershipStates.locked.playable: false`;
    `P1-07-entitlements.md` → Requirements 2 and 6; `P4-05-purchase-flow.md` → Requirement
    9, "at launch the catalog contains zero locked themes".)*
    *Testable — **scoped to this screen's widget tree, not to the app**:* with only the two
    shipped themes installed, no descendant of the theme-selection overlay renders a price
    action, a purchase control or a restore control, and no descendant invokes
    `P4-05-purchase-flow.md`'s purchase or restore operation; a fixture locked theme cannot
    be applied by tapping its row.
    **Why the absence is correct, and why the test is scoped.** It is a Decision, not an
    inference: the purchases section and the global *Restore purchases* control live on the
    Settings screen (`P4-04-settings.md`), explicitly to keep the purchase flow off the
    other menu screens. The assertion is therefore deliberately not an app-wide source scan
    — the restore control exists in the build, one screen over, and an app-wide absence scan
    would fail the moment `P4-04-settings.md` lands. Nothing here contradicts
    `P4-05-purchase-flow.md` Requirement 5, which makes the restore *operation*
    unconditional: that requirement obligates an operation, this one places its control
    elsewhere.

### Selecting a theme

15. **Selecting a theme applies it.** The change takes effect immediately, not on restart.
    *(`Menus and UI.md` → Theme Selection: "Selecting a theme applies it".)*
    *Testable:* select Classic Red vs Blue and the main menu behind the overlay renders in
    Classic's values without an app restart.

16. **Selecting a theme that applies successfully closes the overlay**, returning the
    player to the main menu via `dismissCurrent()`.
    *(`design_handoff_game_ui/README.md` → 2a: "tapping a free or owned row applies the
    theme and closes the overlay"; `P2-01-navigation.md` req 3.)*
    **The close is conditional on the apply succeeding.** Selection is the only moment a
    theme loads in-session, so a failed load and a close would otherwise fire together and
    leave Requirement 20's modal with no overlay to sit on. The handoff sentence describes
    the success path — it applies *and* closes — and `Theming.md` puts the failure modal on
    the Theme screen, which is only possible if the overlay is still there. Requirement 20
    therefore takes precedence on the failure path.
    *Testable:* a successful selection closes the overlay; a selection whose theme fails to
    load leaves it open.

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
    buzzes".)* The mechanism is `P2-03-haptics.md`'s, which records at its OQ-2 that
    whether non-board controls buzz at all is unsettled.

### Where it is *not* available

19. **The theme can be changed from the main menu only — there is no mid-game theme
    change.** No control reachable from a game in progress changes the active theme.
    *(`Theming.md` → Decisions → Can you change the theme mid-game: "No — leave it out for
    now. Theme changes happen from the main menu only"; corroborated by
    `design_handoff_game_ui/README.md` → 1f, "Themes live on the main menu — you can't
    switch mid-game".)*
    *Testable:* there is no route from the game screen or its quick-actions modal that
    reaches this overlay, and no theme control in either.
    `P2-01-navigation.md` requirement 11 asserts the same constraint in the routing graph.

### Failure path

20. **If a theme fails to load, a modal is shown on the theme selection overlay** saying
    the theme is unavailable and asking the player to try another theme. **The overlay stays
    open underneath it** — the modal is drawn on the Theme screen, which is what the
    decision says, and Requirement 16's close does not fire on this path.
    *(`Theming.md` → Decisions → What happens if a theme fails to load: "From the Theme
    screen if a theme fails to load put up a modal with sorry this theme is unavailable
    please try another theme"; restated in `themes.catalog.json` → `failureBehavior`. The
    loader reports which theme failed — `P1-03-theme-system.md` req 34 — and this screen
    consumes that report.)*
    *Testable:* force a load failure for a selected theme; the modal appears and the
    overlay is still mounted beneath it.

21. **After that modal, the app falls back to Neon**, which becomes the active theme, and
    the overlay reflects Neon as the highlighted row.
    *(`Theming.md` → Decisions → What happens if a theme fails to load: "Then fallback to
    neon"; `P1-03-theme-system.md` reqs 27–28.)*
    *Testable:* force a load failure for the selected theme, and after the modal is
    dismissed the active theme is Neon and the Neon row carries the active treatment of
    Requirement 8.
    *Not settled — see Open Question 4:* whether the overlay then stays open on that
    Neon-active list or closes itself once the modal is dismissed. This requirement's test
    reads the row, so it presumes the overlay is still there; nothing in the docs says
    whether it should remain.

### Presentation

22. **Every value used to draw the overlay comes from the active theme** — colors,
    background, fonts, button styling, sounds and motion. Nothing on this screen is
    hardcoded. The preview tiles of Requirement 6 are the single exception, and they read
    another *theme*, not a constant.
    *(`Theming.md` → Architectural Rule; → What a Theme Controls → Visual, "Main menu
    styling (background, button look, title)"; `Menus and UI.md` → Main Menu: "The entire
    main menu is itself theme-driven ... No hardcoded styling here either";
    `P1-03-theme-system.md` req 25.)*
    *Testable:* the hardcoded-theme-value test (`P1-05-theme-guard-test.md`) passes over
    this screen's source with the baseline at zero.

23. **The values below are what Requirement 22 obliges this screen to read from the theme,
    and `P1-03-theme-system.md` Requirement 15 does not carry a slot for them today.** They
    are listed precisely because that PRD consumes these lists: its Requirement 15 names a
    badges slot but no values exist for it, and its Requirement 13 — the list of what
    `neon.theme.json` is known to be missing — does not mention badges at all, so these
    values are today neither authored nor on any gap list. Requirement 22 and
    `P1-05-theme-guard-test.md` make that gap a build failure rather than a cosmetic one.
    *(All values from `design_handoff_game_ui/README.md` → *2a* and
    `themes.catalog.json` → `activeBadge`, `ownershipStates`; checked against
    `neon.theme.json`.)*

    **The theme row** — distinct from `P4-02-open-games-list.md`'s open-game row, which the
    handoff draws at fill `#1e2131`, radius 13, padding `15/16`. These are different values
    for a different row and one slot cannot serve both:
    - row fill `#161826`, **radius 14**, padding 14, internal gap 14;
    - row border, free and owned: `inset 0 0 0 1px #3f424d`; locked: `inset 0 0 0 1px
      #2b2f42`;
    - preview tile size 66×66, and the **locked tile's 45% opacity**;
    - the **active ring** itself: `0 0 0 2px #4fc3ff` plus glow
      `0 0 22px rgba(79,195,255,0.30)`.

    **Badge and price-action values** — the styling is a theme slot; which badge a row gets
    is entitlement state and is not (`P1-03-theme-system.md` req 31):
    - `ACTIVE`: background `rgba(79,195,255,0.18)`, text `#a9e4ff`;
    - `FREE`: background `#292b31`, text `#9397ab`;
    - `OWNED`: background `rgba(45,255,158,0.16)`, text `#a5ffd8`;
    - all tags **9.5pt, tracking 0.1em**;
    - price action: accent outline 2pt `#9184d9`, **radius 11**, padding `9/13`, 14pt, with
      a padlock icon.

    **Sheet chrome not covered by the sheet-surface slot:**
    - the **behind-menu dim — the main menu drops to 35% opacity** behind the overlay. This
      is distinct from the scrim (`rgba(15,16,24,0.72)`, which is Neon's `scrimHeavy`): one
      reduces the opacity of the content beneath, the other is a layer painted over it, and
      the handoff specifies both on this screen.
    - the sheet **header type**: title **20/600** and sub-copy **11.5pt**, neither of which
      exists in Neon's `type.scale` (nearest are `subhead` 22/600, `label` 12/400 and
      `caption` 11/400).

    **Near-misses an implementer will reach for, that the guard will not catch.** Each of
    these resolves to a real value in `neon.theme.json`, so substituting it produces code
    that reads correctly, renders wrongly, and passes `P1-05-theme-guard-test.md`:

    | This screen needs | Nearest existing Neon key | Why it is not the same |
    |---|---|---|
    | `rgba(45,255,158,0.16)` — `OWNED` background | `playerTwoTint` `rgba(45,255,158,0.12)` | same hue, different alpha |
    | `rgba(79,195,255,0.30)` — active ring glow | `boardLineGlow` `rgba(79,195,255,0.90)` | same hue, three times the alpha |
    | radius **11** — price action | `radius.chip` 10, `radius.control` 12 | 11 is absent from Neon's radius set |
    | 9.5pt / 0.1em — all tags | `chipLabel` 9 / 0.1 | half a point apart, and not uppercase-locked |

    Some values here do resolve to colors Neon already defines (`#161826` is `ground`,
    `#3f424d` is `hairlineStrong`, `#2b2f42` is `hairline`, `#9397ab` is `textSubtle`) —
    but nothing names them *for this use*, and two of them (`#292b31`, `#a9e4ff`) appear
    nowhere in `neon.theme.json` at all. Whether each becomes its own slot or an alias of an
    existing one is `P1-03-theme-system.md`'s call, not this PRD's; what this requirement
    fixes is that the values are needed and are not currently reachable.

## Out of Scope

- **The theme system itself** — the theme object, YAML loading, UUID identity,
  merge-over-Neon materialization, the catalog, the non-active read path and the
  failure report: `P1-03-theme-system.md`. Requirement 23 names values that screen needs;
  designing the slots that hold them is that PRD's.
- **Persisting the selected theme UUID** — the `shared_preferences` store, the key, and
  the default-on-empty-store read: `P1-04-persistence.md`.
- **The entitlement model** — what the three ownership states mean, the free-tier defaults
  and the per-theme query this screen reads: `P1-07-entitlements.md`. Requirements 10–14
  cover only what this screen *displays* and what it refuses to apply.
- **The navigation layer** — the routing approach, and what `openThemeSelection()` and
  `dismissCurrent()` do underneath: `P2-01-navigation.md`. This screen invokes them.
- **The main menu** — its layout, title, logo, and the Theme button itself:
  `P4-01-main-menu.md`.
- **The Classic Red vs Blue theme's content** — its YAML file and the concrete values it
  overrides: `P5-01-classic-theme.md`. This PRD requires only that it be listed and
  selectable.
- **The Settings screen's purchases section** — the $4.99 open-game-slot unlock and the
  global *Restore purchases* control both live there, not here: `P4-04-settings.md`
  (`Menus and UI.md` → Decisions → Where the open-game slot unlock is sold).
- **Purchasing and restore** — the store SDK, the purchase and restore operations, what a
  price action opens, and localized pricing: `P4-05-purchase-flow.md`. Worth stating
  precisely, because it is easy to read backwards: **the restore control is a compliance
  requirement, not the mechanism by which entitlements arrive.** Entitlements come from
  Apple — `Transaction.currentEntitlements`, verified on device — and restore for
  non-consumables is largely automatic, with signing in on a new device repopulating them
  without the player doing anything; the visible control exists because Apple's review
  guidelines require it, with `AppStore.sync()` behind it (`Tech Design.md` → Decisions →
  Entitlements — Apple stores them, no backend needed). Note also `themes.catalog.json` →
  `storeRequirements`: prices must be read from the store SDK at runtime and never
  hardcoded — the `$1.99` in the handoff is mock data.
- **The parental gate.** `Tech Design.md` → Decisions → Kids category requires one before
  any purchase flow, and names theme selection as a feature it reaches. It has no trigger on
  this screen today, because Requirement 14 surfaces no purchase entry point here. If a
  locked theme's price action is ever surfaced on this overlay, the gate must precede it —
  that is a consequence to carry into whichever PRD hosts the purchase, not work this one
  specifies.
- **Any paid theme's content.** No paid theme exists. `design_handoff_game_ui/README.md` →
  2a marks Splat and Dinosaurs as placeholders that "do not exist" and says "Do not ship
  them as designed"; Requirement 13 is satisfied with fixtures, not with those two.
- **The settings page's read-only "Theme — Picked from the main menu" display**
  (`design_handoff_game_ui/README.md` → 2b): that belongs to `P4-04-settings.md`. It is not
  a second entry point and does not change Requirement 19.
- **Audio playback**, including whatever sound a menu tap makes: `P2-02-audio.md`. This
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
`previewColors` in `themes.catalog.json`. Owned by `P5-01-classic-theme.md`.

### 3. From `Tech Design.md` → Open Questions → 2. Theme loading

- Are all themes loaded and materialized at startup, or only the selected one, on demand?
  `Theming.md` → Why this matters for the build says materialization happens "at startup"
  but does not say for how many themes.

This sits directly on Requirement 7 — the preview tiles need every listed theme's values,
not just the active one's. `P1-03-theme-system.md` req 33 sharpens it without settling it.

### 4. Gaps found while writing this PRD (raised by the PRD author, not asked by the docs)

Each is something an implementer would otherwise have to guess. None is resolved here.

- **The failure modal is not designed.** `design_handoff_game_ui/README.md` → *Still to
  design* → 3 lists "The 'theme failed to load' modal (`Theming.md`: apologise, then fall
  back to Neon)" as undrawn. Requirements 20 and 21 fix the behavior, the sequencing and
  the message's content; its layout, its dismiss control and whether it offers any action
  beyond acknowledging have no approved design.
- **What the overlay does after the failure modal is dismissed.** Requirement 20 settles
  that the overlay stays open *under* the modal, because the decision puts the modal on the
  Theme screen. What the docs do not say is what happens next: stay open showing Neon as
  active — which is what Requirement 21's test assumes and what "please try another theme"
  implies — or close along with the modal.
- **Where the failure modal goes when the failure happens at launch.** The decision is
  worded "*From the Theme screen* if a theme fails to load" — but the persisted theme is
  loaded at startup, before the player has opened this overlay. Whether the app opens the
  overlay to show the modal, shows it on the main menu, or falls back to Neon silently
  until the player next opens theme selection is not stated anywhere.
- **The preview tile's exact composition.** Requirement 6 fixes that the tile renders the
  theme's own grid lines and both players' marks, which is what the handoff's clause
  requires and what makes two themes distinguishable. Which of the nine cells hold marks,
  and in what arrangement, is drawn but not written down — so two implementations can both
  satisfy the requirement and look different.
- **The theme's display name and blurb have nowhere to live.** Requirement 6 needs a name
  and a one-line description per theme; today both exist only in `themes.catalog.json`, a
  handoff reference asset that ships nowhere, and `P1-03-theme-system.md` → Open Questions
  records that the theme schema has no place for them.
- **What tapping the already-active row does.** Re-apply and close, or nothing. The docs
  describe selecting a theme, not re-selecting the current one.
- **Whether tapping the scrim outside the sheet dismisses the overlay.** The handoff gives
  a close icon button (Requirement 3) and does not say whether the scrim is also a dismiss
  target. Related to `P2-01-navigation.md` → Open Question 10 on whether a sheet is a route.
- **The order of the rows.** The handoff lists Neon first; nothing states whether order is
  catalog order, alphabetical, active-first, or free-before-paid, which starts to matter as
  themes are added (Requirement 4).

### 5. Answered — the Settings screen hosts the purchase and restore controls

**Closed.** Kept as a stub rather than deleted so the trail stays visible and the numbering
of the questions around it stays stable.

This question asked whether this overlay hosts the *Restore purchases* affordance, and
recorded a real gap alongside it: that **no requirement in any of the 24 PRDs surfaced a
restore control anywhere**, while the $4.99 open-game slot unlock ships and is on sale.
`P4-05-purchase-flow.md` Requirement 9 had conceded the equivalent gap for the purchase
entry point and made no equivalent concession for restore.

**Both halves are now settled by one Decision.** `Menus and UI.md` → Decisions → *Where the
open-game slot unlock is sold*: "**The Settings screen.** The Settings screen gains a
purchases section holding the $4.99 open-game-slot unlock and a global **Restore purchases**
control. This is the conventional iOS placement, it keeps one parental gate in one place,
and it keeps the purchase flow off the other menu screens." So:

- **The gap is closed.** `P4-04-settings.md` owns the restore control and the purchase entry
  point; neither is missing from the PRD set any more.
- **Requirement 14 is now doc-backed.** This screen surfacing no purchase or restore control
  is the Decision's explicit intent — keeping the purchase flow off the other menu screens —
  rather than the conditional argument this PRD previously had to fall back on.
- **Requirement 14's test stays screen-scoped**, and now must be: the restore control will
  exist in the build, one screen over.
- **Wave-4 parallelism is no longer contingent.** `P4-03`, `P4-04` and `P4-05` divide
  cleanly: this screen labels, Settings hosts the controls, and the purchase flow owns the
  operations behind them.
