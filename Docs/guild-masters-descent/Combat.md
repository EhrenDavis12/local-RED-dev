# Combat

> **Status:** Early design. Nothing is built yet — the grid, the cooldown pacing and
> Dexterity setting the cooldown are settled, but when the player acts and how the Luck
> reset's chance works aren't.

## Formation

The player sets the team up on a grid of nodes, 5 wide and 3 deep — three rows of five
positions each. Enemies use the same style of grid.

Specialists occupy a node on the grid too, and can be attacked there like anyone else.

The player can also change formation in the middle of battle — formation is ongoing battle
planning rather than a one-time puzzle. Some enemy types can reposition mid-battle too,
but not all of them can.

## Cooldowns

Combat is not turn-based. Every guild member and every enemy runs on its own cooldown — a
process that sets how often that combatant attacks. How fast a member's cooldown is met is
determined by Dexterity, and a cooldown is something that can be bettered at higher
levels.

Because cooldown speed comes from Dexterity, the types that rank Dexterity lower attack
less often — the Brute and the Tank among them — and that's intended rather than something
to be balanced away.

The pacing intent: a low-level fight feels a little slow at first, and a higher-level
fight has more going on, but a fight should take about the same real time at either end,
so combat stays fairly balanced across levels.

## The Luck Reset

When a member finishes an attack, there's a Luck check for whether the cooldown resets
instantly. On success, the member attacks again immediately, with no cooldown wait at all.
That free attack gets no Luck check of its own — that's what "only once" means, so the
effect can't chain into a second free attack. On failure, the cooldown charges normally.

Dexterity sets the rhythm; Luck occasionally skips the wait.

## Player Input

Default attacks are auto-selected. The player can select one enemy to be specifically
targeted by the entire party — this cuts down on clicks during gameplay.

## Attacks and Reach

Characters and enemies have either close-range or far-range attacks, with possible AoE
effects. Close-combat reach is the first available row: if the first row has been removed,
the second row can then be hit. A far-range attack can reach any row on the enemy's grid.

Each strike of a multi-strike attack is resolved on its own: it rolls to hit separately,
and defence is subtracted from it separately.

## The Special Bar

Each member has a special bar. When it's full, the player can use a special. Every attack
a member makes charges that member's bar — that's the base, and it's the same for every
type. Each combat type also has its own bonus condition that charges its bar on top of
that — covered in the Individual Types doc.

## Lasting Effects

Vanish, Shields Up and the Mage's lingering field all last the same number of the
owner's own cooldown cycles — the member whose effect it is. So "the same length" means
the same count, not the same stretch of real time: a fast member's effect is brief on
the clock while a slow member's runs long, and every member gets the same number of
cycles of value out of it. Each of the three is covered in the Individual Types doc.

## Specialists in Combat

A specialist attacks on its own cooldown like anyone else. The specialist makes a basic
attack against a single target — a close-range attack, so its reach is the first available
row like any close attacker, the enemy front line. The attack is weak — the intent is that
specialists help a little rather than being a full detriment to the battle. A specialist
has no special bar at all, and their attack damage works the way it does for anyone else.

## Enemy Targeting

Enemies pick a target from whatever they can reach. The choice is weighted by both how
much damage that target has dealt and how easy it is to kill. A taunt overrides both of
those factors until the taunted enemy's next hit — one attack, then it's spent.

## Equipment Durability

How gear wears down, what breaking costs a member in combat, and repair are covered in
the Equipment doc.

## Open Questions

- What does changing formation mid-battle cost the player, if anything?
- Does the fight run on a real-time clock, or in discrete ticks?
- How does Dexterity convert into cooldown speed, and does it cap?
- How many of the owner's own cooldown cycles do Vanish, Shields Up and the Mage's
  lingering field last?
- If the member whose effect it is dies partway through, does the effect go with them?
  The Mage's lingering field especially, since it sits on the battlefield rather than
  on the Mage.
- When does the player get to act, and does anything pause for them?
- Does the special bar still charge per attack, now that a faster attacker attacks more
  often?
- When a member's cooldown comes up, do all the strikes of a multi-strike attack resolve
  at once?
- How does Luck convert into the chance of an instant reset, and is it capped? A member
  whose Luck took the chance near certain would attack about twice as often.
- Does a free attack spend durability and charge the special bar the way a normal attack
  does?
- Do enemies get the Luck reset too, or is it a member-only advantage?
- When a free attack is a multi-strike attack, does it land all of its strikes?
- After a successful reset, can the member take another Luck check once their next
  cooldown has charged normally, or is there a longer lockout?
