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
return to the top and exit the dungeon. For now a rest area is a safe floor with no
battles on it, so it drops no gold and gives no experience. The party can turn back
anywhere, not only at a rest area — but leaving between rest areas loses the gold found
since the last rest area. For now "anywhere" means between two battles, not in the middle
of one, and a battle that ends in a stand-off counts as the party turning back there.

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
third paragraph, and with defaults on rest areas, turning back mid-battle and stand-offs
in the first; each is proposed as a question for `## Open Questions`.

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
that type's attacks, its special and its type advantages. Monsters carry no gear.

A monster is given a level like a member is, and uses the same stat rules. Deeper floors
have higher-level monsters. What level the monsters on each floor are is a placeholder,
to be balanced later.

In a battle, for now, a monster's damage is its damage stat alone and its defence its
Constitution alone — there's no weapon or armour in either. Its health follows a
member's: for now that's the 10 a new F-rank member starts with, whatever the monster's
level. Monsters get the support ring among themselves, a special bar and the Tank's taunt
the same as members do, and a monster uses its special as soon as its bar is full.
```

**Why:** Answered: the enemies are monsters, but for now we might be limited to just the
archer animations. Answered too: yes, monsters will be assigned one of the types just
like the characters and have those same characteristics of that type; on gear, fixed
numbers; and on where a monster's strength comes from, levels, with deeper floors having
higher-level monsters. The docs gave enemies a grid, targeting and repositioning but
never said what they are. The yellow-shape clause is the project's standing rule for
missing art. The first paragraph is unchanged. With monsters carrying combat types,
`Guild Members.md`'s example of "an enemy force of, say, nine Brutes" fits as written.
How a monster fights is a default for now: the answer on gear was fixed numbers, read as
the monster's own stats with nothing added for gear — while a member's damage is its stat
plus its weapon and its defence is Constitution plus its armour — and its health, the
support ring, the bar and the taunt follow a member's.
For the owner to reconcile: `Individual Types.md` explains two type traits by gear — the
Brute's tanned hide adds a little defence, and the Rogue's weapon adds less damage — and
a monster Brute or Rogue carries none. `## The Dungeon Board`'s "the types of monster and
enemy found in each of the dungeons" is left as it is.

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
where they stand are set once, when the dungeon is created. A floor counts as reached
once the party starts its first battle there, or arrives there if it's a rest area.
```

**Why:** The dive is built this way. "Appear as the party reaches each floor" reads as a
floor's enemies being fixed, but nothing said so outright, or what counts as reaching a
floor for the deepest floor reached. Both are proposed as questions for
`## Open Questions`.

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

For now the entry fee is so much for each member of the party, and the teleportation fee
is one flat amount whatever the party's size. Both amounts are placeholders.

For now, once a party is in, the guild hall can't be reached until the dive ends — no
hiring, shopping or changing gear partway through a dive and then carrying on with it.
```

**Why:** The dive is built this way. "The last rest area reached" reads two ways — the
deepest one ever reached, or the one the most recent dive reached — and nothing said
whether the teleportation fee grows with the party the way the entry fee does, or whether
the player can leave a dive for the guild hall and come back to it. All three are
proposed as questions for `## Open Questions`.

## Change: A question on turning back mid-battle

> Proposed 2026-11-12 · for review

**Where:** `## Open Questions`, at the end of the list

**Now says:**

```
- How far can a training mission level a member?
```

**Proposed:**

```
- How far can a training mission level a member?
- Can a party turn back in the middle of a battle, or only between battles?
```

**Why:** "The party can turn back anywhere" doesn't say whether that includes the middle
of a battle.

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
pending "A question on turning back mid-battle" change to this list is unchanged.
