#!/usr/bin/env python3
"""pairs.json for tools/night1/abpack.py (blind critic pack, piece E): our round stills vs the matching reference stills (private ~/spiderman-learnings/refs, never committed)
+ progress pairs (previous round = the city alone vs this round) + the movies. Notes are neutral view descriptions (no hint which side is ours).
usage: make_pairs.py <round dir> <out pairs.json>"""
import json, sys, os
R = os.path.abspath(sys.argv[1]); out = sys.argv[2]
REF = '/Users/midir/spiderman-learnings/refs/streets/'; TRAV = '/Users/midir/spiderman-learnings/refs/traversal/'
S = lambda i: os.path.join(R, 'stills', i + '.jpg')
pairs = [
 ('park-south-high',   S('p1_south'),      REF + 'centralpark-skyline-over-park__cp_1230.jpg', 'high view over a large park toward a skyline, warm daylight, lawns, paths and tree masses below'),
 ('park-reservoir',    S('p2_reservoir'),  REF + 'centralpark-aerial-ballfields__cp_0554.jpg', 'aerial view over a park water basin, running track and woods, daylight'),
 ('park-pond-woods',   S('p3_lake'),       TRAV + 'swing-over-pond-skyline__cp_1139.jpg', 'view over a park pond with woodland banks, skyline beyond'),
 ('park-great-lawn',   S('p4_greatlawn'),  REF + 'centralpark-aerial-ballfields__cp_0554.jpg', 'high view over open meadows with ball fields and woods'),
 ('park-lawn-eye',     S('p10_lawn_eye'),  REF + 'centralpark-meadow-skyline__cp_0605.jpg', 'eye-level view over a mown lawn toward the tree line and skyline'),
 ('shore-west',        S('p6_west_shore'), REF + 'waterfront-dn__dn_0052.jpg', 'waterfront edge from above: seawall, esplanade, water, piers'),
 ('shore-east',        S('p7_east_shore'), REF + 'river-queens-aerial__gr_0936.jpg', 'river shoreline from above with the far bank'),
 ('piers',             S('p8_pier'),       REF + 'river-pier-golden__gr_0555.jpg', 'piers and water from a low aerial position'),
 ('progress-park-south', S('p1_south'), os.path.join(R, 'stills', 'base_p1_south.jpg'), 'two versions of the same high park view (one is the newer build)'),
 ('progress-reservoir',  S('p2_reservoir'), os.path.join(R, 'stills', 'base_p2_reservoir.jpg'), 'two versions of the same view over the park water basin (one is the newer build)'),
 ('progress-lawn-eye',   S('p10_lawn_eye'), os.path.join(R, 'stills', 'base_p10_lawn_eye.jpg'), 'two versions of the same eye-level lawn view (one is the newer build)'),
 ('progress-west-shore', S('p6_west_shore'), os.path.join(R, 'stills', 'base_p6_west_shore.jpg'), 'two versions of the same shoreline view (one is the newer build)'),
]
pairs = [dict(id=i, x=x, y=y, note=n) for i, x, y, n in pairs]
miss = [(p['id'], k, p[k]) for p in pairs for k in ('x', 'y') if not os.path.exists(p[k])]
for m in miss: print('MISSING', m)
pairs = [p for p in pairs if os.path.exists(p['x']) and os.path.exists(p['y'])]
os.makedirs(os.path.dirname(out), exist_ok=True); json.dump(pairs, open(out, 'w'), indent=1); print(len(pairs), 'pairs ->', out)
