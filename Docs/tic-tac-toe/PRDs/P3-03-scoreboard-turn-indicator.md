**Build-readiness: 87**

# PRD: Scoreboard and Turn Indicator

> **Status:** Draft · Source docs read: `Game Board Design.md`, `Game Overview.md`,
> `Menus and UI.md`, `Theming.md`, `Rules.md`, `Tech Design.md`, `Animations.md`,
> `roadmap.md` (the Decision index, re-read before the requirements each round).
> `Alternative Game Styles.md` is a parking-lot doc and was not sourced.
> `design_handoff_game_ui/` is a read-only reference asset — screens `1d`/`1e` draw this
> strip.
>
> **This round:** the cross-axis stretch is named as `IntrinsicHeight` — as specified it
> would not have compiled; the three label strings get an owner and a file, filling the
> ellipsis in `P3-01` req 48; and `GameScreen` is cited as **landed text** (`P3-01` reqs
> 46–52) rather than as an assignment in flight.
>
> **A fence is a claim that a question is open.** Once the docs answer it, a surviving fence
> tells the next agent that settled behaviour is optional. Every fence here is re-checked
> against `roadmap.md` each round; one that outlives its Decision is a defect, not caution.
>
> Requirements 1–22 keep their numbers — `P1-02` reqs 27 and 38, `P1-03` req 15, `P2-02`
> req 6 and its Out of Scope table, `P2-03`, and `P3-01` reqs 47–50 all cite reqs 2, 4, 7, 9,
> 11, 12, 17, 19, 21 and 22.

**Wave:** P3 — the game screen wave, alongside `P3-01-board-rendering.md`.

**Dependencies — the identifiers this PRD codes against:**

| Dependency | What this strip uses, by name |
|---|---|
| `P1-02-engine-rules.md` | `board.currentPlayer` (`Player.one` / `Player.two`, req 38 — which names *this PRD's requirement 9* as its consumer); `board.score.playerOne` / `.ties` / `.playerTwo` (`Score`, req 39); `board.placementState == PlacementState.gameOver` (req 36); `board.outcome` (req 37). The increment is req 27. |
| `P1-03-theme-system.md` | `activeThemeProvider` — `Provider<Theme>` in `lib/theme/theme_providers.dart` (req 24) — and the keys in requirement 14 (req 15, **schema v8**). **Never `Theme.of(context)`**, which req 24 rejects and `P1-05` scans for. |
| `P1-04-persistence.md` | Where the series score is stored; this strip reads it through the engine's `Score`, never from storage. |
| `P1-05-theme-guard-test.md` | The scan requirement 14 must pass, and the seam that blocks requirement 12's glyph: resolving an `icons.<slot>` with `kind: iconSet` into an `IconData` must live inside `lib/theme/`; `P1-03` req 5 gives it no home yet. |
| `P2-01-navigation.md` | `AppNavigator.openQuickActions()` (req 3), reached through `appNavigatorProvider` (req 4) **by `GameScreen`, not by this strip**; req 10 (two entry points), req 14 (opening it does not leave the game), **req 20** (this layer clears the pending selection on every navigation). |
| `P2-02-audio.md` | `AudioLayer.play(SoundMoment.buttonTap)` via `audioLayerProvider`. Its req 6 wave note and Out of Scope table name **this PRD's req 12** as the sixth `buttonTap` call site. |
| `P2-03-haptics.md` | `HapticService.validAction()` via `hapticServiceProvider`. Its OQ-2 is closed and it names this PRD's req 12 as a settled non-board caller. |
| `P3-01-board-rendering.md` | Owns **`GameScreen`** — reqs 46–52, `lib/ui/board/game_screen.dart`: req 47 puts this strip first in the vertical stack, req 48 passes it board state, req 49 supplies its settings callback, req 50 fixes `stripToBoardGap` at **14pt**, req 51 hosts the clear surface requirement 13 depends on. Also `BoardView` (req 38) at the 402pt frame numbers of req 4, the `ConsumerWidget` pattern of req 43, the `BoardKeys` shape of req 45, and req 39's no-goldens rule. |
| `P3-02-move-input.md` | `boardProvider` (req 29) and `pendingSelectionProvider` (req 24). Its req 26 owns the tap-outside-clears rule. |
| `P3-04-game-over-rematch.md` | Presents the finished game and carries its own next-game and main-menu buttons. It does **not** change the score; its req 13 draws its own 27/600 chips. |

## Problem

Two players share one phone and pass it back and forth, so the screen is the only thing
telling them who is up (`Game Board Design.md` → Turn Indicator). With no scoreboard and
no turn indicator, a player handed the phone cannot tell whose move it is, and nothing
records that they are on their fourth game in a row — which is the whole shape of play the
app is built around: "playing several in a row on the same phone"
(`Game Overview.md` → Session Structure — Games and Continuing).

## Goal

The game screen carries a scoreboard strip above the board showing three counters —
`PLAYER 1`, `TIES`, `PLAYER 2` — for the open game being played, with the active player's
counter highlighted so whoever is handed the phone can see at a glance whose turn it is,
and a settings button at its top right that buzzes, clicks and opens quick actions. The
strip is entirely theme-driven, it never swallows a tap that should clear a pending move,
and it fits above a full 81-cell board on a portrait phone without the board losing any of
its visibility.

> **Author judgment — the interface, fenced because no design doc names one.** Reversible,
> and stated so `GameScreen` and `P3-04` agree rather than each inventing one:
>
> ```dart
> // lib/ui/board/scoreboard_strip.dart
> class ScoreboardStrip extends ConsumerWidget {
>   const ScoreboardStrip({
>     super.key,
>     required this.score,             // Score — P1-02 req 39
>     required this.currentPlayer,     // Player — P1-02 req 38
>     required this.isGameOver,        // board.placementState == gameOver — P1-02 req 36
>     required this.playerOneLabel,    // requirement 11
>     required this.playerTwoLabel,    // requirement 11
>     required this.tiesLabel,         // requirement 11
>     this.onSettingsPressed,          // null renders no button — requirements 12, 21
>   });
>   // build(context, ref) reads activeThemeProvider, and — inside the settings
>   // button's tap handler only — hapticServiceProvider and audioLayerProvider.
> }
> ```
>
> **`ConsumerWidget`, not `StatelessWidget`.** Requirement 14 requires every visual value to
> come from the active theme, and the published accessor is a Riverpod provider
> (`P1-03` req 24), so a `StatelessWidget` cannot satisfy requirement 14 without either an
> unlisted `theme` parameter — which breaks the call-site contract this fence exists to fix —
> or `Theme.of(context)`, which req 24 rejects and `P1-05` scans for. `P3-01` req 43 makes
> the identical choice for `BoardView`, and its req 46 for `GameScreen`.
>
> **Game state and navigation come from the host; the two feedback layers are read here.**
> Board values arrive as parameters so the strip can be built from any `Board` in a widget
> test without a container. `appNavigatorProvider` is read by `GameScreen` (`P3-01` req 49),
> so the strip names no route. The haptic and audio layers are read here because `P2-03` and
> `P2-02` both name **this PRD's requirement 12** as the call site that fires them, and an
> assertion about a call site has to be writable where the call is. Requirement 19's closed
> provider list matches exactly that split.

## Requirements

### The scoreboard

1. **The game screen shows a scoreboard at the top, above the board, holding exactly three
   counters — Player One's, Ties, and Player Two's — in that order.**
   *Source: `Game Board Design.md` → Scoreboard (the three-column table and the ASCII
   layout); `Game Overview.md` → Session Structure — Games and Continuing.*
   *Testable:* the game screen renders three labelled counters in that order above the
   board — one per field of `P1-02` req 39's `Score`, addressable by requirement 20's keys.

2. **The screen is a vertical stack: scoreboard on top, board below.**
   *Source: `Game Board Design.md` → Visual Layout; `P3-01-board-rendering.md` reqs 38 and
   47, which state the same from the screen's side.*
   *Testable:* in a widget test of `GameScreen`, the bottom edge of `ScoreboardStrip` is
   above the top edge of `BoardView`, and the two do not overlap.

3. **The counters show the running score of the open game currently being played** —
   `board.score.playerOne`, `board.score.ties`, `board.score.playerTwo` (`P1-02` req 39),
   one per column, in that order. Where that value is stored is `P1-04-persistence.md`'s,
   and this strip never reads storage.
   *Source: `Game Overview.md` → Decisions → Scoreboard lifetime; `Menus and UI.md` →
   Decisions → What does an open game hold?*
   *Testable:* constructing the strip with `Score(playerOne: 2, ties: 1, playerTwo: 0)`
   renders 2, 1, 0 under those three labels.

4. **The strip shows the incremented score from the moment the game ends** — as soon as the
   game is won or tied, the winner's column, or Ties, reads one higher. It does not wait for
   a rematch. This strip renders the `Score` the engine reports and increments nothing
   itself: the increment is `P1-02-engine-rules.md` requirement 27, bound to the move that
   ends the game.
   *Source: `Menus and UI.md` → Decisions → When does the scoreboard increment ("**At game
   end.** … not when a rematch is taken"); → Decisions → What happens when a game ends?;
   `Game Overview.md` → Session Structure; `Game Board Design.md` → Scoreboard; `Rules.md` →
   Big board full with no three-in-a-row.*
   *Testable:* apply the winning move to a board whose score is 2–1–0; the strip built from
   the returned `Board` reads 3–1–0 with no further input, and rebuilding from that same
   `Board` renders the same three values every time.

5. **The scoreboard carries across games in a series rather than resetting.**
   *Source: `Game Overview.md` → Session Structure; `Menus and UI.md` → Game Over → Rematch
   ("same series, scoreboard intact"); → Decisions → What does an open game hold?*
   *Testable:* the strip built from `startNextGame()`'s returned `Board` (`P1-02` req 26)
   renders the same three values as the strip built from the `Board` before it.

### The turn indicator

6. **The active player's counter is highlighted, and that highlight is the game screen's
   "whose turn it is" affordance.** The active player is `board.currentPlayer` (`P1-02`
   req 38) — engine state, never derived from move parity. Since the turn banner is not built
   (Closed 1), this is the only whose-turn mechanism on the screen.
   *Source: `Game Board Design.md` → Turn Indicator; → Player Feedback / Affordances ("Needs
   to be unmissable"); `P1-02-engine-rules.md` req 38.*
   *Testable:* with `currentPlayer == Player.one` and `isGameOver == false`, the Player One
   counter renders from `chip.playerOne.active.*` and carries
   `ScoreboardKeys.chipActive(Player.one)`; the Player Two counter renders from
   `chip.playerTwo.inactive.*` and carries no active key. Swapping `currentPlayer` swaps
   exactly those two.

7. **At most one counter carries the active-turn highlight, and it is never the Ties
   counter.** While a game is in progress exactly one of the two player counters is active.
   `P1-03` req 15 gives `chip.ties` no active variant "by design," citing this requirement.
   *Source: `Game Board Design.md` → Turn Indicator (singular "the active player's name");
   `Game Overview.md` → Modes; `Menus and UI.md` → A New Game → What It Starts;
   `P1-02-engine-rules.md` req 38.*
   *Testable:* across every turn of a played-out game, while `placementState != gameOver`,
   exactly one `ScoreboardKeys.chipActive(...)` is in the tree and it is never the Ties one;
   in no state are two present.

   > **Fenced judgment — the finished game. Still genuinely open.** `P1-02` req 38 states
   > that `currentPlayer` **alternates on the terminal move too**, so on a finished game it
   > names the *loser*, and tells consumers that must not present a turn on a finished game to
   > gate on `placementState == gameOver` instead. Its *Interface choice* note records that no
   > design doc chooses between alternating and freezing, and `roadmap.md` shows none has
   > since. **So: when `isGameOver` is true, no counter carries the active-turn highlight.**
   > See Open Question 2.

8. **The highlight moves to the other player when a move is confirmed, not when a cell is
   selected.** `currentPlayer` changes only on `applyMove` (`P1-02` req 38), and the change
   is immediate — no intermediate "pass the phone" state.
   *Source: `Game Board Design.md` → Move Input; `Menus and UI.md` → Pass-and-Play Turn
   Handoff; `P3-02-move-input.md` owns the gesture.*
   *Testable:* after the first tap the same counter stays highlighted; after the second tap
   the other one is, with no screen in between.

9. **Which player is highlighted at the start of a game is read from the engine, not
   decided here** — `board.currentPlayer` on the board returned by `newSeries()` or
   `startNextGame()`. Turn order is `P1-02-engine-rules.md`'s (reqs 25, 26, 38).
   *Source: `Rules.md` → Turn Order Across Games; → Decisions → Who goes first after a tie?*
   *Testable:* for a series where Player Two won the previous game, the strip built from
   `startNextGame()`'s board highlights **Player Two** — a parity-derived implementation
   fails this.

### Player labels

10. **The players are Player One and Player Two, and the opponent name entered at New Game
    never appears on this strip.**
    *Source: `Game Overview.md` → Decisions → Player names; `Menus and UI.md` → Decisions →
    Does the opponent name replace "Player Two" in game? ("No — not at this moment").*
    *Testable:* a game created with opponent name "ItSaMeMaRiO" renders no such string
    anywhere on the game screen.

11. **The chips read `PLAYER 1`, `TIES` and `PLAYER 2` — the numeral, not the spelled-out
    form.** Settled by `Game Board Design.md` → Decisions → *What do the scoreboard chips
    read?*, which gives two reasons: every drawn screen shows the numeral, and the spelled-out
    form is materially wider in a fixed-width column. That Decision explicitly **does not**
    change the term for the player, which stays "Player One" / "Player Two" per
    `Game Overview.md` → Decisions → Player names; the chip is a label, not the name.

    **The strings live in one const class, not in the widget and not at the call site.**

    ```dart
    // lib/ui/board/scoreboard_labels.dart
    abstract final class ScoreboardLabels {
      static const String playerOne = 'Player 1';
      static const String ties      = 'Ties';
      static const String playerTwo = 'Player 2';
    }
    ```

    `GameScreen` passes these three (`P3-01` req 48, whose `playerOneLabel: …` ellipsis this
    fills), and the strip takes them as parameters — so requirement 10's future swap to real
    names stays a change at the call site, and `scoreboard_strip.dart` still contains no
    display string of its own. **Not default parameter values**, which would put the literals
    back inside the widget file and fail this requirement's own scan; **not inline at the call
    site**, which would leave `P3-04` or any future host free to spell them differently.
    *Testable:* under Neon the three chips read exactly `PLAYER 1`, `TIES`, `PLAYER 2`; no
    rendered chip ever reads `PLAYER ONE` or `PLAYER TWO`; a source scan of
    `scoreboard_strip.dart` finds no user-facing display string; `GameScreen` references
    `ScoreboardLabels` rather than string literals.

    **Casing is a render-time transform.** When the resolved `chipLabel` style has
    `uppercase == true` (`P1-03` req 15; Neon sets it), the strip renders
    `label.toUpperCase()`; otherwise the string as passed — which is why the constants above
    are title case.
    > **Fenced — what the Decision does not draw.** It shows only the uppercase form, so
    > whether `uppercase: false` yields `Player 1` or still `PLAYER 1` is unstated. **Default:
    > `Player 1`** — the numeral is settled, the casing stays the theme's, because baking the
    > case into the string would make `chipLabel.uppercase` dead for this style while every
    > other consumer of that flag honours it.
    > *A duplication, not an ownership gap.* `P4-01-main-menu.md` **req 2** does the same for
    > the menu, with the same reasoning and its own testable. Two components implement this
    > transform independently; worth one shared text helper eventually.
    *Not a vocabulary question:* `Game Overview.md` → Decisions → *Player-facing vocabulary*
    settles that player-facing text says "board"; none of these strings contains that word.

### Settings button

12. **A settings button sits at the top right of the game screen, alongside the scoreboard.
    Tapping it fires the haptic, plays the tap sound, and invokes `onSettingsPressed` exactly
    once — and `GameScreen` wires that callback to
    `ref.read(appNavigatorProvider).openQuickActions()` (`P3-01` req 49).**
    *Source: `Game Board Design.md` → Scoreboard; `Menus and UI.md` → How you reach settings
    from gameplay; → Decisions → How do you get back to the main menu from a game?;
    `P2-01-navigation.md` reqs 3, 4, 10, 14.*

    **Where each half is asserted, because the read site decides it.** The navigator is read
    by the screen, not the strip (requirement 19's closed provider list), so:
    - *At strip level:* tapping the control invokes `onSettingsPressed` exactly once, fires
      exactly one `HapticService.validAction()`, and plays exactly one
      `play(SoundMoment.buttonTap)` — all three assertable against fakes with no navigator
      present.
    - *At screen level:* the callback `GameScreen` supplies records exactly one
      `openQuickActions()` on `P2-01` req 3's recording fake **and no other navigation
      operation**. `P3-01` req 49 carries the same assertion from its side.

    **"No other navigation operation," not "no other effect."** Three other effects are
    settled, and suppressing any of them is wrong. `P2-03` records this exact wording trap,
    naming this requirement and `P4-01` reqs 14–16 as the two call sites that hit it.
    - **The haptic fires** — `HapticService.validAction()` via `hapticServiceProvider`,
      subject to the vibrate setting, which the layer gates internally. **Settled:**
      `Game Board Design.md` → Decisions → *Does the haptic fire on non-board controls?* —
      "**Yes — every valid tap buzzes, anywhere in the app** … the settings gear" — and
      `P2-03`, whose OQ-2 is closed and which lists this requirement among the settled callers.
    - **The tap sound plays** — requirement 22's mechanism, this requirement's call site.
      **Settled:** `Theming.md` → Decisions → *Do non-board controls make a sound?*; `P2-02`
      req 6's wave note and Out of Scope table both name this requirement as the sixth
      `buttonTap` site.
    - **The pending move is cleared by the navigation layer, not by this strip.**
      `P2-01-navigation.md` req 20 owns it: opening a surface over the board changes no board
      state, so `P3-02` req 30's listener never fires and something must clear actively. This
      strip installs no route observer and calls no `clear()`.

    **`onSettingsPressed` is nullable, and null renders no button** — no disabled control and
    no reserved space; requirement 21 states what the row does with the freed width.

    > **Fenced — the button over the result card. Presentation only.** **Default: present and
    > live.** The old argument is retired: the result card carries its own next-game and
    > main-menu buttons (`Menus and UI.md` → Decisions → *What controls does the game-over
    > result card carry?*), so no player depends on this button to leave a finished game.

    > **Blocked, not guessable — the glyph.** `P1-05` states that turning an `icons.<slot>`
    > with `kind: iconSet` into a concrete `IconData` **must** live inside `lib/theme/`, while
    > `P1-03` req 5 gives that resolver no home and `P1-01` req 14's dependency list contains
    > no icon package. This strip **declares no resolver and no icon constant** — no
    > `Icons.*`, no `PhosphorIcons.*`, no asset path.
    > **Interim child:** `SizedBox.square(dimension: theme.icons.settings.size)` — *not*
    > `SizedBox.shrink()`, which with requirement 14's transparent-fill fallback would ship an
    > invisible, possibly 0×0, untappable target. `icons.settings.size` is required with no
    > fallback, so the slot holds its final dimensions and the interim layout is identical to
    > the final one.

13. **The strip does not absorb taps.** A tap anywhere on the strip that is not the settings
    button must reach the screen's clear surface (`P3-01` req 51). The counters carry **no**
    tap recognizer — no `InkWell`, no `GestureDetector`, no `onTap` — since a recognizer would
    win the gesture arena and silently leave the pending move standing.
    *Source: `Game Board Design.md` → Decisions → Does a tap outside the board clear a
    pending move? ("That includes the legend/how-to-play strip, **the scoreboard**, the
    settings button… One rule, uniformly applied"); `P3-02-move-input.md` req 26 and its req 8
    verification, which asserts this case by name; `P3-01` req 51 hosts the surface.*
    *Testable:* with a pending selection active, a tap on each of the three counters and on
    the strip's background leaves `pendingSelectionProvider` null and `boardProvider`
    unchanged; a widget test finds no tap recognizer in the strip's subtree except the
    settings button's.

### Styling and fit

14. **Every visual value on this strip comes from the active theme**, read through
    `ref.watch(activeThemeProvider)` (`P1-03` req 24) and never through `Theme.of(context)`.
    No colors, fonts, type sizes, radii or durations are written into this component's code.
    *Source: `Theming.md` → Architectural Rule; → What a Theme Controls; `Game Board
    Design.md` → Everything Here Is Theme-Driven; `P1-03-theme-system.md` req 24.*
    *Testable:* `P1-05-theme-guard-test.md` reports zero violations in
    `lib/ui/board/scoreboard_strip.dart`, including its `icon-constant` rule.

    **The keys this strip reads** — `P1-03-theme-system.md` req 15, **schema v8**:

    | Key path | Used for |
    |---|---|
    | `surfaces.scoreboard.chip.playerOne.active.{fill,border,glow,labelStyle,valueStyle}` | Player One's counter while it is their turn |
    | `surfaces.scoreboard.chip.playerOne.inactive.{fill,border,labelStyle,valueStyle}` | Player One's counter otherwise |
    | `surfaces.scoreboard.chip.playerTwo.active.{…}` / `.inactive.{…}` | the same, for Player Two |
    | `surfaces.scoreboard.chip.ties.{fill,border,labelStyle,valueStyle}` | the Ties counter — no active variant, per requirement 7 |
    | `surfaces.scoreboard.radius` | counter corner radius |
    | `icons.settings.{kind,set,name,path,tint,size}` | requirement 12's glyph — resolved by the theme layer, never here |
    | `icons.settings.button.{fill,radius,size}` | its chrome — **optional per slot** |

    **Precedence, stated once so requirements 14, 17 and 21 cannot disagree: the theme wins
    where it speaks.** When `icons.settings.button.size` is present, that is the button box
    and requirement 21's 44pt does not apply; 44pt applies **only** when the key is absent.
    Same for `button.fill` and `button.radius`, which fall back to a transparent fill and
    `surfaces.scoreboard.radius`. Neon transcribes `1d`, so under Neon the box is 44 × 44 and
    the two readings coincide — which is why the precedence has to be written down rather than
    inferred from the fixture.

    **Component keys only — never a palette token that happens to match.** `P1-03` req 15
    states the rule, and its Appendix A.1 uses *this* strip as the live example: the active
    Player One chip fill and `color.playerOneTint` hold the **same value today**, so binding
    to the palette token passes the guard, renders correctly, and breaks silently the first
    time either moves. This component reads no `color.*` key at all, and its type styles come
    from the chips' own `labelStyle` / `valueStyle`, which is where `type.scale.chipLabel`
    (9 / 0.1em) and `type.scale.chipValue` (22 / 600) land. `P3-04`'s result chips are a third
    size (27/600) and are not this component.

    **Spacing is not a theme value.** `Theming.md` → Decisions → *Does a theme control spacing
    and padding?* — "No spacing will be fixed for now" — and `P1-03` **removed every spacing
    key in v7**. The strip's gaps and paddings are **code constants** (requirement 21). Radius
    and the button box stay theme values.

15. **Naming a slot decides nothing about its value, and this strip constrains none of them.**
    Any theme may set `chipLabel` and `chipValue` to any size; the strip lays out around
    whatever it is told (requirement 17's derivation), and requirement 16 is the only
    constraint it places on a theme.
    *Source: `Theming.md` → Architectural Rule; `P1-03-theme-system.md` req 13.*
    *Testable:* folded into requirements 16 and 17 — 16 asserts the one constraint, and 17's
    fourth clause asserts that doubling `chipValue`'s size in a fixture theme changes the
    strip's height rather than clipping, which is what "constrains none of them" means in
    practice.

16. **The active and inactive counter treatments must differ in value in at least one of the
    four fields the two states share** — `fill`, `border`, `labelStyle`, `valueStyle` — for
    each player, in every theme in `assets/themes/`. This is a **value-inequality** check, not
    a perceptual one: `#232532` against `#232533` passes it. It exists to stop the highlight
    resolving to a literal no-op, which would silently remove the game's only whose-turn
    signal (requirement 6).
    *Source: `Game Board Design.md` → Turn Indicator ("**highlighted**"); → Player Feedback /
    Affordances; `Theming.md` → What a Theme Controls ("Every theme must keep these legible…
    not just the default one").*
    *Testable — and it can actually fail:* comparing whole objects would pass unconditionally,
    because `active` carries a `glow` field `inactive` does not have. The assertion is
    field-wise over the four shared fields, on **materialized** theme values:
    `active.fill != inactive.fill || active.border != inactive.border || active.labelStyle !=
    inactive.labelStyle || active.valueStyle != inactive.valueStyle`. A theme that sets all
    four alike and leans on `glow` fails — deliberately.
    **The two type comparisons are field-wise over the inline object, and `color` is one of
    the compared fields.** `labelStyle` and `valueStyle` are **`textStyle` objects that carry
    their own colour** — settled by the user and normative in `P1-03` req 15 → `surfaces`
    (**schema v10**). There is no style name to dereference and no `type.scale` lookup at
    comparison time. Two `textStyle`s are equal when **all six fields** are equal:

    | Field | Required | Compared |
    |---|---|---|
    | `size` | yes | yes |
    | `weight` | yes | yes |
    | **`color`** | **yes** | **yes — and this is the field that makes the check correct** |
    | `tracking` | optional | yes, as a nullable |
    | `lineHeight` | optional | yes, as a nullable |
    | `uppercase` | optional | yes, as a nullable |

    **Why this had to change, and it is not a tidying.** Under the withdrawn reading a
    `*Style` key was a `type.scale` **style name**, and dereferencing it yielded
    `{size, weight, tracking, lineHeight, uppercase}` — **no colour**. So a theme that
    highlights the active player **by label colour alone**, leaving the size and weight
    alone, resolved both states to the *same* `type.scale` entry and compared **equal** on
    both type fields. If that theme also shared `fill` and `border` and leaned on colour, this
    requirement **failed it** — and it is a perfectly good highlight, arguably the cheapest
    and most obvious one an author would reach for. **The check was rejecting a working
    theme**, which is the opposite of its purpose: it exists to catch a highlight that is a
    literal no-op (requirement 6's only whose-turn signal), not to dictate *which* of the
    shared fields carries the difference. With `color` inside the object the check sees the
    difference and passes it.
    **The `ref` reading also had no legal way to colour these chips at all** — `P1-03` req 15
    bars a component from reading a palette key that happens to hold the same value, so there
    was no `color.*` fallback either. That is the impossibility `P1-03` v10 records; this
    requirement is one of roughly twenty text elements it reached.
    **Optionals compare as nullable values: absent equals absent, and absent never equals an
    explicit value.** An earlier draft said "an absent optional equals its documented
    default" — there is no documented default. `P1-03` req 15 declares `tracking`,
    `lineHeight` and `uppercase` optional on a `textStyle` and gives none of them a stated
    fallback, so "absent == 1.0" is not derivable from any document today. Comparing them as
    nullables is decidable now and stays correct if defaults are later written down;
    **flagged to `P1-03`**, which now carries it as an open item, since a renderer still has
    to pick something at paint time and that choice is unstated too. **v10 widened that gap
    rather than closing it** — the same three optionals now sit on every `surfaces.*`
    `textStyle`, not only on `type.scale` entries.
    **`color` is not optional and therefore never compares as null**, which is what keeps the
    six-field comparison decidable today.

17. **The scoreboard fits above the board on a portrait phone with the whole 9x9 board still
    visible and no zoom or scrolling, and its height is derived from its content rather than
    fixed.**
    *Source: `Game Board Design.md` → Scoreboard; → Responsive / Screen Size ("No zoom. The
    whole 9x9 grid stays visible at all times"); `Tech Design.md` → Decisions → Orientation —
    portrait only; `P3-01-board-rendering.md` req 4: **402pt wide, 16pt side padding, board
    370pt** — "the approved visual source of truth… not re-decided here."*

    **The derivation.** The chip, not the button, is the tallest element:

    | Term | Under Neon |
    |---|---|
    | `chipLabel` line box — 9pt at the font's own metrics (`lineHeight` unset ⇒ ≈1.21 em for Inter) | ≈ 11pt |
    | Intra-chip gap, label to value (requirement 21) | 2pt |
    | `chipValue` line box — 22pt at ≈1.21 em | ≈ 27pt |
    | Chip vertical padding, 8 + 8 (requirement 21) | 16pt |
    | **Chip height** | **≈ 56pt** |
    | Button box — `icons.settings.button.size`, 44 under Neon | 44pt |
    | **Strip height = max(chip, button)** | **≈ 56pt** |

    The chip exceeds the button by roughly 12pt, so the button never sets the height.
    **The strip declares no fixed height**: it is `max(chip content + padding, button box)`,
    and both terms move with the theme.

    *Testable — height, not absence of overflow:*
    - Under the **Neon fixture** at the 402 × 874 frame, the strip's rendered height equals
      the value the test computes from the resolved styles — **measured with `TextPainter`**
      over `chipLabel` and `chipValue`, plus the two constants and the button box. Measuring
      the rendered `Text` widgets instead would make two terms circular: the thing under test
      would supply its own expected value.
    - That height is **identical** across `0-0-0` and `99-99-99`; active Player One, active
      Player Two, and `isGameOver`; and with and without the settings button.
    - **Nothing clips**: no `TextOverflow` is reached in any chip in any of those states.
    - With a fixture theme that doubles `chipValue`'s size, the strip's height **grows** and
      still does not clip — which is what makes requirement 15 and this requirement
      compatible rather than contradictory.
    - `BoardView`'s rendered width is 370pt and nothing overflows or scrolls.

    Asserting a computed height rather than the absence of overflow is deliberate: an overflow
    assertion holds at almost any height and so protects the vertical budget from nothing,
    while a hardcoded height is passable by wrapping the row in a fixed box and clipping a
    label — the exact failure this wording exists to prevent.

    > **Fenced — multi-digit scores. Reversible.** The counters are equal-width columns, so a
    > counter **cannot widen** to fit a longer number. **Default: every column value up to 99
    > renders complete inside its column at the 402pt frame, with no ellipsis, no clipping and
    > no font shrinking.** Three digits is undefined and flagged rather than built. The label
    > side of this pressure eased when the chips became `PLAYER 1` rather than `PLAYER ONE`
    > (requirement 11), but the digits are what grow, and they are unchanged.

    > **The vertical budget, now fully numbered.** At the approved frame: 874pt, less 62pt
    > safe-area top (`P3-01` req 50) and 44–52pt bottom (handoff → Spacing), less the 370pt
    > board, less this strip's ≈56pt, less `P3-01` req 50's `stripToBoardGap` of **14pt** —
    > leaving roughly **320–328pt** for `P3-05-how-to-play.md`'s hint and legend (its req 13).
    > `P3-01` owns the screen and therefore the sum; this requirement states its own term.

18. **The strip's text does not scale with the iOS Dynamic Type setting** — but **this strip
    does not implement the clamp.** Flutter's default follows the OS factor, so honoring the
    Decision needs a `MediaQuery` clamp at the app root; this component installs no
    text-scaling override of its own.
    *Source: `Menus and UI.md` → Decisions → Do we support Dynamic Type? ("Not for now");
    `P4-01-main-menu.md` req 20, which disclaims the clamp identically, and
    `P4-04-settings.md` req 17, which records that **no PRD owns it**.*
    *Testable:* the strip's subtree contains no `MediaQuery` override of `textScaler`; with
    the app-root clamp installed, rendering at the largest iOS setting produces requirement
    17's computed height unchanged.
    > **Flagged:** until an app-level owner exists, requirement 17's height guarantee holds
    > only under the default text scale. Same gap as `P4-01` and `P3-05` req 21; it wants one
    > owner, not four component-level clamps.

### The host, its keys, and the row

19. **`GameScreen` hosts this strip, reads game state and the navigator, and passes both
    down** — `ref.watch(boardProvider)` (`P3-02` req 29) for `score`, `currentPlayer` and
    `isGameOver`, the three `ScoreboardLabels` constants of requirement 11, and
    `onSettingsPressed: () => ref.read(appNavigatorProvider).openQuickActions()`.
    **`GameScreen` is `P3-01-board-rendering.md`'s**, specified in its requirements 46–52 as a
    `ConsumerWidget` in `lib/ui/board/game_screen.dart`: req 47 places this strip first in the
    vertical stack, req 48 passes the board state, req 49 supplies the settings callback and
    mirrors requirement 12's screen-level assertion, req 50 fixes `stripToBoardGap`, and
    req 51 hosts the clear surface requirement 13 depends on.
    *Source: `P3-01-board-rendering.md` reqs 46–52; `P2-01-navigation.md` req 2, whose route
    table builds `GameScreen(id: GameId(...))`; `P3-02-move-input.md` req 29;
    `P1-02-engine-rules.md` reqs 36, 38, 39.*
    *Testable:* pumping `GameScreen` with an overridden `boardProvider` renders the strip with
    that board's score and current player; with an overridden `appNavigatorProvider`, tapping
    the gear records one `openQuickActions()`.
    **`ScoreboardStrip` reads exactly three providers and no others** —
    `activeThemeProvider` (requirement 14), and inside the settings button's tap handler
    `hapticServiceProvider` and `audioLayerProvider` (requirement 12). Notably **not**
    `boardProvider`, **not** `pendingSelectionProvider`, and **not** `appNavigatorProvider`.

20. **`ScoreboardKeys` publishes every key literal**, in `lib/ui/board/scoreboard_keys.dart`,
    in the shape of `P3-01` req 45's `BoardKeys`, together with the column enum:

    ```dart
    // lib/ui/board/scoreboard_keys.dart
    enum ScoreColumn { playerOne, ties, playerTwo }
    ```

    | Accessor | Key string | Present when |
    |---|---|---|
    | `strip` | `scoreboard.strip` | always |
    | `chip(ScoreColumn column)` | `scoreboard.chip.{playerOne\|ties\|playerTwo}` | always |
    | `chipActive(Player player)` | `scoreboard.chip.{playerOne\|playerTwo}.active` | that player is `currentPlayer` **and** `!isGameOver` |
    | `label(ScoreColumn column)` | `scoreboard.chip.<column>.label` | always |
    | `value(ScoreColumn column)` | `scoreboard.chip.<column>.value` | always |
    | `settingsButton` | `scoreboard.settingsButton` | `onSettingsPressed != null` |

    **`ScoreColumn` is this PRD's, `Player` is `P1-02` req 38's** — three columns, two
    players, which is the whole reason for the enum. Each accessor returns a
    `ValueKey<String>`; spelling follows `P1-02` req 8's convention. There is deliberately
    **no** `chipActive` for Ties: requirement 7 forbids the state.
    *Testable:* every key is present or absent exactly as its condition states, across an
    in-progress board, a finished board, and a strip built with `onSettingsPressed: null`.

21. **The row: three equal counters, each a label above its value, plus the button.** Left to
    right — the three counters as **equal-width columns**, then the settings button at the
    trailing edge. Within each counter the **label sits above the value**, stacked.
    *Source: `Game Board Design.md` → Scoreboard, whose ASCII draws exactly this — a row of
    three labels with the three values on the line beneath — and `Menus and UI.md` → How you
    reach settings from gameplay, which draws the gear at the top right.*
    *Testable:* at the 402pt frame the three counters have equal widths within a pixel, appear
    in the order of requirement 1, each renders its `label(...)` key above its `value(...)`
    key, and the button occupies the box requirement 14's precedence rule resolves — 44 × 44
    under Neon — at the trailing edge.

    **The layout constants.** Spacing is code, not theme (requirement 14), so these are
    `const` in `scoreboard_strip.dart`, **adopted from the approved handoff's `1d`** rather
    than invented. All are reversible; none is a theme value:

    | Constant | Value | From |
    |---|---|---|
    | Horizontal inset | **16pt** | `P3-01` req 4's board inset, so the strip's edges align with the board's |
    | Chip padding | **8pt vertical, 6pt horizontal** | `1d` — "padding `8/6`" |
    | Inter-chip gap | **6pt** | `1d` — "gap 6" |
    | Intra-chip gap, label to value | **2pt** | not drawn as a number; the smallest gap consistent with `1d`'s stacked chip, and an input to requirement 17's height |
    | Button box | **theme, else 44 × 44** | requirement 14's precedence rule |
    | Strip-to-board gap | **not this strip's** — it contributes no bottom margin | `P3-01` req 50's `stripToBoardGap`, 14pt |

    **The three chips are equal-height, and the mechanism is `IntrinsicHeight`.** All three
    paint to the row's full height, so an active chip's fill, border and glow box matches its
    neighbours' rather than hugging its own text and sitting visibly shorter.
    `Row(crossAxisAlignment: CrossAxisAlignment.stretch)` **will not do this here** and will
    fail at layout: stretch needs a bounded cross-axis constraint, and requirement 17
    deliberately leaves the height unbounded so it can grow with the theme. The row is
    therefore wrapped in `IntrinsicHeight`, which measures the tallest child and gives the
    others that height. **The cost is deliberate:** `IntrinsicHeight` is a second layout pass
    over its subtree, which is acceptable for a three-chip row rendered once per board state
    and would not be for the 81-cell board below it.
    *Testable:* the three chips' rendered heights are equal, and equal to requirement 17's
    computed strip height less nothing — with an active chip and two inactive ones, so the
    fill and border boxes are visibly the same size.

    > **Fenced — when `onSettingsPressed` is null the trailing box collapses** and the three
    > counters divide the full width. Reserving the width would make a button-less strip look
    > mysteriously indented, and nothing needs the space held.

22. **The tap sound in detail.** `AudioLayer.play(SoundMoment.buttonTap)` via
    `audioLayerProvider`, called unconditionally — the mute gate is inside the layer
    (`P2-02` req 16), so this call site never reads the sound setting, and with sound muted
    the call still happens.
    *Source: `Theming.md` → Decisions → *Do non-board controls make a sound?* — "**Yes — one
    tap sound, everywhere.**"; `P2-02-audio.md` req 6.*
    **The call site of record is requirement 12**, which is what `P2-02` req 6's wave note and
    its Out of Scope table both cite; this requirement carries the mechanism, not a second
    site. The exactly-once assertion lives with requirement 12's strip-level testable.

## Out of Scope

- **Where the score is stored** — `P1-04-persistence.md`.
- **Performing the increment, outcome detection, the series score as data, and turn order
  across games** — `P1-02-engine-rules.md` (reqs 20–22, 24–27).
- **Clearing the pending selection** — `P2-01-navigation.md` req 20 on navigation,
  `P3-02-move-input.md` req 26 on taps, `P3-01` req 51's surface.
- **The icon resolver** — `lib/theme/`, per `P1-05` and `P1-03`.
- **The haptic and audio layers themselves** — `P2-03-haptics.md`, `P2-02-audio.md`. This PRD
  owns only the call site.
- **The app-root Dynamic Type clamp** — unowned; see requirement 18.
- **The game-over surface — the result card, its two buttons, the dimmed board behind it, and
  its own score chips** — `P3-04-game-over-rematch.md`; hosted by `P3-01` req 52.
- **What the settings button opens** — `P4-04-settings.md`. **The route it invokes** —
  `P2-01-navigation.md`.
- **`GameScreen`, the strip-to-board gap's value, and the screen's vertical sum** —
  `P3-01-board-rendering.md` reqs 46–52.
- **`BoardView` and its highlights** — `P3-01-board-rendering.md`; **the on-board legend,
  hint text and the free-choice cue** — `P3-05-how-to-play.md`.
- **The open-games list and its per-row score chips** — `P4-02-open-games-list.md`.
- **Real player names.** Requirement 11 keeps the swap cheap; it does not add the feature.
- **Animating the scoreboard or the turn highlight.** `Animations.md` → Scope For Now scopes
  animation to the player's marker only.

## Open Questions

### 1. Closed — kept so they are not re-raised

- **What the chips read.** `PLAYER 1` / `TIES` / `PLAYER 2` — `Game Board Design.md` →
  Decisions → *What do the scoreboard chips read?* Requirement 11.
- **Where the three label strings live.** `ScoreboardLabels`, requirement 11 — filling the
  ellipsis in `P3-01` req 48.
- **Does the settings gear buzz?** Yes — `Game Board Design.md` → Decisions → *Does the
  haptic fire on non-board controls?*; `P2-03` OQ-2 closed, naming requirement 12.
- **Does it click?** Yes — `Theming.md` → Decisions → *Do non-board controls make a sound?*;
  `P2-02` req 6 lists requirement 12 as the sixth `buttonTap` site.
- **Who owns `GameScreen`?** `P3-01-board-rendering.md` reqs 46–52 — landed text, not an
  assignment in flight. With it go `stripToBoardGap` (14pt, its req 50), the clear surface
  (req 51), the game-over overlay (req 52) and the screen's vertical sum.
- **Who applies `chipLabel.uppercase`?** Each component, at render. `P4-01` req 2 does it for
  the menu; requirement 11 does it here. Duplication to consolidate one day, not an absence.
- **The turn banner is not built, and the free-choice cue lives below the board.**
  `surfaces.scoreboard.turnBanner` was **removed in v5**.
- **`surfaces.scoreboard.turnIndicator`** — **removed in v6**, on this PRD's report.
- **`surfaces.scoreboard.{padding,gap}`** — **removed in v7** with every spacing key; spacing
  is code. Requirement 21 holds the constants.
- **Whether the active treatment paints the whole counter or only the name.** The chip keys
  carry `fill`, `border`, `glow`, `labelStyle`, `valueStyle` per player per state.
- **Whose component draws the game-over score chips.** `P3-04` req 13's are 27/600.
- **Is the player dependent on the settings button to leave a finished game?** No.
- **Which PRD owns the increment.** `P1-02` req 27. **Which publishes the board provider.**
  `P3-02` req 29.

### 2. Needs the user's call — each carries a fenced default, so nothing is blocked

- **Is the scoreboard strip inside or outside the game-over dim?** `Menus and UI.md` →
  Decisions → *What does the player see when a game ends?* settles "a result card drawn over
  the board, with the board dimmed behind it." **The strip is not the board.** *Fenced
  default: outside the dim, at full brightness.* At full brightness the player reads the score
  twice at once, here and in the card's own chips; under a full-screen scrim the strip recedes
  and the card carries the score alone. `P3-01` req 52 hosts the overlay either way.
- **Does the settings button render over the result card?** Requirement 12 fences **yes**.
  Presentation only — the card is self-sufficient.
- **What does the turn indicator show on a finished game?** Requirement 7 fences "no counter
  highlighted." Answering it also decides whether `P1-02` should freeze `currentPlayer`.
- **Under `chipLabel.uppercase: false`, does the chip read `Player 1` or `PLAYER 1`?**
  Requirement 11 fences `Player 1`. Only reachable via a theme that turns the flag off; Neon
  does not.
- **How do the counters read past 99?** Requirement 17 fences ≤99 inside an equal-width
  column. What gives at three digits — a smaller value style, an unequal column, or a cap — is
  unsettled.
