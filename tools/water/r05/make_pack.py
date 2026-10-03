#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See DISCLAIMER.md.
"""Round-05 blind critic pack for the river water: pairs.json (x = ours, y = the matching reference or the r03-merged build), both sides of every
pair resized to the SAME pixel size (<= 2048 px wide copies of the 4K stills), then tools/night1/abpack.py.
usage: python3 tools/water/r05/make_pack.py [round dir] [critic dir]
Writes <critic dir>/work/*.jpg|mp4, <critic dir>/pairs.json, <critic dir>/pack (+ pack.key.json beside it). The critic is NOT run here."""
import json, os, subprocess, sys
import cv2

WT = '/Users/midir/sm2-n1/water'
R5 = sys.argv[1] if len(sys.argv) > 1 else WT + '/docs/night1/water/round-05'
CR = sys.argv[2] if len(sys.argv) > 2 else '/Users/midir/sm2-n1/_scratch/critic-W-r05'
R3 = WT + '/docs/night1/water/round-03'
REFS = '/Users/midir/spiderman-learnings/refs/streets/'
ABPACK = '/Users/midir/spider-man-2-astra6/tools/night1/abpack.py'
W = os.path.join(CR, 'work'); os.makedirs(W, exist_ok=True)


def fit(src, dst, w=2048, crop=None):
    """resize an image to w px wide (keeping its aspect ratio); crop = (x0, y0, x1, y1) in source pixels first"""
    im = cv2.imread(src)
    if crop: im = im[crop[1]:crop[3], crop[0]:crop[2]]
    h = int(round(im.shape[0] * w / im.shape[1]))
    im = cv2.resize(im, (w, h), interpolation=cv2.INTER_AREA if im.shape[1] > w else cv2.INTER_CUBIC)
    cv2.imwrite(dst, im, [cv2.IMWRITE_JPEG_QUALITY, 93]); return im.shape[1], im.shape[0]


def pair_same(pid, ours, other, note, w=2048, crop_o=None, crop_y=None):
    """both sides to the same size: width w, height from OURS; the other side is cropped to the same aspect ratio first (centre) if needed"""
    xo, yo = os.path.join(W, pid + '_x.jpg'), os.path.join(W, pid + '_y.jpg')
    sx = fit(ours, xo, w, crop_o)
    im = cv2.imread(other)
    if crop_y: im = im[crop_y[1]:crop_y[3], crop_y[0]:crop_y[2]]
    ar = sx[0] / sx[1]
    h0, w0 = im.shape[:2]
    if abs(w0 / h0 - ar) > 0.01:                       # centre-crop to our aspect ratio
        if w0 / h0 > ar: nw = int(round(h0 * ar)); im = im[:, (w0 - nw) // 2:(w0 - nw) // 2 + nw]
        else: nh = int(round(w0 / ar)); im = im[(h0 - nh) // 2:(h0 - nh) // 2 + nh]
    im = cv2.resize(im, sx, interpolation=cv2.INTER_AREA if im.shape[1] > sx[0] else cv2.INTER_CUBIC)
    cv2.imwrite(yo, im, [cv2.IMWRITE_JPEG_QUALITY, 93])
    return dict(id=pid, x=xo, y=yo, note=note)


def pair_video(pid, ours, other, note):
    """both clips to 1920x1080 at 30 fps (same size), <= 10 s"""
    out = []
    for tag, src in (('x', ours), ('y', other)):
        dst = os.path.join(W, '%s_%s.mp4' % (pid, tag))
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', src, '-t', '10', '-vf', 'scale=1920:1080:flags=lanczos,fps=30', '-an', '-c:v', 'libx264',
                        '-crf', '21', '-preset', 'fast', '-pix_fmt', 'yuv420p', dst], check=True)
        out.append(dst)
    return dict(id=pid, x=out[0], y=out[1], note=note)


P = []
# ours vs the matching real-game reference (same pixel size on both sides)
P.append(pair_same('river-low', R5 + '/river_low_4k.jpg', REFS + 'river-pier-golden__gr_0555.jpg', 'low river view at golden hour beside a pier and a seawall'))
P.append(pair_same('seawall-foam', R5 + '/crop_river_low_4k_seawall_foam.jpg', REFS + 'river-pier-golden__gr_0555.jpg',
                   'water meeting a seawall / pier at golden hour: the contact line (close crop against the reference pier base)',
                   w=1200, crop_y=(0, 1130, 1500, 2160)))
P.append(pair_same('harbour-high', R5 + '/harbour_high_4k.jpg', REFS + 'skyline-perch-nm__nm_0846.jpg', 'high view over the city\'s river water at golden hour, sun behind or to the side'))
P.append(pair_same('harbour-sun-high', R5 + '/harbour_sun_high_4k.jpg', REFS + 'waterfront-og__og_0244.jpg', 'high view over sunlit water at golden hour, facing the low sun'))
P.append(pair_same('river-sun', R5 + '/river_sun_4k.jpg', REFS + 'waterfront-perch-trailer__eny_0149.jpg', 'low view across a river into the low sun'))
# the merged round-03 build against this one (same camera, same pixel size)
P.append(pair_same('prev-vs-this-river-low', R5 + '/river_low_4k.jpg', R3 + '/river_low_4k.jpg', 'two builds of the same low river view'))
P.append(pair_same('prev-vs-this-seawall-foam', R5 + '/crop_river_low_4k_seawall_foam.jpg', R3 + '/crop_river_low_4k_seawall_foam.jpg', 'two builds of the same crop: water against a timber seawall', w=1200))
P.append(pair_same('prev-vs-this-harbour', R5 + '/harbour_high_4k.jpg', R3 + '/harbour_high_4k.jpg', 'two builds of the same high harbour view'))
P.append(pair_same('prev-vs-this-river-sun', R5 + '/river_sun_4k.jpg', R3 + '/river_sun_4k.jpg', 'two builds of the same low view into the sun'))
P.append(pair_video('prev-vs-this-dolly', R5 + '/river_low_dolly.mp4', R3 + '/river_low_dolly.mp4', 'two builds of the same 10 s river dolly along the seawall'))
json.dump(P, open(os.path.join(CR, 'pairs.json'), 'w'), indent=1)
pack = os.path.join(CR, 'pack')
if os.path.isdir(pack):
    import shutil
    if not os.path.realpath(pack).startswith('/Users/midir/sm2-n1/_scratch/critic-W-r05/'): sys.exit('refusing to delete ' + pack)
    shutil.rmtree(pack)
subprocess.run([sys.executable, ABPACK, pack, os.path.join(CR, 'pairs.json')], check=True, cwd=WT)
for p in P:
    a = [os.path.join(pack, p['id'], f) for f in os.listdir(os.path.join(pack, p['id']))]
    print(p['id'], [(os.path.basename(f), os.path.getsize(f) // 1024) for f in a])
