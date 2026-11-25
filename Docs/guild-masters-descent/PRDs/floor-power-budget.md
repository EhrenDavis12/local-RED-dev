# PRD: Floor power budget

> **Status:** Draft, queue item #188 · Source docs read: the originals (The Dungeon, Guild
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

3. A fighting floor has 1 to 3 battles. How many a floor gets is not settled (Open
   Questions).
   — The Dungeon.md § The Dungeon; EhrensDocs/The Dungeon.md, "A floor is a series of
   battles that scrolls right into the next".
4. The floor's power is split between its battles in the order they are fought: 1 battle
   gets all of it; 2 get 40% then 60%; 3 get 20%, 30%, then 50%.
   — The Dungeon.md § The Dungeon.

### Enemies from a battle's share

5. An enemy's scaled cost is its rank's baseline (30 at F, doubling each rank) at the
   dungeon's shallowest floor, falling to a third of that at its deepest. Every monster
   is the dungeon's own rank for now, so in the starting dungeon this runs from 30 down to 10.
   The curve in between is not settled (Open Questions).
   — The Dungeon.md § The Dungeon; EhrensDocs/The Dungeon.md, "The dungeon's enemies are
   monsters".
6. Each battle makes one roll, which varies the scaled cost from half of it to twice it. The
   battle's enemy count is its share divided by that rolled cost, never fewer than 1 and
   never more than 15.
   — The Dungeon.md § The Dungeon; Battle Test.md § The Test Dungeon (one "points an
   enemy" figure per battle).
7. The whole share is spent, divided equally between the battle's enemies. So when the count
   would pass 15, the points left over raise every enemy's points. A share smaller than one
   rolled cost fields a single enemy that holds the whole share.
   — The Dungeon.md § The Dungeon (the overflow sentence, "never fewer than one");
   Battle Test.md § The Test Dungeon (floor 2: a share of 111 is 4 enemies of 28; floor 4,
   battle 1: a share of 27 is 1 enemy of 27).
8. An enemy's cost is its stat points plus what its gear is worth. Monsters carry no gear in
   this build, so all of an enemy's points become stats. The cost, which is what its kill
   pays on, is kept as a figure of its own and is never worked back out from the stats.
   That way gear (#166) can take part of the points later without changing what a kill
   pays.
   — The Dungeon.md § The Dungeon ("An enemy's cost is its stat points plus what its gear
   is worth"); EhrensDocs/The Dungeon.md, "The dungeon's enemies are monsters" (no weapon
   or armour for now).
9. An enemy's stat points are dealt down its type's stat ordering in the ratio
   8 : 7 : 6 : 5 : 4, so a 30-point enemy has 8, 7, 6, 5 and 4. How fractions round is not
   settled (Open Questions). The F-rank starting lines are exactly this shape at 30 points,
   so a monster built at the F baseline has the same stats a monster has today.
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

13. A kill pays the enemy's rank value scaled by its cost over its rank's baseline: full
    value at the baseline, a third at a third, and more than full above it. What a kill
    pays is exact and never rounded. That is what keeps the doc's promise that the same
    points pay the same total whether they are spent on a horde or on a handful.
    — Guild Members.md § Levels and Experience.
14. A combat's total is still divided exactly between the members alive at its end, and the
    shares still add back up to the total. Fractional kill pay must not break that.
    — EhrensDocs/Guild Members.md, "Who shares a combat's experience, for now".

### Saves

15. A dungeon already in a save keeps the monsters it was made with: three battles a floor,
    the table's counts, and monsters with level-1 starting stats that pay their rank's full
    value, exactly as today. That agrees with requirement 13, because those stats are a
    30-point F build. A dive or battle saved partway through carries on as it was saved.
    A save from before this build still loads.
    — EhrensDocs/The Dungeon.md, "A floor's monsters are the same every dive, for now"
    ("a dungeon from an older save keeps the monsters it was made with");
    EhrensDocs/Platform.md (an older save still loads; a monster's maximum health comes
    from its saved Constitution).

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
- **More enemies arriving once the grid is full.**
- **Rebuilding dungeons already in a save** (Open Questions).

## Open Questions

Entries marked *[proposed]* are this PRD's questions; nothing in the docs asks them yet.

- *[proposed]* The originals say "Each floor has 1–3 battles", and EhrensDocs says "The
  first dungeon has 3 battles a floor to win". Does the starting dungeon roll 1 to 3
  battles a floor, or keep 3?
- *[proposed]* If the battle count is rolled, are 1, 2 and 3 equally likely?
- *[proposed]* How does an enemy's scaled cost fall from full baseline to a third? In equal
  steps, or by an equal ratio the way power climbs? And does it count fighting floors only,
  the way power does?
- *[proposed]* In the starting dungeon, the bottom floor (10) is a rest area. For an enemy's
  cost, is the "deepest floor" floor 9 or floor 10?
- *[proposed]* Is the roll from half to twice equally likely anywhere in that range, and is
  the rolled cost a whole number of points?
- *[proposed]* How does each figure round to whole points? That means a floor's power, a
  battle's share, the count (share ÷ cost, rounded down or to nearest), and each enemy's
  points (share ÷ count). The Test Dungeon's numbers are consistent with rounding power and
  points to the nearest whole point, with both halves in its table going down (22.5 → 22,
  20.5 → 20), but it states no rule.
- *[proposed]* How does 8 : 7 : 6 : 5 : 4 round to whole stats, and must the stats add back
  up to the enemy's points? Can a stat round to 0? A 5-point enemy comes out at 1.33, 1.17,
  1.00, 0.83 and 0.67, and a Constitution of 0 is a monster with no health.
- *[proposed]* If an enemy's stats after rounding don't add up to its points, does its kill
  pay on the points or on the stats?
- *[proposed]* The guild only ever has its one starting dungeon. Should a save's dungeon
  have its unreached floors rebuilt under the new rules, rather than keeping its old
  monsters for good?
- The enemy grid holds fifteen. When a floor is deep enough to fill it, do the enemies stop
  there, or do they keep coming? (Combat.md § Open Questions. The Dungeon doc caps a
  battle at 15, and this build honours that cap.)
