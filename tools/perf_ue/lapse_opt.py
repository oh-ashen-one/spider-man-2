#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 06: one step of a closed loop that smooths the L23b curve with the exposure bias keys.
Input: a lapse json (capture_tod_lapse.py: per-frame hour / mean Y), the table the lapse ran with (key file text), the hours of the keys whose pp.AutoExposureBias may move.
  1. target curve T(h): the measured curve with its steps removed: repeated gaussian smoothing + a slope limit (|dT| <= --slope per frame) with the anchors (hours listed in --hold,
     e.g. the golden / night stills the other specs depend on) pinned to their measured value;
  2. the exposure that turns Y(h) into T(h): display luma goes ~ exposure^(1/2.2) before the tone curve saturates, dEV(h) = 2.2 * log2(T / Y) (clamped +-1.2 EV, only where Y > 8);
  3. each adjustable key k gets the Catmull-weighted mean of dEV around its hour (+-window h) times --gain; the new bias = old + that.
Prints the proposal as `h=<hour>:pp.AutoExposureBias=<v>` (look_tod.py --set syntax) and as json.
usage: lapse_opt.py <lapse.json> <keys.txt> --keys-hours 18.8,19.2,... [--hold 18.4,22] [--slope 1.0] [--window 0.25] [--gain 0.8] [--out proposal.json]"""
import argparse, json, math, re
import numpy as np


def parse_key_biases(text):
    """{hour: AutoExposureBias} of a key table text (look_tod.to_text format)"""
    out = {}; h = None
    for ln in text.splitlines():
        t = ln.split()
        if not t: continue
        if t[0] == 'key': h = float(t[1])
        elif t[0] == 'p' and t[1] == 'pp.AutoExposureBias' and h is not None: out[h] = float(t[2])
    return out


def smooth_target(hours, ys, hold, slope, sigma_frames=5, iters=60):
    """cyclic smoothing of the frame-mean series (a 24 h lapse is periodic) with a slope limit and pinned anchors"""
    y = np.asarray(ys, float); n = len(y)
    hrs = np.asarray(hours, float)
    pin = np.zeros(n, bool)
    for h in hold:
        i = int(np.argmin(np.abs(((hrs - h + 12) % 24) - 12))); pin[max(0, i - 2):i + 3] = True
    t = y.copy()
    k = np.exp(-0.5 * (np.arange(-3 * sigma_frames, 3 * sigma_frames + 1) / sigma_frames) ** 2); k /= k.sum()
    for _ in range(iters):
        pad = np.concatenate([t[-len(k):], t, t[:len(k)]])
        s = np.convolve(pad, k, mode='same')[len(k):len(k) + n]
        s[pin] = y[pin]
        # slope limit (cyclic, forward then backward sweep)
        for _ in range(2):
            for i in range(1, n):
                if not pin[i]: s[i] = min(max(s[i], s[i - 1] - slope), s[i - 1] + slope)
            for i in range(n - 2, -1, -1):
                if not pin[i]: s[i] = min(max(s[i], s[i + 1] - slope), s[i + 1] + slope)
        t = s
    return t


def design_target(hours, ys, clips=None, anchors=(), slope=1.3, clip_free=1.2, clip_k=0.08, step=0.25, ymax=200.0, anchor_w=2e4, raise_pen=1.0):
    """round 06, hold 6: the target curve of the closed loop = the curve closest to the measured one (weighted least squares in relative luma) whose frame-to-frame change is <= `slope` Y,
    with the measured values pinned at the `anchors` (hours of the golden / night / dawn stills the other spec lines depend on) and a ceiling where the frame clips (any channel >= 250):
    frames with clipped % above `clip_free` may not exceed measured * max(0.5, 1 - clip_k * (clip - clip_free)). Exact dynamic programme over a luma grid (the cost is separable per frame).
    Returns (target array, info). Unlike smooth_target it can RAISE a valley (a dusk that darkens faster than `slope` is spread out), which is what a slower exposure descent means."""
    y = np.asarray(ys, float); n = len(y); hrs = np.asarray(hours, float)
    clip = np.zeros(n) if clips is None else np.asarray(clips, float)
    levels = np.arange(0.0, ymax + step, step); L = len(levels); k = int(np.floor(slope / step + 1e-9))
    pin = np.zeros(n, bool)
    for h in anchors:
        i = int(np.argmin(np.abs(((hrs - h + 12) % 24) - 12))); pin[i] = True      # one frame per anchor (neighbouring measured frames may differ by more than `slope`)
    ceil = np.where(clip > clip_free, y * np.maximum(0.5, 1.0 - clip_k * (clip - clip_free)), 1e9)
    INF = 1e18
    def cost(i):
        c = (levels - y[i]) ** 2 / (y[i] + 10.0) ** 2
        if raise_pen != 1.0: c = np.where(levels > y[i], c * raise_pen, c)      # asymmetric: brightening a dark valley is costlier than darkening a bump (exposure raises amplify the noise / the clipped sky)
        if pin[i]: c = c * anchor_w                                  # soft pin (a hard one can be infeasible: the measured neighbours of an anchor may differ by more than `slope`)
        c = np.where(levels > ceil[i] + 1e-9, c + 50.0 * (levels - ceil[i]) ** 2 / (y[i] + 10.0) ** 2 + 0.05, c)   # soft ceiling
        return c
    D = np.empty((n, L)); P = np.empty((n, L), np.int32)
    D[0] = cost(0) * 1e3   # start on the measured value
    for i in range(1, n):
        prev = D[i - 1]
        # min over the window [j - k, j + k] of prev: sliding minimum with argmin
        best = np.full(L, INF); arg = np.zeros(L, np.int32)
        for d in range(-k, k + 1):
            lo, hi = max(0, -d), min(L, L - d)
            cand = prev[lo + d:hi + d]
            better = cand < best[lo:hi]
            best[lo:hi] = np.where(better, cand, best[lo:hi]); arg[lo:hi] = np.where(better, np.arange(lo + d, hi + d), arg[lo:hi])
        D[i] = best + cost(i); P[i] = arg
    j = int(np.argmin(D[-1] + cost(n - 1) * 1e3))
    T = np.empty(n)
    for i in range(n - 1, -1, -1):
        T[i] = levels[j]; j = int(P[i][j]) if i > 0 else j
    info = {'max_step': float(np.abs(np.diff(T)).max()), 'rms_change': float(np.sqrt(np.mean((T - y) ** 2))), 'raised_max': float((T - y).max()), 'lowered_max': float((y - T).max())}
    return T, info


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('lapse'); ap.add_argument('keys'); ap.add_argument('--keys-hours', dest='kh', required=True)
    ap.add_argument('--hold', default=''); ap.add_argument('--slope', type=float, default=1.0); ap.add_argument('--window', type=float, default=0.25)
    ap.add_argument('--gain', type=float, default=0.8); ap.add_argument('--out', default='')
    a = ap.parse_args()
    d = json.load(open(a.lapse)); hrs = d['hours_per_frame']; ys = d['mean_y_per_frame']
    bias = parse_key_biases(open(a.keys).read())
    hold = [float(x) for x in a.hold.split(',') if x]
    T = smooth_target(hrs, ys, hold, a.slope)
    Y = np.asarray(ys); dev = np.where(Y > 8.0, 2.2 * np.log2(np.maximum(T, 1.0) / np.maximum(Y, 1.0)), 0.0)
    dev = np.clip(dev, -1.2, 1.2)
    hr = np.asarray(hrs)
    prop = {}
    for kh in [float(x) for x in a.kh.split(',')]:
        dh = ((hr - kh + 12) % 24) - 12
        w = np.clip(1.0 - np.abs(dh) / a.window, 0.0, None)
        if w.sum() <= 0: continue
        delta = float((w * dev).sum() / w.sum()) * a.gain
        old = bias.get(kh)
        if old is None:
            # a key hour that is not in the table: nothing to move
            continue
        prop[kh] = {'old': old, 'delta_ev': round(delta, 3), 'new': round(old + delta, 3)}
    print('target max |dT| per frame %.2f, residual rms %.2f Y' % (float(np.abs(np.diff(T)).max()), float(np.sqrt(np.mean((T - Y) ** 2)))))
    for kh, v in prop.items(): print('h=%g:pp.AutoExposureBias=%g   (was %g, %+.3f EV)' % (kh, v['new'], v['old'], v['delta_ev']))
    if a.out: json.dump({'target': [round(float(x), 2) for x in T], 'proposal': {str(k): v for k, v in prop.items()}}, open(a.out, 'w'), indent=1)


if __name__ == '__main__':
    main()
