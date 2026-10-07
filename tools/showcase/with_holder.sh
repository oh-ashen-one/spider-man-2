#!/bin/bash
# runs a command with SM2_COEXIST_HOLDER set to the owner-approved Qwen resident (exactly one holder file labelled m5-flash*), waiting up to 25 min for it to be the only holder.
# The resident re-registers under a new pid and other tasks take the slot in between: never coexist with any other holder.
for i in $(seq 1 300); do
  # the owner's interactive session (an UnrealEditor -game process) must never be disturbed: any running UnrealEditor means wait
  if pgrep -f "UnrealEditor" > /dev/null; then sleep 5; continue; fi
  # other tasks' renderers (the unity loop, blender): guarded_preview would refuse and the run silently not happen, so wait for them as well
  if pgrep -f "[.]unity/bin/unity" > /dev/null || pgrep -x Blender > /dev/null; then sleep 5; continue; fi
  H=$(python3 - <<'PY'
import json, pathlib
fs = list(pathlib.Path.home().joinpath('.cache/gpu-slot/holders').glob('*.json'))
print(fs[0].stem if len(fs) == 1 and 'm5-flash' in json.loads(fs[0].read_text()).get('label', '') else '')
PY
)
  N=$(ls "$HOME/.cache/gpu-slot/holders" 2>/dev/null | wc -l | tr -d ' ')
  if [ "$N" = "0" ]; then "$@"; exit $?; fi   # nobody holds the GPU: the normal exclusive guarded_preview admission applies
  if [ -n "$H" ]; then
    SM2_COEXIST_HOLDER=$H "$@"; rc=$?
    exit $rc
  fi
  sleep 5
done
echo "no m5-flash holder within 25 min" >&2; exit 75
