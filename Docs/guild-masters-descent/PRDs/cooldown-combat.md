# PRD: Real-time cooldown combat

> **Status:** Draft · Source docs read: `Combat.md`, `Core Concept.md`, `Equipment.md`,
> `Guild Members.md`, `Individual Types.md`, `Specialists.md`, `The Dungeon.md`, and the
> change notes of the same names under `EhrensDocs/`, plus `EhrensDocs/Platform.md` (a new
> doc, no original). Where an original and a change note disagree, the original wins (the
> user, 2026-11-12, in `queue/focus.md`). Built code read: `Core/Combat`, `Core/BattleView`,
> `Game/Battle`, `Core/Dungeon/Dive*.cs`, `Core/Save`, and their EditMode tests.

## Problem

Combat today is turn-based: everyone acts once a round, fastest Dexterity first, and the
battle screen stops on each member's turn until the player presses Attack. A battle ends as
a stand-off after 50 rounds. The originals say combat is not turn-based: every fighter acts
on its own cooldown and the fight never waits for the player. The lasting effects, the Mage's
field and the mid-battle save are all counted in turns, so they change with it, and the Luck
reset is not built at all.

## Goal

A battle runs on its own from start to finish on a tick clock: each member, specialist and
monster attacks whenever its own Dexterity-set cooldown comes up, sometimes gets a free
attack from the Luck reset, and lasting effects and the Mage's field count in their owners'
and victims' cooldowns, not turns. The player watches and can still mark a focus target.
The simulation is driven only by ticks, so a test can run it without real time. Closing the
game mid-battle and reopening it resumes the fight exactly, and older saves still load.

## Requirements

Requirements marked **[Default]** are not from the docs. Each stands in for an unanswered
question listed under Open Questions so the build can go ahead. It is a placeholder rule,
and changing it later should be a small, local change.

### The clock

1. A battle is simulated in ticks of 50 ms, twenty a second. Every count the simulation
   keeps (a wait, time elapsed, an effect's cycles) is a whole number. The tick length is
   settled, not a placeholder. — `Combat.md` § Cooldowns.
2. The engine only moves forward when it is told to advance a number of ticks. It never
   reads the frame rate or the clock. Take two battles with the same state and the same RNG
   state, and advance both by the same total number of ticks, in one call or in many. They
   must play the same, strike for strike and roll for roll. — `Combat.md` § Cooldowns (the
   fight is simulated in discrete ticks, and the ticks are never drawn);
   `EhrensDocs/Platform.md` § Saving (the rest of a battle plays out "exactly as it would
   have … the same rolls and all").
3. Rounds and turns are gone. There is no round counter, no per-round turn queue, and no
   Dexterity-ordered round. This replaces the built `StepTurn`, `RoundOrder`, `NextActor`,
   `PlayRound`, `Run`'s round loop, `Round`, `Turns`, `LastTurn` and `TurnReport`. —
   `Combat.md` § Cooldowns ("Combat is not turn-based").
3a. The engine has two ways to move forward, and nothing else advances it (technical
   decision, main loop):
   - **Advance by ticks.** `AdvanceTicks(n)` advances up to *n* ticks, or fewer if the
     battle ends first. It returns the reports of every action resolved, in the order they
     were resolved.
   - **Advance by one action.** A single-action step moves the clock forward to the next
     action that is due and resolves that one action only. Anything else due on the same
     tick stays pending for the next call, which resolves it without advancing the clock.
     A Luck-reset free attack is its own action, so it is the next call's result. The step
     returns that action's report. It returns nothing once the battle is over, and if the
     stand-off cap (R25) comes before the next action, it advances to the cap and ends the
     battle.
   - Either way, the same state and RNG resolve the same actions with the same rolls. R2
     applies across any mix of the two.
   - `Run()` stays as "step until over".
3b. Each action produces one **action report**. It holds the actor, the tick it resolved
   on, whether it was a Luck-reset free attack, whether it was a special, the field hits
   the action set off (R18, including one that killed the actor before it struck), and the
   strikes it made. The battle keeps every report, oldest first, in place of `Turns` and
   `LastTurn`; that list is not saved, as `Turns` isn't today. `Strikes` stays as built,
   and it is still saved. A move (`Move`) is not an action. The field hit a move into a
   field sets off is returned by that `Move` call and added to the battle's field-hit
   record, so a caller can show it.
3c. Tick counting: a battle stands at tick 0 when it is built. Advancing one tick moves it
   to tick T+1 and resolves everything due at T+1. An action that resolves at tick T and
   then starts a wait of W next acts at tick T+W, so a wait of W resolves on the W-th tick
   advanced after it starts. A remaining wait is stored as the ticks left until that
   combatant is due. A remaining wait of 0 is valid only for a combatant that is due on
   the current tick and has not been resolved yet. That state exists only between two
   single-action steps on one tick.
3d. The dive drives a battle through the same two ways. `Dive.StepTurn` is replaced by
   dive-level equivalents of the single-action step and of advancing by ticks. They take
   in a finished battle the same way `StepTurn` does today.

### Cooldowns

4. Every combatant has its own cooldown: party members, specialists and monsters alike.
   When the cooldown comes up, the combatant acts and a new wait begins. — `Combat.md`
   § Cooldowns, § Specialists in Combat, § Enemies.
5. The wait is the type's base ÷ (1 + Dexterity ÷ 20), rounded to the **nearest** whole
   tick, with an exact half rounding **up**. It never goes below a tenth of the base. It is
   computed in integers, never in floating point:
   W = max(⌊base ÷ 10⌋, ⌊(40 × base + 20 + Dex) ÷ (2 × (20 + Dex))⌋). That expression is
   20 × base ÷ (20 + Dex), rounded half up. So every type at Dexterity 12 rounds up: a Rogue
   waits 63, not 62.5, and not the 62 that C#'s round-half-to-even would give. The
   half-up rule is a technical decision, because the docs say only "rounded to whole
   ticks". The bases are Brute and Tank 180, Fighter
   and Mage 140, Rogue and Archer 100. These numbers are settled, not placeholders. Check
   values: a Rogue at Dexterity 5 waits 80, at 20 waits 50, at 80 waits 20, and at 180 or
   more waits 10. A Fighter at Dexterity 7 waits 104: 103.7 rounds up, which is why this is
   nearest and not down. A Tank at Dexterity 6 waits 138. — `Combat.md` § Cooldowns (formula,
   floor, and both worked lists).
   *Note:* the two worked lists in that section disagree, and the formula is what binds.
   The first list puts a new F-rank Rogue at Dexterity 5, which gives 80. The second gives
   "the same" new recruits 71 / 104 / 138. That only fits the formula with a different
   Dexterity for each type (Rogue 8, Fighter 7, Tank 6), and no common value works. The
   build's F-rank starting Dexterity is Rogue 6, Fighter 5, Tank 4, which matches neither
   list. Tests assert the formula and do not assert either list's "new recruit" figures.
6. A specialist's base wait is a placeholder in the tuning file; the build uses 180, the
   slowest base. The formula and the tenth-of-base floor apply to it as to any type. —
   `Combat.md` § Specialists in Combat says a specialist attacks on its own cooldown but
   gives no base. Per `queue/focus.md`, a missing number gets a placeholder.
7. **[Default]** The Dexterity in the formula is the combatant's own stat. Support-ring help
   does not count, which is how the turn order is built today. This stands in for "Should
   help to a Rogue's or an Archer's Dexterity shorten its cooldown?"
8. **[Default]** Where each cooldown starts is a tuning placeholder: each combatant begins
   the fight with a random share of its first wait already gone, drawn from the battle's
   RNG. The share lies between a placeholder minimum and maximum, and the build uses 0 to ½.
   Setting both to 0 gives "everyone's empty", and both to 1 gives "everyone's ready at
   once". This stands in for the `Combat.md` open question on where cooldowns stand when a
   fight starts. How the draw is made (technical decision, main loop):
   - It happens when the combatant is added (`AddMember`, `AddMonster`), immediately after
     that combatant's own existing draws. A monster's level-up stat picks come first, and a
     member has none. So the draws run in add order.
   - With W the combatant's wait (R5), the draw is
     `elapsed = NextInt(⌊min × W⌋, ⌊max × W⌋ + 1)`, and the remaining wait is
     `max(1, W − elapsed)`. A remaining wait of 1 acts on the first tick advanced.
   - A draw is made even when min = max, so retuning the share never shifts the rest of
     the RNG sequence.
   - Restoring a battle from a save draws nothing.
   - The opening waits are therefore part of the battle's state from tick 0, and R33
     saves them like any other remaining wait.
9. **[Default]** When several cooldowns come up on the same tick, they act one after another
   in the built tie order: higher Dexterity first, then members before monsters, then front
   row first, then left to right. A combatant killed earlier in that tick does not act.
   Nothing in this ordering is random.
10. **[Default]** All the strikes of a multi-strike attack resolve on the tick the cooldown
    comes up, each still rolled on its own, as built. This stands in for "When a member's
    cooldown comes up, do all the strikes of a multi-strike attack resolve at once?"

### The Luck reset

11. After an attack that a cooldown brought round, the attacker makes a Luck check. The
    chance is 25% × Luck ÷ (Luck + 60). The chance is not rounded to a whole percent: Luck 5
    is 1.92%, not 2%. Members, specialists and monsters all make the check, on the same
    terms. — `Combat.md` § The Luck Reset; § Enemies (depth leaves enemies' Luck untouched).
    How the roll is made (technical decision, main loop):
    - It is exact, in integers: success is `NextInt(0, 4 × (Luck + 60)) < Luck`, where Luck
      is the attacker's own Luck stat.
    - It is drawn after all of that attack's other draws.
    - It is drawn even at Luck 0, where it always fails, so the RNG sequence does not
      depend on Luck being 0.
    - An action that makes no attack makes no check: one whose actor the field killed
      first (R20), and a special (R14).
12. On a success the attacker makes a free attack at once: on the same tick, before any
    other combatant acts. The free attack is the type's ordinary attack, never its special.
    It is ordinary in every other way too. Its strikes land on their own rolls, it spends
    durability per hit, it charges the bar, it can taunt, and it can set off the Mage's
    field (R18). It gets no Luck check of its own. — `Combat.md` § The Luck Reset ("attacks
    again immediately", "an ordinary attack in every way", "gets no Luck check of its own").
13. After the free attack, or after a failed check, the full wait begins as normal. The
    attack at the end of that wait is eligible for a check again. — `Combat.md` § The Luck
    Reset.
14. **[Default]** A special gets no Luck check. This stands in for the question below on
    whether a special is "an attack" for the reset.

### Lasting effects

15. Vanish, Shields Up and the Mage's field each last three of their owner's cooldown
    cycles, and the cycle the effect is cast in does not count. Read literally, the effect
    is live from the moment it is cast until the owner's third cooldown after the cast has
    come up and that action has resolved. Then it ends. So the owner's next three actions
    all happen under it: a vanished Rogue makes three auto-hitting attacks. This replaces
    the built count, which ends the effect at the *start* of the caster's fourth turn after
    the cast. — `Combat.md` § Lasting Effects; `EhrensDocs/Combat.md` "When an effect's
    count starts, and a second cast stacking". The end point is a reading; see Open
    Questions.
16. **[Default]** A free attack from the Luck reset does not count as one of the owner's
    cycles. Only a cooldown that comes up after a wait counts.
17. These stay as built and are unchanged here: an effect ends when its owner dies; a second
    Shields Up or field stacks with the first; the field outlives the enemy it was aimed at.
    — `Combat.md` § Lasting Effects; `EhrensDocs/Combat.md`; `EhrensDocs/Individual Types.md`
    "Where the Mage's field lies, and what it does, for now".

### The Mage's field

18. The field no longer deals damage when the caster's own turn starts. It hurts a character
    on the side it lies on in two cases. One is each time that character begins an attack
    while standing on a covered node, and a Luck-reset free attack counts. The other is when
    that character moves from an uncovered node to a covered one. Attacking into the field
    from outside does nothing. A character already on a covered node when the field is cast
    takes nothing until it begins an attack. — `Individual Types.md` § The Mage;
    `EhrensDocs/Individual Types.md` "Where the Mage's field lies …". This replaces the
    built field damage in `TickEffects`.
19. These are unchanged: how much the field does (fixed at the cast), no hit roll, its
    damage counting toward the caster's damage dealt, and hurting a vanished Rogue without
    ending its Vanish. — `EhrensDocs/Individual Types.md`, same change;
    `EhrensDocs/Combat.md` "What the targeting weights count …".
20. **[Default]** The field's damage lands before the attack. If it kills, that character
    makes no attack and no Luck check.
21. **[Default]** A special counts as beginning an attack, including one that strikes no one
    (Vanish, Shields Up).
22. **[Default]** The field is live from the moment it is cast. A character on a covered node
    that begins an attack later on the same tick takes the damage.
23. **[Default]** The Brute's special, which pushes past the front row and returns "in the
    same action", does not count as moving: its node never changes.

### Specials

24. This item does not change when a special happens. A combatant with a full bar uses its
    special in place of its ordinary attack when its cooldown comes up. A monster always
    does. A member does only if the engine's existing hook asks it to. Bars, charge and
    waste are unchanged. — as built; `EhrensDocs/The Dungeon.md` "The dungeon's enemies are
    monsters" ("a monster uses its special as soon as its bar is full"). This will change
    when the special-timing question below is answered.

### How a battle ends

25. A battle ends the moment one side has no one left standing, as built. It also ends as a
    stand-off once it has run a set number of ticks. That number is a placeholder in the
    tuning file and replaces the built 50-round cap; the build uses 6,000 ticks, five
    minutes. A stand-off kills no one further, and the dive treats it as turning back, as
    built. — `EhrensDocs/Combat.md` "How a member with no target picks one, and how a
    battle ends"; `EhrensDocs/The Dungeon.md` "A party can turn back anywhere …".
26. **[Default]** Actions due on the cap's last tick are played. The battle is a stand-off
    only if both sides still stand after them.
27. Auto-selected attacks, the party's focus target, the no-target pick, taunts and the
    targeting weights are unchanged. — `Combat.md` § Player Input;
    `EhrensDocs/Combat.md`.

### The battle screen

28. Nothing waits for the player. The Attack button is gone, nothing is highlighted as
    "whose turn", and the header no longer names an actor. The fight starts ticking when
    the battle screen shows and runs to its result. — `Combat.md` § Player Input ("The fight
    never pauses, and nothing waits for the player").
29. Tapping an enemy to set or clear the focus works at any time, as built. —
    `Combat.md` § Player Input.
30. The battle is driven by real time, through the presenter. `BattleController` is the
    only caller of `AdvanceTicks` while a screen shows a battle. Each frame the screen hands
    it the seconds elapsed. The controller turns them into whole ticks at 20 a second,
    carries the leftover fraction to the next call, calls `AdvanceTicks` with the whole
    ticks, and returns the action reports.
    - The screen starts drawing each returned report on the frame it is returned. Reports
      from different actors play at the same time rather than queuing, so the picture never
      falls further and further behind the fight.
    - The engine never waits for an animation. `TurnPlayback` is built from an action
      report instead of a turn report. The controller's turn phases (`AwaitingPlayer`,
      `AutoTurn`), `ChooseAttack`, `ChooseSpecial` and `StepAuto` go. `Over`, `Result`,
      `Focus` and `TapEnemy` stay.
    - The controller is Core code, so all of this is testable with made-up seconds and no
      Unity time.
    - Sources: `Combat.md` § Cooldowns ("What the player watches is continuous motion"),
      § Player Input (the player acts while it runs); `EhrensDocs/Platform.md` § Saving
      ("An attack already made counts as made, even if it hadn't finished showing on
      screen").
31. Time the game spends closed or in the background advances no ticks. A battle picks up
    at the tick where it stopped. — `Core Concept.md` § Time ("A dive in progress … doesn't
    advance while the game is closed"). To make that hold however a platform reports a gap
    (technical decision), one controller call feeds at most a placeholder number of
    seconds. The build uses 0.25 s, which is 5 ticks, and drops the rest along with the
    carried fraction. So a return from the background, or a long hitch, never fast-forwards
    the fight.
32. **[Default]** For this item, members' specials cannot be used from the screen, and the
    Special button is removed along with Attack. A member's bar fills and sits full. The
    engine keeps the hook from R24, so the later item that adds specials to the screen only
    needs to wire it up.

### The mid-battle save

33. A save made during a battle catches it between two actions. That is usually between
    ticks, but it can be between two single-action steps on one tick. Loading it plays the
    rest of the battle exactly as an uninterrupted battle would have, roll for roll.
    - On top of what is saved today, the save holds the current tick and each combatant's
      remaining wait (R3c; 0 means due on this tick and not yet resolved). It holds whether
      a combatant is owed a Luck-reset free attack it hasn't made yet, and each effect's
      cycles counted (R15, R16).
    - That list is complete. The opening waits are drawn when combatants are added (R8), so
      they are saved remaining waits like any other. Restoring draws nothing.
    - The round, the turn queue and `TurnsStarted` are no longer written.
    - Sources: `Core Concept.md` § Time; `EhrensDocs/Platform.md` § Saving.
34. The save format moves to version 3. Version 1 and version 2 saves still load, and
    loading never rewrites the slot. A version 3 battle that can't be true whatever the
    tuning loads as corrupt and leaves the slot alone, like every other corrupt save. That
    means a negative tick, a negative remaining wait, negative cycles counted, a list whose
    count doesn't match the combatants, or a free attack owed to someone dead or to someone
    not due on the current tick. Nothing is checked against a bound that comes from a
    tuning placeholder: a remaining wait longer than the combatant's computed wait is
    accepted. — `EhrensDocs/Platform.md` § Saving.
35. **[Default]** A version 2 save made mid-battle cannot resume exactly, because it holds
    rounds, not cooldowns. It loads keeping everything it holds: who has died, health,
    bars, effects, taunts and focus.
    - Each effect's built `TurnsStarted` = k becomes cycles counted = min(k, 2). That leaves
      max(1, 3 − k) cycles, so an effect that was live is never loaded as already ended.
    - Each living combatant's remaining wait is its full wait W (R5), with no draw, so
      loading stays roll-free.
    - The current tick starts at 0, and no free attack is owed.
    - A version 2 save made between battles loads as it is.
    - Pins to change with the version: `SaveFormatTests` and `GuildDungeonTests` assert
      `CurrentVersion == 2`.

### Built tests this supersedes

Order of work (technical decision, main loop): `forge-test-author` ports every file below
onto the API in R3a–R3d **before** `forge-code-writer` removes the old one. Most ports are
mechanical: a kit's `Turn()` becomes one single-action step, and `Round()` becomes "step
until each living combatant has acted once".

This list is complete as of this PRD. It was found by grepping `Assets/` for `StepTurn`,
`PlayRound`, `NextActor`, `.Round`, `Round()`, `Turn()`, `Turns`, `LastTurn`,
`TurnReport`, `BattlePhase`, `ChooseAttack`, `StepAuto`, `BattleRoundCap`, `EffectTurns`,
`TurnsStarted`, `Run()` and `CurrentVersion`.

**Retired, or rewritten against the new rules.** These assert rounds, turn order, turn
phases, or turn-counted effects:

- `CombatTurnOrderTests`
- `CombatResultTests`: the round cap becomes the tick cap (R25, R26), and the placeholder
  names change
- `BattleControllerTests`: phases, Attack and Special, armed specials
- `BattleTurnReportTests`, which becomes action-report tests (R3b)
- `TurnPlaybackTests`
- `BattleScreenTests`
- the turn-counted effect tests in `CombatContractTests`, `CombatTypeContractReachTests`,
  `CombatTypesSharedTests` and `CombatMageTests`, including the field's "whoever stands in
  it that turn" test (R18)
- `DiveResumeTests`: the round and whose-turn assertions, and save/load after each action

**Ported mechanically.** These use the removed stepping but assert unchanged rules:

- `CombatStrikeTests`, `CombatTargetingTests`, `CombatSpecialBarTests`, `CombatGearWearTests`
- `CombatSupportRingTests`, `CombatTypeAdvantageTests`, `CombatCombatantTests`
- `CombatTypeEngineHookTests`, `CombatSpecialistTypeTests`
- `CombatArcherTests`, `CombatBruteTests`, `CombatFighterTests`, `CombatRogueTests`,
  `CombatTankTests`
- `DemoEncounterTests`, `BootScreenTests` (`battle.Turns.Count`), `DiveSaveTests`
  (`Dive.StepTurn`)

**Kits:** `CombatTypesTestKit` (`Turn`, `Round`, `TypeKit.Turns`), `BattleViewTestKit`,
`DiveRunTestKit` (`dive.StepTurn`, and its `CurrentVersion == 2` note). Every Dive test
that drives battles through `DiveRunTestKit` is covered by porting the kit.

**Version pins:** `SaveFormatTests` and `GuildDungeonTests` (R35).

**Scripted RNG.** Every battle now makes one extra draw per combatant added (R8) and one
after every attack (R11). Any test that scripts rolls through `CombatTestKit`'s `RoutedRng`
or a queued RNG must account for those draws. Their ranges can coincide with the ranges of
other rolls.

**Non-test code** that uses the removed API, for `forge-code-writer`:

- `Battle.cs`, `BattleSnapshot.cs`, `TurnReport.cs`
- `BattleController.cs`, `TurnPlayback.cs`, `BattleScreen.cs`
- `Dive.cs`, `DiveSave.cs`, `Tuning.cs`
- `Editor/MenuScreenshots.cs` and `Editor/BattleScreenshot.cs`, which press Attack on
  `AwaitingPlayer` and call `StepTurn`

## Out of Scope

- Damage math, type-advantage rules, strikes per attack and flurry length. That is the next
  queued item.
- How the special bar charges and carries between battles; the screen's live specials;
  formation changes on the screen; enemies repositioning.
- Health from Constitution, healing, gear and durability bands, experience, and enemy
  generation.
- Speeding a fight up or slowing it down.
- How actions look on screen beyond R28–R32, such as animation timing and overlap within one
  combatant. That is a look item after this one.

## Open Questions

From the design docs, worded as they word them:

- When a fight starts, where do the cooldowns stand — everyone's empty and waiting out a
  full first wait, everyone's ready at once, or staggered somehow? The opening of a fight
  plays out completely differently depending on which. (`Combat.md`; R8 is the stand-in.
  Research item #63 asks the same thing as its first question.)
- When a member's cooldown comes up, do all the strikes of a multi-strike attack resolve
  at once? (`Combat.md`; R10.)
- Should help to a Rogue's or an Archer's Dexterity shorten its cooldown?
  (`EhrensDocs/Combat.md`; R7.)
- When a Rogue casts Vanish, a Tank uses Shields Up or a Mage casts its field, does that
  cost it an ordinary attack, or does its cooldown run on untouched? (`EhrensDocs/Combat.md`;
  R24 keeps it as built: the special replaces the attack its cooldown brought.)
- Can the player speed a fight up or slow it down, and does that change anything in the
  simulation or only how fast it's drawn? (`Combat.md`; out of scope, but R2 keeps either
  answer cheap.)
- At F rank a member's Luck is single-digit, which puts the reset chance near one attack
  in forty — a member might see one reset in a whole dive. Is the reset meant to be that
  close to absent early on, or should the curve start higher? (`Combat.md`.)

Raised by this PRD. These are proposals of mine; none of them is in the docs:

- When several cooldowns come up on the same tick, who goes first? (R9.)
- Does a Luck-reset free attack count as one of the owner's three cycles for a lasting
  effect? (R16.)
- Is a special "an attack" for the Luck reset? (R14.)
- Does a lasting effect end once the owner's third cooldown after the cast has resolved,
  or at the start of its fourth, as the turn-based build did? The second keeps Shields Up
  on the allies for one more of the Tank's waits. (R15.)
- If the field's damage kills a character as it begins its attack, does that attack still
  happen? (R20.)
- Does a special count as "beginning its own attack" for the field, including one that
  strikes no one? (R21.)
- Does a character in the field take its damage when it begins an attack on the same tick
  the field is cast? (R22.)
- Does the Brute's push past the front row count as moving into a field? (R23.)
- What base wait does a specialist have? (R6; a placeholder for now.)
- Are actions due on the stand-off's last tick played? (R26.)
- Until the battle screen gets live specials, can members use their specials at all? (R32.)
- A version 2 save made mid-battle can't resume exactly. Is keeping its state and
  restarting its cooldowns right, or should it do something else? (R35.)
