#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 05: time-lapse clip of the continuous time of day from the REAL game. One session of /Game/Tests/Look/Look_Midtown_tod, the camera parked on one
city shot pose (shot tour, Source/WebHomage/Look/WHLookTour.cpp), the clock running (-WHToD=<start> -WHToDSpeed=<h per s>), every frame dumped at a fixed
1/60 s step (run_game.sh -movie), H.264 <= 15 MB. Writes <round>/<name>.mp4 and <name>.json (per-frame mean luma / B-R and the largest frame-to-frame jump:
a continuous time of day has no steps). Goes through gpu_slot.sh capture.

usage: tools/perf_ue/capture_tod_lapse.py --round docs/night1/look/round-NN --shot S4 --from 4.0 --hours 24 --seconds 12 [--res 1920x1080] [--name tod_lapse_S4]"""
import argparse, glob, json, math, os, shutil, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, '..', '..'))
UE = os.path.join(WT, 'unreal', 'WebHomage')
RUN_GAME = os.path.join(UE, 'Scripts', 'run_game.sh')
GPU_SLOT = os.environ.get('GPU_SLOT', '/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh')
SCR = os.path.join(os.environ.get('SM2_LOOK_SCRATCH', '/Users/midir/sm2-n1/_scratch/look'), 'lapse')
sys.path.insert(0, HERE)
from capture_tour import U, look_rot, util   # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--round', required=True); ap.add_argument('--shot', default='S4'); ap.add_argument('--from', dest='h0', type=float, default=4.0)
    ap.add_argument('--hours', type=float, default=24.0); ap.add_argument('--seconds', type=float, default=12.0); ap.add_argument('--res', default='1920x1080')
    ap.add_argument('--name', default=''); ap.add_argument('--sp', default='100'); ap.add_argument('--weather', default='-1'); ap.add_argument('--cmds', default='', help="';'-separated live tour commands before the pose, e.g. 'exec wh.ToDSet pp.AutoExposureSpeedUp 40'"); ap.add_argument('--timeout', type=int, default=5000)
    a = ap.parse_args()
    rnd = os.path.abspath(a.round); os.makedirs(rnd, exist_ok=True)
    s = next(x for x in json.load(open(os.path.join(UE, 'Scripts', 'city_shots.json'))) if x['id'].split('_')[0] == a.shot)
    name = a.name or 'tod_lapse_%s' % a.shot
    START = 1.0                       # game s: camera parked on the pose; frames before it are trimmed
    rate = a.hours / a.seconds        # game hours per game second
    h_start = (a.h0 - rate * START) % 24.0
    d = os.path.join(SCR, name); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    p, t = U(*s['pos']), U(*s['target']); r = look_rot(p, t); pl = s.get('player') or s['pos']; hh = U(pl[0], pl[1] + 1.0, pl[2])
    tf = os.path.join(d, 'tour.txt')
    pre = ''.join('! %s\n' % c.strip() for c in a.cmds.split(';') if c.strip())   # e.g. faster eye adaptation: the lapse compresses 1 h into 0.5 s
    open(tf, 'w').write(pre + '%s %.1f %.1f %.1f %.4f %.4f %.4f %.2f %.1f 0 %.1f %.1f %.1f\n' % (a.shot, p[0], p[1], p[2], r[0], r[1], r[2], s.get('fov', 70), a.seconds + 30.0, hh[0], hh[1], hh[2]))
    u = util(); t0 = time.time()
    cmd = [RUN_GAME, d, '-map', '/Game/Tests/Look/Look_Midtown_tod', '-res', a.res, '-quit', '%.2f' % (START + a.seconds + 0.1), '-name', name, '-movie',
           '-timeout', str(a.timeout), '-exec', 'r.ScreenPercentage %s' % a.sp,
           '--', '-WHLookTour=' + tf, '-WHLookTourDir=' + d, '-WHLookTourStart=%.2f' % START, '-WHLookTourMinFrames=1',
           '-WHToD=%.4f' % h_start, '-WHToDSpeed=%.6f' % rate, '-WHWeather=' + a.weather]
    rr = subprocess.run(([GPU_SLOT, 'capture', '--label', 'look', '--'] if os.path.exists(GPU_SLOT) else []) + cmd, capture_output=True, text=True)
    fr = os.path.join(d, name + '_frames')
    frames = sorted(glob.glob(fr + '/MovieFrame*.png'))
    if not frames: print('FAILED', rr.stdout[-800:], rr.stderr[-400:]); sys.exit(1)
    skip = int(round(START * 60)) + 3
    keep = frames[skip:]
    from PIL import Image
    import numpy as np
    stats = []
    prev = None; jumps = []
    for i, f in enumerate(keep):
        im = np.asarray(Image.open(f).convert('RGB').resize((480, 270)), dtype=np.float32)
        y = 0.2126 * im[..., 0] + 0.7152 * im[..., 1] + 0.0722 * im[..., 2]
        m = float(y.mean()); br = float(im[..., 2].mean() - im[..., 0].mean())
        stats.append({'frame': i, 'hour': round((a.h0 + rate * i / 60.0) % 24.0, 4), 'mean_y': round(m, 2), 'b_minus_r': round(br, 2)})
        if prev is not None: jumps.append(abs(m - prev))
        prev = m
    out = os.path.join(rnd, name + '.mp4')
    def enc(extra):
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-framerate', '60', '-start_number', str(skip), '-i', fr + '/MovieFrame%05d.png', '-frames:v', str(len(keep)),
                        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-movflags', '+faststart'] + extra + [out])
    enc(['-crf', '19'])
    if os.path.getsize(out) > 15_000_000:
        kbps = int(14.5e6 * 8 / 1000 / (len(keep) / 60.0))
        enc(['-preset', 'slow', '-b:v', '%dk' % kbps, '-maxrate', '%dk' % kbps, '-bufsize', '%dk' % (kbps * 2)])
    j = sorted(jumps)
    res = {'clip': os.path.basename(out), 'map': '/Game/Tests/Look/Look_Midtown_tod', 'shot': s['id'], 'output': a.res, 'internal': '%s%% of output' % a.sp,
           'hours': [a.h0, (a.h0 + a.hours) % 24.0], 'rate_h_per_s': rate, 'frames': len(keep), 'time_step': 'fixed 1/60 s (-benchmark -fps=60 -dumpmovie)',
           'weather': a.weather, 'live_cmds': a.cmds, 'gpu_util_before_pct': u, 'wall_s': round(time.time() - t0), 'bytes': os.path.getsize(out),
           'frame_to_frame_mean_y_jump': {'max': round(j[-1], 3) if j else None, 'p99': round(j[int(0.99 * (len(j) - 1))], 3) if j else None, 'median': round(j[len(j) // 2], 3) if j else None},
           'per_frame': stats[::6]}
    json.dump(res, open(os.path.join(rnd, name + '.json'), 'w'), indent=1)
    # contact sheet: 8 frames across the lapse (for the critic and the handoff)
    picks = [keep[int(k * (len(keep) - 1) / 7)] for k in range(8)]
    ims = [Image.open(f).convert('RGB').resize((480, 270)) for f in picks]
    sheet = Image.new('RGB', (480 * 4, 270 * 2))
    for k, im in enumerate(ims): sheet.paste(im, ((k % 4) * 480, (k // 4) * 270))
    sheet.save(os.path.join(rnd, name + '_sheet.jpg'), quality=88)
    shutil.rmtree(fr, ignore_errors=True)
    print('lapse', name, os.path.getsize(out) // 1024, 'KB', len(keep), 'frames', 'max jump %.2f Y' % (j[-1] if j else -1), flush=True)


if __name__ == '__main__':
    main()
