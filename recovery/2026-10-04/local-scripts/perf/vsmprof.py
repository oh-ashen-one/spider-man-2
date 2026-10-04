import sys,statistics as st
sys.path.insert(0,'/Users/midir/sm2-n1/perf/tools/perf_ue2')
from windows import load,pct
for p in sys.argv[1:]:
    hdr,idx,data=load(p)
    sd=[r[idx['GPU/ShadowDepths']] for r in data]; ft=[r[idx['FrameTime']] for r in data]
    print(p, len(data), 'SD mean %.2f p95 %.2f  FT p50 %.2f p95 %.2f'%(st.mean(sd),pct(sd,95),pct(ft,50),pct(ft,95)))
    for s in range(0,len(sd),120):
        print('  t%4.1f SD mean %.2f p95 %.2f max %.2f | FT mean %.2f p95 %.2f'%(15+s/60,st.mean(sd[s:s+120]),pct(sd[s:s+120],95),max(sd[s:s+120]),st.mean(ft[s:s+120]),pct(ft[s:s+120],95)))
