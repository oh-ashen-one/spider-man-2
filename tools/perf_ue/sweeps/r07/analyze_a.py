#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 07: pivot of the hold-A sweep (dome_check.py json) - per hour and pose, one row per combo: sky-far / 8-row step / clip rows 0-150 / sky B-R / mean, and how many L27 lines pass.
usage: analyze_a.py <DOME_A.json> [--out <md>]"""
import json, sys
d = json.load(open(sys.argv[1])); rows = d['rows']
L = ['# hold A pivot (dome_check.py)', '', '> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.', '']
for h in sorted({r['hour'] for r in rows if r['hour'] is not None}):
    for pose in ('S4', 'S4w', 'S4e'):
        rs = [r for r in rows if r['hour'] == h and r['pose'] == pose]
        if not rs: continue
        L += ['### %s %g' % (pose, h), '| combo | sky Y | far Y | sky-far | step8 @row | clip0-150 % | B-R | mean | pass a/b/c/d |', '|---|---|---|---|---|---|---|---|---|']
        for r in sorted(rs, key=lambda r: r['variant']):
            p = ''.join({True: 'Y', False: 'n', None: '-'}[r[k]] for k in ('L27a', 'L27b', 'L27c', 'L27d'))
            L.append('| %s | %.1f | %.1f | %+.1f | %.1f @%d | %.2f | %+.1f | %.1f | %s |' % (r['prefix'].rstrip('_'), r['sky_Y'], r['far_Y'], r['sky_minus_far'], r['step8_max'], r['step8_row'], r['clip_rows0_150_pct'], r['sky_BR'], r['mean_Y'], p))
        L.append('')
txt = '\n'.join(L); print(txt)
if len(sys.argv) > 3 and sys.argv[2] == '--out': open(sys.argv[3], 'w').write(txt + '\n')
