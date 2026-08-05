# PRD: Persistence — the storage layer

> **Status:** Draft · Source docs read: `Tech Design.md`, `Menus and UI.md`,
> `Game Overview.md`, `Theming.md`, `Animations.md`, `Rules.md`,
> `Game Board Design.md`. (`Alternative Game Styles.md` is a parking-lot doc and was not
> sourced. `design_handoff_game_ui/` is a read-only reference asset; its *State* section
> is recorded by `Tech Design.md` as a sketch, not a decision, and no requirement below
> comes from it.)

**Wave:** P1 — ships in the first wave, parallel-safe with the other P1 PRDs.

**Dependencies:**

- `P1-02-engine-rules.md` owns the domain models this layer serializes. Same wave, so
  build against the model API rather than defining models here. This PRD names *what
  must survive a restart*, never the class or field shape.
- `P1-03-theme-system.md` owns theme materialization. This PRD only stores and returns
  the selected theme's UUID.
- `P4-05-in-app-purchases.md` owns querying, purchasing and restoring — every StoreKit
  interaction. This PRD owns only what is written to the device as a result. The two meet
  at one seam: that PRD produces entitlement state, this one persists and serves it.
- `P3-02-open-games-list.md` consumes this layer, and owns the open-games list UI
  including the delete action's presentation and confirmation. It shares one unresolved
  decision with this PRD — what happens when a player at the cap starts a new game. See
  Open Questions 3.
- `P3-04-settings.md` consumes this layer; nothing here depends on it.

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
live in Hive as JSON behind a repository interface that can also delete them, and the
player's purchased entitlements are readable locally so the open-game ceiling and which
themes are unlocked resolve without asking Apple every time. A player can quit mid-move,
relaunch, pick the same game out of the open-games list, and find the board, whose turn it
is, and the series scoreboard exactly as they left them — while `engine/` stays pure Dart
and no caller outside `storage/` knows Hive exists.

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
   restored game is equal to the one saved.

7. **An open game persists a whole series, not one board.** What survives per open game:
   the board, whose turn it is, that game's own running scoreboard (Player One / Ties /
   Player Two), and the opponent name the game is titled with in the open-games list.
   *Source: `Menus and UI.md` → Decisions → What does an open game hold? and → What does
   each row in the open-games list show?; `Game Overview.md` → Decisions → Scoreboard
   lifetime and → Session Structure; `Tech Design.md` → Decisions → Game state storage —
   Hive ("the board, whose turn it is, and the scoreboard").*

8. **A rematch continues in the same stored open game.** It does not create a second
   stored record; the scoreboard carries over and increments.
   *Source: `Menus and UI.md` → Game Over → Rematch and → Decisions → What happens when a
   game ends?, → What does an open game hold? ("A rematch continues in the same open game
   with the scoreboard intact").*
   *Testable:* after a rematch, the count of stored open games is unchanged, the record's
   identity is unchanged, and the score reflects the finished game.

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

10. **The store never holds more open games than the current ceiling, and the ceiling is
    not a constant: 3 by default, 100 with the $4.99 cap entitlement.** The ceiling is
    resolved from entitlement state (requirement 18) at the moment it is enforced, never
    hardcoded to 3.
    *Source: `Menus and UI.md` → Decisions → How many open games do we keep? ("3 by
    default, no more. A $4.99 in-app purchase raises the cap to 100 open game slots");
    `Tech Design.md` → Decisions → In-app purchases.*
    *Testable:* with no cap entitlement, no sequence of operations leaves more than 3
    stored; with the entitlement, the same sequences allow up to 100; a test that flips
    the entitlement changes the enforced ceiling with no code change.
    *Not specified here:* what happens when a player at the ceiling starts a new game.
    The docs settle both ceilings and neither behavior at them, so this PRD does not
    choose between refusing the new game and replacing an existing one — see Open
    Questions 3, which `P3-02-open-games-list.md` carries too. Implement requirement 10
    so that both answers stay reachable; do not bake either one in before it is decided.

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
    Project structure — layer-first.*
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
    Project structure — layer-first.*
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
    The app's one sanctioned network path belongs to `P4-05-in-app-purchases.md`, not
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
    gains a delete action, so a slot can be freed").*
    *Testable:* with the ceiling reached, delete one game and a create then succeeds; the
    surviving games and all four preferences are unchanged; the deleted game is still
    absent after rebuilding the store from disk.
    *Not here:* the delete affordance, and whether it confirms first, belong to
    `P3-02-open-games-list.md`.

### Entitlements

> **Premise flag.** That entitlement state is kept on the device *at all* is not stated in
> any design doc — it comes from this PRD's task direction. What the docs settle is that
> the two purchases exist and that Apple is behind them. Which store holds it, and whether
> it is stored rather than re-queried at launch, is Open Questions 5.

18. **Entitlement state is locally readable, covering both purchasable kinds:** per-theme
    unlocks (every theme beyond the two free ones) and the $4.99 100-slot cap unlock. It
    is readable without a StoreKit round trip, so requirement 10's ceiling and a theme's
    unlocked state both resolve from local data.
    *Source: `Tech Design.md` → Decisions → In-app purchases ("Themes beyond the two free
    ones ... and a $4.99 unlock that raises the open-game cap from 3 to 100");
    `Theming.md` → Decisions → Which themes are free, → Are themes unlockable/rewards.
    The local-readability premise is flagged above.*
    *Testable:* the ceiling and a theme's unlocked state can both be read with no network
    available and no StoreKit double configured.

19. **Apple is the authority; the local copy is a cache and never the grantor.** Nothing
    in this layer grants, mints or upgrades an entitlement on its own — it stores what
    `P4-05-in-app-purchases.md` hands it, and a locally stored entitlement is superseded
    by what Apple reports whenever the two disagree. Restoring purchases on a fresh
    install must be able to repopulate this state from Apple alone, with nothing on the
    device to seed it.
    *Source: `Tech Design.md` → Decisions → In-app purchases ("in-app purchases require
    StoreKit, which needs network access and a restore-purchases path tied to the Apple
    ID"); → What the Design Docs Already Imply → the amended Fully offline row.*
    *Testable:* the storage API exposes no way to set an entitlement except by applying a
    result supplied by the purchases layer; on an empty device, a restore repopulates
    entitlements with no local seed.

20. **With nothing stored and nothing purchased, the defaults are the free tier:** a
    ceiling of 3 open games, and only Neon and Classic Red vs Blue unlocked.
    *Source: `Menus and UI.md` → Decisions → How many open games do we keep?;
    `Theming.md` → Decisions → Which themes are free ("Neon and Classic Red vs Blue are
    free. Every theme beyond those two is paid").*
    *Testable:* on an empty store, the ceiling reads 3 and every theme other than those
    two reads as locked.

## Out of Scope

- **The domain models themselves** — board, move, score, and their `freezed` /
  `json_serializable` definitions: `P1-02-engine-rules.md`.
- **Querying, purchasing and restoring** — StoreKit, product lookup, the purchase flow,
  the restore-purchases path, receipt handling, and the paywall UI:
  `P4-05-in-app-purchases.md`. This PRD covers only what lands on the device afterwards.
- **The open-games list UI**, including the delete action's presentation and confirmation,
  and what a player sees when the ceiling is reached: `P3-02-open-games-list.md`. The
  underlying decision both PRDs are waiting on is Open Questions 3.
- **The settings screen and its toggles' UI**: `P3-04-settings.md`.
- **Theme loading, merging over Neon, and materialization** — this layer stores a UUID and
  nothing else about themes: `P1-03-theme-system.md`. Labelling which themes are free or
  paid in the selection list is that PRD's and `P4-05`'s; requirement 18 only stores the
  answer.
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

### 3. What happens when a player at the cap starts a new game? (author-raised)

**Partly answered, still open.** `Menus and UI.md` → Decisions → Deleting an open game now
gives the player a way to free a slot, which removes the trap that made refusing
unsurvivable — a player at the cap is no longer stuck there permanently. It does not decide
what the *attempt* does. The ceiling is now 3 or 100 (requirement 10); the question applies
at whichever one is in force.

Where the three sources stand:

- **The design docs settle both ceilings and neither behavior at them.** `Menus and UI.md`
  → Decisions → How many open games do we keep? says "3 by default, no more" and names the
  $4.99 unlock to 100. No doc says what a create attempt at the ceiling does.
- **The read-only handoff says replace-oldest.** The `1b` screen footer in
  `design_handoff_game_ui/` reads "Starting a fourth replaces the oldest," and the handoff
  annotates that line as unconfirmed. It is a reference asset, not a decision, and it
  predates both the delete action and the 100-slot tier.
- **`P3-02-open-games-list.md` carries this same question**, having reached it
  independently from the UI side. Both PRDs point here rather than each asserting an
  answer.

The two candidate behaviors, now that delete exists:

- **Refuse** — the new game is not created; the player is told the list is full and
  deletes one, or buys the 100-slot unlock, first. Nothing already played is destroyed
  without the player choosing it. The cost is a dead end at the moment they wanted a new
  game.
- **Replace the oldest** — the new game is created and the oldest open game is deleted,
  scoreboard and series included. Starting a new game always works, at the cost of
  silently discarding a series the player never chose to lose — which now sits oddly
  beside an explicit delete action.

Until this is answered, requirement 10 asserts only the ceiling, and neither behavior is
implemented — in this layer or in the open-games list.

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
- **Which layer owns preference access.** `Tech Design.md` → Project structure —
  layer-first describes `storage/` only as "the repository interface and its Hive
  implementation," and never says where `shared_preferences` access lives. Requirement 14
  settles only the part the docs do settle — that it cannot be `engine/`.

<!-- Closed since the previous draft: "how is an open-game slot ever freed" is answered by
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
  which collides with a game that is otherwise fully playable with no network.

Two consequences ride on the answer and are also unsettled:

- **What a player sees before the first successful query on a cold, offline launch** — the
  free tier, or the last known state.
- **What happens to stored games above the free ceiling if the entitlement goes away**
  (refund, family-sharing change, a restore that returns less than before). A player with
  60 open games whose ceiling drops to 3 has 57 games that requirement 10 says should not
  exist. Deleting them is destructive; keeping them silently violates the ceiling. The docs
  do not cover this, and this PRD does not choose.
