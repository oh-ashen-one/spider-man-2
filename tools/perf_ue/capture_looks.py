#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 capture driver for the critic: every city shot view (Scripts/city_shots.json S1..S8) under each time-of-day preset at
3840x2160 and 1920x1080 (stills, from the RUNNING game: Scripts/run_game.sh, offscreen -game), plus one 60 fps swing-chain clip
per preset (fixed 1/60 s step, every frame dumped, H.264 <= 15 MB). Heavy frames go to the scratch dir, the round folder gets
JPEGs, mp4s and NOTES.md (neutral facts only: preset, camera, output size, internal resolution).

usage: tools/perf_ue/capture_looks.py --round docs/night1/look/round-01 [--presets midday,golden,night] [--shots S1,S2,...]
         [--res 3840x2160,1920x1080] [--shot-times 12,20] [--clips] [--clip-seconds 12] [--no-stills]"""
import argparse, json, os, re, shutil, subprocess, sys, time, glob

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, '..', '..'))
UE = os.path.join(WT, 'unreal', 'WebHomage')
RUN_GAME = os.path.join(UE, 'Scripts', 'run_game.sh')
SCR = '/Users/midir/sm2-n1/_scratch/look/capture'

def util():
    s = subprocess.run("ioreg -r -d 1 -w 0 -c IOAccelerator | grep -o '\"Device Utilization %\"=[0-9]*'", shell=True, capture_output=True, text=True).stdout
    m = re.findall(r'=(\d+)', s); return int(m[0]) if m else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--round', required=True); ap.add_argument('--presets', default='midday,golden,night')
    ap.add_argument('--shots', default=''); ap.add_argument('--res', default='3840x2160,1920x1080')
    ap.add_argument('--shot-times', default='12,20'); ap.add_argument('--clips', action='store_true'); ap.add_argument('--no-stills', action='store_true')
    ap.add_argument('--clip-seconds', type=float, default=12.0); ap.add_argument('--sp', default='100', help='r.ScreenPercentage for the captures')
    ap.add_argument('--jpeg-q', type=int, default=90)
    a = ap.parse_args()
    rnd = os.path.abspath(a.round); os.makedirs(rnd + '/stills', exist_ok=True); os.makedirs(SCR, exist_ok=True)
    shots = json.load(open(os.path.join(UE, 'Scripts', 'city_shots.json')))
    want = [s for s in a.shots.split(',') if s]
    notes = []
    times = [float(t) for t in a.shot_times.split(',')]
    if not a.no_stills:
        for preset in a.presets.split(','):
            for s in shots:
                sid = s['id'].split('_')[0]
                if want and sid not in want: continue
                for res in a.res.split(','):
                    name = '%s_%s_%s' % (preset, sid, res)
                    d = os.path.join(SCR, name); shutil.rmtree(d, ignore_errors=True)
                    u = util(); t0 = time.time()
                    cmd = [RUN_GAME, d, '-map', '/Game/Tests/Look/Look_View_%s_%s' % (preset, sid), '-res', res, '-shots', a.shot_times, '-name', name,
                           '-timeout', '900', '-exec', 'r.ScreenPercentage %s' % a.sp]
                    r = subprocess.run(cmd, capture_output=True, text=True)
                    pngs = sorted(glob.glob(d + '/*.png'))
                    if not pngs: print('FAILED', name, r.stdout[-400:], r.stderr[-400:]); continue
                    last = pngs[-1]
                    out = '%s/stills/%s.jpg' % (rnd, name)
                    subprocess.run(['sips', '-s', 'format', 'jpeg', '-s', 'formatOptions', str(a.jpeg_q), last, '--out', out], capture_output=True)
                    notes.append({'kind': 'still', 'file': os.path.relpath(out, rnd), 'preset': preset, 'view': s['id'], 'desc': s['desc'], 'output': res,
                                  'internal': ('%s%% of output' % a.sp), 'camera_pos_m': s['pos'], 'camera_target_m': s['target'], 'fov_deg': s.get('fov', 70),
                                  'game_time_s': times[-1], 'gpu_util_before_pct': u, 'wall_s': round(time.time() - t0)})
                    print('still', name, os.path.getsize(out) // 1024, 'KB', round(time.time() - t0), 's', flush=True)
    if a.clips:
        for preset in a.presets.split(','):
            name = 'swing_%s' % preset
            d = os.path.join(SCR, name); shutil.rmtree(d, ignore_errors=True)
            u = util(); t0 = time.time()
            cmd = [RUN_GAME, d, '-map', '/Game/Tests/Look/Look_Midtown' + ('' if preset == 'midday' else '_' + preset), '-res', '1920x1080', '-quit', str(a.clip_seconds),
                   '-name', name, '-movie', '-timeout', '3000', '-exec', 'r.ScreenPercentage %s' % a.sp,
                   '--', '-WHTravScript=' + os.path.join(HERE, 'scripts', 'city_swing_clip.json'), '-WHTravCsv=' + os.path.join(d, name + '_telemetry.csv')]
            r = subprocess.run(cmd, capture_output=True, text=True)
            mp4 = os.path.join(d, name + '.mp4')
            if not os.path.exists(mp4): print('FAILED clip', name, r.stdout[-400:]); continue
            dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', mp4], capture_output=True, text=True).stdout)
            out = os.path.join(rnd, name + '.mp4')
            if os.path.getsize(mp4) > 15_000_000:
                kbps = int(14.5e6 * 8 / 1000 / dur)
                subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-framerate', '60', '-i', d + '/%s_frames/MovieFrame%%05d.png' % name, '-c:v', 'libx264', '-preset', 'slow',
                                '-b:v', '%dk' % kbps, '-maxrate', '%dk' % kbps, '-bufsize', '%dk' % (kbps * 2), '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out])
            else:
                shutil.copy(mp4, out)
            if os.path.exists(os.path.join(d, name + '_telemetry.csv')): shutil.copy(os.path.join(d, name + '_telemetry.csv'), os.path.join(rnd, name + '_telemetry.csv'))
            nfr = len(glob.glob(d + '/%s_frames/*.png' % name))
            notes.append({'kind': 'clip', 'file': os.path.basename(out), 'preset': preset, 'map': cmd[cmd.index('-map') + 1], 'output': '1920x1080 60 fps H.264',
                          'internal': '%s%% of output (1920x1080)' % a.sp, 'frames': nfr, 'seconds': round(dur, 2), 'bytes': os.path.getsize(out),
                          'script': 'tools/perf_ue/scripts/city_swing_clip.json (P3 traversal hero, -WHTravScript)', 'time_step': 'fixed 1/60 s (-benchmark -fps=60 -dumpmovie)',
                          'gpu_util_before_pct': u, 'wall_s': round(time.time() - t0)})
            shutil.rmtree(d + '/%s_frames' % name, ignore_errors=True)  # heavy PNG frames are disposable once encoded
            print('clip', name, os.path.getsize(out) // 1024, 'KB', nfr, 'frames', flush=True)
    prev = []
    if os.path.exists(rnd + '/notes.json'):
        try: prev = json.load(open(rnd + '/notes.json'))
        except Exception: prev = []
    keep = {n['file']: n for n in prev}; keep.update({n['file']: n for n in notes})
    json.dump(list(keep.values()), open(rnd + '/notes.json', 'w'), indent=1)
    write_notes(rnd, list(keep.values()))

def write_notes(rnd, notes):
    L = ['# Look round capture notes (neutral facts only)', '',
         '> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.', '',
         'Everything below was rendered by the running game (`Scripts/run_game.sh`: standalone `-game`, offscreen, true back-buffer size), not by an editor viewport.',
         'Presets are defined in `unreal/WebHomage/Scripts/look_presets.json` (midday / golden / night) and built by `unreal/WebHomage/Scripts/build_look.py`.',
         'Camera positions are browser metres (x east, y up, z south); the UE position is (100 x, 100 z, 100 y) cm. Stills are JPEG converted from the PNG screenshot taken at the given game time.', '',
         '## Stills', '', '| file | preset | view | output | internal resolution | camera pos (m) | camera target (m) | fov | game time (s) |', '|---|---|---|---|---|---|---|---|---|']
    for n in sorted([n for n in notes if n['kind'] == 'still'], key=lambda n: (n['preset'], n['view'], n['output'])):
        L.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (n['file'], n['preset'], n['view'], n['output'], n['internal'], n['camera_pos_m'], n['camera_target_m'], n['fov_deg'], n['game_time_s']))
    L += ['', '## Clips', '', '| file | preset | map | output | internal resolution | frames | seconds | bytes | time step | script |', '|---|---|---|---|---|---|---|---|---|---|']
    for n in sorted([n for n in notes if n['kind'] == 'clip'], key=lambda n: n['preset']):
        L.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (n['file'], n['preset'], n['map'], n['output'], n['internal'], n['frames'], n['seconds'], n['bytes'], n['time_step'], n['script']))
    L += ['', 'Clip frames are rendered offline at a fixed 1/60 s step (`-benchmark -fps=60 -dumpmovie`), so a clip says nothing about real-time frame rate; see `PERF.md` for measured frame times.', '']
    open(rnd + '/NOTES.md', 'w').write('\n'.join(L))

if __name__ == '__main__':
    main()
