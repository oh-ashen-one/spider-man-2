# P2 Characters: handoff (round 10 IN PROGRESS - interim, rewritten at the end of the round)

> Fan homage project. Not an official Marvel, Sony or Insomniac game. No affiliation. See `DISCLAIMER.md`.

Branch `night1/characters`, worktree `~/sm2-n1/characters`, UE MCP port 8772, browser dev port 5203. Author of round 10: Sonnet 5.5.
Round-09 critic (`critic/round-09-CRITIC.md`, lowest axis 4 = image quality): **biggest gap = in EVERY 8 s fight clip (street_fight_34 AND street_fight_wide, which had 0 knockdowns): >= 4 hit reactions (head / torso >= 0.1 stature within 0.2 s of contact), >= 2 knockdowns with 2 enemies on the ground together >= 1 s, >= 2 distinct get-ups, no enemy holding one guard > 2 s.** Plus a regression: an untextured grey "hero arm" at street_fight_34 1.30 - 1.50 s.

## State when this interim handoff was written (CPU work done, engine work queued)

- Everything below is committed and pushed (`night1/characters`). The content (`/Game/Characters`, `/Game/Tests/Characters`) is NOT committed (script-generated): rebuild with `build_fight.sh` (see Commands). A full `clean` rebuild was QUEUED in the GPU lock behind other agents' jobs (wrapper `build_fight.sh`, nohup, output `_scratch/characters/r10/build.stdout`); if it is gone, queue it again.
- **The "grey arm" is not the hero's arm: it is the Brute's steel PIPE** (bone-log projection: the Brute's hands are at the hero's head at 9.4 s, the pipe passes behind the hero's shoulder and sticks out as a pale tube; CPU render of each actor alone confirms). Round 09's script made the Brute swing it behind the hero at stage 9.25 s, and the pipe texture (galvanised, base (112,116,122)) read white in full sun. Fixes: gunmetal pipe texture (`weapons/weapon_textures.py steel`), and the whole choreography changed (the Brute no longer swings at 9.4 s).
- Choreography v2 (`tools/ue_char/fight/choreo.py`, `fight_script.json`): three 8 s windows (stage 0.65-8.65 wide | 8.65-16.65 3/4 | 16.65-24.65 orbit; shot 0 now lasts 8.6 s: 0.6 s texture warm-up + a full 8 s clip). Per window: 2 knockdowns (Thug + Oxblood | Hood + Beard | Brute + Tee, always two on the ground together 1.8 - 1.95 s), 5 more hit reactions, 2 different get-ups (`getUp` = the hero's backward roll, `getUp2` = NEW elbow-propped sit-up through a squat, authored in `make_fight_clips.py compose_getup2`), one enemy blow that lands (hero flinch), gap filler (`_fillers`: feints / ring shuffles so no enemy keeps one guard pose > ~1.7 s), shove impulse on every reaction, knocked-down bodies end 150 cm from the hero (feet clearance 40 - 50 cm; was 6.9 cm).
- Measured on the SCRIPT's predicted bone log (`preview_cpu.py --bones` -> `fight/r10_check.py`): all three windows PASS (reactions 6-7/7 >= 0.1 stature in 0.2 s, 2 knockdowns, simultaneous 1.84 / 1.84 / 1.95 s, 2 distinct get-ups, longest guard hold 1.37 / 1.75 / 1.27 s). **These are predictions, not results: the real numbers come from the engine bone log (`capture_r5.sh <out> F "" ""` -> `analyze_r10.sh`).**
- Secondary fixes (CPU part done): Hood loose hair-ribbon shells removed (`people/mask.py drop_loose_shells`, 322 triangles; the sunglasses stay), Beard temple hair-curtain gap bridged (`mask.py bridge_hair_gap`, 23 triangles, dark strip) + two-sided Beard / Hood materials (`build_characters.py mi(two_sided=)`), thug nape strip: vertex normals turned to the collar direction (`people/nape_fix.py fix_normals`, they pointed UP = sun-lit) + hue-preserving shade. Not done: hijab walker's rear shin (crowd FBX takes unchanged from round 09), hero brow / nose volume.

## Commands

```
export P2_SCRATCH=/Users/midir/sm2-n1/_scratch/characters UE_WAIT_SKIP=1
bash tools/ue_char/people/build_people.sh                          # street enemies (CPU, ~2.5 min)
python3 tools/ue_char/fight/make_fight_clips.py                    # in-place clip GLB incl. getUp2 + clip_motion.json
python3 tools/ue_char/fight/choreo.py --check                      # fight_script.json + timeline
python3 tools/ue_char/fight/preview_cpu.py --bones OUT.csv && python3 tools/ue_char/fight/r10_check.py OUT.csv OUT.json    # predicted numbers (CPU, ~40 s)
python3 tools/ue_char/fight/preview_cpu.py OUT.png 2.4,3.6 --cam wide|34|orbit --size 960x540                              # CPU render of the real meshes
BUILD_STDOUT=$P2_SCRATCH/r10/build.stdout bash tools/ue_char/fight/build_fight.sh clean,tex,mat,mesh,citizens,rename,fightclips,abp,map,maps5,mapkey,mapavoid
tools/ue_char/capture_r5.sh <out> F "" ""                                                  # fight movies (3 x 8 s) + bone log
STAGE_SHOTS=1 GF_TIMES=4.6,12.0,20.8 tools/ue_char/capture_r5.sh <out> "" gF ""            # 3 stage-exact 4K stills (two enemies down in each)
tools/ue_char/capture_r5.sh <out> "" gE ""                                                 # enemy faces (2 launches)
tools/ue_char/analyze_r10.sh <out> <evidence> <round09 captures>
```
Stop an engine only with `/Users/midir/sm2-n1/_scratch/gpu/bin/stop_ue.sh "/Users/midir/sm2-n1/characters"`; never kill -9 a rendering engine; count engines with `pgrep -x UnrealEditor`.

## Rules that still hold

- The hero is the ORIGINAL "Tessera" suit (procedural, 8192 maps); never revert to or imitate an official suit. Sealed lenses, round-07 crowd avoidance, stencil key, round-06 seam fixes, round-09 scripted fight + its 4 reaction clips all stay.
- No copied IP: enemies / civilians are the owner's own Tripo generations; the fight clips are the browser game's own; weapons are generic primitives. No reference image or footage is committed.

## UPDATE (round 10, after the real re-capture; supersedes the 'engine work queued' state above)

- Found with the real captures: the 'grey arm' of r09 was NOT fully fixed by the gunmetal pipe: the Brute's pipe still passed through the hero's back (grey L-shaped elbow fitting sticking out of his flank, `street_fight_34` 3.25 - 3.45 s) and the Thug's bat through his waist / arm (CPU `fight/weapon_clip_check.py`: bat 5.8 s, pipe 1.4 s of 24 s inside the hero, up to 16 cm).  Fix: `weapons/add_weapon.py` tilt +58 -> -10 deg (swept 0 - 180 deg on the CPU: hero 0.05 s, own head / torso 0.1 - 0.15 s).  Measured on the rebuilt GLBs: bat 0.00 s, pipe 0.00 s, pistol 0.05 s.
- Choreography: two strikes were aimed the wrong way (`enemy_hit` turned the hero toward the attacker before the previous punch landed: hero faced AWAY from the Tee at 3.97 s, facing error 165 deg; 18 deg at 12.73 s).  `choreo.py`: wide window re-timed (enemy_hit 4.50, strikes 5.55 / 6.55 / 7.55, the 8.20 strike dropped), enemy_hit 13.15.  Engine log: worst facing error 3.9 deg over 23 strikes.
- Engine bone log (real game): all three 8 s windows PASS `r10_check.py`.  Numbers in `round-10/SPEC_CHECK.md`.
