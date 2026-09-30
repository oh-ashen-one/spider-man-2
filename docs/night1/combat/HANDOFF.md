# P5 Combat: handoff after round 03

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Branch `night1/combat`, worktree `~/sm2-n1/combat`. UE MCP port 8775, dev port 5206; nothing here uses the editor or MCP: everything is headless commandlets plus `-game`. P5 owns
`Source/WebHomage/Combat`, `/Game/Combat`, `/Game/Tests/Combat`, `Scripts/build_combat.py`, `docs/night1/combat/`. Scratch: `/Users/midir/sm2-n1/_scratch/combat/` (r03 work dirs `r03/exp1-3`, `r03/final1`, `r03/final2`).
Evidence: `round-01/`, `round-02/`, `round-03/` (`NOTES.md` = every number and the experiments, `measure.md` per blow, video, stills, `hit_strips/`). `SPEC.md` = numeric targets with the checker for each, `SHOTLIST.md` = views.
**Round 03 has not been scored by a critic.** Blind pack: `/Users/midir/sm2-n1/_scratch/critic-P5-r03/pack` (key in `pack.key.json`, outside the pack; rebuild with `critic_pack_r03.sh <dir>`).
Round-02 verdict was FAILS (4 / 4 / 5 / 4 / 4), biggest gap "hit reaction and impact"; r03 addresses exactly that (local hit-stop, hit shake, flare, victim reaction).

## READ FIRST: state of the machine when this round ended

The GPU wedged at 06:54 EDT (5 engines at once: `slots=5` in `_scratch/gpu/slots` is above the measured ceiling of ~4). At the end of my session: my engine (pid 10060, worktree `sm2-n1/combat`) was SIGTERMed but
blocked in the render thread; my `gpu_slot.py` wrapper (pid 49574) and my chain bash (pid 9165) are **SIGSTOPped on purpose** so that the wrapper's 40-minute max hold cannot SIGKILL the wedged engine
(its `finally` block SIGKILLs the child group: that is how the 23:08 kernel panic happened). Two other agents' engines are `?E` zombies (17555, 17831) and a `CrashReportClient` (pid 4946, not mine) spins at 100 %.
**Before you run anything:** `ps -axo pid,state,command | grep -E "UnrealEditor|CrashReportClient"`. If 10060 is gone, release my slot with `kill -9 9165 49574` (a bash chain and a python wrapper, never an engine; the kernel
frees the flock at once; a stopped process cannot handle SIGTERM, so do NOT SIGCONT the chain: it would launch the next movie). If 10060 is still there, do not launch anything: the slot lock refuses while an
UnrealEditor is stuck exiting. Never `kill -9` an engine or a zombie.
Delete when idle: `_scratch/combat/r03/final1/cap/movie/fight_frames`, `.../final2/movieA/fight_frames` (PNG dumps, ~5 GB each), `unreal/WebHomage/Saved/Screenshots`.

## Rules that bit (read RULES.md, they are real)

- Never SIGKILL a rendering engine; every Unreal launch goes through `_scratch/gpu/bin/gpu_slot.sh capture --label combat -- ...`; one engine of yours at a time; after 2 crashes stop.
- Do not queue two jobs of your own at once. Other agents hold the exclusive perf lock for 5-25 min repeatedly: r03 waits were 1.5-40 min per hold. Batch everything into one hold.
- `gpu_slot.py` never stops a wrapped engine gently: to stop one, SIGTERM the UnrealEditor pid only (or SIGSTOP the wrapper first, as above, when the engine is wedged).
- Do not rebuild (`build_editor.sh` deletes the dylibs) while a job of yours is queued: the job would load half a build. Compile-check only with `Build.sh` when an engine of yours is alive.

## Build and run

```
unreal/WebHomage/Scripts/build_editor.sh                          # C++ only, ~15-35 s (run it with no engine of yours alive)
python3 unreal/WebHomage/Scripts/build_combat.py --steps combat   # /Game/Tests/Combat/Combat_Street + FX materials (M_CmbFlare) from the script (commandlet, ~25 s)
# the whole capture in ONE hold: map rebuild, seed sweep (nullrhi), auto seed pick, freeze, replay, 1080p60 movie, native-4K stills (~15 min hold once it has the slot)
docs/night1/combat/final_r03.sh <work_dir> auto 11 12 13 ... 23
docs/night1/combat/package_r03.sh <work_dir> <picked seed>       # -> round-03 folder (mp4 <= 15 MB, published-mp4 + master measurements, strips); env MOVIE_DIR / STILLS_DIR / REPLAY_DIR for other layouts
docs/night1/combat/critic_pack_r03.sh /Users/midir/sm2-n1/_scratch/critic-P5-rNN
# re-capture the frozen fight with a 2nd hit-feel setting, automatic pick, then stills (one hold, ~25 min):
docs/night1/combat/movie_r03.sh <work_dir> <record_run_dir e.g. .../final1/sweep/seed14> "-WHCmbHoldR=1.5 -WHCmbShakePx=3.5 -WHCmbShakeHz=2.5 -WHCmbVigA=0.8" 3.05,7.01,7.78,8.22,9.37,10.25,15.42,15.65,20.04,26.68
# experiments: exp_r03.sh <work_dir> <movie_seed> <quit_s> <sim seeds...> (movie with -WHCmbSweep=1: each blow cycles variants, logged as 'variant' events; see BlowVariant())
```
Single steps: `run_fight.sh logic|movie|stills <out> <script.json> [times]` (env `WHCMB_RES`, `WHCMB_QUIT`, `WHCMB_LOOK`, `WHCMB_EXTRA` = extra director flags), `sweep_report.py`, `pick_seed.py`,
`sim_metrics.py <run_dir>`, `react_metrics.py <run_dir>` (victim push / twist / launch, no video), `measure_r03.py <movie_dir> out.md out.json [--video mp4 --trim N --strips dir --sheet jpg]`, `replay_diff.py`.
`scripts/fight30_record.json` = reactive record script; `freeze_script.py` turns a record run into fixed times (`scripts/fight30.json` = seed 14 of r03).
Director flags: `-WHCmbScript= -WHCmbFight=mgb -WHCmbDist= -WHCmbOut= -WHCmbShots= -WHCmbShotName= -WHCmbQuit= -WHCmbLook=` and (r03) `-WHCmbShakePx= -WHCmbShakeHz= -WHCmbHoldR= -WHCmbFlareK= -WHCmbFlareI= -WHCmbVigA= -WHCmbSweep=1`.
Live keys in `Combat_Street`: LMB attack (hold = launcher), F web shooter, E web strike, Q finisher, Z heal, C / Ctrl dodge (R throw not ported).

## Code map (`Source/WebHomage/Combat`, port of `src/game/combat`)

| file | what |
|---|---|
| `WHCombatDirector` | fight lifecycle, tokens, ring slots, threats, **local hit-stop** (`HitStop(frames, victim)`: hero dt 0 + `Hero->CustomTimeDilation 0.002`, victim + enemies within `HoldRadius` get `HoldUntil` / `bHeld`), slow-mo (global dilation, slow-mo only), the framing camera (state held during a hold), `HitShake` (roll + zoom quadrature), `ImpactVignette` (off), `BlowVariant`, per-frame record (`fight_frames.jsonl`: camera, shake, hero-held flag, each enemy: box, visual yaw, held), telemetry |
| `WHCombatSpidey` | move set, `TakeHit`, scripted `launcher` action |
| `WHEnemy` | 14 states, warning marker + laser, hit push (`Slide`), **hit twist** (`StartTwist`, `TwistNow`, `VisYaw()`), `HoldUntil` / `bHeld` (director passes dt 0) |
| `WHCombatFx` | pooled shapes: `Hit` (sparks), **`Impact` (flare + sparks, radius from the camera distance)**, dust, web strands, tracers, spider-sense |
| `WHClipStack`, `WHCombatAnim`, `WHCombatHero` | as in r01 |

Determinism: the sim must not read bone poses. In r03 the rendered movie and the stills run reproduced the record run event for event (381 / 381), r02 drifted; still measure the rendered run itself.

## Integration with traversal (no P3 file edited): what P3 should add (unchanged)

1. Control-override hook before traversal integrates. 2. Public `ToAir(VelM)` / `LaunchJump`, sampled jumpPressed. 3. Input swallowing for E / Q / C / F, an `I.combat` flag. 4. Writable orbit yaw / pitch and
`Shake` / `Impact` on the P3 camera. 5. Keep `UWebTravAnimInstance::CreateAnimInstanceProxy`, `FWebTravAnimProxy::Evaluate` / `PreUpdate` virtual, `ClipRoot` public. 6. HeroDev -> P2 hero: the combat clip path follows `ClipRoot`.
New in r03: the hit-stop sets `Hero->CustomTimeDilation` (0.002 while held, 1.0 otherwise): if the integrator's hero is not an `AWHCombatHero` the director must still be able to reach the hero actor.
Manhattan: set `AWHCombatGameMode` as the map's game mode; the map lighting is baked in `build_combat.py`.

## Next (by expected value, after the round-03 critic verdict)

1. Whatever the critic ranks first. My own list, first: **the combined hit test is at 15 / 34 blows** (crop < 1.0: 24 / 34). Run `movie_r03.sh` with the flags above (slower shake, smaller hold radius, edge vignette pulse), read
   `mA.md` / `mB.md` per blow, and iterate; the reasons per failing blow are in `round-03/measure.md` (crop diffs and whole diffs for 8 frames). If a fixed setting cannot reach both clauses, decide with the owner whether
   the neighbours' hold (2.5 m) is acceptable.
2. **Enders** fail most (3 / 15): last blow of a combo, the victim is thrown across the frame. Check the crop box lag for fast victims (`FrameRecord` uses last frame's bones) and the neighbours.
3. Secondary list from the r02 critic, not done: opening shot (pitch 15-25 deg, 0 roll, hero >= 5 % from every edge in the first 3 s), the T-pose on a spawning enemy (`FWHClipStack::Snapshot` skips tracks with env < 0.001), the hero passing
   through enemies (Separate() pushes only enemies), finisher hard cut + 0.3x slow-mo, the copied white chest emblem on the P2 hero mesh (P2 asset).
4. **Look**: procedural boxes, backlit black silhouettes; needs P1 city facades + P4 look (hero rim light `WHLookHeroLight` on the integration branch). The flare reads orange-white on bright surfaces.
5. Not ported: throwables, Space jump-evade, HUD, audio, crime / reinforcement flow, Niagara FX, real Manhattan fight. Perf never measured (`gpu_slot.sh perf` only).
6. Merge `Opus-5.5-Loop-Night-1` into this branch before the next build (not done in r02 / r03).
7. Workspace hygiene (AGENTS.md): after the branch lands, delete `unreal/WebHomage/Intermediate`, `DerivedDataCache`, `Content/` (script-generated) and `_scratch/combat` frame dumps.
