# Animations

> **Status:** Brain dump. Contradictions are expected and OK. Nothing here is settled.
>
> Animations are **part of the theme**. See [Theming](./Theming.md).
>
> **Approved UI design:** `Docs/tic-tac-toe/design_handoff_game_ui/README.md` —
> [Design Handoff](./design_handoff_game_ui/README.md). Starting values for Neon's
> animation set live in `neon.theme.json → animation` there. Reference asset — read-only.

## The Direction
**Poppy.** That's the word for it. Things grow and shrink, glow, jiggle, dance. Snappy and
playful, not slow and cinematic. It should feel alive and fun — this is a game aimed
partly at kids.

## Scope For Now
Keep it simple to start. We are **not** animating the board, the layout, or transitions
between screens yet. For now animations apply to **the player's marker** — whatever the
theme says that marker is (an X, an O, a checkbox, an icon, an image, whatever goes along
with the theme).

The marker is the thing that moves.

## The Animation Vocabulary
The building blocks, as described:

### Grow & Shrink (the core one)
- **Enlargement and shrinking** of the player's marker.
- Grows and shrinks, or shrinks and grows.
- This is the signature move — "poppy type animations."

### Glow / Backlight
- Making the marker **glow**, with a little bit of a **backlight** behind it.

### Shadowbox
- A **shadowbox** treatment on the marker — a drop shadow / raised box effect that lifts
  it off the board.

### Jiggle
- Making the marker **jiggle** in place.

### Dance
- Making the marker **dance** — moving it around the screen a little bit.

## Animation Sets Are Part of the Theme
> **These should be part of an animation theme set — animations are controlled within the
> theme.**

A theme is not just colors. A theme is the complete package:

| Theme controls | |
|---|---|
| **Art style** | The look — marker art/icons, board styling |
| **All color decisions** | Every color, everywhere |
| **Sound effects** | See [Theming](./Theming.md) |
| **Music** | Background music |
| **Animations** | Which animation set is used, per the above |

So a different theme can bring a different animation personality — one theme might pop and
bounce, another might glow and pulse. The animation set travels with the theme.

## Where Animations Fire
Not yet decided in detail, but the obvious moments:
- **Placing a marker** — the primary one. The mark appears with a pop.
- Winning a small board / claiming a quadrant.
- Cat game.
- Winning the whole game.
- The last-move highlight and active-quadrant highlight (see
  [Game Board Design](./Game%20Board%20Design.md)) — these could be animated rather than
  static, e.g. a pulsing glow on the legal quadrant.

The handoff puts a starting value on each of these:
`Docs/tic-tac-toe/design_handoff_game_ui/neon.theme.json` → `animation` has `placeMark`,
`claimQuadrant`, `catGame`, `winGame`, `activeQuadrant` and `lastMove`, each with a type
and a duration; the last two are drawn as looping glow-pulses. Starting values, in the
handoff's own words — not decisions.

## Animations Inherit From Neon
Animations follow the same inheritance rule as everything else: **Neon is the base
theme**, and any theme that doesn't define its own animations gets Neon's. See
[Theming](./Theming.md) → Neon Is the Base Theme.

So the Neon animation set must be **complete** — every animated moment in the game needs a
Neon definition, because it's the fallback for every other theme.

## Decisions

### Themes author their own animations — no shared library
There is **no shared animation library or menu to pick from**. The vocabulary above
(grow/shrink, glow, jiggle, dance) is the *direction* — not a fixed set of options a theme
selects between.

This is about *authoring*, not inheritance: a theme writes its own animations rather than
picking from a menu, and whatever it doesn't write it inherits from Neon. See **Do themes
inherit Neon's animations?** below.

### Do themes inherit Neon's animations?
**Inherit from Neon, but it can define its own animations that will then merge over the
Neon theme.**

Same model as every other theme value: a theme starts from Neon's complete animation set
and its own definitions merge over the top, overriding only what it names. See
[Tech Design](./Tech%20Design.md) → Decisions → Fallback to Neon — merge, not resolve.

### One animation at a time
Animations **never overlap**. Strictly one at a time.

### Duration lives in the animation
**Speed is specified in the animation itself**, not globally. Each animation carries its
own timing, so a theme controls its own pacing.

### Animations don't block input
Animations **never block input**. You can tap through them, and the animation keeps
playing as normal — it isn't interrupted or skipped, and the game doesn't wait on it.

### Turn animations off — a global setting
There is an **animations on/off toggle**, and it is **not theme-defined**. It's a global
player setting sitting **right alongside the vibration and mute toggles** in the Settings
menu (see [Menus and UI](./Menus%20and%20UI.md)).

Same shape as the other two: global, player-controlled, independent of theme.

### Does iOS Reduce Motion drive the animations toggle?
**No — the animations toggle stays a player setting.** The OS accessibility setting does
not turn animations off on its own: *"no lets leave this as a game setting for user to
command."*

So there is exactly one control, and the player owns it. Reduce Motion being on does not
change what the game does.

### Animations off = instant state change
With animations turned off, the game does the thing **instantly**. The mark simply
appears, the quadrant is simply claimed — no animation, no substitute effect, no fade or
transition standing in for one.

Don't worry about animations at all in this mode. The game state changes and the screen
shows the new state. That's it.

Practical consequence: animations are a **pure layer on top**. The game has to be fully
playable and fully readable with every animation stripped out.

## Open Questions
<!-- Nothing outstanding on this doc right now. -->
