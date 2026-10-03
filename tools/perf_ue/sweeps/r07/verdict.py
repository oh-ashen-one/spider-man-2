#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 07: verdict table of the L27 dome lines on the round's verdict stills (S4 + S4w at 19.5 19.8 20 20.5, S4 + S4e at 6.5 7), from dome_check.py's json.
usage: verdict.py <DOME json> [--md out.md]"""
import json, sys
d = json.load(open(sys.argv[1])); rows = d['rows'] if isinstance(d, dict) else d
V = [('S4', h) for h in (19.5, 19.8, 20.0, 20.5)] + [('S4w', h) for h in (19.5, 19.8, 20.0, 20.5)] + [('S4', h) for h in (6.5, 7.0)] + [('S4e', h) for h in (6.5, 7.0)]
L = ['| still | sky Y | far Y | sky-far (a >= 10) | 8-row step (b <= 25) | clip rows 0-150 % (c <= 0.3) | sky B-R (d -90..-20, facing) | a | b | c | d |', '|---|---|---|---|---|---|---|---|---|---|---|']
npass = ntot = 0; fails = []
for pose, h in V:
    r = [x for x in rows if x['pose'] == pose and x['hour'] == h and (x.get('prefix') or '') == '']
    if not r: L.append('| %s %g | missing |' % (pose, h)); continue
    r = r[0]; ok = lambda x: {True: 'ok', False: 'FAIL', None: ''}[x]
    for k in ('L27a', 'L27b', 'L27c', 'L27d'):
        if r[k] is not None: ntot += 1; npass += 1 if r[k] else 0
        if r[k] is False: fails.append('%s %g %s' % (pose, h, k[-1]))
    L.append('| %s %02d:%02d | %.1f | %.1f | %+.1f | %.1f | %.2f | %+.1f | %s | %s | %s | %s |' % (pose, int(h), round((h % 1) * 60), r['sky_Y'], r['far_Y'], r['sky_minus_far'], r['step8_max'], r['clip_rows0_150_pct'], r['sky_BR'], ok(r['L27a']), ok(r['L27b']), ok(r['L27c']), ok(r['L27d'])))
L.append(''); L.append('lines passed %d of %d; failing: %s' % (npass, ntot, ', '.join(fails) or 'none'))
t = '\n'.join(L); print(t)
if len(sys.argv) > 3 and sys.argv[2] == '--md': open(sys.argv[3], 'w').write(t + '\n')
