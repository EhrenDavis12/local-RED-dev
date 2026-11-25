# PRD: Buff potions

> **Status:** Draft · Source docs read: `Specialists.md`, `Combat.md`, `The Dungeon.md`,
> `Equipment.md`, `Core Concept.md`, `Guild Members.md`, `Individual Types.md`,
> `Battle Test.md`, and in `EhrensDocs/`: `Combat.md`, `The Dungeon.md`, `Equipment.md`,
> `Platform.md`, `Look and Feel.md`, `Specialists.md`, `Core Concept.md`. Code read on
> `queue/196-buff-potions`: the healing potion end to end (`Guild.Potions.cs`, `Member.cs`,
> `PartyPlan.cs`, `Dive.cs`, `Battle.cs`, `LuckBag.cs`, `TankType.cs`, `ShopRows.cs`,
> `SaveManager.cs`, `Tuning.cs`).

Citation keys used below:

- **Brief** — queue item #196, the user 2026-11-24: "build them now if nothing is
  blocking", with the going-ahead defaults **D1–D6** the main loop set for it (cheap to
  change). The originals win over the item title's "drunk like the healing potion".
- **Healing model** — where a doc is silent, the buff follows the healing potion as the
  game is built, per the Brief. The EhrensDocs change note named is the record of that.
- **Main loop 2026-11-25** — decisions the coordinator made after PRD review, as
  going-ahead defaults the user is to confirm: **D7** (which True a draw spends) and the
  build defaults for Open Questions 1–3. Each is also listed under Open Questions.

## Problem

The guild can only carry healing potions into a dive. The five buffs the originals describe
— the only thing the player can *spend* mid-fight to swing it — don't exist, so the
original's "the player acts while it's running — … using a buff potion" has nothing behind
it.

## Goal

The guild can buy all five buffs at the shop, pack them into members' slots when planning a
dive, and use one from the battle screen at any moment of a running fight. Using one costs
no attack and raises its stat (or, for God's Wish, loads Trues into Luck bags) for every
living party member until that battle ends, and nothing of it outlasts the battle.

## Requirements

### The five buffs and what each reaches

1. There are five buff kinds: Wind Step raises Dexterity, Dragon's Vein raises Strength,
   Rock Skin raises Constitution, Ancient Gift raises Intelligence, God's Wish converts Luck
   bag tokens (req 5). — `Specialists.md` § The Alchemist
2. Every buff the guild can get is F rank and raises its stat by a fixed figure, not a roll:
   one tuning-file placeholder per stat buff, each inside the F band of 2 to 5. Nothing
   rolls or places a buff in its band. — Brief D1; `Specialists.md` § The Alchemist (F
   band); Healing model: EhrensDocs `Equipment.md` "For now the only potion is a healing
   potion" (fixed 18)
3. Rock Skin's raise reaches the member's defence only. It never raises maximum or current
   health, including the Brute's ×12. — `Specialists.md` § The Alchemist; `Guild
   Members.md` (health from Constitution)
4. Wind Step's raise reaches each cooldown wait that *begins* after it is used. A wait
   already running is not shortened. — `Combat.md` § Cooldowns; code: `Battle.WaitOf`
   ("worked out where a wait begins and never changed partway through it")
5. God's Wish turns 2 Falses into Trues in each reached member's own Luck bag. A bag left
   with fewer than 2 Falses converts as many as it has (none for none). It has no band and
   no tuning figure: it is 2 at any rank. — `Specialists.md` § The Alchemist; Brief D4
6. Converting adds the converted Falses to the bag's Trues and records them as the
   member's converted count; the bag's token count is unchanged. A pull is the bag's one
   ordinary draw, with no extra draw: if it comes out True while the converted count is
   above 0, the converted count goes down by 1 — converted Trues are spent first. A drawn
   converted True leaves the bag like any pulled token, the check succeeding; it does not
   go back in. — `Specialists.md` § The Alchemist ("spent when it's drawn"); `Combat.md` §
   Luck Checks; Main loop 2026-11-25 D7 (converted first)
7. When the battle a God's Wish was used in ends, each member's bag loses as many Trues as
   its converted count still holds, those tokens staying in the bag as Falses (its token
   count unchanged), and the converted count goes to 0. This holds however the battle ends
   — won, lost, stand-off, or the party turning back mid-battle (which drops the battle
   unsettled). — `Specialists.md` § The Alchemist ("reaches no further than the battle");
   Main loop 2026-11-25 D7; code: `Dive.TurnBack`
8. A stat buff's raise lives in the combatant's stat as the battle reads it
   (`Combatant.GetStat`), never in the member's own stat (`Member.GetStat`), so it never
   reaches anything outside the battle and every battle rule that reads the stat reads it
   raised — damage, cooldown waits (req 4), the support-ring help, the same-tick attack
   order and the Tank's Shields Up figure. Rock Skin's carve-out (req 3) still holds:
   maximum health never reads it. Tests pin help, same-tick order and Shields Up as
   reading the raise. — Main loop 2026-11-25 (defaults for Open Questions 1–3)

### Using a buff

9. The player uses a buff; no member drinks it. Using one costs no member an attack or a
   cooldown, wears nothing, charges no bar and pulls no Luck token. It uses no fight time —
   the way a formation change does — and is applied between ticks. A use made while a tick
   is only partly walked (between two `StepAction` calls on one tick) is applied at the
   next tick boundary: after every action due on that tick has resolved, before any action
   of the next. Until applied, no potion is taken; if the battle ends first, nothing is
   used; and a use not yet applied isn't saved, the way an ordered drink isn't. —
   `Specialists.md` § The Alchemist; `Combat.md` § Player Input; code: `Battle.Move` ("not
   an action: it uses no time"); Main loop 2026-11-25; EhrensDocs `Platform.md` § Saving
   (an ordered drink is lost on close)
10. A buff reaches every party member alive at the moment it is used, specialists included,
    and lasts for the rest of that battle. A member who dies afterwards stops mattering; no
    one is reached later. Monsters are never reached. — `Specialists.md` § The Alchemist;
    Brief D4
11. Using a buff takes one potion of that kind from a living party member who holds one.
    Which holder gives it up is open; see Open Question 4. A dead member's buffs can't be
    used. — Brief D2
12. A buff can be used whenever the battle is running and not over. It can't be used while
    a development build has the fight paused. — `Combat.md` § Player Input; EhrensDocs
    `Combat.md` "The fight pauses only in a development build" and "Drinking a potion is an
    order used at the next cooldown" (drink button not pressable while paused)
13. All five kinds can run at once. Using a kind that is already running replaces it:
    for a stat buff the raise is the new one, not the two added (with fixed figures, the
    same figure); for God's Wish, each bag's remaining converted Trues revert first, as
    req 7 says, and then up to 2 Falses are converted afresh (req 5, 6), so a converted
    count never passes 2. The replaced
    potion is used up. — `Specialists.md` § The Alchemist
14. Auto never uses a buff. — Brief D3
15. Using a buff is deterministic: the same uses at the same ticks of the same fight give
    the same result, at any speed. — EhrensDocs `Combat.md` "The fight can be sped up, and
    only shows sooner"

### Getting buffs

16. The shop sells all five kinds from guild rank F, each for a placeholder price in the
    tuning file, into the guild's stores. Buying works and refuses exactly as buying a
    healing potion does. A buff can't be sold back. — Brief D1; Healing model: EhrensDocs
    `Equipment.md` "For now the only potion is a healing potion"
17. Dive loot is unchanged: no buff ever drops. — Brief D5

### Carrying

18. A buff takes one slot, the same as a healing potion or a unit of loot, and counts as a
    potion everywhere slots are counted — a member's free slots, and the room counted at
    the dive's end. — `The Dungeon.md` § The Dungeon ("A potion takes 1 slot"); EhrensDocs
    `The Dungeon.md` "For now a dive drops ore, herb and healing potions"
19. No member holds a buff in the guild hall. While planning a dive the player chooses, per
    member, how many of each buff kind they pack; each kind starts at 0 for every member.
    A member's potions of every kind together never pass their slots, and the party's
    total of a kind never passes what the stores hold of it. The player sees what's left
    in the stores per kind and the member's slots still free. Going in, or re-entering at a
    rest area, packs exactly those. — Brief D2; Healing model: EhrensDocs `The Dungeon.md`
    "Healing potions are packed at the start of a raid"
20. A played mission has no planning step, so it packs no buffs. — Brief D2 (default 0);
    EhrensDocs `The Dungeon.md` "Healing potions are packed at the start of a raid"
21. When the raid ends, every buff left unused goes back to the stores, a dead member's too;
    one used stays gone. If the whole party falls, every buff packed for the dive is lost.
    — Brief D2; Healing model: EhrensDocs `The Dungeon.md`, same change

### Saving

22. The stores' count of each kind and each member's held count of each kind are saved. A
    member not on the saved dive has their buffs put back in the stores as the save loads.
    — Healing model: EhrensDocs `Platform.md` § Saving
23. A battle saved partway through carries on exactly: the save holds which buffs are
    running and each one's raise, and each member's converted count, so closing and
    opening the game neither ends a buff early nor gives back a used one. A saved battle
    that can't be true is repaired as it loads, not refused: a converted count is clamped
    to 0 through the smaller of 2 and the bag's Trues left, and a raise below 0 goes to 0,
    so the bag still passes `LuckBag.CanBeTrue`. — EhrensDocs `Platform.md` § Saving
    ("plays out exactly as it would have if the game had never closed"; "one drunk on the
    dive is still gone"); Main loop 2026-11-25 (the repair)
24. A save from before buffs loads with none in the stores, none on any member, and none
    running. — Brief D6
25. A save holding a negative buff count, in the stores or on a member, loads with that
    count at none. A member on the saved dive holding more potions in all than their slots
    take is cut to their slots, the extra going to the stores; which kind is cut first is
    open, see Open Question 5. — Healing model: EhrensDocs `Platform.md` § Saving, "For now"

### On screen

26. The battle screen has one button per buff kind the living party holds, showing how many
    of that kind it holds; pressing it uses one (req 9–13). A button can't be pressed when
    req 12 says the buff can't be used. — Brief D3
27. A buff with no picture of its own is drawn as the missing-art stand-in. — Healing
    model: EhrensDocs `Look and Feel.md` (ore and herb as the stand-in); the five icons are
    on the art request list (`queue/reports/205-art-request-list.md`)

## Out of Scope

- The Alchemist, brewing, the laboratory, and buffs above F rank or rolled inside a band.
- Selling a buff back; buffs dropping as loot.
- Auto using a buff; monsters using buffs.
- Buffs on a sent (not played) mission.
- Where the buttons sit, how a running buff is shown, sounds, and the buff art. These are
  look-path work, settled by running the game, not by this PRD.

## Open Questions

Items 1–5 and 7 are gaps the docs and code don't settle. Items 1–3 and 7 are built with
the main loop's going-ahead default (2026-11-25), which tests pin, and wait on the user's
confirmation; items 4–5 carry a **proposed default** — the PRD author's, not the user's.
All are cheap to change.

1. Support-ring help is a share of the member's primary stat. When a buff raises that stat,
   is the help worked out on the raised stat? *Going-ahead default: yes (req 8).* (At F
   it rarely moves the help by more than a point.)
2. Two attacks ready on the same tick go in order of "the higher Dexterity of its own, help
   from the support ring left out". Does Wind Step's raise count in that Dexterity?
   *Going-ahead default: yes (req 8).*
3. The Tank's Shields Up figure is his Constitution plus a roll of his armour, given to the
   allies behind him as defence. Rock Skin "reaches defence only" — does it reach that
   figure? *Going-ahead default: yes (req 8).*
4. When several living members hold the kind being used, whose slot does it come out of?
   It decides whose slot is free for loot at the dive's end. *Proposed default: the first
   holder in the order the party was picked, the order potions are packed in.*
5. A save repair cutting a member to their slots: which kind of potion goes back to the
   stores first? *Proposed default: buffs before healing potions, in the order
   `Specialists.md` lists them, last listed first.*
6. From `Specialists.md`, not blocking this build (no Alchemist yet): "A potion's strength
   scales with the Alchemist's Intelligence, and the Alchemist's Luck check places a potion
   within its band and can raise it — but God's Wish has no band of its own. Does either of
   those reach God's Wish, and does it turn 2 Falses into Trues no matter who brewed it?"
7. After God's Wish, a member's bag holds its own Trues and up to 2 converted ones. When a
   True is drawn, which is spent — a converted one first, or either at random? It decides
   how many Trues the bag keeps once the battle ends. *Going-ahead default D7: converted
   first (req 6, 7).*
