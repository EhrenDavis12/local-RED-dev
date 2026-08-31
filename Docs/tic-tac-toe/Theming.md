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
- Chrome icons — the settings icon, close X, chevrons, plus, and the trash button on an
  open-game row.
- Every surface: modals (winner, draw), sheets (theme select, in-game quick actions), the
  scrim behind them, the settings card, open-game rows and their chips, badges, the
  main-menu logo, and a gradient-capable page background.

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

**Ask that about a slot's *shape*, not only about whether it exists.** A slot that exists
but can't express what its consumer has to draw is impossible too, and it hides better,
because a completeness check finds the slot present and moves on. When a component draws
several distinct treatments and the theme offers it one, the only thing left to write is a
choice made in code — a hardcoded value with no literal in it for a guard to catch. So a
component that draws N treatments gets N themed values, not one plus a switch.

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

**A theme file the app cannot read is left out of the theme list, and nothing tells the
player it exists.** There is no "this theme is unavailable" message anywhere — the broken
file is simply absent from the picker, and every other theme still lists normally. The
same holds when the unreadable file is the one the player last chose: the app falls back
to Neon at launch and says nothing about it. Neon is the one theme with nothing to fall
back to — see **Neon Is the Base Theme** below.

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

Two things sit outside the merge. **A list is a leaf** — a theme naming a list replaces it
whole, because there is no stable identity for "the second item" to merge against. And **a
theme's identity, its display name and its one-line description are never inherited**: a
theme that omits its name fails to load rather than quietly showing Neon's.

**A theme may only name a key Neon already defines.** A key the base does not define, at
any depth, is refused and the theme fails to load — it reads as a typo rather than as an
intentional override. That runs the other way too: a slot Neon does not spell out is a slot
no theme can ever use. So Neon carries every slot explicitly, with `null` where it draws
nothing, and Neon's null is a deliberate clear rather than an unfilled gap.

**A section is cleared key by key, never wholesale.** A theme writing `images: null`
replaces the whole section with a scalar rather than clearing the slots inside it, the
parser refuses it, and the theme is dropped from the picker. The colour and mark sections
have the same shape; none of them is nullable.

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
- **Fallback happens once, not per lookup.** Every installed theme — not just the selected
  one — is materialized into a complete theme at startup by merging over Neon, so at
  runtime every lookup hits a complete theme and there is no fallback step. See
  [Tech Design](./Tech%20Design.md) → The Theme System.

### Closing Neon's value gaps
**The drawn values from the design handoff are transcribed into Neon's YAML.**
`assets/themes/neon.yaml` is our file and the handoff README is the design source, so
writing those values into it is **authoring Neon**, not editing an approved asset.

The gap between the approved `neon.theme.json` and the drawn handoff — badges, modal and
sheet surfaces, several radii and glows — closes by transcription into Neon's YAML.

Two consequences:
- The read-only `neon.theme.json` stays as it is; it is a reference, and Neon's shipped
  YAML is the complete definition. That means the two can drift, and the YAML is
  authoritative where they differ.
- Where the handoff draws no value at all, transcription cannot help and those values need
  authoring from scratch. The trash button and the delete confirmation's treatments were
  decided after the handoff was drawn, so nothing draws them. The settings purchases
  section has no approved screen showing it. And how far the mark grows in its pop is
  nowhere: the handoff gives the pop a duration and an easing but never a magnitude.
  Those gaps stay open.

### Watch out for
A partial theme inherits Neon's *personality*, not just its values. Classic Red vs Blue
with Neon's electric buzz sounds and glow animations may feel mismatched — clean visuals
with electric audio. That's a fine default (it works, nothing is missing), but Red vs Blue
may want to override more than just colors to feel coherent. Worth checking once it's
real; not a problem to solve now.

### The quadrant fill and its veils move together
The locked, claimed and cat-game veils are drawn on top of the quadrant's fill, not on the
theme's own ground, so their correctness is relative to the fill, not to the ground. A
theme that overrides the fill while inheriting the veils, or the other way around, gets
veils tuned for a fill they are no longer drawn over. The fill and the veils have to be
overridden together or not at all.

A theme may also clear the quadrant fill entirely, leaving no card behind the small board
at all — in that case the veils fall on the page background instead of on a fill. The same
point holds there, more so: a theme that clears the fill owns its veils all the more,
because they now have to read against the background rather than against a card.

---

## Theme Catalog

**Three themes ship at launch — Neon, Classic Red vs Blue and Sewing.**

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

### Theme 3 — Sewing
A sewing box on the board. The marks are the tools, and everything has a 3D-like texture
to it, achieved with shadows.

- **The X is a pair of fabric cutting scissors** — the blades on top and the handles on
  the bottom of the X, opened wide and drawn thick and dark so they read in a board cell.
- **The O is a button** with the four holes in the centre.
- **The background is a soft blue cloth** with a gentle drape and soft folds, like a
  curtain or the folds of a dress. It is smooth and fine rather than coarse and woven,
  and deliberately calm, so the board and the text read over it.
- **The nine small boards sit directly on the cloth.** There is no card or box drawn
  behind a small board — the boards are separated by the ribbon alone, which is what lets
  the ribbon stand out.
- **Text that would otherwise sit straight on the background sits on a light-blue denim
  patch** — a scrap of blue jean drawn behind the words so they can be read easily.
- **Each of the three scoreboard chips sits on its own scrap of fabric**, a different cut
  behind Player One, Cat and Player Two, so the three read as three rather than as one
  strip.
- **Every button is a spool of thread**, at every tier — not only the large main-menu
  pair: *"We allso need the spools of threads to be for all the buttens this include the
  Settings and About Us on the main page. The saved games, and the Exit to Main Menu"*
- **The settings icon is a thimble.**
- **The four lines inside each small board are sewing needles.**
- **The four separator lines on the big board are a deep blue twisting ribbon**, with a
  V-cut at each end, drawn in the gap between the quadrants. It is deep so it stays
  clearly darker than the pale blue cloth it is drawn on.

*"What if the inner boards are sewing needles those would be thin as needed to prevent
the crouded ness. And the large board is the ribbons. This should add a deabth of detail
a user would like."*

**Sewing's palette is blue**, and the look it is aiming for is a fabric workshop or a desk
full of sewing things. This theme is judged on being pretty — *"The objective is pritty
for this theme."*

**Sewing is a full theme, not an inheritance proof.** Classic exists to demonstrate the
merge; Sewing is designed to be looked at, so its art is authored rather than inherited.

**Sewing snips.** Its signature sound is a scissor snip — a short, crisp cut of fabric
scissors, as distinct from Neon's electric buzz and Classic's wet splat.

---

## Free and Paid Themes
**Which themes are free is answered outside the theme file, and today every theme that
ships is free.** Neon, Classic Red vs Blue and Sewing all ship free. Sewing is intended
to become a paid theme once purchasing is in place, and that flow is not built yet. The
theme selection list **labels** which themes are free and which are paid, so a paid theme
drops in without redrawing the screen.

*"Ship it now for free but this will morelikly become a paid theme after we get payments
inplace."*

**Ownership is not part of a theme definition.** A theme file carries no ownership or
price key — whether a theme is free, owned or locked is answered outside the theme, so the
same file ships unchanged whether it is free or paid.

## What a Theme Controls
Everything visual and audible. Rough list, not exhaustive:

**Visual**
- Board background / page background — "really cool backgrounds"
- **A patch drawn behind text.** A theme may supply a patch image that is drawn behind
  text which would otherwise fall straight on the page background, so the words stay
  readable over a busy or low-contrast ground. A theme that supplies none draws its text
  straight on the background.
- **Grid lines, and there are two sets of them.** The four lines inside each small board,
  and four separator lines across the big board, drawn in the gap between the quadrants
  — colors, thickness, style and art, for both sets. Each set carries its own thickness,
  so a theme sizes the small board's lines and the big board's separators independently.
  A theme that supplies no big-board art leaves the quadrants separated by the gap alone.
  See [Game Board Design](./Game%20Board%20Design.md) → Board Structure.
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

  **Mark art is authored to read at the size it is drawn.** A mark fills one cell of an
  81-cell board on a phone, so fine detail and photoreal shading collapse into a smudge
  there. Marks are drawn with thick, dark, well-separated shapes that survive that size.
- **Last-move highlight** — the exaggerated treatment on the opponent's most recent mark
- **Active-quadrant highlight** — where you're allowed to play
- **Locked/inactive quadrant styling** — the dimmed state on the eight you can't play in
- **Pending-move preview styling** — the provisional select-before-confirm state. The
  outline round the pending cell, and round the quadrant that move would send the
  opponent to, is drawn from a colour of its own rather than from the theme's body text:
  a theme is free to put dark text on a light ground, and that choice must not darken a
  highlight that still has to read against the board.
- Claimed-quadrant styling
- Cat-game quadrant styling
- Turn indicator styling
- **Scoreboard styling, and art behind each chip.** A theme may supply its own image
  behind each of the three chips — Player One's, Cat's and Player Two's — so the three are
  tellable apart at a glance rather than sharing one cut of the same cloth. A theme that
  supplies none gets the flat chip fill it draws today.
- **`chipTextOnFabric`** — the chip label and value colour used only when a chip is backed
  by art, because the active/inactive ink split that works on a flat fill stops reading on
  fabric.
- Main menu styling (background, button look, title)
- **Menu button art, at both tiers.** A theme may supply art drawn behind a big-tier
  button and art drawn behind a small-tier button — two slots, never one plus a switch,
  because the two tiers are two distinct treatments. A theme that supplies neither gets
  the outline and label the button draws today. Both tiers are one shared widget each, so
  a theme's button art turns up wherever those widgets are reused — the open-games list's
  **New Game** control and the in-game quick-actions sheet — and not only on the main
  menu.
- **`menuButtonSmallFill`** — a fill behind a small menu button's label. Without one the
  label sits straight on the ground: fine on a near-black ground, unreadable on a busy
  light one.
- **Board geometry** — grid-line width, grid-line inset, mark sizes. Spacing and padding
  (outer gap, quadrant padding, inner gap) are fixed in code, not theme-controlled — see
  **What a Theme Does NOT Control** below.
- **Corner radii** — cell, quadrant, modal, chip, control, button
- **The font** — a theme supplies its own typeface. Inter 400/500/600 is bundled as
  **Neon's** font choice, not as an app-wide font constant. See
  [Tech Design](./Tech%20Design.md) → The Theme System → Themes pick their own font.
- **The type scale** — sizes and weights, distinct from a theme's choice of font
- **`accentOnSurface`** — the accent step that must read on a *card*, distinct from the
  one that must read on the *ground*. No single value serves both.
- **Opacities** — the locked, claimed and cat-game veils, and `pendingGhostOpacity`, the
  pending cell's ghost-mark opacity
- **Modals** — winner, draw
- **Sheets** — theme select, in-game quick actions
- **The scrim** — the dimming drawn behind a modal or a sheet
- **The settings card**
- **Open-game rows and their chips**
- **Badges**
- **The main-menu logo**
- **Page background** — gradient-capable
- **Chrome icons** — the settings icon, close X, chevrons, plus, and the trash button on
  an open-game row. A theme may either name a glyph from a bundled icon set or ship its
  own image. The gear is Neon's art for the settings icon, not the name of the slot —
  Sewing draws a thimble there.

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

## How a Theme's Art Is Drawn

**Every art slot is optional.** Absent, cleared, or naming a file that will not load all
draw exactly what the app draws with no art at all — which is why Neon and Classic Red vs
Blue, which name none of them, look the same as they did before any art slot existed. What
a theme may name is **What a Theme Controls** above; this section is how each one gets
drawn once it is named. An art slot names one still image — there is no multi-frame or
animated art.

**A mark's image lives in a key of its own, beside the glyph rather than on top of it.** An
image mark names its file in its own key, never in the glyph's. Because the merge is deep,
an image mark written over Neon's glyph keeps Neon's glyph, its font and its weight
standing underneath it — and that inherited glyph is exactly what gets drawn if the image
will not load. Reusing the glyph's key would overwrite it with a path and leave nothing to
fall back to, and a blank cell in the middle of a game is the one failure this must not
have. Chrome icons work the same way, from the same slot shape.

**One image serves all four lines of a cross.** The art is authored running horizontally;
the two horizontal lines draw it as authored and the two vertical lines draw it rotated a
quarter turn clockwise, so all four read as running in the same rotational sense. That
matters because art has a direction where a stroke does not — a needle has a point at one
end and an eye at the other, and without a rule four needles meeting in a cross would point
whichever way each call site happened to choose.

**Art is measured by its opaque pixels, not by its file.** Generated art arrives centred in
a wide transparent margin — a needle can occupy 6% of its frame's height — so fitting the
file would draw a hairline inside a box that is almost entirely nothing. Marks, chrome
icons, grid-line art, the text patch and the scoreboard chips' art are positioned and
scaled by the smallest rectangle holding every pixel whose alpha is at least 0.05, computed
once when the image loads.

The threshold is load-bearing, not a tidiness detail. The art is drawn with soft drop
shadows, so "alpha greater than zero" would catch the faintest tail of a shadow and hand
back nearly the whole frame — trimming nothing while appearing to work. It sits below
anything a player can see against any ground and above the shadow tails. And the code trims
rather than the file being cropped by hand, because a rule that holds only when somebody
remembered to crop is not a rule the theme system can rely on: the next theme drops in an
untrimmed file and gets a hairline with no error anywhere.

Two slots are exempt, because they are authored to fill their slot rather than to sit
inside a margin: the page background and the two menu-button tiers are drawn from the
whole file.

**A mark's image is centred and contained in a square whose side is the theme's own mark
size** — the in-cell size, or the claim size when a whole quadrant has been won. It keeps
its aspect ratio and is never cropped. Reusing the sizes the glyph already used keeps the
art proportional to the glyph it replaces and adds no second geometry slot. A chrome icon
gets the square its own type size gives it, for the same reason.

**A grid-line image is stretched along the line it replaces and takes its thickness from
the theme.** Length and thickness are set independently and the source aspect ratio is not
preserved — it cannot be, because no line's rect matches the art's shape. When the art
draws, the stroked line and its blur glow are not drawn underneath it, and the grid-line
opacity is not applied to it either: that value tints the stroke this art replaces, and
fading a theme's own artwork by a number authored for a colour is not what a theme author
asked for.

**A page-background image covers the whole screen, centred, cropping whatever overflows,
and sits beneath everything.** It replaces the flat ground fill on every screen and the
radial gradient on the main menu. It is never tiled — nothing guarantees generated art
tiles seamlessly, and a seam grid running across the background is worse than a crop. The
ground colour still fills the screen underneath, so nothing is ever blank while the image
resolves, and the three places that read the ground colour for something that is not a
screen background — the settings toggle's off track, the result card's REMATCH label, the
new-game prompt's text field — keep reading the colour.

**A menu-button image fills the button's box exactly, beneath the label, and replaces the
outline.** The art is clipped to the button's themed corner radius rather than drawn square
into the corners, so a themed radius still describes the button's shape instead of being
silently overruled by the artwork. The label still draws on top, in its own type style and
colour. The button's box is what the player taps, so the art has to occupy exactly that
rect or the art and the tap target disagree.

**Art that will not load is silent.** A named image that is missing or unreadable renders
as though the slot were absent — no crash, no blank region, no dialog, no banner, and
nothing said to the player. A bad mark path draws the glyph beneath it, a bad background
draws the ground colour, a bad small-board line draws the stroke, a bad big-board line
draws nothing at all, and a bad button draws its outline. A named audio file that will not
load is simply silent, the same way a sound that cannot load already is.

**Naming a file that is not there is not a parse failure.** Art is resolved when it is
drawn, not when the theme is loaded, so a theme whose art is missing still parses, still
appears in the picker and is still selectable. Only a theme file the app cannot *read* is
dropped from the list — see **Choosing a Theme** above.

## Sound Decisions

### Sound falls back to Neon
A specific case of the general inheritance rule above — themes don't need a full sound
set; anything undefined comes from Neon.

### Placing a mark may sound different for each player
**A theme may give Player One and Player Two their own placing sound**, so each player's
move sounds like their own piece — Sewing snips its scissors for Player One and rubs
fabric for Player Two. A theme that names only the one shared placing sound gives both
players that, which is what every theme without a per-player pair does.

This is still **one** moment, not two. Placing a mark is a single thing that happens, and
which of a theme's two files it reaches is that theme's business — the same way every
other sound in the game resolves.

### Music
**A theme supplies its own music**, the same way it supplies its sounds. *"Do all four
toggles, Music should be apart of the Theme documents."*

**One track for the whole app, taken from the selected theme.** *"ONe sound.music app wide
baised on selected theme."* Music does not differ by screen.

All four settings toggles ship — Music, Sound Effects, Vibrate on Touch, Animations. See
[Menus and UI](./Menus%20and%20UI.md) → Settings Menu.

**The music is long and it loops seamlessly.** The track fades in at the start of each
loop pass and fades out at the end, so the loop point lands on silence rather than a hard
cut. **The app applies that fade at playback, not the file** — *"this way any music
works."* Nothing depends on a track carrying its own fade, which is what keeps a future
theme's music from having to fade itself.

**There are two fade lengths, not one.** The loop point fades over a second and a half
each way, because a seam nobody should notice needs a long dip that is never heard as one;
the first pass at launch fades in over the same length, since it is the start of a pass
like any other. A theme change, or the Music toggle coming back on, fades in over half a
second instead, because that is a reaction to a tap the player just made and three seconds
of near-silence after tapping a theme reads as the app being slow. The two answer different
questions, so one number would be a bad compromise on both. Neither is a theme value — both
are properties of how this app plays audio rather than of how a theme sounds.

**The music starts once, at launch, and keeps playing across screens.** Nothing starts it
per screen; that would restart the track on every navigation, which is not one track for
the whole app.

**Selecting a theme swaps the music immediately.** The old track stops where it is and the
newly selected theme's track fades in, in the same session with no relaunch. A theme that
names no music goes silent on selection rather than keeping the previous theme's track.
Letting the old track run until the next launch would make a theme's own music unreachable
in the very session a player picked that theme.

**Turning Music off cuts the track off where it is; turning it back on restarts it from the
beginning.** Off takes effect at that instant, not at the end of the pass, and the track
does not play out — the same behaviour the sound-effects toggle already has, so the two
toggles that silence a theme channel behave the same way rather than one stopping dead and
the other finishing its bar. The stop is not faded: a fade there would soften a change the
player just asked for and be heard as the switch being slow. Coming back on restarts rather
than resumes, because carrying a playback position across a stop buys nothing.

The audio is generated through the same pipeline as the art — see
[Tech Design](./Tech%20Design.md) → Where sound and art assets come from.

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
