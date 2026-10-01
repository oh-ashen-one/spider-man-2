#!/bin/bash
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# Round 11 post-processing after chain_r11.sh (CPU only): copy the evidence into docs/night1/characters/round-11, build the swatch sheet, measure the swap on the pixels,
# OCR the 4K stills, write SPEC_CHECK.md.     bash tools/ue_char/suits/post_r11.sh [chain out dir]
set -u
WT="$(cd "$(dirname "$0")/../../.." && pwd)"
export P2_SCRATCH="${P2_SCRATCH:-/Users/midir/sm2-n1/_scratch/characters}"
OUT="${1:-$P2_SCRATCH/r11/chain}"
R="$WT/docs/night1/characters/round-11"; E="$R/evidence"
mkdir -p "$R/stills" "$E"
cd "$WT"
# --- stills: front + chest stay 4K, back + head are committed at 1920 px (size); the swatch sheet uses the 4K originals
for f in "$OUT"/stills/skin_*_4k.jpg; do
  [ -f "$f" ] || continue
  b=$(basename "$f")
  case "$b" in
    *_front_4k.jpg|*_chest_4k.jpg) cp "$f" "$R/stills/$b";;
    *) ffmpeg -loglevel error -y -i "$f" -vf scale=1920:-2 -q:v 3 "$R/stills/${b%_4k.jpg}_1080p.jpg";;
  esac
done
python3 tools/ue_char/suits/swatch_sheet.py "$OUT/stills" "$R/SWATCH_SHEET.jpg"
# --- clips
for pair in "pawn/pawn.mp4:swap_pawn_T_key.mp4" "orbit/orbit.mp4:orbit_all_suits.mp4"; do
  s="${pair%%:*}"; d="${pair##*:}"
  [ -f "$OUT/$s" ] && cp "$OUT/$s" "$R/$d" && ls -la "$R/$d" | awk '{print $5, $9}'
done
[ -f "$OUT/persist/persist_00_t003.0.png" ] && ffmpeg -loglevel error -y -i "$OUT/persist/persist_00_t003.0.png" -q:v 3 "$R/persist_start.jpg"
for f in "$OUT"/persist/persist_*.png; do [ -f "$f" ] && ffmpeg -loglevel error -y -i "$f" -q:v 3 "$R/persist_start.jpg" && break; done
for f in "$OUT"/menu/menu_*.png; do [ -f "$f" ] && ffmpeg -loglevel error -y -i "$f" -q:v 3 "$R/settings_menu_suit_row.jpg" && break; done
# --- evidence copies
for n in pawn persist menu orbit; do [ -f "$OUT/$n/suit_log.txt" ] && cp "$OUT/$n/suit_log.txt" "$E/${n}_suit_log.txt"; done
cp "$OUT/pawn/GameUserSettings_after_pawn.ini" "$E/" 2>/dev/null
cp "$OUT/build_summary.txt" "$E/" 2>/dev/null; cp "$OUT/characters_build.log" "$E/characters_build.log" 2>/dev/null
cp "$OUT/chain.log" "$E/" 2>/dev/null; cp "$OUT/gpu_util_before_stills.txt" "$E/" 2>/dev/null
cp "$OUT"/stills/skins_perf.json "$E/stills_perf.json" 2>/dev/null
cp "$P2_SCRATCH/r11/ipguard_4096.json" "$E/ipguard.json" 2>/dev/null; cp "$P2_SCRATCH/r11/seams_4096.json" "$E/seams.json" 2>/dev/null; cp "$P2_SCRATCH/r11/ocr_atlas.json" "$E/ocr_atlas.json" 2>/dev/null
# --- swap latency on the pixels of the fixed-step movie
[ -d "$OUT/pawn/pawn_frames" ] && python3 tools/ue_char/suits/analyze_swap.py "$OUT/pawn/pawn_frames" "$E/pawn_suit_log.txt" "$E/swap_latency.json"
# --- persistence summary from the logs
{ echo "pawn run end: $(grep -h 'suit saved' "$E/pawn_suit_log.txt" 2>/dev/null | tail -1)";
  echo "relaunch:     $(grep -h 'start suit' "$E/persist_suit_log.txt" 2>/dev/null | tail -1)";
  echo "ini:          $(grep -h -E 'HeroSuit' "$E/GameUserSettings_after_pawn.ini" 2>/dev/null | tr '\n' ' ')"; } > "$E/persist.txt"
cat "$E/persist.txt"
# --- OCR of every 4K still (4 quadrants, normal + inverted, tesseract)
python3 tools/ue_char/suits/ip_guard.py ocr "$E/ocr_stills.json" "$OUT"/stills/skin_*_4k.jpg | tail -3
python3 tools/ue_char/suits/spec_check_r11.py "$R" > "$R/SPEC_CHECK.md" && echo "SPEC_CHECK.md written"
du -sh "$R"
