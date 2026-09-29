#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# (Re)launch THIS worktree's (P4 Look) Unreal Editor: invisible (-RenderOffScreen -NoSound), MCP :8774 + the file job server (tools/perf_ue/job_server.py).
# Waits (polls every 60 s) while 3 or more UnrealEditor instances are running (RULES.md). Close it whenever you are not using it.
# Stop: pkill -9 -f "/Users/midir/sm2-n1/look/unreal/WebHomage/WebHomage.uproject"   (only matches this worktree)
P=/Users/midir/sm2-n1/look/unreal/WebHomage/WebHomage.uproject
mkdir -p /Users/midir/sm2-n1/look/unreal/WebHomage/Saved/Logs
pkill -9 -f "$P"; sleep 3
while [ "$(pgrep -f 'MacOS/UnrealEditor( |$)' | wc -l | tr -d ' ')" -ge 3 ]; do echo "3+ UnrealEditor instances running, waiting 60 s"; sleep 60; done
open -n "/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app" --args "$P" -NoCrashReports -unattended -RenderOffScreen -NoSound \
  -ModelContextProtocolStartServer -ModelContextProtocolPort=8774 \
  -abslog=/Users/midir/sm2-n1/look/unreal/WebHomage/Saved/Logs/look.log \
  "-ExecCmds=py /Users/midir/sm2-n1/look/tools/perf_ue/job_server.py"
