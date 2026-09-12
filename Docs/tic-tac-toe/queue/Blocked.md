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
    A: Yes — Apple in-app purchase. Stripe is out. When we get to Android we'll do the
    Android thing (Play billing) then. (relayed from the user, 2026-09-12)
  - Q: If someone buys the theme on iPhone and the game later comes to Android, is it OK
    that they'd have to buy it again there? "Yes" is the normal answer for a ~$3 cosmetic
    and needs nothing built; "no" eventually means user accounts or a third-party
    service. Cheap to defer — nothing built now forecloses either answer.
    A:
  - Q: What should the paid Sewing theme cost? The docs price the open-games unlock at
    $4.99 but never price the theme. This is typed into App Store Connect, not code —
    changeable anytime, even after launch.
    A:
- Research: online player-vs-player multiplayer — me on my phone against someone on theirs — without Supabase: what server and account options exist (Game Center, Firebase, hosted relay, peer-to-peer, etc.), what each costs and changes for a kids app, and how we'd set it up [research] · branch none
  - **What was found (checked 2026-09-12):** the game is already wire-ready — a move is
    two numbers, the whole board (score included) already saves as JSON, and the rules
    engine is pure, so both phones can validate the same move identically. Nothing needs
    restructuring; what's missing is only the transport and an "opponent" identity.
  - **Yes, this is solvable without Supabase.** Seven options were looked at:
    1. **Apple Game Center turn-based matches.** Apple hosts the match, does invites and
       matchmaking, sends the "your turn" notification, and holds the identity — we
       collect nothing, so the App Store privacy answer stays "no data collected".
       Kids' accounts get Apple's built-in protections and parents can switch multiplayer
       off in Screen Time. Free at any scale. iOS only (Google shut its equivalent down
       in 2020). Catch: no Flutter package covers turn-based matches, so it needs a small
       hand-written Swift bridge (~300 lines over a stable Apple API).
    2. **Firebase** (Google). The usual Flutter answer, free to start, cross-platform, but
       it puts a third-party user ID on a child — a COPPA liability and a known source
       of kids-category review rejections — and flips the privacy label.
    3. **Supabase.** Same identity problem as Firebase, ~$25/month, less kids precedent.
    4. **Game backends** (Nakama, Colyseus, PlayFab, Photon). All need accounts, most have
       no Flutter SDK or cost $15–600/month; all are built for real-time games, not
       taking turns. Disproportionate for a two-player turn game.
    5. **A tiny relay we host** (Cloudflare, room codes instead of accounts). Free to ~$5
       a month, cross-platform, but we'd rebuild push notifications, reconnects, and
       review answers by hand, and sharing a room code means a link out of a kids app.
    6. **Two phones in the same room** (Bluetooth/Wi-Fi peer-to-peer). No server, no
       accounts, free. Gives kitchen-table play only, not remote play. Flutter packages
       are thin; expect to write a small bridge.
    7. **Send the game as a link** each turn over iMessage (chess by mail). No server,
       free, but each share is a link out of a kids app (needs the parental gate) and it
       feels clunky.
  - **Recommendation:** Game Center turn-based matches, optionally with same-room play as
    a cheap first step. It's the only remote option where nobody but Apple ever holds a
    child's identity, it costs nothing, and the "your turn" push comes free. It beats
    Firebase/Supabase/backends because those add a third-party identifier the game gets
    nothing for, and beats the self-hosted relay because that hand-builds what Apple
    already gives. Its only real limit is iOS-only, which the goal already accepts; a
    room-code relay could be added later for Android without undoing anything.
  - **Proposed work if Game Center is the answer** (none of it before game one ships;
    on your answer these move to Later):
    - Confirm Game Center turn-based play is available to under-13 Family Sharing accounts by default [research] [S]
    - Design the online-game record: opponent identity, match ID, whose turn it is, alongside saved games [prd] [M]
    - Game Center turn-based bridge: sign in, create/load match, send a turn, receive the opponent's turn [prd] [M]
    - Online games in the Open Games list and on the board: whose turn, waiting state, invite entry behind the parental gate [look] [M]
    - Allow Game Center as the second sanctioned network path in the tech design's network check [look] [S]
    - Optional: same-room play over Bluetooth/Wi-Fi for two phones with no internet [look] [M]
  - **Contradicts the docs:** nothing today. When this lands, the tech design's "fully
    offline, except for in-app purchases — StoreKit is the one exception" line gains a
    second exception. Left alone until then.
  - Q: Which kind of play do you actually want — remote (anyone, anywhere, take turns
    over days, with "your turn" notifications) or same-room (two phones next to each
    other, no internet)? Game Center gives remote; the Bluetooth route gives same-room;
    both can exist. Cheap to decide, expensive to build both.
    A:
  - Q: Is iOS-only online play acceptable long term, given Android is already out of
    scope? Yes means Game Center (free, no identity collected). No means a small relay
    we host with room codes, at the cost of building notifications and reconnects
    ourselves. Cheap to decide now; changing after the bridge is built means rewriting it.
    A:
