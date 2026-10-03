"""Gate-2 screening without a dolly: XOR/OR of the seawall band masks between stills of the SAME camera 0.25 s apart (the dolly's camera motion
adds change on top, so this is conservative), and gate-1 numbers of the first still.
usage: static_pairs.py <dir with <name>_NN_tTTT.png> [more dirs]   (edge line = the fit of <ref crop>, default scratch r05g/crop_foam.jpg)"""
import sys, glob, os, json, numpy as np, cv2
sys.path.insert(0, '/Users/midir/sm2-n1/water/tools/water')
import water_spec as ws
REF = os.environ.get('FOAM_REF', '/Users/midir/sm2-n1/_scratch/water/r05g/crop_foam.jpg')
A, _ = ws._wall_edge(cv2.imread(REF).astype(np.float32))
for d in sys.argv[1:]:
    fs = sorted(glob.glob(os.path.join(d, '*_t0*.png'))); prev = None; xs = []; area = []; rows = []
    for f in fs:
        fr = cv2.imread(f); s = fr.shape[1] / 3840.0; y0 = int(ws.FOAMCROP[1] * s)
        Yd = ws.luma(fr.astype(np.float32))[y0:fr.shape[0]]
        ex = (np.polyval(A, (np.arange(y0, fr.shape[0]) / s) - ws.FOAMCROP[1]) + ws.FOAMCROP[0]) * s
        Wd, Md = ws._band(Yd, ex, win=int(60 * s)); area.append(int(Md.sum())); rows.append(round(float((Wd >= 12 * s).mean() * 100), 1))
        if prev is not None:
            u = (Md | prev).sum(); xs.append(round(float((Md ^ prev).sum() / u), 3) if u else 0.0)
        prev = Md
    im = cv2.imread(fs[0]); im4 = cv2.resize(im, (3840, 2160), interpolation=cv2.INTER_CUBIC) if im.shape[1] < 3840 else im
    c = os.path.join(d, 'foam_crop.jpg'); cv2.imwrite(c, im4[1250:2160, 1500:2700]); g1 = ws.foam(c)
    print(os.path.basename(d.rstrip('/')), 'xor/or pairs', xs, 'min', min(xs) if xs else None, 'area', area, 'rows>=6px@1080 share', rows,
          '| gate1 (upscaled)', g1['band_px_mean'], g1['rows_ge12px_pct'])
