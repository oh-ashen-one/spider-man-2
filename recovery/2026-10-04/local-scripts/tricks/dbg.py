import json,sys,csv
sys.path.insert(0,'tools/tricks'); import limb_sim as LS, flip_sim as FS, tricks_check as TC
R=json.load(open(sys.argv[1])); prog=sys.argv[2]; t0=float(sys.argv[3]); lo,hi=float(sys.argv[4]),float(sys.argv[5])
T=list(csv.DictReader(open(sys.argv[6] if len(sys.argv)>6 else "/Users/midir/sm2-n1/_scratch/tricks/capture/t60_trick_reel_old_pre_merge/seg1/t60_trick_reel_telemetry.csv")))
c=[c for c in TC.instances(T) if c['prog']==prog and abs(c['t0']-t0)<0.05][0]
P=FS.Prog({p['name']:p for p in FS.parse(FS.SRC)}[c['prog']],c['scale'])
for i,ft in c['rows']:
  r=T[i]
  if not lo<ft<hi: continue
  A=LS.shape_at(P,ft+0.04)
  print('%.3f pitch %7.1f tw %6.1f %-8s %s>%s W%.2f HA%.2f'%(ft,float(r['flip_pitch_deg']),float(r['flip_twist_deg']),r['flip_shape'],A[0],A[1],A[2],A[3]), 'meas',r['limb_z'], 'model',' '.join('%.3f'%LS.world_z(LS.body_pos(R,P,ft,b),float(r['flip_pitch_deg']),float(r['flip_twist_deg'])) for b in LS.ENDS))
