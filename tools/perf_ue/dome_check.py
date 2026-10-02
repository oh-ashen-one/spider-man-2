#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 07: twilight dome continuity checks (LOOK-SPEC L27, from the round-06 critic verdict "Biggest gap") on tod_<pose>_<res>_<variant>.jpg stills.
Per still (1920x1080; S4 / S4w / S4e, any hour; the round's verdict hours are S4 + S4w at 19:30 19:48 20:00 20:30 and S4 + S4e at 06:30 07:00):
  L27a  sky band (rows 0-89, every column) Y >= far band (box 450,192,1350,236 of the 1080 frame, the S4 far shore) + 10
  L27b  no 8-row step of the row-mean luma > 25 Y in rows 100-300 (|mean(row r+8) - mean(row r)|); also reported per 240-px column band (the worst band) as a diagnostic
  L27c  rows 0-150: clipped (any channel >= 250) <= 0.3 % of the pixels
  L27d  sun-facing still (S4w at dusk, S4e at dawn): sky band B-R within -90 .. -20 (S4 reported, not judged)
  L27e  S4 frame mean at 20:30 >= S4 frame mean at 22:00 (same variant prefix) - no dark pit
usage: dome_check.py --dir <stills> [--out <base>] [--res 1920x1080] [--match <substring>]
Hour of a still = the trailing 'h<number>' of its variant name; the variant prefix is the part before it (e.g. 'c3_h20' -> prefix 'c3_')."""
import argparse, glob, json, os, re
import numpy as np
from PIL import Image

FAR_BOX = (450, 192, 1350, 236)
SKY_ROWS = 90
STEP_ROWS = (100, 300)
STEP = 8
CLIP_ROWS = 150


def load(p, w=1920):
    im = Image.open(p).convert('RGB')
    if im.size[0] != w: im = im.resize((w, int(round(im.size[1] * w / im.size[0]))), Image.BOX if im.size[0] > w else Image.BICUBIC)
    return np.asarray(im, dtype=np.float32)


def Y(im): return 0.2126 * im[..., 0] + 0.7152 * im[..., 1] + 0.0722 * im[..., 2]


def check(im, pose, hour):
    y = Y(im)
    sky = im[:SKY_ROWS]; sy = float(y[:SKY_ROWS].mean())
    x0, y0, x1, y1 = FAR_BOX
    far = float(y[y0:y1, x0:x1].mean())
    prof = y.mean(axis=1)
    a, b = STEP_ROWS
    d = np.abs(prof[a + STEP:b + 1] - prof[a:b + 1 - STEP])
    step_max = float(d.max()); step_row = int(a + int(d.argmax()))
    bands = []
    for c in range(0, 1920, 240):
        pc = y[:, c:c + 240].mean(axis=1); dc = np.abs(pc[a + STEP:b + 1] - pc[a:b + 1 - STEP]); bands.append(float(dc.max()))
    top = im[:CLIP_ROWS]
    clip = float((top.max(axis=2) >= 250).mean() * 100.0)
    br = float(sky[..., 2].mean() - sky[..., 0].mean())
    r = {'pose': pose, 'hour': hour, 'sky_Y': round(sy, 2), 'far_Y': round(far, 2), 'sky_minus_far': round(sy - far, 2), 'L27a': bool(sy - far >= 10.0),
         'step8_max': round(step_max, 2), 'step8_row': step_row, 'step8_band_max': round(max(bands), 2), 'L27b': bool(step_max <= 25.0),
         'clip_rows0_150_pct': round(clip, 3), 'L27c': bool(clip <= 0.3), 'sky_BR': round(br, 2), 'mean_Y': round(float(y.mean()), 2),
         'clip_frame_pct': round(float((im.max(axis=2) >= 250).mean() * 100.0), 3)}
    facing = (pose == 'S4w' and hour is not None and hour >= 12) or (pose == 'S4e' and hour is not None and hour < 12)
    r['L27d'] = bool(-90.0 <= br <= -20.0) if facing else None
    return r


def hour_of(v):
    m = re.search(r'h(\d+(?:\.\d+)?)$', v)
    return float(m.group(1)) if m else None


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--dir', required=True); ap.add_argument('--out', default=''); ap.add_argument('--res', default='1920x1080'); ap.add_argument('--match', default='')
    a = ap.parse_args()
    rows = []
    for f in sorted(glob.glob(os.path.join(a.dir, 'tod_*_%s_*.jpg' % a.res))):
        m = re.match(r'tod_(S\d\w*)_%s_(.+)\.jpg' % a.res, os.path.basename(f))
        if not m or m.group(1) not in ('S4', 'S4w', 'S4e'): continue
        if a.match and a.match not in m.group(2): continue
        v = m.group(2); h = hour_of(v)
        r = check(load(f), m.group(1), h); r['variant'] = v; r['prefix'] = v[:len(v) - len(re.search(r'h[\d.]+$', v).group(0))] if h is not None else v; r['file'] = os.path.basename(f)
        rows.append(r)
    pits = {}
    for r in rows:
        if r['pose'] == 'S4' and r['hour'] in (20.5, 22.0): pits.setdefault(r['prefix'], {})[r['hour']] = r['mean_Y']
    pit = {p: {'m2030': v.get(20.5), 'm2200': v.get(22.0), 'L27e': (v[20.5] >= v[22.0]) if (20.5 in v and 22.0 in v) else None} for p, v in pits.items()}
    L = ['| still | pose | hour | sky Y | far Y | sky-far (a >= 10) | 8-row step max @row (b <= 25) | worst column band | clip rows 0-150 % (c <= 0.3) | sky B-R (d facing -90..-20) | mean Y | a | b | c | d |',
         '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    ok = lambda x: {True: 'ok', False: 'FAIL', None: ''}[x]
    for r in rows:
        L.append('| %s | %s | %s | %.1f | %.1f | %+.1f | %.1f @%d | %.1f | %.2f | %+.1f | %.1f | %s | %s | %s | %s |' % (r['variant'], r['pose'], r['hour'], r['sky_Y'], r['far_Y'], r['sky_minus_far'], r['step8_max'], r['step8_row'],
                 r['step8_band_max'], r['clip_rows0_150_pct'], r['sky_BR'], r['mean_Y'], ok(r['L27a']), ok(r['L27b']), ok(r['L27c']), ok(r['L27d'])))
    if pit:
        L += ['', '| variant prefix | S4 mean 20:30 | S4 mean 22:00 | L27e (no pit) |', '|---|---|---|---|']
        for p, v in sorted(pit.items()): L.append('| %s | %s | %s | %s |' % (p or '(none)', v['m2030'], v['m2200'], ok(v['L27e'])))
    print('\n'.join(L))
    if a.out:
        json.dump({'rows': rows, 'pit': pit}, open(a.out + '.json', 'w'), indent=1)
        open(a.out + '.md', 'w').write('# Twilight dome checks (dome_check.py, LOOK-SPEC L27)\n\n> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.\n\n' + '\n'.join(L) + '\n')


if __name__ == '__main__':
    main()
