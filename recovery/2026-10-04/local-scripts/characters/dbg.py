exec(open('/Users/midir/sm2-n1/characters/unreal/WebHomage/Scripts/build_characters.py').read().split('HERO_SKEL = ')[0].replace("(ARGS.get('steps') or 'prep,clean,tex,mat,mesh,citizens,abp,map').split(',')", "[]"))
for d in ('/Game/Characters/_dbg', '/Game/Characters/_tmp'):
    if EAL.does_directory_exist(d): EAL.delete_directory(d)
do_import(GLB + '/Thug.glb', '/Game/Characters/_dbg/Thug', skeleton='/Game/Characters/Hero/SKEL_Hero')
print(len(EAL.list_assets('/Game/Characters/_dbg', recursive=True)))
