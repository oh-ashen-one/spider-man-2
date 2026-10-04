#!/bin/bash
# long wait: up to $3 s (default 260) for pattern $2 in file $1, one short line every ~6 s (keeps the tool session alive), then the tail
N=${3:-260}; t0=$(date +%s)
while [ $(( $(date +%s) - t0 )) -lt $N ]; do echo "."; tail -c 400000 "$1" 2>/dev/null | grep -q "$2" && break; sleep 6; done
tail -${4:-3} "$1"
