import unreal
m = unreal.load_asset('/Engine/EngineSky/VolumetricClouds/m_SimpleVolumetricCloud_Inst')
print('cloud material', m, type(m))
try:
    print('scalars', [(p.get_editor_property('parameter_info').get_editor_property('name'), p.get_editor_property('parameter_value')) for p in m.get_editor_property('scalar_parameter_values')])
    print('vectors', [(p.get_editor_property('parameter_info').get_editor_property('name'), p.get_editor_property('parameter_value')) for p in m.get_editor_property('vector_parameter_values')])
except Exception as e: print('err', e)
par = m.get_editor_property('parent'); print('parent', par)
try:
    print('parent scalars', unreal.MaterialEditingLibrary.get_scalar_parameter_names(par))
    print('parent vectors', unreal.MaterialEditingLibrary.get_vector_parameter_names(par))
except Exception as e: print('err2', e)
print([p for p in dir(unreal.VolumetricCloudComponent) if not p.startswith('_')][:120])
