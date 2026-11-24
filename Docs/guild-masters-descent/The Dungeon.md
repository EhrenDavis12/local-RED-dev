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

Each floor has 1–3 battles. Between floors, every member gets back five per cent of
their maximum health, and nothing comes back between the battles on a single floor.
Every 5th floor is a safe rest area, where every member gets back fifteen per cent
instead of the five, not both, and the player may choose to return to the top and exit
the dungeon. The Cook adds to both figures, covered in the Specialists doc. Retreating
always costs the loot gathered since the last safe floor — any party member can carry
some of it, so how much is lost depends on who came along.

The floors between rest areas group into sets of four, skipping the rest areas themselves,
so the sets run 1–4, then 6–9, then 11–14, and so on. The enemy-type ladder below is
set by these same sets.

A floor has a power level, and it is counted in stat points. The power is a pool of
base-stat points, and an enemy costs the sum of its five base stats to put on the
floor.

- A dungeon's first floor has a power set by the dungeon's own rank, 100 points at F and
  doubling at each rank:

  - F — 100 points
  - E — 200
  - D — 400
  - C — 800
  - B — 1,600
  - A — 3,200
  - S — 6,400
  - SS — 12,800
  - SSS — 25,600

- The power triples from a dungeon's first fighting floor to its deepest, climbing evenly
  across them. A deep dungeon has more floors to build over, so its climb from one floor
  to the next is gentler than a shallow one's.
- Rest areas hold no battles and no power.

The floor's power is split between its battles, weighted so the floor builds toward
its last fight:

- 1 battle — the whole floor's power
- 2 battles — 40% then 60%
- 3 battles — 20%, then 30%, then 50%

A battle's share is spent on enemies. An enemy's baseline cost is set by its rank,
starting at 30 points at F and doubling at each rank:

- F — 30 points
- E — 60
- D — 120
- C — 240
- B — 480
- A — 960
- S — 1,920
- SS — 3,840
- SSS — 7,680

How deep the floor sits in its own dungeon scales that cost down. At a dungeon's
shallowest floor an enemy costs its full baseline; at the deepest it costs a third of
it. So the rising power of the lower floors is spent on numbers rather than on
strength, and the bottom of a dungeon is a horde — the bottom of an F dungeon a horde
of weak F enemies, the bottom of an SSS dungeon a horde of weak SSS ones.

The count falls out of the division. The number of enemies in a battle is its share of
the power divided by what one enemy costs, never fewer than one and never more than
the fifteen the battle grid holds. A roll varies an enemy's cost from half to twice
the scaled figure, so the same share can come out as a few strong enemies or a swarm
of weak ones. Where the count would pass fifteen, the points left over raise each
enemy's cost instead, so the deepest floors field a full grid of enemies that are
individually stronger than the floor's own scaling would make them.

The chance an enemy carries a weapon or wears armour rises with the floor. A weapon's
chance is 1 to 3 per cent on the first floor and rises 5 to 7 points a floor; armour's
chance starts on floor 11 at 3 to 5 per cent and rises at the same rate a floor. A
weapon is therefore always the likelier of the two.

An enemy's cost is its stat points plus what its gear is worth, a piece being worth
the middle of its rolled range — so arming an enemy means fewer of them on the floor.

An enemy's share becomes its stats in a fixed shape. The points are spread down the
ordering its type's stat weighting gives, in the ratio 8 : 7 : 6 : 5 : 4 — so a
30-point enemy comes out at 8 in its type's leading stat, then 7, 6, 5 and 4. The
weightings are in the Guild Members doc.

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
slots restricted to a particular kind of thing — the Specialists doc covers which ones.
A potion takes 1 slot, and so does an item of loot — they cost the same, because if loot
were free a party would simply fill every slot with potions. At one slot each, the
choice is how many potions to pay for in treasure.

Dungeon diving yields materials or items, and the floor itself pays gold. A dive can also
drop a weapon or a piece of armour on certain floors.

- One enemy in four drops materials or an item.
- Materials come as ores or herbs, the two kinds the Miner and the Herbalist carry
  restricted slots for.
- Gold comes by the floor rather than by the enemy. At F rank a floor pays a band from
  its enemy count less three up to its enemy count — a floor of fifteen enemies pays 12
  to 15 gold. Each rank above F adds 10 gold of base to both ends of that band.
- A weapon or a piece of armour drops on the last fighting floor before each rest area,
  and on the dungeon's last floor.
- A drop the party has no room for is lost, the same way a dead member's gear is lost
  when there's no capacity left for it.

Gold is covered in the Core Concept doc.

## Entering the Dungeon

There is a cost to enter the dungeon, 2 gold a member in an F-rank dungeon rising 2 a
rank, and the more members taken, the more expensive it is. This makes party size a
choice for the player.

A large party can have advantages — boss floors where more members are needed to secure
victory — while for exploring, a large party is less advantageous.

There is an inherent risk in diving that the members brought might not be right for the
floors ahead.

A Scout in the party is what turns that risk into a decision: the player can choose to
return and build a new team, or train to be more powerful, before continuing.

The player re-enters at the last rest area reached, and must pay the entry fee again plus
a teleportation fee, reckoned from the floor being returned to: 1 gold a floor in an
F-rank dungeon, rising 1 a rank. This stops the player exploring five floors, returning,
and rearranging the party with no penalty.

Potions take up the party's carrying capacity, and they're added to it at the start of
the raid.

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
- One enemy in four drops materials or an item, and nothing says how often it is one
  rather than the other.
- A weapon or a piece of armour drops on the floor before each rest area and on the
  last floor, and it isn't said how many pieces drop there — one, or more the deeper
  the floor.
- A drop the party has no room for is lost, which is the same rule a dead member's
  gear follows. Should a full party be able to throw something away to make room for
  a find instead?
