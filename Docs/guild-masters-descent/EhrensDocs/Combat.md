# Combat — proposed changes

> **Status:** Change notes against `Combat.md`, for its owner to review. The original is not
> edited.

## Change: Changing formation mid-battle is free

> Proposed 2026-11-11 · for review

**Where:** `## Formation`, third paragraph

**Now says:**

```
The player can also change formation in the middle of battle — formation is ongoing battle
planning rather than a one-time puzzle. Some enemy types can reposition mid-battle too,
but not all of them can.
```

**Proposed:**

```
The player can also change formation in the middle of battle — formation is ongoing battle
planning rather than a one-time puzzle. Changing formation mid-battle is free for now.
Some enemy types can reposition mid-battle too, but not all of them can.
```

**Why:** The original lets the player change formation mid-battle and names no cost, so it
stays free for now.

## Change: Status line no longer lists formation cost as open

> Proposed 2026-11-11 · for review

**Where:** the `> **Status:**` line at the top

**Now says:**

```
> **Status:** Early design. Nothing is built yet — the grid, the turn order and how gear
> breaks are settled, but what changing formation mid-battle costs isn't.
```

**Proposed:**

```
> **Status:** Early design. Nothing is built yet — the grid, the turn order, how gear
> breaks and what changing formation mid-battle costs are settled.
```

**Why:** The one open item it named is now settled (see the change on Formation).

## Change: Formation-cost question answered

> Proposed 2026-11-11 · for review

**Where:** `## Open Questions`

**Now says:**

```
- What does changing formation mid-battle cost the player, if anything?
```

**Proposed:** delete. The `## Open Questions` heading stays, with the entries proposed in
"Questions on turn order and taunts" below.

**Why:** Answered: free for now, written into Formation.

## Change: Members stay hurt from battle to battle, and 0 health is death

> Proposed 2026-11-11 · for review

**Where:** `## Combat`, last paragraph (new paragraphs after it)

**Now says:**

```
Each strike of a multi-strike attack is resolved on its own: it rolls to hit separately,
and defence is subtracted from it separately.
```

**Proposed:**

```
Each strike of a multi-strike attack is resolved on its own: it rolls to hit separately,
and defence is subtracted from it separately.

A member stays hurt from battle to battle: damage taken in one battle is still there at
the start of the next, all the way through a dive. Health comes back only from the Cook,
from a rest area, and from going home.

When a member's health reaches 0 in a battle on a dive, they die on the spot, for good.

Health only matters inside a dive. Back at the guild hall a member's health is back to
full; injury is what carries from one dive to the next.

For now a dive never leaves a member injured: a member comes home fine, or doesn't come
home. Where everyone stands at the end of a battle is where they start the next one, and
the dead leave their places empty. A special bar doesn't carry over — every bar starts
each battle empty.
```

**Why:** Answered: health — stay hurt from battle to battle. Answered too: a member whose
health hits 0 in a dungeon battle dies on the spot, for good; and back at the guild hall
health is back to full — health only matters inside a dive, and injury is what carries
between dives. No doc said what happens to health after a battle, at 0, or after a dive,
though The Dungeon's rest area "where the party heals" and Specialists' Cook, who "heals a
little after every battle", only make sense if damage outlives a battle. The existing
paragraph is unchanged, and The Dungeon's "Death in the dungeon is permanent" already
agrees. Not settled by this: what reaching 0 health does on a training run, which "can
injure a member, but can never kill one"; whether a dive can leave a member injured; and
how much health the Cook and a rest area give back.
The dive is built with a default for now on whether a dive can leave a member injured,
and on two things nothing raised — whether the formation and the special bars carry from
one battle to the next — in the last paragraph; each is proposed as a question for
`## Open Questions`.

## Change: Turn order within a round, and how a battle ends

> Proposed 2026-11-12 · for review

**Where:** `## Combat`, first paragraph (a new paragraph after it)

**Now says:**

```
Combat is turn-based tactics. Turn order is determined by Dexterity — the members' and the
enemies'. On a guild member's turn, that member is highlighted. Default attacks are
auto-selected. The player can select one enemy to be specifically targeted by the entire
party — this cuts down on clicks during gameplay.
```

**Proposed:**

```
Combat is turn-based tactics. Turn order is determined by Dexterity — the members' and the
enemies'. For now everyone acts once a round, members and enemies in one shared order,
highest Dexterity first. The order is set at the start of each round from each one's own
Dexterity, so help from the support ring never moves anyone in it. Ties go to members
before enemies, then front row first, left to right. On a guild member's turn, that
member is highlighted. Default attacks are auto-selected. The player can select one enemy
to be specifically targeted by the entire party — this cuts down on clicks during
gameplay. A member with no enemy selected, or who can't reach the one selected, picks
its target the way an enemy does.

A battle ends when one side has no one left standing. For now a battle also ends after a
set number of rounds, a placeholder, as a stand-off — and a stand-off kills no one
further.
```

**Why:** The combat engine is built this way, and no doc said how many times a combatant
acts, whether help changes the order, how ties break, what a member does with no target
selected, or whether a battle can run forever. The original sentences are unchanged;
the new ones sit between them. Whether higher Dexterity should mean acting more often, and
whether help to Dexterity should move anyone in the order, stay open — see the questions
proposed for `## Open Questions`.

## Change: The base charge is once per attack, and a special empties the bar

> Proposed 2026-11-12 · for review

**Where:** `## Combat`, second paragraph

**Now says:**

```
Each member has a special bar. When it's full, the player can use a special. Every
attack a member makes charges that member's bar — that's the base, and it's the same
for every type. Each combat type also has its own bonus condition that charges its bar
on top of that.
```

**Proposed:**

```
Each member has a special bar. When it's full, the player can use a special. Every
attack a member makes charges that member's bar — that's the base, and it's the same
for every type. Each combat type also has its own bonus condition that charges its bar
on top of that. The base charge comes once per attack, whether the attack hits or not.
Using a special empties the bar, and the special then charges it like any other attack,
unless its type says otherwise — the Fighter's flurry doesn't. A special takes the
turn in place of the ordinary attack. For now that holds for Vanish, Shields Up and the
field too, which strike no one: on the turn one of them is cast, its caster makes no
ordinary attack.
```

**Why:** The combat engine is built this way. "Every attack" didn't say whether a miss
charges, or whether a multi-strike attack charges once or per strike, and nothing said
what using a special does to the bar. Nothing said whether a special that strikes no one leaves the caster its ordinary attack as well; the six combat types are built with the special as the whole turn, and that's proposed as a question below.

## Change: Whose turns an effect's length counts

> Proposed 2026-11-12 · for review

**Where:** `## Combat`, third paragraph

**Now says:**

```
Vanish, Shields Up and the Mage's lingering field all last the same length — the same
fixed number of turns. Each of the three is covered in the Individual Types doc.
```

**Proposed:**

```
Vanish, Shields Up and the Mage's lingering field all last the same length — the same
fixed number of turns, a placeholder. The turns counted are the caster's own: the turn it
was cast on doesn't count, and it lasts that many of the caster's turns after. If the
caster dies, the effect ends with it — a Tank's Shields Up goes when the Tank does. For
now a Shields Up or a field cast while the caster's last one is still running stacks
with it: both run, each to its own end, so the two lots of defence add up and both fields
do their damage. Each of the three is covered in the Individual Types doc.
```

**Why:** The combat engine is built this way. "A fixed number of turns" didn't say whose
turns, whether the cast turn counts, or what happens to an effect when its caster dies. Nothing said what happens when one is cast again while the last is still running; the six combat types are built to stack them, and that's proposed as a question below.

## Change: What the targeting weights count, and how a taunt is spent

> Proposed 2026-11-12 · for review

**Where:** `## Enemy Targeting`, the paragraph (a new paragraph after it)

**Now says:**

```
Enemies pick a target from whatever they can reach. The choice is weighted by both how
much damage that target has dealt and how easy it is to kill. A taunt overrides both of
those factors until the taunted enemy's next hit — one attack, then it's spent.
```

**Proposed:**

```
Enemies pick a target from whatever they can reach. The choice is weighted by both how
much damage that target has dealt and how easy it is to kill. The damage counted is what
the target has dealt in this battle, the Mage's lingering field included; how easy it is
to kill is how low its health is now, next to the others the enemy can reach. How much
each counts is a placeholder. A taunt overrides both of those factors until the taunted
enemy's next hit — one attack, then it's spent.

The taunt is spent by that attack whether it hits or misses. While the taunter is out of
reach, the taunted one picks as normal, and the taunt keeps for its next attack that can
reach the taunter. A newer taunt replaces an older one, and a taunt ends if the taunter
dies. A taunt overrides the party's selected enemy too: a member taunted by an enemy Tank
goes for the Tank.
```

**Why:** The combat engine is built this way. "Damage dealt" didn't say over what span,
and "easy to kill" didn't say how it's judged. "Next hit — one attack" read two ways; this
takes it as one attack, hit or miss. Nothing said what a taunt does while the taunter is
out of reach, when two taunts overlap, when the taunter dies, or against the party's
selected enemy — and with monsters having the six types, a monster Tank taunts members.

## Change: Questions on turn order and taunts

> Proposed 2026-11-12 · for review

**Where:** `## Open Questions`, in place of the formation-cost entry deleted above

**Now says:**

```
- What does changing formation mid-battle cost the player, if anything?
```

**Proposed:**

```
- Should higher Dexterity mean acting more often, rather than only acting earlier?
- Should help to a Rogue's or an Archer's Dexterity move them in the turn order?
- When a taunted member or enemy uses a special that hits its own choice of targets
  rather than one it aims at, is the taunt spent?
- On the turn a Rogue casts Vanish, a Tank uses Shields Up or a Mage casts its field,
  does it also make its ordinary attack?
- If a Tank uses Shields Up, or a Mage casts its field, while its last one is still
  running, do the two stack, or does the new one replace the old?
- Can a dive leave a member injured?
- Does the formation carry from one battle to the next?
- Does a special bar carry over from one battle of a dive to the next?
```

**Why:** None of the docs answers these. The turn order above is a default for now. The
third question comes from how a taunt is spent once the six types' specials are built. The last two come from the specials that strike no one, as the six combat types are built.
The last three come from the dive as it's built: each has a default for now in "Members
stay hurt from battle to battle, and 0 health is death".
