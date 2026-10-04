#!/bin/bash
# wait.sh <logfile> <seconds> [pattern]: print a tick every 7 s until the log gains a new line matching pattern (default any) or time is up
f=$1; n=$(( $2 / 7 )); pat=${3:-.}; c0=$(grep -c "$pat" "$f" 2>/dev/null); c0=${c0:-0}
for i in $(seq 1 $n); do sleep 7; echo "t$i"; c=$(grep -c "$pat" "$f" 2>/dev/null); c=${c:-0}; [ "$c" -gt "$c0" ] && break; done
tail -5 "$f"; date +%T
