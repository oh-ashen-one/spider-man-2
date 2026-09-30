# F 4K/60 perf: handoff after round 05

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Branch `night1/perf`, worktree `~/sm2-n1/perf`, pushed to `origin/night1/perf`. Owns `tools/perf_ue2/` (imports P4's `tools/perf_ue/run_perf.py`) and `docs/night1/perf/`. Scratch `/Users/midir/sm2-n1/_scratch/perf/` (NOT committed: export, tex, logs, raw 4K stills
`r03/before` (as-found reference of the round-03 build), `r04/final`, `r05/final` (shipped), `r05/r4ctl` (round-04 content on the round-05 build), `r05/p3`/`p4` (proxy probes), `rtproxy/` (proxy GLBs), `tree_dump.json`, `life/` (P6 derived inputs copy)).
Spec `SPEC.md` (P1-P11), shot list `SHOTLIST.md` (round-05 update at the end), evidence `round-01` .. `round-05/` (`NOTES.md` = every fact of the round, `TABLE.md`, `LOOK_GATE_raw.md` / `look_gate_final.json`, `perf/<session>/`, `stills/`, `cmp/`, `route_30s.mp4`, `content_audit.json`, `rtproxy_report.json`).
Critics: r01 FAILS, r02 APPROACHES, r03 FAILS, r04 APPROACHES (`critic/`). Round-05 blind pack: `/Users/midir/sm2-n1/_scratch/critic-F-r05/pack` (key `pack.key.json` next to it, `pairs.json`), NOT scored yet.

## ROUND 06 IN PROGRESS (interim note, Opus 5.5; replaced by the full rewrite at the end of the round)
- Target (task brief / r05 critic): cut `LumenScreenProbeGather` (2.96 ms) by >= 1.3 ms in the preset, attribute + cut the +1.24 ms `GPU/Unaccounted` of traffic + crowd; pass = life-on CSV p95 <= 18.0 and p50 <= 16.67, S1 crop (485,0,710,490) SSIM >= 0.97 vs as found, S1 recess (1920-space x1700-1850 y540-650) luma 17.5 +-10 % (r05: 29.5).
- Recess cause (found from stills): rt_lite / rt_lite_trees took ALL City/Props out of ray tracing, including the sidewalk sheds (ISM_shed / ISM_shedtop): GI rays pass through the shed roofs (r03 rt_lite 38.4, r04 / r05 ~29, as found 17.3). New perf_apply step `rt_occluders` (default in build_map now) puts the overhead props back; applied to the local content by `_scratch/perf/r06/chain_a.sh` (geo umap backup `_scratch/perf/r06/geo_backup/`).
- Candidate probe sets `overrides/spg_a..d.cvars` (engine "High" GI probe density 32 px / adaptive 16, octahedral irradiance, stochastic interpolation, half-res short-range AO). Exploration perf session `_scratch/perf/r06/perf/x*` (`chain_b.sh`), S1 stills `_scratch/perf/r06/st/<cand>/`.
- `make_life_variant.py` takes `SM2_PERF_LIFE_CROWD='shadow_radius=..;live_radius=..'` (F's copy `/Game/PerfF/Life/Life_Actors_F`, P6's level untouched).
- Findings so far (session `round-06/perf/x1`, stills `_scratch/perf/r06/st`): (a) recess fixed by `rt_occluders`: 18.0 vs 17.3 as found (1.04x); (b) screen-probe density (`spg_a` DownsampleFactor 32, `spg_b`, `spg_c` 24) does NOT move `GPU/LumenScreenProbeGather` (2.95-3.25 vs 3.00): the probe tracing is not what costs; (c) the life `GPU/Unaccounted` is the GPU skin cache: `r.SkinCache.Mode=0` life p50 17.12 -> 16.08, p95 19.47 -> 18.23, Unaccounted -1.05, RHI 5.1 -> 2.9 ms (`overrides/sk0.cvars`); crowd off = -1.21 ms FT, traffic off -0.08, crowd shadows off -0.11; (d) S1 crop repeat noise of the SAME content is 0.964-0.969 (base vs base2), so 0.97 vs one as-found capture sits at the noise floor; best with as-found VSM/TSR/Nanite settings on the proxies 0.940.
- Session y1 (`round-06/perf/y1`): octahedron 4 = the only probe-gather knob that moves the pass (-0.26 ms, FT -0.27 / -0.22 vs warm), radiance cache High 0, short-range AO off -0.06, translucency volume off -0.17 / -0.19 FT (LumenReflections -0.23); crowd shadow radius 30 m and view margin 15 deg: 0. Life + sk0: p50 16.20, p95 18.31 (in-game 18.77).
- LOOK REJECTED (stills `_scratch/perf/r06/st/{ktv0,koct4,cut}`): translucency volume off lifts the S1 recess to 21.7 (1.26x); octahedron 4 drops the S1 crop to 0.880 (full frame 0.954 / 0.965 vs hwl2); both together recess 23.3, S2 gold 0.939. `r06cut` / `perf60_hwl3` drafts with them are NOT shipped. Skin cache off is look-neutral (full-frame SSIM vs hwl2 0.990 / 0.991 / 0.996, S2 crops pass).
- Session z (`chain_g.sh`): sk0 vs sk0 + `lsu` (Lumen surface-cache relight rate at engine High: direct 64, radiosity 128), ship + life, + a 75 % crowd-density probe.
- **KEY FACT (round 06): the running game already applies the engine "High" GI scalability** (every run log: `Applying CVar settings from Section [GlobalIlluminationQuality@2]`, also AA / Shadow / PostProcess @2 after the Epic @3 sections): screen probes are already 32 px with 16 adaptive, radiance cache 16 / 100, surface-cache relight 64 / 128. That is why `spg_a`, `rch`, `lsu` measured 0 and `spg_c` (24 px = denser) +0.26 ms. Session z1: sk0 ship p50 15.50-15.59 / p95 17.48-17.83; life + sk0 (7 runs) p50 16.11-16.26 / p95 18.22-18.52 (in-game 18.68-18.96); 75 % crowd density = no change. Next: probe density below High (`ds48` / `ds64`, chain_h.sh session w).
- (superseded) Session y (`chain_d.sh`: sk0 + translucency volume off / radiance cache High / octahedron 4 / short-range AO off, crowd shadow radius 30 m / view margin 15) queued behind a long traversal capture.
- Build = round-05 build (integration 3aa92ba); traversal r15/r16 + characters r7 NOT merged this round (like-for-like with the r05 numbers).

## State at the end of round 05 (all numbers `round-05/NOTES.md`; valid exclusive session `round-05/perf/g1`, 3840x2160 output, internal 1920x1080, fixed step)
Build: integration 3aa92ba merged (traversal r14 camera = different route frames than rounds 03/04; characters staged from P2 head 8ab861a = r07 WIP).
Shipped path: preset `overrides/perf60_hwl2.cvars` + `r.ScreenPercentage 50` in `Config/Mac/MacEngine.ini`; content = rebuilt + `perf_apply rt_lite_trees,rt_proxy_trees,cloud`:
the tree HISMs (leaves, crowns, bark) are OUT of ray tracing and **402 per-tile merged proxies** (`/Game/PerfF/RTProxy`, actors `City/RTProxy`, hidden in game + affect indirect lighting while hidden, no collision) are IN.
| line | result | pass |
|---|---|---|
| tree RT instances <= 1 k | 402 (level total 920; was 42 337 leaf instances) | yes |
| mean FT - GPU <= 0.9 | ship_a 1.29 / ship_b 0.48 / ship_c 0.39 (Metal per-process GPUTime offset) | **no in 1 of 3** |
| in-game p95 <= 17.9 x3 | 17.81 / 17.86 / 17.87 (CSV p95 17.79 / 17.76 / 17.75, p50 15.65-15.72) | yes, **margin 0.03-0.09 ms** |
| S1 round-02 crop >= 0.97 | 0.929 (same-content repeat 0.986; control r4 0.945) | **no** |
| S1 canopy luma | 0.998 of as found (r4 control 0.908) | yes |
| same-session control r4 (round-04 content) | p50 15.93 / 16.10, in-game p95 17.80 / 18.21, gap 1.90 / 1.45 | proxies: -0.28 ms p50, -0.15 ms p95 |
| **traffic + crowd ON** (`/Game/PerfF/Life/Manhattan`) | p50 17.1, CSV p95 19.4-19.6, in-game p95 19.9-20.2, 1 hitch | **FAILS P1 and P2** |
| P3 static S2 | 14.40 / 15.61 | yes |

## How to reproduce / rebuild (editor and game closed; wrap EVERY Unreal launch, commandlets included, in the lock; never run a commandlet while your own perf session runs)
```
G=/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh
$G capture --label perf -- python3 tools/perf_ue2/build_map.py        # ALL steps; round 05 ran --steps cpp,characters,map then tree_proxy,perf_apply,perf_preset,perf_audit
#   tree_proxy = tree_proxy_dump.py (commandlet, 17 s) + tree_proxy_build.py (numpy, 6 s) -> _scratch/perf/rtproxy; knobs SM2_PERF_PROXY_K0 (1) / K1 (16) / COVER (3.5) / BARK_* / TILE_M (200)
#   perf_apply rt_proxy_trees imports + builds 402 meshes: ~16 min. SM2_PERF_PROXY_REUSE=1 = flags / collision only on the existing meshes (~2.5 min)
$G capture --label perf -- tools/perf_ue2/build_life_variant.sh      # P6 life content (P6's unchanged build_life.py, F's scratch) + /Game/PerfF/Life/Manhattan (spec name@ini+variant:Life)
SM2_PERF_RTVARS=R,N SM2_PERF_RTVAR_CLOUD_KM=20 <UE commandlet> make_rtvars.py   # controls RTvRk20 (round-04 content) / RTvNk20 (no trees in RT); re-make after any proxy rebuild (copies of the geo level)
python3 tools/perf_ue2/perf_queue.py --out <dir> --tag x --configs "warm@ini,ship_a@ini,r4_a@ini+variant:RTvRk20,...,s2@ini+view:S2,lwarm@ini+variant:Life,..." -- --budget-s 870
$G capture --label perf -- tools/perf_ue2/stills2.sh <out> "ship@ini" "S1 S2 S7 route"     # env SM2_PERF_ROUTE_SHOTS=20,28,38,42
$G capture --label perf -- tools/perf_ue2/route_movie.sh <out> "movie@100+set:perf60_hwl2"
python3 tools/perf_ue2/look_gate.py /Users/midir/sm2-n1/_scratch/perf/r03/before <stills dir>
python3 tools/perf_ue2/serial.py <run dirs>                           # FT - GPU gap (P8)
```
- **After any content change, check a route still / the run log for `Couldn't spawn Pawn`**: round 05 lost two perf sessions (`round-05/perf/void_nohero/`) because collision on the hidden proxies blocked the PlayerStart and the "route" ran with no hero.
- `render_in_main_pass = False` removes a primitive from ray tracing AND Lumen card capture; ray-tracing-only = `hidden_in_game` + `affect_indirect_lighting_while_hidden` (engine `RayTracing.cpp` 1368).
- `unreal/WebHomage/Config/Mac/MacEngine.ini` is GENERATED and UNTRACKED: never `git add -A` / `git add unreal`. Content / DDC / Intermediate are local and kept (the proxies are 717 MB of local .uasset).
- Every F launch passes `-notraceserver`. Stop an engine only with `_scratch/gpu/bin/stop_ue.sh "<pattern of your own path>"`. One Unreal process of F at a time. Start every perf session with a throw-away `warm@ini`; deltas need a same-session control.
- CSVs committed gzipped, logs pruned (keep `csv.csv.gz`, `*_perf.json`, `result.json`, `run.txt`); `_scratch/perf/r05/prune.sh <session dir>`.

## Decisions and open items (facts, ranked)
1. **Traffic + crowd ON fails P1 / P2** (p50 17.1, p95 19.4-20.2). The shipped map has no life content, so the "60 fps" claim only holds without it. Next lever candidates: P6's crowd cost (+1.4 ms p50 / +1.7 ms p95; in g1 GameThread 1.85 -> 4.3 ms and RHI thread 2.7 -> 5.2 ms with life, GPU 14.4 -> 16.9 ms), `r.RayTracing.Culling.Angle` for the vehicles, crowd shadow / RT policy.
2. P2 margin without life is 0.03-0.09 ms in-game (CSV 0.39-0.43 ms). The gap line fails in 1 of 3 runs (1.29 ms) because Metal's GPUTime has a per-process offset; a trace-free, offset-proof gap measure (e.g. RenderThread idle / critical-path columns) would settle it.
3. S1 crop 0.929 < 0.97; repeat noise of the same content is 0.964-0.986. Brightness now matches (0.998); the leaf-level GI pattern differs from the as-found masked any-hit. Options: proxies for the near LOD0 trees kept alpha-masked (costs any-hit), card shape instead of shrunk quads.
4. Route stills vs `r03/before` are no longer like-for-like (P3 r14 camera): a new as-found reference on this build needs a content rebuild without `perf_apply` and `--preset-off`.
5. Integrator: adopt `perf60_hwl2` + SP 50 as `[Mac DeviceProfile]`, and run `build_map.py` steps `tree_proxy,perf_apply` after the city build (or move the proxy build into `build_city.py`); the proxies must stay collision-free.
6. Hero and street people remain out of the RT scene (round 03).
