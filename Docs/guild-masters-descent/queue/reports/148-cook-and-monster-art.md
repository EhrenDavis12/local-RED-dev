# Art for the Cook and the monsters

> **Status:** Queue report for #148, 2026-11-18. Read once and acted on, then removed.

## What was found

Read from annie's queue and Chart in the animation checkout (`local-RED-dev`, read only) and
from the game on `queue/build`.

**The Cook.** The game still draws the Cook as a yellow box: it is the one type with no
entry in `CharacterArt.StandInStills` (`Assets/Resources/Characters/STAND-INS.md` says so).
The Cleric stand-in idea is out of date. Annie now has a Cook of its own:

- annie #243, **in review**: the user's own Cook picture, cleaned (hanging pot and pan
  removed, outline closed, transparent, sized to the Archer's height). Not approved yet.
- annie #259, **blocked**: the Cook's six basic poses; paid drawing is stopped until the
  Replicate account is topped up.
- The Cleric (design 1, healing stance 4, approved 9–10 Nov) is still there as a fallback,
  but it is a different character the game has no type for.

**The monsters.** In the game every monster is one of the six combat types and is drawn as
a mirrored guild member of that type (`Tuning.MonstersUseMemberTypeArt = true`,
`CharacterArt.cs:399`; types drawn at random, `Dungeon.cs:70-90`). The 15 Nov report was
right and the 13 Nov one is stale: every monster family's designs are **approved as
stills** (annie #100, #109, #110, #137, #182, #192, all 9–10 Nov):

| Family | Approved designs | What exists beyond the design |
|---|---|---|
| Goblin | Cutthroat, with a cleaver | six poses blocked on credit (all but the chop pass) |
| Orc / hobgoblin | Gorehorn (glaive), Ironjaw, Ironback, Warboss, Tusker | six poses blocked on credit |
| Skeleton | Gravehorn, Hound Skull (cleaver), Barrow Brute, Hollow Stalker | six poses blocked; a cleaver hit and miss effect (v1) |
| Spider | the round of 10, two to redraw | **Cave Stalker's six poses approved 17 Nov** (relaxed, ready, attack wind-up, attack strike, hurt, dead) |
| Dragon | all 5 of round 2, Sand Horn's horn fixed | six poses blocked; boss music approved |

None of them has a finished animation. What the game could use today is a still: one ready
pose per monster, held through every move, exactly as the Brute, Mage and Porter are drawn
now. The Cave Stalker is the one exception, with six approved poses the game could switch
between (a pose per move, no in-between frames). Annie's enemy death (the hurt pose breaking
into particles, approved 1 Nov) is already the death for anything without its own.

There are five families and six combat types, and the Mage has no monster at all.

## The options

**Cook**

1. **Keep the yellow box until annie's Cook is approved.** No work; the box goes the day
   #243 is approved and copied in. Recommended: it is close, and it is the right character.
2. **Use the cleaned Cook picture now** as an unapproved stand-in, like the Tank's. Small
   copy-in, but the game would carry art still in review.
3. **Use the Cleric as the stand-in.** Small copy-in, but it is the wrong character and gets
   replaced anyway.

**Monsters — use them or not**

1. **Use the approved stills now**, one ready pose per monster, with the Cave Stalker using
   its six poses. Monsters stop looking like the party's own people. Moderate: a monster art
   table, the mirrored-member switch off, and each monster drawn from its family's picture.
   Recommended, because the Goal says to use whatever exists.
2. **Keep mirrored members** until the monster animations exist. No work, but the animations
   are blocked on paid drawing with no date.

**Monsters — which family fights as which type** (only if they are used)

A suggested fit by look, not settled by any doc:

| Type | Family | Why |
|---|---|---|
| Rogue | Goblin | quick, small, a cleaver |
| Brute | Orc | big, glaives and tusks |
| Fighter | Skeleton | armed soldiers in a line |
| Archer | Spider | strikes from range, as webs or spit |
| Tank | Skeleton (Barrow Brute) or Orc (Ironback) | the heaviest of each family |
| Mage | Dragon | fire, an area attack like the Mage's field |

The dragon is built as a boss (boss music, "Dragon boss" on annie's Chart), and boss floors
are not settled in the docs, so using it as an everyday Mage spends it early. The other way
round: leave the Mage as a mirrored member until a caster monster is designed.

All of this is cheap to change later: the mapping is one table, and swapping a family for
a type is one line.

## What this contradicts

- EhrensDocs `The Dungeon.md`, around line 214: "For now the monsters might be limited to
  just the Archer's animations." The game already draws all six types as mirrored members.
  Left alone; #147 has already reworded the Open Questions page to the game as built.

## Open Questions

- The Cook: keep the yellow box until annie's own Cook is approved, use the cleaned Cook
  picture now, or use the Cleric?
- The monsters: use the approved stills now (one held pose each, the Cave Stalker with its
  six), or keep mirrored members until they are animated?
- If they are used: which family fights as which type, and is the dragon an everyday Mage
  or saved for a boss?
