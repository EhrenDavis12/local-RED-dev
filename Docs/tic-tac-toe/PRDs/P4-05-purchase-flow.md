**Build-readiness: 90**

# PRD: Purchase Flow — StoreKit, buying and restoring

> **Status:** Draft · Source docs read: `Tech Design.md`, `Theming.md`, `Menus and UI.md`,
> `Game Overview.md`, `Game Board Design.md`, `Rules.md`, `Animations.md`, `roadmap.md`,
> and the read-only reference asset `design_handoff_game_ui/` (`README.md` → *2a — Theme
> Select (overlay, with paywall)* → *Ownership states — the part to build carefully*;
> `themes.catalog.json`). `Alternative Game Styles.md` is a declared parking-lot doc and
> was not used as a source.

**Wave:** P4 · **File:** `P4-05-purchase-flow.md` — parallel-safe with the other P4 PRDs.

> **This PRD is one half of a split.** A single earlier in-app-purchases PRD held both the
> entitlement model and the store integration, which produced a circular dependency:
> `P1-04-persistence.md` needs entitlement state, while the purchase layer needs `P1-04`'s
> storage. That PRD was divided along the store boundary rather than rewritten: its
> counterpart `P1-07-entitlements.md` (wave 1) is **what the app knows about what the player
> owns** and needs no network; **this PRD is StoreKit, buying and restoring.**

> **Requirement numbering is append-only, and sibling PRDs cite it by number.** Requirements
> 13–16 were added after 1–12 and are among the most load-bearing in the document; they are
> numbered last rather than inserted in logical position because five sibling PRDs already
> point at these numbers:
>
> | PRD | Cites |
> |---|---|
> | `P1-01-app-scaffold.md` | Requirement 7 |
> | `P1-06-crash-reporting.md` | Requirement 7 |
> | `P4-03-theme-selection.md` | Requirements 5 and 9 |
> | `P4-04-settings.md` | Requirements 5 and 10 (its req 20); its req 21 defers its parental gate to **Requirement 12** |
> | `P5-03-release-fastlane.md` | Requirements 1, 7, 9 and 11; its reqs 26–27 and Open Question F depend on **Requirement 12** |
>
> Renumbering would silently repoint all of them. **Requirement 13 is the interface contract
> and should be read first**; Requirements 15 and 16 are what keep the four call sites
> correct, and a reader who stops before them will ship the two bugs those requirements name.

**Depends on:**

- `P1-07-entitlements.md` — the entitlement model. It publishes a **constructible**
  `Entitlements` (its Requirement 11), the `applyStoreResult(Set<String>)` mutator (its
  Requirement 14), `EntitlementProducts` with its wave-1 implementation (its Requirement 20),
  and `entitlementProductsProvider`. **Its `applyStoreResult` is in-memory only** — see
  Requirement 15.
- `P1-04-persistence.md` — the local store, through `EntitlementsStore.write`
  (its Requirement 28). **This layer is the only caller of it** — see Requirement 15.
- `P1-03-theme-system.md` — the theme object and its published accessor,
  `activeThemeProvider` (its Requirement 24). This PRD reads theme values through that
  symbol and defines no theme key; the keys it needs are Requirement 8's.
- `P4-04-settings.md` — the host. Same wave, and parallel-safe: see the host note below.

**Depended on by:** `P5-03-release-fastlane.md`, which declares the in-app purchases on the
App Store Connect record and schedules the Kids Category listing.

**Consumers of the entitlements this PRD populates:** `P4-02-open-games-list.md` (the cap)
and `P4-03-theme-selection.md` (per-theme ownership) — both read them through
`P1-07-entitlements.md`, not from here.

> **The host is settled: the Settings screen.** `Menus and UI.md` → *Where the open-game slot
> unlock is sold*: *"**The Settings screen.** The Settings screen gains a purchases section
> holding the $4.99 open-game-slot unlock and a global **Restore purchases** control. This is
> the conventional iOS placement, it keeps one parental gate in one place, and it keeps the
> purchase flow off the other menu screens."*
>
> **`P4-04-settings.md` is a wave-4 sibling, and the split holds — parallel safety survives.**
> That PRD owns the purchases section's existence and placement: the trigger. **This PRD owns
> everything the trigger presents** — the products, the prices, the purchase operation,
> restore, and the parental gate in front of them. The coupling is the named API in
> Requirement 13.

---

## Problem

The game now sells two things and has nothing to sell them with. `Tech Design.md` →
Decisions → *In-app purchases* records that "the game now sells two things": themes beyond
the two free ones, and "a **$4.99 unlock that raises the open-game cap from 3 to 100**."
`Menus and UI.md` → Decisions → *How many open games do we keep?* reads "3 by default, no
more. A $4.99 in-app purchase raises the cap to 100 open game slots."

`P1-07-entitlements.md` gives the app somewhere to hold the answer to "what does this player
own." What it cannot do is change that answer: nothing queries Apple, nothing takes money,
and a player who pays has no way to get what they paid for back on a new device.

The app is also being listed in Apple's Kids Category (`Tech Design.md` → Decisions → *Kids
category*), which puts a **parental gate** in front of any purchase flow — a constraint that
has to exist before the purchase flow is built, not be added at submission. It also makes
**parental approval the expected purchase path rather than an edge case**, which is what
Requirement 14 exists for.

It also changes a standing property of the app. `Tech Design.md` → *What the Design Docs
Already Imply* used to list "Fully offline. No backend, no network, no accounts" as locked.
That row has been **qualified rather than deleted** — see Requirement 6.

## Goal

The app can buy the products it sells and get them back. One layer, behind one named API,
queries Apple for what the player owns, runs a purchase behind a parental gate, exposes
restore, listens for transactions that resolve out of band, and **commits everything it
learns to memory and disk together** so nothing a player paid for survives only until the
next launch. Apple is the record of truth and is queried at runtime, so there is no receipt
server, no backend of our own and no account system we operate.

## Requirements

### The products

1. **The app sells exactly two things: paid themes, and a $4.99 unlock raising the
   open-game cap from 3 to 100.** No other purchasable product exists.
   *(`Tech Design.md` → Decisions → In-app purchases; `Menus and UI.md` → Decisions → How
   many open games do we keep?; `Theming.md` → Decisions → Which themes are free.)*
   *Testable:* the set of product identifiers the app queries has no member outside these
   two. Whether they are one product or two is **Open Question 1**.

2. **Both products are non-consumables, and both entitlements are permanent once bought:
   not consumed, not expiring, not re-charged on a device the player already bought them
   on.**

   > **Fenced default, from the doc's own reasoning.** `Tech Design.md` → Decisions →
   > *Entitlements — Apple stores them, no backend needed* discusses this app's restore path
   > in terms of **non-consumables** — "Restore for non-consumables is largely automatic" —
   > and describes a refunded or lapsed purchase as simply dropping out of
   > `Transaction.currentEntitlements`. Neither statement coheres unless the two products are
   > non-consumables. Consumable and subscription are ruled out. The doc does not name the
   > type in those words, so this is **stated here as the default an implementer builds to**;
   > `P5-03-release-fastlane.md` must confirm it at product creation, because App Store
   > Connect requires the type to be chosen explicitly and the choice is irreversible.

   *Testable:* an owned entitlement, cleared locally, is recovered by restore without a
   second charge; no code path treats either product as re-purchasable while held.

3. **Displayed prices are read from the store SDK at runtime and localized. No price is
   hardcoded anywhere in the app.** The price shown comes from
   `PurchaseService.productFor(...)` (Requirement 13), never from a literal.
   *(`themes.catalog.json` → `storeRequirements`: "Prices must be read from the store SDK at
   runtime, localized — never hardcoded. The $1.99 above is mock data.")* The `$4.99` in the
   docs is the price to configure in App Store Connect, not a string to render.
   *Testable:* a source scan finds no currency literal in the purchase or gating code; with
   the store stubbed to a different locale and amount, the displayed price follows the stub.

### Querying and restoring

> **Buying is Requirement 10, the gate is Requirement 12, the API is Requirement 13,
> out-of-band transactions are Requirement 14, and Requirements 15–16 govern how every one of
> those commits what it learns.** All are numbered after 1–9 for the cross-reference reason
> given at the top, not because they are peripheral.

4. **The app queries `Transaction.currentEntitlements` for what the player currently owns,
   and commits the result through Requirement 15.** A query that cannot complete surfaces as
   a failure, not as an answer of "owns nothing", and is **not** committed.

   **`Transaction.currentEntitlements`, not `Transaction.all`.** The two are not
   interchangeable: `currentEntitlements` is the set of *currently-valid* transactions, while
   `Transaction.all` is purchase **history including refunded and revoked transactions**. An
   implementation built on `Transaction.all` would grant a refunded player permanent access
   and would make `P1-07-entitlements.md`'s loss case unreachable.
   *(`Tech Design.md` → Decisions → Entitlements: "`Transaction.currentEntitlements` — the set
   of currently-valid transactions … That is the authoritative answer to 'does this player own
   this.' `Transaction.all` gives full purchase history **if it is ever needed**." This
   requirement is what "if it is ever needed" resolves to for now: not needed.)*

   **When the query runs: once at cold launch, and whenever the restore control is used.**
   The launch query is what makes `P1-07-entitlements.md` Requirement 13's `isProvisional`
   contract meaningful — that flag is `true` "until a store answer has been applied **in the
   current session**", and because that PRD's Requirement 17 makes it **non-persisted**, every
   launch starts provisional and every session must attempt one query to clear it. A design
   that queried only when Settings opened would leave the app provisional for the whole
   session on every other screen.
   *(Derived from `P1-07-entitlements.md` Requirements 13 and 17.)*

   *Scope boundary:* what happens to the value afterwards — that it is kept, that it survives
   a restart, that gating reads it rather than waiting on the network — is
   `P1-07-entitlements.md`'s (its Requirements 7, 9, 13 and 18).
   *Testable:* on cold launch with a store double reporting a known ownership set, the layer
   commits exactly once with that set; with the double failing, nothing is committed and the
   failure is reported; a source scan finds no use of `Transaction.all`.

5. **A restore-purchases control exists and is invocable, and restoring commits the Apple
   ID's current entitlements through Requirement 15.** It lives in the Settings screen's
   purchases section as a **global** control.

   > **Restore replaces; it is not additive.** An earlier draft said restore "re-establishes
   > entitlements the Apple ID holds **that are not currently reflected locally**", which
   > reads as additive — contradicting `P1-07-entitlements.md` Requirement 14, where an
   > affirmative store answer **replaces** the held state. The two diverge exactly on
   > revocation: additive semantics can never remove an entitlement, replace semantics can.
   > **This PRD follows Requirement 14: replace.** The consequence — what the app does about
   > open games above a cap that just shrank — lives in `P1-07-entitlements.md` Open
   > Question 1.

   *(`Menus and UI.md` → Where the open-game slot unlock is sold; `themes.catalog.json` →
   `storeRequirements`; `Tech Design.md` → Decisions → In-app purchases: "a restore-purchases
   path tied to the Apple ID".)*
   *Testable:* clear local entitlement state, invoke restore against a store stub reporting
   one owned product, and that entitlement is held again **and present on disk**. With an
   entitlement held locally and the stub reporting **none**, restore leaves the entitlement
   **not** held.

   > **The control is a compliance requirement, not the mechanism.** `Tech Design.md` →
   > Decisions → *Entitlements*: "Restore for non-consumables is largely automatic: signing in
   > on a new device repopulates entitlements without the player doing anything. The visible
   > **Restore purchases** control is still required by Apple's review guidelines, and
   > `AppStore.sync()` is the explicit call behind it."
   >
   > **What this changes for the implementer:** entitlements arrive on a new device from
   > Requirement 4's query, not from a player tapping Restore. Do not build the app so that a
   > fresh install shows the free tier until Restore is pressed — that is a defect, not a
   > design.

### Offline, failure, and the boundary

6. **The app launches and plays with no network and no store.** A purchase check that
   cannot complete must not block launch, block starting or resuming a game, or make the
   app show an error the player has to dismiss to keep playing.
   *(`Tech Design.md` → *What the Design Docs Already Imply* → "**Fully offline, except for
   in-app purchases.** … The exception is a StoreKit query against Apple, not a service we
   run"; → Decisions → In-app purchases.)*
   *Testable:* with every store call stubbed to fail, the app reaches the main menu, starts
   a game, plays it to a win and reopens it from the list.
   *Boundary:* what gating then uses is `P1-07-entitlements.md` Requirements 9 and 13.

7. **No backend of ours, no receipt-validation server, and no account system we operate.**
   The app talks to the platform store and to nothing else: no server of ours, no login, no
   user record. Verification happens **on device**, against Apple-signed transactions. Crash
   reports are still built and not transmitted.
   *(`Tech Design.md` → Decisions → Entitlements: "**No receipt-validation server, and no
   backend of ours.** … verified on device … On-device verification is sufficient for an app
   this size"; → Decisions → Project structure — layer-first; → Decisions → Crash reporting.)*

   *Testable:* an outbound-call scan over `lib/` finds no HTTP client and no network target
   other than the store SDK. **`P1-01-app-scaffold.md` Requirement 6 owns that scan** — it is
   written in wave 1 in exactly this form so that it still passes when this layer lands, and
   `P1-06-crash-reporting.md` Requirement 10 explicitly disclaims writing one and assigns it
   there. One owner, not several.

   > **What the crash-reporting side asserts, and why StoreKit does not weaken it.**
   > `P1-06-crash-reporting.md` Requirement 6 (the report object is never transmitted),
   > Requirement 7 (no catch site or sink references a destination, URL, host, endpoint or
   > socket), **Requirement 9** (no crash-reporting service, telemetry SDK, or network client
   > is added — the strongest, because it bans the SDK outright rather than only its use) and
   > Requirement 10 (no backend of ours, no account system). Its Requirement 16 is a separate
   > transport scan scoped to the crash-reporting files.
   >
   > **Adding StoreKit satisfies none of the things those ban.** The store SDK is not a
   > crash-reporting service, not telemetry, and not an HTTP or socket client added for
   > reporting. An earlier draft cited "`P1-06` Requirement 4" as writing the same
   > outbound-call check — that is wrong; Requirement 4 is `InMemoryCrashReportSink`, the test
   > double.
   >
   > **A Kids-category note, forward-looking and not a requirement today.**
   > `P1-06-crash-reporting.md` Open Question 1 records that in a 4+ Kids app the privacy
   > nutrition label is the *softer* of two constraints: **transmitting** personal data is
   > itself the regulated act, so a crash destination chosen later may need a consent path
   > rather than only a label update. Nothing here transmits — but it is the same category of
   > constraint Requirement 12's gate lives under, and it is why
   > `P5-03-release-fastlane.md` Requirement 30 scopes its privacy answers to "nothing
   > transmitted today".

8. **Any UI this layer adds is theme-driven like everything else** — no hardcoded colors,
   fonts, sounds, motion or asset paths. This covers the purchase surface, the price row,
   the restore control and the parental gate alike.
   *(`Theming.md` → Architectural Rule; `Tech Design.md` → Decisions → Do we add a test that
   fails on hardcoded theme values?)*

   **How this layer reaches the theme.** Through `activeThemeProvider`, published by
   `P1-03-theme-system.md` Requirement 24 in `lib/theme/theme_providers.dart` as a plain
   `Provider<Theme>` — not a `ThemeExtension` reached through `Theme.of(context)`. That
   requirement fixes which form is normative: a **widget** that must rebuild on a theme
   change uses `ref.watch(activeThemeProvider)`, while a **non-widget layer** uses
   `ref.read(...)` **inside the call**. `PurchaseService` is a service with no `BuildContext`,
   so it takes the `read` form; the price row, restore control and gate are widgets and take
   `watch`.

   **The slots this needs do not exist yet.** `P1-03-theme-system.md` Requirement 15 carries
   `surfaces.settingsCard.purchases.{sectionDivider, priceRow, restoreControl}` as
   **`deferred`**, annotated "**nothing drawn** / `P4-04` reqs 20, 22" — `2b` predates the
   Decision that added a purchases section. **Those keys must be promoted to `required`
   before this layer's UI can satisfy this requirement**, and no slot is named anywhere for
   the parental gate's own surface. Flagged, not resolved — the slot list is that PRD's.
   *Testable:* the hardcoded-theme-value test (`P1-05-theme-guard-test.md`) passes over this
   layer's source with the baseline at zero; every visual value resolves through a named key
   off `activeThemeProvider`; a source scan finds no `Theme.of(context)` in this layer.

### What is reachable at launch

9. **At launch no theme is gated, because both themes that ship are free.**
   *(`Theming.md` → Decisions → How many themes ship at launch; → Which themes are free;
   `Menus and UI.md` → Theme Selection.)*
   *Testable:* the shipped `assets/themes/` contains exactly two theme files, and their UUIDs
   are exactly the two free UUIDs in `P1-07-entitlements.md` Requirement 12. Shipping a third
   theme file, or one whose UUID is outside that set, fails this test.

   > **Why the testable is written that way.** An earlier version asserted "the number of
   > catalog entries with ownership `locked` is zero", which is **tautological** under
   > `P1-07-entitlements.md` Requirement 12: paid-ness is derived as "not one of the two free
   > UUIDs", so with only those two shipped, zero locked entries is arithmetic rather than an
   > observation. No implementation could fail it. The check above can fail.

   **The cap unlock is reachable; a theme purchase is not.** This requirement restricts themes
   only. **Consequence:** the entitlement model is built in wave 1 because the docs commit to
   it; **a theme storefront is not**, because there is no theme to sell.

### Buying, the gate, and reaching the store

10. **A purchase can be initiated for a product the app sells, and its result is committed.**
    `PurchaseService.purchase` (Requirement 13) starts a platform purchase for a named
    product, runs it to one of the store's terminal outcomes, and on success commits through
    Requirement 15 — so that a completed purchase is what produces an entitlement, rather
    than any local grant.
    *(`Menus and UI.md` → Where the open-game slot unlock is sold, which puts the unlock on
    the Settings screen and so requires it to be buyable; `Tech Design.md` → Decisions →
    In-app purchases; `P1-07-entitlements.md` Requirement 10, the matching prohibition.)*
    *Gated:* reachable only through Requirement 12's parental gate.
    *Testable — four branches, not three:*
    - **success** → committed once; the reported cap reads 100 **and the value is on disk**.
    - **cancelled** → nothing committed; the cap still reads 3.
    - **failed** → nothing committed; the cap still reads 3.
    - **pending** (Ask to Buy) → nothing committed, the operation returns a
      `PurchaseOutcome.pending` distinguishable from both success and failure, and a
      transaction arriving later through Requirement 14's listener commits the entitlement.

    *Not specified here:* what the player is **shown** for each outcome — Open Question 4.

11. **The store integration is substitutable.** Nothing outside `lib/purchase/` imports or
    calls the platform store SDK, and this layer reaches it through `StoreGateway`
    (Requirement 13) — an interface a test double replaces with no real SDK, no network and
    no store account present.
    *(**Derived, not cited** — no design doc names a test seam. Every *Testable* clause in
    this PRD and in `P1-07-entitlements.md` is written against a stubbed or failing store, and
    `Tech Design.md` → Decisions → CI — local builds only means they run on a developer
    machine with no App Store sandbox guaranteed. `P1-04-persistence.md` Requirement 13 states
    the same shape for Hive.)*
    *Testable:* the whole suite runs green with no network and no store account configured;
    an import scan finds the store plugin imported only under `lib/purchase/`.

12. **A parental gate stands in front of the purchase flow, and no purchase can be
    initiated without passing it.** The app is being listed in Apple's Kids Category, which
    requires the gate; it has to exist before the purchase flow is built.
    *(`Tech Design.md` → Decisions → Kids category: "A **parental gate** is required before
    any purchase flow and before any link that leaves the app … the gate has to exist before
    those are built rather than being added at submission.")*
    *Scope — purchases only.* The same Decision: "**The parental gate's scope is purchases
    only.** The game has no outbound links today."
    *Testable:* `PurchaseService.purchase` cannot reach `StoreGateway` without the gate having
    been passed; a test that invokes it directly without passing the gate reaches no store
    double and produces no entitlement.

    > **Ownership — exactly one PRD owns the gate, and it is this one.** `Tech Design.md`:
    > "What the gate looks like and how it challenges is a PRD's job, not this doc's."
    > `Menus and UI.md` gives the reason to keep it single — Settings is the host because it
    > "keeps **one** parental gate in **one** place."
    >
    > **The enforcement-point collision is resolved.** `P4-04-settings.md` Requirement 21 now
    > reads "The purchase control invokes `P4-05-purchase-flow.md`'s gated purchase entry
    > point, and **this surface implements no parental gate of its own**", with a testable
    > that scans its own files for any gate widget and expects none. **Enforcement sits here.**

    *Not specified here:* the concrete challenge, whether a pass is per-invocation or
    per-session, and whether restore is gated. See Open Question 5.

### The interface

13. **The public surface is named, and these are the names.** Every consumer codes against
    the members below and no consumer invents its own.

    | Name | Kind | What it is |
    |---|---|---|
    | `PurchaseService` | class | the whole of this layer's public behavior |
    | `PurchaseService.purchase(String productId)` | `Future<PurchaseOutcome>` | Requirement 10 — gated by Requirement 12 |
    | `PurchaseService.restore()` | `Future<void>` | Requirement 5 — calls `AppStore.sync()`, then commits |
    | `PurchaseService.refreshEntitlements()` | `Future<void>` | Requirement 4 — queries `currentEntitlements`, then commits |
    | `PurchaseService.productFor(String productId)` | `Future<StoreProduct?>` | Requirement 3 — the metadata the price row renders from |
    | `PurchaseOutcome` | `enum { success, pending, cancelled, failed }` | Requirement 10's four branches; `pending` is Ask to Buy |
    | `StoreProduct` | immutable value class | `id`, `localizedPrice` (pre-formatted `String` from the SDK), `localizedTitle` |
    | `StoreGateway` | interface | Requirement 11's seam — the only thing that touches the plugin |
    | `purchaseServiceProvider` | `Provider<PurchaseService>` | the single access point |

    *(**Engineering naming call, not a doc citation.** This mirrors
    `P1-07-entitlements.md` Requirement 11 and `P1-03-theme-system.md` Requirement 24, and
    follows the Riverpod idiom fixed by `P1-01-app-scaffold.md` Requirement 11 — no codegen,
    no legacy `StateNotifier`.)*

    **What this binds against, now that it is constructible.**
    `P1-07-entitlements.md` Requirement 11 publishes `const Entitlements({required
    ownedProductIds, isProvisional = true})`, `const Entitlements.free()`, value equality over
    `ownedProductIds`, and `entitlementProductsProvider`. This layer therefore needs no
    entitlement type of its own: it produces a `Set<String>` of owned product identifiers and
    hands it to `applyStoreResult(Set<String>)` (that PRD's Requirement 14), and reads
    `EntitlementProducts.openGameCapProductId` for the identifier to query and purchase.

    **Why this requirement exists.** `P4-04-settings.md` Requirement 20 says activating its
    purchase control "invokes `P4-05-purchase-flow.md`'s API (its requirements 5 and 10)" —
    and until this requirement existed, those named no API. Two agents would coin
    `PurchaseService.buy(productId)` and `StoreNotifier.purchase(id)`, both PRDs would pass
    review, and the failure would appear only at integration.

    **This layer lives at `lib/purchase/`** — settled, not provisional.
    *(`Tech Design.md` → Decisions → *Project structure — layer-first* lists
    `purchase/    ← store integration, owned by P4-05-purchase-flow` in the tree, one of "five
    more new layers".)* Note the same residual `P1-07-entitlements.md` Requirement 15 records:
    `P1-01-app-scaffold.md` Requirement 2 still builds and verifies **nine** paths, and
    `purchase/` is not among them. Routed there.

    **Product identifiers — provisional, and behind the seam.** The reverse-DNS identifier for
    the cap unlock is `com.ehrendavis.tictactoeextreme.opengames.slots100`, derived from the
    settled bundle identifier (`Tech Design.md` → Decisions → *Bundle identifier*). **It lives
    in `lib/entitlements/`, not here** — `P1-07-entitlements.md` Requirement 20 fences the
    wave-1 `EntitlementProducts` implementation that holds it, precisely because this
    requirement says the string is reached only through `openGameCapProductId`. This layer
    reads it and never writes it as a literal.
    *What is genuinely blocked is the product **structure**, not the string* — Open Question 1.

    *Testable:* a consumer can start a purchase, run a restore and read a price through
    `purchaseServiceProvider` alone; a source scan finds no second type in `lib/` modelling a
    purchase operation or a store product, and no currency or product-identifier literal in
    `lib/purchase/`.

14. **The layer listens for transactions that resolve outside a purchase call, commits them,
    and finishes every transaction it handles.** Concretely:
    - A `Transaction.updates` listener is registered **for the app's lifetime**, started at
      launch before any purchase is possible, not opened per purchase call.
    - Any transaction arriving through it — an Ask to Buy approval, a purchase completed on
      another device, a transaction the store retries — triggers a commit through
      Requirement 15, sourced per Requirement 16.
    - **Every transaction the layer handles is finished** once committed, from the listener
      and from `PurchaseService.purchase` alike. An unfinished transaction is redelivered by
      StoreKit indefinitely.

    > **Why this is a requirement and not an edge case.** The app is in the **Kids Category**,
    > so **parental approval is the expected purchase path, not an exception.** An Ask to Buy
    > purchase resolves minutes or days later, out of band, very likely in a different app
    > session — after `PurchaseService.purchase` has already returned.
    >
    > **The failure this prevents:** the natural implementation awaits the purchase call,
    > treats anything that is not success as non-success, and returns. The parent approves,
    > the transaction arrives later with nobody listening, and **the child never receives what
    > was bought** — while every other test in this PRD passes.

    *(**Derived, not cited.** No design doc names `Transaction.updates` or transaction
    finishing. It is forced by three cited things together: the Kids Category decision, which
    makes deferred purchases routine; `Tech Design.md` → Decisions → *Entitlements*, which
    puts the app on StoreKit 2 semantics; and `P1-07-entitlements.md` Requirement 14, which
    makes `applyStoreResult` the only way entitlement state may change.)*
    *Testable:* with the store double delivering a transaction through the updates stream with
    no purchase call in flight, the entitlement is committed and present on disk; every
    transaction the double issues is observed finished; a purchase driven to `pending` and
    then approved through the stream ends with the entitlement held.

### Committing what the store says

15. **Applying and persisting happen together, through one operation, and that operation is
    the only place either is called.** Every store answer this layer accepts is committed by
    a single internal operation — call it `PurchaseService._commit(Set<String>
    ownedProductIds)` — which:
    - calls `applyStoreResult(ownedProductIds)` on `P1-07-entitlements.md`'s notifier
      (its Requirement 14), updating in-memory state; **and**
    - writes the resulting `Entitlements` through `EntitlementsStore.write`
      (`P1-04-persistence.md` Requirement 28).

    **Requirements 4, 5, 10 and 14 all commit through this operation and never call either
    half directly.**

    > **Why one operation rather than two calls at four sites.**
    > `P1-07-entitlements.md` Requirement 19 records that its `applyStoreResult` is
    > **in-memory only**, because `P1-04-persistence.md` Requirement 19's testable makes
    > `EntitlementsStore.write` "reachable only from the purchase layer". So persistence is
    > this layer's job — and this layer has **four** places that accept a store answer.
    >
    > **The failure this prevents:** miss the write at any one of them and the entitlement
    > holds for the session and is gone on relaunch. A player buys the cap unlock, sees 100
    > slots, quits, reopens, and has 3 — with no error and nothing in any log. It is the same
    > shape as "pick Classic and get Neon" one layer over: everything works until the app
    > restarts. Four call sites means four chances to forget; one operation means zero.

    *(Routed here by `P1-07-entitlements.md` Requirement 19, which names the hazard and states
    it cannot fix it from that side.)*
    *Testable:* a source scan finds `applyStoreResult` called from exactly one place in
    `lib/purchase/`, and `EntitlementsStore.write` called from exactly one place — the same
    one. For each of Requirements 4, 5, 10 and 14, driving that path to success leaves the
    entitlement **both** readable in the session **and** present in the store, verified by
    rebuilding the store from disk.

16. **Every commit is sourced from a fresh `currentEntitlements` read, and a stale answer
    never overwrites a newer one.** Two rules:

    **(a) Source.** A commit's argument is always a freshly-read full
    `currentEntitlements` snapshot — never a set derived from a single delivered transaction.
    Requirement 14's listener therefore *triggers a re-read* and commits that, rather than
    constructing a set from the transaction it received.

    **(b) Ordering.** Each answer carries a sequence number assigned when its read was
    **issued** — not when it resolved. `_commit` ignores any answer whose sequence is lower
    than the highest already committed.

    > **The race this closes.** Requirement 4's launch query and Requirement 14's listener are
    > independent and can be in flight together. Under replace semantics
    > (`P1-07-entitlements.md` Requirement 14), whichever lands *second* wins — so a slow
    > launch query resolving after the listener applies the **older** answer and silently
    > revokes an entitlement the player just obtained. Sequencing by *issue* time rather than
    > arrival time is what makes the older answer identifiable: the launch query was issued
    > first, so it loses even though it landed last.
    >
    > **What it looks like in the wild:** a player restores purchases, a store answer lands
    > moments later carrying an older snapshot, and their entitlements silently revert. It is
    > timing-dependent, it will not reproduce reliably, and it produces a support report that
    > reads as "it forgot what I bought."
    >
    > Rule (a) is what makes rule (b) sufficient: if every commit carries a full snapshot,
    > ordering is the only thing that can go wrong. If commits carried partial sets derived
    > from individual transactions, no ordering rule would be enough.

    *(**Derived, not cited.** `P1-07-entitlements.md` Requirement 21 fences arrival-order
    application on its side, states that nothing on its surface carries a sequence number or
    timestamp to guard with, and routes the guard here as the only layer that knows which
    answer is newer.)*
    *Testable:* issue read A, issue read B, resolve B then A — the committed state is B's, and
    A is dropped. Deliver a transaction through the updates stream and assert the committed
    argument equals a full `currentEntitlements` snapshot rather than a set derived from that
    transaction alone.

## What this does and does not change about "fully offline"

**Changes:** the app makes network calls (StoreKit needs them to query, purchase and
restore); it is tied to an Apple ID for the entitlement query and restore; "no accounts" is
no longer literally true at the platform level.

**Does not change:**

- **There is still no backend of our own, and no receipt server.** The one exception is "a
  StoreKit query against Apple, not a service we run", verified on device (Requirement 7).
- **There is still no account system we operate.** No sign-in, no user record, no profile.
- **Gameplay is still fully offline.** The game launches, plays and saves with the network
  off (Requirement 6).
- **Crash reports are still not transmitted.** StoreKit being allowed does not make a report
  destination allowed — see Requirement 7's note.
- **`storage/` is still local persistence only.** The write in Requirement 15 is a local
  write like any other.

## Out of Scope

- **The entitlement model** — the free-tier defaults, the per-theme query, the cap value, the
  Riverpod exposure, the seeding at launch and the Apple-is-the-record rule:
  `P1-07-entitlements.md`. This PRD produces store results and commits them.
- **The store's keys and format** — `P1-04-persistence.md`. This PRD calls
  `EntitlementsStore.write` and nothing else.
- **The Settings screen itself** — `P4-04-settings.md`. That PRD owns the trigger; this one
  owns what the trigger presents.
- **A theme storefront.** No paid theme exists (Requirement 9).
- **Purchase outcome messaging** — Requirement 10 requires the four outcomes as mechanism and
  stops there. Open Question 4.
- **Theme materialization, the accessor, and the theme slot list** — `P1-03-theme-system.md`,
  including promoting `surfaces.settingsCard.purchases.*` out of `deferred` (Requirement 8).
- **The theme selection overlay's rows, badges and price button** —
  `P4-03-theme-selection.md`. The *Restore purchases* control is global and lives on Settings.
- **The open-games list and how the cap is displayed or enforced** —
  `P4-02-open-games-list.md`.
- **The App Store Connect record: the product entries, their identifiers, their price tiers,
  the Kids Category listing and the age rating** — `P5-03-release-fastlane.md`.
  **The parental gate itself is not out of scope and did not go there** — the *listing* is
  that PRD's; the **gate is Requirement 12 of this one**.
- **Android billing.** Every monetization statement in the docs names StoreKit and the Apple
  ID; iOS is the primary target with Android "far future".

## Open Questions

### 1. Are the 100-slot unlock and paid themes separate products, or a bundle?

**With the user.** Nothing states whether paid themes are one product, one product per theme,
or bundled with the slot unlock — and nothing gives a paid theme a price (the `$1.99` in
`themes.catalog.json` is mock data). `P1-07-entitlements.md` Requirement 2 and its
`EntitlementProducts` seam keep all three shapes reachable, and its Requirement 20 fences the
wave-1 implementation without assuming a structure. `P5-03-release-fastlane.md` Requirement 9
cannot be completed until this is answered.

### 2. Answered — where the $4.99 open-game slot unlock gets sold

**Closed.** `Menus and UI.md` names **the Settings screen**, which gains a purchases section
holding the unlock and a global *Restore purchases* control. Kept as a stub for numbering
stability.

### 3. Answered — do purchases need a receipt-validation step?

**Closed.** `Tech Design.md` → Decisions → *Entitlements*: "**No receipt-validation server,
and no backend of ours.**" On-device verification "is sufficient for an app this size."
Requirement 7 states it.

### 4. With the user — the plugin, and purchase-outcome messaging

- **Which Flutter plugin sits behind `StoreGateway`.** **StoreKit 2 semantics are
  load-bearing here**: Requirement 4 needs `Transaction.currentEntitlements`, Requirement 5
  needs `AppStore.sync()`, Requirement 14 needs `Transaction.updates` and transaction
  finishing, and Requirement 16 needs to issue a `currentEntitlements` read on demand. Not
  every Flutter plugin surfaces all four. Requirement 11's seam makes the choice swappable,
  but **something has to sit behind it on day one**. **This is the largest single thing
  standing between this PRD and a build.**
- **What the player is shown for each of Requirement 10's four outcomes.** Pending most needs
  copy, because the player is told to wait for someone else — and under the Kids Category
  that is the common case, not the rare one.

### 5. With the user — the parental gate: challenge, lifetime, and whether restore is gated

Requirement 12 requires the gate, settles that this PRD owns it, and — since
`P4-04-settings.md` Requirement 21 was corrected to defer here — settles that **enforcement
sits inside the purchase operation**. Three things remain:

- **What the challenge is.** No design doc describes one; Apple requires that a gate exist and
  be non-trivial for a young child, not that it take a particular form.
- **Whether a pass is per-invocation or per-session.**
- **Whether restore is gated.** Restore spends no money, which argues no; it is a purchases
  control on the same section, which argues yes.

> **Closed since an earlier revision:** *where enforcement sits.* `P4-04-settings.md` now
> states it "implements no parental gate of its own" and invokes this one's gated entry point.

### 6. Related, and with the user on `P1-07-entitlements.md`: does the first frame wait?

Not this PRD's to answer, but Requirement 4's launch query is on the other side of it.
`P1-07-entitlements.md` Requirement 18 fences that startup **awaits** the entitlements disk
read before the first frame, and its Open Question 7 escalates whether that is the right
trade: waiting costs every launch a small read; not waiting means **a paying player can see
their purchases missing on every launch** until the read lands.

Whichever way it goes, Requirement 4 is unchanged — the store query is a separate, slower
thing that happens after the seed and clears `isProvisional`. Recorded here so a reader of
this PRD does not resolve it locally.

### 7. Gaps found while writing this PRD (author-raised)

- **Who declares a richer store-result type.** Requirement 15's `_commit` and
  `applyStoreResult` both take `Set<String>` today. `P1-07-entitlements.md` Open Question 4
  keeps open whether a richer type is wanted and who declares it; Requirement 16 records what
  one would buy — the sequence number is currently this layer's private concern rather than
  part of the hand-off.
- **`surfaces.settingsCard.purchases.*` is still `deferred`** in
  `P1-03-theme-system.md` Requirement 15, and no slot exists for the parental gate's surface
  at all. Requirement 8 cannot be satisfied until those are promoted.
- **The handoff's paywall rationale quotes a superseded decision**, and draws the *Restore
  purchases* link on the theme overlay, which `Menus and UI.md` has since moved to Settings.
  The handoff is read-only, so this PRD records the drift rather than correcting it.

### 8. One consumer PRD is still stale about this one — a revision needs routing

**`P5-03-release-fastlane.md`** states, at its Requirement 27 and Open Question F, that
"neither of those PRDs mentions a parental gate or the Kids Category at all, so nothing
currently schedules the work." **Requirement 12 here schedules it**, this PRD's Problem
section names the Kids Category directly, and Requirement 14 exists because of it. Open
Question F can be narrowed to what is genuinely unscheduled — the gate's challenge design,
its lifetime, and whether restore is gated (Open Question 5).

> **Resolved since an earlier revision:** `P4-04-settings.md` no longer claims this PRD has no
> parental-gate requirement, and its two bad *"`P4-05`, per requirement 21"* self-citations
> are gone.
