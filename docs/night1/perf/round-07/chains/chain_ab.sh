#!/bin/bash
# F round 07 chain ab: clean A/B of the leaf_area content (Nanite preserve-area on leaf cards). p2 was VOID (other processes on the GPU).
#  c3 leaf_area NONE -> perf p3 ; c4 leaf_area PRESERVE_AREA -> perf p4. Same configs, ini = perf60_hwl4.
set -uo pipefail
WT=/Users/midir/sm2-n1/perf; R=/Users/midir/sm2-n1/_scratch/perf/r07; G=/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh
cd $WT; L=+variant:Life
CFG="lwarm@ini$L,life_a@ini$L,ship_a@ini,life_b@ini$L,s2@ini+view:S2,life_c@ini$L,ship_b@ini"
for step in "3 NONE" "4 PRESERVE_AREA"; do
  set -- $step; N=$1; SH=$2
  [ -f /Users/midir/sm2-n1/_scratch/gpu/PAUSED ] && { echo "PAUSED present: stop"; exit 3; }
  SM2_PERF_APPLY_STEPS=leaf_area SM2_PERF_LEAF_SHAPE=$SH $G capture --label perf -- python3 tools/perf_ue2/build_map.py --steps perf_apply > $R/logs/c$N.log 2>&1; echo "$(date +%T) c$N ($SH) rc $?"
  cp /Users/midir/sm2-n1/_scratch/perf/perf_apply.json $R/c${N}_perf_apply.json
  python3 tools/perf_ue2/perf_queue.py --out $R/perf --tag p --start $N --configs "$CFG" -- --budget-s 870
  echo "$(date +%T) p$N done"
done
