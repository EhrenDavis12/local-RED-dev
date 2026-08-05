# PRD: Persistence — the storage layer

> **Status:** Draft · Source docs read: `Tech Design.md`, `Menus and UI.md`,
> `Game Overview.md`, `Theming.md`, `Animations.md`, `Rules.md`,
> `Game Board Design.md`. (`Alternative Game Styles.md` is a parking-lot doc and was not
> sourced. `design_handoff_game_ui/` is a read-only reference asset; its *State* section
> is recorded by `Tech Design.md` as a sketch, not a decision, and no requirement below
> comes from it.)

**Wave:** P1 — ships in the first wave, parallel-safe with the other P1 PRDs.

**Dependencies:**

- `P1-01-app-scaffold.md` creates the `lib/storage/` directory this PRD fills, as part of
  the layer-first tree (its req 2), and states the `engine/`-purity rules from the scaffold
  side (its reqs 4–5). Requirements 12–14 below constrain what goes *in* that tree; they do
  not create it. Same wave.
- `P1-02-engine-rules.md` owns the domain models this layer serializes. Same wave, so
  build against the model API rather than defining models here. This PRD names *what
  must survive a restart*, never the class or field shape.
- `P1-03-theme-system.md` owns theme materialization. This PRD only stores and returns
  the selected theme's UUID.
- `P1-07-entitlements.md` owns the entitlement model, the free-tier defaults, the cap
  numbers, the per-theme query interface and the rule that Apple is the authority while the
  local copy is a cache. Same wave, so build against that interface. This PRD owns only
  what is written to the device and read back. `P4-05-purchase-flow.md` (wave 4) is what
  later produces the store results that entitlement state is populated from; nothing in
  this wave waits on it.
- `P4-02-open-games-list.md` consumes this layer, and owns the open-games list UI
  including the delete action's presentation and confirmation. It shares one unresolved
  decision with this PRD — what New Game does when the player is at the cap. See Open
  Questions 3.
- `P4-04-settings.md` consumes this layer; nothing here depends on it.

## Problem

There is no application code yet, so nothing survives a restart. Closing the app would
lose the player's theme choice and their three toggles, and every game in progress would
vanish — including its running scoreboard. The design docs commit to the opposite on both
counts: preferences are "remembered in whatever state it was left"
(`Menus and UI.md` → Persistence) and a game in progress is "saved to device storage —
resumable from the open-games list" (same table), with each open game carrying its own
scoreboard (`Game Overview.md` → Decisions → Scoreboard lifetime). Without a storage layer
those are unimplementable, and the decisions that depend on them — leaving a game
mid-play, rematch-in-the-same-series, deleting a game to free a slot, and a paid cap of
100 slots — cannot be built.

## Goal

The app has a `storage/` layer that is the single place local persistence happens: the
four player preferences live in `shared_preferences` (the theme as its UUID), open games
live in Hive as JSON behind a repository interface that can also delete them, and whatever
`P1-07-entitlements.md` decides the player owns is written down so it survives a restart.
A player can quit mid-move, relaunch, pick the same game out of the open-games list, and
find the board, the last move played, whose turn it is, and the series scoreboard exactly
as they left them — while `engine/` stays pure Dart and no caller outside `storage/` knows
Hive exists.

## Requirements

### Player preferences

1. **Four preferences persist, and only these four: selected theme, sound effects,
   vibrate on touch, animations.** Each survives an app restart and is restored on
   launch, in whatever state it was left.
   *Source: `Tech Design.md` → Decisions → Persistence package; `Menus and UI.md` →
   Persistence (table).*
   *Testable:* write each value, discard and rebuild the store, read back the same value.

2. **The four preferences are stored with `shared_preferences`.**
   *Source: `Tech Design.md` → Decisions → Persistence package.*

3. **The selected theme is stored as the theme's UUID, not its name.**
   *Source: `Tech Design.md` → Decisions → Theme identity — UUID ("The persisted
   'selected theme' preference stores the UUID, not the theme's name"); `Theming.md` →
   Decisions → Does the theme persist between sessions.*
   *Testable:* the stored value equals the `uuid` in the theme's YAML file; changing a
   theme's display name does not change the stored value or lose the selection.

4. **With nothing stored, the selected theme reads as Neon.** Neon is what a player gets
   before they have ever opened theme selection.
   *Source: `Menus and UI.md` → Decisions → Which theme is active by default;
   `Theming.md` → Neon Is the Base Theme.*
   *Testable:* on an empty store, the preference read returns Neon's UUID.

### Game state

5. **Game state is stored in Hive and never in `shared_preferences`.**
   *Source: `Tech Design.md` → Decisions → Persistence package ("Game state does not go
   here") and → Game state storage — Hive.*
   *Testable:* after creating and playing open games, the `shared_preferences` store
   contains only the four preference keys from requirement 1.

6. **Every open game is saved, and is resumable from the open-games list.** Resuming
   restores the board, whose turn it is, and that game's scoreboard.
   *Source: `Menus and UI.md` → Persistence (table) and → Decisions → Does a game in
   progress have to be saved to device storage?; `Tech Design.md` → Decisions → Game
   state storage — Hive.*
   *Testable:* persist a partially played game, rebuild the store from disk, and the
   restored game is equal to the one saved. Note that this check compares whatever the
   implementer chose to model, so it does not by itself catch a missing field —
   requirement 7 carries the behavioral checks.

7. **An open game persists a whole series, not one board.** What survives per open game:
   the board, the **most recent completed move** (which quadrant, which cell), whose turn
   it is, that game's own running scoreboard (Player One / Ties / Player Two), and the
   opponent name the game is titled with in the open-games list.
   *Source: `Menus and UI.md` → Decisions → What does an open game hold? and → What does
   each row in the open-games list show?; `Game Overview.md` → Decisions → Scoreboard
   lifetime and → Session Structure; `Tech Design.md` → Decisions → Game state storage —
   Hive ("the board, whose turn it is, and the scoreboard"). For the last completed move:
   `P1-02-engine-rules.md` req 23 — the engine's state includes the most recent completed
   move, and it is "what has to survive leaving and resuming a game" — citing
   `Game Board Design.md` → Last Move Highlight and → Lifetime, and `Menus and UI.md` →
   Leaving a game mid-play.*
   *Why the last move is called out:* it has **two** consumers, and the move itself is the
   only thing that serves both. The forced quadrant is derived from it and is **not**
   derivable from the board; the opponent's last-move highlight is rendered from it
   (`P3-01-board-rendering.md` reqs 19–20). Its field name and shape stay
   `P1-02-engine-rules.md`'s (its OQ-3); this requirement says only that it must survive.
   *Testable, both assertions:*
   1. Resume a game whose previous move forced a quadrant — the resumed game forces the
      same quadrant.
   2. Resume a game and the opponent's last-move ring is still drawn, on the same cell it
      was on before the restart.
   An implementer who persists only a derived `forcedQuadrant` passes assertion 1 and
   requirement 6, and fails assertion 2 — which is the case where the highlight silently
   vanishes on every resumed game.

8. **A rematch continues in the same stored open game, and does not itself change the
   score.** Taking the rematch resets the board for the next game; the series score is
   carried forward exactly as it stands, having already been incremented at game end. No
   second stored record is created.
   *Source: `Menus and UI.md` → Decisions → When does the scoreboard increment ("**At game
   end.** The winner's column, or Ties, increments as soon as the game is won or tied — not
   when a rematch is taken. Taking the rematch only resets the board"); → Game Over →
   Rematch ("Taking it resets the board for the next game ... The rematch continues in the
   **same open game** — same series, scoreboard intact"); → Decisions → What does an open
   game hold?*
   *Testable:* after taking a rematch, the count of stored open games is unchanged, the
   stored record is the same one, its board is reset, and all three score counters are
   identical to their values immediately before the rematch was taken.
   *Boundary:* the increment itself is engine-side and lands on the move that ends the game
   — `P1-02-engine-rules.md` req 27. `P3-04-game-over-rematch.md` req 9 cites this
   requirement as its persistence boundary; the two agree that persisting a rematch writes
   a reset board and an unchanged score.

9. **The persisted series carries enough state to resume turn order across games
   correctly** — after a win the winner goes first; after a tie whoever went first in the
   tied game goes first again — with the app having been closed in between. This PRD does
   not prescribe how that is represented; the model shape belongs to
   `P1-02-engine-rules.md`.
   *Source: `Rules.md` → Turn Order Across Games and → Decisions → Who goes first after a
   tie?; `Menus and UI.md` → Decisions → What does an open game hold? ("resuming a game
   from the open-games list resumes the *series*").*
   *Testable:* finish a game in a tie, restart the store from disk, resume, and the same
   player goes first as would have without the restart.

10. **The store does not create an open game that would exceed the current ceiling.** This
    is a **create-time check**, not a standing invariant: it constrains what may be added,
    and nothing else. The ceiling is not a constant — 3 by default, 100 with the cap
    entitlement — and is read from `P1-07-entitlements.md` (its req 3) at the moment a
    create is attempted. This layer defines neither number.
    *Source: `Menus and UI.md` → Decisions → How many open games do we keep? ("3 by
    default, no more. A $4.99 in-app purchase raises the cap to 100 open game slots");
    `Tech Design.md` → Decisions → In-app purchases; `P1-07-entitlements.md` req 3, whose
    testable requires that "no other source in `lib/` defines either number."*
    *Testable:* with the cap entitlement absent, a create attempted with 3 stored does not
    add a fourth; with it present, creates succeed up to 100; flipping the entitlement
    changes the enforced ceiling with no code change; a scan of `lib/storage/` finds
    neither `3` nor `100` as a cap constant.
    *Settled, and enforced here:* the store **never evicts**. A create at the ceiling does
    not silently remove an existing game — replacing the oldest was considered and
    rejected in `P4-02-open-games-list.md` req 7 ("Nothing in this feature deletes a game
    the player did not choose to delete"). A slot is freed only by the explicit delete in
    requirement 17.
    *Deliberately not authorized here:* trimming, evicting or refusing to load games that
    already exist. If the ceiling ever drops below the number stored — an entitlement
    lapsing — this requirement does not license deleting any of them. That case is Open
    Questions 5 and is with the user.
    *Not specified here:* what the New Game action does when the create is refused —
    refuse outright, route the player into the delete flow, or offer the unlock. That is
    Open Questions 3, and `P4-02-open-games-list.md` carries it too.

11. **Leaving a game mid-play discards nothing.** Returning to the main menu from a game
    in progress leaves that game in stored open games, with its scoreboard, resumable.
    *Source: `Menus and UI.md` → Leaving a game mid-play ("going back to the main menu
    doesn't discard anything"); → Decisions → How do you get back to the main menu from a
    game?*
    *Testable:* leave mid-game, rebuild the store from disk, and the game is still
    present and equal to its pre-exit state.

### Layer boundaries

12. **`storage/` holds a repository interface with a Hive implementation that stores
    JSON, and defines no Hive `TypeAdapter`s.**
    *Source: `Tech Design.md` → Decisions → Serialization and the storage layer; →
    Project structure — layer-first. The directory itself is created by
    `P1-01-app-scaffold.md` req 2.*
    *Testable:* the source registers no adapter and generates no `TypeAdapter`; box
    values are JSON.

13. **Only `storage/` knows the store is Hive.** No file outside `storage/` imports
    `hive` or `hive_flutter`, and callers depend on the repository interface, not on its
    Hive implementation.
    *Source: `Tech Design.md` → Decisions → Serialization and the storage layer ("who is
    allowed to know it is Hive").*
    *Testable:* an import scan over `lib/` outside `lib/storage/` finds no `hive` import;
    the repository can be substituted in tests without Hive.

14. **`engine/` imports nothing Flutter-dependent — specifically not `hive_flutter` and
    not `shared_preferences`.** Persistence access lives in `storage/`, which is local
    persistence only.
    *Source: `Tech Design.md` → Decisions → Serialization and the storage layer
    ("`hive_flutter` is not pure Dart, so it must never be imported from `engine/`"); →
    Is the game logic separate from Flutter? ("pure Dart with zero Flutter imports"); →
    Project structure — layer-first. Stated from the scaffold side as
    `P1-01-app-scaffold.md` reqs 4–5; this is the same rule seen from the storage side.*
    *Testable:* an import scan over `lib/engine/` finds zero Flutter-dependent imports.

15. **Serialization lives with the model: `storage/` persists what the models' generated
    `toJson` produces and reconstructs through `fromJson`.** `storage/` writes no
    hand-rolled encoding of its own.
    *Source: `Tech Design.md` → Decisions → Serialization and the storage layer
    ("`toJson`/`fromJson` are generated into `engine/` by json_serializable ... while the
    Hive box, adapters-free, lives in `storage/`").*
    *Testable:* a save/load round trip returns an object equal to the original for every
    persisted type.

16. **`storage/` is local only — nothing in it talks to a network, StoreKit included.**
    The app's one sanctioned network path belongs to `P4-05-purchase-flow.md`, not
    here.
    *Source: `Tech Design.md` → Decisions → Project structure — layer-first ("`storage/`
    is local persistence only ... There is still no backend data layer"); → What the
    Design Docs Already Imply → "Fully offline, except for in-app purchases ... StoreKit
    is the one exception."*

### Deleting an open game

17. **The repository can delete an open game, and deleting frees a slot.** Deletion
    removes that game and its whole series — board, scoreboard and all — permanently,
    leaves every other stored game byte-identical, and touches no preference. After a
    delete at the ceiling, a new game fits.
    *Source: `Menus and UI.md` → Decisions → Deleting an open game ("The open-games list
    gains a delete action, so a slot can be freed"); `P4-02-open-games-list.md` req 7.*
    *Testable:* with the ceiling reached, delete one game and a create then succeeds; the
    surviving games and all four preferences are unchanged; the deleted game is still
    absent after rebuilding the store from disk.
    *Not here:* the delete affordance, and whether it confirms first, belong to
    `P4-02-open-games-list.md`.

### Storing entitlement state

> **Premise flag.** That entitlement state is kept on the device *at all* is not stated in
> any design doc. `P1-07-entitlements.md` originates that premise (its req 7, its own
> flagged premise); this PRD is where it lands. Which store holds it — or whether it is
> held at all rather than re-queried at launch — is Open Questions 5.

> **Boundary with `P1-07-entitlements.md`.** That PRD (same wave) is **the model**: what
> the entitlements are, what the free tier means, the cap numbers, the per-theme
> `free`/`owned`/`locked` query, and the rule that Apple is the authority. This PRD is
> **the write-down**: what bytes are stored, under what key, and what a read gives back.
> The three requirements below say nothing about what the stored values *mean* — a reader
> looking for defaults, cap values or gating belongs in `P1-07`.

18. **Entitlement state is written down and read back unchanged.** Whatever set of
    entitlements `P1-07-entitlements.md` defines — the cap unlock and the per-theme
    unlocks — survives an app restart and returns equal to what was written. Per-theme
    unlocks are keyed by the theme's **UUID**, so renaming a theme does not orphan an
    entitlement the player paid for.
    *Source: `P1-07-entitlements.md` req 7 ("Entitlement state survives an app restart.
    The values are handed to the persistence layer; `P1-04-persistence.md` owns the store,
    the keys and the format"). For UUID keying: `Tech Design.md` → Decisions → Theme
    identity — UUID, the same reasoning that makes requirement 3 store a UUID.*
    *Testable:* write an entitlement set, rebuild the store from disk, and read back an
    equal set; an unlock written against a theme UUID still reads against that UUID after
    the theme's display name changes.

19. **This layer never mints an entitlement, and only an affirmative store answer
    overwrites what is held.** It writes what the purchase layer hands it. A failed,
    timed-out or otherwise unanswered query is **not** an answer of "owns nothing" and
    must not clear or downgrade stored entitlement state.
    *Source: `Tech Design.md` → Decisions → In-app purchases ("a restore-purchases path
    tied to the Apple ID"); `P1-07-entitlements.md` req 10 (the local copy is a copy of
    Apple's answer, never the grantor) and **req 9** ("When the store cannot be reached,
    locally held entitlement state is what gating uses. A failed or timed-out query is not
    treated as an answer of 'owns nothing', and does not clear what is held").*
    *Why the narrowing:* "Apple is the authority" means an *affirmative* store answer
    overrides local state. Read as "whatever Apple reports, whenever the two disagree," a
    dropped network call is a disagreement — and a code writer working from this file
    alone would clear a player's purchases on an offline launch. A failed network call must
    not revoke something a player bought.
    *Testable:* the storage API exposes no way to set an entitlement except by applying a
    result supplied by the purchase layer; with an entitlement stored, stub every store
    call to fail, relaunch, and the stored entitlement is still there and still returned.
    *Not specified here:* what happens if the store affirmatively reports an entitlement
    **gone**. That is `P1-07-entitlements.md`'s Open Question 1 and this PRD's Open
    Questions 5; requirement 19 covers only the unanswered case.

20. **An empty store is a valid state, not an error, and reads back as "nothing stored".**
    A fresh install with no entitlement written must read cleanly, and a restore must be
    able to repopulate the store from a store result alone with nothing local to seed it.
    What "nothing stored" *means* — the free tier, a ceiling of 3, which themes are
    unlocked — is `P1-07-entitlements.md`'s (its reqs 1 and 3), not this layer's.
    *Source: `P1-07-entitlements.md` req 7 and its "Nothing here requires a network or a
    store" note, which makes an unpopulated entitlement store the normal wave-1 condition.*
    *Testable:* on an empty store the entitlement read completes and returns an empty set
    rather than throwing or returning a default tier; on an empty device, applying a
    restore result populates the store with no prior local state.

## Out of Scope

- **The domain models themselves** — board, move, score, and their `freezed` /
  `json_serializable` definitions: `P1-02-engine-rules.md`. That includes the field name
  and shape of the last completed move (its OQ-3); requirement 7 says only that it must
  survive.
- **Incrementing the score.** The increment happens engine-side at game end
  (`P1-02-engine-rules.md` req 27); this layer writes whatever the engine produced.
- **The entitlement model** — what the entitlements are, the free-tier defaults, **both cap
  numbers**, the per-theme `free`/`owned`/`locked` query, and the authority rule:
  `P1-07-entitlements.md`. Requirements 18–20 store and return values; they never define or
  interpret one, and `lib/storage/` defines neither cap number (requirement 10).
- **Querying, purchasing and restoring** — StoreKit, product lookup, the purchase flow,
  the restore-purchases path, receipt handling, and the paywall UI:
  `P4-05-purchase-flow.md`. This PRD covers only what lands on the device afterwards.
- **The open-games list UI**, including the delete action's presentation and confirmation,
  and what a player sees when the ceiling is reached: `P4-02-open-games-list.md`. The
  underlying decision both PRDs are waiting on is Open Questions 3.
- **The settings screen and its toggles' UI**: `P4-04-settings.md`.
- **Theme loading, merging over Neon, and materialization** — this layer stores a UUID and
  nothing else about themes: `P1-03-theme-system.md`. Labelling which themes are free or
  paid in the selection list is `P1-07-entitlements.md`'s (the state) and
  `P4-03-theme-selection.md`'s (the rendering); requirement 18 only stores the answer.
- **Creating the `lib/` tree** — `main.dart`, `app.dart` and the layer directories
  including `storage/` itself: `P1-01-app-scaffold.md` req 2. Requirements 12–14 constrain
  what may live in that directory and what may import it; they do not create it.
- **A migration or versioning scheme for already-stored data.** Unsettled — see Open
  Questions 1. No migration hooks, schema-version fields, or upgrade paths are designed
  here.
- **Any backend, sync, or network storage.** Multiplayer is named as a direction that
  must not be foreclosed (`Tech Design.md` → Decisions → Online multiplayer is an
  intended future direction), not as work now. StoreKit is the app's one network path and
  it is not this layer's.
- **A `music` preference.** The four persisted preferences are theme, sound, vibrate and
  animations (`Menus and UI.md` → Persistence); `Theming.md` → Sound Decisions → One-shot
  sound effects only, for now rules out background music in this version. (The handoff's
  *State* sketch lists a fifth `music` key.)

## Open Questions

### 1. Persisted data — versioning

As worded in `Tech Design.md` → Open Questions → 1. Persisted data — versioning:

> When the shape of stored data changes — a fifth preference is added, a key is renamed,
> an open game gains a field — what happens to data already on the device? A game
> written by v1.0 has to still load in v1.1.

### 2. Does leaving a game still need a confirmation prompt?

As worded in `Menus and UI.md` → Leaving a game mid-play: "Whether leaving still needs a
confirmation prompt is undecided; the original reason for one ('Leave game? Your score
will be lost') no longer applies."

### 3. What does New Game do when the player is at the cap? (author-raised)

**Narrowed since the previous draft.** What is settled now:

- **Both ceilings** — 3 by default, 100 with the $4.99 unlock. *(`Menus and UI.md` →
  Decisions → How many open games do we keep?; the values themselves are
  `P1-07-entitlements.md` req 3's.)*
- **A slot is freed by an explicit, player-initiated delete.** *(`Menus and UI.md` →
  Decisions → Deleting an open game; requirement 17.)*
- **Replace-the-oldest is ruled out.** `P4-02-open-games-list.md` req 7 records it as
  considered and rejected — "Nothing in this feature deletes a game the player did not
  choose to delete" — and notes that the `1b` footer in `design_handoff_game_ui/` that
  proposed it is stale and annotates itself as reflecting an unconfirmed question.
  Requirement 10 follows that: the store never evicts.

**Still open:** what the New Game action does when the player is at the ceiling. Candidates
named for whoever answers, not chosen here:

- **Refuse** — tell the player the list is full and leave them to delete a game
  themselves.
- **Route into the delete flow** — take the tap as intent and ask which game to replace,
  so the deletion is still the player's choice.
- **Offer the unlock** — surface the $4.99 100-slot purchase at the moment the limit
  bites.
- Or some combination of those.

`P4-02-open-games-list.md` carries this same question from the UI side. The storage half is
already fixed either way by requirement 10 — the create does not succeed, and nothing is
evicted — so this decision changes the UI's response, not this layer's behavior.

### 4. Other gaps found while writing this PRD (author-raised)

Each of these is something an implementer of this layer would otherwise have to guess.
None is resolved here.

- **First-launch defaults for the three toggles.** The docs settle that sound, vibrate and
  animations are remembered between sessions, and settle Neon as the default theme, but no
  Decision states what the three toggles read as on a store that has never been written.
  The settings mock in `Menus and UI.md` → Settings Menu draws all three as `[ON]`, which
  is a drawing, not a decision.
- **When a save is written.** "Saved to device storage" and "resumable" are settled; save
  granularity is not. Whether the store is written after every confirmed move, or only
  when the player leaves the game, decides whether a crash or force-quit mid-game loses
  moves.
- **Whether the pending (selected-but-unconfirmed) move survives a restart.** Moves are
  two taps, select then confirm (`Game Overview.md` → How a Move Is Made). The only
  statement that a pending selection is never persisted is in the handoff's *State*
  sketch, which `Tech Design.md` records as "a design sketch, not a decision taken here."
  Distinct from the *completed* last move, which requirement 7 does persist.
- **Which layer owns preference access.** `Tech Design.md` → Project structure —
  layer-first describes `storage/` only as "the repository interface and its Hive
  implementation," and never says where `shared_preferences` access lives. Requirement 14
  settles only the part the docs do settle — that it cannot be `engine/`.

<!-- Closed since earlier drafts: "how is an open-game slot ever freed" is answered by
     Menus and UI → Decisions → Deleting an open game, and is now requirement 17. -->

### 5. Which store do entitlements belong in? (author-raised)

`Tech Design.md` → Decisions → In-app purchases settles that the two purchases exist and
that StoreKit and the Apple ID are behind them. It does not say where — or whether — the
resulting entitlement state is written on the device, and `Menus and UI.md` → Persistence
still lists only the four preferences plus game state. Three candidates, and they are not
equivalent:

- **`shared_preferences`, alongside the four preferences** — small, flat, already the home
  of app-level player state. But `Tech Design.md` → Decisions → Persistence package names
  that store as being "for the four player preferences," so a fifth kind of value stretches
  it.
- **Hive** — already holds structured data, and per-theme unlocks are a growing set rather
  than a single flag. But `Tech Design.md` → Decisions → Game state storage — Hive frames
  Hive as where *game state* lives.
- **Neither — re-queried from StoreKit at launch**, with nothing persisted. Apple stays the
  only source, so nothing on the device can drift or be tampered with; the cost is that the
  ceiling and the theme list are unknown until the query returns, and unavailable offline,
  which collides with a game that is otherwise fully playable with no network. Note this
  option sits badly with `P1-07-entitlements.md` req 9, which requires locally held state
  to be what gating uses when the store cannot be reached.

Two consequences ride on the answer and are also unsettled:

- **What a player sees before the first successful query on a cold, offline launch** — the
  free tier, or the last known state.
- **What happens to stored games above the free ceiling if the entitlement goes away**
  (refund, family-sharing change, a restore that returns less than before). A player with
  60 open games whose ceiling drops to 3 has 57 games that requirement 10 declines to
  touch. Deleting them is destructive; keeping them means the stored count sits above the
  ceiling until the player deletes some. Requirement 10 is deliberately a create-time
  check so that nothing is destroyed by default, but that is a holding position, not the
  answer. The same question is `P1-07-entitlements.md`'s Open Question 1.

*Boundary note, resolved in this pass:* earlier drafts recorded that the overlap between
requirements 18–20 here and `P1-07-entitlements.md` was undrawn. It is drawn now, along the
line that PRD's own note proposes: **`P1-07` is the model, this is the write-down.**
Requirements 18–20 were reduced to storage statements, and the free-tier defaults, the cap
numbers and the gating meaning of an entitlement now live only in `P1-07`. That PRD's Open
Question 4 still records the overlap as open from its side; closing it there is its
author's call, not this PRD's.

### 6. What gives a stored open game its stable identity? (author-raised)

Nothing in the design docs establishes a unique key for an open game, and two requirements
here already lean on one: requirement 8's check that a rematch leaves "the same stored
record," and requirement 17's deletion of one specific game. Resuming a game from the list
needs the same thing.

**The opponent name cannot serve.** `P4-02-open-games-list.md` req 9 pre-fills the New Game
prompt with `ItSaMeMaRiO` and confirming without editing accepts it, so two or three games
titled `ItSaMeMaRiO` is the *default* case rather than an edge case. A name-keyed store
would collide on first use, and `Menus and UI.md` → Decisions → What does each row in the
open-games list show? makes the name a title, not a key.

No id scheme is proposed here. Whoever answers should also say whether the identity is
visible to the player at all, since it is otherwise a purely internal handle, and whether
duplicate titles need disambiguating in the list — the latter is
`P4-02-open-games-list.md`'s call.
