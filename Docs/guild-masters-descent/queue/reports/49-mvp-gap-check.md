# MVP gap check against the updated design docs

> **Status:** Report for queue item #49, 2026-11-12. Rows below were queued under the user's
> standing yes, ahead of the builds they unblock.

## What was found

Nothing the other dev's updated design docs specify for the first version is missing from the
build beyond what #50–#58 already hold (from the reconcile, #48). What remains is five open
questions in the originals that will stop those builds partway unless they are answered first.
All five are queued as `decide:` items, on top of the queue, so they reach the user before the
builds that need them.

One more thing worth knowing: **injuries never happen in the game as built.** Nothing in a dive
injures a member — only the screenshot tool does — so "injuries heal while the player is away"
never shows. #3 already asks whether a dive can leave a member injured; if #3 is closed as
answered by the originals, that question has to be carried forward rather than lost.

## Proposed

PROPOSAL: decide: how a real-time fight's clock starts and where a special falls on it. Two questions are quoted from the originals: "When a fight starts, where do the cooldowns stand — everyone's empty and waiting out a full first wait, everyone's ready at once, or staggered somehow?" and "When a member's cooldown comes up, do all the strikes of a multi-strike attack resolve at once?" The third is ours: does a special the player taps fire at once or on the member's next cooldown, and does it use up that cooldown? [research] [S] — #50 (cooldown combat) and #58 (live specials) can't be specified without these.

PROPOSAL: decide: the damage math's three open rules. All three are quoted from the originals: "Which way does that round?" (fractional damage), "Does that damage count as an area attack too, paying two-thirds defence, or is the reduction only for an attack that is aimed?" (the Mage's field), and "is that the same check that can reset a cooldown, or a separate roll of its own?" (the flurry's fifth and sixth strikes) [research] [S] — #51 has to pin all three in its tests; rounding alone decides whether a hit from far below a member's rank is chip damage or nothing.

PROPOSAL: decide: "A rest floor is still a floor. Does arriving at one give the fifteen per cent only, or the five per cent for the floor as well?" [research] [S] — #54 builds the rest-area heal on this.

PROPOSAL: decide: "Crossing a rank costs a set amount of experience, and reaching the next rank also needs a level threshold — 16 levels for the first, doubling after. Does the experience buy those levels at an even rate, or do the two run on separate counters with whichever is slower deciding?" [research] [S] — #56 can't pin the path to level 16 without it, and experience is in every save, so a wrong guess changes the save format.

PROPOSAL: decide: how a Cook's healing and a Porter's carry grow with level and with the first promotion. The originals say "their specialty improves alongside" and "For a specialist, promotion makes the same ability stronger", yet give the Cook's heal as a flat five and fifteen per cent [research] [S] — the first promotion is in the first version, and as built, promoting a Cook or Porter changes only its stats.

## Dropped

- "decide: how a mission's outcome is decided" and "Mission board and timed missions" from the
  2026-11-11 proposal — timed missions are now Not included.

## Already covered

- Combat rules, health, healing, gear, progression, enemies and the live battle screen — queued
  as #50–#58.
- The Cook's and Porter's base cooldown is a missing number, not a rule: #50 uses a placeholder.
- Dive loot, a dead member's share of experience, whether a special's own hits charge the bar,
  and the loot and carry follow-ups — held by blocked items #48 and #27.
- Not proposed on purpose: which enemies can reposition, speeding a fight up, the enemy grid
  filling past fifteen, and how a ready special reads at a glance — the first version ships
  without the first three, and #58 settles the last by building it and looking.

## Needs your call

None beyond the five queued questions.

## Open Questions

None.
