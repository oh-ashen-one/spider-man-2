import unreal
SRC = "/Users/midir/sm2-n1/traversal/unreal/WebHomage/Saved/HeroDev_spiderman_png.glb"
DST = "/Game/Traversal/HeroDev"
eal = unreal.EditorAssetLibrary
if eal.does_directory_exist(DST):
    eal.delete_directory(DST)
t = unreal.AssetImportTask()
t.set_editor_property("filename", SRC)
t.set_editor_property("destination_path", DST)
t.set_editor_property("automated", True)
t.set_editor_property("replace_existing", True)
t.set_editor_property("save", True)
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
assets = eal.list_assets(DST, recursive=True)
unreal.log("IMP_COUNT %d" % len(assets))
kinds = {}
for a in assets:
    d = eal.find_asset_data(a)
    c = str(d.asset_class_path.asset_name)
    kinds.setdefault(c, []).append(a.split("/")[-1].split(".")[0])
for c, l in kinds.items():
    unreal.log("IMP_KIND %s %d %s" % (c, len(l), ", ".join(sorted(l)[:12])))
for a in assets:
    obj = unreal.load_asset(a)
    if isinstance(obj, unreal.SkeletalMesh):
        b = obj.get_bounds()
        unreal.log("IMP_MESH %s bounds origin %s extent %s" % (a, b.origin, b.box_extent))
        sk = obj.skeleton
        unreal.log("IMP_SKEL %s" % sk.get_path_name())
        for bn in ["root", "hips", "head", "foot.L", "toe.L", "hand.L", "hand.R"]:
            try:
                tr = obj.get_ref_pose_transform(bn) if hasattr(obj, "get_ref_pose_transform") else None
            except Exception as e:
                tr = str(e)
            unreal.log("IMP_BONE %s %s" % (bn, tr))
    if isinstance(obj, unreal.AnimSequence):
        unreal.log("IMP_ANIM %s len %.3f frames %s" % (a.split('/')[-1], obj.get_play_length(), obj.get_editor_property("number_of_sampled_keys") if False else ""))
        break
