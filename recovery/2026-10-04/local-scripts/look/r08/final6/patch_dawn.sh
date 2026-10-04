#!/bin/zsh
# P4 r08: after final_chain2: dawn bias keys 06:39-06:54 smoothed (tapered2), bake, and dusk bias keys 19:06-19:15 smoothed, re-render the twilight lapse segments (seg1, seg3), re-stitch (REUSE)
WT=/Users/midir/sm2-n1/look; cd $WT
GS=/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh
while kill -0 69803 2>/dev/null; do sleep 10; done
cp /Users/midir/sm2-n1/_scratch/look/r08/final6/bias_tapered2.json docs/night1/look/round-08/lapse_bias_overrides.json
python3 tools/perf_ue/sweeps/r08/make_v4.py --knobs docs/night1/look/round-08/diag/knobs_r08.json --r07-bias docs/night1/look/round-08/lapse_bias_overrides.json --in-place || exit 2
$GS capture --label look --timeout 3600 -- tools/perf_ue/rebuild_look.sh rigs,maps midday,golden,night,tod
grep -q "build_look.*DONE" /Users/midir/sm2-n1/_scratch/look/build_look_headless.log || { echo "rebuild not confirmed"; exit 1; }
W=/Users/midir/sm2-n1/_scratch/look/lapse_stitch/tod_lapse_S4; mkdir -p $W/../keep_r08; cp -r $W/seg1 $W/../keep_r08/seg1_tapered1 2>/dev/null; cp -r $W/seg3 $W/../keep_r08/seg3_tapered1 2>/dev/null; rm -rf $W/seg1 $W/seg3
mkdir -p /Users/midir/sm2-n1/_scratch/look/r08/final6/lapse_tapered1 && cp docs/night1/look/round-08/tod_lapse_S4.* /Users/midir/sm2-n1/_scratch/look/r08/final6/lapse_tapered1/ 2>/dev/null; rm -f docs/night1/look/round-08/tod_lapse_S4.json docs/night1/look/round-08/tod_lapse_S4.mp4 docs/night1/look/round-08/tod_lapse_S4_sheet.jpg
REUSE=1 $GS capture --label look --timeout 3600 -- tools/perf_ue/sweeps/r08/hold_lapse.sh
echo "patch_dawn done $(date)"
[ -f docs/night1/look/round-08/tod_lapse_S4.json ] || REUSE=1 $GS capture --label look --timeout 3600 -- tools/perf_ue/sweeps/r08/hold_lapse.sh
