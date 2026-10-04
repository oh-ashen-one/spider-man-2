#!/bin/bash
# final round-02 captures with the committed defaults (variant E): keep the G set aside first
R=/Users/midir/sm2-n1/water/docs/night1/water/round-02; mkdir -p $R/variant_G
for f in $R/*.jpg $R/*.mp4; do [ -f "$f" ] && mv "$f" $R/variant_G/; done
cp /Users/midir/sm2-n1/_scratch/water/final_params.next.json /Users/midir/sm2-n1/_scratch/water/final_params.json
bash /Users/midir/sm2-n1/_scratch/water/hold3.sh
