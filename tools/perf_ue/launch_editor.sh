#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# (Re)launch THIS worktree's (P4 Look) Unreal Editor: invisible (-RenderOffScreen -NoSound), MCP port + the file job server (tools/perf_ue/job_server.py).
# Waits in the GPU-slot queue (gpu_slot.sh capture, N shared slots) before the editor starts. Close it whenever you are not using it.
# Env: SM2_LOOK_MCP_PORT (default 8774), SM2_LOOK_SCRATCH (default /Users/midir/sm2-n1/_scratch/look; job dir = $SM2_LOOK_SCRATCH/uejobs).
# Stop: /Users/midir/sm2-n1/_scratch/gpu/bin/stop_ue.sh "<bracketed pattern of this worktree, e.g. /Users/midir/sm2-n1/[l]ook/unreal>"  (drivers first, SIGTERM, 60 s; never kill -9 first)
WT="$(cd "$(dirname "$0")/../.." && pwd)"
P="$WT/unreal/WebHomage/WebHomage.uproject"
PORT=${SM2_LOOK_MCP_PORT:-8774}
export SM2_LOOK_SCRATCH=${SM2_LOOK_SCRATCH:-/Users/midir/sm2-n1/_scratch/look}
mkdir -p "$WT/unreal/WebHomage/Saved/Logs"
if pgrep -f "MacOS/UnrealEditor $P" >/dev/null; then echo "this worktree's editor is running: stop it with stop_ue.sh first"; exit 2; fi
# (round 03) the cap is enforced by gpu_slot.sh (N shared slots, FIFO; N is tuned by the health monitor), not by counting processes here
# RULES (2026-09-29 16:43): launched through the GPU slot with the binary itself (never `open -n`: the wrapper must outlive the process); the slot is held while the editor runs
GS=${GPU_SLOT:-/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh}
nohup "$GS" capture --label look --json "$WT/unreal/WebHomage/Saved/Logs/look_editor_slot.json" -- "/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor" "$P" -NoCrashReports -unattended -RenderOffScreen -NoSound \
  -ModelContextProtocolStartServer -ModelContextProtocolPort=$PORT \
  -abslog="$WT/unreal/WebHomage/Saved/Logs/look.log" \
  "-ExecCmds=py $WT/tools/perf_ue/job_server.py" > "$WT/unreal/WebHomage/Saved/Logs/look_editor.stdout" 2>&1 &
