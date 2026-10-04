import sys
I={'Tuck':1.0,'Pike':1.35,'Layout':3.2,'Swan':7.5,'Pencil':9,'Straddle':6,'Throne':9,'Twist':3.5,'Reach':7,'Kickout':float(sys.argv[1]) if len(sys.argv)>1 else 5.5}
def sm(x): x=min(max(x,0),1); return x*x*(3-2*x)
BPre,BPost=0.06,0.11
def run(name,pitch,segs):
    dur=sum(d for _,d in segs)
    starts=[];a=0
    for s,d in segs: starts.append(a); a+=d
    def inert(t):
        k=0
        for i,(s,d) in enumerate(segs):
            if t>=starts[i]: k=i
        S0=starts[k];S1=S0+segs[k][1]
        if k>0 and t<S0+BPost:
            w=sm((t-(S0-BPre))/(BPre+BPost)); return I[segs[k-1][0]]*(1-w)+I[segs[k][0]]*w
        if k+1<len(segs) and t>S1-BPre:
            w=sm((t-(S1-BPre))/(BPre+BPost)); return I[segs[k][0]]*(1-w)+I[segs[k+1][0]]*w
        return I[segs[k][0]]
    def env(t): return (0.35+0.65*sm(t/0.12))*(0.12+0.88*sm((dur-t)/0.22))
    N=int(dur*240)+1; g=0; rates=[]
    for i in range(N):
        t=(i+0.5)/240; g+=env(t)/inert(t)/240; rates.append((t,env(t)/inert(t)))
    L=abs(pitch)/g
    r=[(t,L*x) for t,x in rates]
    peak=max(x for _,x in r)
    # longest hold <=150
    best=cur=0
    for t,x in r:
        cur=cur+1/240 if x<=150 else 0; best=max(best,cur)
    # angle at times
    acc=0;ang={}
    for t,x in r:
        acc+=x/240
    print(f"{name}: dur {dur:.2f} L {L:.0f} peak {peak:.0f} mean {abs(pitch)/dur:.0f} hold<=150 {best:.2f}s")
    acc=0
    for t,x in r[::24]: 
        pass
    # print angle remaining at dur-0.3,-0.2,-0.1
    acc=0;out=[]
    for t,x in r:
        acc+=x/240
        for q in (0.35,0.25,0.15):
            if abs(t-(dur-q))<1/480: out.append((q,abs(pitch)-acc))
    print('   remaining deg at dur-q:',[(q,round(a)) for q,a in out])
run('backDouble',720,[('Tuck',float(sys.argv[2]) if len(sys.argv)>2 else 1.0),('Kickout',float(sys.argv[3]) if len(sys.argv)>3 else 0.7)])
run('frontPikeSwan',360,[('Pike',.30),('Pencil',.34),('Swan',.55),('Tuck',.24),('Reach',.22)])
run('corkscrew',360,[('Layout',.2),('Twist',.45),('Swan',.5),('Tuck',.26),('Reach',.22)])
run('backSingle',360,[('Tuck',.3),('Pencil',.4),('Tuck',.3),('Reach',.22)])
run('frontPikeSwan_old',360,[('Pike',.36),('Pencil',.36),('Swan',.72),('Tuck',.27),('Reach',.26)])
