#!/bin/bash
# CPU post-processing of round 03 (no GPU)
WT=/Users/midir/sm2-n1/water; R=$WT/docs/night1/water/round-03; S=/Users/midir/sm2-n1/_scratch/water
cd $WT
python3 -c "
import cv2; im=cv2.imread('$R/river_low_4k.jpg'); cv2.imwrite('$R/crop_river_low_4k_seawall_foam.jpg', im[1250:2160,1500:2700], [cv2.IMWRITE_JPEG_QUALITY, 92])"
python3 tools/water/water_spec.py all $R --json $R/spec.json
mkdir -p $R/iter && for f in $S/iter/r03/*.png; do sips -s format jpeg -s formatOptions 85 "$f" --out "$R/iter/$(basename ${f%.png}).jpg" >/dev/null; done
cp $S/iter/r03/autopick.json $R/iter/ 2>/dev/null
ls -la $R
