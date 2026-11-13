# PRD: Damage math by the originals

> **Status:** Draft, queue item #51 · Source docs read: `Guild Members.md`, `Individual
> Types.md`, `Combat.md`, `Equipment.md`, `The Dungeon.md`, `Core Concept.md`,
> `Specialists.md`, and every change note under `EhrensDocs/`. Gap from
> `queue/reports/48-reconcile-ehrensdocs.md` rows 7, 8, 9 and part of 13; placeholder rules
> from `queue/reports/62-damage-math-open-rules.md`. Engine read on `queue/51-damage-math`.
> Where the originals and EhrensDocs disagree, the originals win (Focus, "The original docs
> win").

## Problem

The engine's hit math is the pre-cooldown version. A hit is attack minus defence. Area attacks
take half of defence. A type advantage doubles the damage, in both triangles. A Brute ignores
a Tank's defence completely. The Fighter's ordinary attack is four strikes at a quarter of
its damage each, the Rogue's two strikes are at half, and the flurry is always six strikes.
Every hit wears the attacker's weapon, specials included. The Mage's field ignores defence.
The originals reject each of these rules, so every number a battle shows today is wrong.

## Goal

Every hit in a battle works out the way the originals say. Defence reduces damage by a ratio
that depends on the attacker's rank. Type advantages in the first triangle work by changing
defence. Every strike carries the attacker's full damage. The flurry runs four to six strikes,
and specials leave the attacker's weapon untouched. The three rules the docs leave open are
built as marked placeholders, each easy to change.

## Requirements

### The hit

1. **The ratio.** A strike that lands deals *(damage stat + weapon roll) × K ÷ (K +
   Defence)*. Defence is the target's own defence when the strike resolves: Constitution,
   plus the armour roll, plus any Shields Up bonus it holds. This replaces *attack −
   defence*. — `Guild Members.md` § Base Stats; `Individual Types.md` § The Tank ("increases
   the Tank's own defence").
2. **K comes from the attacker's rank.** F 20, E 40, D 80, C 160, B 320, A 640, S 1,280,
   SS 2,560, SSS 5,120. These numbers are settled, not placeholders. A diver uses its own
   rank (rung 0 is F, rung 1 is E). — `Guild Members.md` § Base Stats, § Promotion.
3. **A monster's K comes from its rank.** For now every monster is F rank. The only dungeon is
   F rank, and an F dungeon cannot field anything else, because nothing ranks below F.
   Choosing between a dungeon's own rank and the rank below it belongs to the
   enemies-by-dungeon-rank item, not this one. — `Combat.md` § Enemies.
4. **A specialist's K is a placeholder (PLACEHOLDER, pending the user).** A specialist has a
   tier, not a rank, and no doc gives a tier a K. Each tier gets a K from a table in the
   tuning file. The default gives tier *n* the K of rank *n* (Novice 20, Apprentice 40, and so
   on). — `Guild Members.md` § Promotion (specialists climb tiers, not ranks); see Open
   Questions.
5. **Area attacks use two-thirds of defence.** Every attack the engine treats as area uses
   exactly two-thirds of the target's defence: the Mage's column, Volley, and the Mage's field
   (R10). This replaces the factor of one half. Two-thirds is settled, not a placeholder. —
   `Guild Members.md` § Base Stats.
6. **Rounding (PLACEHOLDER, pending the user).** A hit's damage is worked out exactly. It is
   rounded **down once, at the end of the hit**, after every factor: the ratio, the Volley
   neighbour share, and the Archer's streak. No step rounds along the way. There is no minimum
   damage, so a hit can do 0. A 0-damage hit still counts as a hit for wear. — Placeholder
   from report 62 §1; "no minimum damage" from `Guild Members.md` § Base Stats; the wear rule
   from the EhrensDocs `Equipment.md` change "A hit that does nothing still wears gear".

### Type advantages

7. **No damage multiplier.** A type advantage no longer multiplies damage, in either
   triangle. In the second triangle (Rogue over Archer, Archer over Mage, Mage over Rogue) the
   advantage comes only from existing evasion and area rules, which this PRD leaves alone. —
   `Guild Members.md` § Combat Types.
8. **The first triangle works through defence.** The target's defence (R1) is changed before
   the ratio is worked out:
   - a Brute's strike on a Tank uses **half** the Tank's defence, on both the cleave and the
     special. This replaces "ignores the Tank's defence".
   - a Fighter's strike on a Brute uses **half** the Brute's defence.
   - a Fighter's strike on a Tank uses **double** the Tank's defence. This is the Tank's
     advantage, and it acts when the *Fighter attacks*. Today's multiplier acts when the
     Tank attacks. When the Tank strikes a Fighter, nothing is changed.

   These apply between members and monsters alike. — `Individual Types.md` § The Brute,
   § The Tank; `The Dungeon.md` EhrensDocs change (monsters have their type's advantages).

### Strikes

9. **Each strike carries the full damage.** Each strike carries the attacker's full damage
   stat and its own fresh weapon roll. The defender's armour is rolled fresh for each strike
   too. No type splits its damage across strikes. — `Equipment.md` § Quality (the
   per-strike paragraph); `Combat.md` § Attacks and Reach.
10. **The Fighter's ordinary attack is 2 strikes.** It was 4. The count is settled, not a
    placeholder. — `Individual Types.md` § The Fighter.
11. **The Rogue's two strikes each carry full damage.** They were at half. —
    `Equipment.md` § Quality; report 48 row 9.
12. **The flurry is 4 strikes, plus up to 2 more on Luck checks.** It was always 6. Each
    flurry strike follows R9, with no share of its own. The rules for carrying on to another
    target and for refilling the bar are unchanged. — `Individual Types.md` § The Fighter.
13. **The flurry's Luck checks (PLACEHOLDER, pending the user).** The fifth and sixth
    strikes each need a Luck check of the flurry's own, separate from the Luck reset. The
    chance is *50% × Luck ÷ (Luck + 20)*, using the Fighter's Luck. The ceiling of 50% and
    the 20 are placeholders in the tuning file. The sixth strike's check is made only if the
    fifth strike's check succeeded, whether that strike then hit or missed. — Report 62 §3.
    Each check is an exact integer comparison, in the same way the Luck reset's is
    (`Battle.cs:376`, `NextInt(0, 4 × (Luck + 60)) < Luck`). With a ceiling of *p* percent
    and a constant *k*, the check succeeds when `NextInt(0, 100 × (Luck + k)) < p × Luck`; at
    the placeholders that is `NextInt(0, 100 × (Luck + 20)) < 50 × Luck`. Like the reset, the
    check is drawn even at Luck 0. — Main loop, settling a note from `forge-prd-reviewer`.

### The Mage's field

14. **The field is an area attack (PLACEHOLDER, pending the user).** Each time the field
    deals damage, the hit can't miss. It pays two-thirds of the victim's defence (R5), worked
    with the Mage's K. Today it ignores defence. — Report 62 §2.
15. **When the field's damage is set and rounded.** The field's damage before defence is
    still fixed once, at cast: the share times (the Mage's Intelligence, with help, plus one
    staff roll), as the code works it out now. Under R6 that figure is not rounded at cast.
    Each field hit rounds once, after defence. — The EhrensDocs `Individual Types.md` change
    "Where the Mage's field lies"; R6.
15a. **The field's amount is fractional, and saving keeps it exact.** The field's amount
    before defence becomes a fractional number (a `double`). That covers the field's
    effect (`AttackEffect.Amount`) and its saved form in the dive save
    (`BattleEffectSave.Amount`), which `BattleSnapshot` writes and restores.
    - `SaveFile.CurrentVersion` goes to **4**.
    - A version-3 save still loads. Its stored whole number is read as the field's amount,
      already rounded, since version 3 rounded the amount down at cast.
    - A battle that is saved and reloaded deals exactly the same field damage, hit for hit,
      as the same battle never saved.

    Shields Up's amounts are still whole numbers. `DefenceBonus` still returns whole
    defence, the sum of the Shields Up amounts held, exactly as today, so no defence figure
    becomes fractional. — Main loop, settling a blocking finding from `forge-prd-reviewer`.
16. **A field hit is still not a strike.** R14 changes only whether the field misses and
    what it does against defence. A field hit still adds no charge to any bar. It still
    leaves a Rogue's Vanish in place: whether the field should end Vanish is a separate open
    question. Each victim's damage after defence is added to the Mage's damage dealt, which
    the targeting weights count. — The EhrensDocs `Individual Types.md` change ("The Mage's
    lingering field isn't a strike"); the EhrensDocs `Combat.md` change "What the targeting
    weights count"; report 62 §2.

### Wear

17. **Specials don't wear the weapon.** A special spends no use of the attacker's weapon,
    however many hits it lands: the flurry, Volley, the Brute's two-row cleave, and the
    field. The weapon still adds its roll to a special's damage. Armour still spends a use
    for every hit it takes, whether from an ordinary attack or a special. A free attack from
    the Luck reset is an ordinary attack, so it wears the weapon. — `Equipment.md`
    § Durability; `Combat.md` § The Luck Reset.

### Superseded

18. Existing tests that pin the rules this PRD replaces are replaced along with the rules:
    the advantage multiplier, the Brute ignoring a Tank's defence, the area factor of one
    half, the strike shares, the four-strike Fighter, the six-strike flurry, specials wearing
    the weapon, the field ignoring defence, and the field's amount being rounded down at
    cast. The tuning file keeps only placeholders.
    `TypeAdvantageMultiplier`, `AreaDefenceFactor`, `RogueStrikeShare`, `FlurryStrikeShare`
    and `FighterStrikeCount` either go or become settled constants. — `Tuning.cs` header (every
    placeholder lives there and is listed for the user).

## Out of Scope

- The gear bands and durability bands in `Equipment.md`: that is a separate item (#55). This
  PRD uses whatever bands are in the tuning file.
- Health from Constitution × 10, special-bar charging per hit, and when a special can be used.
- Whether a field hit wears the victim's armour. Today it wears nothing. `Equipment.md`
  § Durability says "armour wears from everything", and that is not changed here (see Needs
  your call in the hand-back).
- Choosing a monster's rank in dungeons above F, and monster gear.
- Reduced damage for the Brute's neighbours or for the rest of the Mage's column. Both still
  take full damage, as the EhrensDocs `Individual Types.md` change has it.
- Ordering the random rolls within a strike or a flurry. That is left to the code, as long as
  R13's rule about the sixth strike holds.

## Open Questions

- A hit's damage can land on a fraction — the mitigation is a ratio, and an area attack
  takes two-thirds of the defence into it. Which way does that round? It decides whether a
  hit from far below a member's rank is chip damage forever or genuinely nothing.
  *(`Guild Members.md`. Built as R6's placeholder: round down once.)*
- The Mage's lingering field damages what stands in it. Does that damage count as an area
  attack too, paying two-thirds defence, or is the reduction only for an attack that is
  aimed? *(`Guild Members.md`. Built as R14's placeholder: yes.)*
- The Fighter's fifth and sixth flurry strikes each turn on a Luck check — is that the same
  check that can reset a cooldown, or a separate roll of its own? *(`Individual Types.md`.
  Built as R13's placeholder: a separate roll with its own curve.)*
- Does the field's damage end a Rogue's Vanish, the way an area attack does? *(EhrensDocs
  `Individual Types.md`. Unchanged here: it does not.)*
- With each matchup working through its own mechanism rather than a shared multiplier, the
  six advantages aren't necessarily worth the same amount. Should they be, or is it fine for
  some matchups to bite harder than others? *(`Guild Members.md`.)*
- *PRD author's proposal, not from the docs:* what K does a specialist's tier carry? Built as
  R4's placeholder: the K of the rank with the same position on the ladder.
- *PRD author's proposal, not from the docs:* "The first four strikes always land" — does
  that mean the flurry can't miss, or only that four strikes always happen? Built as the
  engine does today: every flurry strike rolls to hit.
- *PRD author's proposal, not from the docs:* "The flurry's strikes hit hard" — do they
  carry more than an ordinary strike? Built under R9 and R12: no, each one is an ordinary
  full strike.
