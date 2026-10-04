#!/bin/bash
# P3 r21: re-queue a GPU-lock job when the lock's wait times out (exit 75); never runs anything outside gpu_slot.sh
# usage: requeue.sh <log> <wait-for-pid or 0> -- cmd...
LOG=$1; WPID=$2; shift 3
cd /Users/midir/sm2-n1/_scratch/traversal/r21
if [ "$WPID" != 0 ]; then
  while kill -0 $WPID 2>/dev/null; do sleep 10; done
  grep -q "^EXIT 75" probeA.log 2>/dev/null || [ -n "${FORCE:-}" ] || exit 0
fi
while true; do
  [ -e STOP ] && exit 0
  GPU_SLOT_CAPTURE_WAIT_TIMEOUT=10800 /Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label traversal -- "$@" >> "$LOG" 2>&1
  rc=$?; echo "EXIT $rc $(date +%T)" >> "$LOG"
  [ $rc -ne 75 ] && exit 0
done
