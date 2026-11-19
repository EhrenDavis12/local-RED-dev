# PRD: A Fallen Member's Gear Takes Slots

> **Status:** Draft · queue item #155, size S · Source docs read: `Equipment.md`,
> `The Dungeon.md`, `Specialists.md`, `EhrensDocs/Equipment.md`,
> `EhrensDocs/The Dungeon.md`, `EhrensDocs/Open Questions.md`,
> `queue/reports/150-reconcile-18-nov.md`; code: `Core/Dungeon/Dive.cs` (`End`),
> `Core/Guild/Member.cs` (`SlotCapacity`, `FreeSlots`), `Core/Guild/Guild.Potions.cs`,
> `Core/Tuning/Tuning.cs`

## Problem

When a member dies on a dive and the party gets out, all of the dead member's gear comes
home, however full the survivors' slots are. The original design says the gear comes back
only if there is room left in the party's carrying capacity. Carrying capacity has been
counted in slots since #151, but `Dive.End()` never asks how many are free.

## Goal

When a dive ends with someone alive, a fallen member's weapon, armour and shield come home
only while the survivors have free slots for them. Each piece takes a placeholder number of
slots from the tuning file. A piece with no room is left in the dungeon and is gone from the
guild.

## Requirements

1. **Gear comes home only into free slots.** When a dive ends with at least one member
   alive (going home from a rest area, turning back, or a stand-off), each piece a fallen
   member has equipped (weapon, armour, and a Tank's shield) comes home only if the party
   has free slots for it. A piece that comes home goes back to the stores, held by no one,
   as today. A piece that doesn't is lost, gone from the stores for good.
   *Source:* `Equipment.md` › Assignment, last paragraph ("brings their gear back if
   there's room left in the party's carrying capacity … otherwise the gear is lost");
   stores: `Equipment.md` › Assignment, first paragraph. The shield is gear:
   `EhrensDocs/Equipment.md` › "The Tank carries a shield, and shields can be swapped".
   The endings: `EhrensDocs/The Dungeon.md` › "A party can turn back anywhere…" (a
   stand-off counts as turning back).

2. **Slots per piece is a tuning placeholder, starting at 1.** How many slots one piece
   takes is a new `[Placeholder]` value in `Tuning.cs`, set to 1. A weapon, an armour and a
   shield each take that same number.
   *Source:* the slot cost isn't in any doc. `queue/reports/150-reconcile-18-nov.md` ›
   Open Questions ("#155 builds one a piece as a placeholder"). `Tuning.cs` header: every
   placeholder number lives there.

3. **Free slots are the living members' slots, minus what they still carry.** The party's
   free slots are the sum, over the members alive when the dive ends, of each one's slot
   capacity minus the slots their undrunk potions take (`Member.FreeSlots`). Count them
   before the potions go back to the stores. A Porter's extra slots count. A dead member's
   slots count for nothing, and gold takes none.
   *Source:* room "left" in the capacity: `Equipment.md` › Assignment. 5 slots a member,
   1 per potion: `The Dungeon.md` › The Dungeon, third paragraph. Porter:
   `Specialists.md` › The Porter. Only the living carry, gold takes no slots:
   `EhrensDocs/The Dungeon.md` › "A party can turn back anywhere, and gold takes no slots
   for now".

4. **Bringing gear home moves nothing else.** The survivors' potions go back to the
   stores and the gold is brought out exactly as today. No potion and no gold is left
   behind to make room for gear.
   *Source:* `EhrensDocs/The Dungeon.md` › "Healing potions are packed at the start of a
   raid and come back at its end, for now", second paragraph. Gold:
   `EhrensDocs/The Dungeon.md` › "A party can turn back anywhere…".

5. **A broken piece is gear like any other.** It takes slots and comes home on the same
   terms as a working one.
   *Source:* `Equipment.md` › Assignment ("their gear", with no exception) and › Repair
   (a broken piece is fixed back at the guild hall).

6. **A party that all fell loses everything, as today.** If no one is alive when the dive
   ends, every piece the party took in is lost, the fallen members' gear included.
   *Source:* `EhrensDocs/Equipment.md` › "A dead member's gear comes home, for now", last
   sentence. Requirement 3 gives the same result, since no one is left to carry.

## Out of Scope

- Played missions and training missions. No one dies on either
  (`The Dungeon.md` › Training Missions; `PlayedMission.End` removes no one).
- Loot items taking slots. For now a dive yields only gold
  (`EhrensDocs/Equipment.md` › "For now a dive yields only gold").
- The Herbalist's and Miner's restricted slots. They aren't built, and they hold only
  their own yield (`Specialists.md` › The Herbalist and the Miner).
- Packing potions on the planning screen (#156), and any other screen change.
- What happens to a fallen member's own potions (open question 3 below).

## Open Questions

1. **Which pieces come home first when slots run short?** No doc says.
   *Proposed default (mine, cheap to change):* fallen members in party order, the order
   the party was picked and the order potions are packed in. Each member's weapon goes
   first, then armour, then shield. Since every piece costs the same, the first piece that
   doesn't fit ends it, and that piece and everything after it are lost.

2. **When are the free slots counted: when the dive ends, or when each member falls?**
   No doc says. *Proposed default (mine, cheap to change):* when the dive ends, counting
   the members alive then and the potions they still hold. A potion drunk after a death
   therefore frees a slot for that member's gear.

3. From `EhrensDocs/Equipment.md` › "Questions on shields and potions", still open:
   "When a member dies in the dungeon still holding their potion, does it come home the
   way their gear does, and is it lost if the whole party falls?"
   *Default for this item:* unchanged. A fallen member's undrunk potions go back to the
   stores, take no slots, and don't reduce the room left for gear.

4. **Does the end of the dive tell the player which pieces were left behind?** No doc
   says. *Proposed default (mine):* no screen change in this item. The dive's end still
   shows only the count of the fallen.

5. From `EhrensDocs/Open Questions.md` › Loot and carrying, question 3, still unanswered by
   the docs' owner: "When a member dies in the dungeon, how does their gear get home?"
   (A: always comes home, free; B: each piece takes up a slot and comes home only if the
   party has a slot free for it; C: only a Porter can bring it home.) This item builds B,
   because that is how the original `Equipment.md` reads. An answer of A or C undoes it.
