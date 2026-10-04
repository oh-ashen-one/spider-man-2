import unreal
mel = unreal.MaterialEditingLibrary
par = unreal.load_asset('/Engine/EngineSky/VolumetricClouds/m_SimpleVolumetricCloud')
for n in mel.get_scalar_parameter_names(par): print('S', n, mel.get_material_default_scalar_parameter_value(par, n))
for n in mel.get_vector_parameter_names(par): print('V', n, mel.get_material_default_vector_parameter_value(par, n))
# atmosphere / post property discovery
print([p for p in dir(unreal.SkyAtmosphereComponent) if 'lumin' in p or 'height_fog' in p or 'aerial' in p or 'multi' in p])
print([p for p in dir(unreal.ExponentialHeightFogComponent) if 'sky' in p or 'inscat' in p or 'cubemap' in p])
print([p for p in dir(unreal.SkyLightComponent) if not p.startswith('_') and ('occl' in p or 'cloud' in p or 'capture' in p or 'lower' in p or 'sky' in p or 'cubemap' in p)])
print([p for p in dir(unreal.PostProcessSettings) if 'lumen' in p and p.startswith('lumen')])
print([p for p in dir(unreal.PostProcessSettings) if p.startswith('color_') or p.startswith('film_') or p.startswith('white') or 'contrast' in p or 'bloom' in p or 'exposure' in p][:80])
