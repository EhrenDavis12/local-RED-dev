# Attacks that come up on the same tick, other than two close-range fighters

> **Status:** Research for queue item #145, 2026-11-18. Three decisions for the user;
> nothing here is settled until they answer. Sources are the docs' owner's original
> `Combat.md` (Cooldowns), EhrensDocs `Combat.md` ("Close-range fighters take turns on the
> same tick, for now" and the battle-end change), report #128, and the combat engine on
> `queue/build` in `src/guildmasters-descent` (`Assets/Scripts/Core/Combat/Battle.Walk.cs`,
> `Battle.cs`).

## The gap

The originals: "When more than one combatant's cooldown comes up on the same tick, their
attacks all happen at the same time — there's no order between them, and nothing resolves
first. Damage is worked out against where things stood at the start of that tick, so a
combatant that dies on that tick still lands the attack it made on it, and two combatants
can kill each other on the same tick."

The user's 17 Nov ruling ("B my rules for now. as it looks bad otherwise") covered only
close-range fighters: two who pick each other take turns, and one whose target heads off
waits for it to come home. Everything else on a shared tick was never asked: two Archers
shooting each other, a Mage and an Archer, a shot at a fighter heading out, two members
hitting one enemy, a fighter walking up to an Archer who shoots it as it comes.

## What the code does today

Every attack that comes up on a tick goes in turn: the one that became ready first, then
the higher Dexterity, then a random draw (`Battle.Walk.cs`, `Order`). Each attack is
resolved against the fight as it stands after the attacks before it:

- An attacker killed earlier in the tick never attacks (`NextAction` drops it).
- A second attacker whose target died earlier in the tick picks a fresh living target.
- The battle ends the moment one side has no one standing, mid-tick, so the last member
  and the last enemy can never kill each other.

The mid-battle save (`BattleSnapshot`) stores the held attacks in that order, and the
battle screen steps one action at a time (`StepAction`). That is why following the
originals is an [L] build: the engine's core step and the save both change.

## Decision 1: everything else on a shared tick

**Option A — all at once, as the originals say (recommended).** Every same-tick attack
except the close-range cases the user already ruled on is worked out against the start of
the tick. Two Archers who shoot each other both hit; one that dies still fires. The
picture problem behind the 17 Nov ruling does not arise here — a shot follows its target
wherever it is, and a fighter walking up to an Archer has someone standing in the spot to
hit. Cost: the [L] engine and save build. It also brings in Decisions 2 and 3.

**Option B — keep today's turn order for every attack.** Already built, nothing to do,
and one rule for close and ranged alike. But it keeps an order the originals say does not
exist, a faster Archer can kill a slower one before it shoots, and two sides can never
trade final blows.

Changing later: B to A is the same [L] build whenever it happens; it only grows a little as
more rules get built on top of the order. A to B is cheap to state but undoes that build.

## Decision 2 (only under A): two hits on one target, the first enough to kill it

Two members hit the same enemy on one tick and either hit alone would kill it.

**Option A — both land on it; the extra is wasted (recommended).** That is what "worked
out against where things stood at the start of that tick" means. On screen both shots
reach the falling enemy. Simple and true to the originals; the cost is a wasted attack.

**Option B — the second one picks another enemy.** No wasted attacks, but it needs an
order to know which one is "second", which is the order Decision 1 A removes.

The Fighter's flurry is the same question in small: its remaining strikes go to the
nearest enemy still standing when its target dies partway through. Under A, a target
killed by someone else on that tick still counts as standing for the flurry. Cheap to
change either way.

## Decision 3 (only under A): the last member and the last enemy kill each other

Today it cannot happen. Under A it can, and the battle has no rule for it: "A battle ends
when one side has no one left standing."

**Option A — it counts as a loss (recommended).** No member is left to carry anything out,
so it reads like any other wipe; the dungeon's existing loss path handles it.

**Option B — it counts as a win.** The enemies are all gone, so the floor is cleared, but
with nobody alive to claim it.

**Option C — its own outcome**, shown as a mutual wipe. Most honest, but a third ending
that every screen after a battle has to handle.

A and B are a one-line rule and cheap to change later; C is new screens and saved state.

## Open Questions

- Same-tick attacks that aren't two close-range fighters (two Archers, a Mage and an
  Archer, two members on one enemy): all at once as the originals say, or keep today's
  turn order?
- If all at once: two hits on one enemy on the same tick, the first enough to kill it —
  both land and the extra is wasted, or the second picks another enemy?
- If all at once: the last member and the last enemy kill each other on the same tick — a
  loss, a win, or its own ending?
