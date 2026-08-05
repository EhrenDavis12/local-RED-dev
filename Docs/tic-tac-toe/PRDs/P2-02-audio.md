# PRD: Audio Playback

> **Status:** Draft · Source docs read: `Theming.md`, `Tech Design.md`, `Menus and UI.md`,
> `Game Board Design.md`, `Animations.md`, `Game Overview.md`, `Rules.md`, `roadmap.md`,
> and the read-only reference asset `design_handoff_game_ui/` (`README.md`,
> `neon.theme.json`, `themes.catalog.json`). `Alternative Game Styles.md` is a declared
> parking-lot doc and was not used as a source.

**Wave:** P2 · **File:** `P2-02-audio.md` — parallel-safe with the other P2 PRDs.

**Depends on:** `P1-01-app-scaffold.md` (declares the `audioplayers` dependency and creates
`assets/audio/`), `P1-03-theme-system.md` (defines the sound **slots** on the merged theme
object and the merge-over-Neon materialization), `P1-04-persistence.md` (stores the
sound-effects preference this layer reads).

> **The mute toggle is a persisted preference, not a settings-screen behavior.** This PRD
> reads the stored value through `P1-04-persistence.md`. `P4-04-settings.md` draws the
> switch and owns no part of what "off" means — so it is a wave-4 consumer of this feature,
> not a dependency of it.

**Depended on by:** `P3-02-move-input.md` (the confirmed-move sound),
`P3-04-game-over-rematch.md` (result sounds), `P4-01-main-menu.md` /
`P4-03-theme-selection.md` / `P4-04-settings.md` (button-tap sounds),
`P5-01-classic-theme.md` (the splat that overrides Neon's buzz).

**Blocked on assets, deliberately not blocking:** no sound files exist and none are made
here — see Requirement 16 and Out of Scope.

**Call sites are not all assigned.** This PRD owns *what plays*; something else must *call
play*. Only one of the five moments has an owner today — see Out of Scope → **Who calls
play**, which lists the four that do not.

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
theme. It is complete and testable against the theme content that exists today — Neon's
placeholder sound values — it plays Neon's buzz and Classic's splat unchanged the day
those files land, and adding a background-music layer later does not require rebuilding it.

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
   *Testable:* no file outside the audio layer references `audioplayers` or constructs a
   player; every call site names a moment from Requirement 6 and nothing else.
3. **No hardcoded audio anywhere.** Every sound played is read from the currently selected
   theme's sound slots. No audio asset path, file name or sound constant appears anywhere
   outside the theme layer, and the hardcoded-theme-value test must still pass with this
   feature in place.
   *(`Theming.md` → Architectural Rule — *"No hardcoded colors, backgrounds, fonts, piece
   styles, sounds, or animations anywhere in the code"*; `Tech Design.md` → Decisions → Do
   we add a test that fails on hardcoded theme values?)*
   *Testable:* the guard test from `P1-05-theme-guard-test.md` passes with this feature in
   place, and its baseline gains no entry.
   **Scope of the ban depends on an undecided value shape.** Whether the folder segment
   `audio/` may appear in the audio layer is exactly the question Open Question **OQ-1**
   raises. Requirement 17 states where the files live without asserting which component
   spells that out; whichever shape is chosen, this requirement is the constraint it must
   satisfy.
4. **A theme is a full audio-visual package, not a skin.** Sound is theme-driven exactly
   like visuals: changing the active theme changes the entire sound set with **zero changes
   to game, board or menu code**, and adding a new theme adds only a theme definition.
   *(`Theming.md` → Decisions → Do themes affect sound; → Architectural Rule)*
   *Testable:* swap the active theme for one whose sound slots differ and the moments in
   Requirement 6 request the new theme's values, with no diff in game, board or menu code.
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
   *Testable:* with a fake audio sink, each moment records exactly one playback request
   naming its own slot, and no other slot is ever requested.
7. **`sound` has seven keys; only these five are playable.** `neon.theme.json` → `sound`
   also carries `music` and `signature`. **`music` is never played in this version**
   (Requirement 13). **`signature` is descriptive metadata, not an asset** — its value is
   the word `"buzz"`, naming the theme's sonic character, and it is not one of the audio
   moments `Theming.md` lists. The audio layer never plays it, and must not be implemented
   by iterating `sound.*`.
   *(`Theming.md` → What a Theme Controls → Audio (the five moments plus music — nothing
   else); → Theme Catalog → Theme 1 — Neon → Signature sound, which states the buzz as the
   theme's character; `neon.theme.json` → `sound.signature: "buzz"`,
   `sound.music: null`.)*
   *Testable:* with a fake audio sink, no playback request ever names `signature` or
   `music`, including on a theme whose `music` slot is populated.
8. **The pending selection gets no sound of its own.** Sound belongs to the **confirmed**
   move, not the preview — the `placeMark` sound fires on the second (confirm) tap only, so
   the board does not chirp while a player browses options. Selecting a different cell, and
   tapping outside the grid to deselect, are also silent.
   *(`Game Board Design.md` → Move Input — Tap to Select, Tap Again to Confirm → Sound;
   → Changing your mind. Corroborated by `design_handoff_game_ui/README.md` → *2d — Board,
   pending move*: *"No sound fires on selection (docs)."*)*
   *Testable:* with a fake audio sink, a first tap and a deselect tap record no playback; a
   confirm tap records exactly one. (`P3-02-move-input.md` requirement 15 asserts the same
   boundary from the call-site side.)
9. **An illegal tap makes no sound.** A tap outside the legal quadrant *"does nothing"* —
   no shake, no flash, no error message, and no audio.
   *(`Game Board Design.md` → Active Quadrant Highlight → Taps outside the legal quadrant)*
   *Testable:* with a fake audio sink, tapping any illegal cell records no playback.
10. **The haptic and the sound are independent channels.** Firing a haptic never implies
    firing a sound: the haptic fires on *every valid click* including the first tap of a
    two-tap move, which Requirement 8 makes silent.
    *(`Game Board Design.md` → Haptic Rule vs. → Move Input → Sound. Haptics themselves are
    `P2-03-haptics.md`.)*
    *Testable:* a legal first tap records one haptic invocation and zero playback requests.

### Theme sound sets and fallback

11. **Sound falls back to Neon.** A theme needs no full sound set; any sound it does not
    define comes from Neon. Because each theme is materialized into a complete theme at
    startup by merging over Neon, the audio layer performs **no fallback at play time** —
    it plays whatever the materialized active theme holds, and that is always complete.
    *(`Theming.md` → Sound Decisions → Sound falls back to Neon; → Neon Is the Base Theme;
    `Tech Design.md` → Decisions → Fallback to Neon — merge, not resolve)*
    *Testable:* the audio layer contains no fallback, default or null-coalescing branch on
    a sound slot; a theme defining one sound resolves the other four to Neon's values before
    the audio layer sees them.
12. **Neon is the theme every sound ultimately comes from, and its signature is a buzz** —
    like the buzz of a neon light, electric and humming.
    *(`Theming.md` → Theme Catalog → Theme 1 — Neon → Signature sound; → Neon Is the Base
    Theme → How it works)*
    *Owner of the behavior:* `P1-03-theme-system.md` requirements 11, 12 and 14 — Neon
    ships complete with no gaps, and its `sound` keys are stubs. **This PRD authors no theme
    content and must not edit `assets/themes/`.** It is restated here because Requirement 11
    is only true if it holds.
13. **Classic Red vs Blue's signature sound is a splat** — like a water balloon popping, wet
    and playful, deliberately nothing like Neon's electric buzz. It inherits every sound it
    does not override.
    *(`Theming.md` → Theme Catalog → Theme 2 — Classic Red vs Blue → Sound; What it
    inherits from Neon)*
    *Owner of the behavior:* `P5-01-classic-theme.md`, three waves out. **Not assertable in
    wave 2** — no Classic theme file exists yet. It is restated only so that Requirement 4's
    "changing the theme changes the sound set" has a named destination, and so no one builds
    the splat into this layer.

### One-shots now, music not foreclosed

14. **One-shot sound effects only. No background music in this version.** The audio layer
    plays discrete one-shots on actions and never starts a looping or continuous track,
    even if a theme's `music` slot is populated.
    *(`Theming.md` → Sound Decisions → One-shot sound effects only, for now;
    `neon.theme.json` → `sound.music: null`)*
    *Testable:* with a fake audio sink and a theme whose `music` slot names an asset, no
    looping or continuous playback is ever requested — see also Requirement 7.
15. **Adding a music layer later must not be painful.** The audio layer is structured so
    that adding background music is an addition, not a restructuring — a music channel must
    be addable without changing how one-shot effects are requested or played by their
    callers.
    *(`Theming.md` → Sound Decisions → One-shot sound effects only, for now — *"Background
    music is a possible later addition, so don't build the audio system in a way that makes
    adding a music layer painful."* The `music` slot already exists on the theme object per
    `P1-03-theme-system.md`.)*

### The global mute

16. **A global sound-effects toggle silences all of it.** The toggle is:
    - a **player setting, not a theme property** — it mutes **any** theme, and a theme
      cannot define or override it;
    - **global for the whole game**, not per-theme;
    - **remembered between sessions**, in whatever state it was left.

    With it off, no sound effect plays at any of the five moments, under any theme. It
    changes nothing else: not the active theme, not haptics, not animations.
    *(`Theming.md` → Sound Decisions → Global mute; → What a Theme Does NOT Control (the
    three toggles switch off separate channels); `Menus and UI.md` → Decisions → Should
    there be a mute button, and where does it live?; → Persistence)*
    *Testable:* with the persisted value off, a fake audio sink records zero playback
    requests across all five moments under both themes; with it on, each moment records one.
    Toggling it changes no other persisted value and fires no haptic or animation.
    *Ownership:* the stored value is `P1-04-persistence.md`'s and the switch that sets it is
    `P4-04-settings.md`'s (its requirements 1–3 and 7 own where the switch lives and that it
    is reachable mid-game — **this PRD asserts nothing about that surface**). **What "off"
    means — the behavior above — is this PRD's.**

### Working against the theme content that exists

17. **The audio system must be complete and testable against Neon's placeholder sound
    values.** Neon's five slots hold prose placeholders today — `"TODO: neon buzz one-shot"`
    and four `"TODO"` — so they are **named but unloadable, never absent**, and
    `P1-03-theme-system.md` requirement 11 requires Neon complete with no gaps, which may
    make an empty slot illegal by construction. Against that state: the game stays fully
    playable, every non-audio behavior is unchanged, and no requirement in this PRD other
    than audible output depends on a real asset. Every *Testable* line above is written
    against a fake audio sink for exactly this reason.
    *(`neon.theme.json` → `sound`; `design_handoff_game_ui/README.md` → Assets → Sounds
    (*"Sounds — none produced"*); `Tech Design.md` → Decisions → Where do sound and art
    assets come from? — generated with Replicate *"when we actually need them — not now"*,
    and *"it's best to do what we can without images or music"*.)*
    **What the layer does when it tries to play one of those placeholder values is
    deliberately unspecified** — see Open Question **OQ-2**. This requirement asserts the
    game-level invariant, not the layer's handling of an unloadable value.
18. **Sound assets, once produced, are stored in `assets/audio/`** — one of the designated
    asset folders, created by `P1-01-app-scaffold.md` requirement 3 and written by
    `P5-02-asset-generation-replicate.md` requirement 3. This requirement fixes where the
    files live. It does **not** decide whether the theme slot, or the audio layer, spells
    out the folder segment — that is **OQ-1**, and Requirement 3 is the constraint either
    answer must satisfy.
    *(`Tech Design.md` → Decisions → Project structure — layer-first; → Where do sound and
    art assets come from? — *"We will have to have designated folders for assets."*)*
19. **Dropping the real files in changes no code.** When `P5-02-asset-generation-replicate.md`
    produces the buzz and the splat, making them audible is a change to the theme
    definitions only.
    *(Follows from Requirements 3, 4 and 11 — `Theming.md` → Architectural Rule.)*

## Out of Scope

Referenced by filename only; this PRD specifies none of them.

- **Who calls play.** This PRD owns *what plays and under what rules*. It does not own the
  call sites, and **four of the five moments have no owner today.** Detection is not the
  gap — the engine detects a claim, a cat game and a win (`P1-02-engine-rules.md`), and
  that is uncontested. The gap is which PRD's requirement *invokes this layer*:

  | Moment | Call-site owner |
  |---|---|
  | `placeMark` | **Owned** — `P3-02-move-input.md` requirement 15 (confirm tap fires exactly one) |
  | `claimQuadrant` | **None.** No PRD requires anything to fire it |
  | `catGame` | **None.** No PRD requires anything to fire it |
  | `winGame` | **Circular.** `P3-04-game-over-rematch.md` Out of Scope says *"Result sounds — `P2-02-audio.md`"*, and this PRD points back; no numbered requirement in either fires one |
  | `buttonTap` | **None**, and no doc or PRD defines which controls count as buttons — see OQ-4 |

  Assigning the four is a coordination call, not something this PRD can settle by writing
  more requirements: a requirement here would specify another PRD's surface.
- **The theme mechanism and where the sound keys live on the theme object** — the theme
  object, YAML loading, UUID identity, merge-over-Neon, and the `sound` slot list:
  `P1-03-theme-system.md`. This PRD *plays* those slots; it does not define them, and it
  authors no theme content (see Requirement 12).
- **The settings surface** — the row, the switch, the sub-label, and the two places settings
  is reachable from: `P4-04-settings.md`. This PRD specifies only what the toggle's stored
  value does to audio (Requirement 16).
- **Persisting the toggle** — `shared_preferences` and the four persisted preferences:
  `P1-04-persistence.md`.
- **Generating the actual sound files** — `P5-02-asset-generation-replicate.md`.
  `Tech Design.md` → Decisions → Where do sound and art assets come from? decides sound
  assets come from Replicate *when actually needed and explicitly not now*, via **one**
  API-calling script and designated asset folders. This PRD states the dependency and
  requires the audio system to be complete before the assets exist (Requirement 17).
- **The Classic Red vs Blue theme definition** — its YAML file and the concrete list of
  values it overrides: `P5-01-classic-theme.md`. See Requirement 13.
- **Haptics.** Vibration is **not audio and not theme-driven** — it is an app-level
  setting, and a theme cannot define or change the buzz: `P2-03-haptics.md`.
  *(`Theming.md` → What a Theme Does NOT Control)*
- **Animations**, including the one-at-a-time rule and the animations-off instant-state
  path: `P2-04-animations.md`. Nothing in `Animations.md` is stated to apply to sound, and
  this PRD does not carry it across.
- **Background music.** Ruled out for this version by Requirement 14; only Requirement 15's
  "don't make it painful later" constrains this feature.

## Open Questions

### From the design docs, worded as the docs word them

No `## Open Questions` entry in any design doc names audio. `Theming.md` → Open Questions
carries one item that touches this feature only indirectly, and it is owned by
`P5-01-classic-theme.md`:

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
  sound-effects toggle, no music (Requirements 14 and 16). Whether the Music row is drawn
  and disabled, drawn and functional, or not drawn at all needs a call, and the same
  conflict is already flagged from the other side in `P1-04-persistence.md` and
  `P4-04-settings.md`.

### Raised by this PRD, not by the design docs (proposals, clearly mine)

The docs are silent on all of these. Each is a decision an implementer would otherwise
make by accident.

- **OQ-1 — What shape is a sound slot's value?** Requirements 3 and 18 are consistent only
  once this is answered, and the two readings differ in whether Requirement 3 is satisfiable
  at all. Either the slot holds the full relative path (`audio/buzz.mp3`) and the audio layer
  holds no literal, or the slot holds a bare file name (`buzz.mp3`) and the audio layer
  supplies the `audio/` segment — which puts an asset-path literal in code, the thing
  Requirement 3 bans. `P1-05-theme-guard-test.md` requirement 6 observes that `audioplayers`
  uses `AssetSource('audio/…')` and supplies the `assets/` prefix itself, which pushes
  toward the second reading without settling it. Neon's placeholder values (`"TODO: neon
  buzz one-shot"`) are prose and imply no shape. A third option — the slot holds a key and a
  theme-layer manifest maps keys to paths — keeps Requirement 3 clean at the cost of a level
  of indirection. **Not decided here.**
- **OQ-2 — What happens when a named sound will not load?** This is the *only* state
  reachable in wave 2: every Neon slot names a value that cannot resolve to an asset
  (Requirement 17). Silently skip, log once, log per attempt, or surface it — all four are
  guesses. Related but not the same as `Theming.md` → Decisions → What happens if a theme
  fails to load, which is about the theme *file*, and which `P1-03-theme-system.md` already
  flags as needing a definition of "fails to load."
- **OQ-3 — When does a mute change take effect?** The running session, or only at next
  launch? This PRD now owns what "off" means, but not when "off" starts. Note the source
  that would settle it exists and is unused: `Menus and UI.md` → How you reach settings from
  gameplay lists *"The sound effects and vibrate toggles"* in in-game quick actions, and
  `P2-03-haptics.md` requirement 12 reads that same sentence to settle the mid-game case
  **for haptics** ("a mid-game change governs the next tap"). Nothing states it for sound,
  and this PRD does not carry the haptic ruling across. **Recorded, not answered.**
- **OQ-4 — Is "button taps / menu navigation" one sound or several, and what is a button?**
  `Theming.md` lists it as a single audio item and `neon.theme.json` has one `buttonTap`
  slot, but the moment covers primary buttons, back navigation, toggles, overlay open/close
  and list rows. Two things are unstated: whether those share one sound, and which controls
  count at all. The second blocks the call-site assignment in Out of Scope → Who calls play.
- **OQ-5 — Is there a sound for a whole-game draw?** Requirement 6's list has `catGame` (a
  small board) and `winGame`, but `Rules.md` → Edge Cases → Big board full with no
  three-in-a-row → straight draw is a distinct outcome with its own drawn screen
  (`design_handoff_game_ui/README.md` → *1h — Modal: draw*), and no audio slot named for
  it. Reuse `catGame`, reuse `winGame`, add a slot, or stay silent — all four are guesses.
- **OQ-6 — Can two sounds overlap?** The moments in Requirement 6 co-occur: a single
  confirmed move can be `placeMark` **and** `claimQuadrant` **and** `winGame` at the same
  instant. Play all simultaneously, play only the most significant, or queue them.
  `Animations.md` → Decisions → **One animation at a time** settles the equivalent question
  for motion — but it is stated about animations, not sound, so it is **not** carried across
  here.
- **OQ-7 — Does a sound ever delay or block anything?** `Animations.md` → Decisions →
  Animations don't block input settles this for motion. Nothing states whether the turn
  passes, the board redraws, or a screen transitions before, during or regardless of a sound
  finishing. I would expect "never blocks," matching animations, but that is my inference
  and not a decision recorded anywhere.
