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
Dungeon diving yields materials or items, and sometimes small amounts of gold.
```

**Proposed:**

```
Dungeon diving yields materials or items, and sometimes small amounts of gold. For now,
though, loot is just gold: in the first version a dive yields gold and nothing else — no
materials, no items, and no dropped gear.
```

**Why:** Answered: for now loot will just be gold. The paragraph names materials and items
as what a dive yields, which the first version doesn't do; the new sentence scopes the
first version and leaves the longer-term design standing.

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
right into the next battle. The first dungeon has 3 battles a floor to win, against 1
low-level monster each. After the last one comes victory, dropping loot: the floor's gold
drops as one lump at the end of the floor, and only once every battle on that floor is
won — if a floor has 3 battles, the party needs to beat all 3. How much gold a floor drops
is a placeholder, to be balanced later.
```

**Why:** Answered: each floor is a series of battles, and at the end of a battle the
screen scrolls right into the next one; the first dungeon has 3 battles to win against 1
low-level monster each, then victory, dropping loot. Answered too: loot at the end of the
floor — if 3 battles on that floor then they need to beat all 3. "Each floor has 2–3
battles" gave the count but not how one battle leads into the next, or where the loot
drops. The 3 battles are inside the existing 2–3 range, so the range stays for dungeons in
general. What the board's floor layout shows, whether a party picks a route, and what
makes a boss floor are not settled by this. The rest of the paragraph, on rest areas and
retreating, is the next change.

## Change: A party can turn back anywhere, and carries only so much gold out

> Proposed 2026-11-11 · for review

**Where:** `## The Dungeon`, second paragraph, the sentences after the first ("Every 5th
floor is a safe rest area" to the end of the paragraph)

**Now says:**

```
Every 5th floor is a safe rest area, where the party heals and the player may choose to
return to the top and exit the dungeon. Retreating always costs the loot gathered since
the last safe floor — any party member can carry some of it, so how much is lost depends
on who came along.
```

**Proposed:**

```
Every 5th floor is a safe rest area, where the party heals and the player may choose to
return to the top and exit the dungeon. The party can turn back anywhere, not only at a
rest area — but leaving between rest areas loses the gold found since the last rest area.

There is a carry limit for each person. Each member can carry up to 10 gold coming out,
and each Porter up to 100. Gold beyond what the party can carry is left behind. Both
numbers are made up for now, to be balanced later.
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

## Change: The dungeon's enemies are monsters

> Proposed 2026-11-11 · for review

**Where:** `## The Dungeon`, first paragraph (a new paragraph after it)

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
```

**Why:** Answered: the enemies are monsters, but for now we might be limited to just the
archer animations. The docs gave enemies a grid, targeting and repositioning but never
said what they are. The yellow-shape clause is the project's standing rule for missing
art. The first paragraph is unchanged. Not settled by this: whether monsters use the six
combat types' attacks, specials and type advantage; whether they carry gear; and where
their stats come from. For the owner to reconcile: `Guild Members.md`, `## The Support
Ring`, gives the example "an enemy force of, say, nine Brutes" — the Brute is a guild
combat type, so either monsters carry combat types or the example wants a monster in
place of the Brute. `## The Dungeon Board`'s "the types of monster and enemy found in
each of the dungeons" is left as it is.
