import csv, json, sys, math
sys.path.insert(0, 'tools/tricks')
import flip_sim as FS, limb_sim as LS, tricks_check as TC
R = json.load(open('unreal/WebHomage/Saved/HeroFlips_report.json'))
progs = {p['name']: p for p in FS.parse(FS.SRC)}
T = list(csv.DictReader(open(sys.argv[1])))
I = TC.instances(T)
for sgn in (1, -1):
  for psg in (1, -1):
    err = []; corr = []
    for c in I:
        if c['prog'] not in progs: continue
        P = FS.Prog(progs[c['prog']], c['scale'])
        for i, ft in c['rows']:
            r = T[i]
            meas = [float(x) for x in r['limb_z'].split()]
            ph = psg * float(r['flip_pitch_deg']); tw = float(r['flip_twist_deg'])
            pred = [LS.world_z(LS.body_pos(R, P, ft, b), ph, tw, sgn) for b in LS.ENDS]
            err.extend(abs(a - b) for a, b in zip(meas, pred))
    err.sort()
    print('sgn', sgn, 'pitchsign', psg, 'median abs err %.3f p90 %.3f' % (err[len(err)//2], err[int(len(err)*.9)]))
print('--- L with measured pitch: model vs measured')
rows = [(k, r) for k, r in enumerate(T) if k % 6 == 0 and TC.f(r.get('flip_t'), -1) >= 0]
inst_of = {}
for c in I:
    for i, ft in c['rows']: inst_of[i] = c
ms = ps = 0
for (ka, a), (kb, b) in zip(rows, rows[1:]):
    if a['flip_prog'] != b['flip_prog'] or ka not in inst_of or inst_of[ka]['prog'] not in progs: continue
    c = inst_of[ka]; P = FS.Prog(progs[c['prog']], c['scale'])
    def pz(r): return [LS.world_z(LS.body_pos(R, P, float(r['flip_t']), bb), float(r['flip_pitch_deg']), float(r['flip_twist_deg'])) for bb in LS.ENDS]
    dm = max(abs(float(x) - float(y)) for x, y in zip(a['limb_z'].split(), b['limb_z'].split()))
    dp = max(abs(x - y) for x, y in zip(pz(a), pz(b)))
    if dm < 0.1 or dp < 0.1:
        print('t %.2f %-14s %-8s meas %.3f model %.3f' % (float(a['t']), a['flip_prog'], a['flip_shape'], dm, dp))
    ms += dm < 0.1; ps += dp < 0.1
print('measured slow', ms, 'model slow', ps)
