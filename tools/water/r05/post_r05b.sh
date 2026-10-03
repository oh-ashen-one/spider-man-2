#!/bin/bash
# CPU post-processing of round 05b (no GPU): foam / island crops from the final stills, iteration stills of holds D-F (<= 1920 px jpg), dolly
# size check, dolly pair table, spec.json.   usage: bash tools/water/r05/post_r05b.sh
WT=/Users/midir/sm2-n1/water; R=$WT/docs/night1/water/round-05; S=/Users/midir/sm2-n1/_scratch/water
cd $WT
python3 - <<PY
import cv2, glob, os
R='$R'; S='$S'
im=cv2.imread(R+'/river_low_4k.jpg'); cv2.imwrite(R+'/crop_river_low_4k_seawall_foam.jpg', im[1250:2160,1500:2700], [cv2.IMWRITE_JPEG_QUALITY, 92])
im=cv2.imread(R+'/harbour_high_4k.jpg'); cv2.imwrite(R+'/crop_harbour_high_4k_island_seawall.jpg', im[700:1300,1100:2700], [cv2.IMWRITE_JPEG_QUALITY, 92])
os.makedirs(R+'/iter', exist_ok=True)
for pre, d in (('e_', S+'/r05e/stills'), ('f_', S+'/r05f/stills')):
    for f in sorted(glob.glob(d+'/*.png')):
        im=cv2.imread(f); h,w=im.shape[:2]
        if w>1920: im=cv2.resize(im,(1920,int(h*1920/w)),interpolation=cv2.INTER_AREA)
        cv2.imwrite(R+'/iter/'+pre+os.path.basename(f)[:-4]+'.jpg', im, [cv2.IMWRITE_JPEG_QUALITY, 85])
PY
for d in r05e r05f; do for f in report.json; do [ -f $S/$d/$f ] && cp $S/$d/$f $R/iter/${d}_$f; done; done
for n in river_low_dolly river_sun_dolly; do [ -f $R/$n.mp4 ] && echo "$n $(stat -f %z $R/$n.mp4) bytes"; done
python3 tools/water/r05/dolly_pairs.py $R/crop_river_low_4k_seawall_foam.jpg $R/river_low_dolly.mp4 > $R/dolly_pairs.txt 2>&1; tail -1 $R/dolly_pairs.txt
python3 tools/water/water_spec.py all $R --json $R/spec.json > $R/spec.txt 2>&1; grep -E "^(PASS|FAIL)" $R/spec.txt
