#!/bin/bash
# island r03: end hold 2 after r1 (r3 would run into gpu_slot's max hold = SIGKILL of a rendering engine). Stops capture_round.sh (pid 14333)
# right after r1's mp4 is encoded; if r1's engine is still running at 13:00:05 it is stopped with stop_ue.sh (drivers first, SIGTERM, wait).
LOG=/Users/midir/sm2-n1/_scratch/island/logs/holds_r03.log
DEADLINE=$(date -j -f "%Y-%m-%d %H:%M:%S" "2026-10-02 13:00:05" +%s)
while kill -0 14333 2>/dev/null; do
  if grep -q "r1_north_avenue.mp4 2-pass" "$LOG"; then echo "$(date +%T) r1_guard: r1 encoded, stopping capture_round (pid 14333) before r3" >> "$LOG"; kill -TERM 14333; exit 0; fi
  if [ "$(date +%s)" -ge "$DEADLINE" ]; then echo "$(date +%T) r1_guard: hold nearly over, stop_ue.sh" >> "$LOG"; /Users/midir/sm2-n1/_scratch/gpu/bin/stop_ue.sh "/Users/midir/sm2-n1/island" >> "$LOG" 2>&1; exit 0; fi
  sleep 0.2
done
