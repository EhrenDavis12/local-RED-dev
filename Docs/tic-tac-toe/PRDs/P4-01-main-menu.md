# PRD: Main Menu

> **Status:** Draft · Source docs read: `Menus and UI.md`, `Theming.md`, `Tech Design.md`,
> `Game Overview.md`, `Animations.md`, `Game Board Design.md`, `Rules.md`, `roadmap.md`, and
> the read-only reference asset `design_handoff_game_ui/` (`README.md` → *1a — Main Menu*,
> *Fidelity*, *Design tokens*, *Assets*). `Alternative Game Styles.md` is a declared
> parking-lot doc and was not sourced from.
>
> **Revised (round 2)** against the current `P2-01-navigation.md`, `P1-03-theme-system.md`,
> `P2-02-audio.md`, `P2-03-haptics.md` and `P4-03-theme-selection.md`: Requirement 13 gained
> an inclusion boundary, Requirement 10 was re-pointed at the separate slot entries
> `P1-03` now carries, Requirements 14–16 name navigation operations, and the citations into
> `P2-01` were corrected.

**Wave:** P4 · **File:** `P4-01-main-menu.md`

**Depends on:**

- `P1-01-app-scaffold.md` — `lib/ui/menus/` and the Riverpod root.
- `P1-03-theme-system.md` — every value on this screen is read from the theme object. This
  screen consumes **five separate entries** of that PRD's Requirement 15 inventory, not one
  composite slot: the **gradient-capable page background**, the **corner radii**, **main-menu
  styling** (background, title/wordmark/kicker treatment, and a **logo slot**), the **type
  scale**, and **two button tiers, not one**. See Requirement 10.
- `P2-01-navigation.md` — requirement **4** settles that the main menu is the app's launch
  screen, so this PRD does not restate it; requirement **5** holds the Play Game branch,
  requirement **6** the theme overlay over a still-mounted menu, and requirement **7** the two
  settings entry points. Its requirement **3** names the operations this screen calls
  (Requirements 14–16 below).

**Depended on by:** `P4-02-open-games-list.md`, `P4-03-theme-selection.md`,
`P4-04-settings.md` — each is a destination this screen launches, and each specifies its own
behavior. All three are same-wave siblings, so the work is parallel-safe.

---

## Problem

There is no main menu, so there is no way into the game at all. The docs settle three
separate things that only exist once this screen does: that play starts from a **Play Game**
button (`Menus and UI.md` → Decisions → *Is the main menu button "New Game" or "Play Game"?*),
that changing the theme is a first-class, up-front action rather than something buried in
settings (`Theming.md` → Decisions → *Where theme selection lives*), and that the menu itself
is theme-driven like everything else (`Menus and UI.md` → Main Menu). Without the screen,
theme selection has no host — it is an overlay on the main menu, not a screen of its own
(`Menus and UI.md` → Decisions → *Is theme selection its own screen or an overlay?*).

## Goal

The app has a main menu carrying a logo and a title above three buttons — **Play Game**,
**Theme**, and **Settings** — where Play Game and Theme are large and given equal visual
weight, because making it fun for kids to change the theme is the point of putting it there.
Every value on the screen — background, button styling, title — comes from the active theme,
so a new theme restyles the menu with no change to menu code. Under Neon the screen matches
the approved handoff drawing `1a — Main Menu` for the elements Requirement 13 enumerates.

## Requirements

### Structure and content

1. **The main menu presents exactly three buttons: Play Game, Theme, and Settings.**
   *(`Menus and UI.md` → Main Menu → Buttons; Screens (so far) → 1. Main Menu)*
   Recorded from the same section: the menu grew across the brain dump — first *"only a New
   Game button,"* then + Theme, then + Settings — and **three buttons is where it currently
   stands**. Anything beyond three is Open Questions, below.
   *Testable:* the screen exposes three tappable top-level controls and no fourth.

2. **The first button is labelled "Play Game", not "New Game".**
   *(`Menus and UI.md` → Decisions → Is the main menu button "New Game" or "Play Game?" —
   **Play Game**)* "New Game" survives only as an entry at the top of the open-games list,
   which is `P4-02-open-games-list.md`'s territory. Whether the label's **casing** is part of
   the string or a theme text-transform is unsettled — see Open Questions.

3. **Play Game is large** — the dominant control on the screen.
   *(`Menus and UI.md` → Main Menu → Buttons: "Large.")*

4. **Play Game and Theme are the same button: both render from the theme's shared
   large-primary tier**, so equal visual weight is a property of the code rather than an
   obligation each theme has to honor separately. The doc's words are *"a nice big button,
   the same size and treatment as the Play Game button"* — a build in which the two read from
   different slots can drift apart the moment a theme overrides one of them.
   *(`Menus and UI.md` → Main Menu → Buttons: "Large, same weight as Play Game"; `Theming.md`
   → Decisions → Where theme selection lives; `P1-03-theme-system.md` req 15 → "Two button
   tiers, not one — a large primary (Play Game, Theme) and a secondary (Settings)";
   corroborated by `design_handoff_game_ui/README.md` → 1a: "`PLAY GAME` and `THEME` — equal
   weight per the docs", identical border, glow, size, padding and radius)*
   *Testable:* both buttons resolve their border, fill, text style, padding, radius and glow
   from the same tier; no menu-local override sits between either button and that tier.

5. **Theme selection is reached from the main menu and is deliberately not inside Settings.**
   Themes are *"up front, not buried in a settings screen."* A build that satisfies every
   other requirement but reaches themes only through Settings fails this one.
   *(`Menus and UI.md` → Main Menu; `Theming.md` → Decisions → Where theme selection lives)*

6. **Settings is the third button and renders from the theme's secondary tier**, not the
   large-primary tier Requirements 3 and 4 reserve for Play Game and Theme.
   *(`Menus and UI.md` → Main Menu → Buttons — "Settings — opens the settings menu", with no
   "Large" qualifier, unlike the two above it; `design_handoff_game_ui/README.md` → 1a, where
   `Settings` is 15pt with a 1px hairline border against the two 20pt 2pt-bordered buttons;
   `P1-03-theme-system.md` req 15 → Two button tiers, not one)*
   **Its geometry is not settled by this requirement.** `1a` draws Settings as the **left half
   of a two-up row** shared with About Us; with no About Us button (Requirement 1) that row
   has one occupant, and full-width, half-width left-aligned and half-width centered all
   satisfy this requirement while none is pixel-faithful. See Open Questions — this needs an
   answer under *every* outcome of the About Us call.

7. **The menu shows both a title and a logo** — both, not just buttons.
   *(`Menus and UI.md` → Decisions → Does the main menu need a title/logo? — **Yes — both a
   title and a logo.**)*

8. **The logo ships as a placeholder in this PRD.** Real logo art is explicitly deferred:
   assets are generated with Replicate *"when we actually need them — not now."* The handoff
   marks its 1a logo a placeholder — a dashed-bordered 81-dot mark — and *"Replace with real
   art."*
   *(`Tech Design.md` → Decisions → Where do sound and art assets come from?;
   `design_handoff_game_ui/README.md` → Fidelity, Screens → 1a, Assets → Logo)* Producing the
   art and the Replicate script is `P5-02-asset-generation-replicate.md`. The logo renders
   through the theme's **logo slot** (`P1-03-theme-system.md` req 15 → Main menu styling), not
   from a menu-local asset path.

### Theme-driven, with nothing hardcoded

9. **Every visual value on this screen is read from the active theme — background, button
   styling, and title. No hardcoded styling anywhere in the menu.**
   *(`Menus and UI.md` → Main Menu: "The entire main menu is itself theme-driven —
   background, button styling, title. No hardcoded styling here either."; `Theming.md` →
   Architectural Rule)*
   **Note the reach of this requirement versus the reach of the guard.** Requirement 12's scan
   catches colour, font, duration and asset patterns; it does not see geometry, so
   `padding: 96` would pass the guard and still violate this requirement. Whether screen
   padding is a theme value at all is unresolved and carried below.

10. **The menu reads the theme's slots directly, and introduces no menu-local composite that
    stands between it and them.** The five entries it consumes are separate on purpose:
    - the **gradient-capable page background** — `1a`'s ground is a radial gradient, so one
      flat colour is not sufficient;
    - the **corner radii** set;
    - **main-menu styling** — background, title/wordmark/kicker treatment, and the **logo
      slot**;
    - the **type scale**;
    - the **two button tiers** — large primary and secondary.

    The tiers in particular must be read as the shared theme-level slots they are:
    `P1-03-theme-system.md` req 15 cites them jointly to Requirements 4 and 6 here **and** to
    `P4-02-open-games-list.md` req 12, so folding them into a menu-local "button look" breaks
    the sibling's reuse. That PRD's own rationale is the reason the single slot was split:
    *"A single 'button look' slot is satisfied by one style and would force the second to be
    hardcoded."*
    *(`Theming.md` → What a Theme Controls → Visual; → Decisions → What the theme's slots are
    derived from; `P1-03-theme-system.md` req 15 → Board and geometry, Surfaces and chrome,
    Type)*
    *Testable:* no style constant or composite style object is declared under `lib/ui/menus/`;
    every value the menu paints resolves to a named slot on the theme object.

11. **Restyling the main menu for a new theme requires zero changes to menu code** — only a
    new theme definition. Testable as: switching the active theme changes the menu's
    background, button styling and title without touching `lib/ui/menus/`.
    *(`Theming.md` → Architectural Rule)*

12. **The menu passes the hardcoded-theme-value test with no baseline entries** — no
    `Color(0x…)`, `Colors.*`, literal `fontFamily:`, `GoogleFonts.*`, hardcoded `Duration(…)`
    or literal `assets/…` path in the menu's source.
    *(`Tech Design.md` → Decisions → Do we add a test that fails on hardcoded theme values? —
    the baseline starts at zero; the test itself is `P1-05-theme-guard-test.md`)* Its stated
    limit applies here: the guard catches a value written into code, not a value read from the
    wrong slot, and not geometry — see Requirement 9.

13. **Under the Neon theme the screen recreates `1a — Main Menu` from the approved handoff,
    for the six elements named below and no others.** The handoff's colors, type, spacing,
    radii and glow values are final and exact and are to be recreated pixel-for-pixel.

    1. the radial-gradient ground;
    2. the `96 / 28 / 52` padding and the 12pt gaps between buttons;
    3. the 104×104 logo placeholder (Requirement 8);
    4. the `TIC TAC TOE` kicker over the `EXTREME` 44/600 wordmark (Requirement 7);
    5. the large-primary treatment shared by Play Game and Theme (Requirement 4);
    6. the secondary treatment on Settings (Requirement 6), subject to the geometry question
       that requirement records.

    **This list is exhaustive.** Anything else drawn on `1a` — the **About Us button**, the
    tagline *"Nine boards. One winner. Good luck."*, and the footer `Theme: Neon · v0.1.0` —
    is **not** required here and is held in Open Questions. Without that boundary this
    requirement would demand the fourth button Requirement 1 forbids, and two numbered
    requirements would contradict each other.
    *(`design_handoff_game_ui/README.md` → Fidelity; Screens → 1a; Design tokens;
    `Game Overview.md` header — the handoff "is the source of truth for what the game *looks
    like*")*

    **Where Neon's values for these six come from is not settled.**
    `P1-03-theme-system.md` req 13 records that `neon.theme.json` does not cover its own slot
    inventory and that *"the difference is not this PRD's to invent"* — naming *"a gradient
    background, a logo"* among what is missing. Neither that PRD nor this one produces those
    values today. The slots this screen needs and Neon does not hold are enumerated in Open
    Questions, for the `P1-03` revision to place.

### Navigation out of the menu

Each button invokes a named operation from `P2-01-navigation.md` requirement 3. That PRD's
requirement 1 forbids any `Navigator.` call, route construction or route name outside
`lib/navigation/`, so naming the operation is part of the requirement: a menu widget that
calls `Navigator.push` would satisfy the intent of all three below and still fail that scan.

14. **Play Game calls `playGame()`.** The branch on whether stored open games exist is
    evaluated inside the navigation layer, not here — this screen does not test the count and
    does not choose a destination.
    *(`Menus and UI.md` → Main Menu → Buttons; `Game Overview.md` → Modes: "Started from the
    **Play Game** button on the main menu."; the branch is `P2-01-navigation.md` requirement
    5, the operation its requirement 3 table row 2)*
    *Testable:* tapping Play Game invokes `playGame()` exactly once and nothing else; no route
    name, route construction or `Navigator.` call appears under `lib/ui/menus/`. What that
    destination contains is `P4-02-open-games-list.md`'s.

15. **Theme calls `openThemeSelection()`,** which opens theme selection as an overlay with
    this menu still mounted beneath it — not a screen the menu is replaced by.
    *(`Menus and UI.md` → Decisions → Is theme selection its own screen or an overlay? — **An
    overlay** on the main menu; → Screens (so far) → 5; the "menu stays mounted" half is
    `P2-01-navigation.md` requirement 6, the operation its requirement 3 table row 3)*
    *Testable:* tapping Theme invokes `openThemeSelection()` exactly once; while the overlay
    is up this menu is still mounted, and dismissing it reveals the same menu instance rather
    than a newly constructed one. The overlay's contents are `P4-03-theme-selection.md`'s;
    what happens to the *appearance* of the menu underneath is an open question below.

16. **Settings calls `openSettings()`** — the main menu's settings entry point, one of the two
    `P2-01-navigation.md` requirement 7 settles.
    *(`Menus and UI.md` → Main Menu → Buttons; Settings Menu — "Reachable from two places:
    1. The **main menu** (Settings button)."; the operation is `P2-01-navigation.md`
    requirement 3 table row 4)*
    *Testable:* tapping Settings invokes `openSettings()` exactly once and never
    `openQuickActions()`. What it opens is `P4-04-settings.md`'s, and whether the two entry
    points resolve to the same surface is open there.

## Out of Scope

Referenced by filename rather than specified here:

- **Where Play Game leads, and its branch on whether open games exist** — the open-games
  list, the New Game row at the top, the opponent-name prompt and its `ItSaMeMaRiO` default →
  `P4-02-open-games-list.md`; the branch itself → `P2-01-navigation.md` requirement 5.
- **The theme selection overlay itself** — the rows, the two launch themes, the
  active-theme highlight, and the failed-to-load modal → `P4-03-theme-selection.md`. This PRD
  covers only the button that opens it and the fact that the menu hosts it.
- **The settings screen** → `P4-04-settings.md`.
- **The routing layer** — what "back" does, whether exiting a game pops or pushes this
  screen, the back-swipe gesture, and what the three named operations do underneath →
  `P2-01-navigation.md`.
- **Haptics.** No requirement here fires a buzz. The vibrate-on-touch setting, what counts as
  a valid click, and every haptic call site are `P2-03-haptics.md`'s; `P4-04-settings.md`
  req 8 owns the switch. *(That PRD states this PRD "carries **no** haptic requirement at all;
  haptics appear there only in its Out of Scope" — this is the bullet it relies on.)*
- **The button-tap sound.** `P2-02-audio.md` names this PRD a consumer of its `buttonTap`
  slot, but no requirement here fires one, and that PRD's own Out of Scope records `buttonTap`
  as having **no** call-site owner and no definition of which controls count as buttons (its
  OQ-4). Recorded as a gap below rather than closed here — assigning it would specify
  another PRD's surface.
- **The behind-menu dim while the theme overlay is open.** `2a` drops the menu to 35%
  opacity; that value and its ownership are recorded below and in
  `P4-03-theme-selection.md`. Requirement 15 settles only that the menu stays mounted.
- **The theme mechanism** — the theme object, YAML loading, UUID identity, merge-over-Neon,
  and the schema of every slot Requirement 10 consumes → `P1-03-theme-system.md`. This PRD
  reads those slots; it does not define them and does not author theme content.
- **Creating the logo asset** — the single Replicate API script and the designated asset
  folders. `Tech Design.md` → Decisions → *Where do sound and art assets come from?* decides
  the art is Replicate-generated **when actually needed and explicitly not now**, so this PRD
  states the dependency only → `P5-02-asset-generation-replicate.md`.
- **Changing the theme mid-game.** Theme changes happen from the main menu only.
  *(`Theming.md` → Decisions → Can you change the theme mid-game — **No**)*
- **The in-game route back to the main menu** — the top-right settings button and its quick
  actions live on the game screen, not here.
  *(`Menus and UI.md` → Decisions → How do you get back to the main menu from a game?)*
- **`Alternative Game Styles.md`** — declared parking lot; not what is being built.

## Open Questions

### From the design docs — unresolved, worded as the docs word them

- **Future menu items to consider later: Rules/How to Play, Settings, vs. AI, Online.**
  *(`Menus and UI.md` → Open Questions)* Requirement 1 builds the three buttons that are
  settled today; this list is not resolved here. Note that the *on-board* how-to-play layer
  is now in scope and owned by `P3-05-how-to-play.md`; whether a separate Rules/How to Play
  **menu item** exists is still open, and that PRD carries the same question.
- **App name?** *(`Tech Design.md` → Open Questions → 3. Build and distribution)* The menu
  title is directly gated on this — Requirement 7 settles that there *is* a title, not what
  it reads. The handoff draws `TIC TAC TOE` / `EXTREME` on 1a and `Menus and UI.md`'s own
  sketch shows `TIC TAC TOE EXTREME`, but neither is written as an answer to the app-name
  question, and the doc's own note says only the display name under the icon is still open.

### Carried from `P1-03-theme-system.md`, load-bearing here

- **Is screen padding a theme value?** *(`P1-03-theme-system.md` → Open Questions → Needs a
  decision, worded there as:)* "The handoff commits per-screen padding (`96 / 28 / 52` on the
  menu, 16pt sides on board screens, safe-area tops of 62 / 64 / 96). `Theming.md`'s inventory
  names board geometry and radii but not screen padding, so it is unclear whether these are
  theme slots or layout constants — and Requirement 25 makes the distinction load-bearing
  rather than cosmetic." It lands on Requirements 9 and 13 here: `96 / 28 / 52` and the 12pt
  button gaps are required values with no settled home, and the guard cannot see them either
  way.

### Contradiction between the docs and the approved handoff — flagged, not resolved

- **A fourth button: About Us.** `design_handoff_game_ui/README.md` → 1a draws `Settings` and
  `About Us` side by side, and the bundle includes a whole `1c — About Us` screen; the
  handoff's own screen table marks 1c *"new screen — copy TBD"*, and `Menus and UI.md` →
  Screens (so far) says outright: *"The handoff also draws an About Us screen (1c) that this
  doc does not list."* No design doc lists an About Us button or screen, and the drift note in
  Requirement 1 stops at three buttons. **This PRD specifies three buttons and no About Us
  requirement**, and Requirement 13's boundary keeps that from contradicting the
  pixel-fidelity clause. Whether the menu gains a fourth button — and whether 1c exists at
  all — needs a call. `P2-01-navigation.md` → Out of Scope records that no route to it is
  specified either.
- **The tagline and the version footer.** `1a` draws *"Nine boards. One winner. Good luck."*
  under the wordmark and `Theme: Neon · v0.1.0` at the foot. Neither appears in
  `Menus and UI.md` → Main Menu, whose sketch shows logo, title and buttons only. Requirement
  13 now **excludes** both rather than silently pulling them in; if either is wanted, it needs
  adding to that list — and the footer would additionally need a source for the app version
  and for the active theme's display name, which `P1-03-theme-system.md` records the schema
  has no place for.

### Layout the About Us call does not settle either way

- **What shape is the Settings button?** `1a` draws it as the left half of a two-up row it
  shares with About Us. Under three buttons that row has one occupant, and Requirement 6 is
  satisfied by full-width, by half-width left-aligned, and by half-width centered alike; none
  is pixel-faithful, and the handoff draws no single-occupant variant. This needs an answer
  whichever way About Us lands — if the fourth button arrives, the two-up row is the answer
  and the question closes; if it does not, one of the three has to be chosen.

### Slots this screen needs that Neon does not hold — named for the `P1-03` revision, not authored here

`neon.theme.json` has **no menu section at all**, so every value Requirement 13 fixes is
absent from the machine-readable base. `P1-03-theme-system.md` req 13 already refuses to
invent the difference; these are named so that revision has the list rather than deriving it
from the drawing again. All values are from `design_handoff_game_ui/README.md` → Screens → 1a
and Design tokens.

- **The gradient ground.** `radial-gradient(120% 65% at 50% 0%, #20233a 0%, #161826 58%,
  #111320 100%)` — the slot needs shape, focal position, extent and an *ordered multi-stop*
  list, not two endpoint colours. Note the handoff draws a **different ground per surface**
  (`1c` is a `linear-gradient(180deg, …)`), so one shared background slot may not serve.
- **The logo placeholder's nine values:** box 104, radius 20, fill `#1b1e2c`, 1px dashed
  `#5d5294`, glow `0 0 30px rgba(145,132,217,0.22)`, inner padding 11, grid gap 5, dot gap 2,
  dot `#9184d9` at 75%. **The dash on/off lengths are given nowhere** — a dashed border cannot
  be reproduced without them.
- **The kicker's scale entry** — 13pt, tracking 0.34em. It is in no type table; `type.scale`
  has no entry at 13 with that tracking.
- **Text colours for the kicker and the wordmark** — `#b5abfc` and the wordmark's own colour.
  The type scale carries sizes and weights, not colours, so these have nowhere to live today.
- **The wordmark's text glow** — `0 0 34px rgba(145,132,217,0.55)`. `neon.theme.json`
  expresses glows only as CSS `box-shadow` strings inside `board`; a **text**-shadow is a
  **new shape**, not a new key on an existing one.
- **The two button tiers' contents**, per tier: border colour and width (**2pt** vs **1px** —
  a genuine px/pt mix in the source), text colour and size (**20pt** vs **15pt**, neither in
  `type.scale`), padding (22 vs 16), radius, an **outer** glow **and** a separate **inset**
  glow (`0 0 24px rgba(145,132,217,0.28)` plus `inset 0 0 22px rgba(145,132,217,0.10)`).

**One radius disagreement to fix while placing these.** The handoff's Radius table reads
`control 12 · button 13 · large button 14`. `1a`'s large primaries draw **radius 14** —
`buttonLarge`, correct. But `1a`'s secondary draws **radius 12**, which is `control`, while
`button` 13 is what `1b`'s `+ NEW GAME` uses. So the secondary tier's radius is **`control`,
not `button`**, and `P1-03-theme-system.md` req 15 inherited the wrong one when it named the
radius set for this screen.

### Gaps recorded across sibling PRDs — not resolved here

- **Nothing fires the button-tap sound.** `P2-02-audio.md` req 6 maps *"Button taps / menu
  navigation"* to the `buttonTap` slot and names this PRD a consumer, while its own Out of
  Scope table records `buttonTap` as having **no** call-site owner, and its OQ-4 records that
  no doc or PRD defines which controls count as buttons. This screen has three of the most
  obvious candidates and no requirement firing one.
- **Who applies the 35% dim behind the theme overlay, and where does the value live?** `2a`
  specifies *"Menu behind drops to 35% opacity"* on top of a separate scrim
  (`rgba(15,16,24,0.72)`). Requirement 15 settles only that the menu stays mounted;
  `P4-03-theme-selection.md` records the dim as sheet chrome the sheet-surface slot does not
  cover, and `P1-03-theme-system.md` req 13 records that Neon holds no such value — its
  `scrim` 0.62 and `scrimHeavy` 0.72 are the layer *over* the menu, not the opacity *of* it.
  Whether the host menu dims itself or the overlay dims its parent is unassigned.
- **Is "Play Game" the string, or is `PLAY GAME` a theme text-transform?** Requirement 2
  settles the label from `Menus and UI.md`, which writes it in title case; `1a` draws it
  uppercase, as it draws `THEME` uppercase and `Settings` in title case. Nothing says whether
  casing is authored in the string or applied by the button tier's text style — and under
  Requirement 10 a text-transform would be a theme value.

### Raised by this PRD, not by the design docs (mine, and clearly marked)

- **What ships in place of the logo?** Requirement 8 defers the real art, and the handoff's
  dashed-border 81-dot placeholder is explicitly a placeholder. Whether that placeholder is
  shipped as-is until `P5-02-asset-generation-replicate.md` produces art, or the slot renders
  empty, is not settled anywhere.
