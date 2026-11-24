# #198 — The other developer's 24 Nov doc edits, against EhrensDocs and the game

> **Status:** Research report for queue item #198, 2026-11-24. Nothing waits on the user
> except the cheap going-ahead questions listed at the end.

## What changed in the originals

Fourteen commits (`git log --author=royda 4604b43..HEAD`), touching Battle Test, Combat,
Equipment, Guild Members, Individual Types and The Dungeon. Seventeen distinct rule changes.
Only one already matches the game: the Brute's axe and the Tank's war hammer.

## Change → game today → job

| Change in the originals | Game today | Job |
|---|---|---|
| Rogue draws up to 2 evasion tokens against **every** attack | One token for everyone (`Battle.cs:831`) | #186, rebriefed (it said "against an Archer") |
| A target is **rolled**: 20 in 100 to the weakest reachable, 80 shared; far range splits the 80 by row, each row back counting double; taunt and focus 100% | Weighted by damage dealt + missing health (`Battle.cs:738-752`); taunt and focus already match | #186, rebriefed |
| Brute health is Constitution ×12 (others ×10) | ×10 for everyone (`Member.cs:81-83`) | #186, added |
| Light armour F band 5–16 (was 4–13) | 4–13 (`GearBands.cs:33`) | #186, added |
| Bow durability 80–160 (was 40–80) | 40–80 (`GearBands.cs:55-56`) | #186, added |
| Brute carries an axe, Tank a war hammer | Same | already matches |
| Monster gear chance set by the **floor**: weapon 1–3% on floor 1 rising 5–7 a floor, armour from floor 11 | Monsters have no gear (`Combatant.cs:22`) | #166, rebriefed (it said "by the dungeon's rank") |
| Gear is bought out of the floor's power budget, so an armed floor has fewer enemies | Fixed enemy-count table (`Dungeon.cs:50-58`) | #166 + #188 (#166 now builds after #188) |
| Battle Test fixture: gear at full durability; Brute 84 health; Fighter light armour 11–15 | No fixture yet | #167, unblocked and rebriefed (builds after #186 and #166) |
| A Test Dungeon fixture: 14 floors F rank, rests on 5 and 10, power 100→300, set table per floor | Depth is random (`Dungeon.cs:41`) | **#201** new |
| A floor pays gold by its enemy count, 1 gold each at F, doubling each rank | Fixed table × rank scale (`DiveRules.cs:14-15`) | **#199** new |
| Entry fee 2 gold a member at F, doubling each rank | 2, 4, 6, 10… (F and E match) | **#199** new |
| Teleport fee 1 gold a floor returned to at F, rising 1 a rank | Flat 20 (`Tuning.cs:477`) | **#199** new |
| A weapon or armour piece drops on the last fighting floor before each rest, and on the last floor; no room means lost | Dives pay gold only (`Dive.cs:395`) | **#200** new |
| 1 enemy in 4 drops "materials or an item"; materials are ores or herbs | Not built | #194, rebriefed (it said "an item") |

## EhrensDocs, cleaned up

The originals win, so EhrensDocs keeps only the gaps (committed with this report):

- **Removed:** the three axe-and-war-hammer notes (the originals say it now), the entry-fee
  paragraph, and the question on whether the teleport fee rises with party size (the
  originals give it per floor).
- **Cut down:** the targeting note now covers only how a taunt is spent; the re-entry note
  covers only where a party re-enters.
- **Brought up to date:** Brute health ×12, members can come home hurt, materials are ores
  or herbs, gear chances by floor, 1–3 battles a floor, and the Rogue question removed from
  five Guild Members notes (the originals answered it).

## EhrensDocs Open Questions: none answered outright

Every question was checked against the originals as they stand now. None is fully
answered, so all stay as written.

- **Partly answered:** 3 (a dead member's gear: it comes home only if the party has room,
  and every member adds room; how much room a piece takes is still open). 27 (a found
  dungeon's bottom floor is a fighting floor, since gear drops there; what happens after it
  is cleared is still open). 15 (experience split: the originals say "split evenly between
  everyone who came", but whether the dead take a share is the question already waiting on
  #184). 16 (a special's bar refill follows from two rules, but neither says it outright).
- **Still open:** 4, 5, 9, 10, 11, 12, 13, 14, 20, 21, 22, 23, 24, 25, 26, 29.

## Going ahead with (cheap, recorded on the jobs)

- Back-row targeting picks a row first (back rows twice as likely), then an enemy in it
  (#186).
- A tie for weakest splits the extra 20% (#186).
- An enemy's drop is half materials, half items (#194).

## Follow-ups

- `EhrensDocs/Equipment.md`: a kept open question still says the Brute "halves" a Tank's
  defence, while the note's own Why says "quarters". It is the user's wording, so it was
  left alone.
- Four Guild Members Why lines still say "The pending changes to this list above are
  unchanged", which reads oddly now the Rogue entry is gone.
- When #191 (pause in dev builds only) lands, three EhrensDocs pause notes need updating.
