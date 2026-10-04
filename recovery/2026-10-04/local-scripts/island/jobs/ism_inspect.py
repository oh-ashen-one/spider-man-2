import unreal, json
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/Manhattan_WP_ism')
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
acts = unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor)
n_act = n_inst = n_bad = 0; spatial = 0; samples = []
for a in acts:
    if not a.get_actor_label().startswith('WHBoxes__t'): continue
    n_act += 1
    if a.get_editor_property('is_spatially_loaded'): spatial += 1
    for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        m = c.get_editor_property('static_mesh')
        ok = m and m.get_path_name().startswith('/Engine/BasicShapes/Cube') and not c.is_visible() and c.get_collision_profile_name() == 'BlockAll'
        if not ok: n_bad += 1
        k = c.get_instance_count(); n_inst += k
        if len(samples) < 40 and k:
            t = c.get_instance_transform(0, True); samples.append([t.translation.x, t.translation.y, t.translation.z, t.scale3d.x, t.scale3d.y, t.scale3d.z])
res = {'tile_actors': n_act, 'instances': n_inst, 'bad_components': n_bad, 'spatially_loaded_actors': spatial, 'samples': samples}
open('/Users/midir/sm2-n1/_scratch/island/ism_inspect.json', 'w').write(json.dumps(res))
unreal.log('ISM_INSPECT ' + json.dumps({k: v for k, v in res.items() if k != 'samples'}))
