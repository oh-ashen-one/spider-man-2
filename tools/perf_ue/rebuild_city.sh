#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P4 wrapper around P1's city pipeline (tools/export, unchanged) using P4's own port 5205 and scratch dir, so it never touches
# P1's dev server (5202), editor (8771), export or chrome profile.  Round 04: headless commandlets (no editor, no MCP), and it mirrors
# P1's tools/export/build_city.sh round 09 (street cars / trees / traffic, vehicles, sunmask height field for the canyon shade fill).
#   usage: tools/perf_ue/rebuild_city.sh prep     CPU only: vite on 5205, export_city.mjs (headless Chrome) -> <SCR>/export/midtown3x3, P1 prep chain
#          tools/perf_ue/rebuild_city.sh ue       Unreal: build_city.py one pass (clean,tex,mat,mesh,proto,kit,fsky,map, as build_manhattan.py), then rebuild_look.sh geo,rigs,night,maps (all presets incl. tod)
#                                                 wrap it in ONE slot hold:  gpu_slot.sh capture --label look -- tools/perf_ue/rebuild_city.sh ue
#          tools/perf_ue/rebuild_city.sh all      both (SKIP_EXPORT=1 reuses the export)
# Env: SM2_LOOK_SCRATCH (default /Users/midir/sm2-n1/_scratch/look), SM2_LOOK_DEV_PORT (5205).  Your editor must be closed (one Unreal process per agent).
set -e
WT="$(cd "$(dirname "$0")/../.." && pwd)"; cd "$WT"
SCR=${SM2_LOOK_SCRATCH:-/Users/midir/sm2-n1/_scratch/look}; mkdir -p $SCR/logs; export SM2_LOOK_SCRATCH=$SCR
DEVP=${SM2_LOOK_DEV_PORT:-5205}
export SM2_CITY_SCRATCH=$SCR SM2_CITY_PORT=$DEVP SM2_CITY_EXPORT=$SCR/export/midtown3x3 SM2_CITY_TEX=$SCR/tex
EXPD=$SCR/export/midtown3x3/
PHASE=${1:-all}
UEBIN="/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor"
UPROJECT="$WT/unreal/WebHomage/WebHomage.uproject"

prep() {
  [ -d node_modules ] || npm ci
  VITE_PID=""
  if ! curl -s -o /dev/null http://127.0.0.1:$DEVP/; then
    npx vite --port $DEVP --host 127.0.0.1 --strictPort > $SCR/logs/vite.log 2>&1 &
    VITE_PID=$!; sleep 5
  fi
  [ -n "$SKIP_EXPORT" ] || node tools/export/export_city.mjs --url http://127.0.0.1:$DEVP/ --out $SCR/export/midtown3x3 --profile $SCR/chrome-profile
  [ -n "$VITE_PID" ] && kill -TERM $VITE_PID 2>/dev/null || true      # our own vite only (by PID)
  sed -i '' "s#127.0.0.1:$DEVP/#127.0.0.1:5202/#g" $EXPD/manifest.json
  python3 tools/export/patch_export.py $EXPD
  mkdir -p $SCR/tex/maps; python3 tools/export/prep_textures.py $SCR/tex $EXPD/manifest.json
  python3 tools/export/gen_street_signs.py $SCR/tex/street_signs.png
  python3 tools/export/street_kit.py $EXPD
  python3 tools/export/street_props.py $EXPD
  python3 tools/export/export_vehicles.py $EXPD
  python3 tools/export/street_cars.py $EXPD
  python3 tools/export/street_trees.py $EXPD
  python3 tools/export/street_traffic.py $EXPD
  python3 tools/export/far_skyline.py               # (r05) mirror build_manhattan.py city_extra: far skyline (2 km merged tiles, seawall, tree clumps)
  mkdir -p $SCR/r09 $SCR/tex/maps; python3 tools/export/bake_sunmask.py $EXPD $SCR/tex
  node tools/export/gen_shaders.mjs
}

commandlet() {   # name, python prelude (headless -nullrhi commandlet running build_city.py unchanged)
  local job=$SCR/uejobs/$1.py log=$SCR/logs/$1.log
  mkdir -p $SCR/uejobs
  printf '%s\n__file__ = %s\nexec(compile(open(__file__).read(), __file__, "exec"))\n' "$2" "'$WT/unreal/WebHomage/Scripts/build_city.py'" > $job
  echo "[rebuild_city $(date +%H:%M:%S)] commandlet $1 -> $log"
  "$UEBIN" "$UPROJECT" -run=pythonscript -script=$job -unattended -nullrhi -nosplash -RenderOffScreen -NoSound -NoCrashReports -abslog=$log > $log.stdout 2>&1 || true
  if grep -q "LogPython: Error\|Traceback" $log; then grep -m 20 "LogPython: Error\|Traceback" $log; echo "python error in $1"; return 1; fi
  grep "\[build_city" $log | tail -3 | sed 's/^.*LogPython: //'
}

ue() {
  if pgrep -f "MacOS/UnrealEditor $UPROJECT" > /dev/null; then echo "an Unreal process of this worktree is running: stop it with stop_ue.sh first"; exit 2; fi
  PRE='import os, unreal
os.environ["SM2_CITY_EXPORT"] = "'$SCR'/export/midtown3x3"; os.environ["SM2_CITY_TEX"] = "'$SCR'/tex"
unreal.SystemLibrary.execute_console_command(None, "Module Load StaticMeshEditor")'
  commandlet city_pass1 "$PRE
JOB_ARGS = {\"steps\": \"clean,tex,mat,mesh,proto,kit,fsky,map\"}"     # (r05) one pass in build_city.py's default order, like build_manhattan.py step city
  "$WT/tools/perf_ue/rebuild_look.sh" geo,rigs,night,maps
}

case $PHASE in
  prep) prep ;;
  ue) ue ;;
  all) prep; ue ;;
  *) echo "usage: rebuild_city.sh prep|ue|all"; exit 2 ;;
esac
