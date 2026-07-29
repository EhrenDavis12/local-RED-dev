# Animations

> **Status:** Brain dump. Contradictions are expected and OK. Nothing here is settled.
>
> Animations are **part of the theme**. See [Theming](./Theming.md).

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

## Animations Inherit From Neon
Animations follow the same inheritance rule as everything else: **Neon is the base
theme**, and any theme that doesn't define its own animations gets Neon's. See
[Theming](./Theming.md) → Neon Is the Base Theme.

So the Neon animation set must be **complete** — every animated moment in the game needs a
Neon definition, because it's the fallback for every other theme.

## Decisions

### Themes define their own animations from scratch
There is **no shared animation library or menu to pick from**. A theme defines its own
animations from scratch. The vocabulary above (grow/shrink, glow, jiggle, dance) is the
*direction* — not a fixed set of options a theme selects between.

> ⚠️ **Tension with the inheritance model — flagging, not resolving.**
> [Theming](./Theming.md) says Neon is the base theme and anything a theme doesn't define
> falls back to Neon — and Classic Red vs Blue is currently written as *inheriting* Neon's
> animations. "Each theme defines its own from scratch" points the other way. Both are
> recorded. The likely reconciliation is that a theme *may* author its own animations
> rather than choosing from a menu, and inheritance still covers whatever it doesn't
> define — but that hasn't been decided.

### One animation at a time
Animations **never overlap**. Strictly one at a time.

### Duration lives in the animation
**Speed is specified in the animation itself**, not globally. Each animation carries its
own timing, so a theme controls its own pacing.

### Animations don't block input
Animations **never block input**. You can tap through them, and the animation keeps
playing as normal — it isn't interrupted or skipped, and the game doesn't wait on it.

This matters for a two-player pass-and-play game: a player who already knows their move
shouldn't be held up by a mark finishing its bounce. Animation is decoration on top of the
game state, never a gate in front of it.

### Turn animations off — a global setting
There is an **animations on/off toggle**, and it is **not theme-defined**. It's a global
player setting sitting **right alongside the vibration and mute toggles** in the Settings
menu (see [Menus and UI](./Menus%20and%20UI.md)).

Same shape as the other two: global, player-controlled, independent of theme.

### Animations off = instant state change
With animations turned off, the game does the thing **instantly**. The mark simply
appears, the quadrant is simply claimed — no animation, no substitute effect, no fade or
transition standing in for one.

Don't worry about animations at all in this mode. The game state changes and the screen
shows the new state. That's it.

Practical consequence: animations are a **pure layer on top**. The game has to be fully
playable and fully readable with every animation stripped out — which is a good
correctness test. If turning animations off makes something confusing or invisible, that
information was living in the animation when it should have been in the board itself.

## Open Questions
<!-- Nothing outstanding on this doc right now. -->

> The one unresolved item affecting this doc is the ⚠️ tension noted under
> **Themes define their own animations from scratch** — whether a theme authors its own
> animation set or inherits Neon's. See [Theming](./Theming.md).
