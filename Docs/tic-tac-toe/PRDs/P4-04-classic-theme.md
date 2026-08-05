# PRD: Classic Red vs Blue (the second theme)

> **Status:** Draft · Source docs read: `Theming.md`, `Animations.md`, `Tech Design.md`,
> `Menus and UI.md`, `roadmap.md`, and the read-only reference asset
> `design_handoff_game_ui/` (`README.md`, `neon.theme.json`, `themes.catalog.json`).
> `Alternative Game Styles.md` is a declared parking-lot doc and was not used as a source.

**Wave:** P4 · **File:** `P4-04-classic-theme.md`

**Depends on:**

- `P1-03-theme-system.md` — the theme object, UUID identity, YAML loading, and
  merge-over-Neon materialization, plus the complete Neon base this theme overrides. This
  PRD authors a theme *file*; it defines none of the mechanism.
- `P4-01-audio.md` — plays whatever sound slot this theme names.
- `P4-03-animations.md` — runs the animation set this theme inherits.
- `P5-01-asset-generation-replicate.md` — produces the splat sound file and any art this
  theme needs.

**Depended on by:** `P3-03-theme-selection.md` lists this theme and renders its preview
tile; until this PRD is built, the Classic row has a name and a UUID but no authored
overrides. `P4-05-in-app-purchases.md` builds the paid themes, which are authored as
partial overrides in the same shape as this one.

---

## Problem

Two themes ship free — Neon and Classic Red vs Blue (`Theming.md` → Decisions → Which
themes are free) — but only Neon is authored. A player who opens theme selection today can
pick Classic and get Neon, because the file behind it does not exist.

The deeper problem is that the whole theme architecture is unproven. `Theming.md` →
Architectural Rule is a day-one constraint on every file, justified by the claim that
"adding a new theme should require zero changes to game/board/menu code — only adding a
new theme definition." Nothing has tested that claim. Neon is the base and can never
exercise inheritance; a second theme that is *genuinely different* — "one is loud and
electric, the other is clean and classic" — is, in the doc's own words, "a real test that
nothing is hardcoded" (`Theming.md` → Theme Catalog → Theme 2).

## Goal

Classic Red vs Blue exists as a real, selectable, complete theme authored as a **small
partial override over Neon** — the plain familiar look, red player vs blue player, no
neon, no black background, with a splat where Neon buzzes — and everything else inherited.
When it is done, the app has demonstrated the claim `Theming.md` makes about the whole
system: that a theme can be as small as "black → white, neon green → red" and still be a
complete, working theme, and that switching to a visually unrelated theme requires no
change to game, board or menu code.

## Requirements

1. **Classic Red vs Blue ships as the second of the two launch themes.**
   *(`Theming.md` → Decisions → How many themes ship at launch; `Menus and UI.md` → Theme
   Selection)*

2. **It is authored as a partial override, not a full theme.** Classic defines only what it
   wants to be different and inherits the rest from Neon; it is materialized into a
   complete theme by merging its overrides over Neon.
   *(`Theming.md` → Neon Is the Base Theme → How it works; `Tech Design.md` → Decisions →
   Fallback to Neon — merge, not resolve)*
   *Testable:* the authored file contains an override set materially smaller than
   `neon.theme.json`, and the materialized theme has no unset value.

3. **What it overrides is the graphics — the art and colors.** Red player, blue player, no
   black background; no neon.
   *(`Theming.md` → Theme Catalog → Theme 2 → What it overrides)*

4. **Its signature sound is a splat** — like a water balloon popping, wet and playful,
   deliberately nothing like Neon's electric buzz. Classic and Neon have distinct sonic
   identities: Neon buzzes like a light, Classic splats like a water balloon.
   *(`Theming.md` → Theme Catalog → Theme 2 → Sound; corroborated by
   `design_handoff_game_ui/themes.catalog.json` → `signatureSound: "splat"`)*

5. **Everything else is inherited from Neon — animations included.** Classic authors no
   animations; it takes Neon's complete animation set by the same merge rule as every other
   value.
   *(`Theming.md` → Theme Catalog → Theme 2 → What it inherits from Neon; `Animations.md` →
   Animations Inherit From Neon, and Decisions → Do themes inherit Neon's animations?)*

6. **Classic inherits from Neon and from nothing else.** One level, no chains.
   *(`Theming.md` → Inheritance Depth; `themes.catalog.json` → `inheritanceDepth: 1`)*

7. **Classic's identity is a UUID carried in its own theme file**, and that UUID —
   `3d1a8b52-9c47-4b16-8f2e-7a5d0c9e1b34` — is what gets persisted and matched, never the
   name.
   *(`Tech Design.md` → Decisions → Theme identity — UUID;
   `design_handoff_game_ui/themes.catalog.json` → Classic's `id`)*

8. **The theme is a bundled YAML file** under `assets/themes/`, shipped with the app — not
   user-authored, not downloaded.
   *(`Tech Design.md` → Decisions → What format are theme files; Project structure —
   layer-first; `Theming.md` → Where Themes Live)*

9. **Every screen renders under Classic with no missing values.** This is the completeness
   proof, and it is the point of the feature: a theme "as small as *black → white, neon
   green → red*" must still be a complete, working theme.
   *(`Theming.md` → Neon Is the Base Theme → Why this matters for the build)*
   *Testable:* with Classic active, walk every screen the handoff draws — main menu, theme
   select, settings, open-games list, name prompt, board in free-choice, board in forced
   quadrant, board with a pending move, winner modal, draw modal — and none falls back to
   an undefined or null value.

10. **Authoring Classic requires zero changes to game, board or menu code.** Only a theme
    definition is added.
    *(`Theming.md` → Architectural Rule)*
    *Testable:* the diff that adds Classic touches the theme asset and its registration
    only — nothing under the board, menu or game layers.

11. **Classic and Neon must read as two genuinely different looks.** This is the check that
    nothing is hardcoded, not a stylistic preference: every surface Classic overrides
    renders differently under the two themes with no code change between them.
    *(`Theming.md` → Theme Catalog → Theme 2: "Two genuinely different looks, which is a
    real test that nothing is hardcoded")*

12. **Classic must keep the gameplay-critical highlights legible** — the last-move
    highlight and the active-quadrant highlight are gameplay-critical, not decoration. A
    theme that makes them hard to spot is a broken theme. Note that Neon gets this partly
    for free from high contrast against black; Classic does not, so it is the theme where
    this has to be checked deliberately.
    *(`Theming.md` → What a Theme Controls; Theme Catalog → Theme 1)*
    Classic *may* distinguish things by more than colour — shape, icon, outline, pattern —
    since that is "handled per theme"; it is not required to.
    *(`Theming.md` → Decisions → Is anything distinguished by colour alone?)*

13. **Classic ships free, and theme selection labels it as free.** Neon and Classic Red vs
    Blue are the two free themes; every theme beyond those two is paid, and the theme
    selection list labels which themes are free and which are paid. Classic is the boundary
    case — the last free theme, and the shape the first paid theme is copied from.
    *(`Theming.md` → Decisions → Which themes are free; Are themes unlockable/rewards)*
    *Testable:* Classic is selectable and applies with no purchase, entitlement or unlock
    step of any kind, and its row in theme selection carries the free label.

> **Recorded from `Theming.md` → Neon Is the Base Theme → Watch out for — stated, not a
> decision, and not a requirement above.** A partial theme inherits Neon's *personality*,
> not just its values. Classic Red vs Blue with Neon's electric buzz sounds and glow
> animations may feel mismatched — clean visuals with electric audio. That's a fine default
> (it works, nothing is missing), but Red vs Blue may want to override more than just
> colors to feel coherent. Worth checking once it's real; not a problem to solve now.

## Out of Scope

- **The theme mechanism** — the theme object and its slots, YAML loading, UUID identity,
  merge-over-Neon materialization, the complete Neon base, and the failed-to-load modal:
  `P1-03-theme-system.md`. This PRD consumes all of it and changes none of it.
- **Persisting the selection** — `P1-04-persistence.md`.
- **The theme selection UI** — the overlay, the rows, the preview tile, the ACTIVE
  treatment, and the rendering of the free/paid labels: `P3-03-theme-selection.md`.
  Requirement 13 fixes only that Classic is free and is labelled so.
- **Audio playback** — loading and firing sound assets, `audioplayers`, the global mute:
  `P4-01-audio.md`. This PRD names the splat; it does not play it.
- **The animation system** — running animations, one-at-a-time sequencing, non-blocking
  input, the animations-off instant path: `P4-03-animations.md`. Classic inherits Neon's
  set and authors none.
- **Paid themes, purchase and entitlement** — every theme beyond Neon and Classic is paid,
  and that work is `P4-05-in-app-purchases.md`: store integration, purchase and restore
  flows, entitlement state, and the locked/owned treatments. Nothing about Classic is gated
  by any of it. Note that Splat and Dinosaurs in `themes.catalog.json` remain explicitly
  placeholders that do not exist.
  *(`Theming.md` → Decisions → Are themes unlockable/rewards, Which themes are free;
  `design_handoff_game_ui/README.md` → The four themes shown)*
- **Generating the splat sound file and any art** — `P5-01-asset-generation-replicate.md`.
  Assets are generated with Replicate when actually needed and explicitly not now; the
  Classic splat is one of the assets that decision names.
  *(`Tech Design.md` → Decisions → Where do sound and art assets come from?;
  `design_handoff_game_ui/README.md` → Assets → Sounds: "none produced")*
- **Changing the theme mid-game.** Theme changes happen from the main menu only.
  *(`Theming.md` → Decisions → Can you change the theme mid-game)*

## Open Questions

### From `Theming.md` → Open Questions (its own standing question, worded as the doc words it)

- Which values, concretely, does Classic Red vs Blue override? (Settled in principle —
  graphics and its splat sound, inheriting the rest. An exact list will fall out when it's
  actually built.)

This is the central unresolved item and it is deliberately not answered here. No concrete
color values, hex codes or override list appear in this PRD, because the docs leave them to
build time.

### Raised by this PRD, not asked by the design docs (flags, clearly mine)

- **Are the catalog's `previewColors` Classic's real values, or swatch stand-ins?**
  `design_handoff_game_ui/themes.catalog.json` gives Classic
  `{ ground: "#f3f5fe", playerOne: "#d92d3f", playerTwo: "#2453c4" }` — the only concrete
  Classic colors anywhere — but marks the theme `"status": "preview-only — overrides not
  yet authored"`, and `README.md` → Still to design lists "the Classic Red vs Blue theme
  itself (only its two-color preview exists)". Whether authoring starts from those three
  values or replaces them is not stated.
- **Which sound slots does the splat fill?** `Theming.md` names one signature sound;
  `themes.catalog.json` says Classic inherits `"sound (except the splat)"`. Whether the
  splat replaces only the place-a-mark sound, or several of the five audio slots, is not
  written down.
- **Does Classic override the marks at all?** `themes.catalog.json` gives Classic the same
  `✕` / `○` marks as Neon, which would make "the art and colors" (Requirement 3) largely a
  color override in practice. `Theming.md` → Decisions → Marks beyond X and O allows a
  theme its own mark art but does not say Classic uses it.
