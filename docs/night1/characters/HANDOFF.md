# P2 Characters: handoff (round 11, first-pass piece G: hero skins)

> Fan homage project. Not an official Marvel, Sony or Insomniac game. No affiliation. See `DISCLAIMER.md`.

Branch `night1/characters`, worktree `~/sm2-n1/characters`, UE MCP port 8772, browser dev port 5203. Round 11 author: Sonnet 5.5 (2026-10-01 afternoon).
Everything is committed and pushed (`origin/night1/characters`); `/Content` is NOT committed (script-generated, rebuilt by `tools/ue_char/suits/chain_r11.sh` / `build_fight.sh`, see Commands).
Scope since the director's first-pass plan (`git show origin/Opus-5.5-Loop-Night-1:docs/night1/director/PLAN-firstpass.md`, piece G): **the HERO ONLY**. Thugs, fight, crowd are PAUSED (their rounds 05 - 10 below stay as the record).

## STATE AT THE END OF THIS ROUND (read this first)

**Status line is in `round-11/CAPTURES.md`** (what was actually captured and what was not). If `round-11/stills/` or `round-11/swap_pawn_T_key.mp4` are missing, the engine chain did not run: the GPU lock refuses launches while the owner plays a game (log `gpu-unhealthy-wait ... owner game running (CrossOver) ... GTA5.exe`) or while `PAUSED` exists. Then run, from the worktree:

```
export P2_SCRATCH=/Users/midir/sm2-n1/_scratch/characters
OUT=$P2_SCRATCH/r11/chain; mkdir -p $OUT
nohup /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label characters -- bash tools/ue_char/suits/chain_r11.sh $OUT > $OUT/gpu_wrapper.log 2>&1 < /dev/null &     # record the PID
```
One lock hold (<= 40 min): rebuild of /Game/Characters (+ suits + `Char_Skins` + `Char_SkinsPlay`) -> 4K stills of 8 suits x 4 views -> playable-pawn swap movie (7 real T presses) -> persistence re-launch -> settings-menu shot -> orbit movie.
`STEPS="stills pawn"` etc. selects steps; each step skips itself when the hold is nearly used up (CHAIN_LIMIT_S). After it: the post-processing list at the end of this file.

### What exists (all CPU-verified; the engine side is compiled but its first run is the chain above)

| piece | file |
|---|---|
| generator: Tessera's `paint(..., style)` (DEFAULT_STYLE = Tessera, bit-identical to round 08 at 1024 px: max diff 0) | `tools/ue_char/suit8/design.py` |
| suit list, 8 original styles | `tools/ue_char/suits/suits.json` (tessera, verdant, plum, cinder, glacier, ash, saffron, sage) |
| maps per suit (4096 px, ~45 s each; Tessera 8192 from `hero_suit_r8.py`) | `python3 tools/ue_char/suits/gen_suits.py [--only id] [--hero] [--n 4096]` -> `art/night1/characters/hero/suits/<id>_{basecolor,normal,orm}.png` (git-ignored) |
| IP guard: colour-blocking rules P1-P5, structural + palette uniqueness P6, glyph whitelist P7; OCR of atlases / stills | `tools/ue_char/suits/ip_guard.py palette|ocr` (numbers in `round-11/SPEC_CHECK.md`) |
| UV seam check (spec CH18, "no seam > 40 px at 4K") | `tools/ue_char/eval/suit_seams.py` |
| CPU design-aid renders / swatch | `tools/ue_char/suits/swatch_cpu.py` (not evidence: the engine sheet is `swatch_sheet.py`) |
| engine content steps `skins` (textures NeverStream, `MI_HeroSuit_<id>`, `MI_HeroLens_<id>`, data asset `/Game/Characters/Hero/Suits/DA_HeroSuits`) and `skinsmap` (`Char_Skins`, `Char_SkinsPlay`) | `unreal/WebHomage/Scripts/build_characters.py` (end of file) |
| the swap | `Source/WebHomage/Characters/WHHeroSuit.{h,cpp}`: `UWHHeroSuitSubsystem` (UTickableWorldSubsystem): T / Shift+T, gamepad D-pad Up (LB + D-pad Up = back), console `wh.Suit <n|id>` / `wh.SuitNext` / `wh.SuitPrev`, applies to the player pawn's `SpiderSuit` slot (+ `Lens`) and to every other mesh wearing a hero suit |
| persistence | `Core/WHSettings.{h,cpp}`: `SuitIndex`, `SuitId`, `LoadSuit()`, `SaveSuit()`; keys `HeroSuit`, `HeroSuitId` in `GameUserSettings.ini [WebHomage.Settings]`; the in-play swap saves at once; "Reset defaults" keeps the suit |
| settings menu row "Suit" (section HERO) | `Core/WHSettingsMenu.cpp` |
| capture director: `FWHShot.Suit`, `FWHShot.bTargetPlayer` | `Characters/WHCharShowDirector.*` |
| automation flags | `-WHSuit=<n|id>`, `-WHSuitScript=t:n,...`, `-WHSuitKeyScript=t,...` (real T key through the player controller), `-WHSuitPersist` (see the header of `WHHeroSuit.h`) |

The playable pawn (`AWebTravCharacter`, P3) is NOT edited: its `SetupHeroMesh` still loads `MI_Hero_Suit`; the subsystem re-applies the chosen suit to the player's mesh every frame and scans the world every 0.5 s.
Integration note for the integrator: the module needs no new Build.cs dependency (the suit list is a data asset, not an asset-registry scan). `Core/WHSettingsMenu.cpp` got one section (a `ChoiceRow`); `Core/WHSettings.*` got the two fields + two methods.

## Next steps (priority order)

1. If the chain has not run: run it (above), then the post-processing list. Look at the 4K stills: IQ of every suit, any smear / seam, glyph legibility, lens tint.
2. Critic verdict -> fix the single biggest gap (probably look: flat colour fields, hood-vs-body contrast on light suits `glacier` / `sage`, glyph size).
3. Whole-mesh suits (PLAN: "whole-mesh suits later"): a style can already change colours / patterns only; a different silhouette (cape, collar, gauntlets) needs Blender geometry on the hero rig.
4. Per-suit emissive trim (glow lines) needs an emissive input in `M_Char_Suit` (not built).
5. Hero model / animation items from rounds 08 - 10 (head brow / nose volume, run start / stop / turn) are untouched; the hero-only first pass also owes P3 the section-5 clips of `SPEC.md`.

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

## Post-processing after the chain (CPU)

```
OUT=$P2_SCRATCH/r11/chain; R=docs/night1/characters/round-11
cp -r $OUT/stills/skin_*_4k.jpg $R/stills/            # (size-check: commit the front + chest 4K, the rest as 1080p)
python3 tools/ue_char/suits/swatch_sheet.py $R/stills $R/SWATCH_SHEET.jpg
python3 tools/ue_char/suits/analyze_swap.py $OUT/pawn/pawn_frames $OUT/pawn/suit_log.txt $R/evidence/swap_latency.json
python3 tools/ue_char/suits/ip_guard.py ocr $R/evidence/ocr_stills.json $R/stills/skin_*_front_4k.jpg ...
python3 tools/ue_char/suits/spec_check_r11.py $R > $R/SPEC_CHECK.md
```

## Older rounds (hero / enemies / crowd, now paused)

Round 10 numbers (fight clips, hit reactions, knockdowns) and the open items (thug collar wedge, hijab walker shin, hero brow / nose volume, orbit guard hold, hood wisp) are in `round-10/SPEC_CHECK.md` and `critic/round-10-CRITIC.md`. The round-11 hair work of an earlier session
(`tools/ue_char/people/hair.py`, `eval/hair_4k.py`, `crops_r11.py`, `make_pairs_r11.py`... that interim round was superseded by the first-pass plan) is committed but was never rebuilt or captured.
How the fight script works (`tools/ue_char/fight/choreo.py`, `fight_script.json`, `r10_check.py`) is unchanged; commands for it: `git show 69afb4b:docs/night1/characters/HANDOFF.md`.
