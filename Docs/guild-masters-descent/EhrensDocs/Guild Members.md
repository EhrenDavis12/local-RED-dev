# Guild Members — proposed changes

> **Status:** Change notes against `Guild Members.md`, for its owner to review. The original
> is not edited.

## Change: Three questions on levelling and promotion

> Proposed 2026-11-11 · for review

**Where:** `## Open Questions`, at the end of the list

**Now says:**

```
- A hit's damage can land on a fraction — the mitigation is a ratio, and an area attack
  takes two-thirds of the defence into it. Which way does that round? It decides whether
  a hit from far below a member's rank is chip damage forever or genuinely nothing.
```

**Proposed:**

```
- A hit's damage can land on a fraction — the mitigation is a ratio, and an area attack
  takes two-thirds of the defence into it. Which way does that round? It decides whether
  a hit from far below a member's rank is chip damage forever or genuinely nothing.
- When a level-up uses up experience, does the leftover carry toward the next level?
- Do two recruits of the same type and the same rank or tier start with exactly the same
  stats? Starting Stats says they're set by type and rank or tier, but the recruiting
  board's rough impression of a candidate's strengths — promising, unremarkable — suggests
  they can differ.
- Can an injured member be promoted?
```

**Why:** None of the docs answers these. The existing entries are unchanged.

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
the combat ends, and only they get a share.
```

**Why:** The dive is built this way. "All party members" doesn't say whether that's the
ones who started the combat or the ones still alive. That's proposed as a question for
`## Open Questions`.

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

**Now says:**

```
- A hit's damage can land on a fraction — the mitigation is a ratio, and an area attack
  takes two-thirds of the defence into it. Which way does that round? It decides whether
  a hit from far below a member's rank is chip damage forever or genuinely nothing.
```

**Proposed:**

```
- A hit's damage can land on a fraction — the mitigation is a ratio, and an area attack
  takes two-thirds of the defence into it. Which way does that round? It decides whether
  a hit from far below a member's rank is chip damage forever or genuinely nothing.
- In "divided equally between all party members", which members count: the ones who
  started the combat or the ones still alive?
```

**Why:** The game is built with a default for now on this, in the change above. The
pending "Three questions on levelling and promotion" change to this list is unchanged.

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
There is no minimum damage — enough defence can reduce a hit to nothing.
```

**Proposed:**

```
There is no minimum damage — enough defence can reduce a hit to nothing. For now a hit's
damage is worked out exactly and rounded down once, at the end of the hit, after
everything that changes it: the fraction, the reduced damage Volley's neighbours take,
and the Archer's streak. Nothing rounds along the way, and a hit that comes to less than
one does nothing.
```

**Why:** The combat engine is built this way. Which way a fractional hit rounds is asked
in `## Open Questions` and stays open there. Nothing said whether a hit rounds once or at
each step, and rounding at each step loses a point every time.

## Change: The Mage's field is an area attack, for now

> Proposed 2026-11-13 · for review

**Where:** `## Base Stats`, last paragraph

**Now says:**

```
An attack can miss an evasive target. Area attacks — the AoE effects — can't miss: they
land on a space rather than on a person, so evasion does nothing against them. They do
pay a reduced defence, though: an area attack uses two-thirds of the target's defence
when working the fraction above.
```

**Proposed:**

```
An attack can miss an evasive target. Area attacks — the AoE effects — can't miss: they
land on a space rather than on a person, so evasion does nothing against them. They do
pay a reduced defence, though: an area attack uses two-thirds of the target's defence
when working the fraction above. For now the Mage's lingering field counts as an area
attack each time it deals damage: it can't miss, and it uses two-thirds of the victim's
defence, worked with the Mage's K.
```

**Why:** The combat engine is built this way. Whether the field's damage counts as an area
attack is asked in `## Open Questions` and stays open there. What else the field does is
in the `Individual Types.md` change "Where the Mage's field lies, and what it does, for
now".

## Change: Health counts a member's own Constitution, and what's taken stays taken, for now

> Proposed 2026-11-13 · for review

**Where:** `## Base Stats`, the paragraph on health

**Now says:**

```
A member's health is their Constitution times ten — at F rank, where stats are
single-digit, that's a pool in the tens. It is what damage comes out of: whatever gets
through defence is taken off that pool. Because it comes from Constitution, it grows as
Constitution grows, with no separate rule for levelling. Constitution already means
toughness, so it is the pool and the base of defence both, and health needs no stat of its
own.
```

**Proposed:**

```
A member's health is their Constitution times ten — at F rank, where stats are
single-digit, that's a pool in the tens. It is what damage comes out of: whatever gets
through defence is taken off that pool. Because it comes from Constitution, it grows as
Constitution grows, with no separate rule for levelling. Constitution already means
toughness, so it is the pool and the base of defence both, and health needs no stat of its
own. A specialist's health and a monster's come the same way, from their own
Constitution.

For now health counts only a member's own Constitution, never what the support ring adds.
The Tank's primary stat is Constitution, and help that reached its health would make its
pool change with who stands next to it, and shrink when they move away or die. Help still
counts toward the defence Constitution gives. For now, too, when a level-up raises
Constitution mid-dive, current health rises by the same ten a point as the maximum does,
so the damage already taken stays taken.
```

**Why:** The game is built this way. "A member's health" sits under "the fighting
members", which leaves specialists unsaid; Levels and Experience has specialists gain base
stats the same way divers do, and the Dungeon change notes give a monster the same stat
rules. Help raises the receiver's primary stat, and nothing says whether that reaches
health; nor does "it grows as Constitution grows" say what happens to the health a member
has left. Both are proposed as questions in "Questions on health".

## Change: Questions on health

> Proposed 2026-11-13 · for review

**Where:** `## Open Questions`, at the end of the list

**Now says:**

```
- A hit's damage can land on a fraction — the mitigation is a ratio, and an area attack
  takes two-thirds of the defence into it. Which way does that round? It decides whether
  a hit from far below a member's rank is chip damage forever or genuinely nothing.
```

**Proposed:**

```
- A hit's damage can land on a fraction — the mitigation is a ratio, and an area attack
  takes two-thirds of the defence into it. Which way does that round? It decides whether
  a hit from far below a member's rank is chip damage forever or genuinely nothing.
- Help raises the receiver's primary stat, and the Tank's is Constitution. Does that help
  raise the Tank's health too, or only its defence?
- When a level-up raises a member's Constitution mid-dive, does their current health rise
  with the maximum, or stay where it was with only the ceiling moving?
```

**Why:** The game is built with a default for now on each of these, in "Health counts a
member's own Constitution, and what's taken stays taken, for now", and none of the docs
settles them. The pending "Three questions on levelling and promotion" and "A question on
sharing experience" changes to this list are unchanged; these go after the entries they
add.
