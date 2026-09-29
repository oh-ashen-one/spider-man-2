#!/usr/bin/env python3
"""Assemble docs/night1/city/round-NN from a capture_round.sh output dir: JPG captures, perf.json, README (neutral:
camera parameters + frame times + GPU utilization only). usage: assemble_round.py <raw_dir> <round_dir> <round_no>"""
import json, os, sys
from PIL import Image
RAW, R, N = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(R, exist_ok=True)
shots = json.load(open(os.path.join(os.path.dirname(__file__), '../../unreal/WebHomage/Scripts/city_shots.json')))
rows, perf = [], {}
for s in shots:
    for res in ('1920x1080', '3840x2160'):
        png = f'{RAW}/{s["id"]}_{res}_00_t028.0.png'
        if os.path.exists(png): Image.open(png).convert('RGB').save(f'{R}/{s["id"]}_{res}.jpg', quality=88)
        p = json.load(open(f'{RAW}/{s["id"]}_{res}_perf.json')) if os.path.exists(f'{RAW}/{s["id"]}_{res}_perf.json') else {}
        g = json.load(open(f'{RAW}/{s["id"]}_{res}_gpu.json')) if os.path.exists(f'{RAW}/{s["id"]}_{res}_gpu.json') else {}
        p['gpu_util_before_pct'] = g.get('gpu_util_before_pct'); perf[f'{s["id"]}_{res}'] = p; rows.append((s['id'], res, p))
json.dump(perf, open(f'{R}/perf.json', 'w'), indent=1)
L = [f'# P1 City round {N} — captures and camera parameters', '', '> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.', '',
     'Running game: `Scripts/run_game.sh` (`-game`, offscreen, map `/Game/Tests/City/City_View_<id>`, auto-activated CameraActor), screenshot at t = 28 s.',
     'Frame times: game seconds 18-28, `t.MaxFPS 0`, no VSync, TSR with automatic screen percentage. GPU utilization read with ioreg before each run',
     '(GPU shared with other sessions; the P1 editor was also open). Positions in browser metres (x east, y up, z south); UE = (100x, 100z, 100y) cm.', '',
     '| id | camera pos | target | fov | sun (pitch, yaw) |', '|---|---|---|---|---|']
L += [f"| {s['id']} | {s['pos']} | {s['target']} | {s.get('fov', 70)} | {s.get('sun')} |" for s in shots]
L += ['', '| id | output | internal | avg ms | p95 ms | GPU ms | GPU util before |', '|---|---|---|---|---|---|---|']
L += [f"| {i} | {res} | {p.get('internal_w')}x{p.get('internal_h')} | {p.get('avg_ms')} | {p.get('p95_ms')} | {p.get('gpu_avg_ms')} | {p.get('gpu_util_before_pct')} % |" for i, res, p in rows]
open(f'{R}/README.md', 'w').write('\n'.join(L) + '\n')
