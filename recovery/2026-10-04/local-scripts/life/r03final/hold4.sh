#!/bin/bash
# round 03 final, hold 4: S1 curb-lane corridor sweep (3 runs), automatic choice by YOLO (CPU, spec instrument), then the final S1 stills (1080p series + 4K) with the chosen flag.
set -uo pipefail
X=/Users/midir/sm2-n1/_scratch/life/r03/exp.sh
FD=/Users/midir/sm2-n1/_scratch/life/r03final
WT=/Users/midir/sm2-n1/life; R=$WT/docs/night1/life/round-03
T0=$(date +%s)
engine_gone() { for i in $(seq 1 90); do pgrep -f 'sm2-n1/[l]ife/unreal/WebHomage/WebHomage.uproject' >/dev/null || return 0; sleep 2; done; echo "my engine still present after 180 s: stop (no launch on top of it)"; return 1; }
run() { engine_gone || exit 6; echo "== $(date +%T) $1"; "$X" "$@"; }
S1=/Game/Tests/Life/Life_View_S1
run k1_curb60 $S1 1920x1080 12,16,20,24,28 30 - -- -WHLifeSample=8:30:1 -WHLifeClearAhead=24 -WHLifeClearCurb=60:5
run k2_curb45 $S1 1920x1080 12,16,20,24,28 30 - -- -WHLifeSample=8:30:1 -WHLifeClearAhead=24 -WHLifeClearCurb=45:5
run k3_full60 $S1 1920x1080 12,16,20,24,28 30 - -- -WHLifeSample=8:30:1 -WHLifeClearAhead=60
engine_gone || exit 6
echo "== $(date +%T) detect (CPU)"
for n in k1_curb60 k2_curb45 k3_full60; do $FD/sweep_detect.sh $n & done; wait
CHOICE=$(python3 - <<'PY'
import json,statistics as st
R='/Users/midir/sm2-n1/_scratch/life/r03'
def stats(n,f):
    d=json.load(open('%s/%s/%s'%(R,n,f))); ks=sorted(k for k in d if k.endswith('.jpg'))
    sh=[100*d[k]['people_right']/max(1,d[k]['people']) for k in ks]; return st.median(sh),min(sh)
res={}
for n,fl in (('k2_curb45','-WHLifeClearCurb=45:5'),('k1_curb60','-WHLifeClearCurb=60:5'),('k3_full60','')):
    res[n]=(stats(n,'det.json'),stats(n,'det84.json'),fl)
pick=None
for n in ('k2_curb45','k1_curb60'):
    (fm,fmin),(cm,cmin),fl=res[n]
    if cm>=37 and cmin>=30: pick=n; break
if pick is None: pick=max(('k2_curb45','k1_curb60'),key=lambda n:res[n][1][0])
print(res[pick][2]); import sys; print(json.dumps({'pick':pick,'res':res}),file=sys.stderr)
PY
)
echo "== $(date +%T) choice: $CHOICE"
export S1_EXTRA="$CHOICE"
engine_gone || exit 6
EL=$(( $(date +%s) - T0 )); [ $EL -lt 1700 ] || { echo "no time left for the final S1 stills (elapsed $EL s)"; exit 8; }
echo "== $(date +%T) final S1 stills with $S1_EXTRA"; cd $WT; VIEWS=S1 docs/night1/life/capture_round.sh $R stills
engine_gone || exit 6
EL=$(( $(date +%s) - T0 )); if [ $EL -lt 1900 ]; then echo "== $(date +%T) swing (narrow recycle cone)"; cd $WT; docs/night1/life/capture_round.sh $R clip_swing; engine_gone || exit 6; else echo "== SKIP swing (elapsed $EL s)"; fi
echo "== $(date +%T) hold4 done (elapsed $(( $(date +%s) - T0 )) s)"
