# Individual Types

> **Status:** Early design. Nothing is built yet — all six combat types have sheets.

## The Brute

The Brute attacks at close range. It has advantage over the Tank — it can push the Tank's
shield aside and bash the weak points in the armour underneath, quartering the Tank's
defence in the calculation. It's weak to the Fighter: the Fighter halves the Brute's
defence in the calculation. The Brute wears tanned hide, which adds a little defence on
top of its Constitution.

The Brute's ordinary attack cleaves too: it hits the targeted enemy and the two directly
next to it, on whichever row its close range can reach, and each of them can evade it
individually.

The Brute's special skips the nearest occupied row and cleaves the two rows behind it, or
whatever rows remain if there are fewer. The cleave hits the targeted enemy and the two
directly next to it. When the Brute pushes past the front row, it moves there, cleaves,
and returns to its own node, all in the same action. The Brute's bonus charge condition
is hitting more than one enemy: each enemy beyond the first charges 5, rather than the
flat 15 every other type's bonus condition gives.

## The Tank

The Tank attacks at close range. It has advantage over the Fighter: the Tank's defence
counts double in the calculation against a Fighter.

The Tank's ordinary attack hits one target and taunts it, drawing that enemy's attention.

The Tank's special is called Shields Up. It temporarily doubles the Tank's own defence,
measured before any Shields Up already standing on him, and each ally behind him in his
own column gains that same figure — the Tank's own unshielded defence — on top of their
own, two of them when he's in the front row. Firing it again refreshes the Tank's own
shield rather than stacking on it: the fresh shield replaces the standing one and starts
its length over, at the same size. If more than one Tank uses it, the contributions are
fully additive: an ally behind two Tanks gets both lots of defence.

Being attacked is the Tank's bonus: the bar charges faster while the Tank is being
attacked.

## The Fighter

The Fighter attacks at close range, with two smaller strikes — the property both of its
matchups turn on. The number of strikes is fixed by its type; levelling makes each strike
hit harder rather than adding more strikes. The Fighter's ordinary strikes are light,
because its two-handed sword's damage band is smaller than that of a kind putting
everything into a single hit.

Each time the Fighter's cooldown comes up, it makes one ordinary attack, like any other
type — its two strikes all belong to that single attack.

Its special is a flurry of 4 or 6 strikes on a single target. The first four strikes
always land; one Luck check — a pull from the Fighter's Luck bag — then decides the last
two together: a True adds both, a False ends the flurry at four. Each flurry strike does
what one of the Fighter's ordinary strikes does. The flurry hits hard because there are
four or six strikes in it rather than two — not because any one of them is heavier. If the
target dies before the strikes run out, the remaining strikes carry to the nearest enemy
still standing. If any enemy is killed during the flurry, the Fighter's charge bar refills
to 90% — that refill is the Fighter's bonus charge condition.

The flurry's own strikes don't charge the bar.

## The Rogue

The Rogue attacks at far range and has high evasion. Its advantage over the Archer is
against the Archer's attacks: it draws up to two evasion tokens instead of one — if the
first comes up False it draws again, and a single True evades. See the Combat doc for
how an evasion draw works. It's weak to the Mage because the Mage's area attacks can't
be dodged.

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
half that damage. Volley is an area attack, so it can't be dodged — evasion does nothing
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

Its special is a lingering field: it covers two columns of the enemy's grid. The field
affects enemies only — it never damages the player's own members. The field deals damage
through two separate events, each one dealing half of what the Mage's ordinary attack
deals to that same target: a character standing in the field takes damage from it when
that character begins its own attack — that damage lands before the attack does, so if it
kills the character the attack never happens — and a character that moves into the field,
changing its position, takes damage for entering. Reaching in to attack from outside the
field doesn't count as entering — an attacker reaching in to attack a character standing
in the field takes no damage from it.

The Mage's bonus charge condition is allies in front of it in its own column taking hits.

## Open Questions

- What are the stats, skills and abilities for each individual type?
