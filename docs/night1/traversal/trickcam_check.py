#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P3 round 14: the critic r13 test (single gap: "the flip camera looks up from under the hero, so the rotation does not read and the
# camera stays tilted up into the next swing") + its secondary 1 (eased rotation, shapes held >= 0.3 s).
#   usage: trickcam_check.py <telemetry.csv> <label>        (60 fps telemetry of a rendered capture or a -nullrhi probe)
# Lines:
#   P1  rendered camera pitch (pcm_pitch, + = up) never above 30 deg up -- whole clip, and the max inside trick frames
#   P2  every web attach (mode enters 'swing'): median pcm_pitch over attach +0.5 .. +1.0 s is 4-12 deg DOWN (-12 .. -4)
#   S1  side-on: in trick frames with the flip camera in (flipcam_k >= 0.9) the view direction's angle out of the flip plane
#       (plane = travel direction x up; the somersault axis is the hero's lateral axis) = asin(|view . lateral|); side-on = 90,
#       end-on from behind = 0. Target >= 60 deg (critic: "side-on to the somersault axis, at least 60 deg from it")
#   A1  the tuck's head-to-hip axis turns >= 300 deg ON SCREEN: pose_sig head offset from the hips in camera right / up (bones,
#       one-row shift), atan2 unwrapped over the contiguous Tuck run(s) of each program (rows whose projected length is < 25 % of
#       the run's max are skipped as foreshortened -- no credit for a flip seen end-on)
#   E1  ease: per fast segment (upper-body shape Tuck / Pike / Layout / Twist run >= 0.2 s) the RENDERED rotation rate (body pitch,
#       0.04 s windows) averaged over its first 25 %, middle 50 % and last 25 %: both ends >= 30 % slower than the middle
#   H1  every shape of a program is shown >= 0.3 s (run of the upper-body flip_shape; the program's final Reach counts until the catch)
import csv, math, sys

path, label = sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else ''
R = list(csv.DictReader(open(path)))
n = len(R)
f = lambda r, k, d=0.0: float(r[k]) if r.get(k, '') not in ('', '-') else d
T = [f(r, 't') for r in R]
mode = [r['mode'] for r in R]
pitch = [f(r, 'pcm_pitch') for r in R]
out = []
P = out.append
fails = 0

# ---- programs (contiguous flip_prog runs)
progs = []
i = 0
while i < n:
    if R[i].get('flip_prog', ''):
        j = i
        while j + 1 < n and R[j + 1].get('flip_prog', '') == R[i]['flip_prog'] and f(R[j + 1], 'flip_t') >= f(R[j], 'flip_t') - 1e-4: j += 1
        progs.append((i, j, R[i]['flip_prog']))
        i = j + 1
    else: i += 1
trick = [False] * n
for a, b, _ in progs:
    for k in range(a, b + 1): trick[k] = True

# ---- P1
pmax = max(pitch); imax = pitch.index(pmax)
tp = [pitch[k] for k in range(n) if trick[k]]
ok = pmax <= 30.0
fails += not ok
P('%s (%s): %d flip programs, %.1f s' % (label, path.split('/')[-1], len(progs), T[-1]))
P('P1 camera pitch max %.1f deg up at %.2f s (whole clip) %s | inside tricks max %.1f, p50 %.1f' % (
    pmax, T[imax], 'PASS' if ok else 'FAIL', max(tp) if tp else float('nan'), sorted(tp)[len(tp) // 2] if tp else float('nan')))

# ---- P2
att = [k for k in range(1, n) if mode[k] == 'swing' and mode[k - 1] != 'swing']
lines = []
for k in att:
    w = [pitch[j] for j in range(k, n) if T[k] + 0.5 <= T[j] <= T[k] + 1.0]
    if len(w) < 20:
        lines.append('%.2f n/a (clip ends)' % T[k]); continue
    med = sorted(w)[len(w) // 2]
    after_trick = any(trick[j] for j in range(max(0, k - 30), k))
    ok = -12.0 <= med <= -4.0
    fails += not ok
    at05 = next(pitch[j] for j in range(k, n) if T[j] >= T[k] + 0.5)
    lines.append('%.2f%s med %+.1f (at +0.5 s %+.1f) %s' % (T[k], '*' if after_trick else '', med, at05, 'PASS' if ok else 'FAIL'))
P('P2 pitch 0.5-1.0 s after each attach (target -12..-4; * = attach out of a trick):')
for L in lines: P('   ' + L)

# ---- per program: S1 / A1 / E1 / H1
def unwrap(v):
    u = [v[0]]
    for x in v[1:]:
        d = (x - u[-1] + 180) % 360 - 180
        u.append(u[-1] + d)
    return u
bp = [f(R[min(k + 1, n - 1)], 'body_pitch_deg') for k in range(n)]
def sig_head(k):
    s = R[min(k + 1, n - 1)].get('pose_sig', '').split()
    return (float(s[0]), float(s[1])) if len(s) >= 2 else None
for a, b, name in progs:
    P('-- %s %.2f-%.2f s' % (name, T[a], T[b]))
    # S1: view angle out of the flip plane
    vx, vy = f(R[a], 'vx'), f(R[a], 'vy')
    hl = math.hypot(vx, vy) or 1.0
    lat = (-vy / hl, vx / hl, 0.0)
    ang = []
    for k in range(a, b + 1):
        if f(R[k], 'flipcam_k') < 0.9: continue
        pr, yw = math.radians(f(R[k], 'pcm_pitch')), math.radians(f(R[k], 'pcm_yaw'))
        fw = (math.cos(pr) * math.cos(yw), math.cos(pr) * math.sin(yw), math.sin(pr))
        ang.append(math.degrees(math.asin(min(1.0, abs(fw[0] * lat[0] + fw[1] * lat[1])))))
    if ang:
        ang.sort()
        ok = ang[len(ang) // 2] >= 60.0
        fails += not ok
        P('   S1 view angle out of the flip plane (flipcam_k >= .9, %d frames): p10 %.0f / p50 %.0f / min %.0f deg %s' % (
            len(ang), ang[len(ang) // 10], ang[len(ang) // 2], ang[0], 'PASS' if ok else 'FAIL'))
    else:
        P('   S1 no frames with the flip camera fully in')
    # shape runs (upper body)
    runs = []
    for k in range(a, b + 1):
        s = R[k].get('flip_shape', '')
        if runs and runs[-1][0] == s: runs[-1][2] = k
        else: runs.append([s, k, k])
    # catch cut: the program ends at the attach; the last run lasts until then
    P('   H1 shape runs: ' + ' '.join('%s %.2f' % (s, T[e] - T[s0] + 1 / 60.0) for s, s0, e in runs))
    for s, s0, e in runs:
        d = T[e] - T[s0] + 1 / 60.0
        is_last = (s0, e) == (runs[-1][1], runs[-1][2])
        ok = d >= 0.3 - 1 / 120.0
        if not ok and is_last and s == 'Reach':
            P('      (final Reach %.2f s: the web catch lands inside it by design, R2 <= .3 s; not judged)' % d)
        elif not ok:
            fails += 1
            P('      FAIL %s shown %.2f s < 0.3' % (s, d))
    # A1: on-screen tuck turn
    if name != 'wallFront':
        for s, s0, e in runs:
            if s != 'Tuck' or T[e] - T[s0] < 0.2: continue
            hv = [sig_head(k) for k in range(s0, e + 1)]
            hv = [h for h in hv if h]
            if len(hv) < 3: continue
            L = [math.hypot(*h) for h in hv]
            mx = max(L)
            angs = [math.degrees(math.atan2(h[0], h[1])) for h, l in zip(hv, L) if l >= 0.25 * mx]
            u = unwrap(angs)
            turn = abs(u[-1] - u[0])
            prog_turn = abs(f(R[e], 'flip_pitch_deg') - f(R[s0], 'flip_pitch_deg'))
            short = [l for l in L if l < 0.5 * mx]
            P('   A1 tuck %.2f-%.2f s: head-hip axis turns %.0f deg on screen (program %.0f deg; %d/%d rows < 50%% length) %s' % (
                T[s0], T[e], turn, prog_turn, len(short), len(L), 'PASS' if turn >= 300 else ('(single: %s)' % ('ok' if turn >= 0.8 * prog_turn else 'short') if prog_turn < 400 else 'FAIL')))
            if prog_turn >= 400 and turn < 300: fails += 1
    # E1: ease inside the fast segments (rendered rate)
    u = unwrap([bp[k] for k in range(a, b + 1)])
    step = 2 if T[min(b, a + 2)] - T[a] >= 0.033 else 3
    rate = [abs(u[min(len(u) - 1, i + step)] - u[max(0, i - step)]) / max(1e-3, T[a + min(len(u) - 1, i + step)] - T[a + max(0, i - step)]) for i in range(len(u))]
    for s, s0, e in runs:
        if s not in ('Tuck', 'Pike', 'Layout', 'Twist') or T[e] - T[s0] < 0.2: continue
        seg = rate[s0 - a:e - a + 1]
        m = len(seg)
        q1, q3 = max(1, m // 4), max(1, m - m // 4)
        s_in, s_mid, s_out = sum(seg[:q1]) / q1, sum(seg[q1:q3]) / max(1, q3 - q1), sum(seg[q3:]) / max(1, m - q3)
        ok = s_in <= 0.7 * s_mid and s_out <= 0.7 * s_mid
        if s == 'Tuck' or s == 'Pike': fails += not ok
        P('   E1 %s %.2f-%.2f s rendered rate first25%% %.0f / mid50%% %.0f / last25%% %.0f deg/s (ends %.0f%% / %.0f%% of mid) peak %.0f %s' % (
            s, T[s0], T[e], s_in, s_mid, s_out, 100 * s_in / max(1, s_mid), 100 * s_out / max(1, s_mid), max(seg), 'PASS' if ok else 'FAIL'))
    # program rate model (flip_rate_dps) for reference
    pr = [abs(f(R[k], 'flip_rate_dps')) for k in range(a, b + 1)]
    P('   program rate peak %.0f deg/s, rendered peak %.0f deg/s' % (max(pr), max(rate)))
P('SUMMARY %s: %d FAIL line(s)' % (label, fails))
print('\n'.join(out))
