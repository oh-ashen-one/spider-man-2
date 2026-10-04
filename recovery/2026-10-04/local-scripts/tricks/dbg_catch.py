exec(open('/Users/midir/sm2-n1/_scratch/critic-C-r01-work/an.py').read().split('res=[]')[0])
import sys
tsel=float(sys.argv[1])
c=[c for c in I if abs(t[c['i'][-1]]-tsel)<0.05][0]
e=c['i'][-1]
for k in range(e-20,e+30):
    r=T[k]
    pf=rotang(frame(J[k]),frame(J[k+1]))/(t[k+1]-t[k])
    fw=frame(J[k])[0]; up=frame(J[k])[1]
    print(f"{t[k]:6.3f} {r['mode']:6s} {r['sub']:10s} {r['anim_node'][:18]:18s} {r['anim_clip'][:12]:12s} w{r['anim_weight']:>5s} ft {r['flip_t']:>6s} fp {r['flip_pitch_deg']:>7s} bp {r['body_pitch_deg']:>7s} rope {r['body_rope_deg']:>6s} web {r['web_on']} pf {pf:6.0f} up {up.round(2)} fw {fw.round(2)}")
