# CPU mock of Foliage.ush TerrainClumpCrown on a flat patch (shader-only contribution to the 4K high-pass SD); numpy port, not the real render
import numpy as np, sys
from scipy.ndimage import gaussian_filter
def frac(x): return x - np.floor(x)
def h3(p):
    p = frac(p * 0.1031); d = (p * (p[..., [1, 2, 0]] + 33.33)).sum(-1)
    p = p + d[..., None]
    return frac((p[..., 0] + p[..., 1]) * p[..., 2])
def vn(p):
    i = np.floor(p); f = p - i; f = f * f * (3 - 2 * f)
    def H(o): return h3(i + np.array(o, float))
    a = (H((0,0,0)) * (1-f[...,0]) + H((1,0,0)) * f[...,0]) * (1-f[...,1]) + (H((0,1,0)) * (1-f[...,0]) + H((1,1,0)) * f[...,0]) * f[...,1]
    b = (H((0,0,1)) * (1-f[...,0]) + H((1,0,1)) * f[...,0]) * (1-f[...,1]) + (H((0,1,1)) * (1-f[...,0]) + H((1,1,1)) * f[...,0]) * f[...,1]
    return a * (1 - f[..., 2]) + b * f[..., 2]
def clump(cp):
    n1 = vn(cp * 0.62); n2 = vn(cp * 2.1 + 3.1); n3 = vn(cp * 5.3 + 7.7)
    return n1 * 0.65 + n2 * 0.35, n1, n2, n3
def bumph(cp):
    c, n1, n2, n3 = clump(cp); return c * 3 + n3 * 0.5
def smooth(a, b, x): t = np.clip((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)
def run(D, bumpgain=1.0, tilt_deg=35, px=500, seed=3):
    rng = np.random.default_rng(seed)
    foot = 0.000338 * D   # metres per 4K px (hfov 66 deg)
    xs = (np.arange(px) - px / 2) * foot; ys = (np.arange(px) - px / 2) * foot
    X, Y = np.meshgrid(xs, ys)
    th = np.radians(tilt_deg)          # surface tilted towards the camera: normal N0 = (0, -sin, cos)? use facing = cos(tilt)
    P = np.stack([X + 811.0, Y * np.cos(th) + 400.0, Y * np.sin(th) + 55.0], -1)   # world position (metres) of the crown surface seen by each pixel (offset like a real tree)
    cp = P + np.array([0.37, 0.53, 0.29]) * rng.random() * 100
    c, n1, n2, n3 = clump(cp)
    cov = smooth(0.18, 0.55, c * 0.8 + n3 * 0.35)
    expo = np.clip(0.55 + 0.35 * np.sin(Y / (15 * foot / 0.1) + 1.0) + 0.1 * (rng.random((px, px)) - 0.5) * 0, 0, 1)   # slow exposure gradient (vertex aLeaf)
    lv = 0.5
    tA = np.array([0.23, 0.214, 0.078]); tB = np.array([0.13, 0.13, 0.053])
    hsel = 0.5 + (n2 - 0.5) * 0.7 + (lv - 0.5) * 0.35 + (n1 - 0.5) * 0.4
    leaf = tA + (tB - tA) * smooth(0.1, 0.9, hsel)[..., None]
    leaf = leaf * (0.74 + 0.34 * n3)[..., None]
    col = tB * 0.42 + (leaf - tB * 0.42) * smooth(0.3, 0.62, c + n3 * 0.22)[..., None]
    col = col * (1 + (np.array([1.12, 1.1, 0.8]) - 1) * (smooth(0.62, 0.9, n2) * 0.6)[..., None])
    occ = (0.3 + (1.14 - 0.3) * expo ** 1.25) * (0.66 + (1.1 - 0.66) * smooth(0.3, 0.75, c))
    alb = col * occ[..., None]
    # normal from the gradient
    e = 0.12; h0 = bumph(cp)
    g = np.stack([(bumph(cp + np.array([e,0,0])) - h0) / e, (bumph(cp + np.array([0,e,0])) - h0) / e, (bumph(cp + np.array([0,0,e])) - h0) / e], -1)
    N0 = np.array([0.0, -np.sin(th) * 0 + np.sin(th), np.cos(th)]) ; N0 = N0 / np.linalg.norm(N0)
    g = g - (g @ N0)[..., None] * N0
    k = np.clip(0.0012 * D, 0.04, 0.25) * bumpgain
    N = N0 - g * k; N = N / np.linalg.norm(N, axis=-1, keepdims=True)
    L = np.array([0.55, -0.35, 0.3]); L = L / np.linalg.norm(L)    # golden-hour sun
    sun = np.clip(N @ L, 0, 1)
    amb = 0.35
    lum = (alb * (amb + 2.2 * sun)[..., None])
    Yl = 0.2126 * lum[..., 0] + 0.7152 * lum[..., 1] + 0.0722 * lum[..., 2]
    # alpha mask: stochastic coverage -> expected opacity; see-through shows a darker interior (0.35 of the albedo, shaded)
    facing = abs(N @ np.array([0, 0, 1.0]))
    alpha = np.where(facing < 0.72, cov * 1.25 * (1 - smooth(0.3, 0.72, facing)) + smooth(0.3, 0.72, facing), 1.0)
    alpha = np.clip(alpha, 0, 1)
    Yl = Yl * alpha + (1 - alpha) * 0.02
    # tonemap-ish display value
    disp = 255 * np.clip(Yl * 1.6, 0, 1) ** (1 / 2.2)
    hp = disp - gaussian_filter(disp, 3.0)
    crop = hp[px // 2 - 75: px // 2 + 75, px // 2 - 75: px // 2 + 75]
    return float(crop.std()), float(disp.mean()), float(alpha.mean())
for D in (120, 200, 300, 450, 520):
    print(D, ['bump %.1f: sd %.2f mean %.0f alpha %.2f' % ((b,) + run(D, b)) for b in (0.0, 1.0, 1.6)])
