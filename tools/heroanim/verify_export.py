"""Independent evaluated Blender world matrices, including samples between baked keys."""
import bpy,sys,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/heroanim'))
import importlib, bake_hero
importlib.reload(bake_hero)
from bake_hero import action,frame,source_data,posed_globals
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
assert bpy.context.scene.get('session_owner')=='sm2-astra-anim'
doc,_,parents,rest=source_data()
manifest=json.loads((ROOT/'docs/anim/hero/clip-manifest.json').read_text())
rows=[];contact=[]
for name,meta in manifest.items():
 action(rig,name)
 for u in [0,.037,.1,.173,.25,.333,.417,.5,.583,.679,.75,.863,.947,.999]:
  t=meta['duration']*u;frame(t);world=posed_globals(rig,doc,rest)
  rows.append({'clip':name,'time':t,'world':{doc['nodes'][i]['name']:[world[i][r][c] for c in range(4) for r in range(4)] for i in doc['skins'][0]['joints']}})
 if name in ('heroSuitEnter','heroShowcaseIdle'):
  start=1.04 if name=='heroSuitEnter' else 0
  for k in range(61):
   t=start+(meta['duration']-start)*k/60;frame(t);world=posed_globals(rig,doc,rest)
   contact.append({'clip':name,'time':t,'feet':{doc['nodes'][i]['name']:list(world[i].translation) for i in doc['skins'][0]['joints'] if doc['nodes'][i]['name'] in ('foot.L','foot.R')}})
(ROOT/'.scratch/blender-witness.json').write_text(json.dumps({'rows':rows,'contacts':contact}))
action(rig,'heroShowcaseIdle');frame(0)
print('EXPORT_WITNESS',len(rows),'poses',len(contact),'plant samples')
