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
> whether a game id is ever player-visible (OQ 6b), persisted-data versioning (OQ 1), and
> whether `StoredGame` gains a timestamp — which is one answer with `P4-02`'s OQ 4 and
> settles list ordering too (requirement 29, OQ 7). One cross-PRD gap: the save trigger is
> settled in timing but **no requirement in `P3-02-move-input.md` yet claims the call**
> (Out of Scope → *Who calls save*). One flagged risk with a named mitigation: the settings
> seed window (requirement 27). One provider ships with no consumer yet, by design:
> `musicEnabledProvider` (requirement 26).

**Wave:** P1 — ships in the first wave, parallel-safe with the other P1 PRDs.

**Dependencies:**

- `P1-01-app-scaffold.md` creates the `lib/storage/` and `lib/state/` directories this PRD
  fills, as part of the layer-first tree (its req 2), states the `engine/`-purity rules from
  the scaffold side (its reqs 4–5), and fixes the no-codegen Riverpod idiom requirements 26
  and 28 follow (its req 12). Same wave.
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
  every confirmed move — see requirement 6 and Out of Scope → *Who calls save*. Wave 3.
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
survives a restart, a watchable open-games list that refreshes itself after every write, and
four synchronously-readable settings providers that resolve the first-launch default in
exactly one place. A player can quit mid-move — or lose the app to a force-quit — relaunch,
pick the same game out of the open-games list, and find the board, the last move played,
whose turn it is, and the series scoreboard exactly as they left them, because every
confirmed move was written as it happened. Meanwhile `engine/` stays pure Dart and no caller
outside `storage/` knows Hive exists.

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

   **App level (settled, owned elsewhere):** a game is written to storage **after every
   confirmed move**, so nothing is lost to a crash or a force-quit. The write happens on
   the move-commit path, not on leaving the game.
   *Source: `Menus and UI.md` → Decisions → When is a game written to storage? — "**After
   every confirmed move.** Nothing is ever lost to a crash or a force-quit," with the
   reasoning that each write is a single small record, the game is turn-based so writes are
   infrequent, and a game is saved specifically so it can be resumed.*
   *Testable, but not here:* the assertion that a confirmed move reaches storage belongs to
   whichever requirement claims the call site. Today none does — the commit path is
   `P3-02-move-input.md` req 4 and it does not mention persistence. See Out of Scope →
   *Who calls save*. This PRD states the obligation and names the gap; it cannot close it
   from inside a wave-1 file.

7. **A stored open game carries a whole series, not one board's worth of cells.** What a
   stored record holds: the `Board` — which per `P1-02-engine-rules.md` req 29 already
   carries the cells, quadrant states, active quadrant, current player, **the most recent
   completed move**, the outcome, the series score and who went first — plus this layer's
   own record id and the opponent name the game is titled with in the open-games list.
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
   *What it does **not** carry:* any timestamp. See requirement 29 and Open Questions 7.

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
    `hive` or `hive_flutter`, and callers depend on the interfaces in requirement 21 —
    reached through the providers in requirement 28 — not on their implementations.
    *Source: `Tech Design.md` → Decisions → Serialization and the storage layer ("who is
    allowed to know it is Hive").*
    *Testable:* an import scan over `lib/` outside `lib/storage/` finds no `hive` import;
    every provider in requirement 28 can be overridden with an in-memory fake in tests with
    no Hive initialized.

14. **All persistence access lives in `lib/storage/`, and `engine/` imports nothing
    Flutter-dependent — specifically not `hive_flutter` and not `shared_preferences`.**
    Both stores are reached only through requirement 21's interfaces. The providers in
    requirement 26 live in `lib/state/` and reach storage the same way every other consumer
    does — through `PreferencesRepository` — so no persistence package is imported outside
    `lib/storage/`.
    *Source: `Tech Design.md` → Decisions → Serialization and the storage layer
    ("`hive_flutter` is not pure Dart, so it must never be imported from `engine/`"); →
    Is the game logic separate from Flutter? ("pure Dart with zero Flutter imports"); →
    Project structure — layer-first, which places local persistence in `storage/` and
    Riverpod providers in `state/`. Stated from the scaffold side as
    `P1-01-app-scaffold.md` reqs 4–5.*
    *Testable:* an import scan finds `shared_preferences` and `hive_flutter` imported only
    under `lib/storage/`, and zero Flutter-dependent imports under `lib/engine/`.

15. **Serialization lives with the model: `storage/` persists what the models' generated
    `toJson` produces and reconstructs through `fromJson`.** `storage/` writes no
    hand-rolled encoding of its own.
    *Source: `Tech Design.md` → Decisions → Serialization and the storage layer
    ("`toJson`/`fromJson` are generated into `engine/` by json_serializable ... while the
    Hive box, adapters-free, lives in `storage/`").*
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
> normative: these are the names and signatures they may code against. Nothing here is
> provisional — the aggregate type is `Board` per `P1-02-engine-rules.md` req 29, and
> `CreateGameResult` (requirement 25) is ratified.

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
      });
      final GameId id;
      final String opponentName;
      final Board board;
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
    **The opponent name and the id are storage's**, not the engine's — no design doc puts
    either in game state — so they sit on `StoredGame` alongside the `Board`.
    **`StoredGame` carries no timestamp** — see requirement 29 and Open Questions 7.

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

23. **Open games live in one Hive box named `open_games`, keyed by the id string, valued as
    JSON.** The key is `GameId.value`; the value is the `Map<String, dynamic>` produced by
    `StoredGame.toJson()`. One box, one entry per open game, no adapters (requirement 12).
    *Testable:* after two creates, the `open_games` box has two entries whose keys are the
    two `GameId` strings and whose values are JSON maps.

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
    added; below it, `create` returns `GameCreated` carrying a record whose `GameId` is new.

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
    now makes music a theme concern, but nothing plays it yet: `P2-02-audio.md` owns
    one-shot effects and its `SoundMoment` enum has no music member, and no theme file
    carries music audio. The setting is persisted and readable from the moment this PRD
    lands, and whichever PRD eventually plays music reads this provider rather than
    declaring its own — which is the whole point of resolving the default once. Until then
    it is a stored, testable value with no reader.
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

29. **`readAll()` carries no ordering guarantee, and consumers must not assume one.** The
    order is whatever the box yields. It is **not** creation order, **not** recency order,
    and requirement 22 forbids deriving one from `GameId`.
    *Why this is stated rather than left silent:* `P4-02-open-games-list.md` req 2
    previously fenced its row order against "creation order, i.e. the order `readAll()`
    returns (`P1-04` req 21)" — a guarantee this PRD has never made. It has since corrected
    itself. Saying so explicitly is what stops the next consumer fencing against the same
    phantom.
    *The concrete cost, named:* in practice this is Hive box-iteration order, which is
    **not stable across compaction**. No test asserts order, so the failure mode is the
    player's list silently reshuffling between launches rather than a failing suite. That is
    a real defect and this PRD is not fixing it, because the fix is a field decision that is
    not this PRD's to make alone — see below.
    *One field settles three things.* A stored `updatedAt` (or `createdAt`) on `StoredGame`
    would give: a stable sort key, a meaningful order for the list, and the relative
    timestamp `1b` draws on each row. `P4-02` → Open Question 4 asks the product half —
    what a row shows — and its Open Question 6 asks for recency ordering; both need the
    same field, and adding it is a **wave-1 model change here**, not a wave-4 widget change.
    *Testable as written:* two consecutive `readAll()` calls with no intervening mutation
    return the same order; no test in any PRD asserts a *particular* order, and no consumer
    file sorts on `GameId`.
    *Open Questions 7 carries the decision.* If it lands on "add the field", this
    requirement is replaced by an ordering guarantee and requirement 21's `StoredGame` gains
    one line; nothing else in this PRD changes.

## Out of Scope

- **The domain models themselves** — `Board`, `Move`, their fields and their `freezed` /
  `json_serializable` definitions: `P1-02-engine-rules.md` (its reqs 29–31). This PRD
  serializes them and defines none of them.
- **Who calls save.** This PRD owns the repository and states the obligation (requirement
  6). It does not own the call sites. **Timing is now settled; the call is still unclaimed
  in code.** Modelled on `P2-02-audio.md`'s call-site table, which does the same for
  playback:

  | Write | When | Call-site owner |
  |---|---|---|
  | After a confirmed move | Settled — `Menus and UI.md` → Decisions → When is a game written to storage? | **Unclaimed.** The commit path is `P3-02-move-input.md` req 4 ("the mark is placed and the turn passes"); no requirement in that PRD mentions persistence |
  | At game end, carrying the increment | Same write — the game-ending move is a confirmed move | Same unclaimed path. `P3-04-game-over-rematch.md` req 9 can now be written against it |
  | On taking a rematch | Not a move; needs its own write or the next confirmed move covers it | **Unclaimed** — `P3-04-game-over-rematch.md` req 9's territory |
  | On leaving a game to the main menu | No write needed — requirement 11 | n/a |
  | On creating a new game | On confirm in the name prompt | `P4-02-open-games-list.md` req 10, via requirement 28's notifier |
  | On deleting a game | On the delete action | `P4-02-open-games-list.md` req 7, via requirement 28's notifier |
  | On changing a settings toggle | On the switch | `P4-04-settings.md`, via requirement 27's setters |

  The precise gap: **`P3-02-move-input.md` is where the confirmed-move write has to be
  invoked, and that PRD has no requirement claiming it.** Naming it is this PRD's job;
  adding the requirement is that PRD's, in wave 3. The rematch row is a second, smaller
  gap — a rematch resets the board without being a move, so either it writes or the state
  on disk lags by one move until the next confirm.
- **The settings screen, its switches, and where they are reachable from** —
  `P4-04-settings.md`. Requirement 26 owns the *value* and requirement 27 the write path;
  that PRD owns the surface and calls the setters. It now draws four rows, not three.
- **Music itself** — the theme's music slot, where the audio comes from, whether it loops,
  and whether it differs by screen. `Theming.md` → Decisions → Do all four toggles ship,
  and is music a theme concern? makes music a **theme** concern and leaves those three
  questions open in its own Open Questions; the theme-side slot is
  `P1-03-theme-system.md`'s and playback is `P2-02-audio.md`'s (whose `SoundMoment` enum
  has no music member today). This PRD persists the on/off preference and nothing else.
- **What "off" means for each channel** — silence, no buzz, instant state changes:
  `P2-02-audio.md`, `P2-03-haptics.md`, `P2-04-animations.md`. This PRD supplies the
  boolean and asserts nothing about behavior.
- **The open-games list UI** — the rows, the delete affordance, the empty state, and what a
  player sees when `create` returns `CapReached`: `P4-02-open-games-list.md`. Requirement 28
  supplies the data and the mutations; that PRD renders them and decides row content.
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
- **Any backend, sync, or network storage.** Multiplayer is named as a direction that must
  not be foreclosed (`Tech Design.md` → Decisions → Online multiplayer is an intended
  future direction), not as work now.

## Open Questions

### 1. Persisted data — versioning

As worded in `Tech Design.md` → Open Questions → 1. Persisted data — versioning:

> When the shape of stored data changes — a fifth preference is added, a key is renamed,
> an open game gains a field — what happens to data already on the device? A game
> written by v1.0 has to still load in v1.1.

*Note that the doc's own example just happened:* a fifth preference **was** added (music,
requirement 24), before any device holds data, so it cost nothing this time. That is the
cheap case, and it will not stay cheap.
*Consequence of shipping without an answer — moved here from an Out of Scope bullet that was
deciding it by omission:* this PRD designs no migration hook and no schema-version field, so
**v1.0 data ships unversioned** — the `open_games` box holds bare `StoredGame` JSON and the
five preference keys hold bare values. Any scheme adopted later therefore has to treat
*absence of a version* as meaning v1 rather than meaning corrupt. That is a real constraint
on the answer, not a decision this PRD is entitled to make. Adding a version field now,
before any device holds data, is cheaper than inferring one later — and Open Questions 7 may
add a field anyway, which is the natural moment to add both.

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

<!-- Closed since earlier drafts:
     - "How is an open-game slot ever freed" → requirement 17.
     - "Which layer owns preference access" → requirement 14; PreferencesRepository lives in
       lib/storage/.
     - "When is a save written" → ANSWERED. Menus and UI → Decisions → When is a game
       written to storage?: after every confirmed move. Now requirement 6's app-level claim.
       What remains is not a question but an unclaimed call site — see Out of Scope.
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
to decide. This PRD adds no field for it.

### 7. Does `StoredGame` gain a timestamp? (needs the user — one answer settles three things)

**This is the same question as `P4-02-open-games-list.md` → Open Question 4**, reached from
the storage side. That one asks what a row displays; this one asks whether the field exists.
They cannot be answered separately, and the field is a **wave-1 model change** here whichever
way it goes.

What rides on it:

- **List ordering.** Requirement 29 states there is none today, and that Hive
  box-iteration order is not stable across compaction — so the player's list can silently
  reshuffle between launches. A timestamp is the sort key that fixes it. (`P4-02` → Open
  Question 6 asks for recency ordering and needs this same field.)
- **The row's relative timestamp.** `1b` draws one; `P4-02` req 4 fences it out of this wave
  precisely because `StoredGame` has no field to render.
- **Duplicate titles.** A date incidentally disambiguates two games both called
  `ItSaMeMaRiO`, which softens OQ 6b above without making the id itself visible.

Not chosen here, because "does the player see a timestamp" is a product question. But note
the asymmetry: **adding the field is cheap now and expensive later** — it is one line on
`StoredGame` today, and after v1.0 ships it is a migration against unversioned data
(OQ 1). Storing it and not displaying it is a coherent middle: ordering and stability
improve, and the row stays as `P4-02` req 4 fences it until the product half lands.
