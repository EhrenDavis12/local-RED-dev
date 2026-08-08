**Build-readiness: 95**

# PRD: Theme Selection

> **Status:** Draft · Source docs read: `Menus and UI.md`, `Theming.md`, `Tech Design.md`,
> `Game Overview.md`, `Game Board Design.md`, `Animations.md`, `roadmap.md`, and the
> read-only reference asset `design_handoff_game_ui/` (`README.md` → *2a — Theme Select*,
> `themes.catalog.json`, `neon.theme.json`). `Alternative Game Styles.md` is a declared
> parking-lot doc and was not used as a source.
>
> **Revised for build-readiness.** Requirement 23 was **false in every clause** and is
> rewritten around `P1-03-theme-system.md`'s published key paths. Requirements 10–14 name
> `P1-07-entitlements.md`'s published surface. Requirement 24 names this screen's file,
> widget and source root. Five citations to `P2-01-navigation.md` were repointed. The price
> action's behaviour is settled in Requirement 14, and every item in Open Question 4 carries
> a build default.
>
> **Revised** after `Theming.md` → Decisions → *How are themes discovered…* and → *Do themes
> control the app's chrome icons?*; then after → *Does a theme control spacing and padding?*
> (**no** — Requirement 22 excepts spacing, Requirement 23 drops two removed keys); then
> after `Game Board Design.md` → Decisions → *Does the haptic fire on non-board controls?*
> (**yes, app-wide** — Requirement 18 ratified).
>
> **Revised again** after `Theming.md` → Decisions → *Do non-board controls make a sound?* —
> **one tap sound, everywhere**, naming theme rows. **Requirement 25 is new**: this screen
> owns its `buttonTap` call sites, which the Out of Scope previously routed away to
> `P2-02-audio.md` while that PRD's OQ-3 was open. With that question closed the routing left
> the sound unowned, and no PRD would have built it.
>
> **Why 95:** both feedback channels are now owned and asserted at this screen's call sites,
> and every value, operation and type it touches is a published name owned by another PRD.
> The remaining gap is unchanged and is not interface work: the failure modal is still
> undrawn, so an agent invents its layout; nine build defaults in Open Question 4 are the
> author's rather than the user's, two of them behavioural; and Open Question 1 is open,
> though it decides what ships in `assets/themes/` rather than anything in this screen's
> code.
>
> **Requirements 1–24 were not renumbered** — `P1-03`, `P1-07`, `P2-01`, `P2-02`, `P2-03` and
> `P4-05` cite several of them by number. **Requirement 25 is numbered last but belongs beside
> Requirement 18**, and is placed there in document order.

**Wave:** P4 · **File:** `P4-03-theme-selection.md`

**Depends on:**

- `P1-03-theme-system.md` — the schema (its req 15, schemaVersion 7), the deep-merge rule
  (req 8), theme discovery (req 32), the non-active read path and the reportable load
  failure. Every *themed* value this screen draws is a key path published there;
  Requirement 23 lists which ones, and Requirement 22 states what is deliberately not one.
- `P1-04-persistence.md` — storing and restoring the selected theme's UUID.
- `P1-07-entitlements.md` — its **Requirement 11** publishes the surface this screen reads:
  `entitlementsProvider`, `Entitlements.ownershipOf(String themeUuid)` and
  `enum ThemeOwnership { free, owned, locked }`. This screen reads that surface and calls no
  other entitlement symbol.
- `P2-01-navigation.md` — its **requirement 3** publishes `AppNavigator` with
  `openThemeSelection()` and `dismissCurrent()`; its **requirement 9** settles `/theme` as a
  **non-opaque child of `/`**, which is what keeps the menu mounted; its **requirement 5**
  defines `dismissCurrent()` as `if (router.canPop()) router.pop();`. Its route table
  (req 2) already names this screen's widget `ThemeSelectionOverlay` — Requirement 24.
- `P2-02-audio.md` — `audioLayerProvider`, `AudioLayer.play(SoundMoment)` and the
  `FakeAudioLayer` it publishes, for Requirement 25. Its req 6 owns the moment; this screen
  owns its call sites.
- `P2-03-haptics.md` — `HapticService.validAction()` and the `FakeHapticService` its req 15
  publishes, for Requirement 18. That PRD's OQ-2 is **closed**: the rule is app-wide, and it
  names this PRD among three ratified non-board callers.
- `P4-01-main-menu.md` — the main menu this overlay opens on top of, including the Theme
  button. Same wave, parallel-safe.

**Same-wave siblings:** `P4-05-purchase-flow.md` owns buying and restoring as
screen-agnostic invocable operations, and `P4-04-settings.md` hosts the controls that invoke
them — `Menus and UI.md` → Decisions → *Where the open-game slot unlock is sold* settles
that the Settings screen carries the purchases section and the global **Restore purchases**
control. This screen hosts neither (Requirement 14), so all three are parallel-safe.

**Later wave:** `P5-01-classic-theme.md` authors the second theme this screen lists,
including its `meta.name` and `meta.blurb`.

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

A player on the main menu taps **Theme** and gets an overlay, drawn over a still-mounted
menu, listing every theme file in the themes folder — each labeled free or paid, each
describing itself with its own name and one line of copy, with the currently active one
visibly highlighted before they touch anything. Picking one buzzes, clicks, applies it
immediately, and closes the overlay onto a menu now drawn in the new theme; the choice
survives closing the app. Neon is what they see before they have ever opened it. Both themes
that ship are free, so nothing here is buyable — but the row carries its ownership states
from day one, so a paid theme drops in without reshaping the screen. If a theme cannot be
loaded, they are told so on the overlay they are standing on and put back on Neon.

## Requirements

### Where it lives and how it opens

1. **Theme selection is an overlay on the main menu, not its own screen.** The main menu
   remains mounted and painted beneath it. It is presented by `AppNavigator`'s
   **`openThemeSelection()`**; this screen constructs no route and names no path.
   *(`Menus and UI.md` → Decisions → Is theme selection its own screen or an overlay?;
   → Screens (so far) → 5; `Theming.md` → Decisions → Where theme selection lives;
   `design_handoff_game_ui/README.md` → 2a, "never its own screen";
   `P2-01-navigation.md` **req 9**, which fixes `/theme` as a non-opaque child of `/`, and
   **req 3**, which publishes the operation.)*
   *Testable:* with the overlay open, the main menu widget is still in the tree; no route
   string and no `Navigator.` / `router.` call appears in this screen's source
   (`P2-01-navigation.md` req 1's scan).

2. **The overlay is opened by the Theme button on the main menu**, and by nothing else —
   that button is the only caller of `openThemeSelection()`.
   *(`Menus and UI.md` → Main Menu; → Theme Selection; `P2-01-navigation.md` **req 9**.)* The
   button's placement, size and equal-to-Play-Game weight belong to `P4-01-main-menu.md`.

3. **The overlay can be dismissed without changing the active theme**, via the close
   control in its header, which calls **`dismissCurrent()`** — specified as
   `if (router.canPop()) router.pop();`, so it is a no-op when nothing is dismissible.
   *(`design_handoff_game_ui/README.md` → 2a, header: "close icon button right";
   `P2-01-navigation.md` **req 5** for the operation, **req 3** for the interface.)*
   *Testable:* open via `openThemeSelection()`, close via `dismissCurrent()`, and the
   active theme UUID is unchanged while the router's location returns to `/`. Naming the
   operation is what keeps this screen inside `P2-01-navigation.md` req 1's scan — a close
   performed with a bare `Navigator` call would pass a behavioural test and fail that scan.
   The close control's glyph is `icons.close`, which is theme-supplied (Requirement 23); it
   buzzes and clicks like any other control (Requirements 18 and 25).

### What it lists

4. **The list is one row per theme file found in the themes folder.** Discovery is a scan
   of `assets/themes/`; adding a theme is dropping one file in, with no second file to edit
   and no change to this screen's source.
   *(`Theming.md` → Decisions → How are themes discovered, and does a theme file carry its
   own name and description?: "the app **discovers themes by scanning the themes folder**.
   Adding a theme is dropping one file in — no second file to edit, no code change … This
   rules out a separate catalog file as the source of truth, and it rules out a hardcoded
   list in Dart." The scan itself is `P1-03-theme-system.md` req 32; this screen consumes
   its result and performs no file I/O.)*
   *Testable:* dropping a valid theme file into `assets/themes/` and rebuilding adds a third
   row, with no edit under `lib/ui/menus/` (Requirement 24) and no entry added to any list
   in Dart.

   **What the player sees when a theme file is bad.** The scan makes malformed files
   reachable, and this screen is where they become visible or invisible — so it states the
   behaviour rather than leaving it to the loader's caller. What *counts* as a failure is
   `P1-03-theme-system.md`'s; how it is reported is that PRD's.

   - **The list always renders.** One unreadable file never blanks the overlay or prevents
     the other rows from appearing. This is the requirement; the two below are its defaults.
   - *Default for build, reversible:* **a file that fails to parse is omitted from the
     list.** A row cannot be drawn without that file's `meta.name`, `meta.blurb` and preview
     values, and no "broken row" treatment is drawn anywhere in the handoff — Requirement 13
     draws an unowned row as *buyable*, not as damaged. The cost is that a theme author sees
     silence rather than an error, which is worth a look once themes are authored by hand.
   - *Default for build, reversible:* **a duplicated `meta.id` never produces two rows, and
     is never resolved by scan order.** Two files claiming one UUID make the persisted
     selection ambiguous (`P1-04-persistence.md` stores the UUID), and picking by directory
     order would resolve it differently on different platforms. Every file sharing a
     duplicated id is omitted and the duplication is reported. **If the duplicated id is
     Neon's**, that is the "what if Neon fails" case in `P1-03-theme-system.md` and is
     escalated, not answered here.

5. **Two themes ship at launch: Neon and Classic Red vs Blue**, identified by the UUIDs
   `P1-07-entitlements.md` req 12 fixes as the free set —
   `b7c1f0a6-2f5e-4d3a-9c88-0f5a1e2d3c40` and `3d1a8b52-9c47-4b16-8f2e-7a5d0c9e1b34`.
   *(`Theming.md` → Decisions → How many themes ship at launch; `Menus and UI.md` → Theme
   Selection, → Screens (so far) → 5.)* How many rows appear is now a property of **what is
   in the folder** (Requirement 4), so Open Question 1 — the handoff draws four — changes
   what ships, not what this screen does.

6. **Each row shows a preview tile, the theme's name, and a one-line description, all read
   from the theme file itself.** The name is **`meta.name`** and the description is
   **`meta.blurb`**, on that theme; no display string is read from `themes.catalog.json`,
   which is a read-only reference asset that ships nowhere. The preview tile is a
   **miniature quadrant rendered in that theme's own colors and marks**: it draws that
   theme's grid lines — width, inset, opacity and glow, all themed — and one mark of each
   player from that theme's `marks.playerOne` / `marks.playerTwo`, so two themes side by
   side are told apart by the tile alone. An empty grid, or a grid drawn in the *active*
   theme's values, does not satisfy this.
   *(`Theming.md` → Decisions → How are themes discovered, and does a theme file carry its
   own name and description?: "**Each theme file carries its own display name and one-line
   description** … The handoff's `themes.catalog.json` becomes a reference asset rather than
   a shipping input." The tile is `design_handoff_game_ui/README.md` → 2a: "a 66×66 preview
   tile (a miniature quadrant rendered in that theme's own colors and marks), the name, and a
   one-line description in the theme's voice"; the non-active read path and the mark slots
   are `P1-03-theme-system.md`'s.)*
   *Testable:* with Neon active, the Classic row's tile renders Classic's ground and both
   its player marks, and no pixel of it resolves to a Neon color; editing a theme file's
   `meta.name` changes that row's title with no code change; a source scan finds no display
   string read from `themes.catalog.json` and none written into this screen.
   *Default for build, reversible:* the tile fills the **centre cell with `playerOne`'s mark
   and the top-right cell with `playerTwo`'s** — two marks, maximally separated, echoing the
   cell→quadrant relationship the board itself draws. The handoff describes the tile in one
   clause and its drawn arrangement is written down nowhere; this is the PRD author's
   choice, is cosmetic, and changing it touches one widget.
   The tile's **cell gaps are a code constant**, not a theme value — Requirement 22.

7. **The preview tile is the one place in the app that reads a non-active theme's values**,
   and it reads them without making that theme active.
   *(`design_handoff_game_ui/README.md` → 2a; the second read path exists in
   `P1-03-theme-system.md` for this requirement.)* Whether every theme is materialized at
   startup is that PRD's open item; either answer satisfies this requirement.

8. **The currently active theme is highlighted in the list.** The active row carries **both**
   treatments the handoff draws — the ring from `surfaces.themeRow.activeRing` **and** the
   `ACTIVE` badge from `surfaces.badge.active` — and it **keeps its ownership badge as
   well**, so an active free theme shows `ACTIVE` and `FREE` together. A ring alone, or a
   badge alone, is not this requirement.
   *(`Menus and UI.md` → Decisions → How does theme selection show which theme is in use?;
   → Theme Selection; `design_handoff_game_ui/README.md` → 2a → Ownership states, whose
   Active row reads "`ACTIVE` tag (blue) **and** its ownership tag"; `themes.catalog.json`
   → `activeBadge`, cited for the drawn values only.)*
   *Testable:* with Neon active, the Neon row carries the ring, the `ACTIVE` badge and the
   `FREE` badge, and the Classic row carries neither ring nor `ACTIVE` badge; after
   switching, both active treatments move together to the Classic row.

9. **Before a player has ever opened theme selection, Neon is the active theme**, and the
   first time the overlay is opened Neon is the highlighted row.
   *(`Menus and UI.md` → Decisions → Which theme is active by default?; `Theming.md` →
   Neon Is the Base Theme; `themes.catalog.json` → `defaultThemeId`;
   `P1-03-theme-system.md` req 14.)*
   *Testable:* on a device with nothing stored, open the overlay — Neon reads as active.

### Free and paid

10. **The list labels which themes are free and which are paid.** Every row carries exactly
    one **ownership** badge — `FREE`, `OWNED`, or a locked row's price action in place of a
    badge. The `ACTIVE` badge of Requirement 8 is not an ownership badge and does not
    replace one.
    *(`Theming.md` → Decisions → Which themes are free: "The theme selection list
    **labels** which themes are free and which are paid"; → Are themes unlockable/rewards.)*
    *Testable:* every rendered row carries exactly one ownership badge; the active row
    carries that badge plus `ACTIVE`, for two badges total.

11. **Neon and Classic Red vs Blue are free. Every theme beyond those two is paid.** This
    screen does not compute that: it renders whatever `ownershipOf` returns.
    *(`Theming.md` → Decisions → Which themes are free; the rule and the two free UUIDs are
    `P1-07-entitlements.md` reqs 1, 2 and 12.)*
    *Testable:* both shipped rows render the `FREE` badge; a fixture theme outside those two
    UUIDs does not.

12. **A row's ownership state is read from `P1-07-entitlements.md`'s published surface, per
    theme, and from nowhere else.** Concretely, this screen watches **`entitlementsProvider`**
    and calls **`Entitlements.ownershipOf(themeUuid)`**, switching on
    **`ThemeOwnership.free` / `.owned` / `.locked`**. It reads no ownership or price field
    from a theme file, from the scan result, or from `themes.catalog.json`, and it defines no
    second type modelling ownership.
    *(`P1-07-entitlements.md` **req 11** — the published surface, which exists because "four
    PRDs read this layer; without fixed names each writer coins one, every PRD passes
    review, and the call sites do not compose" — and its **req 12**, paid-ness derived from
    the UUID rather than recorded. `themes.catalog.json` → `note`: "Ownership is NOT part of
    a theme definition"; `design_handoff_game_ui/README.md` → 2a: "keep purchase state **out
    of the theme definition**"; `P1-03-theme-system.md` req 31. Apple is the record of truth
    behind that surface and a local copy is an offline convenience — `Tech Design.md` →
    Decisions → Entitlements — Apple stores them, no backend needed.)*
    *Testable:* this screen imports no entitlement symbol other than `entitlementsProvider`,
    `Entitlements` and `ThemeOwnership`; no shipped theme file contains an ownership or
    price key; changing what `ownershipOf` returns for a UUID changes that row's badge with
    no edit to any theme file. Because the provider exposes `Entitlements` **directly and
    synchronously** (`P1-07` req 11), this screen has **no loading branch** — there is no
    "ownership not known yet" state to render.

13. **The row renders all three ownership states without reshaping.** `ThemeOwnership.free`
    → the `FREE` badge; `.owned` → the `OWNED` badge; `.locked` → the price action in place
    of a badge, with the preview tile dimmed to `surfaces.themeRow.lockedPreviewOpacity`.
    A locked row still renders its preview and reads as **buyable, not broken**. The three
    states are a **runtime value returned by `ownershipOf`** — not a field attached to a
    theme, and not a variant selected at build time.
    *(`design_handoff_game_ui/README.md` → 2a → Ownership states — the part to build
    carefully; `themes.catalog.json` → `ownershipStates`; the states are
    `P1-07-entitlements.md` req 4, and that a locked theme still renders its preview is its
    req 6, which guarantees this screen can read a locked theme's values.)*
    **The handoff's phrasing is not the interface.** It says an `ownership` field "can be
    attached per theme"; that describes the *drawing*, and taking it literally would
    reintroduce the theme-file field `P1-03` req 31 and `P1-07` req 5 both forbid. Attach
    nothing; call `ownershipOf`.
    *Testable:* a fake `Entitlements` returning each of the three states in turn renders all
    three treatments through the same row widget, with no change to its layout tree.

14. **No purchase or restore control is surfaced on this screen, and the price action is
    non-interactive.** Concretely:
    - **No row is locked at launch.** Both shipped themes are free, so `ownershipOf` returns
      `ThemeOwnership.free` for every theme a shipping build's folder contains.
    - **The price action is reachable only from fixtures**, and there it **renders and does
      nothing** — no tap target, no purchase sheet, no callback into
      `P4-05-purchase-flow.md`. Requirement 13 requires it *drawn*; this requirement fixes
      that drawn is all it is. It therefore fires **neither** feedback channel — see
      Requirements 18 and 25.
    - **There is no price string to draw.** Prices must come from the store SDK at runtime
      and never be hardcoded (`P4-05-purchase-flow.md` req 3; the `$1.99` in the handoff is
      labelled mock data), and no theme product exists —
      `EntitlementProducts.productIdForTheme` returns `null` for every shipped theme
      (`P1-07-entitlements.md` req 11). A fixture supplies its own placeholder string.
    - **No purchase or restore control lives here.** The purchases section and the global
      *Restore purchases* control are on the Settings screen.

    *(`Menus and UI.md` → Decisions → Where the open-game slot unlock is sold: "**The
    Settings screen.** … it keeps the purchase flow off the other menu screens";
    `Theming.md` → Decisions → Which themes are free + → How many themes ship at launch;
    `P4-05-purchase-flow.md` **req 9**, "at launch the catalog contains zero locked themes",
    and its Out of Scope, which disowns a theme storefront outright; `themes.catalog.json` →
    `ownershipStates.locked.playable: false`.)*
    *Testable — **scoped to this screen's widget tree, not to the app**:* in a shipping
    build no descendant of `ThemeSelectionOverlay` renders a price action, a purchase
    control or a restore control, and no descendant imports or invokes
    `P4-05-purchase-flow.md`'s purchase or restore operations; with a fixture locked theme,
    the price action renders and tapping it changes nothing — no navigation, no provider
    write, no call out.
    **Why the absence is correct, and why the test is screen-scoped.** It is a Decision, not
    an inference: the controls live on Settings, explicitly to keep the purchase flow off
    the other menu screens. An app-wide absence scan would therefore be wrong — the restore
    control exists in the build, one screen over, and such a scan would fail the moment
    `P4-04-settings.md` lands. Nothing here contradicts `P4-05-purchase-flow.md` req 5,
    which makes the restore *operation* unconditional: that requirement obligates an
    operation, this one places its control elsewhere and leaves the drawn price action inert
    until there is something to sell.

### Selecting a theme

15. **Selecting a theme applies it.** The change takes effect immediately, not on restart.
    *(`Menus and UI.md` → Theme Selection: "Selecting a theme applies it".)*
    *Testable:* select Classic Red vs Blue and the main menu behind the overlay renders in
    Classic's values without an app restart.
    A row whose `ownershipOf` is `locked` is not selectable (Requirement 13;
    `P1-07-entitlements.md` req 2); at launch no such row exists.

16. **Selecting a theme that applies successfully closes the overlay**, via
    `dismissCurrent()`.
    *(`design_handoff_game_ui/README.md` → 2a: "tapping a free or owned row applies the
    theme and closes the overlay"; `P2-01-navigation.md` reqs 3 and 5.)*
    **The close is conditional on the apply succeeding.** Selection is the only moment a
    theme loads in-session, so a failed load and a close would otherwise fire together and
    leave Requirement 20's modal with no overlay to sit on. The handoff sentence describes
    the success path — it applies *and* closes — while `Theming.md` puts the failure modal
    on the Theme screen, which is only possible if the overlay is still there. Requirement
    20 takes precedence on the failure path.
    *Testable:* a successful selection leaves the router at `/`; a selection whose theme
    fails to load leaves it at `/theme`.

17. **The selection persists between sessions.** Close the app, open it again, and that is
    still the player's theme, active before they touch anything.
    *(`Theming.md` → Decisions → Does the theme persist between sessions; `Menus and UI.md`
    → Persistence.)* This screen hands the applied selection to the persistence layer at the
    moment it is applied; the store, the key, and that the persisted value is the UUID are
    `P1-04-persistence.md`'s.
    *Testable:* select Classic, restart, and the menu renders in Classic with the Classic
    row active.

18. **Every valid tap on this screen calls `HapticService.validAction()` exactly once** —
    a theme row, the close control, and the failure modal's dismiss action. The layer owns
    the vibrate-on-touch gate, so this screen calls unconditionally, never reads the setting
    and never branches on it.
    *(`Game Board Design.md` → Decisions → **Does the haptic fire on non-board controls?**:
    "**Yes — every valid tap buzzes, anywhere in the app.** Menu buttons, **theme rows**,
    settings toggles, the game-over card's controls, the settings gear — not only board
    cells." Also `Menus and UI.md` → Settings Menu → Vibrate on Touch ("Fires on making a
    selection / clicking") and `Game Board Design.md` → Haptic Rule. The entry point and its
    gate are `P2-03-haptics.md`.)*
    *Testable:* with `hapticServiceProvider` overridden by `P2-03-haptics.md` req 15's
    `FakeHapticService`, each of those taps raises its call count by **exactly one** — never
    zero, never twice. **This assertion is this requirement's to make:** `P2-03-haptics.md`
    req 1's wave note holds that "a valid **tap** reaches `validAction()` exactly once is a
    call-site fact, owned by each calling PRD," and names this requirement as the owner for
    this screen.
    **The interface is unchanged by the app-wide ruling.** `validAction()` still takes no
    argument and returns `void` — a menu button and a theme row call the same member, so
    nothing here distinguishes itself as a non-board caller.
    **The inert price action is not a valid tap** and fires nothing (Requirement 14),
    consistent with *"an invalid tap stays silent in both channels."*
    > **Previously provisional, now ratified.** Earlier revisions carried this as the *broad*
    > reading with a caveat pointing at `P2-03-haptics.md` OQ-2, which warned the decision was
    > "being made by accumulation." It was decided outright instead, and that PRD now lists
    > this requirement among three ratified non-board callers.

25. **Every valid tap on this screen also fires
    `ref.read(audioLayerProvider).play(SoundMoment.buttonTap)` exactly once** — the same
    three sites as Requirement 18: a theme row, the close control, and the failure modal's
    dismiss action. One tap sound, no per-control variation.
    *(`Theming.md` → Decisions → **Do non-board controls make a sound?**: "**Yes — one tap
    sound, everywhere.** Every button, row and toggle plays the same short tap sound: menu
    buttons, **theme rows**, settings toggles, the game-over card's two controls, the trash
    button and the modal's Yes and No." The moment, the enum and the layer are
    `P2-02-audio.md` req 6, whose table gives `buttonTap` the single slot `sound.buttonTap`;
    that Decision grounds itself in the haptic ruling's symmetry — *"so the two feedback
    channels now behave consistently rather than one buzzing where the other is silent."*)*
    **The gate is inside the layer**, exactly as with the haptic: this screen calls
    unconditionally, never reads the sound-effects setting, and **never reads a `sound` key**
    — which is why Requirement 23's "this screen reads no `sound` key" is load-bearing rather
    than incidental. `buttonTap` is one moment and one file; there is no second slot to pick
    between.
    *Testable:* with `audioLayerProvider` overridden by `P2-02-audio.md`'s `FakeAudioLayer`
    in a `ProviderScope`, each of those taps records **exactly one**
    `play(SoundMoment.buttonTap)` — never zero, never twice — and no other `SoundMoment`.
    **This assertion is this requirement's to make:** `P2-02-audio.md` req 6's wave note
    holds that "a control's tap reaches `play` exactly once is a **call-site fact, owned by
    each calling PRD**." The inert price action records zero, per Requirement 14 and that
    PRD's req 9.
    **Numbered last, placed here.** It belongs beside Requirement 18 and is written beside
    it; the number is 25 because Requirements 1–24 are cited across five sibling PRDs.
    > **Why this requirement exists at all.** The Out of Scope previously routed this
    > screen's tap sound to `P2-02-audio.md`, which was correct while its OQ-3 — whether
    > non-board controls make a sound — was open. Once that closed **yes**, the routing left
    > the sound owned by nobody: `P2-02` owns the moment and the layer, not the call sites.
    > **One pointer still needs fixing on the other side:** `P2-02-audio.md` req 6's owner
    > table lists *"`P4-03` req 18 (theme rows)"* — req 18 is the haptic. It should read
    > req 25, and the site list should be the three above rather than rows alone. Flagged
    > here because this PRD cannot edit that one.

### Where it is *not* available

19. **The theme can be changed from the main menu only — there is no mid-game theme
    change.** No control reachable from a game changes the active theme.
    *(`Theming.md` → Decisions → Can you change the theme mid-game; corroborated by
    `design_handoff_game_ui/README.md` → 1f, "Themes live on the main menu — you can't
    switch mid-game".)*
    *Testable:* no call site under the game screen or its quick-actions surface invokes
    `openThemeSelection()`. `P2-01-navigation.md` **requirement 18** enforces the same
    constraint structurally — `/theme` is a child of `/`, not of `/game:gameId`.

### Failure path

20. **If a theme fails to load, a modal is shown on the theme selection overlay** saying
    the theme is unavailable and asking the player to try another theme. **The overlay stays
    mounted underneath it**, and Requirement 16's close does not fire on this path.
    *(`Theming.md` → Decisions → What happens if a theme fails to load: "From the Theme
    screen if a theme fails to load put up a modal with sorry this theme is unavailable
    please try another theme"; `themes.catalog.json` → `failureBehavior`. Which theme failed
    is reported by `P1-03-theme-system.md`; what counts as a failure is that PRD's.)*
    This is the **apply-time** path — a theme the player selected. A file that was already
    unreadable at scan time never produced a row (Requirement 4), so it cannot be selected.
    The modal draws from `surfaces.modal.*` and `type.scale.heading` (Requirement 23), and
    its dismiss action buzzes and clicks like any other control (Requirements 18 and 25).
    *Testable:* force a load failure for a selected theme; the modal appears, the router is
    still at `/theme`, and the overlay is still in the tree beneath it.

21. **After that modal, the app falls back to Neon**, which becomes the active theme, and
    the overlay reflects Neon as the highlighted row.
    *(`Theming.md` → Decisions → What happens if a theme fails to load: "Then fallback to
    neon"; `P1-03-theme-system.md` reqs 27–28.)*
    *Testable:* after the modal is dismissed the active theme is Neon and the Neon row
    carries Requirement 8's active treatment.
    *Default for build, reversible:* **the overlay stays open** on the Neon-active list once
    the modal is dismissed, rather than closing with it — which is what "please try another
    theme" implies and what this test reads. Stated because the test previously presumed it
    silently. Whether the fallback is also *persisted* is a separate default — Open
    Question 4.

### Presentation

22. **Every value used to draw this overlay is read from the active theme through
    `P1-03-theme-system.md`'s schema — except spacing and layout numbers, which are code
    constants.** No color, radius, type style, icon, opacity, sound or motion value is
    written into this screen's source. The preview tiles of Requirement 6 are the one
    exception to *which* theme is read, and they read another theme, not a constant.

    **The boundary, in the Decision's own terms:** a theme controls **the drawn geometry of
    a thing itself** — stroke width, glyph size, corner radius, glow spread. **Code controls
    where things sit relative to one another** — gaps, padding, margins. Element *sizing* is
    where a theme's visual range lives; element *spacing* is layout. Classify a new value
    with that sentence rather than by looking for the word "padding".
    *(`Theming.md` → Decisions → Does a theme control spacing and padding?: "**No. Spacing
    and layout numbers are fixed in the code, not theme-controlled — for now.**" The reason
    is enforcement, not principle: the guard cannot tell `SizedBox(width: 8)` holding a
    themed gap from one holding an incidental gap, so a padding section "would therefore
    have been a rule that nothing verifies — a claimed guarantee the project could not
    keep." `P1-03-theme-system.md` req 15's boundary note, which removed every such key at
    schemaVersion 7 and names this PRD as one of six needing this exception.)*

    **What that makes a code constant on this screen**, with the drawn values it takes from
    `design_handoff_game_ui/README.md` → *2a*: the **sheet's inset** (20), the **theme row's
    internal padding** (14) and **its gap between preview tile, text and badge** (14), the
    **gap between rows**, the **price action's padding** (`9/13`), and the **preview tile's
    cell gaps**. These live in `lib/ui/menus/theme_selection_overlay.dart` (Requirement 24)
    and are **not** review findings — a reviewer flagging them as hardcoded is applying the
    pre-v7 rule.
    *Testable:* `P1-05-theme-guard-test.md` passes over this screen's source with the
    baseline at zero, and no key this screen reads resolves to a removed spacing path.

23. **The keys this screen reads — all published in `P1-03-theme-system.md` Requirement 15
    at schemaVersion 7, all `required`, none to be invented here.** Bind to these paths
    exactly. A value that looks right under a neighbouring key is the failure mode that
    schema exists to prevent, and `P1-05-theme-guard-test.md` cannot catch it: it flags a
    literal written into code, not a read from the wrong key.

    | What this screen draws | Published key path |
    |---|---|
    | The sheet itself | `surfaces.sheet.{fill,radius}` |
    | Its header and close control | `surfaces.sheet.header.{titleStyle,subStyle,closeControl}` |
    | The close glyph | `icons.close.{kind,set,name,tint,size}`, plus optional `icons.close.button.{fill,radius,size}` |
    | The layer over the menu | `surfaces.scrim.themeSelect` |
    | The menu dimmed behind it | `surfaces.menu.dimBehindOverlay` |
    | A theme row | `surfaces.themeRow.{fill,radius,previewTile,activeRing,lockedPreviewOpacity}` |
    | Ownership and active badges | `surfaces.badge.{free,owned,active,priceAction}` |
    | Header and row type | `type.scale.sheetTitle`, `type.scale.sheetSub` |
    | Row and price-action corners | `radius.row`, `radius.priceAction` |
    | The failure modal | `surfaces.modal.{fill,border,radius,shadow}`, `type.scale.heading`, `type.scale.body` |
    | A row's name and description | that theme's `meta.name`, `meta.blurb` |
    | A preview tile's contents | that theme's `board.{gridLineWidth,gridLineInsetPercent,gridLineOpacity,gridLineGlow}` and `marks.playerOne` / `marks.playerTwo` |

    **This screen reads no `sound` key — and that is now load-bearing, not incidental.**
    Requirement 25 fires `SoundMoment.buttonTap` and the audio layer resolves
    `sound.buttonTap` itself, so a lookup here would be a second resolution of the same slot
    and would bypass the layer's gate. Whatever lands on that section's shape does not reach
    this screen.

    **Spacing is deliberately absent from this table.** `surfaces.sheet.padding` and
    `surfaces.themeRow.padding` were removed at schemaVersion 7 and **must not be read or
    re-added**; the values they held are the code constants named in Requirement 22. Every
    key that remains above is a single element's own shape, which is why none of them went
    with it — including `radius.row` and `radius.priceAction`, since a corner is a thing's
    own geometry.

    **The close glyph is theme-supplied, and that is a Decision** — `Theming.md` →
    Decisions → *Do themes control the app's chrome icons?*: "**Yes.** The settings gear,
    close X, chevrons and plus are theme-controlled, and a theme may either name a glyph
    from a bundled icon set or ship its own image." A hardcoded `Icons.close` is not a
    stylistic slip here; `P1-05-theme-guard-test.md`'s widened guard fails the build on it.

    **Two distinctions worth stating, because each is a one-key mistake.**
    `surfaces.scrim.themeSelect` and `surfaces.menu.dimBehindOverlay` are different values
    doing different jobs on this one screen: the scrim is a layer painted over the menu, the
    dim reduces the menu's own opacity to 35%. And `surfaces.themeRow.*` is **not**
    `surfaces.gameRow.*` — `P4-02-open-games-list.md`'s row is a different fill and radius,
    and one key cannot serve both.
    *Neon's values for every key above are transcribed by `P1-03-theme-system.md` req 13,
    whose source table names "the theme rows and badges" explicitly. The near-miss risk for
    the badge, ring, radius and type values is catalogued in that PRD's Appendix A.1 and is
    not repeated here.*
    *Testable:* a source scan over this screen finds no `color.*` read — every themed value
    comes from a `surfaces.*`, `icons.*`, `type.*`, `radius.*`, `board.*`, `marks.*` or
    `meta.*` path — and every theme key it reads appears in
    `lib/theme/required_keys.dart` (`P1-03` req 11).

24. **Where this screen lives.** The widget is **`ThemeSelectionOverlay`**, in
    **`lib/ui/menus/theme_selection_overlay.dart`**, with its row widget and its spacing
    constants alongside it under `lib/ui/menus/`. Requirement 4's testable and Requirement
    22's guard run over that directory.
    *(`Tech Design.md` → Decisions → Project structure — layer-first, whose tree puts screens
    under `ui/menus/`. The widget **name is not this PRD's invention**:
    `P2-01-navigation.md` req 2's route table already builds
    `TransparentPage(child: ThemeSelectionOverlay())` at `/theme`, so this requirement
    records the name that layer compiles against rather than coining a second one. Siblings
    name theirs the same way — `P1-03` → `lib/theme/`, `P2-01` → `lib/navigation/`.)*

## Out of Scope

- **The theme system** — the schema, YAML loading, UUID identity, merge, the folder scan and
  the failure report: `P1-03-theme-system.md`. Requirement 23 binds to its keys and
  Requirement 4 consumes its scan; this PRD designs neither.
- **Persisting the selected theme UUID** — `P1-04-persistence.md`.
- **The entitlement model** — what the three states mean, the free tier, the cap, and the
  provider itself: `P1-07-entitlements.md`. Requirements 10–14 render its answers.
- **The navigation layer** — the router, the route table and what the two operations do
  underneath: `P2-01-navigation.md`.
- **The audio layer** — `audioplayers`, the sink, the sound-effects gate, asset loading and
  what `sound.buttonTap` resolves to: `P2-02-audio.md`. Requirement 25 owns this screen's
  three call sites and nothing else. **Note the change:** an earlier revision routed the tap
  *sound itself* here, which was correct only while that PRD's OQ-3 was open.
- **The haptic mechanism and its gate** — `P2-03-haptics.md`. Requirement 18 owns this
  screen's call sites; the platform call, the vibrate-setting gate and the no-haptic-engine
  case are all that PRD's.
- **The main menu** — `P4-01-main-menu.md`.
- **The Classic Red vs Blue theme's content**, including its own `meta.name` and
  `meta.blurb` — `P5-01-classic-theme.md`.
- **The Settings screen's purchases section** — the $4.99 unlock and the global *Restore
  purchases* control both live there: `P4-04-settings.md` (`Menus and UI.md` → Decisions →
  Where the open-game slot unlock is sold).
- **Purchasing and restore** — `P4-05-purchase-flow.md`. Stated precisely because it is easy
  to read backwards: **the restore control is a compliance requirement, not the mechanism by
  which entitlements arrive.** Entitlements come from Apple via
  `Transaction.currentEntitlements`, verified on device, and restore for non-consumables is
  largely automatic; the visible control exists because Apple's review guidelines require
  it, with `AppStore.sync()` behind it (`Tech Design.md` → Decisions → Entitlements — Apple
  stores them, no backend needed).
- **The parental gate.** `Tech Design.md` → Decisions → Kids category requires one before any
  purchase flow and names theme selection as a feature it reaches. It has no trigger here,
  because Requirement 14 makes the price action inert and surfaces no purchase entry point.
  If a purchase is ever reachable from this overlay, the gate must precede it.
- **Any paid theme's content.** None exists; `design_handoff_game_ui/README.md` → 2a marks
  Splat and Dinosaurs as placeholders that "do not exist" and must not ship as designed.
  Requirement 13 is satisfied with fixtures, not with those two.
- **The settings page's read-only "Theme — Picked from the main menu" display** — that is
  `P4-04-settings.md`'s. It is not a second entry point and does not change Requirement 19.
- **What counts as "fails to load", and what happens if *Neon* fails** —
  `P1-03-theme-system.md`. Requirement 4 states what the player sees at scan time and
  Requirement 20 what they see at apply time; neither defines the trigger.

## Open Questions

### 1. What the handoff draws vs. what ships — the only item still with the user

The free-vs-paid half is **settled** and is Requirements 10–14. What is unresolved is **how
many themes ship**, and this PRD picks neither side:

- `design_handoff_game_ui/README.md` → *2a* draws **four** rows — Neon, Classic, Splat and
  Dinosaurs — and headers the sheet **"Two free, two extra. Switch any time."**
- `Theming.md` → Decisions → How many themes ship at launch says **two**, and
  `Menus and UI.md` → Theme Selection and → Screens (so far) → 5 say the same. Requirement 5
  follows those two docs.

The handoff calls Splat and Dinosaurs placeholders that "do not exist" and says "Do not ship
them as designed", so the four-row drawing may be a mock artifact. But the paid direction is
decided, which makes some future paid theme expected, and nothing states which or when.
Left open:

- Do two theme files ship, or four with two of them unbuilt placeholders?
- **The header sub-copy rides on the answer.** "Two free, two extra. Switch any time."
  describes the four-row layout and is false on a two-row list. Open Question 4's last row
  carries the interim default.

**This does not block building the screen.** Since Requirement 4 became a folder scan, the
answer decides *what is in `assets/themes/`* — the row count follows the folder, and no code
here changes either way.

*Also carried by `P1-03-theme-system.md` → Contradiction, which points here.*

### 2. From `Theming.md` → Open Questions

- Which values, concretely, does Classic Red vs Blue override? (Settled in principle —
  graphics and its splat sound, inheriting the rest. An exact list will fall out when it's
  actually built.)

This lands on Requirement 6: until Classic's file is authored, its preview tile has only the
handoff's `previewColors` to go on. Owned by `P5-01-classic-theme.md`, whose palette
question `Theming.md` has since answered.

### 3. From `Tech Design.md` → Open Questions → 2. Theme loading

- Are all themes loaded and materialized at startup, or only the selected one, on demand?
  `Theming.md` → Why this matters for the build says materialization happens "at startup"
  but does not say for how many themes.

Requirement 7 needs every listed theme's values, not just the active one's; either answer
satisfies it. `P1-03-theme-system.md` owns it.

### 4. Gaps this PRD found — each fenced with a build default

None of these is *resolved*. Each carries a default so an agent does not invent one
silently, and each names what changes if the user answers differently.

| Gap | Default for build | Reversibility |
|---|---|---|
| **The failure modal is not designed** — `design_handoff_game_ui/README.md` → *Still to design* → 3 lists it as undrawn | Requirement 20's copy in `surfaces.modal.*` with `type.scale.heading` + `body`, one acknowledging action and no other choice | One widget; layout only |
| **What the overlay does after the modal is dismissed** | **Stays open** on the Neon-active list (Requirement 21) | One line; the alternative also calls `dismissCurrent()` |
| **Where the failure modal goes when the failure is at launch** — the persisted theme loads before this overlay exists | Fall back to Neon **silently** at launch and show the modal the next time the overlay is opened, since Requirement 20's source says "*From the Theme screen*" | Moves a call, no layout change. Behavioural — wants the user |
| **Whether the Neon fallback is persisted** | **Not persisted** — Requirement 17 persists a selection the player made; this is a substitution the app made | One call site. Wants the user |
| **A malformed or duplicate-`meta.id` theme file** (Requirement 4) | Omitted from the list; duplicates never resolved by scan order; the list still renders | Two branches in the scan's consumer. A theme author sees silence — worth revisiting once themes are hand-authored |
| **The preview tile's exact composition** | Centre cell `playerOne`, top-right cell `playerTwo` (Requirement 6) | Cosmetic; one widget |
| **What tapping the already-active row does** | **No-op** — no re-apply, no close. It still **buzzes and clicks**, since the tap is valid (Requirements 18 and 25) | One branch |
| **Whether the scrim dismisses the overlay** | **Not a dismiss target** — the close control is the only way out | One gesture detector. *(This does not depend on `P2-01-navigation.md` OQ-10, which is opaque-vs-non-opaque page building for the name prompt and quick actions; its req 9 already settles `/theme` as non-opaque.)* |
| **Row order** | **Catalog order** — the order the folder scan returns | A sort call; one line |
| **The header strings** — "Pick your look" and "Two free, two extra. Switch any time." exist only in the handoff | Render the title as drawn; **omit the sub-copy**, because it describes the four-row layout Open Question 1 leaves open and is false on a two-row list | Two strings. Rides on Open Question 1 |

### 5. Answered — the Settings screen hosts the purchase and restore controls

**Closed.** Kept as a stub so the trail stays visible and the numbering around it is stable.

This asked whether this overlay hosts *Restore purchases*, and recorded that **no
requirement in any PRD surfaced a restore control anywhere** while the $4.99 unlock ships.
`Menus and UI.md` → Decisions → *Where the open-game slot unlock is sold* settles both
halves: "**The Settings screen.** The Settings screen gains a purchases section holding the
$4.99 open-game-slot unlock and a global **Restore purchases** control … it keeps the
purchase flow off the other menu screens." So the gap is closed by `P4-04-settings.md`,
Requirement 14 is doc-backed rather than argued, and wave-4 parallelism is no longer
contingent.

### 6. Answered — a theme file carries its own name and blurb, and discovery is a folder scan

**Closed.** Kept as a stub for the trail.

This PRD refused to default the row's name and description, and refused to default theme
discovery, on the grounds that inventing either would create the second source of truth the
question existed to kill. `Theming.md` → Decisions → *How are themes discovered, and does a
theme file carry its own name and description?* answers both: "**Each theme file carries its
own display name and one-line description, and the app discovers themes by scanning the
themes folder.**"

Consequences folded in: Requirement 4 enumerates from the scan and states what a malformed
or duplicate-id file does to the list; Requirement 6 reads `meta.name` and `meta.blurb`;
`themes.catalog.json` is cited as a reference asset only; and Open Question 1 became a
question about the folder's contents rather than about this screen.

### 7. Answered — spacing and padding are code, not theme

**Closed.** Kept as a stub for the trail.

`Theming.md` → Decisions → *Does a theme control spacing and padding?*: "**No. Spacing and
layout numbers are fixed in the code, not theme-controlled — for now.**" The reason is
enforcement rather than principle — the guard cannot distinguish a themed gap from an
incidental one.

This resolved a conflict this PRD was carrying without noticing: Requirement 22 forbade
hardcoded values across the whole schema while Requirement 23 bound to
`surfaces.sheet.padding` and `surfaces.themeRow.padding`, so once those keys were removed
the only legal implementation of this screen's layout was one Requirement 22 prohibited.

**The line is narrow, and worth keeping straight when reading Requirement 6:** a theme still
controls how the board and its preview tile *look* — grid-line width and inset, mark sizes,
colors, glows, radii are all themed. It cannot move things apart.

### 8. Answered — the haptic fires app-wide, so Requirement 18 is ratified

**Closed.** Kept as a stub for the trail.

`Game Board Design.md` → Decisions → *Does the haptic fire on non-board controls?*: "**Yes —
every valid tap buzzes, anywhere in the app.**"

This PRD had carried Requirement 18 as the *broad* reading, with a caveat pointing at
`P2-03-haptics.md` OQ-2 — which warned that three PRDs asserting it while the question was
open meant "the decision is currently being made by accumulation." Worth recording how it
resolved: the accumulation was **not** ratified by inertia. The question was escalated and
decided outright, and Requirement 18 gained the call-site test it had been missing the whole
time it was provisional.

### 9. Answered — non-board controls make a sound, and this screen owns its call sites

**Closed.** Kept as a stub for the trail, and because the failure it fixed is worth naming.

`Theming.md` → Decisions → *Do non-board controls make a sound?*: "**Yes — one tap sound,
everywhere.**" Requirement 25 is the consequence.

**The shape of the near-miss:** while that question was open, routing the tap sound to
`P2-02-audio.md` in Out of Scope was correct — there was no settled sound to own. When it
closed, the routing silently became a gap: `P2-02` owns the moment, the enum and the layer,
but its own req 6 makes each *call site* the calling PRD's, and this PRD had disclaimed the
call site. A sound every control is supposed to make would have shipped in no screen. The
same closure that ratified Requirement 18 created this hole one requirement away, which is
the argument for re-reading a PRD's Out of Scope whenever one of its dependencies closes a
question — an Out of Scope entry is a claim about *someone else's* scope, and it can go stale
without anything in this file changing.

`P2-02-audio.md` req 6's owner table still points at Requirement 18 for theme rows; it should
point at Requirement 25, and at three sites rather than one. Flagged in Requirement 25 —
this PRD cannot edit that file.
