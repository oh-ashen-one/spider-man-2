#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 06: reads a lapse json of tools/perf_ue/capture_tod_lapse.py (per-frame hour / mean Y / B-R / clipped), prints the L23b numbers, the frames whose jump is over
a threshold (the rig steps) and writes a chart (mean Y and clipped % against the game hour, jumps over 3 marked) as <json>.png.
usage: lapse_report.py <lapse.json> [--thr 1.5] [--png out.png] [--cmp other.json]"""
import argparse, json, sys
from PIL import Image, ImageDraw


def load(p):
    d = json.load(open(p))
    return d, d['hours_per_frame'], d['mean_y_per_frame'], d['b_minus_r_per_frame'], d['clipped_pct_per_frame']


def chart(series, out, W=1500, H=520):
    im = Image.new('RGB', (W, H), (18, 18, 22)); dr = ImageDraw.Draw(im)
    x0, x1, y0, y1 = 60, W - 20, 20, H - 40
    def X(i, n): return x0 + (x1 - x0) * i / max(1, n - 1)
    def Yy(v, vmax=220.0): return y1 - (y1 - y0) * min(v, vmax) / vmax
    for v in range(0, 221, 20):
        dr.line([(x0, Yy(v)), (x1, Yy(v))], fill=(50, 50, 56)); dr.text((8, Yy(v) - 5), str(v), fill=(150, 150, 150))
    cols = [(90, 200, 255), (255, 170, 80), (120, 255, 140)]
    for k, (name, hrs, ys, brs, cl) in enumerate(series):
        n = len(ys)
        pts = [(X(i, n), Yy(ys[i])) for i in range(n)]
        dr.line(pts, fill=cols[k % 3], width=2)
        for i in range(1, n):
            if abs(ys[i] - ys[i - 1]) > 3.0: dr.ellipse([pts[i][0] - 4, pts[i][1] - 4, pts[i][0] + 4, pts[i][1] + 4], outline=(255, 60, 60))
        dr.text((x0 + 10 + 260 * k, 4), name, fill=cols[k % 3])
    hrs = series[0][1]; n = len(hrs)
    for h in range(0, 25, 2):
        i = min(range(n), key=lambda j: abs(((hrs[j] - h + 12) % 24) - 12))
        dr.line([(X(i, n), y1), (X(i, n), y1 + 6)], fill=(150, 150, 150)); dr.text((X(i, n) - 8, y1 + 8), '%02d' % h, fill=(150, 150, 150))
    # 130 line (L23b mean limit 05:00-21:30)
    dr.line([(x0, Yy(130)), (x1, Yy(130))], fill=(200, 80, 80))
    im.save(out)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('json'); ap.add_argument('--thr', type=float, default=1.5); ap.add_argument('--png', default=''); ap.add_argument('--cmp', default='')
    a = ap.parse_args()
    d, hrs, ys, brs, cl = load(a.json)
    print('%s: %d frames, %s' % (a.json, len(ys), d.get('instrument_condition')))
    print('L23b', json.dumps({k: v for k, v in d['checks_L23b'].items() if k != 'biggest_jumps'}))
    print('biggest jumps', d['checks_L23b']['biggest_jumps'])
    print('frames with a jump > %.1f:' % a.thr)
    run = []
    for i in range(1, len(ys)):
        dj = ys[i] - ys[i - 1]
        if abs(dj) > a.thr: run.append((hrs[i], dj, ys[i - 1], ys[i]))
    for h, dj, f, t in run: print('  %6.3f h  %+6.2f  (%.1f -> %.1f)' % (h, dj, f, t))
    print('hour  meanY  B-R  clipped%')
    for i in range(0, len(ys), 15): print('%5.2f %6.1f %5.1f %6.2f' % (hrs[i], ys[i], brs[i], cl[i]))
    series = [(a.json.split('/')[-1], hrs, ys, brs, cl)]
    if a.cmp:
        d2, h2, y2, b2, c2 = load(a.cmp); series.append((a.cmp.split('/')[-1], h2, y2, b2, c2))
    chart(series, a.png or a.json.replace('.json', '.png'))


if __name__ == '__main__':
    main()
