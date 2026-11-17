# PRD: A close-range attack waits for its target to be home

> **Status:** Draft · Queue item #121 · Source docs read: Combat.md, EhrensDocs/Combat.md,
> EhrensDocs/Individual Types.md, Individual Types.md, EhrensDocs/Look and Feel.md (Characters
> and animations), the remaining design docs skimmed for same-tick order, ties and
> targetability. Current contract read from code: Core/Combat/Battle.cs, BattleSnapshot.cs,
> Core/BattleView/BattleController.cs, MeleeMotion.cs, MeleeMoves.cs, TurnPlayback.cs,
> BattleClock.cs, Game/Battle/BattleScreen.cs, BattleStage.cs, CombatantView.cs,
> Core/Save/SaveFile.cs, and the EditMode melee and lunging-target tests.

## Problem

The engine resolves an attack in the tick its cooldown comes up; the battle screen then walks
a close-range fighter out to its target's home node, plays the blows, and walks it back, which
takes over a second. Nothing stops the target from going out on a lunge of its own during that
time. When two fighters go for each other at once, each jumps to the other's empty node and
swings at thin air. The user, 2026-11-17: "this looks bad becase now a chracter is no longer in
their spot so the attacker is just attacking thin air."

## Goal

A close-range fighter never walks to a node its target has left. An attack whose target is out
on a lunge of its own waits until the target is home, and attacks that wait go in the order
they became ready. The rule lives in the engine, in ticks, so a headless `Battle.Run` and the
battle screen at x1, x2 or x3 play the same fight from the same seed.

## Terms

- **Mover**: a type the battle screen walks to its target: Brute, Tank, Fighter, Rogue, Cook,
  Porter (`MeleeMoves.Moves`). The Archer and the Mage never leave their node.
- **Lunge**: an action in which a mover lands or misses at least one strike of its own. A special
  that strikes no one (Vanish, Shields Up) is not a lunge (`BattleScreen.PlanMelee`).
- **Away**: a mover from the tick its lunge resolves until that lunge's away window ends.
- **Held attack**: a mover's action whose cooldown has come up, or whose free attack is owed,
  but which has not resolved yet because of R1 to R3 or R5. Nothing of it has resolved: no
  report, no field hit, no special decision, no roll but its target pick and any tie draw.
- **Ready tick**: the tick a held attack's cooldown came up, or its free attack was earned.

## Requirements

Source "User 2026-11-17" is the user's decision on queue item #121, which no design doc carries
yet (see the report). "Contract" means what the code does today and keeps doing.

### The rule

1. When a mover's attack is due, its target is picked as it is today: focus, taunt, weighted
   draw (EhrensDocs/Combat.md › What the targeting weights count; How a member with no target
   picks one). An away combatant stays pickable. If the picked target is away, the attack is
   held. *User 2026-11-17: "My vote is to wait," over making an attacker untargetable.* The
   pick uses the type's attack range, which is the same for its ordinary attack and its special
   (Contract: each `*Type.cs`), so it does not need the special decision (R11).
2. If the picked target is holding an attack of its own with an earlier place in the order
   (R6), the attack is held too. *User 2026-11-17: Char3, ready to attack Char2, waits while
   Char2 waits for Char1, and goes after Char2.*
3. **Default for now (Open Question 1).** A mover that is the target of a lunge still out
   (its attacker is away, and it was that lunge's first pick) holds its own attack until that
   attacker is home, whoever it was going to attack. *Proposed by the PRD author from the user's complaint: the
   attacker otherwise swings at an empty node.*
4. **Default for now (Open Question 2).** Only movers' attacks are held. An Archer's or a
   Mage's attack is made when due, also at an away target, and its shot follows the target
   as it does today (`BattleStageLungingTargetTests`, `BattleStageFireArrowTargetTests`). A
   ranged attack never holds anyone under R3.
5. **Default for now (Open Question 7).** A mover whose own cooldown comes up, or whose free
   attack is owed, while it is still away is held until it is home, through the same walk
   (R7). No mover lunges again from out of place, and a fast mover cannot stay away for good
   and keep the attackers waiting on it. This replaces today's chaining at the stop point
   (`MeleeMotion.PlanAction`, the "chained" case).

### Order

6. Every due or held attack's place in the order is a key, fixed when it falls due: ready tick
   ascending, then the holder's own Dexterity descending (as for its cooldown, EhrensDocs/
   Combat.md › How a cooldown rounds), then its tie draw ascending. *User 2026-11-17: "let
   time stamps of attacks deside what comes first … On ties the player with the higher dex
   goes first, if still a tie pick randomly."*
7. Each tick is one ordered walk, in key order, over every attack due that tick, of any type:
   the attacks already held and the cooldowns coming up this tick together. An earlier stamp
   always goes first, so attacks already held go before this tick's fresh cooldowns. A
   mover's attack first picks its target if it has none, or picks again if its target is dead,
   out of its reach or untargetable (R14); it then resolves unless R1 to R3 or R5 hold it, in
   which case it is held. An Archer's or Mage's attack resolves when walked (R4). A release
   that sends a mover out makes it away for the rest of the walk, so Char2 going out keeps
   Char3, aimed at Char2, waiting. A free attack earned in the walk resolves straight after
   the attack that earned it unless held (R5, R9); an attack held that way is first walked on
   the next tick. *User 2026-11-17: "let time stamps of attacks deside what comes first."*
8. The tie draw is one `IRng.NextInt(0, 1_000_000)`. Before the walk, every group of due or
   held attacks sharing a ready tick and a Dexterity gets one draw each, in today's fixed tie
   order (members before monsters, front row first, left to right; EhrensDocs/Combat.md › The
   clock, how a fight opens, and who goes first). It is drawn once and kept. Whether anyone in
   the group will be aimed at an away target cannot be known before the walk picks targets, so
   such groups always draw (R23). An attack held during the walk that ties with one already
   keyed gets its draw when it is held. Equal draws fall back to that fixed tie order. No other
   tie draw is made.
9. A free attack is held like any other, with the tick it was earned as its ready tick, and
   its owed flag stays set while held. Held, it no longer comes before everyone else in that
   tick. **Default for now (Open Question 6)**, against EhrensDocs/Combat.md › The free attack
   comes first.

### While an attack is held

10. Its cooldown stays come up and its cooldown bar shows full (`CooldownProgress` is 1). On
    screen the holder idles at its node. **Default for now (Open Question 3):** its next wait
    starts when the held attack is made, not when its cooldown came up.
11. The whole action resolves at release, as one report, exactly as a normal action does
    today: the field hit, the use-the-special question, the strikes and their weapon rolls,
    clearing the owed free attack. Arming or disarming a special during the hold counts at
    release. One report per action stays true (Contract: `Battle.Resolve`, `ActionReport`).
12. A lingering field it stands on hurts it at release, before the strikes, and a field hit
    that kills it means the attack is never made (EhrensDocs/Individual Types.md › Mage: "a
    character standing in the field takes damage from it when that character begins its own
    attack"; "the field's damage lands before the attack does").
13. The cycle count of its lasting effects, its Luck check and its new wait all happen when the
    held attack is made, not when it was held (EhrensDocs/Combat.md › When an effect's count
    starts: "the owner's next three attacks all happen under it").
14. The picked target stands while the attack is held. It is picked again, by the normal rule
    (`Battle.ChooseTarget`), only when the held target is dead (`Combatant.IsAlive`), is no
    longer in that attack's reach (`Battle.Reachable`), or is untargetable
    (`Battle.IsUntargetable`, Vanish). The new pick is subject to R1 to R3, and the attack
    keeps its key. **Default for now (Open Question 4):** marking a new focus during the hold does not
    change the held target. If the new pick finds no one, the action ends with no attack, as
    today when `ChooseTarget` finds no one.
15. A held attack is dropped when its holder dies or the battle ends.

### The away window

16. The engine keeps, for each combatant, the tick its away window ends, set when its lunge
    resolves and sized from the resolved action itself: its type, special or ordinary, how many
    strikes, the field and drink events before or between them, and the hops between targets.
    The sizing is one pure function in Core that `MeleeMotion`'s planner also uses, or that
    reads the same constants and clip timings the screen does, so the two cannot drift. It
    looks clips up through `CharacterArt.Has` / `TryClip`, never `Find`. Retiming a clip or a
    melee constant changes window lengths, and so changes a fight's outcome from the same seed.
    *Why in
    the engine: it resolves an action in one tick while the screen plays it over seconds
    (`BattleScreen.StartPlaying`), and the rule has to hold in a headless `Battle.Run` too
    (R21).*
17. A mover counts as home on its window-end tick. The window covers the walk the battle screen
    draws: for every mover type, ordinary and special, one strike and several, with hops and
    with field hits, the screen draws the mover home (`Motion.IsAway` false) on or before the
    window's end at x1, x2 and x3, and no more than a `Tuning` slack placeholder before it. The
    slack covers the screen starting an action up to a frame after the engine's tick, at x3.
18. Because of R5 no mover lunges while it is away, so a window is never extended.
19. A mover killed while away is no longer away; the screen leaves it where it fell, as today
    (`BattleScreen.FreezeMotion`).
20. On the battle screen at x1, x2 and x3, a held attacker released by its target coming home
    never starts its out leg before that target is drawn home, and the two are never both away
    lunging at each other. This replaces `BattleScreenMeleeTests.
    TwoFightersJumpingAtEachOtherEachStopAtTheOthersHomeNode_AndDoNotChase_Q77_Chase`, which
    pins the old behaviour.

### Determinism and saving

21. `Battle.Run`, `StepAction` and `AdvanceTicks` split any way, and the battle screen at any
    speed, give the same reports on the same ticks from the same seed and the same input.
    `StepAction` steps over a cooldown that is held and returns the next action that resolves;
    it stops on a window-end tick only when the walk there releases something (EhrensDocs/
    Combat.md › The clock: "the same fight with the same rolls plays out the same however that
    time is split up"; › The fight can be sped up).
22. A battle saved mid-fight and loaded plays the rest exactly as the uninterrupted battle
    would (Contract: `BattleSnapshot.cs`). The save holds the held attacks in the order they
    were held, each with its target, ready tick and tie draw (if any); for every combatant, its away-window end; and for each
    away mover, the first pick of its lunge (R3). The owed free attack is saved already and
    stays set while held. Nothing about the special is saved: it is decided at release, and the
    armed set is the controller's, as today. The save version goes to 11; a battle from version
    10 or older loads with no one held or away. A held attack by or at a dead combatant, or a
    negative window, is a corrupt save, as `Restore`'s existing checks are.
23. A battle in which no attack is ever held plays as today, with two differences. First, a
    mover now draws its target before a lingering field it stands on rolls the victim's armour,
    because the pick decides whether it holds (R1) and nothing may resolve before that (R11).
    If that field hit kills it, the target draw has still been made, and a taunt the pick used
    is still spent. Second, cooldowns that come up on the same tick with equal Dexterity always
    make tie draws (R8) and go in the drawn order, no longer members before monsters, front row
    first, left to right. The existing engine tests stay green, apart from any that pin either
    order and the one in R20.

## Out of Scope

- Ranged attackers waiting, unless Open Question 2 is answered otherwise.
- The hop targets of a lunge that moves on when its target dies (the Fighter's flurry
  `Nearest`), and a Brute special's other targets: only the first pick is checked against R1
  to R3.
- Two movers lunging at the same target at once; they already stop at the same point.
- A held attack that turns out at release to be a special striking no one (Vanish, Shields
  Up) has still waited; the special is not known until release (R11).
- Any on-screen cue that an attack is waiting.
- What the screen draws right after a load: everyone home, as today, while the engine's
  windows run out.

## Open Questions

1. When a fighter is already on its way to hit someone, and that someone's own turn comes up
   to attack a third character, should it stay put until the hit lands and the attacker is
   back? Going ahead with: yes, it waits (R3).
2. Should an Archer or a Mage also wait to shoot someone who is out on a lunge, or shoot them
   where they are, the arrow following them as it does now? Going ahead with: shoot them where
   they are (R4).
3. A waiting fighter's next cooldown: does it start when it finally attacks (waiting costs it
   time) or from when it became ready (it catches up)? Going ahead with: when it attacks (R10).
4. If the player marks a new focus target while a member is waiting to attack, does it switch
   to the new target? Going ahead with: no, it keeps the one it picked (R14).
5. The user's tie rule ("higher dex goes first, if still a tie pick randomly"): does it replace
   the current order for every set of cooldowns that come up on the same tick — which is
   members before monsters, front row first, left to right, and never random — or only order
   attacks that are waiting? Going ahead with: it replaces it for every attack that falls due,
   waiting or not (R7, R8, R23). Combat.md's own open question, "who goes first?", stays
   open in the doc.
6. A free attack from the Luck reset comes "in the same tick, before anyone else acts". When
   its target is out on a lunge, does it wait like any other attack? Going ahead with: yes
   (R9).
7. A fast fighter can be ready to attack again before it has walked home from its last attack,
   and a lucky one gets a free attack straight away. Today it attacks again from where it
   stands. Should it walk home first and then go out again? Going ahead with: yes, it goes home
   first, the free attack included, so no one is left waiting on a fighter that never comes
   back (R5).
