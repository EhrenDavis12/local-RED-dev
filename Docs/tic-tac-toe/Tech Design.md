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

### Minimum iOS version
**iOS 15.** The in-app purchase layer is built on StoreKit 2 —
`Transaction.currentEntitlements`, `Transaction.updates` and `AppStore.sync()` — and those
APIs require iOS 15.

**Watch out for:** the floor cannot be lowered. Below iOS 15 the plugin falls back to
StoreKit 1, which has no `currentEntitlements` and whose restore returns queue transactions
that do not cleanly exclude revoked purchases — so a refunded player would keep permanent
access, and it fails silently rather than as a build error.

### Orientation — portrait only
**Portrait only.** No landscape.

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
  storage/         ← repository interface + Hive implementation
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

`storage/` is local persistence only — the repository interface and its Hive
implementation (see **Persistence and Serialization** below). There is **no backend data
layer**: nothing in the app talks to a server. Online multiplayer is an intended future
direction, so tech choices must not foreclose syncing board state over a network — a
backend layer gets added if multiplayer arrives.

`navigation/` holds the app's routing layer — see **Navigation** below. It is
Flutter-side, same as `ui/` and `state/` — nothing here changes the `engine/` purity rule.
What goes inside the layer beyond that is a PRD's job, not this doc's.

`assets/themes/`, `assets/images/` and `assets/audio/` are the **designated folders for
assets** required by **Audio and Assets** below.

`audio/`, `haptics/`, `entitlements/`, `diagnostics/` and `purchase/` follow the same
one-folder-per-layer convention, each owned by the PRD named in the tree above. File names
inside each are that PRD's to decide, not this doc's.

## The Rules Engine

**The rules engine is separate from Flutter.** Board state, legal moves, sending rule,
win/cat-game detection and free-choice state are **pure Dart with zero Flutter imports**,
and the UI layer reads from it.

**Game state is immutable.** The engine never mutates a board in place — every move
produces a new state object, and that new object is what the UI renders.

The API is `Board applyMove(Board, Move)` returning new state, not `board.play(move)`
mutating in place — so the pure-Dart engine and the Riverpod layer agree on how state
changes.

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
need for persistent chrome; and it scales past this game's six screens without a second
migration.

Consequences, recorded honestly rather than as caveats:
- It adds a dependency, which `P1-01`'s exhaustive dependency list has to carry.
- Dismissing a route becomes `context.pop()` rather than `Navigator.pop`, so the
  navigation layer's internals are shaped by this choice even though its public
  operations are not.

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
  which is the failure the alternative produces.
- The value carries an indication of whether it is still provisional, so a consumer that
  cares can tell.

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
to remember rather than a thing already handled. What the gate looks like and how it
challenges is a PRD's job, not this doc's.

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
- **`produce`** creates the app record and registers the bundle identifier from the CLI.

It runs on Apple's official App Store Connect API underneath.

**Set up when actually approaching shipping — not now.**

**Watch out for:** fastlane does not automate App Review, which stays manual — and an
Apple Developer Program membership is required before any of it works.

## Open Questions

These are the things I think we need to hammer out. Grouped roughly by how much they
block other work.

### 1. Persisted data — migration
- When the shape of stored data changes — a fifth preference is added, a key is renamed,
  an open game gains a field — what happens to data already on the device? A game
  written by v1.0 has to still load in v1.1.

### 2. Theme loading
- Are all themes loaded and materialized at startup, or only the selected one, on demand?
  [Theming](./Theming.md) → Why this matters for the build says materialization happens
  "at startup" but does not say for how many themes.
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
  - **App Store category, price tier, and territory availability.**
  - **Export compliance** — asked on every upload; can be pre-answered with an
    `Info.plist` key, which is the scaffold's file.
  - **Content rights** — the submission asks whether the app contains third-party
    content, and the answer depends on the licensing of Replicate-generated assets and
    of the bundled Inter and Phosphor dependencies, none of which is established.
  - **Screenshots** at Apple's required device sizes — who captures them, and by what
    means, is unowned.
  - **App Review contact information**, and **sandbox testing of the purchase flow**
    before submission.

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
