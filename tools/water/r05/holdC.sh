#!/bin/bash
# water r05 hold C: (1) the round-05 captures final hold B could not fit, from the SAME content (no rebuild: SKIP_BUILD); (2) last, a rebuild
# with the Dbg 10 variant (debug-only shader branch) and one harbour_high Dbg 10 still. Run ONLY under gpu_slot.sh capture.
S=/Users/midir/sm2-n1/_scratch/water; R5=$S/r05; WT=/Users/midir/sm2-n1/water; UEP=$WT/unreal/WebHomage; T0=$(date +%s)
[ -f /Users/midir/sm2-n1/_scratch/gpu/PAUSED ] && { echo "HOLDC: PAUSED"; exit 6; }
SKIP_BUILD=1 DEADLINE=1700 bash $R5/final.sh
[ $(( $(date +%s) - T0 )) -lt 1300 ] || { echo "HOLDC: no time for Dbg 10"; exit 0; }
[ -f /Users/midir/sm2-n1/_scratch/gpu/PAUSED ] && { echo "HOLDC: PAUSED"; exit 6; }
for _ in $(seq 1 90); do pgrep -f "$UEP/WebHomage.uproject" >/dev/null || break; sleep 1; done
cd $WT
SM2_WATER_SCR=$S SM2_WATER_EXPORT=$S/manhattan/export/midtown3x3 SM2_WATER_PARAMS='{}' SM2_WATER_VARIANTS='{"DBG10": {"Dbg": 10, "_views": ["harbour_high"]}}' \
  python3 unreal/WebHomage/Scripts/build_water.py --steps ue > $R5/build_dbg10.log 2>&1 || { echo "HOLDC: Dbg 10 build FAILED"; exit 4; }
[ $(( $(date +%s) - T0 )) -lt 2040 ] || { echo "HOLDC: no time for the Dbg 10 still"; exit 0; }
cd $UEP; OUT=$S/iter/r05c; mkdir -p $OUT
Scripts/run_game.sh "$OUT/DBG10_harbour_high" -map /Game/Water/Variants/Water_Var_DBG10_harbour_high -res 3840x2160 -shots 16 -name DBG10_harbour_high -exec "r.ScreenPercentage 100" -timeout 220 >/dev/null 2>&1
png=$(ls -t $OUT/DBG10_harbour_high/DBG10_harbour_high_*.png 2>/dev/null | head -1); [ -n "$png" ] && cp "$png" $OUT/DBG10_harbour_high.png && echo "still DBG10 $(date +%T)" || echo "NO STILL DBG10"
for _ in $(seq 1 90); do pgrep -f "$UEP/WebHomage.uproject" >/dev/null || break; sleep 1; done
echo "HOLDC DONE $(date +%T) ($(( $(date +%s) - T0 )) s)"
