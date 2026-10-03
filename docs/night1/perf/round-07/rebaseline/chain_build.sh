#!/bin/zsh
# Piece F round 07 (re-baseline): rebuild the integrated content in THIS worktree with the integrator's morning-build order
# (build_manhattan -> build_water -> build_life -> add_life -> build_combat), F scratch dirs, every Unreal launch inside gpu_slot.sh capture.
# As-found: preset block OFF, no perf_apply. Then F's extra still view S7 (make_views.py).
set -e
WT=/Users/midir/sm2-n1/perf
S=/Users/midir/sm2-n1/_scratch/perf
G=/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh
UE="/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor"
UP=$WT/unreal/WebHomage/WebHomage.uproject
cd $WT
export SM2_MANHATTAN_SCR=$S SM2_WATER_SCR=$S/water SM2_LIFE_SCR=$S/life SM2_LIFE_EXPORT=$S/export/midtown3x3 SM2_COMBAT_SCR=$S/combat
FROM=${FROM:-1}
st() { echo "== $(date +%H:%M:%S) step $1 $2"; }
if [ $FROM -le 1 ]; then st 1 preset_off; python3 tools/perf_ue2/build_map.py --preset-off; fi
if [ $FROM -le 2 ]; then st 2 city_export,city_prep,city_extra; python3 tools/perf_ue2/build_map.py --steps city_export,city_prep,city_extra; fi
# capture holds run at background QoS (taskpolicy -b) and are cut at 40 min: the one-pass city step needed > 40 min with a cold DDC (cut after
# 'kit actors' on 2026-10-03 19:39), so the city rest (kit,fsky,map) runs as its own hold and the other steps one per hold.
if [ $FROM -le 3 ]; then st 3 city_rest; $G capture --label perf --timeout 21600 -- python3 $S/r07b/city_rest.py ${CITY_REST:-kit,fsky,map}; fi
if [ $FROM -le 4 ]; then st 4 traversal; $G capture --label perf --timeout 21600 -- python3 tools/perf_ue2/build_map.py --steps traversal
  st 4b characters; $G capture --label perf --timeout 21600 -- python3 tools/perf_ue2/build_map.py --steps characters; fi
if [ $FROM -le 5 ]; then st 5 look; $G capture --label perf --timeout 21600 -- python3 tools/perf_ue2/build_map.py --steps look
  st 5b map; $G capture --label perf --timeout 21600 -- python3 tools/perf_ue2/build_map.py --steps map; fi
if [ $FROM -le 6 ]; then st 6 water; $G capture --label perf --timeout 21600 -- python3 unreal/WebHomage/Scripts/build_water.py; fi
if [ $FROM -le 7 ]; then st 7 life_prep; python3 unreal/WebHomage/Scripts/build_life.py --steps prep; fi
if [ $FROM -le 8 ]; then st 8 life_content_map; $G capture --label perf --timeout 21600 -- python3 unreal/WebHomage/Scripts/build_life.py --steps content,map; fi
if [ $FROM -le 9 ]; then st 9 add_life
  $G capture --label perf --timeout 21600 -- "$UE" "$UP" -run=pythonscript -script=$WT/tools/perf_ue2/add_life.py -unattended -nullrhi -nosplash -RenderOffScreen -NoSound -NoCrashReports -abslog=$S/logs/add_life.log > /dev/null 2>&1
  grep -E '\[showcase\]' $S/logs/add_life.log; fi
if [ $FROM -le 10 ]; then st 10 combat; SM2_COMBAT_NOWAIT=1 $G capture --label perf --timeout 21600 -- python3 unreal/WebHomage/Scripts/build_combat.py --steps combat; fi
if [ $FROM -le 11 ]; then st 11 views_S7
  SM2_PERF_VIEWS=S7 $G capture --label perf --timeout 21600 -- "$UE" "$UP" -run=pythonscript -script=$WT/tools/perf_ue2/make_views.py -unattended -nullrhi -nosplash -RenderOffScreen -NoSound -NoCrashReports -abslog=$S/logs/make_views.log > /dev/null 2>&1
  grep -E '\[perf_views\]' $S/logs/make_views.log; fi
echo "== $(date +%H:%M:%S) BUILD DONE"
