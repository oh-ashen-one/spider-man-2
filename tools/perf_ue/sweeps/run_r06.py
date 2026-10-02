#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 06: ONE game session of /Game/Tests/Look/Look_Midtown_tod that visits groups of (key table, hour, live pins, poses) and writes a still per pose.
Successor of run_r05.py with (a) the sky poses of tools/perf_ue/sky_poses.json (S4w = perch turned to the dusk sun, S4e = to the dawn sun, S4m = to the 22:00 moon),
(b) a key table per group (`"keys": "<abs file written by Scripts/look_tod.py --out>"` -> `wh.ToDLoad`, so a sweep needs no rebuild) and (c) the settle rule of the brief:
the FIRST pose of a group waits `settle_first` s (default 8) after the hour / key change, the next poses of the same hour `settle` s (default 5).
Every group starts with `wh.ToDClear` and `wh.Weather -1`; params that are NOT keyed are sticky for the session (mpc defaults, tour `! mpc` pins).

usage: run_r06.py --plan plan.json --out <dir> [--res 1920x1080] [--timeout 2300] [--sp 100]
plan.json: {"groups": [{"name": "h19.5", "hour": 19.5, "keys": "/abs/keys.txt" (optional), "cmds": ["exec wh.ToDSet atm.HeightFogContribution 0"], "shots": ["S4", "S4w", "S7"],
                        "settle_first": 8, "settle": 5}, ...]}
stills: <out>/tod_<pose>_<res>_<name>.jpg (+ the PNGs in <out>/png)"""
import argparse, glob, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
PU = os.path.dirname(HERE)
sys.path.insert(0, PU)
from capture_tour import U, look_rot, util, RUN_GAME, UE, slot   # noqa: E402


def load_poses():
    shots = {s['id'].split('_')[0]: s for s in json.load(open(os.path.join(UE, 'Scripts', 'city_shots.json')))}
    shots.update({s['id'].split('_')[0]: s for s in json.load(open(os.path.join(PU, 'sky_poses.json')))})
    return shots


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--plan', required=True); ap.add_argument('--out', required=True); ap.add_argument('--res', default='1920x1080')
    ap.add_argument('--timeout', type=int, default=2300); ap.add_argument('--sp', default='100'); ap.add_argument('--first-settle', type=float, default=12.0)
    ap.add_argument('--dry', action='store_true', help='write the tour file only')
    a = ap.parse_args()
    plan = json.load(open(a.plan))
    shots = load_poses()
    out = os.path.abspath(a.out); png = os.path.join(out, 'png'); os.makedirs(png, exist_ok=True)
    L = ['# P4 r06 plan %s' % a.plan]; first = True; names = []
    for g in plan['groups']:
        cmds = ['exec wh.ToDClear', 'cvar wh.Weather %s' % g.get('weather', -1)]
        if g.get('keys'): cmds.append('exec wh.ToDLoad %s' % g['keys'])
        if g.get('hour') is not None: cmds.append('cvar wh.TimeOfDay %s' % g['hour'])
        cmds += g.get('cmds', [])
        for i, sid in enumerate(g['shots']):
            s = shots[sid]
            p, t = U(*s['pos']), U(*s['target']); r = look_rot(p, t); pl = s.get('player') or s['pos']; h = U(pl[0], pl[1] + 1.0, pl[2])
            if i == 0: L += ['! ' + c for c in cmds]
            settle = a.first_settle if first else (g.get('settle_first', 8.0) if i == 0 else g.get('settle', 5.0))
            L.append('%s@%s %.1f %.1f %.1f %.4f %.4f %.4f %.2f %.1f 0 %.1f %.1f %.1f' % (sid, g['name'], p[0], p[1], p[2], r[0], r[1], r[2], s.get('fov', 70), settle, h[0], h[1], h[2]))
            names.append('%s@%s' % (sid, g['name'])); first = False
    tf = os.path.join(png, 'tour.txt'); open(tf, 'w').write('\n'.join(L) + '\n')
    if a.dry: print(open(tf).read()); return
    for f in glob.glob(png + '/*.png'): os.remove(f)
    u = util(); t0 = time.time()
    cmd = [RUN_GAME, png, '-map', '/Game/Tests/Look/Look_Midtown_tod', '-res', a.res, '-quit', '5000', '-name', 'tour', '-timeout', str(a.timeout),
           '-exec', 'r.ScreenPercentage %s' % a.sp, '--', '-WHLookTour=' + tf, '-WHLookTourDir=' + png, '-WHLookTourStart=8', '-WHLookTourMinFrames=90']
    r = subprocess.run(slot(cmd), capture_output=True, text=True)
    n = 0
    for nm in names:
        f = os.path.join(png, nm + '.png')
        if not os.path.exists(f): continue
        sid, v = nm.split('@')
        subprocess.run(['sips', '-s', 'format', 'jpeg', '-s', 'formatOptions', '92', f, '--out', os.path.join(out, 'tod_%s_%s_%s.jpg' % (sid, a.res, v))], capture_output=True); n += 1
    json.dump({'plan': plan, 'res': a.res, 'internal': '%s%% of output' % a.sp, 'gpu_util_before_pct': u, 'wall_s': round(time.time() - t0), 'stills': n, 'poses': len(names),
               'settle_rule': 'first pose of a group: settle_first s (default 8) after the hour / key change; next poses of the group: settle s (default 5); min 90 frames'},
              open(os.path.join(out, 'session.json'), 'w'), indent=1)
    print('session', n, '/', len(names), 'stills', round(time.time() - t0), 's', flush=True)
    if n == 0: print(r.stdout[-1500:], r.stderr[-500:]); sys.exit(1)


if __name__ == '__main__':
    main()
