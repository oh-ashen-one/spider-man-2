# WebHomage — Unreal Engine 5.8 port

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. Nothing here is meant to infringe copyright. See `../../DISCLAIMER.md`.

Unreal port of the browser build in this repo (the browser version stays the primary, working build).

- Engine: UE 5.8.3 (launcher install, `/Users/Shared/Epic Games/UE_5.8`), Mac Studio M3 Ultra.
- Launch (always detached, crash reporter off so it can't steal the MCP port):
  `open -n "/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app" --args "$PWD/WebHomage.uproject" -NoCrashReports -ModelContextProtocolStartServer -ModelContextProtocolPort=8765`
- MCP: official plugin (`ModelContextProtocol` + `EditorToolset`) on `http://127.0.0.1:8765/mcp`; registered for Claude Code in `/.mcp.json`; CLI helper `tools/ue/mcp.py`.
- Stop only YOUR instance: `pkill -9 -f "<your worktree abs path>/unreal/WebHomage/WebHomage.uproject"` (Studio ignores plain kill; a bare `WebHomage.uproject` pattern kills every agent's editor).
- `.uasset`/`.umap` are Git LFS.

## C++ foundation (night 1, piece F1)

- Module `WebHomage` (Source/WebHomage): `Core/` has `AWebHomageGameMode` (project default), `AWebHomageCharacter`
  (capsule + cylinder proxy, spring-arm camera, Enhanced Input WASD / mouse / Space built at runtime, so no input assets are needed),
  `AWebHomagePlayerController` (mouse-safe: Escape always releases) and `UWebHomageAutomation` (screenshots, perf, auto-quit).
- Build: `Scripts/build_editor.sh` (Xcode 27.0 works with UE 5.8.3 as installed).
- Map `/Game/Maps/Foundation_Test` (editor startup + game default) is regenerated headless by
  `UnrealEditor <uproject> -run=pythonscript -script=$PWD/Scripts/make_foundation_test.py -unattended -nullrhi` (about 20 s).
- Rendering: Lumen GI + reflections with hardware RT (METAL_SM6 supports it in 5.8; the log shows "Ray tracing is enabled"),
  Nanite, VSM, TSR, motion blur, SM6-only target, no frame smoothing / fixed step.
- Capture, video and perf recipes: `CAPTURE.md`.
