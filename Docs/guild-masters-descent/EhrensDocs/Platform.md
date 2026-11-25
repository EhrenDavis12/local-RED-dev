# Platform

> **Status:** Early design. The phone runs sideways and the game saves by itself; the
> save rules marked "for now" are defaults, not yet settled.

## Orientation

Always sideways. On the iPhone the game runs in landscape only — there is no portrait mode.

## Saving

The game saves by itself: the guild is saved when the phone sends the game to the
background, and when the game quits. There's no Save button, because on the iPhone a
backgrounded app can be killed with no warning, and a guild saved only on request would
lose play. Coming back from the background carries on with the guild as it was and
counts the time spent there, because the iPhone often never closes a backgrounded app.

A dive in progress is saved too. If the game is sent to the background or killed partway
through a dive, the save holds the dive itself, and opening the game again carries the
dive on where it stopped — partway through a floor, if that's where it was. Closing the
game never undoes a death: a member who died on the dive is still dead when the game
opens again. Nor does it give back a potion: one drunk on the dive is still gone, and
every member on the dive opens again holding exactly the potions left in their slots.
A member holds potions only on a raid, so as a save loads, whatever sits in the slots of
a member not on the saved dive goes back to the stores — which is how a played mission
the game closed partway through comes back: its undrunk potions in the stores, its drunk
ones gone.

That holds inside a battle too. For now the rest of a battle the game closed in plays out
exactly as it would have if the game had never closed, the same rolls and all — closing
and opening the game can't re-roll an attack or dodge a death. An attack already made
counts as made, even if it hadn't finished showing on screen, and so does every special
that went off in the middle of it. The save holds where every cooldown stands — how long
each fighter still has to wait, whether one is owed a free attack from the Luck reset,
whether a full bar's special is still waiting to go off, and how far each lasting effect
has run — and what's left in every fighter's Luck bag, the enemies' too, so nothing is
drawn again as it loads. A Fighter or a Brute can be waiting on its special and a free
attack at once, and the save holds both. It doesn't hold an order the player gave that
hasn't been used yet: an ordered drink is lost when the game closes, and the battle
carries on from the save with none. Saving doesn't bank anything, either: the gold found
on the dive is still the party's until the dive ends, and what was found since the last
rest area can still be lost.

A battle doesn't move on while the game is closed or in the background: it picks up at
the moment it stopped. A long gap between two frames is dropped rather than played fast —
for now at most a quarter of a second of fight plays in one frame, a placeholder — so
coming back from the background, or a long stall, never fast-forwards a fight.

A save never costs the player the save before it. If saving fails, or the phone dies
partway through, the slot still holds the last good save, whole.

Loading never changes or deletes a save. A save the game can't read, or one made by a
newer version of the game, is reported as such and left on the phone as it is. A save made
by an older version still loads; a dive one of those saved between battles, from before
the save held special bars, loads with every bar empty, a save from before potions loads
with none in the stores and none on any member, a save from before slots loads a member on
the saved dive with the one potion they held and puts anyone else's in the stores, so no
potion is made or lost, a save from before shields loads with no shields in the stores and
none on any Tank, a save from before the Luck bag loads every member, and every enemy in a
saved battle, with an empty bag that fills from that character's Luck at its first pull, a
save from before saved teams loads with all three empty, a battle saved before specials
went off by themselves loads with no special waiting, a bar full in it going off as the
battle carries on, a save from before lost health healed at home loads every member in the
hall at full health, and a save from before enemies had a cost keeps each dungeon as it
was made, three battles a floor, with every monster saved without a cost, on a floor or in
a battle saved partway through, costing its rank's baseline: at F its type's starting
stats, and a kill that pays the full F value, never nothing. A save from before monsters
carried gear keeps each dungeon as it was made, with every monster, on a floor or in a
battle saved partway through, carrying no gear and keeping the cost and stats it was
saved with. A saved battle is never judged against a placeholder number — a fighter left
waiting longer than its own cooldown is accepted — so rebalancing a placeholder can't
turn a good save into one the game can't read.

Maximum health is never taken from a save: every member's and every monster's comes from
the Constitution saved with them, so a save made before health followed Constitution
loads under the rule as it is now.

Current health is taken from a save. Every member is saved with the health they have and
the part of a minute already counted toward their next point, so closing and opening the
game gives back no more health than the time away heals, and never loses that part of a
minute. As a save loads, a member's health is capped at the maximum their Constitution
gives; a higher maximum doesn't raise it, and the gap heals with time at home.

Every member's Luck bag is saved with them, part-used as it is, so closing the game
between battles or between dives never refills a bag or hands back a token.

Experience is saved exactly, as a whole number of parts of a point, 21,621,600 parts to
the point. That is 360,360, which every party size from 1 to 15 divides, times 60, so a
point of an enemy's cost pays a whole number of parts — a thirtieth of a point at F, a
twentieth from E up — and a combat's share is never rounded. Times 30 would cover F only:
an E-rank share split eight ways would stop coming out whole. A save from before enemies
had a cost counted 360,360 parts to the point, and as it loads every member's experience
is multiplied by 60, once and without loss, so their bar, level and whole experience
read the same.

For now:

- There are three save slots. The number is a placeholder.
- Starting a new game in a slot that already holds a save — even one the game can't
  read — needs the player to say to overwrite it. The game never replaces a save on its
  own.
- A save with gear equipped where it can't be — on the wrong combat type, on a
  specialist, in a slot that isn't its own, on two members at once, or gear that's no
  longer in the stores — is fixed as it loads: the gear comes off and goes back to the
  stores, and the save loads. Gear on two members stays with the one hired first.
- A save holding fewer than no potions in the stores is fixed as it loads: the stores go
  to none, and the save loads. So is a member holding fewer than none, who goes to none,
  and a member on the saved dive holding more than their slots take, whose extra goes to
  the stores.
- A special bar saved below empty or past full is brought back inside the bar as it
  loads, and a dive saved between battles where every bar should be empty — at a rest
  area, or before a floor's first battle — loads with them empty.
- A member on a saved dive keeps the health they had when the game saved, capped at
  their maximum — so a member saved at 7 of 10 under the old rule loads at 7 of, say,
  50, rather than keeping the damage they had taken.
- A member in the hall saved with no health, which would read as dead, loads with 1. A
  count toward the next point saved below none, or at a full minute or more, is brought
  inside the minute as it loads, and a member at full loads with none counted.
- A save made before experience became one bar per rank loads each member with their
  level and stats kept and their experience at the point where that level starts — an
  F-rank member at level 5 loads with 6, one at level 1 with none. On a dive one of those
  saved partway through a floor, the battles already won on that floor never pay their
  experience.
- A saved Luck bag that can't be true — more than 50 tokens, fewer than none, or more
  Trues than tokens left — is emptied as it loads, and the save loads. A bag is never
  judged against the character's Luck, since a level-up leaves a bag whose Trues no
  longer match it.
- A saved team that can't be true — more than 15 members, a spot off the grid or used
  twice, or a member in it twice — is emptied as it loads, and the save loads. A saved
  team holding a member who has since left the guild keeps them, and can't be picked
  until it's saved over.
- A saved monster's weapon or armour that can't be true — not its own type's kind for
  that slot, a class that doesn't exist, a range starting below 0 or above its top, a
  maximum durability below 1, or a current durability below none or past its maximum —
  makes the save one the game can't read, on a dungeon floor or in a battle saved partway
  through. So do a monster's stat points saved above its cost, or below 5 other than 0,
  which reads as the cost. Nothing is judged against the gear bands, so rebalancing a
  band can't turn a good save into one the game can't read.

## Open Questions

- Is a save holding a special bar below empty or past full refused, or fixed as it loads?
- When a save holds a special bar where every bar should be empty — at a rest area, or
  before a floor's first battle — is that bar emptied as it loads, or is the save refused?
- A member on a dive saved before health followed Constitution loads with the health they
  had, capped at their new maximum. Should they keep the damage they had taken instead?
- Is a saved Luck bag that can't be true — more tokens than a bag holds, fewer than none,
  or more Trues than tokens — emptied as it loads, or is the save refused?
- A member in the hall saved with no health loads with 1. Is that right, or is the save
  refused?
