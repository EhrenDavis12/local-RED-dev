# Platform

> **Status:** Early design. The phone runs sideways and the game saves by itself; the
> save rules marked "for now" are defaults, not yet settled.

## Orientation

Always sideways. On the iPhone the game runs in landscape only — there is no portrait mode.

## Saving

The game saves by itself: the guild is saved when the phone sends the game to the
background, and when the game quits. There's no Save button, because on the iPhone a
backgrounded app can be killed with no warning, and a guild saved only on request would
lose play. Coming back from the background carries on with the guild as it was and
counts the time spent there, because the iPhone often never closes a backgrounded app.

A dive in progress is saved too. If the game is sent to the background or killed partway
through a dive, the save holds the dive itself, and opening the game again carries the
dive on where it stopped — partway through a floor, if that's where it was. Closing the
game never undoes a death: a member who died on the dive is still dead when the game
opens again.

For now that holds inside a battle too. A battle the game closed in carries on from the
turn it closed on, never from the battle's start, and the rest of it plays out exactly as
it would have if the game had never closed, the same rolls and all — closing and opening
the game can't re-roll a turn or dodge a death. A turn already played counts as played,
even if it hadn't finished showing on screen. Saving doesn't bank anything, either: the
gold found on the dive is still the party's until the dive ends, and what was found since
the last rest area can still be lost.

A save never costs the player the save before it. If saving fails, or the phone dies
partway through, the slot still holds the last good save, whole.

Loading never changes or deletes a save. A save the game can't read, or one made by a
newer version of the game, is reported as such and left on the phone as it is.

For now:

- There are three save slots. The number is a placeholder.
- Starting a new game in a slot that already holds a save — even one the game can't
  read — needs the player to say to overwrite it. The game never replaces a save on its
  own.
- A save with gear equipped where it can't be — on the wrong combat type, on a
  specialist, on two members at once, or gear that's no longer in the stores — is fixed
  as it loads: the gear comes off and goes back to the stores, and the save loads. Gear
  on two members stays with the one hired first.

## Open Questions

- If the game reopens in the middle of a battle, does the battle carry on from the turn it
  closed on, or start again?
