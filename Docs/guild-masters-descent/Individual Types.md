# Individual Types

> **Status:** Early design. Nothing is built yet — all six combat types have sheets.

## The Brute

The Brute attacks at close range. It has advantage over the Tank — it can push the Tank's
shield aside and bash the weak points in the armour underneath, bypassing the defence
subtraction entirely. It's weak to the Fighter: the Brute wears tanned hide, which adds a
little defence on top of its Constitution, so there's less to subtract than against a
properly armoured type, and a Fighter's many strikes keep most of their damage.

The Brute's ordinary attack cleaves too: it hits the targeted enemy and the two directly
next to it, on whichever row its close range can reach, and each of them can evade it
individually.

The Brute's special skips the nearest occupied row and cleaves the two rows behind it, or
whatever rows remain if there are fewer. The cleave hits the targeted enemy and the two
directly next to it. When the Brute pushes past the front row, it moves there, cleaves,
and returns to its own node, all in the same action. The Brute's bonus charge condition is
hitting multiple enemies.

## The Tank

The Tank attacks at close range. It has advantage over the Fighter: the Tank's defence is
subtracted from each incoming hit, and a Fighter lands many smaller strikes, so every one
of them pays that subtraction and loses most of its damage.

The Tank's ordinary attack hits one target and taunts it, drawing that enemy's attention.

The Tank's special is called Shields Up. It temporarily increases the Tank's own defence,
and it also adds that defence to all the allies behind him in his own column — two of them
when he's in the front row. If more than one Tank uses it, the contributions are fully
additive: an ally behind two Tanks gets both lots of defence.

Being attacked is the Tank's bonus: the bar charges faster while the Tank is being
attacked.

## The Fighter

The Fighter attacks at close range, with many smaller strikes — the property both of its
matchups turn on. The number of strikes is fixed by its type; levelling makes each strike
hit harder rather than adding more strikes. The Fighter's ordinary strikes are light —
its damage is spread across them.

Each time the Fighter's cooldown comes up, it makes one ordinary attack, like any other
type — its many strikes all belong to that single attack. Its special bar therefore
charges more slowly than a faster type's; the flurry is what offsets that over the course
of a longer fight.

Its special is a flurry of between 4 and 6 strikes on a single target. The first four
strikes always land; each of the two after that happens on a Luck check, so the flurry
only runs to five or six strikes if those checks succeed. The flurry's strikes hit hard.
If the target dies before the strikes run out, the remaining strikes carry to the nearest
enemy still standing. If any enemy is killed during the flurry, the Fighter's charge bar
refills to 90% — that refill is the Fighter's bonus charge condition.

The flurry's own strikes don't charge the bar.

## The Rogue

The Rogue attacks at far range and has high evasion. Its advantage over the Archer is
against the Archer's ordinary shots: a single shot is a single chance to miss, so
high evasion beats it. It's weak to the Mage because the Mage's area attacks can't be
dodged.

The Rogue's ordinary attack is two quick strikes. Its strikes don't hit as hard as a
Fighter's, because the weapon it carries adds less damage.

The Rogue's special is called Vanish: the Rogue becomes untargetable. Its attacks don't
break Vanish, so it can keep attacking while vanished, and while Vanish is active those
attacks hit automatically — there's no hit check. Vanish ends when an enemy's area attack
hits the Rogue, or when its fixed length runs out. Vanish fails if the Rogue is the only
thing an enemy can reach — then the Rogue can be hit anyway.

The Rogue's bonus charge condition is evading an attack.

## The Archer

The Archer attacks at far range. Its ordinary attack is a single shot, and that one shot
carries the type's whole damage at once. Its special is called Volley: it hits the target,
the enemies one to each side of it, and the one directly behind it. If the target is in
the enemy's back row, with nothing behind it, the extra hit spills forward instead — onto
the position in front of the target. The target takes the full hit; its neighbours take
reduced damage. Volley is an area attack, so it can't be dodged — evasion does nothing
against it.

The Archer's bonus charge condition is hitting the same target twice running. Specials
are outside the streak entirely — a Volley neither continues nor breaks it. Hitting the
same target twice running also raises the Archer's accuracy and its damage — a continuous
percentage increase that caps at 10%. A miss resets the streak.

## The Mage

The Mage attacks at far range. Its attacks are magic damage, driven by Intelligence. Its
ordinary attack is an area attack covering a whole column of the enemy's grid — all three
rows. It's weak to the Archer because the Mage can neither dodge nor absorb, so a
precise single shot is what kills it.

Its special is a lingering field: it covers two columns of the enemy's grid and keeps
damaging enemies standing in it. The field affects enemies only — it never damages the
player's own members.

The Mage's bonus charge condition is allies in front of it in its own column taking hits.

## Open Questions

- What are the stats, skills and abilities for each individual type?
- How fast does a special charge?
- How many strikes is the Fighter's ordinary attack? Its count is fixed by its type, but
  the number isn't set.
- The Fighter's fifth and sixth flurry strikes each turn on a Luck check — is that the
  same check that can reset a cooldown, or a separate roll of its own?
