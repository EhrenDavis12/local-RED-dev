# PRD: Floor power budget

> **Status:** Draft, revised once after review, queue item #188 · Source docs read: the originals (The Dungeon, Guild
> Members, Combat, Battle Test, Core Concept, Equipment, Individual Types, Specialists);
> EhrensDocs change notes for each, plus Open Questions and Platform; queue reports #184
> and #198.

## Problem

Every fighting floor of the guild's dungeon has three battles, each fielding a fixed count
of monsters from a placeholder table (1, 2, 2, 3, 3, 3, 4, 4, 5, 5), and every monster has
its type's level-1 starting stats whatever the floor. A kill pays its rank's full value
whatever the enemy is. The originals now build a floor's enemies from a power budget that
grows with depth and pay a kill for what the enemy cost; the game does neither.

## Goal

A newly created dungeon gives each fighting floor a power budget that rises from its rank's
figure to three times that at the bottom. The budget is split across the floor's battles
and spent on enemies whose number and strength fall out of a rolled, depth-scaled cost.
Their stats are dealt from their points in 8 : 7 : 6 : 5 : 4, and a kill pays experience in
proportion to what the enemy cost. No gear is bought yet, and nothing else about the dive
changes.

## Requirements

### Floor power

1. A fighting floor's power is a pool of base-stat points. The dungeon's first fighting
   floor gets its rank's figure: 100 at F, doubling each rank.
   — The Dungeon.md § The Dungeon.
2. Power triples from the first fighting floor to the deepest fighting floor. The climb
   counts fighting floors only, since rest areas hold no battles and no power, and it is the
   same ratio from each fighting floor to the next. The Test Dungeon's power column shows
   both: 100, 111, 122, 135, then 149 across the floor-5 rest area, and so on up to 300. In the
   10-floor starting dungeon, that runs from 100 on floor 1 to 300 on floor 9, over eight
   fighting floors.
   — The Dungeon.md § The Dungeon ("triples … climbing evenly", "Rest areas hold no
   battles and no power"); Battle Test.md § The Test Dungeon (power column).

### Battles and their shares

3. Each fighting floor rolls 1, 2 or 3 battles, at equal odds, when the dungeon is created,
   and the count is saved with the dungeon. That applies to the starting dungeon too: the
   EhrensDocs line "The first dungeon has 3 battles a floor to win" gives way, because the
   originals win. The Test Dungeon was rolled from these rules and its counts vary by floor:
   1, 1, 2, 3, 2, 2, 3, 2, 3, 3, 3, 2.
   — The Dungeon.md § The Dungeon ("Each floor has 1–3 battles"); Battle Test.md § The
   Test Dungeon (battles column); equal odds is the going-ahead default from #188's
   review.
4. The floor's power is split between its battles in the order they are fought: 1 battle
   gets all of it; 2 get 40% then 60%; 3 get 20%, 30%, then 50%.
   — The Dungeon.md § The Dungeon.

### Enemies from a battle's share

5. An enemy's scaled cost is its rank's baseline (30 at F, doubling each rank) on the first
   fighting floor, falling to a third of that on the deepest fighting floor. It falls the
   way power climbs: the same ratio each step, counting fighting floors only. Every monster
   is the dungeon's own rank for now, so the starting dungeon runs from 30 on floor 1 down
   to 10 on floor 9.
   — The Dungeon.md § The Dungeon; EhrensDocs/The Dungeon.md, "The dungeon's enemies are
   monsters"; the curve and the meaning of "deepest" are going-ahead defaults from #188's
   review.
6. Each battle makes one roll: a multiplier from 0.5 to 2, at even odds anywhere in that
   range. The rolled cost is the scaled cost times that multiplier and may be fractional.
   The battle's enemy count is its share divided by the rolled cost, rounded down, then
   held between 1 and 15.
   — The Dungeon.md § The Dungeon; Battle Test.md § The Test Dungeon (one "points an
   enemy" figure per battle); the odds and the rounding down are going-ahead defaults from
   #188's review.
7. Every enemy in a battle has the same points: the battle's share divided by its count,
   rounded to the nearest whole point. That is the only rounding. Neither the floor's power
   nor the share is rounded before it, so the Test Dungeon's printed power column (100,
   111, 122, 135 …) is those figures shown to the nearest point. An exact half rounds up
   (Open Questions). Because of the rounding, a battle can spend a little more or a little
   less than its share, as the table does. This one rule also covers the edge cases. Past
   15 enemies, the share divided by 15 raises every enemy's points. A share smaller than
   one rolled cost fields a single enemy that holds the whole share.
   — The Dungeon.md § The Dungeon (the overflow sentence, "never fewer than one");
   Battle Test.md § The Test Dungeon. Checked against its table: floor 4 is 134.93 × 50%
   ÷ 3 = 22.49, shown as 22; floor 12 is 245.67 × 50% ÷ 6 = 20.47, shown as 20; floor 2 is
   110.50 ÷ 4 = 27.6, shown as 28; floor 4, battle 1 is a single enemy holding its whole
   share of 27.
8. An enemy's cost is its stat points plus what its gear is worth. Monsters carry no gear in
   this build, so all of an enemy's points become stats. The cost, which is what its kill
   pays on, is kept as a figure of its own and is never worked back out from the stats.
   That way gear (#166) can take part of the points later without changing what a kill
   pays.
   — The Dungeon.md § The Dungeon ("An enemy's cost is its stat points plus what its gear
   is worth"); EhrensDocs/The Dungeon.md, "The dungeon's enemies are monsters" (no weapon
   or armour for now).
9. An enemy's stat points are dealt down its type's stat ordering in the ratio
   8 : 7 : 6 : 5 : 4, so a 30-point enemy has 8, 7, 6, 5 and 4. The F-rank starting lines
   are exactly this shape at 30 points, so a monster built at the F baseline has the same
   stats a monster has today.
   For now, the stats are rounded so they add up to the enemy's points, and no stat is
   below 1. Each stat's exact share is rounded down, and the points left over go one at a
   time to the stats with the largest fractions, the stat earlier in the ordering winning
   a tie. A 5-point enemy comes out at 1, 1, 1, 1, 1. Requirements 5 to 7 never give an
   F enemy fewer than 5 points, and at 5 or more this method never leaves a stat at 0. This
   rule is waiting on the user's confirmation (Open Questions).
   — The Dungeon.md § The Dungeon; Guild Members.md § Stat Weighting by Type;
   EhrensDocs/Guild Members.md, "Starting stats by type".
10. A monster is still level 1 and of the dungeon's own rank. It stands on a node of its
    own, drawn at random. Its type is drawn from all six combat types, as now. Health, K
    and everything else come from its stats and rank by the rules that apply today.
    — EhrensDocs/The Dungeon.md, "The dungeon's enemies are monsters" and "A floor's
    monsters are the same every dive, for now"; going-ahead answer on #188 (no type
    ladder).
11. Every floor's battles, and each monster's type, node, points and stats, are set once
    when the dungeon is created and saved with it. They are the same on every dive.
    — EhrensDocs/The Dungeon.md, "A floor's monsters are the same every dive, for now".
12. The starting dungeon is exactly 10 floors deep, with rest areas on 5 and 10.
    — Going-ahead answer on #188; The Dungeon.md § The Dungeon (every 5th floor).

### Experience

13. A kill pays the enemy's rank value scaled by its cost over its rank's baseline. The cost
    is requirement 8's figure, never the stats, and it is the enemy's whole points. Full
    value at the baseline, a third at a third, and more than full above it. What a kill
    pays is exact and never rounded. That is what keeps the doc's promise that the same
    points pay the same total whether they are spent on a horde or on a handful.
    — Guild Members.md § Levels and Experience.
14. A combat's total is still divided exactly between the members alive at its end, and the
    shares still add back up to the total.
    — EhrensDocs/Guild Members.md, "Who shares a combat's experience, for now".
15. To keep requirement 14 true, the saved unit of experience grows from 360,360 sub-units
    a point (`Xp.cs:9`) to 21,621,600, which is 360,360 × 60. Each point of cost pays 1/30
    of an experience point on an F kill, and 1/20 on any rank from E up: the rank values 3,
    6, 12 … over the baselines 60, 120, 240 … all come to 1/20. The unit has to divide by
    30 and by 20 and still leave a multiple of 360,360, which every party size from 1 to 15
    divides. Growing it × 30 would cover F only, and an E-rank share split eight ways would
    stop coming out whole. There is plenty of headroom: the largest rank total, 1,562,500
    experience from SS to SSS, is about 3.4 × 10^13 units, and a `long` holds 9.2 × 10^18.
    What a played mission's kill pays in experience doesn't change.
    — Follows from requirements 13 and 14.

### Saves

16. A dungeon already in a save keeps the monsters it was made with and is not rebuilt. It
    keeps three battles a floor and the table's counts. A monster saved without points,
    whether on a dungeon floor or in a battle saved partway through, loads as a 30-point
    build: its type's starting line, with a kill paying the full F value it pays today, never
    0. A dive or battle saved partway through carries on as it was saved, and a save from
    before this build still loads.
    — EhrensDocs/The Dungeon.md, "A floor's monsters are the same every dive, for now"
    ("a dungeon from an older save keeps the monsters it was made with");
    EhrensDocs/Platform.md (an older save still loads; a monster's maximum health comes
    from its saved Constitution); keeping the old monsters rather than rebuilding is the
    going-ahead default from #188's review.
17. When a save from before this build loads, every member's saved experience is multiplied
    by 60 into the new unit, once and without loss. A member's bar, level and whole
    experience read the same before and after.
    — EhrensDocs/Platform.md (an older save still loads); requirement 15.

## Out of Scope

- **Monster gear (#166).** Weapon and armour chances by floor, and gear bought out of the
  floor's points, come later. Requirement 8 is the seam for it.
- **The enemy-type ladder.** The pool of enemy types growing with each set of four floors
  is not part of this build. Every floor draws from any of the six types, as today
  (going-ahead answer on #188).
- **A rolled depth for the starting dungeon.** It is not rolled from 5 to 15; it stays at
  10.
- **The Test Dungeon fixture (#201).** Its table is cited above as the originals' worked
  example. It is not built here.
- **Gold, fees and drops (#199, #200, #194).** Floor gold keeps its fixed table, even
  though the originals will tie it to the enemy count.
- **Played missions.** Their monsters are not on a floor, so they keep today's count rule,
  starting stats and full rank pay.
- **Enemies one rank below the dungeon's.**
- **More enemies arriving once the grid is full.** Past 15 is covered by requirement 7
  and goes no further.
- **Rebuilding dungeons already in a save.** Requirement 16 keeps their monsters.

## Follow-ups

For forge-doc-planner. These are doc problems; this PRD doesn't depend on them.

- Battle Test.md, § What This Is For, says "The largest single battle an F-rank dungeon
  produces is 150 points". The Dungeon's rules allow 300, when the bottom fighting floor
  rolls one battle.
- EhrensDocs/The Dungeon.md, "A floor is a series of battles…", still says "The first
  dungeon has 3 battles a floor to win". The originals' 1–3 now replaces it (requirement 3).
- Combat.md keeps "do the enemies stop there, or do they keep coming?" open, though The
  Dungeon.md now caps a battle at fifteen.
- The Dungeon.md says power is "climbing evenly". Only Battle Test's table shows that means
  an equal ratio from floor to floor rather than equal steps.

## Open Questions

Entries marked *[proposed]* are this PRD's questions; nothing in the docs asks them yet.

- *[proposed, awaiting the user's confirmation]* How does 8 : 7 : 6 : 5 : 4 round to whole
  stats? The build goes ahead with requirement 9's rule for now: stats add up to the
  enemy's points, and no stat is below 1.
- *[proposed, awaiting the user's confirmation]* When an enemy's points (share ÷ count)
  come out at exactly a half, which way do they round? The build goes ahead with rounding
  up (requirement 7). It can only happen where the floor's power is a whole number, which
  is the first and last fighting floors.
- The enemy grid holds fifteen. When a floor is deep enough to fill it, do the enemies stop
  there, or do they keep coming? (Combat.md § Open Questions. The Dungeon doc caps a
  battle at 15, and this build honours that cap.)
