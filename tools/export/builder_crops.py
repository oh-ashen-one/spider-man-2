#!/usr/bin/env python3
"""Builder evidence crops of a round (4K frames), written to <round>/builder_checks/: the areas of the round's target (round 08: parked cars, traffic, street trees), so a reader sees the same pixels
the builder looked at. Crops are plain pixel copies (no annotation).   usage: builder_crops.py <round_dir> [out_dir]"""
import os, sys
from PIL import Image
R = sys.argv[1]; O = sys.argv[2] if len(sys.argv) > 2 else os.path.join(R, 'builder_checks'); os.makedirs(O, exist_ok=True)
CROPS = [  # name, 4K frame, x0, y0, x1, y1   (round 08: the critic r07 gap: parked cars / traffic / street trees)
 ('S1_left_trees_x0-900', 'S1_avenue_street', 0, 0, 1800, 1500), ('S1_right_curb_cars', 'S1_avenue_street', 2100, 1000, 3840, 1450), ('S1_far_traffic', 'S1_avenue_street', 1500, 1050, 2600, 1350),
 ('S2_avenue_traffic', 'S2_avenue_swing', 1500, 1000, 2500, 2160), ('S2_far_traffic', 'S2_avenue_swing', 1700, 1000, 2200, 1500),
 ('S6_street_cars', 'S6_timessq_street', 500, 1200, 2700, 1700), ('S5_street_cars', 'S5_timessq_south', 0, 1300, 3840, 2160),
]
for name, view, x0, y0, x1, y1 in CROPS:
    f = os.path.join(R, f'{view}_3840x2160.jpg')
    if not os.path.exists(f): print('missing', f); continue
    Image.open(f).convert('RGB').crop((x0, y0, x1, y1)).save(os.path.join(O, name + '.jpg'), quality=92); print(name)
