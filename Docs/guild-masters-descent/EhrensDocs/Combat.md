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

## Change: Status line on formation cost, speed and pausing

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
> reset's chance, what formation costs and the fight's speed are settled, and for now the
> fight can be paused; how multi-strike cases resolve, how the bars read at a glance, and
> whether the enemy grid keeps filling are not.
```

**Why:** What formation costs and the fight's speed are now settled, and the fight can be paused for now (see the changes on Formation and Player Input).

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

Nothing waits for the player. The fight runs from start to finish, and the player acts
while it's running — using a member's special once that bar is full, changing formation,
and marking the focus target. For now there's a pause button: it stops the fight and
opens a pop-up to resume it or, on a dive or a played mission, quit. While it's paused
the player can't use a special, mark the focus target or retreat. For now, though, a
member's special can't be used from the battle screen: the bar fills and sits full.

A battle ends when one side has no one left standing. For now a battle also ends after a
set length of time, a placeholder, as a stand-off — 6,000 ticks, five minutes of fight —
and a stand-off kills no one further.
```

**Why:** The combat engine is built this way. No doc says what a member does with no
target selected, or whether a battle can run forever. Using members' specials waits on
the battle screen being able to; the engine already lets them. The original sentences are
unchanged, apart from the pause proposed in "The fight can be paused, for now"; the new
ones sit after them.

## Change: A special puts nothing in its owner's bar, for now

> Proposed 2026-11-13 · for review

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
Using the special empties the bar, and it charges again from there. For now a special
puts nothing into its owner's bar: its own hits charge nothing, the Mage's field's damage
included, and it earns no bonus either — a Brute's special landing on two or more
enemies pays nothing. The one exception is the Fighter's flurry, whose kill refills the
bar to 90%, as the Individual Types doc says. For now, too, a special is used when the
member's cooldown comes up, in place of the ordinary attack that cooldown brings round.
```

**Why:** The combat engine is built this way. This doc says what wears a weapon down is
what fills the bar, and the Equipment doc says a special wears the weapon not at all, so
nothing a special does charges it; nothing says whether a special can earn its type's
bonus. Both are proposed as questions in "Questions on the special bar". Whether using a
special also costs the member an ordinary attack is proposed as a question below; for now
it takes the place of the attack its cooldown brings round.

## Change: Every bar empties on a new floor and starts each dive empty, for now

> Proposed 2026-11-13 · for review

**Where:** `## The Special Bar`, fourth paragraph

**Now says:**

```
A part-filled bar carries from one battle to the next within a floor, and moving to the
next floor resets it to empty.
```

**Proposed:**

```
A part-filled bar carries from one battle to the next within a floor, and moving to the
next floor resets it to empty. For now a full bar empties too: every bar starts a new
floor empty, and a rest area is a floor, so arriving at one empties them. For now, too,
every dive starts with every bar empty, a dive that re-enters at a rest area included —
the bar belongs to the dive, not to the member.
```

**Why:** The dive is built this way. "The special is never lost" and "a part-filled bar
… resets it" leave open whether moving to the next floor empties a full bar, and nothing
says whether a bar outlives the dive. Both are proposed as questions in "Questions on the
special bar".

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
that. For now it ends once the third of those has played out, so the owner's next three
attacks all happen under it — a vanished Rogue makes three that can't miss. For now, too,
a free attack from the Luck reset isn't one of the three: only a cooldown that comes up
after a wait counts. For now a Shields Up or a field cast while the owner's last one is
still running stacks with it: both run, each to its own end, so the two lots of defence
add up and both fields do their damage.
```

**Why:** The combat engine is built this way. "Three of the owner's own cooldown cycles"
doesn't say whether the cycle it's cast in counts, whether the effect ends once the third
has played out or as the fourth begins, or whether a free attack from the Luck reset is a
cycle. Nothing says what happens when one is cast again while the last is still running;
the six combat types are built to stack them. Each is proposed as a question below.

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
- An enemy uses its special when its bar is full, but nothing says what decides the moment
  or the target. Does it fire as soon as it can, or hold while a better target is in
  reach?
```

**Proposed:**

```
- An enemy uses its special when its bar is full, but nothing says what decides the moment
  or the target. Does it fire as soon as it can, or hold while a better target is in
  reach?
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

## Change: How a cooldown rounds, and whose Dexterity counts

> Proposed 2026-11-13 · for review

**Where:** `## Cooldowns`, the paragraph beginning "A cooldown is a number of ticks"

**Now says:**

```
A cooldown is a number of ticks, and each combat type has its own base wait: the Brute
and the Tank wait 180 ticks, the Fighter and the Mage 140, and the Rogue and the Archer
100. The wait is that base divided by (1 + Dexterity ÷ 20), rounded to whole ticks — the
simulation counts in whole ticks, as this section already says. It never goes below a
floor of a tenth of the type's own base, however high Dexterity climbs: 18 ticks for a
Brute or Tank, 14 for a Fighter or Mage, 10 for a Rogue or Archer. That floor is reached
at Dexterity 180 whatever the type.
```

**Proposed:**

```
A cooldown is a number of ticks, and each combat type has its own base wait: the Brute
and the Tank wait 180 ticks, the Fighter and the Mage 140, and the Rogue and the Archer
100. The wait is that base divided by (1 + Dexterity ÷ 20), rounded to whole ticks — the
simulation counts in whole ticks, as this section already says. It never goes below a
floor of a tenth of the type's own base, however high Dexterity climbs: 18 ticks for a
Brute or Tank, 14 for a Fighter or Mage, 10 for a Rogue or Archer. That floor is reached
at Dexterity 180 whatever the type. The rounding is to the nearest whole tick, and an
exact half rounds up: a Rogue at Dexterity 12 waits 63 ticks, not 62. For now the
Dexterity is the combatant's own; help from the support ring doesn't shorten a cooldown.
```

**Why:** The combat engine is built this way. "Rounded to whole ticks" didn't say which
way, and rounding a half to the even tick, the way C# rounds by default, gives 62.
Whether help should shorten a cooldown is already proposed as a question in "Questions on
specials, taunts and the dive", and it stays open.

## Change: The clock, and a multi-strike attack landing in one tick

> Proposed 2026-11-13 · for review

**Where:** `## Cooldowns`, last paragraph (new paragraphs after it)

**Now says:**

```
That's what stops the rate being changed casually: at F rank it makes a slow type's wait
deliberate without being tedious, and at the floor every type is acting about once a
second, which is the pacing this doc already asks for — a low-level fight feeling a little
slow and a higher-level one having more going on.
```

**Proposed:**

```
That's what stops the rate being changed casually: at F rank it makes a slow type's wait
deliberate without being tedious, and at the floor every type is acting about once a
second, which is the pacing this doc already asks for — a low-level fight feeling a little
slow and a higher-level one having more going on.

The fight moves on only as time is handed to it. It never reads the frame rate or the
clock itself, so the same fight with the same rolls plays out the same however that time
is split up — which is what lets a saved battle carry on exactly.

All the strikes of a multi-strike attack land in the tick the attack is made, each still
rolled on its own.
```

**Why:** The combat engine is built this way. Nothing said whether a multi-strike
attack's strikes all land in the tick the attack is made; `Combat.md` has them resolve
one after another within the attack, and this keeps them in the one tick.

## Change: The free attack comes first, and a special gets no check, for now

> Proposed 2026-11-13 · for review

**Where:** `## Luck Checks`, first paragraph

**Now says:**

```
When a member finishes an attack, there's a Luck check for whether the cooldown resets
instantly. On success, the member attacks again immediately, with no cooldown wait at all.
That free attack gets no Luck check of its own — that's what "only once" means, so the
effect can't chain into a second free attack. On failure, the cooldown charges normally.
Apart from costing no wait, the free attack is an ordinary attack in every way: all its
strikes land, it spends durability per hit the same as any other attack, and it charges
the special bar the same as any other attack. The member is eligible for a check again on
its very next attack, the one that charges its cooldown normally — the lockout runs no
further than the one free attack itself. Enemies get the Luck reset too, on the same terms
as guild members.
```

**Proposed:**

```
When a member finishes an attack, there's a Luck check for whether the cooldown resets
instantly. On success, the member attacks again immediately, with no cooldown wait at all.
That free attack gets no Luck check of its own — that's what "only once" means, so the
effect can't chain into a second free attack. On failure, the cooldown charges normally.
Apart from costing no wait, the free attack is an ordinary attack in every way: all its
strikes land, it spends durability per hit the same as any other attack, and it charges
the special bar the same as any other attack. The member is eligible for a check again on
its very next attack, the one that charges its cooldown normally — the lockout runs no
further than the one free attack itself. Enemies get the Luck reset too, on the same terms
as guild members. The free attack comes in the same tick, straight after the attack that
earned it, and it's always the type's ordinary attack, never its special. For now a
close-range fighter's free attack waits for its target like any other attack does. For
now a special gets no Luck check.
```

**Why:** The combat engine is built this way. "Immediately" didn't say whether anyone else
could act first, and nothing said whether a special counts as an attack for the reset.
That's proposed as a question below, and so is whether a free attack waits.

## Change: A specialist's cooldown, for now

> Proposed 2026-11-13 · for review

**Where:** `## Specialists in Combat`, the paragraph

**Now says:**

```
A specialist attacks on its own cooldown like anyone else. The specialist makes a basic
attack against a single target — a close-range attack, so its reach is the first available
row like any close attacker, the enemy front line. The attack is weak — the intent is that
specialists help a little rather than being a full detriment to the battle. A specialist
has no special bar at all, and their attack damage works the way it does for anyone else.
```

**Proposed:**

```
A specialist attacks on its own cooldown like anyone else. The specialist makes a basic
attack against a single target — a close-range attack, so its reach is the first available
row like any close attacker, the enemy front line. The attack is weak — the intent is that
specialists help a little rather than being a full detriment to the battle. A specialist
has no special bar at all, and their attack damage works the way it does for anyone else.
For now a specialist's cooldown starts from the slowest base, 180 ticks, a placeholder;
Dexterity shortens it, and the floor of a tenth applies, as for any type.
```

**Why:** The combat engine is built this way. The combat types each have a base wait, and
nothing gives a specialist one. That's proposed as a question below.

## Change: Questions on cooldown combat's defaults

> Proposed 2026-11-13 · for review

**Where:** `## Open Questions`, at the end of the list

**Now says:**

```
- An enemy uses its special when its bar is full, but nothing says what decides the moment
  or the target. Does it fire as soon as it can, or hold while a better target is in
  reach?
```

**Proposed:**

```
- An enemy uses its special when its bar is full, but nothing says what decides the moment
  or the target. Does it fire as soon as it can, or hold while a better target is in
  reach?
- Is a special an attack for the Luck reset — does it get a check?
- Does a free attack from the Luck reset count as one of the owner's three cycles for a
  lasting effect?
- Does a lasting effect end once the owner's third cycle after the cast has played out,
  or as its fourth begins? The second keeps Shields Up on the allies for one more of the
  Tank's waits.
- What base wait does a specialist's cooldown have?
```

**Why:** The combat engine is built with a default for now on each of these, in the
changes above, and none of the docs settles them. The pending "Questions on specials,
taunts and the dive" change to this list is unchanged; these go after the entries it adds.

## Change: Questions on the special bar

> Proposed 2026-11-13 · for review

**Where:** `## Open Questions`, at the end of the list

**Now says:**

```
- An enemy uses its special when its bar is full, but nothing says what decides the moment
  or the target. Does it fire as soon as it can, or hold while a better target is in
  reach?
```

**Proposed:**

```
- An enemy uses its special when its bar is full, but nothing says what decides the moment
  or the target. Does it fire as soon as it can, or hold while a better target is in
  reach?
- Do a special's own hits — the Mage's field's damage among them — charge the bar it has
  just emptied?
- Can a special earn its owner's bonus condition — a Brute's special landing on two or
  more enemies, say?
- Does moving to the next floor empty a full bar too, or only a part-filled one?
- Does a member's special bar carry from one dive to the next, or does every dive start
  with it empty?
```

**Why:** The combat engine and the dive are built with a default for now on each of
these, in "A special puts nothing in its owner's bar, for now" and "Every bar empties on a
new floor and starts each dive empty, for now", and none of the docs settles them. The
pending "Questions on specials, taunts and the dive" and "Questions on cooldown combat's
defaults" changes to this list are unchanged; these go after the entries they add.

## Change: Every character's own Luck bag, and when no token is pulled, for now

> Proposed 2026-11-18 · for review

**Where:** `## Luck Checks`, second paragraph (a new paragraph after it)

**Now says:**

```
A Luck check pulls one token out of a bag of 50, each token either True or False. A False
does nothing; a True means the character is lucky. Once every token has been pulled, the
bag fills back up — and that's the only thing that refills it. A part-used bag carries
over rather than resetting, from one battle to the next and from one floor to the next.
The bag exists because drawing without replacement guarantees the lucky event arrives — at
the floor of one token in fifty it cannot be missed for long — where a roll against a
small percentage can go cold for a very long time.
```

**Proposed:**

```
A Luck check pulls one token out of a bag of 50, each token either True or False. A False
does nothing; a True means the character is lucky. Once every token has been pulled, the
bag fills back up — and that's the only thing that refills it. A part-used bag carries
over rather than resetting, from one battle to the next and from one floor to the next.
The bag exists because drawing without replacement guarantees the lucky event arrives — at
the floor of one token in fifty it cannot be missed for long — where a roll against a
small percentage can go cold for a very long time.

Every character that fights has a bag of its own — every guild member, specialists too,
and every enemy — and no bag is shared; an enemy that's attacked evades from its own bag
the same way a member does. A member's first bag is filled when they join the guild, and
from then on it's theirs, carried part-used from one dive to the next as well, and into a
mission played as a battle. The Luck a bag fills from is the character's own: help from
the support ring doesn't add to it. For now:

- An enemy's bag is new and full when it joins a battle, and lasts only for that battle.
- No token is pulled for the Luck reset after an attack that ends the battle, or one its
  attacker doesn't live through. No free attack can follow, and a True pulled then would
  be thrown away.
```

**Why:** The combat engine is built this way. Nothing said whether an enemy's bag works
like a member's — "Enemies get the Luck reset too, on the same terms as guild members" can
be read either way — or whether a token is pulled when no free attack can follow. Both are
proposed as questions in "Questions on the Luck bag's defaults". Help from the support ring
stays off Luck the way "How a cooldown rounds, and whose Dexterity counts" keeps it off
Dexterity.

## Change: Questions on the Luck bag's defaults

> Proposed 2026-11-18 · for review

**Where:** `## Open Questions`, at the end of the list

**Now says:**

```
- An enemy uses its special when its bar is full, but nothing says what decides the moment
  or the target. Does it fire as soon as it can, or hold while a better target is in
  reach?
```

**Proposed:**

```
- An enemy uses its special when its bar is full, but nothing says what decides the moment
  or the target. Does it fire as soon as it can, or hold while a better target is in
  reach?
- Does an enemy's Luck bag last only for its own battle, new and full each time, or carry
  on from battle to battle the way a member's does?
- When an attack ends the battle, or its attacker doesn't live through it, is a token
  still pulled for the Luck reset?
- The Luck check each combatant makes as a fight begins is called "a separate roll", using
  "the same chance" as the reset. Now that every Luck check a character makes draws from
  its own bag, is the opening check a pull from that bag too, or a roll of its own?
```

**Why:** The combat engine is built with a default for now on the first two, in "Every
character's own Luck bag, and when no token is pulled, for now". The third is the
original's own: Cooldowns calls the opening check a separate roll at the reset's chance,
and Luck Checks has every Luck check a character makes draw from the same bag. The combat
engine doesn't make the opening check yet. The pending changes to this list above are
unchanged; these go after the entries they add.

## Change: The fight can be paused, for now

> Proposed 2026-11-16 · for review

**Where:** `## Player Input`, second paragraph

**Now says:**

```
The fight never pauses, and nothing waits for the player. It runs from start to finish,
and the player acts while it's running — using a member's special once that bar is full,
changing formation, and marking the focus target.
```

**Proposed:**

```
Nothing waits for the player. The fight runs from start to finish, and the player acts
while it's running — using a member's special once that bar is full, changing formation,
and marking the focus target. For now there's a pause button: it stops the fight and
opens a pop-up to resume it or, on a dive or a played mission, quit. While it's paused
the player can't use a special, mark the focus target or retreat.
```

**Why:** The user, 2026-11-16: "Leave the pause button for now we can take it out later."
The battle screen is built with it. This departs from the original's "The fight never
pauses", so it stands for now. The pending "How a member with no target picks one, and how
a battle ends" change to this paragraph carries this wording too; its sentence on specials
goes after these.

## Change: The fight can be sped up, and only shows sooner

> Proposed 2026-11-16 · for review

**Where:** `## Player Input`, last paragraph (a new paragraph after it)

**Now says:**

```
The fight doesn't wait for the player, so the moment to use a special goes by while the
fight carries on around it.
```

**Proposed:**

```
The fight doesn't wait for the player, so the moment to use a special goes by while the
fight carries on around it.

The player can speed the fight up — x1, x2 or x3 — but can't slow it below x1. Faster
only shows the same fight sooner: the same ticks and the same rolls, so the same taps at
the same moments of the fight give the same result. What it changes is the player's real
time to react: at x3 a special's window is a third as long.
```

**Why:** The user, 2026-11-16: "yes its fine." — to keeping the x1/x2/x3 speed button the
battle screen is built with. This answers the original's open question "Can the player
speed a fight up or slow it down, and does that change anything in the simulation or only
how fast it's drawn?": only how fast it's drawn. The fight moves on only as time is handed
to it, as the pending "The clock, and a multi-strike attack landing in one tick" change
says, so speed can't change what happens in it.

## Change: Speed question answered

> Proposed 2026-11-16 · for review

**Where:** `## Open Questions`

**Now says:**

```
- Can the player speed a fight up or slow it down, and does that change anything in the
  simulation or only how fast it's drawn?
```

**Proposed:** delete. The other entries in `## Open Questions`, and the pending changes to
this list above, stay as they are.

**Why:** Answered: x1, x2 or x3, and it changes only how soon the fight is shown, written
into Player Input.

## Change: A close-range attack waits for its target to be home

> Proposed 2026-11-17 · for review

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

A close-range fighter walks out to its target, strikes, and walks back to its own spot,
and it never walks to a spot its target has left. When its attack comes up and the target
it picks is out on an attack of its own, it waits until that target is back in its spot,
then attacks. For now that holds on the same tick too: when a fighter's attack comes up
on the tick its target heads off to hit someone else, it waits until the target is back
in its own spot and then hits it, so its attack lands after the target's. It also waits
while its target is waiting to attack ahead of it, and goes after it. A waiting fighter
keeps the target it picked, and picks again only if that target dies, goes out of its
reach, or vanishes.

For now, two close-range fighters who pick each other on the same tick take turns rather
than attacking at the same time. The attack that became ready first goes first; between
two that became ready on the same tick, the one with the higher Dexterity goes first, and
between equal Dexterity it's a random draw. The first walks out, hits and walks home, and
only then does the other go. If the first hit kills the other fighter, it never swings.

Nothing of a waiting attack happens until the wait ends. Then it's made whole, as any
attack is: a field it stands in hurts it first, whether it uses its special is decided
then, and its strikes roll then. That's also when its next cooldown starts, when its Luck
check is made, and when it counts as one of its attacks for a lasting effect.

How long a fighter is out is worked out by the fight itself, from the same walk the battle
screen draws, so the fight holds the same waits at any speed and when nothing is drawn at
all. Retiming an attack's animation changes how long a fighter is out, and so how a fight
with the same rolls plays out.

For now:

- A fighter someone is on the way to hit stays put until that attacker is home, whoever it
  was going to attack.
- Only close-range fighters wait. An Archer or a Mage shoots its target where it is, out
  on an attack or not, and the shot follows it.
- A fighter whose cooldown comes up, or who earns a free attack, before it's home walks
  home first and then goes out again.
- A waiting fighter's next cooldown starts when it finally attacks, not from when it
  became ready.
- Marking a new focus target doesn't change the target a waiting member has already
  picked.
```

**Why:** The user, 2026-11-17: "the attacker needs to wait for the attacked to be in the
spot and not on the attack" — two fighters going for each other at once each jumped to
the other's empty spot and swung at thin air. Asked then whether two close-range fighters
who pick each other on the same tick should hit at once or take turns, and whether a
fighter whose target heads off on that tick should wait for it to come home, the user
said: "B my rules for now. as it looks bad otherwise." That departs from the original's
same-tick attacks all happening at the same time, so it stands for now; see "Close-range
fighters take turns on the same tick, for now". The combat engine and the battle screen
are built this way. Each "for now" in the list is proposed as a question below.

## Change: Close-range fighters take turns on the same tick, for now

> Proposed 2026-11-18 · for review

**Where:** `## Cooldowns`, the paragraph beginning "When more than one combatant's cooldown
comes up on the same tick"

**Now says:**

```
When more than one combatant's cooldown comes up on the same tick, their attacks all
happen at the same time — there's no order between them, and nothing resolves first.
Damage is worked out against where things stood at the start of that tick, so a combatant
that dies on that tick still lands the attack it made on it, and two combatants can kill
each other on the same tick.
```

**Proposed:**

```
When more than one combatant's cooldown comes up on the same tick, their attacks all
happen at the same time — there's no order between them, and nothing resolves first.
Damage is worked out against where things stood at the start of that tick, so a combatant
that dies on that tick still lands the attack it made on it, and two combatants can kill
each other on the same tick. For now two close-range fighters are the exception, as
Attacks and Reach says: when they pick each other on the same tick they take turns, and
the first hit can kill the other before it swings; and when a fighter's target heads off
on that tick to hit someone else, the fighter waits until it's home, so its attack lands
after its target's.
```

**Why:** The user, 2026-11-17: "B my rules for now. as it looks bad otherwise." — on
whether two close-range fighters who pick each other on the same tick should hit at once
or take turns, and whether a fighter whose target heads off on that tick should wait for
it to come home. Hitting at once would show each fighter walking to the other's empty
spot, which "A close-range attack waits for its target to be home" rules out, so for now
that rule wins over same-tick attacks happening together. The combat engine is built
this way.

## Change: Questions on a close-range attack waiting

> Proposed 2026-11-17 · for review

**Where:** `## Open Questions`, at the end of the list

**Now says:**

```
- An enemy uses its special when its bar is full, but nothing says what decides the moment
  or the target. Does it fire as soon as it can, or hold while a better target is in
  reach?
```

**Proposed:**

```
- An enemy uses its special when its bar is full, but nothing says what decides the moment
  or the target. Does it fire as soon as it can, or hold while a better target is in
  reach?
- When a fighter is already on its way to hit someone, and that someone's own turn comes
  up to attack a third character, should it stay put until the hit lands and the attacker
  is back?
- Should an Archer or a Mage also wait to shoot someone who is out on an attack, or shoot
  them where they are, the shot following them?
- A waiting fighter's next cooldown: does it start when it finally attacks, so waiting
  costs it time, or from when it became ready, so it catches up?
- If the player marks a new focus target while a member is waiting to attack, does it
  switch to the new target?
- When a free attack from the Luck reset has a target that's out on an attack, does it
  wait like any other attack?
- A fast fighter can be ready to attack again before it has walked home from its last
  attack, and a lucky one gets a free attack straight away. Should it walk home first and
  then go out again, or attack again from where it stands?
```

**Why:** The combat engine is built with a default for now on each of these, in "A
close-range attack waits for its target to be home" and "The free attack comes first, and
a special gets no check, for now". The pending changes to this list above are unchanged;
these go after the entries they add.
