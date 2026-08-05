# PRD: Release & Distribution — fastlane

> **Status:** Draft · Source docs read: Tech Design.md, Game Overview.md, Menus and UI.md,
> Theming.md, Animations.md, Game Board Design.md, Rules.md, roadmap.md, and the read-only
> reference asset `design_handoff_game_ui/`. `Alternative Game Styles.md` is a declared
> parking-lot doc and was not sourced from.

> **Wave:** P5 · **File:** `P5-03-release-fastlane.md` · **Depends on:**
> `P1-01-app-scaffold.md` (the bundle identifier and the iOS minimum are set there; this PRD
> consumes them), `P4-05-purchase-flow.md` (the products this PRD declares and configures in
> App Store Connect), `P4-04-settings.md` (the Settings screen is where both products are
> sold, and where the parental gate the Kids Category requires has to live — Requirement 27),
> and the finished screens in waves P3/P4 — **whose PRDs do not deliver screenshots**; see
> Requirement 22. Nothing depends on this PRD.

> **Requirement numbering is append-only.** Requirements 18–25 were added in round 2 and
> 26–30 in round 3, each numbered last rather than inserted in logical position, so earlier
> numbers keep the values this document has already been reviewed against.

> **Deferred — do not start this now.** *[Tech Design → Decisions → Release tooling —
> fastlane: "Set up when actually approaching shipping — not now."]* This document records
> what was decided so it does not have to be re-decided at ship time. It is not a work item
> until the game is actually approaching shipping.

> **Two things still do not wait for that deferral.** The **parental gate** the Kids Category
> requires is wave-4 build work, not release paperwork *[Tech Design → Decisions → Kids
> category]* — Requirement 27, and as of this writing **neither `P4-04-settings.md` nor
> `P4-05-purchase-flow.md` states it**. The **Paid Applications Agreement, banking and tax**
> is a human, multi-day process that gates Requirements 8, 9 and 25, and starting it late
> delays a ship date by weeks — Requirement 18.

> **The app name is settled: "Tic Tac Toe Extreme."** *[Tech Design → Decisions → App name:
> 20 characters, inside Apple's 30-character App Store limit]* It is the `name` field in
> `fastlane/metadata/<locale>/` (Requirement 3) and what `produce` registers alongside the
> bundle identifier (Requirement 5). This document was previously blocked on it; it is not
> any longer.

## Problem

The game is decided to ship as a **public App Store release**, not a personal build and not
TestFlight-only *[Tech Design → Decisions → Distribution — public App Store release]*. That
makes an App Store Connect listing — description, keywords, screenshots, categories — a real
deliverable, and none of it exists. The game also **sells things** *[Tech Design → Decisions
→ In-app purchases]*, so the record has to declare in-app purchases and carry configured
products, which is a second deliverable on the same account, gated behind a second Apple
agreement nobody has signed. It ships into the **Kids Category** *[Tech Design → Decisions →
Kids category]*, which adds a mandatory privacy policy to a project with no website and puts
a parental gate into features that ship in wave 4. Beyond the tooling, *[Tech Design → Open
Questions → 3. Build and distribution]* enumerates a set of hard submission blockers — the
Paid Applications Agreement, export compliance, content rights, review contact details,
sandbox testing, screenshots — and records that they are unowned; before this PRD they were
unrepresented in all 24 PRDs. There is no signing setup, no app record, and no way to push a
build from a laptop. Separately, *[Tech Design → Decisions → CI — local builds only]* means
nothing runs `flutter test` or `flutter analyze` on a push, so whatever the release procedure
checks is the only thing checked.

## Goal

When this is done, the app has an App Store Connect record under its permanent bundle
identifier and its settled name, listed in the Kids Category at 4+, declaring in-app
purchases and holding the configured products, with the agreements and account details that
make a paid app submittable in place, signing material stored and synced from a git repo
rather than living on one machine, the entire store listing existing as text files in the
repo that are edited and committed like code, and a single fastlane run from the CLI pushing
the listing and a build to App Store Connect. Review itself — for the app and for the
purchase products — is still submitted and waited on by hand.

## Requirements

### The tooling and the listing

1. **The release is a public App Store release** — not a personal build, not TestFlight-only
   — and the App Store Connect listing (description, keywords, screenshots, categories) is
   a deliverable of this PRD. *[Tech Design → Decisions → Distribution — public App Store
   release]*

2. **fastlane is the release tooling.** The App Store listing is kept as local text files,
   edited and committed like code, and pushed to App Store Connect from the CLI. *[Tech
   Design → Decisions → Release tooling — fastlane]* Testable: the listing content lives in
   the repo and a `git diff` shows a listing change as a text diff.

3. **`deliver` (aka `upload_to_app_store`) owns the listing files, in the two-tier layout
   the decision specifies.**
   - **Localized fields — one file per field per locale**, under a per-locale directory in
     `fastlane/metadata/`: **description, keywords, release notes, name, subtitle**.
   - **Non-localized fields — one file per field at the top level** of
     `fastlane/metadata/`: **primary and secondary category, copyright**.
   - `fastlane/screenshots/` holds the images.

   Edit locally, commit, run, and it pushes to App Store Connect. *[Tech Design → Decisions
   → Release tooling — fastlane → `deliver`]* **The `name` field's value is "Tic Tac Toe
   Extreme"** *[Tech Design → Decisions → App name]* — 20 characters, inside Apple's
   30-character limit, so no truncation question arises. `copyright` remains a field no
   requirement or doc supplies a value for. Testable up to the point of upload: every
   localized field resolves under a locale directory and every non-localized field at the top
   level, and a `deliver` validation run passes against that tree. *(An earlier draft of this
   requirement put categories in the per-locale tier and claimed a validation run would pass —
   those two clauses could not both be true, because `primary_category` is exactly what a
   per-locale layout is rejected for.)*

4. **`match` stores signing certificates and provisioning profiles in a git repo and syncs
   them.** *[Tech Design → Decisions → Release tooling — fastlane]* Testable: a machine with
   no local signing material can run `match` and produce a signed build.

5. **`produce` creates the app record and registers the bundle identifier and the app name
   from the CLI** — the app record is not hand-created in the App Store Connect web UI. The
   name it registers is **"Tic Tac Toe Extreme"**. *[Tech Design → Decisions → Release
   tooling — fastlane; App name]*

6. **All of it runs on Apple's official App Store Connect API underneath.** *[Tech Design →
   Decisions → Release tooling — fastlane]* Concretely, the fastlane setup authenticates via
   an App Store Connect API key rather than any other mechanism.

7. **The registered bundle identifier is `com.ehrendavis.tictactoeextreme`** — the value the
   scaffold already sets, not a value chosen here. *[Tech Design → Decisions → Bundle
   identifier]* The doc's own warning applies at the moment `produce` runs: **a bundle
   identifier is effectively permanent once the app has been submitted to App Store Connect,
   so it is not a name to revisit casually.**

### In-app purchases on the store side

8. **The App Store Connect record declares in-app purchases.** The game sells two things:
   **themes beyond the two free ones (Neon and Classic Red vs Blue)**, and a **$4.99 unlock
   raising the open-game cap from 3 to 100.** *[Tech Design → Decisions → In-app purchases;
   Theming → Decisions → Which themes are free; Menus and UI → Decisions → How many open
   games do we keep?]* A release that ships the app without declaring IAP is wrong, not
   merely incomplete. Blocked by Requirement 18.

9. **The products configured in App Store Connect are exactly the products the app queries,
   and no others.** What is settled is one product: **the $4.99 open-game cap unlock**, which
   is the only purchasable thing with both a decided existence and a decided price *[Tech
   Design → Decisions → In-app purchases; Menus and UI → Decisions → How many open games do
   we keep?]*, **sold from the Settings screen's purchases section** *[Menus and UI →
   Decisions → Where the open-game slot unlock is sold: "**The Settings screen.** The Settings
   screen gains a purchases section holding the $4.99 open-game-slot unlock and a global
   **Restore purchases** control"]* — the surface is settled, so nothing here waits on it.
   **No paid-theme product is configured by this PRD as written**, because
   `P4-05-purchase-flow.md` Requirement 9 establishes that **zero locked themes ship** (both
   launch themes are free), its Out of Scope declines to build a theme storefront, and its
   Open Question 1 records that whether paid themes are one product, one per theme, or a
   bundle is **undecided**. Configuring per-theme products here would create store entries
   the app never queries — and `P4-05` Requirement 1 asserts the app queries no identifier
   outside the two things it sells, so its test and this one only agree under this reading.
   Testable: the set of configured product identifiers and the set the app queries are the
   same set — no configured product the app never asks for, and no identifier the app asks
   for that returns unknown. **The identifiers themselves do not exist yet** — see Open
   Question B.

10. **Do not overstate what fastlane covers here.** `produce` creates the app record and
    `deliver` pushes the listing, but **in-app purchase products are configured separately
    and are their own review surface** — each product carries its own metadata and review
    state and can be rejected independently of the app. Nothing in Requirements 2–6
    automates that. *[Tech Design → Decisions → Release tooling — fastlane, which scopes the
    three fastlane pieces to the app record, the listing and signing; In-app purchases,
    which adds the products]* Manual process step.

11. **StoreKit is the one thing that reaches the network, and what it reaches is Apple.** The
    app is otherwise fully offline — no backend, no accounts — with StoreKit needing network
    access and a restore-purchases path tied to the Apple ID, and **entitlements living with
    Apple rather than on any server of ours**: `Transaction.currentEntitlements`, verified on
    device, is the record of truth. *[Tech Design → What the Design Docs Already Imply →
    "Fully offline, except for in-app purchases … The exception is a StoreKit query against
    Apple, not a service we run"; Decisions → Entitlements — Apple stores them, no backend
    needed]* This is what the release has to describe truthfully in the places Apple asks —
    see Requirement 30.

### The build being submitted

12. **The submitted build targets iOS, with iPhone first and iPad second.** Android is "far
    future" and is not part of this release. *[Tech Design → Decisions → Device support;
    Primary target — Apple]* "All media devices" is recorded as stated and **is not yet
    scoped to particular platforms**, so nothing here plans for one. Whether the submitted
    build is iPhone-only or universal is not settled anywhere and is not decided here; it
    determines the screenshot device sizes Requirement 22 has to produce.

13. **The submitted build's minimum deployment target is iOS 13**, as set by the scaffold.
    *[Tech Design → Decisions → Minimum iOS version]*

14. **Set up when actually approaching shipping — not now.** *[Tech Design → Decisions →
    Release tooling — fastlane]* This is a scheduling requirement, not something to test:
    the work in this PRD is not begun until the game is approaching ship — **except** the two
    items called out at the top, which cannot wait.

15. **An Apple Developer Program membership is a prerequisite.** None of the above works
    without one. *[Tech Design → Decisions → Release tooling → "Watch out for"]* Manual
    process step — obtained by a human before any fastlane action is attempted. **This is not
    the same agreement as the Paid Applications Agreement in Requirement 18**; membership
    alone does not let the app sell anything.

16. **App Review is not automated.** fastlane uploads; submission to review and the review
    itself stay manual — for the app and, per Requirement 10, for each purchase product.
    *[Tech Design → Decisions → Release tooling → "Watch out for"]* Manual process step,
    with no automated equivalent to build.

17. **No CI is added here. Builds stay local.** `flutter test` and `flutter analyze` run
    locally. *[Tech Design → Decisions → CI — local builds only]*
    *Consequence, not an additional requirement:* nothing runs those commands on a push, so
    by the time a build reaches this pipeline it has passed no automated gate. The release
    procedure is the last line of defense rather than a checkpoint after several earlier
    ones. Whether the release lane itself is required to run them before uploading is not
    decided anywhere — see Open Questions.

### Submission prerequisites and blockers

*[Tech Design → Open Questions → 3. Build and distribution]* enumerates these as "a set of
hard App Store submission blockers, none of which any doc currently mentions, and all of
which must be decided before shipping." They are listed there under Open Questions, so **the
citation is to a blocker list, not to a Decision** — what is settled is that each stands
between the app and the store, not how any of them is answered. Where the work is
unambiguously this PRD's, it is a requirement below; where the answer is a product or
business call, it is an Open Question instead.

18. **The Paid Applications Agreement is executed, and banking and tax details are on file,
    before anything is sold.** *[Tech Design → Open Questions → 3: "required before anything,
    including any in-app purchase, can be sold. A human, multi-day process with no automation
    path."]* Manual process step, with no fastlane equivalent. **This is the hardest blocker
    in the list and it gates Requirements 8, 9 and 25** — all three silently assumed it was
    done. Nothing in this PRD's tooling detects that it is missing; App Store Connect simply
    will not let the products exist.

19. **Export compliance is answered for every upload.** *[Tech Design → Open Questions → 3:
    "asked on every upload; can be pre-answered with an `Info.plist` key, which is the
    scaffold's file."]* This PRD owns giving the answer at upload time. **The pre-answer is
    unowned on both ends:** `P1-01-app-scaffold.md` has no `Info.plist` requirement at all, so
    no PRD puts the key in the file, and this PRD does not write iOS project files. Until that
    lands, the answer is given by hand on every single upload. Manual process step; testable
    only in the negative — an upload that stalls awaiting compliance means the key is absent.

20. **The App Review contact information is supplied on the record.** *[Tech Design → Open
    Questions → 3: "App Review contact information"]* Manual process step, owned here because
    it is a field on the submission and nowhere else.

21. **The purchase flow is exercised against a real App Store sandbox account before
    submission.** *[Tech Design → Open Questions → 3: "sandbox testing of the purchase flow
    before submission"]* This is release-time verification and it belongs here, because
    `P4-05-purchase-flow.md` Requirement 11 deliberately makes the store substitutable and its
    whole suite runs "with no network and no store account configured" — so **every automated
    test of buying and restoring runs against a double, and nothing in the pipeline ever
    touches the real store.** The path to exercise is concrete now that the surface is
    settled: Settings → purchases section, through the parental gate *[Menus and UI →
    Decisions → Where the open-game slot unlock is sold; Tech Design → Decisions → Kids
    category]*. Testable as a manual pass: a sandbox purchase of the cap unlock raises the
    reported cap to 100 on a real device, and a restore on a second device recovers it.

22. **Screenshots are captured at Apple's required device sizes and committed to
    `fastlane/screenshots/`, and this PRD owns capturing them.** *[Tech Design → Open
    Questions → 3: "Screenshots at Apple's required device sizes — who captures them, and by
    what means, is unowned."; Decisions → Distribution — public App Store release, which names
    screenshots as part of the deliverable]* Ownership is accepted here because **no P3 or P4
    PRD accepts it** — none mentions screenshots, names a device size, or specifies a capture
    mechanism, so an earlier draft of this document deferred the work to PRDs that do not
    perform it. What waves P3/P4 supply is the **screens**; turning them into store images is
    release work. Which device sizes are required follows from the iPhone-only vs universal
    question flagged in Requirement 12, and the capture mechanism — by hand on a device or
    simulator, or fastlane's `snapshot` — is not decided anywhere; see Open Question C.

23. **The submitted build carries a 1024×1024 app icon in the iOS asset catalog.** *[Tech
    Design → Decisions → The app icon: "The app ships an icon, and it is not the main-menu
    logo. App Store submission cannot happen without a 1024×1024 icon. It lives in the iOS
    asset catalog rather than the Flutter `assets/` tree, and it is a separate asset from the
    logo."]* What is unowned is production and placement:
    `P5-02-asset-generation-replicate.md` Requirement 3 forbids writing outside `assets/` and
    raises the conflict without resolving it, `P1-01-app-scaffold.md` creates no asset-catalog
    entry, and this PRD does not write iOS project files. **No PRD currently puts an icon in
    the catalog**, and *who produces it, and whether it is generated or hand-made*, is open
    *[Tech Design → Open Questions → 3]*. Testable: the archived build's asset catalog
    contains the 1024×1024 marketing icon; upload fails without it.

24. **Content rights are established before the submission question is answered.** *[Tech
    Design → Open Questions → 3: "the submission asks whether the app contains third-party
    content, and the answer depends on the licensing of Replicate-generated assets and of the
    bundled Inter and Phosphor dependencies, none of which is established."]* This PRD owns
    answering the question at submission; **it cannot own establishing the facts**, which
    concern the Replicate model output terms *[Tech Design → Decisions → Where do sound and
    art assets come from?]* and two bundled third-party dependencies *[design_handoff_game_ui/
    README.md → Assets]* that no PRD's licensing position is written down for. Manual process
    step, blocked until someone establishes them — see Open Question D.

25. **Price tier and territory availability are set on the record before release.** *[Tech
    Design → Open Questions → 3: "App Store category, price tier, and territory
    availability."]* This PRD owns entering the values; **it does not choose them** — the
    app's own price and the territory set are product calls, recorded as Open Questions below.
    The *category* half of that blocker is now answered for the primary category by
    Requirement 26. Blocked by Requirement 18 for anything involving money.

### The Kids Category and what it obliges

26. **The record lists the app in Apple's Kids Category, with an age rating of 4+.** *[Tech
    Design → Decisions → Kids category: "The app will be listed in Apple's Kids Category …
    A separate, consequent fact: the age rating is **4+.**"]* This is a Decision, not a
    listing-time choice — **an earlier draft of this document filed it as a question to settle
    at submission, which the doc now contradicts directly.** The category is a field on the
    record (Requirement 25 enters it); the three obligations below are what make it more than
    a field.

27. **The build submitted under the Kids Category carries a parental gate before the purchase
    flow, and this PRD does not build it.** *[Tech Design → Decisions → Kids category: "A
    **parental gate** is required before any purchase flow and before any link that leaves the
    app … the gate has to exist before those are built rather than being added at submission";
    "**The parental gate's scope is purchases only.** The game has no outbound links today"]*
    The work lands in `P4-04-settings.md` (the screen that hosts the purchases section) and
    `P4-05-purchase-flow.md` (the flow the gate precedes), **both wave 4, well before this
    PRD** — which is why it is a dependency here rather than something to implement here.
    **Flagged, not fixed:** as of this writing neither of those PRDs mentions a parental gate
    or the Kids Category at all, so nothing currently schedules the work — see Open Question
    F. A release blocked at review for a missing gate is the failure this records. What the
    gate looks like and how it challenges is *"a PRD's job, not this doc's"*, and not this
    PRD's either. Scope note: **purchases only** — the game has no outbound links today, and
    if one is ever added it needs the gate too. *Testable at release time:* a build that
    reaches the purchases section without a gate is not submittable under this category.

28. **The submitted build contains no third-party analytics and no behavioural advertising,
    and the release introduces none.** *[Tech Design → Decisions → Kids category:
    "Third-party analytics and behavioural advertising are restricted."]* The app has neither
    today, so this records a constraint that must **stay** true rather than a change to make:
    `P1-06-crash-reporting.md` excludes "analytics, usage metrics, or any other data
    collection", crash reports are built and never transmitted *[Tech Design → Decisions →
    Crash reporting]*, and `P4-05-purchase-flow.md` Requirement 7 admits no network target
    other than the store. Testable: a dependency and outbound-call scan over `lib/` and
    `pubspec.yaml` finds no analytics or advertising SDK and no network target other than
    StoreKit — the same check `P1-01-app-scaffold.md` Requirement 6 already writes in wave 1.

29. **A privacy policy exists and its URL is on the record before submission.** *[Tech Design
    → Decisions → Kids category: "A privacy policy is mandatory."]* The Kids Category turns
    this from a listing field into a hard external prerequisite — **and the project has no
    website of any kind** *[Tech Design → Open Questions → 3]*, so something has to exist to
    host it, alongside the support URL the same blocker names. Writing and hosting the policy
    is outside this PRD and outside the repo; this PRD owns only putting the URL on the
    record. Manual process step, blocked externally. Where it is hosted stays an Open
    Question.

30. **What the record declares about data collection is shaped by there being no backend.**
    The app declares in-app purchases (Requirement 8), uses StoreKit, and **operates no server
    of its own** — entitlements live with Apple and are verified on device, so there is no
    account we hold, no receipt-validation service, and no data we collect *[Tech Design →
    Decisions → Entitlements — Apple stores them, no backend needed; What the Design Docs
    Already Imply → the qualified "Fully offline" row; Decisions → Crash reporting, which
    builds reports and transmits none]*, and per Requirement 28 no analytics SDK either. The
    privacy nutrition label has to say that truthfully. **The questionnaire answers themselves
    are still open** — see Open Questions — but the facts they describe are settled, and they
    are unusually simple ones.

## Out of Scope

Referenced by filename rather than specified here:

- **The in-app purchase implementation** — StoreKit integration, the purchase sheet, restore
  purchases, and the product set — `P4-05-purchase-flow.md`. **The entitlement model** — what
  the player owns, the free-tier defaults, and how the cap of 3 becomes 100 —
  `P1-07-entitlements.md`. This PRD owns only the store-side declaration and product
  configuration those need to exist against, plus the sandbox verification in Requirement 21.
- **The parental gate** — what it looks like, how it challenges, and where it sits relative to
  the Settings purchases section — `P4-04-settings.md` and `P4-05-purchase-flow.md`.
  Requirement 27 states that the submitted build must have one and that neither PRD currently
  says so.
- **Setting the bundle identifier, the iOS minimum, and any `Info.plist` key in the
  Flutter/Xcode project** — `P1-01-app-scaffold.md`. This PRD *consumes* those values; it does
  not write iOS project files. See Requirement 19 for what that leaves unowned.
- **Producing the app icon artwork.** Requirement 23 requires the submitted build to carry
  one; who makes it is open, and `P5-02-asset-generation-replicate.md` is where a generated
  answer would live if that is the answer.
- **Writing and hosting the privacy policy and support pages.** Requirement 29 puts the URL
  on the record; the content and its hosting are outside the repo and unowned.
- **The screens themselves** — waves P3/P4. Requirement 22 keeps the *capture* of screenshots
  here rather than pushing it onto PRDs that do not accept it.
- **Crash reporting.** Errors are caught and the report object is built, but it has no
  transport — `P1-06-crash-reporting.md`. No crash or analytics service is wired up as part
  of shipping, and per Requirement 28 none may be. **This PRD does not accept that PRD's dSYM
  delegation** — see Open Question E.
- **Asset generation** — the logo and sound assets are *"not now"* by decision *[Tech Design
  → Decisions → Where do sound and art assets come from?]* →
  `P5-02-asset-generation-replicate.md`, a same-wave sibling.
- **Alternative Game Styles.md** — parking lot, not what is being built.

## Open Questions

### From the design docs — unresolved, worded as the docs word them

- **A. The exact age-rating questionnaire answers.** *[Tech Design → Open Questions → 5. Kids
  category — age rating questionnaire]*, which now records that "the Kids-category listing
  choice and the resulting parental-gate, analytics, and privacy-policy requirements are
  settled … What remains open is the exact age-rating questionnaire answers." The category
  (Requirement 26), the gate (27), the analytics constraint (28) and the privacy policy (29)
  have moved out of this section and into requirements. What is left is filling in Apple's
  questionnaire so that it produces the 4+ rating the decision states.

- **The privacy nutrition label.** *[Tech Design → Open Questions → 3]* Still unanswered as a
  set of questionnaire answers, though Requirement 30 records that the underlying facts — no
  backend, no accounts we operate, no analytics, no transmitted crash reports, StoreKit
  against Apple only — are settled and simple.

- **Where the privacy policy and support URLs are hosted.** *[Tech Design → Open Questions →
  3: "A privacy policy URL and a support URL — both required listing fields. The project has
  no website of any kind."]* Requirement 29 makes the policy mandatory rather than optional;
  it does not conjure somewhere to put it.

- **Who produces the app icon, and is it generated or hand-made?** *[Tech Design → Open
  Questions → 3]* The icon itself is decided (Requirement 23); only its production is open,
  and no PRD currently places one in the asset catalog.

- **Price tier and territory availability.** *[Tech Design → Open Questions → 3]* Requirement
  25 enters these; nothing chooses them. One in-app purchase price *is* decided — $4.99 for
  the open-game-cap unlock *[Menus and UI → Decisions → How many open games do we keep?]* —
  while what the app itself costs to download and which territories it is available in are
  not stated anywhere. The secondary App Store category is likewise unchosen; the primary is
  settled by Requirement 26.

### Found while writing this PRD — not settled anywhere, and flagged rather than answered

These are gaps I noticed, not proposals with any authority behind them. Each is a place the
person running the release would otherwise have to guess.

- **B. The product-identifier circle is unbroken, and no PRD breaks it.** This document said
  the identifiers "come from `P4-05-purchase-flow.md`"; that PRD's Open Question 4 says "**No
  product identifiers exist.** No doc names a product ID for either product, and this PRD
  invents none. Something must, before the store can be queried or a purchase started
  (`P5-03-release-fastlane.md` registers them)." **Each names the other, so neither invents
  one.** Recording it as a gap rather than a pointer: an identifier scheme has to be chosen by
  someone, and it is a naming decision with the same permanence problem as the bundle
  identifier — a product ID cannot be reused once created. This is independent of the
  still-open question of *how many* products there are.
- **C. How screenshots get captured, and at which device sizes.** Requirement 22 accepts the
  work; nothing decides the mechanism (by hand on a device or simulator, or fastlane's
  `snapshot`, which would be a fourth fastlane component beyond the three the decision names)
  or the device-family set, which depends on the unresolved iPhone-only vs universal question.
- **D. Nothing establishes the licensing this PRD has to attest to.** Requirement 24 answers
  the content-rights question at submission, but the underlying facts — the terms attached to
  Replicate model output, and the licenses of the bundled Inter 400/500/600 and Phosphor icon
  set — are not written down in any doc or PRD. `P5-02-asset-generation-replicate.md` generates
  assets without stating their terms; `P1-01-app-scaffold.md` Open Questions leaves whether
  the scaffold even bundles Inter and Phosphor unsettled.
- **E. dSYMs and symbolication are unowned, and both documents now say so.**
  `P1-06-crash-reporting.md` → Out of Scope points *"Symbolication and dSYM handling"* at this
  PRD — correctly addressed, and it records the refusal in the same breath: *"pointed at
  `P5-03-release-fastlane.md`, which is the right destination if it ever becomes anyone's, but
  **that PRD declines the delegation and nothing else picks it up** … **Recorded as an open
  gap, not a settled hand-off:** it is unowned today, and it becomes release tooling's the day
  a destination is chosen."* **The answer from this side, unchanged: this PRD does not own
  dSYMs today.** No design doc mentions symbolication, dSYM upload, or a crash-report
  destination — crash reports are built and deliberately never transmitted *[Tech Design →
  Decisions → Crash reporting]*, so there is nothing to symbolicate for and no service to
  upload a dSYM to. Writing a dSYM requirement here would invent the destination that decision
  explicitly withholds. If a destination is ever chosen, the upload step is release tooling
  and belongs here; until then it is a gap both documents record identically, not a
  requirement.
- **F. No wave-4 PRD schedules the parental gate.** Requirement 27 records the obligation, and
  `Tech Design.md` is explicit that the gate "has to exist before those are built rather than
  being added at submission" — but `P4-04-settings.md` and `P4-05-purchase-flow.md` do not
  mention a gate or the Kids Category, and this PRD is downstream of both. Raised so it is not
  discovered at review, and flagged rather than fixed: those files are not this PRD's to edit.
- **Versioning and build numbers.** No doc says what version the first release carries, how
  the version is bumped, or whether the build number is incremented by fastlane
  (`increment_build_number`) or by hand. `deliver` refuses to upload without a unique build
  number, so this gets decided at the keyboard by default if it is not decided first.
- **Where the `match` certificate repo lives.** The decision says the certificates and
  profiles are stored in a git repo and synced; it does not say *which* repo, whether it is
  private, or how the `match` passphrase is held. This is credential material, so the
  default answer is not obviously safe.
- **Which locales ship.** `deliver`'s localized tier is one file per field **per locale**,
  which makes the locale set a real decision — and `copyright`, `primary_category` and
  `secondary_category` sit outside it either way. No doc names a locale, and nothing else in
  the project discusses localization at all. `P3-05-how-to-play.md` → Out of Scope makes the
  same point from the copy side: *"Localisation. No design doc raises it; the strings above
  are specified in English as the docs word them."*
- **Which paid theme products exist, and at what prices.** *[Theming → Decisions → Which
  themes are free]* settles that everything beyond Neon and Classic Red vs Blue is paid, but
  names no further theme and no price, and no paid theme ships at launch
  (`P4-05-purchase-flow.md` Requirement 9). Requirement 9 above configures none until that and
  the product-structure question (`P4-05` Open Question 1) are answered.
- **Whether the fastlane lane runs `flutter analyze` and `flutter test` before uploading.**
  See Requirement 17 — the decision is that these run locally and nothing runs them on a
  push; whether the release lane is one of the places they run is not stated.
