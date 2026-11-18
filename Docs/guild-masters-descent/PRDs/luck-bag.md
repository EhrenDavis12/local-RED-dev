# PRD: Luck bag

> **Status:** Draft, queue item #129 · Source docs read: `Combat.md`, `Individual Types.md`,
> `Guild Members.md`, `Battle Test.md`, `Core Concept.md`, `Equipment.md`, `Specialists.md`,
> `The Dungeon.md` (originals, the owner's 13 and 17 Nov edits); `EhrensDocs/Combat.md`,
> `EhrensDocs/Individual Types.md`, `EhrensDocs/Guild Members.md`, `EhrensDocs/Platform.md`,
> `EhrensDocs/Open Questions.md`; queue report `127-archer-accuracy-vs-luck-bag.md`. Code read
> on `queue/129-luck-bag`.

## Problem

Luck is a percentage roll everywhere it acts. The Luck reset rolls 25% × Luck ÷ (Luck + 60)
afresh after each attack (`Battle.cs:394-400`), evasion rolls 2% per point of the target's
Luck capped at 50% (`Battle.cs:611-616`, `Tuning.cs:259-263`), and the flurry makes two checks
of its own on a 50% × Luck ÷ (Luck + 20) curve (`FighterType.cs:35-48`, `Tuning.cs:268-272`).
A roll against a small chance can go cold for a very long time, and the owner's 17 Nov edit
replaced all three with one bag per character that guarantees the lucky event arrives.
Nothing in the save holds Luck state, so there is nowhere for a part-used bag to live.

## Goal

Every Luck check a character makes is a pull from that character's own bag of 50 tokens. The
bag is filled by the settled formula, refills only when empty, and a member's part-used bag
survives battles, floors, dives, level-ups and a save and reload. The Luck reset, evasion
and the flurry all draw from it. The tuning file no longer holds a miss chance or a flurry
Luck curve.

The requirements are in three groups so the test stage can be split by group: **A**, the
bag and the save; **B**, what draws from the bag in combat; **C**, the tuning file. A is
independent of B. B relies on A's pull.

## Requirements

### Group A: the bag and the save

**A1. Who has a bag.** Every character that fights has its own bag: every guild member,
divers and specialists alike, and every monster. No bag is shared.
*Source:* `Combat.md` § Luck Checks: "Every Luck check a character makes draws from the
same bag", and "Enemies get the Luck reset too, on the same terms as guild members".
§ Enemies: an enemy's own Luck stat is what decides whether it evades or resets its cooldown.

**A2. How many Trues.** A filled bag holds 50 tokens. The number that are True is
50 × 25% × Luck ÷ (Luck + 60), rounded up, and never fewer than 1. It is computed exactly,
because a floating-point error at an exact whole number would add a True. Worked figures the
tests should pin: Luck 0 → 1, 5 → 1, 7 → 2, 20 → 4, 40 → 5 (exactly 5, not 6), 60 → 7,
180 → 10. No Luck gives more than 13.
*Source:* `Combat.md` § Luck Checks, the paragraph on how many tokens are True and its
worked list. Luck 0 and Luck 40 are this PRD's, worked from the same formula.

**A3. A pull.** A pull takes one token at random from those left in the bag and does not
put it back. It is one draw from the battle's rng, a whole number from 0 up to but not
including the number of tokens left, and it is True when that number is below the number of
Trues left. Every pull makes exactly one draw, even when the result is certain because
only Trues or only Falses are left.
*Source:* `Combat.md` § Luck Checks: one token, "drawing without replacement".
`EhrensDocs/Combat.md` "The clock, and a multi-strike attack landing in one tick": the same
rolls give the same fight. The draw-even-when-certain rule follows the code's existing
convention (`Battle.cs:394-395`, `668-670`). The exact draw is this PRD's, so that tests
can script a True or a False.

**A4. Refill.** When a pull takes the bag's last token, the bag fills again straight away,
using the character's own Luck at that moment. Nothing else refills or rebuilds a bag: not
a new battle, floor, dive or mission, and not a level-up, a promotion or a change in Luck. A
bag is never re-checked against the character's current Luck.
*Source:* `Combat.md` § Luck Checks: "Once every token has been pulled, the bag fills back
up — and that's the only thing that refills it"; a member that levels up "keeps it exactly
as it is, and a refill uses the member's Luck as it stands at that moment".

**A5. The first bag.** A character's first bag is full, filled from its Luck when the
character is made. A member's is filled when it joins the guild. A monster's is filled when
it is added to its battle.
*Source:* none. The docs do not say how a bag starts. This is the PRD's default, listed
under Open Questions.

**A6. Whose bag carries.** A member's bag belongs to the member. It carries part-used from
battle to battle, from floor to floor, from dive to dive and into a mission played by hand,
and it is saved with the guild. A monster's bag lasts only for its battle, and it is saved
when that battle is saved.
*Source:* `Combat.md` § Luck Checks: "A part-used bag carries over rather than resetting,
from one battle to the next and from one floor to the next", and only emptying refills it
(A4).

**A7. The save.** The save version goes from 11 to 12. For each bag, the save holds how many
tokens are left and how many of them are True. A battle saved partway through and loaded
again makes the same pulls with the same results as it would have made without the save. The
same holds for a member whose bag is saved between battles or between dives.
*Source:* `EhrensDocs/Platform.md` § Saving: "the rest of a battle the game closed in plays
out exactly as it would have … closing and opening the game can't re-roll an attack or dodge
a death", and a save from a newer version is reported rather than read.

**A8. Older saves.** A save from version 11 or older loads every member with a full bag,
filled from the member's Luck as the save loads. Every monster in a saved battle loads the
same way.
*Source:* `EhrensDocs/Platform.md` § Saving: a save made by an older version still loads.
The full bag is this PRD's default, listed under Open Questions.

**A9. A bag that can't be true.** A saved bag can't be true if it has no tokens left, more
than 50 tokens, a negative count, or more Trues than tokens. Such a bag loads as a full bag
filled from the character's current Luck, and the save still loads. A bag is never judged
against the character's Luck, because a level-up legitimately leaves a bag whose Trues no
longer match it (A4).
*Source:* `EhrensDocs/Platform.md` § Saving, "For now": the fix-it-as-it-loads pattern used
for potions and special bars. Applying it to the bag is this PRD's default, listed under
Open Questions.

### Group B: what draws from the bag in combat

**B1. The Luck reset.** The Luck check a character makes after finishing an attack is one
pull from its own bag. A True owes the free attack, and a False does not. This replaces the
percentage roll at `Battle.cs:396-400`. Everything else about the reset stays as built: a free
attack and a special get no check, and a close-range attack that waited makes its check when
it finally attacks.
*Source:* `Combat.md` § Luck Checks, first and second paragraphs. `EhrensDocs/Combat.md` "The
free attack comes first, and a special gets no check, for now" and "A close-range attack
waits for its target to be home".

**B2. No reset pull once the fight is over.** If the attack ended the battle, no reset pull
is made and no token is spent.
*Source:* none. This is the PRD's default, listed under Open Questions. Its reason is that
`Combat.md` says the bag exists to guarantee the lucky event arrives, and a True pulled when
no free attack can follow would be thrown away.

**B3. Evasion.** Every strike that rolls to hit makes one pull from the bag of the character
it is aimed at. A True means the strike misses. Each strike of a multi-strike attack pulls on
its own, and each of the three enemies a Brute's cleave reaches pulls from its own bag. A
miss from a pull counts as a miss for every rule that reads one. This replaces the
miss-chance roll at `Battle.cs:611-616`.
*Source:* `Combat.md` § Luck Checks: "when a member is attacked, it pulls one token, and a
True means the attack misses … it needs no chance of its own". `Combat.md` § Attacks and
Reach: each strike "rolls to hit separately". `Individual Types.md` § The Brute: "each of
them can evade it individually".

**B4. What pulls nothing.** These pull no token:
- every hit of an area attack: the Mage's column, Volley, and every hit the Mage's field deals;
- every strike of an attack a vanished Rogue makes;
- a strike that never happens, such as one passed over because its target is vanished, or
  one lost because nothing is left in reach.

*Source:* `Combat.md` § Luck Checks: "An area attack pulls no token at all". `Guild
Members.md` § Base Stats on area attacks. `Individual Types.md` § The Rogue: while vanished,
"there's no hit check". `EhrensDocs/Guild Members.md` "The Mage's field is an area attack,
for now".

**B5. The flurry's strikes.** Each strike of the flurry rolls to hit like any other strike,
so it pulls from its target's bag (B3). That includes strikes carried to another enemy after
the first target dies, which pull from the new target's bag.
*Source:* `EhrensDocs/Individual Types.md` "The flurry's leftover strikes stay within reach,
and its strikes can miss, for now". Whether the flurry can miss at all is still open; see
Open Questions.

**B6. How long the flurry is.** A flurry makes one pull from the Fighter's own bag. A True
gives 6 strikes and a False gives 4. A flurry makes exactly one such pull, which replaces
the two chained checks at `FighterType.cs:35-48`. The pull is made as the flurry begins,
before its first strike, which is where the flurry's checks are drawn today. So it is spent
even if the fight ends within the first four strikes. This pull is not a Luck reset check,
and a flurry still gets no reset check after it (B1).
*Source:* `Individual Types.md` § The Fighter: "one Luck check — a pull from the Fighter's
Luck bag — then decides the last two together: a True adds both, a False ends the flurry at
four". The timing is this PRD's default, listed under Open Questions.

**B7. Order of draws.** Each pull takes the place in the rng order that the roll it replaces
holds today:
- the evasion pull comes first in a strike, before the weapon roll and the defence rolls;
- the reset pull comes after the attack's strikes;
- the flurry pull comes before the flurry's first strike.

No other draw moves.
*Source:* the code's fixed roll order (`Battle.cs:605-607`), which the scripted-rng tests
depend on.

### Group C: the tuning file

**C1. What leaves.** `MissChancePercentPerLuck`, `MissChanceCapPercent`,
`FlurryLuckCeilingPercent` and `FlurryLuckConstant` are removed from `Tuning.cs`, and nothing
reads a miss chance or a flurry Luck curve any more.
*Source:* `Combat.md` § Luck Checks: evasion "needs no chance of its own — it's the bag's own
density of Trues". `Individual Types.md` § The Fighter: the flurry is decided by one pull.

**C2. The bag's figures are rules, not tuning.** The 50 tokens, the 25%, the 60 and the
floor of one True are settled. They are fixed in code and are not added to the tuning file
as placeholders.
*Source:* `Combat.md`: the status line counts the Luck reset's chance as settled, and § Luck
Checks says "there's no cap rule".

## Out of Scope

- **What the Archer's accuracy raise does under the bag** (queue #127, not yet answered).
  The raise subtracted points from a miss chance, and C1 removes that miss chance, so the
  raise has nothing to act on. In this build an Archer's streak shot pulls from its
  target's bag like any other shot (B3), and the raise does not change that pull. The
  streak's damage raise, its cap, `ArcherStreakStepPercent`, and the rule that a miss resets
  the streak all stay as built. No test for this PRD may assert anything about the
  accuracy raise, so #127's answer can change it without breaking a test.
- **How a fight opens.** The random 0–50% head start (`Battle.cs:318-327`) stays as built.
  The opening Luck check from `Combat.md` § Cooldowns is its own queue row.
- Attacks on the same tick resolving at once, and the 30/5 bar charge. Each is its own row.
- Whether a special gets a Luck reset check. It stays at none, per `EhrensDocs/Combat.md`.
- Showing a bag, or a chance to evade, anywhere on screen. Nothing shows one today.
- Luck outside combat: crafting, and what the Alchemist brews.

## Open Questions

- When the Archer hits the same enemy twice in a row, its later shots already get up to 10%
  more damage. Now that a dodge is a lucky draw from the target's bag rather than a
  percentage, should the streak (A) only raise damage, (B) also give each streak shot a
  2–10% chance to hit anyway when the target draws a dodge, or (C) make the shot impossible
  to dodge once the streak reaches its cap? *(queue #127, `127-archer-accuracy-vs-luck-bag.md`)*
- "The first four strikes always land" — does that mean the flurry can't miss, or only that
  four strikes always happen? *(`EhrensDocs/Individual Types.md`, "Questions on the flurry"; B5
  builds its default)*
- *Proposal, this PRD's:* does a new character's first bag start full, filled from its
  Luck when it is made (A5)?
- *Proposal, this PRD's:* does a save from before the bag load each member, and each monster
  in a saved battle, with a full bag filled from current Luck (A8)?
- *Proposal, this PRD's:* is a saved bag that can't be true fixed by refilling it as it
  loads, or is the save refused (A9)?
- *Proposal, this PRD's:* when an attack ends the battle, is the reset pull skipped so no
  token is spent (B2)?
- *Proposal, this PRD's:* is the flurry's pull made as the flurry begins, and so spent even
  if the fight ends within the first four strikes (B6), or only after the fourth strike, and
  not at all once the fight is over?
