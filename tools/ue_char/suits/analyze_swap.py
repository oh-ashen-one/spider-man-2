#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""Round 11: swap latency of the in-game suit change measured on the pixels of a fixed-step (-movie, 60 fps) run, next to the engine's own log.

  python3 tools/ue_char/suits/analyze_swap.py FRAMES_DIR SUIT_LOG.txt OUT.json [--fps 60] [--roi x0,y0,x1,y1]

FRAMES_DIR holds MovieFrameNNNNN.png.  For every frame the mean colour (CIE Lab) of a central ROI (the tracked hero's torso: default 42-58 % x 35-65 % of the frame)
is computed at 1/4 size; a SWAP is a one-frame step of that mean (> 5 Lab units).  The first very large step (> 25) is the director's camera cut at game time ~1/60 s: it
calibrates movie frame <-> game time.  Each logged 'WH_SUIT injected T press t=<s>' (or 'WH_SUIT set ... t=<s>') is predicted at frame cut + 60 t; the observed step minus the
predicted frame is the latency in frames (x 1000/60 ms).  Also parsed from the log: the engine's own apply_ms and 'swap_done wall_ms / frames / textures_resident'.
"""
import sys, os, re, json, glob
import numpy as np
import cv2


def main():
    fr_dir, log_p, out = sys.argv[1:4]
    a = sys.argv
    fps = float(a[a.index('--fps') + 1]) if '--fps' in a else 60.0
    roi = [float(x) for x in a[a.index('--roi') + 1].split(',')] if '--roi' in a else [0.42, 0.35, 0.58, 0.65]
    files = sorted(glob.glob(os.path.join(fr_dir, 'MovieFrame*.png')))
    means = []
    for f in files:
        im = cv2.imread(f)
        h, w = im.shape[:2]
        im = cv2.resize(im, (w // 4, h // 4), interpolation=cv2.INTER_AREA)
        lab = cv2.cvtColor(im.astype(np.float32) / 255, cv2.COLOR_BGR2LAB)
        H, W = lab.shape[:2]
        r = lab[int(H * roi[1]):int(H * roi[3]), int(W * roi[0]):int(W * roi[2])]
        means.append(r.reshape(-1, 3).mean(0))
    means = np.array(means)
    step = np.linalg.norm(np.diff(means, axis=0), axis=1)          # step[i] = change from frame i to i+1
    cut = int(np.argmax(step > 25)) + 1 if (step > 25).any() else 0
    swaps = [int(i) + 1 for i in np.nonzero(step > 5.0)[0] if int(i) + 1 > cut + 5]
    # merge steps that are neighbours (a swap can span 2 frames)
    merged = []
    for s in swaps:
        if merged and s - merged[-1] <= 2: continue
        merged.append(s)
    log = open(log_p).read() if os.path.exists(log_p) else ''
    presses = [float(m.group(1)) for m in re.finditer(r'injected T press t=([0-9.]+)', log)]
    sets = [dict(i=int(m.group(1)), id=m.group(3), why=m.group(4), t=float(m.group(5)), frame=int(m.group(6)), apply_ms=float(m.group(7)))
            for m in re.finditer(r'WH_SUIT set (\d+)/(\d+) (\S+) \(([^)]*)\) changed=\d t=([0-9.]+) frame=(\d+) apply_ms=([0-9.]+)', log)]
    done = [dict(i=int(m.group(1)), id=m.group(2), wall_ms=float(m.group(3)), frames=int(m.group(4)), res=m.group(5))
            for m in re.finditer(r'WH_SUIT swap_done (\d+) (\S+) wall_ms=([0-9.]+) frames=(\d+) textures_resident=(\d+/\d+)', log)]
    pred = [cut + int(round(fps * (p - 1.0 / fps))) for p in presses]
    lat = []
    for p in pred:
        near = [s for s in merged if p - 3 <= s <= p + 40]
        lat.append(near[0] - p if near else None)
    res = dict(frames=len(files), camera_cut_frame=cut, roi=roi, swap_frames=merged, press_times=presses, predicted_frames=pred, latency_frames=lat,
               latency_ms=[None if l is None else round(l * 1000 / fps, 1) for l in lat], engine_sets=sets, engine_swap_done=done,
               max_latency_s=None if any(l is None for l in lat) or not lat else round(max(lat) / fps, 3), swaps_found=len(merged), presses=len(presses))
    json.dump(res, open(out, 'w'), indent=1)
    print(json.dumps({k: res[k] for k in ('frames', 'camera_cut_frame', 'swap_frames', 'predicted_frames', 'latency_frames', 'latency_ms', 'max_latency_s', 'swaps_found', 'presses')}))
    for d in done: print('engine:', d)


if __name__ == '__main__':
    main()
