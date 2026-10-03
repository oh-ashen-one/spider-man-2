#!/bin/bash
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# Tricks C r02: after the 4 reel windows merged (capture.sh): stitch the telemetry by window (pixel columns valid everywhere), run the
# SPEC checker into round-02/CHECK.txt (catch line C included), ffprobe every committed part and the local full-length file.
set -euo pipefail
cd "$(dirname "$0")/../.."
R=docs/night1/tricks/round-02
C=/Users/midir/sm2-n1/_scratch/tricks/capture/t60_trick_reel
SEGS="0:15,15:30,30:45,45:61"
python3 tools/tricks/stitch_telemetry.py $C t60_trick_reel "$SEGS" $R/t60_trick_reel_telemetry.csv
gunzip -c $R/t60_trick_reel_pose.csv.gz > /Users/midir/sm2-n1/_scratch/tricks/r02/final_pose.csv
python3 tools/tricks/tricks_check.py $R/t60_trick_reel_telemetry.csv /Users/midir/sm2-n1/_scratch/tricks/r02/final_pose.csv > $R/CHECK.txt
for F in $C/t60_trick_reel_full.mp4 $R/t60_trick_reel_part*.mp4; do
  echo "== $(basename $F)" >> $R/CHECK.txt
  ffprobe -v error -show_entries stream=width,height,r_frame_rate,nb_frames,bit_rate:format=duration,size,bit_rate -of default=nw=1 $F >> $R/CHECK.txt
done
grep -E "^(P|V1|V2|K|L|G1|G2|G3|G4|C|X|G1f|PEN|PIK) " $R/CHECK.txt | grep -E "PASS|FAIL"
