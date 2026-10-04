"""r05b hold D report: per still, the round-05 instruments. usage: report_r05d.py <stills dir> [out.json]
DBG10* : decode of the Dbg 10 columns through the calibration ramp (bottom 6 pct of the frame)
*harbour_high* : harbour crop, under-island, island-seawall contact line; *river_low* : near crop, seawall foam gate, far-shore bar;
*river_sun* : near crop + sparkle width"""
import json, os, sys
import cv2, numpy as np
sys.path.insert(0, '/Users/midir/sm2-n1/water/tools/water')
import water_spec as ws, farshore
D = sys.argv[1]; res = {}
COLS = ['contact_dist/32m', 'foot/8m', 'far_cov(recomputed)', 'real_wf', 'nearW', 'dist/2000m', 'real_cf', 'real_dbgC/4m']
def dbg10(p, roi):
    Y = ws.luma(cv2.imread(p).astype(np.float32)); H, W = Y.shape
    ramp = Y[int(0.95 * H):int(0.99 * H)].mean(0)                       # luma along x of the calibration ramp (value = x / W)
    xs = np.arange(W) / W
    # make the ramp monotonic for the inverse lookup
    mono = np.maximum.accumulate(cv2.GaussianBlur(ramp.reshape(1, -1), (0, 0), 6).ravel())
    inv = lambda y: float(np.interp(y, mono, xs))
    sc = W / 3840.0
    y0, y1, x0, x1 = roi; out = {}
    cols = np.arange(int(x0 * sc), int(x1 * sc)); cls = (np.floor(cols / (24.0 * sc * 0 + 24.0)) % 8).astype(int)   # SvPosition.x / 24 (pixels of THIS frame)
    for k, nm in enumerate(COLS):
        sel = cols[cls == k]
        if not len(sel): continue
        v = Y[int(y0 * sc):int(y1 * sc)][:, sel]
        out[nm] = dict(luma_mean=round(float(v.mean()), 1), value=round(inv(float(v.mean())), 3), p90_value=round(inv(float(np.percentile(v, 90))), 3))
    out['_ramp_luma_at_0_.25_.5_.75_1'] = [round(float(ramp[int(f * (W - 1))]), 1) for f in (0, .25, .5, .75, 1)]
    return out
for f in sorted(os.listdir(D)):
    if not f.endswith('.png'): continue
    n = f[:-4]; p = os.path.join(D, f)
    if n.startswith('DBG10'):
        r = dbg10(p, (880, 960, 1250, 2300)) if 'harbour' in n else dbg10(p, (1300, 1700, 1500, 2000))
    elif 'harbour_high' in n: r = dict(harbour=ws.harbour(p), under=ws.under_island(p), line=ws.harbour_line(p, ws.HARBOUR_REF))
    elif 'river_low' in n:
        r = ws.near(p); r.update(farshore.score(p)); im = cv2.imread(p)
        im4 = cv2.resize(im, (3840, 2160), interpolation=cv2.INTER_CUBIC) if im.shape[1] < 3840 else im
        c = os.path.join(D, n + '_seawall_foam.jpg'); cv2.imwrite(c, im4[1250:2160, 1500:2700]); r['foam'] = ws.foam(c)
    elif 'river_sun' in n: r = ws.near(p); r.update(ws.sparkle(p))
    else: continue
    res[n] = r
    print('%-24s %s' % (n, json.dumps({k: v for k, v in r.items() if k not in ('file', 'crop', 'note', 'rgb', 'src_width')})))
json.dump(res, open(sys.argv[2] if len(sys.argv) > 2 else os.path.join(D, 'report.json'), 'w'), indent=1)
