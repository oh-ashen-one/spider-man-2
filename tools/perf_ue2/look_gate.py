#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See DISCLAIMER.md.
"""Piece F look gate, ROUND 07 EDITION (written and committed BEFORE any round-07 optimisation; the critic runs this same file).
Rounds 03 and 06 shipped visual losses that the older gate did not measure (round 06: S2 avenue tree line and S7 lower-left lit
foliage). This version fixes every view, crop, metric and pass line in code; nothing is chosen per run.

usage: look_gate.py <test_dir> [--asfound DIR] [--r06 DIR] [--json out.json] [--md out.md]
  test_dir  = a stills2.sh output with view_S1.png, view_S2.png, view_S7.png, route_t20.png, route_t28.png, route_t42.png (3840x2160 PNG)
  --asfound = the as-found stills of this build (no preset, content untouched): /Users/midir/sm2-n1/_scratch/perf/r03/before
  --r06     = the round-06 shipped stills: /Users/midir/sm2-n1/_scratch/perf/r06/final
Exit code 0 = GATE PASS, 1 = GATE FAIL, 2 = missing input.

References
  S1 / S2 / S7 are compared with the AS-FOUND stills (same static cameras since round 03).
  route t20 / t28 / t42 are compared with the ROUND-06 SHIPPED stills: since round 05 the route uses traversal's r14 chase camera, so the
  as-found route stills show different frames (SSIM 0.23-0.30) and are no valid reference. The route rows are therefore NON-REGRESSION
  rows (vs round 06), not as-found rows. Disclosed limitation.

Image processing (identical for every row)
  every still is area-downsampled to 1920x1080 (cv2.INTER_AREA); all coordinates are (x0, y0, x1, y1) in that space.
  SSIM      = 8x8 box SSIM on Rec.709 luma (crop_ssim.ssim), computed on the crop.
  foliage % = share of crop pixels with G > R + 5 and G > B + 5 (8-bit sRGB): the critic's green-dominant leaf measure.
  canopy Y  = mean luma of the pixels that are foliage in the REFERENCE still, read at the same positions in the test still.
  sat       = mean HSV saturation (OpenCV 0-255) of the whole frame.
  recess Y  = mean luma of the S1 sidewalk-shed recess (1700, 540, 1850, 650).

Rows. class GATE decides PASS / FAIL; class SPEC is the standing SPEC P11 crop line (0.97 vs as found), printed with its own result but not
part of the gate verdict, because two captures of identical content and settings already differ by ~0.03 on this crop (round 06: 0.969
repeat, 0.905-0.929 single captures of the shipped content); its non-regression twin (>= 0.90, lowest single capture seen) is a GATE row.
  ratio lines are two-sided (|test/ref - 1| <= tol) against the as-found reference, one-sided (test/ref >= 1 - tol) against round 06."""
import argparse, json, os, sys
import numpy as np, cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crop_ssim import luma, ssim  # noqa: E402

ASFOUND = '/Users/midir/sm2-n1/_scratch/perf/r03/before'
R06 = '/Users/midir/sm2-n1/_scratch/perf/r06/final'
FULL = (0, 0, 1920, 1080)

# (id, still, reference, metric, crop, line, class)
#   metric: ssim_min (test >= line), fol_2s / canopy_2s / sat_2s / luma_2s (|ratio - 1| <= line), fol_1s / canopy_1s / sat_1s (ratio >= 1 - line)
ROWS = [
    ('S1_glass_spec',   'view_S1', 'asfound', 'ssim_min',  (485, 0, 710, 490),    0.97, 'SPEC'),
    ('S1_glass',        'view_S1', 'asfound', 'ssim_min',  (485, 0, 710, 490),    0.90, 'GATE'),
    ('S1_canopy_fol',   'view_S1', 'asfound', 'fol_2s',    (480, 180, 720, 360),  0.10, 'GATE'),
    ('S1_canopy_Y',     'view_S1', 'asfound', 'canopy_2s', FULL,                  0.10, 'GATE'),
    ('S1_recess_Y',     'view_S1', 'asfound', 'luma_2s',   (1700, 540, 1850, 650), 0.10, 'GATE'),
    ('S1_sat',          'view_S1', 'asfound', 'sat_2s',    FULL,                  0.05, 'GATE'),
    ('S2_treeline_fol', 'view_S2', 'asfound', 'fol_2s',    (780, 380, 1180, 1080), 0.10, 'GATE'),
    ('S2_tile_fol',     'view_S2', 'asfound', 'fol_2s',    (960, 540, 1200, 720), 0.10, 'GATE'),
    ('S2_treeline',     'view_S2', 'asfound', 'ssim_min',  (780, 380, 1180, 1080), 0.90, 'GATE'),
    ('S2_windows',      'view_S2', 'asfound', 'ssim_min',  (0, 38, 576, 960),     0.97, 'GATE'),
    ('S2_gold',         'view_S2', 'asfound', 'ssim_min',  (1459, 0, 1920, 1056), 0.97, 'GATE'),
    ('S2_canopy_Y',     'view_S2', 'asfound', 'canopy_2s', FULL,                  0.10, 'GATE'),
    ('S2_sat',          'view_S2', 'asfound', 'sat_2s',    FULL,                  0.05, 'GATE'),
    ('S7_tile_fol',     'view_S7', 'asfound', 'fol_2s',    (0, 720, 240, 900),    0.10, 'GATE'),
    ('S7_refl',         'view_S7', 'asfound', 'ssim_min',  (0, 560, 720, 1080),   0.97, 'GATE'),
    ('S7_sat',          'view_S7', 'asfound', 'sat_2s',    FULL,                  0.05, 'GATE'),
    ('t20_full',        'route_t20', 'r06',   'ssim_min',  FULL,                  0.95, 'GATE'),
    ('t20_fol',         'route_t20', 'r06',   'fol_1s',    FULL,                  0.10, 'GATE'),
    ('t20_canopy_Y',    'route_t20', 'r06',   'canopy_2s', FULL,                  0.10, 'GATE'),
    ('t20_sat',         'route_t20', 'r06',   'sat_2s',    FULL,                  0.05, 'GATE'),
    ('t28_full',        'route_t28', 'r06',   'ssim_min',  FULL,                  0.95, 'GATE'),
    ('t28_fol',         'route_t28', 'r06',   'fol_1s',    FULL,                  0.10, 'GATE'),
    ('t28_sat',         'route_t28', 'r06',   'sat_2s',    FULL,                  0.05, 'GATE'),
    ('t42_full',        'route_t42', 'r06',   'ssim_min',  FULL,                  0.95, 'GATE'),
    ('t42_fol',         'route_t42', 'r06',   'fol_1s',    FULL,                  0.10, 'GATE'),
    ('t42_sat',         'route_t42', 'r06',   'sat_2s',    FULL,                  0.05, 'GATE'),
]


def load(p):
    im = cv2.imread(p)
    return None if im is None else cv2.resize(im, (1920, 1080), interpolation=cv2.INTER_AREA)


def fol_mask(img):
    b, g, r = [img[..., i].astype(np.int16) for i in range(3)]
    return (g > r + 5) & (g > b + 5)


def sat(img): return float(cv2.cvtColor(img, cv2.COLOR_BGR2HSV)[..., 1].mean())


def measure(metric, A, B, crop):
    x0, y0, x1, y1 = crop
    a, b = A[y0:y1, x0:x1], B[y0:y1, x0:x1]
    if metric == 'ssim_min': return ssim(luma(a), luma(b)), 1.0, None
    if metric.startswith('fol'): ra, rb = fol_mask(a).mean() * 100, fol_mask(b).mean() * 100
    elif metric.startswith('canopy'):
        m = fol_mask(a)
        if m.mean() < 0.01: return None, None, 'reference foliage < 1 % of the crop: not gated'
        ra, rb = float(luma(a)[m].mean()), float(luma(b)[m].mean())
    elif metric.startswith('sat'): ra, rb = sat(a), sat(b)
    elif metric.startswith('luma'): ra, rb = float(luma(a).mean()), float(luma(b).mean())
    else: raise ValueError(metric)
    return rb, ra, None


def evaluate(test, refs):
    rows, cache = [], {}
    def get(d, s):
        k = (d, s)
        if k not in cache: cache[k] = load(os.path.join(d, s + '.png'))
        return cache[k]
    for rid, still, ref, metric, crop, line, cls in ROWS:
        A, B = get(refs[ref], still), get(test, still)
        r = {'id': rid, 'still': still, 'ref': ref, 'metric': metric, 'crop': crop, 'line': line, 'class': cls}
        if A is None or B is None:
            r.update(result='MISSING', note='missing %s' % ('reference' if A is None else 'test still')); rows.append(r); continue
        val, refv, note = measure(metric, A, B, crop)
        if val is None: r.update(result='n/a', note=note); rows.append(r); continue
        if metric == 'ssim_min':
            ok = val >= line; r.update(test=round(val, 4), ratio=None, line_txt='>= %.2f' % line)
        else:
            ratio = val / refv if refv else float('inf')
            ok = abs(ratio - 1) <= line if metric.endswith('_2s') else ratio >= 1 - line
            r.update(test=round(val, 3), refv=round(refv, 3), ratio=round(ratio, 3),
                     line_txt=('ratio %.2f-%.2f' % (1 - line, 1 + line)) if metric.endswith('_2s') else ('ratio >= %.2f' % (1 - line)))
        r['result'] = 'PASS' if ok else 'FAIL'
        rows.append(r)
    gate = [r for r in rows if r['class'] == 'GATE']
    verdict = 'PASS' if all(r['result'] in ('PASS', 'n/a') for r in gate) else 'FAIL'
    return rows, verdict


def md(test, refs, rows, verdict):
    L = ['look_gate.py (round 07 edition) test=%s' % test, 'references: as found = %s ; r06 = %s' % (refs['asfound'], refs['r06']), '',
         '| id | still | ref | metric | crop (1920 space) | reference | test | ratio | line | class | result |', '|---|---|---|---|---|---|---|---|---|---|---|']
    for r in rows:
        refv = '%.3f' % r['refv'] if 'refv' in r else ('-' if r.get('metric') == 'ssim_min' else '')
        L.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
            r['id'], r['still'], r['ref'], r['metric'], ','.join(str(v) for v in r['crop']), refv,
            r.get('test', ''), '' if r.get('ratio') is None else r['ratio'], r.get('line_txt', ''), r['class'],
            r['result'] + (' (%s)' % r['note'] if r.get('note') else '')))
    nf = sum(1 for r in rows if r['class'] == 'GATE' and r['result'] not in ('PASS', 'n/a'))
    L += ['', 'GATE VERDICT: **%s** (%d GATE rows, %d not passing; SPEC rows reported, not gated)' % (verdict, sum(1 for r in rows if r['class'] == 'GATE'), nf)]
    return '\n'.join(L)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('test'); ap.add_argument('--asfound', default=ASFOUND); ap.add_argument('--r06', default=R06)
    ap.add_argument('--json'); ap.add_argument('--md')
    a = ap.parse_args()
    refs = {'asfound': a.asfound, 'r06': a.r06}
    rows, verdict = evaluate(a.test, refs)
    txt = md(a.test, refs, rows, verdict); print(txt)
    if a.json: json.dump({'test': a.test, 'refs': refs, 'rows': rows, 'verdict': verdict}, open(a.json, 'w'), indent=1)
    if a.md: open(a.md, 'w').write(txt + '\n')
    if any(r['result'] == 'MISSING' for r in rows): sys.exit(2)
    sys.exit(0 if verdict == 'PASS' else 1)


if __name__ == '__main__':
    main()
