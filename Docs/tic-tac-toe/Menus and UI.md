# Menus and UI

> **Status:** Brain dump. Contradictions are expected and OK. Nothing here is settled except
> what's under **Decisions**.
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
- **Settings** — opens the settings menu.
- **About Us** — last in the list. See Decisions → Does the About Us screen ship?

Themes are deliberately **up front**, not buried in settings. The theme button gets the
same visual weight as Play Game.

**The main menu has a title and a logo.** Both, not just buttons.

> 📝 *The main menu grew over the course of this brain dump: first "only a New Game
> button," then + Theme, then + Settings, then + About Us. Recording the drift — four
> buttons is where it currently stands.*

```
┌─────────────────────────┐
│                         │
│         [ LOGO ]        │
│   TIC TAC TOE EXTREME   │
│                         │
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
│   ┌─────────────────┐   │
│   │    SETTINGS     │   │
│   └─────────────────┘   │
│                         │
│   ┌─────────────────┐   │
│   │    ABOUT US     │   │
│   └─────────────────┘   │
│                         │
└─────────────────────────┘
```

The entire main menu is itself theme-driven — background, button styling, title. No
hardcoded styling here either.

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
7. **About Us** — reached from the main menu (About Us button). See Decisions → Does the
   About Us screen ship?

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

Content and PRD ownership for About Us are still unsettled — see Decisions → Does the
About Us screen ship?

## Theme Selection
Opened by the **Theme** button on the main menu. As already decided (see Decisions below and
[Theming](./Theming.md)), this is an **overlay on the main menu**, not its own screen.

**Two options at launch:**
- **Neon** — black background, electric neon colors. The base theme.
- **Classic Red vs Blue** — the plain, familiar look. Red player vs blue player.

See [Theming](./Theming.md) → Theme Catalog for the full look of each.

**The currently active theme is highlighted** in the list, so it's obvious which one is in
use before you change anything.

**Neon is the default** — what's active before a player has ever opened theme selection.

Selecting a theme applies it, and it persists between sessions — see
[Theming](./Theming.md) → Decisions.

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
| **Sound effects** | Buzzes, pops and splats | Global mute toggle. Separate from the theme — mute any theme. See [Theming](./Theming.md). |
| **Vibrate on touch** | A little buzz on every tap | Haptic feedback on tap. Fires on every *valid* click. On/off. |
| **Animations** | Marks that pop and glow | Turn animations on/off. See [Animations](./Animations.md). |

See Decisions → What are the settings toggle sub-labels? for these as settled copy.

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

### Vibrate on Touch
A **small, subtle buzz** when the player taps — enough to confirm "you selected that,"
nothing more. It's tactile confirmation of a click or selection.

- Fires on making a selection / clicking.
- Deliberately subtle. Not a rumble.
- Can be turned **on and off in settings**, sitting right alongside the sound effects
  toggle.

Why it earns its place: the board has 81 small tap targets on a phone. A tap that lands
slightly off, or on a locked quadrant, is easy to misread as "did that register?" A buzz
answers that question without the player having to look for a change.

### How you reach settings from gameplay
**A settings button at the top right of the game screen.** Tapping it opens **quick
actions** — a short list of things you can do mid-game, including **exit the game** back
to the main menu.

So the settings button does double duty in-game: it's both the settings entry point and
the way out of a game.

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

Undecided: whether quick actions is the *same* settings screen as the main menu's, or a
trimmed-down in-game version with the exit option added.

## Game Over → Rematch
When a game is won or tied, the scoreboard increments **at game end** — the winner's
column, or Ties. See Decisions → When does the scoreboard increment. A **rematch button
is available as an option**. Taking it resets the board for the next game. See
[Game Overview](./Game%20Overview.md) → Session Structure.

The rematch continues in the **same open game** — same series, scoreboard intact. It does
not start a second open game. See Decisions → What does an open game hold? below.

The winner of that game goes first in the rematch — or on a tie, whoever went first last
time (see [Rules](./Rules.md) → Turn Order Across Games).

This is a result card overlay — see Decisions → What does the player see when a game ends?
below, and Decisions → What controls does the game-over result card carry? for what sits
on it.

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
stored is settled in [Tech Design](./Tech%20Design.md) → Decisions — preferences in
`shared_preferences`, game state in Hive.

### Leaving a game mid-play
Since a game in progress is saved, going back to the main menu doesn't discard anything —
the game stays in the open-games list with its own scoreboard, and you can pick it up
again. Whether leaving still needs a confirmation prompt is undecided; the original
reason for one ("Leave game? Your score will be lost") no longer applies.

## Decisions

### Should there be a mute button, and where does it live?
**Yes — a global "Sound effects" toggle in the Settings menu.** It's a player setting, not
a theme property, so it mutes any theme, and it's remembered between sessions alongside
the vibrate toggle and the selected theme. See [Theming](./Theming.md) → Sound Decisions →
Global mute.

### How do you get back to the main menu from a game?
**Via the settings button at the top right of the game screen.** It opens quick actions,
which include exiting the game. You don't have to finish a game to leave it.

### What happens when a game ends?
**A rematch button is available as an option.** It resets the board for the next game.
The scoreboard increments at game end, not when the rematch is taken — see **When does the
scoreboard increment** below.

The rematch continues in the same open game, with the scoreboard intact — see **What does
an open game hold?** below.

### What does the player see when a game ends?
**A result card drawn over the board, with the board dimmed behind it** — not a separate
screen and not a banner. The finished position stays visible behind the card.

This matches what the approved handoff draws. The scrim, the board-behind opacity, and the
card's own fill/border/radius are all real values that need a home, because the overlay
reading is the one that requires them.

### What controls does the game-over result card carry?
**The result card carries two buttons — one to start the next game, and one to go back to
the main menu.** *"On game over result card we should have a button for next game as well
as back to main menu."*

This resolves a question that three PRDs were holding open from different angles — whether
the settings button stays live over the result card, and whether the card needs its own
exit. It does: the card is self-sufficient, so the player is never dependent on the
settings button to leave a finished game.

### When does the scoreboard increment
**At game end.** The winner's column, or Ties, increments as soon as the game is won or
tied — not when a rematch is taken. Taking the rematch only resets the board.

### Does the main menu need a title/logo?
**Yes — both a title and a logo.**

### Is theme selection its own screen or an overlay?
**An overlay** on the main menu.

### Is the main menu button "New Game" or "Play Game"?
**Play Game.** It branches on whether there are existing open games — no open games goes
straight into a new game, open games goes to the open-games list screen. New Game moves to
the top of that open-games list.

### Does a game in progress have to be saved to device storage?
**Yes — a game in progress is saved to device storage.** How it is stored is answered in
[Tech Design](./Tech%20Design.md) → Decisions → Game state storage — Hive.

### What does each row in the open-games list show?
**The list shows New Game plus any open games, and each open game is titled with the
opponent's name.** When the user selects New Game, they get a prompt to input the name
of their opponent, with the default name **ItSaMeMaRiO**.

### Does the opponent name replace "Player Two" in game?
**No — not at this moment.** The opponent name titles the game in the open-games list and
nothing else. In game, the players are still **Player One** and **Player Two**.

That might change in the future, so don't build it in a way that makes the swap hard to
make later. See [Game Overview](./Game%20Overview.md) → Decisions → Player names.

### Which theme is active by default?
**Neon.** It's what a player sees before they've ever opened theme selection, and it's the
base theme every other theme falls back to. See [Theming](./Theming.md).

### How does theme selection show which theme is in use?
**The currently active theme is highlighted** in the list. Two options at launch, Neon and
Classic Red vs Blue, and the highlight is what tells you which one you're on.

### What does an open game hold?
**An open game holds a whole series — the board plus the running score.** A rematch
continues in the same open game with the scoreboard intact, and resuming a game from the
open-games list resumes the *series*, not just the last individual board.

It also fixes what the count below is counting — the three open games we keep are three
series.

### How many open games do we keep?
**3 by default, no more.** A **$4.99 in-app purchase raises the cap to 100 open game
slots.**

What each of those 3 (or 100) holds is a whole series — see **What does an open game
hold?** above.

### Deleting an open game
**The open-games list gains a delete action, so a slot can be freed.** This closes a hole
— with a cap of 3 and a rematch staying in the same open game, nothing previously ever
freed a slot.

### How does a player delete an open game?
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
had been drawn for it. The approved handoff draws no delete affordance at all on screen
`1b` — this Decision is the source of the affordance, not the drawing.

### Do we support Dynamic Type?
**Not for now.** *"Lets not do this as of yet."*

The app does not scale its text to the iOS Dynamic Type setting in this version.

### Navigation and the back stack
**The app has a defined navigation model — this is now in scope to build out.** No screen
flow in this doc currently says what "back" does anywhere: whether exiting a game pops to
an existing main menu or pushes a fresh one, or whether the iOS back-swipe gesture can
carry a player back into a game they just exited. The user was asked which currently-
unowned work should be built and answered "all of it" — *"I want to be deliberate with all
things here."* The details of the routing approach and of where each back affordance leads
are not decided — see Open Questions below.

The main menu being the app's launch screen is assumed throughout this doc (e.g. Main
Menu is screen 1 in **Screens (so far)**) and stated nowhere explicitly. Recording it here
since nothing contradicts it.

### How to play — the on-board legend and hint
**The game explains its own central mechanic — this is now in scope to build out.** The
approved handoff makes this strip **state-dependent** — what it says changes with what the
board is doing:
- `1d` (opening move / free choice) — the legend (Open · Locked · Cat game) **and** the
  hint *"Tap a square to see where it sends them. / Tap it again to play it."*
- `1e` (forced quadrant + last move) — neither of those. Its bottom strip instead carries
  two lines explaining the two rings: *"They played here last — that's what sent you."* /
  *"The only board you can play in right now."*
- `2d` (pending move) — a third, different pair of lines, on the turn banner rather than a
  bottom strip: *"Play here?"* / *"Tap again to lock it in."*

The sending rule is the hardest thing in the game to explain, kids are a stated target
audience (see [Game Overview](./Game%20Overview.md) → Target Audience & Platform), and
today nothing in these docs explains it anywhere. Whether there is also a fuller
Rules/How-to-Play screen is left open — see Open Questions below, which already carries
that as a future menu item.

### When is a game written to storage?
**After every confirmed move.** Nothing is ever lost to a crash or a force-quit.

Weighed reasoning: each write is a single small record, the game is turn-based so writes
are infrequent, and a game is saved specifically so it can be resumed — losing moves to a
force-quit would undercut that.

### Where the open-game slot unlock is sold
**The Settings screen.** The Settings screen gains a purchases section holding the $4.99
open-game-slot unlock and a global **Restore purchases** control. This is the conventional
iOS placement, it keeps one parental gate in one place, and it keeps the purchase flow off
the other menu screens.

This means the Settings screen now carries more than the four toggles specified in
**Settings Menu** above — it also holds the purchases section described here.

### Is the turn banner built, and where does the free-choice cue live?
**No — the turn banner is not built. The free-choice cue lives in the how-to-play strip
below the board instead.** See [Game Board Design](./Game%20Board%20Design.md) → Decisions
→ Where does the free-choice cue live.

### Does the About Us screen ship?
**Yes — About Us ships, and its button goes last in the main menu button list.** In the
user's words:

> "We want the about us but it can be the last button in the list for now we might move it
> in the future but lets add it here."

So the main menu carries four buttons, in order: Play Game, Theme, Settings, About Us. The
position is explicitly provisional — the user said "for now we might move it in the
future" — so a later reordering is expected rather than a reversal.

Two things this doesn't settle:
- The screen's **content** is not specified by any doc. The handoff draws team photos;
  where those come from is not decided.
- **No PRD currently owns the About Us screen.** The main-menu PRD covers the button; the
  screen itself has no owner yet.

### What are the settings on a fresh install?
**All four toggles default to on** — music, sound effects, vibrate on touch, and
animations — on a fresh install before the player has opened Settings. This matches the
settings mock, which draws all four on: the game presents itself fully — music, sound,
haptics and motion — with the player turning off whatever they do not want. The mock was a
drawing rather than a decision until now, which is why this needed settling.

### What are the settings toggle sub-labels?
**Each of the four toggles carries a short playful sub-label**, matching the handoff's
voice and the fact that children are a target audience. The four, verbatim:

| Toggle | Sub-label |
|---|---|
| Music | Tunes while you play |
| Sound Effects | Buzzes, pops and splats |
| Vibrate on Touch | A little buzz on every tap |
| Animations | Marks that pop and glow |

These are settled strings — quote them exactly, don't paraphrase.

## Open Questions
- Future menu items to consider later: Rules/How to Play, Settings, vs. AI, Online.
- **What is the routing/navigation approach**, and does exiting a game pop back to an
  existing main menu instance or push a fresh one?
- **Where does each back affordance lead** — the in-game back/exit action, and the iOS
  back-swipe gesture — and can the swipe gesture carry a player back into a game they just
  exited?
- **Is there also a fuller Rules/How-to-Play screen**, separate from the on-board legend
  and hint, or does the legend/hint fully cover "how to play" for this version? (Already
  listed above as a future menu item to consider.)
- **Which strip content belongs to which board state, and is the set of states exactly the
  three the handoff draws (`1d`, `1e`, `2d`)?** The board has more states than that — game
  over, and free choice after being sent to a dead quadrant — and it's not decided what,
  if anything, this strip shows for those.
