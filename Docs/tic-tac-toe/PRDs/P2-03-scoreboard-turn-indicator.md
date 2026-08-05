# PRD: Scoreboard and Turn Indicator

> **Status:** Draft · Source docs read: `Game Board Design.md`, `Game Overview.md`,
> `Menus and UI.md`, `Theming.md`, `Rules.md`, `Tech Design.md`, `Animations.md`.
> (`Alternative Game Styles.md` is a parking-lot doc and was not sourced.
> `design_handoff_game_ui/` is a read-only reference asset — screens `1d`/`1e` draw this
> strip; no requirement below is sourced from it, and where it goes beyond the design docs
> that is recorded in Open Questions.)

**Wave:** P2 — the game screen wave, alongside `P2-01-board-rendering.md`.

**Dependencies:**

- `P1-02-engine-rules.md` — supplies whose turn it is and the running score. This PRD
  displays those values and defines none of the rules behind them.
- `P1-03-theme-system.md` — every value on this strip is read from the active theme.
- `P1-04-persistence.md` — where the score is stored and how each open game carries its
  own scoreboard.
- `P2-01-board-rendering.md` — shares the game screen; this strip sits above it.
- `P2-04-game-over-rematch.md` — owns the game-over flow that changes the score. This PRD
  owns only what the strip shows.

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
   state is on screen, the strip already shows the new score. Performing the increment is
   part of the game-over flow and belongs to `P2-04-game-over-rematch.md`; this PRD requires
   only that the strip reflects it at that moment.
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
   Ties column, not a player column, is the one that changed.

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
    scoreboard**, and is the mid-game entry point. What it opens is
    `P3-04-settings.md`'s; this PRD requires only that it is present in that position on
    the game screen and that activating it invokes that entry point.
    *Source: `Game Board Design.md` → Scoreboard ("A settings button sits at the top right,
    alongside the scoreboard — the mid-game entry point to quick actions and exiting the
    game"); `Menus and UI.md` → How you reach settings from gameplay; → Decisions → How do
    you get back to the main menu from a game?*

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

14. **What the turn highlight looks like is a theme value, and every theme must keep it
    legible.** The component states *that* a counter is active; the theme decides how that
    reads.
    *Source: `Game Board Design.md` → Turn Indicator; `Theming.md` → What a Theme Controls
    (the note that these treatments must stay legible in every theme, "not just the default
    one").*

15. **The scoreboard fits above the board on a portrait phone with the whole 9x9 board
    still visible and no zoom or scrolling.** The strip costs vertical space that a board
    with 81 cells needs, and the board's full visibility is the constraint that wins.
    *Source: `Game Board Design.md` → Scoreboard ("Takes vertical space away from the board
    — worth noting given the board already has 81 cells to fit on a phone"); → Responsive /
    Screen Size ("No zoom. The whole 9x9 grid stays visible at all times"); `Tech Design.md`
    → Decisions → Orientation — portrait only.*
    *Testable:* on the target portrait phone frame, the scoreboard, the settings button and
    all 81 cells are laid out without overflow and without a scroll view.

16. **The strip's text does not scale with the iOS Dynamic Type setting.**
    *Source: `Menus and UI.md` → Decisions → Do we support Dynamic Type? ("Not for now").*

## Out of Scope

- **Where the score is stored, and each open game carrying its own scoreboard through
  persistence** — `P1-04-persistence.md`.
- **Incrementing the score as part of the game-over flow, the winner/draw modals, and
  rematch** — `P2-04-game-over-rematch.md`. This PRD states the display requirement only.
- **What the settings button opens** — the quick-actions contents, the toggles, and exiting
  to the main menu: `P3-04-settings.md`.
- **The board itself**, its highlights and its tap handling — `P2-01-board-rendering.md`.
- **Turn-order rules within and across games**, including who goes first after a win or a
  tie — `P1-02-engine-rules.md`.
- **The open-games list and its per-row score chips** — a different screen with different
  labels; `P3-02-open-games-list.md`.
- **Real player names.** Requirement 11 keeps the swap cheap; it does not add the feature.
- **Animating the scoreboard or the turn highlight.** `Animations.md` → Scope For Now
  scopes animation to the player's marker only, and nothing in the docs asks for a
  scoreboard animation.

## Open Questions

### 1. Is the handoff's turn banner part of this feature?

`Game Board Design.md` → Turn Indicator names the highlighted name in the scoreboard as
*the* mechanism for the whose-turn affordance. The approved handoff draws a second element
the design docs never mention: a **turn banner** below the scoreboard row carrying
"Player One, you're up!" plus a mode cue ("Free choice — pick any board" / "Play the middle
board"), and on `2d` it switches to a provisional voice for a pending move
(`design_handoff_game_ui/README.md` → 1d, 1e, 2d).

Two things are unsettled as a result: whether the banner is built at all, and if so whether
it belongs to this feature or to `P2-01-board-rendering.md` (its mode cue describes board
state, not score). Relatedly, the docs highlight *the name*, while the handoff tints the
whole counter chip in the active player's color — settled either way only once the banner
question is.

### 2. Gaps found while writing this PRD (flagged by the PRD author, not asked by the docs)

Neither is resolved here; both are things an implementer would otherwise guess.

- **Whether the settings button stays available and active while a game-over state is on
  screen.** The button is the only way out of a game (`Menus and UI.md` → Decisions → How
  do you get back to the main menu from a game?), and the game-over state overlays the
  finished board — but nothing settles whether it remains reachable underneath.
- **How the counters read once a series runs long.** Nothing settles a maximum score, a
  digit budget, or what the layout does at double or triple digits, and requirement 15
  makes the strip's height the tight dimension.
