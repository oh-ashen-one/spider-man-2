#!/bin/bash
# All derived inputs of build_characters.py's 'prep' step, run OUTSIDE Unreal (no GPU, no editor slot held while it runs). Idempotent.
# Fan homage project; not official Marvel/Sony/Insomniac.   tools/ue_char/prep_all.sh
set -e
WT="$(cd "$(dirname "$0")/../.." && pwd)"
export P2_SCRATCH="${P2_SCRATCH:-$WT/unreal/WebHomage/Saved/P2Build}"
export PATH="/Applications/Blender.app/Contents/MacOS:$PATH"
cd "$WT"
CITIZENS="03_white_tee 12_sundress_mom 13_construction_worker 15_executive 04_blue_sweatshirt 08_black_suit 10_silver_tie 14_teen_skater 18_dapper_elder 19_marathon_runner 01_retired_gent 20_punk_artist 02_leather_jacket 05_black_tee 06_chrome_shades 09_kurta_waistcoat 16_lumberjack_hipster 17_hijabi_student"
python3 tools/ue_char/prep_glbs.py > /dev/null
python3 tools/ue_char/extract_textures.py > /dev/null
python3 tools/ue_char/hero_hand_fix.py
python3 tools/ue_char/hero_suit_r5.py
python3 tools/ue_char/hero_lens_r5.py "$P2_SCRATCH/ueimport/SK_Hero.glb"
bash tools/ue_char/brute/build_brute.sh > /dev/null
bash tools/ue_char/people/build_people.sh
python3 tools/ue_char/eval/underlayer.py $CITIZENS > /dev/null
bash tools/ue_char/eval/export_citizens.sh $CITIZENS
echo "prep_all ok"
