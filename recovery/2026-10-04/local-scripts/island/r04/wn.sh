#!/bin/bash
# wait up to $2 s (default 260) until file $1 grows by a line; print a dot every 20 s (fewer tokens), then the last line
F=$1; N=${2:-260}; n0=$(wc -l < "$F"); t0=$(date +%s)
while [ $(( $(date +%s) - t0 )) -lt $N ]; do sleep 6; [ "$(wc -l < "$F")" -gt "$n0" ] && break; [ $(( ($(date +%s) - t0) % 18 )) -lt 6 ] && echo .; done
tail -1 "$F"
