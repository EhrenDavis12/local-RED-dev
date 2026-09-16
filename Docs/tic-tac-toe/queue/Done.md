# Done

> **What this is:** What shipped in the last 30 days — when, how long it took, the commit,
> and a Grafana link to that item's agent runs and cost.
> **The queue's.** Rows older than 30 days are pruned each tick; `git log` keeps the rest.
> **Hints:** The Grafana link needs the OTEL stack running (`.claude/otel/OTEL-ReadMe.md`),
> and only shows data if the session that did the work had telemetry on.

---
- 2026-09-12 · Research: Supabase as a backend for user accounts, saved user data, and purchase records — what would it take, what does it cost, and what does it change for this app? [research] · 0h 4m · 4ecc507 · http://localhost:3000/d/claude-agents?from=1789157928000&to=1789158185000
  - A: Not needed if the two real needs behind it are solved without it — (1) knowing
    which themes were paid for, which Apple's own purchase records cover, and (2) online
    player-vs-player. Both are now their own research items in Ready; Supabase comes
    back only if that research says nothing else works. (relayed from the user, 2026-09-12)
- 2026-09-12 · Research: App Store in-app purchase vs Stripe for paying for features — what are the advantages of each, which should we use given we want Android one day, and can an app like this connect to Stripe at all? [research] · branch none
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
    A: Yes — one game per platform, separate purchases. Don't link Android and iPhone.
    (relayed from the user, 2026-09-12)
  - Q: What should the paid Sewing theme cost? The docs price the open-games unlock at
    $4.99 but never price the theme. This is typed into App Store Connect, not code —
    changeable anytime, even after launch.
    A: Thinking $2.99 or $4.99 per theme; asked for the market rate and a
    recommendation — see the App Store product setup item, which carries the price.
    (relayed from the user, 2026-09-12)
- 2026-09-12 · Research: online player-vs-player multiplayer — me on my phone against someone on theirs — without Supabase: what server and account options exist (Game Center, Firebase, hosted relay, peer-to-peer, etc.), what each costs and changes for a kids app, and how we'd set it up [research] · branch none
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
    A: Remote. Not two phones in the same room — a friend playing me completely
    remotely from their phone. (relayed from the user, 2026-09-12)
  - Q: Is iOS-only online play acceptable long term, given Android is already out of
    scope? Yes means Game Center (free, no identity collected). No means a small relay
    we host with room codes, at the cost of building notifications and reconnects
    ourselves. Cheap to decide now; changing after the bridge is built means rewriting it.
    A: Yes, iOS-only online play via Game Center is fine if it costs no more money.
    (relayed from the user, 2026-09-12)
- 2026-09-12 · Research: pulling purchase records back from the App Store so the app knows which themes were paid for — what it takes, which API calls (StoreKit / the Flutter in_app_purchase plugin) restore ownership to a device, and a plan we can build from [research] · branch none
  - **What was found (checked 2026-09-12):** yes — Apple keeps the record, and the app can
    read it straight off the device with no server of ours. Apple signs the list of what
    the signed-in Apple ID owns; the phone verifies that signature itself; a refunded or
    revoked purchase simply drops off the list. Reinstalling or installing on a new device
    gets the list automatically at first launch. Family Sharing is a checkbox in App Store
    Connect and needs no app code.
  - **Where the app stands:** nothing purchase-related is built. The purchase and
    entitlement folders are empty, the store plugin isn't a dependency yet, the open-games
    limit is hardcoded to 3 with a note saying "read from entitlements, which don't exist
    yet", every theme row shows FREE, and Settings has no Purchases section or Restore
    button. The iOS 15 floor (needed for the modern StoreKit) is already set.
  - **The calls, in plain terms** (official Flutter `in_app_purchase` plugin, StoreKit 2 is
    now its default):
    - *Every cold launch:* subscribe to the purchase event stream first (this is also
      how a parent's later Ask-to-Buy approval or a refund reaches the app), then ask
      "what does this Apple ID own?" — silent, no password prompt, returns the owned
      product IDs. Save that set as a whole replacement; if the store can't be reached,
      keep the last saved set.
    - *Restore button:* tell Apple to re-sync this device from its servers (this one
      shows an Apple ID password prompt — Apple says use it only behind the button),
      then run the same "what do I own" read.
    - *Buying:* fetch the price from the store, show the parental gate, start the buy,
      then handle the four endings: bought, waiting for a parent, cancelled, error. On
      bought, tell Apple it's finished and re-read the owned set.
    - *Refund:* re-read the owned set whenever any purchase event arrives; the refunded
      item is gone from it. (The plugin quirk: it reports a refund as if it were a
      purchase, so trusting the event's label alone would grant on refund. Re-reading
      the full set sidesteps it and matches the tech design's replace-the-whole-set rule.)
  - **Needs a server?** No. On-device verification is what Apple recommends for this
    shape of app; a server is only for server-side gating or refund webhooks, which the
    design doesn't want. The tech design already says this.
  - **The build plan** (App Store Connect steps marked ASC; the rest is code, in order):
    1. ASC: sign the Paid Applications agreement (banking, tax) — days of lead time, gates all of it.
    2. ASC: create the two non-consumable products (open-games unlock, Sewing theme), Family Sharing on. Product IDs are permanent.
    3. Add the store plugin; add a local StoreKit test file with the same product IDs for Simulator testing; enable the In-App Purchase capability.
    4. Entitlements: a small "what's owned" value (product-ID set + provisional flag + sequence number), cached on disk, with one commit path that never goes backwards.
    5. Store gateway: a thin interface over the plugin (read owned set, sync, buy, prices) plus a fake for tests.
    6. Launch wiring: replace the hardcoded open-games limit with a read from entitlements; read the owned set after first frame; re-read on every purchase event.
    7. Purchase flow: parental gate → buy → the four endings, with "waiting for approval" copy.
    8. Settings → Purchases: unlock row with the store price, Restore button (ungated, as designed).
    9. Theme select: FREE / OWNED / locked per row, from entitlements.
    10. Tests for the commit rules and the gateway against the fake.
    11. Manual: Simulator (buy, refund, Ask-to-Buy approve/decline, clear history + restore), then a sandbox account on a device, then TestFlight.
  - **Contradicts the docs:** the tech design says the Restore button's call *is* Apple's
    sync call. In the plugin those are two different calls — a silent "what do I own"
    read and a separate sync — and the button needs both. It also says a refund "simply
    stops appearing"; true of Apple, but the plugin additionally pushes the refund as an
    event labelled like a purchase (handled above). Doc left alone until you answer.
  - Q: Build the purchase system from this plan now? Saying yes puts it in Ready as a
    [prd] item — it touches money and saved entitlement data, so a wrong guess is
    expensive. The two App Store Connect steps are on you and have the longest lead
    time, so they're worth starting today either way. Nothing here is hard to change
    before code is written.
    A: Yes — start building the systems, including the App Store setup, and do that
    setup as code through fastlane so it's all infrastructure-as-code. No purchase
    point in the app itself yet; just the setup. (relayed from the user, 2026-09-12)
- 2026-09-14 · App Store in-app purchase products as code: a products file plus a fastlane lane that creates and updates the two non-consumable products (open-games unlock, Sewing theme) in App Store Connect, with a dry-run, and the Xcode In-App Purchase capability and a StoreKit test config generated from the same file [look] [M] · 2d 1h · a248369 · http://localhost:3000/d/claude-agents?from=1789232160000&to=1789404000000
  - Applied 2026-09-14: both products now exist in App Store Connect — the open-games
    unlock at $4.99 and the Sewing theme at $1.99, Family Sharing off, English names
    and descriptions set. Re-running the plan lane reports nothing left except
    territory availability, which is deferred until the app's own Pricing and
    Availability is set in App Store Connect (a by-hand step); the next `iap_sync`
    then applies it. Also still by hand: a review screenshot per product, and
    submitting the products with the first app version. The apply surfaced two live
    API facts the docs don't state (a missing schedule is a 404, and inline price ids
    must be `${local-id}`), fixed on the branch. Branch queue/iap-products-as-code
    (6 commits) awaits your review; the Game Center capability row will stack on it
    because both touch the Xcode project file.
- 2026-09-14 · Game Center capability: the entitlement in the Xcode project, the capability on the bundle ID through fastlane, and re-pulled provisioning profiles [look] [S] · 2h 10m · 00b46e5 · http://localhost:3000/d/claude-agents?from=1789407600000&to=1789415400000
  - Live and verified: Game Center is enabled on the bundle ID, the app-level Game
    Center record exists in App Store Connect, the entitlement is in the Xcode project,
    and the App Store profile was regenerated and carries it (pushed to the
    certificates repo). Two lanes: `capabilities_sync` (idempotent) and
    `capabilities_status` (read-only, checks both the store side and the installed
    profile). Branch queue/game-center-capability, stacked on
    queue/iap-products-as-code (both edit the Xcode project). Still by hand at release
    time: enabling Game Center on the app *version* in App Store Connect.
- 2026-09-14 · decide: online play — six decisions the multiplayer build needs [prd] · branch none
  - The user asked on 2026-09-14 to build online play over Game Center: setup, a "Play
    online" button, and match creation (Apple's matchmaker provides find-a-player and
    friend invites). The eleven-row plan is in Proposed (three rows already in Ready).
    Rows that store data or fix the game's shape wait on these:
  - Q: The written goal says the App Store release does not include online play. Does
    the release now wait for online play, or does it go out first and online ships as
    an update? (Goal.md is yours to edit either way.)
    A: Doesn't matter what we're waiting for to release — this is what we're working on
    now. (relayed from the user, 2026-09-14)
  - Q: Do online games count toward the same three-open-games limit as games on this
    phone? If yes, a kid with three games going cannot accept a friend's invite until
    they delete one. Hard to change later — it's written into how games are stored.
    A: Yes — online games count toward the same open-games limit. (relayed from the
    user, 2026-09-14)
  - Q: When should the game ask Apple who the player is? At launch shows every player a
    Game Center welcome banner the first time, even if they never play online; the first
    tap on "Play online" keeps it away from one-phone players. Cheap to change.
    A: Wait until they tap multiplayer, then ask Apple — unless something prevents that
    and it has to happen earlier. (relayed from the user, 2026-09-14. Consequence: the
    app also signs in when it is launched from a Game Center invite or your-turn
    notification, since that is a tap on multiplayer from outside.)
  - Q: How often is the grown-up maths question asked for online play — every new online
    game, only the first time ever, or once per app open? And is it asked when accepting
    a friend's invite, or only when starting one? Cheap to change.
    A: Ask the grown-up question to enter multiplayer — but only when it has to be
    asked: skip it when no parental controls apply. Apple does report this when we ask
    who the player is (it says whether the account is a child's), so the gate is shown
    only for a child account. (relayed from the user, 2026-09-14)
  - Q: If the other player never takes their turn, wait forever or end the game after a
    set time? Apple's default is one week and a week is the shortest it honours in
    practice. And when it ends: the waiting player wins by forfeit, or the game ends
    with no winner? Cheap to change.
    A: Wait forever. Players can delete the game and start a new one. (relayed from the
    user, 2026-09-14)
  - Q: What name is an online game listed under — the other player's Game Center
    nickname (which they chose, could be anything), or a label this player types?
    Moderate to change; the name is fixed when the game is created.
    A: The other player's Game Center nickname. (relayed from the user, 2026-09-14)
- 2026-09-14 · Confirm Game Center turn-based play works on an under-13 Family Sharing account, and that a Kids Category app may ship it [research] [S] · branch none
  - **What was found (checked 2026-09-14):** yes on both counts. A child Apple Account
    can sign in to Game Center and play turn-based games; Apple lists multiplayer as a
    parent-*restrictable* feature (Allow / Friends only / Don't allow), not a disabled
    one, and Game Center enforces the friends-only choice itself — the app only has to
    notice "don't allow" and hide online play with a calm message. Nothing in the App
    Review guidelines or Apple's kids-apps page bars Game Center in a Kids Category app:
    Game Center is Apple, not a third party, so the "no data collected" privacy answer
    holds. No Kids Category game was found shipping Game Center turn-based play, so it
    is unproven rather than prohibited. Children get Apple's safety rails for free: no
    voice, no typed messages, preset invite text only, and the app never sends anything
    but the board.
  - **What Apple's system does for "find a player":** its own sheet lists the player's
    current matches, offers Play Now (random opponent) and Invite Friends (Game Center
    friends and contacts, including sending the invite through Messages). Apple sends
    the "your turn" notification itself. A turn that isn't taken passes after a
    timeout (default one week, and in practice a week is the shortest Apple honours —
    a shorter "abandon" rule would be the app's own logic).
  - **Plan corrections:** the "invite link" API the plan named doesn't exist — Messages
    invites already come free with Apple's sheet, so nothing is lost. The bridge must
    not force "random opponent only" mode (it throws for a friends-only child); it
    uses Apple's default mode and lets the sheet show what's allowed. No Flutter
    package wraps turn-based matches, so the Swift bridge stands.
  - Q: For children, should the app itself refuse random-opponent matching and only
    allow friends, or trust the parent's Game Center setting as Apple designed it
    (parents choose everyone / friends only / off)? Cheap to change later.
    A: Just the parent's Game Center settings. (relayed from the user, 2026-09-14)
- 2026-09-14 · The online-game record: match id, which participant is Player One, whose turn it is, online-vs-local, alongside GameRecord [prd] [M] · 5h 20m · d54d4a2 · http://localhost:3000/d/claude-agents?from=1789412200000&to=1789431400000
  - Full PRD path: 46 requirements, tests first (all 46 covered), 881 tests green, two
    review rounds, harvested into Tech Design (new "What an online game adds to the
    record" subsection and the receive rules under Online Play), PRD deleted. Branch
    queue/online-game-record, stacked on queue/game-center-capability. Note for the
    bridge item: the bridge must save the local move only after Game Center accepts the
    turn, so a stored board never shows the opponent to move on a turn this device did
    not hand off (dropped from the docs as not yet built; the bridge PRD re-decides it).
- 2026-09-15 · Game Center bridge, part one: authenticate, session state, and find a player through Apple's matchmaker [prd] [L] · 9h · f3cb691 · http://localhost:3000/d/claude-agents?from=1789432800000&to=1789465200000
  - Full PRD path: 50 requirements, tests first, 1004 tests green, iOS simulator build
    green, four review rounds (three were Swift-only defects no test can see), harvested
    into Tech Design (four new subsections under Online Play; the one-rename exception
    under Persistence) and Menus and UI; PRD deleted. Branch queue/game-center-bridge-1,
    stacked on queue/online-game-record. Device-pass items for the two-devices row:
    (1) Play Now, invite, cancel, and a declined sign-in on a real device; (2) selecting
    an existing match where it is not your turn fires no completion — the sheet just sits
    until cancelled; (3) while the matchmaker sheet is up, the first turn event wins, so
    an unrelated opponent's turn landing in that window would open the wrong game — part
    two's match-id routing must be verified to close it; (4) UIKit refusing a present
    skips the completion, so that wedge is only mitigated by presenting from the topmost
    controller.
- 2026-09-15 · Parental gate [prd] [M] · 6h 30m · 30485d6 · http://localhost:3000/d/claude-agents?from=1789465800000&to=1789489200000
  - Full PRD path: 32 requirements, tests first, 1127 tests green, two review rounds (the
    second caught a passed raise closing twice when abandoned mid-action), harvested
    into Tech Design (gate rules, two guards, navigation exception, layer) and Menus and
    UI (a Parental Gate section; wording and drawing still open); PRD deleted. Branch
    queue/parental-gate, stacked on queue/game-center-bridge-1. Not yet reachable from
    any screen — the Play online item and the purchase flow call it.
- 2026-09-15 · "Play online" on the main menu, behind the parental gate [look] [S] · 7h · f9f00c4 · http://localhost:3000/d/claude-agents?from=1789495200000&to=1789520400000
  - Look path: plan, tests first (controller table + button), 1159 tests green, played on an
    iPhone SE simulator — which caught the five-button menu clipping on short screens, and
    at large Dynamic Type the title wrapping mid-word; both fixed (compact hero, scroll
    fallback, title scales down). Docs updated: Play online is the fifth main-menu button,
    the flow, short-screen behaviour; the "where does Play online live" question closed.
    Branch queue/play-online-button, stacked on queue/parental-gate. Message wording still
    open. The Game Center flow itself needs a real device with a sandbox account (the
    two-devices row).
- 2026-09-16 · Game Center bridge, part two: end a turn with the board, receive the opponent's turn, quit and resign [prd] [M] · 14h · 8157b4c · http://localhost:3000/d/claude-agents?from=1789524000000&to=1789574400000
  - Full PRD path: 46 requirements, tests first (a two-device relay property test among
    them), 1294 tests green, iOS simulator build green, three review rounds (per-record send
    state, held rematch id captured once, serialized receiver, a throw never poisons the
    queue, resign never wipes a board, fake gates on the session), harvested into Tech
    Design (three channels, receive routing, save-after-accept, rematch handoff, resign on
    delete) and Menus and UI; PRD deleted. Branch queue/game-center-bridge-2, stacked on
    queue/play-online-button. Assumptions recorded in Blocked: delete resigns; the board
    locks while a move awaits handoff. Device-pass notes: the turn-event buffer replays in
    load-completion order, not strict arrival order; a first-ever invite on a phone with no
    online game waits for a Play online tap (question in Blocked).
- 2026-09-16 · The board screen drives a remote turn: input locked when it is not your turn, confirm sends, an arriving turn replaces the board [prd] [M] · 10h · 6928993 · http://localhost:3000/d/claude-agents?from=1789574400000&to=1789610400000
  - Full PRD path: 27 requirements, tests first, 1335 tests green, review clean (two
    hardenings taken), harvested into Tech Design ("The board screen drives a turn"),
    Menus and UI (banner states, online result card) and Game Board Design; PRD deleted.
    Branch queue/board-remote-turn, stacked on queue/game-center-bridge-2. Not yet looked
    at on a device — the online flow needs two devices with sandbox accounts (last row).
