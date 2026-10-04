#!/bin/bash
# exits when the base job log shows ALL DONE (or the waiter is gone and no log)
L=/Users/midir/sm2-n1/_scratch/terrain/manhattan/logs/base_all.log
while true; do
  if grep -q "base_all\] ALL DONE" "$L" 2>/dev/null; then echo DONE; exit 0; fi
  if ! ps -p 14031 >/dev/null 2>&1 && ! pgrep -f "label terrain" >/dev/null 2>&1; then echo "waiter gone"; exit 1; fi
  sleep 20
done
