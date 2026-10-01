#!/bin/bash
# F round 07 content c1: perf_apply leaf_area (Nanite preserve-area on the leaf cards) + rt_proxy_cards (64 Lumen cards per tree RT proxy), headless commandlet in the capture lock.
set -uo pipefail
WT=/Users/midir/sm2-n1/perf; R=/Users/midir/sm2-n1/_scratch/perf/r07; G=/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh
cd $WT
SM2_PERF_APPLY_STEPS=leaf_area,rt_proxy_cards $G capture --label perf -- python3 tools/perf_ue2/build_map.py --steps perf_apply > $R/logs/c1.log 2>&1; echo "$(date +%T) c1 rc $?"
cp /Users/midir/sm2-n1/_scratch/perf/perf_apply.json $R/c1_perf_apply.json 2>/dev/null
