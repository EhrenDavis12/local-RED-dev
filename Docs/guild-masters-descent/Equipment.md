# Equipment

> **Status:** Early design. Nothing is built yet — the weapon kinds and armour kinds, the
> quality ladder, each piece's two attributes, that a piece's figures are rolled from a
> band, condition, and how gear wears out and breaks are settled, but the bands aren't: no
> kind has a damage or defence band set at any class, apart from the one example here.

## What a Member Carries

Each combat type carries one kind of weapon and wears one kind of armour, and both kinds
are fixed by the type — neither changes over a member's life. What changes is their
quality.

The six weapon kinds, one per combat type:

- Fighter — two-handed swords, and only two-handed swords
- Brute — clubs
- Tank — short swords
- Archer — bows
- Mage — staffs
- Rogue — knives

How much damage a weapon adds depends on its kind, so the kinds differ from each other.

The six armour kinds, one per combat type:

- Tank — full armour
- Fighter — light armour
- Brute — tanned hide
- Rogue — hooded armour
- Archer — leather
- Mage — a robe

How much defence armour adds depends on its kind too. The Tank's full armour adds more
defence than the Brute's tanned hide, and the Fighter's light armour sits between the two.

A member's damage comes from whichever of Strength, Dexterity or Intelligence its type
ranks highest, plus their weapon. A member's defence comes from Constitution plus their
equipment. Damage is the stat plus what you carry, defence is the stat plus what you wear.

The weapon the Rogue carries adds less damage than the Fighter's. The Brute wears tanned
hide, which adds a little defence on top of its Constitution — less than a properly
armoured type has.

## Quality

Quality is the axis gear improves along, for armour as well as weapons. It uses the same
nine-rung ladder as guild rank, diver rank and specialist tiers: F → E → D → C → B → A →
S → SS → SSS.

A weapon carries two attributes: an Attack Damage range and a Durability. Each kind of
weapon has its own Attack Damage range, and so does each class — the ranges differ per
kind so the damage comes out balanced across the combat types. But a weapon's range is not
a fixed figure for its kind and class: each kind at each class has a wider band, and an
individual piece's own range is drawn from inside that band when the piece is made, so two
pieces of the same kind and class are not the same. The bands for neighbouring classes
overlap, so a well-rolled piece of a lower class can be better than a poorly-rolled piece
of a higher one. An F-class knife, for instance, draws from a band of 2–12, so one F-class
knife might come out 10–12 while another comes out 2–4. One individual weapon's rolled
range might come out 4–6, and when that member attacks, 4–6 is what the weapon adds to the
damage calculation.

Durability works the same way: a piece's Durability is drawn from a band for its kind and
class rather than being a fixed figure, and the individual piece's figure is rolled from
that band when the piece is made. Once rolled, it counts down by hits, not by attacks:
each hit the weapon lands spends one use, and an attack that misses spends none. Because
the kinds land different numbers of hits per attack, durability is balanced per weapon
kind to make the kinds come out even — a kind that strikes many times per attack needs
a higher durability figure than a kind that strikes once. The weapon breaks when it
reaches zero.

Armour carries two attributes as well, the same shape as a weapon's pair: a Defence range
and a Durability. Defence is a range, the way Attack Damage is a range, and not a single
figure — how much damage reduction the armour gives, and it's drawn from a band the same
way a weapon's range is. Armour's durability works the same way a weapon's does: it
counts down by hits taken, not by attacks faced, and a missed attack spends none of it.

Both ranges roll separately for every strike of a multi-strike attack: the attacker's
Attack Damage range is rolled afresh for each strike, and because each strike already
resolves on its own — rolling to hit separately and subtracting defence separately —
the defender's Defence range is rolled per strike as well.

The shop sells equipment of a baseline quality, and that baseline rises with guild rank. A
crafter in the guild produces better than the shop's baseline.

Weapon quality follows the Blacksmith's tier and armour quality the Armourer's — a
grandmaster makes better weapons than an apprentice.

## Where Gear Comes From

The guild gets equipment from the shop and from crafting.

The shop is available from rank F, where the player can buy items and equipment.

Crafting is something the guild has only by holding a Blacksmith or an Armourer — the
Blacksmith and the Armourer unlock at guild rank D.

Materials feed better equipment: some missions are hunts for materials to make better
equipment, and dives yield materials or items.

## Assignment

Gear sits in the guild's stores rather than belonging to any one member; the player
assigns pieces to members from there.

A specialist has no equipment — no weapon and no armour — so a specialist's defence comes
from Constitution alone.

## Durability

Gear wears down as it is used — weapons degrade from attacking, armour from being hit. It
works fully until it reaches zero, then breaks and contributes nothing — there is no
gradual decline before that.

A piece's condition reads its durability as a percentage of its maximum:

- Good — above 50%
- Worn — 25% to 49%
- Ragged — 1% to 24%
- Broken — 0%

Condition tells the player how close a piece is to breaking and nothing more. Durability
does not affect the damage or defence a piece adds unless it is broken — a ragged sword
adds exactly what a good one of the same kind and class adds. That agrees with the rule
above: gear works fully until it reaches zero, with no gradual decline before that, and
condition just names where a piece sits on the way there.

Broken armour means the member's defence falls back to Constitution alone.

A broken weapon stops being added to the attack at all — the member's damage falls back to
their stat alone. They still attack, and their combat type's attack shape still applies —
a Brute with a broken weapon still cleaves, just feebly. At early levels this is a minor
inconvenience, since the weapon adds little to the calculation to begin with — but once
damage is in the hundreds or thousands, what the weapon was adding means a lot.

Both a weapon and an armour can break partway through a multi-strike sequence, so later
strikes in the same attack can deal or face different damage than earlier ones.

## Repair

Repairs happen in the guild hall between dives.

A Blacksmith or Armourer in the party can also repair in the field, between battles — a
convenience rather than a requirement, and each is scoped to its own trade: the Blacksmith
repairs weapons, the Armourer armour.

Field repair only works on gear that is still above zero. Once an item breaks it stays
broken for the rest of the dive; a Blacksmith or Armourer in the party cannot bring it
back.

## Open Questions

- How much does a step of quality add to armour's defence?
- How much better than the shop's baseline is a crafter's work?
- What does a repair in the guild hall cost?
- How much does a field repair restore, and does the Blacksmith's or Armourer's tier
  change that? Can the guild hall fix a piece that broke on the dive, or is a broken piece
  gone for good?
- Does the dungeon or a mission ever drop a weapon or a piece of armour, or is gear only
  bought and crafted?
- What does crafting consume, and how long does it take? Can a crafter work while out on a
  mission or a dive?
- When the guild holds two Blacksmiths, whose tier sets the weapon quality?
- When a member dies in the dungeon, what happens to the gear they were carrying?
- Does a newly recruited member arrive with gear, or fight unarmed until the player
  assigns some?
- Is there anything stopping the player handing the best gear in the stores to an F-rank
  diver?
- Where does the player assign gear, and how much of a piece does the player see — exact
  numbers, or a rough impression the way the recruiting board shows a candidate's
  strengths?
- Are the six kinds of weapon in a fixed order of damage?
- How is a piece's own range picked out of its band — is the span always the same width,
  with only where it sits rolled, or can one piece have a wider span than another?
- Are a piece's range and its durability rolled once when the piece is made and fixed
  for the life of that piece?
- Does a crafter beat the shop's baseline by rolling higher inside the band, or by
  producing a higher class outright?
- Where do the Rogue's hooded armour, the Archer's leather and the Mage's robe sit
  against full armour, light armour and tanned hide?
