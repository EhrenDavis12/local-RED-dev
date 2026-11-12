# PRD: The Dive

> **Status:** Draft, 2026-11-12, queue item #43. Source docs read: `The Dungeon.md`,
> `Combat.md`, `Guild Members.md`, `Specialists.md`, `Equipment.md`, `Core Concept.md`,
> `Individual Types.md`, and the change notes under `EhrensDocs/` for each of these, plus
> `EhrensDocs/Platform.md`, `queue/focus.md` and `queue/reports/3-member-health.md`. Read
> against the code under `src/guildmasters-descent/Assets/Scripts/Core`. Where a change
> note and the original disagree, the change note wins.

Citations: `TD` = `The Dungeon.md`, `CB` = `Combat.md`, `GM` = `Guild Members.md`, `SP` =
`Specialists.md`, `EQ` = `Equipment.md`, `CC` = `Core Concept.md`, `PF` =
`EhrensDocs/Platform.md`, `FOCUS` = `queue/focus.md`. A `-CN` suffix means that doc's change
note in `EhrensDocs/`, named by its `## Change:` title. `§` names a section in the original.

## Problem

The guild can hire, equip and sell. It cannot dive. The battle engine runs only a demo
fight, and nothing in the guild or the save knows that a dungeon exists. Members also keep
whatever health they ended on, and every member gets a flat 10 health whatever their rank.

## Goal

A player takes a party from the guild hall into the guild's one dungeon and fights down it
floor by floor. They pay to go in, earn gold and experience, decide at each rest area whether
to push on, and can turn back anywhere. Then they come home with whatever gold they can carry,
or lose members for good. Everything the dive changes is in the guild and the save: gold,
fees, deaths, gear brought home or lost, experience, and how deep the guild has got. The
screens that show the dive are not in this PRD. It specifies only the choices the player
has to be able to make.

## Requirements

Already built and relied on, not re-specified: the battle engine and the six types' kits
(`Battle`, `Combatant`, `BattleResult`), monster stats from level (`Battle.AddMonster`), gear
wear during battle, XP sub-units and level-ups (`Member.AwardXp`), gold that never goes below
zero (`Guild.TrySpend`), and injured members being unavailable (`Member.IsAvailable`).

**Unsettled: what the save holds while a dive is in progress.** Requirements 4, 8, 9, 13,
17 and 24, and D15, all depend on what happens when the app is closed, killed or
backgrounded during a dive. That has not been decided. It is the first blocking entry under
Open Questions. Until it is answered, those requirements say what the guild holds *once a
dive ends*. They do not say what is on disk while a dive is still running.

### The guild's dungeon

1. Every guild holds one F-rank dungeon from the moment the game is new. A save from before
   this feature loads with that dungeon added, nothing reached in it.
   *TD-CN "A guild starts off with a single F-rank dungeon"; FOCUS Goal "one dungeon".*
2. The dungeon's depth is drawn when it is created, from a range in the tuning file. For now
   that range is exactly 10 to 10. The user was asked about this, and the build goes ahead
   with 10, so the bottom floor is the second rest area and nothing lies beyond it.
   *TD § Finding Dungeons "A dungeon's depth is random when the dungeon is created"; FOCUS
   In "one dungeon at least 10 floors deep with two rest areas".*
3. Every 5th floor is a rest area: floors 5 and 10.
   *TD § The Dungeon.*
4. The save records four things for the dungeon, and all four survive a save and load:
   - the depth drawn under requirement 2;
   - every floor's monsters under D14 (each battle's monster type, level and cell);
   - the deepest floor reached, which never goes down;
   - the re-entry point under D17.

   Because the save gains these fields, `SaveFile.CurrentVersion` goes up from 1 to 2.
   Version-1 saves still load under requirement 1. Saved dungeon data that the game cannot
   make sense of is handled the way `SaveManager` already handles corruption: the load
   reports `Corrupt` and leaves the slot as it is.
   *TD § The Dungeon Board ("the deepest floor reached"); TD § Entering the Dungeon ("re-enters
   at the last rest area reached"); PF § Saving ("A save the game can't read… is reported as
   such and left on the phone as it is").*

### Health

5. A member's maximum health comes from their rank or tier, through a table in the tuning
   file. F is 10, and every other rung is a placeholder. This replaces the flat
   `Tuning.NewMemberHealth` for members, and it applies to recruits and to existing members
   on load. *GM-CN "Starting health is set by rank, and F rank starts at 10". Defaults D6.*
6. A monster's health is the F-rank figure, whatever the monster's level.
   *TD-CN "The dungeon's enemies are monsters" ("the 10 a new F-rank member starts with,
   whatever the monster's level").*
7. Damage carries from battle to battle for the whole dive. Health comes back only from the
   Cook (requirement 19), a rest area (requirement 20), or the dive ending (requirement 9).
   *CB-CN "Members stay hurt from battle to battle, and 0 health is death".*
8. A member whose health reaches 0 in a dive battle is dead on the spot, for good. They take
   no part in any later battle of the dive, and they are not on the roster once the dive
   ends. *Same CB-CN; TD § The Dungeon ("there is no way to bring a dead member back").*
9. When a dive ends, every member who survived it is at full health. A member in the guild
   hall is never below full health, and that includes right after a load. Today the code
   keeps `CurrentHealth` between dives, which this replaces.
   *CB-CN "Members stay hurt…" ("Back at the guild hall a member's health is back to full").*

### Starting a dive

10. A party is 1 to 15 members from the roster, counting specialists. No member is injured,
    no member appears twice, and each member stands on their own node of the 5-by-3 party
    grid. The dungeon board queue item comes later, so until then the build needs a minimal,
    temporary way for the player to choose the party and place it on the grid before
    entering. Its layout is not this PRD's concern. *CC § The Party; CC § Missions ("can't
    be sent on a mission or taken on a dive"); CB § Formation.*
11. **Enter** starts the party at floor 1 and costs the entry fee. A bigger party always costs
    more than a smaller one, so the fee strictly rises with party size. The amounts are in
    the tuning file (see D16).
    *TD § Entering the Dungeon.*
12. **Re-enter** is offered when there is a re-entry point (D17) and that point is not the
    bottom floor. With a depth of 10, that means Re-enter is never offered from floor 10.
    The party starts at the re-entry point, and its first battle is on the floor after it.
    Re-entering costs the entry fee for this party plus a teleport fee. The party does not
    have to be the one that reached the rest area.
    *TD § Entering the Dungeon; TD § The Dungeon Board ("where they re-enter at the last
    rest area reached").*
13. If the guild cannot pay the fee, the dive does not start and nothing changes. A fee it
    can pay is taken when the dive starts.
    *CC-CN "The guild can't go into debt".*

### Floors, battles and monsters

14. Each battle floor of this dungeon has 3 battles, and each battle is against 1 monster.
    The battles are fought in order. The next battle starts only after the one before it is
    won. *TD-CN "A floor is a series of battles that scrolls right into the next".*
15. Each monster has one of the six combat types, with that type's attacks, special and
    advantages, and it carries no gear. Its level comes from a per-floor table in the tuning
    file. No floor's monsters are a lower level than a shallower floor's, and the deepest
    battle floor's monsters are a higher level than floor 1's.
    *TD-CN "The dungeon's enemies are monsters" ("Deeper floors have higher-level monsters").*
16. A floor drops its gold as one lump, and only once every battle on that floor is won. The
    amount for each floor is in the tuning file. Gold is the only thing a dive yields: no
    materials, no items, no dropped gear.
    *TD-CN "A floor is a series of battles…"; TD-CN "For now a dive yields only gold";
    EQ-CN "For now a dive yields only gold".*
17. Experience is awarded per floor, once all of the floor's battles are won. Each member
    gets the number of monsters the party defeated on that floor, divided by the number of
    party members, counting specialists (D10 says which members count). The share uses the
    existing exact XP sub-units, so it is never rounded.
    *GM § Levels and Experience.*

### Rest areas and the Cook

18. At a rest area the player chooses to **push on** to the next floor or **go home**. When
    no floor lies past the rest area, going home is the only choice.
    *TD § The Dungeon.*
19. After every battle the party wins, each living Cook heals the party by a placeholder
    amount, capped at each member's maximum. At a rest area each living Cook also heals by a
    second placeholder amount, larger than the after-battle one, on top of the rest area's
    own healing. *SP § The Cook ("heals a little after every battle, and substantially more
    at a rest area — on top of the rest area's own healing"). Defaults D11.*
20. Arriving at a rest area heals every living member by a placeholder amount, capped at
    their maximum. *TD § The Dungeon ("where the party heals").*

### Turning back, gold and the carry limit

21. The player can turn back at any point between two battles, not only at a rest area. D9
    covers turning back during a battle.
    *TD-CN "A party can turn back anywhere, and carries only so much gold out".*
22. Going home from a rest area keeps all the gold found on the dive. Turning back anywhere
    else loses the gold found since the last rest area the party passed on this dive. When
    the party has passed no rest area, that is all the gold found on the dive.
    *Same TD-CN ("leaving between rest areas loses the gold found since the last rest area").*
23. When the party walks out, it carries out at most the sum of its living members' carry
    limits: 10 for each member, and for a Porter the figure in D1. Gold over that sum is left
    behind, and the guild receives the rest. A party with no living members carries out
    nothing. Requirement 22 is applied first: the gold found since the last rest area is
    dropped. Only then does the carry limit apply to what is left. *Same TD-CN ("Gold
    beyond what the party can carry is left behind"). Defaults D1, D3.*

### Death, gear and the end of the dive

24. A dive ends in one of three ways: the party goes home from a rest area, the party turns
    back, or a battle leaves no member alive. When it ends, requirements 8, 9, 22, 23 and 25
    are applied together, and the result is what the save holds next.
    *TD § The Dungeon; TD-CN "A party can turn back anywhere…".*
25. When the party walks out, a dead member's weapon and armour come home and go back to the
    stores, held by no one (D2). When a battle leaves no member alive, every piece the party
    took in is lost and leaves the stores.
    *EQ § Assignment ("the party brings their gear back if there's room left… otherwise the
    gear is lost").*

### Defaults standing in for open questions

Each of these is the build's behavior until the user answers the matching open question. Each
is cheap to change, and every number in them lives in the tuning file.

- **D1.** A Porter carries 110: the 10 every member carries, plus 100. *(Open Question 1)*
- **D2.** A dead member's gear always comes home when the party walks out. It does not count
  against the gold carry limit. *(Open Question 2)*
- **D3.** The party holds all the gold it finds while it is inside. The carry limit applies
  only when the party walks out. *(Open Question 3)*
- **D4.** A dive never leaves a member injured: a member comes back fine or dead. *(Open
  Question 4)*
- **D5.** A monster's damage is its damage stat alone, and its defence is its Constitution
  alone. A monster can be any of the six types. This is already how the code is built.
  *(Open Question 5)*
- **D6.** Health comes from rank or tier alone. Level, Constitution and promotion do nothing
  to it beyond moving the member to a new rung's figure. `Guild.TryPromote` also sets
  `MaxHealth` from the health table for the new rung. Every specialist tier is 10, and the E
  placeholder is also 10, so a first promotion changes nothing visible. *(Open Question 6)*
- **D7.** A rest-area floor has no battles. It drops no gold and gives no experience.
  *(Open Question 7)*
- **D8.** A battle that ends in a stand-off counts as the party turning back at that point,
  so requirement 22 applies and the floor gives no experience. *(Open Question 8)*
- **D9.** The party can turn back only between battles, never during one. *(Open Question 9)*
- **D10.** The experience divisor is the number of members alive when the floor's last
  battle is won, and only those members get the share. A floor left before its battles are
  all won gives no experience. *(Open Question 10)*
- **D11.** A Cook heals every living party member, the Cook included. Two Cooks heal twice.
  *(Open Question 11)*
- **D12.** Where everyone stands when a battle ends is where they start the next battle. The
  dead leave their nodes empty. *(Open Question 12)*
- **D13.** Every special bar starts empty at the start of each battle, which is how the code
  is built. *(Open Question 13)*
- **D14.** A floor's monsters, meaning their types, levels and cells, are the same on every
  dive. They are drawn once, when the dungeon is created, and saved (requirement 4). Each
  battle's monster type is drawn uniformly from the six combat types, and its cell uniformly
  from the 15 nodes of the monster grid. Both draws use a seeded RNG, which is a
  placeholder. Its level comes from the per-floor table (requirement 15). *(Open Question
  14)*
- **D15.** A floor counts as reached once the party starts its first battle there, or
  arrives there if it is a rest area. *(Open Question 15)*
- **D16.** The entry fee is a per-member amount times the party size. The teleport fee is one
  flat amount. *(Open Question 16)*
- **D17.** The re-entry point is the deepest rest area the most recent dive reached. A
  re-entered dive counts the rest area it started at. So the point can move back up, for
  example from 10 to 5, and a dive that reaches no rest area leaves no re-entry point. The
  user has been asked, and the build goes ahead with this. *(Open Question 17)*

## Out of Scope

- The dive screen's layout, the dungeon board, party planning and auto-placement. Those are
  the dungeon board queue item (`TD § The Dungeon Board`). This PRD needs those screens only
  to offer the choices in requirements 11, 12, 18 and 21.
- Training missions, timed missions, the mission board, guild ranks above F, crafting, field
  repair, and every specialist except the Cook and the Porter, the Scout's Search included
  (FOCUS Not included).
- Materials, items and dropped gear (requirement 16).
- Boss floors, floor layouts and routes. No doc settles them (TD-CN "A floor is a series of
  battles…", its Why).
- Monster art. The battle screen draws each monster with its own type's art, as
  `Tuning.MonstersUseMemberTypeArt` is set. TD-CN says monsters "might be limited to just
  the Archer's animations". That is the battle screen's to settle, not the dive's.

## Open Questions

**Blocking: needs an answer before what the save holds during a dive can be built.**

- *PF Open Questions:* "What happens to a dive in progress when the app is closed or killed —
  is it saved and resumed, lost, or something else? It decides whether closing the app
  mid-battle can dodge a death." It is unsettled, and there is no default. Requirements 4,
  8, 9, 13, 17 and 24, and D15, depend on it. The game already saves whenever it is sent
  to the background (PF § Saving). The answer is expected to be one of two shapes, and
  either one slots in as a single sentence:
  - **(i)** The disk keeps the guild as it was before the dive. The dive works on a copy and
    commits it only when the dive ends. A dive cut short leaves no trace: no fee paid, no
    deaths, no experience, no new depth, no wear.
  - **(ii)** The disk keeps whatever the last background save caught. The fee is gone, and
    the experience, deepest floor and gear wear earned up to that save are kept.

  Sub-question, under either shape: does a member who died during the dive come back after
  a reload? Whatever the answer, requirement 9 holds: no member is ever in the hall below
  full health.

**Unanswered by the user. The build uses the default named.**

1. Does a Porter carry 100 in total, or 110 (100 plus the 10 everyone carries)? TD-CN leaves
   it open. SP § The Porter says "on top of what any party member already carries". *(D1)*
2. How does a dead member's gear count against a carry limit measured in gold? TD-CN: "how a
   dead member's gear counts against a limit measured in gold". *(D2)*
3. When does the carry limit bite: is extra gold lost as soon as it is found, or only when
   the party walks out? *(D3)* Separately, depth is pinned at 10 for now (requirement 2).
   If it is ever raised, there would be battle floors past the last rest area, and nothing
   says what happens when the bottom floor is cleared.
4. Can a dive leave a member injured? CB-CN: "whether a dive can leave a member injured".
   *(D4)*
5. Do monsters get their attack and defence from level stats alone, or from figures set by
   hand for each kind of monster? Which types do monsters use? *(D5)*
6. CB-CN and GM-CN: "how much health each rank above F starts with; whether a specialist's
   starting health follows their tier the same way; whether health grows with level or with
   a promotion; and whether Constitution plays into it." Also GM-CN Open Questions: "Does a
   higher-rank hire start with more than 10 health?" *(D6)*
7. Is a rest-area floor a floor of battles with a rest at the end, or a safe floor with no
   battles? *(D7)*
8. What does a stand-off battle do to the dive? CB-CN has battles end as a stand-off after a
   set number of rounds. *(D8)*
9. TD-CN Open Questions: "Can a party turn back in the middle of a battle, or only between
   battles?" *(D9)*
10. In "divided by the number of party members", which members count: the ones who started
    the floor or the ones still alive? And does a floor left partway through give any
    experience? *(D10)*
11. Whom does the Cook heal, and do two Cooks both heal? *(D11)*
12. Does the formation carry from one battle to the next? *(D12)*
13. Does a special bar carry over from one battle of a dive to the next? *(D13)*
14. Is a floor's set of monsters the same every dive, or new each time? TD § The Dungeon
    Board ("The enemy types and the floor layout appear as the party reaches each floor")
    suggests they are fixed. *(D14)*
15. When does a floor count as "reached" for the deepest floor reached? *(D15)*
16. Is the teleport fee flat, or does it rise with party size the way the entry fee does?
    *(D16)*
17. "The last rest area reached": is that the deepest rest area ever reached, or the one the
    most recent dive reached? *(D17)*
- Every amount: the fees, the gold each floor drops, monster levels by floor, rest-area and
  Cook healing, the carry limits, and the depth range. Each is a placeholder in the tuning
  file, to be balanced later.
