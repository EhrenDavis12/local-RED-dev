**Build-readiness: 92**

# PRD: Main Menu

> **Status:** Draft · Source docs read: `Menus and UI.md`, `Theming.md`, `Tech Design.md`,
> `Game Overview.md`, `Animations.md`, `Game Board Design.md`, `Rules.md`, `roadmap.md`, and
> the read-only reference asset `design_handoff_game_ui/` (`README.md` → *1a — Main Menu*,
> *1c — About Us*, *Fidelity*, *Design tokens*, *Assets*). `Alternative Game Styles.md` is a
> declared parking-lot doc and was not sourced from.
>
> **Revised for build-readiness.** Every theme value this screen reads is named by its **key
> path** from `P1-03-theme-system.md` requirement 15; the widget, its constructor and its
> providers are named; and the citations into `P2-01-navigation.md` were re-verified against
> that file's current numbering.
>
> **Revised again** after four rulings landed:
> - **About Us ships, as the last button** — requirement 1 is four buttons, requirement 6 is
>   the drawn two-up row, and `P2-01-navigation.md` req 21 accepted this PRD's `openAboutUs()`
>   proposal as written (requirement 23).
> - **The haptic fires on every valid tap anywhere in the app**, menu buttons included.
> - **One tap sound, everywhere** — every button, row and toggle. Both feedback channels are
>   requirement 24, which owns them together.
> - **Spacing and padding are fixed in code, not themed** — the padding fence in requirement 9
>   is deleted. Those numbers are now simply correct.
>
> **Why the stamp is not higher.** One user call remains — do the **tagline and version
> footer** ship (requirement 13's list) — fenced with a stated default, so nothing blocks. One
> schema gap in `P1-03` is still open (`surfaces.button.*` publishes no sub-keys), and the
> **About Us screen has no owner**, which this PRD flags and cannot fix.

**Wave:** P4 · **File:** `P4-01-main-menu.md` — parallel-safe with the other P4 PRDs.

**Dependencies:**

- `P1-01-app-scaffold.md` — creates `lib/ui/menus/`, the `ProviderScope` (its req 11) and the
  portrait lock (its req 7).
- `P1-03-theme-system.md` — the schema this screen compiles against. Every key it reads is
  listed in requirement 10 by path, and its req 24 publishes the accessor.
- `P2-01-navigation.md` — requirement **6** settles that the main menu is the app's launch
  screen, so this PRD does not restate it; requirement **7** holds the Play Game branch,
  requirement **9** the theme overlay over a still-mounted menu, requirement **10** the two
  settings entry points, and requirement **21** the About Us route. Its requirement **3**
  publishes the `AppNavigator` interface this screen calls and its requirement **4** the
  provider that supplies it.
- `P2-03-haptics.md` — requirement **14** publishes `HapticService` and
  `hapticServiceProvider`; requirement **15** owns `FakeHapticService`.
- `P2-02-audio.md` — requirement **2** publishes `AudioLayer` and `SoundMoment`, requirement
  **5** the provider. Its requirement **6** names **this PRD's requirement 24** as the
  call-site owner for the four menu buttons' `buttonTap`.

**Depended on by:** `P4-02-open-games-list.md`, `P4-03-theme-selection.md`,
`P4-04-settings.md` — each is a destination this screen launches and specifies its own
contents. All three are same-wave siblings, so the work is parallel-safe. **About Us is a
fourth destination with no PRD** — a gap rather than a dependency; see Out of Scope.

**The interfaces this screen must present, because another PRD already builds against them.**
`P2-01-navigation.md` requirement 2's route table contains
`builder: (context, state) => const MainMenuScreen()`, which fixes three things that are not
free choices:

```dart
// lib/ui/menus/main_menu_screen.dart
class MainMenuScreen extends ConsumerWidget {
  const MainMenuScreen({super.key});     // const, no required arguments
  @override
  Widget build(BuildContext context, WidgetRef ref) { … }
}
```

- **The class is `MainMenuScreen`.** Naming it `MainMenuPage` breaks that route table with no
  compile error at this PRD's boundary — the mismatch surfaces in `P2-01`'s file.
- **The constructor is `const` and takes no required arguments**, so **constructor injection
  is not available**: a dependency passed in would not compile against a const no-arg builder.
- **Everything is acquired through `ref`**, and each source is published rather than open:
  `ref.watch(activeThemeProvider)` for theme values (`P1-03` req 24, which states that
  provider **is the source of truth, not `Theme.of(context)`**),
  `ref.watch(appNavigatorProvider)` for navigation (`P2-01` req 4), and — at fire time, never
  captured — `ref.read(hapticServiceProvider)` and `ref.read(audioLayerProvider)` for the two
  feedback channels (`P2-03` req 14, `P2-02` req 5). No key, route, buzz or sound is reached
  by any other means.

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

The app has a main menu carrying a logo and a title above four buttons — **Play Game**,
**Theme**, **Settings** and **About Us** — where Play Game and Theme render from the same
large-primary button tier, because making it fun for kids to change the theme is the point of
putting it there. Every value on the screen resolves to a named key on the active theme, every
button change goes through one named navigation operation, and every press both buzzes and
clicks. Under Neon the screen reproduces the approved handoff drawing `1a — Main Menu` for the
elements requirement 13 enumerates.

## Requirements

### Structure and content

1. **The main menu presents exactly four buttons, in this order, top to bottom: Play Game,
   Theme, Settings, About Us.**
   *Source: `Menus and UI.md` → Main Menu → Buttons and → Screens (so far) → 1. Main Menu for
   the first three; **About Us is the user's ruling**, in their words: "We want the about us
   but it can be the last button in the list for now we might move it in the future but lets
   add it here." It agrees with `design_handoff_game_ui/README.md` → 1a, which draws it.*
   Recorded from the same doc section: the menu grew across the brain dump — first *"only a
   New Game button,"* then + Theme, then + Settings — and About Us is the fourth step in that
   same drift.
   *Testable:* the screen exposes exactly four tappable top-level controls, in that order.
   **About Us's position is provisional and the ordering is not load-bearing.** *"For now we
   might move it in the future"* — a later reorder is expected, not a reversal, so nothing
   downstream should depend on About Us being last. Only requirement 6's two-up row pairs it
   with a specific neighbour, and that pairing is what a reorder would revisit.

2. **The first button's label string is `'Play Game'`** — not `'New Game'`, and **not
   `'PLAY GAME'`**.
   *Source: `Menus and UI.md` → Decisions → Is the main menu button "New Game" or "Play
   Game?" — **Play Game**.* "New Game" survives only as an entry at the top of the open-games
   list, which is `P4-02-open-games-list.md`'s.
   **Casing is a theme value, not part of the string.** `1a` draws `PLAY GAME` and `THEME`
   uppercase while drawing `Settings` and `About Us` in title case; that transform is carried
   by the `uppercase` flag on the `type.scale` style each button tier references (`P1-03`
   req 15 → `type`, where `type.scale.<style>` carries an optional `uppercase`). Writing the
   literal `'PLAY GAME'` would make **every future theme** uppercase forever, with no key to
   turn it off — the Architectural Rule broken in a place the guard cannot see.
   *Testable:* the source contains `'Play Game'` and no uppercase button literal; with a
   fixture theme whose referenced style sets `uppercase: false`, the rendered label reads
   `Play Game`.

3. **Play Game renders from the large-primary tier and is the topmost button.**
   *Source: `Menus and UI.md` → Main Menu → Buttons: "Large."*
   *Testable:* it resolves its treatment from `surfaces.button.primary`, and its rendered
   height and type size are strictly greater than the Settings button's. Requirement 4 fixes
   the pair; this fixes that Play Game sits in the larger of the two tiers rather than merely
   differing from Settings.

4. **Play Game and Theme render from the same tier — `surfaces.button.primary`** — so equal
   visual weight is a property of the code rather than an obligation each theme honors
   separately. The doc's words are *"a nice big button, the same size and treatment as the
   Play Game button"*; a build in which the two read from different keys drifts apart the
   moment a theme overrides one of them.
   *Source: `Menus and UI.md` → Main Menu → Buttons ("Large, same weight as Play Game");
   `Theming.md` → Decisions → Where theme selection lives; `P1-03-theme-system.md` req 15 →
   `surfaces.button.{primary,secondary}`, **required**, cited there to `1a`, `2c` / `P4-01`
   reqs 4, 6. Corroborated by `design_handoff_game_ui/README.md` → 1a: "`PLAY GAME` and
   `THEME` — equal weight per the docs", identical border, glow, size, padding and radius.*
   *Testable:* both buttons resolve border, fill, text style, radius and glow from
   `surfaces.button.primary`; a fixture theme that changes one value in that key changes both
   buttons identically; no per-button override exists under `lib/ui/menus/`.

5. **Theme selection is reached from this screen and is deliberately not inside Settings.**
   Themes are *"up front, not buried in a settings screen."*
   *Source: `Menus and UI.md` → Main Menu; `Theming.md` → Decisions → Where theme selection
   lives.*
   *Testable:* `openThemeSelection()` is invoked from this screen, and
   `P4-04-settings.md`'s surface exposes no theme control.

6. **Settings and About Us both render from `surfaces.button.secondary`, sitting side by side
   as a two-up row** — not the primary tier requirements 3 and 4 reserve, and not two stacked
   full-width buttons.
   *Source: `Menus and UI.md` → Main Menu → Buttons ("Settings — opens the settings menu",
   with no "Large" qualifier, unlike the two above it); `design_handoff_game_ui/README.md` →
   1a, which draws exactly this: "`Settings` and `About Us` — side by side, 1px
   `rgba(233,233,237,0.16)` border, 15pt, padding 16, radius 12", against the two 20pt
   2pt-bordered buttons above; `P1-03-theme-system.md` req 15 → `surfaces.button.secondary`.*
   *Testable:* both resolve their treatment from `surfaces.button.secondary` and from no key
   under `surfaces.button.primary`; both occupy one row, sharing its width.
   **This was a fence in an earlier revision and is now a decision.** With three buttons the
   drawn row had one occupant and no faithful single-occupant form existed, so full-width was
   fenced as the honest default. About Us has landed, so the row has its drawn two occupants
   and the handoff — the approved design — is simply followed. If requirement 1's provisional
   ordering is later revisited, this pairing is the part that has to be revisited with it.

7. **The menu shows both a title and a logo** — both, not just buttons. The title is the
   two-part treatment `1a` draws: a kicker above a wordmark.
   *Source: `Menus and UI.md` → Decisions → Does the main menu need a title/logo? — **Yes —
   both a title and a logo.***
   *Testable:* a logo element and both title elements are present, with the strings
   requirement 13 pins.
   *Not this screen's:* the app's **display name under the icon** is still open
   (`Tech Design.md` → Open Questions → 3), and nothing here reads it.

8. **The logo renders through `surfaces.menu.logo`, framed by `surfaces.placeholder`, and
   ships as a placeholder.** Real art is deferred by decision — assets are generated with
   Replicate *"when we actually need them — not now"* — and `P1-03` req 15 marks
   `surfaces.menu.logo` **required** with its asset a placeholder, alongside
   `surfaces.placeholder.{border,radius,glow}`, which it cites to *"`1a`'s logo **and** `1c`'s
   avatars (`P4-01` req 8)"* — so the dashed frame is a published key with a published shape
   (`P1-03` req 35's ring object carries `style ∈ solid | dashed` plus `dashLength` /
   `dashGap`).
   *Source: `Tech Design.md` → Decisions → Where do sound and art assets come from?;
   `design_handoff_game_ui/README.md` → Fidelity, Screens → 1a, Assets → Logo ("Replace with
   real art"); `P1-03-theme-system.md` req 15, req 35.*
   *Testable:* no asset path literal appears under `lib/ui/menus/`, and both the logo and its
   frame come from those keys. Producing the art is `P5-02-asset-generation-replicate.md`'s.

### Theme-driven, with nothing hardcoded

9. **Every visual value on this screen resolves to a key on the active theme — and spacing is
   not one of them.**
   *Source: `Menus and UI.md` → Main Menu ("The entire main menu is itself theme-driven —
   background, button styling, title. No hardcoded styling here either."); `Theming.md` →
   Architectural Rule; `P1-03-theme-system.md` req 25.*

   **Spacing and padding are fixed in code by decision, not by exception.** `Theming.md` →
   Decisions → *Does a theme control spacing and padding?* settles it — *"No spacing will be
   fixed for now"* — and `P1-03` req 15 removed every `*.padding` key in schema v7, stating
   the boundary in its own terms: **a theme controls the drawn geometry of a thing itself**
   (stroke width, glyph size, corner radius, glow spread); **code controls where things sit
   relative to one another** (gaps, padding, margins). So requirement 13's `96 / 28 / 52` and
   12pt button gaps live in this screen's source, and that is correct rather than tolerated.
   *An earlier revision fenced these as a knowing violation pending that question. The fence
   is deleted; nothing on this screen is now an exception to anything.*
   *Testable:* every value in requirement 10's table resolves through `activeThemeProvider`;
   the only numeric literals under `lib/ui/menus/` are layout spacing.

10. **The menu reads exactly these keys, and declares no literal-valued style constant of its
    own.**

    | What it draws | Key path (`P1-03` req 15) |
    |---|---|
    | The gradient ground | `surfaces.menu.background` |
    | Kicker, wordmark, and the wordmark's glow | `surfaces.menu.kickerStyle`, `.wordmarkStyle`, `.wordmarkGlow` |
    | The logo, and its dashed frame | `surfaces.menu.logo`, `surfaces.placeholder.{border,radius,glow}` |
    | Play Game and Theme | `surfaces.button.primary` |
    | Settings and About Us | `surfaces.button.secondary` |
    | Corner radii | `radius.*` — referenced by the tiers; the menu spells no radius itself |
    | Type sizes, weights and the `uppercase` flag | `type.scale.*`, referenced by the tier styles |
    | Dim behind the theme overlay | `surfaces.menu.dimBehindOverlay` (requirement 17) |
    | Pressed / focused affordance | `surfaces.focusRing` (requirement 21) |
    | Tagline and footer, **if they ship** | `surfaces.menu.taglineStyle`, `.footerStyle` — see Open Questions |

    *Source: `P1-03-theme-system.md` req 15 → `surfaces`, `radius`, `type`. Every
    `surfaces.menu.*`, `surfaces.button.*` and `surfaces.placeholder.*` row there is
    **required** and cites `1a` and this PRD's reqs 4, 6, 7, 8 and 13, so each has a value in
    Neon by that PRD's req 11.*
    **The one theme key this screen does *not* read is `sound.buttonTap`** — requirement 24
    names a moment, and the audio layer resolves the path. See there.

    **`surfaces.button.*` is shared, not this screen's.** `P4-04-settings.md` reads the
    secondary tier for its exit control, and `P4-02-open-games-list.md` req 17 reads both tiers
    for the prompt's `Cancel` / `Start playing` pair on `2c`. A menu-local button style would
    silently fork all three.
    *Testable:* no `const` or `final` holding a colour, type size, radius, weight or glow value
    is declared under `lib/ui/menus/`. **Building `BoxDecoration`, `TextStyle` and
    `BorderRadius` from theme-sourced values is required, not banned** — the assertion is on
    *literal-valued* declarations, not on style objects, and layout spacing is exempt per
    requirement 9.

11. **Restyling the menu requires no change to menu code.**
    *Source: `Theming.md` → Architectural Rule; `P1-03-theme-system.md` req 26.*
    *Testable, wave 4 — against a fixture:* pump `MainMenuScreen` twice with
    `activeThemeProvider` overridden by two fixture themes differing in
    `surfaces.menu.background`, `surfaces.button.primary` and `surfaces.menu.wordmarkStyle`;
    the rendered values differ and no source file changes between runs.
    *Wave note:* the second **real** theme is `P5-01-classic-theme.md`, wave 5, which owns the
    cross-theme assertion. A wave-4 requirement cannot assert against a theme that does not
    exist yet, so it asserts against an injected fixture — the posture
    `P2-01-navigation.md` publishes for its own cross-wave testables.

12. **The menu passes the hardcoded-theme-value guard with the baseline at zero** — no colour
    literal or `Colors.*`, no `fontFamily:` or `GoogleFonts.*`, no `fontSize:` or
    `FontWeight.*`, no `BorderRadius.circular(<literal>)`, no `Duration(<literal>)`, no
    `assets/…` path.
    *Source: `Tech Design.md` → Decisions → Do we add a test that fails on hardcoded theme
    values?; the rule set is `P1-05-theme-guard-test.md` req 6, the baseline-at-zero its
    req 4(b).*
    *Testable:* `P1-05`'s scan reports zero findings under `lib/ui/menus/`.
    **Its stated limit is why requirement 10's testable exists separately:** the guard catches a
    value written into code, not a value read from the wrong key.

13. **Under Neon the screen reproduces `1a — Main Menu`, for the six elements below and no
    others.** The handoff's colors, type, spacing, radii and glow values are *"final and
    exact."*

    | # | Element | Drawn values |
    |---|---|---|
    | 1 | Ground | `radial-gradient(120% 65% at 50% 0%, #20233a 0%, #161826 58%, #111320 100%)` |
    | 2 | Frame | padding `96 / 28 / 52`, column, centered, 12pt gaps between buttons — **code-owned per requirement 9** |
    | 3 | Logo placeholder | 104×104, radius 20, fill `#1b1e2c`, 1px dashed `#5d5294`, glow `0 0 30px rgba(145,132,217,0.22)`; inside, an 11pt-padded 3×3 grid (gap 5) of 3×3 dot clusters (gap 2) in `#9184d9` at 75% — 81 dots |
    | 4 | Title | kicker `TIC TAC TOE` 13pt, tracking 0.34em, `#b5abfc`; wordmark `EXTREME` 44/600, glow `0 0 34px rgba(145,132,217,0.55)` |
    | 5 | Primary tier | outlined, 2pt `#9184d9` border on transparent, text `#9184d9`, 20pt, padding 22, radius 14, glow `0 0 24px rgba(145,132,217,0.28)` + `inset 0 0 22px rgba(145,132,217,0.10)` |
    | 6 | Secondary tier | `Settings` and `About Us` side by side, 1px `rgba(233,233,237,0.16)` border, 15pt, padding 16, radius 12 — the two-up row of requirement 6 |

    **This list is exhaustive.** The two things still drawn on `1a` and **not** required here
    are the tagline *"Nine boards. One winner. Good luck."* and the footer
    `Theme: Neon · v0.1.0`; both are held in Open Questions. The boundary matters because
    without it this requirement and requirement 1 would each imply a different button count —
    which is exactly what happened while About Us was unresolved.

    **Item 4 pins the title strings**, so the app-name question does not block this screen —
    only the display name under the icon is still open. **Item 3 pins the logo placeholder**, so
    nothing renders empty while `P5-02` is pending.

    **These values are Neon's, and Neon holds them by `P1-03` req 13**, which assigns
    transcription of *"the menu, the buttons"* from the handoff into `assets/themes/neon.yaml`.
    This screen reads them through requirement 10's keys; it authors none of them and must not
    transcribe them itself. The one exception is item 2, which is not a theme value at all.

    *Verification method:* a widget test at **402 × 874 logical points, `devicePixelRatio` 1.0**
    — the handoff's stated frame — asserting the resolved values element by element. A **golden
    image** at the same size is the cheaper form and is recommended; note that
    `Tech Design.md` → Decisions → *Widget tests for the board — no golden tests* scopes its
    no-goldens ruling to **the board**, and nothing extends it to screens. Flagged in Open
    Questions rather than assumed either way; the element-by-element assertions stand under both
    answers.
    *Source: `design_handoff_game_ui/README.md` → Fidelity, Design tokens, Screens → 1a,
    Spacing ("Screen frame is 402 × 874"); `Game Overview.md` header — the handoff "is the
    source of truth for what the game *looks like*".*

### Navigation out of the menu

Each button invokes one operation from `P2-01-navigation.md` requirement 3's `AppNavigator`
(extended by its requirement 21), obtained via `ref.watch(appNavigatorProvider)`. That PRD's
requirement 1 asserts that `go_router` is imported only under `lib/navigation/` and that no
`Navigator.`, `showDialog` or `showModalBottomSheet` appears under `lib/ui/` — so naming the
operation is part of the requirement: a menu widget that calls `Navigator.push` would satisfy
the intent of all four below and still fail that scan.

**Each testable below reads "no other *navigation* operation," deliberately.** Every press also
fires a haptic **and a sound** (requirement 24); neither is a navigation operation, so both are
already outside these clauses. An implementer reading an unqualified "and nothing else" would
conclude the button may do nothing but navigate — `P3-03` req 12 hit exactly this and narrowed
the same way. The narrowing covers both feedback channels because it names the *category*, not
a count.

14. **Play Game calls `playGame()`.** The branch on whether stored open games exist is
    evaluated inside the navigation layer; this screen never reads the count and never picks a
    destination.
    *Source: `Menus and UI.md` → Main Menu → Buttons; `Game Overview.md` → Modes ("Started from
    the **Play Game** button on the main menu"); the branch is `P2-01-navigation.md` req 7, the
    operation its req 3.*
    *Testable:* with `appNavigatorProvider` overridden by a recording fake, one tap records
    exactly one `playGame()` and no other navigation operation.
    **The button renders no loading state.** `P2-01` req 8 settles that the read is
    asynchronous, that the menu stays on screen while it is in flight, and that *"no spinner, no
    intermediate surface and no blank frame is specified"* — so nothing is required here.

15. **Theme calls `openThemeSelection()`.** The overlay opens over this menu, which stays
    mounted beneath it — in the route table `/theme` is a **child of `/`** with a non-opaque
    page, so the menu remaining mounted is a property of that table, not of this screen's
    discipline.
    *Source: `Menus and UI.md` → Decisions → Is theme selection its own screen or an overlay?
    ("**An overlay** on the main menu"); → Screens (so far) → 5; `P2-01-navigation.md` reqs 9
    and 2.*
    *Testable:* one tap records exactly one `openThemeSelection()` and no other navigation
    operation; in an integration test at `/theme`, `MainMenuScreen` is still in the widget
    tree. The overlay's contents are `P4-03-theme-selection.md`'s.

16. **Settings calls `openSettings()`** — the main menu's entry point, one of the two
    `P2-01-navigation.md` req 10 settles.
    *Source: `Menus and UI.md` → Main Menu → Buttons; → Settings Menu ("Reachable from two
    places: 1. The **main menu** (Settings button)"); `P2-01-navigation.md` reqs 10, 3.*
    *Testable:* one tap records exactly one `openSettings()`, never `openQuickActions()`, and
    no other navigation operation. Whether the two entry points render the same surface is open
    in `P4-04-settings.md`.

### Behavior this screen owns that the drawings imply

*Appended after requirement 16 so requirements 1–16 keep their numbers —
`P1-03-theme-system.md` req 15 cites reqs 4, 6, 7, 8 and 13, `P2-01-navigation.md` cites
reqs 14–16 and 23, and `P2-02-audio.md` req 6 and `P2-03-haptics.md` req 1 both cite req 24.*

17. **While the theme overlay is open, the menu dims itself to
    `surfaces.menu.dimBehindOverlay`.** This is the host's job, not the overlay's: the key sits
    under `surfaces.menu.*`, and only the menu can change its own opacity.
    *Source: `design_handoff_game_ui/README.md` → 2a ("Menu behind drops to 35% opacity");
    `P1-03-theme-system.md` req 15, where `surfaces.menu.dimBehindOverlay` is **required** and
    cited to `2a` at 35%.*
    *Testable:* at `/theme` the menu subtree renders at the key's opacity; back at `/` it
    renders at full opacity; the value comes from the key, not from the widget.
    **Distinct from the scrim**, which is a layer painted *over* the menu and belongs to
    `P4-03-theme-selection.md` via `surfaces.scrim.themeSelect`. Both are drawn on `2a`.

18. **A second tap on a button whose surface is already open does nothing** — no second
    navigation, no second buzz, no second tap sound. Tapping Theme twice must not stack two
    overlays; the same holds for Settings and About Us.
    *Testable:* two taps 50 ms apart record exactly one navigation invocation, one haptic and
    one `SoundMoment.buttonTap`.
    *PRD-author judgment, reversible, and fenced rather than left silent:* no doc addresses it,
    and the failure is a duplicate route that only two `dismissCurrent()` calls will clear. It
    mirrors the re-entrancy rule `P2-01-navigation.md` req 8 already states for `playGame()`,
    which is the same hazard behind a slower operation.

19. **The screen is portrait-only and lays out without overflow from 320 pt wide upward.**
    Portrait is settled app-wide; the width floor follows from the settled minimum OS version.
    *Source: `Tech Design.md` → Decisions → Orientation — portrait only, and → Minimum iOS
    version (**iOS 13**, which reaches the 320 pt-wide iPhone SE 1st generation);
    `P1-01-app-scaffold.md` req 7 holds the lock.*
    *Testable:* pumped at 320×568 and at 402×874, no overflow is reported and all four buttons
    and both title elements are hit-testable. Requirement 13's fidelity assertions apply at
    402×874 only.
    *Fenced default:* the handoff draws one frame and states no responsive rule, so the behavior
    between widths is **scale nothing, let the column stretch** — padding and type sizes stay
    fixed, the primary buttons take the remaining width, and requirement 6's row splits it.
    Reversible.

20. **The menu does not scale its text with the OS text-size setting.**
    *Source: `Menus and UI.md` → Decisions → Do we support Dynamic Type? — **"Not for now. Lets
    not do this as of yet."***
    **This screen does not implement the clamp.** Flutter's default follows the OS factor, so
    honoring that decision needs a `MediaQuery` clamp at the app root — and
    `P4-04-settings.md` req 17 records that **no PRD owns it**. Stated here so an agent does not
    solve it locally on one screen, which would leave the other eleven scaling.

21. **Every button exposes a pressed and a focused state, both drawn from the theme** —
    `surfaces.focusRing` for focus, and the pressed treatment from the button tier.
    *Source: `P1-03-theme-system.md` req 15, where `surfaces.focusRing` is **required**, cited
    to `README.md` → *Interactions & behavior*.*
    *Testable:* no interaction state is drawn from a literal, and the focus indicator resolves
    to `surfaces.focusRing`.
    *Gap, not resolved here:* `1a` draws no pressed state and `surfaces.button.*` publishes no
    sub-keys, so what a press *looks like* has no value behind it — see Open Questions.

22. **If the active theme fails to load, the menu renders whatever the fallback resolves to and
    shows no failure UI of its own.** `P1-03` req 27 falls back to Neon and puts the "theme
    unavailable" modal on the Theme screen; this screen must not render a partial theme and must
    not duplicate that modal.
    *Source: `P1-03-theme-system.md` reqs 27, 28; the modal is `P4-03-theme-selection.md`
    reqs 20–21.*
    *Testable:* with a loader stubbed to fail the active theme, the menu renders every
    requirement 10 key at Neon's values and presents no error surface.

23. **About Us calls `openAboutUs()`.** It pushes `/about` as an ordinary opaque page, a child
    of `/`.
    *Source: the user's ruling under requirement 1; `P2-01-navigation.md` **req 21**, which
    added `openAboutUs()` as the eleventh operation on `AppNavigator` and `Routes.aboutUs` to
    its path constants — accepting this PRD's proposal as written, and recording it as
    settled: "How About Us is reached. Settled — requirement 21's `openAboutUs()` and
    `/about`."*
    *Testable:* one tap records exactly one `openAboutUs()` and no other navigation operation.
    **What that route renders is a different question, and it has no owner** — see Out of
    Scope. `P2-01` req 21 builds `const AboutUsScreen()` and notes the screen is unowned; its
    own testable is written so the route resolves against a placeholder, which is what lets
    this button be built before the screen behind it exists.

24. **Activating any of the four buttons fires one haptic and one sound**, via
    `ref.read(hapticServiceProvider).validAction()` and
    `ref.read(audioLayerProvider).play(SoundMoment.buttonTap)`.

    *Source — two Decisions, deliberately symmetrical:* `Game Board Design.md` → Decisions →
    **Does the haptic fire on non-board controls?** (the haptic fires on every valid tap
    anywhere in the app, menu buttons included) and `Theming.md` → Decisions → **Do non-board
    controls make a sound?** — *"**Yes — one tap sound, everywhere.** Every button, row and
    toggle plays the same short tap sound: menu buttons, theme rows, settings toggles…"*, which
    grounds itself in the haptic ruling *"so the two feedback channels now behave consistently
    rather than one buzzing where the other is silent."*
    *Interfaces:* `P2-03-haptics.md` req 14 (`HapticService`, `hapticServiceProvider`);
    `P2-02-audio.md` reqs 2 and 5 (`AudioLayer`, `SoundMoment`, `audioLayerProvider`).

    **Both channels are held in one requirement on purpose.** `P2-02` req 6 names *"`P4-01`
    req 24 (the four menu buttons)"* as the `buttonTap` call-site owner, and `P2-03` req 1
    names the same number for the haptic. One press is one gesture with two feedback calls;
    splitting them across two requirement numbers would leave one sibling's citation pointing
    at the wrong half.

    **The screen reads neither setting and branches on neither.** `validAction()` takes no
    argument and `play` takes only a moment; both layers gate mute internally — `P2-03` req 14
    (*"callers never check the setting"*) and `P2-02` req 2 (*"The mute gate is INSIDE this
    call"*). A call site that gated for itself is the failure mode both layers exist to
    prevent. This screen therefore reads no `sound` key: it names a moment, and the audio layer
    resolves the path from the active theme.
    **`buttonTap` is one moment and one file, not a family** — `P2-02` req 6, and the schema
    has exactly one `sound.buttonTap` key. There is no per-button variation to express.

    *Testable — and the fake matters.* Override **both** providers in the `ProviderScope`:
    `hapticServiceProvider` with `FakeHapticService` (`test/haptics/fake_haptic_service.dart`,
    `int get count` — `P2-03` req 15) and `audioLayerProvider` with **`FakeAudioLayer`**
    (`P2-02`). One press of each button records `count == 1` and exactly one
    `SoundMoment.buttonTap`; four presses record four of each.
    > **Use `FakeAudioLayer`, not `RecordingOneShotSink`.** `P2-02` req 16 carries a ⚠ against
    > using the fake for *its* gate assertion, because overriding `audioLayerProvider` replaces
    > the gate. That is precisely why the fake is right *here*: this requirement asserts that
    > the **call site fires**, which must hold whether or not sound is muted. The sink sits
    > below the gate and answers a different question — whether anything was audible — which is
    > `P2-02`'s to assert, not this screen's.

    *Wave note:* `P2-02` req 6 and `P2-03` req 1 both state that a control's tap reaching the
    layer exactly once is a **call-site fact owned by each calling PRD**. This is that
    assertion for these four buttons; neither layer asserts it for us.

## Out of Scope

Referenced by filename rather than specified here:

- **Where Play Game leads** — the open-games list, the New Game row, the opponent-name prompt
  and its `ItSaMeMaRiO` default → `P4-02-open-games-list.md`; the branch itself →
  `P2-01-navigation.md` req 7.
- **The theme selection overlay** — rows, preview tiles, the active highlight, the scrim, the
  failure modal → `P4-03-theme-selection.md`. This PRD owns the button, the host, and the dim
  (requirement 17).
- **The settings surface** → `P4-04-settings.md`.
- **The About Us screen itself — and it has no owner.** This PRD owns the *button*
  (requirements 1, 6, 23, 24) and nothing beyond it. **No PRD specifies screen `1c`**: not its
  copy, not its team grid, not its back control, not its theme keys — `P1-03-theme-system.md`
  req 15 has no `surfaces.about*` row, so today the screen has no slots to read from either.
  Two things are unsettled inside it and are recorded rather than resolved:
  - **The content is unspecified.** `1c`'s two body paragraphs are marked *"placeholder copy"*
    and the handoff's *Still to design* lists *"Real logo and About Us copy."*
  - **The team photos have no source.** `P5-02-asset-generation-replicate.md` → Open Questions
    records that *"Screen `1c` is absent from `Menus and UI.md` → Screens (so far) and **no PRD
    owns it**, so neither the screen nor its photos have a home,"* and doubts it is an
    asset-generation question at all: *"real team photos are not something Replicate
    produces."*

  **Corroborated, not solitary:** `P2-01-navigation.md` → Open Question 16 records the same
  gap from the routing side, and states it is the one item it would not let go quiet. Two PRDs
  now flag a screen neither owns — the same shape as the turn banner, which four PRDs declined
  before the user ruled.
- **The haptic layer and the audio layer.** Requirement 24 is a *call site* for both.
  Everything behind it — `HapticService`, `AudioLayer`, the two mute gates, what the buzz feels
  like, which file `buttonTap` resolves to, the platform call, the `audioplayers` integration,
  and the guarantee that one call yields at most one buzz or one sound — belongs to
  `P2-03-haptics.md` and `P2-02-audio.md`. The two switches are `P4-04-settings.md` reqs 8 and
  7's.
  *Previously recorded here as an asymmetry — the haptic settled while the sound was not,
  leaving menu buttons buzzing but silent. **Both are now settled**, `P2-02`'s OQ-3 is closed
  by `Theming.md` → Decisions → Do non-board controls make a sound?, and requirement 24 covers
  both channels.*
- **The routing layer** — the route table, what "back" does, page opacity, and what the
  operations do underneath → `P2-01-navigation.md`.
- **Authoring theme values.** `assets/themes/neon.yaml` is `P1-03-theme-system.md` req 13's,
  including every `surfaces.menu.*`, `surfaces.button.*` and `surfaces.placeholder.*` value
  requirement 13 quotes, and the `sound.buttonTap` asset. This screen reads keys and
  transcribes nothing.
- **The app-root text-scale clamp** (requirement 20) — unowned; `P4-04-settings.md` req 17.
- **Producing the logo art and the tap sound file** → `P5-02-asset-generation-replicate.md`.
- **Changing the theme mid-game.** Theme changes happen from the main menu only.
  *(`Theming.md` → Decisions → Can you change the theme mid-game — **No**)*
- **`Alternative Game Styles.md`** — declared parking lot; not what is being built.

## Open Questions

### Settled since the last revision — recorded, with what each did not settle

- **About Us ships, as the last button.** Absorbed into requirements 1, 6, 13, 23 and 24. It
  did **not** settle the button's position (*"we might move it in the future"* — requirement 1
  records the ordering as provisional) or the screen behind it (unowned, no content — Out of
  Scope).
- **The haptic fires on every valid tap anywhere in the app**, and **one tap sound plays
  everywhere.** Both absorbed into requirement 24. The asymmetry this PRD flagged in the
  previous revision — one channel settled, the other not — is closed in both directions.
- **Spacing and padding are fixed in code.** Requirement 9's fence is deleted. The user's hedge
  is *"for now"*, per `P1-03` req 15's own note, so this may return.

### Needs the user

1. **Do the tagline and the version footer ship?** `1a` draws *"Nine boards. One winner. Good
   luck."* under the wordmark and `Theme: Neon · v0.1.0` at the foot; neither appears in
   `Menus and UI.md` → Main Menu, whose sketch shows logo, title and buttons only. Requirement
   13 **excludes both**. The styling keys exist (`surfaces.menu.taglineStyle`, `.footerStyle`,
   both **required**), and the theme's display name is now available — `P1-03` req 24's
   `themeCatalogProvider` carries `{id, name, blurb, assetKey}` per entry, and schema v4 added
   `meta.name`. **What is still missing is the app version string**, which no PRD supplies. If
   the footer ships, that needs a home.

### Schema gap in `P1-03-theme-system.md` this screen would otherwise invent

Rechecked against schema **v7**; two gaps from an earlier revision are now closed — the
**gradient shape** is defined in req 35 (`{type: linear | radial, stops: [{at, color}], …}`,
`center` + `extent` for radial) and the **dashed-border metrics** have both a shape
(`dashLength` / `dashGap`) and a key (`surfaces.placeholder`, cited to `1a`'s logo and `1c`'s
avatars). One remains:

- **`surfaces.button.{primary,secondary}` publishes no sub-keys.** Every comparable row in that
  table publishes its fields — `gameRow` lists seven, `themeRow` five, `input` seven — while
  the button row publishes only the two tier names. The tiers need, per tier: border colour and
  width (**2pt** vs **1px** — a genuine pt/px mix in the source), text colour and size (**20pt**
  vs **15pt**, neither in `type.scale`), a `radius.*` reference, an **outer** glow **and** a
  separate **inset** glow, plus the pressed and focused states requirement 21 needs. Three
  consumers read this key — this PRD, `P4-02` req 17 and `P4-04` — so without sub-keys they
  bind three shapes.

**One correction still to route.** `P4-04-settings.md`, in its exit-control requirement, quotes
`P1-03` req 15 as saying *"Two button tiers, not one — a large primary (Play Game, Theme) and a
secondary (Settings)."* **That sentence is not in `P1-03`**; its schema table carries the key
row without the prose. The requirement number and the key are both right, so the citation points
at the correct address with words that are not there. This PRD carried the same phantom quote
and now cites the key path instead.

### Method question, flagged rather than assumed

- **Does the no-goldens decision extend from the board to screens?** `Tech Design.md` →
  Decisions → *Widget tests for the board — no golden tests* says *"Widget tests, no goldens.
  Test that taps do the right thing and that the highlight states appear."* Requirement 13 asks
  for pixel fidelity against an approved drawing, which is the case goldens exist for, and the
  decision is scoped to the board by its own title. If goldens are off everywhere, requirement
  13's element-by-element assertions are the fallback and are already written that way — this
  decides cost, not buildability.
