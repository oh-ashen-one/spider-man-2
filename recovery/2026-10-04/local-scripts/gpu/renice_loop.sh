#!/bin/zsh
# keep every loop-owned heavy process at the lowest CPU priority (owner gaming / heavy compute on the Studio)
while true; do
  for p in $(pgrep -f "sm2-n1/[a-z]+/unreal/WebHomage/WebHomage.uproject|Blender.app/Contents/MacOS/Blender -b|rsync -rltD --no-perms|/Volumes/memory/move_afc.sh|sm2-n1/[a-z]+/tools/|build_editor.sh|UnrealBuildTool|UnrealEditor-Cmd|ShaderCompileWorker"); do
    renice 20 -p $p >/dev/null 2>&1
  done
  sleep 30
done
