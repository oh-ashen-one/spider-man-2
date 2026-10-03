"""per-pair XOR/OR of the seawall band masks of river_low_dolly.mp4 at 4 fps (gate 2) with the band area and row share per sample.
usage: dolly_pairs.py <crop_river_low_4k_seawall_foam.jpg> <river_low_dolly.mp4>"""
import sys, numpy as np, cv2
sys.path.insert(0, '/Users/midir/sm2-n1/water/tools/water')
import water_spec as ws
im = cv2.imread(sys.argv[1]).astype(np.float32); A, Y = ws._wall_edge(im)
cap = cv2.VideoCapture(sys.argv[2]); fps = cap.get(cv2.CAP_PROP_FPS) or 60; step = int(round(fps / 4)); n = 0; prev = None; out = []
while True:
    ok, fr = cap.read()
    if not ok: break
    n += 1
    if (n - 1) % step: continue
    s = fr.shape[1] / 3840.0; y0 = int(ws.FOAMCROP[1] * s)
    Yd = ws.luma(fr.astype(np.float32))[y0:fr.shape[0]]
    ex = (np.polyval(A, (np.arange(y0, fr.shape[0]) / s) - ws.FOAMCROP[1]) + ws.FOAMCROP[0]) * s
    Wd, Md = ws._band(Yd, ex, win=int(60 * s))
    if prev is not None:
        u = (Md | prev).sum(); out.append((n, round(float((Md ^ prev).sum() / u), 3) if u else 0.0, int(Md.sum()), round(float((Wd >= 12 * s).mean() * 100), 1)))
    prev = Md
for o in out: print(o)
x = [o[1] for o in out]; print('pairs', len(x), 'min', min(x), 'mean', round(float(np.mean(x)), 3))
