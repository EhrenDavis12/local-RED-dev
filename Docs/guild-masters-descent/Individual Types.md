# Individual Types

> **Status:** Early design. Nothing is built yet — all six combat types have sheets.

## The Brute

The Brute has advantage over the Tank — it can push the Tank's shield aside and bash the
weak points in the armour underneath, bypassing the defence subtraction entirely. It's
weak to the Fighter because the Brute isn't armoured, so there's nothing to subtract from
incoming hits, and a Fighter's many strikes all land in full.

The Brute's special pushes past the front row and cleaves the row behind it: the special
hits the second-nearest occupied row, or the only occupied row if just one row remains.
The cleave hits the targeted enemy and the two directly next to it. When the Brute pushes
past the front row, it moves there, cleaves, and returns to its own node, all in the same
action. The Brute's bonus charge condition is hitting multiple enemies.

## The Tank

The Tank has advantage over the Fighter: the Tank's defence is subtracted from each
incoming hit, and a Fighter lands many smaller strikes, so every one of them pays that
subtraction and loses most of its damage.

The Tank's special is called Shields Up. It temporarily increases the Tank's own defence,
and it also adds that defence to all the allies behind him in his own column — two of them
when he's in the front row. It lasts a fixed number of turns, and if more than one Tank
uses it, the contributions are fully additive: an ally behind two Tanks gets both lots of
defence.

The Tank's bar charges from the Tank's own attacks, the same as every type's. Being
attacked is the Tank's bonus: the bar charges faster while the Tank is being attacked.

## The Fighter

The Fighter attacks with many smaller strikes — the property both of its matchups turn on.

Its special is a flurry of up to 6 strikes on a single target. If the target dies before
the strikes run out, the remaining strikes carry to another enemy. If any enemy is killed
during the flurry, the Fighter's charge bar refills to 90% — that refill is the
Fighter's bonus charge condition.

The flurry's own strikes don't charge the bar.

## The Rogue

The Rogue has high evasion, and has advantage over the Archer because an Archer fires
single precise shots — a single shot is a single chance to miss, so high evasion beats
it. It's weak to the Mage because the Mage's area attacks can't be dodged.

The Rogue's special is called Vanish: the Rogue becomes untargetable. It can attack once
while vanished, and that attack breaks the Vanish. Vanish fails if the Rogue is the only
thing an enemy can reach — then the Rogue can be hit anyway.

The Rogue's bonus charge condition is evading an attack.

## The Archer

Its special is called Volley: it hits the target, the enemies one to each side of it, and
the one directly behind it. The target takes the full hit; its neighbours take reduced
damage. Volley is an area attack, so it can't be dodged — evasion does nothing against
it.

The Archer's bonus charge condition is hitting the same target twice running. Specials
are outside the streak entirely — a Volley neither continues nor breaks it.

## The Mage

The Mage's attacks are magic damage, driven by Intelligence. Its ordinary attack is an
area attack covering a whole column of the enemy's grid — all three rows. It's weak to
the Archer because the Mage can neither dodge nor absorb, so a precise single shot is
what kills it.

Its special is a lingering field: it covers two columns of the enemy's grid and keeps
damaging enemies standing in it for several turns. The field affects enemies only — it
never damages the player's own members.

The Mage's bonus charge condition is allies in front of it in its own column taking hits.

## Open Questions

- What are the stats, skills and abilities for each individual type?
- How fast does a special charge?
