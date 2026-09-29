#!/usr/bin/env python3
"""Dress a raw Tripo person as a street criminal and write a game-oriented static GLB for tools/skinfit/skinfit.py.

Fan homage project; not official Marvel/Sony/Insomniac; no affiliation. Sources are the owner's existing Tripo people
(~/sm2-assets/raw/*.glb, never committed). What this does, per character (see CFG):
  1. rotates the raw mesh (faces +X, arms along Z) to the game's frame (faces +Z, +X = left) and scales it to the hero's height;
  2. rasterises the UV layout into a per-texel 3D position map, so every texture edit is placed by body position, not by guesswork;
  3. fixes the seam artefacts: the raw atlas is thousands of islands with blurry inpainted gaps; the gaps are replaced by
     nearest-island colour (no dark dashes / sparkles at seams under mip filtering);
  4. recolours / removes items (brute: orange beanie -> charcoal knit, red-green plaid -> muted, pom-pom removed and capped;
     thug: ornamental belt buckle and key-chain metal -> plain dark steel);
  5. builds a MODELLED bandana: a shell around the lower face and neck, ray-cast from the head axis onto the real head surface
     (so it follows nose, cheeks, jaw and collar), 7 mm off the skin, with cloth folds, a rolled top edge and its own texture
     strip at the bottom of the atlas. Eyes, forehead, ears and hair stay untouched;
  6. writes a 4096x4096 atlas (raw atlas squeezed to 4096x3584 + 512-px bandana strip) into ONE primitive / ONE material.

usage: python3 tools/ue_char/people/prepare_person.py thug|brute [--out DIR]
"""
import os, sys, argparse, json, time
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gltfio, skinfit  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '../../..'))
RAW = os.path.expanduser('~/sm2-assets/raw')
SCR = '/Users/midir/sm2-n1/_scratch/characters/r3'
ATLAS = 4096
SIZES = json.load(open(os.path.join(HERE, 'people.json')))
CONTENT_H = 3584            # raw atlas is squeezed into rows [0, 3584); rows [3584, 4096) hold the bandana strip

CFG = {
    'thug': dict(src='leather+jacket+man+3d+model.glb', name='StreetThug',
                 # landmarks measured on the normalised mesh with tools/ue_char/people/ortho.py (metres)
                 eye=1.652, nose=1.620, ear_lobe=1.591, chin=1.535, axis_z=-0.02,
                 bandana=(40, 43, 58), bandana_hi=(66, 70, 92), seed=11),
    'brute': dict(src='human+character+3d+model.glb', name='StreetBrute',
                  eye=1.616, nose=1.587, ear_lobe=1.563, chin=1.472, axis_z=-0.02,
                  bandana=(62, 26, 24), bandana_hi=(90, 44, 38), seed=23),
}


# ------------------------------------------------------------------------------------------------------ helpers
def rgb2hsv(a):
    a = a.astype(np.float32) / 255.0
    mx, mn = a.max(-1), a.min(-1)
    d = mx - mn + 1e-9
    h = np.where(mx == a[..., 0], ((a[..., 1] - a[..., 2]) / d) % 6, np.where(mx == a[..., 1], (a[..., 2] - a[..., 0]) / d + 2, (a[..., 0] - a[..., 1]) / d + 4)) * 60.0
    s = np.where(mx > 0, (mx - mn) / (mx + 1e-9), 0.0)
    return h, s, mx


def raster_positions(P, UV, F, n):
    """Per texel: covered flag and interpolated 3D position. Image row = v * n (glTF v is down)."""
    pos = np.zeros((n, n, 3), np.float32)
    cov = np.zeros((n, n), bool)
    for f in F:
        u = UV[f] * n
        x0 = max(int(np.floor(u[:, 0].min() - 0.5)), 0); x1 = min(int(np.ceil(u[:, 0].max() + 0.5)), n - 1)
        y0 = max(int(np.floor(u[:, 1].min() - 0.5)), 0); y1 = min(int(np.ceil(u[:, 1].max() + 0.5)), n - 1)
        if x1 < x0 or y1 < y0:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        a, b, c = u
        den = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
        if abs(den) < 1e-12:
            continue
        w0 = ((b[1] - c[1]) * (gx - c[0]) + (c[0] - b[0]) * (gy - c[1])) / den
        w1 = ((c[1] - a[1]) * (gx - c[0]) + (a[0] - c[0]) * (gy - c[1])) / den
        w2 = 1 - w0 - w1
        m = (w0 >= -0.05) & (w1 >= -0.05) & (w2 >= -0.05)
        if not m.any():
            continue
        Pp = w0[..., None] * P[f[0]] + w1[..., None] * P[f[1]] + w2[..., None] * P[f[2]]
        sl = (slice(y0, y1 + 1), slice(x0, x1 + 1))
        pos[sl][m] = Pp[m]
        cov[sl][m] = True
    return cov, pos


def fill_gutters(img, cov, erode=1):
    """Replace everything outside the (slightly eroded) covered texels by the nearest covered colour."""
    keep = ndi.binary_erosion(cov, iterations=erode) if erode else cov
    _, (iy, ix) = ndi.distance_transform_edt(~keep, return_indices=True)
    return img[iy, ix]


def weave(shape, seed, period=5.0):
    r = np.random.RandomState(seed)
    yy, xx = np.mgrid[0:shape[0], 0:shape[1]].astype(np.float32)
    w = 0.5 + 0.25 * np.sin(xx * 2 * np.pi / period) + 0.25 * np.sin(yy * 2 * np.pi / period)
    n = ndi.gaussian_filter(r.randn(*shape).astype(np.float32), 1.2)
    n /= n.std() + 1e-6
    return w, n


# ------------------------------------------------------------------------------------------------------ mesh edits
def remove_region_and_cap(P, N, UV, F, mask_v, cap_uv):
    """Delete faces touching masked vertices; cap the resulting hole(s) with a fan whose UVs all point to cap_uv (flat colour)."""
    drop = mask_v[F].any(1)
    Fk = F[~drop]
    used = np.unique(Fk)
    # boundary edges of the kept mesh that touch dropped faces
    E = np.concatenate([Fk[:, [0, 1]], Fk[:, [1, 2]], Fk[:, [2, 0]]])
    key = np.sort(E, 1)
    _, inv, cnt = np.unique(key, axis=0, return_inverse=True, return_counts=True)
    bd = E[cnt[inv] == 1]
    dropped_verts = set(np.nonzero(mask_v)[0].tolist())
    # only boundary edges adjacent to the removed region (both verts within 1 ring): use edges whose vertices were on dropped faces
    ring = np.unique(F[drop])
    ring = ring[~mask_v[ring]]
    ringset = set(ring.tolist())
    bd = np.array([e for e in bd if e[0] in ringset and e[1] in ringset])
    newF = [Fk]
    P2, N2, UV2 = [P], [N], [UV]
    if len(bd):
        loop_v = np.unique(bd)
        c = P[loop_v].mean(0)
        cn = N[loop_v].mean(0); cn /= np.linalg.norm(cn) + 1e-9
        ci = len(P)
        # centroid + duplicated loop vertices: all with the flat cap UV, so the cap never smears neighbouring islands' texels
        loopP = P[loop_v]
        dup = {int(v): ci + 1 + k for k, v in enumerate(loop_v)}
        P2 += [c[None], loopP]; N2 += [cn[None], N[loop_v]]; UV2 += [np.array([cap_uv]), np.repeat(np.array([cap_uv]), len(loop_v), 0)]
        capf = np.array([[ci, dup[int(a)], dup[int(b)]] for a, b in bd])
        pos_of = {ci: c}
        pos_of.update({dup[int(v)]: P[v] for v in loop_v})
        for k, f in enumerate(capf):
            g = np.cross(pos_of[int(f[1])] - c, pos_of[int(f[2])] - c)
            if np.dot(g, cn) < 0:
                capf[k] = f[[0, 2, 1]]
        newF.append(capf)
    Pn_all = np.concatenate(P2); Nn_all = np.concatenate(N2); Un_all = np.concatenate(UV2)
    Fn = np.concatenate(newF)
    return Pn_all, Nn_all, Un_all, Fn


def ray_hits(P, F, origins, dirs, ymin, ymax):
    """First triangle hit (distance) for each ray (Moller-Trumbore, vectorised over rays, restricted to triangles in the y band)."""
    tri = P[F]
    cy = tri[:, :, 1].mean(1)
    sel = (cy > ymin - 0.04) & (cy < ymax + 0.04) & (np.hypot(tri[:, :, 0].mean(1), tri[:, :, 2].mean(1)) < 0.4)
    tri = tri[sel]
    v0, v1, v2 = tri[:, 0], tri[:, 1], tri[:, 2]
    e1, e2 = v1 - v0, v2 - v0
    out = np.full(len(origins), np.inf)
    for i in range(len(origins)):
        o, d = origins[i], dirs[i]
        h = np.cross(d, e2)
        a = np.einsum('ij,ij->i', e1, h)
        ok = np.abs(a) > 1e-10
        f = np.where(ok, 1.0 / np.where(ok, a, 1), 0)
        s = o - v0
        u = f * np.einsum('ij,ij->i', s, h)
        q = np.cross(s, e1)
        v = f * (q @ d)
        t = f * np.einsum('ij,ij->i', e2, q)
        hit = ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 0.01)
        if hit.any():
            out[i] = t[hit].min()
    return out


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def build_bandana(P, F, cfg, seed):
    """Shell around the lower face and neck. Returns (verts, normals, uv(0..1 over the strip), faces)."""
    eye, ear, chin, z0 = cfg['eye'], cfg['ear_lobe'], cfg['chin'], cfg['axis_z']
    NPHI, NH = 72, 14
    phi = np.linspace(-np.pi, np.pi, NPHI + 1)              # seam at the back (phi = +-180 deg)
    a = np.abs(phi)
    # lower-face mask over nose, mouth, chin and the front/side of the neck (top under the eyes, bottom on the jacket collar);
    # behind the ears it narrows to a tie strap that runs round the back of the head
    ang = np.radians([0, 35, 70, 90, 105, 125, 150, 180])
    top = np.interp(a, ang, [eye - .015, eye - .030, ear - .008, ear - .014, ear - .004, ear + .026, ear + .028, ear + .028])
    bot = np.interp(a, ang, [chin - .032, chin - .030, chin - .012, chin + .005, ear - .030, ear - .003, ear - .003, ear - .003])
    t = np.linspace(0, 1, NH + 1)
    H = bot[:, None] + (top - bot)[:, None] * t[None, :]      # (NPHI+1, NH+1) heights
    origins = np.stack([np.full(H.shape, 0.0), H, np.full(H.shape, z0)], -1).reshape(-1, 3)
    dirs = np.stack([np.repeat(np.sin(phi)[:, None], NH + 1, 1), np.zeros(H.shape), np.repeat(np.cos(phi)[:, None], NH + 1, 1)], -1).reshape(-1, 3)
    dist = ray_hits(P, F, origins, dirs, H.min(), H.max()).reshape(H.shape)
    fin = np.isfinite(dist)
    med = np.median(dist[fin]) if fin.any() else 0.09
    dist = np.where(fin, dist, med)
    dist0 = np.clip(dist, 0.5 * med, 1.7 * med)
    # cloth bridges bumps: dilate (so nose, lips and chin never poke through), smooth, then never go below the real surface
    dist = ndi.maximum_filter(dist0, size=(3, 3), mode='nearest')
    for _ in range(3):
        dist = (dist + np.roll(dist, 1, 0) + np.roll(dist, -1, 0)) / 3.0
        pad = np.pad(dist, ((0, 0), (1, 1)), mode='edge')
        dist = (pad[:, :-2] + pad[:, 1:-1] + pad[:, 2:]) / 3.0
    dist = np.maximum(dist, dist0)
    rng = np.random.RandomState(seed)
    # folds: diagonal ridges + low-frequency noise, damped at the top edge (which gets a rolled hem instead)
    ph, tt = np.meshgrid(phi, t, indexing='ij')
    folds = 0.0018 * np.sin(ph * 7 + tt * 9 + 0.6 * np.sin(ph * 3)) + 0.0012 * np.sin(-ph * 11 + tt * 5 + 1.3)
    lf = ndi.gaussian_filter(rng.randn(*H.shape), 2.0); lf = 0.0018 * lf / (lf.std() + 1e-6)
    hem = 0.0026 * smoothstep(0.86, 1.0, tt) + 0.0016 * (1 - smoothstep(0.0, 0.10, tt))
    off = 0.0085 + folds + lf + hem
    r = dist + off
    X = r * np.sin(phi)[:, None]; Z = z0 + r * np.cos(phi)[:, None]
    V = np.stack([X, H, Z], -1)
    # wrap: last column of phi equals first geometrically; keep separate vertices (UV seam)
    V[-1] = V[0] * 0 + np.stack([X[-1], H[-1], Z[-1]], -1)
    verts = V.reshape(-1, 3)
    # normals from the grid
    dphi = np.gradient(V, axis=0); dh = np.gradient(V, axis=1)
    nn = np.cross(dphi, dh)
    nn /= np.linalg.norm(nn, axis=-1, keepdims=True) + 1e-12
    radial = np.stack([np.sin(phi)[:, None] * np.ones_like(H), np.zeros_like(H), np.cos(phi)[:, None] * np.ones_like(H)], -1)
    flip = (nn * radial).sum(-1, keepdims=True) < 0
    nn = np.where(flip, -nn, nn)
    normals = nn.reshape(-1, 3)
    # faces (winding so the geometric normal points outward)
    idx = np.arange((NPHI + 1) * (NH + 1)).reshape(NPHI + 1, NH + 1)
    f = []
    for i in range(NPHI):
        for j in range(NH):
            a0, a1, b0, b1 = idx[i, j], idx[i + 1, j], idx[i, j + 1], idx[i + 1, j + 1]
            f.append([a0, a1, b1]); f.append([a0, b1, b0])
    faces = np.array(f)
    g = np.cross(verts[faces[:, 1]] - verts[faces[:, 0]], verts[faces[:, 2]] - verts[faces[:, 0]])
    if (g * normals[faces[:, 0]]).sum(1).mean() < 0:
        faces = faces[:, [0, 2, 1]]
    uv = np.stack([np.repeat((phi / (2 * np.pi) + 0.5)[:, None], NH + 1, 1), np.repeat(t[None, :], NPHI + 1, 0)], -1).reshape(-1, 2)
    return verts, normals, uv, faces


def bandana_strip(cfg, seed):
    """4096 x 512 cloth strip: dark base, thread weave, faint paisley-like dot print, no lettering."""
    W, Hh = ATLAS, ATLAS - CONTENT_H
    base = np.array(cfg['bandana'], np.float32); hi = np.array(cfg['bandana_hi'], np.float32)
    w, n = weave((Hh, W), seed, 4.0)
    yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
    # print: staggered rings/dots in a lattice, low contrast
    px, py = 48.0, 48.0
    cx = (xx % px) - px / 2 + 12 * (np.floor(yy / py) % 2)
    cy = (yy % py) - py / 2
    dots = np.clip(1.0 - np.hypot(cx * 0.9, cy * 1.1) / 9.0, 0, 1)
    dots2 = np.clip(1.0 - np.abs(np.hypot(cx, cy) - 15) / 2.0, 0, 1) * 0.6
    pat = np.clip(dots + dots2, 0, 1)
    img = base[None, None, :] * (0.86 + 0.16 * w[..., None] + 0.05 * n[..., None])
    img = img * (1 - 0.55 * pat[..., None]) + hi[None, None, :] * (0.55 * pat[..., None]) * (0.9 + 0.2 * w[..., None])
    return np.clip(img, 0, 255).astype(np.uint8)


# ------------------------------------------------------------------------------------------------------ recolours
def recolor_brute(img, pos, cov):
    h, s, v = rgb2hsv(img)
    y = pos[..., 1]
    a = img.astype(np.float32)
    lum = (a @ np.array([0.299, 0.587, 0.114], np.float32))
    out = a.copy()
    # orange knit beanie (hue 30-48, saturated, high on the head; the pom-pom is deleted from the mesh) -> charcoal knit, luminance detail kept
    z = pos[..., 2]
    brim = 1.53 + (z + 0.18) * (0.10 / 0.27)                      # slanted lower limit of the beanie: high over the forehead, low at the nape
    orange = ((h >= 27) & (h <= 58) & (s >= 0.5) & (v > 0.12)) | ((h >= 10) & (h < 27) & (s >= 0.7) & (v < 0.45))   # ginger beard / skin stay out (hue < 27, sat < 0.7)
    brim_lo = 1.49 + (z + 0.18) * 0.40
    cuff = (h >= 24) & (h <= 60) & (s >= 0.58) & (v > 0.12)                  # orange cuff just below the slanted brim; skin (sat < 0.5) and ginger beard (hue < 24) stay out
    beanie = cov & (y > 1.48) & ((y > brim) | ((y > brim_lo) & cuff))         # above the brim geometry decides (the knit has orange, brown and black threads)
    tone = np.array([46, 47, 52], np.float32)
    out[beanie] = tone[None, :] * np.clip(lum[beanie] / 120.0, 0.35, 1.7)[:, None]
    # red/green flannel plaid on torso and arms -> one worn brown-grey flannel tone; the check survives only as a soft luminance pattern
    plaid = cov & (y > 0.70) & (y < 1.55) & (((s > 0.32) & ((h < 14) | (h > 335))) | ((s > 0.14) & (h > 70) & (h < 190)))
    x = pos[..., 0]
    keep_skin = ((np.abs(x) > 0.50) & (y < 1.12)) | ((y > 1.40) & (np.abs(x) < 0.14))       # hands (A-pose, wrists out at |x| > 0.5) and neck / lower face are never recoloured
    plaid &= ~keep_skin | (s > 0.58)                                                          # in those zones only the saturated plaid red/green is recoloured
    plaid = ndi.binary_dilation(plaid, iterations=2) & cov & (y > 0.70) & (y < 1.55) & (s > 0.12) & (~keep_skin | (s > 0.58))      # take the anti-aliased edges too
    Lm = ndi.gaussian_filter(np.where(plaid, lum, 0.0), 12) / np.maximum(ndi.gaussian_filter(plaid.astype(np.float32), 12), 1e-3)
    rel = np.clip(lum / np.maximum(Lm, 1.0), 0.55, 1.35)
    rel = 0.6 + 0.4 * ndi.gaussian_filter(rel, 0.8)                                                        # damp the pattern
    tone = np.array([70, 60, 55], np.float32)
    out[plaid] = tone[None, :] * rel[plaid][:, None]
    npl = int(plaid.sum())
    return np.clip(out, 0, 255).astype(np.uint8), int(beanie.sum()), npl


def recolor_thug(img, pos, cov):
    """Ornamental belt buckle and key-chain (invented metalwork with pseudo-lettering) -> plain dark steel."""
    h, s, v = rgb2hsv(img)
    y, x, z = pos[..., 1], pos[..., 0], pos[..., 2]
    a = img.astype(np.float32)
    lum = a @ np.array([0.299, 0.587, 0.114], np.float32)
    metal = cov & (s < 0.18) & (lum > 60) & (y > 0.62) & (y < 1.10)          # belt zone and hip pocket: grey/silver metal only
    out = a.copy()
    steel = np.array([58, 60, 64], np.float32)
    out[metal] = steel[None, :] * np.clip(0.75 + 0.25 * lum[metal] / 160.0, 0.6, 1.2)[:, None]
    return np.clip(out, 0, 255).astype(np.uint8), int(metal.sum())


# ------------------------------------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('which', choices=sorted(CFG))
    ap.add_argument('--out', default=SCR + '/people')
    a = ap.parse_args()
    cfg = CFG[a.which]
    os.makedirs(a.out, exist_ok=True)
    t0 = time.time()
    game = skinfit.Game(os.path.join(ROOT, 'public/assets/spiderman.glb'))
    P, N, UV, F, im = gltfio.read_person(os.path.join(RAW, cfg['src']))
    R = np.array([[0, 0, -1], [0, 1, 0], [1, 0, 0]], float)      # raw faces +X, arms along Z -> game frame (faces +Z, +X left)
    P = P @ R.T; N = N @ R.T
    P = skinfit.normalise_target(P, game)
    print('%s: %d verts %d tris' % (a.which, len(P), len(F)))
    info = {}
    if a.which == 'brute':
        # pom-pom: pull its vertices onto the beanie dome (sphere fitted to the dome vertices) so no hole has to be capped
        pom = (P[:, 1] > 1.705) & (P[:, 2] < -0.07) & (np.abs(P[:, 0]) < 0.08)
        dome = (P[:, 1] > 1.66) & ~pom & (P[:, 1] < 1.72) & (np.abs(P[:, 0]) < 0.11)
        Q = P[dome]
        A_ = np.c_[2 * Q, np.ones(len(Q))]; b_ = (Q ** 2).sum(1)
        sol = np.linalg.lstsq(A_, b_, rcond=None)[0]
        ctr = sol[:3]; rad = float(np.sqrt(sol[3] + (ctr ** 2).sum()))
        d = P[pom] - ctr
        P[pom] = ctr + d / np.linalg.norm(d, axis=1, keepdims=True) * rad
        N[pom] = d / np.linalg.norm(d, axis=1, keepdims=True)
        info.update(pompom_verts=int(pom.sum()), dome_centre=[round(float(x), 3) for x in ctr], dome_radius=round(rad, 3))
    im4 = np.asarray(im.resize((ATLAS, ATLAS), Image.LANCZOS))
    cov, pos = raster_positions(P, UV, F, ATLAS)
    print('  uv coverage %.1f%%' % (100 * cov.mean()))
    if a.which == 'brute':
        im4, nb, npl = recolor_brute(im4, pos, cov); info['beanie_px'] = nb; info['plaid_px'] = npl
    else:
        im4, nm = recolor_thug(im4, pos, cov); info['metal_px'] = nm
    im4 = fill_gutters(im4, cov, erode=1)
    if a.which == 'brute':
        # the actor is widened by `girth` in X/Y at run time: shrink the head (and the top of the neck) by 1/girth so it keeps natural proportions
        f = 1.0 / SIZES['brute']['girth']
        t = smoothstep(1.44, 1.52, P[:, 1])
        sx = 1.0 - (1.0 - f) * t
        z0 = CFG['brute']['axis_z']
        P[:, 0] *= sx
        P[:, 2] = z0 + (P[:, 2] - z0) * sx
        N = np.stack([N[:, 0] / sx, N[:, 1], N[:, 2] / sx], -1); N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-12
        info['head_shrink'] = round(f, 3)
    # bandana shell
    bv, bn, buv, bf = build_bandana(P, F, cfg, cfg['seed'])
    # squeeze the original atlas rows into [0, CONTENT_H)
    atlas = np.zeros((ATLAS, ATLAS, 3), np.uint8)
    atlas[:CONTENT_H] = np.asarray(Image.fromarray(im4).resize((ATLAS, CONTENT_H), Image.LANCZOS))
    atlas[CONTENT_H:] = bandana_strip(cfg, cfg['seed'])
    UV2 = UV.copy(); UV2[:, 1] = UV[:, 1] * (CONTENT_H / ATLAS)
    m = 6.0 / ATLAS
    buv2 = np.stack([np.clip(buv[:, 0], m, 1 - m), (CONTENT_H + m * ATLAS + buv[:, 1] * (ATLAS - CONTENT_H - 2 * m * ATLAS)) / ATLAS], -1)
    Pf = np.concatenate([P, bv]); Nf = np.concatenate([N, bn]); UVf = np.concatenate([UV2, buv2]); Ff = np.concatenate([F, bf + len(P)])
    print('  bandana %d verts %d tris; total %d verts %d tris' % (len(bv), len(bf), len(Pf), len(Ff)))
    out = os.path.join(a.out, cfg['name'] + '_prepared.glb')
    gltfio.write_static_glb(out, Pf, Nf, UVf, Ff, Image.fromarray(atlas), cfg['name'])
    Image.fromarray(atlas).save(os.path.join(a.out, cfg['name'] + '_atlas.png'))
    np.savez_compressed(os.path.join(a.out, cfg['name'] + '_prepared.npz'), P=Pf, N=Nf, UV=UVf, F=Ff, n_body_verts=len(P), n_body_tris=len(F))
    info.update(name=cfg['name'], verts=len(Pf), tris=len(Ff), bandana_tris=len(bf), seconds=round(time.time() - t0, 1))
    json.dump(info, open(os.path.join(a.out, cfg['name'] + '_prepared.json'), 'w'), indent=1)
    print(json.dumps(info))


if __name__ == '__main__':
    main()
