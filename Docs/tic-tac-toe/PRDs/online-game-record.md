# PRD: The online-game record

> **Status:** Draft · Source docs read: Tech Design, Game Overview, Menus and UI, Rules,
> Theming, Game Board Design, Animations (Alternative Game Styles is a parking lot and was
> not sourced from). Code read: `lib/engine/board.dart`, `lib/engine/rules.dart`,
> `lib/storage/game_repository.dart`, `lib/storage/hive_game_repository.dart`,
> `lib/storage/in_memory_game_repository.dart` on branch `queue/online-game-record`.

## Problem

Every open game on the device today is a game between two people holding one phone. An
online game — [Game Overview](../Game%20Overview.md) → Modes, over Apple Game Center
turn-based matches — is the same series of boards, but the device is now one of two holding
a copy, and it has to know three things a local game never needed: which Game Center match
this game is, which of Player One and Player Two *this* device plays, and whether the board
it is holding is still the one the other device has.

There is nowhere to put any of that. `GameRecord` holds the board, a title, two timestamps
and a version stamp, and nothing distinguishes a game on this phone from a game against
someone in another country. Every piece of online work queued behind this one — the
GameKit bridge, the board screen locking input on the opponent's turn, the open-games list
saying whose turn it is, the online game-over and rematch — reads or writes that missing
shape, so each of them would otherwise invent its own.

## Goal

An online game is an open game with three extra stored facts and one extra rule. It lives
in the same Hive box, holds the same id, timestamps, version stamp and list position, and
counts against the same open-games cap. It additionally records the Game Center match it is
currently played through, the series that match belongs to, and which side this device
plays — and nothing else about either player. Two pure-Dart seams exist and are tested with
no GameKit in sight: one turns a record into the bytes the match carries, and one decides
whether a board that arrived from the other device may be applied to the record, by
replaying it against the rules engine. Records already on players' phones load exactly as
they did before.

## Requirements

Each requirement names where it came from. "Derived from Rn" means no design doc states it;
it follows from a requirement here that a doc does state, and it is called out so it can be
argued with.

### What a record holds

**R1.** An online game is a `GameRecord` in the same `open_games` box, with the same
store-minted id, the same repository-owned created and updated timestamps, the same app
version stamp, and the same position in the open-games order. Nothing in this PRD adds a
second store, a second box, or a second record type. (Tech Design → *What a stored open
game holds*; → *The open-games list has a defined order*; Menus and UI → *How many open
games we keep*)

**R2.** An online game adds exactly three stored values, and no others: the **match id** it
is currently played through, a **series id**, and **which side this device plays** — Player
One or Player Two. (Tech Design → *Online Play*; → *What a stored open game holds*)

**R3.** These three are written under a single `online` key on the stored record's JSON,
holding `matchId`, `seriesId` and `localPlayer`. Those key names are on-disk identity the
moment a record ships and are schema, not a naming choice made at implementation time. The
Dart type and field names are the code's to pick. (Tech Design → *Serialization and the
storage layer*, which fixes the box name and the JSON-string encoding for exactly this
reason)

**R4.** **The presence of that key is the only thing that tells an online game from a local
one.** A record whose `online` key is absent, or present and null, is a local game and
loads exactly as it does today; a record carrying the key is online. Nothing infers
online-ness from the title, the board, or anything else. (Derived from R2; Tech Design →
*What a stored open game holds*)

**R5.** **The record stores no Game Center identity.** Not the opponent's player id, not the
local player's, not a team or alias beyond the nickname in R6. The app collects no identity
of its own, and the players' identities live in the match, with Apple. Knowing which side
this device plays is what R2 stores instead of an identifier, and it is the reason that is
the shape. (Tech Design → *Online Play*; → *What the record declares about data collection*)

**R6.** An online game's title is the opponent's Game Center nickname, captured when the
record is created, and a save never changes it — the same lifecycle the typed opponent name
already has. The New Game prompt's rules do **not** reach it: no `ItSaMeMaRiO` default, and
no 16-character limit. (Menus and UI → *Play Game → Where It Takes You*; Tech Design → *What
a stored open game holds*)

**R39.** If the nickname handed to the create is empty or whitespace-only, the record is
titled **`ItSaMeMaRiO`** — the same default a local game falls back to, so there is one
fallback string in the app rather than two. It is a fallback, not a rename: once stored, R6
holds and a save never changes it. Game Center's display name is never empty for an
authenticated player, so this is the defensive path rather than the ordinary one. (Menus and
UI → *Play Game → Where It Takes You*, which names `ItSaMeMaRiO` as the default; R6 for the
lifecycle)

**R7.** **Whose turn it is is not a stored field.** It is `board.currentPlayer` compared
against the side in R2. Whose turn it is is engine state and is never derived a second way,
and storage holds only what no design doc puts in game state. (Tech Design → *The series
lives in the same state*; → *What the engine is not*)

**R8.** The side in R2 is set when the record is created and never changes for the life of
the record — including across a rematch, where the side stored on the record wins over any
assignment that could be derived from the new match. (Derived from R7; Menus and UI → *What
an open game holds*: a rematch continues in the same open game)

**R40.** **The device that starts the match is Player One in the first game of the series;
the device that accepts is Player Two.** Game Center makes the match creator the current
participant when a match is found or created (`GKTurnBasedMatch.find` — *"the local player is
always the current participant"*), so the creator moves first, and game 1's first player is
Player One. The advantage does not accumulate: from game 2 the winner of the last game goes
first, and a tie leaves it where it was. Nothing is derived from this at read time — the side
is stored once at create (R2, R8) and read from the record thereafter. (Rules → *Turn Order
Across Games*; Game Overview → *Session Structure*; GameKit's documented match-creation
behaviour)

**R9.** **A record written before this change still loads, unchanged, as a local game**, and
a local game written after this change is read back by the same code path with no `online`
key required. *"A game written by v1.0 has to still load in v1.1."* (Tech Design → *Open
Questions* → 1. Persisted data — migration. The wider migration policy is still open; see
Open Questions below.)

**R10.** A record whose `online` key is present but unreadable — missing `matchId`, a
`localPlayer` naming no player, wrong types — answers as "nothing stored" for a read by id,
and is skipped by the list read while every other game still comes back. It is left on disk
exactly as it is: neither rewritten nor deleted. (Tech Design → *Reads return "nothing
stored"*)

**R11.** Round-trip: a record created online and read back carries the identical match id,
series id, side, title, board and both timestamps. A local record round-trips exactly as it
does today. (Derived from R1–R4; Tech Design → *Serialization and the storage layer*)

### The series id

**R12.** The series id is opaque, minted once when the first match of a series is created,
unique across devices, never parsed, never displayed, and **unchanged when a rematch mints a
new match id**. It exists because the match id cannot serve: *"nothing may treat a match id
as stable across a series"*, while a rematch *"continues in the same open game with the
scoreboard intact"* — so something stable has to cross the wire, and the record id cannot,
being minted per device. (Tech Design → *Online Play*; Menus and UI → *What an open game
holds*; → *What a stored open game holds* for the record id's per-device nature)

### The wire payload

**R13.** What the match carries is the board as JSON in an envelope of exactly three keys:
`v` (the payload format version, an integer, `1` for this build), `seriesId`, and `board`
(the existing `Board.toJson()`, unchanged). Nothing else crosses the wire — no nickname, no
player id, no turn marker, no timestamps. (Tech Design → *Online Play*: the match carries
the board as JSON; R5 for what may not be added; the version key applies the reasoning of →
*Every persisted record carries a version stamp* to the wire, where two devices on different
app versions is the ordinary case rather than the rare one.)

**R14.** The encoded payload for a full board — 81 cells marked, nine quadrant states with
winning lines, a long-running score — stays well inside Apple's 64 KB match-data ceiling,
and a test asserts a concrete ceiling against a worst-case board rather than leaving the
headroom assumed. (Tech Design → *Online Play*)

**R15.** Encoding then decoding a payload yields a board JSON-equal to the one encoded, for
every board an engine replay can produce — including a fresh series, a board with no last
move, a won board with a winning line, and a draw. (Derived from R13)

**R16.** The encoder and the validator are **pure Dart in `lib/online/`**, importing no
Flutter, no `dart:ui`, no Hive and no platform channel, and a scan test asserts that the way
the engine's purity is already asserted. Tech Design leaves the folder to a PRD; this is it.
The Swift side and the Dart channel wrapper are a later PRD's and do not live here. (Tech
Design → *Online Play*: *"Which folder under `lib/` holds the Dart side is a PRD's job"*; →
*The Rules Engine* for the form of the check)

### Applying a turn that arrived

**R17.** Throughout this section, two boards are **equal** when their `toJson()` maps are
deeply equal. `Board` defines no `==`, and comparing identity or references would reject
every received board. (Derived from `lib/engine/board.dart`)

**R18.** **Same match id — a turn in the current game.** A received board is applied only if
some legal move from the record's stored board produces a board equal to it. On acceptance
the record's board becomes the received board, the updated timestamp is stamped from the
repository's clock, and the record moves to the top of the list exactly as any save does.
(Queue item *The online-game record*, which states the rule as: a received board must be
reachable from the last known board by exactly one legal move, else it is rejected and
reported; Tech Design → *The open-games list has a defined order* for the move to the top)

**R19.** A received board **equal to the stored board** is a re-delivery, not a violation:
nothing is written, and it is reported as its own outcome, distinct from a rejection. Game
Center re-delivers, and treating that as a corrupt payload would raise an error on a normal
event. (Derived from R18)

**R20.** Anything else — two moves ahead, a move by the wrong player, a board with a cell
that changed owner, an unreachable position — is **rejected**: nothing is written, the
stored board is untouched, and the caller is told. What a player is shown is out of scope.
(Queue item, as R18)

**R21.** Validation **enumerates the legal moves and applies them**; it never calls the
engine and catches what it throws. The engine raises an `Error` on an illegal move, it is a
contract violation, and *"no caller is meant to catch it"*. (Tech Design → *What the engine
refuses*; Rules → *Engine Contract*)

**R22.** Every outcome of applying a received payload is a **returned value, never a throw**
— accepted, re-delivery, rejected, undecodable, unrecognised version, and no record held for
this match. This is the same doctrine a refused create and a save against an unknown id
already follow. (Tech Design → *The cap is enforced on create, and the store never evicts*;
→ *Reads return "nothing stored"*)

**R23.** A payload that will not decode — malformed JSON, a wrong-typed field, or a board
that is well-typed but not a legal board's shape — is rejected and nothing is written. So is
a payload whose `v` this build does not recognise. (Derived from R13, R22; Tech Design →
*Reads return "nothing stored"*, which already treats a well-typed-but-illegal board as
unreadable)

### A rematch mints a new match id

**R24.** **New match id, known series id.** Apple's rematch creates a fresh match rather than
reopening the finished one, so the first payload of a rematch arrives under a match id no
record holds, carrying a series id one does. It is matched to that record by series id, and
the record's match id is replaced with the new one. The record keeps its own id, its title,
its created timestamp, its side (R8) and its score. (Tech Design → *Online Play*; Menus and
UI → *What an open game holds*)

**R25.** The board that payload carries is validated against `startNextGame(stored board)`
rather than against the stored board: it is accepted if it equals that next board, or if
some legal move from that next board produces a board equal to it — the rematch's first
player may or may not have moved before sending. (Derived from R18, R24; Rules → *Turn Order
Across Games*, which is what `startNextGame` encodes)

**R26.** If the stored board is **not** finished when such a payload arrives, it is rejected
and nothing is written. A next game is reachable only from a finished game, and the engine
defines no behaviour otherwise. (Tech Design → *The series lives in the same state*)

**R27.** The score survives: after an accepted rematch payload, the record's score is the
score the finished game ended on, and the board is a fresh game. (Derived from R24, R25;
Game Overview → *Session Structure*; Menus and UI → *What an open game holds*)

**R28.** **A rematch is not a create.** No cap check runs, no second record appears, and a
rematch is accepted while the player is at the ceiling. (Menus and UI → *How many open games
we keep*: reaching the cap never makes the app delete or replace a game, and a rematch stays
in the same open game)

### Creating, accepting, and the cap

**R29.** Creating an online game takes the opponent's nickname, the starting board, the match
id, a freshly minted series id and this device's side, and answers exactly as the existing
create does: the stored record with its minted id, or a refusal carrying the effective
ceiling and how many games are held. (Tech Design → *The cap is enforced on create*; existing
`GameRepository.createGame` contract)

**R30.** **Accepting an invite is a create.** It goes through the same call and is refused at
the ceiling exactly as starting one is, and exactly as a local New Game is. There is no
separate online allowance and no exemption for a match somebody else started. Nothing is
evicted to make room. (Tech Design → *The cap is enforced on create*; Menus and UI → *How
many open games we keep*)

**R31.** A payload carrying a series id no held record matches is not an apply — it is the
first payload of a game this device does not have, and reaches the caller as such so the
create path (R29, R30) handles it, cap included. (Derived from R24, R30)

**R32.** Creating an online game for a match id a record already holds does **not** create a
second record; the existing record is answered with instead. A duplicate delivery would
otherwise consume a second cap slot and split one match across two records. (Derived from R1,
R30)

**R33.** Deleting an online game removes the record and its whole series like any other open
game, leaving every other record untouched. What it does to the opponent's copy is not
settled — see Open Questions. (Menus and UI → *Deleting an open game*; Tech Design → *The cap
is enforced on create, and the store never evicts*)

### The repository surface

**R34.** The additions are operations on the existing `GameRepository` interface, and every
caller keeps depending on the interface rather than an implementation. Both the Hive-backed
and the in-memory implementations implement them, and the shared contract battery
(`test/storage/game_repository_contract_test.dart`) runs over both — the in-memory
implementation is shipped code, not a test double, which is what makes that battery worth
anything. (Tech Design → *Serialization and the storage layer*; existing
`lib/storage/in_memory_game_repository.dart`)

**R35.** The surface gains: a create for an online game (R29); a lookup by match id and a
lookup by series id, each answering nothing-held rather than throwing; and an apply of a
received payload to a held record, answering one of the outcomes in R22. Signatures are the
code's to state. (Derived from R22, R24, R29, R31 — each operation exists because one of
those requires it)

**R36.** `saveGame` is unchanged for an online record: only the board is honoured, and the
match id, series id, side, title and created timestamp are preserved exactly as the title
already is. The match id changes on one path only — an accepted rematch payload (R24).
(Existing `GameRepository.saveGame` contract; Tech Design → *What a stored open game holds*)

**R37.** The open-games change stream emits after an accepted remote turn, and does not emit
after a re-delivery or a rejection, because neither changed what the list would show. (Existing
`GameRepositoryChanges` contract)

**R38.** There is no send in this layer. The record's board is advanced past a local move by
an explicit save the bridge makes **after** Game Center has accepted the turn, so a stored
board never shows the opponent to move on a turn this device did not successfully hand off —
which is what keeps R7's derived turn from disagreeing with the match. (Derived from R7)

## Out of Scope

- **All GameKit and Swift.** Authentication, the matchmaker, sending a turn, receiving one,
  invites, "your turn" notifications, quit and resign — a later PRD each.
- **Every screen.** The open-games list showing whose turn it is or which games are online,
  the board locking input on the opponent's turn, the online game-over and its rematch
  button, and "Play online" on the main menu.
- **The parental gate**, and hiding online play when Apple reports multiplayer is restricted.
  (Tech Design → *Kids Category*)
- **What the player is told** when a payload is rejected, or when a create is refused at the
  cap.
- **Deciding which side each device plays at match time.** R40 fixes the rule; carrying it
  out — reading the match's participants and handing the side to the create — is the bridge's.
- **The network scan** the tech design claims, and its GameKit path — a separate queue item.

## Open Questions

- **When the shape of stored data changes — a fifth preference is added, a key is renamed, an
  open game gains a field — what happens to data already on the device?** R9 settles the one
  case this feature creates; the general policy is still open. (Tech Design → Open Questions →
  1. Persisted data — migration)
- **What does New Game do when the player is already at the cap** — refuse and say the list is
  full, route the player into the delete flow, offer the $4.99 unlock at the moment the limit
  bites, or some combination? The same is unsettled for starting an online game and for
  accepting an invite to one, which hit the same cap. (Menus and UI → Open Questions)
- **When a player deletes an online game, should the other player's copy end too, or should it
  only leave this phone?** Unanswered in the queue's Blocked list. It does not block anything
  here — R33 deletes the record either way — but it decides whether the bridge resigns the
  match on the way out.
- **Should a re-delivered identical board (R19) be visible to the player at all, or silently
  ignored?** R19 settles the data side only.
- **What happens when a payload arrives carrying a `v` this build does not recognise** beyond
  R23's rejection — whether the player is told the other device is on a newer version, and
  whether that is distinguishable from a corrupt payload.
