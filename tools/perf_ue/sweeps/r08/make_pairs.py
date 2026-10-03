#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 08 blind critic pairs: x = our round-08 still, y = the private reference (~/spiderman-learnings/refs, never committed), the round-03 still (merged floor) or the round-07 still.
Both sides of every pair are written at the SAME pixel size (1920x1080, centre crop to 16:9, Lanczos resample when the source differs, PNG) into <norm dir> before abpack.py re-encodes them:
the round-07 critic could tell identity from the resolution alone (refs 3840x2160, ours 1920x1080).
usage: make_pairs.py <out pairs.json> <norm dir>"""
import json, os, sys
from PIL import Image

WT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'docs', 'night1', 'look'))
R = '/Users/midir/spiderman-learnings/refs/'
t8 = lambda pose, h: '%s/round-08/stills/tod_%s_1920x1080_%s.jpg' % (WT, pose, h)
t7 = lambda pose, h: '%s/round-07/stills/tod_%s_1920x1080_%s.jpg' % (WT, pose, h)
t3 = lambda preset, pose: '%s/round-03/stills/%s_%s_%s.jpg' % (WT, preset, pose, '1920x1080' if preset != 'night' else '3840x2160')
P = [
 ('dawn-sun-facing', t8('S4e', 'h7'), R + 'streets/skyline-sunset-nm__nm_0329.jpg', 'low sun over the city from a high perch, the perch turned toward the sun'),
 ('dawn-sun-facing-late', t8('S4e', 'h7.5'), R + 'streets/skyline-sunset-nm__nm_0329.jpg', 'low sun over the city from a high perch, the perch turned toward the sun (half an hour later)'),
 ('dusk-sun-facing-low-sun', t8('S4w', 'h19'), R + 'streets/sunset-river-og__og_0559.jpg', 'sun on the horizon, the perch turned toward the sun'),
 ('dusk-early-sun-facing', t8('S4w', 'h19.5'), R + 'streets/sunset-river-og__og_0559.jpg', 'sunset, the perch turned toward the sun'),
 ('dusk-sun-facing', t8('S4w', 'h19.8'), R + 'streets/sunset-river-og__og_0559.jpg', 'dusk (sun just under the horizon), the perch turned toward the sun'),
 ('dusk-skyline', t8('S4', 'h20'), R + 'streets/skyline-empire-top__nm_0024.jpg', 'twilight skyline from a high perch: sky glow, lit windows'),
 ('blue-hour-skyline', t8('S4', 'h20.5'), R + 'streets/skyline-empire-top__nm_0024.jpg', 'late twilight skyline from a high perch'),
 ('dawn-skyline', t8('S4', 'h6.5'), R + 'streets/skyline-sunset-nm__nm_0329.jpg', 'dawn twilight skyline from a high perch'),
 ('golden-skyline', t8('S4', 'h18.4'), R + 'streets/skyline-sunset-nm__nm_0329.jpg', 'golden hour over the city from a high perch: sky, clouds, aerial perspective'),
 ('golden-sunstreet', t8('S7', 'h18.4'), R + 'traversal/swing-avenue-sunset__nm_0654.jpg', 'golden hour, looking down a street toward the sun'),
 ('golden-avenue-street', t8('S1', 'h18.4'), R + 'traversal/swing-avenue-sunlit__og_0609.jpg', 'golden hour, avenue canyon at street level'),
 ('golden-rooftop', t8('S3', 'h18.4'), R + 'streets/rooftops-watertowers-golden__nm_0314.jpg', 'golden hour, rooftop with water tanks and towers'),
 ('night-moon', t8('S4m', 'h22'), R + 'animation/perch-moon__nt_0035.jpg', 'night sky with the moon and clouds, perch'),
 ('night-skyline', t8('S4', 'h22'), R + 'streets/skyline-night-perch__nt_0012.jpg', 'night skyline from a high perch'),
 ('night-street', t8('S1', 'h22'), R + 'streets/night-street-level__nt_0420.jpg', 'night street level'),
 ('day-skyline', t8('S4', 'h13'), R + 'streets/skyline-perch-dn__dn_1438.jpg', 'clear day skyline from a perch'),
 ('overcast-skyline', t8('S4', 'w1_h13'), R + 'streets/skyline-overcast-dn__dn_0134.jpg', 'overcast day skyline from a perch'),
]
# progress: round-03 (the merged floor; fixed presets) vs round 08 (time of day at the matching hour)
for pose, pre, h in (('S4', 'golden', 'h18.4'), ('S7', 'golden', 'h18.4'), ('S1', 'golden', 'h18.4'), ('S4', 'night', 'h22'), ('S1', 'night', 'h22')):
    P.append(('progress-r03-%s-%s' % (pre, pose.lower()), t8(pose, h), t3(pre, pose), 'two versions of our %s view %s (same pose)' % (pre, pose)))
# the midday floor is the fixed midday preset map in both rounds
for pose in ('S4', 'S2', 'S7'):
    P.append(('progress-r03-midday-%s' % pose.lower(), '%s/round-08/stills/midday_%s_1920x1080.jpg' % (WT, pose), t3('midday', pose), 'two versions of our overcast midday view %s (same pose)' % pose))
# progress: round 07 vs round 08 at the twilight hours
for pose, hs in (('S4e', ('h7', 'h7.5', 'h6.5')), ('S4w', ('h19', 'h19.5', 'h19.8', 'h20', 'h20.5')), ('S4', ('h7', 'h19', 'h19.5', 'h20.5'))):
    for h in hs:
        view = {'S4w': 'the perch turned toward the dusk sun', 'S4e': 'the perch turned toward the dawn sun', 'S4': 'the standard skyline perch'}[pose]
        P.append(('progress-r07-%s-%s' % (pose.lower(), h.replace('.', '')), t8(pose, h), t7(pose, h), 'two versions of our twilight view (same pose, same hour %s): %s' % (h[1:], view)))
P.append(('progress-r07-lapse-sheet', '%s/round-08/tod_lapse_S4_sheet.jpg' % WT, '%s/round-07/tod_lapse_S4_sheet.jpg' % WT,
          'contact sheet of two versions of our 24 h time-lapse from the perch (04:00 start, 2 h per second): sky, haze and exposure over the day'))


def norm(src, dst, size):
    im = Image.open(src).convert('RGB')
    w, h = im.size; tw, th = size
    if abs(w / h - tw / th) > 1e-3:   # centre crop to the target aspect
        if w / h > tw / th: nw = int(round(h * tw / th)); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
        else: nh = int(round(w * th / tw)); im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    if im.size != size: im = im.resize(size, Image.LANCZOS)
    im.save(dst)


def main():
    out, nd = sys.argv[1], sys.argv[2]; os.makedirs(nd, exist_ok=True)
    res = []; missing = []
    for i, x, y, n in P:
        if not os.path.exists(x) or not os.path.exists(y): missing.append((i, x if not os.path.exists(x) else y)); continue
        size = Image.open(x).size if 'sheet' in i else (1920, 1080)
        if 'sheet' in i: size = (min(Image.open(x).size[0], Image.open(y).size[0]), min(Image.open(x).size[1], Image.open(y).size[1]))
        nx, ny = os.path.join(nd, i + '_x.png'), os.path.join(nd, i + '_y.png')
        norm(x, nx, size); norm(y, ny, size)
        res.append(dict(id=i, x=nx, y=ny, note=n, x_src=x, y_src=y))
    if missing: print('MISSING', missing)
    json.dump(res, open(out, 'w'), indent=1); print('pairs', len(res))


if __name__ == '__main__':
    main()
