# Menus and UI

> **Status:** Brain dump. Contradictions are expected and OK. Nothing here is settled.

## Main Menu
The game needs a main menu.

**Buttons:**
- **New Game** — starts a two-player same-phone game. Large.
- **Theme** — opens theme selection. Large, same weight as New Game.
  See [Theming](./Theming.md).
- **Settings** — opens the settings menu.

Themes are deliberately **up front**, not buried in settings. The theme button gets the
same visual weight as New Game.

**The main menu has a title and a logo.** Both, not just buttons.

> 📝 *The main menu grew over the course of this brain dump: first "only a New Game
> button," then + Theme, then + Settings. Recording the drift — three buttons is where it
> currently stands.*

```
┌─────────────────────────┐
│                         │
│         [ LOGO ]        │
│   TIC TAC TOE EXTREME   │
│                         │
│                         │
│   ┌─────────────────┐   │
│   │                 │   │
│   │    NEW GAME     │   │
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
└─────────────────────────┘
```

The entire main menu is itself theme-driven — background, button styling, title. No
hardcoded styling here either.

## New Game → What It Starts
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
1. **Main Menu** — New Game + Theme + Settings buttons.
2. **Game Screen** — the board (see [Game Board Design](./Game%20Board%20Design.md)).
3. **Theme Selection** — an **overlay on the main menu**, not its own screen. Opened by
   the Theme button. Two themes at launch, **Neon** and **Classic Red vs Blue**
   (see [Theming](./Theming.md)).
4. **Settings** — reachable from *both* the main menu and the gameplay screen (top-right
   button → quick actions).

## Settings Menu
**Reachable from two places:**
1. The **main menu** (Settings button).
2. The **gameplay screen** — you can get to settings without abandoning a game.

That second one is the important requirement: settings must be available mid-game.

**Contents so far — three toggles:**

| Setting | What it does |
|---|---|
| **Sound effects** | Global mute toggle. Separate from the theme — mute any theme. See [Theming](./Theming.md). |
| **Vibrate on touch** | Haptic feedback on tap. Fires on every *valid* click. On/off. |
| **Animations** | Turn animations on/off. See [Animations](./Animations.md). |

All three are **global**, **player-controlled**, and **not theme-defined** — a theme can't
override them. All three are **remembered between sessions**.

That's the pattern: the theme decides what things look like, sound like, and how they
move; these three toggles let the player switch each of those channels off entirely.

```
┌─────────────────────────┐
│        SETTINGS         │
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
When a game is won or tied, a **rematch button is available as an option**. Taking it
resets the board and increments the scoreboard (winner's column, or Ties). See
[Game Overview](./Game%20Overview.md) → Session Structure.

The rematch continues in the **same save slot** — same series, scoreboard intact. It does
not start a second saved game. See Decisions → What does a save slot hold? below.

The winner of that game goes first in the rematch — or on a tie, whoever went first last
time (see [Rules](./Rules.md) → Turn Order Across Games).

Undecided: whether this is a full result screen, a banner, or an overlay on the finished
board. ("Rematch is an option" implies at least one other choice sits next to it —
presumably exiting to the main menu, which is also reachable via the top-right settings
button.)

## Persistence
| Thing | Persists? |
|---|---|
| **Selected theme** | ✅ Saved to device storage, restored on launch |
| **Sound effects toggle** | ✅ Remembered in whatever state it was left |
| **Vibrate on touch toggle** | ✅ Remembered in whatever state it was left |
| **Animations toggle** | ✅ Remembered in whatever state it was left |
| **Scoreboard** | ✅ Saved with the game — resumes when the game resumes |
| **Game in progress** | ✅ Saved — leave and come back to it later |

So four player preferences persist — theme, sound, vibration, and animations — and so
does game state: a game in progress and its scoreboard. The two are stored differently;
see [Tech Design](./Tech%20Design.md) → Decisions → Persistence package and Game state
storage — Hive.

<!-- Superseded: this previously read "The scoreboard non-persistence is flagged as a
     possible future change — build it so persistence can be added later without a
     rewrite." That future change has happened — the scoreboard now persists with the
     saved game. See Game Overview → Decisions → Scoreboard lifetime. -->

### Leaving a game mid-play
Going back to the main menu no longer discards anything — the game and its scoreboard are
saved, and the game can be picked up again from the game selection screen.

Undecided: whether leaving still warrants a confirmation prompt at all, and if so what it
says now that nothing is lost.

<!-- Superseded: this previously read "Since the scoreboard resets at the main menu,
     going back to the menu discards the running series. Whether that needs a
     confirmation prompt ('Leave game? Your score will be lost') is undecided." The
     premise no longer holds — game state and the scoreboard both persist. See
     Decisions → Does a game in progress persist? -->

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
**A rematch button is available as an option.** It resets the board and increments the
scoreboard.

The rematch continues in the same save slot, with the scoreboard intact — see **What does
a save slot hold?** below.

### Does the main menu need a title/logo?
**Yes — both a title and a logo.**
<!-- Resolved: the logo will be generated with Replicate when needed, not now.
     See Tech Design → Decisions → Where do sound and art assets come from. -->

### Is theme selection its own screen or an overlay?
**An overlay** on the main menu.

### Does a game in progress persist?
**Yes — game data is persistent, so you can reload and come back to the game at any
time.** As stated:

> *"We need to have the game data persistent. So we can reload and come back to the game
> at any time. I do believe this should have been called out already. Main Menu screen ->
> Play Game button -> Game selection screen. In the Game selection screen the user should
> be able to reselect the last game played. Refer to the documents for more details about
> this part. If you don't see this then we might have uncommitted changes from our other
> developer."*

So the flow is **Main Menu → Play Game → Game selection screen**, and the game selection
screen is where you reselect the last game played.

**The game selection screen is not designed yet, and neither is the main-menu rewording.**
The design docs describing it are believed to exist but are not in this repo. Until they
land, the **Main Menu**, **Screens (so far)** and the ASCII mockup above still describe the
old three-button menu with a New Game button — that contradiction is known, not an
oversight.

The scoreboard persists with the game — see [Game Overview](./Game%20Overview.md) →
Decisions → Scoreboard lifetime. Where it is stored is
[Tech Design](./Tech%20Design.md) → Decisions → Game state storage — Hive.

### What does a save slot hold?
**A save slot holds a whole series — the board plus the running score.** A rematch
continues in the same slot with the scoreboard intact, and "the last game played" on the
game selection screen means the last *series*, not the last individual board.

This confirms what the **Persistence** table above and
[Game Overview](./Game%20Overview.md) → Decisions → Scoreboard lifetime already assume,
rather than changing them. What it adds is the *unit*: finishing a game and taking the
rematch continues one slot, it does not consume a second one.

It also fixes what the count in **Open Questions** below is counting — however many saved
games we keep, they are series.

### Do we support Dynamic Type?
**Not for now.** *"Lets not do this as of yet."*

The app does not scale its text to the iOS Dynamic Type setting in this version. Recorded
as a deliberate deferral rather than an oversight, so it can be revisited later.

## Open Questions
- Future menu items to consider later: Rules/How to Play, Settings, vs. AI, Online.
- How many saved games do we keep? **3 is the likely number** — the not-yet-submitted
  design docs are believed to say 3. Confirm once those land. Not settled.
  - What a saved game *is* is settled — a whole series, board plus running score (see
    Decisions → What does a save slot hold?). Only the count is open.
