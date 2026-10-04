t = unreal.AssetImportTask()
t.filename = '/Users/midir/sm2-n1/_scratch/characters/ueimport/SK_Hero.glb'
t.destination_path = '/Game/Characters/_ImportTest'
t.automated = True; t.save = False; t.replace_existing = True
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
paths = list(t.imported_object_paths)
print(len(paths))
for p in paths[:200]:
    a = unreal.load_asset(p)
    s = type(a).__name__
    if isinstance(a, unreal.AnimSequence):
        dfr = a.get_editor_property('target_frame_rate') if hasattr(a,'target_frame_rate') else None
        s += ' len=%.3f' % a.get_play_length()
        try:
            s += ' fr=%s nkeys=%s' % (unreal.AnimationLibrary.get_frame_rate(a), unreal.AnimationLibrary.get_num_keys(a))
        except Exception as e: s += ' ' + str(e)[:80]
    print(p, s)
