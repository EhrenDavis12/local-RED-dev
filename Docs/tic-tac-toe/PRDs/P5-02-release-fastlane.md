# PRD: Release & Distribution — fastlane

> **Status:** Draft · Source docs read: Tech Design.md, Game Overview.md, Menus and UI.md,
> Theming.md, Animations.md, Game Board Design.md, Rules.md, roadmap.md, and the read-only
> reference asset `design_handoff_game_ui/`. `Alternative Game Styles.md` is a declared
> parking-lot doc and was not sourced from.

> **Wave:** P5 · **Depends on:** `P1-01-app-scaffold.md` (the bundle identifier and the iOS
> minimum are set there; this PRD consumes them), `P4-05-in-app-purchases.md` (the products
> this PRD has to declare and configure in App Store Connect), and the finished screens in
> waves P2/P3 (screenshot content). Nothing depends on this PRD.

> **Deferred — do not start this now.** *[Tech Design → Decisions → Release tooling —
> fastlane: "Set up when actually approaching shipping — not now."]* This document records
> what was decided so it does not have to be re-decided at ship time. It is not a work item
> until the game is actually approaching shipping.

> **Blocked on the app name.** *[Tech Design → Open Questions → 3. Build and distribution:
> "App name?"]* The App Store Connect listing cannot be completed without it — see Open
> Questions. Do not invent one.

## Problem

The game is decided to ship as a **public App Store release**, not a personal build and not
TestFlight-only *[Tech Design → Decisions → Distribution — public App Store release]*. That
makes an App Store Connect listing — description, keywords, screenshots, categories — a real
deliverable, and none of it exists. The game also **sells things** *[Tech Design → Decisions
→ In-app purchases]*, so the App Store Connect record has to declare in-app purchases and
carry configured products, which is a second deliverable on the same account. There is no
signing setup, no app record, and no way to push a build from a laptop. Separately, *[Tech
Design → Decisions → CI — local builds only]* means nothing runs `flutter test` or `flutter
analyze` on a push, so whatever the release procedure checks is the only thing checked.

## Goal

When this is done, the app has an App Store Connect record under its permanent bundle
identifier, that record declares in-app purchases and holds the configured products, signing
material is stored and synced from a git repo rather than living on one machine, the entire
store listing exists as text files in the repo that are edited and committed like code, and
a single fastlane run from the CLI pushes the listing and a build to App Store Connect.
Review itself — for the app and for the purchase products — is still submitted and waited on
by hand.

## Requirements

1. **The release is a public App Store release** — not a personal build, not TestFlight-only
   — and the App Store Connect listing (description, keywords, screenshots, categories) is
   a deliverable of this PRD. *[Tech Design → Decisions → Distribution — public App Store
   release]*

2. **fastlane is the release tooling.** The App Store listing is kept as local text files,
   edited and committed like code, and pushed to App Store Connect from the CLI. *[Tech
   Design → Decisions → Release tooling — fastlane]* Testable: the listing content lives in
   the repo and a `git diff` shows a listing change as a text diff.

3. **`deliver` (aka `upload_to_app_store`) owns the listing files.** `fastlane/metadata/`
   holds description, keywords, release notes and categories — **one file per field per
   locale** — and `fastlane/screenshots/` holds the images. Edit locally, commit, run, and
   it pushes to App Store Connect. *[Tech Design → Decisions → Release tooling — fastlane]*
   Testable up to the point of upload: the directory layout is one-file-per-field-per-locale
   and a `deliver` validation run passes against it.

4. **`match` stores signing certificates and provisioning profiles in a git repo and syncs
   them.** *[Tech Design → Decisions → Release tooling — fastlane]* Testable: a machine with
   no local signing material can run `match` and produce a signed build.

5. **`produce` creates the app record and registers the bundle identifier from the CLI** —
   the app record is not hand-created in the App Store Connect web UI. *[Tech Design →
   Decisions → Release tooling — fastlane]*

6. **All of it runs on Apple's official App Store Connect API underneath.** *[Tech Design →
   Decisions → Release tooling — fastlane]* Concretely, the fastlane setup authenticates via
   an App Store Connect API key rather than any other mechanism.

7. **The registered bundle identifier is `com.ehrendavis.tictactoeextreme`** — the value the
   scaffold already sets, not a value chosen here. *[Tech Design → Decisions → Bundle
   identifier]* The doc's own warning applies at the moment `produce` runs: **a bundle
   identifier is effectively permanent once the app has been submitted to App Store Connect,
   so it is not a name to revisit casually.**

8. **The App Store Connect record declares in-app purchases.** The game sells two things:
   **themes beyond the two free ones (Neon and Classic Red vs Blue)**, and a **$4.99 unlock
   raising the open-game cap from 3 to 100.** *[Tech Design → Decisions → In-app purchases;
   Theming → Decisions → Which themes are free; Menus and UI → Decisions → How many open
   games do we keep?]* A release that ships the app without declaring IAP is wrong, not
   merely incomplete.

9. **The purchase products are configured in App Store Connect** — at minimum the $4.99
   open-game-cap unlock and one product per paid theme — with identifiers matching what the
   app requests at runtime. *[Tech Design → Decisions → In-app purchases]* The product set
   and its identifiers come from `P4-05-in-app-purchases.md`; this PRD is where they are
   created on the store side. Testable: the app's StoreKit fetch returns every declared
   product, with no unknown-identifier results.

10. **Do not overstate what fastlane covers here.** `produce` creates the app record and
    `deliver` pushes the listing, but **in-app purchase products are configured separately
    and are their own review surface** — each product carries its own metadata and review
    state and can be rejected independently of the app. Nothing in Requirements 2–6
    automates that. *[Tech Design → Decisions → Release tooling — fastlane, which scopes the
    three fastlane pieces to the app record, the listing and signing; In-app purchases,
    which adds the products]* Manual process step.

11. **StoreKit is the one thing that reaches the network.** The app is otherwise fully
    offline — no backend, no accounts — with StoreKit needing network access and a
    restore-purchases path tied to the Apple ID. *[Tech Design → What the Design Docs Already
    Imply → "Fully offline, except for in-app purchases"]* This is what the release has to
    describe truthfully in the places Apple asks — see Open Questions on the privacy
    nutrition label.

12. **The submitted build targets iOS, with iPhone first and iPad second.** Android is "far
    future" and is not part of this release. *[Tech Design → Decisions → Device support;
    Primary target — Apple]* "All media devices" is recorded as stated and **is not yet
    scoped to particular platforms**, so nothing here plans for one.

13. **The submitted build's minimum deployment target is iOS 13**, as set by the scaffold.
    *[Tech Design → Decisions → Minimum iOS version]*

14. **Set up when actually approaching shipping — not now.** *[Tech Design → Decisions →
    Release tooling — fastlane]* This is a scheduling requirement, not something to test:
    the work in this PRD is not begun until the game is approaching ship.

15. **An Apple Developer Program membership is a prerequisite.** None of the above works
    without one. *[Tech Design → Decisions → Release tooling → "Watch out for"]* Manual
    process step — obtained by a human before any fastlane action is attempted.

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

## Out of Scope

Referenced by filename rather than specified here:

- **The in-app purchase implementation** — StoreKit integration, the purchase sheet, restore
  purchases, entitlement storage, and how the cap of 3 becomes 100 —
  `P4-05-in-app-purchases.md`. This PRD owns only the store-side declaration and product
  configuration that implementation needs to exist against.
- **Setting the bundle identifier and the iOS minimum in the Flutter/Xcode project** —
  `P1-01-app-scaffold.md`. This PRD *consumes* those values; it does not set them.
- **Crash reporting.** Errors are caught and the report object is built, but it has no
  transport — `P1-06-crash-reporting.md`. No crash or analytics service is wired up as part
  of shipping.
- **Screenshot *content*.** The images come from the finished screens delivered in waves
  P2/P3. This PRD owns where the files live and how they are pushed, not what is in them.
- **Asset generation** — the logo and sound assets are *"not now"* by decision *[Tech Design
  → Decisions → Where do sound and art assets come from?]*.
- **Alternative Game Styles.md** — parking lot, not what is being built.

## Open Questions

### From the design docs — unresolved, worded as the docs word them

- **App name?** *[Tech Design → Open Questions → 3. Build and distribution]* Everything else
  in that group is resolved. This one blocks the listing outright: the App Store name is a
  required field in `fastlane/metadata/`, and it is also what `produce` registers alongside
  the bundle identifier. **This PRD cannot be executed until it is answered.**

### Found while writing this PRD — not settled anywhere, and flagged rather than answered

These are gaps I noticed, not proposals with any authority behind them. Each is a place the
person running the release would otherwise have to guess.

- **Versioning and build numbers.** No doc says what version the first release carries, how
  the version is bumped, or whether the build number is incremented by fastlane
  (`increment_build_number`) or by hand. `deliver` refuses to upload without a unique build
  number, so this gets decided at the keyboard by default if it is not decided first.
- **Where the `match` certificate repo lives.** The decision says the certificates and
  profiles are stored in a git repo and synced; it does not say *which* repo, whether it is
  private, or how the `match` passphrase is held. This is credential material, so the
  default answer is not obviously safe.
- **Which locales ship.** `deliver`'s layout is one file per field **per locale**, which
  makes the locale set a real decision. No doc names one, and nothing else in the project
  discusses localization at all.
- **The privacy nutrition label and the age rating — sharper now that the app sells things,
  but still unanswered.** A public App Store release cannot be submitted without both, and
  no design doc mentions either. Two things raise the stakes. The app is no longer
  unconditionally offline: StoreKit reaches the network and ties a restore path to the Apple
  ID *[Tech Design → Decisions → In-app purchases; What the Design Docs Already Imply →
  "Fully offline, except for in-app purchases"]*, which is exactly what the nutrition label
  asks about. And **kids are a stated target audience** *[Game Overview → Target Audience &
  Platform]* while the app now charges for content, which makes the age rating and any
  Kids-category question consequential rather than routine. Recorded as raised stakes, not
  as an answer.
- **A privacy policy.** App Store Connect requires a privacy policy URL for a public
  release. No design doc mentions a policy, a URL, or anywhere to host one — and a purchase
  flow is more, not less, to have to describe in one.
- **Which App Store categories.** "Categories" is named as one of the listing fields, but
  the primary and secondary category are never chosen.
- **The app's own price.** One in-app purchase price is decided — $4.99 for the
  open-game-cap unlock *[Menus and UI → Decisions → How many open games do we keep?]* — but
  what the app itself costs to download is not stated anywhere.
- **Which paid theme products exist, and at what prices.** *[Theming → Decisions → Which
  themes are free]* settles that everything beyond Neon and Classic Red vs Blue is paid, but
  names no further theme and no price. Requirement 9 cannot be completed until that product
  list exists; it presumably arrives with `P4-05-in-app-purchases.md`.
- **The app icon.** The App Store requires a 1024×1024 icon. The only art decided anywhere
  is the **main-menu logo** *[Menus and UI → Decisions → Does the main menu need a
  title/logo?]*, which the handoff still draws as a placeholder and which is
  Replicate-generated "when we actually need them." An app icon is not the same asset as the
  menu logo, and no doc names one.
- **Whether the fastlane lane runs `flutter analyze` and `flutter test` before uploading.**
  See Requirement 17 — the decision is that these run locally and nothing runs them on a
  push; whether the release lane is one of the places they run is not stated.
