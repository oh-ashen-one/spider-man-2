#!/bin/bash
# sweep_detect.sh <run name>: YOLO (spec instrument, CPU) on the 5 stills of an r03 sweep run, full frame and 84 % crop, in parallel
N=$1; D=/Users/midir/sm2-n1/_scratch/life/r03/$N; V=/Users/midir/sm2-n1/_scratch/life/venv; W=/Users/midir/sm2-n1/life
source $V/bin/activate
python $W/tools/life/detect_counts.py --device cpu --json $D/det.json $D/${N}_*.jpg 2>&1 | grep -v Warn > $D/det.txt &
python $W/tools/life/detect_counts.py --device cpu --crop 0.84 --json $D/det84.json $D/${N}_*.jpg 2>&1 | grep -v Warn > $D/det84.txt &
wait
echo "$N detected"
