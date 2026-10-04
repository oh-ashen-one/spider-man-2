#!/bin/bash
# final captures for round 02: usage final_capture.sh "<final spec>"   (run under gpu_slot.sh capture)
SPEC="$1"
S=/Users/midir/sm2-n1/perf/tools/perf_ue2/stills2.sh; M=/Users/midir/sm2-n1/perf/tools/perf_ue2/route_movie.sh; O=/Users/midir/sm2-n1/_scratch/perf/r02/final
$S $O/after "$SPEC" "S1 S2 S7 route"
SM2_PERF_ROUTE_SHOTS=38,42 $S $O/after_hz "$SPEC" "route"
$S $O/before "before@50" "S7 route"
$M $O/movie "$SPEC"
echo FINAL_CAPTURE DONE
