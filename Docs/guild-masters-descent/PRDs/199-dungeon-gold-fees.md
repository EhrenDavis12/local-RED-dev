# PRD: Dungeon gold and fees by the originals

> **Status:** Draft · Queue #199 · Source docs read: The Dungeon.md, Core Concept.md,
> Combat.md, Equipment.md, Specialists.md, Guild Members.md, Individual Types.md,
> Battle Test.md, and every EhrensDocs change note (The Dungeon, Core Concept, Equipment,
> Open Questions, and the rest); queue report 198. Code read: `DiveRules.cs`, `Dive.cs`,
> `Tuning.cs`, `TuningTables.cs`, `DiveLauncher.cs`, the dive test suite.

## Problem

The game pays and charges gold by placeholder tables that the original The Dungeon doc
has since replaced. A floor pays a fixed amount by floor number (8, 10, 12, 14, 0, 20…)
times a rank scale (1, 2, 3, 5, 8…), whatever enemies it held. The entry fee rises 2, 4,
6, 10, 15… a member, matching the original only at F and E. Re-entering at a rest area
costs a flat 20 gold whatever the floor or rank. The user's rule of 18 Nov is that where
the docs conflict, the other dev's originals win.

## Goal

A cleared floor pays gold drawn from how many enemies it actually held, worth 1 gold
each at F and doubling each rank. The entry fee is 2 gold a member at F, doubling each
rank. The teleport fee for re-entering is reckoned from the floor returned to and rises
with rank. Everything else about dive gold stays as it is: when it drops, what a retreat
loses, and who carries it.

## Requirements

### Floor gold

1. **A cleared fighting floor pays drawn count × the rank's gold per count.** The floor
   is cleared when every battle on it is won, and the gold is paid then, as one lump.
   *(The Dungeon.md § The Dungeon, the "Gold comes by the floor" bullet; EhrensDocs/The
   Dungeon.md, change "A floor is a series of battles that scrolls right into the next".)*

2. **The enemy count is every monster on the floor, across all of its battles, as the
   dungeon holds them.** This is the count the floor actually has after the power budget
   and any gear filled it. It is not a table and not a figure worked out from the floor's
   power. It is the same count the floor's loot roll already uses (`Dive.cs`,
   `WinBattle`). A dungeon from an older save uses the monsters it was made with.
   *(The Dungeon.md § The Dungeon: "A floor pays a count drawn from its enemy count";
   EhrensDocs/The Dungeon.md, changes "A floor's monsters are the same every dive, for
   now" and "How a floor's power becomes its enemies, for now".)*

3. **The count is a whole number drawn from (enemy count − 2) up to the enemy count,
   both ends included.** A floor of fifteen enemies pays 13 to 15 gold at F. *(The
   Dungeon.md § The Dungeon.)*
   - **Default, pending Open Question 1:** the low end never goes below 0. A floor of
     one enemy draws from 0 to 1, and a floor of two draws from 0 to 2.
   - **Default, pending Open Question 2:** every whole number in the range is equally
     likely.

4. **Gold per count, by the dungeon's rank: 1 at F, doubling each rank.** *(The
   Dungeon.md § The Dungeon: "1 gold in an F-rank dungeon, doubling each rank".)*

   | F | E | D | C | B | A | S | SS | SSS |
   |---|---|---|---|---|---|---|---|---|
   | 1 | 2 | 4 | 8 | 16 | 32 | 64 | 128 | 256 |

5. **A rest area pays no gold.** It has no battles, so nothing is cleared there. *(The
   Dungeon.md § The Dungeon: "Rest areas hold no battles and no power"; EhrensDocs/The
   Dungeon.md, change "For now a dive drops ore, herb and healing potions": "neither does
   a rest area".)*

6. **Default, pending Open Question 3: the draw is made each time the floor is cleared,
   from the dive's own seeded stream.** The same seed and the same play give the same
   gold, and saving and loading mid-dive cannot draw it a second time. This matches how
   the floor's loot is rolled. The order of the gold draw and the loot roll is the
   implementer's choice, but it must be fixed. *(Proposal by analogy with EhrensDocs/The
   Dungeon.md, change "For now a dive drops ore, herb and healing potions": "rolled again
   each time it is cleared, from the dive's own saved rolls".)*

7. **Nothing else about dive gold changes.** The gold still drops only once every battle
   on the floor is won. Turning back between rest areas still loses the gold found since
   the last one. Gold still takes no slots, and only the living bring it out.
   `DiveRules.GoldBrought` and the gold-since-rest-area bookkeeping stay as they are.
   Carrying limits on loot and gear are not touched. *(EhrensDocs/The Dungeon.md, changes
   "A floor is a series of battles…" and "A party can turn back anywhere, and gold takes
   no slots for now".)*

### Entry fee

8. **Entry fee = party size × the rank's fee per member: 2 at F, doubling each rank.**
   Only D and above change. *(The Dungeon.md § Entering the Dungeon.)*

   | | F | E | D | C | B | A | S | SS | SSS |
   |---|---|---|---|---|---|---|---|---|---|
   | Today | 2 | 4 | 6 | 10 | 15 | 25 | 40 | 60 | 90 |
   | New | 2 | 4 | 8 | 16 | 32 | 64 | 128 | 256 | 512 |

### Teleport fee

9. **Re-entering at a rest area costs the entry fee plus a teleport fee, and the teleport
   fee is the floor returned to × the rank's gold per floor.** *(The Dungeon.md §
   Entering the Dungeon.)*
   - **Default, pending Open Question 4:** the floor returned to is the rest area's own
     floor number, so re-entering at floor 5 counts 5 floors.
   - **Default, pending Open Question 4:** the gold per floor is 1 at F and goes up by 1
     at each rank above it.

     | F | E | D | C | B | A | S | SS | SSS |
     |---|---|---|---|---|---|---|---|---|
     | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |

     So re-entering the starting F dungeon at floor 5 costs 5 gold, down from today's 20.

10. **Party size does not change the teleport fee.** The original gives it per floor,
    where it gives the entry fee per member. *(The Dungeon.md § Entering the Dungeon;
    queue report 198 removed the EhrensDocs question on this for that reason.)*

11. **A guild that can't cover the whole fee doesn't go in, and nothing changes.** This
    is already how the game works. It now applies to the new totals. *(EhrensDocs/Core
    Concept.md, change "The guild can't go into debt".)*

### Save impact

12. **No save change.** The fees are not saved. A dive's saved gold found, its gold since
    the last rest area, and its random-number state already cover the new draw. Gold
    already found in a saved dive keeps its saved value, and floors cleared after loading
    pay by the new rule. No new field and no format version bump. If the implementer
    finds a field is needed, stop and raise it rather than adding one. *(From the code:
    `Dive.cs` save and restore; EhrensDocs/The Dungeon.md, change "A floor's monsters are
    the same every dive": "a dungeon from an older save keeps the monsters it was made
    with".)*

### Tuning

13. **The three rank tables in Requirements 4, 8 and 9 live in `Tuning` as placeholders,
    like the dive tuning around them.** These are retired:
    - `DungeonFloorGold`
    - `DungeonFloorGoldScale`
    - the flat `DiveTeleportFee`
    - `FloorGoldTable`, if nothing else uses it

    `DiveEntryFeePerMember` keeps its role with the new values. *(The project's tuning
    convention, `Tuning.cs`.)*

## Superseded values and tests

This is for the test author. Line numbers are as of this PRD.

**Code that carries the old rule:**
- `DiveRules.FloorGold(rank, floor)` becomes a rule on the enemy count and the draw.
- The fee in `Dive.TryBegin` (`Dive.cs:286`).
- **`DiveLauncher.cs:50` recomputes the fee for its "can't pay the fee of N gold"
  message** with its own copy of the formula, using the flat `Tuning.DiveTeleportFee`.
  It must quote the same fee `TryBegin` charges, including the floor-based teleport fee.

**`DiveRulesTests.cs`. These no longer hold, or test a rule that is gone:**
- `Fee_APartyOfThreeAtFPaysNoMoreThanFloorOneDropsAtF` (L93). Floor 1 can now pay 0–1
  gold.
- `Fee_TheTeleportFeeIsStillTwentyOneFlatAmount` (L118) and
  `Tuning_TheTeleportFeeIsAboveZero` (L193).
- `Gold_AnFRankFloorDropsExactlyTodaysTable` (L126).
- `Gold_EveryBattleFloorDropsMoreAtEachRankUp` (L144). This becomes "gold per count
  doubles each rank".
- `Gold_ARanksFloorsAreTheTablesFloorsTimesOneScale` (L155).
- `R16_EveryBattleFloorDropsSomeGoldAtEveryRank` (L171). This is now false, because a
  floor of one or two enemies can pay 0.
- `Gold_ARestAreaDropsNothingAtAnyRank` (L136). The rule still holds but must be
  restated: there is no per-floor table any more.
- `Tuning_GoldOfFloorsOneToFour…` (L199) and `Tuning_GoldOfEveryBattleFloorIsMore…`
  (L206). These are fixture guards built on the old table. They need a new basis, for
  example a seed or a fixture dungeon whose floors are known to pay enough.

**These still hold and should keep passing:** `R11_EntryFeeRisesStrictlyWithPartySize…`,
`D16_EntryFeeIsAPerMemberAmountTimesPartySize…`, `Fee_AnFRankDungeonCostsTwoGoldAMember`,
`Fee_ThePerMemberFeeRisesStrictlyWithRank` and `Fee_ABiggerPartyPaysMoreAtAHigherRankToo`.

**`DiveRunTestKit.cs`.** `FloorGold(floor)` (L211) and `GoldOf(…)` (L219) assume the
table, and the API comment block at L22–43 describes it. `FixtureEntryFee` still works.
Every test that expects `DiveRunKit.FloorGold(n)` or `GoldOf(…)` as an exact figure needs
the expected gold from the floor's actual enemy count and draw instead:
- `DiveCooldownDriveTests`
- `DiveEndingTests`
- `DiveFloorTests`
- `DiveFlowScreenTests` (L166)
- `DiveLootTests` (L636)
- `DiveRetreatTests`
- `DiveSaveTests`
- `DiveStartTests` (L262)
- `FallenGearSlotsTests` (L624)
- `LootSaveTests` (L293)

Most of these test retreat and bookkeeping rather than the amount. They only need a
correct expected figure, not a new assertion.

**Teleport fee expectations** using `Tuning.DiveTeleportFee`:
- `DiveLauncherTests` (L59, L124)
- `DiveStartTests` (L219, L227, L280, L308, L394)

## Out of Scope

- Gear drops on the floor before a rest area (queue #200), and loot generally.
- The open question on whether a mid-floor retreat loses only that floor's gold or all
  the gold since the last rest area (EhrensDocs/The Dungeon.md, "A question on what gold
  a retreat keeps"). This PRD does not change retreat behaviour.
- Whether gold takes slots (EhrensDocs/Open Questions.md, item 4).
- The Test Dungeon fixture (queue #201), floor power, and enemy counts themselves.
- Any screen change beyond the numbers shown changing.

## Open Questions

These are proposals marked as mine: no doc asks them yet. Each has the default the PRD
builds with.

1. **Floors with one or two enemies.** "Enemy count less two" goes below zero when a
   floor has fewer than two enemies, which today's floors can have: one battle with one
   strong enemy. What does such a floor pay? *Default: the low end is held at 0, so one
   enemy pays 0–1 and two pay 0–2.* Alternatives: hold the low end at 1, so every
   fighting floor pays something, or draw −1…1 and treat a negative as 0, which makes 0
   likelier.
2. **The odds of the draw.** Is every count from (enemy count − 2) to the enemy count
   equally likely? *Default: yes, even odds, as the build does elsewhere.*
3. **When the count is drawn.** Is the floor's gold drawn again each time the floor is
   cleared, from the dive's own saved rolls like its loot? Or is it fixed when the
   dungeon is created, like its monsters? *Default: drawn each clear, from the dive's
   stream.*
4. **How the teleport fee reads.** "1 gold a floor in an F-rank dungeon, rising 1 a
   rank": does the rate per floor go 1, 2, 3… by rank (an E re-entry at floor 5 costs 10)?
   Or does the whole fee go up by 1 a rank (an E re-entry at floor 5 costs 6)? And is "the
   floor being returned to" the rest area's own floor number (5), or the floor the first
   battle is on (6)? *Default: a rate of 1, 2, 3… per floor, times the rest area's floor
   number.*
