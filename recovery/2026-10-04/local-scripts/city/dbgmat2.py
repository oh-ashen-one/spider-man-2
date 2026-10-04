import unreal
mel=unreal.MaterialEditingLibrary
m=unreal.load_asset('/Game/City/Materials/M_CityFacade')
c=[e for e in mel.get_material_expressions(m) if isinstance(e, unreal.MaterialExpressionCustom)][0]
code=c.get_editor_property('code'); F='/Users/midir/sm2-n1/_scratch/city/facade_code.txt'
if 'DEBUG' not in code: open(F,'w').write(code)
base=open(F).read()
if JOB_ARGS.get('mode')=='restore': code=base
else: code=base[:base.rindex('return')] + '// DEBUG\n' + JOB_ARGS['expr']
c.set_editor_property('code', code); mel.recompile_material(m); print(code[-160:])
