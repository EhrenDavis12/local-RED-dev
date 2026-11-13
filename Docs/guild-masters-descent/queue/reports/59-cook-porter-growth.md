# How a Cook's heal and a Porter's carry grow

> **Status:** Research for queue item #59 — parked on two questions for the user.

## The question

The originals say two things that pull against each other:

- `Guild Members.md`, Levelling: "Specialists gain base stats the same way divers do, and
  their specialty improves alongside."
- `Specialists.md`, Tiers: "For a specialist, promotion makes the same ability stronger."
- `Specialists.md`, The Cook: "another five per cent" between floors and "a further fifteen
  per cent" at a rest area. The Porter: "a lot more carrying capacity". Both are given as one
  fixed figure, with nothing for level or tier.

So the docs promise growth with level and with promotion, and give no rule for either. The
first promotion (Novice → Apprentice) is in the first version.

## What the game does now

- The Cook heals a flat amount of health — 1 after each battle won, 2 at a rest area
  (`Tuning.CookHealAfterBattle`, `Tuning.CookHealAtRestArea`, `Dive.cs` `CookHeals`). Not a
  percentage, and the same for every Cook at every level and tier. Percentages are item #54's
  job; this report sits on top of whichever form that lands.
- The Porter carries a flat 100 gold on top of the 10 every member carries
  (`Tuning.DivePorterExtraCarry`, `DiveRules.CarryLimit`). Same for every Porter.
- Levelling raises three base stats by one each, Cook and Porter included, using their stat
  weighting (Cook leads with Constitution, Porter with Strength).
- Promotion (`Guild.TryPromote`) moves the rung, resets the level to 1, keeps the stats, and
  resets health from the rung. Nothing about the specialty changes — which is the gap.

Contradiction to flag, not resolve: the original says the Cook's extra comes **between
floors**; the code gives it **after every battle won**. With 2–3 battles a floor, the code's
Cook heals two or three times as often as the doc says.

## The options

### What grows the ability between promotions

1. **The specialist's top stat.** Cook: Constitution. Porter: Strength. Each point above
   where they started adds a little (say a fifth of a per cent of heal per Constitution
   point, a few gold of carry per Strength point). This reads "improves alongside" literally
   — the specialty rises because the stats rise — and keeps the type's stat weighting
   meaningful for a specialist. A lucky Cook that rolls more Constitution heals better, the
   same way a lucky Fighter hits harder.
2. **The level itself.** Each level adds a step. The catch: promotion resets the level to 1,
   so a per-level bonus would vanish at promotion and the Apprentice would heal *less* than
   the Novice it was a moment before — unless the tier step is big enough to cover it, which
   ties the two numbers together awkwardly.
3. **Nothing.** Only promotion changes the ability; "improves alongside" is read loosely as
   the stats themselves improving. Simplest, but the level-up screen shows nothing for a
   specialist except stats it barely uses — a specialist has no gear and doesn't fight much.

### What the first promotion adds

1. **Half again** — Cook 5% → 7.5% and 15% → 22.5%; Porter 100 → 150.
2. **Double** — 5% → 10%, 15% → 30%, 100 → 200. Strong; two promoted Cooks would heal most of
   a party back at every rest area.
3. **A fixed step** — e.g. +2 points of per cent, +50 gold — the same step every tier.

In every case the figures are made-up placeholders to balance later, like the 10 and 100 of
the carry limit, and the doc's five and fifteen per cent and the Porter's 100 stay the figures
for a brand-new Novice.

## Recommendation

**Top stat for levels, half again for the first promotion.** The stat link is the only option
that gives growth between promotions without the promotion-resets-level problem, and it costs
nothing new to save — the bonus is worked out from stats and tier the game already stores.
Half again makes promotion feel like a real step without letting stacked Cooks trivialise rest
areas before anyone has balanced healing.

## What it would mean for the game

- The member screen can show a Cook's current heal and a Porter's current carry, and both
  tick up on a level-up that raised the top stat, and jump on promotion.
- Every option is a tuning change plus one small rule: cheap to change later, no save format
  touched.
- The Porter's 100-or-110 question (item #27) is separate: it decides what the 100 is added
  to, not how it grows.
