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
> removed in v7), *Do all four toggles ship, and is music a theme concern?* (yes; **the
> key's shape is now settled by the user — one app-wide `sound.music`**, Blocking 1 closed),
> `Menus and UI.md` → *How does a player delete an open game?* (`icons.trash` added in v8),
> and user answers on discovery and chrome icons.
>
> **Revised again for two user settlements.** **(1) Animation scope is marker-only**, which
> demotes the five non-marker moments to `deferred` and is **schema version 9** —
> Requirements 13, 15 and 18 carry it, Requirement 37 records it, and Requirement 12 records
> the second deliberate drift from `neon.theme.json` that it creates. **(2) Every theme is
> materialized at startup**, confirming what Requirements 8, 24 and 32.4 already assumed —
> Blocking item 4 is closed and **no requirement changed**.
>
> **Revised again for a third user settlement — `*Style` is an inline object.** A `*Style`
> key under `surfaces.*` **carries its own colour** and is **not** a `type.scale` reference.
> Requirement 15's `surfaces` tables now carry a **Shape column** with a declared shape for
> every key, the `textStyle` shape is defined there, and the `ref` shape is **withdrawn** from
> the shapes legend — it had no referent. This is **schema version 10** (Requirement 37).
> **This closes a defect four independent reviews each identified as the root cause of most
> of this project's deadlocks**, and it was a genuine impossibility rather than an
> untidiness: under the `ref` reading, roughly twenty text elements across five PRDs had no
> reachable colour key at all, because `type.scale` carries no colour and Requirement 15
> forbids a component reading a palette key. Downstream: `P3-03` req 16 and `P4-02` req 8 are
> corrected; `P3-05`, `P4-01`, `P4-04` and `P5-01` are affected and unedited.
>
> **Schema version 10.** The last open contradiction with `Tech Design.md` closed when its
> guard table dropped the "inside board widgets" scoping; Requirement 25 and that doc now
> agree.
>
> **Revised again for a user reversal — the turn banner is built after all.** `Menus and
> UI.md` → *How to Play — the On-Board Legend and Hint* now states that the banner **is**
> built and carries the pending-move prompt. That destroys the premise v5 removed
> `surfaces.scoreboard.turnBanner` on. **The key is not restored**, because no design doc
> says what the banner needs themed, and a half-shaped row in a normative schema is the
> `*Style` deadlock again (Appendix A.2). Requirement 15's *Not in the schema* table now
> records a **gap** rather than a ruling, Requirement 37 records why **no version bump is
> owed**, and the shape is **Blocking item 8**. **Still schema version 10 — nothing about
> the schema changed.**

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

**A fourth has now bitten once, in the other direction: a key that exists is read as a
commitment to build it.** Five `animation.<moment>` keys were transcribed into the schema
from a stub in `neon.theme.json`, and `P2-04-animations.md` reasonably read six `required`
moments as six moments the game animates — against three design docs that all say the
marker is the only thing that moves. Requirement 18 records the correction. **Naming a key
does not decide its value, and it does not decide that anything reads it.**

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
   **"At startup" means *every* theme, not just the selected one — confirmed by the user.**
   Blocking item 4 asked whether materialization is eager or lazy, and the answer is eager:
   every discovered theme is materialized during the catalog build, so a `ThemeCatalogEntry`
   carries a complete `Theme` from the moment it exists. **This ratifies the requirements as
   written rather than changing them** — Requirement 24's published `ThemeCatalogEntry` type
   already carries a materialized `Theme` per entry, Requirement 32.4 already builds it that
   way, and Requirement 33's "readable without making it active" is only true if it is.
   Recorded so a later reader does not mistake the eagerness for an implementation accident
   and "optimise" it into a lazy path that breaks Requirement 33.
   **Consequence:** Neon ships `sound.music` as an explicit `null` — a deliberate clear, not
   an unfilled slot; Requirement 11's check treats it as defined.
   **A list is a leaf.** A theme naming a list **replaces it whole**. *PRD-author judgment:
   there is no stable identity for "the second keyframe."*
   **`meta` does not merge.** `meta.id`, `meta.name` and `meta.blurb` are never inherited.
   **Testable:** a theme overriding `color.ground` alone materializes with all 42 other
   `color.*` keys at Neon's values; `sound.buttonTap: null` yields no button-tap sound; a
   theme overriding `surfaces.legend.swatchStyle.locked` alone keeps Neon's other five;
   a theme omitting `meta.name` fails to load rather than inheriting `"Neon"`; and after
   startup **every** entry in `themeCatalogProvider` resolves every `required` key without a
   further load.
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
    **The manifest shrank in v9.** It carries `animation.placeMark.*` and **no other
    `animation.<moment>` path**: the five non-marker moments are `deferred` (Requirement 15),
    and the manifest lists `required` keys only. A `deferred` key appearing in
    `required_keys.dart` is a defect — it would fail the first test against a Neon that
    correctly does not author it.
    **And it grew in v10.** Each `*Style` key is now a `textStyle` **object**, so it
    contributes its required sub-fields as separate leaf paths — `…hintStyle.size`,
    `…hintStyle.weight`, `…hintStyle.color` — where it previously contributed one. Roughly
    twenty `*Style` keys become roughly sixty entries. **`color` is the one that matters**:
    it is the field that did not exist before v10, and listing it is what makes "Neon has a
    colour for every piece of text it draws" a runnable assertion rather than a hope. The
    optional three — `tracking`, `lineHeight`, `uppercase` — are **not** manifest entries,
    since the manifest lists `required` paths only.
12. **`assets/themes/neon.yaml` is the authoritative Neon definition.** `neon.theme.json`
    stays as it is and is a **reference**: *"the two can drift, and the YAML is authoritative
    where they differ."* **Do not "correct" the YAML back toward the JSON** — the JSON now
    carries three spacing keys the schema no longer has.

    **Two deliberate drifts now, and the second is the larger one.** Recorded together so
    nobody reconciles either by hand:

    | # | Drift | Since |
    |---|---|---|
    | 1 | The JSON carries `board.outerGap`, `board.quadrantPadding` and `board.innerGap`; the schema does not | v7 — spacing is code, not theme |
    | 2 | The JSON's `animation` block carries **six** moments; the YAML authors **one**, `placeMark` | v9 — animation scope is marker-only (Requirement 18) |

    The second drift matters more than its size suggests, because it is the one that already
    caused a defect in the other direction: the five extra moments were transcribed *out* of
    that stub and into the schema, and were then read downstream as six moments the game
    animates. The JSON is a starting-value reference and `Animations.md` → Where Animations
    Fire says so in as many words — *"Starting values, in the handoff's own words — not
    decisions."* Transcribing from it is Requirement 13(a)'s job **only for keys the schema
    still carries**.
13. **What `assets/themes/neon.yaml` must contain — and the two ways a value gets there.**

    **(a) Transcribed — the large majority.** Every value the approved design draws *that the
    schema still carries*, copied faithfully. Two read-only sources, neither edited:

    | Source | What comes from it |
    |---|---|
    | `neon.theme.json` | `id`, and every key in `color`, `marks`, `type`, `radius`, `sound`; the `board` keys the schema retains; and **`animation.placeMark`'s duration and easing only** |
    | `README.md` and `themes.catalog.json` | everything drawn in the token tables, board sections and screens `1a`–`2d` that the JSON does not carry — the pending-move colour and its rings, grid-line opacity and glow, the claimed and cat-game glows, the cat caption, the modal and sheet surfaces, the scrims, the settings card, the game rows and chips, the theme rows and badges, the menu, the buttons, the input field, the legend typography and its six swatches, the free-choice cue, the scoreboard chips, the five drawn chrome icons, and Neon's `name` and `blurb` |

    **The JSON's other five `animation` moments are not transcribed** — `claimQuadrant`,
    `catGame`, `winGame`, `activeQuadrant`, `lastMove`. They are `deferred` (Requirement 15)
    and Requirement 12's second drift is exactly this. **Do not author them "for
    completeness":** Requirement 18 records what happened the last time they were treated as
    content rather than as a stub.

    **No value is invented, altered or rounded.** Composites are restructured per
    Requirement 35 and motion re-expressed per Requirement 18.

    **New in v10 — every `*Style` key is authored as a `textStyle` object, colour included.**
    A `*Style` leaf is a map, not a style name (Requirement 15 → `surfaces`), so each one
    needs `size`, `weight` **and `color`** transcribed. The colours are drawn and were always
    available — `1d`'s legend greys, `2a`'s sheet header, `1a`'s wordmark, `2c`'s field
    labels, the chip label and value colours — they simply had **no key to land in** until
    v10, which is the whole of the defect this version closes. **This adds no new source:**
    they come from the same README and `themes.catalog.json` row of the table above.
    Requirement 15's legend and scoreboard tables quote several of them inline so the
    transcriber has a starting point rather than a search.

    **(b) Authored — a short, named list.** Some `required` keys have **no drawn source at
    all**: the design settled the affordance without the handoff ever drawing it. These are
    still `required`, and this is the exhaustive list:

    | Key | Why there is nothing to copy | Settled by |
    |---|---|---|
    | `icons.trash.*` | Handoff `1b` predates the delete decision; no trash glyph is drawn anywhere | `Menus and UI.md` → How does a player delete an open game? |
    | `surfaces.destructive.*` | Same drawing, same gap — the revealed control's panel and the modal's Yes button | as above |
    | `animation.placeMark.tracks[].keyframes[].value` | The handoff gives a duration and an easing but never says *how far* the mark grows | `Animations.md` → Themes describe their animations |

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
    | `sound.music`'s **value** | The key's shape is settled (Requirement 17) and Neon ships an explicit `null`; **what audio goes there** is not this PRD's — *"where the audio comes from"* is still open in `Theming.md` → Open Questions, alongside Neon's five `"TODO"` one-shots (*Blocking* item 2) |
    | `animation.{claimQuadrant,catGame,winGame,activeQuadrant,lastMove}.*` | **New in v9.** Animation scope is the player's marker only, settled by the user. `Animations.md` → Where Animations Fire lists these as *"the obvious moments"* and hedges them as *"not yet decided in detail"*, so the moments are kept in the contract by name and authored by nobody. See Requirement 18 |

    **Testable:** every leaf in `neon.yaml` traces to a source in (a) or appears in (b)'s
    table, Requirement 11's manifest resolves completely, and `neon.yaml` contains **no**
    `animation` key other than `animation.placeMark`.
14. Neon's UUID is `b7c1f0a6-2f5e-4d3a-9c88-0f5a1e2d3c40`, and Neon is both the base theme
    and the default active theme.
    *(`neon.theme.json` → `id`; `themes.catalog.json` → `baseThemeId`, `defaultThemeId`;
    `Menus and UI.md` → Decisions → Which theme is active by default?)*

### Requirement 15 — the schema

15. **This is the theme schema. Every key a consumer reads is named here, with its value
    shape and its status.** Naming a key does not decide its value, **and it does not decide
    that anything reads it** — see Requirement 18.

    **Status:** `required` — Neon must hold a value; transcribed unless Requirement 13(b)
    lists it as authored. `deferred` — in the contract, nothing drawn and nothing settled.
    `undecided` — **do not implement**, pending *Blocking*.

    Shapes: `color` = `#rrggbb` or `rgba(r,g,b,a)`; `dp` = logical pixels; `ms` = integer
    milliseconds; `assetPath` = a path under `assets/`, or null; `textStyle` = **an inline
    object carrying its own colour**, defined in the `surfaces` section below.

    **The `ref` shape is withdrawn in v10.** Earlier drafts listed `ref` = *a `type.scale`
    style name* in this legend, and **no key in this schema ever used it** — it was a
    vocabulary entry with no referent, and every consumer that met a `*Style` key had to
    guess which reading applied. The `surfaces` section now declares a shape for every key,
    which is what closes the guess. See *Why `*Style` is an inline object* there.

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
    | `meta.schemaVersion` | integer — **10** | Requirement 37 |
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
    | `board.catCaption` | **`textStyle`** — the same object; it was already spelled `{size, weight, tracking, color}` longhand here before v10 named the shape | README |

    `outerGap`, `quadrantPadding` and `innerGap` are **not here** — fixed in code.

    #### `sound` — seven keys, five playable one-shots

    `sound.{placeMark,claimQuadrant,catGame,winGame,buttonTap}` (`assetPath`, **required**,
    values are prose `"TODO"` today); `sound.signature` (string, **metadata, never played**);
    `sound.music` (`assetPath` or null — **one track for the whole app, settled by the
    user**; Neon ships an explicit `null`). See Requirement 17.

    **The sound moments and the animation moments are no longer the same list, and that is
    deliberate.** Five sounds, one animation. `P3-02-move-input.md` reqs 32–33 fire
    `claimQuadrant` and `catGame` as *sounds* on a commit; nothing fires them as motion.
    A reader who notices the asymmetry and "fixes" it is re-creating the v9 defect from the
    other end — `P3-02` req 33 states the same warning from its side.

    #### `animation` — a motion **description**, not a behaviour name

    **One moment is in scope: `placeMark`.** Animations apply to **the player's marker** and
    to nothing else, settled by the user. Four independent sources say so and none says
    otherwise: `Animations.md` → Scope For Now (*"animations apply to **the player's
    marker**… The marker is the thing that moves"*), `Theming.md` → What a Theme Controls →
    Animation (*"The animation set applied to the player's marker"*), `Game Board Design.md`
    → Animation & Juice (*"currently scoped to the player's marker"*), and the approved
    handoff's own summary — `design_handoff_game_ui/README.md` → *Interactions & behavior*:
    *"**Animations** (from `Animations.md`): poppy, **marker-only**, one at a time, never
    blocking input."*

    | Key path | Shape | Status |
    |---|---|---|
    | `animation.placeMark.duration` | `ms` | **required** |
    | `animation.placeMark.repeat.{count,mode}` | integer \| `infinite` / `restart` \| `reverse` | **required** |
    | `animation.placeMark.tracks` | list of track objects, ≥ 1 | **required** |
    | `…tracks[].{property,easing}` | closed set (Req 18) / easing string | **required** |
    | `…tracks[].delay` | `ms` | optional |
    | `…tracks[].keyframes` | list of ≥ 2 `{at, value}` | **required** |
    | `…keyframes[].at` | 0.0–1.0, fraction of `duration` | **required** |
    | `…keyframes[].value` | number, or `color` | **required — authored** |
    | `…keyframes[].easing` | overrides the track's for the segment ending here | optional |

    `<moment>` ∈ `placeMark`.

    **The five non-marker moments are `deferred`, not deleted:** `claimQuadrant`, `catGame`,
    `winGame`, `activeQuadrant`, `lastMove`. They keep the same shape as `placeMark` if they
    are ever authored, Neon authors none of them (Requirement 13), Requirement 11's manifest
    lists none of them, and **`P2-04-animations.md` plays none of them** — its
    `AnimationMoment` enum has one value. They stay named because `Animations.md` → Where
    Animations Fire still lists them as *"the obvious moments"* under an explicit *"Not yet
    decided in detail"* hedge, so deleting them would assert a closure the docs have not
    made. Promoting one later is a `required` status change, a Neon authoring pass, an
    `AnimationMoment` value and a `meta.schemaVersion` bump under Requirement 37 — a known,
    bounded change, not a redesign.

    #### `surfaces`

    **Why `*Style` is an inline object — settled by the user, and the root cause of most of
    this project's deadlocks.** Every `*Style` key under `surfaces.*` is an **inline object
    that carries its own colour**. It is **not** a `type.scale` style name.

    The two readings were live for nine schema versions, and the `ref` reading is not merely
    uglier — it is **impossible**, by this PRD's own Appendix A.2 triage rule:

    - `type.scale.<style>` carries `{size, weight, tracking, lineHeight, uppercase}` and
      **no colour field**. It never had one; the `type` section above is the whole of it.
    - This section's own rule forbids the escape: *"A component reads its own `surfaces.*`
      or `icons.*` key, never a palette key that happens to hold the same value."* So a
      component may not reach `color.text` to colour a `*Style` either.
    - Therefore, under `ref`, roughly **twenty text elements across five PRDs have no
      reachable colour key at all** — the legend's five styles, the sheet header's two, the
      four toggle-row labels, the game row's title and time, the menu's four, the input's
      three, and the scoreboard chips' label and value. That is *impossible*, not *ugly*:
      there is no implementation an author could write that both renders text and passes
      the build. Only that class blocks (Appendix A.2).

    **Two things inside this PRD already assumed inline**, which is the strongest evidence
    that `ref` was a drafting slip rather than a decision: the legend table below annotates
    `surfaces.legend.freeChoiceCueStyle` as *"12/400 `#4fc3ff`"* — a colour a `type.scale`
    name cannot carry — and `board.catCaption` is spelled out longhand as
    `{size, weight, tracking, color}`, which is exactly this shape under another name.

    **The `textStyle` shape.** Every key below whose Shape reads `textStyle` is this object:

    | Field | Shape | Required |
    |---|---|---|
    | `size` | `dp` | **yes** |
    | `weight` | integer — one of `type.weights.*`'s values | **yes** |
    | `color` | `color` | **yes** — the field the `ref` reading could not supply |
    | `tracking` | number, em | optional |
    | `lineHeight` | number, multiplier | optional |
    | `uppercase` | bool | optional |

    A `textStyle` **duplicates** the numbers a `type.scale` entry would have carried, and
    that duplication is deliberate and permanent: Requirement 35 fixes that this schema has
    **no alias or reference type**, so a hand-duplicated derivation is the only mechanism
    available. `type.scale.*` does not disappear — it stays the published type ramp, read
    directly by the consumers that read it directly (`P3-01`'s marks, `P4-03`'s modal), and
    it is the **documentation** of where a `textStyle`'s numbers came from. It is not a
    lookup a `*Style` performs at runtime.
    **Consequence for `P5-01`:** a `textStyle`'s `color` is a colour leaf, so it is inside
    that PRD's Requirement 6 derivation walk like any other.

    | Key path | Shape | Status | Drawn in / consumer |
    |---|---|---|---|
    | `surfaces.modal.{fill,border,winnerBorder}` | `color` | **required** | `1f`–`1h` / `P3-04` reqs 10, 13; **reused by the delete confirmation** |
    | `surfaces.modal.radius` / `.shadow` | `dp` / shadow list | **required** | as above |
    | `surfaces.sheet.fill` / `.radius` | `color` / `dp` | **required** | `1f`, `2a`, `2c` |
    | `surfaces.sheet.header.{titleStyle,subStyle}` | **`textStyle`** | **required** | `2a` / `P4-03` req 3, `P4-02` req 8 |
    | `surfaces.sheet.header.closeControl` | `{fill, radius, size: dp}` | **required** | `2a` / `P4-03` req 3 |
    | `surfaces.scrim.{modal,settings,themeSelect,namePrompt}` | `color` | **required** | `1f`–`1h`, `2a`, `2c` |
    | `surfaces.settingsCard.{fill,border}` / `.radius` | `color` / `dp` | **required** | `2b` / `P4-04` reqs 6, 16 |
    | `surfaces.settingsCard.toggleRow.{labelStyle,subLabelStyle}` | **`textStyle`** | **required** | `2b` — four rows, one of them Music |
    | `surfaces.settingsCard.switch.{trackOn,trackOff,knobOn,knobOff}` | `color` | **required** | `1f`, `2b` |
    | `surfaces.settingsCard.switch.glowOn` | shadow list | **required** | `1f`, `2b` |
    | `surfaces.settingsCard.purchases.{sectionDivider,priceRow,restoreControl}` | — | **deferred** | nothing drawn, no Decision on treatment |
    | `surfaces.gameRow.fill` / `.radius` | `color` / `dp` | **required** | `1b` / `P4-02` reqs 4, 17, 18 |
    | `surfaces.gameRow.{titleStyle,timeStyle}` | **`textStyle`** | **required** | `1b` / `P4-02` req 27 |
    | `surfaces.gameRow.chip` | `{fill, border, radius: dp, labelStyle: textStyle}` | **required** | `1b` / `P4-02` req 18 |
    | `surfaces.gameRow.chipYouOutline` / `.chevron` | `color` / `color` | **required** | `1b` |
    | `surfaces.themeRow.fill` / `.radius` | `color` / `dp` | **required** | `2a` / `P4-03` reqs 6, 8, 13 |
    | `surfaces.themeRow.previewTile` | `{radius: dp, border}` | **required** | `2a` |
    | `surfaces.themeRow.activeRing` | ring object (Req 35) | **required** | `2a` |
    | `surfaces.themeRow.lockedPreviewOpacity` | number | **required** | `2a` |
    | `surfaces.badge.{free,owned,active,priceAction}` | `{fill, border, radius: dp, labelStyle: textStyle}` | **required** | `2a`, `themes.catalog.json` |
    | `surfaces.menu.background` | gradient (Req 35) | **required** | `1a` / `P4-01` reqs 7, 13 |
    | `surfaces.menu.{kickerStyle,wordmarkStyle,taglineStyle,footerStyle}` | **`textStyle`** | **required** | `1a` / `P4-01` reqs 7, 13 |
    | `surfaces.menu.wordmarkGlow` | shadow list | **required** | `1a` |
    | `surfaces.menu.logo` | `assetPath` — **required** slot; asset is a placeholder | **required** | `1a` / art by `P5-02` |
    | `surfaces.menu.dimBehindOverlay` | `color` | **required** | `2a` (35%) |
    | `surfaces.button.{primary,secondary}` | `{fill, border, borderWidth: dp, radius: dp, labelStyle: textStyle, glow, innerGlow}` | **required** | `1a`, `2c` / `P4-01` reqs 4, 6 |
    | `surfaces.input.{fill,focusBorder,caret}` | `color` | **required** | `2c` / `P4-02` reqs 8, 9, 17 |
    | `surfaces.input.radius` | `dp` | **required** | `2c` |
    | `surfaces.input.{valueStyle,labelStyle,counterStyle}` | **`textStyle`** | **required** | `2c` / `P4-02` reqs 8, 9 |
    | `surfaces.placeholder.border` / `.radius` / `.glow` | `color` / `dp` / shadow list | **required** | `1a`'s logo **and** `1c`'s avatars |
    | `surfaces.focusRing` | ring object (Req 35) | **required** | README → *Interactions & behavior* |

    **`surfaces.button.{primary,secondary}`'s shape answers a question `P4-01` raised and
    could not close.** Its Open Questions record that the tiers need, per tier, *"border
    colour and width (2pt vs 1px), text colour and size (20pt vs 15pt, **neither in
    `type.scale`**), a `radius.*` reference, an **outer** glow **and** a separate **inset**
    glow"* — and that three consumers read the key. The sub-keys above are that list, and the
    parenthetical *"neither in `type.scale`"* is independent confirmation that a button's
    label size was never reachable by dereferencing a style name.
    **What stays open there:** the two tiers' *values*, and the pressed/focused states, which
    `P4-01` req 21 routes to `surfaces.focusRing`. Naming a shape does not author a value.

    **Two tiers of authority in the table above — do not read them as one.** The Shape column
    is new in v10 and not everything in it has the same standing:

    | Tier | Which rows | Standing |
    |---|---|---|
    | **Settled by the user** | every row whose Shape reads **`textStyle`** | The settlement is *`*Style` keys are inline objects carrying their own colour*. These rows are the settlement written out, and the `textStyle` field table is its normative form |
    | **PRD-author judgment — flagged, reversible** | the **composite** rows: `sheet.header.closeControl`, `gameRow.chip`, `themeRow.previewTile`, `badge.*`, and `button.{primary,secondary}`'s non-`labelStyle` fields | No Decision and no handoff table decomposes these. They had to be given *some* shape for the Shape column to be complete, and an under-specified composite is the same deadlock this section exists to end. `button.*` is the best-sourced of them (`P4-01`'s Open Question lists its fields); the other four are inference from what their consumers draw |

    A reviewer who disagrees with a composite row is disagreeing with **me**, not with the
    user, and changing one costs a version bump and nothing else. A reviewer who disagrees
    with a `textStyle` row is re-opening a settled question.
    **Recorded because this PRD has been bitten by the opposite mistake** — Requirement 18(a)
    and Appendix A.1b both record a case where transcribed material was later read as intent.

    **Destructive — `required`, authored (Requirement 13(b)), and reshaped in v8.**

    | Key path | Shape | Carries |
    |---|---|---|
    | `surfaces.destructive.action.fill` / `.radius` | `color` / `dp` | the **panel revealed by swiping a row left**, behind `icons.trash` |
    | `surfaces.destructive.confirmAccept.{fill,border}` / `.radius` | `color` / `dp` | the modal's **Yes** button |
    | `surfaces.destructive.confirmAccept.labelStyle` | **`textStyle`** | the word **Yes** on that button |

    **What changed and why.** The action key previously carried `labelStyle` and `icon`. Both
    are gone: the Decision specifies *"a trash button — an icon, not a worded 'Delete'
    label,"* so **there is no label to style**, and the glyph now has its own slot. A component
    key with no reader comes out — the same test `turnIndicator` failed in v6.
    **`turnBanner` is no longer an example of that test.** It was removed in v5 for the same
    reason, but the premise has since been reversed: `Menus and UI.md` → *How to Play — the
    On-Board Legend and Hint* states the banner **is** built, so it will have a reader. Its
    key is still absent only because nothing settles its shape — Open Question 8.
    **The modal's other button is not a new key.** Its choices are **Yes and No**: **Yes** is
    `surfaces.destructive.confirmAccept`, **No** is the existing `surfaces.button.secondary`,
    and the dialog's chrome is `surfaces.modal` over `surfaces.scrim.modal`.
    **Authoring brief:** deletion is *"the only irreversible action in the app — it destroys
    the game and its whole running scoreboard"* and kids are a stated target audience.

    **Legend and how-to-play strip.**

    | Key path | Shape | Status | Notes |
    |---|---|---|---|
    | `surfaces.legend.hintStyle` | **`textStyle`** | **required** | the two-tap hint — `1d`, 12/400 `#75798c` |
    | `surfaces.legend.labelStyle` | **`textStyle`** | **required** | the legend entry's text — `1d`, 10.5/400 `#595d6c` |
    | `surfaces.legend.swatchStyle.<state>` | `{fill, border, radius: dp, glow}` — **a map keyed by state**, six entries | **required** | `1d` / `P3-05` req 18 |
    | `surfaces.legend.ringExplanationStyle` | **`textStyle`** | **required** | `1e`, `2d` — 12/400 `#b2b6ca` |
    | `surfaces.legend.freeChoiceCueStyle` | **`textStyle`** | **required** | `1d` — 12/400 `#4fc3ff` |

    `<state>` ∈ `open`, `locked`, `catGame`, `lastMove`, `activeQuadrant`, `pending`.

    **`swatchStyle` is the one `*Style` key that is not a `textStyle`, and it is not an
    exception to the settlement.** A swatch is a drawn tile, not a run of text, so it carries
    `fill`, `border` and `glow` rather than `size`, `weight` and `color` — but it is still an
    **inline object carrying its own colour**, which is the settlement. Read the settlement as
    *"a `*Style` key is an inline object that carries its colour,"* not as *"a `*Style` key is
    a `textStyle`."* Its six-entry shape is `P3-05` req 18's, which spells it out and gives
    the reason one flat style cannot serve six treatments: the alternative is a hardcoded
    switch, which is bare Dart and invisible to the guard (Appendix A.1).
    **The three legend colours above are transcribed**, from `P3-05` req 18's own Neon table.
    They are quoted here because a `textStyle` now *has* a colour field and Requirement 13(a)
    must know what goes in it — under the `ref` reading these three values had no slot at all,
    which is the impossibility this section records.

    **Scoreboard chips — per player, because the states are not shared.**

    | Key path | Shape | Status | Notes |
    |---|---|---|---|
    | `…chip.playerOne.active.{fill,border}` | `color` | **required** | `1d` — fill is `rgba(255,61,113,0.14)` |
    | `…chip.playerOne.active.glow` | shadow list | **required** | `1d` — **`active` only**; `inactive` has no `glow` |
    | `…chip.playerOne.active.{labelStyle,valueStyle}` | **`textStyle`** | **required** | `1d` — label 9/0.1em, value 22/600 |
    | `…chip.playerOne.inactive.{fill,border}` | `color` | **required** | `1d`/`1e` |
    | `…chip.playerOne.inactive.{labelStyle,valueStyle}` | **`textStyle`** | **required** | `1d`/`1e` |
    | `…chip.playerTwo.active.{…}` / `.inactive.{…}` | as playerOne | **required** | `1e` |
    | `…chip.ties.{fill,border}` / `.{labelStyle,valueStyle}` | `color` / **`textStyle`** | **required** | **No active variant, by design** — `P3-03` req 7 |
    | `surfaces.scoreboard.radius` | `dp` | **required** | `1d` |

    **The chip `textStyle`s are why `P3-03` req 16 could be made decidable.** That
    requirement compares the active and inactive treatments field-wise to prove the turn
    highlight is not a no-op. Under the withdrawn `ref` reading its two type comparisons had
    to dereference a style name, so a chip whose highlight is carried **by label colour
    alone** — a perfectly good highlight, and a cheap one — compared *equal* and the
    requirement **rejected a working theme**. With `color` inside the `textStyle`, the
    comparison sees it. `P3-03` req 16 is rewritten to match.

    #### Not in the schema

    | Section | Why |
    |---|---|
    | **spacing and padding** | **Decided against** — the guard cannot verify it. Hedged *"for now"* |
    | fill patterns / textures | **not supported** — Requirement 21 |
    | `surfaces.destructive.action.labelStyle` | **removed in v8** — the control is an icon, not a word |
    | `surfaces.scoreboard.turnBanner` | **absent, but not ruled out — this row is a gap, not a ruling.** Removed in v5 because *"the banner is not built"*; `Menus and UI.md` → *How to Play — the On-Board Legend and Hint* now states it **is** built and carries the pending-move prompt, so that reason is dead. The key is not restored here because **no design doc says what the banner needs themed** — Open Question 8 |
    | `surfaces.scoreboard.turnIndicator` | **removed in v6** — no reader |
    | `surfaces.deleteDialog.*` | never existed — the confirmation reuses `surfaces.modal` |
    | a `music.<context>` map | **not taken** — the user settled music as **one `sound.music` key, app-wide**, so a per-screen map is ruled out rather than deferred. Requirement 17 |
    | haptics | Never theme-driven — Requirement 29 |
    | ownership, price | Never in a theme definition — Requirement 31 |

    The five non-marker `animation` moments are **not** in this table: they are `deferred`,
    which is a different thing. A row here is ruled out; a `deferred` key is named, shaped
    and unauthored.

16. **Marks are asset slots on the theme, not shapes drawn in board code.**
    *(`Tech Design.md` → Decisions → Marks — image or icon; `P3-01` req 17)* Neon authors a
    third kind, `glyph` — see *Blocking*.
17. **Five playable one-shot moments, plus `signature` (metadata, never played) and
    `music` — one track, app-wide.** A consumer must not treat `sound.*` as an iterable list
    of playable assets.

    **Music is a theme concern**, per `Theming.md` → Decisions → *Do all four toggles ship,
    and is music a theme concern?*, which **supersedes** *One-shot sound effects only, for
    now*. That Decision established ownership and left the shape open.

    **The shape is now settled by the user: a single `sound.music` key, app-wide, whose value
    comes from the selected theme.** One track for the whole app. Today's placeholder shape is
    therefore retained exactly as it stands — `sound.music` is `assetPath` or null, no key is
    added, nothing is re-shaped, and Neon's explicit `null` (Requirement 8) stays. The
    per-screen `music.<context>` alternative is **not taken**, and Requirement 15's *Not in the
    schema* table records it as ruled out rather than deferred.
    **Music is not a one-shot** — a one-shot fires and ends; music loops and has a lifecycle —
    so it is never another `SoundMoment`, which the settled shape does not change.
    **Nothing plays it**, but the *setting* has a consumer: `P4-04` ships a fourth toggle
    controlling it, and `P1-04` req 26 publishes `musicEnabledProvider`. The key now has a
    settled shape and no value: what audio goes in it, and whether it loops, are still open in
    `Theming.md` → Open Questions and are not this PRD's to answer.
    *(`Theming.md` → What a Theme Controls → Audio; the shape is the user's settlement
    recorded here, not a doc citation; `P2-02` reqs 6, 7, 14.)*
18. **A theme describes its motion; the runtime interprets the description.** Each moment is
    a **duration, a repeat rule and a list of tracks**.
    *(`Animations.md` → Decisions → Themes describe their animations; → Duration lives in the
    animation)*
    **The property set is closed**: `scale`, `opacity`, `glowRadius`, `glowColor`,
    `translateX`, `translateY`, `rotation`. *Blocking item 5 carries the shadowbox finding.*

    | Moment | Was | Becomes | Transcribed | Authored |
    |---|---|---|---|---|
    | `placeMark` | `grow-shrink`, 220ms, `cubic-bezier(.34,1.56,.64,1)` | one `scale` track | duration, easing | scale magnitudes |

    **The other five rows were withdrawn in v9, and the reasoning is worth keeping because it
    was mispriced twice.**

    **(a) They were transcribed from a stub, not authored as intent.** The v2 pass read
    `neon.theme.json → animation`'s six entries as content and re-expressed all six under
    Requirement 13(a). But every design doc that describes animation scope says the same
    thing — the marker is the only thing that moves (Requirement 15's `animation` section
    lists all four sources). **The exceedance came from the same handoff whose own prose says
    marker-only**, three lines away from the block it was transcribed out of. `Animations.md`
    → Where Animations Fire labels that block *"Starting values, in the handoff's own words —
    not decisions."*

    **(b) Carrying all six was not free, and `P2-04` req 28's claim that it was is
    withdrawn.** That requirement said playing a further moment needed "no interface change
    and no interpreter change." Two of the five break that:

    - **`activeQuadrant` and `lastMove` ship `repeat: {count: infinite, mode: reverse}`.** An
      infinitely repeating animation never ends, so it never calls `AnimationCoordinator.end`
      — and `P2-04` req 7's coordinator holds exactly one `AnimationMoment?` slot. Under that
      PRD's req 38 (a moment arriving while one plays is *dropped*) the highlight would hold
      the slot forever and **`placeMark` would never play again**. That is not a wrapper
      change; it is a second concurrency class the coordinator does not have.
    - **`winGame` is not one widget.** A win is a line of *three* claimed quadrants, so the
      moment would need three concurrent `ThemedAnimation` wrappers playing one moment —
      which `P2-04` req 14 forbids by construction and its req 38 would resolve by dropping
      two of the three.

    **(c) What it closes for free.** With no infinitely repeating moment in the schema,
    nothing contradicts `Animations.md` → Decisions → **One animation at a time**. That
    contradiction was `P2-04`'s second blocking question and it is closed by (b) rather than
    by a ruling on the Decision's wording.

    **The interpreter is `P2-04`'s**, and it stays general: it must execute any description
    the schema can express — every property, any track count, any repeat rule — because
    Requirement 9's bar is about what a theme can *describe*, not about how many moments the
    game plays. **Scope and generality are independent axes**; collapsing them re-creates the
    closed list `Animations.md` → Decisions → *Themes describe their animations* rules out.
19. **A theme supplies its own font** — `type.family`. Inter 400/500/600 is bundled as
    **Neon's font choice, not an app-wide font constant**.
20. The last-move, active-quadrant and pending-move treatments are **separately addressable
    keys**; the legend's six swatches are the same rule applied to the strip that explains
    them. **These are static treatments** — `P3-01-board-rendering.md` draws all three and
    none of them animates (Requirement 18).
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
    - **`ThemeCatalogEntry.theme` is materialized, never a promise.** The user confirmed
      startup materialization for every theme (Requirement 8), so this field is a `Theme` and
      not a `Future<Theme>` or a lazily-built getter. That was already the published type;
      the confirmation ratifies it.
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
    - **An interpolation magnitude living in Dart is a theme value that escaped.** Stated for
      motion specifically because `animation.placeMark.tracks[].keyframes[].value` is
      unauthored (Requirement 13(b)), and the tempting fix is a literal scale factor in
      `lib/animation/`. `P2-04` req 33 is that PRD's half.
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
       **Materialized then, for every entry, not on demand** — Requirement 8, confirmed by
       the user. The catalog build is where the merge cost is paid.
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
    `themeCatalogProvider`. This is the requirement startup materialization exists to serve;
    a lazy catalog would make it a load rather than a read.
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
37. **The schema is versioned. `meta.schemaVersion` is now `10`.**

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
    | 9 | **animation scope settled as marker-only**: `animation.{claimQuadrant,catGame,winGame,activeQuadrant,lastMove}` demoted from `required` to `deferred`; Neon authors `placeMark` alone; Requirement 18's table loses five rows |
    | 10 | **`*Style` settled as an inline object carrying its own colour**: the `surfaces` tables gain a **Shape column**, the `textStyle` shape is defined, and the `ref` shape is withdrawn from the legend |

    **v9 is a demotion, not a removal**, and it bumps for the same reason v3's `turnBanner`
    deferral did: `required` is a contract with Requirement 11's manifest and with Neon's
    contents, and both changed. A consumer compiled against v8 would look for five keys Neon
    no longer holds.

    **v10 bumps, and the call is worth showing rather than asserting**, because it is the
    first bump for something that could be argued as a *clarification* — nothing was ever
    authored under the `ref` reading, so arguably nothing changed. It bumps anyway, under
    this requirement's own established rule: **a bump is owed when a key path, a value shape
    or a status changes; it is not owed when only a meaning does.**

    | Precedent | Bumped? | Why |
    |---|---|---|
    | v9 — animation demotion | **yes** | status changed, so Requirement 11's manifest and Neon's contents changed |
    | the music Decision | no | *"changed what `sound.music` means without changing a key path"* |
    | music's shape settlement | no | *"kept the key path it already had"* |
    | startup materialization | no | *"changed no key, no shape and no status"* |
    | `glyph` as a third mark `kind` | no | the set was already written that way — no structural change |
    | **v10 — `*Style` as inline object** | **yes** | **shape**, squarely |
    | **the turn-banner reversal** | **no** | **no key, shape or status changed.** The design docs reversed *whether the banner is built*, not what the schema holds; `surfaces.scoreboard.turnBanner` was absent before and is absent after |

    **It is a shape change, not a meaning change, and the distinction is mechanical.** Under
    `ref`, `surfaces.legend.hintStyle` is a **string** — one YAML scalar, one leaf. Under
    `textStyle` it is a **map** with three required sub-fields. Neon's `neon.yaml` is
    materially different text under the two readings, and Requirement 11's
    `required_keys.dart` gains roughly sixty leaf paths that did not exist as paths before
    (`…hintStyle.size`, `…hintStyle.weight`, `…hintStyle.color`, and the same for every other
    `textStyle`). That is precisely the v9 test — *a contract with Requirement 11's manifest
    and with Neon's contents, and both changed* — and it is met twice over.
    **The clarification argument is real and still loses.** Its strongest form is that no file
    exists to migrate. But v9 had no file to migrate either and bumped regardless, because the
    version is a contract with *consumers*, not a migration counter. Seventeen PRDs cite this
    schema and several quote a version number in prose; a bump is the only mechanism that
    makes them re-read rather than trust a stale quote. `P5-01`'s own Open Questions call that
    decay out by name — *"this PRD's schema references decay silently"* — and this pass found
    exactly that, twice (`P5-01` at 8, `P3-03` at 8, against a live 9).
    **The cheaper error is available here and was declined:** not bumping saves nothing, since
    no migration exists either way, and costs the one signal that tells five downstream PRDs
    their quoted key shapes are stale.
    **Still no migration**, for the reason below: Neon's file is written fresh this wave.
    **No bump for the music Decision, and none for the user's settlement of its shape** — the
    Decision changed what `sound.music` means without changing a key path, and the settlement
    kept the key path it already had. Had the `music.<context>` alternative won, this would
    have been a bump plus a migration; it did not.
    **No bump for the startup-materialization confirmation** either — it changed no key, no
    shape and no status, and Requirement 8 already said "at startup."
    **There is no migration:** the only theme file in existence is Neon's, and Requirement 13
    writes it fresh this wave.

    **No bump for the turn-banner reversal, and version row 5 stays exactly as written.**
    The design docs reversed *whether the banner is built*; they changed no key path, no
    shape and no status here, so the rule above gives no bump. Row 5 records what v5 did, and
    v5 genuinely did remove `turnBanner` — this table is a record of versions, not of what is
    currently believed, and editing row 5 would be a decision log run backwards. The reversal
    is recorded where it belongs instead: as a **gap** in the *Not in the schema* table and as
    **Blocking item 8**. **A version row becomes owed the moment item 8 is answered**, when a
    key path with a declared shape and status enters the schema and Requirement 11's manifest
    gains leaf paths — the v9 test, met. Noted here so the next author bumps then, not now.

## Out of Scope

- **The guard test** — `P1-05`. **Persistence** — `P1-04`. **Entitlements** — `P1-07`.
- **The delete flow itself** — the swipe gesture, the trash button's behaviour, the modal's
  copy, and what deleting does to storage: `P4-02`. This PRD supplies the glyph slot and the
  two destructive treatments.
- **Playing music** — no PRD owns it yet. The key's shape is settled here (Requirement 17);
  the layer that starts, loops and stops a track is nobody's, and `P2-02` req 15 records what
  such a layer inherits from the audio layer.
- **The settings screen and its four toggles** — `P4-04`.
- **All spacing and layout numbers**, now code constants.
- **The animation interpreter** — `P2-04`. **The audio layer** — `P2-02`.
- **Which moments the game animates.** This PRD says what a theme may *describe* and what
  Neon *authors*; `P2-04` req 2 holds the marker-only scope on the runtime side and its
  `AnimationMoment` enum is the executable form of it. The two must agree, and Requirement 18
  records what happened when they did not.
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

### A.1b The near-miss the guard cannot see at all — a key nobody should have read

Every row above is a consumer reading the *wrong* key. v9 records the opposite failure: a
consumer reading a key that resolves perfectly, holds a faithfully transcribed value, and
**should never have been read**. Five `animation.<moment>` keys were `required`, Neon
authored them, `required_keys.dart` would have asserted them, and every test would have been
green — while the app animated five things three design docs say it does not animate.

No scan catches this, because there is nothing wrong with the code. The only defence is the
one Requirement 15's header now states outright: **naming a key does not decide that anything
reads it.** A `required` status is a claim about Neon's completeness, not a work item.

### A.2 Authored, not transcribed — and the two weights of "missing"

Requirement 13(b) is the normative list. The distinction worth carrying: **`icons.trash` is a
deadlock, the other two are debt.** An unauthored `surfaces.destructive` fill renders as
something and ships; unauthored animation magnitudes leave the mark's pop looking flat. A
missing glyph has no legal implementation at all — no slot to read, no literal permitted.

**The triage rule this produces, for every future `deferred` call:** ask whether the absence
is *ugly* or *impossible*. Ugly can wait for a design pass — the feature ships, looks wrong,
and is fixed by authoring one value later with no code change, because the key already exists
and the consumer already reads it. Impossible cannot wait at any price: there is no
implementation an author could write that both satisfies the requirement and passes the
build, so the feature does not ship at all and no amount of scheduling helps. **Only the
second kind blocks.** Applied to what is open now: `surfaces.settingsCard.purchases.*` is
ugly — `P4-04` can render its section unstyled — music's remaining gap is neither, because
nothing plays it yet and its key now exists with a settled shape, and the five deferred
animation moments are neither, because nothing requests them.

**The largest instance of *impossible* this rule has caught was not a missing key — it was an
ambiguous shape, and it went unnoticed for nine versions.** `icons.trash` was one glyph in one
PRD and was found in a single pass. The `*Style` ambiguity (v10) was roughly twenty text
elements across five PRDs, and it hid because **every individual key existed**: a reader
checking completeness found `surfaces.legend.hintStyle` present and `required` and moved on.
Only when the two readings were written out side by side did it become visible that one of
them left no colour anywhere — `type.scale` has no colour field, and this section's own rule
bars the palette fallback. **Four separate reviews reached that conclusion independently**,
which is the strongest signal available that it was structural rather than a matter of taste.
**The rule this adds to A.2's triage:** ask *impossible or ugly* about a key's **shape**, not
only about its presence. A key that exists but cannot express what its consumer must draw is
in the impossible class, and completeness checks — including Requirement 11's manifest — are
blind to it by construction, because they assert that a path resolves and never that the
value at it is sufficient. Appendix A.1b makes the neighbouring point from the other side: a
path resolving is not evidence that anything should read it.

---

## Open Questions

**None of the below blocks a landed consumer from compiling against this PRD** — every
requirement here stands as written whatever the answers are. Item 7 is the closest of the
*ugly* ones: `P4-04` can build its purchases section but has no styling source for it.

**Item 8 is the exception and is a different class.** It does not block this PRD, whose schema
is unchanged, but it is *impossible* rather than *ugly* by A.2's rule for whoever builds the
turn banner: there is no slot to read and no literal permitted, so that work has no legal
implementation until the item is answered.

### Blocking — needs the user

1. **CLOSED — what shape does a theme's music take?** **Answered by the user: a single
   `sound.music` key, app-wide, whose value comes from the selected theme.** In the user's
   words: *"ONe sound.music app wide baised on selected theme."* That is the first of the two
   candidates this item carried — today's placeholder shape, retained — and the per-screen
   `music.<context>` map is **not** taken.

   | Shape | Reading | Outcome |
   |---|---|---|
   | `sound.music: assetPath \| null` — today's placeholder | one track for the whole app | **chosen** |
   | `music.<context>: assetPath \| null` | per-screen tracks | not taken |

   **What this changes here:** Requirement 17 states the shape rather than deferring it,
   Requirement 15's `sound` section drops its "final shape open" qualifier, Requirement 15's
   *Not in the schema* table records `music.<context>` as ruled out rather than "not yet",
   Requirement 13's deferred table now defers the *value* rather than the shape, and
   Requirement 37 confirms there is no version bump and no migration — which is exactly the
   cost this item said the other answer would have carried. **What it changes elsewhere:**
   `P2-02-audio.md` and `P5-01-classic-theme.md` both routed their music questions here.
   Kept as a numbered stub because both cite this item by number.

   **Still open, and not settled by this answer:** *whether music loops* and *where the audio
   comes from* — both worded as `Theming.md` → Open Questions words them. *Whether it differs
   by screen* **is** answered: it does not.
   **Owed to the docs:** `Theming.md` → Decisions → *Do all four toggles ship, and is music a
   theme concern?* still leaves all three sub-questions open; one of them is now closed. That
   doc edit is `forge-doc-writer`'s.
2. **What goes in Neon's five `"TODO"` sound values.**
3. **What counts as "fails to load" beyond Requirement 32's table, and what happens if
   *Neon* fails?**
4. **CLOSED — are all themes materialized at startup, or only the selected one?**
   **Confirmed by the user: all of them, at startup.** This is what the requirements already
   assumed, so **nothing changed** — the item is recorded as a ratification rather than an
   amendment.

   | Requirement | Why it already depended on the eager answer |
   |---|---|
   | 8 | *"Each theme is materialized into a complete theme **at startup**… at runtime every lookup hits a complete theme and there is no fallback step"* |
   | 24 | `ThemeCatalogEntry` carries a `Theme`, not a `Future<Theme>` and not a lazy getter — one materialized theme per catalog entry |
   | 32.4 | the catalog entry *is* `{id, name, blurb, assetKey}` **plus the materialized theme**, built during the scan |
   | 33 | "readable without making it active" is a read, not a load — which is only true if the merge already happened |

   **What the lazy answer would have cost, recorded so the closure is legible:** Requirement
   24's published type becomes `Future<Theme>` or a lazy getter, which reaches `P4-03`'s
   theme-selection list — it renders every non-active theme's preview from
   `themeCatalogProvider`, so a lazy catalog turns a build into an async load with a loading
   state per row. Requirement 33 would have needed rewording rather than merely holding.
   Kept as a numbered stub because Requirement 8 and this PRD's header both cite it.

   **What this does not settle:** *when* the catalog build runs relative to first frame, and
   what the app shows if it is slow. Nothing measures it and no doc raises it; recorded as an
   observation, not a question.
5. **Does the animation property set need an eighth member?** `P2-04` reports **shadowbox has
   no obviously right property** — it maps onto `glowRadius`/`glowColor`, but a drop shadow
   that lifts the marker off the board is *directional and offset*.
   **Unaffected by v9, and slightly sharper because of it.** Shadowbox is a *marker*
   treatment — `Animations.md` → The Animation Vocabulary → Shadowbox describes it as lifting
   the marker off the board — so it sits squarely inside the settled marker-only scope. It is
   one of the five vocabulary items a theme is meant to be able to compose for `placeMark`,
   and it is the one the closed property set cannot express as drawn.
6. **CLOSED — is `glyph` a third mark `kind`?** **Confirmed by the user: yes. The closed set
   is `glyph | icon | image`, exactly as Requirement 15's `marks` section already writes
   it**, and Neon's three marks — `✕`, `○`, `Ø` — stay drawable as glyphs. Requirement 16's
   "Neon authors a third kind" is therefore **ratified rather than provisional**.

   **What this changes here: nothing structural.** The schema already carried the three-member
   set, so there is no key change, no shape change, and **no version bump** (Requirement 37) —
   the same reasoning item 1 records for the music settlement. Requirement 15's `marks` row
   and Requirement 16 both point at *Blocking*, so this item is kept as a numbered stub rather
   than renumbered away.
   **What it changes elsewhere:** `P1-05-theme-guard-test.md`'s `mark-glyph` rule needed no
   adjustment — the compliant read is `marks.<slot>.value`, an expression, and the rule matches
   only a literal. `P3-01-board-rendering.md` req 17's per-`kind` size table already treats
   `glyph` as one of the three.
   **Owed to the docs:** `Tech Design.md` → Decisions → *Marks — image or icon, supplied by the
   theme* still says *"an image or an icon"* and does not carry the third kind; `Theming.md` →
   Decisions → *Marks beyond X and O* is settled by that same Decision and inherits the gap.
   Those doc edits are `forge-doc-writer`'s.
7. **Should `surfaces.settingsCard.purchases.*` become `required` (authored)?** It sits where
   `surfaces.destructive` sat — a required reader and a settled placement, but nothing drawn,
   and no Decision describes what the section *is*.
8. **The turn banner is built again — what does it need from the theme?**

   `Menus and UI.md` → *How to Play — the On-Board Legend and Hint* now states: *"The turn
   banner is built, and it carries the pending-move prompt"* — the two lines *"Play here?"*
   and *"Tap again to lock it in."* shown when a player taps a square to preview a move
   before confirming it. **That settles that the banner exists and what prompt it carries.
   It does not settle what a theme has to define for it**, and no other design doc does
   either — `Theming.md` never names the banner, and `Game Board Design.md` mentions it only
   to say the free-choice cue does *not* live there.

   So `surfaces.scoreboard.turnBanner` is **not** restored. Two things have to be known
   before a key path can be written, and neither is answerable by reading:

   1. **Is the banner on screen for the whole game, or only while a move is pending?** This
      decides the key count, not just its values. *Pending-only* needs one neutral treatment
      and the two prompt lines. *Always-on* needs a per-player set as well — the scoreboard
      chips already pay that cost, one `active` and one `inactive` treatment per player,
      because a shared one could not express the turn highlight.
   2. **What does the banner draw besides the two prompt lines?** The two lines are settled;
      nothing else about the banner's contents is. Whether it also carries a whose-turn line,
      a swatch or a mode cue each adds its own slot, and the design docs name none of them.

   **Why this PRD will not answer it from the drawings.** `design_handoff_game_ui/README.md`
   draws a banner on `1d`, `1e` and `2d`, with a per-player tint, a *"Player One, you're
   up!"* line and a mode cue on the first two, and a neutral dashed treatment with the two
   prompt lines on `2d`. Transcribing that would answer both questions above by accident and
   in the *always-on, four-element* direction. **This PRD has been bitten by exactly that
   before** — Appendix A.1b records five animation keys that were `required`, authored and
   green while the app animated five things the docs say it does not animate, and the rule
   that came out of it is that the handoff is a **drawing, not a decision**. Requirement
   13(a) scopes transcription for the same reason.

   **What it costs to leave open.** Nothing in this PRD, and nothing in wave 1 — the schema
   is unchanged and no requirement moves. It is *impossible*, not *ugly*, for whoever builds
   the banner: with no slot to read and no literal permitted (`Theming.md` → *Architectural
   Rule*), there is no legal implementation, so that work cannot ship rather than shipping
   unstyled. Answering it costs a version bump and Neon authoring one block (Requirement 37).

   **What the answer changes here:** a new `surfaces.scoreboard.turnBanner` block in
   Requirement 15, its row leaving the *Not in the schema* table, a `required`/`deferred`
   call, Requirement 13's Neon contents, Requirement 11's manifest, and a schema version row.

### From the design docs — carried, not resolved

- **What form does the legibility contract take?** Unfalsifiable as written.
- **What does an absent `tracking`, `lineHeight` or `uppercase` resolve to?** **Raised by
  `P3-03` req 16 and still open — v10 sharpens it rather than answering it.** Requirement
  15's `textStyle` table declares all three optional and states **no fallback for any of
  them**, exactly as the `type.scale` entry did before it. `P3-03` compares them as nullables
  (*absent equals absent; absent never equals an explicit value*) because that is decidable
  today, and explicitly records that *"absent == 1.0" is not derivable from any document*.
  **The gap is not the comparison — it is paint time:** a renderer handed a `textStyle` with
  no `lineHeight` still has to pass Flutter *something*, and what that something is is
  unstated. Deliberately not answered here; picking a default would settle by accident the
  question `P3-03` was careful to leave open. Note this is now a **`surfaces.*` question as
  well as a `type.*` one**, since v10 puts the same three optional fields on every
  `textStyle`.
- **Which values does Classic Red vs Blue override?** Owned by `P5-01`; the music position it
  was holding open now has a key shape to write against (Blocking 1 is closed), though not a
  value, and its req 12 needs revisiting against Requirement 21. **v9 shrinks its animation
  surface**: a theme that wants its own motion personality now overrides one moment, not six.
- **Where animations fire, beyond the marker.** `Animations.md` → Where Animations Fire lists
  claiming a quadrant, cat game, winning the game and the two highlights as *"the obvious
  moments"* under an explicit *"Not yet decided in detail."* The marker-only settlement fixes
  the **scope of this version**; it does not rule on whether those moments are ever animated.
  Requirement 15 keeps all five `deferred` for exactly that reason.
- **Unknown or misspelled keys inside a valid theme file** — Requirement 32 catches malformed
  files and bad versions, not bad keys inside a good one.
- **Resolved earlier:** spacing and padding (v7), the three lookup paths (Requirement 24),
  theme discovery and per-file name/blurb (Requirement 32), chrome icons, and the
  `Tech Design.md` guard-table scoping — its table now reads *"`Icons.*` anywhere
  outside the theme layer"*, so nothing is outstanding against Requirement 25.
  **The turn banner has left this list.** It was resolved in v5 on a premise the design docs
  have since reversed, and is now Blocking item 8.
- **The exact slot schema.** Requirement 15 is this PRD's answer, structure ratified. Writing
  it, the chrome-icon Decision, the spacing boundary and now the settled music shape into
  `Theming.md` is `forge-doc-writer`'s to route.

### Contradiction between docs — flagged, not resolved

- **How many themes the selection list shows** — the handoff's *2a* draws four,
  `Theming.md` says two. `P4-03` → OQ 1 carries it; Requirement 32 is indifferent.
- **`P2-02-audio.md` reqs 14 and 15 were written under a superseded stance** — "no background
  music in this version" no longer holds. That PRD has since reconciled reqs 14 and 15 against
  the music Decision, so this flag is stale and can be dropped on the next pass.
- **The handoff's `neon.theme.json` still draws six animation moments** and its own prose
  still says marker-only. That contradiction is *inside a read-only reference asset* and is
  not edited: Requirement 12 records it as a deliberate drift and Requirement 13(a) scopes
  transcription so nobody re-imports it. Flagged rather than reconciled because the file is a
  reference, not a source.

### Owed to the design docs — `forge-doc-writer`'s, not this PRD's

- **`Animations.md` → Scope For Now** now describes a **settled** scope rather than a
  starting one. Its Decisions section carries nine entries and marker-only is not among them,
  yet the whole doc, `Theming.md`, `Game Board Design.md` and the handoff agree on it and the
  user has confirmed it. It reads as a hedge and is not one.
- **`Animations.md` → Decisions → One animation at a time** is no longer in tension with
  anything, because the repeating moments left the schema. Worth recording there that the
  tension existed and how it closed.
- **`Theming.md` → What a Theme Controls → Animation** and **`Game Board Design.md` →
  Animation & Juice** both state marker-only in passing, in body prose, with no Decision
  behind either. Same treatment.
