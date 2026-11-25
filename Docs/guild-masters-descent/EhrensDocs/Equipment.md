# Equipment — proposed changes

> **Status:** Change notes against `Equipment.md`, for its owner to review. The original is
> not edited.

## Change: For now no gear drops, and a mission yields only gold

> Proposed 2026-11-25 · for review

**Where:** `## Where Gear Comes From`, fourth and fifth paragraphs

**Now says:**

```
Gear can drop too: both the dungeon and missions can drop a weapon or a piece of armour,
alongside the materials and items they yield. Dropped gear is rolled the same way a
crafted or bought piece is, and its class comes from where it dropped — from the
dungeon's own rank and how deep the floor is for a dungeon drop, and from the mission's
rank for a mission drop.

Materials feed better equipment: some missions are hunts for materials to make better
equipment, and dives yield materials or items.
```

**Proposed:**

```
Gear can drop too: both the dungeon and missions can drop a weapon or a piece of armour,
alongside the materials and items they yield. Dropped gear is rolled the same way a
crafted or bought piece is, and its class comes from where it dropped — from the
dungeon's own rank and how deep the floor is for a dungeon drop, and from the mission's
rank for a mission drop.

Materials feed better equipment: some missions are hunts for materials to make better
equipment, and dives yield materials or items.

For now, though, no gear drops. In the first version a dive yields gold, ore, herb and
healing potions, and a mission yields gold and nothing else.
```

**Why:** Dropped gear isn't built. Both paragraphs have the dungeon dropping gear; they
stay as the longer-term design, and the new paragraph scopes the first version. What a
dive drops, and how it's carried home, is in The Dungeon's change "For now a dive drops
ore, herb and healing potions, and no gear". Missions are held to gold, for now: that's a
default the build chose, not yet the user's word, and it's proposed as a question in Core
Concept's change "Questions on missions' defaults".

## Change: A dead member's gear takes a slot a piece, for now

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

For now each piece a dead member had on — weapon, armour, and a Tank's shield, broken
or not — takes one slot. The room left is counted as the dive ends: the slots of the
members still alive, a Porter's extra ones too, less the potions they still hold. A
dead member's slots count for nothing, their potions take none of the room, and no
potion or gold is left behind to make room for gear, though loot is: the gear takes its
slots first, and loot gets what's left. The pieces come home in the order
the party was picked, each dead member's weapon first, then armour, then shield, and go
back to the stores, held by no one; whatever no longer fits is left in the dungeon and
lost. If a battle leaves no one in the party alive, every piece the party took in is
lost.
```

**Why:** The dive is built this way. The original has the gear come back only if there's
room left in the party's carrying capacity, which is counted in slots (`The Dungeon.md`,
`## The Dungeon`), but doesn't say how many slots a piece takes, how the room is
counted, which pieces come home when there isn't room for all, or what happens to the
gear when no one comes back. One slot a piece is a placeholder kept in the game's tuning
file with the others. Which pieces come home first, and counting the room as the dive
ends, are defaults the build chose, not yet the user's word, and they're proposed as
questions in The Dungeon's change "Questions on the dive's defaults". Gear coming home
before loot is a default too, proposed as a question in The Dungeon's change "Questions
on loot".

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
materials at the shop, and that sentence is left as it is. For now the shop buys back
only gear: ore, herb and potions can't be sold. What a piece's price is — each piece
is rolled, so two of the same kind and class differ, and crafted or dropped gear was never
bought — is not settled by this.

## Change: For now repair costs gold only

> Proposed 2026-11-11 · for review

**Where:** `## Repair`, first paragraph

**Now says:**

```
Repairs happen in the guild hall between dives. Repairing a piece that still has
durability left costs gold; fixing a piece that has broken costs gold and materials
both. The gold a repair costs scales with the piece's class, the way its damage and
defence bands do.
```

**Proposed:**

```
Repairs happen in the guild hall between dives. Repairing a piece that still has
durability left costs gold; fixing a piece that has broken costs gold and materials
both. The gold a repair costs scales with the piece's class, the way its damage and
defence bands do. For now, though, repair costs gold only: in the first version a broken
piece is fixed for gold and no materials.
```

**Why:** Answered: for now, repair costs gold only. Dives bring home ore and herb, but
nothing spends them yet, so a broken piece is fixed for gold alone. The paragraph and the
third paragraph's "for gold and materials" stay as the longer-term design; the new
sentence scopes the first version. The open question on how much ore or herb a broken
piece needs stays open for that longer-term design.

## Change: Two questions on stores and condition

> Proposed 2026-11-11 · for review

**Where:** `## Open Questions`, after the entry beginning "Crafting a piece and fixing a
broken one"

**Now says:**

```
- Crafting a piece and fixing a broken one both take materials, which come as ores or
  herbs — the Dungeon doc covers where they come from — and it isn't said how much of
  either goes into which.
```

**Proposed:**

```
- Crafting a piece and fixing a broken one both take materials, which come as ores or
  herbs — the Dungeon doc covers where they come from — and it isn't said how much of
  either goes into which.
- Are the guild's stores capped?
- Where do the condition bands' edges fall? Good is above 50% and Worn is 25% to 49%, so a
  piece at exactly 50% — or between 49% and 50%, or between 24% and 25% — sits in no band.
```

**Why:** None of the docs answers the first. The second is a gap in `## Durability`'s
condition list. The existing entries are unchanged.

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

## Change: The Tank carries a shield, and shields can be swapped

> Proposed 2026-11-14 · for review

**Where:** `## What a Member Carries`, the paragraph beginning "How much defence armour
adds depends on its kind too" (a new paragraph after it)

**Now says:**

```
How much defence armour adds depends on its kind too. The Tank's full armour adds more
defence than the Brute's tanned hide, and the Fighter's light armour sits between the two.
Each kind of armour can only be worn by its own combat type, so the player never chooses
between kinds.
```

**Proposed:**

```
How much defence armour adds depends on its kind too. The Tank's full armour adds more
defence than the Brute's tanned hide, and the Fighter's light armour sits between the two.
Each kind of armour can only be worn by its own combat type, so the player never chooses
between kinds.

The Tank carries a shield as well as its weapon and its armour. A shield is a piece of
gear: there is more than one shield, and the player can equip a Tank with a shield, take
it off, or swap it for another.

A shield adds defence on top of the Tank's armour, so a Tank with a shield takes less
damage from every hit. It wears down and breaks just like all other gear: it loses
durability as it's used, it can break partway through a battle and then adds nothing, and
it's repaired the way a weapon or armour is. How much defence a shield adds and how much
durability it has are placeholders, to be balanced later.

For now a shield is built the way armour is. It sits in a slot of its own beside the
Tank's weapon and armour, and never goes in either of theirs. It has a class, a Defence
range and a Durability, each rolled once when it's made; its Defence band doubles with
each class above F, and its Durability band is the same at every class. There are four
shields, each its own item with its own shop entry, and the shop sells all four at class
F. In a battle the shield's range is rolled afresh on every strike, the same as the
armour's, and it counts as part of the Tank's defence on every strike against him — a
Brute's hit quarters the whole of it, shield, armour and any Shields Up on him together.
It isn't part of the figure Shields Up adds, which leaves the shield out, as Individual
Types' change "The Tank's taunt, Shields Up and bonus, for now" says. It spends one use
on every hit that lands on the Tank, wherever the armour spends one, and Shields Up
spends none of it.
```

**Why:** Answered 2026-11-14: "we should keep the shield swappable" — "item wise will
have other shields that can be equipped and equipped". The docs already gave the Tank a
shield (the Brute pushes "the Tank's shield aside" in `Individual Types.md`, and the
Tank's special is Shields Up) but never said it was gear. Answered 2026-11-15: what a
shield adds — "in incresses armor stats" — and whether it wears down and breaks the way a
weapon or armour does — "A just like all other gear". The user didn't give the figures,
so they're placeholders, kept in the game's tuning file with the others. Whatever shield
is equipped, the Tank's art keeps the shield it's drawn with; that's in `Look and Feel.md`,
"Gear and the art". The game is built as the "For now" paragraph says, and each part of
it is a default the build chose, not yet the user's word. Whether a type other than the
Tank can carry a shield, whether a Tank with no shield can still use Shields Up, what
wears a shield down, whether shields have classes, how a Brute's hit treats a shield, who
repairs one on a dive, and whether the four share one picture are proposed as questions
in "Questions on shields and potions". Shields Up's figure leaving the shield out is the
user's going-ahead default, 2026-11-24.

## Change: A broken shield adds nothing, and a working one outlasts broken armour

> Proposed 2026-11-16 · for review

**Where:** `## Durability`, the paragraph "Broken armour means the member's defence falls
back to Constitution alone."

**Now says:**

```
Broken armour means the member's defence falls back to Constitution alone.
```

**Proposed:**

```
Broken armour means the member's defence falls back to Constitution alone, plus a Tank's
shield if it carries one that hasn't broken. A broken shield adds nothing either, so a
Tank whose armour and shield have both broken is down to Constitution alone.
```

**Why:** Follows "The Tank carries a shield, and shields can be swapped": answered
2026-11-15, a shield adds defence on top of the Tank's armour and wears down and breaks
just like all other gear, and `## Durability` already says broken gear contributes
nothing. As written, a Tank whose armour breaks would lose its working shield's defence
too.

## Change: For now the only potion is a healing potion, bought at the shop

> Proposed 2026-11-14 · for review

**Where:** `## What a Member Carries`, last paragraph (a new paragraph after it)

**Now says:**

```
The weapon the Rogue carries adds less damage than the Fighter's. The Brute wears tanned
hide, which adds a little defence on top of its Constitution — less than a properly
armoured type has.
```

**Proposed:**

```
The weapon the Rogue carries adds less damage than the Fighter's. The Brute wears tanned
hide, which adds a little defence on top of its Constitution — less than a properly
armoured type has.

For now the only potion is a healing potion, and the shop sells it. A healing potion
costs 20 gold, a placeholder to be balanced later, and goes into the guild's stores. A
potion can't be sold back to the shop. Every potion the shop sells is F rank, and for now
each one heals the same 18 health points, a placeholder inside the F band of 10 to 25;
no potion rolls an amount of its own.
```

**Why:** Answered 2026-11-14: "only healing potions for now". The originals say how a
healing potion goes into a dive, how a member drinks one and how much it heals, but not
where a guild gets one before it holds an Alchemist, who unlocks at guild rank D; for now
the shop sells them. The price is kept in the game's tuning file with the other
placeholders. Selling one back is a default the build chose, not yet the user's word, and
it's proposed as a question in "Questions on shields and potions". The shop selling F
rank, and every shop potion healing a fixed 18, are the user's going-ahead defaults,
2026-11-18: "every shop potion heals a fixed 18, a placeholder in the tuning file". The
Alchemist's bands set a potion's heal by its rank, and the Alchemist's Intelligence and
Luck place it inside its band; with no Alchemist, nothing places a shop potion, so every
one heals the same, inside the F band.

## Change: A member's gear can't change during a dive, for now

> Proposed 2026-11-16 · for review

**Where:** `## Assignment`, the paragraph beginning "Nothing stops the player giving a
member gear" (a new paragraph after it)

**Now says:**

```
Nothing stops the player giving a member gear of a higher class than the member's own
rank — a C-class piece on an F-rank diver is allowed.
```

**Proposed:**

```
Nothing stops the player giving a member gear of a higher class than the member's own
rank — a C-class piece on an F-rank diver is allowed.

For now a member's gear — weapon, armour and shield — can't be put on or taken off from
the moment the party goes into a dive until that dive ends, even while the player has
stepped back out to the guild hall. A member away on a mission can still have their gear
put on and taken off, since a mission's outcome is fixed when it's sent and never reads
gear.
```

**Why:** The game is built this way. Nothing says whether gear can change partway
through a dive; it's a default the build chose, not yet the user's word. A member on a
dive that hasn't ended can't be dismissed either; that's in Core Concept's change "A
member on a dive can't be dismissed, for now".

## Change: Questions on shields and potions

> Proposed 2026-11-14 · for review

**Where:** `## Open Questions`, at the end of the list, after the two entries that "Two
questions on stores and condition" adds

**Now says:**

```
- Crafting a piece and fixing a broken one both take materials, which come as ores or
  herbs — the Dungeon doc covers where they come from — and it isn't said how much of
  either goes into which.
```

**Proposed:**

```
- Crafting a piece and fixing a broken one both take materials, which come as ores or
  herbs — the Dungeon doc covers where they come from — and it isn't said how much of
  either goes into which.
- Can a type other than the Tank carry a shield?
- When a Tank has no shield equipped, can it still use Shields Up?
- What wears a Tank's shield down — every time the Tank is hit, the same as armour; only
  when the Tank uses Shields Up; or both?
- Do shields come in quality classes with rolled numbers, the way weapons and armour do,
  or is every shield the same apart from its picture?
- When a Brute hits the Tank, should it halve the Tank's whole defence, armour and shield
  together, or ignore the shield's part completely and leave the armour's part whole?
- On a dive, who fixes a Tank's shield in the field — the Armourer, the Blacksmith, or
  nobody, so shields are only repaired back at the guild hall?
- Should all four shields share the one shield picture the game carries, or does each get
  its own — and if so, where do the other three come from?
- If a member comes home without drinking their potion, does it go back to the stores?
- In the guild hall, does a member's potion behave like their gear — taken back in the
  Dorms, left as it is while they're away on a mission, and back to the stores when
  they're dismissed?
- When a member dies in the dungeon still holding their potion, does it come home the
  way their gear does, and is it lost if the whole party falls?
- Can a potion be sold back to the shop?
- While a dive hasn't ended, can the player give a potion to, or take one from, a member
  who is on it?
```

**Why:** None of the docs answers these, and the answers on shields and potions leave them
open. The game is built with a default for now on selling a potion back, in "For now the
only potion is a healing potion, bought at the shop", and on each shield question: only
the Tank carries a shield; a Tank with no shield equipped can still use Shields Up; a
shield spends a use on every hit the Tank takes, wherever armour spends one, and Shields
Up spends none of it; shields have classes and rolled numbers, built the way armour is; a
Brute's hit quarters the Tank's whole defence, shield included; nobody repairs a shield on a
dive, because field repair isn't built yet; and all four shields wear the one shield
picture the game carries, with the other three named on the game's missing-art list. On
potions the default is that no member holds one in the guild hall: potions wait in the
stores and are packed only at the start of a raid, so there's no handing one over or
taking it back, on a dive or off it, and every undrunk potion goes back to the stores
when the raid ends, a dead member's too, unless the whole party fell. That's in The
Dungeon's change "Healing potions are packed at the start of a raid and come back at its
end, for now". The existing entries, and the pending changes to this list above, are
unchanged.

## Change: A span is counted in whole figures, ends included

> Proposed 2026-11-24 · for review

**Where:** `## Quality`, the paragraph beginning "A weapon carries two attributes"

**Now says:**

```
A weapon carries two attributes: an Attack Damage range and a Durability. Each kind of
weapon has its own Attack Damage range, and so does each class — the ranges differ per
kind so the damage comes out balanced across the combat types. But a weapon's range is not
a fixed figure for its kind and class: each kind at each class has a wider band, and an
individual piece's own range is drawn from inside that band when the piece is made, so two
pieces of the same kind and class are not the same. The span itself is rolled too, not
just where it sits in the band — one piece's range can come out wider or narrower than
another's, not only higher or lower within it. A span is never narrower than a quarter
of its band and never wider than half of it, so no piece comes out as a single flat
figure and none spans its whole band.
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
another's, not only higher or lower within it. A span is never narrower than a quarter
of its band and never wider than half of it, so no piece comes out as a single flat
figure and none spans its whole band. A span and a band are both measured by how many
whole figures they cover, ends included: 2–4 covers three, and the knife's F-class band
of 2–12 covers eleven, so an F-class knife's range covers from three figures, like 2–4,
to five, like 2–6.
```

**Why:** The game is built this way, the user's going-ahead default, 2026-11-24. "A
quarter of its band" doesn't say how a span is measured. Measured as the gap between its
ends, 2–4 is 2 against the knife band's 10, under a quarter, so this doc's own example
of an F knife coming out 2–4 or 10–12 would break the rule; counted in whole figures,
ends included, it holds. Armour's range is measured the same way, and so is a shield's,
built the way armour is.
