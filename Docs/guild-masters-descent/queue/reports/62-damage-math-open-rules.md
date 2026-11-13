# The damage math's three open rules

> **Status:** Research for queue item #62, 2026-11-12. Three decisions for the user; nothing
> here is settled until they answer. Sources are the other dev's originals (`Guild
> Members.md`, `Combat.md`, `Individual Types.md`) and the combat engine on `queue/build`
> in `src/guildmasters-descent`.

## Why these three now

Item #51 rebuilds the damage math to the originals: damage × K ÷ (K + Defence), K from the
attacker's rank (F 20, E 40, D 80 … doubling), area attacks paying two-thirds of the
target's defence. Its tests have to pin an exact number for every hit, so each of these
three changes what a test asserts. None of them is answered anywhere in the originals or in
EhrensDocs — all three sit in the originals' Open Questions.

## 1. Which way a fractional hit rounds

**Where it's asked:** `Guild Members.md`, Open Questions — "A hit's damage can land on a
fraction … Which way does that round? It decides whether a hit from far below a member's
rank is chip damage forever or genuinely nothing."

**What the doc already says that bears on it:** "There is no minimum damage — enough
defence can reduce a hit to nothing." And health is a whole pool (Constitution × 10), so the
hit has to become a whole number somewhere.

**What the engine does today:** rounds down, once, at the very end of the hit (after the
type advantage and any share), in `Battle.cs` `Strike`. Every other fraction in the engine
rounds down too.

Worked hits, an F-rank attacker (K = 20) whose stat plus weapon roll comes to 10:

| Target's defence | Exact damage | Round down | Round to nearest | Round up |
|---|---|---|---|---|
| 10 (an F-rank member) | 6.67 | 6 | 7 | 7 |
| 10, by an area attack (pays 6.67) | 7.5 | 7 | 8 | 8 |
| 200 (about a C-rank member) | 0.91 | **0** | 1 | 1 |
| 1,000 (about an A-rank member) | 0.20 | **0** | **0** | 1 |

Where that F hit stops doing anything at all: round down — once defence passes 180; round
to nearest — once it passes 380; round up — never.

**Options:**

- **Round down** (recommended). A hit from far below a member's rank is genuinely nothing,
  which is what "there is no minimum damage" already promises. It's what the engine does, so
  nothing else moves. Cost: at F rank, where hits are single digits, it shaves up to one
  point off every hit — about a seventh of a 7-point hit — so fights run a little longer
  than the exact math says.
- **Round to nearest.** Fairer at low numbers (the average comes out right), and a weak hit
  still dies out eventually, just later — at about twice the defence round-down allows.
- **Round up.** Every hit that lands does at least 1 — chip damage forever. This contradicts
  "there is no minimum damage" in the same doc, so choosing it means that line changes too.
  It also means a crowd of F-rank enemies can always wear down an A-rank member.
- *(Not recommended)* Round by chance — 0.2 becomes 1 a fifth of the time. Exact on
  average, but it adds a dice roll to every hit, which makes fights harder to replay and
  test.

Whichever is chosen, it should round **once, at the end of the hit**, not at each step —
rounding the defence, then the fraction, then the advantage separately loses a point at
each step.

**How hard to change later:** cheap. It's one line in the engine and the tests' expected
numbers; nothing saved depends on it.

## 2. Whether the Mage's lingering field pays two-thirds defence

**Where it's asked:** `Guild Members.md`, Open Questions — "The Mage's lingering field
damages what stands in it. Does that damage count as an area attack too, paying two-thirds
defence, or is the reduction only for an attack that is aimed?"

**What the doc already says that bears on it:** area attacks can't miss "because they land
on a space rather than on a person," and pay two-thirds defence (`Guild Members.md`, Base
Stats). The field covers two columns and hurts a character who begins its attack inside it
or moves into it (`Individual Types.md`, The Mage). Nothing says whether it can miss or what
defence it pays.

**What the engine does today:** neither option. The field's damage is worked out once when
it's cast (the Mage's Intelligence plus one staff roll, times a share) and then dealt flat,
**ignoring defence entirely**, and it never misses. Item #51 has to change that whichever
way this is answered.

**Options:**

- **It's an area attack: two-thirds defence, can't miss** (recommended). The field lands on
  a space, which is the exact reason the doc gives for area attacks being special. It also
  keeps one rule for "Mage damage that isn't aimed at a person."
- **Full defence, and it can't miss.** Makes the field weaker per tick than the Mage's
  ordinary column attack — the field becomes mostly about the area it denies rather than
  its damage.
- **Full defence, and it can miss like an aimed attack.** Weakest; a Rogue standing in the
  field would mostly dodge it, which cuts against the Mage being the Rogue's counter.

Related, and asked separately in EhrensDocs (`Individual Types.md`): whether the field's
damage ends a vanished Rogue's Vanish, the way an area attack does. If the field counts as
an area attack, the natural answer is yes — but that is its own question and stays open.

**How hard to change later:** cheap. It's one flag on the field's damage and a few test
numbers.

## 3. Whether the flurry's fifth and sixth strikes use the Luck reset's check

**Where it's asked:** `Individual Types.md`, Open Questions — "The Fighter's fifth and sixth
flurry strikes each turn on a Luck check — is that the same check that can reset a
cooldown, or a separate roll of its own?"

**What the doc already says that bears on it:** the Luck reset's chance is 25% × Luck ÷
(Luck + 60) — 2% at Luck 5, 6% at 20, 12.5% at 60 (`Combat.md`, The Luck Reset). The flurry
"only runs to five or six strikes if those checks succeed," which reads as the sixth needing
the fifth first.

**What the engine does today:** no check at all — the flurry always runs six strikes. Item
#51 (or #52) has to add the checks either way.

What the reset's curve would mean for the flurry:

| Fighter's Luck | Fifth strike | Sixth strike (needs the fifth) |
|---|---|---|
| 5, a new F-rank recruit | 2% | 0.04% |
| 20 | 6% | 0.4% |
| 60 | 12.5% | 1.6% |
| 180 | 19% | 3.5% |

**Options:**

- **A separate roll with its own, higher curve** (recommended). With the reset's curve the
  flurry is four strikes almost every time for most of the game, so "four to six" is a
  promise the player will rarely see kept. Its own curve can keep the same shape — always
  rising, never reaching its ceiling — with a higher ceiling. A placeholder to build with
  until it's tuned: 50% × Luck ÷ (Luck + 20), which gives 10% at Luck 5, 25% at 20, 37.5% at
  60.
- **The same check as the reset** — the same formula, rolled fresh for each strike. One
  rule to learn, one Luck curve in the game; the cost is the table above. A reset and a
  flurry extension can't be the *same* roll in a literal sense — they happen at different
  moments — so "same check" means same formula, separate dice.

Either way: is the sixth strike rolled only after the fifth succeeds? The doc reads that
way, and it's what the table assumes. If the two were rolled independently, a flurry could
land a sixth strike without a fifth, which doesn't make sense as a count.

**How hard to change later:** cheap. It's a formula and a few test numbers; the chance can
be retuned at any time.

## What happens when the user answers

Each answer lands in EhrensDocs as a change note for the other dev, the way #27 and #25 did
— the originals stay untouched — and goes into #51's PRD verbatim. The engine is not changed
by this item.

## Open Questions

- Which way does a fractional hit round — down, to nearest, or up?
- Does the Mage's lingering field pay two-thirds defence and never miss, like an area
  attack?
- Are the flurry's fifth and sixth strikes the reset's check, or a separate roll with a
  curve of its own?
