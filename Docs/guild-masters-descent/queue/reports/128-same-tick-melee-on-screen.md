# How two close-range fighters hitting each other on the same tick look

> **Status:** Research for queue item #128, 2026-11-17. Two decisions for the user; nothing
> here is settled until they answer. Sources are the docs' owner's original `Combat.md`,
> EhrensDocs `Combat.md` (the pending "A close-range attack waits for its target to be
> home" change), and the combat engine and battle screen on `queue/build` in
> `src/guildmasters-descent`.

## The conflict

`Combat.md` (17 Nov): "When more than one combatant's cooldown comes up on the same tick,
their attacks all happen at the same time — there's no order between them, and nothing
resolves first. Damage is worked out against where things stood at the start of that
tick, so a combatant that dies on that tick still lands the attack it made on it, and two
combatants can kill each other on the same tick."

The user, 17 Nov: "the attacker needs to wait for the attacked to be in the spot and not on
the attack" — after two fighters going for each other each jumped to the other's empty
spot and swung at thin air.

Both can hold in the engine. The problem is only the picture: if two close-range fighters
pick each other on the same tick and both hits land at once, the old drawing (each walks
to the other's spot) is exactly the thin-air swing the user asked to stop.

## What the code does today

`Battle.Walk.cs` puts same-tick attacks in an order (Dexterity, then a draw) and holds a
close-range attack while its target is out on a lunge or holds an attack ahead of it. So
today one of the pair walks out, hits, walks home; only then does the other go — and if
the first hit killed it, it never goes. That order is what item #131 removes. How long a
fighter is out is sized by `MeleeTiming.WindowTicks` from the same walk plan
(`MeleeMotion.PlanAction`) the screen draws, so any new picture also changes how long both
fighters count as away in the engine.

## Decision 1: a pair that picks each other

**Option A — meet in the middle (recommended).** Both walk out at once, meet halfway
between their spots, swing, and both blows land on the same frame; both walk home. A
fighter killed there falls where it stands, halfway, rather than at home. Reads as a
clash, shows plainly that both hits happened together, and nobody walks to an empty spot.
Build cost: one new walk target in the melee planner and a matching away window; the
engine part is #131 either way.

**Option B — one walks, the other swings back from home.** The faster-looking one walks
over; the other stays in its spot and swings as it arrives, both blows landing together.
Cheaper to draw, but which one walks needs a rule (it has no order to borrow any more),
and it reads as a counterattack rather than two attacks.

**Option C — keep today's turn-taking for this pair.** One goes, then the other. This is
the user's 17 Nov rule as built, but it keeps an order the originals say does not exist,
and a fighter killed by the first blow never lands its own, which the originals say it
does. Changing this later is an engine change, not just a drawing change.

A and B are both screen choices, cheap to swap later; C is the expensive one.

## Decision 2: a chain on the same tick

Three fighters: X goes for Y, and Y, on the same tick, goes for Z. Y leaves its spot, so
X has nothing at home to hit.

**Option A — X follows Y (recommended).** X's blow still happens on that tick, as the
originals say; on screen X walks to where Y actually is, beside Z, and hits it there.
Nobody swings at an empty spot. More drawing work: X's walk targets a moving fighter.

**Option B — X waits for Y to come home.** X's attack slips to a later tick, exactly as
the 17 Nov wait does today. Simple, already built, but X's attack is no longer at the
same time as Y's, which the originals say it should be, and if Y dies beside Z, X picks
again.

Either is cheap to change while the engine work in #131 is still to be built; after it, B
to A is a redo of that wait rule.

## What else this touches

- Ranged attackers are unaffected: an Archer or Mage already shoots its target where it
  is, out on an attack or not.
- A fighter whose cooldown comes up while it is still out keeps walking home first (the
  pending EhrensDocs change); nothing here changes that.
- The answers belong in EhrensDocs `Combat.md` next to the pending wait change, through
  the tidy pipeline, before #131 is built.

## Open Questions

- Two close-range fighters pick each other on the same tick: meet in the middle, one walks
  while the other swings from home, or keep taking turns?
- X goes for Y on the same tick Y goes for Z: does X follow Y and hit it beside Z, or wait
  for Y to come home?
