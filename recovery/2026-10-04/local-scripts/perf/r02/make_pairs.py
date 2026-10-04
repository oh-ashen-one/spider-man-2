#!/usr/bin/env python3
# writes /Users/midir/sm2-n1/_scratch/critic-F-r02/pairs.json from the final captures (neutral notes: view descriptions only)
import json, os, sys
F = '/Users/midir/sm2-n1/_scratch/perf/r02/final'
R = '/Users/midir/spiderman-learnings/refs'
R1 = '/Users/midir/sm2-n1/perf/docs/night1/perf/round-01/stills'
P = [
 ('S1-avenue-street', F + '/after/view_S1.png', R + '/streets/street-avenue-hero-taxis__og_0000.jpg', 'street-level avenue canyon looking along the avenue, sunset, glass tower on the left'),
 ('S2-avenue-high', F + '/after/view_S2.png', R + '/streets/street-midtown-high__og_0410.jpg', 'about 40 m above an avenue, looking down the canyon, lit windows and glass towers on both sides'),
 ('S7-sunset-cross-street', F + '/after/view_S7.png', R + '/streets/sunset-swing-trailer__eny_0142.jpg', 'sunset, chase-style camera high over a cross street looking west'),
 ('R1-swing-canyon-above', F + '/after/route_t28.png', R + '/traversal/swing-avenue-canyon-above__nm_0557.jpg', 'chase camera high, pitched down along an avenue canyon during a swing'),
 ('clip-swing-canyon', F + '/movie/route_30s.mp4', R + '/traversal/clips/swing-canyon-chase__nm_0139-0147.mp4', 'swing route through avenue canyons, chase camera (our clip is 30 s, the other 8 s; judge the look, not the length)'),
 ('prev-vs-this-S2', F + '/after/view_S2.png', R1 + '/after_view_S2.jpg', 'same camera, two builds of the same game (about 40 m above an avenue)'),
]
out = []
for i, x, y, note in P:
    if not os.path.exists(x) or not os.path.exists(y): print('MISSING', i, x if not os.path.exists(x) else y); continue
    out.append({'id': i, 'x': x, 'y': y, 'note': note})
os.makedirs('/Users/midir/sm2-n1/_scratch/critic-F-r02', exist_ok=True)
json.dump(out, open('/Users/midir/sm2-n1/_scratch/critic-F-r02/pairs.json', 'w'), indent=1)
print(len(out), 'pairs')
