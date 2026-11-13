# PRD: Healing in the dive becomes percentages

> **Status:** Draft · Source docs read: The Dungeon.md, Specialists.md, Guild Members.md,
> Combat.md, Core Concept.md, Equipment.md, Individual Types.md, and every change note in
> EhrensDocs/ (The Dungeon, Specialists, Guild Members, Combat, Platform, Core Concept,
> Equipment, Individual Types). Code read: `Core/Dungeon/Dive.cs`, `Core/Tuning/Tuning.cs`,
> `Tests/EditMode/DiveRestTests.cs`, `DiveRulesTests.cs`, `DiveHealthTests.cs`.

## Problem

The dive heals in flat points that predate health following Constitution: the Cook gives 1
health to everyone after every battle won, a rest area gives 3 (+2 per Cook), and nothing
comes back between floors. Now that maximum health is Constitution × 10, a flat 3 is a
rounding error for a sturdy member and a big heal for a frail one, and the Cook heals two
or three times a floor where the docs say once.

## Goal

Every heal in a dive is a share of each member's maximum health, at the moments the docs
name and no others: 5% between floors, 15% at a rest area, and the Cook's 5% / 15% on top,
with nothing between the battles of one floor.

## Requirements

**When healing happens**

1. Clearing a floor whose next floor is an ordinary (battle) floor heals every living
   member by the floor heal, 5% of their maximum health. — The Dungeon.md, The Dungeon
   ("Between floors, every member gets back five per cent of their maximum health").
2. Winning a battle that is not the floor's last heals no one — the Cook's after-battle
   heal goes. — The Dungeon.md, The Dungeon ("nothing comes back between the battles on a
   single floor"); Specialists.md, The Cook ("between floors").
3. Clearing the floor before a rest area heals every living member by the rest-area heal,
   15%, **instead of** the floor heal — not 15% plus 5%. *Placeholder default, cheap to
   change.* — The Dungeon.md, The Dungeon (the 15%); the "instead of" is the build's choice
   on the open question below.
4. Pushing on from a rest area to the next floor heals no one. This follows from 3: the
   rest area stands in for the floor heal on both sides of it, so floors 4 → 5 → 6 give one
   15% and no 5% on either side. *Placeholder
   default, same question as 3.* The built dive already moves from floor 5 to floor 6 with
   no heal (`Dive.PushOn`), so this reading needs no change there.

**The Cook**

5. Each living Cook adds 5% to the floor heal and 15% to the rest-area heal, for every
   living member, the Cook included. — Specialists.md, The Cook ("another five per cent …
   a further fifteen per cent — on top of what the party gets anyway").
6. Two Cooks add twice as much; each living Cook adds its share. — EhrensDocs/Specialists.md,
   "Two Cooks heal twice as much, for now".
7. A Cook's share is the same at every level and tier. *Placeholder default, cheap to
   change* — see Needs-your-call note under Open Questions.
8. A Cook dead before the heal adds nothing. *Default, cheap to change.* (Built behaviour
   today; no doc says otherwise.)

**How much**

9. A heal is a percentage of the member's maximum health at the moment it lands — after
   the cleared floor's experience is shared, so a level-up on that floor counts. *Default,
   cheap to change.*
10. All the percentages that apply to a member at one moment are added up first, then
    turned into health once: one living Cook between floors is 10% of maximum, not two
    separately-rounded 5%s. *Default, cheap to change.*
11. A fraction of a point rounds **up**, so every living member gets at least 1 health back
    from any heal (5% of 30 = 1.5 → 2; 5% of 10 = 0.5 → 1). *Default, cheap to change.*
    While maximum health is a multiple of ten and every percentage a multiple of five, the
    only fraction possible is a half, so rounding up and rounding half up give the same
    numbers.
12. A heal never takes a member above their maximum health. — built behaviour (`Dive.HealLiving`).
13. A dead member is never healed: no heal brings anyone back from 0. — The Dungeon.md, The
    Dungeon ("Death in the dungeon is permanent").

**Tuning**

14. The four percentages — floor heal 5, rest-area heal 15, Cook floor share 5, Cook
    rest-area share 15 — live in `Tuning.cs` as `[Placeholder]` values, replacing
    `RestAreaHeal`, `CookHealAfterBattle` and `CookHealAtRestArea`. — the build's choice; the
    figures are The Dungeon.md and Specialists.md's.

## Out of Scope

- Re-entering at a rest area by teleport: the party arrives at full health from the guild
  hall, so it heals nothing on arrival, as now.
- What happens when a dungeon's bottom floor is cleared and it is not a rest area — open in
  EhrensDocs/The Dungeon.md and does not come up for the starting dungeon.
- Growth of the Cook's heal with level or promotion (queue report #59).
- Showing heal amounts on screen; the dive screen already shows current / maximum health.
- Health after a dive (back to full at the guild hall — EhrensDocs/Combat.md, unchanged).

Existing tests that assert the flat figures (`DiveRestTests` R19/R20, `DiveRulesTests`
`Tuning_*Heal*`, `DiveHealthTests` line 170) describe the behaviour this PRD replaces.

## Open Questions

- A rest floor is still a floor. Does arriving at one give the fifteen per cent only, or
  the five per cent for the floor as well? (Guild Members.md, Open Questions. Built for now
  as "fifteen per cent only", requirements 3–4; queue report #61 lays out the readings.)
- Do two Cooks both heal? (EhrensDocs/Specialists.md. Built for now as yes, twice as much,
  requirement 6.)
- How does a Cook's heal grow? Specialists.md, Tiers says "For a specialist, promotion
  makes the same ability stronger", and Guild Members.md, Levels and Experience says a
  specialist's "specialty improves alongside" its stats; neither gives a rule. Built for
  now as flat (requirement 7). (Queue report #59.)
- Proposed by the PRD author, not in any doc: which way does a heal's fraction of a point
  round? Built for now as up (requirement 11).
- Proposed by the PRD author, not in any doc: are the Cook's and the party's percentages
  added before rounding, and is the percentage taken of the maximum after the floor's
  level-ups? Built for now as yes to both (requirements 9–10).
