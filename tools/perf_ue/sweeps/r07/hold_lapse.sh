#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P4 round 07 (resume): the stitched L23b lapse of the CURRENT baked build, in one GPU hold (budget HOLD_BUDGET s, default 2300; the lock's hard limit is 2400 s and ends a hold with SIGTERM + SIGKILL, so no segment is started
# that cannot finish before the deadline at LAPSE_SPF s per rendered frame; per-segment run_game timeout 1700 s, never the 900 s default that would SIGKILL a slow segment).
# First hold: REUSE unset (the work dir is wiped); next holds: REUSE=1 (segments already rendered are reused, the others are rendered).
# usage: [REUSE=1] [LAPSE_SPF=0.3] gpu_slot.sh capture --label look --timeout 3600 -- tools/perf_ue/sweeps/r07/hold_lapse.sh
WT="$(cd "$(dirname "$0")/../../../.." && pwd)"
R=$WT/docs/night1/look/round-07
T0=$(date +%s); HOLD=${HOLD_BUDGET:-2300}
cd "$WT"
RE=""; [ -n "$REUSE" ] && RE="--reuse"
LAPSE_SPF=${LAPSE_SPF:-0.3} python3 tools/perf_ue/lapse_stitch.py --round "$R" --name tod_lapse_S4 --res 960x540 ${=RE} --timeout 1700 --segments "3.7:1.8:4:0.3,5.2:4.0:16:0.3,8.9:8.7:4:0.3,17.3:4.1:16:0.3,21.1:6.9:4:0.3" --deadline $(( T0 + HOLD - 90 ))
echo "hold_lapse done t=$(( $(date +%s) - T0 ))s"
