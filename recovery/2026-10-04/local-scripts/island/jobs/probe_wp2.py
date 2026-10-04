import unreal
def p(*a): print('[probe]', *a)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
EAL = unreal.EditorAssetLibrary
path = '/Game/Island/Probe/Probe_WP'
ok = les.new_level(path, True)
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
p('new_level', ok, w.get_path_name())
ws = w.get_world_settings()
for prop in ('world_partition', 'b_enable_world_partition'):
    try: p(prop, ws.get_editor_property(prop))
    except Exception as e: p('ERR', prop, e)
wp = None
try:
    wp = ws.get_editor_property('world_partition')
except Exception as e: p('wp err', e)
if wp:
    p('wp class', wp.get_class().get_name())
    for prop in ('runtime_hash', 'editor_hash', 'default_hlod_layer', 'b_enable_streaming', 'enable_streaming'):
        try: p(prop, wp.get_editor_property(prop))
        except Exception as e: p('ERR', prop, str(e)[:120])
    try:
        rh = wp.get_editor_property('runtime_hash'); p('rh class', rh.get_class().get_name())
        for prop in ('streaming_grids', 'grids', 'runtime_partitions', 'b_enable_z_culling'):
            try: v = rh.get_editor_property(prop); p(prop, v)
            except Exception as e: p('ERR rh', prop, str(e)[:120])
    except Exception as e: p('rh err', e)
p('SpatialHashRuntimeGridInfo', [x for x in dir(unreal.SpatialHashRuntimeGridInfo) if not x.startswith('_')][:40])
a = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0,0,0))
p('actor spatial props', [x for x in ('is_spatially_loaded','b_is_spatially_loaded') ])
for prop in ('is_spatially_loaded', 'runtime_grid', 'hlod_layer'):
    try: p(prop, a.get_editor_property(prop))
    except Exception as e: p('ERR actor', prop, str(e)[:120])
try:
    a.set_editor_property('is_spatially_loaded', False); p('set spatial ok', a.get_editor_property('is_spatially_loaded'))
except Exception as e: p('ERR set', e)
p('CustomHLOD', [x for x in dir(unreal.WorldPartitionCustomHLOD) if not x.startswith('_')][:60])
p('HLODLayer', [x for x in dir(unreal.HLODLayer) if not x.startswith('_')][:60])
p('LevelInstance', hasattr(unreal, 'LevelInstance'))
ok = unreal.EditorLoadingAndSavingUtils.save_map(w, path); p('saved', ok)
