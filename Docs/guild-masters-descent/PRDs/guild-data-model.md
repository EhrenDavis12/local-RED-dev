# PRD: Guild and Member Data Model

> **Status:** Draft · Source docs read: `Core Concept.md`, `Guild Members.md`, `Equipment.md`,
> `Specialists.md`, `Individual Types.md`, `Combat.md`, `The Dungeon.md`; change notes
> `EhrensDocs/Guild Members.md`, `EhrensDocs/Equipment.md`, `EhrensDocs/Combat.md`,
> `EhrensDocs/The Dungeon.md`, `EhrensDocs/Platform.md`; `queue/focus.md`;
> `queue/reports/3-member-health.md`. Queue item #31.

## Problem

Nothing in the game holds a guild yet. The recruiting board, the roster and Dorms, the shop,
the dungeon board, the save file (#32) and combat (#33/#34) all need to read and change the
same guild, members and gear. Nothing does starting stats, levelling or promotion yet either.
If the shape is guessed wrong, the fix later is a save migration.

## Goal

The core assembly has one plain-data model of an F-rank guild: its gold, its roster (up to
the roster cap), and the gear in its stores. Each member has a type, a rank or tier, a level,
XP, five stats, health and an injury state. Each gear piece has a rolled range and a
durability. The model applies the rules the docs settle: starting stats from type and rank,
the weighted stat pick on level-up, the cap at the level threshold, and the first promotion
at level 16 for gold. Randomness comes from an RNG the caller passes in, so tests can run
from a seed.

## Requirements

Numbers marked **P*n*** are placeholders, listed under Placeholders below. Numbers marked
*settled* come from the docs and are not placeholders.

### Engineering

1. The model lives in the `GuildMastersDescent.Core` assembly and references no
   `UnityEngine` assembly. The existing `CoreAssemblyTests` guard this. [queue item #31]
2. All guild, member and gear state is plain data that a serializer can round-trip. Saved
   state holds no engine objects, delegates or RNG instances. Format, versioning and save
   slots belong to #32. [queue item #31]
3. Every random outcome in this PRD comes from an RNG the caller supplies: the level-up stat
   pick (R14) and the gear rolls (R24). The same seed and the same sequence of calls give the
   same results. [queue item #31]
4. Every **P*n*** is a `[Placeholder]` field in `Assets/Scripts/Core/Tuning/Tuning.cs` and
   shows up in `Tuning.ListPlaceholders()`. *Settled* numbers stay out of `Tuning`, because
   `TuningTests` require every public static field there to carry `[Placeholder]`.
   [`queue/focus.md` § Goal, "Missing details"]

### Guild

5. A guild holds its gold, its guild rank, its roster of members and its stores of gear
   pieces. A new guild is rank F and starts with **P1** gold. Guild rank never changes in
   the MVP. [`Core Concept.md` § Guild Rank, § The Economy; `Equipment.md` § Assignment;
   `queue/focus.md` § Not included]
6. Gold never goes below zero. A spend larger than the guild's gold is refused and changes
   nothing. [`Guild Members.md` § Promotion: level and gold "both are required"]
7. The roster holds at most **P2** members at guild rank F, divers and specialists together.
   Adding a member to a full roster is refused. This cap is separate from the 15-member party
   cap, which this PRD does not handle. [`Core Concept.md` § The Recruiting Board]

### Members

8. The MVP's member types are the six combat types (Brute, Tank, Fighter, Rogue, Archer,
   Mage), which are divers, plus the Cook and the Porter, which are specialists.
   [`Guild Members.md` § Combat Types; `Specialists.md` § Recruiting; `queue/focus.md` § Goal,
   § Not included]
9. A diver has a rank on F → E → D → C → B → A → S → SS → SSS. A specialist has a tier on
   Novice → Apprentice → Journeyman → Adept → Master → Grandmaster → Grandmaster S →
   Grandmaster SS → Grandmaster SSS, and never a rank. The two ladders compare rung for rung:
   Novice sits where F sits. Both full ladders can be represented, even though the MVP only
   reaches the second rung (R18). [`Guild Members.md` § Promotion; `Specialists.md` § Tiers]
10. A member holds:
    - its type and its rank or tier
    - its level and XP
    - five integer base stats (Strength, Dexterity, Constitution, Intelligence, Luck)
    - its health
    - whether it is injured (R19)
    - if it is a diver, at most one assigned weapon and at most one assigned armour (R27)

    [`Guild Members.md` § Base Stats; `Equipment.md` § What a Member Carries;
    `Core Concept.md` § Missions]
11. A new member starts at level 1 with 0 XP, uninjured, with **P3** health.
    [`Guild Members.md` § Starting Stats; `EhrensDocs/Guild Members.md` § Every member starts
    with 10 health]
12. A new member's starting stats depend on its type and its rank or tier, and nothing else.
    No RNG is involved. The MVP only needs F and Novice: table **P4**, where every value is
    single-digit (at most 9). The model refuses to create a member at any other rank or tier,
    because an F-rank guild can only hire up to F. [`Guild Members.md` § Starting Stats;
    `Core Concept.md` § The Recruiting Board]

### Levels and experience

13. Each type orders its five stats from most to least likely to rise on a level-up. The
    orders are *settled*, for all eight MVP types, in [`Guild Members.md` § Stat Weighting by
    Type]. The chance of each stat comes from its position in that order, using weights
    **P5**. The weights strictly decrease along the order and are all above zero, so the
    lead stat is the most likely and every stat can still be picked.
    [`Guild Members.md` § Levels and Experience, § Stat Weighting by Type]
14. Each level gained raises exactly one base stat by **P6**. The stat is drawn by R13's
    weighting from the supplied RNG. Specialists level the same way divers do.
    [`Guild Members.md` § Levels and Experience]
15. XP awarded to a member adds up. The member gains a level whenever the total reaches
    **P7**, the XP needed per level. One award can give several levels, and each level gets
    its own stat pick. How much XP an award is worth is calculated by the dive, not here.
    [`Guild Members.md` § Levels and Experience]
16. A member stops gaining levels at the threshold for its next promotion. The thresholds are
    *settled*: 16 at F or Novice, 32 at E or Apprentice. XP awarded at the threshold is
    thrown away, not saved for after promotion. That includes the rest of an award that
    reaches the threshold partway through.
    [`Guild Members.md` § Promotion: "neglecting a promotion wastes the experience"]

### Promotion

17. A diver at F can be promoted to E, and a specialist at Novice to Apprentice, only when
    both hold: the member is at level 16, and the guild pays **P8** gold. If either fails, the
    promotion is refused and nothing changes. An F-rank guild can make this promotion.
    [`Guild Members.md` § Promotion; `Specialists.md` § Tiers: specialist promotion "works
    exactly the way a diver's rank up does"; `queue/focus.md` § Not included excludes only
    the ladder *past* the first promotion]
18. Promotion moves the member up one rung and resets its level to 1 and its XP to 0. Its
    stats stay as they are, and the guild's gold drops by **P8**. The MVP offers no further
    promotion: an E or Apprentice member levels up to 32 and stops there (R16).
    [`Guild Members.md` § Promotion; `queue/focus.md` § Not included]

### Injury

19. A member is either injured or not. A new injury lasts **P9** of real time. The model can
    advance an injury by a given amount of elapsed time, and the member is healed once the
    remaining time reaches zero. Reading the wall clock belongs to #32. What causes an injury
    belongs to whichever feature inflicts it.
    [`Core Concept.md` § Time, § Missions: injured members "recover on their own for free,
    though slowly"]
20. An injured member counts as unavailable for a dive or a mission.
    [`Core Concept.md` § Missions]

### Gear pieces

21. A gear piece is either a weapon or an armour. It has:
    - a kind
    - a class on the F → SSS quality ladder
    - a rolled range (min–max), which is Attack Damage for a weapon and Defence for armour
    - a maximum durability
    - a current durability

    [`Equipment.md` § Quality]
22. Each combat type has one weapon kind and one armour kind, as listed in
    [`Equipment.md` § What a Member Carries]. A kind belongs to exactly one combat type.
23. Each kind at each class has a range band and a durability band. For class F (see R24):
    - The knife's Attack Damage band is 2–12 (*settled*).
    - The other five weapon bands are **P10**.
    - The armour Defence bands are **P11**.
    - The durability bands are **P12**.

    The placeholder values must keep these orders from the docs:
    - The two-handed sword's band sits above the knife's at both ends.
    - Full armour's Defence band is above light armour's, which is above tanned hide's.
    - The two-handed sword's and the knife's durability bands are above the bow's, because a
      kind that strikes many times per attack needs more durability than one that strikes
      once.

    [`Equipment.md` § What a Member Carries, § Quality]
24. A new piece is created from a kind and a class, and rolls from the supplied RNG:
    - Its range has min ≤ max, and both ends lie inside the band.
    - Both the range's width and its position in the band are rolled, so two pieces of the
      same kind and class can differ in width as well as in level. The width lies between
      **P13** and **P14**.
    - Its maximum durability is rolled from the durability band.
    - Its current durability starts at the maximum.

    The range and the maximum durability never change after creation. The MVP has bands only
    for class F, so creating a piece at any other class is refused.
    [`Equipment.md` § Quality]
25. Current durability goes down one use at a time, and combat decides when. It never goes
    below zero. At zero the piece is broken. A broken piece stays in the stores, because it
    can be repaired later. [`Equipment.md` § Quality, § Durability, § Repair]
26. A piece's condition comes from current durability as a percentage of the maximum:
    - Good: above 50%
    - Worn: 25% to 49%
    - Ragged: 1% to 24%
    - Broken: 0%

    The condition at exactly 50% is an open question (see Open Questions).
    [`Equipment.md` § Durability]

### Stores and assignment

27. The guild owns every piece, and every piece sits in its stores. Assigning a piece links
    it to one member without taking it out of the guild's ownership. A piece is assigned to
    at most one member at a time, and can be unassigned. A piece can be assigned only:
    - to a diver, never a specialist
    - to a diver whose combat type matches the piece's kind
    - into the matching slot, at one weapon and one armour per diver

    A piece's class may be higher than the member's rank.
    [`Equipment.md` § Assignment; `Guild Members.md` § Weapons and Armour;
    `Specialists.md` § Equipment]

## Placeholders

Each placeholder goes in `Tuning.cs` with `[Placeholder]`. The values are suggestions; the
implementer may pick others that meet the constraint shown.

| # | What | Suggested value | Constraint from the docs |
|---|---|---|---|
| P1 | Starting gold for a new guild | 500 | none |
| P2 | Roster cap at guild rank F | 10 | none |
| P3 | Health of a new member | 10 | the user gave 10 and called it a placeholder |
| P4 | Starting stats at F or Novice, per type (8 × 5) | follow each type's order, e.g. 6/5/4/3/2 | single-digit |
| P5 | Level-up weight by position in the type's order | 5/4/3/2/1 | strictly decreasing, all above 0 |
| P6 | Points one level adds to the picked stat | 1 | none |
| P7 | XP needed per level (a flat value; the shape of the curve is a placeholder too) | 2 | none |
| P8 | Gold cost of the first promotion, divers and specialists alike | 200 | none |
| P9 | How long a new injury lasts | 30 minutes | none |
| P10 | Attack Damage bands at class F: two-handed sword, club, short sword, bow, staff | sword 4–14, others near the knife | sword band above the knife's |
| P11 | Defence bands at class F, all six armour kinds | full 4–8, light 2–6, hide 1–3, others 1–5 | full > light > hide |
| P12 | Durability bands at class F, all twelve kinds | bow 20–30, sword and knife 40–60 | sword and knife above bow |
| P13 | Narrowest rolled range width | 0 (a single figure) | stands until the open question on width is answered |
| P14 | Widest rolled range width | half the band | stands until the open question on width is answered |

## Out of Scope

- Saving, loading, versioning, and time passing while the game is closed (#32).
- Combat and the dive (#33/#34): damage, defence, evasion, current health in battle, how XP
  per floor is calculated, death, carry capacity, and what happens to a dead member's gear.
- Recruiting: candidates, hire cost, restocking, the rough impression, and a recruit
  arriving with gear.
- The shop's prices and stock, repairs, dismissing a member, and paying to heal faster.
  These belong to the Dorms and shop rows.
- Guild ranks above F, the six other specialists, crafting, promotion past the first,
  missions, and items or materials in the stores. [`queue/focus.md` § Not included;
  `EhrensDocs/Equipment.md` § For now a dive yields only gold]
- Bands for any class above F, and the rule that neighbouring classes' bands overlap.
- Which dungeons the guild holds, including its starting F-rank dungeon.

## Open Questions

**Blocks building one requirement:**

- R26: The condition bands are "above 50%" for Good and "25% to 49%" for Worn. At exactly
  50%, which is a piece? And between whole percentages (49.5%, 24.5%, 0.5%), is a piece in
  the band below? *(Proposal, mine: yes, the band below; and 0.5% counts as Ragged, because
  only 0 is broken.)*
- R15: XP per floor is "the number of enemies defeated by the party divided by the number of
  party members". When that doesn't divide evenly (3 enemies, 4 members), does each member
  get the fraction, or is it rounded, and which way? This decides the type of the XP field.
  *(Proposal, mine: store XP exactly, fractions included. Then any later rounding rule needs
  no save change.)*

**Notes, not blocking this PRD:**

- When a level-up uses up XP, does the leftover carry toward the next level? *(Proposal,
  mine: it carries. R15 assumes this unless told otherwise.)*
- Do two recruits of the same type and rank start with identical stats? `Guild Members.md`
  says starting stats are "set by its type and its rank or tier". The recruiting board shows
  "a rough impression of where its strengths lie — promising, unremarkable", which suggests
  they differ. R12 follows the first.
- Does a new guild start with any members or gear, or only gold?
- Can an injured member be promoted? No doc restricts it, so R17 doesn't.
- From `EhrensDocs/Guild Members.md`: does health grow with level, rank or tier? Does
  Constitution play into it? What health does a member have back in the hall?
- From `Equipment.md`: "How narrow or wide can a rolled span be — can a piece come out with a
  single figure rather than a range, or with a span as wide as the whole band?" The answer
  sets P13 and P14.
- Are the guild's stores capped?
