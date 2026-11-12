# PRD: Combat Engine Core

> **Status:** Draft · Source docs read: `Combat.md`, `Guild Members.md`, `Individual Types.md`,
> `Equipment.md`, `The Dungeon.md`, `Specialists.md`, `Core Concept.md`; change notes
> `EhrensDocs/Combat.md`, `EhrensDocs/Guild Members.md`, `EhrensDocs/Equipment.md`,
> `EhrensDocs/The Dungeon.md`, `EhrensDocs/Core Concept.md`, `EhrensDocs/Platform.md`; code under
> `src/guildmasters-descent/Assets/Scripts/Core`. Where a change note and its original disagree,
> the change note is used.

## Problem

Divers, gear and health exist in the guild model, but nothing can fight. Every battle on a
dive, the battle screen, and the six combat types all need one set of rules underneath them
for who acts, whether a strike lands, how much it does, what wears out, and who gets hit.

## Goal

A pure-C# engine in the game-core assembly, with no screen, runs one battle between the party
and a group of monsters on two 5-by-3 grids: Dexterity turn order, per-strike hit and damage
from stat plus gear, Luck evasion, area attacks, gear wearing and breaking mid-attack, the
support ring, the type-advantage multiplier, monster targeting with taunt, and special bars
with base charge. It builds on the existing `Member`, `GearPiece`, `StatWeighting`, `IRng` and
`Tuning` types rather than beside them. A combat type plugs in its attacks, special and bonus
charge through a contract the engine defines, so the later types item adds the six types
without changing the engine. Every roll is reproducible from an injected RNG.

## Requirements

### Combatants

1. Each side stands on its own grid of 5 columns by 3 rows, one combatant per node. A
   specialist holds a node like anyone else and can be attacked there. (`Combat.md` §Formation)
2. A member enters a battle at its `CurrentHealth`, not its `MaxHealth`, and leaves it with
   whatever health it ended on, written back to the `Member`. (`EhrensDocs/Combat.md`, "Members
   stay hurt from battle to battle")
3. A combatant that reaches 0 health dies on the spot: it takes no further turn, cannot be
   targeted, and gives no help. The battle result names every member who died. Taking the
   member off the roster and bringing their gear home are the dive's job.
   (`EhrensDocs/Combat.md`, same change; `The Dungeon.md` §The Dungeon)
4. A monster has one of the six combat types (never a specialist type), a level, and no gear.
   Its stats follow the member rules: the type's starting stats (`Tuning.StartingStatsF`), then
   one weighted level-up per level above 1, drawn through `StatWeighting.Pick` and the injected
   RNG. Its damage, defence, health and access to the ring, bar and taunt follow defaults D1–D3
   under Open Questions. (`EhrensDocs/The Dungeon.md`, "The dungeon's enemies are monsters")

### Turn order

5. Turn order is by Dexterity, highest first, with members and monsters in one shared order.
   (`Combat.md` §Combat; `Guild Members.md` §Base Stats) Rounds and reordering follow default
   D4 under Open Questions.

### Resolving a strike

6. A combatant's damage stat is whichever of Strength, Dexterity and Intelligence comes first
   in its type's `StatWeighting` order: Strength for Brute, Tank, Fighter and Porter; Dexterity
   for Rogue, Archer and Cook; Intelligence for Mage. A specialist's damage works the same way.
   (`Guild Members.md` §Base Stats, §Stat Weighting by Type; `Combat.md` §Combat)
7. A strike's attack is the damage stat (with help, req 17) plus a fresh roll inside the
   weapon's own `MinRange`–`MaxRange`, inclusive. A broken weapon, an empty weapon slot, a
   specialist or a monster adds nothing. (`Equipment.md` §Quality, §Durability; `Guild
   Members.md` §Base Stats — "damage is the stat plus what you carry")
8. Defence against a strike is Constitution (with help, when Constitution is the defender's
   primary stat) plus a fresh roll inside the armour's Defence range. Broken armour, an empty
   armour slot, a specialist or a monster adds nothing. (`Equipment.md` §Quality, §Durability,
   §Assignment; `Specialists.md` §Equipment)
9. Damage dealt is attack minus defence, never below 0, with no minimum — enough defence
   stops a hit completely. (`Guild Members.md` §Base Stats) The type multiplier applies after
   the subtraction, per default D5.
10. Each strike of a multi-strike attack resolves on its own — its own hit roll, weapon roll,
    defence roll and wear. (`Combat.md` §Combat; `Equipment.md` §Quality)
11. A strike that is not part of an area attack can miss. The chance to miss comes from the
    target's Luck. A miss deals nothing and wears nothing. (`Guild Members.md` §Base Stats;
    `Equipment.md` §Quality) The formula is default P1.
12. Whether an attack is an area attack is a property the attack declares, not a count of its
    targets: the Brute's cleave hits three enemies and each can evade it, while the Archer's
    Volley and the Mage's column attack are area attacks. An area strike never rolls to hit
    and ignores evasion, and the defence against it is multiplied by a placeholder factor below
    1. (`Guild Members.md` §Base Stats; `Individual Types.md` §The Brute, §The Archer, §The Mage)

### Gear wear

13. A weapon spends one durability for each hit it lands; armour spends one for each hit it
    takes; a miss spends none. A hit that defence reduces to 0 damage still landed, and still
    spends. (`Equipment.md` §Quality)
14. The strike that spends a piece's last use still counts that piece in full — it "works
    fully until it reaches zero". Every strike after it, later in the same attack or in any
    later battle of the dive, gets nothing from it. Wear is applied to the guild's own
    `GearPiece` (`GearPiece.Use`), so it carries into the next battle. (`Equipment.md`
    §Durability, §Repair; `Combat.md` §Equipment Durability)

### Type advantage

15. When the attacker's type has advantage over the target's, the strike's damage is
    multiplied by a placeholder above 1. Only the advantaged direction changes; there is no
    penalty the other way, no advantage across the two triangles, and none to or from a
    specialist. Monster types count exactly as members' do. (`Guild Members.md` §Combat Types;
    `EhrensDocs/The Dungeon.md`, "monsters") How it combines with defence, and with the
    Brute's bypass on a Tank, is default D5.

### Support ring

16. Help runs one way along the ring — Tank→Archer, Archer→Fighter, Fighter→Mage, Mage→Brute,
    Brute→Rogue, Rogue→Tank — between two living combatants on the same side whose nodes
    touch, diagonals included. It is many-to-many. Specialists neither give nor receive it.
    (`Guild Members.md` §The Support Ring)
17. The first help a combatant receives is 5%, each further help 49% of the one before
    (2.45%, then 1.2005%, …), added to the receiver's primary stat — the first stat in its
    `StatWeighting` order. So a Tank's help raises its Constitution, and so its defence, not
    its damage. The first help comes to at least one point; later helps are exact, so at low
    stats they can come to nothing. These two percentages are settled numbers, not
    placeholders. (`Guild Members.md` §Diminishing Returns on Help, §Stat Weighting by Type)
    Rounding is default P2.
18. Help is read from where the combatants stand and who is alive at the moment the stat is
    used, so a death or a formation change alters it straight away. (`Guild Members.md` §The
    Support Ring; `EhrensDocs/Combat.md`, "Changing formation mid-battle is free")

### Targeting

19. A close-range attack reaches the frontmost row of the other grid that still holds a living
    combatant; a far-range attack reaches any row. (`Combat.md` §Combat)
20. A monster picks its target from what it can reach, weighted both by how much damage each
    target has dealt and by how easy it is to kill. The weights are placeholders. (`Combat.md`
    §Enemy Targeting) The details are default P4.
21. A taunt overrides that weighting: the taunted combatant's next attack goes at its taunter,
    and then the taunt is spent. Applying a taunt belongs to the Tank's attack; the engine
    holds the taunt and honours it. (`Combat.md` §Enemy Targeting; `Individual Types.md` §The
    Tank)
22. A member's default attack is chosen automatically on its turn. The caller can name one
    enemy as the party's focus target, which every member attacks. (`Combat.md` §Combat) An
    unreachable focus, or no focus, is default P5.

### Special bar

23. Every diver member has a special bar; a specialist has none. (`Combat.md` §Combat)
24. Every attack a combatant makes — once per attack, whether or not it hits — adds the same
    base charge to its bar, whatever its type. The charge and the bar's size are placeholders.
    (`Combat.md` §Combat; `Individual Types.md` Open Questions, "How fast does a special
    charge?")
25. When a member's bar is full, the caller may choose its special instead of its default
    attack on that member's turn. (`Combat.md` §Combat)

### The contract a combat type implements

26. A combat type supplies an ordinary attack, a special and a bonus-charge rule through a
    contract, and adding one changes nothing in the engine. The contract must be able to say
    each of the following, because a settled type rule depends on it (`Individual Types.md`,
    each type's section, unless noted):
    - which targets an attack hits, from what it can reach — one target, a target and its two
      neighbours, whole rows, a column, the one behind (Brute, Archer, Mage);
    - how many strikes land on each target (Fighter, Rogue);
    - whether the attack is an area attack (req 12);
    - a reduced damage share for some targets (Volley's neighbours);
    - strikes that skip the hit roll (Rogue's attacks under Vanish);
    - strikes that skip the defence subtraction (the Brute on a Tank, default D5);
    - an attacker-side accuracy and damage increase (the Archer's streak);
    - strikes that do not charge the bar, and leftover strikes that move to the nearest enemy
      still standing when a target dies (the Fighter's flurry);
    - setting a bar to a fraction of full (the Fighter's 90% refill);
    - effects lasting one shared fixed number of turns, a placeholder (`Combat.md` §Combat):
      untargetable (Vanish, which ends early when an area attack hits the Rogue and fails when
      the Rogue is the only thing an enemy can reach), extra defence on the user and allies,
      adding up across sources (Shields Up), and damage to enemies standing on given cells
      (the Mage's field);
    - applying a taunt (the Tank);
    - bonus charge from what happens in battle — being attacked, evading, hitting several
      enemies, hitting the same target twice running, allies in front in the same column
      taking hits, a kill during the flurry.

    The specialist's weak close attack plugs in through the same contract. (`Combat.md` §Combat)

### Determinism and results

27. Every random roll — hit, weapon, defence, targeting, monster level-ups, tie-breaks if any
    are random — goes through the injected `IRng`, so a battle run twice with the same scripted
    RNG plays out the same. (`Assets/Scripts/Core/Guild/IRng.cs`)
28. A finished battle reports which side won, every combatant that died, and how many monsters
    the party defeated, which the dive needs for experience. (`Guild Members.md` §Levels and
    Experience; `EhrensDocs/Combat.md`, "Members stay hurt")
29. Every new number is a `[Placeholder]` field in `Tuning.cs`, listed by
    `Tuning.ListPlaceholders()`. (`Assets/Scripts/Core/Tuning/Tuning.cs`; `queue/focus.md`
    Goal, "Missing details")

## Out of Scope

- Each of the six types' attack shapes, specials and bonus-charge conditions, and the
  specialist's weak attack — the later types item. That includes what an ordinary multi-strike
  attack does with strikes left over when its target dies; only the flurry's is settled.
- The battle screen: highlighting, input, showing hits and deaths, moving members mid-battle.
- The dive: healing after a battle or at a rest area, field repair, removing the dead from the
  roster, bringing their gear home, awarding experience, full health back in the hall, and
  which level the monsters on each floor are.
- Saving a battle in progress — `EhrensDocs/Platform.md` leaves it open.
- Health above F rank, or health growing with level — `EhrensDocs/Guild Members.md` leaves it
  open.

## Open Questions

### Defaults from the user (2026-11-11) — built as placeholders, not settled

- **D1.** A monster's damage is its damage stat alone and its defence its Constitution alone —
  no weapon or armour term.
- **D2.** A monster's health follows the same rule as a member of the same level. Today that
  is `Tuning.NewMemberHealth`, flat.
- **D3.** Monsters get the support ring, a special bar and the Tank's taunt, as members do.

### Defaults on rules still open to the user — built on, not settled

- **D4. Turn structure.** Every combatant acts exactly once per round, highest Dexterity
  first. The order is fixed at the start of each round from each combatant's own Dexterity
  (stat plus anything not from help); support-ring help never reorders the round. Open to the
  user: whether higher Dexterity should instead mean acting more often, and whether help to a
  Rogue's or Archer's Dexterity should move them in the order.
- **D5. Type advantage.** The multiplier applies to the damage left after defence is
  subtracted. A Brute striking a Tank gets both: the defence subtraction is skipped entirely
  and the multiplier applies. The docs read differently here, and this default does not
  reconcile them: `Individual Types.md` §The Brute has the Brute's advantage over the Tank as
  "bypassing the defence subtraction entirely", while `Guild Members.md` §Combat Types says a
  type advantage "is a damage multiplier". Open to the user: before or after defence, and
  whether a Brute on a Tank gets both or only one.

### Defaults proposed by this PRD — not from any doc, cheap to change

- **P1.** Misses come only from evasion: miss chance is the target's Luck times a placeholder
  percentage, capped at a placeholder. The Archer's accuracy increase lowers it.
- **P2.** Helps are summed exactly, the first raised to one point if it comes to less, and the
  total is rounded down once before it is added to the stat.
- **P3.** A multi-target attack wears the weapon once per target it hits, reading "each hit
  the weapon lands" literally.
- **P4.** "Damage dealt" counts this battle only; "easy to kill" is lowest current health; the
  choice is a weighted random draw through the RNG.
- **P5.** A member with no focus target, or whose focus it cannot reach, picks its target the
  way a monster does (req 20).
- **P6.** A taunt is spent by the taunted combatant's next attack, hit or miss. It lapses if
  the taunter dies, and is ignored while the taunter is out of reach. A newer taunt replaces
  an older one. A monster Tank's taunt overrides a member's focus target.
- **P7.** Using a special empties the bar; the special then charges it like any attack unless
  its type says otherwise, as the flurry does. A monster uses its special as soon as its bar
  is full.
- **P8.** Effect lengths count the caster's own turns.
- **P9.** Ties in Dexterity: members before monsters, then by grid position, front row first
  and left to right — so ties need no RNG.
- **P10.** Magic damage, the Mage's, meets the same defence as any other damage.
- **P11.** Within a strike the rolls are drawn in a fixed order — hit, then weapon, then
  defence — so a scripted-RNG test can drive them.

### From the design docs, still open

- "What is having a type advantage actually worth in a fight?" (`Guild Members.md`) — a
  placeholder multiplier until answered.
- "How fast does a special charge?" (`Individual Types.md`) — a placeholder charge until
  answered.
