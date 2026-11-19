# Focus

> **Status:** The user's. The desk edits it only to write down what the user said, in their
> words. The mastermind reads it and never edits it.

## Goal

User (2026-11-11): "a fully running Unity game that runs the MVP of the game. This is should
prove our game and that the basic concept is good. Build out a fully running Unity game. This
includes the menu systems character managment and a runnable dungeon. If details are missing,
block that work for now. Use what ever assests we have if we do need more assest then just use
simple bright Yellow shapes to fill in the missing assets."

Refined with the user (2026-11-11), from the design docs:

A playable Unity MVP of Guild Master's Descent that proves the core loop is fun. A player starts
a new F-rank guild in the guild hall, hires divers from the recruiting board, sets their gear,
builds a party on the 5-by-3 grid, and dives a dungeon floor by floor — turn-based battles where
type advantages, the support ring and specials matter, permanent death, and a choice at the
floor-5 rest area to push on or come home with the loot. Then they sell, heal, recruit and go
again.

In: title menu, new game, save and load, settings; the guild hall and its three boards;
recruiting; a roster screen with each member's stats, level, gear and injuries; the shop; one dungeon at least 10 floors deep with two rest areas; combat with all six
combat types plus the Cook and the Porter. Time keeps passing while the game is closed —
injuries heal while the player is away.

- **Platform.** User: "Build in on unity on this computer but it will be tartgeted for Phone
  IOS." Built and tested in the Unity editor on this Mac; the target is the iPhone, so screens
  are laid out for a phone. User (2026-11-11): "Always Sideways" — landscape only.
- **Missing details.** A missing *number* gets a placeholder: a sensible value, kept with every
  other placeholder in one tuning file, and listed for the user. A missing *rule or behaviour*
  blocks that work.
- **Art.** Only final, approved assets from the animation work in the other checkout, copied
  in. Anything missing is a bright yellow shape with its name written on it, and goes on a list
  for the animation side. One exception, user (2026-11-13): "the only thing that won't actually be
  a final art, which is just the at the ready pose for the characters" — each character's static
  ready pose (and rest pose in menus) is used as a stand-in until its idle animation exists.
- **The original docs win.** User (2026-11-12): "if there is a contradiction, the main documents
  win we need to convert any changes that those main documents decided over what we had in the
  EhrenDocs." Where the other dev's docs and our change notes disagree, the change note gives way.
- **Approved look is binding.** User (2026-11-13): "a lot of our design choices have been ignored
  in the building of the game ... We need to find them and make sure the game has these design
  choices." Every look-and-feel choice the user approved on the animation side is how the game
  looks: bars, battle scene layers, menus, fonts, icons, effects.
- **Copy annie's Unity work, don't re-create it.** User (2026-11-13): "Yes, try forge just copy first do trust what Annie did. It's all been approved. It all looks good."
- **The one rule of ours that beats the new docs.** User (2026-11-18): "The only
  contradiction I want to win is from our side is that an enemy must wait on the battle on the
  attack sequence so that so that their present when being attacked so two people are attacking
  at the same time they don't actually attack at the same time one attack than the other
  attacks that's the only thing I want winning over what the new doc Say" So: attacks never
  land at the same moment — one attacker goes, the other waits until its target is back in its
  spot. Every other contradiction, the other dev's docs win.
- **Standing yes.** User chose "Build on its own": the mastermind's proposals toward this Goal
  go straight into the queue and are built without waiting. Each finished piece still waits for
  the user's approval before it is merged.
- **Standing approval.** User (2026-11-11): "just start approveing everthing for now. its a blank
  project so their is no risk here." Until the user takes it back, a finished piece is approved
  and merged into the game by the worker that built it, without waiting for the user.

## Right now

<!-- What matters most this week. Every auto job serves a line of this. -->

- User (2026-11-17): "I don't want your progress to stop. Keep going create more jobs. If
  there's anything left in the documentation that we haven't actually completed yet let's go
  ahead and start those jobs too." So: keep the queue full — build whatever the design docs
  settle that the game does not do yet, including the other dev's newest edits (Combat, Battle
  Test, Individual Types).

## Not included

User (2026-11-11): "not included in the first version we are going for a MVP like a POC." So:
the other six specialists, crafting, and the rank ladder past the first
promotion are all out of the first version. User (2026-11-11): "yes move them out of the MVP for now" —
timed missions are out of the first version too. User (2026-11-11): "leave it out for now will
reintroduce that later. its not needed for MVP" — training missions (automatic dungeon runs
for experience, sent from the dungeon board) are out of the first version.

User (2026-11-17), on guild ranks and finding dungeons: "If the Docs dont describe it then we
cant do it." So: guild ranks above F and finding dungeons are back in, built only as far as the
design docs describe them.

## Later

- Timed missions — out of the MVP for now (user, 2026-11-11).
- Training missions — "will reintroduce that later" (user, 2026-11-11).
- Battle framing with more ground and less sky — "hold off on making more ground and less sky just for now" (user, 2026-11-13).

<!-- Ideas to keep, not to build yet. The mastermind never queues these; the user moves one
to the queue by saying so. -->

## Learn

<!-- Research topics, in order. The mastermind takes the first with no report. -->
