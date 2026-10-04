import unreal, traceback
try:
    for nm in ('grass_near_0','grass_near_3','grass_far_0'):
        sm = unreal.load_asset('/Game/TerrainR4/Props/SM_%s' % nm)
        print('INSPECT', nm, 'verts', unreal.EditorStaticMeshLibrary.get_number_verts(sm, 0), 'tris?', 'bounds', sm.get_bounds().box_extent, 'mat', sm.get_material(0).get_name() if sm.get_material(0) else None,
              'hasVC', sm.get_editor_property('has_vertex_colors') if hasattr(sm,'has_vertex_colors') else 'n/a')
    for nm in ('SM_park_blankets',):
        sm = unreal.load_asset('/Game/TerrainR4/Props/' + nm); print('INSPECT', nm, sm.get_bounds().box_extent, sm.get_material(0).get_name())
    for m in ('M_TerrainGrass','M_TerrainBlanket','M_TerrainPark'):
        a = unreal.load_asset('/Game/TerrainR4/Materials/' + m); print('INSPECT mat', m, a.get_editor_property('shading_model') if m=='M_TerrainGrass' else '', 'two_sided', a.get_editor_property('two_sided'))
    unreal.EditorLoadingAndSavingUtils.load_map('/Game/TerrainR4/Terrain_Land')
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in eas.get_all_level_actors():
        lb = a.get_actor_label()
        if lb in ('ISM_grass', 'ISM_parkBlankets'):
            comps = a.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent)
            print('INSPECT actor', lb, [(c.get_instance_count(), c.static_mesh.get_name(), c.get_material(0).get_name(), c.get_editor_property('instance_end_cull_distance')) for c in comps])
except Exception:
    traceback.print_exc()
