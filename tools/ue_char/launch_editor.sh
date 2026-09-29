#!/bin/sh
# Launch the P2 Characters editor (own instance, MCP :8772, python mailbox). Fan homage project.
WT=/Users/midir/sm2-n1/characters
open -n "/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app" --args "$WT/unreal/WebHomage/WebHomage.uproject" \
  -NoCrashReports -ModelContextProtocolStartServer -ModelContextProtocolPort=8772 \
  -EnablePlugins=PythonScriptPlugin,EditorScriptingUtilities,MovieRenderPipeline,SequencerScripting,IKRig,ControlRig \
  -ExecCmds="py $WT/tools/ue_char/ue_mailbox.py" \
  "-ini:Input:[/Script/Engine.InputSettings]:bCaptureMouseOnLaunch=False" "-ini:Input:[/Script/Engine.InputSettings]:DefaultViewportMouseCaptureMode=NoCapture" -log=CharEditor.log
