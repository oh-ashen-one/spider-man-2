#!/bin/bash
# water r04: after the capture hold ends successfully, ONE exclusive perf hold (native 100 %, 6 maps). Own driver script: stop_ue.sh kills it first.
S=/Users/midir/sm2-n1/_scratch/water; WT=/Users/midir/sm2-n1/water; R=$WT/docs/night1/water/round-04
HP=$(cat $S/r04/hold.pid)
while kill -0 $HP 2>/dev/null; do sleep 20; done
grep -q "HOLD r04 DONE" $S/r04/hold.log || { echo "capture hold did not finish; no perf run"; exit 3; }
mkdir -p $R
ioreg -r -d 1 -c IOAccelerator | grep -o '"Device Utilization %"=[0-9]*' | head -1 > $S/r04/perf_util_before.txt
rm -rf $S/cap/perf_r04
GPU_SLOT_PERF_WAIT_TIMEOUT=14400 /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh perf --label water --json $R/perf_gpu.json -- bash -c "
  T0=\$(date +%s)
  for m in Water_View_RiverLow Water_Perf_RiverLow_Base Water_View_RiverSun Water_Perf_RiverSun_Base Water_Perf_S4 Water_Perf_S4_Base; do
    [ \$(( \$(date +%s) - T0 )) -gt 720 ] && { echo \"perf: out of time before \$m\"; break; }
    python3 '$WT/tools/perf_ue/run_perf.py' --out '$S/cap/perf_r04/'\$m --map /Game/Water/Maps/\$m --script none --configs native100 --res 3840x2160 --window 16:31 --timeout 300 --name \$m || echo \"perf \$m failed\"
  done"
/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh summary $R/perf_gpu.json
python3 $WT/tools/water/perf_summary.py $S/cap/perf_r04 native100 $R/perf.json
echo PERF CHAIN DONE
