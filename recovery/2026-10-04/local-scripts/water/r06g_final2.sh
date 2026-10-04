#!/bin/bash
# round-06 final: hold 1 builds (BUILT differs) + 4K stills + river_low dolly; hold 2 (SKIP_BUILD) river_sun dolly + 1080p stills; hold 3 if needed
cd ~/sm2-n1/water
for h in 1 2 3; do
  while [ -f /Users/midir/sm2-n1/_scratch/gpu/PAUSED ]; do sleep 20; done
  [ $h -gt 1 ] && export SKIP_BUILD=1
  echo "=== final hold $h $(date +%T)"
  /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label water --timeout 2400 -- bash tools/water/r06/final_g.sh
  echo "=== final hold $h exit $? $(date +%T)"
  n=0; for f in river_low_4k.jpg river_sun_4k.jpg harbour_high_4k.jpg harbour_sun_high_4k.jpg S4_golden_4k.jpg river_low_dolly.mp4 river_sun_dolly.mp4 river_low_1080.jpg river_sun_1080.jpg harbour_high_1080.jpg harbour_sun_high_1080.jpg S4_golden_1080.jpg; do
    [ "docs/night1/water/round-06/$f" -nt /Users/midir/sm2-n1/_scratch/water/r06g/BUILT ] && n=$((n+1)); done
  echo "outputs newer than BUILT: $n / 12"; [ $n -ge 12 ] && break
  sleep 10
done
echo "=== FINAL CHAIN DONE $(date +%T)"
