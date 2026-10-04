import unreal, json
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/Manhattan')
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
rows = []
for a in eas.get_all_level_actors():
    for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        sm = c.get_editor_property('static_mesh')
        if not sm: continue
        mats = [m.get_editor_property('material_interface') for m in sm.get_editor_property('static_materials')]
        bl = [str(m.get_base_material().get_editor_property('blend_mode')).split('.')[-1].split(':')[0] for m in mats if m]
        try: cd = (c.get_editor_property('instance_start_cull_distance'), c.get_editor_property('instance_end_cull_distance'))
        except Exception: cd = None
        rows.append({'actor': a.get_actor_label(), 'mesh': sm.get_name(), 'n': c.get_instance_count(), 'tris': sm.get_num_triangles(0),
                     'nanite': bool(sm.get_editor_property('nanite_settings').enabled), 'blend': bl, 'cull': cd,
                     'wpo_disable_dist': c.get_editor_property('world_position_offset_disable_distance') if hasattr(c, 'world_position_offset_disable_distance') else None})
json.dump(rows, open('/Users/midir/sm2-n1/_scratch/perf/audit_hism.json', 'w'), indent=0)
print('[hism]', len(rows))
