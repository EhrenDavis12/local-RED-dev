# PRD: Theme System

> **Status:** Draft · Source docs read: `Theming.md`, `Tech Design.md`, `Animations.md`,
> `Menus and UI.md`, `Game Board Design.md`, `Game Overview.md`, `Rules.md`, `roadmap.md`,
> and the read-only reference asset `design_handoff_game_ui/` (`README.md`,
> `neon.theme.json`, `themes.catalog.json`). `Alternative Game Styles.md` is a declared
> parking-lot doc and was not used as a source.
>
> **Revised** after `Theming.md` → Architectural Rule was rewritten and → Decisions →
> *What the theme's slots are derived from* was added. The slot list is no longer a closed
> six-category list; it is derived from what the screens consume. Requirement 15 now
> carries the full inventory, Requirements 11–13 were reconciled against it, and
> Requirements 32–34 close three structural gaps found by the consumer PRDs.
>
> **Revised again** after `Menus and UI.md` → Decisions → *Where the open-game slot unlock
> is sold* put a purchases section on the Settings screen. Requirement 15 gains the slots
> that section consumes, and Requirement 13 records them as a Neon gap.

**Wave:** P1 · **File:** `P1-03-theme-system.md`

**Depends on:** `P1-01-app-scaffold.md` — same wave; it creates `lib/theme/`,
`assets/themes/`, `pubspec.yaml` and the Riverpod root this layer lands in. Nothing else:
`src/Tic-Tac-Toe-Extreme` has no application code yet.

**Depended on by** — every PRD below declares this one a dependency, and each is a
consumer of the Requirement 15 inventory:

- Wave 1: `P1-04-persistence.md` (stores the selected theme UUID),
  `P1-05-theme-guard-test.md` (enforces Requirement 25), `P1-07-entitlements.md` (attaches
  entitlement to a theme UUID from outside the theme file).
- Wave 2: `P2-02-audio.md` (plays the sound slots), `P2-03-haptics.md` (relies on
  Requirement 29), `P2-04-animations.md` (plays the animation slots).
- Wave 3: `P3-01-board-rendering.md`, `P3-03-scoreboard-turn-indicator.md`,
  `P3-04-game-over-rematch.md`, `P3-05-how-to-play.md`.
- Wave 4: `P4-01-main-menu.md`, `P4-02-open-games-list.md`, `P4-03-theme-selection.md`,
  `P4-04-settings.md`, `P4-05-purchase-flow.md`.
- Wave 5: `P5-01-classic-theme.md` (authors the second theme against this schema),
  `P5-02-asset-generation-replicate.md` (produces the files these slots name).

This PRD defines the **slots**; those define the behavior.

---

## Problem

There is no application code yet, and the one constraint the design docs say is expensive
to retrofit is the theme system: *"All of our code operates off of the theme. No code
should be operating independently from the selected theme"* (`Theming.md` → Architectural
Rule; repeated in `Tech Design.md` → The theme system is the main architectural risk).
Any screen built before the theme layer exists will hardcode a color, a font, a mark, a
sound or a duration, and every one of those is a file that has to be touched again later.

The failure mode is not hypothetical. `Theming.md` → Decisions → *What the theme's slots
are derived from* records that the original six-category list *"was written before the
screens existed"* and *"omits board geometry and sizing, corner radii, the type scale, and
opacities, and it has no slot for any modal, sheet, settings card, open-game row, badge, or
the main-menu logo — so four PRDs were left unbuildable under the 'no hardcoded values'
rule."* A slot list shorter than what the screens consume does not produce a smaller theme
system; it produces screens that quietly hardcode the difference.

There is also no runtime home for the Neon definition. Neon exists as an approved,
machine-readable file in the handoff bundle, but nothing in the app can load it, merge a
partial theme over it, or hand its values to a widget.

## Goal

The app ships a theme layer in which a theme is a **data file, not code**: YAML, bundled
with the app, identified by a UUID, materialized once at startup by merging over a
complete Neon base, and readable from anywhere in the widget tree. Neon is authored in
full — every slot in the inventory defined, no gaps — because it is the floor with no
fallback. Every visual, audio and motion value any screen in this project consumes has a
named slot on that object, so that adding a theme later requires adding a theme file and
changing no game, board or menu code.

## Requirements

### Themes as data

1. A theme is **data loaded at runtime, not a Dart class compiled into the app** — "a
   universal, theme-like object that can be loaded in."
   *(`Tech Design.md` → Decisions → Theme representation — data, not code)*
2. The on-disk format for theme files is **YAML**.
   *(`Tech Design.md` → Decisions → What format are theme files — JSON or YAML?)*
3. Theme files are **bundled/shipped with the app**, living in `assets/themes/*.yaml`.
   They are not user-uploaded, not user-authored and not downloaded from a server.
   *(`Theming.md` → Where Themes Live; `Tech Design.md` → Decisions → Project structure —
   layer-first)*
4. **Each theme carries a UUID in its YAML file, and that UUID is the theme's identity.**
   Nothing downstream identifies a theme by name — renaming a theme must not change which
   theme it is.
   *(`Tech Design.md` → Decisions → Theme identity — UUID)*
5. The theme layer lives at `lib/theme/`, with `theme.dart` holding the merged theme
   object and `loader.dart` holding YAML → theme.
   *(`Tech Design.md` → Decisions → Project structure — layer-first)*

### Inheritance and materialization

6. **Neon is the base theme.** Anything a theme does not define comes from Neon — colors,
   art style, sound effects, animations, "the whole nine yards."
   *(`Theming.md` → Neon Is the Base Theme)*
7. **Inheritance depth is exactly one level.** A theme inherits from Neon, full stop. No
   chains, no theme inheriting from another theme.
   *(`Theming.md` → Inheritance Depth; corroborated by
   `design_handoff_game_ui/themes.catalog.json` → `inheritanceDepth: 1`)*
8. Fallback is implemented as a **merge, not a per-lookup resolve**: each theme is
   materialized into a complete theme **at startup** by merging its overrides over Neon,
   so at runtime every lookup hits a complete theme and there is no fallback step.
   *(`Tech Design.md` → Decisions → Fallback to Neon — merge, not resolve; `Theming.md` →
   Why this matters for the build)*
9. A theme file may define **only** what it wants to be different; a theme that overrides
   two colors and nothing else must still materialize into a complete, working theme.
   *(`Theming.md` → Neon Is the Base Theme → How it works, Why this matters for the
   build)*
10. Animations and sounds merge by the same rule as every other value — a theme starts
    from Neon's complete set and its own definitions merge over the top, overriding only
    what it names.
    *(`Animations.md` → Decisions → Do themes inherit Neon's animations?; `Theming.md` →
    Sound Decisions → Sound falls back to Neon)*

### The Neon base theme

11. **Neon must define every slot in the Requirement 15 inventory** — it is the one theme
    with nothing to fall back to, and a gap in Neon is the one failure the system cannot
    absorb.
    *(`Theming.md` → Neon Is the Base Theme → How it works; Why this matters for the
    build; What happens if a theme fails to load)*
    **Testable:** Requirement 15's inventory is the checklist. Every slot it names resolves
    to a value in Neon's materialized theme, and that is a test rather than a reading of
    the file.
12. **Where `neon.theme.json` defines a value, that value is authoritative and is not
    re-decided here** — its `color`, `marks`, `type`, `radius` and `board` sections are
    final and exact, and the handoff's *Design tokens* tables are the human-readable form
    of the same values.
    *(`design_handoff_game_ui/README.md` → Fidelity, Design tokens; `Theming.md` → Theme
    Catalog → Neon as drawn)*
13. **`neon.theme.json` does not cover the whole of Requirement 15's inventory, and the
    difference is not this PRD's to invent.** `Theming.md` → Open Questions names part of
    the gap directly: the approved file *"has no pending-move highlight values at all — no
    pending colour, no pending cell ring, no destination ring"*, and *"the same gap covers
    the grid-line opacity and glow, the claimed and cat-game mark glows, and the cat-game
    caption style"*, alongside *"any modal or sheet surface, a gradient background, a logo,
    or a theme's own display name and description."*
    Requirements 11 and 12 are both binding and do not conflict: 12 fixes what is already
    drawn, 11 fixes what Neon must end up holding, and closing the difference is an open
    question carried below rather than a value chosen here.
    *(`Theming.md` → Open Questions, second and third bullets;
    `design_handoff_game_ui/README.md` → Cell states and screen 2d, which draw the pending
    values the JSON omits)*

    **The theme-selection overlay's values extend that gap, and are recorded here because
    the design doc's list does not reach them.** Requirement 15 names a badge slot, and
    Neon holds no value for it. This case deserves naming separately because the nearest
    existing Neon keys are **near-misses**: an implementer who reaches for one is not
    hardcoding anything, so `P1-05-theme-guard-test.md` cannot catch it — the screen is
    simply drawn from the wrong slot, four points of alpha or half a point of type away
    from the approved design.
    *(Values drawn in `design_handoff_game_ui/README.md` → 2a and
    `themes.catalog.json` → `ownershipStates`, `activeBadge`; consumed by
    `P4-03-theme-selection.md` reqs 8, 10, 13. Neon's nearest keys from `neon.theme.json`.)*

    - The **`OWNED` badge** is drawn `rgba(45,255,158,0.16)`; Neon's nearest key is
      `color.playerTwoTint` at `rgba(45,255,158,0.12)` — four points of alpha apart, and a
      player token rather than a badge one.
    - The **active row's ring** is drawn `0 0 0 2px #4fc3ff` with glow
      `rgba(79,195,255,0.30)`; `#4fc3ff` is Neon's `color.boardLine`, and its nearest glow
      `color.boardLineGlow` is `rgba(79,195,255,0.90)`.
    - The **price button** is drawn at **radius 11**, which is absent from Neon's radius
      set — `{3, 9, 10, 12, 13, 14, 20, 999}`.
    - **Badge tags** are drawn at 9.5pt with 0.1em tracking; `type.scale.chipLabel` is 9
      with 0.1.

    And these, for which Requirement 15's inventory names no slot at all:

    - The **theme-row surface** — its fill, radius and padding. This is a different surface
      from the open-game row Requirement 15 already covers for
      `P4-02-open-games-list.md`, and is drawn differently.
    - The **locked row's preview tile at 45% opacity**
      (`themes.catalog.json` → `ownershipStates.locked.rowTreatment`).
    - The **behind-menu dim at 35%**, which is distinct from the scrim drawn over it: Neon
      has `color.scrim` at 0.62 and `color.scrimHeavy` at 0.72, and neither is this value.
    - The **sheet header's type** — a 20/600 title over 11.5pt sub-copy. Neither size is in
      `type.scale`, whose nearest entries are `subhead` 22/600 and `caption` 11.

    **The settings card's own radius is a near-miss of the same kind**, and the clearest
    illustration of why this list exists: three of that card's four drawn values resolve
    cleanly to Neon keys and the fourth does not, so an implementer gets the fill and the
    border right and the corner wrong, with nothing failing.
    *(`design_handoff_game_ui/README.md` → 2b — "The four toggles live in one grouped card:
    `#1e2131`, radius 16, padding `6/16`, `0 0 0 1px #2b2f42`"; `neon.theme.json` →
    `radius`, `color`; consumed by `P4-04-settings.md` reqs 6 and 16, and provisioned as
    the settings-card slot in Requirement 15.)*

    - The card is drawn at **radius 16**, absent from Neon's radius set —
      `{3, 9, 10, 12, 13, 14, 20, 999}`. The plausible wrong answers are its two nearest
      keys, `radius.buttonLarge` at 14 and `radius.modal` at 20. Its fill `#1e2131` and its
      border `#2b2f42` *do* resolve, to `color.surfaceRaised` and `color.hairline`.

    **The settings surface's purchases section adds three more, on the same terms** —
    values a screen is required to read from the theme, with no Neon definition and, until
    now, nothing recording them as missing. This is the sharper form of the same trap,
    because **no approved screen draws this section at all**: handoff `2b` predates the
    Decision that put it there, so an implementer has neither a Neon key nor a drawing to
    work from, and every nearby key belongs to a different surface.
    *(`Menus and UI.md` → Decisions → Where the open-game slot unlock is sold; consumed by
    `P4-04-settings.md` reqs 20 and 22, under its req 16, which forbids hardcoding styling
    on that surface.)*

    - The **section grouping** that separates the purchases items from the three toggle
      rows inside the same settings card. Neon's nearest keys — `color.surfaceRaised` and
      `color.hairline` — describe the card itself, not a division within it.
    - The **price row** — product name, price display, and the affordance that initiates
      the purchase. The only price affordance drawn anywhere is the theme overlay's locked
      row (`themes.catalog.json` → `ownershipStates.locked.buttonStyle`: accent outline 2px
      `#9184d9`, radius 11) — a different surface selling a different product.
    - The **restore control**. The only restore control drawn anywhere is the theme
      overlay's footer link on `2a` — 11.5pt `#595d6c`, a size absent from `type.scale` and
      a color equal to `color.textFaint` — and that is again a different surface.

    **A judgment this PRD makes rather than assumes: the settings price row is a *distinct*
    slot from the theme overlay's price action, not the same slot reused.** The two sit in
    different containers (a row inside a grouped full-screen card versus a control inside a
    bottom-sheet list row), sell different products (open-game slots versus a theme), and
    only one of them carries a padlock and a dimmed preview tile beside it. The asymmetry
    settles it: if the two should look identical, a theme can author both slots to the same
    values — but if they are collapsed into one slot and should differ, no theme can pull
    them apart. This is a PRD-author call, not a decision in any design doc; it is
    reversible, and it deserves a sentence in `Theming.md` either way.

    As with the rest of this requirement, these are recorded as gaps between the inventory
    and the approved asset. **Closing them is not this PRD's to invent** — see Open
    Questions.
14. Neon's UUID is `b7c1f0a6-2f5e-4d3a-9c88-0f5a1e2d3c40`, and Neon is both the base theme
    and the default active theme — what a player sees before they have ever opened theme
    selection.
    *(`neon.theme.json` → `id`; `design_handoff_game_ui/themes.catalog.json` →
    `baseThemeId`, `defaultThemeId`; `Menus and UI.md` → Decisions → Which theme is active
    by default?)*

### The slot inventory

15. **The theme object carries every slot below.** This is an enumeration, not an
    illustration: each entry is a value some screen in this project is required to read
    from the theme, and a theme layer missing any one of them forces the consuming PRD to
    hardcode it. The list is **not closed** — the governing rule is that *"the theme's slot
    list is derived from what the screens actually consume,"* so a new screen adds slots —
    but nothing on this list is optional.
    *(`Theming.md` → Architectural Rule, as rewritten; → What a Theme Controls → Visual,
    Audio, Animation; → Decisions → What the theme's slots are derived from. Per-slot
    consumers cited inline.)*
    **Testable:** every concrete value quoted in a consumer PRD resolves to a slot named
    here; no consumer PRD needs a value this inventory cannot supply.

    **Board and geometry**
    - Page/board background, **gradient-capable** — the main menu's ground is a radial
      gradient, so one flat color is not sufficient.
      *(`Theming.md` → "Page background — gradient-capable"; `P4-01-main-menu.md` req 13)*
    - Big-board and small-board grid lines — color, thickness, style, **and the drawn
      line's opacity and glow**. *(`P3-01-board-rendering.md` reqs 5–7)*
    - **Board geometry:** outer gap, quadrant padding, inner gap, grid-line width,
      grid-line inset. *(`Theming.md` → "Board geometry and sizing";
      `P3-01-board-rendering.md` reqs 3, 5, 28; `neon.theme.json` → `board`)*
    - Quadrant fill, quadrant border and its open-state variant, and the forced-ring and
      last-move-ring treatments. *(`P3-01-board-rendering.md` reqs 6, 8, 9, 19)*
    - **Veil opacities as individually addressable values** — locked, claimed, cat-game.
      The locked veil is deliberately weaker than the other two, so one shared opacity will
      not do. *(`Theming.md` → "Opacities — the locked, claimed and cat-game veils";
      `P3-01-board-rendering.md` reqs 10–13)*
    - **Corner radii:** cell, quadrant, chip, control, button, buttonLarge, modal, pill.
      *(`Theming.md` → "Corner radii"; `P3-01-board-rendering.md` req 28;
      `P3-04-game-over-rematch.md` req 13; `P4-01-main-menu.md` req 13; `neon.theme.json` →
      `radius`)*

    **Marks**
    - The player marks themselves (Requirement 16).
    - **Mark sizes**, separately per context: the in-cell mark, the claimed-quadrant P1
      mark, the claimed-quadrant P2 mark and the cat-game glyph — four distinct sizes, not
      one. *(`Theming.md` → "Board geometry and sizing — … mark sizes";
      `P3-01-board-rendering.md` reqs 11, 12, 16; `neon.theme.json` → `type.scale.mark`,
      `markClaimX`, `markClaimO`, `markCat`)*
    - The claimed-mark and cat-mark **glows**. *(`P3-01-board-rendering.md` reqs 11, 12;
      named as a Neon gap in `Theming.md` → Open Questions)*
    - The cat-game **`CAT` caption's type and color**.
      *(`P3-01-board-rendering.md` req 12)*

    **The three highlights** — separately addressable per Requirement 20: last-move,
    active-quadrant (both its forced and its open treatment), locked/inactive, and the
    pending-move preview's **two** halves, the selected cell and the destination quadrant.
    Claimed-quadrant and cat-game quadrant styling likewise.
    *(`Theming.md` → What a Theme Controls → Visual; `P3-01-board-rendering.md` reqs 19,
    21, 23, 29)*

    **Surfaces and chrome**
    - **Modal surface** — card fill, border, radius, and a **winner-colored border**
      variant. This also carries Requirement 27's own failure modal.
      *(`Theming.md` → "Modals — winner, draw"; `P3-04-game-over-rematch.md` reqs 10, 13)*
    - **Sheet surface** — used by the theme-select overlay, the in-game quick-actions sheet
      and the name prompt, including its **header and close control**.
      *(`Theming.md` → "Sheets — theme select, in-game quick actions";
      `P4-03-theme-selection.md` reqs 1, 3; `P4-04-settings.md` req 3;
      `P4-02-open-games-list.md` req 8)*
    - **Scrim** — the approved screens draw four distinct scrim values, so this is a set of
      addressable values rather than one constant.
      *(`P3-04-game-over-rematch.md` req 13; `P4-03-theme-selection.md` req 1;
      `P4-02-open-games-list.md` req 18)*
    - **Settings card** — card fill, border and radius, the toggle row, its sub-label, and
      the switch's **track and knob in both on and off states**. Neon has no value for the
      drawn radius — see Requirement 13.
      *(`Theming.md` → "The settings card"; `P4-04-settings.md` reqs 6, 16)*
    - **The settings surface's purchases section** — three further slots, because the
      Settings screen now carries more than the three toggles:
      - a **section grouping** that separates the purchases items from the toggle rows
        inside the same card;
      - a **price row** — the product's name, its price display, and the affordance that
        initiates the purchase;
      - a **restore control** — a text link or secondary action, **visually distinct from
        both the toggle rows and the price row**.

      Neon holds no value for any of the three and no approved screen draws them — see
      Requirement 13, which also records this PRD's call that the price row is a distinct
      slot from the theme overlay's price action rather than the same slot reused.
      *(`Menus and UI.md` → Decisions → Where the open-game slot unlock is sold — "The
      Settings screen gains a purchases section holding the $4.99 open-game-slot unlock and
      a global **Restore purchases** control"; `P4-04-settings.md` reqs 20 and 22, under
      its req 16, which forbids hardcoding styling on that surface.)*
    - **Open-game rows and their chips** — row fill, row title type, the three score chips
      including their active and inactive states, and the chevron.
      *(`Theming.md` → "Open-game rows and their chips"; `P4-02-open-games-list.md` reqs 4,
      17, 18)*
    - **Badges** — `FREE`, `OWNED`, `ACTIVE`, and the price action's treatment. The badge
      *styling* is a theme slot; which badge a row gets is entitlement state and is not
      (Requirement 31). Neon holds no value for any of them — see Requirement 13.
      *(`Theming.md` → "Badges"; `P4-03-theme-selection.md` reqs 8, 10, 13)*
    - **Turn indicator and scoreboard styling**, including the active player's tinted chip.
      *(`Theming.md` → What a Theme Controls → Visual;
      `P3-03-scoreboard-turn-indicator.md`)*
    - **Main menu styling** — background, title/wordmark/kicker treatment, and a **logo
      slot**. *(`Theming.md` → "Main menu styling", "The main-menu logo";
      `P4-01-main-menu.md` reqs 7, 8, 10, 13)*
    - **Two button tiers, not one** — a large primary (Play Game, Theme) and a secondary
      (Settings), plus the prompt's primary/secondary pair. A single "button look" slot is
      satisfied by one style and would force the second to be hardcoded.
      *(`P4-01-main-menu.md` reqs 4, 6; `P4-02-open-games-list.md` req 12)*
    - **Text input field** — fill, radius, focused border, caret and counter, for the
      opponent-name prompt. *(`P4-02-open-games-list.md` reqs 8, 9, 17)*
    - **Destructive-action styling** for deleting an open game.
      *(`P4-02-open-games-list.md` req 7)*
    - **Legend and hint typography and their text colors** — three distinct text colors are
      drawn. *(`P3-05-how-to-play.md` reqs 17, 18, whose own open question names this gap)*

    **Type**
    - **The type scale** — display, title, heading, subhead, body, label, caption,
      chipLabel and chipValue, each with size and weight, and where drawn tracking and
      line-height. This is a different axis from Requirement 19's typeface: a theme that
      picks a font has not thereby picked sizes.
      *(`Theming.md` → "The type scale — sizes and weights, distinct from a theme's choice
      of font"; `neon.theme.json` → `type.scale`)*

    **Audio** — Requirement 17. **Animation** — Requirement 18.

16. **Marks are asset slots on the theme, not shapes drawn in board code** — a theme
    supplies its mark art as an **image or an icon**, and marks are not locked to X and O.
    The slot must also carry what Neon's approved definition actually authors: a `kind`, a
    `value`, and a **per-mark font and weight** distinct from the theme's `type.family`.
    Neon's ✕, ○ and Ø are Neon's choice of art, not a constraint on the system.
    *(`Tech Design.md` → Decisions → Marks — image or icon, supplied by the theme;
    `Theming.md` → Decisions → Marks beyond X and O; `neon.theme.json` → `marks`, which
    authors `{"kind": "glyph", "value": "✕", "font": "Inter", "weight": 600}`;
    `P3-01-board-rendering.md` req 17)*
    The docs name two kinds and Neon authors a third — see Open Questions.
17. **The theme object carries audio slots for the five moments the game makes a sound** —
    placing a mark, winning a small board / claiming a quadrant, cat game, winning the
    whole game, and button taps / menu navigation — plus **two further keys in the same map
    that are not playable moments**:
    - **`music`**, a background-music slot that is part of the shape but **unused in this
      version**. One-shot sound effects only, and the audio structure must not make adding
      a music layer painful later.
    - **`signature`**, which is **descriptive metadata naming the theme's sonic character —
      Neon's value is the word `"buzz"` — never an asset and never played.**

    Seven keys, five of them playable. The distinction is part of the slot definition, not
    an implementation detail downstream: a consumer must not treat this map as an iterable
    list of sounds.
    *(`Theming.md` → What a Theme Controls → Audio, which lists exactly those five moments
    plus background music; → Sound Decisions → One-shot sound effects only, for now; →
    Theme Catalog → Theme 1 — Neon → Signature sound; `neon.theme.json` → `sound`, whose
    `signature` is `"buzz"` and whose `music` is `null`. Consumed by `P2-02-audio.md`
    reqs 6, 7, 14 and 15 — its req 7 is the one that forbids implementing the audio layer
    by iterating `sound.*`.)*
18. The theme object carries **animation** slots, and each animation carries **its own
    duration** — speed is specified in the animation, not globally, so a theme controls
    its own pacing. The animated moments named are placing a marker, claiming a quadrant,
    cat game, winning the game, and the active-quadrant and last-move highlights.
    *(`Animations.md` → Decisions → Duration lives in the animation; Where Animations
    Fire; `neon.theme.json` → `animation`; consumed by `P2-04-animations.md`)*
19. **A theme supplies its own font**, and the theme object needs somewhere to put one.
    Inter 400/500/600 is bundled as **Neon's font choice, not an app-wide font constant** —
    a font is a themeable value like any other. This is what keeps Requirement 25 whole:
    fonts are named in the slot inventory, so an app-wide font constant would be an
    exception carved into the rule rather than a value the theme owns.
    *(`Theming.md` → Decisions → Does a theme supply its own font; `Tech Design.md` →
    Decisions → Do themes pick their own font?; `design_handoff_game_ui/README.md` →
    Assets → Fonts)*
20. The last-move highlight, the active-quadrant highlight and the pending-move preview
    are **separately addressable slots**, because all three can be on screen at once and
    must be visually distinguishable.
    *(`Game Board Design.md` → Three highlights on screen at once; The Two Highlights
    Together; `design_handoff_game_ui/README.md` → Cell states;
    `P3-01-board-rendering.md` req 29)*
21. The schema must let a theme distinguish things by **more than colour** — shape, icon,
    outline, pattern — because whether anything is distinguished by colour alone is
    "handled per theme," not a system-wide rule.
    *(`Theming.md` → Decisions → Is anything distinguished by colour alone?)*

### Runtime integration

22. Use Flutter's **`ThemeData` / `ThemeExtension` as far as possible**, filled out from
    the theme file. The parts Flutter's theming does not support are implemented
    ourselves.
    *(`Tech Design.md` → Decisions → Flutter's ThemeData vs our own theme object)*
23. **Sounds and animations live in the same theme object**, not a parallel structure —
    Flutter gets what it can take, we handle the rest, all fed from the same file.
    *(`Tech Design.md` → Decisions → Flutter's ThemeData vs our own theme object)*
24. The active theme is exposed through **Riverpod** (plain `Notifier`/`NotifierProvider`,
    no `@riverpod` codegen), and must be readable from **everywhere**, including deep in
    the board widget tree.
    *(`Tech Design.md` → Decisions → State management — Riverpod)*
25. **Architectural Rule.** No hardcoded values anywhere in the code, **across the full
    slot inventory of Requirement 15** — not only colors, backgrounds, fonts, piece styles,
    sounds and animations, but board geometry and sizing, corner radii, the type scale,
    opacities, and every surface: modals, sheets, the settings card and its purchases
    section, open-game rows and their chips, badges, the main-menu logo, and a
    gradient-capable page background. Every visual, audio and motion value is read from the
    currently selected theme: if something on screen has a color, that color came from the
    theme; if something makes a noise, that sound came from the theme; if something moves,
    that motion came from the theme. No exceptions.
    *(`Theming.md` → Architectural Rule, as rewritten; → Decisions → What the theme's slots
    are derived from; `Tech Design.md` → Decisions → Do we add a test that fails on
    hardcoded theme values?, whose scope is *"the slot inventory the Architectural Rule
    names"* and whose pattern table is explicitly *"not a complete enumeration of that slot
    inventory"*.)*
    The guard is `P1-05-theme-guard-test.md`; this requirement is the rule it enforces, so
    narrowing it here would narrow the guard. Note its limit, recorded in Requirement 13:
    the guard catches a value written into code, not a value read from the wrong slot.
26. **Adding a new theme requires zero changes to game, board or menu code** — only adding
    a new theme definition.
    *(`Theming.md` → Architectural Rule)*

### Failure behavior

27. If a theme fails to load, show a **modal on the Theme screen** saying the theme is
    unavailable and asking the player to pick another, **then fall back to Neon**.
    *(`Theming.md` → Decisions → What happens if a theme fails to load; restated in
    `themes.catalog.json` → `failureBehavior`; the screen half is
    `P4-03-theme-selection.md` reqs 20–21)*
28. Neon is the one theme with nothing to fall back to.
    *(`Theming.md` → Decisions → What happens if a theme fails to load; Why this matters
    for the build)*

### Boundaries of the theme object

29. **Haptics are not theme-driven.** Vibration lives at the application setting level; a
    theme cannot define or change the buzz. The theme object has no haptics slot.
    *(`Theming.md` → What a Theme Does NOT Control; relied on by `P2-03-haptics.md` and
    `P4-04-settings.md` req 14)*
30. The sound-effects, animations and vibrate **toggles are global player settings, not
    theme properties** — a theme cannot override them, and they mute or disable a channel
    for every theme. No key in a theme file sets, forces or reads any of the three.
    *(`Theming.md` → Sound Decisions → Global mute; `Animations.md` → Decisions → Turn
    animations off — a global setting; `Menus and UI.md` → Settings Menu;
    `P4-04-settings.md` req 11)*
31. **Ownership / entitlement is not part of a theme definition.** A theme is an
    audio-visual package; purchase state is account/device state and lives outside the
    theme object. This holds now that some themes are paid — a theme file still describes
    a theme; what a player owns lives elsewhere. No shipped theme YAML contains an
    ownership or price key. The same line holds for the purchases section Requirement 15
    provisions: the theme supplies that section's styling, never the product, its price, or
    whether it is owned.
    *(`design_handoff_game_ui/themes.catalog.json` → `note`;
    `design_handoff_game_ui/README.md` → 2a → The four themes shown;
    `P1-07-entitlements.md` req 5; `P4-03-theme-selection.md` req 12)*

### The catalog, and reading a non-active theme

32. **The app has a theme catalog — an enumeration of the installed themes that the UI
    reads to know what exists.** Adding a theme definition must add it to the catalog, and
    therefore add a row to the selection list, with **no change to menu code and no edit to
    a hand-maintained list of UUIDs in Dart**. A hardcoded Dart list of themes satisfies
    neither Requirement 26 nor `P4-03-theme-selection.md` req 4, whose stated test is that
    a third theme definition produces a third row with no edit under the menu UI source.
    *(`Theming.md` → Architectural Rule — "Adding a new theme should require zero changes
    to game/board/menu code — only adding a new theme definition";
    `P4-03-theme-selection.md` reqs 4, 5)*
    **Testable:** dropping a valid theme YAML into `assets/themes/` and rebuilding makes it
    appear in the catalog with no source file edited outside the theme layer.
    How themes are *discovered*, and what a catalog entry holds, are open questions below.
33. **A non-active theme's values must be readable without making it active.** The
    selection list renders each row's preview tile *"in that theme's own colors and
    marks"*, and that is the one place in the app that reads a theme other than the active
    one. Requirement 24's provider exposes the active theme only, so this requires a
    second, explicit read path.
    *(`P4-03-theme-selection.md` reqs 6, 7 — "The preview tile is the one place in the app
    that reads a non-active theme's values. Rendering a row must not require making that
    theme active"; `design_handoff_game_ui/README.md` → 2a)*
    What this costs at startup depends on the unresolved materialization-scope question
    below.
34. **A theme that fails to load must not take the app down with it.** Requirements 27–28
    give the player-facing behavior; this requires the failure be *reportable* — the loader
    surfaces which theme failed, so the selection overlay can name it and fall back.
    *(`Theming.md` → Decisions → What happens if a theme fails to load;
    `P4-03-theme-selection.md` reqs 20–21, which consume the report)*
    What counts as a failure is an open question below.

## Out of Scope

- **The hardcoded-theme-value enforcement test.** Requirement 25 states the rule; the test
  that checks it, its banned-pattern list and its zero baseline are
  `P1-05-theme-guard-test.md`.
- **Persisting the selected theme UUID** to device storage via `shared_preferences` —
  `P1-04-persistence.md`. This PRD only fixes that the identity persisted is the UUID
  (Requirement 4).
- **The theme selection overlay UI** — the sheet, the rows, the preview tiles, the active
  highlight, the free/paid labelling, and the failed-to-load modal's layout:
  `P4-03-theme-selection.md`. Note also that the theme **cannot be changed mid-game**
  (`Theming.md` → Decisions → Can you change the theme mid-game).
- **The entitlement model** — the `free` / `owned` / `locked` states, the free-tier
  defaults and the per-theme query: `P1-07-entitlements.md`. **Buying and restoring:**
  `P4-05-purchase-flow.md`. Themes beyond the two free ones are paid (`Theming.md` →
  Decisions → Which themes are free; `Tech Design.md` → Decisions → In-app purchases), and
  none of it reaches the theme object — Requirement 31.
- **The settings surface's purchases section itself** — the section, its two controls, the
  parental gate that precedes a purchase, and what activating either control invokes:
  `P4-04-settings.md` reqs 20–22 and `P4-05-purchase-flow.md`. This PRD supplies only the
  slots that section is drawn from.
- **The Classic Red vs Blue theme content** — its YAML file and the concrete list of values
  it overrides: `P5-01-classic-theme.md`. Two themes ship at launch (`Theming.md` →
  Decisions → How many themes ship at launch), but only Neon is authored here.
- **Audio playback** — loading and firing the sound assets and the `audioplayers`
  integration: `P2-02-audio.md`. This PRD defines only the slots.
- **Animation playback** — running the animations, one-at-a-time sequencing, non-blocking
  input, and the animations-off instant-state-change path: `P2-04-animations.md`. This PRD
  defines only the slots and that each carries its own duration.
- **Every screen that consumes these slots** — the board (`P3-01-board-rendering.md`), the
  scoreboard (`P3-03-scoreboard-turn-indicator.md`), game over
  (`P3-04-game-over-rematch.md`), the legend and hints (`P3-05-how-to-play.md`), the main
  menu (`P4-01-main-menu.md`), the open-games list (`P4-02-open-games-list.md`) and
  settings (`P4-04-settings.md`). This PRD supplies the slots those read; it draws nothing.
- **Producing sound and art assets.** Assets are generated with Replicate when actually
  needed, not now: `P5-02-asset-generation-replicate.md`.
  *(`Tech Design.md` → Decisions → Where do sound and art assets come from?)*

## Open Questions

### From the design docs, worded as the docs word them

*(`Tech Design.md` → Open Questions → 2. Theme loading — all three sit directly on this
feature and are **not** resolved here.)*

- Are all themes loaded and materialized at startup, or only the selected one, on demand?
  `Theming.md` → Why this matters for the build says materialization happens "at startup"
  but does not say for how many themes. *(Requirement 33 sharpens this rather than settling
  it: the preview tiles need every listed theme's values, not just the active one's.)*
- Are the theme YAML files declared as assets in `pubspec.yaml`? *(`P1-01-app-scaffold.md`
  records the same question from the other side — whether that declaration is its file's or
  this one's. It is also entangled with how the catalog discovers themes, below.)*
- What happens to an unknown or misspelled *key* inside an otherwise-valid theme file?
  Merge-over-Neon will quietly fill the gap with Neon's value, so a typo in a theme file
  fails silently. The hardcoded-theme-value test guards code that bypasses the theme; it
  does not guard a theme file that misspells a key.

*(`Theming.md` → Open Questions — three of its four land on this PRD.)*

- What is the exact slot schema — the key structure — for what a theme defines? The
  approved `neon.theme.json` does not currently cover the pending-move highlight, any modal
  or sheet surface, a gradient background, a logo, or a theme's own display name and
  description. *(Requirement 15 enumerates **which** slots exist; this asks what their keys
  look like. Different questions — only the first is answered here.)*
- Neon is required to be complete (see **Neon Is the Base Theme**), but the approved
  `neon.theme.json` has no pending-move highlight values at all — no pending colour, no
  pending cell ring, no destination ring — while the board's pending preview is a required,
  separately addressable treatment. The same gap covers the grid-line opacity and glow, the
  claimed and cat-game mark glows, and the cat-game caption style. How does this gap get
  closed? *(This is what Requirement 13 refuses to invent, and Requirement 13 extends the
  same gap to the theme-selection overlay's badge, row, dim and header values, to the
  settings card's drawn radius, and to the settings surface's purchases section. The values
  are drawn in `design_handoff_game_ui/README.md` → Cell states, screen 2a, screen 2b and
  screen 2d but are absent from the machine-readable file — and the purchases section is
  drawn nowhere at all — so whether transcribing them counts as authoring Neon or as
  editing an approved read-only asset needs a call.)*
- What form does the legibility contract take — a contrast floor, a review step, something
  else? **What a Theme Controls** requires every theme to keep the last-move and
  active-quadrant highlights legible, but this is unfalsifiable as written: Classic Red vs
  Blue has a near-white ground while inheriting Neon's near-white text and its veils and
  glows tuned for a near-black ground, so a theme could be complete, pass every stated
  check, and still be unreadable.

Also open, from `Theming.md` → Open Questions (owned by `P5-01-classic-theme.md`, listed
here because it is the first real test of Requirement 9):

- Which values, concretely, does Classic Red vs Blue override?

### Contradiction between docs — flagged, not resolved

- **How many themes the selection list shows.** `design_handoff_game_ui/README.md` →
  *2a — Theme Select* and `themes.catalog.json` show **four** themes — Neon, Classic Red
  vs Blue, Splat and Dinosaurs — and header the sheet *"Two free, two extra"*, while
  `Theming.md` → Decisions → How many themes ship at launch says **two**, and
  `Menus and UI.md` → Theme Selection lists exactly those two. The handoff itself marks
  Splat and Dinosaurs as placeholders that "do not exist" and must not ship as designed, so
  this may be a mock artifact rather than a real disagreement — but the two documents still
  describe different screens. `P4-03-theme-selection.md` → Open Question 1 carries it; it
  touches Requirement 32 only in that the catalog must not care how many there are.

  The free-vs-paid half is **settled and no longer contested**: `Theming.md` → Decisions →
  Are themes unlockable/rewards now says some themes are paid, which agrees with the
  handoff's `free` / `owned` / `locked` states and its price button. Requirement 31 is
  stated by both sides and stands unchanged.
- **The mark slot has two kinds in the docs and three in Neon.** `Theming.md` → Decisions →
  Marks beyond X and O and `Tech Design.md` → Decisions → Marks say **an image or an
  icon**; `neon.theme.json` → `marks` authors `"kind": "glyph"` with a text `value`, a
  per-mark `font` and a `weight` — a text glyph in a bundled font, which is neither an
  image file nor an `IconData`. Requirement 16 requires the slot carry what Neon actually
  authors, but whether `glyph` is a third supported kind or a shorthand for "icon" is
  stated nowhere, and it changes the schema.

### Needs a decision — raised by this PRD or by a consumer, not settled in any doc

Each is a place an implementer would otherwise guess.

- **How are themes discovered, and what does a catalog entry hold?** Requirement 32
  requires a catalog and forbids a hand-maintained Dart list; it does not choose between an
  asset-manifest scan, a committed index file, or per-theme `pubspec.yaml` declarations —
  which is entangled with the `pubspec.yaml` question above. Related and equally unstated:
  **does a theme carry its own display name and blurb?** The selection row needs a name and
  a one-line description per theme (`P4-03-theme-selection.md` req 6); today those exist
  only in `themes.catalog.json`, a handoff reference asset that ships nowhere, and
  `Theming.md` → Open Questions notes the schema has no place for them.
- **What counts as "fails to load"?** Requirements 27 and 34 give the behavior but not the
  trigger. Missing file, malformed YAML, missing or duplicate UUID, an unparseable value,
  and a referenced asset that is absent are five different failures, and only some are
  detectable at startup.
- **What happens if *Neon* fails to load?** The docs say Neon is the theme with nothing to
  fall back to, which states the constraint but not the behavior. Hard failure at startup?
  A built-in minimal fallback?
- **Merge depth and null semantics.** Requirement 8 says "merge" without saying whether it
  is shallow — a theme naming `color` replaces that whole section — or deep, per key; and
  without saying what an explicit null means: inherit Neon's, or "deliberately nothing."
  `neon.theme.json` → `sound.music: null` makes the second concrete today, and the
  shallow-vs-deep choice decides whether a theme overriding one color loses the other
  forty.
- **Which of the three lookup paths a widget uses for a given value.** Requirements 22–24
  create three: `ThemeData` via `Theme.of(context)`, a `ThemeExtension` via the same, and
  the Riverpod-exposed theme object. *"As far as possible"* is the only guidance on the
  split, nothing enumerates which slots Flutter's own theming can carry, and
  `P1-05-theme-guard-test.md` has to recognize all three as legitimate reads.
- **What goes in Neon's five `"TODO"` sound slots.** `neon.theme.json` → `sound` carries
  `"TODO: neon buzz one-shot"` and four bare `"TODO"`s. Neon's completeness is **this
  PRD's** to hold: Requirement 11 requires Neon define every slot, and `P2-02-audio.md`
  req 12 disowns it back here — it carries an *Owner of the behavior* line naming
  Requirements 11, 12 and 14, and records that the audio PRD *"authors no theme content and
  must not edit `assets/themes/`."* But the assets are explicitly deferred (`Tech
  Design.md` → Decisions → Where do sound and art assets come from?), and that PRD builds
  against the placeholders as *"named but unloadable, never absent"* (its req 17). Whether
  Neon ships with silent placeholder audio files, keeps the prose TODOs, or is blocked on
  `P5-02-asset-generation-replicate.md` is unstated.
- **Is there a sound slot for a whole-game draw?** `P2-02-audio.md` → Open Questions raises
  it against this inventory: `catGame` is a small-board draw and `winGame` names a winner,
  while a straight draw is a distinct outcome with its own drawn screen (*1h — Modal:
  draw*) and no slot named for it. Reuse one, add a slot, or stay silent — all three are
  guesses today.
- **Is screen padding a theme value?** The handoff commits per-screen padding (`96 / 28 /
  52` on the menu, 16pt sides on board screens, safe-area tops of 62 / 64 / 96).
  `Theming.md`'s inventory names board geometry and radii but not screen padding, so it is
  unclear whether these are theme slots or layout constants — and Requirement 25 makes the
  distinction load-bearing rather than cosmetic.
- **Are chrome icons theme values or app assets?** `design_handoff_game_ui/README.md` →
  Assets names the Phosphor set (chevron-left, chevron-right, plus, x,
  sliders-horizontal) for navigation and control chrome. Mark art is unambiguously
  theme-supplied (Requirement 16), but nothing says whether a theme may replace the chevron
  or the close icon, and `Tech Design.md`'s guard table bans `Icons.*` only *"inside board
  widgets"*.
- **JSON reference vs YAML runtime format.** The approved Neon definition is
  `neon.theme.json` and the handoff says "load it as the base theme," while `Tech
  Design.md` settles the shipped theme-file format as **YAML**. This PRD reads that as:
  ship Neon as YAML transcribed faithfully from `neon.theme.json`, which stays the
  read-only source of truth for the values. If the intent was instead to load the JSON
  directly, that is a decision that needs stating.
- **CSS-shaped values in `neon.theme.json`.** Several `board` values are CSS shadow
  strings (`"0 0 0 1.5px rgba(...), 0 0 14px rgba(...)"`) and colors appear as `rgba()`
  strings. Flutter has no direct equivalent, so the YAML schema has to decide how these
  are represented — structured fields, or parsed strings. Requirement 12 fixes the values,
  not their encoding.
