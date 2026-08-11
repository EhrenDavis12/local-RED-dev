**Build-readiness: 93**

# PRD: Persistence — the storage layer

> **Status:** Draft · Source docs read: `Tech Design.md`, `Menus and UI.md`,
> `Game Overview.md`, `Theming.md`, `Animations.md`, `Rules.md`,
> `Game Board Design.md`. (`Alternative Game Styles.md` is a parking-lot doc and was not
> sourced. `design_handoff_game_ui/` is a read-only reference asset; its *State* section
> is recorded by `Tech Design.md` as a sketch, not a decision, and no requirement below
> comes from it.)
>
> **What remains open, and with whom:** which store holds entitlement state (OQ 5),
> whether a game id is ever player-visible (OQ 6b), and persisted-data versioning (OQ 1).
> **Closed this revision: the timestamp's shape and the sort direction (OQ 8)** — the user
> settled that `StoredGame` carries **both `createdAt` and `updatedAt`**, and that the
> open-games list sorts **most-recent-first, on `updatedAt`**. Requirement 21 carries both
> fields; requirement 29's comparator is now settled rather than proposed. (OQ 7, answered
> in the previous revision, is what put a timestamp on the record at all.)
> **Also settled by the user, and it closes a question that had been handed to a caller:
> `save` stamps `updatedAt` itself and preserves the stored `createdAt`** — the repository
> owns both fields, the caller supplies neither, and `P3-04-game-over-rematch.md` → Open
> Question 10 is answered as a consequence (requirement 21), as is that PRD's own Open
> Question 10. **The cross-PRD gap this file carried is closed:** the save trigger was settled
> in timing with no requirement claiming the call, and **`P3-02-move-input.md` req 36 now
> claims it** — with `P3-04-game-over-rematch.md` req 9 taking the rematch write and
> `P3-01-board-rendering.md` req 54 the resume read (Out of Scope → *Who calls save*, which now
> carries a read table beside the write one). One flagged risk with a named
> mitigation: the settings seed window (requirement 27). One provider ships with no consumer
> yet, by design: `musicEnabledProvider` (requirement 26).

**Wave:** P1 — ships in the first wave, parallel-safe with the other P1 PRDs.

**Dependencies:**

- `P1-01-app-scaffold.md` creates the `lib/storage/` and `lib/state/` directories this PRD
  fills, as part of the layer-first tree (its req 2), states the `engine/`-purity rules from
  the scaffold side (its reqs 4–5), fixes the no-codegen Riverpod idiom requirements 26
  and 28 follow (its req 12), and — **settled by the user** — declares the Hive packages as
  **`hive_ce` + `hive_ce_flutter`** and the Dart package name as `tic_tac_toe_extreme`
  (its *Confirmed by the user* section and req 14). Same wave.
- `P1-02-engine-rules.md` owns the domain models this layer serializes. Its **req 29**
  settles that `Board` is the whole-game-plus-series state — 81 cells, 9 quadrant states,
  placement state and active quadrant, current player, last completed move, outcome, series
  score, and who went first — and states directly that this PRD "serializes one `Board` per
  open game, plus that PRD's own opponent name and record id." Requirement 21 takes that
  verbatim. Same wave.
- `P1-03-theme-system.md` owns theme materialization, the theme catalog, Neon's identity and
  — since `Theming.md` → Decisions → *Do all four toggles ship, and is music a theme
  concern?* — the theme's music. This layer stores an opaque theme UUID string and knows
  nothing about which theme it is. Its **req 24** fixes the read/watch convention
  requirement 28 matches.
- `P1-07-entitlements.md` owns the entitlement model, the free-tier defaults, the cap
  numbers, the per-theme query interface and the authority rule. This PRD owns only what is
  written to the device and read back. `P4-05-purchase-flow.md` (wave 4) produces the store
  results that entitlement state is populated from; nothing in this wave waits on it.
- `P2-02-audio.md` (its req 5) and `P2-03-haptics.md` (its reqs 11–12 and 14) read the
  sound and vibrate settings through the providers requirement 26 declares. Both are barred
  by their own requirements from owning the default, and `P2-03` req 14 explicitly declines
  to declare `vibrateOnTouchEnabledProvider` — this PRD declares it. Wave 2, so these
  symbols must exist in wave 1.
- `P2-01-navigation.md` req 3 codes `openGame(gameId)` against the identity requirement 22
  defines, and its req 4's snippet calls `openGamesRepositoryProvider` — declared by
  requirement 28.
- `P3-02-move-input.md` owns the move-commit path (its req 4) that must call `save` after
  every confirmed move, and **its reqs 35–36 now claim that call** — req 35 declaring the
  `currentGameProvider` that holds the record `save` needs, req 36 making the write. See
  requirement 6 and Out of Scope → *Who calls save*. Wave 3.
- `P3-01-board-rendering.md` req 54 owns the **read** side of a resume: `GameScreen` calls
  `readById` in `initState` (requirements 21 and 28) and seeds `P3-02`'s `boardProvider` and
  `currentGameProvider` from the record before rendering the board. It also owns what the
  screen does when that read returns null or throws. See Out of Scope → *Who calls save* →
  **Reads**. Wave 3.
- `P4-02-open-games-list.md` consumes this layer directly — its reqs 5, 7, 10, 19, 21 and
  25 call `readAll`, `create` and `delete`, carry `GameId`, and watch the list provider
  requirement 28 declares. It owns the list UI and the delete affordance.
- `P3-04-game-over-rematch.md` req 9, `P4-03-theme-selection.md` and `P4-04-settings.md`
  read or write through the interfaces in requirements 21–29 and define no storage of their
  own.

## Problem

There is no application code yet, so nothing survives a restart. Closing the app would
lose the player's theme choice and their four toggles, and every game in progress would
vanish — including its running scoreboard. The design docs commit to the opposite on both
counts: preferences are "remembered in whatever state it was left"
(`Menus and UI.md` → Persistence) and a game in progress is "saved to device storage —
resumable from the open-games list" (same table), with each open game carrying its own
scoreboard (`Game Overview.md` → Decisions → Scoreboard lifetime). Without a storage layer
those are unimplementable, and the decisions that depend on them — leaving a game
mid-play, rematch-in-the-same-series, deleting a game to free a slot, and a paid cap of
100 slots — cannot be built. Seven PRDs across four waves already call into this layer, two
of them against symbols that exist nowhere in the repo, and until it names its operations
*and the providers that expose them* none of them can be written.

## Goal

The app has a `storage/` layer that is the single place local persistence happens, and it
publishes a concrete Dart interface the rest of the app codes against: five preferences in
`shared_preferences` under five named keys, open games in a named Hive box as JSON behind a
repository, whatever `P1-07-entitlements.md` decides the player owns written down so it
survives a restart, a watchable open-games list that refreshes itself after every write and
comes back in a stable order, and four synchronously-readable settings providers that resolve
the first-launch default in exactly one place. A player can quit mid-move — or lose the app to
a force-quit — relaunch, pick the same game out of the open-games list, and find the board,
the last move played, whose turn it is, and the series scoreboard exactly as they left them,
because every confirmed move was written as it happened. Meanwhile `engine/` stays pure Dart
and no caller outside `storage/` knows Hive exists.

## Requirements

### Player preferences

1. **Five preferences persist, and only these five: selected theme, music, sound effects,
   vibrate on touch, animations.** Each survives an app restart and is restored on
   launch, in whatever state it was left.
   *Source: `Tech Design.md` → Decisions → Persistence package (five player preferences);
   `Menus and UI.md` → Persistence (table); `Theming.md` → Decisions → Do all four toggles
   ship, and is music a theme concern? — "**Yes — all four toggles ship (Music, Sound
   Effects, Vibrate on Touch, Animations)**", which resolved the standing disagreement in
   favour of the handoff's four-toggle drawing.*
   *Testable:* write each value through requirement 21's `PreferencesRepository`, discard
   and rebuild the store, read back the same value.

2. **The five preferences are stored with `shared_preferences`.**
   *Source: `Tech Design.md` → Decisions → Persistence package.*

3. **The selected theme is stored as the theme's UUID, not its name.**
   *Source: `Tech Design.md` → Decisions → Theme identity — UUID ("The persisted
   'selected theme' preference stores the UUID, not the theme's name"); `Theming.md` →
   Decisions → Does the theme persist between sessions.*
   *Testable:* the stored value equals the `uuid` in the theme's YAML file; changing a
   theme's display name does not change the stored value or lose the selection.

4. **With nothing stored, the selected-theme read returns "nothing stored", and Neon is
   resolved above this layer.** `readSelectedThemeUuid()` returns `null` on an empty store.
   The app-level guarantee that a player who has never opened theme selection gets Neon is
   delivered by `P1-03-theme-system.md`, which owns the catalog and knows Neon's UUID.
   *Source: `Menus and UI.md` → Decisions → Which theme is active by default;
   `Theming.md` → Neon Is the Base Theme.*
   *Ratified.* An earlier draft had this layer return Neon's UUID on an empty store, which
   would put a theme constant in `lib/storage/`. `Tech Design.md` → Decisions → Do we add a
   test that fails on hardcoded theme values? bans exactly that outside the theme layer and
   `P1-05-theme-guard-test.md` enforces it, so the earlier wording shipped a guaranteed test
   failure.
   *Note the asymmetry with requirement 26:* the theme default is resolved in
   `P1-03-theme-system.md` because only the theme layer knows Neon's UUID; the four
   *toggle* defaults are resolved here, because they are plain booleans with a doc-settled
   value and no other wave-1 owner. Both follow the same rule — the default is resolved
   exactly once, at a visible site, by whoever can name the value without inventing it.
   *Testable:* on an empty store the read returns `null`; a scan of `lib/storage/` finds no
   theme UUID literal.

### Game state

5. **Game state is stored in Hive and never in `shared_preferences`.**
   *Source: `Tech Design.md` → Decisions → Persistence package ("Game state does not go
   here") and → Game state storage — Hive.*
   *Testable:* after creating and playing open games, the `shared_preferences` store
   contains only the five key strings named verbatim in requirement 24 — no game data, no
   sixth key.

6. **The repository stores an open game and returns it intact, and the app writes after
   every confirmed move.** Two claims, at two levels:

   **Repository level (this PRD's to test):** `save` followed by `readById` returns a
   record equal to the one written, across a store rebuilt from disk; `readAll` returns
   every stored game.
   *Testable:* `save` a partially played game, rebuild the store from disk, `readById`
   returns an equal record and `readAll` includes it. This compares whatever the
   implementer chose to model, so it does not by itself catch a missing field —
   requirement 7 carries the field-level check — and it is **green even if nothing ever
   calls `save`**.
   *One exception to "equal to the one written", and it is deliberate:* the two timestamps.
   Requirement 21 makes `save` stamp `updatedAt` and preserve the stored `createdAt`, so a
   record read back matches what was written **except** on those two fields, whose values
   are the repository's answer rather than the caller's input. A test asserting whole-record
   equality across a `save` must construct its expectation from the record the repository
   returns on read, not from the one it passed in.

   **App level (settled, owned elsewhere):** a game is written to storage **after every
   confirmed move**, so nothing is lost to a crash or a force-quit. The write happens on
   the move-commit path, not on leaving the game.
   *Source: `Menus and UI.md` → Decisions → When is a game written to storage? — "**After
   every confirmed move.** Nothing is ever lost to a crash or a force-quit," with the
   reasoning that each write is a single small record, the game is turn-based so writes are
   infrequent, and a game is saved specifically so it can be resumed.*
   *Testable, but not here:* the assertion that a confirmed move reaches storage belongs to
   whichever requirement claims the call site, and **`P3-02-move-input.md` req 36 now does** —
   on the commit path its req 4 defines, fire-and-forget, with its own recording-fake
   assertions that a confirming tap records exactly one `save` and that a first, reselecting,
   clearing or illegal tap records none. See Out of Scope → *Who calls save*. This PRD states
   the obligation and named the gap; closing it was that wave-3 file's to do, and it did.

7. **A stored open game carries a whole series, not one board's worth of cells.** What a
   stored record holds: the `Board` — which per `P1-02-engine-rules.md` req 29 already
   carries the cells, quadrant states, active quadrant, current player, **the most recent
   completed move**, the outcome, the series score and who went first — plus this layer's
   own record id, the opponent name the game is titled with in the open-games list, and
   the **two timestamps** requirement 21 adds.
   *Source: `Menus and UI.md` → Decisions → What does an open game hold? and → What does
   each row in the open-games list show?; `Game Overview.md` → Decisions → Scoreboard
   lifetime and → Session Structure; `Tech Design.md` → Decisions → Game state storage —
   Hive ("the board, whose turn it is, and the scoreboard"); `P1-02-engine-rules.md` reqs 23
   and 29 — the engine's state includes the most recent completed move, and it is "what has
   to survive leaving and resuming a game."*
   *Why the last move is called out:* it has **two** consumers, and the move itself is the
   only thing that serves both. The forced quadrant is derived from it and is **not**
   derivable from the cells; the opponent's last-move highlight is rendered from it
   (`P3-01-board-rendering.md` reqs 19–20).
   *Testable in this wave:* `save` a record whose last completed move is set, rebuild the
   store from disk, `readById`, and the last-move value is present and equal to what was
   written — **not** null, and not reconstructed from the cells. An implementer who
   round-trips only a derived forced-quadrant value fails this.
   *Deferred to wave 3:* the rendering consequence — that the opponent's last-move ring is
   still drawn on the same cell after a resume — is `P3-01-board-rendering.md`'s to assert
   (its reqs 19–20). Nothing in wave 1 can run a rendering check, so it is named here as
   the defect this requirement exists to prevent, and owned there as a test.
   *Both timestamps are part of the record:* Open Questions 7 settled that `StoredGame`
   carries a timestamp, and Open Questions 8 settled that it carries **two** — `createdAt`
   and `updatedAt`. Requirement 21 carries both fields, states which operation writes each,
   and requirement 29 is what reads `updatedAt`.

8. **A rematch continues in the same stored open game, and does not itself change the
   score.** Taking the rematch resets the board for the next game; the series score is
   carried forward exactly as it stands, having already been incremented at game end. No
   second stored record is created — the same `GameId` is written back.
   *Source: `Menus and UI.md` → Decisions → When does the scoreboard increment ("**At game
   end.** The winner's column, or Ties, increments as soon as the game is won or tied — not
   when a rematch is taken. Taking the rematch only resets the board"); → Game Over →
   Rematch ("Taking it resets the board for the next game ... The rematch continues in the
   **same open game** — same series, scoreboard intact"); → Decisions → What does an open
   game hold?*
   *Testable:* after a rematch is saved, `readAll().length` is unchanged, the record carries
   the same `GameId`, its board is reset, and all three score counters are identical to
   their values immediately before the rematch.
   *Boundary:* the increment itself is engine-side and lands on the move that ends the game
   — `P1-02-engine-rules.md` req 27. `P3-04-game-over-rematch.md` req 9 cites this
   requirement as its persistence boundary and was written against "whatever save point
   `P1-04` defines" — **that save point is now defined** (requirement 6), so its testable
   can be written concretely: the write lands on the confirmed move that ends the game.
   *The timestamp consequence, now settled in both halves:* the same `GameId` means the same
   record, so a rematch save keeps its `createdAt` unchanged — and, because **`save` stamps
   `updatedAt` itself** (requirement 21, settled by the user), that save also moves the game
   to the top of requirement 29's most-recent-first order. The caller does not choose: it
   passes the record and the repository stamps. This closes what
   `P3-04-game-over-rematch.md` req 9 had recorded as its Open Question 10.

9. **The persisted series carries enough state to resume turn order across games
   correctly** — after a win the winner goes first; after a tie whoever went first in the
   tied game goes first again — with the app having been closed in between. This PRD does
   not prescribe how that is represented; the model shape belongs to
   `P1-02-engine-rules.md` (its reqs 25–26 and 29).
   *Source: `Rules.md` → Turn Order Across Games and → Decisions → Who goes first after a
   tie?; `Menus and UI.md` → Decisions → What does an open game hold? ("resuming a game
   from the open-games list resumes the *series*").*
   *Testable:* save a series whose last game tied, rebuild the store from disk, read it
   back, and the engine computes the same first player as it would have without the
   restart.

10. **`create` does not add an open game that would exceed the current ceiling.** This is a
    **create-time check**, not a standing invariant: it constrains what may be added, and
    nothing else. The ceiling is not a constant — 3 by default, 100 with the cap
    entitlement — and is read from `P1-07-entitlements.md` (its req 3). This layer defines
    neither number.
    *Source: `Menus and UI.md` → Decisions → How many open games do we keep? ("3 by
    default, no more. A $4.99 in-app purchase raises the cap to 100 open game slots");
    `Tech Design.md` → Decisions → In-app purchases; `P1-07-entitlements.md` req 3, whose
    testable requires that "no other source in `lib/` defines either number."*
    *Testable:* with the cap entitlement absent, `create` with 3 stored returns
    `CapReached` and `readAll().length` stays 3; with it present, creates succeed to 100;
    flipping the entitlement changes the enforced ceiling with no code change; a scan of
    `lib/storage/` finds neither `3` nor `100` as a cap constant.
    *Settled, and enforced here:* the store **never evicts**. A create at the ceiling does
    not silently remove an existing game — replacing the oldest was considered and
    rejected in `P4-02-open-games-list.md` req 7 ("Nothing in this feature deletes a game
    the player did not choose to delete"). A slot is freed only by `delete`.
    *Deliberately not authorized here:* trimming, evicting or refusing to load games that
    already exist. If the ceiling ever drops below the number stored — an entitlement
    lapsing — this requirement does not license deleting any of them.
    *What `create` returns when refused* is requirement 25.
    *The cold-launch window is settled, and the earlier flag here was mis-routed.* An
    earlier draft warned that reading the ceiling "at the moment a create is attempted"
    presumes a synchronous answer, and pointed at `P1-07-entitlements.md`'s Open Question 3.
    That pointer was wrong twice over: OQ 3 is *which store holds the local copy*, and the
    question it described is no longer open. `P1-07` **req 13** now fixes the precedence —
    the most recent store result applied this session, failing that the values restored from
    the local copy, failing that the free tier — with `isProvisional` `true` until a store
    answer lands. So a create during the provisional window uses the **last known cap**, not
    a guess, and a paying player on a cold offline launch keeps their 100 slots.
    *What is still open is the opposite case,* and it belongs to `P1-07-entitlements.md`
    **Open Question 1** — what the app does about games already stored above the cap when an
    entitlement goes away. `P4-02-open-games-list.md` OQ 8 inherited the same mis-pointer;
    all three files describe one owner, and it is `P1-07` OQ 1.

11. **`delete` is the only operation that removes a stored game; leaving a game does not.**
    Nothing in this layer discards a record because the player navigated away — a game left
    mid-play is still present, with its scoreboard, on the next `readAll`.
    *Source: `Menus and UI.md` → Leaving a game mid-play ("going back to the main menu
    doesn't discard anything"); → Decisions → How do you get back to the main menu from a
    game?*
    *Testable:* no repository operation other than `delete` reduces `readAll().length`; a
    saved mid-play record is still returned, equal, from a store rebuilt from disk.
    *Consequence of requirement 6's save timing:* "leaving discards nothing" no longer
    depends on anything happening *at* exit. The last confirmed move was already written
    when it was confirmed, so the exit path performs no write and has nothing to lose —
    which is also why a force-quit, a crash and a deliberate exit all leave the same state
    on disk. This requirement is still a repository-level claim: it holds whether or not
    the exit path does anything at all.

### Layer boundaries

12. **`storage/` holds the repository interfaces in requirement 21 plus their Hive and
    `shared_preferences` implementations, and defines no Hive `TypeAdapter`s.**
    *Source: `Tech Design.md` → Decisions → Serialization and the storage layer; →
    Project structure — layer-first. The directory itself is created by
    `P1-01-app-scaffold.md` req 2.*
    *Testable:* the source registers no adapter and generates no `TypeAdapter`; box
    values are JSON maps.

13. **Only `storage/` knows the store is Hive.** No file outside `storage/` imports
    `hive_ce` or `hive_ce_flutter`, and callers depend on the interfaces in requirement 21 —
    reached through the providers in requirement 28 — not on their implementations.
    *Source: `Tech Design.md` → Decisions → Serialization and the storage layer ("who is
    allowed to know it is Hive"). Which Hive packages those are is settled by the user and
    recorded in `P1-01-app-scaffold.md` → Confirmed by the user and its req 14:
    **`hive_ce` + `hive_ce_flutter`**, not `hive` + `hive_flutter`.*
    *Testable:* an import scan over `lib/` outside `lib/storage/` finds no import whose
    package segment begins `hive` — which catches both spellings, so the scan survives even
    if the choice is ever revisited; every provider in requirement 28 can be overridden with
    an in-memory fake in tests with no Hive initialized.

14. **All persistence access lives in `lib/storage/`, and `engine/` imports nothing
    Flutter-dependent — specifically not `hive_ce_flutter` and not `shared_preferences`.**
    Both stores are reached only through requirement 21's interfaces. The providers in
    requirement 26 live in `lib/state/` and reach storage the same way every other consumer
    does — through `PreferencesRepository` — so no persistence package is imported outside
    `lib/storage/`.
    *Source: `Tech Design.md` → Decisions → Serialization and the storage layer
    ("`hive_flutter` is not pure Dart, so it must never be imported from `engine/`" — the
    doc names the `hive` spelling; the package is `hive_ce_flutter` per the user's
    settlement in `P1-01-app-scaffold.md`, and the rule is unchanged); →
    Is the game logic separate from Flutter? ("pure Dart with zero Flutter imports"); →
    Project structure — layer-first, which places local persistence in `storage/` and
    Riverpod providers in `state/`. Stated from the scaffold side as
    `P1-01-app-scaffold.md` reqs 4–5.*
    *Testable:* an import scan finds `shared_preferences` and `hive_ce_flutter` imported only
    under `lib/storage/`, and zero Flutter-dependent imports under `lib/engine/`.

15. **Serialization lives with the model: `storage/` persists what the models' generated
    `toJson` produces and reconstructs through `fromJson`.** `storage/` writes no
    hand-rolled encoding of its own.
    *Source: `Tech Design.md` → Decisions → Serialization and the storage layer
    ("`toJson`/`fromJson` are generated into `engine/` by json_serializable ... while the
    Hive box, adapters-free, lives in `storage/`").*
    *Boundary, because `StoredGame` is not one of those models:* the rule binds the
    **engine's** types — `Board` and everything inside it. `StoredGame`, `GameId` and the
    two timestamps are this layer's own (requirement 21), and their encoding is specified
    there rather than generated in `engine/`.
    *Testable:* a save/load round trip returns an object equal to the original for every
    persisted type.

16. **`storage/` is local only — nothing in it talks to a network, StoreKit included.**
    The app's one sanctioned network path belongs to `P4-05-purchase-flow.md`, not here.
    *Source: `Tech Design.md` → Decisions → Project structure — layer-first ("`storage/`
    is local persistence only ... There is still no backend data layer"); → What the
    Design Docs Already Imply → "Fully offline, except for in-app purchases ... StoreKit
    is the one exception ... a StoreKit query against Apple, not a service we run."*

### Deleting an open game

17. **`delete(GameId)` removes one open game and frees a slot.** Deletion removes that
    record and its whole series — board, scoreboard and all — permanently, leaves every
    other stored game byte-identical, and touches no preference. After a delete at the
    ceiling, the next `create` succeeds.
    *Source: `Menus and UI.md` → Decisions → Deleting an open game ("The open-games list
    gains a delete action, so a slot can be freed"); `P4-02-open-games-list.md` reqs 7 and
    19, which call this with the row's identifier and never with the title.*
    *Testable:* with three stored games all titled `ItSaMeMaRiO`, deleting the second
    removes exactly that record and leaves the other two byte-identical; a `create` that
    previously returned `CapReached` then succeeds; the deleted record is still absent
    from a store rebuilt from disk.
    *Not here:* the delete affordance, and whether it confirms first, belong to
    `P4-02-open-games-list.md`.

### Storing entitlement state

> **Boundary with `P1-07-entitlements.md`.** That PRD (same wave) is **the model**: what
> the entitlements are, what the free tier means, the cap numbers, the per-theme
> `free`/`owned`/`locked` query, and the rule that Apple is the authority. This PRD is
> **the write-down**: what bytes are stored, under what key, and what a read gives back.
> The three requirements below say nothing about what the stored values *mean* — a reader
> looking for defaults, cap values or gating belongs in `P1-07`. The premise flag earlier
> drafts carried is retired: `Tech Design.md` → Decisions → *Entitlements — Apple stores
> them, no backend needed* now states that "any locally stored entitlement state is an
> offline convenience, not the record," which grounds a local copy without making it the
> authority.

18. **Entitlement state is written down and read back unchanged, as the product identifiers
    the store reported.** Whatever `P1-07-entitlements.md`'s `Entitlements` carries — per
    its req 14, "the set of product identifiers the store reports as currently owned" — is
    persisted verbatim and returns equal to what was written. This layer stores identifiers;
    it translates none of them.
    *Source: `P1-07-entitlements.md` req 7 ("`P1-04-persistence.md` owns the store, the keys
    and the format"), req 11 (the `Entitlements` surface) and req 14 (what an affirmative
    store answer contains).*
    *Testable:* write an `Entitlements` carrying two product identifiers, rebuild the store
    from disk, and read back an equal value; a scan of `lib/storage/` finds no theme UUID
    literal and no product-identifier literal.

    **UUID keying withdrawn — this PRD conceding, not conforming.** Earlier drafts keyed
    per-theme unlocks by the theme's UUID, citing `Tech Design.md` → Decisions → *Theme
    identity — UUID*. That clause protects against keying on a **mutable display name**; an
    Apple product identifier is equally immutable, so the protection it was bought for is
    intact. The UUID keying was not load-bearing, and three things make product identifiers
    the only workable representation:

    - **It is what this layer is handed.** Requirement 19 says this layer writes what the
      store answer contains and interprets nothing. Re-keying to UUIDs would make storage
      translate — the exact thing the boundary note above forbids.
    - **The inverse map does not exist.** `P1-07` req 11 publishes
      `EntitlementProducts.productIdForTheme(String themeUuid) → String?`, which resolves
      **forward only**, and its reqs 5 and 12 bar that layer from reading any theme list to
      build the reverse. A UUID-keyed store would need a map nobody is allowed to construct.
    - **It would foreclose an open product decision.** `P1-07` req 2 explicitly says not to
      bake in "a fixed per-theme product list" before `P4-05-purchase-flow.md` Open
      Question 1 decides whether one purchase covers all paid themes or each theme is its
      own product. If it is one-product-covers-all, a UUID-keyed store is actively wrong —
      it would have to invent per-theme rows for a single purchase.

19. **This layer never mints an entitlement, and only an affirmative store answer
    overwrites what is held.** It writes what it is handed. A failed, timed-out or otherwise
    unanswered query is **not** an answer of "owns nothing" and must not clear or downgrade
    stored entitlement state.
    *Source: `Tech Design.md` → Decisions → Entitlements — Apple stores them, no backend
    needed ("A refunded or lapsed purchase simply stops appearing in
    `currentEntitlements`"); `P1-07-entitlements.md` req 10 (the local copy is a copy of
    Apple's answer, never the grantor), **req 13** (the precedence order while no store
    answer has been applied) and **req 14** ("A failed, timed-out or unanswered query is
    **not** an affirmative answer and must not" replace what is held).*
    *Why the narrowing:* "Apple is the authority" means an *affirmative* store answer
    overrides local state. Read as "whatever Apple reports, whenever the two disagree," a
    dropped network call is a disagreement — and a code writer working from this file alone
    would clear a player's purchases on an offline launch. A failed network call must not
    revoke something a player bought.
    *Testable:* `EntitlementsStore` exposes exactly one mutating member, `write`; with an
    entitlement stored, stub every store call to fail, relaunch, and the stored entitlement
    is still there and still returned unchanged.
    *Corrected in this pass — who may call `write` is not this PRD's to say.* An earlier
    testable asserted `write` was "reachable only from the purchase layer," which quietly
    answered the second half of `P1-07-entitlements.md` **Open Question 4** — whether
    `P4-05-purchase-flow.md` applies its result through the entitlement layer or writes
    directly to storage — against the first option, in a file that is not the owner of that
    question. This requirement now constrains only the store's own surface: **one mutator,
    and it never invents a value.** That holds under either answer to their OQ 4, and this
    PRD takes no position on it.
    *Not specified here:* what happens if the store affirmatively reports an entitlement
    **gone**. `P1-07-entitlements.md` → Open Question 1 holds it; requirement 19 covers
    only the unanswered case.

20. **An empty store is a valid state, not an error, and reads back as "nothing stored".**
    `read()` returns `null` on a fresh install, and `write` must be able to populate the
    store from a store result alone with nothing local to seed it. What "nothing stored"
    *means* — the free tier, a ceiling of 3, which themes are unlocked — is
    `P1-07-entitlements.md`'s (its reqs 1, 3 and 13), not this layer's.
    *Source: `P1-07-entitlements.md` req 7 and its "Nothing here requires a network or a
    store" note, which makes an unpopulated entitlement store the normal wave-1 condition;
    its req 13, whose precedence chain ends at the free tier "only on a device where no
    store answer has ever been applied" — which is exactly a `null` read here.*
    *Testable:* on an empty store `read()` completes and returns `null` rather than
    throwing or returning a default tier; on an empty device, `write` populates the store
    with no prior local state.

### The published interface

> Seven PRDs across four waves call into this layer. Everything in this section is
> normative: these are the names and signatures they may code against. **Nothing here is
> provisional** — the aggregate type is `Board` per `P1-02-engine-rules.md` req 29,
> `CreateGameResult` (requirement 25) is ratified, and the record's **two timestamp fields,
> which side writes each of them, and the order they produce are settled by the user**
> (Open Questions 7 and 8, and the stamping settlement recorded under 8). The
> proposal marker earlier drafts carried on the timestamp is gone.

21. **The storage layer exposes exactly three repositories, split by store**, all in
    `lib/storage/`, all abstract interfaces with one implementation each. They are separate
    because they have different backing stores and different lifetimes, and because
    requirement 5 requires the preference store to be inspectable for exactly five keys.

    ```dart
    // lib/storage/open_games_repository.dart
    abstract interface class OpenGamesRepository {
      Future<List<StoredGame>> readAll();       // ordering: requirement 29
      Future<StoredGame?> readById(GameId id);
      Future<CreateGameResult> create({
        required String opponentName,
        required Board board,
      });

      /// Writes [game] under its own id. Stamps `updatedAt` from the clock and
      /// preserves the stored `createdAt` — both timestamps on [game] are ignored.
      Future<void> save(StoredGame game);

      Future<void> delete(GameId id);
      Future<int> count();
    }

    // lib/storage/preferences_repository.dart
    abstract interface class PreferencesRepository {
      Future<String?> readSelectedThemeUuid();
      Future<void> writeSelectedThemeUuid(String uuid);
      Future<bool?> readMusicEnabled();
      Future<void> writeMusicEnabled(bool value);
      Future<bool?> readSoundEffectsEnabled();
      Future<void> writeSoundEffectsEnabled(bool value);
      Future<bool?> readVibrateOnTouchEnabled();
      Future<void> writeVibrateOnTouchEnabled(bool value);
      Future<bool?> readAnimationsEnabled();
      Future<void> writeAnimationsEnabled(bool value);
    }

    // lib/storage/entitlements_store.dart
    abstract interface class EntitlementsStore {
      Future<Entitlements?> read();
      Future<void> write(Entitlements entitlements);
    }

    // lib/storage/stored_game.dart
    final class StoredGame {
      const StoredGame({
        required this.id,
        required this.opponentName,
        required this.board,
        required this.createdAt,
        required this.updatedAt,
      });
      final GameId id;
      final String opponentName;
      final Board board;

      /// Set once, by `create`, and never written again for the life of the record.
      /// `save` preserves the stored value and discards an incoming one.
      /// UTC. Settled by the user — Open Questions 8.
      final DateTime createdAt;

      /// Stamped by `save` itself, which ignores whatever the caller passes, and
      /// requirement 29's primary sort key. UTC.
      /// Settled by the user — Open Questions 8.
      final DateTime updatedAt;
    }
    ```

    **Every operation is asynchronous.** Both Hive and `shared_preferences` are async on
    first open, and a synchronous facade would either block startup or lie about readiness.
    **Every read returns `null` or an empty list for "nothing stored"** — never a default,
    never a throw. Resolution happens once, above this layer: requirement 26 for the four
    toggles, `P1-03-theme-system.md` for the theme, `P1-07-entitlements.md` for
    entitlements.
    **`Entitlements` is `P1-07-entitlements.md`'s type**, referenced and never defined here;
    what it carries is product identifiers (requirement 18).
    **`Board` is `P1-02-engine-rules.md`'s type and carries the whole series.** Its req 29
    settles that one `Board` holds the cells, quadrant states, active quadrant, current
    player, last completed move, outcome, series score and who went first, and says
    explicitly that this PRD serializes "one `Board` per open game, plus that PRD's own
    opponent name and record id." Earlier drafts of this file proposed a separate
    `GameSeries` aggregate; that name is **withdrawn** — there is one type, it is `Board`,
    and a second name for it would be exactly the duplication req 29 exists to prevent.
    **The opponent name, the id and both timestamps are storage's**, not the engine's — no
    design doc puts any of them in game state — so they sit on `StoredGame` alongside the
    `Board`.
    **`StoredGame` carries both `createdAt` and `updatedAt`, settled by the user.** Open
    Questions 7 settled that the record gains a timestamp; Open Questions 8 settled that it
    gains **both**, not one or the other. **The user's stated reason for carrying both:** it
    leaves the sort key a *display* choice rather than a *schema* one — a list that wanted
    creation order, or a row that wanted "started on", can be served later without an Open
    Questions 1 migration.

    **The repository owns both timestamps; the caller supplies neither. Settled by the
    user.** `create` mints them — both set, and equal on a freshly created record
    (requirement 25). Then, on every `save`:

    - **`updatedAt` is stamped by `save` itself**, from the clock at the moment of the
      write. Whatever value the passed `StoredGame` carries in that field is **ignored**.
    - **`createdAt` is preserved from the record already stored under that `GameId`.** An
      incoming `createdAt` is **discarded**, whatever it is.

    So a caller passes the record it happens to be holding, and the two timestamps that come
    back are the repository's answer rather than its input.
    **Why the repository and not the caller, recorded so nobody re-derives it.** Two reasons,
    and they are the same shape as requirement 28's argument for structural refresh:
    - *Keeping `updatedAt` current stops being a rule anyone can forget.* Requirement 6's
      write happens after every confirmed move, and the call sites are spread across four
      PRDs (Out of Scope → *Who calls save*) — one of which did not exist when this was
      settled. A field each of them had
      to remember to stamp is a field that goes stale at whichever one forgets, and the
      symptom is a silently mis-ordered list rather than a failing test.
    - *`createdAt`'s immutability becomes enforceable rather than conventional.* The field's
      contract is "written once and never changes", but `StoredGame`'s constructor takes it
      as an ordinary argument, so any caller can construct a record with any `createdAt` at
      all. Nothing else in this layer could stop that value reaching disk. Having `save`
      preserve the stored one closes it at the only choke point there is.

    **Both timestamps are UTC, and both are encoded as ISO-8601 strings in the box JSON.**
    `create` and `save` stamp with `DateTime.now().toUtc()`; `StoredGame.toJson()` writes
    each field with `toIso8601String()` — which carries the trailing `Z` on a UTC value —
    and `fromJson` reads it back with `DateTime.parse(...).toUtc()`.
    **Why this is specified rather than left to the implementer:** a **local** `DateTime`
    written with `toIso8601String()` carries **no offset at all**, so a record written in one
    timezone and read in another compares against the rest as though it had been written at a
    different instant — and requirement 29 sorts on exactly that comparison, so the player's
    list would reorder itself after a flight or a DST change. Storing UTC removes the failure
    and costs nothing.
    *[The encoding is a consequence of the settlement above, not a separate decision. The
    one alternative — epoch milliseconds as an `int` — is equivalent and reverses in one
    place, `toJson`/`fromJson`. What must not ship is a local `DateTime`.]*

    **No `copyWith` on `StoredGame` is added for this, and none is added silently.** With the
    repository stamping `updatedAt` and preserving `createdAt`, a caller saving a new board
    has no timestamp to carry forward correctly, so the timestamp reason for a `copyWith` is
    gone. Whether one should exist for the *ordinary* ergonomic reason — a caller holding a
    record and wanting the same record with a new `Board`, without restating five constructor
    arguments — is a question **no requirement in any PRD currently answers**, and it is
    flagged here rather than settled: no consumer PRD requires the member. (Note
    `P3-02-move-input.md` req 22's scan bans `copyWith` on **`Board`** — a different type, a
    different rule, and not a precedent either way for this one.)

    *Testable:* `createdAt` is identical before and after any number of `save` calls on the
    same record, including across a rematch (requirement 8); `updatedAt` is not earlier than
    `createdAt` on any record; a `save` handed a record whose `updatedAt` was hand-set to the
    epoch and whose `createdAt` was hand-set to a year in the future comes back with
    `updatedAt` at the write instant — not the epoch — and `createdAt` equal to the value
    `create` minted, not the future one; two saves separated by a real interval produce a
    strictly later `updatedAt`, and no save ever moves it backwards; every timestamp read
    back satisfies `isUtc`.

22. **`GameId` is an opaque, store-minted, stable-for-life identifier**, and it is the only
    thing that identifies an open game. The repository mints it on `create`; no caller
    constructs one from data. It never changes for the life of the record — a rematch, a
    rename, or any number of saves leave it identical — and it is never reused after a
    delete.

    ```dart
    // lib/storage/game_id.dart
    final class GameId {
      const GameId(this.value);
      factory GameId.fromJson(String json) => GameId(json);
      final String value;
      String toJson() => value;
      @override bool operator ==(Object other) => other is GameId && other.value == value;
      @override int get hashCode => value.hashCode;
      @override String toString() => value;
    }
    ```

    The underlying string is a **UUID v4** minted by the repository. It is opaque: no caller
    parses it, **derives ordering from it**, or displays it. `P2-01-navigation.md` req 3
    takes it as `openGame(gameId)`; `P4-02-open-games-list.md` req 19 carries it on every
    row and passes it to resume and delete.
    *Source:* `P4-02-open-games-list.md` req 19 requires an identity that exists and is
    stable and explicitly declines to choose one; `Menus and UI.md` → Decisions → What does
    each row in the open-games list show? makes the opponent name a **title**, and `P4-02`
    req 9's `ItSaMeMaRiO` default makes duplicate titles the ordinary case, so the name
    cannot be a key.
    *Testable:* three games created with identical opponent names have three different ids;
    an id captured before a rematch equals the id after it; deleting a game and creating
    another never reissues the deleted id.
    *Unchanged by the timestamps:* ordering is derived from requirement 21's `updatedAt`,
    with `createdAt` as requirement 29's tiebreaker, and never from the id. The ban on
    deriving order from `GameId` still stands, and requirement 29 records what it costs —
    there is no third sort key available when both timestamps tie.

23. **Open games live in one Hive box named `open_games`, keyed by the id string, valued as
    JSON.** The key is `GameId.value`; the value is the `Map<String, dynamic>` produced by
    `StoredGame.toJson()`. One box, one entry per open game, no adapters (requirement 12).
    *Testable:* after two creates, the `open_games` box has two entries whose keys are the
    two `GameId` strings and whose values are JSON maps, **each carrying both timestamp
    fields** — a record round-tripped through the box comes back with `createdAt` and
    `updatedAt` equal to what was written, neither dropped nor collapsed into the other, and
    each stored as the **ISO-8601 UTC string** requirement 21 specifies: a value ending in
    `Z` that `DateTime.parse` returns to an equal instant. Changing the device timezone
    between a write and a read changes neither the stored string nor requirement 29's order.

24. **The five `shared_preferences` keys are exactly these strings:**

    | Preference | Key | Type |
    |---|---|---|
    | Selected theme | `ttt.pref.selectedThemeUuid` | `String` |
    | Music | `ttt.pref.musicEnabled` | `bool` |
    | Sound effects | `ttt.pref.soundEffectsEnabled` | `bool` |
    | Vibrate on touch | `ttt.pref.vibrateOnTouchEnabled` | `bool` |
    | Animations | `ttt.pref.animationsEnabled` | `bool` |

    Namespaced so requirement 5's check — that the preference store holds these five and
    nothing else — is mechanical rather than a judgement call.
    *Testable:* each key string appears exactly once in `lib/storage/`, and a store written
    through `PreferencesRepository` contains no key outside this table.

25. **`create` reports a refusal at the cap as a value, not an exception.** *(Ratified. The
    player-facing response to a `CapReached` is `P4-02-open-games-list.md`'s and is still
    unsettled — see Open Questions 3 — but the contract itself is settled.)*

    ```dart
    // lib/storage/create_game_result.dart
    sealed class CreateGameResult {}

    final class GameCreated implements CreateGameResult {
      const GameCreated(this.game);
      final StoredGame game;
    }

    final class CapReached implements CreateGameResult {
      const CapReached({required this.cap, required this.stored});
      final int cap;     // the effective ceiling, from P1-07
      final int stored;  // how many are held right now
    }
    ```

    Reaching the cap is an ordinary, player-reachable condition, not an error, so it is not
    an exception. A `bool` would force `P4-02` to re-query the cap to say anything useful,
    and a `void` would leave it unable to branch at all — which is why an earlier draft's
    claim that the storage half was "fixed either way" was false precision. `cap` and
    `stored` are carried so the list can render "3 of 3" without a second round trip,
    whichever response Open Questions 3 settles on.
    *Testable:* at the ceiling, `create` returns `CapReached` with `cap` equal to the
    entitlement layer's value and `stored` equal to `readAll().length`, and no record is
    added; below it, `create` returns `GameCreated` carrying a record whose `GameId` is new
    and **whose `createdAt` and `updatedAt` are both set rather than left null** — both UTC
    per requirement 21, and, on a freshly created record, equal to each other, since nothing
    has saved it yet.

### Resolved settings providers

> **A deliberate widening of this PRD's boundary, stated plainly.** This is a storage PRD
> declaring state-layer providers. The alternative is that each of `P2-02-audio.md`,
> `P2-03-haptics.md` and `P4-04-settings.md` resolves the same `null`-to-default itself —
> three copies of one rule, which is precisely what produced the gap these requirements
> close: `P2-03` req 14 publishes normative Dart reading `vibrateOnTouchEnabledProvider`
> and deliberately does not declare it, because declaring it would make a haptics layer the
> owner of a first-launch default. Its req 11 then bars itself from resolving the `null` at
> all. `P2-02` req 5 has the same shape for sound.
>
> **Why here rather than elsewhere.** The owner must (a) know the keys and the reads, (b)
> be able to cite the default rather than invent it, and (c) exist in **wave 1**, because
> both consumers ship in wave 2. `P4-04-settings.md` draws the switches but lands in wave 4
> — too late, and it owns presentation rather than value. No other wave-1 PRD touches these
> values. If a dedicated settings-state PRD is ever created, these three requirements move
> there wholesale; until then, leaving them unowned is the worse option, and that is the
> judgement being recorded.

26. **Four settings providers are declared here, each a synchronously readable
    `Provider<bool>`, and each resolves "nothing stored" to `true` — the fresh-install
    default — in this one place.**
    *Source: `Menus and UI.md` → Decisions → What are the settings on a fresh install?
    (every toggle defaults to on before the player has opened Settings); `Theming.md` →
    Decisions → Do all four toggles ship, and is music a theme concern? — "**Yes — all four
    toggles ship (Music, Sound Effects, Vibrate on Touch, Animations), and music belongs to
    the theme**", which settles that there are four and not three.*

    ```dart
    // lib/state/settings_providers.dart

    /// The four global player settings, resolved — never null.
    final class Settings {
      const Settings({
        required this.music,
        required this.soundEffects,
        required this.vibrateOnTouch,
        required this.animations,
      });

      /// The fresh-install state: all four on.
      /// Menus and UI → Decisions → What are the settings on a fresh install?
      static const defaults = Settings(
        music: true,
        soundEffects: true,
        vibrateOnTouch: true,
        animations: true,
      );

      final bool music;
      final bool soundEffects;
      final bool vibrateOnTouch;
      final bool animations;

      Settings copyWith({
        bool? music,
        bool? soundEffects,
        bool? vibrateOnTouch,
        bool? animations,
      }) =>
          Settings(
            music: music ?? this.music,
            soundEffects: soundEffects ?? this.soundEffects,
            vibrateOnTouch: vibrateOnTouch ?? this.vibrateOnTouch,
            animations: animations ?? this.animations,
          );
    }

    /// Holds the resolved settings. Seeded from PreferencesRepository once, off the
    /// tap path — requirement 27. The only writer of the four toggle preferences.
    final class SettingsNotifier extends Notifier<Settings> {
      @override
      Settings build() {
        unawaited(_seed());          // requirement 27
        return Settings.defaults;    // what reads see until the seed lands
      }

      Future<void> _seed() async {
        final repo = ref.read(preferencesRepositoryProvider);
        final music = await repo.readMusicEnabled();
        final sound = await repo.readSoundEffectsEnabled();
        final vibrate = await repo.readVibrateOnTouchEnabled();
        final animations = await repo.readAnimationsEnabled();
        state = Settings(
          music: music ?? Settings.defaults.music,
          soundEffects: sound ?? Settings.defaults.soundEffects,
          vibrateOnTouch: vibrate ?? Settings.defaults.vibrateOnTouch,
          animations: animations ?? Settings.defaults.animations,
        );
      }

      Future<void> setMusic(bool value) async {
        state = state.copyWith(music: value);
        await ref.read(preferencesRepositoryProvider).writeMusicEnabled(value);
      }

      Future<void> setSoundEffects(bool value) async {
        state = state.copyWith(soundEffects: value);
        await ref.read(preferencesRepositoryProvider).writeSoundEffectsEnabled(value);
      }

      Future<void> setVibrateOnTouch(bool value) async {
        state = state.copyWith(vibrateOnTouch: value);
        await ref.read(preferencesRepositoryProvider).writeVibrateOnTouchEnabled(value);
      }

      Future<void> setAnimations(bool value) async {
        state = state.copyWith(animations: value);
        await ref.read(preferencesRepositoryProvider).writeAnimationsEnabled(value);
      }
    }

    final settingsProvider =
        NotifierProvider<SettingsNotifier, Settings>(SettingsNotifier.new);

    /// The four read points. Plain synchronous bools — read at fire time.
    final musicEnabledProvider =
        Provider<bool>((ref) => ref.watch(settingsProvider).music);
    final soundEffectsEnabledProvider =
        Provider<bool>((ref) => ref.watch(settingsProvider).soundEffects);
    final vibrateOnTouchEnabledProvider =
        Provider<bool>((ref) => ref.watch(settingsProvider).vibrateOnTouch);
    final animationsEnabledProvider =
        Provider<bool>((ref) => ref.watch(settingsProvider).animations);
    ```

    **`bool`, not `AsyncValue<bool>`.** Both consumers read on a tap path and cannot await:
    `P2-03` req 14's `hapticServiceProvider` calls `ref.read(vibrateOnTouchEnabledProvider)`
    inside a synchronous, fire-and-forget `validAction()`, and `P2-02` req 5 reads at each
    of five sound moments. An `AsyncValue` would push a loading branch into every one of
    them, and each branch would need a fallback — which is the same default, copied again.
    **Plain `Provider` over a `NotifierProvider`,** matching `P2-03` req 14's own reasoning:
    the *setting* is the state and lives in `settingsProvider`; the four exported symbols
    are read points over it. No `@riverpod`, no `StateNotifier` — `P1-01-app-scaffold.md`
    req 12.
    **`musicEnabledProvider` ships with no consumer, and that is expected.** `Theming.md`
    makes music a theme concern and the user has since settled its key shape — a single
    app-wide `sound.music` (`P1-03-theme-system.md` req 17) — but nothing plays it yet:
    `P2-02-audio.md` owns one-shot effects and its `SoundMoment` enum has no music member,
    and no theme file carries music audio. The setting is persisted and readable from the
    moment this PRD lands, and whichever PRD eventually plays music reads this provider
    rather than declaring its own — which is the whole point of resolving the default once.
    Until then it is a stored, testable value with no reader.
    *Testable:* with an empty store, all four providers read `true`; with
    `ttt.pref.soundEffectsEnabled` stored `false` and the seed complete,
    `soundEffectsEnabledProvider` reads `false` while the other three read `true`; a scan
    finds the literal default in `Settings.defaults` and nowhere else in `lib/`.

27. **The providers are seeded once, off the tap path, and a write updates them
    immediately.**

    **Seeding.** `SettingsNotifier.build()` returns `Settings.defaults` synchronously and
    starts one asynchronous read per preference. When those land, `state` is replaced and
    every watcher rebuilds. No consumer awaits anything, and no read happens per tap.

    **Before the seed lands, reads return the defaults** — all four on. Because the
    fresh-install default *is* all-on, this pre-seed state is **correct rather than merely
    tolerable** for a first-run player: the value a first-run player should see is exactly
    the value shown while the store is being read.
    ⚠ *Flagged, with a named mitigation:* for a returning player who turned something
    **off**, there is a window between first frame and seed completion in which the provider
    reports `true` — one tap in that window could buzz or sound when it should not. The
    mitigation is to await the seed during app bootstrap before the first frame, which is
    `P1-01-app-scaffold.md`'s `main.dart` territory rather than this PRD's; it is named here
    so it is a known cost rather than a surprise. It is not a correctness problem for a
    fresh install, only for a returning player in the first frames. Music makes this
    slightly more visible if music ever autostarts on launch — a returning player who muted
    it would hear a moment of it — which is another reason to await the seed in bootstrap.

    **Writes.** `SettingsNotifier`'s four setters are the **only** write path for these
    preferences: each updates `state` first, then persists through `PreferencesRepository`.
    A caller that writes to the repository directly bypasses the provider and leaves the two
    out of step — so `P4-04-settings.md`'s switches call the setters, not the repository.
    This is what makes `P2-03` req 12 hold: a vibrate toggle flipped in in-game quick
    actions governs the very next tap, because the next `ref.read` sees the new `state`
    without waiting for the write to complete.
    *Testable:* with a fake `PreferencesRepository`, calling `setVibrateOnTouch(false)`
    makes `vibrateOnTouchEnabledProvider` read `false` on the next read within the same
    frame, and the repository records exactly one write; with the fake's read delayed, reads
    before completion return the defaults and reads after return the stored values.

### The storage providers

> Same reasoning as requirements 26–27, one layer down, and routed here by
> `P4-02-open-games-list.md` req 21, which marks both symbols **"Declared by: nobody"** and
> states its screen does not compile until someone does. `P1-03-theme-system.md` req 24
> closed the identical gap for the theme by declaring `activeThemeProvider` in
> `lib/theme/theme_providers.dart`. A storage provider declared in a UI PRD would be the
> alternative, and it is worse: the fake used to override it in tests, and the layer that
> owns its lifetime, both live here.

28. **The repositories are reached only through these providers, and the open-games list is
    watchable.**

    ```dart
    // lib/storage/storage_providers.dart

    /// The three repositories. Each is overridden with an in-memory fake in tests —
    /// requirement 13 — so no test needs Hive or shared_preferences initialized.
    final Provider<OpenGamesRepository> openGamesRepositoryProvider;
    final Provider<PreferencesRepository> preferencesRepositoryProvider;
    final Provider<EntitlementsStore> entitlementsStoreProvider;

    /// The open-games list, and the mutation path that keeps it fresh.
    /// build() delegates to readAll(); every mutation refreshes the list before
    /// returning, so no caller has to remember to invalidate.
    final class OpenGamesNotifier extends AsyncNotifier<List<StoredGame>> {
      @override
      Future<List<StoredGame>> build() =>
          ref.watch(openGamesRepositoryProvider).readAll();

      Future<CreateGameResult> create({
        required String opponentName,
        required Board board,
      }) async {
        final result = await ref
            .read(openGamesRepositoryProvider)
            .create(opponentName: opponentName, board: board);
        if (result is GameCreated) ref.invalidateSelf();
        return result;                       // CapReached leaves the list untouched
      }

      Future<void> save(StoredGame game) async {
        await ref.read(openGamesRepositoryProvider).save(game);
        ref.invalidateSelf();
      }

      Future<void> delete(GameId id) async {
        await ref.read(openGamesRepositoryProvider).delete(id);
        ref.invalidateSelf();
      }
    }

    final openGamesListProvider =
        AsyncNotifierProvider<OpenGamesNotifier, List<StoredGame>>(OpenGamesNotifier.new);
    ```

    **`ref.watch(openGamesListProvider)` yields `AsyncValue<List<StoredGame>>`** — exactly
    the type `P4-02` req 25 requires, because `readAll()` is `Future`-returning.
    **Refresh is structural, not a rule to remember.** `P4-02` req 25 requires the list to
    re-read "after a successful `create` and after a `delete`". Putting the mutations on the
    notifier means the refresh cannot be forgotten — the alternative, callers invoking
    `ref.invalidate(openGamesListProvider)` after each write, is precisely the
    remember-to-do-it shape that produced the gaps requirements 26 and 28 exist to close.
    A `CapReached` deliberately does not invalidate: nothing changed.
    **Widgets `watch`; services `read` at use time** — matching `P1-03-theme-system.md`
    req 24's rule so the three layers agree. `P4-02`'s list screen watches
    `openGamesListProvider`; `P2-01-navigation.md` req 4 and the move-commit path `read`
    `openGamesRepositoryProvider` (or the notifier, for writes that must refresh the list)
    inside the call that needs it, never captured in a constructor.
    **Which symbol a caller wants:** `openGamesListProvider` for the rows and for any write
    that should be visible in the list; `openGamesRepositoryProvider` for a read or write
    with no list on screen — the move-commit save in a game, for instance, where invalidating
    a list nobody is watching is wasted work.
    *Correction routed to `P4-02-open-games-list.md`:* its req 21 table maps `create(...)`
    and `delete(id)` onto `openGamesRepositoryProvider`. Those two calls should go through
    `openGamesListProvider.notifier` so the list refreshes structurally — a one-line change
    to that table, flagged rather than silently diverged from. The `Declared by` column for
    both rows is this requirement.
    *Testable:* a widget test overriding `openGamesRepositoryProvider` with an in-memory
    fake drives create, delete and the rows with no Hive; after
    `openGamesListProvider.notifier.delete(id)` completes, a widget watching
    `openGamesListProvider` rebuilds with one fewer row and no navigation round trip; after
    a `CapReached`, it does not rebuild.

29. **`readAll()` returns a stable order: sorted on `updatedAt`, most-recent-first, with
    `createdAt` as the tiebreaker — not on the box's iteration order, never on `GameId`,
    and not on `createdAt` as the primary key.** The order is
    deterministic: the same stored set produces the same sequence on every read and across
    relaunches, so the player's list does not reshuffle behind them.
    *Source: the user's answers to Open Questions 7 and 8. OQ 7 settled that `StoredGame`
    carries a timestamp — taken together with this requirement's own pre-committed
    consequence, which said that if the answer landed on "add the field", *"this requirement
    is replaced by an ordering guarantee and requirement 21's `StoredGame` gains one line;
    nothing else in this PRD changes."* **OQ 8 then settled the comparator**: the field is
    `updatedAt` and the direction is **most-recent-first**. Both halves are the user's, not
    this PRD's proposal.*

    **The comparator, stated completely, because a one-key version is not deterministic.**
    Order by `updatedAt` **descending**; where two records carry the same `updatedAt`, order
    by `createdAt` **descending**. The second key is not decoration:
    - **Equal `updatedAt` values are reachable.** Requirement 25 makes `createdAt` and
      `updatedAt` equal on a freshly created record, so two games created before either is
      played can carry the same `updatedAt` — the more so where the platform clock is
      coarse.
    - **Dart's `List.sort` is documented as *not stable*.** With one key, tied records fall
      back to whatever order the box iterated them in — which is exactly the Hive
      box-iteration non-determinism this requirement exists to eliminate, reintroduced
      through the back door.
    - **`createdAt` is the only other key available.** It is already on the record
      (requirement 21) and is the only other time-carrying field; requirement 22 forbids the
      obvious third choice by making `GameId` opaque and explicitly non-ordering.
    *[The tiebreaker is this PRD completing the comparator the user settled, not a second
    decision about sort order: it is unobservable except where the settled key ties.]*
    *Residual, recorded rather than papered over:* two records equal on **both** fields would
    fall back to `List.sort`'s unspecified order. Reaching that means two stamps landing on
    the same `DateTime.now().toUtc()` instant — microsecond resolution, each behind a
    distinct player action — so it is not reachable in practice, and requirement 22 leaves no
    third key that could break it.

    *What this replaces, recorded because three PRDs fenced against it:* until an earlier
    revision this requirement stated that `readAll()` carried **no** ordering guarantee, and
    named the concrete cost — in practice Hive box-iteration order, which is **not stable
    across compaction**, so the failure mode was the player's list silently reshuffling
    between launches rather than a failing suite. `updatedAt` is the sort key that fixes it.
    `P4-02-open-games-list.md` req 2 and its Open Question 6 fenced against the absence and
    now cite this instead.
    *Requirement 22 still forbids deriving order from `GameId`*, and nothing here changes
    that: the id is opaque and carries no time information.
    *Why `updatedAt` and not `createdAt`, recorded rather than re-derived:* `createdAt`
    exists on the record (requirement 21) and would produce a different, equally stable
    order. The user settled this one. The evidence that pointed the same way is the list
    screen's own heading — *"Pick up where you left off"* (`P4-02-open-games-list.md`
    req 24, transcribed from the handoff's `1b`) — which is about recency rather than
    creation. Carrying both fields is what keeps that a **display** choice: a later decision
    to show or sort by creation order needs no schema change and no Open Questions 1
    migration.
    *One player-visible consequence of requirement 21's stamping rule, named here because
    this is where the order lives:* any `save` moves its record to index 0, **including a
    save that is not a move** — taking a rematch (`P3-04-game-over-rematch.md` req 9) puts
    that series at the top of the list before a mark is placed in the new game.
    *Testable:* two consecutive `readAll()` calls with no intervening mutation return the
    same order; a store rebuilt from disk returns the same order as before the rebuild;
    given three records with distinct `updatedAt` values, `readAll()` returns them newest
    first — index 0 is the largest `updatedAt` — and a `save` that advances one record's
    `updatedAt` moves it to index 0 on the next read; **given two records created in the
    same session and never played, so their `updatedAt` values collide, `readAll()` returns
    the newest-created first and returns the same order on every repeat read and across a
    store rebuilt from disk**; no consumer file sorts on `GameId`, and no consumer file
    re-sorts the list at all.

## Out of Scope

- **The domain models themselves** — `Board`, `Move`, their fields and their `freezed` /
  `json_serializable` definitions: `P1-02-engine-rules.md` (its reqs 29–31). This PRD
  serializes them and defines none of them. The two timestamps requirement 21 adds are
  **not** among them: they are storage's own fields, like the id and the opponent name, and
  no design doc puts either in game state.
- **Who calls save.** This PRD owns the repository and states the obligation (requirement
  6). It does not own the call sites. **Timing is settled and every write row now has an
  owner** — the last two were claimed in wave 3, by `P3-02-move-input.md` req 36 and
  `P3-04-game-over-rematch.md` req 9. Modelled on `P2-02-audio.md`'s call-site table, which
  does the same for playback:

  **Writes**

  | Write | When | Call-site owner |
  |---|---|---|
  | After a confirmed move | Settled — `Menus and UI.md` → Decisions → When is a game written to storage? | **`P3-02-move-input.md` req 36**, on the commit path its req 4 defines; fire-and-forget, not awaited |
  | At game end, carrying the increment | Same write — the game-ending move is a confirmed move | **Same owner, `P3-02-move-input.md` req 36**; `P3-04-game-over-rematch.md` req 9(a) asserts the same write from the storage side |
  | On taking a rematch | Not a move; needs its own write or the next confirmed move covers it | **`P3-04-game-over-rematch.md` req 9**, which claims it rather than letting the next move cover it. What that write does to `updatedAt` is not a caller's choice: requirement 21 has `save` stamp it |
  | On leaving a game to the main menu | No write needed — requirement 11 | n/a |
  | On creating a new game | On confirm in the name prompt | `P4-02-open-games-list.md` req 10, via requirement 28's notifier |
  | On deleting a game | On the delete action | `P4-02-open-games-list.md` req 7, via requirement 28's notifier |
  | On changing a settings toggle | On the switch | `P4-04-settings.md`, via requirement 27's setters |

  **Reads — because a write-only table is how the read owner went unnamed for so long.**
  This layer publishes `readById` and `readAll` and calls neither; a reviewer noted that the
  table's write-only shape hid the fact that nothing named who resumes a game.

  | Read | When | Call-site owner |
  |---|---|---|
  | Resuming a stored game into the game screen — `readById`, then seeding `boardProvider` and `currentGameProvider` | In `GameScreen.initState`, once per `GameId`, before the board is rendered | **`P3-01-board-rendering.md` req 54.** The two providers are `P3-02-move-input.md`'s reqs 29 and 35; what the screen does when the read returns null or throws is that requirement's, not this PRD's |
  | Listing open games | On the open-games screen | `P4-02-open-games-list.md` reqs 5, 21 and 25, via requirement 28's `openGamesListProvider` |

  **What the two closures changed here.** Requirement 6's *"Testable, but not here"* now has
  a home — `P3-02` req 36 carries the assertion that a confirmed move reaches storage — and
  the rematch row's smaller gap (a rematch resets the board without being a move, so either
  it writes or the state on disk lags by a game) is closed by `P3-04` req 9 choosing to
  write. Naming the gaps was this PRD's job; filling them was theirs.
- **The settings screen, its switches, and where they are reachable from** —
  `P4-04-settings.md`. Requirement 26 owns the *value* and requirement 27 the write path;
  that PRD owns the surface and calls the setters. It now draws four rows, not three.
- **Music itself** — the theme's music slot, where the audio comes from, and whether it
  loops. `Theming.md` → Decisions → Do all four toggles ship, and is music a theme concern?
  makes music a **theme** concern; the user has since settled the key's **shape** as a single
  app-wide `sound.music` (`P1-03-theme-system.md` req 17, which is where the slot lives), and
  playback is nobody's — `P2-02-audio.md`'s `SoundMoment` enum has no music member and its
  req 14 says it never will. This PRD persists the on/off preference and nothing else.
- **What "off" means for each channel** — silence, no buzz, instant state changes:
  `P2-02-audio.md`, `P2-03-haptics.md`, `P2-04-animations.md`. This PRD supplies the
  boolean and asserts nothing about behavior.
- **The open-games list UI** — the rows, the delete affordance, the empty state, what a
  player sees when `create` returns `CapReached`, and **whether a row displays either
  timestamp** requirement 21 now stores: `P4-02-open-games-list.md`. Requirement 28 supplies
  the data and the mutations; that PRD renders them and decides row content, and its Open
  Question 4a still holds the display half.
- **Incrementing the score.** The increment happens engine-side at game end
  (`P1-02-engine-rules.md` req 27); this layer writes whatever the engine produced.
- **The entitlement model** — what the entitlements are, the free-tier defaults, **both cap
  numbers**, the per-theme `free`/`owned`/`locked` query, the theme-UUID-to-product mapping,
  and the authority rule: `P1-07-entitlements.md`. Requirements 18–20 store and return
  values; they never define, translate or interpret one, and `lib/storage/` defines neither
  cap number.
- **Whether `P4-05-purchase-flow.md` writes through the entitlement layer or straight to
  this one** — `P1-07-entitlements.md` Open Question 4. Requirement 19 is written to hold
  either way.
- **Querying, purchasing and restoring** — StoreKit, `Transaction.currentEntitlements`,
  `AppStore.sync()`, the purchase flow and the paywall UI: `P4-05-purchase-flow.md`.
- **Theme loading, merging over Neon, materialization, and resolving the default theme when
  nothing is stored** — this layer stores an opaque UUID string: `P1-03-theme-system.md`.
  Labelling which themes are free or paid is `P1-07-entitlements.md`'s (the state) and
  `P4-03-theme-selection.md`'s (the rendering).
- **Creating the `lib/` tree** — `main.dart`, `app.dart` and the layer directories including
  `storage/` and `state/`: `P1-01-app-scaffold.md` req 2. Awaiting the settings seed before
  the first frame, if that is wanted, is that PRD's `main.dart` too — see requirement 27.
  **Declaring the Hive packages** is also its req 14's: `hive_ce` + `hive_ce_flutter`,
  settled by the user.
- **Any backend, sync, or network storage.** Multiplayer is named as a direction that must
  not be foreclosed (`Tech Design.md` → Decisions → Online multiplayer is an intended
  future direction), not as work now.

## Open Questions

### 1. Persisted data — versioning

As worded in `Tech Design.md` → Open Questions → 1. Persisted data — versioning:

> When the shape of stored data changes — a fifth preference is added, a key is renamed,
> an open game gains a field — what happens to data already on the device? A game
> written by v1.0 has to still load in v1.1.

*Note that the doc's own example just happened, twice:* a fifth preference **was** added
(music, requirement 24), and an open game **has** gained fields (the two timestamps,
requirement 21) — both before any device holds data, so both cost nothing this time. That is
the cheap case, and it will not stay cheap.
*Consequence of shipping without an answer — moved here from an Out of Scope bullet that was
deciding it by omission:* this PRD designs no migration hook and no schema-version field, so
**v1.0 data ships unversioned** — the `open_games` box holds bare `StoredGame` JSON and the
five preference keys hold bare values. Any scheme adopted later therefore has to treat
*absence of a version* as meaning v1 rather than meaning corrupt. That is a real constraint
on the answer, not a decision this PRD is entitled to make. Adding a version field now,
before any device holds data, is cheaper than inferring one later — and the timestamps landed
in this wave, which was the natural moment to add both, so that moment is the one now
passing.

### 2. Does leaving a game still need a confirmation prompt?

As worded in `Menus and UI.md` → Leaving a game mid-play: "Whether leaving still needs a
confirmation prompt is undecided; the original reason for one ('Leave game? Your score
will be lost') no longer applies." Requirement 6's save timing weakens the case further —
with every confirmed move already written, leaving costs nothing at all.

### 3. What does New Game do when the player is at the cap? (author-raised)

**Narrowed.** What is settled:

- **Both ceilings** — 3 by default, 100 with the $4.99 unlock. *(`Menus and UI.md` →
  Decisions → How many open games do we keep?; the values are `P1-07-entitlements.md`
  req 3's.)*
- **A slot is freed by an explicit, player-initiated delete.** *(`Menus and UI.md` →
  Decisions → Deleting an open game; requirement 17.)*
- **Replace-the-oldest is ruled out.** `P4-02-open-games-list.md` req 7 records it as
  considered and rejected — "Nothing in this feature deletes a game the player did not
  choose to delete."
- **The storage-side contract** — `create` returns `CapReached { cap, stored }`
  (requirement 25, ratified), so whatever the answer, the caller can branch and can name
  the numbers.

**Still open:** what the New Game action *does* with that result — refuse and say the list
is full, route the player into the delete flow, offer the $4.99 unlock at the moment the
limit bites, or a combination. `P4-02-open-games-list.md` carries the same question from the
UI side. This changes the caller's response, not this layer's behavior.

### 4. Gaps an implementer would otherwise have to guess (author-raised)

- **Whether the pending (selected-but-unconfirmed) move survives a restart.** Moves are two
  taps, select then confirm (`Game Overview.md` → How a Move Is Made). Requirement 6 now
  settles that the write happens on *confirm*, which strongly implies a pending selection is
  not persisted — but implication is not a decision, and the only explicit statement is in
  the handoff's *State* sketch, which `Tech Design.md` records as "a design sketch, not a
  decision taken here." Distinct from the *completed* last move, which requirement 7 does
  persist.
- **What `save` does with a `GameId` that has no stored record.** Arrived with the stamping
  settlement: requirement 21 has `save` **preserve the stored `createdAt`**, which presumes
  there is one to preserve. `create` is the only minter of a `GameId` (requirement 22) and
  every call site saves a record it read back, so nothing in the app reaches this today —
  but the contract does not say whether such a `save` inserts the record (and with what
  `createdAt`), silently does nothing, or throws. Not reachable, not blocking, and cheap to
  settle now.

<!-- Closed since earlier drafts:
     - "How is an open-game slot ever freed" → requirement 17.
     - "Which layer owns preference access" → requirement 14; PreferencesRepository lives in
       lib/storage/.
     - "When is a save written" → ANSWERED. Menus and UI → Decisions → When is a game
       written to storage?: after every confirmed move. Now requirement 6's app-level claim.
       What remained was not a question but an unclaimed call site; P3-02 req 36 claims it —
       see Out of Scope.
     - "First-launch defaults for the toggles" → ANSWERED. Menus and UI → Decisions →
       What are the settings on a fresh install?: all default to on. Resolved in exactly one
       place, Settings.defaults, by requirement 26 — which also closes the undeclared-symbol
       gap that P2-02 req 5 and P2-03 req 14 were blocked on.
     - "Who declares openGamesRepositoryProvider / openGamesListProvider" → requirement 28.
     - "Are entitlements keyed by theme UUID or product id" → product identifiers,
       requirement 18. This PRD conceded; P1-07's representation stands. -->

### 5. Which store do entitlements belong in? (author-raised)

`Tech Design.md` → Decisions → *Entitlements — Apple stores them, no backend needed* settles
that Apple is the record of truth and that a local copy is "an offline convenience, not the
record." It does not say where that copy is written, and `P1-07-entitlements.md` → Open
Question 3 routes the decision here. Two candidates — the third, "nothing persisted,
re-queried at launch", is ruled out by that PRD's req 13, whose precedence chain requires a
local copy to fall back to:

- **`shared_preferences`, alongside the five preferences** — small, flat, already the home
  of app-level player state. **But it falsifies requirement 5's testable**, which asserts
  the preference store contains only the five keys in requirement 24. This branch costs that
  check, or costs rewording it to "the five preference keys plus entitlement keys" — which
  turns a mechanical scan into a judgement call. Whoever answers should know it is not free.
- **Hive** — already holds structured data, and a set of product identifiers is a growing
  collection rather than a single flag. Costs nothing stated, though `Tech Design.md` →
  Decisions → Game state storage — Hive frames Hive as where *game state* lives, so it
  stretches that wording. It would mean a second box beside `open_games` (requirement 23).

Also unsettled, and `P1-07-entitlements.md`'s to answer (its **Open Question 1**): what
happens to stored games above the free ceiling if an entitlement goes away. A player with 60
open games whose ceiling drops to 3 has 57 games requirement 10 declines to touch.
Requirement 10 is deliberately a create-time check so nothing is destroyed by default, but
that is a holding position, not the answer.

### 6a. The game id — specified here, not open

Recorded so the earlier open question is not read as still blocking: requirement 22 settles
the id's type, opacity, minting, stability and non-reuse. `P4-02-open-games-list.md` req 19,
`P2-01-navigation.md` req 3 and `P3-04-game-over-rematch.md` req 9 can be written against
`GameId` today. Nothing about that half needs the user.

### 6b. Is a game id ever visible to the player? (author-raised — needs the user)

The one half of the identity question that is not an engineering choice. Requirement 22 makes
the id opaque and undisplayed, which is the narrow reading. If two games are both titled
`ItSaMeMaRiO` — the default case, per `P4-02-open-games-list.md` req 9 — the player has no
way to tell the rows apart, and the fix could be a visible disambiguator (a number, a date, a
"last played" line) that would make some part of a game's identity player-facing. Whether
that is wanted, and what it shows, is `P4-02-open-games-list.md`'s to render and the user's
to decide. This PRD adds no field *for that purpose*; note that requirement 21 now stores
**two** dates, so either a "last played" line (`updatedAt`) or a "started on" line
(`createdAt`) is available if the answer is a date — which softens the question without
answering it. Displaying either field is `P4-02` → Open Question 4a's.

### 7. CLOSED — `StoredGame` gains a timestamp

**Answered by the user: yes.** This was the same question as `P4-02-open-games-list.md` →
Open Question 4 (its 4c half), reached from the storage side, and the two could not be
answered separately. It is a **wave-1 model change** and it is made here.

What it settles, in the terms this question was written in:

- **The field exists.** Requirement 21's `StoredGame` carries it; requirement 23's box
  values carry it; requirement 7 names it as part of the record. *(Open Questions 8 has
  since settled that it is two fields, not one.)*
- **List ordering.** Requirement 29 is now an ordering guarantee rather than an admission
  that there is none, and the Hive-compaction reshuffle it warned about is fixed.
  `P4-02` → Open Question 6 can cite requirement 29 instead of fencing against its absence.
- **Duplicate titles.** A stored date incidentally serves OQ 6b above if the answer there is
  a "last played" line — without making the id itself visible.

**What it did not settle, and where that went:**

- **Whether the player ever sees it.** `P4-02` req 4 fences the row's relative timestamp out
  of this wave; its **Open Question 4a** holds the display half, and this answer does not
  touch it. "Storing it and not displaying it" is exactly the coherent middle this question
  described, and it is where the PRDs now sit.
- **The field's name and semantics, and the sort direction** — Open Questions 8, which the
  user has now closed.

### 8. CLOSED — both `createdAt` and `updatedAt`, sorted most-recent-first on `updatedAt`

**Answered by the user, both halves.** Answering 7 settled *that* `StoredGame` carries a
timestamp; this question held what it is called, when it is written, and which end of the
list the newest game sits at. Kept as a numbered stub because requirements 21, 22, 23, 25 and
29, and `P4-02-open-games-list.md`'s requirements 2 and 4 and its Open Questions 4a/4c/6, all
cite this number.

- **The record carries both fields, not one or the other.** `createdAt` is written once, at
  creation, and never changes; `updatedAt` is written on every `save`. Requirement 6 already
  saves after every confirmed move, so keeping `updatedAt` current is free.
  **The user's stated reason for carrying both:** it leaves the sort key a **display** choice
  rather than a **schema** one. Either order can be offered later without touching stored
  data — which matters because Open Questions 1 ships v1.0 unversioned, so a field added
  after devices hold data is the expensive case.
- **The list sorts most-recent-first, on `updatedAt`.** This PRD's proposal is confirmed.
  Requirement 29's comparator is settled, not proposed, and the evidence that pointed at it —
  the list screen's heading *"Pick up where you left off"* (`P4-02` req 24) — is now
  corroboration rather than the basis.
- **Whether either field is player-visible is still open**, and it is not this PRD's:
  `P4-02` → Open Question 4a. Named here only so the display half is not read as closed by
  this answer.

**The consequence this question handed forward is now answered too: `save` stamps.** A
rematch writes the same record (requirement 8), so it plainly keeps its `createdAt`; whether
that write carried the **stale `updatedAt`** or **stamped now** was recorded as an open
question on `P3-04-game-over-rematch.md` req 9, the first caller that would have had to
choose. **The user has settled it one level down, which removes the choice rather than making
it:** `OpenGamesRepository.save` **stamps `updatedAt` itself, ignoring whatever the caller
passes**, and **preserves the stored `createdAt`**, discarding an incoming one — requirement
21, with the reasoning recorded there.

Two consequences, both recorded rather than re-derived:

- **A rematch save stamps, so a rematched series jumps to the top of requirement 29's
  most-recent-first list** before a move is played in the new game. That is player-visible,
  and it is now a property of the storage layer rather than of the caller.
  `P3-04-game-over-rematch.md` → Open Question 10 is **closed as answered** by this
  settlement, and its req 9 states the effect.
- **`createdAt` is immutable in fact, not only by convention.** A caller can construct a
  `StoredGame` with any `createdAt` it likes — the constructor takes one — and `save`
  discards it. Nothing else in this layer could have enforced that.
