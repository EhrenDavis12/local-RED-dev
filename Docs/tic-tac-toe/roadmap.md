# Roadmap — Tic-Tac-Toe-Extreme

> Index of where things live across the design docs in `Docs/tic-tac-toe/`. This is a map,
> not a summary — read the linked doc for the actual content and reasoning.

## [Game Overview](./Game%20Overview.md)
The pitch, core concept, session structure, and target audience for the game.

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

## [Rules](./Rules.md)
The game rules — setup, turn structure, placement/sending rule, winning conditions, and edge
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
The game board's structure, scoreboard, highlight systems, input model, and visual/theme
requirements.

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

**Decisions:** none yet (no `## Decisions` section in this doc).

## [Menus and UI](./Menus%20and%20UI.md)
Menu structure, screen flow, settings, and persistence across the app.

**Headings:**
- Main Menu
- Play Game → Where It Takes You
- A New Game → What It Starts
- Pass-and-Play Turn Handoff
- Screens (so far)
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

## [Theming](./Theming.md)
The theme system — what a theme is, the Neon-base inheritance model, the theme catalog, and
the theme/app-setting boundary.

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
- Marks Beyond X and O
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

## [Animations](./Animations.md)
Animation direction, vocabulary, scope, and how animations relate to the theme system.

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
- Themes define their own animations from scratch
- One animation at a time
- Duration lives in the animation
- Animations don't block input
- Turn animations off — a global setting
- Animations off = instant state change

## [Tech Design](./Tech%20Design.md)
How the game is built — framework, platform target, architectural implications of the design
docs, and open technical questions.

**Headings:**
- Decisions
- Framework — Flutter
- Primary target — Apple
- Language — Dart
- Theme representation — data, not code
- Fallback to Neon — merge, not resolve
- Flutter's ThemeData vs our own theme object
- Orientation — portrait only
- Minimum iOS version
- What the Design Docs Already Imply
- The theme system is the main architectural risk
- Open Questions

**Decisions:**
- Framework — Flutter
- Primary target — Apple
- Language — Dart
- Theme representation — data, not code
- Fallback to Neon — merge, not resolve
- Flutter's ThemeData vs our own theme object
- Orientation — portrait only
- Minimum iOS version

## [Alternative Game Styles](./Alternative%20Game%20Styles.md)
Parking lot doc (per `forge.json` → `parkingLotDocs`) for game-style variants not chosen for
the current build.

**Headings:**
- Lock-In Style

**Decisions:** none — this is a parking lot doc, not a doc of settled decisions.

---

Source of truth is the docs themselves — this file only maps where things live.
