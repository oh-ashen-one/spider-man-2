#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See DISCLAIMER.md.
"""Piece F (round 06, round-05 critic lines): S1 look gate of one or more still dirs vs the as-found stills.
  crop  = round-02 S1 crop (485,0,710,490) in 1920x1080 space, 8x8 box SSIM on luma of the area-downsampled still (crop_ssim.py, same code): line >= 0.97
  recess = mean luma of the recess under the sidewalk shed behind the taxi (1920-space x1700-1850, y540-650): line 17.5 +-10 % of the as-found value
usage: s1_gate.py <ref_dir> <test_dir> [...] [--json out.json]   (files view_S1.png)"""
import argparse, json, os, sys
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crop_ssim import luma, ssim

CROP = (485, 0, 710, 490); RECESS = (1700, 540, 1850, 650)


def load(d):
    im = cv2.imread(os.path.join(d, 'view_S1.png'))
    return None if im is None else cv2.resize(im, (1920, 1080), interpolation=cv2.INTER_AREA)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('ref'); ap.add_argument('tests', nargs='+'); ap.add_argument('--json'); a = ap.parse_args()
    R = load(a.ref); yr = luma(R); x0, y0, x1, y1 = CROP; rx0, ry0, rx1, ry1 = RECESS
    ref_rec = float(yr[ry0:ry1, rx0:rx1].mean()); out = {'ref': a.ref, 'ref_recess_luma': round(ref_rec, 2), 'tests': {}}
    for t in a.tests:
        T = load(t)
        if T is None: out['tests'][t] = {'error': 'no view_S1.png'}; continue
        yt = luma(T); rec = float(yt[ry0:ry1, rx0:rx1].mean())
        r = {'crop_ssim': round(ssim(yr[y0:y1, x0:x1], yt[y0:y1, x0:x1]), 4), 'recess_luma': round(rec, 2), 'recess_ratio': round(rec / ref_rec, 3),
             'crop_meanY_ref': round(float(yr[y0:y1, x0:x1].mean()), 1), 'crop_meanY_test': round(float(yt[y0:y1, x0:x1].mean()), 1),
             'full_ssim': round(ssim(yr, yt), 4)}
        r['pass_crop'] = r['crop_ssim'] >= 0.97; r['pass_recess'] = abs(r['recess_ratio'] - 1) <= 0.10
        out['tests'][t] = r
        print('%-60s crop %.4f %s  recess %.1f (%.2fx) %s  full %.4f' % (t, r['crop_ssim'], 'PASS' if r['pass_crop'] else 'fail', rec, r['recess_ratio'], 'PASS' if r['pass_recess'] else 'fail', r['full_ssim']))
    if a.json: json.dump(out, open(a.json, 'w'), indent=1)


if __name__ == '__main__': main()
