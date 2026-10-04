import csv, sys, math
def pct(v,p):
    v=sorted(v); k=(len(v)-1)*p; a=int(k); b=min(a+1,len(v)-1); return v[a]+(v[b]-v[a])*(k-a)
def load(path):
    R=list(csv.DictReader(open(path)))
    for i in range(len(R)-1):
        for k in ('pcm_pitch','pcm_yaw','pcm_z'): R[i][k]=R[i+1][k]
    return R[:-1]
for d in sys.argv[1:]:
    print('==',d)
    allw=[];allh=[]
    for n in ['a_swing_chain','b_release_trick_dive_zip','f1_flow_backDouble','f2_flow_pikeSwan','f3_flow_corkscrew','f4_chain_flips','f5_canyon_backDouble']:
        try: R=load('%s/%s/probe_telemetry.csv'%(d,n))
        except Exception as e: continue
        idx=[i for i,r in enumerate(R) if r['flip_prog']]
        w=set()
        for i in idx:
            for j in range(i,min(len(R),i+31)): w.add(j)
        w=sorted(w)
        hb=[float(R[i]['hero_bbox_h']) for i in w]
        hh=[float(R[i]['hero_bbox_h']) for i in idx if float(R[i]['flipcam_k'])>=0.9]
        allw+=hb; allh+=hh
        print('%-28s WIN p10/50/90 %.3f %.3f %.3f | HOLD %.3f %.3f %.3f'%(n,pct(hb,.1),pct(hb,.5),pct(hb,.9),pct(hh,.1) if hh else 0,pct(hh,.5) if hh else 0,pct(hh,.9) if hh else 0))
    print('%-28s WIN p10/50/90 %.3f %.3f %.3f | HOLD %.3f %.3f %.3f'%('POOLED',pct(allw,.1),pct(allw,.5),pct(allw,.9),pct(allh,.1),pct(allh,.5),pct(allh,.9)))
