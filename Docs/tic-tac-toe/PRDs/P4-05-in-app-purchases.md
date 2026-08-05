# PRD: In-App Purchases — the purchase and entitlement layer

> **Status:** Draft · Source docs read: `Tech Design.md`, `Theming.md`, `Menus and UI.md`,
> `Game Overview.md`, `Game Board Design.md`, `Rules.md`, `Animations.md`, `roadmap.md`,
> and the read-only reference asset `design_handoff_game_ui/` (`README.md` → *2a — Theme
> Select (overlay, with paywall)* → *Ownership states — the part to build carefully*;
> `themes.catalog.json`). `Alternative Game Styles.md` is a declared parking-lot doc and
> was not used as a source.

**Wave:** P4 · **File:** `P4-05-in-app-purchases.md` — parallel-safe with the other P4
PRDs.

**Depends on:**

- `P1-04-persistence.md` — the local store. This PRD says entitlement state must survive a
  restart; that PRD owns where and how it is written.
- `P1-03-theme-system.md` — the theme catalog and theme materialization. This PRD attaches
  ownership *beside* a theme, never inside its definition, and defines no part of the theme
  object.
- `P3-02-open-games-list.md` — the consumer of the open-game cap value.
- `P3-03-theme-selection.md` — the consumer of the per-theme ownership state.

**Depended on by:** `P5-02-release-fastlane.md`, which declares the in-app purchases on the
App Store Connect record.

**This PRD is new scope.** `Theming.md` → Decisions → *Are themes unlockable/rewards*
previously said every theme was free with "no monetization work now"; it has been rewritten
to the opposite. PRDs written before that reversal — `P1-03-theme-system.md`,
`P3-03-theme-selection.md`, `P4-04-classic-theme.md`, `P5-02-release-fastlane.md` — still
cite the superseded wording. Reconciling them is not this PRD's job.

---

## Problem

The game now sells two things and has nothing to sell them with. `Tech Design.md` →
Decisions → *In-app purchases* records that "the game now sells two things": themes beyond
the two free ones, and "a **$4.99 unlock that raises the open-game cap from 3 to 100**."
`Theming.md` → Decisions → *Which themes are free* commits the theme selection list to
**labelling** which themes are free and which are paid. `Menus and UI.md` → Decisions →
*How many open games do we keep?* now reads "3 by default, no more. A $4.99 in-app purchase
raises the cap to 100 open game slots."

There is no application code yet, so there is nothing that knows what the player owns.
Without that: the theme list has no ownership state to label rows with, the open-game cap is
a constant with no second value, and a player who pays has no way to get what they paid for
back on a new device — which Apple requires for a non-consumable purchase and which the
approved handoff already draws as a *Restore purchases* footer link,
"required by both app stores once you charge for anything"
(`design_handoff_game_ui/README.md` → *2a*).

It also breaks a standing property of the app. `Tech Design.md` → *What the Design Docs
Already Imply* used to list "Fully offline. No backend, no network, no accounts" as locked.
That row has been **qualified rather than deleted** — see Requirement 14 and *What this does
and does not change about "fully offline"* below.

## Goal

The app has one layer that knows what the player owns: it queries the store for the products
this app sells, caches the result locally so the answer survives a relaunch with no network,
exposes two entitlements — *paid themes* and *the 100-slot open-game cap* — to the screens
that gate on them, runs a purchase and a restore, and never blocks launch or gameplay when
the store cannot be reached. Apple remains the authority on what was bought; the local copy
is a cache of Apple's answer, not a second source of truth, and there is still no backend of
our own and no account system we operate.

## Requirements

### The products

1. **The app sells exactly two things: paid themes, and a $4.99 unlock raising the
   open-game cap from 3 to 100.** No other purchasable product exists.
   *(`Tech Design.md` → Decisions → In-app purchases: "The game now sells two things …
   Themes beyond the two free ones (Neon and Classic Red vs Blue), and a $4.99 unlock that
   raises the open-game cap from 3 to 100"; `Menus and UI.md` → Decisions → How many open
   games do we keep?; `Theming.md` → Decisions → Which themes are free.)*
   *Testable:* the set of product identifiers the app queries has no member outside these
   two. Whether they are one product or two is **Open Question 1** — see Requirement 5.

2. **Both entitlements are permanent once bought and are re-obtainable by restoring.** A
   purchase is not consumed, does not expire, and is not re-charged.
   *(`Tech Design.md` → Decisions → In-app purchases: "a restore-purchases path tied to the
   Apple ID"; `themes.catalog.json` → `storeRequirements`: "A 'Restore purchases' affordance
   must be present wherever paid content is listed.")*
   *Testable:* an owned entitlement, cleared from the local cache, is recovered by restore
   without a second charge.

3. **Displayed prices are read from the store SDK at runtime and localized. No price is
   hardcoded anywhere in the app.**
   *(`themes.catalog.json` → `storeRequirements`: "Prices must be read from the store SDK at
   runtime, localized — never hardcoded. The $1.99 above is mock data.")* The `$4.99` in
   `Menus and UI.md` and `Tech Design.md` is the price to configure in App Store Connect
   (`P5-02-release-fastlane.md`), not a string to render.
   *Testable:* a source scan finds no currency literal in the purchase or gating code; with
   the store stubbed to a different locale and amount, the displayed price follows the stub.

### What the entitlements gate

4. **Neon and Classic Red vs Blue are free and are never subject to an entitlement check.**
   A player with no purchases, and a player whose store query never completed, can select
   either one.
   *(`Theming.md` → Decisions → Which themes are free: "Neon and Classic Red vs Blue are
   free. Every theme beyond those two is paid.")*
   *Testable:* with the store unavailable and the entitlement cache empty, both themes are
   selectable.

5. **Every theme beyond those two is paid and is selectable only while the corresponding
   entitlement is held.**
   *(`Theming.md` → Decisions → Are themes unlockable/rewards: "Yes — some themes are paid …
   any other themes will be a paid for theme"; → Which themes are free.)*
   *Testable:* a catalog entry marked paid, with no entitlement held, cannot be applied as
   the active theme.
   *Not specified here:* whether one purchase covers all paid themes or each theme is its
   own product — **Open Question 1**. Build Requirement 5 so either answer remains reachable;
   do not bake a single global "themes unlocked" flag or a per-theme product list in before
   it is decided.

6. **The open-game cap is 3 without the unlock entitlement and 100 with it.** The cap is a
   value the entitlement layer supplies, not a constant compiled into the list screen or the
   storage layer.
   *(`Menus and UI.md` → Decisions → How many open games do we keep?: "3 by default, no
   more. A $4.99 in-app purchase raises the cap to 100 open game slots."; `Tech Design.md` →
   Decisions → In-app purchases.)*
   *Testable:* with the entitlement absent the layer reports 3, with it present it reports
   100, and no other source in `lib/` defines either number.

7. **The entitlement layer exposes, per theme, which of `free` / `owned` / `locked` the
   theme is in**, so the selection list can label it.
   *(`Theming.md` → Decisions → Which themes are free: "The theme selection list **labels**
   which themes are free and which are paid"; `design_handoff_game_ui/README.md` → *2a* →
   *Ownership states — the part to build carefully*; `themes.catalog.json` →
   `ownershipStates`.)* The row treatments, badges and price button are
   `P3-03-theme-selection.md`'s.
   *Testable:* for a catalog of a free theme, a paid-and-owned theme and a paid-and-unowned
   theme, the layer reports `free`, `owned` and `locked` respectively.

8. **Ownership is never part of a theme definition.** No theme YAML file carries an
   ownership, price or purchase field, and materializing a theme does not consult purchase
   state.
   *(`themes.catalog.json` → note: "Ownership is NOT part of a theme definition — a theme is
   an audio-visual package; entitlement is account/device state";
   `design_handoff_game_ui/README.md` → *2a*: "keep purchase state **out of the theme
   definition**".)*
   *Testable:* deleting the entitlement layer entirely still lets every theme file load and
   merge over Neon.

9. **A locked theme still renders its preview; buying is the only gate.** Ownership
   withholds *selection*, not the theme's values.
   *(`themes.catalog.json` → `storeRequirements`: "A locked theme must still render its
   preview; buying is the only gate."; `design_handoff_game_ui/README.md` → *2a*: "A locked
   row must read as **buyable, not broken**".)*

### Querying, caching and restoring

10. **The app queries the store for its products and for what the player owns, and caches
    the answer locally.** Gating reads the cache, so no gating decision waits on the network.
    *(`Tech Design.md` → Decisions → In-app purchases; → *What the Design Docs Already
    Imply* → "Fully offline, except for in-app purchases … StoreKit is the one exception".)*
    *Testable:* with the network disabled after a successful query, launching the app still
    reports the same entitlements.

11. **Cached entitlement state survives an app restart.** The values are handed to the
    persistence layer; `P1-04-persistence.md` owns the store, the keys and the format.
    *(`Tech Design.md` → Decisions → In-app purchases; → Persistence package and → Project
    structure — layer-first, which put local persistence in `storage/`.)*
    *Testable:* purchase, force-quit, relaunch with no network — the entitlement is still
    held.

12. **A *Restore purchases* action exists wherever paid content is listed, and restoring
    re-establishes every entitlement the Apple ID holds.**
    *(`themes.catalog.json` → `storeRequirements`: "A 'Restore purchases' affordance must be
    present wherever paid content is listed."; `design_handoff_game_ui/README.md` → *2a*
    footer: "a centered **Restore purchases** link … required by both app stores once you
    charge for anything"; `Tech Design.md` → Decisions → In-app purchases: "a
    restore-purchases path tied to the Apple ID".)* This PRD owns the operation and its
    result; the theme overlay's footer link is `P3-03-theme-selection.md`'s.
    *Testable:* clear the local cache, run restore against a store stub reporting one owned
    product, and that entitlement is held again.

13. **Entitlement state is readable from anywhere in the app, as Riverpod provider state**,
    and a change to it — a completed purchase or a completed restore — reaches its gating
    consumers within the same session, without a restart.
    *(`Tech Design.md` → Decisions → State management — Riverpod, which covers "the
    requirement that settings and the theme be readable from **everywhere**".)*
    *Testable:* with the theme list open, granting the entitlement in a stubbed store moves
    the affected row out of `locked` without rebuilding the app.

### Offline, failure, and the boundary

14. **The app launches and plays with no network and no store.** A purchase check that
    cannot complete must not block launch, block starting or resuming a game, or make the
    app show an error the player has to dismiss to keep playing.
    *(`Tech Design.md` → *What the Design Docs Already Imply* → "**Fully offline, except for
    in-app purchases.** No backend, no network, no accounts — StoreKit is the one
    exception"; → Decisions → In-app purchases.)*
    *Testable:* with every store call stubbed to fail, the app reaches the main menu, starts
    a game, plays it to a win and reopens it from the list.

15. **When the store cannot be reached, the cached entitlement state is what gating uses.**
    A failed or timed-out query is not treated as an answer of "owns nothing", and does not
    clear the cache.
    *(Derived from Requirement 14's source — an app whose paid features stop working with no
    network is not "fully offline, except for in-app purchases". `Tech Design.md` →
    Decisions → In-app purchases makes network the store's requirement, not the app's.)*
    *Testable:* with an entitlement cached, stub every store call to fail, relaunch, and the
    cap still reads 100 and paid themes stay selectable.
    *Not specified here:* what happens if the store affirmatively reports an entitlement
    *gone* — **Open Question 2**.

16. **Apple is the authority on what was bought; the local cache is a copy of Apple's
    answer.** Nothing in the app treats the local value as the record of truth, and a
    restore overwrites it.
    *(`Tech Design.md` → Decisions → In-app purchases: "a restore-purchases path tied to the
    Apple ID"; `themes.catalog.json` → note: "entitlement is account/device state".)*

17. **No backend of ours, and no account system we operate, is introduced.** The app talks
    to the platform store and to nothing else: no server of ours, no login, no user record.
    Crash reports are still built and not transmitted.
    *(`Tech Design.md` → Decisions → Project structure — layer-first: "`storage/` is local
    persistence only … There is still **no backend data layer**: nothing in the app talks to
    a server"; → Decisions → Crash reporting — catch and build the report, don't send it; →
    *What the Design Docs Already Imply* → the qualified *Fully offline* row.)*
    *Testable:* an outbound-call scan over `lib/` finds no HTTP client and no network target
    other than the store SDK.

18. **Any UI this layer adds is theme-driven like everything else** — no hardcoded colors,
    fonts, sounds, motion or asset paths.
    *(`Theming.md` → Architectural Rule; `Tech Design.md` → Decisions → Do we add a test
    that fails on hardcoded theme values?)*
    *Testable:* the hardcoded-theme-value test (`P1-05-theme-guard-test.md`) passes over this
    layer's source with the baseline at zero.

### What is reachable at launch

19. **At launch, no theme purchase is reachable, because both themes that ship are free.**
    Two themes ship — Neon and Classic Red vs Blue — and both are free, so the catalog
    contains zero locked themes and the only purchasable product a player can reach is the
    open-game cap unlock.
    *(`Theming.md` → Decisions → How many themes ship at launch: "Two — Neon and Classic Red
    vs Blue"; → Decisions → Which themes are free; `Menus and UI.md` → Theme Selection.)*
    *Testable:* on a launch build, the number of catalog entries with ownership `locked` is
    zero.
    **Consequence for this PRD:** the labelling and entitlement model (Requirements 5, 7, 8,
    9) is built now because the docs commit to it; **a theme storefront is not**, because
    there is no theme to sell. See *Out of Scope*.

## What this does and does not change about "fully offline"

Recorded here because `Tech Design.md` qualified that row rather than deleting it, and
because every other PRD in this project was written under the unqualified version.

**Changes:**

- The app now makes network calls. StoreKit needs the network to query products, to
  purchase, and to restore.
- The app is now tied to an Apple ID for one purpose — restore. That is the account the
  entitlement belongs to.
- "No accounts" is no longer literally true at the platform level.

**Does not change:**

- **There is still no backend of our own.** Nothing in the app talks to a server we run
  (Requirement 17).
- **There is still no account system we operate.** No sign-in, no user record, no profile.
  The Apple ID is Apple's, and the app never sees credentials.
- **Gameplay is still fully offline.** Two players, one phone; the game launches, plays and
  saves with the network off (Requirement 14).
- **Crash reports are still not transmitted.** `Tech Design.md` → Decisions → Crash
  reporting is untouched by this; StoreKit being allowed does not make a report destination
  allowed.
- **`storage/` is still local persistence only.** Entitlement caching is a local write like
  any other; no data layer talks to a network.

## Out of Scope

- **A theme storefront.** With two themes shipping and both free (Requirement 19), there is
  no paid theme to sell, no purchase sheet to design for one, and no product identifier for
  one. This PRD builds the model that labels and gates; it does not build a store for
  products that do not exist. The handoff's Splat and Dinosaurs rows are explicitly
  placeholders — "their art, sound and animation sets do not exist … Do not ship them as
  designed" (`design_handoff_game_ui/README.md` → *2a* → The four themes shown).
- **Theme materialization, the theme object, YAML loading and UUID identity** —
  `P1-03-theme-system.md`. This PRD attaches nothing to a theme definition (Requirement 8).
- **Where entitlement values are stored** — `P1-04-persistence.md`. Requirement 11 states
  that they must persist; that PRD owns the store, key and format.
- **The theme selection overlay's rows, badges, price button and *Restore purchases* footer
  link** — `P3-03-theme-selection.md`. This PRD supplies the state those render from
  (Requirement 7) and the operation the link invokes (Requirement 12).
- **The open-games list, its delete action, and how the cap is displayed or enforced in the
  UI** — `P3-02-open-games-list.md`. This PRD supplies the cap value (Requirement 6).
- **The App Store Connect record: the product entries, their identifiers, their price tiers,
  and the listing declaring that the app contains in-app purchases** —
  `P5-02-release-fastlane.md`.
- **What happens when a player at the cap starts a new game** — refuse, or replace the
  oldest. Still unsettled and carried by `P1-04-persistence.md` → Open Questions 3 and
  `P3-02-open-games-list.md`. This PRD changes only what number the cap is, not the behavior
  at it, though it does add a third candidate answer (offer the unlock) that nobody has
  chosen. See Open Question 5.
- **Android billing.** Every monetization statement in the docs names StoreKit and the Apple
  ID (`Tech Design.md` → Decisions → In-app purchases), and iOS is the primary target with
  Android "far future" (→ Decisions → Device support). No Android store work is specified
  here. See Open Question 5.

## Open Questions

### 1. Are the 100-slot unlock and paid themes separate products, or a bundle?

The docs are silent. `Tech Design.md` → Decisions → *In-app purchases* says "the game now
sells two things" and names them, and `Menus and UI.md` prices one of them at $4.99. Nothing
states whether paid themes are one product, one product per theme, or bundled with the slot
unlock — and nothing gives a paid theme a price at all (the `$1.99` in
`themes.catalog.json` is labelled mock data). Requirement 5 is written so either shape stays
reachable.

### 2. If an entitlement is ever lost, what happens to games above the cap?

The docs are silent. A player who buys the unlock, creates 40 open games, and then loses the
entitlement — refund, family-sharing change, a restore on a different Apple ID — is holding
37 games more than the free cap allows. Whether those games are kept and read-only, kept and
hidden, deleted oldest-first, or the cap simply stops being enforced downward is not stated
anywhere. Requirement 15 covers only the *store unreachable* case, deliberately; this is the
*store says no* case.

### 3. Do purchases need a receipt-validation step?

The docs are silent. `Tech Design.md` → Decisions → *In-app purchases* names StoreKit and a
restore path and stops there. Whether the app validates a receipt — and if so where, given
that → Decisions → *Project structure — layer-first* says "There is still **no backend data
layer**: nothing in the app talks to a server" and Requirement 17 keeps it that way — is not
decided.

### 4. Does a paid-theme model imply themes shipping after launch, and does that contradict *Where Themes Live*?

Flagged, not resolved. Two statements in `Theming.md` sit uneasily together:

- **Decisions → Which themes are free:** "Every theme beyond those two is paid." Two themes
  ship (→ Decisions → How many themes ship at launch), and both are free — so the paid
  category is empty until a third theme exists.
- **Where Themes Live:** "**For now, themes are contained within the codebase.** Bundled/
  shipped with the app. Not user-uploaded, not downloaded from a server."

A theme bundled with the app and unlocked by purchase is consistent with both. A theme
*added after launch* is only reachable through an app update under *Where Themes Live*, or
by downloading it, which that section rules out for now. Nothing says which. The question
this raises and does not answer: **is the paid-theme model a plan to add themes in later app
versions, or a plan to bundle unbuilt paid themes into the launch binary?** The answer
decides whether the entitlement layer ever needs to handle a product whose theme file is not
present on the device.

### 5. Gaps found while writing this PRD (author-raised, not asked by the docs)

Each is something an implementer would otherwise have to guess. None is resolved here.

- **No product identifiers exist.** No doc names a product ID for either product, and this
  PRD invents none. Something must, before the store can be queried
  (`P5-02-release-fastlane.md` registers them).
- **How the app reaches StoreKit from Flutter is not decided.** The docs name StoreKit
  (`Tech Design.md` → Decisions → In-app purchases) and name a package for audio,
  persistence and state management — but not for purchases. A plugin choice is a Decision
  that has not been made.
- **Where the $4.99 unlock is offered.** No screen in `Menus and UI.md` or in the approved
  handoff shows it. The handoff's `1b` footer reads "Three saved games. Starting a fourth
  replaces the oldest," which predates the cap decision and is annotated as unconfirmed. The
  theme overlay is the only place paid content is drawn, and the unlock is not a theme.
- **Whether reaching the cap offers the unlock.** This is now a third candidate answer to
  the still-open "what happens at the cap" question (`P1-04-persistence.md` → Open Questions
  3), alongside refuse and replace-oldest. Nobody has chosen.
- **What a failed or cancelled purchase shows the player.** Cancelled, declined, pending
  (Ask to Buy) and errored are four different outcomes; no doc describes any of them, and no
  modal for them is designed.
- **The handoff's rationale for the paywall now quotes a superseded decision.**
  `design_handoff_game_ui/README.md` → *2a* justifies its ownership states with
  "Per `Theming.md` this is a *direction*, not current scope: 'all themes available from the
  start… no monetization work now.'" `Theming.md` no longer says that. The drawn states are
  now live scope; the paragraph explaining them away is stale. The handoff is a read-only
  reference asset, so this PRD records the drift rather than correcting it.
- **Whether the 100 cap is a storage ceiling too.** `P1-04-persistence.md` Requirement 10
  asserts "The store never holds more than 3 open games" as a hard ceiling, written before
  this decision existed. Which layer enforces the now-variable cap — storage, the list
  screen, or this one supplying the number to both — is not settled.
