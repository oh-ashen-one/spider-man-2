#!/bin/bash
# wait up to $1 s (prints a dot line every 9 s so the tool does not background it); stop early when file $2 contains regex $3
N=${1:-270}; F=${2:-}; R=${3:-}
for ((i=0; i<N; i+=9)); do
  if [ -n "$F" ] && [ -f "$F" ] && grep -qE "$R" "$F"; then echo "matched after $i s"; exit 0; fi
  sleep 9; echo .
done
