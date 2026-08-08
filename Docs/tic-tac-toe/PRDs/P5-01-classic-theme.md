**Build-readiness: 86**

# PRD: Classic Red vs Blue (the second theme)

> **Status:** Draft · Source docs read: `Theming.md`, `Animations.md`, `Tech Design.md`,
> `Menus and UI.md`, `roadmap.md`, and the read-only reference asset
> `design_handoff_game_ui/` (`README.md`, `neon.theme.json`, `themes.catalog.json`).
> `Alternative Game Styles.md` is a declared parking-lot doc and was not used as a source.
>
> **Revised for build-readiness.** The deliverable is named as a file with a fenced `meta`
> block; Requirement 5 fences the override set as **key paths** from
> `P1-03-theme-system.md` Requirement 15; Requirement 6 states the **derived-value rule**
> and gives it a runnable check.
>
> **Revised again** after answers on `meta.name` / `meta.blurb`, folder-scan discovery,
> chrome icons, music being a theme concern, and spacing being fixed in code.
>
> **Revised again — Classic has a palette.** `Theming.md` → Decisions → *What are Classic
> Red vs Blue's colours?* settles the three handoff colours as **Classic's real palette, not
> placeholder swatches**, and states that every other value derives from them. Requirement 6
> now names the three anchors and the derivation obligation they carry; Requirement 15's
> failure scenario stops being hypothetical. Schema realigned to **version 8** (`icons.trash`
> added, `surfaces.destructive.action` reshaped).
>
> **Why 86:** the values now have a starting point that an agent can author from, and
> Requirement 6's check has three concrete anchors a reviewer can run by eye on a diff
> instead of an abstract rule. Not higher because Requirement 15 (legibility) still has no
> assertable form, and three questions under *Going to the user* still gate content — the
> splat's slots, the marks, and Classic's music.

**Wave:** P5 · **File:** `P5-01-classic-theme.md`

**Depends on:**

- `P1-03-theme-system.md` — the Requirement 15 schema this file is authored against, the
  UUID identity, the deep-merge rule, and the complete Neon base. This PRD authors a theme
  *file*; it defines none of the mechanism. **Every key path below is quoted from that
  schema at `meta.schemaVersion: 8`.**
- `P2-02-audio.md` — plays the sound slots this theme names.
- `P2-04-animations.md` — interprets the motion descriptions this theme inherits.
- `P5-02-asset-generation-replicate.md` — produces the splat sound file and any art this
  theme needs. Same wave, so the two are sequenced by need rather than by wave.

**Ships after the screen that lists it.** `P4-03-theme-selection.md` is wave 4 and lists
this theme and renders its preview tile, name and blurb; until this PRD lands, the Classic
row has a UUID but no authored file. That screen does not wait on this PRD — it tolerates
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

There is a third problem, and it is the one this PRD's checks exist to fence. Classic
inverts Neon's ground: a light background under text, veils, scrims, glows and chrome tints
all tuned for `neon.theme.json`'s near-black `ground: "#161826"`. The schema has **no alias
or reference type** — `P1-03` Requirement 35 fixes that colours stay strings parsed at load
— so every surface value in `neon.yaml` is a *hand-duplicated derivation* of a palette
token. Setting Classic's `color.playerOne` changes the player and leaves every chip, glow,
badge, label and icon tint still holding Neon's pink at another alpha. The design doc now
names this failure in its own words: *inheriting one silently produces a red player with
pink chips.* Nothing in the repo catches it — `P1-05-theme-guard-test.md` scans `lib/` only
and disclaims validating theme-file contents outright, so **Classic ships green through the
guard no matter what is in it.**

## Goal

`assets/themes/classic.yaml` exists: a partial override over Neon, authored against the
`P1-03` Requirement 15 schema at version 8, built from Classic's three settled palette
anchors and everything correctly derived from them, inheriting every value it does not
name, and requiring no Dart change to exist. When it is done, the app has demonstrated
`Theming.md`'s claim that switching to a visually unrelated theme requires no change to
game, board or menu code — and adding a theme is, literally, dropping one file into a
folder.

**Two success conditions, and they are not the same one.** `Theming.md` → Why this matters
for the build says a theme "as small as *black → white, neon green → red*" is a complete,
working theme, and that remains true of **completeness** — the merge leaves no `required`
key unset. It is *not* a claim about **legibility**, and it predates both the
consumer-derived surface inventory and the Decision that every other Classic value *derives
from* its three anchors. A theme setting three colours is complete against that inventory
and unreadable on it. Completeness is assertable today (Requirement 12); legibility is
blocked (Requirement 15); **derivation is now assertable too, and that is new**
(Requirement 6).

## Requirements

### The artifact

1. **Classic Red vs Blue ships as the second of the two launch themes.**
   *(`Theming.md` → Decisions → How many themes ship at launch; `Menus and UI.md` → Theme
   Selection)*

2. **The deliverable is exactly one file: `assets/themes/classic.yaml`.** YAML, bundled
   with the app, alongside `assets/themes/neon.yaml`. Not user-authored, not downloaded, not
   a Dart class. **Dropping it into that folder is the whole of adding this theme** — the
   app discovers themes by scanning the folder.
   *(`Tech Design.md` → Decisions → Theme representation — data, not code; What format are
   theme files; Project structure — layer-first; `Theming.md` → Where Themes Live;
   `P1-03-theme-system.md` reqs 1–3, 12, 32)*
   *Testable:* the diff adds exactly one file under `assets/themes/` and no `.dart` file.

3. **The `meta` block is declared explicitly, never inherited.** Four keys, all literal in
   Classic's file:

   | Key path | Value | Why it is declared, not inherited |
   |---|---|---|
   | `meta.id` | `3d1a8b52-9c47-4b16-8f2e-7a5d0c9e1b34` | The theme's identity; what gets persisted and matched, never the name |
   | `meta.schemaVersion` | `8` | See below — omitting it, or holding a stale one, is a load failure |
   | `meta.name` | Classic's own display name | Inheriting would make Classic call itself "Neon" in the selection list |
   | `meta.blurb` | Classic's own one-line description | Same |

   *(`Tech Design.md` → Decisions → Theme identity — UUID;
   `design_handoff_game_ui/themes.catalog.json` → Classic's `id`;
   `P1-03-theme-system.md` reqs 4, 15 (`meta`), 32, 37)*

   **`meta.schemaVersion` is a load-failure trap, and this PRD has already fallen into it
   once.** The key is `required`. Under the deep-merge rule (`P1-03` req 8) an absent key
   reads as "inherit Neon's", which looks harmless — but `P1-03` req 37 has the loader
   **reject any file whose version it does not understand**, and req 32 excludes such a file
   from the catalog entirely. That check runs *before* the merge, since the merge target
   depends on the version. So an omitted **or stale** `meta.schemaVersion` does not inherit:
   it drops Classic from the list or routes it to the failed-to-load modal and back to Neon
   (`P1-03` reqs 27, 32, 34) — **a player picks Classic and gets Neon**, the precise failure
   the Problem section exists to end.
   **This number tracks `P1-03` req 37 and has moved five times** (3 → 8, across the icons,
   name/blurb, banner, destructive, spacing and trash revisions). It is the first thing to
   re-read before authoring, not a constant.
   *Testable:* `classic.yaml` appears in the catalog with no entry in the loader's failure
   report, and its literal `schemaVersion` equals `P1-03` req 37's current value.

   **`meta.name` and `meta.blurb` are declared because a theme file carries its own.** Both
   are `required`, and `P4-03-theme-selection.md` req 6 renders both on every row; `P1-03`
   req 32 excludes a file with a blank one. Under deep-merge these are ordinary keys, so an
   omitted `meta.name` would silently inherit Neon's — the one inheritance in the whole file
   that is never right.
   *(`P1-03-theme-system.md` req 15 → `meta`, req 32; `P4-03-theme-selection.md` req 6)*
   **Candidate strings, to transcribe rather than to read.**
   `design_handoff_game_ui/themes.catalog.json` holds `"Classic Red vs Blue"` and *"The
   plain old one. Red you, blue them."* That file is a **reference asset, not a shipping
   input** — nothing at runtime resolves a name or blurb from it — so those two strings are
   candidates for transcription into `classic.yaml`.
   *Testable:* with Classic listed or active, no string rendered for its row equals Neon's.

### What it overrides

4. **What it overrides is the graphics — the art and colors.** Red player, blue player, no
   black background; no neon.
   *(`Theming.md` → Theme Catalog → Theme 2 → What it overrides)*
   This is the source sentence. Requirements 5 and 6 are what it means in key paths and
   values.

5. **The override set, fenced.** *"The art and colors"* reads two ways against the version-8
   schema, and the two produce different products:

   | Reading | What it touches | What ships |
   |---|---|---|
   | **Narrow** — palette only | the 43 `color.*` keys | a red/blue board inside Neon-pink modals, chips, badges, rings and chrome |
   | **Broad** — palette plus every derived surface | `color.*`, plus every colour-shaped leaf under `surfaces.*`, `board.*`, and `icons.*.tint` | a theme that is Classic on every screen |

   The narrow reading satisfies Requirements 2, 12, 13, 14 and 16 and still produces the
   first product. **This PRD adopts the broad reading as the default override set** — and
   the Decision that *"every other value in the theme derives from"* Classic's three anchors
   is the design doc arriving at the same place:

   - **all 43 `color.*` keys** (`P1-03` req 15 → `color`);
   - **every colour-shaped leaf under `surfaces.*`** — the modal, sheet and its header, the
     four scrims, the settings card and its four toggle rows and switch, the game rows and
     their chips and chevron, the theme rows and their preview tile and active ring, the
     four badges, the menu and its wordmark glow and dim, the two buttons, the input field,
     the placeholder border and glow, the five legend styles including the six-state
     `swatchStyle` map, the focus ring, the per-player scoreboard chips in both states plus
     the ties chip, and both `destructive` groups — which after v8 means
     `destructive.action.fill` (its `radius` is geometry) and all three colour leaves of
     `destructive.confirmAccept`;
   - **every colour-shaped leaf under `board.*`** — the two quadrant shadows, the forced,
     last-move, pending-cell and pending-quadrant rings, the grid-line glow, the pending
     quadrant wash, the claimed and cat mark glows, and the cat caption colour;
   - **`icons.<slot>.tint` for all six chrome slots** — `settings`, `close`, `chevronLeft`,
     `chevronRight`, `plus` and, as of v8, **`trash`** — plus `icons.<slot>.button.fill`
     wherever a slot carries one. `icons.trash` deliberately has no `button`: the panel
     behind it is `surfaces.destructive.action`, one control with one surface owner.

   **What Classic inherits, and the boundary that decides it.** `P1-03` states the line and
   this PRD applies it: *a theme controls the drawn geometry of a thing itself — how wide
   its stroke is, how large its glyph is, how round its corners are, how far its glow
   spreads. Code controls where things sit relative to one another — gaps, padding,
   margins.* So Classic inherits every **retained** geometry key —
   `board.gridLineWidth`, `board.gridLineInsetPercent`, all `radius.*`, `type.scale.*` sizes
   and the four mark sizes, `icons.<slot>.size`, and the ring and shadow geometry — along
   with all of `animation.*` (Requirement 10) and the non-tint parts of `icons.*` and
   `marks.*`.
   **No spacing key is in the override set, because none exists.** Version 7 removed
   `board.outerGap`, `board.quadrantPadding`, `board.innerGap`, every `surfaces.*.padding`,
   `surfaces.scoreboard.gap` and the `inset` shape.
   *(`P1-03-theme-system.md` req 15 → The boundary, `icons`, Destructive; req 37 → v7, v8;
   `Theming.md` → Decisions → Does a theme control spacing and padding?)*
   The boundary is narrower than "no numbers": **grid-line width and inset and the mark
   sizes stay themeable**, so Classic can change the board's line weight and its mark art
   substantially. What it cannot do is move things apart.

   **PRD-author judgment on the *scope*, and reversible.** No Decision picks between the
   narrow and broad readings in key-path terms. The values, however, are no longer a
   judgment — see Requirement 6.
   *Testable:* every key path Classic sets resolves in the Requirement 15 schema at its
   current version (no invented keys, no removed keys), and every key path in the list above
   is either set or explicitly justified as inherited in a comment in the file.

6. **The three anchors, and the derivation obligation they carry.** Classic's palette is
   settled:

   | Anchor | Value | Replaces Neon's |
   |---|---|---|
   | Ground | `#f3f5fe` | `color.ground` `#161826` |
   | Player one | `#d92d3f` | `color.playerOne` `#ff3d71` |
   | Player two | `#2453c4` | `color.playerTwo` `#2dff9e` |

   *(`Theming.md` → Decisions → What are Classic Red vs Blue's colours? — the three handoff
   colours are **Classic's real palette, not placeholder swatches**, and *"every other value
   in the theme derives from them"*)*

   **The derivation is real work, not a copy.** Surface and icon values in `neon.yaml` are
   hand-duplicated derivations of palette tokens — the schema has no alias or reference
   type, because `P1-03` req 35 fixes colours as strings parsed at load. **So every colour
   that is a tinted or alpha-adjusted version of one of the three anchors must be recomputed
   from the new value, never inherited.** The design doc states the consequence of getting
   this wrong in its own words: *inheriting one silently produces a red player with pink
   chips.*

   The worked example, from `P1-03` req 15's scoreboard table:

   ```
   surfaces.scoreboard.chip.playerOne.active.fill      rgba(255,61,113,0.14)
                                       .border         #ff3d71   = color.playerOne
                                       .glow           0 0 16px rgba(255,61,113,0.30)
                                       .labelStyle     #ff9fb6   = color.playerOneOnTint
   ```

   Four leaves, all derived from one token. Setting `color.playerOne: "#d92d3f"` and
   stopping ships exactly the failure the Decision names.

   **And the fill is the sharpest case of all.** `P1-03` Appendix A.1 records that Neon's
   active chip fill and `color.playerOneTint` are the **same value** — `rgba(255,61,113,0.14)`
   — while `color.playerTwoTint` is `0.12`. The tints are **not symmetric.** Binding the chip
   to the palette token is invisible *and correct* today, and silently wrong the first time
   either value moves — which is precisely what authoring Classic does to both.

   **Testable, and now with concrete anchors a reviewer can run by eye on the diff:**
   collect the rgb triples of the Neon tokens Classic replaces — starting with
   **`22,24,38`** (`#161826`), **`255,61,113`** (`#ff3d71`) and **`45,255,158`** (`#2dff9e`)
   — and assert that **no leaf anywhere in the materialized Classic theme** still contains
   one of them. Generalised: for every `color.*` token Classic overrides, no Neon triple
   from that token survives anywhere in the merged object. A theme that sets the three
   anchors and leaves `rgba(255,61,113,0.30)` sitting in a chip glow fails.

   **The scope of "anywhere" is literal, and `icons.*.tint` is inside it.** The walk covers
   every string leaf of the merged object — `surfaces.*`, `board.*` **and `icons.*`** — not a
   named subset. A Classic that recolours the board and leaves the six chrome glyphs at
   Neon's tints fails, which is the intended behavior and the reason Requirement 11 puts
   those tints in the override set. This is the one check that can tell a correct Classic
   from a three-line one.

7. **Marks, board geometry and the type scale are not part of the override set by default.**
   Classic inherits `marks.*` (kind, value, font, weight), all `radius.*`, all `type.*` and
   every retained non-colour `board.*` key.
   *(`P1-03-theme-system.md` req 15 → `marks`, `type`, `radius`, `board`, and The boundary)*
   Whether Classic overrides the marks at all is open — see *Going to the user*. If it does,
   `marks.playerOne.value` and `marks.playerTwo.value` join the set and `P5-02` produces the
   art; the mark *sizes* stay themeable either way. Note that `marks.*.font` and `.weight`
   are per-mark and independent of `type.family`, so mark art can change without touching
   the type scale.

### Sound

8. **Its signature sound is a splat** — like a water balloon popping, wet and playful,
   deliberately nothing like Neon's electric buzz.
   *(`Theming.md` → Theme Catalog → Theme 2 → Sound;
   `design_handoff_game_ui/themes.catalog.json` → `signatureSound: "splat"`)*
   Concretely: `sound.signature: "splat"`.
   **This key is metadata and is never played.** `P1-03` req 17 and `P2-02-audio.md` req 7
   both fix `sound.signature` as *descriptive metadata, not an asset* — "the audio layer
   never plays it," and req 7 forbids implementing playback by iterating `sound.*`. So this
   requirement, satisfied alone, ships a theme **audibly identical to Neon**. It carries no
   *Testable* line for audible difference, because which of the five playable slots the splat
   fills is open — see *Going to the user*.
   **`buttonTap` is now the loudest of those five.** `Theming.md` → Decisions → *Do non-board
   controls make a sound?* settles **one tap sound, everywhere**: every button, row and
   toggle plays it — menu buttons, theme rows, settings toggles, the game-over card's two
   controls, the trash button, and the modal's Yes and No. So whether Classic overrides
   `sound.buttonTap` is no longer a hypothetical question about a rarely-heard slot; it is
   the sound a player hears most often in the app.

9. **Until the splat asset exists, Classic sets no playable `sound.*` key and inherits
   Neon's five placeholders.** Neon's slots hold prose `"TODO"` values today — *named but
   unloadable, never absent* (`P2-02` req 17) — and Classic inheriting them keeps its audio
   in exactly the state the rest of the app is already built against.
   **Explicitly not `null`.** Under `P1-03` req 8 a null is a *deliberate clear*, so
   `sound.placeMark: null` would make Classic silent where the design doc says it splats —
   a different bug, and a harder one to notice.
   *(`P1-03-theme-system.md` req 8, req 15 → `sound`; `P2-02-audio.md` reqs 11, 17;
   `Tech Design.md` → Decisions → Where do sound and art assets come from?)*
   **PRD-author judgment, reversible**; `P1-03` Blocking item 2 asks the same question for
   Neon and the answer should apply to both.
   *Testable:* `classic.yaml` contains `sound.signature` and no other `sound.*` key.
   **This makes the metadata-only write of Requirement 8 the correct *interim* state — and a
   defect the day `P5-02-asset-generation-replicate.md` produces the file.**

> **Music — a position recorded, not yet a requirement.** `Theming.md` → Decisions settles
> that **all four toggles ship and music belongs to the theme**: a theme supplies its own
> music the way it supplies its sounds, which reverses the earlier *one-shot effects only*
> stance. **Classic's position is that it overrides music too** — for the same reason it
> overrides the splat, since inheriting Neon's would hand a clean, classic theme an electric
> soundtrack.
>
> **It is not a requirement, and not in Requirement 5's override set, because there is no
> key shape to write against.** `sound.music` exists as a placeholder that predates the
> Decision; `P1-03` Blocking item 1 sets out two incompatible candidates — a single
> `sound.music` `assetPath`, or a `music.<context>` map keyed by screen — and declines to
> pick, because whether music loops, whether it differs by screen, and where the audio comes
> from are all with the user. Stating an override against the wrong shape would have to be
> re-authored the day the real one lands.
>
> Recorded so that Classic's silence on music reads as **pending, not as an oversight**.
> *(`Theming.md` → Decisions → Do all four toggles ship, and is music a theme concern?;
> `P1-03-theme-system.md` req 15 → `sound`, req 17, Blocking item 1)*

### Animation and chrome

10. **Classic authors no animation and inherits Neon's motion whole.**
    *(`Theming.md` → Theme Catalog → Theme 2 → What it inherits from Neon; `Animations.md` →
    Animations Inherit From Neon; → Decisions → Do themes inherit Neon's animations?)*
    *Testable:* `classic.yaml` contains no `animation.*` key.
    **Why all-or-nothing is the only safe option here.** `P1-03` req 8 makes **a list a
    leaf**: a theme naming `animation.<moment>.tracks` **replaces the whole list**, because
    there is no stable identity for "the second keyframe." So there is no such thing as a
    small animation tweak — changing one magnitude means re-authoring every track of that
    moment. Inheriting is safe precisely because it is total.
    **What is inherited is genuinely complete**: `P1-03` req 13(b) makes
    `animation.<moment>.tracks[].keyframes[].value` **`required` and authored in Neon this
    wave**, so Classic inherits real magnitudes, not empty slots.
    **One caveat worth carrying:** a `glowColor` track interpolates a *colour*, and Neon's
    magnitudes are Neon's colours. If any authored track animates toward a palette value,
    Requirement 6's check reaches it like any other leaf — and inheriting it whole is then a
    derivation miss, not a safe default. Worth a look once Neon's magnitudes are authored.

11. **Chrome icons: Classic overrides the tints and inherits the glyphs.** Chrome icons are
    theme-controlled, and a theme may either name a glyph from a bundled icon set or ship
    its own image. The schema's six slots — `settings`, `close`, `chevronLeft`,
    `chevronRight`, `plus` and `trash` — each carry a `tint` that is a Neon palette colour,
    and the first five carry an optional `button.{fill,radius,size}`.

    **Classic's posture, decided:** override `icons.<slot>.tint` for all six and
    `icons.<slot>.button.fill` for the five that have one; inherit `kind`, `set`, `name`,
    `path` and `size`. Classic stays on the bundled set and ships no icon art of its own —
    its quarrel with Neon's chrome is the colour, not the glyph.
    *(`P1-03-theme-system.md` req 15 → `icons`, and its req 26)*
    **`icons.trash` is Neon-authored, not drawn** (`P1-03` req 13(b)) — Classic still only
    re-tints it, but its Neon value will be newer than the rest, so it is the slot most
    likely to be missed in a derivation pass.

    **Why the tints cannot be left to inherit.** Under blanket inheritance Classic renders
    Neon's chrome tints — palette colours picked against `#161826` — on a `#f3f5fe` ground.
    That is precisely the near-miss class Requirement 6's check catches, and because
    `icons.*` is inside that check's walk, **a Classic that inherits its tints fails
    Requirement 6**. Requirements 5, 6 and 11 agree by construction rather than by
    cross-reference.

    `P1-05-theme-guard-test.md`'s icon-constant rule now covers the whole scan root with
    `lib/theme/` permitted, so an `Icons.*` reference reaching around the theme is
    **enforced, not advisory**. That closes the code half; the theme-file half is
    Requirement 6's.

### What can be asserted, and what cannot

12. **Classic materializes complete.** Every key path in `lib/theme/required_keys.dart`
    resolves in Classic's materialized theme.
    *(`Theming.md` → Neon Is the Base Theme → How it works; `Tech Design.md` → Decisions →
    Fallback to Neon — merge, not resolve; `P1-03-theme-system.md` reqs 8, 9, 11)*
    *Testable:* run `P1-03` req 11's manifest test against Classic's materialized theme
    instead of Neon's; every `required` key resolves, counting an explicit null as defined.
    **Scoped to `required` keys deliberately.** Over *all* schema keys this fails by
    construction and would fail for Neon too: `surfaces.settingsCard.purchases.*` is
    `deferred` with nothing drawn, and music beyond the `sound.music` placeholder is deferred
    with it (`P1-03` Appendix A.2, Blocking items 1 and 7). Three former members have left
    that list — `surfaces.destructive.*`, `icons.trash.*` and the animation magnitudes are
    now `required` and authored in Neon (`P1-03` req 13(b)).
    **What it asserts, and what it does not.** Deep-merge makes absence impossible, so this
    passes for any file that parses and declares an understood version. It asserts the merge
    works — not that the merged result is usable, and not that anything was derived.
    Requirement 6 is the check with teeth.

13. **Every screen renders under Classic with no missing values.**
    *(`Theming.md` → Neon Is the Base Theme → Why this matters for the build)*
    *Testable:* with Classic active, walk every screen that exists — main menu, theme select
    overlay, settings (menu route, four toggle rows), the in-game quick-actions sheet,
    open-games list, an open-game row's swipe-revealed trash control and its Yes/No
    confirmation dialog, name prompt, board in free-choice, board in forced quadrant, board
    with a pending move, the how-to-play strip in all three of its states, winner modal,
    draw modal, and the theme-failed-to-load modal (`P1-03` reqs 27, 32, 34) — and none
    falls back to an undefined or null value.
    **Where the ground-dependence bites hardest:** `P3-05-how-to-play.md` requirement 18
    transcribes the strip's three text colours — the hint at `#75798c`, the legend row at
    `#595d6c`, the ring-explanation lines at `#b2b6ca` — all greys chosen against near-black,
    all reached through `surfaces.legend.*`, all inside Requirement 5's override set. That
    PRD explicitly declines to assert legibility (its Out of Scope, pointing at `P1-03`'s
    open question), so nothing downstream will catch it either.
    Like Requirement 12, this passes by construction; the walk is where a human sees the
    derivation misses that Requirement 6's check counts.

14. **Classic and Neon must read as two genuinely different looks.** This is the check that
    nothing is hardcoded, not a stylistic preference.
    *(`Theming.md` → Theme Catalog → Theme 2: "Two genuinely different looks, which is a
    real test that nothing is hardcoded")*
    **No threshold for "genuinely different" is written anywhere**, and inventing one would
    be inventing values the docs have not settled. The enforceable halves live elsewhere:
    Requirement 6 (no Neon triple survives in a materialized Classic leaf) and Requirement
    16 (no code changed).

15. **Classic must keep the gameplay-critical highlights legible** — the last-move highlight
    and the active-quadrant highlight are gameplay-critical, not decoration. A theme that
    makes them hard to spot is a broken theme.
    *(`Theming.md` → What a Theme Controls; Theme Catalog → Theme 1)*
    Classic *may* distinguish things by more than colour — shape, icon, outline, ring style
    including dashes, and motion — since that is "handled per theme"; it is not required to.
    **Fill patterns and textures are not available**: `P1-03` lists them under *Not in the
    schema*.
    *(`Theming.md` → Decisions → Is anything distinguished by colour alone?;
    `P1-03-theme-system.md` req 21 and req 15 → Not in the schema)*
    The treatments themselves are `P3-01-board-rendering.md` requirements 29–30.

    **Blocked — this requirement cannot be given an assertable form here.** `Theming.md` →
    Open Questions asks what form the legibility contract takes and records that the
    contract is unfalsifiable as written. Until that is answered there is no contrast floor,
    review step or other criterion to test against, and writing one into this PRD would
    decide the design docs' open question by accident. It is marked blocked rather than
    dropped because it is the **only** requirement here that a bad theme could fail on
    judgment alone.

    **The failure it is meant to catch is no longer hypothetical — it is the path of least
    resistance.** Now that the three anchors are settled, the cheapest thing an author can do
    is set exactly those three and stop. That theme satisfies Requirements 12, 13 and 14 and
    is unusable: Neon's inherited `color.text: "#e9e9ed"` on Classic's `#f3f5fe` ground is
    near-white on near-white, and every veil, scrim and glow inherited from Neon is an rgba
    tuned for `#161826`. Complete, passing, unreadable. Requirement 6 now catches the
    *derivation* half of that failure mechanically; what it cannot catch is a recomputed
    value that is derived correctly and still illegible. That gap is this requirement, and
    it stays open.

### Code boundary and free tier

16. **Authoring Classic requires zero changes to game, board or menu code.**
    *(`Theming.md` → Architectural Rule; `P1-03-theme-system.md` reqs 26, 32)*
    *Testable:* dropping `classic.yaml` into `assets/themes/` and rebuilding is sufficient —
    **no `.dart` file is edited anywhere**, and in particular nothing under the board, menu
    or game layers. `P1-03` req 32's stated test is the same one from the system side, and
    it forbids "a hand-maintained list of UUIDs in Dart."
    **Which asset declaration this relies on: the directory-level one.** Discovery is by
    **folder scan** — `P1-03` req 32 reads Flutter's asset manifest and selects every bundled
    key under `assets/themes/` ending in `.yaml` — and that only reaches a dropped-in file
    because the *directory* is declared in `pubspec.yaml`, which `P1-03` req 36 fixes and
    `P1-01-app-scaffold.md` owns. **So this PRD's diff is one file and touches `pubspec.yaml`
    not at all.**
    One consequence worth knowing before authoring: entries are ordered by asset key and a
    duplicate `meta.id` loses to the earlier file, with Neon's UUID reserved outright
    (`P1-03` req 32). Copying `neon.yaml` as a starting point — which the derivation work in
    Requirement 6 makes tempting — and forgetting to change `meta.id` silently excludes the
    result.

17. **Classic ships free, and theme selection labels it as free.** Neon and Classic Red vs
    Blue are the two free themes; every theme beyond those two is paid, and the theme
    selection list labels which themes are free and which are paid. Classic is the boundary
    case — the last free theme, and the shape the first paid theme is copied from.
    *(`Theming.md` → Decisions → Which themes are free; Are themes unlockable/rewards)*
    *Testable:* Classic is selectable and applies with no purchase, entitlement or unlock
    step of any kind, and its row in theme selection carries the free label.
    The free-tier default that makes this true is `P1-07-entitlements.md` requirement 1; no
    ownership or price key appears in `classic.yaml` (`P1-03` req 31).

> **Recorded from `Theming.md` → Neon Is the Base Theme → Watch out for — stated, not a
> decision, and not a requirement above.** A partial theme inherits Neon's *personality*,
> not just its values. Classic Red vs Blue with Neon's electric buzz sounds and glow
> animations may feel mismatched — clean visuals with electric audio. That's a fine default
> (it works, nothing is missing), but Red vs Blue may want to override more than just
> colors to feel coherent. Worth checking once it's real; not a problem to solve now.
> **Two settlements sharpen this rather than changing it:** music (see after Requirement 9)
> and one tap sound everywhere (Requirement 8), which together mean the inherited audio is
> now heard on nearly every interaction rather than only on the board.

## Out of Scope

- **The theme mechanism** — the schema itself, YAML loading, UUID identity, deep-merge
  materialization, folder-scan discovery and the catalog, the complete Neon base, and the
  failed-to-load modal: `P1-03-theme-system.md`. This PRD authors a file against that
  schema and changes none of it, **including which keys exist**.
- **The hardcoded-theme-value guard** — `P1-05-theme-guard-test.md`. Its icon-constant rule
  now covers the whole scan root with `lib/theme/` permitted, so chrome cannot reach around
  the theme *in code*. But it still scans `lib/` only, and its Out of Scope still disclaims
  *"validating the contents of a theme file"* and *"catching a value read from the wrong
  slot."* **Classic passes the guard no matter what is in `classic.yaml` — including an
  empty file.** A green guard is not evidence of a correct theme; Requirement 6's check
  exists because nothing else in the repo can distinguish the two.
- **Persisting the selection** — `P1-04-persistence.md`.
- **The theme selection UI** — the overlay, the rows, the preview tile, the ACTIVE
  treatment, the rendering of the name and blurb, and the free/paid labels:
  `P4-03-theme-selection.md`. Requirement 3 supplies the strings; Requirement 17 fixes only
  that Classic is free and is labelled so.
- **Audio playback** — loading and firing sound assets, `audioplayers`, the global mute, and
  where the one tap sound fires: `P2-02-audio.md`. This PRD names slots; it plays nothing.
- **Playing music, and the shape of the music key** — no PRD owns playback yet, and the key
  shape is `P1-03` Blocking item 1.
- **The animation interpreter** — `P2-04-animations.md`. Neon's magnitudes are `P1-03` req
  13(b)'s, not Classic's.
- **Entitlement state and paid themes** — `P1-07-entitlements.md` and
  `P4-05-purchase-flow.md`. Splat and Dinosaurs in `themes.catalog.json` remain explicitly
  placeholders that do not exist.
- **Generating the splat sound file and any art** — `P5-02-asset-generation-replicate.md`.
  What Classic's sound slots hold before that lands is Requirement 9.
- **Defining the legibility contract** — `Theming.md`'s open question, carried at system
  level by `P1-03`. This PRD is where it bites first, not where it gets answered.
- **Changing the theme mid-game.** Theme changes happen from the main menu only.
  *(`Theming.md` → Decisions → Can you change the theme mid-game)*

## Open Questions

### Going to the user

These three gate the remaining **values** in `classic.yaml`; the palette itself no longer
does.

1. **What form does the legibility contract take — a contrast floor, a review step,
   something else?** *(verbatim from `Theming.md` → Open Questions.)* **What a Theme
   Controls** requires every theme to keep the last-move and active-quadrant highlights
   legible, but this is unfalsifiable as written: Classic Red vs Blue has a near-white
   ground while inheriting Neon's near-white text and its veils and glows tuned for a
   near-black ground, so a theme could be complete, pass every stated check, and still be
   unreadable. **Requirement 15 stands on this and is blocked by it.** Requirement 6 now
   catches the derivation half mechanically, which narrows this question rather than
   answering it: a correctly derived value can still be illegible.
2. **Which of the five playable sound slots does the splat fill?** `Theming.md` names one
   signature sound; `themes.catalog.json` says Classic inherits `"sound (except the
   splat)"`. `P2-02` req 6 fixes the five slots. **`buttonTap` is the live one** now that one
   tap sound plays on every button, row and toggle — a splat there is heard constantly, and
   a buzz there is Neon's personality on every Classic screen. Requirement 8 is blocked on
   this.
3. **Does Classic override the marks at all?** `themes.catalog.json` gives Classic the same
   `✕` / `○` marks as Neon. With the palette settled, this is now the largest remaining
   question about what Classic *looks* like: `Theming.md` → Decisions → Marks beyond X and O
   allows a theme its own mark art but does not say Classic uses it. Requirement 7 defaults
   to inheriting.

**Also waiting on `P1-03`, not on the user directly:** Classic's music value, once Blocking
item 1 lands a key shape (position recorded after Requirement 9). The three sub-questions
behind that shape — whether music loops, whether it differs by screen, where the audio comes
from — are already with the user in `Theming.md` → Open Questions.

**Answered since the last revision, and folded in:** whether `previewColors` are Classic's
real values — **yes**, all three, with everything else deriving from them (Requirement 6);
and whether non-board controls make a sound — **yes, one tap sound everywhere**
(Requirement 8, question 2).

### From `Theming.md` → Open Questions — carried, not resolved

- Which values, concretely, does Classic Red vs Blue override? (Settled in principle —
  graphics and its splat sound, inheriting the rest. An exact list will fall out when it's
  actually built.)

**This question is now two items short of the doc's own Decisions**: "graphics and its splat
sound" predates both music being themed and the three anchors being settled. Requirement 5
answers the key-path half as a reversible judgment, Requirement 6 answers the value half for
the three anchors and states the obligation for everything derived from them, and what
remains is the marks, the splat's slots and music. Carried unresolved because the doc's
framing — "an exact list will fall out when it's actually built" — is now due, and this PRD
is where it falls out.

### Raised by this PRD (flags, clearly mine)

- **Does the smallest legible Classic still count as the cheap-theme proof?** With the
  anchors settled, the honest shape of this feature is three given colours plus a derivation
  pass across every surface and icon leaf — no longer "as small as black → white, neon green
  → red." Whether that refutes `Theming.md`'s "new themes become cheap" claim or refines it
  to "cheap in *code*, not in *values*" is worth a sentence in the doc once Classic is real.
  The folder-scan answer is the strongest form of the cheap-in-code half.
- **`P5-02-asset-generation-replicate.md` carries a stale premise about this PRD.** It lists
  `P5-01-classic-theme.md` under *"Depended on by (each ships with placeholders until
  then)"* and states "All of those ship in earlier waves, without assets, by design."
  `P5-01` is the **same** wave. If the answer to *where music comes from* is "generated,"
  music joins its scope too.
- **This PRD's schema references decay silently.** Five version bumps have landed between
  revisions, and one left Requirement 3 fencing a stale `schemaVersion` that no test here
  would have caught, because it lives in prose. Whatever authors `classic.yaml` should
  re-read `P1-03` req 15 and req 37 first rather than trusting the key paths quoted here.
