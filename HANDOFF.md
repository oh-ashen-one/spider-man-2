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
| P3 Traversal + flips | `night1/traversal` | r13 FAILS (5); flips 4→6→6→6; flow fixed | **r14 running (Opus)**: side-on trick camera + eased rotation |
| P2 Characters | `night1/characters` | r6 FAILS (4); seam holes fixed in engine | **r7 running (Sonnet)**: walker avoidance, last key see-through, floating polygon |
| F 4K/60 perf | `night1/perf` | r2 **APPROACHES** (p50 62.4 / p95 55.4 fps at 3840×2160, TSR 46 % = 1766×994) | **r3 running**: move preset into the shipped Manhattan map, remove CPU/GPU sync stall, glass SSIM ≥ 0.97 |
| P1 City | `night1/city` | r9 FAILS (4) | r10: rebuild the S4 far-shore city band (varied heights, seawall/piers) |
| P6 City life | `night1/life` | r2 FAILS (4); r3 code only (no renders) | r3 renders: both sidewalks populated at every camera height |
| P5 Combat | `night1/combat` | r2 FAILS (4); r3 judged, r4 WIP | resume r4 from HANDOFF (local hit-stop, starburst FX) |
| P4 Look | `night1/look` | r2 FAILS (4); r3 presets v2 captured | r3 critic / r4 |
| Water | merged (Opus A/B winner) | — | — |

Merged into integration so far: traversal ≤ r13, city ≤ r9, life ≤ r3, perf ≤ r2. Characters ≤ r6 and traversal ≤ r13 merged after their critics.

## How rounds run

Workflow script (Claude Code Workflow tool), one per piece, parameterised by args:
`~/.claude/projects/-Users-midir-spider-man-2-astra6/16227b43-7e09-4f35-8b47-d0626c6efd77/workflows/scripts/sm2-night-piece-loop-wf_b4ca0126-c9a.js`
Args: `{P, name, wt, branch, docs, startRound, maxRounds, resume, opusFrom?, kind?('perf'), firstTarget, extra?, criticExtra?}`. Builder = Sonnet 5.5 xhigh unless `r >= opusFrom` (then Opus 5.5 high); critic = always a fresh blind Opus 5.5 high agent. The builder writes `/Users/midir/sm2-n1/_scratch/critic-<P>-r<NN>/pairs.json` and runs `tools/night1/abpack.py`; the critic never sees builder notes or the pack key. Critic verdicts land in `docs/night1/<piece>/critic/round-NN-CRITIC.md` on the piece branch.

After a workflow finishes: `git merge origin/night1/<piece>` into integration, `record_round.py`, regenerate + republish the progress page, push.

**Model policy (owner, 2026-09-30 latest):** split building between **Opus 5.5 high** (traversal/flips, combat, perf, integration — hard engineering) and **Sonnet 5.5 xhigh** (city, life, look, character assets, pipelines); **critics always Opus 5.5 high, never skipped**; Fable 5.1 only for stall diagnosis / final acceptance (own weekly limit). Weekly usage was 80 % — prefer one round per piece at a time.

## Safety (read `docs/night1/RULES.md`; global rules merged in oh-ashen-one/agents-md#4)

- Every Unreal launch goes through `/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture|perf --label <piece> -- <cmd>`. **Hard cap 2** heavy renderers (`_scratch/gpu/slots`, health monitor `_scratch/gpu/health_monitor.sh` never raises above 2). `_scratch/gpu/PAUSED` blocks every launch; the lock also refuses while any UnrealEditor is stuck exiting (`ps` stat E/Z).
- Stop engines with `_scratch/gpu/bin/stop_ue.sh "<your worktree>"` (drivers first, SIGTERM, 60 s, SIGKILL last). `run_game.sh` timeouts now do the same.
- Never launch UnrealInsights / UnrealTraceServer / any new network-listening tool unattended (firewall prompt froze the screen on 2026-09-30). Firewall already allows UnrealEditor, UnrealEditor-Cmd, UnrealInsights, zenserver, Python, Node.
- Watchdog (orchestrator's): `_scratch/gpu/watchdog.sh` prints one line per new danger (stuck engine, GPU ≥98 % with 3+ engines, dead desktop session, system dialog). If the desktop session dies (WindowServer reset): create `PAUSED`, commit + push every worktree, notify the owner — agents cannot repair it.
- Incidents so far: 2026-09-29 16:43 WindowServer reset (11 engines); 23:08 kernel panic (SIGKILLed 4K engine stuck in the GPU driver); 2026-09-30 06:55 WindowServer reset (4 engines at 100 % GPU) with a firewall dialog on screen → owner power-off. Lessons: `~/claude-code-game-builder/references/lessons-log.md`.
- Other sessions are active on this machine (`~/spider-man-2`, `~/spider-man-2-claude`, `~/spider-man-2-water-effects`, a Codex MLX model, the shared-brain work in `~/.agents-md`). Never touch their processes, ports or folders.

## Resume checklist for a new session

1. `git -C ~/spider-man-2-astra6 pull`; for each `~/sm2-n1/<piece>`: `git status`, `git log @{u}..HEAD` — commit + push any WIP (`WIP night1/<piece>: ...`).
2. Check no engine is stuck (`ps -axo pid,stat,comm | grep -i unrealeditor`), no `PAUSED` unless intended, health monitor running (`pgrep -f health_monitor`), `cat _scratch/gpu/slots` = 2.
3. Check which workflows finished (piece branches' latest `critic/round-NN-CRITIC.md`), merge judged rounds into integration, record them, republish the progress page.
4. Relaunch the next round per piece with the workflow script above, following "Next" in the table and the model policy.
5. Keep this file current: update the table after every merge and push.
