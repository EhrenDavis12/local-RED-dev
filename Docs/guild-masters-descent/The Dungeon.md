# The Dungeon

> **Status:** Early design. Nothing is built yet — the shape of a dive is settled, floors,
> rest areas and permanent death, but how far training goes isn't.

## The Dungeon Board

The dungeon board has three functions: dungeon information, which shows the types of
monster and enemy found in each of the dungeons; dungeon planning, where the team that
will go into a dungeon is built; and dungeon training, which handles the team that will
train in a dungeon.

A newly claimed dungeon starts near-blank. The enemy types and the floor layout appear
as the party reaches each floor.

For each dungeon, the board shows the deepest floor reached and the dungeon's depth,
side by side.

Planning happens in two steps: the player selects the members first, then arranges them
on the grid. That second step is a zoomed-in view of the battle map rather than a
separate screen. The system does the initial placement, putting combat types in front and
making support links where it can — the player can edit it from there.

The dungeon board is also where the player enters a dungeon, and where they re-enter at
the last rest area reached.

The grid used for the battle map is covered in the Combat doc.

## Finding Dungeons

Dungeons are found through the mission board. The missions that find a dungeon are the
challenge the player works against.

The player can only find dungeons at or below the guild's rank, so ranking up is what
makes new dungeons findable at all. Finding is the only gate — a dungeon the guild
already holds needs no rank to enter.

There is a small chance of finding a dungeon on an ordinary mission, and a dungeon found
that way is claimed outright — finding and claiming are one event on this route.

Ranking up reveals that a dungeon is there, and nothing more about it: the guild knows it
exists and no more than that. A claim mission then appears on the board, and it requires a
big group to go and take it. A claim mission can fail, and it stays on the board — the
dungeon isn't lost, so the guild can try again.

A dungeon's depth is random when the dungeon is created, and it isn't known until the
dungeon is claimed.

The intent is that the player tries to find as many dungeons as they can.

## The Dungeon

Dungeon diving is the main gameplay. Death in the dungeon is permanent — there is no way
to bring a dead member back. The risk is inherent in the choice: send someone you know
will survive, or send a team and see who comes back.

Each floor has 2–3 battles. Every 5th floor is a safe rest area, where the party heals and
the player may choose to return to the top and exit the dungeon. Retreating always costs
the loot gathered since the last safe floor — any party member can carry some of it, so
how much is lost depends on who came along.

Dungeon diving yields materials or items, and sometimes small amounts of gold.

Gold is covered in the Core Concept doc.

## Entering the Dungeon

There is a cost to enter the dungeon, and the more members taken, the more expensive it
is. This makes party size a choice for the player.

A large party can have advantages — boss floors where more members are needed to secure
victory — while for exploring, a large party is less advantageous.

There is an inherent risk in diving that the members brought might not be right for the
floors ahead.

A Scout in the party is what turns that risk into a decision: the player can choose to
return and build a new team, or train to be more powerful, before continuing.

The player re-enters at the last rest area reached, and must pay the entry fee again plus
a teleportation fee. This stops the player exploring five floors, returning, and
rearranging the party with no penalty.

## Training Missions

The player can send automated "training" missions into a dungeon, down to the deepest
floor the party has reached in that dungeon, to let members gain experience — the depth a
training mission can reach is tracked per dungeon. These training missions are sent from
the dungeon board. A training run can injure a member, but can never kill one.

What the injured status means is covered in the Core Concept doc.

## Open Questions

- How far can a training mission level a member?
