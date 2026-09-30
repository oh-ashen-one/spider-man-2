# F 4K/60 perf: handoff after round 02

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Branch `night1/perf`, worktree `~/sm2-n1/perf`. Owns `tools/perf_ue2/` (imports P4's `tools/perf_ue/run_perf.py`) and `docs/night1/perf/`. Scratch `/Users/midir/sm2-n1/_scratch/perf/` (NOT committed; round-02 raw runs in `r02/`).
UE MCP port 8778 unused (everything is `-game` runs + headless commandlets). Spec `SPEC.md` (P1-P7), shot list `SHOTLIST.md`, evidence `round-01/` and `round-02/` (`NOTES.md` = every fact and probe of the round; `perf/` = raw runs per session
with CSV.gz and the lock sidecar; `stills/`, `cmp/`, `refl/`, `cloud/`). The round-01 critic (`critic/round-01-CRITIC.md`) said FAILS TARGET; no critic has scored round 02 yet (blind pack:
`/Users/midir/sm2-n1/_scratch/critic-F-r02/pack`, key outside it).
**Build under test = the round-01 build** (binaries of integration 1bbd260, Manhattan content of 2026-09-29 22:25, restored untouched). Integration e0ada6c (look R2, water, combat, life) is merged at the source level only and was NOT rebuilt or re-measured:
re-measure once it is built (`perf_queue.py` with the specs below). The local `Content/` is the untouched round-01 build; all round-02 content changes live in map copies under `/Game/PerfF/` (never committed) and can be rebuilt with `make_variants.py`.

## What round 02 found (numbers: `round-02/NOTES.md`; all `gpu_slot.sh perf`, exclusive, `perf_valid: true`, 3840x2160 output, 30 s route, fixed step)
1. **Cloud tracing distance: the critic's 15 km does not work, 4 km does.** VolumetricCloud pass over the last 600 route frames: 2.34 ms at 50 km, **1.97 at 15 km**, 1.22 at 10, **0.62 at 6, 0.41 at 4**, 0.31 at 3 (line <= 0.7). Route p95 (software Lumen, TSR 50 %): 19.92 -> 19.55 / 18.41 / 17.81 / **17.62** / 17.39.
   t20 / t28 SSIM 0.993-0.996 (noise floor 0.997). Price: the distant cloud wisps at the horizon disappear (`round-02/cloud/cmp_cloudhz`); SSIM does not see it. **Adopt: `look_presets.json` `clouds.tracing_max_distance` 50 / 40 / 30 -> 4** (F does not own it; golden only was measured).
2. **The look loss of round 01 is the software REFLECTIONS.** Hardware-RT reflections with software GI (`r.Lumen.HardwareRayTracing 1`, `ScreenProbeGather.HardwareRayTracing 0`, `Reflections.HardwareRayTracing 1`) restore the lit windows and glass:
   crop SSIM S1 glass 0.59 -> 0.92-0.96, S2 windows 0.967 -> 0.986-0.992, S2 gold tower 0.766 -> 0.947-0.967. No software cvar helps (five tried). The "crop SSIM >= 0.97 with software Lumen" route of the critic is not reachable.
3. **Hardware-RT reflections cost +4.1 ms with the whole city in the ray-tracing scene, +1.9 ms with the RT-lite scene** (hinterland `City/Far`, trees `City/Props`, far ground `City/far` set `visible_in_ray_tracing = False`; look unchanged, SSIM 0.99 vs full scene).
   Static S2 view: only +0.5 ms; the moving route pays 1.56 ms in the `RayTracingScene` pass, and skeletal meshes in the ray-tracing scene are worth 1.5 ms (`r.RayTracing.Geometry.SkeletalMeshes 0`: p50 -1.5, but the hero's reflection goes with it).
4. **Presets** (route p50 / p95 ms, fps; official session `perf/s4_official`; two repeats where noted):
| preset | TSR / internal | p50 (fps) | p95 (fps) | P1 / P2 / P3 |
|---|---|---|---|---|
| `perf60` + cloud 4 km, software Lumen | 50 % / 1920x1080 | 15.32 (65.3) | 17.48 (57.2) | pass / pass / pass (S2 static 12.8) |
| **`perf60_hwrefl`** + cloud 4 km + RT-lite scene (hardware-RT reflections, software GI, Nanite error 6) | **46 % / 1766x994** | **16.01 / 16.02 (62.5)** | **18.05 / 18.06 (55.4)** | **pass / pass (margin 0.12 ms) / pass (S2 static 13.20)** |
| `perf60_hwrefl` same, TSR 44 % | 44 % / 1690x950 | 15.65 (63.9) | 17.69 (56.5) | pass / pass |
| `perf60_hwrefl` same, TSR 50 % | 50 % / 1920x1080 | 16.75 (59.7) | 18.95 (52.8) | fails by 0.08 / 0.77 ms |
   Round 01 for reference: as-found defaults 26.45 / 32.09 (TSR 50), perf60 without the cloud fix 16.44 / 19.86.
   **Decision for the owner / director (not mine to take):** 1080p internal with software Lumen (glass reflections and lit windows lost) vs 994p internal with the round-01 look kept. My recommendation is `perf60_hwrefl` at TSR 46 % (visual check vs as-found: SSIM 0.96-0.98 on S1 / S2 / S7,
   crops 0.92 / 0.99 / 0.95, luma lines unchanged); its P2 margin is thin, TSR 44 % is the safe value.

## What other pieces must adopt (nothing outside `tools/perf_ue2`, `docs/night1/perf` was edited; the capture gate of round 01 is already in this branch)
1. **P4 look:** cloud tracing distance 4 km in every preset (`look_presets.json`); `overrides/perf60_hwrefl.cvars` as the Mac device-profile / preset step (never DefaultEngine.ini); accept the horizon-wisp loss or find a cheaper horizon cloud (the cost is the marched segment, not the sample cap: `ViewRaySampleMaxCount 96` did nothing).
2. **P1 city / C manhattan build scripts:** set `visible_in_ray_tracing = False` on the components of `City/Far`, `City/Props`, `City/far` (RT-lite; local reproduction: `perf_content.sh apply rt_lite,cloud`, or the map copies of `make_variants.py`). Keep the glass towers (`City/generic`) in the ray-tracing scene: removing them loses the gold tower reflections (S2 gold crop 0.906).
3. **P3 traversal:** `-WHTravMask` gate still required (round 01). The hero + street people are skeletal meshes in the ray-tracing scene: worth 1.5 ms together; a hero-only vs people-only split was queued (session 5, see "Open" below).
4. **Integrator / gpu lock:** perf tickets time out after 30 min (exit 75 -> re-queued at the back); with 4-5 capture holders each session waited 12-26 min. A stuck-exiting engine (`?E`) blocks every launch; `gpu_slot.sh` handles it, nothing else should.

## Commands (repo root; editor closed; every game launch goes through the lock)
```
G=/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh
python3 tools/perf_ue2/make_variants.py   # commandlet, no GPU: SM2_PERF_CLOUD_KM=4RT,6,4RTP  "<UnrealEditor>" <uproject> -run=pythonscript -script=<abs>/tools/perf_ue2/make_variants.py -unattended -nullrhi -RenderOffScreen -NoSound
       # tags: Cl<N> (cloud N km) | Cl<N>RT[1-3] (+ RT-lite scene levels) | ...P (street people out of RT) | ...D<m> (tree draw distance); copies in /Game/PerfF/<tag>/ ; count `pgrep -fl "MacOS/UnrealEditor( |$)"` first, wait if >= 3
python3 tools/perf_ue2/perf_queue.py --out <dir> --configs "warm@46+set:perf60_hwrefl+variant:Cl4RT,a@46+set:perf60_hwrefl+variant:Cl4RT,s2@46+set:perf60_hwrefl+variant:Cl4RT+view:S2" [--tag s] -- --budget-s 870
       # spec = name@SP[+set:<overrides/stem>][+cvar=value][+flag:-GameFlag][+variant:<tag>][+view:S2]; FIRST config of a session is cold: put a throw-away `warm` first; <= 12 configs per 15 min hold
python3 tools/perf_ue2/windows.py <session dir> --md WINDOWS.md      # p50 / p95 and passes (cloud, NaniteVisBuffer) over the first / last 600 frames
python3 tools/perf_ue2/make_table.py <dirs> --md TABLE.md            # every run, p95 of the 2-frame mean, lock verdict
$G capture --label perf -- tools/perf_ue2/stills2.sh <out> "<spec>" "S1 S2 S7 route"     # 4K stills; env SM2_PERF_ROUTE_SHOTS=38,42 for other route times
python3 tools/perf_ue2/crop_ssim.py <ref_dir> <test_dir> --sbs <dir>     # S1 glass / S2 windows / S2 gold crops (P7); compare_stills.py for whole stills (P4)
$G capture --label perf -- tools/perf_ue2/route_movie.sh <out> "<spec>"  # 1080p60 clip (native 1080p internal, Nanite error halved); has a hang watchdog
```
Do not edit a shell script while a capture that runs it is queued or running (bash reads it incrementally; appending is the only safe edit).

## Method rules learned (each cost a wrong conclusion once)
- Every delta needs a control in the SAME session (identical controls were 16.52 / 16.42 / 16.40 / 16.41 ms p50 over four sessions of round 02, so the noise is +-0.1 ms once warm).
- The first config of a session and any new map / cvar combination is cold: p50 fine, p95 wrong (hitches up to 0.8 s). A p95 verdict needs two warm runs (`fin46_a` / `fin46_b` 18.05 / 18.06).
- SSIM on stills misses small areas (horizon clouds gone at SSIM 0.997): look at the side-by-side of the changed region.
- The frame p50 is the truth, not the per-pass table (`RayTracingScene` 1.56 ms moving / 0.03 ms static explains a +1.9 vs +0.5 ms frame delta only after the run of the probes).
- Nanite / TSR costs depend on the OUTPUT resolution: always 3840x2160 output. Content changes for A/B go into map copies, not into the shipped maps.
- Never SIGKILL a rendering engine; `stop_ue.sh`. A launch that sits at 0.1 % CPU with no new log line is hung (sample it); the watchdog in `route_movie.sh` does the same.

## What is left (facts, ranked)
1. Re-measure everything on the built integration HEAD (look R2 lights, water, combat, life add lights / actors / ray-tracing instances; the `-WHTravMask` gate must be on before the perf run for traversal telemetry and off for perf).
2. Get `perf60_hwrefl` to TSR 50 %: needs -0.8 ms p95. Candidates measured: Nanite error 8 (-0.12 p50, last-window p95 -0.4, look unchecked), `DownsampleFactor 2` (-0.34, look loss), `MaxRoughnessToTrace 0.25` (-0.14, gold tower loss), hero-only ray-tracing budget (skeletal meshes are 1.5 ms).
   No gain: BuildMode 0, RayTracing.Culling 0 (worse), skeletal LOD bias 3, HiResSurface 0, RT2 (Nanite kit out), tree draw distance 1.5 km, FarField 0.
3. The horizon cloud: a cheaper way to keep the far wisps (the marched segment is the cost).
4. The route leaves the detailed block at 22.6 s (C's issue 4): a second route inside the block would separate far-LOD cost from street cost.
5. Open in this round (see NOTES section 6): session 5 (street people out of the ray-tracing scene, `Cl4RTP`, 12 configs) and the 1080p60 route clip were queued behind other agents' captures; check `round-02/` for whether they landed.
