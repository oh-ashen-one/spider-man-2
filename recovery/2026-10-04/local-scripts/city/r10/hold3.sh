#!/bin/zsh
# r10 hold 3: rebuild (secondary materials), coordinate search of the S4 far-band lighting around the hold-2 winner (tools/export/s4_opt.py), apply the best, re-capture all 8 views at 1080p.
WT=/Users/midir/sm2-n1/city
OUT=/Users/midir/sm2-n1/_scratch/city/r10/h3
mkdir -p $OUT
T0=$SECONDS
el() { echo $((SECONDS - T0)); }
sick() { ps -axo stat=,comm= | awk '$1 ~ /[ZE]/ && $2 ~ /UnrealEditor/ && $2 !~ /Services/ {f=1} END {exit !f}'; }
waitengine() { while pgrep -f "MacOS/UnrealEditor .*${WT}/unreal" >/dev/null; do sleep 3; done; }
sick && { echo "ABORT: an UnrealEditor is stuck exiting"; exit 6; }
$WT/tools/export/ue/run_commandlet.sh $WT/unreal/WebHomage/Scripts/build_city.py steps=mat,map > $OUT/build.txt 2>&1
RC=$?; echo "build rc=$RC t=$(el)"; [ $RC -ne 0 ] && { echo "BUILD FAILED"; exit 5; }
waitengine
python3 $WT/tools/export/s4_opt.py $OUT/opt 1150 > $OUT/opt.txt 2>&1
echo "opt rc=$? t=$(el)"; tail -3 $OUT/opt.txt | cut -c1-300
eval $(grep '^BEST_TAG=' $OUT/opt.txt | tail -1)
if [ -z "$BEST_TAG" ]; then echo "NO BEST: keeping the current configuration"; BEST_TAG=none; FOG=0.0012; FOGC=0.76,0.78,0.80; AERIAL=0.34; FG=4.0; FK=0.22; FJ=1.3; fi
echo "FINAL: tag=$BEST_TAG FG=$FG FK=$FK FJ=$FJ FOG=$FOG FOGC=$FOGC AERIAL=$AERIAL"
python3 - "$FG" "$FK" "$FJ" "$FOG" "$FOGC" "$AERIAL" <<'PY'
import sys, json, re
fg, fk, fj, fog, fogc, aer = sys.argv[1:7]
p = '/Users/midir/sm2-n1/city/unreal/WebHomage/Scripts/city_shots.json'
d = json.load(open(p))
for s in d:
    if s['id'] == 'S4_perch_skyline':
        for k in ('fog', 'fogc', 'aerial'): s.pop(k, None)
        if float(fog) != 0.0008: s['fog'] = float(fog)
        if fogc != '0.76,0.78,0.80': s['fogc'] = [float(v) for v in fogc.split(',')]
        if float(aer) != 0.34: s['aerial'] = float(aer)
json.dump(d, open(p, 'w'), indent=1)
p = '/Users/midir/sm2-n1/city/unreal/WebHomage/Scripts/build_city.py'
s = open(p).read()
s = re.sub(r"\('FarGain', [0-9.]+\)", "('FarGain', %s)" % fg, s, count=1)
s = re.sub(r"\('FarSunK', [0-9.]+\)", "('FarSunK', %s)" % fk, s, count=1)
s = re.sub(r"\('FarJit', [0-9.]+\)", "('FarJit', %s)" % fj, s, count=1)
open(p, 'w').write(s)
PY
echo "{\"TAG\":\"$BEST_TAG\",\"FG\":\"$FG\",\"FK\":\"$FK\",\"FJ\":\"$FJ\",\"FOG\":\"$FOG\",\"FOGC\":\"$FOGC\",\"AERIAL\":\"$AERIAL\"}" > $OUT/final_config.json
$WT/tools/export/ue/run_commandlet.sh $WT/tools/export/ue/set_mpc.py FarGain=$FG FarSunK=$FK FarJit=$FJ > $OUT/set_final.txt 2>&1
echo "set_mpc final rc=$? t=$(el)"; waitengine
$WT/tools/export/ue/run_commandlet.sh $WT/unreal/WebHomage/Scripts/build_city.py steps=map > $OUT/build_final.txt 2>&1
RC=$?; echo "build final rc=$RC t=$(el)"; [ $RC -ne 0 ] && { echo "BUILD FINAL FAILED"; exit 5; }
waitengine
CAPTURE_DEADLINE_S=$((2250 - $(el))) RES_LIST="1920x1080" $WT/tools/export/capture_round.sh $OUT/final > $OUT/final_capture.txt 2>&1
echo "final captures rc=$? t=$(el)"
waitengine
echo "HOLD3_DONE t=$(el)"
