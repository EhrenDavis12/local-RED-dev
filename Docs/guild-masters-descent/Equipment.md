# Equipment

> **Status:** Early design. Nothing is built yet — the kinds, the quality ladder, the
> bands for damage, defence and durability, wear and breaking, and repair are settled,
> but how crafting and repair are costed, how a roll is made, and what the player is
> shown of a piece isn't.

## What a Member Carries

Each combat type carries one kind of weapon and wears one kind of armour, and both kinds
are fixed by the type — neither changes over a member's life. What changes is their
quality.

The six weapon kinds, one per combat type:

- Fighter — two-handed swords, and only two-handed swords
- Brute — axes
- Tank — war hammers
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
Each kind of armour can only be worn by its own combat type, so the player never chooses
between kinds.

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
pieces of the same kind and class are not the same. The span itself is rolled too, not
just where it sits in the band — one piece's range can come out wider or narrower than
another's, not only higher or lower within it. A span is never narrower than a quarter
of its band and never wider than half of it, so no piece comes out as a single flat
figure and none spans its whole band.

Each kind's F-class Attack Damage band, in ascending order:

- Knife, the Rogue's — 2–12
- Staff, the Mage's — 3–15
- Two-handed sword, the Fighter's — 4–16
- Axe, the Brute's — 4–18
- War hammer, the Tank's — 5–21
- Bow, the Archer's — 6–26

A band is set by how much work one strike has to do: a kind that strikes more than once in
an attack, or lands on more than one enemy, carries a smaller band than one putting
everything into a single hit on a single target.

Each class doubles the band below it — E is double F, D double E, and so on up the nine
rungs to SSS. The knife's F-class band of 2–12 doubles to an E-class band of 4–24, and by
the time it reaches SSS it has doubled all the way to 512–3072. That doubling is also why
the bands for neighbouring classes overlap: an E-class band starts inside the F-class band
it sits above, so a well-rolled piece of a lower class can be better than a poorly-rolled
piece of a higher one. An F-class knife, for instance, might come out 10–12 while another
comes out 2–4, and whatever range a piece rolls is what that weapon adds when the member
attacks.

Durability works the same way: a piece's Durability is drawn from a band for its kind and
class rather than being a fixed figure, and the individual piece's figure is rolled from
that band when the piece is made. Once rolled, it counts down by hits, not by attacks:
each hit the weapon lands spends one use, and an attack that misses spends none. Because
the kinds land different numbers of hits per attack, durability is balanced per weapon
kind to make the kinds come out even — a kind that lands more hits in an attack needs a
higher durability figure than a kind that lands fewer, and what's counted is hits landed,
not strikes made: the Brute's cleave and the Mage's column land three hits from one
strike, the same as a kind that strikes three separate times. The weapon breaks when it
reaches zero.

Each kind's F-class Durability band, grouped by how fast the kind spends durability —
usually the hits it lands in one attack, but for the bow, how often it attacks:

- War hammer, the Tank's — 40–80. One strike on one target, so one hit an attack.
- Knife, the Rogue's, two-handed sword, the Fighter's, and bow, the Archer's — 80–160.
  The knife and sword land two hits an attack; the bow lands one hit, but the Archer
  attacks about twice as often as the Tank, so it spends durability just as fast.
- Axe, the Brute's, and staff, the Mage's — 120–240. One strike, but it lands on three,
  so three hits an attack.

A band follows how fast a kind spends durability — both the hits it lands in an attack
and how often it attacks — so that no kind runs out markedly sooner than the others.

Unlike the damage bands, a kind's Durability band is the same at every class — an SSS
weapon is no more durable than an F one; what it has is a far bigger damage band. Higher
floors mean tougher enemies and longer fights, so durability that grew with class would
simply cancel out, and gear breaking is meant to go on mattering at every rank rather
than only early. It also means losing a weapon hurts more the better it is, which agrees
with the rule above: a broken weapon costs little early and a great deal once damage is
in the hundreds or thousands.

Armour carries two attributes as well, the same shape as a weapon's pair: a Defence range
and a Durability. Defence is a range, the way Attack Damage is a range, and not a single
figure — how much damage reduction the armour gives, and it's drawn from a band the same
way a weapon's range is. Armour's durability works the same way a weapon's does: it
counts down by hits taken, not by attacks faced, and a missed attack spends none of it.

Each kind's F-class Defence band, in ascending order:

- Robe, the Mage's — 1–6
- Hooded armour, the Rogue's — 2–8
- Tanned hide, the Brute's — 2–9
- Leather, the Archer's — 3–10
- Light armour, the Fighter's — 5–16
- Full armour, the Tank's — 6–18

Armour covers roughly a third of a typical strike at the same class, with Constitution
on top of it — that keeps defence meaningful against every incoming strike without
zeroing hits out as a matter of course. The ladder is the same as the weapons': each
class doubles the band below it, up all nine rungs, so defence keeps pace with damage.

Armour's Durability band is the same for every kind: 60–120. Unlike the weapons, armour
isn't grouped by kind — there's nothing to group by. A weapon's band follows the hits it
lands in an attack, which runs from one to three depending on the kind, but every kind of
armour takes hits the same way, so the thing that organised the weapon bands has nothing
to organise here.

Where it sits follows how much more slowly armour wears than a weapon does: a member lands
one to three hits an attack but only takes hits when an enemy chooses them, spread across
a party of up to fifteen. 60–120 sits between the one-hit weapon band at 40–80 and the
two-hit band at 80–160, putting a typical member's armour at roughly a weapon's lifetime.
Like weapon durability, it doesn't change with class — the same band at F as at SSS.

A piece's Attack Damage, its Defence and its Durability are each rolled once, at
creation, and fixed for the life of that piece.

Each strike also carries the member's own damage stat in full, the same as its weapon roll
— the stat isn't split between the strikes of an attack. Both ranges roll separately for
every strike of a multi-strike attack: the attacker's Attack Damage range is rolled afresh
for each strike, and because each strike already resolves on its own — rolling to hit
separately and applying the defender's mitigation separately — the defender's Defence
range is rolled per strike as well.

The shop sells equipment of a baseline quality, and that baseline rises with guild rank. A
crafter in the guild produces better than the shop's baseline.

Weapon quality follows the Blacksmith's tier and armour quality the Armourer's — a
grandmaster makes better weapons than an apprentice. The tier decides which class the
crafter makes at. Within that class, it's the crafter's own main stat that sets where in
the band the piece lands — the Blacksmith's Strength on a weapon, the Armourer's
Constitution on armour.

Luck then gets a check of its own, a pull from the crafter's own Luck bag: a False and the
piece is made normally, at the quality its main stat set. A True raises the piece's
quality by moving its span half the remaining distance to the top of its band — it
scales itself, so a poor roll gains a lot and a roll already near the top gains little,
and it can never overshoot the band, so nothing has to cap it. A second pull follows: a
second False holds the raise where it landed, a second True takes the span the rest of
the way, to the very top of the band, keeping its rolled width. If the piece was already
at that maximum before the check, a second True instead bumps it up to the next class,
landing at the top of that class's band rather than the bottom — the bands overlap, so
the bottom of the next class sits below the top of the one below it, and landing there
would be a downgrade.

When the guild holds more than one Blacksmith, it is the Blacksmith assigned to the smithy
whose tier, Strength and Luck set the weapon quality.

## Where Gear Comes From

The guild gets equipment from the shop, from crafting, and from drops.

The shop is available from rank F, where the player can buy items and equipment.

Crafting is something the guild has only by holding a Blacksmith or an Armourer — the
Blacksmith and the Armourer unlock at guild rank D. A craft takes real time and runs on
the same clock as missions, carrying on while the game is closed. How long depends on
the piece's class — a low-class piece takes minutes, a high-class one takes hours. A
crafter away from the hall is not crafting — the Core Concept doc covers the stations.

Gear can drop too: both the dungeon and missions can drop a weapon or a piece of armour,
alongside the materials and items they yield. Dropped gear is rolled the same way a
crafted or bought piece is, and its class comes from where it dropped — from the
dungeon's own rank and how deep the floor is for a dungeon drop, and from the mission's
rank for a mission drop.

Materials feed better equipment: some missions are hunts for materials to make better
equipment, and dives yield materials or items.

## Assignment

Gear sits in the guild's stores rather than belonging to any one member. The player
assigns weapons and armour to members in the Dorms, a part of the guild hall where they
see a piece's stats and hand gear to members.

Nothing stops the player giving a member gear of a higher class than the member's own
rank — a C-class piece on an F-rank diver is allowed.

A specialist has no equipment — no weapon and no armour — so a specialist's defence comes
from Constitution alone.

A newly recruited member has a chance to arrive already carrying gear, but not always.

If a member dies in the dungeon, the party brings their gear back if there's room left
in the party's carrying capacity — the same capacity the Porter adds a lot of and any
member contributes to by carrying some of the loot; otherwise the gear is lost.

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

A special spends none of the attacker's own weapon durability, however many hits it
lands — the Fighter's flurry, the Archer's Volley, the Brute's two-row cleave and the
Mage's field cost the weapon nothing. Armour spends durability for every hit it takes
regardless, whoever lands it and whether it came from an ordinary attack or a special: a
weapon only wears from ordinary attacks, armour wears from everything.

## Repair

Repairs happen in the guild hall between dives. Repairing a piece that still has
durability left costs gold; fixing a piece that has broken costs gold and materials
both. The gold a repair costs scales with the piece's class, the way its damage and
defence bands do.

A Blacksmith or Armourer in the party can also repair in the field, between battles — a
convenience rather than a requirement, and each is scoped to its own trade: the Blacksmith
repairs weapons, the Armourer armour. How much a field repair restores is decided by the
repairing specialist's rank.

Field repair only works on gear that is still above zero, and once a piece breaks it
stays broken for the rest of the dive — a Blacksmith or Armourer in the party cannot bring
it back there. Back at the guild hall, though, a broken piece can be fixed, for gold and
materials.

## Open Questions

- Crafting a piece and fixing a broken one both take materials, and it isn't said which
  kinds or how many either needs.
- Does the player see a piece's exact rolled range and durability in the Dorms, or only a
  rough impression the way the recruiting board shows a candidate's strengths?
