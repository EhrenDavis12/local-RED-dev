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

## Change: Status line on formation cost and speed

> Proposed 2026-11-11 · for review

**Where:** the `> **Status:**` line at the top

**Now says:**

```
> **Status:** Early design. Nothing is built yet — the grid, the cooldown pacing, the Luck
> reset's chance, how a special fires, and the never-pausing simulation are settled;
> whether a fight can be sped up, what formation costs, whether the enemies keep coming
> once the grid is full, and whether the Mage's field bites a member that drinks are not.
```

**Proposed:**

```
> **Status:** Early design. Nothing is built yet — the grid, the cooldown pacing, the Luck
> reset's chance, how a special fires, the never-pausing simulation, what formation costs
> and the fight's speed are settled; whether the enemies keep coming once the grid is
> full, and whether the Mage's field bites a member that drinks are not.
```

**Why:** What formation costs and the fight's speed are now settled (see the changes on
Formation and Player Input). The never-pausing simulation stays as the original has it:
the pause button is only in a development build, in "The fight pauses only in a
development build".

## Change: Formation-cost question answered

> Proposed 2026-11-11 · for review

**Where:** `## Open Questions`

**Now says:**

```
- What does changing formation mid-battle cost the player, if anything?
```

**Proposed:** delete. The other entries in `## Open Questions` stay as they are.

**Why:** Answered: free for now, written into Formation.

## Change: A dive never injures, and where everyone stands carries over, for now

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

For now a dive never leaves a member injured: a member comes home, hurt or not, or
doesn't come home. Where everyone stands at the end of a battle is where they start the next one, and
the dead leave their places empty.
```

**Why:** The dive is built this way. No doc says whether a dive can leave a member injured,
or whether the formation carries from one battle to the next. Not settled by this: what
reaching 0 health does on a training run, which "can injure a member, but can never kill
one". Each is proposed as a question for `## Open Questions`. Coming home hurt is lost health
that heals at home, as `Core Concept.md` `## The Mead Hall` says, not the injured status.

## Change: A battle ends in a stand-off after a set time, for now

> Proposed 2026-11-12 · for review

**Where:** `## Player Input`, the paragraph beginning "The fight never pauses" (a new
paragraph after it)

**Now says:**

```
The fight never pauses, and nothing waits for the player. It runs from start to finish,
and the player acts while it's running — changing formation, marking the focus target and
using a buff potion.
```

**Proposed:**

```
The fight never pauses, and nothing waits for the player. It runs from start to finish,
and the player acts while it's running — changing formation, marking the focus target and
using a buff potion.

A battle ends when one side has no one left standing. For now a battle also ends after a
set length of time, a placeholder, as a stand-off — 6,000 ticks, five minutes of fight —
and a stand-off kills no one further.
```

**Why:** The combat engine is built this way. No doc says whether a battle can run forever.
The original paragraph is unchanged; the new one sits after it.

## Change: A special puts nothing in its owner's bar, for now

> Proposed 2026-11-13 · for review

**Where:** `## The Special Bar`, the line "Firing the special empties the bar, and it
charges again from there."

**Now says:**

```
Firing the special empties the bar, and it charges again from there.
```

**Proposed:**

```
Firing the special empties the bar, and it charges again from there. For now a special
puts nothing into its owner's bar: its own hits charge nothing, the Mage's field's damage
included, and it earns no bonus either — a Brute's special landing on two or more
enemies pays nothing. The one exception is the Fighter's flurry, whose kill refills the
bar to 90%, as the Individual Types doc says.
```

**Why:** The combat engine is built this way. This doc says what wears a weapon down is
what fills the bar, and the Equipment doc says a special wears the weapon not at all, so
nothing a special does charges it; nothing says whether a special can earn its type's
bonus. Both are proposed as questions in "Questions on the special bar".

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
next floor resets it to empty. For now every dive starts with every bar empty, a dive that
re-enters at a rest area included — the bar belongs to the dive, not to the member.
```

**Why:** The dive is built this way. Nothing says whether a bar outlives the dive. That's
proposed as a question in "Questions on the special bar".

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

A special going off isn't one of its owner's cycles, since it takes no action: the
effect it casts lasts three of the owner's cycles after that. For now it ends once the
third of those has played out, so the owner's next three cooldowns all happen under
it — a vanished Rogue makes three attacks that can't miss, or one fewer for each it
spends drinking a potion instead. For now, too, a free attack from the Luck reset isn't
one of the three: only a cooldown that comes up after a wait counts. For now a field
cast while the Mage's last one is still running stacks with it: both run, each to its
own end, and both fields do their damage.
```

**Why:** The combat engine is built this way. "Three of the owner's own cooldown cycles"
doesn't say whether the cycle it's cast in counts, whether the effect ends once the third
has played out or as the fourth begins, or whether a free attack from the Luck reset is a
cycle. Nothing says what happens when a Mage's field is cast again while the last is still
running; the Mage is built to stack them. Each is proposed as a question below.
A drink ordered in place of an attack uses up one of the three too, as "Drinking a potion
is an order used at the next cooldown, for now" says, so the three are cooldowns, not
attacks.

## Change: How a taunt is spent

> Proposed 2026-11-12 · for review

**Where:** `## Targeting`, last paragraph (a new paragraph after it)

**Now says:**

```
A close attacker facing five in a front line gives the weakest of them 36% and each
of the others 16%.
```

**Proposed:**

```
A close attacker facing five in a front line gives the weakest of them 36% and each
of the others 16%.

The taunt is spent by that attack whether it hits or misses. While the taunter is out of
reach, the taunted one picks as normal, and the taunt keeps for its next attack that can
reach the taunter. A newer taunt replaces an older one, and a taunt ends if the taunter
dies. A taunt overrides the party's selected enemy too: a member taunted by an enemy Tank
goes for the Tank.
```

**Why:** The combat engine is built this way. "Until the taunted enemy's next hit, one
attack and then it's spent" reads two ways; this takes it as one attack, hit or miss.
Nothing says what a taunt does while the taunter is out of reach, when two taunts
overlap, when the taunter dies, or when a taunt and the focus target the player marks
both make one target the only pick — and with monsters having the six types, a monster
Tank taunts members.

## Change: Questions on specials, taunts and the dive

> Proposed 2026-11-12 · for review

**Where:** `## Open Questions`, after the entry beginning "The enemy grid holds fifteen"

**Now says:**

```
- The enemy grid holds fifteen. When a floor is deep enough to fill it, do the enemies
  stop there, or do they keep coming?
```

**Proposed:**

```
- The enemy grid holds fifteen. When a floor is deep enough to fill it, do the enemies
  stop there, or do they keep coming?
- When a taunted member or enemy uses a special that hits its own choice of targets
  rather than one it aims at, is the taunt spent?
- If a Mage casts its field while its last one is still running, do the two stack, or
  does the new one replace the old?
- Can a dive leave a member injured?
- Does the formation carry from one battle to the next?
```

**Why:** None of the docs answers these. The second comes from how a taunt is spent once
the six types' specials are built, and the third from the Mage's field. The last two come
from the dive as it's built: each has a default for now in "A dive never injures, and
where everyone stands carries over, for now".

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
exact half rounds up: a Rogue at Dexterity 12 waits 63 ticks, not 62. The Dexterity is
the helped one where help reaches it: a Rogue's or an Archer's primary stat is Dexterity,
so help from the support ring shortens its cooldown, on either side, and a Rogue at
Dexterity 8 with one help waits 69 ticks, not 71. Every other type waits on its own
Dexterity. The rounding and the floor both apply to the helped Dexterity, and a fight's
first wait counts help too, from the formation the fight starts with. For now a wait is
worked out as it begins, and help that comes or goes partway through doesn't change a
wait already running; it shows from the next one.
```

**Why:** The combat engine is built this way. "Rounded to whole ticks" didn't say which
way, and rounding a half to the even tick, the way C# rounds by default, gives 62. Help
counting is what the originals say between them: Cooldowns has Dexterity set the wait,
Guild Members has help raise the primary stat, and Battle Test's tables, which already
include the help, give its Rogue and Archer a wait of 69 on both teams. The first wait
is worked out once everyone stands in place, so the order members were put on the field
can't change it. Nothing said whether a running wait changes with the help; that's
proposed as a question in "Questions on cooldown combat's defaults".

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
earned it — or after the special, when that attack filled its own bar — and it's always
the type's ordinary attack, never its special. For now a close-range fighter's free
attack waits for its target like any other attack does. For now a special gets no Luck
check.
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

**Where:** `## Open Questions`, after the entry beginning "The enemy grid holds fifteen"

**Now says:**

```
- The enemy grid holds fifteen. When a floor is deep enough to fill it, do the enemies
  stop there, or do they keep coming?
```

**Proposed:**

```
- The enemy grid holds fifteen. When a floor is deep enough to fill it, do the enemies
  stop there, or do they keep coming?
- Is a special an attack for the Luck reset — does it get a check?
- Does a free attack from the Luck reset count as one of the owner's three cycles for a
  lasting effect?
- Does a lasting effect end once the owner's third cycle after the cast has played out,
  or as its fourth begins? The second keeps Shields Up on the allies for one more of the
  Tank's waits.
- What base wait does a specialist's cooldown have?
- When a helper moves away, dies or arrives while a Rogue's or an Archer's wait is already
  running, does that running wait change, or does the change only show from its next wait?
```

**Why:** The combat engine is built with a default for now on each of these, in the
changes above, and none of the docs settles them. The pending "Questions on specials,
taunts and the dive" change to this list is unchanged; these go after the entries it adds.

## Change: Questions on the special bar

> Proposed 2026-11-13 · for review

**Where:** `## Open Questions`, after the entry beginning "The enemy grid holds fifteen"

**Now says:**

```
- The enemy grid holds fifteen. When a floor is deep enough to fill it, do the enemies
  stop there, or do they keep coming?
```

**Proposed:**

```
- The enemy grid holds fifteen. When a floor is deep enough to fill it, do the enemies
  stop there, or do they keep coming?
- Do a special's own hits — the Mage's field's damage among them — charge the bar it has
  just emptied?
- Can a special earn its owner's bonus condition — a Brute's special landing on two or
  more enemies, say?
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
stays off Luck because help reaches only a type's primary stat, and none of the six combat
types leads on Luck.

## Change: The opening check is a pull from the combatant's own bag, for now

> Proposed 2026-11-18 · for review

**Where:** `## Cooldowns`, the paragraph beginning "Cooldowns start empty at the beginning
of a fight"

**Now says:**

```
Cooldowns start empty at the beginning of a fight. But every combatant — guild member and
enemy alike — makes one Luck check of its own as the fight begins, using the same chance
as the mid-fight reset below in Luck Checks. It's a separate roll, not tied to that
one. On success, the combatant starts the fight ready instead of empty, attacking on the
first tick rather than waiting out its first cooldown. On failure, it waits out that first
cooldown like normal. A success is a full jumpstart, not a partial charge — the combatant
is either ready or it isn't.
```

**Proposed:**

```
Cooldowns start empty at the beginning of a fight. But every combatant — guild member and
enemy alike — makes one Luck check of its own as the fight begins, using the same chance
as the mid-fight reset below in Luck Checks. For now that check is one pull from the
combatant's own bag, the way every Luck check it makes is, so a member's opening pull uses
up a token from the bag they carry between battles. On success, the combatant starts the
fight ready instead of empty, attacking on the first tick — the tick the fight starts on,
before any wait has passed — rather than waiting out its first cooldown. On failure, it
waits out that first cooldown like normal. A success is a full jumpstart, not a partial
charge — the combatant is either ready or it isn't. For now that first attack is an
ordinary attack, not a free one: it gets the Luck reset check after it, and counts as one of
its owner's cycles for a lasting effect. The
check is made only when a fight really begins, never when a battle is set up just to show
who's in it, the way party planning does.
```

**Why:** The combat engine is built this way. The original calls the opening check a
separate roll at the reset's chance, and Luck Checks has every Luck check a character
makes draw from the same bag; the engine pulls from the bag for now. Nothing said whether
an attack on the first tick is an ordinary attack or a free one. Both are proposed as
questions in "Questions on the Luck bag's defaults". A battle set up only to show its
fighters pulls nothing because a pull from a member's bag can't be handed back.

## Change: Questions on the Luck bag's defaults

> Proposed 2026-11-18 · for review

**Where:** `## Open Questions`, after the entry beginning "The enemy grid holds fifteen"

**Now says:**

```
- The enemy grid holds fifteen. When a floor is deep enough to fill it, do the enemies
  stop there, or do they keep coming?
```

**Proposed:**

```
- The enemy grid holds fifteen. When a floor is deep enough to fill it, do the enemies
  stop there, or do they keep coming?
- Does an enemy's Luck bag last only for its own battle, new and full each time, or carry
  on from battle to battle the way a member's does?
- When an attack ends the battle, or its attacker doesn't live through it, is a token
  still pulled for the Luck reset?
- The Luck check each combatant makes as a fight begins is called "a separate roll", using
  "the same chance" as the reset. Now that every Luck check a character makes draws from
  its own bag, is the opening check a pull from that bag too, or a roll of its own?
- A combatant that starts the fight ready attacks on the first tick. Is that an ordinary
  attack — with the Luck reset check after it, counting as one of its owner's cycles for a
  lasting effect — or a free attack that gets none of that?
```

**Why:** The combat engine is built with a default for now on all four: the first two in
"Every character's own Luck bag, and when no token is pulled, for now", the last two in
"The opening check is a pull from the combatant's own bag, for now". The third is the
original's own: Cooldowns calls the opening check a separate roll at the reset's chance,
and Luck Checks has every Luck check a character makes draw from the same bag. The pending
changes to this list above are unchanged; these go after the entries they add.

## Change: The fight pauses only in a development build

> Proposed 2026-11-16 · for review

**Where:** `## Player Input`, the paragraph beginning "The fight never pauses" (a new
paragraph after it)

**Now says:**

```
The fight never pauses, and nothing waits for the player. It runs from start to finish,
and the player acts while it's running — changing formation, marking the focus target and
using a buff potion.
```

**Proposed:**

```
The fight never pauses, and nothing waits for the player. It runs from start to finish,
and the player acts while it's running — changing formation, marking the focus target and
using a buff potion.

A development build — the Unity editor or a Development Build player — has a pause
button, so the developer can stop the fight to take screenshots. It stops the fight and
opens a pop-up to resume it or, on a dive or a played mission, quit. While it's paused
the player can't mark the focus target or retreat. A release build, TestFlight included,
has no pause: there the player leaves a dive or a played mission with the Retreat button.
```

**Why:** The battle screen is built with a pause button. The user, 2026-11-24: "Pause
make this a dev only feature. So i can pause and take screen shots if needed. but for
released games this is not an option." So the original's "The fight never pauses" holds
for the game as released, and the pause is only a tool for the developer.

## Change: The fight can be sped up, and only shows sooner

> Proposed 2026-11-16 · for review

**Where:** `## Player Input`, the paragraph beginning "The fight never pauses" (a new
paragraph after it)

**Now says:**

```
The fight never pauses, and nothing waits for the player. It runs from start to finish,
and the player acts while it's running — changing formation, marking the focus target and
using a buff potion.
```

**Proposed:**

```
The fight never pauses, and nothing waits for the player. It runs from start to finish,
and the player acts while it's running — changing formation, marking the focus target and
using a buff potion.

The player can speed the fight up — x1, x2 or x3 — but can't slow it below x1. Faster
only shows the same fight sooner: the same ticks and the same rolls, so the same taps at
the same moments of the fight give the same result.
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

Two close-range fighters who pick each other on the same tick take turns, in the order
Cooldowns sets for every attack on the same tick: the first walks out, hits and walks
home, and only then does the other go. If the first hit kills the other fighter, it never
swings.

Nothing of a waiting attack happens until the wait ends. Then it's made whole, as any
attack is: a field it stands in hurts it first, and its strikes roll then. That's also when its next cooldown starts, when its Luck
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
same-tick attacks all happening at the same time, as every attack on the same tick does;
see "Attacks on the same tick go in turn". The combat engine and the battle screen are
built this way. Each "for now" in the list is proposed as a question below.

## Change: Attacks on the same tick go in turn

> Proposed 2026-11-18 · for review

**Where:** `## Cooldowns`, the paragraph beginning "When more than one combatant's cooldown
comes up on the same tick" and the paragraph after it

**Now says:**

```
When more than one combatant's cooldown comes up on the same tick, their attacks all
happen at the same time — there's no order between them, and nothing resolves first.
Damage is worked out against where things stood at the start of that tick, so a combatant
that dies on that tick still lands the attack it made on it, and two combatants can kill
each other on the same tick.

That simultaneity is between combatants, not inside one combatant's own attack: within a
single attack the strikes still resolve one after another, which is what lets the
Fighter's flurry carry its remaining strikes to the nearest enemy still standing when its
target dies partway through.
```

**Proposed:**

```
When more than one combatant's cooldown comes up on the same tick, their attacks don't
happen at the same time: they go in turn, one after another. The attack that became ready
first goes first; between two that became ready on the same tick, the one with the higher
Dexterity of its own goes first, help from the support ring left out, and between equal
Dexterity it's a random draw. Each attack is worked out against the fight as it stands
after the attacks before it, so a combatant killed earlier in the tick never makes its
attack, and an attacker whose target has already died picks a new one still standing.
The battle ends as soon as one side has no one left standing, even partway through a
tick, so the last member and the last enemy never kill each other. A close-range fighter
also waits for its target to be home, as Attacks and Reach says.

Within one combatant's own attack the strikes resolve one after another too, which is
what lets the Fighter's flurry carry its remaining strikes to the nearest enemy still
standing when its target dies partway through.
```

**Why:** The user, 2026-11-18: "The only contradiction I want to win is from our side is
that an enemy must wait on the battle on the attack sequence so that so that their present
when being attacked so two people are attacking at the same time they don't actually attack
at the same time one attack than the other attacks that's the only thing I want winning
over what the new doc Say" — asked whether attacks on the same tick other than between two
close-range fighters (two Archers shooting each other, a Mage and an Archer, two members
hitting one enemy, a fighter walking up to an Archer) should all happen at once, as the
original says, or go one after another. With the user's 2026-11-17 answer on close-range
fighters, "B my rules for now. as it looks bad otherwise.", every attack on the tick goes
in turn and none happen at once, so two combatants can't kill each other on the same tick.
The combat engine is built this way.

## Change: Questions on a close-range attack waiting

> Proposed 2026-11-17 · for review

**Where:** `## Open Questions`, after the entry beginning "The enemy grid holds fifteen"

**Now says:**

```
- The enemy grid holds fifteen. When a floor is deep enough to fill it, do the enemies
  stop there, or do they keep coming?
```

**Proposed:**

```
- The enemy grid holds fifteen. When a floor is deep enough to fill it, do the enemies
  stop there, or do they keep coming?
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
- When two attacks became ready on the same tick, the one with the higher Dexterity goes
  first. Does help from the support ring count in that Dexterity, the way it counts in a
  Rogue's or an Archer's cooldown?
```

**Why:** The combat engine is built with a default for now on each of these, in "A
close-range attack waits for its target to be home", "Attacks on the same tick go in
turn" and "The free attack comes first, and a special gets no check, for now". The pending changes to this list above are unchanged;
these go after the entries they add.

## Change: Drinking a potion is an order used at the next cooldown, for now

> Proposed 2026-11-18 · for review

**Where:** `## Player Input`, the paragraph beginning "When a member's cooldown comes up"
(new paragraphs after it)

**Now says:**

```
When a member's cooldown comes up, the player can have it drink a healing potion
instead of attacking — drinking costs that attack.
```

**Proposed:**

```
When a member's cooldown comes up, the player can have it drink a healing potion
instead of attacking — drinking costs that attack.

The player has a member drink by ordering it while the fight runs: any living party
member holding a potion can be ordered to, a specialist too, and the order can be taken
back until it's used. It's used at the member's next cooldown, in place of the attack
that cooldown brings, and the member drinks one potion from their own slots. An order
ends when it's used or taken back, when the member dies, or when the battle ends.

Drinking costs the attack and nothing else. The member strikes no one and stays on their
own spot, wears no weapon, charges no bar, and pulls no Luck token, so no free attack
follows; their next cooldown then starts as it would after an attack. A drink is one of
the member's own cooldown cycles for any lasting effect they cast. A drink never takes a
member past their maximum health, and a member at full health can still be ordered to
drink: the potion and the attack are used up and nothing is healed.

For now:

- A member standing in a Mage's field takes the field's hit first, as it would before an
  attack, and drinks after it. If the field kills them, they drink nothing and keep the
  potion.
- A close-range member whose attack is already waiting when the drink is ordered drinks
  as soon as they're back on their own spot, in the place the waiting attack had. Only
  their own absence holds a drink, never their target's.
- A free attack from the Luck reset is always an attack. An order placed before one is
  used at the next cooldown that comes after a wait.
- A drink never spends a taunt. A taunt is spent only by an attack that's made, so it
  keeps for the member's next one.
- Nothing is drunk without an order. With Auto on in a dive, any party member below 30%
  of their maximum health who still holds a potion has a drink ordered for them, a Cook
  or a Porter too, and it's used at their next cooldown like any other order. The 30% is
  a placeholder. Auto never takes a drink order back. If the player takes back the drink
  while the member is still below 30% and holds a potion, Auto orders the drink again
  straight away.
- A drink that's ordered but not yet drunk isn't saved, so it's lost if the game closes.
- On the battle screen each fighter's skill button — up to four, the fourth following
  whichever fighter the player last tapped — has a drink button under it for the same
  member, showing how many potions they hold; pressing it orders the drink or takes it
  back. The Cooks and Porters share one drink button, at the end of that row, which
  starts on the first of them in the party and follows whichever one the player last
  taps. An order stands when its member leaves the button. A drink button can't be
  pressed while the fight is paused, for a fallen member, or for one with no potion left.
```

**Why:** The original says the player can have a member drink instead of attacking when
its cooldown comes up, and that drinking costs that attack, but not how the player says
so before the moment goes by, what else a drink costs, or how it sits with a waiting
attack, a free attack or a special. The combat engine is built this way. Ordering ahead,
a waiting member drinking once home, a free attack never replaced
and an unused order not being saved are the user's going-ahead defaults, 2026-11-18. The
field's hit coming first is the default the build goes ahead with on the original's open
question, which stays open. A drink at full health and a drink leaving a taunt standing
are defaults the build chose, not yet the user's word, proposed as questions in
"Questions on drinking a potion". The battle screen's drink buttons and drinking under
Auto are built this way too. Nothing in the docs says Auto drinks at all; drinking below
30%, and Auto ordering the drink again over the player's own tap, are defaults the build
chose, not yet the user's word, proposed as questions there as well. The Cooks' and
Porters' shared button is a default too, and cheap to change.

## Change: Questions on drinking a potion

> Proposed 2026-11-18 · for review

**Where:** `## Open Questions`, at the end of the list, after the entry beginning "The
Mage's field damages a character"

**Now says:**

```
- The Mage's field damages a character as it begins its own attack. A member can drink a
  potion instead of attacking — does a member standing in a field take the field's
  damage when it drinks?
```

**Proposed:**

```
- The Mage's field damages a character as it begins its own attack. A member can drink a
  potion instead of attacking — does a member standing in a field take the field's
  damage when it drinks?
- Can a member at full health be ordered to drink, using up the potion and the attack
  and healing nothing?
- When a taunted member drinks instead of attacking, does the taunt keep for its next
  attack, or does the drink spend it?
- With Auto on, below what share of their health does a member drink a potion?
- With Auto on, when the player takes back a drink Auto ordered, does the player's choice
  hold, or does Auto order the drink again?
```

**Why:** The game is built with a default for now on each of these, in "Drinking a
potion is an order used at the next cooldown, for now": a member can drink at full
health, a drink leaves the taunt standing, Auto drinks below 30%, and Auto orders the
drink again over the player's tap. The pending changes to this list above are unchanged;
these go at the end of the list, after the original's last entry.

## Change: A new Rogue's worked cooldown is 71 ticks

> Proposed 2026-11-19 · for review

**Where:** `## Cooldowns`, the worked list for the Rogue, first entry

**Now says:**

```
- Dexterity 5, a newly recruited F-rank member — 80 ticks
```

**Proposed:**

```
- Dexterity 8, a newly recruited F-rank Rogue — 71 ticks
```

**Why:** The user, 2026-11-18: "if something from the new docs contradicts the choices
that we make the new docs win". Battle Test's teams set a new F-rank Rogue at Dexterity 8
before help (see the `Guild Members.md` change "Starting stats by type"). 100 ÷ (1 + 8 ÷
20) is 71.4, so 71 ticks, which is what this doc's own seconds list already says: "A
newly recruited F-rank Rogue, 71 ticks". No combat type starts at Dexterity 5. The rest
of the list is unchanged.

## Change: A special goes off by itself, in its own turn

> Proposed 2026-11-24 · for review

**Where:** `## The Special Bar`, first paragraph (new paragraphs after it)

**Now says:**

```
Each member and each enemy has a special bar, and the special fires the moment that bar is
full — the same for both sides. It goes off once the attack that filled it has finished
resolving, and it takes no action of its own, so a member doesn't give up an attack to use
it. Each hit a member lands charges that member's bar: the first hit of an attack charges
it by 30, and each additional hit — another strike of a multi-strike attack, or another
target the attack reaches — charges it by 5. That's the base, and it's the same for
every type. A bar fills on about the third hit once a bonus condition has fired, which
is what puts a special inside the fight that earns it rather than the one after. Each
combat type also has its own bonus condition, and each time it's met it adds 15 on top
of that base — covered in the Individual Types doc. The attack that fills a bar need not
be the holder's own — a bonus condition can be met while the holder isn't attacking at
all, such as being hit or an ally taking a hit — and a bar that fills that way fires right
then, in the middle of whichever attack filled it, the same as it would on the holder's
own attack. The bar is full at 100.
```

**Proposed:**

```
Each member and each enemy has a special bar, and the special fires the moment that bar is
full — the same for both sides. It goes off once the attack that filled it has finished
resolving, and it takes no action of its own, so a member doesn't give up an attack to use
it. Each hit a member lands charges that member's bar: the first hit of an attack charges
it by 30, and each additional hit — another strike of a multi-strike attack, or another
target the attack reaches — charges it by 5. That's the base, and it's the same for
every type. A bar fills on about the third hit once a bonus condition has fired, which
is what puts a special inside the fight that earns it rather than the one after. Each
combat type also has its own bonus condition, and each time it's met it adds 15 on top
of that base — covered in the Individual Types doc. The attack that fills a bar need not
be the holder's own — a bonus condition can be met while the holder isn't attacking at
all, such as being hit or an ally taking a hit — and a bar that fills that way fires right
then, in the middle of whichever attack filled it, the same as it would on the holder's
own attack. The bar is full at 100.

A special goes off by itself. Nothing the player does, and nothing Auto does, can start,
hold or take back a special, and a special and an ordered drink don't affect each other.
A special takes its own turn and never lands at the same moment as another attack, hit
or special. One that comes ready goes ahead of every attack that comes ready on the same
tick, its holder's own free attack included, with no Dexterity compared and no draw
between them; an attack that came ready on an earlier tick and is still waiting keeps
its place ahead of it. Specials that come ready together go by their holders' own
Dexterity, help from the support ring left out, highest first, then by a random draw.

A bar filled in the middle of someone else's attack goes off after the hit that filled
it and before that attack's next strike or next target, and the rest of the attack
carries on against the fight as the special left it: a Fighter's first strike can fill a
Tank's bar, so that its second strike meets Shields Up. When one strike fills several
bars, they all go off after it, in the order above, so the order is set strike by strike
rather than at the end of the attack. A special's own hits can fill someone else's bar
the same way, so one special can go off in the middle of another. A special that has to
wait doesn't hold the attack up: the attack carries on without it, and the special goes
once its wait ends.

Going off costs the holder nothing of its cooldown: the wait already running carries
on, and when it comes up the holder makes its ordinary attack, or drinks if ordered to,
never a special in its place. The attack that filled the bar still gets its Luck reset
check. Charge earned while the bar is already full, such as the later strikes of the
attack that filled it, is lost rather than carried into the next bar.

A Fighter's flurry and a Brute's special wait the way a close-range attack does, until
their target is back in its own spot, keeping that target and picking again only if it
dies, goes out of reach or vanishes. A special whose holder dies before it goes off is
lost, and none goes off once the battle has ended.

For now:

- A Fighter's or a Brute's special also waits until its holder is home. When the
  holder's own attack filled the bar, it walks home first and then goes out again for
  the special, ahead of any free attack that attack earned.
- Volley and the Mage's field don't wait: they hit their target where it is, the way an
  Archer's or a Mage's ordinary attack does. Vanish and Shields Up have no target, so
  they never wait.
- A bar already full when a fight begins goes off as the fight's first step, once the
  battle's intro, or the ride in from the last battle, is over: after every opening Luck
  check and before the first attack. That covers a bar carried full from the floor's
  last battle.
- Each member's skill button shows how full that member's bar is. Pressing it selects
  that member, so the next tap on the grid moves them, and orders nothing.
```

**Why:** The combat engine and the battle screen are built this way. The original has a
special go off the moment its bar is full, taking no action, but doesn't say where it
falls among the other attacks on its tick, what becomes of charge earned while the bar
is full, or what a bar already full as a fight begins does. Ordering it keeps the one
rule of ours that beats the new docs — nothing lands at the same moment as anything
else — and a close-range special waits for its target for the same reason a close-range
attack does, as "A close-range attack waits for its target to be home" says. The skill
buttons stay as a display of the bar, now that nobody orders a special. Each "for now" in
the list is proposed as a question in "Questions on a special going off by itself".

## Change: Questions on a special going off by itself

> Proposed 2026-11-24 · for review

**Where:** `## Open Questions`, at the end of the list

**Now says:**

```
- For a far-range attacker, each row further back counts double when the eighty is
  shared out. Is that the right weight, and should it hold the same way on a grid three
  rows deep as it does on the five-wide one?
```

**Proposed:**

```
- For a far-range attacker, each row further back counts double when the eighty is
  shared out. Is that the right weight, and should it hold the same way on a grid three
  rows deep as it does on the five-wide one?
- When an Archer's Volley or a Mage's field goes off and the enemy it aims at is out of
  its spot on an attack, should the special wait for it to walk back, or hit it wherever
  it is?
- A Fighter's or a Brute's own attack is usually what fills its special bar, and it is
  out at its target when that happens. Should it walk back to its spot first and then
  fire the special, or fire straight from where it stands?
- A special bar that is already full when a fight starts — carried over from the floor's
  last battle — should it go off the moment the fight begins?
- Tapping a member's skill button no longer fires anything. Should the tap still select
  that member, so they can then be moved on the grid, or should the button do nothing at
  all?
```

**Why:** The game is built with a default for now on each of these, in "A special goes
off by itself, in its own turn". The pending changes to this list above are unchanged;
these go at the end of the list, after them.

## Change: A tie for least health, and how the rows share the eighty, for now

> Proposed 2026-11-24 · for review

**Where:** `## Targeting`, last paragraph (new paragraphs after it, ahead of the one the
pending "How a taunt is spent" change adds)

**Now says:**

```
A close attacker facing five in a front line gives the weakest of them 36% and each
of the others 16%.
```

**Proposed:**

```
A close attacker facing five in a front line gives the weakest of them 36% and each
of the others 16%.

Health left is counted in health points, not as a share of each one's most. For now,
when more than one target the attacker can reach is tied for the least, the twenty is
split evenly between them: with two of those five tied, it's 26%, 26%, 16%, 16% and 16%.

For now a far-range attacker shares the eighty out to the rows first, then evenly among
the targets it can reach in each row. A row's weight comes from where it sits on the
grid: each row counts double the row directly in front of it, whether or not that row
has anyone in it, and a row with no one the attacker can reach gets none of the eighty.
So with the middle row empty, the back row counts four times the front. With two in the
front row and one behind them, the weakest in front, the weakest gets 33⅓%, the other in
front 13⅓%, and the one behind 53⅓%. Every chance is the exact figure, never rounded to
a whole percent, and they always add up to a hundred.

Every attack that picks a target picks it this way, on both sides, specials and a
specialist's attack included.
```

**Why:** The combat engine is built this way. The original doesn't say how a tie for
least health shares the twenty, or how "each row further back counting double" treats an
empty row and the targets inside one row. Splitting the tie evenly, picking the row
first, and weighting a row by its place on the grid even across an empty row are the
user's going-ahead defaults, 2026-11-24. The original's own question on the far-range
weight is unchanged and stays open.
