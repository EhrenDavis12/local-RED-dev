# Reconciling EhrensDocs with the updated originals

> **Status:** Research report for queue item #48, 2026-11-12. The EhrensDocs side is done
> (commit 314f155); the build side is queued as items below.

## What changed in EhrensDocs

The other dev's edits (merge e1033ee) to Combat, Core Concept, Equipment, Guild Members,
Individual Types, Specialists and The Dungeon were read against every change note. Under the
user's rule — the originals win — 30 edits landed in EhrensDocs. No original was touched.

- **Removed outright, overridden:** starting health set by rank (originals: Constitution ×
  10); type advantage as a multiplier (originals: advantages come from defence rules); the
  Brute skipping all of a Tank's defence (originals: it halves it); two questions those made
  moot.
- **Rewritten from turns to cooldowns:** combat is no longer turn-based, so every note that
  spoke of rounds or turns (turn order, how a battle ends, effect length, the mid-battle save)
  now speaks of cooldown cycles or time, or was dropped.
- **Rewritten to the originals' numbers:** healing (5% between floors, 15% at a rest area,
  Cook adds the same again), experience per combat by enemy rank, monsters' level and gear,
  the flurry's 4–6 strikes, the Mage field's triggers.
- **Kept, because the originals still leave it open:** loot is gold only for the first
  version; turning back anywhere and the carry limit; repair costs gold only; a member with
  no target picks one like an enemy; a battle stand-off after a set time; two Cooks; the open
  questions the originals still don't answer.

## What the built game does against the originals

| # | Rule now in the originals | Built game today | Size |
|---|---|---|---|
| 1 | Each fighter acts on its own cooldown (50 ms ticks, base wait by type, faster with Dex); the fight never pauses | Rounds in Dexterity order; the screen stops on each member's turn for the player to press Attack; stand-off after 50 rounds | L |
| 2 | Luck reset: a free attack, chance 25% × Luck ÷ (Luck + 60), enemies too | Not built | S, inside 1 |
| 3 | Special bar +10 per hit landed, +15 per bonus condition, carries between battles on a floor, resets each floor | +10 once per attack; bonuses 4–10 by type; bars empty every battle | M |
| 4 | Lasting effects last three of the owner's cooldown cycles | Three of the caster's turns — same idea, re-counted with 1 | S, inside 1 |
| 5 | Heal 5% between floors, 15% at a rest area, nothing between battles; Cook adds 5% / 15% | Cook heals 1 after every battle; rest area heals a flat 3 (+2 Cook); no between-floor heal | S |
| 6 | Health = Constitution × 10, members and monsters | Flat 10 for everyone | S–M |
| 7 | Damage × K ÷ (K + Defence), K by attacker rank; area attacks use ⅔ of defence | Attack minus defence; area attacks use ½ | S |
| 8 | Brute halves Tank's defence, Fighter halves Brute's, Tank's counts double vs Fighter | ×2 damage multiplier on every advantage; Brute ignores Tank's defence | S |
| 9 | Each strike carries the full damage stat + its own weapon roll; Fighter 2 strikes; flurry 4–6 with Luck checks | Fighter 4 strikes at a quarter each; Rogue strikes at half; flurry always 6 | S |
| 10 | Mage field hurts a character when it begins its own attack there, or moves in | Hurts everyone in it at the start of the Mage's turn; moving in does nothing | S–M, inside 1 |
| 11 | XP per kill by enemy rank (F 1, E 3 …), split per combat; level-up raises three stats; crossing a rank costs 20, 100, 500 … | 1 XP per monster per floor; flat 2 XP a level; level-up raises one stat | M |
| 12 | Enemies are the dungeon's rank or one below; rank sets their chance of gear; depth sets how many and how good the gear | Level by floor (1–4), one monster per battle, never any gear | M–L |
| 13 | Gear bands per the Equipment doc (sword 4–16, bow 6–26 …), doubling each class; durability bands; specials don't wear the weapon | Only the knife matches; placeholder bands and durability; specials wear the weapon | S |
| 14 | A dive pauses while the game is closed | Matches — but 1 changes what a mid-battle save holds | inside 1 |
| 15 | Dorms show stats and assign gear | Matches. The smithy / Blacksmith is rank D, outside the F-rank MVP | — |

Missions, dungeon finding and claiming, and raising the guild's rank are in the originals and
not built, but the Focus keeps guild ranks above F and timed and training missions out of the
first version, so no item is queued for them.

## Build items queued

Under the standing yes, in this order — the engine and the damage math first, because almost
every other item asserts against them:

1. Real-time cooldown combat and the Luck reset (rules 1, 2, 4, 10, 14) — [prd] [L]
2. Damage math by the originals (rules 7, 8, 9, and specials sparing the weapon) — [prd] [M]
3. Special bar charges per hit and carries within a floor (rule 3) — [prd] [M]
4. Health from Constitution × 10 (rule 6) — [prd] [S]
5. Healing as percentages between floors and at rest areas (rule 5) — [prd] [S]
6. Gear and durability bands from the Equipment doc (rule 13) — [prd] [S]
7. Experience by enemy rank and three-stat level-ups (rule 11) — [prd] [M]
8. Enemies by dungeon rank, count by depth (rule 12) — [prd] [M]
9. Live specials and formation changes on the battle screen, after 1 — [look] [M]

## Worth the other dev's eye

- Combat's cooldown section has two worked examples that disagree: "Dexterity 5 — 80 ticks"
  fits the formula; the later Rogue 71 / Fighter 104 / Tank 138 only fits Dexterity 8. New
  F-rank recruits are built with Dexterity 4–6.
- Combat's open questions ask whether a monster is something other than a six-type enemy; our
  Dungeon note says it isn't.

## Open Questions

- The first version yields gold only and sends monsters in with no gear, from earlier
  answers. The originals now have dives dropping gear and enemies equipped by the dungeon's
  rank. Keep the first-version cuts, or build the originals' version?
- When a combat's experience is split "between all party members", do members who died in it
  get a share?
- Do a special's own hits charge the bar it just emptied?
