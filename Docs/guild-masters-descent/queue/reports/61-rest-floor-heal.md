# Does a rest floor give the floor's heal too?

> **Status:** Research for queue item #61 — parked on one question for the user.

## The question

From the open questions in `Guild Members.md`, worded as the user wrote it:

> A rest floor is still a floor. Does arriving at one give the fifteen per cent only, or the
> five per cent for the floor as well?

Item #54 (healing as percentages) builds on the answer, and the Cook's extra stacks on
whichever reading wins.

## What the docs and the code already say

- `The Dungeon.md`, The Dungeon: "Between floors, every member gets back five per cent of
  their maximum health, and nothing comes back between the battles on a single floor. Every
  5th floor is a safe rest area, where every member gets back fifteen per cent". It names
  both figures and does not say whether arriving at floor 5 counts as "between floors".
- `Specialists.md`, The Cook: "another five per cent" between floors and "a further fifteen
  per cent" at a rest area, "on top of what the party gets anyway". So the Cook follows the
  same reading as the party.
- `EhrensDocs/The Dungeon.md` (change note): "For now a rest area is a safe floor with no
  battles on it".
- The built dive (`Dive.cs` on `queue/build`) agrees: floor 5 has no battles. Clearing
  floor 4 moves the party onto floor 5 and it heals there; pushing on from floor 5 moves it
  straight to floor 6's first battle with no heal. Today's heal is a flat 3 health at the
  rest area (+2 per Cook) and nothing between floors — #54 replaces both with percentages.
- A party that re-enters at a rest area by teleport heals nothing on arrival; that is
  settled separately and none of the readings below change it.

No outside source settles this — it is a rule of this game, not a fact about the world, so
the research is the docs and the code above.

## Two floor-changes touch a rest floor, not one

Because the rest floor has no battles, the party crosses two floor boundaries around it:
floor 4 into floor 5 (arriving), and floor 5 into floor 6 (leaving). That gives three
readings rather than two:

| Reading | Arriving at floor 5 | Leaving for floor 6 | Healed over floors 1–6 | With one Cook |
|---|---|---|---|---|
| A. Rest area replaces the floor heal | 15% | — | 30% | 60% |
| B. Both, on arrival | 20% | — | 35% | 70% |
| C. Floor heal on leaving instead | 15% | 5% | 35% | 70% |

Totals count the three floor-changes 1→2, 2→3, 3→4 (5% each) plus the rest floor. "With
one Cook" doubles each figure, since the Cook adds the same five and fifteen again.

What each means for the player:

- **A** — the rest area shows exactly the "fifteen per cent" the docs name. The deeper half
  of each five-floor stretch is slightly harsher.
- **B** — the rest area is a bigger moment (a fifth of everyone's health back). The number
  the player sees there, 20%, is not one the docs name anywhere, so the docs would need it
  written in.
- **C** — same total as B, but the extra 5% arrives only *after* the player chooses to push
  on. When the player is deciding whether to go home, the party looks the same as under A;
  the bonus is a small cushion for the next floor's first battle.

## Recommendation

**A — fifteen per cent only.** It keeps the two figures the docs already state as the whole
rule, with no derived 20% to explain, and it matches the built dive, where a rest floor is
a stop rather than a floor that was fought. B is the pick if rest areas should feel more
generous; C splits the difference but makes the heal arrive after the decision it would
inform, which is the least readable of the three.

How hard to change later: cheap. It is one line in the dive's floor-change step and a
tuning number either way; nothing saved depends on it, and #54's tests would change by a
figure or two.

## Contradictions

None. The docs leave the case open rather than contradicting each other, and the code does
not yet heal between floors at all, so no reading is ruled out.

## Open Questions

- A rest floor is still a floor. Does arriving at one give the fifteen per cent only, or
  the five per cent for the floor as well?
