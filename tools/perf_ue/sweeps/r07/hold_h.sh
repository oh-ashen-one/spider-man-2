#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P4 round 07, holds H / I: finish the stitched lapse of the CURRENT build (hold F) under a loaded machine: lapse_stitch.py --reuse renders only the segments not yet in its work dir
# (seg0 / seg1 were rendered in hold F), starts a segment only when it can finish (LAPSE_SPF s per rendered frame), and stitches what exists. Run it again in the next hold until the json has 5 segments.
setopt +o nomatch 2>/dev/null
WT="$(cd "$(dirname "$0")/../../../.." && pwd)"
R=$WT/docs/night1/look/round-07
T0=$(date +%s); HOLD=${HOLD_BUDGET:-2250}
cd "$WT"
LAPSE_SPF=${LAPSE_SPF:-0.65} python3 tools/perf_ue/lapse_stitch.py --round "$R" --name tod_lapse_S4 --res 960x540 --reuse --segments "3.7:1.8:4:0.3,5.2:4.0:16:0.3,8.9:8.7:4:0.3,17.3:4.1:16:0.3,21.1:6.9:4:0.3" --deadline $(( T0 + HOLD - 60 ))
echo "hold_h done t=$(( $(date +%s) - T0 ))s"
