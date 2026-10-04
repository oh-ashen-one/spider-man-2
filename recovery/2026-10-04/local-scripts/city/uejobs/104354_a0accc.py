JOB_ARGS = {}
import unreal
EAL = unreal.EditorAssetLibrary
for p in EAL.list_assets('/Game/City/Meshes/signage', recursive=False):
    sm = unreal.load_asset(p)
    sms = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    print(p.split('/')[-1], 'uv ch', sms.get_num_uv_channels(sm, 0), 'nanite', sm.get_editor_property('nanite_settings').enabled, 'mat', sm.get_material(0).get_name())
