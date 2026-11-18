# PRD: Fight opening

> **Status:** Draft · Source docs read: Combat.md, EhrensDocs/Combat.md, EhrensDocs/Platform.md
> (plus every other design doc and change note, for conflicts — none found)

## Problem

Every combatant starts a fight a random 0–50% of the way into its first wait. The design
docs say something else: cooldowns start empty, and the only thing that skips the first
wait is a Luck check made as the fight begins. The engine makes no opening Luck check at
all.

## Goal

Every fight opens with every cooldown empty. Each combatant makes one Luck check as the
fight begins, pulled from its own Luck bag; a True means it attacks on the fight's first
tick, a False means it waits out its whole first cooldown. The random head start is gone.

## Requirements

1. **No head start.** When a fight begins, every combatant's first wait is its full
   cooldown, as worked out from its type and its own Dexterity. The random opening share is
   removed, and so are the two tuning numbers that set its range.
   *Combat.md, Cooldowns ("Cooldowns start empty at the beginning of a fight").*

2. **One opening check per combatant.** As the fight begins, every combatant makes exactly
   one Luck check: every guild member, every specialist, and every enemy.
   *Combat.md, Cooldowns ("every combatant — guild member and enemy alike — makes one Luck
   check of its own"); EhrensDocs/Combat.md, "Every character's own Luck bag" (specialists
   have bags too).*

3. **The check is one pull from the combatant's own bag.** It is the same pull the Luck
   reset makes: one token, not put back, with the bag filled first if it is empty and filled
   again if the pull takes its last token. A member's pull comes out of the bag they carry
   between battles and dives, so it is gone from that bag afterwards. An enemy's comes out
   of the new bag it got for this battle.
   *Combat.md, Luck Checks ("Every Luck check a character makes draws from the same bag");
   EhrensDocs/Combat.md, "Every character's own Luck bag". A default for now: see Open
   Questions.*

4. **A True is a full jumpstart.** The combatant is ready on the fight's first tick, the
   tick the fight starts on, before any wait has passed (tick 0 in the engine, where today
   nobody can act before tick 1). There is no partial charge. A False leaves it waiting out
   its full first cooldown (requirement 1).
   *Combat.md, Cooldowns ("attacking on the first tick… A success is a full jumpstart, not
   a partial charge").*

5. **The opening attack is an ordinary attack.** A combatant that starts ready attacks
   because its cooldown is full, not because it is owed a free attack. That attack gets the
   Luck reset check after it, counts as one of its owner's cycles for a lasting effect, and
   can be a special if the bar is full.
   *Combat.md, Cooldowns ("starts the fight ready instead of empty") and Luck Checks (only
   the reset's free attack goes without a check); EhrensDocs/Combat.md, "The free attack
   comes first, and a special gets no check, for now". See Needs your call: this is a
   reading of the docs.*

6. **Same-tick rules are unchanged.** Every combatant that starts ready is due on the same
   tick, and the rules that already exist resolve them: damage is worked out against where
   things stood at the start of that tick. Close-range fighters who pick each other take
   turns, with the higher Dexterity first and a random draw between equals. This feature
   adds no ordering of its own.
   *Combat.md, Cooldowns (same-tick paragraph); EhrensDocs/Combat.md, "Close-range fighters
   take turns on the same tick, for now" and "A close-range attack waits for its target to
   be home".*

7. **Only a real fight checks.** The opening checks are made when a fight begins: a dive's
   battle, a mission played as a battle, or the demo encounter. Setting up combatants only
   to show them pulls nothing. The party planning grid builds a battle just to draw the
   placed members, and opening it must not take a token from anyone's bag. Today the head
   start draws only from the battle's dice, so this was harmless; a pull from a member's own
   bag is not.
   *Combat.md, Cooldowns ("as the fight begins") and Luck Checks (a part-used bag carries
   over); EhrensDocs/Platform.md, Saving ("never refills a bag or hands back a token").*

8. **Exactly once, across a save.** A fight saved at any point after it began resumes with
   the opening checks already made. They are never made again on loading, and none is lost.
   The cooldowns and bags the save already holds are enough to carry this.
   *EhrensDocs/Platform.md, Saving ("the same rolls and all… nothing is drawn again as it
   loads").*

9. **Deterministic.** Two fights with the same seed and the same setup open the same way:
   the same combatants start ready, and every later roll matches. The opening pulls are
   made in a fixed order, and each uses the battle's own dice, the way every other pull
   does.
   *EhrensDocs/Combat.md, "The clock, and a multi-strike attack landing in one tick" ("the
   same fight with the same rolls plays out the same").*

### Note for test-author

The existing suite pins the old opening. The cooldown test kit works out first-action ticks
from the opening-share range, and some tests read the two opening tuning numbers. Those
tests go, and tests for requirements 1–9 replace them. Any seeded fixture that searched for
a seed that "reaches a moment" will land on different seeds, because each combatant's
opening draw is now a bag pull instead of a range draw.

## Out of Scope

- Changing the Luck bag itself (its size, its fill rule, or whose bag is whose). That was
  built in #129 and stays as it is.
- How the battle screen and the battle intro show an attack on the first tick.
- Loading a save from before cooldowns were saved. It keeps its current handling.
- Any new tie-break for a first tick with many attackers (requirement 6).

## Open Questions

- The Luck check each combatant makes as a fight begins is called "a separate roll", using
  "the same chance" as the reset. Now that every Luck check a character makes draws from
  its own bag, is the opening check a pull from that bag too, or a roll of its own?
  *(EhrensDocs/Combat.md, "Questions on the Luck bag's defaults". Built for now as a pull
  from the bag, requirement 3, per the dispatch for queue #130: a cheap default the user
  may change.)*
