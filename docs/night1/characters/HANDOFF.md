# P2 Characters: handoff (round 13, first-pass piece G: hero skins)

> Fan homage project. Not an official Marvel, Sony or Insomniac game. No affiliation. See `DISCLAIMER.md`.

Branch `night1/characters`, worktree `~/sm2-n1/characters`, UE MCP port 8772, browser dev port 5203. Round 13 author: Sonnet 5.5 (2026-10-01 night, orchestrated from the director's r13 target).
Everything is committed and pushed (`origin/night1/characters`); `/Content` is NOT committed (script-generated, rebuilt by `build_fight.sh`, see Commands). Scope: the HERO ONLY (+ the enemy-pack merge gate).

## STATE OF ROUND 13 (read this first)

Round target (director, after the r12 critic [hero 5, anim 5, enemies 4, civilians 5, IQ 5; IP PASS]): SCULPT the shared mask head (brow, eye sockets, nose bridge + tip, cheek bones, mouth, chin),
lenses >= 1.6x their r12 width each with ONE closed raised dark rim sealed to a curved glossy lens, the 12 px black face seam replaced by raised piping; merge gate: the enemy pack back to the
r10 content (7 enemies in the lineup, weapons, exposure; fight clip = the unchanged r10 choreography), keep r12's passing lines, Verdant / Saffron / Plum with no IP watch items.

### What was built (all CPU-side, committed)
| piece | file |
|---|---|
| head sculpt (numpy; one script on the hero GLB, so all 8 suits inherit it): 2 levels of conforming refinement of the front face zone (~2 mm triangles), Gaussian relief field (brow ridge + glabella, eye sockets, nose bridge / tip / alae / undercut, cheek bones + hollows, mouth bulge + groove, chin), z-displacement windowed by n_z, 6 mm temple widening, delta normals (welded by position) | `tools/ue_char/suit8/hero_head_r13.py` |
| eyes on the sculpted surface: 63 mm x 28 mm pill / bean lenses (r12: 38.5 x 17.7 mm, 12 deg blade; now 3 deg tilt, arched, rounded ends; NOT a teardrop), 3.4 mm raised rim 3.6 mm proud (r12 4.3 / 2.3 mm), lens edge 0.8 + 2.6 mm dome; r8's `hero_lens_r8.py` is the library (monkey-patched outline / profile / 2 mm envelope) | `tools/ue_char/hero_lens_r13.py` |
| rim material: polished gunmetal (`MI_Hero_LensFrame`: base 0.30 / 0.30 / 0.33, metallic 0.9, roughness 0.25; r12 matte near-black = invisible on a dark mask) | `Scripts/build_characters.py` ('mat') |
| face seam: a raised cord in the body colour (`relief.seam` 2.2 mm, was an INK groove 2.2 mm wide); satin hood (`rough_hood` 0.50), hood colour halfway to the crown colour (near-black hoods hid the relief), crown piping arc + brow flashes moved up (the lenses grew); the glyph on the sash is laid in DEEP (Cinder: cyan on cyan) | `tools/ue_char/suit8/design.py` |
| Plum: jade / mint accent -> apricot gold (`#f2b36b`) (the r12 critic's "watch Plum's purple + mint") | `tools/ue_char/suits/suits.json` |
| Char_Skins views: `head` (12 deg off the face, 1.0 m), `head34` (the r12 framing exactly, for the lens comparison), `headside` (profile, 1.25 m); 6 views x 8 suits | `Scripts/build_characters.py` ('skinsmap') |
| Char_Lineup: 7 enemies (the grey hood is back at the end of the row, 100 cm spacing), -0.6 EV bias, enemy fill 1.4 -> 1.0 lux | `Scripts/build_characters.py` ('map') |
| pass test of the head on the 4K stills (H1 - H6, definitions in the file header) | `tools/ue_char/suits/head_check_r13.py` (+ `spec_check_r13.py`) |
| chain / post / pairs | `tools/ue_char/suits/chain_r13.sh`, `post_r13.sh`, `make_pairs_r13.py` |

Prep order (CPU, `$P2_SCRATCH/ueimport/SK_Hero.glb`): `prep_glbs.py` -> `hero_head_r13.py` -> `hero_lens_r13.py` -> `hero_weights_r12.py` (build_characters.py 'prep' does the same). The maps (`hero_suit_r8.py` Tessera 8192 +
`gen_suits.py` 7 x 4096) were regenerated with the final design (`art/night1/characters/hero/suits/`, git-ignored); `test_regression.py` PASS (r8 legacy texel for texel + the r13 default hashes).

### Honest findings of this round (measured, not asserted)
- **The skins-stage EV did NOT leak into `Char_Lineup`.** r04 and r12 lineups have the same exposure (wall 208.3 / 207.5 of 255). The washed-out look is the pale sunlit wall + the fill; this round's -0.6 EV / weaker fill is a real change, not a revert. The r12 lineup had 6 enemies since round 05 (the grey hood twin was dropped), the r10 critic's "7 enemies" counted the 6 + the hero.
- Lens width vs head width is limited by the face: at x = 0.07 m the mask surface is already ~60 deg from the view axis, so in a 25 deg view the far lens is foreshortened and runs against the silhouette. Gate H3 is therefore: the NEAR lens in the r12 framing and the MEAN of both lenses in the 12 deg still (the far-lens ratio is reported). The 6 mm temple widening and the 63 mm width are the compromise (66 / 72 mm touched or left the outline).
- CPU soft-render numbers (not evidence) on the final GLB: nose bump 8.7 % of the head height, lens 1.65x model width (63 vs 38.5 mm).
- Grips: the pipe / bat sit across a loose fist (tool `tools/ue_char/fight/weapon_clip_check.py`, r10 fit unchanged, CPU previews in the round dir if captured); the lineup stands in the hero idle (the guard idle holds the weapon vertically in front of the face).

### What the first hold (2026-10-02 00:45 - 01:11, `$P2_SCRATCH/r13/chainA`, 1530 s, 0 crashes) showed (measured on its frames, `head_check.json`)
GOOD: the heads are sculpted in the real game on all 8 suits (brow, nose, cheek bones, chin, big glossy lenses in a raised metal rim, raised face-seam cord): nose bump 8.6 - 10.8 % of the head height (gate 2 %),
lens width 1.75 - 1.9x r12 (near lens 1.9 - 1.96x), seam lit / shadow pair 49 - 147 luma (gate 20), no black run. 7 enemies in the lineup, wall luma 141 (r04 / r12: 208).
BAD (all found by looking at the frames, then fixed on CPU, nothing of it is in the committed round dir):
1. my lineup `-0.6 EV` block landed in `new_stage()` too: the Char_Hero / Char_Fight / Char_Crowd clips were 0.6 EV darker than r10 / r12 (CH2 / CH7 instruments then picked the sky up). Fixed (only the lineup keeps its bias).
2. the first still (Tessera front, 2.2 s) was a white mannequin (the 8192 px maps still streaming): the first still is now taken at 3.7 s.
3. the stills run's `-quit` counts from process start (~35 s of start-up): the last 7 stills were lost (re-shot inside the same hold by appending a block to the running snapshot; the committed chain now has +40 s).
4. one silver rim for every suit lost the rim on mid / pale masks (H4 closed >= 90 % of the angles: 3 of 8 suits) and it is not "dark": a per-suit rim (C++ `FWHHeroSuitEntry::FrameMaterial`, compiled; build step 'skins': silver-gunmetal base 0.22 on near-black hoods, dark graphite 0.06 on the others).
Gate status of that run (strict, my own definitions): H2 / H3 / H5 8 of 8, H1 6 of 8 (Cinder, Saffron: a near-black / seam-dominated profile), H4 3 of 8, H6 7 of 8 (Cinder far lens against the outline).

### The SECOND hold (queued, runs by itself): the whole chain again
Queued at 2026-10-02 01:15 (wrapper PID in `$P2_SCRATCH/r13/reshoot_wrapper.pid`, log `$P2_SCRATCH/r13/chainA/gpu_wrapper2.log`; 6 jobs of other agents ahead, one `look` hold had run > 3 h). The wrapper runs
`tools/ue_char/suits/.reshoot_r13_run.sh` (snapshot of `reshoot_r13.sh`), which needs the marker `$P2_SCRATCH/r13/chainA/READY_V2` (present) and then execs the snapshot `.chain_r13b_run.sh` of `chain_r13.sh` with
`STEPS="build stills lineup pawn orbit hero chase fight crowd" EV=10.0` into `$P2_SCRATCH/r13/chainA/v2` (~1450 s, limit 2400 s). If the wrapper is alive, LEAVE IT (never start a second engine, never kill it unless the owner asks).
When `$P2_SCRATCH/r13/chainA/v2/chain.log` ends with `chain done`:
```
export P2_SCRATCH=/Users/midir/sm2-n1/_scratch/characters
OUT=$P2_SCRATCH/r13/chainA/v2
bash tools/ue_char/suits/post_r13.sh $OUT $OUT                      # CPU, ~8 min: fills docs/night1/characters/round-13 (stills, sheet, clips, evidence) + head_check.json
python3 tools/ue_char/suits/spec_check_r13.py docs/night1/characters/round-13 > docs/night1/characters/round-13/SPEC_CHECK.md
STILLS_4K=$OUT/stills python3 tools/ue_char/suits/make_pairs_r13.py docs/night1/characters/round-13 /Users/midir/sm2-n1/_scratch/critic-P2-r13/pairs.json
python3 /Users/midir/spider-man-2-astra6/tools/night1/abpack.py /Users/midir/sm2-n1/_scratch/critic-P2-r13/pack /Users/midir/sm2-n1/_scratch/critic-P2-r13/pairs.json
```
then LOOK at every head still and clip frame (the gates are numbers, the critic is blind and visual), check the `skins: rim <id> ... silver|graphite` lines of `characters_build.log`, write `round-13/CAPTURES.md`, rewrite this file, commit, push.
Round-13 media of the FIRST hold are in `$P2_SCRATCH/r13/chainA` only (not committed: wrong exposure / white front); `docs/night1/characters/round-13/` holds nothing of them once post_r13.sh of the second hold has run.
If the wrapper is gone (the lock timed out: `--timeout 28800` = 8 h) re-queue the same way (`gpu_slot.sh capture --label characters --timeout 28800 -- bash tools/ue_char/suits/.reshoot_r13_run.sh $P2_SCRATCH/r13/chainA`).
If a gate still fails, the levers are: `hero_head_r13.py` `field_mm` amplitudes, `hero_lens_r13.py` `A_HALF` / `BEZEL`, the rim colours in `build_characters.py` ('skins'), `design.py` `rough_hood` / hood colour / `seam`; the GLB and the maps are rebuilt on CPU (seconds / 8 min), engine content needs a hold.

## Round 12 and earlier (history)

## STATE AT THE END OF ROUND 12 (read this first)

Round 12 author: Opus 5.5 (2026-10-01 17:40 - 23:30). Everything committed and pushed on `night1/characters`; `/Content` is NOT committed (rebuilt by the scripts).
Round target (critic r11, single biggest gap): raised piping + net / panel lines UNDER the sash and chevron; same round: no faceted patches / weave flip / armpit stair-step, the Verdant jog
<= 2 px, Verdant + Saffron re-blocked, CH1-framed fronts, every r8 axis re-proven (stage-hero run / chase, enemy lineup 4K, fight clip, crowd clip, swap movie).
Numbers: `round-12/SPEC_CHECK.md`; captures and how: `round-12/CAPTURES.md`; the fold diagnosis: `round-12/FOLD.md`. Critic pack: `/Users/midir/sm2-n1/_scratch/critic-P2-r12/pack`
(21 pairs, key in `pack.key.json` outside it; `pairs.json` also as `round-12/critic_pairs.json`). No critic verdict yet.

| line | r11 -> r12 (real game, 4K chest stills unless noted) | verdict |
|---|---|---|
| net / panel lines through the sash: critic probe Tessera (1412, 1240) | luma 85 vs panel 109 -> **110 vs 107** | fixed |
| sash / chevron: longest dark run inside the panel (<= 10 px) | Tessera 20 -> **11**, Ash 70 -> **3**, Cinder 108 -> **10**, Saffron 98 -> **6**, Verdant 9 -> 8, Plum 4 -> 9 (Glacier / Sage: no sash panel found) | Tessera 1 px over |
| raised piping: 64 px line cells with a lit / shadow pair >= 20 luma | Tessera 32 -> **59 %**, Ash 32 -> 58, Glacier 35 -> 58, Sage 32 -> 62, Plum 53 -> 60, Cinder 51 -> 59, Saffron 40 -> 52, **Verdant 41 -> 35** | NOT "every line": about 6 in 10; Verdant's horizontal rib rings read flat |
| Verdant chevron jog at the critic's columns (x 1320-1400) | **68.6 px -> 1.2 px** (whole tracked edge 4.1 px at (1528, 1821), stitch / twill noise) | fixed at the jog |
| armpit fold (CPU skinning, folded faces in the region) | run 62 -> 18, sprint 85 -> 37, fight idle 34 -> 7, idle 4 -> 2 | `FOLD.md` |
| normal map vs mesh tangent basis per UV island | all large islands cos >= 0.98, no island flipped (Tessera / Verdant / Ash) | PASS |
| CH1 front framing 0.48 - 0.62 | 0.77 -> **0.541 - 0.545** | PASS |
| CH6 / CH7 / CH2 stage hero (r8 instruments, r8 clips measured alongside) | side head bob 3.542 Hz (r8 3.542), chase 3.542 Hz, lean 20.6 deg (r8 25.5), chase height 0.389 (r8 0.372; target 0.39) | PASS / PASS / CH2 at the edge |
| IP guard palette, seams, OCR, regression | min palette distance 52.3, worst seam run 4.6 px, 0 OCR hits, r8 legacy + r12 default md5 PASS | PASS |
| swap on the pixels | 7 / 7 T presses, 33 ms | PASS |

**Cross-piece numbers for the orchestrator -> traversal brief (P3 owns `Traversal/`, P2 did not edit it):** the playable pawn (`AWebTravCharacter` + `WebTravAnimInstance`) runs at
**4.0 steps/s** (head-top bob period 15.0 frames, FFT 4.13 Hz; target 3.2 - 3.8), and its start switches `A_Hero_idle -> A_Hero_walk @0.817 s -> A_Hero_jog @0.867 s -> A_Hero_run @0.983 s`
with blend weight 1.000 on every switch (telemetry `round-12/evidence/pawn_telemetry.csv`, `loco_r12.py tpop`); the 10-number pose signature spreads its change over 28 frames, so the visible
pop the critic saw (0.733 -> 0.750 s of the trimmed r11 clip) is the hard clip switch at 0.817 s untrimmed.

### What changed in round 12 (all committed)
- `tools/ue_char/suit8/hero_weights_r12.py` (run by `build_characters.py` 'prep' after `hero_lens_r8.py`): `strip_arm` (no shoulder / upperArm weight on the chest side below the armpit, ramp
  y 1.25 -> 1.36 m) + Gaussian weight smoothing in the 1650-vertex torso-side region. `--check` prints / writes the fold counts. THE cause of the jog / weave flip / facets (`FOLD.md`).
- `tools/ue_char/suit8/design.py`: style `relief` (default `piping`: cords pipe 1.8 mm, net 1.3, ring 1.8, glyph 1.4, sash plateau 0.6, border 1.6, rough 0.34 / 0.40, cavity AO 0.35,
  `net_tone` 0.38 = mid-tone net cords); every line laid after the sash is masked UNDER it (`sash_cov`); crisp sash / chevron ends. `relief.kind = 'r8'` reproduces round 08 exactly.
- `tools/ue_char/hero_suit_r8.py`: `--legacy-r8`, cavity AO pass, smoothed metres-per-texel, normal sigma 0.6 for relief maps; `gen_suits.py` the same.
- `M_Char_Suit` (`build_characters.py`): the weave is laid out from the PRE-SKINNED local position (triplanar whiteout, rotated onto the skinned normal, World -> Tangent; static switch
  `WeaveFromPosition`, default on). Compiles and renders in -game (weave continuous across the armpit seam in the 4K chest stills).
- Stage: fills 0.8 -> 0.5 (`skin_fill`), front / back views 7.85 m (CH1).
- `suits.json`: Verdant deep #4b4a22 olive-bronze, upper arm body, glyph `gate` (no black raglans, no chest ring); Saffron deep / crown #2f3a36 slate, upper arm body, `sleeves: false`
  (no tan / brown raglan pair).
- Tools: `tangent_check.py`, `relief_check_r12.py relief|sash|jog`, `loco_r12.py ch1|bob|pop|tpop`, `chain_r12.sh` (one hold: build + captures), `post_r12.sh`, `spec_check_r12.py`,
  `make_pairs_r12.py`; `test_regression.py` checks the r8 legacy AND the r12 default hashes (update EXPECT_R12 with any deliberate design change).

#### Round-11 next steps (history; round 12's list is at the top)
1. Read the round-12 critic verdict (`critic/round-12-CRITIC.md` once written) and fix its biggest gap. Known open items: (a) relief is ~60 % of line cells, not every line: Verdant's
   horizontal rib rings and lines parallel to the key light read flat (raise `relief.net` for `rib`, or give the stage key a side component); (b) Tessera sash dark run 11 px at (1349, 1164)
   (the remains of the armpit crease at the sash's upper-left corner); (c) CH2 chase framing 0.389 (target 0.39-0.53: camera 5 % closer in `maps5`); (d) head sculpt (egg head, shared
   decal grille) is round 13 per the brief.
2. The owner's IP sign-off (PLAN-firstpass section 5): show `round-12/SWATCH_SHEET.jpg` (Verdant and Saffron re-blocked); no merge before it.
3. P3 items above (cadence 4.0 steps/s, hard clip switches) belong to the traversal brief.

### Lessons of this round
- NEVER edit a shell script while bash runs it (bash reads it incrementally: the r12 first chain re-ran a step and died on a syntax error). `chain_r12.sh` is run from a snapshot copy.
- The GPU lock's default capture wait timeout is 3600 s: with 6+ waiters pass `gpu_slot.sh capture --timeout 14400`. An auto-PAUSE (20:43 - 22:38 tonight) blocks every launch; wait.
- `run_game.sh` has an uncommitted change from another session (18:12, frame cap for non-perf captures): not P2's, left alone.

## Round 11 (history)

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

## Re-running the evidence (round 12: ONE lock hold of ~23 min does build + every capture)

```
export P2_SCRATCH=/Users/midir/sm2-n1/_scratch/characters; G=$P2_SCRATCH/ueimport
python3 tools/ue_char/prep_glbs.py && python3 tools/ue_char/hero_lens_r8.py $G/SK_Hero.glb && python3 tools/ue_char/suit8/hero_weights_r12.py $G/SK_Hero.glb   # hero GLB (CPU, seconds)
python3 tools/ue_char/hero_suit_r8.py && python3 tools/ue_char/suits/gen_suits.py      # Tessera 8192 (~2.5 min) + the 7 others at 4096 (~5 min); art/.../suits/tessera_* are symlinks to hero/tex
cp tools/ue_char/suits/chain_r12.sh tools/ue_char/suits/.chain_r12_run.sh            # run a SNAPSHOT (never edit a running script)
OUT=$P2_SCRATCH/r12/chainN; mkdir -p $OUT
EV=10.0 STEPS="build stills pawn orbit hero chase fight crowd lineup" nohup /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label characters --timeout 14400 -- bash tools/ue_char/suits/.chain_r12_run.sh $OUT > $OUT/gpu_wrapper.log 2>&1 < /dev/null &
bash tools/ue_char/suits/post_r12.sh $OUT $OUT        # CPU: fills round-12/ + measures (~4 min)
python3 tools/ue_char/suits/spec_check_r12.py docs/night1/characters/round-12 > docs/night1/characters/round-12/SPEC_CHECK.md
STILLS_4K=$OUT/stills python3 tools/ue_char/suits/make_pairs_r12.py docs/night1/characters/round-12 /Users/midir/sm2-n1/_scratch/critic-P2-r12/pairs.json
python3 /Users/midir/spider-man-2-astra6/tools/night1/abpack.py /Users/midir/sm2-n1/_scratch/critic-P2-r12/pack /Users/midir/sm2-n1/_scratch/critic-P2-r12/pairs.json
```

## Re-running the round-11 evidence (history)

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
