import unreal
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Tests/City/City_View_S1_avenue_street')
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in eas.get_all_level_actors():
    n = a.get_actor_label()
    if n.startswith('ISM_') and any(k in n for k in ('hydrant', 'trash', 'newsbox', 'pit', 'mailbox', 'bench', 'meter', 'planter', 'shed', 'signpole', 'lamp', 'mast', 'post')):
        c = a.get_component_by_class(unreal.HierarchicalInstancedStaticMeshComponent)
        near = 0
        for i in range(c.get_instance_count()):
            t = c.get_instance_transform(i, True)
            x = t.translation.x / 100; z = t.translation.y / 100
            if 225 < x < 275 and -320 < z < 200: near += 1
        m = c.static_mesh.get_material(0)
        print(n, c.get_instance_count(), 'near', near, 'mesh', c.static_mesh.get_name(), 'mat', m.get_name() if m else None, 'nanite', c.static_mesh.get_editor_property('nanite_settings').enabled)
