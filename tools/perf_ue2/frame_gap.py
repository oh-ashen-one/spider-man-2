#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See DISCLAIMER.md.
"""Piece F (round 07): the frame-pacing check of the round-06 critic, from a run's CsvProfiler file (csv.csv or csv.csv.gz).
  gap_top5_samerow  mean(FrameTime - GPUTime) over the slowest 5 % of frames (by FrameTime), both columns of the SAME csv row = the critic's measure.
                    Pass line (round-07 target): <= 1.2 ms.
  gap_top5_aligned  the same with GPUTime taken from the PREVIOUS row: the CSV's GPUTime is the GPU time of the last frame the GPU has finished,
                    which on this Metal pipeline is the frame before (corr(FT[n], GPU[n-1]) is reported; it is the larger one in every round-06 run).
  gap_mid           mean gap over the 40-60 % frames (FrameTime percentile), both alignments.
  p50 / p95         CSV FrameTime percentiles; hitches = frames > 25 ms and > 2x median.
  stalls            mean / p95 of every RHITStalls/*, RHITFlushes/*, RenderThreadIdle/* column present (run the game with
                    -csvCategories=RHITStalls,RHITFlushes), and of the same columns in the top-5 % frames.
usage: frame_gap.py <csv> [<csv> ...] [--json out.json] [--md out.md]"""
import argparse, csv, gzip, json, os, sys
import numpy as np


def load(p):
    rows = list(csv.reader(gzip.open(p, 'rt') if p.endswith('.gz') else open(p)))
    hdr = rows[0]; n = len(hdr); data = []
    for r in rows[1:]:
        if len(r) < n or r[0] == 'EVENTS' or r[0].startswith('['): continue
        try: data.append([float(x) if x != '' else 0.0 for x in r[:n]])
        except ValueError: continue
    return hdr, np.array(data)


def analyse(p):
    h, D = load(p); c = lambda k: D[:, h.index(k)]
    ft, g = c('FrameTime'), c('GPUTime')
    top = ft >= np.percentile(ft, 95); mid = (ft > np.percentile(ft, 40)) & (ft < np.percentile(ft, 60))
    ti, mi = np.where(top)[0], np.where(mid)[0]
    ti1, mi1 = ti[ti > 0], mi[mi > 0]
    med = float(np.median(ft))
    out = {'csv': p, 'frames': int(len(ft)), 'p50': round(float(np.percentile(ft, 50)), 2), 'p95': round(float(np.percentile(ft, 95)), 2),
           'p99': round(float(np.percentile(ft, 99)), 2), 'hitches': int(((ft > 25) & (ft > 2 * med)).sum()),
           'gpu_p50': round(float(np.percentile(g, 50)), 2), 'gpu_p95': round(float(np.percentile(g, 95)), 2),
           'gap_mean': round(float((ft - g).mean()), 2),
           'gap_top5_samerow': round(float((ft[top] - g[top]).mean()), 2), 'gap_mid_samerow': round(float((ft[mid] - g[mid]).mean()), 2),
           'gap_top5_aligned': round(float((ft[ti1] - g[ti1 - 1]).mean()), 2), 'gap_mid_aligned': round(float((ft[mi1] - g[mi1 - 1]).mean()), 2),
           'corr_ft_gpu_same': round(float(np.corrcoef(ft[1:], g[1:])[0, 1]), 2), 'corr_ft_gpu_prev': round(float(np.corrcoef(ft[1:], g[:-1])[0, 1]), 2),
           'gpu_even_odd': [round(float(g[0::2].mean()), 2), round(float(g[1::2].mean()), 2)]}
    st = {}
    for i, k in enumerate(h):
        if k.startswith(('RHITStalls/', 'RHITFlushes/', 'RenderThreadIdle/')) or k in ('RHIThreadTime', 'RenderThreadTime', 'GameThreadTime'):
            v = D[:, i]; st[k] = {'mean': round(float(v.mean()), 3), 'p95': round(float(np.percentile(v, 95)), 3), 'top5_mean': round(float(v[top].mean()), 3),
                                  'top5_prev_mean': round(float(v[ti1 - 1].mean()), 3)}
    out['stalls'] = st
    out['pass_gap_le_1.2'] = out['gap_top5_samerow'] <= 1.2
    out['pass_p95_le_18.0'] = out['p95'] <= 18.0
    out['pass_p50_le_16.67'] = out['p50'] <= 16.67
    return out


def md(res):
    L = ['| run | frames | p50 | p95 | hitches | GPU p95 | gap mean | gap top5 (same row) | gap top5 (GPU of previous row) | gap mid same / prev | corr FT~GPU same / prev | p95<=18.0 | p50<=16.67 | gap<=1.2 |',
         '|' + '---|' * 14]
    for r in res:
        L.append('| %s | %d | %.2f | %.2f | %d | %.2f | %.2f | %.2f | %.2f | %.2f / %.2f | %.2f / %.2f | %s | %s | %s |' % (
            os.path.basename(os.path.dirname(r['csv'])) or r['csv'], r['frames'], r['p50'], r['p95'], r['hitches'], r['gpu_p95'], r['gap_mean'],
            r['gap_top5_samerow'], r['gap_top5_aligned'], r['gap_mid_samerow'], r['gap_mid_aligned'], r['corr_ft_gpu_same'], r['corr_ft_gpu_prev'],
            'PASS' if r['pass_p95_le_18.0'] else 'FAIL', 'PASS' if r['pass_p50_le_16.67'] else 'FAIL', 'PASS' if r['pass_gap_le_1.2'] else 'FAIL'))
    stk = sorted({k for r in res for k in r['stalls']})
    if stk:
        L += ['', '| run | ' + ' | '.join(k for k in stk) + ' |', '|' + '---|' * (len(stk) + 1)]
        for r in res:
            L.append('| %s | ' % (os.path.basename(os.path.dirname(r['csv'])) or r['csv']) + ' | '.join(
                ('%.3f / %.3f' % (r['stalls'][k]['mean'], r['stalls'][k]['top5_mean'])) if k in r['stalls'] else '-' for k in stk) + ' |')
        L.append('(stall cells: mean over all frames / mean over the slowest 5 % frames, ms)')
    return '\n'.join(L)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('csvs', nargs='+'); ap.add_argument('--json'); ap.add_argument('--md')
    a = ap.parse_args()
    res = [analyse(p) for p in a.csvs]
    t = md(res); print(t)
    if a.json: json.dump(res, open(a.json, 'w'), indent=1)
    if a.md: open(a.md, 'w').write(t + '\n')


if __name__ == '__main__':
    main()
