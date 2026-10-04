#!/bin/bash
# water r02, GPU hold 1 (one slot, sequential): Manhattan rebuild commandlets + water build + 1080p iteration stills.
# Run ONLY through: gpu_slot.sh capture --label water -- bash hold1.sh   (nested gpu_slot calls pass through)
set -uo pipefail
S=/Users/midir/sm2-n1/_scratch/water; WT=/Users/midir/sm2-n1/water
cd $WT
if [ ! -f $S/hold1.skip_city ]; then
  python3 $S/run_manhattan.py --steps city,traversal,characters,look,map || { echo "HOLD1: manhattan build FAILED"; exit 3; }
fi
SM2_WATER_SCR=$S SM2_WATER_EXPORT=$S/manhattan/export/midtown3x3 SM2_WATER_VARIANTS="$(cat $S/variants.json 2>/dev/null)" \
  python3 unreal/WebHomage/Scripts/build_water.py --steps ue || { echo "HOLD1: water build FAILED"; exit 4; }
$S/iter_stills.sh || { echo "HOLD1: iteration stills aborted"; exit 9; }
if [ -f $S/auto_final ]; then
  python3 $S/autopick.py && bash $S/hold3.sh
fi
echo "HOLD1 DONE"
