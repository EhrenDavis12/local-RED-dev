# What happens to a guild with no members and no money

> **Status:** Research for queue item #102, 2026-11-15. Parked on one question for the user.

## The question

Death in the dungeon is permanent, and the guild can't go into debt. If every member has
died, the gold is under the cheapest hire, and nothing in the stores sells for enough to
make up the difference, the save can't move again. Nothing gives the guild gold without a
member, so waiting doesn't help.

## What the game does today

Read from the code on `queue/build`:

- A new guild starts with 500 gold, no members and no gear (`Tuning.StartingGold`,
  `SaveManager.NewGame`).
- The cheapest hire is a novice specialist at 80 gold; an F-rank diver is 100
  (`Tuning.RecruitHireCostSpecialistNovice`, `RecruitHireCostDiverF`).
- Only gear in the stores can be sold, for half its shop price (`ShopSellSharePercent = 50`);
  gear a member is holding can't. Shop prices run 60–80 for the weapons, so one stored
  weapon sells for 30–40.
- Missions cost nothing to send and pay gold; a dive costs 2 gold a member at F.
- A whole party that dies brings nothing home — gear only comes back with a survivor who
  has room.
- The only way out of a stuck save today is starting a new game over its slot from the
  New Game screen, which asks first.

So the stuck state needs all three at once: **no members, gold under 80, and the stores'
sell value plus the gold still under 80.** A guild with even one living member is never
stuck — missions are free and pay gold, and injuries heal on their own. A guild with only
divers on the board and 80–99 gold isn't stuck either: the board restocks over time.

How it happens in play: the player spends most of the 500 on gear and hires, then the
whole roster dies on one dive. It's quite reachable in the first hour.

## What the docs say

- `The Dungeon.md` — "Death in the dungeon is permanent — there is no way to bring a dead
  member back. The risk is inherent in the choice." That's about members, not the guild.
- `EhrensDocs/Core Concept.md` — the no-debt change note: a payment the guild can't
  cover doesn't happen.
- `EhrensDocs/Core Concept.md` also adds the open question "Does a new guild start with
  any members or gear, or only gold?" — still open; the code answers it with gold only.
- No doc mentions a guild losing, closing, or being rescued.

## The options

**A. The guild falls — game over.** A screen says the guild has fallen and offers a new
game in the same slot. *In the game:* real stakes, roguelike feel; the player loses every
hour of real time they put in, including time away. *Cost:* small — a check after a dive
and a mission, and one screen that reuses New Game's overwrite. Easy to change later
(the save isn't touched until the player says yes).

**B. A free recruit when the guild is empty and broke (recommended).** When the roster is
empty and the gold plus everything sellable can't cover the cheapest hire, the recruiting
board offers one F-rank diver for free. *In the game:* the guild limps on with one
newcomer who can run missions (free) to earn gold back; the dead stay dead, the gear and
gold are still gone. *Cost:* small — one rule worked out from what's already saved (no
new save field), and a "free" label on the board. Easy to change later. It can't be
farmed: it only appears with nobody on the roster, so it's never more than one member,
and dismissing that member gives nothing back.

**C. A trickle of gold while the guild is empty.** With no members, gold slowly rises
over real time until it reaches the cheapest hire. *In the game:* the player has to wait
— minutes or hours — before they can hire again. Fits the real-time design, but it's a
wait with nothing to do, and "how fast" is one more number to tune. Cost similar to B.

**D. Stop it happening.** Refuse to start a dive that takes every member, or keep a
reserve the player can't spend. *In the game:* the player hits a "no" they don't
understand, and it still doesn't help a guild whose one stay-at-home member is dismissed.
Not recommended.

## Recommendation

**B, the free recruit.** The game's stakes are about who you send and who comes back, not
about losing the guild; B keeps every member's death permanent and every lost coin lost,
and only removes the dead end where the save can never move again. It's also the cheapest
to build and the cheapest to undo: it saves nothing new. A is the right choice if the user
wants the guild itself to be what's at risk.

## Open Questions

- When the guild has no living members and can't afford to hire anyone, what should
  happen — the guild falls and you start over, one free recruit to carry on, gold trickles
  in until you can hire, or the game stops you sending everyone?
