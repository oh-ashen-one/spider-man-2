"""r05 hold 2 autopick (no wait): SunTilt = the smallest tilt whose harbour_sun_high 1080 still has crop R-B <= 66 and p1 <= 52 and glints
>= 0.5 %; else the one with the lowest R-B among those with glints >= 0.5 %. FarPx = the smallest with >= 55 % seawall columns >= 3 px (1080 upscaled).
usage: autopick.py <iter dir> <out final_params.json>"""
import json, os, sys
sys.path.insert(0, '/Users/midir/sm2-n1/water/tools/water')
import water_spec as ws
D, OUT = sys.argv[1:3]
T = {'T0': 0.0, 'T10': 0.1, 'base': 0.2, 'T35': 0.35}; F = {'FP2': 2.5, 'base': 4.0, 'FP7': 7.0}
rep, fin = {}, {}
for k, v in T.items():
    p = os.path.join(D, '%s_harbour_sun_high.png' % k)
    if os.path.exists(p): c = ws.sun_colour(p); h = ws.sunhigh(p); rep[k + '_sun'] = dict(tilt=v, crop=c['crop'], upper=c['upper'], glint=h['glint_pct'], cols=h['path_cols_pct_ge2pct_rows'], spark=h['sparkle_px_median'])
for k, v in F.items():
    p = os.path.join(D, '%s_harbour_high.png' % k)
    if os.path.exists(p): rep[k + '_hh'] = dict(farpx=v, line=ws.harbour_line(p, ws.HARBOUR_REF)['cols_ge3px_pct'], hp=ws.harbour(p)['highpass_sd'], under=ws.under_island(p))
sun = sorted([r for k, r in rep.items() if k.endswith('_sun')], key=lambda r: r['tilt'])
ok = [r for r in sun if r['crop']['R_minus_B'] <= 66 and r['crop']['p1'] <= 52 and r['glint'] >= 0.5 and r['cols'] >= 50]
g = [r for r in sun if r['glint'] >= 0.5] or sun
if ok: fin['SunTilt'] = ok[0]['tilt']
elif g: fin['SunTilt'] = min(g, key=lambda r: r['crop']['R_minus_B'])['tilt']
hh = sorted([r for k, r in rep.items() if k.endswith('_hh')], key=lambda r: r['farpx'])
okf = [r for r in hh if (r['line'] or 0) >= 55]
if okf: fin['FarPx'] = okf[0]['farpx']
elif hh: fin['FarPx'] = max(hh, key=lambda r: r['line'] or 0)['farpx']
for k, r in rep.items(): print(k, json.dumps(r))
print('autopick', fin)
json.dump(fin, open(OUT, 'w')); json.dump(dict(rows=rep, pick=fin), open(os.path.join(D, 'autopick.json'), 'w'), indent=1)
