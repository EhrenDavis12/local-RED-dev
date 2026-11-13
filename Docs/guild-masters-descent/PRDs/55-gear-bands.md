# PRD: Gear and durability bands, doubling each class

> **Status:** Draft · Queue item #55 · Source docs read: Equipment.md, Combat.md,
> Specialists.md, Guild Members.md, Individual Types.md, Core Concept.md, The Dungeon.md,
> and every EhrensDocs change note (none touches the bands; the originals win where they
> differ)

## Problem

Gear is rolled from bands that only exist at class F, and all but one of them are
placeholders: only the knife's Attack Damage band matches the Equipment doc. Every other
weapon's damage band, every armour's Defence band, and every durability band are numbers
that were made up before the doc settled them. No piece of any class above F can be made at
all.

## Goal

Every weapon and armour, at every class from F to SSS, is rolled from the bands
`Equipment.md` settles: the F-class damage and defence bands doubled once per class above F,
and the durability bands, which are the same at every class.

## Requirements

**Bands**

1. At class F, each weapon kind's Attack Damage band is the one listed for it in
   `Equipment.md` › Quality ("Each kind's F-class Attack Damage band"). The knife's already
   matches; the other five replace the placeholders.
2. At class F, each armour kind's Defence band is the one listed for it in `Equipment.md` ›
   Quality ("Each kind's F-class Defence band").
3. Above F, a kind's damage or defence band is its F-class band with **both ends** doubled
   once per rung above F — E is ×2, D ×4, up to SSS at ×256. Check values from the doc: knife
   E 4–24, knife SSS 512–3072. The same rule applies to armour. *(Equipment.md › Quality,
   "Each class doubles the band below it"; for armour, "The ladder is the same as the
   weapons'".)*
4. Bands exist for all nine classes; nothing that asks for a band refuses a class for being
   above F. *(Equipment.md › Quality.)*
5. Each weapon kind's Durability band is the one listed for its hit group in `Equipment.md` ›
   Quality ("Each kind's F-class Durability band"), and is **the same at every class** — it
   does not double. *(Equipment.md › Quality, "Unlike the damage bands, a kind's Durability
   band is the same at every class".)*
6. Every armour kind's Durability band is 60–120, at every class. *(Equipment.md › Quality,
   "Armour's Durability band is the same for every kind" and "the same band at F as at
   SSS".)*
7. These figures are settled, so they are no longer `[Placeholder]` entries and no longer
   appear in the placeholder list shown to the user. *(Equipment.md status line: the bands
   "are settled"; `Tuning.cs` holds placeholders only, by its own header.)*

**Rolling and creating pieces**

8. A piece is rolled from the band for its own kind and class, by the existing roll: the
   span width is still rolled between the placeholder narrowest and widest widths (clamped to
   the band), then its position inside the band; durability is rolled from the durability
   band. The width rule is not changed by this PRD; see Open Questions. *(Equipment.md ›
   Quality; the width rule is open there.)*
9. The guild can now create a piece of any class into the stores — the refusal for classes
   above F goes. *(Follows from 4; Equipment.md › Assignment allows "a C-class piece on an
   F-rank diver".)*
10. The shop still offers class F only. Its gate becomes the price table (which only has
    class F), not band availability, so lifting requirement 4 does not open the shop above
    F. *(Equipment.md › Quality, "baseline rises with guild rank" — the higher baselines and
    their prices are not settled, so the shop is unchanged.)*

**Existing saves**

11. A piece already in a save keeps the range and durability it was rolled with, even where
    that now lies outside its kind's new band. Loading neither re-rolls nor rejects it.
    *(Equipment.md › Quality, "rolled once, at creation, and fixed for the life of that
    piece".)*

**Wear (already built — keep covered)**

12. A special spends none of the attacker's weapon durability; armour spends one use per hit
    taken from any attack, special or not. No code change; the tests for this stay green.
    *(Equipment.md › Durability, "A special spends none of the attacker's own weapon
    durability".)*

## Out of Scope

- The shop's baseline above class F and prices for any class but F.
- How a crafter's Luck enters the roll, and crafted or dropped gear in general.
- Any change to the span-width rule.
- Repair cost, which stays a flat price by condition.
- What the Dorms or Shop shows of a piece.
- Rebalancing combat or the dungeon for the larger damage and defence figures.

## Open Questions

- How narrow or wide can a rolled span be — can a piece come out with a single figure
  rather than a range, or with a span as wide as the whole band? *(Equipment.md › Open
  Questions.)*
- *Proposed by the PRD author, not from the docs:* the current width rule caps a span at 4
  points at every class. That is a fair spread on an F-class knife (2–12) but almost a single
  figure on an SSS knife (512–3072). Should the widest width scale with class — doubling
  like the bands — or stay fixed? Until answered, it stays fixed at every class.
