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

Numbers are stable, so R39–R46 — added after the first draft — sit beside the requirements
they belong with rather than at the end. Read the sections in order; the numbers are labels,
not a sequence.

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
holding `matchId`, `seriesId` and `localPlayer`. `matchId` and `seriesId` are strings;
`localPlayer` is the `Player.name` string — `playerOne` or `playerTwo` — exactly as
`Board.toJson` already encodes a player. Those key names and encodings are on-disk identity
the moment a record ships and are schema, not a naming choice made at implementation time.
The Dart type and field names are the code's to pick. (Tech Design → *Serialization and the
storage layer*, which fixes the box name and the JSON-string encoding for exactly this
reason; `lib/engine/board.dart` for the player encoding)

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
already has. The New Game prompt's 16-character limit does **not** reach it. (Menus and UI →
*Play Game → Where It Takes You*; Tech Design → *What a stored open game holds*)

**R39.** **The storage layer applies no name fallback.** A create whose title is empty or
whitespace-only is refused, and the refusal is distinct from the cap refusal so the caller
can tell them apart; nothing is stored. Supplying a title is the caller's, and the bridge
supplies `ItSaMeMaRiO` — the one fallback string the app already holds, in the state layer —
if Game Center ever hands back a blank display name. It never does for an authenticated
player, so this is the defensive path rather than the ordinary one, and it stays out of
storage because a layer that substitutes a title is a layer that can rename a game.
(Menus and UI → *Play Game → Where It Takes You*, which names `ItSaMeMaRiO` as the default
and puts it on the New Game prompt rather than in the store; Tech Design → *What a stored
open game holds* for the set-at-create lifecycle R6 keeps)

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

**R10.** A record whose `online` key is present but unreadable — a missing `matchId`, a
missing `seriesId`, a `localPlayer` naming no player, wrong types — answers as "nothing
stored" for a read by id, and is skipped by the list read while every other game still comes
back. It is left on disk exactly as it is: neither rewritten nor deleted. An **unrecognised
extra key inside the `online` map is ignored**, not treated as unreadable: the three keys in
R3 are what is required, and a record written by a later version that added a fourth still
loads here. (Tech Design → *Reads return "nothing stored"*; → *Open Questions* → 1 for the
forward-loading case)

**R11.** Round-trip: a record created online and read back carries the identical match id,
series id, side, title, board and both timestamps. A local record round-trips exactly as it
does today. (Derived from R1–R4; Tech Design → *Serialization and the storage layer*)

### The series id

**R12.** The series id is opaque, unique across devices, never parsed, never displayed, and
**unchanged when a rematch mints a new match id**. It exists because the match id cannot
serve: *"nothing may treat a match id as stable across a series"*, while a rematch
*"continues in the same open game with the scoreboard intact"* — so something stable has to
cross the wire, and the record id cannot, being minted per device. (Tech Design → *Online
Play*; Menus and UI → *What an open game holds*; → *What a stored open game holds* for the
record id's per-device nature)

**R41.** **The create takes the series id from its caller; the storage layer never mints
one.** There are exactly two sources and no third: it is freshly minted by the device that
**starts** the match, and it is **copied out of the received payload** when a first payload
arrives for a series this device does not hold (R31). Both devices therefore hold the same
series id from the first turn onward, which is what R24 matches on. (Derived from R12, R31;
contrast Tech Design → *What a stored open game holds*, where the **record** id is
store-minted precisely because it is per-device)

### The wire payload

**R13.** What the match carries is the board as JSON in an envelope of exactly three keys:
`v` (the payload format version, an integer, `1` for this build), `seriesId`, and `board`
(the existing `Board.toJson()`, unchanged). Nothing else crosses the wire — no nickname, no
player id, no turn marker, no timestamps, **and no match id** — the match id is not in the
payload, it is what the match was delivered under (R44). (Tech Design → *Online Play*: the
match carries the board as JSON; R5 for what may not be added; the version key applies the
reasoning of → *Every persisted record carries a version stamp* to the wire, where two
devices on different app versions is the ordinary case rather than the rare one.)

**R42.** The encoder produces **UTF-8 bytes** (`Uint8List`) and the decoder takes bytes,
because Game Center's match data is bytes. Nothing above this seam handles a JSON string.
(Derived from R13; Tech Design → *Online Play*, where Apple holds the match data)

**R14.** The encoded payload for a full board — 81 cells marked, nine quadrant states with
winning lines, a long-running score — stays well inside Apple's 64 KB match-data ceiling.
**The encoder refuses to produce a payload over 48 KB**, with an error of its own rather
than a silent oversized send: 48 KB keeps headroom under Apple's hard ceiling, and *"anything
later added to the record spends against it"*. A test asserts both the refusal and that a
worst-case board is nowhere near it. (Tech Design → *Online Play*)

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

**R44.** The apply takes **three things: the record, the arriving match id, and the payload
bytes**. The match id is not in the payload (R13) — it is what Game Center delivered the
data under — and it is passed alongside because R24 and R43 both turn on it. (Derived from
R13, R24, R43)

**R45.** **Which branch runs is decided by the stored board, not by the match id.** A stored
board still in progress takes the in-game branch (R18); a stored board that is finished
takes the rematch branch (R24, R25). Deciding on "the match id differs" instead would misread
a re-delivery under the old match id after a rematch, and would have no branch at all for the
first payload of a rematch that happens to arrive before the record was re-pointed. (Derived
from R18, R24; Tech Design → *The series lives in the same state*, where the finished game
is what makes a next game reachable)

**R43.** **A payload is applied only when it is the opponent's turn to have sent it** — that
is, when the stored board's current player is the side this device does **not** play (R7). A
payload arriving while it is this device's turn is rejected as `outOfTurn` and nothing is
written, even if its board would otherwise pass R18. Both tests hold; neither replaces the
other. Reachability alone would accept a board this device itself produced and had echoed
back to it. (Derived from R7, R18)

**R18.** **Stored board in progress — a turn in the current game.** A received board is
applied only if some legal move from the record's stored board produces a board equal to it.
On acceptance the record's board becomes the received board, the arriving match id must equal
the stored one (R46), the updated timestamp is stamped from the repository's clock, and the
record moves to the top of the list exactly as any save does. (Queue item *The online-game
record*, which states the rule as: a received board must be reachable from the last known
board by exactly one legal move, else it is rejected and reported; Tech Design → *The
open-games list has a defined order* for the move to the top)

**R19.** A received board **equal to the stored board** is a re-delivery, not a violation:
nothing is written, and it is reported as its own outcome, distinct from a rejection. Game
Center re-delivers, and treating that as a corrupt payload would raise an error on a normal
event. (Derived from R18)

**R20.** Anything else — two moves ahead, a board with a cell that changed owner, a move into
a quadrant the sending rule did not allow, any unreachable position — is `notReachable`:
nothing is written, the stored board is untouched, and the caller is told. (A payload that is
reachable but arrived when it was this device's turn is `outOfTurn`, not this — R43.) What a
player is shown is out of scope. (Queue item, as R18)

**R21.** Validation **enumerates the legal moves and applies them**; it never calls the
engine and catches what it throws. The engine raises an `Error` on an illegal move, it is a
contract violation, and *"no caller is meant to catch it"*. (Tech Design → *What the engine
refuses*; Rules → *Engine Contract*)

**R22.** Every outcome of applying a received payload is a **returned value, never a throw**,
and the outcomes are **distinct enumerated values a caller can branch on**, not one failure
with a message: `applied`, `alreadyApplied` (R19), `notReachable` (R20), `outOfTurn` (R43),
`staleMatch` (R46), `undecodable` (R23), `unsupportedVersion` (R23), and `noSuchRecord`. A
caller that cannot tell a re-delivery from a corrupt payload cannot behave differently on
them, which is the whole point of R19. This is the same doctrine a refused create and a save
against an unknown id already follow. (Tech Design → *The cap is enforced on create, and the
store never evicts*; → *Reads return "nothing stored"*)

**R23.** A payload that will not decode — malformed JSON, a wrong-typed field, a missing
envelope key, or a board that is well-typed but not a legal board's shape — is
`undecodable`, and nothing is written. A payload whose `v` this build does not recognise is
`unsupportedVersion`, reported separately, because the two call for different things from
whoever handles them. (Derived from R13, R22; Tech Design → *Reads return "nothing stored"*,
which already treats a well-typed-but-illegal board as unreadable)

### A rematch mints a new match id

**R24.** **Stored board finished — the rematch branch.** Apple's rematch creates a fresh
match rather than reopening the finished one, so the first payload of the next game arrives
under a match id the record does not hold, carrying the series id it does (R12, R41). It is
matched to that record by series id, and the record's match id is replaced with the arriving
one. The record keeps its own id, its title, its created timestamp, its side (R8) and its
score. Acceptance stamps the updated timestamp and moves the record to the top of the list,
exactly as any other apply does (R18). (Tech Design → *Online Play*; Menus and UI → *What an
open game holds*)

**R25.** The board that payload carries is validated against `startNextGame(stored board)`
rather than against the stored board: it is accepted if it equals that next board, or if some
legal move from that next board produces a board equal to it — **zero or one move, and both
are ordinary.** Game Center makes the rematch's initiator the current participant whoever the
engine says goes first, so an initiator whose side is *not* the first player of the next game
ends its turn immediately with the fresh board and no move on it, and that untouched next
board is what arrives. Acceptance stamps the updated timestamp and moves the record to the
top, as R24 says. (Derived from R18, R24; Rules → *Turn Order Across Games*, which is what
`startNextGame` encodes; GameKit's documented rematch behaviour)

**R46.** **An arriving match id that differs from the stored one while the stored board is
still in progress is `staleMatch`** — rejected, nothing written. It is not a rematch, because
R45 selects that branch on the finished board; it is a turn from a match this record is no
longer, or was never, playing. (Derived from R45; Tech Design → *The series lives in the same
state*, where a next game is reachable only from a finished game)

**R27.** The score survives: after an accepted rematch payload, the record's score is the
score the finished game ended on, and the board is a fresh game. (Derived from R24, R25;
Game Overview → *Session Structure*; Menus and UI → *What an open game holds*)

**R26.** **The initiating device has its own path, and it is one write.** Taking the next
game on this phone advances the record to `startNextGame(stored board)` and stores the new
match id together — one operation, e.g. `startNextOnlineGame(recordId, newMatchId)` — so a
record can never sit with the next game's board under the finished game's match id, or the
reverse. It requires a finished stored board and answers a value, not a throw, when the board
is in progress or the id names no record. (Derived from R24, R45; Tech Design → *The series
lives in the same state*)

**R28.** **A rematch is not a create**, on either device. No cap check runs, no second record
appears, and a rematch is accepted while the player is at the ceiling. (Menus and UI → *How
many open games we keep*: reaching the cap never makes the app delete or replace a game, and
a rematch stays in the same open game)

### Creating, accepting, and the cap

**R29.** Creating an online game takes the opponent's nickname, the starting board, the match
id, **the series id** and this device's side — all five from the caller, none minted here
(R39, R41) — and answers exactly as the existing create does: the stored record with its
store-minted record id, or a refusal carrying the effective ceiling and how many games are
held. (Tech Design → *The cap is enforced on create*; existing `GameRepository.createGame`
contract)

**R30.** **Accepting an invite is a create**, and it is refused at the ceiling exactly as
starting one is and exactly as a local New Game is. There is no separate online allowance and
no exemption for a match somebody else started, and nothing is evicted to make room. But the
create happens **when the starter's first payload lands, not when the invitation is
accepted** — before that there is no board to store, and this layer stores no record without
one. So the cap bites on the arriving payload's route (R31). (Tech Design → *The cap is
enforced on create*; Menus and UI → *How many open games we keep*; derived from R1, which
makes a record a board plus its series)

**R31.** A payload carrying a series id no held record matches is not an apply — it is the
first payload of a game this device does not have, and reaches the caller as such so the
create path (R29, R30) handles it, cap included. Its series id is what the create is then
given (R41), and its match id and board are the other two. (Derived from R24, R30, R41)

**R32.** Creating an online game for a match id a record already holds does **not** create a
second record: the existing record is answered with, **unchanged** — not re-titled, not
re-stamped — and the change stream emits nothing, because nothing changed. A duplicate
delivery would otherwise consume a second cap slot and split one match across two records.
(Derived from R1, R30; existing `GameRepositoryChanges` contract)

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
anything. **The battery covers operations and their outcomes only.** The JSON-level
requirements — R3's keys and encodings, R9's older records, R10's unreadable ones, R11's
round-trip — are asserted against the codec and the Hive implementation, because the
in-memory store never serializes anything and would pass them vacuously. (Tech Design →
*Serialization and the storage layer*; existing `lib/storage/in_memory_game_repository.dart`)

**R35.** The surface gains: a create for an online game (R29); a lookup by match id and a
lookup by series id, each answering nothing-held rather than throwing; an apply of a received
payload to a held record (R44), answering one of the outcomes in R22; and the initiating
device's next-game-plus-new-match-id write (R26). Signatures are the code's to state.
(Derived from R22, R24, R26, R29, R31, R44 — each operation exists because one of those
requires it)

**R36.** `saveGame` is unchanged for an online record: only the board is honoured, and the
match id, series id, side, title and created timestamp are preserved exactly as the title
already is. **The match id changes on exactly two paths and no others** — the initiating
device's own next-game write (R26), and an accepted rematch payload (R24). (Existing
`GameRepository.saveGame` contract; Tech Design → *What a stored open game holds*)

**R37.** The open-games change stream emits after an accepted remote turn and after the
next-game write (R26), and does not emit after a re-delivery or any rejection, because
neither changed what the list would show. (Existing `GameRepositoryChanges` contract)

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
- **Substituting a title when Game Center's display name is blank.** R39 refuses an empty
  title; the bridge passes `ItSaMeMaRiO` in that case, using the constant the state layer
  already holds.
- **Deciding when to offer a rematch, and initiating one.** R26 is the write; the button, and
  calling Apple's rematch to get the new match id, are the online game-over PRD's.
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
