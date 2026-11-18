# PRD: The Archer's capped streak can't be dodged

> **Status:** Draft, queue item #141 · Source docs read: `Individual Types.md`,
> `Combat.md`, `Guild Members.md`, EhrensDocs `Individual Types.md`, EhrensDocs
> `Guild Members.md`, EhrensDocs `The Dungeon.md`, queue report
> `127-archer-accuracy-vs-luck-bag.md`

## Problem

The Archer's streak still claims to raise accuracy, but a dodge is now a token pulled from
the target's Luck bag (`Combat.md`, Luck Checks), so there is no miss chance left to lower.
The user's 17 Nov call (#127, answer C) replaces that half of the raise: once the raise is
at its cap, the Archer's shots on that target can't be dodged.

Today, in `src/guildmasters-descent`:

- `ArcherType.Shot` works out the raise and sets it as both `DamageMultiplier` and
  `MissChanceReduction` on the shot's `TargetPlan`. Nothing reads `MissChanceReduction`:
  `Battle.Strike` pulls the target's bag unless the plan is an area attack or the target
  plan is `AutoHit`. So the accuracy raise already does nothing.
- Volley skips the pull by being an area attack (`AttackPlan.IsArea`), which also brings
  two-thirds defence and reaching a vanished Rogue. The Rogue's strikes while vanished skip
  the pull with `TargetPlan.AutoHit`, which carries neither.
- `Tuning.ArcherStreakStepPercent`'s label reads "Percent of damage and accuracy the
  Archer's streak adds per consecutive hit."
- Comments in `CombatArcherTests.cs` and `CombatTypesSharedTests.cs` say the accuracy raise
  is open under #127. It is no longer open. The section header in `CombatContractTests.cs`
  ("The Archer's streak: attacker-side accuracy and damage") still names accuracy too.

## Goal

An Archer, member or monster, whose streak raise on a target has reached the 10% cap lands
every ordinary shot on that target without its bag being pulled, until the streak breaks.
The streak raises damage only, nothing in the code carries an accuracy raise, and the tuning
label says so.

## Requirements

1. **A capped shot can't be dodged.** An ordinary shot whose streak raise is at the cap
   pulls no token from the target's Luck bag and always hits. The first such shot is the
   first one carrying the full 10%. With today's placeholder step of 2%, that is the
   seventh hit in a row. Work it out from the step and the cap, never as a fixed count.
   *(EhrensDocs `Individual Types.md`, "Change: Volley and the Archer's streak, for now",
   Proposed, second paragraph: "once the raise reaches its cap, the Archer's shots on that
   target can't be dodged until the streak breaks — like Volley, they pull no token from its
   bag"; `Combat.md`, Luck Checks.)*
2. **Below the cap, shots are dodged as now.** A shot with a raise of 0 up to one step
   short of the cap pulls the target's token as any shot does. A True is a miss, and a miss
   resets the streak. *(Same paragraph: "A miss resets the streak"; `Combat.md`, Luck
   Checks.)*
3. **A capped shot is still an ordinary single shot, not an area attack.** The only thing it
   takes from Volley is skipping the pull. It pays the target's full defence, not
   two-thirds. It passes over a vanished Rogue the way any single-target attack does, and it
   doesn't end Vanish. It still carries the 10% damage raise, applied after defence. One
   edge case follows from this and is worth a test. When a vanished Rogue is the only enemy
   the Archer can reach, Vanish fails and the capped shot hits it. No token is pulled, and
   the Rogue stays vanished. *(EhrensDocs `Individual Types.md`, same section: "Its ordinary
   attack is a single shot" and "Damage is raised in percent more after defence";
   `Guild Members.md`, Base Stats, which makes the two-thirds defence a property of area
   attacks; `Individual Types.md`, The Rogue, where an area attack is what ends Vanish.)*
4. **A capped shot continues the streak.** It is a hit on the same target, so it counts as
   one. The raise stays at the cap, the next shot is capped too, and each one pays the
   streak's bonus charge on top of the ordinary shot's charge, as today. *(EhrensDocs
   `Individual Types.md`, same section: the bonus is "hitting the same target twice
   running", "until the streak breaks", and "each hit that continues the streak pays the
   bonus charge".)*
5. **The streak breaks as today.** Any ordinary shot by that Archer at a different enemy
   breaks it, hit or miss. A capped shot can't miss, so once capped, a shot at another
   enemy is the only thing that breaks it. A Volley neither continues it nor breaks it. After a break the count starts over, and shots are
   dodgeable again until the new streak reaches the cap. *(Same section: "Specials are
   outside the streak entirely — a Volley neither continues nor breaks it.")*
6. **There is no accuracy raise.** The streak raises damage only. The shot sets no
   miss-chance reduction, and `TargetPlan.MissChanceReduction` goes, since nothing else
   sets or reads it. *(EhrensDocs `Individual Types.md`, same section, Proposed: "raises the
   Archer's damage", with accuracy struck, and its Why.)*
7. **The tuning label says damage only.** `ArcherStreakStepPercent`'s label names damage
   and not accuracy, and it still says the 10% cap is settled. The step stays a placeholder
   at its current value. *(Same section: "each hit after adds another step, a placeholder,
   up to the cap".)*

## Out of Scope

- When the raise starts (second hit or third), how big the step is, and the 10% cap. All
  of these stay as built.
- Volley, its spill-forward, and its neighbours' share.
- Anything shown on screen for a capped streak. No doc asks for an indicator.
- The Rogue's evasion bonus. It already can't pay on a strike that pulls no token, so
  nothing changes there.

## Open Questions

Neither of these is answered by this PRD. The build keeps today's default for both, as
EhrensDocs records it.

- Does the Archer's streak raise start with the second hit or the third? *(EhrensDocs
  `Individual Types.md`, "Questions on Vanish, taunts and the field". Default for now: the
  second hit starts it, so the third shot is the first raised. This sets which shot is the
  first capped one.)*
- How often does each type's bonus condition pay, the Brute's aside? The sheets name the
  condition, not how many times it pays in one attack. *(Same list. Default for now: each
  hit that continues the streak pays.)*
