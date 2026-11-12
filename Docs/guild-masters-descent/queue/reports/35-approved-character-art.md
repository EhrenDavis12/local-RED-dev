# Approved character art, and what the animation side still owes

> **Status:** Queue report for #35, 2026-11-12. Read once and acted on, then removed.

## What came into the game

Only what annie's Chart (`local_runs/chart/chart.json` in the animation checkout) marks
`done` was copied. That is one character in one look: the **Archer in Forest Robes with the
Wood Bow**, nine animations, each a body sheet with a weapon sheet laid on top —
idle, idle with a head turn, idle with a weight shift, attack, hurt, defend, run, run stop,
death. They were copied from the sheets annie installed in its own Unity project, never
linked. Left out on purpose: the run start (still in review), the Heavenly and Fire looks,
and the hit spark (in review).

The design docs already lean this way: The Dungeon change note says that for now the
monsters "might be limited to just the Archer's animations".

## What the game asks for and has no art for

Every combat character needs six animations: idle, attack, defend, hurt, special, death.
Anything missing shows as a bright yellow shape with its name on it.

| Game character | Has | Missing | Where annie is |
|---|---|---|---|
| Archer | idle, attack, defend, hurt, death (+ run, run stop, idle variants) | special | Nothing queued for a special |
| Rogue | — | all six | Idle, attack, hurt, defend, death **approved as clips**, no sprite sheets made yet; special not started |
| Tank | — | all six | Knight idle/attack/hurt/defend in review; warhammer grip fix blocked |
| Fighter | — | all six | Idle, attack, defend in review; hurt blocked |
| Mage | — | all six | Star Sage idle/attack/hurt/defend in review; spell effect in review |
| Brute | — | all six | Attack and defend in review |
| Porter | — | all six | Attack and hurt in review |
| Cook | — | all six | Nothing yet |
| Monsters | — | all | Spider, dragon, skeleton, goblin, hobgoblin designs in review |

Effects the battle will want and has none of: a hit spark (in review), a blocked hit
(blocked), the Mage's bolt and field (in review), a miss.

## Approved art outside this item

- **Menu screens** — the main map as the main menu, settings, about, character select and
  shop pages, approved 2026-11-10. Not copied: this item is the characters. They belong
  with the title-menu and hall work.
- **An older set of six** — knight, archer, barbarian, healer, mage, rogue, each with idle,
  attack, defend, hurt, skill and burst, sitting in the demo app's finished-assets folder
  from September. The Chart does not mark any of it done, so it was not copied. See the
  question below.

## Follow-ups

- The sheets load only in the editor today. The battle screen has to give them a way into
  the phone build (Resources or Addressables) and cut each sheet into frames, with each
  frame's pivot at the feet.
- A missing-art name must use the type ("Brute idle"), never a member's own name, or the
  missing list fills with one line per person.
- On the iPhone the sheets are compressed (about 240 MB for the Archer's full set, down from
  about 960 MB). One setting halves that again if memory gets tight.
- Nothing tests the art catalog yet.

## Open Questions

- The older September set (knight, archer, barbarian, healer, mage, rogue, six animations
  each) is in the animation project's finished folder but the Chart never marks it done.
  Copy it in too, or keep to Chart-done only? Going ahead with: Chart-done only.
