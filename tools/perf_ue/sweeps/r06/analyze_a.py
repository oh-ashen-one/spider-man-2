#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 06 hold 6 (A) analysis (CPU only): compares the twilight variants W1 / W3 / W4 with the committed hold-4 table (the round-06 stills) at the L24 hours, prints the night variant N1 (moon, hero-box
clip, highlight roll-off), the dawn mist (L26) and the golden black-lift variants (Y<10, p5), and the lapse diagnostics D0 / D2.
usage: analyze_a.py --sweep <sweep_e dir> --base <round-06/stills dir> [--diag <diag6 dir>]"""
import argparse, glob, json, os, re, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PU = os.path.dirname(HERE)
sys.path.insert(0, os.path.dirname(PU) if False else os.path.join(HERE, '..', '..'))
import twilight_check as TC   # noqa: E402


def stats(p):
    a = np.asarray(Image.open(p).convert('RGB'), dtype=np.float32)
    y = TC.Y(a)
    return {'mean': float(y.mean()), 'clip': float((a.max(axis=2) >= 250).mean() * 100), 'BR': float(a[..., 2].mean() - a[..., 0].mean()), 'sky': TC.band(a), 'far': TC.far_band(a),
            'p5': float(np.percentile(y, 5)), 'lt10': float((y < 10).mean() * 100)}


def find(d, pose, var):
    f = os.path.join(d, 'tod_%s_1920x1080_%s.jpg' % (pose, var))
    return f if os.path.exists(f) else None


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--sweep', required=True); ap.add_argument('--base', required=True); ap.add_argument('--diag', default='')
    a = ap.parse_args()
    print('## twilight variants: sky band Y / B-R, far Y (S4), clipped %, frame mean; L24a = sky Y > far Y (S4), L24b = sun-facing B-R <= -20')
    hours = {'S4': [6.5, 7, 7.5, 19, 19.5, 20, 20.5, 21], 'S4e': [6.5, 7, 7.5], 'S4w': [19, 19.5, 20, 20.5]}
    for pose in ('S4', 'S4e', 'S4w'):
        print('\n### %s' % pose)
        print('| hour | base | W1 | W3 | W4 |'); print('|---|---|---|---|---|')
        for h in hours[pose]:
            cells = []
            for v in ('base', 'W1', 'W3', 'W4'):
                f = find(a.base, pose, 'h%g' % h) if v == 'base' else find(a.sweep, pose, '%s_h%g' % (v, h))
                if not f: cells.append('-'); continue
                s = stats(f)
                ok = ''
                if pose == 'S4': ok = ' a%s' % ('ok' if s['sky']['Y'] > s['far']['Y'] else 'FAIL')
                else:
                    need = (6.5 <= h <= 7.5) if pose == 'S4e' else (19.0 <= h <= 20.5)
                    ok = (' b%s' % ('ok' if s['sky']['BR'] <= -20 else 'FAIL')) if need else ''
                cells.append('sky %.0f/%+.0f far %.0f mean %.0f clip %.1f%%%s' % (s['sky']['Y'], s['sky']['BR'], s['far']['Y'], s['mean'], s['clip'], ok))
            print('| %g | %s |' % (h, ' | '.join(cells)))
    print('\n## night N1 (22:00) vs base')
    for pose in ('S4m', 'S4', 'S1', 'S6', 'S5', 'S7'):
        for v, d, var in (('base', a.base, 'h22'), ('N1', a.sweep, 'N1_h22')):
            f = find(d, pose, var)
            if not f: continue
            s = stats(f); extra = ''
            if pose == 'S4m':
                im = TC.load(f); m = TC.moon_disk(im, 'S4m', 22.0); y = TC.Y(im); box = np.zeros(y.shape, bool); box[:250] = True
                yy, xx = np.mgrid[:y.shape[0], :y.shape[1]]; mp = m.get('predicted_px'); ex = box & (((xx - mp[0]) ** 2 + (yy - mp[1]) ** 2) > 70 ** 2) if mp else box
                extra = ' moon %.1f px peak %.0f hp(excl) %.2f' % (m.get('disk_diameter_px', 0), m.get('peak_Y', 0), TC.hp_std(y, ex))
            print('%-4s %-4s mean %.1f clip %.2f%% B-R %+.1f%s' % (v, pose, s['mean'], s['clip'], s['BR'], extra))
    print('\n## dawn mist 07:36 (L26 S1 correlation vs golden 18:24 <= 0.6)')
    g = find(a.base, 'S1', 'h18.4')
    gl = TC.Y(np.asarray(Image.open(g).convert('RGB').resize((480, 270), Image.BOX), dtype=np.float32)) if g else None
    for v, d, var in (('base mist', a.base, 'mist_h7.6'), ('N1 mist', a.sweep, 'N1_mist_h7.6')):
        f = find(d, 'S1', var)
        if f and gl is not None:
            l = TC.Y(np.asarray(Image.open(f).convert('RGB').resize((480, 270), Image.BOX), dtype=np.float32)); print('%-10s corr %.3f' % (v, float(np.corrcoef(l.ravel(), gl.ravel())[0, 1])))
    print('\n## golden 18:24 black lift: Y<10 % / p5 / mean per pose (spec: Y<10 <= 8 %, p5 <= 12, mean 61..100)')
    print('| pose | base | G1 (.0012) | G2 (.0022) |'); print('|---|---|---|---|')
    for pose in ['S%d' % i for i in range(1, 9)]:
        cells = []
        for var, d in (('h18.4', a.base), ('G1_h18.4', a.sweep), ('G2_h18.4', a.sweep)):
            f = find(d, pose, var)
            if not f: cells.append('-'); continue
            s = stats(f); cells.append('<10 %.1f%% p5 %.1f mean %.1f clip %.2f%%' % (s['lt10'], s['p5'], s['mean'], s['clip']))
        print('| %s | %s |' % (pose, ' | '.join(cells)))
    if a.diag:
        print('\n## lapse diagnostics')
        for jp in sorted(glob.glob(os.path.join(a.diag, '*', '*.json'))):
            d = json.load(open(jp)); c = d['checks_L23b']
            print('%s: %d frames substeps %s max jump %.2f p99 %.2f frames>3 %d >1.5 %d  window mean<=%.1f clipped<=%.2f%% (at %.2f h)' % (os.path.basename(jp), d['frames'], d.get('substeps', 1), c['max_jump'], c['p99_jump'], c['frames_over_3'], c['frames_over_1.5'],
                  c['window_05_2130']['max_mean_y'], c['window_05_2130']['max_clipped_pct'], c['window_05_2130']['hour_of_max_clipped']))
            print('   biggest:', ', '.join('%.2fh %+.1f' % (j['hour'], j['jump']) for j in c['biggest_jumps'][:6]))


if __name__ == '__main__':
    main()
