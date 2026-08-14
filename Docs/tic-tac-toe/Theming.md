# Theming

> **Status:** Brain dump. Contradictions are expected and OK.
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

Meaning — no hardcoded values anywhere in the code. The slot list is derived from what the
screens actually consume, not from a category list written in the abstract:
- Colors, backgrounds, fonts, piece styles, sounds, animations.
- Board geometry — grid-line width, grid-line inset, mark sizes. Spacing and padding —
  outer gap, quadrant padding, inner gap — are the one named exception; see **What a Theme
  Does NOT Control** below.
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
  the theme.** No exceptions once the app is running — the one screen drawn without a
  theme is the **Failed to load Neon Theme** screen, which exists precisely because there
  is no theme to read; see **Choosing a Theme** below.
- Adding a new theme should require zero changes to game/board/menu code — only adding
  a new theme definition.

This is a day-one constraint because retrofitting it later means touching every file.

**When a theme value is missing, ask whether the absence is *ugly* or *impossible* — only
the second one blocks.** Ugly: a slot exists in the schema and a consumer reads it, but
nobody has authored a value yet. The feature ships — it renders, it looks wrong, and it
gets fixed later by authoring one value with no code change, because the key and its
reader are already there. This can wait for a design pass. Impossible: there is no slot to
read *and* the rule above forbids writing the value literally in code. Then there is no
legal implementation at all — the feature doesn't ship, and scheduling doesn't help,
because no amount of later authoring changes what a developer can write today. This can't
wait.

A missing colour is the ugly case — a delete button renders unstyled, which is legal and
shippable. A missing icon, where there's no slot to read and no permitted literal, is the
impossible case — the button can't be drawn at all. One is debt, the other a deadlock, and
treating them the same schedules the wrong one.

<!-- Enforced by: the hardcoded-theme-value test, which covers the slot inventory listed
     above. See Tech Design → Testing → A test that fails on hardcoded theme
     values. -->

## Where Themes Live
- **For now, themes are contained within the codebase.** Bundled/shipped with the app.
- Not user-uploaded, not downloaded from a server, not user-authored. That's a possible
  later thing, not now.
- **The app discovers themes by scanning the themes folder**, and each theme file carries
  its own display name and one-line description. Adding a theme is dropping one file in —
  no second file to edit, no code change.

This follows directly from the principle already stated for animations: *"i want to drop a
file in the new theme folder that can tell the application what animations are and
everything else the applicaiton needs to know."* The name and blurb are part of "everything
else."

There is no separate catalog file as the source of truth, and no hardcoded list in Dart.
The handoff's `themes.catalog.json` is a reference asset, not a shipping input.

## Choosing a Theme
Theme selection lives **on the main menu**. Themes up front — a nice big button, the same
size and treatment as the Play Game button. Not buried in a settings screen. It opens as
an overlay on the main menu rather than its own screen — see
[Menus and UI](./Menus%20and%20UI.md) → Theme Selection.

**The selected theme persists between sessions.** Once a player selects a theme, it stays
active. Close the app, open it again, that's still their theme. Requires persisting the
selection to device storage.

<!-- The persisted value is the theme's UUID, not its name, so renaming a theme does not
     lose the selection. See Tech Design → The Theme System. -->

**You can't change the theme mid-game** — leave it out for now. Theme changes happen from
the main menu only. Possible later feature if we decide we want it.

**If a theme fails to load, a modal on the Theme screen says the theme is unavailable, and
the app falls back to Neon.** *"From the Theme screen if a theme fails to load put up a
modal with sorry this theme is unavailable please try another theme. Then fallback to
neon."* Neon is the one theme with nothing to fall back to — see **Neon Is the Base
Theme** below.

**If Neon itself fails to load, the app does not start.** The first screen is a
**Failed to load Neon Theme** screen and the player cannot get past it: *"If Neon fails to
load then the first screen should be Failed to load Neon Theme. dont let the user proceed
its a loud fail."* A loud, deliberate hard stop — not a degraded mode, and not a silent
one.

**That screen is drawn in plain, unstyled text, like a raw error message** — no theme
values, no branding, no styling of any kind, because the thing that supplies styling is
what failed: *"Just put it in play text like an error message this should never happen. so
we want this failing loud. Only if Neon fails."* It is the one screen in the app drawn
without a theme, and it should never appear.

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

### The merge rules
**Deep merge, null = clear.** *"If the new theme has no value at all then that is inherit.
Like it's missing the option entirely."* Three distinct cases:

- **Key absent** from the overriding theme → inherit Neon's value.
- **Key present with a value** → that value wins.
- **Key present and explicitly null** → the value is *cleared*, not inherited.

And the merge is **deep**: a theme naming one key inside a section keeps Neon's other keys
in that section rather than replacing the whole section. Nested maps merge recursively.

See [Tech Design](./Tech%20Design.md) → The Theme System.

**Consequence:** `neon.theme.json` ships `sound.music` as an explicit `null`. Under this
rule a null means "cleared," so Neon's own null is a deliberate clear rather than a gap —
worth noting so nobody later mistakes it for an unfilled slot.

### Why this matters for the build
- **Neon must be complete before anything else ships.** It's the floor everything stands
  on. A gap in Neon is a gap with no fallback — that's the one failure the system can't
  absorb.
- **New themes become cheap.** A theme can be as small as "black → white, neon green →
  red" and still be a complete, working theme. That directly supports adding more themes
  later.
- **Fallback happens once, not per lookup.** Each theme is materialized into a complete
  theme at startup by merging over Neon, so at runtime every lookup hits a complete theme
  and there is no fallback step. See [Tech Design](./Tech%20Design.md) →
  The Theme System.

### Closing Neon's value gaps
**The drawn values from the design handoff are transcribed into Neon's YAML.**
`assets/themes/neon.yaml` is our file and the handoff README is the design source, so
writing those values into it is **authoring Neon**, not editing an approved asset.

Two consequences:
- The read-only `neon.theme.json` stays as it is; it is a reference, and Neon's shipped
  YAML is the complete definition. That means the two can drift, and the YAML is
  authoritative where they differ.
- Where the handoff draws no value at all — the settings purchases section is the known
  case, since no approved screen shows it — transcription cannot help, and those values
  still need authoring from scratch. That gap stays open.

### Watch out for
A partial theme inherits Neon's *personality*, not just its values. Classic Red vs Blue
with Neon's electric buzz sounds and glow animations may feel mismatched — clean visuals
with electric audio. That's a fine default (it works, nothing is missing), but Red vs Blue
may want to override more than just colors to feel coherent. Worth checking once it's
real; not a problem to solve now.

---

## Theme Catalog

**Two themes ship at launch — Neon and Classic Red vs Blue.**

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

**Classic is the inheritance proof, not a second designed theme.** *"still build out the
Red vs Blue theme with some minor changes to the schema to represent the Red Vs Blue
theme. But it will mostly be an example and Proof of how it inherits from Neon."* Neon is
the base and cannot inherit from anything, so Classic is the only place the inheritance
model is ever exercised before launch. It has to override enough to demonstrably differ,
and inherit the rest visibly and on purpose — it is not held to being a fully-designed,
shipping-quality theme.

**What it overrides:**
- **Graphics.** That's the override — the art and colors. Red player, blue player, no
  black background.
- **Sound:** a **splat** — like a water balloon popping. Wet and playful, deliberately
  nothing like Neon's electric buzz.

**The palette:** `#f3f5fe` for the ground, `#d92d3f` for player one, `#2453c4` for player
two. These are Classic's real palette, not placeholder swatches, and every other value in
the theme derives from them.

A colour that is a tinted or alpha-adjusted version of one of these three must be
recomputed from the new value rather than inherited from the first theme, because
inheriting one silently produces a red player with pink chips.

**Classic is a light theme, and that is more than a palette swap.** Its ground is
near-white where Neon's is near-black, so any value whose correctness depends on its
*relationship* to the ground — contrast, not hue — has to be overridden rather than
inherited. Neon's text ramp is the certain case: inherited whole it puts near-white text
on a near-white ground, which is unusable rather than merely off-palette. A hue-defined
value is different — red is red because red is the design, not because of what sits behind
it — which is why the three anchors are anchors.

**What it inherits from Neon:** everything else — animations included.

The two themes now have distinct sonic identities: Neon **buzzes** like a light,
Classic **splats** like a water balloon.

---

## Free and Paid Themes
**Neon and Classic Red vs Blue are free. Every theme beyond those two is paid.** The theme
selection list **labels** which themes are free and which are paid.

*"We will label what themes are free as of now we will have 2 free themes the neon and
the red Vs Blue themes any other themes will be a paid for theme."*

**Ownership is not part of a theme definition.** A theme file carries no ownership or
price key — whether a theme is free, owned or locked is answered outside the theme, so the
same file ships unchanged whether it is free or paid.

## What a Theme Controls
Everything visual and audible. Rough list, not exhaustive:

**Visual**
- Board background / page background — "really cool backgrounds"
- Big board and small board grid lines (colors, thickness, style)
- **The player marks themselves** — marks are not locked to X and O. A theme supplies its
  own mark art as a **glyph, an image or an icon** — those three kinds, and nothing else.
  **The image is the real answer for a theme;** the glyph and the icon are the short
  route, so nobody has to author image files for something as simple as an X and an O:
  *"truly it can just be images and the image would just show an X and another an O if it
  really comes done to issues between icons or images. But for themes it would have ot be
  an Image, Icons were just the short route so we dont need to create images for such a
  thing. If nessasary create a .svg of an X and an O and convert that into an image."*
  Where neither a glyph nor an icon will do, the mark is drawn as an `.svg` and converted
  to an image. A theme might swap the marks for icons, emoji, animals or shapes — a
  dinosaur theme might use a T-Rex — and the theme system must be built so that's
  possible. Neon still uses X and O; that's Neon's choice of art, not a constraint on the
  system.
- **Last-move highlight** — the exaggerated treatment on the opponent's most recent mark
- **Active-quadrant highlight** — where you're allowed to play
- **Locked/inactive quadrant styling** — the dimmed state on the eight you can't play in
- **Pending-move preview styling** — the provisional select-before-confirm state
- Claimed-quadrant styling
- Cat-game quadrant styling
- Turn indicator styling
- Scoreboard styling
- Main menu styling (background, button look, title)
- **Board geometry** — grid-line width, grid-line inset, mark sizes. Spacing and padding
  (outer gap, quadrant padding, inner gap) are fixed in code, not theme-controlled — see
  **What a Theme Does NOT Control** below.
- **Corner radii** — cell, quadrant, modal, chip, control, button
- **The font** — a theme supplies its own typeface. Inter 400/500/600 is bundled as
  **Neon's** font choice, not as an app-wide font constant. See
  [Tech Design](./Tech%20Design.md) → The Theme System → Themes pick their own font.
- **The type scale** — sizes and weights, distinct from a theme's choice of font
- **Opacities** — the locked, claimed and cat-game veils
- **Modals** — winner, draw
- **Sheets** — theme select, in-game quick actions
- **The scrim** — the dimming drawn behind a modal or a sheet
- **The settings card**
- **Open-game rows and their chips**
- **Badges**
- **The main-menu logo**
- **Page background** — gradient-capable
- **Chrome icons** — the settings gear, close X, chevrons, plus, and the trash button on
  an open-game row. A theme may either name a glyph from a bundled icon set or ship its
  own image.

> **Every theme must keep these legible.** The last-move highlight and active-quadrant
> highlight are *gameplay-critical*, not decoration — a theme that makes them hard to spot
> breaks the game. A pretty theme that hides the last move is a broken theme.

Distinguishing things by more than colour is **handled per theme** — a theme can add
non-colour distinguishing features, and the theme system has to allow it: shape, icon,
outline, pattern. It is not a system-wide rule: *"Themes will be defined and other things
can be added for this."*

**No theme is required to do it.** Classic Red vs Blue happens to separate its players by
shape as well as by colour, but that is that theme's own choice, not an obligation the
system enforces — a theme whose two players differ by hue alone is still a valid theme:
*"colour-blind players We wont have themes require this type. Red VS blue can sill have
different shapes like like X and O but even it it was splats that are similar and red vs
blue the Theme is not necessary thinking about color blindness. If a theme does that
poorly then another theme would be better from them."* A theme that handles it badly is
simply not the theme for that player: *"Im not interested in Color blind handling that
theme just wont be for that person."*

This is separate from the legibility requirement above, which every theme must still meet.

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

### Music
**A theme supplies its own music**, the same way it supplies its sounds. *"Do all four
toggles, Music should be apart of the Theme documents."*

**One track for the whole app, taken from the selected theme.** *"ONe sound.music app wide
baised on selected theme."* Music does not differ by screen.

All four settings toggles ship — Music, Sound Effects, Vibrate on Touch, Animations. See
[Menus and UI](./Menus%20and%20UI.md) → Settings Menu.

Nothing currently produces any music. Whether music loops and where the audio comes from
are not settled — see Open Questions.

### The tap sound
**One tap sound, everywhere.** Every button, row and toggle plays the same short tap
sound: menu buttons, theme rows, settings toggles, the game-over card's two controls, the
trash button and the modal's Yes and No. One sound file covers all of it.

This matches the haptic — see [Game Board Design](./Game%20Board%20Design.md) → Haptic
Rule — so the two feedback channels behave consistently rather than one buzzing where the
other is silent.

The board sound moments are separate — placing a mark, claiming a quadrant, the cat game,
winning — and an invalid tap stays silent in both channels.

### Global mute
There's a **global mute / sound toggle, separate from the theme.** Muting is a player
setting, not a theme property — you can mute any theme.

- **Global for the whole game**, not per-theme.
- **Remembered between sessions** — the toggle stays in whatever state it was left in,
  same as the theme selection.
- Lives in the **Settings menu** (see [Menus and UI](./Menus%20and%20UI.md)), and is
  offered again inside the in-game quick actions.
- **Flipping it mid-game takes effect immediately** — not at the next game, and not at
  the next launch. **Muting cuts off a sound that is playing right then**; it stops where
  it is rather than playing out.

**It silences the sound effects and nothing else.** With it off, no sound plays at any of
the board or button moments, under any theme. Music has its own toggle and keeps playing;
haptics and animations are untouched.

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
| Music | ✅ Yes |
| Animations | ✅ Yes |
| **Haptics / vibration** | ❌ No — app setting |
| **Spacing and padding** | ❌ No — fixed in code |
| **The words on screen** | ❌ No — copy is fixed in code |
| **Ownership and price** | ❌ No — answered outside the theme |

Note the asymmetry with the settings toggles: music, sound and animations are
*theme-defined but player-switchable*, while haptics are *never theme-defined at all*. The
four toggles in [Menus and UI](./Menus%20and%20UI.md) look alike, but three of them switch
off a theme channel and one switches off an app behavior.

Spacing and padding are also **not** theme-controlled: spacing and layout numbers are
fixed in the code — for now. *"No spacing will be fixed for now."*

This is the one place that cuts against the project's general direction of pushing as much
as possible into the theme. The reason is enforcement: the hardcoded-theme-value test (see
[Tech Design](./Tech%20Design.md) → Testing → A test that fails on hardcoded
theme values) **cannot** catch a hardcoded gap. It can see a colour, a font size, a radius
or an asset path, but `SizedBox(width: 8)` holding a themed gap and `SizedBox(width: 8)`
holding an incidental one are indistinguishable to it. A padding section in the schema
would therefore have been a rule that nothing verifies — a claimed guarantee the project
could not keep.

Themes still control colour, marks, sounds, icons, animation, radii and the type scale.
Spacing and padding is the one slot pulled out of the inventory, and "for now" is the
user's own hedge — this is reversible if the enforcement story changes.

**A theme styles text; it does not write it.** The words themselves are fixed in code —
the scoreboard's three chip labels, the settings toggles' names and their sub-labels. A
theme sets their size, weight, tracking and colour; the strings are content, not style.

**Stated in its own terms:** a theme controls **everything visual about the game except the
placement of objects** — the art, the icons, the images, the music and the sound effects
are all the theme's. The grid lines are the clearest case: *"I want ribbons as the tick tac
to lines. This should be controled by the theme but the pacment of the lines is still
controled by the game its self. jsut what those lines look like is contoled by the theme."*

Concretely: a theme controls **the drawn geometry of a thing itself** — stroke width, glyph
size, corner radius, glow spread. Code controls **where things sit relative to one
another** — gaps, padding, margins. Element *sizing* is where a theme's visual range lives;
element *spacing* is layout. Classify a new value with that sentence, not by looking for
the word "padding."

## Open Questions
- Which values, concretely, does Classic Red vs Blue override? (Settled in principle —
  graphics and its splat sound, inheriting the rest. An exact list will fall out when it's
  actually built.)
- **Which values beyond the text ramp are ground-relative**, and therefore have to be
  overridden rather than inherited when Classic inverts Neon's ground? The text ramp is
  the certain case. The veils and scrims, the hairlines and the glows are candidates on
  the evidence, not a settled set — and the smaller Classic's override set, the more each
  remaining inheritance carries.
- **Which of the theme's playable sounds does Classic's splat fill?** The playable moments
  are placing a mark, claiming a quadrant, the cat game, winning, and the tap sound. The
  tap sound is the live one now that one tap sound plays on every button, row and toggle —
  a splat there is heard constantly, and a buzz there is Neon's personality on every
  Classic screen.
- **Does Classic override the marks at all?** A theme may supply its own mark art, but
  nothing says Classic uses it — the handoff gives Classic the same ✕ / ○ marks as Neon.
- What is the exact slot schema — the key structure — for what a theme defines? The
  approved `neon.theme.json` does not currently cover the pending-move highlight, any
  modal or sheet surface, a gradient background, or a logo.
- Neon is required to be complete (see **Neon Is the Base Theme**). The gap between the
  approved `neon.theme.json` and the drawn handoff — the pending-move highlight, badges,
  modal and sheet surfaces, several radii and glows — closes by transcription into Neon's
  YAML (see **Neon Is the Base Theme** → Closing Neon's value gaps). The settings
  purchases section is the one value with **no drawn counterpart at all**, since no
  approved screen shows it — transcription can't supply a value nothing draws, so that
  piece still needs authoring from scratch. Is the purchases section the only such case,
  or are there others the handoff never drew?
- What form does the legibility contract take — a contrast floor, a review step,
  something else? **What a Theme Controls** requires every theme to keep the last-move
  and active-quadrant highlights legible, but this is unfalsifiable as written: Classic
  Red vs Blue has a near-white ground while inheriting Neon's near-white text and its
  veils and glows tuned for a near-black ground, so a theme could be complete, pass every
  stated check, and still be unreadable.
- **Does motion count as a non-colour distinguishing feature?** **What a Theme Controls**
  lets a theme tell things apart by shape, icon, outline or pattern, and motion is not on
  that list. Two things pull against adding it: animations are a channel the player can
  switch off, so anything carried by motion alone goes with the toggle, and animation
  scope is the player's marker only. Is the list closed, or may a theme distinguish by
  motion as well?
- **Does a theme's music loop?** Not settled by **Sound Decisions** → Music.
- **Where does the music come from** — composed, licensed, generated? Not settled.
- **Can two sounds play at once?** One confirming tap can place a mark, claim a quadrant
  and win the whole game all at the same time. Play all of them together, play only the
  most significant one, or queue them up one after another?
- **What does a drawn big board sound like?** The cat game — a small board filled with no
  winner — has its own sound. A straight draw of the whole board has no sound of its own,
  so as things stand the game that nobody wins ends in silence.
- **Does the game make a noise when the phone's ringer is switched to silent, and does it
  interrupt whatever the player is already listening to?** The two come as a pair: the
  setting that makes the game respect the ringer switch is the same one that leaves the
  player's own music playing underneath it, and the setting that sounds over a silenced
  phone is the one that stops their music. Nothing in the app can check which is right —
  it has to be heard.
