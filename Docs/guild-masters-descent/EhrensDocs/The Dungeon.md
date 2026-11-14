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

**Where:** `## The Dungeon`, third paragraph

**Now says:**

```
Dungeon diving yields materials or items, and sometimes small amounts of gold. A dive can
also drop a weapon or a piece of armour.
```

**Proposed:**

```
Dungeon diving yields materials or items, and sometimes small amounts of gold. A dive can
also drop a weapon or a piece of armour. For now, though, loot is just gold: in the first
version a dive yields gold and nothing else — no materials, no items, and no dropped gear.
```

**Why:** Answered: for now loot will just be gold. The paragraph names materials, items and
dropped gear as what a dive yields, which the first version doesn't do; the new sentence
scopes the first version and leaves the longer-term design standing.

## Change: A floor is a series of battles that scrolls right into the next

> Proposed 2026-11-11 · for review

**Where:** `## The Dungeon`, second paragraph, its first sentence (the paragraph beginning
"Each floor has 2–3 battles.")

**Now says:**

```
Each floor has 2–3 battles.
```

**Proposed:**

```
Each floor is a series of battles, 2–3 of them. At the end of a battle the screen scrolls
right into the next battle, with no result screen and nothing to click in between: a
floor's battles play straight through, back to back. The first dungeon has 3 battles a
floor to win. After the last one comes victory, dropping loot: the floor's gold drops as
one lump at the end of the floor, and only once every battle on that floor is won — if a
floor has 3 battles, the party needs to beat all 3. How much gold a floor drops is a
placeholder, to be balanced later. For now every battle on a floor has the same number of
monsters, set by the floor: a deeper floor never has fewer, and the deepest floor with
battles has more than the first. How many is a placeholder too, to be balanced later.
```

**Why:** Answered: each floor is a series of battles, and at the end of a battle the
screen scrolls right into the next one; the first dungeon has 3 battles to win, then
victory, dropping loot. Answered too: loot at the end of the floor — if 3 battles on that
floor then they need to beat all 3. "Each floor has 2–3 battles" gave the count but not
how one battle leads into the next, or where the loot drops. The 3 battles are inside the
existing 2–3 range, so the range stays for dungeons in general. How many monsters a battle
has follows Combat's `## Enemies` — the deeper the floor, the more enemies turn up in each
fight — and the dive is built with a set number for each floor, the same every battle on
it. What the board's floor layout shows, whether a party picks a route, and what makes a
boss floor are not settled by this. The rest of the paragraph, on rest areas and
retreating, is the next change. Answered 2026-11-14, too: "you enter a level and the
level should go through" — a floor's battles play back to back, with no screen after
each one showing what was gained and waiting for a click on Continue.

## Change: A party can turn back anywhere, and carries only so much gold out

> Proposed 2026-11-11 · for review

**Where:** `## The Dungeon`, second paragraph, from "Every 5th floor is a safe rest area" to
the end of the paragraph

**Now says:**

```
Every 5th floor is a safe rest area, where every member gets back fifteen per cent, and
the player may choose to return to the top and exit the dungeon. The Cook adds to both
figures, covered in the Specialists doc. Retreating always costs the loot gathered since
the last safe floor — any party member can carry some of it, so how much is lost depends
on who came along.
```

**Proposed:**

```
Every 5th floor is a safe rest area, where every member gets back fifteen per cent, and
the player may choose to return to the top and exit the dungeon. The Cook adds to both
figures, covered in the Specialists doc. For now a rest area is a safe floor with no
battles on it, so it drops no gold and gives no experience. The party can turn back
anywhere, not only at a rest area — but leaving between rest areas loses the gold found
since the last rest area. "Anywhere" includes the middle of a battle: a Retreat button
is there all through a floor's battles, and the party can leave with it at any moment.
For now a battle that ends in a stand-off counts as the party turning back there.

There is a carry limit for each person. Each member can carry up to 10 gold coming out,
and each Porter up to 100. Gold beyond what the party can carry is left behind. Both
numbers are made up for now, to be balanced later.

For now a Porter's 100 is on top of the 10 every member carries. The party holds all the
gold it finds while it's inside, and the limit only bites on the way out: leaving between
rest areas first loses the gold found since the last one, and then whatever is left over
the limit stays behind. Only the living carry, so a party with no one left alive brings
nothing out. A dead member's gear doesn't count against the limit.
```

**Why:** Answered: yes, there is a carry limit each person — up to 10 gold coming out, a
Porter 100 gold per porter, made-up numbers to balance later. And: yes, turn back
anywhere, losing the gold found since the last rest area. The original names the rest
area as where the player may exit, and its retreat sentence only implies leaving
elsewhere; this says so outright. "Any party member can carry some of it, so how much is
lost depends on who came along" no longer holds: turning back between rest areas loses
all the gold found since the last rest area whoever came along, and who came along
decides instead how much gold comes out at all. Not settled by this: whether a Porter's
100 is on top of the 10 every member carries, how much more the Herbalist and the Miner
carry, and how a dead member's gear counts against a limit measured in gold.
The dive is built with a default for now on the first and the last of those, in the
third paragraph, and with defaults on rest areas and stand-offs in the first; each is
proposed as a question for `## Open Questions`. Answered 2026-11-14: the party can
retreat at any time, the middle of a battle included — "you can holler a retreat sign
that will take them out". Which gold a retreat keeps is proposed as a question in
"A question on what gold a retreat keeps".

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
comes back between the battles on a single floor. A rest area's fifteen per cent is in
place of the five, not on top of it, and a Cook's is the same — its fifteen there, not
its five as well. Clearing the floor before a rest area gives the fifteen alone, and
pushing on from the rest area to the next floor gives nothing, so floors 4 → 5 → 6 give
one fifteen per cent and no five. For now a heal is a share of the maximum health a
member has once the floor's last battle has shared its experience, so a level-up on that
floor counts. Everything that lands on a member at
once — the party's share and every Cook's — is added up first and turned into health
once, and a fraction of a point rounds up, so every living member gets at least one point
back. A heal never takes anyone past their maximum.
```

**Why:** Answered 2026-11-13: "OK, then just the 15%" — arriving at a rest floor gives the
fifteen per cent only, never the five as well, and a Cook adds its fifteen only, not its
five too. The question goes from Guild Members.md's `## Open Questions` (see "Rest-floor
heal question answered" in its change notes). The rest of the paragraph is how the dive is
built. Nothing said which maximum a heal is a share of
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

Every monster is assigned one of the six combat types, just like the guild's members,
and has the same characteristics of that type — a monster Tank or a monster Archer has
that type's attacks, its special and its type advantages.

A monster is given a rank and a level like a member is, and uses the same stat rules. For
now every monster in a dungeon is the dungeon's own rank — F, as the guild's starting
dungeon is, and there's no grade below F — and level 1, with exactly its type's starting
stats at that rank, on every floor. Depth changes how many monsters turn up in a battle,
never what each one is.

In a battle, for now, a monster's damage is its damage stat alone and its defence its
Constitution alone — there's no weapon or armour in either. Monsters get the support ring
among themselves, a special bar and the Tank's taunt the same as members do, and a
monster uses its special as soon as its bar is full.
```

**Why:** Answered: the enemies are monsters, but for now we might be limited to just the
archer animations. Answered too: yes, monsters will be assigned one of the types just
like the characters and have those same characteristics of that type; and on gear, fixed
numbers. Combat's `## Enemies` builds enemies from the six combat types and asks, in its
open questions, whether a monster is something other than that; this says it isn't. The
yellow-shape clause is the project's standing rule for missing art. A monster's rank and
level follow Combat's `## Enemies` too: an enemy is the dungeon's rank or one grade below
it, with exactly what its type and rank give, and depth decides how many turn up, not what
each one is. The first paragraph is unchanged. How a monster fights is a default for now:
the answer on gear was fixed numbers, read as the monster's own stats with nothing added
for gear, while Combat's `## Enemies` gives an enemy a chance of a weapon and of armour
set by the dungeon's rank.
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

## Change: Where a party re-enters, and what it pays, for now

> Proposed 2026-11-12 · for review

**Where:** `## Entering the Dungeon`, last paragraph (new paragraphs after it)

**Now says:**

```
The player re-enters at the last rest area reached, and must pay the entry fee again plus
a teleportation fee. This stops the player exploring five floors, returning, and
rearranging the party with no penalty.
```

**Proposed:**

```
The player re-enters at the last rest area reached, and must pay the entry fee again plus
a teleportation fee. This stops the player exploring five floors, returning, and
rearranging the party with no penalty.

For now the last rest area reached is the deepest one the most recent dive reached, and
a dive that re-entered counts the rest area it started at. So the re-entry point can move
back up, from floor 10 to floor 5, and a dive that reaches no rest area leaves none. Any
party can re-enter, not only the one that got there, and its first battle is on the floor
after the rest area. There's no re-entering at a rest area with no floor past it.

For now the entry fee is so much for each member of the party, and how much depends on
the dungeon's rank — the lower the rank, the cheaper the fee, and the less gold its floors
drop. An F-rank dungeon costs 2 gold a member, so a party of three pays 6 and the first
floor's 8 gold more than pays it back. Each rank up costs more per member and drops more
gold a floor. The teleportation fee stays one flat amount whatever the party's size. All
the amounts are placeholders.

For now, once a party is in, the guild hall can't be reached until the dive ends — no
hiring, shopping or changing gear partway through a dive and then carrying on with it.
```

**Why:** The dive is built this way. "The last rest area reached" reads two ways — the
deepest one ever reached, or the one the most recent dive reached — and nothing said
whether the teleportation fee grows with the party the way the entry fee does, or whether
the player can leave a dive for the guild hall and come back to it. All three are
proposed as questions for `## Open Questions`. Answered 2026-11-14, too, on the entry
fee: "it takes 10 gold per person to send them into the dungeon after completing three
fights. I only get eight gold. ... That's financially bankrupt me instantly in the game.
... We need to make the entrance fee a lot cheaper for these dungeons. The cheaper, the
dungeon, the cheaper the entrance fee that might be a necessary thing. Then the lesser
the reward." At 10 gold a member a party of three paid 30 to win 8 on floor 1.

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
turn back anywhere, and carries only so much gold out" has a retreat between rest areas
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
- Is a rest-area floor a floor of battles with a rest at the end, or a safe floor with no
  battles?
- What does a battle that ends in a stand-off do to the dive?
- Does a Porter carry 100 in total, or 110 — the 100 on top of the 10 everyone carries?
- When does the carry limit bite: is extra gold lost as soon as it's found, or only when
  the party walks out?
- How does a dead member's gear count against a carry limit measured in gold?
- Is a floor's set of monsters the same every dive, or new each time?
- When does a floor count as reached, for the deepest floor reached?
- "The last rest area reached": is that the deepest rest area ever reached, or the one the
  most recent dive reached?
- Is the teleportation fee flat, or does it rise with party size the way the entry fee
  does?
- While a dive is in progress, can the player leave it for the guild hall — hire, shop,
  change gear — and come back to it?
- If a dungeon is deeper than its last rest area, what happens when the bottom floor is
  cleared?
```

**Why:** The dive is built with a default for now on each of these but the last, in the
changes above, and none of the docs settles them. The last is open because nothing says;
the starting dungeon's depth is set to end on a rest area, so it doesn't come up yet. The
pending "A question on what gold a retreat keeps" change to this list is unchanged.

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
