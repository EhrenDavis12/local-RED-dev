**Build-readiness: 82** — *author's estimate after round-4 fencing, not a grade. Last formal
grade **42** (actionability 7, verifiability 11, decision completeness 6, interface precision
8, self-containment 10). What holds it under 85 is not vagueness but three things no reading
settles: **no product identifiers exist** (Open Question B), **the Paid Applications Agreement
is unsigned** (Requirement 18), and **nobody supplies the app icon** (Requirement 23). Answer
those and everything else here is executable.*

# PRD: Release & Distribution — fastlane

> **Status:** Draft · Source docs read: Tech Design.md, Game Overview.md, Menus and UI.md,
> Theming.md, Animations.md, Game Board Design.md, Rules.md, roadmap.md, and the read-only
> reference asset `design_handoff_game_ui/`. `Alternative Game Styles.md` is a declared
> parking-lot doc and was not sourced from.

> **Wave:** P5 · **File:** `P5-03-release-fastlane.md` · **Depends on:**
> `P1-01-app-scaffold.md` (the bundle identifier, the iOS minimum and the platform/device
> family are set there; this PRD consumes them), `P4-05-purchase-flow.md` (the products this
> PRD declares and configures in App Store Connect, and the owner of the parental gate),
> `P4-04-settings.md` (the purchases section that hosts the buy and restore controls),
> `P5-02-asset-generation-replicate.md` **Stage 2** (see below), and the finished screens in
> waves P3/P4 — **whose PRDs do not deliver screenshots**; see Requirement 22. Nothing depends
> on this PRD.

> **Which asset-generation stage this depends on: Stage 2, not Stage 1.**
> `P5-02-asset-generation-replicate.md` splits into *"**Stage 1 — the tool.** The script, its
> prompt manifest and its metadata file. No asset is generated, no `pubspec.yaml` line is added,
> and no model is chosen"* and *"**Stage 2 — the first real generation run.** Assets land, and
> the `pubspec.yaml` declarations of Requirement 9 land **in the same change**"* — the split
> exists because declaring an empty asset directory fails the Flutter build
> (`P1-01-app-scaffold.md` requirement 3). A submitted build has to contain the sounds and logo
> its shipping themes reference, so **first submission cannot precede that PRD's Stage 2**.
> Stage 1 alone leaves an app that builds but ships placeholder-free themes with nothing behind
> their asset paths. **The app icon is in neither stage** unless the user says it is —
> Requirement 23.

> **Requirement numbering is append-only.** 18–25 were added in round 2, 26–30 in round 3 and
> 31–39 in round 4, each numbered last rather than inserted in logical position, so earlier
> numbers keep the values this document has already been reviewed against.

> **Deferred — do not start this now.** *[Tech Design → Decisions → Release tooling —
> fastlane: "Set up when actually approaching shipping — not now."]* This document records
> what was decided so it does not have to be re-decided at ship time.

> **One thing does not wait for that deferral.** The **Paid Applications Agreement, banking
> and tax** is a human, multi-day process that gates Requirements 8, 9, 25 and 34, and
> starting it late delays a ship date by weeks — Requirement 18.

> **Fences.** Several requirements below pick a concrete value the design docs do not state —
> the lane names, the locale, the version, the credential mechanism. Each is marked **Fence**
> and each is **reversible until something cites it**; the alternative is an implementer
> choosing silently. Where a fence touches money, legal identity or credentials it says so and
> asks for confirmation before first submission rather than assuming.

## Problem

The game ships as a **public App Store release** *[Tech Design → Decisions → Distribution —
public App Store release]*, so the App Store Connect listing — description, keywords,
screenshots, categories — is a real deliverable, and none of it exists. The game **sells
things** *[Tech Design → Decisions → In-app purchases]*, so the record must declare in-app
purchases and carry configured products, gated behind a second Apple agreement nobody has
signed. It ships into the **Kids Category** *[Tech Design → Decisions → Kids category]*, which
makes a privacy policy mandatory for a project with no website. And *[Tech Design → Open
Questions → 3. Build and distribution]* enumerates hard submission blockers — export
compliance, content rights, review contact details, sandbox testing, screenshots — recording
that they are unowned. There is no signing setup, no app record, no lane, and no way to push a
build from a laptop. Separately, *[Tech Design → Decisions → CI — local builds only]* means
nothing runs `flutter test` or `flutter analyze` on a push, so whatever the release procedure
checks is the only thing checked.

## Goal

When this is done, `bundle exec fastlane release` from the iOS project directory runs the
local checks, syncs signing material, builds the app and uploads the build and the listing to
App Store Connect — against a record under the settled bundle identifier and name, listed in
the Kids Category at 4+, declaring in-app purchases and holding non-consumable products, with
the agreements, account details and credentials that make a paid app submittable in place, and
the entire listing living in the repo as text files edited and committed like code. Review
itself — for the app and for each product — is still submitted and waited on by hand, against
a written checklist rather than memory.

## Requirements

### The lanes and the files

31. **Fence — the fastlane project exists at `src/Tic-Tac-Toe-Extreme/ios/fastlane/`**, the
    standard location for a Flutter app's iOS release, holding `Fastfile`, `Appfile`,
    `Matchfile` and `Deliverfile`, with `Gemfile` and `Gemfile.lock` at
    `src/Tic-Tac-Toe-Extreme/ios/` pinning the fastlane version. Every `fastlane/…` path in
    this document is relative to that directory. *[Tech Design → Decisions → Release tooling —
    fastlane names the tool, the three components and the `fastlane/metadata/` and
    `fastlane/screenshots/` trees, but no location; the location is this PRD's fence.]*
    *Testable:* the five files exist at those paths and `bundle exec fastlane lanes` lists the
    lanes of Requirement 32 without error.

32. **Fence — four lanes, named, with `release` composed in this order.**

    | Lane | Does |
    |---|---|
    | `certs` | `match(type: "appstore", readonly: true)` — fetch signing material, create nothing |
    | `screenshots` | collect the images of Requirement 22 into `fastlane/screenshots/` |
    | `metadata` | `upload_to_app_store(skip_binary_upload: true, skip_screenshots: false)` — push listing text and images without a build |
    | `release` | the full path: local checks → `match(type: "appstore")` → `increment_build_number` → `build_app` → `upload_to_app_store` |

    Nothing downstream can invoke a lane this document does not name; before this requirement
    the Goal promised "a single fastlane run" and named none. *[Composition follows Tech
    Design → Decisions → Release tooling — fastlane, which names `match`, `deliver`
    (`upload_to_app_store`) and `produce`; the lane names and the split are this PRD's
    fence.]* `produce` is not a lane — it runs once, by hand, to create the record
    (Requirement 5).
    *Testable:* `bundle exec fastlane release --dry-run`-equivalent inspection shows the four
    actions in that order; `metadata` completes without producing a build.

33. **Fence, and a security fence — credentials never enter the repository.**
    - **App Store Connect API key:** the lanes authenticate through `app_store_connect_api_key`
      reading **`ASC_KEY_ID`**, **`ASC_ISSUER_ID`** and **`ASC_KEY_CONTENT`** from the
      environment. The `.p8` file lives **outside the repository** and is never committed in
      any form. *[Requirement 6 requires the official API; it named no mechanism, which left
      the highest-consequence guess in this document to an implementer.]*
    - **`match`:** `type: "appstore"`, `git_url` from **`MATCH_GIT_URL`**, passphrase from
      **`MATCH_PASSWORD`**, and **the certificate repository must be private**. *Which* repo
      is the user's call (Open Questions); that it is private and env-supplied is not.
    - **`.gitignore`** (in the iOS project) excludes `*.p8`, `fastlane/report.xml`,
      `fastlane/Preview.html`, and any local `.env` file.

    **Why this is a fence and not a preference:** Requirement 2 establishes "it lives in the
    repo and a `git diff` shows the change" as this feature's house pattern, which reads as an
    instruction to commit files. That pattern covers **listing text and images only**. A `.p8`
    committed to a repository is an unrecoverable credential leak — the key cannot be
    un-published, only revoked.
    *Testable:* a scan of the working tree and of `git log -p` finds no `.p8`, no
    `-----BEGIN PRIVATE KEY-----` block and no `MATCH_PASSWORD` literal; the `certs` lane
    succeeds with the three `ASC_*` variables set and fails cleanly with them unset.

39. **A written submission checklist exists at `fastlane/RELEASE-CHECKLIST.md`, and every
    requirement in this PRD marked *Manual process step* appears on it** with a place to
    record who did it and when. Nine requirements here are human steps with no artifact;
    without a checklist nothing makes them checkable, and the first evidence of a missed one
    is a rejected submission. *(This PRD's own accounting; no design doc asks for it.)*
    *Testable:* every requirement whose text contains "Manual process step" — 10, 15, 16, 18,
    19, 20, 21, 24, 29 — has a line in that file.

### The tooling and the listing

1. **The release is a public App Store release** — not a personal build, not TestFlight-only
   — and the App Store Connect listing (description, keywords, screenshots, categories) is
   a deliverable of this PRD. *[Tech Design → Decisions → Distribution — public App Store
   release]*

2. **fastlane is the release tooling.** The App Store listing is kept as local text files,
   edited and committed like code, and pushed to App Store Connect from the CLI. *[Tech
   Design → Decisions → Release tooling — fastlane]* **Scope of "kept in the repo": listing
   text and screenshots only — never credentials (Requirement 33).**
   *Testable:* the listing content lives in the repo and a `git diff` shows a listing change
   as a text diff.

3. **`deliver` (aka `upload_to_app_store`) owns the listing files, in the two-tier layout
   the decision specifies.**
   - **Localized fields — one file per field per locale**, under a per-locale directory in
     `fastlane/metadata/`: **description, keywords, release notes, name, subtitle**.
   - **Non-localized fields — one file per field at the top level** of
     `fastlane/metadata/`: **primary and secondary category, copyright**.
   - `fastlane/screenshots/` holds the images.

   *[Tech Design → Decisions → Release tooling — fastlane → `deliver`]* **The `name` field's
   value is "Tic Tac Toe Extreme"** *[Tech Design → Decisions → App name]* — 20 characters,
   inside Apple's 30-character limit, so no truncation question arises. The locale directory
   and the `copyright` value are fenced in Requirement 35.
   *Testable:* every localized field resolves under a locale directory and every non-localized
   field at the top level, and a `deliver` validation run passes against that tree. *(An
   earlier draft put categories in the per-locale tier and claimed validation would pass —
   both cannot be true, because `primary_category` is exactly what a per-locale layout is
   rejected for.)*

35. **Fence — one locale, `en-US`, and a `copyright` string.** The localized tier of
    Requirement 3 is `fastlane/metadata/en-US/`, and it is the only locale directory.
    `copyright` reads **`2026 Ehren Davis`** (year of first release, then the holder).
    *[No design doc names a locale, and `deliver` cannot create a directory whose name it does
    not know, so a per-locale tree is unbuildable without this; `copyright` is likewise a
    required file with no source. `P3-05-how-to-play.md` → Out of Scope makes the same point
    from the copy side: "Localisation. No design doc raises it; the strings above are specified
    in English as the docs word them."]* The holder is inferred from the bundle identifier
    `com.ehrendavis.…` and from the repository's author — **a legal-identity value, so confirm
    it before first submission** (Open Questions). Adding locales later is additive: a new
    directory beside `en-US`.
    *Testable:* `fastlane/metadata/` contains exactly one locale directory, named `en-US`, and
    a top-level `copyright.txt` with a non-empty value.

4. **`match` stores signing certificates and provisioning profiles in a git repo and syncs
   them.** *[Tech Design → Decisions → Release tooling — fastlane]* Configured per Requirement
   33. *Testable:* a machine with no local signing material runs `certs` and then produces a
   signed build.

5. **`produce` creates the app record and registers the bundle identifier and the app name
   from the CLI** — the app record is not hand-created in the App Store Connect web UI. The
   name it registers is **"Tic Tac Toe Extreme"**. *[Tech Design → Decisions → Release
   tooling — fastlane; App name]* Run once, not as a lane.

6. **All of it runs on Apple's official App Store Connect API underneath**, authenticated by
   the API key of Requirement 33 rather than an Apple ID session. *[Tech Design → Decisions →
   Release tooling — fastlane]*

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
   games do we keep?]* Blocked by Requirement 18.
   *Testable:* the record's in-app-purchase declaration is set, and a build submitted without
   it is rejected at review — the negative case is Apple's, not ours to test.

9. **The products configured in App Store Connect are exactly the products the app queries,
   and no others.** What is settled is one product: **the $4.99 open-game cap unlock** *[Tech
   Design → Decisions → In-app purchases; Menus and UI → Decisions → How many open games do we
   keep?]*, **sold from the Settings screen's purchases section** *[Menus and UI → Decisions →
   Where the open-game slot unlock is sold]* — the surface is settled, so nothing here waits on
   it. **No paid-theme product is configured by this PRD as written**, because
   `P4-05-purchase-flow.md` Requirement 9 establishes that **zero locked themes ship**, its Out
   of Scope declines a theme storefront, and its Open Question 1 records that whether paid
   themes are one product, one per theme, or a bundle is **undecided**. Configuring per-theme
   products would create store entries the app never queries, against `P4-05` Requirement 1.
   *Testable:* the set of configured product identifiers and the set the app queries are the
   same set. **The identifiers themselves do not exist yet** — Open Question B, and until they
   do this testable cannot be run.

34. **Both products are created as non-consumables.** *[Derived where
    `P4-05-purchase-flow.md` Open Question 4 assigns the derivation to this PRD by name, and
    supplied by its Requirement 2, which grounds permanence in `Tech Design → Decisions →
    Entitlements — Apple stores them, no backend needed`: "Restore for non-consumables is
    largely automatic … a refunded or lapsed purchase simply stops appearing in
    `Transaction.currentEntitlements`." Neither statement coheres unless the products are
    non-consumables.]* **App Store Connect fixes the product type at creation and it cannot be
    changed afterwards** — a consumable created by mistake has to be abandoned and replaced
    under a new identifier, which compounds Open Question B's permanence problem. Blocked by
    Requirement 18.
    *Testable:* each configured product's type reads *Non-Consumable*; `P4-05` Requirement 2's
    restore behavior holds in sandbox (Requirement 21).

10. **Do not overstate what fastlane covers here.** `produce` creates the app record and
    `deliver` pushes the listing, but **in-app purchase products are configured separately and
    are their own review surface** — each carries its own metadata and review state and can be
    rejected independently of the app. No lane in Requirement 32 touches them. *[Tech Design →
    Decisions → Release tooling — fastlane, which scopes the three components to the app
    record, the listing and signing; In-app purchases, which adds the products]* Manual process
    step.

11. **StoreKit is the one thing that reaches the network, and what it reaches is Apple.** The
    app is otherwise fully offline — no backend, no accounts — with StoreKit needing network
    access and a restore path tied to the Apple ID, and **entitlements living with Apple rather
    than on any server of ours**: `Transaction.currentEntitlements`, verified on device, is the
    record of truth. *[Tech Design → What the Design Docs Already Imply → "Fully offline,
    except for in-app purchases … a StoreKit query against Apple, not a service we run";
    Decisions → Entitlements — Apple stores them, no backend needed]* See Requirement 30 for
    what the record has to say about it.

### The build being submitted

12. **The submitted build targets iOS, with iPhone first and iPad second.** Android is "far
    future" and is not part of this release. *[Tech Design → Decisions → Device support;
    Primary target — Apple]* **Operative device family: universal (iPhone + iPad).**
    `P1-01-app-scaffold.md` Requirement 16 creates the project with `--platforms ios,android`,
    and its Open Questions leave the iOS target device family "at the `flutter create` default
    rather than narrowed, because narrowing it is a product call" — that default is universal.
    So this PRD plans for iPhone **and** iPad (Requirement 22's sizes follow). **Narrowing to
    iPhone-only is reversible until first submission** and remains the user's call.

13. **The submitted build's minimum deployment target is iOS 13**, as set by the scaffold.
    *[Tech Design → Decisions → Minimum iOS version]*

36. **Fence — the first release is version `1.0.0`, and the build number is incremented by
    the `release` lane** via `increment_build_number` (Requirement 32), not by hand. *[No doc
    states a version. `deliver` refuses an upload without a unique build number, so the
    alternative is not "undecided" but "decided at the keyboard on upload night."]* The
    marketing version thereafter is a human edit to `pubspec.yaml`'s `version:` field; the
    build number never repeats.
    *Testable:* two consecutive `release` runs produce two different build numbers, and the
    first upload carries `1.0.0`.

14. **Set up when actually approaching shipping — not now.** *[Tech Design → Decisions →
    Release tooling — fastlane]* A scheduling requirement, not something to test — except
    Requirement 18, which cannot wait.

15. **An Apple Developer Program membership is a prerequisite.** *[Tech Design → Decisions →
    Release tooling → "Watch out for"]* Manual process step. **Not the same agreement as
    Requirement 18**; membership alone does not let the app sell anything.

16. **App Review is not automated.** fastlane uploads; submission to review and the review
    itself stay manual — for the app and, per Requirement 10, for each product. *[Tech Design
    → Decisions → Release tooling → "Watch out for"]* Manual process step.

17. **No CI is added here. Builds stay local.** `flutter test` and `flutter analyze` run
    locally. *[Tech Design → Decisions → CI — local builds only]* **Fence closing this
    requirement's own gap:** the `release` lane runs `flutter analyze` and `flutter test`
    first and **aborts on either failing**, so the one automated gate that exists sits where
    the last line of defense is. *Testable:* with a deliberately failing test, `release`
    exits non-zero and uploads nothing.

### Submission prerequisites and blockers

*[Tech Design → Open Questions → 3. Build and distribution]* enumerates these as "a set of
hard App Store submission blockers … all of which must be decided before shipping" — **a
blocker list, not a Decision**. Where the work is unambiguously this PRD's it is a requirement;
where the answer is a product or business call it is an Open Question. All of them appear on
the checklist of Requirement 39.

18. **The Paid Applications Agreement is executed, and banking and tax details are on file,
    before anything is sold.** *[Tech Design → Open Questions → 3: "required before anything,
    including any in-app purchase, can be sold. A human, multi-day process with no automation
    path."]* Manual process step. **The hardest blocker in the list; it gates Requirements 8,
    9, 25 and 34.** Nothing in the tooling detects that it is missing — App Store Connect
    simply will not let the products exist.

19. **Export compliance is answered for every upload.** *[Tech Design → Open Questions → 3:
    "asked on every upload; can be pre-answered with an `Info.plist` key, which is the
    scaffold's file."]* This PRD owns giving the answer at upload time; the key is fenced in
    Requirement 37. Manual process step until that key lands.

37. **Fence — the pre-answer key is `ITSAppUsesNonExemptEncryption`, set to `false`.** The app
    uses no encryption beyond the HTTPS StoreKit performs on its behalf, which is exempt; the
    app implements and calls none of its own *[Requirement 28; `P4-05-purchase-flow.md`
    Requirement 7 admits no network target other than the store]*. **This PRD does not write
    iOS project files**, so the key lands in `P1-01-app-scaffold.md`'s territory —
    `ios/Runner/Info.plist` — and that PRD has no `Info.plist` requirement at all, leaving it
    unowned on both ends. Until it lands, Requirement 19 is answered by hand on every upload.
    Reversible: if the app ever ships its own cryptography, the answer changes and so does the
    filing.
    *Testable:* with the key present, an upload completes without pausing for the compliance
    question.

20. **The App Review contact information is supplied on the record.** *[Tech Design → Open
    Questions → 3]* Manual process step, owned here because it is a submission field and
    nowhere else.

21. **The purchase flow is exercised against a real App Store sandbox account before
    submission.** *[Tech Design → Open Questions → 3: "sandbox testing of the purchase flow
    before submission"]* It belongs here because `P4-05-purchase-flow.md` Requirement 11 makes
    the store substitutable and its whole suite runs "with no network and no store account
    configured" — **every automated test of buying and restoring runs against a double, and
    nothing else ever touches the real store.** The path is concrete: Settings → purchases
    section → parental gate → buy *[Menus and UI → Decisions → Where the open-game slot unlock
    is sold; `P4-04-settings.md` Requirements 20–21; `P4-05-purchase-flow.md` Requirement 12]*.
    Manual process step. *Testable as a manual pass:* a sandbox purchase of the cap unlock
    raises the reported cap to 100 on a real device, and a fresh install on a second device
    signed into the same Apple ID shows it owned without touching *Restore*.

22. **Screenshots are captured at Apple's required device sizes and committed to
    `fastlane/screenshots/`, and this PRD owns capturing them.** *[Tech Design → Open Questions
    → 3: "Screenshots at Apple's required device sizes — who captures them, and by what means,
    is unowned."]* Ownership is accepted here because **no P3 or P4 PRD accepts it** — none
    mentions screenshots, a device size, or a capture mechanism. What waves P3/P4 supply is the
    **screens**; turning them into store images is release work. **Per Requirement 12 the sizes
    required are the current iPhone and iPad reference sizes**, because the build is universal
    until someone narrows it. The mechanism — by hand on a simulator, or fastlane's `snapshot`,
    a fourth component beyond the three the decision names — is not decided; the `screenshots`
    lane of Requirement 32 exists either way.
    *Testable:* `fastlane/screenshots/en-US/` contains at least one image at each size Apple
    currently requires for the device families of Requirement 12, and `metadata` uploads them.

23. **The submitted build carries a 1024×1024 app icon in the iOS asset catalog — and today
    nothing supplies one, which makes this a hard upload blocker rather than an open
    question.** *[Tech Design → Decisions → The app icon: "The app ships an icon, and it is not
    the main-menu logo … It lives in the iOS asset catalog rather than the Flutter `assets/`
    tree."]* **`upload_to_app_store` fails without it**, so the `release` lane of Requirement 32
    cannot complete — this is not a thing to discover at submission.
    **Why it has no supplier:** `P5-02-asset-generation-replicate.md` **Requirement 3** confines
    that script's generated output to `assets/images/` and `assets/audio/` and writes no
    generated asset anywhere else, and an iOS icon must sit in `ios/Runner/Assets.xcassets/`.
    That PRD's own Open Question puts the choice with the user: *"**If yes**, Requirement 3
    must widen to permit `ios/Runner/Assets.xcassets/`. **If no**, it stays unowned
    roster-wide."* Meanwhile `P1-01-app-scaffold.md` creates no asset-catalog entry, and this
    PRD does not write iOS project files.
    *Testable:* the archived build's asset catalog contains the 1024×1024 marketing icon;
    `release` fails at upload without it.

24. **Content rights are established before the submission question is answered.** *[Tech
    Design → Open Questions → 3]* This PRD owns answering at submission; it cannot own
    establishing the facts, which concern Replicate model output terms and the bundled Inter
    and Phosphor licenses. Manual process step, blocked until someone establishes them — Open
    Question D.

25. **Price tier and territory availability are set on the record before release.** *[Tech
    Design → Open Questions → 3]* This PRD enters the values; **it does not choose them**. The
    primary category half is answered by Requirement 26. Blocked by Requirement 18 for anything
    involving money.

### The Kids Category and what it obliges

26. **The record lists the app in Apple's Kids Category, with an age rating of 4+.** *[Tech
    Design → Decisions → Kids category]* A Decision, not a listing-time choice.

27. **The submitted build carries a parental gate before the purchase flow — already specified
    upstream, and this PRD neither builds nor re-specifies it.** *[Tech Design → Decisions →
    Kids category: a gate "is required before any purchase flow … the gate has to exist before
    those are built rather than being added at submission"; scope is "purchases only"]*
    **Correction of fact:** earlier drafts of this requirement asserted that neither wave-4 PRD
    mentioned a gate. That is false against the current documents, and acting on it would
    re-open specified work:
    - `P4-05-purchase-flow.md` **Requirement 12** is the gate and claims it outright —
      *"exactly one PRD owns the gate, and it is this one"* — owning its design and behavior.
    - `P4-04-settings.md` **Requirements 20–22** build the purchases section, with **21**
      pinning the ordering (*"The purchase control does not reach the purchase flow unless the
      parental gate has been passed"*) and deferring the challenge to `P4-05`.

    What this PRD contributes is only the release-side consequence: a build reaching the
    purchases section without a passed gate is not submittable under this category, and
    Requirement 21's sandbox pass exercises the gated path. **The one thing still unowned is
    the gate's concrete challenge** — see Open Question F.

28. **The submitted build contains no third-party analytics and no behavioural advertising,
    and the release introduces none.** *[Tech Design → Decisions → Kids category:
    "Third-party analytics and behavioural advertising are restricted."]* A constraint that
    must **stay** true rather than a change to make: `P1-06-crash-reporting.md` Requirement 9
    adds no telemetry SDK or network client, its Requirement 10 introduces no backend, and
    `P4-05-purchase-flow.md` Requirement 7 admits no network target but the store.
    *Testable:* the dependency and outbound-call scan `P1-01-app-scaffold.md` Requirement 6
    already writes finds no analytics or advertising SDK and no network target other than
    StoreKit — reusing that check rather than adding a second one, which is also how
    `P1-06` Requirement 10 routes it.

29. **A privacy policy exists and its URL is on the record before submission.** *[Tech Design
    → Decisions → Kids category: "A privacy policy is mandatory."]* The Kids Category turns
    this from a listing field into a hard external prerequisite — **and the project has no
    website of any kind**, so something has to exist to host it, alongside the support URL.
    Writing and hosting are outside this PRD and outside the repo. Manual process step, blocked
    externally.

30. **What the record declares about data collection is shaped by there being no backend —
    scoped to what is true today.** The app declares in-app purchases (Requirement 8), uses
    StoreKit, and **operates no server of its own**: entitlements live with Apple and are
    verified on device, so there is no account we hold and no receipt service *[Tech Design →
    Decisions → Entitlements — Apple stores them, no backend needed]*. **Nothing is transmitted
    today**, and that is now a checked property rather than an assurance:
    `P1-06-crash-reporting.md` **Requirement 6** forbids any send of a crash report,
    **Requirement 7** forbids any destination or transport appearing in that feature at all,
    **Requirement 9** admits no telemetry SDK or network client, **Requirement 10** introduces
    no backend of ours, and its **Requirement 16** specifies the transport scan that verifies
    Requirement 6 rule by rule, in the shape `P1-05-theme-guard-test.md` uses. With Requirement
    28's no-analytics constraint, the nutrition label is defensible as *no data collected*
    **for the build being submitted**.
    **It is not settled beyond that.** `P1-06` **Open Question 1** holds the crash report's
    field set open and attaches compliance weight to it — the opponent name a child types at
    New Game may end up in the report, and "the field set decided now is what a future
    destination would send, and that is what the label would have to declare." Re-check this
    requirement the day a destination is chosen.

## Out of Scope

- **The purchase implementation and the parental gate** — StoreKit, the purchase sheet,
  restore, the product set, and the gate's design and behavior: `P4-05-purchase-flow.md`
  (Requirement 12 owns the gate). **The purchases section and the gate ordering**:
  `P4-04-settings.md` Requirements 20–22. **The entitlement model**:
  `P1-07-entitlements.md`. This PRD owns the store-side declaration, the product
  configuration and the sandbox verification only.
- **Writing iOS project files** — the bundle identifier, the iOS minimum, the device family,
  and `ITSAppUsesNonExemptEncryption` — `P1-01-app-scaffold.md`. This PRD consumes those
  values; Requirement 37 records the one that is unowned.
- **Producing the app icon artwork, and widening any PRD's write scope to the iOS asset
  catalog.** Requirement 23 requires the build to carry an icon and records that nothing
  supplies one; `P5-02-asset-generation-replicate.md`'s open question is where the "generate
  it" answer would land, and it is the user's to give.
- **Generating the theme sounds and the logo** — `P5-02-asset-generation-replicate.md`, whose
  **Stage 2** must precede first submission (see the dependency note above). This PRD neither
  runs that script nor declares its output.
- **Writing and hosting the privacy policy and support pages.** Requirement 29 puts the URL on
  the record; the content and hosting are outside the repo and unowned.
- **The screens themselves** — waves P3/P4. Requirement 22 keeps the *capture* here.
- **Crash reporting** — `P1-06-crash-reporting.md`. No crash or analytics service is wired up,
  and per Requirement 28 none may be. **This PRD does not accept that PRD's dSYM delegation**
  — Open Question E.
- **Alternative Game Styles.md** — parking lot, not what is being built.

## Open Questions

### With the user — no reading settles these

- **B. The product identifiers.** `P4-05-purchase-flow.md` Open Question 4: "**No product
  identifiers exist.** No doc names a product ID for either product, and this PRD invents none.
  Something must … (`P5-03-release-fastlane.md` registers them)." **Each PRD names the other,
  so neither invents one**, and Requirement 9's testable cannot run until someone does. A
  product identifier is permanent and unreusable — the same trap as the bundle identifier, now
  compounded by Requirement 34's product type also being fixed at creation.
- **Who supplies the 1024×1024 app icon?** *[Tech Design → Open Questions → 3]* The icon is
  decided; its production is not, and **an upload fails without it** (Requirement 23).
  `P5-02-asset-generation-replicate.md` frames the fork exactly: if it is generated there, that
  PRD's Requirement 3 widens to permit `ios/Runner/Assets.xcassets/`; if not, *"it stays
  unowned roster-wide."* Either answer is cheap now and expensive on upload night.
- **The app's own download price, and the territories it is available in.** Requirement 25
  enters them; nothing chooses them. One IAP price is decided ($4.99 for the cap unlock); no
  paid theme has one.
- **Which git repository holds the `match` certificates.** Requirement 33 fixes the mechanism
  and requires it be private; the location is credential-adjacent and the user's.
- **Where the privacy policy and support pages are hosted.** *[Tech Design → Open Questions →
  3: "The project has no website of any kind."]* Requirement 29 makes the policy mandatory; it
  does not conjure somewhere to put it.
- **The content-rights facts** — Replicate output terms, and the Inter 400/500/600 and Phosphor
  licenses (Open Question D).
- **The age-rating questionnaire answers and the privacy nutrition label answers.** *[Tech
  Design → Open Questions → 5, which now records that the category, gate, analytics and
  privacy-policy requirements are settled and "what remains open is the exact age-rating
  questionnaire answers"; → Open Questions → 3 for the label.]* Requirement 30 records what is
  true of the submitted build; the questionnaires still have to be filled in by a human.
- **The secondary App Store category.** The primary is settled by Requirement 26.
- **Whether paid theme products exist at all**, and if so their structure and prices
  (`P4-05-purchase-flow.md` Open Question 1). Requirement 9 correctly configures none until
  this lands.
- **Confirm before first submission:** the `copyright` string of Requirement 35 names a legal
  holder inferred from the bundle identifier, and Requirement 12's universal device family is
  cheaper to narrow before submission than after.

### Found while writing this PRD — flagged, not answered

- **D. Nothing establishes the licensing Requirement 24 has to attest to.** The terms on
  Replicate model output and the Inter/Phosphor licenses are written down nowhere;
  `P5-02-asset-generation-replicate.md` generates assets without stating their terms — its own
  open questions say the same and route the need back here — and `P1-01-app-scaffold.md` leaves
  whether the scaffold bundles Inter and Phosphor unsettled.
- **E. dSYMs and symbolication are unowned, and both documents say so.**
  `P1-06-crash-reporting.md` → Out of Scope points *"Symbolication and dSYM handling"* at this
  PRD and records the refusal in the same breath: *"that PRD declines the delegation and
  nothing else picks it up … Recorded as an open gap, not a settled hand-off."* **The answer
  from this side, unchanged: this PRD does not own dSYMs today.** No design doc mentions
  symbolication or a crash-report destination — reports are built and deliberately never
  transmitted — so writing a dSYM requirement here would invent the destination that decision
  withholds. If a destination is chosen, the upload step is release tooling and belongs here.
- **F. The parental gate's concrete challenge has no owner.** The gate itself is owned
  (`P4-05-purchase-flow.md` Requirement 12) and its ordering is pinned (`P4-04-settings.md`
  Requirement 21), but `P4-05` says plainly *"Not specified here: the concrete challenge. Apple
  mandates that a gate exist, not what it asks, and no design doc describes one"*, and
  `P4-04`'s Open Question 3 records the same. A gate that ships without a designed challenge is
  a review risk on a Kids-category app. **Also stale, and not mine to fix:** `P4-04`
  Requirement 21's *"Gap this names"* note still says `P4-05` "has no parental-gate requirement
  today", which its Requirement 12 has since answered.
- **Whether the `screenshots` lane uses `snapshot`.** Requirement 22 fences the sizes and the
  destination, not the mechanism; adopting `snapshot` would add a fourth fastlane component
  beyond the three the design doc names, which is a decision worth taking deliberately.
