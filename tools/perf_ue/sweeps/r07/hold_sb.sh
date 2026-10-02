#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P4 round 07, hold A: the twilight dome sweep (gen_sweep_b.py plan, baked table + live pins, ONE game session, ~120 stills) + dome_check.py. Run inside gpu_slot.sh capture (the inner slot call passes through).
WT="$(cd "$(dirname "$0")/../../../.." && pwd)"
S=${SM2_LOOK_SCRATCH:-/Users/midir/sm2-n1/_scratch/look}/r07/sweepB
cd "$WT"; mkdir -p "$S"
T0=$(date +%s)
python3 tools/perf_ue/sweeps/r07/gen_sweep_b.py --out "$S" || exit 2
python3 tools/perf_ue/sweeps/run_r06.py --plan "$S/plan_b.json" --out "$S" --timeout 2100; echo "sweep rc=$? t=$(( $(date +%s) - T0 ))s"
python3 tools/perf_ue/dome_check.py --dir "$S" --out "$S/DOME_B" > /dev/null; echo "hold_sb done t=$(( $(date +%s) - T0 ))s"
# (same hold) lapse windows of the best-guess r07 table (holdB/doc_v0.json = make_v3.py knobs_r07.json + bias_in.json, loaded with -WHToDKeys): dusk 18.1-21.4 and dawn 5.5-8.2 at x16, one loop iteration
# (its bias suggestion is only advisory); evidence of the geometric sun surface decay and the lit dome in motion
B=${SM2_LOOK_SCRATCH:-/Users/midir/sm2-n1/_scratch/look}/r07/holdB
if [ -f "$B/doc_v0.json" ] && [ $(( $(date +%s) - T0 )) -lt 1750 ]; then
  python3 tools/perf_ue/lapse_loop_w.py --out "$B/lw0" --doc "$B/doc_v0.json" --substeps 16 --iters 1 --keys-hours 5.6,6.1,6.35,6.5,6.6,6.7,6.8,6.9,7.0,7.1,7.2,7.3,7.4,7.6,7.8,8.0,8.4,18.6,18.7,18.8,18.9,19.0,19.1,19.2,19.3,19.4,19.5,19.6,19.7,19.8,19.9,20.2,20.4,20.6,21.0 --deadline $(( T0 + 2300 )) 2>&1 | tail -8
fi
echo "hold_sb + lapse windows done t=$(( $(date +%s) - T0 ))s"
