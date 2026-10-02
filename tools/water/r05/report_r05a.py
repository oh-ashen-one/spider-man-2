"""r05 hold 1 report: Dbg 9 thermometer decode, river_low foam (1080p -> 4K-scale crop), harbour_high line / reflections, harbour_sun_high colour.
usage: report_r05a.py <iter dir>"""
import json, os, sys
import cv2, numpy as np
sys.path.insert(0, '/Users/midir/sm2-n1/water/tools/water')
import water_spec as ws
D = sys.argv[1]; res = {}
BANDS = [('A width', 8192), ('A height', 8192), ('A mips', 16), ('A Load @0m texel', 8), ('A SampleLevel @0m uv', 8), ('A SampleLevel @open (file 11.7 m)', 32),
         ('B width', 8192), ('B height', 8192), ('B @0m uv', 8), ('B @open (file 11.8 m)', 32), ('C height', 8192), ('C @0m uv', 8),
         ('C @open (file 11.8 m)', 32), ('ShoreDist @open', 400)]
def dbg9(p):
    Y = ws.luma(cv2.imread(p).astype(np.float32)); H, W = Y.shape; out = {}
    x0, x1 = int(0.012 * 0.48 * W) + 2, int(0.48 * W) - 1
    for k, (nm, full) in enumerate(BANDS):
        yc = int((0.54 + 0.032 * (k + 0.6)) * H); row = Y[yc - 3:yc + 4, x0:x1].mean(0)
        thr = (np.percentile(row, 2) + np.percentile(row, 98)) / 2; white = row > thr
        lo, hi = np.percentile(row, 2), np.percentile(row, 98)
        frac = float(white.mean()) if hi - lo > 20 else (1.0 if lo > 128 else 0.0)
        # the thermometer is white from x = 0 up to value/full: the first dark pixel marks the value
        dark = np.where(~white)[0]; first = (dark[0] / len(row)) if len(dark) else 1.0
        if hi - lo <= 20: first = frac
        out[nm] = dict(value=round(first * full * (x1 - x0) / (0.48 * W - 0.012 * 0.48 * W) + 0.012 * full, 2), contrast=round(float(hi - lo), 1))
    return out
for f in sorted(os.listdir(D)):
    if not f.endswith('.png'): continue
    n = f[:-4]; p = os.path.join(D, f)
    if n.startswith('DBG9'):
        r = dbg9(p)
        for g in sorted(os.listdir(os.path.join(D, n))):
            if g.endswith('.png'): r['_' + g] = dbg9(os.path.join(D, n, g))
    elif 'harbour_sun_high' in n: r = dict(sun=ws.sun_colour(p), sunhigh=ws.sunhigh(p))
    elif 'harbour_high' in n: r = dict(harbour=ws.harbour(p), under=ws.under_island(p), line=ws.harbour_line(p, ws.HARBOUR_REF))
    elif 'river_low' in n:
        r = ws.near(p); im = cv2.imread(p)
        im4 = cv2.resize(im, (3840, 2160), interpolation=cv2.INTER_CUBIC) if im.shape[1] < 3840 else im
        c = os.path.join(D, n + '_seawall_foam.jpg'); cv2.imwrite(c, im4[1250:2160, 1500:2700]); r['foam'] = ws.foam(c)
    else: continue
    res[n] = r
    print('%-24s %s' % (n, json.dumps({k: v for k, v in r.items() if k not in ('file', 'crop', 'note', 'rgb')})))
json.dump(res, open(os.path.join(D, 'report.json'), 'w'), indent=1)
