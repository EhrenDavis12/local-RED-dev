# PRD: Game Center bridge, part one — authenticate, session state, find a player

> **Status:** Draft · Source docs read: Tech Design (Project Structure, State Management,
> Navigation, Persistence and Serialization, Online Play, Kids Category, Testing,
> Distribution and Release), Menus and UI (Play Game → Where It Takes You, How many open
> games we keep, Open Questions), queue/Done.md (the Game Center research rows verified
> 2026-09-12 and 2026-09-14), plus the worktree's `lib/`, `ios/Runner/`, `RELEASE.md`.

## Problem

Online play is decided — remote turn-based play over Apple Game Center, Apple holding the
match, the matchmaking, the identity and the "your turn" push ([Tech Design](../Tech%20Design.md)
→ Online Play). The store already knows how to hold an online game: `createOnlineGame`,
`readGameByMatchId`, `applyReceivedTurn` and the rest are built and tested. But nothing in
the app has ever spoken to GameKit. There is no Swift bridge, no Dart interface over it, and
no way to learn who the player is, whether their account may play multiplayer at all, or to
put Apple's find-a-player sheet on screen. Every later online row — the Play online button,
sending a turn, receiving one, the open-games reconcile — calls this contract, so all of
them are blocked on it and all of them would otherwise each invent their own half of it.

## Goal

The app can ask Apple who the player is, hold that answer as app state anything can read, put
Apple's turn-based matchmaker on screen, and turn the match that comes back into a stored
online game — through one Dart interface with a fake behind it, over one Swift platform
channel whose method names and argument shapes are written down in one place. When this is
done, a later row that needs Game Center adds a call to an existing contract instead of
designing one.

## Requirements

### Where the code lives

**R1.** The channel-facing Dart lives in its own layer folder, `lib/gamecenter/`, and not in
`lib/online/`. [Tech Design](../Tech%20Design.md) → Online Play requires `lib/online/` to
import no platform channel, and → Project Structure groups by kind, one folder per layer, so
the bridge is a layer of its own. (The folder *name* is this PRD's choice; no doc names one —
see Open Questions.)

**R2.** `lib/online/`'s existing purity scan (`test/online/purity_scan_test.dart`) stays green
unchanged — no file this feature adds to `lib/online/` imports a platform channel, Flutter,
`dart:ui` or Hive. The series-id minter (R32) does go there and imports `dart:math` only.
Source: [Tech Design](../Tech%20Design.md) → Project Structure, Online Play.

**R3.** The two channel-name strings (R4) appear in exactly one Dart file under `lib/`, which
is in `lib/gamecenter/`, and in exactly one Swift file under `ios/Runner/`. Nothing else in
the app constructs a channel to GameKit. Source: [Tech Design](../Tech%20Design.md) → Online
Play ("the GameKit calls are written in Swift on the iOS side and reached from Dart over a
channel") — one channel, one place, is what keeps the string contract in R5–R12 checkable.

### The channel contract — the one place a string contract crosses languages

**R4.** Two channels, named exactly:

| Channel | Name | Direction |
|---|---|---|
| `MethodChannel` | `com.ehrendavis.tictactoeextreme/gamecenter` | Dart → Swift, replies |
| `EventChannel` | `com.ehrendavis.tictactoeextreme/gamecenter/session` | Swift → Dart |

The prefix is the bundle identifier settled in [Tech Design](../Tech%20Design.md) →
Distribution and Release → Bundle identifier. Both use Flutter's standard message codec; no
custom codec. Hand-written channels, not pigeon or any other generator: every package
dependency this app takes is a decision recorded in [Tech Design](../Tech%20Design.md)
(`go_router`, `hive_ce`, `audioplayers`, `in_app_purchase`), and none records a channel
generator — see Open Questions.

**R5.** The method channel exposes exactly three methods, all taking no arguments:
`authenticate`, `presentMatchmaker`, `loadMatches`. Any other method name answers
`FlutterMethodNotImplemented`.

**R6.** `authenticate` replies with a **session map**:

```
{ "state": "unauthenticated" | "authenticating" | "authenticated" | "restricted",
  "nickname": String,     // present only when state == "authenticated"
  "isUnderage": bool }    // present when state == "authenticated" or "restricted"
```

`restricted` is what `GKLocalPlayer.isMultiplayerGamingRestricted` being true reports, and
`isUnderage` is `GKLocalPlayer.isUnderage`. Sources: [Tech Design](../Tech%20Design.md) →
Online Play (restricted → online play is not offered) and → Kids Category (`isUnderage` is
what decides whether the parental gate is raised).

`"authenticating"` never appears in a *method* reply — it is an event-channel-only value
(R7). A reply carrying it is handled by R15 like any other unrecognised state.

**R7.** The event channel emits the same session map (R6): the current value immediately on
subscription, and every later change after that. **Subscribing installs nothing and asks
GameKit nothing.** `GKLocalPlayer.authenticateHandler` is installed on the first
`authenticate()` call and never on a listen, so a subscription presents no sign-in view
controller and shows no banner — which matters because the provider (R20) may subscribe at
any time, including at app launch. Before that first `authenticate()` the channel replays
`unauthenticated` on subscribe and reports nothing else. After it, a change GameKit
originates with no Dart call behind it — the player signing out in iOS Settings — arrives
through that handler and is emitted here. It never emits an error event. Source:
[Tech Design](../Tech%20Design.md) → Online Play ("A player who never touches online play
never sees Game Center's sign-in banner"), which a listen-installed handler would break.

**R8.** `presentMatchmaker` replies with:

```
{ "status": "found" | "cancelled" | "failed",
  "match": <match map>,   // present only when status == "found"
  "message": String }     // present only when status == "failed"
```

**R9.** `loadMatches` replies with:

```
{ "status": "ok" | "failed",
  "matches": [ <match map>, … ],   // present only when status == "ok"; may be empty
  "message": String }              // present only when status == "failed"
```

**R10.** A **match map** is exactly these keys:

```
{ "matchId": String,
  "status": "matching" | "open" | "ended" | "unknown",
  "participants": [ { "nickname": String, "isLocalPlayer": bool }, … ],
  "localParticipantIndex": int,      // index into participants
  "currentParticipantIndex": int?,   // null when the match has no current participant
  "hasData": bool }                  // whether the match carries any turn data yet
```

`participants` is in GameKit's own order, which is the order turns rotate in. A participant
whose player Apple has not resolved carries the empty string as its nickname — which is the
ordinary case for a Play Now match, whose `status` is `matching` and whose opponent does not
exist yet (R45). `hasData` is true only when GameKit's `matchData` is **both non-nil and
non-empty**: a freshly created match carries one or the other depending on the path that
created it, and telling those apart would make R30's starter test depend on which path ran.
`currentParticipantIndex` is "whose turn"; the board's own current player is engine state and
is never derived from it ([Tech Design](../Tech%20Design.md) → Persistence and Serialization
→ What an online game adds to the record: "Whose turn it is is engine state and is never
derived a second way"). The turn *data* itself is not carried here — part two adds a key for
it, additively, and both sides of this channel ship in one binary so that costs nothing.

**R11.** The Swift side never replies with a `FlutterError` for any outcome named in R6, R8
or R9 — a cancelled matchmaker, a failed sign-in, a restricted account and a GameKit error
are all reply *values*. Source: [Tech Design](../Tech%20Design.md) → Online Play and →
Persistence and Serialization, which make every outcome a caller can act on a returned value
rather than a throw, in both the receive path and the store.

**R46.** Every `message` string a failure value carries is non-empty — the ones that arrive
over the channel (R8, R9) and the ones the Dart side originates itself (R14's mapped
exceptions, R25's second presentation) alike. No test pins any wording — a caller branches on
the value, never on the text, and nothing renders it to a player in this feature (see Out of
Scope).

**R12.** The Swift side performs no GameKit work until a Dart call arrives: registering the
channel does not set an authenticate handler, does not present anything, and does not touch
`GKLocalPlayer`. The channel is registered in `ios/Runner/AppDelegate.swift`, alongside the
generated plugin registrant, and the matchmaker is presented from the key window's root view
controller. Source: [Tech Design](../Tech%20Design.md) → Online Play ("Game Center sign-in
happens when the player first enters online play, not at cold launch. … A player who never
touches online play never sees Game Center's sign-in banner").

R5's method-not-implemented behaviour and this requirement are Swift-side facts: both are
covered by the device pass (R40–R41) and by nothing in `flutter test`. Part two revises this
requirement when it installs `GKLocalPlayerListener`.

### The Dart interface

**R13.** `lib/gamecenter/` publishes this surface, and every caller in the app depends on the
interface rather than on either implementation:

```dart
sealed class GameCenterSession {}
class GameCenterUnauthenticated extends GameCenterSession {}   // const
class GameCenterAuthenticating  extends GameCenterSession {}   // const
class GameCenterAuthenticated   extends GameCenterSession {
  final String nickname;
  final bool isUnderage;
}
class GameCenterRestricted      extends GameCenterSession {
  final bool isUnderage;
}

class GameCenterParticipant { final String nickname; final bool isLocalPlayer; }
class GameCenterMatch {
  final String matchId;
  final GameCenterMatchStatus status;       // matching | open | ended | unknown
  final List<GameCenterParticipant> participants;
  final int localParticipantIndex;
  final int? currentParticipantIndex;
  final bool hasData;
}

sealed class MatchmakerResult {}
class MatchFound            extends MatchmakerResult { final GameCenterMatch match; }
class MatchmakerCancelled   extends MatchmakerResult {}
class MatchmakerFailed      extends MatchmakerResult { final String message; }
class MatchmakerUnavailable extends MatchmakerResult { final GameCenterSession session; }

sealed class LoadMatchesResult {}
class MatchesLoaded     extends LoadMatchesResult { final List<GameCenterMatch> matches; }
class MatchesLoadFailed extends LoadMatchesResult { final String message; }

abstract class GameCenterBridge {
  Stream<GameCenterSession> get sessions;      // broadcast; replays current on listen
  GameCenterSession get current;               // the last value; never null
  Future<GameCenterSession> authenticate();
  Future<MatchmakerResult> presentMatchmaker();
  Future<LoadMatchesResult> loadMatches();
}
```

**R14.** Nothing on `GameCenterBridge` throws in any outcome named above — a missing platform
implementation included. On a build with no Swift side (`MissingPluginException`) and on any
`PlatformException`, `authenticate()` answers `GameCenterUnauthenticated`,
`presentMatchmaker()` answers `MatchmakerFailed`, and `loadMatches()` answers
`MatchesLoadFailed`. Same source as R11.

**R15.** Decoding is strict and per key, with no coercion — no `toString()`, no numeric
parsing, no defaulting a missing key. A reply that is not a map, or that violates any row
below, is treated as the failure value for that call, whole: `GameCenterUnauthenticated` for
a session reply, `MatchmakerFailed` for `presentMatchmaker`, `MatchesLoadFailed` for
`loadMatches`. Never a throw, and never a partially-filled value — one bad participant fails
the whole `loadMatches` reply rather than yielding a list with a hole in it.

| Where | Key | Must be | Violation |
|---|---|---|---|
| session map | `state` | String, one of `unauthenticated`, `authenticating`, `authenticated`, `restricted` | `GameCenterUnauthenticated` |
| session map, `state == "authenticated"` | `nickname` | String, present; may be empty | `GameCenterUnauthenticated` |
| session map, `state == "authenticated"` | `isUnderage` | bool, present | `GameCenterUnauthenticated` |
| session map, `state == "restricted"` | `isUnderage` | bool, present | `GameCenterUnauthenticated` |
| match map | `matchId` | String, non-empty | `MatchmakerFailed` / `MatchesLoadFailed` |
| match map | `status` | String, one of `matching`, `open`, `ended`, `unknown` | same |
| match map | `participants` | List of Maps, each with `nickname` String (may be empty) and `isLocalPlayer` bool | same |
| match map | `participants` | exactly two entries, exactly one of them `isLocalPlayer == true` | same |
| match map | `localParticipantIndex` | int, a valid index into `participants` | same |
| match map | `currentParticipantIndex` | int, a valid index into `participants`, or null | same |
| match map | `hasData` | bool, present | same |

A method reply carrying `state: "authenticating"` is an unrecognised state for a reply (R6)
and decodes to `GameCenterUnauthenticated`. That does not touch R17: the in-flight
`GameCenterAuthenticating` value is published by the Dart side before the call goes out, not
read off a reply.

**R42.** An error or a close on the event channel — including no Swift side at all
(`MissingPluginException`, which is every `flutter test` run) — leaves the last known session
value standing, `GameCenterUnauthenticated` when there has been none, and surfaces nothing:
no throw, no error on `sessions`, no change of value. Same source as R11 and R14.

### Session state and its provider

**R16.** The session starts at `GameCenterUnauthenticated` and reaches any other value only
through `authenticate()` or an event on the session channel. Constructing the bridge,
subscribing to `sessions`, reading the provider, building any widget, and app launch itself
all leave it at `GameCenterUnauthenticated`. Source: [Tech Design](../Tech%20Design.md) → Online Play
(sign-in on entering online play, not at cold launch).

**R17.** `authenticate()` moves the session to `GameCenterAuthenticating` before the platform
call goes out, and then to exactly one of `GameCenterAuthenticated`,
`GameCenterRestricted` or `GameCenterUnauthenticated`. Every value it passes through is
published on `sessions`.

**R18.** `authenticate()` is idempotent and safe to call any number of times: a second call
while one is in flight returns the same in-flight future and sends no second platform call,
so at most one sign-in view controller is ever presented. A call made when the session is
already `GameCenterAuthenticated` or `GameCenterRestricted` still calls the platform (GameKit
answers from its cached local player) but must not present anything a second time — which is
what makes the two entry points in R19 safe to wire independently.

**R19.** The app authenticates on exactly two occasions and no others: the tap that enters
online play, and the app being opened from a Game Center invite or "your turn" notification.
**This is a constraint on part one, not a deliverable of it.** Part one ships no notification
hook, no launch-from-invite path and no entry point beyond `authenticate()` itself; what it
owes is that `authenticate()` is callable before the first frame and before any screen
exists, so whatever handles external entry in part two can call it. `GKLocalPlayerListener`
and the launch path are part two's, and nothing here is asserted in `flutter test`. Source:
[Tech Design](../Tech%20Design.md) → Online Play ("the app authenticates on the tap that
enters online play, and again when the app is opened from a Game Center invite or a 'your
turn' notification, since that is entering online play from outside") and → Navigation → Deep
links are possible, not wired (external entry arrives through GameKit, not as a URL).

**R20.** The session is readable from anywhere through a Riverpod `NotifierProvider` holding
a plain `GameCenterSession` — never an `AsyncValue` a consumer has to branch on, because
`GameCenterAuthenticating` is already the in-flight value. The provider subscribes to
`sessions` and republishes every value. The bridge itself is reached through a `Provider`,
defaulting to the channel-backed implementation and overridable with the fake. Sources:
[Tech Design](../Tech%20Design.md) → State Management (`Notifier`/`NotifierProvider`, no
Riverpod codegen; readable from everywhere) and → In-App Purchases and Entitlements → The
entitlement provider's shape (a plain value with an in-flight indication, not an async
wrapper every consumer must branch on). Both providers live in `lib/gamecenter/`, the way
`gameThemeProvider` lives in `lib/theme/` and `audioServiceProvider` in `lib/audio/`.

**R43.** `sessions` is a broadcast stream: any number of listeners may subscribe at any time,
each one is replayed the current value on subscribe, and a listener cancelling affects no
other and tears nothing down. `current` answers the same value that the last subscriber would
be replayed. The fake (R36) behaves identically — a caller's test must not be able to tell
the two apart on this. A single-subscription stream would make the provider and any second
reader mutually exclusive, which is what this forbids.

**R21.** `GameCenterRestricted` is a state of its own and not a flag on
`GameCenterAuthenticated`, so a caller deciding whether to offer online play branches on the
state rather than on a boolean it can forget to read — the same shape the engine's placement
state uses ([Tech Design](../Tech%20Design.md) → The Rules Engine → Three placement states).
What the player is told instead is not this feature's — see Out of Scope.

### The matchmaker

**R22.** `presentMatchmaker()` presents `GKTurnBasedMatchmakerViewController` over a
`GKMatchRequest` with `minPlayers` 2 and `maxPlayers` 2, and **never sets a matchmaking
mode** — Apple's default stands, and automatch-only is never forced. Sources:
[Tech Design](../Tech%20Design.md) → Online Play ("The app never forces automatch-only mode —
that throws for a friends-only child, and it never imposes a restriction Apple has not") and
queue/Done.md, the 2026-09-14 research row ("The bridge must not force 'random opponent only'
mode … it uses Apple's default mode and lets the sheet show what's allowed").

**R23.** `presentMatchmaker()` called while the session is not `GameCenterAuthenticated`
answers `MatchmakerUnavailable` carrying the current session, presents nothing, and sends no
platform call. It does not authenticate on the caller's behalf — sign-in is R19's two
occasions and nothing else.

**R24.** The three outcomes Apple's sheet produces map to `MatchFound`,
`MatchmakerCancelled` and `MatchmakerFailed`, and they are distinct values rather than one
failure carrying a message, because a caller that cannot tell a cancel from an error cannot
behave differently on them ([Tech Design](../Tech%20Design.md) → Online Play, on the receive
path's enumerated outcomes).

**R25.** Only one matchmaker presentation is in flight at a time, and **the guard is in
Dart**: a second `presentMatchmaker()` while one is in flight resolves `MatchmakerFailed`
with no platform call made at all, which is what makes it assertable in `flutter test`. The
Swift side additionally refuses to present a second sheet, as a backstop covered by the
device pass. No doc states this; that two sheets must not stack is not a judgement call, but
*which* value the second call gets is, and this is the PRD's pick over queueing it.

### Loading the player's matches

**R26.** `loadMatches()` answers every turn-based match Apple currently holds for the local
player (`GKTurnBasedMatch.loadMatches`), as match maps (R10), **in whatever order GameKit
answers them**. The order is unspecified and no test asserts one; this feature imposes none
of its own and nothing may depend on it. It reads only; it creates, stores,
reconciles and deletes nothing. Reconciling them against the open-games list is a later row
(see Out of Scope).

**R27.** `loadMatches()` called while the session is not `GameCenterAuthenticated` answers
`MatchesLoadFailed` and sends no platform call.

### Match found → the stored online game

**R28.** The handoff is one named operation in `lib/gamecenter/` that takes a
`GameCenterMatch` and a `GameRepository` and answers:

```dart
sealed class StartOnlineGameResult {}
class OnlineGameStarted           extends StartOnlineGameResult { final GameRecord record; }
class OnlineGameAwaitingFirstTurn extends StartOnlineGameResult {}
class OnlineGameRefusedAtCap      extends StartOnlineGameResult {
  final int ceiling; final int currentCount;
}
class OnlineGameRefusedEmptyTitle extends StartOnlineGameResult {}
```

It never throws. The series-id minter is a parameter with a real default, so a test can assert
the exact value handed to the store.

**R29.** A match whose `matchId` the store already holds (`readGameByMatchId`) answers
`OnlineGameStarted` with that existing record. Nothing is created, nothing is re-titled, and
no series id is minted. Source: [Tech Design](../Tech%20Design.md) → Persistence and
Serialization → The cap is enforced on create ("Creating an online game for a match id a
record already holds is not a second create. The existing record is answered back
unchanged"). This is the matchmaker-selected-an-existing-match case.

**R30.** For a match the store does not hold, **this device is the starter exactly when the
match carries no data yet and the local participant is the current participant**
(`hasData == false && localParticipantIndex == currentParticipantIndex`). Source:
[Tech Design](../Tech%20Design.md) → Online Play ("Game Center makes the match's creator the
current participant, so the creator moves first").

**R31.** As the starter, the handoff calls `createOnlineGame` with exactly these arguments:

| Argument | Value |
|---|---|
| `opponentName` | the nickname of the one participant whose `isLocalPlayer` is false — which always exists, by R15's two-participants row — trimmed; `defaultOpponentName` (`lib/state/game_controller.dart`) when that is empty or whitespace-only — the ordinary Play Now case, see R45 |
| `board` | `newSeries()` from the engine |
| `matchId` | the match's `matchId` |
| `seriesId` | freshly minted here, on this call |
| `localPlayer` | `Player.playerOne` |

Sources: [Tech Design](../Tech%20Design.md) → Persistence and Serialization → What an online
game adds to the record ("Creating an online game takes the opponent's nickname, the starting
board, the match id, the series id and this device's side — all five from the caller. … it
mints no series id"); → Online Play ("The series id … has exactly two sources: the device that
**starts** the match mints it" and "The device that starts the match plays Player One in the
first game of the series"); [Menus and UI](../Menus%20and%20UI.md) → Play Game ("An online
game is titled with the opponent's Game Center nickname, taken when the match is created").
The blank-nickname fallback is this PRD's — no doc addresses a blank nickname; see Open
Questions. The handoff importing `defaultOpponentName` from `lib/state/` is accepted rather
than duplicating the constant: it is the one place the app's default title is written down,
and a second copy is a second answer.

**R32.** The series id is **32 lowercase hex characters, from 128 bits of `Random.secure()`**
— no new package dependency, and no dependence on a clock a test may freeze. The minter is a
pure-Dart function in `lib/online/`, which is where the payload that carries a series id
across the wire already lives, and it imports nothing that layer's purity scan forbids
(`dart:math` only). Tests assert the format and that 10,000 mints collide zero times. The id
stays opaque, never parsed and never displayed, and it has to be unique across devices — not
merely within this process — because the accepting device copies it out of the first payload
and both devices then hold it. Source: [Tech Design](../Tech%20Design.md) → Online Play.
`mintGameId()` in `lib/storage/` does not satisfy "unique across devices" and is not reused
here.

**R33.** A match the store does not hold and this device did not start — an accepted invite
with no data yet, or a match already carrying the opponent's data — answers
`OnlineGameAwaitingFirstTurn`, and nothing is stored. Source:
[Tech Design](../Tech%20Design.md) → Persistence and Serialization → The cap is enforced on
create ("On the accepting device the create happens when the starter's first payload lands,
not when the invitation is accepted — before that there is no board to store"). The path that
does that storing is part two.

**R34.** The store's two refusals reach the caller as distinct values:
`GameCreateRefused` → `OnlineGameRefusedAtCap`, carrying the ceiling and the current count so
a caller can say "3 of 3" without a second round trip; `GameCreateRefusedEmptyTitle` →
`OnlineGameRefusedEmptyTitle`. Neither is a throw, and neither is collapsed into the other.
Sources: [Tech Design](../Tech%20Design.md) → Persistence and Serialization ("Reaching the cap
is an ordinary, player-reachable condition, not an error"; the empty-title refusal "is
distinct from the cap refusal so the caller can tell the two apart") and
[Menus and UI](../Menus%20and%20UI.md) → How many open games we keep ("Online games count
against the same cap"). What the player is *offered* at the cap is unsettled — see Open
Questions.

**R35.** The handoff performs exactly one store write on the starter path and none on any
other path. In particular `OnlineGameAwaitingFirstTurn`, both refusals and the
already-held case write nothing.

### A deliberate exception to "an online game is never renamed"

A Play Now match comes back from Apple's sheet **before the opponent exists** — `status` is
`matching`, and the other participant carries no player and so no nickname. The starter still
has to take the first turn from the board screen, so the record has to exist now, which means
it has to be titled now, with a name Game Center cannot yet supply. That is why the rule in
[Tech Design](../Tech%20Design.md) → Persistence and Serialization ("The opponent name is set
at create and a save never changes it"; "An online game's name is the opponent's Game Center
nickname, captured when the match is created") gains one narrow exception here. It is
recorded as an exception rather than a softening of the rule: a save still never renames, and
this is the only operation that does. To be landed in the design docs at harvest.

**R44.** `GameRepository` gains one operation for that rename — e.g.
`setOnlineOpponentName(String recordId, String nickname)` — with these rules, and it is the
only way a stored title ever changes:

- It is allowed on an **online** record only: a record with no `online` values held answers
  the same "nothing stored" value an id the store never held gets, and writes nothing.
- An empty or whitespace-only `nickname` is refused, distinctly from "nothing stored", and
  writes nothing — the same shape the online create's empty-title refusal already has
  ([Tech Design](../Tech%20Design.md) → Persistence and Serialization: "The storage layer
  applies no name fallback").
- Every outcome is a returned value; it never throws.
- A successful rename touches the title and nothing else: the board, the three `online`
  values, the created timestamp and the record id are all unchanged. It stamps the updated
  timestamp, moves the record to the top of `readAllGames`'s order, and emits on
  `GameRepositoryChanges.changes`, exactly as any save does. A refusal emits nothing, because
  nothing changed.
- Both shipped implementations (`InMemoryGameRepository`, `HiveGameRepository`) implement it,
  and it is asserted in the shared repository test battery both already run, so the two
  cannot answer it differently.

**R45.** A starter's match whose opponent has not resolved is created exactly as R31 says,
with `defaultOpponentName` as the title — a placeholder, not a chosen name — and is renamed
exactly once, through R44, when the opponent resolves, to the nickname Game Center then
reports. Nothing else in the app calls that rename; it exists for this one case. Noticing the
resolution and making the call is **part two's**: it arrives on the turn event that carries
the resolved participants (see Out of Scope). Part one ships the operation, not its trigger.

### The fake

**R36.** `FakeGameCenterBridge` implements `GameCenterBridge` with no platform channel, and
every test of a caller uses it rather than the channel. It supports:

- scripting the session value each `authenticate()` call resolves to, in order, including a
  call that leaves the session unauthenticated;
- pushing a session value onto `sessions` with no `authenticate()` call, so R7's
  signed-out-in-Settings case is assertable;
- scripting the `MatchmakerResult` and `LoadMatchesResult` each call answers;
- holding a call unresolved, so R18's in-flight case and R25's second-presentation case are
  assertable;
- recording every call made to it, in order, so "presented nothing" and "sent no platform
  call" in R23, R25 and R27 are assertable rather than merely stated. (R12 is Swift-side and
  R30 is a rule about the handoff, not about the bridge; neither is asserted through the
  fake.)

**R37.** The fake lives under `lib/gamecenter/`, not under `test/`, because it is the double
callers in other layers test against. It holds no test-only shortcut that the real bridge
cannot honour.

### What is testable where

**R38.** Every requirement from R13 to R37 **except R19** is asserted in `flutter test`,
along with R42–R46: the Dart side against `FakeGameCenterBridge`, and the channel
encode/decode (R4–R11, R14, R15, R46) against a mock handler installed with
`TestDefaultBinaryMessengerBinding` — the pattern already used in
`test/audio/fake_audioplayers_platform.dart` and across `test/navigation/`. The handoff
(R28–R35, R45) is asserted against `InMemoryGameRepository`, and R44 in the shared repository
battery both implementations run. R19 is a constraint on what part one does *not* build and
has nothing to assert. Source: `project.json` → testing (`flutter test`),
[Tech Design](../Tech%20Design.md) → Testing.

**R39.** R3 is asserted by a scan test, in the same shape as the existing purity scans: the
channel-name strings occur in exactly one file under `lib/`.

**R40.** The Swift side is verified by a device pass and by nothing automated: no Swift test
target is added, and no test asserts that GameKit authenticates, that the sign-in or
matchmaker view controllers present, that R5 answers `FlutterMethodNotImplemented`, that R12
holds, that R25's Swift backstop refuses a second sheet, or what a real account's restricted
and underage flags say. Source: [Tech Design](../Tech%20Design.md) → Distribution and Release → CI — local builds
only, and → Testing (`flutter test` is the suite; appearance and platform behaviour are
checked by running the app). The Game Center capability, entitlement and provisioning profile
this needs are already live — `RELEASE.md` → Game Center.

**R41.** The device pass covers, on a real device signed into Game Center: sign-in presenting
and completing; the matchmaker sheet appearing and offering both Play Now and Invite Friends;
a match created through it producing a stored online game titled with the opponent's
nickname (or the placeholder title, on a Play Now match — R45); cancelling the sheet storing
nothing; and `loadMatches` answering the match just created. A child account run covers the
underage and restricted flags.

**R47.** A throwaway debug entry point may be added to drive that pass — a temporary button
or a debug-only call site that invokes `authenticate()`, `presentMatchmaker()` and
`loadMatches()`. It is not shipped: it is removed before the branch is merged, and no
requirement here depends on it. The real entry point is the "Play online" control, which is
part two's (see Out of Scope).

## Out of Scope

Part two and later rows, none of which this feature may preclude:

- Ending a turn with the board, and receiving the opponent's turn — including the inherited
  rule from the online-game record's close-out that **the bridge saves the local move only
  after Game Center accepts the turn**, so a stored board never shows the opponent to move on
  a turn this device did not hand off. Nothing here writes a move at all, so nothing here
  precludes it.
- `GKTurnTimeoutNone` — turns never time out ([Tech Design](../Tech%20Design.md) → Online
  Play). That is set where a turn is ended, which is part two.
- `GKLocalPlayerListener`, the launch-from-invite and launch-from-notification paths, and the
  call to `authenticate()` from them (R19). Part two revises R12 when it installs the
  listener.
- Noticing that a Play Now opponent has resolved, and calling R44's rename — it arrives on
  the turn event that carries the resolved participants. Part one ships the operation only.
- Quit, resign, and deleting an online game.
- The "Play online" button, the online screens, and whatever hides or disables the entry
  point on a `GameCenterRestricted` account or on a non-iOS build.
- The parental gate for a child's account ([Tech Design](../Tech%20Design.md) → Kids
  Category). This feature only carries `isUnderage` on the session so the gate can read it.
- Reconciling `loadMatches` against the open-games list, and anything the open-games list
  shows about an online game.
- Any player-facing copy, surface or animation for a failed sign-in, a restricted account, a
  cancelled matchmaker or a GameKit error.
- Game Center leaderboards and achievements.

## Open Questions

- **Where does "Play online" live?** The main menu is settled at four buttons — Play Game,
  Theme, Settings, About Us, with Settings and About Us sharing a row — and nothing says
  whether online play is a fifth button, a choice inside Play Game, or something on the
  open-games list. ([Menus and UI](../Menus%20and%20UI.md) → Open Questions.) So R19's first
  occasion — "the tap that enters online play" — has no tap to hang on yet.
- **What does New Game do when the player is already at the cap** — refuse and say the list
  is full, route the player into the delete flow, offer the $4.99 unlock at the moment the
  limit bites, or some combination of those? The same is unsettled for starting an online
  game and for accepting an invite to one, which hit the same cap.
  ([Menus and UI](../Menus%20and%20UI.md) → Open Questions.) R34 hands the caller the
  ceiling and the count; what the caller does with them is this question.
- **Online play — what the player is told.** ([Tech Design](../Tech%20Design.md) → Open
  Questions 12.) Nothing settles what the player sees for a failed or declined sign-in, a
  cancelled matchmaker, a GameKit error, or the "calm, kid-facing message" a restricted
  account gets.
- **What title does an online game take when the opponent's Game Center nickname is blank?**
  No doc addresses it. [Menus and UI](../Menus%20and%20UI.md) → Play Game says an online
  game is titled with the nickname and that "none of this reaches an online game" about the
  ItSaMeMaRiO default; [Tech Design](../Tech%20Design.md) refuses an empty online title at
  the store and leaves the title to the caller. R31 falls back to `defaultOpponentName`
  because the store would otherwise refuse the create — that is this PRD's call, not a
  doc's.
- **Hand-written channels or a generator?** R4 picks hand-written `MethodChannel` /
  `EventChannel` because every package dependency in this app is a decision recorded in
  [Tech Design](../Tech%20Design.md) and none records pigeon. No doc rules either way.
- **What is the bridge layer's folder called?** R1 picks `lib/gamecenter/` from
  [Tech Design](../Tech%20Design.md) → Project Structure's one-folder-per-layer convention;
  the convention is settled, the name is not.
