# P5 Combat: handoff after round 02

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Branch `night1/combat`, worktree `~/sm2-n1/combat`. UE MCP port 8775, dev port 5206; nothing here uses the editor or MCP: everything is headless commandlets plus `-game`. P5 owns
`Source/WebHomage/Combat`, `/Game/Combat`, `/Game/Tests/Combat`, `Scripts/build_combat.py`, `docs/night1/combat/`. Scratch: `/Users/midir/sm2-n1/_scratch/combat/`.
Evidence: `round-01/`, `round-02/` (`NOTES.md` = every number, `measure.md`, video, stills). `SPEC.md` = numeric targets with the checker for each, `SHOTLIST.md` = views.
**Round 02 has not been scored by a critic.** Blind pack for it: `/Users/midir/sm2-n1/_scratch/critic-P5-r02/pack` (key in `pack.key.json`, outside the pack). The round-01 verdict was FAILS
(3 / 4 / 3 / 3 / 3); r02 fixes its three ranked gaps (hit-stop + reaction, enemy aggression + telegraphs, combat camera): see the table in `round-02/NOTES.md`.

## Rules that bit this round (read RULES.md, they are real)

- 2026-09-29 23:08 kernel panic: never SIGKILL a rendering engine; every Unreal launch (commandlets too) goes through `_scratch/gpu/bin/gpu_slot.sh capture --label combat -- ...`; one engine of yours
  at a time (do NOT queue two of your own jobs: the lock will start both when two slots free up); after 2 crashes stop.
- `gpu_slot.py`'s `finally` block SIGKILLs the child group 0.3 s after the wrapper is terminated, so `stop_ue.sh` on a wrapped run still ends in a SIGKILL. To stop a wrapped engine: SIGTERM the
  UnrealEditor pid only and let the wrapper exit with its child. `run_fight.sh` (end) uses `stop_ue.sh` only for an engine left running after the wrapper returned.
- Other agents hold the exclusive perf lock for 5-15 min repeatedly: expect 5-15 min waits per capture; batch everything into one hold (`final_r02.sh`).

## Build and run

```
unreal/WebHomage/Scripts/build_editor.sh                          # C++ only, ~15 s incremental (run it with no engine of yours alive)
python3 unreal/WebHomage/Scripts/build_combat.py --steps combat   # /Game/Tests/Combat/Combat_Street from the script (commandlet, ~25 s); other steps: cpp, traversal, characters
# the whole capture in ONE hold: map rebuild, seed sweep (nullrhi), auto seed pick, freeze, replay, 1080p60 movie + measure, native-4K stills
docs/night1/combat/final_r02.sh <work_dir> auto 11 12 13 ... 26   # ~15 min hold once it has the slot; results in <work_dir>/{sweep,cap}
docs/night1/combat/package_r02.sh <work_dir> <picked seed>        # -> round-NN folder (edit the round number inside first)
```
Single steps: `run_fight.sh logic|movie|stills <out> <script.json> [times]` (env `WHCMB_RES`, `WHCMB_QUIT`, `WHCMB_LOOK` for quick looks), `sweep.sh` (seed sweep, one hold), `sweep_report.py`, `pick_seed.py`,
`look_sweep.sh <out> <script> <times> <presets file 'name|k=v,...'>` (`-WHCmbLook` keys: sunI sunR/G/B sunPitch sunYaw skyI expBias expMin expMax fogD fogR/G/B lampI fillI sat contrast vig),
`sim_metrics.py <run_dir>` (video-free spec numbers), `measure_r02.py <movie_dir> out.md out.json --sheet boxes.jpg` (pixels), `replay_diff.py`.
Scripts: `scripts/fight30_record.json` is the reactive record script (beats with `react: free|threat|air`, `rel` chains, `launcher` key, `reflex`, `keep` / `reserve`, `hero_armor`,
`hero_min_hp`); `freeze_script.py` turns a record run into fixed times (`scripts/fight30.json`, seed 23). The r01 scripts (`fight25*.json`) still run.
Director flags: `-WHCmbScript= -WHCmbFight=mgb -WHCmbDist= -WHCmbOut= -WHCmbShots= -WHCmbShotName= -WHCmbQuit= -WHCmbLook=`. Live keys in `Combat_Street`: LMB attack (hold = launcher), F web shooter,
E web strike, Q finisher, Z heal, C / Ctrl dodge (R throw not ported).

## Code map (`Source/WebHomage/Combat`, port of `src/game/combat`)

| file | what |
|---|---|
| `WHCombatDirector` | fight lifecycle, tokens (melee up to 3, gun up to 2), ring slots inside the camera arc, threats, `HitStop(frames)` / `Slowmo`, reinforcements, script beats (`rel`, `react`, reflex), the framing camera + finisher push-in + hero-margin controller + lens bubble, `ApplyLook`, per-frame record (`fight_frames.jsonl`: camera + screen box of every character), telemetry |
| `WHCombatSpidey` | move set (strike / launcher / air combo + slam / dive / web strike / yank / dodge / web shooter / finisher / heal), `TakeHit` (`hero_armor`), scripted `launcher` action |
| `WHEnemy` | melee / gunman / brute (scale 1.3, x1.4 wide), 14 states, warning marker + laser (`WarnOn`, `UpdateWarn`), hit push (`Slide`), stumble flinch in the contact frame |
| `WHCombatFx` | pooled shapes: hit sparks (real-time hold for the hit-stop, `HoldFrames`), dust, web strands, tracers, spider-sense streaks |
| `WHClipStack`, `WHCombatAnim`, `WHCombatHero` | as in r01 |

Determinism: the sim must not read bone poses (nullrhi does not refresh them). The camera bubble uses `BubbleP` (camera before the bone-based margin pass) for that reason; still, nullrhi and rendered
runs drift apart after ~7 s (millimetre noise) and the frozen replay is not bit-exact in the movie. Use the nullrhi sweep only to pick a seed; measure the rendered run.

## Integration with traversal (no P3 file edited): what P3 should add (unchanged from r01)

1. Control-override hook before traversal integrates (the director re-places the body every frame with `UWebTraversalComponent::Teleport`). 2. Public `ToAir(VelM)` and `LaunchJump`, expose the
sampled jumpPressed (Space jump-evade not ported). 3. Input swallowing for E / Q / C / F on the frames combat uses them, plus an `I.combat` flag. 4. Writable orbit yaw / pitch and `Shake` / `Impact`
on the P3 camera (combat keeps its own on top). 5. Keep `UWebTravAnimInstance::CreateAnimInstanceProxy`, `FWebTravAnimProxy::Evaluate` / `PreUpdate` virtual and `ClipRoot` public.
6. When P2's hero replaces HeroDev, the combat clip path follows `ClipRoot` (the `A_Hero_` prefix needs a name map).
Manhattan: set `AWHCombatGameMode` as the map's game mode (or subclass it), start fights with `-WHCmbFight=` / a script, the director only needs P3's traversal world index. The map lighting is baked
in `build_combat.py` (Manhattan has its own from P4): the sun-facing penalty and the camera bubble read the `DirectionalLight` at `Init`.

## Next (by expected value, after the round-02 critic verdict)

1. Whatever the critic ranks first. My own list: **slam-landing dust** near-white 3.2 % (limit 3): darker / fewer puffs or shorter life; one light hit that freezes only 2 clean frames (14.27 s);
   the **camera** sits 5.5 m back at the median and 7.5 m at 95 % (the margin controller dollies out: try a narrower hero bbox from fewer bones, or a wider fov instead of dolly);
   24 frames with a dolly step > 0.3 m (max 0.98 m at 14.97 / 29.1 / 32.0 s): rate-limit the hard pass by widening the soft target during flips / finishers.
2. **Look**: procedural boxes, flat; needs P1 city facades + P4 look. Backlit moments give black silhouettes: a hero rim light (P4 `WHLookHeroLight`, on the integration branch) would fix them.
3. Not ported: throwables, Space jump-evade, HUD, audio, crime / reinforcement flow, Niagara FX, real Manhattan fight. Perf was never measured (run under `gpu_slot.sh perf` only).
4. Merge `Opus-5.5-Loop-Night-1` into this branch before the next build (r02 did not: it would have changed the WIP baseline mid-round; the integrator merges night1/combat anyway).
5. Workspace hygiene (AGENTS.md): after the branch lands, delete `unreal/WebHomage/Intermediate`, `DerivedDataCache`, `Content/` (script-generated) and `_scratch/combat` frame dumps.
