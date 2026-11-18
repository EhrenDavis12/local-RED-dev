# Look and feel: approved on the animation side vs. the game as built

> **Status:** Research report for queue item #64 (2026-11-13). The full list of approved
> choices now lives in `EhrensDocs/Look and Feel.md`; this report only checks the game against
> it and names the gaps.

## What was found

The game uses the approved still backdrops (meadow and cave), the approved formation lane
heights (scaled down), the Archer's sprite sheets, the parchment map and gold icon 1.
Nothing else the user approved has reached it. All the motion is missing — parallax, wind,
ground blend, the battle intro, the idle mix — and so are the bars, damage text, effects,
scroll menus, font, palette screens, icons and every sound.

The user's example is right. The game draws two horizontal bars under each figure, green
health and blue special (`CombatantView.BuildHud`). The approved design (animation item #56,
"1,5,11") is two thin vertical bars, red and blue, standing about 15 px behind each character
on the quiver side, drawn above everyone, that nudge 16–40 px aside on a hit or an attack.

Why it happened: the choices were approved in the animation checkout's queue and never written
into forge's design docs, so no build item ever named them. `EhrensDocs/Look and Feel.md` now
holds them, and the Focus says the approved look is binding.

Checked on the game's `main` (the working tree is on `queue/build`, which adds no visual change).

Path prefixes: **A** = `/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs`,
**U** = `/Users/ehrendavis/work/local-RED-dev/src/unity-side-scroler/sideScrollerBattles/Assets/Annie`,
**G** = `src/guildmasters-descent`.

## Choice by choice

| Choice | In game | Evidence | Gap → whose work |
|---|---|---|---|
| Meadow layers (sky, mountains, hills, trees, ground, bushes) | yes, as a still | `G/Assets/Resources/Backdrops/Meadow/L01–L17`; `BackdropArt.cs` freezes at 13.1 s | — |
| Parallax and cloud drift | no | `BattleBackdropView.cs` sets each offset once | game work (speeds already in `BackdropArt.cs`) |
| Battle intro (scroll, run-in) | no | no intro code; run sheets sit outside Resources | game work — `U/BattleScene1Full/` |
| Idle mix, random start frames | no | `CombatantView` plays "idle" from frame 0 | game work (sheets already in `G/Assets/Art`) |
| Ground and grass blend | no | no shader | game work — `U/BattleScene1GroundBlend/` |
| Wind | no | no shader | game work — `U/BattleScene1Wind/` |
| Formation and size by distance | partly | lane heights match, but `BattleFormationFit = 0.65` draws every figure at 65% | question for the user (below) |
| Cave | yes, as a still | `G/Assets/Resources/Backdrops/Cave/*` | drift: game work |
| Contact shadows, small occluder, cave darkness, repeat-free ground | no | — | **annie's work**: only sandbox tests exist; game-ready layers needed |
| **Health and mana bars** | no | `CombatantView.BuildHud`, horizontal, under the feet | **game work** — `U/BattleScene1Full/Runtime/SfDirector.cs`, `Data/full_plan_f.json` |
| Archer art | yes | `G/Assets/Resources/Characters/Archer/` | — |
| Rogue (Assassin) animations | no, yellow placeholder | `CharacterArt.ArtIdFor` only knows the Archer | **annie's work**: clips approved, no sprite sheets |
| Fighter attack, other types | no | — | **annie's work**: sheets and the rest of each set |
| Monsters | no, drawn as flipped Archers | `Tuning.MonstersUseMemberTypeArt = true` | **annie's work**: no monster animation approved |
| Death dissolve | no, dead dim to 45% | `BattleDeadBrightness` | game work — `U/EnemyDeath/` |
| Arrows and layered hit | no | no effect code | game work — `U/ArcherVsArcher/`, `SfEffect.cs`, `A/effects/particles_v1/` |
| Archer miss, knife, fire arrow, cleaver | no | — | game work — `U/ArrowMiss`, `U/KnifeFx`, `U/FireArrowSpell`, `U/SkeletonClawFx` |
| Damage text | no | `HitNumbers.cs`: built-in font, white | game work — `U/DamageText/Textures_chibi_half/` |
| One Rod scroll menus | no | `UiParts`, `MenuColors`: plain blocks | game work — `A/scenes/ui_parchment/game_ready_v1/` (still in review on the animation side) |
| Scroll unroll and roll-up | no | — | game work — `U/ScrollUnroll/` |
| Map is the main menu, no title screen | partly | `BootScreen.cs` still shows a title screen; map buildings carry name tags | game work; tags: question below |
| Parchment map | yes | `G/Assets/Resources/Menus/map_B_paper.png` | — |
| Settings, about, character select, shop screens | no | — | game work — `game_ready_v1/` |
| Victory and Defeat pop-ups | no | `BattleScreen.ShowBanner`: black block | game work — `game_ready_v1/{victory2,defeat9}` |
| Game font (Eagle Lake) | no | `UiParts.DefaultFont` = LegacyRuntime | game work — `A/scenes/ui_parchment/lettering_v2/fonts/eaglelake/` |
| Gold icon | yes | `G/Assets/Resources/Menus/gold_1.png` | — |
| Crystal, item icons, close button | no | — | game work — `icons_currency/crystal`, `icons_v2/I03`, `icons_items` |
| Palette on characters | no | — | **annie's work**: no recoloured sheets |
| Palette on screens | partly | map only | comes with the menu work |
| Sound effects and music | no | no AudioSource anywhere | game work — `A/sounds/` (still in review), music folders |

## Annie's list (hand this to the animation side)

- Sprite sheets for the approved Rogue (Assassin) clips and the Fighter attack.
- Approved animation sets for every other type and every monster.
- The Archer's special.
- Character sheets recoloured in the approved palette.
- Game-ready contact shadow, small occluder and cave darkness layers (and repeat-free ground).
- Sign-off on the game-ready menu pieces (#223) and the gathered sound library (#220), both
  still waiting on the user there.

## Game work queued

Under the standing yes, in this order: the battle scene in motion; the bars; hits, arrows
and the death dissolve; damage text; One Rod menus with the scroll; the font; icons; sound
and music. Every one copies files into the game, never links to the other checkout. The
text-baked screen pictures are never used as UI — the menus are built from the game-ready
pieces.

## Recommendation

Build the battle scene and the bars first: they are what the user sees most and what they
named. The two questions below are cheap to change either way.

## Open Questions

- The game draws every fighter at 65% of the approved size so all fifteen fit. Should fighters
  be drawn at the full approved size, even if the back rows crowd the sky?
- The map's buildings carry name tags, but the approved map has no labels "for now". Keep the
  tags so players know what each building is, or remove them?
