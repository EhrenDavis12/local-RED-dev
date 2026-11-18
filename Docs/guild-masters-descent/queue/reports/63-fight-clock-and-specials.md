# How a real-time fight's clock starts, and where a special falls on it

> **Status:** Research for queue item #63, 2026-11-12. Three decisions for the user. Nothing
> here is settled until the user answers; the answers land in the design docs through the
> tidy pipeline.

## Why this matters now

The originals make combat real-time: every fighter runs its own cooldown, counted in 50 ms
ticks, and the fight never pauses (Combat.md, Cooldowns and Player Input). The engine built
so far (#33, #34) is still turn-based — rounds, fastest Dexterity first, and a special is
asked for on the member's turn and *replaces* that turn's ordinary attack
(`Assets/Scripts/Core/Combat/Battle.cs`, `TakeTurn`). Queue items #50 (cooldown combat) and
#58 (using specials live) can't be specified until these three are decided.

What the docs already say that bears on them:

- Cooldowns: base wait per type (Brute/Tank 180 ticks, Fighter/Mage 140, Rogue/Archer 100)
  ÷ (1 + Dexterity ÷ 20). At F rank that is about 3.6 s for a Rogue, 5.2 s for a Fighter,
  6.9 s for a Tank.
- Individual Types.md, the Fighter: "Each time the Fighter's cooldown comes up, it makes one
  ordinary attack, like any other type — its two strikes all belong to that single attack."
- Combat.md: "Each strike of a multi-strike attack is resolved on its own: it rolls to hit
  separately, and the defender's mitigation is applied to it separately."
- Combat.md, Player Input: "The fight doesn't wait for the player, so the moment to use a
  special goes by while the fight carries on around it."
- Lasting effects run for three of the owner's own cooldown cycles.

## 1. Where the cooldowns stand when a fight starts

The originals ask this themselves: "everyone's empty and waiting out a full first wait,
everyone's ready at once, or staggered somehow?"

| Option | What the player sees | Catch |
|---|---|---|
| **Empty, full first wait** | Nothing happens for ~3.6 s; then the Rogues and Archers fire, the Fighters and Mages at ~5 s, the Tanks and Brutes at ~7 s. | A dead opening every fight, and the same type always strikes first. With 2–3 fights a floor this is felt many times a dive. |
| **Everyone ready at once** | Every member and enemy attacks on the first tick — up to 30 attacks at once. | A burst nobody can read, and the outcome of the opening is decided before the player can touch anything. Needs a tie-break order. |
| **Staggered: each starts part-way through its first wait** | First blows land within a second or so, then the rhythm settles into each type's own pace. | One extra tuning number (how far in each fighter may start). The start is a roll, so two identical fights open differently. |

Genre precedent: Final Fantasy's Active Time Battle games start gauges part-filled rather
than all empty or all full, and treat a full-gauge start as a special bonus (FF8's
Initiative ability, preemptive strikes in FF13). That's the staggered option, with "full at
the start" reserved as a reward.

**Recommendation: staggered** — each fighter, member and enemy alike, starts a random
amount of the way into its first wait, up to half of it. It removes the dead opening
without the opening burst, keeps fast types generally first, and leaves "starts ready" free
as a future reward (a scout, a surprise attack). **Cheap to change later** — it is one
placeholder in the tuning file and touches no save data.

## 2. Do all strikes of a multi-strike attack resolve at once?

Covers the Fighter's and the Rogue's two-strike ordinary attacks and the Fighter's 4–6
strike flurry.

| Option | What the player sees | Catch |
|---|---|---|
| **All on the same tick, drawn in quick succession** | The strikes play one after another over a fraction of a second, but the outcome is decided the moment the cooldown comes up. | None in the rules — it matches "its two strikes all belong to that single attack". |
| **Spaced out over several ticks** | Same on screen. | The target can die, move, or Vanish between strikes, and other fighters can act in the middle of one attack; each of those needs its own rule. The flurry's "carry to the nearest enemy" already covers a target dying mid-attack, so it works either way. |

**Recommendation: all on the same tick in the simulation**, each strike still rolled on its
own as the docs say, with the animation spacing them out. It is what the Fighter's
description already reads as, and it adds no new edge cases. **Cheap to change later** for
how it looks; moderate if the simulation is later spaced out, because each mid-attack case
then needs a rule and tests.

## 3. A special the player taps — at once or on the next cooldown, and does it use up the cooldown?

| Option | What the player sees | Catch |
|---|---|---|
| **A. Fires at once; the cooldown runs on untouched** | The tap is an instant extra attack on top of the member's normal rhythm. | A special is pure bonus damage, so there's never a reason to hold it except to aim it. |
| **B. Fires at once; the cooldown restarts from empty** | Instant response to the tap; the member's next ordinary attack is a full wait later. | Using it the instant before an ordinary attack would have landed wastes most of a wait — a small timing skill, or a small annoyance. |
| **C. Waits for the next cooldown and replaces that ordinary attack** (how the engine works now) | The tap "arms" the special; it goes off up to ~7 s later for a Tank. | On a phone a tap that does nothing visible for seconds reads as broken, and by then the moment the tap was for (enemies bunched for a Volley, a member about to die for Shields Up) may have passed. |

The docs lean toward the tap being a moment: "the moment to use a special goes by while the
fight carries on around it" only holds if the special lands when the player taps.

**Recommendation: B — it fires the moment it's tapped and restarts that member's cooldown.**
It answers the tap at once, which is what the docs' wording implies and what a phone needs,
and the restart keeps a special a choice instead of free damage. A follow-on default under B:
the special gets no Luck reset check of its own (the reset is described for "an attack", and
a reset straight after a special would make it free again) — flagged, not decided.
**Moderately cheap to change later**: it is a rule in the engine with tests on it, so before
#50 and #58 are built it costs nothing, and after them it costs rewriting those tests.

## Contradictions with the docs

None. Combat.md's Status line lists "how multi-strike cases resolve" as unsettled and its
Open Questions holds questions 1 and 2 word for word; EhrensDocs/Combat.md already asks a
narrower form of question 3 ("does that cost it an ordinary attack, or does its cooldown
run on untouched?") for the three effect specials.

## Sources

- `Docs/guild-masters-descent/Combat.md` — Cooldowns, The Luck Reset, Player Input, Attacks
  and Reach, Lasting Effects, Open Questions.
- `Docs/guild-masters-descent/Individual Types.md` — the Fighter.
- `Docs/guild-masters-descent/EhrensDocs/Combat.md` — "Questions on specials, taunts and the
  dive".
- `src/guildmasters-descent/Assets/Scripts/Core/Combat/Battle.cs` — `StepTurn`, `TakeTurn`.
- [Initiative (Final Fantasy VIII), Final Fantasy Wiki](https://finalfantasy.fandom.com/wiki/Initiative_(Final_Fantasy_VIII))
  — starting a battle with a full gauge is a special ability, not the default.
- [Battles, FF8 speedrunning wiki](https://ff8.wiki/wiki/Battles) — the starting gauge value
  changes with first strike or back attack.
- [Preemptive Strikes, Final Fantasy XIII (Jegged)](https://jegged.com/Games/Final-Fantasy-XIII/Tips-and-Tricks/Basic/Preemptive-Strikes.html)
  — a full start as the reward for a preemptive strike.
- [Active Time Battle, Giant Bomb](https://giantbomb.com/wiki/Concepts/Active_Time_Battle)
  — the genre's general shape.
