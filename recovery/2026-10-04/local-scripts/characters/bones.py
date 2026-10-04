import unreal
a = unreal.load_asset('/Game/Characters/Hero/Anims/A_Hero_run')
print('BONES', [str(n) for n in unreal.AnimationLibrary.get_animation_track_names(a)])
