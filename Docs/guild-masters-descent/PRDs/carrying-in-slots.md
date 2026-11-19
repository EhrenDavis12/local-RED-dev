# PRD: Carrying in Slots

> **Status:** Draft · Source docs read: The Dungeon.md, Specialists.md, Combat.md,
> Equipment.md, Guild Members.md, Core Concept.md, Individual Types.md, Battle Test.md;
> EhrensDocs change notes for The Dungeon, Specialists, Equipment, Core Concept, Combat,
> Platform, Open Questions; queue/focus.md; queue/reports/150-reconcile-18-nov.md; queue
> item #151's going-ahead defaults (user, 2026-11-18). Code read on
> `queue/151-carry-slots` (save version 12).

## Problem

What a party carries is a gold cap: 10 gold for each living member and 100 more for a Porter.
Each member holds either no healing potion or one. The player hands it over in the Dorms, and
the member keeps it from one dive to the next. The design docs now count carrying in slots
instead. Every member carries 5, a Porter more by tier, and a potion takes one slot. Potions
go into those slots at the start of a raid, not in the guild hall.

## Goal

Every member has a slot capacity set by their type and tier. Healing potions are the only
thing that fills a slot in the first version. They are packed from the stores into slots
when a dive or a played mission starts, and they come back out when it ends. Gold no longer
has a carry cap. The save holds what sits in each member's slots, and saves from version 12
and earlier load into the new shape without creating or losing a potion.

## Requirements

Requirements marked **[default]** rest on a "going ahead with" choice, not on a settled doc.
Each one names the Open Question it hangs on.

### Capacity

1. Every member carries 5 slots, whatever their type, rank or tier: divers, the Cook and the
   Porter's base alike. — The Dungeon.md `## The Dungeon`, ¶3
2. A Porter carries 5 slots plus 5 for each tier reached: Novice 10, Apprentice 15, and so
   on up to 50 at Grandmaster SSS. A promotion raises the capacity straight away.
   — Specialists.md `## The Porter`
3. A member never holds more potions than their capacity. A member's **free slots** are
   their capacity minus the potions they hold. This is the figure #155 will read, so the
   game works it out in one place. — The Dungeon.md `## The Dungeon`, ¶3

### What takes a slot

4. A healing potion takes 1 slot. — The Dungeon.md `## The Dungeon`, ¶3
5. Gold takes no slots, and how much gold a dive brings home no longer depends on who came
   along. The two gold-carry placeholders (10 a member, 100 a Porter) leave the tuning file.
   — user default, queue #151 ("gold takes no slots")
6. Two gold losses stay as they are today. Turning back between rest areas loses the gold
   found since the last rest area. A party with no one left alive brings no gold out.
   — The Dungeon.md `## The Dungeon`, ¶2; EhrensDocs/The Dungeon.md, change "A party can
   turn back anywhere…" ("Only the living carry")
7. No item of loot exists in the first version, so nothing but potions fills a slot yet.
   — EhrensDocs/The Dungeon.md, change "For now a dive yields only gold"

### Packing at the start of a raid

8. Potions move from the stores into members' slots at the start of a raid. That happens
   when a dive is entered, when a dive is re-entered at a rest area, and when a mission is
   played as a battle. — The Dungeon.md `## Entering the Dungeon`, last ¶; user default,
   queue #151 ("a played mission packs potions the same way a dive does")
9. **[default — Open Question 1]** Until #156 lets the player choose, the start of a raid
   packs one potion for each member from the stores, in the order the party was picked,
   for as long as the stores last. A party with too few potions still goes in, and members
   later in the order go without.
10. A raid that is refused packs nothing and leaves the stores count unchanged. That covers
    an unpaid fee, an invalid party, a missing re-entry point, and a refused play.
    — EhrensDocs/Core Concept.md, change "A mission can be played…" ("a refused play
    changes nothing"); `Dive.TryBegin`'s existing contract ("Refused, changing nothing")
11. A mission that is sent rather than played packs nothing. — user default, queue #151
    (which covers played missions only); EhrensDocs/Core Concept.md, change "A mission can
    be played…" (a sent mission never fights)
12. **[default — Open Questions 1 and 2]** The Dorms potion hand-out (give and take back)
    is removed. No member holds a potion in the guild hall. — user default, queue #151
    ("that per-member potion goes away with slots")

### During the raid

13. A member drinks only from the potions in their own slots. Each drink uses exactly one.
    One member's potions never reach another member. — user default, queue #151
14. This PRD does not change when a member drinks or how much a potion heals. The drink
    rule in the game today stays as it is until #152, #157 and #158 replace it, and it
    takes each drink from the drinker's own slots. A member who still holds a potion after
    drinking can drink again on a later hit that meets that rule. — scope of queue #151
    (brief)

### End of the raid

15. **[default — Open Question 2]** When a dive ends, each surviving member's undrunk
    potions go back to the stores. This applies to going home and to turning back.
16. **[default — Open Question 3]** A member who died on the dive has their undrunk potions
    go back to the stores. If the whole party fell, every potion packed for that dive is
    lost. This is the code's behaviour today, extended to more than one potion.
    — `Dive.End`
17. When a played mission ends, however it ends, every member's undrunk potions go back to
    the stores. Potions drunk in it stay gone. — EhrensDocs/Core Concept.md, change "A
    mission can be played…" ("a member drinks their potion as in any battle, and both stay
    that way after the mission"); Open Question 2 for the return
18. If the game closes partway through a played mission, the next load finds that
    mission's undrunk potions back in the stores and its drunk ones gone. — EhrensDocs/Core
    Concept.md (the played battle isn't saved); EhrensDocs/Platform.md `## Saving` ("Nor
    does it give back a potion")

### Save and migration

19. The save format goes from version 12 to 13. A version 13 save holds two things: the
    potions in the stores, and how many potions are in each member's slots. A dive saved
    partway reopens with every member holding exactly what they held when it was saved.
    — EhrensDocs/Platform.md `## Saving`
20. Loading a save from version 9 to 12 works like this:
    - A member on the saved dive who held the old single potion loads with 1 potion in
      their slots.
    - **[default — Open Question 2]** A member who is not on a saved dive and held one has
      it moved to the stores.
    - Stores plus slots add up to the same total before and after the load.
    - None of this is reported as a repair, because the save simply predates slots.
    — EhrensDocs/Platform.md `## Saving` ("A save made by an older version still loads")
21. A save from before version 9 still loads with no potions in the stores and none on any
    member. — EhrensDocs/Platform.md `## Saving`
22. A version 13 save that holds an impossible count is fixed as it loads, never refused,
    and each fix is reported:
    - A member's count below zero becomes none.
    - A count above that member's capacity puts the extra potions into the stores.
    - A stores count below zero becomes none, as it does today.

    Potions in the slots of a member who is not on a saved dive go back to the stores, and
    this one is not reported. A played mission that was cut off leaves the save that way
    legitimately (requirement 18). — EhrensDocs/Platform.md `## Saving`, "For now" list
    (the fix-as-it-loads pattern)

## Out of Scope

- Healing potion heal bands by rank: #152.
- A fallen member's gear coming home only if there are free slots: #155. Until then a dead
  member's gear still comes home free (EhrensDocs/Equipment.md, change "A dead member's gear
  comes home, for now"), and gear takes no slots.
- The player choosing which potions to pack on the party-planning screen: #156. Requirement
  9 is the stand-in it replaces.
- A drink button on each member card: #157. Full-auto drinking below 30%: #158.
- The Herbalist and the Miner, and slots restricted to one kind of yield. Neither type
  exists in the game, and the Focus leaves "the other six specialists" out of the first
  version. Capacity is set per type and tier (requirement 1), and that is where they slot
  in later.
- Items of loot taking slots, because the first version has no item loot. Buff potions too.
- Showing slots or capacity on any screen, beyond removing the Dorms hand-out.

## Open Questions

1. *(Proposal, mine. No doc settles it.)* Until the party-planning screen lets the player
   choose, how many potions does a raid pack for each member? The build defaults to one
   each, in pick order, while the stores last.
2. "If a member comes home without drinking their potion, does it go back to the stores?"
   — EhrensDocs/Equipment.md, "Questions on shields and potions". The build defaults to yes,
   so no potion sits in a member's slots outside a raid.
3. "When a member dies in the dungeon still holding their potion, does it come home the way
   their gear does, and is it lost if the whole party falls?" — EhrensDocs/Equipment.md,
   "Questions on shields and potions". The build defaults to today's code: it comes home,
   unless the whole party fell.
4. "While a dive hasn't ended, can the player give a potion to, or take one from, a member
   who is on it?" — EhrensDocs/Equipment.md, "Questions on shields and potions". With the
   hand-out removed, the build has no way to do either.
5. "Do potions and loot compete for slots during the dive, or only on the way out?"
   — queue/reports/150-reconcile-18-nov.md. This doesn't come up until item loot exists.
