# Menus and UI

> **Status:** Brain dump. Contradictions are expected and OK.
>
> **Approved UI design:** `Docs/tic-tac-toe/design_handoff_game_ui/README.md` —
> [Design Handoff](./design_handoff_game_ui/README.md). Every screen here now has a
> drawn counterpart — the per-screen map is in **Screens (so far)** below. Reference
> asset — read-only.

## Main Menu
The game needs a main menu.

**Buttons:**
- **Play Game** — if there are no existing games, takes the player straight into a new
  two-player same-phone game. If there are existing games, takes the player to a screen
  listing all open games. Large.
- **Theme** — opens theme selection. Large, same weight as Play Game.
  See [Theming](./Theming.md).
- **Settings** — opens the settings menu. Smaller than the two above it.
- **About Us** — last in the list, same smaller treatment as Settings.

**Settings and About Us sit side by side in one row**, sharing its width — not two more
full-width buttons stacked under Play Game and Theme. So the menu has two button tiers:
the big pair, and the small pair beneath them.

**Play Game and Theme are the same tier, not merely similar.** Both draw from one
treatment, so a change to one is a change to both and no theme can drift them apart.

Themes are deliberately **up front**, not buried in settings. The theme button gets the
same visual weight as Play Game.

Button labels are written the way they read — **Play Game**, not **PLAY GAME**. Whether a
label renders in caps is a theme value like anything else, so the caps in the sketch below
are Neon's choice, not part of the label.

**The main menu has a title and a logo.** Both, not just buttons. The title is two parts —
**TIC TAC TOE** above, **EXTREME** beneath it as the wordmark. Under the title sits the
tagline, *"Nine boards. One winner. Good luck."* The logo is a placeholder for now, a
dashed-bordered mark standing in for real art.

**A footer line runs along the foot of the menu**, carrying the active theme's name and
the app version — `Theme: Neon · v0.1.0` under Neon.

```
┌─────────────────────────┐
│                         │
│         [ LOGO ]        │
│       TIC TAC TOE       │
│         EXTREME         │
│ Nine boards. One winner.│
│        Good luck.       │
│                         │
│   ┌─────────────────┐   │
│   │                 │   │
│   │    PLAY GAME    │   │
│   │                 │   │
│   └─────────────────┘   │
│                         │
│   ┌─────────────────┐   │
│   │      THEME      │   │
│   └─────────────────┘   │
│                         │
│  ┌────────┐ ┌────────┐  │
│  │SETTINGS│ │ABOUT US│  │
│  └────────┘ └────────┘  │
│                         │
│   Theme: Neon · v0.1.0  │
└─────────────────────────┘
```

The entire main menu is itself theme-driven — background, button styling, title. No
hardcoded styling here either.

**While theme selection is open, the main menu dims behind it.** The menu stays where it
is underneath the overlay — it drops its own opacity, which is the menu's own job, and the
overlay lays its scrim on top of that. Two layers, not one.

### About Us
**About Us ships, and its button goes last in the main menu button list.** In the user's
words:

> "We want the about us but it can be the last button in the list for now we might move it
> in the future but lets add it here."

So the main menu carries four buttons, in order: Play Game, Theme, Settings, About Us. The
position is explicitly provisional — the user said "for now we might move it in the
future" — so a later reordering is expected rather than a reversal.

Because Settings and About Us share a row, that pairing is the part a later reorder has to
revisit — nothing else in the menu depends on About Us being last.

Two things this doesn't settle:
- The screen's **content** is not specified by any doc. The handoff draws team photos;
  where those come from is not decided.
- **No PRD currently owns the About Us screen.** The main-menu PRD covers the button; the
  screen itself has no owner yet.

## Play Game → Where It Takes You
Play Game branches on whether there are existing open games.

- **No open games** — straight into a new game, no intermediate screen.
- **Open games exist** — a new screen listing all open games, with **New Game** as an
  option at the **top of the list**.
- **Each open game is titled with its opponent's name** — that's what a row shows.
- **Selecting New Game prompts for the opponent's name**, with a default of
  **ItSaMeMaRiO**.

```
┌─────────────────────────┐
│      OPEN GAMES         │
│                         │
│   ┌─────────────────┐   │
│   │    NEW GAME     │   │
│   └─────────────────┘   │
│                         │
│   ┌─────────────────┐   │
│   │  OPPONENT NAME  │   │
│   └─────────────────┘   │
│                         │
│   ┌─────────────────┐   │
│   │   ItSaMeMaRiO   │   │
│   └─────────────────┘   │
│                         │
└─────────────────────────┘
```
Each open game is titled with its opponent's name. ItSaMeMaRiO is the default.

Undecided: whether the empty-state path (no open games → straight into a new game) also
shows the opponent-name prompt, or skips it. "No intermediate screen" and the prompt
can't both be true on that path.

**The opponent name does not replace "Player Two" in game.** It titles the game in the
open-games list and nothing else. In game, the players are still **Player One** and
**Player Two**. That might change in the future, so don't build it in a way that makes the
swap hard to make later. See [Game Overview](./Game%20Overview.md) →
Session Structure — Games and Continuing.

### What an open game holds
**An open game holds a whole series — the board plus the running score.** A rematch
continues in the same open game with the scoreboard intact, and resuming a game from the
open-games list resumes the *series*, not just the last individual board.

It also fixes what the count below is counting — the three open games we keep are three
series.

### How many open games we keep
**3 by default, no more.** A **$4.99 in-app purchase raises the cap to 100 open game
slots.**

What each of those 3 (or 100) holds is a whole series — see **What an open game holds**
above.

### Deleting an open game
**The open-games list carries a delete action, so a slot can be freed.** With a cap of 3
and a rematch staying in the same open game, nothing else frees a slot.

**Swipe left on the row → a trash button appears → tap it → a modal asks whether to
permanently delete this game, with Yes and No → Yes deletes, No dismisses the modal.** In
the user's own words:

> "It should be a slide left a trash button shows up, Click it, A modal pops up saying
> permanently delete this game with Yes and No, On Yes delete the game, On no exit the
> modal"

The revealed control is a **trash button** — an icon, not a worded "Delete" label. The
modal's buttons are **Yes and No**, not Cancel/Delete.

The confirmation is there because deleting a game is the only irreversible action in the
app — it destroys the game and its whole running scoreboard — and kids are a stated target
audience (see [Game Overview](./Game%20Overview.md) → Target Audience & Platform).

Consequence for theming: this is the first affordance that needs a **destructive**
treatment, which the theme schema currently holds as deferred, precisely because nothing
has been drawn for it. The approved handoff draws no delete affordance at all on screen
`1b` — this section is the source of the affordance, not the drawing.

## A New Game → What It Starts
- A **two player game on the same exact phone**. One device, passed back and forth.
- Turn order alternates: Player One → Player Two → Player One → Player Two → ...
- After a player makes their move, it becomes the other player's turn.
- No AI opponent, no online play in this version.

## Pass-and-Play Turn Handoff
- The game switches the active player automatically after each move.
- The UI has to make it obvious *whose turn it is right now*, since both players are
  looking at the same screen.
- Note: tic-tac-toe has no hidden information, so there's no need for a "pass the phone,
  don't peek" screen between turns. The handoff can be instant.

## How to Play — the On-Board Legend and Hint
**The game explains its own central mechanic — this is in scope to build out.** The
approved handoff makes this strip **state-dependent** — what it says changes with what the
board is doing:
- `1d` (opening move / free choice) — the legend (Open · Locked · Cat game) **and** the
  hint *"Tap a square to see where it sends them. / Tap it again to play it."*
- `1e` (forced quadrant + last move) — neither of those. Its bottom strip instead carries
  two lines explaining the two rings: *"They played here last — that's what sent you."* /
  *"The only board you can play in right now."*
- `2d` (pending move) — a third, different pair of lines, and the explanation is split
  across two surfaces. The turn banner carries *"Play here?"* / *"Tap again to lock it
  in."*, and the bottom strip carries its own pair: *"Your pick, not played yet — and
  where it sends them."* / *"Still showing what they did last — it stays until you
  commit."*

**The strip only explains what is actually on screen.** A line about a ring that isn't
there is dropped, and its swatch with it — on the opening move nobody has played yet, so
the last-move line doesn't render.

**The hint is the only place in the whole product that says the two-tap mechanic exists**,
so neither half of it can be dropped if the copy is ever rewritten. The preview half is
what teaches the sending rule, and the "tap it again" half is what stops a first tap
reading as a failure.

The sending rule is the hardest thing in the game to explain, kids are a stated target
audience (see [Game Overview](./Game%20Overview.md) → Target Audience & Platform), and
today nothing in these docs explains it anywhere. Whether there is also a fuller
Rules/How-to-Play screen is left open — see Open Questions below, which already carries
that as a future menu item.

**The strip has to state the sending rule itself — that the square you play inside a small
board is what decides which board your opponent plays in next.** None of the drawn copy
closes that: the hint says a tap shows you "where it sends them" without saying that
*where* is decided by *which square*, and the forced-state line states the causality after
the fact — *"that's what sent you"* — without the mapping, and only to a player who can
already read the rings. The sentence itself isn't written and no approved screen draws
it — see Open Questions below.

**The turn banner is built, it is always visible, and it carries two things.** Normally
it says whose turn it is — the approved handoff draws this as *"Player One, you're up!"*.
When a move is pending it switches to the pending-move prompt: the two lines *"Play
here?"* and *"Tap again to lock it in."* that appear when a player taps a square to
preview a move before confirming it. That is what the approved handoff draws on screen
`2d`.

Because the banner is always visible, it takes vertical space on every board screen, not
only while a move is pending.

The free-choice cue is a separate matter and lives in the how-to-play strip below the
board — see [Game Board Design](./Game%20Board%20Design.md) → The free-choice state. On a
free-choice turn it shows alongside the legend and the hint, not instead of them. It drops
out while a move is pending and comes back when the player commits or picks somewhere
else. A forced quadrant needs no cue of its own, since *"The only board you can play in
right now."* already says it.

## Screens (so far)
1. **Main Menu** — Play Game + Theme + Settings + About Us buttons.
2. **Open Games List** — lists all open games, with New Game at the top of the list;
   reached from Play Game when open games exist.
3. **New Game Name Prompt** — asks for the opponent's name when New Game is picked, with
   **ItSaMeMaRiO** as the default. Undecided whether it's its own screen or an overlay.
4. **Game Screen** — the board (see [Game Board Design](./Game%20Board%20Design.md)).
5. **Theme Selection** — an **overlay on the main menu**, not its own screen. Opened by
   the Theme button. Two themes at launch, **Neon** and **Classic Red vs Blue**
   (see [Theming](./Theming.md)). See [Theme Selection](#theme-selection) below.
6. **Settings** — reachable from *both* the main menu and the gameplay screen (top-right
   button → quick actions).
7. **About Us** — reached from the main menu (About Us button). See Main Menu → About Us.

Each of these now has an approved drawing in
[Design Handoff](./design_handoff_game_ui/README.md):

| Screen above | Handoff screen |
|---|---|
| Main Menu | `1a — Main Menu` |
| Open Games List | `1b — Select Game` |
| New Game Name Prompt | `2c — New Game, opponent name prompt` |
| Game Screen | `1d` (free choice), `1e` (forced quadrant), `2d` (pending move) |
| Theme Selection | `2a — Theme Select (overlay, with paywall)` |
| Settings (main menu) | `2b — Settings page (from the main menu)` |
| Settings (in game) | `1f — Modal: in-game settings / quick actions` |
| Game over | `1g — Modal: winner`, `1h — Modal: draw` |
| About Us | `1c — About Us` |

Content and PRD ownership for About Us are still unsettled — see Main Menu → About Us.

## Navigation and the Back Stack
**The app has a defined navigation model — this is in scope to build out.** The routing
layer and the routing package are settled in [Tech Design](./Tech%20Design.md) →
Navigation. The user was asked which currently-unowned work should be built and answered
"all of it" — *"I want to be deliberate with all things here."*

**Leaving a game takes the player to the main menu, and the same holds for the other
screens — there is no known exception yet.** In the user's own words: *"the exit game
should take you to the main menu. Same with most of the screens. I don't think we have an
exception to that just yet."* The rule is the default everywhere until a screen turns up
that needs something else.

What is not decided is the stack mechanics, not the destination — whether exiting a game
pops to an existing main menu instance or pushes a fresh one, and where the iOS back-swipe
gesture leads. See Open Questions below.

**The main menu is the app's launch screen.** It is assumed throughout this doc (e.g. Main
Menu is screen 1 in **Screens (so far)**) and stated nowhere else.

## Theme Selection
Opened by the **Theme** button on the main menu, and by nothing else. This is an
**overlay** on the main menu, not its own screen — see [Theming](./Theming.md). The main
menu stays mounted and painted underneath it, dimmed — see **Main Menu** above.

**The sheet's header is "Pick your look"**, with **"Both free. Switch any time."** on a
second line under it.

**Two options at launch:**
- **Neon** — black background, electric neon colors. The base theme.
- **Classic Red vs Blue** — the plain, familiar look. Red player vs blue player.

See [Theming](./Theming.md) → Theme Catalog for the full look of each.

**The list is one row per theme file in the themes folder**, so adding a theme is dropping
one file in and nothing on this screen changes — see [Theming](./Theming.md) → Where
Themes Live. **The list always renders.** One theme file the app can't read never blanks
the overlay or stops the other rows from appearing.

**Each row shows a preview tile, the theme's name and a one-line description, all read
from that theme's own file.** The preview tile is a miniature quadrant rendered in that
theme's own colors and marks — that theme's grid lines, and one mark from each player — so
two themes side by side are told apart by the tile alone. An empty grid, or a grid drawn
in the *active* theme's colors, isn't this.

**The currently active theme is highlighted** in the list, so it's obvious which one is in
use before you change anything. The active row carries both treatments — a ring around
the row **and** an **ACTIVE** badge — and it keeps its ownership badge as well, so an
active free theme reads **ACTIVE** and **FREE** together. A ring on its own, or a badge on
its own, isn't the highlight.

**Every row also carries exactly one ownership badge** — **FREE**, **OWNED**, or, on a
locked row, a price action in place of the badge with the preview tile dimmed. **ACTIVE**
is not an ownership badge and never replaces one. What the three states mean, and why a
locked row still shows its preview, is [Tech Design](./Tech%20Design.md) → In-App
Purchases and Entitlements. The row draws all three without reshaping, so a paid theme
drops into the list later without redrawing the screen.

**Nothing on this overlay is buyable, and no purchase or restore control lives here.**
Both themes that ship are free, so no row is locked at launch. The purchases section and
the global **Restore purchases** control are on the Settings screen — see **Settings
Menu** → **Purchases**. The approved handoff draws a *Restore purchases* link in this
overlay's footer; that link isn't built here, because one global control on Settings keeps
the purchase flow off the other menu screens.

**Neon is the default** — what's active before a player has ever opened theme selection,
and it's the base theme every other theme falls back to. See [Theming](./Theming.md).

**Selecting a theme applies it immediately** — the menu behind the overlay is already in
the new theme, no restart — and the overlay closes. The choice persists between sessions;
see [Theming](./Theming.md) → Choosing a Theme. **The overlay can also be closed without
changing anything**, with the close control in its header.

**If the theme fails to load, the overlay does not close.** The "sorry this theme is
unavailable" modal sits on top of the overlay, which stays underneath it, and the app
falls back to Neon — so Neon is the highlighted row behind the modal. The modal and the
fallback are [Theming](./Theming.md) → Choosing a Theme.

```
┌─────────────────────────┐
│      THEME SELECT       │
│                         │
│   ┌─────────────────┐   │
│   │▓▓▓▓▓ NEON ▓▓▓▓▓▓│   │
│   └─────────────────┘   │
│                         │
│   ┌─────────────────┐   │
│   │  CLASSIC RED VS │   │
│   │      BLUE       │   │
│   └─────────────────┘   │
│                         │
└─────────────────────────┘
```
Neon is shown highlighted because it's the currently active theme.

## Settings Menu
**Reachable from two places:**
1. The **main menu** (Settings button).
2. The **gameplay screen** — you can get to settings without abandoning a game.

That second one is the important requirement: settings must be available mid-game.

**Contents so far — four toggles:**

| Setting | Sub-label | What it does |
|---|---|---|
| **Music** | Tunes while you play | Global mute toggle for background music. Separate from the theme — mute any theme's music. See [Theming](./Theming.md). |
| **Sound effects** | Buzzes, pops and splats | Global mute toggle. Separate from the theme — mute any theme. See [Theming](./Theming.md) → Sound Decisions → Global mute. |
| **Vibrate on touch** | A little buzz on every tap | Haptic feedback on tap. Fires on every *valid* click. On/off. |
| **Animations** | Marks that pop and glow | Turn animations on/off. See [Animations](./Animations.md). |

These sub-labels are settled strings — quote them exactly, don't paraphrase. Where they
differ from the wording in the approved handoff, these win.

All four are **global**, **player-controlled**, and **not theme-defined** — a theme can't
override them. All four are **remembered between sessions**.

That's the pattern: the theme decides what things look like, sound like, and how they
move; these four toggles let the player switch each of those channels off entirely.

```
┌─────────────────────────┐
│        SETTINGS         │
│                         │
│  Music            [ON ] │
│                         │
│  Sound Effects    [ON ] │
│                         │
│  Vibrate on Touch [ON ] │
│                         │
│  Animations       [ON ] │
│                         │
│          [ Back ]       │
└─────────────────────────┘
```

### Defaults on a fresh install
**All four toggles default to on** — music, sound effects, vibrate on touch, and
animations — on a fresh install before the player has opened Settings. This matches the
settings mock, which draws all four on: the game presents itself fully — music, sound,
haptics and motion — with the player turning off whatever they do not want.

### Vibrate on Touch
A **small, subtle buzz** when the player taps — enough to confirm "you selected that,"
nothing more. It's tactile confirmation of a click or selection.

- Fires on making a selection / clicking.
- Deliberately subtle. Not a rumble.
- Can be turned **on and off in settings**, sitting right alongside the sound effects
  toggle.

**The switch governs every buzz in the app, not only board taps.** With it off, no valid
action anywhere buzzes — menu buttons, theme rows, and the settings toggles themselves.
The rule it switches on and off is [Game Board Design](./Game%20Board%20Design.md) →
Haptic Rule.

**Flipping it mid-game governs the very next tap.** The vibrate toggle is offered inside
in-game quick actions, so what the setting reads at the moment of a tap is what decides
whether that tap buzzes — not what it read when the app or the game started.

Why it earns its place: the board has 81 small tap targets on a phone. A tap that lands
slightly off, or on a locked quadrant, is easy to misread as "did that register?" A buzz
answers that question without the player having to look for a change.

### Purchases
**The Settings screen carries a purchases section**, holding the $4.99 open-game-slot
unlock and a global **Restore purchases** control. This is the conventional iOS placement,
it keeps one parental gate in one place, and it keeps the purchase flow off the other menu
screens.

So the Settings screen carries more than the four toggles above — it also holds this
purchases section.

### How you reach settings from gameplay
**A settings button at the top right of the game screen.** Tapping it opens **quick
actions** — a short list of things you can do mid-game, including **exit the game** back
to the main menu.

So the settings button does double duty in-game: it's both the settings entry point and
the way out of a game. You don't have to finish a game to leave it.

```
┌─────────────────────────────────┐
│  PLAYER 1   TIES   PLAYER 2  ⚙  │  ← settings, top right
│     2        1        0         │
├─────────────────────────────────┤
│                                 │
│        [ THE BIG BOARD ]        │
│                                 │
└─────────────────────────────────┘
```

**Quick actions contents (so far):**
- Exit the game / back to main menu
- The sound effects and vibrate toggles

**Exit is an ordinary button, not a destructive one** — no red, no warning treatment.
Leaving destroys nothing: the game and its score are saved and the player picks it up
again from the open-games list. Destructive treatment has to keep meaning "this destroys
something," which only the delete control in the open-games list does — see **Play Game →
Where It Takes You** → **Deleting an open game**.

The toggles here are the same values as on the settings screen — one of each, app wide,
not an in-game copy. Flip one here and it is flipped there.

**Tapping the settings button clears a pending, unconfirmed move** — it is one instance of
the rule that any tap outside the nine quadrants deselects. See
[Game Board Design](./Game%20Board%20Design.md) → Changing your mind.

Undecided: whether quick actions is the *same* settings screen as the main menu's, or a
trimmed-down in-game version with the exit option added. What that decides is which of the
four toggles the in-game surface carries — on the *same screen* reading, the Animations
row, the Music row and the purchases section all arrive in game together.

## Dynamic Type
**The app does not scale its text to the iOS Dynamic Type setting in this version.** Not
for now — *"Lets not do this as of yet."*

So the Settings screen carries no text-size control of its own.

## Game Over → Rematch
When a game is won or tied, the scoreboard increments **at game end** — the winner's
column, or Ties, as soon as the game is won or tied, not when a rematch is taken. A
**rematch button is available as an option**. Taking it only resets the board for the next
game. See [Game Overview](./Game%20Overview.md) → Session Structure.

**The rematch and the next-game button are the same thing under two names** — one
behaviour, reached by one button. There is no third way on from a finished game.

**A finished game is counted once, ever.** The increment belongs to the move that ended
the game and to nothing else: reopening that game later counts nothing further, and going
back to the main menu without taking the rematch doesn't un-count it.

The rematch continues in the **same open game** — same series, scoreboard intact. It does
not start a second open game. See **Play Game → Where It Takes You** → **What an open game
holds**.

The winner of that game goes first in the rematch — or on a tie, whoever went first last
time (see [Rules](./Rules.md) → Turn Order Across Games).

**Nothing resets the board on its own.** A game the players finished and never rematched
stays finished — reopen it from the open-games list and you get that finished board with
the result card over it, both buttons live, exactly as it was left.

### The result card
**A result card drawn over the board, with the board dimmed behind it** — not a separate
screen and not a banner. The finished position stays visible behind the card.

This matches what the approved handoff draws. The board keeps being drawn behind the card
rather than replaced by it — dimmed, but still legible enough to read the finished
position. The scrim, the dim behind it, and the card's own fill, border and radius are
theme values like everything else; its spacing and padding are not, since those are fixed
in code app-wide (see [Theming](./Theming.md) → What a Theme Does NOT Control).

**The card says what happened, in words, and a win and a tie read differently.** A win
names the winning player. A tie names nobody — most quadrants claimed does not win it (see
[Rules](./Rules.md) → Edge Cases).

**It shows the running score, already counting the game that just ended**, with the column
that moved identifiable, and **it says who goes first in the next game**.

**The result card carries two buttons — one to start the next game, and one to go back to
the main menu.** *"On game over result card we should have a button for next game as well
as back to main menu."*

The card is self-sufficient, so the player is never dependent on the settings button to
leave a finished game. The result stays up until one of the two is pressed, and leaving
destroys nothing — the game and its score are already saved, and the series is picked back
up from the open-games list exactly as it stands.

**Next game is the affirmative action and takes the heavier button treatment; back to the
main menu is the lighter alternative.** Continuing the session is what the game is built
around (see [Game Overview](./Game%20Overview.md) → Session Structure), and that weighting
is a permanent-looking difference to a player, so it is stated rather than left to whoever
builds the card.

## Persistence
| Thing | Persists? |
|---|---|
| **Selected theme** | ✅ Saved to device storage, restored on launch |
| **Music toggle** | ✅ Remembered in whatever state it was left |
| **Sound effects toggle** | ✅ Remembered in whatever state it was left |
| **Vibrate on touch toggle** | ✅ Remembered in whatever state it was left |
| **Animations toggle** | ✅ Remembered in whatever state it was left |
| **Scoreboard** | ✅ Per game — each open game carries its own scoreboard, saved with that game |
| **Game in progress** | ✅ Saved to device storage — resumable from the open-games list |

So there are five persisted preferences — theme, music, sound, vibration, and animations —
plus game state: every open game is saved, each with its own scoreboard. How that gets
stored is settled in [Tech Design](./Tech%20Design.md) → Persistence and Serialization
— preferences in `shared_preferences`, game state in Hive.

### When a game is written to storage
**After every confirmed move.** Nothing is ever lost to a crash or a force-quit.

Each write is a single small record, the game is turn-based so writes are infrequent, and
a game is saved specifically so it can be resumed — losing moves to a force-quit would
undercut that.

### Leaving a game mid-play
Since a game in progress is saved, going back to the main menu doesn't discard anything —
the game stays in the open-games list with its own scoreboard, and you can pick it up
again. Whether leaving still needs a confirmation prompt is undecided; the original
reason for one ("Leave game? Your score will be lost") no longer applies.

## Open Questions
- Future menu items to consider later: Rules/How to Play, Settings, vs. AI, Online.
- **Does exiting a game pop back to an existing main menu instance, or push a fresh
  one?**
- **Where does the iOS back-swipe gesture lead**, and can it carry a player back into a
  game they just exited?
- **Is there also a fuller Rules/How-to-Play screen**, separate from the on-board legend
  and hint, or does the legend/hint fully cover "how to play" for this version? (Already
  listed above as a future menu item to consider.)
- **Which strip content belongs to which board state, and is the set of states exactly the
  three the handoff draws (`1d`, `1e`, `2d`)?** The board has more states than that — game
  over, and free choice after being sent to a dead quadrant — and it's not decided what,
  if anything, this strip shows for those.
- **What does the strip say to explain the sending rule?** Nothing written or drawn says,
  in words, that the square you play inside a small board is what decides which board your
  opponent plays in next. Whatever it says has to work in the words a player reads —
  "square" for a cell and "board" for one of the nine — where "board" is also the name for
  the whole grid.
- **What exactly does the free-choice cue say?** The handoff's *"Free choice — pick any
  board"* is the surviving candidate, and whether it ships as drawn is the call. It has to
  read unmistakably as one of the nine and not as the whole grid.
- **Does the strip still say anything of its own while a move is pending?** The turn
  banner carries the pending-move prompt, and the handoff draws the strip talking as
  well — or the strip could go quiet and leave the banner to do it.
- **Do the hint and the legend ever fade once a player knows the game?** They're training
  wheels on the screen with the tightest vertical budget in the app, and a player on their
  fortieth game pays for them every turn. If they can fade, nothing says what triggers
  it — a move count, a games-played count, a setting, a dismiss control — and a dismiss
  control needs a way to bring them back.
- **After the "this theme is unavailable" modal is dismissed, does the overlay stay open
  on the Neon list, or close along with the modal?**
- **Where does the "theme is unavailable" message go when the load fails at launch**,
  before the overlay is even open — fall back to Neon quietly and show it the next time
  theme selection is opened, or say something at launch?
- **Is the Neon fallback remembered?** When a theme fails to load and the app drops back
  to Neon, does Neon become the saved choice, or is the player's original pick kept and
  tried again next launch?
- **What does a player see when a theme file is broken?** The list still renders either
  way, but nothing says whether that theme is quietly missing from it or shown as
  unavailable.
- **What should the Vibrate on Touch toggle do on a device that produces no haptic?** An
  iPad has no Taptic Engine, and an iPhone with the OS's own System Haptics switched off
  feels nothing either — in both cases the app's switch still reads ON and the player has
  no way to tell that a different switch is responsible.
- **Does the Settings screen show which theme is active?** The approved handoff draws a
  read-only theme card there, and nothing here specifies one.
- **What are the two buttons on the result card called?** The docs call the mechanic a
  rematch and the control the next-game button; the approved handoff draws **REMATCH** and
  a ghost **Exit to Main Menu**. Nothing settles the actual strings.
- **What does the result card call a drawn big board?** The drawn draw modal words it as a
  "cat game," which [Game Overview](./Game%20Overview.md) → Terminology defines as a small
  board filled with no winner and [Rules](./Rules.md) → Edge Cases calls a straight draw.
- **Can the result card be put aside to look at the finished board?** The board is visible
  behind it either way, but neither drawn result modal carries a close control the way the
  in-game settings sheet does.
- **Does the `+1` under the column that just moved show again when a finished game is
  reopened later**, or only on the result that has just happened?
