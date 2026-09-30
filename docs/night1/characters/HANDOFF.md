# P2 Characters: handoff (round 09, IN PROGRESS until the last line of this file says otherwise)

> Fan homage project. Not an official Marvel, Sony or Insomniac game. No affiliation. See `DISCLAIMER.md`.

Branch `night1/characters`, worktree `~/sm2-n1/characters`, UE MCP port 8772, browser dev port 5203. Author of round 09: Sonnet 5.5.
Round-08 critic (`critic/round-08-CRITIC.md`, all axes 5): **biggest gap = the enemies stand in guard idle for 4 s of `street_fight_34`, 0 knockdowns, 0 hit reactions.**
**Round-09 target (director):** in a re-captured 8 s `street_fight_34` show >= 3 distinct hit reactions, >= 1 knockdown with the torso on the ground >= 1 s, no 1 s window in which all 7 hold guard idle. Secondary: tee-mask see-through holes (198 / 91 / 24 px), 100 x 180 px thug collar skin wedge, rigid civilian coats, the rear shin going horizontal at 18 % of stature.

## State right now (update this block, nothing else, if you only continue)

- Everything below is committed and pushed (`git log -1` on `night1/characters`). `Content/Characters`, `Content/Tests/Characters` are local rebuilt copies (no `.uasset` / `.umap` is committed, no LFS). Scratch: `/Users/midir/sm2-n1/_scratch/characters/` (round-09 work in `r9/`).
- Captures of round 09 go to `/Users/midir/sm2-n1/_scratch/characters/r9/cap` first, then into `docs/night1/characters/round-09/captures/` (mp4 <= 15 MB). If `round-09/CAPTURES.md` does not exist yet, **no engine capture of round 09 has been taken**; the numbers in `round-09/` are then CPU-side only and must not be quoted as game results.
- GPU: every Unreal launch waits in `gpu_slot.sh`'s strict FIFO behind other agents' exclusive perf runs (20 - 40 min per launch today). One engine of mine at a time.

## What round 09 built (the findings worth knowing)

1. **The fight is a SCRIPT, a pure function of the stage clock** (`Source/WebHomage/Characters/WHCharStage.h`: the capture director's shot clock = world time + the offset of `-WHCharShot=N`, so a capture that starts at shot 1 sees the same state as one that plays through shot 0).
   - `FWHScriptBeat` (`WHCharAnimInstance.h`): a timed clip (start, rate, blend in / out, hold, weight) played over the base idle / locomotion; overlapping beats cross-fade (weights normalised), the base gets what is left. `UWHCharAnimInstance::Script`.
   - `FWHPathKey` + `AWHCharLoopWalker::StagePath` / `Script`: a Stand-mode actor's location / yaw are interpolated from keys; the horizontal speed it implies drives the locomotion blend (a walk-in plays the walk clip).
   - `-WHBoneLog=<csv>` (director): per frame and walker the world position of hips / spine2 / head / hands / feet; `tools/ue_char/fight/fight_check.py` reads it.
2. **Clips** (`tools/ue_char/fight/make_fight_clips.py`): the browser game's thug clips carry their travel in the pelvis (stumble back 0.30 m, knockdown 0.53 m, hero get-up 0.53 m). Written IN PLACE (pelvis x / z held at the guard value) as `SK_Street_Fight.glb` (clips `hitBack hitLeft hitRight down getUp`, imported by the build step `fightclips` as `/Game/Characters/People/Anims/A_Fight_*`); the travel is in `clip_motion.json` and becomes the actor's path. The hero's `punch1/2/3 kick uppercut hitReact` and the thug's `thugPunch1/2 thugKick` are used as they are. The thug's own `thugGetUp` dips 0.4 m below the floor: not used (the hero's `getUp` in place is).
3. **Choreography** (`tools/ue_char/fight/choreo.py` -> `fight_script.json`): hero + 6 enemies, 26 s. The hero works round the ring one way (Thug 240 deg, Hood 178, Beard 118, Brute 55, Tee 0, Oxblood 300): no turn > ~62 deg; each target steps in to the strike's reach, is hit at the measured contact instant (hero clips: punch1 0.33 s, punch2 0.27, punch3 0.33, kick 0.30, uppercut 0.25) and reacts 20 ms later (stumble back / left / right, brute flinch = hit reaction at weight 0.55, knockdown held on the ground, get-up), then walks back to its place. Enemies also strike the hero (3 connect: hero flinch). 3 knockdowns in the script (Tee 8.4 s, Thug 12.1 s, Brute 16.3 s, Oxblood 19.6 s = 4). `python3 tools/ue_char/fight/choreo.py --check` prints the timeline, reactions per shot, knockdown intervals, closest approach; `tools/ue_char/fight/preview_cpu.py OUT.png t1,t2 --cam wide|34|orbit` renders the REAL meshes posed and blended like the engine (CPU, ~5 s): use it before spending a GPU launch on any choreography change.
4. **Build**: `tools/ue_char/fight/build_fight.sh clean,tex,mat,mesh,citizens,rename,fightclips,abp,map,maps5,mapkey,mapavoid` = the full idempotent rebuild (~100 s in the lock; `BUILD_STDOUT=<file>` to keep the engine output, the script prints the lock line and the last log lines). Partial builds fail at `abp` if the ABPs already exist (make_abp deletes + recreates; a referenced asset cannot be deleted): always `clean` first. New steps: `fightclips`, `citizenclips`, `peoplemesh` (only useful together with `clean`-less experiments).
5. **Secondary fixes (CPU-side, verified offline, engine frames pending unless CAPTURES.md says otherwise):**
   - tee mask holes: `people/mask.py flip_seethrough` (back-faced lip-crease slivers = see-through through a single-sided mask; ortho raster from 0 / +-28 deg, flip the covering back-facing triangles < 15 mm2). Offline: holes at y 1.609 m x +-6 mm gone. Measure on captures with `tools/ue_char/eval/seethrough_4k.py` (round 08 tee_face_4k: 188 / 72 / 22 px components = the critic's three).
   - thug collar wedge: **reproduced without the engine** (`people/pose_view.py`: skinned walking thug from the lineup's close-up camera) and traced to the neck skin of the nape / side of the neck (bind pose |phi| > 96 deg, y 1.545 - 1.580 m, triangles 4192 - 4220), ABOVE the round-08 texel zone (y < 1.505). Fixed after skinfit by `people/nape_fix.py` (called by build_people.sh): skin-hue texels of those triangles take the hood's shadow. Offline: skin pixels in the wedge box 1046 / 2551 -> 183 / 31 at 1080p. Measure on captures with `tools/ue_char/eval/wedge_4k.py` (round 08: 7336 px component at 1750,1353 - 1844,1525).
   - crowd legs: `tools/ue_char/crowd/lift_cap.py` (hooked into `eval/citizen_rig.load_people`) caps the swing-foot lift of the five crowd walks at 10 % of stature (18.8 % before for walkF); FBX takes re-exported and measured (`round-09/evidence/fbx_lift_citizens.json`: 9.9 - 10.5 %). Long coats were NOT changed (weights already give the hem 50 % thigh influence); the lower rear foot no longer kicks the coat up.
6. **Pipeline facts:** `UE_WAIT_SKIP=1`, never edit a running shell script, kill only by PID (see round-08 notes below); the lock is FIFO: a waiting exclusive `perf` job blocks every later capture even when a slot is free. Changing a camera / choreography after the build started needs a new `clean` build (the wipe happens in the wrapper BEFORE the lock wait, so the content is empty while you queue).

## Commands

```
export P2_SCRATCH=/Users/midir/sm2-n1/_scratch/characters UE_WAIT_SKIP=1
python3 tools/ue_char/fight/make_fight_clips.py                  # in-place clips GLB + clip_motion.json (needs ueimport/SK_Thug.glb)
python3 tools/ue_char/fight/choreo.py --check                    # fight_script.json + timeline / reaction / knockdown report
python3 tools/ue_char/fight/preview_cpu.py /tmp/x.png 3.6,9.6 --cam 34 --size 960x540    # CPU render of the fight with the real meshes
bash tools/ue_char/people/build_people.sh                         # street enemies (tee see-through flip, thug nape fix), ~2 min CPU
bash tools/ue_char/eval/export_citizens.sh <18 names>             # crowd FBX with the lift cap (Blender, CPU)
BUILD_STDOUT=$P2_SCRATCH/r9/build.stdout bash tools/ue_char/fight/build_fight.sh clean,tex,mat,mesh,citizens,rename,fightclips,abp,map,maps5,mapkey,mapavoid
tools/ue_char/run_r9_captures.sh <out> "F E C S"                  # F: fight movies (bone log fight_bones.csv) + 3 4K stills at 3.8 / 9.6 / 21.0 s; E enemy faces; C crowd movies; S crowd stills
python3 tools/ue_char/fight/fight_check.py <out>/fight_bones.csv <out>/fight_check.json --t0 8 --t1 16 --video <clip.mp4> --video-t0 8.05 --cam -660,-335,410,0,0,95,48
python3 tools/ue_char/eval/seethrough_4k.py tee_face_4k.jpg ; python3 tools/ue_char/eval/wedge_4k.py thug_face_4k.jpg
python3 tools/ue_char/make_pairs_r9.py <cap> <round08 cap> <crops> pairs.json ; python3 /Users/midir/spider-man-2-astra6/tools/night1/abpack.py <pack> pairs.json
```
Stop an engine only with `/Users/midir/sm2-n1/_scratch/gpu/bin/stop_ue.sh "<worktree abs path>"`; count engines with `pgrep -x UnrealEditor`. macOS has no `timeout`; the tool shell blocks `sleep` > ~25 s.

## Older rounds (round 08 and before): still true

- The hero is the ORIGINAL "Tessera" suit (procedural, 8192 maps: `tools/ue_char/suit8/`, `hero_suit_r8.py`, eyes `hero_lens_r8.py`); never revert to or imitate an official suit. Sealed lenses, round-07 crowd avoidance, stencil key (`Char_HeroKey`, `-WHFlatClasses`), round-06 seam fixes all stay.
- Hero captures of round 08 (`round-08/captures/hero_*`) are current: nothing of the hero changed in round 09.
- Known problems: suit is dark (52 % ink-teal), amber nets read as fishnet to some eyes; hero showcase framing 0.79H vs CH1 0.48 - 0.62; no run start / stop / turn / idle clips (CH10, SPEC section 5); crowd density 10 - 11 people (CH16 low end, needs > 18 distinct citizens); head-to-head screen contacts in a two-way flow; citizens are low-poly (6 k triangles); performance is not measured (shared GPU, contaminated slots).

## No copied IP (owner rule)

The hero suit is procedural from code. Enemies and civilians: the owner's own Tripo generations (`~/sm2-assets/raw`) and the browser game's own crowd rig; the fight clips are the browser game's own clips (in place) and the hero's own; weapons are generic primitives. No reference image or footage is committed (the critic pack lives in `_scratch`, references stay in the private `~/spiderman-learnings`).
