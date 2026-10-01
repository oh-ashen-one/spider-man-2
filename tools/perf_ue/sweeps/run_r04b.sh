#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# Round-04 (resumed) phases, each inside ONE GPU-slot hold:   gpu_slot.sh capture --label look -- tools/perf_ue/sweeps/run_r04b.sh <phase>
#   S   live sweeps: golden v_g7a (sun geometry), v_g7b (fill / grade), night v_n7 (skyline windows), 1080p native, stills -> $SCR/eval7/stills
#   F   rebuild the rigs (golden,night) headless, then the round stills: golden + night + midday 1080p native and 4K with the perf preset's 50 % (1920x1080 internal)
#   C   swing clips golden, night, midday (fixed 1/60 s step)
# The slot's max hold (2400 s) SIGKILLs what is still running, which must never hit an engine (RULES.md 2026-09-29 panic): every step gets a game timeout that ends
# >= 4 min before the hold limit (run_game.sh stops with SIGTERM + 60 s), and a step is skipped when the remaining budget is too small.
WT="$(cd "$(dirname "$0")/../../.." && pwd)"
SCR=${SM2_LOOK_SCRATCH:-/Users/midir/sm2-n1/_scratch/look}
RND=${R04_ROUND:-$WT/docs/night1/look/round-04}
LIMIT=${R04_LIMIT:-2150}     # seconds of the hold we allow ourselves (slot max 2400)
T0=$SECONDS
left() { echo $(( LIMIT - (SECONDS - T0) )); }
step() {   # min_seconds_needed, command...  (the command gets --timeout <left - 90>)
  local need=$1; shift
  local l=$(left)
  if [ $l -lt $need ]; then echo "[run_r04b] skip (left ${l}s < ${need}s): $*"; return 0; fi
  echo "[run_r04b $(date +%H:%M:%S)] left ${l}s: $*"
  "$@" --timeout $(( l - 90 ))
}
mkdir -p "$RND"
TOUR="$WT/tools/perf_ue/capture_tour.py"
case "$1" in
  S) python3 "$WT/tools/perf_ue/sweeps/gen_g7.py" "$SCR/eval7" && python3 "$WT/tools/perf_ue/sweeps/gen_n7.py" "$SCR/eval7" || exit 1
     step 600 python3 "$TOUR" --round "$SCR/eval7" --presets golden --res 1920x1080 --variants "$SCR/eval7/v_g7a.json" --work "$SCR/eval7/tour_a"
     step 600 python3 "$TOUR" --round "$SCR/eval7" --presets golden --res 1920x1080 --variants "$SCR/eval7/v_g7b.json" --work "$SCR/eval7/tour_b"
     step 420 python3 "$TOUR" --round "$SCR/eval7" --presets night --res 1920x1080 --shots S1,S4,S5,S6 --variants "$SCR/eval7/v_n7.json" --work "$SCR/eval7/tour_n" ;;
  F) "$WT/tools/perf_ue/rebuild_look.sh" ${R04_STEPS:-rigs,night,maps} ${R04_PRESETS:-golden,night} || exit $?
     step 500 python3 "$TOUR" --round "$RND" --presets golden --res 1920x1080 --work "$SCR/tour_r04" --redo
     step 500 python3 "$TOUR" --round "$RND" --presets golden --res 3840x2160 --sp 50 --work "$SCR/tour_r04" --redo
     step 500 python3 "$TOUR" --round "$RND" --presets night --res 1920x1080 --work "$SCR/tour_r04" --redo
     step 500 python3 "$TOUR" --round "$RND" --presets night --res 3840x2160 --sp 50 --work "$SCR/tour_r04" --redo
     step 500 python3 "$TOUR" --round "$RND" --presets midday --res 1920x1080 --work "$SCR/tour_r04" --redo
     step 500 python3 "$TOUR" --round "$RND" --presets midday --res 3840x2160 --sp 50 --work "$SCR/tour_r04" --redo ;;
  C) for p in golden night midday; do step 600 python3 "$WT/tools/perf_ue/capture_looks.py" --round "$RND" --presets $p --clips --no-stills --no-warmup; done ;;
  *) echo "usage: run_r04b.sh S|F|C"; exit 2 ;;
esac
echo "[run_r04b] phase $1 done, $(( SECONDS - T0 )) s"
