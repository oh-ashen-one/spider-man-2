#!/bin/bash
# water r02 hold 3: final water build (params from final_params.json, no variants) + round captures (stills 1080/4K, both dollies)
set -uo pipefail
S=/Users/midir/sm2-n1/_scratch/water; WT=/Users/midir/sm2-n1/water; R=$WT/docs/night1/water/round-02
cd $WT
SM2_WATER_SCR=$S SM2_WATER_EXPORT=$S/manhattan/export/midtown3x3 SM2_WATER_PARAMS="$(cat $S/final_params.json)" SM2_WATER_VARIANTS='{}' \
  python3 unreal/WebHomage/Scripts/build_water.py --steps ue || { echo "HOLD3: water build FAILED"; exit 4; }
SM2_WATER_SCR=$S tools/water/capture_round.sh $R stills water
SM2_WATER_SCR=$S tools/water/capture_round.sh $R movie water
echo "HOLD3 DONE"
