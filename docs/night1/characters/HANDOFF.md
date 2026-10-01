# P2 Characters: handoff (round 11, first-pass piece G: hero skins)

> Fan homage project. Not an official Marvel, Sony or Insomniac game. No affiliation. See `DISCLAIMER.md`.

Branch `night1/characters`, worktree `~/sm2-n1/characters`, UE MCP port 8772, browser dev port 5203. Round 11 author: Sonnet 5.5 (2026-10-01 afternoon; resumed and finished 17:05 - 17:25 after the owner's pause).
Everything is committed and pushed (`origin/night1/characters`); `/Content` is NOT committed (script-generated, rebuilt by `build_fight.sh`, see Commands).
Scope since the director's first-pass plan (`git show origin/Opus-5.5-Loop-Night-1:docs/night1/director/PLAN-firstpass.md`, piece G): **the HERO ONLY**. Thugs, fight, crowd are PAUSED (their rounds 05 - 10 below stay as the record).

## ROUND 12 IN PROGRESS (Opus 5.5, 2026-10-01 evening) - read this first

Round target (critic r11): raised piping on all 8 suits, net / piping layered UNDER the sash and chevron, no faceted patches / weave flip / stair-step at the armpit, Verdant jog <= 2 px, Verdant + Saffron re-blocked, CH1-framed fronts, r8 hero run / chase + enemy lineup + fight + crowd re-shot.

Done and pushed (CPU side, verified on CPU renders and checkers):
- ROOT CAUSE of the jog / stair-step / weave-flip line / faceted patches: a FOLD of the side of the torso in the idle / run poses (neighbouring vertices weighted to different arm bones,
  shoulder 0.12 vs upperArm 0.11). The suit textures are continuous across that UV seam. Fix: `tools/ue_char/suit8/hero_weights_r12.py` smooths the per-joint weights in the
  torso-side region (1650 vertices, positions / UVs / normals untouched); `build_characters.py` 'prep' runs it after `hero_lens_r8.py`; `--check` prints fold counts (idle@0: 4 -> 2 folded faces,
  CPU posed render: the notch is gone).
- `design.py` style `relief` (default `piping`): every panel / net line is a raised rounded cord (heights 0.65 - 0.95 mm, roughness 0.36 / 0.42), sash / chevron border strips raised,
  the accent panel a padded plateau, and every net / piping / stitch line laid after the sash is masked UNDER it (colour + height + roughness); cavity AO at the cord feet; normal map sigma 0.6
  and per-texel smoothed metres-per-texel. `relief.kind = 'r8'` (`hero_suit_r8.py --legacy-r8`) still reproduces round 08 texel for texel; `test_regression.py` checks both (r8 + r12 md5s).
- `M_Char_Suit`: the weave is laid out from the PRE-SKINNED local position (triplanar, whiteout blend, rotated onto the skinned normal, World -> Tangent), static switch `WeaveFromPosition`
  (default on; off = the old UV twill). Unverified in the engine until the build runs.
- `suits.json`: Verdant deep #4b4a22 olive-bronze (no black raglans), upper arm body, glyph `gate` (no ring); Saffron deep #2f3a36 slate, upper arm body, `sleeves: false` (no raglan pair).
  IP guard palette PASS (min palette distance 52.3), seams PASS (worst run 4.3 px).
- `tools/ue_char/suits/tangent_check.py`: normal map vs the mesh tangent frames per UV island (PASS: large islands cos >= 0.99, no island flipped; fingers 0.8).
- Checkers for the critic's numbers: `relief_check_r12.py relief|sash|jog`, `loco_r12.py ch1|bob|pop`. Round-11 baselines: Tessera relief cells >= 20: 32 %, sash longest dark run 46 px,
  Ash 121 px, Verdant jog 69 px.
- Engine side: `chain_r12.sh` (one gpu_slot hold: stills pawn orbit hero chase fight crowd lineup), `post_r12.sh` (fills round-12/ + every measure), `make_pairs_r12.py`.

Next (if you resume here): the content build was queued in the GPU lock (`build_fight.sh clean,tex,mat,mesh,citizens,rename,fightclips,abp,map,maps5,skins,skinsmap`, needs prep outputs:
`python3 tools/ue_char/prep_glbs.py; python3 tools/ue_char/hero_lens_r8.py $P2_SCRATCH/ueimport/SK_Hero.glb; python3 tools/ue_char/suit8/hero_weights_r12.py $P2_SCRATCH/ueimport/SK_Hero.glb`
and the maps: `python3 tools/ue_char/hero_suit_r8.py` (Tessera 8192) + `python3 tools/ue_char/suits/gen_suits.py`), then
`EV=10.0 STEPS="stills pawn orbit" gpu_slot.sh capture --label characters -- bash tools/ue_char/suits/chain_r12.sh $P2_SCRATCH/r12/chainA` and `STEPS="hero chase fight crowd lineup" ... chainB`,
then `bash tools/ue_char/suits/post_r12.sh $P2_SCRATCH/r12/chainA $P2_SCRATCH/r12/chainB`. Check the build log for `M_Char_Suit` compile errors / the weave-from-position line first.

## STATE AT THE END OF ROUND 11 (read this first)

Round 11 is DONE except the blind critic's verdict: all acceptance numbers are in `round-11/SPEC_CHECK.md`, what was captured (and how, at which resolution) in `round-11/CAPTURES.md`, the suits in `round-11/SUITS.md`, the owner's swatch sheet is `round-11/SWATCH_SHEET.jpg`.

| acceptance line (PLAN-firstpass section 4) | result |
|---|---|
| >= 6 ORIGINAL suits from the parameterised Tessera generator | **8** (tessera, verdant, plum, cinder, glacier, ash, saffron, sage); IP guard P1 - P7 pass, min palette distance 47.1, atlases OCR 0 hits |
| in-game swap: key cycle + `wh.Suit`, persisted in WHSettings, <= 0.5 s | T / Shift+T, D-pad Up, console, settings-menu row; real-time 4K swaps 64 - 68 ms (3 frames), 7 of 7 injected T presses visible 2 frames (33 ms) later on the movie pixels; the pawn run ended in verdant, the relaunch and the menu both read verdant from `GameUserSettings.ini` |
| swatch sheet for the owner | `round-11/SWATCH_SHEET.jpg` (front + back + chest of every suit) |
| no seam > 40 px, 4K stills | texture-level seam runs <= 4.6 px; a small stair-step at the left-chest sash end is visible in the 4K chest close-ups (UV island boundary, see CAPTURES) |
| critic pack | `/Users/midir/sm2-n1/_scratch/critic-P2-r11/pack` (17 pairs: 4 full-body, 4 back, 3 chest, 2 head, swatch sheet, swap clip, orbit clip, round-08 Tessera vs round-11 Tessera; key in `pack.key.json` outside it), built from `pairs.json` by `make_pairs_r11.py` + `abpack.py`; no critic verdict yet: IQ >= 6 is the critic's line |

What happened in the resume (2026-10-01 14:40 - 16:00): the owner's GTA V reservation blocked the lock twice (by design, never worked around); the manual-exposure stills of the interrupted chain were BLACK (AEM_Manual = camera EV100 9.9 minus the bias, stage sun 8 lux): measured bias +9 -> floor luma 121, +10 -> 172 (auto exposure's 170). The stage default is now **+10.0** (`build_characters.py`, `skin_ev`) and every run passes `-WHExposure=10.0` (`evidence/exposure_calib.txt`).
`tools/ue_char/suits/chain_r11_final2.sh` is the ONE hold that produces all the evidence (build skins + skinsmap -> [EV calibration] -> 4K stills -> pawn swap movie -> persistence relaunch -> settings-menu shot -> orbit movie; stops after 2 engine crashes; 600 s of lock hold). `tools/ue_char/suits/post_r11.sh <chain dir>` then fills `round-11/` (stills, sheet, clips trimmed, evidence, swap analysis, OCR, `SPEC_CHECK.md`).
The orbit movie of the main chain showed the default pawn of `Char_Skins` as a small dark post on the horizon (its off-stage PlayerStart was 60 m away). **Fixed and re-shot (second hold, 2026-10-01 17:09 - 17:13, 223 s, 0 crashes, instances of mine = 1)**: the start is now 1.8 km away (`build_characters.py`), `STEPS="build orbit" EV=10.0 chain_r11_final2.sh .../r11/chain5`, and the COMMITTED `round-11/orbit_all_suits.mp4` is that re-shot movie (checked on 23 frames by hand, before/after crop in `evidence/orbit_post_removed_before_after.png`; details in `CAPTURES.md` "Orbit note"). The owner's GTA V reservation (15:41 pause) was lifted at 17:05; the lock then granted the hold after a 150 s queue behind other agents.
Round-11 resume checklist (all done): orbit re-shot, `post_r11.sh` re-run (swatch sheet, OCR 1 reviewed hit, swap analysis: unchanged numbers, `SPEC_CHECK.md` regenerated identical), critic pack rebuilt from the final files (17 pairs, `/Users/midir/sm2-n1/_scratch/critic-P2-r11/pack`, key outside it in `pack.key.json`), everything committed and pushed.

### What exists (all verified in the real game this round)

| piece | file |
|---|---|
| generator: Tessera's `paint(..., style)` (DEFAULT_STYLE = Tessera, bit-identical to round 08 at 1024 px: max diff 0, `test_regression.py`) | `tools/ue_char/suit8/design.py` |
| suit list, 8 original styles | `tools/ue_char/suits/suits.json` |
| maps per suit (4096 px, ~45 s each; Tessera 8192 from `hero_suit_r8.py`) | `python3 tools/ue_char/suits/gen_suits.py [--only id] [--hero] [--n 4096]` -> `art/night1/characters/hero/suits/<id>_{basecolor,normal,orm}.png` (git-ignored) |
| IP guard: colour-blocking rules P1-P5, structural + palette uniqueness P6, glyph whitelist P7; OCR of atlases / stills | `tools/ue_char/suits/ip_guard.py palette|ocr` (numbers in `round-11/SPEC_CHECK.md`) |
| UV seam check (spec CH18) | `tools/ue_char/eval/suit_seams.py` |
| CPU design-aid renders / swatch | `tools/ue_char/suits/swatch_cpu.py` (not evidence); engine sheet: `swatch_sheet.py` |
| engine content steps `skins` (textures NeverStream, `MI_HeroSuit_<id>`, `MI_HeroLens_<id>`, data asset `/Game/Characters/Hero/Suits/DA_HeroSuits`) and `skinsmap` (`Char_Skins`, `Char_SkinsPlay`) | `unreal/WebHomage/Scripts/build_characters.py` (end of file) |
| the swap | `Source/WebHomage/Characters/WHHeroSuit.{h,cpp}`: `UWHHeroSuitSubsystem` (UTickableWorldSubsystem): T / Shift+T, gamepad D-pad Up (LB + D-pad Up = back), console `wh.Suit <n|id>` / `wh.SuitNext` / `wh.SuitPrev`, applies to the player pawn's `SpiderSuit` slot (+ `Lens`) and to every other mesh wearing a hero suit |
| persistence | `Core/WHSettings.{h,cpp}`: `SuitIndex`, `SuitId`, `LoadSuit()`, `SaveSuit()`; keys `HeroSuit`, `HeroSuitId` in `GameUserSettings.ini [WebHomage.Settings]`; the in-play swap saves at once; "Reset defaults" keeps the suit |
| settings menu row "Suit" (section HERO) | `Core/WHSettingsMenu.cpp` |
| capture director: `FWHShot.Suit`, `FWHShot.bTargetPlayer`, `-WHExposure=<EV bias>` | `Characters/WHCharShowDirector.*` |
| automation flags | `-WHSuit=<n|id>`, `-WHSuitScript=t:n,...`, `-WHSuitKeyScript=t,...` (real T key through the player controller; a scripted run ignores the GLOBAL macOS Shift state, which leaked in from the owner's other game), `-WHSuitPersist` (see the header of `WHHeroSuit.h`) |
| swap latency on pixels | `tools/ue_char/suits/analyze_swap.py` (colour histogram of the hero's pixels; matches each logged key injection with the first swap step) |
| exposure calibration helper | `tools/ue_char/suits/ev_calib.py` (bare-floor luma, secant search for 170) |

The playable pawn (`AWebTravCharacter`, P3) is NOT edited: its `SetupHeroMesh` still loads `MI_Hero_Suit`; the subsystem re-applies the chosen suit to the player's mesh every frame and scans the world every 0.5 s.
Integration note for the integrator: the module needs no new Build.cs dependency (the suit list is a data asset, not an asset-registry scan). `Core/WHSettingsMenu.cpp` got one section (a `ChoiceRow`); `Core/WHSettings.*` got the two fields + two methods.

## Next steps (priority order)

1. Read the critic verdict for round 11 (`critic/round-11-CRITIC.md` once written) and fix its single biggest gap. Candidates I saw myself: (a) the stair-step at the left-chest sash end of every suit (a UV island boundary of the shared atlas, visible in the 4K chest close-ups: fix by making the sash / net layout continuous across that boundary in `design.py` or by padding the atlas islands). Looked at in the resume (crops of `stills/skin_saffron_chest_4k.jpg` x 1100-1900 / y 1500-2160 and `skin_cinder_chest_4k.jpg` x 1000-2000 / y 1200-2160, the hero's right armpit seen from the front): the cloth weave direction flips across a jagged island edge, the black sash border jumps by ~15 px (3 mm) and there are faint polygon-shaped shade patches in the flat colour (cinder cyan sash); the texture-level seam check cannot see the weave flip or the patches, so the next fix needs (i) the weave UV direction made island-independent (derive the weave coordinates from the 3D position in `M_Char_Suit`, or from a per-island rotation table) and (ii) a check of the normal map (derived from the height map) against the mesh normals at that armpit, (b) the back views are dim (the key sun is in front: add a rim / back fill on the stage), (c) the first suit's 8192 px Tessera maps stream in visibly for ~0.4 s at game start (consider 4096 for Tessera, or touching the textures at subsystem init), (d) `glacier` / `sage` are close to the white end at the fixed exposure.
2. Whole-mesh suits (PLAN: "whole-mesh suits later"): a style can already change colours / patterns only; a different silhouette (cape, collar, gauntlets) needs Blender geometry on the hero rig.
3. Per-suit emissive trim (glow lines) needs an emissive input in `M_Char_Suit` (not built).
4. Hero model / animation items from rounds 08 - 10 (head brow / nose volume, run start / stop / turn) are untouched; the hero-only first pass also owes P3 the section-5 clips of `SPEC.md`.

## Rules that still hold

- ORIGINAL suits only (never an official suit, emblem, web-line pattern or recognisable colour blocking; no image generation for suit art; never write "Spider-Man" or "spider" in a generation prompt). The guard + critic read it every round.
- Every Unreal launch through `gpu_slot.sh` (cap 1), `stop_ue.sh` only, never kill -9 an engine, no listeners, one engine at a time. The lock waits while the owner plays a game: that is by design, not a bug to work around.
- Content is script-generated (`/Content` never committed, no LFS).

## Commands

```
export P2_SCRATCH=/Users/midir/sm2-n1/_scratch/characters UE_WAIT_SKIP=1
python3 tools/ue_char/suits/gen_suits.py --hero --n 4096                    # all suits (CPU, ~6 min); --only cinder for one
python3 tools/ue_char/suits/ip_guard.py palette art/night1/characters/hero/suits OUT.json
python3 tools/ue_char/eval/suit_seams.py art/night1/characters/hero/suits OUT.json
python3 tools/ue_char/suits/swatch_cpu.py art/night1/characters/hero/suits OUT.jpg --views front,three,back   # design aid
unreal/WebHomage/Scripts/build_editor.sh                                    # C++ (close your own editor first)
bash tools/ue_char/fight/build_fight.sh clean,tex,mat,mesh,citizens,rename,fightclips,abp,skins,skinsmap      # content (needs the lock)
python3 tools/ue_char/suits/make_pairs_r11.py docs/night1/characters/round-11 $P2_SCRATCH/../critic-P2-r11/pairs.json
python3 /Users/midir/spider-man-2-astra6/tools/night1/abpack.py /Users/midir/sm2-n1/_scratch/critic-P2-r11/pack /Users/midir/sm2-n1/_scratch/critic-P2-r11/pairs.json
```
Stop an engine only with `/Users/midir/sm2-n1/_scratch/gpu/bin/stop_ue.sh "/Users/midir/sm2-n1/characters"`; count engines with `pgrep -x UnrealEditor`.

## Re-running the evidence (one lock hold, ~10 min, only when the owner is not playing)

```
export P2_SCRATCH=/Users/midir/sm2-n1/_scratch/characters
OUT=$P2_SCRATCH/r11/chain4; mkdir -p $OUT      # a short re-shoot of one part: STEPS="build orbit" (or "stills", "pawn" ...) with EV=10.0 and its own out dir (the orbit used chain5)
EV=10.0 nohup /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label characters -- bash tools/ue_char/suits/chain_r11_final2.sh $OUT > $OUT/gpu_wrapper.log 2>&1 < /dev/null &     # record the PID; STEPS="build orbit" runs a subset; without EV= the chain calibrates the exposure first
# then (CPU): ORBIT_OUT=<dir whose orbit3/ is committed> STILLS=stills_a bash tools/ue_char/suits/post_r11.sh $OUT
python3 tools/ue_char/suits/make_pairs_r11.py docs/night1/characters/round-11 /Users/midir/sm2-n1/_scratch/critic-P2-r11/pairs.json
python3 /Users/midir/spider-man-2-astra6/tools/night1/abpack.py /Users/midir/sm2-n1/_scratch/critic-P2-r11/pack /Users/midir/sm2-n1/_scratch/critic-P2-r11/pairs.json
```
`round-11/evidence/ocr_review.txt` is hand-written (the one OCR false positive); re-check it after a new OCR run.

## Older rounds (hero / enemies / crowd, now paused)

Round 10 numbers (fight clips, hit reactions, knockdowns) and the open items (thug collar wedge, hijab walker shin, hero brow / nose volume, orbit guard hold, hood wisp) are in `round-10/SPEC_CHECK.md` and `critic/round-10-CRITIC.md`. The round-11 hair work of an earlier session
(`tools/ue_char/people/hair.py`, `eval/hair_4k.py`, `crops_r11.py`, `make_pairs_r11.py`... that interim round was superseded by the first-pass plan) is committed but was never rebuilt or captured.
How the fight script works (`tools/ue_char/fight/choreo.py`, `fight_script.json`, `r10_check.py`) is unchanged; commands for it: `git show 69afb4b:docs/night1/characters/HANDOFF.md`.
