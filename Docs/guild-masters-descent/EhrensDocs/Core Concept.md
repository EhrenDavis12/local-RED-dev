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
complete and injuries heal while the player is away.
```

**Proposed:**

```
Time passes in real time, and it keeps passing while the game is closed — missions
complete and injuries heal while the player is away.

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
count: injuries healing, the recruiting board's and the mission board's restocks, and the
missions that are out. The two "for now" rules are defaults, not yet the user's word.
With no limit, setting the phone's clock forward heals the guild early and brings
missions home early; nothing guards against that.

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
member is below F. A mission gives no experience, and it doesn't touch health or wear
gear.

For now, while a member is out on a mission they can't be taken on a dive, sent on
another mission, have their gear changed, be promoted or be dismissed — not until
they're back. The next time the hall is shown after a mission ends, a notice says how it
went: the gold it paid, or who came home injured.

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
