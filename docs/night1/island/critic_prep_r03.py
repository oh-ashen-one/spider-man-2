#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# Island (A) round 03 blind critic pack inputs (M2 whole island): trims our route clips (run_game 29 Mbps masters, 1920x1080 60 fps) to
# the reference clip lengths, downscales 3840x2160 stills where the other side is 1080p, writes pairs.json. Only captures made THIS round
# (mtime after R03_T0) are used; a missing one leaves its pair out (printed).
#   python3 docs/night1/island/critic_prep_r03.py
#   python3 /Users/midir/spider-man-2-astra6/tools/night1/abpack.py /Users/midir/sm2-n1/_scratch/critic-A-r03/pack /Users/midir/sm2-n1/_scratch/critic-A-r03/pairs.json
import json, os, subprocess, time
BASE = '/Users/midir/sm2-n1/_scratch/critic-A-r03'
OUT = BASE + '/src'
os.makedirs(OUT, exist_ok=True)
R = '/Users/midir/sm2-n1/island/docs/night1/island/round-03'
M = '/Users/midir/sm2-n1/_scratch/island/capture'
REF = '/Users/midir/spiderman-learnings/refs'
PREV_R2 = '/Users/midir/sm2-n1/island/docs/night1/island/round-02/r2_south_avenue.mp4'   # round-02 build (M1), same route start
R03_T0 = time.mktime((2026, 10, 2, 5, 0, 0, 0, 0, -1))


def ff(*a): subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', *a], check=True)


def fresh(p): return p and os.path.exists(p) and os.path.getmtime(p) >= R03_T0


def clip(name, t0, dur):
    src = os.path.join(M, name, name + '.mp4')
    if not fresh(src): return None
    o = os.path.join(OUT, '%s_%gs.mp4' % (name, t0))
    ff('-ss', str(t0), '-i', src, '-t', str(dur), '-an', '-c:v', 'libx264', '-crf', '18', '-preset', 'fast', '-pix_fmt', 'yuv420p', o)
    return o


def clip_file(src, tag, t0, dur):
    o = os.path.join(OUT, tag + '.mp4')
    ff('-ss', str(t0), '-i', src, '-t', str(dur), '-an', '-c:v', 'libx264', '-crf', '18', '-preset', 'fast', '-pix_fmt', 'yuv420p', o)
    return o


def still(src, tag, w=1920, need_fresh=True):
    if not os.path.exists(src) or (need_fresh and not fresh(src)): return None
    o = os.path.join(OUT, tag + '.jpg'); ff('-i', src, '-vf', 'scale=%d:-2' % w, '-q:v', '2', o); return o


P = [
    {'id': 'v1-street-start', 'x': clip('r1_north_avenue', 0.0, 8.0), 'y': REF + '/traversal/clips/swing-start-from-street__og_0000-0008.mp4',
     'note': 'movement, 8 s: from a run on the avenue sidewalk into the first web swings up the avenue'},
    {'id': 'v2-avenue-chain-late', 'x': clip('r2_south_avenue', 18.0, 8.0), 'y': REF + '/traversal/clips/swing-avenue-traffic__dn_0949-0957.mp4',
     'note': 'movement, 8 s: a long swing chain far down an avenue (street level below: lanes, paint, cars, sidewalks)'},
    {'id': 'v3-crosstown', 'x': clip('r3_crosstown_east', 9.0, 8.0), 'y': REF + '/traversal/clips/swing-canyon-chase__nm_0139-0147.mp4',
     'note': 'movement, 8 s: swinging along a narrower cross street between mid-rise blocks'},
    {'id': 'v4-wallrun-roofs', 'x': clip('r4_wallrun_roofs', 0.0, 10.0), 'y': REF + '/traversal/clips/wallrun-empire__nm_0003-0013.mp4',
     'note': 'movement, 10 s: swing into a facade, wall-run up it, over the top onto the roofs'},
    {'id': 's1-perch-north', 'x': still(R + '/stills/a1_high_north_00_t000.6_3840x2160.jpg', 'a1_north_3840', 3840), 'y': REF + '/streets/skyline-perch-dn__dn_1438.jpg',
     'note': 'still, 3840x2160: high view looking up the island; does the city read as continuous detailed city to the horizon'},
    {'id': 's2-aerial-south', 'x': still(R + '/stills/a1_high_south_00_t000.6_3840x2160.jpg', 'a1_south_3840', 3840), 'y': REF + '/streets/skyline-queens-aerial__gr_0033.jpg',
     'note': 'still, 3840x2160: high view over the towers looking down the island'},
    {'id': 's3-avenue-late', 'x': still(R + '/stills/r2_south_avenue_t26s_1920x1080.jpg', 'r2_t26'), 'y': still(REF + '/streets/street-avenue-hero-taxis__og_0000.jpg', 'ref_avenue_taxis', need_fresh=False),
     'note': 'still, 1920x1080: over an avenue far from the start; road surface, lane paint, cars, sidewalks below'},
    {'id': 's4-rooftops', 'x': still(R + '/stills/r4_wallrun_roofs_t20s_1920x1080.jpg', 'r4_t20'), 'y': still(REF + '/streets/rooftops-watertowers-golden__nm_0314.jpg', 'ref_rooftops', need_fresh=False),
     'note': 'still, 1920x1080: hero on / just above mid-rise roofs (water tanks, bulkheads)'},
    {'id': 'p1-previous-vs-this', 'x': clip('r2_south_avenue', 18.0, 10.0), 'y': clip_file(PREV_R2, 'r2_prev_r02_18s', 18.0, 10.0),
     'note': 'movement, 10 s: two builds of the same game, same start and the same held swing input (this build re-presses after 0.3 s, the other after 0.8 s), '
             '18-28 s into a chain down one avenue: which one keeps swinging on drawn buildings over a dressed street'},
]
skipped = [p['id'] for p in P if not (p['x'] and os.path.exists(p['x']) and p['y'] and os.path.exists(p['y']))]
P = [p for p in P if p['id'] not in skipped]
if skipped: print('pairs left out (capture missing):', skipped)
json.dump(P, open(BASE + '/pairs.json', 'w'), indent=1)
print('pairs', len(P))
