# Guild Members

> **Status:** Early design. Nothing is built yet — the help percentages, both member
> ladders — ranks and tiers — and each type's stat weighting are settled, but what help
> applies to, and what a type advantage is worth, are not.

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

## Base Stats

The power of the fighting members is based on five base stats:

- Strength
- Dexterity
- Constitution
- Intelligence
- Luck

Dexterity is also the speed attribute: it's what determines turn order in combat.

A member's defence comes from Constitution plus their equipment.

There is no minimum damage — enough defence can reduce a hit to nothing.

A member's evasion comes from Dexterity and Luck.

An attack can miss an evasive target. Area attacks — the AoE effects — can't miss: they
land on a space rather than on a person, so evasion does nothing against them. They do
pay a reduced defence, though: defence still applies to them, but at less than its usual
value.

Strength drives physical damage; Intelligence drives magic damage.

## Starting Stats

A newly recruited member's starting stats are set by its type and its rank or tier. The
type sets the shape of those stats; the rank or tier sets their magnitude — so a C-rank
hire starts higher across the board than an F-rank one.

## Levels and Experience

Each level a member gains increases one base stat. Which stat goes up is weighted
random — a member's type makes certain stats more likely but not guaranteed, so members
of the same type turn out slightly different from each other. Specialists gain base
stats the same way divers do, and their specialty improves alongside.

Experience is awarded per floor: once a floor's battles resolve, experience is the number
of enemies defeated by the party divided by the number of party members, counting
specialists.

## Stat Weighting by Type

Each type has an ordering of all five base stats, from most likely to gain on a
level-up through least likely.

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

## Specialists

Specialist types include Porter, Cook, Scout, Herbalist, Miner, Blacksmith, Armourer, and
Alchemist. That list isn't complete.

## Party Size

The maximum number of members on a team is 15, including specialists. The player might not
want to take that many every time, because there could be penalties incurred with AoE, and
because of possible dungeon effects — a detail that isn't fully worked out yet.

## Open Questions

- What is having a type advantage actually worth in a fight?
- What does a support bonus increase — damage, the base stats, or something else?
- Does the experience a defeated enemy is worth scale with dungeon depth?
