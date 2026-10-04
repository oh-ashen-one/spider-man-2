import csv,sys,math
for p in sys.argv[1:]:
    R=list(csv.DictReader(open(p))); f=lambda r,k: float(r[k])
    fr=[];mx=0;mxt=0
    for i in range(1,len(R)):
        d=math.dist((f(R[i],'pcm_x'),f(R[i],'pcm_y'),f(R[i],'pcm_z')),(f(R[i-1],'pcm_x'),f(R[i-1],'pcm_y'),f(R[i-1],'pcm_z')))
        hd=f(R[i],'cam_hero_dist_m')
        if d<0.01 and f(R[i],'speed_mps')>8: fr.append(f(R[i],'t'))
        if hd>mx: mx=hd;mxt=f(R[i],'t')
    print(p.split('/')[-1],'frozen-camera frames (moved<1cm while hero>8 m/s):',len(fr),('%.2f..%.2f'%(fr[0],fr[-1])) if fr else '', 'max cam-hero dist %.1f m @ %.2f s'%(mx,mxt))
