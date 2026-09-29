#!/bin/bash
# Street enemies (thug, brute, hood, tee, beard) for Unreal: raw Tripo people (~/sm2-assets/raw, the owner's assets, never committed) -> dress -> fit to the hero's
# 58-bone skeleton -> texture-free GLB for Interchange + 4096^2 base colour PNG. Idempotent; the (slow) skinfit step is cached on the
# SHA of the prepared mesh.   Fan homage project; not official Marvel/Sony/Insomniac.
#   tools/ue_char/people/build_people.sh [--force]
set -e
WT="$(cd "$(dirname "$0")/../../.." && pwd)"
SCR=/Users/midir/sm2-n1/_scratch/characters/r3
GLB=/Users/midir/sm2-n1/_scratch/characters/ueimport
ART="$WT/art/night1/characters/people"
mkdir -p "$SCR/people" "$SCR/fit" "$GLB" "$ART"
for src in "leather+jacket+man+3d+model.glb" "human+character+3d+model.glb" "human+figure+3d+model.glb" "adult+male+3d+model.glb" "human+character+3d+model (3).glb" "baseball+cap+3d+model.glb"; do
  [ -f "$HOME/sm2-assets/raw/$src" ] || { echo "missing raw Tripo person: ~/sm2-assets/raw/$src" >&2; exit 1; }
done
pids=()
PEOPLE="thug brute hood tee beard"
for c in $PEOPLE; do
  C="Street$(python3 -c "print('$c'.capitalize())")"
  python3 "$WT/tools/ue_char/people/prepare_person.py" $c --out "$SCR/people" > "$SCR/people/$C.prep.log"
  sha=$(shasum "$SCR/people/${C}_prepared.glb" | cut -d' ' -f1)
  if [ "$1" = "--force" ] || [ ! -f "$SCR/fit/$C.glb" ] || [ "$(cat "$SCR/fit/$C.sha" 2>/dev/null)" != "$sha" ]; then
    ( python3 "$WT/tools/skinfit/skinfit.py" "$SCR/people/${C}_prepared.glb" "$SCR/fit/$C.glb" --name "$C" --spatial-smooth 0.035 --weld --report "$SCR/fit/$C.json" > "$SCR/fit/$C.log" 2>&1 && echo "$sha" > "$SCR/fit/$C.sha" ) &
    pids+=($!)
  fi
done
for p in "${pids[@]}"; do wait "$p"; done
for c in $PEOPLE; do
  C="Street$(python3 -c "print('$c'.capitalize())")"
  N="$(python3 -c "print('$c'.capitalize())")"
  [ -f "$SCR/fit/$C.glb" ] || { echo "skinfit failed for $C (see $SCR/fit/$C.log)" >&2; exit 1; }
  python3 "$WT/tools/ue_char/strip_glb.py" "$SCR/fit/$C.glb" "$GLB/SK_Street_$N.glb" > /dev/null
  cp "$SCR/people/${C}_atlas.png" "$ART/${c}_basecolor.png"
  for v in "$SCR/people/${C}"_*_atlas.png; do            # tint variants (same mesh): <c>_<Variant>_basecolor.png
    [ -f "$v" ] || continue
    t=$(basename "$v" _atlas.png); t=${t#${C}_}
    cp "$v" "$ART/${c}_${t}_basecolor.png"
  done
done
# upright / heavy walk clips (numpy IK on the hero walk), appended to a copy of the thug fit; UE imports only the animations from it
python3 "$WT/tools/ue_char/people/make_walk.py" "$SCR/fit/StreetThug.glb" "$SCR/fit/walks.glb" > "$SCR/fit/walks.log"
python3 "$WT/tools/ue_char/strip_glb.py" "$SCR/fit/walks.glb" "$GLB/SK_Street_Walks.glb" > /dev/null
echo "people ok: $(ls "$GLB"/SK_Street_*.glb | wc -l) meshes, textures in $ART"
