import sys, cv2, numpy as np
# per-frame mean abs diff of consecutive frames (downscaled gray); a cut shows as an isolated spike vs its neighbours
p=sys.argv[1]; cap=cv2.VideoCapture(p); prev=None; d=[]
while True:
    ok,f=cap.read()
    if not ok: break
    g=cv2.cvtColor(cv2.resize(f,(240,135)),cv2.COLOR_BGR2GRAY).astype(np.float32)
    if prev is not None: d.append(float(np.abs(g-prev).mean()))
    prev=g
d=np.array(d); med=np.median(d)
print(p.split('/')[-1], 'frames',len(d)+1,'diff median %.2f p99 %.2f max %.2f @ %.2fs'%(med,np.percentile(d,99),d.max(),(d.argmax()+1)/60))
# isolated spikes: > 3x the median of the 4 neighbours and > 8
sp=[(i+1)/60 for i in range(2,len(d)-2) if d[i]>8 and d[i]>3*np.median(np.r_[d[i-2:i],d[i+1:i+3]])]
print(' isolated spikes (>8 and >3x neighbours):',['%.2f'%s for s in sp] if sp else 'none')
