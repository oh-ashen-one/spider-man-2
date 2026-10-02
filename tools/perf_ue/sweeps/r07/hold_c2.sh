#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P4 round 07, hold C: hold_b.sh with the v1 knobs ($SM2_LOOK_SCRATCH/r07/holdC/knobs_r07.json: free twilight metering (min EV -1), a dense bias curve on every twilight key, golden 18.4 override,
# moon volumetric .1, cooler dawn factor): 2 loop iterations on EVERY twilight key, build, dome + golden stills, stitched lapse.
H="$(cd "$(dirname "$0")" && pwd)"
S=${SM2_LOOK_SCRATCH:-/Users/midir/sm2-n1/_scratch/look}/r07/holdC
export HOLD_DIR=holdC LOOP_ITERS=${LOOP_ITERS:-2} MAXD=${MAXD:-3.0} GAIN=${GAIN:-0.9} LOOP_DEADLINE=${LOOP_DEADLINE:-850} KEYS_H=$(cat "$S/keys_h.txt")
exec "$H/hold_b.sh" loop,build,stills,lapse
