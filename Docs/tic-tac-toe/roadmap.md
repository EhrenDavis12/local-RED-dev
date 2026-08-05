# Roadmap — Tic-Tac-Toe-Extreme

An index of where things live across the design docs. Not a summary — for what a section
actually says, read the doc.

## [Design Handoff — UI](./design_handoff_game_ui/README.md)
**Not a design doc — an approved reference asset.** Repo-relative path:
`Docs/tic-tac-toe/design_handoff_game_ui/README.md`. High-fidelity UI for all 12 screens,
built from the docs below and approved. Read-only: nothing in this repo edits it.

**Bundle:**
- `README.md` — the handoff itself (tokens, board geometry, per-screen specs, state shape)
- `neon.theme.json` — the complete Neon theme, machine-readable
- `themes.catalog.json` — four themes plus ownership/paywall states
- `design-files/` — HTML/JSX prototypes; references, not production code

**Screens:**
- `1a` Main Menu · `1b` Select Game · `1c` About Us · `1d` Board, free choice
- `1e` Board, forced quadrant + last move · `1f` Modal, in-game settings
- `1g` Modal, winner · `1h` Modal, draw
- `2a` Theme Select (with paywall) · `2b` Settings page · `2c` New Game name prompt
- `2d` Board, pending move

**Sections worth deep-linking:** Design tokens · The board (the important part) ·
Quadrant states · Cell states · Interactions & behavior · State · Assets · Still to design

## [Game Overview](./Game%20Overview.md)
The pitch, core concept, and session structure for the game — what recursive tic-tac-toe is
and how a session of many games hangs together.

**Headings:**
- The Pitch
- Core Concept
- Session Structure — Games and Continuing
- How a Move Is Made
- Player Experience
- Target Audience & Platform
- Inspirations / References
- Modes
- Terminology (working vocabulary)
- Decisions
- Open Questions

**Decisions:**
- Recursion depth
- Scoreboard lifetime
- Player names
- Single-player / AI opponent

## [Menus and UI](./Menus%20and%20UI.md)
Menu structure, screen flow, theme selection, settings, persistence, and the game-over
rematch flow.

**Headings:**
- Main Menu
- Play Game → Where It Takes You
- A New Game → What It Starts
- Pass-and-Play Turn Handoff
- Screens (so far)
- Theme Selection
- Settings Menu
  - Vibrate on Touch
  - How you reach settings from gameplay
- Game Over → Rematch
- Persistence
  - Leaving a game mid-play
- Decisions
- Open Questions

**Decisions:**
- Should there be a mute button, and where does it live?
- How do you get back to the main menu from a game?
- What happens when a game ends?
- Does the main menu need a title/logo?
- Is theme selection its own screen or an overlay?
- Is the main menu button "New Game" or "Play Game"?
- Does a game in progress have to be saved to device storage?
- What does each row in the open-games list show?
- Does the opponent name replace "Player Two" in game?
- When does the scoreboard increment
- Which theme is active by default?
- How does theme selection show which theme is in use?
- What does an open game hold?
- How many open games do we keep?
- Deleting an open game
- Do we support Dynamic Type?

## [Rules](./Rules.md)
The rules of play — setup, turn structure, placement rules, winning conditions, and edge
cases.

**Headings:**
- Setup
- Turn Structure
- Placement Rules
  - Cell → Quadrant Mapping
- Winning a Sub-Board
- Winning the Game
- Edge Cases
  - Cat game (small board draw)
  - Sent to a dead quadrant → free choice
  - Big board full with no three-in-a-row → straight draw
- Turn Order Across Games
- Variants / Optional Rules
- Conflicting Ideas (unresolved)
- Decisions
- Open Questions

**Decisions:**
- Who goes first after a tie?

## [Game Board Design](./Game%20Board%20Design.md)
The visual and interaction design of the board itself — layout, highlights, move input, and
haptics.

**Headings:**
- Board Structure
- Scoreboard
  - Turn Indicator
- Visual Layout
- Last Move Highlight
  - Why this matters more here than in normal tic-tac-toe
  - Lifetime
- Active Quadrant Highlight
  - The free-choice state
  - Taps outside the legal quadrant
- The Two Highlights Together
- Player Feedback / Affordances
- Move Input — Tap to Select, Tap Again to Confirm
  - Why this is more than a safety net
  - Changing your mind
  - Confirming
  - Sound
  - Three highlights on screen at once
- Pieces & Marks
- Everything Here Is Theme-Driven
- Animation & Juice
- Responsive / Screen Size
- Sketches & Notes
- Haptic Rule
- Open Questions

**Decisions:** none yet — this doc has no Decisions section.

## [Theming](./Theming.md)
The theme system — what a theme is, how it inherits from Neon, and what it controls.

**Headings:**
- The Idea
- Architectural Rule (the important part)
- Where Themes Live
- Decisions
- What Is a Theme?
- Neon Is the Base Theme (inheritance model)
  - How it works
  - Why this matters for the build
  - Watch out for
- Theme Catalog
  - Theme 1 — Neon (base)
  - Theme 2 — Classic Red vs Blue
- What a Theme Controls
- Sound Decisions
  - Sound falls back to Neon
  - One-shot sound effects only, for now
  - Global mute
- Inheritance Depth
- What a Theme Does NOT Control
- Open Questions

**Decisions:**
- How many themes ship at launch
- Where theme selection lives
- Does the theme persist between sessions
- Can you change the theme mid-game
- Do themes affect sound
- Are themes unlockable/rewards
- Which themes are free
- Does a theme supply its own font
- Marks beyond X and O
- What happens if a theme fails to load
- Is anything distinguished by colour alone?

## [Animations](./Animations.md)
The animation vocabulary and how animations tie into the theme system.

**Headings:**
- The Direction
- Scope For Now
- The Animation Vocabulary
  - Grow & Shrink (the core one)
  - Glow / Backlight
  - Shadowbox
  - Jiggle
  - Dance
- Animation Sets Are Part of the Theme
- Where Animations Fire
- Animations Inherit From Neon
- Decisions
- Open Questions

**Decisions:**
- Themes author their own animations — no shared library
- Do themes inherit Neon's animations?
- One animation at a time
- Duration lives in the animation
- Animations don't block input
- Turn animations off — a global setting
- Does iOS Reduce Motion drive the animations toggle?
- Animations off = instant state change

## [Alternative Game Styles](./Alternative%20Game%20Styles.md)
Parking lot for variants and roads-not-taken — not the current game. See
[Rules](./Rules.md) for the actual rules.

**Headings:**
- Lock-In Style

**Decisions:** none — this is a parking-lot doc, not a Decisions/Open Questions doc.

## [Tech Design](./Tech%20Design.md)
How we build it — framework, language, storage, state management, project structure, and
release/distribution.

**Headings:**
- Decisions
- What the Design Docs Already Imply
  - The theme system is the main architectural risk
- Open Questions
  - 1. Persisted data — versioning
  - 2. Theme loading
  - 3. Build and distribution

**Decisions:**
- Framework — Flutter
- Primary target — Apple
- Language — Dart
- Theme representation — data, not code
- What format are theme files — JSON or YAML?
- Theme identity — UUID
- Fallback to Neon — merge, not resolve
- Flutter's ThemeData vs our own theme object
- Orientation — portrait only
- Minimum iOS version
- Is the game logic separate from Flutter?
- Persistence package
- Game state storage — Hive
- Serialization and the storage layer
- Unit tests for the rules engine
- Do themes pick their own font?
- How is the board rendered?
- Audio package
- Marks — image or icon, supplied by the theme
- Device support
- Where do sound and art assets come from?
- Do we add a test that fails on hardcoded theme values?
- State management — Riverpod
- Online multiplayer is an intended future direction
- Game state is immutable
- Project structure — layer-first
- Widget tests for the board — no golden tests
- Fresh build, not a refactor
- Distribution — public App Store release
- Bundle identifier
- CI — local builds only
- Release tooling — fastlane
- Crash reporting — catch and build the report, don't send it
- In-app purchases

---

This is an index of locations, not a summary of content. For what any of this actually
says, read the docs themselves.
