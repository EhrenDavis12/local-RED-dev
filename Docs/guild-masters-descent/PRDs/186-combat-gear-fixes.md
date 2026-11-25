# PRD: Combat and gear fixes to match the originals (#186)

> **Status:** Draft · Source docs read: `Combat.md`, `Individual Types.md`, `Guild Members.md`,
> `Equipment.md`, `Battle Test.md`, `Core Concept.md`, `Specialists.md`, `The Dungeon.md`,
> and the EhrensDocs change notes against each, plus `EhrensDocs/Open Questions.md`;
> background in `queue/reports/184-original-docs-review.md` and
> `queue/reports/198-original-docs-24-nov.md`.

## Problem

The game was built to EhrensDocs rules that the other developer's docs have since replaced.
Under the user's 18 Nov rule the originals win, so today the game gets these wrong: a Rogue
evades with one token, targets are weighted by damage dealt and missing health, a Brute has
the same health as everyone else, light armour and the bow use old bands, a Brute halves a
Tank's defence, Shields Up is a flat +3 that stacks on a re-cast, and a piece's range is
0–4 points wide at every class.

## Goal

Combat and gear math match the originals on these eight rules, on both sides of a fight,
with each rule pinned by an EditMode test. Nothing else about combat changes.

## Requirements

Every rule applies to party members and monsters alike: enemies are built from the same six
types, working the same way (Combat, Enemies; Combat, Targeting).

### Evasion

1. Wherever a strike makes its target pull an evasion token, a Rogue target pulls up to two:
   the second only when the first is False, and either True evades. This holds against
   every attacker, not only an Archer, and for each strike on its own, since every strike
   rolls to hit separately. (Combat, Luck Checks; Individual Types, The Rogue; Combat,
   Attacks and Reach.)
2. Where no token is pulled at all, a Rogue pulls none either: an area attack, a vanished
   Rogue's own strikes, and the Archer's capped-streak shot. (Combat, Luck Checks;
   Individual Types, The Rogue; EhrensDocs Individual Types, "Volley and the Archer's
   streak, for now".)
3. A strike evaded on the second token is an evaded strike in every way, including the
   Rogue's bonus charge, which still pays once per strike evaded. (Individual Types, The
   Rogue; EhrensDocs Individual Types, "The Rogue's bonus pays per strike evaded, for now".)

### Targeting

4. One rule picks the target for every attack that picks one, on both sides, specials and
   specialists included. A taunt, and the party's focus target, still make that target a
   100% pick exactly as they do today. (Combat, Targeting; Combat, Specialists in Combat.)
5. The candidates are what the attack's range reaches, unchanged from today: the first
   occupied row at close range, every row at far range, a vanished Rogue passed over unless
   it is all there is. (Combat, Attacks and Reach; Individual Types, The Rogue.)
6. 20 of the 100 go to the candidate with the least health left, counted in current health
   points. When several tie for least, the 20 are split evenly between them. (Combat,
   Targeting; the tie split is the user's going-ahead default on queue item #186,
   2026-11-24.)
7. At close range the other 80 are split evenly among all candidates, the least-health one
   included. Five in a front line with distinct health: the weakest 36%, each other 16%;
   with two tied for least: 26%, 26%, 16%, 16%, 16%. (Combat, Targeting.)
8. At far range the 80 are given to rows first, then split evenly among the candidates in
   each row. A row's weight is set by its position: each row counts double the row
   directly in front of it, whether or not that row has anyone in it, and an empty row gets
   none of the 80. Worked: two in the front row, one in the row behind, the weakest in
   front — weakest 33⅓%, the other front one 13⅓%, the back one 53⅓%. With the middle row
   empty, the back row counts four times the front. (Combat, Targeting; picking the row
   first, and weighting by position across an empty row, are the user's going-ahead
   defaults on #186, 2026-11-24.)
9. Each chance is the exact figure the rule gives, not rounded to a whole percent, and the
   chances add up to 100. Damage dealt this battle and health missing play no part; the
   `TargetDamageWeight` and `TargetKillWeight` placeholders go. (Combat, Targeting.)

### Health

10. Maximum health is Constitution × 12 for a Brute and × 10 for every other type,
    specialists included. A monster Brute is × 12 too: Battle Test's enemy Brute, at
    Constitution 7, has 84. (Guild Members, Base Stats; Battle Test, The Enemy Team.)
11. A level-up that raises a Brute's Constitution raises its maximum and current health by
    12 a point. (Guild Members, Base Stats, "it grows as Constitution grows"; EhrensDocs
    Guild Members, "Health counts a member's own Constitution, and what's taken stays
    taken, for now".)
12. Maximum health is always worked out from Constitution, never read from a saved figure,
    so a Brute from a save made before this change loads, and promotes, at × 12. (Guild
    Members, Base Stats.)

### Gear bands

13. The Fighter's light armour has an F-class Defence band of 5–16, doubling each class
    above like every band. (Equipment, Quality.)
14. The bow's Durability band is 80–160 at every class, with the knife and the two-handed
    sword; the war hammer alone stays 40–80. (Equipment, Quality.)
15. A piece already made keeps its rolled range and durability. The new bands and the span
    rule below apply only to pieces made from now on. (Equipment, Quality: "rolled once, at
    creation, and fixed for the life of that piece".)

### Range span

16. Every newly made weapon, armour and shield range has a span no narrower than a quarter
    of its band and no wider than half of it, at every class, and sits inside its band. No
    piece is a single flat figure and none spans its whole band. The
    `RangeWidthMin`/`RangeWidthMax` placeholders go. (Equipment, Quality; shields:
    EhrensDocs Equipment, "The Tank carries a shield", "built the way armour is".)
17. A span and a band are both measured by how many whole figures they cover, ends
    included: 2–4 covers 3, and the knife's F band of 2–12 covers 11, so an F knife covers
    3 to 5 figures (2–4 at its narrowest, 2–6 at its widest). That is the only measure under which Equipment's
    own example, an F knife coming out 2–4 or 10–12, satisfies the rule. (Equipment,
    Quality.)

### Brute against Tank

18. A Brute's strike that lands on a Tank — the chosen target, a cleave neighbour, or one in
    the special's rows — uses a quarter of that Tank's defence, where today it uses half.
    The quarter is of the Tank's whole defence: Constitution, armour, shield and any Shields
    Up on him. It is not rounded; the hit rounds down once, at the end. (Individual Types,
    The Brute and The Tank; EhrensDocs Equipment, "The Tank carries a shield"; EhrensDocs
    Guild Members, "A hit rounds down once, at the end, for now".)

### Shields Up

19. Shields Up's figure is set once, when it is cast: the Tank's Constitution, with help,
    plus one roll of his armour. His shield piece is not in it, and nor is any Shields Up
    already standing on him, his own or another Tank's. Armour that is broken or not worn
    adds nothing to the roll, and the roll is not a hit, so it wears nothing. (Individual
    Types, The Tank; Equipment, Durability; the figure's make-up is the user's going-ahead
    default on #186, 2026-11-24.)
20. That figure holds unchanged for the whole length, for the Tank and for every ally who
    has it: his armour breaking, or his help changing, while it lasts does not move it.
    (User default on #186, 2026-11-24.)
21. While it is up, the figure is added to the Tank's own defence, doubling it, and to each
    ally behind him in his column — the allies who stand there when it is cast, as today.
    The flat `ShieldsUpDefence` placeholder goes. (Individual Types, The Tank; EhrensDocs
    Individual Types, "The Tank's taunt, Shields Up and bonus, for now".)
22. Casting it again while his own is still up replaces it rather than stacking: a fresh
    figure by requirement 19, and a fresh length of three of his cycles. Each ally behind
    him at the re-cast gets the same refresh in place of their old share. An ally who held
    his last share but no longer stands behind him keeps that old share until it runs out
    its own length. (Individual Types, The Tank; the allies' refresh, and the moved ally
    keeping theirs, are the user's going-ahead defaults on #186, 2026-11-24.)
23. Two Tanks' Shields Up still add in full on an ally behind both, and one Tank's re-cast
    never touches another Tank's. (Individual Types, The Tank.)
24. Worked: a Tank at Constitution 8, no help, with no armour or shield casts it — his
    defence is 16 and the ally behind him gains 8; a re-cast leaves him at 16, not 24. With
    full armour he rolls once at the cast, say 12, and the figure is 20 for the whole
    length, added on top of the armour he rolls on each strike against him.
    (Requirements 19–22.)

Existing EditMode tests that assert the old figures — one token for a Rogue, the weighted
target draw, × 10 for a Brute, the old light armour and bow bands, the half, the flat +3
and stacking, the 0–4 width — are superseded by these requirements and are
`forge-test-author`'s to rewrite.

## Out of Scope

- Specials firing by themselves (#185), healing at home (#187), floor power budgets (#188),
  monster gear (#166), the Battle Test fixture (#167).
- The crafter's Luck raise on a span, and field repair: neither crafting nor field repair is
  built.
- Whether support-ring help reaches the Tank's health (an open question in Battle Test).
- Showing target chances, spans or the Shields Up figure anywhere on screen.

## Open Questions

- **From `Combat.md`, verbatim:** For a far-range attacker, each row further back counts
  double when the eighty is shared out. Is that the right weight, and should it hold the
  same way on a grid three rows deep as it does on the five-wide one? (Built as stated in
  Targeting until answered.)
