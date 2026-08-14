**Build-readiness: 76** — round-7 grade as corrected; round-8 changes await re-grade. Two
things changed: requirement 29 no longer depends on the row learning that **No** was tapped —
which under requirement 28's host was unimplementable and untestable — and requirement 30 now
fires **both** feedback channels, closing the largest hole in `SoundMoment.buttonTap`'s
coverage.

# PRD: Open Games List and the New Game Name Prompt

> **Status:** Draft · Source docs read: `Menus and UI.md`, `Game Overview.md`, `Rules.md`,
> `Theming.md`, `Game Board Design.md`, `Tech Design.md`, `Animations.md`, `roadmap.md`, and
> the read-only reference asset `design_handoff_game_ui/` (screens `1b — Select Game` and
> `2c — New Game, opponent name prompt`). `Alternative Game Styles.md` is a declared
> parking-lot doc and was not sourced from.

> **Wave:** P4 · **Depends on:**
> `P1-01-app-scaffold.md` (`lib/ui/menus/`, the `ProviderScope`, the no-codegen Riverpod
> idiom, and its **req 14** exhaustive dependency list), `P1-02-engine-rules.md` (`Board`, and
> **req 32's `Board.newSeries()`**), `P1-03-theme-system.md` (**req 15**'s slot schema at
> **v8** — every key requirement 17 names now exists, including `icons.trash` and
> `surfaces.destructive`), `P1-04-persistence.md` (**reqs 21** `OpenGamesRepository` and
> `StoredGame` — **which now carries `createdAt` and `updatedAt`**, **22** `GameId`, **25**
> `CreateGameResult`, **10** the create-time cap check, **17** `delete`, **28** the providers
> this screen reads, **29** the `updatedAt`-ordered, most-recent-first `readAll()`),
> `P1-07-entitlements.md` (**req 3**, via `entitlementsProvider` →
> `Entitlements.openGameCap`), `P2-01-navigation.md` (**reqs 1, 2, 3, 7, 11, 12**, plus the
> two additions requirement 28 asks it for), `P2-02-audio.md` (**req 6**'s
> `audioLayerProvider` → `play(SoundMoment.buttonTap)` — requirement 30), `P2-03-haptics.md`
> (**req 14**'s `hapticServiceProvider` → `HapticService.validAction()` — requirement 30), and
> `P4-01-main-menu.md` (the Play Game button — same wave, parallel-safe). Hands off to
> `P3-01-board-rendering.md`.

> **Reading order for an implementer:** requirements **21–30** fix the file, the widget
> classes, the providers, the data source, the call sites, the copy, the async states, the
> modal surface **and its host**, the revealed-row lifecycle and the two feedback channels.
> Everything numbered 1–20 codes against them.

## Build it — what is decided, and what is a default that may move

Every requirement here is buildable today. Two kinds of statement appear, marked at each one:

- **Settled** — traceable to a Decision in a design doc, to a settlement the user has made, or
  to a published interface in a sibling PRD. Do not deviate.
- **Fenced default** — a build-level choice this PRD made so the work is not blocked, each with
  the open question it defers to and what it costs to reverse. Fences are in requirements 3, 4,
  11, 22, 26, 27, 28 and 29.

**Requirement 2's fence is gone, and so is its residual.** It fenced row order against the
absence of a sort key, and the user has since settled both halves: `StoredGame` carries a
timestamp (`P1-04` → Open Question 7) and the list sorts **most-recent-first on `updatedAt`**
(`P1-04` → Open Question 8). `P1-04` req 29 is now a fully settled ordering guarantee and this
screen cites it rather than fencing on it or flagging a residual. That leaves eight fences, of
which **six reverse inside one widget file and two do not.**

| Reverses in one file | Reverses across files, or needs another PRD's change |
|---|---|
| **3** pinned vs scrolling — a widget-tree move | **22** the `CapReached` branch — if Open Question 3 lands on the upsell, this PRD and `P4-05-purchase-flow.md` stop being parallel-safe inside wave 4 |
| **4** the interim row — now genuinely one file: the score chips were always one widget, and **the timestamp fields now exist** (`P1-04` req 21), so rendering one is a widget change rather than a wave-1 model change. What is still not this PRD's to decide is *whether* either is shown — Open Question 4a | **28** the modal's host — **three files across two owners**, and it changed what requirement 29 could assert. See requirement 28 |
| **11** name normalization — the field's configuration | |
| **26** load and empty states — one widget or one call | |
| **27** the modal's sentence — one string | |
| **29** the revealed-row lifecycle — the row widget alone | |

**The lesson the 76 taught, recorded so it is not repeated:** a reversal cost measured only in
*files this PRD owns* is incomplete. Requirement 28's host change touched no model and no
storage, but it removed the ability of a *different* requirement to observe an outcome — and an
assertion that cannot be written is worse than one that is missing, because a red test leaves
nobody able to tell whether the code or the spec is wrong.
**The timestamp is the counter-example worth keeping beside it:** requirement 4's cost was
correctly reported as *not one file* precisely because it needed a wave-1 model change, and the
answer to that question is what made it one file. The reporting was right both times.

**Two strings still do not exist** (Open Question 14). Neither blocks the screen: the footer is
simply not shipped, and the `CapReached` branch renders the numbers it is handed
(requirement 22) whatever the final wording turns out to be.

## What is settled since the round-5 grade

- **`icons.trash` exists** — `P1-03` req 15's icon set, added as **required (authored)** rather
  than transcribed, because `1b` predates the delete decision. Requirement 17 binds it.
- **`surfaces.destructive` is reshaped and bound**: `action.{fill,radius}` is the panel a swipe
  reveals, `confirmAccept.{fill,labelStyle,border,radius}` is the modal's **Yes**.
- **The modal needs no new surface keys**, confirmed by `P1-03`, whose `surfaces.modal` row now
  reads *"reused by the delete confirmation"*.
- **Spacing and padding are not themed at all** — every spacing key was removed in v7
  (`Theming.md` → Decisions → *Does a theme control spacing and padding?*).
- **Non-board controls make a sound** — one tap sound everywhere (`Theming.md` → Decisions →
  *Do non-board controls make a sound?*). Requirement 30 carries both channels.
- **`StoredGame` carries a timestamp** — the user answered `P1-04` → Open Question 7 **yes**,
  which was the same question as this PRD's Open Question 4c. Requirements 2 and 4 change with
  it; Open Question 6 is closed; Open Question 4a — whether the *row shows* it — is not.
- **The record carries two dates, and the order is settled** — the user has since answered
  `P1-04` → Open Question 8: `StoredGame` carries **both `createdAt` and `updatedAt`**, and
  `readAll()` returns **most-recent-first on `updatedAt`**. Requirement 2 no longer carries a
  residual, and requirement 4's fence now covers *two* candidate dates rather than one.

## Problem

Play Game is the only way into a game, and today it has nowhere to go. A player with games
already on the go has no way to see them, choose between them, or delete one to free a slot,
and no way to say who they are playing before starting a new one — so the saved series the app
keeps (`Menus and UI.md` → Decisions → How many open games do we keep?) are unreachable, and an
open game has no title to be listed under. The docs settle that Play Game branches on whether
open games exist, that the list is titled by opponent name, that a swipe reveals a trash button
whose modal confirms before anything is destroyed, and that New Game asks for that name; none
of it exists.

## Goal

Tapping **Play Game** with no open games drops the player straight into a new two-player
pass-and-play game with no list screen in between; tapping it with open games shows a screen
listing every open game, each titled with its opponent's name, with **New Game** at the top of
that list and a swipe-to-reveal trash button that confirms before freeing a slot. Picking an
open game resumes that whole series — its board and its running score — and picking New Game
prompts for the opponent's name, defaulted to **ItSaMeMaRiO**, before starting a fresh series
on the same phone.

## Requirements

### Entry — where Play Game takes you

1. **With zero open games, Play Game goes straight into a new game and the open-games list
   screen is not shown.**
   *Source: `Menus and UI.md` → Play Game → Where It Takes You ("No open games — straight into a
   new game, no intermediate screen"); → Decisions → Is the main menu button "New Game" or "Play
   Game"?*
   *Testable:* with no stored open games, tapping Play Game never renders
   `OpenGamesListScreen`.
   *Note:* whether the **name prompt** appears on this path is unresolved — Open Question 1.
   `P2-01` **req 7** holds the branch inside `playGame()`. This constrains **entry only**;
   arriving at zero rows by deleting the last game is requirement 26.

2. **With one or more open games, Play Game opens the list screen, and it renders every open
   game it is given:** none is hidden, truncated or paginated away.
   *Source: `Menus and UI.md` → Play Game → Where It Takes You ("Open games exist — a new screen
   listing all open games"); → Screens (so far) → 2. Open Games List.*
   *Testable:* seeded with 1, 2 and 3 stored games, the screen renders exactly that many game
   rows.
   *Derived, not cited:* the list **scrolls**. No design doc says so; it follows from
   requirement 6's cap of 100 against the handoff's 402×874 frame.
   **Row order is guaranteed by the provider, and this screen adds none of its own.**
   `P1-04` **req 29** returns a **stable order sorted most-recent-first on the `updatedAt`
   field `StoredGame` carries** — the user settled the field's existence (`P1-04` → Open
   Question 7) and then the comparator itself (`P1-04` → Open Question 8), which is what turned
   that requirement from *"`readAll()` carries no ordering guarantee"* into a settled
   guarantee. This screen renders rows in the order the list provider yields, performs no sort,
   and does not reorder after a write. The silent-reshuffle failure this requirement used to
   fence against — Hive box-iteration order being unstable across compaction — is gone at the
   source rather than papered over here.
   *No residual.* An earlier draft flagged the **sort direction** as `P1-04`'s proposal rather
   than a settlement. The user has confirmed it — most-recent-first — so there is nothing left
   held open, and nothing on this screen changes either way, because this screen does not sort.
   *Testable, for the ordering this screen must not disturb:* seeded with three stored games
   whose `updatedAt` values differ, the rendered row order is exactly the provider's order, and
   the row whose `updatedAt` is newest is rendered first.
   *Scoped to the normal state:* this requirement and requirement 6 assume the stored count is
   at or below the effective cap. The over-cap state is **Open Question 8**.

3. **New Game is an option at the top of that list**, above every open game row.
   *Source: `Menus and UI.md` → Play Game → Where It Takes You ("with **New Game** as an option
   at the **top of the list**"); `design_handoff_game_ui/` → *1b*.*
   *Testable:* New Game precedes all game rows in the rendered order at every list length.
   *Fenced default — pinned or scrolling:* it **scrolls with the list**, as the first item of the
   scrollable. *Reversal cost:* one file — a `Column` above the `ListView`, or a
   `SliverPersistentHeader`. No data, no call site — **Open Question 11**.

4. **Each open game row shows the opponent name as its title, and — this wave — nothing else but
   the chevron.**
   *Source: `Menus and UI.md` → Decisions → What does each row in the open-games list show?
   ("each open game is titled with the opponent's name"), which settles the title and nothing
   further.*
   *Testable, with the row in its **resting** state (requirement 29 defines the other):* a
   `StoredGame` with `opponentName: 'Dad'` renders a row whose title is exactly `Dad`; the row
   renders no date and no score chips; a tap resolves to requirement 5's call and a
   leftward swipe to requirement 29's reveal.
   *Fenced default — the interim row:* title (`surfaces.gameRow.titleStyle`) + chevron
   (`icons.chevronRight`), on `surfaces.gameRow.{fill,radius}` at `radius.row`.
   **`surfaces.gameRow.{timeStyle,chip,chipYouOutline}` are deliberately left unread this
   wave.** *Reversal cost — one file for both halves:* the chips are one widget file, since
   the score is already on `Board`; **rendering a date is now one widget file too**, because
   `P1-04` req 21's `StoredGame` carries **both `createdAt` and `updatedAt`** (the user settled
   Open Question 4c, then `P1-04` → Open Question 8). What still gates it is not a missing field
   but a product call — **Open Question 4a**, whether the row displays a date at all, **which
   of the two it is**, and the copy it would render, which nothing specifies.
   **This asks `P1-03` to move those three keys to `deferred`,** exactly as it holds
   `surfaces.scoreboard.turnBanner`: *"A required key with no reader would make Requirement 11's
   check assert a value nothing consumes — so it stays in the contract and out of the check
   until that decision lands."* **The ask is unchanged by the fields landing** — a stored field
   with no reader is still no reader, and two stored fields with no reader are still no reader.

   > **Why this row is fenced and requirement 23's counter is not.** Both are `required` keys
   > with this screen as their only consumer, so the naive rule — "a required key must be read"
   > — would force both. The distinction is what the handoff *draws* and whether the docs
   > *contest* it. The counter's content is drawn (`11/16`), uncontested, and needs no data the
   > model lacks, so it is built. The chips' content is contested — `1b` labels them
   > `YOU / TIES / THEM` while every design doc says Player One / Player Two (Open Question 4d)
   > — and the date, though it now has two fields behind it, has no settled answer to
   > *whether* it is shown, *which* date it is, or *how* it is worded. **Drawn and uncontested →
   > build it. Contested, or unsettled in product terms → leave the key unread and ask `P1-03`
   > to defer it.**

5. **Selecting an open game resumes that series, not just its last board** — the board picks up
   where it was left and the game's own running score (Player One / Ties / Player Two) comes
   back with it, rather than restarting at zero.
   *Source: `Menus and UI.md` → Decisions → What does an open game hold?; `Game Overview.md` →
   Decisions → Scoreboard lifetime.*
   **Call site:** tapping a row **in its resting state** calls
   `ref.read(appNavigatorProvider).openGame(row.id)` — signature `P2-01` **req 3**, transition
   its **req 12**. A tap while the row is revealed does something else; requirement 29.
   *Testable:* against a recording `AppNavigator` fake, tapping a resting row records exactly one
   `openGame` carrying that row's `GameId` and no other call. That the restored board and score
   are correct is `P1-04` req 6's test.

6. **The effective open-game cap is read from the entitlement layer:**
   `ref.watch(entitlementsProvider).openGameCap` — 3 without the unlock, 100 with it.
   *Source: `Menus and UI.md` → Decisions → How many open games do we keep?; `Tech Design.md` →
   Decisions → In-app purchases; the symbol is `P1-07` **req 3**.*
   *Testable — behavioural, not a scan:* with the entitlement stubbed absent, a create attempt at
   3 stored produces requirement 22's branch showing `cap` 3; with it present, three stored games
   create a fourth successfully. **The literal scan that used to sit here is dropped**: `P1-07`
   req 3's own testable already asserts that *"no other source in `lib/` defines either number"*.
   **Its one observable consequence this wave is requirement 22's `CapReached` branch.**
   Enforcement is create-time in `P1-04` req 10, and requirement 2 bars this screen from
   enforcing the cap by drawing fewer rows.

7. **Deleting an open game is four steps: swipe left → a trash button appears → tap it → a modal
   confirms.** Nothing is destroyed until **Yes** is tapped.
   *Source: `Menus and UI.md` → Decisions → **How does a player delete an open game?**, in the
   user's own words:*

   > *"It should be a slide left a trash button shows up, Click it, A modal pops up saying
   > permanently delete this game with Yes and No, On Yes delete the game, On no exit the
   > modal"*

   **The revealed control is a trash button — an icon, not a worded "Delete" label**, which the
   Decision states explicitly. The modal's buttons are **Yes and No**, not Cancel/Delete
   (requirement 27).
   **Why the confirmation is not decoration, in the Decision's own terms:** deleting a game is
   *"the only irreversible action in the app — it destroys the game and its whole running
   scoreboard"*, and kids are a stated target audience (`Game Overview.md` → Target Audience &
   Platform).
   **How it is drawn — settled, and the ownership split matters.** The swipe exposes a panel
   whose fill and corner are `surfaces.destructive.action.{fill,radius}`; the glyph on it is
   `icons.trash` with its own `tint` and `size`. **`icons.trash` deliberately carries no
   `button` sub-object** — unlike the five chrome icons, which sit on a screen's own background
   and own their button treatment. Here the panel is the surface and **the row's height sizes
   it**, so one control has exactly one surface owner. Do not wrap the glyph in a button that
   supplies its own fill or radius.
   **Call sites:** tapping the trash button closes the reveal (requirement 29) and calls
   requirement 28's `openDeleteConfirmation(row.id)`. **Yes** dismisses and deletes, in the order
   requirement 27 fixes. Every one of these gestures also fires both feedback channels
   (requirement 30). The row's `GameId` is requirement 19's.

   *Testable — five assertions. The first two exist to fail the implementations that collapse
   the Decision's steps:*
   - **The swipe reveals, and reveals only.** Swiping a row fully across and lifting the finger
     records **no** call on the notifier or the repository **and raises no modal**; the list
     still holds every game. **The trash button must be an independently activatable control** —
     hit-testable, and activating *it* is what raises the modal. This fails `Dismissible` with
     `confirmDismiss`, where the swipe crossing a threshold raises the dialog and the revealed
     panel is decorative paint: under that implementation the swipe alone raises something, so
     this assertion goes red. It also fails `Dismissible(onDismissed: delete)`, which records a
     call where this asserts none.
   - **No destroys nothing.** Tapping the trash button raises the modal; tapping **No** records
     no `delete` call, and the game is still present afterwards.
   - **Yes deletes exactly one game.** With three stored games all titled `ItSaMeMaRiO`
     (requirement 19's shape), tapping Yes on the second calls `delete` once with the second's
     `GameId`; the list rebuilds with the other two, both byte-identical; and a create that
     previously returned `CapReached` now returns `GameCreated`.
   - **The revealed control is an icon button.** It renders no text; the widget under test
     exposes an icon and no `Text` child, and its fill and radius resolve from
     `surfaces.destructive.action` rather than from any wrapper of its own.
   - **Order is untouched.** Deleting removes one row and this screen reorders nothing — the
     survivors come back in the order `P1-04` req 29's most-recent-first `updatedAt` sort
     yields, which is the same relative order they were in. See requirement 2.

   *Considered and rejected:* automatically **replacing the oldest** open game, as drawn in
   `1b`'s footer. That footer is stale and is not authoritative; its replacement copy is
   unwritten (requirement 24).

### The New Game name prompt

> The prompt's three screen changes belong to `P2-01` **requirement 11**, which names them
> `openNewGamePrompt()`, `openGame(id)` and `dismissCurrent()` in its **requirement 3**.
> Requirements 8–12 specify the prompt's **contents and effects** and invoke those operations.
> Per `P2-01` req 11 the prompt **reports its outcome by calling forward, not by returning a
> value** — it is not a `Future<String?>` and not a `showDialog`.

8. **The New Game control calls `openNewGamePrompt()`, and the prompt renders exactly this
   copy:**

   | Element | Verbatim copy | Slot | Fidelity |
   |---|---|---|---|
   | Title | `Who are you playing?` | `surfaces.sheet.header.titleStyle` | exact — 20/600 |
   | Sub | `Just a name for the list — on the board you're still Player One and Player Two.` | `surfaces.sheet.header.subStyle` | `2c` draws 12.5. Requirement 20 |
   | Field label | `Opponent` | `surfaces.input.labelStyle` | exact |
   | Helper | `Leave it as is if you can't be bothered.` | `surfaces.input.labelStyle` | no distinct helper key exists; requirement 20 |
   | Secondary action | `Cancel` | `surfaces.button.secondary` | exact |
   | Primary action | `Start playing` | `surfaces.button.primary` | exact |

   **The `→ type.scale.*` notation is corrected, not merely tidied.** The two header rows
   previously read `surfaces.sheet.header.titleStyle` **→** `type.scale.sheetTitle`, which
   asserted that a `*Style` key *dereferences* a style name. **It does not.** The user has
   settled that a `*Style` key under `surfaces.*` is an **inline object carrying its own
   colour** — normative in `P1-03` req 15 → `surfaces`, **schema v10**, where these two keys
   are declared `textStyle`. So `titleStyle` holds `{size, weight, color, …}` directly; there
   is no arrow and no lookup.
   `type.scale.sheetTitle` and `.sheetSub` still exist as the published type ramp and are
   where these numbers were **drawn from**, which is why they are still worth naming — but
   that is provenance, not a runtime reference. Slot columns elsewhere in this PRD name a key
   a widget reads, and these two now do the same.
   **What this changes about the two fidelity notes.** The title's 20/600 is unaffected. The
   sub's *"mismatch — `sheetSub` is 11.5, `2c` draws 12.5"* was a mismatch **only under the
   dereference reading**: two independent objects cannot disagree, so `subStyle.size` can
   simply be 12.5 while `type.scale.sheetSub` stays 11.5 for its own consumers. **Requirement
   20 still carries that row and this PRD does not resolve it here** — whether the two
   *should* agree is a fidelity question for `P1-03`'s transcription pass, and it is now a
   choice rather than a conflict.
   *Source: `Menus and UI.md` → Play Game → Where It Takes You; → Screens (so far) → 3; the
   strings are `design_handoff_game_ui/` → *2c*, quoted verbatim because copy an implementer
   invents is invisible to every test that does not name it.*
   *Vocabulary check:* the sub already says *"on the board"*, which is what `Game Overview.md` →
   Decisions → *Player-facing vocabulary* requires; no string in this table, requirement 24 or
   requirement 27 uses "quadrant". That Decision settled the big-board/small-board word only; it
   did **not** settle what the row's score chips are labelled (Open Question 4d).
   *Testable:* activating New Game records exactly one `openNewGamePrompt()` and creates no game;
   the rendered prompt contains all six strings character for character.

9. **The field is pre-filled with `ItSaMeMaRiO` and the text is selected**, so typing replaces
   it.
   *Source: `Menus and UI.md` → Play Game → Where It Takes You; `design_handoff_game_ui/` →
   *2c*.*
   *Testable:* on open, the controller's text is `ItSaMeMaRiO` and its selection spans the whole
   value; confirming without editing creates a game titled `ItSaMeMaRiO`.

10. **Confirming creates exactly one open game and then opens it.** The call is
    `ref.read(openGamesListProvider.notifier).create(opponentName: <normalized name>, board:
    Board.newSeries())` (`P1-04` **req 28**); on `GameCreated` the screen calls
    `openGame(result.game.id)` (`P2-01` **req 11**). The name titles the game in the list and is
    used nowhere else.
    *Source: `Menus and UI.md` → Decisions → Does the opponent name replace "Player Two" in
    game?; `Game Overview.md` → Decisions → Player names.*
    **Who supplies the `Board`:** this screen, as `Board.newSeries()` — `P1-02` **req 32** (81
    cells empty, `score` 0/0/0, `firstPlayerThisGame == Player.one`,
    `currentPlayer == Player.one`), matching `Rules.md` → Turn Order Across Games. Requirement 14
    disclaims only who goes first in a **rematch** (`P1-02` req 34).
    **Who supplies the dates:** the repository, on `create` — `P1-04` req 21 makes `createdAt`
    and `updatedAt` both `StoredGame`'s fields, and its req 25's testable asserts a created
    record has both set (and, on a fresh create, equal to each other). This screen passes a name
    and a board and nothing else; the two-argument call is unchanged.
    *Testable:* confirming with `Jules` calls the notifier's `create` once with
    `opponentName: 'Jules'` and a board equal to `Board.newSeries()`; on `GameCreated` it records
    exactly one `openGame(result.game.id)`. The `CapReached` branch is requirement 22.

11. **An empty name falls back to `ItSaMeMaRiO` rather than blocking, and the field accepts at
    most 16 characters.**
    *Source: `design_handoff_game_ui/` → *2c*. The `.md` docs restate neither rule.*
    *Testable:* clearing the field and confirming calls `create` with
    `opponentName: 'ItSaMeMaRiO'`; a 17th character cannot be entered.
    *Fenced default — normalization:* input is **trimmed**; a **whitespace-only** entry is
    therefore empty and takes the default; "16 characters" counts **UTF-16 code units**, matching
    Flutter's `maxLength`; an **over-limit paste truncates**. *Reversal cost:* one file — the
    field's configuration — **Open Question 10**.

12. **Cancelling creates nothing** — no repository call, no change to the stored count — and
    calls `dismissCurrent()`.
    *Testable:* cancelling records exactly one `dismissCurrent()` and no `openGame`; no `create`
    reaches the notifier fake; the list is unchanged.

### What a new game starts

13. **A new game is a two-player game on the same phone.** For this screen: the create path takes
    no opponent-type, difficulty or player-count argument, and produces one artifact — a
    `StoredGame` whose board is `Board.newSeries()`.
    *Source: `Menus and UI.md` → A New Game → What It Starts; `Game Overview.md` → Modes.*
    *Testable:* the only `create` call this screen makes is requirement 10's two-argument one; a
    scan of these files finds no mode, AI, difficulty or player-count symbol.

14. **Turn order alternates Player One → Player Two, and the active player switches automatically
    after each move.**
    *Source: `Menus and UI.md` → A New Game → What It Starts; → Pass-and-Play Turn Handoff.*
    Alternation is `P1-02` req 33; the indicator is `P3-03-scoreboard-turn-indicator.md`'s;
    rematch order is `P1-02` req 34. This screen's only stake is that the board it hands over
    starts with Player One.

15. **There is no "pass the phone, don't peek" screen between turns — the handoff is instant.**
    *Source: `Menus and UI.md` → Pass-and-Play Turn Handoff.*
    *Testable, as a constraint on this screen:* the confirm sequence is `create` → `openGame` with
    no third surface, and these files contain no handoff or ready-check widget.

16. **No AI opponent and no online play in this version.**
    *Source: `Menus and UI.md` → A New Game → What It Starts; `Game Overview.md` → Decisions →
    Single-player / AI opponent.*
    *Testable:* covered by requirement 13's scan.

### Presentation

17. **Every value this screen draws resolves to a `P1-03` req 15 key path — v8, where all of them
    now exist.** No colour, size, radius, font, **duration** or icon literal is written into this
    screen's code.
    *Source: `Theming.md` → Architectural Rule.*

    | What it draws | Key path | Read this wave? |
    |---|---|---|
    | Game row card and title | `surfaces.gameRow.{fill,radius,titleStyle}`, `radius.row` | yes |
    | Row date and score chips | `surfaces.gameRow.{timeStyle,chip,chipYouOutline}` | **no — requirement 4's fence; asked to be `deferred`** |
    | Row chevron | `surfaces.gameRow.chevron` / `icons.chevronRight` | yes |
    | Revealed panel behind the trash glyph | `surfaces.destructive.action.{fill,radius}` | yes |
    | Trash glyph | `icons.trash.{kind,set,name,path,tint,size}` — **no `button` sub-object; the row's height sizes the panel** | yes |
    | Modal's **Yes** | `surfaces.destructive.confirmAccept.{fill,labelStyle,border,radius}` | yes |
    | Modal's **No** | `surfaces.button.secondary` | yes |
    | Modal card and scrim | `surfaces.modal.{fill,border,radius,shadow}`, `surfaces.scrim.modal` | yes — requirement 27 |
    | Prompt sheet | `surfaces.sheet.{fill,radius}`, `surfaces.sheet.header.{titleStyle,subStyle,closeControl}` | yes |
    | Prompt scrim | `surfaces.scrim.namePrompt` | yes |
    | Name field and counter | `surfaces.input.{fill,radius,focusBorder,caret,valueStyle,labelStyle,counterStyle}` | yes |
    | Cancel / Start playing | `surfaces.button.{primary,secondary}` | yes |
    | `+`, back and chevron glyphs | `icons.{plus,chevronLeft,chevronRight}` with `icons.<slot>.button.{fill,radius,size}` | yes |
    | Type | `type.scale.{subhead,label,sheetTitle,rowTitle}` | yes — see requirement 20 |

    **The sound this screen plays is not in this table**, because it is not a value this screen
    reads: requirement 30 names a `SoundMoment` and the audio layer resolves the theme's slot
    behind it (`P2-02` req 6). This screen reads no `sound` key and no `Theme.sound` path.
    **Spacing and padding are not in this table because they are not themed.** `P1-03` removed
    every spacing key in v7 — *"Spacing and padding are fixed in code, not themed, because the
    guard cannot catch a hardcoded gap"* (`Theming.md` → Decisions → *Does a theme control
    spacing and padding?*). Gaps, insets and row padding on this screen are written in code and
    are **not** guard violations. The rule for classifying a new value, in that PRD's words: a
    theme controls *"the drawn geometry of a thing itself"*; code controls *"where things sit
    relative to one another."*
    *Testable:* `P1-05-theme-guard-test.md`'s scan passes over these files with the baseline at
    zero, and every key marked "yes" resolves in Neon's materialized theme.

18. **The screen matches `1b` and the prompt matches `2c`,** recreated in Flutter, not ported from
    the HTML prototypes — **except where requirement 20 records that no key carries the drawn
    value, except for the row content requirement 4 defers, and except for the trash button and
    modal, which `1b` does not draw at all** and whose values `P1-03` therefore **authored**
    rather than transcribed.
    *Source: `design_handoff_game_ui/` → README.*
    *Testable:* every copy string in requirements 8, 24 and 27 renders character for character;
    each element marked "yes" in requirement 17 reads its named key and no literal; the prompt
    renders over a still-mounted list (`P2-01` req 2's child route).
    **Where fidelity and requirement 17 conflict, requirement 17 wins and requirement 20 records
    the debt.** Rendering the theme's value is off by 1–2pt from the drawing, and writing
    `fontSize: 22` trips `P1-05` req 6's **`font-size-literal`** rule
    (`r'fontSize\s*:\s*[\d.]+'`) against a baseline its req 8 keeps at zero.

### The screen's interfaces, added by rounds 3–8 of review

> Numbered after 18 so cross-references other PRDs already hold into this one — `P1-03` req 15
> cites requirements 4, 7, 8, 9, 12, 17 and 18; `P1-04` reqs 22, 25 and 28 cite requirements 19,
> 21 and 25; `P2-01` reqs 11–13 cite requirements 5, 8, 10, 12 and 19; `P2-02` req 6 and
> `P2-03` req 1 both cite requirement 30 — keep pointing at the text they were written against.

19. **Every row carries the `GameId` of its open game, and resume and delete act on it. The
    opponent name is a title and is never a key.**
    `GameId` is fully specified: `P1-04` **req 22** — a `final class` over a store-minted **UUID
    v4**, opaque, stable for life, never reused after a delete. Settled, not pending: `P1-04` →
    Open Question **6a**.
    *Testable:* with three stored games all titled `ItSaMeMaRiO`, deleting the second calls
    `delete` with the second's id and leaves the other two byte-identical; selecting the third
    records `openGame` with the third's id.
    *Still open, and only this half:* whether any part of a game's identity is ever shown to the
    player — `P1-04` → Open Question **6b**, carried here as Open Question 9. **The modal does not
    depend on it:** the settled copy says *"this game"*, not the opponent name (requirement 27).
    *Note, since the fields now exist:* `StoredGame` carries two dates — `createdAt` and
    `updatedAt` — either of which would serve that question if the answer is a date. Showing one
    is Open Question 4a's, not this requirement's, and the id stays opaque either way.

20. **Values this screen draws that still have no key in `P1-03` req 15's schema.** Each is a
    request to that PRD.

    | Drawn value | Where | Nearest existing key | Why it does not serve |
    |---|---|---|---|
    | Underlay dim **30%** | `2c`, list behind the sheet | `surfaces.menu.dimBehindOverlay` | that is `2a`'s **35%**, a different surface |
    | Sheet sub at **12.5** | `2c` | `type.scale.sheetSub` = **11.5** | `sheetSub` came from `2a`'s 11.5 sub |
    | **Modal title style** | requirement 27 | none | `surfaces.modal.*` carries fill, border, radius and shadow — no type. **`P3-04-game-over-rematch.md` already routes "result title type (28/600)" to `P1-03`; these two should arrive together** |
    | **Text colours** for every string | `1b`, `2c`, requirement 27 | none — `type.scale.<style>` carries size, weight, tracking and line-height only | the dangerous one: an agent reaches for `color.text`, which is not a literal, so `P1-05` passes green while `P1-03` Appendix A.1's rule — *"a component reads its own `surfaces.*` or `icons.*` key, never a `color.*` key that happens to look right"* — breaks silently |
    | The `CapReached` message | requirement 22 | none | no key styles it, and no copy exists |
    | Helper-text style | `2c` | `surfaces.input.labelStyle` | label and helper are drawn differently; one key serves both |
    | `+ NEW GAME` row outline and type | `1b` — accent-outlined, 17pt | `surfaces.button.primary` (`1a`: 20pt) | neither button tier matches. *(Its padding is no longer part of this mismatch — padding is code's.)* |

    *Resolving exactly, recorded so they are not re-raised:* `1b`'s heading 22/600 →
    `type.scale.subhead`; `1b`'s sub 12 → `type.scale.label`; the back control →
    `icons.chevronLeft` at `radius.control`.

21. **The screen is three widgets in `lib/ui/menus/`, reached only through providers.** Class
    names and routes for the first two are `P2-01` **req 2**'s route table and are not this PRD's
    to rename; the third is requirement 28's, provisionally named here.

    ```dart
    // lib/ui/menus/open_games_list_screen.dart   -> route '/games'      (P2-01 req 2)
    class OpenGamesListScreen extends ConsumerWidget { … }

    // lib/ui/menus/new_game_prompt.dart          -> route '/games/new'  (P2-01 req 2)
    class NewGamePrompt extends ConsumerStatefulWidget { … }  // holds the TextEditingController

    // lib/ui/menus/delete_game_confirmation.dart -> requirement 28's route
    class DeleteGameConfirmation extends ConsumerWidget { … }  // takes the GameId
    ```

    | Symbol | Declared by | Used for |
    |---|---|---|
    | `appNavigatorProvider` → `AppNavigator` | `P2-01` reqs 3, 4 | `openNewGamePrompt()`, `openGame(id)`, `dismissCurrent()`, `leaveOpenGamesList()`, `openDeleteConfirmation(id)` |
    | `openGamesListProvider` → `AsyncValue<List<StoredGame>>` | `P1-04` **req 28** | `watch` for the rows |
    | `openGamesListProvider.notifier` → `OpenGamesNotifier` | `P1-04` **req 28** | `create(...)` (requirement 10) and `delete(id)` (requirement 7) |
    | `entitlementsProvider` → `Entitlements` | `P1-07` reqs 3, 11 | `openGameCap` (requirement 6) |
    | `hapticServiceProvider` → `HapticService` | `P2-03` **req 14** | `validAction()` (requirement 30) |
    | `audioLayerProvider` → `AudioLayer` | `P2-02` **req 6** | `play(SoundMoment.buttonTap)` (requirement 30) |

    **Writes go through the notifier, not the repository provider** — `P1-04` req 28:
    *"`openGamesListProvider` for the rows and for any write that should be visible in the
    list."* This screen reads `openGamesRepositoryProvider` directly nowhere.
    **Where the revealed-row state lives, stated because it was previously implied and wrong.**
    Each row widget owns whether it is revealed, and **nothing above the rows tracks which row is
    open** — there is no screen-level field and no `lib/ui/` provider. That is only consistent
    because requirement 29 no longer claims single-row exclusivity: exclusivity needs a
    coordination point above the rows, and every available home is closed — screen state
    contradicts the `ConsumerWidget` above, a `lib/ui/` provider is what requirement 25 calls
    *"the failure this requirement existed to prevent"*, and a package group-controller is not in
    `P1-01` req 14's exhaustive dependency list. **If exclusivity is wanted (Open Question 20),
    one of those three has to be opened first**, and this line changes with it.
    *Testable:* a widget test overriding these providers with fakes drives every path in this PRD
    with no Hive, no StoreKit, no real router, no platform channel and no audio device; a scan
    finds no `Navigator.`, no route string and no dialog-opening call in these files.

22. **Confirming switches on `CreateGameResult`, and the `CapReached` branch is never a silent
    no-op.**
    `create` returns `GameCreated(StoredGame game)` or
    `CapReached({required int cap, required int stored})` — `P1-04` **req 25**. A `CapReached`
    deliberately does not invalidate the list (`P1-04` req 28) — nothing changed.
    *Testable:* with the notifier fake at the ceiling, confirming produces an observable change —
    the prompt stays up, a message naming `cap` and `stored` renders, and no `openGame` is
    recorded. A test exercising only `GameCreated` does not satisfy this.
    *Why its own requirement:* the cheap implementation of requirement 10 is
    `if (result is GameCreated) openGame(...)` with no `else`, which lets a player at the cap tap
    **Start playing** and watch nothing happen, with every test green.
    *Fenced default — what the branch shows:* the prompt stays open and renders one line naming
    the two numbers. **The wording is not fixed here** — Open Question 3. *Reversal cost:* **not
    one file** — one string if the answer is a refusal, but if it is the upsell this PRD and
    `P4-05-purchase-flow.md` stop being parallel-safe inside wave 4.

23. **The field renders a live character counter.**
    `2c` draws `11/16`, and `P1-03` req 15 marks `surfaces.input.counterStyle` **required** with
    this screen as its only consumer.
    *Testable:* with `ItSaMeMaRiO` in the field the counter reads `11/16`; typing updates it on
    the same frame; its style resolves from `surfaces.input.counterStyle`.

24. **The list screen renders this copy.**

    | Element | Verbatim copy | Slot |
    |---|---|---|
    | Heading | `Pick up where you left off` | `type.scale.subhead` — 22/600, exact |
    | Sub | `<n> games on the go · scores are saved` | `type.scale.label` — 12/400, exact |

    *Source: `design_handoff_game_ui/` → *1b*.*
    *Testable:* with two stored games the sub reads `2 games on the go · scores are saved`.
    *Unwritten, and named so it is not invented:* `1 games` is wrong and no pluralization is
    chosen; `0 games` renders during the load state and permanently after the last delete; and
    `1b`'s footer states behavior requirement 7 rejects and has no replacement — ship no footer
    until Open Question 3 lands. All three are Open Question 14, and none blocks the screen.
    *Noted, not acted on:* the heading was the evidence `P1-04` req 29 cited when it *proposed*
    most-recent-first. The user has since settled that direction (`P1-04` → Open Question 8), so
    the heading is corroboration rather than the basis. This copy is transcribed and does not
    change either way.

25. **The list's data source is `openGamesListProvider`, and refresh is structural.**
    `P1-04` **req 28** declares it as an
    `AsyncNotifierProvider<OpenGamesNotifier, List<StoredGame>>` whose `build()` delegates to
    `readAll()`, with `create`, `save` and `delete` on the notifier calling `invalidateSelf()`.
    *Testable:* after `openGamesListProvider.notifier.delete(id)` completes, the screen rebuilds
    with one fewer row and no navigation round trip; after a `CapReached`, it does not rebuild.
    *Recorded, because this began as an unanswered ask:* an earlier draft marked this provider
    **"Declared by: nobody"**. `P1-04` req 28 answers it. **Nothing here improvises a provider in
    `lib/ui/`** — that is the failure this requirement exists to prevent, and requirements 28 and
    21 are where it would otherwise recur.

26. **Two async states the screen must render, neither of them drawn.**
    - **While the list is loading** (`AsyncValue.loading`), the screen renders its header chrome
      and no rows. *Fenced default:* no spinner — there is no theme key for one, and the read is a
      local Hive box. `P2-01` req 8 sets the precedent: *"while the read is in flight the main
      menu stays on screen. No spinner, no intermediate surface and no blank frame is specified
      here."*
    - **When the last game is deleted**, the screen stays on `/games` showing New Game alone.
      Requirement 1 forbids the list *on entry* at zero and says nothing about arriving there.
    *Testable:* with a fake whose read never completes, the screen renders the heading and zero
    rows and does not throw; deleting the only game leaves `OpenGamesListScreen` on display with
    New Game present, zero game rows, and no navigation call recorded.
    *Reversal cost:* one file — **Open Question 13**.

27. **The delete modal: settled copy, settled order, modal surface, no new surface keys.**

    | Element | Copy | Slot |
    |---|---|---|
    | Message | *Fenced —* `Permanently delete this game?` | `surfaces.modal.*` + a title style with no key (requirement 20) |
    | Accept | `Yes` | `surfaces.destructive.confirmAccept.{fill,labelStyle,border,radius}` |
    | Dismiss | `No` | `surfaces.button.secondary` |

    **`Yes` and `No` are settled, verbatim** — the Decision states them and says outright they
    are *"not Cancel/Delete"*. They are not paraphrasable.
    **What each button does, in order.** **No** calls `dismissCurrent()` and nothing else.
    **Yes** calls `dismissCurrent()` **first**, then
    `ref.read(openGamesListProvider.notifier).delete(id)`. The order is deliberate: this modal is
    a route parameterised by a `GameId` (requirement 28), so deleting first would leave the
    surface mounted for a frame over an id that no longer exists. Dismissing first also removes
    the failure an implementer would otherwise reach by building Yes as delete-only — the app
    parked on the confirmation route with nothing behind it.
    *Testable:* after Yes, exactly one `dismissCurrent()` and one `delete` are recorded in that
    order, and the confirmation is no longer mounted; after No, exactly one `dismissCurrent()`
    and zero `delete` calls.
    *Not specified, and not invented here:* what happens if `delete` fails. No design doc and no
    sibling PRD describes a failure path for it, and this PRD does not add one.
    *Fenced default — the exact sentence.* The Decision gives the substance in the user's words
    (*"A modal pops up saying permanently delete this game with Yes and No"*) rather than a
    finished string; `Permanently delete this game?` is that phrase as a question. **The word
    "permanently" is the user's and carries the irreversibility.** The phrasing says *"this
    game"*, not the opponent name, which keeps the modal unambiguous when three rows read
    `ItSaMeMaRiO`. *Reversal cost:* one string — **Open Question 18**.
    **Surface — confirmed, no new key.** `surfaces.modal.{fill,border,radius,shadow}` over
    `surfaces.scrim.modal`, the pair `P3-04-game-over-rematch.md` reqs 10 and 13 use. `P1-03` v8
    ratified this from its side. Only its **title type** has no key — requirement 20.

28. **The modal is raised through the navigation layer, as a child route of `/games`.** This is a
    **fenced default, and it is the build instruction** — not a question waiting on an answer.

    *Build this:* a child route of `/games` — provisionally `/games/confirm-delete` — whose
    widget is `DeleteGameConfirmation` (requirement 21), opened by

    ```dart
    Future<void> openDeleteConfirmation(GameId id);   // provisional, like the route
    ```

    on `AppNavigator`, and closed by `dismissCurrent()`. The screen calls the operation; it does
    not push, name a route, or open a dialog itself. **Both the operation name and the path are
    provisional and `P2-01`'s to ratify** — the shape is what matters: one operation, carrying a
    `GameId`, returning `Future<void>` like every other (`P2-01` req 3).

    **Why this shape, and not one of the other three.**

    | Mechanism | Status |
    |---|---|
    | `showDialog` / `showModalBottomSheet` | **banned** — `P2-01` req 1's scan, outside `lib/navigation/` |
    | `showGeneralDialog` / `showAdaptiveDialog` | **worse** — neither contains the substring `showDialog`, so both pass today's scan while defeating its intent. Do not use them; see ask 2 |
    | Local widget state (`ConsumerStatefulWidget`, or a `StateProvider<GameId?>` in `lib/ui/`) | **forbidden here** — requirement 21 declares the list a `ConsumerWidget` holding no local state, and requirement 25 records an improvised provider in `lib/ui/` as *"the failure this requirement existed to prevent"* |

    **The precedent is inside this same feature:** the name prompt is a transient surface over
    the list, and `P2-01` req 2 makes it the child route `/games/new` with `openNewGamePrompt()`
    and `dismissCurrent()` (its req 11).

    **What this host costs, stated accurately after an earlier draft understated it.** Reversal
    is **three files across two owners** — the route entry and operation in `lib/navigation/`,
    the call site here, and `DeleteGameConfirmation` itself. More importantly: **`P2-01` req 3
    fixes that no operation returns a result to its caller**, and `go_router` is banned outside
    `lib/navigation/`, so **the row cannot observe what the modal did.** An earlier draft of
    requirement 29 relied on the row learning that No was tapped; under this host that is not
    implementable, and its testable could not have been written. Requirement 29 now removes the
    dependency by ordering rather than by adding a channel. **A host is not only a routing
    choice — it decides what other requirements can assert.**

    **Two asks still routed to `P2-01` — Open Question 16.** They upgrade this from a fence to a
    citation; they do not gate the build.
    1. **Ratify the route and the operation** — a `Routes` entry under `/games`, the signature
       above, and `DeleteGameConfirmation` in its req 2 route table, as it already does for
       `NewGamePrompt`. The id must travel with it, the way `/game/:gameId` does.
    2. **Extend req 1's escape scan to `showGeneralDialog` and `showAdaptiveDialog`** — and any
       other `show*Dialog` entry point. Today the scan names `Navigator.`,
       `GlobalKey<NavigatorState>`, `showDialog` and `showModalBottomSheet`. **This one matters
       whichever host is chosen** — it is a hole in another PRD's guard, not a consequence of
       this fence.

29. **The revealed row has two states, and the reveal is gone before the modal opens.**
    Requirement 4's testable describes the resting state; this describes the other.

    - A swipe past the reveal threshold **stays open when the finger lifts** — it does not spring
      back, because the Decision requires the player to *tap* the revealed trash button
      (requirement 7), and a reveal that collapses on lift cannot be tapped.
    - **Tapping the trash button closes the reveal, and then the modal opens.** The row is
      already resting by the time the confirmation is on screen, so **nothing downstream of the
      modal has to reach back into the row** — which is what makes this implementable under
      requirement 28's host, where operations return `Future<void>` and the row cannot observe
      the outcome. This ordering is **this PRD's choice**, not a Decision: no design doc
      describes the reveal at all. It was made because the alternative — the reveal persisting
      until No is tapped — has no implementation path.
    - The reveal otherwise closes on swiping it back, and on **a tap on the row body, which
      closes the reveal and does not call `openGame`.** Closing is safer next to a destructive
      control, though it means a tap that would resume a game silently does not; it is the
      standard iOS behaviour, which is the only reason to prefer it.
    - **The reveal is instant — no animation, no `Duration`.** Requirement 17 bans a duration
      literal and `P1-05` keeps the baseline at zero, so an animated reveal would need a theme
      key that does not exist. `Animations.md` → Scope For Now also excludes transitions.
    - **Single-row exclusivity is not required this wave.** Two rows may be revealed at once.
      Requiring otherwise needs a coordination point above the rows, and requirement 21 records
      that all three possible homes are currently closed — see **Open Question 20**, which is a
      product call.

    *Testable:* after a completed swipe the trash button is present and hit-testable in a later
    frame; tapping it leaves the row resting **and** records one `openDeleteConfirmation`;
    tapping the revealed row's body records **no** `openGame` call and leaves the row resting;
    the reveal completes within one frame with no `Duration` anywhere in these files.
    *Reversal cost:* one file — the row widget — for everything except exclusivity, which needs
    a new coordination point first.

30. **Every valid tap on this screen fires both feedback channels — the haptic and the tap
    sound — on the same eight gestures.**

    ```dart
    ref.read(hapticServiceProvider).validAction();              // P2-03 req 14
    ref.read(audioLayerProvider).play(SoundMoment.buttonTap);   // P2-02 req 6
    ```

    **The eight sites:** a row tap that resumes a game, New Game, the trash button, **Yes**,
    **No**, `Cancel`, `Start playing`, and the back control.
    *Source — two Decisions, one per channel:* `Game Board Design.md` → Decisions (every valid
    tap buzzes, app-wide), which closed `P2-03` → OQ-2; and `Theming.md` → Decisions → *Do
    non-board controls make a sound?*, which settles **one tap sound everywhere** — every button,
    row and toggle. `P4-01-main-menu.md` req 24 carries the same pair for its menu buttons.

    Three properties carry across both channels, and each removes a decision from the call site:
    - **The gate is inside each layer.** `P2-03` req 10 checks `vibrateOnTouchEnabledProvider`
      and `P2-02` req 6's `ThemedAudioLayer` closes over `soundEffectsEnabledProvider`, so **this
      screen calls unconditionally and reads neither setting**. It also reads no `sound` key and
      no `Theme.sound` path — the moment names the intent, the layer resolves the asset.
    - **`buttonTap` is one moment with one asset**, so there is no per-control variation to
      choose. `P2-02` req 6's own testable asserts *"every `buttonTap` call resolves the same
      path regardless of which control triggered it."*
    - **The exactly-once assertion is this PRD's**, not the layers'. `P2-02` req 6 states that a
      control's tap reaching `play` exactly once is *"a call-site fact, owned by each calling
      PRD"* and names this requirement as the owner of these eight sites; `P2-03` req 1 says the
      same for the haptic.

    *Testable:* in a `ProviderScope` overriding `hapticServiceProvider` with a recording
    `FakeHapticService` and `audioLayerProvider` with **`FakeAudioLayer`**, each of the eight
    gestures records exactly one `validAction()` and exactly one
    `play(SoundMoment.buttonTap)` — never zero, never twice, and no other moment. A swipe that
    only reveals is a valid action and fires both once; a body tap that closes the reveal fires
    both once.
    **Use `FakeAudioLayer`, not `RecordingOneShotSink`.** The sink sits *below* the mute gate, so
    asserting against it answers a different question — whether a file was played — while this
    requirement is about whether the call site fired. `P2-02` req 6's own wave-2 tests use the
    sink because they are testing the layer; this one is testing the caller.
    *Recorded:* `P2-02` req 6's owner table listed this requirement as an owner of
    `SoundMoment.buttonTap` while it was haptic-only. It is an owner now.

## Out of Scope

Referenced by filename rather than specified here:

- **The main menu** → `P4-01-main-menu.md`.
- **The routing layer** — the Play Game branch, the prompt's transitions, resume, leaving the
  list, route opacity, and ratifying requirement 28's route and operation →
  `P2-01-navigation.md`.
- **Storage** — the repository, Hive, `GameId` minting, the create-time cap check, the `delete`
  implementation, `StoredGame`'s shape **including both timestamp fields, their semantics and
  the sort direction** (`P1-04` reqs 21 and 29, settled at its Open Question 8), the ordering
  guarantee, and the providers → `P1-04-persistence.md`. This screen reads what it is given and
  sorts nothing.
- **Both feedback layers themselves** — the platform call, the mute and vibrate gates, asset
  resolution, the no-engine case → `P2-03-haptics.md` and `P2-02-audio.md`. This screen is a
  caller of each.
- **The entitlement model and the cap's value** → `P1-07-entitlements.md`. **The purchase** →
  `P4-05-purchase-flow.md`.
- **The game screen and everything inside a game** → `P3-01-board-rendering.md`,
  `P3-02-move-input.md`, `P3-03-scoreboard-turn-indicator.md`, `P3-04-game-over-rematch.md`.
- **The rules of play** → `P1-02-engine-rules.md`, `Rules.md`.
- **The theme schema.** Requirement 20 names the values still without a key and requirement 4
  asks for three keys to be deferred → `P1-03-theme-system.md`.
- **Theme selection and settings**, reachable from the main menu, not from here.
- **The About Us screen (`1c`)** — drawn in the handoff, unlisted in `Menus and UI.md`.
- **`Alternative Game Styles.md`** — parking lot, not what is being built.

## Open Questions

### Needs the user — none of them blocking a build

4. **What does a row show besides the opponent's name?** *(The build half is fenced in
   requirement 4.)* Four decisions, not one — **and one of the four is now answered.**

   - **4a — Does a row show a date, and which one?** **Still open, and it no longer depends on
     4c.** Two fields exist — `createdAt` and `updatedAt` (`P1-04` req 21) — so this question is
     now *whether* the player sees a date and, if so, *which*: a "last played" line reads
     `updatedAt`, a "started on" line reads `createdAt`. Neither follows from the fields
     existing. Lands in `Menus and UI.md` → Decisions, then requirement 4 here and `P1-03`
     req 15's status for `surfaces.gameRow.timeStyle`. If it lands on yes, the wording is
     unwritten too — nothing specifies what a relative date reads as.
   - **4b — Does a row show the three score chips?** Still open, and always was independent of
     4c — the score is already in `Board`. Lands the same way.
   - **4c — ANSWERED: the dates are stored regardless of what is displayed.** The user settled
     `P1-04` → Open Question 7 **yes**, which is where this half lived: `StoredGame` carries a
     timestamp, as a wave-1 model change; `P1-04` → Open Question 8 then settled that it carries
     **two**. That PRD's req 29 said *"one field settles three things"* — a stable sort key, a
     meaningful list order, and the relative timestamp `1b` draws — and the first two are now
     delivered by its settled ordering guarantee. **Storing without displaying is exactly where
     this landed**, which is the coherent middle this question described: the ordering defect is
     fixed and requirement 4's fence is intact.
     *No residual.* The field names, their semantics and the sort direction were the leftovers;
     the user has closed all three at `P1-04` → Open Question 8.
   - **4d — If the chips ship, what are they labelled?** `1b` says `YOU / TIES / THEM`; every
     design doc says Player One / Player Two. **A separate question from the one already
     settled** — `Game Overview.md` → *Player-facing vocabulary* closed "board" vs "quadrant" and
     says nothing about player labels.

   **Two files still disagree until 4a/4b land:** `P1-03` req 15 marks
   `surfaces.gameRow.{timeStyle,chip,chipYouOutline}` **required** and names this PRD's
   requirements 4, 17 and 18 as their consumer; requirement 4 leaves them unread. The date
   answer does not resolve that — stored fields with no reader are still no reader.

20. **Is single-row exclusivity wanted on the revealed row?** Requirement 29 says two rows may be
    revealed at once, because requiring otherwise needs a coordination point above the rows and
    requirement 21 records that all three homes are closed today: screen-level state contradicts
    the list's `ConsumerWidget`, a `lib/ui/` provider is what requirement 25 forbids, and a
    package group-controller is absent from `P1-01` req 14's exhaustive dependency list.
    **Answering "no" costs nothing and the screen is finished as written; answering "yes" means
    opening one of those three first.** No design doc mentions the reveal at all, so this is a
    product call rather than a gap.

21. **Should the destructive path sound like everything else?** *(An observation, recorded rather
    than decided.)* Requirement 30 fires the same `buttonTap` on all eight gestures, including
    the trash button and **Yes** — the consistent reading of *"one tap sound everywhere"*, and
    what this PRD builds. It is the one place on this screen where the two channels could
    reasonably diverge: **Yes** destroys a series permanently, and an ordinary button tap is what
    it will sound like. Nothing suggests otherwise and `buttonTap` has no variants to reach for,
    so changing it would mean adding a moment to `P2-02`'s five — which is why this is noted, not
    fenced.

14. **Two pieces of copy do not exist**, and this PRD invents neither: the **`CapReached`
    message** (requirement 22, blocked behind Open Question 3) and **`1b`'s footer replacement
    with its plural and zero cases** (requirement 24). *(A third would join them if 4a lands on
    "yes" — the date's wording is unwritten as well.)*

3. **What does New Game do when the player is already at the effective cap?** Settled: both
   ceilings, delete frees a slot, replace-the-oldest rejected, and the storage contract. Open:
   what the player is *offered* — refuse, route into delete, or offer the $4.99 unlock. Also
   `P1-04` → Open Question 3. **If the answer is the upsell**, this PRD and
   `P4-05-purchase-flow.md` stop being parallel-safe inside wave 4.

1. **Does the empty-state path show the name prompt?** `Menus and UI.md` → Play Game → Where It
   Takes You: *"Undecided: whether the empty-state path … also shows the opponent-name prompt, or
   skips it."* Also `P2-01` → Open Question 4. **It decides whether the prompt has one caller or
   two.**

8. **What does the list do when the stored count exceeds the effective cap?** Requirements 2 and
   6 are scoped away from it. Open in `P1-07` → Open Question 1 and `P1-04` → Open Question 5.
   Three PRDs defer it onto each other; none can answer it, because keeping 57 games a player can
   no longer create is a product call.

9. **Is any part of a game's identity ever shown to the player?** `P1-04` → Open Question **6b**.
   Three rows reading `ItSaMeMaRiO` is the default case and requirement 4's interim row gives a
   player nothing to tell them apart. Requirement 27's copy says "this game", so the modal does
   not depend on the answer. **Note the overlap with 4a:** a displayed date would disambiguate
   the rows without making the id itself visible, so answering 4a "yes" would soften this without
   answering it.

### Routed to another PRD — asks, not questions for the user

16. **Ratify requirement 28's route and operation, and close the scan loophole.** Neither blocks
    this file: requirement 28 is the build instruction. Ask 1 turns the fence into a citation;
    **ask 2 is worth doing regardless**, because `showGeneralDialog` and `showAdaptiveDialog`
    pass a scan meant to catch exactly them.

6. **CLOSED — nothing specifies the order the list arrives in.** `P1-04` **req 29** now does:
   `readAll()` returns a stable order sorted **most-recent-first on `updatedAt`**, because the
   user settled that the fields exist (that PRD's Open Question 7, this PRD's 4c) and then
   settled the comparator itself (that PRD's Open Question 8). Requirement 2 cites the guarantee
   instead of fencing against its absence, and the silent-reshuffle failure mode is gone.
   **Nothing is left over:** the sort direction was the residual and it is now settled, and this
   screen was indifferent to it either way because it sorts nothing. Kept as a numbered stub so
   requirement 2's citation stays stable.

### Fenced in this PRD — a build default is in place, with its reversal cost

10. **How is the entered name normalized?** Requirement 11. One file.

11. **Does New Game scroll away with the list, or stay pinned?** Requirement 3. One file.

13. **What renders while the list loads, and when the last game is deleted?** Requirement 26.
    One file.

18. **The delete modal's exact sentence.** Requirement 27 fences
    `Permanently delete this game?`. One string.

2. **Is the name prompt its own screen or an overlay?** Under `P2-01` req 2 this is a
   `pageBuilder` choice on a route that exists either way — but requirement 20's underlay dim
   only exists under the overlay reading.

7. **How does the player leave the list without picking anything?** `1b` draws a back button; no
   design doc says where back goes. `P2-01` **req 13** owns `leaveOpenGamesList()`; its Open
   Question 8 holds the destination open. *(Note `P2-01`'s Open Question 2 — the game exit — has
   since been settled by the user as `router.go('/')`, and that PRD records explicitly that the
   argument does not transfer to this control.)*

### Answered since an earlier draft — recorded so they are not re-raised

15. **Does the reveal survive a No?** — **DISSOLVED, not fenced.** Requirement 29 closes the
    reveal when the trash button is tapped, so by the time the modal is on screen the row is
    already resting and the question cannot arise. This replaced a fence that had **no
    implementation path**: `P2-01` req 3 returns no result to any caller and bans `go_router`
    outside `lib/navigation/`, so the row could never have learned that No was tapped, and the
    testable *"tapping No leaves the row resting"* could not have been written.

17. **`icons.trash` does not exist, and there is no legal fallback.** — **ANSWERED.** `P1-03` v8
    adds `icons.trash` as **required (authored)** and reshapes `surfaces.destructive` into
    `action.{fill,radius}` + `confirmAccept.{fill,labelStyle,border,radius}`.

5. **How is the delete action reached, and does it confirm?** — **ANSWERED.** Swipe left → trash
   button → modal → Yes/No. Requirement 7 implements it, 27 carries the copy and the order, 17
   binds the paint, 28 hosts it, 29 orders the reveal, 30 sounds and buzzes it.

12. **`openGamesRepositoryProvider` and the list provider are declared nowhere.** — **ANSWERED**
    by `P1-04` req 28.

19. **Do controls outside the board buzz — and do they sound?** — **ANSWERED, both channels.**
    Every valid tap buzzes app-wide (`Game Board Design.md` → Decisions) and every button, row
    and toggle plays one tap sound (`Theming.md` → Decisions → *Do non-board controls make a
    sound?*). Requirement 30 owns this screen's eight call sites for both.

**Modal padding — never a numbered question, and closed from the other side.** `P1-03` v7 removed
**every** spacing key: padding is fixed in code where a guard cannot catch a hardcoded gap
(`Theming.md` → Decisions → *Does a theme control spacing and padding?*). Requirement 20 drops it
as a boundary, not a gap.
