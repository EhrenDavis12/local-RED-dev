# PRD: Missions from the Mission Board

> **Status:** Draft · Source docs read: Core Concept.md, Equipment.md, Guild Members.md,
> The Dungeon.md, Specialists.md, Combat.md, Individual Types.md; EhrensDocs change notes
> for Core Concept, Equipment, Guild Members, Combat, The Dungeon, Specialists, Individual
> Types; EhrensDocs/Platform.md; queue/focus.md. Code read: Core/Guild (Guild, Member,
> RecruitingBoard, ITimeDriven), Core/Save (SaveFile, SaveManager), Core/Tuning,
> Core/Menu (HallEntries), Core/Dungeon/PartyPlan, Game/Menu (HallRoomScreen,
> GuildHallScreen), Game/Session/GameSession.

## Problem

The only way the guild earns gold is the dive. The Mission Board room in the hall says
"There are no missions in this version." User (2026-11-14): "I need a way to send my guys
out onto other missions to make money." This brings timed missions into the first version,
overriding the Focus's "Not included" line on them.

## Goal

From the Mission Board, the player sends idle members out on F-rank timed missions. While
out, those members can't dive. The mission runs in real time, open or closed, and when it
ends it either pays gold or sends its members home injured. Saves made before missions
still load.

## Requirements

### What a mission is

1. Every mission on the board is rank F, and the board shows each mission's rank. The
   board offers only missions at or below the guild's grade, and the guild never rises
   above F in this version. — Core Concept `## Missions` ¶2; Focus `## Not included`
   (guild ranks above F).
2. Each mission needs a stated number of members. The number differs from mission to
   mission: some need one, some need several. The board shows it. — Core Concept
   `## Missions` ¶3. *Whether that is exactly N or at least N: see Open Questions.*
3. An F-rank mission takes minutes. Its length is fixed when the mission appears.
   — Core Concept `## Missions` ¶3 ("low-rank missions take minutes").
4. A mission can turn out easier or harder than its stated rank. The player is never
   shown which. — Core Concept `## Missions` ¶2. *What the variance moves: see Open
   Questions.*

### Sending

5. Divers and specialists can both be sent. — Core Concept `## Missions` ¶4 (the death
   rule names "rank or tier"); Specialists `## The Herbalist and the Miner` (specialists
   work "on above-ground missions").
6. An injured member can't be sent. — Core Concept `## Missions` ¶4. (Code:
   `Member.IsAvailable` already says this.)
7. A member out on a mission can't be picked for a dive or sent on a second mission.
   Picking them on the Dungeon Board is refused, the way picking an injured member is
   refused now (`PartyPlan.CheckPick` / `Check`). — Core Concept `## Missions` ¶1.
8. A placeholder number of missions can run at once at rank F (`MissionSlotsF`). Sending
   one more is refused and changes nothing. — Core Concept `## Missions` ¶3.
9. Sending a mission costs no gold. The player can't pay to make a mission finish
   sooner: its timer always runs its full length. — Core Concept `## Missions` ¶4 ("a
   mission timer runs its full length whatever the player pays"). No doc gives a mission
   a cost.

### Time

10. A mission's timer runs on the guild's one clock and is moved forward only by
    `Guild.Settle`, as a new `ITimeDriven` part. So it runs while the game is open, in
    the background, or closed. Each second counts once. Time away has no limit. If the
    phone's clock is set back, the mission waits until the clock catches up. —
    Core Concept `## Time` ¶1; EhrensDocs/Core Concept "How time away is counted".
11. A mission that ended while the player was away has already paid, or already injured
    its members, by the time the guild is next settled. Its members are back. An injury
    from a mission that ended partway through the time away has already healed by
    exactly the time since that mission ended: no less, and no credit for time before
    the end. The contract a test pins: suppose one settle of `E` seconds reaches a
    mission with `T` seconds left, where `T ≤ E`. Each member it injures then has
    `InjuryDurationSeconds − (E − T)` left, floored at 0. That figure is the same whether
    the `E` seconds are settled at once or in any number of pieces. — EhrensDocs/Core
    Concept "How time away is counted" ("an injury heals by exactly the time that has
    passed since it happened"); Core Concept `## Time` ¶1.
11a. A mission ends when its time left reaches 0 or less. A settle that brings it exactly
    to 0 ends it in that settle.
12. A mission's outcome can't be changed by saving and loading, or by how often the game
    was opened while it ran. Settling in pieces gives the same result as settling once.
    The recruiting board already works this way. — EhrensDocs/Platform `## Saving` ¶3
    (saving and loading "can't re-roll"; stated there for battles, and extended here
    to missions); EhrensDocs/Core Concept "How time away is counted" (each second counts
    once). The outcome is drawn when the mission is sent, from an `IRng` the caller passes
    in, and it is stored on the running mission. Settling draws nothing, so a test can
    drive the outcome through the `IRng`.
12a. Sending settles first, the way `TryHire` does. A refusal changes nothing beyond that
    settle.
12b. Wherever the rules ask whether a member is on the held dive, the caller passes the
    held dive in (`GameSession.HeldDive`). `Guild` doesn't hold the dive. (This applies
    if Open Question 8's default is taken.)
12c. Each way of refusing a member who is out on a mission gets its own outcome value: the
    Dungeon Board pick (`PickOutcome`, `PartyOutcome`), and equip, promote and dismiss if
    Open Question 6's default is taken. `TryDismiss` may change from `bool` to an outcome
    type to carry it.

### Outcome

13. A mission that succeeds adds its gold to the guild. The total is capped at
    `int.MaxValue`, the way `TrySell` and the dive cap theirs. — Core Concept
    `## Missions` ¶5 ("Missions pay"); user request 2026-11-14.
14. A mission that fails sends its members home injured, not dead. Each one gets the same
    injury `Guild.InjureMember` gives: the existing `InjuryDurationSeconds`, with the
    longer of the old and new time kept (`Member.Injure`). Inside the settle it is
    applied directly through `Member.Injure`, never through `Guild.InjureMember`. That
    method settles first, so calling it from inside `Settle` would count elapsed time
    twice or recurse. The mission's part then takes the rest of the settle's elapsed time
    (elapsed − the mission's time left) off that new injury itself. For that to be right,
    the mission part runs after `InjuryPart` in `TimeDrivenParts`. The injury part then
    never sees, in the same settle, an injury the mission part has just made, so no
    second is taken off twice (req 11). — Core Concept `## Missions` ¶4. *Which
    members, and whether any gold is paid: see Open Questions.*
15. No member dies on a mission in this version. The death risk applies only to a member
    whose rank or tier is below the mission's rank, and no member is below F. —
    Core Concept `## Missions` ¶4.
16. A mission gives no experience. Experience comes from kills, and mission rewards
    "keep the guild going but don't advance it". — Guild Members `## Levels and
    Experience` ¶2; Core Concept `## Missions` ¶6.
17. A mission doesn't change a member's health. Health matters only inside a dive.
    — EhrensDocs/Combat "Health is full at the guild hall".

### Save format

18. The save version goes from 7 to 8. A save holds the mission board's offers and
    whatever it needs to restock them the same way after a load, plus each running
    mission. For a running mission it holds: rank, members needed, pay, the member IDs,
    the time left, and whatever fixes its outcome (req. 12). Time left is stored the way
    injuries and the board's restock store theirs: as seconds counted down by settling,
    not as a wall-clock end time. — Code pattern: `Member.InjurySecondsRemaining`,
    `RecruitingBoard.SecondsTowardRestock`.
18a. The save also holds the results of finished missions until the hall notice
    (Open Question 9) has shown them. A mission that ends during a settle on load or
    resume never loses its result. A save without that field loads with no results
    waiting.
19. A save of version 7 or older has no missions. It loads with an empty board that is
    first stocked when opened, the way the recruiting board is (`SaveManager.Check`),
    with no missions running and every member at home. This isn't a repair and isn't
    logged as one. — EhrensDocs/Platform `## Saving` ¶5 ("A save made by an older version
    still loads").
20. A saved mission with more time left than the current placeholder lengths allow is
    loaded as it is, not refused or cut down. — EhrensDocs/Platform `## Saving` ¶5
    ("rebalancing a placeholder can't turn a good save into one the game can't read").
21. A saved mission holding values the model gives no meaning to is reported as a save
    the game can't read. Examples: negative time left, an undefined rank, a number of
    members below 1. This matches the existing `IsMeaningful` checks. — EhrensDocs/
    Platform `## Saving` ¶5. *A mission naming a member who isn't on the roster, or
    shared between two missions, or also on the saved dive: see Open Questions 10. The
    build takes its default.*

### Hall

22. The Mission Board room stops saying "There are no missions in this version." It
    offers the board's missions, lets the player choose members and send them, and shows
    each running mission with its time left. — Core Concept `## The Three Boards`,
    `## Missions`. Layout is built and looked at, not specified here.
23. Wherever the hall shows a member's availability, a member out on a mission shows as
    away. That means the Dorms roster row and the Dungeon Board's party picker, which
    today show "Injured". — Core Concept `## Missions` ¶1; Focus `## Goal` ("a roster
    screen with each member's stats, level, gear and injuries").

### Placeholders (all in `Core/Tuning/Tuning.cs`, each with `[Placeholder]`)

These are numbers only. Each is a starting value to balance later.

| Name | Value | Note |
|---|---|---|
| `MissionSlotsF` | 3 | Missions running at once at rank F ("a few") |
| `MissionBoardSize` | 4 | Missions the board offers when stocked |
| `MissionRestockSeconds` | 3600 | Real seconds between board restocks (if the restock default below is taken) |
| `MissionMembersMin` / `Max` | 1 / 3 | Range of members a mission needs |
| `MissionDurationSecondsMinF` / `MaxF` | 300 / 900 | An F mission's length, 5–15 minutes |
| `MissionPayGoldF` | by members needed: 1 → 20–40, 2 → 40–70, 3 → 60–100 | Gold an F mission pays. Sized against a floor's 8–32 gold and the 60 gold a 30-minute injury costs to heal |
| `MissionFailChancePercent` | easier 10 / as stated 25 / harder 50 | Only if the outcome default below is taken |
| `MissionVarianceWeights` | easier 25 / as stated 50 / harder 25 | Only if the outcome default below is taken |

## Out of Scope

- Training missions from the Dungeon Board (Focus `## Not included`, user 2026-11-11).
- Guild ranks above F, and mission ranks above F (user 2026-11-14).
- Milestone quests and promotion tests (Core Concept `## Guild Rank`).
- Claim missions, and the chance that an ordinary mission finds and claims a dungeon (The
  Dungeon `## Finding Dungeons` ¶3). The original says ordinary missions carry this chance.
  This version leaves it out per the user's scope.
- Items and materials as mission rewards (Core Concept `## Missions` ¶5). The game has no
  items or materials yet.
- The Herbalist's and Miner's yield bonus (Specialists): not in this version.
- The Mission room's Demo Battle button stays as it is.

## Open Questions

Each question below is a rule the docs leave open. Each has a cheap default, marked as
this PRD's proposal and not the docs' word. The build can go ahead on the default.

1. **What decides whether a mission succeeds or fails, and what does the "backend
   variance" move?** The docs give what failure costs but no way to reach it. Nothing
   says whether the members' stats, types, gear or number count. *Proposed default:* when
   a mission appears it is secretly drawn easier, as stated, or harder
   (`MissionVarianceWeights`). Each has a flat failure chance (`MissionFailChancePercent`).
   Nothing about the members counts. The outcome is drawn when the mission is sent and
   applied when it ends. Gear doesn't wear on a mission. Cheap to change: it is one
   function plus three tuning lines.
2. **On a failure, are all the members injured or only some, and is any gold paid?**
   *Proposed default:* every member sent comes home injured, and no gold is paid. Cheap.
3. **Does a mission need exactly its stated number of members, or at least that many?**
   *Proposed default:* exactly. Cheap.
4. **Can a mission bring back gear in this version?** Core Concept and Equipment say a
   mission "can also bring back gear". The dive's first version yields gold only
   (EhrensDocs/Equipment "For now a dive yields only gold"). Equipment's open question
   "Is dropped gear rolled the same way a crafted or bought piece is, and does its class
   follow the dungeon floor or the mission's rank?" is still open. *Proposed default:*
   gold only for now, the same as the dive. Cheap to add later, since gear rolling exists
   (`Guild.TryAddGear`).
5. **How does the board fill and refill?** No doc says. *Proposed default:* the board
   works like the recruiting board. It holds `MissionBoardSize` offers and is stocked
   when first opened. A restock every `MissionRestockSeconds` replaces every offer still
   on it. A sent mission leaves the board and is not replaced until the next restock.
   Running missions are untouched by a restock. Cheap.
6. **What can the player do with a member who is out on a mission: change their gear,
   promote them, dismiss them?** *Proposed default:* none of the three until the member
   is back. Cheap.
7. **Can a mission be called back early?** *Proposed default:* no. It runs its full
   length (req. 9). Cheap.
8. **Can a member who is on a held dive be sent on a mission?** The player can be in the
   hall while a dive is held (`GuildHallScreen.RoomOpened`). The docs state only that a
   member on a mission can't dive, not the reverse. *Proposed default:* no, they're in
   the dungeon. Cheap.
9. **How does the player learn that a mission finished, and how it went?** *Proposed
   default:* the next time the hall is shown, a notice lists each mission that ended
   since it was last shown, with the gold paid or who came home injured. It works like
   the existing repair notice. Cheap; it is UI.
10. **A save whose mission names a member not on the roster, a member on two missions, or
    a member also on the saved dive: refused, or fixed as it loads?** *Proposed default:*
    fixed, and logged as a repair. The bad member is taken off the mission. The mission
    keeps running with the members it has left and still pays in full. A mission left
    with no valid member is dropped. A mission whose member count doesn't match its
    stated need, with every ID valid, is also treated as a repair under the same rule.
    This matches how bad gear slots are fixed now (EhrensDocs/Platform `## Saving`, "For
    now"). Cheap.
