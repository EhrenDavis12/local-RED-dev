# Plan: bring annie's approved BattleScene1Full (take F) into Guild Master's Descent

## Findings that shape the plan

1. **The battle has no scene. It is built in code, all in uGUI.** `Assets/Scenes/Boot.unity` is the only scene, and `BuildSettingsTests.BuildSettings_HoldExactlyOneEnabledScene_Boot_Scaffold_Build` requires it to stay that way.
2. **Our battle is already a hand-made uGUI copy of annie's scene.** Earlier queue items rebuilt her lanes, wind, ground blend, SfEffect hit, bars, intro take F, miss and dissolve as RawImage/Image code. The tables in `Tuning.cs`, `BattleBarArt.cs`, `BackdropArt.cs` and `HitFxArt.cs` use her numbers. So this item replaces the drawing layer. It does not add new behaviour.
3. **Every texture the Full scene uses is already in our project, byte for byte (md5 checked), but under different GUIDs.** That covers all meadow lanes, wind masks, M1, G_grass, all 16 archer sheets and arrow_wood.
4. **ArcherVsArcher's materials and textures already sit in `Assets/Resources/Fx/ArrowHit/` with annie's GUIDs and identical bytes.** This includes Mat_SpriteUnlit, the dust, spark, streak and trail materials, and their PNGs. The scene's references to them resolve with nothing copied. Copying ArcherVsArcher again would cause GUID collisions.
5. **The Full scene does not reference ArrowMiss, EnemyDeath, DamageText or BattleScene1Intro.** Of BattleScene1Intro it only uses textures, and we already have those. Our existing ports of those items stay as they are.
6. **The cave (annie item 27) has no Unity scene in annie's project.** Our `Assets/Resources/Backdrops/Cave/{WALL3_C, FL_F, WALL3_C_join, STAL_A3_strip, CEIL_B}.png` are md5-identical to her approved files in `local_runs/scenes/battle2/{wall2,floor,stalactites,ceiling}/`. The numbers in `BackdropArt.Cave` come from `stal_render.py`. We already have the cave.
7. **SfDirector is not a timeline.** It replays a precomputed plan, one tick per frame at 48 ticks a second. The plan is made offline by `plan.py`: kind, frame, ox, hp, mp and nudge for every figure and tick, plus 33 fixed shots.
   - What can be reused: its geometry (`scene.json`), the bar drawing, the bar placement and nudge, and the per-tick shot loop driving SfEffect.
   - What cannot: its per-tick arrays.
8. **Where the bar placement lives.** It is not in `Mat_full_bar.mat`; that is only BsUnlit with a placeholder texture. Each figure's box comes from `plan.bars[i]` (x0, y0, W, Hh, cw), drawn at runtime by `SfDirector.DrawBar`.
   - The source of those numbers is `local_runs/unity/battle_scene1_full/plan/bars.json`. It adds `D_hit`/`D_attack` per figure (34 to 45 and 16 to 22 px), `MINFILL 7`, `EASE 12`, and the colours SEP (74,46,26), PAPER (236,222,190), RED (214,38,38), BLUE (52,120,235).
   - For figure 0, x1 = 97 against feet x 170, and y1 = 471 against feet y 532. Our `GapPx 72` and `BottomPx 61` already match.
   - Nudge timing in plan.py: up over 6 ticks with smoothstep, hold to tick 48 of the 60-tick clip, back down over 12 ticks. Ours is 5 up and 10 down, so it changes to annie's.
9. **Colour space differs.** Annie's project is Linear and ours is Gamma (`m_ActiveColorSpace` 1 vs 0). See question 2.
10. **Phone memory rules out annie's texture import.** She imports as RGBA32 uncompressed with no mips. `CharacterArtImporter` notes the Archer alone would take about 1.25 GiB uncompressed on iPhone. So the copied materials must point at our textures, which import as ASTC on iPhone with mips.

## 1. How the battle is drawn now, and what changes

**Entry points:**
- `HallRoomScreen` (demo button) and `DiveScreen` call `BattleScreen.Build(camera, controller, …, backdrop)`.
- `BattleScreen` (Game/Battle) is a Screen Space - Camera canvas on the Boot perspective camera.
- `BattleScreen.Tick(dt)` → `BattleController.Advance` (Core) → `ActionReport` → `TurnPlayback` → per-event Start/Land.

**Views:**
- `BattleBackdropView`: RawImage lanes using our UI ports of WwWind and GbMix.
- `CombatantView` (×30): art Images, three uGUI bars, nudge, focus/highlight/tint, taps, dissolve.
- `BattleFx`: `ArrowHitFx`, a uGUI port of SfEffect with `FxSim`, and `ArrowMissFx`.
- `HitNumbers`, `DeathDissolve`, `ResultScroll`, `BattleIntro` (take F, Core).

**Replaced (drawing only):**
- `BattleBackdropView` → annie's 15 lane quads, wind and ground blend. The cave gets BsUnlit quads built from `BackdropArt.Cave`.
- The art Images in `CombatantView` → annie's body/weapon quads.
- The uGUI bars → annie's DrawBar quads, plus our white stamina column.
- `ArrowHitFx` → annie's 10-slot SfEffect pool.

**Kept:**
- All of `BattleScreen`, `BattleController`, `TurnPlayback`, `BattleIntro`, the clip choice and idle mix in `CombatantView`, and the ShownHealth/cooldown/special state. `CombatantView` stays the model; the stage reads from it.
- Also kept: `HitNumbers`, `ArrowMissFx`, the `DeathDissolve` for still-art deaths, taps, focus marker, Special button, header and result scroll.

## 2. Import approach

I recommend copying annie's `.unity`, materials, shaders, scripts and data with their `.meta` files (GUIDs kept). A one-time editor converter then saves her `BattleScene1` root as a prefab, `Assets/Resources/Battle/BattleStage.prefab`. Our new `BattleStage` component, which takes SfDirector's place, drives it from combat events.

Why: her real objects arrive unchanged, with every sort order, particle module, trail, layer toggle and value. No build-settings change is needed, so the Boot-only test stays. And the `.unity` stays in the project as the reference copy that tests pin.

Additive scene loading was rejected because it breaks the build-settings rule. Rebuilding the scene from data was rejected because it re-creates her work.

## 3. URP → built-in

Results of scanning every GUID in the scene and its materials:
- **No URP package shaders are referenced.** No Sprite-Lit-Default and no URP Unlit.
- **No Volume, post-processing, 2D Renderer data or UniversalAdditionalCameraData.** The 35 MonoBehaviours are SfDirector, WwWind, GbPatternSwitch, AnnieCapture, 10 SfEffect, 10 Light2D and 11 AnnieLayers.
- **Sorting is fine:** Default sorting layer only.

| URP dependency | Where | Built-in replacement |
|---|---|---|
| `Annie/BsUnlit` (GUID af5f0561…) | lanes, bodies, weapons, bars | Port in place, keeping the file and `.meta` GUID (see the edits below) |
| `Annie/WwWind` (5d9420b0…) | 5 wind lanes | Same port. Texture samples become `tex2Dgrad`/`tex2D` |
| `Annie/GbMix` (4b0dcea7…) | L11 ground | Same port, plus the `UNITY_COLORSPACE_GAMMA` linear lerp block copied from our `Assets/Resources/Shaders/GbMix.shader` (the earlier approved Gamma fix) |
| Light2D ×10 (`L6_Light` in each Fx_Spark; script 073797af… in the URP package) | SfEffect.light2d | Remove it. It has no visible effect: every renderer in the scene uses BsUnlit or Sprites/Default, which are unlit, so a 2D light changes no pixel. The converter strips the missing scripts. Our SfEffect copy drops the field, the `using UnityEngine.Rendering.Universal;` line, and the three `light2d` blocks in HideAll, Impact and Post |
| `Unity.RenderPipelines.Universal.2D.Runtime` in `Annie.BattleScene1Full.asmdef` | asmdef | Delete that reference |
| Sprites/Default (builtin fileID 10753, guid 0000…f000…) | particle and sprite materials | Exists in built-in. No change |

**Shader edits, the same in all three shaders:**
- Drop `"RenderPipeline"="UniversalPipeline"`. With that tag, built-in skips the SubShader and draws pink.
- `HLSLPROGRAM`/`ENDHLSL` → `CGPROGRAM`/`ENDCG`.
- Include `UnityCG.cginc` instead of the URP `Core.hlsl`.
- `TEXTURE2D(x); SAMPLER(sampler_x);` → `sampler2D x;`, and `SAMPLE_TEXTURE2D(_GRAD)` → `tex2D` / `tex2Dgrad`.
- Delete `CBUFFER_START/END`.
- `TransformObjectToHClip(p)` → `UnityObjectToClipPos(p)`.

**One forced shader change, for a screen wider than 16:9 (see question 1).**
- Pass world x from the vertex shader: `o.wx = mul(unity_ObjectToWorld, i.pos).x`.
- In scroll mode, use `(_Off + i.wx) / _LaneW` instead of `(_Off + i.uv.x*1920.0) / _LaneW`.
- In WwWind, use `pu = (i.wx - _WwSpeed*_WwT)/1920.0`.
- On a 1920-wide quad at x 0..1920, `i.wx == i.uv.x*1920` exactly, so 16:9 output is unchanged.

**Remapping the GUIDs.** These are not URP GUIDs; they are annie's texture GUIDs, which do not exist in our project. Do a text replace of the old GUID with ours in the copied `.mat` files and in the copied `.unity` (for `SfDirector.arrowTex`). All targets are under `Assets/Resources/`.

```
04212efbbdef34728ab6564cd56e55e0 -> a5303832823714174be0e89b31a59247  L14_planted_trees
202d24bda8d404cfd927aebe6379beac -> 119fbe3b0574d4be79b2678026ebb2f1  run_stop_body_forest
299a4bd7890ed4abd8de3bb807c7ca3e -> 4746215aec41b4c9ba15185e20e18475  arrow_wood (-> Fx/ArrowHit)
2c9c76ff4843f4b27b1399e3a485b9dc -> cc464dfbb42274752828b7b3b468e865  L04_clouds_near
2e06fb7e69210485a8283bef82fc5e79 -> 8ff32dddb37bd46babfd645dccfa2b9e  L08_trees_far
374206a55054e4463985d0c4cdce9900 -> 53350b455368847d2872591373f046ff  robes_death_weapon_wood
3d115134dbf3947c195568322653d53a -> 25edc0d2c2be348348faf296d685ed3d  idle_body_forest
4235b66d756994f0bac8fb332866ac64 -> fe02f0c8896c244faaf4295d2d5821ca  robes_run_weapon_wood
462b3780917ec46b48287e723c24436f -> 4cbe8c8a0230e4d7098ab29234aa1fee  L09_trees_mid
46569b4f0b8e548efbfb773297050bee -> 9dbdb53c774f64091a06e5b89ac62de4  run_body_forest
4906e0530af0945feaf1ea8fd4208c78 -> 690b2b2472d684e8e9dd0c4ee5e58e2b  L11_ground
5a7bfb94ea19045e4b49b071daab3f1e -> c0211a8ca78864dcf9751ecd491932b6  L06_mountains_front
5b8db9fe460a344998f7cec4095865f7 -> 27b4aaf66afc74b49b647ab5bdbd9d29  M_L17_clumps
61b9f0a9f1e3d494688c3cbe792a80f3 -> 50a2e6bbcec8f41da8c449f391bc3099  L17_clumps
61ca4aa2ce534498c839aa1629705cf9 -> 6c8065949e41144f08bffade93444dac  idle_headturn_body_forest
6260647a7d964452f8ad66b40907c40a -> ca85118bb13b845d2a2aba9333a3745a  M1_patches
6aab56061f015444daf76d9cb139467c -> a8ebdc8f9bc8a468195bdd058b028c8e  robes_idle_weapon_wood
6bac5b05def5248dcbbebacff056abab -> cc967ae358838468aa5c6c3cbc495870  death_body_forest
75d2fb26fdbaa46719fe756319ed928c -> 62ceb769c273e4f96bdd3fae48099a06  hit_spark_sheet (-> Fx/ArrowHit)
76b0eb4417aac43ff9859c44cda3d639 -> f7a216749c65740a5af9281607c2ffc5  L12_ground_haze
77363e4df6270407397f5992c57134c6 -> e9c159e5293654e239ad448de8e2da37  G_grass
775ac88197cb74bba93b07708ee13db1 -> a36b0bacb755f48bfa9126f7f2ace5be  L07_hills
7a1f1954a863f41b68df1f92127246a6 -> d9ec272c74d5544029dba754612be522  L01_sky
85081816e357f43c7aced69180c6ba56 -> 1893de4b7779c41aea33da75cab7f3b6  idle_shift_body_forest
8c01ec8db665941e0a856c5630458366 -> ba89cf95d326e449d8b14bdf073972fa  L03_clouds_mid
8da7b4ef89f3141c284dc636a72d0a68 -> 13e17a309105a4f208d8e20738f902e5  L05_mountains_back
8ef48552aac5f46889364b222e27dfca -> f3138bfee990f4cd3969a7561580cdca  robes_idle_shift_weapon_wood
917f4e25ad7de40b6ba2c3b48c0073e0 -> 08e606907afa24fdfa389c3a86128041  L13_k2_band
9e9631cb5b2b74d0cad3f537566bd0ff -> 3877c15814eaf4cb883c3adfc956a5d8  robes_attack_weapon_wood
a5cc3d2af1b1b4f7784f832a9afa760b -> d5852dc8540a447e588a711a6bd0632f  robes_run_stop_weapon_wood
a7dbcaf0e0eed437f92fa3ba7a738bb0 -> 1df5df5fe14eb4e629e6acb6278c938a  attack_body_forest
aa711b82e7e9e446cbd813e2e4510a2a -> cbeb205ec058947b9ba3390bd1d11ad9  P_wind
b4f786e8b996148e9ab5a59ef40ea41b -> f2ff5de5fc91e45f6818d91f308eba70  L02_clouds_far
b53e3196dc51742a68738bbfc903dbcf -> eaca8ce965ce94024b24e1ac86fea7a4  M_L10_trees_near
bd320e7c39bc142a5b8c571fba6fb67d -> a0f296c1fd99a449ea6a5d87b0baf2e1  M_L13_k2_band
c6df6e25659024688bc75a13e3440e56 -> 4654ea4db3995454e9020ad786b75fde  robes_hit_weapon_wood
cbfe6a4c7d6b04025bd05433ec04efc4 -> fd1cd2a94616c4d4c9a6ef7c18c65644  L15_bushes
dd08edcebdc004daf9d65ee91321871a -> 1de28d46350464230af1f1ee435adc28  hit_body_forest
e28b580d7dc0b49a6987ba3361d92a27 -> 52b6127c0dc9b446aafcf75ab7aaf2f6  M_L15_bushes
fa259f2ff25804c249a9bf16a6f8cf65 -> d94b3cac041f04ba1aeab6d999a5a69a  M_L14_planted_trees
fa4cacaf5ef83457f9e41b021f60f889 -> 84f671d54e8394b469ae7465331f8937  L10_trees_near
fe3b91057ec334b0d8b5346e1da23991 -> 870f8a9181c8a471fa48d88d93b03950  robes_idle_headturn_weapon_wood
```

In the copied `.unity`, set GbPatternSwitch `m2` and `m3` (badce3d8…, 67e603fd…) to `{fileID: 0}`. Those textures are not copied, and the pattern is fixed at M1.

## 4. Asmdefs and namespaces

Copy annie's four asmdefs unchanged, except for deleting the URP reference: `Annie.Shared`, `Annie.BattleScene1Wind`, `Annie.BattleScene1GroundBlend` and `Annie.BattleScene1Full`. Keep her namespaces.

The scene binds scripts by `.cs.meta` GUID and serialized field name. Folding the scripts into `GuildMastersDescent.Game` would risk those bindings for no gain.

Then add `"Annie.Shared", "Annie.BattleScene1Wind", "Annie.BattleScene1GroundBlend", "Annie.BattleScene1Full"` to the references of:
- `GuildMastersDescent.Game.asmdef`
- `GuildMastersDescent.Editor.asmdef`
- `GuildMastersDescent.Tests.EditMode.asmdef`

Core stays engine-free, so `CoreAssemblyTests` still holds.

## 5. Driving her director from our combat events

**New `Assets/Scripts/Game/Battle/BattleStage.cs`.** A MonoBehaviour on the prefab root, in place of SfDirector, with SfDirector's serialized fields copied over by the converter: `sceneJson`, `laneRenderers`, `laneNames`, `bodyR`, `weaponR`, `bodyMats`, `weaponMats`, `cols`, `cell`, `pool`, `barR`, `rowBase`, `kRow`, `arrowTex`, plus a new `barsJson`.

**Reused verbatim from SfDirector**, each with a source comment:
- the `SfFig`/`SfSceneData` types (used directly from `Annie.BattleScene1Full`);
- `PlaceQuad`;
- the `n`/`oy` rounding;
- the `CellRect` maths, generalised to any `ArtClip` (cell from `clip.CellSize`, sheet size from the texture);
- `DrawBar`;
- the bar placement and nudge (`x0 ± nd`);
- the whole `Shots` loop: slot `q % pool.Length`, `slotOwner` stale check, 30 fps step mapping `(8n+phi)/5 + t_spawn <= T`, `PlaceFlight` every tick at `STEP = 2000/48`, `ArrowLenPx = 410*ka`, `aScale = 100*490/arrowTex.width*ka`, arrow order `max(rowS,rowT)+60`, `kEff = 100*kRow[target]`, `Begin(... rowT+50, arrowOrder)`.

**SfEffect is reused as is**, apart from the Light2D removal. One change is forced by our edit-mode tests and screenshot harness, which never call Awake: move the Awake body into `public void EnsureInit()` (idempotent), have Awake call it, and have BattleStage call it on every pool slot after it instantiates the prefab.

**Clock.** `BattleStage.Advance(dt)` adds up time and runs whole 48 Hz ticks. Each tick runs `Shots`, the bar fill ease and the nudge. When `!Application.isPlaying`, it also calls `ParticleSystem.Simulate(1/48f, true, false)` on playing systems.

**Wind.** WwWind and GbPatternSwitch run on a frame clock, so the converter disables them and BattleStage applies their data itself:
- Wind: per-lane `_Peak` = `peakB` (take 2) via MaterialPropertyBlock, using Get then Set so `_Off` is kept. Each tick sets the globals `_WwT` to our wind seconds and `_WwSpeed` to `wind.speedPxPerSec` (240).
- Ground: `_MaskTex = m1`, `_MaskMul 1`, `_MaskAdd 0` via MaterialPropertyBlock on the ground renderer. These are the values GbPatternSwitch's M1 branch sets. The material asset itself holds "Off" (Mul 0, Add 1).

**Hooks BattleScreen calls:**
- `ShowBackdrop(backdropSeconds, windSeconds)`: lane `_Off` = `BackdropArt.OffsetAt(layer by laneName, s)`, skipping `L12_ground_haze` as SfDirector does. At `StillSeconds` 13.1 this gives annie's rest offsets exactly: 1038.6, 1091, 1169.6×3, 1903.2, 2217.6, 2689.2, 3160.8, 264, 0, 264, 264, 264, 1207.2.
- `SyncFigures(slots)`, every frame. Per view:
  - Figure index `i = Column*6 + (Party?0:3) + (2-Row)` (annie row = 5 − Column, annie col = 2 − Row).
  - Clip and frame come from the view. Flip when the side is Monsters.
  - The intro offset is turned back into frame px and rounded to whole px, the way annie's `ox` is.
  - Material: annie's `bodyMats`/`weaponMats` entry that already holds the texture (the archer), or else one cached BsUnlit material per texture (our ready stills, defend).
  - Hide the quads for an empty node, a placeholder, or a node that is dissolving (the uGUI dissolve draws those).
- Bars, per view:
  - Fill: `hp = round(inner*health/max)`, never less than 7 while above 0. `mp` = special fill. Both eased over 12 ticks with `cur + (v-cur)*(1-(1-x)^2)`.
  - Fatal hit: the bar is gone by +11 ticks.
  - Nudge: `D_hit`/`D_attack` from bars.json, rising `(u+1)/6` with smoothstep and falling over the clip's last 12 ticks.
- Stamina column (our addition):
  - It joins on the left of annie's box, sharing its separator: inner width `max(2, round(2*cw/6))` px, empty SEP, fill white, rising from the bottom.
  - The texture widens to `W + s + 1`, and `x0` moves left by `s + 1`.
  - Annie's red and blue columns keep their exact x on both sides. For monsters the stamina column sits in the 10 to 20 px gap next to the figure.
- `Shoot(attacker, target, startTick)`: computes the shot with Core `StageShot` (below) and claims a slot.

**Core additions (pure C#):**
- `Core/Art/StageArt.cs`: AX 247, AY 431, grip (391.312, 211.736), anch (300, 238), arrow length 410, STEP, spawn delay 6 ticks, EASE 12, MINFILL 7.
- `Core/BattleView/StageShot.cs`: a port of plan.py `geom` and the export's A/phi search:
  - `G = to_screen(shooter, GRIP)`, `P = to_screen(target, ANCH)`;
  - `L = ceil((D - Lc/2)/STEP)`, `t_hit = t_spawn + L`;
  - best `(A, phi)` with `(8A+phi)//5 == L`;
  - also exposes `HitSeconds`.
- In `BattleScreen.PlanEvents`, an arrow hit's `LandAt` = `i*window + StageShot.HitSeconds`, so the number and the bar drop land on annie's impact step. `StartEvent` calls `_stage.Shoot` instead of `_fx.ShootHit`, keeping `ShootMiss`.

**Camera:**
- `BattleStage.Build(Camera ui, BattleBackdrop which)` loads the prefab and puts it on the new layer `BattleStage` (index 8 in TagManager, set recursively).
- It creates `BattleStageCamera`: ortho, near 0.1, far 100, at (960, −540, −10), clear SolidColor black (annie's values), `depth = ui.depth - 1`, `targetTexture = ui.targetTexture`, culling mask only the BattleStage layer.
- The UI camera excludes that layer and is set to `CameraClearFlags.Depth` while the battle is up. `OnDestroy` puts it back.
- Ortho size: `540` when the aspect is at least 16:9, else `960/aspect`.
- Lane quads (sky and haze included) widen to `1080*aspect`, still centred on 960.

**Cave.** Hide the meadow lane, wind and pattern objects. Build one BsUnlit quad per `BackdropArt.Cave` layer:
- `_Scroll 1`, `_LaneW 3840`, texture through `ArtTextures`;
- top at `-Y0`, height `Rows`;
- sorting orders 1000 to 5000, all behind the figures at 16100 and above.

**Layout.** This follows from question 1's default. In `BattleLayout.FrameScale`, `Math.Max` becomes `Math.Min` (fit to height), and `Tuning.BattleFormationFit` becomes 1.0. `BackdropField` becomes height-fit to match, so taps, hit numbers and miss arcs line up with the stage.

**Hiding the uGUI drawing.** Each `CombatantView` gets a CanvasGroup with alpha 0 over its art (unless it is a placeholder or dissolving) and over its bars. Its state, sprites and the existing tests stay in place.

**Release order on destroy:** stage instance, camera, runtime materials and bar textures first; then `CharacterSheets` and `ArtTextures`.

## 6. Tests to pin first (forge-test-author)

1. **Copied assets:**
   - Every `.mat` under `Assets/Annie/**` and in the prefab has `shader.isSupported` and a shader name in {`Annie/BsUnlit`, `Annie/WwWind`, `Annie/GbMix`, `Sprites/Default`}.
   - No copied shader contains `UniversalPipeline` or `com.unity.render-pipelines`.
   - Every texture slot is non-null except GbPatternSwitch m2 and m3.
   - No `.mat`, `.unity` or prefab references a GUID that `AssetDatabase.GUIDToAssetPath` cannot resolve. This uses a regex over the YAML and ignores the 0000… builtins.
2. **Prefab:**
   - No missing scripts anywhere (`GameObjectUtility.GetMonoBehavioursWithMissingScriptCount == 0`).
   - No AnnieCapture and no SfDirector. One BattleStage with 30 bodyR, 30 weaponR, 30 barR, 10 pool, 15 lanes.
   - Sort orders unchanged: bars 30000, body `16100+(5-row)*100+2j`.
   - Everything on the BattleStage layer.
   - No PNG under `Assets/Annie/`.
3. **Fidelity numbers:**
   - The bar boxes BattleStage places equal `full_plan_f.json` `bars[i]` for all 30 figures (x0, y0, W, Hh), with stamina adding `s+1` on the left.
   - Nudge sequence for figure 3 hit at tick 651 equals the plan: 3, 9, 17, 25, 31, 34… held to tick 698, then 33, 31, 29, 25, 21, 17, 13, 9, 5, 3, 1, 0.
   - HP ease for the same hit equals 59, 57, 54, 52, 50, 49, 47, 46, 45, 45, 44.
   - `StageShot` for every one of the 33 plan shots reproduces G, P, t_hit − t_spawn, A and phi.
   - The figure index map matches scene.json side, row and col for all 30.
   - Lane offsets at `StillSeconds` equal `laneOff[400]`.
4. **Wiring:**
   - After a hit report, the target figure's quad shows the hurt clip.
   - The bar texture's red height steps down and its x moves outward.
   - A pool slot goes busy, then hides after A+70 steps.
   - A miss still goes through `ArrowMissFx`.
   - The dead keep their last frame.
   - The UI camera's clear flags are restored on destroy.
   - At 16:9, 19.5:9 and 21:9, a figure's feet projected through the stage camera land within 1 px of its `ReferenceBounds` feet through the canvas.
5. **Shaders:** a BsUnlit quad 0..1920 at `_Off` X renders the same as the original uv formula. The existing `BackdropShaderBehaviourTests` style applies.

Existing tests that pin 0.82, cover fit, Rise 5/Fall 10, the uGUI bar visibility or `BattleBackdropView` through `BattleScreen` need updating. These are in `BattleLayoutTests`, `BattleLayoutFrameTests`, `BattleBarsViewTests`, `BattleScreenBackdropMotionTests` and `TuningTests`. The baseline is 4123 passing (`test-results.xml`).

## 7. Checking by eye

**Running things:**
- Tests: `/Users/ehrendavis/.unity/bin/unity test /Users/ehrendavis/work/local-RED-dev-2/src/guildmasters-descent --mode EditMode --output test-results.xml` (add `--filter Stage` for the new ones).
- The converter, once copied: `unity run <project> -- -executeMethod GuildMastersDescent.EditorTools.BattleStageImporter.Build`
- Shots: `unity run <project> -- -executeMethod GuildMastersDescent.EditorTools.BattleScreenshot.Capture -shotPath Screenshots/battle.png`
- Both run in batch edit mode, so the project must not be open in an Editor.

**Harness change.** `BattleScreenshot.SaveAs` must call `Render()` on every `BattleStageCamera` whose target is `studio.Target` before `studio.Camera.Render()`. Add `CaptureStageCompare`:
- **1920×1080 shot, `stage-f0400.png`.** An Editor-only 15-v-15 all-Archer battle, no intro, backdrop at rest, `_WwT = (400-108)/48 = 6.083` (annie's `windShift`). Put it side by side with take1f `frames/f0400.png` and write a diff.
  - The sky and mountain band (y < 340) should match to within gamma edge differences.
  - Figure poses differ, because the idles are random.
- **`stage-cave.png`.** The same at 1920×1080, beside `local_runs/scenes/battle2/preview/stal_TEST_still.png`.
- **`stage-bars-crop.png`.** A 1:1 crop of the left army (x 0..800, y 340..1080) with hand-set health and special that differs per figure. Beside the same crop of take1f `frames/f0702.png` and `hud_bars/round4/compare_phone.png` panels 1/5/11.
- **`battle-*.png`** at 2532×1170 and 2520×1080 (21:9), regenerated. The current `Screenshots/battle-03-hit.png` is stale and still shows placeholders and old buttons.

Use the `playtest` skill for the in-game look on the simulator: trails and particles in real time. Edit-mode `Simulate` approximates those.

## 8. Slices, in order (each fits one writer dispatch)

**S1. Copy and convert.** Copy into `/Users/ehrendavis/work/local-RED-dev-2/src/guildmasters-descent/Assets/Annie/`, with `.meta` files and the same subpaths, from `.../sideScrollerBattles/Assets/Annie/`:
- `Shared/{Annie.Shared.asmdef, AnnieLayers.cs, AnnieCapture.cs}`
- `BattleScene1/Shaders/BsUnlit.shader`, `BattleScene1/Data/scene.json`, and `BattleScene1/Materials/Mat_{L01_sky, L02_clouds_far, L03_clouds_mid, L04_clouds_near, L05_mountains_back, L06_mountains_front, L07_hills, L08_trees_far, L09_trees_mid, L12_ground_haze, arrow_wood, hit_spark}.mat`
- `BattleScene1Wind/{Runtime/Annie.BattleScene1Wind.asmdef, Runtime/WwWind.cs, Shaders/WwWind.shader}` and `BattleScene1Wind/Materials/Mat_{L10_trees_near, L13_k2_band, L14_planted_trees, L15_bushes, L17_clumps}_wind.mat`
- `BattleScene1GroundBlend/{Runtime/Annie.BattleScene1GroundBlend.asmdef, Runtime/GbPatternSwitch.cs, Shaders/GbMix.shader, Materials/Mat_L11_ground_blend.mat}`
- `BattleScene1Full/{Runtime/*.asmdef, Runtime/SfDirector.cs, Runtime/SfEffect.cs, Materials/*.mat (17), Data/full_plan_f.json, Scenes/BattleScene1Full.unity}`
- Plus `/Users/ehrendavis/work/local-RED-dev/src/asset-animation-demo/local_runs/unity/battle_scene1_full/plan/bars.json` → `Assets/Annie/BattleScene1Full/Data/bars.json`

Then:
- Apply the GUID table and the m2/m3 nulling.
- Port the three shaders.
- Make the SfEffect edits (Light2D removal, EnsureInit) and the asmdef edits.
- Add the TagManager layer `BattleStage` at index 8.
- Write the editor converter `Assets/Scripts/Editor/BattleStageImporter.cs`:
  1. Open the scene additively.
  2. On the `BattleScene1` root: strip missing scripts and AnnieCapture.
  3. Add BattleStage and copy the SfDirector fields over by name; set `barsJson`; destroy SfDirector.
  4. Disable WwWind and GbPatternSwitch.
  5. Set the layer recursively.
  6. `PrefabUtility.SaveAsPrefabAsset` → `Assets/Resources/Battle/BattleStage.prefab`.
  7. Close the scene without saving.

At this point BattleStage only has fields plus `EnsureInit` on the pool.

*Done when:* the project compiles; the converter runs; tests 6.1 and 6.2 pass; all 4123 old tests pass.

**S2. Core.** `StageArt`, `StageShot`, the figure index map, the layout change to height-fit and fit 1.0, and nudge 6/12. *Done when:* tests 6.3 pass and the updated layout tests pass.

**S3. Stage backdrop and camera.** `BattleStage.Build`, the camera, lane widening, `ShowBackdrop`, wind and ground values, the cave quads, `BattleScreen` building the stage instead of `BattleBackdropView`, and the harness render change. *Done when:* `stage-f0400.png` backdrop matches (7) and `stage-cave.png` looks right.

**S4. Figures and bars.** `SyncFigures`, the CanvasGroup hiding, DrawBar with the stamina column, the ease, the nudge, and release. *Done when:* the bar tests in 6.3 and 6.4 pass, and the bar crop looks right.

**S5. Arrow hits.** `Shoot`, the pool, the `PlanEvents` LandAt change, edit-mode Simulate. `ShootHit` and `ArrowHitFx` are no longer used for hits. *Done when:* the hit wiring tests in 6.4 pass and `battle-03-hit.png` shows annie's flash, ring and sparks.

**S6. Tidy and evidence.** Delete code that is now dead (`BattleBackdropView`, `ArrowHitFx`, `FxSim` and `FxTrailGraphic` if nothing references them), regenerate every screenshot, write the side-by-sides. *Done when:* the full suite is green and the comparison PNGs are in `Screenshots/`.

## Every change forced on annie's copy

- Shader ports to built-in, plus the world-x scroll.
- The Gamma linear-lerp in GbMix.
- Light2D removed.
- AnnieCapture removed. It has `autoStart: 1` in the scene and would record frames.
- SfDirector replaced by BattleStage, using the event clock instead of her plan.
- WwWind and GbPatternSwitch disabled, their values applied by BattleStage.
- `SfEffect.EnsureInit`.
- Textures pointed at ours, which are ASTC with mips on iPhone; hers are RGBA32 with no mips.
- Stage on its own layer and camera.
- Lanes widened past 1920 on wide screens, with the 1920-wide sky stretched. It is a plain gradient.
- Stamina column added.
- uGUI still draws misses, dissolves, numbers and placeholders over the stage, so a dissolving or missed arrow on a back row draws above nearer figures.

## Questions for the user (with the default I'd take)

1. **How the phone frame fits.** Default: show annie's full 1080-high frame, fitting to height, with the lanes extended sideways. That is her exact positions and sizes, with fit 1.0. It replaces item 75's approved fit 0.82, which crops the sky and squeezes the formation. On 21:9, the M1 ground mask's wrap could show in the leftmost ~36 px. The alternative keeps 0.82 and scales every one of her coordinates instead.
2. **Colour space.** Default: keep Gamma, with GbMix compensated. Alpha edges and particles will blend slightly differently from her Linear video. Switching to Linear would change every One Rod menu screen.
3. **Bars at full health.** Annie draws nothing at full health. Default: keep ours always visible while the fighter is alive, because players need to read stamina and special.
4. **Dimming the dead.** Default: follow annie, so a dead archer holds frame 39 with no dimming.

### Critical Files for Implementation
- /Users/ehrendavis/work/local-RED-dev/src/unity-side-scroler/sideScrollerBattles/Assets/Annie/BattleScene1Full/Runtime/SfDirector.cs
- /Users/ehrendavis/work/local-RED-dev/src/unity-side-scroler/sideScrollerBattles/Assets/Annie/BattleScene1Full/Runtime/SfEffect.cs
- /Users/ehrendavis/work/local-RED-dev-2/src/guildmasters-descent/Assets/Scripts/Game/Battle/BattleScreen.cs
- /Users/ehrendavis/work/local-RED-dev-2/src/guildmasters-descent/Assets/Scripts/Game/Battle/CombatantView.cs
- /Users/ehrendavis/work/local-RED-dev-2/src/guildmasters-descent/Assets/Scripts/Core/BattleView/BattleLayout.cs
- /Users/ehrendavis/work/local-RED-dev-2/src/guildmasters-descent/Assets/Scripts/Editor/BattleScreenshot.cs