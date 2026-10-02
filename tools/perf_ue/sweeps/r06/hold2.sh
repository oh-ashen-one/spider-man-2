#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P4 round 06, hold 2 = the final capture of the committed table (rebuild + stills session + lapse). It is queued BEFORE the table is tuned so that it keeps its place in the
# GPU queue; it only runs when $SM2_LOOK_SCRATCH/r06/READY_hold2 exists (written by the builder once the table in Scripts/look_presets.json is committed), otherwise it exits at once
# and the builder queues it again by hand (never re-queue from inside a hold: a nested gpu_slot call passes through).
WT="$(cd "$(dirname "$0")/../../../.." && pwd)"
S=${SM2_LOOK_SCRATCH:-/Users/midir/sm2-n1/_scratch/look}/r06
if [ ! -f "$S/READY_hold2" ]; then echo "hold2: table not ready ($S/READY_hold2 missing): exiting without rendering"; exit 0; fi
mv "$S/READY_hold2" "$S/READY_hold2.used.$(date +%H%M)"
cd "$WT"
exec tools/perf_ue/sweeps/r06/final_r06.sh build,stills,lapse
