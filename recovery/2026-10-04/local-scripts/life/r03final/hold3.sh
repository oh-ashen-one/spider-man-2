#!/bin/bash
# round 03 final, hold 3 (final captures): waits (max 14 min) for the GO file that says the parameters are decided and the C++ is rebuilt, then
# stills (S1 / S2, 1080p + 4K), swing, street, signal clips. Time-guarded so that no engine is running when the 40 min hold limit hits.
set -uo pipefail
WT=/Users/midir/sm2-n1/life
R=$WT/docs/night1/life/round-03
GO=/Users/midir/sm2-n1/_scratch/life/r03final/GO
T0=$(date +%s)
cd $WT
engine_gone() { for i in $(seq 1 90); do pgrep -f 'sm2-n1/[l]ife/unreal/WebHomage/WebHomage.uproject' >/dev/null || return 0; sleep 2; done; echo "my engine still present after 180 s: stop (no launch on top of it)"; return 1; }
for i in $(seq 1 84); do [ -f "$GO" ] && break; sleep 10; done
[ -f "$GO" ] || { echo "no GO within 14 min: releasing the hold"; exit 7; }
echo "== $(date +%T) GO seen after $(( $(date +%s) - T0 )) s"
# step <estimated seconds> <label> <command...>: skipped when it would run past 33 min of hold time
step() { local est=$1 lab=$2; shift 2; local el=$(( $(date +%s) - T0 )); if [ $(( el + est )) -gt 1980 ]; then echo "== $(date +%T) SKIP $lab (hold elapsed $el s + $est s > 1980 s)"; return 0; fi
  engine_gone || exit 6; echo "== $(date +%T) $lab"; "$@"; }
step 600 "stills 1080p + 4K" docs/night1/life/capture_round.sh $R stills
step 300 "swing" docs/night1/life/capture_round.sh $R clip_swing
step 480 "street" docs/night1/life/capture_round.sh $R clip_street
step 360 "signal" docs/night1/life/capture_round.sh $R clip_signal
engine_gone || exit 6
echo "== $(date +%T) hold3 done (elapsed $(( $(date +%s) - T0 )) s)"
