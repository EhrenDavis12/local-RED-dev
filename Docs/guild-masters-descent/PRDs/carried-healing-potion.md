# PRD: Carried Healing Potion

> **Status:** Draft, queue item #98 · Source docs read: `Core Concept.md`, `Combat.md`,
> `Equipment.md`, `Guild Members.md`, `Individual Types.md`, `Specialists.md`,
> `The Dungeon.md`, and every change note under `EhrensDocs/` (`Equipment.md`,
> `Combat.md`, `The Dungeon.md`, `Platform.md`, `Look and Feel.md`, `Guild Members.md`,
> `Core Concept.md`, `Specialists.md`, `Individual Types.md`), plus
> `queue/reports/81-items-review.md` and `queue/focus.md`. Code read on
> `src/guildmasters-descent` (`Guild.cs`, `Member.cs`, `Shop.cs`, `ShopRows.cs`,
> `MemberSheet.cs`, `Battle.cs`, `BattleSnapshot.cs`, `Dive.cs`, `SaveFile.cs`,
> `SaveManager.cs`, `Tuning.cs`, `HitNumbers.cs`, `BattleScreen.cs`).

## Problem

The shop sells only gear. Inside a floor nothing gives health back: the dive heals only
between floors and at rest areas (`The Dungeon.md`, The Dungeon). A member on their way down
can't be kept alive, and the player can't spend gold on doing that.

## Goal

The player buys healing potions at the shop and hands one to a member in the Dorms. In a
battle, the first time that member drops low, they drink it by themselves: a green "+"
number rises and their health bar climbs. The player never taps anything. The potion is
gone once drunk. A potion that isn't drunk stays with the member. Saves keep all of it, and
saves from before potions load with none.

## Requirements

Unless a requirement names another source, it comes from
`EhrensDocs/Equipment.md`, change "A member carries one healing potion and drinks it by
themselves" (**the change note**). Requirements marked **default** follow defaults recorded
for queue item #98 while the user's answers are pending. Each matches an entry in Open
Questions, and each is cheap to change. Requirements marked **user default** were settled by
the user for this build, recorded as cheap to change, and are not yet in a design doc.

### Holding a potion

1. A member holds at most one potion, in a potion slot of its own next to their weapon and
   armour slots. The only potion is the healing potion. (The change note: "one potion",
   "for now the only potion is a healing potion".)
2. **Default:** every member type can hold one: the six combat types, the Cook and the
   Porter. The Dorms member sheet shows the potion slot for the Cook and the Porter too.
   Today the sheet draws the slots only when `MemberSheet.CarriesGear` is true
   (`DormsScreen.cs:305`), and that is false for a specialist. So the potion slot needs its
   own condition: shown for every member. (Queue #98 default; open question "Can a
   specialist carry a potion into a dive too, or only the six combat types?")
3. The potion's picture is the red round flask (`Menus/icons/icon_round_flask_64/128`),
   wherever a potion is drawn. (`EhrensDocs/Look and Feel.md`, Icons, "What the game
   carries": "the red round flask, which is the health potion"; report 81, Icons for
   annie.)

### Buying and handing over

4. The shop's Buy column offers the healing potion next to the gear, at the placeholder
   price below. Buying one pays the price and puts one potion in the guild's stores. With
   too little gold the buy is refused and nothing changes. (The change note: "bought at
   the shop"; `EhrensDocs/Core Concept.md`, "The guild can't go into debt".) The number of
   potions the stores can hold is not capped, the same as gear. (Whether the stores are
   capped at all is still an open question: `EhrensDocs/Equipment.md`, "Two questions on
   stores and condition".)
5. In the Dorms, the player hands a potion from the stores to a member whose potion slot
   is empty. The stores then hold one fewer. A member who already holds a potion can't be
   given a second. Doing this with no potions in the stores changes nothing. (The change
   note: "handed over in the Dorms"; requirement 1.)
5a. **User default:** in the Dorms, the player can take a member's potion back. It goes to
    the stores and the slot is empty.
5b. **User default:** while a member is away on a mission, their potion can be neither
    handed over nor taken back. Today the mission lock guards only the gear paths
    (`Guild.CheckEquip`, `TryAssign`, `Unassign`), so the potion paths need it too. This
    matches `EhrensDocs/Core Concept.md`, "Missions are in the first version": an away
    member can't "have their gear changed".
5c. **User default:** dismissing a member puts their potion back in the stores. A held
    potion isn't counted in the stores (requirement 5), so `Guild.TryDismiss`
    (`Guild.cs:456-464`) would lose it unless it is returned there.
5d. **User default:** a potion can't be sold back to the shop. The Sell column lists gear
    only. This holds however the potion is modelled: whatever the code does with gear
    (selling, repair, durability, condition) never applies to a potion.

### Drinking

6. A member drinks only during a battle. The trigger: a hit leaves a living member who
   holds a potion with health **strictly under** the threshold share of their current
   maximum health (placeholder 30%). The comparison is exact, with no rounding. At maximum
   50, a member left on 15 doesn't drink and one left on 14 does. Once drunk, the slot is
   empty for the rest of the dive. (The change note: "drinks it by themselves when they
   drop low in a battle". Report 81, Potions, option A, which the user chose: "drunk by
   itself the first time health drops under a set share (placeholder 30%)".)
7. Every kind of damage can trigger it: ordinary strikes, specials, area hits, and the
   Mage's lingering field. That includes the field damage a member takes when the player
   moves them onto a field mid-battle (`Battle.Move`). (Requirement 6: "the first time
   health drops under", whatever the source.)
8. The drink happens straight after the hit that triggered it, before the next strike of
   the same attack and before anyone else acts. A hit that takes a member to 0 kills them,
   and they don't drink. Any hit that lands counts, even one whose damage defence takes
   to 0, and a miss never counts. The only way a 0-damage hit can trigger a drink is a
   member already under the threshold, after a rebalance (requirement 16). That member
   drinks on the next hit that lands on them. (Report 81, "the first time health drops under"; `Guild
   Members.md`, Base Stats: "When a member's health reaches zero, they are dead.")
9. **Default:** drinking costs nothing. It is not an action. It leaves the member's wait,
   any free attack they are owed and their special bar as they were. (Queue #98 default;
   open question "Does drinking the potion cost a member anything in the battle?")
10. **User default:** the potion heals a placeholder share of the member's maximum health,
    rounded up. A heal never takes a member past their maximum. (The change note: the heal
    amount is a placeholder. `EhrensDocs/The Dungeon.md`, "How a heal in the dive lands":
    "A heal never takes anyone past their maximum".)

### Showing it

11. On the battle screen the triggering hit plays first. Then a green "+N" rises from the
    member, where N is the health they actually gained, and their health bar climbs to the
    healed figure. Today the bar only ever steps down (`BattleScreen.cs:1174`). Anything
    later in the same action starts from the healed health. (`EhrensDocs/Look and Feel.md`,
    Damage text: "a heal is green with a '+'". Report 81, option A: "a hurt member drinks
    and a green '+' number pops". The `HitKind.Heal` glyphs already exist in
    `HitNumbers.cs`.)
11a. The engine reports every drink: who drank, the health gained, and the hit it followed.
     It reports a drink both in the record of an action (today `ActionReport` carries only
     `Strikes` and `FieldHits`) and in what `Battle.Move` hands back (today only
     `FieldHits`). That way the screen can play each drink in its place. A drink set off by
     field damage on a move shows its "+N" and climbing bar straight after that field hit,
     the same as one set off in an action. (Requirements 7, 8 and 11.)

### After the dive

12. **Default:** a member who comes home without drinking keeps the potion in their slot
    for the next dive. That holds however the dive ended, by going home or by turning back.
    (Queue #98 default; open question "If a member comes home without drinking their
    potion, does it go back to the stores?")
12a. **User default:** a member who dies on a dive still holding their potion sends it home
     to the stores when the dive ends, the same as their gear. If the whole party falls,
     every potion the party carried is lost. `Dive.End` (`Dive.cs:475-481`) takes a dead
     member off the roster, so it has to put their potion back in the stores first.
     (`EhrensDocs/Equipment.md`, "A dead member's gear comes home, for now", applied to the
     potion.)

### Saves

13. The save holds the potions in the stores and each member's potion slot. The save
    version goes from 8 to 9, so that an older build of the game reports a new save as
    "made by a newer version" and doesn't load it while dropping the potions.
    (`EhrensDocs/Platform.md`, Saving: "one made by a newer version of the game, is
    reported as such and left on the phone as it is". The version history in
    `SaveFile.cs`.)
14. A save of version 8 or older loads unchanged, with no potion in the stores and none on
    any member. This is not reported as a repair. (`EhrensDocs/Platform.md`, Saving: "A
    save made by an older version still loads". Queue #98.)
15. A dive saved after a member drinks loads with that member's slot empty, mid-battle
    included. Closing and reopening the game never gives back a potion that was drunk.
    (`EhrensDocs/Platform.md`, Saving: the rest of a battle plays out "exactly as it would
    have if the game had never closed".)
16. Loading never checks a member's potion against the threshold. If the threshold has
    been rebalanced, a saved member can sit under it while still holding a potion. That
    member loads as saved and drinks on the next hit that leaves them under the threshold
    (requirement 6). (`EhrensDocs/Platform.md`, Saving: "A saved battle is never judged
    against a placeholder number".)
16a. A version 9 save may hold a potion value no game could have written: a negative number
     of potions in the stores, or a member slot holding something other than one potion or
     none. That value is fixed as the save loads, to none in the stores or an empty slot,
     and the save still loads. The fix is reported as a repair. (`EhrensDocs/Platform.md`,
     Saving, "For now": gear equipped where it can't be "is fixed as it loads… and the save
     loads". `SaveManager.RepairEquippedSlots` handles gear this way.)

### Placeholders

17. These three go in `Assets/Scripts/Core/Tuning/Tuning.cs`, each with `[Placeholder]`
    like every other placeholder there. (`queue/focus.md`, Missing details: "A missing
    *number* gets a placeholder… kept with every other placeholder in one tuning file".)

    | Placeholder | Value | Where the value comes from |
    |---|---|---|
    | Drink threshold, % of max health | 30 | Report 81, option A, which the user chose; user default |
    | Heal, % of max health, rounded up | 30 | User default |
    | Shop price, gold | 20 | User default |

## Out of Scope

- Shields of any kind. That is a separate item, and it is blocked.
- Tapping to drink, or any other way for the player to drive a drink (report 81,
  option B).
- Any potion other than the healing potion, and the Alchemist's brewed potions
  (`Specialists.md`, The Alchemist). The change note keeps those separate.
- Drinking outside a battle: between battles, between floors, at a rest area.
- Monsters carrying potions.
- Any marker on the battle screen or the Dungeon Board showing who holds a potion. Any new
  drinking animation or sound. These are look-and-adjust work if wanted later.

## Open Questions

From `EhrensDocs/Equipment.md`, "Questions on shields and potions". The build follows the
default noted on each until the user answers:

- Can a specialist carry a potion into a dive too, or only the six combat types?
  *(Default: anyone who goes into battle, which means the six combat types plus the Cook
  and the Porter. Requirement 2.)*
- Does drinking the potion cost a member anything in the battle — its next attack, or a
  wait — or is it free? *(Default: free. Requirement 9.)*
- If a member comes home without drinking their potion, does it go back to the stores?
  *(Default: no, it stays in their slot. Requirement 12.)*
