# Combat

> **Status:** Early design. Nothing is built yet — the grid, the cooldown pacing,
> Dexterity's conversion into cooldown ticks, the tick-based simulation, and that the
> fight never pauses for the player are settled, but how the Luck reset's chance works
> isn't.

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

The fight is simulated in discrete ticks. Everything the simulation counts — a cooldown,
an effect's remaining cycles, a durability count — is a whole number, never a fraction of
one. What the player watches is continuous motion; the ticks themselves are never drawn
on screen. The simulation stays whole numbers because a fight built that way can be
reasoned about and balanced — a fight with fifteen guild members and a facing force of
enemies run on a continuous clock would be far harder to balance, and far harder to
chase a bug through.

A cooldown is a number of ticks, and each combat type has its own base wait: the Brute
and the Tank wait 180 ticks, the Fighter and the Mage 140, and the Rogue and the Archer
100. The wait is that base divided by (1 + Dexterity ÷ 20), rounded to whole ticks — the
simulation counts in whole ticks, as this section already says. It never goes below a
floor of a tenth of the type's own base, however high Dexterity climbs: 18 ticks for a
Brute or Tank, 14 for a Fighter or Mage, 10 for a Rogue or Archer. That floor is reached
at Dexterity 180 whatever the type.

A worked list for the Rogue, base 100:

- Dexterity 5, a newly recruited F-rank member — 80 ticks
- Dexterity 20 — 50 ticks
- Dexterity 80 — 20 ticks
- Dexterity 180 and above — 10 ticks, the floor

The conversion divides rather than subtracts because Dexterity starts single-digit and
climbs for thousands of levels, so anything that subtracts from a flat wait either does
nothing early or runs past zero later. Dividing gives a new member a visible gain from
their first few points while a veteran needs ever more for ever less.

The floor is there because without it the fast types would run away with the fight — a
member with Dexterity in the hundreds would act many times over for each attack a slow one
lands. The floor compresses that gap at the top, so the slower types keep gaining after
the fastest have stopped. That protects the deliberate slowness of the Brute and the
Tank, which this doc already states is intended.

Because the base and the floor are both properties of the type, the ratio between a slow
type and a fast one holds at every point on the curve — a Brute waits the same multiple of
a Rogue's wait at Dexterity 5, at Dexterity 80, and at the floor. That makes the
deliberate slowness of the Brute and the Tank structural rather than something that only
shows early.

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

The fight never pauses, and nothing waits for the player. It runs from start to finish,
and the player acts while it's running — using a member's special once that bar is full,
changing formation, and marking the focus target.

The fight doesn't wait for the player, so the moment to use a special goes by while the
fight carries on around it.

## Attacks and Reach

Characters and enemies have either close-range or far-range attacks, with possible AoE
effects. Close-combat reach is the first available row: if the first row has been removed,
the second row can then be hit. A far-range attack can reach any row on the enemy's grid.

Each strike of a multi-strike attack is resolved on its own: it rolls to hit separately,
and defence is subtracted from it separately.

## The Special Bar

Each member has a special bar. When it's full, the player can use a special. Every attack
a member makes charges that member's bar — that's the base, and it's the same for every
type. The bar charges per attack, not per strike: a multi-strike attack charges it once,
the same as a single-strike attack does. So a member that attacks more often charges
faster, and the slower-attacking types charge more slowly. Each combat type also has its
own bonus condition that charges its bar on top of that — covered in the Individual Types
doc.

The bar caps at full — the special is never lost, and it waits until the player uses it.
While it sits full, charge is wasted: attacks the member makes while full charge nothing,
and so does the type's bonus condition — that progress toward the next special is gone.
Using the special empties the bar, and it charges again from there.

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
- How much real time is a tick worth — how fast does the simulation run against what the
  player is watching?
- Can the player speed a fight up or slow it down, and does that change anything in the
  simulation or only how fast it's drawn?
- How many of the owner's own cooldown cycles do Vanish, Shields Up and the Mage's
  lingering field last?
- If the member whose effect it is dies partway through, does the effect go with them?
  The Mage's lingering field especially, since it sits on the battlefield rather than
  on the Mage.
- With a party of fifteen filling bars while the fight runs, how does the player see
  which specials are ready at a glance?
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
