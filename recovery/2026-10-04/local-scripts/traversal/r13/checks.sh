#!/bin/bash
# P3 round 13 checks on the rendered telemetry / movies -> round-13/*.txt (CPU only; sky_check needs opencv from the specv venv)
cd /Users/midir/sm2-n1/traversal/docs/night1/traversal || exit 1
R=round-13; PY=/Users/midir/sm2-n1/_scratch/traversal/specv/bin/python
CL="a_swing_chain b_release_trick_dive_zip c_wallrun_perch d_sprint_jump_first_swing f1_flow_backDouble f2_flow_pikeSwan f3_flow_corkscrew f4_chain_flips f5_canyon_backDouble"
{ echo "# P3 round 13 FLOW CHECK (flow_check.py) on the rendered 1080p60 telemetry + movies, lit /Game/Maps/Manhattan. $(date '+%Y-%m-%d %H:%M')"
  echo "# Homage fan game; not affiliated with Marvel, Sony or Insomniac. Tests: release->first shape <= .25 s, reach->attach <= .3 s, T4 <= 3.1 s, T2 <= 3.3 s, per-frame camera <= 3 deg / 4 deg / 1.2 m, flip-camera blend-out >= .4 s, backDouble <= 2 shapes, hero V."
  for n in $CL; do echo; $PY flow_check.py $R/${n}_telemetry.csv $n --video $R/$n.mp4; $PY /Users/midir/sm2-n1/_scratch/traversal/r13/cutscan.py $R/$n.mp4; python3 /Users/midir/sm2-n1/_scratch/traversal/r13/freeze_scan.py $R/${n}_telemetry.csv; done; } > $R/FLOW_CHECK.txt 2>&1
{ echo "# P3 round 13 FLIP CHECK (flip_check.py, FLIPS_SPEC F1-F5, F7-F11) per clip"; for n in a_swing_chain b_release_trick_dive_zip c_wallrun_perch f1_flow_backDouble f2_flow_pikeSwan f3_flow_corkscrew f4_chain_flips f5_canyon_backDouble; do echo; python3 flip_check.py $R/${n}_telemetry.csv $n; done; } > $R/FLIP_CHECK.txt 2>&1
{ echo "# P3 round 13 sky-ring test (sky_check.py; critic r11 test: >= 70 % of trick frames with >= 50 % sky in a 40 px ring AND hero >= .15 of the frame)"; $PY sky_check.py $R b_release_trick_dive_zip c_wallrun_perch f1_flow_backDouble f2_flow_pikeSwan f3_flow_corkscrew f4_chain_flips f5_canyon_backDouble a_swing_chain; } > $R/SKY_CHECK.txt 2>&1
{ echo "# P3 round 13 apex / flip-camera check (apex_check.py; flow flips start at the release, so 'over the tallest roof' is n/a)"; for n in f1_flow_backDouble f2_flow_pikeSwan f3_flow_corkscrew f4_chain_flips f5_canyon_backDouble a_swing_chain b_release_trick_dive_zip; do python3 apex_check.py $R/${n}_telemetry.csv $n; done; } > $R/APEX_CHECK.txt 2>&1
{ echo "# P3 round 13 anim / camera safety (anim_check.py, cam_check.py)"; for n in $CL; do python3 anim_check.py $R/${n}_telemetry.csv $n 2>&1 | tail -8; python3 cam_check.py $R/${n}_telemetry.csv $n 2>&1 | tail -6; done; } > $R/ANIM_CAM_CHECK.txt 2>&1
echo done; wc -l $R/*.txt
