# Battle Test

> **Status:** Settled: the two teams, their levels, their gear, and the field they fight
> on. Not settled: whether the narrower test field stands in for the game's own grid.

## What This Is For

A fixed pair of teams so that test battles can be run and compared against each other.
Both sides are F rank at level 1. The point is repeatability — the same teams, the same
gear, the same positions every run, so a change to a rule shows up as a change in the
outcome rather than being lost in different starting conditions.

The enemy team is 180 base stat points — six enemies at the F-rank baseline cost of 30
each, before the help bonus the formation gives. The largest single battle an F-rank
dungeon produces is 150 points, spread across fifteen enemies that each cost a third of
baseline. So this fixture is a heavier fight than F rank produces, and it concentrates
that weight in six bodies rather than fifteen. It is a bench for checking the combat
rules against each other rather than a sample of what a dungeon floor serves up. What a
floor's power is and what an enemy costs are covered in the Dungeon doc.

The teams here are set by hand rather than generated from a floor's power budget, and
they stay set by hand so that every run stays comparable with the ones before it.

## The Field

Each side has a field three positions wide and three rows deep. Front row is row 1,
nearest the enemy; row 3 is the back. Both teams use the same formation, mirrored.

Positions, for both sides:

- Row 1 — Brute (left), Tank (centre), Fighter (right)
- Row 2 — Rogue (left), Mage (centre), Archer (right)
- Row 3 — empty

This formation closes the support ring completely: every member receives help from exactly
one other, so each gets the first help bonus — five per cent of its primary stat, rounded
up to at least one point, which at these stats is **+1 to the primary stat**. The stats in
the tables below already include it.

The game's own battle grid is five wide and three deep, so this is a narrower field used
for testing.

## The Player's Team

Every piece of gear has **20 durability**.

| Member | Position | Level | Stats (Str/Dex/Con/Int/Luck) | Health | Cooldown | Weapon | Armour | Attack power | Defence |
|---|---|---|---|---|---|---|---|---|---|
| Brute | row 1 left | 1 | 9 / 6 / 7 / 4 / 5 | 84 | 138 ticks | club, 9–13 | tanned hide, 4–6 | 18–22, cleaves 3 | 11–13 |
| Tank | row 1 centre | 1 | 7 / 6 / 9 / 4 / 5 | 90 | 138 ticks | short sword, 11–15 | full armour, 11–15 | 18–22, taunts | 20–24 |
| Fighter | row 1 right | 1 | 9 / 7 / 6 / 4 / 5 | 60 | 104 ticks | two-handed sword, 8–11 | light armour, 11–15 | 17–20 per strike, 2 strikes | 17–21 |
| Rogue | row 2 left | 1 | 6 / 9 / 5 / 4 / 7 | 50 | 69 ticks | knife, 4–7 | hooded armour, 3–5 | 13–16 per strike, 2 strikes | 8–10 |
| Mage | row 2 centre | 1 | 4 / 7 / 6 / 9 / 5 | 60 | 104 ticks | staff, 6–10 | robe, 2–4 | 15–19, column | 8–10 |
| Archer | row 2 right | 1 | 7 / 9 / 5 / 4 / 6 | 50 | 69 ticks | bow, 14–19 | leather, 5–8 | 23–28 | 10–13 |

## The Enemy Team

Same six types, same stats, same positions. **All six wear the armour of their type**,
each at **10 durability**, matching the player team's own rolls. **Only the Fighter
carries a weapon**, also at **10 durability**, so the other five attack for their stat
alone.

| Member | Position | Level | Stats (Str/Dex/Con/Int/Luck) | Health | Cooldown | Weapon | Armour | Attack power | Defence |
|---|---|---|---|---|---|---|---|---|---|
| Brute | row 1 left | 1 | 9 / 6 / 7 / 4 / 5 | 84 | 138 ticks | none | tanned hide, 4–6 | 9, cleaves 3 | 11–13 |
| Tank | row 1 centre | 1 | 7 / 6 / 9 / 4 / 5 | 90 | 138 ticks | none | full armour, 11–15 | 7, taunts | 20–24 |
| Fighter | row 1 right | 1 | 9 / 7 / 6 / 4 / 5 | 60 | 104 ticks | two-handed sword, 8–11 | light armour, 11–15 | 17–20 per strike, 2 strikes | 17–21 |
| Rogue | row 2 left | 1 | 6 / 9 / 5 / 4 / 7 | 50 | 69 ticks | none | hooded armour, 3–5 | 9 per strike, 2 strikes | 8–10 |
| Mage | row 2 centre | 1 | 4 / 7 / 6 / 9 / 5 | 60 | 104 ticks | none | robe, 2–4 | 9, column | 8–10 |
| Archer | row 2 right | 1 | 7 / 9 / 5 / 4 / 6 | 50 | 69 ticks | none | leather, 5–8 | 9 | 10–13 |

## Levels and Experience

Both teams start at level 1. At F rank, crossing to E rank takes 20 experience and
reaching level 16, which from level 1 is 15 level-ups, so an even rate across the rank
puts a level at about 1.33 experience each.

Every enemy here is F rank, and each is built at the full F-rank baseline cost, so each
pays the full F value on a kill — a kill's pay scales with what the enemy cost, covered
in the Guild Members doc. An F-rank kill is worth 1 experience, so clearing all six pays
6, divided equally between the six party members — 1 each a battle. So a member gains a
level roughly every battle and a third, and reaches level 16, the level that makes it
eligible for E rank after about 20 battles. That twenty-battle figure is a property of
this fixture — six full-cost enemies a battle — rather than of a dungeon floor.

The fixture itself stays at level 1. It is a fixed starting state, so a run never leaves
the teams levelled up — the accumulation above is what a sequence of battles would
produce, not a change to the teams recorded here.

## Open Questions

- The game's battle grid is five wide and three deep; this test uses three wide. Is the
  narrower field only a convenience for testing, or should tests run on the full grid?
- Every member here receives one help, which adds a point to its primary stat. For the
  Tank that primary is Constitution, and health is Constitution times ten — so does the
  help raise its health from 80 to 90, as the table assumes, or does help reach defence
  only?
- A level costs about 1.33 experience here because crossing F rank takes 20 experience
  and 15 level-ups, split evenly. Whether experience really buys levels at an even rate
  is an open question in the Guild Members doc — if the two run on separate counters
  instead, this figure is wrong.
