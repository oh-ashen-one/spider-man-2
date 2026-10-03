#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P4 round 07 (resume): ONE loop iteration on chosen windows only (lapse_loop_w.py), table = make_v3(knobs, bias_in) of $HOLD_DIR; writes $HOLD_DIR/loop/bias_overrides.json and the measured windows (it0/).
# usage: HOLD_DIR=holdQ2 WINDOWS=17.3:4.1 gpu_slot.sh capture --label look --timeout 3600 -- tools/perf_ue/sweeps/r07/hold_loopw.sh
WT="$(cd "$(dirname "$0")/../../../.." && pwd)"
F=${SM2_LOOK_SCRATCH:-/Users/midir/sm2-n1/_scratch/look}/r07/${HOLD_DIR:?}
T0=$(date +%s)
cd "$WT"
python3 tools/perf_ue/sweeps/r07/make_v3.py --knobs "$F/knobs_r07.json" --bias-overrides "$F/bias_in.json" --out "$F/doc_pre.json" || exit 2
python3 tools/perf_ue/lapse_loop_w.py --out "$F/loop" --doc "$F/doc_pre.json" --windows ${WINDOWS:-17.3:4.1} --substeps 16 --iters 1 --max-delta ${MAXD:-2.0} --gain ${GAIN:-0.9} --keys-hours $(cat "$F/keys_h.txt") --deadline $(( T0 + 1750 )) 2>&1 | tail -10
echo "hold_loopw done t=$(( $(date +%s) - T0 ))s"
