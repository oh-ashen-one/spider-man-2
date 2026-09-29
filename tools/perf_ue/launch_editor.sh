#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# (Re)launch THIS worktree's (P4 Look) Unreal Editor: invisible (-RenderOffScreen -NoSound), MCP port + the file job server (tools/perf_ue/job_server.py).
# Waits (polls every 60 s) while 3 or more UnrealEditor instances are running (RULES.md). Close it whenever you are not using it.
# Env: SM2_LOOK_MCP_PORT (default 8774), SM2_LOOK_SCRATCH (default /Users/midir/sm2-n1/_scratch/look; job dir = $SM2_LOOK_SCRATCH/uejobs).
# Stop: pkill -9 -f "<worktree>/unreal/WebHomage/WebHomage.uproject"   (only matches this worktree)
WT="$(cd "$(dirname "$0")/../.." && pwd)"
P="$WT/unreal/WebHomage/WebHomage.uproject"
PORT=${SM2_LOOK_MCP_PORT:-8774}
export SM2_LOOK_SCRATCH=${SM2_LOOK_SCRATCH:-/Users/midir/sm2-n1/_scratch/look}
mkdir -p "$WT/unreal/WebHomage/Saved/Logs"
pkill -9 -f "$P"; sleep 3
while [ "$(pgrep -f 'MacOS/UnrealEditor( |$)' | wc -l | tr -d ' ')" -ge 3 ]; do echo "3+ UnrealEditor instances running, waiting 60 s"; sleep 60; done
open -n "/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app" --args "$P" -NoCrashReports -unattended -RenderOffScreen -NoSound \
  -ModelContextProtocolStartServer -ModelContextProtocolPort=$PORT \
  -abslog="$WT/unreal/WebHomage/Saved/Logs/look.log" \
  "-ExecCmds=py $WT/tools/perf_ue/job_server.py"
