from gen_n1 import N, dump
from gen_n3 import Z, CONE
def W(extra=(), **k):
    return Z(4000, CONE + list(extra), **k)
APDS = lambda v: "set SkyAtmosphere - AerialPespectiveViewDistanceScale %g" % v
dump('v_n4', {
    't0': W(),
    't1_fog': W(fog=0.01),
    't2_apds': W([APDS(10)]),
    't3_moon': W(moon=30, sky=3.0),
    't4_fog_apds': W([APDS(10)], fog=0.01),
    't5_all': W([APDS(10)], fog=0.01, moon=30),
    't6_bias': W(bias=-0.3)})
