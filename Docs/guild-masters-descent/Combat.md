# Combat

> **Status:** Early design. Nothing is built yet — the grid, the cooldown pacing, the Luck
> reset's chance, and the never-pausing simulation are settled; whether a fight can be
> sped up, how multi-strike cases resolve, what formation costs, how the bars read at a
> glance, and whether the enemy grid keeps filling are not.

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
shows early, and it's intended rather than something to be balanced away.

The pacing intent: a low-level fight feels a little slow at first, and a higher-level
fight has more going on, but a fight should take about the same real time at either end,
so combat stays fairly balanced across levels.

A tick is 50 milliseconds — twenty ticks a second. That turns the ticks above into waits
a player actually feels:

- A newly recruited F-rank Rogue, 71 ticks — about 3.6 seconds between attacks
- The same Fighter, 104 ticks — about 5.2 seconds
- The same Tank, 138 ticks — about 6.9 seconds
- A Rogue at the cooldown floor, 10 ticks — half a second
- A Tank at the floor, 18 ticks — just under a second

That's what stops the rate being changed casually: at F rank it makes a slow type's wait
deliberate without being tedious, and at the floor every type is acting about once a
second, which is the pacing this doc already asks for — a low-level fight feeling a little
slow and a higher-level one having more going on.

## The Luck Reset

When a member finishes an attack, there's a Luck check for whether the cooldown resets
instantly. On success, the member attacks again immediately, with no cooldown wait at all.
That free attack gets no Luck check of its own — that's what "only once" means, so the
effect can't chain into a second free attack. On failure, the cooldown charges normally.
Apart from costing no wait, the free attack is an ordinary attack in every way: all its
strikes land, it spends durability per hit the same as any other attack, and it charges
the special bar the same as any other attack. The member is eligible for a check again on
its very next attack, the one that charges its cooldown normally — the lockout runs no
further than the one free attack itself. Enemies get the Luck reset too, on the same terms
as guild members.

The chance is a quarter at most: 25% × Luck ÷ (Luck + 60). It approaches that quarter
without ever reaching it, so there's no cap rule and no point where Luck stops doing
anything — it just gets steadily less worth chasing.

A worked list:

- Luck 5, a newly recruited F-rank member — 2%
- Luck 20 — 6%
- Luck 60 — 12.5%, half the ceiling
- Luck 180 — 19%
- Higher still — closer and closer to 25%, never past it

The ceiling is there because a reset is a free attack, so the chance *is* the percentage
by which that member's attack rate goes up. A quarter is strong and clearly felt without
ever approaching the doubling that an uncapped chance would allow.

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
and the defender's mitigation is applied to it separately.

## The Special Bar

Each member has a special bar. When it's full, the player can use a special. An enemy's
bar works the same way, and an enemy uses its special when its bar is full. Each hit a
member lands charges that member's bar: the first hit of an attack charges it by 30,
and each additional hit — another strike of a multi-strike attack, or another
target the attack reaches — charges it by 5. That's the base, and it's the same for
every type. A bar fills on about the third hit once a bonus condition has fired, which
is what puts a special inside the fight that earns it rather than the one after. Each
combat type also has its own bonus condition, and each time it's met it adds 15 on top
of that base — covered in the Individual Types doc. The bar is full at 100.

Charge and weapon durability both count hits, so what wears a weapon down is what fills
the bar.

The bar caps at full — the special is never lost, and it waits until the player uses it.
While it sits full, charge is wasted: attacks the member makes while full charge nothing,
and so does the type's bonus condition — that progress toward the next special is gone.
Using the special empties the bar, and it charges again from there.

A part-filled bar carries from one battle to the next within a floor, and moving to the
next floor resets it to empty.

## Lasting Effects

Vanish, Shields Up and the Mage's lingering field all last three of the owner's own
cooldown cycles — the member whose effect it is. So "the same length" means the same
count, not the same stretch of real time: a fast member's effect is brief on the clock
while a slow member's runs long, and every member gets the same number of cycles of value
out of it. Three comes from Vanish: while it's up, the Rogue can't be targeted and
attacks can't miss, so every extra cycle is another free, unanswerable attack. Three is
enough to be decisive and short enough to stay a window rather than a phase, and the other
two take the same count from it. Each of the three is covered in the Individual Types doc.

A lasting effect ends when the member whose effect it is dies. That isn't obvious for
the two of the three that sit somewhere other than on their owner: the Mage's lingering
field sits on the battlefield rather than on the Mage, and Shields Up's defence sits on
the allies behind the Tank rather than on the Tank. The duration is a count of the
owner's own cooldown cycles, and a member who is dead completes no more of them, so
there's no clock left for the effect to run on.

## Specialists in Combat

A specialist attacks on its own cooldown like anyone else. The specialist makes a basic
attack against a single target — a close-range attack, so its reach is the first available
row like any close attacker, the enemy front line. The attack is weak — the intent is that
specialists help a little rather than being a full detriment to the battle. A specialist
has no special bar at all, and their attack damage works the way it does for anyone else.

## Enemies

Enemies are built from the same six combat types as guild members, working the same way.
What changes with a dungeon is tied to the dungeon's own rank: it sets both the rank of
the enemies found there and their chance of gear. An enemy is either the dungeon's own
rank or one grade below it, and no other grade — a C-rank dungeon fields C-rank and
D-rank enemies, nothing higher and nothing lower. The dungeon's rank also determines the
chance that an enemy carries a weapon and the chance that it wears armour.

Depth is a second dial, separate from rank. The deeper into a dungeon the player goes,
the more enemies turn up in each fight, and the better the equipment those enemies carry.
Think of it as the enemies getting luckier the deeper the dungeon runs — rank sets what
grade they are and whether they're equipped at all; depth decides how many show up and how
good that gear is. That luck is in the generation, not the stat — it only shapes how many
enemies and how much gear the fight creates; the enemies' own Luck stat is untouched,
exactly what their type and rank would otherwise give, so depth doesn't make them evade
more or reset their cooldowns more often.

## Enemy Targeting

Enemies pick a target from whatever they can reach. The choice is weighted by both how
much damage that target has dealt and how easy it is to kill. A taunt overrides both of
those factors until the taunted enemy's next hit — one attack, then it's spent.

## Equipment Durability

How gear wears down, what breaking costs a member in combat, and repair are covered in
the Equipment doc.

## Open Questions

- What does changing formation mid-battle cost the player, if anything?
- Can the player speed a fight up or slow it down, and does that change anything in the
  simulation or only how fast it's drawn?
- With a party of fifteen filling bars while the fight runs, how does the player see
  which specials are ready at a glance?
- When a member's cooldown comes up, do all the strikes of a multi-strike attack resolve
  at once?
- The enemy grid holds fifteen. When a floor is deep enough to fill it, do the enemies
  stop there, or do they keep coming?
- The dungeon board shows the types of monster and enemy found in a dungeon. Is a
  monster something other than an enemy built from the six combat types?
- When a fight starts, where do the cooldowns stand — everyone's empty and waiting out a
  full first wait, everyone's ready at once, or staggered somehow? The opening of a fight
  plays out completely differently depending on which.
- At F rank a member's Luck is single-digit, which puts the reset chance near one attack
  in forty — a member might see one reset in a whole dive. Is the reset meant to be that
  close to absent early on, or should the curve start higher?
- An enemy uses its special when its bar is full, but nothing says what decides the moment
  or the target. Does it fire as soon as it can, or hold while a better target is in
  reach?
- When two combatants come up on the same tick, what resolves first? A test run had a
  member attack and then die on the same tick, and the other order would have killed it
  before its attack landed.
- The Mage's field damages a character as that character begins its own attack. Does the
  field's damage resolve before the attack or after it? A test run had a member at 2
  health begin a special with a full bar, take 6 from the field, and die — so one order
  spends the special and the other erases it.
