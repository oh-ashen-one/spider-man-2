import math
I={'Tuck':1.0,'Pike':1.35,'Layout':3.2,'Swan':7.5,'Pencil':9.0,'Straddle':6.0,'Throne':9.0,'Twist':3.5,'Reach':7.0}
P={'backDouble':(-720,[('Tuck',.28),('Pencil',.62),('Tuck',.28),('Layout',.14),('Tuck',.28),('Straddle',.36),('Tuck',.22),('Throne',.32),('Reach',.22)]),
'frontPikeSwan':(360,[('Pike',.34),('Pencil',.36),('Swan',.72),('Tuck',.24),('Reach',.26)]),
'corkscrew':(360,[('Layout',.22),('Twist',.5),('Swan',.6),('Tuck',.26),('Reach',.24)]),
'backSingle':(-360,[('Tuck',.28),('Pencil',.46),('Tuck',.28),('Reach',.24)]),
'wallFront':(360,[('Tuck',.24),('Layout',.3),('Tuck',.24),('Throne',.34)])}
sm=lambda x:(lambda y:y*y*(3-2*y))(min(1,max(0,x)))
BP,BQ=.05,.09
def shape(segs,t):
    D=sum(d for _,d in segs); t=min(max(t,0),D-1e-4); acc=0
    for k,(s,d) in enumerate(segs):
        if t<acc+d: break
        acc+=d
    s0,s1=acc,acc+segs[k][1]
    if k>0 and t<s0+BQ: return segs[k-1][0],segs[k][0],sm((t-(s0-BP))/(BP+BQ))
    if k+1<len(segs) and t>s1-BP: return segs[k][0],segs[k+1][0],sm((t-(s1-BP))/(BP+BQ))
    return segs[k][0],segs[k][0],0
def env(t,D): return (0.35+0.65*sm(t/.12))*(0.12+0.88*sm((D-t)/.22))
for n,(pt,segs) in P.items():
    D=sum(d for _,d in segs); H=240; g=[0]; 
    for i in range(1,int(math.ceil(D*H))+2):
        tm=(i-.5)/H; a,b,w=shape(segs,tm); g.append(g[-1]+env(tm,D)/(I[a]*(1-w)+I[b]*w)/H)
    L=pt/g[int(math.ceil(D*H))]
    print(n,'dur %.2f L %.0f'%(D,L))
    acc=0; out=[]
    for s,d in segs:
        ang0=g[int(acc*H)]*L; ang1=g[int((acc+d)*H)]*L
        out.append('%s %.2f-%.2f %4.0f->%4.0f (%3.0f deg/s)'%(s,acc,acc+d,ang0,ang1,(ang1-ang0)/d)); acc+=d
    print('\n'.join('   '+o for o in out))
