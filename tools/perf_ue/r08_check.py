#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 08: the round-07 critic's "Biggest gap" lines on tod_<pose>_<res>_<variant>.jpg stills (1920x1080, luma Y = .2126 R + .7152 G + .0722 B of the 8-bit sRGB values).
  L5  (S4e 07:00, S4e 07:30, S4w 19:00): frame mean 59..118, Y<10 <= 8.8 %, clipped (any channel >= 250) <= 0.7 %
  SAT (same stills): sky rows 0-89 mean HSV saturation (max-min)/max per pixel >= 0.40
  BH  S4 20:30: sky rows 0-89 B-R >= 0
  DISK S4w 19:30..20:30: sub-horizon disk = connected blob of pixels with Y >= 120 and Y - median(41x41) >= 30 in rows 200..700 (below the sky line of the perch pose),
       area >= 200 px (a 16 px disk), compact (bbox aspect .5..2, ellipse fill >= .5) and not touching row 200; reported: blob count, largest equivalent diameter, peak Y. Zero blobs passes.
usage: r08_check.py --dir <stills> [--out <base>] [--prefix <variant prefix>]"""
import argparse, glob, json, os, re
import numpy as np
from PIL import Image
from scipy import ndimage

L5_STILLS = [('S4e', 7.0), ('S4e', 7.5), ('S4w', 19.0)]
DISK_STILLS = [('S4w', 19.5), ('S4w', 19.8), ('S4w', 20.0), ('S4w', 20.5)]


def load(p):
    im = Image.open(p).convert('RGB')
    if im.size[0] != 1920: im = im.resize((1920, 1080), Image.BOX)
    return np.asarray(im, dtype=np.float32)


def Y(im): return 0.2126 * im[..., 0] + 0.7152 * im[..., 1] + 0.0722 * im[..., 2]


def l5(im):
    y = Y(im); mx = im.max(axis=2); mn = im.min(axis=2)
    sky = slice(0, 90)
    sat = np.where(mx[sky] > 0, (mx[sky] - mn[sky]) / np.maximum(mx[sky], 1e-6), 0.0)
    r = {'mean': float(y.mean()), 'y_lt10_pct': float((y < 10).mean() * 100), 'clip_pct': float((mx >= 250).mean() * 100),
         'sky_sat': float(sat.mean()), 'sky_BR': float(im[sky, :, 2].mean() - im[sky, :, 0].mean()), 'sky_Y': float(y[sky].mean())}
    r['L5'] = bool(59 <= r['mean'] <= 118 and r['y_lt10_pct'] <= 8.8 and r['clip_pct'] <= 0.7)
    r['SAT'] = bool(r['sky_sat'] >= 0.40)
    return r


def disk(im):
    y = Y(im)
    band = y[200:700]
    small = band.reshape(125, 4, 480, 4).mean(axis=(1, 3))   # median over ~41x41 px computed at 1/4 resolution (speed)
    med = np.kron(ndimage.median_filter(small, size=11), np.ones((4, 4), np.float32))
    m = (band >= 120) & (band - med >= 30)
    lab, n = ndimage.label(m)
    blobs = []
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        if len(ys) < 200: continue
        # a disk is compact and lies inside the band: blobs that touch the band's top row (sky patches between towers where the skyline dips to row 200),
        # elongated ones (bbox aspect outside .5..2) or sparse ones (fill of the bbox ellipse < .5) are not disks
        h, w = ys.max() - ys.min() + 1, xs.max() - xs.min() + 1
        if ys.min() == 0 or not (0.5 <= w / h <= 2.0) or len(ys) / (np.pi / 4 * w * h) < 0.5: continue
        blobs.append({'area': int(len(ys)), 'diam': float(2 * np.sqrt(len(ys) / np.pi)), 'x': float(xs.mean()), 'y': float(ys.mean() + 200), 'peak': float(band[ys, xs].max())})
    blobs.sort(key=lambda b: -b['area'])
    # the round-07 disk position (the fill.W glint on the river, centre ~(1404, 387)): peak luma and its excess over the local median in a 130x120 box
    bx = y[330:450, 1340:1470]; bm = med[130:250, 1340:1470]
    return {'blobs': len(blobs), 'largest': blobs[0] if blobs else None, 'band_peak_Y': float(band.max()), 'DISK': not blobs,
            'r07_box_peak_Y': float(bx.max()), 'r07_box_peak_over_median': float((bx - bm).max())}


def find(d, pose, hour, prefix):
    for f in glob.glob(os.path.join(d, 'tod_%s_1920x1080_%sh*.jpg' % (pose, prefix))):
        m = re.search(r'_%sh(\d+(?:\.\d+)?)\.jpg$' % re.escape(prefix), f)
        if m and abs(float(m.group(1)) - hour) < 1e-3: return f
    return None


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--dir', required=True); ap.add_argument('--out', default=''); ap.add_argument('--prefix', default='')
    a = ap.parse_args()
    res = {'L5': {}, 'DISK': {}, 'BH': None}
    for pose, h in L5_STILLS:
        f = find(a.dir, pose, h, a.prefix)
        if f: res['L5']['%s_%g' % (pose, h)] = dict(l5(load(f)), file=os.path.basename(f))
    for pose, h in DISK_STILLS:
        f = find(a.dir, pose, h, a.prefix)
        if f: res['DISK']['%s_%g' % (pose, h)] = dict(disk(load(f)), file=os.path.basename(f))
    f = find(a.dir, 'S4', 20.5, a.prefix)
    if f:
        r = l5(load(f)); res['BH'] = {'sky_BR': r['sky_BR'], 'sky_Y': r['sky_Y'], 'sky_sat': r['sky_sat'], 'BH': bool(r['sky_BR'] >= 0), 'file': os.path.basename(f)}
    L = ['| still | mean (59..118) | Y<10 % (<= 8.8) | clipped % (<= 0.7) | L5 | sky sat (>= .40) | SAT | sky B-R | sky Y |', '|---|---|---|---|---|---|---|---|---|']
    ok = lambda b: 'ok' if b else 'FAIL'
    for k, r in res['L5'].items():
        L.append('| %s | %.1f | %.2f | %.3f | %s | %.3f | %s | %+.1f | %.1f |' % (k, r['mean'], r['y_lt10_pct'], r['clip_pct'], ok(r['L5']), r['sky_sat'], ok(r['SAT']), r['sky_BR'], r['sky_Y']))
    if res['BH']: L += ['', 'Blue hour S4 20:30 sky B-R %+.1f (>= 0: %s), sky Y %.1f, sky sat %.3f' % (res['BH']['sky_BR'], ok(res['BH']['BH']), res['BH']['sky_Y'], res['BH']['sky_sat'])]
    L += ['', '| still | sub-horizon blobs | largest diam px | at (x, y) | peak Y | band peak Y | round-07 disk box: peak Y / over local median | zero disk |', '|---|---|---|---|---|---|---|---|']
    for k, r in res['DISK'].items():
        b = r['largest']
        L.append('| %s | %d | %s | %s | %s | %.0f | %.0f / %+.0f | %s |' % (k, r['blobs'], '%.1f' % b['diam'] if b else '-', '(%.0f, %.0f)' % (b['x'], b['y']) if b else '-', '%.0f' % b['peak'] if b else '-', r['band_peak_Y'],
                                                        r['r07_box_peak_Y'], r['r07_box_peak_over_median'], ok(r['DISK'])))
    txt = '\n'.join(L); print(txt)
    if a.out:
        json.dump(res, open(a.out + '.json', 'w'), indent=1); open(a.out + '.md', 'w').write(txt + '\n')


if __name__ == '__main__':
    main()
