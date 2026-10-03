#!/bin/bash
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# CPU post-processing of round 06 (no GPU): foam / island crops from the final stills, screening stills of holds A-F (<= 1920 px jpg) + their
# numbers, dolly size check, dolly pair table, spec.json / spec.txt.   usage: bash tools/water/r06/post_r06.sh
WT=/Users/midir/sm2-n1/water; R=$WT/docs/night1/water/round-06; S=/Users/midir/sm2-n1/_scratch/water
cd $WT
python3 - <<PY
import cv2, glob, os
R='$R'; S='$S'
im=cv2.imread(R+'/river_low_4k.jpg'); cv2.imwrite(R+'/crop_river_low_4k_seawall_foam.jpg', im[1250:2160,1500:2700], [cv2.IMWRITE_JPEG_QUALITY, 92])
im=cv2.imread(R+'/harbour_high_4k.jpg'); cv2.imwrite(R+'/crop_harbour_high_4k_island_seawall.jpg', im[700:1300,1100:2700], [cv2.IMWRITE_JPEG_QUALITY, 92])
os.makedirs(R+'/iter', exist_ok=True)
keep = {'r06a': ['OFF_rl', 'OFF_rs', 'base_rl', 'base_rs', 'DBG11_rl', 'DBG11_rs', 'S6_rl'], 'r06b': ['DF0_rl', 'DF0_rs', 'R3_rl', 'R4_rl', 'R4_rs'],
        'r06c': ['CB_rl', 'R5_rs', 'P1k_rs'], 'r06d': ['R5_rl', 'K4_rs'], 'r06e': ['base_rs', 'GC_rs'], 'r06f': None}
for d, names in keep.items():
    for f in sorted(glob.glob(S+'/'+d+'/stills/*.png')):
        n=os.path.basename(f)[:-4]
        if names is not None and n not in names: continue
        im=cv2.imread(f); h,w=im.shape[:2]
        if w>1920: im=cv2.resize(im,(1920,int(h*1920/w)),interpolation=cv2.INTER_AREA)
        cv2.imwrite(R+'/iter/'+d[-1]+'_'+n+'.jpg', im, [cv2.IMWRITE_JPEG_QUALITY, 85])
PY
for d in r06a r06b r06c r06d r06e r06f; do [ -d $S/$d/stills ] && python3 tools/water/r06/screen.py $S/$d/stills > $R/iter/screen_$d.txt; done
for n in river_low_dolly river_sun_dolly; do [ -f $R/$n.mp4 ] && echo "$n $(stat -f %z $R/$n.mp4) bytes"; done
python3 tools/water/r05/dolly_pairs.py $R/crop_river_low_4k_seawall_foam.jpg $R/river_low_dolly.mp4 > $R/dolly_pairs.txt 2>&1; tail -1 $R/dolly_pairs.txt
python3 tools/water/water_spec.py all $R --json $R/spec.json > $R/spec.txt 2>&1; grep -E "^(PASS|FAIL)" $R/spec.txt | tail -16
