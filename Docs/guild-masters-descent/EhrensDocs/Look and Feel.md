# Look and Feel

> **Status:** New doc proposed for the originals. The user's approved look for the game,
> gathered from the animation work; binding on the game build. Each choice carries the
> user's approving words, the animation-side item number (written "animation item #56" so
> it is not confused with the build queue's numbers) and where the final asset lives. The
> assets live in the other checkout, under
> `/Users/ehrendavis/work/local-RED-dev/src/`, and are copied into the game, never linked.
> A choice marked "in review" or "not picked" is not approved.

## Battle scene (meadow)

The first battle scene is a sunny meadow seen from the side, built in layers that drift at
different speeds so the camera move reads as depth. The Unity scene that holds it all is
`/Users/ehrendavis/work/local-RED-dev/src/unity-side-scroler/sideScrollerBattles/Assets/Annie/BattleScene1/`.
Approved 2026-10-29: "almost identical to the video im happy with that." (animation item
#41).

**Sky and clouds.** A bold sky with 11 separate bold clouds drifting on three layers. Far
clouds are smaller, paler and slower; near ones are bigger and faster. A faint edge line on
the near clouds is accepted. The user, 2026-10-23: "I would like to go with bold… layer
many individual clouds." Approved 2026-10-24: "everything looks so great with the parallax
effect. I love it. Let's keep it." (animation item #16). Assets:
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/scenes/battle1/sky/C3/`,
exported as `/Users/ehrendavis/work/local-RED-dev/src/unity-side-scroler/sideScrollerBattles/Assets/Annie/BattleScene1/Textures/`
layers L01 to L04.

**Mountains.** Separate flat two-tone mountains: 4 in front and 3 paler behind, both ranges
drifting very slowly. Same 2026-10-24 words as the sky: "everything looks so great with
the parallax effect. I love it. Let's keep it." (animation item #17). Assets:
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/scenes/battle1/mountains/M2/`,
exported as layers L05 and L06 in the same Textures folder.

**Hills.** Option A, the reviewer's pick; the user did not choose between A and C. Same
2026-10-24 words: "everything looks so great with the parallax effect. I love it. Let's
keep it." (animation item #18). Exported as layer L07 in the same Textures folder.

**Trees.** Style T-B: separate trees on two or three parallax layers, plus trees planted
on the ground that move at ground speed and read as rooted. The user, 2026-10-26: "the
trees look amazing i think you can wrap up that work" (animation item #19). Assets:
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/scenes/battle1/trees/v3/`,
exported as layers L08 to L10 and L14.

**Ground.** Textured sandy soil with fine stones and no grass blades, 3840 by 680 pixels
from the horizon at y=400. The user, 2026-10-26: "I do like the ground that has a
texterue to it and does a good blend" (animation item #20). Exported as layer L11.

**Bushes, rocks and grass patches.** Style S-B: two-tone with a light band and a thin
dark-green outline, moving with the ground; the front clumps move faster. The user,
2026-10-24: "the rocks and the bushes and some grass going along with the terrain. That
looks wonderful." (animation item #21). Exported as layers L15 and L17.

**No grass edge.** The ground has no grass edge. The user, 2026-10-26: "i only like the top
one. Just keep it simple and clean." (animation item #25).

**Ground and grass blend.** A grey-pattern mask blends grass into the soil. The user,
2026-10-29: "OK this all works for me." (animation item #50). Assets:
`/Users/ehrendavis/work/local-RED-dev/src/unity-side-scroler/sideScrollerBattles/Assets/Annie/BattleScene1GroundBlend/`
(shader GbMix, masks M1 to M3, G_grass).

**Wind.** The strong take: close trees, grass and bushes sway sideways only, the tops by
about 15.7 pixels, with a gust roughly every 4 seconds. Mountains, hills and far trees
stay still. The user, 2026-10-30: "I prefer the strong version otherwise its almost un
noticiable." (animation item #55). Assets:
`/Users/ehrendavis/work/local-RED-dev/src/unity-side-scroler/sideScrollerBattles/Assets/Annie/BattleScene1Wind/`
(the WwWind shader plus masks).

**Scene preview.** The user, 2026-10-26: "I love it finalize it." (animation items #22
and #27).

**Formation.** Option B3 with straight columns: 3 wide by 5 deep per side. Back rows are
smaller and the spacing grows to compensate; rows zig-zag; heads may rise into the sky;
both armies are mirrored. The user, 2026-10-26: "lets sign off on the placement and move
on" (animation item #26). Reference sheet:
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/scenes/battle1/formation/compare_sheet_B3fix.png`.

**Size by distance.** A figure's height is 0.1101 times its feet's y plus 126.4 pixels.
The user, 2026-11-12: "1, 3, 5,10 work for me." (animation item #209). Assets:
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/auto/sandbox/209/`.

**Idle mix.** Idle, head turn and weight shift are mixed at random, with random start
frames so nobody breathes in step. The user, 2026-10-28: "the idling we're done. Consider
that complete." (animation item #32). Assets:
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/scenes/battle1/preview_idle_attack/preview_v2/`.

**The intro.** The final take, F: an empty field, then a 4 second camera scroll with
parallax. The left army runs in at random times at normal leg speed; the enemies slide in
from the right in formation. The clouds stop when the camera stops. The first arrow flies
at about 6.25 seconds. Dead bodies stay down and their bar goes away. The user,
2026-11-01: "Battle scene intro is approved." (animation item #64). Assets:
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/unity/battle_scene1_full/take1f/`; the scene is
`/Users/ehrendavis/work/local-RED-dev/src/unity-side-scroler/sideScrollerBattles/Assets/Annie/BattleScene1Full/Scenes/BattleScene1Full.unity`
and holds the ground blend, wind, bars, arrows and hit effects together.

## Battle scene (cave)

The second battle scene is a small enclosed tunnel. The back wall moves at almost floor
speed, the ceiling is solid rock with stalactites here and there, ore veins run through
the rock, and a soft light comes from the upper left. The user, 2026-10-26: "I love it
finalize it." (animation item #27). Assets, with the brief, the preview still and the
stalactite renderer:
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/scenes/battle2/`
(`BRIEF.md`, `preview/stal_TEST_still.png`, `stal_render.py`).

## Shadows and depth

Approved 2026-11-12 for both scenes. These exist only as sandbox tests; there are no
game-ready layers yet.

**Contact shadows.** One shadow per object: a faint sliver for grass, a soft oval for
bushes, the strongest for trees. Characters get deeper shadows, about 25 to 30 percent.
The user, 2026-11-12: "i do like the idea of sadows makes the game come alive" and "the
deeper shadows for the charachters are better." (animation items #201 and #221). Assets:
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/auto/sandbox/221/`
(`sheet_r3.png`).

**Foreground occluder.** Dark, blurred bush or stalactite cards cropped by the frame edge,
kept small. The user, 2026-11-12: "I do like the the foreground objects but the just need
to be small." (animation item #212). Assets:
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/auto/sandbox/212/`.

**Cave darkness.** A camera-fixed vignette and a light pool under the fighters. The user,
2026-11-12: "1, 3, 5,10 work for me." (animation item #214). Assets:
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/auto/sandbox/214/vignette_layer.png`.

**Repeat-free ground.** Stochastic tiling, so the ground never visibly repeats. Same
words: "1, 3, 5,10 work for me." (animation item #203). Assets:
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/auto/sandbox/203/`.

**Not picked.** Haze (animation item #213), the tree strip (animation item #202) and the
material swatches (animation items #196 and #199) were filed away; they are not part of
the look.

**Still in review, not approved.** The full 15-a-side preview (animation item #222).

## Health and mana bars

The user, 2026-10-30: "1,5,11 thesee are what we want to go with for the Health bar
system." (animation item #56). Each character has two thin vertical columns side by side:
bright red health and bright blue mana or stamina, each 6 pixels wide. The separator is dark
brown (74,46,26) and the empty part is paper colour (236,222,190). A front-row bar is 15 by
64 pixels.

- The bar stands about 15 pixels from its character, on the back side (the quiver side),
  and does not follow the body.
- It is drawn on top of all characters whatever their row, with no body glow (option 1).
- Where it overlaps the quiver of the archer in front, it stays as it is (option 5).
- It nudges out of the way when its character is hit or attacks (option 11; the plan's
  values are 16 to 40 pixels). This is the "bump".

Assets:
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/scenes/battle1/hud_bars/round4/`.
Unity code:
`/Users/ehrendavis/work/local-RED-dev/src/unity-side-scroler/sideScrollerBattles/Assets/Annie/BattleScene1Full/Runtime/SfDirector.cs`
(Bars, DrawBar). Data:
`/Users/ehrendavis/work/local-RED-dev/src/unity-side-scroler/sideScrollerBattles/Assets/Annie/BattleScene1Full/Data/full_plan_f.json`
(bars, colors, nudge).

## Characters and animations

The animation chart is
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/chart/chart.json`.
Character files live under
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/characters/`.

**Archer** (Forest Robes with Wood Bow). Idle, head turn, weight shift, attack with no
draw (animation item #14), hurt, defend, run, run stop and death are done. Run start and
the hit spark are still in review, not approved.

**Assassin** (the game's Rogue). Approved as clips; there are no game-ready sheets.
- Idle key, animation item #1: "The assassin is looking good".
- Main idle, a 6 second breathing bob (animation item #65): "ok we can approve the assaisn
  ideal". Assets:
  `/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/characters/rogue/work/idle_v6/g0/`.
- Weight shift (animation item #43): "keep it".
- Attack with no dip (animation item #4): "I love the snap right into the attack action".
- Hurt, v9 s10902 (animation item #5): "let's just go with the new video".
- Defend, the guard key (animation item #6): "call it good".
- Run, r9 v6 (animation item #52): "i can approve it".
- Run stop (animation item #53): "approve that".
- Death, take s9803 (animation item #10).
- Before attacking, the assassin dashes forward by code, with no new animation (animation
  item #68): "a single jump is fine by me".

**Fighter.** Design 1 (animation item #105, 2026-11-09): "design 1 is good to go". Attack
is a 0.6 second start-and-end chop (animation item #208, 2026-11-12): "OuRS SE(TEST) looks
the best". Asset:
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/characters/fighter/startend_v1/`.
Idle (animation item #218) and defend (animation item #217) are in review, not approved;
hurt (animation item #216) and death (animation item #219) are blocked.

**Designs approved as stills only.** No animations yet.
- Mage, Star Sage (animation item #96), ready pose 2 (animation item #102):
  `/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/characters/mage/ready_v2/`.
- Tank, base key F_s3935_fix (animation item #13) with the warhammer (animation item
  #115). The grip fix (animation item #175) is blocked.
- Brute, stance G_s3741 (animation item #12).
- Porter, design 4 (animation item #117), "for now".
- Blacksmith, design 2 with the hammer fix (animation item #176):
  `/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/characters/blacksmith/basekey_v1/`.
- Alchemist, design 3 (animation item #120).
- Cleric, design 1 with healing stance 4 (animation items #178 and #183).
- Scout, Pathfinder column 2, spyglass off (animation item #207):
  `/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/characters/scout/design_v5/`.
- Goblin, Cutthroat (animation item #137):
  `/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/characters/goblin/fix_v1/`.
- Orcs: Gorehorn, Ironjaw, Ironback, Warboss and Tusker (animation item #109).
- Skeletons: Gravehorn, Hound Skull, Barrow Brute and Hollow Stalker (animation item
  #110).
- Spiders (animation item #100).
- All 5 round-2 dragons, with Sand Horn's horn fixed (animation items #182 and #192).

Each of these has its pick sheet at
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/characters/<name>/…/review/pick_sheet.png`.

**Roster colour rule.** Every character keeps to the colour families taken from the
Archer. The user, 2026-11-02: "let's enforce that". (animation items #98 and #101).
Reference:
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/auto/style_guide/families.png`.

**Gear and the art.** A character's art never changes with its gear. The Brute swings its
axe, the Tank holds its warhammer and its shield, and the Archer wears its Forest Robes,
whatever they have equipped: the Tank shows the shield it is drawn with whichever shield
it carries, or none, and the Archer's leather armour is gear, not a change of costume.
The user, 2026-11-14: "nothing about the animations character changes so the shield he
has the shield he'll always have" and "let them have what the design says, but in the
end, the art is not gonna change".

## Effects

**Particle sprites.** Twelve kinds. The user: "yes apporved so we can move on". (animation
item #39). Assets:
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/effects/particles_v1/`.

**Layered arrow hit.** A subtle arrow trail, a flash, a core, front and back particles, a
shockwave, a linger and a light. The user: "Lets keep it for now" (animation item #40); a
plain hit may want fewer layers later. It is used on every hit in the intro. Assets:
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/unity/archer_vs_archer/v2/`
and
`/Users/ehrendavis/work/local-RED-dev/src/unity-side-scroler/sideScrollerBattles/Assets/Annie/ArcherVsArcher/`;
code in
`/Users/ehrendavis/work/local-RED-dev/src/unity-side-scroler/sideScrollerBattles/Assets/Annie/BattleScene1Full/Runtime/SfEffect.cs`.

**Archer miss.** The user: "I love the archer miss". (animation item #69). Assets:
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/unity/arrow_miss/`
and
`/Users/ehrendavis/work/local-RED-dev/src/unity-side-scroler/sideScrollerBattles/Assets/Annie/ArrowMiss/`.

**Assassin knife hit and miss.** (animation item #68). Assets:
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/unity/knife_fx/`
and
`/Users/ehrendavis/work/local-RED-dev/src/unity-side-scroler/sideScrollerBattles/Assets/Annie/KnifeFx/`.

**Enemy death dissolve.** The hurt pose dissolves into particles from the head down. It is
used for any character with no death animation of its own. The user: "Enemy death is good
approved". (animation item #81). Assets:
`/Users/ehrendavis/work/local-RED-dev/src/unity-side-scroler/sideScrollerBattles/Assets/Annie/EnemyDeath/`.

**Mage fire arrow, v1.** The user, 2026-11-12: "can be approved for now". (animation item
#111). Assets:
`/Users/ehrendavis/work/local-RED-dev/src/unity-side-scroler/sideScrollerBattles/Assets/Annie/FireArrowSpell/`
and
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/unity/fire_arrow_spell/A/`.

**Skeleton cleaver hit and miss, v1.** The user: "can be a V1". (animation item #133).
Assets:
`/Users/ehrendavis/work/local-RED-dev/src/unity-side-scroler/sideScrollerBattles/Assets/Annie/SkeletonClawFx/`.

**Block clash.** Parked, not approved (animation item #215).

## Damage text

Damage numbers use the chibi font (Titan One, baked) at half size, and show damage only.
Damage is red with no minus sign; a heal is green with a "+". "Miss" is pale cream and
"Blocked" is pale steel blue. The text rises and drifts. The user, 2026-11-02: "The damage
numbers are good, approved" (animation item #71). Glyphs:
`/Users/ehrendavis/work/local-RED-dev/src/unity-side-scroler/sideScrollerBattles/Assets/Annie/DamageText/Textures_chibi_half/`;
clip:
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/unity/damage_text/take_c_chibi_half/`.

## Menus and the scroll

**The One Rod scroll.** R04 One Rod is the house style for every menu and button. The user,
2026-10-29: "R04 One Rode is our choice for all our menus and buttons… apply it to any
menue items we create when building in unity" (animation items #38 and #49). Assets:
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/scenes/ui_parchment/scroll_v3/R04_OneRod/`.

**Scroll animation.** Made by code: the rod rolls across while the writing stays still,
0.8 seconds each way, and closing is opening reversed. The user: "The scroll animation is
amazing approved" (animation item #74). Assets:
`/Users/ehrendavis/work/local-RED-dev/src/unity-side-scroler/sideScrollerBattles/Assets/Annie/ScrollUnroll/`
and
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/unity/scroll_unroll/take_A/`.

**Screens.** The map is the main menu, and each building opens its own scroll page. There
is no title screen; the user: "No not needed for now" (animation item #113). The picks are
settings 4, about 6, character select 8 and shop 10. Assets:
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/scenes/ui_parchment/screens_v1/`.

**Victory and Defeat pop-ups.** Victory 2 is a tall scroll with the loot as a written
list. Defeat 9 is brown ink with hand-lettered Retry and Exit. Exit is red on a win and
Retry is red on a loss; there is no loot on a loss. The user: "I'm picking two and nine"
(animation items #77 and #83). Assets:
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/scenes/ui_parchment/victory_v1/`,
re-lettered in
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/scenes/ui_parchment/font_v1/`.

**Game-ready pieces.** All 7 screens with no baked text, plus `layout.json` text slots,
in normal, pressed and selected states (animation item #223). Still in review, not
approved:
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/scenes/ui_parchment/game_ready_v1/`.

**Readable text and spacing.** One global minimum text size that every text in the game
obeys, no exceptions: cap height 32 px on a 2340x1080 phone for any text, 36 for button and
tab labels, 44 for titles (provisional; not yet checked on a device). Text never shrinks to
fit below it: a label that doesn't fit gets a wider scroll or shorter words. There is no
faded or 0.6-alpha ink, and disabled words keep at least 3:1 contrast. A scroll holds only a
page, a title, a one-action button (two words at most) or an icon pick. Status, stats,
prices, reasons and long text go on the page paper: Buy, Hire and Send say only the action,
the price sits on the paper above, and a red "Need 80 gold" line sits on the paper when
gold is short. Inner margins are a share of the paper between rod and curl: buttons, tabs
and chips 11% each side and 15% top and bottom; headers 15% and 5%; pick tiles and cards
8%; pages and pop-ups 4% left, 6% right, 10% top and 8% bottom. Stacked lines keep a clear
gap between their ink, and nothing is drawn over a portrait. The font has no "#" and no
middle dot, so menu text uses neither ("F-rank Fighter 2", "-" as the separator). Shop
tiles show the icon and price only; the name is in the detail panel. The user approved the
mocks 2026-11-15: "The mocks do look cleaner. Lets implament them." and "We should have a
global min text value so we stop displaying unreadable text." (animation item #242, queue
item #104). Measurements and the mock sheet:
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/ui_review/242/`
(REPORT.md, sheet.png).

## Map

A parchment inked map, style 4, on one fixed screen with no labels for now. The user,
2026-10-28: "the parchment Inc. map looks to be the winner" (animation item #31). Assets:
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/scenes/menu_map/v2/S04/`.
It is recoloured with "paper kept warm" (animation item #197). The map is an interactive
menu only; the user: "that map was just ment to be an interactive menu", so there is no
pathfinding on it.

## Font

One game font: Eagle Lake (option 11, "Steady Manuscript") with its ink treatment, for all
text except damage numbers. The user, 2026-11-01: "No font other than that for now" and
"The font for the rest of the app is approved" (animation items #76 and #83). Assets:
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/scenes/ui_parchment/lettering_v2/fonts/eaglelake/EagleLake-Regular.ttf`;
baked atlases at 18, 28, 44 and 92 in
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/scenes/ui_parchment/font_v1/bake/`.

## Icons

**Icon style.** I03 "Scorched Edge": 14 items_v3 icons, boot B1, shields S1 to S4 and
close button Q1, with hard red slashes, best on tan buttons. The user: "yes that's it.
We're going with it." (animation item #60). Assets:
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/scenes/ui_parchment/icons_v2/I03/`.

**Item set.** Scroll C, key A, chest B, staff A, bow B, arrows B, ring A and amulet A
(animation item #112). Assets:
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/scenes/ui_parchment/icons_items/`.

**Currency.** Gold icon 1 and violet crystal 4, "for now" (animation items #75 and #82).
Assets:
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/scenes/ui_parchment/icons_currency/gold/`
and
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/scenes/ui_parchment/icons_currency/crystal/`.

**What the game carries.** Only the pictures the game draws: the gear icons, the shields
for the Tank's shields, and the red round flask, which is the health potion. The rest are
left out of the game and out of the shop — the food and the jug, the ring, the amulet,
the key, the chest, the scroll, the boot, the curved sword, the arrows, the crystal and
the other two flasks. The user, 2026-11-14: "remove the 21 pictures that nobody uses we
don't need them them from the shop too".

## Palette

The game palette is palette_v4 option 3: red, green and blue plus gold corners, at
"bright" strength. The user, 2026-11-11: "go with 3 RGB + gold Bright" (animation item
#193). Assets:
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/auto/style_guide/palette_v4/`.
Every screen uses "paper kept warm" ("3 (paper kept warm)", animation item #197):
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/auto/style_guide/palette_v4/menus_map_v1/`.

## Sound and music

**Sound effects.** Approved buckets: arrows (animation items #62, #63 and #66), assassin
(#67), grunts and battle cries (#72), the menu click pool and paper pool (#73), gold
(#78), and animation items #106, #107, #108, #144, #149, #154, #160 and #174. They are
gathered, 67 buckets and 801 sounds, in
`/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/sounds/`
(animation item #220), and that gathering is still in review, not approved. The 13
fill-in buckets of animation item #185 are unheard and not approved.

**Music.** All music is turned down about 2 dB.
- Battle songs: animation item #61,
  `/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/auto/sandbox/61/paid/takes/`;
  and animation item #80,
  `/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/auto/sandbox/80/`.
- Menu songs: animation item #70,
  `/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/auto/sandbox/70/takes/`.
- Victory and defeat songs: animation item #79,
  `/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/auto/sandbox/79/takes/`.
- The Celtic title and town songs (animation item #114) and the boss loop (animation item
  #132) "could also be approved"; they are not recorded as approved.

## Open Questions

- Which way does the wind blow? (It is built left to right; the question was never
  answered.)
- How tall is the bush in front of the front row?
- What vertical bar size do the back rows get? (The approved data is in pixels at scene
  scale.)
