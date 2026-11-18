# 144 — A new F-rank member's starting stats

> **Status:** Research done 2026-11-18; parked on the user's decisions.

## What was asked

Which numbers a newly recruited level-1 F-rank member starts with, per type. Every
recruit, and every monster (monsters are built from the same table), takes its stats from
this one table, so it sets the health, pace and damage of every fight.

## What the docs and the game say

- **Guild Members** says only that a new level-1 F-rank member "starts with single-digit
  stats", shaped by type. It gives no numbers.
- **Battle Test** gives full level-1 F-rank lines for the six fighting types. Its tables
  already include one point of support-ring help on each type's primary stat. With that
  point taken off, the starting lines are:

  | Type | Str / Dex / Con / Int / Luck |
  |---|---|
  | Brute | 8 / 6 / 7 / 4 / 5 |
  | Tank | 7 / 6 / 8 / 4 / 5 |
  | Fighter | 8 / 7 / 6 / 4 / 5 |
  | Rogue | 6 / 8 / 5 / 4 / 7 |
  | Archer | 7 / 8 / 5 / 4 / 6 |
  | Mage | 4 / 7 / 6 / 8 / 5 |

- **Combat** agrees with those lines in its seconds list: "a newly recruited F-rank Rogue,
  71 ticks" is Dexterity 8, and the 104 and 138 ticks match the Fighter's 7 and the Tank's
  6. But the same doc's worked cooldown list says "Dexterity 5, a newly recruited F-rank
  member — 80 ticks" — that is the one passage that disagrees. Its Luck list, "Luck 5, a
  newly recruited F-rank member — 1 True in 50", matches Battle Test's Luck 5 for four of
  the six types.
- **The game** (`Tuning.StartingStatsF`, marked placeholder) runs every stat **exactly 2
  lower** than Battle Test, for all six types: Rogue 4/6/3/2/5, Brute 6/4/5/2/3 and so on.
  It also has the two specialists Battle Test doesn't cover: Cook 4/5/6/2/3 and Porter
  6/3/5/2/4.
- Recruits on the board vary from the table by up to 1 point either way, kept between 1
  and 9. Battle Test's highest starting stat is 8, so that still fits.

## What changing it would mean in the game

Moving to Battle Test's numbers lifts everyone — members and monsters alike — by 2 in
every stat:

| Type | Health now → then | Seconds between attacks now → then |
|---|---|---|
| Brute | 50 → 70 | 7.5 → 6.9 |
| Tank | 60 → 80 | 7.5 → 6.9 |
| Fighter | 40 → 60 | 5.6 → 5.2 |
| Rogue | 30 → 50 | 3.9 → 3.6 |
| Archer | 30 → 50 | 3.9 → 3.6 |
| Mage | 40 → 60 | 5.6 → 5.2 |

Health rises by half or more while weapons stay the same, so early fights last longer and
a single hit takes a smaller bite. The fast types' Luck goes up too (a new Rogue's Luck 7
gives 2 lucky tokens in 50 instead of 1). Because monsters use the same table, the
balance between the two sides stays where it is; what changes is how long fights take and
how much a weapon matters next to the stat.

Members already hired keep the stats they were hired with; only new recruits and monsters
change. In the code it is one table edit — the tests read the table rather than copying
numbers, so few should need touching.

## Options

- **A — Battle Test's numbers** for the six fighting types (the table above), and the Cook
  and Porter raised by the same 2 points: Cook 6/7/8/4/5, Porter 8/5/7/4/6.
- **B — Keep the game's lower numbers** and treat Battle Test's as a test fixture only.
  Combat's 71/104/138-tick list would then not describe a new member.
- **C — Different numbers** the user picks.

## Recommendation

**A.** Two of the docs' owner's own documents already agree on these numbers, the game's
lower ones were placeholders picked before Battle Test existed, and the shift is uniform
(+2 everywhere), so the types keep exactly the shapes they have now. Raising the Cook and
Porter by the same 2 keeps them in step with the fighters they travel with.

If A is chosen, Combat's "Dexterity 5, a newly recruited F-rank member — 80 ticks" line
contradicts it; that gets a change note in EhrensDocs (the original stays as the docs'
owner wrote it). If B is chosen, the 71/104/138-tick lines get the change note instead.

Easy to change later either way: it is one table, and nothing saved depends on it except
members hired in between, who keep what they had.

## Sources

- `Battle Test.md` — The Field (the +1 help), The Player's Team table
- `Combat.md` — the Rogue cooldown list and the seconds list; the Luck worked list
- `Guild Members.md` — Starting Stats
- `src/guildmasters-descent/Assets/Scripts/Core/Tuning/Tuning.cs` — `StartingStatsF`,
  `RecruitStatVariance`

## Open Questions

- Should a new F-rank member start with Battle Test's numbers (Rogue 6/8/5/4/7 and so on,
  two higher than the game today), or keep the game's current lower ones?
- If the numbers go up, do the Cook and Porter go up by the same 2 points?
