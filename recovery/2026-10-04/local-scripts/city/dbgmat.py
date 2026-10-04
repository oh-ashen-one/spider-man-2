import unreal
mel=unreal.MaterialEditingLibrary
m=unreal.load_asset('/Game/City/Materials/M_CityFacade')
c=[e for e in unreal.MaterialEditingLibrary.get_material_expressions(m) if isinstance(e, unreal.MaterialExpressionCustom)] if hasattr(mel,'get_material_expressions') else None
print('custom', c)
