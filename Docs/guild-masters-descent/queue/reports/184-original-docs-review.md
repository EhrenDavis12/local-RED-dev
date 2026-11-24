# #184 — The other developer's 20–23 Nov doc edits, against EhrensDocs and the game

> **Status:** Research report for queue item #184, 2026-11-24. Parks on the user's calls below.

## What changed in the originals

Fifteen commits by the other developer since the 18 Nov reconcile (`git log 14e5952..HEAD
--author=royda`), across every original doc. The new or changed rules:

- **Specials** fire on their own the moment a bar fills, for both sides, once the attack that
  filled it has resolved, and take no action of their own (Combat, The Special Bar).
- **Targeting** is one rule for both sides; a far-range attacker also weighs how far back a row
  sits, so it shoots past the front line (Combat, Targeting).
- **Shields Up** doubles the Tank's unshielded defence; allies behind gain that figure; a
  re-cast refreshes the shield (Individual Types, The Tank). The **Brute** now quarters a
  Tank's defence.
- **Rogue** draws up to two evasion tokens against an Archer (Combat, Luck).
- **Gear span** is a quarter to a half of its band (Equipment).
- **Dungeon** floors have 1–3 battles and spend a power budget on their enemies; enemy stats
  spread 8:7:6:5:4; enemy types grow per set of four floors; a kill pays for what the enemy
  cost; 1 enemy in 4 drops something (The Dungeon; Guild Members).
- **Health** lost on a dive heals 1 point a minute at home, also while the game is closed; the
  **mead hall** with a Cook station heals faster for gold (Core Concept, The Mead Hall;
  Specialists, The Cook).
- **Alchemist**: five buffs, one per stat, God's Wish, potion bands by rank; home-trade
  stations for every trade (Specialists; Core Concept).
- **Battle Test**: the fixture stays a hand-set bench; 15 level-ups at F.

## EhrensDocs, brought in line

The originals win, so every EhrensDocs change note the originals now answer — the same way or
differently — was deleted or cut back, leaving only the gaps the originals don't answer
(41 edits across ten files, committed with this report). Six questions in EhrensDocs Open
Questions were removed as answered: enemy strength, enemy types, tapping a special, the
Mage's field, what a found dungeon holds, experience a level. Our one rule that beats the
originals — attacks never land at the same moment — stays.

## Where the game is now wrong

The game was built to the EhrensDocs rules that just gave way. Each is a queued fix:

| Rule in the originals | Game today | Queued |
|---|---|---|
| Specials fire themselves when the bar fills | The player arms them; they replace the next attack (`Battle.cs:436`, `BattleController.cs:29`) | #185 |
| Brute quarters Tank defence | Halves it (`BruteType.cs:22`) | #186 |
| Shields Up doubles unshielded defence, re-cast refreshes | Flat +3, re-casts stack (`TankType.cs:22-27`) | #186 |
| Rogue draws two tokens against an Archer | One (`Battle.cs:723`) | #186 |
| Far-range targeting weighs back rows | No row weight (`Battle.cs:645`) | #186 |
| Gear span a quarter to a half of its band | 0–4 points at every class (`GearPiece.cs:50`) | #186 |
| Health heals 1 a minute at home | Full on return (`Dive.cs:550`) | #187 |
| Floors spend a power budget; enemies built from it | Fixed count table, level-1 starting stats (`Dungeon.cs:37-90`) | #188 |
| The mead hall and paid Cook healing | Not built | #189 |

Already matching: damage rounds down once; the Mage's field is an area attack at half the
ordinary attack; experience and levels are one counter; a rest floor's 15% is instead of the
5%.

Left out on purpose: the Alchemist's buffs, God's Wish, the laboratory, armoury and smithy,
and crafting time belong to specialists the first version leaves out. Drop rate, monster gear,
the Battle Test fixture and found-dungeon depth are already held by #27, #166, #167 and #139.

## Options and recommendation

The fixes are not optional under the user's rule, so they were queued. The open calls are the
user's earlier choices that still contradict the originals, and rules the originals leave
open; each is asked on the item it blocks.

Recommendation: let the originals win on the user's earlier choices too (pause button, weapon
names, one-screen party planning, Dorms gear numbers), except where a first-version scope cut
keeps the build small (gold-only loot and repair, healing potions only, monsters without gear)
— those stay cut until the specialists and loot work is in scope. Why: the user's 24 Nov rule
is that the originals overwrite anything in EhrensDocs, and the scope cuts are about what is
built first, not about what the rule is.

## Open Questions

- See the questions on #184, #188 and #189 in the queue.
