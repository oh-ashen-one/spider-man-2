#!/bin/bash
# F round 07 chain ab2 (restart of chain_ab after the lock's 30-min perf wait timeout kept sending the session to the back of the FIFO):
# same A/B, the wait timeouts raised to 3 h through the lock's documented env (exclusivity unchanged). Content is at c3 = leaf_area NONE.
set -uo pipefail
WT=/Users/midir/sm2-n1/perf; R=/Users/midir/sm2-n1/_scratch/perf/r07; G=/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh
export GPU_SLOT_PERF_WAIT_TIMEOUT=10800 GPU_SLOT_CAPTURE_WAIT_TIMEOUT=10800
cd $WT; L=+variant:Life
CFG="lwarm@ini$L,life_a@ini$L,ship_a@ini,life_b@ini$L,s2@ini+view:S2,life_c@ini$L,ship_b@ini"
[ -f /Users/midir/sm2-n1/_scratch/gpu/PAUSED ] && { echo "PAUSED present: stop"; exit 3; }
python3 tools/perf_ue2/perf_queue.py --out $R/perf --tag p --start 3 --configs "$CFG" -- --budget-s 870; echo "$(date +%T) p3 done"
[ -f /Users/midir/sm2-n1/_scratch/gpu/PAUSED ] && { echo "PAUSED present: stop"; exit 3; }
SM2_PERF_APPLY_STEPS=leaf_area SM2_PERF_LEAF_SHAPE=PRESERVE_AREA $G capture --label perf -- python3 tools/perf_ue2/build_map.py --steps perf_apply > $R/logs/c4.log 2>&1; echo "$(date +%T) c4 (PRESERVE_AREA) rc $?"
cp /Users/midir/sm2-n1/_scratch/perf/perf_apply.json $R/c4_perf_apply.json
[ -f /Users/midir/sm2-n1/_scratch/gpu/PAUSED ] && { echo "PAUSED present: stop"; exit 3; }
python3 tools/perf_ue2/perf_queue.py --out $R/perf --tag p --start 4 --configs "$CFG" -- --budget-s 870; echo "$(date +%T) p4 done"
