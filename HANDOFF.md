# HANDOFF — Opus 5.5 Loop (Night 1 → Day 2)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Rolling handoff for any session that picks this loop up (the orchestrating session may stop at any time — weekly usage was 80 % on 2026-09-30). **Read this, then `NIGHT1.md` (ownership + model policy) and `docs/night1/RULES.md` (safety) before touching anything.** Verify state with git; this file can lag by one round.

## What this is

The owner's overnight goal: enhance the homage browser game (public fork `oh-ashen-one/spider-man-2`) and port it to **Unreal Engine 5.8.3** toward *Marvel's Spider-Man 2* quality — traversal, Manhattan, characters, animation, combat, look, 4K/60 — through a **build → capture → blind Opus critic → fix** loop per piece (method: the public skill `oh-ashen-one/claude-code-game-builder`, installed at `~/.claude/skills/claude-code-game-builder`).

- Integration branch: **`Opus-5.5-Loop-Night-1`**, worktree `~/spider-man-2-astra6` (this file). Never merge to `main` without the owner.
- Each piece has its own branch + worktree under `~/sm2-n1/<piece>` (table in `NIGHT1.md`). Only that piece's builder edits its folders; the integrator merges into `Opus-5.5-Loop-Night-1`.
- Unreal content is **not committed** (no LFS). Every map/asset is rebuilt by committed scripts: `unreal/WebHomage/Scripts/build_manhattan.py` (city + traversal + characters + look + map, ~12 min), then `build_water.py`, `build_life.py`, `build_combat.py`. Showcase recipe: `~/sm2-n1/_scratch/showcase/build.sh` (separate scratch dirs so it never collides with builders).
- Progress page (owner-facing): https://claude.ai/artifact/BprMUxvQ4dZs4pfCoT8aCE — data `docs/night1/progress.json`, ledger `docs/night1/model-ledger.json`, render `python3 tools/night1/progress.py` (prints the files map), record a round with `tools/night1/record_round.py '<json>'`.
- Owner flips request: `docs/night1/traversal/FLIPS_BRIEF.md` (gymnast-quality flips; reference clip local only at `~/sm2-n1/_scratch/refs/owner/flips_owner_2026-09-29.mov` — never commit it).

## Piece status (2026-09-30 ~10:40)

| Piece | Branch | Last judged round → verdict (lowest axis) | Next |
|---|---|---|---|
| P3 Traversal + flips | `night1/traversal` | r15 merged (flips 7, camera 5). r17 (branch): **no axis below 6**, camera 6, sky 79%, tricks above the roofs; flips 6 — not merged yet | **r18 running (Opus)**: limbs keep moving through every trick (pose.py 0 slow samples), distinct inverted shapes; flips ≥ 7 |
| P2 Characters | `night1/characters` | r8 merged (all 5). r10 (branch): fight fixed (6–7 reactions, 2 knockdowns, 2 get-ups), enemies 6, IQ 4 — not merged | **r11–r12 running (Opus)**: hair assets + collar wedge, IQ ≥ 5 |
| F 4K/60 perf | `night1/perf` | r5 **APPROACHES** (merged). r6: life-on **median 61.5 fps PASS**, p95 53–54.5 fps fail; undisclosed foliage loss → **r6 NOT merged** | **r7 running (Opus)**: committed look_gate.py first; remove life-on frame-pacing bubble; restore foliage |
| P1 City | `night1/city` | r9 FAILS (4) | r10: rebuild the S4 far-shore city band (varied heights, seawall/piers) |
| P6 City life | `night1/life` | r2 FAILS (4); r3 code only (no renders) | r3 renders: both sidewalks populated at every camera height |
| P5 Combat | `night1/combat` | r3 FAILS (4) | **r4–r5 running (Opus)**: additive impact burst, every blow moves the victim |
| P4 Look | `night1/look` | r3 FAILS (4) | **r4–r5 running (Opus)**: golden key/fill contrast, night windows |
| Water | merged (Opus A/B winner) | — | — |

Merged into integration so far: traversal ≤ r15, city ≤ r9, life ≤ r3, perf ≤ r5. Characters ≤ r8 and traversal ≤ r13 merged after their critics.

## How rounds run

Workflow script (Claude Code Workflow tool), one per piece, parameterised by args:
`~/.claude/projects/-Users-midir-spider-man-2-astra6/16227b43-7e09-4f35-8b47-d0626c6efd77/workflows/scripts/sm2-night-piece-loop-wf_b4ca0126-c9a.js`
Args: `{P, name, wt, branch, docs, startRound, maxRounds, resume, opusFrom?, kind?('perf'), firstTarget, extra?, criticExtra?}`. Builder = Sonnet 5.5 xhigh unless `r >= opusFrom` (then Opus 5.5 high); critic = always a fresh blind Opus 5.5 high agent. The builder writes `/Users/midir/sm2-n1/_scratch/critic-<P>-r<NN>/pairs.json` and runs `tools/night1/abpack.py`; the critic never sees builder notes or the pack key. Critic verdicts land in `docs/night1/<piece>/critic/round-NN-CRITIC.md` on the piece branch.

After a workflow finishes: `git merge origin/night1/<piece>` into integration, `record_round.py`, regenerate + republish the progress page, push.

**Model policy (owner, 2026-10-01 01:30, latest): mostly Opus 5.5 + a healthy share of Sonnet 5.5; Opus critics; Fable 5.1 directs (see NIGHT1.md + director/PLAN-night2.md). Older note —** split building between **Opus 5.5 high** (traversal/flips, combat, perf, integration — hard engineering) and **Sonnet 5.5 xhigh** (city, life, look, character assets, pipelines); **critics always Opus 5.5 high, never skipped**; Fable 5.1 only for stall diagnosis / final acceptance (own weekly limit). Weekly usage was 80 % — prefer one round per piece at a time.

## Safety (read `docs/night1/RULES.md`; global rules merged in oh-ashen-one/agents-md#4)

- Every Unreal launch goes through `/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture|perf --label <piece> -- <cmd>`. **Hard cap 1** heavy renderer since 2026-10-01 02:02 (`_scratch/gpu/slots`; `_scratch/gpu/health_monitor.sh` clamps to 1, auto-pauses and stops the newest `-game` on GPU-pinned / WindowServer-starved signals). `_scratch/gpu/PAUSED` blocks every launch; the lock also refuses while any UnrealEditor is stuck exiting (`ps` stat E/Z).
- Stop engines with `_scratch/gpu/bin/stop_ue.sh "<your worktree>"` (drivers first, SIGTERM, 60 s, SIGKILL last). `run_game.sh` timeouts now do the same.
- Never launch UnrealInsights / UnrealTraceServer / any new network-listening tool unattended (firewall prompt froze the screen on 2026-09-30). Firewall already allows UnrealEditor, UnrealEditor-Cmd, UnrealInsights, zenserver, Python, Node.
- Watchdog (orchestrator's): `_scratch/gpu/watchdog.sh` prints one line per new danger (stuck engine, GPU ≥98 % with 3+ engines, dead desktop session, system dialog). If the desktop session dies (WindowServer reset): create `PAUSED`, commit + push every worktree, notify the owner — agents cannot repair it.
- Incidents so far: 2026-09-29 16:43 WindowServer reset (11 engines); 23:08 kernel panic (SIGKILLed 4K engine stuck in the GPU driver); 2026-09-30 06:55 WindowServer reset (4 engines at 100 % GPU) with a firewall dialog on screen → owner power-off; **2026-10-01 02:02 WindowServer reset with only 2 engines** (GPU pinned 2 min → WS main thread stuck in a Metal submit, WS CPU fell to ~1 %) → desktop session restarted, the orchestrating Claude session died at 02:05, loop idle until 06:37. Run the orchestrator in `tmux`. Lessons: `~/claude-code-game-builder/references/lessons-log.md`.
- Other sessions are active on this machine (`~/spider-man-2`, `~/spider-man-2-claude`, `~/spider-man-2-water-effects`, a Codex MLX model, the shared-brain work in `~/.agents-md`). Never touch their processes, ports or folders.

## Resume checklist for a new session

1. `git -C ~/spider-man-2-astra6 pull`; for each `~/sm2-n1/<piece>`: `git status`, `git log @{u}..HEAD` — commit + push any WIP (`WIP night1/<piece>: ...`).
2. Check no engine is stuck (`ps -axo pid,stat,comm | grep -i unrealeditor`), no `PAUSED` unless intended, health monitor running (`pgrep -f health_monitor`), `cat _scratch/gpu/slots` = 2.
3. Check which workflows finished (piece branches' latest `critic/round-NN-CRITIC.md`), merge judged rounds into integration, record them, republish the progress page.
4. Relaunch the next round per piece with the workflow script above, following "Next" in the table and the model policy.
5. Keep this file current: update the table after every merge and push.

- 2026-10-01 00:05: owner actively using the Studio (Steam/CrossOver, EXO). Loop engine cap lowered to **1** (`_scratch/gpu/slots`; health_monitor max 1) until the owner says otherwise. Restore with: edit health_monitor.sh `slots -lt 1` → `-lt 2`, `echo 2 > slots`, restart the monitor.

## Overnight 2026-10-01 (owner: "keep cooking"; plays the build in the morning)

- Running: traversal r18 (Opus, living flips), perf r7 (Opus, life-on pacing + look_gate.py), characters r10 (Sonnet, reactions + grey arm), city r10–r11 (Sonnet, far-shore band), life r3–r4 (Sonnet, sidewalk crowds). Relaunch each piece's next round from its latest critic when it finishes; merge only rounds with no regression.
- Engine cap is 1 while the owner's Steam/CrossOver is open; `_scratch/gpu/cap_restore.sh` returns it to 2 after 15 quiet minutes.
- **Before the owner wakes:** stop launching new rounds ~1 h ahead, merge judged rounds, rebuild the combined map headless (`~/sm2-n1/_scratch/showcase/build.sh`, plus `build_combat.py --steps combat` if combat moved), and DO NOT open a window — the owner will say when to launch the playable build (standalone `-game -windowed -ResX=1920 -ResY=1080`, mouse sensitivity via `wh.MouseSensitivity`).

- 2026-10-01 01:25: owner asleep, asked for max safe load: engine cap 2 (hard rule), seven pieces running in parallel (CPU-side work fills the gaps). Fixed a health_monitor bug where STRAIN raised the cap from 1 to 2 (min was hard-coded 2; now min 1, max 2).

- Fable night-2 plan: `docs/night1/director/PLAN-night2.md` (60% Opus). **Cut-off: no new round launches after 07:30; critics finished by 08:30; headless rebuild + acceptance checklist by 09:30** (morning acceptance pass = Fable 5.1 max). Characters r12 and look r5 run on Opus (launched before the plan; plan said Sonnet) — every later round goes through the Fable director step built into the loop script.
- **Owner schedule (2026-10-01, supersedes the cut-off above): run until ~09:00 EST, then open the playable build.** 06:30 no new launches · 07:30 wrap-up: Fable 5.1 max acceptance pass → `docs/night1/director/ACCEPTANCE-morning.md` (merge list + what to try), merges, headless rebuild (`~/sm2-n1/_scratch/showcase/build.sh`, combat step, `add_life.py`) by ~08:50 · 09:00 open the standalone game window once (`-game -windowed -ResX=1920 -ResY=1080`) and post controls + overnight summary. These are session timers in the orchestrating Claude session; a replacement session must do them by hand.

- **2026-10-01 06:40 (new orchestrator session after the 02:02 reset):** WIP pushed on traversal (0702b68), perf (009d005), city (c05187a), life (f6db782); orphaned perf `chain_ab2.sh` stopped by PID; cap 1 + governor live; PAUSED kept until the Fable triage picks what to finish before the 09:00 build.
- **2026-10-01 06:50 Fable 5.1 morning triage (after the 02:02 reset):** merged combat r3 (fc185e8) and look r3 (fb10b8a) into integration. Traversal r17 and characters r10 NOT merged (flips 7→6, IQ 5→4); the 09:00 build ships characters r8, perf r5 preset. In flight, cap 1: blind Opus critics on traversal r18 (merge HEAD 0702b68 only if flips ≥ 7 and no axis below r15 [7,5,6,6,6]) and life r3 (≥ r2 [5,5,5,4,4]); Sonnet building the city r10 pack (then Opus critic, ≥ r9 [5,5,4,5,5]); Sonnet finishing combat r4 captures on the single GPU slot (then Opus critic, every axis ≥ r3). Everything else resumes tonight. PAUSED lifted 06:50 (moved to PAUSED.lifted-0700).
- **07:13 merges done (Fable rules):** integration now has traversal r18 (cdc7ae9, hero suit forced to the original Tessera material), city r10 (ad93a86), life r3 (d87a224), combat r3+r4 (b2a3636), look r3. Not merged: traversal r17, characters r9-r10 (IQ 5→4), perf r6-r7. **build_manhattan.py fixed** (ce1c659): it predated city r08-r10 and never ran export_vehicles/street_cars/street_trees/street_traffic/far_skyline/bake_sunmask or the kit/fsky steps — new `city_extra` step + one city pass. Morning rebuild: `~/sm2-n1/_scratch/showcase/morning_build.sh` (MB_STEPS=... to resume; log morning_build.log). After it: S4 far-band guard (tools/export/s4_far_check.py; revert city if T1 < 12 px or T2 > 38.7 %), visual check the hero shows the Tessera suit (no copied emblem), then open the game at 09:00.
- **Next round targets (from the critics):** traversal r19 vary each trick ±10-20 % + tight tuck ≥0.25 s; city r11 S4 far-tower window grid, far band ≤10 % >204; life r4 plant the feet (stance ≤10 cm/s); combat r5 camera + lighting (hero ≥35 % frame, no backlit opening); characters r11 hair + collar, IQ ≥5; look r4 golden key/fill contrast; perf r7 life-on pacing under look_gate.py. All at cap 1 (serial GPU).
- **07:50 build accepted (Fable a784607, docs/night1/director/ACCEPTANCE-morning.md).** Checks on the rebuilt content: S4 far band T2 0.8 % / T1 18.6 px (city kept; C12/C13 fail = look r4's job); Manhattan hero = original Tessera suit; Combat_Street white-glow hero fixed (146c92c: the traversal hero fill light, tuned for the 26-44 klux Manhattan sun, was ~150x the 10 lux combat sun → AWHCombatHero zeroes it; hero now reads backlit/dark — combat r5 lighting target). 09:00: open standalone `-game -windowed -ResX=1920 -ResY=1080` on /Game/Maps/Manhattan for the owner.
- **2026-10-01 13:00 FIRST PASS started (owner: "the highest-quality version of web slinging around the highest-quality version of Manhattan"; plan docs/night1/director/PLAN-firstpass.md, priorities OWNER-PRIORITIES.md).** Running loop workflows (builder -> blind Opus critic -> Fable director): traversal r19-20 (Opus; owner playtest bugs: swing breaks, E-zip from wall-run, wall-run anim, swing/air anim, mouse dies; then trick variation + tight tuck), island r1-2 (new branch night1/island, worktree ~/sm2-n1/island; Opus; full-island export spike + streaming + collision), sky/look r5-6 (Opus; continuous time of day), skins/characters r11-12 (Sonnet; original suit generator + swap). Disk-reclaim agent freeing regenerable scratch (70 GB free; island needs >= 150-250). Paused: combat, life, perf (perf folds into island milestones). Owner playtest fixes already on integration: mouse 0.0025 rad/px + capture (ed0bee5, 4a07dc7), settings menu + PS5 pad + graphics (48030a0), combat hero fill (146c92c), traversal collision = per-building boxes only (690dfa7). Playable launch for the owner's 3440x1440: Epic, 55 % res, V-sync off, perf60_hwl2 dpcvars + r.Lumen.ScreenProbeGather.DownsampleFactor=32 (~40+ fps; integrated build lacks perf_apply content steps — LumenScreenProbeGather 18 ms otherwise).
- **2026-10-01 14:26 Studio restart (owner's GTA V alone starved WindowServer; no loop engine was rendering).** Orchestrator session died; at 14:40 a new session committed leftover WIP (traversal 5d62690, look 6f37618), restarted health_monitor (not a LaunchAgent — restart it by hand after any reboot: `cd ~/sm2-n1/_scratch/gpu && nohup ./health_monitor.sh &`), lifted PAUSED and relaunched the 4 first-pass workflows with resume:true (traversal r20, island r1, look r5, characters r11). Traversal r19 FAILED (swing 6, camera 4 < r18) — not merged. SD-card move of AFC folders resumed with a verify that ignores exFAT ._ files (originals untouched until verified).
