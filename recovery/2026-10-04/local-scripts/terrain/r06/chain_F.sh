#!/bin/bash
# r06 final chain: incremental build of /Game/TerrainR6 (STEPS), then the S stills hold and the M movies hold on the SAME content (nothing rebuilt in between),
# then one attempt at an exclusive perf run (exits 75 while the Mac is unattended).
L=/Users/midir/sm2-n1/_scratch/terrain/r06; G=/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh
cd /Users/midir/sm2-n1/terrain || exit 1
if [ -n "${STEPS:-}" ]; then
  echo "build $STEPS start $(date +%H:%M:%S)"
  SM2_TERRAIN_ROOT=/Game/TerrainR6 $G capture --label terrain --timeout 28800 -- tools/terrain/run_build.sh "$STEPS" > $L/buildF.log 2>&1
  echo "build rc=$? $(date +%H:%M:%S)"
  grep -a "build_terrain" /Users/midir/sm2-n1/_scratch/terrain/manhattan/logs/terrain_build.log | grep -c "FAILED\|Traceback"
  sleep 3
fi
STAGE=S TERRAIN_ROOT=/Game/TerrainR6 $G capture --label terrain --timeout 28800 -- docs/night1/terrain/round6.sh > $L/holdS.log 2>&1
echo "S rc=$? $(date +%H:%M:%S)"
[ -e /Users/midir/sm2-n1/_scratch/terrain/capture/STOPPED ] && { echo "S hold stopped: no movies"; exit 4; }
grep -q "WARM-UP SHADER CHECK FAILED" $L/holdS.log && { echo "shader check failed: no movies"; exit 5; }
sleep 5
STAGE=M MOVIE_CRF=${MOVIE_CRF:-30} TERRAIN_ROOT=/Game/TerrainR6 $G capture --label terrain --timeout 28800 -- docs/night1/terrain/round6.sh > $L/holdM.log 2>&1
echo "M rc=$? $(date +%H:%M:%S)"
sleep 5
ioreg -r -d 1 -w 0 -c IOAccelerator | grep -o '"Device Utilization %"=[0-9]*' | head -1 > $L/perf_gpu_util_before.txt
$G perf --label terrain --json docs/night1/terrain/round-06/perf_gpu.json -- unreal/WebHomage/Scripts/run_game.sh /Users/midir/sm2-n1/_scratch/terrain/capture/perf_p1 -map /Game/TerrainR6/Maps/V_p1_south -res 3840x2160 -perf 3:8 -quit 9 -name perf_p1 -timeout 900 -- -notraceserver > $L/perf.log 2>&1
echo "perf rc=$? $(date +%H:%M:%S)"
echo "chain F done $(date +%H:%M:%S)"
