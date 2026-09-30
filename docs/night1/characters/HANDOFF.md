# P2 Characters: handoff after round 06

> Fan homage project. Not an official Marvel, Sony or Insomniac game. No affiliation. See `DISCLAIMER.md`.

Branch `night1/characters`, worktree `~/sm2-n1/characters`, UE MCP port 8772, browser dev port 5203. Author of round 06: Sonnet 5.5 (the interrupted first half of the round: Opus 5.5).
Round-05 critic (blind, `critic/round-05-CRITIC.md`): hero model 4, hero animation 5, enemies 5, civilians 4, image quality 3; FAILS on CH18 + garment integrity. Round-06 target set by the director: **verify the seam fix in the engine** (zero enclosed key pixels inside torsos / sleeves, no vertex spikes on the olive coat, trousers and hoodie collar, no stretched fingers, proved with 3x crops of the same regions).

## STATUS AT THE END OF ROUND 06 (read this first)

- **The round-06 content fix works in the engine.** Fresh engine captures (10:09-11:41 on 2026-09-30, Studio just rebooted) of the whole round-05 shot list are in `docs/night1/characters/round-06/captures/` (10 clips <= 5.6 MB, 20 native-4K stills + 3 1080p frames; movies 1080p60, internal 1920x1080, disclosed in `CAPTURES.md`). Numbers per SPEC line: `round-06/SPEC_CHECK.md`. The 3x crops of the critic's regions (`captures/crops_3x/`, left round 05 / right round 06) show: olive coat one closed panel (no knee flap), trousers smooth (no spikes), near-lane hand = five separate fingers, black-tee armpit hole gone.
- **Chroma-key census (key_report.py with the new key-colour test):** true see-through components inside a cloth panel: round 05 >= 6 (armpit, two torso slits, sleeve slit, coat slit, trouser slit), **round 06 = 0** (hand-classified on crops: `evidence/truekey_interior_components_round0{5,6}.jpg`). Raw enclosed-component counts barely move (22 -> 20 true key; the rest are gaps between limbs / walkers); do not quote them as the result. What is left in that census: **3 small ankle gaps between a trouser cuff and a shoe collar** (211 / 55 / 9 px at 4K on `crowd_key_tracking`). Offline gate: cracks 1035 -> 244, edges > 10 cm 915 -> 0.
- **Hoodie collar (thug):** the "black shards" are hard-edged sun shadows of the hood rim, not geometry (diagnostic with shadows off, `evidence/collar_shadow_test.jpg`). Lineup lighting softened (sun disc 3 deg, enemy fill 1.4 lux, `build_characters.py` `sun_angle` / `enemy_fill`); the wedge inside the hood is softer but still visible. Only the five `*_face_4k` stills come from that second (`map`-only) build.
- **Texture-streaming warm-up in `-movie` runs** (first ~0.4 s show low mips): the first clip of each run is trimmed by 0.6 s (`hero_run_side`, `hero_run_chase`, `street_fight_wide`, `crowd_tracking`).
- **Blind critic pack is built:** `/Users/midir/sm2-n1/_scratch/critic-P2-r06/pack` (19 pairs, key outside at `pack.key.json`, pairs in `round-06/critic_pairs.json`): the standard reference pairs plus round-05 vs round-06 (still, clip, run, key stills, four 3x-region close-ups). The critic's verdict goes to `round-06/CRITIC.md` and `critic/round-06-CRITIC.md` (not written yet).
- **Nothing is running, nothing is queued.** No engine of mine is alive; no `.uasset` / `.umap` was committed; `Content/Characters`, `Content/Tests/Characters` are local rebuilt copies (regenerate with the build command below). The worktree's `DerivedDataCache/` is empty (0 B, the shared engine DDC is used) and `Intermediate/` is 40 KB: nothing to clean.

## How this round ran (for the successor)

1. `prep_all.sh` was NOT re-run: the refit + weights + FBX + 2048 px textures for the 18 citizens were current (`$P2_SCRATCH/eval/refit/*_final.npz` older than `art/night1/characters/export/citizens/*.fbx`).
2. Build (`clean,tex,mat,mesh,citizens,rename,abp,map,maps5,mapkey`, 65 s through `gpu_slot.sh`), then `tools/ue_char/run_r6_captures.sh $P2_SCRATCH/r6/cap "K S E H F C"` (K = key stills, S = crowd 4K, E = faces, H = hero movies + stills + leap, F = fight, C = crowd movies). Queue waits: 0-19 min behind other agents' exclusive perf runs (one launch per group; `ue_wait.sh` polls the hard cap of 2).
3. Measurements: `analyze_r5.sh` with `YOLO_DEVICE=cpu OMP_NUM_THREADS=4` (new env switch; default is still `mps`; the GPU was held by another agent's exclusive perf run), `key_report.py`, `spike_key.py`, `leap_track.py`, `gait_phase.py`, `crops_r6.py`, `crack_view.py`.

## Commands

```
export P2_SCRATCH=/Users/midir/sm2-n1/_scratch/characters      # the default (unreal/WebHomage/Saved/P2Build) does not exist: EVERY tool needs this
tools/ue_char/prep_all.sh                                       # every derived input (hero maps + lens, hulls, people + weapons, refit citizens + weights + FBX), no Unreal, no GPU
python3 tools/ue_char/eval/refit.py NAME [NAME ...]              # raw Tripo -> welded rest-pose mesh + weights + 2048 px texture (cached fit)
python3 tools/ue_char/eval/weights_r6.py NAME [NAME ...]         # final weights (STRETCH_REL / STRETCH_ABS / SKIRT_TOPO / SKIRTW / SMOOTHW knobs)
python3 tools/ue_char/eval/eval_r6.py [--legacy] [--imgs DIR] NAME ...   # offline CH18 gate (minutes, no GPU); --legacy = round-05 geometry
python3 tools/ue_char/eval/key_report.py KEY.jpg ... --out DIR   # CH18 in the engine: enclosed components, true_key vs green-tinted surface, 3x crops
python3 tools/ue_char/eval/spike_key.py KEY.jpg ...              # silhouette spikes on a key still (counts fingertips too)
python3 tools/ue_char/eval/leap_track.py CLIP.mp4 OUT.json       # head-top / feet track + crouch drop of the leap clip
python3 tools/ue_char/eval/crops_r6.py <captures> <out> --r5 <round-05 captures>   # the critic's 3x regions, old | new
tools/ue_char/build_characters_headless.sh '{"steps":"clean,tex,mat,mesh,citizens,rename,abp,map,maps5,mapkey"}'   # full content rebuild (~65 s in the GPU lock + queue); '{"steps":"map"}' = the lineup only, no wipe
tools/ue_char/run_r6_captures.sh <out> "K S E H F C"             # capture groups, one capture_r5.sh call each; frame folders removed after cutting
tools/ue_char/analyze_r5.sh <captures> <evidence>               # cracks / count / YOLO / head bob / lean / key holes / gait (YOLO_DEVICE=cpu to keep the GPU free)
unreal/WebHomage/Scripts/build_editor.sh                        # after C++ changes
```
Scripts are bash: in zsh a `$VAR` list is not word-split (use `bash -c` or a script file) and `echo =====` is a command substitution error. Stop an engine only with `/Users/midir/sm2-n1/_scratch/gpu/bin/stop_ue.sh "<worktree abs path>"`. `pgrep -fl "MacOS/UnrealEditor"` matches your own shell command line; count engines with `pgrep -x UnrealEditor`.

## File map (what P2 owns)

| Path | What |
|---|---|
| `tools/ue_char/eval/` | **round 06:** `refit.py`, `weights_r6.py`, `cit_proxy.py`, `eval_r6.py`, `key_report.py` (now with the key-colour test), `spike_key.py`, `leap_track.py`, `crack_view.py`, `crops_r6.py`, `boundary_loops.py`. Round 05 (legacy fallback): `underlayer.py`, `citizen_rig.py`, `crack_probe.py`, `crack_render.py`, `key_holes.py`, `gait_phase.py`, `critic_r04/` (count / cracks; `YOLO_DEVICE` env), `video_checks.py`, `citizens.py` (FBX exporter; keeps the `SCR = _scr('eval')` line P6's `tools/life/citizens_fbx.py` substitutes) |
| `tools/ue_char/people/`, `weapons/`, `heroanim/`, `hero_suit_r5.py`, `hero_lens_r5.py` | enemies, weapons, hero clips / suit / lens (unchanged) |
| `tools/ue_char/capture_r5.sh`, `run_r6_captures.sh`, `analyze_r5.sh`, `ue_wait.sh` | capture / analysis / launch wait |
| `unreal/WebHomage/Source/WebHomage/Characters/` | sequence idle, jump variants, phase seed, director visibility (unchanged) |
| `unreal/WebHomage/Scripts/build_characters.py` | maps `Char_Hero`, `Char_Fight`, `Char_Crowd`, `Char_CrowdKey`, `Char_Lineup` (now: sun 3 deg disc, fill 1.4), ABPs, 18 citizens |
| `docs/night1/characters/round-06/` | `captures/` (clips, stills, `crops_3x/`), `evidence/`, `CAPTURES.md`, `SPEC_CHECK.md`, `critic_pairs.json` |

## Local-only binaries (nothing below is committed; all regenerable from `~/sm2-assets/raw` + the repo)

- `unreal/WebHomage/Content/{Characters,Tests/Characters}`; `art/night1/characters/**/*.png, *.fbx` (git-ignored).
- `/Users/midir/sm2-n1/_scratch/characters/`: `ueimport/`, `eval/refit` (NAME.npz, NAME_final.npz, NAME_fit.json, NAME_tex.png), `eval/hull`, `eval/tiles`, `r4/yv` (ultralytics venv), `r5/`, `r6/` (offline proxy renders, `cap/` + `cap_lineup2/` + `collar/` raw captures, `untrimmed/` originals of the four trimmed clips, logs).

## Gotchas

1. **Render every side.** The offline probes of round 05 viewed the citizens from one side only and declared the coat coherent; the flap was on the other side. `eval_r6.py` uses 8 yaws per frame.
2. **Weld before you weight, weld before you un-pose.** glTF vertices are split at uv / normal seams; anything per-vertex must run on position-welded vertices and be copied back (`refit.py`, `weights_r6.py`).
3. **A key-still hole count is not a crack count.** Dark hair, skin and cloth in shade pass the green thresholds (the map is lit green by its own bounce); use `key_report.py`'s `true_key` flag and read the crops. Gaps between overlapping walkers and between a hanging arm and the torso are enclosed too. `key_holes.py` (legacy) counts all of them; the critic's `cracks.py` counts bright edge pixels and hair highlights.
4. **Movies start with low-mip textures for ~0.4 s** (streaming): never cut a clip from the first 0.5 s of a `-movie` run, or set `r.Streaming.FullyLoadUsedTextures 1` (not tried).
5. **A stuck-exiting engine of any agent freezes every queue** (`gpu_slot.sh` refuses launches); other agents' exclusive perf runs can hold the lock for 10-20 min. Queue, do CPU work meanwhile, do not bypass. `run_game.sh` now SIGTERMs (then waits 60 s) on its `-timeout`; always pass a generous timeout.
6. **Do not run MPS work (YOLO) while another agent holds the exclusive perf lock**: use `YOLO_DEVICE=cpu`.
7. `build_characters.py` step `mapkey` duplicates `Char_Crowd` before keying it. `clean` wipes `Content/Characters` and `Content/Tests/Characters` on disk: it needs every art input present. `'{"steps":"map"}'` rebuilds only `Char_Lineup` (no clean).
8. The 4K real-time still groups and the movies do not share a clock (director clock drifts ~1.5 s at 5 s): compare defects, not frames, between runs.
9. Earlier gotchas that still hold: `UnrealEditor.modules` can keep pointing at a deleted dylib after `build_editor.sh`; `capture_r5.sh` must be executable; masks: only the outermost shell is draped; hero and thug clips share one skeleton; never edit a shell script a running bash is executing in place.

## Next steps (in order)

1. Read the blind critic's verdict on the round-06 pack (`round-06/CRITIC.md`); write `critic/round-06-CRITIC.md`.
2. **Ankle / shoe-collar gaps** (3 small true-key gaps in `crowd_key_tracking`): bridge strip between the facing boundary loops (`tools/ue_char/eval/boundary_loops.py` lists them: trouser cuff / shoe collar) in `weights_r6.py` / `refit.py`; re-check with `key_report.py` (target: 0 true-key components below the knee).
3. Hood-interior shadow wedge in `thug_face_4k`: try a shadowless fill from the camera side or contact-shadow softening if the critic still calls it a shard.
4. `r.Streaming.FullyLoadUsedTextures 1` for the movie runs so no clip needs trimming.
5. Secondary (round-05 critic): original suit design (IP; owner decision), one closed lens rim, crowd avoidance (two walkers overlap in `crowd_key_a`) and arms hanging at 5-10 deg (now ~30 deg out), fight hit reactions / knockdowns, masks with drape (no lip read). None was touched in round 06.
6. Refit the 2 citizens not in the crowd (`07_black_graphic_tee`, `11_graphic_tee_bonnet`) only if P6 wants them.

## Known problems

- 3 ankle-cuff gaps (above); hood shadow wedge softened, not gone.
- The hero suit design (white spider on the chest, blue legs with red stripes) is still the open brand flag: owner decision, unchanged.
- Hijabi coat: a few hem edges still grow up to 5.4 cm in a stride, and the jeans can show through the coat hem at full stride (the coat follows the thighs at 60 %).
- Citizens are low-poly (6 k triangles): fingers are five faceted wedges, arms 10-12-sided tubes.
- Performance is not measured (shared GPU, contaminated capture slots).

## No copied IP (owner rule)

Enemies and civilians: the owner's own Tripo generations (`~/sm2-assets/raw`) and the browser game's own crowd rig; weapons are generic primitives with procedural wear, no lettering. No reference image or footage is committed (the critic pack lives in `_scratch`, references stay in the private `~/spiderman-learnings`).
