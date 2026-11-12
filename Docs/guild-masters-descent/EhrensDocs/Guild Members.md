# Guild Members — proposed changes

> **Status:** Change notes against `Guild Members.md`, for its owner to review. The original
> is not edited.

## Change: Starting health is set by rank, and F rank starts at 10

> Proposed 2026-11-11 · for review

**Where:** `## Starting Stats`, second paragraph (a new paragraph after it)

**Now says:**

```
A newly recruited level-1 F-rank member starts with single-digit stats.
```

**Proposed:**

```
A newly recruited level-1 F-rank member starts with single-digit stats.

A member's starting health is based on their rank. An F-rank member starts with 10
health, and a higher-rank hire starts with more. For now those are basic numbers, and
placeholders to be tuned — 10 and every other rank's health alike.
```

**Why:** Answered: let's just start with a basic health number at 10. Answered too: based
on rank, and F ranks are 10 for now. No doc said what health a member has, though The
Dungeon's rest area "where the party heals" and Combat's enemy targeting on "how easy it
is to kill" both rely on one. Health set by rank fits the first paragraph's "a C-rank
hire starts higher across the board than an F-rank one". The existing paragraph is
unchanged. Not settled by this: how much health each rank above F starts with; whether a
specialist's starting health follows their tier the same way; whether health grows with
level or with a promotion; and whether Constitution plays into it.

## Change: Three questions on levelling and promotion

> Proposed 2026-11-11 · for review

**Where:** `## Open Questions`

**Now says:**

```
- What is having a type advantage actually worth in a fight?
- Does the experience a defeated enemy is worth scale with dungeon depth?
```

**Proposed:**

```
- What is having a type advantage actually worth in a fight?
- Does the experience a defeated enemy is worth scale with dungeon depth?
- When a level-up uses up experience, does the leftover carry toward the next level?
- Do two recruits of the same type and the same rank or tier start with exactly the same
  stats? Starting Stats says they're set by type and rank or tier, but the recruiting
  board's rough impression of a candidate's strengths — promising, unremarkable — suggests
  they can differ.
- Can an injured member be promoted?
```

**Why:** None of the docs answers these. The existing entries are unchanged.

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

## Change: For now a type advantage multiplies what's left after defence

> Proposed 2026-11-12 · for review

**Where:** `## Combat Types`, last paragraph

**Now says:**

```
A type advantage is a damage multiplier: an advantaged attack deals proportionally more
damage than the same attack without the advantage. Each matchup's own mechanism is
covered in the Individual Types doc.
```

**Proposed:**

```
A type advantage is a damage multiplier: an advantaged attack deals proportionally more
damage than the same attack without the advantage. For now the multiplier applies to the
damage left once defence is subtracted, so a hit that defence stops entirely still does
nothing, and how much it multiplies by is a placeholder. Each matchup's own mechanism is
covered in the Individual Types doc.
```

**Why:** The combat engine is built this way. The open question on what an advantage is
worth stays open. Whether it applies before or after defence is proposed as a question
below.

## Change: Two questions on type advantage and defence

> Proposed 2026-11-12 · for review

**Where:** `## Open Questions`, after the first entry

**Now says:**

```
- What is having a type advantage actually worth in a fight?
```

**Proposed:**

```
- What is having a type advantage actually worth in a fight?
- Does a type advantage multiply the damage before defence is subtracted, or after it?
- Does a Brute striking a Tank get both the defence subtraction skipped and the
  multiplier, or only one of them?
```

**Why:** The docs read two ways here. `Individual Types.md` has the Brute's advantage over
the Tank as "bypassing the defence subtraction entirely", while `## Combat Types` says a
type advantage "is a damage multiplier". The pending "Three questions on levelling and
promotion" change to this list is unchanged.
