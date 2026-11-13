# PRD: Experience by Enemy Rank, Three-Stat Level-Ups, and the Experience Cost of a Rank

> **Status:** Draft, 2026-11-13, queue item #56 · Source docs read: `Guild Members.md`,
> `Combat.md`, `The Dungeon.md`, `Specialists.md`, `Individual Types.md`, `Core Concept.md`,
> `Equipment.md`; change notes `EhrensDocs/Guild Members.md`, `EhrensDocs/The Dungeon.md`,
> `EhrensDocs/Combat.md`, `EhrensDocs/Specialists.md`, `EhrensDocs/Individual Types.md`,
> `EhrensDocs/Core Concept.md`, `EhrensDocs/Platform.md`, `EhrensDocs/Equipment.md`;
> `queue/focus.md`; background `queue/reports/60-rank-experience-and-levels.md`,
> `queue/reports/48-reconcile-ehrensdocs.md` (rule 11). Where an original and a change note
> disagree, the original wins (`queue/focus.md` → Goal, "The original docs win").

## Problem

Today every monster is worth 1 experience whatever its rank, and the experience is handed
out once per floor, not per combat. A level costs a flat 2 experience, so F to E takes 30
rather than the 20 the docs give, and a level-up raises one stat instead of three. The
level threshold and the rank's experience cost are two unrelated numbers.

## Goal

A combat pays experience by the rank of each enemy killed in it, shared among the members
still standing when it ends. Experience fills one bar per rank: the rank's experience cost is
exactly what takes a member from level 1 to the rank's level threshold, and each level-up
raises three different stats by one. The first promotion, F to E, is the only one reachable
in this version, but levelling inside any rank follows that rank's own cost and threshold.

## Requirements

### Experience from a combat

1. **Worth by rank.** When a combat ends, its experience is the sum, over every enemy killed
   in it, of that enemy's worth by its own rank: F 1, E 3, D 6, C 12, B 24, A 48, S 96,
   SS 192, SSS 384. These are the docs' numbers, not placeholders. *(Guild Members.md →
   Levels and Experience.)* In this version every monster is F (an F dungeon fields its own
   rank, and there is no grade below F), so only F's worth is reachable; the table still
   carries all nine. *(Combat.md → Enemies; EhrensDocs/The Dungeon.md → "The dungeon's
   enemies are monsters".)*

2. **Per combat, not per floor.** Experience is added up and shared at the end of each
   combat — each battle on a floor — not once when the floor is cleared. A level-up it causes
   takes effect before the next combat starts. *(Guild Members.md → Levels and Experience:
   "added up at the end of a combat".)* This replaces the built per-floor award.

   **A stand-off — a queue default for now, not the user's word.** A combat that ends in a
   stand-off still pays the experience for the enemies killed in it before it ended, shared
   by requirement 3, before the party turns back. *(The docs tie experience to kills and to
   the end of a combat, not to winning it — Guild Members.md → Levels and Experience; the
   stand-off itself is EhrensDocs/Combat.md's.)*

3. **Who shares it — a default for now, not the user's word.** The total is divided equally
   between the party members still alive when that combat ends, specialists counted. A
   member who died in that combat, or earlier, gets no share of it. *(Guild Members.md →
   Levels and Experience, narrowed by EhrensDocs/Guild Members.md → "Who shares a combat's
   experience, for now"; applied as a queue default, #48 Q2.)* The question stays open; see
   Open Questions.

4. **An equal division loses nothing.** Each sharer gets exactly the total ÷ the number
   sharing; no share is rounded, so the shares always add back up to the total. *(Guild
   Members.md → Levels and Experience, "divided equally"; the built game holds shares
   exactly, and the docs say nothing about fractions — flagged in the hand-back.)*

5. **Before the floor heal.** On a floor's last combat, its experience is shared and its
   level-ups applied before the floor's heal (or rest-area heal) is worked out, so a heal is
   a share of the maximum health after the level-up. *(EhrensDocs/The Dungeon.md → the
   healing change, "once the floor's experience is shared, so a level-up on that floor
   counts".)*

### Experience is the bar, level is the number

6. **One bar per rank.** A member holds one experience amount: what they have earned in
   their current rank or tier. There is no second counter. *(EhrensDocs/Guild Members.md →
   "Experience is the bar, level is the number".)*

7. **A rank's cost and threshold.** Each rung's level threshold and experience cost are:

   | Crossing | Threshold | Cost |
   |---|---|---|
   | F → E | 16 | 20 |
   | E → D | 32 | 100 |
   | D → C | 64 | 500 |
   | C → B | 128 | 2,500 |
   | B → A | 256 | 12,500 |
   | A → S | 512 | 62,500 |
   | S → SS | 1,024 | 312,500 |
   | SS → SSS | 2,048 | 1,562,500 |

   These are the docs' numbers, not placeholders. *(Guild Members.md → Promotion.)* A
   specialist's tiers use the same rows rung for rung, Novice where F sits. *(Guild
   Members.md → Promotion: "The same eight thresholds serve both ladders"; Specialists.md →
   Tiers: "Promoting a specialist works exactly the way a diver's rank up does", and the
   ladders "line up rung for rung".)*

8. **When a level is reached — a placeholder.** Level N of a rank is reached once the
   experience earned in that rank is at least ceil(cost × (N−1) ÷ (threshold−1)). For F to E
   that puts levels 2 through 16 at 2, 3, 4, 6, 7, 8, 10, 11, 12, 14, 15, 16, 18, 19, 20.
   Reaching the threshold and having earned the rank's whole cost happen at the same moment.
   *(EhrensDocs/Guild Members.md → "Experience is the bar, level is the number".)* How the
   cost is cut into single levels is a placeholder, cheap to change: it lives in the tuning
   file, is marked as a placeholder there, and appears in the placeholder list.

9. **Every rank levels by its own row.** A member levels inside whatever rank or tier they
   hold by that rung's cost and threshold — an E-rank member climbs from level 1 to 32 on
   E → D's 100 — even though promoting past E is not in this version. *(Guild Members.md →
   Promotion; `queue/focus.md` → Not included keeps only the promotion past F → E out.)*

10. **Several levels at once.** One share that crosses several levels gives each level its
    own level-up (requirement 12), in order. *(Guild Members.md → Levels and Experience: "A
    level-up raises three of a member's base stats".)*

11. **Capped at the threshold.** A member at their rank's threshold gains no more levels and
    no more experience: whatever they would have earned past the rank's cost is gone, not
    banked. At the cap the stored experience is exactly the rank's full cost — 20 for an
    F-rank member at level 16 — and stays there until promotion. *(Guild Members.md →
    Promotion: "stops gaining levels … neglecting a promotion wastes the experience";
    EhrensDocs/Guild Members.md → "Experience is the bar, level is the number".)*

12. **Promotion.** The promotion check stays the level threshold and the gold, both required;
    there is no separate experience check, because the threshold and the cost are reached
    together (requirement 8). Promotion sets the level to 1 and the experience earned in the
    new rank to nothing; the stats are kept. *(Guild Members.md → Promotion;
    EhrensDocs/Guild Members.md → "Experience is the bar, level is the number".)*

### Level-ups

13. **Three different stats, one point each.** A level-up raises three different base stats
    by exactly one each — never the same stat twice in one level-up — chosen by the
    member's type's ordering in Stat Weighting by Type, most likely through least likely. The
    one point is the docs' rule, not a tuning figure. *(Guild Members.md → Levels and
    Experience; Stat Weighting by Type.)*

    **How the three are drawn — a queue default for now, not the user's word.** Three
    weighted draws in a row, each from the stats not yet drawn in this level-up, weighted by
    each stat's position in the type's ordering using the placeholder level-up weights
    (requirement 17). The docs say only "chosen by the type's weighting, most likely through
    least likely".

14. **Specialists level the same way**, each by its own type's ordering — the Cook's and the
    Porter's in this version. *(Guild Members.md → Levels and Experience: "Specialists gain
    base stats the same way divers do"; Stat Weighting by Type.)*

15. **Constitution raises health with it.** A level-up that raises Constitution raises both
    maximum and current health by ten, so damage already taken stays taken. *(Guild
    Members.md → Base Stats; EhrensDocs/Guild Members.md → "Health counts a member's own
    Constitution, and what's taken stays taken, for now".)* Built already; it must survive
    the change to three stats.

16. **Monsters use the same level-up.** A monster above level 1 gets its stats from its
    type's starting stats plus the same three-stat level-ups, one per level past 1.
    *(EhrensDocs/The Dungeon.md → "The dungeon's enemies are monsters": "uses the same stat
    rules".)* Every dungeon monster is level 1 in this version, so this only matters where a
    higher level is set.

### Placeholders this feature owns

17. The tuning file carries, marked as placeholders and listed: the rule that cuts a rank's
    cost into levels (requirement 8), and the level-up weights by position in a type's
    ordering (already there). The flat experience-per-level placeholder is retired. The
    worth by rank, the costs, the thresholds and the one point per stat are the docs'
    numbers and are not marked as placeholders. *(`queue/focus.md` → Goal, "Missing
    details".)*

### Saves

18. **Older saves — a queue default for now, not the user's word.** The save format version
    goes from 6 to 7, since a member's stored experience now means experience earned in the
    rank (requirement 6) rather than progress toward the next level. A save older than 7
    loads each member with their level and stats kept and their experience set to where
    that level starts under requirement 8 (an F-rank member at level 5 loads with 6; at
    level 1, with nothing). In a version 6 save taken mid-floor, the battles already won on
    that floor have unpaid experience — the old game paid only on clearing the floor — and
    that experience is lost on load. *(No doc covers saves across this change; the game has
    no players yet, so this is cheap.)*

## Out of Scope

- Promotion past F → E, and anything about its gold price — unchanged. *(`queue/focus.md` →
  Not included.)*
- Whether an injured member can be promoted — open in EhrensDocs/Guild Members.md, and this
  feature leaves the built behaviour alone.
- Training missions and timed missions. *(`queue/focus.md` → Not included.)*
- A specialist's specialty improving with level or tier; the Cook heals the same at every
  level for now. *(EhrensDocs/Specialists.md.)*
- Rebalancing how many fights a rank takes (an open question in the originals).
- Experience from anything other than combat kills.
- Layout of the member sheet and roster; what the bar shows is a question below, its look
  is built and looked at.

## Open Questions

From the design docs, worded as they word them:

- In "divided equally between all party members", which members count: the ones who
  started the combat or the ones still alive? *(EhrensDocs/Guild Members.md. Built for now
  as the ones still alive — requirement 3.)*
- When a level-up uses up experience, does the leftover carry toward the next level?
  *(EhrensDocs/Guild Members.md. Requirement 8's one bar carries it by construction — the
  bar is never spent, only read — so this reads as answered by the bar, but it still sits
  open; flagged in the hand-back.)*
- The experience a rank costs multiplies by five each step while what a kill is worth
  doubles, so every rank takes about two and a half times the fights of the one before — at
  around six enemies a fight and a party of six, F to E is about twenty fights and SS to SSS
  about eight thousand, roughly thirteen and a half thousand for the whole climb. Which side
  gets tuned, the cost of a rank or what a stronger enemy is worth? *(Guild Members.md.)*
- How the cost is cut into single levels isn't settled; the even spread, rounded up, is a
  placeholder for now. *(EhrensDocs/Guild Members.md → "Experience is the bar, level is the
  number", Why.)*

Raised by this PRD — the docs don't answer it:

- **What the bar shows.** The member sheet shows one bar. Does it fill toward the next
  level, or across the whole rank toward the threshold? *Doesn't block the rules; cheap to
  change.*
