# PRD: Loot drops — materials and items from enemies

> **Status:** Draft, queue item #194. Buildable: Open Questions 1 to 3 and 9 run on
> going-ahead defaults, each a placeholder waiting on the user's word and cheap to
> change. · Source docs read: `The Dungeon.md`, `Equipment.md`,
> `Core Concept.md`, `Specialists.md`, `Guild Members.md`, `Individual Types.md`,
> `Combat.md`, `Battle Test.md`; `EhrensDocs/` The Dungeon, Equipment, Core Concept,
> Platform, Look and Feel, Open Questions; queue reports 184 and 198; queue item #27's
> answers. Code read on `src/guildmasters-descent` (`Dive.cs`, `Member.cs`,
> `Guild.Potions.cs`, `SaveFile.cs`, `ResultSpec.cs`, `Tuning.cs`).

## Problem

A dive pays gold and nothing else. That is the first-version cut in EhrensDocs (The
Dungeon and Equipment, "For now a dive yields only gold"), and this job lifts it. With
no materials in the game, repairing broken gear for gold and materials (#195) has
nothing to spend. And a member's slots hold nothing but potions and a fallen member's
gear, so the original's choice of "how many potions to pay for in treasure" never comes
up.

## Goal

When a party clears a floor, about one enemy in four on it drops materials (ore or herb)
or an item. That loot sits in the party's slots and follows the rules gold follows for
retreat and wipe. Whatever the party brings home goes into the guild's stores, and the
save keeps it. The two kinds of material exist as named things #195 can spend.

## Requirements

### What drops

1. **The drop roll.** Every enemy on a cleared floor gets its own chance to drop
   something. The chance is one in four, kept in `Tuning` as a placeholder. — *The
   Dungeon, `## The Dungeon`: "One enemy in four drops materials or an item."* The docs
   give one figure for every rank and every floor, so it doesn't change with depth.
   Rolling each enemy on its own, rather than taking exactly a quarter of the floor, is
   the build's reading (Open Question 10).
2. **Materials or an item.** A drop is materials or an item at even odds, kept in
   `Tuning` as a placeholder. — *The user's going-ahead answer on #194, 2026-11-24
   (report 198, "Going ahead with"), answering The Dungeon's `## Open Questions` (Open
   Question 4 below).*
3. **The materials that exist.** There are exactly two: **ore** and **herb**. These are
   the names #195 spends. The docs name no sub-kinds, such as one ore against another,
   so the build adds none. — *The Dungeon, `## The Dungeon`: "Materials come as ores or
   herbs"; Equipment, `## Open Questions`.* *Default pending the user's word:* each unit
   records the rank of the dungeon it came from, which is always F for now (Open
   Question 9).
4. **Ore or herb.** *Placeholder, not the docs' word:* a materials drop is ore or herb at
   even odds, kept in `Tuning` (Open Question 11).
5. **How much one drop is.** *Placeholder, not the docs' word:* a materials drop is one
   unit of its kind, and each unit takes one slot. The docs say only that "an item of
   loot" takes one slot (Open Question 11).
6. **An item is a healing potion.** *Default pending the user's word:* an item drop is
   one healing potion, the game's existing one, which heals the fixed 18 a shop potion
   heals. There is no new item type. No doc names an item a dive drops (Open Question
   3). — *The shop potion: EhrensDocs Equipment, "For now the only potion is a healing
   potion".* *Placeholder, following from requirement 12:* a dropped potion is loot
   until the party leaves. It can't be drunk on the dive it dropped on (Open Question
   13).

### When it drops

7. **Loot comes with the floor's gold.** It drops at the end of the floor, together with
   the gold, and only once every battle on the floor is won. A floor the party leaves
   by turning back, by a stand-off or by a wipe drops nothing. Rest areas have no
   battles, so they drop nothing. — *EhrensDocs The Dungeon, "A floor is a series of
   battles that scrolls right into the next": "After the last one comes victory,
   dropping loot". The user on #27, 2026-11-11: "Loot at the end of the floor. if 3
   battles on that floor then they need to beat all 3."*
8. **Saving and loading can't re-roll a drop.** The roll comes from the dive's own saved
   random stream, so loading a save can never roll a floor's drops a second time. —
   *EhrensDocs Platform, "nothing is drawn again as it loads".* *Placeholder, not the
   docs' word:* clearing the same floor on a later dive rolls its drops again. They are
   not fixed when the dungeon is made, the way its monsters are (Open Question 12).

### Carrying

9. **Slots.** A unit of materials takes one slot, and so does an item. Each costs the
   same as a potion. Gold still takes none. — *The Dungeon, `## The Dungeon`: "A potion
   takes 1 slot, and so does an item of loot"; EhrensDocs The Dungeon, "gold takes no
   slots".*
10. **No room means lost.** A drop the party has no room for is lost. There is no way to
    throw something away to make room (Open Question 5). — *The Dungeon, `## The
    Dungeon`.*
11. **What counts as room.** Room means the free slots of the members still alive,
    including a Porter's extra slots, minus the potions they still hold. A dead member's
    slots hold nothing. — *The Dungeon: a lost drop is lost "the same way a dead
    member's gear is lost"; EhrensDocs Equipment, "A dead member's gear takes a slot a
    piece, for now", which defines the room that way. EhrensDocs The Dungeon: "Only the
    living carry".*
12. **Room is counted as the party leaves.** *Default pending the user's word (Open
    Question 1):* nothing limits what the party gathers during the dive. Loot is held by
    the party as a whole, never by one member, and the room in requirement 11 is counted
    once, as the dive ends. This is the same moment a fallen member's gear is counted
    today. So a potion drunk during the dive makes room, and a member who falls leaves
    nothing of their own to sort out.
12a. **The order things come home.** *Default pending the user's word (Open Question 2):*
    the free slots go first to a fallen member's gear, in the order it comes home
    today. Loot gets what is left. *Placeholder:* when the loot doesn't all fit, it is
    kept in this order until the slots run out, and the rest is lost:
    1. healing potions
    2. ore
    3. herb

    Within one kind, a higher rank comes before a lower one; every unit is F for now
    (Open Question 14).

### The end of the dive

13. **Going home at a rest area.** Everything the party carries comes home. — *The
    Dungeon, `## The Dungeon`: retreating costs only "the loot gathered since the last
    safe floor".*
14. **Turning back between rest areas.** This covers the mid-battle Retreat and a
    stand-off. The party loses all the loot gathered since the last rest area and keeps
    what it had before it, subject to room. — *The Dungeon, `## The Dungeon`:
    "Retreating always costs the loot gathered since the last safe floor"; EhrensDocs
    The Dungeon, "A party can turn back anywhere" (the stand-off counts as turning back
    there).* See Open Question 8.
15. **A wipe.** If no one in the party is alive, all its loot is lost. — *EhrensDocs The
    Dungeon: "a party with no one left alive brings nothing out".*
16. **Into the stores.** Loot that comes home goes into the guild's stores. Ore and herb
    are counted by kind and rank. A dropped potion joins the stores' potions and is
    indistinguishable from a bought one. This job adds no cap to
    the stores (Open Question 7). — *Core Concept, `## The Economy`: the guild holds and
    sells "items and materials"; Equipment, `## Assignment`: gear "sits in the guild's
    stores".* Loot is the party's until the dive ends, the same as gold. — *EhrensDocs
    Platform: "Saving doesn't bank anything".*

### On screen

17. **The victory list.** The victory list for a cleared floor shows each kind of loot
    that dropped as its own row beside the gold. A loss shows no loot. A kind with no
    icon gets the project's missing-art stand-in: a bright yellow shape with its name
    written on it. — *EhrensDocs Look and Feel, "Victory and Defeat pop-ups"; EhrensDocs
    The Dungeon, "The dungeon's enemies are monsters" (the missing-art rule).* The
    healing potion uses its own icon, the red round flask. The rows are gold, ore, herb
    and healing potion, which fits the pop-up's five-row limit.

### Saving

18. **The save format moves to version 19.** It holds:
    - the ore and herb in the guild's stores, counted by kind and rank
    - the loot a saved dive carries, counted by kind (and rank, for materials) and
      split into what was found since the last rest area and what was found before, as
      the dive's gold already is

    Nothing in the save says which member holds what (requirement 12).

    — *EhrensDocs Platform: a dive in progress is saved, and gold "found since the last
    rest area can still be lost".*
19. **Older saves.** A version 18 or older save still loads. Its stores hold no
    materials, and a saved dive in it carries no loot. Nothing else about loading it
    changes. — *EhrensDocs Platform: "A save made by an older version still loads".*
    Impossible loot figures are handled the way that save already handles their
    neighbours. A negative count in the stores is set to none as the save loads, as the
    potion count is. A dive's loot that can't be true is refused, as the dive's gold is.
    — *EhrensDocs Platform, the potion rule; `Dive.Restore`'s gold check.*

## Out of Scope

- **Dropped weapons and armour** on the last fighting floor before a rest area and on
  the last floor. That is #200, which faces the same question of when room is counted
  (Open Question 1).
- **Repair with gold and materials.** That is #195. This job only provides the ore and
  herb it spends.
- **Selling materials or items at the shop.** *Core Concept, `## The Economy`* says the
  guild sells them, but that is a shop change and its own job.
- **Missions, played or sent.** They stay gold only. *EhrensDocs Core Concept* keeps
  this as an open question ("Should a played mission bring back items, materials or
  gear…").
- **The Herbalist's and Miner's restricted slots and their extra yield.** *Specialists*
  unlocks both at guild rank E, and ranks above F are out of the first version
  (*EhrensDocs Core Concept*). Loot goes only in regular slots.
- **Throwing loot away to make room** (Open Question 5).
- **A hall screen listing the stores' materials.** That is a [look] job, if wanted.
- **Changes to how a floor's gold is counted.** That is #199.

## Open Questions

1. *(EhrensDocs The Dungeon, "Questions on carrying")* "Do potions and loot compete for
   slots during the dive, or only on the way out?" — Going ahead with **on the way
   out** (requirement 12), pending the user's word. #200 shares this question.
2. *(Proposed by this PRD)* When the free slots at the end of a dive can't hold both,
   which comes home first: the loot, or a fallen member's gear? EhrensDocs Equipment
   says "no potion or gold is left behind to make room for gear" and says nothing about
   loot. — Going ahead with the gear first (requirement 12a), pending the user's word.
3. *(Proposed by this PRD)* What is "an item"? The Dungeon and Equipment say a dive
   yields "materials or items", but no doc names an item a dive drops. The Dungeon's
   slot paragraph counts "a potion" and "an item of loot" separately, which suggests a
   loot item is something other than a potion. — Going ahead with the healing potion
   (requirement 6), pending the user's word.
4. *(The Dungeon, `## Open Questions`)* "One enemy in four drops materials or an item,
   and nothing says how often it is one rather than the other." — Going ahead with half
   and half, the user's placeholder, 2026-11-24.
5. *(The Dungeon, `## Open Questions`)* "A drop the party has no room for is lost, which
   is the same rule a dead member's gear follows. Should a full party be able to throw
   something away to make room for a find instead?"
6. *(Equipment, `## Open Questions`)* "Crafting a piece and fixing a broken one both
   take materials, which come as ores or herbs — the Dungeon doc covers where they come
   from — and it isn't said how much of either goes into which." — #195's, recorded here
   because #195 depends on this job.
7. *(EhrensDocs Equipment, "Two questions on stores and condition")* "Are the guild's
   stores capped?"
8. *(EhrensDocs The Dungeon, "A question on what gold a retreat keeps")* "When a party
   retreats partway through a floor, does it lose only that floor's gold and carry on
   with the gold it had before the floor, or all the gold found since the last rest
   area?" — Requirement 14 follows the original's "since the last safe floor" for loot.
   If the answer for gold is "only that floor", gold and loot would follow different
   rules.
9. *(Proposed by this PRD)* Does a unit of ore or herb carry a rank, from the dungeon it
   came from, or are all ore alike? — Going ahead with each unit recording its rank
   (requirement 3), pending the user's word. Every dungeon is F in the first version, so
   play doesn't change now.
10. *(Proposed by this PRD, cheap)* Does "one enemy in four" mean each enemy rolls on
    its own, or that exactly a quarter of a floor's enemies drop? Going ahead with each
    enemy rolling on its own.
11. *(Proposed by this PRD, cheap)* How often is a materials drop ore rather than herb,
    and how much is one drop? Going ahead with even odds, and one unit taking one slot.
12. *(Proposed by this PRD, cheap)* When the same floor is cleared on a later dive, are
    its drops rolled again, or fixed when the dungeon is made, as its monsters are?
    Going ahead with rolled again.
13. *(Proposed by this PRD, cheap)* Can a healing potion that drops on a dive be drunk
    on that same dive? Going ahead with no: it is loot until the party leaves
    (requirement 6).
14. *(Proposed by this PRD, cheap)* When the loot doesn't all fit on the way out, which
    is left behind? Going ahead with potions kept first, then ore, then herb, and a
    higher rank first within a kind (requirement 12a).
