# PRD: Healing potions by rank, drunk instead of attacking

> **Status:** Draft, queue item #152 · Source docs read: Combat.md, Specialists.md,
> The Dungeon.md, Equipment.md, Guild Members.md, Core Concept.md, Individual Types.md,
> Battle Test.md, and every EhrensDocs change note (Combat, Equipment, The Dungeon,
> Platform, Core Concept, Specialists, Look and Feel, Open Questions); queue/focus.md;
> queue report 150. Code read: Battle.cs, Battle.Walk.cs, BattleController.cs,
> Guild.Potions.cs, Tuning.cs, SaveManager.cs (potions), Potion*Tests.cs.

## Problem

A potion is drunk for the player today. Any hit that leaves a holder under 30% of their
maximum health makes them drink at once, for free — no attack lost, wait and bar
untouched — and it heals 30% of their maximum. The originals say neither. A potion heals
a number of points set by its rank, and drinking is the player's call: when a member's
cooldown comes up they can have it drink, and the drink costs that attack.

## Goal

Drinking is something the player orders. A member told to drink does so at their next
cooldown, in place of that attack, and heals the amount an F-rank shop potion gives.
No potion is drunk unless the player orders it. The engine exposes the order, and the
drink-button item (#157) calls it.

## Requirements

### What a potion heals

1. A healing potion heals a number of health points from the band its rank sets. The
   nine bands are the ones in Specialists.md and are settled numbers, not placeholders.
   — *Specialists.md, The Alchemist*
2. Every potion in this version is an F-rank potion bought at the shop, so its band is
   10 to 25. — *EhrensDocs/Equipment.md, "For now the only potion is a healing potion,
   bought at the shop"; the user's going-ahead default "the shop sells F-rank potions"
   (queue report 150)*
3. Every shop potion heals the same amount. That amount is one placeholder in the tuning
   file, set to 18 for now. It must lie inside the F band and is listed with the other
   placeholders. It replaces the 30%-of-maximum heal. *(Whether each potion should roll
   its own amount instead is under Open Questions.)* — *queue/focus.md, Missing details;
   Equipment.md, Quality: "The shop sells equipment of a baseline quality"*
4. A drink never takes the drinker past their maximum health. What gets reported is the
   health actually gained. — *EhrensDocs/The Dungeon.md, "How a heal in the dive lands,
   for now": "A heal never takes anyone past their maximum"*

### Drinking is the player's call

5. No potion is ever drunk automatically. A hit that leaves a holder low drinks nothing,
   whatever the threshold, and that holds with Auto on too. Bringing back threshold
   drinking under Auto is #158's job. — *Combat.md, Player Input; queue report 150 (the
   auto-drink change note was removed to match the originals)*
6. While a battle runs, the player can order a drink for any living party member who
   holds at least one potion. Specialists count, because they attack on their own
   cooldown like anyone else. No order can be placed for a monster, a dead member, a
   member holding no potion, or a battle that is over. The player can take an order
   back before it is used. — *Combat.md, Player Input; Combat.md, Specialists in Combat*
7. An order is used at the member's next cooldown. In place of the attack that cooldown
   brings, the member drinks one potion from their own slots. An order ends when it is
   used, when it is taken back, when the member dies, or when the battle ends.
   — *Combat.md, Player Input; EhrensDocs/The Dungeon.md, "Healing potions are packed
   at the start of a raid…": a member drinks only from their own slots, one at a time*
8. The field hits first. A member standing in a Mage's field takes the field's hit as
   their action begins, just as they would before an attack, and drinks only after it. If
   the field kills them, they drink nothing and the potion stays in their slot.
   — *The user's going-ahead default, queue report 150, on Combat.md's open question;
   EhrensDocs/Combat.md, "A close-range attack waits…": "a field it stands in hurts it
   first"*
9. Drinking costs the attack and nothing else. A member who drinks:
   - makes no strikes and picks no target,
   - stays on their own spot instead of walking out,
   - wears no weapon,
   - charges no special bar,
   - pulls no Luck token for the reset, so no free attack follows,
   - leaves any taunt on them unspent, kept for their next attack.

   Their next cooldown then starts, exactly as it would after an attack.
   — *Combat.md, Player Input ("drinking costs that attack"); Luck Checks ("When a
   member finishes an attack"); The Special Bar (charge comes from hits);
   Equipment Durability via Equipment.md; Enemy Targeting, with EhrensDocs/Combat.md
   "What the targeting weights count…" (a taunt is spent by an attack)*
10. A drink counts as one of the member's own cooldown cycles for any lasting effect
    they cast. So a vanished Rogue who drinks has used one of their three cycles.
    — *Combat.md, Lasting Effects ("three of the owner's own cooldown cycles");
    EhrensDocs/Combat.md, "When an effect's count starts…" ("only a cooldown that comes
    up after a wait counts")*
11. A drink is an action of the battle, made at the member's cooldown (requirement 7).
    Its report names who drank, the health gained and the health after, and shows that
    it took the place of an attack. When that action plays, the battle
    screen shows the heal as a green "+" number on the drinker, and their health bar
    climbs. — *EhrensDocs/Look and Feel.md, Damage text*
12. The rules above apply in every battle a member can carry potions into, played
    missions included. — *EhrensDocs/Core Concept.md, played missions: "a member drinks
    from the potions packed for it as in any battle"*
13. The save format does not change. Potions are still counted in the stores and in
    each member's slots, and every saved potion is an F-rank shop potion, so older saves
    load exactly as they do today. — *EhrensDocs/Platform.md, Saving; follows from 2
    and 3*

## Out of Scope

- **The drink button on each member card (#157).** This PRD provides the order that
  button calls, and nothing on screen beyond what requirement 11 describes. Whether a
  drink can be ordered while the fight is paused is #157's to settle.
- **Drinking below 30% under Auto (#158).**
- **Packing potions into party slots on the planning screen (#156).** Until then each
  member is packed one potion, in pick order, as today.
- **The Alchemist.** Brewing, the Intelligence scaling, the Luck check that places a
  potion in its band, and buff potions are all left out. queue/focus.md puts the other
  six specialists out of the first version. Potions come only from the shop.
- Shop potions of any rank above F, the potion's price, and selling potions back.

## Open Questions

- *(Combat.md)* "The Mage's field damages a character as it begins its own attack. A
  member can drink a potion instead of attacking — does a member standing in a field
  take the field's damage when it drinks?" — built with the user's going-ahead default
  of yes (requirement 8).
- *(Mine — proposal, not the docs')* Should every shop potion heal the same amount, or
  should each one roll its own amount inside 10–25 when it is bought, the way shop gear
  does? And if they all heal the same, should that amount sit at the band's bottom (the
  shop's "baseline"), or near the middle? Built with: all the same, 18. Changing to a
  per-potion roll later means a save change.
- *(Mine — proposal)* What if a member has a drink ordered and their special ordered,
  and their cooldown comes up? Proposed: a member holds one order at a time, so ordering
  either one takes back the other.
- *(Mine — proposal)* A close-range member whose attack is already waiting for its
  target to get home is told to drink. Do they drink at once, or keep waiting first?
  Proposed: a drink needs no target, so they drink as soon as they are home themselves.
- *(Mine — proposal)* Can a drink take the place of a free attack from the Luck reset?
  Proposed: no. The free attack is "an ordinary attack in every way", and a special is
  never used on one, so the order waits for the next cooldown that comes after a wait.
- *(Mine — proposal)* If the game closes mid-battle with a drink ordered but not yet
  drunk, is the order still there when the battle carries on? Proposed: no, the same as
  an ordered special today.
