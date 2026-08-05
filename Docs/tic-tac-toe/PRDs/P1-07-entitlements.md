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
> is StoreKit, buying and restoring. Every requirement of the original lives in exactly one
> of the two — none was invented and none was dropped.

**Depends on:**

- `P1-03-theme-system.md` — the theme catalog and theme UUID identity. This PRD attaches
  ownership *beside* a theme, never inside its definition, and defines no part of the theme
  object. Same wave.
- `P1-04-persistence.md` — where entitlement state is written down. This PRD says what must
  survive a restart; that PRD owns the store, the keys and the format. Same wave. The
  boundary between the two is drawn — see Open Question 4.

**Depended on by:** `P1-04-persistence.md` (the ceiling it enforces), `P4-02-open-games-list.md`
(the open-game cap value), `P4-03-theme-selection.md` (the per-theme ownership state its rows
are labelled from), `P4-05-purchase-flow.md` (which writes store results into this state).

**Nothing here requires a network or a store.** With no purchase layer built, every read in
this PRD resolves to the free tier, which is what makes it a wave-1 feature.

---

## Problem

There is no application code yet, so there is nothing that knows what the player owns.
Without that: the theme list has no ownership state to label rows with, and the open-game
cap is a constant with no second value.

Both consequences land on features that ship before any store integration does.
`Menus and UI.md` → Decisions → *How many open games do we keep?* now reads "3 by default,
no more. A $4.99 in-app purchase raises the cap to 100 open game slots" — so
`P1-04-persistence.md` cannot enforce a ceiling without asking something what the player
owns. `Theming.md` → Decisions → *Which themes are free* commits the theme selection list to
**labelling** which themes are free and which are paid. Neither can wait for StoreKit, and
neither should have to: the game is otherwise fully playable with no network.

## Goal

The app has one layer that knows what the player owns. It exposes two entitlements — *paid
themes* and *the 100-slot open-game cap* — to the screens that gate on them, answers from a
local copy so no gating decision waits on the network, and defaults to the free tier when
nothing has been bought. Apple is the record of truth and is queryable at runtime; the local
copy is an offline convenience, not a second source of truth, and this layer never mints an
entitlement of its own.

## Requirements

### What the entitlements gate

1. **Neon and Classic Red vs Blue are free and are never subject to an entitlement check.**
   A player with no purchases, and a player whose store query never completed, can select
   either one.
   *(`Theming.md` → Decisions → Which themes are free: "Neon and Classic Red vs Blue are
   free. Every theme beyond those two is paid.")*
   *Testable:* with the store unavailable and no entitlement state present, both themes are
   selectable.

2. **Every theme beyond those two is paid and is selectable only while the corresponding
   entitlement is held.**
   *(`Theming.md` → Decisions → Are themes unlockable/rewards: "Yes — some themes are paid …
   any other themes will be a paid for theme"; → Which themes are free.)*
   *Testable:* a catalog entry marked paid, with no entitlement held, cannot be applied as
   the active theme.
   *Not specified here:* whether one purchase covers all paid themes or each theme is its
   own product — `P4-05-purchase-flow.md` **Open Question 1**. Build Requirement 2 so either
   answer remains reachable; do not bake a single global "themes unlocked" flag or a
   per-theme product list in before it is decided.

3. **The open-game cap is 3 without the unlock entitlement and 100 with it.** The cap is a
   value the entitlement layer supplies, not a constant compiled into the list screen or the
   storage layer.
   *(`Menus and UI.md` → Decisions → How many open games do we keep?: "3 by default, no
   more. A $4.99 in-app purchase raises the cap to 100 open game slots."; `Tech Design.md` →
   Decisions → In-app purchases.)*
   *Testable:* with the entitlement absent the layer reports 3, with it present it reports
   100, and no other source in `lib/` defines either number.

4. **The entitlement layer exposes, per theme, which of `free` / `owned` / `locked` the
   theme is in**, so the selection list can label it.
   *(`Theming.md` → Decisions → Which themes are free: "The theme selection list **labels**
   which themes are free and which are paid"; `design_handoff_game_ui/README.md` → *2a* →
   *Ownership states — the part to build carefully*; `themes.catalog.json` →
   `ownershipStates`.)* The row treatments, badges and price button are
   `P4-03-theme-selection.md`'s.
   *Testable:* for a catalog of a free theme, a paid-and-owned theme and a paid-and-unowned
   theme, the layer reports `free`, `owned` and `locked` respectively.

5. **Ownership is never part of a theme definition.** No theme YAML file carries an
   ownership, price or purchase field, and materializing a theme does not consult purchase
   state.
   *(`themes.catalog.json` → note: "Ownership is NOT part of a theme definition — a theme is
   an audio-visual package; entitlement is account/device state";
   `design_handoff_game_ui/README.md` → *2a*: "keep purchase state **out of the theme
   definition**".)*
   *Testable:* deleting the entitlement layer entirely still lets every theme file load and
   merge over Neon.

6. **A locked theme still renders its preview; buying is the only gate.** Ownership
   withholds *selection*, not the theme's values.
   *(`themes.catalog.json` → `storeRequirements`: "A locked theme must still render its
   preview; buying is the only gate."; `design_handoff_game_ui/README.md` → *2a*: "A locked
   row must read as **buyable, not broken**".)*

### Keeping it, reading it, and who has authority

> **Why a local copy exists — grounded, where this was previously flagged as a premise with
> no source.** Earlier drafts carried an explicit flag that no design doc said entitlement
> state is kept on the device at all. `Tech Design.md` → Decisions → *Entitlements — Apple
> stores them, no backend needed* now settles the shape from the other direction: **Apple is
> the record of truth and it is queryable at runtime**, via
> `Transaction.currentEntitlements` — "cryptographically signed by Apple and verified on
> device … the authoritative answer to 'does this player own this'". The same Decision names
> what a local copy is for and what it is not: "**Any locally stored entitlement state is an
> offline convenience, not the record.**"
>
> That is the whole justification for Requirement 7, and the flag is retired. What remains
> open is only *which* store holds the copy — `P1-04-persistence.md` → Open Questions 5.

7. **Entitlement state is kept locally as an offline convenience, and survives an app
   restart.** The local copy exists so gating resolves with no network available; it is
   never the record of truth. The values are handed to the persistence layer;
   `P1-04-persistence.md` owns the store, the keys and the format.
   *(`Tech Design.md` → Decisions → Entitlements — Apple stores them, no backend needed:
   "Apple is the record of truth and it is queryable at runtime. Any locally stored
   entitlement state is an offline convenience, not the record."; → Decisions → Persistence
   package and → Project structure — layer-first, which put local persistence in
   `storage/`.)*
   *Testable:* purchase, force-quit, relaunch with no network — the entitlement is still
   held.

8. **Entitlement state is readable from anywhere in the app, as Riverpod provider state**,
   and a change to it — a completed purchase or a completed restore — reaches its gating
   consumers within the same session, without a restart.
   *(`Tech Design.md` → Decisions → State management — Riverpod, which covers "the
   requirement that settings and the theme be readable from **everywhere**".)*
   *Testable:* with the theme list open, granting the entitlement in a stubbed store moves
   the affected row out of `locked` without rebuilding the app.
   *Not settled:* whether that provider's type admits a "not known yet" state — see Open
   Question 6.

9. **When the store cannot be reached, locally held entitlement state is what gating uses.**
   A failed or timed-out query is not treated as an answer of "owns nothing", and does not
   clear what is held.
   *(Now doc-backed rather than derived. `Tech Design.md` → Decisions → Entitlements — Apple
   stores them, no backend needed makes the authoritative source **queryable**: ownership is
   a question asked of Apple at runtime rather than a fact the app holds. A query that fails
   therefore returns *no information* — an absence, not an answer — so treating it as "owns
   nothing" would be inventing an answer Apple never gave. Also `Tech Design.md` → *What the
   Design Docs Already Imply* → the qualified fully-offline row, which keeps the game
   playable with the network off.)*
   *Testable:* with an entitlement held, stub every store call to fail, relaunch, and the
   cap still reads 100 and paid themes stay selectable.
   *Not specified here:* what happens if the store affirmatively reports an entitlement
   *gone* — **Open Question 1**.

10. **Apple is the record of truth on what was bought; the local copy is a copy of Apple's
    answer, never the grantor.** Nothing in this layer mints, grants or upgrades an
    entitlement on its own — every entitlement it holds originates in a store result.
    *(`Tech Design.md` → Decisions → Entitlements — Apple stores them, no backend needed:
    "Apple is the record of truth and it is queryable at runtime"; → Decisions → In-app
    purchases: "a restore-purchases path tied to the Apple ID"; `themes.catalog.json` →
    note: "entitlement is account/device state".)*
    *Testable:* the entitlement layer exposes no API that sets an entitlement from anything
    other than a store result — no local grant, no debug-only setter in shipped code — and on
    a device with no entitlement state, only a purchase or a restore can produce one.

    > **Which direction "authority" runs — settled, and now derivable from the docs.** This
    > requirement and Requirement 9 are consistent under one rule: an *affirmative* store
    > answer overrides what is held locally, while a *failed* one does not. That follows
    > directly from `Tech Design.md` → Decisions → *Entitlements* — Apple's answer is the
    > record and the local copy is "an offline convenience, not the record", so an
    > affirmative answer wins; a failed query is an absence of information and so overrides
    > nothing. `P1-04-persistence.md` requirement 19 was narrowed to match and cites
    > Requirement 9 here by number.
    >
    > **An earlier draft of that requirement was worded so that, read literally, a failed
    > query could supersede local state. That collision is closed; the next reader should not
    > go looking for it.** What remains genuinely open is not the direction but the *loss*
    > case — see **Open Question 1**.

## Out of Scope

- **StoreKit, the purchase flow, restore-purchases, purchase outcomes, the parental gate and
  the store-side product concerns** — `P4-05-purchase-flow.md`. This PRD holds what the app
  knows; that one holds how it finds out and how a player buys. It supplies the store results
  this layer stores (Requirement 10); it is the only thing that may produce one.
- **Where entitlement values are stored** — `P1-04-persistence.md`. Requirement 7 states
  that they must persist; that PRD owns the store, key and format, and carries the open
  question of which store that is.
- **Theme materialization, the theme object, YAML loading and UUID identity** —
  `P1-03-theme-system.md`. This PRD attaches nothing to a theme definition (Requirement 5).
- **The theme selection overlay's rows, badges and price button** —
  `P4-03-theme-selection.md`. This PRD supplies the state those render from (Requirement 4).
- **The open-games list, its delete action, and how the cap is displayed or enforced in the
  UI** — `P4-02-open-games-list.md`. This PRD supplies the cap value (Requirement 3).
  Enforcing it in the store is `P1-04-persistence.md`'s.
- **The App Store Connect record: the product entries, their identifiers, their price tiers,
  the Kids Category listing and the age rating** — `P5-03-release-fastlane.md`.
- **What happens when a player at the cap starts a new game** — refuse, or replace the
  oldest. Still unsettled and carried by `P1-04-persistence.md` → Open Questions 3 and
  `P4-02-open-games-list.md`. This PRD changes only what number the cap is, not the behavior
  at it.
- **Any paid theme's content.** No paid theme exists.
  `design_handoff_game_ui/README.md` → *2a* marks Splat and Dinosaurs as placeholders that
  "do not exist" and says "Do not ship them as designed"; Requirement 4 is satisfied with
  fixtures, not with those two.
- **`Alternative Game Styles.md`** — declared parking lot; not what is being built.

## Open Questions

### 1. What should the app do about games above the cap when an entitlement goes away?

*(Narrowed. Carried from Open Question 2 of the pre-split in-app-purchases PRD, whose
mechanism half is now answered.)*

**The mechanism is settled.** `Tech Design.md` → Decisions → *Entitlements — Apple stores
them, no backend needed*: "A refunded or lapsed purchase simply stops appearing in
`currentEntitlements` — that is what answers 'what happens when an entitlement goes away.'"
So "what counts as lost" has an answer: an entitlement is lost exactly when it stops coming
back from Apple. The three triggers earlier drafts listed separately — a restore returning
fewer entitlements, a refund or revocation, and a failed query — collapse into one rule plus
Requirement 9's exception: an affirmative answer that omits an entitlement is a loss; a
failed query is not an answer at all.

**What the app does about it is still open, and is the user's call.** A player buys the
unlock, creates 40 open games, and then no longer holds the entitlement. Whether those 37
games above the free cap are kept and read-only, kept and hidden, deleted oldest-first, or
the cap simply stops being enforced downward is not stated anywhere. Deleting them is
destructive; keeping them silently violates Requirement 3's ceiling.
`P1-04-persistence.md` → Open Questions 5 raises the same case from the storage side.

### 2. Can a paid theme ever be a product whose theme file is not on the device?

*(Carried unchanged from Open Question 4 of the pre-split in-app-purchases PRD.)*

The consequence for this layer: if every paid theme is bundled in the app binary and merely
unlocked, the entitlement layer only ever gates content the device already has. If a paid
theme can arrive any other way, the layer must also handle an entitlement held for something
that is not installed.

Nothing settles which. `Theming.md` → *Where Themes Live* — prose above the Decisions
section, in a doc whose banner says nothing there is settled — notes "**for now**, themes are
contained within the codebase. Bundled/shipped with the app. Not user-uploaded, not
downloaded from a server. That's a possible later thing, not now." Read as written that is a
current-state note with an explicit "for now", not a decision, so this PRD does not treat it
as being in tension with the paid-theme decision and does not ask anyone to adjudicate one.
What stays open is only the question above: an app-update-only model and a
downloaded-content model put different requirements on this layer, and Requirement 2 assumes
neither.

### 3. Which store holds entitlement state

Carried by `P1-04-persistence.md` → Open Questions 5, which sets out the candidates —
`shared_preferences` or Hive — and the consequences that ride on the answer. *That* a local
copy exists is no longer in question: `Tech Design.md` → Decisions → *Entitlements* names it
an offline convenience and Requirement 7 states it. Only where it lives is open. The third
candidate earlier drafts listed — "nothing persisted, re-queried at launch" — is now in
tension with Requirement 9, which needs something to fall back on when the query fails.

### 4. Answered — where the boundary sits between this PRD and `P1-04-persistence.md`

**Closed.** Kept as a stub rather than deleted so the trail stays visible and the numbering
of the questions around it stays stable.

Earlier drafts of this PRD, `P1-04-persistence.md` and `P4-05-purchase-flow.md` each stated
some version of "entitlement state is held locally, survives a restart, is what gating reads
when the store is unreachable, and defaults to the free tier", giving one statement three
homes and no owner. The line has since been drawn, and it fell where this PRD's earlier note
proposed:

- **This PRD is the model.** What the entitlements are (Requirements 1 and 2), the free
  tier, the cap numbers (Requirement 3), the per-theme `free` / `owned` / `locked` query
  (Requirement 4), in-session propagation (Requirement 8), and the authority rule
  (Requirements 9 and 10).
- **`P1-04-persistence.md` is the write-down.** As revised, its requirements 18–20 state
  what bytes are stored, under what key, and what a read gives back — nothing about what any
  of it means. Its requirement 18 keys per-theme unlocks by theme UUID, citing Requirement 7
  here, which is what assigns "the store, the keys and the format" to that layer. Its
  requirement 20 no longer states free-tier defaults at all: an empty store reads back as
  "nothing stored", and what *that* means is Requirements 1 and 3 here.
- **`P4-05-purchase-flow.md` is the store side.** Its requirement 4 was narrowed to the
  query and the hand-off and no longer restates the caching-and-gating half.

The `P1-04` half of the boundary is fully drawn. **Two adjacent questions about the
`P4-05` seam are still open and are with the user** — whether `P4-05` writes through this
layer or directly to `P1-04`, and who owns the store-result type the hand-off carries.
Neither is attempted here.

### 5. Which `lib/` layer does this live in? (raised by review; not answered here)

`P1-01-app-scaffold.md` requirement 2 builds the layer-first tree exactly as
`Tech Design.md` → Decisions → *Project structure — layer-first* names it, and **no
directory in that tree is named for entitlements.** `P1-03-theme-system.md` names
`lib/theme/`, `P1-04-persistence.md` names `storage/`, and this PRD names nothing — so an
implementer picks a folder by accident.

The precedent is that the tree is a **doc-level decision**: the layer-first Decision in
`Tech Design.md` is what enumerates the directories, and a new layer arrives by amending it
rather than by a PRD asserting one. `P2-01-navigation.md` → Open Question 13 records the
identical gap for the routing layer, which suggests this is a pattern worth fixing once
rather than twice. Whether entitlements is a layer of its own, part of `storage/`, or part
of `state/` is not proposed here.

### 6. Is the entitlement answer synchronous, or is there a "not known yet" state?

Requirement 9 covers the case where the store **cannot be reached**. Nothing covers the case
where the answer is **not known yet** — a cold launch with a query in flight, before any
result has arrived. Those are different situations: one has a settled local answer to fall
back on, the other may have nothing at all on a genuine first run.

**One candidate answer is now ruled out.** `Tech Design.md` → Decisions → *Entitlements —
Apple stores them, no backend needed* names `Transaction.currentEntitlements`, which is an
**async sequence** — so a cold launch genuinely has a window in which the authoritative
answer is not yet known, and a purely synchronous "the answer is always available" model is
not achievable against that API.

What is still a design choice is the shape the provider in Requirement 8 exposes —
`Entitlements`, `AsyncValue<Entitlements>`, or a local-copy-plus-refresh model that reports
the last known answer while a query is in flight. `P1-04-persistence.md`,
`P4-02-open-games-list.md` and `P4-03-theme-selection.md` all code against that type, so it
is expensive to change later. Related from the storage side: `P1-04-persistence.md` → Open
Questions 5 already asks what a player sees "before the first successful query on a cold,
offline launch". Not answered here.
