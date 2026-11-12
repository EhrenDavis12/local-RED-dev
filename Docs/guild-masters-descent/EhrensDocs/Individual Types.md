# Individual Types — proposed changes

> **Status:** Change notes against `Individual Types.md`, for its owner to review. The
> original is not edited.

## Change: The flurry's leftover strikes stay within reach

> Proposed 2026-11-12 · for review

**Where:** `## The Fighter`, second paragraph

**Now says:**

```
Its special is a flurry of up to 6 strikes on a single target. The flurry's strikes hit
hard. If the target dies before the strikes run out, the remaining strikes carry to the
nearest enemy still standing. If any enemy is killed during the flurry, the Fighter's
charge bar refills to 90% — that refill is the Fighter's bonus charge condition.
```

**Proposed:**

```
Its special is a flurry of up to 6 strikes on a single target. The flurry's strikes hit
hard. If the target dies before the strikes run out, the remaining strikes carry to the
nearest enemy still standing that the Fighter's close range can reach, passing over a
vanished Rogue unless that's all there is. If nothing is in reach, the remaining strikes
are lost. If any enemy is killed during the flurry, the Fighter's charge bar refills to
90% — that refill is the Fighter's bonus charge condition.
```

**Why:** The combat engine is built this way. "The nearest enemy still standing" could
have reached past the front row, which the Fighter's close range never can.

## Change: A failed Vanish fails for that strike only

> Proposed 2026-11-12 · for review

**Where:** `## The Rogue`, third paragraph

**Now says:**

```
The Rogue's special is called Vanish: the Rogue becomes untargetable. Its attacks don't
break Vanish, so it can keep attacking while vanished, and while Vanish is active those
attacks hit automatically — there's no hit check. Vanish ends when an enemy's area attack
hits the Rogue, or when its fixed length runs out. Vanish fails if the Rogue is the only
thing an enemy can reach — then the Rogue can be hit anyway.
```

**Proposed:**

```
The Rogue's special is called Vanish: the Rogue becomes untargetable. Its attacks don't
break Vanish, so it can keep attacking while vanished, and while Vanish is active those
attacks hit automatically — there's no hit check. Vanish ends when an enemy's area attack
hits the Rogue, or when its fixed length runs out. Vanish fails if the Rogue is the only
thing an enemy can reach — then the Rogue can be hit anyway. For now that failure is for
the one strike only: the Rogue stays vanished, and the next strike checks again.
```

**Why:** The combat engine is built this way. "Fails" didn't say whether Vanish ends or
only gives way for the moment. Whether the check is per strike or per attack is proposed
as a question below.

## Change: The Mage's field goes straight through, for now

> Proposed 2026-11-12 · for review

**Where:** `## The Mage`, second paragraph

**Now says:**

```
Its special is a lingering field: it covers two columns of the enemy's grid and keeps
damaging enemies standing in it. The field affects enemies only — it never damages the
player's own members.
```

**Proposed:**

```
Its special is a lingering field: it covers two columns of the enemy's grid and keeps
damaging enemies standing in it. The field affects enemies only — it never damages the
player's own members. It does its damage at the start of each of the Mage's turns while
it lasts, to whoever is standing in it then. For now the field's damage goes straight
through: it doesn't roll to hit, no defence is subtracted from it, and it wears no
armour. The Mage's ordinary column attack is different — its magic damage meets defence
the way any area attack does.
```

**Why:** The combat engine is built this way. "Keeps damaging" didn't say when, and
nothing said whether magic damage meets defence. Whether the field should meet defence is
proposed as a question below.

## Change: Questions on Vanish, taunts and the field

> Proposed 2026-11-12 · for review

**Where:** `## Open Questions`, at the end of the list

**Now says:**

```
- What are the stats, skills and abilities for each individual type?
- How fast does a special charge?
```

**Proposed:**

```
- What are the stats, skills and abilities for each individual type?
- How fast does a special charge?
- When Vanish fails because the Rogue is the only thing an enemy can reach, is that
  judged once for the whole attack, or again for each strike?
- When an attack reaches further than its range usually would — the Brute's special,
  cleaving past the front row — is "the only thing an enemy can reach" judged by the
  attack's usual reach, or by what that attack actually reaches?
- If the Tank's attack passes over a vanished Rogue, is the Rogue still taunted?
- Should the Mage's field meet the defence of the enemies standing in it?
```

**Why:** None of the docs answers these. The existing entries are unchanged.
