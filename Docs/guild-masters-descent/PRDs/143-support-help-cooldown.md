# PRD: Support-ring help shortens a Rogue's or an Archer's cooldown

> **Status:** Draft, queue item #143, size S · Source docs read: `Battle Test.md`,
> `Guild Members.md`, `Combat.md`, `Individual Types.md`, `Specialists.md`,
> `EhrensDocs/Combat.md`, `EhrensDocs/Guild Members.md`, `EhrensDocs/Open Questions.md`;
> source `Assets/Scripts/Core/Combat/Battle.cs` (`HelpBonus`, `WaitOf`)

## Problem

The game gets two numbers wrong against the original docs:

- **Help rounding.** The first help comes out as `max(1, 5% × stat)` before the total is
  rounded down. It is never rounded up on its own, so 5% of 30 gives 1 point where the docs
  give 2.
- **Cooldown.** The wait reads only the combatant's own Dexterity. Help to a Rogue's or an
  Archer's Dexterity never shortens it. So the Battle Test Rogue and Archer, own Dexterity
  8 plus one help, wait 71 ticks where the settled tables give 69.

The engine follows `EhrensDocs/Combat.md`, "How a cooldown rounds, and whose Dexterity
counts" ("For now the Dexterity is the combatant's own"). The user has ruled that the
original docs win where the two contradict. Some existing tests assert the old behaviour:
`CombatCooldownTests` R7, `CombatKit.ExpectedHelp`, and the "a wait of 71" fixture comment
in `CombatSupportRingTests`. They are expected to change.

## Goal

Help to a primary stat rounds the way `Guild Members.md` says: the first help rounds up,
later helps are exact, and the total rounds down once. A Rogue or an Archer, on either side,
waits by its Dexterity with that help counted. The Battle Test teams then run at the
cooldowns their tables give: 138 / 138 / 104 / 69 / 104 / 69.

## Requirements

1. **The first help rounds up.** The first help is 5% of the receiver's own primary stat,
   rounded up to a whole point and never less than one.
   *Guild Members.md, Diminishing Returns on Help* ("The first help rounds up to at least
   one point"); *Battle Test.md, The Field* ("rounded up to at least one point").

2. **Later helps are exact and chain from the unrounded 5%.** Each further help is 49% of
   the previous help's exact value, so the second is 2.45% of the stat. It is not 49% of the
   rounded-up first point. The later helps are added unrounded, and the total is rounded
   down once, so at low stats a later help can add nothing.
   *Guild Members.md, Diminishing Returns on Help* ("the second help is 2.45%"; "every later
   help is exact, so at low stats a later help can come to nothing"). Rounding down once is
   the engine's current behaviour and is kept.

   Worked values (help points added to the primary stat):

   | Own primary stat | Helps | Docs | Game today |
   |---|---|---|---|
   | 0 | 1 | 1 | 1 |
   | 4 | 2 | 1 (1 + 0.098) | 1 |
   | 8 | 1 | 1 (0.4 up) | 1 |
   | 20 | 1 | 1 (exactly 1, not raised) | 1 |
   | 21 | 1 | 2 (1.05 up) | 1 |
   | 30 | 1 | **2** (1.5 up) | 1 |
   | 30 | 2 | 2 (2 + 0.735) | 2 |
   | 30 | 3 | **3** (2 + 0.735 + 0.36015) | 2 |

   This rounding applies to help on every type's primary stat, not only Dexterity. The
   docs describe one help rule (*Guild Members.md, Diminishing Returns on Help*).

3. **A Rogue's or an Archer's cooldown counts help.** The wait is the type's base divided by
   (1 + Dexterity ÷ 20), as today, but Dexterity here is the helped value: own Dexterity
   plus the help points from requirements 1–2. The tenth-of-base floor and the
   nearest-tick, half-up rounding are unchanged, and both apply to the helped value.
   *Combat.md, Cooldowns* ("How fast a member's cooldown is met is determined by
   Dexterity"); *Guild Members.md, Base Stats* ("Dexterity is also the speed attribute")
   and *Diminishing Returns on Help* (help applies to the primary stat, which for the Rogue
   and the Archer is Dexterity per *Stat Weighting by Type*); *Battle Test.md, The Field*
   ("The stats in the tables below already include it") and the tables' Cooldown column.
   This supersedes the "for now" sentence in *EhrensDocs/Combat.md, "How a cooldown rounds,
   and whose Dexterity counts"*, under the user's precedence rule. Its half-up rounding
   stands, because the original does not contradict it.

   Worked values, Rogue or Archer, base 100:

   | Own Dexterity | Helps | Helped Dexterity | Wait (docs) | Wait (game today) |
   |---|---|---|---|---|
   | 8 | 0 | 8 | 71 | 71 |
   | 8 | 1 | 9 | **69** | 71 |
   | 30 | 1 | 32 | **38** | 40 |

4. **Both sides.** An enemy Rogue or Archer gets the same helped cooldown from its own
   side's support ring. The Battle Test enemy Rogue and Archer wait 69 ticks.
   *Battle Test.md, The Enemy Team* ("Same six types, same stats, same positions", Cooldown
   column 69); *Combat.md, Enemies* ("built from the same six combat types as guild
   members, working the same way").

5. **The first wait counts help too.** A combatant whose opening Luck check fails waits the
   helped wait for its first attack. The Battle Test Rogue's and Archer's first attacks come
   on tick 69. This holds whatever order the members were placed on the grid: the wait
   reflects the formation the fight starts with, not the neighbours present at the moment
   each member was added.
   *Combat.md, Cooldowns* ("it waits out that first cooldown like normal"); *Battle
   Test.md* tables; *EhrensDocs/Guild Members.md, "Help counts where everyone stands right
   now"*.

6. **No other cooldown changes.** Help reaches only the receiver's primary stat, and among
   divers only the Rogue and the Archer lead on Dexterity. A Brute's, Tank's, Fighter's or
   Mage's wait stays on its own Dexterity: 138 / 138 / 104 / 104 ticks in the Battle Test.
   Specialists neither give nor receive help, so their waits are unchanged.
   *Guild Members.md, The Support Ring* ("not the specialists like Porter and Cook") and
   *Diminishing Returns on Help*, *Stat Weighting by Type*; *Battle Test.md* tables (the
   Fighter and the Mage at Dexterity 7 wait 104, the Brute and the Tank at Dexterity 6 wait
   138, all unhelped Dexterity).

## Out of Scope

- **Building the Battle Test teams as a fixture** or the three-wide field. Its numbers are
  used here as the acceptance figures only.
- **The same-tick order by Dexterity.** Whether it counts help is listed under Open
  Questions, and this PRD does not change it.
- **Health, Luck and the Luck bag.** The Tank-health question stays open in `Battle
  Test.md`, and help does not reach Luck.
- **Damage.** It already reads the helped primary stat and changes only through
  requirements 1–2.
- **Correcting `Combat.md`'s worked figures.** See the report. This PRD does not depend on
  them.

## Open Questions

- *(Raised by this PRD; the docs do not word it.)* When a helper moves away, dies or
  arrives while a Rogue's or an Archer's wait is already running, does that running wait
  change, or does the change only show from its next wait? `EhrensDocs/Guild Members.md`
  says help "changes it straight away", but not what that means for a wait already
  counting down. The answer also decides what the stamina bar reads partway through such a
  wait.
- *(Raised by this PRD.)* When cooldowns come up on the same tick, the one with the higher
  Dexterity goes first (`EhrensDocs/Combat.md`, the close-range turn-taking change). Does
  that Dexterity count help? The engine uses own Dexterity today.
