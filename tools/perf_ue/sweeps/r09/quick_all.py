#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""Round 09: golden L1 / L5 (S7) per still + the share of pixels below Y 25 (city r10 line for S3 / S7 / S8) for tour frames named <S#>@<variant>.png or <preset>_<S#>_<res>[_<v>].jpg.
usage: quick_all.py <dir> [--json out.json]"""
import sys, os, glob, json, re
import numpy as np, cv2
SPEC = ('L1', 61, 100, 8.0, 1.8, -55, -20); SPEC_S7 = ('L5', 59, 118, 8.8, 0.7, -55, -20)
def stats(p):
    im = cv2.imread(p); im = im if im.shape[1] == 1920 else cv2.resize(im, (1920, int(round(im.shape[0] * 1920 / im.shape[1]))), interpolation=cv2.INTER_AREA)
    f = im.astype(np.float32); Y = .2126 * f[..., 2] + .7152 * f[..., 1] + .0722 * f[..., 0]
    return dict(mean=float(Y.mean()), nb10=float((Y < 10).mean() * 100), nb25=float((Y < 25).mean() * 100), clip=float((im >= 250).any(axis=2).mean() * 100), BR=float(f[..., 0].mean() - f[..., 2].mean()))
if __name__ == '__main__':
    d = sys.argv[1]; jo = sys.argv[sys.argv.index('--json') + 1] if '--json' in sys.argv else None
    rows = {}
    for p in sorted(glob.glob(os.path.join(d, '*.png')) + glob.glob(os.path.join(d, '*.jpg'))):
        b = os.path.basename(p); m = re.match(r'(S\d)@(.+)\.png$', b); m2 = re.match(r'([a-z]+)_(S\d)_\d+x\d+_?(.*)\.(?:jpg|png)$', b)
        if m: s, v = m.group(1), m.group(2)
        elif m2: s, v = m2.group(2), m2.group(1) + ('_' + m2.group(3) if m2.group(3) else '')
        else: continue
        st = stats(p); sp = SPEC_S7 if s == 'S7' else SPEC
        st['L'] = sp[0]; st['pass'] = bool(sp[1] <= st['mean'] <= sp[2] and st['nb10'] <= sp[3] and st['clip'] <= sp[4] and sp[5] <= st['BR'] <= sp[6])
        rows.setdefault(v, {})[s] = st
    for v, r in rows.items():
        n = sum(x['pass'] for x in r.values())
        print('%-24s L1/L5 %d/%d | ' % (v[:24], n, len(r)) + ' '.join('%s %.0f/%.1f/%.2f/%+.0f%s' % (s, x['mean'], x['nb10'], x['clip'], x['BR'], '' if x['pass'] else '!') for s, x in sorted(r.items()))
              + ' | Y<25 S3 %s S7 %s S8 %s' % tuple(('%.1f' % r[s]['nb25']) if s in r else '-' for s in ('S3', 'S7', 'S8')))
    if jo: json.dump(rows, open(jo, 'w'), indent=1)
