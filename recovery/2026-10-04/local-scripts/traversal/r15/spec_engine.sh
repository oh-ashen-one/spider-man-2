#!/bin/bash
cd /Users/midir/sm2-n1/traversal/docs/night1/traversal || exit 1
R=round-15; LAY=/Users/midir/sm2-n1/_scratch/traversal/manhattan/export/midtown3x3/layout.json
{ echo "# TRAVERSAL-SPEC engine-side check, round 15 — lit /Game/Maps/Manhattan (golden), 1080p60 telemetry; generated $(date '+%Y-%m-%d %H:%M')"
echo "# (homage fan game; not affiliated with Marvel, Sony or Insomniac). Video instruments (YOLO / vp_cam / nearflow) NOT run this round."
for S in "a_swing_chain 0.4 15.6" "b_release_trick_dive_zip 0 7" "c_wallrun_perch 0 10.5" "d_sprint_jump_first_swing 2.6 12"; do
  set -- $S; N=$1
  echo; echo "================ $N (window $2-$3 s)"
  echo "---- T1-T4 / T7 (rhythm_check.py)"; python3 rhythm_check.py $R/${N}_telemetry.csv $LAY $2 $3 2>&1 | tail -25
  echo "---- T8-T14, T16, T19 (spec_cam_check.py, AVENUE_YAW=90)"; AVENUE_YAW=90 python3 spec_cam_check.py $R/${N}_telemetry.csv $N $2 $3 2>&1 | tail -25
done
echo; echo "================ c wall-run (T22)"; python3 wall_check.py $R/c_wallrun_perch_telemetry.csv c 2>&1 | tail -8; } > $R/SPEC_CHECK.txt 2>&1
