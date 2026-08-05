# PRD: Haptics

> **Status:** Draft · Source docs read: `Game Board Design.md`, `Menus and UI.md`,
> `Theming.md`, `Tech Design.md`, `Animations.md`, `Game Overview.md`, `Rules.md`,
> `roadmap.md`, plus the read-only reference asset `design_handoff_game_ui/README.md`
> (→ *Interactions & behavior*, *1f — Modal: in-game settings*, *2b — Settings page*,
> *2d — Board, pending move*). `Alternative Game Styles.md` is a declared parking-lot doc
> and was read only to confirm it is out of scope — no requirement here comes from it.

**Wave:** P4.

**Dependencies:**

- `P2-02-move-input.md` — owns the two-tap select-then-confirm gesture and what counts as a
  legal cell. This PRD says only *when a buzz fires*, never how a move is made.
- `P2-01-board-rendering.md` — owns the locked/dimmed quadrant styling. Requirement 9 below
  records the constraint this feature places on it; it specifies no visuals.
- `P3-04-settings.md` — owns the settings surfaces and the vibrate-on-touch toggle control.
- `P1-04-persistence.md` — owns storing and restoring that toggle. This PRD only reads it.
- `P1-03-theme-system.md` — req 29 already states the theme object has no haptics slot.
  Requirement 7 below is the behavioral half of that same boundary.

**Note on source status:** `Game Board Design.md` carries the house banner *"Nothing here is
settled"* and has **no `## Decisions` section** (`roadmap.md` records this). The Haptic Rule
is nonetheless treated as settled here, because it is stated as a rule in that doc, restated
in `Menus and UI.md` → Settings Menu (*"Fires on every valid click"*), listed in
`Tech Design.md` → What the Design Docs Already Imply as a requirement *"already locked by
decisions made elsewhere"*, and drawn into the approved handoff. Nothing in this PRD comes
from a single unsupported mention.

## Problem

The board has 81 tap targets on a phone, each roughly 35pt — under Apple's 44pt guidance
(`Game Board Design.md` → Responsive / Screen Size). A tap that lands slightly off, or on one
of the eight quadrants the player is not allowed to play in, leaves them asking *"did that
register?"* and hunting the screen for a change (`Menus and UI.md` → Vibrate on Touch).

The docs answer that with feedback the player feels rather than reads, and they answer it
without an error state: nothing shakes, flashes, or tells the player off. That only works if
the rule holds everywhere and without exception — a buzz that fires on an illegal tap, or
fails to fire on a legal one, inverts the signal and makes the board less trustworthy than
having no haptic at all. Today no such rule is implemented anywhere.

## Goal

Every valid click in the app produces one small, subtle buzz, and nothing else ever does.
That single rule becomes the app's validity signal — *a buzz means "that registered," no
buzz means "that did nothing"* — so an illegal tap needs no error message, no shake and no
flash to explain itself. The buzz is gated only by the player's vibrate-on-touch setting,
lives at the application-setting level, and is identical under every theme.

## Requirements

### When the haptic fires

1. **The haptic fires on every valid click.** Any valid selection or valid action produces
   exactly one haptic event.
   *Source: `Game Board Design.md` → Haptic Rule ("The haptic fires on every valid click.
   Any valid selection or valid action buzzes"); `Menus and UI.md` → Settings Menu
   ("Fires on every *valid* click"); `design_handoff_game_ui/README.md` → Interactions &
   behavior ("Haptic on every valid tap").*
   *Testable:* each valid action fires the haptic exactly once — never zero times, never
   twice for one action.

2. **The first tap of a two-tap move fires it**, because selecting a legal cell is itself a
   valid action. The confirming second tap, being a valid action too, fires it as well.
   *Source: `Game Board Design.md` → Haptic Rule ("including the first tap of a two-tap
   move, since selecting a legal cell is a valid action"); `design_handoff_game_ui/README.md`
   → *2d — Board, pending move* ("No sound fires on selection (docs). The haptic **does**
   fire — selecting a legal cell is a valid action").*
   *Testable:* a select-then-confirm sequence on a legal cell fires two haptic events, one
   per tap. Note this differs from sound, which fires only on the confirmed move
   (`Game Board Design.md` → Move Input → Sound) — the two channels are not interchangeable.

3. **Re-selecting a different legal cell fires it**, since that is a valid selection.
   *Source: `Game Board Design.md` → Haptic Rule (any valid selection); → Move Input →
   Changing your mind ("Tap a different cell → that cell becomes the new selection").*
   *Testable:* tapping legal cell A then legal cell B fires two haptic events and leaves one
   pending selection.

### When it does not

4. **An illegal tap does nothing.** No shake, no flash, no error message — and no buzz. This
   covers any tap the app does not accept, including taps on cells inside a locked, claimed
   or cat-game quadrant.
   *Source: `Game Board Design.md` → Active Quadrant Highlight → Taps outside the legal
   quadrant ("**An illegal tap does nothing.** No shake, no flash, no error message — and,
   per the haptic rule, **no buzz**"); `design_handoff_game_ui/README.md` → Interactions &
   behavior ("Illegal tap does nothing — no shake, no flash, no error, and **no haptic**").*
   *Testable:* tapping every cell of every non-legal quadrant produces zero haptic events,
   zero state changes, and no visible error affordance of any kind.

5. **No error state exists for invalid input anywhere in this feature.** The absence of the
   buzz is the feedback; nothing is added to explain, warn about, or scold an invalid tap —
   not a toast, not a message, not a substitute effect.
   *Source: `Game Board Design.md` → Haptic Rule ("The player doesn't need an error state —
   the *absence* of feedback is the feedback. Nothing scolds them; invalid taps just quietly
   don't happen"); → Taps outside the legal quadrant ("The lack of a buzz *is* the
   feedback").*
   *Testable:* the resulting system holds as a pair — for any tap, exactly one of these is
   true: it was valid and buzzed, or it did nothing at all and produced no output on any
   channel.

### What it feels like

6. **The buzz is small and subtle** — one discrete confirmation that "you selected that,"
   nothing more. Deliberately not a rumble: no sustained, repeating or escalating vibration,
   and no distinct haptic per action type.
   *Source: `Menus and UI.md` → Settings Menu → Vibrate on Touch ("A **small, subtle buzz**
   … enough to confirm 'you selected that,' nothing more … Deliberately subtle. Not a
   rumble"); `design_handoff_game_ui/README.md` → *1f* ("A little buzz on every valid tap").*
   *Testable:* every valid action fires the same single short haptic; no code path produces a
   continuous or repeated vibration. Which concrete iOS haptic style this maps to is **not**
   settled — see OQ-1.

### Where it lives

7. **Haptics are not theme-driven.** Vibration lives at the application-setting level; a
   theme cannot define or change the buzz, and the theme object carries no haptics slot.
   *Source: `Theming.md` → What a Theme Does NOT Control ("Haptics are **not** theme-driven.
   Vibration lives at the **application setting level** … a theme cannot define or change the
   buzz"); `P1-03-theme-system.md` req 29; `design_handoff_game_ui/README.md` →
   Interactions & behavior ("Haptics are an app setting, never theme-driven").*
   *Testable:* no theme file contains a haptic key, and no haptic value is read through the
   theme layer. Consistent with `P1-05-theme-guard-test.md`, a literal haptic value in source
   is **not** a theme-guard violation.

8. **It is a single app-level behavior, identical under every theme.** The same valid action
   produces the same buzz on Neon and on Classic Red vs Blue, and on any theme added later.
   *Source: `Theming.md` → What a Theme Does NOT Control ("It's a single app-level behavior,
   the same under every theme"); → the theme-boundary table (Haptics / vibration: ❌ No — app
   setting).*
   *Testable:* switching the active theme and repeating the same valid action produces an
   identical haptic event.

9. **The locked/dimmed styling has to prevent the illegal tap in the first place**, because
   nothing explains it afterwards. This feature adds no compensating affordance and depends
   on that styling doing the work; the visuals themselves are specified in
   `P2-01-board-rendering.md`.
   *Source: `Game Board Design.md` → Taps outside the legal quadrant ("This is why the
   locked/dimmed styling matters so much: it has to prevent the tap, because nothing will
   explain it after the fact"); `design_handoff_game_ui/README.md` → Interactions & behavior
   ("which is why the locked veil sits at 0.50: it must be obviously non-tappable while still
   readable").*
   *Testable:* recorded as a constraint carried into `P2-01-board-rendering.md`, not as
   behavior implemented here.

### The setting that gates it

10. **All haptics are gated on the vibrate-on-touch setting.** With it off, no valid action
    anywhere in the app fires a haptic; with it on, requirement 1 holds.
    *Source: `Game Board Design.md` → Haptic Rule ("Subject to the vibrate-on-touch setting
    being on"); `Menus and UI.md` → Settings Menu ("**Vibrate on touch** — Haptic feedback on
    tap. Fires on every *valid* click. On/off").*
    *Testable:* with the setting off, a full select-then-confirm move and every other valid
    action fire zero haptic events; turning it on restores exactly the behavior of
    requirements 1–3.

11. **The setting is a global player setting, not a theme property**, and its stored value is
    what governs — this feature reads it and never owns, defaults or writes it.
    *Source: `Menus and UI.md` → Settings Menu ("All three are **global**,
    **player-controlled**, and **not theme-defined** — a theme can't override them");
    → Persistence (the vibrate toggle is remembered between sessions);
    `P1-04-persistence.md` (owner of the stored value).*
    *Testable:* the haptic layer has no default of its own and no writer; it reads the
    persisted preference.

12. **A mid-game change to the setting governs the next tap.** The vibrate toggle is offered
    inside in-game quick actions, so its current value — not a value captured at app or game
    start — decides whether the next valid action buzzes.
    *Source: `Menus and UI.md` → How you reach settings from gameplay → Quick actions
    contents ("The sound effects and vibrate toggles"); → Settings Menu ("settings must be
    available mid-game"); `design_handoff_game_ui/README.md` → *1f* (the vibrate row is in
    the in-game sheet).*
    *Testable:* toggling vibrate off from the in-game sheet and returning to the board, the
    very next valid tap fires no haptic; toggling it back on, the next one does.

## Out of Scope

Named so the boundary is explicit. Each is specified elsewhere; do not specify it here.

- **The two-tap select-then-confirm gesture, what counts as a legal cell, and the
  tap-outside-to-deselect behavior** — `P2-02-move-input.md`. This PRD attaches a buzz to
  valid actions; it does not define them.
- **Locked, dimmed, claimed and cat-game quadrant visuals, and the three highlights** —
  `P2-01-board-rendering.md`. Requirement 9 records a constraint on that work, nothing more.
- **The settings screen and sheet, the toggle control, and its layout** —
  `P3-04-settings.md`.
- **Storing and restoring the vibrate-on-touch preference, and its first-launch default** —
  `P1-04-persistence.md`.
- **Sound effects, the global mute toggle, and the audio package** — `P4-01-audio.md`. Sound
  is theme-driven and fires on different events; the two channels are specified separately
  and must not be wired together.
- **Animations and the animations toggle** — `P4-03-animations.md`.
- **Anything from `Alternative Game Styles.md`.** That is a declared parking-lot doc and
  explicitly not the game being built.

## Open Questions

### OQ-1 — Which concrete haptic does "small, subtle buzz" map to?

`Menus and UI.md` → Vibrate on Touch specifies the *feel* — "a **small, subtle buzz**",
"deliberately subtle", "not a rumble" — and no doc names a platform API or intensity. iOS is
the primary target (`Tech Design.md` → Decisions → Primary target — Apple), which on Flutter
offers a range from `HapticFeedback.selectionClick()` through light/medium/heavy impacts.
Nothing in the docs picks one. Requirement 6 constrains the character and the count; the
concrete style is left open deliberately rather than chosen here.

### OQ-2 — Do menu and button taps buzz, or only board taps?

The rule as written is app-wide — "every valid click", "any valid selection or valid
action" — and the setting is named "Vibrate on **touch**". But every example the docs give is
a board tap, and the justification given in `Menus and UI.md` → Vibrate on Touch is entirely
about the board's 81 small targets. Whether pressing PLAY GAME, a theme row, REMATCH, or the
vibrate toggle itself buzzes is not stated. `P2-04-game-over-rematch.md` req 15 has already
read the rule the broad way for the rematch control; that is a sibling PRD's reading, not a
decision in the docs. A narrow reading and a broad reading produce visibly different apps, so
this needs a call rather than an implementer's guess.

### OQ-3 — What happens on a device with no haptic engine?

No doc addresses it. `Tech Design.md` → Decisions → Device support names iPhone first, iPad
second, Android far future — and iPad has no Taptic Engine, so this is reachable inside the
stated support ordering, not a hypothetical. Whether the app degrades silently, falls back to
a system vibration, or hides the vibrate toggle entirely is unspecified.

### OQ-4 — Gaps found while writing this PRD

Flagged by the PRD author, not asked by the docs. Each is something an implementer would
otherwise decide by accident. None is resolved here.

- **Does tapping outside the grid to deselect buzz?** `Game Board Design.md` → Move Input →
  Changing your mind makes "tap outside the full grid → deselects entirely" one of the two
  ways out of a pending selection, so it is a real action that changes state — but it is also
  a tap on nothing, which reads as the paradigm case of "that did nothing". The Haptic Rule's
  "any valid action" does not settle which it is.
- **Do actions the player did not initiate by tapping buzz?** The rule is worded around
  clicks and taps. Whether a haptic accompanies non-tap events — a quadrant being claimed, a
  game being won, the turn handing over — is not stated. The narrow reading (taps only) is
  assumed nowhere in this PRD; requirement 1 fires on valid *actions the player performs*,
  and nothing here attaches a haptic to a game event.
