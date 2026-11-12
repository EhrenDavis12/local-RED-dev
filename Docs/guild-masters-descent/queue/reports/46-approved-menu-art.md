# Approved menu and background art in the game — what came in, what is still missing

> **Status:** Report for queue item #46, 2026-11-12. Branch `queue/46-approved-menu-art` in
> `src/guildmasters-descent`.

## What came in

Copied (never linked) from the animation checkout, only what annie's queue records as approved:

| Art | Approved as | Where it shows in the game |
|---|---|---|
| Parchment inked map, recoloured "paper kept warm" | annie #31, recolour #197 option 3 | Behind the title screen and as the guild hall |
| Gold icon 1 | annie #75 | The hall's gold counter |
| Meadow battle background, 16 layers | annie #16–#22, exported in the approved Unity scene #64 | The demo battle |
| Cave battle background, 5 layers | annie #27 (the `stal_TEST` still) | Every battle in a dive |

The hall is now the map: the five buildings are the five entry points, each with a name tag —
the arena is the Mission Board, the guild house the Recruiting Board, the cave the Dungeon
Board, the cottage the Dorms, the armory the Shop. Both battle backgrounds are still (drawn at
the same moment as the approved stills); the drifting parallax is a follow-up.

## Not used, and why

- **The approved settings, about, character select and shop screens** (annie #113, recoloured
  in #197) are flat pictures with made-up text painted in — an Archer pick, "Sword 220", a
  Battle speed and a Language row the game does not have. Pasting them over the live screens
  would show wrong words, so they stay as layout references.
- **The R04 One Rod scroll style** (annie #49) has no pieces to build menus from: its page,
  pop-up and buttons are flat pictures with words in them, drawn by a script. Every button and
  panel stays a plain block until annie exports the pieces.
- **Contact shadows, haze sheets, the cave vignette, the occluder and the tree strip**
  (annie #201, #212, #213, #214, #202) are still tests, not approved.

## Still a yellow shape

- Title Logo on the title screen.
- "Mission Board" art in the Mission room, "Dungeon Board" art on the Dungeon Board screen.
- Every `<Type> Portrait` on the Recruiting Board and in the Dorms.
- Battle characters: every type but the Archer, the Archer's special, and all monsters.

## Not yellow, but still waiting on art from the animation side

- R04 scroll pieces cut out with transparency, ready to stretch: rod, page body, curled end,
  tab, pop-up, and tan and red buttons in normal and pressed states. This one unlocks every
  menu, button, slider and pop-up.
- A paper background for the rooms (New Game, Load, Settings, Dorms, Shop, the boards, the
  dive screen), which stay black for now.
- Battle HUD bars and the Victory / Defeat banner (only flat mockups exist).
- The game font (Eagle Lake, option 11, could be copied in later).

## Follow-ups on the game side

- The map as the very first screen, with no title screen (the user's word on annie #113):
  needs New Game, Load and Settings moved onto the map.
- Parallax drift and cloud movement on both battle backgrounds; the meadow grass blend.
- The battle grid's top lane stands on the hills rather than the ground; fit the grid to the
  ground line.
- On the hall, the Dorms tag and the gold counter sit over some bushes — readable but busy.

## Open Questions

- None beyond the queue item's own questions.
