import sys, math
# offline replica of WebFlips rate model (round 14: per-segment ease = inertia multiplier ramps at the segment ends)
I = {'Tuck': 1.0, 'Pike': 1.35, 'Layout': 3.2, 'Swan': 7.5, 'Pencil': 9, 'Straddle': 6, 'Throne': 9, 'Twist': 3.5, 'Reach': 7, 'Kickout': 9.0}
def sm(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
BPre, BPost = 0.06, 0.11
EW = 0.45
def run(name, pitch, segs, catch=0.16, quiet=False):
    # seg = (shape, dur, easeIn, easeOut)
    segs = [s if len(s) == 4 else (s[0], s[1], 0, 0) for s in segs]
    dur = sum(s[1] for s in segs)
    starts = []; a = 0
    for s in segs: starts.append(a); a += s[1]
    def segI(k, t):
        sh, d, ei, eo = segs[k]
        u = min(max((t - starts[k]) / d, 0), 1)
        m = 1 + ei * (1 - sm(u / EW)) + eo * (1 - sm((1 - u) / EW))
        return I[sh] * m
    def inert(t):
        k = 0
        for i in range(len(segs)):
            if t >= starts[i]: k = i
        S0 = starts[k]; S1 = S0 + segs[k][1]
        if k > 0 and t < S0 + BPost:
            w = sm((t - (S0 - BPre)) / (BPre + BPost)); return segI(k - 1, t) * (1 - w) + segI(k, t) * w
        if k + 1 < len(segs) and t > S1 - BPre:
            w = sm((t - (S1 - BPre)) / (BPre + BPost)); return segI(k, t) * (1 - w) + segI(k + 1, t) * w
        return segI(k, t)
    def env(t): return (0.35 + 0.65 * sm(t / 0.12)) * (0.12 + 0.88 * sm((dur - t) / 0.22))
    N = int(dur * 240) + 1; g = 0; rates = []
    for i in range(N):
        t = (i + 0.5) / 240; x = env(t) / inert(t); g += x / 240; rates.append((t, x))
    L = abs(pitch) / g
    r = [(t, L * x) for t, x in rates]
    peak = max(x for _, x in r)
    tc = dur - catch
    # hold <= 150 before the catch
    best = cur = 0
    for t, x in r:
        if t > tc: break
        cur = cur + 1 / 240 if x <= 150 else 0; best = max(best, cur)
    acc = 0; at_catch = 0
    for t, x in r:
        acc += x / 240
        if t <= tc: at_catch = acc
    line = f"{name}: dur {dur:.2f} catch@{tc:.2f} peak {peak:.0f} mean {abs(pitch)/dur:.0f} hold<=150 {best:.2f}s deg@catch {at_catch:.0f}/{abs(pitch)}"
    print(line)
    # per segment quartile ratios (program rate), fast segs
    for k, s in enumerate(segs):
        seg = [x for t, x in r if starts[k] <= t < starts[k] + s[1]]
        m = len(seg); q1, q3 = m // 4, m - m // 4
        a_, b_, c_ = sum(seg[:q1]) / q1, sum(seg[q1:q3]) / (q3 - q1), sum(seg[q3:]) / (m - q3)
        tot = sum(seg) / 240
        print(f"   {s[0]:8s} {s[1]:.2f}s  {tot:5.0f} deg  q {a_:4.0f}/{b_:4.0f}/{c_:4.0f} ({100*a_/b_:.0f}%/{100*c_/b_:.0f}%) peak {max(seg):.0f} min {min(seg):.0f}")
    return r

if __name__ == '__main__':
    exec(open(sys.argv[1]).read()) if len(sys.argv) > 1 else None
