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

**R2.** `lib/online/`'s existing purity scan (`test/online/purity_scan_test.dart`) stays
green unchanged — no file added by this feature goes into `lib/online/`.
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
  "isUnderage": bool }    // present only when state == "authenticated"
```

`restricted` is what `GKLocalPlayer.isMultiplayerGamingRestricted` being true reports, and
`isUnderage` is `GKLocalPlayer.isUnderage`. Sources: [Tech Design](../Tech%20Design.md) →
Online Play (restricted → online play is not offered) and → Kids Category (`isUnderage` is
what decides whether the parental gate is raised).

**R7.** The event channel emits the same session map (R6) — the current one immediately on
subscription, and again on every later change the platform reports, including one GameKit
reports with no Dart call behind it (`GKLocalPlayer.authenticateHandler` may fire again when
the player signs in or out in iOS Settings). It never emits an error event.

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
whose player Apple has not resolved carries the empty string as its nickname.
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

**R12.** The Swift side performs no GameKit work until a Dart call arrives: registering the
channel does not set an authenticate handler, does not present anything, and does not touch
`GKLocalPlayer`. Source: [Tech Design](../Tech%20Design.md) → Online Play ("Game Center
sign-in happens when the player first enters online play, not at cold launch. … A player who
never touches online play never sees Game Center's sign-in banner").

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
class GameCenterRestricted      extends GameCenterSession {}   // const

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
  Stream<GameCenterSession> get sessions;
  GameCenterSession get session;               // the last value; never null
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

**R15.** A reply that is not a map, or whose `state`/`status` is absent or an unrecognised
string, or whose match map is missing a key R10 requires, is treated as the failure value for
that call (`GameCenterUnauthenticated`, `MatchmakerFailed`, `MatchesLoadFailed`) — never a
throw, never a partially-filled value.

### Session state and its provider

**R16.** The session starts at `GameCenterUnauthenticated` and reaches any other value only
through `authenticate()` or an event on the session channel. Constructing the bridge, reading
the provider, building any widget, and app launch itself all leave it at
`GameCenterUnauthenticated`. Source: [Tech Design](../Tech%20Design.md) → Online Play
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
Part one owns the second only as far as the hook — `authenticate()` being callable before the
first frame and before any screen exists, from whatever handles external entry. Source:
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

**R25.** Only one matchmaker presentation is in flight at a time: a second
`presentMatchmaker()` while one is open answers `MatchmakerFailed` rather than presenting a
second sheet. No doc states this; that a second sheet must not stack is not a judgement call,
but *which* value the second call gets is, and this is the PRD's pick over queueing it.

### Loading the player's matches

**R26.** `loadMatches()` answers every turn-based match Apple currently holds for the local
player (`GKTurnBasedMatch.loadMatches`), as match maps (R10), most recent first as GameKit
answers them — this feature imposes no order of its own. It reads only; it creates, stores,
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
| `opponentName` | the nickname of the one participant whose `isLocalPlayer` is false, trimmed; `defaultOpponentName` (`lib/state/game_controller.dart`) when that is empty or whitespace-only |
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
Questions.

**R32.** The minted series id is opaque, never parsed and never displayed, and unique across
devices — not merely within this process, because the accepting device copies it out of the
first payload and both devices then hold it. Source: [Tech Design](../Tech%20Design.md) →
Online Play. `mintGameId()` in `lib/storage/` does not satisfy "unique across devices" and is
not reused here.

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
  call" in R12, R23, R27 and R30 are assertable rather than merely stated.

**R37.** The fake lives under `lib/gamecenter/`, not under `test/`, because it is the double
callers in other layers test against. It holds no test-only shortcut that the real bridge
cannot honour.

### What is testable where

**R38.** Every requirement from R13 to R37 is asserted in `flutter test`: the Dart side
against `FakeGameCenterBridge`, and the channel encode/decode (R4–R11, R14, R15) against a
mock handler installed with `TestDefaultBinaryMessengerBinding` — the pattern already used in
`test/audio/fake_audioplayers_platform.dart` and across `test/navigation/`. The handoff
(R28–R35) is asserted against `InMemoryGameRepository`. Source: `project.json` → testing
(`flutter test`), [Tech Design](../Tech%20Design.md) → Testing.

**R39.** R3 is asserted by a scan test, in the same shape as the existing purity scans: the
channel-name strings occur in exactly one file under `lib/`.

**R40.** The Swift side is verified by a device pass and by nothing automated: no Swift test
target is added, and no test asserts that GameKit authenticates, that the sign-in or
matchmaker view controllers present, or what a real account's restricted and underage flags
say. Source: [Tech Design](../Tech%20Design.md) → Distribution and Release → CI — local builds
only, and → Testing (`flutter test` is the suite; appearance and platform behaviour are
checked by running the app). The Game Center capability, entitlement and provisioning profile
this needs are already live — `RELEASE.md` → Game Center.

**R41.** The device pass covers, on a real device signed into Game Center: sign-in presenting
and completing; the matchmaker sheet appearing and offering both Play Now and Invite Friends;
a match created through it producing a stored online game titled with the opponent's
nickname; cancelling the sheet storing nothing; and `loadMatches` answering the match just
created. A child account run covers the underage and restricted flags.

## Out of Scope

Part two and later rows, none of which this feature may preclude:

- Ending a turn with the board, and receiving the opponent's turn — including the inherited
  rule from the online-game record's close-out that **the bridge saves the local move only
  after Game Center accepts the turn**, so a stored board never shows the opponent to move on
  a turn this device did not hand off. Nothing here writes a move at all, so nothing here
  precludes it.
- `GKTurnTimeoutNone` — turns never time out ([Tech Design](../Tech%20Design.md) → Online
  Play). That is set where a turn is ended, which is part two.
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
