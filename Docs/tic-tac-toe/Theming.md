# Theming

> **Status:** Brain dump. Contradictions are expected and OK. Nothing here is settled except
> what's under **Decisions**.
>
> **Approved UI design:** `Docs/tic-tac-toe/design_handoff_game_ui/README.md` —
> [Design Handoff](./design_handoff_game_ui/README.md). Neon now exists as a concrete,
> machine-readable definition: `neon.theme.json` in that folder, plus the token tables in
> the handoff's *Design tokens* section. Reference asset — read-only.

## The Idea
A **theme button** — a place where you can change up the theme of the board. Styling,
really cool backgrounds, anything like that. The point is to make it **fun for kids to
change out the theme**.

## Architectural Rule (the important part)
Build the theme system **from the beginning**, not bolted on later.

> **All of our code operates off of the theme. No code should be operating independently
> from the selected theme.**

Meaning — no hardcoded values anywhere in the code, across the full slot inventory the
screens actually consume:
- Colors, backgrounds, fonts, piece styles, sounds, animations.
- Board geometry and sizing — outer gap, quadrant padding, inner gap, grid-line width,
  grid-line inset, mark sizes.
- Corner radii — cell, quadrant, modal, chip, control, button.
- The type scale — sizes and weights, distinct from "fonts" meaning a typeface.
- Opacities — the locked, claimed and cat-game veils.
- Every surface: modals (winner, draw), sheets (theme select, in-game quick actions), the
  settings card, open-game rows and their chips, badges, the main-menu logo, and a
  gradient-capable page background.

And:
- Every visual, audio, and motion value is read from the currently selected theme.
- If something on screen has a color, that color came from the theme. If something makes
  a noise, that sound came from the theme. **If something moves, that motion came from
  the theme.** No exceptions.
- Adding a new theme should require zero changes to game/board/menu code — only adding
  a new theme definition.

This is a day-one constraint because retrofitting it later means touching every file.

<!-- Enforced by: the hardcoded-theme-value test, which covers the slot inventory listed
     above. See Tech Design → Decisions → Do we add a test that fails on hardcoded theme
     values? -->

## Where Themes Live
- **For now, themes are contained within the codebase.** Bundled/shipped with the app.
- Not user-uploaded, not downloaded from a server, not user-authored. That's a possible
  later thing, not now.

---

## Decisions

### How many themes ship at launch
**Two — Neon and Classic Red vs Blue.** See the Theme Catalog below.

### Where theme selection lives
**On the main menu.** Themes up front — a nice big button, the same size and treatment
as the Play Game button. Not buried in a settings screen.

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
**Yes — some themes are paid.** *"We will label what themes are free as of now we will
have 2 free themes the neon and the red Vs Blue themes any other themes will be a paid for
theme."*

This reverses the earlier position on this doc, which said all themes were free and
unlocked with no monetization goal. That is no longer the case — see **Which themes are
free** below.

### Which themes are free
**Neon and Classic Red vs Blue are free. Every theme beyond those two is paid.** The theme
selection list **labels** which themes are free and which are paid.

### Does a theme supply its own font
**Yes — a font stays a themeable value.** Inter 400/500/600 is bundled as **Neon's** font
choice, not as an app-wide font constant. See [Tech Design](./Tech%20Design.md) →
Decisions → Do themes pick their own font?, which stays true and is now clarified rather
than contradicted.

### Marks beyond X and O
**Marks are not locked to X and O — a theme supplies its own mark art, as an image or an
icon.** From [Tech Design](./Tech%20Design.md) → Decisions: *"Due to themes im thinking
the marks can be an image or an icon. For example neon just needs icons of X and O while
the dinosaur theme might use a T-Rex as an Icon."*

The marks aren't locked to X and O — a theme might swap them for icons, emoji, animals,
shapes, etc. The theme system must be built so that's possible. Neon still uses X and O
icons; that's Neon's choice of art, not a constraint on the system.

### What happens if a theme fails to load
**A modal on the Theme screen saying the theme is unavailable, then fall back to Neon.**
As stated: *"From the Theme screen if a theme fails to load put up a modal with sorry this
theme is unavailable please try another theme. Then fallback to neon."*

Neon is the one theme with nothing to fall back to, per **Neon Is the Base Theme** below.

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

### How a theme merges over Neon
**Deep merge, null = clear.** *"If the new theme has no value at all then that is inherit.
Like it's missing the option entirely."* Three distinct cases:

- **Key absent** from the overriding theme → inherit Neon's value.
- **Key present with a value** → that value wins.
- **Key present and explicitly null** → the value is *cleared*, not inherited.

And the merge is **deep**: a theme naming one key inside a section keeps Neon's other keys
in that section rather than replacing the whole section. Nested maps merge recursively.

See [Tech Design](./Tech%20Design.md) → Decisions → Fallback to Neon — merge, not resolve.

**Consequence:** `neon.theme.json` ships `sound.music` as an explicit `null`. Under this
rule a null means "cleared," so Neon's own null is a deliberate clear rather than a gap —
worth noting so nobody later mistakes it for an unfilled slot.

### What the theme's slots are derived from
**The theme's slot list is derived from what the screens actually consume, not from a
category list written in the abstract.** The earlier six-category list — colors,
backgrounds, fonts, piece styles, sounds, animations — was written before the screens
existed. It omits board geometry and sizing, corner radii, the type scale, and
opacities, and it has no slot for any modal, sheet, settings card, open-game row, badge,
or the main-menu logo — so four PRDs were left unbuildable under the "no hardcoded
values" rule. See **Architectural Rule** above for the corrected enumeration.

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

<!-- "Fully built out" now has a file behind it: neon.theme.json in
     design_handoff_game_ui/. It covers color, marks, type, radius and board geometry;
     its sound and animation keys are still stubs. See Design Handoff → Design tokens. -->

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
  and there is no fallback step. See [Tech Design](./Tech%20Design.md) → Decisions →
  Fallback to Neon — merge, not resolve.

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

**Neon as drawn:** the complete Neon definition is
`Docs/tic-tac-toe/design_handoff_game_ui/neon.theme.json` — color, marks, type, radius,
board geometry, and stub sound/animation keys. Every screen in
[Design Handoff](./design_handoff_game_ui/README.md) is drawn in Neon, so it doubles as
the reference for what "fully built out" means here.

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
- **Board geometry and sizing** — outer gap, quadrant padding, inner gap, grid-line
  width, grid-line inset, mark sizes
- **Corner radii** — cell, quadrant, modal, chip, control, button
- **The type scale** — sizes and weights, distinct from a theme's choice of font
- **Opacities** — the locked, claimed and cat-game veils
- **Modals** — winner, draw
- **Sheets** — theme select, in-game quick actions
- **The settings card**
- **Open-game rows and their chips**
- **Badges**
- **The main-menu logo**
- **Page background** — gradient-capable

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
- What is the exact slot schema — the key structure — for what a theme defines? The
  approved `neon.theme.json` does not currently cover the pending-move highlight, any
  modal or sheet surface, a gradient background, a logo, or a theme's own display name
  and description.
- Neon is required to be complete (see **Neon Is the Base Theme**), but the approved
  `neon.theme.json` has no pending-move highlight values at all — no pending colour, no
  pending cell ring, no destination ring — while the board's pending preview is a
  required, separately addressable treatment. The same gap covers the grid-line opacity
  and glow, the claimed and cat-game mark glows, and the cat-game caption style. How does
  this gap get closed?
- What form does the legibility contract take — a contrast floor, a review step,
  something else? **What a Theme Controls** requires every theme to keep the last-move
  and active-quadrant highlights legible, but this is unfalsifiable as written: Classic
  Red vs Blue has a near-white ground while inheriting Neon's near-white text and its
  veils and glows tuned for a near-black ground, so a theme could be complete, pass every
  stated check, and still be unreadable.
