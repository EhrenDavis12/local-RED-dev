# PRD: Scoreboard and Turn Indicator

> **Status:** Draft · Source docs read: `Game Board Design.md`, `Game Overview.md`,
> `Menus and UI.md`, `Theming.md`, `Rules.md`, `Tech Design.md`, `Animations.md`.
> (`Alternative Game Styles.md` is a parking-lot doc and was not sourced.
> `design_handoff_game_ui/` is a read-only reference asset — screens `1d`/`1e` draw this
> strip; no requirement below is sourced from it, and where it goes beyond the design docs
> that is recorded in Open Questions.)

**Wave:** P3 — the game screen wave, alongside `P3-01-board-rendering.md`.

**Dependencies:**

- `P1-02-engine-rules.md` — supplies whose turn it is, the running series score, and the
  increment itself: its requirement 27 moves the winner's or Ties column on the move that
  ends the game, and its requirements 20–22, 24–26 own outcome detection, the series state
  and turn order. This PRD displays those values and performs none of that.
- `P1-03-theme-system.md` — every value on this strip is read from the active theme.
  Requirement 14 below names the slots this strip needs; `P1-03` requirement 15 currently
  names "turn indicator" and "scoreboard" as one bundle each, which is coarser than what
  this strip renders.
- `P1-04-persistence.md` — where the score is stored and how each open game carries its
  own scoreboard.
- `P2-01-navigation.md` — **wave 2, ships before this PRD.** Its requirement 7 holds the
  rule that settings is reachable from exactly two entry points, one of them "the game
  screen's top-right button," and its requirement 10 holds that opening that surface does
  not leave the game. Requirement 12 below places that button and invokes that entry
  point; it does not define the route.
- `P3-01-board-rendering.md` — shares the game screen; this strip sits above it.
- `P3-04-game-over-rematch.md` — presents the finished game and offers the rematch. It
  does **not** change the score (its Out of Scope disclaims "the score as data, the
  increment itself"), and its requirements 11–12 cover what the *result surface* says
  about the score, not this strip.

> **One forward reference, deliberately narrow.** Requirement 12 places a settings button on
> this strip and requires that activating it invokes the settings entry point. What that
> button *opens* is `P4-04-settings.md`'s, which is a **later wave**. This is not a build
> dependency — the button and its position ship here, the route exists from wave 2
> (`P2-01-navigation.md`), and the destination surface is wired when that PRD lands — but it
> is the one place this PRD points forward, and it is flagged rather than hidden.

## Problem

Two players share one phone and pass it back and forth, so the screen is the only thing
telling them who is up (`Game Board Design.md` → Turn Indicator). With no scoreboard and
no turn indicator, a player handed the phone cannot tell whose move it is, and nothing
records that they are on their fourth game in a row — which is the whole shape of play the
app is built around: "playing several in a row on the same phone"
(`Game Overview.md` → Session Structure — Games and Continuing).

## Goal

The game screen carries a scoreboard strip above the board showing three counters —
Player One, Ties, Player Two — for the open game being played, with the active player's
name highlighted so whoever is handed the phone can see at a glance whose turn it is, and
a settings button at its top right as the mid-game way into quick actions. The strip is
entirely theme-driven, and it fits above a full 81-cell board on a portrait phone without
the board losing any of its visibility.

## Requirements

### The scoreboard

1. **The game screen shows a scoreboard at the top, above the board, holding exactly three
   counters labelled Player One, Ties, and Player Two, in that order.**
   *Source: `Game Board Design.md` → Scoreboard (the three-column table and the ASCII
   layout); `Game Overview.md` → Session Structure — Games and Continuing ("A scoreboard
   at the top of the game screen tracks Player One / Ties / Player Two").*
   *Testable:* the game screen renders three labelled counters in that order above the
   board.

2. **The screen is a vertical stack: scoreboard on top, board below.**
   *Source: `Game Board Design.md` → Visual Layout ("Vertical stack: scoreboard on top,
   board below").*

3. **The counters show the running score of the open game currently being played.** Each
   open game has its own score; this strip shows the one belonging to the game on screen.
   Where that value lives is `P1-04-persistence.md`'s.
   *Source: `Game Overview.md` → Decisions → Scoreboard lifetime ("Each open game carries
   its own scoreboard"); `Menus and UI.md` → Decisions → What does an open game hold?*
   *Testable:* rendering two different open games renders their two different scores.

4. **The strip shows the incremented score from the moment the game ends** — as soon as the
   game is won or tied, the winner's column, or Ties, reads one higher. It does not wait for
   a rematch to be taken; taking the rematch only resets the board. So while the game-over
   state is on screen, the strip already shows the new score. This strip renders the score
   the engine reports and never increments anything itself: performing the increment belongs
   to `P1-02-engine-rules.md` requirement 27, which binds it to the move that ends the game.
   *Source: `Menus and UI.md` → Decisions → When does the scoreboard increment ("**At game
   end.** The winner's column, or Ties, increments as soon as the game is won or tied — not
   when a rematch is taken. Taking the rematch only resets the board"); → Decisions → What
   happens when a game ends?; → Game Over → Rematch; `Game Overview.md` → Session Structure
   — Games and Continuing ("Continuing **resets the board**. The score increments at game
   end, not when continuing is taken"); `Game Board Design.md` → Scoreboard ("Increments
   when a game ends: the winner's column, or the Ties column on a tie"); `Rules.md` → Big
   board full with no three-in-a-row ("The Ties counter on the scoreboard goes up one").*
   *Testable:* play a game to a win with the score at 2–1–0; at the instant the game is over
   and before any rematch input, the strip reads 3–1–0. Play one to a straight draw and the
   Ties column, not a player column, is the one that changed. Rendering the same finished
   game twice shows the same three values both times — this component contributes no
   counting of its own.

5. **The scoreboard carries across games in a series rather than resetting.** Continuing
   into the next game resets the board but not the counters, so a session reads as a running
   series.
   *Source: `Game Overview.md` → Session Structure — Games and Continuing ("Continuing
   **resets the board**… The scoreboard carries across games so a session becomes a running
   series"); `Menus and UI.md` → Game Over → Rematch ("The rematch continues in the same
   open game — same series, scoreboard intact"); → Decisions → What does an open game hold?*
   *Testable:* after a rematch resets the board, the three counters read exactly what they
   read before the rematch was taken.

### The turn indicator

6. **The active player's name in the scoreboard is highlighted, and that highlight is the
   game screen's "whose turn it is" affordance.** No separate mechanism is specified for
   it here.
   *Source: `Game Board Design.md` → Turn Indicator ("The active player's name in the
   scoreboard is highlighted to show whose turn it is… This is the mechanism for the
   'whose turn it is' affordance"); → Player Feedback / Affordances ("Whose turn it is —
   … Needs to be unmissable").*
   *Testable:* with Player One to move, the Player One counter renders in the highlighted
   state and the Player Two counter does not.

7. **Exactly one of the two player counters is highlighted at any time.** The Ties counter
   is a counter only and never carries the active-turn highlight — turns alternate between
   Player One and Player Two, so there is always exactly one active player.
   *Source: `Game Board Design.md` → Turn Indicator (singular "the active player's name");
   `Game Overview.md` → Modes ("Turns alternate Player One → Player Two → Player One →
   Player Two"); `Menus and UI.md` → A New Game → What It Starts.*
   *Testable:* across every turn of a played-out game, the count of highlighted counters is
   always 1 and the Ties counter is never it.

8. **The highlight moves to the other player when a move is confirmed, not when a cell is
   selected.** The first tap of the two-tap move does not change the turn indicator; the
   confirming tap does, and the change is immediate — there is no intermediate
   "pass the phone" state.
   *Source: `Game Board Design.md` → Move Input ("Tapping the same cell again commits the
   move. The mark is placed and the turn passes"); `Menus and UI.md` → Pass-and-Play Turn
   Handoff ("The game switches the active player automatically after each move… The handoff
   can be instant").*
   *Testable:* after the first tap the same counter stays highlighted; after the second tap
   the other one is highlighted, with no screen in between.

9. **Which player is highlighted at the start of a game is read from the engine, not
   decided here.** Turn order within and across games is `P1-02-engine-rules.md`'s.
   *Source: `Rules.md` → Turn Order Across Games; `Rules.md` → Decisions → Who goes first
   after a tie?*

### Player labels

10. **The two players are always labelled "Player One" and "Player Two" on this strip.** The
    opponent name entered at New Game does not appear here — it titles the game in the
    open-games list and nothing else.
    *Source: `Game Overview.md` → Decisions → Player names ("Always 'Player One' and 'Player
    Two' — no custom names… The opponent name entered at New Game does not replace 'Player
    Two' on the in-game scoreboard"); `Menus and UI.md` → Decisions → Does the opponent name
    replace "Player Two" in game? ("No — not at this moment").*
    *Testable:* a game created with opponent name "ItSaMeMaRiO" renders "Player Two" on the
    scoreboard, and the opponent name appears nowhere on the game screen.

11. **The two labels are supplied to the scoreboard as data, not written as literals inside
    its layout code**, so swapping in real player names later is a change at the caller and
    does not require editing this component.
    *Source: `Game Overview.md` → Decisions → Player names ("With the option to change that
    later. Don't hardcode the strings in a way that fights adding real names down the
    road"); `Menus and UI.md` → Decisions → Does the opponent name replace "Player Two" in
    game? ("don't build it in a way that makes the swap hard to make later").*
    *Testable:* a widget test can render the scoreboard with two arbitrary name strings and
    see them displayed, with no change to the scoreboard's own source.

### Settings button

12. **A settings button sits at the top right of the game screen, alongside the
    scoreboard**, and activating it invokes the game-screen settings entry point held by
    `P2-01-navigation.md` requirement 7. What that entry point opens is `P4-04-settings.md`'s;
    this PRD requires only the button, its position, and that invocation.
    *Source: `Game Board Design.md` → Scoreboard ("A settings button sits at the top right,
    alongside the scoreboard — the mid-game entry point to quick actions and exiting the
    game"); `Menus and UI.md` → How you reach settings from gameplay; → Decisions → How do
    you get back to the main menu from a game?; `P2-01-navigation.md` requirement 7
    ("Settings is reachable from exactly two entry points — the main menu's Settings button
    and the game screen's top-right button — and from nowhere else").*
    *Testable:* the game screen renders exactly one settings control, in the top-right
    position alongside the scoreboard; activating it calls the navigation layer's
    game-screen settings entry point exactly once, and calls no other route — assertable
    against a test double for that layer without `P4-04-settings.md` existing. Per
    `P2-01-navigation.md` requirement 10 the game is still mounted afterwards.
    *Note on wave order:* the route ships in wave 2 and the surface it opens ships in wave 4;
    this button and its invocation ship here, in between.

### Styling and fit

13. **Every visual value on this strip comes from the active theme — scoreboard styling and
    turn-indicator styling alike.** No colors, fonts, sizes, or motion values are written
    into this component's code.
    *Source: `Theming.md` → Architectural Rule ("No hardcoded colors, backgrounds, fonts…
    Every visual, audio, and motion value is read from the currently selected theme"); →
    What a Theme Controls (lists "Turn indicator styling" and "Scoreboard styling");
    `Game Board Design.md` → Everything Here Is Theme-Driven, → Turn Indicator ("what the
    highlight looks like is theme-driven").*
    *Testable:* the hardcoded-theme-value test (`P1-05-theme-guard-test.md`) reports zero
    violations for these files.

14. **The theme slots this strip needs, at the grain it needs them.** Requirement 13 is
    unbuildable against two bundled slots: `P1-03-theme-system.md` requirement 15 names
    "turn indicator" and "scoreboard" as one slot each, while what this strip renders varies
    **per player** and **per state**. The slots this PRD requires the theme object to carry:

    | Slot | Needed by |
    |---|---|
    | Strip container background | requirement 1 |
    | Inter-counter gap; counter padding; counter corner radius | requirements 1, 16 |
    | Inactive counter surface, and its outline | requirements 1, 7 |
    | **Active counter fill, border and glow — one per player** | requirements 6, 7 |
    | **Active and inactive label color — one pair per player** | requirements 6, 7 |
    | Counter *label* typography and counter *value* typography, as two slots | requirement 1 |
    | The Ties counter's own treatment | requirement 7 — it can never take the active state, so it cannot borrow a player's |
    | The settings icon button's icon asset and its tint | requirement 12 — `P1-03` covers no icon-button slot today |

    Naming a slot decides nothing about its value: what any of these look like is the
    theme's, and Neon's values are the handoff's.
    *Source: `Theming.md` → Architectural Rule ("No hardcoded colors, backgrounds, fonts…
    everywhere"), → What a Theme Controls (turn indicator styling, scoreboard styling);
    `Game Board Design.md` → Turn Indicator ("what the highlight looks like is
    theme-driven"). That the grain is per-player and per-state is what this strip's own
    requirements 6, 7 and 12 require; `design_handoff_game_ui/README.md` → 1d/1e draws it
    that way (each active chip tinted in its own player's color) and is cited as evidence
    of the grain, not as the source of any value.*
    *Testable:* every value this component reads resolves through a named theme slot, and
    changing the active theme changes all of them with no code change.

15. **What the turn highlight looks like is a theme value, and every theme must keep it
    legible.** The component states *that* a counter is active; the theme decides how that
    reads.
    *Source: `Game Board Design.md` → Turn Indicator; `Theming.md` → What a Theme Controls
    (the note that these treatments must stay legible in every theme, "not just the default
    one").*

16. **The scoreboard fits above the board on a portrait phone with the whole 9x9 board
    still visible and no zoom or scrolling.** The strip costs vertical space that a board
    with 81 cells needs, and the board's full visibility is the constraint that wins.
    *Source: `Game Board Design.md` → Scoreboard ("Takes vertical space away from the board
    — worth noting given the board already has 81 cells to fit on a phone"); → Responsive /
    Screen Size ("No zoom. The whole 9x9 grid stays visible at all times"); `Tech Design.md`
    → Decisions → Orientation — portrait only.*
    *Testable:* on the target portrait phone frame, the scoreboard, the settings button and
    all 81 cells are laid out without overflow and without a scroll view.
    Note that `P3-05-how-to-play.md` competes for the same vertical budget from below the
    board; its requirement 13 states the same constraint from the other end.

17. **The strip's text does not scale with the iOS Dynamic Type setting.**
    *Source: `Menus and UI.md` → Decisions → Do we support Dynamic Type? ("Not for now").*

## Out of Scope

- **Where the score is stored, and each open game carrying its own scoreboard through
  persistence** — `P1-04-persistence.md`.
- **Performing the increment, outcome detection, the series score as data, and turn order
  across games** — `P1-02-engine-rules.md` (requirements 20–22, 24–27). Requirement 4 states
  *when* the increment lands because this strip must show it then, not because this layer
  performs it.
- **The game-over surface — the winner and draw modals, the rematch control, and what that
  surface says about the score** — `P3-04-game-over-rematch.md` (its requirements 11–12).
  That PRD does not change the score either.
- **What the settings button opens** — the quick-actions contents, the toggles, and exiting
  to the main menu: `P4-04-settings.md`. **The route it invokes** —
  `P2-01-navigation.md` (requirements 7 and 10).
- **The board itself**, its highlights and its tap handling — `P3-01-board-rendering.md`
  and `P3-02-move-input.md`.
- **The on-board legend and hint text below the board** — `P3-05-how-to-play.md`.
- **The free-choice text cue's existence and wording** — `P3-05-how-to-play.md`
  requirement 10 owns it; only its *host* is open here (Open Question 1).
- **The open-games list and its per-row score chips** — a different screen with different
  labels; `P4-02-open-games-list.md`.
- **Real player names.** Requirement 11 keeps the swap cheap; it does not add the feature.
- **Animating the scoreboard or the turn highlight.** `Animations.md` → Scope For Now
  scopes animation to the player's marker only, and nothing in the docs asks for a
  scoreboard animation. The animation layer itself is `P2-04-animations.md`.

## Open Questions

### 1. Is the handoff's turn banner built, and if not, where does the free-choice cue live?

`Game Board Design.md` → Turn Indicator names the highlighted name in the scoreboard as
*the* mechanism for the whose-turn affordance. The approved handoff draws a second element
the design docs never mention: a **turn banner** below the scoreboard row carrying
"Player One, you're up!" plus a mode cue ("Free choice — pick any board" / "Play the middle
board"), and on `2d` it switches to a provisional voice for a pending move
(`design_handoff_game_ui/README.md` → 1d, 1e, 2d).

Two things are unsettled:

- **Whether the banner is built at all.** If it is, whether it belongs to this feature or to
  `P3-01-board-rendering.md` is the second half of that call — its mode cue describes board
  state, not score.
- **Which element hosts the free-choice text cue.** The cue itself is owned and required:
  `P3-05-how-to-play.md` requirement 10 requires that the free-choice state is stated in
  words, and `P3-01-board-rendering.md` requirement 21 builds the highlight half and
  explicitly leaves the text half to that PRD. What is open is only its host — the handoff
  puts it inside the banner, and `P3-05` places its own explanatory layer *below* the board.
  So this is a two-way question between this PRD and `P3-01`/`P3-05`'s bottom strip, not a
  cue with no home.

Relatedly, the docs highlight *the name*, while the handoff tints the whole counter chip in
the active player's color — settled either way only once the banner question is.
*(`Menus and UI.md` → Open Questions carries the underlying question.)*

### 2. Gaps found while writing this PRD (flagged by the PRD author, not asked by the docs)

None is resolved here; each is a place an implementer would otherwise guess.

- **Whether the settings button stays available and active while a game-over state is on
  screen.** The button is the only way out of a game (`Menus and UI.md` → Decisions → How
  do you get back to the main menu from a game?), and the game-over state overlays the
  finished board — but nothing settles whether it remains reachable underneath. Also
  carried by `P3-04-game-over-rematch.md` → OQ3 and `P2-01-navigation.md` → Open Question
  12.
- **Whether the settings button buzzes.** This PRD is silent, and the docs' haptic rule is
  written app-wide ("the haptic fires on every valid click") but justified entirely by the
  board's 81 small targets. `P3-04-game-over-rematch.md` requirement 15 already reads it
  broadly and fires the haptic on Rematch as "a valid action," while
  `P2-03-haptics.md` → OQ-2 records that whether non-board controls buzz at all is
  unsettled. As things stand, two sibling PRDs' implementers would guess differently about
  two controls on the same screen.
- **Whose component draws the score chips inside the game-over surface.**
  `P3-04-game-over-rematch.md` requirement 11 requires the scoreboard shown as part of the
  result with the moved column identifiable. If that is this component re-rendered, two
  things collide: the handoff's `1h` highlights the **TIES** chip, which requirement 7 here
  forbids ever taking the active state, and the `+1` treatment both `1g` and `1h` draw has
  no slot in requirement 14. If it is a separate component, the two must not drift.
- **How the counters read once a series runs long.** Nothing settles a maximum score, a
  digit budget, or what the layout does at double or triple digits, and requirement 16
  makes the strip's height the tight dimension.
