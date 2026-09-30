#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""Golden-hour key / fill contrast numbers (LOOK-SPEC L21, round 04; the line comes from the round-03 critic verdict, `critic/round-03-CRITIC.md`, "Biggest gap").
Per still (resized to 1920 px wide like every P4 instrument; luma Y = .2126 R + .7152 G + .0722 B of the 8-bit sRGB values):
  p5 Y            5th percentile of the luma, target <= 12 (refs 8..11)
  p95/p5          ratio of the 95th to the 5th percentile, target >= 16 (refs 18..26)
  sat             mean HSV saturation, (max - min) / max of the 8-bit RGB per pixel, target >= 0.44
  mean / clipped  L1 companions that must still hold: mean Y 61..100, Y < 10 <= 8 %, clipped (any channel >= 250) <= 1.8 %
  facade pair     S1 / S5 / S6: mean Y of a sunlit facade box over mean Y of a shaded facade box (facade_pairs.json, 1080p coordinates), target ratio >= 3
The p5 / p95 / saturation formulas reproduce the critic's round-03 instrument (round-03 golden S1..S8: p5 20.6 20.2 19.8 39.6 17.6 21.3 21.6 17.8, saturation .282 .405 .288 .393 .425 .366 .395 .413).
usage: key_fill_check.py [files...] [--dir D --res 1920x1080] [--pairs facade_pairs.json] [--md out.md] [--json out.json]"""
import argparse, glob, json, os, re, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PAIRS = os.path.abspath(os.path.join(HERE, '..', '..', 'docs', 'night1', 'look', 'facade_pairs.json'))
T = {'p5': 12.0, 'ratio': 16.0, 'sat': 0.44, 'mean_lo': 61.0, 'mean_hi': 100.0, 'near_black': 8.0, 'clipped': 1.8, 'pair': 3.0}

def load(path):
    im = Image.open(path).convert('RGB')
    if im.width != 1920: im = im.resize((1920, int(round(im.height * 1920 / im.width))), Image.BOX if im.width % 1920 == 0 else Image.LANCZOS)
    return np.asarray(im, dtype=np.float32)

def luma(a): return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]

def hsv_sat(a):
    mx, mn = a.max(axis=2), a.min(axis=2)
    return np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0.0)

def stats(path, pairs=None):
    a = load(path); Y = luma(a)
    p5, p95 = float(np.percentile(Y, 5)), float(np.percentile(Y, 95))
    d = {'file': os.path.basename(path), 'mean': float(Y.mean()), 'p5': p5, 'p95': p95, 'ratio': p95 / max(p5, 0.5), 'sat': float(hsv_sat(a).mean()),
         'near_black_pct': float((Y < 10).mean() * 100), 'clipped_pct': float((a.max(axis=2) >= 250).mean() * 100)}
    m = re.match(r'golden_(S\d)', d['file'])
    if m and pairs and m.group(1) in pairs:
        p = pairs[m.group(1)]; sl = luma(box(a, p['sunlit'])); sh = luma(box(a, p['shaded']))
        d['pair'] = {'sunlit_Y': float(sl.mean()), 'shaded_Y': float(sh.mean()), 'ratio': float(sl.mean() / max(sh.mean(), 0.5)), 'sunlit_p50': float(np.median(sl)), 'shaded_p50': float(np.median(sh)),
                     'note': p.get('note', '')}
    d['ok'] = {'p5': d['p5'] <= T['p5'], 'ratio': d['ratio'] >= T['ratio'], 'sat': d['sat'] >= T['sat'], 'mean': T['mean_lo'] <= d['mean'] <= T['mean_hi'],
               'near_black': d['near_black_pct'] <= T['near_black'], 'clipped': d['clipped_pct'] <= T['clipped']}
    if 'pair' in d: d['ok']['pair'] = d['pair']['ratio'] >= T['pair']
    return d

def box(a, b):
    x0, y0, x1, y1 = b; return a[y0:y1, x0:x1]

def table(rows):
    yn = lambda c: 'yes' if c else 'NO'
    L = ['| still | mean Y | p5 Y (<= 12) | p95 Y | p95/p5 (>= 16) | HSV sat (>= .44) | Y<10 % | clipped % | facade pair sunlit / shaded Y = ratio (>= 3) | passes |', '|' + '---|' * 10]
    for d in rows:
        pr = d.get('pair'); ok = d['ok']
        L.append('| %s | %.1f %s | %.1f %s | %.0f | %.1f %s | %.3f %s | %.2f | %.2f %s | %s | %d/%d |' % (
            d['file'], d['mean'], yn(ok['mean']), d['p5'], yn(ok['p5']), d['p95'], d['ratio'], yn(ok['ratio']), d['sat'], yn(ok['sat']), d['near_black_pct'], d['clipped_pct'], yn(ok['clipped']),
            ('%.0f / %.0f = %.2f %s' % (pr['sunlit_Y'], pr['shaded_Y'], pr['ratio'], yn(ok['pair']))) if pr else '-', sum(ok.values()), len(ok)))
    return L

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('files', nargs='*'); ap.add_argument('--dir'); ap.add_argument('--res', default='1920x1080'); ap.add_argument('--pairs', default=PAIRS)
    ap.add_argument('--md'); ap.add_argument('--json')
    a = ap.parse_args()
    pairs = json.load(open(a.pairs)) if os.path.exists(a.pairs) else None
    files = list(a.files) or sorted(glob.glob(os.path.join(a.dir, 'golden_S?_%s*.*' % a.res)))
    files = sorted([f for f in files if f.lower().endswith(('.jpg', '.png')) and re.match(r'golden_S\d', os.path.basename(f))], key=lambda f: os.path.basename(f))
    rows = [stats(f, pairs) for f in files]
    out = '\n'.join(table(rows)) + '\n'
    if rows:
        out += '\nGolden set: p5 <= 12 on %d / %d, p95/p5 >= 16 on %d / %d, saturation >= .44 on %d / %d, mean 61..100 on %d / %d.\n' % tuple(
            x for k in ('p5', 'ratio', 'sat', 'mean') for x in (sum(1 for d in rows if d['ok'][k]), len(rows)))
    print(out)
    if a.md: open(a.md, 'w').write(out)
    if a.json: json.dump(rows, open(a.json, 'w'), indent=1)

if __name__ == '__main__':
    main()
