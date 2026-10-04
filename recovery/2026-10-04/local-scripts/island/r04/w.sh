#!/bin/bash
# wait up to 27 s for pattern $2 in file $1, printing a tick every 6 s
for i in 1 2 3 4; do grep -q "$2" "$1" 2>/dev/null && break; sleep 6.5; echo -n "$i "; echo; done; tail -${3:-2} "$1"
