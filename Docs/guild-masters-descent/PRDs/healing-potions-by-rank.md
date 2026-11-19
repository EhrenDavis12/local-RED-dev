# PRD: Healing potions by rank, drunk instead of attacking

> **Status:** Draft, queue item #152 · Source docs read: Combat.md, Specialists.md,
> The Dungeon.md, Equipment.md, Guild Members.md, Core Concept.md, Individual Types.md,
> Battle Test.md, and every EhrensDocs change note (Combat, Equipment, The Dungeon,
> Platform, Core Concept, Specialists, Look and Feel, Open Questions); queue/focus.md;
> queue report 150. Code read: Battle.cs, Battle.Walk.cs, BattleController.cs,
> Guild.Potions.cs, Tuning.cs, SaveManager.cs (potions), ActionReport.cs, TurnPlayback.cs,
> Potion*Tests.cs. Revised after review: the user's going-ahead defaults (2026-11-18) are
> requirements 3 and 14 to 18; the reviewer's notes are settled in 19 to 24.

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
   placeholders. It replaces the 30%-of-maximum heal, and no potion rolls an amount of its
   own. — *the user's going-ahead default, 2026-11-18 ("every shop potion heals a fixed
   18, a placeholder in the tuning file"); queue/focus.md, Missing details*
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
   - leaves any taunt on them unspent, kept for their next attack (see 19).

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

### The user's going-ahead defaults (2026-11-18)

These five were settled with the user as defaults, cheap to change. None is in a design
doc yet.

14. **One order at a time.** A member holds at most one order. Ordering a drink takes
    back an ordered special, and ordering a special takes back an ordered drink. So at
    a cooldown the member either drinks or uses the special, never both.
15. **A waiting close-range member drinks once they're home.** Say a close-range
    member's attack is already waiting when the drink is ordered. They drink as soon as
    they are back on their own spot. Only their own absence holds the drink. Three
    things hold an attack but not a drink: their target being away, their target having
    an attack due ahead of theirs, and their being the first target of a lunge that is
    still out (Battle.Walk.cs `IsHeld`). The drink's place in the order is the one the
    waiting attack already had.
16. **A free attack is never replaced.** A free attack from the Luck reset is always an
    attack. An order placed before one stays put and is used at the next cooldown that
    comes after a wait. This is the same as a special, which is never used on a free
    attack.
17. **An order isn't saved.** A drink that is ordered but not yet drunk is lost if the
    game closes. The saved battle doesn't hold drink orders, the same as an ordered
    special today, and a battle that carries on from a save has none.
18. **18 points.** Every shop potion heals 18 (requirement 3).

### Settled from the review

These are cheap defaults chosen to close the reviewer's notes.

19. **Taunt.** A drink never spends a taunt. A close-range member's target may already
    have been picked, spending the taunt, before the drink was ordered (Battle.Walk.cs,
    the pick in `NextAction`). If the action then turns out to be a drink, the taunt
    goes back on them and is kept for their next attack. — *follows from 9; Combat.md,
    Enemy Targeting*
20. **Full health.** A member at full health can be ordered to drink. The drink still
    uses up the potion and the attack, heals 0, and reports a gain of 0. Combat.md's
    "the player can have it drink" sets no health condition. — *Combat.md, Player Input*
21. **Where the order lives, and the calls.** The order lives in `Battle`, so a battle
    with no screen plays it the same way.
    - `Battle` has `CanOrderDrink(Combatant)`, which applies requirement 6's conditions.
      It also has `OrderDrink(Combatant)`, which returns whether the order was taken,
      plus `CancelDrink(Combatant)` and `IsDrinkOrdered(Combatant)`.
    - `BattleController` wraps these for the screen as `CanOrderDrink`, `ToggleDrink`
      and `IsDrinkOrdered`, and it is what #157 calls. The controller holds rule 14,
      since an ordered special lives there (`_armed`). Arming a special cancels the
      drink order in `Battle`, and ordering a drink removes the member from `_armed`.
    - The controller's tidy-up drops drink orders for the dead and at the battle's end,
      as it already does for specials.
22. **Report shape.** A drink made in place of an attack is an `ActionReport`. It has no
    strikes, `UsedSpecial` and `IsFreeAttack` are both false, and there is a new
    `DrankInstead` flag set to true.
    - Its `Drinks` holds one `DrinkReport` with neither `FollowedStrike` nor
      `FollowedFieldHit` set. That is how a drink in its own right is told apart, so
      the "exactly one is set" note in ActionReport.cs is wrong from now on.
    - `TurnPlayback.From` plays the action's field hits first and then this drink event
      (`PlaybackKind.Drink`).
    - The action is not a lunge (`MeleeTiming.IsLunge` false), so the drinker is never
      away.
    - Since no hit sets off a drink any more (requirement 5), no hit's report and no
      `MoveReport` carries a drink.
23. **Threshold tuning.** `Tuning.PotionDrinkThresholdPercent` stays in the tuning file,
    at 30, for #158. Nothing reads it in this feature. `Tuning.PotionHealPercent` goes,
    and the new heal placeholder of requirement 3 takes its place in the placeholder
    listing.
24. **Existing tests that are wrong.** These assert the old behaviour: drinking set off
    by a hit under the threshold, for free, healing 30%. They must be rewritten or
    deleted against this PRD.
    - `PotionDrinkTests.cs`, every test.
    - `PotionBattleScreenTests.cs`: `R11_TheHitPlaysFirst_…` and `R11a_ADrinkSetOffByFieldDamageOnAMove_…`.
    - `PotionSaveTests.cs`: `R16old_AMemberSavedUnderTheThreshold…DrinksOnTheNextHit`, `ADiveSavedMidBattleAfterADrink…` and `ADiveSavedBeforeADrink…`. These still matter, but they must reach the drink by ordering one.
    - `PotionHoldingTests.cs`: `R17_ThePotionPlaceholdersAreListedOnce…`, whose `PotionHealPercent` case gives way to the new heal placeholder.
    - `BattleLiveInputTests.cs`: the four `Q137_…` drink-on-a-field-move and drink-on-a-swap tests.
    - `CarryInSlotsRaidTests.cs`: `R13_EachDrinkUsesExactlyOnePotion…`, `R13_OneMembersPotionsNeverReachAnother…`, `R14_AMemberStillHoldingAPotionAfterDrinking…`, `R15_R16_ADrunkPotionIsNeverGivenBack…`, `R16_AMemberWhoDrankAndThenDied…`, `R17_APotionDrunkInAPlayedMissionStaysGone…` and `R18_IfTheGameClosesPartwayThroughAPlayedMission…`. Their rules still hold; only the way the drink is set off changes.
    - `CombatMeleeWaitHoldTests.cs`: `R16_ADrinkSetOffByTheFieldHitLengthensTheWindow`.
    - `GameAudioSoundGapsTests.cs`: `ADrinkSetOffByAHit_…` and `ADrinkSetOffByFieldDamageOnAMove_…`. The potion sound now plays on an ordered drink.
    - `MissionPlayOutcomeTests.cs`: `AMemberCarryingAPotionDrinksItUnderTheUsualThreshold…` and `AHeldPotionAboveTheThresholdIsNeverDrunk…`.

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
