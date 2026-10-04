#!/usr/bin/env python3
# offline side-view sky potential from the traversal heightmap (5 m grid): for a hero at (x, y, h over street) travelling along
# axis 'ns' (y) or 'ew' (x), the best ring sky share of a side-on camera (yaw 75..105 off behind, elev 4..28 below the hero,
# 3.3 m) -- same ring as SearchSkyView (16 rays, +-8 / +-11 deg), rays marched through the height field, outside the map = sky
import csv, math, sys
hm = {}
for r in csv.DictReader(open('/Users/midir/sm2-n1/_scratch/traversal/r12/hm/heightmap.csv')):
    hm[(int(float(r['x'])), int(float(r['y'])))] = float(r['z'])
def top(x, y):
    return hm.get((int(round(x / 5.0)) * 5, int(round(y / 5.0)) * 5), None)
RING = [(0, 11), (0, -11), (8, 0), (-8, 0), (8, 11), (-8, 11), (8, -11), (-8, -11), (8, 5), (-8, 5), (8, -5), (-8, -5), (4, 11), (-4, 11), (4, -11), (-4, -11)]
def ray_free(o, d, L=400.0, step=2.0):
    s = 0.6
    while s < L:
        p = (o[0] + d[0] * s, o[1] + d[1] * s, o[2] + d[2] * s)
        z = top(p[0], p[1])
        if z is None: return True
        if p[2] < z: return False
        s += step
    return True
def best(x, y, h, axis):
    fw = (0, 1, 0) if axis == 'ns' else (1, 0, 0)
    back = (-fw[0], -fw[1], 0)
    hero = (x, y, h)
    res = []
    for side in (1, -1):
        bs = 0.0; be = None
        for yd in (75, 90, 105):
            yr = math.radians(yd * side)
            bf = (back[0] * math.cos(yr) - back[1] * math.sin(yr), back[0] * math.sin(yr) + back[1] * math.cos(yr), 0)
            for ed in (4, 12, 20, 28):
                er = math.radians(ed)
                tc = (bf[0] * math.cos(er), bf[1] * math.cos(er), -math.sin(er))
                cam = (hero[0] + tc[0] * 3.3, hero[1] + tc[1] * 3.3, hero[2] + tc[2] * 3.3)
                D = (-tc[0], -tc[1], -tc[2])
                rt = (-D[1], D[0], 0); n = math.hypot(rt[0], rt[1]) or 1; rt = (rt[0] / n, rt[1] / n, 0)
                up = (D[1] * rt[2] - D[2] * rt[1], D[2] * rt[0] - D[0] * rt[2], D[0] * rt[1] - D[1] * rt[0])
                free = 0
                for a, b in RING:
                    ta, tb = math.tan(math.radians(a)), math.tan(math.radians(b))
                    d = (D[0] + rt[0] * ta + up[0] * tb, D[1] + rt[1] * ta + up[1] * tb, D[2] + rt[2] * ta + up[2] * tb)
                    m = math.sqrt(sum(c * c for c in d)); d = tuple(c / m for c in d)
                    o = (cam[0] + d[0] * 3.9, cam[1] + d[1] * 3.9, cam[2] + d[2] * 3.9)
                    free += ray_free(o, d)
                s = free / 16.0
                if s > bs: bs, be = s, (yd * side, ed)
        res.append((bs, be))
    return max(res, key=lambda r: r[0])
if __name__ == '__main__':
    axis = sys.argv[1]; h = float(sys.argv[2])
    x0, x1, y0, y1 = [int(v) for v in sys.argv[3].split(',')]
    step = int(sys.argv[4]) if len(sys.argv) > 4 else 10
    for yy in range(y0, y1 + 1, step):
        line = ''
        for xx in range(x0, x1 + 1, step):
            g = top(xx, yy) or 0.0
            s, _ = best(xx, yy, g + h, axis)
            line += ' .:-=+*#%@'[min(9, int(s * 9.99))] if s > 0 else ' '
        print('%5d %s' % (yy, line))
