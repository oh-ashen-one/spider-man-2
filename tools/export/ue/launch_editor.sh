#!/bin/zsh
# (Re)launch THIS worktree's Unreal Editor (P1 City): MCP :8771 + file job server (tools/export/ue/job_server.py).
# Stop: pkill -9 -f "/Users/midir/sm2-n1/city/unreal/WebHomage/WebHomage.uproject"
P=/Users/midir/sm2-n1/city/unreal/WebHomage/WebHomage.uproject
pkill -9 -f "$P"; sleep 3
open -n "/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app" --args "$P" -NoCrashReports -unattended \
  -ModelContextProtocolStartServer -ModelContextProtocolPort=8771 \
  -abslog=/Users/midir/sm2-n1/city/unreal/WebHomage/Saved/Logs/city.log \
  "-ExecCmds=py /Users/midir/sm2-n1/city/tools/export/ue/job_server.py"
