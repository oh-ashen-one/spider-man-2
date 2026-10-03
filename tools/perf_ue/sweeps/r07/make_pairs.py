#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 07 blind critic pairs: x = our round-07 still, y = the private reference (~/spiderman-learnings/refs, never committed) or the round-06 still (progress pairs).
Progress pairs cover every verdict still of the twilight dome (S4 + S4w at 19:30 19:48 20:00 20:30, S4 + S4e at 06:30 07:00).
usage: make_pairs.py <out pairs.json>"""
import json, os, sys
WT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'docs', 'night1', 'look'))
R = '/Users/midir/spiderman-learnings/refs/'
t7 = lambda pose, h: '%s/round-07/stills/tod_%s_1920x1080_h%s.jpg' % (WT, pose, h)
t6 = lambda pose, h: '%s/round-06/stills/tod_%s_1920x1080_h%s.jpg' % (WT, pose, h)
P = [
 ('dusk-sun-facing', t7('S4w', '19.8'), R + 'streets/sunset-river-og__og_0559.jpg', 'dusk (sun just under the horizon), the perch turned toward the sun: sky dome, horizon glow, city'),
 ('dusk-early-sun-facing', t7('S4w', '19.5'), R + 'streets/sunset-river-og__og_0559.jpg', 'sunset, the perch turned toward the sun'),
 ('dusk-skyline', t7('S4', '20'), R + 'streets/skyline-empire-top__nm_0024.jpg', 'twilight skyline from a high perch: sky glow, lit windows'),
 ('blue-hour-skyline', t7('S4', '20.5'), R + 'streets/skyline-empire-top__nm_0024.jpg', 'late twilight skyline from a high perch'),
 ('dawn-sun-facing', t7('S4e', '7'), R + 'streets/skyline-sunset-nm__nm_0329.jpg', 'low sun over the city from a high perch, the perch turned toward the sun'),
 ('dawn-skyline', t7('S4', '6.5'), R + 'streets/skyline-sunset-nm__nm_0329.jpg', 'dawn twilight skyline from a high perch'),
 ('golden-skyline', t7('S4', '18.4'), R + 'streets/skyline-sunset-nm__nm_0329.jpg', 'golden hour over the city from a high perch: sky, clouds, aerial perspective'),
 ('golden-sunstreet', t7('S7', '18.4'), R + 'traversal/swing-avenue-sunset__nm_0654.jpg', 'golden hour, looking down a street toward the sun'),
 ('golden-avenue-street', t7('S1', '18.4'), R + 'traversal/swing-avenue-sunlit__og_0609.jpg', 'golden hour, avenue canyon at street level'),
 ('golden-rooftop', t7('S3', '18.4'), R + 'streets/rooftops-watertowers-golden__nm_0314.jpg', 'golden hour, rooftop with water tanks and towers'),
 ('night-moon', t7('S4m', '22'), R + 'animation/perch-moon__nt_0035.jpg', 'night sky with the moon and clouds, perch'),
 ('night-skyline', t7('S4', '22'), R + 'streets/skyline-night-perch__nt_0012.jpg', 'night skyline from a high perch'),
 ('night-street', t7('S1', '22'), R + 'streets/night-street-level__nt_0420.jpg', 'night street level'),
 ('day-skyline', t7('S4', '13'), R + 'streets/skyline-perch-dn__dn_1438.jpg', 'clear day skyline from a perch'),
]
for pose, hs in (('S4w', ('19.5', '19.8', '20', '20.5')), ('S4', ('19.5', '19.8', '20', '20.5', '6.5', '7')), ('S4e', ('6.5', '7'))):
    for h in hs:
        view = {'S4w': 'the perch turned toward the dusk sun', 'S4e': 'the perch turned toward the dawn sun', 'S4': 'the standard skyline perch'}[pose]
        P.append(('progress-%s-%s' % (pose.lower(), h.replace('.', '')), t7(pose, h), t6(pose, h), 'two versions of our twilight view (same pose, same hour %s): %s' % (h, view)))
P.append(('progress-golden-skyline', t7('S4', '18.4'), t6('S4', '18.4'), 'two versions of our golden-hour skyline (same pose, same hour)'))
P.append(('progress-night-skyline', t7('S4', '22'), t6('S4', '22'), 'two versions of our night skyline (same pose, same hour)'))
P.append(('progress-lapse-sheet', '%s/round-07/tod_lapse_S4_sheet.jpg' % WT, '%s/round-06/tod_lapse_S4_sheet.jpg' % WT, 'contact sheet of two versions of our 24 h time-lapse from the perch (04:00 start, 2 h per second): sky, haze and exposure over the day'))
out = [dict(id=i, x=x, y=y, note=n) for i, x, y, n in P]
missing = [p['x'] for p in out if not os.path.exists(p['x'])] + [p['y'] for p in out if not os.path.exists(p['y'])]
if missing: print('MISSING', missing)
json.dump(out, open(sys.argv[1], 'w'), indent=1); print('pairs', len(out))
