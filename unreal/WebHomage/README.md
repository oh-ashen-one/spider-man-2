# WebHomage — Unreal Engine 5.8 port

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. Nothing here is meant to infringe copyright. See `../../DISCLAIMER.md`.

Unreal port of the browser build in this repo (the browser version stays the primary, working build).

- Engine: UE 5.8.3 (launcher install, `/Users/Shared/Epic Games/UE_5.8`), Mac Studio M3 Ultra.
- Launch (always detached, crash reporter off so it can't steal the MCP port):
  `open -n "/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app" --args "$PWD/WebHomage.uproject" -NoCrashReports -ModelContextProtocolStartServer -ModelContextProtocolPort=8765`
- MCP: official plugin (`ModelContextProtocol` + `EditorToolset`) on `http://127.0.0.1:8765/mcp`; registered for Claude Code in `/.mcp.json`; CLI helper `tools/ue/mcp.py`.
- Stop only this instance: `pkill -9 -f "WebHomage.uproject"` (Studio ignores plain kill).
- `.uasset`/`.umap` are Git LFS.
