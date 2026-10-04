import bpy, sys
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath="/Users/midir/sm2-n1/traversal/public/assets/spiderman.glb")
arm=[o for o in bpy.data.objects if o.type=='ARMATURE'][0]
print("ARM", arm.name, arm.matrix_world, arm.rotation_mode)
bpy.context.view_layer.objects.active=arm
for b in ['hips','spine','spine2','neck','head','thigh.L','shin.L','foot.L','toe.L','upperArm.L','forearm.L','hand.L','shoulder.L','thigh.R','upperArm.R']:
    pb=arm.pose.bones[b]; print("BONE",b,"head",tuple(round(x,3) for x in pb.head),"tail",tuple(round(x,3) for x in pb.tail), "parent", pb.parent.name if pb.parent else None)
print("ACTIONS", len(bpy.data.actions), [a.name for a in bpy.data.actions][:5])
print("ANIMDATA", arm.animation_data.action.name if arm.animation_data and arm.animation_data.action else None)
