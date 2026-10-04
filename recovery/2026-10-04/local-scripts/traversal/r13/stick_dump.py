import bpy, sys, json
argv = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.scene.render.fps = 30
bpy.ops.import_scene.gltf(filepath=argv[0])
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
out = {}
B = ["hips","spine","spine1","spine2","neck","head","upperArm.L","forearm.L","hand.L","upperArm.R","forearm.R","hand.R","thigh.L","shin.L","foot.L","thigh.R","shin.R","foot.R"]
for act in bpy.data.actions:
    if not act.name.startswith("flip"): continue
    arm.animation_data.action = act
    fr = {}
    for f in (0, 8, 12, 16, 18, 22, 30):
        bpy.context.scene.frame_set(f); bpy.context.view_layer.update()
        fr[f] = {b: [list(arm.pose.bones[b].head), list(arm.pose.bones[b].tail)] for b in B}
    out[act.name] = fr
json.dump(out, open(argv[1], "w"))
print("DUMP_OK", list(out))
