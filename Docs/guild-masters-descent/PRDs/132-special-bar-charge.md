# PRD: Special bar charge by the originals (#132)

> **Status:** Draft · Source docs read: Combat.md, Individual Types.md, Battle Test.md,
> Equipment.md, EhrensDocs/Combat.md, EhrensDocs/Individual Types.md, EhrensDocs/Open
> Questions.md · Code read on `src/guildmasters-descent` branch `queue/132-special-bar-charge`

## Problem

The engine charges a flat 10 for every hit an ordinary attack lands
(`BarFigures.BaseCharge`), and pays the Brute one flat 15 the moment its cleave lands on a
second enemy (`BruteType.BonusCharge`). The originals now say something different: the
first hit of an attack charges 30 and each hit after it 5, and the Brute's bonus is 5 for
each enemy beyond the first. So every special arrives at the wrong time. Single-hit types
fill about three times slower than the docs intend, and the Brute's bonus is wrong for
every three-wide cleave.

Volley's neighbour share is still a tuning placeholder (`Tuning.VolleyNeighbourShare`,
listed in `Lists/placeholders.md`), but Individual Types settles it at half.

## Goal

Every ordinary attack charges its attacker's bar 30 for its first landed hit and 5 for
each landed hit after that. The Brute's bonus pays 5 for each enemy beyond the first. The
other types' bonuses, and the rule that specials charge nothing, stay exactly as built.
Volley's half share is a settled figure and no longer appears in the placeholder list.

## Requirements

**Base charge**

1. The first hit an ordinary attack lands charges its attacker's bar by **30**.
   *(Combat.md § The Special Bar, "the first hit of an attack charges it by 30")*

2. Each further hit the same attack lands charges **5**, whether it is another strike on
   the same target or a hit on another target. Examples: a Fighter's or Rogue's two
   landed strikes charge 30 + 5. A Mage column landing on three enemies charges
   30 + 5 + 5. *(Combat.md § The Special Bar, "each additional hit — another strike of a
   multi-strike attack, or another target the attack reaches — charges it by 5")*

3. A strike that misses charges nothing and does not use up the attack's first hit. If an
   attack's first strike is evaded and its second lands, the second charges 30. An attack
   that lands nothing charges nothing. *(Combat.md § The Special Bar, "Each hit a member
   lands charges that member's bar"; "Charge and weapon durability both count hits";
   Equipment.md, durability: "an attack that misses spends none")*

4. A free attack from the Luck reset is an attack of its own. Its first landed hit charges
   30 again, even when it comes in the same tick as the attack that earned it.
   *(Combat.md § Luck Checks, "it charges the special bar the same as any other attack")*

5. Base charge is the same for every type, on both sides. Members and enemies are charged
   alike. *(Combat.md § The Special Bar, "the same for every type"; "An enemy's bar works
   the same way")*

6. Specials still charge nothing. That covers the special's own hits, the Mage's field
   damage, and any bonus a special might earn. The Fighter's flurry kill still refills
   the bar to 90%. Neither 30 nor 5 ever applies to a special's hits. *(EhrensDocs/Combat.md,
   "A special puts nothing in its owner's bar, for now"; Individual Types.md § The
   Fighter)*

**Bonus charge**

7. The Brute's bonus pays **5 for each different enemy beyond the first** that its
   ordinary attack lands on. This replaces the single flat 15, and it comes on top of
   the base charge. A cleave that lands on three enemies charges 30 + 5 + 5 (base) +
   5 + 5 (bonus) = 50. Landing on two charges 40, and landing on one charges 30. An enemy
   that evades counts toward neither the base nor the bonus. The Brute's special pays no
   bonus. *(Individual Types.md § The Brute, "each enemy beyond the first charges 5,
   rather than the flat 15"; EhrensDocs/Individual Types.md, "Where the Brute's cleaves
   land, for now": "a miss doesn't count, and neither does the special")*

8. Every other type's bonus still adds **15** each time its condition is met, with its
   current for-now pay rule unchanged: Tank, per enemy strike aimed at him; Rogue, per
   strike evaded; Archer, per hit continuing the streak; Mage, per enemy strike landing on
   an ally in front of it; Fighter, the flurry refill only. An Archer shot that continues
   its streak therefore charges 30 + 15. *(Combat.md § The Special Bar, "each time it's met
   it adds 15"; EhrensDocs/Individual Types.md, the Tank, Rogue, Archer, Mage and Fighter
   bonus change notes)*

**Settled figures**

9. The charge figures are settled, not tuning: 30, 5, the bonus 15, the Brute's 5 and the
   full bar at 100. None of them appears in `Tuning.ListPlaceholders()`.
   *(Combat.md § The Special Bar; Individual Types.md § The Brute)*

10. Volley's neighbour share is **half**, and it is settled. It leaves Tuning, so it is
    not listed by `Tuning.ListPlaceholders()`, and its line is removed from
    `Lists/placeholders.md`. Volley's damage is unchanged: same value, same math.
    *(Individual Types.md § The Archer, "its neighbours take half that damage")*

**What changes in code** (for orientation, not a design): `Core/Combat/BarFigures.cs`
(the single `BaseCharge`), the base-charge line in `Battle.Strike`, `BruteType.BonusCharge`,
`Tuning.VolleyNeighbourShare` and its readers, and `Lists/placeholders.md`. Some existing
tests assert the old rules and will flip: 10 a hit (`CombatSpecialBarTests`), the Brute's
flat 15, and Volley's share being a placeholder below 1 (`CombatTypesSharedTests`
"EachNewNumberIsAPlaceholderInTuning…", plus the share reads in `CombatArcherTests` and
`DamageMathTests`).

## Out of Scope

- Whether a special's hits charge, and whether a special can earn a bonus. Both stay at
  their for-now defaults (requirement 6).
- How often each bonus pays within one attack, apart from the Brute's. The Fighter's
  refill-versus-15 question also stays out.
- What counts as a landed hit. A hit that defence stops entirely still counts, as now.
- How Volley's neighbour damage is worked out. Only its listing changes.
- Bar carry-over between battles, floors and dives. Saves are untouched: a bar is still
  one number from 0 to 100.
- The battle screen. Nothing new is drawn.
- Doc changes. The originals already state this rule, and no EhrensDocs change note
  disagrees with it.

## Open Questions

From the docs, worded as they are there. None of these blocks this build, and each keeps
its current for-now default:

- Do a special's own hits — the Mage's field's damage among them — charge the bar it has
  just emptied? *(EhrensDocs/Combat.md, "Questions on the special bar")*
- Can a special earn its owner's bonus condition — a Brute's special landing on two or
  more enemies, say? *(same)*
- How often does each type's bonus condition pay, the Brute's aside? The sheets name the
  condition, not how many times it pays in one attack. *(EhrensDocs/Individual Types.md,
  "Questions on Vanish, taunts and the field")*
- `Combat.md` gives every type's bonus 15 each time it's met, and this doc makes the
  Fighter's a refill to 90%. Is the Fighter's bonus the refill, 15, or both?
  *(EhrensDocs/Individual Types.md, "A question on the Fighter's bonus")*

Proposed by the PRD author, not from the docs:

- "The target takes the full hit; its neighbours take half that damage." Does "that
  damage" mean half of what the target took, or half of what each neighbour would have
  taken against its own defence? The engine does the second. This PRD leaves it as it is.
