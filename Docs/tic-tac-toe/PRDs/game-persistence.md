# PRD: Game Persistence — the storage layer and its schema

> **Status:** Draft · Source docs read: [Tech Design](../Tech%20Design.md),
> [Menus and UI](../Menus%20and%20UI.md), [Game Overview](../Game%20Overview.md),
> [Rules](../Rules.md), [Game Board Design](../Game%20Board%20Design.md),
> [Theming](../Theming.md), [Animations](../Animations.md). *Alternative Game Styles* is a
> parking lot and was not sourced from.

## Problem

Nothing the players do survives closing the app. The rules engine holds a whole game plus the
series it belongs to, and `lib/storage/` holds the five player preferences, but there is no
home for an open game — so a session ends when the app does, the open-games list has nothing
to list, and `openGameCountProvider` is hardcoded to zero.

This is the one part of the feature worth settling on paper: the record shape lands on
players' devices, and changing it afterwards is a migration rather than an edit.

## Goal

An open game — the whole series, board and scoreboard together — is written to device
storage and read back exactly as it was left, addressed by an opaque store-minted id, ordered
most-recently-played first, and capped at a ceiling this layer reads but does not own. Only
`lib/storage/` knows the store is Hive; every caller depends on a repository interface whose
reads answer "nothing stored" rather than defaulting or throwing.

## Requirements

### The stored record

**R1.** A stored open game is a single record holding the engine's whole game-plus-series
state, plus three things that are storage's own: the record id, the opponent name the game is
titled with, and two timestamps. Those three sit alongside the game state rather than inside
it. *(Tech Design → Persistence and Serialization → What a stored open game holds; Tech
Design → The Rules Engine → What the engine is not)*

**R2.** A record round-trips without loss: reading back a record yields game state equal,
field for field, to what was written — the 81 cells, the nine quadrant states, the placement
state, whose turn it is, the last completed move, the result, the winning line, the running
score, and who went first this game. *(Tech Design → One value holds the game and the series;
→ What a stored open game holds)*

**R3.** The most recent completed move is persisted as the move itself — the quadrant and the
cell — and never as a derived value such as the forced quadrant. It has two consumers: the
forced quadrant is derived from it and is not recoverable from the cells, and the last-move
highlight is drawn from it. Where the engine has no last move, the record has none, and no
stand-in value is written. *(Tech Design → What a stored open game holds; → The engine
publishes… / last completed move is absent rather than a stand-in)*

**R4.** The persisted series carries enough state to resume turn order across games with the
app having been closed in between: reopening a stored series and taking the next game puts
the same player first as it would have without the restart. *(Tech Design → What a stored
open game holds; [Rules](../Rules.md) → Turn Order Across Games)*

**R5.** Every record written carries a stamp identifying the app version that wrote it, from
the first release, and the repository owns that stamp exactly as it owns the timestamps
(R9): the caller supplies no version and anything it passes is discarded. The stamp means
*the app version that last wrote this record*, so a record created under one version and
saved under a later one carries the later one. Nothing branches on the stamp today — what the
app does on reading a record written by an older version is unanswered (see Open Questions).
*(Tech Design → Every persisted record carries a version stamp; → What a stored open game
holds, for the same choke-point reasoning applied to the timestamps)*

**R6.** The opponent name is stored on the record as supplied at create and is never the
record's key: it is a title, and duplicate titles are the ordinary case. A save is not a
rename — it preserves the stored name and discards whatever the caller passed, the same way
it preserves the created timestamp (R9), so a caller holding a stale copy cannot overwrite a
title. No doc specifies a rename and none is added here. *(Tech Design → What a stored open
game holds; [Menus and UI](../Menus%20and%20UI.md) → Play Game → Where It Takes You)*

### The id

**R7.** The id is opaque, store-minted, and stable for the life of the record: a rematch, a
rename, or any number of saves leave it identical, and it is never reused after a delete.
Nothing parses it, derives ordering from it, or displays it. *(Tech Design → What a stored
open game holds)*

### The timestamps

**R8.** The record carries both a created and an updated timestamp — not one or the other —
and both are UTC. A local `DateTime` serialized to ISO-8601 carries no offset, so a record
written in one timezone would read in another as a different instant, and the list is ordered
on exactly that comparison. *(Tech Design → What a stored open game holds)*

**R9.** The repository owns both timestamps and the caller supplies neither. Create stamps
both from the clock, equal to each other. A save stamps updated from the clock and preserves
the stored created value, discarding whatever the caller passed in either field. *(Tech
Design → What a stored open game holds; → The open-games list has a defined order)*

### The repository contract

**R10.** The layer publishes a repository interface in `lib/storage/` covering create, read
one, read all, save, and delete. Every caller depends on that interface rather than on any
implementation. **Create takes the opponent name and the board the game starts from, and
nothing else** — no id, no timestamps, no version (R5, R7, R9) — and on success answers the
stored record, its minted id included, because the id is store-minted and the caller has no
other way to learn it (R7). *(Tech Design → Serialization and the storage layer; → What a
stored open game holds; Project Structure)*

**R11.** Every operation is asynchronous. *(Tech Design → Reads return "nothing stored", and
defaults resolve above this layer)*

**R12.** Every read returns "nothing stored" — never a default, and never a throw. An id that
is not held and an id whose stored record cannot be read back — malformed JSON, a missing or
wrong-typed field — answer identically: nothing stored. Reading the list of an empty store
answers an empty list, which is a valid state rather than an error. A read stays a read: a
record that failed to decode is neither rewritten nor deleted. *(Tech Design → Reads return
"nothing stored", and defaults resolve above this layer)*

**R13.** A record that cannot be read back is skipped by the list read, and every other
stored game comes back. Failing the whole read on one bad record would hide every game the
player still has. *(Tech Design → Reads return "nothing stored", and defaults resolve above
this layer)*

**R14.** Reading the open-games list returns most-recent-first on the updated timestamp,
tiebroken by the created timestamp, most recent first — never the box's iteration order, and
never the id. Hive's iteration order is not stable across compaction. The tiebreaker is
load-bearing: a freshly created record has both stamps equal, so two games created before
either is played tie on the primary key, and Dart's `List.sort` is not stable. Records tying
on **both** stamps are separated by a final key of the implementation's choosing, so the
comparator is total; ordering by that key is not the rule and it is never a display order.
The result is deterministic — the same stored set produces the same sequence on every read
and across relaunches. *(Tech Design → The open-games list has a defined order;
[Menus and UI](../Menus%20and%20UI.md) → Play Game → Where It Takes You)*

**R15.** Any save moves its record to the top of that order, including a save that is not a
move — taking the next game puts that series first before a mark is placed in it. *(Tech
Design → The open-games list has a defined order)*

**R16.** A save against an id the store does not hold writes nothing and creates nothing. It
is not an upsert: creating that way would bypass the create-time cap (R17, R19) and could
resurrect a game that R20 deleted permanently. It does not throw either — it comes back as a
value the caller can act on, in the same spirit as a refused create (R17), because a silent
no-op that discards a player's move is the other failure. *(Tech Design → The cap is enforced
on create, and the store never evicts; → Reads return "nothing stored", and defaults resolve
above this layer)*

**R17.** Creating an open game is refused when it would exceed the current ceiling. Reaching
the cap is an ordinary, player-reachable condition rather than an error, so a refused create
comes back as a value carrying the effective ceiling and how many games are held — enough for
the caller to say "3 of 3" without a second round trip — and never as a throw. *(Tech Design
→ The cap is enforced on create, and the store never evicts)*

**R18.** The ceiling is read from entitlement state and reaches the repository from outside
it — supplied to the implementation when it is constructed, or read through a source it is
given, never looked up by `storage/` itself. This layer defines neither number: no file under
`lib/storage/` states 3 or 100. *(Tech Design → The cap is enforced on create, and the store
never evicts; → In-App Purchases and Entitlements → Ownership is keyed by product;
[Menus and UI](../Menus%20and%20UI.md) → How many open games we keep)*

**R19.** The cap is a create-time check and not a standing invariant: it constrains what may
be added and nothing else. The store never evicts — a create at the ceiling removes nothing —
and if the ceiling drops below the number already stored, nothing here deletes anything.
*(Tech Design → The cap is enforced on create, and the store never evicts;
[Menus and UI](../Menus%20and%20UI.md) → How many open games we keep)*

**R20.** Deleting removes one open game and its whole series — board, scoreboard and all —
permanently, leaves every other stored game untouched, and touches no preference. Nothing
else in this layer discards a record: a game left mid-play is still there, with its
scoreboard, on the next read. *(Tech Design → The cap is enforced on create, and the store
never evicts; [Menus and UI](../Menus%20and%20UI.md) → Deleting an open game; → Leaving a
game mid-play)*

### Boundaries the layer has to hold

**R21.** Only `lib/storage/` knows the store is Hive. No file outside it imports `hive_ce` or
`hive_ce_flutter`, and `lib/engine/` imports neither — `hive_ce_flutter` is not pure Dart.
This is held with a check rather than discipline, like the neighbouring boundary rules, and
the check is a **new, app-wide one**: the existing engine-purity test scans `lib/engine/`
only, so it cannot see a Hive import in `lib/ui/` or `lib/state/`. *(Tech Design →
Serialization and the storage layer; → The Rules Engine)*

**R22.** The box holds JSON. No Hive `TypeAdapter` is written or registered anywhere in the
app. *(Tech Design → Serialization and the storage layer)*

**R23.** The box has one name, fixed by this document rather than by whoever writes the code
first: **`open_games`**. It becomes on-disk identity the moment a record ships, so it is
schema, and renaming it later orphans every stored game. *(Tech Design → Serialization and
the storage layer — the Hive box lives in `storage/`; naming it here follows the same
reasoning as the preference store's fixed key namespace under → Reads return "nothing
stored")*

**R24.** Serialization lives with the model, in pure Dart with no Flutter import: the
engine's game-plus-series state converts to and from JSON in `lib/engine/`, and the storage
layer writes no encoding of the game state of its own. The existing hand-written engine
models — `Board`, `Move`, `QuadrantState`, `PlacementState`, `Score` — are **kept as they
are** and gain conversion; they are not rewritten through `freezed`. Generated serialization
is permitted where it is simpler and required nowhere. *(Tech Design → Serialization and the
storage layer — see Notes for the Design Docs below, where that section is now wrong on
`freezed`)*

**R25.** The layer is testable against an in-memory fake of the repository interface with no
Hive initialized. *(Tech Design → Serialization and the storage layer)*

### The wiring that makes the writes real

Persistence nothing calls is not persistence. These five are the minimum that connects the
layer to the game being played, and nothing beyond them is in scope.

**R26.** A game is written to storage after every confirmed move, as the move is confirmed
rather than on leaving the game. *(Menus and UI → Persistence → When a game is written to
storage)*

**R27.** Taking the next game is written straight away too, even though it is not a move —
otherwise a player who takes the rematch and quits before playing reopens the finished board
with the result card still over it. *(Menus and UI → When a game is written to storage)*

**R28.** Leaving a game performs no write of its own. A force-quit, a crash and a deliberate
walk back to the main menu all leave the same thing on disk. *(Menus and UI → Leaving a game
mid-play)*

**R29.** The game in play is identified by its record id in the state layer, so a save knows
which record it is saving. *(Tech Design → What a stored open game holds — the id is the only
thing that identifies an open game; → The screen loads its game before it draws one)*

**R30.** The game screen reads the stored game it was opened for, by that id, and draws no
board and no scoreboard until the read lands. Starting a brand-new game creates its record
first (R10), and the id that create answers with is what the session then holds.
*(Tech Design → The screen loads its game before it draws one;
[Menus and UI](../Menus%20and%20UI.md) → Play Game → Where It Takes You: "Opening a game from
the list shows that game… the board is not drawn until the saved position has loaded")*

## Out of Scope

- The open-games list screen and every row's content, the New Game name prompt and its
  `ItSaMeMaRiO` default and 16-character limit, swipe-to-reveal, the trash button and the
  delete confirmation modal. This PRD covers the delete *operation*, not the flow that calls
  it. *(Menus and UI → Play Game → Where It Takes You; → Deleting an open game)*
- What the app offers a player who is already at the cap. This layer refuses the create and
  reports the numbers; what is shown is not settled — see Open Questions.
- Every widget, route, navigation, theming, animation, audio and haptic behaviour **except
  the wiring named in R26–R30** — holding the played game's id, loading a game by id before
  drawing it, saving on a confirmed move and on the next game, and creating a record for a
  brand-new game. Nothing beyond those five.
- What the caller does with R16's "no such record" answer, and with R12's "nothing stored"
  when a game the player opened is gone — see Open Questions.
- The five player preferences, already built on `shared_preferences`, and the preference
  store's key namespace.
- Entitlements and purchases beyond reading a ceiling. Nothing here queries the store, and
  nothing in `storage/` talks to a network. *(Tech Design → Entitlement state is written down,
  never minted)*
- Where entitlement state itself is persisted — an open question below, and a separate box or
  key either way.
- The rules engine's own behaviour. Nothing in this feature changes what a move does.
- Renaming a stored game. R7 requires the id survive one; no rename operation is specified by
  any doc, and none is added here.
- Persisting crash reports. They are held in memory today. *(Tech Design → Reports are held
  in memory)*

## Notes for the Design Docs

Not open questions — settled things the docs do not yet say correctly. Recorded here for
whoever revises them; this PRD does not fix a design doc.

- **`Tech Design.md` → *Serialization and the storage layer* is wrong on `freezed`.** It says
  "`freezed` + `json_serializable` for the domain models in `engine/`". The engine's models
  ship hand-written, with 193 tests pinning them, and they stay that way (R24) — regenerating
  them buys no behaviour change while putting the purity guarantee through a generator. What
  the doc is actually asking for, and what survives, is that serialization live with the
  model in pure Dart.
- **The shipped `PreferencesRepository` writes no version stamp**, though Tech Design → *Every
  persisted record carries a version stamp* requires one on both stores. The
  `shared_preferences` implementation does write a `version` key; the interface and the
  in-memory implementations do not carry the rule. Out of scope here — flagged so it is not
  lost.
- **`lib/state/open_game_count.dart` is hardcoded to zero**, with a comment saying game
  persistence does not exist yet. It becomes wrong the day this ships.

## Open Questions

**1. Reading a record written by an older app version.** Carried unchanged from
[Tech Design](../Tech%20Design.md) → Open Questions → *1. Persisted data — migration*:

> When the shape of stored data changes — a fifth preference is added, a key is renamed, an
> open game gains a field — what happens to data already on the device? A game written by
> v1.0 has to still load in v1.1.

Every record carries the stamp (R5) and nothing reads it, which is where the preferences
implementation already stands.

**2. What the player sees when the game they opened is gone or unreadable.** R12 and R13
settle what the *storage layer* answers; what the app does with that answer is open. Carried
from [Menus and UI](../Menus%20and%20UI.md) → Open Questions: **"What should happen when a
player opens a game that is no longer there, or that can't be read back?"** — *"Going quietly
back to the main menu tells them nothing about why, and an error surface would need copy and
a control that nothing specifies."*

**3. What supplies the ceiling before entitlements exist** — *my question, not the docs'.*
R18 forbids `storage/` from defining 3 or 100, and entitlement state does not exist yet, so
something outside this layer has to state the default 3 in the meantime.

**4. Games already stored above the cap if the unlock goes away.** Carried from
[Menus and UI](../Menus%20and%20UI.md) → Open Questions: *"A player with 60 open games whose
ceiling drops back to 3 has 57 games nothing is willing to touch."* R19 settles that this
layer deletes none of them; what the app does about it is open.

**5. Which store holds entitlement state.** Carried from [Tech Design](../Tech%20Design.md) →
Open Questions → *5.* — `shared_preferences` alongside the five preferences, or Hive, which
"means a second box beside the open-games one." It decides whether this layer's box is the
only one.

**6. How a test builds a mid-game board.** Carried from [Tech Design](../Tech%20Design.md) →
Open Questions → *9.*: *"The tempting shortcut is building fixtures from stored JSON, and that
binds the whole suite to a serialized shape 1. Persisted data — migration above leaves open —
where the breakage then looks like a rules failure rather than a fixture one."* This feature
is what makes that shortcut available.
