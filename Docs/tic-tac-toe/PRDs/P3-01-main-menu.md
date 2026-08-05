# PRD: Main Menu

> **Status:** Draft · Source docs read: `Menus and UI.md`, `Theming.md`, `Tech Design.md`,
> `Game Overview.md`, `Animations.md`, `Game Board Design.md`, `Rules.md`, `roadmap.md`, and
> the read-only reference asset `design_handoff_game_ui/` (`README.md` → *1a — Main Menu*,
> *Fidelity*, *Design tokens*, *Assets*). `Alternative Game Styles.md` is a declared
> parking-lot doc and was not sourced from.

**Wave:** P3 · **File:** `P3-01-main-menu.md`

**Depends on:** `P1-01-app-scaffold.md` (the `lib/ui/menus/` home and the Riverpod root),
`P1-03-theme-system.md` (the theme object this screen reads every value from — including its
`main menu styling` slot).

**Depended on by:** `P3-02-open-games-list.md`, `P3-03-theme-selection.md`,
`P3-04-settings.md` — each is a destination this screen launches, and each specifies its own
behavior.

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
the approved handoff drawing `1a — Main Menu`.

## Requirements

### Structure and content

1. **The main menu presents exactly three buttons: Play Game, Theme, and Settings.**
   *(`Menus and UI.md` → Main Menu → Buttons; Screens (so far) → 1. Main Menu)*
   Recorded from the same section: the menu grew across the brain dump — first *"only a New
   Game button,"* then + Theme, then + Settings — and **three buttons is where it currently
   stands**. Anything beyond three is Open Questions, below.

2. **The first button is labelled "Play Game", not "New Game".**
   *(`Menus and UI.md` → Decisions → Is the main menu button "New Game" or "Play Game?" —
   **Play Game**)* "New Game" survives only as an entry at the top of the open-games list,
   which is `P3-02-open-games-list.md`'s territory.

3. **Play Game is large** — the dominant control on the screen.
   *(`Menus and UI.md` → Main Menu → Buttons: "Large.")*

4. **Theme is large and carries the same visual weight as Play Game** — "a nice big button,
   the same size and treatment as the Play Game button." The two are styled as a matched
   pair; neither is subordinate to the other.
   *(`Menus and UI.md` → Main Menu → Buttons: "Large, same weight as Play Game"; `Theming.md`
   → Decisions → Where theme selection lives; corroborated by
   `design_handoff_game_ui/README.md` → 1a: "`PLAY GAME` and `THEME` — equal weight per the
   docs", identical border, glow, size, padding and radius)*

5. **Theme selection is reached from the main menu and is deliberately not inside Settings.**
   Themes are *"up front, not buried in a settings screen."* A build that satisfies every
   other requirement but reaches themes only through Settings fails this one.
   *(`Menus and UI.md` → Main Menu; `Theming.md` → Decisions → Where theme selection lives)*

6. **Settings is the third button and is not given the large treatment** that Requirements 3
   and 4 reserve for Play Game and Theme. In the approved drawing it is a smaller secondary
   control.
   *(`Menus and UI.md` → Main Menu → Buttons — "Settings — opens the settings menu", with no
   "Large" qualifier, unlike the two above it; `design_handoff_game_ui/README.md` → 1a, where
   `Settings` is 15pt with a 1px hairline border against the two 20pt 2pt-bordered buttons)*

7. **The menu shows both a title and a logo** — both, not just buttons.
   *(`Menus and UI.md` → Decisions → Does the main menu need a title/logo? — **Yes — both a
   title and a logo.**)*

8. **The logo ships as a placeholder in this PRD.** Real logo art is explicitly deferred:
   assets are generated with Replicate *"when we actually need them — not now."* The handoff
   marks its 1a logo a placeholder — a dashed-bordered 81-dot mark — and *"Replace with real
   art."*
   *(`Tech Design.md` → Decisions → Where do sound and art assets come from?;
   `design_handoff_game_ui/README.md` → Fidelity, Screens → 1a, Assets → Logo)* Producing the
   art and the Replicate script is `P5-01-asset-generation-replicate.md`.

### Theme-driven, with nothing hardcoded

9. **Every visual value on this screen is read from the active theme — background, button
   styling, and title. No hardcoded styling anywhere in the menu.**
   *(`Menus and UI.md` → Main Menu: "The entire main menu is itself theme-driven —
   background, button styling, title. No hardcoded styling here either."; `Theming.md` →
   Architectural Rule)*

10. **The menu reads the theme's existing `main menu styling` slot** — background, button
    look, title — rather than introducing menu-local style constants.
    *(`Theming.md` → What a Theme Controls → Visual: "Main menu styling (background, button
    look, title)"; slots are defined by `P1-03-theme-system.md`)*

11. **Restyling the main menu for a new theme requires zero changes to menu code** — only a
    new theme definition. Testable as: switching the active theme changes the menu's
    background, button styling and title without touching `lib/ui/menus/`.
    *(`Theming.md` → Architectural Rule)*

12. **The menu passes the hardcoded-theme-value test with no baseline entries** — no
    `Color(0x…)`, `Colors.*`, literal `fontFamily:`, `GoogleFonts.*`, hardcoded `Duration(…)`
    or literal `assets/…` path in the menu's source.
    *(`Tech Design.md` → Decisions → Do we add a test that fails on hardcoded theme values? —
    the baseline starts at zero; the test itself is `P1-05-theme-guard-test.md`)*

13. **Under the Neon theme the screen recreates `1a — Main Menu` from the approved handoff**,
    whose colors, type, spacing, radii and glow values are final and exact and are to be
    recreated pixel-for-pixel: the radial-gradient ground, `96 / 28 / 52` padding, the
    104×104 logo placeholder, the `TIC TAC TOE` kicker over the `EXTREME` 44/600 wordmark,
    and the button treatments in Requirements 4 and 6.
    *(`design_handoff_game_ui/README.md` → Fidelity; Screens → 1a; Design tokens;
    `Game Overview.md` header — the handoff "is the source of truth for what the game *looks
    like*")* The Neon values themselves come from `P1-03-theme-system.md`; this PRD requires
    only that the menu render them.

### Navigation out of the menu

14. **Play Game starts play from the main menu.** What happens next — the branch on whether
    open games exist — is specified in `P3-02-open-games-list.md` and not here.
    *(`Menus and UI.md` → Main Menu → Buttons; `Game Overview.md` → Modes: "Started from the
    **Play Game** button on the main menu.")*

15. **Theme opens theme selection as an overlay on the main menu, not a separate screen** —
    the menu stays the host and remains beneath the overlay.
    *(`Menus and UI.md` → Decisions → Is theme selection its own screen or an overlay? — **An
    overlay** on the main menu; `Menus and UI.md` → Screens (so far) → 5)* The overlay's own
    content and behavior are `P3-03-theme-selection.md`.

16. **Settings opens the settings menu.** Its contents are `P3-04-settings.md`.
    *(`Menus and UI.md` → Main Menu → Buttons; Settings Menu — "Reachable from two places:
    1. The **main menu** (Settings button).")*

## Out of Scope

Referenced by filename rather than specified here:

- **Where Play Game leads, and its branch on whether open games exist** — the open-games
  list, the New Game row at the top, the opponent-name prompt and its `ItSaMeMaRiO` default →
  `P3-02-open-games-list.md`.
- **The theme selection overlay itself** — the rows, the two launch themes, the
  active-theme highlight, and the failed-to-load modal → `P3-03-theme-selection.md`. This PRD
  covers only the button that opens it and the fact that the menu hosts it.
- **The settings screen** — the sound, vibrate and animations toggles and their persistence →
  `P3-04-settings.md`.
- **The theme mechanism** — the theme object, YAML loading, UUID identity, merge-over-Neon,
  and the `main menu styling` slot's schema → `P1-03-theme-system.md`. This PRD consumes
  those slots; it does not define them.
- **Creating the logo asset** — the single Replicate API script and the designated asset
  folders. `Tech Design.md` → Decisions → *Where do sound and art assets come from?* decides
  the art is Replicate-generated **when actually needed and explicitly not now**, so this PRD
  states the dependency only → `P5-01-asset-generation-replicate.md`.
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
  settled today; this list is not resolved here.
- **App name?** *(`Tech Design.md` → Open Questions → 3. Build and distribution)* The menu
  title is directly gated on this — Requirement 7 settles that there *is* a title, not what
  it reads. The handoff draws `TIC TAC TOE` / `EXTREME` on 1a and `Menus and UI.md`'s own
  sketch shows `TIC TAC TOE EXTREME`, but neither is written as an answer to the app-name
  question, and the doc's own note says only the display name under the icon is still open.

### Contradiction between the docs and the approved handoff — flagged, not resolved

- **A fourth button: About Us.** `design_handoff_game_ui/README.md` → 1a draws `Settings` and
  `About Us` side by side, and the bundle includes a whole `1c — About Us` screen; the
  handoff's own screen table marks 1c *"new screen — copy TBD"*, and `Menus and UI.md` →
  Screens (so far) says outright: *"The handoff also draws an About Us screen (1c) that this
  doc does not list."* No design doc lists an About Us button or screen, and the drift note in
  Requirement 1 stops at three buttons. **This PRD specifies three buttons and no About Us
  requirement.** Whether the menu gains a fourth button — and whether 1c exists at all —
  needs a call.
- **Handoff elements on 1a that no design doc mentions:** the tagline *"Nine boards. One
  winner. Good luck."* under the wordmark, and the footer `Theme: Neon · v0.1.0`.
  Requirement 13 asks for a pixel-faithful recreation of 1a, so as written it pulls both in;
  neither appears in `Menus and UI.md` → Main Menu, whose sketch shows logo, title and
  buttons only. If either is not wanted, Requirement 13 needs narrowing.

### Raised by this PRD, not by the design docs (mine, and clearly marked)

- **Is the main menu the app's launch screen?** Every doc treats it as the root — it is
  screen 1, the in-game exit returns to it, and Neon is *"what a player sees before they've
  ever opened theme selection"* — but no Decision states it, so an implementer is inferring
  it.
- **What ships in place of the logo?** Requirement 8 defers the real art, and the handoff's
  dashed-border 81-dot placeholder is explicitly a placeholder. Whether that placeholder is
  shipped as-is until `P5-01` produces art, or the slot renders empty, is not settled
  anywhere.
