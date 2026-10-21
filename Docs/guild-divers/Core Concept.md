# Guild Divers

> **Status:** Early concept. Nothing is built yet — this is the first pass at what the
> game is.

## The Premise

The player manages a guild. The player has no presence or avatar in the world — they are
not a character in it. The main screen is the inside of a guild hall.

## Guild Rank

The game starts at an F-rank guild. Grade is raised by clearing milestone quests — named,
one-off tests that appear when the guild is close to promotion. They're separate from the
routine work on the mission board. The full ladder, in order:

F → E → D → C → B → A → S → SS → SSS

## The Three Boards

The hall has three boards — a mission board, a recruiting board, and a dungeon board.

The dungeon board has three functions: dungeon information, which shows the types of
monster and enemy found in each of the dungeons; dungeon planning, where the team that
will go into a dungeon is built; and dungeon training, which handles the team that will
train in a dungeon.

## The Party

A party is made of multiple divers, plus support characters. Support characters have a
reason for being there and need to be protected by the party. Support characters have
out-of-combat abilities — for example, a porter, who adds a lot more carrying capacity on
top of what any party member already carries, and a cook who helps healing between
battles. That list isn't complete.

## Missions

Missions are support activities that help the guild — things like gathering herbs to make
medicine, or hunting for materials to make better equipment. Missions are timed, and any
member sent on one is not available for the dungeon dive.

Missions have a stated rank, using the same F–SSS ladder as guild rank — a mission marked
C is one a C-rank guild is expected to handle. The mission board only offers missions at
or below the guild's own grade; a guild cannot reach for a mission ranked above itself.
There's backend variance on top of that, though: a mission can turn out easier or harder
than its stated rank suggests. That's deliberate, to give the player a sense of mystery.

Mission failure normally results in an injured status, not death. The exception: sending
an under-levelled individual member on a mission, even one the guild is otherwise suited
for, carries a chance that member is killed.

## The Dungeon

Dungeon diving is the main gameplay. Death in the dungeon is permanent — there is no way
to bring a dead member back. The risk is inherent in the choice: send someone you know
will survive, or send a team and see who comes back.

Each floor has 2–3 battles. Every 5th floor is a safe rest area, where the party heals and
the player may choose to return to the top and exit the dungeon. Retreating always costs
the loot gathered since the last safe floor — any party member can carry some of it, but a
porter, if one came along, carries far more.

## Formation

The player sets the team up on a grid of nodes, 3 wide and 5 deep. It's managed in a
planning sub-menu. Enemies use the same style of grid.

Support characters occupy a node on the grid too, but they take no turn of their own —
their value is entirely outside combat.

The player can also change formation in the middle of battle — formation is ongoing battle
planning rather than a one-time puzzle.

## Combat

Combat is turn-based tactics. Turn order is determined by the speed attribute of the chosen
members and the speed of the enemies. On a guild member's turn, that member is highlighted and
the player selects the target of the next attack.

Each member has a special bar that fills over time. When it's full, the player can use a
special.

Characters and enemies have either close-range or far-range attacks, with possible AoE
effects. Close-combat reach is the first available row: if the first row has been removed,
the second row can then be hit.

## Training Missions

However far down the player has reached, they can send automated "training" missions down to
that depth, to let members gain experience. These training missions are sent from the dungeon
board.

## Open Questions

- How many divers and support characters go on a dive?
- What changes at each rank from F to SSS?
- What types of characters can the player recruit? (parked for later)
- What does changing formation mid-battle cost the player, if anything?
- How far can a training mission level a member?
- With multiple dungeons, is the depth a training mission can reach tracked per dungeon, or shared across them?
