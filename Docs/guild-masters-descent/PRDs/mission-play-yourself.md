# PRD: Play a Mission Yourself

> **Status:** Draft · Source docs read: Core Concept, Combat, The Dungeon, Guild Members,
> Individual Types, Specialists, Equipment (originals and EhrensDocs change notes), Look and
> Feel, Platform (EhrensDocs). Code read on `queue/106-mission-play-yourself`: `Guild.Missions.cs`,
> `MissionBoard.cs`, `Missions.cs`, `MissionBoardView.cs`, `HallRoomScreen.cs`, `BattleScreen.cs`,
> `DiveScreen.cs`, `Dive.cs`, `Battle.cs`, `DemoEncounter.cs`, `GameSession.cs`, `SaveFile.cs`.

Requirements marked **Default** are a cheap, reversible choice made for this build, not yet the
user's word. Each one is asked again under Open Questions. Where an original design doc and
an EhrensDocs change note disagree, the original wins and the change note gives way; a change
note that only fills a gap still stands (the user's rule, `queue/focus.md`).

## Problem

The only way to earn gold by fighting is a dive, which costs an entry fee. Missions pay, but
only on their own: the player sends members and waits out a timer, and the result is a secret
roll. The user, 2026-11-15: "i need a way to actually fight with out going into the doungon to
make some chash on my own. Allow me to auto a mission whcih it currently does or let me run
through it. from the mission board."

## Goal

On the Mission Board, every mission on offer can still be sent and auto-resolved exactly as it
is today, or played as a real battle on the existing battle screen with the members the player
picked. Winning a played mission pays the mission's gold at once. Losing one costs what a failed
mission costs. Nothing about a dive changes, and the save format does not change.

## Requirements

### Choosing to play

1. **Both ways, same board.** For the mission chosen on the Mission Board and the members picked
   for it, the player can either send it (today's auto-resolve, unchanged) or play it. Source:
   the user, 2026-11-15 (queue item #106). No design doc records played missions yet.
2. **The same gate as sending.** Play is offered and refused under exactly the rules that govern
   Send: exactly the mission's stated number of members, none injured, none already out on a
   mission, none in a dive that hasn't ended, and a free mission slot. The guild is brought up
   to now first, so a mission a restock has already replaced is refused as no longer on the
   board. A refused play changes nothing. Source: Core Concept change "Missions are in the first
   version, as F-rank jobs that pay gold" (paragraph 2); Core Concept `## Missions` ("Anything
   the guild sends people out on takes one of those slots"). In code this is
   `Guild.CheckSendMission`, reused, not copied.
3. **The mission leaves the board when the battle starts**, the same as a sent mission, and a
   restock during the battle doesn't touch it. **Default:** it never comes back, so a played
   mission can't be replayed, won or lost. Source: Core Concept change "Missions are in the
   first version…" (paragraph 1: "a mission that's sent leaves the board… A restock never
   touches a mission that's already out").

### Who fights, and against what

4. **Who fights** is exactly the members picked for the mission, divers and specialists alike,
   and no one else. Source: Core Concept change "Missions are in the first version…" (paragraph
   2: "Divers and specialists can both go").
5. **Default: no planning step.** The picked members are placed by the same automatic placement
   the Dungeon Board uses (combat types in front, specialists behind), and the player can move
   them during the fight as in any battle. Source: The Dungeon `## The Dungeon Board` ("The
   system does the initial placement"); Combat change "Changing formation mid-battle is free".
6. **Default: what a played mission fields.** Monsters built the way the dungeon's are: each one
   of the six combat types, drawn at random, rank F, level 1, its type's starting stats, each on
   a node of its own drawn at random. Whether a monster carries a weapon or wears armour is a
   chance set by the mission's rank, as for a dungeon's enemies; at F both chances are 0 for
   now, placeholders in the tuning file, so an F mission's monsters carry no gear. How many
   depends on the mission's hidden
   variance, so "easier or harder than its stated rank" shows in the fight itself: one fewer
   than the members needed (never fewer than one) for an easier mission, the same number for
   one as stated, one more for a harder one. The three counts are placeholders in the tuning
   file. The enemies are not shown before the fight; the variance stays secret. Source: The
   Dungeon change "The dungeon's enemies are monsters"; Combat `## Enemies` ("The dungeon's rank
   also determines the chance that an enemy carries a weapon and the chance that it wears
   armour"); Core Concept `## Missions` ("backend
   variance… easier or harder than its stated rank suggests… a sense of mystery").
7. **Default: the meadow backdrop.** A mission is above ground, so it is fought in the meadow
   scene, not the cave. Source: Specialists `## The Herbalist and the Miner` ("above-ground missions");
   Look and Feel `## Battle scene (meadow)`.

### The battle

8. **The existing battle screen, entered and left the way a dive enters and leaves it.** It is
   built with a battle controller and a finished-callback, as the dive screen does, not a new
   screen. The battle plays by every rule any battle has (cooldowns, the Luck reset, specials
   from the skill buttons, focus, free formation changes, the stand-off at the tick cap). Its
   Retreat button and its pause Quit are today tied to a dive, and must work for a mission
   battle too. A pause Quit the player confirms is a retreat, in every way a press of Retreat
   is, and so a loss under requirement 14. Source: Combat (whole doc and change notes); code: `DiveScreen.PlayBattle`,
   `BattleScreen.Build`.
9. **Special bars start empty** and nothing of them outlasts the battle: a bar belongs to a
   dive, never to the member. Source: Combat change "Every bar empties on a new floor and starts
   each dive empty, for now".
10. **Gear wears as in any battle.** Weapons wear from attacking and armour from being hit, and
    the wear stays after the mission. Source: Equipment `## Durability` ("Gear wears down as it
    is used"). The Core Concept change note's "it doesn't… wear gear" gives way to it.
    **Default:** a member carrying a potion drinks it under the usual threshold, as in any
    battle, and it stays drunk. Source: Equipment change "A member carries one healing potion
    and drinks it by themselves".
11. **Default: no timer.** A played mission ignores the mission's length. It resolves the
    moment the battle's result is decided, never appears among the missions out, and holds no
    slot once the battle is over. Its outcome (gold, injuries, experience) is recorded on the
    guild at that moment, before the battle screen's finished callback runs; the callback only
    carries the player's Exit or Retry. Source: the user, 2026-11-15 ("run through it"). Departs
    from Core Concept `## Missions` ("Missions are timed"), so it stays a question.

### How it ends

12. **A win pays the mission's gold**, at once, capped the way a sale is. **Default:** nothing
    else, no items, materials or gear. Core Concept `## Missions` and Equipment `## Where Gear
    Comes From` say missions also bring back items, materials and gear, but neither gives a
    rule for what or how much, so those are deferred. Source: Equipment change "For now a dive
    yields only gold" ("For now, though, loot is just gold… a dive or a mission yields gold and
    nothing else"); Core Concept change
    "Missions are in the first version…" (paragraph 4).
13. **A loss pays nothing, and every member sent comes home injured**, exactly as a failed auto
    mission does: a fresh injury counted from the battle's end, where an older, longer injury
    already on a member stands. Source: Core Concept change "Missions are in the first
    version…" (paragraph 4: "every member sent comes home injured"); Core Concept `## Missions`
    ("Mission failure normally results in an injured status").
14. **Default: a stand-off and a retreat are losses** (requirement 13), the same way a dive
    counts a stand-off as turning back. Source: Core Concept `## Missions` ("members abandon a
    mission before dying"); The Dungeon change "A party can turn back anywhere…".
15. **No one dies on a mission.** A member brought to no health drops out of the fight as in
    any battle, but stays on the roster with their gear. After the battle, every member sent is
    back to full health. A dive's ending removes its dead from the roster; a mission's must not.
    Source: Core Concept `## Missions` ("members abandon a mission before dying"); Core Concept
    change "Missions are in the first version…" (paragraph 4: "No one dies on a mission"); Combat
    change "Health is full at the guild hall…".
16. **Default: injury goes by the outcome, not the member.** A won mission injures no one, even
    a member who fell during it; a lost one injures every member sent, even one still standing.
    This mirrors the auto mission. Source: Core Concept change "Missions are in the first
    version…" (paragraph 4).
17. **Kills pay experience**, as in any combat: each kill is worth what its enemy's rank is
    worth, added up when the battle ends and divided equally. Source: Guild Members `## Levels
    and Experience`. The Core Concept change note's "A mission gives no experience" gives way
    to it. **Default:** only members still standing when the battle ends share it, exactly as
    in a dive, so a loss pays none; a stand-off pays for the kills made in it; a retreat,
    a confirmed pause Quit included, pays nothing, as a dive's retreat drops its battle
    unsettled. Source: Guild Members change "Who shares a combat's experience, for now"; code:
    `Dive.ShareExperience`, `Dive.TurnBack`. Experience is already saved, so this needs no
    save change.
18. **A win is never undone.** Once the battle's result is decided, Retreat and Quit do
    nothing, as on a dive. Source: The Dungeon change "A party can turn back anywhere…"; code:
    `Dive.TurnBack`.
19. **Default: where the player lands.** The result scroll shows as for any battle. Exit goes to
    the guild hall and Retry to the Mission Board, mirroring a dive, whose Retry goes to the
    Dungeon Board. A played mission adds nothing to the hall notice, because the result scroll
    has already told the player. On a won played mission the scroll's Gold row shows the
    mission's pay; today that row is measured from a dive's gold, which a mission battle has
    none of. Source: code, `DiveScreen.PlayBattle`, `BattleScreen.ShowBanner`.

### Saving

20. **Default: no save format change.** The save stays at version 10. The battle itself is not
    saved. The guild is saved as it stands: the offer already gone, and any gear wear or potions
    drunk so far. Sent to the background, the battle picks up where it stopped. If the game is
    closed or killed partway through, the guild loads with the mission gone and unpaid, nobody
    injured, and everyone at full health. Source: Platform `## Saving` ("A battle doesn't move on
    while the game is closed or in the background"; "A member not on the saved dive loads at
    full").

### The auto path

21. **Sending is untouched.** Today's send, timer, outcome roll, pay, injury and hall notice
    behave exactly as before, and every existing mission test still passes. Source: Core
    Concept change "Missions are in the first version…".

## Out of Scope

- Any change to dives, the Dungeon Board or the demo battle.
- A planning step that places the mission's members on the grid before the fight.
- Showing a mission's enemies, or its variance, before the fight.
- Rewards other than gold, and any balancing of mission pay against dungeon gold.
- Mission-specific monster art; missing art follows the standing yellow-shape rule.
- Calling an auto mission back early.
- Saving a mission battle partway through (see requirement 20).

## Open Questions

- Who shares a played mission's kill experience? The default is the members still standing
  when it ends, as in a dive, so a loss pays none, a stand-off pays for its kills, and a
  retreat pays nothing.
- The original says missions are timed. Should a played mission resolve the moment its battle
  ends, or still run out the mission's timer before it pays? The default is the moment the
  battle ends.
- Should a played mission bring back items, materials or gear as well as gold, as the original
  docs say missions do? The default is gold only, until there is a rule for what and how much.
- Should a member drink their potion in a played mission, using it up? The default is yes, as
  in any battle.
- When the player retreats from a played mission, or it ends in a stand-off, are the members
  injured as on a loss, or do they come home fine with no pay? The default is injured.
- In a played mission, is injury per member (whoever fell is injured, win or lose) or per
  outcome (a loss injures everyone, a win no one)? The default is per outcome.
- If the game is killed partway through a played mission, the default loses the mission with
  no pay and no injury, so killing the game dodges a loss's injury. Should a cut-off battle
  count as a retreat instead? That needs a save version bump: version 11 saves a marker for a
  played mission in progress, and an older save loads with none.
- How many monsters does a played mission field, and should the mission's hidden variance
  decide it? The default is one fewer, the same, or one more than the members needed.
- Can a played mission be replayed after it's lost? The default is no: it leaves the board when
  the battle starts.
- Does a played mission need a free mission slot, even though it never runs on a timer? The
  default is yes.
- On a failed mission, are all the members injured or only some, and is any gold paid? (Core
  Concept change notes.)
- What decides whether a mission succeeds or fails — do the members' stats, types, gear or
  number count — and what does the backend variance move? (Core Concept change notes.)
