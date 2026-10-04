#!/bin/bash
# CPU post-processing of round 05 (no GPU): foam crop, iteration stills (1920 px jpg), dolly size check, spec.json
WT=/Users/midir/sm2-n1/water; R=$WT/docs/night1/water/round-05; S=/Users/midir/sm2-n1/_scratch/water
cd $WT
python3 -c "
import cv2; im=cv2.imread('$R/river_low_4k.jpg'); cv2.imwrite('$R/crop_river_low_4k_seawall_foam.jpg', im[1250:2160,1500:2700], [cv2.IMWRITE_JPEG_QUALITY, 92])
im=cv2.imread('$R/harbour_high_4k.jpg'); cv2.imwrite('$R/crop_harbour_high_4k_island_seawall.jpg', im[700:1300,1100:2700], [cv2.IMWRITE_JPEG_QUALITY, 92])"
mkdir -p $R/iter
python3 - <<PY
import cv2, glob, os, shutil
for pre, d in (('h1_', '$S/iter/r05a'), ('h2_', '$S/iter/r05b'), ('h3_', '$S/iter/r05c')):
    for f in sorted(glob.glob(d + '/*.png')):
        im = cv2.imread(f); h, w = im.shape[:2]
        if w > 1920: im = cv2.resize(im, (1920, int(h * 1920 / w)), interpolation=cv2.INTER_AREA)
        cv2.imwrite('$R/iter/' + pre + os.path.basename(f)[:-4] + '.jpg', im, [cv2.IMWRITE_JPEG_QUALITY, 85])
    for f in ('report.json', 'report.txt', 'autopick.json'):
        if os.path.exists(d + '/' + f): shutil.copy(d + '/' + f, '$R/iter/' + pre + f)
    for g in glob.glob(d + '/DBG9_river_low/*_t0*.png'):
        cv2.imwrite('$R/iter/' + pre + os.path.basename(g)[:-4] + '.jpg', cv2.imread(g), [cv2.IMWRITE_JPEG_QUALITY, 90])
PY
for n in river_low_dolly river_sun_dolly; do
  sz=$(stat -f %z $R/$n.mp4 2>/dev/null || echo 0)
  if [ "$sz" -gt 15000000 ]; then
    ffmpeg -loglevel error -y -framerate 60 -start_number 359 -i "$S/cap/$n/dolly_frames/MovieFrame%05d.png" -frames:v 600 \
      -c:v libx264 -pix_fmt yuv420p -crf 23 -preset slow -movflags +faststart "$R/$n.mp4"; echo "$n re-encoded at CRF 23: $(stat -f %z $R/$n.mp4)"
  fi
done
python3 tools/water/water_spec.py all $R --json $R/spec.json
ls -la $R
