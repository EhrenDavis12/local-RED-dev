# PRD: Health from Constitution

> **Status:** Draft · Source docs read: Guild Members.md, Combat.md, The Dungeon.md,
> Specialists.md, Individual Types.md, Equipment.md, Core Concept.md, and the EhrensDocs
> change notes against each (Combat, The Dungeon, Guild Members, Specialists, Core Concept,
> Equipment, Individual Types, Platform)

## Problem

Every member and every monster has 10 health, whatever its Constitution. A Tank with
Constitution 6 holds exactly as much as a Rogue with 3, levelling Constitution never adds
health, and a monster's pool ignores its stats entirely. Maximum health today comes from a
table indexed by rank or tier, which the originals have replaced: the "health set by rank"
change note was removed as overridden when EhrensDocs were reconciled against the
originals (queue report 48, row 6).

## Goal

A combatant's maximum health is its Constitution times ten — members (divers and
specialists alike) and monsters — and it follows Constitution as Constitution rises, with
no rank, tier or level term anywhere in it.

## Requirements

1. **Members.** A member's maximum health is their Constitution × 10. — *Guild
   Members.md, `## Base Stats`* ("A member's health is their Constitution times ten").
2. **Specialists follow the same rule.** A specialist is a member, has Constitution, and
   gains base stats the way divers do, so requirement 1 covers it unchanged; there is no
   separate specialist figure. — *Guild Members.md, `## Base Stats` and `## Levels and
   Experience`* ("Specialists gain base stats the same way divers do"); *Specialists.md,
   `## Equipment`* (a specialist's defence is "from Constitution alone").
3. **Monsters.** A monster's maximum health is its own Constitution × 10. — *Combat.md,
   `## Enemies`* ("built from the same six combat types as guild members, working the same
   way"); *EhrensDocs/The Dungeon.md*, change "The dungeon's enemies are monsters" ("uses
   the same stat rules").
4. **No rank, tier or level term.** Maximum health depends on Constitution alone. The
   by-rung health table and the flat new-member/monster figure are removed, not left as a
   fallback or a floor. Promotion changes maximum health only through Constitution, which
   promotion keeps. — *Guild Members.md, `## Base Stats`* ("with no separate rule for
   levelling … health needs no stat of its own"), *`## Promotion`* ("the stats already
   earned are kept"); report 48 row 6.
5. **It grows when Constitution rises.** When a level-up raises a member's Constitution,
   their maximum health rises by 10 per point at once, mid-dive included (level-ups land
   during a dive). What happens to their *current* health is a default — see Open
   Questions. — *Guild Members.md, `## Base Stats`* ("it grows as Constitution grows").
6. **Full in the hall.** A member not on a dive is at their full maximum health, including
   straight after a promotion or a level-up that happened in the hall. — *EhrensDocs/
   Combat.md*, change "Health is full at the guild hall" ("Back at the guild hall a
   member's health is back to full").
7. **Old saves load under the new rule.** Loading any save, including one written under
   the rank table, sets every member's maximum health from their saved Constitution; the
   saved maximum is not trusted. Members not on a saved dive load at full (requirement 6).
   A member on a saved dive keeps their saved current health, capped at the new maximum
   (default — see Open Questions). A saved mid-battle monster keeps its saved current
   health; its maximum comes from its saved stats. — *EhrensDocs/Combat.md*, change
   "Health is full at the guild hall"; the cap is today's load behaviour
   (`SaveManager.SetHealthFromRank`), kept.
8. **Health is not a placeholder.** The ×10 is a settled rule from the originals, not a
   tuning placeholder awaiting balance. — *Guild Members.md, `## Base Stats`*.

## Out of Scope

- How much health comes back between floors, at rest areas, or from a Cook — the healing
  item (report 48 row 5). It reads maximum health; this item only changes what that is.
- What monsters' Constitution is — monster level, rank and stats belong to the enemies
  item (report 48 row 12).
- What reaching 0 health means, and anything about injury.
- Constitution falling, potions, and any temporary Constitution change other than the
  support-ring case named in Open Questions.

## Open Questions

- **Going ahead with:** when Constitution rises mid-dive, the damage a member has already
  taken stays taken — current health rises by the same 10 per point that maximum health
  does. (The other reading: current health stays where it was and only the ceiling moves.)
  The docs say the pool grows, not what happens to what's left in it. Cheap to change.
- **Going ahead with:** health uses the combatant's own Constitution, not Constitution
  after support-ring help. Help raises a receiver's primary stat, and the Tank's primary
  stat is Constitution — the engine already counts helped Constitution toward the Tank's
  defence — so a literal reading would make a helped Tank's maximum health change with
  who stands next to it, and fall when they move away or die. *Guild Members.md, `## Diminishing
  Returns on Help`* and *`## Base Stats`* don't say which. Cheap to change.
- **Going ahead with:** a member on a dive saved under the old rule loads with their saved
  current health, capped at the new maximum — so a member at 7 of 10 loads at 7 of, say,
  50 — rather than keeping the damage they had taken. Only affects saves made mid-dive
  before this ships.
