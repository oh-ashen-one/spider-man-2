#!/usr/bin/env python3
"""Builder evidence crops of a round (4K frames), written to <round>/builder_checks/: the areas the round-06 critic named (defect list), so a reader sees the same pixels
the builder looked at. Crops are plain pixel copies (no annotation).   usage: builder_crops.py <round_dir> [out_dir]"""
import os, sys
from PIL import Image
R = sys.argv[1]; O = sys.argv[2] if len(sys.argv) > 2 else os.path.join(R, 'builder_checks'); os.makedirs(O, exist_ok=True)
CROPS = [  # name, 4K frame, x0, y0, x1, y1
 ('S1_fascia_sign', 'S1_avenue_street', 0, 560, 700, 900), ('S1_left_shop_windows', 'S1_avenue_street', 340, 860, 1500, 1320), ('S1_right_shop_windows', 'S1_avenue_street', 2500, 1080, 3000, 1300),
 ('S3_wall_mural', 'S3_rooftop_watertower', 500, 0, 1760, 1960), ('S4_far_band', 'S4_perch_skyline', 800, 320, 2800, 720),
 ('S5_stair_wall_and_block', 'S5_timessq_south', 2400, 1300, 3840, 2160), ('S5_billboards_left', 'S5_timessq_south', 0, 300, 1300, 1500),
 ('S6_slogan_area', 'S6_timessq_street', 2000, 200, 3200, 900), ('S6_racer_billboard_area', 'S6_timessq_street', 1300, 800, 1900, 1300),
]
for name, view, x0, y0, x1, y1 in CROPS:
    f = os.path.join(R, f'{view}_3840x2160.jpg')
    if not os.path.exists(f): print('missing', f); continue
    Image.open(f).convert('RGB').crop((x0, y0, x1, y1)).save(os.path.join(O, name + '.jpg'), quality=92); print(name)
