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

## Testing

### Unit tests for the rules engine
The rules engine gets unit tests — **this is where the real complexity is.**

### Widget tests for the board — no golden tests
**Widget tests, no goldens.** Test that taps do the right thing and that the highlight
states appear. Skip golden image tests.

### A test that fails on hardcoded theme values
**The suite carries a test that fails on hardcoded theme values, covering the slot
inventory the Architectural Rule names.** An ordinary test in the suite, not a custom
analyzer plugin. It scans the source under `lib/` for banned patterns outside the theme
layer itself, and it holds a per-file baseline that fails when a new violation appears.
There is no application code yet, so **the baseline starts at zero**.

<!-- "The theme layer" is concretely `lib/theme/`. See Project Structure. -->

The scope comes from [Theming](./Theming.md) → Architectural Rule, which derives its slot
list from what the screens actually consume rather than a closed category list. Indicative
patterns to catch, to be sharpened at the keyboard rather than settled here — and not a
complete enumeration of that slot inventory:

| Category | Roughly what the scan looks for |
|---|---|
| **Colors** | Raw `Color(0x…)` literals and references to Flutter's `Colors.*` palette |
| **Animations** | Hardcoded `Duration(…)` timing values |
| **Fonts** | `GoogleFonts.*` and literal `fontFamily:` values |
| **Piece styles** | Hardcoded `'X'`/`'O'` strings and `Icons.*` anywhere outside the theme layer |
| **Sounds and backgrounds** | Literal `assets/…` paths outside the theme layer |

Durations are in scope because [Animations](./Animations.md) → How Animations Play puts
timing inside the theme's animation definitions, so a hardcoded `Duration` is a theme
value that escaped.

PRD review found several of these indicative patterns miss the idiomatic forms this
project actually decided on, and this is a finding to sharpen rather than a redesign: the
sound rule looks for literal `assets/…` paths, but `audioplayers` uses
`AssetSource('audio/…')` and supplies the prefix itself; the font rule looks for
`GoogleFonts.*`, which will never appear because Inter is bundled; and the piece-style
rule looks for `'X'`/`'O'`, while Neon's approved marks are `✕ ○ Ø`.

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
