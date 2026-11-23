# Specialists

> **Status:** Early design. Nothing is built yet — every specialist type is gated by guild
> rank, and the schedule of which rank unlocks which is set.

## Recruiting

Every specialist type is gated by guild rank, and the unlocks are front-loaded into the
first three ranks — the player needs access to the supports early, so that the chance to
level them up is available.

- F — the Cook and the Porter
- E — the Scout, the Herbalist and the Miner
- D — the Armourer, the Alchemist and the Blacksmith

The guild can hold more than one of a specialist type.

## Tiers

Specialists don't use the F → SSS rank ladder. They have nine tiers of their own, and use
them instead of ranks — not as well as them. The full tier ladder, in order:

Novice → Apprentice → Journeyman → Adept → Master → Grandmaster → Grandmaster S →
Grandmaster SS → Grandmaster SSS

A tier stands in for a rank wherever a rank is compared to something else — the two
ladders both have nine rungs, so they line up rung for rung: Novice sits where F sits,
Grandmaster SSS where SSS sits.

Promoting a specialist works exactly the way a diver's rank up does.

For a specialist, promotion makes the same ability stronger.

Each specialist type's stat weighting is covered in the Guild Members doc.

## Equipment

A specialist has no equipment — no weapon and no armour. So a specialist's defence comes
from Constitution alone.

## The Porter

A Porter carries the base 5 slots any member carries, plus 5 for each tier it has
reached. The slot system itself is covered in the Dungeon doc.

- Novice — 10 slots
- Apprentice — 15
- Journeyman — 20
- Adept — 25
- Master — 30
- Grandmaster — 35
- Grandmaster S — 40
- Grandmaster SS — 45
- Grandmaster SSS — 50

## The Cook

The Cook heals a little between floors — another five per cent — and substantially more at
a rest area — a further fifteen per cent — on top of what the party gets anyway.

At the mead hall, a Cook heals a member by the amount of the Cook's own highest stat —
a flat number of health points, not a percentage. That heal lands once a minute, the
same beat healing runs on with no Cook at all, so each heal's gold cost — set by the
Cook's own tier — is a cost per minute rather than a one-off:

- Novice — 1 gold
- Apprentice — 5
- Journeyman — 10
- Adept — 15
- Master — 20
- Grandmaster — 25
- Grandmaster S — 30
- Grandmaster SS — 35
- Grandmaster SSS — 40

Each heal also makes a Luck check, a pull from the Cook's own Luck bag — see the Combat
doc for how a Luck check and its bag of fifty work. A True fully heals that member and
costs no gold at all.

The mead hall itself is covered in the Core Concept doc.

## The Scout

The Scout can "Search" the next 5 floors for the party and give an idea of what is coming.
It is not a guarantee. The Scout can Search at rest areas.

## The Herbalist and the Miner

The Herbalist and the Miner both increase yield, on above-ground missions and on dives
alike — the Herbalist yields herbs, the Miner minerals. Each carries the base 5 slots
any member carries, plus extra slots restricted to its own yield — herbs only for the
Herbalist, minerals only for the Miner — that grow by 5 a tier. The slot system itself is
covered in the Dungeon doc.

- Novice — 5 regular and 5 restricted
- Apprentice — 5 and 10
- Journeyman — 5 and 15
- Adept — 5 and 20
- Master — 5 and 25
- Grandmaster — 5 and 30
- Grandmaster S — 5 and 35
- Grandmaster SS — 5 and 40
- Grandmaster SSS — 5 and 45

## The Blacksmith

The Blacksmith makes weapons. On a dive, the Blacksmith can repair damaged gear in the
field, between battles — weapons, consistent with its trade.

The quality of the weapons the Blacksmith makes follows its tier — a grandmaster makes
better weapons than an apprentice.

## The Armourer

The Armourer makes armour. On a dive, the Armourer can repair damaged gear in the field,
between battles — armour, consistent with its trade.

The quality of the armour the Armourer makes follows its tier.

## The Alchemist

The Alchemist makes potions. Potions come in two kinds: temporary buffs, which raise
stats for a fight, and healing potions, which restore health. At a rest area, the
Alchemist can brew from what the party has gathered.

- Wind Step — raises Dexterity.
- Dragon's Vein — raises Strength.
- Rock Skin — raises Constitution, but it reaches defence only — it does not raise the
  member's health.
- Ancient Gift — raises Intelligence.
- God's Wish — turns 2 of the member's Luck bag's Falses into Trues, rather than
  raising Luck the way the other four raise their stat. See the Combat doc for how a
  Luck bag and its Trues work.

A converted True is spent when it's drawn, turning back into a False, and any of the two
still unspent when the battle ends turn back as well — the potion reaches no further
than the battle it was drunk for.

A buff is used by the player, not drunk by a member, so using one costs no member an
attack, and it reaches every member of the party rather than just one.

A healing potion restores a number of health points, from a band set by its rank:

- F — 10 to 25
- E — 25 to 60
- D — 60 to 115
- C — 115 to 190
- B — 190 to 285
- A — 285 to 400
- S — 400 to 535
- SS — 535 to 690
- SSS — 690 to 865

Each band starts where the one below it ends, and each is 20 points wider than the one
below.

A potion's strength scales with the Alchemist's Intelligence, so a cleverer Alchemist
brews stronger potions.

The Alchemist's Luck gets a check of its own, the same bag-pull check a crafted weapon
or piece of armour gets — see the Equipment doc for how a True and a second True raise
what gets brewed. Together with Intelligence, that's what places a potion inside its
band and raises it — the same shape as a crafter's main stat and Luck for gear.

## Open Questions

- A weapon and a piece of armour each roll from a band for their kind and class — what
  does a buff potion roll: how much it raises a stat by, and whether it has bands of
  its own?
- There are five buffs and each reaches the whole party. It isn't said whether more
  than one can be in effect at a time, or whether two of the same buff stack or the
  second simply replaces the first.
