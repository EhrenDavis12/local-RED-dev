# PRD: Health heals at home, 1 point a minute

> **Status:** Draft, queue item #187 [S] · Source docs read: Core Concept, Guild Members,
> Specialists, The Dungeon, Combat, Equipment, Individual Types, Battle Test (originals);
> EhrensDocs Core Concept, Guild Members, Specialists, The Dungeon, Combat, Equipment,
> Platform, Open Questions, Look and Feel; queue report 184. Source read:
> `src/guildmasters-descent` (Member, Guild, Dive, PlayedMission, SaveManager,
> SaveLifecycle, RosterRow, PartyPickRow, MemberSheet).

## Problem

A member who comes home from a dive hurt is put straight back to full health
(`Dive.cs` `End`, line 550). The originals say lost health takes time to come back. As it
stands, a dive's damage costs nothing once the party is home, and there's nothing for the
mead hall (#189) to speed up.

## Goal

A member who survives a dive comes home with the health they ended it on. From then on they
get 1 point back a minute, up to their maximum, counted on the guild's existing clock. That
clock keeps running while the game is closed or in the background, and never counts the
time a member spends fighting, in a dive or a played mission. Saves keep each member's health, and an older save loads
with everyone in the hall at full.

## Requirements

### Coming home

1. When a dive ends, each surviving member keeps the health they had when it ended. This
   is the same for every ending: going home from a rest area, retreating, and a stand-off.
   Nobody's health is raised to full. Dead members leave the roster, as they do today.
   *Core Concept, The Mead Hall ("Health lost on a dive doesn't come back at once");
   EhrensDocs Combat, "A dive never injures" ("a member comes home, hurt or not").*
2. Being short of health is not being injured. A hurt member doesn't show as "Injured",
   and being short of health on its own never stops them being sent on a dive or a mission
   or being picked into a saved team. *User's call in the #187 brief ("allowed, as
   today"). The original's question on this stays open; see Open Questions.*

### Healing

3. A member below their maximum health gets back 1 point for every full minute of time
   that counts, and no more. No gold is spent and the player does nothing. *Core Concept,
   The Mead Hall ("With no Cook in the guild, health comes back on its own at 1 point a
   minute, and there is nothing to pay for").*
4. The time is counted by the guild's existing settle clock, the one injuries already
   heal by (`Guild.Settle`, `LastSettledUnixSeconds`). So it follows the same rules: time
   closed and time in the background count the same as time open, there is no limit on
   time away, a clock change for time zone or summer time adds or takes away nothing, and
   a phone clock set back counts nothing until it catches up. Don't add a second clock.
   *Core Concept, Time ("lost health is recovered while the player is away"); EhrensDocs
   Core Concept, "How time away is counted"; the brief.*
5. No time counts toward a member's healing while they are away fighting. That means in a
   dive that hasn't ended, or in a played mission whose result isn't decided yet. It
   covers:
   - time with the game closed partway through a dive;
   - a backgrounded game settling while a dive or a played mission is on
     (`SaveLifecycle.OnApplicationPause`);
   - loading a save that holds a dive;
   - every other settle, whoever calls it.

   Only the time at home counts. That holds however the settles fall around the day the
   party leaves and the day it comes back. *Core Concept, Time ("A dive in progress ...
   doesn't advance while the game is closed"); the brief; user's call 2026-11-24 for
   played missions.*
5a. **How the exclusion works.** The guild holds the dive in progress and the played
   mission in progress, if any. It holds them in memory only and never saves them, the
   same way it holds its clock (`AttachClock`). `Guild.Settle()` keeps no arguments. Each
   time it heals a member, it first asks those held fights whether that member is still
   away (`Dive.Holds`, or the played mission's party while its result is null). A fight
   that has ended stops excluding its members, even if it is still held. The fights are
   registered by the code that creates them, never by the code that calls `Settle`:
   - `Dive.TryBegin` (`Dive.cs:226`) settles the guild before the party leaves, then
     registers the dive.
   - `Dive.Restore` (`Dive.cs:624`) registers the dive it restores. That runs inside
     `SaveManager.Check`, so it is in place before `SaveManager.Load:130` settles.
   - `Dive.End` (`Dive.cs:505`) settles the guild while the dive still holds its party,
     before it marks the dive ended and sends anyone home. Then it clears the
     registration.
   - `PlayedMission.TryBegin` already settles at line 86. It registers the mission once
     the battle starts.
   - `PlayedMission.End` already settles at line 194, while the mission is still
     registered. It clears the registration afterwards.

   No caller of `Settle` changes. That includes `OpenBoard`, `TryHire`, `TryHeal`,
   `InjureMember`, the mission board's settles, `SaveManager.Load`,
   `SaveLifecycle.OnApplicationPause` and every screen's `Refresh`. *Mechanism chosen
   from the code, per the reviewer's finding.* Passing the dive into `Settle` from every
   caller is the other way to do it, and it's rejected. Most of those callers have no
   dive in reach and would pass none. Then one missed or null caller heals the party
   mid-dive. With registration done where a fight begins, no caller can get it wrong.
6. Partial minutes are never lost. The seconds counted toward a member's next point carry
   over between settles and across a save and reload. So a member settled every 30
   seconds still gets 1 point a minute. *Default (author's pick, per the brief). The
   only other reading, rounding down each settle, would mean a player tapping through
   menus never heals.*
7. Healing stops at the member's maximum health and never goes past it. When a member
   reaches full, any seconds left over are dropped, and so are the carried seconds of any
   member at full. *Default (author's pick). It matches EhrensDocs The Dungeon, "How a
   heal in the dive lands" ("A heal never takes anyone past their maximum").*
8. A member's count toward their next point starts again from zero when they come home
   from a dive. Their first point back comes one full minute after the dive ends.
   *Default (author's pick, cheap to change).*
9. Until the mead hall is built (#189), having a Cook in the guild changes nothing here.
   Every member heals at 1 point a minute whether or not the guild has a Cook. *Core
   Concept, The Mead Hall ("recovery happens on its own given time, and gold buys it
   sooner"). Adding the Cook is #189's work.*
10. A member out on a sent mission keeps healing, the same as one in the hall. *User's
    call, 2026-11-24. A sent mission "doesn't touch health" (EhrensDocs Core Concept,
    missions change).*
11. Injury and lost health are tracked separately. Each heals on its own count, and
    neither one pauses or speeds up the other. *Core Concept, Open Questions ("A member
    short of health is not the same as an injured one"); default for the case where both
    apply, which nothing in the game produces today.*

### Maximum health changing

12. Promotion doesn't change current health. A hurt member is just as hurt after being
    promoted, which replaces today's refill to full in `Guild.TryPromote`. Maximum health
    still comes from Constitution, and promotion keeps the stats. *Guild Members,
    Promotion ("the stats already earned are kept"); EhrensDocs Open Questions #11 (going
    ahead with "Promotion ... doesn't change a member's health directly").*
13. A level-up that raises Constitution keeps today's rule: current health rises by the
    same amount as the maximum. *EhrensDocs Guild Members, "Health counts a member's own
    Constitution".* Level-ups happen only in combat, so this feature doesn't change how
    that happens. It only means the raised figure now comes home.
14. When maximum health is worked out again from Constitution as a save loads, a member's
    current health is capped at the new maximum. A higher maximum doesn't raise current
    health: the gap heals by requirement 3. *EhrensDocs Platform, Saving ("Maximum health
    is never taken from a save"; a member on a saved dive "keeps the health they had ...
    capped at their maximum"), extended here to members in the hall.*

### Saving and older saves

15. The save holds each member's current health, which `Member.CurrentHealth` already
    stores, and one new field per member, `Member.HealthRegenSeconds`, for the seconds
    counted toward their next point. The guild's `LastSettledUnixSeconds` is reused as it
    is. The save version goes from 15 to 16. *EhrensDocs Platform, Saving ("A save made by
    an older version still loads"); the brief.*
16. A save from version 16 on loads every member in the hall with their saved health. It
    is capped at their maximum (requirement 14) and raised to at least 1, because 0 health
    reads as dead. Their carried seconds are kept between 0 and 59, and set to 0 for a
    member at full. Members on a saved dive keep the rule they have today. *Default
    repair (author's pick). It follows how EhrensDocs Platform's "For now" list fixes
    other impossible values as a save loads.*
17. A save older than version 16 loads every member in the hall at full health, with no
    carried seconds, exactly as such a save loads today. Members on a saved dive keep
    today's rule. *The brief ("existing members saved at full health are fine").*
18. A loaded save is settled to now as it is today, so time passed while the game was
    closed heals members in the hall straight away (requirements 4 and 5 apply).
    *Core Concept, Time.*

### Display

19. The member sheet's existing "Health current / max" line shows the member's real
    current health. *Already built (`MemberSheet.HealthLine`).*
20. The Dorms roster row and the dungeon board's party-pick row also show health as
    current / max, so the player can see who is hurt when picking a party. *Default
    (author's pick, per the brief). This is the look-and-adjust path: placement and
    wording get settled by running the app, not by tests.*
21. Shown health updates when a screen is redrawn, which is when it opens and after every
    tap, the same as the injury countdown. It doesn't tick live on screen. *Default
    (author's pick). Matches `DormsScreen.Refresh`.*

## Out of Scope

- The mead hall, paid healing, and anything the Cook does at home (#189). Requirement 9
  leaves the place for it. Nothing here pins how the Cook's heal combines with the
  1-a-minute heal.
- Healing inside a dive (the 5% between floors and the 15% at rest areas) and the Cook's
  dive healing. None of that changes.
- A played mission's outcome. A member still comes home from one at full health, as
  EhrensDocs Core Concept "A mission can be played as a battle" says (user's call,
  2026-11-24). The only change here is that its fighters don't heal while it's on
  (requirement 5).
- Whether a member short of health may be sent: allowed, as today (requirement 2). The
  question isn't answered here.
- A "full in N minutes" readout, a hall notice, or any other new UI beyond requirement
  20.
- Injury rules, injury healing, and the paid injury heal in the Dorms.

## Open Questions

- A member short of health is not the same as an injured one, and nothing says whether
  it holds them back. Can a member be sent on a dive or a mission while still short of
  health, or must they be whole first? *(Core Concept, Open Questions. The originals'
  owner hasn't answered; the build allows it, per requirement 2.)*
