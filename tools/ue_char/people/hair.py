#!/usr/bin/env python3
"""Round 11 (critic r10, single biggest gap: 'give every head ONE hair asset'): hair clean-up of the street enemies before skinfit.

Fan homage project; not an official Marvel, Sony or Insomniac game; no affiliation.

The raw Tripo heads carry their hair in one of two ways:
  * a separate hair SHELL (Beard, Tee): a component of its own over the head surface. Its open edges hang 3 - 15 mm off the head (temple
    curtain of the Beard), so the background or the scalp's skin shows between hair and face; round 10 bridged the Beard's gap with a strip
    textured by ONE hair texel = a flat brown card (critic r10: 125 x 220 px at 4K).  Here: tuck_hair() pulls every open-edge vertex of the
    shell that floats within `reach` of the head onto the head surface (+ a 1.2 mm lift), with a smooth fall-off into the shell, and
    paint_scalp() gives the scalp texels that lie UNDER the shell the hair's own dark colour, so any remaining crack shows hair, not skin.
  * hair painted on the body surface (Hood): two colours (maroon curls over a blond side / back) read as two overlapping hair meshes with
    a 570 px seam.  unify_hair() recolours the blond hair texels into the maroon palette (luminance quantile mapping, hue / chroma of the
    maroon) so the head has one hair colour.
"""
import numpy as np
import cv2
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from scipy import sparse
from scipy.sparse.csgraph import connected_components


def _rgb2hsv(a):
    a = a.astype(np.float32) / 255.0
    mx, mn = a.max(-1), a.min(-1)
    d = mx - mn + 1e-9
    h = np.where(mx == a[..., 0], ((a[..., 1] - a[..., 2]) / d) % 6, np.where(mx == a[..., 1], (a[..., 2] - a[..., 0]) / d + 2, (a[..., 0] - a[..., 1]) / d + 4)) * 60.0
    s = np.where(mx > 0, (mx - mn) / (mx + 1e-9), 0.0)
    return h, s, mx


def weld(P, tol=1e-4):
    key = np.round(P / tol).astype(np.int64)
    _, inv = np.unique(key, axis=0, return_inverse=True)
    return inv.ravel()


def face_components(P, F):
    w = weld(P); n = w.max() + 1
    e = np.concatenate([F[:, [0, 1]], F[:, [1, 2]]])
    g = sparse.coo_matrix((np.ones(len(e)), (w[e[:, 0]], w[e[:, 1]])), shape=(n, n))
    _, lab = connected_components(g, directed=False)
    return lab[w[F[:, 0]]]


def hair_shell(P, F, y_min=1.50, min_tris=800):
    """Face mask of the hair shell: the biggest component lying entirely above y_min (the body / head component reaches the feet)."""
    fl = face_components(P, F)
    ymin = np.full(fl.max() + 1, 1e9); np.minimum.at(ymin, fl, P[F][:, :, 1].min(1))
    size = np.bincount(fl)
    cand = np.where((ymin > y_min) & (size >= min_tris))[0]
    if not len(cand): return np.zeros(len(F), bool)
    best = cand[np.argmax(size[cand])]
    return fl == best


def _surface_samples(P, F, k=6):
    """Points + face normals sampled on the triangles F (barycentric grid with k steps per edge)."""
    bc = [(i / k, j / k) for i in range(k + 1) for j in range(k + 1 - i)]
    bc = np.array([(a, b, 1 - a - b) for a, b in bc])
    T = P[F]
    S = np.einsum('bk,fkd->fbd', bc, T).reshape(-1, 3)
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    return S, np.repeat(n, len(bc), 0)


def tuck_hair(P, F, H, axis_z=-0.02, y_min=1.50, reach=0.016, falloff=0.006, lift=0.0012):
    """Open-edge vertices of the hair shell (faces H) that float outside the head surface within `reach` are moved onto it (+ lift along the
    head's normal); the other shell vertices follow with weight exp(-(d / falloff)^2), d = distance to the nearest tucked edge vertex.
    Returns (P, info)."""
    w = weld(P); nw = w.max() + 1
    head = (~H) & (P[F][:, :, 1].min(1) > y_min - 0.12) & (np.hypot(P[F][:, :, 0], P[F][:, :, 2] - axis_z).max(1) < 0.16)
    S, Sn = _surface_samples(P, F[head])
    tree = cKDTree(S)
    FH = w[F[H]]
    e = np.concatenate([FH[:, [0, 1]], FH[:, [1, 2]], FH[:, [2, 0]]])
    lo = np.minimum(e[:, 0], e[:, 1]); hi = np.maximum(e[:, 0], e[:, 1])
    u, c = np.unique(lo.astype(np.int64) * nw + hi, return_counts=True)
    bv = np.unique(np.concatenate([u[c == 1] // nw, u[c == 1] % nw])).astype(int)
    rep = np.zeros((nw, 3)); rep[w] = P
    d, i = tree.query(rep[bv])
    side = ((rep[bv] - S[i]) * Sn[i]).sum(1)                 # > 0: the edge vertex is outside the head surface
    tuck = (d < reach) & (side > -0.001)
    disp = np.zeros((nw, 3))
    tv = bv[tuck]
    target = S[i[tuck]] + Sn[i[tuck]] * lift
    disp[tv] = target - rep[tv]
    # propagate into the shell
    hv = np.unique(FH)
    if len(tv):
        tt = cKDTree(rep[tv])
        dd, j = tt.query(rep[hv])
        wgt = np.exp(-(dd / falloff) ** 2)
        other = ~np.isin(hv, tv)
        disp[hv[other]] = disp[tv[j[other]]] * wgt[other][:, None]
    P2 = P + disp[w]
    return P2, dict(hair_edge_verts=int(len(bv)), tucked_edge_verts=int(tuck.sum()), tuck_max_mm=round(float(np.linalg.norm(disp, axis=1).max() * 1000), 1),
                    tuck_mean_mm=round(float(np.linalg.norm(disp[tv], axis=1).mean() * 1000), 1) if len(tv) else 0.0)


def _uv_mask(UV, F, n):
    m = np.zeros((n, n), np.uint8)
    pts = (UV[F] * n).astype(np.int32)
    cv2.fillPoly(m, list(pts), 1)
    for p in pts: cv2.polylines(m, [p], True, 1, 1)
    return m.astype(bool)


def paint_scalp(img, cov, pos, P, N, UV, F, H, axis_z=-0.02, y_min=1.50, reach=0.045, seed=7):
    """Head-surface texels (not the shell's own) whose surface point is covered by the shell (a ray along the head normal hits it within
    `reach`) take the shell's own dark hair colour with a fine strand noise.  Returns (img, info)."""
    n = img.shape[0]
    Hm = _uv_mask(UV, F[H], n)
    wv = weld(P)
    head = (~H) & (P[F][:, :, 1].min(1) > y_min - 0.10) & (np.hypot(P[F][:, :, 0], P[F][:, :, 2] - axis_z).max(1) < 0.16)
    vids = np.unique(F[head])
    # vertex normals of the head part
    T = P[F[head]]; fn = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
    vn = np.zeros((wv.max() + 1, 3)); np.add.at(vn, wv[F[head]].ravel(), np.repeat(fn, 3, 0))
    vn /= np.linalg.norm(vn, axis=1, keepdims=True) + 1e-12
    O = P[vids]; D = vn[wv[vids]]
    from mask import _ray_hits_any
    hit = _ray_hits_any(O - D * 0.006, D, P, F[H], reach + 0.006)   # from 6 mm inside: shell triangles within 2 mm of the scalp count too
    region = cov & ~Hm & (pos[..., 1] > y_min - 0.10) & (np.hypot(pos[..., 0], pos[..., 2] - axis_z) < 0.16)
    ys, xs = np.nonzero(region)
    tree = cKDTree(O)
    dd, j = tree.query(pos[ys, xs].astype(np.float64), k=4)
    wk = 1.0 / (dd + 1e-4)
    cvr = (hit[j] * wk).sum(1) / wk.sum(1)
    W = np.zeros(region.shape, np.float32); W[ys, xs] = np.clip((cvr - 0.25) / 0.5, 0, 1)
    W = ndi.gaussian_filter(W, 1.2) * region
    a = img.astype(np.float32)
    hair_px = a[Hm & cov]
    lum = hair_px @ np.array([0.299, 0.587, 0.114], np.float32)
    dark = hair_px[lum <= np.percentile(lum, 45)]
    base = np.median(dark, 0)
    rng = np.random.RandomState(seed)
    g = ndi.gaussian_filter(rng.randn(n, n).astype(np.float32), (0.7, 2.5)); g /= g.std() + 1e-6
    col = base[None, None, :] * np.clip(0.9 + 0.18 * g, 0.6, 1.4)[..., None]
    out = a * (1 - W[..., None]) + col * W[..., None]
    return np.clip(out, 0, 255).astype(np.uint8), dict(scalp_verts_covered=int(hit.sum()), scalp_verts=int(len(vids)), scalp_texels=int((W > 0.5).sum()),
                                                       scalp_colour=[int(x) for x in base])


def unify_hair(img, cov, pos, cfg, y_lo=None):
    """Blond hair texels of the head (hue 26 - 62 deg, saturation 0.08 - 0.55, value > 0.42, above the ear lobe, off the face front)
    take the maroon palette: luminance quantile-mapped onto the maroon hair texels', chroma = the maroon median's.  Feathered by hue."""
    h, s, v = _rgb2hsv(img)
    x, y, z = pos[..., 0], pos[..., 1], pos[..., 2]
    az = cfg.get('axis_z', -0.02)
    r = np.hypot(x, z - az)
    ylo = cfg['ear_lobe'] - 0.01 if y_lo is None else y_lo
    headz = cov & (y > ylo) & (r < 0.16)
    face = (z - az > 0.045) & (y < cfg['eye'] + 0.035) & (np.abs(x) < 0.075)     # eyes / brows / glasses / nose bridge
    a = img.astype(np.float32)
    lum = a @ np.array([0.299, 0.587, 0.114], np.float32)
    maroon = headz & ~face & ((h > 330) | (h < 24)) & (s > 0.22) & (v < 0.62)
    # light (blond) hair = pale-warm AND strand-textured (the skin of the forehead / ears is smooth): local luminance std over 9 x 9 texels, averaged over 15 x 15
    l1 = cv2.blur(lum, (9, 9)); l2 = cv2.blur(lum * lum, (9, 9)); tex = cv2.blur(np.sqrt(np.maximum(l2 - l1 * l1, 0)), (15, 15))
    hue_w = np.clip((h - 12) / 6, 0, 1) * np.clip((68 - h) / 6, 0, 1)
    W = hue_w * (headz & ~face & (s < 0.62) & (lum > 95) & ~maroon) * np.clip((tex - 5.0) / 3.0, 0, 1)
    W = ndi.gaussian_filter(W.astype(np.float32), 0.8) * headz
    ml = lum[maroon]; bl = lum[W > 0.5]
    qs = np.linspace(0, 100, 101)
    mq = np.percentile(ml, qs); bq = np.percentile(bl, qs)
    lum_new = np.interp(lum, bq, mq)
    mc = np.median(a[maroon], 0); mc_l = float(mc @ np.array([0.299, 0.587, 0.114]))
    col = mc[None, None, :] * (lum_new / max(mc_l, 1.0))[..., None]
    out = a * (1 - W[..., None]) + col * W[..., None]
    return np.clip(out, 0, 255).astype(np.uint8), dict(unify_blond_texels=int((W > 0.5).sum()), unify_maroon_texels=int(maroon.sum()), unify_target=[int(x_) for x_ in mc])


def fringe_hairline(img, cov, pos, P, F, cfg, band=0.009, seed=5):
    """Hood: the maroon fringe overhangs the forehead with a straight 45-cm-long edge (critic r10: '570 px seam').  Forehead texels UNDER the overhang
    (a ray along the head normal hits the head's own fringe within 4 cm) and a band of `band` metres beyond it (noisy, feathered edge) take the
    maroon hair palette, so the fringe edge lies on hair and the hairline below it is soft and irregular."""
    az = cfg.get('axis_z', -0.02); eye = cfg['eye']
    wv = weld(P)
    T = P[F]; fn = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
    vn = np.zeros((wv.max() + 1, 3)); np.add.at(vn, wv[F].ravel(), np.repeat(fn, 3, 0)); vn /= np.linalg.norm(vn, axis=1, keepdims=True) + 1e-12
    used = np.unique(F)
    q = P[used]
    zone_v = (q[:, 1] > eye + 0.004) & (q[:, 1] < eye + 0.10) & (q[:, 2] - az > 0.02) & (np.hypot(q[:, 0], q[:, 2] - az) < 0.16)
    vid = used[zone_v]
    headF = F[(T[:, :, 1].min(1) > eye - 0.02) & (np.hypot(T[:, :, 0], T[:, :, 2] - az).max(1) < 0.17)]
    from mask import _ray_hits_any
    hit = _ray_hits_any(P[vid] + vn[wv[vid]] * 0.0005, vn[wv[vid]], P, headF, 0.04, skip_verts=vid)
    cv_ = vid[hit]
    if not len(cv_): return img, dict(fringe_covered_verts=0)
    a = img.astype(np.float32); lum = a @ np.array([0.299, 0.587, 0.114], np.float32)
    h, s_, v = _rgb2hsv(img)
    x, y, z = pos[..., 0], pos[..., 1], pos[..., 2]
    region = cov & (y > eye + 0.004) & (y < eye + 0.10) & (z - az > 0.0) & (np.hypot(x, z - az) < 0.16)
    ys, xs = np.nonzero(region)
    d, _ = cKDTree(P[cv_]).query(pos[ys, xs].astype(np.float64))
    rng = np.random.RandomState(seed); n = img.shape[0]
    nz = ndi.gaussian_filter(rng.randn(n // 8, n // 8).astype(np.float32), 1.5); nz /= nz.std() + 1e-6
    nz = cv2.resize(nz, (n, n), interpolation=cv2.INTER_LINEAR)
    lim = band * (1.0 + 0.35 * nz[ys, xs])
    w = 1.0 - np.clip((d - 0.6 * lim) / (0.4 * lim + 1e-6), 0, 1)
    W = np.zeros(region.shape, np.float32); W[ys, xs] = w
    W = ndi.gaussian_filter(W, 1.0) * region
    maroon = cov & (y > eye) & ((h > 330) | (h < 24)) & (s_ > 0.22) & (v < 0.62)
    mc = np.median(a[maroon], 0)
    g = ndi.gaussian_filter(rng.randn(n, n).astype(np.float32), (0.6, 2.2)); g /= g.std() + 1e-6
    col = mc[None, None, :] * np.clip(0.80 + 0.22 * g, 0.5, 1.3)[..., None]
    out = a * (1 - W[..., None]) + col * W[..., None]
    return np.clip(out, 0, 255).astype(np.uint8), dict(fringe_covered_verts=int(len(cv_)), fringe_zone_verts=int(len(vid)), fringe_texels=int((W > 0.5).sum()))
