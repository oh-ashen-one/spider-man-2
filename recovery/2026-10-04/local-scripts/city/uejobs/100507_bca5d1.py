JOB_ARGS = {}
import unreal
p = '/Game/City/Materials/MPC_City'
m = unreal.EditorAssetLibrary.load_asset(p)
sp = [q for q in m.get_editor_property('scalar_parameters') if not str(q.get_editor_property('parameter_name')).endswith('1')]
m.set_editor_property('scalar_parameters', sp)
unreal.EditorAssetLibrary.save_asset(p)
print([str(q.get_editor_property('parameter_name')) for q in sp])
