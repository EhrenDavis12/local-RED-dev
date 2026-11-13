# Equipment — proposed changes

> **Status:** Change notes against `Equipment.md`, for its owner to review. The original is
> not edited.

## Change: The Dorms shows none of a piece's numbers

> Proposed 2026-11-11 · for review

**Where:** `## Assignment`, first paragraph

**Now says:**

```
Gear sits in the guild's stores rather than belonging to any one member. The player
assigns weapons and armour to members in the Dorms, a part of the guild hall where they
see a piece's stats and hand gear to members.
```

**Proposed:**

```
Gear sits in the guild's stores rather than belonging to any one member. The player
assigns weapons and armour to members in the Dorms, a part of the guild hall where they
hand gear to members. For now the Dorms shows none of a piece's numbers — not its rolled
range and not its durability.
```

**Why:** Answered: the Dorms is just blank at the moment. That replaces "see a piece's
stats", which said the opposite.

## Change: Dorms-visibility question answered

> Proposed 2026-11-11 · for review

**Where:** `## Open Questions`

**Now says:**

```
- Does the player see a piece's exact rolled range and durability in the Dorms, or only a
  rough impression the way the recruiting board shows a candidate's strengths?
```

**Proposed:** delete. The other entries in `## Open Questions` stay as they are.

**Why:** Answered: the Dorms shows nothing of a piece's numbers for now, written into
Assignment.

## Change: For now a dive yields only gold

> Proposed 2026-11-11 · for review

**Where:** `## Where Gear Comes From`, fourth and fifth paragraphs

**Now says:**

```
Gear can drop too: both the dungeon and missions can drop a weapon or a piece of armour,
alongside the materials and items they yield.

Materials feed better equipment: some missions are hunts for materials to make better
equipment, and dives yield materials or items.
```

**Proposed:**

```
Gear can drop too: both the dungeon and missions can drop a weapon or a piece of armour,
alongside the materials and items they yield.

Materials feed better equipment: some missions are hunts for materials to make better
equipment, and dives yield materials or items.

For now, though, loot is just gold. In the first version a dive yields gold and nothing
else — no materials, no items, and no dropped gear.
```

**Why:** Answered: for now loot will just be gold. Both paragraphs have the dungeon
dropping gear and yielding materials or items, which the first version doesn't do; they
stay as the longer-term design, and the new paragraph scopes the first version.

## Change: A dead member's gear comes home, for now

> Proposed 2026-11-12 · for review

**Where:** `## Assignment`, last paragraph (a new paragraph after it)

**Now says:**

```
If a member dies in the dungeon, the party brings their gear back if there's room left
in the party's carrying capacity — the same capacity the Porter adds a lot of and any
member contributes to by carrying some of the loot; otherwise the gear is lost.
```

**Proposed:**

```
If a member dies in the dungeon, the party brings their gear back if there's room left
in the party's carrying capacity — the same capacity the Porter adds a lot of and any
member contributes to by carrying some of the loot; otherwise the gear is lost.

For now, though, a dead member's gear always comes home when the party walks out, whatever
gold the party is carrying, and goes back to the stores, held by no one. If a battle
leaves no one in the party alive, every piece the party took in is lost.
```

**Why:** The dive is built this way. The carry limit is now measured in gold (the
`The Dungeon.md` change "A party can turn back anywhere, and carries only so much gold
out"), and nothing says how gear counts against it, so for now it doesn't; that question
is proposed in The Dungeon's changes. The original didn't say what happens to the gear
when no one comes back.

## Change: Gear can be sold back to the shop

> Proposed 2026-11-11 · for review

**Where:** `## Where Gear Comes From`, second paragraph

**Now says:**

```
The shop is available from rank F, where the player can buy items and equipment.
```

**Proposed:**

```
The shop is available from rank F, where the player can buy items and equipment. The
player can sell gear back to the shop too, for a share of its price. The share is a
placeholder, to be balanced later.
```

**Why:** Answered: sure, yes — the player can sell gear back to the shop. No doc said gear
can be sold: `Core Concept.md`'s `## The Economy` has the guild selling items and
materials at the shop, and that sentence is left as it is. With a dive yielding only gold
for now, gear is the one thing the guild has to sell. What a piece's price is — each piece
is rolled, so two of the same kind and class differ, and crafted or dropped gear was never
bought — is not settled by this.

## Change: For now repair costs gold only

> Proposed 2026-11-11 · for review

**Where:** `## Repair`, first paragraph

**Now says:**

```
Repairs happen in the guild hall between dives. Repairing a piece that still has
durability left costs gold; fixing a piece that has broken costs gold and materials
both.
```

**Proposed:**

```
Repairs happen in the guild hall between dives. Repairing a piece that still has
durability left costs gold; fixing a piece that has broken costs gold and materials
both. For now, though, repair costs gold only: in the first version a broken piece is
fixed for gold and no materials.
```

**Why:** Answered: for now, repair costs gold only. Nothing in the first version gives the
guild materials, so a broken piece could not otherwise be fixed. The paragraph and the
third paragraph's "for gold and materials" stay as the longer-term design; the new
sentence scopes the first version. The open question on which materials a broken piece needs stays open for that
longer-term design.

## Change: Two questions on stores and condition

> Proposed 2026-11-11 · for review

**Where:** `## Open Questions`, at the end of the list

**Now says:**

```
- Does the Armourer have a station of its own the way the Blacksmith has the smithy,
  deciding which of two Armourers sets armour quality?
```

**Proposed:**

```
- Does the Armourer have a station of its own the way the Blacksmith has the smithy,
  deciding which of two Armourers sets armour quality?
- Are the guild's stores capped?
- Where do the condition bands' edges fall? Good is above 50% and Worn is 25% to 49%, so a
  piece at exactly 50% — or between 49% and 50%, or between 24% and 25% — sits in no band.
```

**Why:** None of the docs answers the first. The second is a gap in `## Durability`'s
condition list. The existing entries, and the pending deletion of the Dorms question, are
unchanged.

## Change: A hit that does nothing still wears gear

> Proposed 2026-11-12 · for review

**Where:** `## Durability`, first paragraph

**Now says:**

```
Gear wears down as it is used — weapons degrade from attacking, armour from being hit. It
works fully until it reaches zero, then breaks and contributes nothing — there is no
gradual decline before that.
```

**Proposed:**

```
Gear wears down as it is used — weapons degrade from attacking, armour from being hit. It
works fully until it reaches zero, then breaks and contributes nothing — there is no
gradual decline before that. A hit counts even when defence takes all of its damage: the
armour that took it still spends a use, and so does the weapon that landed it, unless the
hit came from a special.
```

**Why:** The combat engine is built this way. With no minimum damage, a hit can do nothing,
and "each hit the weapon lands" didn't say whether such a hit still counts.
A special spends none of the weapon's uses, as `## Durability` already says further down.

## Change: For now the shop sells class F only

> Proposed 2026-11-13 · for review

**Where:** `## Quality`, the paragraph beginning "The shop sells equipment of a baseline
quality" (a new paragraph after it)

**Now says:**

```
The shop sells equipment of a baseline quality, and that baseline rises with guild rank. A
crafter in the guild produces better than the shop's baseline.
```

**Proposed:**

```
The shop sells equipment of a baseline quality, and that baseline rises with guild rank. A
crafter in the guild produces better than the shop's baseline.

For now, though, the shop's baseline stays at class F. A piece of any class can be made,
but only class F has a price, so a guild at rank F buys class F gear and the shop has
nothing for a guild above rank F.
```

**Why:** The game is built this way. What the baseline is above F, and what a piece costs
there, isn't settled, so the shop doesn't rise with the guild yet. No guild rises above
rank F yet, so the empty shop above F doesn't come up.

## Change: For now a span is no wider at SSS than at F

> Proposed 2026-11-13 · for review

**Where:** `## Quality`, second paragraph

**Now says:**

```
A weapon carries two attributes: an Attack Damage range and a Durability. Each kind of
weapon has its own Attack Damage range, and so does each class — the ranges differ per
kind so the damage comes out balanced across the combat types. But a weapon's range is not
a fixed figure for its kind and class: each kind at each class has a wider band, and an
individual piece's own range is drawn from inside that band when the piece is made, so two
pieces of the same kind and class are not the same. The span itself is rolled too, not
just where it sits in the band — one piece's range can come out wider or narrower than
another's, not only higher or lower within it.
```

**Proposed:**

```
A weapon carries two attributes: an Attack Damage range and a Durability. Each kind of
weapon has its own Attack Damage range, and so does each class — the ranges differ per
kind so the damage comes out balanced across the combat types. But a weapon's range is not
a fixed figure for its kind and class: each kind at each class has a wider band, and an
individual piece's own range is drawn from inside that band when the piece is made, so two
pieces of the same kind and class are not the same. The span itself is rolled too, not
just where it sits in the band — one piece's range can come out wider or narrower than
another's, not only higher or lower within it.
For now a span is rolled anywhere from a single figure to four points wide, and never
wider than its band, at every class — so an SSS knife's span, inside 512–3072, is no wider
than an F knife's inside 2–12. The same goes for armour's Defence.
```

**Why:** The game is built this way, with placeholder widths. How narrow or wide a span can
be is asked in `## Open Questions` and stays open there. Because the bands double each
class and the width doesn't, a top-class piece comes out as almost a single figure.
Whether the widest span should grow with class is proposed as a question for
`## Open Questions`.

## Change: A question on span width

> Proposed 2026-11-13 · for review

**Where:** `## Open Questions`, after the entry beginning "How narrow or wide can a rolled
span be"

**Now says:**

```
- How narrow or wide can a rolled span be — can a piece come out with a single figure
  rather than a range, or with a span as wide as the whole band?
```

**Proposed:**

```
- How narrow or wide can a rolled span be — can a piece come out with a single figure
  rather than a range, or with a span as wide as the whole band?
- Should the widest a rolled span can be grow with class, doubling the way the bands do,
  or stay the same at every class?
```

**Why:** None of the docs answers it. The span width above is a default for now. The other
entries, and the pending changes to this list, are unchanged.
