**Build-readiness: 93**

# PRD: Theme System

> **Status:** Draft · Source docs read: `Theming.md`, `Tech Design.md`, `Animations.md`,
> `Menus and UI.md`, `Game Board Design.md`, `Game Overview.md`, `Rules.md`, `roadmap.md`,
> and the read-only reference asset `design_handoff_game_ui/` (`README.md`,
> `neon.theme.json`, `themes.catalog.json`). `Alternative Game Styles.md` is a declared
> parking-lot doc and was not used as a source.
>
> **Revised for build-readiness.** Requirement 15 is a **normative schema** — key path,
> value shape, status. Requirement 8 carries the settled deep-merge rule. Requirement 13
> states exactly what `neon.yaml` must contain. Requirement 24 publishes the accessor.
>
> **Revised** after `Theming.md` → *Closing Neon's value gaps*, `Animations.md` → *Themes
> describe their animations*, `Game Board Design.md` → *Where does the free-choice cue
> live?*, `Theming.md` → *Does a theme control spacing and padding?* (no — every spacing key
> removed in v7), *Do all four toggles ship, and is music a theme concern?* (yes; shape open,
> Blocking 1), `Menus and UI.md` → *How does a player delete an open game?* (`icons.trash`
> added in v8), and user answers on discovery and chrome icons.
>
> **Schema version 8.** The last open contradiction with `Tech Design.md` closed when its
> guard table dropped the "inside board widgets" scoping; Requirement 25 and that doc now
> agree.

**Wave:** P1 · **File:** `P1-03-theme-system.md`

**Depends on:** `P1-01-app-scaffold.md` — same wave; it creates `lib/theme/`,
`assets/themes/`, `pubspec.yaml` and the Riverpod root this layer lands in.

**Depended on by** — every PRD below declares this one a dependency, and each compiles
against the Requirement 15 schema and the Requirement 24 providers:

- Wave 1: `P1-04-persistence.md`, `P1-05-theme-guard-test.md`, `P1-07-entitlements.md`.
- Wave 2: `P2-02-audio.md`, `P2-03-haptics.md`, `P2-04-animations.md`.
- Wave 3: `P3-01-board-rendering.md`, `P3-03-scoreboard-turn-indicator.md`,
  `P3-04-game-over-rematch.md`, `P3-05-how-to-play.md`.
- Wave 4: `P4-01-main-menu.md`, `P4-02-open-games-list.md` (the delete flow: `icons.trash`
  and `surfaces.destructive`), `P4-03-theme-selection.md`, `P4-04-settings.md` (its **four**
  toggles), `P4-05-purchase-flow.md`.
- Wave 5: `P5-01-classic-theme.md`, `P5-02-asset-generation-replicate.md`.

This PRD defines the **schema, the base theme and the accessor**; those define the behavior.

---

## Problem

There is no application code yet, and the one constraint the design docs say is expensive
to retrofit is the theme system: *"All of our code operates off of the theme. No code
should be operating independently from the selected theme"* (`Theming.md` → Architectural
Rule).

The failure mode is not hypothetical. `Theming.md` → Decisions → *What the theme's slots
are derived from* records that the original six-category list *"was written before the
screens existed"* and omitted board geometry, radii, the type scale, opacities and every
surface — *"so four PRDs were left unbuildable under the 'no hardcoded values' rule."*

A second failure mode is specific to this PRD, and it has two levels. Seventeen PRDs read
values from this layer, and none can name a key until this one does. **One level up, the
same thing happens to the accessor itself:** "readable through Riverpod" admits both
`ref.read(activeThemeProvider)` and a `ThemeExtension` reached through `Theme.of(context)`,
and those do not compile together. Requirement 15 closes the first level; Requirement 24 the
second.

A third is subtler and has bitten three times: **a missing key does not fail loudly.** A
consumer with nowhere to read from either writes a literal — which the guard catches — or
binds to the nearest existing key, which it does not. And when a component needs **N**
variants and is handed one style object, it does the third thing: a hardcoded switch among
style objects, which is bare Dart and invisible to the guard entirely.

**Not every gap is the same weight, and the difference decides priority.** An unauthored
*value* is debt: a control rendered with a plain fill is ugly but legal, and it ships.
A missing *glyph* is a deadlock: with no slot to read and no permitted literal, there is no
legal way to draw the thing at all. `icons.trash` was the second instance of that class
after `padding`, which is why it is `required` in the same pass that reported it — see
Appendix A.2, which states the triage rule this produced.

## Goal

The app ships a theme layer in which a theme is a **data file, not code**: YAML, dropped into
`assets/themes/`, discovered by a folder scan, identified and described by its own contents,
materialized once at startup by deep-merging over a complete Neon base, and reachable from
anywhere through one named provider. The schema is published with key paths and value shapes,
and is bounded to what the guard can actually enforce. `assets/themes/neon.yaml` holds every
value the approved design defines, plus the short list the design settled without drawing.

## Requirements

### Themes as data

1. A theme is **data loaded at runtime, not a Dart class compiled into the app**.
   *(`Tech Design.md` → Decisions → Theme representation — data, not code)*
2. The on-disk format for theme files is **YAML**.
   *(`Tech Design.md` → Decisions → What format are theme files — JSON or YAML?)*
3. Theme files are **bundled/shipped with the app**, living in `assets/themes/*.yaml`.
   *(`Theming.md` → Where Themes Live; `Tech Design.md` → Decisions → Project structure)*
4. **Each theme carries a UUID in its YAML file, and that UUID is the theme's identity.**
   Schema key: `meta.id`.
   *(`Tech Design.md` → Decisions → Theme identity — UUID)*
5. The theme layer lives at `lib/theme/`: `theme.dart`, `loader.dart`, `catalog.dart`,
   `theme_providers.dart` (Requirement 24) and `required_keys.dart` (Requirement 11).
   *(`Tech Design.md` → Decisions → Project structure — layer-first)*

### Inheritance and materialization

6. **Neon is the base theme.** Anything a theme does not define comes from Neon.
   *(`Theming.md` → Neon Is the Base Theme)*
7. **Inheritance depth is exactly one level.**
   *(`Theming.md` → Inheritance Depth; `themes.catalog.json` → `inheritanceDepth: 1`)*
8. **Deep merge, null = clear.** Each theme is materialized into a complete theme **at
   startup** by merging its overrides over Neon, so at runtime every lookup hits a complete
   theme and there is no fallback step. Three cases:

   | Case | Result |
   |---|---|
   | **Key absent** from the overriding theme | inherit Neon's value |
   | **Key present with a value** | that value wins |
   | **Key present and explicitly null** | the value is **cleared**, not inherited |

   And the merge is **deep**: *"a theme naming one key inside a section keeps Neon's other
   keys in that section rather than replacing the whole section. Nested maps merge
   recursively."*
   *(`Theming.md` → Decisions → How a theme merges over Neon; `Tech Design.md` → Decisions
   → Fallback to Neon — merge, not resolve)*
   **Consequence:** Neon ships `sound.music` as an explicit `null` — a deliberate clear, not
   an unfilled slot; Requirement 11's check treats it as defined.
   **A list is a leaf.** A theme naming a list **replaces it whole**. *PRD-author judgment:
   there is no stable identity for "the second keyframe."*
   **`meta` does not merge.** `meta.id`, `meta.name` and `meta.blurb` are never inherited.
   **Testable:** a theme overriding `color.ground` alone materializes with all 42 other
   `color.*` keys at Neon's values; `sound.buttonTap: null` yields no button-tap sound; a
   theme overriding `surfaces.legend.swatchStyle.locked` alone keeps Neon's other five;
   a theme omitting `meta.name` fails to load rather than inheriting `"Neon"`.
9. A theme file may define **only** what it wants to be different — beyond `meta` — and must
   still materialize complete.
10. Animations and sounds merge by the same rule as every other value.
    *(`Animations.md` → Decisions → Do themes inherit Neon's animations?; `Theming.md` →
    Sound Decisions → Sound falls back to Neon)*

### The Neon base theme

11. **Neon defines every key the Requirement 15 schema marks `required`** — whether that
    value is transcribed from the handoff or authored (Requirement 13).
    *(`Theming.md` → Neon Is the Base Theme; → Decisions → Closing Neon's value gaps)*
    **Testable — runnable form:** `lib/theme/required_keys.dart`, a flat
    `const List<String>` of every `required` key path. One test iterates it and asserts each
    resolves in Neon's materialized theme, **counting an explicit null as defined**. A second
    asserts list and schema agree.
12. **`assets/themes/neon.yaml` is the authoritative Neon definition.** `neon.theme.json`
    stays as it is and is a **reference**: *"the two can drift, and the YAML is authoritative
    where they differ."* **Do not "correct" the YAML back toward the JSON** — the JSON now
    carries three spacing keys the schema no longer has.
    *(`Theming.md` → Decisions → Closing Neon's value gaps)*
13. **What `assets/themes/neon.yaml` must contain — and the two ways a value gets there.**

    **(a) Transcribed — the large majority.** Every value the approved design draws *that the
    schema still carries*, copied faithfully. Two read-only sources, neither edited:

    | Source | What comes from it |
    |---|---|
    | `neon.theme.json` | `id`, and every key in `color`, `marks`, `type`, `radius`, `sound`; the `board` keys the schema retains; and `animation`'s durations, easings and loop flags |
    | `README.md` and `themes.catalog.json` | everything drawn in the token tables, board sections and screens `1a`–`2d` that the JSON does not carry — the pending-move colour and its rings, grid-line opacity and glow, the claimed and cat-game glows, the cat caption, the modal and sheet surfaces, the scrims, the settings card, the game rows and chips, the theme rows and badges, the menu, the buttons, the input field, the legend typography and its six swatches, the free-choice cue, the scoreboard chips, the five drawn chrome icons, and Neon's `name` and `blurb` |

    **No value is invented, altered or rounded.** Composites are restructured per
    Requirement 35 and motion re-expressed per Requirement 18.

    **(b) Authored — a short, named list.** Some `required` keys have **no drawn source at
    all**: the design settled the affordance without the handoff ever drawing it. These are
    still `required`, and this is the exhaustive list:

    | Key | Why there is nothing to copy | Settled by |
    |---|---|---|
    | `icons.trash.*` | Handoff `1b` predates the delete decision; no trash glyph is drawn anywhere | `Menus and UI.md` → How does a player delete an open game? |
    | `surfaces.destructive.*` | Same drawing, same gap — the revealed control's panel and the modal's Yes button | as above |
    | `animation.<moment>.tracks[].keyframes[].value` | The handoff gives durations, easings and loop flags but never says *how far* | `Animations.md` → Themes describe their animations |

    **Everything else `required` is transcribed.**
    **`icons.trash` is the urgent one, and not for aesthetic reasons.** The other two are
    debt: an unauthored colour still renders, and a theme with plain values ships. A missing
    glyph is a **deadlock** — `P1-05`'s icon-constant rule covers the whole scan root against
    a zero baseline, so `Icons.delete` in `lib/ui/menus/` fails the build, and with no slot
    there is no legal alternative. Authoring a Phosphor `trash` reference costs one line;
    leaving it costs `P4-02` its delete flow entirely. Appendix A.2 generalises this into the
    rule for triaging any future `deferred` call.

    **Still `deferred`:**

    | Key | Why |
    |---|---|
    | `surfaces.settingsCard.purchases.*` | Nothing drawn, and no Decision describes what the section *is* — *Blocking* item 7 |
    | Music beyond `sound.music`'s placeholder null | A theme supplies its music, but the key's final **shape** is open — *Blocking* item 1 |

    **Testable:** every leaf in `neon.yaml` traces to a source in (a) or appears in (b)'s
    table, and Requirement 11's manifest resolves completely.
14. Neon's UUID is `b7c1f0a6-2f5e-4d3a-9c88-0f5a1e2d3c40`, and Neon is both the base theme
    and the default active theme.
    *(`neon.theme.json` → `id`; `themes.catalog.json` → `baseThemeId`, `defaultThemeId`;
    `Menus and UI.md` → Decisions → Which theme is active by default?)*

### Requirement 15 — the schema

15. **This is the theme schema. Every key a consumer reads is named here, with its value
    shape and its status.** Naming a key does not decide its value.

    **Status:** `required` — Neon must hold a value; transcribed unless Requirement 13(b)
    lists it as authored. `deferred` — in the contract, nothing drawn and nothing settled.
    `undecided` — **do not implement**, pending *Blocking*.

    Shapes: `color` = `#rrggbb` or `rgba(r,g,b,a)`; `dp` = logical pixels; `ms` = integer
    milliseconds; `assetPath` = a path under `assets/`, or null; `ref` = a `type.scale` style
    name.

    #### The boundary: what a theme does *not* control

    **Spacing and padding are fixed in code, not themed**, because the guard cannot catch a
    hardcoded gap — a padding section would have been *"a rule that nothing verifies."*
    *(`Theming.md` → Decisions → Does a theme control spacing and padding?)*

    | Fixed in code | Still themed |
    |---|---|
    | outer gap, quadrant padding, inner gap | grid-line width, grid-line inset, mark sizes |

    **Stated in its own terms:** a theme controls **the drawn geometry of a thing itself** —
    stroke width, glyph size, corner radius, glow spread. Code controls **where things sit
    relative to one another**. Classify a new key with that sentence, not by looking for the
    word "padding."

    #### `meta` — all **required**, and never inherited (Requirement 8)

    | Key path | Shape | Notes |
    |---|---|---|
    | `meta.id` | UUID string | the theme's identity |
    | `meta.schemaVersion` | integer — **8** | Requirement 37 |
    | `meta.name` | string | the display name. `P4-03` req 6 renders it |
    | `meta.blurb` | string | the one-line description. `P4-03` req 6 renders it |

    #### `color` — 43 keys, all **required**

    | Group | Key paths |
    |---|---|
    | Grounds and surfaces | `ground`, `groundDeep`, `groundLift`, `surface`, `surfaceRaised`, `surfaceSunken`, `hairline`, `hairlineStrong` |
    | Text | `text`, `textMuted`, `textSubtle`, `textDim`, `textFaint` |
    | Board | `boardLine`, `boardLineGlow`, `quadrantBorder`, `quadrantBorderOpen`, `quadrantFill` |
    | Player one | `playerOne`, `playerOneMark`, `playerOneGlow`, `playerOneTint`, `playerOneOnTint` |
    | Player two | `playerTwo`, `playerTwoMark`, `playerTwoGlow`, `playerTwoTint`, `playerTwoOnTint` |
    | Highlights | `highlightForced`, `highlightForcedGlow`, `highlightLastMove`, `highlightLastMoveGlow`, `highlightPending` |
    | Accent | `accent`, `accentLight`, `accentSoft` |
    | Cat game | `catGame`, `catGameGlow` |
    | Veils and scrims | `veilLocked`, `veilClaimed`, `veilCat`, `scrim`, `scrimHeavy` |

    **`color.*` and `radius.*` are palette tokens, not component tokens.** A component reads
    its own `surfaces.*` or `icons.*` key, never a palette key that happens to hold the same
    value.

    #### `marks` — **required**

    `marks.{playerOne,playerTwo,catGame}.{kind,value,font,weight}`, where `kind` is
    `glyph | icon | image` (see *Blocking*) and `font`/`weight` are **per-mark**.

    #### `icons` — glyphs, all **required**

    | Key path | Shape |
    |---|---|
    | `icons.<slot>.kind` | `iconSet` \| `image` |
    | `icons.<slot>.set` | string — e.g. `phosphor`; required when `kind: iconSet` |
    | `icons.<slot>.name` | string — the glyph name in that set |
    | `icons.<slot>.path` | `assetPath` — required when `kind: image` |
    | `icons.<slot>.tint` | `color` |
    | `icons.<slot>.size` | `dp` |
    | `icons.<slot>.button.{fill,radius,size}` | optional per slot — **chrome buttons only** |

    | Slot | Consumer | Source |
    |---|---|---|
    | `settings` | `P3-03` req 12 — drawn 44×44 on `1d`/`1e` | transcribed |
    | `close` | `P4-03` req 3, `P4-04` | transcribed |
    | `chevronLeft` | the back control on `1b`/`1c` | transcribed |
    | `chevronRight` | the row chevron on `1b`, `P4-02` | transcribed |
    | `plus` | the New Game row on `1b`, `P4-02` | transcribed |
    | **`trash`** | **`P4-02`'s revealed delete control** | **authored** — Req 13(b) |

    **`icons.trash` takes no `button` sub-object.** The other five are chrome sitting on a
    screen's own background, so each owns its button treatment. The trash is a **revealed row
    control**: swiping the row exposes a panel behind it, and that panel is
    `surfaces.destructive.action` — fill and radius — while the row's own height sizes it.
    Giving the slot a `button` sub-object would put two owners on one surface.
    **One control, one surface owner:** `icons.trash` carries the glyph, its `tint` and its
    `size`; `surfaces.destructive.action` carries what is behind it.
    *(`Menus and UI.md` → Decisions → How does a player delete an open game? — *"The revealed
    control is a **trash button** — an icon, not a worded 'Delete' label."*)*

    #### `type` — **required**

    `type.family`; `type.weights.{regular,medium,semibold}`; `type.scale.<style>.{size,
    weight}` with optional `tracking`, `lineHeight`, `uppercase`. `<style>` ∈ `display`,
    `title`, `heading`, `subhead`, `body`, `label`, `caption`, `chipLabel`, `chipValue`,
    `mark`, `markClaimX`, `markClaimO`, `markCat`, `sheetTitle`, `sheetSub`, `rowTitle`.

    #### `radius` — **required**, palette tokens

    `cell`, `quadrant`, `chip`, `control`, `button`, `buttonLarge`, `modal`, `pill`, `card`,
    `row`, `priceAction`. All `dp`.

    #### `board` — **required**

    | Key path | Shape | Source |
    |---|---|---|
    | `board.gridLineWidth` | `dp` | JSON — **explicitly themed** by the spacing Decision |
    | `board.gridLineInsetPercent` | number, percent | JSON — likewise |
    | `board.quadrantShadow`, `.quadrantShadowOpen` | shadow list (Req 35) | JSON |
    | `board.forcedRing`, `.lastMoveRing` | ring object (Req 35) | JSON |
    | `board.gridLineOpacity`, `.gridLineGlow` | number / shadow list | README |
    | `board.pendingCellRing`, `.pendingQuadrantRing` | ring object | 2d |
    | `board.pendingGhostOpacity`, `.pendingQuadrantWash` | number / color | 2d |
    | `board.claimedMarkGlow`, `.catMarkGlow` | shadow list | README |
    | `board.catCaption.{size,weight,tracking,color}` | `dp` / int / number / color | README |

    `outerGap`, `quadrantPadding` and `innerGap` are **not here** — fixed in code.

    #### `sound` — seven keys, five playable one-shots

    `sound.{placeMark,claimQuadrant,catGame,winGame,buttonTap}` (`assetPath`, **required**,
    values are prose `"TODO"` today); `sound.signature` (string, **metadata, never played**);
    `sound.music` (`assetPath` or null — the placeholder, its final shape open per *Blocking*
    item 1). See Requirement 17.

    #### `animation` — a motion **description**, not a behaviour name

    | Key path | Shape | Status |
    |---|---|---|
    | `animation.<moment>.duration` | `ms` | **required** |
    | `animation.<moment>.repeat.{count,mode}` | integer \| `infinite` / `restart` \| `reverse` | **required** |
    | `animation.<moment>.tracks` | list of track objects, ≥ 1 | **required** |
    | `…tracks[].{property,easing}` | closed set (Req 18) / easing string | **required** |
    | `…tracks[].delay` | `ms` | optional |
    | `…tracks[].keyframes` | list of ≥ 2 `{at, value}` | **required** |
    | `…keyframes[].at` | 0.0–1.0, fraction of `duration` | **required** |
    | `…keyframes[].value` | number, or `color` | **required — authored** |
    | `…keyframes[].easing` | overrides the track's for the segment ending here | optional |

    `<moment>` ∈ `placeMark`, `claimQuadrant`, `catGame`, `winGame`, `activeQuadrant`,
    `lastMove`.

    #### `surfaces`

    | Key path | Status | Drawn in / consumer |
    |---|---|---|
    | `surfaces.modal.{fill,border,radius,shadow,winnerBorder}` | **required** | `1f`–`1h` / `P3-04` reqs 10, 13; **reused by the delete confirmation** |
    | `surfaces.sheet.{fill,radius}` | **required** | `1f`, `2a`, `2c` |
    | `surfaces.sheet.header.{titleStyle,subStyle,closeControl}` | **required** | `2a` / `P4-03` req 3 |
    | `surfaces.scrim.{modal,settings,themeSelect,namePrompt}` | **required** | `1f`–`1h`, `2a`, `2c` |
    | `surfaces.settingsCard.{fill,border,radius}` | **required** | `2b` / `P4-04` reqs 6, 16 |
    | `surfaces.settingsCard.toggleRow.{labelStyle,subLabelStyle}` | **required** | `2b` — four rows, one of them Music |
    | `surfaces.settingsCard.switch.{trackOn,trackOff,knobOn,knobOff,glowOn}` | **required** | `1f`, `2b` |
    | `surfaces.settingsCard.purchases.{sectionDivider,priceRow,restoreControl}` | **deferred** | nothing drawn, no Decision on treatment |
    | `surfaces.gameRow.{fill,radius,titleStyle,timeStyle,chip,chipYouOutline,chevron}` | **required** | `1b` / `P4-02` reqs 4, 17, 18 |
    | `surfaces.themeRow.{fill,radius,previewTile,activeRing,lockedPreviewOpacity}` | **required** | `2a` / `P4-03` reqs 6, 8, 13 |
    | `surfaces.badge.{free,owned,active,priceAction}` | **required** | `2a`, `themes.catalog.json` |
    | `surfaces.menu.{background,kickerStyle,wordmarkStyle,wordmarkGlow,taglineStyle,footerStyle}` | **required** | `1a` / `P4-01` reqs 7, 13 |
    | `surfaces.menu.logo` | **required** slot; asset is a placeholder | `1a` / art by `P5-02` |
    | `surfaces.menu.dimBehindOverlay` | **required** | `2a` (35%) |
    | `surfaces.button.{primary,secondary}` | **required** | `1a`, `2c` / `P4-01` reqs 4, 6 |
    | `surfaces.input.{fill,radius,focusBorder,caret,valueStyle,labelStyle,counterStyle}` | **required** | `2c` / `P4-02` reqs 8, 9, 17 |
    | `surfaces.placeholder.{border,radius,glow}` | **required** | `1a`'s logo **and** `1c`'s avatars |
    | `surfaces.focusRing` | **required** | README → *Interactions & behavior* |

    **Destructive — `required`, authored (Requirement 13(b)), and reshaped in v8.**

    | Key path | Carries |
    |---|---|
    | `surfaces.destructive.action.{fill,radius}` | the **panel revealed by swiping a row left**, behind `icons.trash` |
    | `surfaces.destructive.confirmAccept.{fill,labelStyle,border,radius}` | the modal's **Yes** button |

    **What changed and why.** The action key previously carried `labelStyle` and `icon`. Both
    are gone: the Decision specifies *"a trash button — an icon, not a worded 'Delete'
    label,"* so **there is no label to style**, and the glyph now has its own slot. A component
    key with no reader comes out — the same test `turnBanner` and `turnIndicator` failed.
    **The modal's other button is not a new key.** Its choices are **Yes and No**: **Yes** is
    `surfaces.destructive.confirmAccept`, **No** is the existing `surfaces.button.secondary`,
    and the dialog's chrome is `surfaces.modal` over `surfaces.scrim.modal`.
    **Authoring brief:** deletion is *"the only irreversible action in the app — it destroys
    the game and its whole running scoreboard"* and kids are a stated target audience.

    **Legend and how-to-play strip.**

    | Key path | Status | Notes |
    |---|---|---|
    | `surfaces.legend.hintStyle` | **required** | the two-tap hint — `1d`, 12/400 |
    | `surfaces.legend.labelStyle` | **required** | the legend entry's text — `1d`, 10.5/400 |
    | `surfaces.legend.swatchStyle.<state>` | **required** | **a map keyed by state**, six entries |
    | `surfaces.legend.ringExplanationStyle` | **required** | `1e`, `2d` |
    | `surfaces.legend.freeChoiceCueStyle` | **required** | `1d` — 12/400 `#4fc3ff` |

    `<state>` ∈ `open`, `locked`, `catGame`, `lastMove`, `activeQuadrant`, `pending`.

    **Scoreboard chips — per player, because the states are not shared.**

    | Key path | Status | Notes |
    |---|---|---|
    | `surfaces.scoreboard.chip.playerOne.active.{fill,border,glow,labelStyle,valueStyle}` | **required** | `1d` |
    | `surfaces.scoreboard.chip.playerOne.inactive.{fill,border,labelStyle,valueStyle}` | **required** | `1d`/`1e` |
    | `surfaces.scoreboard.chip.playerTwo.active.{…}` / `.inactive.{…}` | **required** | `1e` |
    | `surfaces.scoreboard.chip.ties.{fill,border,labelStyle,valueStyle}` | **required** | **No active variant, by design** |
    | `surfaces.scoreboard.radius` | **required**, `dp` | `1d` |

    #### Not in the schema

    | Section | Why |
    |---|---|
    | **spacing and padding** | **Decided against** — the guard cannot verify it. Hedged *"for now"* |
    | fill patterns / textures | **not supported** — Requirement 21 |
    | `surfaces.destructive.action.labelStyle` | **removed in v8** — the control is an icon, not a word |
    | `surfaces.scoreboard.turnBanner` | **removed in v5** — the banner is not built |
    | `surfaces.scoreboard.turnIndicator` | **removed in v6** — no reader |
    | `surfaces.deleteDialog.*` | never existed — the confirmation reuses `surfaces.modal` |
    | a `music.<context>` map | **not yet** — *Blocking* item 1 |
    | haptics | Never theme-driven — Requirement 29 |
    | ownership, price | Never in a theme definition — Requirement 31 |

16. **Marks are asset slots on the theme, not shapes drawn in board code.**
    *(`Tech Design.md` → Decisions → Marks — image or icon; `P3-01` req 17)* Neon authors a
    third kind, `glyph` — see *Blocking*.
17. **Five playable one-shot moments, plus `signature` (metadata, never played) and
    `music`.** A consumer must not treat `sound.*` as an iterable list of playable assets.

    **Music is a theme concern**, per `Theming.md` → Decisions → *Do all four toggles ship,
    and is music a theme concern?*, which **supersedes** *One-shot sound effects only, for
    now*. The Decision establishes ownership, not shape: `sound.music` stays the minimal
    placeholder, no key is added or re-shaped, and the choice is *Blocking* item 1.
    **Music is not a one-shot** — a one-shot fires and ends; music loops and has a lifecycle —
    so whatever shape wins, it is never another `SoundMoment`.
    **Nothing plays it**, but the *setting* has a consumer: `P4-04` ships a fourth toggle
    controlling it. A confirmed consumer of the setting and none of the asset is why this is
    `deferred` rather than removed.
    *(`Theming.md` → What a Theme Controls → Audio; `P2-02` reqs 6, 7.)*
18. **A theme describes its motion; the runtime interprets the description.** Each moment is
    a **duration, a repeat rule and a list of tracks**.
    *(`Animations.md` → Decisions → Themes describe their animations; → Duration lives in the
    animation)*
    **The property set is closed**: `scale`, `opacity`, `glowRadius`, `glowColor`,
    `translateX`, `translateY`, `rotation`. *Blocking item 5 carries the shadowbox finding.*

    | Moment | Was | Becomes | Transcribed | Authored |
    |---|---|---|---|---|
    | `placeMark` | `grow-shrink`, 220ms, `cubic-bezier(.34,1.56,.64,1)` | one `scale` track | duration, easing | scale magnitudes |
    | `claimQuadrant` | `grow-shrink-glow`, 420ms | `scale` + `glowRadius` | duration | both magnitudes |
    | `catGame` | `shrink-fade`, 300ms | `scale` + `opacity` | duration | scale magnitude |
    | `winGame` | `glow-pulse`, 900ms | one `glowRadius` track | duration | pulse magnitude |
    | `activeQuadrant` | `glow-pulse`, 1600ms, `loop` | `glowRadius`, `repeat: {infinite, reverse}` | duration, loop | pulse magnitude |
    | `lastMove` | as above | as above | duration, loop | pulse magnitude |

    **The interpreter is `P2-04`'s.**
19. **A theme supplies its own font** — `type.family`. Inter 400/500/600 is bundled as
    **Neon's font choice, not an app-wide font constant**.
20. The last-move, active-quadrant and pending-move treatments are **separately addressable
    keys**; the legend's six swatches are the same rule applied to the strip that explains
    them.
21. **The schema supports distinguishing things by shape, icon, outline style and motion —
    and *not* by fill pattern or texture.** `P5-01` req 12's pattern permission has no
    backing here.

### Runtime integration

22. **Flutter's `ThemeData` / `ThemeExtension` is populated *from* the theme object** — a
    **mirror, not the source**.
23. **Sounds and animations live in the same theme object**, which is also why the theme
    object rather than `ThemeData` is the accessor.
24. **The accessor is published. Consumers read the theme through these symbols and no
    others.**

    ```dart
    // lib/theme/theme_providers.dart

    /// The materialized active theme. Never null (Requirement 8).
    /// Reachable with or without a BuildContext.
    final Provider<Theme> activeThemeProvider;

    /// The installed themes, discovered by folder scan (Requirement 32),
    /// ordered by asset key. Each entry carries {id, name, blurb, assetKey}
    /// and its own materialized Theme — the read path required by Requirement 33.
    final Provider<List<ThemeCatalogEntry>> themeCatalogProvider;

    /// The selected theme's UUID, and the only write path for changing it.
    final NotifierProvider<ActiveThemeNotifier, String> activeThemeIdProvider;
    ```

    - **`activeThemeProvider` is the source of truth**, not `Theme.of(context)`.
    - **No `BuildContext` is required** — decisive, because `P2-02` req 2 publishes
      `void play(SoundMoment)`, which has none.
    - **Widgets `watch`. Services `read` at use time.**
    - **`ThemeCatalogEntry`** — `id`, `name`, `blurb`, `assetKey`, `theme`.
    - **Overriding `activeThemeProvider` is the test seam.**

    **PRD-author judgment**, following `P1-04` req 26's precedent.
25. **Architectural Rule.** No hardcoded values anywhere in the code, across the full
    Requirement 15 schema — including motion, chrome, and **the shape of a variant set**.
    **Spacing is the one named exception.**
    *(`Theming.md` → Architectural Rule, as amended; `Tech Design.md` → Decisions → Do we add
    a test that fails on hardcoded theme values?, whose guard table now reads *"`Icons.*`
    anywhere outside the theme layer"* — the earlier board-widgets scoping is gone, and this
    requirement and that doc agree.)*
    **The guard's limits:**
    - It catches a value written into code, not a value read from the wrong key
      (Appendix A.1).
    - It **cannot see bare numeric geometry** (`P1-05` req 4(c)) — which is why spacing came
      out, and why **`board.gridLineWidth`** is the one deliberate false negative left.
    - It cannot see a switch over hardcoded style objects — hence per-state key shapes.
    - **Where it works perfectly is icons**, now that its rule covers the whole scan root:
      that is what turned a missing `trash` slot from an oversight into a build failure.
26. **Adding a new theme requires zero changes to game, board or menu code** — only dropping
    a theme file into `assets/themes/`.

### Failure behavior

27. If a theme fails to load, show a **modal on the Theme screen**, then **fall back to
    Neon**. *(`P4-03` reqs 20–21)*
28. Neon is the one theme with nothing to fall back to.

### Boundaries of the theme object

29. **Haptics are not theme-driven**, and the haptic fires on every valid tap app-wide as an
    app behavior. *(`Theming.md` → What a Theme Does NOT Control; `P2-03`)*
30. **Four toggles ship — Music, Sound Effects, Vibrate on Touch, Animations — and all four
    are global player settings, not theme properties.** They are read through `P1-04`'s
    providers, never through `activeThemeProvider`.
    **The asymmetry is three-to-one:** music, sound and animations switch off a *theme-defined
    channel*; vibrate switches off an *app behavior a theme never defines*.
    *(`Theming.md` → Decisions → Do all four toggles ship…; `P4-04` req 11)*
31. **Ownership / entitlement is not part of a theme definition.**

### The catalog, and reading a non-active theme

32. **Themes are discovered by scanning the themes folder.**
    1. `assets/themes/` is declared in `pubspec.yaml` **as a directory**.
    2. At startup the catalog reads Flutter's **asset manifest** and selects every bundled key
       under `assets/themes/` ending in `.yaml`.
    3. Each file is validated: well-formed YAML, an understood `meta.schemaVersion`, non-empty
       `meta.id`, `meta.name`, `meta.blurb`.
    4. A **catalog entry** is `{id, name, blurb, assetKey}` plus the materialized theme.
    5. Entries are ordered **by asset key**; display order is `P4-03`'s.

    | Failure | Result |
    |---|---|
    | Unparseable YAML, or missing/blank `meta.*` | that file is **excluded** and reported |
    | `meta.schemaVersion` not understood | same |
    | **Duplicate `meta.id`** | the entry earlier by asset key wins |
    | A duplicate of **Neon's** UUID from another file | the other file always loses — reserved |
    | No valid theme at all | Neon has failed to load; *Blocking* item 3 |

    **PRD-author judgment, flagged:** the duplicate-id and reserved-base-id rules are not in
    any design doc.
33. **A non-active theme's values are readable without making it active** — via
    `themeCatalogProvider`.
34. **A theme that fails to load must not take the app down with it.**

### Encoding, dependencies and versioning

35. **Composite values are structured fields, not parsed CSS strings.**
    - **shadow list** — `{offsetX, offsetY, blur, spread: dp, color, inset: bool}`.
    - **ring object** — `{width: dp, style, color, offset: dp, radius: dp, glow: shadow
      list}`, `style` ∈ `solid | dashed`, plus **`dashLength` / `dashGap`**.
    - **gradient** — `{type: linear | radial, stops: [{at, color}], …}`.
    - **colors stay strings**, parsed at load.
36. **YAML parsing uses the `yaml` package, declared in `pubspec.yaml` by `P1-01`, and
    `assets/themes/` is declared as a directory.** **PRD-author judgment on both.**
37. **The schema is versioned. `meta.schemaVersion` is now `8`.**

    | Version | What changed |
    |---|---|
    | 1 | the original `type` / `durationMs` / `easing` / `loop` animation shape |
    | 2 | animation redesigned as a motion description |
    | 3 | `icons` added; scoreboard chips per-player; `turnBanner` deferred |
    | 4 | `meta.name` and `meta.blurb` added |
    | 5 | `turnBanner` removed; `freeChoiceCueStyle` and `surfaces.placeholder` added; gradient and dash shapes defined |
    | 6 | `surfaces.destructive` promoted to required (authored); `swatchStyle` per-state; `legend.labelStyle` added; `turnIndicator` removed |
    | 7 | all spacing and padding keys removed |
    | 8 | `icons.trash` added; `surfaces.destructive.action` reshaped to `{fill, radius}` |

    **No bump for the music Decision** — it changed what `sound.music` means without changing
    a key path, and its real shape is still open.
    **There is no migration:** the only theme file in existence is Neon's, and Requirement 13
    writes it fresh this wave.

## Out of Scope

- **The guard test** — `P1-05`. **Persistence** — `P1-04`. **Entitlements** — `P1-07`.
- **The delete flow itself** — the swipe gesture, the trash button's behaviour, the modal's
  copy, and what deleting does to storage: `P4-02`. This PRD supplies the glyph slot and the
  two destructive treatments.
- **Playing music** — no PRD owns it yet.
- **The settings screen and its four toggles** — `P4-04`.
- **All spacing and layout numbers**, now code constants.
- **The animation interpreter** — `P2-04`. **The audio layer** — `P2-02`.
- **The how-to-play strip** — `P3-05`. **The scoreboard** — `P3-03`.
- **The About Us screen's own surface keys** — `1c` ships but no PRD names what it reads.
- **The Classic theme** — `P5-01`. **Assets and the real logo** — `P5-02`.

---

## Appendix A — non-normative

**Nothing in this appendix is work.**

### A.1 Near-miss forensics — why the schema names keys the guard cannot protect

| Drawn value | The near-miss it invites |
|---|---|
| **Active P1 chip fill `rgba(255,61,113,0.14)`** | **`color.playerOneTint`, the *same value*.** Correct today, silently wrong the first time either moves. `color.playerTwoTint` is `0.12` — **not** symmetric |
| **Free-choice cue `#4fc3ff`** | `color.boardLine`, the same hex. Board-blue *on purpose* |
| **Six legend swatches** | one `swatchStyle` plus a Dart switch — the failure with no literal in it |
| **`board.gridLineWidth` 1.5** | a literal `1.5` in a painter. The one *deliberate* false negative |
| `OWNED` badge `rgba(45,255,158,0.16)` | `color.playerTwoTint` at `0.12` |
| Legend label 10.5 / `#595d6c` | `surfaces.legend.hintStyle` at 12 / `#75798c` |
| **The trash glyph** | `Icons.delete` — **the one row the guard catches.** It fails the build instead of shipping wrong |
| Any value via `Theme.of(context)` | resolves, returning Flutter's mirror — wrong for `surfaces.*`, `sound.*`, `animation.*` |

**The trash row is the odd one out, and that asymmetry is the argument for the widened
`Icons.*` rule.** Every other row is a value that resolves to something plausible and ships:
the screen renders, nothing throws, and the defect surfaces whenever someone next compares
against the handoff. `Icons.delete` cannot do that — the scan covers the whole root against a
zero baseline, so it fails the build the moment it is written. That is worth the rule's cost
in false negatives elsewhere, and it is more persuasive as an observed case than it was as a
prediction: the missing `trash` slot was found *because* the guard would have stopped the
workaround.

### A.2 Authored, not transcribed — and the two weights of "missing"

Requirement 13(b) is the normative list. The distinction worth carrying: **`icons.trash` is a
deadlock, the other two are debt.** An unauthored `surfaces.destructive` fill renders as
something and ships; unauthored animation magnitudes leave motion looking flat. A missing
glyph has no legal implementation at all — no slot to read, no literal permitted.

**The triage rule this produces, for every future `deferred` call:** ask whether the absence
is *ugly* or *impossible*. Ugly can wait for a design pass — the feature ships, looks wrong,
and is fixed by authoring one value later with no code change, because the key already exists
and the consumer already reads it. Impossible cannot wait at any price: there is no
implementation an author could write that both satisfies the requirement and passes the
build, so the feature does not ship at all and no amount of scheduling helps. **Only the
second kind blocks.** Applied to what is open now: `surfaces.settingsCard.purchases.*` is
ugly — `P4-04` can render its section unstyled — and music's shape is neither, because nothing
plays it yet.

---

## Open Questions

**None of the below blocks a landed consumer from compiling against this PRD.** Items 1 and 7
are the closest: nothing plays music, and `P4-04` can build its purchases section but has no
styling source for it. Both are *ugly*, not *impossible*, by A.2's rule.

### Blocking — needs the user

1. **What shape does a theme's music take?** The Decision settles ownership and explicitly
   leaves open *"whether music loops, whether it differs by screen, and where the audio comes
   from."* The per-screen half decides the key:

   | Shape | Reading | Cost if wrong |
   |---|---|---|
   | `sound.music: assetPath \| null` — today's placeholder | one track for the whole app | every theme authored against it needs re-authoring, plus a version bump and a migration |
   | `music.<context>: assetPath \| null` | per-screen tracks | provisions keys nothing reads today |

   **Not picked here** — the question is cheap for the user and both wrong answers are
   expensive.
2. **What goes in Neon's five `"TODO"` sound values.**
3. **What counts as "fails to load" beyond Requirement 32's table, and what happens if
   *Neon* fails?**
4. **Are all themes materialized at startup, or only the selected one?**
5. **Does the animation property set need an eighth member?** `P2-04` reports **shadowbox has
   no obviously right property** — it maps onto `glowRadius`/`glowColor`, but a drop shadow
   that lifts the marker off the board is *directional and offset*.
6. **Is `glyph` a third mark `kind`?** The docs say *image or icon*; Neon authors `glyph`.
7. **Should `surfaces.settingsCard.purchases.*` become `required` (authored)?** It sits where
   `surfaces.destructive` sat — a required reader and a settled placement, but nothing drawn,
   and no Decision describes what the section *is*.

### From the design docs — carried, not resolved

- **What form does the legibility contract take?** Unfalsifiable as written.
- **Which values does Classic Red vs Blue override?** Owned by `P5-01`; it will need a music
  position the day Blocking 1 lands, and its req 12 needs revisiting against Requirement 21.
- **Unknown or misspelled keys inside a valid theme file** — Requirement 32 catches malformed
  files and bad versions, not bad keys inside a good one.
- **Resolved earlier:** spacing and padding (v7), the three lookup paths (Requirement 24), the
  turn banner (v5), theme discovery and per-file name/blurb (Requirement 32), chrome icons,
  and the `Tech Design.md` guard-table scoping — its table now reads *"`Icons.*` anywhere
  outside the theme layer"*, so nothing is outstanding against Requirement 25.
- **The exact slot schema.** Requirement 15 is this PRD's answer, structure ratified. Writing
  it, the chrome-icon Decision and the spacing boundary into `Theming.md` is
  `forge-doc-writer`'s to route.

### Contradiction between docs — flagged, not resolved

- **How many themes the selection list shows** — the handoff's *2a* draws four,
  `Theming.md` says two. `P4-03` → OQ 1 carries it; Requirement 32 is indifferent.
- **`P2-02-audio.md` reqs 14 and 15 were written under a superseded stance** — "no background
  music in this version" no longer holds. Being reconciled by that PRD.
