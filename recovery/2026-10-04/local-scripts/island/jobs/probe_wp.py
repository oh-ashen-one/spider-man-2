import unreal
def p(*a): print('[probe]', *a)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
import inspect
p('new_level doc:', les.new_level.__doc__)
for n in dir(unreal):
    if 'WorldPartition' in n or 'RuntimeHash' in n or 'RuntimePartition' in n or 'HLOD' in n or 'Hlod' in n or 'SpatialHash' in n:
        p('cls', n)
