#!/usr/bin/env python3
"""Captures one final-loop clip (SPEC_FINAL shot list): real -game, playable profile + Fast preset, 1920x1080 output, 100 % internal, TSR, fixed 1/60 s, -dumpmovie, 1.5 s pre-roll cut,
the default (Tessera) suit. Multi-case clips (s2, s3) run one engine per case and are concatenated. One engine at a time through with_holder.sh.
outputs: <scratch>/<round>/<clip>/<case>/{frames/, route_telemetry.csv, route.log}; <docs round dir>/<clip>.mp4 (<= 15 MB), <clip>_telemetry.csv (cases concatenated, extra columns case, clip_t), <clip>_render.json
usage: run_clip.py <round> <clip> [--map island|island-night] [--cases c1,c2] [--crf 22] [--keep-frames]"""
import argparse, csv, json, shutil, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCR = Path.home() / 'sm2-n1/_scratch/final/swing'
SHOTS = ROOT / 'unreal/WebHomage/Saved/Showcase/User/Saved/Screenshots/MacEditor'   # play.py runs with -UserDir=Saved/Showcase/User/
PRE = 1.5
ap = argparse.ArgumentParser()
ap.add_argument('round'); ap.add_argument('clip'); ap.add_argument('--map'); ap.add_argument('--cases'); ap.add_argument('--crf', type=int, default=22); ap.add_argument('--keep-frames', action='store_true'); ap.add_argument('--reuse', action='store_true', help='post-process frames / telemetry left by an earlier engine run of this case (no launch)')
a = ap.parse_args()
clips = json.loads((ROOT / 'docs/night1/traversal/scripts/final/clips.json').read_text())
cases = clips[a.clip]
if a.cases: cases = [c for c in cases if c[0] in a.cases.split(',')]
game_map = a.map or ('island-night' if a.clip.startswith('s5') else 'island')
docs = ROOT / 'docs/night1/final/swing' / a.round; docs.mkdir(parents=True, exist_ok=True)
work = SCR / a.round / a.clip; work.mkdir(parents=True, exist_ok=True)
fast = ROOT / 'unreal/WebHomage/Config/PerfPlayableFast.cvars'
info = {'clip': a.clip, 'map': game_map, 'cases': []}
all_rows, total_frames, n_out = [], 0, 0
out_frames = work / 'all_frames'; shutil.rmtree(out_frames, ignore_errors=True); out_frames.mkdir(parents=True)
clip_t = 0.0
for name, q in cases:
    d = work / name
    if not a.reuse: shutil.rmtree(d, ignore_errors=True); d.mkdir(parents=True)
    if not a.reuse:
        for f in SHOTS.glob('MovieFrame*.png'): f.unlink()
    cmd = [str(ROOT / 'tools/showcase/with_holder.sh'), 'python3', str(ROOT / 'tools/showcase/play.py'), '--map', game_map, '--profile', 'playable', '--res-scale', '100', '--res', '1920x1080',
           '--capture', str(d), '--name', 'route', '--script', str(ROOT / 'docs/night1/traversal/scripts/final' / (name + '.json')), '--quit', str(q + PRE), '--timeout', '3000',
           '--game-arg=-benchmark', '--game-arg=-fps=60', '--game-arg=-dumpmovie', '--game-arg=-WHMovieAsync', '--game-arg=-WHTravPreroll=%s' % PRE, '--game-arg=-WHPerfPreset=%s' % fast, '--launch']
    t0 = time.time()
    if not a.reuse: subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    wall = time.time() - t0
    try:   # engine wall time from the log's first / last stamps (also valid with --reuse)
        import re, datetime
        st = [m.group(1) for m in re.finditer(r'^\[(\d{4}\.\d\d\.\d\d-\d\d\.\d\d\.\d\d)', (d / 'route.log').read_text(errors='replace'), re.M)]
        fmt = '%Y.%m.%d-%H.%M.%S'; wall = (datetime.datetime.strptime(st[-1], fmt) - datetime.datetime.strptime(st[0], fmt)).total_seconds() or wall
    except Exception: pass
    frames = sorted(SHOTS.glob('MovieFrame*.png'))
    rows = list(csv.DictReader((d / 'route_telemetry.csv').open())) if (d / 'route_telemetry.csv').exists() else []
    if not rows or not frames:
        sys.exit('%s: no telemetry / frames (rows %d, frames %d); log %s' % (name, len(rows), len(frames), d / 'route.log'))
    skip = len(frames) - len(rows)
    if skip < 0: sys.exit('%s: fewer frames (%d) than telemetry rows (%d)' % (name, len(frames), len(rows)))
    for f in frames[skip:]:
        n_out += 1; shutil.move(str(f), str(out_frames / ('f%06d.png' % n_out)))
    for f in frames[:skip]: f.unlink()
    for i, rr in enumerate(rows):
        rr['case'] = name; rr['clip_t'] = '%.4f' % (clip_t + float(rr['t'])); rr['clip_frame'] = str(total_frames + i)
    all_rows += rows; total_frames += len(rows); clip_t += float(rows[-1]['t']) + 1 / 60
    info['cases'].append({'case': name, 'frames_rendered': len(frames), 'preroll_frames_cut': skip, 'rows': len(rows), 'wall_s': round(wall, 1), 'fps_render': round(len(frames) / wall, 2)})
    print(name, info['cases'][-1], flush=True)
    shutil.copy(d / 'route.log', work / (name + '.log'))
with (docs / (a.clip + '_telemetry.csv')).open('w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(all_rows[0].keys())); w.writeheader(); w.writerows(all_rows)
mp4 = docs / (a.clip + '.mp4')
crf = a.crf
while True:
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-framerate', '60', '-i', str(out_frames / 'f%06d.png'), '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', str(crf), '-preset', 'slow', '-movflags', '+faststart', str(mp4)], check=True)
    if mp4.stat().st_size <= 15 * 1024 * 1024 or crf >= 36: break
    crf += 3
info.update({'frames': total_frames, 'duration_s': round(total_frames / 60, 2), 'mp4_mb': round(mp4.stat().st_size / 1048576, 2), 'crf': crf, 'wall_s_total': round(sum(c['wall_s'] for c in info['cases']), 1)})
(docs / (a.clip + '_render.json')).write_text(json.dumps(info, indent=1))
if not a.keep_frames: shutil.rmtree(out_frames)
print(json.dumps(info))
