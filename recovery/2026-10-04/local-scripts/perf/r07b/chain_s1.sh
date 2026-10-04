#!/bin/zsh
# Piece F round 07 re-baseline, after chain_build.sh: (1) exclusive perf session a1 on the integrated /Game/Maps/Manhattan (traffic + crowd = Life_Actors
# sublevel, add_life.py), preset OFF in MacEngine.ini: as-found x3 at the ini resolution, one as-found at SP 50, the round-07 preset hwl4 per run (no content
# change) and hwl4 with the as-found Nanite error; (2) as-found 3840 stills (new look_gate reference) S1 S2 S7 + route t20/t28/t42, fixed step, each view twice.
set -e
WT=/Users/midir/sm2-n1/perf
S=/Users/midir/sm2-n1/_scratch/perf
G=/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh
cd $WT
echo "== $(date +%H:%M:%S) perf a1"
python3 tools/perf_ue2/perf_queue.py --out $S/r07b/perf --tag a --retries 20 \
  --configs "warm@ini,af_a@ini,af_b@ini,af_c@ini,af50@50,h4@50+set:perf60_hwl4,h4m1@50+set:perf60_hwl4+r.Nanite.MaxPixelsPerEdge=1" \
  -- --map /Game/Maps/Manhattan --budget-s 840 || echo "perf queue rc $?"
echo "== $(date +%H:%M:%S) stills as-found"
export SM2_PERF_STILL_FIXED=1 SM2_PERF_STILL_TWICE=1 SM2_PERF_ROUTE_SHOTS=20,28,42
for V in "S1 S2" "S7" "route"; do
  $G capture --label perf --timeout 21600 -- tools/perf_ue2/stills2.sh $S/r07b/asfound "asfound@ini" "$V" || echo "stills $V rc $?"
done
echo "== $(date +%H:%M:%S) S1 DONE"
