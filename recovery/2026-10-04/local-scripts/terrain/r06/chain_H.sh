#!/bin/bash
# r06 diagnostic after the final package: VB_p10 (city alone, no terrain) at the p10 camera, to see whether the smooth 'single big leaf' at (1139-1190, 237-280) is a city object
L=/Users/midir/sm2-n1/_scratch/terrain/r06; G=/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh
while kill -0 $(cat $L/chain_G.pid) 2>/dev/null; do sleep 20; done
cd /Users/midir/sm2-n1/terrain || exit 1
O=/Users/midir/sm2-n1/_scratch/terrain/capture/VB_p10_lawn_eye; rm -rf "$O"
$G capture --label terrain --timeout 28800 -- unreal/WebHomage/Scripts/run_game.sh "$O" -map /Game/TerrainR6/Maps/VB_p10_lawn_eye -res 3840x2160 -shots 2 -quit 3 -name VB_p10_lawn_eye -timeout 1500 -- -benchmark -fps=30 -notraceserver > $L/vb_p10.log 2>&1
echo "VB rc=$? $(date +%H:%M:%S)"
for p in "$O"/VB_p10_lawn_eye_*.png; do [ -f "$p" ] && sips -s format jpeg -s formatOptions 90 "$p" --out /Users/midir/sm2-n1/terrain/docs/night1/terrain/round-06/diag/base_p10_lawn_eye.jpg >/dev/null; done
echo "chain H done $(date +%H:%M:%S)"
