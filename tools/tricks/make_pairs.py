# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# Tricks C r01: source clips + pairs.json for the blind A/B critic pack (tools/night1/abpack.py). Everything it writes stays in _scratch
# (the owner clip is footage of the real game: local only, never committed).
#   python3 tools/tricks/make_pairs.py <reel.mp4> <reel_telemetry.csv> <traversal f4.mp4> <out dir>      -> <out dir>/pairs.json
# x = ours (tricks r01 reel excerpt, cropped around the hero to the owner clip's 610:556 aspect), y = the owner clip segment (FLIPS_SPEC
# S1 / S2 / S3 / S6), both scaled to the SAME 1220x1112; progress pairs: traversal r26 f4 vs the tricks r01 reel, both 1280x720.
import csv, json, os, statistics, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tricks_check import instances  # noqa: E402

REEL, TEL, F4, OUT = sys.argv[1:5]
OWNER = '/Users/midir/sm2-n1/_scratch/refs/owner/flips_owner_2026-09-29.mov'
W, H = 1220, 1112
os.makedirs(OUT, exist_ok=True)
T = list(csv.DictReader(open(TEL)))
I = [c for c in instances(T) if c['scale'] > 0]
# movie time of telemetry time t: the merged reel's frame 0 is sequence frame 0 (capture.sh); MOVIE_OFF (s) corrects a measured offset
OFF = float(os.environ.get('MOVIE_OFF', '0'))


def ff(*a):
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y'] + list(a), check=True)


def ours(c, name, pre=0.35, post=0.45, until=None):
    t0, t1 = c['t0'] - pre, (until if until is not None else c['t0'] + c['len']) + post
    rows = [r for r in T if t0 <= float(r['t']) <= t1 and float(r.get('px_bottom') or 0) > float(r.get('px_top') or 0)]
    cx = statistics.median((float(r['px_left']) + float(r['px_right'])) / 2 for r in rows)
    cy = statistics.median((float(r['px_top']) + float(r['px_bottom'])) / 2 for r in rows)
    hh = statistics.median(max(float(r['px_bottom']) - float(r['px_top']), float(r['px_right']) - float(r['px_left'])) for r in rows)
    ch = min(1080.0, max(420.0, hh / 0.27)); cw = ch * 610 / 556
    bx = max(0, min(1920 - cw, cx - cw / 2)); by = max(0, min(1080 - ch, cy - ch / 2))
    dst = os.path.join(OUT, 'ours_' + name + '.mp4')
    ff('-ss', '%.3f' % max(0, t0 + OFF), '-t', '%.3f' % (t1 - t0), '-i', REEL, '-an', '-vf',
       'crop=%d:%d:%d:%d,scale=%d:%d,setsar=1' % (cw, ch, bx, by, W, H), '-r', '50', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', dst)
    return dst, (t0, t1)


def owner(a, b, name):
    dst = os.path.join(OUT, 'ref_' + name + '.mp4')
    ff('-ss', '%.3f' % a, '-t', '%.3f' % (b - a), '-i', OWNER, '-an', '-vf', 'scale=%d:%d:flags=lanczos,setsar=1' % (W, H),
       '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', dst)
    return dst


def first(p, k=0):
    L = [c for c in I if c['prog'] == p]
    return L[min(k, len(L) - 1)] if L else None


pairs = []
plan = [  # id, our program (instance), owner segment (s), note
    ('single-release-flip', 'backSingle', 0, (0.80, 2.44), 'One flip off a swing release into the next web catch.'),
    ('triple-chain', 'backTripleChain', 0, (8.40, 11.36), 'Three rotations in one release, a shape per rotation.'),
    ('pike-twist-open', 'barani', 0, (21.32, 23.80), 'Piked / inverted shapes opening to an upright spread before the next catch.'),
    ('layout', 'backLayout', 0, (0.80, 2.44), 'Straight-body flip off a release.'),
    ('corkscrew-twist', 'corkscrew', 0, (8.32, 9.40), 'Twisting rotation in the air.'),
    ('inverted-pencil', 'frontPikeSwan', 0, (4.60, 5.96), 'Inverted held shape, then the unwind.'),
    ('double-tuck', 'frontDouble', 0, (8.40, 10.10), 'Fast tucked rotations.'),
]
for pid, prog, k, (a, b), note in plan:
    c = first(prog, k)
    if not c: print('no instance of', prog); continue
    x, (t0, t1) = ours(c, pid)
    y = owner(a, b, pid)
    pairs.append(dict(id=pid, x=x, y=y, note=note + ' Both %dx%d.' % (W, H)))
    print(pid, prog, 'ours t %.2f-%.2f' % (t0, t1), 'ref %.2f-%.2f' % (a, b))
# progress: traversal's merged r26 f4 flip chain vs this reel (the same lit city, 1280x720 each)
dur_f4 = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', F4], capture_output=True, text=True).stdout)
for n, (a, b) in enumerate([(0.0, dur_f4)]):
    xa = os.path.join(OUT, 'reel_%d.mp4' % n); ya = os.path.join(OUT, 'f4_%d.mp4' % n)
    ff('-ss', '%.3f' % (a + OFF), '-t', '%.3f' % (b - a), '-i', REEL, '-an', '-vf', 'scale=1280:720,setsar=1', '-c:v', 'libx264', '-crf', '20', '-pix_fmt', 'yuv420p', xa)
    ff('-ss', '%.3f' % a, '-t', '%.3f' % (min(b, dur_f4) - a), '-i', F4, '-an', '-vf', 'scale=1280:720,setsar=1', '-c:v', 'libx264', '-crf', '20', '-pix_fmt', 'yuv420p', ya)
    pairs.append(dict(id='progress-flips-%d' % (n + 1), x=xa, y=ya, note='Flip chain through the lit city, %.0f-%.0f s of each clip. Both 1280x720.' % (a, b)))
json.dump(pairs, open(os.path.join(OUT, 'pairs.json'), 'w'), indent=1)
print('pairs', len(pairs), '->', os.path.join(OUT, 'pairs.json'))
