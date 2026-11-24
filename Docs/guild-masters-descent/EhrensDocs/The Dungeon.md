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

## Change: For now a dive yields only gold

> Proposed 2026-11-11 · for review

**Where:** `## The Dungeon`, the paragraph beginning "Dungeon diving yields materials or items"

**Now says:**

```
Dungeon diving yields materials or items, and the floor itself pays gold. A dive can also
drop a weapon or a piece of armour on certain floors.
```

**Proposed:**

```
Dungeon diving yields materials or items, and the floor itself pays gold. A dive can also
drop a weapon or a piece of armour on certain floors. For now, though, loot is just gold:
in the first version a dive yields gold and nothing else — no materials, no items, and no
dropped gear.
```

**Why:** Answered: for now loot will just be gold. The paragraph and the list after it
name materials, items and dropped gear as what a dive yields, which the first version
doesn't do; the new sentence scopes the first version and leaves the longer-term design
standing.

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
floor's battles play straight through, back to back. The first dungeon has 3 battles a
floor to win. After the last one comes victory, dropping loot: the floor's gold drops as
one lump at the end of the floor, and only once every battle on that floor is won — if a
floor has 3 battles, the party needs to beat all 3.
```

**Why:** Answered: each floor is a series of battles, and at the end of a battle the
screen scrolls right into the next one; the first dungeon has 3 battles to win, then
victory, dropping loot. Answered too: loot at the end of the floor — if 3 battles on that
floor then they need to beat all 3. "Each floor has 1–3 battles" gave the count but not
how one battle leads into the next, or where the loot drops. The 3 battles are inside the
original's 1–3 range, so the range stays for dungeons in general. What the board's floor layout shows, whether a party picks a route, and what makes a
boss floor are not settled by this. The rest of the paragraph, on rest areas and
retreating, is the next change. Answered 2026-11-14, too: "you enter a level and the
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
gold found since the last rest area. "Anywhere" includes the middle of a battle: a
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

In a battle, for now, a monster's damage is its damage stat alone and its defence its
Constitution alone — there's no weapon or armour in either.
```

**Why:** Answered: the enemies are monsters, but for now we might be limited to just the
archer animations. Answered too, on gear: fixed numbers. The yellow-shape clause is the
project's standing rule for missing art. A monster's rank follows Combat's `## Enemies`:
an enemy is the dungeon's rank or one grade below it. The first paragraph is unchanged.
How a monster fights is a default for now: the answer on gear was fixed numbers, read as
the monster's own stats with nothing added for gear, while The Dungeon's `## The Dungeon`
gives an enemy a chance of a weapon from the first floor and of armour from floor 11,
rising with the floor.
For the owner to reconcile: `Individual Types.md` explains two type traits by gear — the
Brute's tanned hide adds a little defence, and the Rogue's weapon adds less damage — and
a monster Brute or Rogue carries none for now.

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

For now a floor's monsters are the same on every dive: which monsters, their levels and
where they stand are set once, when the dungeon is created, and a dungeon from an older
save keeps the monsters it was made with. Each monster stands on a node of its own, drawn
at random. A floor counts as reached once the party starts its first battle there, or
arrives there if it's a rest area.
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
last doesn't come up until a dive yields items. The pending changes to this list above
are unchanged.

## Change: Party planning is one screen

> Proposed 2026-11-16 · for review

**Where:** `## The Dungeon Board`, the paragraph beginning "Planning happens in two steps"

**Now says:**

```
Planning happens in two steps: the player selects the members first, then arranges them
on the grid. That second step is a zoomed-in view of the battle map rather than a
separate screen. The system does the initial placement, putting combat types in front and
making support links where it can — the player can edit it from there.
```

**Proposed:**

```
Party planning is one screen. The guild's characters are listed on the left, each showing
who it is — picture, type, name and level — and the placement grid is on the right. The
player picks, places and rearranges at the same time, and can see everyone they are
taking, up to 15. As each member is added, the game still places them first, putting
combat types in front and making support links where it can, and the player edits from
there. Taking a member off the grid puts them back in the list.
```

**Why:** The user, 2026-11-16: "If we choose our members we can choose up to 15 members
but I won't be able to see them all. So let's design the select your characters, place
your characters on the same screen where we have the list of the characters on the left
and the placement on the right side. This way they can place and rearrange at the same
time, knowing who they are getting."

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
defaults the build chose, not yet the user's word, and cheap to change. The pending
"Party planning is one screen" change to the paragraph before is unchanged.
