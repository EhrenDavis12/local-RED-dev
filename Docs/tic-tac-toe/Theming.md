# Theming

> **Status:** Brain dump. Contradictions are expected and OK. Nothing here is settled.

## The Idea
A **theme button** — a place where you can change up the theme of the board. Styling,
really cool backgrounds, anything like that. The point is to make it **fun for kids to
change out the theme**.

## Architectural Rule (the important part)
Build the theme system **from the beginning**, not bolted on later.

> **All of our code operates off of the theme. No code should be operating independently
> from the selected theme.**

Meaning:
- No hardcoded colors, backgrounds, fonts, piece styles, sounds, or animations anywhere
  in the code.
- Every visual, audio, and motion value is read from the currently selected theme.
- If something on screen has a color, that color came from the theme. If something makes
  a noise, that sound came from the theme. **If something moves, that motion came from
  the theme.** No exceptions.
- Adding a new theme should require zero changes to game/board/menu code — only adding
  a new theme definition.

This is a day-one constraint because retrofitting it later means touching every file.

<!-- Enforced by: the hardcoded-theme-value test, which covers all six categories listed
     above. See Tech Design → Decisions → Do we add a test that fails on hardcoded theme
     values? -->

## Where Themes Live
- **For now, themes are contained within the codebase.** Bundled/shipped with the app.
- Not user-uploaded, not downloaded from a server, not user-authored. That's a possible
  later thing, not now.

---

## Decisions

### How many themes ship at launch
**Two — Neon and Classic Red vs Blue.** See the Theme Catalog below. Two is enough to
prove the theme system actually works and nothing is hardcoded.

### Where theme selection lives
**On the main menu.** Themes up front — a nice big button, the same size and treatment
as the New Game button. Not buried in a settings screen.

### Does the theme persist between sessions
**Yes.** Once a player selects a theme, it stays active. Close the app, open it again,
that's still their theme. Requires persisting the selection to device storage.

<!-- The persisted value is the theme's UUID, not its name, so renaming a theme does not
     lose the selection. See Tech Design → Decisions → Theme identity — UUID. -->

### Can you change the theme mid-game
**No — leave it out for now.** Theme changes happen from the main menu only. Possible
later feature if we decide we want it.

### Do themes affect sound
**Yes. Themes come with sound.** A theme is a full audio-visual package, not just a skin.
Sound is theme-driven exactly like visuals are — no hardcoded audio anywhere.

### Are themes unlockable/rewards
**No — all themes available from the start.** Every theme is free and unlocked.

Later on we might get into paid/purchasable themes, but **that is not the current goal**.
Worth knowing the direction exists so we don't build something that makes it impossible,
but no monetization work now.

### Marks beyond X and O
**Marks are not locked to X and O — a theme supplies its own mark art, as an image or an
icon.** From [Tech Design](./Tech%20Design.md) → Decisions: *"Due to themes im thinking
the marks can be an image or an icon. For example neon just needs icons of X and O while
the dinosaur theme might use a T-Rex as an Icon."*

Since themes are aimed at being fun for kids, the marks aren't locked to X and O — a
theme might swap them for icons, emoji, animals, shapes, etc. The theme system must be
built so that's possible. Neon still uses X and O icons; that's Neon's choice of art,
not a constraint on the system.

### What happens if a theme fails to load
**A modal on the Theme screen saying the theme is unavailable, then fall back to Neon.**
As stated: *"From the Theme screen if a theme fails to load put up a modal with sorry this
theme is unavailable please try another theme. Then fallback to neon."*

So the failure is surfaced to the player rather than swallowed — they are told the theme
they picked is unavailable and asked to pick another — and the game continues on Neon
rather than on a broken theme. Neon is the one theme with nothing to fall back to, per
**Neon Is the Base Theme** below.

Theme selection is an overlay on the main menu rather than its own screen — see
[Menus and UI](./Menus%20and%20UI.md) → Decisions → Is theme selection its own screen or
an overlay?

### Is anything distinguished by colour alone?
**Handled per theme — a theme can add non-colour distinguishing features.** It is not a
system-wide rule. As stated: *"Themes will be defined and other things can be added for
this."*

So this gets solved when a theme is defined, and the theme system has to allow a theme to
distinguish things by more than colour — shape, icon, outline, pattern. It is not
currently written as a requirement that every theme must do so; compare **What a Theme
Controls** below, which does require every theme to keep the gameplay-critical highlights
legible.

---

## What Is a Theme?
A theme is the **complete package** — not a color swap. Five pillars:

| Pillar | What it covers |
|---|---|
| **Art style** | Marker art/icons, board styling, backgrounds |
| **All color decisions** | Every color, everywhere. No exceptions. |
| **Sound effects** | Every sound the game makes |
| **Music** | Background music |
| **Animations** | The animation set — see [Animations](./Animations.md) |

---

## Neon Is the Base Theme (inheritance model)
> **The Neon theme is the default theme for all other themes.** Anything a theme is
> missing falls back to Neon.

This applies to **everything**, not just sound:

- Colors
- Art style
- Sound effects
- Animations
- The whole nine yards

### How it works
- **Neon is fully built out.** Every single themeable value has a Neon definition. It is
  the most defined thing we have — a complete theme set for animations, sound effects,
  colors, art, all of it.
- **Every other theme is a partial override.** Classic Red vs Blue defines only what it
  wants to be different, and **inherits the rest from Neon**.

```
        ┌──────────────────────────┐
        │   NEON  (base theme)     │
        │   complete — every value │
        │   defined, no gaps       │
        └───────────┬──────────────┘
                    │ inherits everything not overridden
        ┌───────────┴──────────────┐
        │  CLASSIC RED VS BLUE     │
        │  overrides: colors, art  │
        │  inherits: sounds,       │
        │            animations,   │
        │            everything    │
        │            else          │
        └──────────────────────────┘
```

### Why this matters for the build
- **Neon must be complete before anything else ships.** It's the floor everything stands
  on. A gap in Neon is a gap with no fallback — that's the one failure the system can't
  absorb.
- **New themes become cheap.** A theme can be as small as "black → white, neon green →
  red" and still be a complete, working theme. That directly supports adding more themes
  later.
- **Fallback happens once, not per lookup.** Each theme is materialized into a complete
  theme at startup by merging over Neon, so at runtime every lookup hits a complete theme
  and there is no fallback step. See [Tech Design](./Tech%20Design.md) → Decisions → How
  does fallback-to-Neon work?
<!-- Superseded: this bullet previously read "Build the theme lookup as: ask the active
     theme → if undefined, ask Neon." Per-lookup fallback lost to merge-over-Neon.
     See Tech Design → Decisions → How does fallback-to-Neon work? -->

### Watch out for
A partial theme inherits Neon's *personality*, not just its values. Classic Red vs Blue
with Neon's electric buzz sounds and glow animations may feel mismatched — clean visuals
with electric audio. That's a fine default (it works, nothing is missing), but Red vs Blue
may want to override more than just colors to feel coherent. Worth checking once it's
real; not a problem to solve now.

---

## Theme Catalog

### Theme 1 — Neon (base)
The first theme. The look:

- **Black background.**
- **Neon colors** — things that really pop and snap.
- Bright, high-contrast, electric. Colors glowing against the dark.

**This is the base theme** — fully defined, no gaps. See the inheritance model above.

This one is a natural fit for the animation direction: neon and glow/backlight effects
(see [Animations](./Animations.md)) reinforce each other. Grow-and-shrink pops read
especially well against black.

Bonus: high contrast makes the gameplay-critical highlights (last move, active quadrant)
easy to keep legible — neon glow *is* a highlight treatment.

**Signature sound:** a **buzz**, like the buzz of a neon light. Electric, humming.

### Theme 2 — Classic Red vs Blue
The straightforward, traditional one. Red player vs blue player. No neon, no black
background — the plain, familiar look.

Good pairing with Neon: one is loud and electric, the other is clean and classic. Two
genuinely different looks, which is a real test that nothing is hardcoded.

**What it overrides:**
- **Graphics.** That's the override — the art and colors. Red player, blue player, no
  black background.
- **Sound:** a **splat** — like a water balloon popping. Wet and playful, deliberately
  nothing like Neon's electric buzz.

**What it inherits from Neon:** everything else — animations included.
<!-- Resolved: animations inherit from Neon, and a theme's own animations merge over it.
     See Animations → Decisions → Do themes inherit Neon's animations? -->

The two themes now have distinct sonic identities: Neon **buzzes** like a light,
Classic **splats** like a water balloon.

---

## What a Theme Controls
Everything visual and audible. Rough list, not exhaustive:

**Visual**
- Board background / page background — "really cool backgrounds"
- Big board and small board grid lines (colors, thickness, style)
- The player marks themselves — see **Marks beyond X and O** under Decisions
- **Last-move highlight** — the exaggerated treatment on the opponent's most recent mark
- **Active-quadrant highlight** — where you're allowed to play
- **Locked/inactive quadrant styling** — the dimmed state on the eight you can't play in
- **Pending-move preview styling** — the provisional select-before-confirm state
- Claimed-quadrant styling
- Cat-game quadrant styling
- Turn indicator styling
- Scoreboard styling
- Main menu styling (background, button look, title)

> **Every theme must keep these legible.** The last-move highlight and active-quadrant
> highlight are *gameplay-critical*, not decoration — a theme that makes them hard to spot
> breaks the game. A pretty theme that hides the last move is a broken theme.

**Audio**
- Placing a mark
- Winning a small board / claiming a quadrant
- Cat game
- Winning the whole game
- Button taps / menu navigation
- Background music

**Animation**
- The animation set applied to the player's marker — grow/shrink, glow/backlight,
  shadowbox, jiggle, dance. See [Animations](./Animations.md) for the full vocabulary.

<!-- Resolved: marks are theme-supplied image or icon, not locked to X and O.
     See Decisions → Marks beyond X and O. -->

## Sound Decisions

### Sound falls back to Neon
A specific case of the general inheritance rule above — themes don't need a full sound
set; anything undefined comes from Neon.

### One-shot sound effects only, for now
No background music in this version. Sound effects only — discrete one-shots on actions.
Background music is a **possible later addition**, so don't build the audio system in a
way that makes adding a music layer painful.

### Global mute
There's a **global mute / sound toggle, separate from the theme.** Muting is a player
setting, not a theme property — you can mute any theme.

- **Global for the whole game**, not per-theme.
- **Remembered between sessions** — the toggle stays in whatever state it was left in,
  same as the theme selection.
- Lives in the **Settings menu** (see [Menus and UI](./Menus%20and%20UI.md)).

## Inheritance Depth
**One level only.** A theme inherits from Neon, full stop. **Neon is the base level** and
nothing inherits from anything else. No chains, no theme-inheriting-from-another-theme.

## What a Theme Does NOT Control
Haptics are **not** theme-driven. Vibration lives at the **application setting level** and
is unrelated to theming — a theme cannot define or change the buzz. It's a single
app-level behavior, the same under every theme.

This draws the boundary of the theme system. Compare:

| | Theme-controlled? |
|---|---|
| Colors, art, backgrounds | ✅ Yes |
| Sound effects | ✅ Yes |
| Animations | ✅ Yes |
| **Haptics / vibration** | ❌ No — app setting |

Note the asymmetry with the settings toggles: sound and animations are *theme-defined but
player-switchable*, while haptics are *never theme-defined at all*. The three toggles in
[Menus and UI](./Menus%20and%20UI.md) look alike, but two of them switch off a theme
channel and one switches off an app behavior.

## Open Questions
- Which values, concretely, does Classic Red vs Blue override? (Settled in principle —
  graphics and its splat sound, inheriting the rest. An exact list will fall out when it's
  actually built.)
