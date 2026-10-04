# Tricks (C) — handoff (round 2: code + probe measured; reel NOT rendered, no critic pack)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Branch `night1/tricks`, worktree `~/sm2-n1/tricks`, scratch `/Users/midir/sm2-n1/_scratch/tricks`. Owned this round (director brief r02):
`unreal/WebHomage/Source/WebHomage/Traversal/WebTravFlips.{h,cpp}`, `docs/night1/tricks/`, `tools/tricks/`. NOT owned: WebTravAnimInstance.cpp,
WebTravCamera.*, WebTraversalComponent.*, WebTravCharacter.*, and (this round) the keyed clip script `docs/night1/traversal/blender/make_flip_shapes.py`
(needs go to `REQUEST-traversal.md`). Integration merged at the start of r02: `origin/Opus-5.5-Loop-Night-1` 035c2c92 (docs only since r01);
`git diff origin/Opus-5.5-Loop-Night-1 -- unreal/` touches only WebTravFlips.{h,cpp}.

## State
- Round 02 is measured on the `-nullrhi` probe of the real game only: `docs/night1/tricks/round-02/NUMBERS.md`, `CHECK_probe.txt`,
  `t60_trick_reel_probe_{telemetry.csv,pose.csv.gz}`. C (catch rotation) FAILS: 0 of 22 <= 250 deg/s, median of the per-trick maxima
  435 deg/s (r01 603), worst 821. P V1 V2 K G2 G3 G4 pass; L 8 slow samples; G1f / PEN / PIK fail (clip work).
- **The reel was not rendered.** 2026-10-03 20:05 the health monitor stopped the first window's engine (pid 33556, "WindowServer
  starved, gpu 100 % ws_cpu 0") and that engine stayed in the exiting state (`ps` stat `?E`, still at 20:30) with the GPU at 100 %,
  WindowServer at 0 % CPU, the lock PAUSED and DEMOTED. Nothing else of tricks was launched; the chained render holds were cancelled.
  Next session: check `ps -o pid,stat -p 33556` and `_scratch/gpu/health.log` first; render only after the orchestrator lifts PAUSED.
- To render this build: `TAG=f PROBE=0 RENDER=1 RENDER_ARGS="-WHHeroFill=16000,36000"` through `hold_r02.sh` (VERDICT of probe f is in
  `_scratch/tricks/probe_r02/f/`; copy it to the TAG dir you use), 3 holds (windows 0:15 15:30 30:45 45:61), then `finish_r02.sh`,
  then the critic pack (below; `PREV_REEL=_scratch/tricks/r02/r01_reel_hq.mp4`, the r01 CRF 16 master).
- r02 code (WebTravFlips.cpp, "catch lean"): from 0.3-0.7 s before a program's catch time it predicts the catch with the traversal's own
  anchor search (public `Anchors->Find` from the predicted body position; exact anchor in 19 of 20 probe catches) and the swing frame it
  starts in (StartSwing's virtual pivot / velocity projection, approximated), or the streamlined air frame when no web is in reach; it
  lerps the program's pitch / twist into that frame (twist x0.3: the facing about the rope is ill-conditioned, measured) and blends the
  shapes into the swing node's starting pose (new shapes `CatchLow(L)` / `CatchBank(L)` = the hero's swingLow / swingCornerBank clips).
  The pose log adds `catch_*` columns and mesh / body / predicted-frame quaternions. `-WHTrickCatch=0` turns it off (A/B vs r01).
- What is left of the catch snap is outside WebTravFlips (measured, REQUEST-traversal.md items 7-9): the swing's spine bank switches on
  in ONE frame from the previous swing's stale `Sw.Bank` (up to 20 deg in a frame), the body roll `S.Roll = Sw.Bank * 0.5` comes from the
  same stale bank, PoseFigure has no roll channel for a flip (the rope's sideways lean, 10-70 deg, cannot be prepared), and programs that
  run out of web get caught 0.1-0.3 s later from the dive frame.

## How to rebuild / capture (all engine work inside `gpu_slot.sh capture --label tricks`)
- C++: `unreal/WebHomage/Scripts/build_editor.sh` (no engine of this worktree running), or `touch _scratch/tricks/REBUILD_CPP` and the
  next `probe_reel.py` compiles first inside its hold. Content was not rebuilt in r02 (only C++ changed; the Content of this worktree is the
  r01 build of the same integration state).
- One hold: `TAG=x PROBE=1 RENDER=0 gpu_slot.sh capture --label tricks -- tools/tricks/hold_r02.sh` = `-nullrhi` probe of the reel script
  (telemetry + pose log, route score, `tricks_check.py` -> `_scratch/tricks/probe_r02/x/VERDICT`, ~1.5 min). `RENDER=1` then renders the
  reel windows without a `DONE` marker (0:15, 15:30, 30:45, 45:61; ~15 min each, two per 40-min hold; `HOLD_T0=<epoch>` when the hold
  started earlier than the script). The merge + encode runs after the 4th window (`capture.sh`), then `tools/tricks/finish_r02.sh`.
- Checks: `tools/tricks/tricks_check.py <telemetry> <pose>` (lines P V1 V2 K L G1 G2 G3 G4 + r02: C catch rotation, X exit poses, G1f per
  frame layout, PEN pencil knee, PIK pike); `tools/tricks/catch_table.py` = C of two captures side by side.
- Critic pack: `PREV_REEL=<r01 reel> PREV_TEL=<r01 telemetry> tools/tricks/make_pairs.py <reel> <telemetry> - <out dir>` then
  `python3 /Users/midir/spider-man-2-astra6/tools/night1/abpack.py <pack> <pairs.json>` and `tools/tricks/pack_sheets.sh <pack>`.
- Hero light test: `tools/tricks/light_test.sh` (renders one short window per `-WHHeroFill` spec, inside a hold). Not yet run with a
  valid script path (the 19:04 run used a relative path: hero at spawn, frames not comparable); `-WHHeroFill=16000,36000` is unverified.

## Gotchas
- `stop_ue.sh` pgreps its pattern: never run it from a command line that contains the worktree path (it kills that shell) -- build the
  pattern from two pieces (`P=/Users/midir/sm2-n1/tri; P="${P}cks"`).
- A shell script that is running can be extended by appending lines (bash reads it incrementally); editing lines it already passed does
  nothing, rewriting a script that is mid-loop is unsafe.
- Queueing a second hold while one runs can acquire the other free slot: chain holds from one driver (`_scratch/tricks/r02/chain.sh`).
- Relative `-WHTravScript=` paths do not resolve inside the engine (the light test of 19:04 showed the hero standing at spawn).
- The L rule (critic pose.py) samples every 6th telemetry row; a held pose (e.g. a catch pose waiting for a late web) reads as slow.

## Next
- C (catch rotation) needs the traversal items 7-8 (ramped spine bank / fresh Sw.Bank at StartSwing, an optional roll channel); with them
  the catch lean already computes the roll (`GC.Rho`).
- Secondary still open (clip work, not owned this round): layout knees every frame, pencil knee median 135 deg, pike hip median 125 deg.
