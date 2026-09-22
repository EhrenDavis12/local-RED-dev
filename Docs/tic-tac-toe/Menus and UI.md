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
- **Settings** — opens the settings menu. Smaller than the three above it.
- **About Us** — last in the list, same smaller treatment as Settings.

**Settings and About Us sit side by side in one row**, sharing its width — not two more
full-width buttons stacked under the large ones. So the menu has two button tiers: the
big two, and the small pair beneath them.

**Play Game and Theme are the same tier, not merely similar.** Both draw from one
treatment, so a change to one is a change to the other and no theme can drift them apart.

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

**The menu compacts itself rather than clipping on a short screen.** At the handoff's own
390×844 the layout above is drawn exactly as it stands. When the height is too small for
it — an iPhone SE at 375×667 is the screen that found this — the hero shrinks: a smaller
icon box, tighter gaps, and the tagline dropped. If even that would not fit, the menu
scrolls, so nothing is ever lost off the bottom. The height it switches at is worked out
from the active theme's own type sizes rather than a fixed screen size, so a theme with
larger text compacts sooner instead of inheriting Neon's threshold.

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
position is explicitly provisional — the user said "for now we might move it
in the future" — so a later reordering is expected rather than a reversal.

Because Settings and About Us share a row, that pairing is the part a later reorder has to
revisit — nothing else in the menu depends on About Us being last.

One thing this doesn't settle:
- The screen's **content** is not specified by any doc. The handoff draws team photos;
  where those come from is not decided.

## Play Game → Where It Takes You
Play Game branches on whether there are existing open games.

- **No open games** — the list opens with the New Game choice already up, so the choice
  between a game on this phone and an online one is there on a fresh install too. Where
  there is no Game Center to offer, it still goes straight into a new game on this phone,
  no intermediate screen.
- **Open games exist** — a new screen listing all open games, with **New Game** as an
  option at the **top of the list**.
- **Each open game is titled with its opponent's name** — that's what a row shows.
- **Selecting New Game asks which kind of game first** — on this phone, invite a friend, or
  play an anonymous game. On this phone then prompts for the opponent's name, with a default
  of **ItSaMeMaRiO**; the two online choices go to Game Center instead and nobody types a
  name. See **Starting a game — on this phone or online** below.
- **An online game is titled with the opponent's Game Center nickname**, taken when the match
  is created. Nobody types it. Nothing renames it either, with one exception: an anonymous
  game is started before there is an opponent to name it after, so it carries a placeholder
  title while it looks for a player and takes the real nickname once one is found — see
  [Tech Design](./Tech%20Design.md) → Online Play.

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

**The list is ordered most-recently-played first**, so the game you were last in sits at
the top. It shows every open game — none is hidden, truncated or paginated away — so with
the cap raised to 100 the list scrolls.

**A row shows the opponent's name, and on an online game a line saying where that game
stands.** An anonymous game that has not found anybody yet says it is looking for a player,
and that line outranks every other one except the opponent having left; opening that row goes
to the searching screen rather than the board. What else a row carries is not settled: the
handoff draws a relative time and three score chips on every row, and neither is decided —
see Open Questions.

**The footer drawn on `1b` — "Three saved games. Starting a fourth replaces the oldest." —
does not ship.** Nothing ever removes a game the player did not choose to delete, so the
drawing is stale on that point, and what the footer says instead is unwritten.

**The opponent name typed at New Game does not replace "Player Two" in game.** It titles
the game in the open-games list and nothing else. In a game on this phone the players are
still **Player One** and **Player Two**.

**An online game's scoreboard reads the two players' Game Center account names** in place
of Player One and Player Two — this player's own account on one side and the opponent's on
the other. See [Game Overview](./Game%20Overview.md) →
Session Structure — Games and Continuing.

**The name field comes up pre-filled with ItSaMeMaRiO and the text selected**, so typing
replaces it. Leaving it empty falls back to ItSaMeMaRiO rather than blocking, and the
field takes at most 16 characters. Cancelling the prompt creates nothing. The prompt never
comes up for an online game, whose title is the opponent's Game Center nickname — though an
online game whose opponent has not resolved yet carries a placeholder title until that
nickname arrives.

**Opening a game from the list shows that game.** The board is not drawn until the saved
position has loaded, so a player never sees an empty board, or the game they were in
before, standing in for it.

### Starting a game — on this phone or online
**New Game asks which kind of game first.** Three choices, weighted the same: **On this
phone**, **Invite a friend** and **Play an anonymous game**. On this phone goes to the
opponent-name prompt above. Both online choices run the same online entry first — Game Center
sign-in, then the grown-up question if the account is a child's — and differ only in how the
opponent is found: Invite a friend opens Apple's find-a-player sheet, and Play an anonymous
game is our own door to a random opponent and shows no Apple sheet at all. See
[Tech Design](./Tech%20Design.md) → Online Play.

**Play an anonymous game exists because Apple's sheet cannot be made to say what it does.**
Apple's own **Start Game** button says nothing about playing a random person, and it starts a
game before anybody has been found, so a player who taps it is left on a board with no
opponent and no explanation. Our own door can say what it is doing: a searching screen while
it looks, and the game starting once a pair is actually found, so the game knows you found
somebody.

**Both online choices are hidden where there is no Game Center**, which today means anything
that is not iOS. With one choice left the prompt skips the question and opens the name prompt
straight away.

**Local and online games share one limit and one list.** There is no separate online
allowance and no second list of games — the open-games list is where every game lives, and
New Game is the only place any of them is started from.

**New Game refuses at the cap before anything is asked of Apple**, whichever online choice was
tapped, so neither Apple's sheet nor a search for a random opponent is ever reached by a player
with no slot to put the game in. A match started at the cap would be left orphaned in Game
Center with nothing on this phone pointing at it.

**Invite a friend ends one of these ways:**

- **A match is found** — the game is stored and opens on the board, the same as picking it
  out of the list.
- **The match is waiting on the other player's first move** — a short message says so and
  the player stays on the open-games list. The game turns up in the list once that first
  turn lands.
- **The account is not allowed to play online**, **the open-games box is full**, or
  **Game Center fails** — each shows a short message and the player stays on the list.

**On the other phone an invited game appears the moment the invite is accepted** — Player Two,
waiting on the other player — because the starting phone puts the fresh board into the match as
soon as the match is made. If that does not go through, the game turns up with the first move
instead, and a short message says they joined until it does.

**Play an anonymous game ends one of these ways:**

- **Somebody was already waiting** — their game is picked up as it stands, stored here, and
  opens on the board with the first move to make. The player who joins an anonymous game plays
  **Player One** and moves first.
- **Nobody was waiting** — a game is started and stored here straight away, marked as looking
  for a player, and the searching screen comes up. The player who starts an anonymous game
  plays **Player Two**, so whoever joins moves first.
- **The account is not allowed to play online**, **the open-games box is full**, or
  **Game Center fails** — each shows a short message and the player stays on the list.

**A game that is still looking for a player is an ordinary open game.** It is in the list, it
holds a slot against the limit like any other, and deleting it is how the search is called off
— the ordinary delete, with its best-effort resign. Its row says it is looking for a player,
and opening it goes back to the searching screen rather than to the board.

**The searching screen** is calm: a looping indicator, a line saying it is looking for a
player, and a button to keep looking in the background, which goes back to the open-games list
and leaves the game searching. While it is up it keeps checking that the handoff to Game Center
actually went out — on arrival and on every check after — and a **Retry** appears only when it
has not. It catches up with Game Center every fifteen seconds, and when the first move arrives
or the opponent's name resolves it says who was found for a beat and then opens the board.

**An invite that arrives while the box is full creates nothing** — a message says to delete
a game to make room for it. Deleting one brings the game in: the app catches up with Game
Center after every delete, and the invite it turned away arrives on that catch-up.

**The list refreshes itself when a turn arrives** — a row that said it was waiting on the
other player says it is your turn, without the player leaving the screen and coming back. **A
game the other player has left says so on its row**, in place of whose turn it is, until it is
deleted.

**What any of those messages say is not settled** — see Open Questions.

**These messages use the themed snackbar the New Game prompt already uses for its own
full-box message** — one style for one kind of message, whichever door raised it. A new
message replaces one still on screen rather than queueing behind it. The New Game sheet
closes the moment Online is chosen, so they land on the open-games list behind it: the sheet
is long gone by the time Game Center answers.

**A second tap while one is already in flight does nothing.** One sign-in, one gate and one
matchmaker at a time.

### Pick your Icon
**An online game asks each player to pick their own icon the first time that game's board is
opened on this phone**, before a move is made or seen. One screen split into a top half and
a bottom half, titled **Pick your Icon**: the theme's two player marks, one in each half, and
the player taps the one they want to be. *"It would be One screen devided in half with Pick
your Icon."* *"I like top and bottom"*

**The pick is asked once per open game and kept through rematches.** A rematch continues in
the same open game, so the mark a player chose stays theirs for the whole series and the
screen never comes up again for that game. It is saved with that game on this phone, so
starting a second online game asks again.

**The pick is that phone's alone.** The mark the player picked is drawn for them and the
other mark for the other player, on this phone only. The other player picks on their own
phone, out of their own theme, and may pick the same one — neither pick crosses to the other
phone and neither player is forced into a mark or a theme by the other. *"Themes should be
what they want on their phone and not forced into a theme by the other player. this is gonig
to be impotant as a player might have a theme and really wants to be a specific icon."*

What the pick does and does not reach is [Game Board Design](./Game%20Board%20Design.md) →
Pieces & Marks.

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

**Reaching the cap never makes the app delete or replace a game on its own.** A slot is
freed only by the player deleting one — see **Deleting an open game** below, and
[Tech Design](./Tech%20Design.md) → The cap is enforced on create, and the store never
evicts. What the New Game action offers a player who is already at the cap is not settled
— see Open Questions.

**Online games count against the same cap, and there is one list, not two.** An online game
holds a slot exactly as a game on this phone does, so a player at the cap can neither start
one nor accept an invite to one until they delete a game. There is no separate online
allowance and no second list — an invite turned away at the cap comes back in once a game
is deleted. See **Starting a game — on this phone or online** above.

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
modal's buttons are **Yes and No**, not Cancel/Delete. **The trash button is themed like
anything else on screen** — every theme styles it, in its own colour and in its own art
where the theme ships art, and it is never drawn in an unstyled default: *"The game delete
button needs to follow the theme in some way otherwise it look bad."* See
[Theming](./Theming.md) → What a Theme Controls.

**The revealed trash button stays put when the finger lifts** — it has to, since the player
has to tap it — and the reveal closes again on swiping the row back, on tapping the trash
button, or on tapping the row body. **Tapping the row body closes the reveal and does not
open the game**: it is the standard iOS behaviour and the safer one to sit next to a
destructive control, at the cost of a tap that would have resumed a game doing nothing.

**The row itself has to show that it slides left to delete.** A player who does not already
know the gesture has nothing to find: *"I know to slide left to delete but the user does
not. We need a way to tell the user to swipe left on the game button to delete."* The answer
is a design cue on the row — *"The best would be some kind of design aspect signals to the
user how to delete and that the button is slidable to be deleted."* — with help text as the
floor rather than the answer: *"Help Text is bear minumum."* What that cue is is not settled
— see Open Questions.

The confirmation is there because deleting a game is the only irreversible action in the
app — it destroys the game and its whole running scoreboard — and kids are a stated target
audience (see [Game Overview](./Game%20Overview.md) → Target Audience & Platform).

**Deleting an online game resigns the Game Center match and takes it off Game Center's own
list**, so the other player's copy ends instead of waiting on a turn that never comes and
the match does not sit in Apple's list after the player has thrown the game away. Both are
best-effort and neither blocks the delete: a player who asked for a game to be gone gets it
gone whether or not Apple could be reached. **Deleting a game the other player already left
resigns nothing** — they are gone, so there is nothing to tell them — but it is still taken
off Apple's list. Either way the game is gone for good: the phone remembers that match well
enough to throw away anything that turns up for it afterwards, so a deleted game never
reappears. See [Tech Design](./Tech%20Design.md) → Online Play.

**Deleting an anonymous game that is still looking for a player cancels the search.** There is
no separate cancel: the search is the game, so the ordinary delete — the same confirmation, the
same best-effort resign, the same memory of the match so nothing turns up for it afterwards —
is what stops it.

**Deleting the last open game leaves the player on the list**, with New Game alone on it,
rather than dropping them into a new game.

Consequence for theming: the trash button and the modal's **Yes** are the only
**destructive** treatment in the app, and nothing else gets one. The approved handoff draws
no delete affordance at all on screen `1b` — this section is the source of the affordance,
not the drawing.

## A New Game → What It Starts
- A **two player game on the same exact phone**. One device, passed back and forth.
- It starts **empty** — no marks anywhere on the nine boards, a score of **0–0–0**, and
  **Player One** to move (see [Rules](./Rules.md) → Turn Order Across Games).
- Turn order alternates: Player One → Player Two → Player One → Player Two → ...
- After a player makes their move, it becomes the other player's turn.
- No AI opponent. This section is the game on this phone; an online game is started from
  the same New Game, by choosing Online — see **Play Game → Where It Takes You** →
  **Starting a game — on this phone or online** above, and
  [Tech Design](./Tech%20Design.md) → Online Play.

## Pass-and-Play Turn Handoff
- The game switches the active player automatically after each move.
- The UI has to make it obvious *whose turn it is right now*, since both players are
  looking at the same screen. Two things say it: the turn banner names the active player
  whenever no move is pending, and the active player's counter on the scoreboard is
  highlighted — see [Game Board Design](./Game%20Board%20Design.md) → Turn Indicator.
- Note: tic-tac-toe has no hidden information, so there's no need for a "pass the phone,
  don't peek" screen between turns. The handoff is instant.

**The turn passes on the confirming tap, not on the first one.** Tapping a cell to preview
a move leaves it the same player's turn — the active player changes only when that move
is confirmed, and it changes there and then. Nothing sits between the confirming tap and
the opponent's turn: no interstitial, no "pass the phone" screen, no intermediate state
of any kind. The approved handoff says it the same way — *"Turn handoff is instant —
no 'pass the phone' screen; there is no hidden info."*

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

**The turn banner is built, and it is visible whenever there is a turn to announce, not
only while a move is pending, and it carries two things.** Normally it says whose turn it
is — the approved handoff draws this as *"Player One, you're up!"*. When a move is
pending it switches to the pending-move prompt: the two lines *"Play here?"* and *"Tap
again to lock it in."* that appear when a player taps a square to preview a move before
confirming it. That is what the approved handoff draws on screen `2d`.

Because the banner is visible whenever there is a turn to announce, it takes vertical
space on every board screen with a turn to announce, not only while a move is pending.

**On an online game the banner's slot carries that game's own state instead.** While it is
the opponent's turn it names them by their Game Center account name — *"Waiting on Sam…"* —
with that side's own mark beside it as always, and nothing else on the screen moves. On your
own turn it reads *"You're up!"* and names nobody, there being only one player on this phone
to address. Player One and Player Two stay the banner's names on a game on this phone, where
there is no account to name either player with.
While a confirmed move is being handed to Game Center the banner says so, and it reads the
same whether that send was begun by the confirming tap or by a retry. A send that did not go
through says so and carries two controls with it: send it again, and leave for the main
menu — whether Game Center refused it or it never got that far. Those two are the only
controls the online states add — each plays the button-tap
sound and fires no haptic, like the result card's own way out — and the confirmed move
stays on the board behind them, to be sent again. When the other player has left, the banner
says so and says nothing else: it takes the slot ahead of every other state and keeps it even
once the board has finished, since there is no result card there to hand off to, and it
carries no control of its own. What the sending, failed-send and opponent-left states say is
not settled — see Open Questions.

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
3. **New Game Prompt** — asks first whether the game is on this phone, an invite to a friend
   or an anonymous game, then, for a game on this phone, asks for the opponent's name with
   **ItSaMeMaRiO** as the default. Undecided whether it's its own screen or an overlay.
4. **Game Screen** — the board (see [Game Board Design](./Game%20Board%20Design.md)).
5. **Theme Selection** — an **overlay on the main menu**, not its own screen. Opened by
   the Theme button. Three themes at launch — **Neon**, **Classic Red vs Blue** and
   **Sewing** (see [Theming](./Theming.md)). See [Theme Selection](#theme-selection)
   below.
6. **Settings** — reachable from *both* the main menu and the gameplay screen (top-right
   button → quick actions).
7. **About Us** — reached from the main menu (About Us button). A full screen of its own,
   not an overlay: nothing stays visible behind it. See Main Menu → About Us.
8. **Parental Gate** — the grown-up check, over whatever raised it rather than in place of
   it. See [The Parental Gate](#the-parental-gate) below.
9. **Searching** — the waiting room for an anonymous game that has not found a player yet.
   Reached by starting one, and by opening a still-searching game from the open-games list.
   See Play Game → Where It Takes You → Starting a game — on this phone or online.
10. **Pick your Icon** — one screen split top and bottom, shown the first time an online
    game's board is opened on this phone, where each player picks which of the theme's two
    marks is theirs. See Play Game → Where It Takes You → Pick your Icon.

The first seven each have an approved drawing in
[Design Handoff](./design_handoff_game_ui/README.md); the parental gate, the searching
screen and Pick your Icon have none:

| Screen above | Handoff screen |
|---|---|
| Main Menu | `1a — Main Menu` |
| Open Games List | `1b — Select Game` |
| New Game Prompt | `2c — New Game, opponent name prompt` |
| Game Screen | `1d` (free choice), `1e` (forced quadrant), `2d` (pending move) |
| Theme Selection | `2a — Theme Select (overlay, with paywall)` |
| Settings (main menu) | `2b — Settings page (from the main menu)` |
| Settings (in game) | `1f — Modal: in-game settings / quick actions` |
| Game over | `1g — Modal: winner`, `1h — Modal: draw` |
| About Us | `1c — About Us` |

`1a` draws the menu's four buttons, and the menu carries exactly those four.

Content for About Us is still unsettled — see Main Menu → About Us.

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

**Exiting a game replaces the stack rather than unwinding one step.** The main menu comes
back with nothing behind it — the game is gone from the back stack, so the iOS back-swipe
can't carry a player back into a game they just left. That holds the same way whether the
game was abandoned mid-play from quick actions or finished and left from the result card;
both leave by the same route.

**Every navigation clears a pending, unconfirmed move** — opening a menu or sheet over the
board, and leaving the board altogether. It's the same rule as any tap outside the nine
quadrants, reaching the surfaces that open on top of it — see
[Game Board Design](./Game%20Board%20Design.md) → Changing your mind.

**The back-swipe can't carry a player out of a live game either — the gesture is turned
off on the game screen.** The only way off the board is the explicit exit: quick actions
mid-play, back to main menu on the result card, or the way out offered beside a send Game
Center refused. It's turned off there because a swipe off the board would slip past that
clearing, which every other way off the board does. The block belongs to the screen rather
than to the state of the game, so it holds over a finished board as well as a live one —
the result card carries its own way out, so nobody is stranded on one.

**The open-games list has a back control that leaves it without picking anything.** `1b`
draws one; where it goes isn't decided — see Open Questions below.

**The main menu is the app's launch screen.** It is assumed throughout this doc (e.g. Main
Menu is screen 1 in **Screens (so far)**) and stated nowhere else.

## Theme Selection
Opened by the **Theme** button on the main menu, and by nothing else. This is an
**overlay** on the main menu, not its own screen — see [Theming](./Theming.md). The main
menu stays mounted and painted underneath it, dimmed — see **Main Menu** above.

**The sheet's header is "Pick your look"**, with **"Switch any time."** on a second line
under it.

**Three options at launch:**
- **Neon** — black background, electric neon colors. The base theme.
- **Classic Red vs Blue** — the plain, familiar look. Red player vs blue player.
- **Sewing** — a soft blue cloth ground, scissors and buttons for marks.

See [Theming](./Theming.md) → Theme Catalog for the full look of each.

**The list is one row per theme file in the themes folder**, so adding a theme is dropping
one file in and nothing on this screen changes — see [Theming](./Theming.md) → Where
Themes Live. **The list always renders.** One theme file the app can't read never blanks
the overlay or stops the other rows from appearing.

**Each row shows a preview tile, the theme's name and a one-line description, all read
from that theme's own file.** The preview tile is a miniature quadrant rendered in that
theme's own colors and marks — that theme's grid lines, and one mark from each player — so
two themes side by side are told apart by the tile alone. An empty grid, or a grid drawn
in the *active* theme's colors, isn't this. The tile is a single quadrant, so it shows a
theme's small-board lines and never its big-board separators.

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
Every theme that ships is free, so no row is locked at launch. The purchases section and
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

**A theme file the app cannot read never reaches this list.** It is dropped rather than
shown, so there is no unavailable row to tap and no failure message on this overlay —
see [Theming](./Theming.md) → Choosing a Theme.

**A theme whose art is missing still reaches it.** Art is resolved when it is drawn, not
when the theme is loaded, so a theme naming a file that is not there still parses, still
lists, and is still selectable — it simply draws what a theme with no art draws. Only an
unreadable theme *file* is dropped.

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
│  PLAYER 1   CAT    PLAYER 2  ⚙  │  ← settings, top right
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

## The Parental Gate
**The gate is its own surface, over whatever raised it** — the purchases section, and either
online choice in New Game, for a child's account. It shows a line addressed to a
grown-up, the problem in words, a field for the answer, a Submit, and a way out. After the
third wrong answer it stops asking: the prompt, the problem, the field and Submit all go,
and what is left is a line saying the tries are used up, with the way out. The way out and
a tap on the scrim behind the card both leave the gate while attempts remain, and so does
anything that takes the surface away without either — the platform back-swipe among them.

**None of the wording is settled**, and none of it is drawn: the handoff has no gate screen,
the same gap [Theming](./Theming.md) records for the settings purchases section. What the
gate asks, what a pass is worth, and what raises it are
[Tech Design](./Tech%20Design.md) → In-App Purchases and Entitlements → The parental gate — a
word problem, every time.

## Dynamic Type
**The app does not scale its text to the iOS Dynamic Type setting in this version.** Not
for now — *"Lets not do this as of yet."*

So the Settings screen carries no text-size control of its own.

## Game Over → Rematch
When a game is won or tied, the scoreboard increments **at game end** — the winner's
column, or Cat, as soon as the game is won or tied, not when a rematch is taken. A
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
its win line drawn and the result card below it, exactly as it was left.

### The result card
**On a win, the result card is preceded by the game-win sequence** — the deciding
quadrant's small-board celebration, then the big-board win line drawing across the three
winning quadrants, then the win display — and the result card appears once that
finishes. See [Animations](./Animations.md) → Where Animations Fire. With animations off,
none of that plays and the result card appears instantly, same as today. Once the card is
showing, its own behavior is unchanged.

**The result card is a bottom-anchored panel** — it sits at the bottom of the screen, below
the board, with no scrim and no dim. Not a separate screen and not a banner. The finished
board and its big-board win line stay fully visible while the card is up, so there is
nothing to put aside to look at the finished board — the board is never covered in the
first place.

The card's own fill, border and radius are theme values like everything else; its spacing
and padding are not, since those are fixed in code app-wide (see
[Theming](./Theming.md) → What a Theme Does NOT Control).

**The card says what happened, in words, and a win and a tie read differently.** A win
names the winning player — Player One or Player Two on a game on this phone, and on an
online game that player's Game Center account name, *"Sam takes it!"*. A tie names nobody —
most quadrants claimed does not win it (see [Rules](./Rules.md) → Edge Cases).

**It shows the running score, already counting the game that just ended**, with the column
that moved identifiable, and **it says who goes first in the next game** — naming that
player the same way the win line does, by account name on an online game.

**The result card carries two buttons — one to start the next game, and one to go back to
the main menu.** *"On game over result card we should have a button for next game as well
as back to main menu."*

**The rematch button shows on an online game too**, and taking it asks Game Center for the
rematch rather than only resetting the board here: Apple mints a fresh match, the series
carries on in the same open game with the scoreboard intact, and the next game's board is
handed off under that new match the same way any move is. While the app is asking, the button
says so and a second tap does nothing; a rematch Apple refuses leaves the card up and says so.
Both players tapping it at once is safe — whichever rematch lands first is the one the series
continues in.

**The winner's rematch waits until the loser has seen the result.** Apple will not mint a
rematch while the old match is still open, and it is the losing player's phone that closes
it, as soon as that finished board is on their screen — see
[Tech Design](./Tech%20Design.md) → Online Play. So the winner's card comes up with its
button already saying it is waiting on the other player, *"Waiting for Sam to see the
result"* — no tap is needed to find that out, the button takes no tap, and the wait survives
a relaunch — and it comes back to life by itself once their phone has closed the match. The
rematch is never queued to start on its own; the player taps it again when it does. The name
is the opponent's Game Center account name, with the same fallback every other line naming
them already uses.

**A send in flight and a failed send both outrank the waiting button.** Until the finishing
move has actually left this phone the screen shows what it shows for those two states — the
sending notice, and the failed send with its retry and its way out — rather than telling the
player they are waiting on an opponent who has not been handed the move yet. The losing
player's own card never waits either: it draws the ordinary rematch button throughout, and a
rematch Apple refuses there leaves the card up and says so.

**A game the other player left offers no rematch.** They left mid-game, so the board never
finished and there is no result card either — the banner says they left, the board takes no
taps, and deleting the game is the way out. The rematch is hidden rather than shown disabled,
because nothing defines a disabled-control treatment and a hidden control needs no theme value
of its own.

**A game the opponent ended shows the card with no celebration.** An arriving turn plays no
animation at all — no claim pop, no small-board line, no big-board line drawing across and
no win display — so the finished board is drawn at rest with its win line and the card
is up, which is the same thing a reopened finished game shows (see
[Animations](./Animations.md) → Where Animations Fire). The celebration belongs to the
confirming tap that ends the game, and on an online game that tap was made on the other
phone.

The card is self-sufficient, so the player is never dependent on the settings button to
leave a finished game. The result stays up until one of its buttons is pressed, and leaving
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

The write lands as the move is confirmed, on the move itself — not on leaving the game.

**Taking the next game is written straight away too, even though it isn't a move.** The
board a rematch starts is saved as it comes up, rather than waiting for the first move of
that game to carry it. Otherwise a player who takes the next game and quits before playing
reopens the *finished* board with the result card still over it, having already asked for
a new one.

**On an online game both of those writes wait for Game Center to accept the turn.** The move
appears on the board as it is confirmed, but nothing is stored until Apple has taken it — so a
stored board never shows the opponent to move on a turn this phone never handed off — and
taking the next game of an online series is written with its new match id on the same accept.
Until a move goes through, that game accepts no further move, and a send that fails keeps the
move on screen to be sent again. Quitting the app in the gap between Apple taking the move and
this phone writing it does not lose it: Apple's copy is the one both phones agreed on, and the
next turn to arrive puts the missing move back. A move Apple never took is lost, which is what
the other player sees too. See [Tech Design](./Tech%20Design.md) → Online Play.

**A brand-new game is written the moment it starts**, before a single mark is placed — the
record has to exist for anything later to be saved against it. So a player who starts a
game and walks away without playing still finds it in the open-games list, empty, holding
one of their slots until they delete it.

### Leaving a game mid-play
Since a game in progress is saved, going back to the main menu doesn't discard anything —
the game stays in the open-games list with its own scoreboard, and you can pick it up
again. Whether leaving still needs a confirmation prompt is undecided; the original
reason for one ("Leave game? Your score will be lost") no longer applies.

Leaving performs no write of its own — the last confirmed move was already saved when it
was confirmed, so there is nothing left to lose at the exit. A force-quit, a crash and a
deliberate walk back to the main menu all leave the same thing on disk.

Nothing but deleting a game from the open-games list ever removes one — see **Deleting
an open game** above.

## Open Questions
- Future menu items to consider later: Rules/How to Play, Settings, vs. AI.
- **Where does the parental gate belong among the app's screens, and what does it say?** It
  is built and it works, but nothing draws it and nothing settles its wording — the grown-up
  prompt, the problem line, the Submit and the out-of-attempts line are all the screen's own
  choice for now.
- **What do the online messages say?** Four land on the open-games list, where New Game
  raised them — the account is not allowed to play online, the match is waiting on the
  other player, the open-games box is full, and Game Center couldn't do it. Two more land
  on whichever of the main menu or the open-games list the player is looking at, because an
  invite arrives without being asked for — you joined someone's game, and an invite arrived
  with no slot to put it in. None of the wording is settled. What a player is told for a
  declined sign-in, a cancelled matchmaker or a payload that is turned away is
  [Tech Design](./Tech%20Design.md) → Open Questions → *Online play — what the player is
  told*.
- **Does the back-swipe stay live on every other screen**, or is "you leave a surface by
  its own control" a rule of the whole app? It's off on the game screen only, because
  that's the one place a swipe would walk away from a pending move. Everywhere else it
  unwinds one step, which on the open-games list quietly picks one of the two answers to
  the question below.
- **What does the Android system back button do?** Nothing written mentions it, on any
  screen. Whatever turns the swipe off on the game screen turns Android back off there
  too, which is a side effect rather than a decision anyone took.
- **Where does back from the open-games list lead** — one step back, which is the main
  menu whenever the list was reached from it, or always to the main menu whatever it was
  reached from? The two only differ once there's a second way into the list.
- **What control takes you back to the game from the in-game settings surface?** Reaching
  settings mid-game doesn't abandon the game, but nothing names the control that returns
  you to it. The handoff gives `1f` a close button and a "Back to the game" action; the
  docs give it neither.
- **Does anything render before the main menu?** The main menu is the launch screen, but
  nothing rules out a splash, or a loading state held while the saved theme is
  materialized.
- **Is there also a fuller Rules/How-to-Play screen**, separate from the on-board legend
  and hint, or does the legend/hint fully cover "how to play" for this version? (Already
  listed above as a future menu item to consider.)
- **Which strip content belongs to which board state, and is the set of states exactly the
  three the handoff draws (`1d`, `1e`, `2d`)?** The board has more states than that — game
  over, free choice after being sent to a dead quadrant, and on an online game waiting on
  the opponent, a move being sent, a send that failed, and the other player having left —
  and it's not decided what, if anything, this strip shows for those.
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
- **Is the Neon fallback remembered?** When a theme fails to load and the app drops back
  to Neon, does Neon become the saved choice, or is the player's original pick kept and
  tried again next launch?
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
- **Does the `+1` under the column that just moved show again when a finished game is
  reopened later**, or only on the result that has just happened?
- **What does New Game do when the player is already at the cap** — refuse and say the list
  is full, route the player into the delete flow, offer the $4.99 unlock at the moment the
  limit bites, or some combination of those? It refuses and says so today, for a game on
  this phone and for an online one alike, and an invite arriving at the cap is turned away
  with a message; whether a refusal is where this lands is what is open. The cap itself and
  the rule that only a player-initiated delete frees a slot are settled; this is only what
  the player is offered instead.
- **What happens to games already stored above the cap if the unlock goes away?** A player
  with 60 open games whose ceiling drops back to 3 has 57 games nothing is willing to
  touch.
- **Does an open-game row show anything besides the opponent's name?** The handoff draws a
  relative time and three score chips on every row. If a date ships, it isn't settled
  whether it's when the game was started or when it was last played, or how it reads.
- **If the score chips ship, what are they labelled?** The handoff draws
  `YOU / TIES / THEM`; every design doc says Player One and Player Two.
- **How does a player tell apart two open games that are both called ItSaMeMaRiO?** That's
  the default name, so it's the ordinary case, and a row carrying only the name gives them
  nothing to go on.
- **Should swiping one row open close another row that is already revealed**, or can two
  sit open at once?
- **What is the design cue that tells a player the row slides left to delete?** The row has
  to signal it visually rather than leaving the gesture to be guessed, and help text is the
  bare minimum rather than the answer. Nothing settles what the cue actually is.
- **What should happen when a player opens a game that is no longer there**, or that can't
  be read back? Going quietly back to the main menu tells them nothing about why, and an
  error surface would need copy and a control that nothing specifies.
- **What does the open-games list say for one game, or none?** "1 games on the go" is
  wrong, and the footer the handoff draws states behaviour this doc rejects, so its
  replacement is unwritten too.
