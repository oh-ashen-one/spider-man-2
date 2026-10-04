import unreal
def p(*a): print('[probe]', *a)
path = '/Game/Island/Probe/Probe_WP'
unreal.EditorLoadingAndSavingUtils.load_map(path)
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
wp = w.get_world_settings().get_editor_property('world_partition')
base = wp.get_path_name()
p('wp', base)
found = None
for hn in ('WorldPartitionRuntimeHashSet_0', 'WorldPartitionRuntimeSpatialHash_0'):
    o = unreal.find_object(None, base + '.' + hn)
    p(hn, o)
    if o:
        try: p('partitions', o.get_editor_property('runtime_partitions'))
        except Exception as e: p('ERR rp', str(e)[:200])
        for i in range(4):
            g = unreal.find_object(None, base + '.' + hn + '.RuntimePartitionLHGrid_%d' % i)
            p('grid', i, g)
            if g:
                for prop in ('CellSize', 'LoadingRange', 'bBlockOnSlowStreaming', 'Priority', 'HLODIndex'):
                    try: p('  ', prop, g.get_editor_property(prop))
                    except Exception as e: p('  ERR', prop, str(e)[:100])
                if i == 0: found = g
if found:
    found.set_editor_property('CellSize', 25600)
    found.set_editor_property('LoadingRange', 120000)
    p('set', found.get_editor_property('CellSize'), found.get_editor_property('LoadingRange'))
    p('saved', unreal.EditorLoadingAndSavingUtils.save_map(w, path))
