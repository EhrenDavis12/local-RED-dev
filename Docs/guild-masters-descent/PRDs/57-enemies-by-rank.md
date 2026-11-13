# PRD: Enemies by Dungeon Rank, Count by Depth

> **Status:** Draft · Source docs read: Combat.md, Core Concept.md, Equipment.md, Guild
> Members.md, Individual Types.md, Specialists.md, The Dungeon.md; change notes in
> EhrensDocs/ (Combat, Core Concept, Equipment, Guild Members, Individual Types, Platform,
> Specialists, The Dungeon); queue/reports/48-reconcile-ehrensdocs.md (row 12); queue/focus.md.
> Source read: `Core/Dungeon/Dungeon.cs`, `Core/Dungeon/Dive.cs`, `Core/Combat/Battle.cs`,
> `Core/Combat/DamageMath.cs`, `Core/Save/SaveManager.cs`, `Core/Dungeon/DungeonInfo.cs`,
> `Core/Tuning/Tuning.cs`.

## Problem

Every battle in the dungeon is one monster, and that monster gets stronger by floor through a
placeholder level table (1–4). The originals say the opposite on both counts: an enemy's
strength is its rank and type, and depth changes how many enemies turn up, not what each one
is. So a deep floor today is the same one-on-one fight with a luckier, tougher monster, and
the party never faces a force.

## Goal

When a dungeon is created, every enemy on it is the dungeon's rank (F, in this version) with
exactly its type's stats at that rank, whatever the floor; and each battle fields a number of
enemies set by its floor, never fewer on a deeper floor. Everything else about how a
monster is generated, fights and is saved stays as it is.

## Requirements

### Rank

1. **An enemy is the dungeon's rank or one grade below it, and no other grade.** The ladder
   starts at F (Core Concept.md `## Guild Rank`; Guild Members.md `## Promotion`), so there is
   no grade below F: **every enemy in an F-rank dungeon is F rank.** — Combat.md `## Enemies`.
2. **The enemy's rank is stored with it** when the dungeon is created, and saved with the
   dungeon, so that what reads an enemy's rank — its K (Guild Members.md `## Base Stats`) and
   what its kill is worth (Guild Members.md `## Levels and Experience`) — can read it from the
   enemy. In this version every stored enemy rank is F. — Combat.md `## Enemies` ("it sets
   both the rank of the enemies found there").

### Stats

3. **An enemy's stats are its type's starting stats at its rank**, the same table a new
   recruit of that type and rank starts from (`Tuning.StartingStatsF` at F). — Guild
   Members.md `## Starting Stats` ("the type sets the shape … the rank or tier sets their
   magnitude"); Combat.md `## Enemies` ("exactly what their type and rank would otherwise
   give").
4. **Depth never changes an enemy's stats.** An enemy of a given type and rank has identical
   stats on floor 1 and on the deepest floor — Luck included. The floor-by-floor monster
   level goes: new enemies are level 1 and get no level-ups from the floor they stand on.
   — Combat.md `## Enemies` ("the enemies' own Luck stat is untouched … so depth doesn't
   make them evade more or reset their cooldowns more often"). A level that rises with the
   floor raises stats picked by the type's weighting, Luck among them, which is exactly what
   that sentence rules out; the originals win over the change note that set it (see
   Needs your call in the report).

### How many

5. **Every battle on a floor fields the same number of enemies, set by the floor.** — Combat.md
   `## Enemies` ("the more enemies turn up in each fight").
6. **A deeper floor never fields fewer enemies a battle than a shallower one, and the dungeon's
   deepest battle floor fields more than its first.** — Combat.md `## Enemies` ("The deeper
   into a dungeon the player goes, the more enemies turn up in each fight").
7. **No battle fields more than 15 enemies** — one to a node of the 5-by-3 enemy grid.
   — Combat.md `## Formation`. Whether a floor deep enough to fill the grid stops there stays
   open (below); the placeholder table must not reach 15, so it does not come up.
8. **The count is a placeholder table in `Tuning.cs`**, by floor, floor 1 first, replacing the
   single `DungeonMonstersPerBattle`; a rest floor's entry is ignored, and a floor past the
   table's end takes its last entry, as the other floor tables do. Proposed values, all
   placeholders — floors 1–10: **1, 2, 2, 3, –, 3, 4, 4, 5, –**. Tests read the table rather
   than pin these numbers. — Focus `Missing details` (a missing number gets a placeholder in
   the one tuning file).

### Where they stand

9. **Each enemy takes a node of its own, drawn at random among the 15, as today.** No doc says
   how enemies are placed; this keeps the built behaviour rather than inventing a rule (see
   Needs your call). — Combat.md `## Formation` ("Enemies use the same style of grid").

### Saves

10. **A dungeon saved before this change loads with the monsters it was created with** — their
    count, types, levels and nodes — and each loads as F rank. — EhrensDocs/The Dungeon.md
    "A floor's monsters are the same every dive, for now" (set once, when the dungeon is
    created); EhrensDocs/Platform.md `## Saving` ("A save made by an older version still
    loads").

### Unchanged

11. These stay exactly as built; a test that held before this change still holds:
    - An enemy's type is one of the six combat types, drawn per enemy as today. — Combat.md
      `## Enemies`; EhrensDocs/The Dungeon.md "The dungeon's enemies are monsters".
    - **No gear on any enemy:** damage is its stat alone, defence its Constitution alone.
      — EhrensDocs/The Dungeon.md "The dungeon's enemies are monsters"; the first-version
      cut kept as the default on queue item #48 (report `## Open Questions`, first entry).
    - A floor's enemies are drawn once, at dungeon creation, and are the same every dive.
      — EhrensDocs/The Dungeon.md "A floor's monsters are the same every dive, for now".
    - Battles per floor, rest floors with no battles, and the floor's gold — EhrensDocs/The
      Dungeon.md "A floor is a series of battles…" and "A party can turn back anywhere…";
      the dungeon's depth — Focus `## Goal` (one dungeon at least 10 floors deep).
    - Experience stays one per enemy on the floor, which is already what an F-rank kill is
      worth. — Guild Members.md `## Levels and Experience`. Experience by rank is queue
      item #7, not this one.
    - An F-rank enemy's K is 20. — Guild Members.md `## Base Stats`.

## Out of Scope

- **Gear on enemies** — the dungeon's rank setting the chance of a weapon and of armour, and
  depth setting how good it is (Combat.md `## Enemies`). Cut from the first version; a later
  item.
- Dungeons above F, and with them: how often an enemy is one grade below rather than the
  dungeon's own, and the starting stats of any rank above F. No such dungeon can be made in
  this version (Focus `## Not included`: guild ranks above F).
- Enemies repositioning mid-battle (Combat.md `## Formation`).
- Experience by enemy rank (queue item #7).
- Which types a given dungeon favours (The Dungeon.md `## The Dungeon Board` names "the types
  of monster and enemy found in each of the dungeons"; nothing says a dungeon has a set).
- How the Dungeon Board words a monster now that its level no longer varies — copy, built and
  looked at.

## Open Questions

- The enemy grid holds fifteen. When a floor is deep enough to fill it, do the enemies stop
  there, or do they keep coming? (Combat.md `## Open Questions`)
- *Proposed by the PRD author, not in the docs:* "That luck is in the generation" — is a
  floor's enemy count a fixed number for that floor, or a roll that depth tilts upward? This
  PRD builds a fixed number per floor (requirement 8).
- *Proposed by the PRD author, not in the docs:* Where do enemies stand on their grid — at
  random, as built, or placed the way the party is first placed, with support links made
  where they can be? This PRD keeps random (requirement 9).
