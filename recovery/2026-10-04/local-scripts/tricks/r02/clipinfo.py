import bpy, sys, math
from mathutils import Vector
argv=sys.argv[sys.argv.index("--")+1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.scene.render.fps=30
bpy.ops.import_scene.gltf(filepath=argv[0])
arm=next(o for o in bpy.data.objects if o.type=="ARMATURE")
names=[a.name for a in bpy.data.actions]
print("ACTIONS", names)
want=[n for n in names if any(k in n for k in ("swing","flipReach","flipKickout","fallCalm","airApex"))]
F=Vector((0,-1,0)); U=Vector((0,0,1)); L=Vector((1,0,0))
for n in want:
    act=bpy.data.actions[n]
    arm.animation_data_create(); arm.animation_data.action=act
    fr=act.frame_range
    for fi in (fr[0], (fr[0]+fr[1])/2):
        bpy.context.scene.frame_set(int(fi)); bpy.context.view_layer.update()
        out=[]
        for b in ("hips","spine2","head"):
            pb=arm.pose.bones.get(b)
            if not pb: continue
            m=pb.matrix  # armature space
            y=m.to_3x3()@Vector((0,1,0)); z=m.to_3x3()@Vector((0,0,1))
            # bone axis (y) components: fwd, up, left(+X)
            out.append(f"{b}: axis f{y.dot(F):+.2f} u{y.dot(U):+.2f} l{y.dot(L):+.2f} | z f{z.dot(F):+.2f} u{z.dot(U):+.2f} l{z.dot(L):+.2f}")
        print(f"{n:22s} fr{int(fi):3d} "+" || ".join(out))
