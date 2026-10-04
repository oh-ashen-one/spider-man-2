#!/bin/zsh
set -e
cd /Users/midir/sm2-n1/city
python3 tools/export/patch_export.py
python3 tools/export/prep_textures.py
python3 tools/export/gen_street_signs.py
python3 tools/export/street_kit.py
python3 tools/export/street_props.py
python3 tools/export/export_vehicles.py
python3 tools/export/street_cars.py
python3 tools/export/street_trees.py
python3 tools/export/street_traffic.py
python3 tools/export/far_skyline.py
python3 tools/export/bake_sunmask.py
node tools/export/gen_shaders.mjs
echo PREP_DONE
