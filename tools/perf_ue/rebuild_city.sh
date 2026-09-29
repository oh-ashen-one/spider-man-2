#!/bin/zsh
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P4 wrapper around P1's city pipeline (tools/export, unchanged) using P4's own ports and scratch dirs, so it never touches
# P1's dev server (5202), editor (8771), export or chrome profile.
#   1. vite on 5205 (this worktree)   2. tools/export/export_city.mjs -> <SCR>/export/midtown3x3   3. rewrite the manifest's
#   texture URLs 5205 -> 5202 (prep_textures.py / build_city.py split on '5202/')   4. prep_textures.py + gen_shaders.mjs
#   5. Scripts/build_city.py in the P4 editor (tools/perf_ue/launch_editor.sh, job server) = /Game/City + /Game/Tests/City
#   6. tools/perf_ue/rebuild_look.sh geo   (patch the city geometry level for the traversal + Look_Boxes)   [run by you afterwards]
# usage: tools/perf_ue/rebuild_city.sh        (about 10 min export + import; the editor must be running: tools/perf_ue/launch_editor.sh)
set -e
WT="$(cd "$(dirname "$0")/../.." && pwd)"; cd "$WT"
SCR=/Users/midir/sm2-n1/_scratch/look; mkdir -p $SCR
[ -d node_modules ] || npm ci
curl -s -o /dev/null http://127.0.0.1:5205/ || { (nohup npx vite --port 5205 --host 127.0.0.1 --strictPort > $SCR/vite.log 2>&1 &); sleep 4; }
[ -n "$SKIP_EXPORT" ] || node tools/export/export_city.mjs --url http://127.0.0.1:5205/ --out $SCR/export/midtown3x3 --profile $SCR/chrome-profile
sed -i '' 's#127.0.0.1:5205/#127.0.0.1:5202/#g' $SCR/export/midtown3x3/manifest.json
python3 tools/export/prep_textures.py $SCR/tex $SCR/export/midtown3x3/manifest.json
node tools/export/gen_shaders.mjs
UEJOB_TIMEOUT=7200 python3 tools/perf_ue/uejob.py unreal/WebHomage/Scripts/build_city.py steps=${STEPS:-clean,tex,mat,mesh,proto,map}
echo "city content rebuilt. Now: close the editor (pkill -9 -f $WT/unreal/WebHomage/WebHomage.uproject), then tools/perf_ue/rebuild_look.sh"
