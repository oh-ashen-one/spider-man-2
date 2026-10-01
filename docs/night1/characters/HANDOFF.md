# P2 Characters: handoff (end of round 10)

> Fan homage project. Not an official Marvel, Sony or Insomniac game. No affiliation. See `DISCLAIMER.md`.

Branch `night1/characters`, worktree `~/sm2-n1/characters`, UE MCP port 8772, browser dev port 5203. Author of round 10: Sonnet 5.5. Everything below is committed and pushed (`origin/night1/characters`); the content (`/Game/Characters`, `/Game/Tests/Characters`) is NOT committed (script-generated, rebuild with `build_fight.sh`, see Commands). Numbers: `round-10/SPEC_CHECK.md`; provenance: `round-10/CAPTURES.md`.

## Round 11 IN PROGRESS (interim note, Opus 5.5, 2026-10-01 02:10)

Target (critic r10, lowest axis image quality 4): one hair asset per head, no colour seam > 40 px inside the hair, no flat card > 20 px, no background between hair and skin
(hood / beard / tee faces at 4K); thug collar: no skin-toned blob > 15 x 15 px.  Done on the CPU side (committed): `tools/ue_char/people/hair.py` (Hood blond -> maroon `unify_hair`;
Beard / Tee hair shell: `tuck_hair` edges onto the head, `paint_scalp` (scalp under the shell + the shell's own baked-skin texels -> hair colour), Beard `compress_hair`; the r10
`bridge_gap` flat card removed), `nape_fix.py` (strip -> the hood's own dark), checker `eval/hair_4k.py`, `crops_r11.py`, `make_pairs_r11.py`, `analyze_r11.sh`.
Engine chain `$P2_SCRATCH/r11/chain.sh` (build -> gE faces -> F fight movie -> gF stills) was queued in the GPU lock at 02:00 (PID in `$P2_SCRATCH/r11/chain.pid`).
If this note is still here, the round did not finish: rebuild with build_people.sh + build_fight.sh (full steps) and re-run the chain.

## Where the round stands

Round-09 critic (`critic/round-09-CRITIC.md`, lowest axis 4 = image quality): biggest gap = in EVERY 8 s fight clip >= 4 hit reactions (head / torso >= 0.1 stature within 0.2 s of contact), >= 2 knockdowns with 2 enemies down together >= 1 s, >= 2 distinct get-ups, no enemy holding one guard > 2 s; plus an "untextured grey hero arm" at 1.30 - 1.50 s.

Round 10 (measured on the real game's bone log, `fight/r10_check.py`; YOLO cross-check `fight/video_grounded.py`):

| | wide | 3/4 | orbit |
|---|---|---|---|
| hit reactions >= 0.1 stature in 0.2 s | 6 / 6 | 7 / 7 | 7 / 7 |
| knockdowns (>= 1 s) | 2 | 2 | 2 |
| two enemies down together | 1.84 s (YOLO 2.0) | 1.84 s (1.6) | 1.94 s (2.4) |
| distinct get-ups | 2 | 2 | 2 |
| longest guard hold | 1.40 s | 1.82 s | 1.98 s |

Round 09 on the same instrument: 0 knockdowns in wide, 0.00 s together in 3/4, guard holds 3.6 - 4.4 s, one get-up kind.

- **The "grey arm" was the Brute's steel pipe** passing through the hero's back (grey elbow fitting sticking out of his flank); the Thug's bat also went through him. The gunmetal pipe colour of the first round-10 pass was not enough. Fix: `weapons/add_weapon.py` tilt +58 -> -10 deg (bat / pipe rise beside the fist instead of pointing at the hero). CPU check `fight/weapon_clip_check.py`: bat 5.8 s -> 0 s, pipe 1.4 s -> 0 s of 24 s inside the hero's body. Proof: `round-10/captures/crops_3x/r10_arm.jpg`, `r10_hero_*.jpg`.
- **Two strikes were aimed the wrong way** (found only on the engine log, not on the script's predicted log): `enemy_hit` made the hero face its attacker before his own previous punch landed (165 deg away from the Tee at 3.97 s). Re-timed in `choreo.py`; worst facing error at the contact over 23 strikes is now 3.9 deg (`evidence/facing_check.json`).
- Secondary: Hood hair ribbons removed (a 40 px wisp above the crown remains), Beard temple gap bridged with a dark card, tee holes 0 (>= 20 px). **Thug collar wedge NOT fixed** (3,136 px at 4K, round 09 1,790, round 08 7,336: the round-10 normals / shade change made it worse by the metric). Hijab walker's rear shin NOT changed. Hero head brow / nose volume NOT done.

## Open items for the next round (priority order)

1. Thug collar wedge: the strip of nape skin between the hair line and the hood collar (`people/nape_fix.py`). Albedo darkening (round 09), then normals + hue-preserving shade (round 10) did not remove a lit tan plane in the engine. Ideas not tried: shade the strip's texels to the hood's own hue and saturation (not a darker skin), or move the strip's three triangles' vertices into the hood collar. Iterate on `people/pose_view.py` first (CPU, no engine), then measure with `eval/wedge_4k.py` on a real `thug_face_4k.jpg`.
2. Hijab walker's rear shin: the five crowd walks have a swing shin >= 30 deg from horizontal after `crowd/lift_cap.py` (knee 0.38 - 0.40 m, ankle 0.17 m above the planted ankle). A flatter-looking toe-off needs a shorter stride, which means foot slide unless the walkers' speeds are scaled with it.
3. Hero head: brow and nose volume (critic r08 / r09), hero showcase framing (CH1), run start / stop / turn / idle (CH10, section 5 of the spec).
4. Orbit guard hold is 1.98 s (limit 2.0): add a filler for the Tee between 17.2 and 18.6 s (`choreo.py _fillers` leaves gaps below its 1.7 s threshold) if the critic measures stricter.
5. Hood's stray wisp above the crown (`people/mask.py drop_loose_shells` threshold).

## Commands

```
export P2_SCRATCH=/Users/midir/sm2-n1/_scratch/characters UE_WAIT_SKIP=1
bash tools/ue_char/people/build_people.sh                          # street enemies + weapon fit (CPU, ~3 min)
python3 tools/ue_char/fight/make_fight_clips.py                    # in-place clip GLB incl. getUp2 + clip_motion.json (only when the clips change)
python3 tools/ue_char/fight/choreo.py --check                      # writes fight_script.json + timeline
python3 tools/ue_char/fight/preview_cpu.py --bones OUT.csv && python3 tools/ue_char/fight/r10_check.py OUT.csv OUT.json    # PREDICTED numbers (CPU, ~40 s); then ALWAYS look at an engine capture: the prediction cannot see aim or weapon problems
python3 tools/ue_char/fight/weapon_clip_check.py OUT.json         # weapons through the hero's body (CPU, ~13 s, real skinned meshes)
python3 tools/ue_char/fight/preview_cpu.py OUT.png 2.4,3.6 --cam wide|34|orbit --size 960x540                              # CPU render of the real meshes (matches the engine frame closely)
BUILD_STDOUT=$P2_SCRATCH/rN/build.stdout bash tools/ue_char/fight/build_fight.sh clean,tex,mat,mesh,citizens,rename,fightclips,abp,map,maps5,mapkey,mapavoid   # wipes /Game/Characters first, then waits for the lock: never launch a capture while it is queued
tools/ue_char/capture_r5.sh <out> F "" ""                                                  # fight movies (3 x 8 s) + bone log (needs an EMPTY <out>/segF_frames; ~7 min run, 3 GB of frames)
STAGE_SHOTS=1 GF_TIMES=4.6,12.0,20.8 tools/ue_char/capture_r5.sh <out> "" gF ""            # 3 stage-exact 4K stills (two enemies down in each)
tools/ue_char/capture_r5.sh <out> "" gE ""                                                 # enemy faces (2 launches)
tools/ue_char/analyze_r10.sh <out> <evidence> <round09 captures>                           # r10_check, contact_check, video activity, YOLO counts, face metrics
$P2_SCRATCH/r4/yv/bin/python tools/ue_char/fight/video_grounded.py clip.mp4 out.json        # pixel check of the knockdowns
python3 tools/ue_char/crops_r10.py <captures> <round09 captures> <out>                      # 3x crops (hero-centred strips at 1.30 / 1.40 / 1.50 s, faces)
python3 tools/ue_char/make_pairs_r10.py <captures> <abs round09 captures> <abs crops dir> <pairs.json>; python3 /Users/midir/spider-man-2-astra6/tools/night1/abpack.py <pack dir> <pairs.json>
```
Stop an engine only with `/Users/midir/sm2-n1/_scratch/gpu/bin/stop_ue.sh "/Users/midir/sm2-n1/characters"`; never kill -9 a rendering engine; count engines with `pgrep -x UnrealEditor`. Every launch waits in the lock's FIFO (cap 1 - 2 slots; 7 - 26 min per launch this round): start the chain in the background (`nohup`, record the PID) and do CPU work meanwhile.

## How the fight script works (`tools/ue_char/fight/`)

- `choreo.py` writes `fight_script.json`: hero + 6 enemies, a pure function of the stage clock (`Source/WebHomage/Characters/WHCharStage.h`, `FWHScriptBeat`, `FWHPathKey`). `strike(t0, hero_clip, target, reaction)` = the target steps in, the hero turns (`face`), strikes, the target reacts 20 ms after the contact (`down` = knockdown held on the ground until `getup=`); `enemy_hit(t0, who, clip)` = an enemy blow that lands (the hero flinches). **A hero turn belongs 0.05 s after the previous punch's contact at the earliest: `enemy_hit` turns the hero from t0 - 0.35 s.** `_fillers()` inserts feints / shuffles into idle gaps (guard hold <= ~2 s).
- Three 8 s windows: stage 0.65 - 8.65 (wide) | 8.65 - 16.65 (3/4) | 16.65 - 24.65 (orbit). Per window: 2 knockdowns (two enemies down together), 2 different get-ups (`getUp` = backward roll, `getUp2` = sit-up), 4 - 5 more reactions, one enemy blow that lands.
- `r10_check.py` = the critic's numbers on a bone log (`-WHBoneLog`), `contact_check.py` = fist / foot to the victim's head, `weapon_clip_check.py` = weapons through the hero, `video_activity.py` / `video_grounded.py` = pixels.

## Rules that still hold

- The hero is the ORIGINAL "Tessera" suit (procedural, 8192 maps); never revert to or imitate an official suit. Sealed lenses, round-07 crowd avoidance, stencil key, round-06 seam fixes, round-09 scripted fight + its 4 reaction clips all stay.
- No copied IP: enemies / civilians are the owner's own Tripo generations; the fight clips are the browser game's own; weapons are generic primitives. No reference image or footage is committed.
- Never `kill -9` a rendering engine, never launch UnrealInsights / TraceServer-style listeners, never pkill by pattern: PIDs only. After any engine crash twice: stop and report.
