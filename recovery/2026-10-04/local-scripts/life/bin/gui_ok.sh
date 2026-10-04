#!/bin/bash
# exit 0 when a macOS GUI app can finish launching in this session (Unreal needs NSApplication's didFinishLaunching, see docs/night1/life/HANDOFF.md "2026-09-30 WindowServer incident")
B=/Users/midir/sm2-n1/_scratch/life/bin/ns_launch_probe
O=$(mktemp /Users/midir/sm2-n1/_scratch/life/bin/probe.XXXXXX)
"$B" > "$O" 2>&1 &
P=$!
for i in 1 2 3 4 5 6 7 8; do sleep 1; grep -q didFinishLaunching "$O" && break; done
R=1; grep -q didFinishLaunching "$O" && R=0
kill $P 2>/dev/null; wait $P 2>/dev/null; rm -f "$O"
exit $R
