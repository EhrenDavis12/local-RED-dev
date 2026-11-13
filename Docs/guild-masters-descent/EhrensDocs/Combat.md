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
> **Status:** Early design. Nothing is built yet — the grid, the cooldown pacing, the Luck
> reset's chance, and the never-pausing simulation are settled; whether a fight can be
> sped up, how multi-strike cases resolve, what formation costs, how the bars read at a
> glance, and whether the enemy grid keeps filling are not.
```

**Proposed:**

```
> **Status:** Early design. Nothing is built yet — the grid, the cooldown pacing, the Luck
> reset's chance, the never-pausing simulation and what formation costs are settled;
> whether a fight can be sped up, how multi-strike cases resolve, how the bars read at a
> glance, and whether the enemy grid keeps filling are not.
```

**Why:** What formation costs is now settled (see the change on Formation).

## Change: Formation-cost question answered

> Proposed 2026-11-11 · for review

**Where:** `## Open Questions`

**Now says:**

```
- What does changing formation mid-battle cost the player, if anything?
```

**Proposed:** delete. The other entries in `## Open Questions` stay as they are.

**Why:** Answered: free for now, written into Formation.

## Change: Health is full at the guild hall, and where everyone stands carries over

> Proposed 2026-11-11 · for review

**Where:** `## Attacks and Reach`, last paragraph (new paragraphs after it)

**Now says:**

```
Each strike of a multi-strike attack is resolved on its own: it rolls to hit separately,
and the defender's mitigation is applied to it separately.
```

**Proposed:**

```
Each strike of a multi-strike attack is resolved on its own: it rolls to hit separately,
and the defender's mitigation is applied to it separately.

Health only matters inside a dive. Back at the guild hall a member's health is back to
full; injury is what carries from one dive to the next.

For now a dive never leaves a member injured: a member comes home fine, or doesn't come
home. Where everyone stands at the end of a battle is where they start the next one, and
the dead leave their places empty.
```

**Why:** Answered: back at the guild hall health is back to full — health only matters
inside a dive, and injury is what carries between dives. No doc says what happens to
health after a dive. The existing paragraph is unchanged. Not settled by this: what
reaching 0 health does on a training run, which "can injure a member, but can never kill
one", and whether a dive can leave a member injured. The dive is built with a default for
now on that, and on one thing nothing raised — whether the formation carries from one
battle to the next — in the last paragraph; each is proposed as a question for
`## Open Questions`.

## Change: How a member with no target picks one, and how a battle ends

> Proposed 2026-11-12 · for review

**Where:** `## Player Input`, first and second paragraphs (a new paragraph after the second)

**Now says:**

```
Default attacks are auto-selected. The player can select one enemy to be specifically
targeted by the entire party — this cuts down on clicks during gameplay.

The fight never pauses, and nothing waits for the player. It runs from start to finish,
and the player acts while it's running — using a member's special once that bar is full,
changing formation, and marking the focus target.
```

**Proposed:**

```
Default attacks are auto-selected. The player can select one enemy to be specifically
targeted by the entire party — this cuts down on clicks during gameplay. A member with
no enemy selected, or who can't reach the one selected, picks its target the way an
enemy does.

The fight never pauses, and nothing waits for the player. It runs from start to finish,
and the player acts while it's running — using a member's special once that bar is full,
changing formation, and marking the focus target.

A battle ends when one side has no one left standing. For now a battle also ends after a
set length of time, a placeholder, as a stand-off — and a stand-off kills no one further.
```

**Why:** The combat engine is built this way. No doc says what a member does with no
target selected, or whether a battle can run forever. The original sentences are
unchanged; the new ones sit after them.

## Change: A special's own hits charge the bar, for now

> Proposed 2026-11-12 · for review

**Where:** `## The Special Bar`, third paragraph

**Now says:**

```
The bar caps at full — the special is never lost, and it waits until the player uses it.
While it sits full, charge is wasted: attacks the member makes while full charge nothing,
and so does the type's bonus condition — that progress toward the next special is gone.
Using the special empties the bar, and it charges again from there.
```

**Proposed:**

```
The bar caps at full — the special is never lost, and it waits until the player uses it.
While it sits full, charge is wasted: attacks the member makes while full charge nothing,
and so does the type's bonus condition — that progress toward the next special is gone.
Using the special empties the bar, and it charges again from there. For now the
special's own hits charge it like any other attack's, unless its type says otherwise.
```

**Why:** The combat engine is built this way. Nothing says whether a special's own hits
charge the bar it has just emptied. Whether using a special also costs the member an
ordinary attack is proposed as a question below.

## Change: When an effect's count starts, and a second cast stacking

> Proposed 2026-11-12 · for review

**Where:** `## Lasting Effects`, last paragraph (a new paragraph after it)

**Now says:**

```
A lasting effect ends when the member whose effect it is dies. That isn't obvious for
the two of the three that sit somewhere other than on their owner: the Mage's lingering
field sits on the battlefield rather than on the Mage, and Shields Up's defence sits on
the allies behind the Tank rather than on the Tank. The duration is a count of the
owner's own cooldown cycles, and a member who is dead completes no more of them, so
there's no clock left for the effect to run on.
```

**Proposed:**

```
A lasting effect ends when the member whose effect it is dies. That isn't obvious for
the two of the three that sit somewhere other than on their owner: the Mage's lingering
field sits on the battlefield rather than on the Mage, and Shields Up's defence sits on
the allies behind the Tank rather than on the Tank. The duration is a count of the
owner's own cooldown cycles, and a member who is dead completes no more of them, so
there's no clock left for the effect to run on.

The cycle an effect is cast in doesn't count: it lasts three of the owner's cycles after
that. For now a Shields Up or a field cast while the owner's last one is still running
stacks with it: both run, each to its own end, so the two lots of defence add up and both
fields do their damage.
```

**Why:** The combat engine is built this way. "Three of the owner's own cooldown cycles"
doesn't say whether the cycle it's cast in counts. Nothing says what happens when one is
cast again while the last is still running; the six combat types are built to stack them,
and that's proposed as a question below.

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

## Change: Questions on specials, taunts and the dive

> Proposed 2026-11-12 · for review

**Where:** `## Open Questions`, at the end of the list

**Now says:**

```
- At F rank a member's Luck is single-digit, which puts the reset chance near one attack
  in forty — a member might see one reset in a whole dive. Is the reset meant to be that
  close to absent early on, or should the curve start higher?
```

**Proposed:**

```
- At F rank a member's Luck is single-digit, which puts the reset chance near one attack
  in forty — a member might see one reset in a whole dive. Is the reset meant to be that
  close to absent early on, or should the curve start higher?
- Should help to a Rogue's or an Archer's Dexterity shorten its cooldown?
- When a taunted member or enemy uses a special that hits its own choice of targets
  rather than one it aims at, is the taunt spent?
- When a Rogue casts Vanish, a Tank uses Shields Up or a Mage casts its field, does that
  cost it an ordinary attack, or does its cooldown run on untouched?
- If a Tank uses Shields Up, or a Mage casts its field, while its last one is still
  running, do the two stack, or does the new one replace the old?
- Can a dive leave a member injured?
- Does the formation carry from one battle to the next?
```

**Why:** None of the docs answers these. The third comes from how a taunt is spent once
the six types' specials are built, and the next two from the specials that strike no one.
The last two come from the dive as it's built: each has a default for now in "Health is
full at the guild hall, and where everyone stands carries over".
