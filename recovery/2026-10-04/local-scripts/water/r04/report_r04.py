"""r04 iteration report + autopick. usage: report_r04.py <iter dir> <variants.json> <out auto_params.json>
far field (base / L1 / L3) picked on harbour_high (hp sd, pale blobs) + harbour_sun_high; glitter (base / G2) on harbour_sun_high; merged."""
import json, os, sys
import cv2
sys.path.insert(0, '/Users/midir/sm2-n1/water/tools/water')
import water_spec as ws
D, VJ, OUT = sys.argv[1:4]
sys.path.insert(0, '/Users/midir/sm2-n1/water/unreal/WebHomage/Scripts')
var = json.load(open(VJ))
P = lambda n: os.path.join(D, n + '.png')
res = {}
for f in sorted(os.listdir(D)):
    if not f.endswith('.png'): continue
    n = f[:-4]; p = P(n); r = {}
    if 'harbour_high' in n: r = ws.harbour(p)
    elif 'harbour_sun_high' in n: r = ws.sunhigh(p)
    elif 'river_sun' in n: r = ws.near(p); r.update(ws.sparkle(p))
    elif 'river_low' in n and not n.startswith('DBG'):
        r = ws.near(p)
        if cv2.imread(p).shape[1] == 3840:
            im = cv2.imread(p); c = os.path.join(D, n + '_seawall_foam.jpg'); cv2.imwrite(c, im[1250:2160, 1500:2700]); r['foam'] = ws.foam(c)
    res[n] = r
    print('%-24s %s' % (n, json.dumps({k: v for k, v in r.items() if k not in ('file', 'crop', 'note', 'rgb')})))
def hpen(n):
    h = res.get(n + '_harbour_high'); s = res.get(n + '_harbour_sun_high')
    if not h: return None
    pen = max(0, 10 - h['highpass_sd']) / 2 + h['pale_blobs_ge20px'] / 3.0
    if s: pen += max(0, 0.5 - s['glint_pct']) * 2 + max(0, 50 - s['path_cols_pct_ge2pct_rows']) / 25
    return pen
def gpen(n):
    s = res.get(n + '_harbour_sun_high')
    if not s: return None
    return max(0, 0.5 - s['glint_pct']) * 2 + max(0, 50 - s['path_cols_pct_ge2pct_rows']) / 25 + max(0, (s['sparkle_px_median'] or 99) - 6) / 3
far = {n: hpen(n) for n in ('base', 'L1', 'L3') if hpen(n) is not None}
gl = {n: gpen(n) for n in ('base', 'G2') if gpen(n) is not None}
print('far-field penalties', far, 'glitter penalties', gl)
fin = {}
if far:
    b = min(far, key=far.get)
    if b != 'base': fin.update({k: v for k, v in var[b].items() if not k.startswith('_')})
if gl:
    b = min(gl, key=gl.get)
    if b != 'base': fin.update({k: v for k, v in var[b].items() if not k.startswith('_')})
json.dump(fin, open(OUT, 'w')); json.dump(dict(rows=res, far=far, glitter=gl, pick=fin), open(os.path.join(D, 'report.json'), 'w'), indent=1)
print('autopick params (over the build defaults):', fin)
