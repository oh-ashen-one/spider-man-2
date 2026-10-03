#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""r06 screening numbers of 1080p / 4K stills (water_spec r06 instruments; 1080p frames are upscaled to 4K first, so hp reads lower than
native 4K): river_low *_rl: near mean / hp; river_sun *_rs: flanks, path ratio (400 px), native sparkle width.  usage: screen.py <dir> [--json out]"""
import glob, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import water_spec as w
d = sys.argv[1]; out = {}
for f in sorted(glob.glob(os.path.join(d, '*.png'))):
    n = os.path.basename(f)[:-4]
    if n.startswith('DBG'): continue
    if n.endswith('_rl'): q = w.r06_low(f); out[n] = q; print('%-10s near mean %5.1f hp %5.2f p1 %5.1f' % (n, q['mean_Y'], q['highpass_sd'], q['p1']))
    elif n.endswith('_rs'): q = w.r06_sun(f); out[n] = q; print('%-10s flanks %5.1f (%5.1f / %5.1f) path400 %5.1f ratio %.2f (200: %.2f) sparkle native %4.1f %%' % (n, q['flank_mean'], q['flank_L'], q['flank_R'], q['path400_Y'], q['path400_ratio'], q['path_ratio'], q['sparkle_width_native_pct']))
if '--json' in sys.argv: json.dump(out, open(sys.argv[sys.argv.index('--json') + 1], 'w'), indent=1)
