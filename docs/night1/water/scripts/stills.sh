#!/bin/bash
# final stills through the GPU lock: <name> <map> -> docs/night1/water/round-01/<name>_{4k,1080}.jpg
R=/Users/midir/sm2-n1/water-ab-sonnet/docs/night1/water/round-01
CAP=/Users/midir/sm2-n1/_scratch/water-sonnet/cap
for spec in "$@"; do
  NAME="${spec%%=*}"; MAP="${spec#*=}"
  for RES in 3840x2160 1920x1080; do
    TAG=$([ "$RES" = 3840x2160 ] && echo 4k || echo 1080)
    /Users/midir/sm2-n1/_scratch/water-sonnet/cap.sh f_${NAME}_${TAG} "$MAP" $RES -shots 28 -exec "r.ScreenPercentage 100" | head -1
    P=$(ls $CAP/f_${NAME}_${TAG}/f_${NAME}_${TAG}_00_*.png | head -1)
    python3 -c "
from PIL import Image
Image.open('$P').convert('RGB').save('$R/${NAME}_${TAG}.jpg', quality=92, subsampling=0)
print('$R/${NAME}_${TAG}.jpg')"
  done
done
