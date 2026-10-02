#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See DISCLAIMER.md.
"""Island piece (A), round 02: critic test 2 on r4 (wall-run / roofs). After the perch the script sprints along the roof (t >= RUN_T) toward a
parapet; the run must END in a stop or a vault at the parapet (not pass through it), and the first touchdown after the jump / drop must be on a
drawn surface (fire escape, roof, street) within 0.45 m.

    python3 tools/export/island_r4_check.py <export_dir> <r4_telemetry.csv> [--run-t 11.0] [--out report.json]"""
import csv, json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from island_route_check import Drawn, BODY_H


def main():
    a = sys.argv[1:]
    out = None; run_t = 11.0
    if '--out' in a: i = a.index('--out'); out = a[i + 1]; del a[i:i + 2]
    if '--run-t' in a: i = a.index('--run-t'); run_t = float(a[i + 1]); del a[i:i + 2]
    E, path = a
    D = Drawn(E)
    rows = [r for r in csv.DictReader(open(path))]
    f = lambda r, k: float(r[k]) if r.get(k) not in (None, '') else 0.0
    seg = [r for r in rows if f(r, 't') >= run_t]
    # the roof run: consecutive ground frames above 10 m from run_t on
    run = []
    for r in seg:
        if r['mode'] in ('ground',) and f(r, 'z_m') - BODY_H > 10.0: run.append(r)
        elif run: break
    rep = {'csv': os.path.basename(path), 'run_t': run_t, 'run_frames': len(run)}
    if run:
        last = run[-1]; nxt = seg[len(run)] if len(run) < len(seg) else None
        ovl = [(round(f(r, 't'), 3), D.overlap(f(r, 'x_m'), f(r, 'y_m'), f(r, 'z_m') - BODY_H)) for r in run]
        ovl = [o for o in ovl if o[1]]
        # how the run ended: the hero stopped (speed < 1 m/s while the stick is held), vaulted / climbed (sub-state), or left the roof (jump)
        stopped = any(f(r, 'hspeed_mps') < 1.0 and abs(f(r, 'in_move_y')) + abs(f(r, 'in_move_x')) > 0.2 for r in run[5:])
        subs = sorted(set(r['sub'] for r in run))
        rep.update({'run_t0': f(run[0], 't'), 'run_t1': f(last, 't'), 'run_start': [f(run[0], 'x_m'), f(run[0], 'y_m'), round(f(run[0], 'z_m') - BODY_H, 2)],
                    'run_end': [f(last, 'x_m'), f(last, 'y_m'), round(f(last, 'z_m') - BODY_H, 2)], 'run_subs': subs,
                    'next_mode': None if nxt is None else [nxt['mode'], nxt['sub']], 'stopped_at_obstacle': stopped,
                    'vault_or_climb': any(k in ' '.join(subs + ([nxt['sub']] if nxt else [])).lower() for k in ('vault', 'mantle', 'climb', 'hop', 'topout')),
                    'overlap_frames_during_run': len(ovl), 'overlap_examples': ovl[:5]})
        # first touchdown after the run
        after = seg[len(run):]
        air = False; td = None
        for r in after:
            if r['mode'] in ('air',): air = True
            if air and r['mode'] in ('land', 'ground', 'perch'):
                td = r; break
        if td is not None:
            x, y, z = f(td, 'x_m'), f(td, 'y_m'), f(td, 'z_m') - BODY_H
            what, dz = D.support(x, y, z, tol=0.45)
            rep['touchdown'] = {'t': f(td, 't'), 'mode': td['mode'], 'sub': td['sub'], 'feet': [x, y, round(z, 2)], 'surface': what, 'dz_m': round(dz, 3),
                                'pass': what is not None}
    if out: json.dump(rep, open(out, 'w'), indent=1)
    print(json.dumps(rep, indent=1))


if __name__ == '__main__':
    main()
