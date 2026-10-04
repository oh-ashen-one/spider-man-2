from gen_m5 import M, dump
def S(cmds, lux=None, ang=None, sl=None):
    c = list(cmds)
    if lux is not None: c.append("set Sun - Intensity %g" % lux)
    if ang is not None: c.append("set Sun - LightSourceAngle %g" % ang)
    return c
base = dict(bias=0.9, sky=1.0, offs=0.008)
dump('v_m6', {
    'g1': S(M(**base)),
    'g2': S(M(**base), 8000, 4),
    'g3': S(M(**dict(base, sl=2.5)), 4000, 6),
    'g4': S(M(**dict(base, sl=3.0, bias=1.0)), 2000, 8),
    'g5': S(M(**dict(base, sky=1.0, bias=0.9, ray=0.02, mie=0.25)), 6000, 5),
    'g6': S(M(**dict(base, sky=1.0, bias=0.9, fog_den=0.0045, fogamb=4.0)), 6000, 5)})
