#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 08: one line of numbers per still (PNG or JPEG) of a sweep folder: frame mean, Y<10 %, clipped %, sky band (rows 0-89) Y / HSV saturation / B-R, far band (450,192,1350,236) Y,
sky-far, max 8-row step of the row-mean luma in rows 100-300 (L27b), rows 0-150 clipped % (L27c).  usage: quick.py <dir or files...> [--match s]"""
import glob, os, sys
import numpy as np
from PIL import Image


def stats(f):
    a = np.asarray(Image.open(f).convert('RGB')).astype(np.float32)
    if a.shape[1] != 1920: a = np.asarray(Image.open(f).convert('RGB').resize((1920, 1080), Image.BOX)).astype(np.float32)
    y = .2126 * a[..., 0] + .7152 * a[..., 1] + .0722 * a[..., 2]
    mx = a.max(2); mn = a.min(2); s = np.where(mx[:90] > 0, (mx[:90] - mn[:90]) / np.maximum(mx[:90], 1), 0)
    far = y[192:236, 450:1350].mean(); prof = y.mean(1); d = np.abs(prof[108:301] - prof[100:293])
    return dict(mean=y.mean(), lt10=(y < 10).mean() * 100, clip=(mx >= 250).mean() * 100, skyY=y[:90].mean(), sat=s.mean(), BR=a[:90, :, 2].mean() - a[:90, :, 0].mean(),
                far=far, skyfar=y[:90].mean() - far, step=d.max(), clip150=(a[:150].max(2) >= 250).mean() * 100)


def main():
    match = sys.argv[sys.argv.index('--match') + 1] if '--match' in sys.argv else ''
    args = [x for i, x in enumerate(sys.argv[1:], 1) if not x.startswith('--') and sys.argv[i - 1] != '--match']
    fs = []
    for p in args: fs += sorted(glob.glob(os.path.join(p, '*.png')) + glob.glob(os.path.join(p, '*.jpg'))) if os.path.isdir(p) else [p]
    print('%-28s %6s %6s %5s %6s %5s %6s %6s %7s %5s %5s' % ('still', 'mean', 'Y<10', 'clip', 'skyY', 'sat', 'B-R', 'far', 'sky-far', 'step', 'c150'))
    for f in fs:
        if match and match not in f: continue
        r = stats(f)
        print('%-28s %6.1f %6.1f %5.2f %6.1f %5.3f %+6.1f %6.1f %+7.1f %5.1f %5.2f' % (os.path.basename(f)[:28], r['mean'], r['lt10'], r['clip'], r['skyY'], r['sat'], r['BR'], r['far'], r['skyfar'], r['step'], r['clip150']))


if __name__ == '__main__':
    main()
