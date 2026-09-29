#!/bin/zsh
# (Re)launch THIS worktree's Unreal Editor (P1 City): MCP :8771 + file job server (tools/export/ue/job_server.py).
# Owner rule 2026-09-29: invisible (-RenderOffScreen -NoSound), close it when not in use, never start it while 3+ Unreal
# instances are already running (waits, polling every 60 s).
# Stop: pkill -9 -f "/Users/midir/sm2-n1/city/unreal/WebHomage/WebHomage.uproject"
# (r07) parameterised: the worktree is derived from this file's location; SM2_CITY_MCP_PORT (default 8771), SM2_CITY_SCRATCH (job dir) come from the environment
WT=${0:A:h:h:h:h}
P=$WT/unreal/WebHomage/WebHomage.uproject
MCP=${SM2_CITY_MCP_PORT:-8771}
pkill -9 -f "$P"; sleep 3
while [ "$(pgrep -f 'MacOS/UnrealEditor( |$)' | wc -l)" -ge 3 ]; do echo "3+ Unreal instances running, waiting 60 s"; sleep 60; done
ENVARGS=(); for v in SM2_CITY_SCRATCH SM2_CITY_JOBS SM2_CITY_EXPORT SM2_CITY_TEX SM2_CITY_PORT; do [ -n "${(P)v}" ] && ENVARGS+=(--env "$v=${(P)v}"); done   # `open` does not pass the environment on
open -n "${ENVARGS[@]}" "/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app" --args "$P" -NoCrashReports -unattended -RenderOffScreen -NoSound \
  -ModelContextProtocolStartServer -ModelContextProtocolPort=$MCP \
  -abslog=$WT/unreal/WebHomage/Saved/Logs/city.log \
  "-ExecCmds=py $WT/tools/export/ue/job_server.py"
