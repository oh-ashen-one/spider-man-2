"""Hand-keyed hero performance library. Character axes: X left, Y up, Z forward.
Each row is a deliberate pose/time, not a runtime procedural trick. Run through MCP.
"""
import bpy, math, json, sys
from pathlib import Path
from mathutils import Matrix, Vector, Quaternion, Euler
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/heroanim'))
import importlib, bake_hero
importlib.reload(bake_hero)
from bake_hero import bake, action, frame, C, CI
scene=bpy.context.scene
assert scene.get('session_owner')=='sm2-astra-anim'
rig=next(o for o in scene.objects if o.type=='ARMATURE')
scene.render.fps=24
rad=math.radians
def cv(v): return C.to_3x3() @ Vector(v)
def refresh(): bpy.context.view_layer.update()
def rot(name,angles):
    b=rig.pose.bones[name];r=b.bone.matrix_local.to_quaternion()
    q=Euler(tuple(rad(v) for v in angles),'XYZ').to_quaternion()
    q=C.to_quaternion() @ q @ CI.to_quaternion()
    b.rotation_quaternion=r.inverted() @ q @ r
def aim(name,d):
    b=rig.pose.bones[name];m=b.matrix.copy()
    old=(m.to_3x3() @ Vector((0,1,0))).normalized()
    q=old.rotation_difference(d.normalized())
    r=q @ m.to_quaternion()
    b.matrix=Matrix.LocRotScale(m.translation,r,Vector((1,1,1)))
    refresh()
def limb(side,kind,params,body):
    flex,abd,bend=params[:3];sgn=1 if side=='L' else -1
    f,a,k=map(rad,(flex,abd,bend))
    upper=Vector((sgn*math.sin(a),-math.cos(a)*math.cos(f),math.cos(a)*math.sin(f)))
    lowerf=f+(k if kind=='arm' else -k)
    lower=Vector((sgn*math.sin(a),-math.cos(a)*math.cos(lowerf),math.cos(a)*math.sin(lowerf)))
    names=('upperArm','forearm') if kind=='arm' else ('thigh','shin')
    for name,d in zip(names,(upper,lower)): aim(name+'.'+side,body @ cv(d))
    if kind=='leg':
        # Foot travels with the body, with a small ankle articulation; no rigid dangling flippers.
        b=rig.pose.bones['foot.'+side];q=b.bone.matrix_local.to_quaternion()
        footPitch=rad(params[3] if len(params)>3 else 0)
        dq=Quaternion(cv((1,0,0)),footPitch)
        b.matrix=Matrix.LocRotScale(b.matrix.translation,body @ dq @ q,Vector((1,1,1)))
    refresh()
def ikleg(side,target,pole):
    a=rig.pose.bones['thigh.'+side];b=rig.pose.bones['shin.'+side];c=rig.pose.bones['foot.'+side]
    A=a.matrix.translation.copy();B=b.matrix.translation.copy();E=c.matrix.translation.copy()
    l1=(B-A).length;l2=(E-B).length
    T=cv(target);D=T-A;d=min(D.length,(l1+l2)*.999)
    u=D.normalized();p=cv(pole)-A;p-=u*p.dot(u);p.normalize()
    x=(l1*l1-l2*l2+d*d)/(2*d);h=math.sqrt(max(0,l1*l1-x*x))
    knee=A+u*x+p*h
    aim(a.name,knee-A);aim(b.name,T-b.matrix.translation)
    c.matrix=Matrix.LocRotScale(c.matrix.translation,c.bone.matrix_local.to_quaternion(),Vector((1,1,1)))
    refresh()
NEUTRAL={'arms':[(30,26,45),(20,32,50)],'legs':[(24,9,40,4),(-12,8,25,-4)],'chest':-3}
def pose(p):
    for b in rig.pose.bones:
        b.rotation_mode='QUATERNION';b.location=(0,0,0);b.rotation_quaternion=(1,0,0,0);b.scale=(1,1,1)
    refresh()
    root=p.get('root',(0,0,0));rot('hips',root)
    hips=rig.pose.bones['hips']
    hips.location=hips.bone.matrix_local.to_3x3().inverted() @ cv(p.get('offset',(0,0,0)))
    chest=p.get('chest',0);twist=p.get('twist',0);roll=p.get('lean',0)
    for name,w in [('spine',.3),('spine1',.35),('spine2',.35)]:rot(name,(chest*w,twist*w,roll*w))
    rot('neck',(-chest*.2,p.get('look',0)*.4,0))
    rot('head',(-chest*.2+p.get('head',0),p.get('look',0)*.6,0))
    refresh()
    pelvis=hips.matrix.to_quaternion() @ hips.bone.matrix_local.to_quaternion().inverted()
    chestbone=rig.pose.bones['spine2']
    torso=chestbone.matrix.to_quaternion() @ chestbone.bone.matrix_local.to_quaternion().inverted()
    for side,pars in zip(('L','R'),p.get('arms',NEUTRAL['arms'])):limb(side,'arm',pars,torso)
    for side,pars in zip(('L','R'),p.get('legs',NEUTRAL['legs'])):limb(side,'leg',pars,pelvis)
    if p.get('plant'):
        ox,_,oz=p.get('offset',(0,0,0))
        for side,sx in [('L',1),('R',-1)]:
            ikleg(side,(sx*.16+(ox if abs(ox) > 1 else 0),.082,oz+sx*.045),(ox+sx*.16,.55,oz+.7))
    for side in ('L','R'):
        # Corrective shoulder volume follows half of upper-arm swing.
        upper=rig.pose.bones['upperArm.'+side]
        delt=rig.pose.bones['deltoid.'+side]
        delt.rotation_quaternion=Quaternion().slerp(upper.rotation_quaternion,.5)
        # Finger curl: small, relaxed bends retain readable open hands during recovery.
        curl=p.get('curl',.22)
        for b in rig.pose.bones:
            if b.name.endswith('.'+side) and any(b.name.startswith(n) for n in ('index','middle','ring','pinky')):
                b.rotation_quaternion=Quaternion((1,0,0),curl)
    refresh()
def P(**kw):return dict(NEUTRAL,**kw)
# Angles are anatomical degrees. Rotation progress is explicitly keyed through inversion.
front=[
 (0,P()),
 (.10,P(root=(12,0,0),chest=-12,arms=[(130,20,24),(110,30,35)],legs=[(8,8,18),(-15,8,32)])),
 (.24,P(root=(62,0,0),chest=-16,arms=[(165,18,18),(140,28,30)],legs=[(-12,9,20),(24,10,38)])),
 (.42,P(root=(148,0,0),chest=-7,arms=[(100,60,24),(65,70,38)],legs=[(28,12,30),(-24,8,24)])),
 (.63,P(root=(234,0,0),chest=10,arms=[(45,48,60),(15,55,50)],legs=[(40,10,50),(-10,12,30)])),
 (.85,P(root=(310,0,0),chest=9,arms=[(25,34,62),(50,35,56)],legs=[(30,8,55),(12,8,40)])),
 (1.06,P(root=(350,0,0),chest=3,arms=[(34,28,38),(42,32,46)],legs=[(18,8,32),(-9,10,28)])),
 (1.30,P(root=(360,0,0)))]
back=[
 (0,P()),
 (.12,P(root=(-18,0,0),chest=-12,arms=[(138,24,30),(125,28,36)],legs=[(15,8,32),(4,8,30)])),
 (.30,P(root=(-80,0,0),chest=-18,arms=[(155,30,24),(140,38,32)],legs=[(5,10,30),(-25,8,45)])),
 (.52,P(root=(-170,0,0),chest=-8,arms=[(110,55,48),(65,58,60)],legs=[(35,12,52),(-10,10,38)])),
 (.75,P(root=(-260,0,0),chest=12,arms=[(45,42,68),(20,52,50)],legs=[(52,8,75),(18,10,50)])),
 (1.02,P(root=(-340,0,0),chest=6,arms=[(28,30,48),(35,32,55)],legs=[(20,8,38),(-6,8,30)])),
 (1.30,P(root=(-360,0,0)))]
cork=[
 (0,P()),
 (.12,P(root=(30,-15,6),twist=-12,arms=[(125,25,25),(5,55,70)],legs=[(8,7,15),(-25,10,42)])),
 (.28,P(root=(68,-70,5),twist=-15,arms=[(155,18,20),(10,40,75)],legs=[(0,5,12),(-18,9,35)])),
 (.46,P(root=(78,-158,0),twist=-8,arms=[(130,24,34),(35,32,84)],legs=[(12,7,25),(-12,12,42)])),
 (.64,P(root=(68,-255,-6),twist=7,arms=[(75,48,55),(30,50,58)],legs=[(25,12,45),(-20,10,35)])),
 (.86,P(root=(25,-337,-3),twist=4,arms=[(38,38,55),(42,35,50)],legs=[(34,10,52),(8,9,32)])),
 (1.10,P(root=(0,-360,0)))]
tuck=[
 (0,P()),
 (.10,P(root=(24,0,0),chest=12,arms=[(70,22,80),(65,25,85)],legs=[(65,8,100),(48,10,90)])),
 (.23,P(root=(93,0,0),chest=20,arms=[(38,20,115),(35,22,120)],legs=[(115,10,135),(100,12,130)],head=10,curl=.5)),
 (.40,P(root=(205,0,0),chest=18,arms=[(35,22,118),(40,20,115)],legs=[(110,10,135),(100,12,132)],curl=.5)),
 (.57,P(root=(294,0,0),chest=8,arms=[(58,45,62),(45,55,65)],legs=[(62,10,80),(38,12,60)])),
 (.76,P(root=(347,0,0),chest=2,arms=[(32,40,38),(26,36,46)],legs=[(20,10,35),(-10,10,25)])),
 (.98,P(root=(360,0,0)))]
scissor=[
 (0,P()),
 (.15,P(root=(12,30,-7),twist=15,arms=[(105,40,48),(0,55,65)],legs=[(65,12,28),(-38,10,34)])),
 (.34,P(root=(20,110,-10),twist=18,arms=[(65,65,40),(40,58,65)],legs=[(80,15,24),(-52,12,28)])),
 (.54,P(root=(10,220,8),twist=-10,arms=[(20,65,65),(85,48,42)],legs=[(-30,10,55),(55,12,40)])),
 (.78,P(root=(4,320,4),twist=-4,arms=[(15,40,55),(52,42,50)],legs=[(10,10,35),(25,8,42)])),
 (1.10,P(root=(0,360,0)))]
jump=[
 (0,P(offset=(0,-.22,0),chest=16,arms=[(-35,18,40),(-24,24,48)],plant=True)),
 (.08,P(offset=(0,-.10,0),chest=8,arms=[(42,20,45),(70,25,55)],plant=True)),
 (.16,P(chest=-8,arms=[(138,25,35),(100,40,55)],legs=[(3,5,12),(-15,8,25)])),
 (.28,P(chest=-6,arms=[(120,36,50),(75,52,70)],legs=[(72,10,110),(35,10,80)])),
 (.44,P(chest=-3,arms=[(60,48,58),(35,55,62)],legs=[(60,14,90),(20,12,55)])),
 (.60,P())]
idle=P(offset=(.015,-.025,0),arms=[(5,10,22),(12,15,28)],legs=[(0,0,0),(0,0,0)],chest=-2,twist=5,look=-5,plant=True,curl=.3)
entry=[
 (0,P(offset=(3.5,-.10,0),root=(0,0,0),arms=[(-30,22,45),(40,25,62)],plant=True)),
 (.14,P(offset=(2.0,.2,0),root=(20,0,-15),chest=-8,arms=[(130,28,35),(100,40,52)],legs=[(10,8,15),(-28,10,55)])),
 (.34,P(offset=(.65,.95,0),root=(95,25,-20),chest=6,arms=[(90,35,65),(25,45,85)],legs=[(82,10,115),(65,12,95)])),
 (.55,P(offset=(.18,1.05,0),root=(207,50,-12),chest=14,arms=[(35,24,110),(45,28,95)],legs=[(108,10,135),(80,12,115)])),
 (.76,P(offset=(.025,.60,0),root=(302,24,-5),chest=8,arms=[(40,50,60),(50,42,65)],legs=[(45,12,70),(30,12,50)])),
 (.94,P(offset=(0,.08,0),root=(355,0,0),chest=5,arms=[(42,30,45),(30,40,52)],legs=[(20,8,35),(15,8,30)])),
 (1.04,P(offset=(0,-.32,0),root=(360,0,0),chest=24,arms=[(30,30,55),(5,38,50)],plant=True,look=-8)),
 (1.18,P(offset=(.012,-.24,0),root=(360,0,0),chest=18,arms=[(20,22,45),(8,28,38)],plant=True,look=-8)),
 (1.48,P(offset=(.025,-.05,0),root=(360,0,0),chest=4,arms=[(10,14,28),(14,20,36)],plant=True,look=-6)),
 (1.82,dict(idle,root=(360,0,0))),
 (2.20,dict(idle,root=(360,0,0)))]
idlekeys=[(0,idle),(.8,dict(idle,offset=(.018,-.021,0),chest=-2.8)),(1.6,dict(idle,offset=(.015,-.018,0),chest=-3.2,look=-3)),(2.4,dict(idle,offset=(.012,-.022,0),chest=-2.5)),(3.2,idle)]
CLIPS={'heroLayoutFront':front,'heroLayoutBack':back,'heroCorkscrew':cork,'heroTuckFlip':tuck,'heroScissor':scissor,'heroJumpLaunch':jump,'heroSuitEnter':entry,'heroShowcaseIdle':idlekeys}
rig.animation_data.action=None
for track in rig.animation_data.nla_tracks:track.mute=True
for name,keys in CLIPS.items():
    old=bpy.data.actions.get(name)
    if old:bpy.data.actions.remove(old)
    a=bpy.data.actions.new(name);a.use_fake_user=True;rig.animation_data.action=a
    previous={}
    for t,p in keys:
        rig.animation_data.action=None
        pose(p)
        want=C.to_quaternion() @ Euler(tuple(rad(v) for v in p.get('root',(0,0,0))),'XYZ').to_quaternion() @ CI.to_quaternion()
        got=(rig.pose.bones['hips'].matrix @ rig.data.bones['hips'].matrix_local.inverted()).to_quaternion()
        assert abs(want.dot(got)) > .9999, (name,t,'hip rotation lost',list(want),list(got))
        rig.animation_data.action=a
        for b in rig.pose.bones:
            if b.name in previous and b.rotation_quaternion.dot(previous[b.name])<0:b.rotation_quaternion.negate()
            previous[b.name]=b.rotation_quaternion.copy()
            for attr in ('location','rotation_quaternion','scale'):b.keyframe_insert(attr,frame=t*24,group=b.name)
    # Blender 4.4+ slotted Action API. Explicit smooth, clamped handles avoid impact overshoot.
    for layer in a.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    for k in curve.keyframe_points:
                        k.interpolation='BEZIER';k.handle_left_type='AUTO_CLAMPED';k.handle_right_type='AUTO_CLAMPED'
    a['authorship']='Hand-keyed pose progression in tools/heroanim/author_hero.py'
    a['purpose']='menu' if 'Suit' in name or 'Showcase' in name else 'traversal'
    print('AUTHORED',name,keys[-1][0],len(keys))
bake(rig,list(CLIPS),ROOT/'public/assets/animations/hero-acrobatics.json',fps=120)
action(rig,'heroLayoutFront');frame(.42)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'art/anim/hero.blend'))
(ROOT/'docs/anim/hero/clip-manifest.json').write_text(json.dumps({n:{'duration':keys[-1][0],'keyTimes':[k[0] for k in keys],'poses':len(keys)} for n,keys in CLIPS.items()},indent=2))
print('AUTHORED_AND_BAKED',len(CLIPS))
