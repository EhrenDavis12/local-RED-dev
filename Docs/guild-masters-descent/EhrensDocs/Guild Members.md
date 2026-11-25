# Guild Members — proposed changes

> **Status:** Change notes against `Guild Members.md`, for its owner to review. The original
> is not edited.

## Change: Two questions on recruits and promotion

> Proposed 2026-11-11 · for review

**Where:** `## Open Questions`, which is empty in the original

**Now says:** nothing — the original's `## Open Questions` is empty.

**Proposed:**

```
- Do two recruits of the same type and the same rank or tier start with exactly the same
  stats? Starting Stats says they're set by type and rank or tier, but the recruiting
  board's rough impression of a candidate's strengths — promising, unremarkable — suggests
  they can differ.
- Can an injured member be promoted?
```

**Why:** None of the docs answers these.

## Change: Who shares a combat's experience, for now

> Proposed 2026-11-12 · for review

**Where:** `## Levels and Experience`, the paragraph after the list of what a kill is worth

**Now says:**

```
The total is added up at the end of a combat and divided equally between all party
members, counting specialists.
```

**Proposed:**

```
The total is added up at the end of a combat and divided equally between all party
members, counting specialists. For now the members counted are the ones still alive when
the combat ends, and only they get a share. Each share is exact, never rounded, so the
shares always add back up to the total. For now, too, a combat that ends in a stand-off
still pays for the enemies killed in it before the party turns back.
```

**Why:** The dive is built this way. "All party members" doesn't say whether that's the
ones who started the combat or the ones still alive. That's proposed as a question for
`## Open Questions`. Nor did anything say whether a share rounds, or whether a stand-off,
which nobody wins, pays for its kills; experience comes from kills and is added up at the
end of a combat, and a stand-off still ends one. The stand-off is proposed as a question
in "Questions on experience".

## Change: A kill pays on the enemy's cost, exactly

> Proposed 2026-11-24 · for review

**Where:** `## Levels and Experience`, the list after "The total is added up at the end of
a combat" (a new paragraph after it)

**Now says:**

```
- What a kill pays is that rank value scaled by what the enemy cost to put on the floor.
  An enemy built at its rank's full baseline cost pays the rank value in full; one built
  at a third of that baseline pays a third of it.
- So a battle's experience is set by the power it was given rather than by how that
  power was divided — the same points spent as a horde of weak enemies and as a handful
  of strong ones pay the same total.
- What an enemy costs, and the baseline cost for each rank, are covered in the Dungeon
  doc.
```

**Proposed:**

```
- What a kill pays is that rank value scaled by what the enemy cost to put on the floor.
  An enemy built at its rank's full baseline cost pays the rank value in full; one built
  at a third of that baseline pays a third of it.
- So a battle's experience is set by the power it was given rather than by how that
  power was divided — the same points spent as a horde of weak enemies and as a handful
  of strong ones pay the same total.
- What an enemy costs, and the baseline cost for each rank, are covered in the Dungeon
  doc.

What a kill pays is exact and never rounded, and an enemy that cost more than its rank's
baseline pays more than the rank value. The cost it pays on is the enemy's whole cost,
never what its stats add up to. For now an enemy on a mission played by hand isn't built
from a floor's power, so its kill pays its rank's value in full.
```

**Why:** The game is built this way. The original scales a kill by the enemy's cost but
doesn't say whether that rounds; paying exactly is what keeps its promise that a horde
and a handful pay the same total. Paying on the cost rather than the stats means gear on
a monster later takes part of its points without changing what its kill pays. The
pending "Who shares a combat's experience, for now" change to the paragraph before is
unchanged.

## Change: Help counts where everyone stands right now

> Proposed 2026-11-12 · for review

**Where:** `## The Support Ring`, third paragraph

**Now says:**

```
Help gives a benefit that increases power. It applies when the two members are located
next to each other on the battle map — diagonals count as being next to each other. It's
many-to-many: a member can give help to multiple allies while receiving help from multiple
allies.
```

**Proposed:**

```
Help gives a benefit that increases power. It applies when the two members are located
next to each other on the battle map — diagonals count as being next to each other. It's
many-to-many: a member can give help to multiple allies while receiving help from multiple
allies. Help counts where everyone stands and who is still alive at the moment it's used,
so a death or a change of formation mid-battle changes it straight away.
```

**Why:** The combat engine is built this way. With formation changes free mid-battle and
members dying on the spot, it matters whether help is fixed when a battle starts or follows
the board as it changes.

## Change: A question on sharing experience

> Proposed 2026-11-12 · for review

**Where:** `## Open Questions`, at the end of the list

**Now says:** nothing — the original's `## Open Questions` is empty.

**Proposed:**

```
- In "divided equally between all party members", which members count: the ones who
  started the combat or the ones still alive?
```

**Why:** The game is built with a default for now on this, in the change above. The
pending "Two questions on recruits and promotion" change to this list is unchanged.

## Change: A specialist's K comes from its tier

> Proposed 2026-11-13 · for review

**Where:** `## Base Stats`, the paragraph after the list of K by rank

**Now says:**

```
K doubles at each rank, the same way the damage and defence bands double.
```

**Proposed:**

```
K doubles at each rank, the same way the damage and defence bands double.

A specialist climbs tiers, not ranks, so its K comes from its tier, rung for rung: a
Novice's K is 20, an Apprentice's 40, and so on up to 5,120 at Grandmaster SSS.
```

**Why:** The combat engine is built this way. K comes from the attacker's rank, and a
specialist has none. The Specialists doc's `## Tiers` has a tier stand in for a rank rung
for rung wherever a rank is compared to something else, which this reads as covering K.

## Change: A hit rounds down once, at the end, for now

> Proposed 2026-11-13 · for review

**Where:** `## Base Stats`, the line on minimum damage

**Now says:**

```
There is no minimum damage — enough defence can reduce a hit to nothing, and a hit's
damage rounds down, so anything short of a full point is nothing at all.
```

**Proposed:**

```
There is no minimum damage — enough defence can reduce a hit to nothing, and a hit's
damage rounds down, so anything short of a full point is nothing at all. For now that
rounding happens once, at the end of the hit, after everything that changes it: the
fraction, the reduced damage Volley's neighbours take, and the Archer's streak. Nothing
rounds along the way.
```

**Why:** The combat engine is built this way. Nothing says whether a hit rounds once or at
each step, and rounding at each step loses a point every time.

## Change: Health counts a member's own Constitution, and what's taken stays taken, for now

> Proposed 2026-11-13 · for review

**Where:** `## Base Stats`, the paragraph on health

**Now says:**

```
A member's health is their Constitution times ten — the Brute's is times twelve — at F
rank, where stats are single-digit, that's a pool in the tens. It is what damage comes
out of: whatever gets through defence is taken off that pool. Because it comes from
Constitution, it grows as Constitution grows, with no separate rule for levelling.
Constitution already means toughness, so it is the pool and the base of defence both, and
health needs no stat of its own.
```

**Proposed:**

```
A member's health is their Constitution times ten — the Brute's is times twelve — at F
rank, where stats are single-digit, that's a pool in the tens. It is what damage comes
out of: whatever gets through defence is taken off that pool. Because it comes from
Constitution, it grows as Constitution grows, with no separate rule for levelling.
Constitution already means toughness, so it is the pool and the base of defence both, and
health needs no stat of its own. A specialist's health and a monster's come the same way, from their own
Constitution.

For now health counts only a member's own Constitution, never what the support ring adds.
The Tank's primary stat is Constitution, and help that reached its health would make its
pool change with who stands next to it, and shrink when they move away or die. Help still
counts toward the defence Constitution gives. For now, too, when a level-up raises
Constitution mid-dive, current health rises by as much as the maximum does, so the damage
already taken stays taken.
```

**Why:** The game is built this way. "A member's health" sits under "the fighting
members", which leaves specialists unsaid; Levels and Experience has specialists gain base
stats the same way divers do, and the Dungeon change notes give a monster the same stat
rules. Help raises the receiver's primary stat, and nothing says whether that reaches
health; nor does "it grows as Constitution grows" say what happens to the health a member
has left. Both are proposed as questions in "Questions on health".
For the owner to reconcile: experience is shared at the end of every combat, so a
level-up that raises Constitution after a battle partway through a floor raises current
health before the next battle, while The Dungeon.md says nothing comes back between the
battles on a single floor.

## Change: Questions on health

> Proposed 2026-11-13 · for review

**Where:** `## Open Questions`, at the end of the list

**Now says:** nothing — the original's `## Open Questions` is empty.

**Proposed:**

```
- Help raises the receiver's primary stat, and the Tank's is Constitution. Does that help
  raise the Tank's health too, or only its defence?
- When a level-up raises a member's Constitution mid-dive, does their current health rise
  with the maximum, or stay where it was with only the ceiling moving?
```

**Why:** The game is built with a default for now on each of these, in "Health counts a
member's own Constitution, and what's taken stays taken, for now", and none of the docs
settles them. The pending "Two questions on recruits and promotion" and "A question on
sharing experience" changes to this list are unchanged; these go after the entries they
add.

## Change: Experience is the bar, level is the number

> Proposed 2026-11-13 · for review

**Where:** `## Promotion`, last paragraph and its list (new paragraphs after them)

**Now says:**

```
Crossing a rank also costs a set amount of experience, multiplying by five at each step:

- F to E — 20
- E to D — 100
- D to C — 500
- C to B — 2,500
- B to A — 12,500
- A to S — 62,500
- S to SS — 312,500
- SS to SSS — 1,562,500
```

**Proposed:**

```
Crossing a rank also costs a set amount of experience, multiplying by five at each step:

- F to E — 20
- E to D — 100
- D to C — 500
- C to B — 2,500
- B to A — 12,500
- A to S — 62,500
- S to SS — 312,500
- SS to SSS — 1,562,500

For now the steps are uneven by at most a point, so a rank's total stays exact: level N of
a rank is reached once ceil(cost × (N−1) ÷ (threshold−1)) experience has been earned in
that rank. For F to E that puts level 2 at 2, level 3 at 3, level 4 at 4, level 5 at 6,
and level 16 at 20.

Promotion needs the level threshold and the gold and nothing more — the experience is
never checked or spent on its own — and starts the member in the new rank at level 1
with the bar empty. For now the bar on the member sheet fills across the whole rank,
toward the threshold, rather than toward the next level. For now, too, a member at the
top of the ladder — SSS, or a specialist at Grandmaster SSS — has no rank left to cross,
so earns no experience and gains no levels.
```

**Why:** Answered 2026-11-13: "level is a number experience as a bar". The original's
`## Promotion` spreads a rank's cost evenly across its level-ups; how that even spread
lands on whole points isn't settled, and rounding up is a placeholder for now and cheap
to change. The one bar also settles whether leftover experience carries toward the next
level: the bar is never spent, only read, so nothing is left over. Promotion's "only the
level counter resets" is about the stats being kept; the bar empties with the level,
since it holds what was earned in the old rank. What the member sheet's bar fills toward,
and the top of the ladder, are defaults for now, each proposed as a question in
"Questions on experience".

## Change: Questions on experience

> Proposed 2026-11-13 · for review

**Where:** `## Open Questions`, at the end of the list

**Now says:** nothing — the original's `## Open Questions` is empty.

**Proposed:**

```
- Does a combat that ends in a stand-off still pay for the enemies killed in it?
- The member sheet shows one experience bar. Does it fill toward the next level, or across
  the whole rank toward the threshold?
- A member at SSS, or a specialist at Grandmaster SSS, has no rank left to cross. Do they
  still earn experience and gain levels?
```

**Why:** The game is built with a default for now on each of these, in "Who shares a
combat's experience, for now" and "Experience is the bar, level is the number", and none
of the docs settles them. The pending changes to this list above are unchanged; these go
after the entries they add.

## Change: Help comes back to whole points once

> Proposed 2026-11-18 · for review

**Where:** `## Diminishing Returns on Help`, second paragraph

**Now says:**

```
The bonus applies to the receiving member's primary stat — the stat its type's ordering
leads on. The first help rounds up to at least one point; every later help is exact, so
at low stats a later help can come to nothing.
```

**Proposed:**

```
The bonus applies to the receiving member's primary stat — the stat its type's ordering
leads on. The first help rounds up to at least one point; every later help is exact, so
at low stats a later help can come to nothing. The helps are added up and the total is
rounded down once, to whole points: on a primary stat of 30, one help adds 2, two add 2,
and three add 3.
```

**Why:** The combat engine is built this way. "Every later help is exact" didn't say how
the exact helps come back to the whole points a stat counts in, and rounding the total
down is what lets a later help come to nothing.

## Change: Starting stats by type

> Proposed 2026-11-19 · for review

**Where:** `## Starting Stats`, second paragraph (new text after it)

**Now says:**

```
A newly recruited level-1 F-rank member starts with single-digit stats.
```

**Proposed:**

```
A newly recruited level-1 F-rank member starts with single-digit stats. Before any help
from the support ring, a member at F rank and level 1, or a specialist at Novice, starts
with these:

| Type | Str / Dex / Con / Int / Luck |
|---|---|
| Brute | 8 / 6 / 7 / 4 / 5 |
| Tank | 7 / 6 / 8 / 4 / 5 |
| Fighter | 8 / 7 / 6 / 4 / 5 |
| Rogue | 6 / 8 / 5 / 4 / 7 |
| Archer | 7 / 8 / 5 / 4 / 6 |
| Mage | 4 / 7 / 6 / 8 / 5 |
| Cook | 6 / 7 / 8 / 4 / 5 |
| Porter | 8 / 5 / 7 / 4 / 6 |

The six combat types' lines are Battle Test's teams with the one point of help each
member gets there taken off its primary stat. For now the Cook's and the Porter's are 2
up in every stat, in step with the fighters. For now a recruit on the recruiting board
varies from its type's line by up to 1 point either way in each stat, kept between 1 and
9.
```

**Why:** The user, 2026-11-18: "if something from the new docs contradicts the choices
that we make the new docs win". Battle Test's level-1 F-rank teams give a starting line
for each of the six combat types. Its tables already include one point of support-ring
help on each member's primary stat, so the starting line is that point lower. Battle Test
doesn't cover the Cook or the Porter. The game's placeholder lines ran 2 below Battle
Test's for every type, and the Cook's and the Porter's go up by the same 2 for now. That
is proposed as a question in "A question on the Cook's and the Porter's starting stats".
This doc's `Combat.md` seconds list already uses these lines. Its Rogue worked list
doesn't, and has a change note of its own.

## Change: A question on the Cook's and the Porter's starting stats

> Proposed 2026-11-19 · for review

**Where:** `## Open Questions`, at the end of the list

**Now says:** nothing — the original's `## Open Questions` is empty.

**Proposed:**

```
- The cook and the porter aren't in the other dev's numbers. If the fighters' starting
  stats go up by 2, should the cook and porter go up by the same 2, or stay where they
  are?
```

**Why:** The game goes ahead with a default on this, in "Starting stats by type", and
none of the docs settles it. The pending changes to this list above are unchanged; this
goes after the entries they add.
