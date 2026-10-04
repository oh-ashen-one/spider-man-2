JOB_ARGS = {}
import unreal, math
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Tests/City/City_View_S5_timessq_south')
# camera (browser -> UE): U(x,y,z) = (100x, 100z, 100y)
pos = (-12*100, -255*100, 6*100); tgt = (0, -40*100, 48*100)
import numpy as np
P = np.array(pos, float); T = np.array(tgt, float)
f = T - P; f /= np.linalg.norm(f)
# UE: X forward east.. use generic right = f x up(0,0,1)
right = np.cross(f, [0, 0, 1.0]); right /= np.linalg.norm(right)
up = np.cross(right, f)
tan = math.tan(math.radians(80) / 2)
def ray(px, py, W=1920, H=1080):
    x = (px / W * 2 - 1) * tan; y = (1 - py / H * 2) * tan * H / W
    d = f + x * right + y * up
    return d / np.linalg.norm(d)
def hit(o, e, O, d):
    lo = o - e; hi = o + e
    with np.errstate(divide='ignore', invalid='ignore'):
        t1 = (lo - O) / d; t2 = (hi - O) / d
    tmin = np.nanmax(np.minimum(t1, t2)); tmax = np.nanmin(np.maximum(t1, t2))
    return (tmax >= max(tmin, 0)), tmin
res = []
for a in eas.get_all_level_actors():
    try: o, e = a.get_actor_bounds(False)
    except Exception: continue
    o = np.array([o.x, o.y, o.z]); e = np.array([e.x, e.y, e.z])
    for (px, py) in [(1750, 100), (1660, 60), (1870, 500)]:
        h, t = hit(o, e, P, ray(px, py))
        if h and t > 0 and t < 5e5:
            res.append((round(t / 100, 1), a.get_actor_label(), a.get_class().get_name(), (px, py), [round(v/100) for v in e]))
res.sort(key=lambda r: r[0])
seen = set()
for r in res[:40]:
    k = (r[1], r[3])
    if k in seen: continue
    seen.add(k); print(r)
