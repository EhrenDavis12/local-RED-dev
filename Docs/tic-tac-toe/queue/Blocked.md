# Blocked

> **What this is:** Work waiting on you. Each item lists the questions the queue could not
> answer by reading, and where its partial work lives.
> **Shared.** The queue writes the item and its `Q:` lines; you write the `A:` lines.
> **Hints:** Answer under the question, in plain words. If an answer is a design decision, it
> lands in the design docs before the work resumes. An item with every `A:` filled in returns
> to the top of Ready on the next tick.

---
- Research: App Store in-app purchase vs Stripe for paying for features — what are the advantages of each, which should we use given we want Android one day, and can an app like this connect to Stripe at all? [research] · branch none
  - **What was found (checked 2026-09-11):** Apple requires its own in-app purchase for
    anything digital sold inside an app — a paid theme included. There is a US-only
    loophole (from the Epic lawsuit) that lets an app link out to a web checkout like
    Stripe, but a kids-category app may not put purchase links in front of kids, the
    buyer would be sent out of the app to a web page asking for a credit card (no
    Ask-to-Buy, no parental approval flow), and the courts are in the process of letting
    Apple charge a commission on those web sales anyway. Stripe itself says digital goods
    in iOS apps must go through that link-out route — its normal in-app payment sheet is
    only allowed for physical goods. So for this app, Stripe is effectively not available,
    not merely worse.
  - **The money:** with Apple's Small Business Program (15% cut) a $2.99 theme pays you
    $2.54; through Stripe it would pay $2.60 — six cents more per sale, and Stripe would
    require running a server to record who bought what, which the app doesn't have and
    the goal explicitly excludes.
  - **Android one day:** Google Play has the same rule — digital goods must use Play's
    billing. So Stripe wouldn't help there either. The official Flutter purchase plugin
    covers both stores with one code path, so the purchase code written now carries over;
    only the store-side product setup is new per store.
  - **Recommendation:** Apple in-app purchase through the official Flutter plugin
    (`in_app_purchase`), no third-party service. It matches the tech design as written
    (Apple keeps the record of who owns what, refunds revoke automatically, restore is
    built in, parent-approves-later works) and needs no server and no accounts.
    RevenueCat (a purchase-management service) was considered and lost: free at this
    scale, but it adds a data-collecting third-party service to a kids app for features
    a single one-time purchase never uses.
  - Q: For the paid theme, go with Apple's own in-app purchase (the recommendation above)?
    Saying yes settles the design; the alternatives are effectively unavailable for a
    kids app. Cheap to revisit before the purchase code is built, expensive after.
    A:
  - Q: If someone buys the theme on iPhone and the game later comes to Android, is it OK
    that they'd have to buy it again there? "Yes" is the normal answer for a ~$3 cosmetic
    and needs nothing built; "no" eventually means user accounts or a third-party
    service. Cheap to defer — nothing built now forecloses either answer.
    A:
  - Q: What should the paid Sewing theme cost? The docs price the open-games unlock at
    $4.99 but never price the theme. This is typed into App Store Connect, not code —
    changeable anytime, even after launch.
    A:
