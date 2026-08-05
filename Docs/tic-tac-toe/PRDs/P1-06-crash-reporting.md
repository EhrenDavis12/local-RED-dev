# PRD: Crash Reporting — Catch and Build, Don't Send

> **Status:** Draft · Source docs read: Tech Design, Theming, Menus and UI, Game Overview,
> Game Board Design, Rules, Animations, roadmap (index), design_handoff_game_ui (reference
> asset, read-only)

**Wave:** 1 · **File:** `P1-06-crash-reporting.md`

**Depends on:** `P1-01-app-scaffold.md` (the Flutter project and `pubspec.yaml` must exist).
Parallel-safe with everything else in wave 1.

This is a deliberately small PRD. The design docs say one thing about crash reporting and
this document says that one thing precisely. Where the docs are silent — the report
object's fields, whether reports survive a restart, whether the player ever sees anything —
those are listed under Open Questions and must not be answered by the implementer.

> **Written against the amended offline row.** `Tech Design.md` → *What the Design Docs
> Already Imply* no longer reads "Fully offline. No backend, no network, no accounts." It
> now reads **"Fully offline, except for in-app purchases"** — StoreKit is a named
> exception needing network access and a restore path tied to the Apple ID, arriving in
> `P4-05-purchase-flow.md`. **This changes nothing about the substance of this PRD.** Crash
> reports are still built and still not transmitted; `Tech Design.md` → Decisions → Crash
> reporting says so in as many words: *"StoreKit being permitted does not make a report
> destination permitted — those are two separate exceptions."* What it does change is how
> Requirements 3 and 4 are worded and tested, so that a check written in this wave still
> passes when the store layer lands in P4.

## Problem

The app has no error handling at all today (there is no application code yet). When
something throws, the failure is invisible: nothing records what happened, and there is no
object describing the crash to reason about later. Adding that after the fact means going
back through every layer to insert catches — the same retrofit cost the theme system is
built early to avoid.

The counterpart problem is the reason this hasn't simply been solved with an off-the-shelf
crash SDK: there is nowhere to send the data, and every such SDK assumes a destination and
a network.

## Goal

When this is done, errors in the app are caught rather than lost, and each caught error
produces an in-process crash-report object. Nothing is transmitted anywhere: this feature
adds no network call, no backend of ours, no crash-reporting service, and no account
system. The catch points and the report object exist from the first build so that choosing
a destination later is a matter of deciding where to send an object that is already being
built — not a matter of retrofitting error handling.

## Requirements

1. **Errors are caught, and a caught error produces a crash-report object.** An error that
   would otherwise go unhandled results in exactly one crash-report object being
   constructed in process.
   *Source: Tech Design → Decisions → Crash reporting — catch and build the report, don't
   send it ("just catch and build out the object").*
   *Testable:* raise an error through the app's error path in a test; assert a crash-report
   object was constructed.

2. **The crash-report object is never transmitted.** The report object exposes no send,
   upload, flush, or destination API, and no code path takes a constructed report and puts
   it on a network — including the one network path the app is permitted.
   *Source: Tech Design → Decisions → Crash reporting ("We just won't send it out just yet…
   Just don't send it. yet") — today's answer for the destination is "nowhere"; and the
   same Decision's amendment: "StoreKit being permitted does not make a report destination
   permitted — those are two separate exceptions, and this one stops being true the day a
   destination is chosen."*
   *Testable:* the report type's public API contains no transmit-shaped member; no call site
   passes a report to a network API of any kind, the store SDK included.

3. **No crash-reporting service, telemetry SDK, or network client is added by this
   feature.** `pubspec.yaml` gains no Crashlytics/Sentry-style SDK and no HTTP or socket
   client as part of this work.
   *Source: Tech Design → Decisions → Crash reporting; Tech Design → What the Design Docs
   Already Imply → "**Fully offline, except for in-app purchases.** No backend, no network,
   no accounts — StoreKit is the one exception, needing network access and a
   restore-purchases path tied to the Apple ID."*
   *Testable:* inspect `pubspec.yaml` dependencies.
   *Boundary:* this does **not** forbid the store SDK. That dependency is
   `P4-05-purchase-flow.md`'s to add, and it is the one permitted exception — but it is a
   purchase transport, not a report transport, and Requirement 2 forbids routing a report
   through it.

4. **This feature introduces no backend of ours and no account system we operate.** Nothing
   it adds talks to a server of ours: no HTTP client, no login, no user record. Per Tech
   Design → Project structure — layer-first there is still no backend data layer, and
   `storage/` remains local persistence only.
   *Source: Tech Design → Decisions → Project structure — layer-first ("There is still **no
   backend data layer**: nothing in the app talks to a server"); Tech Design → What the
   Design Docs Already Imply → the qualified *Fully offline, except for in-app purchases*
   row.*
   *Testable:* an outbound-call scan over `lib/` finds no HTTP client and no network target
   other than the store SDK. That is deliberately the same form as `P1-01-app-scaffold.md`
   Requirement 6 and `P4-05-purchase-flow.md` Requirement 7, so one check serves all three.
   The stricter form — "no networking API is reachable from `lib/`" — must **not** be
   built: `P1-01` Requirement 6 forbids it because it fails the day `P4-05` ships, and that
   PRD has no way to know the check exists.
   *What this does not license:* the scan permits the store SDK as a network target and
   nothing else. A report destination is not a store call and does not become permitted by
   this requirement — see Requirement 2.

5. **Building the report is separated from disposing of it, so a destination can be added
   later without touching the catch sites.** Catch sites construct a report and hand it off;
   they do not know what happens to it. Today what happens to it is nothing.
   *Source: Tech Design → Decisions → Crash reporting ("We will come up with where it will
   be sent to later"); Tech Design → Decisions → Online multiplayer is an intended future
   direction ("Tech choices must not foreclose syncing…").*
   *Testable:* no catch site references a destination, transport, endpoint, or queue.

6. **Crash-reporting code introduces no Flutter import into `engine/`.** If engine code
   participates in error reporting at all, whatever it touches stays pure Dart.
   *Source: Tech Design → Decisions → Is the game logic separate from Flutter? ("pure Dart
   with zero Flutter imports"); Tech Design → Decisions → Serialization and the storage
   layer (the same rule applied to `hive_flutter`).*
   *Testable:* `engine/` contains zero Flutter imports (the existing rule, also
   `P1-01-app-scaffold.md` Requirement 4; this feature must not be the thing that breaks
   it).

## Out of Scope

- **Transport of any kind** — sending, queuing for send, retrying, batching, endpoint
  configuration, auth. The destination is deliberately deferred, not undecided-and-blocking:
  Tech Design records today's answer as "nowhere," with the destination to be chosen later.
- **In-app purchases and StoreKit** — `P4-05-purchase-flow.md`. That layer is the app's one
  permitted network exception and it is not this feature's to build, use, or route anything
  through.
- **Project setup, `pubspec.yaml` creation, and dependency baseline** — `P1-01-app-scaffold.md`.
- **Persistence mechanics** (`shared_preferences`, Hive, the repository interface) —
  `P1-04-persistence.md`. Whether a crash report needs to survive a restart is an open
  question raised below, not answered here; if the answer is yes, that work lands against
  the persistence layer and inherits Tech Design → Open Questions → 1. Persisted data —
  versioning.
- **Release tooling and App Store Connect** — `P5-03-release-fastlane.md`.
- **Symbolication and dSYM handling** — pointed at `P5-03-release-fastlane.md`, which is the
  right destination if it ever becomes anyone's, but **that PRD declines the delegation and
  nothing else picks it up.** `P5-03` → Out of Scope says in as many words that it "does not
  accept that PRD's dSYM delegation," and its Open Question E gives the reason: no design doc
  mentions symbolication, dSYM upload, or a crash-report destination, so writing a dSYM
  requirement there would invent the destination the crash-reporting Decision explicitly
  withholds. **Recorded as an open gap, not a settled hand-off:** it is unowned today, and it
  becomes release tooling's the day a destination is chosen. Nothing in this PRD depends on it.
- **The "theme failed to load" modal.** That is a decided, user-facing recovery behavior
  owned by the theming work (Theming → Decisions → What happens if a theme fails to load:
  modal, then fall back to Neon). Whether it *also* produces a crash report is an open
  question below.
- **Analytics, usage metrics, or any other data collection.** Nothing in the design docs
  asks for these. The offline row is qualified for StoreKit alone; it does not open a
  general allowance for outbound data.

## Open Questions

The design docs are silent on all of these. They are listed so they get decided
deliberately rather than by whoever writes the code first.

1. **What fields does the crash-report object hold?** Tech Design says "build out the crash
   report" and names nothing that goes in it. Sub-question worth settling at the same time:
   does the report capture any game or player data — board state, the opponent name entered
   at New Game — or only technical error information?

2. **Is a report held only in memory, or persisted?** A report built at the moment of a
   crash and never written down is gone when the app dies, which may or may not be the
   intent given the object exists to be sent somewhere eventually. If persisted, which store
   — `shared_preferences` or Hive (Tech Design → Decisions → Persistence package, Game state
   storage — Hive) — and does it inherit the versioning question in Tech Design → Open
   Questions → 1?

3. **Are reports buffered or capped?** If several errors occur in one session, is each one a
   separate report, is there a cap, and what happens to the oldest?

4. **Does the player see anything when an error is caught?** The docs never say. Two nearby
   decisions point in opposite directions and neither is about this: an illegal tap
   deliberately shows nothing at all (Game Board Design → Taps outside the legal quadrant:
   "no shake, no flash, no error message"), while a theme that fails to load deliberately
   shows a modal (Theming → Decisions → What happens if a theme fails to load).

5. **Which errors are in scope for a report?** Only errors that would otherwise be
   unhandled, or also errors that are caught and recovered from — a theme file that fails to
   parse being the concrete case already decided elsewhere.

6. **Where does this code live in the layer-first structure?** Tech Design → Decisions →
   Project structure — layer-first names no home for error handling, so there is nowhere for
   this feature's code to go without either inventing a directory or putting it in a layer
   that means something else. **Neither this PRD nor the scaffold invents one:**
   `P1-01-app-scaffold.md` Requirement 2 builds the doc's tree and says explicitly that it
   is "not a closed set on this PRD's authority," pointing back at this question rather than
   adding a directory to close it.
   **There is a precedent for how it would be closed:** that same tree was amended once
   already for a comparable case — `navigation/` was added as a new layer because the
   Navigation decision "names an explicit navigation layer that this tree had no home for,"
   exactly as `storage/` was added before it. Crash reporting is the remaining homeless
   layer in wave 1. Closing it the same way is a `Tech Design.md` edit (forge-doc-writer's,
   not this PRD's), and it would then have to reach `P1-01`'s tree, as the `navigation/`
   amendment did.
   Related and still open: is the report object a `freezed` + `json_serializable` model like
   the domain models, or a plain class? (Tech Design → Decisions → Serialization and the
   storage layer scopes that choice to "the domain models in `engine/`," which a crash
   report is not.)
