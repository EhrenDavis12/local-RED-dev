# Roadmap — Tic-Tac-Toe-Extreme

This is an index of where things live across the design docs, not a summary of what they
say. For the content itself, read the docs directly.

## Game Overview.md
What the game is, the pitch, and core concepts.

- ## The Pitch
- ## Core Concept
- ## Session Structure — Games and Continuing
- ## How a Move Is Made
- ## Player Experience
- ## Target Audience & Platform
- ## Inspirations / References
- ## Modes
- ## Terminology (working vocabulary)
- ## Decisions
  - ### Recursion depth
  - ### Scoreboard lifetime
  - ### Player names
  - ### Single-player / AI opponent
- ## Open Questions

## Rules.md
The game rules — setup, turn structure, placement, winning, and edge cases.

- ## Setup
- ## Turn Structure
- ## Placement Rules
  - ### Cell → Quadrant Mapping
- ## Winning a Sub-Board
- ## Winning the Game
- ## Edge Cases
  - ### Cat game (small board draw)
  - ### Sent to a dead quadrant → free choice
  - ### Big board full with no three-in-a-row → straight draw
- ## Turn Order Across Games
- ## Variants / Optional Rules
- ## Conflicting Ideas (unresolved)
- ## Decisions
  - ### Who goes first after a tie?
- ## Open Questions

## Game Board Design.md
How the board is structured and rendered — layout, highlights, input, and haptics.

- ## Board Structure
- ## Scoreboard
- ## Visual Layout
- ## Last Move Highlight
  - ### Why this matters more here than in normal tic-tac-toe
  - ### Lifetime
- ## Active Quadrant Highlight
  - ### The free-choice state
  - ### Taps outside the legal quadrant
- ## The Two Highlights Together
- ## Player Feedback / Affordances
- ## Move Input — Tap to Select, Tap Again to Confirm
  - ### Why this is more than a safety net
  - ### Changing your mind
  - ### Confirming
  - ### Sound
  - ### Three highlights on screen at once
- ## Pieces & Marks
- ## Everything Here Is Theme-Driven
- ## Animation & Juice
- ## Responsive / Screen Size
- ## Sketches & Notes
- ## Haptic Rule
- ## Open Questions

## Menus and UI.md
Menus, screens, settings, and persistence.

- ## Main Menu
- ## New Game → What It Starts
- ## Pass-and-Play Turn Handoff
- ## Screens (so far)
- ## Settings Menu
  - ### Vibrate on Touch
  - ### How you reach settings from gameplay
- ## Game Over → Rematch
- ## Persistence
  - ### Leaving a game mid-play
- ## Decisions
  - ### Should there be a mute button, and where does it live?
  - ### How do you get back to the main menu from a game?
  - ### What happens when a game ends?
  - ### Does the main menu need a title/logo?
  - ### Is theme selection its own screen or an overlay?
  - ### Does a game in progress persist?
  - ### What does a save slot hold?
  - ### Do we support Dynamic Type?
- ## Open Questions

## Theming.md
The theming system — architecture, inheritance from Neon, theme catalog, and sound.

- ## The Idea
- ## Architectural Rule (the important part)
- ## Where Themes Live
- ## Decisions
  - ### How many themes ship at launch
  - ### Where theme selection lives
  - ### Does the theme persist between sessions
  - ### Can you change the theme mid-game
  - ### Do themes affect sound
  - ### Are themes unlockable/rewards
  - ### Marks beyond X and O
  - ### What happens if a theme fails to load
  - ### Is anything distinguished by colour alone?
- ## What Is a Theme?
- ## Neon Is the Base Theme (inheritance model)
  - ### How it works
  - ### Why this matters for the build
  - ### Watch out for
- ## Theme Catalog
  - ### Theme 1 — Neon (base)
  - ### Theme 2 — Classic Red vs Blue
- ## What a Theme Controls
- ## Sound Decisions
  - ### Sound falls back to Neon
  - ### One-shot sound effects only, for now
  - ### Global mute
- ## Inheritance Depth
- ## What a Theme Does NOT Control
- ## Open Questions

## Animations.md
Animation vocabulary and how animations tie into the theme system.

- ## The Direction
- ## Scope For Now
- ## The Animation Vocabulary
  - ### Grow & Shrink (the core one)
  - ### Glow / Backlight
  - ### Shadowbox
  - ### Jiggle
  - ### Dance
- ## Animation Sets Are Part of the Theme
- ## Where Animations Fire
- ## Animations Inherit From Neon
- ## Decisions
  - ### Themes author their own animations — no shared library
  - ### Do themes inherit Neon's animations?
  - ### One animation at a time
  - ### Duration lives in the animation
  - ### Animations don't block input
  - ### Turn animations off — a global setting
  - ### Does iOS Reduce Motion drive the animations toggle?
  - ### Animations off = instant state change
- ## Open Questions

## Tech Design.md
How the game is built — framework, language, architecture, and open implementation
questions.

- ## Decisions
  - ### Framework — Flutter
  - ### Primary target — Apple
  - ### Language — Dart
  - ### How is a theme represented?
  - ### What format are theme files — JSON or YAML?
  - ### Theme identity — UUID
  - ### How does fallback-to-Neon work?
  - ### Do we use Flutter's ThemeData/ThemeExtension, or roll our own?
  - ### Do sounds and animations live in the same theme object?
  - ### Orientation
  - ### Minimum iOS version
  - ### Is the game logic separate from Flutter?
  - ### Persistence package
  - ### Game state storage — Hive
  - ### Serialization and the storage layer
  - ### Unit tests for the rules engine
  - ### Do themes pick their own font?
  - ### How is the board rendered?
  - ### Audio package
  - ### Marks — image or icon, supplied by the theme
  - ### Device support
  - ### Where do sound and art assets come from?
  - ### Do we add a test that fails on hardcoded theme values?
  - ### State management — Riverpod
  - ### Game state is immutable
  - ### Project structure — layer-first
  - ### Widget tests for the board — no golden tests
  - ### Fresh build, not a refactor
  - ### Distribution — public App Store release
  - ### Bundle identifier
  - ### CI — local builds only
  - ### Release tooling — fastlane
  - ### Crash reporting — catch and build the report, don't send it
- ## What the Design Docs Already Imply
  - ### The theme system is the main architectural risk
- ## Open Questions

## Alternative Game Styles.md
Parking lot doc — game-style variants and roads-not-taken, not the current design.

- ## Lock-In Style

---

This map is an index of where things live, not a summary of what they say. For the actual
content and current status of any decision, read the docs above directly.
