JOB_ARGS = {}

import unreal
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Tests/City/City_View_S1_avenue_street')
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
print([a.get_actor_label() for a in eas.get_all_level_actors() if 'street' in a.get_actor_label() or 'tree' in a.get_actor_label()][:20])
lv = unreal.EditorLevelUtils
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
print([l.get_path_name() for l in unreal.EditorLevelUtils.get_levels(w)])
