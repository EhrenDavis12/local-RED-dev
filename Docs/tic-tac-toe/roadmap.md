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
- Open Questions

## [Menus and UI](./Menus%20and%20UI.md)
Menu structure, screen flow, navigation, theme selection, settings, persistence, and the
game-over rematch flow.

**Headings:**
- Main Menu
  - About Us
- Play Game → Where It Takes You
  - What an open game holds
  - How many open games we keep
  - Deleting an open game
- A New Game → What It Starts
- Pass-and-Play Turn Handoff
- How to Play — the On-Board Legend and Hint
- Screens (so far)
- Navigation and the Back Stack
- Theme Selection
- Settings Menu
  - Defaults on a fresh install
  - Vibrate on Touch
  - Purchases
  - How you reach settings from gameplay
- Dynamic Type
- Game Over → Rematch
  - The result card
- Persistence
  - When a game is written to storage
  - Leaving a game mid-play
- Open Questions

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
- Engine Contract
- Variants / Optional Rules
- Conflicting Ideas (unresolved)
- Open Questions

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
  - When the selected move claims its own send target
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

## [Theming](./Theming.md)
The theme system — what a theme is, how it inherits from Neon, and what it controls.

**Headings:**
- The Idea
- Architectural Rule (the important part)
- Where Themes Live
- Choosing a Theme
- What Is a Theme?
- Neon Is the Base Theme (inheritance model)
  - How it works
  - The merge rules
  - Why this matters for the build
  - Closing Neon's value gaps
  - Watch out for
- Theme Catalog
  - Theme 1 — Neon (base)
  - Theme 2 — Classic Red vs Blue
- Free and Paid Themes
- What a Theme Controls
- Sound Decisions
  - Sound falls back to Neon
  - Music
  - The tap sound
  - Global mute
- Inheritance Depth
- What a Theme Does NOT Control
- Open Questions

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
- How Animations Play
- Turning Animations Off
- Open Questions

## [Alternative Game Styles](./Alternative%20Game%20Styles.md)
Parking lot for variants and roads-not-taken — not the current game. See
[Rules](./Rules.md) for the actual rules.

**Headings:**
- Lock-In Style

## [Tech Design](./Tech%20Design.md)
How we build it — framework, language, storage, state management, project structure, and
release/distribution.

**Headings:**
- What the Design Docs Already Imply
- Platform and Targets
  - Minimum iOS version
  - Orientation — portrait only
  - Fresh build, not a refactor
- Project Structure
- The Rules Engine
  - One value holds the game and the series
  - The engine speaks the project's vocabulary
  - Quadrants and cells are indexed the same way
  - Three placement states, and the UI reads them
  - The series lives in the same state
  - The engine publishes which three quadrants won
  - What the engine refuses
  - What the engine is not
- State Management
- Navigation
- Rendering the Board
  - Marks — supplied by the theme
- The Theme System
  - Flutter's ThemeData vs our own theme object
  - Themes pick their own font
  - The theme system is the main architectural risk
- Persistence and Serialization
  - Serialization and the storage layer
  - Every persisted record carries a version stamp
  - What a stored open game holds
  - The open-games list has a defined order
  - The cap is enforced on create, and the store never evicts
  - Reads return "nothing stored", and defaults resolve above this layer
  - Entitlement state is written down, never minted
- Audio and Assets
  - Where sound and art assets come from
  - One script, and the per-asset inputs are data
  - The generator is an authoring tool, not a build step
  - What gets generated, and where it lands
  - Nothing generated is applied directly — drafts, then approval
  - Declared in `pubspec.yaml`, or it does not ship
  - Regenerating, and leaving nothing behind
- In-App Purchases and Entitlements
  - Entitlements — Apple stores them, no backend needed
- Kids Category
- Crash Reporting
  - What gets caught
  - What a crash report captures
  - The one error that carries game state renders none of it
  - A caught error is silent to the player and logged for the developer
  - Reports are held in memory
- Testing
  - Unit tests for the rules engine
  - Widget tests for the board — no golden tests
  - A test that fails on hardcoded theme values
- Distribution and Release
  - App name
  - Bundle identifier
  - Distribution — public App Store release
  - The app icon
  - CI — local builds only
  - Release tooling — fastlane
- Open Questions
  - 1. Persisted data — migration
  - 2. Theme loading
  - 3. Build and distribution
  - 4. Kids category — age rating questionnaire
  - 5. Which store holds entitlement state?
  - 6. Crash reporting
  - 7. Timing and opacity that aren't theme values
  - 8. Generated assets
  - 9. The rules engine

---

This is an index of locations, not a summary of content. For what any of this actually
says, read the docs themselves.
