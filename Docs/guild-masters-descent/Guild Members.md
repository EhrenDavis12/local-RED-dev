# Guild Members

> **Status:** Early design. Nothing is built yet — the help percentages and what they
> apply to, both member ladders — ranks and tiers — each type's stat weighting, and how
> a type advantage works are settled, but whether the six advantages are worth the same
> isn't.

## Combat Types

Divers, the fighting members, have a combat type, and certain types are stronger and
weaker against others, in the style of rock-paper-scissors. The combat types break into
two triangles.

The first triangle:

- Brute has advantage on Tank
- Tank has advantage on Fighter
- Fighter has advantage on Brute

The second triangle:

- Rogue has advantage on Archer
- Archer has advantage on Mage
- Mage has advantage on Rogue

A type advantage isn't a multiplier added on top of an attack. Each matchup comes out of
rules already in play — evasion against a single shot, defence subtracted from every
strike separately, area attacks that can't be dodged, and how much defence each kind of
armour adds. Each matchup's own mechanism is covered in the Individual Types doc.

## The Support Ring

This is about the six combat types helping each other in battle — not the specialists like
Porter and Cook. The two triangles overlap by providing support to each other, in a ring:

- Tank helps Archer
- Archer helps Fighter
- Fighter helps Mage
- Mage helps Brute
- Brute helps Rogue
- Rogue helps Tank

Help gives a benefit that increases power. It applies when the two members are located
next to each other on the battle map — diagonals count as being next to each other. It's
many-to-many: a member can give help to multiple allies while receiving help from multiple
allies.

For example, an Archer standing behind two Fighters that are side by side gives both
Fighters a bonus. An Archer standing behind two Tanks receives a bonus from both of them.

The intent is to give the player a sense that they can balance how to support the guild
members. The full six-type ring is achievable but not always the best formation — against
an enemy force of, say, nine Brutes, the player might field more Fighters and Archers
instead for the best battle strategy.

## Diminishing Returns on Help

The bonus diminishes as the count of helpers grows, so surrounding a member isn't a
straight multiplication but a percentage increase. The first help is 5%. Each subsequent
help is 49% of the previous bonus — so the second help is 2.45%.

The bonus applies to the receiving member's primary stat — the stat its type's ordering
leads on. The first help rounds up to at least one point; every later help is exact, so
at low stats a later help can come to nothing.

## Base Stats

The power of the fighting members is based on five base stats:

- Strength
- Dexterity
- Constitution
- Intelligence
- Luck

Dexterity is also the speed attribute: it's what determines how fast a member's cooldown
is met in combat.

A member's damage comes from whichever of Strength, Dexterity or Intelligence its type
ranks highest, plus their weapon.

A member's defence comes from Constitution plus their equipment.

A member's health is their Constitution times ten — at F rank, where stats are
single-digit, that's a pool in the tens. It is what damage comes out of: whatever gets
through defence is taken off that pool. Because it comes from Constitution, it grows as
Constitution grows, with no separate rule for levelling. Constitution already means
toughness, so it is the pool and the base of defence both, and health needs no stat of its
own.

When a member's health reaches zero, they are dead. What that means in the dungeon is
covered in the Dungeon doc.

Damage is the stat plus what you carry, defence is the stat plus what you wear.

There is no minimum damage — enough defence can reduce a hit to nothing.

A member's evasion comes from Luck.

An attack can miss an evasive target. Area attacks — the AoE effects — can't miss: they
land on a space rather than on a person, so evasion does nothing against them. They do
pay a reduced defence, though: defence still applies to them, but at two-thirds of its
usual value.

## Weapons and Armour

What each combat type carries and wears, gear's quality, where it comes from, and how it
wears out are all covered in the Equipment doc.

## Starting Stats

A newly recruited member's starting stats are set by its type and its rank or tier. The
type sets the shape of those stats; the rank or tier sets their magnitude — so a C-rank
hire starts higher across the board than an F-rank one.

A newly recruited level-1 F-rank member starts with single-digit stats.

## Levels and Experience

A level-up raises three of a member's base stats by one each — three different stats,
chosen by the type's weighting, most likely through least likely. A member's type makes
certain stats more likely but not guaranteed, which is what makes members of the same type
turn out slightly different from each other.
Specialists gain base stats the same way divers do, and their specialty improves
alongside.

Experience comes from kills, and what a kill is worth is set by the defeated enemy's rank:

- F — 1
- E — 5
- D — 10
- C — 15
- B — 20
- A — 25
- S — 30
- SS — 35
- SSS — 40

The total is added up at the end of a combat and divided equally between all party
members, counting specialists.

## Stat Weighting by Type

Each type has an ordering of all five base stats. The ordering decides which three
stats go up on a level-up, from most likely through least likely.

- Brute — Strength, Constitution, Dexterity, Luck, Intelligence
- Tank — Constitution, Strength, Dexterity, Luck, Intelligence
- Fighter — Strength, Dexterity, Constitution, Luck, Intelligence
- Rogue — Dexterity, Luck, Strength, Constitution, Intelligence
- Archer — Dexterity, Strength, Luck, Constitution, Intelligence
- Mage — Intelligence, Dexterity, Constitution, Luck, Strength

- Porter — Strength, Constitution, Luck, Dexterity, Intelligence
- Cook — Constitution, Dexterity, Strength, Luck, Intelligence
- Scout — Dexterity, Luck, Constitution, Strength, Intelligence
- Herbalist — Luck, Dexterity, Constitution, Strength, Intelligence
- Miner — Constitution, Strength, Luck, Dexterity, Intelligence
- Blacksmith — Strength, Luck, Constitution, Dexterity, Intelligence
- Armourer — Constitution, Luck, Strength, Dexterity, Intelligence
- Alchemist — Intelligence, Luck, Dexterity, Constitution, Strength

## Promotion

Divers have their own rank, separate from guild rank and mission rank, on the same
ladder: F → E → D → C → B → A → S → SS → SSS. Specialists don't use that ladder —
instead they climb nine tiers of their own, named in the specialists doc.

To promote a member, the member must reach the level threshold, and the player must pay
gold for the official promotion — both are required. Promotion resets the member's level
to 1; the stats already earned are kept, and only the level counter resets.

A member stops gaining levels once they reach the threshold for their next rank or tier,
and stays there until the player pays the gold for the official promotion — so neglecting
a promotion wastes the experience the party keeps earning in the meantime.

The level a member needs doubles at each promotion: the first is level 16, the second is
32, and so on — 16, 32, 64, 128, 256, 512, 1024, 2048. The same eight thresholds serve
both ladders — nine tiers means eight promotions, exactly as many as nine ranks.

Crossing a rank also costs a set amount of experience, multiplying by five at each step:

- F to E — 20
- E to D — 100
- D to C — 500
- C to B — 2,500
- B to A — 12,500
- A to S — 62,500
- S to SS — 312,500
- SS to SSS — 1,562,500

## Specialists

Specialist types include Porter, Cook, Scout, Herbalist, Miner, Blacksmith, Armourer, and
Alchemist. That list isn't complete.

## Party Size

The maximum number of members on a team is 15, including specialists. The player might not
want to take that many every time, because there could be penalties incurred with AoE, and
because of possible dungeon effects — a detail that isn't fully worked out yet.

## Open Questions

- With each matchup working through its own mechanism rather than a shared multiplier, the
  six advantages aren't necessarily worth the same amount. Should they be, or is it fine
  for some matchups to bite harder than others?
- Crossing a rank costs a set amount of experience, and reaching the next rank also needs
  a level threshold — 16 levels for the first, doubling after. Does the experience buy
  those levels at an even rate, or do the two run on separate counters with whichever is
  slower deciding?
- The experience a rank costs multiplies by five each step, while what a kill is worth
  goes up by five a rank. Those don't keep pace: at around six enemies a fight and a party
  of six, F to E takes about twenty fights and SS to SSS takes about forty-four thousand.
  Which side gets tuned — the cost of a rank, or what a stronger enemy is worth?
- A rest floor is still a floor. Does arriving at one give the fifteen per cent only, or
  the five per cent for the floor as well?
- The Mage's lingering field damages what stands in it. Does that damage count as an area
  attack too, paying two-thirds defence, or is the reduction only for an attack that is
  aimed?
