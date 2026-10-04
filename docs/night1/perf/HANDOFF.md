# F 4K/60 perf: handoff (round 07, re-baseline STOPPED at the 2026-10-03 20:05 desktop reset)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Branch `night1/perf`, worktree `~/sm2-n1/perf`, pushed to `origin/night1/perf`. Owns `tools/perf_ue2/` (imports P4's `tools/perf_ue/run_perf.py`) and `docs/night1/perf/`.
Scratch `/Users/midir/sm2-n1/_scratch/perf/` (not committed). The 2026-10-03 disk cleanup removed the older scratch evidence (`r05`, `r06`, `r07`, `rtproxy` content, `life`); `r03/before` (round-03 as-found stills) is still there but is from an older integration.
Spec `SPEC.md` (P1-P11), shot list `SHOTLIST.md`, evidence `round-01` .. `round-07/`. Critics r01 FAILS, r02 APPROACHES, r03 FAILS, r04 APPROACHES, r05 APPROACHES, r06 FAILS (`critic/`).

## Round 07 brief (Opus director; owner: "shit needs to be 4K")
Integrated Manhattan with traffic + crowd ON, 3840x2160 output, TSR internal >= 1920x1080 disclosed, exclusive lock + < 30 % settle gate, 3 life runs x 1800 frames at fixed step.
Pass: CSV p50 <= 16.67 and p95 <= 18.0 in 3/3; no frame > 25 ms; top-5 % FrameTime-GPU gap <= 1.2 ms both same-row and frame-aligned (previous-row GPUTime);
`look_gate.py` exit 0 on 3840 stills vs a NEW as-found reference of this integration (preset off, no perf_apply); S1 glass crop SSIM >= 0.97; S2 tile (960,540) foliage >= 7.0 %; S7 tile (0,720) foliage >= 11 %.
Disclose every content / foliage change. Measure the AS-FOUND integration first, then optimise.

## State now (verified 2026-10-03 20:16)
- **No round-07 perf number and no round-07 still exists on the new integration.** Nothing was measured: the rebuild did not finish before the stop.
- Merged `origin/Opus-5.5-Loop-Night-1` cd42c1f2 (traversal r25/r26, characters r17, terrain r05, city r11, tricks r01) as ac87bc4b. C++ rebuilt (`build_editor.sh` OK, `UnrealEditor.modules -> libUnrealEditor-WebHomage.dylib`).
- Content rebuilt so far in this worktree (as-found, preset block OFF, no perf_apply): city export / prep / extra (F's vite 5209), city (`clean,tex,mat,mesh,proto,kit` in `city_pass1`, cut by the 40-min capture max hold right after `kit actors`; then `city_rest.py kit,fsky,map` rc 0), life prep (45 vehicle GLBs, 20 citizen FBX).
  NOT yet rebuilt: traversal, characters, look, map, water, life content + map, add_life, combat, view S7. The Manhattan map in Content is therefore NOT a valid as-found state yet (older traversal / characters / look / map content from before the merge).
- **Stop reason:** at 20:05 WindowServer was reset (new WindowServer + loginwindow, pid 38262 / 38265, started ~20:05:30); the GPU reads 100 % Device / Renderer / Tiler utilization with no Unreal render running; health_monitor PAUSED (`WindowServer starved (gpu 100% ws_cpu 0)`). F had no engine running (its chain was queued in gpu_slot). Per the house rule (dead desktop session = pause, push WIP, notify), F withdrew its queued capture job (killed its own gpu_slot waiter PID 31747 + wrapper 31745 by PID, nothing had launched) and stopped. Evidence: `round-07/rebaseline/desktop_reset_2005.txt`, build logs next to it.
- Earlier in the session (18:47) health_monitor also stopped the owner-play game wrapper (pid 22174) for "GPU pinned >= 98 % for 90 s with 2 engines" (`_scratch/gpu/health.log`); not F's.
- Nothing of F is running (no engine, no vite, no chain).

## Resume (fresh session; only after the orchestrator / owner has cleared PAUSED and the desktop is healthy)
1. `cd ~/sm2-n1/perf && git fetch origin && git merge origin/Opus-5.5-Loop-Night-1` (if it moved), `unreal/WebHomage/Scripts/build_editor.sh`.
2. Finish the as-found rebuild in ONE outer capture hold (inner gpu_slot calls pass through):
   `FROM=4 SKIP_PREP=1 /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label perf --timeout 21600 -- docs/night1/perf/round-07/rebaseline/chain_build.sh`
   (copy it to `_scratch/perf/r07b/` first or run it from the repo; it uses absolute paths; `city_rest.py` must sit at `_scratch/perf/r07b/city_rest.py` only for step 3). If the city / export changed in the merge, start at `FROM=1`
   but expect `city_pass1` to need > 40 min with a cold DDC under background QoS: split it (`city_rest.py clean,tex,mat,mesh` then `city_rest.py proto,kit,fsky,map`).
   Integrator reference timings (warm DDC): whole rebuild ~21 min; traversal / characters / look / map ~1 min each.
3. As-found measurement + reference stills: `docs/night1/perf/round-07/rebaseline/chain_s1.sh` (perf session `a1` on `/Game/Maps/Manhattan`, which carries the Life_Actors sublevel after `add_life.py`:
   warm, `af_a/b/c@ini` (as-found, disclose `wh_perf.internal_w/h`), `af50@50`, `h4@50+set:perf60_hwl4`, `h4m1@50+set:perf60_hwl4+r.Nanite.MaxPixelsPerEdge=1`; then stills `_scratch/perf/r07b/asfound` S1 S2 S7 + route t20/t28/t42, fixed step, twice each).
4. Gates: `python3 tools/perf_ue2/frame_gap.py <run>/csv.csv` (p50 / p95 / raw frames > 25 ms / same-row + aligned top-5 % gap); `python3 tools/perf_ue2/look_gate.py <test stills> --asfound _scratch/perf/r07b/asfound --r06 _scratch/perf/r07b/asfound`
   (the round-06 stills are gone; using the new as-found dir for the route rows is a parameter, not an edit of the committed gate - disclose it). S2 / S7 absolute foliage % = the `refv`/`test` columns of `S2_tile_fol` / `S7_tile_fol`.
5. Optimise with per-run cvar sets first (no content change = nothing to disclose but cvars); write the winner with `build_map.py --steps perf_preset` (env `SM2_PERF_PRESET`, `SM2_PERF_PRESET_SP=50`), then 3 life runs at `@ini` in one exclusive session.

## Known traps
- `unreal/WebHomage/Config/Mac/MacEngine.ini` was committed by the orphaned r07 WIP (ccb13d2d, `git add -A` after the usage-limit stop); it holds the hwl4 preset block. `build_map.py --preset-off` deletes it in the working tree (as-found state). It is deliberately NOT staged as deleted; commit it only in the final shipped state. Never `git add -A`.
- Capture holds run under `taskpolicy -b` (background QoS, slower CPU / IO) and are killed at 40 min (exit 124). Queue round trips between holds can take 10-15 min each when other builders hold both slots: chain steps inside one outer hold.
- `gpu_procs.py` flags a run VOID when another process uses > 2 % (WindowServer > 8 %) GPU time. At 18:59 the desktop alone used ~25 % (WindowServer 9.7 %, Codex Service 6.6 %, a Chrome helper 6.3 %, ghostty 2.7 %), so every run on this desktop will read VOID; the brief's validity criterion is the gpu_slot sidecar (`exclusive`, `contaminated`, `settle.min/max`; gate < 30 %). Report both; round-07 p2 showed ~1.2-1.5 ms slower frames under such load.
- The game applies AA / Shadow / GI / PostProcess scalability 2 (High) after Epic; an `.cvars` probe of a High value is a no-op; `-dpcvars` overrides. `WHSettings` (new settings menu) does not touch automated runs (`bLive` false).
- Every F launch passes `-notraceserver`. Stop an engine only with `_scratch/gpu/bin/stop_ue.sh "/Users/midir/sm2-n1/perf"`; kill only own PIDs.

## Findings carried from the orphaned round-07 work (old integration 3aa92ba; `round-07/NOTES.md`, `round-07/perf/`)
- The top-5 % FT-GPU "bubble" is not a BLAS / life sync: `GPU/RayTracingGeometry` = 0 in every frame; a static S2 view (no movement, no life) has FT-GPU mean 1.26 ms and same-row top-5 % gap 2.77 ms. The CSV GPUTime is the previous frame's (corr prev 0.70-0.86 > same 0.25-0.66); aligned top-5 % gap 1.2-1.9 ms. Slow life frames are GPU-heavy windows (probe gather, Lumen card captures, shadows). `r.GTSyncType 1`, `r.RayTracing.AsyncBuild 1`, one sky face per frame did not help.
- Look causes: S2 tree-line thinning = Nanite error 8 (`r.Nanite.MaxPixelsPerEdge=8` in perf60_hwl*); S7 reflected tree / S1 canopy loss = tree representation in ray tracing (perf_apply `rt_lite_trees` + `rt_proxy_trees`). A preset-only candidate (no perf_apply) avoids both content losses; its cost on the new integration is unmeasured.
- Best old-integration life result: `lsky4` (hwl3 + card refresh 0 + capture factor 128 + sky cloud divider 4) p50 15.88 / p95 17.98, one run, quiet desktop.
- Skin cache off (`r.SkinCache.Mode=0`) saved ~1 ms with ~600 citizens; characters r17 still has no recompute-tangents skin-cache use (`build_characters.py` sets import-time tangents only).

## Round-06 shipped state (old integration; `round-06/NOTES.md`): life p50 16.19-16.27 pass, p95 18.36-18.84 fail, S1 crop 0.929, S2 / S7 foliage losses undisclosed (not merged).
