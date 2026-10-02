#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 06: closed loop that smooths the L23b curve with the exposure bias of the twilight keys. Runs INSIDE one GPU hold (every iteration is one 960x540 lapse, ~100 s at 2 h/s or ~280 s sub-stepped x4, through
capture_tod_lapse.py, which goes through gpu_slot.sh as a nested capture).
(hold 6) the target is lapse_opt.design_target (the curve closest to the measured one with |dY| <= --slope per frame, golden / night anchors pinned, ceiling where the red sky clips) and --substeps N renders the lapse sub-stepped:
  repeat: lapse with the current table -> measured mean Y per frame -> target = the measured curve with its steps removed (lapse_opt.smooth_target: gaussian smoothing + slope limit,
  anchors pinned) -> dEV = 2.2 log2(target / measured) averaged around each adjustable key -> pp.AutoExposureBias(key) += gain * dEV -> next table.
Stops when the lapse passes L23b (max jump <= 3, p99 <= 1.5, 05:00-21:30 mean <= 130 / clipped <= 1.8 %), after --iters, or when the remaining budget (--deadline, a unix time) is short.
Writes <out>/it<N>/ (lapse json), <out>/keys_it<N>.txt and <out>/bias_overrides.json = {hour: bias} to merge into Scripts/look_presets.json (make_v2.py knob `twilight_overrides`).
usage: lapse_loop.py --out <dir> --cvars <wh.ToDLapseCvars string> [--iters 4] [--deadline <unix time>] [--keys-hours ...] [--hold ...] [--slope 1.1] [--gain 0.8] [--start-keys <file>]"""
import argparse, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(WT, 'unreal', 'WebHomage', 'Scripts')); sys.path.insert(0, os.path.join(HERE, 'sweeps', 'r06'))
import numpy as np   # noqa: E402
import look_tod, lapse_opt, make_v2   # noqa: E402


def spline_basis(tab, adj, hrs):
    """W[i, j] = d bias(hour_i) / d bias(key adj[j]) of the driver's Catmull-Rom (finite differences on the python twin look_tod.evaluate, bias param only)"""
    import copy
    base = {'keys': [{'h': k['h'], 'p': {'pp.AutoExposureBias': float(k['p']['pp.AutoExposureBias'])}} for k in tab['keys']]}
    v0 = np.array([look_tod.evaluate(base, h % 24.0)['pp.AutoExposureBias'] for h in hrs])
    W = np.zeros((len(hrs), len(adj)))
    for j, hk in enumerate(adj):
        t2 = copy.deepcopy(base)
        for k in t2['keys']:
            if abs(k['h'] - hk) < 1e-6: k['p']['pp.AutoExposureBias'] += 0.05
        W[:, j] = (np.array([look_tod.evaluate(t2, h % 24.0)['pp.AutoExposureBias'] for h in hrs]) - v0) / 0.05
    return W


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--cvars', default=''); ap.add_argument('--iters', type=int, default=4)
    ap.add_argument('--deadline', type=float, default=0.0); ap.add_argument('--keys-hours', default='5.6,6.1,6.25,6.35,6.45,6.5,6.55,6.65,6.8,6.9,7.0,7.1,7.2,7.3,7.4,7.6,7.8,8.0,8.4,8.8,18.8,19.0,19.2,19.35,19.5,19.65,19.8,19.9,20.2,20.4,20.6,21.0')
    ap.add_argument('--hold', default='4.9,9.5,13,16.5,18.4,21.4,0'); ap.add_argument('--raise-pen', type=float, default=4.0); ap.add_argument('--slope', type=float, default=1.3); ap.add_argument('--gain', type=float, default=0.8)
    ap.add_argument('--window', type=float, default=0.25); ap.add_argument('--substeps', type=int, default=1); ap.add_argument('--max-delta', type=float, default=1.3, help='largest total change (EV) of a key bias from the starting table'); ap.add_argument('--no-ls', action='store_true', help='use the round-06 window averages instead of the spline least-squares update'); ap.add_argument('--ridge', type=float, default=0.02); ap.add_argument('--anchor-w', type=float, default=2e3); ap.add_argument('--from-it', type=int, default=0, help='first iteration number (a continued loop)'); ap.add_argument('--doc', default='', help='table document (default: the committed Scripts/look_presets.json)')
    a = ap.parse_args()
    out = os.path.abspath(a.out); os.makedirs(out, exist_ok=True)
    doc = json.load(open(a.doc)) if a.doc else look_tod.load_doc()
    kh = [float(x) for x in a.keys_hours.split(',')]; hold = [float(x) for x in a.hold.split(',') if x]
    sets = []; overrides = {}
    base_bias = {k['h']: k['p']['pp.AutoExposureBias'] for k in look_tod.expand(doc, [])['keys']}
    for it in range(a.from_it, a.from_it + a.iters):
        if a.deadline and time.time() + 200 > a.deadline: print('loop: deadline close, stopping before iteration', it); break
        tab = look_tod.expand(doc, sets)
        kf = os.path.join(out, 'keys_it%d.txt' % it); open(kf, 'w').write(look_tod.to_text(tab))
        rd = os.path.join(out, 'it%d' % it)
        cmd = [sys.executable, os.path.join(HERE, 'capture_tod_lapse.py'), '--shot', 'S4', '--res', '960x540', '--no-encode', '--round', rd, '--name', 'lapse', '--from', '4.0', '--hours', '24', '--seconds', '12',
               '--keys', kf, '--timeout', '900', '--substeps', str(a.substeps)] + (['--cmds', 'exec wh.ToDLapseCvars ' + a.cvars] if a.cvars else [])
        r = subprocess.run(cmd, capture_output=True, text=True); print(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-300:], flush=True)
        jp = os.path.join(rd, 'lapse.json')
        if not os.path.exists(jp): print('loop: lapse failed'); sys.exit(2)
        d = json.load(open(jp)); c = d['checks_L23b']
        print('iteration %d: max jump %.2f p99 %.2f mean<=%.1f clipped<=%.2f %% -> %s' % (it, c['max_jump'], c['p99_jump'], c['window_05_2130']['max_mean_y'], c['window_05_2130']['max_clipped_pct'], 'PASS' if c['pass'] else 'fail'), flush=True)
        if c['pass']: break
        hrs, ys = d['hours_per_frame'], d['mean_y_per_frame']
        T, info = lapse_opt.design_target(hrs, ys, d['clipped_pct_per_frame'], hold, a.slope, anchor_w=a.anchor_w, raise_pen=a.raise_pen); print('target', json.dumps({k: round(v, 2) for k, v in info.items()}), flush=True)
        Y = np.asarray(ys); dev = np.clip(np.where(Y > 8.0, 2.2 * np.log2(np.maximum(T, 1.0) / np.maximum(Y, 1.0)), 0.0), -1.2, 1.2); hr = np.asarray(hrs)
        nk = {k['h']: k['p'] for k in tab['keys']}
        if not a.no_ls:
            adj = [h for h in kh if h in nk]
            W = spline_basis(tab, adj, hrs)
            m = np.where(Y > 8.0, 1.0, 0.0)
            A = W * m[:, None]; bvec = dev * m
            delta = np.linalg.solve(A.T @ A + a.ridge * np.eye(len(adj)) * max(1.0, float(m.sum()) / 100.0), A.T @ bvec)
            for h, dl in zip(adj, delta):
                nb = float(nk[h]['pp.AutoExposureBias']) + a.gain * float(dl)
                nb = min(max(nb, base_bias[h] - a.max_delta), base_bias[h] + a.max_delta)
                sets.append('h=%g:pp.AutoExposureBias=%.4f' % (h, nb)); overrides[str(h)] = round(nb, 4)
            print('ls update: residual rms %.3f EV -> %.3f EV, deltas %s' % (float(np.sqrt(np.mean((dev * m) ** 2))), float(np.sqrt(np.mean((dev * m - A @ delta) ** 2))), ' '.join('%g:%+.2f' % (h, dl) for h, dl in zip(adj, delta))), flush=True)
        else:
          for h in kh:
            if h not in nk: continue
            dh = ((hr - h + 12) % 24) - 12; w = np.clip(1.0 - np.abs(dh) / a.window, 0.0, None)
            if w.sum() <= 0: continue
            nb = float(nk[h]['pp.AutoExposureBias']) + a.gain * float((w * dev).sum() / w.sum())
            nb = min(max(nb, base_bias[h] - a.max_delta), base_bias[h] + a.max_delta)
            sets.append('h=%g:pp.AutoExposureBias=%.4f' % (h, nb)); overrides[str(h)] = round(nb, 4)
        json.dump(overrides, open(os.path.join(out, 'bias_overrides.json'), 'w'), indent=1)
    print('overrides', json.dumps(overrides))


if __name__ == '__main__':
    main()
