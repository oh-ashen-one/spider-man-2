# Round 06: captures

> Fan homage project. Not an official Marvel, Sony or Insomniac game. No affiliation.

**Status: no engine capture exists for round 06.** Every Unreal launch of the loop was frozen behind two `UnrealEditor` processes of other agents that stayed stuck in the GPU driver (`?E`, exiting, from 06:22; still there at 08:30, 1 h 32 min): `gpu_slot.sh` refuses all launches while an engine is stuck exiting (RULES.md, 23:08 kernel panic), the GPU read 100 % with no engine running, and this session's queued content build never got a slot. The lock was not bypassed and no process of another agent was touched. `captures/` is therefore empty; nothing here is an engine result.

What exists instead (all OFFLINE, no GPU, clearly not the game):

| File (`evidence/`) | What |
|---|---|
| `offline_ch18_refit_eval.json`, `offline_ch18_round05_eval.json`, `*_summary.txt` | `tools/ue_char/eval/eval_r6.py` on the 18 crowd citizens: round-06 refit meshes vs the round-05 geometry (pack LOD0 + 3 mm expansion + hull), same code, 8 views x (walk clip + idle), 700 px/m |
| `offline_before_after_proxy.jpg` | the three regions of the brief (olive coat, near-lane hand, black-tee armpit) at the same pose, round 05 above, round 06 below (proxy raster: single-sided, textured per triangle) |
| `offline_citizens_montage_270.jpg`, `_90.jpg` | all 18 refit citizens mid-stride from both sides (flat, proxy raster) |
| `keyreport_round05/*.json` | `tools/ue_char/eval/key_report.py` on the round-05 ENGINE chroma-key stills: the baseline the round-06 stills must beat (interior hole components 47 / 31 / 47 / 31; the critic's black-tee armpit hole is component 6 of crowd_key_a: bbox 413,1167 29x14, 279 px) |

To produce the real captures: see "Finish the round" in `../HANDOFF.md` (one build launch + `tools/ue_char/run_r6_captures.sh`). Expected files: `crowd_key_{a,tracking,c,wide}_4k.jpg`, `crowd_tracking_4k.jpg`, `crowd_wide_4k.jpg`, `crowd_tracking.mp4`, `crowd_wide.mp4`, `thug_face_4k.jpg` (+ brute / hood / tee / beard faces), then the hero and fight sets, `crops_3x/*.jpg`.
