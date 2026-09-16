# Tech Design

> **Status:** Brain dump / early tech decisions. Contradictions are expected and OK.
>
> This doc covers *how we build it*. What we're building lives in
> [Game Overview](./Game%20Overview.md), [Rules](./Rules.md),
> [Game Board Design](./Game%20Board%20Design.md), [Menus and UI](./Menus%20and%20UI.md),
> [Theming](./Theming.md), and [Animations](./Animations.md).
>
> **Approved UI design:** `Docs/tic-tac-toe/design_handoff_game_ui/README.md` —
> [Design Handoff](./design_handoff_game_ui/README.md). Its *State* section sketches a
> per-game data shape and its *Assets* section names concrete font and icon dependencies.
> Reference asset — read-only.

## What the Design Docs Already Imply
Some technical requirements are already locked by decisions made elsewhere. Listing them
here so they don't get re-litigated:

| Requirement | Comes from |
|---|---|
| **Fully offline, except for Apple's own services.** No backend of ours and no accounts of ours — StoreKit and Game Center are the two exceptions, and both are Apple's rather than ours. StoreKit needs network access and a restore-purchases path tied to the Apple ID; Game Center holds the turn-based match, its data and the player identity. Neither is a service we run — see In-App Purchases and Entitlements and Online Play below. | Two players, one phone or two; qualified by In-App Purchases and Entitlements, and Online Play |
| **Local persistence** for 5 values: theme, music, sound, vibrate, animations | [Menus and UI](./Menus%20and%20UI.md) → Persistence |
| **Game-state persistence.** Every open game is saved and resumable, each with its own scoreboard. | [Menus and UI](./Menus%20and%20UI.md) → Persistence |
| **Audio playback** for one-shot sound effects, and for looping music the app fades in and out itself | [Theming](./Theming.md) |
| **Haptics** on every valid click | [Game Board Design](./Game%20Board%20Design.md) → Haptic Rule |
| **A theme system with fallback** — every visual/audio/motion value resolves through the active theme, falling back to Neon | [Theming](./Theming.md) |
| **Animations toggleable off entirely**, with instant state changes instead | [Animations](./Animations.md) |
| **Portrait phone layout**, whole 9x9 board visible, no zoom | [Game Board Design](./Game%20Board%20Design.md) |

## Platform and Targets

**Flutter and Dart.** Already in use for the game, and Dart comes with Flutter.

**iOS is the primary target as of right now.** Android is supported by virtue of Flutter,
but Apple is what we're building and testing against first.

Practical meaning: when a platform question comes up, iOS wins. Android is a
build-target, not a design constraint.

The ordering, as stated: **"We will want to port our game over to every devices. iPhone
will be the primary target iPads next then will want to branch out to all media devices.
such as Android in the far future."**

Concretely: **iPhone first, iPad second, Android far future.** "All media devices" is
recorded as stated and is not yet scoped to particular platforms.

**The project is built for iOS and Android only.** No web, macOS, Windows or Linux build
exists, and those platform folders are not created. Adding one later is cheap and does not
disturb `lib/`, so this scopes what is built and tested today rather than ruling a platform
out.

### Minimum iOS version
**iOS 15.** The in-app purchase layer is built on StoreKit 2 —
`Transaction.currentEntitlements`, `Transaction.updates` and `AppStore.sync()` — and those
APIs require iOS 15.

**Watch out for:** the floor cannot be lowered. Below iOS 15 the plugin falls back to
StoreKit 1, which has no `currentEntitlements` and whose restore returns queue transactions
that do not cleanly exclude revoked purchases — so a refunded player would keep permanent
access, and it fails silently rather than as a build error.

### Orientation — portrait only
**Upright portrait only.** No landscape, and no 180° rotation — the app does not run
upside-down.

The lock is set at both the Flutter level and the iOS project level, and both name the
upright orientation alone. Setting only the Flutter one is not a partial lock: iOS never
delivers a rotation the project has not declared, so a Flutter-level preference for
upside-down is dead code that reads like a decision that the app rotates.

**Watch out for:** iOS declares supported orientations separately for iPhone and for iPad,
and the generated iPad declaration allows both landscape orientations. Narrowing only the
iPhone one leaves the app rotating on an iPad, and the Flutter-level lock hides that in
most manual testing.

### Fresh build, not a refactor
**A fresh build.** Nothing from the earlier Flutter work carries into this design —
everything in this doc describes something being built new, not refactored toward.

## Project Structure

**Layer-first.** Group by kind, not by feature:

```
lib/
  main.dart
  app.dart
  engine/          ← pure Dart, zero Flutter imports
    board.dart
    rules.dart
  storage/         ← repository interfaces + their store implementations
  online/          ← pure Dart: the turn payload codec and the receive validator
  gamecenter/      ← the Game Center bridge: the platform channel and session
  theme/
    theme.dart     ← merged theme object
    loader.dart    ← YAML → theme
  state/           ← Riverpod providers
  navigation/      ← the app's routing layer
  audio/           ← sound playback
  haptics/         ← haptic feedback
  entitlements/    ← StoreKit entitlement state
  diagnostics/     ← crash catching/reporting
  purchase/        ← store integration
  parentalgate/    ← the gate, its fake, and its pure Dart problem generator
  ui/
    board/
    menus/
assets/
  themes/*.yaml
  images/
  audio/
```

**The Dart package name is `tic_tac_toe_extreme`**, the lower_snake_case form of the app
name and the final segment of the bundle identifier. Every `package:` URI in the codebase
is rooted at it. The repository's own directory name cannot serve — hyphens and capitals
are not legal in a Dart package identifier — and changing it later is a whole-codebase
rewrite.

`storage/` is local persistence only — the repository interfaces and the implementations
that back them. Which repositories exist, which store each is backed by, and what each
holds is **Persistence and Serialization** below. There is **no backend data layer**:
nothing in the app talks to a server of ours, and none gets added. Online play is remote
play over **Apple Game Center turn-based matches** — Apple holds the match data, the
matchmaking, the invites, the player identity and the "your turn" push, so the app still
runs no service of its own and still collects no identity of its own. The board position
crosses the wire to Apple's match and comes back; `storage/` still holds only what is on
this device. Online play is iOS only, and same-room play — Bluetooth, peer-to-peer, two
phones in one room — is not wanted. It is being built: what it is, and how the bridge to
GameKit works, is **Online Play** below.

That rule is checked rather than trusted: a scan over `lib/` finds no HTTP client and no
network target other than the store SDK and GameKit. It covers `lib/` only, so build-time
tooling outside that tree is out of its reach by construction. What is fixed is that
property, not a list of banned symbols — widening it when a new transport appears is
ordinary maintenance, narrowing it to let a real network call through is not. It must
**not** be written as "no networking API is reachable from `lib/`": in-app purchases and
Game Center are the two sanctioned network paths, so the stricter form fails the day the
store layer lands.

`engine/`'s purity is held by a test that scans the layer's imports rather than by
discipline — see **The Rules Engine** below for what that check matches.

`online/` holds the pure Dart side of online play and its purity is held the same way, by a
scan over the layer's imports — no Flutter, no `dart:ui`, no Hive and no platform channel.
It imports the engine and nothing else of the app's, which is what keeps the two decisions
a turn turns on testable with no GameKit in sight. The series id's minter lives there too,
with the payload that carries a series id across the wire. See **Online Play** below.

`gamecenter/` holds the other half of online play — everything that faces the platform
channel: the channel-backed bridge, the fake that stands in for it, the session providers,
the handoff from a found match to a stored game, and the receiver that routes an arriving
turn to its stored record. Keeping it out of `online/` is what lets that layer's purity scan
stay true. The three channel-name strings are written in exactly one file on each side — one
under `lib/gamecenter/`, one under `ios/Runner/` — and a scan test holds that, so the string
contract between the two languages has one place to be checked against. The scan matches by
substring, so a second file naming a channel anywhere would fail it regardless of which
layer wanted it. The Swift half is registered from `AppDelegate` alongside the generated
plugin registrant.

`parentalgate/` is the gate's own layer rather than a file inside `purchase/`, since
purchases and online entry both call it and neither owns it. The service, the fake that
stands in for it, and the problem generator all live there. The generator is pure Dart and
takes its source of randomness as a parameter, so a seeded source pins the exact problem and
its answer in a test; its purity is held by an import scan the same way `engine/`'s and
`online/`'s are — over that one file rather than the whole folder, since the service beside
it carries no such guarantee.

`theme/` holds more than the merged theme object and its loader. Resolving a theme's icon
slot to a concrete `IconData`, and a stored integer weight to a `FontWeight`, both live in
this layer, because neither can be written as a theme value read and passed through — an
icon constant and a `FontWeight` are not labelled numbers. The hardcoded-theme-value guard
permits both only here (see **Testing** below), so either one written anywhere else under
`lib/` fails that guard with no legal fix.

`main.dart` is the entry point and nothing else: it initializes the Flutter binding,
applies the orientation lock, and calls `runApp` exactly once, from one place. `app.dart`
holds the root widget. That single `runApp` call site is what crash handling wraps, which
puts its handlers and any guarded zone **outside** `ProviderScope`, so a failure during
scope construction is still caught.

**`ProviderScope` is the outermost app-level widget**, above the root widget. That
placement is what makes settings and the theme readable from anywhere in the tree,
including deep in the board — see **State Management** below.

**The app is routed from the first build**, on the routed `MaterialApp.router` form rather
than a `home:` widget, so installing the real route table replaces a value instead of
restructuring the root widget.

`navigation/` holds the app's routing layer — see **Navigation** below. Route construction
happens there and nowhere else. It is Flutter-side, same as `ui/` and `state/` — nothing
here changes the `engine/` purity rule. What goes inside the layer beyond that is a PRD's
job, not this doc's.

`assets/themes/`, `assets/images/` and `assets/audio/` are the **designated folders for
assets** required by **Audio and Assets** below. A folder's `pubspec.yaml` declaration
lands with the first real file put into it, never before — Flutter fails the build when a
declared asset directory holds no files.

`audio/`, `haptics/`, `entitlements/`, `diagnostics/` and `purchase/` follow the same
one-folder-per-layer convention. File names inside each are not this doc's to decide.

## The Rules Engine

**The rules engine is separate from Flutter.** Board state, legal moves, sending rule,
win/cat-game detection and free-choice state are **pure Dart with zero Flutter imports**,
and the UI layer reads from it.

**The purity check rejects any import of `package:flutter/…` and any import of
`dart:ui`** — both, not the first alone. Both are unimportable from a pure Dart VM
test, so a scan that let `dart:ui` through would keep passing while the layer stopped
being testable without a widget harness, which is the purpose the scan serves.

**It imports no Hive package either, whatever the spelling.** `storage/` owns the store —
see **Persistence and Serialization** below — and the purity check matches any package
whose name begins `hive`, so it keeps holding if that choice is ever revisited.

**Game state is immutable.** The engine never mutates a board in place — every move
produces a new state object, and that new object is what the UI renders.

The API is `Board applyMove(Board, Move)` returning new state, not `board.play(move)`
mutating in place — so the pure-Dart engine and the Riverpod layer agree on how state
changes.

### One value holds the game and the series

**`Board` is the whole game plus the series it belongs to** — the 81 cells, the 9 quadrant
states, the placement state and the forced quadrant, whose turn it is, the last completed
move, the outcome and the line that won it, the running score, and who went first in this
game. There is no outer type wrapping it: the state a game-ending move returns already
carries the incremented score, so a caller has one value to render, save and resume.

The name is narrower than what it holds, and it is kept rather than quietly improved —
the API above and every consuming layer are written against it.

### The engine speaks the project's vocabulary

**The public surface uses the working vocabulary** — big board, quadrant, small board,
claim, cat game, Player One, Player Two — from
[Game Overview](./Game%20Overview.md) → Terminology. No abbreviation of *quadrant*, and
nothing shortened to `p1`/`p2`.

**The engine holds no mark glyph and no display string.** X and O are theme-supplied asset
slots — see **Marks — supplied by the theme** below — so nothing in the engine names a
glyph, an icon, an asset path, or any text a player reads. The players are Player One and
Player Two, named so that real names can be added later without fighting the engine.

### Quadrants and cells are indexed the same way

**Both are 0 to 8, row-major from the top left** — 0 top-left, 4 centre, 8 bottom-right —
for a cell inside its small board and for a quadrant inside the big board alike. That
shared numbering is what makes the sending rule an identity: the index of the cell played
is the index of the quadrant the opponent is sent to. The 1–9 labels in
[Rules](./Rules.md) → Cell → Quadrant Mapping are that same order, written for humans to
read.

### Three placement states, and the UI reads them

**Forced, free choice and game over are engine state, not something the UI infers.** The
engine names which one is active, and in the forced state which quadrant. The opening move
is the free-choice state over all nine quadrants, not a state of its own.

A consumer branches on the placement state and never on "there is no forced quadrant" —
free choice and game over both have none, so that test reads a finished game as free
choice. A forced state always names a quadrant with at least one legal move in it, because
a send onto a quadrant that just died resolves to free choice instead.

**One still-open quadrant is still free choice, not forced.** When the send lands on a
dead quadrant and exactly one quadrant is left open, the state is free choice. The legal
moves are identical either way; the difference is what the board draws — that quadrant
reads as available rather than as the forced one, see
[Game Board Design](./Game%20Board%20Design.md) → The free-choice state.

**A claim or cat game is resolved before the send is.** That ordering inside a move is
what makes a move that kills its own destination hand the opponent a free choice, which
[Rules](./Rules.md) → Sent to a dead quadrant states as the rule.

**The legal-move set is empty exactly when the game is over**, so an in-progress board
always offers at least one move.

### The series lives in the same state

**The score is series state, and the engine moves it** — the winner's column, or Ties, is
already incremented on the state the game-ending move returns. See
[Menus and UI](./Menus%20and%20UI.md) → When does the scoreboard increment. Starting the
next game resets the board and moves no counter, because the finished game was counted
when it ended. Starting the next game is reachable only from a finished game — from the
game-over modal that offers it, or by starting fresh from the main menu. There is no path
to it from a game in progress, so the engine defines no behaviour for that case and
nothing tests it.

**Whose turn it is, is engine state, never derived from move parity.** Turn order across
games ([Rules](./Rules.md) → Turn Order Across Games) makes Player Two the first player of
some games, so the engine also retains who went first in the current game. A move names a
quadrant and a cell and never a player — the mark is the current player's, which makes
alternation the engine's to enforce rather than the caller's to get right.

**Watch out for:** a turn derived from move parity passes a single-game test suite and
then silently inverts the turn indicator for every later game in a series.

**The move that ends the game does not alternate.** Every other move flips whose turn it
is; the winning move leaves the winner as the current player, so a finished game reads as
the winner's wherever it is read rather than naming the player who lost. The cost is that
the last move is the one exception to alternation, and anything asserting that invariant
has to carve it out. On a straight draw there is no winner to stop on, so the value stays
with whoever made the final move — nobody is to move on a finished game, and anything that
presents a turn gates on the game-over state.

**The last completed move is part of the state, and it is absent rather than a stand-in
value on a board nobody has played** — a fresh series and the board that starts the next
game both have none. A stand-in would draw the last-move ring on a cell nobody played, on
the first board of every rematch.

### The engine publishes which three quadrants won

**On a won game the engine names the three quadrants of the completed big-board line**, so
whatever announces or highlights the win reads it rather than re-deriving it. It is absent
on an in-progress board and on a draw, and there is no stand-in value to test for.

Absence carries two meanings and is not a draw signal: a consumer reads the outcome
first and asks for the line only in the two winning cases. The three come back in
ascending order — a list needs some order, no doc gives one, and anything wanting the
order a line is drawn in sorts them itself. When one claim completes two lines at once,
exactly one comes back: the first in a fixed order — rows top to bottom, then columns
left to right, then the top-left-to-bottom-right diagonal, then the
top-right-to-bottom-left diagonal — so the value is deterministic. That order is
**total**: it separates the two diagonals rather than treating them as one slot,
because a claim can complete both of them and no row or column. Which line a *player*
should be shown in that case is an open question below.

The line is derivable from the quadrant states, so nothing turns on whether it is stored
with a saved game or recomputed on load.

**This makes a winning-quadrant highlight expressible; it designs none.** What is drawn
with the value belongs to [Game Board Design](./Game%20Board%20Design.md) and
[Animations](./Animations.md).

### What the engine refuses

[Rules](./Rules.md) → Engine Contract settles that the engine throws rather than returning
silently. The engine's own share of that contract:

- **Two reasons, and the already-finished game is checked first**, so a move applied to a
  finished game reports that rather than "not a legal move" — both are true of it and only
  one of them is useful.
- **It raises an `Error`, not an `Exception`.** This is a contract violation rather than a
  recoverable condition, and no caller is meant to catch it.
- **The error carries the offending move and the board it was applied to.** That is the
  debugging value, and it is read from a debugger attached in process. What may be
  *rendered* from it is **Crash Reporting** → *The one error that carries game state
  renders none of it* below; the engine's own tests assert that rendering this error as
  text prints no board content.
- **A move carrying a quadrant or cell index outside 0–8 is an illegal move**, and is
  refused the same way as any other. What comes back from *reading* a cell or a
  quadrant out of range is a separate matter, and is an open question below.

### What the engine is not

The engine draws nothing, holds no theme value, and knows nothing about screens. A pending
selection — the first tap of the two-tap move — is input state and never engine state. The
record id, the opponent name and the timestamps a saved game carries belong to storage,
not to game state; see **What a stored open game holds** below.

## State Management

**Riverpod, without Riverpod's own codegen to start.** Plain `NotifierProvider`
declarations, no `@riverpod` annotations. Riverpod codegen can be adopted later without
rewriting the logic.

It also covers the requirement that settings and the theme be readable from
**everywhere**, including deep in the board widget tree.

**Watch out for:** fey-tactics uses `StateNotifier`, which is the legacy API. Use
`Notifier`/`NotifierProvider` — fey-tactics is a reference for the sync shape, not for
the API surface.

**A layer with one real implementation and a fake is reached through a plain `Provider` of
its abstract interface, and a test substitutes the fake by overriding that provider** — no
singleton, no global instance. The Game Center bridge and the parental gate are both shaped
that way, and both fakes ship as app code rather than test code, because they are the double
every other layer tests against.

## Navigation

**The app has an explicit navigation layer, and the routing package is `go_router`.** The
user asked for the choice that serves the end objective of building larger games, made
once and correctly rather than as a stopgap: *"I want to pick the navigation layer that
solves for the full problems this application can have. Something that is not just
temporary but the right choice for the end objective of building larger games… Lets get
this right the first time."*

Why: it is the Flutter team's recommended routing package; it is declarative, so routes
are described rather than imperatively pushed; it handles deep links and the browser URL
bar without rework; it supports nested and shell navigation, which is what larger games
need for persistent chrome; and it scales past this game's seven screens without a second
migration.

Consequences, recorded honestly rather than as caveats:
- It adds a dependency.
- Dismissing a route becomes `context.pop()` rather than `Navigator.pop`, so the
  navigation layer's internals are shaped by this choice even though its public
  operations are not.

### Screens call operations, not routes

**The layer publishes one interface of named operations, and a screen calls an operation
rather than a route.** A screen calls something like "exit game to main menu"; it does not
`go`, `push`, `pop`, or name a path. That is the contract every screen codes against, and
publishing it before the mechanism was chosen is why `go_router` arrived as an additive
change rather than a rewrite — the back-stack choices still open land as edits inside this
layer, and no call site moves when one of them is settled.

**The layer reads the stored open-game count itself and writes nothing.** Play Game's
branch — into a new game, or into the list of open ones — is evaluated inside the layer,
so no screen reads the count for itself. Nothing here creates, saves or deletes a game:
the layer presents the delete confirmation but never performs the deletion, which is why
leaving a game discards nothing (see
[Menus and UI](./Menus%20and%20UI.md) → Navigation and the Back Stack).

### No operation reports an outcome back

**No navigation operation returns a result to its caller.** An operation completes when
the navigation is done, not when the surface it opened is finished with, so a modal's
outcome — which button the player pressed, whether they confirmed or cancelled — never
comes back through the interface. It cannot be recovered another way either, because
observing the router from outside this layer is not allowed.

**So any flow that seems to need a modal's answer has to be restructured so that nothing
has to hear it**: the surface acts on the state itself, or the caller does its work before
opening the surface rather than after it closes. This has already bitten once — a list
row's delete reveal, specified to close when its confirmation was dismissed, became
unimplementable the moment that confirmation became a route, and was fixed by closing the
reveal before the modal opens. A host choice that touches no model, no storage and no
engine can still make a sibling requirement unassertable, so check what a flow needs to
*hear* before assuming a route can host it.

### Nothing outside the layer puts a surface on screen

**The only way a widget outside the navigation layer causes a surface to appear or
disappear is by calling one of the layer's operations.** Like the engine's purity and the
no-networking rule, this is checked rather than trusted: the routing package is imported
only inside the layer, which catches every routing call because none of them compiles
without that import; and outside it, nothing references Flutter's navigator, overlay or
route types, holds a navigator key, or calls anything in the `show…` family.

**That second scan matches a shape, not a list of names.** An earlier form banned
`showDialog` and `showModalBottomSheet` by name — but `showGeneralDialog` and
`showAdaptiveDialog` contain neither substring and sail through a guard written to stop
exactly what they do, and `showCupertinoDialog`, `showCupertinoModalPopup`, `showMenu` and
`showBottomSheet` are the same family. A deny-list is always one API name behind; matching
`show` followed by a capital is not, because what it relies on is the naming convention
rather than any particular name. It is deliberately over-broad, and the escape hatch is
the point: a legitimate `show…` call lives in the navigation layer like every other
presentation mechanism.

**Neither scan sees a gesture.** Both are about calls, and the platform back-swipe makes
none — it pops the route itself. That is why turning the gesture off on the game screen
had to be done explicitly rather than falling out of these scans: the hole it closes is
the absence of a call, which no scan for forbidden calls can find.

### The layer is reached through a provider

**Screens acquire the navigation layer through a Riverpod provider, and by no other
means** — no static singleton, no global instance, no `BuildContext` extension reaching a
navigator key. One implementation holds the router; screens read the navigator and never
the router itself.

This is not a stylistic preference. The provider is the injection point: under a singleton
or an internally-held navigator key there is nowhere to substitute a recording fake, and
"this screen invoked that navigation exactly once" could not be asserted at all.

### Surfaces that stay on top of something are nested

**A surface that has to leave something mounted beneath it is declared as a child of what
it sits on**, rather than each screen being trusted to preserve what is behind it. That is
what makes "the menu is still there behind the overlay" a property of the route table
rather than of a screen's discipline, and it is what keeps a game mounted underneath an
in-game surface.

It also enforces one rule structurally rather than by convention: theme selection sits
under the main menu and not under the game, so it cannot be reached from inside a game
without leaving it — you can't change the theme mid-game (see
[Theming](./Theming.md) → Choosing a Theme).

### The parental gate is pushed, and that is the one exception

**The parental gate's surface is a top-level route pushed over whatever is on screen.** It is
the one exception to this layer's shape, where a route change is a replacement by
construction rather than a `push` — see [Menus and UI](./Menus%20and%20UI.md) → Navigation
and the Back Stack. The gate is raised from the main menu, from Settings and from wherever
the purchase flow lands, so it has no single parent to be nested under, and it has to return
the player to a caller it does not know, which is exactly what a replacement cannot do.
Pushing leaves what raised it mounted and visible beneath, and popping lands the player back
where they were.

**It is reached through a second small interface beside the game-launch one** — show the
gate, dismiss the gate, and nothing else, with its own provider. `AppNavigator`'s fixed
operations are left alone, for the same reason the game-launch operations were kept off them:
every screen and every recording fake already depends on that shape. Both of the gate's
operations go through the layer's single choke point, so raising the gate over the board
clears a pending, unconfirmed move like every other navigation does.

**The gate's surface reports its outcome to the gate service, never through the navigator**,
since no navigation operation reports an outcome back. The service holds the pending action,
runs it on a pass, and takes the surface off screen itself. The surface's disposal reports an
abandon too, so a gate the platform took away rather than a control closing cannot leave a
stale action pending behind it.

**Nothing unmounts when a surface opens over the board, so nothing clears a pending move
by accident** — which is why clearing it belongs to this layer. Every operation clears the
pending, unconfirmed selection before it navigates; clearing when there is none is a
no-op, and making it unconditional means no operation added later can forget to. It cannot
live in the board layer instead, because that layer would have to observe the router to
know a navigation happened, which is the one boundary this layer exists to hold. The rule
itself is [Game Board Design](./Game%20Board%20Design.md) → Changing your mind.

### Deep links are possible, not wired

The route structure is link-shaped, because that is part of what `go_router` was chosen
for. The app does have an external entry point — it can be launched from a Game Center
invite or a "your turn" notification — but that arrives through GameKit rather than as a
URL, and there is no invite-link API to wire up, so no URL scheme, universal link or
associated-domain configuration is specified. The capability is retained; nothing is wired
to it.

The route table and route paths are not designed here — that is a PRD's job.

## Rendering the Board

**The board is rendered with widgets.** *"ok widgets is the winner lets make that
happen."* 81 `GestureDetector`s in nested `GridView`/`Column`s, not a `CustomPainter`.

**Watch out for:** nested `Border.all` doubles interior grid lines — two adjacent 1px
borders read as 2px — and hairlines can look uneven at fractional device pixel ratios.
The known fix is a hybrid: widgets for cells and marks, plus one thin `CustomPaint`
overlay drawing only the grid lines. That is an escape hatch, not a decision taken.

**No cell carries a border of its own.** The small-board lines are drawn as their own
lines, inset inside the quadrant, so two cell borders never meet and the doubling above
cannot arise. The geometry is [Game Board Design](./Game%20Board%20Design.md) → Board
Structure.

**The board draws state and gates nothing.** Every one of the 81 cells takes a tap
whether or not the move is legal, and what a tap means — select, confirm, or nothing at
all — is decided in the state layer rather than in the board.

**Watch out for:** dropping the tap handler from illegal cells looks like an obvious
simplification and is a bug. A cell with no handler of its own does not win the tap, so it
falls through to the tap-away-to-clear surface underneath and wipes the player's pending
selection — an illegal tap, which is supposed to do nothing at all, would instead undo the
move they had lined up. For the same reason a cell's tap target is its whole box and not
the pixels it paints: an empty cell paints nothing, so a board that only took taps where
it had drawn something would be inert.

**The same holds for a board the player may not play on at all.** While an online game is
waiting on the opponent, nothing wraps the board in a pointer blocker and no cell loses its
handler — the refusal is the state layer's, exactly as an illegal tap's is. See **Online
Play** below.

**The boundary is a widget, not a rectangle:** a tap a cell takes never clears the
pending selection; every other tap on the game screen does — the gaps between cells and
quadrants, the board's margins, the scoreboard, the how-to-play strip. The surface that
catches them is the screen's, not the board's, and it covers the whole screen rectangle
rather than only the parts that paint. Taps a control claims never reach it, which is why
the other half of the rule lives in the navigation layer — see **Navigation** above.

### Marks — supplied by the theme
**Marks are asset slots on the theme, not shapes drawn in board code.** The theme supplies
the mark art; board code places it and draws nothing itself. Which kinds of art a theme
may supply — and why an image is the real answer for a theme — is
[Theming](./Theming.md) → What a Theme Controls.

### The screen loads its game before it draws one

**The game screen reads the stored game it was opened for, and draws no board until that
read lands** — no board and no scoreboard, just the background. The screen is the only
thing that knows which game it was asked for: the router hands over an id and stops, and
the storage layer has no idea which game is on screen.

**Watch out for:** the game state the board renders outlives the screen, so a board drawn
before the read lands is the *previous* game's position sitting on this game's screen. It
is the same failure as opening a saved game onto an empty board — complete, legal and
correct-looking, with nothing about it saying the wrong game is on screen. Withholding the
board until the read lands is what makes that unobservable.

## The Theme System

**Themes are data — a YAML object loaded at runtime**, not a Dart class compiled into the
app. A universal, theme-like object that can be loaded in.

**Each theme carries a UUID in its YAML file, and that UUID is the theme's identity.**
*"the themes should be saved by UUID in the YAML files."*

The persisted "selected theme" preference stores the UUID, not the theme's name. See
[Theming](./Theming.md) → Choosing a Theme.

**Merge over Neon.** Each theme is materialized into a complete theme by merging it over
Neon — every installed theme, once at startup, not just the selected one and not per
lookup. See [Theming](./Theming.md) → Neon Is the Base Theme.

**A theme that is not in use is still a complete theme**, so reading another theme's
values is a read and never a load. The theme list depends on that: its rows draw each
theme in that theme's own colors and marks, not the active theme's — see
[Menus and UI](./Menus%20and%20UI.md) → Theme Selection. Materializing only the selected
theme and resolving the others on demand is the tempting optimisation, and it turns every
row on that screen into a load.

**A component reads its own key, never a palette value that happens to match.** The theme
holds palette-level values — the colors, the corner radii — and component-level values
that name the thing they style. A component binds to the component-level key even where a
palette value holds the same color today, because the two part company the moment a theme
wants that one control to differ. The hardcoded-theme-value test does not catch a value
read from the wrong key, so this one is a convention rather than an enforced rule — see
**Testing** below.

**Not every slot on a theme is something to play or draw.** A theme's sound entries are
not a uniform list — alongside the moments the game plays, a theme names its own sonic
identity in a word, and that word is metadata rather than an asset. Anything that walks a
theme's sounds as a list of playable assets picks it up and tries to play it. Sounds are
reached by naming the moment instead, which is **Audio and Assets** below.

### Flutter's ThemeData vs our own theme object
**Use Flutter's `ThemeData`/`ThemeExtension` as far as possible**, filled out from our
theme YAML file. The remaining parts, not supported by the Flutter theme, we implement
ourselves.

Sounds and animations live in the **same theme object** — not a parallel structure. We
give Flutter's `ThemeData` what we can and handle the rest ourselves, all from the same
file.

**Our theme object is the source, and `ThemeData` is the mirror** — populated from it,
never the other way round. A value read back out of `ThemeData` is reading the copy, so
consumers read the theme object itself.

**Reaching it takes no `BuildContext`.** That is what lets a service read the same theme a
widget does: playing a sound is one call that names a moment and carries no context (see
**Audio and Assets** below), and it still has to resolve which file that moment names. A
theme reachable only through the widget tree could not answer that call.

### Themes pick their own font
**A font is a themeable value like any other**, and the theme object needs somewhere to
put one. See [Theming](./Theming.md) → Architectural Rule.

Inter 400/500/600 is bundled as **Neon's** font choice, not an app-wide font constant. See
[Theming](./Theming.md) → What a Theme Controls.

### The theme system is the main architectural risk
> *"All of our code operates off of the theme. No code should be operating independently
> from the selected theme."*

This is the one constraint that touches every file, and it's the one that's expensive to
retrofit. Whatever we choose for state management and widget structure has to make
"every value comes from the theme" the *easy* path, not a discipline we have to maintain
by hand.

The countermeasure is the hardcoded-theme-value test — see **Testing** below. That is what
turns this from a discipline into a check.

## Persistence and Serialization

**`shared_preferences` for the five player preferences, Hive for game state.** Open games
— the board, whose turn it is, and the scoreboard — are stored in Hive, not in
`shared_preferences`. The Hive packages are **`hive_ce` + `hive_ce_flutter`**, the
actively maintained community fork, not `hive` + `hive_flutter`.

This is what makes [Menus and UI](./Menus%20and%20UI.md) → Persistence and
[Game Overview](./Game%20Overview.md) → Session Structure — Games and Continuing
implementable.

### Serialization and the storage layer
**Hand-written domain models in `engine/` carrying their own `toJson`/`fromJson`, and a
`storage/` layer holding the repository interfaces with Hive and `shared_preferences`
implementations that store JSON. No Hive `TypeAdapter`s.**

Two consequences worth naming, because they cut across other sections:

- **`hive_ce_flutter` is not pure Dart, so it must never be imported from `engine/`.**
  `storage/` owns it — and more strongly, **only `storage/` knows the store is Hive.** No
  file outside it imports either Hive package, and every caller depends on the repository
  interfaces rather than their implementations. That is also what lets tests run against
  in-memory fakes with no Hive initialized.
- **Serialization lives with the model.** `toJson`/`fromJson` are hand-written in
  `engine/` — pure Dart, Flutter-free — while the Hive box, adapters-free, lives in
  `storage/`. The storage layer writes no encoding of the game state of its own; what it
  does encode by hand is the record envelope around it — the opponent name, the two
  timestamps, the version stamp and, on an online game, the three values under **What an
  online game adds to the record** below. The engine's models are kept as they are and gain
  conversion rather than being rewritten through `freezed`: regenerating working, tested
  code buys no behaviour change, and it would put the engine's purity guarantee through a
  generator. Generated serialization stays permitted where it is simpler, and is required
  nowhere.

**The box has one name, `open_games`, and it holds JSON-encoded strings rather than
decoded maps.** Both are on-disk identity the moment a record ships, so both are schema
rather than a choice whoever writes the code first gets to make — renaming the box orphans
every stored game.

### Every persisted record carries a version stamp
**Every record written to either store carries a stamp identifying the app version that
wrote it, and it is there from the first release.** Preferences and open games both.

The stamp costs almost nothing while no device holds a save, and it cannot be recovered
afterward: without it, a record written by an older version is indistinguishable from one
written by the current version, and the app is left inferring a version from the shape of
the data. What the app *does* when it reads a record written by an older version is a
separate question, and an open one — see **Open Questions** below.

**The repository owns the stamp, exactly as it owns the timestamps.** It is applied on
every write and whatever the caller passes is discarded, so the stamp means *the app
version that last wrote this record*: a record created under one version and saved under a
later one carries the later one.

### What a stored open game holds
**A stored open game is the engine's whole game-plus-series state, plus what belongs to
storage rather than to the game: the record id, the opponent name the game is titled with,
two timestamps, the app version stamp, and — on an online game — the three values that say
which match it is being played through.** No design doc puts any of those in game state, so
they sit alongside the board rather than inside it.

**The most recent completed move is persisted as the move itself, not as a derived
value.** It has two consumers and only the move serves both: the forced quadrant is
derived from it and is *not* recoverable from the cells, and the opponent's last-move
highlight is drawn from it. Round-tripping only a forced-quadrant value loses the second.

**The persisted series carries enough state to resume turn order across games** — see
[Rules](./Rules.md) → Turn Order Across Games — with the app having been closed in
between.

**The id is opaque, store-minted and stable for life.** It is the only thing that
identifies an open game: a rematch, a rename, or any number of saves leave it identical,
and it is never reused after a delete. Nothing parses it, derives ordering from it, or
displays it. The opponent name cannot serve as the key, because it is a title and
duplicate titles are the ordinary case.

**The opponent name is set at create and a save never changes it.** A save preserves the
stored name and discards whatever the caller passed, the same way it preserves the created
timestamp — otherwise every save is a rename, and no doc specifies a rename or a control
that would perform one.

**An online game's name is the opponent's Game Center nickname, captured when the match is
created.** The rule above holds unchanged for it: set at create, and a save never changes
it. So the field has two sources — typed by the player for a game on this phone, taken from
Game Center for an online one — and one lifecycle, with a single narrow exception for an
online game whose opponent has not resolved yet, in **What an online game adds to the
record** below. See **Online Play** below.

**The record carries both a created and an updated timestamp, not one or the other.** That
leaves the sort key a *display* choice rather than a *schema* one — a list that wanted
creation order, or a row that wanted "started on", can be served later without migrating
data already on the device.

**The repository owns both timestamps; the caller supplies neither.** A save stamps the
updated timestamp from the clock and preserves the stored created one, discarding whatever
the caller passed in either field. Both halves are deliberate: keeping the updated stamp
current stops being a rule every call site has to remember — the symptom of forgetting is
a silently mis-ordered list rather than a failing test — and the created stamp's
immutability becomes enforceable at the one choke point instead of merely conventional.

**Both timestamps are UTC.** A local `DateTime` serialized to ISO-8601 carries no offset at
all, so a record written in one timezone and read in another compares as though it had
been written at a different instant — and the open-games list is ordered on exactly that
comparison, so the list would reorder itself after a flight or a DST change. The
repository forces UTC on whatever its clock answers rather than trusting it to be UTC
already, so the guarantee is structural rather than something each caller has to honour.

### What an online game adds to the record
**An online game is an open game in the same box** — the same store-minted id, the same
repository-owned timestamps, the same version stamp, the same position in the open-games
order, and the same cap. There is no second store, no second box and no second record type.
It adds exactly three stored values and no others: the Game Center match it is currently
played through, the series that match belongs to, and which side this device plays.

**The three are written under a single `online` key on the record's JSON**, holding
`matchId`, `seriesId` and `localPlayer`. The first two are strings; `localPlayer` is the
player's name string — `playerOne` or `playerTwo` — exactly as the board already encodes a
player. Those key names and encodings are on-disk identity the moment a record ships, so
they are schema rather than a naming choice made at implementation time.

**The presence of that key is the only thing that tells an online game from a local one.** A
record whose `online` key is absent, or present and null, is a local game and loads exactly
as a record written before online play existed. Nothing infers online-ness from the title,
the board, or anything else.

**An `online` key that is present but unreadable makes the whole record unreadable** — a
missing `matchId` or `seriesId`, a `localPlayer` naming no player, any of the three
wrong-typed — and it gets the answer every other unreadable record gets: "nothing stored"
for a read by id, skipped by the list read while every other game still comes back, and left
on disk exactly as it is. **An unrecognised extra key inside the map is ignored** rather than
treated as unreadable, so a record written by a later version that added a fourth value still
loads here.

**The record stores no Game Center identity** — not the opponent's player id, not the local
player's, not a team or an alias beyond the nickname the game is titled with. The players'
identities live in the match, with Apple. Knowing which side this device plays is what is
stored instead of an identifier, and it is the reason that is the shape.

**Whose turn it is is not a stored field.** It is the board's current player compared against
the side this device plays. Whose turn it is is engine state and is never derived a second
way.

**The side this device plays is set at create and never changes for the life of the record**,
including across a rematch: the side on the record wins over any assignment the new match
could suggest.

**Creating an online game takes the opponent's nickname, the starting board, the match id,
the series id and this device's side — all five from the caller.** The store mints the record
id and nothing else; it mints no series id, and it substitutes no title.

**One operation renames a stored game, and it exists for one case.** A random-opponent match
comes back from Apple's sheet before the opponent exists, so the record has to be created —
and therefore titled — with a name Game Center cannot yet supply; it takes the placeholder
title and is renamed exactly once, when the opponent resolves. Setting the online opponent
name is the only way a stored title ever changes after create, and a save still never renames.
It is allowed on an online record only: a local record answers the same "nothing stored" an id
the store never held gets. An empty or whitespace-only nickname is refused, distinctly from
"nothing stored", and neither refusal writes or emits anything. A successful rename touches
the title alone — the board, the three `online` values, the created timestamp and the id are
unchanged — and otherwise behaves exactly as a save does: it stamps the updated timestamp,
moves the record to the top of the list, and emits on the change stream.

**A save never touches the three.** Only the board is honoured, exactly as the title and the
created timestamp already are. **The match id changes on exactly two paths and no others** —
the initiating device's own next-game write, and an accepted rematch payload.

**Advancing to the next game and pointing the record at the new match is one write.** Taking
the next game on this phone stores the next board and the new match id together, so a record
can never sit with the next game's board under the finished game's match id, or the reverse.
It requires a finished stored board, and answers a value rather than throwing when the board
is still in progress or the id names no record.

**That write optionally takes the board to store**, so a device that has already handed a
board off to Game Center writes that board and the new match id together rather than needing
a second write to add the move it just sent. A given board is validated first, by one rule:
it must equal the next game of the stored series, or be exactly one legal move from it. Legal
moves are enumerated and applied, the way the receive rules do it; no turn test runs and no
side is consulted, because this board is the device's own rather than one that arrived, and
those branches would refuse the ordinary case. A board that fails — two moves ahead, from
another series, anything unreachable — is refused with its own distinct value, and nothing is
written on any refusal.

**Applying a turn that arrived takes a record id, not a record** — the store reads the current
one itself rather than trusting a copy the caller may be holding stale. Every outcome is a
returned value the caller can branch on, never a throw, and nothing is written on any outcome
but acceptance. An accepted turn stamps the updated timestamp, moves the record to the top of
the list exactly as any save does, and emits on the change stream; a re-delivery or a refusal
emits nothing, because neither changed what the list would show. An apply against a record
with no online values held answers the same "nothing stored" as an id the store never held.
Which outcome a payload gets is **Online Play** below.

### The open-games list has a defined order
**Reading the open-games list returns most-recent-first on the updated timestamp,
tiebroken by the created one** — never the box's iteration order, and never the id. The
order is deterministic: the same stored set produces the same sequence on every read and
across relaunches, so the player's list does not reshuffle behind them. Hive's
box-iteration order is **not** stable across compaction, which is the concrete failure
this prevents — a list silently reshuffling between launches rather than a failing test.

The tiebreaker is not decoration: a freshly created record has both stamps equal, so two
games created before either is played can tie on the primary key, and Dart's `List.sort`
is not stable.

Two records can tie on **both** stamps, so the comparator ends in a final key of the
implementation's choosing and is total. Ordering by that key is not the rule and it is
never a display order — it is only what stops a tie from resolving differently between two
reads.

**Any save moves its record to the top, including a save that is not a move** — taking a
rematch puts that series first before a mark is placed in the new game.

### The cap is enforced on create, and the store never evicts
**Creating an open game is refused when it would exceed the current ceiling**, and that is
a create-time check rather than a standing invariant: it constrains what may be added and
nothing else. The ceiling is not a constant — see [Menus and UI](./Menus%20and%20UI.md) →
How many open games we keep — and the storage layer reads it from entitlement state rather
than defining either number itself. Entitlement state does not exist yet, so the default
of 3 is resolved at startup, above the storage layer, and handed to the repository when it
is constructed — no file under `lib/storage/` states 3 or 100.

**An online game is an open game and counts against the same ceiling.** Creating one and
accepting an invite to one are both creates, so both are refused at the ceiling exactly as
a local New Game is, and a player at the cap frees a slot the only way there is — by
deleting a game. There is no separate online allowance and no exemption for a match
somebody else started. On the accepting device the create happens **when the starter's first
payload lands, not when the invitation is accepted** — before that there is no board to
store, and this layer stores no record without one — so the cap bites on the arriving
payload's route rather than on the acceptance.

**Creating an online game for a match id a record already holds is not a second create.** The
existing record is answered back unchanged — not re-titled, not re-stamped — and nothing is
emitted on the change stream, because nothing changed. A duplicate delivery would otherwise
consume a second slot and split one match across two records. That answer comes before both
the title check and the cap.

**The storage layer applies no name fallback.** An online create whose title is empty or
whitespace-only is refused, and that refusal is distinct from the cap refusal so the caller
can tell the two apart; nothing is stored. Supplying a title is the caller's, because a layer
that substitutes a title is a layer that can rename a game. This reaches the online create
alone — a local create still stores what it is handed, since the New Game prompt has already
applied its own default by then. See [Menus and UI](./Menus%20and%20UI.md) → Play Game.

**A rematch is not a create.** No cap check runs on either device when a series moves to its
next game, no second record appears, and a rematch is accepted while the player is at the
ceiling — it continues in the same open game.

**The cap counts only the records that can be read back.** A record that cannot be read is
not in the list the player sees, so counting it would refuse a create against games the
player has no way to find or delete.

**The store never evicts.** A create at the ceiling does not silently remove an existing
game; a slot is freed only by an explicit, player-initiated delete. If the ceiling ever
drops below the number already stored — an entitlement lapsing — nothing here licenses
deleting any of them.

**Reaching the cap is an ordinary, player-reachable condition, not an error**, so a refused
create reports it as a value carrying the effective ceiling and how many are held, rather
than throwing. That lets the caller say "3 of 3" without a second round trip.

**A save against an id the store does not hold writes nothing and creates nothing.** It is
not an upsert: creating that way would be a second creation path past the cap, and it
could resurrect a game a player deleted. It does not throw either — it comes back as a
value the caller can act on, in the same spirit as a refused create, because a save that
silently discards a player's move is the other failure.

**Deleting removes one open game and its whole series** — board, scoreboard and all —
permanently, leaves every other stored game untouched, and touches no preference. Nothing
else in this layer discards a record: a game left mid-play is still there, with its
scoreboard, on the next read.

### Reads return "nothing stored", and defaults resolve above this layer
**Every persistence operation is asynchronous**, because both stores are async on first
open and a synchronous facade would either block startup or lie about readiness.

**Every read returns "nothing stored" — never a default, and never a throw.** An empty
store is a valid state rather than an error. What "nothing stored" *means* is resolved
once, above this layer, by whoever can name the value without inventing it: the theme
layer resolves the default theme because only it knows Neon's UUID, and the state layer
resolves the four toggle defaults because they are plain booleans with a doc-settled
value. Putting a theme constant in `storage/` would trip the hardcoded-theme-value test —
see **Testing** below.

**A record that is present but cannot be read back answers as "nothing stored", exactly as
an id the store never held.** Malformed JSON, a missing or wrong-typed field, and a record
that is well-typed but not a legal board — cell rows of the wrong length, a forced
placement naming no quadrant — all answer the same way. The last of those matters because
such a record decodes without complaint and only fails later, above this layer, where the
failure no longer looks like a storage one.

**A record that cannot be read back is skipped by the list read, and every other stored
game comes back.** Failing the whole read on one bad record would hide every game the
player still has.

**A read stays a read.** A record that failed to decode is left on disk exactly as it is,
neither rewritten nor deleted.

**When the box itself cannot be opened, the app falls back to an in-memory store and still
launches.** A bad documents directory, a stale lock file or a corrupt box tail would
otherwise throw on every relaunch with no UI and no error to show for it. Every read then
answers "nothing stored" — the same doctrine one unreadable record already gets, applied
to the whole store — and nothing written in that session survives. The box on disk is left
exactly as it was: deleting or recreating it to recover would destroy a player's saved
games to fix a read error, which is worse than the error.

**The selected theme is stored as the theme's UUID, not its name**, so renaming a theme
neither changes the stored value nor loses the player's selection.

**The preference store holds those five keys and nothing else.** They are namespaced so
that check is mechanical rather than a judgement call.

### Entitlement state is written down, never minted
**What is stored is the set of product identifiers the store reported, verbatim.** This
layer translates none of them and never mints an entitlement — it writes what it is
handed. What the stored values *mean* is **In-App Purchases and Entitlements** below.

**Only an affirmative store answer overwrites what is held.** A failed, timed-out or
otherwise unanswered query is **not** an answer of "owns nothing", and must not clear or
downgrade stored entitlement state. Read the other way — "whatever Apple reports, whenever
the two disagree" — a dropped network call is a disagreement, and a player's purchases
would be cleared on an offline launch. A failed network call must not revoke something a
player bought.

**Nothing in `storage/` talks to a network, StoreKit included.** The app's one sanctioned
network path is the purchase flow.

<!-- A candidate shape for the persisted Game object — cells, quadrants, activeQuadrant,
     currentPlayer, lastMove, score, firstPlayerThisGame — is sketched in Design Handoff →
     State (Docs/tic-tac-toe/design_handoff_game_ui/README.md). It is a design sketch, not
     a decision taken here. -->

## Audio and Assets

**`audioplayers`** for sound playback.

### One way to play a sound
**Playing a sound is one call that names a moment**, and nothing else in the app plays
audio. A caller says which moment just happened and never constructs a player, names an
asset, or waits for anything. Placing a mark also names whose mark it is, because a theme
may sound the two players differently (see [Theming](./Theming.md) → Placing a mark may
sound different for each player) — it is still one moment, and the only one whose call
takes anything beyond its own name. Which file a moment resolves to is the active theme's
business — see [Theming](./Theming.md) → Architectural Rule — so the layer that plays it
holds no asset path of its own.

**The mute gate lives inside that call.** The sound effects setting is read there, on
every call, and never captured at app start or when the layer is built. Call sites fire
the call unconditionally and never consult the setting themselves: a call site that
checked first would put the rule in as many places as there are sounds, and forgetting it
in one of them is a bug nothing would catch.

**Turning the setting off does two things at once** — it gates every sound that has not
started, and it silences whatever is sounding at that instant, which stops where it is
rather than playing out (see [Theming](./Theming.md) → Global mute). So flipping the
toggle mid-game reaches the sound already in the air, not just the next one.

**Stopping is the layer's own, never a verb offered to callers.** Silencing what is
playing is how the layer answers the setting changing underneath it, so a caller still
has one call and no way to stop a sound, ask whether one is playing, or branch on either.
A stop handed outward would put the mute rule back among the call sites the gate exists
to keep it out of.

**Nothing outside that layer may reach the machinery underneath it.** That is what makes
the gate unbypassable rather than conventional — anything able to reach a player directly
could play a sound around the mute entirely.

**The call is fire-and-forget.** It returns immediately and never reports whether anything
was audible. Gated off by the toggle, silent because the theme cleared that slot, and
failed to load are all indistinguishable to the caller, deliberately: a caller that could
branch on playback state would put audio logic back at the call site.

### Silence is a normal outcome
**A theme slot with no sound in it means that moment is silent**, and that is ordinary
operation rather than an error — nothing is logged, nothing is reported. Fallback happens
when a theme is merged over Neon, not when a sound is played, so this layer performs no
substitution at play time and holds no notion of Neon. See [Theming](./Theming.md) →
Sound Decisions → Sound falls back to Neon.

**A sound that names a file it cannot load is silent to the player too.** The failure is
caught where it happens: no dialog, no banner, and no crash report — this layer adds
nothing to what **Crash Reporting** below collects. What is deliberately not swallowed is
a wiring failure, because hiding one behind a silent no-op turns a broken app into a
merely quiet one.

**Today that means all of it is silent.** Neon's sound slots hold placeholders until the
first generated file lands, and the layer is complete and testable before any of them
exist. Making a moment audible afterwards is a change to the theme definitions and the
asset bundle, never to playback code.

### Music is a separate layer, not another moment
**A one-shot call cannot express music, and that is a fact about the call rather than a
gap in it.** A one-shot fires and ends; music loops, ducks under an effect, pauses when
the app backgrounds and resumes when it returns, and persists across screens instead of
belonging to a moment. Every one of those needs state and verbs a caller drives, and this
call deliberately offers none — the one stop this layer performs is its own answer to the
mute, not something a caller can ask for. Adding music as another moment would produce a
track that plays once and stops.

A theme supplies its own music (see [Theming](./Theming.md) → Music), and whatever plays
it is a sibling of this layer rather than an extension of it. It inherits the theme-driven
rule and the same settings-gate shape, against the Music toggle instead of the sound
effects one — and none of this layer's interface.

**What that sibling offers is one call.** A caller says "play the active theme's music" and
nothing else — no stop, no pause, no is-playing, no ducking, and no background or
foreground handling. Stopping is the layer's own, exactly as it is for sound effects: it
happens from a listener on the Music setting rather than from anything a caller can reach.
Calling that one call again while a track is already playing is what swaps themes, so the
launch call site and a theme change share one mechanism rather than two.

**The loop and its fade are the app's, never the file's.** The player is set to loop, and
the app ramps the volume down before the wrap and back up after it, on timers it schedules
from the track's own duration. It deliberately does not wait on a playback-complete event:
the Android player suppresses that event while looping, so a fade cycle depending on it
would ramp to silence at the first wrap and never come back there, while working by
accident on iOS.

### The audio session is process-wide, and chosen rather than defaulted
**The session is configured once for the whole app**, and it has to be set explicitly: the
audio plugin's own default is not neutral, so leaving it alone ships a policy nobody
picked. Two player-visible behaviors ride on that one choice — whether the game sounds
over a silenced phone, and whether it interrupts whatever the player is already listening
to. They come as a pair and are still open; see [Theming](./Theming.md) → Open Questions.

Because the session is process-wide, a music layer added later shares it and cannot choose
differently. Whatever is settled there binds both.

### Where sound and art assets come from
**Generation lives in its own project-agnostic framework, not a script inside this
project.** The framework lives directly inside the `local-RED-dev` mono repo at
`src/Asset-Gen-Framework`. It is not a separate repository and not a submodule — unlike this
project's own source, which is — it is a shared utility that projects in the mono repo call.
It holds only the plumbing: the Replicate API calls, credential handling, reading the prompt
manifest, the drafts fence, the per-asset record, and checking that a downloaded file's bytes
match the format its entry declared. It holds nothing about any particular asset — no prompt,
no model choice, no filename, no knowledge of themes or slots — which is what lets one
framework serve games that have nothing in common. This project's side of the arrangement is:
it writes the prompt manifest, it says what it wants and what to call it, and it approves what
comes back.

**Generated with Replicate when we actually need them — not now.** This covers both the
sound assets (the Neon buzz, the Classic splat) and the art (the logo): *"I have used
Replicate in the past so will need to build out a clean Replicate API calling mechanism
for this."*

Timing is part of the answer: *"We don't have to start now and it's best to do what we can
without images or music but once needed Replicate can help us out here."*

The requirement on how it gets built, as stated:

> *"You can check out the fey-tactics for the API call however do not take on the system
> from fey-tactics as it's not a good system we just need the APIs and will need to build
> our own system that operates clean and generates no junk. We will have to have
> designated folders for assets. And I would prefer to not have junk scripts lying around.
> Just one script that makes the API call with what we need. Not a script of every asset
> generation."*

Concretely: **one script that makes the API call**, not a generator per asset type;
**designated folders for assets**; no leftover scripts.

Worth confirming at first use: the user notes that the Replicate model
`sourceful/riverflow-2.0-pro` *"does allow for png transparent background images."* That
is recorded as the user's note, not verified against the current model card, and not a
model choice.

A **Replicate agent** may follow — *"we might need to build out a Replicate Agent that
has the skills to utilize Replicate for both audio and images when needed"* — but that
is hedged and explicitly not now, and it would live in the agent system rather than in
this doc.

<!-- Design Handoff → Assets names two third-party dependencies this decision does not
     cover: Inter 400/500/600 (bundled, not from a CDN) and the Phosphor icon set.
     Neither is Replicate-generated. See
     Docs/tic-tac-toe/design_handoff_game_ui/README.md. -->

### One script, and the per-asset inputs are data
**Adding an asset adds an entry to a list, never a second script.** The one script reads a
hand-written prompt manifest — one entry per asset, naming the model, the prompt, the
format and any model parameters — and generates whichever entry it is asked for. That is
what keeps *"not a script of every asset generation"* true as the asset set grows: what
varies per asset is data the user writes, not code.

The manifest is YAML, for the same reason theme files are — it is hand-authored project
data. The script reads it and never writes it, and it invents nothing that belongs in it:
prompts, formats and model ids are the user's to write. A prompt an agent made up would be
recorded as provenance and read back later as a decision.

**The framework is Python.** It is shared across projects rather than being this project's
script, so matching this project's toolchain is not what matters — Python is on every
machine already, and it handles HTTP, the manifest, and the file checks cleanly.

**fey-tactics is consulted for the API call and for nothing else.** It is not part of this
project and is not reachable from it, and Replicate's HTTP API is publicly documented, so
the reference is a convenience rather than a dependency. The weight of the decision is the
prohibition on adopting their system.

### The generator is an authoring tool, not a build step
**Nothing in the app or its build ever runs it.** It is not invoked by `flutter build`,
`flutter run`, `flutter test` or any CI job; no code under `lib/` imports it or shells out
to it; and the app builds, tests and archives on a machine that has never held a Replicate
credential. The credential is read from the environment, never from a committed file, a
flag or a prompt, and never lands in anything the tool writes.

This is what keeps **Fully offline, except for Apple's own services.** under **What the
Design Docs Already Imply** above true — the app makes no Replicate call, because
generation happened on a developer's machine long before the build. It also has to be true
because **CI — local builds only** below leaves nowhere to hold a build-time secret.

### What gets generated, and where it lands
**`assets/images/` and `assets/audio/` are where art and audio ship from, and the
generator writes to neither.** Everything it produces lands in a drafts area first — see
the next subsection — and reaches those folders only by being approved and moved.
`assets/themes/` holds theme YAML and is a destination at neither stage. The app icon sits
outside all of this: it lives in the iOS asset catalog rather than the Flutter `assets/`
tree (see **Distribution and Release** → **The app icon**), and this rule widens to reach
it — it is generated here too, and lands in the asset catalog rather than `assets/`.

**Every prompt manifest entry carries the exact output filename, and the framework writes
that name and never invents one** — that is what keeps it free of any knowledge about
themes or slots. Computing that name from the theme and the slot it fills is this project's
rule: it is what gives one source of truth for the path a theme's YAML points at, makes the
name an asset is drafted under the name it ships under, and theme-prefixes every generated
file, the logo included, so one theme can override a slot without colliding with another
theme's file in a flat folder.

**What it owes is per theme, not per game** — each theme's playable sound slots, its
music track and its main-menu logo (see [Theming](./Theming.md) → What a Theme Controls).
Mark art is produced here too when a theme names it: that section calls an image *"the
real answer for a theme."* Neon and Classic draw their marks as glyphs; Sewing's scissors
and button are mark art, so it owes mark images.

**Logos ship as PNG with alpha at 1x, 2x and 3x, all three downscaled from one render.**
Flutter treats the three as the same artwork at different densities, so generating each
independently would make the logo change appearance from device to device. A render that
is not square, or too small to downscale from, is rejected rather than cropped:
crop-center, crop-top, letterbox and squash all satisfy "make it square" and most of them
mangle a logo, so the fix belongs in what was asked for, not in the tool.

**A sound's format is declared per entry and checked against the bytes that arrive**, so a
file never contradicts its own extension. `.mp3` is what the audio layer is written
against, and `stability-ai/stable-audio-2.5` returns `.mp3` natively. That model exposes no
loop and no fade input of any kind, which is why the seamless-loop request lives in the
prompt text alone and may not be honoured, and why the fade at the loop point is the app's
job at playback.

**Music is generated here too.** A theme supplies its own music (see
[Theming](./Theming.md) → Music), and its track is a prompt manifest entry like any
other sound. The track carries no fade of its own — the app fades it in and out at
playback — so what the generator owes is the bare track.

### Sound effects are normalised after generation
**Every sound effect is levelled to sit under the music by a tool in this repo, not by
asking the prompt for it.** Each effect plays over a continuously looping music track, so
each one has to sit under it — and the generator cannot hit a loudness reliably however
the prompt is worded. One effect came back six decibels louder than the music, on the
sound that fires on every single move. So the level is set mechanically after generation
rather than asked for again.

**The tool measures first and applies only the difference.** Running it twice never
attenuates a file twice, and a file already at level is left alone rather than re-encoded.
It refuses a theme's music track — the music is the reference the effects are measured
against, not something to normalise against itself — and it fails loudly when a file lands
outside the band it aims for, rather than reporting success on a file it did not fix.
Re-run it unmodified after any effect is regenerated; it measures whatever the model
produced next rather than encoding today's levels.

**It measures and re-encodes with `ffmpeg`.** That is a developer's dependency, the same
as the generator itself: the app does not use it, and nothing in the build runs either
one — see **The generator is an authoring tool, not a build step** above.

### Nothing generated is applied directly — drafts, then approval
As stated:

> *"WE can generate the content fenced in however i never what the content to be directly
> applyed. we want each asset to be created into a assests_Draft folder of some type then
> approved and moved to the real folder to be implamented and tracked by themes. So fence
> it into a Draft folder first. Approval is my just saying yes use this assest X then move
> it along."*

So generation is two stages. **The drafts area lives inside this project, kept separate
from the shipped asset folders, and it is the only place the framework writes.** A draft
sits next to where it would eventually ship, so approving one is a move within this
repository rather than a copy across repositories. The framework is told where to write and
can reach nowhere else. What that area is called is still code's to settle — the decision
here is the fence, not the path.

**Approval is a person saying yes, and it is the user's to give.** There is no score, no
threshold and nothing automatic: the user says use this one, and only then does the asset
move into its shipped folder to be implemented and tracked by themes.

**The fence is structural rather than a rule the tool has to remember.** Approved art does
not live anywhere the generator can write, so a rerun cannot clobber it — the guarantee
holds even if the tool is wrong about everything else.

**A drafts area is not a shipped location.** It is not declared in `pubspec.yaml` and
nothing in it reaches the bundle, which is what makes drafting cheap: generate, look,
discard, generate again, with nothing at stake until the move.

### Declared in `pubspec.yaml`, or it does not ship
**The declaration for `assets/images/` and `assets/audio/` lands in the same change as the
first approved file in each.** It is a hand edit and not something the generator writes:
`pubspec.yaml` is pinned and hand-maintained, and a tool that loaded and re-dumped it
would reformat the file and could clobber the theme declaration already there. The drafts
area is never declared.

**Watch out for:** approving an asset is two moves, and the second is the one that gets
forgotten. Move the file into its shipped folder without the declaration and the bundle
contains nothing — the sound never plays, the logo renders nothing, and every test still
passes. A working-looking, non-functioning feature.

### Regenerating, and leaving nothing behind
**A run leaves the drafted assets and one record, and nothing else** — no temp files, no
scratch scripts, no response dumps, no half-written asset. That is *"operates clean and
generates no junk"* in operational form: a run that dies partway leaves the tree as it was
rather than leaving a truncated file behind.

**One record per asset, holding the last generation only.** Not a history and not an
append-only log — regenerating an asset replaces that asset's entry rather than adding to
it: *"Im more happy about just the one record per asset vs Every record."* An entry holds
the pinned model version, the prompt, the seed and the parameters that produced the asset.
**The model version is always pinned**, never a bare model name, which is the whole reason
the record is worth keeping.

**What the record is for is knowing what was last asked for, so the next request is a
change from it** rather than a fresh invention: *"So we know what we last asked for and
chagne from there."*

**It is contained and trashable.** One file the generator owns, written nowhere else and
never into any other document — *"i dont want asset generation to spam out of controle or
palute other documents."* Deleting it is survivable: it costs the ability to tweak from
the last request, and nothing else.

**Regenerating is deliberate and one named asset at a time.** There is no bulk regenerate,
because a single command that redoes everything is exactly how generation gets out of
control; and an existing draft is replaced only when the rerun says so explicitly.

## In-App Purchases and Entitlements

**The game now sells two things.** A paid theme beyond the free set (Neon, Classic Red vs
Blue and Sewing), and a **$4.99 unlock that raises the open-game cap from 3 to 100.** See
[Theming](./Theming.md) → Free and Paid Themes, and [Menus and UI](./Menus%20and%20UI.md)
→ Play Game → Where It Takes You → How many open games we keep.

**Consequence for offline status:** in-app purchases require StoreKit, which needs network
access and a restore-purchases path tied to the Apple ID. StoreKit is one of the two
exceptions to **Fully offline** under **What the Design Docs Already Imply** above; Game
Center is the other.

### The store plugin — Flutter's official `in_app_purchase`
**The purchase layer is the official Flutter `in_app_purchase` plugin**, with
`in_app_purchase_storekit` under it on iOS. That package's StoreKit 2 path is the default
on iOS 15 and up, which is the floor **Platform and Targets** → *Minimum iOS version*
sets — so the `Transaction.currentEntitlements` semantics this section is built on are
what the app actually gets, rather than something it has to opt into.

**Stripe and third-party purchase services — RevenueCat and the like — are out.** Apple
requires digital goods to be sold through in-app purchase, and a purchase service of our
own would mean a server and player accounts. There is no server and there are no accounts.

**`restorePurchases()` is silent, and `AppStore.sync()` is the one the player sees.** The
plugin's `restorePurchases()` reads `Transaction.currentEntitlements` without showing the
player anything, and delivers what it finds as a batch of `restored` events on the
purchase stream. A player who owns nothing produces no events at all, so the events are
not what says the read finished — only the returned Future completing says that.
`AppStore.sync()` is a separate call, reached through
`InAppPurchaseStoreKitPlatformAddition`, and it does prompt for an Apple ID. **Restore
purchases runs the sync first, then the silent read.**

### Entitlements — Apple stores them, no backend needed
**No receipt-validation server, and no backend of ours.** StoreKit provides
`Transaction.currentEntitlements` — the set of currently-valid transactions for this app
under the signed-in Apple ID, cryptographically signed by Apple and verified on device.
That is the authoritative answer to "does this player own this." `Transaction.all` gives
full purchase history if it is ever needed.

Restore for non-consumables is largely automatic: signing in on a new device repopulates
entitlements without the player doing anything. The visible **Restore purchases** control
is still required by Apple's review guidelines, and what it runs is `AppStore.sync()`
followed by the silent `currentEntitlements` read — see *The store plugin — Flutter's
official `in_app_purchase`* above. The sync is the half the player sees, because it
prompts for an Apple ID; the read is the half that produces the answer. So the control is
a compliance requirement more than a functional one.

On-device verification is sufficient for an app this size.

**Purchases are per platform.** An entitlement lives with the Apple ID that bought it, so
if the game ever ships on Android a theme bought on an iPhone is bought again there.
Nothing links a purchase across platforms, because linking them needs accounts and a
server of ours, and there are neither.

**Consequence for the architecture: Apple is the record of truth and it is queryable at
runtime.** Any locally stored entitlement state is an offline convenience, not the record.
A refunded or lapsed purchase stops appearing in `currentEntitlements` — that is what
answers "what happens when an entitlement goes away." What the purchase stream says about
it is a different matter: see *Committing an answer — all of it, in order, to memory and
disk* below.

**The entitlement provider's shape — last-known plus refresh.** Entitlement state is exposed
as a plain value, seeded from the locally cached copy and refreshed when the store answers —
not as an async wrapper every consumer must branch on. This is the same class of decision as
**State Management** above.

Consequences:
- Consumers never handle a "pending" case; they always get a usable answer.
- A paying player never sees their purchased content as locked while a query is in flight —
  which is the failure the alternative produces. The last known answer is what gating uses
  until a newer one arrives, and the free tier is what a device that has never stored
  anything reports — never what the app falls back to because an answer has not landed yet.
- The value carries an indication of whether it is still provisional, so a consumer that
  cares can tell.

### Ownership is keyed by product, and only the store may change it
**What the app holds is a set of store product identifiers** — the products the player
owns, not the things those products unlock. Asking whether a theme is owned resolves
forward: which product unlocks this theme, and is that product in the set? Nothing maps
backwards from a product to a theme, and nothing needs to. A product identifier has no
relationship to a display name, so renaming a theme cannot orphan an entitlement the player
paid for. What gets written down, and under what rule, is **Persistence and Serialization**
→ *Entitlement state is written down, never minted*.

**Paid-ness is derived, not recorded.** A theme is paid because it is not one of the free
themes — see [Theming](./Theming.md) → Free and Paid Themes. No theme file, catalog
entry or ownership marker records it, so there is no second list of paid themes to keep
in step with the first.

**The purchasable theme is Sewing, once purchasing is built.** Sewing ships free at first
release and becomes the paid theme once the purchase flow lands — none of the other free
themes becomes the paid one. What that means for the store record is
**Distribution and Release** → *The store-side products*; when the purchase flow lands is
**Open Questions**.

**Every theme is in exactly one of three states — free, owned, or locked**, and that is what
the theme selection list labels its rows from.

**The open-game cap is a value this model supplies, not a constant written anywhere else.**
The storage layer reads it rather than defining it — see **Persistence and Serialization** →
*The cap is enforced on create, and the store never evicts* — and no screen defines it
either.

**Nothing anywhere in the app mints an entitlement.** Every entitlement held originates in
an answer from the store. There is no local grant and no debug-only setter in shipped code:
the ability to hand out an entitlement is not a thing that exists. **Persistence and
Serialization** forbids it of the storage layer; this forbids it of everything.

**An affirmative store answer replaces what is held; it never adds to it.** Replacing is
what makes a refund or a revocation take effect at all — an answer that could only add would
never be able to take anything away, and the loss case above would be unreachable.

### Committing an answer — all of it, in order, to memory and disk
**The store is asked once at every cold launch, and again whenever the player uses Restore.**
An answer from a previous session is last-known, never confirmation, so every session asks
for itself. A design that only asked when the purchases screen opened would run the whole
session on a stale answer.

**A store answer is always a complete snapshot of what the player currently owns**, never a
set assembled from a single transaction that happened to arrive. Partial answers and replace
semantics cannot coexist: a fragment applied as a replacement silently drops everything it
does not mention.

**No event on the purchase stream is trusted for what it claims to be.** The plugin
forwards a refund or a revocation tagged `purchased`, so an app that read an entitlement
off the event's status would hand back the thing Apple just took away. Every event is a
signal to re-read the whole owned set and commit that, and `currentEntitlements` already
leaves revoked products out — so the re-read is the answer and the event is only the
prompt.

**An older answer never overwrites a newer one, and "older" means asked earlier, not arrived
earlier.** Two questions can be in flight at once — the one every launch asks, and the one a
transaction resolving out of band provokes — and the slow one can land last while carrying
the older picture. Applied, it silently revokes something the player just obtained. In the
wild that reads as *"it forgot what I bought"*: timing-dependent, and it will not reproduce
on demand.

**Memory and disk are updated together, in one place.** Every answer the app accepts — from
launch, from restore, from a purchase, from a transaction that resolved out of band — goes
through the same commit, so no path can update one and forget the other. Forgetting the disk
half gives a player who buys the unlock, sees 100 slots, quits and reopens to 3, with no
error and nothing in any log.

### What a player is owed, with or without a network
- **The game launches and plays with no network and no store.** A purchase check that cannot
  complete does not block launch, does not block starting or resuming a game, and does not
  put an error on screen that has to be dismissed to keep playing.
- **Free content is never gated.** A player with no purchases, and a player whose store query
  never completed, reaches every free theme.
- **A purchase takes effect immediately.** A completed purchase or restore reaches everything
  that gates on it within the same session, with no restart.
- **What is bought stays bought.** Both products are permanent once purchased — not consumed,
  not expiring, and never charged again on a device that already has them. The store-side
  half of that is **Distribution and Release** → *The store-side products*.
- **An app that shows the free tier until Restore is pressed is defective, not cautious.**
  Entitlements arrive on a new device from the launch query above; the visible control is a
  review requirement, not the mechanism.
- **A locked theme still previews.** Ownership withholds selection, not the theme's values —
  a locked row reads as buyable, not broken.

### Buying ends one of four ways, and one of them ends later
**A purchase ends as success, cancelled, failed, or pending, and only success produces an
entitlement.** Nothing else in the app can produce one.

**Pending is the normal case here, not the rare one.** The app is in the Kids Category, so
parental approval is the expected purchase path: a parent approves minutes or days later,
out of band, very likely while this app is not the one asking. **A purchase approved that way
still reaches the player.** The failure this forbids is the natural implementation — await
the purchase, treat anything that is not success as not-success, return — where the parent
approves, nobody is listening, and the child never receives what was bought, while every
other part of the flow looks correct.

What the player is *shown* for each of the four is not settled — see **Open Questions**.

### Prices come from the store at runtime
**Every price shown is read from the store at runtime and localized. No price is hardcoded
anywhere in the app.** The **$4.99** in these docs is the number to configure on the store
record, not a string to render: a player in another currency sees their own, and a price
changed on the record reaches the app without a build.

### The parental gate — a word problem, every time
**The gate challenges with an arithmetic problem stated in words, answered with a number** —
*"Enter the answer: seven times eight."* **The operands are spelled out as words rather than
digits**, and that is the load-bearing part: digits are solvable by a child who can count,
while the word form defeats pre-readers and early readers alike. The problem is a
multiplication of two whole numbers from 2 to 9, so the smallest answer is 4 and the largest
81, and it is answered by typing digits into a field that takes no more than two of them.

**One problem per raise, fixed for all three attempts** — a wrong answer does not swap the
question out from under the person answering it. The next raise generates a fresh one, and
two raises in a row never show the same problem; the operands are interchangeable for that
test, so *"seven times eight"* and *"eight times seven"* are one problem. The gate remembers
only the previous raise's problem, in memory and never written down, so the first raise after
a launch has nothing to avoid.

**Three wrong attempts end the raise**, and the third wrong answer is what ends it: the gate
stops asking, says the tries are used up, and the guarded action never runs — for a purchase,
without ever reaching the store. Every way out from there reports the same out-of-attempts
result, never an abandon. Nothing imposes a cooldown, so the gate can be raised again
straight away, and that raise gets its own three attempts.

**Leaving the gate without answering, while attempts remain, abandons the raise** — the
pending action is dropped, nothing runs, and no attempt is spent.

**A raise resolves exactly once, and the gate is what decides it.** The first of a pass, a
third wrong answer or an abandon wins, and no later signal about that raise changes the
outcome or answers a second time. The pending action is consumed in the same step that
resolves the raise, so it runs exactly once however many signals arrive. If it throws, the
gate still closes and the error reaches the guard's caller rather than being swallowed.

**A pass is good for one purchase and nothing else** — or for one entry into online play,
which is worth exactly one pass the same way. There is no remembered pass — the next
purchase raises the gate again, immediately after a passed one included. This also avoids
having to define "session" at all: cold launch, foreground return and dismissing a surface
are three different answers and none of them is obviously right.

**Restore is not gated.** Restore spends no money.

**The gate is enforced at the purchase itself, not by whatever raises it.** No purchase can
be initiated without passing it, and the surfaces hosting the purchase controls implement no
gate of their own — which is what [Menus and UI](./Menus%20and%20UI.md) → Settings Menu →
Purchases means by keeping one parental gate in one place. Moving the challenge out to the
caller and passing an assurance inward would weaken the guarantee from enforced to
conventionally observed, which is the whole thing the gate exists for.

**The only way past the gate is to hand it the action.** It publishes no pass value a caller
can hold, store or present back to it, and nothing accepts an assurance that the gate was
passed somewhere else. A caller hands over the action and learns what happened to it, which
is a report rather than an authorisation — holding one gets a caller nothing.

**Two guards, and one of six answers.** One guards a purchase; the other guards entry into
online play and takes a resolved Game Center session alongside the action (**Kids Category**
below). Each answers exactly one of: the action ran, either after a pass or because no gate
was owed; refused without asking; no resolved session to decide from; busy; abandoned; or out
of attempts. Six distinct values a caller branches on rather than one flag or a failure
carrying a message, for the same reason the Game Center bridge gives for its own. The answer
arrives when the gate closes, and on a pass that is after the action's own work has finished;
refused, busy and no-session come back immediately, having put nothing on screen.

**Busy means a raise was already up.** A second raise while one is pending does nothing at
all — no second surface, no second problem — and never replaces the pending action.

Why the gate exists at all is **Kids Category** below.

## Online Play

**Online play is remote play over Apple Game Center turn-based matches**, and it is being
built as part of this game's work. Apple holds the match data, the matchmaking, the invites,
the player identity and the "your turn" push, so the app runs no service of its own and
collects no identity of its own. It is iOS only. Same-room play — Bluetooth, peer-to-peer,
two phones in one room — is not wanted and is not built.

**The bridge is a Swift platform channel.** No Flutter package wraps Game Center's
turn-based matches, so the GameKit calls are written in Swift on the iOS side and reached
from Dart over a channel. **The Dart side is split in two: the pure decisions live in
`lib/online/`, and everything that faces the channel lives in `lib/gamecenter/`.** A scan
over `lib/online/`'s imports finds no Flutter, no `dart:ui`, no Hive and no platform
channel, held the way `engine/`'s purity is. Both decisions a turn turns on — what the bytes
a match carries look like, and whether bytes that arrived may be applied — are made there,
against the engine alone, so the channel code cannot creep into them. `lib/gamecenter/`
holds the channel-backed bridge, the fake that stands in for it, the session state and the
handoff from a found match to a stored game.

**Finding an opponent is Apple's matchmaker screen, not ours.** It offers Play Now, which
pairs the player with a random opponent, and Invite Friends, which covers Game Center
friends and contacts and can send the invite through Messages. There is no invite-link API,
so nothing generates a shareable link and nothing has to.

**The match carries the board as JSON, and Apple caps match data at 64 KB.** A whole
position and its series is a few KB, so the cap is headroom rather than a constraint today —
but it is a hard ceiling, and anything later added to the record spends against it.

**What crosses the wire is the board as JSON in an envelope of exactly three keys** — the
payload format version, the series id, and the board — encoded as UTF-8 bytes, because Game
Center's match data is bytes. Nothing else crosses: no nickname, no player id, no turn
marker, no timestamps, and **no match id**. The match id is not in the payload; it is what
the match was delivered under, and it travels alongside the bytes to whatever handles them.
The version key is on the wire for the same reason every persisted record carries a version
stamp, only more so — two devices on different app versions is the ordinary case here rather
than the rare one.

**The encoder refuses to produce a payload over 48 KB**, throwing rather than making a silent
oversized send. That keeps headroom under Apple's hard ceiling, and a worst-case board — 81
cells marked, nine quadrant states with their winning lines, a long-running score — is
nowhere near it. Throwing is right here and nowhere else in online play: the encoder runs
before anything is sent, on this device's own data, so an oversized payload is a defect in
what was built rather than something that arrived from outside.

**Turns never time out.** Every turn is ended with `GKTurnTimeoutNone` — GameKit takes the
timeout on each `endTurn` rather than at creation, so that is where the app states it — and a
match waits as long as it takes for the other player to move, days or forever.

**A player who wants out of an online game deletes it from the open-games list**, the same as
any other open game, and **deleting resigns the match**, so the other player is not left
waiting on a turn that will never come. The resign goes out first and the record is removed
after, but it is best-effort: a resign Apple refuses, or one attempted with no network, never
blocks or undoes the delete — a game that cannot be deleted while the phone is offline is
worse than an opponent left waiting. Resigning is also what makes a delete stick, since a
resigned match sends this phone no more turns. Nothing is written to mark a resigned match:
the record is gone, so there is nowhere to write it, and an event that later arrives for that
match is dropped. Deleting a game on this phone calls nothing. See
[Menus and UI](./Menus%20and%20UI.md) → Deleting an open game.

**A rematch online is a new match with a new id.** Apple's rematch mints a fresh match
rather than reopening the finished one, so nothing may treat a match id as stable across a
series.

**The series id is what stays constant while the match id changes.** It is opaque, unique
across devices, never parsed and never displayed, and it exists because the match id cannot
serve: a rematch continues in the same open game with the scoreboard intact, so something
stable has to cross the wire, and the record id cannot — it is minted per device. It has
exactly two sources and no third: the device that **starts** the match mints it, and a device
receiving the first payload of a series it does not hold **copies it out of that payload**.
Both devices hold the same series id from the first turn onward, which is what lets a
rematch's fresh match id find the record it belongs to.

**A board that arrives is replayed against the rules engine before it is believed, and which
board it is measured against is decided by the stored board — never by the match id.** A
stored board still in progress is measured against itself: the arriving board is applied only
if some single legal move from the stored board produces it. A stored board that is finished
is measured against the next game of the series instead, and there the arriving board is
accepted if it equals that next board or is one legal move from it — **zero or one move, and
both are ordinary**, because a rematch's initiator ends its turn with the fresh board
untouched when the engine says the other side goes first. Validation enumerates the legal
moves and applies them; it never feeds the engine a board and catches what it throws, since
the engine's throw on an illegal move is a contract violation no caller is meant to catch.

**A payload is applied only when it is the opponent's turn to have sent it**, tested on the
board the arriving one is measured against — never on a finished board, whose current player
the engine leaves on the last mover, the winner of the game that just ended, who is not who
goes first in the next one. The turn test and the reachability test both hold and neither
replaces the other: reachability alone would accept a board this device itself produced and
had echoed back to it.

**A board equal to the stored one is a re-delivery, not a violation** — nothing is written,
and it is reported as its own outcome. Game Center re-delivers, and treating that as a
corrupt payload would raise an error on an ordinary event.

**Everything else is refused, and nothing is written on any refusal**: a board two moves ahead
or otherwise unreachable, a payload that arrived when it was this device's own turn, an
arriving match id that differs from the stored one while the stored board is still in
progress, a payload naming a series the record does not hold, a payload that will not decode,
and one on a version this build does not recognise. Each is a distinct value the caller can
branch on rather than one failure carrying a message — a caller that cannot tell a
re-delivery from a corrupt payload cannot behave differently on them. What the player is
shown for any of them is not settled — see **Open Questions**.

**An arriving turn is routed to its own stored record by the match id it was delivered
under.** A record held for that match id takes it; failing that, the payload's series id finds
the record, which is how a rematch's fresh match id reaches the game it belongs to; and
failing both, the payload is the first of a series this device does not hold, and the record
is created here. An event that carries no payload applies nothing — that is the ordinary
starter's-own-match event, which GameKit reports before either side has put data in the match.
An event whose local participant has already quit and whose match this device holds no record
for is dropped: this device has left that match and there is nothing to apply it to. A payload
that will not decode with no record to route it to is refused on its own, there being no
stored series to measure it against.

**The accepting device's create is refused unless the arriving board is reachable from a fresh
series** — the fresh board itself, or one legal move from it — judged by the same rules every
arriving board is judged by. A create is the one arrival path with no stored board to measure
against, so without this it is the one path where an arbitrary board would be stored
unchecked. A refused create writes nothing. The created record plays Player Two, takes the
payload's series id and the event's match id, and is titled with the opponent's nickname,
falling back to the same placeholder a game on this phone defaults to.

**The opponent's name resolves through these same events.** The rename fires only when the
event names a non-empty nickname, the stored title is still the placeholder, and the two
differ; if any of the three fails, no store call is made at all rather than one the store then
refuses. It runs on every event that gets that far, whether or not a payload was applied and
whether the record was just created or already held. An opponent whose real nickname is the
placeholder is renamed to itself, which is a no-op rather than a defect.

**Every outcome of an arriving turn is published on a stream as well as answered** — applied,
created, a re-delivery, each refusal, and the drops above. Nothing renders any of them; the
stream is the seam the board screen and the open-games list read. `didBecomeActive` is carried
through and nothing branches on it: Apple defines it as "this event launched or foregrounded
the app", which is true of the ordinary case too, and a match created from the sheet while the
app is already foreground arrives with it false — so it is a fact about the event rather than
anything a game can act on.

**A local move is written to this device's store only after Game Center accepts the turn.**
The confirming tap on an online game puts the move on the session board and marks the game as
awaiting handoff, saves nothing, and hands the encoded board to Game Center; only on Apple's
ok is that board written, under the same match id it was sent under. A stored board showing
the opponent to move on a turn this device never handed off would be a game neither device can
continue, and it would survive a relaunch. The match id is chosen once, before the send, and
the write reuses it rather than re-reading the record — re-reading is what would let the send
and the write disagree about which match the board belongs to. A send Apple accepted whose
write the store then refuses is its own answered value: the board stays on the session as
sent and the turn is never re-sent, because the opponent already holds it. See
[Menus and UI](./Menus%20and%20UI.md) → When a game is written to storage.

**While a move is awaiting handoff, that game refuses another one.** A second move on a turn
the first has not handed off would put this device two moves ahead of the opponent, which
their device refuses as unreachable and nothing can repair. A failed send writes nothing and
keeps the confirmed move on the board, and sending again re-sends that same board — a retry,
not a second move, which the refusal is exactly what makes safe. A relaunch loses an unsent
move and shows the board as it stood before it, which is what the opponent sees too. One send
is in flight at a time, and a second while one is unanswered never reaches the platform.

**A rematch's handoff follows the same rule and stores no marker to do it.** The initiator
holds Apple's new match id in the session only, hands off the next game's board under that id
— the fresh board, plus its own first move when the engine says it goes first — and only on ok
writes the next game's board and the new match id together, in the single write that operation
already is. A relaunch loses the held id: the player taps rematch again, Apple mints another
match, and the first is abandoned with nothing stored pointing at it. That is acceptable,
because a match neither player ever played is invisible to both devices and costs no slot.

**The device that starts the match plays Player One in the first game of the series; the
device that accepts plays Player Two.** Game Center makes the match's creator the current
participant, so the creator moves first, and the first game's first player is Player One. The
advantage does not accumulate: from the second game the winner of the last game goes first,
and a tie leaves it where it was — see [Rules](./Rules.md) → Turn Order Across Games. The side
is stored on the record once, at create, and read from there afterwards rather than
re-derived from the match.

**Game Center sign-in happens when the player first enters online play.** The app
authenticates on the tap that enters online play, and once at launch when — and only when —
the store already holds at least one online game. That launch-time sign-in is what makes a
"your turn" notification work at all: GameKit delivers a turn event only to a registered
listener, and the listener is registered on the first successful authentication. Holding an
online game is the narrowest condition that reaches it, so a player who never touches online
play still never sees Game Center's sign-in banner.

**When Apple reports multiplayer is not allowed for the account, online play is refused
with a message rather than an error.** `GKLocalPlayer.isMultiplayerGamingRestricted`
carries a parent's "don't allow" setting. The restriction is only known once the player is
signed in, so the **Play online** button is neither hidden nor disabled — it sits on the
menu like any other, and the tap comes back with a calm, kid-facing message. See
[Menus and UI](./Menus%20and%20UI.md) → Play online → Where It Takes You.

**Random opponents versus friends-only is the parent's Game Center setting, and the app
adds nothing of its own.** Game Center enforces the friends-only choice itself. The app
never forces automatch-only mode — that throws for a friends-only child — and it never
imposes a restriction Apple has not.

**Online games count against the open-game cap**, the same 3-by-default, 100-with-the-unlock
ceiling as games on this phone — see **Persistence and Serialization** → *The cap is
enforced on create, and the store never evicts*.

The parental gate that online play raises for a child's account is **Kids Category** below.

### The board screen drives a turn

**An online game plays on the same board screen as a game on this phone**, and that screen
derives one state to say what it may do: waiting on the opponent, your turn, a move being
sent, a send that failed, or game over. It is derived from the session alone and never
stored — whose turn it is is the board's current player compared against the side this
device plays. The order they are tested in is what makes them right: a failed send, then a
send in flight, then a finished board, and only then whose turn it is. **A send in flight
and a failed send outrank a finished board**, because the move that ends the game still has
to be handed off and a failed send of it has to stay retryable — a winning move whose send
fails shows the retry, not only the result card. A finished board outranks whose turn it
is, since its current player is the winner rather than someone to move.

**Only your own turn takes a move.** A tap on the opponent's turn is refused by the state
layer's tap gate, as its own distinct refusal, checked before legality so it answers the
same whatever cell it lands on. A refused tap does nothing at all — no mark, no pending
selection, no shake, no message and no buzz.

**The lock is taps and nothing else.** While waiting on the opponent the board renders
exactly as it does on your own turn: the forced-quadrant highlight and the last-move
highlight both stay drawn, nothing dims and nothing is added. Which quadrant the opponent
must play in is information the player wants, and the two highlights are the board's core
readability — so there is no dimming, no veil and no online-only treatment to design. How
the lock is *not* built is **Rendering the Board** above.

**The confirming tap makes one call, and the screen never sends of its own accord.** The
state layer is what applies the move, marks the game awaiting handoff and hands the encoded
board to Game Center; the retry on a failed send is the only send the screen itself asks
for. A retry reads as a send in flight rather than as still failed — the record of the last
failure clears the moment a send is actually attempted, past every refusal and before the
platform call. A send Apple accepts says nothing of its own: the board simply goes back to
waiting on the opponent.

**The screen listens to arriving-turn outcomes for as long as it is mounted, and subscribes
before it loads its own game.** That stream replays nothing, so an outcome landing between
mount and the load returning would otherwise be lost. It constructs no receiver of its own —
one receiver subscribes for the app's lifetime. It acts on exactly two outcomes, a turn
applied and a record created, and only when the record they name is the one on screen;
every other outcome changes nothing there, including a re-delivery and every refusal.

**On one of those two it re-reads the record and replaces the board and the online values
from it.** The re-read draws no loading state: withholding the board until a read lands
belongs to a screen's first read, and blanking the board to a spinner on every opponent
move would be a defect of its own rather than that rule being honoured. What it applies is
guarded — it is dropped whole if the player has left for another game by the time the read
lands, judged by the record id the same way a send is; a read that answers nothing, the
record being gone, leaves the session exactly as it was; and a rematch's held match id is
left untouched, belonging to a handoff in flight rather than to the record just re-read.
The re-read clears the pending, unconfirmed selection and its preview, since one computed
against the board that was just replaced is no longer a legal move on the board in front of
the player; it clears any running win celebration, which would otherwise lock input on a
board that is now this side's to play; and it clears the awaiting-handoff and failed-send
marks, the stored board being authoritative once a turn has arrived for it. Nothing else
runs — input unlocks because the board's current player is now the local side, and a
re-read is safe to run repeatedly, including one landing while the screen's own first load
is still in flight.

**Opening an online game is playing, not entering.** From the open-games list or from a
"your turn" notification, the screen shows the current stored board and nothing more: it
makes no Game Center call, raises no sign-in and raises no parental gate. See **Kids
Category** below.

### The channel contract

**Three channels carry everything, and each side names them in exactly one file.** A method
channel, `com.ehrendavis.tictactoeextreme/gamecenter`, carries calls and their replies; an
event channel, `com.ehrendavis.tictactoeextreme/gamecenter/session`, carries session changes
GameKit originates; and a second event channel,
`com.ehrendavis.tictactoeextreme/gamecenter/turns`, carries the turn events it originates.
Turn events are not folded into the session channel: that channel replays its current value
on subscribe and lets a malformed event leave the last known session standing, and neither
holds for a turn event, which has no current value and must not be silently coalesced. The
prefix is the bundle identifier. All three use Flutter's standard message codec, and all
three are hand-written — no channel generator is a dependency this app takes.

**The method channel exposes exactly five methods**: `authenticate`, `presentMatchmaker`,
`loadMatches`, `endTurn` and `resignMatch`. The first three take no argument; `endTurn` takes
a match id and the encoded payload bytes, and `resignMatch` takes a match id alone. Each of
those two answers a `status` of `ok`, or `failed` with a non-empty message — a match id
GameKit does not hold, a match the local player is not in, and a GameKit failure are all the
same one failure, since no caller has a second behaviour to take on them. Called while the
session is not authenticated, each answers failed and sends no platform call, the same
refusal the matchmaker and the match load already make. Any other name answers
not-implemented.

**No outcome on this channel is an error.** A declined sign-in, a restricted account, a
cancelled matchmaker and a GameKit failure are all reply values: the Swift side never answers
a `FlutterError`, and nothing on the Dart interface throws — including on a build with no
Swift side at all, which is every `flutter test` run. Every failure value carries a non-empty
message, and nothing branches on that text.

**`authenticate` answers a session map** keyed `state` — `unauthenticated`, `authenticated`
or `restricted` — carrying `nickname` and `isUnderage` when authenticated, `isUnderage` alone
when restricted, and an optional `message` saying why an unauthenticated result came back.
The event channel emits the same map: the current value on subscribe, and every later change.
The in-flight `authenticating` state never crosses the channel in either direction — the Dart
side publishes that one itself.

**`presentMatchmaker` answers `found`, `cancelled` or `failed`** — a match map on `found`, a
message on `failed`. **`loadMatches` answers `ok` with a list of match maps, possibly empty,
or `failed` with a message.**

**A match map is exactly six keys**: `matchId`, `status` (`matching`, `open`, `ended` or
`unknown`), `participants`, `localParticipantIndex`, `currentParticipantIndex` — null when the
match has no current participant — and `hasData`. A participant is a nickname and whether it
is the local player, and the list is in GameKit's own order, which is the order turns rotate
in; a participant Apple has not resolved carries the empty string, the ordinary case for a
Play Now match whose opponent does not exist yet. `hasData` is read from *loaded* match data —
GameKit leaves a match's data nil until it is loaded, so the Swift side loads it before
describing a match, or every match of a series would look like a fresh one. Whose turn it is
on the board is still engine state and is never read off `currentParticipantIndex`.

**`endTurn` hands the payload to GameKit verbatim**, with the next participants being every
participant of the match that is not the local player, in GameKit's own order.

**Resigning quits the local participant and changes nothing else.** GameKit offers no single
call covering both cases and the in-turn form fails when called out of turn, so the bridge
picks by whether the local player is the match's current participant. The in-turn form is
handed the match's own loaded data unchanged — resigning is not a move, so the board the
other device sees must not change, and GameKit requires match data there, so passing empty
data would wipe the opponent's board. Only the local participant's outcome is set.

**A turn event is exactly five keys**: `matchId`, the six-key `match` map built from the
match it arrived for, `matchData` — the match's loaded data as bytes, or null when it holds
none — `didBecomeActive` verbatim, and `localParticipantQuit`, true when the local
participant is done with a quit outcome. The match id is a top-level key as well as a field
of `match` because it is what routes the event, and it travels alongside the bytes rather
than inside them. The Swift side loads the match's data before emitting, exactly as it does
before describing a match, or every event would carry no payload; a match whose data fails to
load, or whose local participant cannot be resolved, emits nothing. An event is emitted even
while a matchmaker presentation is pending — it still reaches the receiver and is routed by
match id — and which event completes that presentation is unaffected.

**Turn events that arrive with no Dart subscriber are buffered and replayed**, in arrival
order, on the next subscribe and again after a cancel, and the buffer is cleared as it is
replayed. It holds at most one event per match id: a second event for a match already
buffered replaces that entry in place and keeps its position, so the buffer cannot grow
without bound and a superseded board is never replayed. Nothing about this depends on how the
app was launched — an event that launched the app is handled exactly as one that arrived
while it was running.

**The Dart side subscribes to the turn channel lazily, on its first listener**, unlike the
session channel, which subscribes at construction. Subscribing does no GameKit work and
registers no listener, so a player who never enters online play still never sees Game Center;
until something listens, the platform holds its events in the buffer above. The turn stream
replays nothing to a new subscriber — a turn event is an occurrence, not a value with a
current state — so what a late subscriber missed is the platform buffer's to deliver. One
receiver subscribes for the app's lifetime, constructed at app start by the root widget; it
is the only subscriber that writes to the store, and a second live one would double-apply
every arriving turn.

**Decoding what arrives is strict, per key, and all-or-nothing.** Nothing is coerced, no
missing key is defaulted, and no value is half-filled: a reply that is not a map, an
unrecognised `state` or `status`, a wrong-typed field, a participant list that is not exactly
two entries with exactly one local player, or an index that does not index that list — each
makes the whole call answer its own failure value. One bad match fails a whole `loadMatches`
reply rather than yielding a list with a hole in it. A malformed event on the session channel
is ignored and the last known session stands, as it does on an error or a close. A turn event
is decoded the same way and dropped whole on any failure, with one exception: a `match` map
that fails to decode is carried through as absent rather than dropping the event, since the
event routes by match id and applying a turn reads no field of that map. Dropping it would
lose a legal move to a field the move never reads; the only thing an absent match map costs
is the rename.

**`flutter test` reaches the Dart half only.** The channel is exercised against a mock handler
and every other layer tests against the fake bridge; the Swift half carries no test target and
is checked by running the app on a device signed into Game Center.

### Signing in, and the session anything can read

**Registering the channel does no GameKit work, and neither does subscribing.** The sign-in
handler is installed on the first `authenticate` call and never on a listen, so something
subscribing at launch presents no sign-in view controller and shows no banner. Before that
first call the session channel reports unauthenticated on subscribe and nothing else; after
it, a change GameKit originates with no call behind it — the player signing out in iOS
Settings — arrives through that same handler. A later call re-installs the handler **only
while the player is not authenticated**, which is what makes a declined sign-in retryable;
re-installing it over a signed-in player would re-present Apple's sheet for nothing. Once the
player is signed in, the call answers from the cached local player and presents nothing.

**`authenticate` is safe to call any number of times.** A second call while one is in flight
joins the first rather than starting a second sign-in, so at most one sheet is ever on screen.
Events on the session channel are not published while a call is in flight — the reply is what
publishes the outcome, and without that the channel's on-subscribe replay would overwrite the
in-flight state the moment the first call was made.

**The session is one plain value anything can read**, through a provider holding it directly
rather than an async wrapper, since the in-flight state is already one of the four values it
can hold: unauthenticated, optionally with a reason; authenticating; authenticated, with the
nickname and whether the account is a child's; and restricted, with whether the account is a
child's. **Restricted is a state of its own and not a flag on authenticated**, so a caller
deciding whether to offer online play branches on the state rather than on a boolean it can
forget to read — the same shape the engine's placement state uses. The stream is broadcast and
replays the current value to each new subscriber, and one subscriber cancelling tears nothing
down for the others.

**A fake bridge ships as app code rather than test code**, behind the same interface, because
it is the double every other layer tests against. It matches the real bridge on the stream's
replay behaviour and on every refusal, and holds no shortcut the real one could not honour.

### Presenting Apple's matchmaker

**The match request is minimum two players, maximum two, and sets no matchmaking mode at
all** — that is where "never forces automatch-only" is honoured concretely.

**A found match does not arrive through the matchmaker's delegate.** Its found callback has
been deprecated since iOS 9 and is not delivered at all on this app's iOS floor, so a bridge
waiting on it waits forever. The match arrives instead on the local player listener's turn
event, which is why that listener is registered on the first successful sign-in — and not
before, since a player who never enters online play must never see Game Center at all. The
delegate still supplies the other two outcomes. Found, cancelled and failed stay three
distinct values rather than one failure carrying a message, because a caller that cannot tell
a cancel from an error cannot behave differently on them.

**One sheet at a time, and the guard that makes it testable is on the Dart side**: a second
presentation while one is in flight fails without reaching the platform. The Swift side
refuses a second sheet as a backstop and clears its own guard only once the dismissal has
completed, so the next presentation cannot race the dismissal animation.

**Everything is presented on the topmost presented controller of the foreground-active scene's
key window, never the window's root** — the root is Flutter's own view controller, and
presenting on it while a Flutter surface is already up throws. When nothing can present, the
call answers rather than waiting: `authenticate` comes back unauthenticated with a reason,
`presentMatchmaker` comes back failed. A call that cannot present is never left pending. Every
reply and every event is delivered on the main thread, since GameKit's completion handlers
promise nothing about which thread they call on.

**Neither the matchmaker nor a match load signs the player in on the caller's behalf.** Called
while the session is not authenticated, the matchmaker answers "unavailable" carrying the
current session and the match load answers failed, and neither sends a platform call.

**Entering online play signs in first and then calls the parental gate with the session that
produced.** The gate decides from the session it is handed and never authenticates, so what
it guards is the second half of entering — presenting the matchmaker, or accepting the
invitation — and never the sign-in itself. What it does with each session state is **Kids
Category** below.

**Asking Apple which matches it holds reads only.** It creates, stores, reconciles and deletes
nothing, and imposes no order of its own on what GameKit answers — nothing may depend on the
order matches come back in. A match whose local participant GameKit cannot identify is left
out of the answer and the rest still come back, the same doctrine the store applies to a
record it cannot read; nothing is defaulted, because a defaulted index would name the opponent
and make this device look like the starter. That same match arriving as a *found* result fails
instead, there being nothing left for the caller to act on.

### A found match becomes a stored game

**The handoff takes a found match and the store, and answers one of four values**: the stored
record, awaiting-the-first-turn, refused at the cap — carrying the ceiling and the current
count, so a caller can say "3 of 3" without a second round trip — or refused for an empty
title. It never throws, and it writes at most once: only the starter path writes at all.

**A match whose id the store already holds answers that existing record** — nothing created,
nothing re-titled, no series id minted. **This device is the starter exactly when the match
carries no data yet and the local participant is the current participant.** Everything else is
awaiting the first turn and stores nothing, which is the accepting device's ordinary state
until the starter's first payload lands.

**The starter's create hands the store a freshly minted series id, a new series board, the
match id, Player One as this device's side, and the other participant's nickname as the
title.** When that nickname is blank — or the participant does not exist yet, which is the
ordinary Play Now case — the title falls back to the same **ItSaMeMaRiO** a game on this phone
defaults to, as a placeholder; the store applies no fallback of its own and would refuse an
empty title. The placeholder is replaced once, when the opponent resolves — see **Persistence
and Serialization** → *What an online game adds to the record*.

**The series id is 32 lowercase hex characters minted from 128 bits of a secure random
source**, on the starting device, on that one call. It has to be unique across devices rather
than merely within this process, since the accepting device copies it out of the first payload
and both then hold it — the store's own record-id minter does not satisfy that and is not
reused here.

## Kids Category

**The app will be listed in Apple's Kids Category.** This is not only a listing choice — it
changes what gets built in features that ship long before release work:

- A **parental gate** is required before any purchase flow, before any link that leaves the
  app, and — for a child's account — before entering online play.
- Third-party analytics and behavioural advertising are restricted.
- A privacy policy is mandatory.

These reach the purchase flow and theme-selection features directly, and the gate has to
exist before those are built rather than being added at submission.

A separate, consequent fact: the age rating is **4+.**

**The parental gate guards purchases and online play.** Every purchase raises it. Entering
online play raises it **only when Apple reports the signed-in account is a child's** —
`GKLocalPlayer.isUnderage` — so an adult account is never gated on the way into a match. That
flag rides on the session state the bridge publishes, for a restricted account as well as an
authenticated one, so whatever raises the gate reads it from app state rather than asking
GameKit again.
Entering means the deliberate step: tapping **Play online** to find or invite an opponent,
or accepting an invitation. Opening an online game that already exists — from the
open-games list or from a "your turn" notification — is playing, not entering, and raises
nothing. The game has no outbound links today — no in-app support URL, no social links, no
advertising — so purchases and online play are the only triggers that currently exist. If
an outbound link is ever added, it needs the gate too — that is a thing to remember rather
than a thing already handled. What the gate asks, and how long a pass lasts, is **In-App
Purchases and Entitlements** above. What online play is, is **Online Play** above.

**The gate exists as one service with two guards** — one for a purchase, one for entry into
online play — and the online guard is handed a session that has already been resolved. It
authenticates nothing itself and sends no platform call. A restricted account is refused
without asking: Apple has said multiplayer is not allowed for it, so there is nothing to
enter, and `isUnderage` is never read on that path because the refusal comes first. A session
that is unauthenticated or still in flight is not gated either — the guard answers that there
is nothing to decide from and runs nothing, because the entry point signs in before it calls
and the matchmaker refuses an unsigned player anyway. An adult account runs straight through
with nothing on screen, and a child's account is asked.

## Crash Reporting

**Catch errors and construct the crash-report object from the start. Do not transmit it.**
As stated:

> *"I have nowhere to send the data. I think it would be good to set the game up to handle
> this putting in the catches now from the start to build out the crash report. We just
> won't send it out just yet. We will come up with where it will be sent to later. But for
> now just catch and build out the object. Just don't send it. yet"*

So the error handling and the report object are day-one work; the transport is not. The
destination is deliberately left for later rather than being an open question — today's
answer is "nowhere."

This keeps **Fully offline, except for Apple's own services.** under **What the Design
Docs Already Imply** above true for now. StoreKit and Game Center being permitted does not
make a report destination permitted — those are separate exceptions, and this one stops
being true the day a destination is chosen.

**No off-the-shelf crash SDK is used.** Crashlytics, Sentry and the rest all assume a
destination and a network, and there is neither — so none is added, and no HTTP or socket
client comes in with one. The Kids category restricts third-party analytics on top of
that.

### What gets caught
**Unhandled errors only, and exactly one report per error.** An error that application
code catches and recovers from — a theme file that fails to parse being the decided case,
see [Theming](./Theming.md) → Choosing a Theme — produces no report, and there is no
application-facing "report this" entry point.

Catching is in place before the first frame, so an error thrown during startup — while
preferences load, while themes materialize — is caught rather than lost.

**Errors inside a spawned isolate reach no handler and are not reported.** Nothing in the
app spawns one today; whoever adds the first one owns the gap.

### What a crash report captures
**The error, the stack trace, and a timestamp. Nothing else.** No game state, no screen,
and specifically no opponent name — no text a player has typed.

This is about more than debugging convenience: the app is in the **Kids category**, and in
a 4+ app *transmitting* personal data is itself the regulated act, not merely something a
privacy label declares. Capturing nothing personal means that if a destination is ever
added later, no consent flow is required — the decision keeps a future option open rather
than only satisfying today's rules.

Named cost: reproducing a bug that depends on board position or which screen the player was
on becomes harder, because the report will not say.

### The one error that carries game state renders none of it
**`IllegalMoveError.toString()` renders the reason and the offending move, and never the
board.** A report holds the thrown error object itself, so every way a report is ever
rendered as text goes through that object's `toString()`. The engine's `IllegalMoveError`
carries the `Move` and the `Board` it was applied to, and it is the one object reachable
from a report that holds a whole board position. The error **keeps** its `Board` — that
is the debugging value the payload was written for, and it stays readable from a debugger
attached in process — and nothing renders it into text.

The residual is a contract on a *string*, not an invariant on the object: the `Board` is
still on the error, so any route that renders or copies a report other than `toString()`
re-leaks the position — a `toJson` on either type, a persisted report, a reflective or
generated serializer walking the error, or a debugger dump written to a file. Whoever adds
persistence or a destination owns closing that.

### A caught error is silent to the player and logged for the developer
As stated:

> *"What i want for now is a signlent fail to the user but the error gets logged in the
> concel in the background. This should allow the dev to see it. Note i want this
> sentralized so that  the location of the log can be redirected in the future. so all
> logs such as this can be sent or reported on. that not yet. for now just concel log them
> using a centralized method we can update and controle the where in teh future."*

**The player sees nothing.** No dialog, banner, snackbar, toast, sound, haptic, navigation
or theme change results from a caught error, and the framework's default presentation is
preserved exactly — a build-phase failure renders whatever Flutter renders by default.

**The report is logged to the console, and every log goes through one centralized
method.** That is what lets a developer see the failure while working. No call site writes
to the console itself, because the point of the choke point is that the destination can be
redirected later — to wherever reports are eventually sent — without touching a single
caller.

The console is a developer-facing log, not a transmission. It does not make a report
destination chosen, and **Fully offline, except for Apple's own services.** stays true.
What reaches the console is the report rendered as text, so the contract above governs what
it can say.

### Reports are held in memory
**A report is kept in memory and goes no further.** It is written to no file and to
neither store, so reports are gone when the app closes — including the crash that produced
them. Retention is bounded rather than unlimited, because an error thrown from a build
method re-fires every frame and would otherwise grow the list without end.

## Testing

### Unit tests for the rules engine
The rules engine gets unit tests — **this is where the real complexity is.**

### Widget tests for the board — no golden tests
**Widget tests, no goldens.** Test that taps do the right thing and that the highlight
states appear. Skip golden image tests.

### A test that fails on hardcoded theme values
**The suite carries a test that fails on hardcoded theme values, covering the slot
inventory the Architectural Rule names.** An ordinary test in the suite, not a custom
analyzer plugin — and not an `analyzer`/AST-based scanner either. It scans the source
under `lib/` for banned patterns outside the theme layer itself, and it holds a per-file
baseline that fails when a new violation appears. Nothing under `lib/` violates it, so
**the baseline is empty and stays empty**. It runs in the default `flutter test` run, with
no extra flag, tag or separate command.

<!-- "The theme layer" is concretely `lib/theme/`. See Project Structure. -->

**Two exclusions, both by path.** `lib/theme/` is exempt — it holds the merged theme
object and the loader, so it is the one place a literal theme value legitimately appears.
Generated files are exempt too, `*.g.dart` and `*.freezed.dart` anywhere under `lib/`: a
developer cannot fix a violation in a file `build_runner` rewrites. Nothing generates into
`lib/` today — the engine's models are hand-written — so the exemption is a standing rule
rather than one anything currently relies on. Everything else under `lib/` is scanned.

The scope comes from [Theming](./Theming.md) → Architectural Rule, which derives its slot
list from what the screens actually consume rather than a closed category list. The
categories below are what the guard claims; the patterns inside them are a floor to widen,
never a ceiling, and still not a complete enumeration of that slot inventory:

| Category | Roughly what the scan looks for |
|---|---|
| **Colors** | Raw `Color(0x…)` literals and references to Flutter's `Colors.*` palette |
| **Animations** | `Duration(…)` timing built from a numeric literal |
| **Fonts** | Literal `fontFamily:` values |
| **Type scale** | Literal `fontSize:` values, `FontWeight.*` outside the theme layer |
| **Radii** | `BorderRadius`/`Radius` corner radii built from a numeric literal |
| **Opacities** | `withOpacity(…)`/`withValues(alpha: …)` given a numeric literal |
| **Piece styles** | Hardcoded `'X'`/`'O'`/`✕`/`○`/`Ø` mark glyphs, in board code |
| **Chrome icons** | `Icons.*` and any icon package's constants, outside the theme layer |
| **Sounds and backgrounds** | `AssetSource('audio/…')`, and literal `assets/…` image paths |

Durations are in scope because [Animations](./Animations.md) → How Animations Play puts
timing inside the theme's animation definitions, so a hardcoded `Duration` is a theme
value that escaped.

`GoogleFonts.*` is not scanned for, because Inter is bundled rather than fetched and it
will never appear. Sounds need their own pattern because `audioplayers` supplies the
`assets/` prefix itself, so a literal `assets/` path never appears for a sound; literal
`assets/…` paths still catch images and backgrounds, which have no prefix-supplying API
hiding them. Marks are scoped to board code, because a bare `'X'` in a menu is far more
likely to be ordinary text than an escaped theme value, while a chrome icon is a
violation anywhere outside the theme layer.

**A pattern matches a value typed in and lets an expression through.**
`Duration(milliseconds: 220)` is a theme value that escaped;
`Duration(milliseconds: theme.animation.placeMark.durationMs)` is the behaviour the guard
exists to encourage and passes. That is the general form of the escape a caller is meant
to use — read the value from the theme and pass it — and any rule added later follows it.
The two that cannot, because an icon constant and a `FontWeight` are not labelled numbers,
are permitted inside `lib/theme/` instead: resolving a theme's icon slot to a concrete
`IconData`, and a stored integer weight to a `FontWeight`, both happen there, which is
what makes those two rules satisfiable at all. Each pattern ships with a case asserting
the compliant, theme-derived form produces no violation, so tightening one back fails here
rather than in the feature that trips over it.

**A green guard is not a covered inventory.** It catches a value typed into code as a
literal. It cannot see a value that arrives through a variable or arithmetic, a path
assembled rather than written, a theme-supplied glyph name hardcoded as a string, or a
widget that reads the right slot and then ignores half of it. Completing the guard does
not satisfy [Theming](./Theming.md) → Architectural Rule in full, and the suite being
green must not be read as the inventory being covered.

**The remaining bare-numeric slots are deferred until there is UI code to calibrate
against.** A theme value that reaches code as an unlabelled number — grid-line width,
grid-line inset, and the size fields on marks and icons — has no distinctive constructor
to match on the way `Color(0x…)` has. Grid-line width is a known, accepted false negative,
and the rest get calibrated when the first painter writes a bare numeric into real UI
code, not guessed at before it exists.

**No rule may target `padding:`, `width:`, `height:` or `SizedBox`.** Spacing and layout
numbers are code constants ([Theming](./Theming.md) → What a Theme Does NOT Control), so a
rule there would fail sanctioned code with no legal fix. That is a boundary, not a gap.

**The baseline records what was found, not where.** An entry is keyed on the file, the
rule and the matched text, with an occurrence count; line numbers are reported in the
failure but never stored. Keying on a per-file count would let one violation be swapped
for another with the total unchanged, and keying on line numbers would fail on any edit
that shifts lines — a guard that cries wolf gets deleted.

**Fixing a violation never breaks the build.** A file with fewer violations than its
baseline passes, and stale entries — a fixed violation, a deleted file, a rule that no
longer exists — are printed as a note to prune rather than failed. Failing on improvement
would make deleting a hardcoded value the thing that breaks the build.

**A hardcoded theme value is fixed, never recorded.** The baseline exists to catch a
regression, not to house an exception: it starts at zero and stays there while the code is
clean, and a violation found on the day this lands gets fixed rather than written into it.
There is no `// ignore:` convention, no allow-list annotation, no per-line suppression,
and no baseline entry standing in for one — a suppression convention has to be honored
forever, and there is no sanctioned home for a deliberately hardcoded theme value. A diff
that adds baseline entries is a diff that adds hardcoded theme values, and reads that way
in review.

**The failure is loud and it explains itself.** It names every new violation — file, line,
rule and the matched text — and says why that value may not be hardcoded, so someone
hitting it for the first time can fix it without going to find the rule. A guard that
fails with "1 new violation" and no location is a guard someone deletes rather than
debugs. Two things fail loudly rather than degrading quietly: a missing or malformed
baseline file, which is never silently treated as empty, and a file under `lib/` that
cannot be read or decoded, which is never skipped. A skipped file is an unscanned file,
which is the false assurance this whole test exists to prevent.

This is the structural enforcement that **The theme system is the main architectural
risk** above asks for, and it is what makes [Theming](./Theming.md) → Architectural Rule a
checkable rule rather than a matter of discipline.

### Every asset path a theme names must resolve

**A path named in a theme file with no file behind it fails the suite.** At runtime a
missing image behaves exactly like an absent slot — no crash, no blank, the fallback draws
(see [Theming](./Theming.md) → How a Theme's Art Is Drawn), which is the right thing for a
player and the wrong thing for a build: it means nothing anywhere failed loudly when a
theme's art silently never shipped. A theme's art and its music track sat unbundled through
an entire build cycle with every test green before this check existed.

**The check walks the merged theme document rather than a list of slots.** It iterates
whatever keys the merge actually produced under a theme's art, mark, icon and sound
sections, so a slot added to Neon later is covered the moment it exists, with no edit to
the test. A hand-written slot list goes stale exactly when the schema grows, which is the
one moment it matters most — and that is not hypothetical: a hand-listed version of this
check missed the text-patch slot on the day it was added.

**No test reads a generated file's bytes, dimensions or duration.** Tests assert the
wiring — that a slot parses, merges, falls back and reaches the widget that draws it — from
their own tiny fixtures. The shipped art is drafts, regenerated on the user's word, and a
test reading it would break on a change that is purely cosmetic and correct.

## Distribution and Release

### App name
**"Tic Tac Toe Extreme."** 20 characters, inside Apple's 30-character App Store limit. The
approved handoff draws it as a kicker/wordmark split (`TIC TAC TOE` over `EXTREME`) on
screen `1a`.

### Bundle identifier
**`com.ehrendavis.tictactoeextreme`.** Lowercase reverse-DNS, the conventional Apple form.

**Watch out for:** a bundle identifier is effectively permanent once the app has been
submitted to App Store Connect, so this is not a name to revisit casually.

### Distribution — public App Store release
**The App Store.** A public release, not a personal or TestFlight-only build.

That makes the App Store Connect listing a real deliverable — description, keywords,
screenshots, categories — which is what **Release tooling — fastlane** below manages.

### The app icon
**The app ships an icon, and it is not the main-menu logo.** App Store submission cannot
happen without a 1024×1024 icon. It lives in the iOS asset catalog rather than the
Flutter `assets/` tree, and it is a separate asset from the logo. It is generated through
the Asset-Gen-Framework like the game's other art, from its own prompt-manifest entry, and
it stays a deliberately simpler asset than the main-menu logo — the logo's detail does not
survive the small sizes an icon is rendered at. The generated draft is transparent PNG and
is flattened onto the theme's ground colour on the way into the catalog, because an iOS app
icon must carry no alpha channel or App Store Connect rejects the build.

### CI — local builds only
**No CI. Local builds only.** `flutter test` and `flutter analyze` run locally.

Consequence worth noting: the test decisions above — the rules-engine unit tests, the
board widget tests, and the hardcoded-theme-value test — run when they are run locally.
Nothing runs them on a push.

### Release tooling — fastlane
**fastlane.** The App Store listing is kept as local text files, edited and committed
like code, and pushed to App Store Connect from the CLI.

The three pieces:

- **`deliver`** (aka `upload_to_app_store`) keeps the listing as local files:
  `fastlane/metadata/` for description, keywords, release notes and categories — one
  file per field per locale for the localized fields (description, keywords, release
  notes, name, subtitle), and one file per field at the top level for the
  non-localized fields (primary and secondary category, copyright) — and
  `fastlane/screenshots/` for the images. Edit locally, commit, run, and it pushes to
  App Store Connect.
- **`match`** stores signing certificates and provisioning profiles in a git repo and
  syncs them.
- **`produce`** creates the app record and registers the bundle identifier and the app
  name from the CLI — the record is never hand-created in the App Store Connect web UI.
  It runs once, when the record is created, not on every release.

It runs on Apple's official App Store Connect API underneath, authenticated by an App
Store Connect API key rather than an Apple ID session.

**Set up when actually approaching shipping — not now.**

**Watch out for:** fastlane does not automate App Review, which stays manual — and an
Apple Developer Program membership is required before any of it works. That membership
is not the same thing as the Paid Applications Agreement below: it lets you ship an app,
not sell anything.

### The release run
**One command runs the release, and it starts by running the local checks.** `flutter
analyze` and `flutter test` run first, and the release aborts if either fails — nothing
is built and nothing is uploaded from a tree that does not pass. With **CI — local
builds only** above, that is the only automated gate that exists: whatever the release
procedure checks is the only thing anything checks.

From there the run syncs the signing material, increments the build number, builds the
app, and uploads the build and the listing to App Store Connect. **The first release is
version `1.0.0`.** The build number is incremented by the run rather than by hand and
never repeats; an upload is refused without a unique one, so the alternative is not
"undecided" but "decided at the keyboard on upload night." The marketing version
thereafter is a hand edit to `pubspec.yaml`.

**A listing change can be pushed on its own, without producing a build.** That is what
makes keeping the listing as text worth doing — a wording fix is a commit and a push,
not a release.

Submitting to App Review is still a human step, and so is waiting on the review itself.

### Credentials never live in the repository
**"Kept in the repo" covers the listing text and the screenshots, and nothing else.**
The App Store Connect API key, the signing passphrase, and the address of the
certificate repository are all read from the environment. The key file lives outside the
repository and is never committed in any form, and **the certificate repository is
private.**

This is a rule rather than a preference because a private key committed to a repository
is an unrecoverable leak: it cannot be un-published, only revoked.

### The listing ships in one locale
**`en-US`, and it is the only one.** Nothing is localized for the first release, and
adding a locale later is additive — a new set of field files beside the existing ones.
The listing also carries a copyright line naming the year of first release and a holder;
who the holder is has not been decided — see Open Questions.

**Screenshots are release work.** Building the screens does not produce them; turning a
finished screen into a store image at Apple's required sizes is its own job, and the
images are committed alongside the listing text. **The submitted build is universal —
iPhone and iPad** — because the scaffold leaves the iOS device family at its default, so
the sizes required are Apple's current iPhone and iPad reference sizes. Narrowing to
iPhone-only is cheaper before first submission than after; see Open Questions.

### The store-side products
**The record declares in-app purchases, and the products configured on it are exactly
the products the app queries — no others.** A store entry the app never queries is a
product nobody can buy and a review surface nobody maintains.

**The first public release carries two purchasable products:** the **$4.99 unlock that
raises the open-game cap from 3 to 100**, sold from the Settings screen's purchases
section, and **one purchasable theme**. The theme product belongs to first release, not
to the MVP that comes before it.

**A purchasable theme needs a theme to sell.** Sewing is now specified and ships free in
the submitted build, so what blocks this product is the purchase flow, not the absence of
a theme. Whether paid themes are ultimately one product, one per theme, or a bundle is
still open: one purchasable theme at first release settles the launch shape, not the
model. See Open Questions.

**Products are created as non-consumables**, which is what the entitlement model already
assumes: restore is largely automatic, and a refunded purchase simply stops appearing in
the player's entitlements. Neither is true of a consumable. **App Store Connect fixes
the product type at creation and it cannot be changed afterwards** — a consumable
created by mistake has to be abandoned and replaced under a new identifier, which is
permanent too.

**Products are configured separately from the app record and are their own review
surface.** Each carries its own metadata and review state and can be rejected
independently of the app, and no part of the release run touches them.

### The Paid Applications Agreement does not wait
**Everything else here waits for shipping to actually approach. This does not.** The
Paid Applications Agreement, and the banking and tax details that go with it, is a
human, multi-day process with no automation path, and it gates the products existing at
all — nothing can be sold, including any in-app purchase, until it is executed. Starting
it late delays a ship date by weeks.

**Nothing in the tooling detects that it is missing.** App Store Connect simply will not
let the products exist.

### Export compliance is pre-answered
**`ITSAppUsesNonExemptEncryption` is set to `false`, in the iOS project's
`Info.plist`.** The app implements and calls no cryptography of its own, and the HTTPS
StoreKit performs on its behalf is exempt. Without the key, the compliance question is
answered by hand on every upload — a step to forget rather than a decision to make. If
the app ever ships its own cryptography, the answer changes and so does the filing.

### What the record declares about data collection
**Nothing of the player's is transmitted to anyone but Apple, so the privacy nutrition
label's answer for the build being submitted is "no data collected."** The app operates no
server of its own: entitlements live with Apple and are verified on device, an online
game's board and the player's identity live in an Apple Game Center match, crash reports
are built and never sent, and there is no analytics or advertising SDK to declare — see
**Crash Reporting**, **In-App Purchases and Entitlements** and **Online Play** above. Game
Center is Apple, not a third party, which is what keeps the answer "no data collected".

**It is not settled beyond that build.** Whatever a crash report ends up carrying is
what a future destination would send, and that is what the label would then have to
declare — so this is re-checked the day a destination is chosen. The label and the
age-rating questionnaire are filled in by a human either way.

### The manual steps, and the checklist that holds them
**Every step of submission that leaves no artifact is written down rather than
remembered** — on a checklist kept in the repo beside the release tooling, with a place
to record who did each one and when. The first evidence of a missed step is otherwise a
rejected submission. The steps are the Paid Applications Agreement, the Developer
Program membership, submitting the app and each product to review, the App Review
contact details, the content-rights answer, the price and territory entries, the privacy
policy URL, and the sandbox pass below.

**The purchase flow is exercised against a real App Store sandbox account before
submission.** Every automated test of buying and restoring runs against a double, and
nothing automated ever touches the real store — so this manual pass is the only time the
real thing is exercised at all. The path is the one a player takes: Settings → purchases
section → parental gate → buy.

## Open Questions

These are the things I think we need to hammer out. Grouped roughly by how much they
block other work.

### 1. Persisted data — migration
- When the shape of stored data changes — a fifth preference is added, a key is renamed,
  an open game gains a field — what happens to data already on the device? A game
  written by v1.0 has to still load in v1.1.

### 2. Theme loading
- Are the theme YAML files declared as assets in `pubspec.yaml`?
- What happens to an unknown or misspelled *key* inside an otherwise-valid theme file?
  Merge-over-Neon will quietly fill the gap with Neon's value, so a typo in a theme file
  fails silently. The hardcoded-theme-value test guards code that bypasses the theme; it
  does not guard a theme file that misspells a key.

### 3. Build and distribution
- Who produces the app icon, and is it generated or hand-made? See Distribution and
  Release → The app icon.
- A set of hard App Store submission blockers, none of which any doc currently mentions,
  and all of which must be decided before shipping:
  - **Paid Applications Agreement**, plus banking and tax details — required before
    anything, including any in-app purchase, can be sold. A human, multi-day process
    with no automation path.
  - **A privacy policy URL and a support URL** — both required listing fields. The
    project has no website of any kind.
  - **The privacy nutrition label and the age rating questionnaire.**
  - **The secondary App Store category, the price tier, and territory availability.**
    The primary category is settled by the Kids-category listing.
  - **Content rights** — the submission asks whether the app contains third-party
    content, and the answer depends on the licensing of Replicate-generated assets and
    of the bundled Inter and Phosphor dependencies, none of which is established.
  - **Screenshots** at Apple's required device sizes — by what means they are captured
    is open: by hand on a simulator, or with fastlane's `snapshot`, which would be a
    fourth fastlane component beyond the three under Distribution and Release →
    Release tooling — fastlane.
  - **App Review contact information**, and **sandbox testing of the purchase flow**
    before submission.
  - **The product identifiers.** No doc names one for either of the two products and
    none has been minted. An identifier is permanent and cannot be reused, and the
    product type is fixed at creation as well, so a mistake has to be abandoned rather
    than corrected.
  - **Which theme is the purchasable one**, and whether paid themes are ultimately one
    product, one per theme, or a bundle. One purchasable theme at first release settles
    the launch shape, not the model.
  - **Which git repository holds the signing certificates.** It has to be private;
    where it lives is open.
  - **Whether the submitted build stays universal.** Narrowing to iPhone-only is
    cheaper before first submission than after.
  - **Who the copyright line names.** The listing requires one — the year of first
    release and a holder — and nothing states the holder.
- **Nobody owns debug symbols (dSYMs) or symbolication.** Without symbols, a stack trace
  from a release build is raw addresses rather than function names. Uploading symbols
  would be release tooling's job if a crash-report destination were ever chosen, but no
  destination is chosen and choosing one is a separate decision — see Crash Reporting.

### 4. Kids category — age rating questionnaire
- The Kids-category listing choice and the resulting parental-gate, analytics, and
  privacy-policy requirements are settled — see Kids Category, and the age rating (4+).
  What remains open is the exact age-rating questionnaire answers.

### 5. Which store holds entitlement state?
- The local copy of the player's entitlements is an offline convenience rather than the
  record (see In-App Purchases and Entitlements), but nothing says where it is written.
  **`shared_preferences`**, alongside the five preferences — small, flat, already the home
  of app-level player state; but it costs the mechanical check that the preference store
  holds exactly the five preference keys and nothing else, turning that scan into a
  judgement call. Or **Hive** — already structured, and a set of product identifiers is a
  growing collection rather than a single flag, though it means a second box beside the
  open-games one. "Nothing persisted, re-queried at launch" is ruled out: the
  last-known-plus-refresh provider needs a local copy to fall back to.

### 6. Crash reporting
- After an unhandled asynchronous error, should the app carry on, or hand the error to the
  platform's default handler instead?
- Should a build-phase failure that re-fires every frame ever escalate, rather than render
  the default error widget forever?
- Are errors the app catches and recovers from reported too? Today only unhandled ones
  are. The standing case on the other side is a theme file that fails to parse
  ([Theming](./Theming.md) → Choosing a Theme).
- Are reports held only in memory, or persisted? They are in memory today, which means
  they are gone when the app dies — including the crash that produced them. If they
  should survive: which store, `shared_preferences` or Hive, and does the stored shape
  inherit **1. Persisted data — migration** above? Whatever answers this has to say which
  rendering of the error reaches the store, because the board position is still on the
  error object even though nothing prints it.

### 7. Timing and opacity that aren't theme values
- A `Duration` or an opacity built from a numeric literal is a violation wherever it
  appears under `lib/`, including timing and opacity that are not theme values at all — a
  debounce interval, a storage timeout, a debug overlay. The escape is the same either
  way: name the value and pass it as an expression. Is that an acceptable tax on non-theme
  code, or should timing and opacity that aren't theme values be exempt?

### 8. Generated assets
- **What is the logo, actually?** Nothing states its subject. The approved handoff draws a
  placeholder of 81 dots — the game itself — and says *"Replace with real art"*, which
  reads either as the brief for the real logo or as a description of the thing being
  replaced.
- **Are generated asset files committed to the repo?** [Theming](./Theming.md) → Where
  Themes Live says themes are bundled and shipped with the app, which implies the assets
  they name ship too, but nothing says whether the binaries live in git.

### 9. The rules engine
- If a win completes two lines at once, does the game name one of them, or both? The
  engine returns one so the value is deterministic, but that fixes what the engine
  publishes, not what a player should be shown — and "both" is not expressible in what it
  returns today. Widening that later is a change at every consumer; widening which one it
  picks is not.
- What comes back from reading a cell or a quadrant with an index outside 0–8? An
  out-of-range index on the write path is an illegal move; the read path has no stated
  answer, so today it is whatever the underlying collection happens to do.
- How may a test build a mid-game board? The only way in through the public surface is a
  fresh series plus a replay of legal moves, which is faithful but long. The tempting
  shortcut is building fixtures from stored JSON, and that binds the whole suite to a
  serialized shape **1. Persisted data — migration** above leaves open — where the
  breakage then looks like a rules failure rather than a fixture one.

### 10. The bundled icon set
- Which bundled icon set the app ships, and whether it arrives as a package dependency or
  as icon art bundled per theme. [Theming](./Theming.md) → What a Theme Controls sanctions
  either — "a theme may either name a glyph from a bundled icon set or ship its own image"
  — and the approved handoff names Phosphor without that being a decision, but no decision
  names a set. If it is a package it joins the declared dependencies; if it is per-theme
  image assets it lands under the asset-folder rule in **Project Structure** above.
- Downstream of that: does the `cupertino_icons` dependency the Flutter scaffold generates
  stay? Nothing reads it, and the hardcoded-theme-value guard bans its constants outside
  the theme layer — but it is one small first-party package, and it is already there if
  the icon set ever lands on Cupertino glyphs.

### 11. In-app purchases and entitlements
- Does the first frame wait on the entitlements read? Waiting costs every launch one small
  disk read before anything is drawn, and a paying player never sees a flash of
  locked-everything. Not waiting paints immediately and lets a paying player see their own
  content locked, briefly, on every launch until the read lands.
- What is the player shown for each of the four purchase endings? Pending is the one that
  needs real copy — the player is being told to wait for someone else, and under the Kids
  Category that is the common case rather than the rare one.
- Can a paid theme ever be a product whose theme file is not on the device? If every paid
  theme ships in the build and a purchase merely unlocks it, the model only ever gates
  content the device already has. If a paid theme can arrive any other way, it has to handle
  an entitlement held for something not installed. [Theming](./Theming.md) → Where Themes
  Live says themes live in the codebase "for now", which is prose with a "for now" in it
  rather than a decision.
- Does the third theme land in time for the first public release, or after it? Distribution
  and Release states that the first release carries a theme product, and a theme product
  cannot be configured before the theme it sells exists. The theme itself is deferred as not
  needed right now. Whether those are the same point in time is not stated.

### 12. Online play — what the player is told
- Should a re-delivered identical board be visible to the player at all, or silently
  ignored? The data side is settled — nothing is written, and it is reported as its own
  outcome — but nothing says whether the player sees anything.
- What happens when a payload arrives carrying a version this build does not recognise,
  beyond the rejection itself — whether the player is told the other device is on a newer
  version, and whether that is distinguishable to them from a corrupt payload.
- What does the player see for a sign-in that fails or is declined, for a cancelled
  matchmaker, for a move Game Center would not take, and for a GameKit error the bridge
  reports? Each comes back as its own value; a send the board screen made is the one that
  now draws something — a message, a retry and a way out — and nothing renders the rest.
  The calm, kid-facing message a restricted account gets is decided in **Online Play**
  above, but its wording is not, and neither is the failed send's.
