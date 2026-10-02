#!/bin/bash
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P3 round 25 critic pack (like with like): the swing chain both halves (round target: rope readable on every web frame, over pale facades
# at 0.9-1.1 s and dark glass at 10.5-11.2 s) vs the two reference chase chains, the c roof turn -> zip -> perch (owner bug 5 gate) vs a golden
# rooftop perch, the pawn run (cadence hard line) vs the reference chase-cam run, a multi-flip control, and r24 vs r25 on the same chain window.
# Refcuts are scratch-only copies (from the private refs), never committed.
set -euo pipefail
R=/Users/midir/sm2-n1/traversal/docs/night1/traversal/round-25
R24=/Users/midir/sm2-n1/traversal/docs/night1/traversal/round-24
REFS=/Users/midir/spiderman-learnings/refs
C=/Users/midir/sm2-n1/_scratch/critic-P3-r25
X=$C/ours; mkdir -p $X $C/refcuts
cp -n /Users/midir/sm2-n1/_scratch/critic-P3-r24/refcuts/*.mp4 $C/refcuts/ 2>/dev/null || true
cut() { ffmpeg -loglevel error -y -ss "$3" -i "$2" -t "$4" -an -vf "crop=1186:1080:(iw-1186)/2:0,scale=610:556" -c:v libx264 -crf 18 -pix_fmt yuv420p "$X/$1.mp4"; }
refcut() { ffmpeg -loglevel error -y -ss "$3" -i "$2" -t "$4" -an -vf "crop=ih*1186/1080:ih:(iw-ih*1186/1080)/2:0,scale=610:556" -c:v libx264 -crf 18 -pix_fmt yuv420p "$C/refcuts/$1.mp4"; }
[ -f $C/refcuts/run_chase.mp4 ] || refcut run_chase $REFS/animation/clips/run-toward-camera__dn_0418-0425.mp4 0 7
[ -f $C/refcuts/perch_golden.mp4 ] || refcut perch_golden $REFS/streets/clips/skyline-perch-golden__nm_0844-0852.mp4 0 3.5
cut swing_1 $R/a_swing_chain.mp4 0.5 8.0
cut swing_2 $R/a_swing_chain.mp4 7.5 8.0
cut perch_c $R/c_wallrun_perch.mp4 7.4 3.4
cut run_p1 $R/p1_pawn_run.mp4 2.0 7.0
cut multi_flip $R/f1_flow_backDouble.mp4 0.9 6.0
cut swing_r24 $R24/a_swing_chain.mp4 7.5 8.0
cut swing_r25 $R/a_swing_chain.mp4 7.5 8.0
cat > $C/pairs.json <<JSON
[
 {"id":"swing-chain-1","x":"$X/swing_1.mp4","y":"$C/refcuts/swing_chase.mp4","note":"fast web-swinging down a street canyon: can you follow the web line from the hand to the frame edge on every frame, over sky, pale stone and dark glass; arc altitude and the poses between webs"},
 {"id":"swing-chain-2","x":"$X/swing_2.mp4","y":"$C/refcuts/S45_chain.mp4","note":"fast web-swinging down a street canyon: can you follow the web line from the hand to the frame edge on every frame, over sky, pale stone and dark glass; arc altitude and the poses between webs"},
 {"id":"rooftop-perch","x":"$X/perch_c.mp4","y":"$C/refcuts/perch_golden.mp4","note":"on a rooftop: the camera framing while the hero stands, zips to a ledge and perches (is he always in frame, does the view jump)"},
 {"id":"street-run","x":"$X/run_p1.mp4","y":"$C/refcuts/run_chase.mp4","note":"the hero running down a street seen from behind: step rhythm, stride, body motion"},
 {"id":"multi-flip","x":"$X/multi_flip.mp4","y":"$C/refcuts/S3_multi.mp4","note":"web release into an airborne pass with several somersaults, then back onto a web"},
 {"id":"progress-swing","x":"$X/swing_r25.mp4","y":"$X/swing_r24.mp4","note":"two versions of our game: the same swing chain from the same start -- which web line reads better, which is the better swing"}
]
JSON
cp $C/pairs.json $C/pairs.with_paths.json
python3 /Users/midir/spider-man-2-astra6/tools/night1/abpack.py $C/pack $C/pairs.json
