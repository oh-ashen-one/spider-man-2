import unreal
m = unreal.load_asset("/Game/Traversal/HeroDev/HeroDev/SkeletalMeshes/SpiderMan.SpiderMan")
sk = m.skeleton
names = [str(n) for n in unreal.SkeletalMeshEditorSubsystem and []]
try:
    ref = m.get_editor_property("ref_skeleton")
except Exception as e:
    ref = None
s = unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem) if hasattr(unreal, "SkeletalMeshEditorSubsystem") else None
bn = []
for i in range(80):
    try:
        n = sk.get_editor_property("bone_tree") if False else None
    except Exception:
        pass
anim = unreal.load_asset("/Game/Traversal/HeroDev/swing.swing")
try:
    names = unreal.AnimationLibrary.get_animation_track_names(anim)
except Exception as e:
    names = [str(e)]
unreal.log("BONES " + ", ".join(str(n) for n in names))
