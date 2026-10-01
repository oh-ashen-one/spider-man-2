#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See DISCLAIMER.md.
"""Island piece (A): route check of a traversal telemetry CSV (Source/WebHomage/Traversal/WebTravScript: -WHTravScript + -WHTravCsv) against the
city export the map was built from.  Answers the M1 acceptance questions for one route:

  fall-through  feet below the water plane (z < -2 m), or the body deep inside a WHBox (>= 0.6 m from every face) for >= 0.15 s
  stuck         moving input held (stick / swing / zip) but speed < 0.4 m/s for >= 1.0 s (perch / idle without input is fine)
  mid-air       a SUPPORTED mode (ground / perch / land) with no surface under the feet: neither a WHBox top (footprint contains the feet,
                top within 0.45 m) nor the street (feet <= 0.5 m) -- or a box top that is a phantom (drawn roof > 1.5 m lower, coll_audit grid)
  wall-air      wall mode with no box face within 1.2 m of the feet
  facadeLod     distance from every hero position to the nearest facadeLod (bare-mass) tile of the build (target: none within 1.2 km)

    python3 tools/export/island_route_check.py <export_dir> <telemetry.csv> [more.csv ...] [--out report.json]

Telemetry units: UE metres (x east, y south = browser z, z up = browser y)."""
import csv, json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from island_coll_audit import boxes_of

SUPPORTED = ('ground', 'perch', 'land')


def load_boxes(E):
    B = np.array([[b[0], b[2], b[1], b[3], b[5], b[4]] for b in boxes_of(E)], np.float64)  # -> UE metres: x0, y0(=z0), z0(=y0), x1, y1, z1
    return B


def lod_tiles(E):
    M = json.load(open(os.path.join(E, 'manifest.json')))
    T = []
    for r in M['meshes']:
        if r['name'].startswith('facadeLod'):
            c = r['center']; T.append((c[0] - 128, c[2] - 128, c[0] + 128, c[2] + 128))
    return np.array(T, np.float64) if T else np.zeros((0, 4))


def check(E, csv_path, B, L, audit_hv=None, reg=None):
    rows = list(csv.DictReader(open(csv_path)))
    f = lambda r, k: float(r[k]) if r.get(k) not in (None, '') else 0.0
    ev = {'fall_through': [], 'stuck': [], 'mid_air': [], 'wall_air': []}
    inside_t = 0.0; stuck_t = 0.0; prev_t = None; lod_min = math.inf
    n_sup = 0
    for r in rows:
        t = f(r, 't'); dt = 0.0 if prev_t is None else max(0.0, t - prev_t); prev_t = t
        x, y, z = f(r, 'x_m'), f(r, 'y_m'), f(r, 'z_m'); mode = r['mode']
        if len(L):
            dx = np.maximum(np.maximum(L[:, 0] - x, x - L[:, 2]), 0); dy = np.maximum(np.maximum(L[:, 1] - y, y - L[:, 3]), 0)
            lod_min = min(lod_min, float(np.min(np.hypot(dx, dy))))
        # boxes containing the feet column
        inxy = (B[:, 0] <= x) & (x <= B[:, 3]) & (B[:, 1] <= y) & (y <= B[:, 4])
        # fall-through
        if z < -2.0: ev['fall_through'].append([round(t, 3), 'below water', round(z, 2)])
        mid = z + 0.9
        deep = inxy & (B[:, 2] + 0.6 < mid) & (mid < B[:, 5] - 0.6) & (B[:, 0] + 0.6 < x) & (x < B[:, 3] - 0.6) & (B[:, 1] + 0.6 < y) & (y < B[:, 4] - 0.6)
        if deep.any() and mode != 'wall':
            inside_t += dt
            if inside_t >= 0.15 and (not ev['fall_through'] or ev['fall_through'][-1][1] != 'inside box' or t - ev['fall_through'][-1][0] > 1.0):
                ev['fall_through'].append([round(t, 3), 'inside box', round(z, 2)])
        else: inside_t = 0.0
        # stuck
        moving_input = abs(f(r, 'in_move_x')) + abs(f(r, 'in_move_y')) > 0.2 or f(r, 'in_swing') > 0.5 or f(r, 'in_zip') > 0.5
        if moving_input and f(r, 'speed_mps') < 0.4 and mode not in ('perch',):
            stuck_t += dt
            if stuck_t >= 1.0 and (not ev['stuck'] or t - ev['stuck'][-1][0] > 1.0): ev['stuck'].append([round(t, 3), mode, round(x, 1), round(y, 1), round(z, 1)])
        else: stuck_t = 0.0
        # mid-air on a supported mode
        if mode in SUPPORTED:
            n_sup += 1
            tops = B[inxy, 5] if inxy.any() else np.zeros(0)
            near_box = tops.size and np.min(np.abs(tops - z)) <= 0.45
            street = z <= 0.5
            phantom = False
            if near_box and audit_hv is not None and reg is not None:
                c, rw = int(x - reg['x0']), int(y - reg['z0'])
                if 0 <= rw < audit_hv.shape[0] and 0 <= c < audit_hv.shape[1]:
                    phantom = float(audit_hv[rw, c]) < z - 1.5
            if not (near_box or street) or phantom:
                ev['mid_air'].append([round(t, 3), mode, r['sub'], round(x, 1), round(y, 1), round(z, 2), 'phantom box' if phantom else 'no surface'])
        if mode == 'wall':
            near = (B[:, 0] - 1.2 <= x) & (x <= B[:, 3] + 1.2) & (B[:, 1] - 1.2 <= y) & (y <= B[:, 4] + 1.2) & (B[:, 2] - 0.5 <= z) & (z <= B[:, 5] + 0.5)
            if not near.any(): ev['wall_air'].append([round(t, 3), round(x, 1), round(y, 1), round(z, 2)])
    dur = f(rows[-1], 't') - f(rows[0], 't') if rows else 0
    path = sum(math.dist((f(a, 'x_m'), f(a, 'y_m'), f(a, 'z_m')), (f(b, 'x_m'), f(b, 'y_m'), f(b, 'z_m'))) for a, b in zip(rows, rows[1:]))
    modes = {}
    for r in rows: modes[r['mode']] = modes.get(r['mode'], 0) + 1
    return {'csv': os.path.basename(csv_path), 'frames': len(rows), 'seconds': round(dur, 2), 'path_m': round(path, 1), 'modes': modes,
            'supported_frames': n_sup, 'fall_through': len(ev['fall_through']), 'stuck': len(ev['stuck']), 'mid_air_frames': len(ev['mid_air']),
            'wall_air_frames': len(ev['wall_air']), 'facadeLod_min_dist_m': None if lod_min == math.inf else round(lod_min, 1), 'events': ev,
            'start': [f(rows[0], 'x_m'), f(rows[0], 'y_m'), f(rows[0], 'z_m')] if rows else None,
            'end': [f(rows[-1], 'x_m'), f(rows[-1], 'y_m'), f(rows[-1], 'z_m')] if rows else None}


def main():
    a = sys.argv[1:]
    out = None
    if '--out' in a: i = a.index('--out'); out = a[i + 1]; del a[i:i + 2]
    E, csvs = a[0], a[1:]
    B, L = load_boxes(E), lod_tiles(E)
    hvp = os.path.join(E, 'coll_audit_hv.npy')
    hv = np.load(hvp).astype(np.float32) if os.path.exists(hvp) else None
    reg = json.load(open(os.path.join(E, 'manifest.json')))['region']
    res = [check(E, c, B, L, hv, reg) for c in csvs]
    summ = {'routes': len(res), 'seconds': round(sum(r['seconds'] for r in res), 1), 'fall_through': sum(r['fall_through'] for r in res),
            'stuck': sum(r['stuck'] for r in res), 'mid_air_frames': sum(r['mid_air_frames'] for r in res), 'wall_air_frames': sum(r['wall_air_frames'] for r in res),
            'facadeLod_min_dist_m': min((r['facadeLod_min_dist_m'] for r in res if r['facadeLod_min_dist_m'] is not None), default=None),
            'boxes': len(B), 'facadeLod_tiles': len(L)}
    rep = {'summary': summ, 'routes': res}
    if out: json.dump(rep, open(out, 'w'), indent=1)
    for r in res:
        print('%-34s %5.1f s %6.0f m  fall %d  stuck %d  mid-air %d  wall-air %d  lod-dist %s  modes %s' % (r['csv'], r['seconds'], r['path_m'], r['fall_through'], r['stuck'],
              r['mid_air_frames'], r['wall_air_frames'], r['facadeLod_min_dist_m'], r['modes']))
    print('TOTAL', json.dumps(summ))


if __name__ == '__main__':
    main()
