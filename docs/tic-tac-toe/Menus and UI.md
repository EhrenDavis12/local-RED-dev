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
| **Scoreboard** | ❌ Resets when you leave to the main menu |
| **Game in progress** | ❌ Not saved |

So there are four persisted values, all of them player preferences: theme, sound,
vibration, and animations. Nothing about game state is saved.

> The scoreboard non-persistence is flagged as a possible future change — build it so
> persistence can be added later without a rewrite.

### Leaving a game mid-play
Since the scoreboard resets at the main menu, going back to the menu discards the running
series. Whether that needs a confirmation prompt ("Leave game? Your score will be lost")
is undecided.

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

### Does the main menu need a title/logo?
**Yes — both a title and a logo.**

### Is theme selection its own screen or an overlay?
**An overlay** on the main menu.

## Open Questions
- Future menu items to consider later: Rules/How to Play, Settings, vs. AI, Online.
