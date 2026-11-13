# Battle Test

> **Status:** Settled: the two teams, their gear, and the field they fight on. Not
> settled: whether the narrower test field stands in for the game's own grid.

## What This Is For

A fixed pair of teams so that test battles can be run and compared against each other.
Both sides are F rank at level 1. The point is repeatability — the same teams, the same
gear, the same positions every run, so a change to a rule shows up as a change in the
outcome rather than being lost in different starting conditions.

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

| Member | Position | Stats (Str/Dex/Con/Int/Luck) | Health | Cooldown | Weapon | Armour | Attack power | Defence |
|---|---|---|---|---|---|---|---|---|
| Brute | row 1 left | 9 / 6 / 7 / 4 / 5 | 70 | 138 ticks | club, 9–13 | tanned hide, 4–6 | 18–22, cleaves 3 | 11–13 |
| Tank | row 1 centre | 7 / 6 / 9 / 4 / 5 | 90 | 138 ticks | short sword, 11–15 | full armour, 11–15 | 18–22, taunts | 20–24 |
| Fighter | row 1 right | 9 / 7 / 6 / 4 / 5 | 60 | 104 ticks | two-handed sword, 8–11 | light armour, 6–9 | 17–20 per strike, 2 strikes | 12–15 |
| Rogue | row 2 left | 6 / 9 / 5 / 4 / 7 | 50 | 69 ticks | knife, 4–7 | hooded armour, 3–5 | 13–16 per strike, 2 strikes | 8–10 |
| Mage | row 2 centre | 4 / 7 / 6 / 9 / 5 | 60 | 104 ticks | staff, 6–10 | robe, 2–4 | 15–19, column | 8–10 |
| Archer | row 2 right | 7 / 9 / 5 / 4 / 6 | 50 | 69 ticks | bow, 14–19 | leather, 5–8 | 23–28 | 10–13 |

## The Enemy Team

Same six types, same stats, same positions. **Almost none of them are equipped**: only the
Fighter carries a weapon, and only the Tank wears armour, each with **10 durability**.
Everyone else fights bare — so their damage is their stat alone and their defence is their
Constitution alone.

| Member | Position | Stats (Str/Dex/Con/Int/Luck) | Health | Cooldown | Weapon | Armour | Attack power | Defence |
|---|---|---|---|---|---|---|---|---|
| Brute | row 1 left | 9 / 6 / 7 / 4 / 5 | 70 | 138 ticks | none | none | 9, cleaves 3 | 7 |
| Tank | row 1 centre | 7 / 6 / 9 / 4 / 5 | 90 | 138 ticks | none | full armour, 11–15 | 7, taunts | 20–24 |
| Fighter | row 1 right | 9 / 7 / 6 / 4 / 5 | 60 | 104 ticks | two-handed sword, 8–11 | none | 17–20 per strike, 2 strikes | 6 |
| Rogue | row 2 left | 6 / 9 / 5 / 4 / 7 | 50 | 69 ticks | none | none | 9 per strike, 2 strikes | 5 |
| Mage | row 2 centre | 4 / 7 / 6 / 9 / 5 | 60 | 104 ticks | none | none | 9, column | 6 |
| Archer | row 2 right | 7 / 9 / 5 / 4 / 6 | 50 | 69 ticks | none | none | 9 | 5 |

## Open Questions

- The game's battle grid is five wide and three deep; this test uses three wide. Is the
  narrower field only a convenience for testing, or should tests run on the full grid?
- Every member here receives one help, which adds a point to its primary stat. For the
  Tank that primary is Constitution, and health is Constitution times ten — so does the
  help raise its health from 80 to 90, as the table assumes, or does help reach defence
  only?
