#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 06, hold 8: a 24 h lapse (S4 perch, nominal 2 h/s, 720 output frames of 2 game minutes) rendered as SEGMENTS with different render sub-steps, stitched into one clip + one json.
Why: a sub-stepped x4 lapse (clock 0.5 h/s) still lags the settled lighting by 20-40 Y at 19:48-20:30 (hold 7: lapse 54.6 against a settled still 15.0 at 19:48; x1 and x2 are worse): the engine's temporal
lighting caches need ~12 rendered frames to follow, and the twilights change by 4 Y per output frame. The twilights are therefore rendered at x16 (0.125 h/s: the lag is under one output frame, <= ~3 Y), the
slow day and night parts at x4. Every segment starts `drop` game hours earlier than its nominal start (a warm-up of the caches and the metering) and drops those frames.
usage: lapse_stitch.py --round docs/night1/look/round-06 --name tod_lapse_S4 [--keys <abs key file>] [--res 960x540]
        [--segments "3.7:1.8:4:0.3,5.2:3.0:16:0.3,7.9:10.5:4:0.3,18.1:3.3:16:0.3,21.1:6.9:4:0.3"]    (from : hours : substeps : drop-hours; the nominal segments are 04:00-05:30, 05:30-08:30 ... see below)
Writes <round>/<name>.mp4 / .json / _sheet.jpg (`segments`, `substeps_per_segment`, `instrument_condition` in the json)."""
import argparse, json, os, shutil, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import capture_tod_lapse as C   # noqa: E402
DEFAULT = "3.7:1.8:4:0.3,5.2:3.0:16:0.3,7.9:10.5:4:0.3,18.1:3.3:16:0.3,21.1:6.9:4:0.3"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--round', required=True); ap.add_argument('--name', default='tod_lapse_S4'); ap.add_argument('--keys', default=''); ap.add_argument('--res', default='960x540')
    ap.add_argument('--segments', default=DEFAULT); ap.add_argument('--timeout', type=int, default=900); ap.add_argument('--shot', default='S4'); ap.add_argument('--cmds', default='')
    ap.add_argument('--reuse', action='store_true', help='(round 07) keep the work dir and reuse segments already rendered there (a lapse split over two GPU holds of the SAME build); the json says which were reused')
    ap.add_argument('--deadline', type=float, default=0.0, help='unix time: segments that cannot finish before it are not started (the stitched json then says so)')
    a = ap.parse_args()
    rnd = os.path.abspath(a.round); os.makedirs(rnd, exist_ok=True)
    work = os.path.join(os.environ.get('SM2_LOOK_SCRATCH', '/Users/midir/sm2-n1/_scratch/look'), 'lapse_stitch', a.name); (None if a.reuse else shutil.rmtree(work, ignore_errors=True)); os.makedirs(work, exist_ok=True)
    segs = []
    for sp in a.segments.split(','):
        f, h, n, dr = sp.split(':'); segs.append((float(f), float(h), int(n), float(dr)))
    hrs, ys, brs, cls = [], [], [], []; mp4s = []; info = []; t0 = time.time(); live = ''
    for k, (f, h, n, dr) in enumerate(segs):
        nm = 'seg%d' % k; rd = os.path.join(work, nm)
        est = h / 2.0 * 60.0 * n * float(os.environ.get('LAPSE_SPF', '0.09')) + 45.0     # s: rendered frames x 0.09 s (LAPSE_SPF: measured s per rendered frame, 0.6 under a loaded machine) + start-up
        jp0 = os.path.join(rd, nm + '.json'); reused = a.reuse and os.path.exists(jp0)
        if not reused and a.deadline and time.time() + est > a.deadline: print('stitch: deadline, not starting segment', k, flush=True); break
        cmd = [sys.executable, os.path.join(HERE, 'capture_tod_lapse.py'), '--shot', a.shot, '--res', a.res, '--round', rd, '--name', nm, '--from', '%g' % f, '--hours', '%g' % h, '--seconds', '%g' % (h / 2.0),
               '--substeps', str(n), '--drop-first-hours', '%g' % dr, '--trim-end', '--timeout', str(a.timeout)] + (['--keys', os.path.abspath(a.keys)] if a.keys else []) + (['--cmds', a.cmds] if a.cmds else [])
        if reused: print('stitch: segment', k, 'reused from', rd, flush=True)
        else: r = subprocess.run(cmd, capture_output=True, text=True); print(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-300:], flush=True)
        jp = os.path.join(rd, nm + '.json')
        if not os.path.exists(jp): print('stitch: segment', k, 'failed'); sys.exit(2)
        d = json.load(open(jp)); live = d.get('live_cmds', live)
        hrs += d['hours_per_frame']; ys += d['mean_y_per_frame']; brs += d['b_minus_r_per_frame']; cls += d['clipped_pct_per_frame']; mp4s.append(os.path.join(rd, nm + '.mp4'))
        info.append({'from': f, 'hours': h, 'substeps': n, 'drop_first_hours': dr, 'frames_kept': d['frames'], 'rendered_frames': d.get('rendered_frames'), 'max_jump_inside': d['frame_to_frame_mean_y_jump']['max'], 'reused_from_earlier_hold': bool(reused)})
    chk = C.lapse_checks(hrs, ys, cls)
    out = os.path.join(rnd, a.name + '.mp4')
    lst = os.path.join(work, 'list.txt'); open(lst, 'w').write(''.join("file '%s'\n" % m for m in mp4s))
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', '-movflags', '+faststart', out])
    if os.path.exists(out) and os.path.getsize(out) > 15_000_000:
        dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', out], capture_output=True, text=True).stdout)
        kb = int(14.5e6 * 8 / 1000 / dur); tmp = out + '.tmp.mp4'
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', out, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'slow', '-b:v', '%dk' % kb, '-maxrate', '%dk' % kb, '-bufsize', '%dk' % (2 * kb), tmp]); os.replace(tmp, out)
    j = sorted(abs(ys[i + 1] - ys[i]) for i in range(len(ys) - 1))
    res = {'clip': os.path.basename(out), 'map': '/Game/Tests/Look/Look_Midtown_tod', 'shot': a.shot, 'output': a.res, 'internal': '100% of output', 'hours': [4.0, 4.0], 'rate_h_per_s': 2.0, 'frames': len(ys), 'segments': info,
           'time_step': 'fixed 1/60 s (-benchmark -fps=60 -dumpmovie) per segment; the clock runs at 2/N h/s (N = substeps of the segment) and every N-th rendered frame is kept',
           'live_cmds': live, 'keys': a.keys or 'baked into Look_Rig_tod', 'wall_s': round(time.time() - t0), 'bytes': os.path.getsize(out) if os.path.exists(out) else 0,
           'instrument_condition': ('metering pinned per frame: pp.AutoExposureSpeedUp / Down = 40 (capture-only live pins; the game keeps 6 / 3) + segmented sub-stepped render: ' + '; '.join('%g-%g h x%d' % (s['from'] + s['drop_first_hours'], s['from'] + s['hours'], s['substeps']) for s in info)
                                    + ' (each segment starts %s h early and drops those frames: warm-up of the lighting caches); x16 = clock 0.125 h/s, x4 = 0.5 h/s, fixed 1/60 s step, every N-th frame kept; no render setting is changed' % ('/'.join('%g' % s['drop_first_hours'] for s in info[:1]))),
           'frame_to_frame_mean_y_jump': {'max': round(j[-1], 3), 'p99': round(j[int(0.99 * (len(j) - 1))], 3), 'median': round(j[len(j) // 2], 3)}, 'checks_L23b': chk,
           'hours_per_frame': [round(h % 24.0, 4) for h in hrs], 'mean_y_per_frame': [round(v, 2) for v in ys], 'b_minus_r_per_frame': [round(v, 2) for v in brs], 'clipped_pct_per_frame': [round(v, 3) for v in cls]}
    json.dump(res, open(os.path.join(rnd, a.name + '.json'), 'w'), indent=1)
    # contact sheet: 8 frames across the clip
    try:
        from PIL import Image
        dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', out], capture_output=True, text=True).stdout)
        ims = []
        for k in range(8):
            fp = os.path.join(work, 'sheet%d.png' % k)
            subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', '%.3f' % (dur * k / 8.0 + 0.01), '-i', out, '-frames:v', '1', fp])
            ims.append(Image.open(fp).convert('RGB').resize((480, 270)))
        sheet = Image.new('RGB', (480 * 4, 270 * 2))
        for k, im in enumerate(ims): sheet.paste(im, ((k % 4) * 480, (k // 4) * 270))
        sheet.save(os.path.join(rnd, a.name + '_sheet.jpg'), quality=88)
    except Exception as e:
        print('sheet failed', e)
    print('stitched', a.name, len(ys), 'frames max jump %.2f p99 %.2f  05-21:30 max mean %.1f max clipped %.2f %%  L23b %s' % (res['frame_to_frame_mean_y_jump']['max'], res['frame_to_frame_mean_y_jump']['p99'],
          chk.get('window_05_2130', {}).get('max_mean_y', -1), chk.get('window_05_2130', {}).get('max_clipped_pct', -1), 'PASS' if chk['pass'] else 'fail'), flush=True)


if __name__ == '__main__':
    main()
