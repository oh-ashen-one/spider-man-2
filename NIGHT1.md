# Opus 5.5 Loop — Night 1 (ownership contract)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation, nothing here is meant to infringe. See `DISCLAIMER.md`.

Integration branch: **`Opus-5.5-Loop-Night-1`** (worktree `~/spider-man-2-astra6`, owned by the orchestrator session).
Target: Marvel's Spider-Man 2 quality — traversal, Manhattan streets, characters, animation, combat, cohesion.
Hardware: Mac Studio M3 Ultra (80-core GPU, 256 GB). Output target **3840×2160 @ 60 fps**, internal resolution always disclosed, perf measured during real gameplay.

## Pieces and owners

Each piece has its own branch, worktree, Unreal content folder, MCP port and Blender instance. **Only the owner edits its folders.** Shared files (`main.js`, `.uproject`, `Config/Default*.ini`, `Source/WebHomage/WebHomage.Build.cs`) change only through the integrator.

| Piece | Branch | Worktree | UE content / source it owns | MCP port | Browser dev port |
|---|---|---|---|---|---|
| F1 UE C++ foundation | `night1/ue-foundation` | `~/sm2-n1/ue-foundation` | `Source/WebHomage/Core`, Target files, `Config/` (until handed back) | 8770 | — |
| F2 Reference library | (private repo `spiderman-learnings`, branch `night1/refs`) | `~/spiderman-learnings` | `refs/` | — | — |
| F3 Browser baseline + playtest | `night1/browser-baseline` | `~/sm2-n1/browser-baseline` | `docs/night1/baseline/` | — | 5201 |
| P1 City (export + UE city + facades) | `night1/city` | `~/sm2-n1/city` | `tools/export/`, `/Game/City`, `/Game/Tests/City`, `Shaders/City/`, `Scripts/build_city.py`, `Scripts/city_shots.json` | 8771 | 5202 |
| P2 Characters (hero, skins, thugs, crowd) | `night1/characters` | `~/sm2-n1/characters` | `/Game/Characters`, `tools/ue_char/`, `Source/WebHomage/Characters/`, `Scripts/build_characters.py`, Blender work under `art/night1/characters` | 8772 | 5203 |
| P3 Traversal + camera | `night1/traversal` | `~/sm2-n1/traversal` | `Source/WebHomage/Traversal`, `/Game/Traversal`, `/Game/Tests/Traversal` | 8773 | 5204 |
| P4 Look, lighting, post, perf | `night1/look` | `~/sm2-n1/look` | `/Game/Look`, `/Game/Tests/Look`, `tools/perf_ue/` | 8774 | 5205 |
| P5 Combat (wave 2) | `night1/combat` | `~/sm2-n1/combat` | `Source/WebHomage/Combat`, `/Game/Combat` | 8775 | 5206 |
| P6 City life: crowd, traffic, water (wave 2) | `night1/life` | `~/sm2-n1/life` | `/Game/Life`, `/Game/Water` | 8776 | 5207 |
| Integrator / regression playtester | `Opus-5.5-Loop-Night-1` | `~/spider-man-2-astra6` | `/Game/Maps/Manhattan` (main map), merges | 8765 | 5200 |

Evidence goes to `docs/night1/<piece>/round-NN/` (captures, clips, perf CSV, critic verdicts). Large videos are committed as mp4 ≤ 15 MB each.

## Loop per piece

1. Builder builds → runs the real game → captures matching views / movement sequences listed in `docs/night1/<piece>/SHOTLIST.md`.
2. A **fresh critic** (new agent, no builder summary) gets only the rendered captures/clips + the matching Spider-Man 2 references, anonymised A/B where practical, and returns: scores per axis, the **single biggest gap**, and a verdict (`FAILS TARGET` / `APPROACHES TARGET` / `MEETS TARGET`) with evidence.
3. Builder fixes that one gap. Repeat. No fixed round count; a piece closes only on a critic `MEETS TARGET` backed by evidence.
4. Between waves, a fresh integration agent plays the merged game (browser + UE), logs regressions, fixes coherence.

## Protected (never touch)

`~/spider-man-2` (flight-dynamics session), `~/spider-man-2-claude` (3d-animations-astra), `~/spider-man-2-water-effects`, dev ports 5173/5191, Blender MCP port 19891 and any Blender/Unreal instance this loop did not start, branch `main`.

## Model assignment (owner request 2026-09-29: Sonnet 5.5 where it fits, to save usage)

| Role | Model | Why |
|---|---|---|
| Critics (every round, fresh context) | **Opus 5.5** | The verdict is the quality gate; it must stay harsh and trustworthy. |
| P3 Traversal + camera + runtime animator (C++) | **Opus 5.5** | Deep physics/animation C++ with long accumulated context; highest-risk engineering. |
| Integration playtester between waves | **Opus 5.5** | Cross-piece judgment, regression hunting. |
| P1 City, P2 Characters, P4 Look/perf, P5 Combat port, P6 City life, F2 refs, F3 baseline captures | **Sonnet 5.5, extra-high thinking** | Pipeline, content-script, capture and port work driven by concrete critic instructions. |

Sonnet builders run as Workflow agents (`model: 'sonnet', effort: 'xhigh'`), one fresh agent per round. Continuity comes from `docs/night1/<piece>/HANDOFF.md`, which every builder rewrites at the end of its round (state, how to build/capture, open issues, next gap). The agent type `~/.claude/agents/sm2-sonnet-builder.md` does the same for sessions started after 2026-09-29.
