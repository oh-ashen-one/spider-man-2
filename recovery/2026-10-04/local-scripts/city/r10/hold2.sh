#!/bin/zsh
# r10 hold 2 (adaptive): build the new far skyline + FarSunK materials, sweep the S4 far-band lighting (one-at-a-time around A, then the combination), pick the best by tools/export/s4_score.py,
# write it into city_shots.json (S4 fog / fogc) + build_city.py defaults (MPC FarGain / FarSunK), rebuild the maps, capture all 8 views at 1080p (perf window included), then (time permitting) a glass / emission tag.
# ONE engine at a time, sequential, one gpu_slot hold (max 2400 s): every stage checks the clock.
WT=/Users/midir/sm2-n1/city
OUT=/Users/midir/sm2-n1/_scratch/city/r10/h2
mkdir -p $OUT
T0=$SECONDS
el() { echo $((SECONDS - T0)); }
sick() { ps -axo stat=,comm= | awk '$1 ~ /[ZE]/ && $2 ~ /UnrealEditor/ && $2 !~ /Services/ {f=1} END {exit !f}'; }
waitengine() { while pgrep -f "MacOS/UnrealEditor .*${WT}/unreal" >/dev/null; do sleep 3; done; }
sick && { echo "ABORT: an UnrealEditor is stuck exiting"; exit 6; }
cap() { # dir id
  sick && { echo "ABORT: engine stuck exiting before $2"; exit 7; }
  mkdir -p $1; $WT/tools/export/capture_one.sh $1 $2 1920x1080 > $1/cap_$2.txt 2>&1
  echo "capture $1 $2 rc=$? t=$(el)"; waitengine; sleep 5
}
setmpc() { # tag k=v ...
  tag=$1; shift
  $WT/tools/export/ue/run_commandlet.sh $WT/tools/export/ue/set_mpc.py "$@" > $OUT/set_$tag.txt 2>&1
  RC=$?; echo "set_mpc $tag $* rc=$RC t=$(el)"; [ $RC -ne 0 ] && { echo "SET_MPC FAILED"; exit 5; }
  waitengine
}
score() { # tag frame
  mkdir -p $OUT/$1; python3 $WT/tools/export/s4_score.py $2 > $OUT/$1/score.json 2>$OUT/$1/score.err; echo "score $1: $(cat $OUT/$1/score.json | cut -c1-400)"
}
cap_score() { # tag mapid  (current MPC)
  cap $OUT/$1 $2
  n=${2%%_*}; score $1 $OUT/$1/${n}_1920x1080_00_t028.0.png
}
run_cfg() { # tag fargain farsunk mapid
  setmpc $1 FarGain=$2 FarSunK=$3
  cap_score $1 $4
}
$WT/tools/export/ue/run_commandlet.sh $WT/unreal/WebHomage/Scripts/build_city.py steps=mat,fsky,map > $OUT/build.txt 2>&1
RC=$?; echo "build rc=$RC t=$(el)"; [ $RC -ne 0 ] && { echo "BUILD FAILED"; exit 5; }
waitengine
$WT/tools/export/ue/run_commandlet.sh $WT/tools/export/ue/view_variants.py names=g1,g3,g4 fog_g1=0.0012 fogc_g3=0.62,0.64,0.67 fogc_g4=0.50,0.52,0.55 > $OUT/variants.txt 2>&1
RC=$?; echo "variants rc=$RC t=$(el)"; [ $RC -ne 0 ] && { echo "VARIANTS FAILED"; exit 5; }
waitengine
# ---- stage 1: one-at-a-time around A (FarGain 4, FarSunK .15, fog .0008, fogc .76 .78 .80); map-level variants run right after A (same MPC), then the MPC variants
run_cfg A 4.0 0.15 S4_perch_skyline
cap_score A1 S4vg1
cap_score A3 S4vg3
cap_score A4 S4vg4
run_cfg B 4.0 0.10 S4_perch_skyline
run_cfg B2 4.0 0.22 S4_perch_skyline
echo "STAGE1 DONE t=$(el)"
# ---- stage 2: the combination of the winners
eval $(python3 $WT/tools/export/s4_pick.py $OUT combine 2>$OUT/combine.err)
echo "combined: FG=$FG FK=$FK FOG=$FOG FOGC=$FOGC"
if [ "$FG $FK $FOG $FOGC" != "4.0 0.15 0.0008 0.76,0.78,0.80" ]; then
  mkdir -p $OUT/Z; echo "{\"FG\":\"$FG\",\"FK\":\"$FK\",\"FOG\":\"$FOG\",\"FOGC\":\"$FOGC\"}" > $OUT/Z/config.json
  $WT/tools/export/ue/run_commandlet.sh $WT/tools/export/ue/view_variants.py names=gz fog_gz=$FOG fogc_gz=$FOGC > $OUT/variants_z.txt 2>&1
  RC=$?; echo "variants z rc=$RC t=$(el)"; waitengine
  [ $RC -eq 0 ] && run_cfg Z $FG $FK S4vgz
fi
echo "STAGE2 DONE t=$(el)"
# ---- final configuration
eval $(python3 $WT/tools/export/s4_pick.py $OUT final 2>$OUT/final.err)
echo "FINAL: tag=$TAG FG=$FG FK=$FK FOG=$FOG FOGC=$FOGC"
echo "{\"TAG\":\"$TAG\",\"FG\":\"$FG\",\"FK\":\"$FK\",\"FOG\":\"$FOG\",\"FOGC\":\"$FOGC\"}" > $OUT/final_config.json
python3 - "$FG" "$FK" "$FOG" "$FOGC" <<'PY'
import sys, json, re
fg, fk, fog, fogc = sys.argv[1:5]
p = '/Users/midir/sm2-n1/city/unreal/WebHomage/Scripts/city_shots.json'
d = json.load(open(p))
for s in d:
    if s['id'] == 'S4_perch_skyline':
        for k in ('fog', 'fogc'): s.pop(k, None)
        if fog != '0.0008': s['fog'] = float(fog)
        if fogc != '0.76,0.78,0.80': s['fogc'] = [float(v) for v in fogc.split(',')]
json.dump(d, open(p, 'w'), indent=1)
p = '/Users/midir/sm2-n1/city/unreal/WebHomage/Scripts/build_city.py'
s = open(p).read()
s = re.sub(r"\('FarGain', [0-9.]+\)", "('FarGain', %s)" % fg, s, count=1)
s = re.sub(r"\('FarSunK', [0-9.]+\)", "('FarSunK', %s)" % fk, s, count=1)
open(p, 'w').write(s)
PY
setmpc F FarGain=$FG FarSunK=$FK
$WT/tools/export/ue/run_commandlet.sh $WT/unreal/WebHomage/Scripts/build_city.py steps=map > $OUT/build_final.txt 2>&1
RC=$?; echo "build final rc=$RC t=$(el)"; [ $RC -ne 0 ] && { echo "BUILD FINAL FAILED"; exit 5; }
waitengine
# ---- all 8 views, 1080p, with the frame-time window (the deadline keeps the hold under its 2400 s maximum)
CAPTURE_DEADLINE_S=$((2200 - $(el))) RES_LIST="1920x1080" $WT/tools/export/capture_round.sh $OUT/final > $OUT/final_capture.txt 2>&1
echo "final captures rc=$? t=$(el)"
waitengine
echo "FINAL SET DONE t=$(el)"
# ---- extras (only with time left): glass / emission tag D on the views the critic boxes live in, then restore the MPC
if [ $(el) -lt 1750 ]; then
  setmpc D F0Scale=0.5 DayEmisK=0.18
  for id in S8_aerial_midtown S5_timessq_south S2_avenue_swing S1_avenue_street; do [ $(el) -lt 2150 ] && cap $OUT/D $id; done
  setmpc R F0Scale=0.8 DayEmisK=0.22
fi
echo HOLD2_DONE t=$(el)
