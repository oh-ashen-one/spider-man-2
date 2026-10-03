#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 09 blind critic pairs: x = our round-09 still, y = the private reference (~/spiderman-learnings/refs, never committed), the merged look round-03 still,
the city round-11 S4 frame, or the round-08 golden preset on the round-09 city (the 'before' of this round).
Both sides of every pair are written at the SAME pixel size (1920x1080, centre crop to 16:9, Lanczos when the source differs, PNG) into <norm dir>; abpack.py re-encodes them.
usage: make_pairs.py <out pairs.json> <norm dir>"""
import json, os, sys
from PIL import Image

LOOK = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'docs', 'night1', 'look'))
CITY = os.path.abspath(os.path.join(LOOK, '..', 'city'))
R = '/Users/midir/spiderman-learnings/refs/'
R9 = LOOK + '/round-09/stills/'
g9 = lambda s: R9 + 'golden_%s_1920x1080_manhattan.jpg' % s          # golden preset, integrated map /Game/Maps/Manhattan (shot tour)
s4v = R9 + 'golden_S4_1920x1080_manhattan_view.jpg'                   # /Game/Maps/Manhattan_View_S4 (the map's own shot camera, t = 38 s)
f9 = lambda p, s: R9 + '%s_%s_1920x1080.jpg' % (p, s)                 # fixed midday / night preset maps
t9 = lambda s, h: R9 + 'tod_%s_1920x1080_%s.jpg' % (s, h)             # time of day (round-08 table, round-09 city)
b9 = lambda s: R9 + 'before_golden_%s_1920x1080.jpg' % s              # round-08 golden preset on the round-09 city (sweep base frame)
t3 = lambda p, s: '%s/round-03/stills/%s_%s_%s.jpg' % (LOOK, p, s, '1920x1080' if p != 'night' else '3840x2160')
P = [
 ('golden-perch-skyline', s4v, R + 'streets/skyline-perch-nm__nm_0846.jpg', 'golden hour over the city from a high perch: sky, haze, far skyline'),
 ('golden-perch-skyline-2', g9('S4'), R + 'streets/skyline-sunset-nm__nm_0329.jpg', 'low sun over the city from a high perch'),
 ('golden-sunstreet', g9('S7'), R + 'traversal/swing-avenue-sunset__nm_0654.jpg', 'golden hour, looking down a street toward the sun'),
 ('golden-avenue-street', g9('S1'), R + 'traversal/swing-avenue-sunlit__og_0609.jpg', 'golden hour, avenue canyon at street level'),
 ('golden-rooftop', g9('S3'), R + 'streets/rooftops-watertowers-golden__nm_0314.jpg', 'golden hour, rooftop with water tanks and towers'),
 ('golden-aerial', g9('S8'), R + 'traversal/press-dive-over-city-golden__psblog_11.jpg', 'golden hour, high view over the city'),
 ('golden-swing-view', g9('S2'), R + 'traversal/press-swing-canyon-golden__psblog_08.jpg', 'golden hour, high view down an avenue'),
 ('overcast-skyline', f9('midday', 'S4'), R + 'streets/skyline-overcast-dn__dn_0134.jpg', 'overcast day skyline from a perch'),
 ('night-skyline', f9('night', 'S4'), R + 'streets/skyline-night-perch__nt_0012.jpg', 'night skyline from a high perch'),
 ('night-street', f9('night', 'S1'), R + 'streets/night-street-level__nt_0420.jpg', 'night street level'),
 ('dusk-sun-facing', t9('S4w', 'h19.5'), R + 'streets/sunset-river-og__og_0559.jpg', 'sunset, the perch turned toward the sun'),
 ('dawn-sun-facing', t9('S4e', 'h7'), R + 'streets/skyline-sunset-nm__nm_0329.jpg', 'low sun over the city from a high perch, turned toward the sun'),
 ('blue-hour-skyline', t9('S4', 'h20.5'), R + 'streets/skyline-empire-top__nm_0024.jpg', 'late twilight skyline from a high perch'),
 ('night-moon', t9('S4m', 'h22'), R + 'animation/perch-moon__nt_0035.jpg', 'night sky with the moon and clouds, perch'),
]
# progress: merged look round 03 (fixed presets) vs round 09 (fixed presets on the integrated map)
for s in ('S4', 'S7', 'S1', 'S3'):
    P.append(('progress-r03-golden-%s' % s.lower(), g9(s) if s != 'S4' else s4v, t3('golden', s), 'two versions of our golden view %s (same pose)' % s))
for s in ('S4', 'S7'):
    P.append(('progress-r03-midday-%s' % s.lower(), f9('midday', s), t3('midday', s), 'two versions of our overcast midday view %s (same pose)' % s))
for s in ('S4', 'S1'):
    P.append(('progress-r03-night-%s' % s.lower(), f9('night', s), t3('night', s), 'two versions of our night view %s (same pose)' % s))
# the S4 frame the city round-11 critic judged (city test map, city lighting) vs round 09 S4 (integrated map, golden preset)
P.append(('progress-city-r11-s4', s4v, CITY + '/round-11/S4_perch_skyline_1920x1080.jpg', 'two versions of the same perch view over the skyline'))
# before / after of this round on the same city build: the round-08 golden preset vs round 09
for s in ('S4', 'S7', 'S3'):
    P.append(('progress-before-golden-%s' % s.lower(), g9(s), b9(s), 'two versions of our golden view %s on the same city (same pose)' % s))


def norm(src, dst, size):
    im = Image.open(src).convert('RGB')
    w, h = im.size; tw, th = size
    if abs(w / h - tw / th) > 1e-3:
        if w / h > tw / th: nw = int(round(h * tw / th)); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
        else: nh = int(round(w * th / tw)); im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    if im.size != size: im = im.resize(size, Image.LANCZOS)
    im.save(dst)


def main():
    out, nd = sys.argv[1], sys.argv[2]; os.makedirs(nd, exist_ok=True)
    res = []; missing = []
    for i, x, y, n in P:
        if not os.path.exists(x) or not os.path.exists(y): missing.append((i, x if not os.path.exists(x) else y)); continue
        nx, ny = os.path.join(nd, i + '_x.png'), os.path.join(nd, i + '_y.png')
        norm(x, nx, (1920, 1080)); norm(y, ny, (1920, 1080))
        res.append(dict(id=i, x=nx, y=ny, note=n, x_src=x, y_src=y))
    if missing: print('MISSING', missing)
    json.dump(res, open(out, 'w'), indent=1); print('pairs', len(res))


if __name__ == '__main__':
    main()
