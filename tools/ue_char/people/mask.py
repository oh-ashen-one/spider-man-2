"""Round-04 enemy face masks and texture fixes for the people pipeline (numpy/scipy). Fan homage; no affiliation.

The round-03 bandana was a separate ray-cast shell: at 72 x 14 samples it read as a flat card with polygon edges, clipped the ears and
let the nose through between rays. Here the mask IS the head surface:
  subdivide_region()  one midpoint subdivision of the triangles around the lower face / neck (red-green refinement, no T-junctions,
                      UV seams split on both sides by welded position);
  drape()             pushes the lower-face vertices radially out onto the convex hull of the front of the head (the cloth spans
                      nose -> cheeks and chin -> collar instead of following lips and the neck hollow), plus a few mm of cloth
                      thickness and small folds; ears are excluded, so nothing can poke through or clip;
  paint_mask()        paints the cloth into the body atlas by 3D position (feathered edge + stitched hem, weave, soft fold shading,
                      no tiled print), and a tie band round the back of the head, leaving the ears bare;
  seam_blend()        averages texels along UV-island borders with the texels at the same 3D position on the other island (hides the
                      hard colour seams of the Tripo atlas, e.g. the scalp/forehead line);
  auto_landmarks()    nose tip / eye / ear-lobe / chin heights from the mesh (for people without hand-measured CFG numbers)."""
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import ConvexHull, cKDTree


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


# ------------------------------------------------------------------------------------------------ landmarks and mask region
def auto_landmarks(P, axis_z=-0.02):
    top = P[:, 1].max()
    head = (P[:, 1] > top - 0.30) & (P[:, 1] < top - 0.08) & (np.abs(P[:, 0]) < 0.025)
    i = np.argmax(np.where(head, P[:, 2], -9))
    nose = float(P[i, 1]); nz = float(P[i, 2])
    # chin: lowest centre-line point still within 4.5 cm behind the nose tip before the neck recedes
    col = (np.abs(P[:, 0]) < 0.02) & (P[:, 1] < nose) & (P[:, 1] > nose - 0.16) & (P[:, 2] > nz - 0.045)
    chin = float(P[col, 1].min()) if col.any() else nose - 0.09
    return dict(eye=nose + 0.031, nose=nose, ear_lobe=nose - 0.027, chin=chin, axis_z=axis_z, nose_z=nz)


def mask_bounds(phi, cfg):
    """top/bottom heights of the mask as a function of azimuth phi (0 = front)."""
    eye, ear, chin = cfg['eye'], cfg['ear_lobe'], cfg['chin']
    a = np.abs(phi)
    ang = np.radians([0, 35, 70, 90, 105, 125, 150, 180])
    top = np.interp(a, ang, [eye - .016, eye - .026, ear + .012, ear + .020, ear + .030, ear + .038, ear + .040, ear + .040])
    bot = np.interp(a, ang, [chin - .040, chin - .036, chin - .016, ear - .012, ear + .004, ear + .010, ear + .010, ear + .010])
    if not cfg.get('tie_band', True):          # long / voluminous hair at the back: the mask ends behind the ears (no painted tie)
        cut = smoothstep(np.radians(108), np.radians(116), a)
        top = top * (1 - cut) + (bot - 0.01) * cut
    return top, bot


def cyl(P, cfg):
    x, z = P[..., 0], P[..., 2] - cfg['axis_z']
    return np.arctan2(x, z), np.hypot(x, z)


def ear_flag(P, cfg, Pall):
    """True where a point belongs to an ear: beyond the cheek width of the front half of the head at that height, not in front."""
    y = P[..., 1]
    phi, r = cyl(P, cfg)
    ear = cfg['ear_lobe']
    band = (y > ear - 0.012) & (y < ear + 0.075) & (np.abs(phi) > np.radians(55)) & (np.abs(phi) < np.radians(135))
    # cheek half-width per 5 mm slice from the front half
    front = (Pall[:, 2] > cfg['axis_z'] + 0.035) & (Pall[:, 1] > ear - 0.03) & (Pall[:, 1] < ear + 0.09) & (np.hypot(Pall[:, 0], Pall[:, 2] - cfg['axis_z']) < 0.13)
    ys = np.arange(ear - 0.03, ear + 0.09, 0.005)
    w = np.array([np.percentile(np.abs(Pall[front & (np.abs(Pall[:, 1] - yy) < 0.004), 0]), 97) if (front & (np.abs(Pall[:, 1] - yy) < 0.004)).sum() > 5 else 0.07 for yy in ys])
    wy = np.interp(y, ys, w)
    return band & (np.abs(P[..., 0]) > wy + 0.004)


def region_weight(P, cfg, feather=0.006):
    """0..1 inside the mask (1 = fully cloth), by height against the azimuth-dependent top/bottom curves."""
    phi, r = cyl(P, cfg)
    top, bot = mask_bounds(phi, cfg)
    y = P[..., 1]
    w = smoothstep(bot - feather * 0.5, bot + feather * 0.5, y) * (1 - smoothstep(top - feather * 0.5, top + feather * 0.5, y))
    # radial limit: the face (nose tip radius + 4.5 cm) in front, generous at the back so voluminous hair gets the whole tie band
    rmax = np.where(np.abs(phi) > np.radians(100), 0.26, cfg.get('nose_r', 0.13) + 0.045)
    return w * (r < rmax)


# ------------------------------------------------------------------------------------------------ geometry
def weld_ids(P, tol=1e-6):
    k = np.round(P / tol).astype(np.int64)
    _, inv = np.unique(k, axis=0, return_inverse=True)
    return inv.reshape(-1)


def subdivide_region(P, N, UV, F, sel_tri):
    """one red-green midpoint subdivision of the selected triangles (and the needed splits of their neighbours)."""
    wid = weld_ids(P)
    def gk(a, b):
        a, b = wid[a], wid[b]
        return (a, b) if a < b else (b, a)
    split = set()
    for t in np.where(sel_tri)[0]:
        a, b, c = F[t]
        split.add(gk(a, b)); split.add(gk(b, c)); split.add(gk(c, a))
    P, N, UV = list(P), list(N), list(UV)
    mids = {}
    def mid(a, b):
        k = (a, b) if a < b else (b, a)
        if k not in mids:
            P.append((P[a] + P[b]) / 2); n = N[a] + N[b]; N.append(n / (np.linalg.norm(n) + 1e-12)); UV.append((UV[a] + UV[b]) / 2)
            mids[k] = len(P) - 1
        return mids[k]
    out = []
    for f in F:
        a, b, c = int(f[0]), int(f[1]), int(f[2])
        s = [gk(a, b) in split, gk(b, c) in split, gk(c, a) in split]
        n = sum(s)
        if n == 0: out.append((a, b, c)); continue
        if n == 3:
            ab, bc, ca = mid(a, b), mid(b, c), mid(c, a)
            out += [(a, ab, ca), (ab, b, bc), (ca, bc, c), (ab, bc, ca)]; continue
        # rotate so that the pattern is canonical
        v = [a, b, c]
        if n == 1:
            k = s.index(True); a, b, c = v[k], v[(k + 1) % 3], v[(k + 2) % 3]
            m = mid(a, b); out += [(a, m, c), (m, b, c)]
        else:
            k = s.index(False); c, a, b = v[k], v[(k + 1) % 3], v[(k + 2) % 3]   # unsplit edge is c->a
            m1, m2 = mid(a, b), mid(b, c)
            out += [(a, m1, m2), (m1, b, m2), (a, m2, c)]
    return np.array(P), np.array(N), np.array(UV), np.array(out, np.int64)


def vertex_normals(P, F):
    wid = weld_ids(P)
    fn = np.cross(P[F[:, 1]] - P[F[:, 0]], P[F[:, 2]] - P[F[:, 0]])
    acc = np.zeros((wid.max() + 1, 3))
    for k in range(3): np.add.at(acc, wid[F[:, k]], fn)
    n = acc[wid]
    return n / (np.linalg.norm(n, axis=1, keepdims=True) + 1e-12)


def drape(P, F, cfg, seed=0, thick=0.0035):
    """push lower-face / neck vertices radially onto the convex hull of the front head (cloth spans the hollows). Returns P, weight."""
    P = P.copy()
    w = region_weight(P, cfg, feather=0.012)
    ear = ear_flag(P, cfg, P)
    phi, r = cyl(P, cfg)
    near = (r < 0.13) & (P[:, 1] > cfg['chin'] - 0.07) & (P[:, 1] < cfg['eye'] + 0.01)
    hull_pts = P[near & ~ear & (np.abs(phi) < np.radians(115))]
    hull = ConvexHull(hull_pts)
    Nn, C = hull.equations[:, :3], hull.equations[:, 3]
    o = np.stack([np.zeros(len(P)), P[:, 1], np.full(len(P), cfg['axis_z'])], 1)
    d = np.stack([np.sin(phi), np.zeros(len(P)), np.cos(phi)], 1)
    sel = (w > 0) & ~ear & near
    rng = np.random.RandomState(seed)
    moved = np.zeros(len(P))
    for i in np.where(sel)[0]:
        nd = Nn @ d[i]
        ok = nd > 1e-6
        t = (-(C[ok] + Nn[ok] @ o[i])) / nd[ok]
        rh = float(t.min()) if ok.any() else r[i]
        # draping strength: full in front of the face / under the chin, fading toward the sides (cloth hugs the cheeks at the sides)
        side = 1 - smoothstep(np.radians(55), np.radians(100), abs(phi[i]))
        fold = 0.0012 * np.sin(phi[i] * 9 + P[i, 1] * 60) + 0.0008 * np.sin(-phi[i] * 5 + P[i, 1] * 110 + 1.1)
        rn = r[i] + (max(rh, r[i]) - r[i]) * side * w[i] + (thick + fold) * w[i]
        moved[i] = rn - r[i]
        P[i, 0] = np.sin(phi[i]) * rn; P[i, 2] = cfg['axis_z'] + np.cos(phi[i]) * rn
    return P, moved


# ------------------------------------------------------------------------------------------------ texture
def seam_blend(img, cov, pos, band=3, radius=0.004, k=12, step=2):
    """average texels near island borders with every texel within `radius` (3D) - hides colour jumps across UV seams."""
    border = cov & ~ndi.binary_erosion(cov, iterations=band)
    src = np.zeros_like(cov); src[::step, ::step] = True; src &= cov
    sp = pos[src]; sc = img[src].astype(np.float32)
    tree = cKDTree(sp)
    bp = pos[border]
    dist, idx = tree.query(bp, k=k, distance_upper_bound=radius)
    valid = np.isfinite(dist)
    idx = np.where(valid, idx, 0)
    wgt = np.where(valid, 1.0 - dist / radius, 0.0)
    col = (sc[idx] * wgt[..., None]).sum(1) / np.maximum(wgt.sum(1, keepdims=True), 1e-6)
    out = img.astype(np.float32)
    has = wgt.sum(1) > 0.5
    cur = out[border]
    cur[has] = col[has]
    out[border] = cur
    return np.clip(out, 0, 255).astype(np.uint8), int(border.sum())


def cloth(shape, seed, base, hi):
    """plain cotton: fine weave + grain noise + low-frequency tone variation (no print)."""
    r = np.random.RandomState(seed)
    yy, xx = np.mgrid[0:shape[0], 0:shape[1]].astype(np.float32)
    weave = 0.5 + 0.25 * np.sin(xx * 2 * np.pi / 3.2) * np.sin(yy * 2 * np.pi / 3.2)
    g = ndi.gaussian_filter(r.randn(*shape).astype(np.float32), 0.8); g /= g.std() + 1e-6
    lf = ndi.gaussian_filter(r.randn(*shape).astype(np.float32), 40); lf /= lf.std() + 1e-6
    base = np.asarray(base, np.float32); hi = np.asarray(hi, np.float32)
    return base, hi, weave, g, lf


def paint_mask(img, cov, pos, cfg, seed):
    """paint the cloth mask by 3D position; returns img, mask weight map."""
    Pm = pos.reshape(-1, 3)
    w = region_weight(pos, cfg, feather=0.003)
    w = np.where(cov, w, 0)
    ear = ear_flag(pos, cfg, Pm[cov.reshape(-1)])
    w = np.where(ear, 0, w)
    phi, r = cyl(pos, cfg)
    top, bot = mask_bounds(phi, cfg)
    y = pos[..., 1]
    base = np.asarray(cfg['mask'], np.float32); hi = np.asarray(cfg.get('mask_hi', [c * 1.35 for c in cfg['mask']]), np.float32)
    rng = np.random.RandomState(seed)
    # procedural texture evaluated in 3D (no UV-dependent tiling): weave on (arc length, height), folds as soft diagonal bands
    s = phi * np.maximum(r, 0.05)
    weave = 0.5 + 0.5 * np.sin(s * 2 * np.pi / 0.0011) * np.sin(y * 2 * np.pi / 0.0011)
    grain = ndi.gaussian_filter(rng.randn(*w.shape).astype(np.float32), 0.7); grain /= grain.std() + 1e-6
    folds = 0.5 + 0.5 * np.sin(s * 70 + (y - cfg['nose']) * 140 + 0.8 * np.sin(s * 23))
    folds2 = 0.5 + 0.5 * np.sin(-s * 45 + (y - cfg['nose']) * 95 + 2.0)
    shade = 0.80 + 0.12 * folds + 0.08 * folds2
    edge_d = np.minimum(top - y, y - bot)            # distance to the nearer edge (m)
    hem = smoothstep(0.0, 0.004, edge_d) * (1 - 0.35 * np.exp(-((edge_d - 0.0045) / 0.0012) ** 2))   # stitched rolled hem 4-5 mm in
    stitch = (np.abs(edge_d - 0.0062) < 0.0005) & (np.sin(s * 2 * np.pi / 0.004) > 0.2)
    col = base[None, None, :] * (shade * (0.88 + 0.10 * weave + 0.05 * grain) * hem)[..., None]
    col = np.where(stitch[..., None], hi[None, None, :], col)
    # lighter at the nose bridge / chin ridge (the cloth is stretched there)
    col = col * (1 + 0.10 * np.exp(-((phi / 0.35) ** 2)) * smoothstep(cfg['chin'], cfg['nose'], y))[..., None]
    out = img.astype(np.float32) * (1 - w[..., None]) + col * w[..., None]
    return np.clip(out, 0, 255).astype(np.uint8), w
