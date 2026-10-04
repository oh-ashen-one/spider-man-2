import csv, sys, math
n=sys.argv[1]; thr=float(sys.argv[2]); kmin=float(sys.argv[3]) if len(sys.argv)>3 else 0.0
R=list(csv.DictReader(open('/Users/midir/sm2-n1/_scratch/traversal/r16/probe/%s/probe_telemetry.csv'%n)))
for i in range(len(R)-1):
    for k in ('pcm_pitch','pcm_yaw','pcm_x','pcm_y','pcm_z'): R[i][k]=R[i+1][k]
def wrap(a): return (a+180)%360-180
cnt=0
for i,r in enumerate(R[:-1]):
    if i==0: continue
    yr=abs(wrap(float(r['pcm_yaw'])-float(R[i-1]['pcm_yaw'])))*60
    k=float(r['flipcam_k'])
    if yr>thr and k>=kmin and cnt<int(sys.argv[4]) if len(sys.argv)>4 else yr>thr and k>=kmin:
        cnt+=1
        print(r['t'],r['mode'],r['sub'],r['flip_prog'],'ft',r['flip_t'],'k',r['flipcam_k'],'yaw %.1f rate %.0f'%(float(r['pcm_yaw']),yr),'slew',r['cam_slew'],'dist',r['cam_hero_dist_m'],'fd',r['flipcam_dist_m'],'pit',r['pcm_pitch'],'vx/vy',r['vx'],r['vy'],'chain',r['chain'])
