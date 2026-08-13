**Build-readiness: 90**

# PRD: Crash Reporting — Catch and Build, Don't Send

> **Status:** Draft · Source docs read: Tech Design, Theming, Menus and UI, Game Overview,
> Game Board Design, Rules, Animations, roadmap (index), design_handoff_game_ui (reference
> asset, read-only)

**Wave:** 1 · **File:** `P1-06-crash-reporting.md`

**Depends on:** `P1-01-app-scaffold.md` — the Flutter project, `main.dart`, `pubspec.yaml`
and the `lib/` tree including `lib/diagnostics/` must exist. That PRD ships before the rest
of its own wave; this one runs after it. Parallel-safe with everything else in wave 1.

> **Numbering is frozen and append-only.** Requirements 1–16 keep the numbers and meanings
> they had in the previous revision; 17, 18 and 19 are appended. Open Questions keep their
> numbers too — answered ones are marked **Answered** in place rather than removed, so
> inbound citations keep resolving. See the redirect note at the head of *Open Questions*.

> **Why 90.** Both blockers are gone. **Open Question 1 (the field set) is answered** — a
> report holds the error, the stack trace and a timestamp, and nothing else (Requirement 17),
> and `Tech Design.md` now carries that Decision. **Open Question 2 (where the code lives) is
> closed** — `Tech Design.md` → Decisions → Project structure — layer-first now carries
> `diagnostics/ ← crash catching/reporting, owned by P1-06-crash-reporting`, and `P1-01`
> Requirement 2 creates it. `CrashReport` is constructible, so every testable in this PRD is
> now writable. Requirement 19 is what keeps Requirement 17 true *through* the `error` field
> rather than only beside it. What remains open (Questions 3–7) is fenced by a requirement
> with an interim answer, so nothing blocks execution; each is a decision that would *change*
> behaviour, not one that is missing before work can start.

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

When this is done, an unhandled error anywhere in the app is caught by a known handler,
turned into a `CrashReport` holding the error, its stack trace and a timestamp, and handed
to a `CrashReportSink` that keeps it in memory and does nothing else with it. Exactly one
report per error — no double-counting, no silent gap. Nothing personal is captured, nothing
is transmitted, no dependency is added, and the player sees exactly what Flutter would have
shown anyway. The catch sites and the report type exist from the first build so that
choosing a destination later means writing a second `CrashReportSink`, not revisiting every
handler.

## Requirements

### What gets caught

1. **This wave reports unhandled errors only.** An "error" for the purposes of every
   requirement below is one that reaches the framework's or the platform's uncaught-error
   path. Errors that application code catches and recovers from — a theme file that fails to
   parse being the decided case (`Theming.md` → Decisions → What happens if a theme fails to
   load) — do **not** produce a report in this wave, and **this wave installs no
   application-facing "report this" entry point.**
   *Source: Tech Design → Decisions → Crash reporting — catch and build the report, don't
   send it ("putting in the catches now from the start … just catch and build out the
   object"). The doc does not distinguish the two kinds; this requirement fences the narrow
   reading rather than expanding scope by inference.*
   *Downstream, and now settled:* `P2-01-navigation.md` Requirement 8 cites this requirement
   and deliberately reports nothing when its repository read fails. Whether recovered errors
   ever report is Open Question 4, which no longer blocks anyone.

2. **Exactly two handlers are installed, in `main()` before `runApp`, and `runZonedGuarded`
   is not used.**

   | Handler | Catches |
   |---|---|
   | `FlutterError.onError` | Errors the Flutter framework catches — build, layout, paint, gesture and other framework callbacks |
   | `PlatformDispatcher.instance.onError` | Uncaught asynchronous and platform-thread errors that escape to the root zone; the handler returns `true` |

   **`runZonedGuarded` must not be installed.** It and `PlatformDispatcher.instance.onError`
   are alternatives to each other, not complements — wrapping `runApp` in a guarded zone
   *and* setting `PlatformDispatcher.onError` is the textbook double-report. Pick the
   platform-dispatcher form, which is the current guidance and needs no zone.
   *Availability note:* `PlatformDispatcher.instance.onError` requires Flutter 3.3 / Dart
   2.18 or newer. `P1-01` creates a fresh project on a current SDK, so this holds. If a
   pinned SDK ever predates it, substitute `runZonedGuarded` **instead of** it — never both.
   *Note for `P1-01` Requirement 11, which anticipates "any guarded zone" this PRD might
   install:* there is none. The handlers are assignments made before `runApp`, so its
   guarantee of a single wrappable call site is satisfied without wrapping anything.

   **The de-duplication rule that makes "exactly one" true:** each handler constructs one
   `CrashReport` and calls `CrashReportSink.add` exactly once, then returns. Neither handler
   rethrows, forwards to the other, or calls the other's hook. Presenting an error is not
   reporting it — `FlutterError.presentError` (Requirement 8) does not produce a second
   report.

   **Returning `true` decides what happens next for async errors**, and that is deliberate:
   the error is marked handled, the platform's default handler does not run, and the app
   continues. See Open Question 3, narrowed to what this requirement does *not* decide.

   **Background-isolate errors are out of scope this wave, deliberately and not by
   oversight.** Errors in a spawned isolate reach neither handler and would need
   `Isolate.current.addErrorListener` inside that isolate. Nothing in wave 1 spawns one — no
   PRD in the set calls `compute` or `Isolate.spawn` — so installing the listener now would
   be untestable ceremony. **The trigger to revisit is the first isolate anyone adds**, and
   whoever adds it owns the gap.
   *Testable:* three injected errors — one thrown from a widget `build`, one from an
   uncaught `Future`, one from a `Timer` callback — each produce exactly one report; the
   sink holds three.

### The objects

3. **The handoff is one type and one method, and catch sites depend on nothing else.**

   ```dart
   /// Three fields, fixed by Requirement 17. Nothing else is captured.
   class CrashReport {
     final Object error;
     final StackTrace stackTrace;
     final DateTime timestamp;   // captured at construction
   }

   /// The seam. Installed by Requirement 13; both handlers call it.
   abstract interface class CrashReportSink {
     void add(CrashReport report);
   }
   ```

   No handler references a sink implementation, a destination, or a transport — only
   `CrashReportSink.add`. Adding a destination later means writing a second implementation of
   this interface and passing it to Requirement 13's installer; no catch site changes.
   *Source: Tech Design → Decisions → Crash reporting ("We will come up with where it will
   be sent to later"); → Decisions → Online multiplayer is an intended future direction
   ("Tech choices must not foreclose syncing…"); the field set is Requirement 17's citation.
   The names and the signature are this PRD's, so that `forge-code-writer` and
   `forge-test-author` — which never see each other's output — build against the same surface
   instead of two invented ones.*
   **`error` is `Object`, which is why Requirement 19 exists:** the field holds the thrown
   object itself, so what a rendered report *says* is decided by that object's `toString()`,
   not by this class.

4. **The installed sink is `InMemoryCrashReportSink`, and it is the observation point every
   test uses.**

   ```dart
   class InMemoryCrashReportSink implements CrashReportSink {
     @override void add(CrashReport report);
     List<CrashReport> get reports;   // unmodifiable view, oldest first
     void clear();
   }
   ```

   Tests assert against `reports` and reset with `clear()`. No test asserts on console
   output, private state, or a spy the test itself installs at a seam the source does not
   offer. **How a test gets its sink in place is Requirement 13.**
   *Not an outbound-call check.* `P4-05-purchase-flow.md` Requirement 7 cites this
   requirement as writing one; it does not — see *Inbound claims that do not match this PRD*.
   *Testable:* the suite constructs an `InMemoryCrashReportSink`, installs it via
   Requirement 13, triggers an error, and reads `reports`.

5. **Retention is capped: the in-memory sink holds at most the 50 most recent reports,
   dropping the oldest on overflow.** An exception thrown from a `build` method re-fires
   every frame, so "one report per error" plus unbounded retention is an unbounded list.
   *[Interim value chosen by this PRD, not by a design doc — see Open Question 6. The number
   is changeable in one place and nothing else depends on it.]*
   *Testable:* add 60 reports; `reports.length` is 50 and the first added is gone.

### What must not happen

6. **The crash-report object is never transmitted.** No type in this feature declares a
   send, upload, flush, post, or destination member, and no call site passes a `CrashReport`
   to a network API — including the one network path the app is permitted.
   *Source: Tech Design → Decisions → Crash reporting ("We just won't send it out just yet…
   Just don't send it. yet") — today's answer for the destination is "nowhere"; and the same
   Decision: "StoreKit being permitted does not make a report destination permitted — those
   are two separate exceptions, and this one stops being true the day a destination is
   chosen."*
   *Testable — by source scan, not at runtime:* Flutter does not support `dart:mirrors`, so
   a test cannot enumerate a type's members at runtime. **The scan is specified rule by rule
   in Requirement 16**, which also states why Requirement 10 does not excuse anyone from
   writing it.

7. **No catch site or sink references a destination.** No URL, host, endpoint, socket,
   channel-to-elsewhere, or retry/back-off logic appears in this feature.
   *Scan boundary, so a legal buffer is not flagged:* the forbidden set is **destinations and
   transports**. `InMemoryCrashReportSink`'s list is retention, not a send-queue — a bounded
   in-memory `List<CrashReport>` with no consumer is explicitly permitted by Requirements 4
   and 5, and Requirement 16's rule table exempts it by name.

8. **This feature changes nothing the player sees.** The framework's default presentation is
   preserved exactly:
   - `FlutterError.onError` calls `FlutterError.presentError(details)` after handing the
     report to the sink, so debug-mode console output and the framework's own behaviour are
     unchanged.
   - **`ErrorWidget.builder` is left at the framework default and is not overridden in this
     wave.** A build-phase failure renders whatever Flutter renders by default.
   - No dialog, banner, snackbar, toast, sound, haptic, navigation or theme change results
     from a caught error.

   *[Fence set by this PRD. No design doc specifies any user-visible crash behaviour; the two
   nearby decisions are about other things — an illegal tap deliberately shows nothing
   (`Game Board Design.md` → Taps outside the legal quadrant), a failed theme load
   deliberately shows a modal (`Theming.md` → Decisions). Written as a requirement rather
   than left as a question so the implementer is not guessing; the user can overturn it —
   Open Question 7.]*
   *Testable:* a widget test whose child throws in `build` renders the default error widget,
   pushes no route, and shows no dialog; the sink holds one report.

9. **No crash-reporting service, telemetry SDK, or network client is added by this
   feature.** `pubspec.yaml` gains no Crashlytics/Sentry-style SDK and no HTTP or socket
   client as part of this work.
   *Source: Tech Design → Decisions → Crash reporting; → Decisions → Kids category
   ("Third-party analytics and behavioural advertising are restricted"); → What the Design
   Docs Already Imply → "**Fully offline, except for in-app purchases.** No backend, no
   network, no accounts — StoreKit is the one exception…"*
   *Testable:* inspect `pubspec.yaml` dependencies.
   *Boundary:* this does not forbid the store SDK, which is `P4-05-purchase-flow.md`'s to
   add — but it is a purchase transport, not a report transport, and Requirement 6 forbids
   routing a report through it.

10. **This feature introduces no backend of ours and no account system we operate**, and it
    **writes no new *outbound-call* check.** Nothing it adds talks to a server of ours: no
    HTTP client, no login, no user record.
    *Source: Tech Design → Decisions → Project structure — layer-first ("There is still **no
    backend data layer**: nothing in the app talks to a server"); → What the Design Docs
    Already Imply → the qualified *Fully offline, except for in-app purchases* row.*
    *Ownership, stated so it is written once:* **the outbound-call scan is
    `P1-01-app-scaffold.md` Requirement 6's to write** — one scan over `lib/`, finding no
    HTTP client and no network target other than the store SDK. This PRD adds no second one;
    it inherits that one and must not break it. `P4-05-purchase-flow.md` Requirement 7
    inherits the same scan in wave 4. The stricter form — "no networking API is reachable
    from `lib/`" — must **not** be built, per `P1-01` Requirement 6, because it fails the day
    `P4-05` ships.
    **This sentence does not excuse Requirement 16.** The outbound-call scan and the
    transport scan are different checks with different roots and different rules: one asks
    whether the *app* calls the network, the other asks whether *this feature* has grown a
    send path. Requirement 16 is this PRD's to write and nobody else writes it.

11. **Crash-reporting code introduces no Flutter import into `engine/`.** The two handlers
    are necessarily Flutter-side, and Requirement 15 places this feature in `lib/diagnostics/`
    — outside `engine/` entirely — so this requirement is satisfied by construction and
    exists to keep it that way.
    *Source: Tech Design → Decisions → Is the game logic separate from Flutter? ("pure Dart
    with zero Flutter imports"); → Decisions → Project structure — layer-first, whose tree
    now names `diagnostics/` as this feature's layer.*
    *Testable:* `P1-01-app-scaffold.md` Requirement 4's existing scan — every file under
    `lib/engine/` free of `package:flutter/`, `dart:ui`, `package:flutter_riverpod/` and
    `package:go_router/` imports — still passes after this feature lands.

12. **Handler installation happens before the first frame.** Both handlers from Requirement 2
    are installed in `main()` before `runApp(...)`, so an error thrown during startup — while
    preferences load, while themes materialize — is caught rather than lost.
    *Source: Tech Design → Decisions → Crash reporting ("putting in the catches now from the
    start").*
    *Testable:* an error thrown during startup produces a report.

### How it is installed, constructed, placed and checked

13. **Installation is one function, taking the sink as a parameter and returning a restore
    callback. There is no global, no static instance, and no provider.**

    ```dart
    /// Installs both handlers from Requirement 2, each closing over [sink].
    /// Returns a callback that restores whatever handlers were in place before,
    /// so a test can leave the process as it found it.
    void Function() installCrashHandlers(CrashReportSink sink);
    ```

    - `main()` calls `installCrashHandlers(InMemoryCrashReportSink())` before `runApp`
      (Requirement 12) and ignores the return value.
    - A test calls `installCrashHandlers(mySink)` in `setUp`, holds its own reference to
      `mySink`, and calls the returned callback in `tearDown`. **That is how every testable in
      Requirements 2, 4, 8 and 12 reaches the sink** — the test owns the instance it asserts
      against, so nothing needs to be reachable from elsewhere.
    - **Explicitly forbidden, because each satisfies looser wording and breaks the other
      agent's half:** a top-level mutable global sink, a `static CrashReportSink.instance`,
      an ambient service locator, and a Riverpod provider holding the sink.

    *Why not Riverpod, given it is the app's state management:* `P1-01-app-scaffold.md`
    Requirement 11 places this feature's handlers **outside `ProviderScope`** so that
    failures during scope construction are still caught. A sink read from a provider is not
    reachable at that point, so the one mechanism the house style would suggest is the one
    that cannot work here.
    *Downstream:* `P2-01-navigation.md` Requirement 8 cites this seam's forbidden list as its
    reason for not inventing a report path.

14. **Each handler has a named constructor.** The two handlers receive different shapes, and
    flattening them at the call site is where an implementer would improvise.

    ```dart
    /// From FlutterError.onError. Takes details.exception and details.stack.
    CrashReport.fromFlutterError(FlutterErrorDetails details);

    /// From PlatformDispatcher.instance.onError, which receives (Object, StackTrace).
    CrashReport.fromPlatformError(Object error, StackTrace stack);
    ```

    Both populate the three fields in Requirement 3 and nothing else. `details.stack` may be
    null on a `FlutterErrorDetails`; when it is, `StackTrace.empty` is stored — the field is
    non-nullable so that no consumer has to branch.
    *Source: the signatures are this PRD's; what they store is Requirement 17's.*

15. **This feature's files live in `lib/diagnostics/`.** No longer a proposal — the layer is
    in the design doc and the scaffold creates it.

    | File | Holds |
    |---|---|
    | `lib/diagnostics/crash_report.dart` | `CrashReport` and its two constructors (Reqs 3, 14, 17) |
    | `lib/diagnostics/crash_report_sink.dart` | `CrashReportSink`, `InMemoryCrashReportSink` (Reqs 3–5) |
    | `lib/diagnostics/install.dart` | `installCrashHandlers` (Req 13) |

    Imports are `package:tic_tac_toe_extreme/diagnostics/…`, using the package name `P1-01`
    establishes.
    *Source: `Tech Design.md` → Decisions → Project structure — layer-first, whose tree now
    reads `diagnostics/ ← crash catching/reporting, owned by P1-06-crash-reporting`, one of
    "five more new layers, each proposed by the PRD that needs it"; `P1-01-app-scaffold.md`
    Requirement 2 creates the directory, and its Requirement 11 notes that which file under
    `lib/diagnostics/` wraps `runApp` is this PRD's call — it is `install.dart`.*
    **File names inside the layer are this PRD's**, per the same Decision. The three above are
    this PRD's call; nothing outside this requirement and Requirement 16 names a path.
    *Consequence worth naming:* `lib/diagnostics/` sits inside `P1-05-theme-guard-test.md`'s
    `lib/**/*.dart` scan root. Harmless — this feature has no colors, fonts, durations, icons
    or asset paths — but it must stay that way for the guard's day-one-zero baseline to hold.

16. **The transport scan — owner, files, root, rules, exemptions, failure output.** This is
    the check Requirements 6 and 17 are verified by, written in the shape
    `P1-05-theme-guard-test.md` uses for its guard, because prose patterns are a coin flip.

    **Owner:** this PRD. **Files:**
    - `test/crash_transport_test.dart` — the test.
    - `test/support/crash_transport/scanner.dart` — the scanner and its rule table.

    **The scanner must not live under `lib/`**, for the reason `P1-05` gives for its own: its
    rule table holds the banned names as string literals and would flag itself.

    **Root:** `lib/diagnostics/**/*.dart`. Not all of `lib/`; a widget named `postGameSummary`
    elsewhere is nobody's business here.

    | Rule | Matches | Deliberately does not match |
    |---|---|---|
    | `transport-member` | A **declaration** — method, getter, setter or field — whose name is exactly `send`, `upload`, `post`, `flush`, `transmit`, `dispatch`, `endpoint`, `destination`, or `url` | `postGameReport`, `sendable`, or any name that merely contains one of these as a substring |
    | `report-to-network` | A `CrashReport` (or the `reports` list) passed as an argument to any member of a network client, or to `HttpClient`, `Socket`, `WebSocket`, `dart:io`'s network surface, or the store SDK | Passing a report to `CrashReportSink.add` or to `List.add` |
    | `network-import` | An import of `dart:io`, `dart:html`, `package:http`, or any store SDK from a file in the root | Nothing — this feature imports none of them |
    | `report-field-count` | An **instance field declared on `class CrashReport`** whose name is not exactly `error`, `stackTrace` or `timestamp`. A *field*, for this rule, is an instance variable declaration (`final`, `var`, `late`) **or** a `this.`-initializing constructor parameter | `static` members and `static const`s; getters and methods, which compute from the three fields and carry nothing new; the two named constructors of Requirement 14 and their non-`this.` parameters; local variables; fields on any other class in the root, including `InMemoryCrashReportSink`'s |

    **`report-field-count` is the mechanism that enforces Requirement 17's field set, and it
    is the only one.** Requirement 6 already records why: Flutter does not support
    `dart:mirrors`, so **no runtime unit test can enumerate `CrashReport`'s members** — a test
    asserting "exactly three fields" is not writable at all. Requirement 17 therefore declares
    no second check, and there is no unit-test half to look for.
    **What it does not reach, so nobody reads it as more than it is:** it counts fields **on**
    `CrashReport`. It says nothing about what is reachable **through** `error`, which is
    Requirement 19's subject.

    **Exempt contexts, so the check is not a coin flip:** matches inside `//` and `///`
    comments, inside `/* */` blocks, and inside string literals are ignored, so
    `// don't send this` is not a violation. Matching is on **whole identifiers** at
    declaration sites, not on substrings anywhere in a file. `InMemoryCrashReportSink`, its
    `reports` getter, its backing list and its `clear()` are exempt by name from
    `transport-member` — Requirement 7 permits exactly that buffer, and a scan that flags it
    would leave the feature no legal implementation.

    **Failure output** names the file, line, matched identifier and rule id, in the shape
    `P1-05` Requirement 6 uses — for `report-field-count`, the line of the offending field
    declaration and its name. **No suppression convention** — no comment that switches a
    rule off. If a rule is wrong, change the rule table.
    *Testable:* the scanner is called with inline fixture strings — a legal
    `InMemoryCrashReportSink`, a `void send(CrashReport r)` declaration, an
    `httpClient.post(report)` call, an `import 'package:http/http.dart'`, the string
    `'// don't send this'`, a legal three-field `CrashReport`, and a `CrashReport` carrying a
    fourth field `final String route;` — and reports violations for exactly the three
    transport fixtures and the four-field one.

### What the report holds

17. **A crash report captures the error, the stack trace, and a timestamp. Nothing else.**
    No game state, no board position, no screen or route, no device or user identifier, and
    **specifically no opponent name — no text a player has typed.**

    *Source: `Tech Design.md` → Decisions → **What does a crash report capture?** — "**The
    error, the stack trace, and a timestamp. Nothing else.** No game state, no screen, and
    specifically no opponent name — no text a player has typed," which also carries the
    reasoning and the accepted cost below. The answer originated as the user's, relayed
    2026-08-07, closing this PRD's Open Question 1; the doc now records it, so this
    requirement cites the doc.*
    **The reasoning, which is the part that generalises and is why it belongs in the
    requirement rather than only in a changelog:** the app is in Apple's **Kids category** at
    a **4+** rating (`Tech Design.md` → Decisions → Kids category), and in a 4+ app
    **transmitting personal data is itself the regulated act**, not something a privacy label
    merely declares. Capturing nothing personal means that if a destination is ever chosen,
    **no consent flow is required** — the decision keeps a future option open rather than only
    satisfying today's rules.

    **The accepted cost, recorded so it is not rediscovered as a defect:** a bug that depends
    on board position or on which screen the player was on becomes harder to reproduce,
    because the report will not say. That was named and accepted when the decision was taken,
    and `Tech Design.md` records it in the same Decision.

    **This requirement is the durable one.** A field added later is not a free change: it must
    clear the same rule, and any field carrying player-entered text reopens the consent
    question above.
    **The field set is enforced by Requirement 16's `report-field-count` rule — not by a unit
    test**, which `dart:mirrors`' absence makes unwritable (Requirement 6). Earlier revisions
    of this requirement claimed a scanner rule that did not exist in Requirement 16's table;
    the rule now exists and is named.
    *Testable:* the scanner's `report-field-count` rule passes on `crash_report.dart` as
    written and fails on a fixture declaring a fourth field. A unit test constructs a report
    through both constructors in Requirement 14 and asserts the error and stack round-trip and
    the timestamp is set.
    **What this requirement cannot see, and Requirement 19 covers:** `error` is an `Object`,
    so a report holding three fields can still *render* a board position if the object in that
    field prints one.

18. **`CrashReport` is a plain Dart class — not a `freezed` model, and not
    `json_serializable`.** No generated file, no `build_runner` step for this feature.
    *Source: `Tech Design.md` → Decisions → Serialization and the storage layer scopes
    `freezed` + `json_serializable` to **"the domain models in `engine/`"**. A crash report is
    neither — it lives in `lib/diagnostics/` (Requirement 15), and with nothing transmitted
    (Requirement 6) and nothing persisted (Requirement 4) there is no `toJson` for the
    generator to produce. This closes the second half of Open Question 2 by scope rather than
    by preference; if a destination or persistence later needs serialization, that work adds
    it then.*
    *Testable:* no `*.g.dart` or `*.freezed.dart` file exists under `lib/diagnostics/`.

19. **The one error type that carries game state renders none of it:
    `IllegalMoveError.toString()` prints the reason and the `Move`, and never the `Board`.**

    Requirement 3 stores `final Object error` — **the error object itself** — so every way a
    report is ever rendered as text goes through that object's `toString()`. The engine's
    `IllegalMoveError` (`P1-02-engine-rules.md` req 42) carries the offending `Move` **and the
    `Board` it was applied to**, and it is the one object reachable from a `CrashReport` that
    holds an 81-cell board position. An unconstrained `toString()` on it is what would put
    that position inside a report whose field set (Requirement 17) exists to exclude it —
    through a field Requirement 16's `report-field-count` rule cannot see, because the leak is
    *inside* `error` rather than beside it.

    **Settled by the user, as the resolution of the contradiction both PRDs previously
    flagged.** The error object **keeps** its `Board` field — that is the debugging value
    `P1-02` req 42 was written for, and it stays readable from a debugger attached in process
    — and **nothing renders it into text**: `toString()` returns the `IllegalMoveReason` and
    the `Move`'s two indices, and nothing drawn from the board.
    *Source: the user's settlement, recorded here and in `P1-02-engine-rules.md` req 42, which
    carries the same contract from the throwing side. The field set it protects is Requirement
    17's, whose citation is `Tech Design.md` → Decisions → What does a crash report capture?*

    **The residual, recorded so it is not rediscovered later as a defect.** This is a contract
    on a **string**, not an invariant on the object. The `Board` is still on the error, so any
    route that renders or copies a report *other than* `toString()` re-leaks the position: a
    `toJson` added to the error or to `CrashReport`, a **persisted** report (Open Question 5),
    a reflective or code-generated serializer walking `error`, or a debugger dump written to a
    file. **Whoever adds persistence or a destination owns closing that**, and Open Question 5
    now carries it as a stated constraint rather than as a discovery waiting to happen.
    Nothing here designs either.

    *Testable, from the consuming side:* a `CrashReport` built through either Requirement 14
    constructor from an `IllegalMoveError` thrown on a board with a distinctive position
    renders — via `'${report.error}'` — a string that contains the reason and both of the
    move's indices, and that contains neither `board.toString()` nor any of the field names a
    `freezed` `Board.toString()` prints (`cells`, `quadrants`, `score`).
    *The assertion on the error type itself is `P1-02-engine-rules.md` req 42's*, written in
    the engine's own suite; this one asserts the path a report actually takes.

## Inbound claims that do not match this PRD

Flagged, not fixed — these live in other PRDs and are theirs to correct.

- **`P4-05-purchase-flow.md` Requirement 7** (and its header citation table) says this PRD's
  **Requirement 4** "writes the same check in the same form" as `P1-01` Requirement 6's
  outbound-call scan. It does not. Requirement 4 is `InMemoryCrashReportSink`, and
  Requirement 10 explicitly disclaims writing any outbound-call check — `P1-01` Requirement 6
  owns that one, alone. **The claim that matters to `P4-05` is still true** — nothing here
  transmits, per Requirements 6, 7, 9 and 10 — but it should cite those, not Requirement 4.
- **Resolved, recorded so it is not re-raised:** `P2-01-navigation.md` Requirement 8 used to
  assert that a failed repository read "is reported through `P1-06`'s handler." It now states
  the opposite — the failure is caught, recovered, and **not** reported this wave — citing
  this PRD's Requirement 1 for the unhandled-only scope and Requirement 13 for the absence of
  any application-facing report path. Nothing further is owed in either direction.

## Out of Scope

- **Transport of any kind** — sending, queuing for send, retrying, batching, endpoint
  configuration, auth. The destination is deliberately deferred: Tech Design records today's
  answer as "nowhere," with the destination to be chosen later.
- **An application-facing "report this caught error" API** — Requirement 1. It would exist
  only if Open Question 4 widens the scope.
- **Background-isolate error capture** — Requirement 2 states why, and names the trigger to
  revisit.
- **In-app purchases and StoreKit** — `P4-05-purchase-flow.md`.
- **The outbound-call scan** — `P1-01-app-scaffold.md` Requirement 6 (see Requirement 10).
  Not to be confused with Requirement 16, which is this PRD's.
- **Creating `lib/diagnostics/` and the rest of the tree** — `P1-01-app-scaffold.md`
  Requirement 2. This PRD writes the files inside it.
- **`IllegalMoveError` itself — its type, its two reasons and its payload** —
  `P1-02-engine-rules.md` req 42. Requirement 19 constrains only what that error *renders*,
  which is this PRD's business because Requirement 3 holds the object.
- **Persistence mechanics** — `P1-04-persistence.md`. Whether a report survives a restart is
  Open Question 5, which Requirement 19's residual now constrains.
- **Release tooling and App Store Connect** — `P5-03-release-fastlane.md`.
- **Symbolication and dSYM handling** — pointed at `P5-03-release-fastlane.md`, the right
  destination if it ever becomes anyone's, but **that PRD declines the delegation and nothing
  else picks it up**: no design doc mentions symbolication, dSYM upload, or a crash-report
  destination, so a dSYM requirement there would invent the destination the crash-reporting
  Decision withholds. **An open gap, not a settled hand-off.**
- **The "theme failed to load" modal** — theming's, per `Theming.md` → Decisions. Whether it
  also produces a report is Open Question 4.
- **Analytics, usage metrics, or any other data collection.** No design doc asks for these,
  and the Kids category restricts third-party analytics outright.

## Open Questions

> **Numbering is frozen; answered questions stay in place.** Open Questions were renumbered
> once, before this revision. Inbound citations in `P1-01-app-scaffold.md`, `P2-02-audio.md`
> and `P2-03-haptics.md` may still cite **Open Question 6** for *where the error-handling code
> lives* — that is **Open Question 2**, and it is now **answered**. Open Question 6 is the
> retention cap.

1. **~~What is the report's minimum field set?~~ Answered — see Requirement 17.** The report
   holds the error, the stack trace and a timestamp; no game state, no screen, and no text a
   player typed. The reasoning is recorded in Requirement 17 because it generalises to any
   future field: in a Kids-category 4+ app, transmitting personal data is the regulated act,
   so capturing nothing personal keeps a future destination free of a consent flow. The
   accepted cost — position- and screen-dependent bugs get harder to reproduce — is recorded
   there too. **`Tech Design.md` now carries this decision** as Decisions → *What does a crash
   report capture?*, with both the Kids-category reasoning and the named cost, so Requirement
   17 cites the doc and no doc edit is owed. (Earlier revisions of this PRD flagged one; that
   flag is stale and has been removed.)

2. **~~Where does this code live, and what shape is `CrashReport`?~~ Answered — see
   Requirements 15 and 18.** `Tech Design.md` → Decisions → Project structure — layer-first
   now lists `diagnostics/ ← crash catching/reporting, owned by P1-06-crash-reporting`, added
   alongside four other layers because "this closes the same gap in five PRDs at once," and
   `P1-01` Requirement 2 creates the directory. `CrashReport` is a plain class in
   `lib/diagnostics/`, not a `freezed`/`json_serializable` model and not in `engine/`.

3. **What does the app do after catching — the part Requirement 2 has not already decided?**
   Requirement 2 settled the async case: `PlatformDispatcher.onError` returns `true`, meaning
   handled-and-continue, so **"terminate" is foreclosed for every asynchronous error** and
   only the returning-`false` variant would reopen it. What remains open is (a) whether
   continue-on-async-error is the stance you want, given that returning `false` instead would
   let the platform's default handler run, and (b) whether a build-phase failure that
   re-fires every frame should ever escalate rather than render the default error widget
   forever. No design doc addresses either. **Not blocking** — the interim behaviour is
   stated and testable.

4. **Unhandled errors only, or recovered errors too?** Requirement 1 fences this wave to
   unhandled. **No longer has a waiting dependent:** `P2-01-navigation.md` resolved its own
   Requirement 8 by explicitly not reporting a recovered repository failure and citing this
   scope. The standing case on the other side is a theme file that fails to parse
   (`Theming.md` → Decisions). If the answer is "recovered too," the seam already exists —
   `CrashReportSink.add`, reachable through the sink passed to Requirement 13 — so no new API
   is needed.

5. **Is a report held only in memory, or persisted?** Requirement 4 keeps them in memory,
   which means they are gone when the app dies — including the crash that produced them. If
   they should survive: which store, `shared_preferences` or Hive (`Tech Design.md` →
   Decisions → Persistence package, Game state storage — Hive), and does the stored shape
   inherit `Tech Design.md` → Open Questions → 1. Persisted data — versioning?
   **This got simpler, not harder, once Requirement 17 landed.** An earlier revision flagged
   redaction and an at-rest cap as unowned worries. With no player-entered text in a report
   there is nothing to redact, so persistence carries no privacy question — only the ordinary
   ones about where and in what shape. Recorded so the caution is not left standing
   unexamined and treated as a reason to hesitate.
   **One constraint this answer inherits, from Requirement 19.** Persisting a report means
   writing `error` down somehow, and `error` may be an `IllegalMoveError` holding a whole
   `Board`. Requirement 19's contract binds `toString()` and nothing else, so a persistence
   design that serializes the error object by any other route — a `toJson`, a reflective or
   generated serializer — re-leaks the board position Requirement 17 excludes. Whatever
   answers this question has to say which rendering of `error` reaches the store. Named as a
   constraint on the answer; not designed here.

6. **Is 50 the right retention cap?** Requirement 5 states 50 as this PRD's interim call so
   nothing is blocked. Any number, or "unbounded is fine," replaces it in one place.

7. **Should a caught error ever be visible to the player?** Requirement 8 fences this to "no"
   — the framework default, nothing added — because no design doc specifies any crash UI and
   an unspecified one would be invented. Recorded so the fence stays visible as a default the
   user can overturn rather than a decision taken quietly.
