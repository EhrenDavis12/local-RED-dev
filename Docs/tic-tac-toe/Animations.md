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
Animations apply to **the player's marker as it is placed** — whatever the theme says that
marker is (an X, an O, a checkbox, an icon, an image, whatever goes along with the theme).
That is settled, not a starting scope.

The marker is the thing that moves.

**Winning a small board and winning the whole game are also in scope now.** A
three-in-a-row — on a small board or on the big board — draws a **win line** over the
winning triple, progressively over roughly one second, followed by the claim mark's
animated appearance on a small-board win. See **Where Animations Fire** below for the full
sequences.

We are **not** animating the board, the layout, or transitions between screens.

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

What this means:
- A theme author adds a theme file and gets new motion. **Adding an animation must not
  require changing game code.**
- What a theme supplies is therefore a *description* of motion — what changes, by how
  much, over what time, with what easing, and whether it repeats — not the name of a
  behaviour the runtime already knows.

A theme describes each animated moment as a **duration, a repeat rule, and a list of
tracks**. Each track names one property to move, its own easing, and the keyframes it
interpolates between. The runtime executes that description rather than recognising
animations by name.

The properties a track can move are a **fixed set**, and new motion composed from them
needs no code — that is the bar, and it is met. A property outside the set is a runtime
change, not something a theme can introduce on its own.

The vocabulary above reaches that description: grow and shrink is scale, glow and
backlight are a glow radius and colour, jiggle and dance are rotation and translation.
Shadowbox is the one that doesn't sit comfortably in it — see **Open Questions**.

There is **no shared animation library or menu to pick from**. The vocabulary above
(grow/shrink, glow, shadowbox, jiggle, dance) is the *direction* — not a fixed set of
options a theme selects between.

This is about *authoring*, not inheritance: a theme writes its own animations rather than
picking from a menu, and whatever it doesn't write it inherits from Neon. See
**Animations Inherit From Neon** below.

## Where Animations Fire
**Placing a marker** — the mark appears with a pop. That is the moment that started the
scope, and it stays marker-level and unconditional.

**Winning a small board, and winning the whole game, now animate too.** Cat game still
does not animate — a cat-game quadrant simply reads as claimed, with no celebration, the
same as it always has.

Small-board win sequence: winning mark lands (the place-mark animation as always) → a win
line draws over the winning triple on that small board, progressively over roughly one
second → the claim mark that covers the quadrant pops out (an animated appearance of the
existing claim overlay — grow/pop; the handoff's `claimQuadrant` values are the starting
point) → play resumes.

Game-win sequence: the final quadrant's small-board celebration plays as above → the
big-board win line draws across the three winning quadrants, over roughly one second → a win
display appears — the space below the board that the turn banner vacates is its natural
home → the result card appears. **On an online game the win display names the winning player
by their Game Center account name**, because each phone picks its own marks and both players
may be drawn as the same one, so the mark alone would not say who won — see
[Game Board Design](./Game%20Board%20Design.md) → Pieces & Marks. The result card is now the
end of this sequence, not an instantaneous appearance. Once the result card appears, the
big-board win line stays — it no longer clears when the celebration sequence ends. It is the
resting state of a finished board, shown for as long as the finished board is, including a
reopened finished game.

The win line is drawn with the active theme's art, through a theme image slot of its own —
the same pattern as the game's other image slots. See [Theming](./Theming.md).

The last-move highlight and active-quadrant highlight are **static**: they are drawn, not
animated. See [Game Board Design](./Game%20Board%20Design.md).

The handoff puts a starting value on each of these:
`Docs/tic-tac-toe/design_handoff_game_ui/neon.theme.json` → `animation` has `placeMark`,
`claimQuadrant`, `catGame`, `winGame`, `activeQuadrant` and `lastMove`, each with a type
and a duration; the last two are drawn as looping glow-pulses. Starting values, in the
handoff's own words — not decisions. The marker's, the claim pop's and the win line's are
now used.

Widening the animated scope this way costs a schema change — new animation slots beyond
`placeMark` for the win line — a Neon definition for every new slot, since Neon's set must
stay complete, a new theme image slot for the win-line art, and a code change. None of
that is something a theme can do on its own. Changing *how* any of these animates, once
the slot exists, is theme data alone — including motion the runtime has never executed
before. The timings above (~1s per line, the handoff's pop values) are starting values to
be tuned by playtesting, not commitments.

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

**One animation means one moment, not one property.** A single animation can move several
properties at once — that is one animation with several tracks running together, not two
animations overlapping.

**A win sequence is several animated moments in a row, not one.** The win line, the claim
pop, and — on a game win — the big-board win line all play under the same one-at-a-time
rule: each is queued after the one before it finishes, never simultaneous.

An animation that repeats forever never ends, so it would hold the slot against
everything else. Nothing in the game plays on a permanent loop.

**Speed is specified in the animation itself**, not globally. Each animation carries its
own timing, so a theme controls its own pacing.

**Place-mark animations never block input.** You can tap through them, and the animation
keeps playing as normal — it isn't interrupted or skipped, and the game doesn't wait on it.

**Win sequences do block input.** From the moment a win is detected until its celebration
finishes — the win line, the claim pop, and on a game win the big-board line and the win
display — taps do nothing.

## Turning Animations Off
There is an **animations on/off toggle**, and it is **not theme-defined**. It's a global
player setting sitting **right alongside the music, sound-effects and vibration toggles**
in the Settings menu (see [Menus and UI](./Menus%20and%20UI.md)). Same shape as the other
three: global, player-controlled, independent of theme. No theme file key sets, overrides
or reads it, and switching themes never changes its value.

iOS Reduce Motion does not drive it — the toggle stays a player setting: *"no lets leave
this as a game setting for user to command."* So there is exactly one control, and the
player owns it. Reduce Motion being on does not change what the game does.

With animations turned off, the game does the thing **instantly**. The mark simply
appears, the quadrant is simply claimed — no animation, no substitute effect, no fade or
transition standing in for one. A win is the same: no win-line draw, no claim pop, no input
lock — the quadrant is simply claimed, the game is simply won, and the result card appears
instantly. A finished board still *shows* its win line statically, the same as the claim
mark — the line is state display, not animation; only the ~1s draw is the animation that's
skipped.

Don't worry about animations at all in this mode. The game state changes and the screen
shows the new state. That's it.

Practical consequence: animations are a **pure layer on top**. The game has to be fully
playable and fully readable with every animation stripped out.

## Open Questions
- **Can a theme describe a shadowbox as drawn?** The vocabulary describes shadowbox as
  lifting the marker off the board, which is directional and offset — a symmetric glow is
  not. Does the set of animatable properties need one more member for it, or is a glow
  close enough?
- **What should happen when a theme describes motion the runtime cannot execute?** Play
  nothing and change state instantly, treat it as a theme that failed to load (see
  [Theming](./Theming.md)), or fall back to Neon's motion for that moment?
- **If a second animation is triggered while one is playing, does it queue or is it
  dropped?** "Never overlap" rules out playing both, and "never interrupted" rules out
  replacing the one that's running — which leaves queueing it or dropping it.
- **What happens if animations are switched off while one is playing?** Does the running
  animation finish, or stop where it is? "It isn't interrupted or skipped" and "with the
  toggle off nothing runs" both fit.
