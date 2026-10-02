#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# CPU-only analysis of hold1.sh outputs ($SM2_LOOK_SCRATCH/r06): twilight / moon / dawn-correlation numbers of the sweep stills, golden variants through the golden spec checkers,
# the three lapses, the hero clip. Writes sweep_twilight.{md,json}, sweep_tests.{md,json}, lapse_L*.png next to the inputs.
WT="$(cd "$(dirname "$0")/../../../.." && pwd)"
S=${SM2_LOOK_SCRATCH:-/Users/midir/sm2-n1/_scratch/look}/r06
cd "$WT"
echo "=== twilight_check (sky band vs far band, sun-facing B-R, moon, S1 dawn correlation)"
python3 tools/perf_ue/twilight_check.py --dir "$S/sweep" --out "$S/sweep_twilight" | grep -v "^| .* | S[1235678] |" 
echo; echo "=== spec numbers of the golden / night variants"
python3 tools/perf_ue/tod_tests.py --dir "$S/sweep" --out "$S/sweep_tests" --map 'G*=golden,D*=golden,M*=night,Hero*=night' --scratch "$S/tod_tests_scratch" 2>&1 | tail -30
for L in L0 L1 L2; do
  if [ -f "$S/lapse_$L/lapse_$L.json" ]; then echo; echo "=== lapse $L"; python3 tools/perf_ue/lapse_report.py "$S/lapse_$L/lapse_$L.json" --thr 1.5 | head -60; fi
done
python3 tools/perf_ue/lapse_report.py "$S/lapse_L0/lapse_L0.json" --cmp "$S/lapse_L2/lapse_L2.json" --png "$S/lapse_L0_vs_L2.png" > /dev/null 2>&1
for J in "$S"/clips/swing_tod_22*_hero_luma.json; do [ -f "$J" ] && { echo; echo "=== hero clip $J"; cat "$J"; }; done
