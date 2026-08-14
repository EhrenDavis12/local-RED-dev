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
| **Fully offline, except for in-app purchases.** No backend, no network, no accounts — StoreKit is the one exception, needing network access and a restore-purchases path tied to the Apple ID. The exception is a StoreKit query against Apple, not a service we run — see In-App Purchases and Entitlements below. | Two players, one phone; qualified by In-App Purchases and Entitlements |
| **Local persistence** for 5 values: theme, music, sound, vibrate, animations | [Menus and UI](./Menus%20and%20UI.md) → Persistence |
| **Game-state persistence.** Every open game is saved and resumable, each with its own scoreboard. | [Menus and UI](./Menus%20and%20UI.md) → Persistence |
| **Audio playback** for one-shot sound effects (no music yet) | [Theming](./Theming.md) |
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
  theme/
    theme.dart     ← merged theme object
    loader.dart    ← YAML → theme
  state/           ← Riverpod providers
  navigation/      ← the app's routing layer
  audio/           ← sound playback, owned by P2-02-audio
  haptics/         ← haptic feedback, owned by P2-03-haptics
  entitlements/    ← StoreKit entitlement state, owned by P1-07-entitlements
  diagnostics/     ← crash catching/reporting, owned by P1-06-crash-reporting
  purchase/        ← store integration, owned by P4-05-purchase-flow
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
nothing in the app talks to a server. Online multiplayer is an intended future direction,
so tech choices must not foreclose syncing board state over a network — a backend layer
gets added if multiplayer arrives.

That rule is checked rather than trusted: a scan over `lib/` finds no HTTP client and no
network target other than the store SDK. It covers `lib/` only, so build-time tooling
outside that tree is out of its reach by construction. What is fixed is that property, not
a list of banned symbols — widening it when a new transport appears is ordinary
maintenance, narrowing it to let a real network call through is not. It must **not** be
written as "no networking API is reachable from `lib/`": in-app purchases are the one
sanctioned network path, so the stricter form fails the day the store layer lands.

`engine/`'s purity is held by a test that scans the layer's imports rather than by
discipline — see **The Rules Engine** below for what that check matches.

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
one-folder-per-layer convention, each owned by the PRD named in the tree above. File names
inside each are that PRD's to decide, not this doc's.

## The Rules Engine

**The rules engine is separate from Flutter.** Board state, legal moves, sending rule,
win/cat-game detection and free-choice state are **pure Dart with zero Flutter imports**,
and the UI layer reads from it.

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
when it ended.

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

Absence carries two meanings and is not a draw signal: a consumer reads the outcome first
and asks for the line only in the two winning cases. The three come back in ascending
order — a list needs some order, no doc gives one, and anything wanting the order a line
is drawn in sorts them itself. When one claim completes two lines at once, exactly one
comes back: the first in a fixed order — rows top to bottom, then columns left to right,
then the two diagonals — so the value is deterministic. Which line a *player* should be
shown in that case is an open question below.

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
- It adds a dependency, which `P1-01`'s exhaustive dependency list has to carry.
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

**Nothing unmounts when a surface opens over the board, so nothing clears a pending move
by accident** — which is why clearing it belongs to this layer. Every operation clears the
pending, unconfirmed selection before it navigates; clearing when there is none is a
no-op, and making it unconditional means no operation added later can forget to. It cannot
live in the board layer instead, because that layer would have to observe the router to
know a navigation happened, which is the one boundary this layer exists to hold. The rule
itself is [Game Board Design](./Game%20Board%20Design.md) → Changing your mind.

### Deep links are possible, not wired

The route structure is link-shaped, because that is part of what `go_router` was chosen
for. But nothing asks for an external entry point and the app is otherwise fully offline,
so no URL scheme, universal link or associated-domain configuration is specified. The
capability is retained; nothing is wired to it.

The route table and route paths are not designed here — that is a PRD's job.

## Rendering the Board

**The board is rendered with widgets.** *"ok widgets is the winner lets make that
happen."* 81 `GestureDetector`s in nested `GridView`/`Column`s, not a `CustomPainter`.

**Watch out for:** nested `Border.all` doubles interior grid lines — two adjacent 1px
borders read as 2px — and hairlines can look uneven at fractional device pixel ratios.
The known fix is a hybrid: widgets for cells and marks, plus one thin `CustomPaint`
overlay drawing only the grid lines. That is an escape hatch, not a decision taken.

### Marks — supplied by the theme
**Marks are asset slots on the theme, not shapes drawn in board code.** The theme supplies
the mark art; board code places it and draws nothing itself. Which kinds of art a theme
may supply — and why an image is the real answer for a theme — is
[Theming](./Theming.md) → What a Theme Controls.

## The Theme System

**Themes are data — a YAML object loaded at runtime**, not a Dart class compiled into the
app. A universal, theme-like object that can be loaded in.

**Each theme carries a UUID in its YAML file, and that UUID is the theme's identity.**
*"the themes should be saved by UUID in the YAML files."*

The persisted "selected theme" preference stores the UUID, not the theme's name. See
[Theming](./Theming.md) → Choosing a Theme.

**Merge over Neon.** Each theme is materialized into a complete theme by merging it over
Neon.

### Flutter's ThemeData vs our own theme object
**Use Flutter's `ThemeData`/`ThemeExtension` as far as possible**, filled out from our
theme YAML file. The remaining parts, not supported by the Flutter theme, we implement
ourselves.

Sounds and animations live in the **same theme object** — not a parallel structure. We
give Flutter's `ThemeData` what we can and handle the rest ourselves, all from the same
file.

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
**`freezed` + `json_serializable` for the domain models in `engine/`, and a `storage/`
layer holding the repository interfaces with Hive and `shared_preferences`
implementations that store JSON. No Hive `TypeAdapter`s.**

Two consequences worth naming, because they cut across other sections:

- **`hive_ce_flutter` is not pure Dart, so it must never be imported from `engine/`.**
  `storage/` owns it — and more strongly, **only `storage/` knows the store is Hive.** No
  file outside it imports either Hive package, and every caller depends on the repository
  interfaces rather than their implementations. That is also what lets tests run against
  in-memory fakes with no Hive initialized.
- **Serialization lives with the model.** `toJson`/`fromJson` are generated into `engine/`
  by json_serializable — pure Dart, Flutter-free — while the Hive box, adapters-free,
  lives in `storage/`. The storage layer writes no hand-rolled encoding of its own.

### Every persisted record carries a version stamp
**Every record written to either store carries a stamp identifying the app version that
wrote it, and it is there from the first release.** Preferences and open games both.

The stamp costs almost nothing while no device holds a save, and it cannot be recovered
afterward: without it, a record written by an older version is indistinguishable from one
written by the current version, and the app is left inferring a version from the shape of
the data. What the app *does* when it reads a record written by an older version is a
separate question, and an open one — see **Open Questions** below.

### What a stored open game holds
**A stored open game is the engine's whole game-plus-series state, plus three things that
are storage's own: the record id, the opponent name the game is titled with, and two
timestamps.** No design doc puts any of those three in game state, so they sit alongside
the board rather than inside it.

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
comparison, so the list would reorder itself after a flight or a DST change.

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

**Any save moves its record to the top, including a save that is not a move** — taking a
rematch puts that series first before a mark is placed in the new game.

### The cap is enforced on create, and the store never evicts
**Creating an open game is refused when it would exceed the current ceiling**, and that is
a create-time check rather than a standing invariant: it constrains what may be added and
nothing else. The ceiling is not a constant — see [Menus and UI](./Menus%20and%20UI.md) →
How many open games we keep — and the storage layer reads it from entitlement state rather
than defining either number itself.

**The store never evicts.** A create at the ceiling does not silently remove an existing
game; a slot is freed only by an explicit, player-initiated delete. If the ceiling ever
drops below the number already stored — an entitlement lapsing — nothing here licenses
deleting any of them.

**Reaching the cap is an ordinary, player-reachable condition, not an error**, so a refused
create reports it as a value carrying the effective ceiling and how many are held, rather
than throwing. That lets the caller say "3 of 3" without a second round trip.

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
asset, or waits for anything. Which file a moment resolves to is the active theme's
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

### The audio session is process-wide, and chosen rather than defaulted
**The session is configured once for the whole app**, and it has to be set explicitly: the
audio plugin's own default is not neutral, so leaving it alone ships a policy nobody
picked. Two player-visible behaviors ride on that one choice — whether the game sounds
over a silenced phone, and whether it interrupts whatever the player is already listening
to. They come as a pair and are still open; see [Theming](./Theming.md) → Open Questions.

Because the session is process-wide, a music layer added later shares it and cannot choose
differently. Whatever is settled there binds both.

### Where sound and art assets come from
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

**The script is Dart**, so generation needs no second toolchain — the SDK already ships
with Flutter.

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

This is what keeps **Fully offline, except for in-app purchases.** under **What the Design
Docs Already Imply** above true — the app makes no Replicate call, because generation
happened on a developer's machine long before the build. It also has to be true because
**CI — local builds only** below leaves nowhere to hold a build-time secret.

### What gets generated, and where it lands
**`assets/images/` and `assets/audio/` are where art and audio ship from, and the
generator writes to neither.** Everything it produces lands in a drafts area first — see
the next subsection — and reaches those folders only by being approved and moved.
`assets/themes/` holds theme YAML and is a destination at neither stage. The app icon sits
outside all of this: it lives in the iOS asset catalog rather than the Flutter `assets/`
tree (see **Distribution and Release** → **The app icon**), so if it is ever generated
here, this rule has to widen to reach it.

**The generator computes filenames; nobody types one.** A file is named from the theme and
the slot it fills, so there is one source of truth for the path a theme's YAML points at,
and the name an asset is drafted under is the name it ships under. Every generated file is
theme-prefixed, the logo included, which is what lets one theme override a slot without
colliding with another theme's file in a flat folder.

**What it owes is per theme, not per game** — each theme's playable sound slots and its
main-menu logo (see [Theming](./Theming.md) → What a Theme Controls). Mark art is produced
here too when a theme names it: that section calls an image *"the real answer for a
theme."* Both themes that exist today draw their marks as glyphs, so no mark image is
needed yet.

**Logos ship as PNG with alpha at 1x, 2x and 3x, all three downscaled from one render.**
Flutter treats the three as the same artwork at different densities, so generating each
independently would make the logo change appearance from device to device. A render that
is not square, or too small to downscale from, is rejected rather than cropped:
crop-center, crop-top, letterbox and squash all satisfy "make it square" and most of them
mangle a logo, so the fix belongs in what was asked for, not in the tool.

**A sound's format is declared per entry and checked against the bytes that arrive**, so a
file never contradicts its own extension. `.mp3` is what the audio layer is written
against, but most Replicate audio models emit wav or flac — which format ships is open
below.

**Music is not part of this.** A theme supplies its own music (see
[Theming](./Theming.md) → Music), and where that audio comes from — composed, licensed or
generated — is open there, not here.

### Nothing generated is applied directly — drafts, then approval
As stated:

> *"WE can generate the content fenced in however i never what the content to be directly
> applyed. we want each asset to be created into a assests_Draft folder of some type then
> approved and moved to the real folder to be implamented and tracked by themes. So fence
> it into a Draft folder first. Approval is my just saying yes use this assest X then move
> it along."*

So generation is two stages. **The generator writes into a drafts area kept separate from
the shipped asset folders, and that is the only place it writes.** What that area is
called is code's to settle — the decision here is the fence, not the path.

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

**The game now sells two things.** Themes beyond the two free ones (Neon and Classic Red
vs Blue), and a **$4.99 unlock that raises the open-game cap from 3 to 100.** See
[Theming](./Theming.md) → Free and Paid Themes, and [Menus and UI](./Menus%20and%20UI.md)
→ Play Game → Where It Takes You → How many open games we keep.

**Consequence for offline status:** in-app purchases require StoreKit, which needs network
access and a restore-purchases path tied to the Apple ID. StoreKit is the one exception to
**Fully offline** under **What the Design Docs Already Imply** above.

### Entitlements — Apple stores them, no backend needed
**No receipt-validation server, and no backend of ours.** StoreKit provides
`Transaction.currentEntitlements` — the set of currently-valid transactions for this app
under the signed-in Apple ID, cryptographically signed by Apple and verified on device.
That is the authoritative answer to "does this player own this." `Transaction.all` gives
full purchase history if it is ever needed.

Restore for non-consumables is largely automatic: signing in on a new device repopulates
entitlements without the player doing anything. The visible **Restore purchases** control
is still required by Apple's review guidelines, and `AppStore.sync()` is the explicit call
behind it — so the control is a compliance requirement more than a functional one.

On-device verification is sufficient for an app this size.

**Consequence for the architecture: Apple is the record of truth and it is queryable at
runtime.** Any locally stored entitlement state is an offline convenience, not the record.
A refunded or lapsed purchase simply stops appearing in `currentEntitlements` — that is what
answers "what happens when an entitlement goes away."

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
ones — see [Theming](./Theming.md) → Free and Paid Themes. No theme file, catalog entry or
ownership marker records it, so there is no second list of paid themes to keep in step with
the first.

**The purchasable theme is a third theme, and it does not exist yet.** Neither of the two
free themes becomes the paid one — the product is a theme beyond them, and building it is
deliberately deferred rather than pending. What that means for the store record is
**Distribution and Release** → *The store-side products*; when the theme lands is
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
while the word form defeats pre-readers and early readers alike. The problem is randomised
each time the gate is raised, and **three wrong attempts dismiss it** without ever reaching
the store.

**A pass is good for one purchase and nothing else.** There is no remembered pass — the next
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

Why the gate exists at all is **Kids Category** below.

## Kids Category

**The app will be listed in Apple's Kids Category.** This is not only a listing choice — it
changes what gets built in features that ship long before release work:

- A **parental gate** is required before any purchase flow and before any link that leaves
  the app.
- Third-party analytics and behavioural advertising are restricted.
- A privacy policy is mandatory.

These reach the purchase flow and theme-selection features directly, and the gate has to
exist before those are built rather than being added at submission.

A separate, consequent fact: the age rating is **4+.**

**The parental gate's scope is purchases only.** The game has no outbound links today — no
in-app support URL, no social links, no advertising — so purchases are the only trigger that
currently exists. If an outbound link is ever added, it needs the gate too — that is a thing
to remember rather than a thing already handled. What the gate asks, and how long a pass
lasts, is **In-App Purchases and Entitlements** above.

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

This keeps **Fully offline, except for in-app purchases.** under **What the Design Docs
Already Imply** above true for now. StoreKit being permitted does not make a report
destination permitted — those are two separate exceptions, and this one stops being true
the day a destination is chosen.

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
destination chosen, and **Fully offline, except for in-app purchases.** stays true. What
reaches the console is the report rendered as text, so the contract above governs what it
can say.

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
baseline that fails when a new violation appears. There is no application code yet, so
**the baseline starts at zero**. It runs in the default `flutter test` run, with no extra
flag, tag or separate command.

<!-- "The theme layer" is concretely `lib/theme/`. See Project Structure. -->

**Two exclusions, both by path.** `lib/theme/` is exempt — it holds the merged theme
object and the loader, so it is the one place a literal theme value legitimately appears.
Generated files are exempt too, `*.g.dart` and `*.freezed.dart` anywhere under `lib/`:
`freezed` and json_serializable generate into `engine/`, inside the scan root, and a
developer cannot fix a violation in a file `build_runner` rewrites. Everything else under
`lib/` is scanned.

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
Flutter `assets/` tree, and it is a separate asset from the logo. Who produces it, and
whether it is generated, is open — see Open Questions.

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

**A purchasable theme needs a theme to sell.** One beyond the two free ones has to exist
and ship in the submitted build, and no third theme is specified today — so that product
cannot be configured until one is. Which theme is the paid one is open, and so is
whether paid themes are ultimately one product, one per theme, or a bundle: one
purchasable theme at first release settles the launch shape, not the model. See Open
Questions.

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
**Nothing is transmitted, so the privacy nutrition label's answer for the build being
submitted is "no data collected."** The app operates no server of its own: entitlements
live with Apple and are verified on device, crash reports are built and never sent, and
there is no analytics or advertising SDK to declare — see **Crash Reporting** and
**In-App Purchases and Entitlements** above.

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
- **Which image model and which audio model?** Nothing can be generated until both are
  chosen, and the image model has to be one that emits transparent PNG and can be asked
  for a square render.
- If no audio model emits mp3, do we ship wav instead, or transcode with **ffmpeg**? The
  second adds an external binary nothing else in the project needs.
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
- What happens if the next game is started while a game is still in progress? Starting the
  next game is settled for a *finished* game — reset the board, carry the score, apply the
  turn-order rule — and there is no first player to derive from a board with no result.
  The candidates are throw, reset and discard the game in progress, or leave it undefined.
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
- Which store plugin sits behind the purchase layer. Nothing is chosen, and it is the
  largest single thing standing between this section and a build. Whichever it is has to
  expose the StoreKit 2 semantics this section depends on — the current-entitlements query,
  the ability to re-issue it on demand, the explicit restore call, and the stream of
  transactions that resolve out of band. Not every Flutter plugin surfaces all four. See
  Platform and Targets → Minimum iOS version.
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
