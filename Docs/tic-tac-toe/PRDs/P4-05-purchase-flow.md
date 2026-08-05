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

> **Requirement numbering is deliberately non-contiguous with document order.** Requirements
> 10, 11 and 12 were added after 1–9 were written and are among the most load-bearing in the
> document. They are numbered last rather than inserted in logical position because **four
> sibling PRDs cite this one's requirements by number**: `P1-01-app-scaffold.md` and
> `P1-06-crash-reporting.md` cite **Requirement 7**, `P4-03-theme-selection.md` cites
> **Requirements 5 and 9**, and `P5-03-release-fastlane.md` cites **Requirements 7, 9 and
> 11**. Renumbering would silently repoint all of them. Read the *Buying, the gate, and
> reaching the store* section as though it sat beside *Querying and restoring*.

**Depends on:**

- `P1-07-entitlements.md` — the entitlement model, the free-tier defaults, the query
  interface, and the rule that Apple is the record of truth while the local copy is an
  offline convenience. This PRD produces the store results that layer holds; it defines none
  of the model.
- `P1-04-persistence.md` — the local store. That PRD owns where and how entitlement state is
  written.
- `P1-03-theme-system.md` — the theme catalog and theme materialization. This PRD attaches
  ownership *beside* a theme, never inside its definition.
- `P4-04-settings.md` — the host. Same wave, and parallel-safe: see the host note below.

**Depended on by:** `P5-03-release-fastlane.md`, which declares the in-app purchases on the
App Store Connect record.

**Consumers of the entitlements this PRD populates:** `P4-02-open-games-list.md` (the cap)
and `P4-03-theme-selection.md` (per-theme ownership) — both read them through
`P1-07-entitlements.md`, not from here.

> **The host is settled: the Settings screen.** `Menus and UI.md` → *Where the open-game slot
> unlock is sold* now reads: *"**The Settings screen.** The Settings screen gains a purchases
> section holding the $4.99 open-game-slot unlock and a global **Restore purchases** control.
> This is the conventional iOS placement, it keeps one parental gate in one place, and it
> keeps the purchase flow off the other menu screens."* The same doc records the consequence:
> the Settings screen "now carries more than the three toggles specified in **Settings Menu**
> above."
>
> **`P4-04-settings.md` is a wave-4 sibling, and the split holds — parallel safety survives.**
> That PRD owns the purchases section's existence and placement: the trigger, and where it
> sits among the toggles. **This PRD owns everything the trigger presents** — the products,
> the prices, the purchase operation, restore, and the parental gate in front of them
> (Requirements 3, 5, 10, 12). The coupling is a one-line interface rather than a screen, so
> neither PRD needs the other built in order to be built, and neither can silently change the
> other's behavior.

---

## Problem

The game now sells two things and has nothing to sell them with. `Tech Design.md` →
Decisions → *In-app purchases* records that "the game now sells two things": themes beyond
the two free ones, and "a **$4.99 unlock that raises the open-game cap from 3 to 100**."
`Menus and UI.md` → Decisions → *How many open games do we keep?* now reads "3 by default,
no more. A $4.99 in-app purchase raises the cap to 100 open game slots."

`P1-07-entitlements.md` gives the app somewhere to hold the answer to "what does this player
own." What it cannot do is change that answer: nothing queries Apple, nothing takes money,
and a player who pays has no way to get what they paid for back on a new device — which the
approved handoff already draws as a *Restore purchases* footer link, "required by both app
stores once you charge for anything" (`design_handoff_game_ui/README.md` → *2a*).

The app is also being listed in Apple's Kids Category (`Tech Design.md` → Decisions → *Kids
category*), which puts a **parental gate** in front of any purchase flow — a constraint that
has to exist before the purchase flow is built, not be added at submission.

It also changes a standing property of the app. `Tech Design.md` → *What the Design Docs
Already Imply* used to list "Fully offline. No backend, no network, no accounts" as locked.
That row has been **qualified rather than deleted** — see Requirement 6 and *What this does
and does not change about "fully offline"* below.

## Goal

The app can buy the products it sells and get them back. One layer queries Apple for what
the player owns, runs a purchase behind a parental gate, exposes restore, hands what it
learns to the entitlement layer, and never blocks launch or gameplay when the store cannot
be reached. Apple is the record of truth and is queried at runtime, so there is no receipt
server, no backend of our own and no account system we operate.

## Requirements

### The products

1. **The app sells exactly two things: paid themes, and a $4.99 unlock raising the
   open-game cap from 3 to 100.** No other purchasable product exists.
   *(`Tech Design.md` → Decisions → In-app purchases: "The game now sells two things …
   Themes beyond the two free ones (Neon and Classic Red vs Blue), and a $4.99 unlock that
   raises the open-game cap from 3 to 100"; `Menus and UI.md` → Decisions → How many open
   games do we keep?; `Theming.md` → Decisions → Which themes are free.)*
   *Testable:* the set of product identifiers the app queries has no member outside these
   two. Whether they are one product or two is **Open Question 1** — see
   `P1-07-entitlements.md` Requirement 2.

2. **Both entitlements behave as permanent once bought: not consumed, not expiring, not
   re-charged on a device the player already bought them on.**

   > **Grounded, where this was previously the author's derivation.** `Tech Design.md` →
   > Decisions → *Entitlements — Apple stores them, no backend needed* discusses this app's
   > restore path in terms of **non-consumables** — "Restore for non-consumables is largely
   > automatic: signing in on a new device repopulates entitlements without the player doing
   > anything" — and describes a refunded or lapsed purchase as simply dropping out of
   > `Transaction.currentEntitlements`. Neither statement coheres unless the two products are
   > non-consumables, which is exactly what makes them permanent and restorable. The doc does
   > not name the product type in those words, so this remains a reading rather than a
   > quotation — but it is now the **doc's** reading, not the author's, and it rules out
   > consumable and subscription. See Open Question 4.

   *Testable:* an owned entitlement, cleared locally, is recovered by restore without a
   second charge.

3. **Displayed prices are read from the store SDK at runtime and localized. No price is
   hardcoded anywhere in the app.**
   *(`themes.catalog.json` → `storeRequirements`: "Prices must be read from the store SDK at
   runtime, localized — never hardcoded. The $1.99 above is mock data.")* The `$4.99` in
   `Menus and UI.md` and `Tech Design.md` is the price to configure in App Store Connect
   (`P5-03-release-fastlane.md`), not a string to render.
   *Testable:* a source scan finds no currency literal in the purchase or gating code; with
   the store stubbed to a different locale and amount, the displayed price follows the stub.

### Querying and restoring

> **Buying itself is Requirement 10 and the gate is Requirement 12**, in the *Buying, the
> gate, and reaching the store* section below. They are numbered last for the
> cross-reference reason given at the top of this document, not because they are peripheral.

4. **The app queries Apple for what the player owns, and hands the result to the entitlement
   layer.** A query that cannot complete surfaces as a failure, not as an answer of "owns
   nothing".
   *(`Tech Design.md` → Decisions → Entitlements — Apple stores them, no backend needed:
   "StoreKit provides `Transaction.currentEntitlements` — the set of currently-valid
   transactions for this app under the signed-in Apple ID, cryptographically signed by Apple
   and verified on device. That is the authoritative answer to 'does this player own this.'
   `Transaction.all` gives full purchase history if it is ever needed."; → Decisions →
   In-app purchases, for what is sold.)*
   *Scope boundary:* what happens to the answer afterwards — that it is kept locally as an
   offline convenience, that it survives a restart, and that gating reads the local copy
   rather than waiting on the network — is **`P1-07-entitlements.md`'s** (its Requirements 7
   and 9), not this PRD's. An earlier draft of this requirement restated that half and made
   a third claimant to it; see `P1-07-entitlements.md` Open Question 4.
   *Testable:* with a store double reporting a known product set and a known ownership set,
   the layer completes a query and hands both to the entitlement layer; with the double
   failing, the layer reports a failure and hands over nothing. The offline-gating
   consequence is tested by `P1-07-entitlements.md` Requirement 9, not here.

5. **A restore-purchases control exists and is invocable, and restoring re-establishes
   entitlements the Apple ID holds that are not currently reflected locally.** It lives in
   the Settings screen's purchases section as a **global** control.
   *(`Menus and UI.md` → Where the open-game slot unlock is sold: the Settings screen "gains
   a purchases section holding the $4.99 open-game-slot unlock and a global **Restore
   purchases** control"; `themes.catalog.json` → `storeRequirements`; `Tech Design.md` →
   Decisions → In-app purchases: "a restore-purchases path tied to the Apple ID".)*
   *Testable:* clear local entitlement state, invoke restore against a store stub reporting
   one owned product, and that entitlement is held again.

   > **The control is a compliance requirement, not the mechanism.** `Tech Design.md` →
   > Decisions → *Entitlements — Apple stores them, no backend needed* is explicit:
   > "Restore for non-consumables is largely automatic: signing in on a new device
   > repopulates entitlements without the player doing anything. The visible **Restore
   > purchases** control is still required by Apple's review guidelines, and
   > `AppStore.sync()` is the explicit call behind it — so the control is a compliance
   > requirement more than a functional one."
   >
   > **What this changes for the implementer:** entitlements arrive on a new device from
   > Requirement 4's query, not from a player tapping Restore. Do not build the app so that
   > a fresh install shows the free tier until Restore is pressed — that would be a defect,
   > not a design. The control must still exist and must still call `AppStore.sync()`.

   *Not specified here:* what a restore that returns **fewer** entitlements than are held
   locally does — see `P1-07-entitlements.md` **Open Question 1**, whose *mechanism* is now
   settled even though the app's response to it is not.

### Offline, failure, and the boundary

6. **The app launches and plays with no network and no store.** A purchase check that
   cannot complete must not block launch, block starting or resuming a game, or make the
   app show an error the player has to dismiss to keep playing.
   *(`Tech Design.md` → *What the Design Docs Already Imply* → "**Fully offline, except for
   in-app purchases.** No backend, no network, no accounts — StoreKit is the one exception …
   The exception is a StoreKit query against Apple, not a service we run"; → Decisions →
   In-app purchases.)*
   *Testable:* with every store call stubbed to fail, the app reaches the main menu, starts
   a game, plays it to a win and reopens it from the list.
   *Boundary:* what gating then uses is `P1-07-entitlements.md` Requirement 9 — a failed or
   timed-out query is not an answer of "owns nothing".

7. **No backend of ours, no receipt-validation server, and no account system we operate.**
   The app talks to the platform store and to nothing else: no server of ours, no login, no
   user record. Verification of what the player owns happens **on device**, against
   Apple-signed transactions. Crash reports are still built and not transmitted.
   *(`Tech Design.md` → Decisions → Entitlements — Apple stores them, no backend needed: "**No
   receipt-validation server, and no backend of ours.** … cryptographically signed by Apple
   and verified on device … On-device verification is sufficient for an app this size"; →
   Decisions → Project structure — layer-first: "There is still **no backend data layer**:
   nothing in the app talks to a server"; → Decisions → Crash reporting.)*
   *Testable:* an outbound-call scan over `lib/` finds no HTTP client and no network target
   other than the store SDK. `P1-01-app-scaffold.md` Requirement 6 and
   `P1-06-crash-reporting.md` Requirement 4 write the same check in the same form in wave 1,
   so those checks still pass when this layer lands.

8. **Any UI this layer adds is theme-driven like everything else** — no hardcoded colors,
   fonts, sounds, motion or asset paths. This covers the purchase surface and the parental
   gate alike.
   *(`Theming.md` → Architectural Rule; `Tech Design.md` → Decisions → Do we add a test
   that fails on hardcoded theme values?)*
   *Testable:* the hardcoded-theme-value test (`P1-05-theme-guard-test.md`) passes over this
   layer's source with the baseline at zero.

### What is reachable at launch

9. **At launch the catalog contains zero locked themes, because both themes that ship are
   free.** Two themes ship — Neon and Classic Red vs Blue — and both are free, so no theme
   is gated and there is no theme purchase to reach.
   *(`Theming.md` → Decisions → How many themes ship at launch: "Two — Neon and Classic Red
   vs Blue"; → Decisions → Which themes are free; `Menus and UI.md` → Theme Selection.)*
   *Testable:* on a launch build, the number of catalog entries with ownership `locked` is
   zero.
   **The cap unlock is reachable; a theme purchase is not.** The open-game cap unlock is a
   product the app sells (Requirement 1), can buy (Requirement 10), and now has a settled
   home — the Settings screen's purchases section. This requirement says only that *no theme*
   is purchasable at launch; it does not restrict the cap unlock's reachability.
   **Consequence:** the labelling and entitlement model (`P1-07-entitlements.md`
   Requirements 2, 4, 5 and 6) is built in wave 1 because the docs commit to it; **a theme
   storefront is not**, because there is no theme to sell. See *Out of Scope*.

### Buying, the gate, and reaching the store

10. **A purchase can be initiated for a product the app sells, and its result is applied to
    entitlement state.** The layer exposes an operation that starts a platform purchase for
    a named product, runs it to one of the store's terminal outcomes, and on success hands
    the resulting entitlement to `P1-07-entitlements.md` through the boundary its
    Requirement 10 defines — so that a completed purchase is what produces an entitlement,
    rather than any local grant. Without this operation the app declares products for sale
    that cannot be bought.
    *(`Menus and UI.md` → Where the open-game slot unlock is sold, which puts the unlock on
    the Settings screen and so requires it to be buyable; `Tech Design.md` → Decisions →
    In-app purchases, which names StoreKit and what is sold; `P1-07-entitlements.md`
    Requirement 10, which requires every entitlement to originate in a store result and
    therefore presumes this operation exists without specifying it.)*
    *Gated:* the purchase operation is reachable only through Requirement 12's parental gate.
    *Testable:* with a store double reporting a successful purchase of the cap unlock,
    invoking the purchase operation leaves `P1-07-entitlements.md`'s reported cap at 100;
    with the double reporting failure or cancellation, the cap still reads 3 and no
    entitlement is held.
    *Not specified here:* what the player is shown for each outcome — cancelled, declined,
    pending (Ask to Buy) and errored are four different results and no doc describes any of
    them. See Open Question 4.

11. **The store integration is substitutable.** Nothing outside this layer imports or calls
    the platform store SDK, and this layer reaches it through an interface a test double can
    replace with no real SDK, no network and no store account present.
    *(**Derived, not cited** — no design doc names a test seam. It is the shape the cited
    decisions force: every *Testable* clause in this PRD and in `P1-07-entitlements.md` is
    written against a stubbed or failing store, and `Tech Design.md` → Decisions → CI — local
    builds only means they run on a developer machine with no App Store sandbox guaranteed.
    `P1-04-persistence.md` Requirement 13 already states the same shape for Hive — "the
    repository can be substituted in tests without Hive" — so this is the established
    pattern, not a new one.)*
    *Testable:* the whole suite runs green with no network and no store account configured;
    a source scan finds no store-plugin import outside this layer.
    *Why it is load-bearing:* if the plugin is called directly from the entitlement notifier,
    none of the stubbed-store tests in this PRD or in `P1-07-entitlements.md` can be written
    at all.

12. **A parental gate stands in front of the purchase flow, and no purchase can be
    initiated without passing it.** The app is being listed in Apple's Kids Category, which
    requires the gate; it has to exist before the purchase flow is built rather than be
    added at submission.
    *(`Tech Design.md` → Decisions → Kids category: "**The app will be listed in Apple's Kids
    Category.** … A **parental gate** is required before any purchase flow and before any
    link that leaves the app … These reach the purchase flow and theme-selection features
    directly, and the gate has to exist before those are built rather than being added at
    submission.")*
    *Scope — purchases only.* The same Decision: "**The parental gate's scope is purchases
    only.** The game has no outbound links today — no in-app support URL, no social links, no
    advertising — so purchases are the only trigger that currently exists. If an outbound
    link is ever added, it needs the gate too — that is a thing to remember rather than a
    thing already handled." Nothing else in the app is gated by this requirement.
    *Testable:* the purchase operation (Requirement 10) cannot be reached without the gate
    having been passed; a test that invokes it directly without passing the gate reaches no
    store double and produces no entitlement.

    > **Ownership — exactly one PRD owns the gate, and it is this one.** `Tech Design.md`
    > assigns the design explicitly: "What the gate looks like and how it challenges is a
    > PRD's job, not this doc's." `Menus and UI.md` gives the reason to keep it single —
    > Settings is the host because it "keeps **one** parental gate in **one** place." Under
    > the host/trigger split above, `P4-04-settings.md` owns the purchases section that hosts
    > the trigger, and **this PRD owns the gate's design and behavior**, because the gate is
    > part of what the trigger presents. `P4-04-settings.md` should defer to this requirement
    > rather than specify a gate of its own.

    *Not specified here:* the concrete challenge. Apple mandates that a gate exist, not what
    it asks, and no design doc describes one. See Open Question 4.

## What this does and does not change about "fully offline"

Recorded here because `Tech Design.md` qualified that row rather than deleting it, and
because the PRDs written before the amendment were written under the unqualified version.

**Changes:**

- The app now makes network calls. StoreKit needs the network to query products, to
  purchase, and to restore.
- The app is now tied to an Apple ID for one purpose — the entitlement query and restore.
  That is the account the entitlement belongs to.
- "No accounts" is no longer literally true at the platform level.

**Does not change:**

- **There is still no backend of our own, and no receipt server.** The one exception is "a
  StoreKit query against Apple, not a service we run" (`Tech Design.md` → *What the Design
  Docs Already Imply*), verified on device (Requirement 7).
- **There is still no account system we operate.** No sign-in, no user record, no profile.
  The Apple ID is Apple's, and the app never sees credentials.
- **Gameplay is still fully offline.** Two players, one phone; the game launches, plays and
  saves with the network off (Requirement 6).
- **Crash reports are still not transmitted.** `Tech Design.md` → Decisions → Crash
  reporting is untouched by this; StoreKit being allowed does not make a report destination
  allowed.
- **`storage/` is still local persistence only.** Keeping entitlement state is a local write
  like any other; no data layer talks to a network.

## Out of Scope

- **The entitlement model** — the free-tier defaults, the per-theme `free`/`owned`/`locked`
  query, the cap value, the Riverpod exposure, the local copy and the Apple-is-the-record
  rule: `P1-07-entitlements.md`. This PRD produces store results; that one holds them.
- **The Settings screen itself** — the purchases section's placement among the toggles, and
  the screen's own layout and styling: `P4-04-settings.md`. That PRD owns the trigger; this
  one owns what the trigger presents, including the parental gate (Requirement 12).
- **A theme storefront.** With two themes shipping and both free (Requirement 9), there is
  no paid theme to sell, no purchase sheet to design for one, and no product identifier for
  one. Requirement 10 builds the operation; it does not build a theme storefront around it.
  The handoff's Splat and Dinosaurs rows are explicitly placeholders — "their art, sound and
  animation sets do not exist … Do not ship them as designed"
  (`design_handoff_game_ui/README.md` → *2a* → The four themes shown).
- **Purchase outcome messaging** — what a cancelled, declined, pending or errored purchase
  shows the player. Requirement 10 stops at the operation and its result. Open Question 4.
- **Theme materialization, the theme object, YAML loading and UUID identity** —
  `P1-03-theme-system.md`.
- **Where entitlement values are stored** — `P1-04-persistence.md`.
- **The theme selection overlay's rows, badges and price button** —
  `P4-03-theme-selection.md`. Note that the *Restore purchases* control is now global and
  lives on Settings (Requirement 5), not on that overlay.
- **The open-games list, its delete action, and how the cap is displayed or enforced in the
  UI** — `P4-02-open-games-list.md`.
- **The App Store Connect record: the product entries, their identifiers, their price tiers,
  the Kids Category listing and the age rating** — `P5-03-release-fastlane.md`.
- **What happens when a player at the cap starts a new game** — refuse, or replace the
  oldest. Still unsettled and carried by `P1-04-persistence.md` → Open Questions 3 and
  `P4-02-open-games-list.md`. Now that the unlock has a home on Settings, "offer the unlock"
  remains a candidate but is not thereby chosen.
- **Android billing.** Every monetization statement in the docs names StoreKit and the Apple
  ID (`Tech Design.md` → Decisions → In-app purchases), and iOS is the primary target with
  Android "far future" (→ Decisions → Device support). No Android store work is specified
  here. See Open Question 4.

## Open Questions

### 1. Are the 100-slot unlock and paid themes separate products, or a bundle?

The docs are silent. `Tech Design.md` → Decisions → *In-app purchases* says "the game now
sells two things" and names them, and `Menus and UI.md` prices one of them at $4.99. Nothing
states whether paid themes are one product, one product per theme, or bundled with the slot
unlock — and nothing gives a paid theme a price at all (the `$1.99` in
`themes.catalog.json` is labelled mock data). `P1-07-entitlements.md` Requirement 2 is
written so either shape stays reachable, and Requirement 10 above takes a product identifier
rather than assuming a fixed set.

### 2. Answered — where the $4.99 open-game slot unlock gets sold

**Closed.** `Menus and UI.md` → *Where the open-game slot unlock is sold* now names **the
Settings screen**, which gains a purchases section holding the unlock and a global *Restore
purchases* control. Kept as a stub so the trail stays visible and the numbering below stays
stable. The host/trigger split this PRD adopted while the question was open needs no change
now that it is answered — see the host note at the top, and Requirement 12's ownership note
for what that means for the parental gate.

### 3. Answered — do purchases need a receipt-validation step?

**Closed.** `Tech Design.md` → Decisions → *Entitlements — Apple stores them, no backend
needed*: "**No receipt-validation server, and no backend of ours.**"
`Transaction.currentEntitlements` is cryptographically signed by Apple and verified on
device, and "on-device verification is sufficient for an app this size." Requirement 7 now
states this rather than flagging it, and it settles the tension this question previously
raised against → Decisions → *Project structure — layer-first*: there is no backend, and
none is needed.

### 4. Gaps found while writing this PRD (author-raised, not asked by the docs)

Each is something an implementer would otherwise have to guess. None is resolved here.

- **No product identifiers exist.** No doc names a product ID for either product, and this
  PRD invents none. Something must, before the store can be queried or a purchase started
  (`P5-03-release-fastlane.md` registers them). Requirement 10 is written to take an
  identifier, not to know one.
- **The product type is now narrowed, not named.** `Tech Design.md` → Decisions →
  *Entitlements* discusses restore in terms of non-consumables and describes entitlements
  dropping out of `currentEntitlements`, which rules out consumable and subscription and is
  why Requirement 2 is now grounded rather than derived. What the doc still does not do is
  state "both products are non-consumable" as a Decision, and App Store Connect requires that
  type to be chosen explicitly at product creation (`P5-03-release-fastlane.md`).
- **How the app reaches StoreKit from Flutter is not decided.** The docs name StoreKit
  (`Tech Design.md` → Decisions → In-app purchases, → Entitlements) and name a package for
  audio, persistence and state management — but not for purchases. A plugin choice is a
  Decision that has not been made; note that the entitlements Decision names StoreKit 2 APIs
  (`Transaction.currentEntitlements`, `AppStore.sync()`), which not every Flutter plugin
  surfaces. Requirement 11 makes the choice swappable without making it.
- **What the parental gate's challenge actually is.** Requirement 12 requires the gate and
  assigns its ownership; `Tech Design.md` says outright that "what the gate looks like and
  how it challenges is a PRD's job, not this doc's", and no design doc describes one. Apple
  requires that a gate exist and be non-trivial for a child, not that it take a particular
  form. The concrete challenge is undesigned, and it is this PRD's to design once someone
  decides what it should be.
- **Whether reaching the cap offers the unlock.** A third candidate answer to the still-open
  "what happens at the cap" question (`P1-04-persistence.md` → Open Questions 3), alongside
  refuse and replace-oldest. The unlock now has a home on Settings, which makes "send them to
  Settings" a fourth. Nobody has chosen.
- **What a failed or cancelled purchase shows the player.** Cancelled, declined, pending
  (Ask to Buy) and errored are four different outcomes; no doc describes any of them, and no
  modal for them is designed. Requirement 10 requires the operation to reach each outcome
  and stops there.
- **The handoff's rationale for the paywall now quotes a superseded decision.**
  `design_handoff_game_ui/README.md` → *2a* justifies its ownership states with
  "Per `Theming.md` this is a *direction*, not current scope: 'all themes available from the
  start… no monetization work now.'" `Theming.md` no longer says that. The drawn states are
  now live scope; the paragraph explaining them away is stale. The handoff also draws the
  *Restore purchases* link on the theme overlay, which `Menus and UI.md` has since moved to
  Settings. The handoff is a read-only reference asset, so this PRD records the drift rather
  than correcting it.

### 5. Carried to `P1-07-entitlements.md`

Two questions the original document raised now sit on the entitlement half and are worded
there, not here:

- **If an entitlement is ever lost, what happens to games above the cap?** —
  `P1-07-entitlements.md` Open Question 1. The **mechanism** is now settled by
  `Tech Design.md` → Decisions → *Entitlements* ("A refunded or lapsed purchase simply stops
  appearing in `currentEntitlements`"); what the app should *do* about games above a dropped
  cap is not.
- **Can a paid theme ever be a product whose theme file is not on the device?** —
  `P1-07-entitlements.md` Open Question 2.
