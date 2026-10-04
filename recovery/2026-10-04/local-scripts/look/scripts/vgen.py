# variant command generator for midday sweeps
import json,sys
def col(n,r,g,b,a=1): return "(R=%g,G=%g,B=%g,A=%g)"%(r,g,b,a)
def M(**k):
    d=dict(ray_col=(0.175,0.409,1.0),ray=0.02,mie=0.10,mieg=0.6,sky=1.5,sl=2.0,fogamb=1.0,hfc=1.0,aps=3.0,bias=0.7,offs=0.004,fog_den=0.0032,apd=0.0)
    d.update(k)
    c=["exec showflag.fog 1","exec showflag.volumetricfog 1","exec showflag.atmosphere 1","set Clouds VolumetricCloud bHiddenInGame False",
     "set SkyAtmosphere - RayleighScattering "+col('',*d['ray_col']),
     "set SkyAtmosphere - RayleighScatteringScale %g"%d['ray'],"set SkyAtmosphere - MieScatteringScale %g"%d['mie'],"set SkyAtmosphere - MieAnisotropy %g"%d['mieg'],
     "set SkyAtmosphere - SkyLuminanceFactor "+col('',d['sky'],d['sky'],d['sky']),
     "set SkyAtmosphere - HeightFogContribution %g"%d['hfc'],"set SkyAtmosphere - AerialPespectiveViewDistanceScale %g"%d['aps'],
     "set SkyLight - Intensity %g"%d['sl'],
     "set HeightFog - SkyAtmosphereAmbientContributionColorScale "+col('',d['fogamb'],d['fogamb'],d['fogamb']),
     "set HeightFog - FogDensity %g"%d['fog_den'],
     "post AutoExposureBias %g"%d['bias'],
     "post ColorOffset (X=%g,Y=%g,Z=%g,W=0)"%(d['offs'],d['offs']*1.05,d['offs']*1.15)]
    return c
def dump(name,variants): json.dump({'variants':variants},open('/Users/midir/sm2-n1/_scratch/look/eval/%s.json'%name,'w'),indent=1)
