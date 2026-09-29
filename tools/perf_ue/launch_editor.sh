#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# (Re)launch THIS worktree's (P4 Look) Unreal Editor: MCP :8774 + the file job server (tools/perf_ue/job_server.py).
# Stop: pkill -9 -f "/Users/midir/sm2-n1/look/unreal/WebHomage/WebHomage.uproject"   (only matches this worktree)
P=/Users/midir/sm2-n1/look/unreal/WebHomage/WebHomage.uproject
mkdir -p /Users/midir/sm2-n1/look/unreal/WebHomage/Saved/Logs
pkill -9 -f "$P"; sleep 3
open -n "/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app" --args "$P" -NoCrashReports -unattended \
  -ModelContextProtocolStartServer -ModelContextProtocolPort=8774 \
  -abslog=/Users/midir/sm2-n1/look/unreal/WebHomage/Saved/Logs/look.log \
  "-ExecCmds=py /Users/midir/sm2-n1/look/tools/perf_ue/job_server.py"
