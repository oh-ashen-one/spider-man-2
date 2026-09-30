# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""Round 07: search a crowd layout (lane offset dy + start x0 per walker) whose STRAIGHT-LINE paths never bring two walkers closer than MINSEP
(so the runtime avoidance has nothing to do in the shots), keeps the two-way flow (right-hand traffic: the +X stream on the +Y = camera side of
each lane pair) and a busy tracking / wide frame.  Both director shots are checked: tracking 8 s (camera follows x = 110 t) and wide 6 s
(restart at LineStart).  Output: the chosen table as JSON, printed as the python literal build_characters.py contains.

  python3 tools/ue_char/crowd/layout_search.py [--seed 1] [--iters 6000] [--minsep 115]
"""
import sys, json, math
import numpy as np
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import avoid_sim as A

seed = 1; iters = 6000; MINSEP = 115.0
a = sys.argv[1:]
if '--seed' in a: seed = int(a[a.index('--seed') + 1])
if '--iters' in a: iters = int(a[a.index('--iters') + 1])
if '--minsep' in a: MINSEP = float(a[a.index('--minsep') + 1])
rng = np.random.default_rng(seed)

NAMES = [c for c, *_ in A.MID_R6 + A.NEAR_R6]
DIR0 = {c: d for c, _, _, d in A.MID_R6 + A.NEAR_R6}
X00 = {c: x for c, _, x, _ in A.MID_R6 + A.NEAR_R6}
NEAR = [c for c, *_ in A.NEAR_R6]
SPD = np.array([A.SPEED[A.STYLE[c]] for c in NAMES])
DIRS = np.array([DIR0[c] for c in NAMES], float)
isnear = np.array([c in NEAR for c in NAMES])
TA = np.arange(0, 8.0, 1 / 30.0); TB = np.arange(0, 6.0, 1 / 30.0)
TAV = np.arange(0, 10.0, 1 / 30.0); TBV = np.arange(0, 8.0, 1 / 30.0)   # separation is checked 2 s beyond each shot (the avoidance look-ahead)
FOV_T = 64.0; CAMD_T = 1150.0; CAMH = 45.0   # tracking: distance to the tracked point on the mid lane centre line y = CY5
CAM_W = (-1400.0, A.CY5 + 420.0)             # wide camera


TAN_T = math.tan(math.radians(FOV_T / 2)); HALFW = 45.0          # silhouette half width incl. arms / stride, cm
WIDE_FOV = 50.0; WIDE_AIM = (500.0, A.CY5)


def screen_overlap(dy, x0):
    """(mean visible count, mean near count, fraction of frames with >= 1 overlapping pair of screen silhouettes) in the tracking shot"""
    Xc = x0[:, None] + (DIRS * SPD)[:, None] * TA[None, :] - 110.0 * TA[None, :]            # x relative to the camera
    depth = (CAMD_T - dy)[:, None] * np.ones_like(Xc)
    u = Xc / (depth * TAN_T); hw = HALFW / (depth * TAN_T)
    vis = (np.abs(u) < 1.0)
    lo, hi = u - hw, u + hw
    ov = np.zeros(len(TA), bool); npair = 0
    n = len(dy)
    for i in range(n):
        for j in range(i + 1, n):
            o = vis[i] & vis[j] & (lo[i] < hi[j]) & (lo[j] < hi[i])
            ov |= o; npair += int(o.sum())
    return vis.sum(0).mean(), (vis & isnear[:, None]).sum(0).mean(), float(ov.mean()), npair / len(TA)


def wide_count(dy, x0):
    cam = np.array(CAM_W); aim = np.array(WIDE_AIM); f = aim - cam; yaw0 = math.atan2(f[1], f[0])
    X = x0[:, None] + (DIRS * SPD)[:, None] * TB[None, :]; Y = (A.CY5 + dy)[:, None] * np.ones_like(X)
    ang = np.arctan2(Y - cam[1], X - cam[0]) - yaw0
    return (np.abs(ang) < math.radians(WIDE_FOV / 2 - 3)).sum(0).mean()


def cost(dy, x0):
    """violations (pair-frames below MINSEP) + soft terms"""
    v = 0.0; minall = 1e9
    for T in (TAV, TBV):
        X = x0[:, None] + (DIRS * SPD)[:, None] * T[None, :]              # (n, T)
        dx = X[:, None, :] - X[None, :, :]                                # (n, n, T)
        dyy = (dy[:, None] - dy[None, :])[:, :, None]
        d = np.sqrt(dx * dx + dyy * dyy)
        iu = np.triu_indices(len(dy), 1)
        dd = d[iu]                                                        # (pairs, T)
        v += float(np.maximum(MINSEP - dd, 0.0).sum()) / 30.0
        minall = min(minall, float(dd.min()))
    dens, near_vis, ovf, npair = screen_overlap(dy, x0)
    return v, minall, dens, near_vis, ovf, npair, wide_count(dy, x0)


def penalty(dy, x0):
    v, mn, dens, nv, ovf, npair, wc = cost(dy, x0)
    p = v * 5.0
    p += max(0.0, 12.0 - dens) * 8.0                                     # want >= 12 people in the tracking frame on average
    p += max(0.0, 3.0 - nv) * 8.0                                        # want >= 3 near-lane walkers in frame
    p += max(0.0, 13.0 - wc) * 4.0                                       # wide shot
    p += ovf * 12.0 + npair * 3.0                                        # screen-silhouette overlaps (occlusions), soft
    return p, (v, mn, dens, nv, ovf, npair, wc)


def lo_hi(c):
    return (690, 820) if c in NEAR and DIR0[c] > 0 else ((560, 670) if c in NEAR else (-340, 340))


dy = np.array([d for c, d, *_ in [(c, dd) for c, dd, _, _ in A.MID_R6 + A.NEAR_R6]], float)
x0 = np.array([X00[c] for c in NAMES], float)
best = (1e18, None)
cur_p, cur_m = penalty(dy, x0)
T0 = 30.0
for it in range(iters):
    i = rng.integers(len(NAMES)); c = NAMES[i]
    ndy = dy.copy(); nx0 = x0.copy()
    if rng.random() < 0.6:
        lo, hi = lo_hi(c); ndy[i] = np.clip(round((dy[i] + rng.normal(0, 60)) / 10) * 10, lo, hi)
    else:
        nx0[i] = np.clip(round((x0[i] + rng.normal(0, 250)) / 10) * 10, X00[c] - 900, X00[c] + 900)
    p, m = penalty(ndy, nx0)
    temp = T0 * (1 - it / iters) + 0.05
    if p < cur_p or rng.random() < math.exp(-(p - cur_p) / temp):
        dy, x0, cur_p, cur_m = ndy, nx0, p, m
        if p < best[0]: best = (p, (dy.copy(), x0.copy(), m))
p, (dy, x0, m) = best
print('penalty %.1f  violations %.2f  min pair distance %.1f cm  tracking density %.2f  near in frame %.2f  frames with a screen overlap %.2f  mean overlapping pairs %.2f  wide count %.2f' % ((p,) + m))
rows = [(c, int(dy[i]), int(x0[i]), int(DIRS[i])) for i, c in enumerate(NAMES)]
mid = [r for r in rows if r[0] not in NEAR]; near = [r for r in rows if r[0] in NEAR]
print('MID =', mid); print('NEAR =', near)
json.dump(dict(mid=mid, near=near, minsep=MINSEP, min_pair_cm=m[1], density=m[2], overlap_frames=m[4], wide=m[6]), open('/Users/midir/sm2-n1/_scratch/characters/r7/layout_seed%d.json' % seed, 'w'))
