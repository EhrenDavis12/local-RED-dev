# Art request list for annie

> **Status:** Research report, 2026-11-25. This is a read-only survey of the game on `main`
> and the design docs as they stand today. It is the list to hand to annie. Nothing here is
> approved art. Each row says which approved art it should match.

## Summary

| Group | Now (yellow box, a held stand-in, or nothing) | Later (the docs want it, the feature isn't built) |
|---|---|---|
| Characters | 39 battle clips across 8 types, 8 drink clips, 4 relaxed portraits | 6 specialist sets, 5 monster families |
| Items | 5 icons (ore, herb, 3 shields) | 5 buff-potion icons, plus 3 looks nobody has defined yet (loot item, rank looks) |
| Screens & UI | 4 (Auto icon, Vanish, Shields Up, Mage field) | 7 effects, 4 station pictures |

How "now" was found: every yellow box comes from `PlaceholderShape.Create` or
`MissingAssets.Register`. The full call list is in `CharacterArt.Find`, `GearIcons.KeyOf`,
`ResultScroll.WriteLoot`, `EffectShapes.Create`, `BattleScreen.BuildAutoButton` and
`UiParts.Portrait/Still`. The game also writes its own list to `Lists/missing-art.md` in
the game repo. That copy is from 20 Nov, so it is partial: Porter, Tank idle/defend and Mage
idle/hurt/defend are missing from it because the screenshot run never reaches them. The
tables below come from the code, not from that list.

**Character art can't just be dropped in by file name.** A clip loads only once
`CharacterArt.cs` has an entry for it: frames, fps, columns, rows, cell size and feet
column. Annie's `<clip>.sheet.json` carries those numbers, so every hand-off needs a build
item after it. Icons and stills are different: they load by the exact key given below.

## Characters

### Shared spec for every battle clip

- **Sheet:** one body PNG with the weapon drawn into the frames, as the Rogue, Fighter,
  Tank and Mage have it. Frames sit on a grid of square cells, read left to right and top
  to bottom. The figure faces right on a transparent background.
- **Scale:** a 512 px cell, feet at column 247 and row 431, so the feet stand 81 px above
  the cell's bottom. The body is 404 px tall. A bigger cell is fine if the feet keep that
  81 px margin. Today's sheets use cells from 480 to 896 px.
- **Speed:** 16 fps (Archer, Rogue) to 24 fps (Fighter, Tank, Mage). Idle and run loop,
  and death holds its last frame. Hurt ends on the ready pose.
- **On screen:** 184 px tall in the back lane up to 240 px in the front lane, on the
  1920×1080 battle frame (`Tuning.BattleLaneFigureHeight`). Monsters are the same figure
  mirrored.
- **Where it goes:** `Assets/Resources/Characters/<Type>/<action>.png`. The game calls the
  hurt clip "hurt" but the file is named `hit.png`.
- **Clip names the game asks for:** `idle`, `attack`, `special` (combat types only),
  `hurt`, `defend` (played on a blocked hit), `death`, `run` and `run_stop` (the battle
  intro). `idle_headturn` and `idle_shift` are optional extras that the idle mix uses if
  they exist.
- **Style to match:** the Fighter's approved sheets (`Characters/Fighter/idle.png`, 6144²,
  144 frames) and the Rogue's (`Characters/Rogue/*.png`). Every character keeps to the
  colour families taken from the Archer (`Look and Feel.md`, "Roster colour rule").
- **A missing clip today:** the type's ready still (`Characters/<Type>/ready.png`, 1024²) is
  held through the move. A type with no still at all gets a yellow box. A missing death
  falls back to the approved enemy-death dissolve on screen, but it is still listed as
  missing.

### Battle clips — now

✔ = has a clip. ✘ = missing; the ready still is held in its place.

| Type | idle | attack | special | hurt | defend | death | run | run_stop | Missing |
|---|---|---|---|---|---|---|---|---|---|
| Archer | ✔ | ✔ | ✘ | ✔ | ✔ | ✔ | ✔ | ✔ | 1 |
| Rogue | ✔ | ✔ | ✘ | ✔ | ✔ | ✔ | ✔ | ✔ | 1 |
| Fighter | ✔ | ✔ | ✘ | ✔ | ✔ | ✔ | ✘ | ✘ | 3 |
| Tank | ✘ | ✔ | ✘ | ✔ | ✘ | ✔ | ✘ | ✘ | 5 |
| Mage | ✘ | ✔ | ✘ | ✘ | ✘ | ✘ | ✘ | ✘ | 7 |
| Brute | ✘ | ✘ | ✘ | ✘ | ✘ | ✘ | ✘ | ✘ | 8 |
| Porter | ✘ | ✘ | — | ✘ | ✘ | ✘ | ✘ | ✘ | 7 |
| Cook | ✘ | ✘ | — | ✘ | ✘ | ✘ | ✘ | ✘ | 7 |

That is 39 clips. Specialists have no special bar, so they have no special clip. They do
attack, get hit, block, die and run in like anyone else (`Combat.md`: "A specialist attacks
on its own cooldown like anyone else").

What each special has to show, quoted from `Individual Types.md`:

- **Archer, Volley:** "it hits the target, the enemies one to each side of it, and the one
  directly behind it."
- **Rogue, Vanish:** "the Rogue becomes untargetable." The clip is the moment of vanishing.
  The lasting look is the Vanish effect under Screens & UI.
- **Fighter, flurry:** "a flurry of 4 or 6 strikes on a single target."
- **Tank, Shields Up:** "temporarily doubles the Tank's own defence" and covers the allies
  behind him.
- **Mage, field:** "a lingering field: it covers two columns of the enemy's grid." The
  clip is the cast.
- **Brute, the special cleave:** "skips the nearest occupied row and cleaves the two rows
  behind it… When the Brute pushes past the front row, it moves there, cleaves, and returns
  to its own node, all in the same action."

The Brute's ordinary attack is also a cleave: "it hits the targeted enemy and the two
directly next to it."

What each type looks like, and where its approved source is (`Look and Feel.md`, and
`Assets/Resources/Characters/STAND-INS.md`):

| Type | Approved look | Source key |
|---|---|---|
| Archer | Forest Robes, Wood Bow | `Characters/Archer/*_body_forest.png` |
| Rogue | the Assassin | `rogue/keys/K0_rogue.png`; six poses approved (#250) |
| Fighter | Design 1 | `fighter/startend_v1/`; six poses (#249) |
| Tank | the Knight with warhammer and shield | `handoff/characters/Knight/keys/ready.png` |
| Mage | Star Sage, ready pose 2 | `mage/ready_v2/` |
| Brute | stance G_s3741, double-bladed axe | `brute/keys/K0_brute.png` |
| Porter | design 4, "for now"; six poses approved (#254) | `porter/design_v1/` |
| Cook | the cleaned Cook, "Cook at the ready is approved" (#243) | `cook/design_v1/cands/C_cook_clean.png` |

"A character's art never changes with its gear" (`Look and Feel.md`), so nobody needs
per-gear sheets.

### Drink clip — now (nothing is drawn)

The game already lets any member, Cook and Porter included, drink a healing potion
instead of attacking, from the drink buttons. The docs: "the player can have it drink a
healing potion instead of attacking" (`Combat.md`). The screen plays no animation: the
health bar rises and that is all. That makes 8 clips, one per type, named `drink`. The game
has no slot for this clip yet, so code has to call it too. The potion-drink sounds are
already in `Resources/Audio/Sfx/items/potion_drink`. The flask should match
`Menus/icons/icon_round_flask_128.png`.

### Menu portraits — now (a stand-in is shown)

A portrait is the type's `relaxed.png`: 1024², facing right, feet at the same fraction of
the square as a battle cell. It shows at 200×200 on the Dorms sheet and 220×220 on a
recruit card, in UI units against a 2532×1170 reference screen
(`Tuning.DormsPortraitSize`, `RecruitPortraitSize`). The ready pose stands in today for
four types:

| Type | Drop at | Note |
|---|---|---|
| Brute | `Resources/Characters/Brute/relaxed.png` | no relaxed pose approved |
| Tank | `Resources/Characters/Tank/relaxed.png` | none approved |
| Rogue | `Resources/Characters/Rogue/relaxed.png` | the Assassin's six-pose set (#250) includes a relaxed pose: copy it in |
| Cook | `Resources/Characters/Cook/relaxed.png` | none approved |

The Porter has a newer approved relaxed pose ("relaxed v2", #254), but the game still
carries v1. Style to match: `Characters/Fighter/relaxed.png` and `Characters/Mage/relaxed.png`.

### Specialists — later (not in the game yet)

The originals unlock the Scout, Herbalist and Miner at E, and the Armourer, Alchemist and
Blacksmith at D (`Specialists.md`). Specialists "occupy a node on the grid" in battle, so
each one needs the same set as the Cook: a relaxed portrait, a ready still, and idle,
attack, hurt, defend, death, run, run_stop and drink. Specialists carry no weapon or armour.

| Specialist | What it does | Design status (`Look and Feel.md`) |
|---|---|---|
| Blacksmith | makes and repairs weapons | design 2 with the hammer fix, approved as a still (`blacksmith/basekey_v1/`) |
| Alchemist | brews potions | design 3, approved as a still |
| Scout | — | Pathfinder, column 2, spyglass off (`scout/design_v5/`) |
| Herbalist | extra herb slots | no design |
| Miner | extra "minerals" slots | no design |
| Armourer | makes and repairs armour | no design |

The Cleric is approved as a design (#178, #183), but the game has no Cleric type.

### Monsters — later

Today every monster is a mirrored guild member of one of the six combat types
(`Tuning.MonstersUseMemberTypeArt`). The originals say a monster "is built from the same six
combat types too" (`Combat.md`). EhrensDocs says "The dungeon's enemies are monsters" and
that missing monster art is a yellow shape (`EhrensDocs/The Dungeon.md`). For each family:
a ready still at least, then the same eight clips, at the shared spec above, facing right
(the game mirrors them).

| Family | Approved designs | Beyond the design |
|---|---|---|
| Goblin | Cutthroat, with a cleaver (#137) | — |
| Orc | Gorehorn, Ironjaw, Ironback, Warboss, Tusker (#109) | — |
| Skeleton | Gravehorn, Hound Skull, Barrow Brute, Hollow Stalker (#110) | cleaver hit and miss effect v1 (#133), not copied into the game |
| Spider | the spiders (#100) | Cave spider's six poses approved (#263) |
| Dragon | 5 round-2 dragons (#182, #192) | Ember Wyrm, six keys v2, approved (#264); boss music exists |

The sounds are already in the game: `Audio/Sfx/creatures/` has goblin, hobgoblin, gorehorn,
skeleton, spider and dragon buckets.

## Items

### Shared spec for every icon

- **Style:** I03 "Scorched Edge" with "hard red slashes, best on tan buttons"
  (`Look and Feel.md`, Icons).
- **Sizes:** two PNGs per icon, 64 and 128 px square, transparent. Key:
  `Assets/Resources/Menus/icons/icon_<name>_64.png` and `_128.png`.
- **Style to match:** `icon_round_flask_128.png`, `icon_shield_128.png` and
  `icon_gold_128.png` in that folder.
- **On screen:** 64×64 on the victory list (layout rows at x 658), up to 128 in the shop and
  Dorms. The game picks the 64 file at 64 px or below and the 128 file above that.

### Now

| Asset | What it is | Where it shows | Today |
|---|---|---|---|
| Ore icon | ore dropped by monsters, spent to repair broken gear | victory list, one row per kind, 64 px | yellow box labelled "Ore" (`ResultSpec` uses `NoIcon`). Files `icon_ore_64/128.png` are already in `Menus/icons`, from annie's queue-226 set, which is in review. They show a grey rock with red flecks. `Look and Feel.md` says "Ore and herb have no picture yet". The victory screen also needs the art copied into `Menus/results/victory/pieces/` and a code change. |
| Herb icon | herbs dropped by monsters | same | yellow box labelled "Herb". `icon_herb_64/128.png` (a green bunch tied with twine) is in the same position as the ore icon. |
| Buckler icon | shield kind 2 | Dorms, shop, gear picker | wears the round shield; listed as "Buckler icon" |
| Kite shield icon | shield kind 3 | same | same; listed as "Kite shield icon". The name `icon_kite_shield` is already taken by **Full armour's** icon, so this one needs a different key, e.g. `icon_shield_kite`. |
| Tower shield icon | shield kind 4 | same | same; listed as "Tower shield icon" |

The three shields currently all map to `icon_shield` in `GearIcons.NameOf`. New keys need a
one-line code change each.

### Later

| Asset | What it is | Doc wording |
|---|---|---|
| Wind Step | buff potion | "raises Dexterity" (`Specialists.md`) |
| Dragon's Vein | buff potion | "raises Strength" |
| Rock Skin | buff potion | "raises Constitution, but it reaches defence only" |
| Ancient Gift | buff potion | "raises Intelligence" |
| God's Wish | buff potion | "turns 2 of the member's Luck bag's Falses into Trues" |
| Loot "item" | a monster drop that isn't a material | "One enemy in four drops materials or an item" (`The Dungeon.md`). No doc says what an item is. |

The buff potions are brewed by the Alchemist and used by the player during a fight. They
need a HUD button whose icon is probably the potion's own: "A buff is used by the player,
not drunk by a member… it reaches every member of the party". They should match the healing
potion `icon_round_flask`. `Look and Feel.md` removed the tri-flask and wax-vial icons from
the game: "remove the 21 pictures that nobody uses".

Gear found on a dive (`The Dungeon.md`: "A weapon or a piece of armour drops on the last
fighting floor before each rest area") and monster gear use the existing gear icons, so they
need no new art.

## Screens & UI

### Now

| Asset | What it is | Where and how big | Today |
|---|---|---|---|
| Auto icon | the Auto button on the battle HUD (members drink by themselves below 30%) | inside the HUD scroll button, left of Retreat, 48 px edge at most (`TopRowIconEdge`) | empty yellow square. Match `Menus/icons/icon_back_64.png` (Retreat's icon) and `battle_hud/pieces/glyph_pause_48.png`. Suggested key: `Menus/icons/icon_auto_64/128.png`. No doc describes how it looks. |
| Rogue vanish effect | lasting look on a vanished Rogue, "untargetable" | a frame around the figure, 184–240 px tall on the 1920×1080 battle frame | four yellow bars plus a tag reading "Rogue vanish" |
| Tank shields up effect | lasting look on the Tank and each ally behind him | a plate per covered figure, about 22% of the figure's width by 30% of its height, near its chest | yellow plates plus a tag reading "Tank shields up" |
| Mage field effect | a lingering field over two columns of the enemy grid, hurting anyone who attacks from it or walks in | a strip over each covered column, lane depth included | yellow strips plus a tag reading "Mage field" |

Effects in the game are particle and texture sets under `Resources/Fx/<Name>/`
(Materials and Textures), built in annie's Unity project. Style to match: the approved
layered arrow hit (`Fx/ArrowHit`), the archer miss (`Fx/ArrowMiss`), the enemy death
dissolve (`Fx/EnemyDeath`) and the fire arrow (`Annie/FireArrowSpell`), plus the twelve
approved particle sprites (#39).

### Later

| Asset | What it is | Note |
|---|---|---|
| Brute cleave effect | ordinary attack hitting three side by side, and the special that cleaves two rows back | no doc describes the look |
| Fighter flurry effect | 4 or 6 strikes on one target | — |
| Archer Volley effect | arrows on the target, both sides of it and the one behind | the arrow hit exists; the spread does not |
| Mage column attack | "an area attack covering a whole column of the enemy's grid — all three rows" | the game currently shows the single fire arrow |
| Heal effect | Cook healing, potion healing | the green "+" damage text already exists. The effect itself does not. |
| Buff potion effect | a buff reaching the whole party | — |
| Blocked hit clash | a blow stopped by defence | parked at annie, not approved (#215) |
| Station pictures (4) | the smithy, the armoury, the laboratory and the mead hall (`Core Concept.md`) | The map has 8 buildings: arena, guild, cave, home, shop, armory, about, settings, each 332×304-ish. The armory is drawn but opens nothing. No doc says whether stations are map buildings, rooms or pictures. |

The skeleton cleaver hit and miss effect (#133, v1) exists at annie but not in the game. It
arrives with the monsters.

## Not missing, for the record

- Meadow and cave backdrops, all menu screens (One Rod), the map, the fonts, damage text,
  bars, gold, the round flask, the class icons for the six combat types, and every
  weapon and armour icon.
- `icon_rank_*`, `icon_stat_*`, `icon_wood`, `icon_bone`, `icon_hide`, `icon_helmet`,
  `icon_injury` and `icon_timer` are in `Menus/icons` but no code draws them.
- The originals' newest edits (24 Nov: gold, fees, gear finds, monster gear, the axe and the
  war hammer, materials as ores or herbs) add no character actions. No current doc mentions
  a Mage or Spider action change.

## Open Questions

- The ore and herb pictures (a grey rock with red flecks, a green bunch of leaves tied with
  twine) already sit in the game's files but are not approved, and the victory list shows
  yellow boxes instead. Are those two pictures good enough to use, or should annie draw new
  ones? (Cheap to change later.)
- Should ore and herb look different at each rank, F through SSS, or is it one picture per
  kind with the rank written next to it? (Cheap now, more pictures later if yes.)
- The Tank can hold four kinds of shield (round, buckler, kite, tower), but his battle art
  always shows the same shield. Should the gear list show four different shield pictures,
  or should all four share the one round-shield picture?
- The Full armour icon is a kite shield, and one of the shields is also called "Kite
  shield". Should Full armour get a picture of armour instead?
- When a member drinks a potion in battle, should they play a short drinking animation, or
  should the health bar just rise as it does now?
- The docs say the Mage's normal attack hits a whole column of three enemies, but the
  game shows a single fire arrow hitting one. Should the Mage get a column-wide spell
  effect, or is the fire arrow fine for now?
- Should monsters use their own approved designs (goblin, orc, skeleton, spider, dragon),
  and if so, which kind of monster fights as which kind of guild member? Is the dragon an
  everyday enemy or saved for a boss?
- What should the five buff potions look like: one flask shape in five colours, or five
  different bottles?
- When an enemy drops "an item" rather than ore or herb, what is that item?
- Should the smithy, armoury, laboratory and mead hall each be a building on the map, a
  room inside the guild hall, or have no picture of their own?
- The Herbalist, the Miner and the Armourer have no character design yet. Should annie
  start those, and is the approved Cleric meant to become one of the game's types?
- The Brute, the Tank and the Cook have no relaxed pose for their menu portrait, so their
  battle-ready pose is used. Should annie make relaxed poses for them?
- What should the Auto button's icon show?
