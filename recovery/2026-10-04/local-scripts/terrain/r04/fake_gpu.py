#!/usr/bin/env python3
"""dry-run stub for gpu_slot.sh: `fake_gpu.py capture --label terrain -- run_game.sh OUT [opts] [-- extra]` fabricates the artifacts run_game.sh would leave"""
import sys, os, re, random
a = sys.argv[1:]; i = a.index('--'); cmd = a[i + 1:]
out = cmd[1]; opts = cmd[2:]
def opt(n, d=None):
    return opts[opts.index(n) + 1] if n in opts else d
name = opt('-name', 'shot'); os.makedirs(out, exist_ok=True)
extra = opts[opts.index('--') + 1:] if '--' in opts else []
print('FAKE run_game', name, 'map', opt('-map'), 'res', opt('-res'), 'movie' if '-movie' in opts else '', 'extra', ' '.join(extra)[:120])
from PIL import Image
if '-shots' in opts:
    Image.new('RGB', (3840, 2160), (60, 120, 40)).save(os.path.join(out, '%s_0001.png' % name))
    open(os.path.join(out, name + '.log'), 'w').write('LogWebHomage: Display: WH_PERF fake 100.0 ms\n')
elif '-movie' in opts:
    fd = os.path.join(out, name + '_frames'); os.makedirs(fd, exist_ok=True)
    for k in range(1, 31): Image.new('RGB', (192, 108), (k * 5, 100, 50)).save(os.path.join(fd, 'MovieFrame%05d.png' % k))
    open(os.path.join(out, name + '.log'), 'w').write('WebTravWorld: fake\nWH_QUIT fake\n')
    open(os.path.join(out, name + '_telemetry.csv'), 'w').write('frame,t\n0,0\n')
else:
    open(os.path.join(out, name + '.log'), 'w').write('fake log\n')
for e in extra:
    if e.startswith('-WHTravCsv='):
        p = e.split('=', 1)[1]; os.makedirs(os.path.dirname(p), exist_ok=True)
        hdr = 'frame,t,x_m,y_m,z_m,height_above_floor_m,cam_x,cam_y'
        rows = []
        sc = random.Random(name).uniform(0.2, 1.0)
        for k in range(0, 940, 4):
            t = k / 60.0; rows.append('%d,%.4f,%.1f,%.1f,%.1f,%.1f,%.1f,%.1f' % (k, t, 250 - 25 * t * sc, -300 - 40 * t, 30, 30 if name.endswith('s3_y240_sky1_hang') else 12, 250 - 25 * t * sc, -300 - 40 * t))
        open(p, 'w').write(hdr + '\n' + '\n'.join(rows) + '\n')
