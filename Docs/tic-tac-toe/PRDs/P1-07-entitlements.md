**Build-readiness: 88**

# PRD: Entitlements — what the app knows about what the player owns

> **Status:** Draft · Source docs read: `Tech Design.md`, `Theming.md`, `Menus and UI.md`,
> `Game Overview.md`, `Game Board Design.md`, `Rules.md`, `Animations.md`, `roadmap.md`,
> and the read-only reference asset `design_handoff_game_ui/` (`README.md` → *2a — Theme
> Select (overlay, with paywall)* → *Ownership states — the part to build carefully*;
> `themes.catalog.json`). `Alternative Game Styles.md` is a declared parking-lot doc and
> was not used as a source.

**Wave:** P1 · **File:** `P1-07-entitlements.md` — parallel-safe with the other P1 PRDs.

> **This PRD is one half of a split.** A single earlier in-app-purchases PRD held both the
> entitlement model and the store integration, which produced a circular dependency:
> `P1-04-persistence.md` needs entitlement state to resolve the open-game ceiling, while the
> purchase layer needs `P1-04`'s storage to keep its results. That PRD was divided along the
> store boundary rather than rewritten: **this PRD is what the app knows about what the
> player owns, and it needs no network**; its counterpart `P4-05-purchase-flow.md` (wave 4)
> is StoreKit, buying and restoring.

> **Requirement numbering is append-only.** Requirements 16–21 were added after 1–15, and
> are numbered last rather than inserted in logical position because sibling PRDs cite this
> one's requirements **by number**: `P4-03-theme-selection.md` cites Requirements 2 and 6,
> `P4-05-purchase-flow.md` cites Requirements 2, 4, 5, 6, 7, 9, 10 and 14, and
> `P1-04-persistence.md` cites Requirements 7, 9 and 10. Renumbering would silently repoint
> all of them.
>
> **Requirement 11 is the interface contract and should be read first.** Requirements 16–21
> complete it: representation, what is not persisted, how the value is seeded at launch, who
> writes to disk, the wave-1 product map, and apply ordering. **A reader who stops at
> Requirement 11 cannot compile this layer.**

**Depends on:**

- `P1-03-theme-system.md` — theme UUID identity. This PRD attaches ownership *beside* a
  theme, never inside its definition, and reads no theme file. Same wave.
- `P1-04-persistence.md` — where entitlement state is written down. That PRD owns the store,
  the keys and the format, and publishes `EntitlementsStore` (its Requirement 28). **This
  layer does not call it** — see Requirement 19.

**Depended on by:** `P1-04-persistence.md` (the ceiling it enforces), `P4-02-open-games-list.md`
(the open-game cap value), `P4-03-theme-selection.md` (the per-theme ownership state its rows
are labelled from), `P4-05-purchase-flow.md` (which produces the store results this layer
applies).

**Nothing here requires a network or a store.** With no purchase layer built, every read in
this PRD resolves to the free tier, which is what makes it a wave-1 feature.

---

## Problem

There is no application code yet, so there is nothing that knows what the player owns.
Without that: the theme list has no ownership state to label rows with, and the open-game
cap is a constant with no second value.

Both consequences land on features that ship before any store integration does.
`Menus and UI.md` → Decisions → *How many open games do we keep?* reads "3 by default, no
more. A $4.99 in-app purchase raises the cap to 100 open game slots" — so
`P1-04-persistence.md` cannot enforce a ceiling without asking something what the player
owns. `Theming.md` → Decisions → *Which themes are free* commits the theme selection list to
**labelling** which themes are free and which are paid. Neither can wait for StoreKit.

There is a second problem, and it is the one that bites at build time. **Four PRDs compile
against this layer.** `P1-04-persistence.md` persists the value, `P4-02-open-games-list.md`
reads the cap, `P4-03-theme-selection.md` reads per-theme ownership, and
`P4-05-purchase-flow.md` applies store results. If each writer invents a name — or finds a
named type it cannot construct — every PRD passes review and **the call sites do not
compose**. Requirements 11 and 16–21 exist to stop that.

## Goal

The app has one layer that knows what the player owns, **with a named, constructible public
surface every consumer codes against**. It exposes two entitlements — *paid themes* and *the
100-slot open-game cap* — answers synchronously from a value seeded at launch so no gating
decision waits on the network, and defaults to the free tier only when nothing has ever been
stored. Apple is the record of truth and is queryable at runtime; the local copy is an
offline convenience, and this layer never mints an entitlement of its own.

## Requirements

### What the entitlements gate

1. **Neon and Classic Red vs Blue are free and are never subject to an entitlement check.**
   A player with no purchases, and a player whose store query never completed, can select
   either one.
   *(`Theming.md` → Decisions → Which themes are free: "Neon and Classic Red vs Blue are
   free. Every theme beyond those two is paid.")*
   *Testable:* with the store unavailable and no entitlement state present,
   `ownershipOf` returns `ThemeOwnership.free` for both UUIDs and both themes are
   selectable.

2. **Every theme beyond those two is paid and is selectable only while the corresponding
   entitlement is held.**
   *(`Theming.md` → Decisions → Are themes unlockable/rewards: "Yes — some themes are paid …
   any other themes will be a paid for theme"; → Which themes are free.)*
   *Testable:* a theme whose UUID is neither of the two free UUIDs (Requirement 12), with no
   entitlement held, reports `ThemeOwnership.locked` and cannot be applied as the active
   theme.
   *"The corresponding entitlement"* is resolved forward through
   `EntitlementProducts.productIdForTheme` — see Requirement 16 for why that direction, and
   Requirement 20 for its wave-1 implementation.

3. **The open-game cap is 3 without the unlock entitlement and 100 with it.** The cap is a
   value the entitlement layer supplies, not a constant compiled into the list screen or the
   storage layer.
   *(`Menus and UI.md` → Decisions → How many open games do we keep?; `Tech Design.md` →
   Decisions → In-app purchases.)*
   *Testable:* with the entitlement absent `openGameCap` reports 3, with it present it
   reports 100, and no other source in `lib/` defines either number.

4. **The entitlement layer exposes, per theme, which of `free` / `owned` / `locked` the
   theme is in**, so the selection list can label it.
   *(`Theming.md` → Decisions → Which themes are free; `design_handoff_game_ui/README.md` →
   *2a* → *Ownership states*; `themes.catalog.json` → `ownershipStates`.)* The row
   treatments, badges and price button are `P4-03-theme-selection.md`'s.
   *Testable:* given Neon's UUID, a non-free UUID whose entitlement is held, and a non-free
   UUID whose entitlement is not, `ownershipOf` returns `free`, `owned` and `locked`
   respectively — **with no catalog field consulted**, per Requirement 12.

5. **Ownership is never part of a theme definition.** No theme YAML file carries an
   ownership, price or purchase field, and materializing a theme does not consult purchase
   state.
   *(`themes.catalog.json` → note: "Ownership is NOT part of a theme definition"; consistent
   with `P1-03-theme-system.md` Requirement 31.)*
   *Testable:* deleting the entitlement layer entirely still lets every theme file load and
   merge over Neon.

6. **A locked theme still renders its preview; buying is the only gate.** Ownership
   withholds *selection*, not the theme's values.
   *(`themes.catalog.json` → `storeRequirements`; `design_handoff_game_ui/README.md` → *2a*:
   "A locked row must read as **buyable, not broken**".)*
   *Testable:* this layer exposes **no operation that takes a theme UUID and withholds,
   filters, nulls or defers that theme's values** — `ownershipOf` returns a
   `ThemeOwnership` and nothing else. A consumer holding a `locked` result can still load and
   render that theme through `P1-03-theme-system.md` without calling into this layer.

### Keeping it, reading it, and who has authority

> **Why a local copy exists.** `Tech Design.md` → Decisions → *Entitlements — Apple stores
> them, no backend needed*: **Apple is the record of truth and it is queryable at runtime**,
> via `Transaction.currentEntitlements`. The same Decision names what a local copy is for and
> what it is not: "**Any locally stored entitlement state is an offline convenience, not the
> record.**"

7. **Entitlement state is kept locally as an offline convenience, and survives an app
   restart.** The local copy exists so gating resolves with no network available; it is
   never the record of truth. `P1-04-persistence.md` owns the store, the keys and the format
   (its Requirements 18–20 and its `EntitlementsStore`).
   *(`Tech Design.md` → Decisions → Entitlements — Apple stores them, no backend needed;
   → Decisions → Persistence package.)*
   **Who writes it is Requirement 19 — and it is not this layer.** How the value gets back
   *in* at launch is Requirement 18.
   *Testable:* purchase, force-quit, relaunch with no network — the entitlement is still
   held and `openGameCap` reports 100 on the first frame (Requirement 18).

8. **Entitlement state is readable from anywhere in the app, as Riverpod provider state**,
   and a change to it — a completed purchase or a completed restore — reaches its gating
   consumers within the same session, without a restart.
   *(`Tech Design.md` → Decisions → State management — Riverpod; `P1-01-app-scaffold.md`
   Requirement 11, which fixes the idiom as a plain `NotifierProvider`, no codegen.)*
   *Testable:* with the theme list open, applying a store result that grants an entitlement
   moves the affected row out of `locked` without rebuilding the app.

9. **When the store cannot be reached, locally held entitlement state is what gating uses.**
   A failed or timed-out query is not treated as an answer of "owns nothing", and does not
   clear what is held.
   *(`Tech Design.md` → Decisions → Entitlements makes the authoritative source **queryable**:
   ownership is a question asked of Apple at runtime. A query that fails returns *no
   information* — an absence, not an answer — so treating it as "owns nothing" would be
   inventing an answer Apple never gave.)*
   *Testable:* with an entitlement held, stub every store call to fail, relaunch, and
   `openGameCap` still reports 100 and paid themes still report `owned`.
   *Not specified here:* what happens if the store affirmatively reports an entitlement
   *gone* — **Open Question 1**.

10. **Apple is the record of truth on what was bought; the local copy is a copy of Apple's
    answer, never the grantor.** Nothing in this layer mints, grants or upgrades an
    entitlement on its own — every entitlement it holds originates in a store result.
    *(`Tech Design.md` → Decisions → Entitlements; `themes.catalog.json` → note:
    "entitlement is account/device state".)*
    *Testable:* the only member of Requirement 11's surface that mutates state is
    `applyStoreResult` (Requirement 14). There is no local grant and no debug-only setter in
    shipped code.
    *This requirement is the prohibition; **Requirement 14 is the operation.***

    > **Which direction "authority" runs.** An *affirmative* store answer overrides what is
    > held locally; a *failed* one does not. That follows from `Tech Design.md` → Decisions →
    > *Entitlements* — Apple's answer is the record and the local copy is "an offline
    > convenience, not the record". `P1-04-persistence.md` Requirement 19 and
    > `P4-05-purchase-flow.md` Requirement 5 both now say the same; there is no residual
    > contradiction. What remains open is the *loss* case — **Open Question 1**.

### The interface

11. **The public surface is named and constructible, and these are the signatures.** Every
    consumer codes against these and no consumer invents its own.

    ```dart
    // lib/entitlements/entitlements.dart

    /// One snapshot of what the player owns. Immutable value type.
    final class Entitlements {
      const Entitlements({
        required this.ownedProductIds,
        this.isProvisional = true,
      });

      /// The free tier — nothing owned. What an unpopulated device reports
      /// (Requirements 1 and 3), and the seed of last resort (Requirement 18).
      const Entitlements.free()
          : ownedProductIds = const {},
            isProvisional = true;

      /// Product identifiers the store reported as currently owned.
      /// Product IDs, not theme UUIDs — Requirement 16.
      final Set<String> ownedProductIds;

      /// True until a store answer has been applied this session (Requirement 13).
      /// NOT persisted, and excluded from == — Requirement 17.
      final bool isProvisional;

      int get openGameCap;                            // Requirement 3
      ThemeOwnership ownershipOf(String themeUuid);   // Requirements 4, 16

      /// Value equality over `ownedProductIds` only. Requirement 17 explains
      /// why `isProvisional` is excluded.
      @override bool operator ==(Object other);
      @override int get hashCode;
    }

    enum ThemeOwnership { free, owned, locked }

    // lib/entitlements/entitlement_products.dart

    abstract interface class EntitlementProducts {
      String get openGameCapProductId;
      String? productIdForTheme(String themeUuid);   // null when nothing unlocks it
    }

    // lib/entitlements/entitlements_notifier.dart

    final class EntitlementsNotifier extends Notifier<Entitlements> {
      @override
      Entitlements build();                          // Requirement 18 — seeding

      /// The only mutator. Requirement 14.
      void applyStoreResult(Set<String> ownedProductIds);
    }

    // lib/entitlements/entitlement_providers.dart

    final NotifierProvider<EntitlementsNotifier, Entitlements> entitlementsProvider;
    final Provider<EntitlementProducts> entitlementProductsProvider;
    ```

    *(**Engineering naming call, not a doc citation.** No design doc names an API — the docs
    settle meaning, not signatures. The mechanism is fixed by `P1-01-app-scaffold.md`
    Requirement 11 and `Tech Design.md` → Decisions → State management — Riverpod. The block
    is written in the style `P1-04-persistence.md` Requirement 28 uses, for the same reason.)*

    **The state type is `Entitlements`, not `AsyncValue<Entitlements>`** — settled by
    `Tech Design.md` → Decisions → *Entitlements — Apple stores them, no backend needed*,
    which now carries: "**The entitlement provider's shape — last-known plus refresh.**
    Entitlement state is exposed as a plain value, seeded from the locally cached copy and
    refreshed when the store answers — not as an async wrapper every consumer must branch on.
    This is the same class of decision as **State management — Riverpod** above." Consumers
    never handle a pending case; Requirement 13 is the precedence rule that makes the value
    answerable at every moment, and Requirement 18 is what makes the seed real.

    *Testable:* a consumer can construct an `Entitlements` in a test without the store, the
    persistence layer or a provider container — which is what
    `P4-03-theme-selection.md` Requirement 13's "a fake `Entitlements` returning each of the
    three states" requires — and two instances with equal `ownedProductIds` compare equal,
    which is what `P1-04-persistence.md` Requirement 18's "read back an **equal** set"
    requires. A source scan finds no second type in `lib/` modelling ownership or the cap,
    and no `AsyncValue` wrapping entitlement state.

12. **Paid-ness is derived, not recorded.** A theme is paid **iff its UUID is not one of the
    two free UUIDs.** No catalog field, theme-file key or ownership marker records it.

    | Theme | UUID | Source |
    |---|---|---|
    | Neon | `b7c1f0a6-2f5e-4d3a-9c88-0f5a1e2d3c40` | `themes.catalog.json` → `baseThemeId` / `defaultThemeId`; restated by `P1-03-theme-system.md` Requirement 13 |
    | Classic Red vs Blue | `3d1a8b52-9c47-4b16-8f2e-7a5d0c9e1b34` | `themes.catalog.json` → Classic's `id`; restated by `P5-01-classic-theme.md` Requirement 7 |

    *(`Theming.md` → Decisions → Which themes are free: "**Every theme beyond those two is
    paid.**" A complete rule over UUIDs, so paid-ness needs no separate record.
    `Tech Design.md` → Decisions → Theme identity — UUID makes the rule stable under
    renaming.)*
    *Testable:* the free set is exactly these two UUIDs; `ownershipOf` returns `free` for
    both and never `free` for any other UUID; a source scan finds no ownership, price or
    "isPaid" field read from any theme file or catalog.

13. **While no store answer has been applied, the layer reports the last known answer — not
    the free tier.** In order of precedence: the most recent store result applied this
    session; failing that, the value seeded at launch from the local copy (Requirement 18);
    failing that — and only where nothing has ever been stored — `Entitlements.free()`.
    `isProvisional` is `true` until a store answer has been applied in the current session.

    **This is the "last-known plus refresh" model, stated as behavior.** `isProvisional` is
    the "carries an indication of whether it is still provisional" half of that decision, and
    is deliberately advisory — nothing in Requirements 1–4 changes behavior based on it.

    *(Requirement 9's rule applied to a second case: a query **in flight** is as much an
    absence of information as a query that **failed**, and `currentEntitlements` is
    asynchronous, so a cold launch always has a window before any answer exists.)*
    *Testable — two cases, and the second is the one that catches the real bug:*
    - **Seeded notifier, query pending** → with the cap unlock in the seed, `openGameCap`
      reports 100 and a held paid theme reports `owned`, while `isProvisional` is `true`.
    - **Cold launch against a populated store** → boot the app as
      `P1-01-app-scaffold.md` boots it, with the cap unlock already in
      `EntitlementsStore` and every store call stubbed to hang. **The first frame reads
      `openGameCap == 100`.** This test must exercise the real startup path, not a
      pre-seeded notifier — see Requirement 18 for why.

    *The failure this prevents:* the cheapest implementation reports the free tier until an
    answer lands, so **a paying customer sees their content locked on every launch**.
    Requirement 9's test does not catch it, and neither does the first case above.

14. **`applyStoreResult` is the hand-off, and the only mutator.** It takes an **affirmative**
    store answer — the set of product identifiers the store reports as currently owned — and
    replaces the held entitlement state with what that answer implies.
    - An affirmative answer **replaces** what is held, per Requirement 10.
    - A failed, timed-out or unanswered query is **not** an affirmative answer and must not
      be passed to it; Requirement 9 governs that case.
    - Applying the same answer twice leaves the same state — idempotent.
    - Applying an answer sets `isProvisional` to `false`.
    - It updates **in-memory state only.** Persisting is Requirement 19's, and is not this
      layer's.
    - Ordering when two answers can race is Requirement 21's.

    **The signature is `void applyStoreResult(Set<String> ownedProductIds)`** — fenced as the
    build default. `P4-05-purchase-flow.md` Requirements 4, 5, 10 and 14 all call it. Open
    Question 4 governs *who declares* a richer result type if one is wanted, not the shape
    fenced here.
    *(This requirement exists because those four requirements hand a store result to this
    layer, and Requirement 10 defines a *prohibition*, not an operation.)*
    *Testable:* applying a result naming the cap product moves `openGameCap` from 3 to 100
    and `isProvisional` from `true` to `false`; applying it a second time changes nothing;
    no other member of the surface can produce that transition.

15. **This layer lives at `lib/entitlements/`.** Settled, not provisional.
    *(`Tech Design.md` → Decisions → *Project structure — layer-first* now lists
    `entitlements/    ← StoreKit entitlement state, owned by P1-07-entitlements` in the tree,
    and records it as one of "five more new layers, each proposed by the PRD that needs it".)*

    **The residual, which nobody currently holds:** `P1-01-app-scaffold.md` Requirement 2
    builds the tree and verifies "after a fresh clone of the committed branch, **all nine
    paths exist**" — a list written before the doc added these five layers, and
    `entitlements/` is not among the nine. **Routed to `P1-01-app-scaffold.md`**: that
    requirement needs to build and verify the amended tree, or this layer has no directory to
    land in. Nothing in this PRD can fix it.

### Representation, seeding, persistence, products, ordering

16. **`Entitlements` holds product identifiers, and `ownershipOf` resolves forward.** The
    representation is `Set<String> ownedProductIds` — store product IDs. Answering
    "is this theme owned?" resolves **forward**: take the theme UUID, ask
    `EntitlementProducts.productIdForTheme(uuid)` for the product that unlocks it, and test
    membership in `ownedProductIds`. A `null` product means nothing unlocks that theme, which
    with Requirement 12 yields `locked` for any non-free UUID.

    **Why forward and not by UUID.** The store answers in product identifiers — that is what
    `Transaction.currentEntitlements` returns — so product IDs are what this layer is handed
    (Requirement 14). Keying by theme UUID instead would need an inverse map, product → theme,
    which does not exist on this surface: `EntitlementProducts` publishes only the forward
    direction, and Requirements 5 and 12 bar this layer from reading any theme list to build
    one. Forward resolution needs no such map.

    > **A collision routed to `P1-04-persistence.md`, not resolved here.** That PRD's
    > Requirement 18 states "Per-theme unlocks are keyed by the theme's **UUID**, so renaming
    > a theme does not orphan an entitlement the player paid for." Under this requirement the
    > persisted value is `Entitlements`, whose representation is product IDs — so per-theme
    > unlocks are keyed by **product ID**, not UUID. **Both cannot be true of the same
    > object.**
    >
    > The good news is that req 18's *stated purpose* survives intact: renaming a theme
    > orphans nothing, because a product ID has no relationship to a display name at all — it
    > is, if anything, more stable than a UUID. **The correction belongs in `P1-04`'s wording,
    > not in this layer's representation**, because reversing it here would require the
    > inverse map this requirement explains does not exist. Routed, not silently overridden.

    *Testable:* `ownershipOf` calls `productIdForTheme` exactly once per query and consults no
    theme list; with `productIdForTheme` stubbed to return a product present in
    `ownedProductIds`, the UUID reports `owned`; stubbed to return `null`, a non-free UUID
    reports `locked`.

17. **`isProvisional` is not persisted, and is excluded from equality.** It describes the
    current session, not what the player owns. `P1-04-persistence.md` writes and reads whole
    `Entitlements` values, so if `isProvisional` were a serialized field a cold launch would
    restore it as `false` — asserting that a store answer had been applied this session when
    none has — and Requirement 13's contract would be violated on the first frame of every
    launch. A restored value therefore always has `isProvisional == true`.

    **It is excluded from `==` for a second, independent reason.**
    `P1-04-persistence.md` Requirement 18's testable writes a value and demands the read-back
    compare **equal**. The written value has `isProvisional == false` (a store answer had just
    been applied); the restored one has `true`. If equality covered the flag, that testable
    could never pass. Equality is over `ownedProductIds` alone.
    *Testable:* serialize an `Entitlements` with `isProvisional == false`, restore it, and the
    restored value has `isProvisional == true` and compares **equal** to the original.

18. **`build()` returns a value seeded from disk before the first frame.**
    `EntitlementsNotifier.build()` is synchronous — a `Notifier` must return its initial state
    without awaiting — while `EntitlementsStore.read()` is `Future<Entitlements?>`
    (`P1-04-persistence.md` Requirement 28). A `build()` that starts the read and returns
    `Entitlements.free()` meanwhile satisfies its own signature and **ships the bug
    Requirement 13 exists to prevent**.

    **The fence:** application startup awaits `EntitlementsStore.read()` **once, before the
    first frame**, and provides the result as this notifier's seed — a provider override at
    the `ProviderScope` `P1-01-app-scaffold.md` Requirement 10 installs. `build()` then
    returns that seed synchronously. Where the read returns `null`
    (`P1-04-persistence.md` Requirement 20) or fails, the seed is `Entitlements.free()`.
    No other startup ordering satisfies both Requirement 13's precedence and the synchronous
    signature.
    *Testable:* Requirement 13's cold-launch case — boot with the cap unlock in the store and
    all store calls hanging; the first frame reads `openGameCap == 100`. Deleting the seeding
    step makes it read 3, and that must fail the suite.
    *Not settled — with the user:* whether the first frame **waits** on that read at all. See
    Open Question 7.

19. **This layer does not write to disk; the purchase layer does.**
    `applyStoreResult` updates in-memory state and stops there. Persisting the new value
    through `EntitlementsStore.write` is the caller's — which
    `P1-04-persistence.md` Requirement 19's testable already settles: "the only mutating
    operation on `EntitlementsStore` is `write`, and it is **reachable only from the purchase
    layer**."

    **This answers half of Open Question 4** — `P4-05-purchase-flow.md` writes directly to
    `P1-04-persistence.md` rather than through this layer — and it is recorded here rather
    than left implicit, because a writer building from this PRD alone would otherwise write
    nothing, leaving Requirement 7's testable failing and Requirement 13's "seeded from the
    local copy" tier permanently empty.

    > **The hazard this creates, routed to `P4-05-purchase-flow.md`.** Applying and persisting
    > are now two calls the purchase layer must make together. Making one without the other
    > gives an in-memory grant that vanishes on relaunch, or a stored grant the session never
    > sees. That PRD's Requirements 4, 5, 10 and 14 each call `applyStoreResult`; **each also
    > needs to write**, and none of them says so today.

    *Testable:* a source scan finds no reference to `EntitlementsStore` or
    `entitlementsStoreProvider` under `lib/entitlements/`.

20. **The wave-1 `EntitlementProducts` implementation is fenced.** Until product structure is
    decided (Open Question 4 of `P4-05-purchase-flow.md`), the shipped implementation is:
    - `openGameCapProductId` returns
      `com.ehrendavis.tictactoeextreme.opengames.slots100`, the identifier
      `P4-05-purchase-flow.md` Requirement 13 fences, derived from the settled bundle
      identifier (`Tech Design.md` → Decisions → *Bundle identifier*).
    - `productIdForTheme` returns `null` for **every** theme UUID, because no paid theme
      exists (`P4-05-purchase-flow.md` Requirement 9: both shipped themes are free).

    **Why this is stated here.** `P4-05-purchase-flow.md` Requirement 13 says the identifier
    "is reached **only** through `EntitlementProducts.openGameCapProductId`" — which puts the
    one literal in this layer. Without this requirement, Requirement 12's testable ("a source
    scan finds no ownership, price or 'isPaid' field") and `P4-05`'s ("no product-identifier
    literal outside `lib/purchase/`") pull in opposite directions and neither layer may hold
    the string. This one names its home: `lib/entitlements/`, behind the interface, replaced
    by one edit when `P5-03-release-fastlane.md` registers the real identifier.
    *Testable:* `productIdForTheme` returns `null` for both free UUIDs and for an arbitrary
    third UUID; `openGameCapProductId` is the only product-identifier literal in `lib/`.

21. **Store answers are applied in arrival order, and the layer does not reorder them.**
    `applyStoreResult` is last-in-wins: the most recent call defines the held state, per
    Requirement 14's replace semantics.

    **The race this names.** `P4-05-purchase-flow.md` has two independent callers — its
    Requirement 4 launch query and its Requirement 14 `Transaction.updates` listener — and
    both can be in flight at once. If a slow launch query resolves *after* a listener
    delivered a newer answer, replace semantics apply the **older** answer and silently
    revoke an entitlement the player just obtained.
    **This PRD fences only its own half:** applies are serialized in arrival order and never
    reordered or coalesced. **Guarding against a stale apply is the caller's**, and is
    routed to `P4-05-purchase-flow.md` — nothing on this surface carries a timestamp or
    sequence number to guard with, and adding one would be inventing a result type Open
    Question 4 has not settled.
    *Testable:* two `applyStoreResult` calls in sequence leave the state of the second,
    regardless of their contents; the layer exposes no reordering, queueing or merge
    behavior.

## Out of Scope

- **StoreKit, the purchase flow, restore-purchases, purchase outcomes, the parental gate and
  the store-side product concerns** — `P4-05-purchase-flow.md`. It supplies the store results
  this layer applies (Requirement 14) and persists them (Requirement 19).
- **Where entitlement values are stored, and the write itself** — `P1-04-persistence.md`.
- **Theme materialization, the theme object, YAML loading and UUID identity** —
  `P1-03-theme-system.md`. This PRD reads no theme file (Requirements 5, 12, 16).
- **The theme selection overlay's rows, badges and price button** —
  `P4-03-theme-selection.md`. This PRD supplies the state those render from (Requirement 4).
- **The open-games list, its delete action, and how the cap is displayed or enforced** —
  `P4-02-open-games-list.md` and `P1-04-persistence.md`. This PRD supplies the cap value.
- **The App Store Connect record and the real product identifiers** —
  `P5-03-release-fastlane.md`. Requirement 20 fences a provisional one.
- **Any paid theme's content.** No paid theme exists; Requirement 4 is satisfied with fixture
  UUIDs.
- **`Alternative Game Styles.md`** — declared parking lot.

## Open Questions

### 1. What does the open-games list *show* when the cap drops below the games already stored?

**Narrowed twice, and most of this is now settled — by siblings, not here.**

*The mechanism is settled.* `Tech Design.md` → Decisions → *Entitlements*: "A refunded or
lapsed purchase simply stops appearing in `currentEntitlements` — that is what answers 'what
happens when an entitlement goes away.'" An entitlement is lost exactly when it stops coming
back from Apple; Requirement 9's exception distinguishes that from a failed query.

*The wave-1 behaviour is also settled, by two sibling requirements that together leave no
choice:* `P1-04-persistence.md` Requirement 10 enforces the ceiling **at create time only**
and states "the store **never evicts**", and `P4-02-open-games-list.md` Requirement 7 records
replace-the-oldest as considered and rejected — "Nothing in this feature deletes a game the
player did not choose to delete." So when a cap drops from 100 to 3 with 40 games stored:
**nothing is deleted, nothing is hidden, every stored game stays resumable, and no new game
can be created until the player's own deletions bring the count under 3.** No requirement
anywhere permits any other outcome, and this PRD is not the place that would change it.

**What genuinely remains, and is with the user:** what `P4-02-open-games-list.md` *displays*
in that state. Forty rows above a cap of three, with New Game refusing, needs an explanation
the player can act on, and no doc describes one. That is a display question on that PRD, not
a data question here.

> **A pointer this PRD had wrong, now corrected.** Earlier drafts said
> `P1-04-persistence.md` → Open Questions 5 "raises the same case from the storage side." It
> does not: that question is **"Which store do entitlements belong in?"** —
> `shared_preferences` versus Hive — and it touches the cap-drop case only to hand it back
> here. There is **one owner with pointers into it, not a three-way loop.**
> `P4-02-open-games-list.md` Open Question 8 inherited the same mistaken pointer, and
> `P1-04-persistence.md` Requirement 10 repeats it a third time; both should point at this
> question instead.

### 2. Can a paid theme ever be a product whose theme file is not on the device?

**With the user.** If every paid theme is bundled and merely unlocked, this layer only ever
gates content the device already has. If a paid theme can arrive any other way, the layer
must handle an entitlement held for something not installed.

`Theming.md` → *Where Themes Live* notes "**for now**, themes are contained within the
codebase … That's a possible later thing, not now" — prose with an explicit "for now", not a
decision.
*Does not block wave-1 code:* Requirement 12 derives paid-ness from the UUID alone, and
Requirement 16's forward resolution returns `locked` for anything with no product, installed
or not.

### 3. Answered — which store holds entitlement state

Carried by `P1-04-persistence.md` → Open Questions 5. Not this PRD's: Requirement 7 states
that a copy exists, Requirement 19 states this layer does not write it, and
`EntitlementsStore` hides the choice behind an interface. Kept as a stub for numbering
stability.

### 4. Who declares a richer store-result type? — first half only

**With the user, and now half-answered.**

*Answered:* whether `P4-05-purchase-flow.md` writes through this layer or directly to
`P1-04-persistence.md`. It writes **directly** — `P1-04-persistence.md` Requirement 19's
testable makes `EntitlementsStore.write` "reachable only from the purchase layer".
Requirement 19 here records it.

*Still open:* whether `applyStoreResult` should take something richer than
`Set<String>` — a result type carrying, say, a timestamp or a source discriminator — and if
so, which PRD declares it. Requirement 14 fences `Set<String>` as the build default, and
Requirement 21 records the one thing a richer type would buy: a guard against a stale apply
winning a race. Call sites compose either way.

### 5. Answered — which `lib/` layer this lives in

**Closed.** `Tech Design.md` → Decisions → *Project structure — layer-first* now lists
`entitlements/` in the tree, owned by this PRD. Requirement 15 states it. The residual —
`P1-01-app-scaffold.md` Requirement 2 still building and verifying nine paths that do not
include it — is routed there and is not an open question of this PRD's.

### 6. Answered — what type does `entitlementsProvider` expose?

**Closed: `Entitlements`, exposed directly.** `Tech Design.md` → Decisions → *Entitlements —
Apple stores them, no backend needed* carries "**The entitlement provider's shape — last-known
plus refresh**", with all three consequences: consumers never handle a pending case,
a paying player never sees purchased content locked while a query is in flight, and the value
carries whether it is still provisional. Requirements 11, 13, 17 and 18 implement them.

### 7. Does the first frame wait on the entitlements read? — **with the user**

Requirement 18 fences *that* a seed happens before `build()`, because nothing else satisfies
both Requirement 13's precedence and a synchronous `Notifier`. What it cannot settle is the
user-facing trade:

- **Wait** — startup awaits one small disk read before the first frame. A paying player never
  sees a locked-everything flash; every launch costs the read.
- **Do not wait** — the app paints immediately and entitlement-dependent surfaces correct
  themselves a frame or two later. Cheaper launch; a paying player can see their content
  locked, briefly, on every launch.

This is the same class of trade as Requirement 13's, one layer earlier, and **fencing it
wrong produces the worse guess**: an implementer optimising for launch speed reintroduces
exactly the failure Requirement 13 was written to prevent. `P1-01-app-scaffold.md`
Requirement 10 owns the `ProviderScope` where the override lands, so whichever way this goes,
that PRD is where it is implemented.
