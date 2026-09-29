#!/bin/zsh
# Rebuild P1 City content from committed sources: browser export -> texture prep -> shader includes -> UE build.
# Requires: dev server on :5202 (npx vite --port 5202 --host 127.0.0.1 --strictPort) and the P1 editor with its job
# server (tools/export/ue/launch_editor.sh).  STEPS=clean,tex,mat,mesh,proto,map (default all).
set -e
cd "$(dirname "$0")/../.."
[ -n "$SKIP_EXPORT" ] || node tools/export/export_city.mjs
python3 tools/export/patch_export.py
python3 tools/export/prep_textures.py
python3 tools/export/gen_street_signs.py
python3 tools/export/street_kit.py
python3 tools/export/street_props.py
node tools/export/gen_shaders.mjs
UEJOB_TIMEOUT=7200 python3 tools/export/ue/uejob.py unreal/WebHomage/Scripts/build_city.py steps=${STEPS:-clean,tex,mat,mesh,proto,map}
