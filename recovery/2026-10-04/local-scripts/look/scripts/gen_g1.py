import json
def col(r, g, b, a=1): return "(R=%g,G=%g,B=%g,A=%g)" % (r, g, b, a)
def dump(name, variants): json.dump({'variants': variants}, open('/Users/midir/sm2-n1/_scratch/look/eval/%s.json' % name, 'w'), indent=1)
def G(**k):
    d = dict(wt=7300, mie_col=(1, 1, 1), mie=0.01, aps=3.0, fog_den=0.0052, fog_col=(0.26, 0.2, 0.2), dir_col=(0.3, 0.15, 0.06), bias=0.95, shoulder=0.3, sun=44000, wclip=0.04)
    d.update(k)
    return ["set SkyAtmosphere - MieScattering " + col(*d['mie_col']), "set SkyAtmosphere - MieScatteringScale %g" % d['mie'],
            "set SkyAtmosphere - AerialPespectiveViewDistanceScale %g" % d['aps'],
            "set HeightFog - FogDensity %g" % d['fog_den'], "set HeightFog - FogInscatteringLuminance " + col(*d['fog_col']),
            "set HeightFog - DirectionalInscatteringLuminance " + col(*d['dir_col']),
            "post WhiteTemp %g" % d['wt'], "post AutoExposureBias %g" % d['bias'], "post FilmShoulder %g" % d['shoulder'], "post FilmWhiteClip %g" % d['wclip'],
            "set Sun - Intensity %g" % d['sun']]
dump('v_g1', {
    'a_wt7800': G(wt=7800),
    'b_wt8300': G(wt=8300),
    'c_miewarm': G(wt=7800, mie_col=(1.0, 0.72, 0.45), mie=0.03, aps=5.0),
    'd_denser': G(wt=7800, mie_col=(1.0, 0.72, 0.45), mie=0.03, aps=5.0, fog_den=0.0075, fog_col=(0.42, 0.28, 0.2)),
    'e_shoulder': G(wt=7800, mie_col=(1.0, 0.72, 0.45), mie=0.03, aps=5.0, shoulder=0.5),
    'f_bias': G(wt=7800, mie_col=(1.0, 0.72, 0.45), mie=0.03, aps=5.0, bias=0.8),
    'g_combo': G(wt=7800, mie_col=(1.0, 0.72, 0.45), mie=0.03, aps=5.0, fog_den=0.0075, fog_col=(0.42, 0.28, 0.2), shoulder=0.5, bias=0.85, sun=38000)})
