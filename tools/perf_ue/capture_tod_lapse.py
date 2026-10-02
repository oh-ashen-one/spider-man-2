#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 05: time-lapse clip of the continuous time of day from the REAL game. One session of /Game/Tests/Look/Look_Midtown_tod, the camera parked on one
city shot pose (shot tour, Source/WebHomage/Look/WHLookTour.cpp), the clock running (-WHToD=<start> -WHToDSpeed=<h per s>), every frame dumped at a fixed
1/60 s step (run_game.sh -movie), H.264 <= 15 MB. Writes <round>/<name>.mp4 and <name>.json (per-frame mean luma / B-R and the largest frame-to-frame jump:
a continuous time of day has no steps). Goes through gpu_slot.sh capture.

(round 06) L23b instrument condition: the lapse compresses an hour into half a second, so the eye adaptation must be metered per frame: the tool pins
`pp.AutoExposureSpeedUp 40` and `pp.AutoExposureSpeedDown 40` (live `wh.ToDSet` pins, capture-only; the game's own speeds stay 6 / 3) unless --no-pin; the JSON records
the pin as `instrument_condition`. The JSON carries EVERY frame (hour, mean Y, B-R, clipped %) and the L23b checks: max / p99 / median frame-to-frame jump, the 05:00-21:30
window (frame mean <= 130, clipped <= 1.8 %) and the biggest jumps with their game hour. --keys <abs file> loads another key table (-WHToDKeys), --no-encode skips the mp4. --substeps N (round 06): render N frames per output frame so the engine's temporal lighting caches settle (see the argument help).

usage: tools/perf_ue/capture_tod_lapse.py --round docs/night1/look/round-NN --shot S4 --from 4.0 --hours 24 --seconds 12 [--res 1920x1080] [--name tod_lapse_S4]"""
import argparse, glob, json, math, os, shutil, subprocess, sys, time
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, '..', '..'))
UE = os.path.join(WT, 'unreal', 'WebHomage')
RUN_GAME = os.environ.get('WH_RUN_GAME', os.path.join(UE, 'Scripts', 'run_game.sh'))   # WH_RUN_GAME: a stand-in for the game in the CPU-only tests of the loop tooling
GPU_SLOT = os.environ.get('GPU_SLOT', '/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh')
SCR = os.path.join(os.environ.get('SM2_LOOK_SCRATCH', '/Users/midir/sm2-n1/_scratch/look'), 'lapse')
sys.path.insert(0, HERE)
from capture_tour import U, look_rot, util   # noqa: E402
PIN = 'exec wh.ToDSet pp.AutoExposureSpeedUp 40;exec wh.ToDSet pp.AutoExposureSpeedDown 40'
SKY_POSES = os.path.join(HERE, 'sky_poses.json')


def frame_stats(f):
    """(mean Y of the 480x270 resize, B-R of it, clipped % of the full-resolution frame: any channel >= 250)"""
    from PIL import Image
    import numpy as np
    img = Image.open(f).convert('RGB')
    full = np.asarray(img)
    clip = float((full.max(axis=2) >= 250).mean() * 100.0)
    im = np.asarray(img.resize((480, 270)), dtype=np.float32)
    y = 0.2126 * im[..., 0] + 0.7152 * im[..., 1] + 0.0722 * im[..., 2]
    return float(y.mean()), float(im[..., 2].mean() - im[..., 0].mean()), clip


def lapse_checks(hours, ys, clips):
    """L23b numbers from per-frame series (hours[i] = game hour of frame i)"""
    import numpy as np
    d = np.abs(np.diff(np.asarray(ys)))
    srt = np.sort(d)
    out = {'max_jump': float(srt[-1]) if len(srt) else None, 'p99_jump': float(srt[int(0.99 * (len(srt) - 1))]) if len(srt) else None, 'median_jump': float(srt[len(srt) // 2]) if len(srt) else None,
           'frames_over_3': int((d > 3.0).sum()), 'frames_over_1.5': int((d > 1.5).sum())}
    idx = [i for i, h in enumerate(hours) if 5.0 <= h <= 21.5]
    if idx:
        out['window_05_2130'] = {'max_mean_y': float(max(ys[i] for i in idx)), 'max_clipped_pct': float(max(clips[i] for i in idx)),
                                 'hour_of_max_mean': float(hours[max(idx, key=lambda i: ys[i])]), 'hour_of_max_clipped': float(hours[max(idx, key=lambda i: clips[i])])}
    top = np.argsort(-d)[:8]
    out['biggest_jumps'] = [{'hour': round(float(hours[int(i) + 1]), 3), 'jump': round(float(d[i]), 2), 'from': round(float(ys[int(i)]), 1), 'to': round(float(ys[int(i) + 1]), 1)} for i in top]
    out['pass'] = bool(out['max_jump'] is not None and out['max_jump'] <= 3.0 and out['p99_jump'] <= 1.5 and 'window_05_2130' in out and out['window_05_2130']['max_mean_y'] <= 130.0
                       and out['window_05_2130']['max_clipped_pct'] <= 1.8)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--round', required=True); ap.add_argument('--shot', default='S4'); ap.add_argument('--from', dest='h0', type=float, default=4.0)
    ap.add_argument('--hours', type=float, default=24.0); ap.add_argument('--seconds', type=float, default=12.0); ap.add_argument('--res', default='1920x1080')
    ap.add_argument('--name', default=''); ap.add_argument('--sp', default='100'); ap.add_argument('--weather', default='-1'); ap.add_argument('--cmds', default='', help="';'-separated live tour commands before the pose, e.g. 'exec wh.ToDSet pp.AutoExposureSpeedUp 40'"); ap.add_argument('--timeout', type=int, default=5000)
    ap.add_argument('--no-pin', action='store_true', help='do NOT pin the metering speed (round-05 behaviour, eye adaptation lags the clock)'); ap.add_argument('--keys', default='', help='abs path of a key table to load instead of the baked one (-WHToDKeys)')
    ap.add_argument('--freeze', type=float, default=0.0, help='(round 06 diagnostic) extra game seconds with the clock STOPPED after the lapse (wh.TimeOfDaySpeed 0 through a second pose): shows how long the lighting lags a change; frames after the freeze keep their (frozen) hour')
    ap.add_argument('--save-frames', default='', help="e.g. '440:452,66:78': keep these frames (index in the lapse) as jpgs in <round>/<name>_frames_kept/ (diagnosing a step)")
    ap.add_argument('--substeps', type=int, default=1, help="(round 06) render N frames per output frame: the clock advances 1/N of the output step per rendered frame (fixed 1/60 s step) and every Nth frame is kept, so the engine's temporal lighting caches (Lumen GI, sky light capture, volumetric fog history; ~35 frames) settle between two kept frames. N=4 turns the 2 h/s lapse into a 0.5 h/s render with the same 724 output frames; the lapse json records it as the instrument condition")
    ap.add_argument('--no-encode', action='store_true'); ap.add_argument('--pose-file', default='', help='extra pose file (json like city_shots.json); the sky poses of tools/perf_ue/sky_poses.json are always known')
    a = ap.parse_args()
    rnd = os.path.abspath(a.round); os.makedirs(rnd, exist_ok=True)
    poses = json.load(open(os.path.join(UE, 'Scripts', 'city_shots.json'))) + json.load(open(SKY_POSES)) + (json.load(open(a.pose_file)) if a.pose_file else [])
    s = next(x for x in poses if x['id'].split('_')[0] == a.shot)
    cmds = ';'.join(c for c in (PIN if not a.no_pin else '', a.cmds) if c)
    name = a.name or 'tod_lapse_%s' % a.shot
    START = 1.0                       # game s: camera parked on the pose; frames before it are trimmed
    N = max(1, a.substeps)
    out_rate = a.hours / a.seconds    # game hours per OUTPUT second (the lapse's nominal rate)
    rate = out_rate / N               # game hours per game second the engine really runs (N > 1: sub-stepped lapse)
    gsec = a.seconds * N              # game seconds rendered
    h_start = (a.h0 - rate * START) % 24.0
    d = os.path.join(SCR, name); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    p, t = U(*s['pos']), U(*s['target']); r = look_rot(p, t); pl = s.get('player') or s['pos']; hh = U(pl[0], pl[1] + 1.0, pl[2])
    tf = os.path.join(d, 'tour.txt')
    pre = ''.join('! %s\n' % c.strip() for c in cmds.split(';') if c.strip())   # e.g. faster eye adaptation: the lapse compresses 1 h into 0.5 s
    pose = '%s %.1f %.1f %.1f %.4f %.4f %.4f %.2f %%.1f 0 %.1f %.1f %.1f\n' % (a.shot, p[0], p[1], p[2], r[0], r[1], r[2], s.get('fov', 70), hh[0], hh[1], hh[2])
    if a.freeze > 0: open(tf, 'w').write(pre + pose % gsec + '! cvar wh.TimeOfDaySpeed 0\n' + (pose % (a.freeze + 30.0)).replace(a.shot + ' ', a.shot + 'b ', 1))
    else: open(tf, 'w').write(pre + pose % (gsec + 30.0))
    u = util(); t0 = time.time()
    cmd = [RUN_GAME, d, '-map', '/Game/Tests/Look/Look_Midtown_tod', '-res', a.res, '-quit', '%.2f' % (START + gsec + a.freeze + 0.1 + 0.07 * N), '-name', name, '-movie',
           '-timeout', str(a.timeout), '-exec', 'r.ScreenPercentage %s' % a.sp,
           '--', '-WHLookTour=' + tf, '-WHLookTourDir=' + d, '-WHLookTourStart=%.2f' % START, '-WHLookTourMinFrames=1',
           '-WHToD=%.4f' % h_start, '-WHToDSpeed=%.6f' % rate, '-WHWeather=' + a.weather] + (['-WHToDKeys=' + os.path.abspath(a.keys)] if a.keys else [])
    rr = subprocess.run(([GPU_SLOT, 'capture', '--label', 'look', '--'] if os.path.exists(GPU_SLOT) else []) + cmd, capture_output=True, text=True)
    fr = os.path.join(d, name + '_frames')
    frames = sorted(glob.glob(fr + '/MovieFrame*.png'))
    if not frames: print('FAILED', rr.stdout[-800:], rr.stderr[-400:]); sys.exit(1)
    skip = int(round(START * 60)) + 3
    allkeep = frames[skip:]
    keep = allkeep[::N]               # N > 1: every Nth rendered frame is an output frame (the frames in between only let the lighting caches settle)
    from PIL import Image
    import numpy as np
    with ProcessPoolExecutor(max_workers=6) as ex: res_f = list(ex.map(frame_stats, keep, chunksize=8))
    ys = [r[0] for r in res_f]; brs = [r[1] for r in res_f]; cl = [r[2] for r in res_f]
    tmax = gsec * 60.0   # frames after the freeze keep the hour they froze at
    hrs = [(a.h0 + rate * min(3 + i * N, tmax) / 60.0) % 24.0 for i in range(len(keep))]   # keep[0] is frame START*60+3 of the dump: 3 frames after the pose was entered
    jumps = [abs(ys[i + 1] - ys[i]) for i in range(len(ys) - 1)]
    chk = lapse_checks(hrs, ys, cl)
    out = os.path.join(rnd, name + '.mp4')
    if a.no_encode: out = os.path.join(d, name + '.mp4')
    seld = fr + '_sel'; shutil.rmtree(seld, ignore_errors=True); os.makedirs(seld)    # the kept frames, numbered contiguously (symlinks)
    for i, f in enumerate(keep): os.symlink(os.path.abspath(f), os.path.join(seld, 'f%05d.png' % i))
    def enc(extra):
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-framerate', '60', '-i', seld + '/f%05d.png', '-frames:v', str(len(keep)),
                        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-movflags', '+faststart'] + extra + [out])
    if not a.no_encode: enc(['-crf', '19'])
    if not a.no_encode and os.path.getsize(out) > 15_000_000:
        kbps = int(14.5e6 * 8 / 1000 / (len(keep) / 60.0))
        enc(['-preset', 'slow', '-b:v', '%dk' % kbps, '-maxrate', '%dk' % kbps, '-bufsize', '%dk' % (kbps * 2)])
    j = sorted(jumps)
    res = {'clip': os.path.basename(out), 'map': '/Game/Tests/Look/Look_Midtown_tod', 'shot': s['id'], 'output': a.res, 'internal': '%s%% of output' % a.sp,
           'hours': [a.h0, (a.h0 + a.hours) % 24.0], 'rate_h_per_s': out_rate, 'clock_rate_rendered_h_per_s': rate, 'substeps': N, 'frames': len(keep),
           'rendered_frames': len(allkeep), 'time_step': 'fixed 1/60 s (-benchmark -fps=60 -dumpmovie)' + ('' if N == 1 else '; the clock runs at %g h/s and every %d-th rendered frame is kept (a %g h/s lapse: one output frame = %.1f game minutes)' % (rate, N, out_rate, out_rate)),
           'weather': a.weather, 'live_cmds': cmds, 'instrument_condition': (('metering pinned per frame: pp.AutoExposureSpeedUp / Down = 40 (capture-only live pins; the game keeps 6 / 3)' if not a.no_pin else 'metering NOT pinned (game speeds 6 / 3)')
                                   + ('' if N == 1 else ' + sub-stepped render: %d frames per output frame (clock %g h/s, fixed 1/60 s step, every %d-th frame kept) so the temporal lighting caches (Lumen GI, sky light capture, volumetric fog history, ~35 frames) settle between output frames; no render setting is changed' % (N, rate, N))
                                   + ((' + render settings while the clock runs > 0.3 h/s (wh.ToDLapseCvars, the sky light capture and the volumetric fog history have a ~35 frame latency = 0.6 game hour at 2 h/s): ' + [c for c in cmds.split(';') if 'ToDLapseCvars' in c][0].split('ToDLapseCvars', 1)[1].strip()) if 'ToDLapseCvars' in cmds else '')),
           'keys': a.keys or 'baked into Look_Rig_tod', 'gpu_util_before_pct': u, 'wall_s': round(time.time() - t0), 'bytes': os.path.getsize(out) if os.path.exists(out) else 0,
           'frame_to_frame_mean_y_jump': {'max': round(j[-1], 3) if j else None, 'p99': round(j[int(0.99 * (len(j) - 1))], 3) if j else None, 'median': round(j[len(j) // 2], 3) if j else None},
           'checks_L23b': chk, 'hours_per_frame': [round(h, 4) for h in hrs], 'mean_y_per_frame': [round(v, 2) for v in ys], 'b_minus_r_per_frame': [round(v, 2) for v in brs], 'clipped_pct_per_frame': [round(v, 3) for v in cl]}
    json.dump(res, open(os.path.join(rnd, name + '.json'), 'w'), indent=1)
    if a.save_frames:
        kd = os.path.join(rnd, name + '_frames_kept'); os.makedirs(kd, exist_ok=True)
        for rg in a.save_frames.split(','):
            lo, hi = (int(x) for x in rg.split(':'))
            for i in range(max(0, lo), min(len(keep), hi + 1)):
                Image.open(keep[i]).convert('RGB').save(os.path.join(kd, 'f%04d_h%.3f.jpg' % (i, hrs[i])), quality=90)
    # contact sheet: 8 frames across the lapse (for the critic and the handoff)
    picks = [keep[int(k * (len(keep) - 1) / 7)] for k in range(8)]
    ims = [Image.open(f).convert('RGB').resize((480, 270)) for f in picks]
    sheet = Image.new('RGB', (480 * 4, 270 * 2))
    for k, im in enumerate(ims): sheet.paste(im, ((k % 4) * 480, (k // 4) * 270))
    sheet.save(os.path.join(rnd, name + '_sheet.jpg'), quality=88)
    shutil.rmtree(fr, ignore_errors=True); shutil.rmtree(seld, ignore_errors=True)
    print('lapse', name, (os.path.getsize(out) // 1024) if os.path.exists(out) else 0, 'KB', len(keep), 'frames', 'max jump %.2f Y  p99 %.2f  05-21:30 max mean %.1f max clipped %.2f %%  L23b %s' % (
        j[-1] if j else -1, chk['p99_jump'], chk.get('window_05_2130', {}).get('max_mean_y', -1), chk.get('window_05_2130', {}).get('max_clipped_pct', -1), 'PASS' if chk['pass'] else 'fail'), flush=True)


if __name__ == '__main__':
    main()
