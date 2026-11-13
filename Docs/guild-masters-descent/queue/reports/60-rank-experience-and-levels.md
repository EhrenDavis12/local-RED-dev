# How a rank's experience cost and its level threshold fit together

> **Status:** Research for queue item #60, 2026-11-12. Parked on the user's call; nothing
> here is a decision.

## The question

From `Guild Members.md` → Open Questions, verbatim:

> Crossing a rank costs a set amount of experience, and reaching the next rank also needs a
> level threshold — 16 levels for the first, doubling after. Does the experience buy those
> levels at an even rate, or do the two run on separate counters with whichever is slower
> deciding?

## What the docs and the code say now

- **The originals** (`Guild Members.md` → Promotion) give two numbers per rank: the level
  threshold (16, 32, 64 … 2048) and the experience cost (20, 100, 500 … 1,562,500). They also
  say a member *stops gaining levels* at the threshold and "neglecting a promotion wastes the
  experience the party keeps earning in the meantime". Nothing says what one level costs.
- **EhrensDocs** has a pending question on whether leftover experience carries to the next
  level, and nothing on this one.
- **The code** (`Core/Guild/Member.cs` `AwardXp`, `Core/Guild/Xp.cs`, `Core/Tuning/Tuning.cs`)
  runs one counter: a flat placeholder of 2 experience a level, leftover carries between
  levels, everything past the cap is thrown away, and promotion checks only the level and the
  gold. So today F to E costs 30 experience, not the docs' 20 — a placeholder, not a
  contradiction anyone chose. The save holds a level and one experience amount per member.

## The options

**A. One counter: the rank's cost is spread evenly across its levels.** Climbing from level
1 to 16 costs the 20 experience in total, about one and a third a level; E to D spreads 100
over levels 1 to 32. Since the costs don't divide evenly, each level is reached when the
running total passes its share, rounded up (level 2 at 2, level 3 at 3, level 4 at 4, level
5 at 6 …), so the steps are uneven by at most one point and the total is exact.
- *In the game:* the experience bar and the level are the same progress. Hitting the
  threshold and having paid the rank's experience happen at the same moment.
- *The "wasted experience" line* reads exactly as written: at the cap, kills give nothing.
- *Save:* unchanged — a level and one experience amount, as now. The build only swaps the
  flat placeholder for the per-rank cost.

**B. Two counters, the slower one decides.** Levels come from some experience-per-level
rate, and separately the member banks experience toward the rank's cost; promotion needs
both.
- *In the game:* a member can sit at level 16 still short on rank experience, or have the
  experience and still be climbing levels — two bars to read on the member sheet.
- *Needs a number the docs don't have:* what one level costs. With both curves fixed by
  formula, one of the two is always the slower at every rank, so the other never matters;
  B only earns its keep if the two are tuned separately.
- *The "wasted experience" line* needs restating: does the rank bank keep filling while
  levels are capped?
- *Save:* adds a second experience amount per member. The game isn't released, so no
  player's save would break — the cost is redoing the levelling tests and the member sheet.

## Recommendation

**A.** It's the only reading where the doc's own "stops gaining levels … wastes the
experience" sentence holds with no extra rule, it needs no new number, the member sheet
keeps one bar, and the save stays as built. B adds a per-level rate the docs would have to
invent and a second counter whose only effect is that one of the two always wins.

## What it means for #56

Under A, #56 builds "level N of a rank is reached at ceil(cost × (N−1) ÷ (threshold−1))
experience earned in that rank", replacing the flat 2-a-level placeholder. Under B, #56
needs the per-level rate decided first.

## Sources

- `Docs/guild-masters-descent/Guild Members.md` — Levels and Experience, Promotion, Open
  Questions
- `Docs/guild-masters-descent/EhrensDocs/Guild Members.md` — pending levelling questions
- `src/guildmasters-descent/Assets/Scripts/Core/Guild/Member.cs`, `Xp.cs`,
  `Core/Tuning/Tuning.cs`, `Core/Guild/Guild.cs` (promotion check) on `queue/build`
