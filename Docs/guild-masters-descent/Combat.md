# Combat

> **Status:** Early design. Nothing is built yet — the grid, the turn order and how gear
> breaks are settled, but what changing formation mid-battle costs isn't.

## Formation

The player sets the team up on a grid of nodes, 5 wide and 3 deep — three rows of five
positions each. Enemies use the same style of grid.

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
has no special bar at all, and their attack damage works the way it does for anyone
else.

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

## Open Questions

- What does changing formation mid-battle cost the player, if anything?
