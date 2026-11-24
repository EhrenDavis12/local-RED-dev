# PRD: Specials fire on a full bar

> **Status:** Draft, queue item #185 · Source docs read: `Combat.md`, `Individual Types.md`,
> `Equipment.md` (Durability); `EhrensDocs/Combat.md`, `EhrensDocs/Individual Types.md`,
> `EhrensDocs/Platform.md`, `EhrensDocs/Open Questions.md`; `queue/focus.md`;
> `queue/reports/184-original-docs-review.md`. Searched the rest of the originals and
> EhrensDocs for specials and bars; nothing else bears on this.

## Problem

Today a full bar does nothing on its own. The player arms it by pressing the member's skill
plate, or Auto arms it, and the special then replaces that member's next ordinary attack
(`Battle.cs` `Resolve`, `BattleController.cs` `UseSpecial`). A monster's full bar also
waits for its next cooldown and replaces that attack. The originals now say a special goes
off on its own the moment the bar fills, for both sides, and costs no attack. The game
is wrong on both counts (`queue/reports/184-original-docs-review.md`, "Where the game is
now wrong").

## Goal

A full bar fires its special straight away, for party members and monsters alike. Nobody
arms it and it never costs an attack. Within our one rule that no two attacks land at once,
it goes off right after the attack that filled it, which can be someone else's attack when
a bonus filled it. The skill plates stay on the battle screen as read-only charge displays.
Nothing the player or Auto does can start, hold or cancel a special.

## Requirements

### When a special fires

1. A special fires by itself as soon as its holder's bar is full (100). This holds for
   party members and monsters alike. A full bar never waits for the holder's next
   cooldown. One consequence: a Brute's special fires even when no enemy row stands
   behind the front one. It hits nothing and empties the bar, as the sweep with no row
   behind it does today. The player can no longer hold it for a better moment. —
   `Combat.md`, The Special Bar, ¶1; `Individual Types.md`, The Brute ("or whatever rows
   remain if there are fewer").
2. When the holder's own attack fills the bar, the special goes off once that attack has
   finished resolving (every strike of it), and before any other combatant's attack due on
   that tick. The order against the holder's own free attack is Open Question 2. —
   `Combat.md`, The Special Bar, ¶1 ("goes off once the attack that filled it has finished
   resolving").
3. When a bonus condition fills the bar during an attack that isn't the holder's (being hit,
   an ally taking a hit, evading), the special fires in the middle of that attack. It goes
   after the hit that filled the bar has resolved and before that attack's next strike or
   next target. The rest of the attack then resolves against the fight as the special left
   it. Example: a Fighter's first strike fills a Tank's bar, Shields Up goes up, and the
   Fighter's second strike meets the shielded defence. If the special has to wait
   (requirement 14), the interrupted attack carries on without it, and the special goes
   once its wait ends. The engine therefore has to be able to break an attack open between
   its hits. — `Combat.md`, The Special Bar, ¶1 ("a bar that fills that way fires right
   then, in the middle of whichever attack filled it").
4. A bar can be filled by a special's hits as well as by an ordinary attack's. Such a bar
   fires by the same rule, so one special can set off another. — `Combat.md`, The Special
   Bar, ¶1 ("the special fires the moment that bar is full"; "The attack that fills a bar
   need not be the holder's own").

### What a special costs

5. A special takes no action. The holder's cooldown is not touched by it: the wait already
   running carries on, and it is neither restarted nor used up. A combatant whose cooldown
   comes up always makes its ordinary attack (or its ordered drink), never a special in
   its place. — `Combat.md`, The Special Bar, ¶1 ("it takes no action of its own, so a
   member doesn't give up an attack to use it").
6. The ordinary attack that filled the bar still gets its Luck reset check, as every
   attack does. The special itself gets no Luck check, so it never earns a free attack. —
   `Combat.md`, Luck Checks, ¶1; `EhrensDocs/Combat.md`, "The free attack comes first, and
   a special gets no check, for now".
7. A free attack is always the type's ordinary attack. It charges the bar like any attack,
   and a bar it fills fires by requirement 2. — `Combat.md`, Luck Checks, ¶1;
   `EhrensDocs/Combat.md`, "The free attack comes first, and a special gets no check, for
   now".
8. Firing empties the bar to 0, and it charges from there. Charge earned while the bar is
   already full, such as the later strikes of the attack that filled it, is not carried
   over to the next bar. — `Combat.md`, The Special Bar ("The bar is full at 100";
   "Firing the special empties the bar, and it charges again from there").
9. A special still puts nothing into its own holder's bar. The one exception is the
   Fighter's flurry, which refills the bar to 90% when it kills. — `Individual Types.md`,
   The Fighter; `EhrensDocs/Combat.md`, "A special puts nothing in its owner's bar, for
   now".
10. Firing a special is not one of its holder's cooldown cycles. A lasting effect it casts
    starts counting at the holder's next cooldown and lasts three of them. — `Combat.md`,
    Lasting Effects, ¶1; `EhrensDocs/Combat.md`, "When an effect's count starts, and a
    second cast stacking".
11. A holder standing in a Mage's field takes the field's hit as its special begins. If
    that hit kills it, the special does not happen. — `Individual Types.md`, The Mage, ¶2;
    `EhrensDocs/Individual Types.md`, "Where the Mage's field lies, and what it does, for
    now" ("a special counts as beginning an attack").
12. Specials and drink orders no longer affect each other. Ordering a drink takes back no
    special, and a special firing takes back no drink order. — `Combat.md`, The Special
    Bar, ¶1 (a special takes no action, so it is not an order); the user's call given with
    queue item #185 (arming removed).

### Our one rule: one at a time, target in place

13. A special never resolves at the same moment as any other attack, hit or special. It
    takes its own turn, and that includes a special that interrupts an attack under
    requirement 3. — `queue/focus.md`, "The one rule of ours that beats the new docs";
    `EhrensDocs/Combat.md`, "Attacks on the same tick go in turn".
14. A close-range special (the Brute's sweep, the Fighter's flurry) waits until its target
    is back in its own spot. It waits on the same terms as a close-range ordinary attack:
    it keeps its target, and it picks again only if that target dies, goes out of reach or
    vanishes. A far-range special (Volley, the Mage's field) does not wait: it hits its
    target where it is, the way a far-range ordinary attack does. That is the cheap default,
    and the coordinator is putting it to the user as a going-ahead question. Vanish and
    Shields Up have no target, so they never wait. What happens when the holder is the one
    still out is Open Question 1. — `queue/focus.md`, the one rule;
    `EhrensDocs/Combat.md`, "A close-range attack waits for its target to be home" ("Only
    close-range fighters wait. An Archer or a Mage shoots its target where it is").
15. The fight decides every wait, not the screen. A special is drawn when the fight
    resolves it, so a drawn fight at any speed and a fight with nothing drawn fire the
    same specials on the same ticks. — `EhrensDocs/Combat.md`, "A close-range attack waits
    for its target to be home" ("worked out by the fight itself, from the same walk the
    battle screen draws"); "The clock, and a multi-strike attack landing in one tick".
16. If a special's holder dies before the special fires, the special is lost. If the
    battle ends first, the special does not fire. A battle ends the moment one side has no
    one standing. — `EhrensDocs/Combat.md`, "Attacks on the same tick go in turn" ("a
    combatant killed earlier in the tick never makes its attack"; "The battle ends as soon
    as one side has no one left standing, even partway through a tick").

### Saving

17. A special that is due or waiting when the game saves is held by the save. After
    loading it fires exactly as it would have without the save: same tick, same order,
    same rolls. It is fight state, not a player's order, so the rule that drops unused
    orders does not apply to it. — `EhrensDocs/Platform.md`, Saving, ¶3.

### The battle screen and Auto

18. The arming path is removed. The player has no way to order, arm, hold or take back a
    special. Each member's skill plate stays and shows how full that member's bar is.
    Pressing a plate orders nothing. Whether a press still selects the member is Open
    Question 5. — the user's call given with queue item #185; `EhrensDocs/Combat.md`,
    "Drinking a potion…" (the skill buttons and the drink button under each).
19. No "armed" or "ordered special" state is drawn anywhere, on a plate or on a bar. —
    the user's call given with queue item #185.
20. Auto no longer does anything with specials. Its drink ordering is unchanged. — the
    user's call given with queue item #185; `EhrensDocs/Combat.md`, "Drinking a potion…"
    (the Auto bullet).

## Out of Scope

- What each special does, how much a bar charges, and each type's bonus condition. Those
  are already built, and the changes the originals made to them are queue item #186.
- How a plate or a bar looks, including the full-bar colour and the special's animation.
  That is the look path: build it and look at it.
- The drink button, potion rules, and how Auto decides to drink.
- Weapon and armour wear from specials (`Equipment.md`, Durability), which is unchanged.

## Open Questions

Each proposal below is the PRD author's own, not something the docs settle.

1. **The holder is still out.** When a Fighter's or a Brute's own attack fills its bar,
   the fighter is still standing at its target. Does it walk home first and then walk out
   again for the special, or go straight into the special from where it stands?
   *Proposal:* walk home first, as a free attack does (`EhrensDocs/Combat.md`, "A
   close-range attack waits…").
2. **Special or free attack first.** One attack can both fill the bar and win the Luck
   reset. Combat says the special goes off once that attack has resolved. Our change note
   says the free attack comes "straight after the attack that earned it". Which goes
   first? *Proposal:* the special, since the originals win.
3. **Several bars fill on one attack.** One attack can fill more than one bar, such as a
   Volley landing on an enemy Tank and a Rogue. In what order do the specials go?
   *Proposal:* the order attacks on one tick already use: the higher Dexterity first,
   then a draw.
4. **A bar left full when the battle ends.** A bar filled by the attack that ends the
   battle is never fired. It carries to the floor's next battle (`Combat.md`, The Special
   Bar), and a saved bar can load full too. When does a full bar fire in a new battle?
   *Proposal:* as the fight begins, after the opening Luck checks and before the first
   attack.
5. **Pressing a plate.** Today pressing a member's plate also selects them, so the next
   tap on the grid moves them. Should a press still select the member, or should the plate
   do nothing at all? (Cheap to change.)
6. From `EhrensDocs/Combat.md`, still open: "When a taunted member or enemy uses a special
   that hits its own choice of targets rather than one it aims at, is the taunt spent?"
7. From `EhrensDocs/Combat.md`, still open (requirement 6 uses its default): "Is a special
   an attack for the Luck reset — does it get a check?"
8. From `EhrensDocs/Individual Types.md`, still open (requirement 11 uses its default):
    "Does a special count as beginning an attack for the field, including one that strikes
    no one, like Vanish or Shields Up?"
