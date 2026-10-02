#!/bin/bash
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# Terrain r04 capture hold (ONE slot hold, max 40 min). Enqueue with (detached):
#   /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label terrain --timeout 28800 -- docs/night1/terrain/round4.sh      (env STAGE=A | B | R)
# STAGE=A  hold 1 = lawn + canopy-gate set from the r04 build (/Game/TerrainR4): safe warm-up, p10 p4 p9 p1 at 4K, the t4 movie, the t5 route probes, GPU ms of p1 / p10 on the HEAD content vs this build
# STAGE=B  hold 2 = the other five stills + the t5 movie (route chosen from the probes)
# STAGE=R  resume: ONLY_IDS / WANT / MOVIES from the environment (e.g. ONLY_IDS="p6_west_shore" WANT="stills")
# Content is built BEFORE the slot (nullrhi commandlets, no GPU). Capture safety (two health-monitor stops on 2026-10-02): 960x540 warm-up with r.ScreenPercentage 50 and a 4 fps fixed step,
# 4K stills stay at the 4 fps frame cap; watch /Users/midir/sm2-n1/_scratch/gpu/health.log during the first 2 minutes.
set -uo pipefail
S=/Users/midir/sm2-n1/_scratch/terrain
for _ in $(seq 1 120); do [ -e $S/BUILDING ] || break; sleep 5; done
if [ -e $S/BUILDING ]; then echo "terrain content still building after 10 min: giving the slot back"; exit 5; fi
export HOLD_START=$(date +%s)
HERE="$(cd "$(dirname "$0")" && pwd)"
export WH_CAPTURE_MAXFPS="${WH_CAPTURE_MAXFPS:-4}" WARM_QUIT="${WARM_QUIT:-12}" HIDE_HERO=1 BASE_IDS=""
case "${STAGE:-A}" in
  A) # hold 1 (calibration + canopy gate): safe warm-up, the four lawn / canopy stills at 4K (p10 p4 p9 p1), the t4 movie, the t5 route probes (nullrhi), then GPU ms of p1 / p10 on the HEAD content vs this build
     export TERRAIN_ROOT="${TERRAIN_ROOT:-/Game/TerrainR4}" BASE_ROOT=/Game/Terrain ONLY_IDS="p10_lawn_eye p4_greatlawn p9_park_panorama p1_south" PRIO_IDS="p10_lawn_eye p4_greatlawn p9_park_panorama p1_south" STILL_TAG=r04 \
            MOVIES=t4_lawn_sprint PROBE_DIR="$HERE/round-04/t5_candidates"
     ROUND="$HERE/${ROUND_NAME:-round-04}"; WANT=(warm stills moves t5probe basegpu);;
  B) # hold 2: everything the first hold did not take (the other five stills + the t5 movie on the chosen route); BASE_IDS stays empty
     export TERRAIN_ROOT="${TERRAIN_ROOT:-/Game/TerrainR4}" ONLY_IDS="${ONLY_IDS:-p2_reservoir p3_lake p6_west_shore p7_east_shore p8_pier}" PRIO_IDS="${PRIO_IDS-}" STILL_TAG="${STILL_TAG:-r04}" MOVIES=t5_avenue_to_park
     ROUND="$HERE/${ROUND_NAME:-round-04}"; WANT=(warm stills moves);;
  R) # resume: ONLY_IDS / WANT / MOVIES from the environment
     export TERRAIN_ROOT="${TERRAIN_ROOT:-/Game/TerrainR4}" PRIO_IDS="${PRIO_IDS-}" STILL_TAG="${STILL_TAG:-r04}"; ROUND="$HERE/${ROUND_NAME:-round-04}"; read -r -a WANT <<< "${WANT:-stills}";;
  *) echo "unknown STAGE"; exit 2;;
esac
mkdir -p "$ROUND/stills"
echo "round4: stage ${STAGE:-B} root $TERRAIN_ROOT round $ROUND want ${WANT[*]} start $(date +%H:%M:%S) GPU $(ioreg -r -d 1 -w 0 -c IOAccelerator | grep -o '"Device Utilization %"=[0-9]*' | head -1)"
"$HERE/capture_round.sh" "$ROUND" "${WANT[@]}"
