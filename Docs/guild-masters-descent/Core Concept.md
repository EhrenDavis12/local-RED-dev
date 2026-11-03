# Guild Master's Descent

> **Status:** Early concept. Nothing is built yet — the systems are taking shape, but most
> of the numbers aren't set.

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

A party is made of multiple divers, plus specialists. Specialists have a reason for being
there and need to be protected by the party. Specialists have out-of-combat abilities.

The maximum team is 15 members, including specialists, and the player chooses how many of
that to take.

## Missions

Missions are support activities that help the guild — things like gathering herbs to make
medicine, or hunting for materials to make better equipment. Missions are timed, and any
member sent on one is not available for the dungeon dive.

Missions have a stated rank, using the same F–SSS ladder as guild rank — a mission marked
C is one a C-rank guild is expected to handle. The mission board only offers missions at
or below the guild's own grade; a guild cannot reach for a mission ranked above itself.
There's backend variance on top of that, though: a mission can turn out easier or harder
than its stated rank suggests. That's deliberate, to give the player a sense of mystery.

Mission failure normally results in an injured status, not death. An injured member is out
of action until healed — they can't be sent on a mission or taken on a dive. They recover
on their own for free, though slowly — or the player can pay gold to speed it up. The
exception: sending an individual member whose own rank or tier is below the mission's
rank, even one the guild as a whole is otherwise suited for, carries a chance that member
is killed.

Missions pay, and they also collect items and materials the guild can sell; some mission
rewards can themselves be items.

## The Recruiting Board

The recruiting board is where new members are hired — divers and specialists alike.
Recruiting costs gold. A recruit's rank or tier caps out at the guild's own: an A-rank
guild can hire up to A-rank members.

A candidate on the board shows its type and its rank or tier plainly, along with a rough
impression of where its strengths lie — promising, unremarkable, that kind of thing. There
are no exact stat numbers.

The board restocks over time: new candidates appear as time passes, so a poor board is
worth waiting out.

The guild's roster size grows with guild rank. That's separate from the fifteen-member
party cap, which stays the same regardless of guild rank.

A member can be dismissed to make room on the roster. The gold spent recruiting and
promoting that member is lost.

The intent is that a member raised up through the ranks ends up stronger than one hired at
that rank, because it keeps the stats earned at every level climbed along the way.

Which specialist types the guild can recruit is covered in the Specialists doc.

## The Economy

Gold is the money in the game.

At rank F the guild has access to a shop. The guild sells items and materials there, and
the shop sells to the guild too — the player can buy items and equipment.

Having a blacksmith, armourer or alchemist in the guild gives it that kind of crafting.

## Finding Dungeons

Dungeons are found through the mission board. The missions that find a dungeon are the
challenge the player works against.

There are two ways to find one. There's a small chance of finding a dungeon on an ordinary
mission. When the guild ranks up, one mission appears on the board to claim that rank's
dungeon — the claim mission requires a big group to go and take it. A claim mission can
fail, and it stays on the board — the dungeon isn't lost, so the guild can try again.

Once a dungeon is found, the guild claims it. A dungeon's depth is random when it's
created.

The player can only find dungeons at or below the guild's rank, so ranking up is what
makes new dungeons findable at all. Finding is the only gate — once a dungeon is claimed,
it can be dived, with no separate rank requirement to enter one the guild already holds.

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

## Formation

The player sets the team up on a grid of nodes, 5 wide and 3 deep — three rows of five
positions each. It's managed in a planning sub-menu. Enemies use the same style of grid.

Specialists occupy a node on the grid too, and can be attacked there like anyone else.

The player can also change formation in the middle of battle — formation is ongoing battle
planning rather than a one-time puzzle. Some enemy types can reposition mid-battle too,
but not all of them can.

## Combat

Combat is turn-based tactics. Turn order is determined by Dexterity — the members' and the
enemies'. On a guild member's turn, that member is highlighted. Default attacks are
auto-selected. The player can select one enemy to be specifically targeted by the entire
party — this cuts down on clicks during gameplay.

Each member has a special bar. When it's full, the player can use a special. Every
attack a member makes charges that member's bar — that's the base, and it's the same
for every type. Each combat type also has its own bonus condition that charges its bar
on top of that.

A specialist takes a turn like anyone else. On it, the specialist makes a basic attack
against a single target — a close-range attack, so its reach is the first available row
like any close attacker, the enemy front line. The attack is weak — the intent is that
specialists help a little rather than being a full detriment to the battle. A specialist
has no special bar at all, and their attack damage comes from Strength, like other
physical attackers.

Characters and enemies have either close-range or far-range attacks, with possible AoE
effects. Close-combat reach is the first available row: if the first row has been removed,
the second row can then be hit. A far-range attack can reach any row on the enemy's grid.

## Equipment Durability

Gear wears down as it is used — weapons degrade from attacking, armour from being hit. It
works fully until it reaches zero, then breaks and contributes nothing — there is no
gradual decline before that.

Broken armour means the member's defence falls back to Constitution alone.

A broken weapon leaves the member unarmed and much weaker: they still attack, for a
fraction of the damage, and their combat type's attack shape still applies — a Brute with
a broken weapon still cleaves, just feebly.

Repairs happen in the guild hall between dives. A Blacksmith or Armourer in the party can
also repair in the field, a convenience rather than a requirement. Field repair only works
on gear that is still above zero. Once an item breaks it stays broken for the rest of the
dive — a Blacksmith or Armourer in the party cannot bring it back.

## Training Missions

However far down the player has reached, they can send automated "training" missions down
to that depth, to let members gain experience. These training missions are sent from the
dungeon board. A training run can injure a member, but can never kill one.

## Open Questions

- What changes at each rank from F to SSS?
- What does changing formation mid-battle cost the player, if anything?
- How far can a training mission level a member?
- With multiple dungeons, is the depth a training mission can reach tracked per dungeon,
  or shared across them?
