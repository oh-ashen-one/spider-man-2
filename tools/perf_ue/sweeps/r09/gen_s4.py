#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""Round 09: live-tuning variants of the SKY / AERIAL-PERSPECTIVE knobs of the fixed golden preset (Look_Rig_golden) for the S4 perch.
Every variant sets EVERY knob below (tour state is sticky).  Base = presets.golden of Scripts/look_presets.json.
usage: gen_s4.py <out.json> '<json {name: {knob: value}}>'      knobs: ray mie mie_abs aniso ap ap_start hfc skylum(r,g,b) miecol(r,g,b)
       dens fall start maxop fogcol(r,g,b) dircol(r,g,b) direxp dirstart cutoff haze_dens haze_off haze_fall
       (multipliers are not used: values are absolute)"""
import json, os, sys
WT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
P = json.load(open(os.path.join(WT, 'unreal/WebHomage/Scripts/look_presets.json')))['presets']['golden']
A, F = P['atmosphere'], P['fog']
BASE = dict(ray=A['rayleigh_scattering_scale'], mie=A['mie_scattering_scale'], mie_abs=A['mie_absorption_scale'], aniso=A['mie_anisotropy'],
            ap=A['aerial_perspective_distance_scale'], ap_start=A['aerial_perspective_start_depth'], hfc=A['height_fog_contribution'],
            skylum=A['sky_luminance_factor'][:3], miecol=A['mie_scattering'][:3],
            dens=F['fog_density'], fall=F['fog_height_falloff'], start=F['start_distance'], maxop=F['fog_max_opacity'], fogcol=F['fog_inscattering_luminance'][:3],
            dircol=F['directional_inscattering_luminance'][:3], direxp=F['directional_inscattering_exponent'], dirstart=F['directional_inscattering_start_distance'],
            cutoff=F.get('fog_cutoff_distance', 0.0), haze_dens=F['haze']['fog_density'], haze_off=F['haze']['fog_height_offset'], haze_fall=F['haze']['fog_height_falloff'])
def c4(c): return '(R=%g,G=%g,B=%g,A=1)' % tuple(c)
def lines(k):
    d = dict(BASE); d.update(k)
    s, f = 'set SkyAtmosphere SkyAtmosphereComponent ', 'set HeightFog ExponentialHeightFogComponent '
    return [s + 'RayleighScatteringScale %g' % d['ray'], s + 'MieScatteringScale %g' % d['mie'], s + 'MieAbsorptionScale %g' % d['mie_abs'],
            s + 'MieAnisotropy %g' % d['aniso'], s + 'AerialPespectiveViewDistanceScale %g' % d['ap'], s + 'AerialPerspectiveStartDepth %g' % d['ap_start'],
            s + 'HeightFogContribution %g' % d['hfc'], s + 'SkyLuminanceFactor ' + c4(d['skylum']), s + 'MieScattering ' + c4(d['miecol']),
            f + 'FogDensity %g' % d['dens'], f + 'FogHeightFalloff %g' % d['fall'], f + 'StartDistance %g' % d['start'], f + 'FogMaxOpacity %g' % d['maxop'],
            f + 'FogInscatteringLuminance ' + c4(d['fogcol']), f + 'DirectionalInscatteringLuminance ' + c4(d['dircol']),
            f + 'DirectionalInscatteringExponent %g' % d['direxp'], f + 'DirectionalInscatteringStartDistance %g' % d['dirstart'], f + 'FogCutoffDistance %g' % d['cutoff'],
            f + 'SecondFogData (FogDensity=%g,FogHeightFalloff=%g,FogHeightOffset=%g)' % (d['haze_dens'], d['haze_fall'], d['haze_off'])]
if __name__ == '__main__':
    out, spec = sys.argv[1], json.loads(sys.argv[2])
    json.dump({'variants': {n: lines(k) for n, k in spec.items()}, 'spec': spec, 'base': BASE}, open(out, 'w'), indent=1)
    print('wrote', out, len(spec), 'variants')
