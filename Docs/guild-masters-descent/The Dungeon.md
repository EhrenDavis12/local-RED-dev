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
dungeon is claimed. It's rolled from a band set by the dungeon's own rank, starting at F
and adding 6 to each end per rank:

- F — 5 to 15 floors
- E — 11 to 21
- D — 17 to 27
- C — 23 to 33
- B — 29 to 39
- A — 35 to 45
- S — 41 to 51
- SS — 47 to 57
- SSS — 53 to 63

The intent is that the player tries to find as many dungeons as they can.

## The Dungeon

Dungeon diving is the main gameplay. Death in the dungeon is permanent — there is no way
to bring a dead member back. The risk is inherent in the choice: send someone you know
will survive, or send a team and see who comes back.

Each floor has 1–3 battles. Between floors, every member gets back five per cent of their
maximum health, and nothing comes back between the battles on a single floor. Every 5th
floor is a safe rest area, where every member gets back fifteen per cent, and the player
may choose to return to the top and exit the dungeon. The Cook adds to both figures,
covered in the Specialists doc. Retreating always costs the loot gathered since the last
safe floor — any party member can carry some of it, so how much is lost depends on who
came along.

The floors between rest areas group into sets of four, skipping the rest areas themselves,
so the sets run 1–4, then 6–9, then 11–14, and so on. Both ladders below — enemy count and
enemy type — are set by these same sets.

Each fight's enemy count is a band set by the set a floor falls in, starting at 1–3
enemies and rising by one at each step:

- Floors 1–4 — 1 to 3 enemies
- Floors 6–9 — 2 to 4
- Floors 11–14 — 3 to 5
- Floors 16–19 — 4 to 6
- Floors 21–24 — 5 to 7
- Floors 26–29 — 6 to 8
- Floors 31–34 — 7 to 9
- Floors 36–39 — 8 to 10
- Floors 41–44 — 9 to 11
- Floors 46–49 — 10 to 12
- Floors 51–54 — 11 to 13
- Floors 56–59 — 12 to 14
- Floors 61 and deeper — 13 to 15

The battle grid holds fifteen, and the top of this ladder is as many enemies as the grid
holds. The deepest dungeons the ranks allow reach it: an SSS dungeon rolls between 53 and
63 floors, and the ladder's top band starts at floor 61.

Each set also has a limited pool of enemy types that can appear there, growing by one type
per set:

- Floors 1–4 — 1 to 2 types
- Floors 6–9 — 2 to 3
- Floors 11–14 — 3 to 4
- Floors 16–19 — 4 to 5
- Floors 21–24 — 5 to 6
- Floors 26 and deeper — all six

The ladder stops at six because there are only six combat types.

Capacity is counted in slots, and every member carries 5 slots. Some members carry extra
slots restricted to a particular kind of thing — the Specialists doc covers which ones. A
healing potion takes 1 slot, and so does an item of loot — they cost the same, because if
loot were free a party would simply fill every slot with potions. At one slot each, the
choice is how much healing to pay for in treasure.

Dungeon diving yields materials or items, and sometimes small amounts of gold. A dive can
also drop a weapon or a piece of armour. One enemy in four drops something, and one drop
in ten is gear rather than materials or an item.

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

Healing potions take up the party's carrying capacity, and they're added to it at the
start of the raid.

## Training Missions

The player can send automated "training" missions into a dungeon, down to the deepest
floor the party has reached in that dungeon, to let members gain experience — the depth a
training mission can reach is tracked per dungeon. These training missions are sent from
the dungeon board. A training run can injure a member, but can never kill one.

What the injured status means is covered in the Core Concept doc.

## Open Questions

- How far can a training mission level a member?
- Each set of floors has a pool of enemy types that can appear there, but nothing says how
  that pool is chosen — rolled when the dungeon is created, or when the party first
  reaches the set, and whether a deeper set keeps the shallower set's types or draws fresh
  ones.
