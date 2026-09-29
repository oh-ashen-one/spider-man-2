#!/bin/zsh
# (Re)launch THIS worktree's Unreal Editor (P1 City): MCP :8771 + file job server (tools/export/ue/job_server.py).
# Owner rule 2026-09-29: invisible (-RenderOffScreen -NoSound), close it when not in use, never start it while 3+ Unreal
# instances are already running (waits, polling every 60 s).
# Stop: pkill -9 -f "/Users/midir/sm2-n1/city/unreal/WebHomage/WebHomage.uproject"
P=/Users/midir/sm2-n1/city/unreal/WebHomage/WebHomage.uproject
pkill -9 -f "$P"; sleep 3
while [ "$(pgrep -f 'MacOS/UnrealEditor( |$)' | wc -l)" -ge 3 ]; do echo "3+ Unreal instances running, waiting 60 s"; sleep 60; done
open -n "/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app" --args "$P" -NoCrashReports -unattended -RenderOffScreen -NoSound \
  -ModelContextProtocolStartServer -ModelContextProtocolPort=8771 \
  -abslog=/Users/midir/sm2-n1/city/unreal/WebHomage/Saved/Logs/city.log \
  "-ExecCmds=py /Users/midir/sm2-n1/city/tools/export/ue/job_server.py"
