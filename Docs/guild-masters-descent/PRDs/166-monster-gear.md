# PRD: Monster Gear (queue #166)

> **Status:** Draft, 2026-11-25 · Source docs read: The Dungeon.md, Combat.md, Equipment.md,
> Battle Test.md, Guild Members.md, Individual Types.md, Specialists.md, Core Concept.md,
> and the change notes under EhrensDocs/ (The Dungeon, Equipment, Guild Members, Combat,
> Platform, Look and Feel, Core Concept). Code read on `queue/166-monster-gear`:
> `Core/Dungeon/Dungeon.cs`, `PowerBudget.cs`, `Dive.cs`, `Core/Combat/Battle.cs`,
> `BattleSnapshot.cs`, `Combatant.cs`, `Core/Guild/GearPiece.cs`, `GearBands.cs`,
> `GearKind.cs`, `Xp.cs`, `Core/Save/SaveManager.cs`, `SaveFile.cs`.

## Problem

Every monster fights bare: it attacks for its stat alone and defends with Constitution
alone (`Combatant.cs`: "Null for a monster: it has no gear and no slots"). The originals
have depth make enemies likelier to be equipped and better equipped, and have that gear
paid for out of the floor's power, so a deep floor plays the same as a shallow one apart
from numbers. The user answered on 2026-11-24 to give monsters gear the way the originals
say.

## Goal

When a dungeon is created, each of its monsters may be given a weapon and, from floor 11,
armour of its own type's kind, at a chance set by the floor; the pieces are rolled from
the same bands as members' gear and are better deeper down; each piece's worth is part of
what the monster costs, so armed battles field fewer enemies; in a fight a monster's gear
adds, wears and breaks exactly as a member's does; and the gear is saved with the dungeon
and with a battle saved partway through. Older saves load with their monsters unarmed.

## Requirements

### How likely a monster is to be armed

1. **Three figures per dungeon.** When a dungeon is created it rolls, once: a weapon start
   of 1, 2 or 3; a rise of 5, 6 or 7; and an armour start of 3, 4 or 5. Each is a whole
   number at equal odds, drawn in that order: weapon start, rise, armour start. The armour
   chance rises by the same rise as the weapon chance.
   *Source:* The Dungeon.md § The Dungeon ("1 to 3 per cent … rises 5 to 7 points a floor;
   armour's chance starts on floor 11 at 3 to 5 per cent and rises at the same rate");
   Battle Test.md § The Test Dungeon (one start and one rise run through the whole table,
   in whole per cent). Equal odds is a default (D1).
2. **The chance on a floor counts every floor, rest areas included.** On floor `f`:
   weapon chance = start + rise × (f − 1); armour chance = 0 below floor 11, else armour
   start + rise × (f − 11). A chance of 100 or more means always. *Test:* with figures
   2 / 6 / 4 the chances on floors 1, 2, 4, 6, 9, 11, 14 are weapon 2, 8, 20, 32, 50, 62, 80
   and armour 0, 0, 0, 0, 0, 4, 22 — the Test Dungeon table. *Source:* The Dungeon.md
   § The Dungeon; Battle Test.md § The Test Dungeon (floor 6 is 32%, so floor 5's rest area
   counts).
3. **The roll is per monster.** Each monster rolls its own weapon chance, then its own
   armour chance, independently. A chance roll is `rng.NextInt(0, 100) < chance`, the
   game's existing habit (`RecruitingBoard.cs:90`), and it is always drawn, even when the
   chance is 0 or below (armour before floor 11) or 100 or above, so the draw order never
   depends on the floor. *Source:* Battle Test.md § The Test Dungeon ("the chance each enemy
   on that floor has of carrying one"). Order, independence and always drawing are a
   default (D2).
4. In today's 10-floor starting dungeon armour's chance is 0 on every floor, so its
   monsters carry weapons only. This is a consequence, not a special case: nothing caps
   armour to the starting dungeon. *Source:* EhrensDocs/The Dungeon.md change "How a
   floor's power becomes its enemies, for now" (10 floors deep).

### What the gear is

5. **Kind.** A monster's weapon is its type's weapon kind and its armour its type's armour
   kind, as for members. A monster never carries a shield. *Source:* Battle Test.md § The
   Test Dungeon ("any gear an enemy has is of its own type's kind"); Equipment.md § What a
   Member Carries; Battle Test.md § The Enemy Team (the enemy Tank has armour and no
   shield).
6. **Class.** A monster's piece is the class of the monster's own rank. *Default (D3).*
   Equipment.md § Where Gear Comes From ties a dungeon drop's class to the dungeon's rank
   and depth but gives no formula.
7. **Rolled like any piece.** The range and the durability are rolled from the same bands,
   by the same span and placement rules, as any member's piece, and the piece starts at
   full durability. *Source:* Equipment.md § Quality; EhrensDocs/Equipment.md change "A
   span is counted in whole figures, ends included".
8. **Better deeper down.** After the roll, the piece's span is moved toward the top of its
   band by the floor's place in the climb: not at all on the dungeon's first fighting
   floor, all the way to the top on its deepest, keeping its rolled width. The move is
   worked in whole numbers, never a floating-point climb: on fighting floor `k` of `n`
   (fighting floors only, 1-based), move = `(k − 1) × (band max − piece max) / (n − 1)`,
   rounded down; 0 when `n` is 1. *Test:* starting dungeon (8 fighting floors),
   knife band 2–12, piece rolled 2–4: fighting floor 1 → 2–4; fighting floor 4 (climb
   3/7) → 5–7; fighting floor 8 → 10–12. Durability is not moved. *Source for "better":*
   Combat.md § Enemies ("depth sets … how good that gear is"); the mechanism copies
   Equipment.md § Quality's Luck raise (moving the span toward the top, keeping its width).
   The mechanism is a default (D4).

### What gear costs, and how it changes a battle

9. **A piece's worth** is the middle of its range as it stands after requirement 8's
   slide, `(min + max) / 2`, an exact half rounding up. *Test:* axe 9–13 is worth 11; knife 4–7 is worth 6. *Source:* The
   Dungeon.md § The Dungeon ("a piece being worth the middle of its rolled range"). The
   rounding is a default (D5).
10. **An enemy's cost is its stat points plus its gear's worth**, and arming enemies means
    fewer of them in the battle. *Source:* The Dungeon.md § The Dungeon; Battle Test.md
    § The Test Dungeon ("Gear is bought out of the same points as the enemy itself"). See
    Open Questions — two change notes read the other way.
11. **How a battle is filled.** The battle rolls its cost multiplier exactly as today. Then
    enemies are drawn one at a time, up to 15. Each drawn enemy costs the rolled cost plus
    the worth of whatever gear it rolled. An enemy is kept if it is the first, or if the
    running total of kept costs including it is no more than the battle's share; the first
    enemy that does not fit is discarded and drawing stops. *Test:* with no piece rolled
    the count is exactly `PowerBudget.EnemyCount(share, rolledCost)` for every share and
    cost; share 100, rolled cost 30, first enemy armed with an axe worth 11 and the rest
    unarmed → two enemies (41 + 30 fits, a third would make 101).
    *Default (D6)*; it reduces to the built rule when nothing is armed.
12. **Every kept enemy has the same stat points:** (share − total worth of the kept
    enemies' gear) ÷ count, to the nearest whole point, an exact half rounding up, and
    never below 5. Its stats are those points dealt by the existing 8 : 7 : 6 : 5 : 4 rule,
    and its cost is those points plus its own gear's worth. *Test:* the axe example above
    gives stat points 45 each and costs 56 and 45; with nothing armed the points equal
    `PowerBudget.PointsEach` for that floor, battle and count, the first- and last-floor
    whole-number arithmetic included; share 20, rolled cost 40, the lone enemy armed with a
    piece worth 22 → stat points 5, cost 27. *Source:* EhrensDocs/The Dungeon.md change "How a floor's power
    becomes its enemies, for now" (equal points, the rounding, the 5-point floor, a battle
    may spend a little more or less than its share). Extending it to gear is a default
    (D6).
13. **A kill pays on the whole cost**, gear's worth included, never on the stat points.
    *Source:* EhrensDocs/Guild Members.md change "A kill pays on the enemy's cost, exactly";
    Guild Members.md § Levels and Experience.
14. **Draw order, per battle:** the cost multiplier; then for each enemy drawn, in turn, its
    type, its weapon chance (always drawn, requirement 3), its weapon's rolls if armed (in
    `GearPiece.Roll`'s order), its armour chance (always drawn), its armour's rolls if
    armoured; then the kept enemies' nodes, in order, by the existing partial shuffle. A
    piece's rolls are drawn only for a piece the monster gets. The dungeon's three figures
    (requirement 1) are drawn right after the depth. A played mission (`PlayedMission.cs`)
    and the demo battle keep today's draw order unchanged (D11). *Default (D7).* Given a
    seeded RNG the whole dungeon is reproducible. The rule is not bent to keep existing
    #188 tests green: those that assume unarmed monsters (`FloorPowerDungeonTests.cs`
    ~188–206, with `ConstantRng(false)`, under which every chance roll arms the monster)
    are narrowed to unarmed battles.

### In a fight

15. **Gear adds exactly as a member's does.** A monster's damage is its damage stat plus a
    roll of its working weapon; its defence is Constitution plus a roll of its working
    armour. Everything that rolls a member's weapon or armour rolls a monster's the same
    way — an ordinary strike, a field hit on it, the Mage's field amount, the Tank's
    Shields Up figure. *Test:* a level-1 enemy Fighter with Strength 9 and a two-handed
    sword 8–11 strikes for 17–20 before defence. *Source:* Battle Test.md § The Enemy Team;
    Combat.md § Enemies ("working the same way"); Equipment.md § What a Member Carries.
16. **Gear wears and breaks exactly as a member's does:** a weapon spends a use per hit it
    lands from an ordinary attack and none from a special; armour spends a use per hit
    taken, field hits and specials included, even a hit defence absorbs whole; a broken
    piece adds nothing, and can break partway through a multi-strike attack. *Source:*
    Equipment.md § Durability; EhrensDocs/Equipment.md change "A hit that does nothing
    still wears gear".
17. **Wear lasts the battle only.** Each battle builds its monsters from the dungeon's saved
    pieces at their saved durability, and the wear a battle does is never written back to
    the dungeon, the same as a monster's health. Re-fighting a floor on a later dive meets
    the same pieces as they were made. *Default (D8).*
18. A battle can be given a monster's weapon and armour directly, each optional, each at
    any current durability from 0 up — so a hand-set fixture can field armed monsters.
    How a hand-placed armed monster's cost and stats are set is #167's to decide; here a
    hand-placed monster's cost and stats stay as today. *Source:* Battle Test.md § The
    Enemy Team (enemies at 10 durability).

### Saving

19. **Saved with the dungeon.** Each dungeon monster's weapon and armour, when it has them,
    are saved with it — kind, class, range, maximum and current durability. A loaded
    monster has exactly the stats, cost and gear it was made with, whatever later changes
    to the worth rule (requirement 9) or the bands — so its stat points are kept as a figure
    of their own, as its cost already is, and never worked back out from cost less worth.
    A monster with no gear has stat points equal to its cost. *Source:* EhrensDocs/The Dungeon.md
    change "A floor's monsters are the same every dive, for now".
20. **Saved in a battle.** A battle saved partway through holds each monster's pieces at
    their current durability, and restores to play on exactly as the original would have.
    *Source:* `BattleSnapshot.cs` (the existing contract: a restored battle plays the rest
    exactly as the original).
21. **Older saves.** The save version rises to 18. A save from version 17 or earlier loads
    every dungeon monster, and every monster in a saved battle, with no gear and with the
    cost and stats it had; no dungeon is rerolled. A monster saved with no weapon or no
    armour loads with none — never as a zero-figure piece (`JsonUtility` turns a missing
    nested object into a default one; see `SaveFile.cs`'s `HasDive`). *Source:*
    EhrensDocs/The Dungeon.md change "A floor's monsters are the same every dive, for now"
    ("a dungeon from an older save keeps the monsters it was made with"); EhrensDocs/
    Platform.md (a save from an older version still loads).
22. **A saved piece that cannot be true** — the wrong kind for the monster's type or slot,
    an undefined class, a minimum below 0 or above its maximum, a maximum durability below
    1, a current durability below 0 or above its maximum, or a monster whose stat points
    are under 5 or above its cost — makes the save corrupt, the same as an impossible
    dungeon monster does today. The same check, with the same result, applies to a
    monster's pieces in a battle saved partway through. Nothing is checked against the
    bands. *Default (D10).*
23. **Monster gear is not the guild's.** It never enters the stores, never takes a guild
    gear ID or moves the guild's gear counter, and is never shown in the Dorms or the shop.
    *Default (D9).*

## Defaults taken

Each is written into the requirements above. Every one changes only how new dungeons are
generated or how a battle runs; none changes the save's shape, and a dungeon already made
keeps the monsters it was made with — so changing a default later reaches new games only.

- **D1 — Equal odds on the three figures** (req 1). The doc gives ranges, no weighting.
- **D2 — Weapon roll then armour roll, independent, both always drawn** (req 3). The docs
  give two chances and no link; always drawing keeps the draw order the same on every
  floor.
- **D3 — Piece class = the monster's rank** (req 6). Every monster is F today, so every
  piece is F; the doc gives no depth-to-class formula.
- **D4 — "Better deeper" = the span slides toward the band's top with the climb** (req 8).
  Borrows the Luck raise's own mechanism and stays inside the class's band, so F gear
  never outclasses F. It is a balance lever: deep weapons are worth more, so deep armed
  battles shrink more.
- **D5 — Worth rounds an exact half up** (req 9). Matches #188's half-up rounding.
- **D6 — Fill the battle enemy by enemy; equal stat points; at least 5** (reqs 11, 12).
  Reduces to the built rule when no one is armed, keeps the doc's "fewer of them", and
  lets a lone enemy overspend its share as the built rule already does.
- **D7 — Draw order** (req 14). Any fixed order would do; this one rolls gear before the
  count needs it.
- **D8 — Wear is not written back to the dungeon** (req 17). The saved piece already holds
  a current durability, so writing wear back later needs no new save shape.
- **D9 — Monster gear sits outside the guild's stores and IDs** (req 23). Loot (#194, #200)
  can give a piece an ID when it ever enters the stores.
- **D10 — An impossible saved piece is a corrupt save** (req 22). Consistent with today's
  dungeon checks; making it a repair instead is a local change.
- **D11 — Played missions and the demo battle stay unarmed** (Out of Scope). They have no
  floor, so the floor chance does not apply.
- **D12 — The three figures are not saved** (req 1). Each monster's gear is saved, which is
  all play needs; a board that shows the chance later would need them added.

## Out of Scope

- Monster gear dropping as loot, or coming home in any form — #194, #200.
- The Battle Test fixture's armed enemy team — #167. Requirement 18 is all it needs from
  here.
- The Test Dungeon fixture — #201. Requirement 2 takes its figures (2 / 6 / 4) as given.
- Monsters on a mission played by hand, and the demo battle: no gear (D11).
- Anything on screen. A character's art never changes with its gear (EhrensDocs/Look and
  Feel.md, "Gear and the art"), and no panel shows a monster's gear.
- Floor gold by enemy count (#199). Under requirement 11 an armed floor fields fewer
  enemies, so once #199 lands an armed floor pays less gold; nothing here changes the gold.
- Monster shields, monster gear repair, and a depth-to-class step above the monster's rank.

## Open Questions

- **Does arming an enemy shrink the battle, or come out of the enemy's own stats?** The
  original says "An enemy's cost is its stat points plus what its gear is worth … so
  arming an enemy means fewer of them on the floor" (The Dungeon.md § The Dungeon), and
  Battle Test has gear "bought out of the same points as the enemy itself". Two change
  notes say gear "can take part of the points without changing what a kill pays"
  (EhrensDocs/The Dungeon.md, "How a floor's power becomes its enemies, for now";
  EhrensDocs/Guild Members.md, "A kill pays on the enemy's cost, exactly"), which reads as
  the count unchanged and the stats paying for the gear. This PRD follows the original,
  under the project's rule that the originals win; the battle's total pay stays at about
  its share either way. Reading it the other way would also need a rule for gear worth
  more than an enemy's whole points (a deep F enemy has about 10 points; a top-band bow is
  worth about 22).
