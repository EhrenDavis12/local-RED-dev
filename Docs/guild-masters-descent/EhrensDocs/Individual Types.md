# Individual Types — proposed changes

> **Status:** Change notes against `Individual Types.md`, for its owner to review. The
> original is not edited.

## Change: A Brute's hit on a Tank skips all of its defence

> Proposed 2026-11-12 · for review

**Where:** `## The Brute`, first paragraph

**Now says:**

```
The Brute attacks at close range. It has advantage over the Tank — it can push the Tank's
shield aside and bash the weak points in the armour underneath, bypassing the defence
subtraction entirely. It's weak to the Fighter: the Brute wears tanned hide, which adds a
little defence on top of its Constitution, so there's less to subtract than against a
properly armoured type, and a Fighter's many strikes keep most of their damage.
```

**Proposed:**

```
The Brute attacks at close range. It has advantage over the Tank — it can push the Tank's
shield aside and bash the weak points in the armour underneath, bypassing the defence
subtraction entirely. Nothing of the Tank's defence is subtracted: not its Constitution,
not its armour and not Shields Up. For now the Brute's hit still gets the type advantage
multiplier on top, and it still wears the Tank's armour like any other hit. It's weak to
the Fighter: the Brute wears tanned hide, which adds a little defence on top of its
Constitution, so there's less to subtract than against a properly armoured type, and a
Fighter's many strikes keep most of their damage.
```

**Why:** The combat types are built this way. "Bypassing the defence subtraction
entirely" didn't say whether Shields Up is part of what's bypassed. Whether the Brute also
gets the multiplier is already proposed as a question in the Guild Members change notes.
Whether its hit still wears the Tank's armour is proposed as a question below.

## Change: Where the Brute's cleaves land, for now

> Proposed 2026-11-12 · for review

**Where:** `## The Brute`, second and third paragraphs

**Now says:**

```
The Brute's ordinary attack cleaves too: it hits the targeted enemy and the two directly
next to it, on whichever row its close range can reach, and each of them can evade it
individually.

The Brute's special skips the nearest occupied row and cleaves the two rows behind it, or
whatever rows remain if there are fewer. The cleave hits the targeted enemy and the two
directly next to it. When the Brute pushes past the front row, it moves there, cleaves,
and returns to its own node, all in the same action. The Brute's bonus charge condition is
hitting multiple enemies.
```

**Proposed:**

```
The Brute's ordinary attack cleaves too: it hits the targeted enemy and the two directly
next to it, on whichever row its close range can reach, and each of them can evade it
individually. For now each of the three takes the Brute's full damage.

The Brute's special skips the nearest occupied row and cleaves the two rows behind it, or
whatever rows remain if there are fewer. The cleave hits the targeted enemy and the two
directly next to it. A close attack's targeted enemy stands in the row the special skips,
so for now the cleave centres on the targeted enemy's column in each row behind: it hits
the node in that column and the two directly next to it, three wide in each row — up to
six enemies in all. Each of them can evade it individually, like the ordinary cleave.
When the Brute pushes past the front row, it moves there, cleaves, and returns to its own
node, all in the same action. The Brute's bonus charge condition is hitting multiple
enemies. For now it pays once an attack, when the attack's hits land on two or more
different enemies; a miss doesn't count.
```

**Why:** The combat types are built this way. A close attack's targeted enemy is in the
front row, which the special skips, so the special needed a centre. Nothing said whether
it hits three enemies in all or three in each row, whether the cleave's neighbours take
reduced damage the way Volley's do, or how often hitting multiple enemies pays. Each is
proposed as a question below.

## Change: The Tank's taunt, Shields Up and bonus, for now

> Proposed 2026-11-12 · for review

**Where:** `## The Tank`, second to fourth paragraphs

**Now says:**

```
The Tank's ordinary attack hits one target and taunts it, drawing that enemy's attention.

The Tank's special is called Shields Up. It temporarily increases the Tank's own defence,
and it also adds that defence to all the allies behind him in his own column — two of them
when he's in the front row. If more than one Tank uses it, the contributions are fully
additive: an ally behind two Tanks gets both lots of defence.

Being attacked is the Tank's bonus: the bar charges faster while the Tank is being
attacked.
```

**Proposed:**

```
The Tank's ordinary attack hits one target and taunts it, drawing that enemy's attention.
For now the target is taunted even when the attack misses.

The Tank's special is called Shields Up. It temporarily increases the Tank's own defence,
and it also adds that defence to all the allies behind him in his own column — two of them
when he's in the front row. If more than one Tank uses it, the contributions are fully
additive: an ally behind two Tanks gets both lots of defence. For now what the allies get
is the increase, the same amount the Tank gains, not the Tank's whole defence. It goes
to whoever stands behind him when he raises it, and doesn't follow anyone moving into or
out of his column while it lasts.

Being attacked is the Tank's bonus: the bar charges faster while the Tank is being
attacked. For now it pays for each enemy strike aimed at him, hit or miss. The Mage's
lingering field isn't a strike, so its damage earns nothing.
```

**Why:** The combat types are built this way. Nothing said whether a miss still taunts,
whether "that defence" is the increase or the Tank's whole defence, whether the bonus
follows the column as allies move, or how often being attacked pays. Each is proposed as a
question below.

## Change: The Fighter's damage is split before defence

> Proposed 2026-11-12 · for review

**Where:** `## The Fighter`, first paragraph

**Now says:**

```
The Fighter attacks at close range, with many smaller strikes — the property both of its
matchups turn on. The number of strikes is fixed by its type; levelling makes each strike
hit harder rather than adding more strikes. The Fighter's ordinary strikes are light —
its damage is spread across them.
```

**Proposed:**

```
The Fighter attacks at close range, with many smaller strikes — the property both of its
matchups turn on. The number of strikes is fixed by its type; levelling makes each strike
hit harder rather than adding more strikes. The Fighter's ordinary strikes are light —
its damage is spread across them. The damage is split before defence is subtracted, so
every light strike pays the whole of the target's defence; that is what the Tank's
advantage over the Fighter rests on, and splitting it after defence would make many light
strikes add up to one big hit. For now, if the target dies before the strikes run out,
the rest are lost — only the flurry carries on to another enemy.
```

**Why:** The combat types are built this way. "Spread across them" didn't say whether the
split comes before defence or after. The Tank's sheet only holds if it comes before: "every
one of them pays that subtraction and loses most of its damage". Only the flurry is said to
carry on when its target dies. Whether the ordinary strikes should too is proposed as a
question below.

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

## Change: The Rogue's two strikes are shaped like the Fighter's, for now

> Proposed 2026-11-12 · for review

**Where:** `## The Rogue`, second paragraph

**Now says:**

```
The Rogue's ordinary attack is two quick strikes. Its strikes don't hit as hard as a
Fighter's, because the weapon it carries adds less damage.
```

**Proposed:**

```
The Rogue's ordinary attack is two quick strikes. Its strikes don't hit as hard as a
Fighter's, because the weapon it carries adds less damage. For now its damage is spread
across the two the way a Fighter's is — an equal share each, split before defence is
subtracted — and if the target dies after the first, the second is lost.
```

**Why:** The combat types are built this way. "Don't hit as hard as a Fighter's, because
the weapon it carries adds less damage" only holds if the two attacks are shaped alike.
Both points are proposed as questions below.

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

## Change: The Rogue's bonus pays per strike evaded, for now

> Proposed 2026-11-12 · for review

**Where:** `## The Rogue`, fourth paragraph

**Now says:**

```
The Rogue's bonus charge condition is evading an attack.
```

**Proposed:**

```
The Rogue's bonus charge condition is evading an attack. For now it pays for each enemy
strike it evades, so dodging two strikes of one attack pays twice.
```

**Why:** The combat types are built this way. "Evading an attack" didn't say whether a
multi-strike attack pays once or once for each strike evaded. How often each bonus pays is
proposed as a question below.

## Change: Volley and the Archer's streak, for now

> Proposed 2026-11-12 · for review

**Where:** `## The Archer`, first and second paragraphs

**Now says:**

```
The Archer attacks at far range. Its ordinary attack is a single shot, and that one shot
carries the type's whole damage at once. Its special is called Volley: it hits the target,
the enemies one to each side of it, and the one directly behind it. If the target is in
the enemy's back row, with nothing behind it, the extra hit spills forward instead — onto
the position in front of the target. The target takes the full hit; its neighbours take
reduced damage. Volley is an area attack, so it can't be dodged — evasion does nothing
against it.

The Archer's bonus charge condition is hitting the same target twice running. Specials
are outside the streak entirely — a Volley neither continues nor breaks it. Hitting the
same target twice running also raises the Archer's accuracy and its damage — a continuous
percentage increase that caps at 10%. A miss resets the streak.
```

**Proposed:**

```
The Archer attacks at far range. Its ordinary attack is a single shot, and that one shot
carries the type's whole damage at once. Its special is called Volley: it hits the target,
the enemies one to each side of it, and the one directly behind it. If the target is in
the enemy's back row, with nothing behind it, the extra hit spills forward instead — onto
the position in front of the target. For now it spills forward only from the back row: an
empty node behind a target in any other row just isn't hit. The target takes the full
hit; its neighbours take reduced damage. Volley is an area attack, so it can't be dodged
— evasion does nothing against it.

The Archer's bonus charge condition is hitting the same target twice running. Specials
are outside the streak entirely — a Volley neither continues nor breaks it. Hitting the
same target twice running also raises the Archer's accuracy and its damage — a continuous
percentage increase that caps at 10%. A miss resets the streak. For now the second hit in
a row starts the raise, so the first shot it lifts is the third, and each hit after adds
another step, a placeholder, up to the cap. Accuracy is raised in points off the target's
chance to miss, and damage in percent more after defence. For now, too, each hit that
continues the streak pays the bonus charge.
```

**Why:** The combat types are built this way. Nothing said whether Volley spills forward
whenever the node behind is empty or only from the back row. Nor did it say whether the
streak's raise is points off the miss chance or a share of it, whether it applies from the
second hit or the third, or how often the bonus pays. Each is proposed as a question below.

## Change: Every enemy in the Mage's column takes full damage, for now

> Proposed 2026-11-12 · for review

**Where:** `## The Mage`, first paragraph

**Now says:**

```
The Mage attacks at far range. Its attacks are magic damage, driven by Intelligence. Its
ordinary attack is an area attack covering a whole column of the enemy's grid — all three
rows. It's weak to the Archer because the Mage can neither dodge nor absorb, so a
precise single shot is what kills it.
```

**Proposed:**

```
The Mage attacks at far range. Its attacks are magic damage, driven by Intelligence. Its
ordinary attack is an area attack covering a whole column of the enemy's grid — all three
rows. For now every enemy in the column takes the full damage. It's weak to the Archer
because the Mage can neither dodge nor absorb, so a precise single shot is what kills it.
```

**Why:** The combat types are built this way. Only Volley's neighbours are said to take
reduced damage. Whether the rest of the column should is proposed as a question below,
alongside the Brute's cleave.

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
player's own members. A monster Mage's field lies on the party's grid, so it is the party
it hurts: a field never damages the side that cast it. It does its damage at the start of
each of the Mage's turns while it lasts, to whoever is standing in it then. It stays for
its whole length even when the enemy it was aimed at dies. For now the field's damage
goes straight through: it doesn't roll to hit, no defence is subtracted from it, and it
wears no armour. It hurts a vanished Rogue standing in it too, without ending its Vanish.
The Mage's ordinary column attack is different — its magic damage meets defence the way
any area attack does.

For now the two columns are the target's and the one to its right, or the one to its left
when the target is in the right-hand column. How much the field does each turn is set
once, when it's cast: a share, a placeholder, of the Mage's Intelligence, with help, plus
one roll of its staff. Casting it spends no use of the staff.
```

**Why:** The combat engine and the six combat types are built this way. "Keeps damaging"
didn't say when, and nothing said whether magic damage meets defence. With monsters having
the six types, a monster Mage's field is on the party's grid, which "the player's own
members" didn't foresee. Nothing said which two columns, how much the field does, whether
it spends a use of the staff, whether it outlives the enemy it was aimed at, or whether it
ends a vanished Rogue's Vanish. Whether the field should meet defence, which columns, how
much, and Vanish are proposed as questions below.

## Change: The Mage's bonus pays per hit, for now

> Proposed 2026-11-12 · for review

**Where:** `## The Mage`, third paragraph

**Now says:**

```
The Mage's bonus charge condition is allies in front of it in its own column taking hits.
```

**Proposed:**

```
The Mage's bonus charge condition is allies in front of it in its own column taking hits.
For now it pays for each enemy strike that lands on one of them, even one that defence
stops entirely.
```

**Why:** The combat types are built this way. "Taking hits" didn't say whether a hit that
does nothing counts, or how often the condition pays. How often each bonus pays is
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
- Which enemy does the Brute's special centre on? A close attack's targeted enemy is
  in the front row, which the special skips.
- Does the Brute's special cleave three wide in each of the two rows behind — up to six
  enemies — or hit three enemies in all?
- When a Brute's hit skips a Tank's defence, does it still wear the Tank's armour?
- Do the enemies next to the Brute's target, and every enemy in the Mage's column,
  take the full damage? Only Volley's neighbours are said to take reduced damage.
- Is the Tank's target taunted when his attack misses?
- "It also adds that defence to all the allies behind him" — is that the Shields Up
  increase, or the Tank's whole defence?
- If an ally moves into or out of the Tank's column while Shields Up lasts, does the bonus
  follow them?
- Is a Rogue's damage spread across its two strikes the way a Fighter's is? "Its strikes
  don't hit as hard as a Fighter's, because the weapon it carries adds less damage" only
  holds if the two are shaped alike.
- If the target of a Fighter's or a Rogue's ordinary attack dies mid-attack, do the
  rest of the strikes carry on to another enemy? Only the flurry is said to.
- Is the Archer's streak raise measured in points off the miss chance, or a share of it,
  and does it start with the second hit or the third?
- Does Volley spill forward only from the back row, or whenever the node behind is empty?
- Which two columns does the Mage's field cover?
- How much does the field do each turn — set from the Mage's damage when it's cast, or
  read again each turn? Does casting it spend a use of the staff?
- Does the field's damage end a Rogue's Vanish, the way an area attack does?
- How often does each type's bonus condition pay? The sheets name the condition, not how
  many times it pays in one attack.
```

**Why:** None of the docs answers these. The ones after the field's defence come from the
defaults the six combat types are built with. The existing entries are unchanged, and
"How fast does a special charge?" stays open.
