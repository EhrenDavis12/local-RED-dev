# PRD: Mage's field wears armour

> **Status:** Draft · Source docs read: `Equipment.md`, `Combat.md`, `Individual Types.md`,
> `EhrensDocs/Equipment.md`, `EhrensDocs/Individual Types.md`, `EhrensDocs/Combat.md`,
> `EhrensDocs/The Dungeon.md`; source `src/guildmasters-descent` (`Battle.cs`,
> `MageType.cs`, `GearPiece.cs`, and the tests named below)

## Problem

When a Mage's lingering field hurts a character, the victim's armour, and a Tank's shield,
are rolled for its defence but spend no use. An ordinary strike that lands spends one use of
each piece the target has working (`Battle.Strike`, the `armour.Use()` / `shield.Use()`
lines); the field's hit (`Battle.FieldHurts`) never calls either, and its comment says so:
"rolled fresh, armour first, but not worn". So armour standing in a monster Mage's field
lasts longer than the design says it should, and breaks later in a dive than it would.

No design doc says the field spares armour. `Equipment.md` says the opposite: armour "wears
from everything", and it names the Mage's field among the specials whose hits still wear
armour.

Three existing tests assert the current behaviour and have to be inverted, not kept:

- `CombatShieldTests.AFieldHitWearsNeitherTheArmourNorTheShield_ShieldR10_R13`
- `CombatMageTests.TheFieldIsAnAreaAttackThatCannotMiss_…_R25_R14`, the assertion "the
  field wears no armour"
- `DamageMathTests.TheFieldStillSpendsNoUseOfTheStaff_AndItsHitsWearNothing_R17`. It only
  checks the staff, which stays true, but its name says the hits wear nothing.

## Goal

Every time a Mage's field hurts a character, that character's working armour spends one
use, and so does a Tank's working shield, exactly as when an ordinary strike lands on them.
The field still costs the Mage's own staff nothing.

## Requirements

1. **Each field hit spends one use of the victim's working armour.** This covers both ways
   the field hurts someone: a character standing in it when it begins its own attack (a
   special counts as beginning an attack), and a character moving into it. One field hit
   is one use.
   — `Equipment.md` `## Durability`, paragraph "A special spends none of the attacker's own
   weapon durability…" ("Armour spends durability for every hit it takes regardless, whoever
   lands it and whether it came from an ordinary attack or a special … armour wears from
   everything", and the Mage's field is named in it); `Equipment.md` `## Quality` (armour
   "counts down by hits taken"); `EhrensDocs/Individual Types.md` "Where the Mage's field
   lies, and what it does, for now" (the two ways it does damage, and a special counting
   as beginning an attack)

2. **Every field hit counts, with no exceptions for what it did.** A field hit never rolls
   to hit, so it never misses, and each one spends the use even if:
   - defence takes all of its damage,
   - it kills the victim, or
   - the victim is a vanished Rogue.

   — `EhrensDocs/Equipment.md` "A hit that does nothing still wears gear"; `Equipment.md`
   `## Durability` ("every hit it takes regardless"); `EhrensDocs/Individual Types.md`
   "Where the Mage's field lies…" (no hit roll; it hurts a vanished Rogue too)

3. **A Tank's working shield spends one use on each field hit as well, alongside the
   armour.** The two wear independently, just as they do on a strike: each working piece
   spends its own use. A broken piece, or an empty slot, spends nothing.
   — `EhrensDocs/Equipment.md` "The Tank carries a shield, and shields can be swapped",
   the "For now" paragraph ("It spends one use on every hit that lands on the Tank, wherever
   the armour spends one"); "A broken shield adds nothing, and a working one outlasts broken
   armour". This is a for-now default with its question still open; see Open Questions.

4. **The field hit that spends a piece's last use is still defended by that piece in full.**
   The piece is broken from then on, so any later hit faces the victim without it. That
   includes a second overlapping field hitting the same character in the same moment, and a
   strike later on.
   — `Equipment.md` `## Durability`, first paragraph ("works fully until it reaches zero,
   then breaks and contributes nothing") and the paragraph "Both a weapon and an armour can
   break partway through a multi-strike sequence…"; ordinary strikes already behave this
   way (`Battle.Strike`: defence is rolled before `Use()`)

5. **The field still spends no use of the Mage's weapon.** Neither the staff roll taken
   when the field is cast nor any of the field's hits spends a staff use.
   — `Equipment.md` `## Durability` ("the Mage's field cost the weapon nothing … a weapon
   only wears from ordinary attacks"). The code already does this, and it must stay true.

## Out of Scope

- **Everything else about a field hit stays as it is:** its damage, the order of its rolls
  (armour, then shield, no hit roll), that it adds nothing to any bar, how it triggers a
  potion, and Vanish.
- **Monster gear.** For now monsters carry no gear (`EhrensDocs/The Dungeon.md`), so in
  practice only a monster Mage's field, lying on the party's grid, has armour to wear.
  Giving monsters gear, including the Battle Test fixture's armoured enemies, is a
  separate question.
- Shields Up and the shield. It already spends no shield use, and that does not change.
- How durability or condition is shown to the player.
- The field's open timing questions (`EhrensDocs/Individual Types.md` "Questions on the
  field's timing").

## Open Questions

- What wears a Tank's shield down — every time the Tank is hit, the same as armour; only
  when the Tank uses Shields Up; or both?
  (`EhrensDocs/Equipment.md`, "Questions on shields and potions".) Requirement 3 follows
  the for-now default, which is every hit, the same as armour. If the answer turns out to
  be "only when the Tank uses Shields Up", requirement 3 is reversed, and so is the shield
  wear on ordinary strikes.
