#!/usr/bin/env python3
"""Paint out a chest emblem that Tripo bled through onto the BACK of a fitted skin (skinfit.py output).

Tripo builds the back from the input views and sometimes copies the front chest logo onto the upper back. This tool
rasterises the skin's bind-pose surface into UV space, selects texels on the upper back (surface normal pointing
backwards, inside a band around the spine at shoulder-blade height), finds the ones whose colour departs from that
patch's dominant suit colour, and inpaints them (OpenCV Telea) from the surrounding texture. The front is never
touched, because only back-facing surface is considered.

usage: backlogo.py SKIN.glb [--out SKIN.glb] [--thresh 60] [--keep 'r,g,b;r,g,b'] [--preview mask.png]
"""
import argparse, io, json, struct
import numpy as np
import cv2
from PIL import Image
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from skinfit import read_glb, accessor, image_bytes  # noqa: E402

GRID = 1024


def raster_uv(P, N, UV, F, select):
    """For triangles picked by `select` (per-face bool), write per-texel 3D position and normal into GRID² maps."""
    pos = np.full((GRID, GRID, 3), np.nan, np.float32); nrm = np.zeros((GRID, GRID, 3), np.float32)
    uvp = UV * GRID; uvp[:, 1] = uvp[:, 1]  # glTF UV: origin top-left, v down -> image rows directly
    for f in np.nonzero(select)[0]:
        a, b, c = F[f]
        ta, tb, tc = uvp[a], uvp[b], uvp[c]
        x0, x1 = int(max(0, np.floor(min(ta[0], tb[0], tc[0])))), int(min(GRID - 1, np.ceil(max(ta[0], tb[0], tc[0]))))
        y0, y1 = int(max(0, np.floor(min(ta[1], tb[1], tc[1])))), int(min(GRID - 1, np.ceil(max(ta[1], tb[1], tc[1]))))
        if x1 < x0 or y1 < y0: continue
        xs, ys = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        d = (tb[1] - tc[1]) * (ta[0] - tc[0]) + (tc[0] - tb[0]) * (ta[1] - tc[1])
        if abs(d) < 1e-12: continue
        l0 = ((tb[1] - tc[1]) * (xs - tc[0]) + (tc[0] - tb[0]) * (ys - tc[1])) / d
        l1 = ((tc[1] - ta[1]) * (xs - tc[0]) + (ta[0] - tc[0]) * (ys - tc[1])) / d
        l2 = 1 - l0 - l1
        m = (l0 >= -0.01) & (l1 >= -0.01) & (l2 >= -0.01)
        if not m.any(): continue
        yy, xx = (ys[m] - 0.5).astype(int), (xs[m] - 0.5).astype(int)
        w = np.stack([l0[m], l1[m], l2[m]], 1)
        pos[yy, xx] = w @ np.stack([P[a], P[b], P[c]])
        nrm[yy, xx] = w @ np.stack([N[a], N[b], N[c]])
    return pos, nrm


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('skin'); ap.add_argument('--out')
    ap.add_argument('--thresh', type=float, default=60.0, help='colour distance (0-441) from the dominant back colour')
    ap.add_argument('--band', type=float, nargs=4, default=[-0.16, 0.16, 1.12, 1.55], help='x0 x1 y0 y1 (metres, bind pose)')
    ap.add_argument('--preview')
    ap.add_argument('--keep', help='allowed suit colours "r,g,b;r,g,b" (default: the dominant back colour only)')
    a = ap.parse_args()
    j, b = read_glb(a.skin)
    p = j['meshes'][0]['primitives'][0]
    P = accessor(j, b, p['attributes']['POSITION']); N = accessor(j, b, p['attributes']['NORMAL'])
    UV = accessor(j, b, p['attributes']['TEXCOORD_0']); F = accessor(j, b, p['indices']).reshape(-1, 3).astype(np.int64)
    img_i = j['textures'][j['materials'][0]['pbrMetallicRoughness']['baseColorTexture']['index']]
    src = img_i.get('extensions', {}).get('EXT_texture_webp', {}).get('source', img_i.get('source'))
    tex = np.array(Image.open(io.BytesIO(image_bytes(j, b, j['images'][src]))).convert('RGB'))
    x0, x1, y0, y1 = a.band
    fc = P[F].mean(1); fn = N[F].mean(1)
    sel = (fn[:, 2] < -0.35) & (fc[:, 0] > x0) & (fc[:, 0] < x1) & (fc[:, 1] > y0) & (fc[:, 1] < y1)
    print(f'{a.skin}: {sel.sum()} back-patch triangles')
    pos, nrm = raster_uv(P, N, UV, F, sel)
    region = ~np.isnan(pos[..., 0])
    H = tex.shape[0]
    small = cv2.resize(tex, (GRID, GRID), interpolation=cv2.INTER_AREA).astype(np.float32)
    cols = small[region]
    # dominant colour: median of the largest colour cluster (k-means, k=3)
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.5)
    _, lab, cen = cv2.kmeans(cols, 3, None, crit, 4, cv2.KMEANS_PP_CENTERS)
    dom = cen[np.bincount(lab.ravel()).argmax()]
    keep = np.array([[float(c) for c in s.split(',')] for s in a.keep.split(';')], np.float32) if a.keep else dom[None]
    dist = np.min(np.linalg.norm(small[:, :, None, :] - keep[None, None], axis=3), axis=2)
    mask = (region & (dist > a.thresh)).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=2)
    frac = mask[region].mean() / 255 if region.any() else 0
    print(f'  dominant back colour {dom.round()} ; {frac * 100:.1f}% of the back patch flagged as emblem')
    big = cv2.resize(mask, (H, H), interpolation=cv2.INTER_NEAREST)
    fixed = cv2.inpaint(tex[..., ::-1].copy(), big, 9, cv2.INPAINT_TELEA)[..., ::-1]
    if a.preview:
        pv = tex.copy(); pv[big > 0] = [0, 255, 0]
        Image.fromarray(np.concatenate([cv2.resize(pv, (1024, 1024)), cv2.resize(fixed, (1024, 1024))], 1)).save(a.preview)
    # write back: replace the image bytes, rebuild the binary chunk
    bio = io.BytesIO(); Image.fromarray(fixed).save(bio, 'WEBP', quality=90, method=6); new = bio.getvalue()
    views = j['bufferViews']; iv = j['images'][src]['bufferView']
    chunks, off = [], 0
    out_bin = bytearray()
    for k, v in enumerate(views):
        data = new if k == iv else b[v.get('byteOffset', 0):v.get('byteOffset', 0) + v['byteLength']]
        while len(out_bin) % 4: out_bin += b'\0'
        v['byteOffset'] = len(out_bin); v['byteLength'] = len(data); out_bin += data
    while len(out_bin) % 4: out_bin += b'\0'
    j['buffers'][0]['byteLength'] = len(out_bin)
    js = json.dumps(j, separators=(',', ':')).encode()
    while len(js) % 4: js += b' '
    out = a.out or a.skin
    with open(out, 'wb') as f:
        f.write(struct.pack('<III', 0x46546C67, 2, 28 + len(js) + len(out_bin)))
        f.write(struct.pack('<II', len(js), 0x4E4F534A)); f.write(js)
        f.write(struct.pack('<II', len(out_bin), 0x004E4942)); f.write(bytes(out_bin))
    print(f'  wrote {out}')


if __name__ == '__main__':
    main()
