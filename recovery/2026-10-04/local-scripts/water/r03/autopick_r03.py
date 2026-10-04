"""r03 autopick: score base + variants on the 1080p iteration stills against the r03 targets (1080 -> 4K high-pass factor 1.45, measured r02).
usage: autopick_r03.py <iter dir> <variants.json> <out final_params.json>"""
import json, os, sys
sys.path.insert(0, '/Users/midir/sm2-n1/water/tools/water')
import water_spec as ws
D, VJ, OUT = sys.argv[1:4]
base = json.load(open('/Users/midir/sm2-n1/_scratch/water/r03/base_params.json'))
var = json.load(open(VJ))
cands = {'base': {}}; cands.update({k: {p: v for p, v in d.items() if not p.startswith('_')} for k, d in var.items()})
HPF = 1.45
rows = {}
for name in cands:
    f = lambda v: os.path.join(D, '%s_%s.png' % (name, v))
    if not all(os.path.exists(f(v)) for v in ('river_low', 'river_sun', 'harbour_high')): continue
    rl = ws.near(f('river_low')); rs = ws.near(f('river_sun')); rs.update(ws.sparkle(f('river_sun'))); hb = ws.harbour(f('harbour_high'))
    pen = 0.0
    def short(v, tgt, sc, hi=False):
        return max(0.0, (v - tgt) / sc) if hi else max(0.0, (tgt - v) / sc)
    pen += short(rl['highpass_sd'] * HPF, 12, 4) + short(rl['p99_5'], 150, 20) + short(rl['glint_pct_ge140'], 1, 1) + short(rl['mean_Y'], 80, 8, True) + short(rl['p1'], 25, 15, True)
    pen += short(rs['sparkle_width_pct'], 50, 15) + short(rs['mean_Y'], 90, 15, True) + short(rs['glint_pct_ge140'], 3, 3) + short(rs['glint_pct_ge140'], 15, 10, True)
    pen += short(hb['highpass_sd'] * HPF, 10, 4) + short(hb['glint_pct_ge140'], 2, 2) + hb['pale_blobs_ge20px'] / 10.0
    rows[name] = dict(penalty=round(pen, 2), river_low=rl, river_sun=rs, harbour=hb)
    print('%-5s pen %.2f | rl mean %.1f p1 %.1f p99.5 %.1f hp %.2f (x1.45 %.1f) gl %.2f | rs mean %.1f gl %.1f spk %.1f | hb hp %.2f gl %.2f blobs %d'
          % (name, pen, rl['mean_Y'], rl['p1'], rl['p99_5'], rl['highpass_sd'], rl['highpass_sd'] * HPF, rl['glint_pct_ge140'], rs['mean_Y'], rs['glint_pct_ge140'],
             rs['sparkle_width_pct'], hb['highpass_sd'], hb['glint_pct_ge140'], hb['pale_blobs_ge20px']))
if not rows: sys.exit(1)
best = min(rows, key=lambda k: rows[k]['penalty'])
fin = dict(base); fin.update(cands[best])
json.dump(fin, open(OUT, 'w'))
json.dump(dict(pick=best, rows=rows), open(os.path.join(D, 'autopick.json'), 'w'), indent=1)
print('pick', best, fin)
