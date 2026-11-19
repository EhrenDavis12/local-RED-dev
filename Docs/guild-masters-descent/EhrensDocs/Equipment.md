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

For now, though, loot is just gold. In the first version a dive or a mission yields gold and nothing
else — no materials, no items, and no dropped gear.
```

**Why:** Answered: for now loot will just be gold. Both paragraphs have the dungeon
dropping gear and yielding materials or items, which the first version doesn't do; they
stay as the longer-term design, and the new paragraph scopes the first version. Missions
are held to gold too, for now: that's a default the build chose, not yet the user's word,
and it's proposed as a question in Core Concept's change "Questions on missions'
defaults".

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

For now, though, a dead member's gear always comes home when the party walks out, however
full the party's slots are, and goes back to the stores, held by no one. If a battle
leaves no one in the party alive, every piece the party took in is lost.
```

**Why:** The dive is built this way. The party's carrying capacity is counted in slots
(`The Dungeon.md`, `## The Dungeon`), and nothing says how many slots a dead member's
gear takes, so for now it takes none; that question is proposed in The Dungeon's changes.
The original didn't say what happens to the gear when no one comes back.

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

## Change: The Brute carries axes and the Tank warhammers

> Proposed 2026-11-14 · for review

**Where:** `## What a Member Carries`, the list of the six weapon kinds

**Now says:**

```
- Fighter — two-handed swords, and only two-handed swords
- Brute — clubs
- Tank — short swords
- Archer — bows
- Mage — staffs
- Rogue — knives
```

**Proposed:**

```
- Fighter — two-handed swords, and only two-handed swords
- Brute — axes
- Tank — warhammers
- Archer — bows
- Mage — staffs
- Rogue — knives
```

**Why:** Answered 2026-11-14: the weapons follow the character art that's already drawn —
the Brute swings an axe and the Tank holds a warhammer. The user: "the tank now has a
Warhammer just just make it so cause the animations to redo is painful". Only the names
change. Each band in `## Quality` stays as it is, because a band is set by how a kind's
strikes land, and the axe cleaves the way the club did. The next two changes rename the
kinds in Quality's band lists.

## Change: The Attack Damage bands name the axe and the warhammer

> Proposed 2026-11-14 · for review

**Where:** `## Quality`, the list after "Each kind's F-class Attack Damage band, in
ascending order:"

**Now says:**

```
- Knife, the Rogue's — 2–12
- Staff, the Mage's — 3–15
- Two-handed sword, the Fighter's — 4–16
- Club, the Brute's — 4–18
- Short sword, the Tank's — 5–21
- Bow, the Archer's — 6–26
```

**Proposed:**

```
- Knife, the Rogue's — 2–12
- Staff, the Mage's — 3–15
- Two-handed sword, the Fighter's — 4–16
- Axe, the Brute's — 4–18
- Warhammer, the Tank's — 5–21
- Bow, the Archer's — 6–26
```

**Why:** Follows "The Brute carries axes and the Tank warhammers". The bands are
unchanged.

## Change: The Durability bands name the axe and the warhammer

> Proposed 2026-11-14 · for review

**Where:** `## Quality`, the list after "Each kind's F-class Durability band, grouped by
how many hits it lands in one attack:"

**Now says:**

```
- Bow, the Archer's, and short sword, the Tank's — 40–80. One strike on one target, so
  one hit an attack.
- Knife, the Rogue's, and two-handed sword, the Fighter's — 80–160. Two strikes, so two
  hits an attack.
- Club, the Brute's, and staff, the Mage's — 120–240. One strike, but it lands on three,
  so three hits an attack.
```

**Proposed:**

```
- Bow, the Archer's, and warhammer, the Tank's — 40–80. One strike on one target, so one
  hit an attack.
- Knife, the Rogue's, and two-handed sword, the Fighter's — 80–160. Two strikes, so two
  hits an attack.
- Axe, the Brute's, and staff, the Mage's — 120–240. One strike, but it lands on three,
  so three hits an attack.
```

**Why:** Follows "The Brute carries axes and the Tank warhammers". The bands are
unchanged.

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
armour's, and it counts as part of the Tank's defence wherever defence is used — a
Brute's hit halves the whole of it, shield and armour together. It spends one use on
every hit that lands on the Tank, wherever the armour spends one, and Shields Up spends
none of it.
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
in "Questions on shields and potions".

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
- Does the Armourer have a station of its own the way the Blacksmith has the smithy,
  deciding which of two Armourers sets armour quality?
```

**Proposed:**

```
- Does the Armourer have a station of its own the way the Blacksmith has the smithy,
  deciding which of two Armourers sets armour quality?
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
Brute's hit halves the Tank's whole defence, shield included; nobody repairs a shield on a
dive, because field repair isn't built yet; and all four shields wear the one shield
picture the game carries, with the other three named on the game's missing-art list. On
potions the default is that no member holds one in the guild hall: potions wait in the
stores and are packed only at the start of a raid, so there's no handing one over or
taking it back, on a dive or off it, and every undrunk potion goes back to the stores
when the raid ends, a dead member's too, unless the whole party fell. That's in The
Dungeon's change "Healing potions are packed at the start of a raid and come back at its
end, for now". The existing entries, and the pending changes to this list above, are
unchanged.
