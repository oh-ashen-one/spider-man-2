#!/bin/bash
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# Terrain r04 capture hold (ONE slot hold, max 40 min). Enqueue with (detached):
#   /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label terrain --timeout 28800 -- docs/night1/terrain/round4.sh      (env STAGE=A | B | R)
# STAGE=A  the pass-2 canopy gate on the HEAD content /Game/Terrain (built before r04): safe warm-up + p1_south + p10_lawn_eye at 4K + the t5 route probes (nullrhi, no pixels)  -> round-04/stageA
# STAGE=B  the round's capture set from the r04 build (TERRAIN_ROOT, default /Game/TerrainR4): safe warm-up, the lawn stills first, then the others, then the two movies    -> round-04
# STAGE=R  resume: ONLY_IDS / WANT from the environment (e.g. ONLY_IDS="p6_west_shore p7_east_shore" WANT="stills moves")
# Content is built BEFORE the slot (nullrhi commandlets, no GPU). Capture safety (two health-monitor stops on 2026-10-02): 960x540 warm-up with r.ScreenPercentage 50 and a 4 fps fixed step,
# 4K stills stay at the 4 fps frame cap; watch /Users/midir/sm2-n1/_scratch/gpu/health.log during the first 2 minutes.
set -uo pipefail
S=/Users/midir/sm2-n1/_scratch/terrain
for _ in $(seq 1 120); do [ -e $S/BUILDING ] || break; sleep 5; done
if [ -e $S/BUILDING ]; then echo "terrain content still building after 10 min: giving the slot back"; exit 5; fi
export HOLD_START=$(date +%s)
HERE="$(cd "$(dirname "$0")" && pwd)"
export WH_CAPTURE_MAXFPS="${WH_CAPTURE_MAXFPS:-4}" WARM_QUIT="${WARM_QUIT:-12}" HIDE_HERO=1 BASE_IDS=""
case "${STAGE:-B}" in
  A) export TERRAIN_ROOT=/Game/Terrain ONLY_IDS="p1_south p10_lawn_eye" PRIO_IDS="p1_south p10_lawn_eye" STILL_TAG=r04-pass2gate PROBE_DIR="$HERE/round-04/t5_candidates"
     ROUND="$HERE/round-04/stageA"; WANT=(warm stills t5probe);;
  B) export TERRAIN_ROOT="${TERRAIN_ROOT:-/Game/TerrainR4}" PRIO_IDS="${PRIO_IDS-p10_lawn_eye p4_greatlawn p9_park_panorama p1_south}" STILL_TAG="${STILL_TAG:-r04}"
     ROUND="$HERE/${ROUND_NAME:-round-04}"; WANT=(warm stills moves);;
  R) export TERRAIN_ROOT="${TERRAIN_ROOT:-/Game/TerrainR4}" PRIO_IDS="${PRIO_IDS-}" STILL_TAG="${STILL_TAG:-r04}"; ROUND="$HERE/${ROUND_NAME:-round-04}"; read -r -a WANT <<< "${WANT:-stills}";;
  *) echo "unknown STAGE"; exit 2;;
esac
mkdir -p "$ROUND/stills"
echo "round4: stage ${STAGE:-B} root $TERRAIN_ROOT round $ROUND want ${WANT[*]} start $(date +%H:%M:%S) GPU $(ioreg -r -d 1 -w 0 -c IOAccelerator | grep -o '"Device Utilization %"=[0-9]*' | head -1)"
"$HERE/capture_round.sh" "$ROUND" "${WANT[@]}"
