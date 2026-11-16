# Does the battle screen keep its pause button and x1/x2/x3 speed?

> **Status:** Report for queue item #111, 2026-11-16. Research only, no branch. Parks on two
> questions for the user.

## What the docs say

- The other dev's Combat doc, Player Input: "The fight never pauses, and nothing waits for
  the player. It runs from start to finish, and the player acts while it's running." And
  again: "The fight doesn't wait for the player, so the moment to use a special goes by while
  the fight carries on around it." EhrensDocs/Combat.md keeps the same sentence.
- The same doc leaves speed open: "Can the player speed a fight up or slow it down, and does
  that change anything in the simulation or only how fast it's drawn?"
- EhrensDocs/Core Concept.md (played missions) already assumes a pause menu: "Quitting from
  the pause menu is a retreat." That is our change note, and the Focus says the originals win
  where they disagree.
- Core Concept (both copies): a dive in progress does not advance while the game is closed —
  it picks up where it left off. That is about closing the app, not a button.

## What the game does now

- **Pause button** (top of the battle screen) opens a scroll pop-up with Resume, Back and —
  on a dive or a played mission — Quit, which asks "Leave the mission?" / turns the party
  back. While it is open the fight's clock stops, and the skill buttons, the focus target and
  the Retreat button are locked. Settings was dropped from that pop-up.
- **Retreat** already has its own button on the battle screen, outside the pop-up. So taking
  the pause button away does not strand the way out of a fight.
- **Speed button** steps x1 → x2 → x3 → x1. It multiplies how many seconds of fight pass per
  real second, the intro, effects and particles included. The fight is still counted in the
  same 50 ms ticks with the same rolls, so the same taps at the same fight moments give the
  same result. What changes is the player's real time to react: at x3 a special's window is a
  third as long.
- Both came in with annie's battle screen layout (queue #90, approved under the standing
  approval). annie's report #46 lists the battle HUD as "only flat mockups", and Look and Feel
  records no approval of the pause or speed controls.
- Closing or switching away from the app: Unity stops the game's frame loop on iPhone while
  it is in the background, so the fight freezes there whatever the button answer is. That
  holds the dive the way Core Concept says. It has not been checked on a device.

## Options

### Pause button

1. **Take it out (recommended).** The fight runs to the end as the original doc says; the
   player leaves with Retreat. Our "quitting from the pause menu" note would be rewritten to
   say Retreat. Keeps the pressure the doc builds combat around — a special you miss is gone.
2. **Keep it.** The player can stop mid-fight, which a phone game often wants (a doorbell, a
   call answered without leaving the app). It contradicts the original doc, so the doc would
   need a change note saying the user chose it over "never pauses".
3. **Keep a pause that hides the fight.** Pausing covers the battle, so it can't be used to
   plan a special in a frozen moment. A middle road; more to build than either above.

Cheap to change later either way: on-screen controls only, no save or rule change.

### Speed

1. **Keep x1/x2/x3 (recommended).** The doc leaves it open rather than ruling it out, the
   result of a fight does not change with the speed, and a long fight can be hurried. The
   answer to the doc's question would land as: it changes only how fast the fight is shown,
   not what happens — though the player gets less time to react.
2. **Keep only x1 and x2.** Less risk that a player at x3 just can't tap specials in time.
3. **Take it out.** Every fight runs at one speed; the fight's length is set by its tuning
   alone (the doc wants a fight to take about the same real time at any depth).

Also cheap to change later.

## Recommendation

Take the pause button out and keep speed at x1/x2/x3. "Never pauses" is a stated rule in the
original, and the Focus says the original wins; speed is an open question there, and the
built speed already answers it the cheap way — same fight, shown faster. Interrupted phone
play is still covered because the fight freezes when the app is put away.

## Open Questions

- Should the battle screen keep its pause button, or should the fight run without one?
- Should the speed button stay, and with which speeds?
