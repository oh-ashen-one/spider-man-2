import json,sys,glob,os,statistics as st
R='/Users/midir/sm2-n1/_scratch/life/r03'
for n in sys.argv[1:]:
    out=[]
    for f in ('det.json','det84.json'):
        p=os.path.join(R,n,f)
        if not os.path.exists(p): out.append('n/a'); continue
        d=json.load(open(p)); ks=sorted(k for k in d if k.endswith('.jpg'))
        P=[d[k]['people'] for k in ks]; Rg=[d[k]['people_right'] for k in ks]; sh=[100*r/max(1,t) for r,t in zip(Rg,P)]
        out.append('people %s right %s share %s | med %.0f min %.0f pooled(t12-24) %.0f' % (P,Rg,[round(x) for x in sh],st.median(sh),min(sh),100*sum(Rg[:4])/max(1,sum(P[:4]))))
    print(n); print('  full:',out[0]); print('  crop:',out[1])
