# PRD: The Six Combat Types and the Specialists' Attack

> **Status:** Draft · Source docs read: Combat.md, Individual Types.md, Guild Members.md,
> Equipment.md, Specialists.md, The Dungeon.md, Core Concept.md, and the change notes in
> EhrensDocs/ (Combat.md, Individual Types.md, Guild Members.md, Equipment.md,
> The Dungeon.md, Core Concept.md, Platform.md). Engine read: `Assets/Scripts/Core/Combat/`.

Citation keys: **IT** [Individual Types.md](../Individual Types.md) · **C**
[Combat.md](../Combat.md) · **GM** [Guild Members.md](../Guild Members.md) · **EQ**
[Equipment.md](../Equipment.md) · **SP** [Specialists.md](../Specialists.md). A trailing
`*` means the change note of the same name in `EhrensDocs/`, which is the settled design
where it changes the original (e.g. **IT\*** "A failed Vanish fails for that strike
only").

## Problem

The combat engine is built, but nothing real plugs into it: every battle so far runs on
test fakes. No Brute can cleave, no Tank can taunt or raise Shields Up, and a Cook or
Porter on the grid cannot take a turn at all, because there is no combat type for the
engine to ask. Until the six types exist, the first dungeon's battles cannot be fought.

## Goal

Every one of the six combat types — for members and monsters alike — fights the way its
sheet says, through the engine's existing type contract (`ICombatType`,
`ICombatAttack`, `AttackPlan`, `AttackEffect`, `BonusCharge`): its ordinary attack, its
special, and its bonus charge condition. The Cook and the Porter take their turns with a
weak close attack and never have a special bar. Every number the docs leave unset is a
placeholder in `Tuning.cs`.

## Requirements

### Shared

1. **Monsters get the same types.** A monster of a type has that type's ordinary attack,
   special and bonus charge, exactly as a member does. (The Dungeon\* "The dungeon's
   enemies are monsters")
2. **Specials charge the base like any attack**, except the flurry (req. 15). This
   includes Shields Up, Vanish and the field, which hit nobody. (C\* "The base charge is
   once per attack, and a special empties the bar")
3. **A special's chosen target.** For a special that strikes nobody (Shields Up, Vanish),
   the engine still picks a target before the plan runs, as built today. Whether that
   spends a taunt is an open question in the docs (Open Questions); the PRD pins nothing
   about whether a target roll is drawn, and tests must not depend on it either way. The
   party's selected enemy is never spent by this. (C § Combat; C\* "Questions on turn
   order and taunts")
4. **The three timed effects** — Vanish, Shields Up, the field — each last
   `Tuning.EffectTurns` of the caster's turns and end early only when the caster dies, or
   (Vanish only) when an enemy area attack hits the Rogue. In particular **the field does
   not end when an enemy in it, or the enemy it was aimed at, dies.** Today the engine
   ends any effect whose named target dies; the field must not be tied to one. (C § Combat
   third paragraph; C\* "Whose turns an effect's length counts"; IT § The Rogue)

### The Brute

5. **Ordinary — cleave.** Close range. Hits the chosen target and the enemies directly
   left and right of it in the same row; an empty neighbouring node is simply not hit.
   Each strike rolls to hit on its own — the cleave is not an area attack. (IT § The
   Brute, second paragraph; C § Combat, "Each strike of a multi-strike attack")
6. **Against a Tank, a Brute's strike skips defence entirely** — no Constitution, armour
   or Shields Up is subtracted. Whether the type-advantage multiplier also applies is open
   (Open Questions); as built, it does. (IT § The Brute, first paragraph; GM\* "Two
   questions on type advantage and defence")
7. **Special.** Skips the nearest occupied enemy row and cleaves the grid rows behind it —
   two, or whatever rows remain. In **each** of those rows it cleaves three wide: the
   enemy in the same column as the Brute's chosen front-row target, and the enemies
   directly left and right of that node — up to six enemies in all. Empty nodes are not
   hit. Its strikes are individually evadable like the ordinary cleave. (IT § The Brute,
   third paragraph; the centring and the two-row reach are defaults — see Open Questions)
8. **The Brute's move to the front and back is presentation only.** In the engine the
   Brute never leaves its node, and nothing acts between the cleave and its return. (IT
   § The Brute, "all in the same action")
9. **Bonus charge — hitting multiple enemies.** An attack whose strikes land on two or
   more different enemies earns `BruteMultiHitCharge`. Misses and passed-over vanished
   enemies do not count. (IT § The Brute)

### The Tank

10. **Ordinary.** Close range, one strike on the chosen target, and taunts it. (IT § The
    Tank)
11. **Shields Up.** Adds `ShieldsUpDefence` to the Tank's own defence, and the same to
    every ally — specialists included — behind him in his own column on his own grid
    (two when he is in the front row, one from the middle row, none from the back). Two
    Tanks' contributions add up in full. (IT § The Tank; see Open Questions on "that
    defence")
12. **Bonus charge — being attacked.** Each enemy strike aimed at the Tank, hit or miss,
    earns `TankAttackedCharge`. Field damage is not a strike and earns nothing. (IT § The
    Tank)

### The Fighter

13. **Ordinary.** Close range, `FighterStrikeCount` strikes on the chosen target. The
    count never changes with level. Each strike carries `1 / FighterStrikeCount` of the
    Fighter's damage, **and that split happens before defence is subtracted** — every
    light strike pays the full defence subtraction. This is what the Tank's advantage over
    the Fighter rests on. *The engine's `DamageShare` is applied after defence, so the
    contract needs a before-defence share for this.* (IT § The Fighter; IT § The Tank,
    "every one of them pays that subtraction")
14. **Special — flurry.** Up to 6 strikes on the chosen target, each carrying
    `FlurryStrikeShare` of the Fighter's damage. When the target dies, the rest carry to
    the nearest enemy still standing within close reach, passing over a vanished Rogue
    unless that is all there is; if none is in reach, they are lost. (IT\* "The flurry's
    leftover strikes stay within reach")
15. **The flurry's own strikes charge nothing** — no base charge, no bonus. If any enemy
    is killed during the flurry, the Fighter's bar is set to 90% of full; otherwise it is
    left empty. 90% is settled, not a placeholder. (IT § The Fighter; C\* "The base charge
    is once per attack")

### The Rogue

16. **Ordinary.** Far range, two strikes on the chosen target, each carrying
    `RogueStrikeShare` of the Rogue's damage, split before defence like the Fighter's.
    (IT § The Rogue; see Open Questions on the split)
17. **Vanish.** The Rogue becomes untargetable for the effect's length. While vanished its
    own strikes hit automatically. Its attacks do not end Vanish. An enemy area strike
    landing on it ends Vanish. (IT § The Rogue)
18. **A failed Vanish fails for one strike only**, judged before each strike, by the
    attack's declared range — as the engine already does. Both points are open questions
    in the docs; this is the current default. (IT\* "A failed Vanish fails for that strike
    only"; IT\* "Questions on Vanish, taunts and the field")
19. **Bonus charge — evading.** Each enemy strike aimed at the Rogue that misses earns
    `RogueEvadeCharge`. (IT § The Rogue)

### The Archer

20. **Ordinary.** Far range, one strike carrying the Archer's whole damage. (IT § The
    Archer)
21. **Volley.** An area attack — it cannot miss, and pays the area attack's reduced
    defence. It hits the chosen target for full damage, and for `VolleyNeighbourShare` of
    the damage: the enemy one node to each side, and the one directly behind (the next row
    back). When the target is in the grid's back row, that last hit lands on the node in
    front of it instead. Empty nodes take nothing. (IT § The Archer; GM § Base Stats, area
    attacks)
22. **The streak.** An ordinary shot that hits the same enemy as the Archer's previous
    ordinary shot continues the streak; a miss resets it, and a hit on a different enemy
    starts a new one. Volley neither continues nor breaks it. Each continued hit earns
    `ArcherStreakCharge`. (IT § The Archer)
23. **The streak's edge.** While a streak continues, each further shot at that enemy is
    raised by `ArcherStreakStepPercent` more per consecutive hit — both its damage and its
    accuracy (points off the target's miss chance) — capped at 10% each. 10% is settled.
    (IT § The Archer; see Open Questions)

### The Mage

24. **Ordinary — column attack.** Far range, magic damage from Intelligence. An area
    attack on every enemy in the chosen target's column, all three rows; it meets reduced
    defence like any area attack, and ends a Rogue's Vanish. (IT § The Mage; IT\* "The
    Mage's field goes straight through, for now")
25. **Special — lingering field.** Covers two columns of the enemy grid. At the start of
    each of the Mage's turns while it lasts, every enemy standing in those columns then
    takes damage (how much is a defaulted open question, below). The damage goes
    straight through: no hit roll, no defence, no armour wear. It never hurts the caster's
    own side. Field damage counts toward the Mage's damage dealt for enemy targeting.
    (IT § The Mage; IT\* "The Mage's field goes straight through"; C\* "What the
    targeting weights count")
26. **Bonus charge — allies in front taking hits.** Each enemy strike that lands on an
    ally — specialist or diver — standing in front of the Mage in its own column earns
    `MageColumnHitCharge`, even a hit that defence reduced to nothing. (IT § The Mage)

### The Cook and the Porter

27. **On its turn a specialist makes one close-range strike on a single target**, chosen
    the way any member's is. Its damage is the standard formula — its damage stat, no
    weapon (a specialist carries none) — with no extra reduction; the weakness comes from
    that. (C § Combat, fourth paragraph; SP § Equipment)
28. **A specialist never has a special bar** and never uses a special. (C § Combat)

### Placeholders

29. These numbers are not set by any doc. Each goes in `Tuning.cs` with a `[Placeholder]`
    note, beside every other placeholder, and nowhere else.

| Name | Proposed | Meaning |
|---|---|---|
| `FighterStrikeCount` | 4 | Strikes in the Fighter's ordinary attack. More than the Rogue's 2. |
| `FlurryStrikeShare` | 1.0 | Share of the Fighter's damage each flurry strike carries, before defence. |
| `RogueStrikeShare` | 0.5 | Share of the Rogue's damage each of its two strikes carries, before defence. |
| `VolleyNeighbourShare` | 0.5 | Share of the damage Volley's three extra hits take. Below 1. |
| `ShieldsUpDefence` | 3 | Defence Shields Up adds to the Tank and to each ally behind him. |
| `ArcherStreakStepPercent` | 2 | Damage and accuracy added per consecutive hit; the 10% cap is settled. |
| `FieldDamageShare` | 0.5 | Share of the Mage's damage the field does each turn. |
| `BruteMultiHitCharge` | 10 | Bonus charge for an attack landing on two or more enemies. |
| `TankAttackedCharge` | 4 | Bonus charge per enemy strike aimed at the Tank. |
| `RogueEvadeCharge` | 10 | Bonus charge per enemy strike the Rogue evades. |
| `ArcherStreakCharge` | 10 | Bonus charge per continued streak hit. |
| `MageColumnHitCharge` | 5 | Bonus charge per hit on an ally in front in the Mage's column. |

### Engine

30. **The type contract gains a before-defence damage share.** A type's plan can set, per
    target, a share of the attacker's damage that is applied before defence is
    subtracted, alongside the existing after-defence `DamageShare`. The Fighter's
    ordinary strikes (req. 13), the flurry (req. 14) and the Rogue's strikes (req. 16) use
    it. Without it, splitting damage after defence makes many light strikes total the same
    as one big hit, and the Tank's advantage over the Fighter disappears. (IT § The Tank,
    "every one of them pays that subtraction and loses most of its damage")

## Out of Scope

- The engine's own rules — turn order, targeting weights, how taunts are spent, the
  support ring, the type-advantage multiplier's value, gear wear, evasion from Luck.
  Built already. The two contract gaps this needs (before-defence share, req. 13; a field
  with no named target, req. 4) are the only engine changes.
- Stats and starting stats per type — what makes the Rogue's evasion high comes from its
  Luck, already set.
- How a special is chosen on screen, and any animation, including the Brute's move.
- The specialists' out-of-combat abilities (the Cook's healing, the Porter's carrying),
  and every specialist other than the Cook and the Porter.

## Open Questions

**With a cheap default we'd go ahead with** (proposed defaults are this PRD's, not the
docs'):

- Which enemy does the Brute's special centre on? "The cleave hits the targeted enemy
  and the two directly next to it" (IT § The Brute), but the targeted enemy of a close
  attack is in the front row, which the special skips. *Default: the enemy in the same
  column as the chosen front-row target.*
- Does the Brute's special hit a three-wide cleave in each of the two rows (up to six
  enemies), or three enemies in all? *Default: three wide in each row.*

- When the nearest occupied row is the grid's back row, so no row remains behind it, what
  does the Brute's special hit? *Default: nothing; the bar still takes its base charge.*
- Do the Brute cleave's neighbours, and every enemy in the Mage's column, take the full
  damage? Only Volley's neighbours are said to take reduced damage. *Default: full.*
- Does a Brute striking a Tank get both the defence subtraction skipped and the
  multiplier, or only one of them? (GM\*) *Default: both, as the engine does.*
- "It also adds that defence to all the allies behind him" — is that the Shields Up
  increase, or the Tank's whole defence? *Default: the increase.*
- If an ally moves into or out of the Tank's column while Shields Up lasts, does the
  bonus follow? *Default: no — fixed to whoever was behind him when cast.*
- Is the Tank's target taunted when his attack misses? *Default: yes, as built.*
- If the Tank's attack passes over a vanished Rogue, is the Rogue still taunted? (IT\*)
  With these six types it cannot happen — the Tank's one strike is always on a target
  that can be picked — so nothing is built for it.
- When a taunted member or enemy uses a special that hits its own choice of targets
  rather than one it aims at, is the taunt spent? (C\*) *Default: yes, as built.*
- When Vanish fails because the Rogue is the only thing an enemy can reach, is that
  judged once for the whole attack, or again for each strike? (IT\*) *Default: each
  strike.*
- When an attack reaches further than its range usually would — the Brute's special,
  cleaving past the front row — is "the only thing an enemy can reach" judged by the
  attack's usual reach, or by what that attack actually reaches? (IT\*) *Default: usual
  reach.*
- Is a Rogue's damage spread across its two strikes the way a Fighter's is? "Its strikes
  don't hit as hard as a Fighter's, because the weapon it carries adds less damage" only
  holds if the two are shaped alike. *Default: yes, half each (`RogueStrikeShare`).*
- If the target of a Fighter's or Rogue's ordinary attack dies mid-attack, do the rest of
  the strikes carry on to another enemy? Only the flurry is said to. *Default: they are
  lost.*
- On the turn a Rogue casts Vanish, a Tank Shields Up or a Mage its field, does it also
  make its ordinary attack? *Default: no, the special is the turn.*
- Is the Archer's streak bonus measured in percentage points off the miss chance, or a
  share of it, and does the raise apply from the second hit or the third? *Default:
  points, from the third shot — the second hit starts the raise.*
- Does Volley spill forward only from the back row, or whenever the node behind is empty?
  *Default: back row only.*
- Which two columns does the Mage's field cover? *Default: the chosen target's column and
  the one to its right, or to its left at the right edge.*
- How much does the field do each turn — set from the Mage's damage when cast, or read
  each turn? Does it spend a use of the staff? *Default: set at cast from Intelligence
  plus a staff roll, times `FieldDamageShare`; no staff use.*
- How often does each bonus condition pay? The sheets name the condition, not the count.
  *Defaults, as written in the requirements above: the Brute once per attack; the Tank
  per strike aimed at him, hit or miss; the Rogue per strike evaded; the Archer per
  continued hit; the Mage per hit landed, even one defence stopped.*
- Does the field's damage end a Rogue's Vanish, the way an area attack does? *Default:
  no, as built.*
- "It never damages the player's own members" — a monster Mage's field is on the party's
  grid. *Default: a field never hurts the caster's own side, so a monster Mage's field
  does hurt the party.*
- Should the Mage's field meet the defence of the enemies standing in it? (IT\*)
