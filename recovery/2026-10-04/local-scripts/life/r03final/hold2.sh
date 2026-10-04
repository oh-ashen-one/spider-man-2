#!/bin/bash
# round 03 final, hold 2 (east-side sweep): S1 1080p stills (t 12/16/20/24/28) for east factor x fill combinations, then S2. One gpu_slot hold, one engine at a time.
set -uo pipefail
X=/Users/midir/sm2-n1/_scratch/life/r03/exp.sh
engine_gone() { for i in $(seq 1 90); do pgrep -f 'sm2-n1/[l]ife/unreal/WebHomage/WebHomage.uproject' >/dev/null || return 0; sleep 2; done; echo "my engine still present after 180 s: stop (no launch on top of it)"; return 1; }
run() { engine_gone || exit 6; echo "== $(date +%T) $1"; "$X" "$@"; }
S1=/Game/Tests/Life/Life_View_S1
run h1_s1_e13_f1800 $S1 1920x1080 12,16,20,24,28 30 - -- -WHLifeSample=8:30:1 -WHLifeClearAhead=24
run h2_s1_e16_f1800 $S1 1920x1080 12,16,20,24,28 30 - -- -WHLifeSample=8:30:1 -WHLifeClearAhead=24 -WHLifeEast=1.6
run h3_s1_e13_f2500 $S1 1920x1080 12,16,20,24,28 30 - -- -WHLifeSample=8:30:1 -WHLifeClearAhead=24 -WHLifeFill=2500
run h4_s1_e16_f2500 $S1 1920x1080 12,16,20,24,28 30 - -- -WHLifeSample=8:30:1 -WHLifeClearAhead=24 -WHLifeEast=1.6 -WHLifeFill=2500
run h5_s2_e13 /Game/Tests/Life/Life_View_S2 1920x1080 12,16,20,24,28 30 - -- -WHLifeSample=8:30:1
engine_gone || exit 6
echo "== $(date +%T) hold2 done"
