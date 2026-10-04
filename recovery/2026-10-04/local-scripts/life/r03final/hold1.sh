#!/bin/bash
# round 03 final, hold 1 (verification): map rebuild (commandlet inside the hold), S1 + S2 1080p stills, swing clip. One gpu_slot hold, one engine at a time.
set -uo pipefail
WT=/Users/midir/sm2-n1/life
R=$WT/docs/night1/life/round-03
cd $WT
# a nested launch inside a hold skips the lock's stuck-exit check: wait until MY engine process has fully exited (max 180 s), never kill it
engine_gone() { for i in $(seq 1 90); do pgrep -f 'sm2-n1/[l]ife/unreal/WebHomage/WebHomage.uproject' >/dev/null || return 0; sleep 2; done; echo "my engine still present after 180 s: stop (no launch on top of it)"; return 1; }
echo "== $(date +%T) map rebuild"; python3 -B unreal/WebHomage/Scripts/build_life.py --steps map || { echo "map build failed"; exit 5; }
engine_gone || exit 6
echo "== $(date +%T) stills 1080p"; RESES=1920x1080 docs/night1/life/capture_round.sh $R stills
engine_gone || exit 6
echo "== $(date +%T) swing"; docs/night1/life/capture_round.sh $R clip_swing
engine_gone || exit 6
echo "== $(date +%T) hold1 done"
