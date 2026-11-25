# The Dungeon — proposed changes

> **Status:** Change notes against `The Dungeon.md`, for its owner to review. The original
> is not edited.

## Change: A guild starts off with a single F-rank dungeon

> Proposed 2026-11-11 · for review

**Where:** `## Finding Dungeons`, first paragraph

**Now says:**

```
Dungeons are found through the mission board. The missions that find a dungeon are the
challenge the player works against.
```

**Proposed:**

```
A guild starts off with a single F-rank dungeon. Every other dungeon is found through the
mission board. The missions that find a dungeon are the challenge the player works
against.
```

**Why:** Answered: a guild starts off with a single F-rank dungeon. "Dungeons are found
through the mission board" said every dungeon is found, and the starting one isn't.

## Change: For now a dive drops ore, herb and healing potions, and no gear

> Proposed 2026-11-25 · for review

**Where:** `## The Dungeon`, the paragraph beginning "Dungeon diving yields materials or items"

**Now says:**

```
Dungeon diving yields materials or items, and the floor itself pays gold. A dive can also
drop a weapon or a piece of armour on certain floors.
```

**Proposed:**

```
Dungeon diving yields materials or items, and the floor itself pays gold. A dive can also
drop a weapon or a piece of armour on certain floors. For now, though, no gear drops, and
the materials and items are ore, herb and the healing potion. When a floor is cleared,
each enemy on it has its own one-in-four chance to drop something: half the time one
healing potion, the same as a bought one, and otherwise one ore or one herb, at even odds.
The loot drops with the floor's gold, and only once every battle on the floor is won, so
a floor the party leaves early drops nothing, and neither does a rest area. A floor's
drops are rolled again each time it is cleared, from the dive's own saved rolls, so
saving and loading can't roll them a second time. Each unit of ore or herb records the
rank of the dungeon it came from.

Each unit of loot takes one slot. Until the dive ends the loot is the party's as a whole,
never one member's: nothing limits what the party gathers on the way down, and a potion
that drops can't be drunk on the dive it dropped on. The room is counted once, as the
dive ends — the free slots of the members still alive, a Porter's extra ones too, less
the potions they still hold — and a fallen member's gear takes its share first. The loot
fills what's left in this order, and the rest is lost: healing potions, then ore, then
herb, and within a kind a higher rank before a lower one. Going home at a rest area
brings everything that fits. Turning back between rest areas, a stand-off included,
loses the loot found since the last rest area, and the rest comes home if it fits. A
party with no one left alive brings nothing out. What comes home goes into the guild's
stores: ore and herb counted by kind and rank, and a dropped potion with the bought ones.
```

**Why:** The game is built this way. The paragraph and the list after it name materials,
items and dropped gear as what a dive yields, but not which materials and items there
are, when they drop, or how they're carried. Ore and herb are the original's two
materials, and one enemy in four, the same for every rank and floor, is its drop rate.
Losing what was found since the last rest area on turning back is the original's
"Retreating always costs the loot gathered since the last safe floor". Half the drops
being an item is the user's placeholder for the original's open question on how often a
drop is one rather than the other. The rest are defaults the build chose, not yet the
user's word: counting the room as the dive ends is asked in "Questions on carrying", and
the others in "Questions on loot". Dropped gear stays out of the first version.

## Change: A floor is a series of battles that scrolls right into the next

> Proposed 2026-11-11 · for review

**Where:** `## The Dungeon`, second paragraph, its first sentence (the paragraph beginning
"Each floor has 1–3 battles.")

**Now says:**

```
Each floor has 1–3 battles.
```

**Proposed:**

```
Each floor is a series of battles, 1–3 of them. At the end of a battle the screen scrolls
right into the next battle, with no result screen and nothing to click in between: a
floor's battles play straight through, back to back. How many a floor has is rolled for
each fighting floor when the dungeon is created, 1, 2 or 3 at equal odds, the starting
dungeon too. After the last one comes victory, dropping loot: the floor's gold drops as
one lump at the end of the floor, and only once every battle on that floor is won — if a
floor has 3 battles, the party needs to beat all 3.
```

**Why:** Answered: each floor is a series of battles, and at the end of a battle the
screen scrolls right into the next one, then victory, dropping loot. Answered too: loot
at the end of the floor — if 3 battles on that floor then they need to beat all 3. "Each
floor has 1–3 battles" gave the count but not how one battle leads into the next, or
where the loot drops. The original's 1–3 holds for the starting dungeon too, since the
new docs win where they and an earlier answer disagree; the equal odds are a default the
build chose, not yet the user's word. What the board's floor layout shows, whether a
party picks a route, and what makes a boss floor are not settled by this. The rest of the
paragraph, on rest areas and retreating, is the next change. Answered 2026-11-14, too: "you enter a level and the
level should go through" — a floor's battles play back to back, with no screen after
each one showing what was gained and waiting for a click on Continue.

## Change: A party can turn back anywhere, and gold takes no slots for now

> Proposed 2026-11-11 · for review

**Where:** `## The Dungeon`, second paragraph, from "Every 5th floor is a safe rest area" to
the end of the paragraph

**Now says:**

```
Every 5th floor is a safe rest area, where every member gets back fifteen per cent
instead of the five, not both, and the player may choose to return to the top and exit
the dungeon. The Cook adds to both figures, covered in the Specialists doc. Retreating
always costs the loot gathered since the last safe floor — any party member can carry
some of it, so how much is lost depends on who came along.
```

**Proposed:**

```
Every 5th floor is a safe rest area, where every member gets back fifteen per cent
instead of the five, not both, and the player may choose to return to the top and exit
the dungeon. The Cook adds to both figures, covered in the Specialists doc. The party can
turn back anywhere, not only at a rest area — but leaving between rest areas loses the
gold and loot found since the last rest area. "Anywhere" includes the middle of a battle: a
Retreat button is there all through a floor's battles, and the party can leave with it at
any moment. For now a battle that ends in a stand-off counts as the party turning back
there.

For now gold takes no slots, so carrying capacity never limits the gold a party brings
out, and who came along doesn't change how much: leaving between rest areas loses the
gold found since the last one, and no other gold is left behind. Only the living carry,
so a party with no one left alive brings nothing out, and a dead member's gear comes home
only into the slots the living have free.
```

**Why:** Answered: yes, turn back anywhere, losing the gold found since the last rest
area. The original names the rest area as where the player may exit, and its retreat
sentence only implies leaving elsewhere; this says so outright. "Any party member can
carry some of it, so how much is lost depends on who came along" no longer holds:
turning back between rest areas loses all the gold found since the last rest area
whoever came along. The original's paragraph on capacity, after this one, counts it in
slots and has a healing potion and an item of loot take one each, but doesn't say
whether gold takes any; for now it takes none, so capacity never limits the gold a party
brings out. How a dead member's gear counts against it is in Equipment's change "A dead
member's gear takes a slot a piece, for now", which keeps the original's rule that the
gear comes back only if there's room left. The second paragraph has a default for now on
gold, and the first has a default on stand-offs; each is proposed as a
question for `## Open Questions`. Answered 2026-11-14: the party can retreat at any time, the middle
of a battle included — "you can holler a retreat sign that will take them out". Which
gold a retreat keeps is proposed as a question in "A question on what gold a retreat
keeps".

## Change: How a heal in the dive lands, for now

> Proposed 2026-11-13 · for review

**Where:** `## The Dungeon`, second paragraph, its second sentence (beginning "Between
floors"), with new sentences after it

**Now says:**

```
Between floors, every member gets back five per cent of their maximum health, and nothing
comes back between the battles on a single floor.
```

**Proposed:**

```
Between floors, every member gets back five per cent of their maximum health, and nothing
comes back between the battles on a single floor. Clearing the floor before a rest area
gives the fifteen alone, and pushing on from the rest area to the next floor gives
nothing, so floors 4 → 5 → 6 give one fifteen per cent and no five. For now a heal is a
share of the maximum health a member has once the floor's last battle has shared its
experience, so a level-up on that floor counts. Everything that lands on a member at once
— the party's share and every Cook's — is added up first and turned into health once, and
a fraction of a point rounds up, so every living member gets at least one point back. A
heal never takes anyone past their maximum.
```

**Why:** Answered 2026-11-13: "OK, then just the 15%", which the original now says too.
Clearing the floor before a rest area, and pushing on past it, follow from that; the rest
of the paragraph is how the dive is built. Nothing said which maximum a heal is a share of
when a member levels up on the floor just cleared, whether the party's share and a Cook's
are rounded together or one at a time, or which way a fraction of a point rounds. Those
three are proposed as questions for `## Open Questions`.

## Change: The dungeon's enemies are monsters

> Proposed 2026-11-11 · for review

**Where:** `## The Dungeon`, first paragraph (new paragraphs after it)

**Now says:**

```
Dungeon diving is the main gameplay. Death in the dungeon is permanent — there is no way
to bring a dead member back. The risk is inherent in the choice: send someone you know
will survive, or send a team and see who comes back.
```

**Proposed:**

```
Dungeon diving is the main gameplay. Death in the dungeon is permanent — there is no way
to bring a dead member back. The risk is inherent in the choice: send someone you know
will survive, or send a team and see who comes back.

The dungeon's enemies are monsters. For now the monsters might be limited to just the
Archer's animations; anything a monster has no art for is a bright yellow shape with its
name written on it.

A monster is given a rank and a level like a member is, and uses the same stat rules. For
now every monster in a dungeon is the dungeon's own rank — F, as the guild's starting
dungeon is, and there's no grade below F — and level 1.
```

**Why:** Answered: the enemies are monsters, but for now we might be limited to just the
archer animations. The yellow-shape clause is the
project's standing rule for missing art. A monster's rank follows Combat's `## Enemies`:
an enemy is the dungeon's rank or one grade below it. The first paragraph is unchanged.

## Change: How a monster's gear is rolled and paid for, for now

> Proposed 2026-11-25 · for review

**Where:** `## The Dungeon`, the two paragraphs beginning "The chance an enemy carries a
weapon or wears armour rises with the floor" (new paragraphs after them)

**Now says:**

```
The chance an enemy carries a weapon or wears armour rises with the floor. A weapon's
chance is 1 to 3 per cent on the first floor and rises 5 to 7 points a floor; armour's
chance starts on floor 11 at 3 to 5 per cent and rises at the same rate a floor. A
weapon is therefore always the likelier of the two.

An enemy's cost is its stat points plus what its gear is worth, a piece being worth
the middle of its rolled range — so arming an enemy means fewer of them on the floor.
```

**Proposed:**

```
The chance an enemy carries a weapon or wears armour rises with the floor. A weapon's
chance is 1 to 3 per cent on the first floor and rises 5 to 7 points a floor; armour's
chance starts on floor 11 at 3 to 5 per cent and rises at the same rate a floor. A
weapon is therefore always the likelier of the two.

An enemy's cost is its stat points plus what its gear is worth, a piece being worth
the middle of its rolled range — so arming an enemy means fewer of them on the floor.

For now each dungeon rolls its own three figures once, when it's created, each a whole
number at even odds: the weapon's chance on the first floor, 1 to 3 per cent; the rise,
5 to 7 points a floor, the same for both; and armour's chance on floor 11, 3 to 5 per
cent. Every floor counts toward the rise, rest areas included — so with a start of 2 and
a rise of 6, a weapon's chance is 32 per cent on floor 6 — and a chance of 100 or more
means always. Each monster rolls its weapon chance and its armour chance for itself, one
apart from the other. The starting dungeon is 10 floors deep, so its monsters carry
weapons only.

A monster's weapon is its type's weapon kind and its armour its type's armour kind, as a
member's are, and a monster never carries a shield. For now a piece is the class of the
monster's own rank, and its range and durability are rolled from the same bands, the same
way, as any member's piece, starting at full durability. Deeper floors give better gear:
once rolled, the piece's range slides toward the top of its band, keeping its width — not
at all on the dungeon's first fighting floor, all the way to the top on its deepest, and
evenly between, counting fighting floors only and rounding down to a whole figure. The
slide stays inside the class's band, so F gear never outclasses F. Durability doesn't
slide.

A piece's worth is the middle of its range after the slide, an exact half rounding up:
an axe of 9–13 is worth 11, and a knife of 4–7 is worth 6.

In a fight a monster's gear adds, wears and breaks exactly as a member's does. For now
the wear lasts that battle only, the same as a monster's health: every battle starts from
the pieces as the dungeon made them, so a floor fought again on a later dive meets the
same gear, unworn. A monster's gear is its own and never the guild's — it never goes into
the stores.
```

**Why:** The game is built this way. The original gives each chance's range, the rise
and what a piece is worth, but not whether the figures are rolled once a dungeon or
afresh, whether rest areas count toward the rise, whether a monster's two chances are
rolled together, what class a monster's piece is, how "the better the equipment those
enemies carry" in Combat's `## Enemies` works, which way a half rounds, or what happens
to a monster's gear after a battle. Battle Test's Test Dungeon table has a weapon at 32
per cent on floor 6, which counts the rest area on 5, and says "any gear an enemy has is
of its own type's kind". Every "for now" here is a default the build chose, not yet the
user's word, and changing one reaches only dungeons made after it: a dungeon already made
keeps its monsters and their gear. For the owner to reconcile: Battle Test's `## The
Enemy Team` has its armour and the Fighter's sword at 10 durability, "matching the player
team's own rolls", but `## The Player's Team` has every piece at the top of its
durability band — 120 for every armour, 160 for the two-handed sword — and a monster's
piece here starts at full durability, as a member's does.

## Change: How a floor's power becomes its enemies, for now

> Proposed 2026-11-24 · for review

**Where:** `## The Dungeon`, the paragraph beginning "An enemy's share becomes its stats in
a fixed shape" (new paragraphs after it)

**Now says:**

```
An enemy's share becomes its stats in a fixed shape. The points are spread down the
ordering its type's stat weighting gives, in the ratio 8 : 7 : 6 : 5 : 4 — so a
30-point enemy comes out at 8 in its type's leading stat, then 7, 6, 5 and 4. The
weightings are in the Guild Members doc.
```

**Proposed:**

```
An enemy's share becomes its stats in a fixed shape. The points are spread down the
ordering its type's stat weighting gives, in the ratio 8 : 7 : 6 : 5 : 4 — so a
30-point enemy comes out at 8 in its type's leading stat, then 7, 6, 5 and 4. The
weightings are in the Guild Members doc.

For now the starting dungeon is 10 floors deep, with rest areas on 5 and 10, rather than
rolled from the F band. "Climbing evenly" is the same ratio from each fighting floor to
the next, counting fighting floors only, and an enemy's scaled cost falls the same way,
from its baseline on the first fighting floor to a third of it on the deepest. So the
starting dungeon runs from 100 power on floor 1 to 300 on floor 9, and from 30 points an
enemy down to 10.

Each battle makes one roll for the cost, from half to twice the scaled figure at even
odds. Its enemy count is its share divided by the rolled cost, rounded down, then held
between 1 and 15. Every enemy in a battle has the same stat points: the share divided by
the count, rounded to the nearest whole point, an exact half rounding up. That is the
only rounding — neither the floor's power nor the share is rounded first — so a battle
can spend a little more or a little less than its share. The same rule covers both
edges: past 15, the share divided by 15 raises every enemy's points, and a share smaller
than one rolled cost fields a single enemy holding the whole share.

For now a battle with gear in it is filled one enemy at a time. Enemies are drawn up to
15, each costing the rolled cost plus the worth of whatever gear it rolled, and one is
kept if it's the first, or if the kept enemies' costs, its own included, come to no more
than the share — landing exactly on the share is kept, armed or not. The first that
doesn't fit is let go and no more are drawn. With no one armed, that is exactly the count
above. The kept enemies still all have the same stat points: the share less the worth of
all their gear, divided by the count and rounded the same way, never below 5. So a share
of 100 at a rolled cost of 30, with the first enemy carrying an axe worth 11, fields two
enemies, each on 45 stat points, costing 56 and 45.

An enemy's cost is its stat points plus its gear's worth, and both are kept as figures of
their own: the cost is never worked back out from the stats, nor the stat points from the
cost less the worth. An unarmed enemy's cost is its stat points. For now the stats are
rounded so they add up to the enemy's stat points: each stat's exact share is rounded
down, and the points left over go one at a time to the stats with the largest fractions,
the stat earlier in the ordering winning a tie. An F enemy never has fewer than 5 stat
points, so no stat is below 1, and a 30-point enemy has exactly its type's starting
stats.

For now there's no enemy-type ladder: every floor draws each monster's type from all six
combat types.
```

**Why:** The game is built this way. The original gives the power, the shares, the
baseline, the roll and the 8 : 7 : 6 : 5 : 4 shape, but not the curve "climbing evenly"
means, how the count and the points round, how the ratio lands on whole stats, or how a
battle is filled once its enemies carry gear; Battle Test's Test Dungeon table, rolled
from these rules, shows the equal ratio. The starting dungeon's depth, the even odds,
rounding the count down and having no type ladder yet are defaults the build chose, and
so are filling a battle with gear in it one enemy at a time and its enemies sharing the
stat points the gear leaves, never below 5 — the original's "arming an enemy means fewer
of them on the floor" is what that keeps. How the stats round, and which way an exact
half goes, are waiting on the user's word, and are proposed as questions in "Questions on
the floor power budget". For the owner to reconcile: Battle Test's `## What This Is For`
says "The largest single battle an F-rank dungeon produces is 150 points", but these
rules give 300 when the deepest fighting floor rolls one battle; and Combat's `## Open
Questions` still asks whether the enemies keep coming once the grid of fifteen fills,
though this doc caps a battle at fifteen.

## Change: A floor's monsters are the same every dive, for now

> Proposed 2026-11-12 · for review

**Where:** `## The Dungeon Board`, second paragraph

**Now says:**

```
A newly claimed dungeon starts near-blank. The enemy types and the floor layout appear
as the party reaches each floor.
```

**Proposed:**

```
A newly claimed dungeon starts near-blank. The enemy types and the floor layout appear
as the party reaches each floor.

For now a floor's monsters are the same on every dive: how many battles the floor has,
which monsters, their levels, their points, their gear and where they stand are set
once, when the dungeon is created, and a dungeon from an older save keeps the monsters it
was made with. Each monster stands on a node of its own, drawn at random. A floor counts
as reached once the party starts its first battle there, or arrives there if it's a rest
area.
```

**Why:** The dive is built this way. "Appear as the party reaches each floor" reads as a
floor's enemies being fixed, but nothing said so outright, or what counts as reaching a
floor for the deepest floor reached. Both are proposed as questions for
`## Open Questions`. Nothing said where a monster stands on its grid either; Combat's
`## Formation` says only that enemies use the same style of grid.

## Change: Where a party re-enters, for now

> Proposed 2026-11-12 · for review

**Where:** `## Entering the Dungeon`, the paragraph beginning "The player re-enters at the
last rest area reached" (new paragraphs after it)

**Now says:**

```
The player re-enters at the last rest area reached, and must pay the entry fee again plus
a teleportation fee, reckoned from the floor being returned to: 1 gold a floor in an
F-rank dungeon, rising 1 a rank. This stops the player exploring five floors, returning,
and rearranging the party with no penalty.
```

**Proposed:**

```
The player re-enters at the last rest area reached, and must pay the entry fee again plus
a teleportation fee, reckoned from the floor being returned to: 1 gold a floor in an
F-rank dungeon, rising 1 a rank. This stops the player exploring five floors, returning,
and rearranging the party with no penalty.

For now the last rest area reached is the deepest one the most recent dive reached, and
a dive that re-entered counts the rest area it started at. So the re-entry point can move
back up, from floor 10 to floor 5, and a dive that reaches no rest area leaves none. Any
party can re-enter, not only the one that got there, and its first battle is on the floor
after the rest area. There's no re-entering at a rest area with no floor past it.

For now, once a party is in, the guild hall can't be reached until the dive ends — no
hiring, shopping or changing gear partway through a dive and then carrying on with it.
```

**Why:** The dive is built this way. "The last rest area reached" reads two ways — the
deepest one ever reached, or the one the most recent dive reached — and nothing said
whether the player can leave a dive for the guild hall and come back to it. Both are
proposed as questions for `## Open Questions`.

## Change: Healing potions are packed at the start of a raid and come back at its end, for now

> Proposed 2026-11-18 · for review

**Where:** `## Entering the Dungeon`, last paragraph (new paragraphs after it)

**Now says:**

```
Potions take up the party's carrying capacity, and they're added to it at the start of
the raid.
```

**Proposed:**

```
Potions take up the party's carrying capacity, and they're added to it at the start of
the raid.

A raid starts when a party goes into a dive, re-enters one at a rest area, or plays a
mission as a battle. A mission that's sent packs nothing, and a raid that's refused packs
nothing and changes nothing. No member holds a potion in the guild hall: there's no
handing one to a member in the Dorms, and every potion waits in the stores until a raid
packs it.

For a dive, the player chooses how many potions each member packs while planning the
party, and going in or re-entering packs exactly those from the stores. A member's count
runs from none up to their slots, and the party's total never passes what the stores
hold. While choosing, the player sees how many of that member's slots are still free for
loot and how many potions are left in the stores. For now each member starts at one as
they're picked, while the stores have any left, and the counts are never saved: leaving
the board drops them. A played mission has no planning step, so for now its start packs
one potion for each member from the stores, in the order the party was picked, for as
long as the stores last. A party with too few still goes in, and the members later in
the order go without.

For now a member drinks only from the potions in their own slots, one at a time, so one
member's potions never reach another, and a member who still holds one after drinking
can drink again. When the raid ends, every potion left undrunk goes back to the stores —
a dead member's too — and one drunk stays gone. If the whole party falls on a dive, every
potion packed for it is lost.
```

**Why:** The game is built this way. The original says potions take capacity and are
added at the start of the raid, but not which raids, how many each member takes, whose a
member drinks from, or where the undrunk ones go. Its "the choice is how much healing to
pay for in treasure" is why the player picks the count for a dive. Handing a potion to a
member in the Dorms went away with slots, since nobody holds one between raids. Every
"for now" here is a default the build chose, not yet the user's word: drinking from
one's own slots, and what a played mission packs, are proposed as questions in
"Questions on carrying"; whether an undrunk potion goes back to the stores, and what
happens to a dead member's, are already asked in Equipment's change "Questions on
shields and potions". Each member starting at one, and the counts not being saved, are
cheap to change.

## Change: Buff potions are packed for a dive and come back at its end, for now

> Proposed 2026-11-25 · for review

**Where:** `## Entering the Dungeon`, last paragraph (new paragraphs after it, after the
ones "Healing potions are packed at the start of a raid and come back at its end, for now"
adds)

**Now says:**

```
Potions take up the party's carrying capacity, and they're added to it at the start of
the raid.
```

**Proposed:**

```
Potions take up the party's carrying capacity, and they're added to it at the start of
the raid.

A buff potion takes one slot, the same as a healing potion, and counts as a potion
everywhere slots are counted, the room counted at the dive's end included. For a dive,
the player chooses how many of each buff kind each member packs while planning the party,
and going in or re-entering packs exactly those from the stores. Every kind starts at none
for each member. A member's potions of every kind together never pass their slots, and the
party's total of a kind never passes what the stores hold of it; while choosing, the
player sees what's left of each kind in the stores and how many of the member's slots are
still free. For now a played mission packs no buffs, and no buff drops as loot on a dive.

When the raid ends, every buff left unused goes back to the stores, a dead member's too,
and one used stays gone. If the whole party falls on a dive, every buff packed for it is
lost.
```

**Why:** The game is built this way, carrying buffs the way it carries healing potions.
The original's "A potion takes 1 slot" doesn't say whether a buff counts as one, and
nothing says how buffs are packed or where the unused ones go. A played mission packing
none, and no buff dropping as loot, are defaults the build chose, not yet the user's word,
proposed as questions in "Questions on buff potions in the dive". Each kind starting at
none is cheap to change.

## Change: A question on what gold a retreat keeps

> Proposed 2026-11-14 · for review

**Where:** `## Open Questions`, at the end of the list

**Now says:**

```
- How far can a training mission level a member?
```

**Proposed:**

```
- How far can a training mission level a member?
- When a party retreats partway through a floor, does it lose only that floor's gold and
  carry on with the gold it had before the floor, or all the gold found since the last
  rest area?
```

**Why:** The user, 2026-11-14: "they won't gain any of that gold for that level. You
should still continue with the gold they had. Before the level." The change "A party can
turn back anywhere, and gold takes no slots for now" has a retreat between rest areas
lose all the gold found since the last rest area, and the two may not agree.

## Change: Questions on the dive's defaults

> Proposed 2026-11-12 · for review

**Where:** `## Open Questions`, at the end of the list

**Now says:**

```
- How far can a training mission level a member?
```

**Proposed:**

```
- How far can a training mission level a member?
- What does a battle that ends in a stand-off do to the dive?
- Does gold take up slots, or does it ride free, with slots holding only potions and
  items of loot?
- How does a dead member's gear count against the party's carrying capacity, now counted
  in slots?
- When a member dies in the dungeon and the survivors don't have room for all of their
  gear, which pieces get left behind?
- Is the room for a dead member's gear counted when the dive ends, or when the member
  falls?
- After a dive where some of a fallen member's gear was left in the dungeon, should the
  end-of-dive screen say which pieces were lost?
- Is a floor's set of monsters the same every dive, or new each time?
- When does a floor count as reached, for the deepest floor reached?
- "The last rest area reached": is that the deepest rest area ever reached, or the one the
  most recent dive reached?
- While a dive is in progress, can the player leave it for the guild hall — hire, shop,
  change gear — and come back to it?
- If a dungeon is deeper than its last rest area, what happens when the bottom floor is
  cleared?
```

**Why:** The dive is built with a default for now on each of these but the last, in the
changes above and, for a dead member's gear, in Equipment's change "A dead member's gear
takes a slot a piece, for now": one slot a piece, pieces coming home in pick order,
weapon then armour then shield, the room counted as the dive ends, and no change to the
end-of-dive screen. None of the docs settles them. The last is open because nothing
says; the starting dungeon's depth is set to end on a rest area, so it doesn't come up
yet. The pending "A question on what gold a retreat keeps" change to this list is
unchanged.

## Change: Questions on healing in the dive

> Proposed 2026-11-13 · for review

**Where:** `## Open Questions`, at the end of the list

**Now says:**

```
- How far can a training mission level a member?
```

**Proposed:**

```
- How far can a training mission level a member?
- When a member levels up on the floor just cleared, is the heal between floors a share of
  their maximum health before the level-up or after it?
- When the party's heal and a Cook's land on a member at the same moment, are they added
  up and rounded once, or rounded one at a time?
- Which way does a heal's fraction of a point round?
```

**Why:** The dive is built with a default for now on each of these, in "How a heal in the
dive lands, for now", and none of the docs settles them. The pending changes to this list
above are unchanged.

## Change: Questions on carrying

> Proposed 2026-11-18 · for review

**Where:** `## Open Questions`, at the end of the list

**Now says:**

```
- How far can a training mission level a member?
```

**Proposed:**

```
- How far can a training mission level a member?
- During a raid, does each member drink only from the potions in their own slots, or does
  the party share them?
- Does a played mission pack healing potions into slots the way a dive does?
- Do potions and loot compete for slots during the dive, or only on the way out?
```

**Why:** The game is built with a default for now on the first two, in "Healing potions
are packed at the start of a raid and come back at its end, for now": each member
drinking from their own, and a played mission, which has no planning step, packing one
each in pick order while the stores last, where a dive packs what the player chose. The
last has a default too, in "For now a dive drops ore, herb and healing potions, and no
gear": loot takes room only on the way out, counted as the dive ends. The pending changes
to this list above are unchanged.

## Change: Questions on loot

> Proposed 2026-11-25 · for review

**Where:** `## Open Questions`, at the end of the list

**Now says:**

```
- How far can a training mission level a member?
```

**Proposed:**

```
- How far can a training mission level a member?
- When the free slots at the end of a dive can't hold both, which comes home first: the
  loot, or a fallen member's gear?
- What is "an item"? The Dungeon and Equipment say a dive yields "materials or items",
  but no doc names an item a dive drops.
- Does a unit of ore or herb carry a rank, from the dungeon it came from, or are all ore
  alike?
- Does "one enemy in four" mean each enemy rolls on its own, or that exactly a quarter of
  a floor's enemies drop?
- How often is a materials drop ore rather than herb, and how much is one drop?
- When the same floor is cleared on a later dive, are its drops rolled again, or fixed
  when the dungeon is made, as its monsters are?
- Can a healing potion that drops on a dive be drunk on that same dive?
- When the loot doesn't all fit on the way out, which is left behind?
```

**Why:** The dive is built with a default for now on each of these, in "For now a dive
drops ore, herb and healing potions, and no gear": the gear first, the healing potion,
each unit recording its dungeon's rank, each enemy rolling on its own, even odds and one
unit a slot, drops rolled again each dive, a dropped potion not drunk on its dive, and
potions then ore then herb, a higher rank first. None of the docs settles them. The
pending changes to this list above are unchanged.

## Change: Questions on buff potions in the dive

> Proposed 2026-11-25 · for review

**Where:** `## Open Questions`, at the end of the list

**Now says:**

```
- How far can a training mission level a member?
```

**Proposed:**

```
- How far can a training mission level a member?
- Does a played mission carry buff potions, and if so, how many of each, with no planning
  step to choose them?
- Can a buff potion drop as loot on a dive?
```

**Why:** The game is built with a default for now on both, in "Buff potions are packed for
a dive and come back at its end, for now": a played mission packs none, and no buff
drops. The pending changes to this list above are unchanged.

## Change: The guild keeps three saved teams

> Proposed 2026-11-20 · for review

**Where:** `## The Dungeon Board`, the paragraph beginning "The dungeon board is also
where the player enters a dungeon" (a new paragraph after it)

**Now says:**

```
The dungeon board is also where the player enters a dungeon, and where they re-enter at
the last rest area reached.
```

**Proposed:**

```
The dungeon board is also where the player enters a dungeon, and where they re-enter at
the last rest area reached.

The guild keeps three saved teams, Team 1, Team 2 and Team 3, saved with the guild. A
saved team is who goes and the spot each one stands on. While planning a party, the
player can pick a saved team, which fills the grid with its members on their saved spots
in place of whatever was planned, and the player edits from there. A team can be picked
only when every member in it is available — still in the guild, not injured and not out
on a mission; one that isn't shows but can't be picked. During a dive, between battles
and at a rest area, the player can save the party into any of the three, over whatever
it held: the members still alive, on the spots they stand on now. A saved team holds no
potions, so each member starts at one, as anyone picked does.
```

**Why:** The user, 2026-11-18: "I also what a place where i can save team formations.
give me 3 slots to save 3 team formations. a fomratoin is available to select for a
dongeon if all members in that team are available. clicking the formation auto populates
those characters for the doungon dive. While in the doungon dive you should be able to
save a formation to one of the 3 slots. for next time." The game is built this way. No
doc has saved teams. What "available" means, and a saved team holding no potions, are
defaults the build chose, not yet the user's word, and cheap to change.

## Change: Questions on the floor power budget

> Proposed 2026-11-24 · for review

**Where:** `## Open Questions`, at the end of the list

**Now says:**

```
- A drop the party has no room for is lost, which is the same rule a dead member's
  gear follows. Should a full party be able to throw something away to make room for
  a find instead?
```

**Proposed:**

```
- A drop the party has no room for is lost, which is the same rule a dead member's
  gear follows. Should a full party be able to throw something away to make room for
  a find instead?
- How does 8 : 7 : 6 : 5 : 4 round to whole stats?
- When an enemy's points (share ÷ count) come out at exactly a half, which way do they
  round?
```

**Why:** The game goes ahead with a default on both, in "How a floor's power becomes its
enemies, for now": stats that add up to the enemy's points with none below 1, and a half
rounding up. A half can only come up on the first and last fighting floors, where the
floor's power is a whole number. The pending changes to this list above are unchanged.
