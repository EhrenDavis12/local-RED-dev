# Member health — what the docs already say

> **Status:** Research for queue item #3, 2026-11-11. Answers what the docs settle; the rest
> parks as questions for the user.

## Where health comes from

Answered by the user (2026-11-11): every member starts at 10 health, a placeholder tuning
number. Landed as a change note in `EhrensDocs/Guild Members.md` for the other dev to
review.

Left open by it: `Guild Members.md` says a higher-rank hire "starts higher across the board
than an F-rank one". A flat 10 for everyone holds only if health is not one of the stats
rank scales. Cheap to change later — one number per rank in the tuning file.

## Does damage carry from battle to battle within a dive?

No doc says it outright, but two passages only make sense if it does:

- `The Dungeon.md`, The Dungeon: "Every 5th floor is a safe rest area, where the party
  heals" — healing at a rest area means damage from the floors before it is still there.
- `Specialists.md`, The Cook: "The Cook heals a little after every battle, and
  substantially more at a rest area" — healing after a battle means the damage outlives
  the battle.

Options:

1. **Damage carries** (what the docs imply). Health only comes back from the Cook, rest
   areas, and going home. Every battle wears the party down, and the push-on-or-go-home
   choice at floor 5 has teeth.
2. **Full health every battle.** Simpler, but the Cook's after-battle healing and rest-area
   healing would do nothing.

Recommendation: 1 — it is the only reading that gives the Cook and rest areas a job.
Cheap to change later (one rule in the combat engine).

## Is falling to 0 health in a dungeon battle death?

`The Dungeon.md`: "Death in the dungeon is permanent — there is no way to bring a dead
member back." `Equipment.md`: "If a member dies in the dungeon, the party brings their gear
back if there's room left". Training runs "can injure a member, but can never kill one".
No doc says what 0 health means in a battle.

Options:

1. **0 health is death, at once.** The member is gone for good; matches "permanent death"
   in the Focus most directly.
2. **0 health is "down"; dead only if the party loses or leaves them.** Softer, and gives a
   way for a down member to be saved by winning the battle.
3. **0 health is an injury unless something else happens** (e.g. a second hit while down).

Recommendation: 1 for the MVP — it is the plainest reading and the simplest to build.
Moderately cheap to change later; it touches the combat engine and the battle screen.

## What health does a member have back in the hall?

No doc says. Injury is a separate status (`Core Concept.md`: an injured member is out of
action until healed, recovers slowly for free or faster for gold) — so health and injury
are two different things.

Options:

1. **Back to full on return.** Health is a within-dive resource only; injury is the
   between-dive cost.
2. **Damage stays, heals over time in the hall.** Adds a second recovery clock next to
   injury.

Recommendation: 1 — injury already does the between-dive job, and a second clock would
double it. Cheap to change later.

## Open Questions

- Does a higher-rank hire start with more than 10 health?

- Does damage carry from battle to battle within a dive?
- Is falling to 0 health in a dungeon battle death?
- What health does a member have back in the hall?
