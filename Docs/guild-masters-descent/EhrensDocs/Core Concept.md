# Core Concept — proposed changes

> **Status:** Change notes against `Core Concept.md`, for its owner to review. The original
> is not edited.

## Change: The guild can't go into debt

> Proposed 2026-11-11 · for review

**Where:** `## The Economy`, first paragraph

**Now says:**

```
Gold is the money in the game.
```

**Proposed:**

```
Gold is the money in the game. The guild can't go into debt: its gold never drops below
zero, and a payment the guild can't cover doesn't happen — nothing changes.
```

**Why:** No doc said what happens when the guild can't afford something. Promotion's "both
are required" already means a guild short of the gold can't promote; this states it once
for every payment, so the shop, recruiting, repair and paying to heal faster all work the
same way.

## Change: Three questions on the roster, injury and a new guild

> Proposed 2026-11-11 · for review

**Where:** `## Open Questions`

**Now says:**

```
- What changes at each rank from F to SSS?
```

**Proposed:**

```
- What changes at each rank from F to SSS?
- Does the roster cap count specialists as well as divers?
- If an already-injured member is injured again, what happens to the time left on the
  injury?
- Does a new guild start with any members or gear, or only gold?
```

**Why:** None of the docs answers these, and the guild's roster, injuries and starting
state all need an answer. The existing entry is unchanged.

## Change: How time away is counted

> Proposed 2026-11-11 · for review

**Where:** `## Time`, first paragraph (new paragraphs after it)

**Now says:**

```
Time passes in real time, and it keeps passing while the game is closed — missions
complete, injuries heal, and lost health is recovered while the player is away.
```

**Proposed:**

```
Time passes in real time, and it keeps passing while the game is closed — missions
complete, injuries heal, and lost health is recovered while the player is away.

Every second counts once, whether the game was open, sitting in the background or
closed: an injury heals by exactly the time that has passed since it happened. The
clock is real time, so changing time zone, or the clocks going forward or back for
summer time, neither adds time nor takes it away.

For now, there's no limit on how much time away counts — a player gone for a month
comes back to a month's healing. And if the phone's clock is set back, the guild's time
stands still until the clock catches up to where it was, so setting it back and then
forward again never counts the same time twice.
```

**Why:** No doc said how time away is counted, and the game now counts it. The existing
paragraph is unchanged. Everything that moves while the player is away moves by this one
count: injuries healing, lost health coming back, the recruiting board's and the mission
board's restocks, and the missions that are out. The two "for now" rules are defaults, not
yet the user's word. With no limit, setting the phone's clock forward heals the guild
early and brings missions home early; nothing guards against that.

## Change: Missions are in the first version, as F-rank jobs that pay gold

> Proposed 2026-11-14 · for review

**Where:** `## Missions`, last paragraph (new paragraphs after it)

**Now says:**

```
The intent is that mission rewards keep the guild going but don't advance it — the climb
comes from milestone quests and from what the dungeon yields.
```

**Proposed:**

```
The intent is that mission rewards keep the guild going but don't advance it — the climb
comes from milestone quests and from what the dungeon yields.

Missions are in the first version. Every mission is rank F, since the guild doesn't rise
above F in the first version. For now the board holds a handful of missions and is
stocked the first time it's opened. It restocks on a timer, open or closed: a restock
replaces every mission still on it, and a mission that's sent leaves the board and isn't
replaced until the next restock. A restock never touches a mission that's already out.

For now a mission needs exactly its stated number of members, no more and no fewer.
Divers and specialists can both go. A member already out on a mission, or in a dive that
hasn't ended, can't be sent. Sending costs nothing, and for now a mission can't be called
back early: once it's sent it runs its full length.

For now how a mission goes is decided the moment it's sent. When a mission appears on
the board it is secretly easier, as stated, or harder than its rank, and that sets its
chance of failing; who is sent — their stats, type, gear or how many — counts for
nothing. Because the outcome is fixed at sending, saving and loading, or how often the
game is opened while it runs, can't change it.

For now a mission that succeeds pays gold and nothing else — no items, no materials, no
gear, and it never finds a dungeon. A mission that fails pays nothing, and every member
sent comes home injured. A mission that ends while the player is away has already paid,
or already injured its members, by the time they're back, and an injury from it has
already healed by the time since the mission ended. No one dies on a mission, since no
member is below F. A mission that's sent gives no experience, and it doesn't touch
health or wear gear.

For now, while a member is out on a mission they can't be taken on a dive, sent on
another mission, be promoted or be dismissed — not until they're back. Their gear can
still be put on and taken off while they're out, since the outcome is fixed at sending
and never reads gear; it can't be changed while they're in a dive. The next time the hall
is shown after a sent mission ends, a notice says how it went: the gold it paid, or who
came home injured.

How many missions can run at once, how many the board offers, how often it restocks, how
long a mission takes, what it pays and how likely each kind is to fail are all
placeholders, to be balanced later.
```

**Why:** The user, 2026-11-14: "I need a way to send my guys out onto other missions to
make money." That brings missions into the first version, and the game is built this
way. Ranks above F stay out of the first version, the user's word on 2026-11-11.
The original says what a mission is, what failing costs and what it pays. It doesn't say
how the board fills, whether a mission's member count is exact, what decides the
outcome, or what the player can do with a member who is away. Every "for now" in the
new paragraphs is a default the build chose, not yet the user's word, and each one is
proposed as a question in "Questions on missions' defaults". The existing paragraphs are
unchanged: the longer-term design stands, with ranks above F, items, materials, gear,
claim missions, milestone quests and the Herbalist's and Miner's yield.

## Change: Questions on missions' defaults

> Proposed 2026-11-14 · for review

**Where:** `## Open Questions`, at the end of the list

**Now says:**

```
- What changes at each rank from F to SSS?
```

**Proposed:**

```
- What changes at each rank from F to SSS?
- What decides whether a mission succeeds or fails — do the members' stats, types, gear
  or number count — and what does the backend variance move?
- On a failed mission, are all the members injured or only some, and is any gold paid?
- Does a mission need exactly its stated number of members, or at least that many?
- Can a mission bring back gear in the first version?
- How does the mission board fill and refill?
- While a member is out on a mission, can the player change their gear, promote them or
  dismiss them?
- Can a mission be called back early?
- Can a member who is in a dive that hasn't ended be sent on a mission?
- How does the player learn that a mission finished, and how it went?
```

**Why:** The game is built with a default for now on each of these, in "Missions are in
the first version, as F-rank jobs that pay gold", and none of the docs settles them. The
pending "Three questions on the roster, injury and a new guild" change to this list is
unchanged.

## Change: A member on a dive can't be dismissed, for now

> Proposed 2026-11-15 · for review

**Where:** `## The Recruiting Board`, the paragraph beginning "A member can be dismissed"

**Now says:**

```
A member can be dismissed to make room on the roster. The gold spent recruiting and
promoting that member is lost.
```

**Proposed:**

```
A member can be dismissed to make room on the roster. The gold spent recruiting and
promoting that member is lost.

For now a member who is in a dive that hasn't ended can't be dismissed, even while the
player has stepped back out to the guild hall — not until the dive ends, the same as a
member away on a mission.
```

**Why:** The game is built this way. Dismissing a member partway through a dive can break
the save. It's a default the build chose, recorded as cheap to change and not yet the
user's word, and it's proposed as a question in "A question on dismissing a member on a
dive".

## Change: A question on dismissing a member on a dive

> Proposed 2026-11-15 · for review

**Where:** `## Open Questions`, at the end of the list, after the entries that "Questions on
missions' defaults" adds

**Now says:**

```
- What changes at each rank from F to SSS?
```

**Proposed:**

```
- What changes at each rank from F to SSS?
- Can a member who is in a dive that hasn't ended be dismissed?
```

**Why:** The game is built with a default for now, in "A member on a dive can't be
dismissed, for now", and none of the docs settles it. The pending changes to this list
above are unchanged.

## Change: A mission can be played as a battle, for now

> Proposed 2026-11-16 · for review

**Where:** `## Missions`, after the paragraphs that "Missions are in the first version, as
F-rank jobs that pay gold" adds

**Now says:**

```
The intent is that mission rewards keep the guild going but don't advance it — the climb
comes from milestone quests and from what the dungeon yields.
```

**Proposed:**

```
The intent is that mission rewards keep the guild going but don't advance it — the climb
comes from milestone quests and from what the dungeon yields.

Every mission on the board can be sent, or played: fought as a battle by the player, with
the members picked for it, on the same battle screen a dive uses. Play is refused whenever
Send would be, a free mission slot included, and a refused play changes nothing. The
mission leaves the board the moment the battle starts, so for now a played mission can't
be played again, won or lost. For now there's no planning step: the members are placed the
way the Dungeon Board places them, and the fight is in the meadow, since a mission is
above ground.

For now a played mission fields monsters drawn the way a dungeon's are, at the mission's
rank, and how many depends on its secret variance: one fewer than the members it needs
(never fewer than one) if it turned out easier, the same number if it's as stated, one
more if it turned out harder. The counts are placeholders. A mission isn't a floor, so
its monsters aren't built from a floor's power: each has its type's starting stats,
carries no gear, since there's no floor for the chance to come from, and its kill pays
its rank's value in full. Neither the monsters nor the variance shows
before the fight.

The battle plays by every rule any battle has. Gear wears as it's used, and a member
drinks from the potions packed for it as in any battle; the wear and the potions drunk
stay that way after the mission, and every potion left undrunk goes back to the stores.
Kills pay experience as in any combat, to the members still standing when it ends; a
retreat pays none.

For now a played mission has no timer: it ends the moment its battle does, and it never
shows among the missions out. A win pays the mission's gold at once, and nothing else. A
loss, a stand-off or a retreat pays nothing, and every member sent comes home injured,
whoever fell; a won mission injures no one. Leaving with the Retreat button is a retreat,
and so is quitting from the pause pop-up in a development build; once the battle is
decided neither one can undo it. No one dies: a member brought to no health drops out of
the fight, and after it everyone sent is back at full health and still on the roster. The
battle's result says how it went, so the hall's notice adds nothing.

The battle itself isn't saved, and the save doesn't change. If the game is closed partway
through, the mission is gone, unpaid, and nobody is injured, and the potions packed for
it are back in the stores, less any drunk. For now its fighters keep the health they had
when the game closed, one brought to no health coming back with 1, and heal from there at
home.
```

**Why:** The user, 2026-11-15: "i need a way to actually fight with out going into the
doungon to make some chash on my own. Allow me to auto a mission whcih it currently does
or let me run through it. from the mission board." The game is built this way. Kills
paying experience and gear wearing follow the originals' `## Levels and Experience` in
Guild Members and `## Durability` in Equipment, which govern any combat, so "Missions are
in the first version, as F-rank jobs that pay gold" now says its "no experience, no wear"
covers only a mission that's sent. Having no timer departs from the original's "Missions
are timed", so it stays a question. Every "for now" here is a default the build chose, not
yet the user's word, and each one is proposed as a question in "Questions on played
missions". Answered 2026-11-24: the pause is only in a development build, so in the game
as released a played mission is left with the Retreat button.

## Change: Questions on played missions

> Proposed 2026-11-16 · for review

**Where:** `## Open Questions`, at the end of the list, after the entries that "A question
on dismissing a member on a dive" adds

**Now says:**

```
- What changes at each rank from F to SSS?
```

**Proposed:**

```
- What changes at each rank from F to SSS?
- The original says missions are timed. Should a played mission resolve the moment its
  battle ends, or still run out the mission's timer before it pays? The default is the
  moment the battle ends.
- Who shares a played mission's kill experience? The default is the members still
  standing when it ends, as in a dive, so a loss pays none, a stand-off pays for its
  kills, and a retreat pays nothing.
- Should a played mission bring back items, materials or gear as well as gold, as the
  original docs say missions do? The default is gold only, until there is a rule for what
  and how much.
- Should a member drink their potion in a played mission, using it up? The default is
  yes, as in any battle.
- When the player retreats from a played mission, or it ends in a stand-off, are the
  members injured as on a loss, or do they come home fine with no pay? The default is
  injured.
- In a played mission, is injury per member (whoever fell is injured, win or lose) or per
  outcome (a loss injures everyone, a win no one)? The default is per outcome.
- If the game is closed partway through a played mission, the default loses the mission
  with no pay and no injury, so closing the game dodges a loss's injury. Should a cut-off
  battle count as a retreat instead? That would need a change to the save.
- How many monsters does a played mission field, and should the mission's hidden variance
  decide it? The default is one fewer, the same, or one more than the members needed.
- Can a played mission be replayed after it's lost? The default is no: it leaves the board
  when the battle starts.
- Does a played mission need a free mission slot, even though it never runs on a timer?
  The default is yes.
- If the game is closed partway through a played mission, its fighters keep the health
  they had when it closed, rather than coming back at full as they do once its battle is
  decided. Should a cut-off battle send them home at full too? The default is they keep
  it.
```

**Why:** The game is built with a default for now on each of these, in "A mission can be
played as a battle, for now", and none of the docs settles them. The pending changes to
this list above are unchanged.

## Change: A guild with no members and no way to hire gets nothing, for now

> Proposed 2026-11-17 · for review

**Where:** `## The Economy`, after the paragraph that "The guild can't go into debt" adds

**Now says:**

```
Gold is the money in the game.
```

**Proposed:**

```
Gold is the money in the game. The guild can't go into debt: its gold never drops below
zero, and a payment the guild can't cover doesn't happen — nothing changes.

For now nothing happens when the guild is stuck. If every member has died, the gold is
under the cheapest hire, and nothing in the stores sells for enough to make up the
difference, the game gives no help — no free recruit, no gold trickling in, and no screen
saying the guild has fallen. The player is better off starting a new game. This will
change later.
```

**Why:** The user, 2026-11-17: "For now nothing at this point a user is better off starting
a new game. This will be changed later." No doc said what happens to a guild with no
members and no money. Death is permanent and the guild can't go into debt, so a guild in
this state can never move again. A guild with even one living member is never stuck,
because missions cost nothing to send and pay gold. Starting a new game over the stuck
save already asks the player first, as the Platform doc's save slots say.

## Change: Lost health heals at home, for now

> Proposed 2026-11-24 · for review

**Where:** `## The Mead Hall`, first paragraph (new paragraphs after it)

**Now says:**

```
Health lost on a dive doesn't come back at once — a member that comes home hurt needs
time to heal, the same as an injury. With no Cook in the guild, health comes back on its
own at 1 point a minute, and there is nothing to pay for — waiting is all there is. The
mead hall is a room in the hall where the player pays gold to speed that up: recovery
happens on its own given time, and gold buys it sooner.
```

**Proposed:**

```
Health lost on a dive doesn't come back at once — a member that comes home hurt needs
time to heal, the same as an injury. With no Cook in the guild, health comes back on its
own at 1 point a minute, and there is nothing to pay for — waiting is all there is. The
mead hall is a room in the hall where the player pays gold to speed that up: recovery
happens on its own given time, and gold buys it sooner.

A member comes home from a dive with the health they ended it on, however it ended —
from a rest area, on a retreat or in a stand-off. From then on they get 1 point back for
every full minute, up to their maximum and never past it. The minute is counted the way
all time away is: open, in the background or closed, every second counts once. Part of a
minute is never lost; it carries over to the next point, across saving and loading too.

Only time at home counts. Time a member spends in a dive that hasn't ended, or in a
played mission whose battle isn't decided, heals them nothing, whether the game is open
or closed. A member out on a sent mission keeps healing, the same as one in the hall.
Once a played mission's battle is decided, everyone sent is back at full health anyway.

For now there is no mead hall to pay at, so every member heals at 1 point a minute,
whether or not the guild has a Cook. For now, too, lost health holds no one back: a
member short of health isn't injured, and can still be sent on a dive or a mission or
picked into a saved team. Lost health and an injury heal on their own counts, and neither
pauses or speeds up the other.
```

**Why:** The game is built this way. The original says lost health comes back at 1 point
a minute and keeps coming back while the game is closed, and that a dive doesn't advance
while closed, but not what time counts toward a member's healing while they're away
fighting, or what becomes of part of a minute. Lost health comes back by the same count
as everything else time moves, in "How time away is counted". A member on a sent mission
healing, and a played mission still sending everyone home at full, are the user's word on
2026-11-24. The "for now" rules are defaults the build chose, not yet the user's word.
Whether a member short of health may be sent stays a question, as the original's
`## Open Questions` already asks it.
