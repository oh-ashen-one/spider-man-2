import unreal
def p(*a): print('[probe]', *a)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
EAL = unreal.EditorAssetLibrary
cl = '/Game/Island/Probe/Probe_Classic'
if not EAL.does_asset_exist(cl):
    les.new_level(cl, False); eas.spawn_actor_from_class(unreal.PointLight, unreal.Vector(0, 0, 300))
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(); unreal.EditorLoadingAndSavingUtils.save_map(w, cl)
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Island/Probe/Probe_WP')
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
li = eas.spawn_actor_from_class(unreal.LevelInstance, unreal.Vector(0, 0, 0))
p('li', li, [x for x in dir(li) if 'world' in x.lower() or 'level' in x.lower()][:40])
for prop in ('world_asset', 'WorldAsset', 'desired_runtime_behavior', 'DesiredRuntimeBehavior'):
    try: p(prop, li.get_editor_property(prop))
    except Exception as e: p('ERR', prop, str(e)[:150])
wa = unreal.load_asset(cl)
for prop in ('world_asset', 'WorldAsset'):
    try: li.set_editor_property(prop, wa); p('set ok', prop, li.get_editor_property(prop)); break
    except Exception as e: p('ERR set', prop, str(e)[:150])
try: p('set_world_asset', li.set_world_asset(wa))
except Exception as e: p('ERR set_world_asset', str(e)[:150])
try:
    lis = unreal.get_editor_subsystem(unreal.LevelInstanceSubsystem) if hasattr(unreal, 'LevelInstanceSubsystem') else None
    p('LIS', lis)
except Exception as e: p('ERR lis', e)
li.set_editor_property('is_spatially_loaded', False) if True else None
p('saved', unreal.EditorLoadingAndSavingUtils.save_map(w, '/Game/Island/Probe/Probe_WP'))
