import unreal, math
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Tests/City/City_View_S4_perch_skyline')
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
P = (182*100.0, -92*100.0, 306*100.0); T = (-120*100.0, -470*100.0, 150*100.0)
def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def add(a,b): return tuple(x+y for x,y in zip(a,b))
def mul(a,k): return tuple(x*k for x in a)
def norm(a):
    l = math.sqrt(sum(x*x for x in a)); return tuple(x/l for x in a)
def cross(a,b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
f = norm(sub(T,P)); right = norm(cross((0,0,1.0),f)); up = cross(right,f)
tan = math.tan(math.radians(75)/2)
def ray(px,py,W=1920,H=1080):
    x=(px/W*2-1)*tan; y=(1-py/H*2)*tan*H/W
    return norm(add(add(f,mul(right,x)),mul(up,y)))

def hit(o,e,O,d):
    tmin=-1e30; tmax=1e30
    for i in range(3):
        if abs(d[i])<1e-9:
            if O[i]<o[i]-e[i] or O[i]>o[i]+e[i]: return False,0
            continue
        t1=(o[i]-e[i]-O[i])/d[i]; t2=(o[i]+e[i]-O[i])/d[i]
        if t1>t2: t1,t2=t2,t1
        tmin=max(tmin,t1); tmax=min(tmax,t2)
    return tmax>=max(tmin,0), tmin
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
acts=[]
for a in eas.get_all_level_actors():
    try: o,e=a.get_actor_bounds(False)
    except Exception: continue
    acts.append((a.get_actor_label(),(o.x,o.y,o.z),(e.x,e.y,e.z)))
for (px,py) in [(100,320),(600,315),(100,215),(600,190),(1300,225),(1000,290)]:
    d=ray(px,py); res=[]
    for lab,o,e in acts:
        if lab.startswith(('facade__','detail__','roofs__','asphalt__','sidewalk__','ISM_','streetkit','markings','Sun','Sky','Height','Water','PPV','Player','Clouds','ShotCam')): continue
        h,t=hit(o,e,P,d)
        if h and t>0: res.append((round(t/100),lab))
    res.sort()
    print(px,py,res[:8])
