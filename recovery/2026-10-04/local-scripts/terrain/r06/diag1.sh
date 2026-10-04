#!/bin/bash
# Terrain r06 diag 1: build D_shadow (nullrhi commandlet) then capture it top-down, both through the GPU lock (one hold each, sequential).
set -uo pipefail
WT=/Users/midir/sm2-n1/terrain; GS=/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh; O=/Users/midir/sm2-n1/_scratch/terrain/r06/${OUTN:-diag1}
ROOT=${ROOT:-/Game/TerrainR5b}
mkdir -p $O
if [ -z "${SKIP_BUILD:-}" ]; then
  echo "build start $(date +%H:%M:%S)"
  SM2_TERRAIN_ROOT=$ROOT $GS capture --label terrain --timeout 28800 -- $WT/tools/terrain/run_build.sh diag > $O/build.txt 2>&1
  echo "build rc=$? $(date +%H:%M:%S)"
  grep -a "build_terrain" /Users/midir/sm2-n1/_scratch/terrain/manhattan/logs/terrain_build.log | tail -5
fi
for V in ${VARIANTS:-base}; do
  EX="r.ScreenPercentage 100"
  case $V in
    base) ;;
    csm) EX="$EX,r.Shadow.Virtual.Enable 0";;
  esac
  echo "capture $V start $(date +%H:%M:%S)"
  $GS capture --label terrain --timeout 28800 -- $WT/unreal/WebHomage/Scripts/run_game.sh $O/$V -map $ROOT/Maps/${MAPN:-D_shadow} -res 1920x1080 -shots 12,20 -quit 21 -name d_$V -timeout 900 -exec "$EX" -- -notraceserver
  echo "capture $V rc=$? $(date +%H:%M:%S)"
done
echo done
