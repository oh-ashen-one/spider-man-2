#!/bin/bash
# poll helper: one short line every 5 s; the last line of $1 whenever it changes; stop after $2 seconds or when $3 (regex) appears in $1
f=$1; n=$(( ${2:-270} / 8 )); pat=${3:-__never__}; last=""
for i in $(seq 1 $n); do
  l=$(tail -1 "$f" 2>/dev/null)
  if [ "$l" != "$last" ]; then echo "$(date +%T) ${l:0:220}"; last=$l; else echo "."; fi
  grep -qE "$pat" "$f" 2>/dev/null && { echo MATCH; exit 0; }
  sleep 8
done
