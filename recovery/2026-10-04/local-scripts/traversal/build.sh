#!/bin/bash
# P3 build helper: clear every WebHomage dylib + the module manifest first (F1 wrapper can leave the manifest pointing at a
# deleted hot-reload dylib), then run the F1 wrapper.
cd /Users/midir/sm2-n1/traversal/unreal/WebHomage || exit 1
rm -f Binaries/Mac/libUnrealEditor-WebHomage*.dylib Binaries/Mac/UnrealEditor.modules
Scripts/build_editor.sh > /Users/midir/sm2-n1/_scratch/traversal/build_last.log 2>&1
RC=$?
grep -E "error|Result:|OK:|ERROR" /Users/midir/sm2-n1/_scratch/traversal/build_last.log | head -30
exit $RC
