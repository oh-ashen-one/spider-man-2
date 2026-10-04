import csv,sys,math
sys.path.insert(0,'/Users/midir/sm2-n1/tricks/tools/tricks')
import tricks_check as TC
d=sys.argv[1]
T=list(csv.DictReader(open(d+'/probe_telemetry.csv'))); Pz=list(csv.DictReader(open(d+'/probe_pose.csv')))
f=TC.f
key=lambda r:(round(f(r['x_m']),2),round(f(r['y_m']),2),round(f(r['z_m']),2))
PI={}
for r in Pz: PI.setdefault(key(r),r)
J=[PI.get(key(r)) for r in T]
I=TC.instances(T)
for c in I:
    e=c['rows'][-1][0]; j=J[e]; n=T[e+1] if e+1<len(T) else T[e]
    pa=(f(j['catch_ax']),f(j['catch_ay']),f(j['catch_az']))
    aa=(f(n['anchor_x']),f(n['anchor_y']),f(n['anchor_z']))
    dist=math.dist(pa,aa) if n['mode']=='swing' else float('nan')
    # chest rotation in 0.1s windows
    ws=[]
    for k in range(e-3,e+25):
        if k+6<len(T) and J[k] and J[k+6]: ws.append(round(TC.rot_deg(TC.chest_frame(J[k]),TC.chest_frame(J[k+6]))/0.1))
    print(f"{c['prog']:16s} end {f(T[e]['t']):6.2f} ft {c['rows'][-1][1]:.3f} catch_on {j['catch_on']} w {j['catch_w']} pred {'swing' if j['catch_swing']=='1' else 'air  '} next {n['mode']:5s} anchor err {dist:6.1f}  beta {j['catch_beta']:>6s} gam {j['catch_gamma']:>6s} rho {j['catch_rho']:>6s} | {ws[::3]}")
