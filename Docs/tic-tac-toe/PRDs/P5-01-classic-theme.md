# PRD: Classic Red vs Blue (the second theme)

> **Status:** Draft · Source docs read: `Theming.md`, `Animations.md`, `Tech Design.md`,
> `Menus and UI.md`, `roadmap.md`, and the read-only reference asset
> `design_handoff_game_ui/` (`README.md`, `neon.theme.json`, `themes.catalog.json`).
> `Alternative Game Styles.md` is a declared parking-lot doc and was not used as a source.

**Wave:** P5 · **File:** `P5-01-classic-theme.md`

**Depends on:**

- `P1-03-theme-system.md` — the theme object, UUID identity, YAML loading, and
  merge-over-Neon materialization, plus the complete Neon base this theme overrides. This
  PRD authors a theme *file*; it defines none of the mechanism.
- `P2-02-audio.md` — plays whatever sound slot this theme names.
- `P2-04-animations.md` — runs the animation set this theme inherits.
- `P5-02-asset-generation-replicate.md` — produces the splat sound file and any art this
  theme needs. Same wave, so the two are sequenced by need rather than by wave.

**Ships after the screen that lists it.** `P4-03-theme-selection.md` is wave 4 and lists
this theme and renders its preview tile; until this PRD lands, the Classic row has a name
and a UUID but no authored overrides. That screen does not wait on this PRD — it tolerates
the unauthored row — which is why this work sits in a later wave rather than beside it.

**Related:** `P4-05-purchase-flow.md` sells the paid themes, which are authored as partial
overrides in the same shape as this one; `P1-07-entitlements.md` holds the ownership state
that labels them. Nothing about Classic is gated by either.

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

There is a second, sharper problem this PRD cannot solve on its own. Classic is the first
theme to invert Neon's ground: a light background under text, veils, scrims and glows that
were all tuned for `neon.theme.json`'s near-black `ground: "#161826"`. Merge-over-Neon
guarantees Classic will be *complete*. Nothing yet guarantees it will be *readable* — and
`Theming.md` now records that gap as an open question of its own.

## Goal

Classic Red vs Blue exists as a real, selectable theme authored as a **partial override
over Neon** — the plain familiar look, red player vs blue player, no neon, no black
background, with a splat where Neon buzzes — inheriting everything it does not name. When
it is done, the app has demonstrated the claim `Theming.md` makes about the whole system:
that switching to a visually unrelated theme requires no change to game, board or menu
code.

**Two success conditions, and they are not the same one.** `Theming.md` → Why this matters
for the build says a theme "as small as *black → white, neon green → red*" is a complete,
working theme, and that remains true of **completeness** — the merge leaves no value
unset. It is *not* a claim about **legibility**, and it predates the consumer-derived
surface inventory now in `Theming.md` → What a Theme Controls (modals, sheets, the settings
card, open-game rows and chips, badges, the logo, the type scale, the opacities). A theme
overriding two colours is complete against that inventory and unreadable on it. This PRD
holds completeness as assertable today and records legibility as blocked; see Requirement
12.

## Requirements

1. **Classic Red vs Blue ships as the second of the two launch themes.**
   *(`Theming.md` → Decisions → How many themes ship at launch; `Menus and UI.md` → Theme
   Selection)*

2. **It is authored as a partial override, not a full theme.** Classic defines only what it
   wants to be different and inherits the rest from Neon; it is materialized into a
   complete theme by merging its overrides over Neon.
   *(`Theming.md` → Neon Is the Base Theme → How it works; `Tech Design.md` → Decisions →
   Fallback to Neon — merge, not resolve)*
   *Testable:* the materialized theme has no unset value.
   **What this asserts, and what it does not.** Merge-over-Neon makes absence impossible by
   construction (`P1-03-theme-system.md` req 8), so this passes for any theme file that
   parses. It asserts that the merge works — not that the merged result is usable. The
   earlier form of this requirement also demanded an override set "materially smaller than
   `neon.theme.json`"; that phrase named no threshold and is withdrawn, because it now pulls
   directly against Requirement 12. See the tension recorded there and in Open Questions.

3. **What it overrides is the graphics — the art and colors.** Red player, blue player, no
   black background; no neon.
   *(`Theming.md` → Theme Catalog → Theme 2 → What it overrides)*

4. **Its signature sound is a splat** — like a water balloon popping, wet and playful,
   deliberately nothing like Neon's electric buzz. Classic and Neon have distinct sonic
   identities: Neon buzzes like a light, Classic splats like a water balloon.
   *(`Theming.md` → Theme Catalog → Theme 2 → Sound; `design_handoff_game_ui/themes.catalog.json`
   → `signatureSound: "splat"`)*
   **Blocked — no assertable form today, and satisfiable while silent.**
   `P2-02-audio.md` req 7 settles that `sound.signature` is *descriptive metadata, not an
   asset* — "the audio layer never plays it" — and `themes.catalog.json`'s `signatureSound`
   is the same kind of field. So a theme file carrying nothing but `sound: { signature:
   splat }` satisfies this requirement as worded and ships a theme **audibly identical to
   Neon**. Distinguishing "the splat is authored" from "the word *splat* is recorded"
   requires knowing which of the five playable slots (`P2-02-audio.md` req 6) the splat
   fills, which is an open question below and is not answered here. Until it is, this
   requirement carries no *Testable* line.

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
   proof.
   *(`Theming.md` → Neon Is the Base Theme → Why this matters for the build)*
   *Testable:* with Classic active, walk every screen that exists — main menu, theme select
   overlay, settings (menu route), the in-game quick-actions sheet, open-games list, name
   prompt, board in free-choice, board in forced quadrant, board with a pending move, the
   how-to-play legend and its hint line (`P3-05-how-to-play.md`), winner modal, draw modal,
   and the theme-failed-to-load modal (`P1-03-theme-system.md` reqs 27, 34 —
   `design_handoff_game_ui/README.md` → Still to design records that this one is not drawn)
   — and none falls back to an undefined or null value.
   **What this asserts, and what it does not.** Like Requirement 2, this passes by
   construction: after the merge there are no undefined values to find. The screens listed
   are the ones where a *ground-dependent* value would be visible, so the walk is the right
   walk — but "no null" is not "readable," and the how-to-play layer's three distinct text
   colours (`P3-05-how-to-play.md` req 19) are exactly the values most at risk. Legibility
   is Requirement 12, and Requirement 12 is blocked.

10. **Authoring Classic requires zero changes to game, board or menu code.** Only a theme
    definition is added.
    *(`Theming.md` → Architectural Rule)*
    *Testable:* dropping the Classic YAML into `assets/themes/` and rebuilding is
    sufficient — the diff edits no source file outside the theme layer, and in particular
    touches nothing under the board, menu or game layers.
    **Aligned to `P1-03-theme-system.md` req 32**, whose stated test is that a valid theme
    YAML appears in the catalog "with no source file edited outside the theme layer" and
    which forbids "a hand-maintained list of UUIDs in Dart." An earlier form of this
    requirement permitted the diff to touch "the theme asset *and its registration*"; if
    discovery is automatic there is no registration step, so that phrasing permitted a diff
    req 32 forbids. It is withdrawn. How themes are discovered is `P1-03`'s open question,
    not this PRD's to settle.

11. **Classic and Neon must read as two genuinely different looks.** This is the check that
    nothing is hardcoded, not a stylistic preference.
    *(`Theming.md` → Theme Catalog → Theme 2: "Two genuinely different looks, which is a
    real test that nothing is hardcoded")*
    **What this asserts, and what it does not.** The earlier form — "every surface Classic
    *overrides* renders differently" — quantified over Classic's own override set, so
    overriding a single colour satisfied it. Scoping it instead to the whole surface
    inventory in `Theming.md` → What a Theme Controls would make it falsifiable, but the
    threshold for "genuinely different" is not written anywhere, and inventing one would be
    inventing the override list this PRD is required not to invent. So this stands as the
    stated intent with no *Testable* line, and the enforceable half lives in Requirement 10
    (no code changed) rather than here.

12. **Classic must keep the gameplay-critical highlights legible** — the last-move
    highlight and the active-quadrant highlight are gameplay-critical, not decoration. A
    theme that makes them hard to spot is a broken theme.
    *(`Theming.md` → What a Theme Controls; Theme Catalog → Theme 1)*
    Classic *may* distinguish things by more than colour — shape, icon, outline, pattern —
    since that is "handled per theme"; it is not required to.
    *(`Theming.md` → Decisions → Is anything distinguished by colour alone?)*
    The treatments themselves are `P3-01-board-rendering.md` requirements 29–30, and
    `P3-05-how-to-play.md` requirement 19 extends the same legibility contract to the
    on-board legend and hint.

    **Blocked — this requirement cannot be given an assertable form here.** `Theming.md` →
    Open Questions now asks what form the legibility contract takes and records that the
    contract is unfalsifiable as written. Until that is answered, there is no contrast
    floor, review step or any other criterion to test against, and writing one into this
    PRD would be deciding the design docs' open question by accident. It is marked blocked
    rather than dropped because it is the **only** requirement in this document that a bad
    theme could fail.

    **The failure it is meant to catch, concretely.** An implementer who overrides the three
    `previewColors` and nothing else gets a theme that satisfies Requirements 2, 9 and 11 and
    is unusable: Neon's inherited `text: "#e9e9ed"` on Classic's `ground: "#f3f5fe"` is
    near-white on near-white, and every veil, scrim and glow inherited from Neon is an rgba
    tuned for `#161826`. Complete, passing, unreadable.

    **Tension with Requirement 2, stated and not resolved.** `Theming.md` → What a Theme
    Controls now enumerates modal, sheet, scrim, settings-card, row, chip, badge, logo,
    button, text-input, destructive and legend surfaces on top of the board. Geometry and
    radii are ground-independent and Classic can safely inherit them; every added *surface*
    slot, however, resolves to a colour tuned for a near-black ground. So the smallest
    override set that satisfies Requirement 2's spirit is the one most likely to fail this
    requirement, and satisfying this requirement plausibly means overriding twenty or more
    colours — which is no longer "as small as black → white, neon green → red." Neither
    outcome is refutable while the legibility contract is open. Which way it resolves is
    part of the standing "which values does Classic override" question, and is not decided
    here.

13. **Classic ships free, and theme selection labels it as free.** Neon and Classic Red vs
    Blue are the two free themes; every theme beyond those two is paid, and the theme
    selection list labels which themes are free and which are paid. Classic is the boundary
    case — the last free theme, and the shape the first paid theme is copied from.
    *(`Theming.md` → Decisions → Which themes are free; Are themes unlockable/rewards)*
    *Testable:* Classic is selectable and applies with no purchase, entitlement or unlock
    step of any kind, and its row in theme selection carries the free label.
    The free-tier default that makes this true is `P1-07-entitlements.md` requirement 1.

> **Recorded from `Theming.md` → Neon Is the Base Theme → Watch out for — stated, not a
> decision, and not a requirement above.** A partial theme inherits Neon's *personality*,
> not just its values. Classic Red vs Blue with Neon's electric buzz sounds and glow
> animations may feel mismatched — clean visuals with electric audio. That's a fine default
> (it works, nothing is missing), but Red vs Blue may want to override more than just
> colors to feel coherent. Worth checking once it's real; not a problem to solve now.

## Out of Scope

- **The theme mechanism** — the theme object and its slots, YAML loading, UUID identity,
  merge-over-Neon materialization, theme discovery and the catalog, the complete Neon base,
  and the failed-to-load modal: `P1-03-theme-system.md`. This PRD consumes all of it and
  changes none of it.
- **Persisting the selection** — `P1-04-persistence.md`.
- **The theme selection UI** — the overlay, the rows, the preview tile, the ACTIVE
  treatment, and the rendering of the free/paid labels: `P4-03-theme-selection.md`.
  Requirement 13 fixes only that Classic is free and is labelled so.
- **Audio playback** — loading and firing sound assets, `audioplayers`, the global mute:
  `P2-02-audio.md`. This PRD names the splat; it does not play it.
- **The animation system** — running animations, one-at-a-time sequencing, non-blocking
  input, the animations-off instant path: `P2-04-animations.md`. Classic inherits Neon's
  set and authors none.
- **Entitlement state and paid themes** — every theme beyond Neon and Classic is paid. The
  ownership model, the free-tier defaults and the locked/owned states are
  `P1-07-entitlements.md`; the store integration, purchase and restore flows are
  `P4-05-purchase-flow.md`. Nothing about Classic is gated by either. Note that Splat and
  Dinosaurs in `themes.catalog.json` remain explicitly placeholders that do not exist.
  *(`Theming.md` → Decisions → Are themes unlockable/rewards, Which themes are free;
  `design_handoff_game_ui/README.md` → The four themes shown)*
- **Generating the splat sound file and any art** — `P5-02-asset-generation-replicate.md`.
  Assets are generated with Replicate when actually needed; the Classic splat is one of the
  assets that decision names. What Classic's sound slot holds *before* that lands is an
  open question below.
  *(`Tech Design.md` → Decisions → Where do sound and art assets come from?;
  `design_handoff_game_ui/README.md` → Assets → Sounds: "none produced")*
- **Defining the legibility contract** — whether it is a contrast floor, a review step or
  something else is `Theming.md`'s open question, and `P1-03-theme-system.md` carries it as
  a system-wide question. This PRD is where it bites first, not where it gets answered.
- **Changing the theme mid-game.** Theme changes happen from the main menu only.
  *(`Theming.md` → Decisions → Can you change the theme mid-game)*

## Open Questions

### From `Theming.md` → Open Questions (worded as the doc words them)

- Which values, concretely, does Classic Red vs Blue override? (Settled in principle —
  graphics and its splat sound, inheriting the rest. An exact list will fall out when it's
  actually built.)
- What form does the legibility contract take — a contrast floor, a review step,
  something else? **What a Theme Controls** requires every theme to keep the last-move
  and active-quadrant highlights legible, but this is unfalsifiable as written: Classic
  Red vs Blue has a near-white ground while inheriting Neon's near-white text and its
  veils and glows tuned for a near-black ground, so a theme could be complete, pass every
  stated check, and still be unreadable.

The first is the central unresolved item and is deliberately not answered here: no concrete
color values, hex codes or override list appear in this PRD, because the docs leave them to
build time. The second is carried because **Requirement 12 states the legibility contract as
binding on this theme while the contract's form is open** — the requirement stands on this
question, and `P1-03-theme-system.md` carries the same question at the system level.

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
  written down. `P2-02-audio.md` requirement 6 fixes the five slots; which of them Classic
  overrides is this question. Requirement 4 is blocked on it.
- **Does Classic override the marks at all?** `themes.catalog.json` gives Classic the same
  `✕` / `○` marks as Neon, which would make "the art and colors" (Requirement 3) largely a
  color override in practice. `Theming.md` → Decisions → Marks beyond X and O allows a
  theme its own mark art but does not say Classic uses it.
- **What does Classic's sound slot hold before the splat file exists?**
  `P1-03-theme-system.md` carries the same question for Neon's five `"TODO"` sound slots —
  silent placeholder files, prose TODOs, or blocked on generation — and the answer applies
  identically here, since `P5-02-asset-generation-replicate.md` is **the same wave** as this
  PRD, not an earlier one. Note that `P5-02` currently asserts this PRD "ships with
  placeholders" and lists it among PRDs that "ship in earlier waves, without assets, by
  design"; that premise is stale and needs correcting in that PRD, not here.
- **Does the smallest legible Classic still count as the cheap-theme proof?** Requirement
  12's tension note is the substance; recording it here because it is the question that
  decides whether this feature validates `Theming.md`'s "new themes become cheap" claim or
  quietly refutes it.
