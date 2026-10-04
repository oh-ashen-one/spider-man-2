import unreal
mel = unreal.MaterialEditingLibrary
for n in ('M_TerrainCards','M_TerrainLeaves','M_TerrainClump'):
    m = unreal.load_asset('/Game/Terrain/Materials/'+n)
    for prop in (unreal.MaterialProperty.MP_EMISSIVE_COLOR, unreal.MaterialProperty.MP_BASE_COLOR, unreal.MaterialProperty.MP_OPACITY_MASK, unreal.MaterialProperty.MP_SUBSURFACE_COLOR):
        node = mel.get_material_property_input_node(m, prop)
        out = mel.get_material_property_input_node_output_name(m, prop)
        print('PROBE', n, str(prop), node.get_class().get_name() if node else None, out)
