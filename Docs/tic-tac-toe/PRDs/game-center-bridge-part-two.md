# PRD: Game Center bridge, part two — ending a turn, receiving one, and resigning

> **Status:** Draft · Source docs read: Tech Design, Menus and UI, Game Overview, Rules,
> Game Board Design, Animations, Theming (Alternative Game Styles is a parking-lot doc and
> was not sourced from). Existing code read from the `queue/play-online-button` worktree:
> `lib/gamecenter/`, `lib/online/`, `lib/storage/game_repository.dart`,
> `lib/state/game_controller.dart`, `lib/state/online_entry.dart`,
> `ios/Runner/GameCenterChannel.swift`.

## Problem

Part one signs the player in, presents Apple's matchmaker, and turns a found match into a
stored online game. Nothing crosses the wire after that. A player who starts an online
game can place a mark, but the move never reaches Apple's match, the opponent's move never
arrives, and there is no way out of a match other than deleting the record on this phone
and leaving the other player waiting on a turn that will never come.

Every piece the move needs already exists and is unreachable: `encodeTurnPayload` /
`decodeTurnPayload` (`lib/online/turn_payload_codec.dart`), the receive validator
(`lib/online/turn_decision.dart`), and the store's `applyReceivedTurn`,
`readGameByMatchId`, `readGameBySeriesId`, `createOnlineGame`, `startNextOnlineGame` and
`setOnlineOpponentName` (`lib/storage/game_repository.dart`). What is missing is the
transport between them and GameKit.

## Goal

A confirmed move on an online game is encoded and handed to Game Center, and only once
Apple has accepted it does it reach this device's store; a turn the opponent ends arrives
as an event, is routed to its own stored record by match id — or, for the first turn of a
series this device does not yet hold, creates that record — and is applied through the
receive rules already built; and deleting an online game resigns the match, so the other
player is not left waiting on a turn that will never come. The board screen, the open-games
list and the game-over flow are not built here; each gets the state-layer seam it calls.

## Requirements

### The channel

**R1.** The method channel keeps the name it has —
`com.ehrendavis.tictactoeextreme/gamecenter` — and gains two methods, `endTurn` and
`resignMatch`, for five in total. These two are the first that take an argument. Any other
method name still answers not-implemented. (Tech Design → Online Play → The channel
contract, which today states three methods and none taking an argument; this feature
widens both.)

**R2.** A third channel is added, an event channel named
`com.ehrendavis.tictactoeextreme/gamecenter/turns`, carrying turn events GameKit
originates. It is not folded into the session event channel: that channel's contract is
"the current value on subscribe, and every later change", and a malformed event on it
leaves the last known session standing — neither holds for turn events, which have no
current value and must not be silently coalesced. (Tech Design → The channel contract;
Signing in, and the session anything can read.)

**R3.** All three channel-name strings are written in exactly one Dart file under `lib/`
and exactly one Swift file under `ios/Runner/`, and the existing scan test that holds that
for the first two covers the third. The third Dart constant lives in the same file as the
other two — `lib/gamecenter/channel_game_center_bridge.dart` — because the scan matches the
name by substring, so a second file naming it anywhere would fail the scan regardless of
which layer wanted it. (Tech Design → Project Structure: "The two channel-name strings are
written in exactly one file on each side … and a scan test holds that".)

**R4.** No outcome on either new method is an error: the Swift side never answers a
`FlutterError`, and nothing on the Dart interface throws — including on a build with no
Swift side at all, which is every `flutter test` run. Every failure value carries a
non-empty message, and nothing branches on that text. (Tech Design → The channel contract.)

**R5.** Every reply and every event on the new method and the new channel is delivered on
the main thread. (Tech Design → Presenting Apple's matchmaker: "Every reply and every event
is delivered on the main thread, since GameKit's completion handlers promise nothing about
which thread they call on".)

### Ending a turn

**R6.** `endTurn` takes an argument map of exactly two keys: `matchId` (String) and
`payload` (the encoded bytes, carried as the standard codec's byte-array type). It answers
a map keyed `status` with `ok`, or `failed` carrying a non-empty `message`.

**R7.** The Swift side loads the match named by `matchId` and calls GameKit's
`endTurn(withNextParticipants:turnTimeout:matchData:completionHandler:)`, with the next
participants being every participant of the match that is not the local player, in
GameKit's own order; `GKTurnTimeoutNone` as the timeout; and the `payload` bytes verbatim
as the match data. (Tech Design → Online Play: "Turns never time out. A match is created
with `GKTurnTimeoutNone`" — GameKit takes the timeout on each `endTurn` rather than at
creation, so this call is where the app states it; and "The match carries the board as
JSON".)

**R8.** A `matchId` GameKit does not hold, a match the local player cannot be placed in, and
a GameKit failure all answer `failed` with a message. Nothing about them is distinguishable
to the caller beyond that — unlike the matchmaker's three outcomes, there is no second
behaviour for a caller to take. (Tech Design → The channel contract: every failure is a
reply value.)

### Resigning a match

**R9.** `resignMatch` takes an argument map of exactly one key, `matchId`, and answers
`status` `ok` or `failed` with a non-empty message, the same shape as R6.

**R10.** The Swift side loads the match and resigns the local participant with the `.quit`
outcome: `participantQuitInTurn` when the local player is the match's current participant,
`participantQuitOutOfTurn` when it is not. GameKit offers no single call covering both, and
calling the in-turn form out of turn fails.

**R11.** The in-turn form is handed the other participant as its next participants, the
match's own currently loaded match data unchanged, and `GKTurnTimeoutNone`. Resigning is not
a move, so the board the other device sees must not change — and GameKit's in-turn quit
requires match data, so passing empty data here would wipe the opponent's board.

**R12.** Deleting an online game resigns the match. The delete flow calls `resignMatch` for
the record's match id and then removes the record — see R45 for the ordering and for what a
failed resign does. *This is the main loop's recorded assumption, not a doc-settled
decision: the queue's Blocked question "when a player deletes an online game, should the
other player's copy end too" is still unanswered, and resigning is the kinder default it
names. Reversing it later removes one call; nothing is persisted either way.* (Tech Design →
Online Play: "A player who wants out of an online game deletes it from the open-games list";
→ Persistence and Serialization: "Deleting removes one open game and its whole series".)

**R45.** The delete flow calls `resignMatch` for the record's match id first and removes the
record after, and **the resign is best-effort: its failure is an answered value that is
never allowed to block or undo the delete.** A player who asked for a game to be gone gets
it gone whether or not Apple could be reached — the alternative is a game that cannot be
deleted while the phone is offline, which is worse than an opponent left waiting. Deleting a
local game calls nothing. Nothing is written to mark a resigned match: the record is gone, so
there is nowhere to write it and no schema change. An event that later arrives for that match
is dropped by R25 step 1.

### Turn events on the wire

**R13.** Every `player(_:receivedTurnEventFor:didBecomeActive:)` the registered
`GKLocalPlayerListener` receives is emitted on the turn event channel, as a map of exactly
five keys:

| Key | Value |
|---|---|
| `matchId` | the id the event was delivered under |
| `match` | the six-key match map part one already defines, built from this match |
| `matchData` | the match's loaded data as bytes, or null when the match holds none |
| `didBecomeActive` | GameKit's own flag, verbatim |
| `localParticipantQuit` | whether the local participant's status is `.done` with a `.quit` outcome |

The match id is a top-level key as well as a field of `match` because it is what routes the
event and it travels alongside the bytes rather than inside them. (Tech Design → Online
Play: "The match id is not in the payload; it is what the match was delivered under, and it
travels alongside the bytes to whatever handles them"; → The channel contract for the match
map's six keys.)


**R14.** The Swift side loads the match's data before emitting, exactly as `loadMatches`
already does for `hasData` — GameKit leaves a match's data nil until it is loaded, so an
event emitted without that load would carry no payload for every turn. A match whose data
fails to load, or whose local participant cannot be resolved, emits nothing. (Tech Design →
The channel contract; → Presenting Apple's matchmaker, on a match with no resolvable local
participant being left out rather than defaulted.)

**R15.** An event is emitted even while a matchmaker presentation is pending. Part one
consumes the first such event into the matchmaker's reply and emits nothing; it now does
both. This is what closes part one's device-pass finding that an unrelated opponent's turn
landing while the sheet is up is swallowed: the event still reaches the receiver and is
routed to its own record by match id. It does not change which event completes the pending
presentation — the first one still wins. (Tech Design → Presenting Apple's matchmaker, on
the found match arriving on the listener's turn event rather than the delegate; part one's
own note in `ios/Runner/GameCenterChannel.swift`: "discriminating an unrelated, concurrent
turn event by match id is part two's, once every match is routed to its own stored record".)

**R16.** Events that arrive while no Dart subscriber is attached to the turn channel are
buffered and replayed, in arrival order, on the next `onListen` — before the first one, and
again after an `onCancel`. The buffer holds at most one event per match id: a second event
for a match already buffered replaces that entry in place, keeping its original position in
the order, so the buffer cannot grow without bound if Dart never subscribes and a superseded
board is never replayed. The buffer is cleared as it is replayed.

**R17.** Subscribing to the turn channel does no GameKit work and registers no listener, so
a player who never enters online play still never sees Game Center. The listener stays
registered where part one registers it: once, on the first successful authentication. Turn
events before that are impossible. (Tech Design → Signing in, and the session anything can
read: "Registering the channel does no GameKit work, and neither does subscribing"; →
Presenting Apple's matchmaker, on the listener being registered on the first successful
sign-in "and not before".)

### The Dart bridge surface

**R18.** `GameCenterBridge` gains three members, and both implementations — the
channel-backed one and the fake that ships as app code — honour all three identically,
including every refusal. (Tech Design → State Management; → Signing in: "A fake bridge ships
as app code rather than test code … and holds no shortcut the real one could not honour".)

- `Stream<TurnEvent> get turnEvents` — broadcast, one subscription to the platform channel
  however many Dart listeners attach, and one listener cancelling tears nothing down for
  the others.
- `Future<EndTurnResult> endTurn({required String matchId, required Uint8List payload})`
- `Future<ResignMatchResult> resignMatch({required String matchId})`

**R19.** The platform turn channel is subscribed **lazily, on the first Dart listener** —
not eagerly at construction, which is what the session channel does. The receiver (R24) is
that listener, and until something listens the platform side holds its events in R16's
buffer rather than into a Dart stream nobody is reading. `turnEvents` itself replays
nothing on subscribe: a turn event is an occurrence, not a value with a current state, so
the session stream's replay behaviour is deliberately not copied, and what a late
subscriber would have missed is the platform buffer's to deliver.

**R20.** `EndTurnResult` and `ResignMatchResult` are each a sealed pair — an ok value and a
failed value carrying a non-empty message. Neither throws, for any outcome, on any build.
(R4.)

**R21.** `endTurn` and `resignMatch` called while the session is not
`GameCenterAuthenticated` answer their failed value and send no platform call, the same way
`presentMatchmaker` and `loadMatches` already refuse. Neither authenticates on the caller's
behalf. (Tech Design → Presenting Apple's matchmaker: "Neither the matchmaker nor a match
load signs the player in on the caller's behalf".)

**R22.** Decoding a turn event is strict and per key: nothing is coerced and no missing key
is defaulted. An event that is not a map, or whose `matchId` is missing, wrong-typed or
empty, or whose `matchData`, `didBecomeActive` or `localParticipantQuit` is wrong-typed, is
dropped and nothing is emitted on `turnEvents`. **A `match` value that fails part one's
match-map decode is the one exception:** it is carried through as absent rather than
dropping the event, because the event routes by `matchId` and applying a turn reads no field
of the match map. The only thing an absent match map costs is the rename step (R28), which
needs a nickname. Dropping the whole event instead would lose a legal move to a field the
move never reads. (Tech Design → The channel contract: "Decoding what arrives is strict, per
key, and all-or-nothing … A malformed event on the session channel is ignored".)

**R23.** `FakeGameCenterBridge` gains a way to push a turn event and to script the next
`endTurn` and `resignMatch` answers, and records both calls in its existing `calls` list, so
a caller's test can assert "sent no platform call" rather than merely stating it.

### The receiver

**R24.** One receiver in `lib/gamecenter/` subscribes to `turnEvents` and is the only
subscriber that writes to the store. It is reached through a provider of its interface, is
constructed once, and stays subscribed for the app's lifetime; a second live instance would
double-apply every arriving turn. (Tech Design → State Management.)

**R25.** For each event, in this order:

1. If the event carries `localParticipantQuit` true and no record is held for its match id
   → the event is dropped: this device has already left that match and there is nothing to
   apply it to. Published as its own outcome (R29) and nothing else runs.
2. Read the record held for the event's match id (`readGameByMatchId`).
3. If one is held **and the event carries a payload** → `applyReceivedTurn(recordId:
   record.id, matchId: event.matchId, payload: event.matchData)`, then continue at step 7.
4. If one is held **and the event carries no payload** → nothing is applied, and the event
   continues at step 7. This is the ordinary starter's-own-match event: GameKit reports the
   match the sheet just produced before either side has put data in it, and the participant
   it resolves is exactly what the rename step wants.
5. If none is held and the event carries no payload → nothing is applied and nothing is
   renamed; published as ignored (R29).
6. If none is held → decode the payload. A payload that will not decode, or names a version
   this build does not recognise, is dropped and published as its own refusal (R29); there
   is no record to route it to and no stored series to measure it against. Otherwise read
   the record whose series is the payload's series id (`readGameBySeriesId`): if one is
   held → `applyReceivedTurn` against that record's id, with the event's match id, which is
   the rematch's fresh match id finding the record it belongs to; if neither lookup holds a
   record → this is the first payload of a series this device does not hold, and it is
   created (R26).
7. Resolve the opponent's name (R28).

(Tech Design → Online Play, on the series id: "a device receiving the first payload of a
series it does not hold copies it out of that payload"; → Persistence and Serialization →
What an online game adds to the record, on `applyReceivedTurn` taking a record id rather
than a record.)

**R26.** The accepting device's create calls `createOnlineGame` with: the decoded board;
the payload's series id; the event's match id; `Player.playerTwo` as this device's side; and
the opponent participant's trimmed nickname as the title, falling back to the same
`ItSaMeMaRiO` placeholder a game on this phone defaults to when that nickname is blank —
the ordinary case until Apple resolves the opponent. (Tech Design → Online Play: "The device
that starts the match plays Player One in the first game of the series; the device that
accepts plays Player Two"; → A found match becomes a stored game, for the placeholder
fallback and for storage applying no fallback of its own.)

**R27.** That create is refused unless the arriving board is exactly one legal move from a
fresh series, judged by the same `evaluateReceivedTurn` the store's apply path uses, against
`newSeries()` with `playerTwo` as the local side. A board that arrives is replayed against
the rules engine before it is believed, and a create is the one arrival path with no stored
board to measure against — without this it is the one path where an arbitrary board is
stored unchecked. A refused create writes nothing. (Tech Design → Online Play: "A board that
arrives is replayed against the rules engine before it is believed".)

**R28.** The receiver calls `setOnlineOpponentName` once, with the opponent participant's
trimmed nickname, when **all three** hold: the event's match map is present and names that
nickname non-empty; the record's stored title is still the placeholder; and the trimmed
nickname differs from that title. If any fails, no store call is made at all — not a call
the store then refuses. This runs on every event that reaches step 7, whether or not a
payload was applied, and whether the record was just created or already held. A record whose
title is anything else is never renamed. (Tech Design → Persistence and
Serialization → What an online game adds to the record: "it takes the placeholder title and
is renamed exactly once, when the opponent resolves"; → A found match becomes a stored
game.) The stored title equalling the placeholder is the only signal available for "not yet
resolved", so an opponent whose real Game Center nickname is `ItSaMeMaRiO` is renamed to
itself — a no-op rename, not a defect.

**R29.** The receiver's work for one event is a callable entry point,
`Future<TurnEventOutcome> handleTurnEvent(TurnEvent event)`, which the subscription calls
and a test calls directly. Every outcome is a returned value, never a throw, and each one is
also published on a broadcast outcome stream. The values are distinct rather than one
failure carrying a message, because a caller that cannot tell a re-delivery from a corrupt
payload cannot behave differently on them: applied (with the record id), created (with the
record id), a re-delivery, each of the store's distinct refusals (not reachable, out of
turn, stale match, undecodable, unsupported version, no such record), refused at the cap
(carrying the ceiling and the count), refused as unreachable-from-a-fresh-series, undecodable
with no record to route it to, dropped as already quit, and ignored. `didBecomeActive` is
not among them — it is a fact the receiver reads off the event, not something that happened
to a game. Nothing in this feature renders any outcome; the stream is the seam the board
screen and the open-games list read. (Tech Design → Online Play: "Each is a distinct value
the caller can branch on rather than one failure carrying a message"; what the player is
told is an open question in that doc.)

**R30.** The receiver never creates a record the matchmaker path would also create. The two
cannot collide: `startOnlineGame` creates only on the starter path — no match data and the
local participant current — while R25 reaches its create only for an event that carries a
payload, and `createOnlineGame` for a match id a record already holds answers that record
back rather than creating a second one. (Tech Design → A found match becomes a stored game;
→ The cap is enforced on create.)

**R31.** An online game an invited player accepted becomes a stored game through this path
and no other: the acceptance stores nothing, and the record appears when the starter's first
payload lands. (Tech Design → The cap is enforced on create: "On the accepting device the
create happens when the starter's first payload lands, not when the invitation is
accepted"; Menus and UI → Play online → Where It Takes You: "The game turns up in the
open-games list once that first turn lands".)

### Sending a move

**R32.** The state layer gains one operation, `Future<SendTurnResult> sendTurn(recordId)`,
and it is the only caller of `endTurn`. It answers a sealed value and never throws:
`TurnSent`, `TurnSendFailed` (carrying a non-empty message), `TurnSendInFlight`,
`TurnNotOnline` (the session holds no online triple), `NoPendingMove` (nothing is waiting to
be handed off), and `TurnSentNotStored` (carrying the store's own refusal — see R33). The
board screen calls it; what that screen draws before, during and after is the next row's, not
this one's.

**R33.** On an online game, the local move is written to the store **only after Game Center
accepts the turn**. The confirming tap on an online game applies the move to the session
board and sets `pendingHandoff`, saves nothing, and calls `sendTurn`; `sendTurn` encodes the
session board with the record's series id and calls `endTurn` under **the session's held new
match id when one is present — a rematch in flight — and the record's stored match id
otherwise**. **Only on ok** is that board written, under the same match id it was sent
under: through the ordinary save path for a move, and through R46's next-game write for a
rematch handoff. `pendingHandoff` clears there and nowhere else. The match id is chosen once,
before the send, and the write reuses it rather than re-reading the record — re-reading is
what would let the send and the write disagree about which match the board belongs to.
A send Apple accepted whose write the store then refuses answers `TurnSentNotStored`,
carrying that refusal: `pendingHandoff` clears there too and the session keeps the board as
sent, because the turn is gone — the opponent has it, and re-sending would be a second
handoff of a board they already hold. It is unreachable whenever R46's validation and the
board actually sent agree, which is a property of this code rather than of anything a player
can do, so in practice it names a programmer error rather than a condition; it exists so that
"accepted but not stored" is a value a caller can see instead of a silent divergence between
the two devices. Tests pin it only by making the fake store refuse.
Nothing is written before the ok. A stored board that showed the opponent to move on a turn
this device never handed off would be a game neither device can continue, and it survives a
relaunch. *This decision is made here: Menus and UI → When a game is written to storage says
a game is written after every confirmed move, and says nothing about online play; the online
exception is not in any design doc and belongs in one at harvest.*

**R34.** When `endTurn` fails, nothing is written to the store, `pendingHandoff` stays set
with the confirmed board still on the session, and the session records that the last send
failed. `sendTurn` called again on that record re-sends the same board — a retry, not a
second move — so the same `TurnSent` path closes it. A relaunch loses the unsent move and
shows the board as it stood before it, which is what the opponent sees too.

**R35.** One send is in flight per record at a time; a second `sendTurn` for a record whose
send has not answered yet sends no platform call and answers `TurnSendInFlight`. (Same shape
as the in-flight guards on `authenticate` and `presentMatchmaker`, Tech Design → Signing in;
→ Presenting Apple's matchmaker.)

**R36.** The payload is produced by `encodeTurnPayload` with the record's stored series id
and the board being handed off, and by nothing else. `PayloadTooLargeError` is a defect in
this device's own data rather than an arriving condition, so it is not caught and turned
into a send failure. (Tech Design → Online Play: "The encoder refuses to produce a payload
over 48 KB, throwing rather than making a silent oversized send … Throwing is right here and
nowhere else in online play".)

**R37.** A rematch follows the same save-after-accept rule, and stores no marker to do it.
The initiator creates Apple's rematch, holds the new match id **in the session only**, hands
off the next game's board under that new match id — the fresh board, plus its own first move
if the engine says it goes first — and only on `ok` writes
`startNextOnlineGame(recordId, newMatchId, board: sentBoard)` (R46). The board that was sent
and the new match id land together in **one** write, so advancing to the next game and
pointing the record at the new match stays the single operation it is by contract; it just
happens after the handoff rather than before. On a failed send
nothing is written, the record still shows the finished game, and a retry re-sends on the
held new match id. **A relaunch loses the held id**: the player taps rematch again, Apple
mints another match, and the first one is abandoned with nothing stored pointing at it —
acceptable, because an abandoned match the player never played is invisible to both devices
and costs no slot. The board handed off may be the fresh board untouched; a zero-move
handoff is ordinary when the other side goes first. (Tech Design → Persistence and
Serialization: "Advancing to the next game and pointing the record at the new match is one
write"; → Online Play: "zero or one move, and both are ordinary".) Where `newMatchId` comes
from — Apple's rematch — is the game-over row's, not this one's.

**R42.** `GameSession` gains the record's online triple — match id, series id and which side
this device plays — set by `loadGame` and by the create paths from the record they read, and
absent on a local game. It gains `pendingHandoff`, `lastSendFailed` and the rematch's held
new match id alongside them: all three are session-only and none is persisted. The held new
match id is what R33 sends and writes under while it is present, and it is set only by the
rematch path and cleared by the write that consumes it — so an online game not in the middle
of a rematch has none, and both the send and the write fall back to the record's stored match
id. The confirm path branches on the triple's presence and
on nothing else, which is the same test the store already uses to tell an online record from
a local one. (Tech Design → Persistence and Serialization → What an online game adds to the
record: "The presence of that key is the only thing that tells an online game from a local
one"; → *Whose turn it is is not a stored field* — the side is read from the record, never
re-derived.)

**R43.** While `pendingHandoff` is true, the state layer refuses another move on that game:
`tapCell` answers a refusal value and changes nothing — no selection, no preview, no board.
A second move on a turn the first one has not handed off would produce a board two moves
ahead of the opponent's, which their device refuses as unreachable and nothing can repair.
The refusal is what makes R34's retry safe: the board `sendTurn` re-sends is provably the
one the player confirmed.

**R46.** `startNextOnlineGame` gains an optional `board` argument, and it is the one change
this feature makes to the store's surface. Without it the operation behaves exactly as it
does today — it stores `startNextGame(stored board)` with the new match id. With it, the
given board is stored with the new match id in the same single write, and it is validated
first, by this rule directly: **the given board must equal `startNextGame(stored board)`, or
be produced by exactly one legal move from it.** Legal moves are enumerated and applied, as
the receive rules do, never a board fed to the engine and its throw caught. No turn test runs
and no `localPlayer` is consulted — `evaluateReceivedTurn` is not reused here, because this
board is the initiator's own rather than one that arrived, and its turn and re-delivery
branches would refuse the ordinary case. A board that fails — two moves ahead, from another
series, anything unreachable — is refused with its own distinct value, alongside the two
refusals the operation already answers, and **nothing is written on a refusal**. The
operation still never throws. Without the argument the initiator would need a second write to
add the move it already sent, which is the one thing this operation exists to prevent. (Tech
Design → Persistence and Serialization: "Advancing to the next game and pointing the record
at the new match is one write … so a record can never sit with the next game's board under
the finished game's match id, or the reverse"; → Online Play: "zero or one move, and both are
ordinary".)

### The launch path

**R38.** Nothing about the receiver's wiring depends on how the app was launched: the
receiver subscribes at app start, the platform buffer replays whatever arrived before that,
and an event that launched the app is handled exactly as one that arrived while it was
running. `didBecomeActive` is carried through to the receiver and nothing branches on it —
Apple defines it as "this event launched or foregrounded the app", which is true of the
ordinary case too, so it is a fact about the event rather than anything a game can act on.

**R44.** The receiver is constructed at app start by the root widget — `App.build` in
`lib/app.dart` reads `turnEventReceiverProvider`, the same way it already reads the router
and the theme. Constructing it is what subscribes to `turnEvents` (R19) and therefore what
drains the platform buffer (R16), so the read is not incidental: nothing else in the app
reaches that provider, and without it every arriving turn would sit in the buffer unread.

**R39.** *(Proposed — not settled by any design doc; see Open Questions.)* The app calls
`authenticate` once at launch when, and only when, the store holds at least one online
record. Tech Design → Online Play settles that the app authenticates "when the app is opened
from a Game Center invite or a 'your turn' notification", and equally that sign-in does not
happen at cold launch and that "a player who never touches online play never sees Game
Center's sign-in banner". GameKit delivers the launching turn event only to a registered
listener, and part one registers that listener on the first successful authentication — so
without some launch-time trigger the notification path cannot work at all. Holding an online
game is the narrowest condition that satisfies both statements.

### Testing

**R40.** Everything on the Dart side is covered by `flutter test`, with no GameKit and no
device:

- The channel calls and their decode table, against a mock method-channel handler: the exact
  method names and argument keys sent, every reply shape in R6/R9, a reply that is not a
  map, a missing `status`, and a `MissingPluginException`.
- Turn-event decoding (R22), against a mock event-channel stream — including that a bad
  `match` map still yields a routable event and that a bad `matchId` does not.
- The receiver's whole routing table (R25–R31), driven through `handleTurnEvent` against
  `InMemoryGameRepository` and `FakeGameCenterBridge`: found by match id, found by series id,
  created, cap refusal, every `ApplyTurnResult` variant, the payload-carries-nothing branches,
  an undecodable payload with no record held, an event dropped for a quit local participant,
  the rename firing exactly once and making no store call when any of R28's three conditions
  fails, and a malformed event writing nothing.
- `sendTurn`'s ordering and the session's confirm path (R32–R35, R42, R43): that the
  repository sees no write until `endTurn` has answered ok, that a failure writes nothing and
  leaves `pendingHandoff` set, that re-sending after a failure sends the same board and then
  saves it, that a second move while `pendingHandoff` is set changes nothing, that a second
  send while one is in flight sends no platform call, and each of the six `SendTurnResult`
  values — `TurnSentNotStored` reachable only by making the fake store refuse a write the
  send had already succeeded at.
- The rematch order (R37, R42): that `startNextOnlineGame` is not called until the new
  match's `endTurn` has answered ok, that the send goes out under the held new match id
  rather than the record's stored one, and that the write lands under that same id.
- `startNextOnlineGame`'s new argument (R46), added to the shared contract battery every
  `GameRepository` implementation already runs — so `InMemoryGameRepository` and
  `HiveGameRepository` cannot drift on it: without a board (today's behaviour, unchanged);
  with a board equal to `startNextGame(stored)`; with that board plus one legal move; a board
  two moves ahead refused with the new value; and nothing written and nothing emitted on the
  change stream for any refusal.
- The delete flow (R45): that `resignMatch` is called for an online record and not for a
  local one, and that a failed resign still deletes.

**R41.** The Swift half carries no test target and is checked by running the app on a device
signed into Game Center (Tech Design → The channel contract). Device-only: that `endTurn`
actually advances the match and the opponent's device receives it; the buffer-and-replay
path on a launch from a your-turn notification; `resignMatch` in and out of turn, and what
the other device sees after one; that `localParticipantQuit` reads true on the other side
after a resign; and the matchmaker-window routing part one's device pass flagged (R15).

## Out of Scope

- **The board screen's behaviour on an online game** — input locked when it is not your
  turn, what a confirm looks like while a send is in flight, an arriving turn replacing the
  board under a pending selection. This PRD defines the seams it calls (`sendTurn`, the
  receiver's outcome stream) and nothing it draws. It is the next Ready row.
- **The open-games list's online states** — your turn, waiting, which games are online.
- **Game over and rematch** — reporting the outcome, ending the match with Apple, and what
  the rematch button does. R37 and R46 define only what the wire needs of
  `startNextOnlineGame`: the order of the handoff, and the board argument that keeps it one
  write.
- **Any player-facing message.** What is shown for a re-delivery, an unrecognised payload
  version, a failed send or a refused turn is unsettled in Tech Design → Open Questions →
  *Online play — what the player is told* and Menus and UI → Open Questions.
- **The delete confirmation and the open-games list's delete affordance**, which already
  exist (Menus and UI → Deleting an open game). R45 adds one call inside that flow and
  changes nothing a player sees.
- **The design docs themselves.** R1, R2, R12 and R33 each make a statement a design doc
  does not yet carry; recording them is `forge-doc-writer`'s at harvest.

## Open Questions

- **When a player deletes an online game, should the other player's copy end too (the
  delete resigns the match, so they see "game over" instead of waiting forever), or should
  it only leave this phone (their copy keeps waiting for a turn that never comes, until they
  delete it as well)?** (queue → Blocked, unanswered.) R12 and R45 build the first answer as
  the main loop's recorded assumption — reversing it removes one call and one test.
- **What triggers sign-in when the app is launched from a your-turn notification or an
  invite?** Tech Design → Online Play says the app authenticates then, and also that it does
  not authenticate at cold launch. R39 is this PRD's proposal — authenticate at launch only
  when an online game is stored — and is the author's, not the docs'.
- **Should a re-delivered identical board be visible to the player at all, or silently
  ignored?** (Tech Design → Open Questions → *Online play — what the player is told*.) The
  data side is settled; R29 makes the outcome observable and renders nothing.
- **What happens when a payload arrives carrying a version this build does not recognise,
  beyond the rejection itself — whether the player is told the other device is on a newer
  version, and whether that is distinguishable to them from a corrupt payload.** (Tech
  Design → Open Questions.)
- **What does the player see for a sign-in that fails or is declined, for a cancelled
  matchmaker, and for a GameKit error the bridge reports?** (Tech Design → Open Questions.)
  Extended by this feature to a send Game Center refused (R34), which no doc covers either.
- **What do the Play online messages say?** (Menus and UI → Open Questions.)
