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
produces an in-process crash-report object. Nothing is transmitted anywhere: no network
call, no backend, no crash-reporting service, no accounts. The catch points and the report
object exist from the first build so that choosing a destination later is a matter of
deciding where to send an object that is already being built — not a matter of retrofitting
error handling.

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
   it on a network.
   *Source: Tech Design → Decisions → Crash reporting ("We just won't send it out just yet…
   Just don't send it. yet") — today's answer for the destination is "nowhere."*
   *Testable:* the report type's public API contains no transmit-shaped member; no call site
   passes a report to an HTTP/socket API.

3. **No crash-reporting service, telemetry, or network dependency is added.** `pubspec.yaml`
   gains no Crashlytics/Sentry-style SDK and no HTTP or socket client as part of this
   feature.
   *Source: Tech Design → Decisions → Crash reporting; Tech Design → What the Design Docs
   Already Imply → "Fully offline. No backend, no network, no accounts."*
   *Testable:* inspect `pubspec.yaml` dependencies.

4. **The app remains fully offline after this feature.** No backend, no network traffic, no
   accounts. Per Tech Design → Project structure — layer-first, there is still no backend
   data layer; `storage/` is local persistence only.
   *Source: Tech Design → What the Design Docs Already Imply → "Fully offline. No backend,
   no network, no accounts."*
   *Testable:* static check that no networking API is reachable from `lib/`.
   *Flag, stated in the doc itself:* this row stops being true the day a destination is
   chosen. Nothing built here may assume that day has come.

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
   *Testable:* `engine/` contains zero Flutter imports (the existing rule; this feature must
   not be the thing that breaks it).

## Out of Scope

- **Transport of any kind** — sending, queuing for send, retrying, batching, endpoint
  configuration, auth. The destination is deliberately deferred, not undecided-and-blocking:
  Tech Design records today's answer as "nowhere," with the destination to be chosen later.
- **Project setup, `pubspec.yaml` creation, and dependency baseline** — `P1-01-app-scaffold.md`.
- **Persistence mechanics** (`shared_preferences`, Hive, the repository interface) —
  `P1-04-persistence.md`. Whether a crash report needs to survive a restart is an open
  question raised below, not answered here; if the answer is yes, that work lands against
  the persistence layer and inherits Tech Design → Open Questions → 1. Persisted data —
  versioning.
- **Release tooling, App Store Connect, symbolication and dSYM handling** —
  `P5-02-release-fastlane.md`.
- **The "theme failed to load" modal.** That is a decided, user-facing recovery behavior
  owned by the theming work (Theming → Decisions → What happens if a theme fails to load:
  modal, then fall back to Neon). Whether it *also* produces a crash report is an open
  question below.
- **Analytics, usage metrics, or any other data collection.** Nothing in the design docs
  asks for these, and they would break the offline constraint.

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
   Project structure — layer-first lists `engine/`, `storage/`, `theme/`, `state/`, `ui/`
   and names no home for error handling. Related: is the report object a `freezed` +
   `json_serializable` model like the domain models, or a plain class? (Tech Design →
   Decisions → Serialization and the storage layer scopes that choice to "the domain models
   in `engine/`," which a crash report is not.)
