#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P4 round 08: ONE closed-loop iteration on the exposure bias of the twilight keys (lapse_loop_w.py, x16 windows of the S4 lapse, table loaded at BeginPlay with -WHToDKeys, no rebuild)
# for the round-08 table make_v4.py(<knobs>, <bias in>). Writes <dir>/loop/bias_overrides.json + the measured windows (<dir>/loop/it0/windows.json).
# usage: gpu_slot.sh capture --label look --timeout 3600 -- tools/perf_ue/sweeps/r08/hold_loopw.sh <knobs.json> <bias_in.json> <dir>
WT="$(cd "$(dirname "$0")/../../../.." && pwd)"
T0=$(date +%s)
cd "$WT"; mkdir -p "$3"
python3 tools/perf_ue/sweeps/r08/make_v4.py --knobs "$1" --r07-bias "$2" --out "$3/doc_pre.json" || exit 2
KH=5.6,6.1,6.25,6.35,6.4,6.45,6.5,6.55,6.6,6.65,6.7,6.75,6.8,6.85,6.9,6.95,7,7.05,7.1,7.15,7.2,7.25,7.3,7.35,7.4,7.45,7.6,7.8,8,8.4,8.8,18.45,18.5,18.55,18.6,18.65,18.7,18.75,18.8,18.85,18.9,18.95,19,19.05,19.1,19.15,19.2,19.25,19.3,19.35,19.4,19.45,19.5,19.55,19.6,19.65,19.7,19.75,19.8,19.85,19.9,20.2,20.4,20.6,21,21.4
python3 tools/perf_ue/lapse_loop_w.py --out "$3/loop" --doc "$3/doc_pre.json" --windows ${WINDOWS:-5.2:4.0,17.3:4.1} --substeps 16 --iters 1 --max-delta ${MAXD:-2.0} --gain ${GAIN:-0.9} --slope ${SLOPE:-1.3} --keys-hours ${KEYS_H:-$KH} --deadline $(( T0 + 2250 )) --timeout 1700 2>&1 | tail -12
echo "hold_loopw done t=$(( $(date +%s) - T0 ))s"
