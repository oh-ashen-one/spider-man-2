"""r04 hold 2 report + fallback autopick (foam CBias / BendK on river_low 4K; ChopFar / MidK on harbour_high).
usage: report_r04b.py <iter dir> <variants.json> <out auto_params.json>"""
import json, os, sys
import cv2
sys.path.insert(0, '/Users/midir/sm2-n1/water/tools/water')
import water_spec as ws
D, VJ, OUT = sys.argv[1:4]
var = json.load(open(VJ)); res = {}
for f in sorted(os.listdir(D)):
    if not f.endswith('.png') or f.startswith('DBG'): continue
    n = f[:-4]; p = os.path.join(D, f)
    if 'harbour_high' in n: r = ws.harbour(p)
    elif 'harbour_sun_high' in n: r = ws.sunhigh(p)
    else:
        r = ws.near(p); im = cv2.imread(p)
        if im.shape[1] == 3840:
            c = os.path.join(D, n + '_seawall_foam.jpg'); cv2.imwrite(c, im[1250:2160, 1500:2700]); r['foam'] = ws.foam(c)
    res[n] = r
    print('%-24s %s' % (n, json.dumps({k: v for k, v in r.items() if k not in ('file', 'crop', 'note', 'rgb')})))
fin = {}
fo = {n.split('_')[0]: r['foam'] for n, r in res.items() if 'foam' in r}
if fo:
    b = max(fo, key=lambda k: (fo[k]['rows_ge12px_pct'] >= 30) * 100 + fo[k]['band_px_mean'] - 0.0 * (k.startswith('B')))
    if b != 'base' and b in var: fin.update({k: v for k, v in var[b].items() if not k.startswith('_')})
hh = {n.split('_')[0]: r for n, r in res.items() if n.endswith('harbour_high')}
if hh:
    b = max(hh, key=lambda k: hh[k]['highpass_sd'] - hh[k]['pale_blobs_ge20px'] / 100.0)
    if b != 'base' and b in var: fin.update({k: v for k, v in var[b].items() if not k.startswith('_')})
json.dump(fin, open(OUT, 'w')); json.dump(dict(rows=res, pick=fin), open(os.path.join(D, 'report.json'), 'w'), indent=1)
print('autopick params (over the build defaults):', fin)
