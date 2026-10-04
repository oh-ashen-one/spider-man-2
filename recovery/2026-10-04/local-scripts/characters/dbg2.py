import unreal
MEL = unreal.MaterialEditingLibrary
i = unreal.load_asset('/Game/Characters/Hero/Materials/MI_Hero_Suit')
for n in ('BaseColor', 'ORM', 'Normal', 'DetailNormal'):
    print('DBG', n, MEL.get_material_instance_texture_parameter_value(i, n))
t = unreal.load_asset('/Game/Characters/Hero/Textures/T_Hero_BaseColor')
print('DBG tex', t, t.get_editor_property('srgb'), t.get_editor_property('compression_settings'), t.blueprint_get_size_x() if t else None)
m = unreal.load_asset('/Game/Characters/Shared/Materials/M_Char_Suit')
print('DBG texparams', MEL.get_texture_parameter_names(m))
