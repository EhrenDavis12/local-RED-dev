# Roadmap — where things live

An index of locations, not a summary. Headings only; the docs are the source of truth.

## Design docs (originals, read-only)

### Battle Test.md — Battle Test
A fixed pair of teams, their levels, gear and test field, so test battles can be compared.
- What This Is For
- The Field
- The Player's Team
- The Enemy Team
- Levels and Experience
- Open Questions

### Combat.md — Combat
Formation, cooldowns and Luck checks, player input, reach, the special bar, lasting
effects, specialists and enemies in combat, targeting and gear durability.
- Formation
- Cooldowns
- Luck Checks
- Player Input
- Attacks and Reach
- The Special Bar
- Lasting Effects
- Specialists in Combat
- Enemies
- Targeting
- Equipment Durability
- Open Questions

### Core Concept.md — Guild Master's Descent
The overall premise and top-level systems.
- The Premise
- Time
- Guild Rank
- The Three Boards
- The Dorms and the Stations
- The Mead Hall
- The Party
- Missions
- The Recruiting Board
- The Economy
- Open Questions

### Equipment.md — Equipment
What members carry, and gear quality, sourcing, assignment, durability and repair.
- What a Member Carries
- Quality
- Where Gear Comes From
- Assignment
- Durability
- Repair
- Open Questions

### Guild Members.md — Guild Members
Combat types, stats, levels, promotion, specialists and party size.
- Combat Types
- The Support Ring
- Diminishing Returns on Help
- Base Stats
- Weapons and Armour
- Starting Stats
- Levels and Experience
- Stat Weighting by Type
- Promotion
- Specialists
- Party Size
- Open Questions

### Individual Types.md — Individual Types
Sheets for the six combat types.
- The Brute
- The Tank
- The Fighter
- The Rogue
- The Archer
- The Mage
- Open Questions

### Specialists.md — Specialists
Specialist recruiting, tiers, equipment and each specialist type.
- Recruiting
- Tiers
- Equipment
- The Porter
- The Cook
- The Scout
- The Herbalist and the Miner
- The Blacksmith
- The Armourer
- The Alchemist
- Open Questions

### The Dungeon.md — The Dungeon
The dungeon board, finding and entering dungeons, and training missions.
- The Dungeon Board
- Finding Dungeons
- The Dungeon
- Entering the Dungeon
- Training Missions
- Open Questions

## Files with pending changes

- `EhrensDocs/Combat.md` — proposed changes to Combat.md (formation cost, status line,
  open question, a dive never injuring and positions carrying between battles for now,
  how a cooldown rounds, the clock and a multi-strike attack landing in one tick, the Luck
  reset's free attack and specials, a battle ending in a stand-off after a set time, a
  special putting nothing in its owner's bar, every dive starting with every bar empty,
  an effect's count, its end and a second cast stacking, how a taunt is spent, a
  specialist's cooldown, open questions on specials, taunts and the dive, on cooldown
  combat's defaults, and on the special bar, the fight pausing for now, the fight's
  speed, the speed question answered, a close-range attack waiting for its target to be
  home, attacks on the same tick going in turn, questions on that wait, every
  character's own Luck bag and when no token is pulled for now, the opening check as a
  pull from the combatant's own bag for now, questions on the Luck bag's defaults,
  drinking a potion as an order used at the next cooldown for now (the battle screen's
  drink buttons and Auto drinking included), questions on drinking a potion, a new
  Rogue's worked cooldown of 71 ticks, a special going off by itself in its own turn, and
  questions on it).
- `EhrensDocs/Core Concept.md` — proposed changes to Core Concept.md (the guild can't go
  into debt, open questions on the roster, injury and a new guild, how time away is
  counted, missions in the first version as F-rank jobs that pay gold, open
  questions on missions' defaults, a member on a dive can't be dismissed for now, and a
  question on dismissing a member on a dive, a mission can be played as a battle for
  now, questions on played missions, and a guild with no members and no way to hire gets
  nothing, for now).
- `EhrensDocs/Equipment.md` — proposed changes to Equipment.md (Dorms visibility, open
  question, dive and mission loot is gold only, selling gear back, repair costs gold only for now,
  open questions on stores and condition, a zero-damage hit still wears gear, a dead
  member's gear takes slots for now, the shop sells class F only for now, the Tank's
  swappable shield, the healing potion bought at
  the shop, F rank and healing a fixed 18, for now, a member's gear locked for a dive for
  now, a broken shield adding nothing, and questions on shields and potions).
- `EhrensDocs/Guild Members.md` — proposed changes to Guild Members.md (open questions on
  recruits and promotion, who shares a combat's experience and a stand-off's for now, help
  follows the board live, an open question on sharing experience, a specialist's K from
  its tier, a hit rounding down once for now, health from a member's own Constitution
  and what's taken staying taken for now, questions on health, experience as the bar and
  level as the number for now, questions on experience, help coming back to whole points
  once, starting stats by type, and a question on the Cook's and the Porter's starting
  stats).
- `EhrensDocs/Individual Types.md` — proposed changes to Individual Types.md (where the
  Brute's cleaves land, the Tank's taunt, Shields Up and bonus for now, the Fighter's and
  the Rogue's ordinary strikes when the target dies, the Rogue's bonus for now, the
  flurry's leftover strikes staying within reach and its strikes able to miss for now, a
  failed Vanish fails for one strike, Volley and the Archer's streak for now, the Mage's
  column, field, the field's defence and wear, timing and bonus for now, open questions
  on Vanish, taunts, the field and the types' defaults, on the field's timing, and on the
  flurry, the Fighter's bonus as the refill for now, an open question on the Fighter's
  bonus, the flurry's Luck pull coming as it begins for now, and a question on the
  flurry's pull).
- `EhrensDocs/Look and Feel.md` — new doc proposed for the originals (Look and Feel): the
  user's approved look for the game, gathered from the animation work.
  - Battle scene (meadow)
  - Battle scene (cave)
  - Shadows and depth
  - Health and mana bars
  - Characters and animations
  - Effects
  - Damage text
  - Menus and the scroll
  - Map
  - Font
  - Icons
  - Palette
  - Sound and music
  - Open Questions
- `EhrensDocs/Open Questions.md` — new doc proposed for the originals (Open Questions —
  for the design docs' owner): the questions the build is waiting on.
  - How to answer
  - Open Questions
    - Loot and carrying
    - Enemies
    - Health
    - Battle
    - Guild rank
    - Finding dungeons
- `EhrensDocs/Platform.md` — new doc proposed for the originals (Platform): the iPhone
  runs landscape only, and the game saves by itself, mid-battle too, working out maximum
  health afresh as a save loads and keeping every Luck bag, any special waiting to go off
  and the three saved teams.
  - Orientation
  - Saving
  - Open Questions
- `EhrensDocs/The Dungeon.md` — proposed changes to The Dungeon.md (starting dungeon, dive
  loot is gold only, a floor is a series of battles whose gold drops at the end, turning
  back anywhere and gold taking no slots for now, enemies
  are monsters with a rank and level and how they fight for now, a floor's monsters the
  same every dive and where each stands, re-entering for now, open questions
  on what gold a retreat keeps and the dive's defaults, how a heal in the dive lands (for now), open questions on healing in the
  dive, potions packed at a raid's start and returned at its end for now, questions on
  carrying, party planning as one screen, and the guild's three saved teams).
- `EhrensDocs/Specialists.md` — proposed changes to Specialists.md (two Cooks heal twice
  as much, a dead Cook adds nothing and a Cook heals the same at every level for now, open
  questions on the Cook).

The design docs themselves are the source of truth; consult them, not this map, for content.
