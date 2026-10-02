# Round 13: captures (P2 hero skins, the sculpted mask head)

> Fan homage project. Not an official Marvel, Sony or Insomniac game. No affiliation. See `DISCLAIMER.md`.

**State of this folder: FIRST-HOLD results (2026-10-02 00:45 - 01:11) + the honest list of what is wrong with them. A second GPU-lock hold (`tools/ue_char/suits/reshoot_r13.sh`, queued behind other agents' jobs) re-runs the whole chain with
the fixes below; when it has run, `post_r13.sh` overwrites this folder and this file is rewritten.** Numbers: `SPEC_CHECK.md` (every number is read from `evidence/`).

**Round target (critic r12, single biggest gap):** sculpt the shared mask head (brow, nose bridge, cheek, chin relief); lenses >= 1.6x their r12 width, each with ONE closed raised dark rim >= 6 px at 4K sealed to a curved glossy lens; the 12 px black face seam as raised piping.
Merge gate: the enemy pack at its r10 content, keep r12's passing lines, Verdant / Saffron / Plum without IP watch items.

**Source.** The REAL game: UE 5.8.3 `-game`, Metal, offscreen (`Scripts/run_game.sh`), one GPU-lock hold (`gpu_slot.sh capture`, wait 2882 s, hold 1531 s, 0 engine crashes, one engine of mine at a time) running `tools/ue_char/suits/chain_r13.sh`
(`STEPS="build stills lineup pawn orbit hero chase fight crowd"`): the content was rebuilt from the committed scripts first, inside the hold (`build_fight.sh clean,tex,mat,mesh,citizens,rename,fightclips,abp,map,maps5,skins,skinsmap`, 68 s; `/Content` is not committed).
GPU utilisation before every run: `evidence/gpu_util_before_runs.txt`; the lock reported `contaminated=true` (no exclusive lock): no frame time in this folder is a performance number.
**Resolution (disclosed).** 4K stills: output 3840x2160, internal 3840x2160 (`r.ScreenPercentage 100`, `evidence/stills_perf.json`, `evidence/lineup_perf.json`); every 4K still is committed as 4K JPEG (q2); the measures ran on the lossless PNG originals (scratch dir).
Movies: 1920x1080, `-movie` = every frame dumped at a fixed 1/60 s step, H.264 crf 18-20.

| file | map / shot | what |
|---|---|---|
| `stills/skin_<suit>_head_4k.jpg` (8) | Char_Skins, view `head`: 12 deg off the face axis, 1.0 m, FOV 26, EV bias +10 | the sculpted head (gates H1, H4, H5, H6) |
| `stills/skin_<suit>_head34_4k.jpg` (8) | view `head34`: the round-12 head framing exactly (25 deg, 1.0 m) | lens width against the r12 still (H3) |
| `stills/skin_<suit>_headside_4k.jpg` (8) | view `headside`: profile, 1.25 m, whole head in frame | nose bump against the head height (H2) |
| `stills/skin_<suit>_front_4k.jpg`, `..._chest_4k.jpg` (8 + 8) | views front (7.85 m, CH1) and chest | **Tessera front = the ROUND-12 image** (the first-run still was a white mannequin: the 8192 px maps were still streaming at 2.2 s; fixed for the second hold: first still at 3.7 s) |
| `stills/skin_<suit>_back_1080p.jpg` | back | |
| `SWATCH_SHEET.jpg` | composed from the 4K stills (front + back + chest + head of all 8 suits) | owner sheet (Tessera's front panel is the r12 image) |
| `swap_pawn_T_key.mp4` (11.4 s), `orbit_all_suits.mp4` (11.4 s) | Char_SkinsPlay (the PLAYABLE pawn, 7 real T presses) / Char_Skins orbit | valid first-hold clips |
| `enemy_lineup_4k.jpg`, `enemy_lineup_34_4k.jpg` | Char_Lineup shots 5 / 6, 4K real-time still at 3.0 s | 7 enemies; the 3/4 camera of this run overlaps the figures (milder camera committed for the second hold) |

**Not in this folder (first-hold clips rejected after looking at their frames):** `hero_run_*`, `street_fight_wide`, `crowd_tracking`. The first hold's `new_stage()` carried the lineup's -0.6 EV bias by mistake (a replace hit two identical lines of `build_characters.py`):
the stage-hero / fight / crowd maps were 0.6 EV darker than r10 / r12 (floor luma 56 against 119, sky 106 against 183 in the chase clip), and the CH2 / CH7 colour-mask instrument then picked the dark sky up (hero height 0.209, lean nan).
The content of those clips is unchanged since r10 / r12 (fight script, choreography, weapon fit: `evidence/fight_unchanged_since_r10.txt`), so the critic pack of this state uses the committed round-12 clips for them (`make_pairs_r13.py cur()`); the second hold re-shoots them at the r10 exposure.

## What the frames show (looked at, not only measured)
- The head is sculpted in the real game on all 8 suits: brow ridge, eye sockets, nose bridge / tip, cheek bones, mouth, chin, a profile with a nose and a chin; big glossy lenses (63 mm, 1.65x the r12 model width) in a raised metal rim; the face seam is a raised cord in the body colour.
- The rim of this run is ONE silver-gunmetal material for every suit: it reads on dark masks, matches the mask on mid-tone ones (Verdant, Ash, Saffron: H4 closed < 90 %) and is not "dark": replaced for the second hold by a per-suit rim (graphite on mid / pale masks, C++ `FrameMaterial`).
- Cinder (near-black hood) shows the relief only faintly (H1 fails); the 3 horizontal slots of Verdant / Glacier / Saffron sit on the lip / mouth relief.
- Plum is apricot gold now (was jade / mint); the lens is a pale apricot.

## Evidence (`evidence/`)
`head_check.json` / `head_check.txt` + `measures/head_overlays/*.jpg` (lens masks, midline, front-most silhouette column and chord on every still), `measures/` (relief / sash / jog of the chest stills, CH1), `ipguard.json`, `seams.json`, `ocr_stills.json`, `regression.txt`,
`swap_latency.json`, `lineup_exposure.json`, `fight_unchanged_since_r10.txt`, `characters_build.log`, `chain.log`, `pawn_*`.
