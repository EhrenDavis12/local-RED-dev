# PRD: Gear Finds

> **Status:** Draft, queue #200 · Source docs read: The Dungeon.md, Equipment.md (originals);
> EhrensDocs/The Dungeon.md, EhrensDocs/Equipment.md, EhrensDocs/Open Questions.md,
> EhrensDocs/Platform.md, EhrensDocs/Look and Feel.md; code on `queue/200-gear-finds`
> (Dive.cs, DiveSave.cs, FallenGear.cs, LootRules.cs, MonsterGear.cs, GearPiece.cs,
> Dungeon.cs, Guild.cs, DiveScreen.cs).

Citation keys: **O-Dungeon** / **O-Equipment** are the other dev's originals; **E-Dungeon** /
**E-Equipment** are the EhrensDocs change notes, named by change title (likewise
**E-Platform**, and **E-Open Questions** by number). **D1–D5** are the
cheap, reversible defaults queue #200 recorded for the user; **P1–P2** are this PRD's own
proposals, also defaults, listed under Open Questions.

This feature reverses E-Dungeon "For now a dive drops ore, herb and healing potions, and no
gear" and the gear half of E-Equipment "For now no gear drops, and a mission yields only
gold" — the user's approved reversal, 25 Nov. Where those notes and the originals disagree,
the originals win (project rule, 18 Nov).

## Problem

A dive brings home gold, ore, herb and healing potions, and never a weapon or armour. The
originals have a dive drop gear on set floors; the game doesn't, so the only gear a guild
gets is bought, or arrives on a recruit.

## Goal

Clearing the last fighting floor before a rest area, or the dungeon's last floor, finds one
weapon or armour piece, rolled like any other piece at the dungeon's class and slid by
depth. The party carries it home in a slot under the existing room rules, loses it under the
existing turning-back and party-death rules, and it reaches the guild's stores with an ID.
The dive's result says what was found, brought home and lost.

## Requirements

### Where a find drops

1. A fighting floor **qualifies** when the floor after it is a rest area
   (`Dungeon.IsRestFloor(floor + 1)`), or when it is the dungeon's last floor. *[O-Dungeon
   § The Dungeon, "A weapon or a piece of armour drops on the last fighting floor before each
   rest area, and on the dungeon's last floor"]*
2. A qualifying floor finds **exactly one** piece, whatever its depth. A floor that qualifies
   both ways still finds one. *[D1; O-Dungeon § Open Questions, "how many pieces drop
   there"]*
3. A rest area is never fought, so it finds nothing, even when it is the dungeon's last floor.
   The last fighting floor before it already qualifies under 1. The starting dungeon
   (10 floors, rest areas on 5 and 10) therefore finds on floors 4 and 9 only. *[follows from
   1, 2 and 4; E-Dungeon "How a floor's power becomes its enemies, for now" for the depth]*
4. The find comes only when the floor is cleared, the same moment as the floor's gold and
   loot. A floor the party leaves early, by turning back or a stand-off, finds nothing. *[E-
   Dungeon "For now a dive drops ore…", "only once every battle on the floor is won", applied
   to gear by queue #200]*
5. A floor cleared again on a later dive finds again. The piece is drawn from the dive's own
   saved stream, **after** the floor's gold and loot, so the gold and loot a given seed
   produces are unchanged by this feature. *[P1, following loot and gold: E-Dungeon "For now
   a dive drops ore…" and "How a floor's gold count is drawn, for now"]*

### What the piece is

6. A find is a weapon or an armour piece at even odds, **never a shield**. Its kind is the
   weapon or armour kind of one of the six combat types, drawn at even odds. *[D2; O-
   Dungeon § The Dungeon, "a weapon or a piece of armour"]*
7. Its class is the dungeon's own rank. *[D3; O-Equipment § Where Gear Comes From, "its class
   comes from where it dropped — from the dungeon's own rank and how deep the floor is"]*
8. It is rolled exactly as a bought piece is (`GearPiece.Roll`: range, span and durability
   from the kind's bands), then its range slides toward the top of its band by the floor's
   place among the dungeon's fighting floors, **identically to a monster's piece**
   (`MonsterGear.Roll`'s slide). It starts at full durability. Durability does not slide. *[O-
   Equipment § Where Gear Comes From, "rolled the same way a crafted or bought piece is";
   D3; E-Dungeon "How a monster's gear is rolled and paid for, for now" for the slide]*
   - Testable edges: a find on the dungeon's first fighting floor does not slide; a find on
     its deepest fighting floor has its maximum at the top of its band; the slide never
     leaves the class's band.
9. A find gets **no Luck check** and no class bump. Those belong to a crafter, and a find has
   none. *[O-Equipment § Quality, the Luck check is "a pull from the crafter's own Luck bag"]*
10. The piece's figures are fixed when it is found. Reaching the stores never re-rolls it.
    *[O-Equipment § Quality, "rolled once, at creation, and fixed for the life of that piece"]*

### Carrying it

11. Until the dive ends, a find is the party's as a whole, like loot. It is not in the stores
    and cannot be equipped mid-dive. *[E-Dungeon "For now a dive drops ore…", "the party's as
    a whole"; E-Equipment "A member's gear can't change during a dive, for now"]*
12. A find takes `Tuning.GearSlotsPerPiece` slots (1). *[E-Equipment "A dead member's gear
    takes a slot a piece, for now"; O-Dungeon § The Dungeon, capacity in slots]*
13. The room is counted once, as the dive ends, exactly as it is now: the living members'
    free slots, after the potions and buffs they still hold. It fills in this order, and
    whatever does not fit is lost: *[D5; E-Dungeon "For now a dive drops ore…"; O-Dungeon
    § The Dungeon, "A drop the party has no room for is lost"]*
    1. fallen members' gear (`FallenGear.Returning`, unchanged);
    2. found pieces, deepest find first *[P2]*;
    3. loot (`LootRules.Keep`, unchanged).

    Why this order: fallen gear is already the guild's, so losing it costs something owned.
    It also keeps the settled rule that a fallen member's gear "takes its slots first"
    (E-Equipment, as above). A found piece comes before loot because it is the rarer and
    costlier find: at most one per run of floors, against units of ore, herb or potion.
14. A full party cannot throw anything away to make room. A find that does not fit is lost.
    *[D4; O-Dungeon § The Dungeon, "A drop the party has no room for is lost"]*
15. Going home at a rest area brings every find that fits under 13. *[E-Dungeon "For now a
    dive drops ore…", "Going home at a rest area brings everything that fits"]*
16. Turning back between rest areas, a stand-off included, loses every piece found since the
    last rest area the party passed, before the room is counted. A piece found before that
    rest area still comes home if it fits. *[O-Dungeon § The Dungeon, "Retreating always
    costs the loot gathered since the last safe floor"; E-Dungeon "A party can turn back
    anywhere…"]*
17. A party with no one left alive brings no find home. *[E-Dungeon "For now a dive drops
    ore…", "A party with no one left alive brings nothing out"]*

### Reaching the stores

18. A find that comes home goes into the guild's stores, held by no one, and only then takes
    a guild gear ID from `Guild.NextGearId`. A find that is lost never takes an ID and never
    touches the stores. *[queue #200; precedent E-Dungeon "How a monster's gear is rolled…",
    a monster's gear "never goes into the stores", and MonsterGear's "takes no guild ID"]*

### The result and the screen

19. `DiveResult` reports every piece **found** on the dive and every piece **brought home**,
    each with its kind, class and figures, the brought ones with their new IDs. The lost
    pieces are the found ones not brought home. *[queue #200]*
20. The victory list after a qualifying floor shows the piece among what the floor dropped,
    beside the gold and loot. *[E-Dungeon "A floor is a series of battles…", "After the last
    one comes victory, dropping loot"; queue #200]*
21. The end-of-dive panel adds one row, shown only when the dive found at least one piece,
    giving the pieces brought home of the pieces found: label "Gear home", value "<brought>
    of <found>" (e.g. "1 of 2").
    It is one row, not two, because the dive screen's left column has a fixed height: a
    fifth info row squeezes the Message zone until two-line messages overflow, so the panel
    stays at its four-row cap. Nothing more is drawn. *[queue #200, "keep any UI line
    minimal"; the dive screen's fixed left-column layout in source]*

### Saving

22. A dive saved and loaded mid-dive keeps every find it carries, with the same figures, and
    keeps which of them were found since the last rest area. A load never rolls a find
    again. *[E-Platform, "Nor does it roll a floor's loot again"; queue #200]*
23. A save from before this feature loads with no finds. A save whose find cannot be true is
    refused, the same way loot that cannot be true is: a shield, a kind or class that doesn't
    exist, a range below 0 or inverted, a maximum durability below 1, or a current durability outside
    0 to its maximum. *[E-Dungeon "For now a
    dive drops ore…" for loot's refusal; MonsterGear.IsSound for what a sound piece is]*

## Out of Scope

- Gear found on missions. O-Equipment says missions drop gear too; E-Equipment keeps a
  mission to gold for now, and that stands.
- Throwing something away to make room (D4).
- Showing which fallen or found pieces were lost on the end-of-dive screen. That is an open
  question in E-Dungeon "Questions on the dive's defaults", and only counts are shown here.
- What happens after the bottom floor of a dungeon that doesn't end on a rest area. That is
  open (E-Open Questions #27), and the starting dungeon's depth is fixed at 10, so it doesn't
  arise. A find on such a floor is still awarded on clearing it (1, 4).
- Shields as finds, and the enemy-type ladder.

## Open Questions

From the originals, answered here only by a default:

- A weapon or a piece of armour drops on the floor before each rest area and on the last
  floor, and it isn't said how many pieces drop there — one, or more the deeper the floor.
  *(D1: one.)*
- A drop the party has no room for is lost, which is the same rule a dead member's gear
  follows. Should a full party be able to throw something away to make room for a find
  instead? *(D4: no.)*

Queue #200's defaults, awaiting the user's word:

- D2: weapon or armour at even odds, never a shield, kind from a combat type drawn at even
  odds. Alternatives the code would support just as cheaply: the type of one of the cleared
  floor's own monsters, which would follow a future enemy-type ladder, or of a living party
  member, which favours gear the party can use.
- D3: class is the dungeon's rank, with MonsterGear's depth slide.
- D5: room fills fallen gear, then finds, then loot.

This PRD's proposals (not from the docs or the brief):

- P1: a floor cleared again on a later dive finds again, the way its loot and gold are rolled
  again. The alternative is once per floor per dungeon, which a player cannot farm.
- P2: when the room can't hold every find, the deepest one comes home first, since the slide
  makes it the better piece. This echoes loot's "a higher rank before a lower one". The
  alternative is the order found.
