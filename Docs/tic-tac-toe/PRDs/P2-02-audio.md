**Build-readiness: 69** — last formal grade (round 10).

**The call-site table was wrong and is now corrected against each sibling's actual text.** The
finding was right; the specifics I was handed were not, in both directions. Verified one file
at a time:

| Site | Claimed | Actual |
|---|---|---|
| `P4-01` req 24 | haptic only | **owns both** — *"fires one haptic and one sound"*, `play(SoundMoment.buttonTap)` |
| `P4-03` | req 18 owns it | req 18 is the **haptic**; **req 25** is the sound, added when OQ-3 closed |
| `P4-04` req 25 | real | **real** — both channels, six controls |
| `P3-03` | req 12 wrong, use req 22 | **req 12 is correct** — that PRD states *"the call site of record is requirement 12 and not requirement 22; requirement 22 details the call and owns no site of its own"* |
| `P4-02` req 30 | haptic only | **confirmed** — no `SoundMoment` anywhere in the file |
| `P3-04` req 5 | neither | **confirmed**, and circular: its req 16 says *"Whether the two card controls fire `buttonTap` is `P2-02`'s to say, not this PRD's"* |

So `buttonTap` is **4 of 6 sites owned, 2 unassigned** — not 2 of 6. The false supporting claim
("each already fires the haptic on the same gesture") is deleted; it does not hold for `P3-04`
req 5, which is the control inventory. The header no longer says every moment is owned.

**Also corrected in this pass:** `P1-04`'s `Settings` carries **four** fields and five
persisted preferences, not three (reqs 5, 22); req 15's retention reason was a citation that
does not exist — `P1-03` req 17 cites **reqs 6 and 7** — and now says so plainly; req 17 gains
an assertable testable in place of a claim this layer cannot make.

**Not changed, because it was already correct:** `P1-01` req 2 is cited as building **fourteen**
paths including `audio/`, in the Depends-on bullet, in *The directory, settled on both sides*,
and in Out of Scope. That was fixed last round and is still right.

# PRD: Audio Playback

> **Status:** Draft · Source docs read: `Theming.md`, `Tech Design.md`, `Menus and UI.md`,
> `Game Board Design.md`, `Animations.md`, `Game Overview.md`, `Rules.md`, `roadmap.md`,
> and the read-only reference asset `design_handoff_game_ui/` (`README.md`,
> `neon.theme.json`, `themes.catalog.json`). `Alternative Game Styles.md` is a declared
> parking-lot doc and was not used as a source.

**Wave:** P2 · **File:** `P2-02-audio.md` — parallel-safe with the other P2 PRDs.

**Scope:** this PRD owns **one-shot sound effects only**. A theme supplies its own music, and
**music is not in this layer** — see Requirements 14 and 15.

**Depends on:**

- `P1-01-app-scaffold.md` — declares the `audioplayers` dependency, creates `assets/audio/`,
  fixes the no-codegen Riverpod idiom (req 12) and sets the analyzer floor (req 15). **Its
  req 2 creates `lib/audio/` and names this PRD as the layer's owner**, one of the fourteen
  paths its tree now builds.
- `P1-03-theme-system.md` — **req 15** is the schema (`sound`, seven keys, five playable,
  value shape `assetPath`); **req 8** is the merge rule, including null-as-clear; **req 24**
  publishes `activeThemeProvider` (`Provider<Theme>`, `lib/theme/theme_providers.dart`) and
  makes `read`-at-use-time normative here. **Its Blocking item 1 holds music's key shape.**
- `P1-04-persistence.md` — **req 26** declares `soundEffectsEnabledProvider`, a
  `Provider<bool>` in **`lib/state/settings_providers.dart`**, resolving an absent stored
  value to `true`; **req 27** makes a setter's new value visible to the next `read` in the
  same frame. Its `Settings` carries **four** toggles (music, sound effects, vibrate,
  animations) across **five** persisted preferences.
- `P1-06-crash-reporting.md` — **req 2** installs `PlatformDispatcher.instance.onError`, which
  turns any unhandled async error into a `CrashReport`. That is why Requirement 25's catch
  form is part of the contract rather than a style choice.

> **`play(SoundMoment)` needs no `BuildContext`.** `P1-03` req 24 settles the active theme as
> a plain Riverpod object rather than a `ThemeExtension`, naming this signature as the
> decisive reason.

**Depended on by:** `P3-02-move-input.md` req 15 and its forthcoming claim/cat requirement,
`P3-03-scoreboard-turn-indicator.md` req 12, `P3-04-game-over-rematch.md` reqs 16–17,
`P4-01-main-menu.md` req 24, `P4-03-theme-selection.md` req 25, `P4-04-settings.md` req 25
(whose **fourth** toggle is Music, a layer this PRD does not own), `P5-01-classic-theme.md`,
`P5-02-asset-generation-replicate.md` reqs 3, 7–9, which cites reqs 17–19.

**Three call sites are still unassigned** — `claimQuadrant`, `catGame`, and two of the six
`buttonTap` sites. See Requirement 6 and Out of Scope; none is this PRD's to write.

**What is assertable when.** Wave 2 ships the layer and everything observable at its own
seams: Requirements 2–7, 11, 14, 16, 17, 20, 21(a), 22, 23, 25 and 26. Requirements 8, 9, 10
and 19 need a board, a sibling layer or a shipped asset; **21(b) has no wave-2 assertion at
all**, stated as such rather than papered over.

---

## The directory, settled on both sides

`lib/audio/` exists and is this PRD's. It arrived the way the tree's other layers did — by
amending the design doc first: `Tech Design.md` → Decisions → *Project structure —
layer-first* lists `audio/ ← sound playback, owned by P2-02-audio` alongside `haptics/`,
`entitlements/`, `diagnostics/` and `purchase/`, noting that *"file names inside each are that
PRD's to decide."*

**`P1-01-app-scaffold.md` req 2 has since carried that amendment through**: it builds
**fourteen** paths, pairs each with its owning PRD — `audio/` with this one — creates all
fourteen with `.gitkeep` where empty, and verifies that no other directory appears under
`lib/`. Nothing is outstanding on either side, and this PRD proposes no directory.

## Problem

The game is silent, and there is no code path that could make it otherwise. Nothing loads,
holds or plays an audio file, so a confirmed move, a claimed quadrant, a cat game, a won
game and a menu tap are all indistinguishable to a player who is not looking directly at
the thing that changed — on a board with 81 cells, passed back and forth between two people.

There is also a structural risk. `Theming.md` → Architectural Rule says *"if something
makes a noise, that sound came from the theme"*, and the first feature that plays a sound
is the one that decides whether that stays true. An audio layer that reaches for a file
path directly, or that hardcodes which sound belongs to which event, breaks the rule the
whole theme system exists to enforce and has to be unpicked from every caller later.

## Goal

The app can make a noise, and every noise it makes came from the active theme. One named,
injectable layer built on `audioplayers` plays one-shot sound effects at the moments the
design docs name, taking every asset path from the materialized theme object and holding none
of its own. A global player-owned sound-effects toggle silences all of it under any theme,
taking effect on the next sound rather than the next launch. It is complete and testable
against the theme content that exists today — Neon's `"TODO"` placeholders — and it plays
Neon's buzz and Classic's splat unchanged the day those files land.

## Requirements

### The audio layer

1. **The audio package is `audioplayers`.**
   *(`Tech Design.md` → Decisions → Audio package. The dependency is declared by
   `P1-01-app-scaffold.md`.)*

2. **The seam is one injectable layer, addressed by naming a moment.** Callers never
   construct a player, name an asset, or await anything.

   ```dart
   // lib/audio/sound_moment.dart
   enum SoundMoment { placeMark, claimQuadrant, catGame, winGame, buttonTap }

   // lib/audio/audio_layer.dart
   abstract interface class AudioLayer {
     /// Fire-and-forget. Returns immediately; never reports whether anything
     /// was audible. For what "never throws" does and does not cover, see
     /// Requirement 25.
     /// The mute gate is INSIDE this call — callers invoke it unconditionally
     /// and never read the setting (Requirement 16).
     void play(SoundMoment moment);
   }
   ```

   - `SoundMoment` has **exactly these five values** — one per Requirement 6 row, and none
     for `music` or `signature` (Requirements 7, 14).
   - `play` returns **`void`**, is synchronous and non-awaitable, and is the **only** public
     method. No `stop`, no `isPlaying`, no future to await: a caller that could branch on
     playback state would put audio logic back at the call site.
   - **`AudioLayer` is the only audio symbol the rest of the app may name.** `OneShotSink`,
     `OneShotPlayer`, `AudioSession`, `oneShotSinkProvider`, `audioPlayerFactoryProvider`,
     `audioSessionProvider`, `ThemedAudioLayer` and `AudioPlayersSink` are public Dart symbols
     only because Dart has no library-private-across-files; **nothing outside `lib/audio/` may
     reference them.** This is what makes the mute gate unbypassable and OQ-5's fence
     structural: a widget that could reach `oneShotSinkProvider` could play a sound around
     Requirement 16 entirely.

   *(**Derived, not stated** — no doc names an audio layer; it is the shape
   `Theming.md` → Architectural Rule and `Tech Design.md` → Decisions → Do we add a test that
   fails on hardcoded theme values? force. The fire-and-forget contract mirrors
   `P2-04-animations.md` req 6 and `P2-03-haptics.md` req 13.)*
   *Testable (wave 2):* the enum has exactly five values; a source scan finds no reference to
   `audioplayers`, `AudioPlayer`, or any symbol listed above anywhere under `lib/` outside
   `lib/audio/`. **The scan reads executable code only — `import`/`export` URIs and comment
   text are exempt** (see Requirement 3, which shares the rule).

3. **No hardcoded audio anywhere, and the theme slot carries the whole path.** Every sound
   played is read from the active theme's sound slots. `P1-03-theme-system.md` req 15 fixes
   the value shape: **`assetPath` = "a path under `assets/`, or null"** — the slot holds the
   full path, not a bare file name and not a key into a manifest.
   `P5-02-asset-generation-replicate.md` req 7 publishes the filenames
   (`assets/audio/neon-<slot>.<ext>`, `assets/audio/classic-<slot>.<ext>`), and its req 8
   makes **audio format per-entry rather than global**: the generation entry's `ext` declares
   it and req 7 verifies it, with `.mp3` expected but `wav` an open path because most
   Replicate audio models emit wav or flac. **Nothing here depends on which:** `AssetSource`
   is format-agnostic and this layer never writes an extension.

   **Prefix handling, stated because Requirement 21(a)'s determinism depends on it:**
   `audioplayers` `AssetSource` takes a path *relative to* `assets/` and supplies the prefix
   itself, so the layer strips a single leading `assets/`. **A slot value that does not begin
   with `assets/` is not playable** — rejected synchronously, never handed to the sink. The
   layer contains **no asset path, file name or audio-format literal**; the sole string it
   holds is the `'assets/'` prefix constant, which is clean against the guard: `P1-05`'s
   `asset-path` rule requires at least one character after `assets/`, and its `asset-source`
   rule requires a quote immediately after the paren, so passing a variable does not match.
   No whitelist is needed; `P1-03` req 25 records the same finding for the theme layer.
   *(`Theming.md` → Architectural Rule; `Tech Design.md` → Decisions → Do we add a test that
   fails on hardcoded theme values?; `P1-03-theme-system.md` reqs 15, 25;
   `P1-05-theme-guard-test.md` req 6; `P5-02` reqs 7–8.)*
   *Testable (wave 2):* the guard test passes and its baseline gains no entry; **excluding
   `import`/`export` URIs and comments**, a grep of `lib/audio/` finds no `.mp3`, `.wav`,
   `.flac` or `.m4a` literal and exactly one `'assets/'`. (Without that exclusion the scan is
   unsatisfiable — every `import` in this layer's own files ends in `.dart`.) Given
   `assets/audio/x.mp3` the sink receives `audio/x.mp3`; given `assets/audio/x.wav` it
   receives `audio/x.wav`.

4. **A theme is a full audio-visual package, not a skin.** Sound is theme-driven exactly
   like visuals: changing the active theme changes the entire sound set with **zero changes
   to game, board or menu code**, and adding a new theme adds only a theme definition.
   *(`Theming.md` → Decisions → Do themes affect sound; → Architectural Rule)*
   *Testable (wave 2):* overriding `activeThemeProvider` with a fixture theme whose sound
   slots differ — the test seam `P1-03` req 24 names — the same `SoundMoment` resolves to the
   new theme's path, with no diff in game, board or menu code.

5. **The public surface is named, and these are the names.**

   ```dart
   // lib/audio/audio_layer_provider.dart

   import 'package:flutter_riverpod/flutter_riverpod.dart';
   import 'audio_layer.dart';                 // AudioLayer — Requirement 2
   import 'audio_players_sink.dart';          // AudioPlayersSink, AudioPlayersPlayer,
                                              // GlobalAudioSession — Requirement 25
   import 'sound_moment.dart';                // SoundMoment — Requirement 2
   import '../theme/theme.dart';              // Theme — P1-03 req 15's object
   import '../theme/theme_providers.dart';    // activeThemeProvider — P1-03 req 24
   import '../state/settings_providers.dart'; // soundEffectsEnabledProvider — P1-04 req 26

   typedef SoundEffectsSource = bool Function();
   typedef ActiveThemeSource = Theme Function();

   /// One player's worth of one-shot playback. Declared here rather than using
   /// `AudioPlayer` directly so a test can substitute one — Requirement 25.
   abstract interface class OneShotPlayer {
     void start(String assetRelativePath);
     void stopNow();
     void dispose();
   }

   /// The process-wide audio session. An interface because the real call is a
   /// static (`AudioPlayer.global.setAudioContext`) and a static cannot be
   /// observed — Requirements 25, 26.
   abstract interface class AudioSession {
     void configure();
   }

   /// The boundary between this layer's rules and the plugin.
   /// There is no `stop`: restart-on-re-fire is the sink's own business
   /// (Requirement 25), which is what keeps OQ-5's fence structural.
   abstract interface class OneShotSink {
     /// [assetRelativePath] is already stripped of the `assets/` prefix and has
     /// already passed Requirement 21(a)'s prefix check.
     void playOneShot(SoundMoment moment, String assetRelativePath);
     void disposeAll();
   }

   final class ThemedAudioLayer implements AudioLayer {
     ThemedAudioLayer({
       required this.soundEffects,
       required this.activeTheme,
       required this.sink,
     });

     final SoundEffectsSource soundEffects;
     final ActiveThemeSource activeTheme;
     final OneShotSink sink;

     /// Requirement 21(a)'s memo. An INSTANCE field, never static — see below.
     final Set<SoundMoment> _loggedBadPaths = <SoundMoment>{};

     @override
     void play(SoundMoment moment) { /* Requirements 16, 11, 21(a), then sink */ }
   }

   typedef OneShotPlayerFactory = OneShotPlayer Function();

   final audioPlayerFactoryProvider =
       Provider<OneShotPlayerFactory>((ref) => AudioPlayersPlayer.new);
   final audioSessionProvider = Provider<AudioSession>((ref) => GlobalAudioSession());

   /// The sink owns the players, so it owns their release — Requirement 23.
   final oneShotSinkProvider = Provider<OneShotSink>((ref) {
     final sink = AudioPlayersSink(
       createPlayer: ref.watch(audioPlayerFactoryProvider),
       session: ref.watch(audioSessionProvider),
     );
     ref.onDispose(sink.disposeAll);
     return sink;
   });

   final audioLayerProvider = Provider<AudioLayer>((ref) => ThemedAudioLayer(
         soundEffects: () => ref.read(soundEffectsEnabledProvider),
         activeTheme: () => ref.read(activeThemeProvider),
         sink: ref.watch(oneShotSinkProvider),
       ));
   ```

   - **Every imported symbol is named with its file.** `Theme` is `P1-03` req 15's schema
     object from `lib/theme/theme.dart`; `activeThemeProvider` is
     `lib/theme/theme_providers.dart` (`P1-03` req 24); `soundEffectsEnabledProvider` is
     **`lib/state/settings_providers.dart`** (`P1-04` req 26), *not* `lib/storage/`. The
     directories are stated because `P2-03-haptics.md` and `P4-04-settings.md` both shipped
     import paths pointing at the wrong one for this provider family.
   - **The factory returns `OneShotPlayer`, not `AudioPlayer`.** A factory returning the
     concrete plugin type cannot be faked, which left Requirements 23, 25 and 26 with nothing
     to observe. `AudioPlayersPlayer` (Requirement 25) is the one class that touches
     `audioplayers`.
   - **⚠ Assumption this PRD is fencing, not a citation.** `P1-03` req 24 publishes
     `Provider<Theme>` but **does not show a member access**, and its req 15 gives the *YAML*
     shape (`assetPath` = a path under `assets/`, or null) without pinning the Dart member or
     its nullability. This PRD assumes **`activeTheme().sound.placeMark` and its four siblings
     are `String?`**. Nullability is load-bearing: Requirement 11 requires a null branch, and
     `P1-03` req 8's own testable (`sound.buttonTap: null` yields no button-tap sound) makes
     null reachable even though req 15 marks the five slots `required` — `required` there
     means *Neon must hold a value*, not *the Dart type is non-nullable*. **If `Theme.sound`
     exposes non-nullable strings, Requirement 11 cannot be implemented as written.** Routed
     to `P1-03`; not worked around here.
   - **`ref.read` for the two *value* sources, never `ref.watch`.** `P1-03` req 24 makes this
     normative — *"Widgets `watch`. Services `read` at use time, never captured in a
     constructor"* — and names this layer directly. `watch` would make `audioLayerProvider` a
     dependent, rebuilding it on every theme change or toggle flip. The closures capture
     `ref`, not the values. **`ref.watch` of the three infrastructure providers is correct**:
     none has a value that changes at runtime.
   - **The memo in `_loggedBadPaths` is an instance field, never `static`.** A static memo
     survives across tests in the same process, so Requirement 21(a)'s "exactly five lines"
     would pass in the first test that ran it and fail in every later one — a flake whose
     cause is invisible from the failing test.

   *(`Tech Design.md` → Decisions → State management — Riverpod; `P1-03` req 24; `P1-04`
   reqs 26–27; `P2-03-haptics.md` req 14 as the shape template.)*
   *Testable (wave 2) — the `read`/`watch` constraint.* In a `ProviderContainer` with
   `preferencesRepositoryProvider` overridden by **`FakePreferencesRepository`** — an
   in-memory store that is *empty*, so each of its **four** preference reads completes with
   `null`, which `P1-04` req 26 resolves to `true` — and `oneShotSinkProvider` overridden with
   a `RecordingOneShotSink`:

   ```dart
   final first = container.read(audioLayerProvider);
   container.read(settingsProvider.notifier).setSoundEffects(false);
   final second = container.read(audioLayerProvider);
   expect(identical(first, second), isTrue);  // a `watch` implementation rebuilds → fails
   //
   // No await, no pump, no pumpEventQueue anywhere between the three lines above:
   // SettingsNotifier.build() fires unawaited(_seed()), and if that seed resolves it
   // overwrites all four fields — restoring soundEffects to the default `true` and
   // silently invalidating the assertion. The setter assigns state before its first
   // await, so the un-awaited call has already taken effect on the next line.
   // (P2-03 req 14 carries the same caveat for the vibrate half.)
   ```

   Repeat with `activeThemeIdProvider`'s `selectTheme(...)` for the theme half. A source scan
   of `lib/audio/` finds no `ref.watch(activeThemeProvider)` and no
   `ref.watch(soundEffectsEnabledProvider)`.
   **Why this declares its own preferences stub rather than reusing `P2-03`'s.** That PRD's
   equivalent is `_NullPreferencesRepository`, declared with a leading underscore inside its
   own test file per its req 15 table. Dart privacy is per-library, so an underscore-prefixed
   class **cannot be imported by another test file** — reuse is not available, and two stubs
   for the same job in the same wave is the language's doing rather than a duplication this
   PRD chose. If either is ever promoted to a shared `test/support/` file, the other should be
   deleted in the same change.

### Which moments make a sound

6. **Sound fires at exactly these five moments**, each reading its own theme slot:

   | Moment | `SoundMoment` | Theme slot | Call-site owner |
   |---|---|---|---|
   | Placing a mark | `placeMark` | `sound.placeMark` | `P3-02` req 15 |
   | Winning a small board / claiming a quadrant | `claimQuadrant` | `sound.claimQuadrant` | `P3-02` — assigned, req not yet written |
   | Cat game | `catGame` | `sound.catGame` | `P3-02` — assigned, req not yet written |
   | Winning the whole game | `winGame` | `sound.winGame` | `P3-04` req 16 |
   | Button taps / menu navigation | `buttonTap` | `sound.buttonTap` | four owned, two unassigned — below |

   **`claimQuadrant` and `catGame` belong to the commit path.** Both are consequences of a
   *committed move*, not rendering events: `P3-02-move-input.md` already fires `placeMark`
   there and owns the commit, while `P3-01-board-rendering.md` draws the claim veil and the
   cat caption without knowing when a move lands. Like `placeMark`, both fire on the
   **confirm** tap and never on the preview (Requirement 8).
   ⚠ **Assigned but not yet written.** `P3-02`'s req 15 verification still says *"whether the
   same commit also produces `claimQuadrant`, `catGame` or `winGame` is not this PRD's"*, and
   its Out of Scope still routes those three here. Until that flips the two documents point at
   each other, so this PRD names the owner and no requirement number.

   **`buttonTap` is one moment and one sound file, not a family.** *"**Yes — one tap sound,
   everywhere.** Every button, row and toggle plays the same short tap sound: menu buttons,
   theme rows, settings toggles, the game-over card's two controls, the trash button and the
   modal's Yes and No."* There is no per-control variation and no second slot — a distinction
   the schema could not express anyway, since `P1-03` req 15 gives `sound` exactly one
   `buttonTap` key.
   *(`Theming.md` → Decisions → **Do non-board controls make a sound?**, which grounds itself
   in the same symmetry as the haptic ruling — `Game Board Design.md` → Decisions → *Does the
   haptic fire on non-board controls?* That Decision also states it **does not change the
   board sound moments** and that **an invalid tap stays silent in both channels**, which is
   Requirement 9 from the doc's side.)*

   **The six `buttonTap` sites, four owned and two not:**

   | Site | Owner |
   |---|---|
   | The four menu buttons | **`P4-01` req 24** — fires one haptic *and* one sound |
   | Theme rows, close, failure-modal dismiss | **`P4-03` req 25** — its req 18 is the haptic half |
   | Four toggles, exit, dismiss | **`P4-04` req 25** |
   | The in-game settings gear | **`P3-03` req 12** — that PRD records req 12 as the site of record, req 22 as the detail |
   | The open-games list — rows, New Game, trash, Yes/No, Cancel, back | **none.** `P4-02` req 30 fires the haptic on eight sites and names no sound |
   | The game-over card's two controls | **none, and circular.** `P3-04` req 16 says *"Whether the two card controls fire `buttonTap` is `P2-02`'s to say, not this PRD's"* — while this PRD holds that a call site is the caller's. Someone must break the tie |

   *Wave note, following `P2-03` req 1's:* assertable **here** as *one `play(...)` produces at
   most one sink call, never two* (Requirement 16 names the seam). That a given event reaches
   `play` exactly once is a **call-site fact, owned by each calling PRD** — which is why the
   four owners above each carry their own exactly-once assertion, and why the two unowned rows
   cannot be closed by writing anything in this file. **Stated because the equivalent note in
   `P2-03` is what told `P4-03` its assertion was its own to write**, and that PRD added
   req 25 in response.

   *(`Theming.md` → What a Theme Controls → Audio, which lists these five plus background
   music; slot names and shapes from `P1-03` req 15 → `sound`.)*
   *Testable (wave 2):* with a fixture theme and a `RecordingOneShotSink`, each moment records
   exactly one call naming its own enum value and that slot's path, and no other slot is read;
   every `buttonTap` call resolves the same path regardless of which control triggered it.

7. **`sound` has seven keys; this layer plays five.** `neon.theme.json` → `sound` also
   carries `music` and `signature`. **`music` is not played by this layer** — Requirement 14.
   **`signature` is descriptive metadata, not an asset** — its value is the word `"buzz"`,
   naming the theme's sonic character. The layer never plays either, and must not be
   implemented by iterating `sound.*`; `SoundMoment` having no value for either is the
   structural guarantee.
   *(`Theming.md` → Theme Catalog → Theme 1 — Neon → Signature sound; `P1-03` req 17, which
   states the same rule from the schema side — *"A consumer must not treat `sound.*` as an
   iterable list of playable assets"* — and cites this PRD's reqs 6 and 7.)*
   *Testable (wave 2):* no sink call ever carries `signature`'s or `music`'s value, including
   on a fixture theme whose `music` slot is populated.

8. **The pending selection gets no sound of its own.** Sound belongs to the **confirmed**
   move — `placeMark` fires on the second (confirm) tap only, and so do `claimQuadrant` and
   `catGame` when that commit produces them (Requirement 6).
   *(`Game Board Design.md` → Move Input → Sound; → Changing your mind;
   `design_handoff_game_ui/README.md` → *2d*: *"No sound fires on selection (docs)."*)*
   *Testable (wave 3 — needs a board):* `P3-02-move-input.md` req 15 publishes the assertion
   from the call-site side and cites this requirement by number.

9. **An illegal tap makes no sound.** A tap outside the legal quadrant *"does nothing"* —
   no shake, no flash, no error message, and no audio.
   *(`Game Board Design.md` → Active Quadrant Highlight → Taps outside the legal quadrant;
   restated app-wide by `Theming.md` → Decisions → Do non-board controls make a sound?, which
   closes with *"an invalid tap stays silent in both channels."*)*
   *Testable (wave 3 — there is no tap to make in wave 2):* covered by `P3-02` req 15's
   verification, with `FakeAudioLayer` installed.

10. **The haptic and the sound are independent channels.** The haptic fires on *every valid
    click* including the first tap of a two-tap move, which Requirement 8 makes silent — so on
    the board the two channels deliberately diverge, while on controls they agree
    (Requirement 6).
    *(`Game Board Design.md` → Haptic Rule vs. → Move Input → Sound.)*
    *Testable (wave 3 — needs a board and both layers):* a legal first tap records one
    `validAction()` against `FakeHapticService` and zero moments against `FakeAudioLayer`.

### Theme sound sets, fallback, and null

11. **Sound resolution happens in the merge, not in this layer — but null is a legitimate
    value the layer must handle.** Anything a theme does not define comes from Neon, and
    because each theme is materialized at startup, this layer performs **no fallback at play
    time** and contains no Neon-substitution logic.

    **A materialized slot can still be null, and that is not an error.** `P1-03` req 8 makes
    null an *explicit clear*, and its own testable states `sound.buttonTap: null` "yields no
    button-tap sound". **A null slot means that moment is silent:** the layer plays nothing,
    treats it as normal operation, logs nothing, and reports nothing. Silence-by-configuration
    is distinct from an unloadable value (Requirement 21). See Requirement 5's assumption
    fence on the Dart nullability this depends on.
    *(`Theming.md` → Sound Decisions → Sound falls back to Neon; `Tech Design.md` →
    Decisions → Fallback to Neon — merge, not resolve; `P1-03` reqs 8, 15.)*
    *Testable (wave 2):* the layer contains no reference to Neon and no per-lookup fallback; a
    fixture theme whose `sound.buttonTap` is null produces zero sink calls on a button tap and
    zero log lines, while its other four moments reach the sink.

12. **Neon is the theme every sound ultimately comes from, and its signature is a buzz.**
    *(`Theming.md` → Theme Catalog → Theme 1 — Neon → Signature sound)*
    *Owner of the behavior:* `P1-03` reqs 11–13. **This PRD authors no theme content and must
    not edit `assets/themes/`.**

13. **Classic Red vs Blue's signature sound is a splat.** It inherits every sound it does not
    override.
    *(`Theming.md` → Theme Catalog → Theme 2 — Classic Red vs Blue → Sound)*
    *Owner of the behavior:* `P5-01-classic-theme.md`. **Not assertable in wave 2.**

### One-shots here; music elsewhere

14. **This layer plays one-shots. Music is not a `SoundMoment` and never will be.**
    `Theming.md` → Decisions → *Do all four toggles ship, and is music a theme concern?*
    settles that **all four toggles ship and a theme supplies its own music**, reversing
    *One-shot sound effects only, for now*, which that doc now marks superseded and keeps as
    history.

    **What changes: nothing in this layer.** What changes is why. It is no longer *"no music
    in this version"* — it is that **`void play(SoundMoment)` cannot model music**, and that
    is a fact about the interface rather than a gap in it. A one-shot fires and ends; music
    has a lifecycle — it loops, it ducks under an effect, it pauses when the app backgrounds
    and resumes when it returns, and it persists across screens rather than belonging to a
    moment. Every one of those needs state and a second verb, and Requirement 2 deliberately
    has neither. Adding a `SoundMoment.music` would produce a value that plays once and stops,
    which is not what a theme's music means. **`P1-03` req 17 states the same conclusion from
    the schema side** — *"Music is not a one-shot … so whatever shape wins, it is never
    another `SoundMoment`."*

    So: **`SoundMoment` gains no music value, `sound.music` is never read here, and the layer
    never starts a looping or continuous track**, whatever a theme's `music` slot holds.
    *Testable (wave 2):* `SoundMoment` has exactly the five values of Requirement 6;
    `OneShotSink` has no looping entry point; `AudioPlayersPlayer` sets `ReleaseMode.stop`,
    never `.loop`; a fixture theme whose `music` slot names an asset produces no sink call.

15. **— not a requirement; a boundary note.**

    **On the number.** Earlier drafts retained it "so existing citations resolve," citing
    `P1-03` req 17 as naming "reqs 6, 7, 14 and 15". **That citation was wrong**: `P1-03`
    req 17 cites *"`P2-02` reqs 6, 7"* and nothing else. **No sibling PRD cites req 15
    today.** The number is retained anyway, for a real reason rather than a false one:
    renumbering would shift 16–26, and reqs 16, 17, 18, 19, 21, 22 and 25 *are* cited by
    `P3-02`, `P3-03`, `P4-01`, `P4-03`, `P4-04`, `P3-04` and `P5-02`.

    **The music layer is a sibling of this one, not an extension of it, and it does not exist
    yet.** The fourth toggle ships in wave 4 (`P4-04-settings.md`) while the thing it switches
    does not — `P1-03` req 17 records that `sound.music` stays `deferred` precisely because
    there is a confirmed consumer of the **setting** and none of the **asset**, with its
    **Blocking item 1** holding the key's shape open between two incompatible candidates.

    Whoever builds that layer inherits three things from this one and none of its interface:
    the theme-driven rule (Requirement 3), the settings-gate shape (Requirement 16, against
    the music toggle rather than the sound toggle), and `AudioSession` (Requirement 26) —
    which is process-wide, so a music layer configures nothing of its own and the two must
    agree. **This PRD claims no ownership of music and specifies none of it.**

### The global mute

16. **A global sound-effects toggle silences all of it, from the next sound onward.** The
    toggle is a **player setting, not a theme property** — it mutes any theme and a theme
    cannot override it; **global for the whole game**; **remembered between sessions**. With
    it off, no sound plays at any of the five moments, under any theme. It changes nothing
    else: not the active theme, not haptics, not animations, **and not music** — the Music
    toggle is a fourth, separate setting (`P4-04-settings.md`) over a layer this PRD does not
    own.

    **The gate lives inside `play`** (Requirement 2), evaluated as `soundEffects()` — i.e.
    `ref.read(soundEffectsEnabledProvider)` — on every call, never captured at app start,
    game start, or construction. Call sites invoke `play` unconditionally and never consult
    the setting. **A mid-game change governs the next sound**, because the toggle is offered
    inside in-game quick actions.
    *(`Theming.md` → Sound Decisions → Global mute; `Menus and UI.md` → Decisions → Should
    there be a mute button, and where does it live?; → How you reach settings from gameplay →
    Quick actions contents, which lists **"The sound effects and vibrate toggles"** — the same
    sentence `P2-03-haptics.md` req 12 reads to settle the mid-game case for the vibrate half.
    Same sentence, same ruling.)*

    *Testable (wave 2) — and note what this must NOT assert.* The assertion counts **sink
    calls on the real layer**, following `P2-03` req 13's shape. Construct `ThemedAudioLayer`
    with **all three** constructor arguments:
    - `sink:` a `RecordingOneShotSink`;
    - `soundEffects:` a source returning the branch under test;
    - `activeTheme:` **a fixture theme whose `sound.placeMark` begins with `assets/`** — the
      canonical fixture is `assets/audio/fixture.mp3`. **This argument is load-bearing.**
      Supplying Neon's real theme yields `"TODO"`, which Requirement 21(a) pre-rejects, so the
      sink records zero in *both* branches and the "records one" half fails a correct
      implementation — via the path check rather than the gate.

    With the source `true` the sink records one call; with it `false`, zero — in both cases
    the caller invoked `play` unconditionally. Flipping the source between calls, the next
    call obeys the new value with no reconstruction.
    > ⚠ **Do not assert this through `FakeAudioLayer`.** Installing a fake via
    > `audioLayerProvider.overrideWithValue` **replaces the gate**, so with the setting off
    > the fake still records all five moments — callers call `play` unconditionally by
    > design. A test asserting "zero recorded with sound off" through the fake would fail a
    > *correct* implementation, and the likely repair is someone moving the gate out to the
    > call sites, which breaks Requirement 2. `P3-04` req 16 and `P4-01` req 24 both carry the
    > mirror image of this warning for the other direction.

    *Ownership:* the stored value and its resolved provider are `P1-04`'s; the switch is
    `P4-04`'s. **What "off" means is this PRD's.**

### Working against the theme content that exists

17. **The layer ships complete and tested with no audio assets in the repository.** Neon's
    five playable slots hold prose placeholders today — `"TODO: neon buzz one-shot"` and four
    bare `"TODO"` — **named but unloadable, never absent**, and `assets/audio/` holds only a
    `.gitkeep` until `P5-02` lands the first file. Nothing in this PRD's own test suite
    requires a real asset: every wave-2 assertion runs against fixture paths, the doubles of
    Requirement 22, or the `"TODO"` values themselves.
    *(`neon.theme.json` → `sound`; `design_handoff_game_ui/README.md` → Assets → Sounds;
    `Tech Design.md` → Decisions → Where do sound and art assets come from?; `P1-03`
    Blocking item 2, *"What goes in Neon's five `TODO` sound values."*
    `P5-02-asset-generation-replicate.md` cites reqs 17–19 as *"playback, complete and
    testable before any asset exists."*)*
    *Testable (wave 2):* with `assets/audio/` containing no audio file and Neon's five slots
    holding `"TODO"`, this layer's entire test suite passes; a scan of `test/audio/` finds no
    test that reads a file from `assets/audio/`.
    *Deliberately not asserted here:* that *the game* stays playable and every non-audio
    behavior is unchanged. That is an app-level property, not observable from this layer, and
    it belongs to whichever wave first has a game to play.

18. **Sound assets, once produced, are stored in `assets/audio/`** — created by `P1-01` req 3,
    written by `P5-02` req 3, named by its req 7, and declared in `pubspec.yaml` by its req 9
    in the same change that lands the first file. **That ownership is agreed on both sides:**
    `P1-01` req 3 assigns the declaration to `P5-02` and cites this requirement by name as
    concurring.
    *(`Tech Design.md` → Decisions → Project structure — layer-first.)*

19. **Dropping the real files in changes no code *in `lib/`*.** Making a moment audible is a
    change to the theme definitions and the asset bundle — never to this layer.
    *(Follows from Requirements 3, 4 and 11 — `Theming.md` → Architectural Rule.)*
    *Testable (wave 5 — needs a produced asset):* replacing a slot's `"TODO"` with the real
    path makes that moment audible with **no diff under `lib/`**. Not "no diff outside
    `assets/`": `P5-02` req 9 adds the `assets/audio/` declaration to `pubspec.yaml` in that
    same change, because Flutter fails the build on a declared-but-empty asset directory.

### Failure, absence, first launch, lifecycle

20. **Requesting a moment is fire-and-forget, and nothing on the path awaits.** `play` returns
    immediately and the caller never learns whether a sound played, was gated off, was silent
    because the slot is null, or failed to load.

    **The claim that carries this is structural and specific: `AudioPlayersPlayer.start` and
    `.stopNow` contain no `await` and are not `async`.** That is the one form which catches
    the defect worth catching — awaiting `stop()` before `play()`, which delays the audible
    start by a platform round trip. Weaker forms do not: "`play` is `void`" is enforced by the
    compiler, "`ThemedAudioLayer` has no `async`" constrains a class that was never at risk,
    and a "sink that blocks" test cannot be written at all, since `playOneShot` returns `void`
    and no caller holds a future.
    *(Taking the default `P2-04-animations.md` req 6 fenced for the motion channel, and
    matching `P2-03` req 13. The doc warrant — `Animations.md` → Decisions → Animations don't
    block input — is stated about animations, so this is **a sibling's default adopted
    deliberately**, not a doc ruling about sound.)*
    *Testable (wave 2):* a source scan of `AudioPlayersPlayer` finds no `await` and no
    `async`; every plugin future in it is wrapped per Requirement 25's catch form.
    *Testable (wave 3):* no call site branches on `play`'s result.

21. **A named sound that will not load never reaches the player, and the log is bounded.**

    **(a) Wrong shape — synchronous, deterministic, and the path wave 2 exercises.** A slot
    value that does not begin with `assets/` is rejected **before the sink is called**:
    nothing plays, nothing throws, and **exactly one** `debugPrint` line is emitted per slot
    per app run, the slot added to `_loggedBadPaths` before returning. Handing
    `AssetSource('TODO')` to the plugin and logging on the async failure instead would make
    the count non-deterministic — a second `placeMark` can fire before the first failure lands
    and sets the memo. All five of Neon's `"TODO"` values fail this check.

    **Logging call: `debugPrint`** — named because it decides whether (a)'s count is
    capturable at all; a test can override `debugPrint` and collect lines, while
    `dart:developer.log` cannot be intercepted the same way.
    *Testable (wave 2):* with a fixture theme carrying Neon's five `"TODO"` values, playing
    all five moments twice produces no exception, zero `RecordingOneShotSink` calls, and
    exactly five captured `debugPrint` lines.

    **(b) Right shape, absent file — caught and swallowed, and it has NO wave-2 assertion.**
    A path beginning `assets/` that names no bundled file cannot be detected synchronously.
    Requirement 25's catch form swallows it, nothing surfaces to the player, and no line-count
    guarantee is claimed.

    **Why there is no test, stated rather than implied.** An earlier revision proposed
    asserting "no unhandled async error" via a `PlatformDispatcher.instance.onError` probe.
    **That probe cannot fire under `flutter_test`:** the framework runs the test body inside a
    guarded zone, and `PlatformDispatcher.instance.onError` is reached only by errors escaping
    to the *root* zone — so it records nothing whether the catch form is present or absent,
    and passes identically either way. The obvious substitute is no better: a missing asset
    fails inside `rootBundle.load`, not on the plugin's method channel, so mocking
    **`xyz.luan/audioplayers`** with `TestDefaultBinaryMessenger.setMockMethodCallHandler` —
    the shape `P2-03` req 15 uses for its own channel — reproduces a `MissingPluginException`,
    which is case (a)-adjacent, not case (b). A real assertion needs a test asset bundle that
    resolves some keys and rejects others, which is a harness this PRD is not going to specify
    blind. **Recorded as an untested path**, which is honest and cheap, rather than as a test
    that passes vacuously.

22. **The test doubles are published here, and these are they.** `P3-02` req 15, `P3-04`
    reqs 16–17, `P4-01` req 24, `P4-03` req 25, `P4-04` req 25 and `P3-03` req 12 all code
    against `FakeAudioLayer`; Requirements 5, 6, 11, 16 and 21(a) code against
    `RecordingOneShotSink`; Requirements 23, 25 and 26 code against the player and session
    doubles.

    ```dart
    // test/support/fake_audio_layer.dart          (shipped by THIS PRD, wave 2)
    final class FakeAudioLayer implements AudioLayer {
      final List<SoundMoment> played = <SoundMoment>[];
      @override
      void play(SoundMoment moment) => played.add(moment);
      void clear() => played.clear();
    }

    // test/support/recording_one_shot_sink.dart   (shipped by THIS PRD, wave 2)
    final class RecordingOneShotSink implements OneShotSink {
      final List<({SoundMoment moment, String path})> calls = [];
      int disposeAllCount = 0;
      @override
      void playOneShot(SoundMoment moment, String assetRelativePath) =>
          calls.add((moment: moment, path: assetRelativePath));
      @override
      void disposeAll() => disposeAllCount++;
    }

    // test/support/fake_one_shot_player.dart      (shipped by THIS PRD, wave 2)
    /// Records the order of start/stop so Requirement 25's restart-on-re-fire
    /// is observable, and whether it was disposed, for Requirement 23.
    final class FakeOneShotPlayer implements OneShotPlayer {
      final List<String> events = <String>[];   // 'start:<path>' | 'stop'
      bool disposed = false;
      @override
      void start(String assetRelativePath) => events.add('start:$assetRelativePath');
      @override
      void stopNow() => events.add('stop');
      @override
      void dispose() => disposed = true;
    }

    // test/support/recording_audio_session.dart   (shipped by THIS PRD, wave 2)
    final class RecordingAudioSession implements AudioSession {
      int configureCount = 0;
      @override
      void configure() => configureCount++;
    }
    ```

    Plus **`FakePreferencesRepository`** — an empty in-memory `PreferencesRepository` whose
    **four** preference reads complete with `null` (Requirement 5, which also records why
    `P2-03`'s private stub cannot be reused). All lists are **ordered**: `P3-02` asserts a
    sequence and Requirement 25 asserts stop-before-start.

    **Which double answers which question**, because picking wrong asserts the wrong layer:
    `FakeAudioLayer` sees *which moments the call site requested* — this is the one every
    call-site PRD in Requirement 6 wants, board and controls alike; `RecordingOneShotSink`
    sees *what survived the gate and the path check*; `FakeOneShotPlayer` sees *what the sink
    did to a player*. `P3-04` req 16 and `P4-01` req 24 both carry this distinction from their
    side and name `FakeAudioLayer` explicitly.
    ⚠ Under `overrideWithValue` a provider's own body does not run — see Requirement 23.

    **On a fresh install the game makes noise, and this layer does not decide that.**
    *Owner:* `Menus and UI.md` → Decisions → **What are the settings on a fresh install?**,
    with the mechanism in `P1-04` req 26, whose `Settings.defaults` turns **all four** toggles
    on. **This layer never observes null and holds no default of its own.**
    *Testable (wave 2):* `lib/audio/` contains no default, no `?? true` and no null check on
    the setting; with an empty preference store a qualifying moment reaches the sink.

23. **Native handles are released, and the release is observable.** `AudioPlayersSink` owns
    the players, so `oneShotSinkProvider` registers `ref.onDispose(sink.disposeAll)`
    (Requirement 5). `disposeAll()` is the single release point and is idempotent.

    **Why the obvious test does not work.** `Provider.overrideWithValue` is backed by a
    `ValueProvider`: the original `create` body never runs, so `ref.onDispose` is never
    registered, and a test that overrides `oneShotSinkProvider` with a `RecordingOneShotSink`
    and disposes the container sees `disposeAllCount == 0` — not 1.
    **`audioPlayerFactoryProvider` exists to solve exactly this:** override the *factory*, and
    the production body still runs.
    *(**This PRD's call.** No doc addresses lifecycle. A widget-test suite that builds a
    container per test would otherwise leak five handles per test.)*
    *Testable (wave 2):* in a `ProviderContainer` with `audioPlayerFactoryProvider` overridden
    by a factory returning `FakeOneShotPlayer`s, resolve `audioLayerProvider`, then
    `container.dispose()` — every player the factory produced has `disposed == true`.
    Separately, calling `disposeAll()` twice leaves each player disposed once.

24. **— not a requirement; a design note.** No sibling cites this number; it is retained
    because renumbering would shift 25 and 26, which `P3-04`, `P4-03` and `P4-04` do cite.

    *Player-instance strategy, pending OQ-1:* **one player per `SoundMoment`, five in total**
    (Requirement 25). Different moments co-occurring overlap; the same moment re-firing
    restarts rather than layers; in-flight sounds are never cut short by muting, because
    neither `AudioLayer` nor `OneShotSink` has a `stop`.

    **Demoted because it has no assertion it uniquely owns.** Its former testable's three
    clauses were Requirement 16 restated, Requirement 6 entailed, and "two calls produce two
    records" — **no implementation that passes Requirement 6 can fail them.** The property it
    existed to fence is co-occurrence, and `ThemedAudioLayer` has no concept of it: the call
    site makes three independent `play` calls and the layer cannot tell them from three
    unrelated ones. What is real and assertable lives one layer down, in Requirement 25's
    same-instance restart test. **Reversibility is unchanged:** all three behaviors live inside
    `AudioPlayersSink`.

    *Worth noting for `buttonTap` specifically:* one player for every control in the app means
    two taps in quick succession on different buttons restart the same player rather than
    overlapping. That follows from Requirement 6's one-sound rule and is almost certainly
    right for a tap sound — but it is a consequence of the strategy above, not an independent
    decision, and it moves if OQ-1 does.

25. **`AudioPlayersSink`, `AudioPlayersPlayer`, `GlobalAudioSession` — the classes that
    actually make noise, and how to watch them.**

    ```dart
    // lib/audio/audio_players_sink.dart
    final class AudioPlayersPlayer implements OneShotPlayer { /* wraps AudioPlayer */ }
    final class GlobalAudioSession implements AudioSession { /* Requirement 26 */ }

    final class AudioPlayersSink implements OneShotSink {
      AudioPlayersSink({
        required OneShotPlayerFactory createPlayer,
        required AudioSession session,
      });

      @visibleForTesting
      Map<SoundMoment, OneShotPlayer> get players;
    }
    ```

    - **`AudioPlayersPlayer` is the only class that touches `audioplayers`.** Everything above
      it speaks `OneShotPlayer`, which is what makes Requirements 20, 23 and this one
      assertable without the plugin.
    - **`GlobalAudioSession` wraps the static.** `AudioPlayer.global.setAudioContext` is a
      static call and a static cannot be intercepted, so Requirement 26's "configured exactly
      once" would have had no observation point. The interface is the observation point.
    - **Five players, created eagerly** in the constructor, one per `SoundMoment`, and
      `session.configure()` called **once** there — not per player. Eager creation keeps
      `disposeAll`'s count deterministic and keeps first-fire allocation off the tap path.
    - **`playOneShot(moment, path)` calls `stopNow()` then `start(path)` on that moment's
      player.** The stop lives **here**, not in `ThemedAudioLayer`; nothing above the sink has
      a `stop` to call.
    - **The catch form is `unawaited(f.catchError(…, test: …))`, per plugin future**, inside
      `AudioPlayersPlayer`:

      ```dart
      unawaited(_player.play(AssetSource(path)).catchError(
        (Object _) {},
        test: (Object e) =>
            e is PlatformException || e is MissingPluginException || e is FlutterError,
      ));
      ```

      **A bare `catchError` is wrong**, and an earlier revision of this PRD used one while
      claiming `P2-03` req 14's authority — that PRD in fact ships a `test:` predicate and
      states why: a bare catch *"swallows everything, permanently — including a `TypeError`
      introduced by a later change, which is exactly the bug worth reporting."* The three
      types here are the channel failures plus **`FlutterError`, which is what
      `rootBundle.load` throws for a missing asset** — Requirement 21(b)'s case. A programming
      error still reaches `P1-06` req 2's handler, by design. **`try/catch` around the call
      does nothing**: these futures fail asynchronously, so a synchronous block sees nothing
      and the rejection escapes to the root zone as a shipped crash report.
      **`unawaited` is documentation, not lint compliance** — `P1-01` req 15 sets the analyzer
      floor at `package:flutter_lints/flutter.yaml`, which does not enable `unawaited_futures`.
      `P2-03` req 14 records making and correcting exactly this claim.
    - **What "never throws" covers**, restored from `P2-03`'s carve-out: the three types above,
      from the plugin call, and nothing else. It does **not** cover `soundEffects()` or
      `activeTheme()` in `ThemedAudioLayer.play` — those run outside any guard, and a closure
      reading a disposed `ProviderContainer` throws synchronously. That is ordinary Riverpod
      lifetime, and it is deliberately not caught: swallowing it would hide a wiring bug
      behind a silent no-op.
    - **`ReleaseMode.stop`, never `.loop`** (Requirement 14). **`disposeAll()`** disposes all
      five and is idempotent.

    *(**This PRD's call.** No doc addresses any of it.)*
    *Testable (wave 2, with `FakeOneShotPlayer` and `RecordingAudioSession`):* re-firing one
    moment yields `events == ['start:p', 'stop', 'start:p']` on the **same** instance; two
    different moments touch two different instances; constructing the sink leaves
    `configureCount == 1`; `disposeAll` twice leaves each player disposed once. Separately,
    against `AudioPlayersPlayer` with the plugin channel mocked at **`xyz.luan/audioplayers`**
    via `TestDefaultBinaryMessenger.setMockMethodCallHandler`, a rejected future produces no
    unhandled error and `start` contains no `await`.

26. **The iOS audio session is `ambient` + `mixWithOthers` — a stated default, reversible,
    pending OQ-4.** Two consequences, both player-visible, both deliberate:
    - **A silenced phone silences the game**, regardless of Requirement 16's toggle. The
      ringer switch wins. This is **not a defect in Requirement 16 and must not be "fixed" as
      one** — it is the conventional behavior for a casual game.
    - **The player's own music keeps playing.** The app never interrupts or ducks another
      app's audio. Note this now also constrains the future music layer (Requirement 15):
      the session is process-wide, so both must agree.

    *(**This PRD's call.** `audioplayers` requires an explicit `AudioContext` on iOS, the
    primary target (`Tech Design.md` → Decisions → Primary target — Apple), and **the plugin's
    own default is not neutral** — leaving it unset ships a policy nobody chose. The
    alternative, `playback`, sounds over a silenced phone and interrupts the player's music.
    **Reversibility:** one constant inside `GlobalAudioSession`.)*
    *Testable (wave 2):* the `AudioContext` value appears exactly once in `lib/`, inside
    `GlobalAudioSession`; `RecordingAudioSession.configureCount == 1` per sink construction.
    **The audible behavior is device-only and no automated test asserts it** — flagged rather
    than papered over.

## Out of Scope

- **Who calls play.** This PRD owns *what plays and under what rules*, not the call sites.
  Detection is not the gap — the engine detects a claim, a cat game and a win
  (`P1-02-engine-rules.md`). The gap is which PRD's requirement *invokes this layer*, and
  **three sites are still open**:

  | Moment / site | Call-site owner |
  |---|---|
  | `placeMark` | **Owned** — `P3-02` req 15 |
  | `claimQuadrant`, `catGame` | **Assigned to `P3-02`** — fires on the commit; requirement not yet written there |
  | `winGame` | **Owned** — `P3-04` req 16 |
  | `buttonTap` — menu, theme, settings, gear | **Owned** — `P4-01` req 24, `P4-03` req 25, `P4-04` req 25, `P3-03` req 12 |
  | `buttonTap` — open-games list | **Unassigned** — `P4-02` req 30 fires the haptic on eight sites and names no sound |
  | `buttonTap` — game-over card controls | **Unassigned, and circular** — `P3-04` req 16 routes the question here; this PRD holds that a call site belongs to its caller |

  **A gap declared closed is worse than a gap declared open**, which is why the two `buttonTap`
  rows say *unassigned* rather than being folded into the four that are real. None of the three
  can be closed by writing anything in this file: a requirement here would specify another
  PRD's surface.
- **Music — the layer, the key shape, the assets, and the fourth toggle's behavior.**
  Requirements 14 and 15 state only that this layer does not play it and cannot model it.
  Shape is `P1-03` Blocking item 1; the toggle is `P4-04-settings.md`; provenance is `P5-02`.
- **The theme mechanism, the sound slots' definition, and the theme accessor** — `P1-03`
  reqs 15, 17, 24, including the Dart nullability Requirement 5 fences.
- **The settings surface** — `P4-04-settings.md`.
- **Persisting the toggles and their first-launch defaults** — `P1-04` reqs 26–27.
- **Generating the sound files, naming them, and declaring the asset directory** — `P5-02`
  reqs 3, 7, 8, 9; the declaration assignment is agreed with `P1-01` req 3 (Requirement 18).
- **The Classic Red vs Blue theme definition** — `P5-01-classic-theme.md`.
- **Crash reporting.** Requirement 25's catch form keeps this layer *out* of `P1-06`'s scope,
  which reports unhandled errors only; it adds no reporting of its own.
- **Haptics** — `P2-03-haptics.md`. **Animations** — `P2-04-animations.md`; Requirement 20
  adopts its fire-and-forget contract and nothing else, and its one-at-a-time rule is **not**
  carried across (see OQ-1).
- **The `lib/` tree** — `P1-01` req 2 owns it and already carries `audio/`.

## Open Questions

### Closed since the last round

**`claimQuadrant` and `catGame` are assigned to `P3-02-move-input.md`** — both are consequences
of a committed move rather than rendering events, so they belong with the commit path that
already fires `placeMark`. Requirement 6 and Out of Scope record the owner; neither cites a
requirement number, because `P3-02` has not written one yet.

**Four of the six `buttonTap` sites are owned** — `P4-01` req 24, `P4-03` req 25, `P4-04`
req 25 and `P3-03` req 12, each carrying its own exactly-once assertion. `P4-03` added req 25
in direct response to Requirement 6's wave note, which is the note working as intended.

**Earlier rounds:** `P1-01` req 2 now creates `lib/audio/` and names this PRD as its owner;
`Theming.md` → Decisions → *Do non-board controls make a sound?* closed OQ-3 and the
haptic/sound asymmetry with it; the four-vs-three toggle contradiction was superseded by the
music Decision; Requirements 15 and 24 were demoted; Requirement 21(b) was given an honest "no
wave-2 assertion"; the `OneShotPlayer` and `AudioSession` seams were added; the catch form
gained its `test:` narrowing.

### From the design docs, worded as the docs word them

- Which values, concretely, does Classic Red vs Blue override? *Owned by `P5-01`.*
- Whether music loops, whether it differs by screen, and where the audio comes from.
  *(`Theming.md` → Open Questions.)* **Not this PRD's** — routed to `P1-03` Blocking item 1.

### Needs the user — a coding agent cannot settle these

> **Numbering note for citers:** OQ-3 is **answered and kept as a closed stub**, following
> `P3-02`'s handling of its own OQ-8, because siblings cite these by number. `P5-02` cites
> this section's earlier numbering — its "OQ-5" (the draw) and "OQ-4" (`buttonTap`) are
> **OQ-2** and **OQ-3** here.

- **OQ-1 — Can two sounds overlap?** A single confirmed move can be `placeMark` **and**
  `claimQuadrant` **and** `winGame` at once. Play all simultaneously, play only the most
  significant, or queue them. **Requirement 24's note ships "play all" as the default** so
  nothing is decided by accident — the risk being that the player-instance choice answers it
  silently, one reused player shipping *"last sound wins"* with no decision recorded.
  **Now named from the call-site side too:** with `claimQuadrant` and `catGame` assigned to
  `P3-02`, that PRD is expected to state the case where one tap produces three sounds, so
  *three sounds on one tap* reads as designed rather than as a defect.
- **OQ-2 — What does a *tie* sound like?** `catGame` is the *small*-board case
  (`Game Overview.md` → Terminology); `Rules.md` → Edge Cases names the big-board case a
  **straight draw**, and no slot exists for it. **Downstream default already in place:**
  `P3-04` req 17 makes the draw silent this wave, reversible by adding a moment to
  Requirement 6's inventory. **Mirrored in that PRD's OQ-7 — answer it once, there.**
- **OQ-3 — CLOSED.** *Which controls count as buttons, and is `buttonTap` one sound or
  several?* Answered by `Theming.md` → Decisions → *Do non-board controls make a sound?*:
  **one tap sound, everywhere** — see Requirement 6. Kept as a stub for citers. Note this
  closed the *policy*; two of the six call sites are still unassigned, which is a coordination
  matter rather than an open question.
- **OQ-4 — Is `ambient` + `mixWithOthers` the policy?** **The only item genuinely with the
  user.** Requirement 26 ships it as the default, so this is a ruling on stated behavior
  rather than a gap. It commits to: a silenced phone silences the game regardless of the
  in-app toggle, and the player's music is never interrupted. `playback` inverts both. The
  plugin's default is not neutral, so it cannot be left unset — and the result is
  audible-only, so no automated test will catch a wrong choice before someone hears it.
  **Now also binds the future music layer**, which shares the process-wide session.
- **OQ-5 — Does muting stop a sound already in flight?** **Fenced structurally by
  Requirements 2, 5 and 25:** no `stop` exists above the sink, so in-flight one-shots finish
  and muting governs the next sound only. A one-shot is short enough that the difference may
  never be perceptible — but "mute" plausibly means "silence now," which would mean adding a
  verb to `AudioLayer` and reopening Requirement 2's single-method surface.
