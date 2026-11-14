# Which items can our members actually use?

> **Status:** Research for queue item #81, 2026-11-14. Parked on the user's calls below.
> Source read on `src/guildmasters-descent` branch `queue/build`.

## What was found

Every combat type carries one weapon kind and one armour kind, fixed by type
(`Equipment.md`, What a Member Carries). The code has exactly those twelve kinds and
nothing else (`Assets/Scripts/Core/Guild/GearKind.cs`). Specialists carry no gear in the
docs (`Specialists.md`, Equipment) or the code (`Guild.CheckEquip` returns `CarriesNoGear`,
`Assets/Scripts/Core/Guild/Guild.cs:410`). `EhrensDocs/` changes none of the kinds.

Icons come from `GearIcons.KeyOf` (`Assets/Scripts/Core/Menu/GearIcons.cs`), and the
files are in `Assets/Resources/OneRod/Icons/`. The character art is in
`Assets/Resources/Characters/<Type>/ready.png`. I looked at all of them.

| Type | Weapon (docs) | Armour (docs) | Item in game? | Icon now | Icon fits? | Character art holds |
|---|---|---|---|---|---|---|
| Fighter | two-handed sword | light armour | yes, both | `sword` / `chestplate` | partly: a one-handed sword, the same picture as the Tank's short sword. No for armour: the same steel plate as the Tank's full armour | long sword in both hands, chainmail and steel shoulder plates |
| Brute | club | tanned hide | yes, both | `axe` / `chestplate` | **no**: a single-bit axe. **No**: steel plate for a hide | **double-bladed battle axe**, fur mantle, leather straps |
| Tank | short sword | full armour | yes, both | `sword` / `chestplate` | yes / yes | **warhammer and a tall purple shield**, plate armour |
| Archer | bow | leather | yes, both | `bow` / `chestplate` | yes / **no**: steel plate for leather | bow, "Forest Robes" (`EhrensDocs/Look and Feel.md`) |
| Mage | staff | robe | yes, both | `staff` / `chestplate` (the fallback, since Robe has no case) | yes / **no** | crooked staff with an orb, purple and gold robe |
| Rogue | knife | hooded armour | yes, both | `dagger` / `helmet` | yes / **no**: a knight's plumed helmet for a hood | two knives, dark hood, teal mask |
| Cook, Porter | none | none | none, by design | — | — | — |

Score: 5 of 12 kinds have an icon that fits. 4 of 6 armours share one steel-chestplate
picture, the Robe through the fallback. The two swords share one picture. A test pins this
mapping (`Assets/Tests/EditMode/GearIconsTests.cs:93-102`), so changing an icon means
changing that test too.

## Items nobody can use (remove)

- **No gear kind in the game is unusable.** All 12 kinds have an owner
  (`GearKinds.OwnerOf`), the shop sells all 12 at class F (`Shop.Offers`, prices in
  `Assets/Scripts/Core/Tuning/Tuning.cs:179`), and equipping refuses the wrong type
  (`EquipOutcome.WrongType`).
- **21 icon files are in the game but are never drawn as an item.** All of them are in
  `Assets/Resources/OneRod/Icons/`: `scimitar`, `shield_1`–`shield_4`, `boot`, `ring`,
  `amulet`, `key`, `chest`, `scroll`, `arrows`, `crystal` ("drawn nowhere", per
  `GearIcons.cs`), `apple`, `loaf`, `cheese`, `drumstick`, `jug`, `round_flask`,
  `tri_flask`, `wax_vial`. The shop and victory layouts carry some of them as example
  content, but the code strips that out (`ShopScreen.cs:198`, `ResultScroll.cs:17-19`).
  Removing them is cheap: delete the files and their rows in `GearIconsTests.Copies`.
  **Keep** `round_flask` (a red potion, the health potion if one is added) and the
  shields (in case the Tank's shield becomes an item).

## Items missing (add)

- **No gear kind is missing**: each type's weapon and armour exists.
- **7 kinds need an icon of their own**: club, two-handed sword, light armour, tanned
  hide, leather, robe, hooded armour.
- **Possibly missing, depending on the user's calls:** a warhammer (if the Tank's weapon
  follows its art), a shield (the docs already give the Tank one: "push the Tank's shield
  aside", `Individual Types.md`, The Brute; and its special is "Shields Up"), and a
  carried potion (new, see Potions).

## Icon check (contradictions between docs and art)

| What | Docs say | Art shows | Where |
|---|---|---|---|
| Brute weapon | club | double-bladed axe | `Equipment.md`; `Characters/Brute/ready.png` |
| Tank weapon | short sword | warhammer + shield | `Equipment.md`; `Characters/Tank/ready.png`; `EhrensDocs/Look and Feel.md` ("with the warhammer", item #115) |
| Archer armour | leather | forest robes | `Equipment.md`; `EhrensDocs/Look and Feel.md` |

So "the club looks like an axe" has two sides: the icon is an axe, and so is the Brute
itself. annie has a queue-226 icon set in review (class badges, herb, ore). Its `hide`
icon was rejected as "a bear rug"
(`local-RED-dev/.../ui_parchment/icons_game_v1/sheet_226.png`), so nothing ready-made
covers the missing armours.

## Potions

- **What the docs say:** potions exist only as the **Alchemist's** brews. "Potions are
  temporary buffs: they raise stats for a fight", brewed at a rest area, with strength
  scaling with Intelligence (`Specialists.md`, The Alchemist). The Alchemist unlocks at
  guild rank D. What a potion rolls is an open question. The shop sells "items and
  equipment" (`Core Concept.md`; `Equipment.md`), but no doc defines a single item.
- **A member-held health potion is new.** No doc or code has it. A grep for potion,
  flask and consumable in `Assets/Scripts` finds nothing. It also changes the healing
  rules: "nothing comes back between the battles on a single floor" (`The Dungeon.md`),
  so a potion would be the only heal partway through a floor.
- **What is already in place:** the red `round_flask` icon, and the green "+" heal number
  (`EhrensDocs/Look and Feel.md`, Damage text).

| Option | In play | Work | Hard to change later |
|---|---|---|---|
| **A. Auto-drink:** one potion slot per diver, drunk by itself the first time health drops under a set share (placeholder 30%) | You hand a potion over in the Dorms. Mid-battle, a hurt member drinks and a green "+" number pops. No tapping | Medium: a slot on the member (a new save field, which is harmless), a shop row, and one rule in the engine. The battle needs no new input, and the docs keep the fight running without waiting on the player (`Combat.md`, Player Input) | Cheap. A tap button (B) can be added on top later |
| B. Tap to drink | You tap a member's potion during battle | Large: the battle screen has no member-tap actions yet. Even specials are "can't be used from the battle screen" for now (`EhrensDocs/Combat.md`). Tapping across 15 members in a fight that won't pause is fiddly | Moderate |
| C. Not in the MVP | No potions until the Alchemist (rank D) | None | — |

**Recommend A.** It is the cheapest to build, it fits a fight that never pauses, it gives
the shop its first non-gear item, and B can still be added on top later. The design
change goes in an `EhrensDocs/` change note, because the originals are read-only.

## How far shop and equipping are planned

| Piece | Docs | Code |
|---|---|---|
| Shop buy | Settled: open from rank F, baseline quality rises with rank (`Equipment.md`). For now, class F only (`EhrensDocs/Equipment.md`) | **Built**: all 12 kinds at class F, flat placeholder prices, rolled on buy (`Shop.cs`, `ShopScreen.cs`) |
| Shop sell | Settled: sell back for a placeholder share (`EhrensDocs/Equipment.md`) | **Built**: 50%; a held piece must be unequipped first (`ShopRows.cs`) |
| Shop above F | Open: prices and baseline | Sells nothing above F |
| Shop "items" (non-gear) | Named but never defined | None |
| Equip / unequip | Settled: Dorms, stores are guild-owned, own type only, a higher class is allowed (`Equipment.md`, Assignment) | **Built**: Dorms with roster, member sheet, slots with icons, Equip/Unequip/Repair (`DormsScreen.cs`, `Guild.TryEquip`, `Guild.Unassign`) |
| Showing a piece's numbers | Contradiction: original "see a piece's stats", EhrensDocs "shows none for now" | Shows the name, class and condition only |
| Gear in battle | Settled: damage, defence, wear by hits, breaking (`Equipment.md`, `Combat.md`) | **Built** (`Battle.cs:436`, `Battle.cs:622`) |
| Repair | Settled; gold only for now (`EhrensDocs/Equipment.md`) | **Built**, priced by condition (`Guild.cs:363`) |
| Recruit arrives with gear | Settled | **Built** (`Guild.cs:215-232`) |
| Crafting, drops, materials | Planned, with open questions on cost and roll | Not built. Loot is gold only for now |
| Stores cap | Open | No cap |
| Potions | Alchemist buffs only, open on what they roll | None |

## Recommendation

1. Keep all 12 gear kinds. Settle the Brute's and the Tank's weapons against their art
   first, because the icons depend on those answers.
2. Have annie draw the 7 missing icons, plus a warhammer or shield if the answers call for
   them.
3. Once the icons land, change `GearIcons.KeyOf` and its test. This is a `[look]` item,
   with no PRD.
4. Build the carried potion as option A. It needs a PRD, because it adds a save field and
   an engine rule, and a wrong guess there costs a migration and a rebalance.
5. Delete the unused food, jewellery, key, chest, scroll, boot, scimitar and arrows icons,
   if the user agrees.

## Icons for annie

The style to match is the game's approved icon set (I03 "Scorched Edge", tinted per queue
226):

- Painted cartoon objects with a thick dark-brown outline and soft cel shading.
- One bright highlight on metal or glass.
- Saturated colour: cool steel greys and warm wood browns.
- One object per icon on a transparent background, with no text, delivered at 128 and 64
  px.
- Weapons lie on a diagonal, handle bottom-left and head top-right.
- They have to read on a tan parchment button.

Match these two:
`/Users/ehrendavis/work/local-RED-dev-2/src/guildmasters-descent/Assets/Resources/OneRod/Icons/axe.png`
(weapons) and `.../OneRod/Icons/chestplate.png` (armour). The source set is in
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/scenes/ui_parchment/icons_game_v1/icons/`.

| Icon | Should depict |
|---|---|
| Club | A heavy wooden cudgel with a thick knobbly head, maybe iron-banded or studded, and no blade. Only needed if the Brute keeps a club |
| Two-handed sword | A greatsword: long straight blade, long two-hand grip, wide crossguard. It must look clearly longer than the existing sword |
| Light armour | A chainmail shirt with steel shoulder plates. It must not look like the full-plate chestplate |
| Tanned hide | A worn hide vest with a fur collar and leather straps, shown as a garment, not a flat pelt (the last try read as a bear rug) |
| Leather | A brown laced leather jerkin with stitched panels and a forest-green trim |
| Robe | A purple wizard's robe with gold trim, shown folded or hanging |
| Hooded armour | A charcoal hood and cowl with a teal mask scarf, with no metal |
| Warhammer (only if chosen) | A steel war hammer on a long wooden haft |
| Shield (only if chosen) | A tall purple kite shield with a gold cross. The existing round shields don't match the Tank |
| Health potion | No new art: the existing red `round_flask` fits |

## Open Questions

- The Brute's character art swings a big double-bladed battle axe, but the design calls
  its weapon a club, and the shop shows a "Club" with an axe picture. Should the Brute's
  weapon be an axe (rename it and keep the art, which is cheap) or a club (annie draws a
  club icon, and the Brute's character art eventually needs redrawing, which is
  expensive)?
- The Tank's art holds a warhammer and a big shield, but the design gives it a short
  sword. Should its weapon stay a short sword, or become a warhammer? Either way it's a
  cheap rename plus one icon.
- Should the Tank's shield be a piece of gear you can buy and swap, or just part of how
  the Tank looks? Making it gear adds a third slot for one type, a moderate change. Leaving
  it as looks costs nothing.
- The Archer's art wears forest robes, but the design says leather armour. Should its
  armour icon look like a leather jerkin or a forest robe? It's only a picture, so a quick
  call is fine.
- The game has 21 pictures nobody ever sees: food, rings, keys, scrolls, a boot, spare
  shields, a curved sword, arrows and flasks. Delete the ones with no planned use, keeping
  the red potion flask and the shields? Easy to undo; annie still has the originals.
- Should a member be able to carry a potion into a dive? The options:
  - **Recommended:** one potion each, which they drink by themselves the first time
    they're badly hurt in a battle. You see a green "+" heal and never tap anything.
  - You tap a member's potion during the fight to make them drink. This is more control,
    but much more to build, and fiddly with a big party in a fight that doesn't pause.
  - No potions until the Alchemist (a later guild rank).

  Starting with the automatic one is cheap to change later, and a tap button can be added
  on top.
- If potions go in, is a heal-only potion bought at the shop enough for now, or should it
  also come in other kinds (strength, defence)? Starting heal-only is cheap to widen later.
