#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 06, hold 8: closed loop on the exposure bias of the twilight keys that measures only the TWILIGHT WINDOWS at a high render sub-step (x16: the engine's temporal lighting caches lag under one output frame,
see lapse_stitch.py: the x4 lapse of hold 7 read 54.6 Y at 19:48 against 15.0 for a settled still). One iteration = the dawn window and the dusk window, each rendered by capture_tod_lapse.py (960x540, nominal 2 h/s,
a warm-up of --warm game hours is dropped), ~4.5 min together. The target of each window is lapse_opt.design_target (slope-limited, both window ends pinned, brightening a valley costs --raise-pen) and the update
of the key biases is the spline least-squares step of lapse_loop.py. Writes <out>/bias_overrides.json = {hour: bias} (make_v2.py --bias-overrides) and <out>/it<N>/ with the window jsons.
usage: lapse_loop_w.py --out <dir> --doc <table doc> [--windows "5.5:2.7,18.1:3.3"] [--substeps 16] [--warm 0.3] [--iters 2] [--deadline <unix>]"""
import argparse, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(WT, 'unreal', 'WebHomage', 'Scripts')); sys.path.insert(0, os.path.join(HERE, 'sweeps', 'r06'))
import numpy as np   # noqa: E402
import look_tod, lapse_opt, lapse_loop   # noqa: E402


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--doc', required=True); ap.add_argument('--windows', default='5.5:2.7,18.1:3.3'); ap.add_argument('--substeps', type=int, default=16)
    ap.add_argument('--warm', type=float, default=0.3); ap.add_argument('--iters', type=int, default=2); ap.add_argument('--deadline', type=float, default=0.0)
    ap.add_argument('--keys-hours', default='5.6,6.1,6.25,6.35,6.45,6.5,6.55,6.65,6.8,6.9,7.0,7.1,7.2,7.3,7.4,7.6,7.8,8.0,8.4,18.8,19.0,19.2,19.35,19.5,19.65,19.8,19.9,20.2,20.4,20.6,21.0')
    ap.add_argument('--raise-pen', type=float, default=2.0); ap.add_argument('--slope', type=float, default=1.3); ap.add_argument('--gain', type=float, default=0.9); ap.add_argument('--max-delta', type=float, default=2.0)
    ap.add_argument('--ridge', type=float, default=0.02); ap.add_argument('--anchor-w', type=float, default=2e4); ap.add_argument('--from-it', type=int, default=0); ap.add_argument('--timeout', type=int, default=900)
    a = ap.parse_args()
    out = os.path.abspath(a.out); os.makedirs(out, exist_ok=True)
    doc = json.load(open(a.doc)); kh = [float(x) for x in a.keys_hours.split(',')]
    wins = [(float(w.split(':')[0]), float(w.split(':')[1])) for w in a.windows.split(',')]
    sets = []; overrides = {}
    base_bias = {k['h']: k['p']['pp.AutoExposureBias'] for k in look_tod.expand(doc, [])['keys']}
    for it in range(a.from_it, a.from_it + a.iters):
        if a.deadline and time.time() + 330 > a.deadline: print('loopw: deadline close, stopping before iteration', it); break
        tab = look_tod.expand(doc, sets)
        kf = os.path.join(out, 'keys_it%d.txt' % it); open(kf, 'w').write(look_tod.to_text(tab))
        H, Y, C, E = [], [], [], []   # hours, mean Y, clipped %, window edge flags
        segs = []
        for k, (h0, dh) in enumerate(wins):
            rd = os.path.join(out, 'it%d' % it, 'w%d' % k)
            cmd = [sys.executable, os.path.join(HERE, 'capture_tod_lapse.py'), '--shot', 'S4', '--res', '960x540', '--no-encode', '--round', rd, '--name', 'lapse', '--from', '%g' % h0, '--hours', '%g' % dh, '--seconds', '%g' % (dh / 2.0),
                   '--substeps', str(a.substeps), '--drop-first-hours', '%g' % a.warm, '--trim-end', '--keys', kf, '--timeout', str(a.timeout)]
            r = subprocess.run(cmd, capture_output=True, text=True); print(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-300:], flush=True)
            jp = os.path.join(rd, 'lapse.json')
            if not os.path.exists(jp): print('loopw: window', k, 'failed'); sys.exit(2)
            d = json.load(open(jp)); segs.append(d)
            H.append(np.array(d['hours_per_frame'])); Y.append(np.array(d['mean_y_per_frame'])); C.append(np.array(d['clipped_pct_per_frame']))
        allj = np.concatenate([np.abs(np.diff(y)) for y in Y]); allc = np.concatenate(C)
        print('iteration %d: windows max jump %.2f p99 %.2f frames>3 %d >1.5 %d, clipped max %.2f %%' % (it, allj.max(), np.percentile(allj, 99), (allj > 3).sum(), (allj > 1.5).sum(), allc.max()), flush=True)
        json.dump({'windows': wins, 'hours': [h.tolist() for h in H], 'mean_y': [y.tolist() for y in Y], 'clipped': [c.tolist() for c in C]}, open(os.path.join(out, 'it%d' % it, 'windows.json'), 'w'))
        # per-window targets (both window ends pinned), stacked
        HR, DEV = [], []
        for h, y, c in zip(H, Y, C):
            T, info = lapse_opt.design_target(h, y, c, [float(h[0]), float(h[-1])], a.slope, anchor_w=a.anchor_w, raise_pen=a.raise_pen)
            print('target', json.dumps({k: round(v, 2) for k, v in info.items()}), flush=True)
            HR.append(h); DEV.append(np.clip(np.where(y > 8.0, 2.2 * np.log2(np.maximum(T, 1.0) / np.maximum(y, 1.0)), 0.0), -1.5, 1.5))
        hrs = np.concatenate(HR); dev = np.concatenate(DEV); Yall = np.concatenate(Y)
        nk = {k['h']: k['p'] for k in tab['keys']}
        adj = [h for h in kh if h in nk]
        W = lapse_loop.spline_basis(tab, adj, hrs); m = (Yall > 8.0).astype(float)
        A = W * m[:, None]; b = dev * m
        delta = np.linalg.solve(A.T @ A + a.ridge * np.eye(len(adj)) * max(1.0, float(m.sum()) / 100.0), A.T @ b)
        for h, dl in zip(adj, delta):
            nb = float(nk[h]['pp.AutoExposureBias']) + a.gain * float(dl)
            nb = min(max(nb, base_bias[h] - a.max_delta), base_bias[h] + a.max_delta)
            sets.append('h=%g:pp.AutoExposureBias=%.4f' % (h, nb)); overrides[str(h)] = round(nb, 4)
        print('ls update: residual rms %.3f EV -> %.3f EV, deltas %s' % (float(np.sqrt(np.mean((dev * m) ** 2))), float(np.sqrt(np.mean((dev * m - A @ delta) ** 2))), ' '.join('%g:%+.2f' % (h, dl) for h, dl in zip(adj, delta))), flush=True)
        json.dump(overrides, open(os.path.join(out, 'bias_overrides.json'), 'w'), indent=1)
    print('overrides', json.dumps(overrides))


if __name__ == '__main__':
    main()
