# Blocked

> **What this is:** Work waiting on you. Each item lists the questions the queue could not
> answer by reading, and where its partial work lives.
> **Shared.** The queue writes the item and its `Q:` lines; you write the `A:` lines.
> **Hints:** Answer under the question, in plain words. If an answer is a design decision, it
> lands in the design docs before the work resumes. An item with every `A:` filled in returns
> to the top of Ready on the next tick.

---
- App Store in-app purchase products as code: a products file plus a fastlane lane that creates and updates the two non-consumable products (open-games unlock, Sewing theme) in App Store Connect, with a dry-run, and the Xcode In-App Purchase capability and a StoreKit test config generated from the same file [look] [M] · branch queue/iap-products-as-code
  - **Built (2026-09-12):** the two products are now described in one file in the app repo
    and pushed to App Store Connect by a fastlane lane, Terraform-style: `iap_plan` shows
    what would change (writes nothing), `iap_sync` applies it and is safe to re-run
    (creates what's missing, patches only what may change, never deletes — extras are
    reported), `iap_sync dry_run:true` previews. The same file generates the Simulator
    test config, and the Xcode In-App Purchase capability is on. 45 tests cover the
    diff-and-apply logic; the plan lane was run against the live account and reports
    exactly the eight creates expected. Nothing in the app itself was touched — no
    plugin, no buy button. Branch is ready for your review.
  - **What the live account showed:** the API key works and the app record exists, with
    no in-app purchases yet. The app's Pricing and Availability has never been set in
    App Store Connect, so the lane will create the products with names and prices but
    defer their territory availability (it says so, and picks it up on the next run
    once you set the app's pricing). Whether the Paid Applications Agreement is signed
    can't be read from the API; the first apply tells us (it fails with a clear message
    if not).
  - **Product identifiers proposed** (permanent once created — check them before apply):
    `com.ehrendavis.tictactoeextreme.opengames100` (the $4.99 open-games unlock) and
    `com.ehrendavis.tictactoeextreme.theme.sewing` (the Sewing theme). Family Sharing is
    off for both because Apple lets you turn it on later but never off.
  - **Theme price — market rate and recommendation:** single cosmetic themes in casual
    and kids apps cluster at $0.99–$2.99; "unlock everything" packs at $3.99–$6.99. The
    open-games unlock is already $4.99, so a single theme at $4.99 reads as the same
    value as a whole feature. Recommendation: **$2.99 per theme** (you keep $2.54 after
    Apple's 15% small-business cut), and if more paid themes come later, an all-themes
    bundle at $4.99–$5.99. The file carries $2.99 as a placeholder. Changeable anytime,
    even after launch.
  - Q: Apply it? Saying yes runs `iap_sync` against App Store Connect and creates the
    two products with the identifiers above. The identifiers are permanent; everything
    else about a product can be changed later by editing the file and re-running.
    A: Yes — set up all the purchases so they're ready to go. (relayed from the user,
    2026-09-14)
  - Q: Sewing theme price — $2.99 (recommended) or $4.99? Typed into the products file;
    changeable anytime.
    A: $1.99. (relayed from the user, 2026-09-14)
  - Q: The goal says Sewing is the paid theme at launch, but the design docs say in
    four places that every theme ships free and Sewing becomes paid "once the purchase
    flow lands", and the theme picker shows no locked row. Confirm Sewing is locked and
    for sale at first release? Yes means the docs and the theme picker's locked row
    get revised; cheap, but it is a screen behaviour, not just wording.
    A: Not yet — for now keep the themes free in the app; the store setup can be done.
    (relayed from the user, 2026-09-14)
  - Q: Two App Store Connect steps only you can do, with the longest lead time: sign the
    Paid Applications Agreement (Agreements, Tax, and Banking — needs banking and tax
    info) and set the app's Pricing and Availability. Done, or when?
    A:
- decide: online play — six decisions the multiplayer build needs [prd] · branch none
  - The user asked on 2026-09-14 to build online play over Game Center: setup, a "Play
    online" button, and match creation (Apple's matchmaker provides find-a-player and
    friend invites). The eleven-row plan is in Proposed (three rows already in Ready).
    Rows that store data or fix the game's shape wait on these:
  - Q: The written goal says the App Store release does not include online play. Does
    the release now wait for online play, or does it go out first and online ships as
    an update? (Goal.md is yours to edit either way.)
    A:
  - Q: Do online games count toward the same three-open-games limit as games on this
    phone? If yes, a kid with three games going cannot accept a friend's invite until
    they delete one. Hard to change later — it's written into how games are stored.
    A:
  - Q: When should the game ask Apple who the player is? At launch shows every player a
    Game Center welcome banner the first time, even if they never play online; the first
    tap on "Play online" keeps it away from one-phone players. Cheap to change.
    A:
  - Q: How often is the grown-up maths question asked for online play — every new online
    game, only the first time ever, or once per app open? And is it asked when accepting
    a friend's invite, or only when starting one? Cheap to change.
    A:
  - Q: If the other player never takes their turn, wait forever or end the game after a
    set time (Apple's usual default is two weeks) and hand the win to whoever is still
    playing? Cheap to change — one setting sent with each turn.
    A:
  - Q: What name is an online game listed under — the other player's Game Center
    nickname (which they chose, could be anything), or a label this player types?
    Moderate to change; the name is fixed when the game is created.
    A:
