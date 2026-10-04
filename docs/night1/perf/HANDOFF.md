# F 4K/60 perf: handoff after round 06

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Branch `night1/perf`, worktree `~/sm2-n1/perf`, pushed to `origin/night1/perf`. Owns `tools/perf_ue2/` (imports P4's `tools/perf_ue/run_perf.py`) and `docs/night1/perf/`. Scratch `/Users/midir/sm2-n1/_scratch/perf/` (NOT committed: export, tex, logs, raw 4K stills
`r03/before` (as-found reference), `r05/final`, `r06/final` (shipped), `r06/final_life` (traffic + crowd), `r06/st/<candidate>/` (S1 / S2 / S7 look probes), `r06/geo_backup/` (geometry level before `rt_occluders`), `r06/chain_*.sh` (the exact round-06 command chains), `rtproxy/`, `life/`).
Spec `SPEC.md` (P1-P11), shot list `SHOTLIST.md` (round-06 update at the end), evidence `round-01` .. `round-06/` (`NOTES.md` = every fact of the round, `TABLE.md`, `CLIPS.md`, `s1_gate*.json`, `LOOK_GATE_raw.md`, `crops_r02.json`, `perf/<session>/`, `stills/`, `cmp/`, `route_30s.mp4`, `route_life_30s.mp4`).
Critics: r01 FAILS, r02 APPROACHES, r03 FAILS, r04 APPROACHES, r05 APPROACHES (`critic/`). Round-06 blind pack: `/Users/midir/sm2-n1/_scratch/critic-F-r06/pack` (10 pairs incl. a traffic + crowd still and clip; key `pack.key.json` next to it, `pairs.json`), NOT scored yet.

## ROUND 07 RESUMED 2026-10-03 18:49 (re-baseline on integration cd42c1f2) - read this first
- Merged origin/Opus-5.5-Loop-Night-1 (cd42c1f2: traversal r25/r26, characters r17, terrain r05, city r11, tricks r01) as ac87bc4b; C++ rebuilt (build_editor.sh OK).
- Content rebuild in this worktree with the morning-build order, F scratch, as-found (preset block OFF, no perf_apply): `docs/night1/perf/round-07/rebaseline/chain_build.sh`
  (logs `_scratch/perf/r07b/logs/`). Capture holds run at background QoS and are cut at 40 min: the one-pass city step was cut after `kit actors` (19:39), finished by `city_rest.py kit,fsky,map` (rc 0, 19:58). Steps 4-11 (traversal, characters, look, map, water, life content/map, add_life, combat, views S7) run inside ONE outer capture hold (inner gpu_slot calls pass through).
- `unreal/WebHomage/Config/Mac/MacEngine.ini` was committed by the orphaned r07 WIP (ccb13d2d); `--preset-off` deletes it in the working tree for the as-found runs. Not staged; the final round commit carries the shipped preset state.
- 20:05 health_monitor PAUSED (WindowServer starved, GPU 100 % with no Unreal process of F running); F waits in the gpu_slot queue, nothing of F renders.
- Next: `_scratch/perf/r07b/chain_s1.sh` (= `round-07/rebaseline/chain_s1.sh`): as-found perf session a1 (life ON, 3 runs at ini + SP50 + hwl4 per run) and as-found 3840 stills = new look_gate reference `_scratch/perf/r07b/asfound`.

## ROUND 07 IN PROGRESS (Opus 5.5; resumed 2026-09-30 23:30 after a usage-limit stop) - if you are a fresh session, resume from here
- Committed first, unchanged for the round: `tools/perf_ue2/look_gate.py` (`python3 tools/perf_ue2/look_gate.py <stills dir>`; exit 0 = PASS).
- Checkers: `frame_gap.py <csv>` (critic's same-row top-5 % FT-GPU gap), `frame_windows.py <csv>` (per-150-frame windows + per-pass top5-vs-mid), `gpu_procs.py` (other processes' GPU time; perf_route marks VOID).
- FINDINGS (round-07 sessions d1 / e1 / g1, `round-07/perf/`, `round-07/frame_windows_wip.md`): the FT-GPU gap is NOT a life / BLAS sync. Static S2 (no movement, no traffic, RT geometry constant 403 MB, GPU/RayTracingGeometry 0.00) has FT-GPU mean 1.26 ms and same-row top-5 % gap 2.77 ms; the life run's mean gap ~1.0 ms is the same in fast and slow windows; the slow life frames are the GPU-heavy windows (frames 450-1050: GPU 16.0-16.2 ms mean, probe gather 3.6 vs 3.0). The CSV GPUTime is the previous frame's (corr prev 0.7-0.86 > same 0.5).
- Look: S2 tree-line thinning = Nanite error 8 (probe `npe1`/`npe2` restore S2 tree line 1.04 and tile 0.94; error 4 tile 0.73). S7 reflected tree / S1 canopy: NOT culling angle (`ca1`), not Nanite; lost since round 03/04 = how trees are represented in ray tracing (proxies with 12 Lumen cards). Fix under test: content `perf_apply leaf_area,rt_proxy_cards` (Nanite preserve-area on leaf cards; 64 Lumen cards per proxy) = chain `_scratch/perf/r07/chain_c1.sh`.
- Preset under test: `overrides/perf60_hwl4.cvars` (= hwl3 + `r07cap`: card refresh 0, capture factor 128, sky-capture cloud divider 4); `build_map.py` default and MacEngine.ini now hwl4. Best candidate so far `lsky4` life p95 17.98 (1 run).
- Done: c1 (leaf_area PRESERVE_AREA + 64 proxy cards) -> stills `final` (S7 glass SSIM 0.889: 64 cards x 402 proxies under-captured with r07cap; rt_proxy_cards REJECTED, fixed neither S7 nor S1); c2 (cards back to 12) -> stills `final2` (S2 tree line 1.107, tile 1.15, t28 fol 0.866; S1 canopy 0.62, S7 tile 0.017 still lost), `n6` (Nanite error 6 + preserve area: S2 1.057 / 0.999 PASS). Perf session p2 VOID (Codex Service / WindowServer / avconferenced on the GPU; every config ~1.2-1.5 ms slower) - kept in `round-07/perf/p2_VOID`.
- Running: `_scratch/perf/r07/chain_ab.sh` = clean A/B of leaf_area: c3 NONE -> perf p3, c4 PRESERVE_AREA -> perf p4 (life x3, ship x2, S2). The GPU lock queue was 30-60 min deep (other agents' long capture holds). After it: pick NONE or PRESERVE_AREA by cost, final stills (`final2` is already the PRESERVE_AREA state), clips, critic pack `_scratch/critic-F-r07/`.

## State at the end of round 06 (all numbers `round-06/NOTES.md`; official exclusive session `round-06/perf/f1`, 3840x2160 output, internal 1920x1080, fixed step)
Build: same as round 05 (integration 3aa92ba; traversal r15/r16 + characters r7 NOT merged this round).
Shipped path: preset **`overrides/perf60_hwl3.cvars` = `perf60_hwl2` + `r.SkinCache.Mode=0`** + `r.ScreenPercentage 50` in `Config/Mac/MacEngine.ini` (`build_map.py` default now); content = rebuilt + `perf_apply rt_lite_trees,rt_proxy_trees,rt_occluders,cloud` (`rt_occluders` new: sidewalk sheds / shelters / kiosks / subway entrances / dumpsters back in ray tracing).
| line | result | pass |
|---|---|---|
| life ON (`/Game/PerfF/Life/Manhattan`) CSV p50 <= 16.67 | 16.21 / 16.27 / 16.19 | **yes** (round 05: 17.1) |
| life ON CSV p95 <= 18.0 | 18.38 / 18.84 / 18.36 | **NO** (round 05: 19.4-19.6) |
| life ON in-game p95 | 18.93 / 19.58 / 18.94 | (P2 18.2: no) |
| life ON hitches | 0 / 14 (one machine-wide stall burst, all threads + GPU slow, frames 1209-1288) / 0 | no in 1 run |
| LumenScreenProbeGather -1.3 ms | 0 shipped: the game already runs GI scalability **High** (32 px probes); every further cut (48 / 64 px, octahedron 4, translucency volume off) fails the S1 look | **NO** |
| life `GPU/Unaccounted` +1.24 attributed / cut | = GPU skin cache (~600 citizens); skin cache off: Unaccounted at ship level, life p50 -1.0 ms | yes |
| S1 crop (485,0,710,490) SSIM >= 0.97 | 0.929 (repeat noise of the same content ~0.97; best with as-found settings 0.940) | **NO** |
| S1 recess luma 17.5 +-10 % | 18.0 (round 05 29.6) | yes |
| ship (no life) p50 / CSV p95 / in-game p95 | 15.44-15.58 / 17.61-17.72 / 17.63-17.70, 0 hitches | yes |
| P3 static S2 | 14.52 / 15.76 | yes |
| P8 FT - GPU <= 1.0 | ship 1.72 / 1.15 / 1.34 (Metal offset caveat) | no |
| P10 ShadowDepths p95 <= 2.5 | 2.65 | no |

## How to reproduce / rebuild (editor and game closed; wrap EVERY Unreal launch, commandlets included, in the lock; never run a commandlet while your own perf session runs)
```
G=/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh
$G capture --label perf -- python3 tools/perf_ue2/build_map.py        # ALL steps; or --steps cpp,characters,map then tree_proxy,perf_apply,perf_preset,perf_audit
SM2_PERF_APPLY_STEPS=rt_occluders $G capture --label perf -- python3 tools/perf_ue2/build_map.py --steps perf_apply   # 19 s, only the round-06 content step
python3 tools/perf_ue2/build_map.py --steps perf_preset               # writes the perf60_hwl3 block into Config/Mac/MacEngine.ini (no Unreal launch)
$G capture --label perf -- tools/perf_ue2/build_life_variant.sh      # P6 life content + /Game/PerfF/Life/Manhattan; make_life_variant.py takes SM2_PERF_LIFE_CROWD='shadow_radius=..;..' (F's copy of the life level)
python3 tools/perf_ue2/perf_queue.py --out <dir> --tag f --configs "warm@ini,ship_a@ini,lwarm@ini+variant:Life,life_a@ini+variant:Life,..." -- --budget-s 870
python3 tools/perf_ue2/pass_diff.py <session dir> --control ship_a --life-control life_a --md out.md   # CSV p50/p95, in-game p95, threads, GPU passes, deltas
$G capture --label perf -- tools/perf_ue2/stills2.sh <out> "ship@ini" "S1 S2 S7 route"     # env SM2_PERF_ROUTE_SHOTS=20,28,38,42; "life@ini+variant:Life" "route" for traffic + crowd
python3 tools/perf_ue2/s1_gate.py /Users/midir/sm2-n1/_scratch/perf/r03/before <stills dir>...   # round-02 S1 crop SSIM + recess luma (round-05 critic lines)
$G capture --label perf -- tools/perf_ue2/route_movie.sh <out> "movie@100+set:perf60_hwl3[+variant:Life]"
python3 tools/perf_ue2/look_gate.py /Users/midir/sm2-n1/_scratch/perf/r03/before <stills dir>; python3 tools/perf_ue2/serial.py <run dirs>
```
- **Check every run log for `Applying CVar settings from Section [GlobalIlluminationQuality@2]`**: the game applies AA / Shadow / GI / PostProcess scalability **2 (High)** after Epic; an `.cvars` probe of a "High" value is a no-op. `-dpcvars` (device-profile priority) does override it.
- `r.SkinCache.Mode=1` per run on top of the hwl3 ini gives a NOT faithful round-05 control (f1 `r5life` 22.1 ms p95, RHI 6.7); the clean skin-cache attribution is x1 `life` vs `lsk0` and z1.
- After any content change check a route still / log for `Couldn't spawn Pawn` (round 05 lost two sessions to proxy collision). The proxies stay collision-free.
- `unreal/WebHomage/Config/Mac/MacEngine.ini` is GENERATED and UNTRACKED: never `git add -A` / `git add unreal`. Content / DDC / Intermediate are local and kept (proxies 717 MB).
- Every F launch passes `-notraceserver`. Stop an engine only with `_scratch/gpu/bin/stop_ue.sh "<pattern of your own path>"`, kill only your own PIDs. Start every perf session with a throw-away `warm`; deltas need a same-session control.
- CSVs committed gzipped, logs pruned (keep `csv.csv.gz`, `*_perf.json`, `result.json`, `run.txt`).

## Decisions and open items (facts, ranked)
1. **Life p95 is 0.36 ms over 18.0 in the clean runs.** The life overhead left after the skin cache is ~0.6 ms FT (Basepass +0.17, NaniteVisBuffer +0.13 moving traffic, velocities +0.10, shadows +0.09, fill light +0.10); the frames are GPU-bound in window s 5-22.5. Not proportional to crowd density (pool-capped at 600 live citizens). Untested levers: a smaller citizen pool / `LiveRadiusHigh` (visible density trade, P6's call), citizen skeletal LODs (P6 / P2 content), tree-proxy far-card decimation (`SM2_PERF_PROXY_K1` 16 -> 32; the proxies cost ~0.8 ms FT; ~16 min `perf_apply rt_proxy_trees` rebuild), fill light off (-0.1 ms, P6 look feature).
2. The screen-probe-gather lever is exhausted under the S1 look gate (table in NOTES 2b). A ProfileGPU-level breakdown of the 2.96 ms was not taken (no trace tools; only stat / CSV).
3. S1 crop 0.929 vs 0.97 sits at the capture repeat noise (0.964-0.986); the canopy RT representation (opaque merged proxies vs masked leaves) is the measurable remainder (0.940 with as-found settings, round-04 masked content 0.945-0.951).
4. life_b's stall burst (all threads + GPU slow together) is unexplained; the lock does not see non-Unreal GPU users (a local MLX model runs on this machine).
5. Integrator: adopt `perf60_hwl3` + SP 50 as `[Mac DeviceProfile]` (skin cache off is safe: no recompute tangents / morphs / skinned RT in the project), run `build_map.py` steps `tree_proxy,perf_apply` (now incl. `rt_occluders`) after the city build. Recommend P6 keep `r.SkinCache.Mode=0` in mind for any future morph / cloth work.
6. P8 gap and P10 ShadowDepths (2.65) fail; no VSM work this round.
