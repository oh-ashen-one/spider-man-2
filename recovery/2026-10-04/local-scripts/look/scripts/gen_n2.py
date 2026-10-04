from gen_n1 import N, dump
def Y(lamp=1.7, halo=60, head=1000, extra=(), **k):
    d = dict(bias=-0.3, moon=22, sky=3.0); d.update(k)
    return N(["set LampHalo_* PointLight Intensity %g" % halo, "set CarHead_* SpotLight Intensity %g" % head] + list(extra), lamp=lamp, **d)
dump('v_n2', {
    'm1': Y(),
    'm2': Y(lamp=2.4, bias=-0.7),
    'm3': Y(lamp=2.4, halo=120, bias=-0.8),
    'm4': Y(lamp=3.0, head=2000, bias=-0.9),
    'm5': Y(lamp=2.4, bias=-0.7, contrast=1.5),
    'm6': Y(lamp=2.0, halo=120, head=2000, bias=-0.6),
    'm7': Y(lamp=2.0, halo=120, head=2000, bias=-0.6, offs=(0.008, 0.01, 0.016)),
    'm8': Y(lamp=2.0, halo=120, head=2000, bias=-0.6, moon=30, sky=3.5)})
