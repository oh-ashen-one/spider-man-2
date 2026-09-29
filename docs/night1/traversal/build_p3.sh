#!/bin/bash
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P3 build helper: clear every WebHomage dylib + the module manifest first (F1 wrapper can leave the manifest pointing at a
# deleted hot-reload dylib), then run the F1 wrapper.
cd "$(dirname "$0")/../../../unreal/WebHomage" || exit 1
mkdir -p Saved
rm -f Binaries/Mac/libUnrealEditor-WebHomage*.dylib Binaries/Mac/UnrealEditor.modules
Scripts/build_editor.sh > Saved/build_last.log 2>&1
RC=$?
grep -E "error|Result:|OK:|ERROR" Saved/build_last.log | head -30
exit $RC
