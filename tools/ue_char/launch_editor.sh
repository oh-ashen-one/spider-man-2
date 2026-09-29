#!/bin/sh
# Launch the P2 Characters editor (own instance, MCP :8772, python mailbox). Fan homage project.
WT=/Users/midir/sm2-n1/characters
"$WT/tools/ue_char/ue_wait.sh"   # owner rule: never a 3rd+ Unreal instance; close the editor when not in use
open -n "/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app" --args "$WT/unreal/WebHomage/WebHomage.uproject" \
  -RenderOffScreen -NoSound -NoCrashReports -ModelContextProtocolStartServer -ModelContextProtocolPort=8772 \
  -EnablePlugins=PythonScriptPlugin,EditorScriptingUtilities,MovieRenderPipeline,SequencerScripting,IKRig,ControlRig \
  -ExecCmds="py $WT/tools/ue_char/ue_mailbox.py" \
  "-ini:Input:[/Script/Engine.InputSettings]:bCaptureMouseOnLaunch=False" "-ini:Input:[/Script/Engine.InputSettings]:DefaultViewportMouseCaptureMode=NoCapture" -abslog=$WT/unreal/WebHomage/Saved/Logs/characters.log
