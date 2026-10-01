# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# P3 round 11 (owner brief FLIPS_BRIEF.md): gymnast shape clips keyed on the hero rig in Blender (headless).
#   blender -b -P make_flip_shapes.py -- <hero.glb> <out.glb> [<report.json>]
# Imports the hero GLB (public/assets/spiderman.glb, 58 bones), keys one action per held gymnastic shape (tuck, pike, layout,
# swan, pencil, straddle, throne, twist, reach) by aiming every limb / spine bone at a direction given in the BODY frame
# (F forward, U up, O outward for the bone's side), parent first, and exports ONLY these actions (+ the untouched 'airApex'
# action as a round-trip check) to <out.glb>. build_traversal.py splices the flip actions into Saved/HeroDev.glb
# (rotation channels only, matched by node name) after checking that 'airApex' survived the Blender round trip unchanged.
# Each clip is 1 s: key 0 = the shape, key 1 s = the same shape "breathing" (limbs 6-8 % further out) so a held shape is never
# frozen. Clip names: flipTuck, flipPike, flipLayout, flipSwan, flipPencil, flipStraddle, flipThrone, flipTwist, flipReach.
import bpy
import json
import sys
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
SRC = argv[0] if len(argv) > 0 else "public/assets/spiderman.glb"
OUT = argv[1] if len(argv) > 1 else "HeroFlips.glb"
REPORT = argv[2] if len(argv) > 2 else None

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.scene.render.fps = 30  # BEFORE the import: the importer maps glTF seconds to frames at the scene fps
bpy.ops.import_scene.gltf(filepath=SRC)
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
bpy.context.view_layer.objects.active = arm
scene = bpy.context.scene

# body frame of the imported rig (glTF +Z forward -> Blender -Y; the rig's .L side is +X)
F = Vector((0.0, -1.0, 0.0))
U = Vector((0.0, 0.0, 1.0))


def d(f, u, o, side):
    """Direction from body-frame components: f forward, u up, o outward (toward the bone's own side)."""
    s = 1.0 if side == "L" else -1.0
    v = F * f + U * u + Vector((s * o, 0.0, 0.0))
    return v.normalized()


CHAIN = ["hips", "spine", "spine1", "spine2", "neck", "head",
         "shoulder.L", "upperArm.L", "forearm.L", "hand.L", "shoulder.R", "upperArm.R", "forearm.R", "hand.R",
         "thigh.L", "shin.L", "foot.L", "toe.L", "thigh.R", "shin.R", "foot.R", "toe.R"]

# ---- shapes: bone -> (f, u, o). Side-less entries apply to both sides (o mirrored). None = keep the rest direction.
#   arms: upperArm / forearm; hand follows the forearm; legs: thigh / shin / foot (pointed toes follow the shin) / toe
POINT = "point"  # foot / toe along the shin (pointed toes)


def legs(thigh, shin, foot=POINT):
    return {"thigh": thigh, "shin": shin, "foot": foot, "toe": POINT}


SHAPES = {
    # tight tuck: knees to the chest, hands on the shins, back rounded, chin down
    "flipTuck": dict(spine=(0.35, 1, 0), spine1=(0.6, 1, 0), spine2=(0.8, 1, 0), neck=(1.0, 0.9, 0), head=(1.0, 0.55, 0),
                     upperArm=(1.0, -0.35, 0.4), forearm=(0.25, -1.0, 0.05), hand="follow",
                     **legs((1.0, 0.95, 0.12), (-0.35, -1.0, 0.05))),
    # pike: legs straight and together, folded forward at the hips, hands reaching to the ankles
    "flipPike": dict(spine=(0.3, 1, 0), spine1=(0.6, 1, 0), spine2=(0.95, 1, 0), neck=(1.0, 0.7, 0), head=(1.0, 0.4, 0),
                     upperArm=(1.0, 0.1, 0.12), forearm=(1.0, 0.35, 0.05), hand="follow",
                     **legs((1.0, 0.55, 0.03), (1.0, 0.6, 0.02))),
    # layout: one straight line, slight hollow, arms along the sides a hand-width out
    "flipLayout": dict(spine=(0.04, 1, 0), spine1=(0.02, 1, 0), spine2=(0.0, 1, 0), neck=(0.02, 1, 0), head=(0.05, 1, 0),
                       upperArm=(0.05, -1.0, 0.33), forearm=(0.05, -1.0, 0.22), hand="follow",
                       **legs((0.03, -1.0, 0.03), (0.0, -1.0, 0.02))),
    # swan: arched back, chest proud, arms spread wide and a little back, legs together extended behind
    "flipSwan": dict(spine=(-0.18, 1, 0), spine1=(-0.32, 1, 0), spine2=(-0.4, 1, 0), neck=(-0.25, 1, 0), head=(-0.15, 1, 0),
                     upperArm=(-0.3, 0.2, 1.0), forearm=(-0.22, 0.32, 1.0), hand="follow",
                     **legs((-0.28, -1.0, 0.02), (-0.4, -1.0, 0.02))),
    # pencil: straight, legs glued together, arms out low on the diagonal (the reference's inverted pencil)
    "flipPencil": dict(spine=(0.0, 1, 0), spine1=(0.0, 1, 0), spine2=(0.0, 1, 0), neck=(0.0, 1, 0), head=(0.03, 1, 0),
                       upperArm=(0.12, -0.5, 1.0), forearm=(0.12, -0.35, 1.0), hand="follow",
                       **legs((0.0, -1.0, 0.012), (0.0, -1.0, 0.0))),
    # straddle: straight legs split wide to the sides, arms spread level
    "flipStraddle": dict(spine=(0.12, 1, 0), spine1=(0.12, 1, 0), spine2=(0.1, 1, 0), neck=(0.1, 1, 0), head=(0.12, 1, 0),
                         upperArm=(0.15, 0.08, 1.0), forearm=(0.15, 0.18, 1.0), hand="follow",
                         **legs((0.3, -0.62, 1.0), (0.3, -0.6, 1.0))),
    # throne: upright "seated" spread (reference 23.0-23.4 s): knees up and apart, shins hanging, arms in a wide V
    "flipThrone": dict(spine=(-0.08, 1, 0), spine1=(-0.1, 1, 0), spine2=(-0.1, 1, 0), neck=(-0.05, 1, 0), head=(0.0, 1, 0),
                       upperArm=(0.05, 0.75, 1.0), forearm=(0.02, 1.0, 0.65), hand="follow",
                       **legs((1.0, 0.12, 0.45), (0.12, -1.0, 0.12))),
    # twist (corkscrew): legs straight and crossed tight, arms folded across the chest (small inertia about the long axis)
    "flipTwist": dict(spine=(0.02, 1, 0), spine1=(0.02, 1, 0), spine2=(0.02, 1, 0), neck=(0.02, 1, 0), head=(0.06, 1, 0),
                      upperArm=(0.75, -0.55, -0.1), forearm=(0.25, 0.3, -1.0), hand="follow",
                      **legs((0.0, -1.0, -0.03), (0.0, -1.0, -0.05))),
    # reach (catch prep): web arm (right) reaching up and forward, left arm out, knees lightly bent
    "flipReach": dict(spine=(0.05, 1, 0), spine1=(0.02, 1, 0), spine2=(0.0, 1, 0), neck=(0.0, 1, 0), head=(0.1, 1, 0),
                      upperArm_R=(0.45, 1.0, 0.25), forearm_R=(0.45, 1.0, 0.18), upperArm_L=(0.25, 0.05, 1.0), forearm_L=(0.35, 0.15, 1.0),
                      hand="follow", **legs((0.55, -0.85, 0.1), (-0.25, -1.0, 0.05))),
}
# breathing key: how much further out the limbs go at 1 s (blend toward a slightly more open copy)
BREATH = 0.07

# round 13 (critic r12: "Layout is a rigid, identical plank"; "backDouble uses 5 shapes"): KEYED shapes -- a list of (frame at 30 fps,
# shape) keys instead of one held pose + breathing. Arms lead, legs follow (their changes are keyed 3-6 frames later), so no two limbs
# switch on the same frame.
def _lay(ua, fa, th_l, sh_l, th_r, sh_r, sp=(0.04, 0.02, 0.0)):
    d = dict(spine=(sp[0], 1, 0), spine1=(sp[1], 1, 0), spine2=(sp[2], 1, 0), neck=(0.02, 1, 0), head=(0.05, 1, 0),
             upperArm=ua, forearm=fa, hand="follow", foot=POINT, toe=POINT)
    d["thigh_L"], d["shin_L"], d["thigh_R"], d["shin_R"] = th_l, sh_l, th_r, sh_r
    return d


KEYED = {
    # layout: the straight line breathes with overlapping limbs -- the arms float out and forward, the legs part a little behind them
    "flipLayout": [
        (0, _lay((0.05, -1.0, 0.33), (0.05, -1.0, 0.22), (0.03, -1.0, 0.03), (0.0, -1.0, 0.02), (0.03, -1.0, 0.03), (0.0, -1.0, 0.02))),
        (12, _lay((0.3, -0.75, 0.55), (0.35, -0.6, 0.45), (0.03, -1.0, 0.03), (0.0, -1.0, 0.02), (0.03, -1.0, 0.03), (0.0, -1.0, 0.02),
                  sp=(0.0, -0.04, -0.06))),
        (18, _lay((0.35, -0.6, 0.6), (0.4, -0.45, 0.5), (0.12, -1.0, 0.04), (0.05, -1.0, 0.02), (-0.08, -1.0, 0.04), (-0.14, -1.0, 0.02),
                  sp=(-0.02, -0.06, -0.08))),
        (30, _lay((0.1, -0.9, 0.45), (0.12, -0.85, 0.35), (0.06, -1.0, 0.05), (0.02, -1.0, 0.03), (-0.02, -1.0, 0.05), (-0.05, -1.0, 0.03),
                  sp=(0.02, 0.0, -0.03))),
    ],
    # kick-out (the double's open finish, then the catch): out of the tuck the arms swing up and forward, sweep wide and back while the
    # body arches and the legs, still piked, straighten and scissor behind them; the web arm (right) comes up for the catch at the end
    "flipKickout": [
        (0, _lay((0.45, 0.9, 0.3), (0.4, 1.0, 0.25), (0.35, -0.95, 0.05), (0.15, -1.0, 0.03), (0.35, -0.95, 0.05), (0.15, -1.0, 0.03),
                 sp=(0.15, 0.12, 0.08))),
        (8, _lay((0.15, 0.55, 1.0), (0.1, 0.6, 1.0), (0.25, -1.0, 0.05), (0.1, -1.0, 0.03), (0.25, -1.0, 0.05), (0.1, -1.0, 0.03),
                 sp=(0.0, -0.05, -0.08))),
        (16, _lay((-0.2, 0.15, 1.0), (-0.2, 0.25, 1.0), (0.05, -1.0, 0.05), (-0.02, -1.0, 0.03), (0.0, -1.0, 0.05), (-0.08, -1.0, 0.03),
                  sp=(-0.14, -0.22, -0.26))),
        (22, _lay((-0.05, 0.3, 1.0), (0.0, 0.4, 1.0), (0.22, -1.0, 0.06), (0.08, -1.0, 0.03), (-0.2, -1.0, 0.06), (-0.34, -1.0, 0.03),
                  sp=(-0.1, -0.16, -0.18))),
        (30, dict(_lay(None, None, (0.45, -0.9, 0.08), (-0.2, -1.0, 0.05), (0.25, -1.0, 0.07), (-0.3, -1.0, 0.04), sp=(0.05, 0.02, 0.0)),
                  upperArm_R=(0.45, 1.0, 0.25), forearm_R=(0.45, 1.0, 0.18), upperArm_L=(0.25, 0.1, 1.0), forearm_L=(0.35, 0.2, 1.0))),
    ],
}


def reset_pose():
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION"
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.location = (0, 0, 0)
        pb.scale = (1, 1, 1)
    bpy.context.view_layer.update()


def aim(pb, want):
    """Rotate pose bone pb (armature space, about its head) so head->tail points along want (minimal arc)."""
    bpy.context.view_layer.update()
    cur = (pb.tail - pb.head)
    if cur.length < 1e-6 or want.length < 1e-6:
        return
    q = cur.normalized().rotation_difference(want.normalized())
    h = pb.head.copy()
    M = Matrix.Translation(h) @ q.to_matrix().to_4x4() @ Matrix.Translation(-h) @ pb.matrix
    pb.matrix = M
    bpy.context.view_layer.update()


def spec_for(shape, bone):
    base, side = (bone.split(".")[0], bone.split(".")[1]) if "." in bone else (bone, "C")
    key_side = base + "_" + side
    if key_side in shape:
        return shape[key_side], side
    return shape.get(base), side


def apply_shape(shape, open_k=0.0):
    reset_pose()
    for bone in CHAIN:
        if bone == "hips" or bone.startswith("shoulder"):
            continue
        pb = arm.pose.bones[bone]
        sp, side = spec_for(shape, bone)
        if sp is None:
            continue
        if sp == "follow":  # hand along the forearm
            par = arm.pose.bones[bone.replace("hand", "forearm")]
            aim(pb, (par.tail - par.head))
            continue
        if sp == POINT:  # pointed foot / toe: along the shin
            src = "shin" if bone.startswith("foot") else "foot"
            par = arm.pose.bones[src + "." + side]
            aim(pb, (par.tail - par.head))
            continue
        f, u, o = sp
        if open_k and (bone.startswith("upperArm") or bone.startswith("forearm") or bone.startswith("thigh")):
            o = o + open_k * (1.0 if o >= 0 else -1.0) * 0.6
        aim(pb, d(f, u, o, side if side in ("L", "R") else "L"))


def key_all(frame):
    for bone in CHAIN + [b.name for b in arm.pose.bones if b.name not in CHAIN]:
        pb = arm.pose.bones[bone]
        pb.keyframe_insert("rotation_quaternion", frame=frame)


report = {}
keep = {"airApex"}
arm.animation_data_create()
def _clean(shape):
    return {k: v for k, v in shape.items() if v is not None}


for name, keys in KEYED.items():
    act = bpy.data.actions.new(name)
    act.use_fake_user = True
    arm.animation_data.action = act
    for fr, shape in keys:
        apply_shape(_clean(shape))
        key_all(fr)
    keep.add(name)
    print("FLIPSHAPE", name, "keyed", [fr for fr, _ in keys])

for name, shape in SHAPES.items():
    if name in KEYED:
        continue
    act = bpy.data.actions.new(name)
    act.use_fake_user = True
    arm.animation_data.action = act
    apply_shape(shape)
    key_all(0)
    # body-frame check of the key joints (feet, hands, head) relative to the hips
    hip = arm.pose.bones["hips"].head
    rep = {}
    for j in ("head", "hand.L", "hand.R", "foot.L", "foot.R", "shin.L"):
        p = arm.pose.bones[j].head - hip
        rep[j] = [round(p.dot(F), 3), round(p.dot(U), 3), round(p.x, 3)]  # forward, up, x(+L)
    rep["bones"] = {pb.name: [[round(x, 3) for x in (pb.head - hip)], [round(x, 3) for x in (pb.tail - hip)]] for pb in arm.pose.bones
                    if not any(k in pb.name for k in ("index", "middle", "ring", "pinky", "thumb"))}
    report[name] = rep
    apply_shape(shape, BREATH)
    key_all(30)
    keep.add(name)
    print("FLIPSHAPE", name, json.dumps({k: v for k, v in rep.items() if k != "bones"}))

# export only the flip actions + airApex (round-trip check)
for a in list(bpy.data.actions):
    if a.name not in keep:
        bpy.data.actions.remove(a)
arm.animation_data.action = bpy.data.actions["airApex"]
reset_pose()
kw = dict(filepath=OUT, export_format="GLB", export_animations=True, export_force_sampling=True, export_materials="NONE",
          export_animation_mode="ACTIONS")
try:
    bpy.ops.export_scene.gltf(**kw, export_optimize_animation_size=False)
except TypeError:
    bpy.ops.export_scene.gltf(**kw)
if REPORT:
    json.dump(report, open(REPORT, "w"), indent=1)
print("FLIPSHAPES_OK", OUT, sorted(keep))
