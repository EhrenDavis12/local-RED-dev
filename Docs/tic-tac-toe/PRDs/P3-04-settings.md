# PRD: Settings — the three toggles, from both entry points

> **Status:** Draft · Source docs read: `Menus and UI.md`, `Theming.md`, `Animations.md`,
> `Game Board Design.md`, `Tech Design.md`, `Game Overview.md`, `Rules.md`.
> (`Alternative Game Styles.md` is a parking-lot doc and was not sourced.
> `design_handoff_game_ui/` is a read-only reference asset — screens `2b` and `1f` were
> read, and where the handoff and the docs disagree the disagreement is recorded under Open
> Questions rather than resolved. No requirement below is sourced from the handoff.)

**Wave:** P3 — the settings surface itself, once the things it switches off exist.

**Dependencies:**

- `P1-04-persistence.md` owns storing and restoring the four preferences. This PRD reads
  and writes through that layer and defines no storage of its own.
- `P1-03-theme-system.md` owns the theme object and its materialization. This PRD requires
  only that the three toggles are *not* part of it.
- `P3-01-main-menu.md` owns the Settings button on the main menu; this PRD owns what that
  button opens.
- `P2-03-scoreboard-turn-indicator.md` owns the placement of the in-game settings button in
  the scoreboard strip; this PRD owns what tapping it opens.
- `P4-01-audio.md`, `P4-02-haptics.md`, `P4-03-animations.md` own the three channels. This
  PRD owns the player-facing switch for each and what "off" means; they own the mechanism.

## Problem

Sound, haptics and animations are all theme-driven or app-driven behaviors a player has no
way to stop. There is no application code yet, so today there is no settings surface at
all: no way to mute a theme (`Theming.md` → Sound Decisions → Global mute), no way to turn
off the buzz that fires on every valid tap (`Menus and UI.md` → Vibrate on Touch), and no
way to turn animations off (`Animations.md` → Decisions → Turn animations off). Worse for
the pass-and-play case, there is also no way out of a game short of finishing it — the
docs put the exit inside this same surface (`Menus and UI.md` → Decisions → How do you get
back to the main menu from a game?), so without it a player who starts a game is stuck in
it.

## Goal

A player can reach settings from two places — the main menu's Settings button and the
gameplay screen's top-right button — and from either one switch sound effects, vibrate on
touch and animations on or off. The three are global, player-owned and remembered between
sessions, so a theme can never override them; and because the in-game route is a set of
quick actions that also contains "exit to main menu", a player can change a setting or
walk away mid-game without losing the game, which stays in the open-games list with its
own scoreboard.

## Requirements

### Entry points

1. **The main menu's Settings button opens the settings surface.**
   *Source: `Menus and UI.md` → Main Menu ("**Settings** — opens the settings menu");
   → Settings Menu ("Reachable from two places: 1. The **main menu** (Settings button)");
   → Screens (so far) #6.*

2. **The gameplay screen's settings button opens the settings surface too, and reaching it
   does not abandon or end the game in progress.** The doc calls this the important
   requirement of the two: settings must be available mid-game.
   *Source: `Menus and UI.md` → Settings Menu ("2. The **gameplay screen** — you can get to
   settings without abandoning a game. That second one is the important requirement");
   → How you reach settings from gameplay; `Game Board Design.md` → Scoreboard.*
   *Testable:* open the surface mid-game, dismiss it, and the board, whose turn it is, the
   pending selection state and the scoreboard are exactly as they were.

3. **The in-game entry point opens *quick actions* — a short list of things you can do
   mid-game — not just a list of toggles.** Contents so far: exit the game / back to the
   main menu, plus the sound effects and vibrate toggles.
   *Source: `Menus and UI.md` → How you reach settings from gameplay ("Tapping it opens
   **quick actions** — a short list of things you can do mid-game, including **exit the
   game** back to the main menu"), and its **Quick actions contents (so far)** list.*
   *Note:* whether the Animations toggle also appears here follows from Open Question 1 —
   the doc's quick-actions list names only sound and vibrate, while the Settings Menu
   section names three toggles.

4. **The settings button does double duty in-game: it is both the settings entry point and
   the way out of a game.** Exiting is available without finishing the game.
   *Source: `Menus and UI.md` → How you reach settings from gameplay ("So the settings
   button does double duty in-game"); → Decisions → How do you get back to the main menu
   from a game? ("It opens quick actions, which include exiting the game. You don't have to
   finish a game to leave it").*

5. **Exiting from quick actions returns the player to the main menu and discards nothing.**
   The game stays in the open-games list with its own scoreboard and is resumable.
   *Source: `Menus and UI.md` → Leaving a game mid-play ("going back to the main menu
   doesn't discard anything — the game stays in the open-games list with its own
   scoreboard, and you can pick it up again"); → Decisions → What does an open game hold?;
   `Game Overview.md` → Decisions → Scoreboard lifetime.*
   *Testable:* leave mid-game, return to the open-games list, reopen the same game, and the
   board and its running series score are unchanged.

### The three toggles

6. **The settings surface offers exactly three toggles — Sound effects, Vibrate on touch,
   Animations — each a plain on/off.** There is no fourth setting.
   *Source: `Menus and UI.md` → Settings Menu ("Contents so far — three toggles" table);
   → Persistence (the persisted preferences are theme, sound, vibrate, animations — "So
   there are four persisted preferences").*
   *Note:* the handoff draws a fourth, **Music**, in both `2b` and `1f` — see Open
   Question 3.

7. **Sound effects is a global mute.** It is global for the whole game rather than
   per-theme, it is separate from the theme, and it mutes *any* theme.
   *Source: `Theming.md` → Sound Decisions → Global mute ("**Global for the whole game**,
   not per-theme"); `Menus and UI.md` → Decisions → Should there be a mute button, and
   where does it live? ("it mutes any theme").*
   *Testable:* with sound off, switch between Neon and Classic Red vs Blue and no sound
   plays under either.

8. **Vibrate on touch switches the haptic on and off.** With it on, the haptic fires on
   every valid click, including the first tap of a two-tap move; with it off, no haptic
   fires anywhere.
   *Source: `Menus and UI.md` → Settings Menu table ("Haptic feedback on tap. Fires on
   every *valid* click. On/off"); → Vibrate on Touch; `Game Board Design.md` → Haptic Rule
   ("Subject to the vibrate-on-touch setting being on").*

9. **Animations off means the game does the thing instantly** — the mark simply appears,
   the quadrant is simply claimed. No animation, and no substitute effect, fade or
   transition standing in for one. The game stays fully playable and fully readable in this
   mode.
   *Source: `Animations.md` → Decisions → Animations off = instant state change; →
   Decisions → Turn animations off — a global setting.*
   *Testable:* with animations off, a confirmed move produces the new board state with no
   intermediate frames and no substitute effect.

10. **iOS Reduce Motion does not drive the Animations toggle.** There is exactly one
    control and the player owns it; Reduce Motion being on does not change what the game
    does.
    *Source: `Animations.md` → Decisions → Does iOS Reduce Motion drive the animations
    toggle? ("no lets leave this as a game setting for user to command").*
    *Testable:* with Reduce Motion on at the OS level and the Animations toggle on,
    animations still play.

11. **All three are global, player-controlled and not theme-defined — a theme cannot
    override them.** No key in a theme file sets, forces or reads any of the three, and
    switching themes never changes their values.
    *Source: `Menus and UI.md` → Settings Menu ("All three are **global**,
    **player-controlled**, and **not theme-defined** — a theme can't override them");
    `Animations.md` → Decisions → Turn animations off ("it is **not theme-defined**");
    `Theming.md` → Sound Decisions → Global mute ("Muting is a player setting, not a theme
    property").*
    *Testable:* set the three toggles, switch the active theme, and all three values are
    unchanged; a theme file carrying keys with these names changes nothing.

12. **The two entry points edit the same values.** There is one global value per toggle —
    not a main-menu copy and an in-game copy.
    *Source: `Menus and UI.md` → Settings Menu ("All three are **global**"); → How you
    reach settings from gameplay.*
    *Testable:* change a toggle in-game, exit to the main menu, open Settings there, and it
    shows the changed value (and the reverse).

13. **All three are remembered between sessions, in whatever state they were left**, read
    back on launch through the persistence layer rather than any store of this feature's
    own.
    *Source: `Menus and UI.md` → Settings Menu ("All three are **remembered between
    sessions**"); → Persistence (table); `Theming.md` → Sound Decisions → Global mute
    ("**Remembered between sessions**"); `Tech Design.md` → Decisions → Persistence package.*

### What the toggles are, structurally

14. **Sound and Animations switch off a *theme channel*; Vibrate switches off an *app
    behavior* that is never theme-defined at all.** The three look alike in the UI, but
    only two of them correspond to something a theme defines. Concretely: the theme object
    has no haptic concept, and turning sound or animations off suppresses a theme-supplied
    channel without altering the active theme or its definition.
    *Source: `Theming.md` → What a Theme Does NOT Control ("Haptics are **not**
    theme-driven. Vibration lives at the **application setting level** ... two of them
    switch off a theme channel and one switches off an app behavior"); → What Is a Theme?
    (sound and animations are pillars of a theme).*
    *Testable:* the theme schema defines sound and animation values and defines nothing
    haptic; muting does not modify the loaded theme.

15. **Neither entry point offers theme selection or a theme change.** Theme selection lives
    on the main menu, and the theme cannot be changed mid-game.
    *Source: `Theming.md` → Decisions → Where theme selection lives ("Not buried in a
    settings screen"); → Decisions → Can you change the theme mid-game ("**No** — leave it
    out for now. Theme changes happen from the main menu only"); `Menus and UI.md` → Theme
    Selection.*
    *Testable:* no control on either surface changes the selected theme.

16. **Both surfaces are theme-driven — no hardcoded colors, backgrounds, fonts or motion
    values**, and both pass the hardcoded-theme-value test.
    *Source: `Theming.md` → Architectural Rule ("No hardcoded colors, backgrounds, fonts,
    piece styles, sounds, or animations anywhere in the code"); `Menus and UI.md` → Main
    Menu ("The entire main menu is itself theme-driven ... No hardcoded styling here
    either"); `Tech Design.md` → Decisions → Do we add a test that fails on hardcoded theme
    values?*

### Text scaling

17. **Dynamic Type is not supported.** The app does not scale its text to the iOS Dynamic
    Type setting in this version, and the settings surface offers no text-size control of
    its own.
    *Source: `Menus and UI.md` → Decisions → Do we support Dynamic Type? ("**Not for now.**
    *'Lets not do this as of yet.'*").*

## Out of Scope

- **Storing and restoring the four preferences**, including first-launch behavior on an
  empty store: `P1-04-persistence.md`.
- **The haptic mechanism** — how the buzz is produced, and how subtle it is:
  `P4-02-haptics.md`.
- **Audio playback and how muting is implemented** in the audio layer: `P4-01-audio.md`.
- **The animations system** — the vocabulary, where animations fire, durations, the
  one-at-a-time and don't-block-input rules: `P4-03-animations.md`.
- **The main menu itself**, including the Settings button's own styling and placement:
  `P3-01-main-menu.md`.
- **The in-game settings button's placement in the scoreboard strip**:
  `P2-03-scoreboard-turn-indicator.md`.
- **Theme selection and the theme system**: `P1-03-theme-system.md` — and per requirement
  15, theme selection is deliberately absent from both surfaces.
- **A Music toggle.** `Theming.md` → Sound Decisions → One-shot sound effects only, for now
  rules out background music in this version, and `Menus and UI.md` → Persistence lists
  four persisted preferences with no music among them. The handoff draws one anyway — see
  Open Question 3.
- **A confirmation prompt on exit.** Unsettled — see Open Question 2. Nothing here designs
  one, and nothing here rules one out.
- **What else quick actions might eventually hold.** The doc says "contents (so far)"; this
  PRD builds the listed contents and nothing more.

## Open Questions

### 1. Is quick actions the same screen as the main menu's settings, or a trimmed-down version?

As worded in `Menus and UI.md` → How you reach settings from gameplay:

> Undecided: whether quick actions is the *same* settings screen as the main menu's, or a
> trimmed-down in-game version with the exit option added.

The handoff draws them as two different things — `2b — Settings page (from the main menu)`
is a full screen and `1f — Modal: in-game settings / quick actions` is a bottom sheet, with
`2b`'s own text saying "1f stays the trimmed in-game version with the exit action." That is
*an* answer, but it is the handoff's, and no Decision in the docs takes it. It also decides
requirement 3's open half — whether the Animations toggle appears in quick actions.

### 2. Does leaving a game still need a confirmation prompt?

As worded in `Menus and UI.md` → Leaving a game mid-play:

> Whether leaving still needs a confirmation prompt is undecided; the original reason for
> one ("Leave game? Your score will be lost") no longer applies.

### 3. Gaps found while writing this PRD (flagged by the PRD author, not asked by the docs)

Each of these is something an implementer of this surface would otherwise have to guess.
None is resolved here.

- **The handoff draws four toggles, the docs settle three.** `1f` and `2b` both include a
  **Music** row (drawn `off` in `1f`), but `Theming.md` → Sound Decisions → One-shot sound
  effects only, for now says there is no background music in this version, and
  `Menus and UI.md` → Persistence lists exactly four persisted preferences with no music
  key. Requirement 6 follows the docs. Same conflict already flagged by
  `P1-04-persistence.md`.
- **First-launch defaults for the three toggles.** The docs settle that all three are
  remembered between sessions, but no Decision says what they read as before anything has
  been written. The mock in `Menus and UI.md` → Settings Menu draws all three as `[ON]`,
  which is a drawing, not a decision.
- **When a toggle change takes effect.** "Global" and "player-controlled" are settled;
  whether flipping a toggle applies to the running game the moment it is flipped, or only
  on the next launch, is not stated anywhere. The in-game entry point only makes sense
  under the first reading, but that is inference, not a Decision.
- **How the in-game surface is dismissed back to the game.** Requirement 2 settles that
  getting to settings does not abandon the game, but no doc names the control that returns
  you to it. The handoff gives `1f` a close button and a "Back to the game" action; the
  docs give it neither.
- **`Menus and UI.md` → Open Questions reads stale.** Its single entry — "Future menu items
  to consider later: Rules/How to Play, Settings, vs. AI, Online" — lists Settings as a
  future item, while the same doc's Main Menu section and Decisions treat the Settings
  button as settled. Worth a doc pass; not this PRD's to fix.
