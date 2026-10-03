#!/bin/bash
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# tricks r02 hold (run INSIDE one gpu_slot capture hold, max 40 min): optional content build (STEPS=..., BUILD=1), probe the reel with
# -nullrhi (PROBE=1: telemetry + pose log, route score, tricks_check -> <probe dir>/VERDICT), then render the reel windows that have no DONE
# marker while >= 22 min of the hold remain (RENDER=1). The 61 s reel: windows 0:15,15:30,30:45,45:61 (the last trick's catch + 0.4 s
# stays inside the clip). TAG names the probe dir; PROBE_ARGS passes extra game args to the probe (A/B).
cd /Users/midir/sm2-n1/tricks
T0=${HOLD_T0:-$(date +%s)}; LEFT() { echo $(( 2400 - ( $(date +%s) - T0 ) )); }
UP=/Users/midir/sm2-n1/tri; UP="${UP}cks/unreal/WebHomage/WebHomage.uproject"
while pgrep -f "$UP" >/dev/null; do sleep 5; done
if [ "${BUILD:-0}" = 1 ]; then
  python3 tools/tricks/run_build.py "${STEPS:-traversal}" 2>&1 | grep -E "=== step|all done|error|Error|failed" | tail -20
fi
W=/Users/midir/sm2-n1/_scratch/tricks/probe_r02/${TAG:-a}; mkdir -p $W
if [ "${PROBE:-1}" = 1 ]; then
  MAXPROBES=${MAXPROBES:-1} python3 tools/tricks/probe_reel.py docs/night1/tricks/scripts/t60_trick_reel.json $W/best.json $W
fi
cat $W/VERDICT 2>/dev/null
if [ "${RENDER:-0}" = 1 ] && grep -q "route OK" $W/VERDICT; then
  C=/Users/midir/sm2-n1/_scratch/tricks/capture/t60_trick_reel
  for K in 0 1 2 3; do
    if [ -f "$C/seg$K/DONE" ]; then continue; fi
    if [ "$(LEFT)" -lt 1320 ]; then echo "window $K left for the next hold ($(LEFT) s left)"; break; fi
    QUIT_t60_trick_reel=61.0 NOHOLD=1 SEGS="0:15,15:30,30:45,45:61" SEG_ONLY=$K EXTRA_ARGS="-WHTrickWarm=4 ${RENDER_ARGS:-}" tools/tricks/capture.sh docs/night1/tricks/round-02 t60_trick_reel
    N=$(ls "$C/seg$K/t60_trick_reel_frames" 2>/dev/null | wc -l | tr -d ' ')
    if [ "$N" -ge 850 ]; then touch "$C/seg$K/DONE"; else echo "window $K short ($N frames)"; break; fi
  done
fi
echo "hold r02 end, $(LEFT) s left"
