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
receive rules already built; and a match can be resigned through one bridge operation
whose trigger is left to an unanswered question. The board screen, the open-games list and
the game-over flow are not built here; each gets the state-layer seam it calls.

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
for the first two covers the third. (Tech Design → Project Structure: "The two channel-name
strings are written in exactly one file on each side … and a scan test holds that".)

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

**R11.** The in-turn form is handed the match's own currently loaded match data, unchanged,
and `GKTurnTimeoutNone`. Resigning is not a move, so the board the other device sees must
not change — and GameKit's in-turn quit requires match data, so passing empty data here
would wipe the opponent's board.

**R12.** Nothing in this feature calls `resignMatch`. Deleting an online game does exactly
what it does today — it removes this device's record and touches Game Center not at all
(Tech Design → Persistence and Serialization: "Deleting removes one open game and its whole
series"). Whether a delete should resign the match is unanswered; see Open Questions.

### Turn events on the wire

**R13.** Every `player(_:receivedTurnEventFor:didBecomeActive:)` the registered
`GKLocalPlayerListener` receives is emitted on the turn event channel, as a map of exactly
four keys:

| Key | Value |
|---|---|
| `matchId` | the id the event was delivered under |
| `match` | the six-key match map part one already defines, built from this match |
| `matchData` | the match's loaded data as bytes, or null when the match holds none |
| `didBecomeActive` | GameKit's own flag, verbatim |

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
presentation — the first one still wins. (Part one's device-pass note, queue `Done.md`,
2026-09-15.)

**R16.** Events that arrive before Dart has subscribed to the turn channel are buffered and
replayed, in arrival order, on the first `onListen`. The buffer holds at most one event per
match id — the most recent — so it cannot grow without bound if Dart never subscribes, and
a superseded board for the same match is never worth replaying. Buffering resumes whenever
no subscriber is attached.

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

**R19.** `turnEvents` replays nothing on subscribe. A turn event is an occurrence, not a
value with a current state, so the session stream's replay behaviour is deliberately not
copied; what a late subscriber would have missed is covered by R16's platform-side buffer
instead.

**R20.** `EndTurnResult` and `ResignMatchResult` are each a sealed pair — an ok value and a
failed value carrying a non-empty message. Neither throws, for any outcome, on any build.
(R4.)

**R21.** `endTurn` and `resignMatch` called while the session is not
`GameCenterAuthenticated` answer their failed value and send no platform call, the same way
`presentMatchmaker` and `loadMatches` already refuse. Neither authenticates on the caller's
behalf. (Tech Design → Presenting Apple's matchmaker: "Neither the matchmaker nor a match
load signs the player in on the caller's behalf".)

**R22.** A turn event whose map violates any row of the decode table — not a map, a missing
or wrong-typed key, a `match` value that fails part one's match-map decode, an empty
`matchId` — is dropped, and nothing is emitted on `turnEvents`. Decoding is strict, per key
and all-or-nothing; nothing is coerced and no missing key is defaulted. (Tech Design → The
channel contract: "Decoding what arrives is strict, per key, and all-or-nothing … A
malformed event on the session channel is ignored".)

**R23.** `FakeGameCenterBridge` gains a way to push a turn event and to script the next
`endTurn` and `resignMatch` answers, and records both calls in its existing `calls` list, so
a caller's test can assert "sent no platform call" rather than merely stating it.

### The receiver

**R24.** One receiver in `lib/gamecenter/` subscribes to `turnEvents` and is the only
subscriber that writes to the store. It is reached through a provider of its interface, is
constructed once, and stays subscribed for the app's lifetime; a second live instance would
double-apply every arriving turn. (Tech Design → State Management.)

**R25.** For each event, in this order:

1. Read the record held for the event's match id (`readGameByMatchId`).
2. If one is held → `applyReceivedTurn(recordId: record.id, matchId: event.matchId,
   payload: event.matchData)`.
3. If none is held and the event carries no payload → nothing is applied; continue at
   step 6.
4. If none is held → decode the payload and read the record whose series is the payload's
   series id (`readGameBySeriesId`). If one is held → `applyReceivedTurn` against that
   record's id, with the event's match id. This is the rematch's fresh match id finding the
   record it belongs to.
5. If neither lookup holds a record → this is the first payload of a series this device does
   not hold, and it is created (R26).
6. Resolve the opponent's name (R28).

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

**R28.** When the event's match map carries a non-empty nickname for the opponent
participant and the record's stored title is still the placeholder, the receiver calls
`setOnlineOpponentName` once with that nickname. This runs on every well-formed event,
whether or not a payload was applied, and whether the record was just created or already
held. A record whose title is anything else is never renamed. (Tech Design → Persistence and
Serialization → What an online game adds to the record: "it takes the placeholder title and
is renamed exactly once, when the opponent resolves"; → A found match becomes a stored
game.) The stored title equalling the placeholder is the only signal available for "not yet
resolved", so an opponent whose real Game Center nickname is `ItSaMeMaRiO` is renamed to
itself — a no-op rename, not a defect.

**R29.** The receiver answers, and publishes on a broadcast stream, one value per event
naming what happened: applied (with the record id), created (with the record id), a
re-delivery, each of the store's distinct refusals (not reachable, out of turn, stale match,
undecodable, unsupported version, no such record), refused at the cap (carrying the ceiling
and the count), refused as unreachable-from-a-fresh-series, and ignored. It never throws.
Nothing in this feature renders any of them; that stream is the seam the board screen and
the open-games list read. (Tech Design → Online Play: "Each is a distinct value the caller
can branch on rather than one failure carrying a message"; what the player is told is an
open question in that doc.)

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

**R32.** The state layer gains one operation, `sendTurn(recordId)`, and it is the only
caller of `endTurn`. The board screen calls it; what the screen draws before, during and
after is the next row's, not this one's.

**R33.** On an online game, the local move is written to the store **only after Game Center
accepts the turn**. The sequence for a confirmed move is: hold the confirmed board in the
session → encode it with the record's series id → `endTurn` → on ok, save the confirmed
board through the ordinary save path. Nothing is written before the ok. A stored board that
showed the opponent to move on a turn this device never handed off would be a game neither
device can continue, and it survives a relaunch. *This decision is made here: Menus and UI →
When a game is written to storage says a game is written after every confirmed move, and
says nothing about online play; the online exception is not in any design doc and belongs in
one at harvest.*

**R34.** When `endTurn` fails, nothing is written to the store, the confirmed board stays in
the session marked as not handed off, and the outcome is readable from the state layer so a
screen can say so and offer the move again. A relaunch therefore shows the board as it stood
before the move — which is what the opponent sees too.

**R35.** One send is in flight per record at a time; a second `sendTurn` for a record whose
send has not answered yet sends no platform call and answers as already in flight. (Same
shape as the in-flight guards on `authenticate` and `presentMatchmaker`, Tech Design →
Signing in; → Presenting Apple's matchmaker.)

**R36.** The payload is produced by `encodeTurnPayload` with the record's stored series id
and the board being handed off, and by nothing else. `PayloadTooLargeError` is a defect in
this device's own data rather than an arriving condition, so it is not caught and turned
into a send failure. (Tech Design → Online Play: "The encoder refuses to produce a payload
over 48 KB, throwing rather than making a silent oversized send … Throwing is right here and
nowhere else in online play".)

**R37.** For a rematch, the order is reversed: `startNextOnlineGame(recordId, newMatchId)`
is written first, and `sendTurn` then hands off the stored next-game board under the new
match id and the same series id. Advancing to the next game and pointing the record at the
new match is one write by contract, so it cannot be deferred behind an `endTurn`. A failed
send there leaves the record on the new match with the fresh board and is retried; unlike a
lost move, nothing the player did is lost. The board handed off may be the fresh board
untouched — a zero-move handoff is ordinary when the engine says the other side goes first.
(Tech Design → Persistence and Serialization: "Advancing to the next game and pointing the
record at the new match is one write"; → Online Play: "zero or one move, and both are
ordinary".) Where `newMatchId` comes from — Apple's rematch — is the game-over row's, not
this one's.

### The launch path

**R38.** Nothing about the receiver's wiring depends on how the app was launched: the
receiver subscribes at app start, the platform buffer replays whatever arrived before that,
and an event that launched the app is handled exactly as one that arrived while it was
running. `didBecomeActive` is carried through to the receiver's published outcome and
nothing branches on it — Apple defines it as "this event launched or foregrounded the app",
which is true of the ordinary case as well.

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
- Turn-event decoding (R22), against a mock event-channel stream.
- The receiver's whole routing table (R25–R31), against `InMemoryGameRepository` and
  `FakeGameCenterBridge`: found by match id, found by series id, created, cap refusal,
  every `ApplyTurnResult` variant, the rename firing exactly once and not at all on a
  non-placeholder title, and a malformed event writing nothing.
- `sendTurn`'s ordering (R33–R35): that the repository sees no write until `endTurn` has
  answered ok, that a failure writes nothing, and that a second send while one is in flight
  sends no platform call.

**R41.** The Swift half carries no test target and is checked by running the app on a device
signed into Game Center (Tech Design → The channel contract). Device-only: that `endTurn`
actually advances the match and the opponent's device receives it; the buffer-and-replay
path on a launch from a your-turn notification; `resignMatch` in and out of turn; and the
matchmaker-window routing part one's device pass flagged (R15).

## Out of Scope

- **The board screen's behaviour on an online game** — input locked when it is not your
  turn, what a confirm looks like while a send is in flight, an arriving turn replacing the
  board under a pending selection. This PRD defines the seams it calls (`sendTurn`, the
  receiver's outcome stream) and nothing it draws. It is the next Ready row.
- **The open-games list's online states** — your turn, waiting, which games are online.
- **Game over and rematch** — reporting the outcome, ending the match with Apple, and what
  the rematch button does. R37 defines only what `startNextOnlineGame` needs from the wire.
- **Any player-facing message.** What is shown for a re-delivery, an unrecognised payload
  version, a failed send or a refused turn is unsettled in Tech Design → Open Questions →
  *Online play — what the player is told* and Menus and UI → Open Questions.
- **Changing what deleting a game does**, and any resign trigger (R12).
- **The design docs themselves.** R1, R2 and R33 each make a statement a design doc does
  not yet carry; recording them is `forge-doc-writer`'s at harvest.

## Open Questions

- **When a player deletes an online game, should the other player's copy end too (the
  delete resigns the match, so they see "game over" instead of waiting forever), or should
  it only leave this phone (their copy keeps waiting for a turn that never comes, until they
  delete it as well)?** (queue → Blocked, unanswered.) R9–R11 build the operation either
  answer needs; R12 leaves it uncalled.
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
