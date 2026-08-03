# Handoff: Tic Tac Toe Extreme — UI (4 pages + 2 modals)

## Overview

Approved high-fidelity designs for **Tic Tac Toe Extreme**, the recursive
board-in-a-board pass-and-play game described in the project's design docs
(`Game Overview.md`, `Menus and UI.md`, `Game Board Design.md`, `Theming.md`,
`Rules.md`, `Animations.md`).

Covered here:

| # | Screen | Doc reference |
|---|---|---|
| 1a | Main Menu | Menus and UI → Main Menu |
| 1b | Select Game (open-games list) | Menus and UI → Play Game → Where It Takes You |
| 1c | About Us | *new screen — copy TBD* |
| 1d | Game Board — opening move / free choice | Game Board Design |
| 1e | Game Board — forced quadrant + last-move highlight | Game Board Design |
| 1f | Modal — in-game Settings / quick actions | Menus and UI → Settings Menu |
| 1g | Modal — winner, over the finished board | Menus and UI → Game Over → Rematch |
| 1h | Modal — draw ("Nobody wins this one!") | Rules → Big board full with no three-in-a-row |
| 2a | Theme Select overlay — incl. paywall states | Menus and UI → Theme Selection; Theming → Are themes unlockable |
| 2b | Settings page (from the main menu) | Menus and UI → Settings Menu |
| 2c | New Game — opponent name prompt | Menus and UI → New Game Name Prompt |
| 2d | Game Board — pending-move preview | Game Board Design → Move Input |

Everything is drawn in the **Neon** theme, which per `Theming.md` is the base
theme every other theme merges over.

## About the design files

The files in `design-files/` are **design references written in HTML** — prototypes
showing intended look and behavior. They are **not production code to copy**.

- `Tic Tac Toe Extreme - Screens.dc.html` — all 8 screens laid out side by side in
  iPhone frames.
- `Board.dc.html` — the 9×9 board renderer (all quadrant/cell states).
- `ios-frame.jsx` — the iPhone bezel used for presentation only. **Do not port it.**
- `nocturne-styles.css` — the design-system token sheet the neutrals came from.

The task is to **recreate these designs in the game's own environment** (Flutter, per
`Tech Design.md`'s Hive reference — or whatever the codebase actually uses), following
its established patterns. Nothing here should be hand-copied as HTML.

> **Critical architectural constraint from `Theming.md`:** no hardcoded colors, fonts,
> sizes, sounds or motion anywhere in game code. Every value in this document must be
> read from the active theme. `neon.theme.json` in this folder is the complete Neon
> definition, shaped for exactly that — load it as the base theme and let other themes
> merge over it.

## Fidelity

**High-fidelity.** Colors, type, spacing, radii and glow values are final and exact.
Recreate pixel-for-pixel using the codebase's own widgets. Two things are explicitly
placeholders and are marked as such on screen:

- the **logo** on 1a (a dashed-bordered 81-dot mark standing in for real art),
- the **About Us copy and team photos** on 1c.

## Design tokens

Machine-readable in **`neon.theme.json`**. Summary:

### Color

| Role | Hex / value | Used for |
|---|---|---|
| ground | `#161826` | page background |
| groundDeep / groundLift | `#111320` / `#20233a` | main-menu radial gradient ends |
| surface | `#232532` | modal cards |
| surfaceRaised | `#1e2131` | list cards (1b), team cards (1c) |
| surfaceSunken | `#1b1e2c` | inactive scoreboard chips |
| hairline | `#2b2f42` | 1px chip / card outlines |
| hairlineStrong | `#3f424d` | toggle track (off) |
| text | `#e9e9ed` | primary text |
| textMuted / textSubtle / textDim / textFaint | `#b2b6ca` / `#9397ab` / `#75798c` / `#595d6c` | descending text hierarchy |
| **boardLine** | `#4fc3ff` | small-board grid lines + quadrant borders |
| **playerOne** | `#ff3d71` (mark `#ff5c85`) | Player One ✕, their chips |
| **playerTwo** | `#2dff9e` (mark `#4dffb0`) | Player Two ○, their chips |
| **highlightForced** | `#b57cff` | active-quadrant ring |
| **highlightPending** | `#e9e9ed` (dashed) | provisional selection + destination |
| **highlightLastMove** | `#d2cefd` | opponent's last-move ring |
| catGame | `#9aa2c2` | dead-quadrant Ø |
| accent | `#9184d9` (light `#b5abfc`, soft `#d2cefd`) | menu chrome, toggles |

Color logic, and why it is built this way:

- **Blue is the board.** Grid lines and quadrant borders only.
- **Red and green are the players.** They also differ by *shape* (✕ vs ○), so the game
  is playable without color discrimination — `Theming.md` asks each theme to solve this.
- **Purple is reserved for the two gameplay-critical highlights** and nothing else, so
  "where they played" / "where you must play" never competes with the board or the marks.

Veils (all over `#0f101a`): locked quadrant `0.50`, claimed quadrant `0.76`,
cat quadrant `0.76`, modal scrim `0.62` (`0.72` for the settings modal).

### Type

**Inter** throughout — 400 body, 500 medium, 600 for numbers/titles/marks.

| Style | Size / weight | Notes |
|---|---|---|
| Display (menu title) | 44 / 600 | tracking −0.02em |
| Page title (1c) | 34 / 600 | line-height 1.08 |
| Modal title | 28 / 600 | |
| Screen heading (1b) | 22 / 600 | |
| Body | 14 / 400 | line-height 1.65, `text-wrap: pretty` |
| Caption | 11–12 / 400 | |
| Chip label | 9 / 400 | uppercase, tracking 0.1em |
| Chip value | 22 / 600 (27 in result modals) | |
| Cell mark | 19 / 600 | |
| Claimed-quadrant ✕ / ○ | 56 / 52 | |
| Cat Ø | 44 / 500 + 8px "CAT" caption, tracking 0.16em | |

### Radius

cell 3 · quadrant 9 · chip 10 · control 12 · button 13 · large button 14 · modal 20 · pill 999

### Spacing

Screen frame is **402 × 874** (iPhone logical points).
Safe-area top padding 62 on board screens, 96 on the menu, 64 on 1b/1c.
Horizontal padding 16 on board screens, 20 on 1b, 24 on 1c, 28 on 1a. Bottom 44–52.

---

## The board (the important part)

Rendered by `Board.dc.html`. One component, driven entirely by per-quadrant state.

### Geometry

```
big board      3 × 3 grid, gap 8
  quadrant     padding 5, radius 9, fill rgba(18,20,32,0.60)
    cells      3 × 3 grid, gap 3, square, TRANSPARENT (no cell fill)
    gridlines  drawn as an overlay inset 5 (i.e. inside the padding box)
```

At 402pt wide with 16pt side padding the board is 370pt → quadrant ≈ 118pt →
cell ≈ 35pt. Below Apple's 44pt target, which the docs accept: the two-tap
select-then-confirm interaction is what makes small targets safe. **No zoom** —
the full 9×9 is always visible.

### Grid lines — read this carefully

The small-board crosses are **drawn lines, not gaps**, and they **must not touch the
quadrant border**:

- 2 vertical lines at 33.33% and 66.67% of the quadrant's inner box, each 1.5pt wide,
  running from 9% to 91% of the height.
- 2 horizontal lines, same but transposed.
- Color `#4fc3ff` at 0.75 opacity, glow `0 0 7px rgba(79,195,255,0.90)`.

The quadrant border is the same blue at full presence:
`0 0 0 1.5px rgba(79,195,255,0.5)`, outer glow `0 0 14px rgba(79,195,255,0.16)`,
inner glow `inset 0 0 12px rgba(79,195,255,0.06)`.

So the hierarchy the docs ask for — heavy big board, light small boards — is carried by
*weight and glow*, not by two different colors, and the inset keeps the two grids
visually separate.

### Quadrant states

| State | Treatment |
|---|---|
| **Open** (playable, free-choice mode) | border brightens to `rgba(79,195,255,0.85)` + glow `0 0 20px rgba(79,195,255,0.35)` |
| **Forced** (the one legal quadrant) | 2pt `#b57cff` ring, offset −3, radius 12, glow `0 0 20px 5px rgba(181,124,255,0.6)` + `inset 0 0 16px rgba(181,124,255,0.3)` |
| **Locked** (illegal this turn) | veil `rgba(15,16,26,0.50)` — dimmed but still readable, deliberately not blacked out |
| **Claimed by P1** | veil `0.76` + centered ✕ 56pt `#ff5c85`, glow `0 0 26px rgba(255,61,113,0.95)` |
| **Claimed by P2** | veil `0.76` + centered ○ 52pt `#4dffb0`, glow `0 0 26px rgba(45,255,158,0.90)` |
| **Cat game** (dead) | veil `0.76` + centered Ø 44pt `#9aa2c2`, glow `0 0 22px rgba(154,162,194,0.75)`, with an 8pt `CAT` label under it |

Claimed and cat quadrants use the same overlay language on purpose: all three read as
"finished," and the color tells you whose it is (or that it belongs to nobody).

### Cell states

| State | Treatment |
|---|---|
| Empty | nothing — transparent |
| P1 mark | ✕ 19/600 `#ff5c85`, glow `0 0 12px rgba(255,61,113,0.95)` + `0 0 3px rgba(255,180,200,0.9)` |
| P2 mark | ○ 19/600 `#4dffb0`, glow `0 0 12px rgba(45,255,158,0.90)` + `0 0 3px rgba(200,255,230,0.85)` |
| **Opponent's last move** | 2pt `#d2cefd` ring, offset −1, radius 5, glow `0 0 14px 3px rgba(181,171,252,0.90)` + `inset 0 0 8px rgba(181,171,252,0.4)` |
| **Pending selection** (first tap) | 2pt **dashed** `#e9e9ed` at 85%, offset −1, radius 5, plus a ghost mark in the current player's color at 40% opacity |

The pending move also lights the **destination quadrant**: 2pt dashed `#e9e9ed` at 80%,
offset −3, radius 12, over a `rgba(233,233,237,0.05)` wash. Dashed = provisional; solid =
committed. That single distinction separates the three highlights:

| Highlight | Scope | Look |
|---|---|---|
| Opponent's last move | one cell | solid lavender ring |
| Active quadrant | one quadrant | solid purple glowing ring |
| Pending move | one cell + one quadrant | **dashed white**, cell also holds a ghost mark |

**Z-order inside a quadrant:** cells 0 → grid lines 1 → veils/claim/cat overlays 2 →
forced ring + destination ring 3 → **last-move ring / pending ring 4**. The last-move ring
is intentionally above the locked veil, so a mark in a now-locked quadrant still reads at a
glance — which is the whole point of the highlight per `Game Board Design.md`.

2d shows all three at once and is worth studying: they played the centre cell of the
bottom-right quadrant (solid lavender), which forced you into the centre quadrant (solid
purple), and your pending pick there is the bottom-left cell (dashed) — which would send
them to the bottom-left quadrant (dashed). Keep that cell→quadrant correspondence exact in
any future mock; it is the rule made visible.

---

## Screens

### 1a — Main Menu

Radial gradient ground: `radial-gradient(120% 65% at 50% 0%, #20233a 0%, #161826 58%, #111320 100%)`.
Padding `96 / 28 / 52`, column, centered.

1. **Logo placeholder** — 104×104, radius 20, `#1b1e2c` fill, **1px dashed `#5d5294`**
   border, glow `0 0 30px rgba(145,132,217,0.22)`; inside, an 11pt-padded 3×3 grid
   (gap 5) of 3×3 dot clusters (gap 2) in `#9184d9` at 75% — 81 dots, the game itself.
   *Replace with real art.*
2. **Title** — kicker `TIC TAC TOE` 13pt, tracking 0.34em, `#b5abfc`; wordmark
   `EXTREME` 44/600, glow `0 0 34px rgba(145,132,217,0.55)`; tagline
   "Nine boards. One winner. Good luck." 13pt `#9397ab`.
3. **Buttons**, pushed to the bottom, 12pt gaps:
   - `PLAY GAME` and `THEME` — equal weight per the docs. Outlined, 2pt `#9184d9`
     border on transparent, text `#9184d9`, 20pt, padding 22, radius 14,
     glow `0 0 24px rgba(145,132,217,0.28)` + `inset 0 0 22px rgba(145,132,217,0.10)`.
   - `Settings` and `About Us` — side by side, 1px `rgba(233,233,237,0.16)` border,
     15pt, padding 16, radius 12.
4. Footer `Theme: Neon · v0.1.0`, 11pt `#595d6c`.

Nothing is filled solid — Nocturne's rule, and it suits the neon look.

### 1b — Select Game

Back button (36×36 icon button, radius 11) + heading "Pick up where you left off" 22/600
with sub "3 games on the go · scores are saved" 12pt `#75798c`.

**`+ NEW GAME`** sits at the **top of the list** (docs), styled as the accent-outlined
primary, 17pt, padding 18, radius 13.

Each open game is a card: `#1e2131`, radius 13, padding `15/16`, 11pt gap.
- Row 1: opponent name 18/600 (left) · relative time 11pt `#75798c` (right).
- Row 2: three mini score chips `YOU / TIES / THEM`, radius 8, `#161826` fill,
  9pt labels + 19/600 values; the **YOU** chip carries a
  `inset 0 0 0 1px rgba(145,132,217,0.35)` outline. Chevron at the far right.

Sample rows: `ItSaMeMaRiO 3-1-2 · 2 hours ago`, `Dad 0-0-4 · Yesterday`,
`Jules 1-2-1 · Sat, 14 Jun`. Footer: "Three saved games. Starting a fourth replaces the
oldest." — reflects the docs' open question (3 slots, unconfirmed).

Selecting `NEW GAME` must prompt for the opponent's name, default **ItSaMeMaRiO**.
**That prompt is not designed yet.**

### 1c — About Us

Ground `linear-gradient(180deg, #1a1d30 0%, #161826 42%)`. Back button, kicker
`ABOUT US` 11pt tracking 0.24em `#b5abfc`, three-line title 34/600, then a
**Nocturne fading rule** (1px, transparent → `rgba(233,233,237,0.16)` at 40px → fade out).

Two body paragraphs, 14pt `#b2b6ca`, line-height 1.65 — **placeholder copy**.
Then a 2-column team grid: `#1e2131` cards, radius 12, padding 14, each with a 34×34
dashed-border avatar placeholder, name 14/600, role 11pt `#75798c`.
Footer: `Neon` and `v0.1.0` tags + "Made on one phone, passed back and forth."

### 1d — Game Board, opening move (free choice)

- **Scoreboard row**: three chips (`1fr` each, gap 6, radius 10, padding `8/6`) +
  a 44×44 settings icon button at the top right (docs). Active player's chip is
  tinted in their color: P1 `rgba(255,61,113,0.14)` fill, 1px `#ff3d71`,
  glow `0 0 16px rgba(255,61,113,0.30)`, label `#ff9fb6`.
- **Turn banner** below it: radius 11, padding `11/13`, tinted like the active chip —
  the player's mark, "Player One, you're up!" 14/600, and the mode cue
  "Free choice — pick any board" in board-blue `#4fc3ff`.
- **Board**: all nine quadrants in the **open** state.
- Hint text: "Tap a square to see where it sends them. / Tap it again to play it."
- Legend pinned to the bottom: Open (blue outline) · Locked (dim swatch) · Cat game (Ø).

### 1e — Game Board, forced quadrant + last move

Same shell, Player Two active (green chip + green banner, cue "Play the middle board"
in `#c9b3ff`). Board state shown: q0 claimed ✕, q2 cat, q4 **forced**, q7 claimed ○,
q8 locked but holding the **last-move** ring on its center cell — center cell → center
quadrant, which is exactly why q4 is the forced one. Keep that consistency in any
future mock; it is the game's core rule made visible.

Bottom legend explains both rings in words:
"They played here last — that's what sent you." / "The only board you can play in right now."

### 1f — Modal: in-game settings / quick actions

Board behind is blurred 2px at 40% opacity; scrim `rgba(15,16,24,0.72)`, **z-index 10**
(the board's claim overlays are stacked, so the sheet's container needs its own
stacking context — `isolation: isolate` on the board wrapper).

Bottom sheet: `#232532`, radius 20, padding 20, shadow
`0 0 0 1px #595d6c, 0 16px 40px rgba(0,0,0,0.65)`.

Title "Settings" 20/600 + close icon button. Four rows, each 13pt vertical padding:

| Row | Sub-label | Shown as |
|---|---|---|
| Sound effects | Buzzes, pops and splats | on |
| Music | Background track | off |
| Vibrate on touch | A little buzz on every valid tap | on |
| Animations | Marks pop, glow and jiggle | on |

**Toggle spec** — 52×31 pill. On: `rgba(145,132,217,0.28)` track, `inset 0 0 0 1.5px #9184d9`,
glow `0 0 14px rgba(145,132,217,0.35)`, 25pt `#d2cefd` knob right. Off: `#161826` track,
`inset 0 0 0 1.5px #3f424d`, 25pt `#595d6c` knob left.

Then a fading rule, the note "Themes live on the main menu — you can't switch mid-game."
(docs: no mid-game theme change), and two actions: **Back to the game** (primary
outline) and **Exit to Main Menu** (secondary). Footer: "Your game and score are saved
automatically."

### 1g — Modal: winner

Finished board stays visible at 60% behind a scrim of
`radial-gradient(70% 40% at 50% 62%, rgba(255,61,113,0.20), transparent 70%)` over
`rgba(15,16,24,0.62)`. Card as above but bordered in the winner's color:
`0 0 0 1px #ff3d71, 0 0 46px rgba(255,61,113,0.30), 0 16px 40px rgba(0,0,0,0.65)`.

Contents, centered: winner's mark at 52pt · "Player One takes it!" 28/600 ·
"Three boards in a row, straight down the middle." 13.5pt `#9397ab` · the three score
chips at 27/600 with a `+1` under the incremented column · **REMATCH** (primary, 18pt,
padding 18) · "Player One goes first next time." · ghost **Exit to Main Menu**.

### 1h — Modal: draw

Same card, neutral border. Glyph pair `✕ / ○` at 44pt in each player's color at 55%
opacity. "Nobody wins this one!" · "The big board filled up with no three in a row.
Cat game." · TIES chip highlighted with `+1` · REMATCH · "Player One goes first again —
a tie doesn't pass it on." (per `Rules.md`).

---

## 2a — Theme Select (overlay, with paywall)

An **overlay on the main menu**, never its own screen (docs). Menu behind drops to 35%
opacity; scrim `rgba(15,16,24,0.72)`; bottom sheet identical to 1f (`#232532`, radius 20,
padding 20).

Header: "Pick your look" 20/600 + "Two free, two extra. Switch any time." 11.5pt `#75798c`,
close icon button right.

Each theme is a row: radius 14, `#161826` fill, padding 14, 14pt gap — a **66×66 preview
tile** (a miniature quadrant rendered in that theme's own colors and marks), the name, and
a one-line description in the theme's voice.

### Ownership states — the part to build carefully

| State | Row treatment | Badge / action |
|---|---|---|
| **Active** | `0 0 0 2px #4fc3ff` + glow `0 0 22px rgba(79,195,255,0.30)` | `ACTIVE` tag (blue) **and** its ownership tag |
| **Free** | `inset 0 0 0 1px #3f424d` | `FREE` tag — `#292b31` bg, `#9397ab` text |
| **Owned** (purchased) | `inset 0 0 0 1px #3f424d`, fully lit | `OWNED` tag — `rgba(45,255,158,0.16)` bg, `#a5ffd8` text |
| **Locked** (for sale) | `inset 0 0 0 1px #2b2f42`, **preview tile at 45% opacity**, name in `#b2b6ca`, description in `#75798c` | price button instead of a tag: accent outline, 2pt `#9184d9`, radius 11, padding `9/13`, 14pt, padlock icon + `$1.99` |

All tags are 9.5pt, tracking 0.1em.

A locked row must read as **buyable, not broken**: the price button is the only
accent-outlined control in the sheet, so it takes the eye. Tapping a locked row anywhere
opens the purchase sheet; tapping a free or owned row applies the theme and closes the
overlay.

Footer: a centered **Restore purchases** link, 11.5pt `#595d6c`, with a small icon —
required by both app stores once you charge for anything.

### The four themes shown

See `themes.catalog.json`. Neon and Classic are real and specified; **Splat** and
**Dinosaurs** exist here only to demonstrate the locked and owned states — their art,
sound and animation sets do not exist. Their preview tiles are deliberately drawn as
**dashed-border placeholders**. Do not ship them as designed.

Per `Theming.md` this is a *direction*, not current scope: "all themes available from the
start… no monetization work now." Build the theme list so an `ownership` field
(`free | owned | locked`) and a price can be attached per theme without reshaping the
screen, and keep purchase state **out of the theme definition** — a theme is an
audio-visual package; entitlement is account/device state.

## 2b — Settings page (from the main menu)

Full screen, not a sheet — this is the main-menu route; 1f stays the trimmed in-game
version with the exit action. Padding `64 / 20 / 52`.

Back button + "Settings" 22/600 + "These stick around between games." 12pt `#75798c`.

The four toggles live in one grouped card: `#1e2131`, radius 16, padding `6/16`,
`0 0 0 1px #2b2f42`, each row 15pt vertical padding, name 15/500 with an 11.5pt `#75798c`
sub-label. Toggle spec is identical to 1f.

Below it, a separate card shows **Theme — Picked from the main menu** with the active
theme as a tag and no control: the docs forbid changing the theme from anywhere but the
menu, and showing it read-only here answers the "where is it?" question without adding a
second entry point.

Footer: "Sound and animations are part of the theme — these switches turn them off for
every theme." That is the mental model the docs describe; keep the sentence.

## 2c — New Game, opponent name prompt

A sheet over the games list (list dimmed to 30% behind `rgba(15,16,24,0.74)`), with the
system keyboard up. The docs leave "own screen or overlay" open — this picks overlay, so
the list stays visible and Cancel costs nothing.

- Title "Who are you playing?" 20/600.
- Sub: "Just a name for the list — on the board you're still Player One and Player Two."
  12.5pt `#75798c`. This encodes the docs' decision that the opponent name does **not**
  replace "Player Two" in game.
- Field: label "Opponent" 11pt `#9397ab`; input min-height 52, radius 13, `#161826`,
  focused border `inset 0 0 0 2px #9184d9` + glow `0 0 18px rgba(145,132,217,0.25)`,
  value 18/500, caret `#b5abfc`, character counter `11/16` at 11pt `#595d6c`.
- Default value **ItSaMeMaRiO**, pre-selected so typing replaces it.
- Helper: "Leave it as is if you can't be bothered."
- Actions: `Cancel` (secondary, flex 1) and `Start playing` (primary, flex 2).

**Max 16 characters** — the list row truncates past that. An empty name falls back to the
default rather than blocking.

## 2d — Board, pending move

Same board shell as 1e. The turn banner switches to the provisional voice: a dashed
swatch, "Play here?" 14/600, and "Tap again to lock it in" — neutral-tinted
(`rgba(233,233,237,0.06)`, `inset 0 0 0 1px rgba(233,233,237,0.35)`) rather than the active
player's color, because nothing has happened yet.

No sound fires on selection (docs). The haptic **does** fire — selecting a legal cell is a
valid action.

---

## Interactions & behavior

Design-level only; game logic lives in `Rules.md`.

- **Two-tap move.** Tap a legal cell → provisional selection, big board previews the
  destination quadrant. Tap the same cell again → commit. Tap a different cell →
  reselect. Tap outside the grid → clear. *Preview visuals still to be designed.*
- **Illegal tap does nothing** — no shake, no flash, no error, and **no haptic**. The
  absence of the buzz is the feedback, which is why the locked veil sits at 0.50: it
  must be obviously non-tappable while still readable.
- **Haptic on every valid tap**, including the first tap of a two-tap move
  (subject to the Vibrate setting). Haptics are an app setting, never theme-driven.
- **Turn handoff is instant** — no "pass the phone" screen; there is no hidden info.
- **Settings button** (top right, both board screens) opens 1f; it is also the only way
  out of a game. Leaving is safe — the game and its scoreboard persist.
- **Game over** → 1g / 1h overlays the finished board; the board stays visible behind.
  **REMATCH** resets the board, increments the right column, and stays in the same save
  slot. Winner goes first; after a tie, whoever went first goes first again.
- **Animations** (from `Animations.md`): poppy, marker-only, one at a time, never
  blocking input, per-animation durations, and a global off switch that produces
  *instant* state changes with no substitute effect. Starting values are in
  `neon.theme.json → animation`. Every screen above is fully readable with animation off —
  that is the correctness test.
- **Focus/hover** on any pointer or keyboard platform: 2px `#9184d9` outline at 2px offset.

## State

Per open game (persisted — `Tech Design.md` names Hive):

```
Game {
  id, opponentName,
  cells[9][9]        // null | 'p1' | 'p2'
  quadrants[9]       // 'open' | 'p1' | 'p2' | 'cat'
  activeQuadrant     // 0..8, or null = free choice
  currentPlayer      // 'p1' | 'p2'
  lastMove           // { quadrant, cell } | null
  pendingSelection   // { quadrant, cell } | null   (never persisted)
  score { p1, ties, p2 }
  firstPlayerThisGame
  updatedAt
}
```

Global preferences (persisted separately): `themeId` (UUID, default Neon), `sound`,
`music`, `vibrate`, `animations`.

Derived for rendering: a quadrant is **forced** when `activeQuadrant === i`;
**open** when `activeQuadrant === null` and `quadrants[i] === 'open'`;
**locked** otherwise.

## Assets

- **Fonts** — Inter 400/500/600 (Google Fonts). Bundle it; do not rely on a CDN.
- **Icons** — Phosphor (chevron-left, chevron-right, plus, x, sliders-horizontal).
  The prototype hand-draws simplified equivalents on a 256 viewBox; use the real
  Phosphor set in the app.
- **Logo** — placeholder only. Needs real art.
- **Team photos** (1c) — placeholder only.
- **Sounds** — none produced. Neon's signature is an electric buzz; Classic Red vs Blue
  is a splat.

## Files in this bundle

```
design_handoff_game_ui/
├── README.md                 ← this file
├── neon.theme.json           ← the complete Neon theme, machine-readable
├── themes.catalog.json       ← the four themes + ownership/paywall states
└── design-files/
    ├── Tic Tac Toe Extreme - Screens.dc.html   all 12 screens (turn 2 at the top)
    ├── Board.dc.html                            the board renderer
    ├── ios-frame.jsx                            presentation bezel — do not port
    └── nocturne-styles.css                      token sheet the neutrals came from
```

Open the two `.dc.html` files in a browser to see the designs.

## Still to design

1. The Classic Red vs Blue theme itself (only its two-color preview exists).
2. Splat and Dinosaurs — art, sound and animation sets, and the purchase sheet.
3. The "theme failed to load" modal (`Theming.md`: apologise, then fall back to Neon).
4. Real logo and About Us copy.
5. Leave-game confirmation, if you decide one is still warranted now that nothing is lost.
