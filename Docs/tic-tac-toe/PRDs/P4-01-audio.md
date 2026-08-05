# PRD: Audio Playback

> **Status:** Draft · Source docs read: `Theming.md`, `Tech Design.md`, `Menus and UI.md`,
> `Game Board Design.md`, `Animations.md`, `Game Overview.md`, `Rules.md`, `roadmap.md`,
> and the read-only reference asset `design_handoff_game_ui/` (`README.md`,
> `neon.theme.json`, `themes.catalog.json`). `Alternative Game Styles.md` is a declared
> parking-lot doc and was not used as a source.

**Wave:** P4 · **File:** `P4-01-audio.md`

**Depends on:** `P1-01-app-scaffold.md` (declares the `audioplayers` dependency and creates
`assets/audio/`), `P1-03-theme-system.md` (defines the sound **slots** on the merged theme
object and the merge-over-Neon materialization), `P1-04-persistence.md` (persists the
sound-effects preference), `P3-04-settings.md` (the toggle UI).

**Depended on by:** `P2-02-move-input.md` (the confirmed-move sound),
`P2-04-game-over-rematch.md` (result sounds), `P3-01-main-menu.md` /
`P3-03-theme-selection.md` / `P3-04-settings.md` (button-tap sounds),
`P4-04-classic-theme.md` (the splat that overrides Neon's buzz).

**Blocked on assets, deliberately not blocking:** no sound files exist and none are made
here — see Requirement 16 and Out of Scope.

---

## Problem

The game is silent, and there is no code path that could make it otherwise. Nothing loads,
holds or plays an audio file, so a confirmed move, a claimed quadrant, a cat game, a won
game and a menu tap are all indistinguishable to a player who is not looking directly at
the thing that changed — on a board with 81 cells, passed back and forth between two
people.

There is also a structural risk. `Theming.md` → Architectural Rule says *"if something
makes a noise, that sound came from the theme"*, and the first feature that plays a sound
is the one that decides whether that stays true. An audio layer that reaches for a file
path directly, or that hardcodes which sound belongs to which event, breaks the rule the
whole theme system exists to enforce and has to be unpicked from every caller later.

## Goal

The app can make a noise, and every noise it makes came from the active theme. A single
audio layer, built on `audioplayers`, plays one-shot sound effects at the moments the
design docs name, taking every asset from the materialized theme object and nothing from
its own code. A global player-owned sound-effects toggle silences all of it under any
theme. It works correctly today with no sound files present, it plays Neon's buzz and
Classic's splat unchanged the day those files land, and adding a background-music layer
later does not require rebuilding it.

## Requirements

### The audio layer

1. **The audio package is `audioplayers`.**
   *(`Tech Design.md` → Decisions → Audio package. The dependency is declared by
   `P1-01-app-scaffold.md`.)*
2. **All playback goes through one audio layer.** Widgets, the board and the menus request
   a named sound moment; they never construct a player, an asset path or playback options
   themselves.
   *(**Derived, not stated** — no doc names an audio layer. It is the shape the cited rules
   force: `Theming.md` → Architectural Rule requires every sound to come from the theme,
   and `Tech Design.md` → Decisions → Do we add a test that fails on hardcoded theme values?
   bans *"literal `assets/…` paths outside the theme layer"*, so callers cannot hold their
   own. If a different structure satisfies Requirement 3, this requirement is negotiable.)*
3. **No hardcoded audio anywhere.** Every sound played is read from the currently selected
   theme's sound slots. No audio asset path, file name or sound constant appears outside
   the theme layer, and the hardcoded-theme-value test must still pass with this feature in
   place.
   *(`Theming.md` → Architectural Rule — *"No hardcoded colors, backgrounds, fonts, piece
   styles, sounds, or animations anywhere in the code"*; `Tech Design.md` → Decisions → Do
   we add a test that fails on hardcoded theme values?)*
4. **A theme is a full audio-visual package, not a skin.** Sound is theme-driven exactly
   like visuals: changing the active theme changes the entire sound set with **zero changes
   to game, board or menu code**, and adding a new theme adds only a theme definition.
   *(`Theming.md` → Decisions → Do themes affect sound; → Architectural Rule)*
5. **The audio layer reads the active theme and the sound setting through Riverpod**
   (plain `Notifier`/`NotifierProvider`, no `@riverpod` codegen), so both are readable from
   anywhere that fires a sound, including deep in the board widget tree.
   *(`Tech Design.md` → Decisions → State management — Riverpod)*

### Which moments make a sound

6. **Sound fires at exactly these five moments**, each reading its own theme slot:

   | Moment | Theme slot (`neon.theme.json` → `sound`) |
   |---|---|
   | Placing a mark | `placeMark` |
   | Winning a small board / claiming a quadrant | `claimQuadrant` |
   | Cat game | `catGame` |
   | Winning the whole game | `winGame` |
   | Button taps / menu navigation | `buttonTap` |

   *(`Theming.md` → What a Theme Controls → Audio, which lists exactly these five plus
   background music; slot names from the read-only `neon.theme.json` → `sound`.)*
7. **The pending selection gets no sound of its own.** Sound belongs to the **confirmed**
   move, not the preview — the `placeMark` sound fires on the second (confirm) tap only, so
   the board does not chirp while a player browses options. Selecting a different cell, and
   tapping outside the grid to deselect, are also silent.
   *(`Game Board Design.md` → Move Input — Tap to Select, Tap Again to Confirm → Sound;
   → Changing your mind. Corroborated by `design_handoff_game_ui/README.md` → *2d — Board,
   pending move*: *"No sound fires on selection (docs)."*)*
8. **An illegal tap makes no sound.** A tap outside the legal quadrant *"does nothing"* —
   no shake, no flash, no error message, and no audio.
   *(`Game Board Design.md` → Active Quadrant Highlight → Taps outside the legal quadrant)*
9. **The haptic and the sound are independent channels.** Firing a haptic never implies
   firing a sound: the haptic fires on *every valid click* including the first tap of a
   two-tap move, which Requirement 7 makes silent.
   *(`Game Board Design.md` → Haptic Rule vs. → Move Input → Sound. Haptics themselves are
   `P4-02-haptics.md`.)*

### Theme sound sets and fallback

10. **Sound falls back to Neon.** A theme needs no full sound set; any sound it does not
    define comes from Neon. Because each theme is materialized into a complete theme at
    startup by merging over Neon, the audio layer performs **no fallback at play time** —
    it plays whatever the materialized active theme holds, and that is always complete.
    *(`Theming.md` → Sound Decisions → Sound falls back to Neon; → Neon Is the Base Theme;
    `Tech Design.md` → Decisions → Fallback to Neon — merge, not resolve)*
11. **Neon's signature sound is a buzz** — like the buzz of a neon light, electric and
    humming. Neon defines all five slots, because it is the one theme with nothing to fall
    back to.
    *(`Theming.md` → Theme Catalog → Theme 1 — Neon → Signature sound; → Neon Is the Base
    Theme → How it works; `neon.theme.json` → `sound.signature: "buzz"`)*
12. **Classic Red vs Blue's signature sound is a splat** — like a water balloon popping,
    wet and playful, deliberately nothing like Neon's electric buzz. It inherits every
    sound it does not override.
    *(`Theming.md` → Theme Catalog → Theme 2 — Classic Red vs Blue → Sound; What it
    inherits from Neon. Authoring that theme file is `P4-04-classic-theme.md`.)*

### One-shots now, music not foreclosed

13. **One-shot sound effects only. No background music in this version.** The audio layer
    plays discrete one-shots on actions and never starts a looping or continuous track,
    even if a theme's `music` slot is populated.
    *(`Theming.md` → Sound Decisions → One-shot sound effects only, for now;
    `neon.theme.json` → `sound.music: null`)*
14. **Adding a music layer later must not be painful.** The audio layer is structured so
    that adding background music is an addition, not a restructuring — a music channel must
    be addable without changing how one-shot effects are requested or played by their
    callers.
    *(`Theming.md` → Sound Decisions → One-shot sound effects only, for now — *"Background
    music is a possible later addition, so don't build the audio system in a way that makes
    adding a music layer painful."* The `music` slot already exists on the theme object per
    `P1-03-theme-system.md`.)*

### The global mute

15. **A global sound-effects toggle silences all of it.** The toggle is:
    - a **player setting, not a theme property** — it mutes **any** theme, and a theme
      cannot define or override it;
    - **global for the whole game**, not per-theme;
    - **remembered between sessions**, in whatever state it was left;
    - resident in the **Settings menu**, reachable from both the main menu and mid-game.

    With it off, no sound effect plays at any of the five moments, under any theme. It
    changes nothing else: not the active theme, not haptics, not animations.
    *(`Theming.md` → Sound Decisions → Global mute; → What a Theme Does NOT Control (the
    three toggles switch off separate channels); `Menus and UI.md` → Decisions → Should
    there be a mute button, and where does it live?; → Settings Menu; → Persistence)*

### Working before the assets exist

16. **The audio system must work before any sound asset exists.** No sound files are
    produced yet — Neon's `sound` keys are `"TODO"` stubs and the handoff records
    *"Sounds — none produced."* Every requirement above except the actual audible output
    must be satisfiable and testable today: the game stays fully playable, every non-audio
    behavior is unchanged, and nothing crashes, blocks or logs an error because a sound is
    absent.
    *(`Tech Design.md` → Decisions → Where do sound and art assets come from? — generated
    with Replicate *"when we actually need them — not now"*, and *"it's best to do what we
    can without images or music"*; `neon.theme.json` → `sound`;
    `design_handoff_game_ui/README.md` → Assets → Sounds)*
17. **Sound assets, once produced, live in `assets/audio/`** — one of the designated asset
    folders. The audio layer expects them there and nowhere else.
    *(`Tech Design.md` → Decisions → Project structure — layer-first; → Where do sound and
    art assets come from? — *"We will have to have designated folders for assets."*)*
18. **Dropping the real files in changes no code.** When `P5-01` produces the buzz and the
    splat, making them audible is a change to the theme definitions only.
    *(Follows from Requirements 3, 4 and 10 — `Theming.md` → Architectural Rule.)*

## Out of Scope

Referenced by filename only; this PRD specifies none of them.

- **The theme mechanism and where the sound keys live on the theme object** — the theme
  object, YAML loading, UUID identity, merge-over-Neon, and the `sound` slot list:
  `P1-03-theme-system.md`. This PRD *plays* those slots; it does not define them.
- **The settings toggle UI** — the row, the switch, the sub-label, and the two places
  settings is reachable from: `P3-04-settings.md`. This PRD specifies only what the toggle
  does to audio (Requirement 15).
- **Persisting the toggle** — `shared_preferences` and the four persisted preferences:
  `P1-04-persistence.md`.
- **Generating the actual sound files** — `P5-01-asset-generation-replicate.md`.
  `Tech Design.md` → Decisions → Where do sound and art assets come from? decides sound
  assets come from Replicate *when actually needed and explicitly not now*, via **one**
  API-calling script and designated asset folders. This PRD states the dependency and
  requires the audio system to work before the assets exist (Requirement 16).
- **The Classic Red vs Blue theme definition** — its YAML file and the concrete list of
  values it overrides: `P4-04-classic-theme.md`. This PRD fixes only that its signature
  sound is a splat and that everything it does not override comes from Neon.
- **Haptics.** Vibration is **not audio and not theme-driven** — it is an app-level
  setting, and a theme cannot define or change the buzz: `P4-02-haptics.md`.
  *(`Theming.md` → What a Theme Does NOT Control)*
- **Animations**, including the one-at-a-time rule and the animations-off instant-state
  path: `P4-03-animations.md`. Nothing in `Animations.md` is stated to apply to sound, and
  this PRD does not carry it across.
- **Background music.** Ruled out for this version by Requirement 13; only Requirement 14's
  "don't make it painful later" constrains this feature.
- **Firing the events.** Detecting that a quadrant was claimed, a small board was a cat
  game, or the game was won belongs to the engine and the board/game-over PRDs
  (`P1-02-engine-rules.md`, `P2-02-move-input.md`, `P2-04-game-over-rematch.md`). This PRD
  specifies what a sound moment *is* and what plays, not who detects it.

## Open Questions

### From the design docs, worded as the docs word them

No `## Open Questions` entry in any design doc names audio. `Theming.md` → Open Questions
carries one item that touches this feature only indirectly, and it is owned by
`P4-04-classic-theme.md`:

- Which values, concretely, does Classic Red vs Blue override? (Settled in principle —
  graphics and its splat sound, inheriting the rest. An exact list will fall out when it's
  actually built.)

### Contradiction between docs — flagged, not resolved

- **A Music toggle the docs do not have.** `design_handoff_game_ui/README.md` → *1f* and
  *2b* both draw **four** toggles — Sound effects, **Music ("Background track", shown
  off)**, Vibrate on touch, Animations — and its *State* section lists a fifth global
  preference, `music`. `Menus and UI.md` → Settings Menu says **three** toggles and
  → Persistence says **four** persisted preferences (theme, sound, vibrate, animations),
  and `Theming.md` → Sound Decisions → One-shot sound effects only, for now says there is
  **no background music in this version**. This PRD follows the design docs: one
  sound-effects toggle, no music (Requirements 13 and 15). Whether the Music row is drawn
  and disabled, drawn and functional, or not drawn at all needs a call, and the same
  conflict is already flagged from the other side in `P1-04-persistence.md`.

### Raised by this PRD, not by the design docs (proposals, clearly mine)

The docs are silent on all of these. Each is a decision an implementer would otherwise
make by accident.

- **Can two sounds overlap?** No doc says. This matters immediately because the moments in
  Requirement 6 co-occur: a single confirmed move can be `placeMark` **and**
  `claimQuadrant` **and** `winGame` at the same instant. Options are play all
  simultaneously, play only the most significant, or queue them. Note that `Animations.md`
  → Decisions → **One animation at a time** settles the equivalent question for motion —
  but it is stated about animations, not sound, so it is **not** carried across here.
- **What happens if a sound asset is missing or fails to load?** Requirement 16 requires
  the game to keep working with *no* assets at all, which is today's state and is
  testable. It does not settle the case of a theme naming an asset that is absent or
  corrupt at runtime — silently skip, log, or surface it. Related but not the same as
  `Theming.md` → Decisions → What happens if a theme fails to load, which is about the
  theme file, and which `P1-03` already flags as needing a definition of "fails to load."
- **Is "button taps / menu navigation" one sound or several?** `Theming.md` lists it as a
  single audio item, but it covers taps on primary buttons, back navigation, toggles,
  overlay open/close and list rows. One shared `buttonTap` slot (which is all
  `neon.theme.json` has) or distinct sounds per action is unstated.
- **Is there a sound for a whole-game draw?** Requirement 6's list has `catGame` (a small
  board) and `winGame`, but `Rules.md` → Edge Cases → Big board full with no
  three-in-a-row → straight draw is a distinct outcome with its own drawn screen
  (`design_handoff_game_ui/README.md` → *1h — Modal: draw*), and no audio slot named for
  it. Reuse `catGame`, reuse `winGame`, add a slot, or stay silent — all four are guesses
  today.
- **Does a sound ever delay or block anything?** `Animations.md` → Decisions → Animations
  don't block input settles this for motion. Nothing states whether the turn passes, the
  board redraws, or a screen transitions before, during or regardless of a sound finishing.
  I would expect "never blocks," matching animations, but that is my inference and not a
  decision recorded anywhere.
