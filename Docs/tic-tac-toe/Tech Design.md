# Tech Design

> **Status:** Brain dump / early tech decisions. Contradictions are expected and OK.
> Nothing here is settled except what's under **Decisions**.
>
> This doc covers *how we build it*. What we're building lives in
> [Game Overview](./Game%20Overview.md), [Rules](./Rules.md),
> [Game Board Design](./Game%20Board%20Design.md), [Menus and UI](./Menus%20and%20UI.md),
> [Theming](./Theming.md), and [Animations](./Animations.md).

## Decisions

### Framework — Flutter
**Flutter.** Already in use for the game.

The reason it fits: it compiles to **both Android and Apple** from one codebase, so we're
not writing the game twice.

### Primary target — Apple
**iOS is the primary target as of right now.** Android is supported by virtue of Flutter,
but Apple is what we're building and testing against first.

Practical meaning: when a platform question comes up, iOS wins. Android is a
build-target, not a design constraint.

### Language — Dart
Comes with Flutter.

---

## What the Design Docs Already Imply
Some technical requirements are already locked by decisions made elsewhere. Listing them
here so they don't get re-litigated:

| Requirement | Comes from |
|---|---|
| **Fully offline.** No backend, no network, no accounts. | Two players, one phone |
| **Local persistence** for 4 values: theme, sound, vibrate, animations | [Menus and UI](./Menus%20and%20UI.md) → Persistence |
| **No game-state persistence.** Games aren't saved. | Same |
| **Audio playback** for one-shot sound effects (no music yet) | [Theming](./Theming.md) |
| **Haptics** on every valid click | [Game Board Design](./Game%20Board%20Design.md) → Haptic Rule |
| **A theme system with fallback** — every visual/audio/motion value resolves through the active theme, falling back to Neon | [Theming](./Theming.md) |
| **Animations toggleable off entirely**, with instant state changes instead | [Animations](./Animations.md) |
| **Portrait phone layout**, whole 9x9 board visible, no zoom | [Game Board Design](./Game%20Board%20Design.md) |

### The theme system is the main architectural risk
> *"All of our code operates off of the theme. No code should be operating independently
> from the selected theme."*

This is the one constraint that touches every file, and it's the one that's expensive to
retrofit. Whatever we choose for state management and widget structure has to make
"every value comes from the theme" the *easy* path, not a discipline we have to maintain
by hand.

---

## Open Questions

These are the things I think we need to hammer out. Grouped roughly by how much they
block other work.

### 1. Theme system — how is a theme actually represented?
The design says Neon is a complete base and other themes are partial overrides that
inherit anything they don't define ([Theming](./Theming.md)). Concretely:

- Is a theme a **Dart class/object** compiled into the app, or **data** (JSON/YAML)
  loaded at runtime? (Themes are "contained within the codebase" for now either way.)
  Answer: Json or Yaml would be a good universal theam like object that can be loaded in.
- How does fallback-to-Neon work — a resolver that checks the active theme then Neon,
  or does each theme get *materialized* into a complete theme at startup by merging over
  Neon?
  Answer: Merge over neon
- Do we use Flutter's own `ThemeData`/`ThemeExtension`, or roll our own theme object?
  Flutter's system is built for exactly this and gives us `Theme.of(context)` everywhere,
  but it's designed around Material's vocabulary, not ours (quadrant highlights, mark
  art, sound sets, animation specs).
  Answer: User the TeameData/ThemeExtensions from flutter as possilbe filled out from our theam Json/Yaml file. The remaining parts not  suppoerted in the Flutter theme. Will need to be implamented on our own.
- Sounds and animations aren't things Flutter's theming handles at all. Do those live in
  the same theme object, or in a parallel structure? 
  Answer: All live in the same theme object And we give what we can to the flutter themeData and handel the rest our selves all from the same doc. 

### 2. State management
What holds game state and settings? Options in rough order of ceremony:
`setState`/`InheritedWidget` → `provider` → `riverpod` → `bloc`.

Relevant considerations for this specific app:
- Game state is small and entirely local. There's no async, no network, no server sync.
- Settings and theme need to be readable from **everywhere**, including deep in the board
  widget tree.
- Do you have a preference already, or a pattern you've used in your existing Flutter
  work on this?

### 3. Is the game logic separate from Flutter?
Proposal to confirm or reject: keep the rules engine (board state, legal moves, sending
rule, win/cat-game detection, free-choice state) as **pure Dart with zero Flutter
imports**, and let the UI layer read from it.

- Upside: the rules become unit-testable without a widget test, and the rules are the
  part where bugs actually hurt (sending rule, dead-quadrant free choice, big-board draw).
- Is that worth the structure, or do you want it simpler?

### 4. How is the board rendered?
- **Widgets** — 81 `GestureDetector`s in nested `GridView`/`Column`s. Simple, idiomatic,
  easy to animate individual cells.
- **CustomPainter / Canvas** — draw the board manually, hit-test taps ourselves. More
  control over the grid lines and highlight effects, more work.
- Neon's glow effects and the three simultaneous highlight treatments may push toward one
  or the other. Any instinct here?

### 5. Persistence package
Four small key-value preferences. `shared_preferences` is the obvious default. Any
reason to prefer something else (`hive`, `flutter_secure_storage`)? Nothing here is
sensitive.

### 6. Audio package
One-shot sound effects, with background music as a possible later addition.
`audioplayers` and `just_audio` are the usual choices. Preference?

Related: **do you have or plan to source the actual sound assets** (the Neon buzz, the
Classic splat)? That's a content dependency, not just a code one.

### 7. Assets and art
- Where does the **logo** come from ([Menus and UI](./Menus%20and%20UI.md) says the main
  menu needs one)?
- Marks: are X and O drawn in code (shapes/icons), or are they **image assets** per theme?
  This connects to the still-open "marks beyond X and O" question in
  [Theming](./Theming.md).
- Fonts — does a theme pick its own font? (Not currently stated anywhere.)

### 8. Orientation and device support
- **Portrait only**, or does landscape need to work? Portrait-locked is simpler and the
  board is square-ish, but two people sharing a phone on a table might turn it.
- Minimum iOS version?
- Do we care about iPad, or phone only? The docs say "phone" throughout.
Answer: Prtrait only, minimum IOS 13

### 9. Project structure
Rough folder layout — where do rules, theme definitions, widgets, and assets live? Worth
agreeing before there's much code, since the theme rule means theme access shows up
everywhere.

### 10. Testing
- Unit tests for the rules engine — worth it? (My read: yes, this is where the real
  complexity is.)
- Widget/golden tests for the board and its highlight states?
- Or keep it light and test by playing?

### 11. Build and distribution
- Is this going to the **App Store**, or is it a personal/TestFlight build?
- Bundle identifier / app name?
- Any CI, or local builds only?

### 12. Existing code
You said you've **already been using Flutter to write the game** — how far along is it,
and does any of it survive into this design? That changes whether this doc describes a
fresh build or a refactor toward these decisions.

<!-- The repo currently contains no application code — docs only. Worth confirming
     whether the existing Flutter work lives somewhere else. -->
