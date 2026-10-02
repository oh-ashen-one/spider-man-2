# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""Round 16 instrument (critic r15: "the Cinder centre seam zig-zags ~60 px"): track the face centre seam cord on a 4K headfront still and measure its lateral deviation.

The seam is a light raised cord on the hood midline.  Per row (top of the hood -> chin) the tracker takes the brightest ridge (luma minus a 25 px median background) inside +-W px of
the previous row's column (seeded at the top of the head by the strongest ridge near the head's centre column), skipping the lens / brow-pipe rows where no ridge is found.
Outputs per still: the column per row, `dev100` = max |x(y + 100) - x(y)| over the tracked rows (gate <= 10 px), `resid` = max |x - straight line fit|, an overlay crop.
usage: python3 seam_track_r16.py <stills dir> <out.json> [--png DIR] [--suits a,b]"""
import json, sys, os
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import median_filter, uniform_filter1d

SUITS = ['tessera', 'verdant', 'plum', 'cinder', 'glacier', 'ash', 'saffron', 'sage']


def luma(a):
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


def head_box(L, rgb):
    """the hood: the darkest big blob in the upper middle of the frame (rows where the background is sky / floor): use the column profile of 'not background'"""
    H, W = L.shape
    bg_top = np.median(rgb[5:40, :, :].reshape(-1, 3), axis=0)
    d = np.linalg.norm(rgb - bg_top[None, None], axis=-1)
    return d


def track(path, png=None, tag=''):
    rgb = np.asarray(Image.open(path).convert('RGB')).astype(np.float32)
    L = luma(rgb)
    H, W = L.shape
    # the cord is ~30 px wide and light (luma ~200 on a 50 - 130 hood): a 25 px box filter across, then per row the brightest column near the previous one
    B = uniform_filter1d(L, 15, axis=1)
    cx = W // 2
    xs = {}
    x = None; miss = 0
    for y in range(60, H - 40):
        if x is None:
            seg = B[y, cx - 400:cx + 400]; j = int(np.argmax(seg)) + cx - 400
            rid = B[y, j] - 0.5 * (B[y, j - 32] + B[y, j + 32])
            if rid > 25 and np.std(L[y, j - 200:j - 40]) < 25 and np.std(L[y, j + 40:j + 200]) < 25: x = float(j); xs[y] = x
            continue
        lo, hi = int(x) - 24, int(x) + 25
        seg = B[y, lo:hi]; j = int(np.argmax(seg)) + lo
        wide = B[y, lo - 90:hi + 90]
        bg = np.percentile(wide, 30)
        # a ridge: the peak beats the 30th percentile of +-115 px by 45 luma and both sides 40 px away by 30 (a horizontal pipe / lens rim lifts the whole row)
        ok = B[y, j] - B[y, j - 34] > 12 and B[y, j] - B[y, j + 34] > 12
        if ok and abs(j - x) <= 6 + miss // 4:
            # sub-pixel: centroid of L above the half-max inside +-16 px
            seg2 = L[y, j - 16:j + 17]; t = seg2 - (seg2.max() + bg) / 2; t = np.clip(t, 0, None)
            xc = j - 16 + float((t * np.arange(33)).sum() / max(t.sum(), 1e-6))
            xs[y] = xc; x = xc; miss = 0
        else:
            miss += 1
            if miss > 250: break
    ys = np.array(sorted(xs)); xv = np.array([xs[k] for k in ys])
    if len(ys) < 300: return dict(ok=False, why='short track %d' % len(ys))
    # smooth 9 rows (stitch noise), then the 100 px lateral step
    xsm = uniform_filter1d(xv, 9)
    dev = []
    lookup = dict(zip(ys.tolist(), xsm.tolist()))
    for yy, xx in zip(ys, xsm):
        if (yy + 100) in lookup: dev.append((abs(lookup[yy + 100] - xx), int(yy)))
    d100 = max(dev) if dev else (None, None)
    A = np.vstack([ys, np.ones_like(ys)]).T
    co, *_ = np.linalg.lstsq(A, xsm, rcond=None)
    res = xsm - A @ co
    out = dict(ok=True, y_top=int(ys[0]), y_bot=int(ys[-1]), n_rows=int(len(ys)), dev100=round(float(d100[0]), 1), dev100_at_y=d100[1],
               resid_max=round(float(np.abs(res).max()), 1), slope=round(float(co[0]), 4), range_x=round(float(xsm.max() - xsm.min()), 1),
               cols=[[int(a), round(float(b), 1)] for a, b in zip(ys[::20], xsm[::20])])
    if png:
        im = Image.open(path).convert('RGB')
        dr = ImageDraw.Draw(im)
        for a, b in zip(ys, xsm): dr.point((b + 25, a), fill=(255, 0, 255))
        x0c = int(xsm.mean())
        im.crop((max(0, x0c - 700), max(0, ys[0] - 60), min(W, x0c + 700), min(H, ys[-1] + 60))).resize((700, int(700 * (ys[-1] - ys[0] + 120) / 1400))).save(os.path.join(png, 'seam_%s.jpg' % tag), quality=88)
    return out


def main():
    d, outp = sys.argv[1], sys.argv[2]
    png = sys.argv[sys.argv.index('--png') + 1] if '--png' in sys.argv else None
    suits = sys.argv[sys.argv.index('--suits') + 1].split(',') if '--suits' in sys.argv else SUITS
    if png: os.makedirs(png, exist_ok=True)
    res = {}
    for s in suits:
        p = os.path.join(d, 'skin_%s_headfront_4k.png' % s)
        if not os.path.exists(p): p = p.replace('.png', '.jpg')
        res[s] = track(p, png, s)
        r = res[s]
        print(s, 'dev100 %s at y %s  resid %s  range %s rows %s' % (r.get('dev100'), r.get('dev100_at_y'), r.get('resid_max'), r.get('range_x'), r.get('n_rows')) if r['ok'] else r)
    res['gate_dev100_le_10'] = all(res[s].get('ok') and res[s]['dev100'] <= 10 for s in suits)
    json.dump(res, open(outp, 'w'), indent=1)
    print('GATE dev100 <= 10 on all:', res['gate_dev100_le_10'])


if __name__ == '__main__':
    main()
