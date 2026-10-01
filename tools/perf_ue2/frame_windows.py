#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See DISCLAIMER.md.
"""Piece F (round 07): where the slow frames of a route run sit and what is different in them, from a CsvProfiler file.
  windows  per 150-frame window: number of top-5 % frames (by FrameTime), mean FrameTime, GPUTime, FT-GPU, thread times, render-thread visibility wait,
           ray-tracing geometry (ReferencedSizeMB, GPU BLAS build pass, RT geometry manager tick) and the largest GPU passes.
  passes   every GPU/* and render-thread column: mean, even-minus-odd frame mean, top-5 % minus 40-60 % frames (same row and previous row), std.
usage: frame_windows.py <csv> [<csv> ...]"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from frame_gap import load

WCOLS = ['FrameTime', 'GPUTime', 'RenderThreadTime', 'GameThreadTime', 'RHIThreadTime', 'Exclusive/RenderThread/EventWait/Visibility',
         'RayTracingGeometry/ReferencedSizeMB', 'GPU/RayTracingGeometry', 'Exclusive/RenderThread/RayTracingGeometryManager_Tick',
         'GPU/LumenScreenProbeGather', 'GPU/ShadowDepths', 'GPU/LumenSceneUpdate', 'GPU/NaniteVisBuffer', 'GPU/Unaccounted']


def main(paths):
    for p in paths:
        h, D = load(p); c = lambda k: D[:, h.index(k)] if k in h else np.zeros(len(D))
        ft, g = c('FrameTime'), c('GPUTime'); thr = np.percentile(ft, 95); n = len(ft)
        print('== %s  frames %d  p95 %.2f  FT-GPU mean %.2f  GPU even/odd %.2f / %.2f  lag-1 autocorr GPU %.2f FT %.2f' % (
            p, n, thr, (ft - g).mean(), g[0::2].mean(), g[1::2].mean(), np.corrcoef(g[1:], g[:-1])[0, 1], np.corrcoef(ft[1:], ft[:-1])[0, 1]))
        print('| frames | top5 | FT-GPU | ' + ' | '.join(k.split('/')[-1] for k in WCOLS) + ' |'); print('|' + '---|' * (len(WCOLS) + 3))
        for s in range(0, n, 150):
            sl = slice(s, s + 150)
            print('| %d-%d | %d | %.2f | ' % (s, min(s + 150, n), (ft[sl] >= thr).sum(), (ft[sl] - g[sl]).mean()) + ' | '.join('%.2f' % c(k)[sl].mean() for k in WCOLS) + ' |')
        idx = np.arange(1, n); top = idx[ft[1:] >= thr]; mid = idx[(ft[1:] > np.percentile(ft, 40)) & (ft[1:] < np.percentile(ft, 60))]
        rows = []
        for i, k in enumerate(h):
            if not (k.startswith('GPU/') or k.startswith('Exclusive/RenderThread') or k in ('RHIThreadTime', 'GameThreadTime', 'RenderThreadTime')): continue
            v = D[:, i]; eo = v[0::2].mean() - v[1::2].mean(); ds = v[top].mean() - v[mid].mean(); dp = v[top - 1].mean() - v[mid - 1].mean()
            rows.append((abs(ds) + abs(dp) + abs(eo), k, v.mean(), eo, ds, dp, v.std()))
        rows.sort(reverse=True)
        print('\n| column | mean | even-odd | top5-mid (same row) | top5-mid (previous row) | std |\n|---|---|---|---|---|---|')
        for r in rows[:18]: print('| %s | %.3f | %.3f | %.3f | %.3f | %.3f |' % (r[1], r[2], r[3], r[4], r[5], r[6]))
        print()


if __name__ == '__main__':
    main(sys.argv[1:])
