# Animations

> **Status:** Brain dump. Contradictions are expected and OK. What's settled is stated in
> present tense; anything unsettled is in **Open Questions**.
>
> Animations are **part of the theme**. See [Theming](./Theming.md).
>
> **Approved UI design:** `Docs/tic-tac-toe/design_handoff_game_ui/README.md` —
> [Design Handoff](./design_handoff_game_ui/README.md). Starting values for Neon's
> animation set live in `neon.theme.json → animation` there. Reference asset — read-only.

## The Direction
**Poppy.** That's the word for it. Things grow and shrink, glow, shadowbox, jiggle, dance.
Snappy and playful, not slow and cinematic. It should feel alive and fun — this is a game
aimed partly at kids.

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

**A theme describes its animations as data, and the runtime interprets that data.** The
user's intent: *"Say we want to create a new theme with new animations. I don't want to
code the new animations into the game. I want to drop a file in the new theme folder that
can tell the application what animations are and everything else the application needs to
know to execute one of them… we just want to make sure the themes control as much as we
can. This way new themes are easy to design and control customizations."*

What this means, without designing the format:
- A theme author adds a theme file and gets new motion. **Adding an animation must not
  require changing game code.**
- What a theme supplies is therefore a *description* of motion — what changes, by how
  much, over what time, with what easing, and whether it repeats — not the name of a
  behaviour the runtime already knows.
- Neon's current animation entries (`type`, `durationMs`, `easing`, `loop`) are a
  starting point that does not yet reach this bar, since `type` names a behaviour rather
  than describing one.

Consequence: this is a larger piece of work than a fixed set of named animations, and the
schema for describing motion has to be designed. The schema itself belongs to the theme
system's PRD and is not settled here.

There is **no shared animation library or menu to pick from**. The vocabulary above
(grow/shrink, glow, shadowbox, jiggle, dance) is the *direction* — not a fixed set of
options a theme selects between.

This is about *authoring*, not inheritance: a theme writes its own animations rather than
picking from a menu, and whatever it doesn't write it inherits from Neon. See
**Animations Inherit From Neon** below.

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

A theme starts from Neon's complete animation set and its own definitions merge over the
top, overriding only what it names — the same model as every other theme value. See
[Tech Design](./Tech%20Design.md) → The Theme System.

So the Neon animation set must be **complete** — every animated moment in the game needs a
Neon definition, because it's the fallback for every other theme.

## How Animations Play
Animations **never overlap**. Strictly one at a time.

**Speed is specified in the animation itself**, not globally. Each animation carries its
own timing, so a theme controls its own pacing.

Animations **never block input**. You can tap through them, and the animation keeps
playing as normal — it isn't interrupted or skipped, and the game doesn't wait on it.

## Turning Animations Off
There is an **animations on/off toggle**, and it is **not theme-defined**. It's a global
player setting sitting **right alongside the vibration and mute toggles** in the Settings
menu (see [Menus and UI](./Menus%20and%20UI.md)). Same shape as the other two: global,
player-controlled, independent of theme.

iOS Reduce Motion does not drive it — the toggle stays a player setting: *"no lets leave
this as a game setting for user to command."* So there is exactly one control, and the
player owns it. Reduce Motion being on does not change what the game does.

With animations turned off, the game does the thing **instantly**. The mark simply
appears, the quadrant is simply claimed — no animation, no substitute effect, no fade or
transition standing in for one.

Don't worry about animations at all in this mode. The game state changes and the screen
shows the new state. That's it.

Practical consequence: animations are a **pure layer on top**. The game has to be fully
playable and fully readable with every animation stripped out.

## Open Questions
<!-- Nothing outstanding on this doc right now. -->
