# PRD: The Special Bar, per the originals

> **Status:** Draft · Queue item #52 · Source docs read: Combat.md, Individual Types.md,
> The Dungeon.md, Equipment.md, Core Concept.md, Guild Members.md, Specialists.md, and the
> change notes in EhrensDocs/ (Combat, Individual Types, The Dungeon, Platform, Equipment,
> Core Concept, Guild Members, Specialists); queue/reports/48-reconcile-ehrensdocs.md.
> Where a change note and an original disagree, the original wins (user, 2026-11-12).

## Problem

The built bar charges by the wrong rules (reconcile report #48, table row 3):

- The base +10 is added once per attack, hit or miss (`Battle.Execute`, `plan.ChargesBar`),
  so a Brute cleave landing three hits charges the same as a Tank shot that misses.
- Each type's bonus is 4–10 (`Tuning.BruteMultiHitCharge` … `MageColumnHitCharge`), not 15.
- Every bar starts each battle empty (`Dive.BeginBattle`, its "default D13"), and the dive
  save has nowhere to hold a bar between battles (`DivePartyMemberSave` is id + cell).

## Goal

A bar charges 10 for every hit its owner's ordinary attacks land and 15 each time its type's bonus condition
is met, caps at 100, carries from battle to battle within a floor, empties when the party
moves to a new floor, and survives the game closing at any point of the dive — with every
save made by an older version still loading.

## Requirements

### Charging

1. **Base charge is per hit landed.** Each strike that hits adds 10 to its attacker's bar; a
   miss adds nothing. A multi-strike attack charges once per strike that lands; an attack
   that reaches several targets charges once per target it lands on — the Brute's cleave
   and the Mage's column charge up to 30. A hit counts whatever damage it does, as it does
   for durability. A special's own hits charge nothing — the flurry, Volley, the two-row
   cleave and the Mage's field alike, since the bar fills from what wears the weapon and a
   special wears it not at all. A special puts nothing at all into its owner's bar — no base
   and no bonus, so a Brute's two-row cleave landing on two or more enemies earns no +15 —
   with the Fighter's refill to 90 (requirement 4) the one exception, because Individual
   Types.md spells it out. — Combat.md § The Special Bar ¶1, ¶2; Equipment.md § Quality
   "what's counted is hits landed, not strikes made", § Durability ¶5. *(Our change note
   disagrees; the originals win — see Open Questions.)*
2. **A Luck-reset free attack charges like any other attack.** — Combat.md § The Luck Reset
3. **Each time a type's bonus condition is met it adds 15**, on top of the base. How often
   each condition is met uses the change notes' defaults, unchanged by this feature: the
   Brute once per attack whose hits land on two or more different enemies; the Tank per enemy
   strike aimed at him, hit or miss; the Rogue per enemy strike it evades; the Archer per
   hit that continues its streak (Volley neither continues nor breaks it); the Mage per enemy
   strike landing on an ally in front of it in its column. — Combat.md § The Special Bar ¶1;
   Individual Types.md, each type's sheet; EhrensDocs/Individual Types.md, the "for now"
   notes on the Brute, Tank, Rogue, Archer and Mage
4. **The Fighter's bonus stays the refill**: if any enemy is killed during the flurry, the bar
   is set to 90; the flurry's own strikes charge nothing. — Individual Types.md § The
   Fighter. *(Conflicts with "adds 15" in Combat.md — see Open Questions.)*
5. **The bar is full at 100 and caps there.** Charge arriving while it is full — base or
   bonus — is lost, not banked. — Combat.md § The Special Bar ¶1, ¶3
6. **Monsters' bars charge by the same rules** as members'. A specialist has no bar and
   charges nothing; a specialist's between-battles entry in the dive save writes 0 and is
   ignored on read. — EhrensDocs/The Dungeon.md "The dungeon's enemies are monsters";
   Combat.md § Specialists in Combat
7. The three figures — 10, 15, 100 — are settled by the originals and are no longer tuning
   placeholders. — Combat.md § The Special Bar ¶1

### Carrying

8. **A member's bar at the end of a won battle is what it starts the floor's next battle
   with**, part-filled or full. — Combat.md § The Special Bar ¶3 ("the special is never
   lost"), ¶4
9. **Moving to the next floor empties every member's bar** — after a floor's last battle is
   won, and on pushing on from a rest area. A rest area is a floor, so arriving at one
   empties the bars too. — Combat.md § The Special Bar ¶4; The Dungeon.md § The Dungeon
   ("every 5th floor is a safe rest area"). *(Whether a full bar is emptied too is open.)*

### Saving

10. **A dive saved between battles holds each member's bar**, and loading it carries the dive
    on with those bars; a dive saved mid-battle keeps holding each combatant's bar in the
    battle as it does today, and that battle's end carries them on per requirement 8. —
    EhrensDocs/Platform.md § Saving ¶2, ¶3
11. **The save format version goes from 4 to 5.** A version 1–4 save still loads: a dive saved
    between battles loads with every bar empty — what those versions played by — and a
    battle saved mid-fight loads its combatants' bars as saved. (That a version 4 game
    reports a version 5 save as newer already holds, at `SaveManager.cs:150`, and is not
    tested here.) — EhrensDocs/Platform.md § Saving ¶5;
    `SaveFile.CurrentVersion`, `Dive.BeginBattle`

## Out of Scope

- Using a member's special from the battle screen — the bar still fills and sits full (queue
  item 9, after the engine; EhrensDocs/Combat.md "How a member with no target picks one").
- How the bars read at a glance with fifteen members (open in Combat.md).
- Whether using a special costs the member an ordinary attack, and when a special fires.
- Damage math, cooldowns, the Luck reset's chance, lasting effects, and how each special
  works.

## Open Questions

- **Do a special's own hits charge the bar it just emptied?** (reconcile report #48.) Combat.md
  says "what wears a weapon down is what fills the bar", and Equipment.md § Durability ¶5 says
  a special wears the weapon not at all. Our change note disagrees — yes "for now, unless its
  type says otherwise" (EhrensDocs/Combat.md "A special's own hits charge the bar, for now")
  — and the originals win. *Default for now: a special's hits charge nothing (requirement
  1).*
- **Can a special earn its owner's bonus condition?** Only the Brute's two-row cleave can meet
  one today (two or more enemies hit); no doc says whether it pays. *(Mine.)* *Default for
  now: no — a special puts nothing into its owner's bar, the Fighter's refill to 90 excepted.
  Cheap to change: one condition.*
- **Do the Mage's field's hits charge the Mage's bar?** *(Mine.)* *Default for now: field
  damage charges nobody* — as built, and now in agreement with the default above.
- **The Fighter: 15, or refill to 90?** Combat.md gives every type's bonus +15; Individual
  Types.md says the Fighter's bonus *is* the refill to 90%. *(Mine.)* *Default for now: the
  refill to 90, nothing more.*
- **Does moving to the next floor empty a full bar too, or only a part-filled one?** Combat.md
  says "the special is never lost" and "a part-filled bar … moving to the next floor resets
  it". *(Mine.)* *Default for now: every bar empties, full or not.*
- **Does a bar survive the dive ending?** Turning back, a stand-off, going home, and
  re-entering at a rest area all end or start a dive. *(Mine.)* *Default for now: every dive
  starts with every bar empty; the bar is dive state, not kept on the member.*
- **A saved bar below 0 or above 100** — refuse the save, or fix it as it loads, the way
  Platform's gear rule does? *(Mine.)* *Default for now: clamp it into 0–100 and load* —
  between-battles bars and every combatant's bar in a mid-battle save alike (today
  `BattleSnapshot.cs:122` assigns it unchecked).
- **A version 5 save holding a non-zero bar where every bar should be empty** — at a rest
  area, or before a floor's first battle. *(Mine.)* *Default for now: zero those bars on
  load.*
- How often does each type's bonus condition pay? The sheets name the condition, not how many
  times it pays in one attack. (EhrensDocs/Individual Types.md, proposed open question;
  requirement 3 builds on its "for now" defaults.)
