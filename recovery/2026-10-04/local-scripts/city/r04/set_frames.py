import unreal
EAL = unreal.EditorAssetLibrary
mat = unreal.load_asset('/Game/City/Materials/M_CityFrame')
n = 0
for p in EAL.list_assets('/Game/City/Meshes/generic', recursive=False):
    if 'SM_tsFrames' in p:
        sm = unreal.load_asset(p); sm.set_material(0, mat); EAL.save_asset(p); n += 1
print('tsFrames meshes retargeted', n)
