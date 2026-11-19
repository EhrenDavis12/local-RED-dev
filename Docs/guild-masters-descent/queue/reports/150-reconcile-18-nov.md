# #150 — Reconcile with the docs owner's 18 Nov edits

> **Status:** done 2026-11-18 · owner commits 96da7c9..489a267

## What the owner changed

- **Combat** — when a member's cooldown comes up, the player can have it drink a healing
  potion instead of attacking; drinking costs that attack. New open question: does a member
  drinking in a Mage's field take the field's damage?
- **Equipment** — a crafted piece's place in its band comes from the crafter's main stat
  (Blacksmith Strength, Armourer Constitution), then a Luck-bag pull: True moves it half
  the way to the top, a second True to the top, or up a class if it was already there.
- **Specialists** — Porter 5 slots + 5 a tier; Herbalist and Miner 5 slots + restricted
  slots for their own yield, 5 a tier; healing potions heal from a band by rank (F 10–25 …
  SSS 690–865); the Alchemist's Intelligence and a Luck pull place a potion in its band.
- **The Dungeon** — capacity is counted in slots, 5 a member; a healing potion and an item
  of loot take 1 slot each; potions are loaded into it at the start of the raid.

## What changed on our side

EhrensDocs change notes reconciled to the originals (15 findings): the one-potion-per-member,
auto-drink-under-30%, free-drink and heal-30% notes are gone; the gold carry limit (10 a
member, 100 a Porter) is gone; Open Questions on the Porter's gold and the Herbalist/Miner
are struck. Our one kept rule is untouched: attacks never land at once — on the same tick,
one attacks and then the other.

## Build rows

Already queued by the desk: **#151** carrying in slots, **#152** healing potions by rank and
drinking instead of attacking. Added from the gap check:

- **#155** a fallen member's gear comes home only if there are free slots [prd] [S]
- **#156** packing potions into slots on the party planning screen [look] [S]
- **#157** the drink button on a member's battle card [look] [S]
- **#158** full auto drinks below 30% health [look] [S]

Not queued: crafting by main stat + Luck pulls, Alchemist brewing, and the Herbalist and
Miner — the Focus leaves crafting and the other specialists out of the first version.
#151's and #152's titles include the Herbalist/Miner and Alchemist parts; their builders
should check the Focus before building those.

## Defaults the builds go ahead with

Recorded as going-ahead questions on #151 and #152: gold takes no slots; each member drinks
from its own slots; a played mission packs potions like a dive; a member drinking in a
Mage's field still takes the field's hit; the shop sells F-rank potions.

## Open Questions

- Does a dead member's gear take slots, and how many? #155 builds one a piece as a
  placeholder.
- Do potions and loot compete for slots during the dive, or only on the way out?
